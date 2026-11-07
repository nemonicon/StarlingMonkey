// Synthetic retained-log DATA only; no stream/resource/timer/socket/guest objects.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {analyze,parseDiagnosticLog,marker} from './classification.mjs';
const plan=JSON.parse(readFileSync(new URL('./plan.json',import.meta.url),'utf8'));
const label='inert-data',firstLabel='inert-first',ordinal=3;
const event=(phase,fields={})=>({schemaVersion:1,marker,origin:'actual-wasi-guest',sequence:1,
 firstLabel,ordinal,label,route:'/output',phase,context:null,...fields});
const seq=events=>events.map((e,i)=>({...e,sequence:i+1}));
const enter=()=>[event('adapter-enter',{requestSignalLinkedToPeer:true,independentPeerDisconnectSignal:false,adapterPolicy:'observed-io-abort-specific-output-closed-v2'}),
 event('request-signal-created',{aborted:false,alreadyAbortedBeforeListener:false,reasonMatchesObservedIo:false}),
 event('handler-enter',{signalAborted:false,requestSignalLinkedToPeer:true,requestSignalPolicy:'observed-io-only',independentPeerDisconnectSignal:false}),event('handler-finally')];
const normal=()=>seq([...enter(),event('output-write-invocation-attempt',{bytes:1}),event('output-write-returned'),event('outgoing-finish-returned'),event('response-reader-lock-release-returned'),event('adapter-finally-returned')]);
const abort=()=>[event('io-abort-invocation-attempt',{firstObservation:true}),event('request-signal-abort-event',{signalAborted:true,reasonMatchesObservedIo:true}),event('io-abort-returned',{controllerAborted:true,requestCreated:true,requestSignalAborted:true,requestReasonMatchesFirstObservedIo:true})];
const handled=()=>seq([...enter(),event('producer-pull-enter'),event('producer-pull-finally'),event('output-write-invocation-attempt',{bytes:4096}),event('output-write-returned'),
 event('output-write-invocation-attempt',{bytes:4096}),event('output-write-failed',{error:{payloadTag:'closed'}}),...abort(),event('known-output-closed-handling-enter'),
 event('response-reader-cancel-invocation-attempt'),event('producer-cancel-enter'),event('producer-cancel-returned'),event('response-reader-cancel-returned'),event('response-reader-lock-release-returned'),
 event('dispose-returned',{resource:'output-stream'}),event('dispose-returned',{resource:'outgoing-body-unfinished'}),event('dispose-returned',{resource:'incoming-request'}),
 event('adapter-finally-returned'),event('known-output-closed-handled-return',{requestSignalAborted:true,adapterCleanupCallsReturned:true,nativeResourceCountsOrStoreDeathProved:false,outgoingBodyFinished:false})]);
const record={label,status:200,clientCloseObserved:true,forcedClientCleanup:false,firstBodyBeforeClose:true};
const run=(events,kind='output-close',extra={})=>analyze({...record,...extra},events,{firstLabel,ordinal,kind});
let checks=0;
assert.equal(run(handled()).knownHandledOutputClosedPath,true);checks++;
assert.equal(run(handled()).safeToRequestAgain,true);checks++;
for(const phase of ['output-write-failed','io-abort-invocation-attempt','io-abort-returned','request-signal-abort-event','known-output-closed-handling-enter',
 'response-reader-cancel-invocation-attempt','producer-cancel-enter','producer-cancel-returned','response-reader-cancel-returned','response-reader-lock-release-returned','adapter-finally-returned','known-output-closed-handled-return']){
 const result=run(seq(handled().filter(e=>e.phase!==phase)));assert.equal(result.knownHandledOutputClosedPath,false,phase);assert.equal(result.safeToRequestAgain,false,phase);checks++;
}
for(const phase of ['adapter-failed','dispose-failed','io-abort-failed','input-cleanup-failed','response-reader-cancel-failed','response-reader-cancel-failed-suppressed']){
 assert.equal(run(seq([...handled(),event(phase,{resource:'any'})])).safeToRequestAgain,false,phase);checks++;
}
for(const change of [e=>e.phase==='output-write-failed'?{...e,error:{payloadTag:'last-operation-failed'}}:e,
 e=>e.phase==='io-abort-returned'?{...e,requestSignalAborted:false}:e,
 e=>e.phase==='request-signal-abort-event'?{...e,reasonMatchesObservedIo:false}:e,
 e=>({...e,firstLabel:'changed-factory'}),e=>({...e,ordinal:1})]){
 assert.equal(run(handled().map(change)).safeToRequestAgain,false);checks++;
}
const reordered=handled(),a=reordered.findIndex(e=>e.phase==='response-reader-lock-release-returned'),b=reordered.findIndex(e=>e.phase==='response-reader-cancel-returned');
[reordered[a],reordered[b]]=[reordered[b],reordered[a]];assert.equal(run(seq(reordered)).safeToRequestAgain,false);checks++;
assert.equal(run(normal()).ioPathObserved,false);checks++;
assert.equal(run(normal()).safeToRequestAgain,true);checks++;
assert.equal(run(handled(),'output-close',{transportOrCollectionError:{type:'object'}}).safeToRequestAgain,false);checks++;
assert.equal(run(handled(),'output-close',{firstBodyBeforeClose:false}).ioPathObserved,false);checks++;
assert.equal(run(seq([...handled(),event('producer-pull-enter')])).safeToRequestAgain,false);checks++;
for(const resource of ['output-stream','outgoing-body-unfinished','incoming-request']){
 assert.equal(run(seq(handled().filter(e=>!(e.phase==='dispose-returned'&&e.resource===resource)))).safeToRequestAgain,false);checks++;
}
const barrier=event('input-read-invocation-attempt',{inputBytes:1024,hostReadEnteredOrBlockedProved:false});
const input=()=>seq([...enter(),barrier,event('input-read-failed',{error:{payloadTag:'last-operation-failed'}}),...abort(),
 event('handler-read-failed',{received:1024,signalAborted:true,signalReasonMatchesReadError:true}),event('handler-body-finally',{received:1024,signalAborted:true}),
 event('output-write-invocation-attempt',{bytes:1}),event('output-write-returned'),event('outgoing-finish-returned'),event('response-reader-lock-release-returned'),event('adapter-finally-returned')]);
