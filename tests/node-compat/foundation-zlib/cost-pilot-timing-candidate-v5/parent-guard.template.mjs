// Genuine read-only source/native/artifact guards. No action runs on import.
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {lstat,readdir} from 'node:fs/promises';
import {descriptor,regular} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {indexed,deepFreeze,local} from '../cost-jco-correctness-candidate-v2/proofs.mjs';
import {need,integer} from '../cost-pilot-timing-candidate-v1/planner.mjs';
import {same,descriptorsIn,contractModel,quietWindowModel,providerComparisons} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';
import {compactExpectations} from '../cost-pilot-timing-candidate-v1/compact-plan.mjs';
import {verifyContractDescriptor,captureProofDescriptors} from '../cost-pilot-timing-candidate-v2/contract-descriptors.mjs';
import {captureSourceFamilies} from './source-families.mjs';
import {ORIGINAL_PILOT_SOURCE_INDEX,ORIGINAL_MATCHED_PLAN,actualIndexLimit,assertCompleteIndexCount,calibrationRoleModel,calibrationResultModel} from './calibration-model.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
export const CALIBRATION_DECISION='3cf4eb748d9fcf1e985eddfbdfd49544e507e83300056336fc8665fff22c546e';
export const outputRoot=phase=>{need(phase==='timing','V5 has no pilot launch action');return '/private/tmp/starling-node-compat/zlib-cost-timing-v5';};
export function phaseAuthorityModel(v,sha){
 need(typeof sha==='string'&&/^[a-f0-9]{64}$/.test(sha),'exact own source index SHA');
 need(v?.schemaVersion===1&&v.state==='ROOT_REVIEWED_ZLIB_COST_PILOT_TIMING_PHASE_V1'&&v.phase==='timing','separate NEW Root phase authority; no ff208 CLOSED-state carrier');
 need(v.sourceIndexSha256===sha&&v.actionAllowed===true&&v.sourceIndependentReview?.index&&v.sourceIndependentReview?.result,'actual source peer and Root action');
 need(typeof v.runId==='string'&&/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(v.runId)&&v.outputRoot===outputRoot(v.phase),'exact fresh phase namespace/run identity');
 need(v.calibrationDecisionSha256===CALIBRATION_DECISION,'Root selected original paired calibration design');calibrationRoleModel(v);
 integer(v.globalBudgetMs,1,86400000,'global phase budget selected BEFORE launch');
 for(const key of['phaseAuthority','quietWindowAuthority','preparedPlan'])descriptor(v[key]);
 need(v.phase==='timing'?v.warmNPlan?.index&&v.warmNPlan?.result&&v.warmNPlan?.contract:v.warmNPlan===null,'timing requires actual independently reviewed matched-N proof');
 if(v.phase==='timing')descriptor(v.warmNMatchedPlan);else need(v.warmNMatchedPlan===null,'pilot cannot reuse a warm-N plan');
 for(const key of['operationalAdmission','runtimeAcceptanceClaim','metadataProjection','controlSubtraction','sourcePromotionAllowed'])need(v[key]===false,'scope remains closed '+key);
 return true;
}
export async function exactMembership(root,names){const found=[];
 async function walk(path,prefix){for(const entry of await readdir(path,{withFileTypes:true})){const full=join(path,entry.name),s=await lstat(full);need(!s.isSymbolicLink(),'no evidence symlink');if(s.isDirectory())await walk(full,prefix+entry.name+'/');else{need(s.isFile(),'ordinary evidence file');found.push(prefix+entry.name);}}}
 await walk(root,'');need(same(found.sort(),[...names].sort()),'exact finite indexed membership');
}
async function sourceIndex(row){
 const ix=descriptor(row),v=JSON.parse(await regular(ix));need(v.schemaVersion===1&&Array.isArray(v.files)&&v.files.length>0&&v.files.length<=512,'finite own source index');const rows=[],seen=new Set();
 for(const item of v.files){local(item.path);need(!seen.has(item.path),'unique source row');seen.add(item.path);const r=descriptor({path:join(dirname(ix.path),item.path),sha256:item.sha256,bytes:item.bytes});await regular(r,{maxBytes:64*1024*1024});rows.push(r);}
 await exactMembership(dirname(ix.path),[...seen,'index.json']);
 return{rows,recheck:async()=>{await regular(ix);for(const row of rows)await regular(row,{maxBytes:64*1024*1024});await exactMembership(dirname(ix.path),[...seen,'index.json']);}};
}
export async function contractedProof(proof,expectedState){
 const p=await indexed(proof,{state:expectedState}),cr=descriptor(proof.contract);need(p.rows.filter(r=>same(r,cr)).length===1,'stable contract indexed exactly once');
 await exactMembership(dirname(proof.index.path),[...p.rows.map(r=>r.path.slice(dirname(proof.index.path).length+1)),'index.json']);
 const c=deepFreeze(JSON.parse(await regular(cr))),v=p.data,model=contractModel(v,c,p.rows),referenced=[...captureProofDescriptors(v,c)];
 for(const row of referenced)await verifyContractDescriptor(row);
 let actualNames=null;
 if(v.actualIndex){
  const ix=descriptor(v.actualIndex),index=JSON.parse(await regular(ix));need(index.schemaVersion===1&&Array.isArray(index.files),'actual output index schema');assertCompleteIndexCount(index.files.length,actualIndexLimit(expectedState,v));
  const names=new Set();for(const row of index.files){local(row.path);need(!names.has(row.path),'unique actual output member');names.add(row.path);const r=descriptor({path:join(dirname(ix.path),row.path),sha256:row.sha256,bytes:row.bytes});await regular(r,{maxBytes:64*1024*1024});referenced.push(r);}
  actualNames=[...names,'index.json','completion.json'];await exactMembership(dirname(ix.path),actualNames);
 }
 return{proof:p,data:v,contract:c,components:model.components,recheck:async()=>{await p.recheck();await regular(cr);for(const row of referenced)await verifyContractDescriptor(row);if(actualNames)await exactMembership(dirname(v.actualIndex.path),actualNames);}};
}
export async function auditPrerequisites({sourceIndex:ownRow,sourceIndependentReview}={}){
 need(ownRow&&sourceIndependentReview,'NULL own seal/source peer refuses BEFORE genuine guards');
 need(ownRow.path===join(HERE,'index.json'),'only this sealed source implementation');
 const inheritedFamilies=await captureSourceFamilies(ownRow);
 const own=await sourceIndex(ownRow),sourcePeer=await indexed(sourceIndependentReview,{state:'INDEPENDENT_ZLIB_COST_PILOT_TIMING_SOURCE_REVIEW_PASSED_V1'});
 need(sourcePeer.data.sourceIndexSha256===ownRow.sha256&&sourcePeer.data.sourceOnly===true&&sourcePeer.data.ownerActionsInvoked===false,'own independent source review');
 const refsRow=own.rows.find(r=>r.path===join(HERE,'references.json')),refs=deepFreeze(JSON.parse(await regular(refsRow)));
 const correct=await contractedProof(refs.fullCorrectness,'INDEPENDENT_ZLIB_COST_JCO_CORRECTNESS_V3_RESULTS_REVIEW_PASSED_V1');
 const transport=await contractedProof(refs.stockWasmtimeStrings,'INDEPENDENT_ZLIB_COST_STOCK_WASMTIME42_STRING_TRANSPORT_RESULTS_VERIFIED_V1');
 const controls=await contractedProof(refs.actualControlsProof,'INDEPENDENT_ZLIB_COST_JCO_CONTROL_V2_RESULTS_REVIEW_PASSED_V1');
 need(controls.data.controlOperations===540&&controls.data.codecCalls===0&&controls.data.pilotPrerequisitesSatisfied===false,'actual controls separate from phase authority');
 need(correct.data.controlOperations===0&&correct.data.actualBatchControlProofPending===true&&transport.data.actualBatchControlProofPending===true,'original proof control/pending fields never relabeled');
 const decision=JSON.parse(await regular(refs.calibrationDecision));need(refs.calibrationDecision.sha256===CALIBRATION_DECISION&&decision.sourceDesignSelected===true&&decision.executionAuthority===false,'selected source-only calibration DATA');
 // Original authority is passed unchanged into the genuine read-only API.
 const {correctnessPreflight}=await import('../cost-jco-correctness-candidate-v3/admission.mjs');
 const frame=await correctnessPreflight({correctnessSourceIndexSha256:'0124b94f28b20cea7d85c8e7a2619a33099ee98ed56d4920dd5d5749da28cb8c',rootAction:correct.contract.requiredExactDescriptors.rootAuthority});
 for(const arm of['native-on','fflate-on','fflate-off'])need(same(frame.frames[arm].artifact.component,correct.components[arm])&&same(controls.components[arm],correct.components[arm]),'exact genuine artifact '+arm);
 providerComparisons(Object.fromEntries(['native-on','fflate-on','fflate-off'].map(arm=>[arm,frame.frames[arm].proofResult])));
 const cases=JSON.parse(await regular(refs.cases)),inputFacts=JSON.parse(await regular(refs.controlInputFacts)),raw=JSON.parse(await regular(refs.rawFixtures)),catalog=JSON.parse(await regular(refs.reviewedEncoderStreams));
 const expected=compactExpectations({cases,inputFacts,rawFixtures:raw.fixtures,streams:catalog.streams,oracleSha256:correct.data.oracleSha256});
 const artifacts=Object.fromEntries(['native-on','fflate-on','fflate-off'].map(arm=>[arm,frame.frames[arm].artifact]));
 const calibration=await contractedProof(refs.actualCalibrationReview,'INDEPENDENT_ZLIB_COST_PILOT_RESULTS_REVIEW_PASSED_V1');
 calibrationResultModel(calibration.data,calibration.contract,{components:Object.fromEntries(Object.entries(artifacts).map(([arm,a])=>[arm,a.component])),cases:refs.cases,calibrationDecisionSha256:CALIBRATION_DECISION});
 const recheck=async()=>{await calibration.recheck();await inheritedFamilies.recheck();await own.recheck();await sourcePeer.recheck();await correct.recheck();await transport.recheck();await controls.recheck();await frame.recheck();for(const row of[refsRow,refs.calibrationDecision,refs.cases,refs.controlInputFacts,refs.rawFixtures,refs.reviewedEncoderStreams])await regular(row);};await recheck();
 return Object.freeze({frame,own,refs,expected,artifacts,calibration,recheck});
}
export async function readOnlyParentProofAudit({sourceIndex:ownRow,rootAction}={}){
 need(ownRow&&rootAction,'NULL new source/Root action refuses');const rootRow=descriptor(rootAction),root=deepFreeze(JSON.parse(await regular(rootRow)));phaseAuthorityModel(root,ownRow.sha256);
 const admitted=await auditPrerequisites({sourceIndex:ownRow,sourceIndependentReview:root.sourceIndependentReview});
 need(same(root.warmNPlan,admitted.refs.actualCalibrationReview),'Root binds the exact original independently reviewed b5 calibration');
 const planRow=descriptor(root.preparedPlan),plan=deepFreeze(JSON.parse(await regular(planRow,{maxBytes:128*1024})));
 need(plan.schemaVersion===1&&plan.state==='PREPARED_COMPACT_CODEC_MEASUREMENT_PLAN_DATA_ONLY_V1'&&plan.sourceIndexSha256===ownRow.sha256&&plan.calibrationDecisionSha256===CALIBRATION_DECISION&&plan.operationalAdmission===false,'actual prepared compact plan, no authority projection');
 need(same(plan.expected,admitted.expected)&&same(plan.artifacts,admitted.artifacts),'entire compact plan matches parent full proof admission');
 need(same(plan.calibrationSourceIndex,ORIGINAL_PILOT_SOURCE_INDEX)&&same(plan.calibrationReview,admitted.refs.actualCalibrationReview)&&same(plan.calibrationMatchedPlan,ORIGINAL_MATCHED_PLAN),'New genuine plan keeps original calibration DATA roles');
 const phaseRow=descriptor(root.phaseAuthority),phase=deepFreeze(JSON.parse(await regular(phaseRow))),quietRow=descriptor(root.quietWindowAuthority),quiet=deepFreeze(JSON.parse(await regular(quietRow)));
 need(phase.schemaVersion===1&&phase.state==='ROOT_APPROVED_BOUNDED_CODEC_MEASUREMENT_PHASE_V1'&&phase.actionAllowed===true&&phase.runId===root.runId&&phase.phase===root.phase&&phase.sourceIndexSha256===ownRow.sha256&&phase.globalBudgetMs===root.globalBudgetMs&&same(phase.calibrationSourceIndex,root.calibrationSourceIndex)&&same(phase.preparedPlan,planRow)&&same(phase.quietWindowAuthority,quietRow)&&same(phase.warmNPlan,root.warmNPlan)&&same(phase.warmNMatchedPlan,root.warmNMatchedPlan),'separate exact Root phase file');
 const checkWindow=(remainingMs=root.globalBudgetMs)=>quietWindowModel(quiet,{runId:root.runId,sourceSha:ownRow.sha256,phase:root.phase,nowUtcMs:Date.now(),globalBudgetMs:Math.max(1,remainingMs)});
 checkWindow();
 const recheck=async()=>{await regular(rootRow);await regular(planRow,{maxBytes:128*1024});await regular(phaseRow);await regular(quietRow);await admitted.recheck();};await recheck();
 return Object.freeze({...admitted,root,rootAction:rootRow,planRow,phaseRow,quietRow,checkWindow,recheck});
}
