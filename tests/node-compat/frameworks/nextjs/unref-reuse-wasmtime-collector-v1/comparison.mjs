// Pure retained DATA only. Imports define functions; no workload/timer/store runs.
import assert from 'node:assert/strict';
import {isDeepStrictEqual} from 'node:util';
import {validateUnrefCollection} from '../../../async-context/unref-reuse-candidate-v1/validation.mjs';
import {unrefPublicProjection} from '../../../async-context/unref-reuse-candidate-v1/cases.mjs';
const phases=['A','B','C'];
const exact=(value,keys)=>{assert(value&&typeof value==='object'&&!Array.isArray(value));assert.deepEqual(Object.keys(value).sort(),[...keys].sort());};
export function validateCollection(value,call,contract,hostCase,boundaryMode){
 assert(Number.isInteger(call)&&call>=1&&call<=3);
 validateUnrefCollection(value,phases[call-1],hostCase,boundaryMode,contract);
 return{callChecks:value.checks.length,callbackChecks:value.callbackChecks.length};
}
export function validate(value,call,contract,hostCase){
 exact(value,['schemaVersion','marker','call','method','collection']);assert.equal(value.schemaVersion,1);
 assert.equal(value.marker,'NEXT_NATIVE_UNREF_REUSE_V1');assert.equal(value.call,call);assert.equal(value.method,'GET');
 return validateCollection(value.collection,call,contract,hostCase,'actual-native-private-boundaries');
}
// Invoke only AFTER the complete raw body is durable. No projection/oracle work.
export function assessSafety(bytes,status,call,contract,hostCase){
 let value;
 try{value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}
 catch(error){return{safeToReuse:false,reason:'malformed-or-undecodable-response',error:String(error)};}
 try{validate(value,call,contract,hostCase);}
 catch(error){return{envelope:value,safeToReuse:false,reason:'strict-native-envelope-or-collection-refused',validationFailure:{name:error?.name??typeof error,message:error?.message??String(error),stack:error?.stack??null}};}
 if(status!==200)return{envelope:value,safeToReuse:false,reason:'http-status-'+status,reportedPassed:value.collection.passed};
 return{envelope:value,safeToReuse:true,reason:'strict-native-envelope-and-collection-validated'};
}
export function compare(actual,node,call,contract,hostCase){
 validate(actual,call,contract,hostCase);validateCollection(node,call,contract,node.firstHostCase,'node-public-empty-store-projection');
 const actualProjection=unrefPublicProjection(actual.collection),nodeProjection=unrefPublicProjection(node);
 return{call,phase:phases[call-1],classification:isDeepStrictEqual(actualProjection,nodeProjection)?'matches-node-public-projection':'difference-requires-review',
  actualProjection,nodeProjection,actualWholeCollection:actual.collection,nodeOriginalWholeCollection:node};
}
export function parseOracle(text,contract){
 assert.equal(typeof text,'string');const frames=text.trim().split('\n').map(JSON.parse);assert.equal(frames.length,5);
 const identity=frames[0];exact(identity,['kind','hostOnly','version','execArgv','hostCase','nativeOrGuestOrEngineExecuted']);
 assert.equal(identity.kind,'identity');assert.equal(identity.hostOnly,true);assert.equal(identity.version,'v22.14.0');assert.deepEqual(identity.execArgv,[]);assert.equal(identity.nativeOrGuestOrEngineExecuted,false);
 const values=[];
 for(let call=1;call<=3;call++){
  const f=frames[call];exact(f,['kind','phase','ordinal','observed']);assert.equal(f.kind,'whole-call');assert.equal(f.phase,phases[call-1]);assert.equal(f.ordinal,call);
  validateCollection(f.observed,call,contract,identity.hostCase,'node-public-empty-store-projection');values.push(f.observed);
 }
 const summary=frames[4];exact(summary,['schemaVersion','state','passed','hostOnly','completed','calls','phases','hostCase','policy','finalCleanup','nativeOrGuestOrEngineExecuted','physicalStoreOrNativeOwnerIdentityProved','timerAccuracyOrPermanentCancellationProved']);
 assert.equal(summary.schemaVersion,1);assert.equal(summary.state,'UNREF_REUSE_NODE22_HOST_REFERENCE_PASSED_V1');assert.equal(summary.passed,true);assert.equal(summary.hostOnly,true);assert.equal(summary.completed,3);assert.deepEqual(summary.calls,[1,2,3]);assert.deepEqual(summary.phases,phases);assert.equal(summary.hostCase,identity.hostCase);assert.equal(summary.policy,'preserve-old-unref-tasks');assert.deepEqual(summary.finalCleanup,values[2].finalCleanup);
 for(const k of ['nativeOrGuestOrEngineExecuted','physicalStoreOrNativeOwnerIdentityProved','timerAccuracyOrPermanentCancellationProved'])assert.equal(summary[k],false);
 const hostCallChecks=values.reduce((n,v)=>n+v.checks.length,0),distinctCallbackChecks=values[2].callbackChecks.length;
 assert.equal(hostCallChecks,51);assert.equal(distinctCallbackChecks,9);assert.deepEqual(values.map(v=>v.callbackChecks.length),[0,7,9]);
 return{frames,values,summary,identity,hostCallChecks,distinctCallbackChecks,callbackInventoriesAreCumulativeNotSummed:true};
}
