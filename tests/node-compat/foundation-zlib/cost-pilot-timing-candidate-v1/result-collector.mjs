// Pure independent parent replay of all complete typed worker returns.
import {need,controlIds,nValue,metric,COMPARISONS} from './planner.mjs';
import {CompactCollector,decodeRetainedString} from './collector.mjs';
import {same} from './proof-model.mjs';
export function processResourceModel(v){
 const labels=['after-source-authentication-before-loader','after-reviewed-esm-tla-load','after-final-source-audit'];
 need(v&&Array.isArray(v.boundarySamples)&&v.boundarySamples.length===3&&v.boundarySamples.every((s,i)=>s.label===labels[i]&&Number.isSafeInteger(s.rssBytes)&&s.rssBytes>0&&Number.isSafeInteger(s.nodePublicMaxRssKilobytes)&&s.nodePublicMaxRssKilobytes>0),'exact public process boundary samples');
 need(typeof v.reviewedEsmTlaLoadNs==='string'&&/^[1-9][0-9]{0,15}$/.test(v.reviewedEsmTlaLoadNs)&&BigInt(v.reviewedEsmTlaLoadNs)<=7200000000000n,'positive combined ESM/TLA load interval');
 need(Number.isSafeInteger(v.nodePublicMaxRssKilobytes)&&v.nodePublicMaxRssKilobytes>=Math.max(...v.boundarySamples.map(s=>s.nodePublicMaxRssKilobytes))&&v.maxRssUnits==='Node22 resourceUsage API kilobytes'&&v.rssUnits==='bytes','honest whole-process public units');
 need(v.wholeNodeProcessOnly===true&&v.includesAuthenticationAndLoaderOverhead===true&&v.parentHugeProofAndOracleReportsLoaded===false&&v.guestHeapOrCapacityClaim===false&&v.continuousRssSamplingClaim===false&&v.physicallyColdStartupClaim===false,'public process scope, no guest/capacity/cold-cache claim');return true;
}
export function callSchedule(job){
 const id=job.expected.caseId;nValue(id,job.n);const rows=[{name:'identity',args:[],role:'identity-before'},{name:'setup',args:[id],role:'setup'}];
 for(const control of controlIds(id))rows.push({name:'batch',args:[control,1],role:'control-before'});
 for(let i=0;i<3;i++)rows.push({name:'batch',args:[id,job.n],role:'warmup'});
 for(let i=0;i<job.samples;i++)rows.push({name:'batch',args:[id,job.n],role:'sample'});
 for(const control of controlIds(id))rows.push({name:'batch',args:[control,1],role:'control-after'});
 rows.push({name:'checkpoint',args:[],role:'checkpoint'},{name:'identity',args:[],role:'identity-after'});
 need(rows.length===(job.phase==='timing'?20:14),'exact complete call schedule');return rows;
}
export function replayWorker({job,result,rawCalls,terminal}){
 need(terminal?.status===0&&terminal.closed===true&&terminal.ownedGroupGone===true&&terminal.terminalExitZeroObserved===true&&terminal.timedOut===false&&terminal.signal===null&&terminal.spawnError===null&&terminal.externalSignal===null&&terminal.outputLimitExceeded===false&&terminal.errors.length===0&&terminal.signals.length===0,'actual clean owned raw terminal before acceptance');
 need(result.schemaVersion===1&&result.state==='CODEC_COST_PHASE_WORKER_UNREVIEWED_RAW_AND_EXTERNAL_ZERO_REQUIRED_V1'&&result.jobId===job.jobId&&result.phase===job.phase&&result.arm===job.expected.arm&&result.caseId===job.expected.caseId&&result.n===job.n&&result.repetition===job.repetition&&result.side===job.side,'exact newly executed worker identity');
 const schedule=callSchedule(job),collector=new CompactCollector(job.expected),samples=[],controls=[];
 need(Array.isArray(result.records)&&result.records.length===schedule.length&&Array.isArray(rawCalls)&&rawCalls.length===schedule.length,'all primitive records retained, no sample omission');
 for(let i=0;i<schedule.length;i++){
  const want=schedule[i],record=result.records[i],raw=rawCalls[i];need(record.name===want.name&&same(record.args,want.args)&&raw.schemaVersion===1&&raw.name===want.name&&same(raw.args,want.args),'full actual call order/arguments');
  need(raw.returned?.type==='string'&&raw.returned.fullPrimitiveCaptured===true&&raw.returned.codeUnits===raw.returned.value.length&&!Object.hasOwn(raw,'thrown'),'whole typed primitive success');
  const value=decodeRetainedString(raw.returned.value,{...record.raw,fsynced:true,fullPrimitiveCaptured:true});need(same(value,record.value),'parsed record equals complete retained primitive');
  need(record.elapsedNs===raw.elapsedNs&&typeof raw.elapsedNs==='string'&&/^[1-9][0-9]{0,14}$/.test(raw.elapsedNs)&&BigInt(raw.elapsedNs)<=600000000000n&&raw.clockFailure===null,'exact positive full-unit public-call duration');
  if(want.name==='identity')collector.identity(value);else if(want.name==='setup')collector.setup(value);else if(want.name==='checkpoint')collector.checkpoint(value);
  else if(want.args[0]>=30){collector.control(value,want.args[0]);controls.push({role:want.role,id:want.args[0],elapsedNs:raw.elapsedNs,result:value.result});}
  else collector.batch(value,job.n);
  const timed=want.role==='sample'||want.role.startsWith('control-');need(raw.timed===timed&&record.timed===timed,'warmups not admitted samples; controls separate raw timings');
  if(want.role==='sample')samples.push({elapsedNs:raw.elapsedNs,...metric({logicalBytes:job.expected.logicalBytes,n:job.n,elapsedNs:raw.elapsedNs})});
 }
 need(same(result.counts,collector.counters)&&result.counts.codecCalls===(3+job.samples)*job.n&&result.counts.controlOperations===6&&result.finalSourceAuditPassed===true,'complete final counter/source evidence');
 need(result.controlSubtraction===false&&result.guestHeapBytesOrCapacityClaim===false&&result.wholeNodeProcessRssScopeOnly===true,'no subtraction or guest memory claim');
 processResourceModel(result.processResources);
 need(samples.length===job.samples&&controls.length===6,'all raw measured samples and controls');
 const compressedBytes=job.expected.direction==='encode'?job.expected.outputBytes:job.expected.inputBytes;
 return{schemaVersion:1,jobId:job.jobId,pid:terminal.pid,phase:job.phase,comparison:job.comparison,repetition:job.repetition,side:job.side,arm:job.expected.arm,caseId:job.expected.caseId,n:job.n,
  direction:job.expected.direction,inputBytesPerOperation:job.expected.inputBytes,outputBytesPerOperation:job.expected.outputBytes,logicalUncompressedBytesPerOperation:job.expected.logicalBytes,compressedBytesPerOperation:compressedBytes,compressedToRawRatio:job.expected.logicalBytes===0?null:compressedBytes/job.expected.logicalBytes,
  warmups:3,samples:job.samples,freshOwnedProcess:true,sampleMs:job.phase==='pilot-candidate'?Number(BigInt(samples[0].elapsedNs))/1e6:null,
  measuredSamples:samples,rawControls:controls,counts:collector.counters,rawExitCode:0,ownedGroupGone:true,cleanTerminal:true,
  allRawRetained:true,finalSourceAuditPassed:true,wholeProcessMs:terminal.operationalElapsedMs,
  processResources:result.processResources,controlSubtraction:false};
}
export function aggregateTiming(rows){
 need(Array.isArray(rows)&&rows.length===360&&new Set(rows.map(v=>v.jobId)).size===360&&new Set(rows.map(v=>v.pid)).size===360,'all original fresh timing workers before report');const groups=[];
 for(const spec of COMPARISONS)for(let caseId=0;caseId<30;caseId++){
  const comparison=spec.id,selected=rows.filter(v=>v.comparison===comparison&&v.caseId===caseId);need(selected.length===6,'two arms with three fresh repetitions');
  const arms=[spec.A,spec.B];need(selected.every(v=>arms.includes(v.arm)),'exact separate comparison arms');
  groups.push({comparison,caseId,arms:arms.map(arm=>{const workers=selected.filter(v=>v.arm===arm);need(workers.length===3&&new Set(workers.map(v=>v.repetition)).size===3&&workers.every(v=>[0,1,2].includes(v.repetition)&&v.measuredSamples.length===7&&v.side===(arm===spec.A?'A':'B')),'three independent process units; seven correlated samples each');
   const units=workers.map(v=>{const values=v.measuredSamples.map(x=>Number(BigInt(x.elapsedNs))/1e6).sort((a,b)=>a-b);return{n:v.n,withinWorkerMedianMs:values[3],allSevenSamples:v.measuredSamples,processResources:v.processResources,inputBytesPerOperation:v.inputBytesPerOperation,outputBytesPerOperation:v.outputBytesPerOperation,compressedBytesPerOperation:v.compressedBytesPerOperation,compressedToRawRatio:v.compressedToRawRatio};});
   return{arm,independentFreshProcessUnits:units,pooledWithinWorkerSamplesTreatedIndependent:false};})});
 }
 return{schemaVersion:1,groups,workerCount:360,codecBatchCalls:3600,rawN1ControlOperations:2160,controlsSubtracted:false,
  sameEngineProviderAndUnusedProfileSeparate:true,guestHeapOrCapacityClaim:false,universalPerformanceWinClaim:false};
}
