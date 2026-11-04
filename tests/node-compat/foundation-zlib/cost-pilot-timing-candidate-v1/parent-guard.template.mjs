// SOURCE TEMPLATE: genuine existing read-only guards; no CLI/action on import.
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {descriptor,regular} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {indexed,deepFreeze,local} from '../cost-jco-correctness-candidate-v2/proofs.mjs';
import {need} from './planner.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
const EQ=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export function phaseAuthorityModel(v,sha){
 need(typeof sha==='string'&&/^[a-f0-9]{64}$/.test(sha),'exact own source index SHA');
 need(v?.schemaVersion===1&&v.state==='ROOT_REVIEWED_ZLIB_COST_PILOT_TIMING_PHASE_V1'&&['pilot-candidate','timing'].includes(v.phase),'separate NEW Root phase authority; no ff208 CLOSED-state carrier');
 need(v.sourceIndexSha256===sha&&v.actionAllowed===true&&v.sourceIndependentReview?.index&&v.sourceIndependentReview?.result,'actual source peer and Root action');
 need(v.actualControlsProof?.index&&v.actualControlsProof?.result&&v.actualControlsProof?.contract,'independent actual controls contract required; Root9b alone is not acceptance');
 need(v.quietWindowAuthority&&v.phaseAuthority,'separate reviewed quiet-window and phase files required');
 need(v.phase==='timing'?v.warmNPlan!==null:v.warmNPlan===null,'timing requires reviewed actual matched-N plan');
 for(const key of['operationalAdmission','runtimeAcceptanceClaim','metadataProjection','controlSubtraction','sourcePromotionAllowed'])need(v[key]===false,'scope remains closed '+key);
 return true;
}
async function sourceIndex(row){
 const ix=descriptor(row),v=JSON.parse(await regular(ix));need(v.schemaVersion===1&&Array.isArray(v.files)&&v.files.length>0&&v.files.length<=256,'finite own source index');const rows=[],seen=new Set();
 for(const item of v.files){local(item.path);need(!seen.has(item.path),'unique source row');seen.add(item.path);const r=descriptor({path:join(dirname(ix.path),item.path),sha256:item.sha256,bytes:item.bytes});await regular(r,{maxBytes:64*1024*1024});rows.push(r);}
 return{rows,recheck:async()=>{await regular(ix);for(const row of rows)await regular(row,{maxBytes:64*1024*1024});}};
}
async function contractedProof(proof,expectedState){
 const p=await indexed(proof,{state:expectedState}),cr=descriptor(proof.contract);need(p.rows.filter(r=>EQ(r,cr)).length===1,'stable contract indexed exactly once');
 const c=deepFreeze(JSON.parse(await regular(cr))),v=p.data;need(c.requiredReviewState===expectedState&&v.verifiedPassed===true,'actual independently reviewed result');
 for(const[key,wanted]of Object.entries(c.requiredFixedValues??{}))need(EQ(v[key],wanted),'immutable original proof fixed field '+key);
 for(const[key,wanted]of Object.entries(c.requiredCoverage??{}))need(EQ(v.coverage?.[key],wanted),'finite original coverage '+key);
 for(const[key,wanted]of Object.entries(c.requiredExactDescriptors??{}))need(EQ(v[key],wanted),'actual proof descriptor '+key);
 if(c.requiredComponents)need(EQ(v.components,c.requiredComponents),'same three actual component bytes');
 if(c.requiredActualComponentReviews)need(EQ(v.actualComponentReviews,c.requiredActualComponentReviews),'same original artifact reviews');
 const referenced=[],seen=new Set();
 async function walk(value){if(!value||typeof value!=='object')return;
  if(typeof value.path==='string'&&typeof value.sha256==='string'&&Number.isSafeInteger(value.bytes)){
   const row=descriptor(value),key=JSON.stringify(row);if(!seen.has(key)){seen.add(key);await regular(row,{maxBytes:64*1024*1024});referenced.push(row);}
  }
  for(const child of Object.values(value))await walk(child);
 }
 await walk(v);await walk(c.requiredExactDescriptors);
 // Full correctness and actual controls indices are rehashed in the PARENT,
 // outside timing/startup/RSS regions. No giant proof report goes to a worker.
 for(const key of['actualIndex'])if(v[key]){
  const ix=descriptor(v[key]),index=JSON.parse(await regular(ix));need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length>0&&index.files.length<=16384,'bounded actual output index');
  const names=new Set();for(const row of index.files){local(row.path);need(!names.has(row.path),'unique actual output member');names.add(row.path);const r=descriptor({path:join(dirname(ix.path),row.path),sha256:row.sha256,bytes:row.bytes});await regular(r,{maxBytes:64*1024*1024});referenced.push(r);}
 }
 return{proof:p,data:v,contract:c,recheck:async()=>{await p.recheck();await regular(cr);for(const row of referenced)await regular(row,{maxBytes:64*1024*1024});}};
}
export async function readOnlyParentProofAudit({sourceIndex:ownRow,rootAction}={}){
 // NULL rejects before any helper/preflight/output/loader access.
 need(ownRow&&rootAction,'NULL new source/Root action refuses');const rootRow=descriptor(rootAction),root=deepFreeze(JSON.parse(await regular(rootRow)));phaseAuthorityModel(root,ownRow.sha256);
 const own=await sourceIndex(ownRow),status=JSON.parse(await regular(own.rows.find(r=>r.path===join(HERE,'implementation-status.json'))));
 // This source proposal intentionally cannot authorize an actual launch. A new
 // immutable reviewed implementation must close every listed lifecycle gate.
 need(status.actualLifecycleReady===true&&status.realMonotonicClockAndDurableAdapterReviewed===true&&status.realOwnedTimeoutAndEnvironmentReviewed===true,'injected proposal has no admitted actual lifecycle');
 const sourcePeer=await indexed(root.sourceIndependentReview,{state:'INDEPENDENT_ZLIB_COST_PILOT_TIMING_SOURCE_REVIEW_PASSED_V1'});need(sourcePeer.data.sourceIndexSha256===ownRow.sha256&&sourcePeer.data.sourceOnly===true&&sourcePeer.data.ownerActionsInvoked===false,'own source-only review');
 const refs=deepFreeze(JSON.parse(await regular(own.rows.find(r=>r.path===join(HERE,'references.json')))));
 const correct=await contractedProof(refs.fullCorrectness,'INDEPENDENT_ZLIB_COST_JCO_CORRECTNESS_V3_RESULTS_REVIEW_PASSED_V1');
 const transport=await contractedProof(refs.stockWasmtimeStrings,'INDEPENDENT_ZLIB_COST_STOCK_WASMTIME42_STRING_TRANSPORT_RESULTS_VERIFIED_V1');
 const controls=await contractedProof(root.actualControlsProof,'INDEPENDENT_ZLIB_COST_JCO_CONTROL_V2_RESULTS_REVIEW_PASSED_V1');
 need(controls.data.controlOperations===540&&controls.data.codecCalls===0,'actual independent controls separate from original correctness control0');
 need(correct.data.controlOperations===0&&correct.data.actualBatchControlProofPending===true,'historical correctness flags never relabeled');
 need(transport.data.actualBatchControlProofPending===true&&transport.data.timingAllowed===false,'historical transport scope never relabeled');
 // Genuine read-only admission receives its original accepted authority file,
 // unchanged. The new Root phase state is NEVER passed into the old API.
 const {correctnessPreflight}=await import('../cost-jco-correctness-candidate-v3/admission.mjs');
 const original=correct.contract.requiredExactDescriptors.rootAuthority;
 const frame=await correctnessPreflight({correctnessSourceIndexSha256:'0124b94f28b20cea7d85c8e7a2619a33099ee98ed56d4920dd5d5749da28cb8c',rootAction:original});
 for(const arm of['native-on','fflate-on','fflate-off'])need(EQ(frame.frames[arm].artifact.component,correct.data.components[arm])&&EQ(controls.data.components[arm],correct.data.components[arm]),'exact admitted artifact '+arm);
 const recheck=async()=>{await regular(rootRow);await own.recheck();await sourcePeer.recheck();await correct.recheck();await transport.recheck();await controls.recheck();await frame.recheck();};await recheck();
 return Object.freeze({frame,rootAction:rootRow,phase:root.phase,fullProofsParentOnly:true,recheck});
}
