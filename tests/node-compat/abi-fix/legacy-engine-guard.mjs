// Positive controls for narrow legacy-engine exceptions; all components import nothing.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {loadToolchain} from '../toolchain.mjs';
import {loadComponentizer} from '../componentizer.mjs';
const here=dirname(fileURLToPath(import.meta.url)),tc=await loadToolchain();
const normal=await loadComponentizer(tc),legacy=await loadComponentizer(tc,{legacyDiagnostic:true});
const {componentWit,transpile}=await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco')));
const output=resolve(process.env.NODE_COMPAT_LEGACY_ENGINE_OUTPUT??'/tmp/starling-node-compat/legacy-engine-guard');await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
const world='package starling:legacy-engine-guard@0.1.0; world profile { export run: func() -> u32; }';
const source='export const run = () => 0xffffffff;';const sha=b=>createHash('sha256').update(b).digest('hex');
const reports=[];
for(const[name,engine,loader,expected,auditId]of[
 ['released6094',join(tc.directory,'node_modules/@bytecodealliance/componentize-js/lib/starlingmonkey_embedding.wasm'),legacy,4292870144,'componentize-js-0.23.0-released-broken-control'],
 ['historical3f5','/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.candidate.release.wasm',legacy,0xffffffff,'188-source-release-held-constant-import-i32-control'],
 ['normal99f','/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.abi-i32-i64-v1.allocation-r2.wasm',normal,0xffffffff,null],
]){const result=await loader.componentize(source,{engine,witWorld:world,worldName:'profile',disableFeatures:['stdio','random','clocks','http','fetch-event']});assert.equal(result.legacyEngineDiagnosticAudit?.id??null,auditId);const emittedWit=await componentWit(result.component);assert.deepEqual(emittedWit.split('\n').filter(l=>/^\s*import /.test(l)),[]);const path=join(output,name+'.wasm');await writeFile(path,result.component);const {files}=await transpile(result.component,{name});for(const[n,b]of Object.entries(files)){const p=join(output,n);await mkdir(dirname(p),{recursive:true});await writeFile(p,b);}const guest=await import(pathToFileURL(join(output,name+'.js')));const observed=guest.run();assert.equal(observed,expected);reports.push({name,engine,engineSha256:sha(await readFile(engine)),componentPath:path,componentSha256:sha(result.component),emittedImports:[],expected,observed,legacyEngineDiagnosticAudit:result.legacyEngineDiagnosticAudit??null,packaging:loader.provenance});}
await writeFile(join(here,'legacy-engine-guard-results.json'),JSON.stringify({schemaVersion:1,atUtc:new Date().toISOString(),source,world,reports,scope:'Only exact known old release bytes are admitted under explicit diagnostic selection; normal audited release uses observed configuration metadata. No arbitrary unknown engine or DEBUG bypass.'},null,2)+'\n');console.log(JSON.stringify(reports.map(r=>({name:r.name,observed:r.observed,diagnostic:r.legacyEngineDiagnosticAudit?.id??null})),null,2));