assert.equal(run(input(),'upload-close',{synchronizedMilestone:input().find(e=>e.phase==='input-read-invocation-attempt')}).ioPathObserved,true);checks++;
for(const phase of ['handler-read-failed','handler-body-finally','request-signal-abort-event']){
 assert.equal(run(seq(input().filter(e=>e.phase!==phase)),'upload-close',{synchronizedMilestone:input().find(e=>e.phase==='input-read-invocation-attempt')}).ioPathObserved,false);checks++;
}
assert.equal(run(input().map(e=>e.phase==='handler-read-failed'?{...e,signalReasonMatchesReadError:false}:e),'upload-close',{synchronizedMilestone:input().find(e=>e.phase==='input-read-invocation-attempt')}).ioPathObserved,false);checks++;
assert.equal(run(input().map(e=>e.phase==='input-read-failed'?{...e,error:{payloadTag:'closed'}}:e),'upload-close',{synchronizedMilestone:input().find(e=>e.phase==='input-read-invocation-attempt')}).ioPathObserved,false);checks++;
const body=Buffer.from(JSON.stringify({complete:true,received:8192,ordinal,readFailure:null,signalAborted:false,requestSignalPolicy:'observed-io-only',independentPeerDisconnectSignal:false})).toString('base64');
assert.equal(run(normal(),'healthy-upload',{decodedBodyBase64:body}).functionChecksPassed,true);checks++;
assert.equal(run(input(),'healthy-upload',{decodedBodyBase64:body}).functionChecksPassed,false);checks++;
const preAborted=input().filter(e=>e.phase!=='request-signal-abort-event').map(e=>e.phase==='request-signal-created'?{...e,aborted:true,alreadyAbortedBeforeListener:true,reasonMatchesObservedIo:true}:e.phase==='io-abort-returned'?{...e,requestCreated:false,requestSignalAborted:null,requestReasonMatchesFirstObservedIo:null}:e);
assert.equal(run(seq(preAborted),'upload-close',{synchronizedMilestone:input().find(e=>e.phase==='input-read-invocation-attempt')}).ioPathObserved,true);checks++;
const encoded=handled().map(e=>JSON.stringify(e)).join('\n')+'\n';assert.equal(parseDiagnosticLog(encoded,plan.allowedGuestPhases).events.length,handled().length);checks++;
assert.throws(()=>parseDiagnosticLog(JSON.stringify(event('handler-enter',{signalAborted:false,requestSignalLinkedToPeer:false}))+'\n',plan.allowedGuestPhases));checks++;
assert.throws(()=>parseDiagnosticLog(JSON.stringify(event('unknown-phase'))+'\n',plan.allowedGuestPhases));checks++;
console.log(JSON.stringify({schemaVersion:1,sourceOnly:true,pureDataChecks:checks,syntheticLogDataOnly:true,
 realResourceObjectsOrAbortControllerOrWasiOrActorsInvoked:false,actualGuestAssertions:0}));
