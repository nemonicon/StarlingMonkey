import {verifyProductionV9} from './production-v9-preflight.mjs';
// Valid public WIT interface getters, after Starling's pre-initialization.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {readFile,writeFile,mkdir,symlink} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {loadToolchain} from '../toolchain.mjs';
import {loadComponentizer} from '../componentizer.mjs';
import {decodeCliString} from '../foundations/native-scalar-harness.mjs';
const productionPreflight=await verifyProductionV9();
const hash=x=>createHash('sha256').update(x).digest('hex'),here=dirname(fileURLToPath(import.meta.url));
const engine=resolve(process.env.NODE_COMPAT_ENGINE),sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT),output=resolve(process.env.NODE_COMPAT_STRICT_EVENT_OUTPUT);
await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
const metadata=JSON.parse(await readFile(engine+'.build.json'));assert.equal(hash(await readFile(engine)),metadata.engineSha256);assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');assert.equal(metadata.strictInitialization,true);assert.equal(metadata.oomTesting,false);assert.equal(metadata.strictEventExceptionPolicy?.embeddingBoundaryPatchSha256,hash(await readFile(join(here,'componentize-strict-event-boundary-v2.patch'))));
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);
const toolchain=await loadToolchain(),selected=await loadComponentizer(toolchain);
try{await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'));}catch(error){if(error.code!=='EEXIST')throw error;}
const adapter=resolve(here,'../../../host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');assert.equal(hash(await readFile(adapter)),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const witWorld='package test:late-event-fixed; world test { export inspect-result: func() -> string; export api: interface { run: func() -> string; } }';
const {transpile,componentWit}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco'))),cases=[];
for(const[name,body,rejected,marker]of[
 ['late-event',"const t=new EventTarget();t.addEventListener('test',()=>spawn());t.dispatchEvent(new Event('test'));",true,/child_process\.spawn/],
 ['late-undefined-event',"const t=new EventTarget();t.addEventListener('test',()=>{throw undefined});t.dispatchEvent(new Event('test'));",true,/undefined/],
 ['late-unhandled-promise','Promise.resolve().then(()=>spawn());',true,/child_process\.spawn|ERR_SM_NODE_INITIALIZATION_REJECTION/],
 ['late-handled-promise','const p=Promise.resolve().then(()=>spawn());queueMicrotask(()=>p.catch(()=>{}));',false],
 ['late-caught-event',"const t=new EventTarget();t.addEventListener('test',()=>{try{spawn()}catch(error){handled=error.code}});t.dispatchEvent(new Event('test'));",false],
 ['late-clean','handled=\'clean\';',false],
]){
 const source="import{spawn}from'node:child_process';let getters=0,handled=null;export function inspectResult(){return JSON.stringify({getters,handled,bound:true})}export const api={get run(){getters++;"+body+"return inspectResult}};";
 let built,error;try{built=await selected.componentize(source,{engine,preview2Adapter:adapter,witWorld,worldName:'test',disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});}catch(failure){error=failure.message;}
 const record={name,source,sourceSha256:hash(source),rejected:!!error,error};assert.equal(!!error,rejected,name);if(error&&marker)assert.match(error,marker,name);
 if(built){
  assert.deepEqual(built.interfaceAudit.emittedImports,[]);record.interfaceAudit=built.interfaceAudit;record.emittedWit=await componentWit(built.component);record.componentSha256=hash(built.component);record.componentBytes=built.component.length;
  const path=join(output,name+'.component.wasm');await writeFile(path,built.component);const jsname=name.replaceAll('-','_');const{files}=await transpile(built.component,{name:jsname});for(const[n,bytes]of Object.entries(files)){await mkdir(dirname(join(output,n)),{recursive:true});await writeFile(join(output,n),bytes);}
  const mod=await import(pathToFileURL(join(output,jsname+'.js')));record.jco=[JSON.parse(await mod.inspectResult()),JSON.parse(await mod.api.run())];assert.deepEqual(record.jco[0],record.jco[1]);assert.equal(record.jco[0].getters,1);assert.equal(record.jco[0].bound,true);
  const host=spawnSync(process.env.NODE_COMPAT_WASMTIME,['run','--invoke','inspect-result()',path],{encoding:'utf8',timeout:120000,maxBuffer:2*1024*1024});assert.equal(host.status,0,host.stderr);record.wasmtime={status:host.status,observed:JSON.parse(decodeCliString(host.stdout.trim())),stderr:host.stderr};assert.deepEqual(record.wasmtime.observed,record.jco[0]);
 }
 cases.push(record);console.log(JSON.stringify({name,rejected:!!error}));
}
const report={schemaVersion:1,productionPreflight,state:'production-v9-post-binding-acceptance-passed',recordedAtUtc:new Date().toISOString(),engineSha256:metadata.engineSha256,engineReceipt:metadata,sourceRoot,sourceFilesVerified:metadata.sourceManifest.length,componentizerProvenance:selected.provenance,runnerSha256:hash(await readFile(fileURLToPath(import.meta.url))),cases,limitations:['Valid public WIT interface getters and ordinary Promise/event operations only; no DEBUG/fault/raw memory or malformed carriers.','Rejects both late event errors and late unhandled Promise rejection after draining; handlers attached by a later microtask remain effective.','Actual production v9 guest embedding patch; no host modification.']};
await writeFile(join(output,'production-v9-late-results.json'),JSON.stringify(report,null,2)+'\n');await writeFile(join(here,'production-v9-late-results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({state:report.state,cases:cases.length,output}));
