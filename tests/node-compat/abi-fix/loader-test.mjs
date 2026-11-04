import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { cp, readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const toolchain=await loadToolchain();
const selected=await loadComponentizer(toolchain);
assert(['patched-import-i32-v1','patched-import-i32-clock-v2'].includes(selected.provenance.selection));
assert.throws(()=>selected.componentize('export function x() {}',{}),/explicit audited native engine/);
await assert.rejects(selected.componentize('export const run=()=>1',{engine:'/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.abi-i32-i64-v1.gc-stress.oom-testing.debug.allocation-r2.wasm'}),error=>error.code==='ERR_SM_NODE_UNREBASED_DEBUG_MEMORY');
const diagnostic=await loadComponentizer(toolchain,{debugScalarOOMDiagnostic:true});
const scalarWorld=await readFile(join(here,'../oom/profile.wit'),'utf8');
const debugOptions={engine:process.env.NODE_COMPAT_DEBUG_ENGINE??'/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.abi-i32-i64-v1.gc-stress.oom-testing.debug.allocation-r2.wasm',witWorld:scalarWorld,worldName:'profile',disableFeatures:['stdio','random','clocks','http','fetch-event']};
for(const overrides of[{witWorld:scalarWorld.replace('s32','string')},{witWorld:scalarWorld.replace('world profile {','world profile { import extra:func();')},{disableFeatures:['stdio','random','http','fetch-event']},{witPath:'/tmp/not-admitted.wit'}]) {
 await assert.rejects(diagnostic.componentize('export const run=()=>1',{...debugOptions,...overrides}),/AssertionError/);
}
const oldOverride=process.env.NODE_COMPAT_ALLOW_UNREBASED_DEBUG_DIAGNOSTIC;process.env.NODE_COMPAT_ALLOW_UNREBASED_DEBUG_DIAGNOSTIC='1';
const legacyWithOverride=await loadComponentizer(toolchain,{legacyDiagnostic:true});
await assert.rejects(legacyWithOverride.componentize('export const run=()=>1',debugOptions),error=>error.code==='ERR_SM_NODE_UNREBASED_DEBUG_MEMORY');
if(oldOverride===undefined)delete process.env.NODE_COMPAT_ALLOW_UNREBASED_DEBUG_DIAGNOSTIC;else process.env.NODE_COMPAT_ALLOW_UNREBASED_DEBUG_DIAGNOSTIC=oldOverride;
const releasedEngine=join(toolchain.directory,'node_modules/@bytecodealliance/componentize-js/lib/starlingmonkey_embedding.wasm');
await assert.rejects(selected.componentize('export const run=()=>1',{engine:releasedEngine}),/Audited engine metadata required/);
await assert.rejects(selected.componentize('export const run=()=>1',{engine:'/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.candidate.release.wasm'}),/Unambiguous observed Release\/Debug configuration required/);
const output=resolve(process.env.NODE_COMPAT_LOADER_TEST_OUTPUT??'/tmp/starling-node-compat/import-abi-loader-tests');
await mkdir(output,{recursive:true});
const renamedDebug=join(output,'unknown-renamed.wasm');await cp(debugOptions.engine,renamedDebug);
await assert.rejects(legacyWithOverride.componentize('export const run=()=>1',{engine:renamedDebug}),/Audited engine metadata required/);

const loaderURL=pathToFileURL(resolve(here,'../componentizer.mjs')).href;
const tcURL=pathToFileURL(resolve(here,'../toolchain.mjs')).href;
const checks=[];
function child(name,modulePath,expected,legacy=false){const env={...process.env};delete env.NODE_COMPAT_LEGACY_COMPONENTIZER;if(modulePath)env.NODE_COMPAT_COMPONENTIZE_MODULE=modulePath;else delete env.NODE_COMPAT_COMPONENTIZE_MODULE;const code=`const {loadComponentizer}=await import(${JSON.stringify(loaderURL)});const {loadToolchain}=await import(${JSON.stringify(tcURL)});await loadComponentizer(await loadToolchain(),{legacyDiagnostic:${legacy}});`;const r=spawnSync(process.execPath,['--input-type=module','-e',code],{env,encoding:'utf8'});assert.notEqual(r.status,0,name);assert.match(r.stderr,expected,name);checks.push({name,status:r.status,matchedError:String(expected)});}
child('stock requires explicit opt-in',null,/stock packaging requires explicit legacyDiagnostic/);
const saved=process.env.NODE_COMPAT_COMPONENTIZE_MODULE;delete process.env.NODE_COMPAT_COMPONENTIZE_MODULE;
const legacy=await loadComponentizer(toolchain,{legacyDiagnostic:true});assert.equal(legacy.provenance.selection,'stock-legacy-diagnostic');assert.throws(()=>legacy.componentize('export function x() {}',{}),/explicit audited native engine/);process.env.NODE_COMPAT_COMPONENTIZE_MODULE=saved;
for(const [name,target,mutate,rewriteHash]of [
 ['manifest patch tamper','splicer-build.json',b=>{const m=JSON.parse(b);m.patch.sha256='0'.repeat(64);return Buffer.from(JSON.stringify(m));},false],
 ['unknown additional patch in v1 manifest','splicer-build.json',b=>{const m=JSON.parse(b);m.packagingVersion='componentize-js-0.23.0+sm-import-i32.v1';m.additionalPatches=[{id:'unknown',sha256:'0'.repeat(64)}];return Buffer.from(JSON.stringify(m));},false],
 ['JavaScript artifact tamper','lib/spidermonkey-embedding-splicer.js',b=>Buffer.concat([b,Buffer.from('\n//tamper\n')]),false],
 ['platform source tamper with forged manifest digest','src/platform.js',b=>Buffer.concat([b,Buffer.from('\n//tamper\n')]),true],
 ['core artifact tamper with forged manifest digest','lib/spidermonkey-embedding-splicer.core.wasm',b=>{const c=Buffer.from(b);c[c.length-1]^=1;return c;},true],
]){const root=join(output,name.replaceAll(' ','-'));await mkdir(root,{recursive:true});for(const p of ['src','lib','package.json','splicer-build.json'])await cp(join(selected.directory,p),join(root,p),{recursive:true,force:true});const changed=mutate(await readFile(join(root,target)));await writeFile(join(root,target),changed);if(rewriteHash){const m=JSON.parse(await readFile(join(root,'splicer-build.json')));m.checkedFiles.find(e=>e.path===target).sha256=createHash('sha256').update(changed).digest('hex');await writeFile(join(root,'splicer-build.json'),JSON.stringify(m));}child(name,join(root,'src/componentize.js'),name==='unknown additional patch in v1 manifest'?/Unknown additional patches in v1 manifest/:/AssertionError/);}
const report={schemaVersion:1,atUtc:new Date().toISOString(),packagingManifestSha256:selected.provenance.manifestSha256,passed:checks.length+12,checks,additionalChecks:['Normal calls reject missing metadata, historical unknown configuration and an unlabelled renamed DEBUG binary','DEBUG diagnostic rejects indirect return, imports, feature expansion and witPath before packaging','legacy diagnostic/environment flag cannot bypass DEBUG refusal','known unrebased DEBUG engine refused before packaging','patched loader accepts known actual artifacts','patched componentize rejects missing explicit engine','explicit legacy diagnostic accepts stock bytes and still rejects missing explicit engine'],scope:'Tampering occurs only in isolated external copies; audited package and shared npm installation remain unchanged.'};
await writeFile(join(here,'loader-test-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:report.passed,output},null,2));
