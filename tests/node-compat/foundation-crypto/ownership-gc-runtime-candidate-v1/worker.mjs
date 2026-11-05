// Only the main guard below can enter the actual generated module.
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {descriptor,need} from '../ownership-component-candidate-v1/authority.mjs';
import {DurableOutput} from '../ownership-component-candidate-v1/durable.mjs';
import {runtimePreflight} from './guard.mjs';
import {loadSession} from './loading.mjs';
import {zeroCounters,nextRun,runRecord,inspectRecord,clearRecord,validateRecord} from './checks.mjs';
import {EXPECTED} from './checks.mjs';
export async function runWorker(config,scenario){
 need(['retained','fresh','wrapper'].includes(scenario),'Finite ordinary scenario');const frame=await runtimePreflight(descriptor(config)),out=await DurableOutput.create(join(frame.outputRoot,scenario));let seq=0,rawWritten=0;
 try{
  const session=await loadSession(frame),oracle={tagHex:EXPECTED},gcExpected=frame.expectedRecord;let pressureRequestsObserved=0,pressureRecordsObserved=0;
  async function call(name,args){
   let value;try{value=session.invoke(name,args);}catch(error){await out.write('raw/'+String(++seq).padStart(3,'0')+'.json',{name,args,kind:'throw',thrownType:typeof error,error:error instanceof Error?{name:error.name,message:error.message}:null},{json:true});rawWritten++;throw error;}
   // Retain the COMPLETE public primitive before type/length/JSON assertions.
   await out.write('raw/'+String(++seq).padStart(3,'0')+'.json',{name,args,kind:'return',returnedType:typeof value,...(typeof value==='string'?{value}:{opaque:true,fullOpaqueValueClaim:false})},{json:true});rawWritten++;
   need(typeof value==='string'&&value.length<=2*1024*1024,'Ordinary complete bounded string; no guessed async loader');return JSON.parse(value);
  }
  let c=zeroCounters();
  if(scenario==='wrapper'){const value=await call('validate',[]);validateRecord(value,oracle,gcExpected);pressureRequestsObserved=value.gcObservation.publicGcPressureRequests;pressureRecordsObserved=value.gcObservation.publicGcPressureRecords;c={inspectCalls:2,runCalls:4,clearCalls:1,validateCalls:1,keyImportsAttempted:2,keyImportsFulfilled:2,signCalls:11,verifyCalls:10};}
  else{
   c.inspectCalls++;inspectRecord(await call('inspect',[]),c,false,false,gcExpected);
   for(let rotation=0;rotation<(scenario==='retained'?3:1);rotation++)for(let id=0;id<4;id++){c=nextRun(c,id);const value=await call('run',[id]);runRecord(value,id,c,oracle,gcExpected);pressureRequestsObserved+=value.gcObservation.publicGcPressureRequests;pressureRecordsObserved+=value.gcObservation.publicGcPressureRecords;}
   c.clearCalls++;clearRecord(await call('clear',[]),c,gcExpected);c.inspectCalls++;inspectRecord(await call('inspect',[]),c,false,false,gcExpected);
  }
  await session.recheck();await frame.recheck();await out.recheck();const result=await out.write('results.json',{schemaVersion:1,state:'CRYPTO_OWNER355_GC_SESSION_COMPLETE_EXTERNAL_ZERO_REQUIRED',scenario,sourceIndexSha256:frame.sourceIndexSha256,publicStringReturns:seq,finalCounters:c,publicGcPressureRequestsObserved:pressureRequestsObserved,publicGcPressureRecordsObserved:pressureRecordsObserved,actualNativeGcCountObserved:false,allCompletePublicChecksPassed:true,asyncGuestScalarObservedAsOrdinaryString:true,generatedModuleImported:true,onlyNewGuardedComponent:true,applicationReferencesReleased:true,nativeFreeOrWipeOrIsolatedRootObserved:false,resetOrRequestReuseClaim:false,operationalAdmission:false,runtimeAcceptanceClaim:false},{json:true});
  const index=await out.write('index.json',{schemaVersion:1,files:[...out.rows.values()]},{json:true});await out.write('completion.json',{schemaVersion:1,state:'CRYPTO_OWNER355_GC_WORKER_COMPLETE_EXTERNAL_EXIT_ZERO_REQUIRED',scenario,index,result},{json:true});await out.recheck();return {root:out.root,publicStringReturns:seq};
 }catch(error){try{await out.write('failure.json',{schemaVersion:1,state:'FAILED_CRYPTO_GC_SESSION_NO_ACCEPTANCE',scenario,rawReturnRecordAttempts:seq,rawReturnRecordsRetained:rawWritten,thrownType:typeof error},{json:true});}catch{}throw error;}finally{try{await frame.recheck();}finally{await out.close();}}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){need(process.argv.length===4,'One exact config descriptor and finite scenario');process.stdout.write(JSON.stringify(await runWorker(JSON.parse(process.argv[2]),process.argv[3]))+'\n');}
