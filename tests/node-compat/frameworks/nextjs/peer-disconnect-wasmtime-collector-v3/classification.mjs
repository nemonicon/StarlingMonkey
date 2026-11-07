// Pure retained-DATA classification. No streams/resources, guest calls or I/O.
import assert from 'node:assert/strict';
export const marker='NEXT_PEER_DISCONNECT_DIAGNOSTIC_V1';
export function parseDiagnosticLog(text,allowedPhases) {
  const events=[],hostLines=[];
  const lines=text.split('\n');const incomplete=lines.pop();
  for(const line of lines) {
    let value;try{value=JSON.parse(line);}catch{hostLines.push(line);continue;}
    if(value?.marker!==marker){hostLines.push(line);continue;}
    assert.equal(value.schemaVersion,1);assert.equal(value.origin,'actual-wasi-guest');
    assert(Number.isSafeInteger(value.sequence)&&value.sequence>0);
    assert(Number.isSafeInteger(value.ordinal)&&value.ordinal>=0);
    assert(value.label===null||(typeof value.label==='string'&&value.label.length<=128));
    assert(value.firstLabel===null||(typeof value.firstLabel==='string'&&value.firstLabel.length<=128));
    assert(value.context===null||typeof value.context==='string');assert(allowedPhases.includes(value.phase));
    if(value.phase==='adapter-enter'){assert.equal(value.requestSignalLinkedToPeer,true);assert.equal(value.independentPeerDisconnectSignal,false);assert.equal(value.adapterPolicy,'observed-io-abort-specific-output-closed-v2');}
    if(value.phase==='handler-enter'){assert.equal(typeof value.signalAborted,'boolean');assert.equal(value.requestSignalLinkedToPeer,true);assert.equal(value.requestSignalPolicy,'observed-io-only');assert.equal(value.independentPeerDisconnectSignal,false);}
    if(value.phase==='input-read-invocation-attempt'){
      assert(Number.isSafeInteger(value.inputBytes)&&value.inputBytes>=0&&value.inputBytes<=8192);
      assert.equal(value.hostReadEnteredOrBlockedProved,false);
    }
    if(value.phase==='input-read-returned'){assert(Number.isSafeInteger(value.bytes)&&value.bytes>=0);assert(Number.isSafeInteger(value.inputBytes)&&value.inputBytes>=0);}
    if(value.phase==='output-write-invocation-attempt')assert(Number.isSafeInteger(value.bytes)&&value.bytes>=1&&value.bytes<=4096);
    if(value.phase==='dispose-returned'||value.phase==='dispose-invocation-attempt'||value.phase==='dispose-failed')assert.equal(typeof value.resource,'string');
    if(value.phase==='request-signal-created'){assert.equal(typeof value.aborted,'boolean');assert.equal(value.alreadyAbortedBeforeListener,value.aborted);assert.equal(typeof value.reasonMatchesObservedIo,'boolean');}
    if(value.phase==='request-signal-abort-event'){assert.equal(value.signalAborted,true);assert.equal(typeof value.reasonMatchesObservedIo,'boolean');}
    if(value.phase==='io-abort-returned'){assert.equal(typeof value.controllerAborted,'boolean');assert.equal(typeof value.requestCreated,'boolean');assert(value.requestSignalAborted===null||typeof value.requestSignalAborted==='boolean');assert(value.requestReasonMatchesFirstObservedIo===null||typeof value.requestReasonMatchesFirstObservedIo==='boolean');}
    if(value.phase==='known-output-closed-handled-return'){assert.equal(value.requestSignalAborted,true);assert.equal(value.adapterCleanupCallsReturned,true);assert.equal(value.nativeResourceCountsOrStoreDeathProved,false);assert.equal(value.outgoingBodyFinished,false);}
    events.push(value);
  }
  return{events,hostLines,incompleteTail:incomplete??''};
}
export function analyze(record,events,{firstLabel,ordinal,kind}) {
 const own=events.filter(e=>e.label===record.label),phase=p=>own.filter(e=>e.phase===p),one=p=>phase(p).length===1;
 assert(own.length<=192);
 assert(own.every((e,i)=>Number.isSafeInteger(e.sequence)&&e.sequence>0&&(i===0||e.sequence>own[i-1].sequence)));
 const identity=own.length>0&&own.every(e=>e.firstLabel===firstLabel&&e.ordinal===ordinal);
 const fatalPhases=['adapter-failed','dispose-failed','io-abort-failed','input-cleanup-failed',
  'response-reader-cancel-failed','response-reader-cancel-failed-suppressed'];
 const fatalEvents=own.filter(e=>fatalPhases.includes(e.phase));
 const writes=phase('output-write-invocation-attempt'),returns=phase('output-write-returned'),writeFailures=phase('output-write-failed');
 const readTerminals=phase('input-read-failed').map(e=>({tag:e.error?.payloadTag??e.error?.tag??null,error:e.error}));
 const created=phase('request-signal-created'),aborts=phase('io-abort-returned'),abortEvents=phase('request-signal-abort-event');
 const freshSignal=created.length===1&&created[0].aborted===false&&created[0].reasonMatchesObservedIo===false&&
  phase('io-abort-invocation-attempt').length===0&&aborts.length===0&&abortEvents.length===0&&
  phase('handler-enter').every(e=>e.signalAborted===false);
 const signalProof=created.length===1&&aborts.length>0&&phase('io-abort-invocation-attempt').length===aborts.length&&
  aborts.every(e=>e.controllerAborted===true&&(e.requestCreated===false?
   e.requestSignalAborted===null&&e.requestReasonMatchesFirstObservedIo===null:
   e.requestSignalAborted===true&&e.requestReasonMatchesFirstObservedIo===true))&&
  ((created[0].aborted===true&&created[0].reasonMatchesObservedIo===true&&abortEvents.length===0)||
   (created[0].aborted===false&&abortEvents.length===1&&abortEvents[0].reasonMatchesObservedIo===true));
 const common=identity&&one('adapter-enter')&&one('handler-enter')&&one('handler-finally')&&one('adapter-finally-returned')&&fatalEvents.length===0;
 const normalPath=common&&one('outgoing-finish-returned')&&one('response-reader-lock-release-returned')&&
  writes.length>0&&writes.length===returns.length&&writeFailures.length===0;
 const dropped=kind=>phase('dispose-returned').filter(e=>e.resource===kind).length;
 const actualClosedWrite=writeFailures.length===1&&(writeFailures[0].error?.payloadTag??writeFailures[0].error?.tag)==='closed';
 const handledOrder=['output-write-failed','known-output-closed-handling-enter','response-reader-cancel-invocation-attempt',
  'producer-cancel-enter','producer-cancel-returned','response-reader-cancel-returned',
  'response-reader-lock-release-returned','adapter-finally-returned','known-output-closed-handled-return'];
 const orderObserved=handledOrder.every((name,i)=>one(name)&&(i===0||phase(handledOrder[i-1])[0].sequence<phase(name)[0].sequence));
 const child=phase('dispose-returned').find(e=>e.resource==='output-stream'),parent=phase('dispose-returned').find(e=>e.resource==='outgoing-body-unfinished'),incoming=phase('dispose-returned').find(e=>e.resource==='incoming-request');
 const dropOrder=Boolean(child&&parent&&incoming&&phase('response-reader-lock-release-returned')[0]?.sequence<child.sequence&&
  child.sequence<parent.sequence&&parent.sequence<incoming.sequence&&incoming.sequence<phase('adapter-finally-returned')[0]?.sequence);
 const postFailureAbort=actualClosedWrite&&phase('io-abort-invocation-attempt').some(attempt=>attempt.sequence>writeFailures[0].sequence&&
  attempt.sequence<phase('known-output-closed-handling-enter')[0]?.sequence&&aborts.some(done=>done.sequence>attempt.sequence&&done.sequence<phase('known-output-closed-handling-enter')[0]?.sequence));
 const handledPath=common&&actualClosedWrite&&writes.length===returns.length+1&&signalProof&&orderObserved&&dropOrder&&postFailureAbort&&
  one('known-output-closed-handling-enter')&&one('known-output-closed-handled-return')&&
  one('response-reader-cancel-invocation-attempt')&&one('response-reader-cancel-returned')&&
  one('producer-cancel-enter')&&one('producer-cancel-returned')&&one('response-reader-lock-release-returned')&&
  phase('producer-pull-enter').length===phase('producer-pull-finally').length&&phase('producer-pull-finally').every(e=>e.sequence<phase('known-output-closed-handled-return')[0]?.sequence)&&
  phase('outgoing-finish-invocation-attempt').length===0&&phase('outgoing-finish-returned').length===0&&
  dropped('output-stream')===1&&dropped('outgoing-body-unfinished')===1&&dropped('incoming-request')===1&&
  phase('dispose-returned').every(e=>!['unconsumed-outparam','untransferred-response'].includes(e.resource));
 const result={identityObserved:identity,eventCount:own.length,ownEvents:own,fatalAdapterEvents:fatalEvents,
  adapterFailureObserved:phase('adapter-failed').length>0,adapterFinallyObserved:one('adapter-finally-returned'),
  knownNormalHandlerPath:normalPath,knownHandledOutputClosedPath:handledPath,knownFailedHostTerminal:false,
  handledCloseRequiredOrderObserved:orderObserved,childBeforeParentDropOrderObserved:dropOrder,
  hostReadEnteredOrBlockedProved:false,afterReturnNativeCleanupProved:false,
  signalPolicyObserved:signalProof,freshHealthySignalObserved:freshSignal,
  signalObservations:phase('handler-enter').map(e=>({signalAborted:e.signalAborted,requestSignalPolicy:e.requestSignalPolicy,
   independentPeerDisconnectSignal:e.independentPeerDisconnectSignal})),
  typedReadTerminals:readTerminals,writeFailures:writeFailures.map(e=>e.error),
  readerCancelReturned:one('response-reader-cancel-returned'),producerCancelReturned:one('producer-cancel-returned')};
 let body;if(record.decodedBodyBase64!==undefined)body=Buffer.from(record.decodedBodyBase64,'base64');
 if(kind==='healthy-upload') {
  let value;try{value=JSON.parse(body?.toString('utf8'));}catch{}
  result.functionChecksPassed=normalPath&&freshSignal&&record.status===200&&value?.complete===true&&value.received===8192&&
   value.ordinal===ordinal&&value.readFailure===null&&value.signalAborted===false&&value.requestSignalPolicy==='observed-io-only'&&value.independentPeerDisconnectSignal===false;
 } else if(kind==='healthy-output') {
  result.functionChecksPassed=normalPath&&freshSignal&&record.status===200&&body?.length===32768&&
   Array.from({length:8},(_,n)=>body.subarray(n*4096,(n+1)*4096).every(x=>x===65+n)).every(Boolean)&&one('producer-close-returned');
 } else if(kind==='inspect') {
  let value;try{value=JSON.parse(body?.toString('utf8'));}catch{}
  const inspection=value?.inspection;
  result.functionChecksPassed=normalPath&&freshSignal&&record.status===200&&value?.marker===marker&&
   inspection?.firstLabel===firstLabel&&inspection.lastOrdinal===ordinal&&Array.isArray(inspection.requests);
  result.inspection=inspection??null;result.afterReturnJsHistoryObserved=result.functionChecksPassed;
 } else if(kind==='upload-close') {
  const milestone=record.synchronizedMilestone;
  const barrier=milestone?.phase==='input-read-invocation-attempt'&&milestone.inputBytes>=1024&&
   milestone.label===record.label&&milestone.hostReadEnteredOrBlockedProved===false&&own.some(e=>
    e.phase===milestone.phase&&e.sequence===milestone.sequence&&e.inputBytes===milestone.inputBytes);
  const failed=readTerminals.some(e=>e.tag==='last-operation-failed'),eof=readTerminals.some(e=>e.tag==='closed');
  const catcher=phase('handler-read-failed').some(e=>e.received===1024&&e.signalAborted===true&&e.signalReasonMatchesReadError===true);
  const bodyFinally=phase('handler-body-finally').some(e=>e.received===1024&&e.signalAborted===true);
  result.coverage={readAttemptBarrierObserved:barrier,inputIoFailureObserved:failed,inputClosedObserved:eof,
   handlerCatchSignalAndReasonObserved:catcher,handlerBodyFinallyAbortedObserved:bodyFinally,
   applicationReaderCancelRejectionsRetained:phase('handler-reader-cancel-failed-suppressed'),
   httpBodyCompletionProved:false,independentPeerDisconnectSignal:false};
  result.ioPathObserved=identity&&barrier&&failed&&catcher&&bodyFinally&&signalProof;
  result.coverageStatus=result.ioPathObserved?'observed-input-failure-and-io-abort-within-export':
   eof?'inconclusive-closed-under-length-no-http-completion-proof':'inconclusive-input-io-or-abort-path';
 } else if(kind==='output-close') {
  result.outputWasiStreamErrorObserved=actualClosedWrite;
  result.ioPathObserved=identity&&record.firstBodyBeforeClose===true&&handledPath;
  result.coverageStatus=result.ioPathObserved?'observed-specific-output-closed-abort-cleanup-and-normal-return':
   'inconclusive-output-error-abort-cancel-cleanup-or-return-path';
 } else throw new Error('Unknown peer case kind');
 const caseGate=kind==='upload-close'?result.ioPathObserved===true:
  kind==='output-close'?record.firstBodyBeforeClose===true&&(handledPath||freshSignal):result.functionChecksPassed===true;
 result.safeToRequestAgain=(normalPath||handledPath)&&caseGate&&record.clientCloseObserved===true&&
  !record.transportOrCollectionError&&!record.frameDecodeError&&!record.forcedClientCleanup;
 if(!identity)result.inconclusiveReason='missing-or-changed-js-factory-identity';
 else if(fatalEvents.length)result.inconclusiveReason='adapter-or-abort-cancel-dispose-failure';
 else if(!result.safeToRequestAgain)result.inconclusiveReason='strict-normal-or-handled-export-path-not-established';
 return result;
}
