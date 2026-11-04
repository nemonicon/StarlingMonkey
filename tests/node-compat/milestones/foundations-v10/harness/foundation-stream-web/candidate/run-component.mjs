import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,symlink} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {loadToolchain} from '../../toolchain.mjs';
import {loadComponentizer} from '../../componentizer.mjs';
import {bundleProfile} from '../../profile-bundler.mjs';
import {selectedManifestsForEngine} from '../../module-selection.mjs';
assert.equal(process.version,'v22.14.0');assert(process.env.NODE_COMPAT_ENGINE&&process.env.NODE_COMPAT_WASMTIME&&process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT);
const here=dirname(fileURLToPath(import.meta.url)),sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT);
const engine=resolve(process.env.NODE_COMPAT_ENGINE),wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME);
const output=resolve(process.env.NODE_COMPAT_STREAM_CANDIDATE_OUTPUT??'/tmp/starling-node-compat/foundations-v6/stream-web-candidate');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex'),metadata=JSON.parse(await readFile(engine+'.build.json'));
assert.equal(hash(await readFile(engine)),metadata.engineSha256);assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');assert.equal(metadata.oomTesting,false);
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);
assert.equal(metadata.sourceManifest.find(entry=>entry.path==='builtins/web/text-codec/text-decoder.cpp')?.sha256,
  '4697d8951a724d92e7550d48bd10cd2652d4d789797dc90ad8401216e9a4512c','Only corrected ordinary native decoder is admitted');
const toolchain=await loadToolchain(),{componentize,provenance}=await loadComponentizer(toolchain);
const{componentWit,transpile}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const version=spawnSync(wasmtime,['--version'],{encoding:'utf8'});assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
try{await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'),'dir');}catch(error){if(error.code!=='EEXIST')throw error;}
const expected={codecs:JSON.parse(await readFile(join(here,'codec-node-results.json'))),guard:JSON.parse(await readFile(join(here,'byob-node-results.json'))),
  typedViews:JSON.parse(await readFile(join(here,'typed-view-node-results.json'))),controllers:JSON.parse(await readFile(join(here,'controller-node-results.json')))};
const bundled=await bundleProfile({...toolchain,input:join(here,'component.mjs'),builtinManifests:selectedManifestsForEngine(metadata,{sourceRoot}),
  virtualModules:{'node-compat:stream-web-candidate-oracles':'export default '+JSON.stringify(expected)+';'}});
assert.deepEqual(bundled.imports,[]);await writeFile(join(output,'application.bundle.mjs'),bundled.code);
const{component,interfaceAudit}=await componentize(bundled.code,{engine,witWorld:await readFile(join(here,'../profile.wit'),'utf8'),worldName:'profile',
  disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});
const path=join(output,'candidate.component.wasm');await writeFile(path,component);
const wit=await componentWit(component);assert.deepEqual(wit.split('\n').filter(line=>/^\s*import /.test(line)),[]);
await writeFile(join(output,'candidate.wit'),wit);
const{files}=await transpile(component,{name:'candidate'});
for(const[file,bytes]of Object.entries(files)){const target=join(output,file);await mkdir(dirname(target),{recursive:true});await writeFile(target,bytes);}
const instance=await import(pathToFileURL(join(output,'candidate.js'))),calls=[];
function check(report,index){
  assert(!report.failure,JSON.stringify(report.failure));assert.equal(report.passed,true);assert.equal(report.calls,index);
  assert.equal(report.constructors,expected.codecs.constructorCases.length);assert.equal(report.codecs,expected.codecs.codecCases.length);
  assert.equal(report.cancellations,expected.codecs.cancellationCases.length);assert.equal(report.guardCases,expected.guard.cases.length);
  assert.deepEqual(report.guardDeviations,['min-two','proxy-genuine-receiver','shadowed-view-fields']);
  assert(report.compressionAlwaysDeferred&&report.globalCodecsUnchanged&&report.nativeConstructorIdentities);
  assert(report.originalDescriptorsRestored&&report.deferredIterableSlots);
  assert.equal(report.primordials.replacementInvocations,0);
  assert.equal(report.policies.checks.length,16);
  assert.equal(report.typedViews,12);
  assert.deepEqual(report.typedViewDeviations,['DataView']);assert.equal(report.guardedControllerCases,6);
}
for(let index=1;index<=2;index++){
  const report=JSON.parse(await instance.run());calls.push(report);await writeFile(join(output,'calls.json'),JSON.stringify(calls,null,2)+'\n');check(report,index);
}
const host=spawnSync(wasmtime,['run','--invoke','run()',path],{encoding:'utf8',timeout:180000,maxBuffer:1024*1024});
await writeFile(join(output,'wasmtime.log'),JSON.stringify(host,null,2)+'\n');assert.equal(host.status,0,host.error?.message||host.stderr);
const wasmtimeReport=JSON.parse(JSON.parse(host.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,hex)=>String.fromCodePoint(parseInt(hex,16)))));
check(wasmtimeReport,1);assert.deepEqual(wasmtimeReport,calls[0]);
const templatePath=join(here,'../native-kernel.template.cpp');
const result={schema:1,atUtc:new Date().toISOString(),scope:'ISOLATED bounded codec/guard prototype, uninstalled. Fixture-registered reader brand only; actual native public API callback remains uncompiled.',
  engine,engineSha256:metadata.engineSha256,sourceRoot,metadata,componentizer:provenance,
  component:{path,bytes:component.length,sha256:hash(component),emittedImports:[],emittedWit:wit,interfaceAudit},
  calls,wasmtime:version.stdout.trim(),wasmtimeReport,
  kernelTemplate:{path:templatePath,sha256:hash(await readFile(templatePath)),state:'Uncompiled and unused in this component'},
  sourceManifest:await Promise.all(['factory.mjs','fixture-record.mjs','codec-cases.mjs','codec-node-oracle.mjs','codec-node-results.json',
    'guard-cases.mjs','byob-node-oracle.mjs','byob-node-results.json','policy-cases.mjs','typed-view-cases.mjs','typed-view-node-oracle.mjs',
    'typed-view-node-results.json','controller-cases.mjs','controller-node-oracle.mjs','controller-node-results.json',
    'component.mjs','run-component.mjs'].map(async path=>({path,sha256:hash(await readFile(join(here,path)))}))),
  limitations:['No production registration/CMake or global codec installation; selected native BYOB prototype read is mutated only in the opt-in isolated simulation.',
    'Private brand callback is a fixture registry of registered native readers, not production arbitrary/cross-realm brand proof.',
    'UTF8 decoder only; other known native labels deferred, unknown labels preserve mapped native invalid-encoding error.',
    'Compression/Decompression always explicit deferred functions; no compression constructors captured/invoked.',
    'WDC.signal, from/values/asyncIterator remain explicit earlier source gaps; no complete stream/web support.']};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n');await writeFile(join(here,'component-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({output,zeroImports:true,constructors:calls[0].constructors,codecs:calls[0].codecs,cancellations:calls[0].cancellations,
  guardCases:calls[0].guardCases,guardDeviations:calls[0].guardDeviations,wasmtimePassed:true}));
