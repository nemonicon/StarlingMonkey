// Pure host capture/diagnostic seams only. No worker/API/crypto/generated call.
import assert from 'node:assert/strict';
import {capturedCall,captureFailureDiagnostics,diagnosticWrite} from './runtime-body.mjs';
let checks=0;
for(const X of [new Error('synthetic guest X'),Object.freeze({synthetic:'frozen-X'}),null,false,0,-0,undefined,1n,'synthetic-X']){
 for(const diagnosticThrows of [false,true]){
  const Y=Object.freeze({synthetic:'writer-Y'}),Z=Object.freeze({synthetic:'diagnostic-Z'}),sequence={attempted:0,written:0};let caught,didThrow=false,callbackCalls=0;
  try{await capturedCall({invoke(){throw X;},name:'run',args:[0],sequence,write:async()=>{throw Y;},onCaptureFailure:async failure=>{callbackCalls++;assert.equal(failure.captureError,Y);assert.equal(failure.kind,'throw');assert.equal(Object.isFrozen(failure),true);if(diagnosticThrows)throw Z;}});}catch(error){caught=error;didThrow=true;}
  assert.equal(didThrow,true);checks++;assert.equal(Object.is(caught,X),true);checks++;assert.equal(sequence.captureFailures[0].captureError,Y);checks++;
  assert.equal(sequence.attempted,1);assert.equal(sequence.written,0);assert.equal(callbackCalls,1);checks++;
  assert.equal(sequence.diagnosticFailures?.length??0,diagnosticThrows?1:0);if(diagnosticThrows)assert.equal(sequence.diagnosticFailures[0].diagnosticError,Z);checks++;
  const safe=captureFailureDiagnostics(sequence);JSON.stringify(safe);assert.equal(safe.captureWriteFailures[0].kind,'throw');checks++;
 }
}
const returned='{"synthetic":true}',Y=Object.freeze({synthetic:'returned-writer-Y'}),state={attempted:0,written:0};let caught;
try{await capturedCall({invoke:()=>returned,name:'inspect',args:[],sequence:state,write:async()=>{throw Y;}});}catch(error){caught=error;}
assert.equal(caught,Y);assert.equal(state.captureFailures[0].captureError,Y);assert.equal(state.written,0);checks++;
const X=Object.freeze({synthetic:'successful-raw-throw'}),success={attempted:0,written:0};let raw;
try{await capturedCall({invoke(){throw X;},name:'inspect',args:[],sequence:success,write:async(p,v)=>{raw=v;}});}catch(error){caught=error;}
assert.equal(caught,X);assert.equal(raw.kind,'throw');assert.equal(success.written,1);assert.equal(success.captureFailures,undefined);checks++;
// This is the actual helper used by worker AND parent failure.json paths.
for(const error of [new Error('failure-record writer'),null,false,Object.freeze({synthetic:'failure-record'})]){
 const sequence={attempted:1,written:0};const written=await diagnosticWrite({write:async()=>{throw error;},name:'failure.json',value:{diagnosticOnly:true},sequence});
 assert.equal(written,false);assert.equal(sequence.diagnosticFailures[0].diagnosticError,error);checks++;
 let propagated;try{await diagnosticWrite({write:async()=>{throw error;},name:'failure.json',value:{},sequence});throw X;}catch(e){propagated=e;}
 assert.equal(propagated,X);checks++;
}
const diagnosticState={};assert.equal(await diagnosticWrite({write:async()=>{},name:'failure.json',value:{},sequence:diagnosticState}),true);assert.equal(diagnosticState.diagnosticFailures,undefined);checks++;
const ordinary={attempted:0,written:0};assert.deepEqual(await capturedCall({invoke:()=>'{"ok":true}',name:'inspect',args:[],sequence:ordinary,write:async()=>{}}),{ok:true});assert.deepEqual(ordinary,{attempted:1,written:1});checks++;
console.log(JSON.stringify({schemaVersion:1,passed:true,checks,combinedOriginals:9,combinedCallbackModes:2,originalThrowIdentityPreserved:true,actualWriterAndDiagnosticValuesRetainedInHostState:true,failedCaptureCanComplete:false,ownerAPIsOrWorkerOrOracleOrGeneratedOrEngineOrGuestInvoked:false}));
