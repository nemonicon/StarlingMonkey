// Pure malformed DATA only; neither module imports a guest or reads a clock.
import assert from 'node:assert/strict';
import {validateResourceRun as oldValidate} from '../combined-clock-lifecycle-candidate-v1/collectors.mjs';
import {validateResourceRun as newValidate} from '../combined-clock-lifecycle-candidate-v2/collectors.mjs';
function bad(run,completed){
 const state=()=>({initial:{timerCallbacks:0,startedCases:0,completedCases:0},counters:{inspect:0,run,validate:0,timerCallbacks:0,startedCases:run,completedCases:completed},registeredIds:[],ownPendingNativeHandleCountInstrumented:false,hostResourceTableObserved:false,resetCalled:false});
 const before=state(),after=state();after.counters.timerCallbacks=2;after.counters.completedCases++;after.registeredIds=[1,2];
 return {schemaVersion:1,kind:'scheduler-resource-run-v1',caseId:0,current:1,completed:true,result:{id:1,pressureChecksum:3192,events:[{kind:'one-shot',value:'queued-1',strictReceiverNull:true}]},before,after,nativeResourceCountsObserved:false,hostClockValuesUsedAsOracle:false};
}
for(const record of [bad(9,0),bad(1,9)]){oldValidate(JSON.stringify(record),0);assert.throws(()=>newValidate(JSON.stringify(record),0));}
console.log(JSON.stringify({passed:true,oldCollectorAdmittedMalformedCases:2,newCollectorRejectedBoth:true,guestImported:false,guestExecuted:false,clocksRead:false}));
