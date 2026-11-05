// Actual owned-child entry, dormant until a future separately authorized launch.
import {join,dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {realpath} from 'node:fs/promises';
import {descriptor,regular} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {deepFreeze,local} from '../cost-jco-correctness-candidate-v2/proofs.mjs';
import {DurableOutput} from '../cost-jco-correctness-candidate-v2/durable.mjs';
import {streamHash} from '../cost-tooling-candidate-v3/context.mjs';
import {typed} from '../cost-jco-correctness-candidate-v2/transport.mjs';
import {phaseAuthorityModel} from './parent-guard.template.mjs';
import {same,quietWindowModel} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';
import {MEASUREMENT_ENV} from '../cost-pilot-timing-candidate-v1/lifecycle-policy.mjs';
import {createParentHandshake} from '../cost-pilot-timing-candidate-v1/public-call-channel.mjs';
import {need} from '../cost-pilot-timing-candidate-v1/planner.mjs';
import {loadTimingSession} from '../cost-pilot-timing-candidate-v1/loading.mjs';
import {injectedWorker,workerDescriptorModel} from '../cost-pilot-timing-candidate-v1/worker.template.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
export async function runWorker(input){
 const inputRow=descriptor(input),v=deepFreeze(JSON.parse(await regular(inputRow,{maxBytes:65536})));workerDescriptorModel(v);
 const rootRow=descriptor(v.rootAuthority),root=deepFreeze(JSON.parse(await regular(rootRow)));phaseAuthorityModel(root,v.sourceIndexSha256);
 need(v.parentOutputRoot===root.outputRoot&&v.outputRoot===root.outputRoot+'/jobs/'+v.jobId&&inputRow.path===root.outputRoot+'/descriptors/'+v.jobId+'.json','exact parent-owned descriptor/job namespace');
 need(/^[A-Za-z0-9][A-Za-z0-9_-]{0,159}$/.test(v.jobId)&&v.phase===root.phase,'finite exact phase/job');
 need(same(v.phaseAuthority,root.phaseAuthority)&&same(v.quietWindowAuthority,root.quietWindowAuthority)&&same(v.preparedPlan,root.preparedPlan)&&same(v.warmNPlan,root.warmNMatchedPlan),'same Root phase/plan/window descriptors');
 need(same(v.sourceIndependentReviewIndex,root.sourceIndependentReview.index),'same actual independent source peer');
 need(process.version==='v22.14.0'&&process.execArgv.length===0&&same(Object.fromEntries(Object.entries(process.env).sort()),Object.fromEntries(Object.entries(MEASUREMENT_ENV).sort())),'exact pinned plain Node/environment, no inherited overrides');
 const ownIx=descriptor(v.sourceIndex),index=JSON.parse(await regular(ownIx));need(ownIx.path===join(HERE,'index.json')&&ownIx.sha256===v.sourceIndexSha256&&Array.isArray(index.files)&&index.files.length<=512,'exact immutable own source');
 const rows=[];for(const row of index.files){local(row.path);need(row.bytes<=4*1024*1024,'compact source-only worker intake, no huge proof/oracle report');rows.push(descriptor({path:join(HERE,row.path),sha256:row.sha256,bytes:row.bytes}));}
 const depsRow=rows.find(r=>r.path===join(HERE,'worker-dependencies.json'));need(depsRow,'indexed physical worker import closure');const deps=JSON.parse(await regular(depsRow));need(Array.isArray(deps.files)&&deps.files.length>0&&deps.files.length<=256,'finite actual worker module closure');
 const dependencies=deps.files.map(descriptor);for(const row of dependencies)need(row.bytes<=4*1024*1024,'small dependency source only');
 const refsRow=rows.find(r=>r.path===join(HERE,'references.json')),refs=JSON.parse(await regular(refsRow)),node=descriptor(refs.node);need(await realpath(process.execPath)===node.path,'actual pinned executable path');await streamHash(node,{maximumBytes:128*1024*1024});
 const planRow=descriptor(v.preparedPlan),plan=deepFreeze(JSON.parse(await regular(planRow,{maxBytes:128*1024})));need(plan.sourceIndexSha256===ownIx.sha256&&plan.state==='PREPARED_COMPACT_CODEC_MEASUREMENT_PLAN_DATA_ONLY_V1','actual parent-prepared compact DATA');
 need(plan.expected.filter(c=>same(c,v.expected)).length===1&&same(plan.artifacts[v.expected.arm],v.artifact),'one exact compact case/artifact from Root-bound plan');
 const phase=JSON.parse(await regular(v.phaseAuthority)),quiet=JSON.parse(await regular(v.quietWindowAuthority));
 need(phase.schemaVersion===1&&phase.state==='ROOT_APPROVED_BOUNDED_CODEC_MEASUREMENT_PHASE_V1'&&phase.runId===root.runId&&phase.phase===root.phase&&phase.actionAllowed===true&&phase.sourceIndexSha256===ownIx.sha256&&phase.globalBudgetMs===root.globalBudgetMs&&same(phase.preparedPlan,planRow)&&same(phase.warmNPlan,root.warmNPlan)&&same(phase.warmNMatchedPlan,root.warmNMatchedPlan)&&same(phase.quietWindowAuthority,root.quietWindowAuthority),'actual separate phase authority');
 quietWindowModel(quiet,{runId:root.runId,sourceSha:ownIx.sha256,phase:root.phase,nowUtcMs:Date.now(),globalBudgetMs:1});
 if(v.phase==='timing'){
  const matched=JSON.parse(await regular(v.warmNPlan,{maxBytes:128*1024}));need(matched.schemaVersion===1&&matched.state==='ACTUAL_MATCHED_N_PLAN_DATA_V1','original actual warm-N DATA; independent review is separate');
  const row=matched.rows.filter(r=>r.comparison===v.comparison&&r.caseId===v.expected.caseId&&r.arm===v.expected.arm);need(row.length===1&&row[0].n===v.n&&row[0].workerTimeoutMs===v.workerTimeoutMs,'exact independently accepted matched N/budget');
 }else need(v.workerTimeoutMs===600000,'whole pilot candidate hard bound');
 const recheck=async()=>{await regular(inputRow);await regular(rootRow);await regular(ownIx);for(const row of rows)await regular(row,{maxBytes:4*1024*1024});for(const row of dependencies)await regular(row,{maxBytes:4*1024*1024});await regular(planRow,{maxBytes:128*1024});await regular(v.phaseAuthority);await regular(v.quietWindowAuthority);if(v.warmNPlan)await regular(v.warmNPlan,{maxBytes:128*1024});await streamHash(node,{maximumBytes:128*1024*1024});};
 await recheck();const output=await DurableOutput.create(v.outputRoot);let session,handshake;const boundaries=[];
 const resource=(label)=>boundaries.push({label,rssBytes:process.memoryUsage().rss,nodePublicMaxRssKilobytes:process.resourceUsage().maxRSS});
 try{
  await output.write('started.json',{schemaVersion:1,jobId:v.jobId,phase:v.phase,sourceIndex:ownIx,rootAuthority:rootRow,expected:v.expected,artifact:v.artifact,partial:true},{json:true});
  resource('after-source-authentication-before-loader');const started=process.hrtime.bigint();session=await loadTimingSession(v.artifact);const loaded=process.hrtime.bigint();resource('after-reviewed-esm-tla-load');
  handshake=createParentHandshake({input:process.stdin,output:process.stdout});
  const write=async(name,value)=>{const row=await output.write(name,value,{json:true});return row;};
  const row=await injectedWorker({descriptor:v,session,clock:{nowNs:()=>process.hrtime.bigint()},write,recheck,
   onCallStart:e=>handshake.start(e),onCallEnd:e=>handshake.end(e),
   resourceFacts:()=>{resource('after-final-source-audit');return{boundarySamples:boundaries,reviewedEsmTlaLoadNs:(loaded-started).toString(),
    loadScope:'combined artifact hashes/parser/binding/direct ESM top-level initialization/instantiation/post-load hashes; no separate compile/instantiate claim',
    nodePublicMaxRssKilobytes:process.resourceUsage().maxRSS,maxRssUnits:'Node22 resourceUsage API kilobytes',rssUnits:'bytes',wholeNodeProcessOnly:true,
    includesAuthenticationAndLoaderOverhead:true,parentHugeProofAndOracleReportsLoaded:false,guestHeapOrCapacityClaim:false,continuousRssSamplingClaim:false,physicallyColdStartupClaim:false};}});
  await session.recheck();await recheck();await output.recheck();
  const indexRow=await output.write('index.json',{schemaVersion:1,files:[...output.rows.values()]},{json:true}),completion=await output.write('completion.json',{schemaVersion:1,state:'CODEC_PHASE_WORKER_COMPLETE_EXTERNAL_OWNED_ZERO_REQUIRED_V1',jobId:v.jobId,sourceIndexSha256:v.sourceIndexSha256,results:row,index:indexRow,component:v.artifact.component},{json:true});await output.recheck();return{index:indexRow,completion};
 }catch(error){let audit=false;try{if(session)await session.recheck();await recheck();audit=true;}catch{}try{await output.write('failure.json',{schemaVersion:1,state:'CODEC_PHASE_WORKER_FAILED_UNACCEPTED',thrown:typed(error),partialRawRetained:true,postFailureSourceAuditPassed:audit},{json:true});}catch{}throw error;}
 finally{if(handshake)handshake.close();await output.close();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 need(process.argv.length===3,'one exact private descriptor');runWorker(JSON.parse(process.argv[2])).then(value=>process.stdout.write(JSON.stringify({event:'cost-worker-complete',...value})+'\n')).catch(()=>{process.exitCode=1;});
}
