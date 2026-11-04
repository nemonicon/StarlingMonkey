// Separate control action. No prior action state is forged or projected.
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {lstat} from 'node:fs/promises';
import {descriptor,regular,sha} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {indexed,deepFreeze,local} from '../cost-jco-correctness-candidate-v2/proofs.mjs';
import {need} from '../cost-jco-correctness-candidate-v2/transport.mjs';
export const NODE=Object.freeze({path:'/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256:'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes:108619024});
export const ARMS=Object.freeze(['native-on','fflate-on','fflate-off']);
export const COMPONENT='cf3110b3af503fecd2408781a4dcb53b21670b74cd94e3266c4f0b86f795d794',GUEST='ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8',TOOLING='ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8';
const HERE=dirname(fileURLToPath(import.meta.url));
export const OUTPUT='/private/tmp/starling-node-compat/zlib-cost-jco-control-correctness-v2';
export const PRIOR_SOURCE='0124b94f28b20cea7d85c8e7a2619a33099ee98ed56d4920dd5d5749da28cb8c';
export const PRIOR_REVIEW='e03bb0db65f6009e86a6d55e4553e820d143c702128976efc5ef47e092548083',CONTRACT='25411f2ecb278c1eeda7b27a0aafa47b29cc3d9a53221a327e9e5c94002936f1';
const same=(a,b)=>a.path===b.path&&a.sha256===b.sha256&&a.bytes===b.bytes;
export function authorityModel(v,sourceSha){
 sha(sourceSha);need(v?.schemaVersion===1&&v.state==='ROOT_REVIEWED_ZLIB_COST_JCO_CONTROL_CORRECTNESS_V2'&&v.action==='untimed-jco-controls'&&v.actionAllowed===true,'New explicit control-only Root authority; NULL refuses');
 need(v.controlSourceIndexSha256===sourceSha&&v.outputRoot===OUTPUT&&v.priorCorrectnessSourceIndexSha256===PRIOR_SOURCE&&v.priorCorrectnessReviewIndexSha256===PRIOR_REVIEW&&v.priorCorrectnessContractSha256===CONTRACT,'Exact own/prior control scope');
 need(v.armSessions===3&&v.primaryCasesPerArm===30&&v.controlRepetitions===2&&JSON.stringify(v.controlRangeBases)==='[30,60,90]'&&v.operationsPerCall===1&&v.expectedControlOperationsPerArm===180&&v.workerTimeoutMs===600000,'Exact finite N1 control schedule');
 need(v.ordinaryGuestControlCallsAllowed===true&&v.codecCallsAllowed===false&&v.nodeCodecCallsAllowed===false&&v.observeStageValidateAllowed===false&&v.wasmtimeAllowed===false&&v.pilotOrTimingAllowed===false&&v.operationalAdmission===false&&v.runtimeAcceptanceClaim===false&&v.metadataProjection===false,'No codec/WT/pilot/timing/admission extension');
 need(v.sourceIndependentReview?.index&&v.sourceIndependentReview?.result,'Own independent SOURCE review required');descriptor(v.sourceIndependentReview.index);descriptor(v.sourceIndependentReview.result);return true;
}
async function sourceIndex(root,expected){
 const path=join(root,'index.json'),size=(await lstat(path)).size,ix=descriptor({path,sha256:expected,bytes:size}),index=JSON.parse(await regular(ix)),rows=[],seen=new Set();
 need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length>0&&index.files.length<=1024,'Finite source index');
 for(const r of index.files){local(r.path);need(!seen.has(r.path),'Unique source row');seen.add(r.path);const row=descriptor({path:join(root,r.path),sha256:r.sha256,bytes:r.bytes});await regular(row,{maxBytes:64*1024*1024});rows.push(row);}
 return Object.freeze({rows:Object.freeze(rows),recheck:async()=>{await regular(ix);for(const row of rows)await regular(row,{maxBytes:64*1024*1024});}});
}
async function completedProof(prerequisites){
 need(prerequisites.review.index.sha256===PRIOR_REVIEW&&prerequisites.review.contract.sha256===CONTRACT,'Hard-pinned completed correctness review/contract');
 const proof=await indexed(prerequisites.review,{state:'INDEPENDENT_ZLIB_COST_JCO_CORRECTNESS_V3_RESULTS_REVIEW_PASSED_V1'});
 const contractRow=descriptor(prerequisites.review.contract),contract=deepFreeze(JSON.parse(await regular(contractRow))),r=proof.data;
 for(const[k,v]of Object.entries(contract.requiredFixedValues))need(JSON.stringify(r[k])===JSON.stringify(v),'Actual prior fixed result '+k);
 for(const[k,v]of Object.entries(contract.requiredCoverage))need(r.coverage[k]===v,'Actual prior full coverage '+k);
 const rows=Object.values(contract.requiredExactDescriptors).map(descriptor);for(const[k,v]of Object.entries(contract.requiredExactDescriptors))need(same(descriptor(r[k]),v),'Actual prior exact descriptor '+k);
 for(const row of rows)await regular(row,{maxBytes:128*1024*1024});
 const actualIndex=JSON.parse(await regular(contract.requiredExactDescriptors.actualIndex)),outputRows=[],names=new Set(),root=dirname(contract.requiredExactDescriptors.actualIndex.path);
 need(actualIndex.schemaVersion===1&&Array.isArray(actualIndex.files)&&actualIndex.files.length>0&&actualIndex.files.length<=30000,'Finite actual completed output closure');
 for(const item of actualIndex.files){local(item.path);need(!names.has(item.path),'Unique prior output member');names.add(item.path);const row=descriptor({path:join(root,item.path),sha256:item.sha256,bytes:item.bytes});await regular(row,{maxBytes:128*1024*1024});outputRows.push(row);}
 const done=JSON.parse(await regular(contract.requiredExactDescriptors.actualCompletion)),terminal=JSON.parse(await regular(contract.requiredExactDescriptors.externalParentTerminal));
 need(done.state==='UNTIMED_JCO_CORRECTNESS_COMPLETE_EXTERNAL_PARENT_ZERO_AND_REVIEW_REQUIRED_V3'&&done.sourceIndexSha256===PRIOR_SOURCE&&done.index.sha256===contract.requiredExactDescriptors.actualIndex.sha256&&done.results.sha256===contract.requiredExactDescriptors.actualResult.sha256&&terminal.rawExitCode===0,'Actual completed original parent0, never old controls');
 const oldAuthority=descriptor(contract.requiredExactDescriptors.rootAuthority),recheck=async()=>{await proof.recheck();await regular(contractRow);for(const row of rows)await regular(row,{maxBytes:128*1024*1024});for(const row of outputRows)await regular(row,{maxBytes:128*1024*1024});};
 return Object.freeze({proof,contract,oldAuthority,outputRows:outputRows.length,recheck});
}
export async function controlPreflight({controlSourceIndexSha256,rootAction}={}){
 need(controlSourceIndexSha256&&rootAction,'NULL control authority refuses before outputs/loaders');const sourceSha=sha(controlSourceIndexSha256),rootRow=descriptor(rootAction),authority=deepFreeze(JSON.parse(await regular(rootRow)));authorityModel(authority,sourceSha);
 need(process.version==='v22.14.0'&&process.execArgv.length===0&&!process.env.NODE_OPTIONS&&!process.env.NODE_PATH,'Pinned plain Node22 environment');for(const key of Object.keys(process.env))need(!key.startsWith('NAPI_RS_'),'No native-binding override');
 const own=await sourceIndex(HERE,sourceSha),priorSource=await sourceIndex(join(HERE,'..','cost-jco-correctness-candidate-v3'),PRIOR_SOURCE),donorSource=await sourceIndex(join(HERE,'..','cost-jco-correctness-candidate-v2'),'d2516c934df3fa8f3ecd58b187cc2bc0f28fab996ab97ada0854e4988d9befeb');
 const original=await sourceIndex(join(HERE,'../cost-jco-control-correctness-candidate-v1'),'ad0d651fdb8653a8a708514131bad52cf8cc05b657c6cefd92604aca3c3f7a23');
 const lineageRow=own.rows.find(r=>r.path===join(HERE,'lineage.json'));need(lineageRow,'Exact failure lineage');const lineage=deepFreeze(JSON.parse(await regular(lineageRow))),failure=await indexed(lineage.failureReview,{state:'INDEPENDENT_ZLIB_COST_JCO_CONTROL_V1_PRE_WORKER_FAILURE_VERIFIED'});need(failure.data.finding==='COST-CONTROL-PARENT-DIRECTORY-M1','Actual prior pre-worker failure, never old control pass');await regular(lineage.rootFailure);await regular(lineage.requiredCorrection);
 const peer=await indexed(authority.sourceIndependentReview,{state:'INDEPENDENT_ZLIB_COST_JCO_CONTROL_SOURCE_REVIEW_PASSED_V2'});need(peer.data.controlSourceIndexSha256===sourceSha&&peer.data.sourceOnly===true&&peer.data.sourceReviewPassed===true&&peer.data.ownerActionsInvoked===false,'Own exact source review, not action approval');
 const pRow=own.rows.find(r=>r.path===join(HERE,'prerequisites.json'));need(pRow,'Indexed exact prerequisite descriptors');const prerequisites=deepFreeze(JSON.parse(await regular(pRow))),completed=await completedProof(prerequisites);
 // Invoke only the real prior READ-ONLY guard with its genuine unchanged Root
 // authority. The new control action itself is authorized solely above.
 const {correctnessPreflight}=await import('../cost-jco-correctness-candidate-v3/admission.mjs');
 const frame=await correctnessPreflight({correctnessSourceIndexSha256:PRIOR_SOURCE,rootAction:completed.oldAuthority});
 for(const arm of['native-on','fflate-on','fflate-off'])need(same(frame.frames[arm].artifact.component,completed.contract.requiredComponents[arm]),'Same actual reviewed component '+arm);
 need(same(frame.oracle,completed.contract.requiredExactDescriptors.oracle),'Same actual reviewed oracle');
 const recheck=async()=>{await regular(rootRow);await own.recheck();await original.recheck();await failure.recheck();await regular(lineage.rootFailure);await regular(lineage.requiredCorrection);await priorSource.recheck();await donorSource.recheck();await peer.recheck();await completed.recheck();await frame.recheck();};await recheck();
 return Object.freeze({sourceSha,rootAction:rootRow,outputRoot:OUTPUT,frames:frame.frames,oracle:frame.oracle,priorCorrectnessRootAuthority:completed.oldAuthority,priorCompletedOutputRows:completed.outputRows,criticalFiles:Object.freeze([...own.rows,...original.rows,...frame.criticalSourceFiles,rootRow]),recheck});
}
