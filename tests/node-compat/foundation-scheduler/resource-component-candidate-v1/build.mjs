// Future construction parent; entry authenticated every custom dependency first.
import {readFile,mkdir,statfs} from 'node:fs/promises';
import {dirname,join,relative,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {requireConstructionFrame,descriptor,regular,streamHash,hash,need} from './entry.mjs';
import {DurableOutput} from '../../foundation-crypto/ownership-component-candidate-v1/durable.mjs';
import {runOwnedCommand} from '../../foundation-crypto/ownership-component-candidate-v1/durable-host.mjs';
import {checkOwnedTerminal} from '../../foundation-crypto/ownership-component-candidate-v1/abi.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
function child(root,path){const n=relative(root,path);need(n&&!isAbsolute(n)&&n.split('/').every(p=>p&&p!=='.'&&p!=='..'),'Exact owned descendant');return n;}
async function rowAt(path){const b=await readFile(path);return descriptor({path,sha256:hash(b),bytes:b.length});}
async function headroom(path,min){const v=await statfs(path);need(v.bavail*v.bsize>=min,'Operational disk floor, not a space guarantee');}
export async function buildComponent(frame){
 requireConstructionFrame(frame);const {source,native}=frame,{root,refs}=source;await frame.recheck();await headroom(dirname(root.outputRoot),2*1024*1024*1024);
 const output=await DurableOutput.create(root.outputRoot),registered=new Set();
 try{
  const manifests=await output.write('selected-manifests.json',native.selectedManifests,{json:true});
  const d={schemaVersion:1,state:'PARENT_AUDITED_RESOURCE342_COMPONENT_WORKER_V1',sourceIndexSha256:source.sourceSha,constructionConfig:source.configRow,rootAction:source.rootRow,fixture:root.fixture,engine:refs.engine,metadata:refs.metadata,code:refs.fixtures[root.fixture].code,wit:refs.fixtures[root.fixture].wit,selectedManifests:{path:join(output.root,manifests.path),sha256:manifests.sha256,bytes:manifests.bytes},outputRoot:output.root+'/worker'};
  const row=await output.write('worker-descriptor.json',d,{json:true});need(row.bytes<=32768,'Private bounded descriptor; full proofs stay in parent');await mkdir(join(output.root,'processes'),{mode:0o700});await headroom(output.root,800*1024*1024);
  const outcome=await runOwnedCommand({output:output.root,name:'componentize',executable:refs.node.path,args:[join(HERE,'entry.mjs'),source.sourceSha,'worker',JSON.stringify({path:join(output.root,row.path),sha256:row.sha256,bytes:row.bytes})],timeoutMs:root.workerTimeoutMs,maxOutputBytes:16*1024*1024,write:async(path,value)=>output.write(child(output.root,path),typeof value==='string'?Buffer.from(value):value),register:path=>registered.add(path),onProgress:v=>process.stdout.write(JSON.stringify({event:'resource-component-operational-heartbeat',...v})+'\n')});
  for(const path of registered){const r=await rowAt(path),name=child(output.root,path);output.rows.set(name,{...r,path:name});}
  checkOwnedTerminal(outcome); // raw streams and terminal are durable before this assertion
  const worker=join(output.root,'worker'),completionRow=await rowAt(join(worker,'completion.json')),completion=JSON.parse(await regular(completionRow));need(completion.state==='RESOURCE_COMPONENT_WORKER_COMPLETE_EXTERNAL_ZERO_REQUIRED_V1','Actual worker completion');
  const ix={path:join(worker,'index.json'),sha256:completion.index.sha256,bytes:completion.index.bytes},index=JSON.parse(await regular(ix));need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length<=128,'Finite actual worker list');const names=new Set();
  for(const row of index.files){const path=join(worker,row.path),name=child(worker,path);need(row.path===name&&!names.has(name),'Exact unique worker member');names.add(name);await streamHash({...row,path});output.rows.set('worker/'+name,{...row,path:'worker/'+name});}
  for(const path of[ix.path,completionRow.path]){const r=await rowAt(path),name=child(output.root,path);output.rows.set(name,{...r,path:name});}
  await frame.recheck();await output.recheck();
  const result=await output.write('results.json',{schemaVersion:1,state:'RESOURCE342_COMPONENT_CONSTRUCTION_COMPLETE_UNREVIEWED_V1',sourceIndexSha256:source.sourceSha,resourceSourceIndexSha256:refs.resourceSourceIndex.sha256,toolingSourceIndexSha256:refs.toolingIndex.sha256,fixture:root.fixture,rootAction:source.rootRow,bootstrapConfig:refs.bootstrapConfig,actualBootstrapReview:refs.actualBootstrapReview,nativeEngine:refs.engine,metadata:refs.metadata,configuredSourceRoot:native.configuredSourceRoot,frozenSourceRoot:native.sourceRoot,workerCompletion:completionRow,ownedWorkerTerminal:await rowAt(outcome.terminalPath),rawWorkerExitCode:0,ownedGroupGone:true,initializationOnly:true,ordinaryGuestExportsInvoked:false,generatedModuleImported:false,timerRuntimeInvoked:false,operationalAdmission:false,runtimeAcceptanceClaim:false},{json:true});
  const indexRow=await output.write('index.json',{schemaVersion:1,state:'RESOURCE_COMPONENT_OUTPUT_UNREVIEWED_FILES_V1',files:[...output.rows.values()]},{json:true});
  const completed=await output.write('completion.json',{schemaVersion:1,state:'RESOURCE_COMPONENT_PARENT_COMPLETE_EXTERNAL_ZERO_AND_INDEPENDENT_REVIEW_REQUIRED_V1',index:indexRow,result,ordinaryGuestExportsInvoked:false,timerRuntimeInvoked:false},{json:true});await output.recheck();return{root:output.root,index:indexRow,completion:completed};
 }catch(error){try{await output.write('failure.json',{schemaVersion:1,state:'FAILED_RESOURCE_COMPONENT_CONSTRUCTION_NO_ACCEPTANCE',thrownType:typeof error,partialOwnedOutputsRetained:true,ordinaryGuestExportsInvoked:false,timerRuntimeInvoked:false},{json:true});}catch{}throw error;}finally{try{await frame.recheck();}finally{await output.close();}}
}
