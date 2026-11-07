import assert from 'node:assert/strict';
import {AsyncResource} from 'node:async_hooks';
import {createNodeReference} from '../context-interleaving-candidate-v1/node-reference.mjs';
import {createUnrefReuseState,unrefPublicProjection} from './cases.mjs';
assert.equal(process.version,'v22.14.0');
assert.equal(process.env.NODE_OPTIONS,undefined);
assert(!process.execArgv.includes('--experimental-async-context-frame'));
const hostCase='node-unref-first-'+process.pid;
const state=createUnrefReuseState(createNodeReference(AsyncResource));
let finalCleanup,completed=0;
console.log(JSON.stringify({kind:'identity',hostOnly:true,version:process.version,execArgv:process.execArgv,hostCase,
 nativeOrGuestOrEngineExecuted:false}));
try{
 for(const phase of ['A','B','C']){
  // No intentional yield between A's resolved return and B's genuine entry.
  const result=await state.referenceCall(phase,hostCase);
  if(phase==='C'){finalCleanup=state.dispose();result.finalCleanup=finalCleanup;}
  console.log(JSON.stringify({kind:'whole-call',phase,ordinal:result.ordinal,observed:result}));
  assert.equal(result.passed,true,JSON.stringify(result));unrefPublicProjection(result);completed++;
 }
 assert.equal(finalCleanup.workloadPendingAfterClear,0);assert.deepEqual(finalCleanup.errors,[]);
 console.log(JSON.stringify({schemaVersion:1,state:'UNREF_REUSE_NODE22_HOST_REFERENCE_PASSED_V1',passed:true,
  hostOnly:true,completed,calls:[1,2,3],phases:['A','B','C'],hostCase,policy:'preserve-old-unref-tasks',
  finalCleanup,nativeOrGuestOrEngineExecuted:false,physicalStoreOrNativeOwnerIdentityProved:false,
  timerAccuracyOrPermanentCancellationProved:false}));
}finally{if(!finalCleanup)console.log(JSON.stringify({kind:'failure-cleanup',observed:state.dispose()}));}
