// Actual exported parser+classifier regression on synthetic log DATA only.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import * as previous from '../peer-disconnect-wasmtime-collector-v2/classification.mjs';
import * as current from './classification.mjs';
const plan=JSON.parse(readFileSync(new URL('./plan.json',import.meta.url),'utf8'));
const label='review-data-only',firstLabel='review-first',ordinal=3;
const event=(phase,fields={})=>({schemaVersion:1,marker:current.marker,origin:'actual-wasi-guest',
 sequence:0,firstLabel,ordinal,label,route:'/output',phase,context:null,...fields});
function normal(aborted,writes=1) {
 const events=[event('adapter-enter',{requestSignalLinkedToPeer:true,independentPeerDisconnectSignal:false,adapterPolicy:'observed-io-abort-specific-output-closed-v2'}),
  event('request-signal-created',{aborted,alreadyAbortedBeforeListener:aborted,reasonMatchesObservedIo:aborted}),
  event('handler-enter',{signalAborted:aborted,requestSignalLinkedToPeer:true,requestSignalPolicy:'observed-io-only',independentPeerDisconnectSignal:false}),
  event('handler-finally')];
 for(let i=0;i<writes;i++)events.push(event('output-write-invocation-attempt',{bytes:4096}),event('output-write-returned'));
 events.push(event('outgoing-finish-returned'),event('response-reader-lock-release-returned'),event('adapter-finally-returned'));
 return events.map((e,i)=>({...e,sequence:i+1}));
}
const record={label,status:200,clientCloseObserved:true,forcedClientCleanup:false,firstBodyBeforeClose:true};
function inspect(module,events){
 const text=events.map(e=>JSON.stringify(e)).join('\n')+'\n';
 const parsed=module.parseDiagnosticLog(text,plan.allowedGuestPhases);
 return module.analyze(record,parsed.events,{firstLabel,ordinal,kind:'output-close'});
}
const unknown=normal(true),old=inspect(previous,unknown),fixed=inspect(current,unknown);
assert.equal(old.knownNormalHandlerPath,true);assert.equal(old.freshHealthySignalObserved,false);
assert.equal(old.signalPolicyObserved,false);assert.equal(old.knownHandledOutputClosedPath,false);
assert.equal(old.ioPathObserved,false);assert.equal(old.safeToRequestAgain,true);
assert.equal(fixed.knownNormalHandlerPath,true);assert.equal(fixed.safeToRequestAgain,false);
const queued=inspect(current,normal(false,8));
assert.equal(queued.freshHealthySignalObserved,true);assert.equal(queued.knownNormalHandlerPath,true);
assert.equal(queued.safeToRequestAgain,true);assert.equal(queued.ioPathObserved,false);
assert(queued.coverageStatus.startsWith('inconclusive-'));
console.log(JSON.stringify({schemaVersion:1,sourceOnly:true,actualExportedParserAndAnalyzeUsed:true,
 syntheticLogDataOnly:true,oldUnexpectedPreabortedNormalSafe:true,newUnexpectedPreabortedNormalSafe:false,
 queuedAllEightFreshNormalSafe:true,queuedAllEightIoCoverage:false,
 actualActorsOrAbortControllerResourcesTimersOrNetworkInvoked:false}));
