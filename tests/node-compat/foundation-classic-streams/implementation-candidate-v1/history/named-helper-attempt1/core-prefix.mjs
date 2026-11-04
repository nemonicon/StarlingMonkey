// UNAPPLIED pure guest JS state machines. No public runtime require/process API.
export function createClassicCore(dependencies) {
'use strict';
const {Object,Array,Error,TypeError,RangeError,AggregateError,Promise,String,Number,Boolean,Symbol,Set,Uint8Array,ArrayBuffer,DataView,Function,RegExp,Math,Reflect}=globalThis;
const {Buffer,events,StringDecoder,nextTick,AbortSignal,AbortController,disposeSymbol,asyncDisposeSymbol}=dependencies;
const Apply=Reflect.apply,Define=Object.defineProperty,GetDescriptor=Object.getOwnPropertyDescriptor;
const ErrorCtor=Error,TypeErrorCtor=TypeError,RangeErrorCtor=RangeError;
const PromiseCtor=Promise,AggregateErrorCtor=AggregateError;
const NativeArray=Array,NativeObject=Object,NativeString=String,NativeNumber=Number,NativeBoolean=Boolean;
const NativeSymbol=Symbol,NativeSet=Set,NativeUint8Array=Uint8Array;
const arrayBufferIsView=ArrayBuffer.isView;
const typed=Object.getPrototypeOf(Uint8Array.prototype);
const typedName=GetDescriptor(typed,Symbol.toStringTag).get;
const typedBuffer=GetDescriptor(typed,'buffer').get,typedOffset=GetDescriptor(typed,'byteOffset').get,typedLength=GetDescriptor(typed,'byteLength').get;
const dataBuffer=GetDescriptor(DataView.prototype,'buffer').get,dataOffset=GetDescriptor(DataView.prototype,'byteOffset').get,dataLength=GetDescriptor(DataView.prototype,'byteLength').get;
const bufferFrom=Buffer.from,bufferAlloc=Buffer.alloc,bufferAllocUnsafe=Buffer.allocUnsafe,bufferIsEncoding=Buffer.isEncoding;
const own=(object,key,value)=>Define(object,key,{__proto__:null,value,writable:true,enumerable:true,configurable:true});
const MAX_QUEUED_UNITS=16*1024*1024,MAX_QUEUED_CHUNKS=4096;
if(typeof nextTick!=='function'||typeof Buffer!=='function'||typeof events.EventEmitter!=='function'||typeof StringDecoder!=='function'||typeof events.addAbortListener!=='function'||typeof disposeSymbol!=='symbol'||typeof asyncDisposeSymbol!=='symbol')throw new TypeErrorCtor('Missing captured classic-stream prerequisites');
function profileFailure(code,operation,message){const error=new RangeErrorCtor(message);own(error,'code',code);own(error,'module','node:stream');own(error,'operation',operation);own(error,'profile','sm-node-22.14.0-m0.12');return error;}
function checkQueueLimit(state,chunk,count,operation){
 const length=state.objectMode?1:chunk.length;
 if(count>=MAX_QUEUED_CHUNKS||state.length+length>(state.objectMode?MAX_QUEUED_CHUNKS:MAX_QUEUED_UNITS))
  throw profileFailure('ERR_SM_NODE_STREAM_LIMIT',operation,'Bounded queued stream units/chunks exceeded; discard this stream');
}
function isArrayBufferView(value){return arrayBufferIsView(value);}
function isUint8Array(value){try{return Apply(typedName,value,[])==='Uint8Array';}catch{return false;}}
function byteViewToBuffer(value){
 let buffer,offset,length;
 try{buffer=Apply(typedBuffer,value,[]);offset=Apply(typedOffset,value,[]);length=Apply(typedLength,value,[]);}
 catch{buffer=Apply(dataBuffer,value,[]);offset=Apply(dataOffset,value,[]);length=Apply(dataLength,value,[]);}
 // The installed Buffer validates fixed/attached/unshared backing and bounds.
 return Apply(bufferFrom,Buffer,[buffer,offset,length]);
}
