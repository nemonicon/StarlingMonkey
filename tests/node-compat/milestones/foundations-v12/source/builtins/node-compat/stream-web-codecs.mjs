// ISOLATED opt-in guest prototype. No production registration/global codecs.
// Encoder framing follows Node22 internal/webstreams/encoding.js (MIT), but
// bulk Unicode conversion remains in the captured native encoder.
export const MAX_SOURCE_UNITS=1024*1024;
export const MAX_INPUT_BYTES=16*1024*1024;
export function createCodecModule(record){
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
