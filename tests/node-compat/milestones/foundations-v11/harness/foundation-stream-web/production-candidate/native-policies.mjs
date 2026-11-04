// Public installed-module policies only; two private factory-record tests stay
// in the preserved source-stage corpus and are not fabricated as app APIs.
const MAX_SOURCE_UNITS=1048576,MAX_INPUT_BYTES=16777216;
import {pipeline,errorValue} from '../candidate/codec-cases.mjs';
function ensure(value,message){if(!value)throw Error(message);}
async function guardRejection(module,track,view,options){
  const source=new module.ReadableStream({type:'bytes',start(controller){controller.enqueue(Uint8Array.of(9,10));controller.close();}});
  const reader=track(source.getReader({mode:'byob'}));let error;
  try{await reader.read(view,options);}catch(caught){error=caught;}
  await reader.cancel();await reader.closed;reader.releaseLock();return error;
}
export async function policyCases(module,fixture){
  const checks=[];
  for(const label of ['utf-16le','utf-16be','windows-1252','shift_jis']){
    let error;try{new module.TextDecoderStream(label);}catch(caught){error=caught;}
    ensure(error?.code==='ERR_SM_NODE_UNSUPPORTED','known label must fail '+label);checks.push('deferred-label:'+label);
  }
  const tooMuchText=await pipeline(new module.TextEncoderStream(),['a'.repeat(MAX_SOURCE_UNITS+1)]);
  ensure(tooMuchText.writes[0]?.error?.code==='ERR_SM_NODE_LIMIT','encoder source cap');checks.push('encoder-over-limit');
  const encoderEdge=await pipeline(new module.TextEncoderStream(),['a'.repeat(MAX_SOURCE_UNITS)]);
  ensure(encoderEdge.outputs[0]?.byteLength===MAX_SOURCE_UNITS&&encoderEdge.close.fulfilled,'encoder accepted boundary');checks.push('encoder-at-limit');
  const tooMuchData=await pipeline(new module.TextDecoderStream(),[new Uint8Array(MAX_INPUT_BYTES+1)]);
  ensure(tooMuchData.writes[0]?.error?.code==='ERR_SM_NODE_LIMIT','decoder byte cap');checks.push('decoder-over-limit');
  const decoderEdgeInput=new Uint8Array(MAX_INPUT_BYTES);decoderEdgeInput.fill(97);
  const decoderEdge=await pipeline(new module.TextDecoderStream(),[decoderEdgeInput]);
  ensure(decoderEdge.outputs[0]?.stringLength===MAX_INPUT_BYTES&&decoderEdge.outputs[0].first==='a'&&decoderEdge.outputs[0].last==='a'&&decoderEdge.close.fulfilled,'decoder accepted boundary');
  checks.push('decoder-at-limit');
  const resizableDecoder=new ArrayBuffer(4,{maxByteLength:8});
  const resizableResult=await pipeline(new module.TextDecoderStream(),[new Uint8Array(resizableDecoder)]);
  ensure(resizableResult.writes[0]?.error?.code==='ERR_SM_NODE_UNSUPPORTED','decoder RAB policy');checks.push('decoder-resizable');
  const detachedDecoder=new Uint8Array(4);detachedDecoder.buffer.transfer();
  const detachedResult=await pipeline(new module.TextDecoderStream(),[detachedDecoder]);
  ensure(detachedResult.writes[0]?.error?.code==='ERR_SM_NODE_UNSUPPORTED','decoder detached policy');checks.push('decoder-detached');
  ensure((await guardRejection(module,fixture.track,new Uint8Array(MAX_INPUT_BYTES+1)))?.code==='ERR_SM_NODE_LIMIT','BYOB byte cap');checks.push('byob-over-limit');
  const resizable=new ArrayBuffer(4,{maxByteLength:8});
  ensure((await guardRejection(module,fixture.track,new Uint8Array(resizable)))?.code==='ERR_SM_NODE_UNSUPPORTED','BYOB RAB policy');checks.push('byob-resizable');
  class Subclass extends Uint8Array{}
  ensure((await guardRejection(module,fixture.track,new Subclass(4)))?.code==='ERR_SM_NODE_UNSUPPORTED','BYOB subclass policy');checks.push('byob-subclass');
  const source=new module.ReadableStream({type:'bytes',start(controller){controller.enqueue(Uint8Array.of(9,10));controller.close();}});
  const reader=fixture.track(new module.ReadableStreamBYOBReader(source)),view=new Uint8Array(4);let minError;
  try{await reader.read(view,{min:2});}catch(error){minError=error;}
  ensure(minError?.code==='ERR_SM_NODE_UNSUPPORTED'&&view.byteLength===4,'unsupported min must not detach/consume');
  const recovery=await reader.read(new Uint8Array(4));ensure(JSON.stringify([...recovery.value])==='[9,10]','unsupported min preserves source queue');
  await reader.closed;reader.releaseLock();checks.push('byob-minimum-no-operation-and-recovery');
  const shared={available:typeof SharedArrayBuffer==='function',checks:0};
  if(shared.available){
    for(const input of [new SharedArrayBuffer(1),new Uint8Array(new SharedArrayBuffer(1))]){
      const result=await pipeline(new module.TextDecoderStream(),[input]);ensure(result.writes[0]?.error?.code==='ERR_SM_NODE_UNSUPPORTED','shared decoder policy');shared.checks++;
    }
  }
  return{checks,shared,limits:{sourceUnits:MAX_SOURCE_UNITS,inputBytes:MAX_INPUT_BYTES},ordinaryNativeBrandProof:false};
}
export async function primordialCases(module,record){
  const saved={String,Error,TypeError,RangeError,apply:Reflect.apply,integer:Number.isInteger,isView:ArrayBuffer.isView,
    get:WeakMap.prototype.get,set:WeakMap.prototype.set,charCodeAt:String.prototype.charCodeAt,slice:String.prototype.slice,
    encode:record.TextEncoder.prototype.encode,decode:record.TextDecoder.prototype.decode,
    enqueue:record.TransformStreamDefaultController.prototype.enqueue,terminate:record.TransformStreamDefaultController.prototype.terminate,
    readable:Object.getOwnPropertyDescriptor(record.TransformStream.prototype,'readable'),writable:Object.getOwnPropertyDescriptor(record.TransformStream.prototype,'writable')};
  let invoked=0;function replaced(){invoked++;throw new saved.Error('replaced intrinsic');}
  let encoded,decoded,error;
  try{
    globalThis.String=globalThis.Error=globalThis.TypeError=globalThis.RangeError=replaced;
    Reflect.apply=Number.isInteger=ArrayBuffer.isView=replaced;
    WeakMap.prototype.get=WeakMap.prototype.set=replaced;
    saved.String.prototype.charCodeAt=saved.String.prototype.slice=replaced;
    record.TextEncoder.prototype.encode=record.TextDecoder.prototype.decode=replaced;
    record.TransformStreamDefaultController.prototype.enqueue=record.TransformStreamDefaultController.prototype.terminate=replaced;
    Object.defineProperty(record.TransformStream.prototype,'readable',{get:replaced,configurable:true});
    Object.defineProperty(record.TransformStream.prototype,'writable',{get:replaced,configurable:true});
    encoded=await pipeline(new module.TextEncoderStream(),['\ud83c','\udf0d']);
    decoded=await pipeline(new module.TextDecoderStream(),[Uint8Array.of(0xe2),Uint8Array.of(0x82,0xac)]);
    try{new module.CompressionStream();}catch(caught){error=caught;}
  }finally{
    globalThis.String=saved.String;globalThis.Error=saved.Error;globalThis.TypeError=saved.TypeError;globalThis.RangeError=saved.RangeError;
    Reflect.apply=saved.apply;Number.isInteger=saved.integer;ArrayBuffer.isView=saved.isView;
    WeakMap.prototype.get=saved.get;WeakMap.prototype.set=saved.set;
    saved.String.prototype.charCodeAt=saved.charCodeAt;saved.String.prototype.slice=saved.slice;
    record.TextEncoder.prototype.encode=saved.encode;record.TextDecoder.prototype.decode=saved.decode;
    record.TransformStreamDefaultController.prototype.enqueue=saved.enqueue;record.TransformStreamDefaultController.prototype.terminate=saved.terminate;
    Object.defineProperty(record.TransformStream.prototype,'readable',saved.readable);Object.defineProperty(record.TransformStream.prototype,'writable',saved.writable);
  }
  ensure(invoked===0,'replaced producer/intrinsic executed');
  ensure(JSON.stringify(encoded.outputs)==='[[240,159,140,141]]'&&encoded.close.fulfilled,'captured encoder');
  ensure(JSON.stringify(decoded.outputs)==='["€"]'&&decoded.close.fulfilled,'captured decoder');
  ensure(error?.code==='ERR_SM_NODE_UNSUPPORTED','captured error constructor');
  return{replacementInvocations:invoked,encoder:true,decoder:true,error:errorValue(error)};
}
