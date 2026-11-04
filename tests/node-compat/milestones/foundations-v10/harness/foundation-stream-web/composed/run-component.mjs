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
assert.equal(process.version,'v22.14.0');
for(const key of ['NODE_COMPAT_ENGINE','NODE_COMPAT_WASMTIME','NODE_COMPAT_ENGINE_SOURCE_ROOT'])assert(process.env[key],key);
const here=dirname(fileURLToPath(import.meta.url)),engine=resolve(process.env.NODE_COMPAT_ENGINE);
const sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT),wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME);
const output=resolve(process.env.NODE_COMPAT_STREAM_COMPOSED_OUTPUT??'/tmp/starling-node-compat/foundations-v6/stream-web-composed-v1');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex'),metadata=JSON.parse(await readFile(engine+'.build.json'));
assert.equal(hash(await readFile(engine)),metadata.engineSha256);
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');assert.equal(metadata.oomTesting,false);
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);
const toolchain=await loadToolchain(),{componentize,provenance}=await loadComponentizer(toolchain);
const{componentWit,transpile}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const version=spawnSync(wasmtime,['--version'],{encoding:'utf8'});assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
try{await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'),'dir');}catch(error){if(error.code!=='EEXIST')throw error;}
const expected={};
for(const[key,path]of Object.entries({codecs:'candidate/codec-node-results.json',guards:'candidate/byob-node-results.json',views:'candidate/typed-view-node-results.json',
  controllers:'candidate/controller-node-results.json',iteration:'iteration/node-results.json',data:'dataview/node-results.json'}))
  expected[key]=JSON.parse(await readFile(join(here,'../'+path)));
const bundled=await bundleProfile({...toolchain,input:join(here,'component.mjs'),builtinManifests:selectedManifestsForEngine(metadata,{sourceRoot}),
  virtualModules:{'node-compat:stream-composed-oracles':'export default '+JSON.stringify(expected)+';'}});
assert.deepEqual(bundled.imports,[]);await writeFile(join(output,'application.bundle.mjs'),bundled.code);
const{component,interfaceAudit}=await componentize(bundled.code,{engine,witWorld:await readFile(join(here,'../profile.wit'),'utf8'),worldName:'profile',
  disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});
const path=join(output,'composed.component.wasm');await writeFile(path,component);
const wit=await componentWit(component);assert.deepEqual(wit.split('\n').filter(line=>/^\s*import /.test(line)),[]);await writeFile(join(output,'composed.wit'),wit);
const{files}=await transpile(component,{name:'composed'});
for(const[file,bytes]of Object.entries(files)){const target=join(output,file);await mkdir(dirname(target),{recursive:true});await writeFile(target,bytes);}
const instance=await import(pathToFileURL(join(output,'composed.js'))),calls=[];
function check(report,index){assert(!report.failure,JSON.stringify(report.failure));assert(report.passed);assert.equal(report.calls,index);
  assert(report.nativeIdentities&&report.originalDescriptorsRestored);
  for(const[key,count]of Object.entries({constructors:41,codecs:250,cancellations:4,guards:24,views:12,controllers:6,iterations:67,data:26}))assert.equal(report[key],count,key);
  assert.deepEqual(report.guardDeviations,['min-two','proxy-genuine-receiver','shadowed-view-fields']);
  assert.deepEqual(report.dataDeviations,['released-reader-rejects-before-transfer']);
  assert.equal(report.policies.checks.length,16);assert.equal(report.dataPolicies.checks.length,6);
  assert.equal(report.ownErrors.checks,10);assert.equal(report.ownErrors.inheritedGets,0);assert.equal(report.ownErrors.inheritedSets,0);
  for(const key of ['codecIntrinsics','iterationIntrinsics','dataIntrinsics'])assert.equal(report[key].replacementInvocations,0);
}
for(let index=1;index<=2;index++){const report=JSON.parse(await instance.run());calls.push(report);await writeFile(join(output,'calls.json'),JSON.stringify(calls,null,2)+'\n');check(report,index);}
const host=spawnSync(wasmtime,['run','--invoke','run()',path],{encoding:'utf8',timeout:180000,maxBuffer:1024*1024});
await writeFile(join(output,'wasmtime.log'),JSON.stringify(host,null,2)+'\n');assert.equal(host.status,0,host.error?.message||host.stderr);
const wasmtimeReport=JSON.parse(JSON.parse(host.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,hex)=>String.fromCodePoint(parseInt(hex,16)))));
check(wasmtimeReport,1);assert.deepEqual(wasmtimeReport,calls[0]);
const sourcePaths=['checks.mjs','component.mjs','run-component.mjs','../production-candidate/factory.mjs','../production-candidate/codecs.mjs',
  '../production-candidate/readable-iteration.mjs','../production-candidate/byob.mjs',
  '../candidate/fixture-record.mjs','../candidate/codec-cases.mjs','../candidate/codec-node-results.json','../candidate/guard-cases.mjs','../candidate/byob-node-results.json',
  '../candidate/policy-cases.mjs','../candidate/factory.mjs','../candidate/typed-view-cases.mjs','../candidate/typed-view-node-results.json',
  '../candidate/controller-cases.mjs','../candidate/controller-node-results.json','../iteration/cases.mjs','../iteration/node-results.json','../iteration/intrinsics.mjs',
  '../dataview/cases.mjs','../dataview/node-results.json','../dataview/policy.mjs'];
const result={schema:1,atUtc:new Date().toISOString(),scope:'ISOLATED composed uninstalled stream/web m0.9 source candidate; native capture still fixture-only',
  engine,engineSha256:metadata.engineSha256,sourceRoot,metadata,componentizer:provenance,
  component:{path,bytes:component.length,sha256:hash(component),emittedImports:[],emittedWit:wit,interfaceAudit},
  sourceManifest:await Promise.all(sourcePaths.map(async path=>({path,sha256:hash(await readFile(join(here,path)))}))),
  calls,wasmtime:version.stdout.trim(),wasmtimeReport,
  limitations:['No production registration or native class capture/brand callback compiled','Ordinary local native stream receivers only; no proxy/cross-realm proof',
    'Fixed/attached/unshared inputs, min1 only; compression/WDC.signal/proxy/cross-realm gaps remain explicit','No total application queue/lifetime limit; each outstanding iterator call retains a serialized promise operation']};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n');await writeFile(join(here,'component-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({output,codecs:calls[0].codecs,iterations:calls[0].iterations,data:calls[0].data,zeroImports:true,wasmtimePassed:true}));
