// UNAPPLIED: the argument is a finite private record of installed dependencies.
import {createClassicCore} from './classic-core.generated.mjs';
export function createClassicStreams(dependencies) {
 'use strict';
 const Define=Object.defineProperty,OwnKeys=Reflect.ownKeys,Apply=Reflect.apply,ErrorCtor=Error,IsArray=Array.isArray,Slice=Array.prototype.slice;
 const profile='sm-node-22.14.0-m0.12';
 function unsupported(operation){const error=new ErrorCtor('node:stream.'+operation+' is unavailable in '+profile);
  Define(error,'code',{__proto__:null,value:'ERR_SM_NODE_UNSUPPORTED',writable:true,enumerable:true,configurable:true});
  Define(error,'module',{__proto__:null,value:'node:stream',writable:true,enumerable:true,configurable:true});
  Define(error,'operation',{__proto__:null,value:operation,writable:true,enumerable:true,configurable:true});
  Define(error,'profile',{__proto__:null,value:profile,writable:true,enumerable:true,configurable:true});
  throw error;
 }
 function deferred(operation){return function unavailableOperation(){unsupported(operation)}}
 const {Stream,promises:promiseFunctions}=createClassicCore(dependencies);
 function isWebLike(value){return value!==null&&typeof value==='object'&&!(value instanceof Stream)&&('getReader'in value||'getWriter'in value||'pipeThrough'in value);}
 function classicOnly(value,operation){if(isWebLike(value))unsupported(operation+'(Web stream)');}
 function pipelineArguments(args,promise){
  const last=args[args.length-1];
  const stages=IsArray(args[0])?args[0]:Apply(Slice,args,[0,promise&&last&&typeof last==='object'&&!(last instanceof Stream)&&!isWebLike(last)?-1:promise?args.length:-1]);
  for(const value of stages){classicOnly(value,'pipeline');if(typeof value==='function')unsupported('pipeline(function stage)');}
 }
 const callbackPipeline=Stream.pipeline,callbackFinished=Stream.finished,addAbortSignal=Stream.addAbortSignal;
 function pipeline(...args){pipelineArguments(args,false);return Apply(callbackPipeline,this,args);}
 function finished(stream,...args){classicOnly(stream,'finished');return Apply(callbackFinished,this,[stream,...args]);}
 function promisePipeline(...args){pipelineArguments(args,true);return Apply(promiseFunctions.pipeline,this,args);}
 function promiseFinished(stream,...args){classicOnly(stream,'finished');return Apply(promiseFunctions.finished,this,[stream,...args]);}
 for(const [fn,name,length]of[[finished,'eos',3],[promisePipeline,'pipeline',0],[promiseFinished,'finished',2]]){
  Define(fn,'name',{__proto__:null,value:name,configurable:true});Define(fn,'length',{__proto__:null,value:length,configurable:true});}
 Stream.pipeline=pipeline;Stream.finished=finished;
 Stream.addAbortSignal=function addAbortSignalBounded(signal,stream){classicOnly(stream,'addAbortSignal');return Apply(addAbortSignal,this,[signal,stream]);};
 Define(Stream.addAbortSignal,'name',{__proto__:null,value:'addAbortSignal',configurable:true});
 for(const name of['fromWeb','toWeb'])for(const constructor of['Readable','Writable','Duplex'])
  Define(Stream[constructor],name,{__proto__:null,value:deferred(constructor+'.'+name),writable:true,configurable:true,enumerable:true});
 Define(Stream.Duplex,'from',{__proto__:null,value:deferred('Duplex.from'),writable:true,configurable:true,enumerable:true});
 for(const name of['compose','map','filter','forEach','toArray','some','find','every','flatMap','drop','take','reduce','iterator'])
  Define(Stream.Readable.prototype,name,{__proto__:null,value:deferred('Readable.prototype.'+name),writable:true,configurable:true,enumerable:false});
 delete Stream.Readable.prototype.asIndexedPairs; // Not a Node22 member.
 for(const constructor of['Readable','Writable'])Define(Stream[constructor].prototype,dependencies.asyncDisposeSymbol,
  {__proto__:null,value:deferred(constructor+'.prototype[Symbol.asyncDispose]'),writable:true,configurable:true,enumerable:false});
 Stream.compose=deferred('compose');Stream.duplexPair=deferred('duplexPair');
 const promises={finished:promiseFinished,pipeline:promisePipeline};
 const custom=Symbol.for('nodejs.util.promisify.custom');
 for(const [fn,promise]of[[pipeline,promisePipeline],[finished,promiseFinished]])Define(fn,custom,{__proto__:null,get(){return promise},enumerable:true,configurable:false});
 const promiseRecord={default:promises,finished:promises.finished,pipeline:promises.pipeline};
 // Real root default remains callable and mutable, with the same constructors.
 Define(Stream,'promises',{__proto__:null,get(){return promises},configurable:true,enumerable:true});
 const root={Duplex:Stream.Duplex,PassThrough:Stream.PassThrough,Readable:Stream.Readable,Stream,Transform:Stream.Transform,Writable:Stream.Writable,
  _isArrayBufferView:Stream._isArrayBufferView,_isUint8Array:Stream._isUint8Array,_uint8ArrayToBuffer:Stream._uint8ArrayToBuffer,
  addAbortSignal:Stream.addAbortSignal,compose:Stream.compose,default:Stream,destroy:Stream.destroy,duplexPair:Stream.duplexPair,
  finished:Stream.finished,getDefaultHighWaterMark:Stream.getDefaultHighWaterMark,isDestroyed:Stream.isDestroyed,isDisturbed:Stream.isDisturbed,
  isErrored:Stream.isErrored,isReadable:Stream.isReadable,isWritable:Stream.isWritable,pipeline:Stream.pipeline,promises,
  setDefaultHighWaterMark:Stream.setDefaultHighWaterMark};
 if(OwnKeys(root).includes('then')||OwnKeys(promiseRecord).includes('then'))throw new ErrorCtor('Invalid finite classic namespace');
 return {root,promises:promiseRecord};
}
