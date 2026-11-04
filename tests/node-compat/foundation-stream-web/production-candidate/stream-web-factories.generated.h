// Generated UNINSTALLED candidate; do not edit.
// Canonical-source SHA-256: 0d2044f75841e36bc2d5cf898ebe1eaa330f05ee407a51898619d30a49a64410
static constexpr const char kStreamWebFactorySource[] = R"SM_NODE_PROFILE((() => {
'use strict';
const createCodecModule=(() => {
// ISOLATED opt-in guest prototype. No production registration/global codecs.
// Encoder framing follows Node22 internal/webstreams/encoding.js (MIT), but
// bulk Unicode conversion remains in the captured native encoder.
const MAX_SOURCE_UNITS=1024*1024;
const MAX_INPUT_BYTES=16*1024*1024;
function createCodecModule(record){
  const ErrorCtor=Error,TypeErrorCtor=TypeError,RangeErrorCtor=RangeError,StringCtor=String;
  const apply=Reflect.apply,define=Object.defineProperty,defines=Object.defineProperties;
  const ownKeys=Reflect.ownKeys,descriptor=Object.getOwnPropertyDescriptor;
  const isView=ArrayBuffer.isView;
  const call=(fn,self,args=[])=>apply(fn,self,args);
  const keys=['ReadableStream','ReadableStreamDefaultReader','ReadableStreamBYOBReader','ReadableStreamBYOBRequest',
    'ReadableByteStreamController','ReadableStreamDefaultController','WritableStream','WritableStreamDefaultWriter',
    'WritableStreamDefaultController','ByteLengthQueuingStrategy','CountQueuingStrategy','TransformStream',
    'TransformStreamDefaultController','TextEncoder','TextDecoder','isReadableStreamBYOBReader'];
  function own(object,key,value){define(object,key,{__proto__:null,value,writable:true,enumerable:true,configurable:true});return object;}
  function fail(Ctor,code,message){const error=new Ctor(message);if(code!==undefined)own(error,'code',code);throw error;}
  function unsupported(operation){const error=new ErrorCtor('node:stream/web.'+operation+' is unavailable in the bounded isolated prototype');
    own(error,'code','ERR_SM_NODE_UNSUPPORTED');own(error,'module','node:stream/web');own(error,'operation',operation);
    own(error,'profile','sm-node-22.14.0-m0.9');throw error;}
  function limit(resource){const error=new RangeErrorCtor('node:stream/web exceeds '+resource+' budget');
    own(error,'code','ERR_SM_NODE_LIMIT');own(error,'resource',resource);throw error;}
  if(!record||typeof record!=='object'||ownKeys(record).length!==keys.length)fail(TypeErrorCtor,'ERR_SM_NODE_RECORD','Expected exact private native-class record');
  const nativeValues={__proto__:null};
  for(const key of keys){const entry=descriptor(record,key);
    if(!entry||!('value'in entry)||typeof entry.value!=='function')fail(TypeErrorCtor,'ERR_SM_NODE_RECORD','Missing private native class/callback '+key);
    nativeValues[key]=entry.value;
  }
  const {ReadableStream,ReadableStreamDefaultReader,ReadableStreamBYOBReader,ReadableStreamBYOBRequest,
    ReadableByteStreamController,ReadableStreamDefaultController,WritableStream,WritableStreamDefaultWriter,
    WritableStreamDefaultController,ByteLengthQueuingStrategy,CountQueuingStrategy,TransformStream,
    TransformStreamDefaultController,TextEncoder:Encoder,TextDecoder:Decoder}=nativeValues;
  const getter=(prototype,key)=>descriptor(prototype,key).get;
  const typed=Object.getPrototypeOf(Uint8Array.prototype);
  const typedBytes=getter(typed,'byteLength'),typedBuffer=getter(typed,'buffer');
  const typedName=getter(typed,Symbol.toStringTag);
  const dataBytes=getter(DataView.prototype,'byteLength'),dataBuffer=getter(DataView.prototype,'buffer');
  const bufferBytes=getter(ArrayBuffer.prototype,'byteLength'),bufferResizable=descriptor(ArrayBuffer.prototype,'resizable')?.get;
  const bufferDetached=descriptor(ArrayBuffer.prototype,'detached')?.get;
  if(!bufferDetached||!bufferResizable)fail(TypeErrorCtor,'ERR_SM_NODE_RECORD','Pinned ArrayBuffer lifecycle getters required');
  const sharedBytes=globalThis.SharedArrayBuffer&&getter(globalThis.SharedArrayBuffer.prototype,'byteLength');
  const charCodeAt=String.prototype.charCodeAt,slice=String.prototype.slice;
  const tsReadable=getter(TransformStream.prototype,'readable'),tsWritable=getter(TransformStream.prototype,'writable');
  const enqueue=TransformStreamDefaultController.prototype.enqueue,terminate=TransformStreamDefaultController.prototype.terminate;
  const controllerPrototype=TransformStreamDefaultController.prototype,controllerError=controllerPrototype.error;
  const desiredDescriptor=descriptor(controllerPrototype,'desiredSize');
  const encode=Encoder.prototype.encode,decode=Decoder.prototype.decode;
  const decoderEncoding=getter(Decoder.prototype,'encoding');
  const encoderEncoding=getter(Encoder.prototype,'encoding');
  const encoderStates=new WeakMap(),encoderGet=encoderStates.get.bind(encoderStates),encoderSet=encoderStates.set.bind(encoderStates);
  const decoderStates=new WeakMap(),decoderGet=decoderStates.get.bind(decoderStates),decoderSet=decoderStates.set.bind(decoderStates);
  function state(get,self,name){const value=get(self);if(!value)fail(TypeErrorCtor,undefined,'Invalid '+name+' receiver');return value;}
  function sourceBytes(input){
    if(input===undefined)fail(TypeErrorCtor,'ERR_INVALID_ARG_TYPE','chunk must be a BufferSource');
    let bytes,buffer,viewKind=null;
    if(isView(input)){
      viewKind=call(typedName,input)===undefined?'data':'typed';
      buffer=viewKind==='data'?call(dataBuffer,input):call(typedBuffer,input);
    }else{
      try{bytes=call(bufferBytes,input);buffer=input;}
      catch{
        let shared=false;if(sharedBytes)try{call(sharedBytes,input);shared=true;}catch{}
        if(shared)unsupported('shared decoder input');
        fail(TypeErrorCtor,'ERR_INVALID_ARG_TYPE','chunk must be an unshared BufferSource');
      }
    }
    // A native AB getter supplies a brand check and rejects shared memory.
    try{call(bufferBytes,buffer);}catch{unsupported('shared decoder input');}
    if(call(bufferDetached,buffer))unsupported('detached decoder input');
    if(call(bufferResizable,buffer))unsupported('resizable decoder input');
    if(viewKind)bytes=viewKind==='data'?call(dataBytes,input):call(typedBytes,input);
    if(bytes>MAX_INPUT_BYTES)limit('decoder-input-bytes');
    return bytes;
  }
  class TextEncoderStream{
    constructor(){
      const handle=new Encoder(),value={handle,pending:'',transform:null};
      value.transform=new TransformStream({
        transform(chunk,controller){
          // Node22's stream specifically uses String(), including Symbol.
          let text=StringCtor(chunk);
          if(text.length>MAX_SOURCE_UNITS)limit('encoder-source-units');
          if(value.pending)text=value.pending+text;
          value.pending='';
          if(text.length){const last=call(charCodeAt,text,[text.length-1]);
            if(last>=0xd800&&last<=0xdbff){value.pending=call(slice,text,[-1]);text=call(slice,text,[0,-1]);}}
          if(text.length)call(enqueue,controller,[call(encode,handle,[text])]);
        },
        flush(controller){if(value.pending){call(enqueue,controller,[call(encode,handle,[value.pending])]);value.pending='';}},
      });
      encoderSet(this,value);
    }
    get encoding(){return call(encoderEncoding,state(encoderGet,this,'TextEncoderStream').handle);}
    get readable(){return call(tsReadable,state(encoderGet,this,'TextEncoderStream').transform);}
    get writable(){return call(tsWritable,state(encoderGet,this,'TextEncoderStream').transform);}
  }
  class TextDecoderStream{
    constructor(label='utf-8',options=undefined){
      // Match Node22 label conversion before options validation. Template
      // conversion deliberately rejects Symbol, unlike encoder String(chunk).
      const normalizedLabel=`${label}`;
      if(options!==undefined&&options!==null&&typeof options!=='object'&&typeof options!=='function')
        fail(TypeErrorCtor,'ERR_INVALID_ARG_TYPE','options must be an object');
      let flagReadsStarted=false,handle,readFatal=false,readIgnore=false,firstFatal,firstIgnore;
      // Cache each first flag read: native Node rereads its private options,
      // whereas Starling reads once. User getters still run exactly in the
      // pinned fatal,ignoreBOM,ignoreBOM,fatal order on both backends.
      const nativeOptions={get fatal(){flagReadsStarted=true;if(!readFatal){readFatal=true;firstFatal=options?.fatal;}return firstFatal;},
        get ignoreBOM(){if(!readIgnore){readIgnore=true;firstIgnore=options?.ignoreBOM;}return firstIgnore;}};
      try{handle=new Decoder(normalizedLabel,nativeOptions);}
      catch(error){if(!flagReadsStarted&&error instanceof RangeErrorCtor)own(error,'code','ERR_ENCODING_NOT_SUPPORTED');throw error;}
      // Node22 rereads these for fast-path bookkeeping; its public getters
      // still expose the FIRST decode flags. Keep the observable reads without
      // allocating a second native decoder or changing decode/getter flags.
      void !!options?.ignoreBOM;void !!options?.fatal;
      const ignoreBOM=!!firstIgnore,fatal=!!firstFatal;
      const encoding=call(decoderEncoding,handle);
      if(encoding!=='utf-8')unsupported('TextDecoderStream encoding '+encoding);
      const value={handle,encoding,fatal,ignoreBOM,transform:null};
      const nativeFatal=!!firstFatal;
      function decoded(args){try{return call(decode,handle,args);}
        catch(error){if(nativeFatal&&error instanceof TypeErrorCtor&&!descriptor(error,'code'))own(error,'code','ERR_ENCODING_INVALID_ENCODED_DATA');throw error;}}
      value.transform=new TransformStream({
        transform(chunk,controller){sourceBytes(chunk);const output=decoded([chunk,{stream:true}]);
          if(output.length)call(enqueue,controller,[output]);},
        flush(controller){const output=decoded([]);if(output.length)call(enqueue,controller,[output]);call(terminate,controller);},
      });
      decoderSet(this,value);
    }
    get encoding(){return state(decoderGet,this,'TextDecoderStream').encoding;}
    get fatal(){return state(decoderGet,this,'TextDecoderStream').fatal;}
    get ignoreBOM(){return state(decoderGet,this,'TextDecoderStream').ignoreBOM;}
    get readable(){return call(tsReadable,state(decoderGet,this,'TextDecoderStream').transform);}
    get writable(){return call(tsWritable,state(decoderGet,this,'TextDecoderStream').transform);}
  }
  for(const name of ['encoding','readable','writable'])defines(TextEncoderStream.prototype,{[name]:{enumerable:true}});
  for(const name of ['encoding','fatal','ignoreBOM','readable','writable'])defines(TextDecoderStream.prototype,{[name]:{enumerable:true}});
  function CompressionStream(format){unsupported('CompressionStream');}
  function DecompressionStream(format){unsupported('DecompressionStream');}

  // Never call the old native implementation with its uninitialized prototype
  // as receiver. These opt-in guards are isolated until the native fix compiles.
  function initializedController(self){if(self===controllerPrototype)fail(TypeErrorCtor,'ERR_INVALID_THIS','Invalid TransformStreamDefaultController receiver');}
  const controllerGuards={
    enqueue(chunk){initializedController(this);return call(enqueue,this,[chunk]);},
    error(reason){initializedController(this);return call(controllerError,this,[reason]);},
    terminate(){initializedController(this);return call(terminate,this);},
    get desiredSize(){initializedController(this);return call(desiredDescriptor.get,this);},
  };
  for(const name of ['enqueue','error','terminate'])define(controllerPrototype,name,{...descriptor(controllerPrototype,name),value:controllerGuards[name]});
  define(controllerPrototype,'desiredSize',{...desiredDescriptor,get:descriptor(controllerGuards,'desiredSize').get});
  const module={ReadableStream,ReadableStreamDefaultReader,ReadableStreamBYOBReader,ReadableStreamBYOBRequest,
    ReadableByteStreamController,ReadableStreamDefaultController,TransformStream,TransformStreamDefaultController,
    WritableStream,WritableStreamDefaultWriter,WritableStreamDefaultController,ByteLengthQueuingStrategy,
    CountQueuingStrategy,TextEncoderStream,TextDecoderStream,CompressionStream,DecompressionStream};
  return{...module,default:module};
}

return createCodecModule;
})();
const installReadableIteration=(() => {
// ISOLATED continuation of the frozen codec/guard stage. Node22 stream
// algorithms and MIT source attribution are pinned in source-pins.json.
function installReadableIteration(record){
  const {ReadableStream:Stream,ReadableStreamDefaultReader:Reader,
    ReadableStreamDefaultController:Controller}=record;
  const apply=Reflect.apply,define=Object.defineProperty,descriptor=Object.getOwnPropertyDescriptor;
  const getPrototype=Object.getPrototypeOf,setPrototype=Object.setPrototypeOf;
  const TypeErrorCtor=TypeError,PromiseCtor=Promise;
  const then=PromiseCtor.prototype.then,resolve=PromiseCtor.resolve.bind(PromiseCtor);
  const call=(fn,self,args=[])=>apply(fn,self,args);
  const chain=(promise,fulfilled,rejected)=>call(then,promise,[fulfilled,rejected]);
  const locked=descriptor(Stream.prototype,'locked').get;
  const read=Reader.prototype.read,cancel=Reader.prototype.cancel,release=Reader.prototype.releaseLock;
  const closed=descriptor(Reader.prototype,'closed').get;
  const enqueue=Controller.prototype.enqueue,close=Controller.prototype.close;
  const iteratorSymbol=Symbol.iterator,asyncSymbol=Symbol.asyncIterator;
  function codeOwn(error,code){define(error,'code',{__proto__:null,value:code,writable:true,enumerable:true,configurable:true});return error;}
  function invalid(code,message){throw codeOwn(new TypeErrorCtor(message),code);}
  const asyncPrototype=getPrototype(getPrototype(getPrototype((async function*(){})())));
  const iteratorBase=setPrototype({next:undefined,return:undefined},asyncPrototype);

  function iteratorRecord(iterable){
    // Property access and callable errors deliberately remain ordinary errors.
    let method=iterable[asyncSymbol];
    if(method==null){
      method=iterable[iteratorSymbol];
      if(method===undefined)invalid('ERR_ARG_NOT_ITERABLE','The argument must be iterable');
      const iterator=call(method,iterable);
      // Node22 util.getIterator uses typeof object, excluding callable results.
      if(typeof iterator!=='object'||iterator===null)invalid('ERR_INVALID_STATE','Iterator method must return an object');
      const next=iterator.next;
      // Match the pinned async-generator bridge: yielded promises from sync
      // iterators are awaited and sync return delegation retains its semantics.
      const adapter=(async function*(){return yield*{[iteratorSymbol](){return iterator;}};})();
      // Capture the original next once, as Node's GetIterator does before
      // creating the bridge (the bridge itself reads next again on first use).
      void next;
      return{iterator:adapter,next:adapter.next};
    }
    const iterator=call(method,iterable);
    if(typeof iterator!=='object'||iterator===null)invalid('ERR_INVALID_STATE','Iterator method must return an object');
    return{iterator,next:iterator.next};
  }
  const methods={
    from(iterable){
      const source=iteratorRecord(iterable);
      return new Stream({
        pull(controller){
          const result=call(source.next,source.iterator);
          if(typeof result!=='object'||result===null)invalid('ERR_INVALID_STATE','Iterator.next must return an object');
          return chain(resolve(result),entry=>{
            if(typeof entry!=='object'||entry===null)invalid('ERR_INVALID_STATE','Iterator.next promise must fulfill with an object');
            if(entry.done)call(close,controller);else call(enqueue,controller,[entry.value]);
          });
        },
        cancel(reason){
          const method=source.iterator.return;
          if(method===undefined)return;
          return chain(resolve(call(method,source.iterator,[reason])),entry=>{
            if(typeof entry!=='object'||entry===null)invalid('ERR_INVALID_STATE','Iterator.return promise must fulfill with an object');
          });
        },
      },{highWaterMark:0});
    },
    values(options=undefined){
      // Class prototypes have no initialized stream; never delegate that
      // receiver. Native getter supplies the ordinary receiver brand check.
      if(this===Stream.prototype)invalid('ERR_INVALID_THIS','Invalid ReadableStream receiver');
      try{call(locked,this);}catch{invalid('ERR_INVALID_THIS','Invalid ReadableStream receiver');}
      if(options!==undefined&&options!==null&&typeof options!=='object'&&typeof options!=='function')
        invalid('ERR_INVALID_ARG_TYPE','options must be an object');
      const preventCancel=!!options?.preventCancel;
      let reader;
      try{reader=new Reader(this);}catch(error){
        if(error instanceof TypeErrorCtor&&!descriptor(error,'code'))codeOwn(error,'ERR_INVALID_STATE');throw error;
      }
      // Releasing an ordinary reader can reject its closed promise; handle it
      // privately even if the iterator's caller never inspects that promise.
      chain(call(closed,reader),()=>{},()=>{});
      let done=false,current,started=false;
      const finished=value=>({done:true,value});
      function nextStep(){
        if(done)return resolve(finished(undefined));
        return chain(call(read,reader),entry=>{
          current=undefined;
          if(entry.done){done=true;call(release,reader);return finished(undefined);}
          return{value:entry.value,done:false};
        },error=>{current=undefined;done=true;call(release,reader);throw error;});
      }
      function returnStep(value){
        if(done)return resolve(finished(value));
        done=true;
        if(preventCancel){call(release,reader);return resolve(finished(value));}
        let cancellation;
        try{cancellation=call(cancel,reader,[value]);}finally{call(release,reader);}
        return chain(resolve(cancellation),()=>finished(value));
      }
      return setPrototype({
        next(){
          if(!started){current=resolve();started=true;}
          current=current!==undefined?chain(current,nextStep,nextStep):nextStep();
          return current;
        },
        return(value){
          started=true;
          current=current!==undefined?chain(current,()=>returnStep(value),()=>returnStep(value)):returnStep(value);
          return current;
        },
        [asyncSymbol](){return this;},
      },iteratorBase);
    },
  };
  define(Stream,'from',{value:methods.from,writable:true,enumerable:false,configurable:true});
  define(Stream.prototype,'values',{value:methods.values,writable:true,enumerable:true,configurable:true});
  define(Stream.prototype,asyncSymbol,{value:methods.values,writable:true,enumerable:false,configurable:true});
  return{from:methods.from,values:methods.values};
}

return installReadableIteration;
})();
const installDataViewBYOB=(() => {
// ISOLATED ordinary-view adapter. nativeRead MUST be captured from the real
// native BYOB prototype before installing the frozen base simulation.
// No call delegates a DataView to the known unsupported native branch.
function installDataViewBYOB(record,nativeRead){
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

return installDataViewBYOB;
})();
// Uninstalled m0.9 production candidate. Exactly one private native record;
// capture/registration/CMake remain separately reviewed integration work.
function createStreamWebModule(record){
  // Validate every private field before reading any possibly untrusted getter.
  // createCodecModule performs exact own-data/function record validation first.
  const module=createCodecModule(record);
  const nativeRead=record.ReadableStreamBYOBReader.prototype.read;
  installReadableIteration(record);
  installDataViewBYOB(record,nativeRead);
  return module;
}

return createStreamWebModule;
})())SM_NODE_PROFILE";
