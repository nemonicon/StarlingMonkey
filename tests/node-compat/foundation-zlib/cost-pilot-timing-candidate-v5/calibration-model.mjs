// Pure original-calibration/new-timing source roles and finite file-count bounds.
import {need,PLAN_MATH} from '../cost-pilot-timing-candidate-v1/planner.mjs';
import {same} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';
export const ORIGINAL_PILOT_SOURCE_INDEX=Object.freeze({path:'/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-zlib/cost-pilot-timing-candidate-v4/index.json',sha256:'b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1',bytes:9952});
export const ORIGINAL_PILOT_ACTUAL_INDEX=Object.freeze({path:'/private/tmp/starling-node-compat/zlib-cost-pilot-v4/index.json',sha256:'7dfac0e7f60797f65869e81ead4ce197dbb812a819cc814fb9109936e47c23d1',bytes:6494111});
export const ORIGINAL_PILOT_ACTUAL_RESULTS=Object.freeze({path:'/private/tmp/starling-node-compat/zlib-cost-pilot-v4/results.json',sha256:'2d96dd6b266bfb7668f4a04b535fda68978d5a9b7400866f8269a32a76f952c4',bytes:4650114});
export const ORIGINAL_MATCHED_PLAN=Object.freeze({path:'/private/tmp/starling-node-compat/zlib-cost-pilot-v4/matched-n-plan.json',sha256:'e545f0064485d87cd1bcb919221997578b427df8499e5f8271e2e4e445ccdf3b',bytes:21921});
export const PILOT_REVIEW_STATE='INDEPENDENT_ZLIB_COST_PILOT_RESULTS_REVIEW_PASSED_V1';
export const INDEX_BOUNDS=Object.freeze({legacyProof:16384,maxPilotWorkers:1536,pilotFilesPerWorker:37,pilotOtherFiles:62,pilot:56894,timingWorkers:360,timingFilesPerWorker:49,timingOtherFiles:2,timing:17642});
need(PLAN_MATH.maxPilotWorkers===INDEX_BOUNDS.maxPilotWorkers&&PLAN_MATH.timingWorkers===INDEX_BOUNDS.timingWorkers,'Unchanged genuine schedule determines bounds');
need(INDEX_BOUNDS.pilot===PLAN_MATH.maxPilotWorkers*37+62&&INDEX_BOUNDS.timing===PLAN_MATH.timingWorkers*49+2,'Explicit complete-index arithmetic');
export function actualIndexLimit(expectedState,data){
 if(expectedState!==PILOT_REVIEW_STATE)return INDEX_BOUNDS.legacyProof;
 need(data?.state===PILOT_REVIEW_STATE&&data.sourceIndexSha256===ORIGINAL_PILOT_SOURCE_INDEX.sha256&&same(data.sourceIndex,ORIGINAL_PILOT_SOURCE_INDEX),'Only the actual original calibration gets the pilot bound');
 return INDEX_BOUNDS.pilot;
}
export function assertCompleteIndexCount(count,limit){need(Number.isSafeInteger(count)&&count>0&&count<=limit,'Complete finite actual output index; no truncation/subset');return true;}
export function calibrationRoleModel(root){need(same(root.calibrationSourceIndex,ORIGINAL_PILOT_SOURCE_INDEX)&&same(root.warmNMatchedPlan,ORIGINAL_MATCHED_PLAN),'Root binds original calibration source and actual matched plan, never own timing source');return true;}
export function calibrationResultModel(data,contract,{components,cases,calibrationDecisionSha256}){
 need(data?.schemaVersion===1&&data.state===PILOT_REVIEW_STATE&&data.verifiedPassed===true&&data.sourceIndexSha256===ORIGINAL_PILOT_SOURCE_INDEX.sha256&&same(data.sourceIndex,ORIGINAL_PILOT_SOURCE_INDEX),'Genuine original b5 pilot review identity');
 need(data.calibrationDecisionSha256===calibrationDecisionSha256&&data.allMatchedNReviewed===true&&data.allOwnedWorkersRawZeroClean===true&&data.pilotOnly===true&&data.timingAllowed===false,'Actual complete original calibration, not timing authority');
 need(same(data.actualIndex,ORIGINAL_PILOT_ACTUAL_INDEX)&&same(data.actualResults,ORIGINAL_PILOT_ACTUAL_RESULTS)&&same(data.matchedPlan,ORIGINAL_MATCHED_PLAN),'Exact actual b5 output descriptors');
 need(same(data.components,components)&&same(contract.requiredComponents,components),'Actual calibrated component tuples equal current genuine admission');
 need(same(data.cases,cases)&&same(contract.requiredExactDescriptors.cases,cases)&&same(contract.requiredExactDescriptors.matchedPlan,ORIGINAL_MATCHED_PLAN),'Original case corpus and matched-plan bytes explicitly bound');
 need(Array.isArray(data.calibrations)&&data.calibrations.length===60,'Whole60 comparison-case calibration records');return true;
}
