// Real future parent orchestration. Import alone runs no action.
import {dirname,join,relative,isAbsolute,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {mkdir,readFile,statfs} from 'node:fs/promises';
import {descriptor,regular,hash} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {DurableOutput} from '../cost-jco-correctness-candidate-v2/durable.mjs';
import {typed} from '../cost-jco-correctness-candidate-v2/transport.mjs';
import {runOwnedCommand} from './owned-lifecycle.mjs';
import {readOnlyParentProofAudit,contractedProof,exactMembership,CALIBRATION_DECISION} from './parent-guard.template.mjs';
import {need,COMPARISONS,candidateNs,chooseMatchedN,matchedPlan,timingSchedule} from './planner.mjs';
import {remainingBudget} from './lifecycle-policy.mjs';
import {same} from './proof-model.mjs';
import {replayWorker,aggregateTiming} from './result-collector.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),nowMs=()=>Number(process.hrtime.bigint()/1000000n);
function child(root,path){const name=relative(root,path);need(name&&!isAbsolute(name)&&!name.startsWith('../')&&!name.includes('\\')&&name.split('/').every(v=>v&&v!=='.'&&v!=='..'),'exact owned child path');return name;}
async function disk(minimum){const v=await statfs('/private/tmp/starling-node-compat');need(v.bavail*v.bsize>=minimum,'operational disk gate; no capacity guarantee');}
export async function runPhase(options){
 const admitted=await readOnlyParentProofAudit(options),root=admitted.root;let warm=null,matched=null;
 if(root.phase==='timing'){
  warm=await contractedProof(root.warmNPlan,'INDEPENDENT_ZLIB_COST_PILOT_RESULTS_REVIEW_PASSED_V1');
  need(warm.data.sourceIndexSha256===options.sourceIndex.sha256&&warm.data.calibrationDecisionSha256===CALIBRATION_DECISION&&warm.data.allMatchedNReviewed===true&&warm.data.allOwnedWorkersRawZeroClean===true&&warm.data.pilotOnly===true&&warm.data.timingAllowed===false,'separate actual pilot review with complete60case calibration');
  const computed=matchedPlan(warm.data.calibrations),row=descriptor(root.warmNMatchedPlan);need(same(row,warm.contract.requiredExactDescriptors.matchedPlan),'actual matched-N plan bound by independent pilot contract');
  matched=JSON.parse(await regular(row,{maxBytes:128*1024}));need(matched.schemaVersion===1&&matched.state==='ACTUAL_MATCHED_N_PLAN_DATA_V1'&&same(matched.rows,computed),'all actual120arm matched-N/budget rows recomputed');
 }else need(root.warmNMatchedPlan===null,'pilot has no accepted warmN plan');
 await disk(2*1024**3);await admitted.recheck();admitted.checkWindow();const phaseStarted=nowMs(),output=await DurableOutput.create(root.outputRoot),origins=[],observations=[],calibrations=[];
 const write=(name,value)=>output.write(name,value,{json:true});
 try{
  await mkdir(join(output.root,'jobs'),{mode:0o700});await mkdir(join(output.root,'processes'),{mode:0o700});
  async function execute({comparison,caseId,arm,n,repetition=null,side,jobId,workerTimeoutMs}){
   remainingBudget({startMs:phaseStarted,nowMs:nowMs(),globalBudgetMs:root.globalBudgetMs,workerBudgetMs:workerTimeoutMs});admitted.checkWindow(root.globalBudgetMs-(nowMs()-phaseStarted));await disk(800*1024**2);
   const expected=admitted.expected.filter(c=>c.caseId===caseId&&c.arm===arm);need(expected.length===1,'one exact compact expected case');
   const value={schemaVersion:1,phase:root.phase,comparison,repetition,side,jobId,n,expected:expected[0],warmups:3,samples:root.phase==='timing'?7:1,
    publicCallHardMs:600000,workerTimeoutMs,sourceIndexSha256:options.sourceIndex.sha256,sourceIndex:options.sourceIndex,
    rootAuthority:admitted.rootAction,sourceIndependentReviewIndex:root.sourceIndependentReview.index,phaseAuthority:admitted.phaseRow,quietWindowAuthority:admitted.quietRow,
    preparedPlan:admitted.planRow,warmNPlan:root.warmNMatchedPlan,parentOutputRoot:output.root,outputRoot:join(output.root,'jobs',jobId),artifact:admitted.artifacts[arm]};
   const row=await write('descriptors/'+jobId+'.json',value),input=descriptor({path:join(output.root,row.path),sha256:row.sha256,bytes:row.bytes}),registered=new Set();need(row.bytes<=65536,'compact descriptor, not giant CLI data');
   const status=await runOwnedCommand({output:output.root,name:jobId,executable:admitted.refs.node.path,args:[join(HERE,'worker.mjs'),JSON.stringify(input)],
    write:(path,data)=>output.write(child(output.root,path),data),register:path=>registered.add(path),timeoutMs:workerTimeoutMs,publicCallTimeoutMs:600000,phaseDeadlineMonotonicMs:phaseStarted+root.globalBudgetMs,maxOutputBytes:1048576,onProgress:event=>process.stdout.write(JSON.stringify({event:'codec-phase-operational-heartbeat',...event})+'\n')});
   for(const path of registered){const raw=await readFile(path),name=child(output.root,path);output.rows.set(name,{path:name,sha256:hash(raw),bytes:raw.length});}
   // runOwnedCommand has already fsynced both pipes and terminal BEFORE assertions.
   need(status.terminalExitZeroObserved&&status.ownedGroupGone&&status.status===0&&status.errors.length===0&&status.signals.length===0&&status.stderrFile.bytes===0,'actual clean owned child, no failure/partial adoption');
   const workerRoot=value.outputRoot,indexBytes=await readFile(join(workerRoot,'index.json')),index=JSON.parse(indexBytes),completeBytes=await readFile(join(workerRoot,'completion.json')),complete=JSON.parse(completeBytes);
   need(complete.state==='CODEC_PHASE_WORKER_COMPLETE_EXTERNAL_OWNED_ZERO_REQUIRED_V1'&&complete.jobId===jobId&&complete.sourceIndexSha256===options.sourceIndex.sha256&&complete.index.sha256===hash(indexBytes)&&complete.index.bytes===indexBytes.length&&same(complete.component,value.artifact.component),'exact newly executed worker completion');
   need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length>0&&index.files.length<=128,'bounded worker inventory');const names=new Set();
   for(const item of index.files){const name=child(workerRoot,join(workerRoot,item.path));need(name===item.path&&!names.has(name),'unique worker-local member');names.add(name);const actual={path:join(workerRoot,name),sha256:item.sha256,bytes:item.bytes};await regular(actual,{maxBytes:64*1024*1024});output.rows.set(child(output.root,actual.path),{path:child(output.root,actual.path),sha256:item.sha256,bytes:item.bytes});}
   await exactMembership(workerRoot,[...names,'index.json','completion.json']);
   for(const[name,raw]of[['index.json',indexBytes],['completion.json',completeBytes]])output.rows.set(child(output.root,join(workerRoot,name)),{path:child(output.root,join(workerRoot,name)),sha256:hash(raw),bytes:raw.length});
   const rr=index.files.find(r=>r.path==='worker-results.json');need(rr&&same(rr,complete.results),'actual indexed worker result/completion');const result=JSON.parse(await regular({path:join(workerRoot,rr.path),sha256:rr.sha256,bytes:rr.bytes})),rawCalls=[];
   for(const record of result.records){const rawRow=index.files.find(r=>r.path===record.raw.path);need(rawRow&&same(rawRow,record.raw),'each raw primitive indexed exactly');rawCalls.push(JSON.parse(await regular({path:join(workerRoot,rawRow.path),sha256:rawRow.sha256,bytes:rawRow.bytes})));}
   const observed=replayWorker({job:value,result,rawCalls,terminal:status});observations.push(observed);
   origins.push({jobId,arm,comparison,caseId,n,repetition,side,pid:status.pid,terminal:child(output.root,status.terminalPath),result:{path:join(workerRoot,rr.path),sha256:rr.sha256,bytes:rr.bytes},component:value.artifact.component});
   need(new Set(origins.map(v=>v.pid)).size===origins.length,'every pilot/timing unit is a fresh owned process');return observed;
  }
  if(root.phase==='pilot-candidate'){
   for(const comparison of COMPARISONS)for(let caseId=0;caseId<30;caseId++){
    const curve=[];let selected=null;
    for(const n of candidateNs(caseId)){
     const arms=[];for(const side of['A','B']){const arm=comparison[side];arms.push(await execute({comparison:comparison.id,caseId,arm,n,side,jobId:'pilot-'+(comparison.id==='same-engine-provider'?'provider':'profile')+'-c'+caseId+'-n'+n+'-'+arm,workerTimeoutMs:600000}));}
     curve.push({comparison:comparison.id,caseId,n,arms});
     if(arms.every(v=>v.sampleMs>=50)){selected=chooseMatchedN(curve,caseId,comparison.id);break;}
    }
    need(selected,'entire phase refuses if either arm cannot reach target at case cap');calibrations.push(selected);await write('calibration/'+comparison.id+'-c'+caseId+'.json',{curve,selected});
   }
   need(calibrations.length===60,'all original cases/comparisons before warmN publication');await write('matched-n-plan.json',{schemaVersion:1,state:'ACTUAL_MATCHED_N_PLAN_DATA_V1',rows:matchedPlan(calibrations),independentReviewStillRequired:true});
  }else{
   for(const spec of timingSchedule()){
    const match=matched.rows.filter(v=>v.comparison===spec.comparison&&v.caseId===spec.caseId&&v.arm===spec.arm);need(match.length===1,'all original timed workers have actual matchedN');
    await execute({...spec,...match[0],jobId:'timing-'+(spec.comparison==='same-engine-provider'?'provider':'profile')+'-c'+spec.caseId+'-r'+spec.repetition+'-'+spec.arm});
   }
   await write('aggregate-observations.json',aggregateTiming(observations));
  }
  await admitted.recheck();if(warm)await warm.recheck();remainingBudget({startMs:phaseStarted,nowMs:nowMs(),globalBudgetMs:root.globalBudgetMs,workerBudgetMs:1});admitted.checkWindow(1);await output.recheck();
  const result=await write('results.json',{schemaVersion:1,state:'CODEC_COST_PHASE_COMPLETE_UNREVIEWED_EXTERNAL_ZERO_AND_INDEPENDENT_REVIEW_REQUIRED_V1',phase:root.phase,sourceIndexSha256:options.sourceIndex.sha256,calibrationDecisionSha256:CALIBRATION_DECISION,rootAuthority:admitted.rootAction,origins,observations,calibrations,
   actualWorkers:origins.length,rawN1ControlOperations:origins.length*6,codecBatchCalls:origins.length*(root.phase==='timing'?10:4),
   sourceRecheckPassed:true,allOwnedWorkersRawZeroClean:true,sourceDesignSelected:true,actualComponentSizesDataOnly:Object.fromEntries(Object.entries(admitted.artifacts).map(([arm,v])=>[arm,v.component.bytes])),controlsSubtracted:false,metadataProjection:false,operationalAdmission:false,runtimeAcceptanceClaim:false,timingAcceptanceClaim:false});
  const index=await write('index.json',{schemaVersion:1,files:[...output.rows.values()]}),completion=await write('completion.json',{schemaVersion:1,state:'CODEC_PHASE_COMPLETE_EXTERNAL_PARENT_ZERO_AND_REVIEW_REQUIRED_V1',result,index,sourceIndexSha256:options.sourceIndex.sha256});await output.recheck();return{index,completion};
 }catch(error){let audit=false;try{await admitted.recheck();if(warm)await warm.recheck();audit=true;}catch{}try{await write('failure.json',{schemaVersion:1,state:'CODEC_COST_PHASE_FAILED_UNACCEPTED',thrown:typed(error),completedOrigins:origins,partialRawRetained:true,postFailureSourceAuditPassed:audit,operationalAdmission:false});}catch{}throw error;}
 finally{await output.close();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 need(process.argv.length===3,'one exact future Root config descriptor');const options=JSON.parse(await regular(JSON.parse(process.argv[2])));process.stdout.write(JSON.stringify(await runPhase(options))+'\n');
}
