// Pure counterexamples only. No fixture/generated application/provider imported.
import assert from 'node:assert/strict';
import {captureSync,captureDiagnostics} from './capture.mjs';
import {fatalJcoObservation} from './models.mjs';
const d=n=>({path:'/synthetic-no-action/'+n,sha256:'a'.repeat(64),bytes:1}),own=d('index.json'),component=d('component.wasm');
const marker={schemaVersion:1,state:'COMBINED355_FATAL_PUBLIC_CALL_ARMED_V3',sourceIndex:own,component,fixtureId:'fatal',name:'run',args:[],moduleImportCompleted:true,publicExportAboutToBeInvoked:true};
const terminal={closed:true,ownedGroupGone:true,spawnError:null,timedOut:false,externalSignal:null,outputLimitExceeded:false,errors:[],signals:[],signalCount:0,status:1,signal:null,terminalExitZeroObserved:false};let checks=0;
function inconclusive(v){assert.equal(v.observedInvocationFailure,true);assert.equal(v.callbackCause,'inconclusive');for(const key of ['expectedCallbackFailureProved','fatalCallbackGateSatisfied','nativeCallbackReachedObserved','uniqueOriginalJsErrorIdentityProved'])assert.equal(v[key],false);checks++;}
async function rowFor(value,writeFailure=false){const rows=[],sequence={attempted:0,written:0},writer=Error('writer');let seen=false,caught;try{await captureSync({invoke(){throw value;},name:'run',args:[],sequence,now:()=>0,write:async(n,r)=>{if(writeFailure)throw writer;rows.push(r);}});}catch(e){seen=true;caught=e;}assert(seen&&Object.is(caught,value));checks++;return{typed:rows[0]??null,caught:{capture:captureDiagnostics(sequence)}};}
const expected=await rowFor(Error('RESOURCE_UNHANDLED_TIMER_CALLBACK')),unrelated=await rowFor(Error('UNRELATED_BINDING_OR_SHIM'));
assert.deepEqual(expected.typed,unrelated.typed);checks++;inconclusive(fatalJcoObservation(terminal,marker,expected.typed,expected.caught,component,own));inconclusive(fatalJcoObservation(terminal,marker,unrelated.typed,unrelated.caught,component,own));
for(const value of [null,undefined,0,false,'RESOURCE_UNHANDLED_TIMER_CALLBACK',Object.freeze(Error('frozen unrelated'))]){const r=await rowFor(value);inconclusive(fatalJcoObservation(terminal,marker,r.typed,r.caught,component,own));}
let getterReads=0;const poisoned=Object.freeze({get message(){getterReads++;throw 1;},get stack(){getterReads++;throw 2;},get toString(){getterReads++;throw 3;}}),r=await rowFor(poisoned);inconclusive(fatalJcoObservation(terminal,marker,r.typed,r.caught,component,own));assert.equal(getterReads,0);checks++;
inconclusive(fatalJcoObservation({...terminal,status:null,signal:'SIGABRT'},marker,null,null,component,own));
for(const value of [Error('expected label'),null,undefined,0,false]){const r=await rowFor(value,true);assert.throws(()=>fatalJcoObservation(terminal,marker,r.typed,r.caught,component,own));checks++;}
for(const change of [{timedOut:true},{externalSignal:'SIGTERM'},{signals:[{signal:'SIGKILL'}]},{errors:[{stage:'forced cleanup'}]},{status:null,signal:'SIGTERM'},{status:null,signal:'SIGKILL'}]){assert.throws(()=>fatalJcoObservation({...terminal,...change},marker,expected.typed,expected.caught,component,own));checks++;}
assert.throws(()=>fatalJcoObservation(terminal,null,expected.typed,expected.caught,component,own));checks++;
assert.throws(()=>fatalJcoObservation(terminal,{...marker,moduleImportCompleted:false},expected.typed,expected.caught,component,own));checks++;
assert.throws(()=>fatalJcoObservation(terminal,marker,{...expected.typed,kind:'return'},expected.caught,component,own));checks++;
assert.throws(()=>fatalJcoObservation({...terminal,status:null,signal:'SIGABRT'},marker,{...expected.typed,kind:'return'},null,component,own));checks++;
assert.throws(()=>fatalJcoObservation(terminal,marker,null,null,component,own));checks++;
console.log(JSON.stringify({schemaVersion:1,checks,passed:true,expectedAndUnrelatedOpaqueRecordsIdentical:true,allGenericThrowsAndAbortCauseInconclusive:true,expectedCallbackFailureProved:false,fatalCallbackGateSatisfied:false,errorGettersRead:getterReads,fixtureOrNativeOrGeneratedInvoked:false}));
