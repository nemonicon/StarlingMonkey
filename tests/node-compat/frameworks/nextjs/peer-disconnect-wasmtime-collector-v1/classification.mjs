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
    if(value.phase==='handler-enter'){assert.equal(typeof value.signalAborted,'boolean');assert.equal(value.requestSignalLinkedToPeer,false);}
    if(value.phase==='input-read-invocation-attempt'){
      assert(Number.isSafeInteger(value.inputBytes)&&value.inputBytes>=0&&value.inputBytes<=8192);
      assert.equal(value.hostReadEnteredOrBlockedProved,false);
    }
    if(value.phase==='input-read-returned'){assert(Number.isSafeInteger(value.bytes)&&value.bytes>=0);assert(Number.isSafeInteger(value.inputBytes)&&value.inputBytes>=0);}
    if(value.phase==='output-write-invocation-attempt')assert(Number.isSafeInteger(value.bytes)&&value.bytes>=1&&value.bytes<=4096);
    if(value.phase==='dispose-returned'||value.phase==='dispose-invocation-attempt'||value.phase==='dispose-failed')assert.equal(typeof value.resource,'string');
    events.push(value);
  }
  return{events,hostLines,incompleteTail:incomplete??''};
}
export function analyze(record,events,{firstLabel,ordinal,kind}) {
  const own=events.filter(e=>e.label===record.label),phase=p=>own.filter(e=>e.phase===p);
  assert(own.length<=192);
  const identity=own.length>0&&own.every(e=>e.firstLabel===firstLabel&&e.ordinal===ordinal);
  const outputFailures=phase('output-write-failed'),readFailures=phase('input-read-failed');
  const exactOne=p=>phase(p).length===1;
  const normalPath=identity&&exactOne('adapter-enter')&&exactOne('handler-enter')&&
    exactOne('handler-finally')&&exactOne('outgoing-finish-returned')&&exactOne('adapter-finally-returned')&&
    phase('adapter-failed').length===0&&outputFailures.length===0&&phase('dispose-failed').length===0&&
    phase('output-write-invocation-attempt').length>0&&phase('output-write-invocation-attempt').length===phase('output-write-returned').length;
  const typedReadTerminals=readFailures.map(e=>({tag:e.error?.payloadTag??e.error?.tag??null,error:e.error}));
  const result={identityObserved:identity,eventCount:own.length,ownEvents:own,
    adapterFailureObserved:phase('adapter-failed').length>0,adapterFinallyObserved:exactOne('adapter-finally-returned'),
    knownNormalHandlerPath:normalPath,knownFailedHostTerminal:false,
    hostReadEnteredOrBlockedProved:false,afterReturnNativeCleanupProved:false,
    signalObservations:phase('handler-enter').map(e=>({signalAborted:e.signalAborted,requestSignalLinkedToPeer:e.requestSignalLinkedToPeer})),
    typedReadTerminals,writeFailures:outputFailures.map(e=>e.error),
    readerCancelReturned:phase('response-reader-cancel-returned').length>0,
    producerCancelReturned:phase('producer-cancel-returned').length>0};
  let body;
  if(record.decodedBodyBase64!==undefined)body=Buffer.from(record.decodedBodyBase64,'base64');
  if(kind==='healthy-upload') {
    let value;try{value=JSON.parse(body?.toString('utf8'));}catch{}
    result.functionChecksPassed=normalPath&&record.status===200&&value?.complete===true&&value?.received===8192&&
      value?.ordinal===ordinal&&value?.readFailure===null&&value?.signalAborted===false;
  } else if(kind==='healthy-output') {
    result.functionChecksPassed=normalPath&&record.status===200&&body?.length===32768&&
      Array.from({length:8},(_,n)=>body.subarray(n*4096,(n+1)*4096).every(x=>x===65+n)).every(Boolean)&&
      exactOne('producer-close-returned');
  } else if(kind==='inspect') {
    let value;try{value=JSON.parse(body?.toString('utf8'));}catch{}
    const inspection=value?.inspection;
    result.functionChecksPassed=normalPath&&record.status===200&&value?.marker===marker&&
      inspection?.firstLabel===firstLabel&&inspection?.lastOrdinal===ordinal&&Array.isArray(inspection?.requests);
    result.inspection=inspection??null;
    result.afterReturnJsHistoryObserved=result.functionChecksPassed;
  } else if(kind==='upload-close') {
    const milestone=record.synchronizedMilestone;
    const synchronized=milestone?.phase==='input-read-invocation-attempt'&&milestone.inputBytes>=1024&&
      milestone.label===record.label&&milestone.hostReadEnteredOrBlockedProved===false;
    const failed=typedReadTerminals.some(e=>e.tag==='last-operation-failed');
    const eof=typedReadTerminals.some(e=>e.tag==='closed');
    result.coverage={readAttemptBarrierObserved:synchronized,inputIoFailureObserved:failed,inputClosedObserved:eof,
      handlerCatchObserved:phase('handler-read-failed').length>0,
      handlerBodyFinallyObserved:phase('handler-body-finally').length>0,
      httpBodyCompletionProved:false,peerLinkedRequestSignalImplemented:false};
    result.ioPathObserved=identity&&synchronized&&failed&&result.coverage.handlerCatchObserved&&result.coverage.handlerBodyFinallyObserved;
    result.coverageStatus=result.ioPathObserved?'observed-input-io-failure-within-export':
      eof?'inconclusive-closed-under-length-no-http-completion-proof':'inconclusive-read-path';
  } else if(kind==='output-close') {
    result.outputWasiStreamErrorObserved=outputFailures.some(e=>['closed','last-operation-failed'].includes(e.error?.payloadTag??e.error?.tag));
    result.ioPathObserved=identity&&record.firstBodyBeforeClose===true&&result.outputWasiStreamErrorObserved&&
      result.readerCancelReturned&&result.producerCancelReturned;
    result.coverageStatus=result.ioPathObserved?'observed-output-failure-and-cancel-within-export':
      'inconclusive-no-complete-write-failure-cancel-path';
  } else throw new Error('Unknown peer case kind');
  // A finally marker on a rethrow path never authorizes another export.
  result.safeToRequestAgain=normalPath&&record.clientCloseObserved===true&&!record.transportOrCollectionError&&
    !record.frameDecodeError&&!record.forcedClientCleanup;
  if(!identity)result.inconclusiveReason='missing-or-changed-js-factory-identity';
  else if(!result.safeToRequestAgain)result.inconclusiveReason=result.adapterFailureObserved?
    'failed-export-outcome-unknown-discard-required':'normal-handler-completion-not-established';
  return result;
}
