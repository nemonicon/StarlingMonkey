// Host-only synthetic plain DATA; never import a fixture or the private builtin.
import assert from 'node:assert/strict';
import {requireNativeDelta, requireNextExportBoundary, requireAllInvalidEvidence, CASE_NATIVE} from './collectors.mjs';
import {validateSnapshot} from '../combined-clock-diagnostics-candidate-v1/validate-snapshot.mjs';
const names = ['queueEnqueue','queueDetachRun','queueDetachCancel','interestIncr','interestDecr','selectorCall','prunedInvalid','selectorEmpty','pollCall','emptyPollAttempt','timerConstruct','timerRetire','timerDestroy','timerAcquire','timerDropAttempt','timerDropReturned','hostMonotonicDropAttempt','hostMonotonicDropReturned','immediateCacheAcquire','immediateCacheUse','callEntered','loopBoundary','postCallBoundary'];
const runtime = {queued:'0',interest:0,loopRunning:false,timerRegistry:'0',immediateCacheOwned:false};
const absent = {present:false,callSerial:'0',functionIndex:'0',runtime:{...runtime},loopResultObserved:false,loopReturnedSuccess:false,currentFunction:-1,freeListSize:'0'};
const before = {schemaVersion:1,diagnosticOnly:true,overflow:false,invariantViolation:false,recordingComplete:true,hostResourceTableObserved:false,destructionAtHostStoreExitObserved:false,eventSerial:'0',currentCallSerial:'1',current:{...runtime,interest:1},afterLoop:structuredClone(absent),afterPostCall:structuredClone(absent),counters:Object.fromEntries(names.map(n=>[n,'0'])),timerLeases:[]};
before.counters.callEntered='1';before.counters.interestIncr='1';
const raw=JSON.stringify, clone=structuredClone;let checks=0;
function pass(fn){fn();checks++;}function fails(fn){assert.throws(fn);checks++;}
function makeAfter(e){
 const a=clone(before);a.current.loopRunning=true;a.eventSerial=String(4*e.acquire);
 const values={queueEnqueue:e.acquire,queueDetachRun:e.run,queueDetachCancel:e.cancel,selectorCall:e.run,pollCall:e.run,timerConstruct:e.construct,timerRetire:e.construct,timerDestroy:e.construct,timerAcquire:e.acquire,timerDropAttempt:e.acquire,timerDropReturned:e.acquire,hostMonotonicDropAttempt:e.acquire,hostMonotonicDropReturned:e.acquire};
 for(const[n,v]of Object.entries(values))a.counters[n]=String(v);
 for(let i=0;i<e.acquire;i++)a.timerLeases.push({serial:String(i+1),timerId:i+1,acquiredAt:String(4*i+1),invalidatedAt:String(4*i+2),dropAttemptAt:String(4*i+3),dropReturnedAt:String(4*i+4),owned:false});
 return a;
}
for(const e of CASE_NATIVE)pass(()=>requireNativeDelta(raw(before),raw(makeAfter(e)),e));
const after=makeAfter(CASE_NATIVE[1]);
for(const edit of [v=>v.overflow=true,v=>v.invariantViolation=true,v=>v.recordingComplete=false,v=>v.timerLeases[0].owned=true,v=>v.timerLeases[0].dropReturnedAt='0',v=>v.counters.timerRetire='1',v=>v.counters.timerDestroy='1',v=>v.counters.hostMonotonicDropReturned='1',v=>v.counters.prunedInvalid='1',v=>v.counters.selectorEmpty='1',v=>v.counters.emptyPollAttempt='1',v=>v.counters.immediateCacheUse='1',v=>v.current.interest=0,v=>v.current.timerRegistry='1',v=>v.current.loopRunning=false,v=>v.eventSerial='9',v=>v.currentCallSerial='2',v=>v.counters.callEntered='2',v=>v.timerLeases[0].serial='2',v=>v.extra='unknown']){
 const bad=clone(after);edit(bad);fails(()=>requireNativeDelta(raw(before),raw(bad),CASE_NATIVE[1]));
}
const next=clone(after);next.currentCallSerial='2';next.current.loopRunning=false;
for(const n of ['callEntered','loopBoundary','postCallBoundary','interestIncr','interestDecr'])next.counters[n]=String(BigInt(next.counters[n])+1n);
next.afterLoop={present:true,callSerial:'1',functionIndex:'7',runtime:{...runtime},loopResultObserved:true,loopReturnedSuccess:true,currentFunction:7,freeListSize:'1'};
next.afterPostCall={...clone(next.afterLoop),loopResultObserved:false,loopReturnedSuccess:false,currentFunction:-1,freeListSize:'0'};
pass(()=>requireNextExportBoundary(raw(after),raw(next),7));
for(const edit of [v=>v.afterLoop.callSerial='0',v=>v.afterPostCall.functionIndex='8',v=>v.afterLoop.runtime.interest=1,v=>v.afterPostCall.freeListSize='1',v=>v.afterPostCall.currentFunction=7,v=>v.current.interest=0,v=>v.counters.postCallBoundary='0',v=>v.timerLeases[0].timerId=99]){
 const bad=clone(next);edit(bad);fails(()=>requireNextExportBoundary(raw(after),raw(bad),7));
}
fails(()=>requireNextExportBoundary(raw(after),raw(next),8));
fails(()=>requireNextExportBoundary(raw(after),raw(next),null));
// Public double clear is genuine native detach-cancel, NOT all-invalid pruning.
fails(()=>requireAllInvalidEvidence(raw(before),raw(after)));
// Native offset and two different hidden host Stores can have identical exported
// snapshot data: these fields do not exist in the actual module schema.
for(const field of ['mono_clock_offset','resumeEpoch','hostStoreAlive','rawHostMonotonicNow']){
 const unsupported=clone(before);unsupported[field]='123';fails(()=>validateSnapshot(raw(unsupported)));
}
const incomplete=clone(before);incomplete.overflow=true;incomplete.recordingComplete=false;
incomplete.timerLeases=Array.from({length:513},(_,i)=>({serial:String(i+1)}));fails(()=>validateSnapshot(raw(incomplete)));
assert.deepEqual(CASE_NATIVE.reduce((a,r)=>Object.fromEntries(Object.keys(a).map(k=>[k,a[k]+r[k]])),{construct:0,acquire:0,run:0,cancel:0}),{construct:46,acquire:48,run:14,cancel:34});checks++;
console.log(JSON.stringify({schemaVersion:1,state:'SYNTHETIC_DIAGNOSTIC_FIXTURE_MODELS_PASSED_V1',checks,guestExecuted:false,nativeTaskInvoked:false,clockRead:false,allInvalidFixtureAvailable:false,nativeOffsetObserved:false,hostStoreDropObserved:false}));
