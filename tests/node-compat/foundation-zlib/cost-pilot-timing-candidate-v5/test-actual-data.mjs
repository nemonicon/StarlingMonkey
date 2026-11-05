// Retained DATA + pure functions only. Never runs a preflight/worker/loader/codec.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {ORIGINAL_PILOT_SOURCE_INDEX,ORIGINAL_PILOT_ACTUAL_INDEX,ORIGINAL_MATCHED_PLAN,PILOT_REVIEW_STATE,actualIndexLimit,assertCompleteIndexCount,calibrationResultModel} from './calibration-model.mjs';
import {matchedPlan} from '../cost-pilot-timing-candidate-v1/planner.mjs';
import {same} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';
const digest=b=>createHash('sha256').update(b).digest('hex');
async function json(row){const raw=await readFile(row.path);assert.equal(raw.length,row.bytes);assert.equal(digest(raw),row.sha256);return JSON.parse(raw);}
const refs=JSON.parse(await readFile(new URL('./references.json',import.meta.url),'utf8'));
assert(refs.actualCalibrationReview,'Actual B proof must be sealed before this DATA test');
const data=await json(refs.actualCalibrationReview.result),contract=await json(refs.actualCalibrationReview.contract),correct=await json(refs.fullCorrectness.contract);
assert(calibrationResultModel(data,contract,{components:correct.requiredComponents,cases:refs.cases,calibrationDecisionSha256:refs.calibrationDecision.sha256}));
assert.deepEqual(data.sourceIndex,ORIGINAL_PILOT_SOURCE_INDEX);
const ix=await json(ORIGINAL_PILOT_ACTUAL_INDEX);assert.equal(ix.files.length,33066);assert(assertCompleteIndexCount(ix.files.length,actualIndexLimit(PILOT_REVIEW_STATE,data)));
const actual=await json(refs.actualPilotResults);assert(same(actual.calibrations,data.calibrations));
const match=await json(ORIGINAL_MATCHED_PLAN),computed=matchedPlan(data.calibrations);assert(same(match.rows,computed));assert.equal(computed.length,120);
assert.deepEqual(contract.requiredExactDescriptors.actualIndex,ORIGINAL_PILOT_ACTUAL_INDEX);
console.log(JSON.stringify({schemaVersion:1,state:'V5_REAL_CALIBRATION_DATA_PURE_MODELS_PASSED',originalPilotSource:ORIGINAL_PILOT_SOURCE_INDEX,actualPilotIndexRows:ix.files.length,comparisonCases:data.calibrations.length,recomputedMatchedRows:computed.length,caseCorpusAndCurrentComponentsExact:true,newPlanOrPhaseProduced:false,sourceOnly:true,preflightOrHelperOrWorkerOrLoaderOrGuestOrMeasurementInvoked:false}));
