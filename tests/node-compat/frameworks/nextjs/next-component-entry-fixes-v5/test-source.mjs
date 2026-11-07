// Source/function-text/inert DATA tests only; no real resource/Request/stream/IO.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('./adapter.mjs',import.meta.url),'utf8');
const begin=source.indexOf('async function handleResources(incoming,outparam){'),end=source.indexOf('\n  }\n  return{handle',begin);
assert(begin>=0&&end>begin);const functionText=source.slice(begin,end+4);
const extract=name=>{const a=source.indexOf('function '+name+'('),b=source.indexOf('\n}',a);assert(a>=0&&b>a);return source.slice(a,b+2);};
const gates=new Function(extract('isObservedClosedOutput')+'\n'+extract('mayReturnHandledClosed')+'\nreturn {isObservedClosedOutput,mayReturnHandledClosed};')();
let checks=0;
const raw={payload:{tag:'closed'}},other={payload:{tag:'closed'}},valid={observed:true,raw,caught:raw,tag:'closed',responseSet:true};
assert.equal(gates.isObservedClosedOutput(valid),true);checks++;
for(const delta of [{observed:false},{raw:other},{caught:other},{tag:'last-operation-failed'},{tag:undefined},{responseSet:false}]){
 assert.equal(gates.isObservedClosedOutput({...valid,...delta}),false);checks++;
}
const complete={classified:true,cancelReturned:true,readerReleased:true,cleanupReturned:true,requestAborted:true,fatalSet:false};
assert.equal(gates.mayReturnHandledClosed(complete),true);checks++;
for(const key of ['classified','cancelReturned','readerReleased','cleanupReturned','requestAborted']){
 assert.equal(gates.mayReturnHandledClosed({...complete,[key]:false}),false);checks++;
}
assert.equal(gates.mayReturnHandledClosed({...complete,fatalSet:true}),false);checks++;
const incoming=Symbol('incoming-data'),outparam=Symbol('outparam-data');
for(const marker of [undefined,null,false,0,'',NaN,Symbol('marker'),{marker:true}]){
 for(const cleanupFails of [false,true]){
  const drops=[];const cleanupMarker=Symbol('cleanup-data');
  const drop=value=>{if(value!==undefined){drops.push(value===outparam?'outparam':value===incoming?'incoming':'unknown');if(cleanupFails&&value===outparam)throw cleanupMarker;}};
  function inertAllocation(){throw marker;}
  const make=new Function('drop','AbortController','streamError','streamFailure','isObservedClosedOutput','mayReturnHandledClosed','return ('+functionText+');');
  const fn=make(drop,inertAllocation,()=>undefined,()=>{throw new Error('Unknown primary must not be normalized');},gates.isObservedClosedOutput,gates.mayReturnHandledClosed);
  let caught,caughtSet=false;try{await fn(incoming,outparam);}catch(error){caughtSet=true;caught=error;}
  assert(caughtSet);assert(Object.is(caught,marker));assert.deepEqual(drops,['outparam','incoming']);checks++;
 }
}
// Existing ClassicBody initView forwards signal with the original receiver.
// Only plain dictionary DATA/its unchanged Proxy is exercised, not a Request.
const v4=readFileSync(new URL('../next-component-entry-fixes-v4/guest-entry.mjs',import.meta.url),'utf8');
const a=v4.indexOf('  function initView(init) {'),b=v4.indexOf('  const Request = new Proxy',a);assert(a>=0&&b>a);
const initView=new Function('get','return ('+v4.slice(a,b).trim()+');')(Reflect.get);
let receiver;const signal=Symbol('signal-data');const init=Object.freeze({get body(){return undefined;},get signal(){receiver=this;return signal;}});
const view=initView(init);assert.equal(view.value.body,undefined);assert.equal(view.value.signal,signal);assert.equal(receiver,init);checks++;
for(const marker of [false,undefined]){
 const dictionary={get signal(){throw marker;}};const v=initView(dictionary);let caught,caughtSet=false;
 try{void v.value.signal;}catch(error){caughtSet=true;caught=error;}assert(caughtSet);assert.equal(caught,marker);checks++;
}
console.log(JSON.stringify({schemaVersion:1,sourceOnly:true,inertDataChecks:checks,actualFunctionTextUsed:true,
 unknownAndFalsyPrimaryRetainedAcrossCleanup:true,allocationGuardCleanupCallbacks:['outparam','incoming'],
 unchangedClassicBodySignalForwardingChecked:true,actualResourceOrRequestOrAbortControllerOrStreamOrHostOrGuestInvoked:false}));
