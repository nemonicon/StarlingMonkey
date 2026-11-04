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
const output=resolve(process.env.NODE_COMPAT_STREAM_DATAVIEW_OUTPUT??'/tmp/starling-node-compat/foundations-v6/stream-web-dataview-v1');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex'),metadata=JSON.parse(await readFile(engine+'.build.json'));
assert.equal(hash(await readFile(engine)),metadata.engineSha256);
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');assert.equal(metadata.oomTesting,false);
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);
const toolchain=await loadToolchain(),{componentize,provenance}=await loadComponentizer(toolchain);
const{componentWit,transpile}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const version=spawnSync(wasmtime,['--version'],{encoding:'utf8'});assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
try{await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'),'dir');}catch(error){if(error.code!=='EEXIST')throw error;}
const expected={...JSON.parse(await readFile(join(here,'node-results.json'))),
  typedViews:JSON.parse(await readFile(join(here,'../candidate/typed-view-node-results.json'))),
  guards:JSON.parse(await readFile(join(here,'../candidate/byob-node-results.json')))};
const bundled=await bundleProfile({...toolchain,input:join(here,'component.mjs'),builtinManifests:selectedManifestsForEngine(metadata,{sourceRoot}),
  virtualModules:{'node-compat:stream-dataview-oracle':'export default '+JSON.stringify(expected)+';'}});
assert.deepEqual(bundled.imports,[]);await writeFile(join(output,'application.bundle.mjs'),bundled.code);
const{component,interfaceAudit}=await componentize(bundled.code,{engine,witWorld:await readFile(join(here,'../profile.wit'),'utf8'),worldName:'profile',
  disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});
const path=join(output,'dataview.component.wasm');await writeFile(path,component);
const wit=await componentWit(component);assert.deepEqual(wit.split('\n').filter(line=>/^\s*import /.test(line)),[]);await writeFile(join(output,'dataview.wit'),wit);
const{files}=await transpile(component,{name:'dataview'});
for(const[file,bytes]of Object.entries(files)){const target=join(output,file);await mkdir(dirname(target),{recursive:true});await writeFile(target,bytes);}
const instance=await import(pathToFileURL(join(output,'dataview.js'))),calls=[];
function check(report,index){assert(!report.failure,JSON.stringify(report.failure));assert(report.passed);assert.equal(report.calls,index);
  assert.equal(report.cases,expected.cases.length);assert(report.nativeReaderIdentity&&report.originalDescriptorsRestored);
  assert.equal(report.originalNativeDataViewCalls,0);assert.equal(report.typedViews,12);assert.equal(report.guardCases,24);
  assert.equal(report.policies.checks.length,6);assert.equal(report.intrinsics.replacementInvocations,0);
  assert.deepEqual(report.deviations,[{name:'released-reader-rejects-before-transfer',nodeCode:'ERR_INVALID_STATE',candidateCode:'absent'}]);}
for(let index=1;index<=2;index++){const report=JSON.parse(await instance.run());calls.push(report);await writeFile(join(output,'calls.json'),JSON.stringify(calls,null,2)+'\n');check(report,index);}
const host=spawnSync(wasmtime,['run','--invoke','run()',path],{encoding:'utf8',timeout:180000,maxBuffer:1024*1024});
await writeFile(join(output,'wasmtime.log'),JSON.stringify(host,null,2)+'\n');assert.equal(host.status,0,host.error?.message||host.stderr);
const wasmtimeReport=JSON.parse(JSON.parse(host.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,hex)=>String.fromCodePoint(parseInt(hex,16)))));
check(wasmtimeReport,1);assert.deepEqual(wasmtimeReport,calls[0]);
const sourcePaths=['adapter.mjs','cases.mjs','policy.mjs','node-oracle.mjs','node-results.json','component.mjs','run-component.mjs',
  '../candidate/factory.mjs','../candidate/fixture-record.mjs','../candidate/typed-view-cases.mjs','../candidate/typed-view-node-results.json',
  '../candidate/guard-cases.mjs','../candidate/byob-node-results.json'];
const result={schema:1,atUtc:new Date().toISOString(),scope:'ISOLATED uninstalled DataView BYOB adapter over captured native Uint8Array read',
  engine,engineSha256:metadata.engineSha256,sourceRoot,metadata,componentizer:provenance,
  component:{path,bytes:component.length,sha256:hash(component),emittedImports:[],emittedWit:wit,interfaceAudit},
  sourceManifest:await Promise.all(sourcePaths.map(async path=>({path,sha256:hash(await readFile(join(here,path)))}))),
  calls,wasmtime:version.stdout.trim(),wasmtimeReport,
  limitations:['No production registration or native class capture/brand callback compiled','Ordinary local native stream receivers only; no proxy/cross-realm proof',
    'Parent codec/guard limits and compression/WDC.signal deferrals remain unchanged','Default/min1 only; DataView always adapted to Uint8Array before original native read']};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n');await writeFile(join(here,'component-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({output,cases:calls[0].cases,zeroImports:true,wasmtimePassed:true}));
