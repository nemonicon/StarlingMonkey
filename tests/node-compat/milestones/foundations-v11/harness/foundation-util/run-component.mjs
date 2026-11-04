import assert from 'node:assert/strict';
import * as nodeUtil from 'node:util';
import * as nodeTypes from 'node:util/types';
import * as nodeSys from 'node:sys';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {loadToolchain} from '../toolchain.mjs';
import {loadComponentizer} from '../componentizer.mjs';
import {bundleProfile} from '../profile-bundler.mjs';
import {selectedManifestsForEngine} from '../module-selection.mjs';
import {runComponentCases} from './component-cases.mjs';
const here=dirname(fileURLToPath(import.meta.url)),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const engine=resolve(process.env.NODE_COMPAT_ENGINE??'/tmp/starling-node-compat/foundations-v6/native-freeze/off-foundations.engine.wasm');
const metadataBytes=await readFile(engine+'.build.json'),metadata=JSON.parse(metadataBytes),engineSha256=hash(await readFile(engine));
assert.equal(engineSha256,'33b9cb248afbb4a3b3653c7b76bd656e51443e6823fa72d712758c742cd59516');assert.equal(metadata.engineSha256,engineSha256);
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');assert.equal(metadata.observedCMakeOptions.WEVAL,'OFF');assert.equal(metadata.entropyPolicy,'off');assert.equal(metadata.strictInitialization,true);
for(const name of ['gcStress','oomTesting','debuggerEnabled','wptSupportEnabled'])assert.equal(metadata[name],false);
assert.equal(metadata.sourceInputsCapturedBeforeBuild,true);assert.equal(metadata.sourceManifest.length,285);
const sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT??'/tmp/starling-node-compat/foundations-v6/native-freeze/source');
async function verifyNative(){for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);assert.equal(hash(await readFile(engine)),engineSha256);assert.equal(hash(await readFile(engine+'.build.json')),hash(metadataBytes));}
await verifyNative();
const output=resolve(process.env.NODE_COMPAT_UTIL_OUTPUT??'/tmp/starling-node-compat/foundation-util/component-v1');await mkdir(output,{recursive:true});await writeFile(join(output,'started.json'),JSON.stringify({atUtc:new Date().toISOString(),engine,engineSha256})+'\n',{flag:'wx'});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
const files=['run-component.mjs','component-cases.mjs','prototype-component.mjs','prototype.wit','prototype-core.mjs','prototype-unsupported.mjs','prototype-metadata.mjs','types-prototype.mjs','util-prototype.mjs','sys-prototype.mjs','prototype-scope.json','prototype-scope.mjs'];
const sources=[];await mkdir(join(output,'source'),{recursive:true});for(const name of files){const bytes=await readFile(join(here,name));await writeFile(join(output,'source',name),bytes);sources.push({name,sha256:hash(bytes)});}
const scope=JSON.parse(await readFile(join(here,'prototype-scope.json'))),inventory=JSON.parse(await readFile(join(here,'node-inventory.json')));
assert.deepEqual((await import('./prototype-scope.mjs')).default,scope,'ESM scope carrier must exactly match versioned JSON');
const tc=await loadToolchain(),packaging=await loadComponentizer(tc),manifests=selectedManifestsForEngine(metadata,{sourceRoot});assert.equal(packaging.provenance.selection,'patched-import-i32-clock-v2');
const bundle=await bundleProfile({rolldown:tc.rolldown,parseAst:tc.parseAst,input:join(here,'prototype-component.mjs'),builtinManifests:manifests});assert.deepEqual(bundle.imports,[]);await writeFile(join(output,'application.bundle.mjs'),bundle.code);
const preview2Adapter=join(sourceRoot,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'),adapterSha256=hash(await readFile(preview2Adapter));assert.equal(adapterSha256,'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const wit=await readFile(join(here,'prototype.wit'),'utf8'),options={engine,witWorld:wit,worldName:'profile',disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[],preview2Adapter};
const{component,interfaceAudit}=await packaging.componentize(bundle.code,options),componentPath=join(output,'util-prototype.component.wasm');await writeFile(componentPath,component);
const{componentWit,transpile}=await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco'))),emittedWit=await componentWit(component);assert.deepEqual(emittedWit.split('\n').filter(line=>/^\s*import /.test(line)),[]);assert.match(emittedWit,/export run: func\(\) -> string;/);await writeFile(join(output,'component.wit'),emittedWit);
const{files:generated}=await transpile(component,{name:'util-prototype'});for(const[name,bytes]of Object.entries(generated)){const path=join(output,name);await mkdir(dirname(path),{recursive:true});await writeFile(path,bytes);}
const guest=await import(pathToFileURL(join(output,'util-prototype.js'))),reports=[];let oracle;
async function validate(report,call){
  assert(!report.failure,report.failure);assert.equal(report.calls,call);assert.equal(report.snapshotIdentityPreserved,true);assert.equal(report.nodeOnlyNativeHelperDelegation,false);
  for(const[key,id]of [['utilExports','node:util'],['sysExports','node:util'],['typeExports','node:util/types']])assert.deepEqual(report[key],inventory.modules.find(value=>value.id===id).exports);
  if(!oracle)oracle=await runComponentCases({util:nodeUtil,types:nodeTypes,sys:nodeSys,predicateNames:scope.typesImplemented,features:report.features});
  assert.equal(report.checks,oracle.checks);assert.deepEqual(report.observations,oracle.observations);assert.deepEqual(report.explicitLimits,oracle.explicitLimits);
  assert.equal(report.deferred.length,108);assert(report.deferred.every(value=>value.code==='ERR_SM_NODE_UNSUPPORTED'));
}
for(let call=1;call<=2;call++){const report=JSON.parse(guest.run());reports.push(report);await writeFile(join(output,'progress.json'),JSON.stringify(reports,null,2)+'\n');await validate(report,call);}
const wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
const host=spawnSync(wasmtime,['run','--invoke','run()',componentPath],{encoding:'utf8',timeout:120000,maxBuffer:2097152});await writeFile(join(output,'wasmtime.stdout'),host.stdout??'');await writeFile(join(output,'wasmtime.stderr'),host.stderr??'');assert.equal(host.status,0,host.error?.message??host.stderr);
const wave=host.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,number)=>String.fromCodePoint(parseInt(number,16))),hostReport=JSON.parse(JSON.parse(wave));await validate(hostReport,1);
const initialization=[];
for(const[name,source,marker]of [
  ['inspect-call',`import {inspect} from ${JSON.stringify(join(here,'util-prototype.mjs'))};inspect({});export function run(){return ''}`,'node:util.inspect is deferred'],
  ['callsites-new',`import {getCallSites} from ${JSON.stringify(join(here,'util-prototype.mjs'))};new getCallSites();export function run(){return ''}`,'node:util.getCallSites is deferred'],
  ['proxy-predicate',`import {isProxy} from ${JSON.stringify(join(here,'types-prototype.mjs'))};isProxy({});export function run(){return ''}`,'node:util/types.isProxy is deferred'],
  ['sys-callbackify',`import {callbackify} from ${JSON.stringify(join(here,'sys-prototype.mjs'))};callbackify(()=>{});export function run(){return ''}`,'node:util.callbackify is deferred'],
]){
  const entry=join(output,name+'.mjs');await writeFile(entry,source);const negative=await bundleProfile({rolldown:tc.rolldown,parseAst:tc.parseAst,input:entry,builtinManifests:manifests});assert.deepEqual(negative.imports,[]);let error;try{await packaging.componentize(negative.code,options);}catch(caught){error=String(caught);}assert(error?.includes(marker),name+' top-level must fail');initialization.push({name,sourceSha256:hash(source),bundleSha256:hash(negative.code),rejected:true,marker,error});
}
await verifyNative();for(const entry of sources)assert.equal(hash(await readFile(join(here,entry.name))),entry.sha256,entry.name);
const result={schemaVersion:1,state:'isolated-ordinary-component-prototype-passed',atUtc:new Date().toISOString(),engine,engineSha256,engineMetadataSha256:hash(metadataBytes),sourceRoot,nativeSourcesVerifiedBeforeAndAfter:285,sources,sourcesCapturedBeforeAndVerifiedAfter:true,packaging:packaging.provenance,options,adapterSha256,bundleSha256:hash(bundle.code),componentPath,componentSha256:hash(component),componentBytes:component.length,emittedImports:[],emittedWit,interfaceAudit,oracle:{node:process.version,executable:process.execPath,executableSha256:hash(await readFile(process.execPath)),sharedCases:oracle},reports,wasmtime:{executable:wasmtime,sha256:hash(await readFile(wasmtime)),report:hostReport},initialization,scope:'Local real ESM util/types/sys prototypes bundled into a frozen-v6 Release application; NOT registered node:util/native module integration. Actual installed native TextEncoder/Decoder identities preserved. No Node-only native-helper delegation, private engine inspection, DEBUG/fault or host capability. Cross-realm/SAB limits explicit. CommonJS builtin admission/resolution remains untested until an actual selected util manifest/install exists.'};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({state:result.state,componentSha256:result.componentSha256,checks:reports[0].checks,predicateFeatures:reports[0].features,limits:reports[0].explicitLimits,retainedJcoCalls:2,freshWasmtimeCalls:1,deferredChecks:reports[0].deferred.length,initialization:initialization.length,emittedImports:[],output},null,2));
