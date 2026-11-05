// Imported only after the stdlib-only entry authenticates all source/Root/actual data.
import {readFile,mkdir,statfs} from 'node:fs/promises';
import {dirname,join,relative,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {descriptor,regular,need,hash} from '../ownership-component-candidate-v1/authority.mjs';
import {DurableOutput} from '../ownership-component-candidate-v1/durable.mjs';
import {runOwnedCommand} from '../ownership-component-candidate-v1/durable-host.mjs';
import {checkOwnedTerminal} from '../ownership-component-candidate-v1/abi.mjs';
import {loadSession} from './loading.mjs';
import {nodeOracle,checkOracle} from './oracle.mjs';
import {EXPECTED,zeroCounters,nextRun,runRecord,inspectRecord,clearRecord,validateRecord} from './checks.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
const local=(root,path)=>{const n=relative(root,path);need(n&&!isAbsolute(n)&&!n.startsWith('../')&&n.split('/').every(v=>v&&v!=='.'&&v!=='..'),'Only owned descendant');return n;};
async function rowAt(path){const b=await readFile(path);return descriptor({path,sha256:hash(b),bytes:b.length});}
export function primitive(value){
 const type=typeof value;if(type==='string'||type==='boolean'||value===null)return{type,value};
 if(type==='undefined')return{type};
 if(type==='number')return{type,...(Number.isFinite(value)?Object.is(value,-0)?{special:'negative-zero'}:{value}:{special:Number.isNaN(value)?'NaN':value===Infinity?'positive-infinity':'negative-infinity'})};
 if(type==='bigint')return{type,decimal:BigInt.prototype.toString.call(value)};
 // No getters, toJSON, coercion, Symbol description or Proxy introspection.
 return{type,opaque:true,fullOpaqueValueClaim:false};
}
export async function capturedCall({invoke,name,args,write,sequence,onCaptureFailure}){
 const id=++sequence.attempted;let value,thrown=false;
 try{value=invoke(name,args);}catch(error){value=error;thrown=true;}
 const row={schemaVersion:1,name,args,kind:thrown?'throw':'return',observed:primitive(value)};
 try{await write('raw/'+String(id).padStart(3,'0')+'.json',row);sequence.written++;}
 catch(captureError){
  // Host-only auxiliary state retains the actual writer value without touching X.
  const failure=Object.freeze({sequence:id,name,kind:row.kind,captureError});
  (sequence.captureFailures??=[]).push(failure);
  if(onCaptureFailure!==undefined)try{need(typeof onCaptureFailure==='function','Diagnostic callback must be a host function');await onCaptureFailure(failure);}catch(diagnosticError){(sequence.diagnosticFailures??=[]).push(Object.freeze({scope:'capture-failure-callback',diagnosticError}));}
  if(thrown)throw value; // Even falsy/primitive/frozen X; never replace with Y or Z.
  throw captureError;
 }
 if(thrown)throw value; // Exact original throw after successful typed retention.
 need(typeof value==='string'&&value.length<=2*1024*1024,'Complete ordinary bounded string, never await/coerce unexpected return');return JSON.parse(value);
}
export function captureFailureDiagnostics(sequence){
 return{captureWriteFailures:(sequence.captureFailures??[]).map(r=>({sequence:r.sequence,name:r.name,kind:r.kind,observed:primitive(r.captureError)})),captureDiagnosticFailures:(sequence.diagnosticFailures??[]).map(r=>({scope:r.scope,observed:primitive(r.diagnosticError)}))};
}
export async function diagnosticWrite({write,name,value,sequence}){
 try{await write(name,value);return true;}catch(diagnosticError){(sequence.diagnosticFailures??=[]).push(Object.freeze({scope:name,diagnosticError}));return false;}
}
async function finalProtection(frame,session,out){
 const errors=[];for(const[scope,fn]of [['generated-artifact',()=>session?.recheck()],['native-api-package-source',()=>frame.recheck()],['owned-output',()=>out.recheck()]])try{await fn();}catch(error){errors.push({scope,thrown:primitive(error)});}return errors;
}
export async function runWorker(frame,scenario){
 need(frame?.kind==='secret355-normal-runtime-admission-v3'&&['retained','fresh','wrapper'].includes(scenario),'New exact admitted scenario');
 const out=await DurableOutput.create(join(frame.outputRoot,scenario)),sequence={attempted:0,written:0};let session=null,primary=null,primaryValue,finalErrors=[],c=zeroCounters();
 try{
  try{
   await out.write('retained-record-data.json',frame.retainedRecordData,{json:true});await out.write('retained-record-shape.json',frame.retainedRecordShape,{json:true});
   session=await loadSession(frame);const oracle={tagHex:EXPECTED};
   const call=(name,args)=>capturedCall({invoke:session.invoke,name,args,write:(p,v)=>out.write(p,v,{json:true}),sequence,onCaptureFailure:failure=>out.write('capture-write-failure-'+String(failure.sequence).padStart(3,'0')+'.json',{schemaVersion:1,sequence:failure.sequence,name:failure.name,kind:failure.kind,observed:primitive(failure.captureError),rawRecordRetained:false,diagnosticOnly:true},{json:true})});
   if(scenario==='wrapper'){
    validateRecord(await call('validate',[]),oracle);c={inspectCalls:2,runCalls:4,clearCalls:1,validateCalls:1,keyImportsAttempted:2,keyImportsFulfilled:2,signCalls:11,verifyCalls:10};
   }else{
    c.inspectCalls++;inspectRecord(await call('inspect',[]),c,false,false);
    for(let rotation=0;rotation<(scenario==='retained'?3:1);rotation++)for(let id=0;id<4;id++){c=nextRun(c,id);runRecord(await call('run',[id]),id,c,oracle);}
    c.clearCalls++;clearRecord(await call('clear',[]),c);c.inspectCalls++;inspectRecord(await call('inspect',[]),c,false,false);
   }
  }catch(error){primary=primitive(error);primaryValue=error;}
  finally{finalErrors=await finalProtection(frame,session,out);}
  if(primary!==null||finalErrors.length||(sequence.captureFailures?.length??0)||(sequence.diagnosticFailures?.length??0)){await diagnosticWrite({write:(p,v)=>out.write(p,v,{json:true}),name:'failure.json',sequence,value:{schemaVersion:1,state:'FAILED_SECRET355_NORMAL_SESSION_NO_ACCEPTANCE_V3',scenario,rawCallAttempts:sequence.attempted,rawRecordsWritten:sequence.written,allAttemptedRawRecordsWritten:sequence.attempted===sequence.written,primary,...captureFailureDiagnostics(sequence),finalProtectionErrors:finalErrors,partialEvidenceOnly:true,operationalAdmission:false}});if(primary!==null)throw primaryValue;throw new Error('Secret355 session final protection failed; retained observations');}
  need(sequence.attempted===sequence.written&&(sequence.captureFailures?.length??0)===0&&(sequence.diagnosticFailures?.length??0)===0,'No missing raw or diagnostic failure');
  const result=await out.write('results.json',{schemaVersion:1,state:'SECRET355_NORMAL_SESSION_COMPLETE_EXTERNAL_ZERO_REQUIRED_V3',scenario,sourceIndexSha256:frame.sourceIndexSha256,component:frame.artifacts.component,publicStringReturns:sequence.written,rawCallAttempts:sequence.attempted,rawRecordsWritten:sequence.written,finalCounters:c,allCompletePublicChecksPassed:true,fullRawBeforeAssertions:true,generatedModuleImported:true,asyncGuestScalarObservedAsOrdinaryString:true,onlyNewGuardedSecret355Component:true,applicationReferencesReleased:true,nativeFreeOrWipeOrIsolatedRootObserved:false,resetOrRequestReuseClaim:false,gcOrOomOrFaultOrPressureExecuted:false,finalProtectionErrors:[],operationalAdmission:false,runtimeAcceptanceClaim:false},{json:true});
  await out.recheck();const index=await out.write('index.json',{schemaVersion:1,files:[...out.rows.values()]},{json:true});await out.write('completion.json',{schemaVersion:1,state:'SECRET355_NORMAL_WORKER_COMPLETE_EXTERNAL_EXIT_ZERO_REQUIRED_V3',scenario,index,result},{json:true});await out.recheck();return{root:out.root,publicStringReturns:sequence.written};
 }finally{await out.close();}
}
export async function runParent(frame){
 need(frame?.kind==='secret355-normal-runtime-admission-v3','New exact runtime admission');const space=await statfs(dirname(frame.outputRoot));need(space.bavail*space.bsize>=2*1024**3,'Operational2GiB start guard');
 const out=await DurableOutput.create(frame.outputRoot),sessions=[],failureSequence={attempted:0,written:0};let primary=null,primaryValue,finalErrors=[];
 try{
  try{
   await out.write('retained-record-data.json',frame.retainedRecordData,{json:true});await out.write('retained-record-shape.json',frame.retainedRecordShape,{json:true});
   const oracle=await nodeOracle();await out.write('node-oracle.json',oracle,{json:true});checkOracle(oracle);
   // Genuine donor lifecycle requires this directory before ordinary()/spawn.
   await mkdir(join(out.root,'processes'),{mode:0o700});
   for(const scenario of ['retained','fresh','wrapper']){
    const registered=new Set(),terminal=await runOwnedCommand({output:out.root,name:scenario,executable:frame.node.path,args:[join(HERE,'entry.mjs'),'worker',JSON.stringify(frame.configRow),scenario],write:(path,bytes)=>out.write(local(out.root,path),bytes),register:path=>registered.add(path),timeoutMs:frame.workerTimeoutMs,maxOutputBytes:16*1024*1024,onProgress:v=>process.stdout.write(JSON.stringify({event:'secret355-normal-operational-heartbeat',...v})+'\n')});
    // Register available streams BEFORE asserting the terminal/semantic result.
    for(const path of registered){const r=await rowAt(path);out.rows.set(local(out.root,path),{path:local(out.root,path),sha256:r.sha256,bytes:r.bytes});}
    checkOwnedTerminal(terminal);
    const root=join(out.root,scenario),completion=JSON.parse(await readFile(join(root,'completion.json')));need(completion.state==='SECRET355_NORMAL_WORKER_COMPLETE_EXTERNAL_EXIT_ZERO_REQUIRED_V3'&&completion.scenario===scenario,'Exact whole worker completion');
    const ixRow=descriptor({path:join(root,'index.json'),sha256:completion.index.sha256,bytes:completion.index.bytes}),ix=JSON.parse(await regular(ixRow));need(ix.schemaVersion===1&&ix.files.length>1&&ix.files.length<32,'Finite worker inventory');const seen=new Set();
    for(const r of ix.files){const path=join(root,r.path),n=local(root,path);need(n===r.path&&!seen.has(n),'Unique confined member');seen.add(n);await regular({path,sha256:r.sha256,bytes:r.bytes});out.rows.set(scenario+'/'+n,{path:scenario+'/'+n,sha256:r.sha256,bytes:r.bytes});}
    for(const name of ['index.json','completion.json']){const r=await rowAt(join(root,name));out.rows.set(scenario+'/'+name,{path:scenario+'/'+name,sha256:r.sha256,bytes:r.bytes});}
    const resultRow=descriptor({path:join(root,completion.result.path),sha256:completion.result.sha256,bytes:completion.result.bytes}),result=JSON.parse(await regular(resultRow));need(result.sourceIndexSha256===frame.sourceIndexSha256&&result.allCompletePublicChecksPassed===true&&result.publicStringReturns===(scenario==='retained'?15:scenario==='fresh'?7:1)&&result.rawCallAttempts===result.rawRecordsWritten&&result.finalProtectionErrors.length===0,'Whole complete raw-return count/protection');sessions.push({scenario,result:resultRow,terminal:await rowAt(terminal.terminalPath),publicStringReturns:result.publicStringReturns});
   }
  }catch(error){primary=primitive(error);primaryValue=error;}
  finally{finalErrors=await finalProtection(frame,null,out);}
  if(primary!==null||finalErrors.length){await diagnosticWrite({write:(p,v)=>out.write(p,v,{json:true}),name:'failure.json',sequence:failureSequence,value:{schemaVersion:1,state:'FAILED_SECRET355_NORMAL_RUNTIME_NO_ACCEPTANCE_V3',completedSessions:sessions,primary,...captureFailureDiagnostics(failureSequence),finalProtectionErrors:finalErrors,partialEvidenceOnly:true,operationalAdmission:false}});if(primary!==null)throw primaryValue;throw new Error('Secret355 runtime final protection failed; no completion');}
  const result=await out.write('results.json',{schemaVersion:1,state:'SECRET355_NORMAL_RUNTIME_COMPLETE_UNREVIEWED_V3',sourceIndexSha256:frame.sourceIndexSha256,rootAction:frame.rootAction,component:frame.artifacts.component,nodeOracle:'node-oracle.json',sessions,publicStringReturns:23,guestCaseRecords:20,guestKeyImports:10,guestSignAttempts:55,guestVerifyAttempts:50,successfulGuestSignatureFullBytesCompared:45,normalOnly:true,generatedModuleImported:true,threeFreshOwnedNodeProcesses:true,fullRawPublicReturnsRetainedBeforeAssertions:true,wasmtimeExecuted:false,gcOrOomOrFaultOrPressureOrResetExecuted:false,nativeFreeOrWipeOrIsolatedRootObserved:false,finalProtectionErrors:[],operationalAdmission:false,runtimeAcceptanceClaim:false},{json:true});
  await out.recheck();const index=await out.write('index.json',{schemaVersion:1,files:[...out.rows.values()]},{json:true});const completion=await out.write('completion.json',{schemaVersion:1,state:'SECRET355_NORMAL_RUNTIME_COMPLETE_EXTERNAL_PARENT_ZERO_AND_REVIEW_REQUIRED_V3',index,result},{json:true});await out.recheck();return{root:out.root,index,completion};
 }finally{await out.close();}
}
