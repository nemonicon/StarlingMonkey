// Independent extracted PURE functions and retained JSON DATA only.
// No owner module, operational API, helper, loader, provider or guest is imported.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const D=fileURLToPath(new URL('.',import.meta.url));
const S=fileURLToPath(new URL('../cost-pilot-timing-candidate-v5/',import.meta.url));
const json=async path=>JSON.parse(await readFile(path,'utf8'));
const refs=await json(S+'references.json');
const readVerified=async row=>{const b=await readFile(row.path);assert.equal(b.length,row.bytes);assert.equal(createHash('sha256').update(b).digest('hex'),row.sha256);return b.toString('utf8');};
const inputs=await json(D+'input-hashes.json');
const rowFor=p=>{const r=inputs.files.find(r=>r.path===p);assert(r,'source must first be independently hashed');return r;};
const planner=await readVerified(rowFor(fileURLToPath(new URL('../cost-pilot-timing-candidate-v1/planner.mjs',import.meta.url))));
const proof=await readVerified(rowFor(fileURLToPath(new URL('../cost-pilot-timing-candidate-v1/proof-model.mjs',import.meta.url))));
const calibration=await readVerified(rowFor(S+'calibration-model.mjs'));
const pureText=[planner,proof,calibration].map(s=>s.replace(/^import .*;\n/gm,'').replace(/\bexport\s+/g,'')).join('\n');
const model=new Function(pureText+'\nreturn {PLAN_MATH,POLICY,INDEX_BOUNDS,PILOT_REVIEW_STATE,ORIGINAL_PILOT_SOURCE_INDEX,ORIGINAL_MATCHED_PLAN,actualIndexLimit,assertCompleteIndexCount,calibrationRoleModel,calibrationResultModel,timingSchedule,matchedPlan,callCap:caseCap};')();
const data=JSON.parse(await readVerified(refs.actualCalibrationReview.result));
const contract=JSON.parse(await readVerified(refs.actualCalibrationReview.contract));
const correct=JSON.parse(await readVerified(refs.fullCorrectness.contract));
const actualMatched=JSON.parse(await readVerified(refs.actualMatchedPlan));
const actualIndex=JSON.parse(await readVerified(refs.actualPilotIndex));
const observations=[];
function pass(label,fn){assert.equal(fn(),true,label);observations.push({label,passed:true});}
function refuse(label,fn){assert.throws(fn,undefined,label);observations.push({label,refused:true});}
const clone=v=>structuredClone(v);
const options={components:correct.requiredComponents,cases:refs.cases,calibrationDecisionSha256:refs.calibrationDecision.sha256};
pass('entire real actual B5 review matches real current component/case/decision contract',()=>model.calibrationResultModel(data,contract,options));
pass('real 33066-row pilot index is accepted whole',()=>model.assertCompleteIndexCount(actualIndex.files.length,model.actualIndexLimit(model.PILOT_REVIEW_STATE,data)));
pass('explicit new timing SHA coexists with preserved original calibration descriptor',()=>model.calibrationRoleModel({sourceIndexSha256:'e799350100bb3b54148fdc5bd46a857579a6aae7608890f620569ea3704ab321',calibrationSourceIndex:data.sourceIndex,warmNMatchedPlan:data.matchedPlan}));
for(const [label,edit] of [
 ['source SHA relabel',v=>v.sourceIndexSha256='e799350100bb3b54148fdc5bd46a857579a6aae7608890f620569ea3704ab321'],
 ['source descriptor path drift',v=>v.sourceIndex.path+='.drift'],
 ['source descriptor digest drift',v=>v.sourceIndex.sha256='0'.repeat(64)],
 ['source descriptor byte drift',v=>v.sourceIndex.bytes++],
 ['actual index drift',v=>v.actualIndex.sha256='0'.repeat(64)],
 ['actual results drift',v=>v.actualResults.bytes++],
 ['matched plan drift',v=>v.matchedPlan.path+='.drift'],
 ['case corpus drift',v=>v.cases.sha256='0'.repeat(64)],
 ['component tuple drift',v=>v.components['native-on'].sha256='0'.repeat(64)],
 ['decision drift',v=>v.calibrationDecisionSha256='0'.repeat(64)],
 ['missing curve',v=>v.calibrations.pop()],
 ['extra curve',v=>v.calibrations.push(v.calibrations[0])],
 ['incomplete matched review',v=>v.allMatchedNReviewed=false],
 ['unclean worker claim',v=>v.allOwnedWorkersRawZeroClean=false],
 ['timing authority transfer',v=>v.timingAllowed=true],
 ['not pilot-only',v=>v.pilotOnly=false],
]){const changed=clone(data);edit(changed);refuse(label,()=>model.calibrationResultModel(changed,contract,options));}
for(const key of ['cases','matchedPlan']){const changed=clone(contract);changed.requiredExactDescriptors[key].bytes++;refuse('contract '+key+' drift',()=>model.calibrationResultModel(data,changed,options));}
const alteredComponents=clone(contract);alteredComponents.requiredComponents['fflate-off'].bytes++;
refuse('contract component drift',()=>model.calibrationResultModel(data,alteredComponents,options));
const limit=model.actualIndexLimit(model.PILOT_REVIEW_STATE,data);
assert.equal(limit,56894);assert.equal(model.INDEX_BOUNDS.timing,17642);assert.equal(model.actualIndexLimit('ANOTHER_PROOF',data),16384);
for(const n of [1,33066,56894])pass('complete pilot bound '+n,()=>model.assertCompleteIndexCount(n,limit));
for(const n of [0,-0,-1,1.5,NaN,Infinity,'33066',56895,Number.MAX_SAFE_INTEGER])refuse('invalid/over-bound pilot count '+String(n),()=>model.assertCompleteIndexCount(n,limit));
pass('complete original timing bound',()=>model.assertCompleteIndexCount(17642,model.INDEX_BOUNDS.timing));
refuse('timing bound overflow',()=>model.assertCompleteIndexCount(17643,model.INDEX_BOUNDS.timing));
refuse('unrelated proof retains legacy cap',()=>model.assertCompleteIndexCount(16385,model.actualIndexLimit('ANOTHER_PROOF',data)));
for(const edit of [v=>v.sourceIndexSha256='0'.repeat(64),v=>v.sourceIndex.bytes++,v=>v.state='OTHER']){const changed=clone(data);edit(changed);refuse('oversize role not inherited by malformed calibration',()=>model.actualIndexLimit(model.PILOT_REVIEW_STATE,changed));}
for(const edit of [v=>v.calibrationSourceIndex.bytes++,v=>v.warmNMatchedPlan.sha256='0'.repeat(64)]){const r={calibrationSourceIndex:clone(data.sourceIndex),warmNMatchedPlan:clone(data.matchedPlan)};edit(r);refuse('Root original-role drift',()=>model.calibrationRoleModel(r));}
const computed=model.matchedPlan(data.calibrations);assert.deepEqual(computed,actualMatched.rows);assert.equal(computed.length,120);
const schedule=model.timingSchedule();assert.equal(schedule.length,360);
for(let id=0;id<30;id++)for(const comparison of ['same-engine-provider','unused-profile']){
 const selected=schedule.filter(r=>r.caseId===id&&r.comparison===comparison);assert.equal(selected.length,6);
 assert.deepEqual(selected.map(r=>r.side),['A','B','B','A','A','B']);
 for(const spec of selected){const m=computed.filter(r=>r.caseId===id&&r.comparison===comparison&&r.arm===spec.arm);assert.equal(m.length,1);assert(m[0].n<=model.callCap(id));assert.equal(spec.samples,7);assert.equal(spec.warmups,3);assert.equal(spec.controlN,1);}
}
assert.equal(schedule.length*10,3600);assert.equal(schedule.length*6,2160);
assert.equal(model.PLAN_MATH.maxPilotWorkers,1536);assert.equal(1536*37+62,56894);assert.equal(360*49+2,17642);
observations.push({label:'real 60 calibration records reproduce all 120 actual matched rows',passed:true});
observations.push({label:'all 360 original AB/BA/AB workers cover cases, matched N and unchanged 3600/2160 schedule',passed:true});
const result={schemaVersion:1,state:'INDEPENDENT_V5_EXTRACTED_PURE_AND_REAL_DATA_MODELS_PASSED',checks:observations.length,actualCalibrationRecords:data.calibrations.length,actualMatchedRows:computed.length,actualPilotIndexRows:actualIndex.files.length,originalPilotSourceIndex:data.sourceIndex,newTimingSourceIndexSha256:'e799350100bb3b54148fdc5bd46a857579a6aae7608890f620569ea3704ab321',timingWorkers:360,codecBatchCalls:3600,rawN1Controls:2160,observations,ownerModulesImported:false,ownerActionsInvoked:false,providerOrGuestInvoked:false};
await writeFile(D+'pure-audit.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
