// FUTURE parent action. No loader, codec, engine or child at initialization.
import {readFile,mkdir,lstat,readdir,realpath} from 'node:fs/promises';
import {join,dirname,relative,resolve,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {componentPreflight,NODE} from './guard.mjs';
import {descriptor,regular,need,hash} from './authority.mjs';
import {DurableOutput} from './durable.mjs';
import {runOwnedCommand} from './durable-host.mjs';
import {checkOwnedTerminal} from './abi.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
function childName(root,path){const name=relative(root,path);need(name&&!isAbsolute(name)&&!name.startsWith('../')&&!name.includes('\\')&&name.split('/').every(p=>p&&p!=='.'&&p!=='..'),'Owned child output name');return name;}
async function rowAt(path,expectedSha=null){const raw=await readFile(path);need(expectedSha===null||hash(raw)===expectedSha,'Exact critical file');return descriptor({path,sha256:hash(raw),bytes:raw.length});}
export async function buildComponent(options){
 const admitted=await componentPreflight(options);
 // Parent guard performed all proofs and full source/native/tool validation.
 // Worker receives only critical immutable tuples, not those heavy audits.
 const pub=JSON.parse(await regular(admitted.publicationIndex)),critical=[];
 const prefixes=['packaging/tests/node-compat/','tools/packager/src/','tools/packager/lib/','tools/packager/splicer-build.json','tools/packager/package.json','control/'];
 for(const item of pub.files)if(prefixes.some(prefix=>item.path.startsWith(prefix))){
  // Full parent audited all files. Critical worker checks bounded loader/code
  // files; the real selected loader additionally checks actual splicer pins.
  if(item.bytes<=64*1024*1024)critical.push(descriptor({path:join(admitted.publicationRoot,item.path),sha256:item.sha256,bytes:item.bytes}));
 }
 need(critical.length>0&&critical.length<=256,'Bounded critical loader tuple list');
 const engine={path:admitted.enginePath,sha256:admitted.pin.engineSha256,bytes:admitted.pin.engineBytes},metadata=await rowAt(admitted.enginePath+'.build.json',admitted.pin.metadataSha256);
 critical.push(descriptor(engine),metadata);for(const name of['authority.mjs','abi.mjs','collector.mjs','build.mjs','build-worker.mjs','guard.mjs','proofs.mjs','durable.mjs','durable-host.mjs','public-abi.wit'])critical.push(await rowAt(join(HERE,name)));
 for(const name of['authority.mjs','abi.mjs','collector.mjs','proofs.mjs','durable.mjs','durable-host.mjs'])critical.push(await rowAt(join(HERE,'../cost-component-candidate-v1',name)));
 const adapterPath=join(admitted.packagingRoot,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'),adapter=await rowAt(adapterPath,'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');need(adapter.bytes===53512,'Actual53512 adapter');
 await admitted.recheck();const output=await DurableOutput.create(admitted.outputRoot),registered=new Set();
 try{
  await mkdir(join(output.root,'processes'),{mode:0o700});
  const d={schemaVersion:1,state:'PARENT_AUDITED_ZLIB_COST_COMPONENT_WORKER_V1',componentSourceIndexSha256:admitted.componentSourceIndexSha256,toolingSourceIndexSha256:admitted.toolingSourceIndexSha256,guestSourceIndexSha256:admitted.guestSourceIndexSha256,arm:admitted.arm,rootAction:admitted.rootAction,publicationRoot:admitted.publicationRoot,packagingRoot:admitted.packagingRoot,toolchainRoot:admitted.toolchainRoot,packagerRoot:admitted.packagerRoot,outputRoot:output.root+'/worker',code:admitted.codeRow,engine,metadata,adapter,criticalFiles:critical,maxComponentBytes:admitted.maxComponentBytes,ordinaryGuestExportCallsAllowed:false};
  const workerRow=await output.write('worker-descriptor.json',d,{json:true});need(workerRow.bytes<=65536,'Proof-free worker descriptor stays64KiB');
  const workerDescriptor={path:join(output.root,workerRow.path),sha256:workerRow.sha256,bytes:workerRow.bytes};
  const write=async(path,data)=>output.write(childName(output.root,path),typeof data==='string'?Buffer.from(data):data);
  const status=await runOwnedCommand({output:output.root,name:'componentize',executable:NODE.path,args:[join(HERE,'build-worker.mjs'),JSON.stringify(workerDescriptor)],write,register:path=>registered.add(path),timeoutMs:admitted.workerTimeoutMs,maxOutputBytes:16*1024*1024,onProgress:event=>process.stdout.write(JSON.stringify({event:'component-build-operational-heartbeat',...event})+'\n')});
  // Streams/terminal have already been fsynced by the owned helper. Register
  // their exact bytes before any exit/ABI validation assertion.
  for(const path of registered){const r=await rowAt(path);output.rows.set(childName(output.root,path),{path:childName(output.root,path),sha256:r.sha256,bytes:r.bytes});}
  checkOwnedTerminal(status); // terminal was persisted before this assertion
  const workerRoot=join(output.root,'worker'),completionPath=join(workerRoot,'completion.json'),completion=JSON.parse(await readFile(completionPath));
  need(completion.state==='COMPONENT_WORKER_COMPLETE_EXTERNAL_EXIT_ZERO_REQUIRED','Worker completion is not a parity pass');
  const ixPath=join(workerRoot,'index.json'),ixRaw=await readFile(ixPath);need(hash(ixRaw)===completion.index.sha256&&ixRaw.length===completion.index.bytes,'Actual worker index');const ix=JSON.parse(ixRaw),names=new Set();
  for(const item of ix.files){const name=childName(workerRoot,join(workerRoot,item.path));need(!names.has(name),'Unique worker artifact');names.add(name);const path=join(workerRoot,name);await regular({path,sha256:item.sha256,bytes:item.bytes},{maxBytes:64*1024*1024});output.rows.set('worker/'+name,{path:'worker/'+name,sha256:item.sha256,bytes:item.bytes});}
  for(const name of['index.json','completion.json']){const r=await rowAt(join(workerRoot,name));output.rows.set('worker/'+name,{path:'worker/'+name,sha256:r.sha256,bytes:r.bytes});}
  await admitted.recheck();await output.recheck();
  const result=await output.write('results.json',{schemaVersion:1,state:'ZLIB_COST_COMPONENT_BUILD_COMPLETE_UNREVIEWED_V1',arm:admitted.arm,sourceIndexSha256:admitted.componentSourceIndexSha256,toolingSourceIndexSha256:admitted.toolingSourceIndexSha256,sourcePublicationIndexSha256:admitted.publicationIndexSha256,rootAction:admitted.rootAction,code:admitted.codeRow,native:admitted.pin,workerCompletion:{path:completionPath,...await rowAt(completionPath)},ownedWorkerStatus:status.terminalPath,rawWorkerExitCode:0,ownedGroupGone:true,guestInitializationExecutedByComponentization:true,ordinaryGuestExportsInvoked:false,actualFreshWasmtimeStringTransportProved:false,correctnessClaim:false,operationalAdmission:false,timingAllowed:false},{json:true});
  const index=await output.write('index.json',{schemaVersion:1,state:'UNREVIEWED_COMPONENT_BUILD_OUTPUT',files:[...output.rows.values()]},{json:true});
  const complete=await output.write('completion.json',{schemaVersion:1,state:'COMPONENT_BUILD_COMPLETE_EXTERNAL_PARENT_EXIT_ZERO_REQUIRED',index,result,sourceIndexSha256:admitted.componentSourceIndexSha256,ordinaryGuestExportsInvoked:false,timingAllowed:false},{json:true});await output.recheck();return{output:output.root,index,completion:complete};
 }catch(error){try{await output.write('failure.json',{state:'FAILED_COMPONENT_BUILD_NOT_ACCEPTED',thrownType:typeof error,partialOwnedOutputsRetained:true,timingAllowed:false},{json:true});}catch{}throw error;}
 finally{await output.close();}
}
async function main(){need(process.argv.length===3,'One exact external config descriptor JSON');const options=JSON.parse(await regular(JSON.parse(process.argv[2])));const result=await buildComponent(options);process.stdout.write(JSON.stringify(result)+'\n');}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))await main();
