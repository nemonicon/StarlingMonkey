// Inert Promise/object DATA only. No browser, server, timers, network or handles.
import assert from 'node:assert/strict';
import {createNetworkObserver} from './observer-core.mjs';
let checks=0;
function setup(limits={maxEvents:10,maxEventBytes:4096,maxPayloadBytes:8192}){
 const rows=[],errors=[];let clock=0;
 const observer=createNetworkObserver({now:()=>String(++clock),onCdp:x=>rows.push(x),onLimit:(error,detail)=>errors.push({error,detail}),limits});
 return {observer,rows,errors};
}
function deferred(){let resolve,reject;const promise=new Promise((r,j)=>{resolve=r;reject=j;});return{promise,resolve,reject};}
const data={requestId:1,url:'http://inert.invalid/actions',method:'POST'};
{
 const {observer}=setup(),request={};
 const value=await observer.raceFailure(request,data,()=>Promise.resolve(null));
 assert.equal(value.kind,'fulfilled');assert.equal(observer.requireValue(value),null);checks++;
}
for(const marker of [new Error('original body'),0,false,null,undefined]){
 const {observer}=setup();const result=await observer.raceFailure({},data,()=>{throw marker;});
 assert.equal(result.kind,'rejected');let caught,caughtSet=false;
 try{observer.requireValue(result);}catch(error){caughtSet=true;caught=error;}
 assert(caughtSet);assert(Object.is(caught,marker));checks++;
}
for(const early of [false,true]){
 const {observer}=setup(),request={},underlying=deferred();
 const failure={errorText:'net::ERR_ABORTED'};
 if(early)observer.requestFailed(request,data,failure);
 const pending=observer.raceFailure(request,data,()=>underlying.promise);
 if(!early)observer.requestFailed(request,data,failure);
 const value=await pending;
 assert.equal(value.kind,'requestfailed');assert.equal(value.terminal.requestId,1);assert.equal(value.terminal.failure,failure);
 assert.equal(value.underlyingPromiseHandled,true);
 assert.throws(()=>observer.requireValue(value),error=>error.code==='ERR_BROWSER_REQUEST_FAILED'&&error.requestFailedTerminal===value.terminal);
 // The later target-close rejection has a settlement handler already attached.
 underlying.reject(new Error('Target closed SECONDARY'));await Promise.resolve();await Promise.resolve();checks++;
}
{
 const {observer}=setup(),one={},two={},second=deferred();let secondSettled=false;
 const pending=observer.raceFailure(two,{...data,requestId:2},()=>second.promise).then(x=>{secondSettled=true;return x;});
 observer.requestFailed(one,data,{errorText:'first failed'});await Promise.resolve();await Promise.resolve();assert.equal(secondSettled,false);
 second.resolve('second body');assert.equal(observer.requireValue(await pending),'second body');checks++;
 assert.throws(()=>observer.noteRequest(two,{...data,requestId:3}),/identity changed/);checks++;
}
{
 const {observer,rows,errors}=setup();
 const payload={requestId:'CDP.123',timestamp:123.456,errorText:'net::ERR_ABORTED',canceled:true,blockedReason:'other',unknownFutureField:{falseValue:false,zero:0,empty:null}};
 observer.cdp('Network.loadingFailed',payload,{test:'server-action',phase:'before-close'});
 assert.deepEqual(rows[0].payload,payload);assert.equal(rows[0].arrivalNs,'1');assert.equal(rows[0].payload.requestId,'CDP.123');
 payload.unknownFutureField.zero=9;assert.equal(rows[0].payload.unknownFutureField.zero,0);assert.deepEqual(errors,[]);checks++;
}
{
 const {observer,rows,errors}=setup({maxEvents:2,maxEventBytes:4096,maxPayloadBytes:8192});
 observer.cdp('Network.dataReceived',{requestId:'id',timestamp:1},{});observer.cdp('Network.loadingFinished',{requestId:'id',timestamp:2},{});
 observer.cdp('Network.loadingFailed',{requestId:'id',errorText:'oversized count'},{});
 observer.cdp('Page.frameNavigated',{frame:{id:'late'}},{});
 assert.equal(rows.length,2);assert.equal(errors.length,1);assert.equal(errors[0].error.code,'ERR_BROWSER_CDP_OBSERVER_LIMIT');
 assert.equal(observer.stats.stopped,true);assert.equal(observer.stats.eventsAfterStop,1);assert.equal(observer.stats.overflow.reason,'bounded-cdp-limit');checks++;
}
for(const kind of ['per-event','total','serialization']){
 const {observer,rows,errors}=setup({maxEvents:10,maxEventBytes:kind==='per-event'?4:4096,maxPayloadBytes:kind==='total'?4:8192});
 const payload={requestId:'record',unknown:'not silently ignored'};if(kind==='serialization')payload.circular=payload;
 observer.cdp('Network.requestWillBeSent',payload,{});assert.equal(rows.length,0);assert.equal(errors.length,1);assert.equal(observer.stats.stopped,true);checks++;
}
for(const key of ['maxEvents','maxEventBytes','maxPayloadBytes']){
 assert.throws(()=>setup({maxEvents:10,maxEventBytes:10,maxPayloadBytes:10,[key]:0}),/Finite observer limit/);checks++;
}
console.log(JSON.stringify({sourceOnly:true,inertObserverChecks:checks,failedBeforeResponseAndAfterWait:true,
 originalBodyErrorsAndFalsyValuesPreserved:true,distinctRequestObjectsNeverMerged:true,
 underlyingRejectionsHandled:true,fullUnknownCdpFieldsRetained:true,limitsFailStop:true,
 browserOrServerOrNetworkOrTimerOrResourceInvoked:false}));
