'use strict'
const inspection=require("lib/ours/util/inspect.js")
const Primordials=require("lib/ours/primordials.js")
const custom=NativeSymbol.for('nodejs.util.promisify.custom')
function once(callback){let called=false;return function(...args){if(called)return;called=true;return Apply(callback,this,args)}}
function createDeferredPromise(){let resolve,reject;const promise=new PromiseCtor((a,b)=>{resolve=a;reject=b});return{promise,resolve,reject}}
function promisify(fn){return new PromiseCtor((resolve,reject)=>fn((error,...args)=>error?reject(error):resolve(args[0])))}
own(promisify,'custom',custom)
const abortAny=AbortSignal.any
module.exports={AggregateError:AggregateErrorCtor,kEmptyObject:NativeObject.freeze({}),once,createDeferredPromise,promisify,
 debuglog(){return function(){}},format:inspection.format,inspect:inspection.inspect,
 types:{isAsyncFunction(fn){return typeof fn==='function'&&Apply(NativeObject.prototype.toString,fn,[])==='[object AsyncFunction]'},isArrayBufferView},
 isBlob(){return false},deprecate(fn){return fn},addAbortListener:events.addAbortListener,
 AbortSignalAny(signals){return Apply(abortAny,AbortSignal,[signals])}}
