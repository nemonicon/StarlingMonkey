// Retrospective DATA check of worker-body's pre-output guards.
// No worker call, DurableOutput creation, loader, guest, or action admission.
import {readFile,realpath} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
import {descriptor,regular} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {deepFreeze} from '../cost-jco-correctness-candidate-v2/proofs.mjs';
import {streamHash} from '../cost-tooling-candidate-v3/context.mjs';
import {phaseAuthorityModel} from '../cost-pilot-timing-candidate-v3/parent-guard.template.mjs';
import {same,quietWindowModel} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';
import {MEASUREMENT_ENV} from '../cost-pilot-timing-candidate-v1/lifecycle-policy.mjs';
import {workerDescriptorModel} from '../cost-pilot-timing-candidate-v1/worker.template.mjs';
const sourceDirectory=fileURLToPath(new URL('../cost-pilot-timing-candidate-v3/',import.meta.url));
const original='/private/tmp/starling-node-compat/zlib-cost-pilot-v3';
const launch=JSON.parse(await readFile(original+'/processes/pilot-provider-c0-n1-native-on.launch.json'));
const inputRow=descriptor(JSON.parse(launch.args[1]));
const checks=[];
let stage='descriptor';
function need(v,label){if(!v)throw Error(label);checks.push(label);}
try {
 const v=deepFreeze(JSON.parse(await regular(inputRow,{maxBytes:65536})));
 stage='descriptor-model';workerDescriptorModel(v);checks.push(stage);
 stage='root-model';const root=deepFreeze(JSON.parse(await regular(v.rootAuthority)));phaseAuthorityModel(root,v.sourceIndexSha256);checks.push(stage);
 stage='namespace';need(v.parentOutputRoot===root.outputRoot&&v.outputRoot===root.outputRoot+'/jobs/'+v.jobId&&inputRow.path===root.outputRoot+'/descriptors/'+v.jobId+'.json','namespace');
 need(/^[A-Za-z0-9][A-Za-z0-9_-]{0,159}$/.test(v.jobId)&&v.phase===root.phase,'job/phase');
 stage='authority-relations';need(same(v.phaseAuthority,root.phaseAuthority)&&same(v.quietWindowAuthority,root.quietWindowAuthority)&&same(v.preparedPlan,root.preparedPlan)&&same(v.warmNPlan,root.warmNMatchedPlan),'phase/plan/window relations');
 need(same(v.sourceIndependentReviewIndex,root.sourceIndependentReview.index),'source peer relation');
 stage='execution-environment';need(process.version==='v22.14.0'&&process.execArgv.length===0&&same(Object.fromEntries(Object.entries(process.env).sort()),Object.fromEntries(Object.entries(MEASUREMENT_ENV).sort())),'pinned Node and exact environment');
 stage='source-intake';const ownIx=descriptor(v.sourceIndex),index=JSON.parse(await regular(ownIx));
 need(ownIx.path===join(sourceDirectory,'index.json')&&ownIx.sha256===v.sourceIndexSha256&&Array.isArray(index.files)&&index.files.length<=512,'source identity');
 const rows=index.files.map(r=>descriptor({...r,path:join(sourceDirectory,r.path)}));
 need(rows.every(r=>r.bytes<=4*1024*1024),'compact source members');
 const deps=JSON.parse(await regular(rows.find(r=>r.path===join(sourceDirectory,'worker-dependencies.json'))));
 need(Array.isArray(deps.files)&&deps.files.length>0&&deps.files.length<=256,'dependency shape');
 need(deps.files.every(r=>r.bytes<=4*1024*1024),'compact dependencies');
 stage='node-path';const refs=JSON.parse(await regular(rows.find(r=>r.path===join(sourceDirectory,'references.json')))),node=descriptor(refs.node);
 need(await realpath(process.execPath)===node.path,'actual executable canonical path');await streamHash(node,{maximumBytes:128*1024*1024});checks.push('actual Node hash');
 stage='prepared-plan';const plan=deepFreeze(JSON.parse(await regular(v.preparedPlan,{maxBytes:128*1024})));
 need(plan.sourceIndexSha256===ownIx.sha256&&plan.state==='PREPARED_COMPACT_CODEC_MEASUREMENT_PLAN_DATA_ONLY_V1','plan identity');
 need(plan.expected.filter(c=>same(c,v.expected)).length===1&&same(plan.artifacts[v.expected.arm],v.artifact),'exact case/artifact');
 stage='phase-file';const phase=JSON.parse(await regular(v.phaseAuthority)),quiet=JSON.parse(await regular(v.quietWindowAuthority));
 need(phase.schemaVersion===1&&phase.state==='ROOT_APPROVED_BOUNDED_CODEC_MEASUREMENT_PHASE_V1'&&phase.runId===root.runId&&phase.phase===root.phase&&phase.actionAllowed===true&&phase.sourceIndexSha256===ownIx.sha256&&phase.globalBudgetMs===root.globalBudgetMs&&same(phase.preparedPlan,v.preparedPlan)&&same(phase.warmNPlan,root.warmNPlan)&&same(phase.warmNMatchedPlan,root.warmNMatchedPlan)&&same(phase.quietWindowAuthority,root.quietWindowAuthority),'phase-file relations');
 stage='retrospective-window-model';quietWindowModel(quiet,{runId:root.runId,sourceSha:ownIx.sha256,phase:root.phase,nowUtcMs:Date.parse(launch.startedAtUtc),globalBudgetMs:1});checks.push('window model at original recorded launch time; no new authority');
 stage='pilot-timeout';need(v.workerTimeoutMs===600000,'worker hard bound');
 stage='pre-output-reads';for(const row of rows)await regular(row,{maxBytes:4*1024*1024});for(const row of deps.files)await regular(row,{maxBytes:4*1024*1024});checks.push('all pre-output source/dependency reads');
 console.log(JSON.stringify({schemaVersion:1,checks,passed:true,modelOnly:true,workerCalled:false,guestInvoked:false,outputCreated:false,originalFailureCauseProven:false}));
} catch(error) {
 console.log(JSON.stringify({schemaVersion:1,checks,passed:false,failedStage:stage,error:{name:error.name,message:error.message,stack:error.stack},modelOnly:true,workerCalled:false,guestInvoked:false,outputCreated:false,originalFailureCauseProven:false}));
}
