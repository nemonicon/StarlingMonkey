// INJECTED SOURCE TEMPLATE ONLY. No CLI entry, loader call or action on import.
// A future independently reviewed real owned launcher/phase guard is REQUIRED.
import {need,nValue,primary,controlIds,POLICY} from './planner.mjs';
import {CompactCollector,compactCase,decodeRetainedString} from './collector.mjs';
import {typed} from '../cost-jco-correctness-candidate-v2/transport.mjs';
export function workerDescriptorModel(v){
 need(v?.schemaVersion===1&&['pilot-candidate','timing'].includes(v.phase),'explicit bounded phase');
 const c=compactCase(v.expected);primary(c.caseId);nValue(c.caseId,v.n);
 need(v.comparison==='same-engine-provider'||v.comparison==='unused-profile','two original comparisons');
 need(v.warmups===3&&v.samples===(v.phase==='timing'?7:1),'original3warmups/7samples; pilot separately1');
 need(v.publicCallHardMs===600000&&Number.isSafeInteger(v.workerTimeoutMs)&&v.workerTimeoutMs>0&&v.workerTimeoutMs<=7200000,'finite hard bounds');
 // These are DESCRIPTOR references, not boolean authority carriers. The future
 // parent must authenticate the actual Root/peer/phase/quiet-window files.
 for(const name of ['rootAuthority','sourceIndependentReviewIndex','phaseAuthority','quietWindowAuthority']){
  const r=v[name];need(r&&typeof r.path==='string'&&/^[a-f0-9]{64}$/.test(r.sha256)&&Number.isSafeInteger(r.bytes)&&r.bytes>0,'actual separately authenticated '+name);
 }
 need(v.phase==='pilot-candidate'?v.warmNPlan===null:v.warmNPlan&&/^[a-f0-9]{64}$/.test(v.warmNPlan.sha256),'timing requires actual matched-N plan; pilot does not issue it');
 need(!Object.hasOwn(v,'oracle')&&!Object.hasOwn(v,'proofReport')&&!Object.hasOwn(v,'fullCorrectnessResult'),'no huge host proof/oracle DATA in owned worker');return true;
}
export async function injectedWorker({descriptor,session,clock,write,recheck}){
 workerDescriptorModel(descriptor);const job=structuredClone(descriptor),collector=new CompactCollector(job.expected);let sequence=0;
 need(session&&typeof session.invoke==='function'&&typeof session.recheck==='function','actual reviewed synchronous ESM/TLA session shape');
 need(typeof clock?.nowNs==='function'&&typeof write==='function'&&typeof recheck==='function','future real monotonic clock/durable owned writer/source recheck');
 // Caller must already have authenticated sources/proofs, the exact descriptor
 // and the new phase action; this injected function is NOT an admission guard.
 async function call(name,args,label,timed){
  need(['identity','setup','batch','checkpoint'].includes(name),'timing never observes/stages/validates');
  const prefix=String(sequence++).padStart(4,'0')+'-'+label;
  await write(prefix+'-before.json',{schemaVersion:1,name,args,partial:true,timed});
  let returned,thrown,failed=false,start,end,clockFailure=null;
  // Only the synchronous public call is inside this monotonic interval. It
  // includes provider operation(s), every output-byte FNV and guest JSON/wire
  // conversion. Host evidence writes, parsing and assertions follow the clock.
  start=clock.nowNs();
  try{returned=session.invoke(name,args);}catch(error){failed=true;thrown=error;}
  finally{try{end=clock.nowNs();}catch(error){clockFailure=typed(error);}}
  const elapsed=typeof start==='bigint'&&typeof end==='bigint'?end-start:null;
  const raw=await write(prefix+'-raw.json',{schemaVersion:1,name,args,timed,elapsedNs:typeof elapsed==='bigint'?elapsed.toString():null,
   clockFailure,
   ...(failed?{thrown:typed(thrown)}:{returned:typed(returned)}),partial:true});
  need(!failed,'complete typed throw retained BEFORE failure');
  need(clockFailure===null&&typeof elapsed==='bigint'&&elapsed>0n&&elapsed<=600000000000n,'positive finite monotonic public-call interval');
  const receipt={...raw,fullPrimitiveCaptured:typeof returned==='string',fsynced:true};
  const value=decodeRetainedString(returned,receipt);return{value,raw,elapsedNs:elapsed.toString(),name,args,timed};
 }
 const controls=[];const codec=[];
 try{
  await recheck();const identity=await call('identity',[],'identity-before',false);collector.identity(identity.value);
  const setup=await call('setup',[job.expected.caseId],'setup',false);collector.setup(setup.value);
  for(const id of controlIds(job.expected.caseId)){const r=await call('batch',[id,1],'control-before-'+id,true);collector.control(r.value,id);controls.push(r);}
  for(let i=0;i<3;i++){const r=await call('batch',[job.expected.caseId,job.n],'warmup-'+i,true);collector.batch(r.value,job.n);codec.push({...r,role:'warmup'});}
  for(let i=0;i<job.samples;i++){const r=await call('batch',[job.expected.caseId,job.n],'sample-'+i,true);collector.batch(r.value,job.n);codec.push({...r,role:'sample'});}
  for(const id of controlIds(job.expected.caseId)){const r=await call('batch',[id,1],'control-after-'+id,true);collector.control(r.value,id);controls.push(r);}
  const checkpoint=await call('checkpoint',[],'checkpoint',false);collector.checkpoint(checkpoint.value);
  const after=await call('identity',[],'identity-after',false);collector.identity(after.value);
  const counts=collector.counters;need(counts.codecCalls===job.n*(3+job.samples)&&counts.controlOperations===6,'exact codec/control totals');
  need(counts.perExportEntries.observe===0&&counts.perExportEntries.stage===0&&counts.perExportEntries.validate===0,'no untimed payload exports in measured worker');
  await session.recheck();await recheck();
  return await write('worker-results.json',{schemaVersion:1,state:'CODEC_COST_PHASE_WORKER_UNREVIEWED_RAW_AND_EXTERNAL_ZERO_REQUIRED_V1',
   phase:job.phase,comparison:job.comparison,arm:job.expected.arm,caseId:job.expected.caseId,n:job.n,
   controls,codec,counts,finalSourceAuditPassed:true,externalOwnedTerminalRequired:true,controlSubtraction:false,
   guestHeapBytesOrCapacityClaim:false,wholeNodeProcessRssScopeOnly:true,operationalAdmission:false,runtimeAcceptanceClaim:false});
 }catch(error){let audit=false;try{await session.recheck();await recheck();audit=true;}catch{}
  await write('worker-failure.json',{schemaVersion:1,state:'CODEC_COST_PHASE_WORKER_FAILED_UNACCEPTED',thrown:typed(error),
   fullPartialRawRetained:true,postFailureSourceAuditPassed:audit,codecObserved:codec.length,controlsObserved:controls.length});throw error;
 }
}
