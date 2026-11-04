// ISOLATED ordinary-view adapter. nativeRead MUST be captured from the real
// native BYOB prototype before installing the frozen base simulation.
// No call delegates a DataView to the known unsupported native branch.
export function installDataViewBYOB(record,nativeRead){
  const Reader=record.ReadableStreamBYOBReader,brand=record.isReadableStreamBYOBReader;
  const U8=Uint8Array,DV=DataView,TypeErrorCtor=TypeError,RangeErrorCtor=RangeError,ErrorCtor=Error;
  const apply=Reflect.apply,define=Object.defineProperty,descriptor=Object.getOwnPropertyDescriptor,getPrototype=Object.getPrototypeOf;
  const isView=ArrayBuffer.isView,isInteger=Number.isInteger;
  const call=(fn,self,args=[])=>apply(fn,self,args),getter=(prototype,key)=>descriptor(prototype,key).get;
  const typed=getPrototype(U8.prototype),typedBytes=getter(typed,'byteLength'),typedLength=getter(typed,'length');
  const typedBuffer=getter(typed,'buffer'),typedOffset=getter(typed,'byteOffset'),typedName=getter(typed,Symbol.toStringTag);
  const dataBytes=getter(DV.prototype,'byteLength'),dataBuffer=getter(DV.prototype,'buffer'),dataOffset=getter(DV.prototype,'byteOffset');
  const bufferBytes=getter(ArrayBuffer.prototype,'byteLength'),resizable=getter(ArrayBuffer.prototype,'resizable');
  const prototypes=new Set([Int8Array.prototype,U8.prototype,Uint8ClampedArray.prototype,Int16Array.prototype,Uint16Array.prototype,
    Int32Array.prototype,Uint32Array.prototype,Float32Array.prototype,Float64Array.prototype,BigInt64Array.prototype,BigUint64Array.prototype,DV.prototype]);
  const ordinary=prototypes.has.bind(prototypes);
  function coded(Ctor,code,message){const error=new Ctor(message);define(error,'code',{__proto__:null,value:code,writable:true,configurable:true,enumerable:true});throw error;}
  function unsupported(operation){coded(ErrorCtor,'ERR_SM_NODE_UNSUPPORTED',operation+' unavailable in isolated bounded BYOB adapter');}
  const previous=descriptor(Reader.prototype,'read');
  async function read(view,options=undefined){
    if(!brand(this))coded(TypeErrorCtor,'ERR_INVALID_THIS','Invalid BYOB reader');
    if(!isView(view))coded(TypeErrorCtor,'ERR_INVALID_ARG_TYPE','view must be an ArrayBufferView');
    if(options!==undefined&&options!==null&&typeof options!=='object'&&typeof options!=='function')
      coded(TypeErrorCtor,'ERR_INVALID_ARG_TYPE','options must be an object');
    if(!ordinary(getPrototype(view)))unsupported('subclass or cross-realm view');
    for(const key of ['buffer','byteOffset','byteLength','length','constructor'])if(descriptor(view,key))unsupported('modified view layout');
    const dataView=call(typedName,view)===undefined;
    const bytes=call(dataView?dataBytes:typedBytes,view),buffer=call(dataView?dataBuffer:typedBuffer,view);
    let backing;try{backing=call(bufferBytes,buffer);}catch{unsupported('shared view');}
    if(bytes===0||backing===0)coded(TypeErrorCtor,'ERR_INVALID_STATE','View or backing buffer empty or detached');
    const min=options?.min??1;
    if(typeof min!=='number')coded(TypeErrorCtor,'ERR_INVALID_ARG_TYPE','options.min must be a number');
    if(!isInteger(min)||min<=0)coded(TypeErrorCtor,'ERR_INVALID_ARG_VALUE','options.min must be a positive integer');
    const elements=dataView?bytes:call(typedLength,view);
    if(min>elements)coded(RangeErrorCtor,'ERR_OUT_OF_RANGE','options.min exceeds view length');
    if(bytes>16777216){const error=new RangeErrorCtor('byob-view-bytes');
      define(error,'code',{__proto__:null,value:'ERR_SM_NODE_LIMIT',writable:true,configurable:true,enumerable:true});
      define(error,'resource',{__proto__:null,value:'byob-view-bytes',writable:true,configurable:true,enumerable:true});throw error;}
    if(call(resizable,buffer))unsupported('resizable view');
    if(min>1)unsupported('minimum greater than one');
    if(!dataView)return call(nativeRead,this,[view]);
    // Get fresh offsets/length after the observable min getter. Construction
    // rejects any standard detachment performed by that getter, before entry.
    const alias=new U8(buffer,call(dataOffset,view),call(dataBytes,view));
    const result=await call(nativeRead,this,[alias]);
    if(result.value===undefined)return{value:undefined,done:result.done};
    const value=result.value;
    return{value:new DV(call(typedBuffer,value),call(typedOffset,value),call(typedBytes,value)),done:result.done};
  }
  define(Reader.prototype,'read',{...previous,value:read});
  return read;
}
