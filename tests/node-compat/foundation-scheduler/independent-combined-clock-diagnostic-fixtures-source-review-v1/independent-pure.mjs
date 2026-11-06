// Host synthetic DATA only. No fixture/private native module/process/clock import.
import assert from 'node:assert/strict';
import {requireAllInvalidEvidence, requireNativeDelta, requireNextExportBoundary} from '../combined-clock-diagnostic-fixtures-candidate-v1/collectors.mjs';
import {validateSnapshot} from '../combined-clock-diagnostics-candidate-v1/validate-snapshot.mjs';
const names=['queueEnqueue','queueDetachRun','queueDetachCancel','interestIncr','interestDecr','selectorCall','prunedInvalid','selectorEmpty','pollCall','emptyPollAttempt','timerConstruct','timerRetire','timerDestroy','timerAcquire','timerDropAttempt','timerDropReturned','hostMonotonicDropAttempt','hostMonotonicDropReturned','immediateCacheAcquire','immediateCacheUse','callEntered','loopBoundary','postCallBoundary'];
const runtime={queued:'0',interest:0,loopRunning:false,timerRegistry:'0',immediateCacheOwned:false};
const absent={present:false,callSerial:'0',functionIndex:'0',runtime:{...runtime},loopResultObserved:false,loopReturnedSuccess:false,currentFunction:-1,freeListSize:'0'};
const before={schemaVersion:1,diagnosticOnly:true,overflow:false,invariantViolation:false,recordingComplete:true,hostResourceTableObserved:false,destructionAtHostStoreExitObserved:false,eventSerial:'0',currentCallSerial:'1',current:{...runtime,interest:1},afterLoop:structuredClone(absent),afterPostCall:structuredClone(absent),counters:Object.fromEntries(names.map(n=>[n,'0'])),timerLeases:[]};
before.counters.callEntered=before.counters.interestIncr='1';let cases=0;const raw=JSON.stringify;
assert.deepEqual(validateSnapshot(raw(before)),before);cases++;
const pruned=structuredClone(before);Object.assign(pruned.counters,{queueEnqueue:'1',prunedInvalid:'1',selectorEmpty:'1',selectorCall:'1'});
assert.deepEqual(requireAllInvalidEvidence(raw(before),raw(pruned)),{observedPruningOnly:true,constructibleWithSnapshotOnlyApi:false,fullGateAccepted:false});cases++;
for(const [field,value]of [['mono_clock_offset','0'],['resumeEpoch','0'],['hostStoreAlive',true],['freeBytes','0'],['rawHostMonotonicNow','0']]){const bad=structuredClone(before);bad[field]=value;assert.throws(()=>validateSnapshot(raw(bad)));cases++;}
for(const [field,value]of [['callEntered','0'],['interestDecr','2'],['timerAcquire','1'],['loopBoundary','2'],['timerRetire','1']]){const bad=structuredClone(before);bad.counters[field]=value;assert.throws(()=>validateSnapshot(raw(bad)));cases++;}
for(const [field,value]of [['overflow',true],['recordingComplete',false],['hostResourceTableObserved',true],['destructionAtHostStoreExitObserved',true]]){const bad=structuredClone(before);bad[field]=value;assert.throws(()=>validateSnapshot(raw(bad)));cases++;}
assert.throws(()=>requireAllInvalidEvidence(raw(before),raw(before)));cases++;
assert.throws(()=>requireNextExportBoundary(raw(before),raw(before),0));cases++;
const noDelta=structuredClone(before);noDelta.current.loopRunning=true;
assert.deepEqual(requireNativeDelta(raw(before),raw(noDelta),{construct:0,acquire:0,run:0,cancel:0}).delta,Object.fromEntries(names.map(n=>[n,0n])));cases++;
for(const value of [-1,0.5,513,NaN])assert.throws(()=>requireNativeDelta(raw(before),raw(noDelta),{construct:value,acquire:0,run:0,cancel:0})),cases++;
console.log(JSON.stringify({schemaVersion:1,passed:true,cases,allInvalidSyntheticPositiveStillFullGateFalse:true,unsupportedNativeFieldsRefused:true,fixtureOrGuestImported:false,nativeOrClockActions:false}));
