// Independent actual exported pure functions only. No operational entry/helper,
// generated/fixture imports, guest, host worker, timer or compiler is invoked.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {fatalJcoObservation} from '../combined-native-runtime-candidate-v2/models.mjs';
import {fatalJcoEvidence} from '../combined-native-runtime-candidate-v1/models.mjs';
import {captureSync,captureDiagnostics} from '../combined-native-runtime-candidate-v2/capture.mjs';
import {plannedCalls} from '../combined-native-runtime-candidate-v2/session-model.mjs';
const P=dirname(fileURLToPath(import.meta.url)),source=join(P,'../combined-native-runtime-candidate-v2');
const refs=JSON.parse(await readFile(join(source,'references.json'))),ix=JSON.parse(await readFile(join(P,'intake-summary.json'))).sourceIndex;
const component=refs.artifactSlots.fatal.knownComponent;
assert(component&&component.sha256.startsWith('9d28937f'));
const terminal={closed:true,ownedGroupGone:true,spawnError:null,timedOut:false,externalSignal:null,outputLimitExceeded:false,errors:[],signals:[],signalCount:0,status:1,signal:null,terminalExitZeroObserved:false};
const mark=(version,own)=>({schemaVersion:1,state:'COMBINED355_FATAL_PUBLIC_CALL_ARMED_'+version,sourceIndex:own,component,fixtureId:'fatal',name:'run',args:[],moduleImportCompleted:true,publicExportAboutToBeInvoked:true});
const marker=mark('V2',ix),oldmarker=mark('V1',refs.previousSourceIndex);let checks=0,getters=0,legacyAccepted=0;
async function capture(value,{writerFail=false,returns=false}={}){
 const rows=[],sequence={attempted:0,written:0},writer=Object.freeze(Error('independent memory writer failure'));let didThrow=false,caught;
 try{await captureSync({invoke(){if(returns)return value;throw value;},name:'run',args:[],sequence,now:()=>123,write(n,row){if(writerFail)throw writer;rows.push(row);}});}catch(error){didThrow=true;caught=error;}
 if(returns)assert.equal(didThrow,false);else{assert(didThrow);assert(Object.is(caught,value));}checks++;
 return{typed:rows[0]??null,caught:{capture:captureDiagnostics(sequence)}};
}
function checkInconclusive(row,t=terminal){const value=fatalJcoObservation(t,marker,row.typed,row.caught,component,ix);assert.equal(value.callbackCause,'inconclusive');for(const k of ['expectedCallbackFailureProved','fatalCallbackGateSatisfied','nativeCallbackReachedObserved','uniqueOriginalJsErrorIdentityProved'])assert.equal(value[k],false);checks++;return value;}
const expected=await capture(Error('RESOURCE_UNHANDLED_TIMER_CALLBACK')),unrelated=await capture(Error('not the callback'));
assert.deepEqual(expected.typed,unrelated.typed);checks++;
for(const row of [expected,unrelated]){fatalJcoEvidence(terminal,oldmarker,row.typed,row.caught,component,refs.previousSourceIndex);legacyAccepted++;checkInconclusive(row);}
for(const value of [undefined,null,false,0,-0,NaN,Infinity,1n,'RESOURCE_UNHANDLED_TIMER_CALLBACK',Object.freeze(Error('frozen unrelated')),Object.freeze({get message(){getters++;throw 1;},get stack(){getters++;throw 2;},get then(){getters++;throw 3;}})])checkInconclusive(await capture(value));
assert.equal(getters,0);checks++;
checkInconclusive({typed:null,caught:null},{...terminal,status:null,signal:'SIGABRT'});
for(const value of [null,undefined,false,Error('unrelated')]){const row=await capture(value,{writerFail:true});assert.throws(()=>fatalJcoObservation(terminal,marker,row.typed,row.caught,component,ix));checks++;}
const returned=await capture('unexpected return',{returns:true});assert.throws(()=>fatalJcoObservation(terminal,marker,returned.typed,returned.caught,component,ix));checks++;
for(const change of [{status:0,terminalExitZeroObserved:true},{timedOut:true},{ownedGroupGone:false},{signal:'SIGTERM',status:null},{signal:'SIGKILL',status:null},{errors:['cleanup failed']},{signals:['SIGKILL']},{outputLimitExceeded:true}]){assert.throws(()=>fatalJcoObservation({...terminal,...change},marker,expected.typed,expected.caught,component,ix));checks++;}
for(const bad of [null,{...marker,moduleImportCompleted:false},{...marker,publicExportAboutToBeInvoked:false},{...marker,sourceIndex:refs.previousSourceIndex},{...marker,component:{...component,sha256:'f'.repeat(64)}}]){assert.throws(()=>fatalJcoObservation(terminal,bad,expected.typed,expected.caught,component,ix));checks++;}
assert.equal(plannedCalls('resource','retained').length,23);assert.equal(plannedCalls('resource','fresh').length,9);assert.equal(23+9+3,35);assert.deepEqual(plannedCalls('resource','retained').slice(1,-1).map(r=>r.args[0]),Array.from({length:21},(_,i)=>i%7));assert.equal(21+7+3*7,49);assert.equal(49*2,98);assert.equal(7*46,322);checks+=7;
for(const id of ['clock-snapshot','surviving-interest']){assert.equal(plannedCalls(id,'retained').length,3);assert.equal(plannedCalls(id,'fresh').length,1);assert.throws(()=>plannedCalls(id,'node-oracle'));checks+=3;}
const contract=JSON.parse(await readFile(join(source,'future-runtime-review-contract.template.json')));assert.equal(contract.fatalGateReviewPassedState,null);assert.equal(contract.perFixtureRequiredStates.fatal,undefined);assert.deepEqual(contract.fatalObservationRequiredFixedValues,{callbackCause:'inconclusive',expectedCallbackFailureProved:false,fatalCallbackGateSatisfied:false,current355NativeCallbackDiagnosticAvailable:false});checks+=3;
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_FATAL_CAUSE_AND_PRESERVED_SCHEDULE_PURE_CASES_PASSED',checks,legacyExpectedAndUnrelatedAccepted:legacyAccepted,actualCaptureRowsIndistinguishable:true,newGenericCauseAlwaysInconclusive:true,expectedCallbackFailureProved:false,fatalCallbackGateSatisfied:false,getterReads:getters,operationalActionsInvoked:false,syntheticMemoryCaptureOnly:true}));
