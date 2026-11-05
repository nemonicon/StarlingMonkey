import {readFile,mkdir,statfs} from 'node:fs/promises';
import {dirname,join,relative,resolve,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {descriptor,regular,need,hash} from '../ownership-component-candidate-v1/authority.mjs';
import {DurableOutput} from '../ownership-component-candidate-v1/durable.mjs';
import {runOwnedCommand} from '../ownership-component-candidate-v1/durable-host.mjs';
import {checkOwnedTerminal} from '../ownership-component-candidate-v1/abi.mjs';
import {runtimePreflight} from './guard.mjs';
import {nodeOracle,checkOracle} from './oracle.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
const local=(root,path)=>{const n=relative(root,path);need(n&&!isAbsolute(n)&&!n.startsWith('../')&&n.split('/').every(v=>v&&v!=='.'&&v!=='..'),'Only owned descendant');return n;};
async function rowAt(path){const b=await readFile(path);return descriptor({path,sha256:hash(b),bytes:b.length});}
export async function runGc(config){
 const frame=await runtimePreflight(descriptor(config)),space=await statfs(dirname(frame.outputRoot));need(space.bavail*space.bsize>=2*1024**3,'Operational free-space guard');const out=await DurableOutput.create(frame.outputRoot),sessions=[];
 try{
  const oracle=await nodeOracle();await out.write('node-oracle.json',oracle,{json:true});checkOracle(oracle);await mkdir(join(out.root,'processes'),{mode:0o700});
  for(const scenario of ['retained','fresh','wrapper']){
   const registered=new Set(),terminal=await runOwnedCommand({output:out.root,name:scenario,executable:frame.node.path,args:[join(HERE,'worker.mjs'),JSON.stringify(frame.configRow),scenario],write:(path,bytes)=>out.write(local(out.root,path),bytes),register:path=>registered.add(path),timeoutMs:frame.workerTimeoutMs,maxOutputBytes:16*1024*1024,onProgress:v=>process.stdout.write(JSON.stringify({event:'crypto-gc-operational-heartbeat',...v})+'\n')});
   for(const path of registered){const r=await rowAt(path);out.rows.set(local(out.root,path),{path:local(out.root,path),sha256:r.sha256,bytes:r.bytes});}checkOwnedTerminal(terminal);
   const root=join(out.root,scenario),completion=JSON.parse(await readFile(join(root,'completion.json')));need(completion.state==='CRYPTO_OWNER355_GC_WORKER_COMPLETE_EXTERNAL_EXIT_ZERO_REQUIRED'&&completion.scenario===scenario,'Exact ordinary worker completion');
   const indexRow=descriptor({path:join(root,'index.json'),sha256:completion.index.sha256,bytes:completion.index.bytes}),ix=JSON.parse(await regular(indexRow));need(ix.schemaVersion===1&&ix.files.length>1&&ix.files.length<32,'Finite full worker inventory');const seen=new Set();
   for(const r of ix.files){const path=join(root,r.path),n=local(root,path);need(n===r.path&&!seen.has(n),'Unique worker member');seen.add(n);await regular({path,sha256:r.sha256,bytes:r.bytes});out.rows.set(scenario+'/'+n,{path:scenario+'/'+n,sha256:r.sha256,bytes:r.bytes});}
   for(const name of ['index.json','completion.json']){const r=await rowAt(join(root,name));out.rows.set(scenario+'/'+name,{path:scenario+'/'+name,sha256:r.sha256,bytes:r.bytes});}
   const resultRow=descriptor({path:join(root,completion.result.path),sha256:completion.result.sha256,bytes:completion.result.bytes}),result=JSON.parse(await regular(resultRow));need(result.sourceIndexSha256===frame.sourceIndexSha256&&result.allCompletePublicChecksPassed===true&&result.publicStringReturns===(scenario==='retained'?15:scenario==='fresh'?7:1),'Expected complete session and count');need(result.publicGcPressureRequestsObserved===(scenario==='retained'?48:16)&&result.publicGcPressureRecordsObserved===result.publicGcPressureRequestsObserved&&result.actualNativeGcCountObserved===false,'Exact scoped public pressure counts, no native collection count');sessions.push({scenario,result:resultRow,terminal:await rowAt(terminal.terminalPath),publicStringReturns:result.publicStringReturns,publicGcPressureRequestsObserved:result.publicGcPressureRequestsObserved});
  }
  await frame.recheck();await out.recheck();const result=await out.write('results.json',{schemaVersion:1,state:'CRYPTO_OWNER355_GC_RUNTIME_COMPLETE_UNREVIEWED_V1',sourceIndexSha256:frame.sourceIndexSha256,rootAction:frame.rootAction,component:frame.artifacts.component,nodeOracle:'node-oracle.json',sessions,publicStringReturns:23,guestKeyImports:10,guestSignCalls:55,guestVerifyCalls:50,gcVariantOnly:true,publicGcPressureRequestsObserved:sessions.reduce((n,s)=>n+s.publicGcPressureRequestsObserved,0),expectedScopedRequests:{retained:48,fresh:16,wrapper:16},actualNativeGcCountObserved:false,generatedModuleImported:true,asyncScalarReturnedOrdinaryStrings:true,threeFreshOwnedProcesses:true,fullRawPublicReturnsRetainedBeforeAssertions:true,wasmtimeExecuted:false,publicBufferPressureFixtureExecuted:true,oomOrResetExecuted:false,nativeFreeOrWipeOrIsolatedRootObserved:false,operationalAdmission:false,runtimeAcceptanceClaim:false},{json:true});
  const index=await out.write('index.json',{schemaVersion:1,files:[...out.rows.values()]},{json:true});const completion=await out.write('completion.json',{schemaVersion:1,state:'CRYPTO_OWNER355_GC_RUNTIME_COMPLETE_EXTERNAL_PARENT_ZERO_AND_REVIEW_REQUIRED',index,result},{json:true});await out.recheck();return {root:out.root,index,completion};
 }catch(error){try{await out.write('failure.json',{schemaVersion:1,state:'FAILED_CRYPTO_GC_RUNTIME_NO_ACCEPTANCE',thrownType:typeof error,completedSessions:sessions.length},{json:true});}catch{}throw error;}finally{try{await frame.recheck();}finally{await out.close();}}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){need(process.argv.length===3,'One exact new Root config descriptor');process.stdout.write(JSON.stringify(await runGc(JSON.parse(process.argv[2])))+'\n');}
