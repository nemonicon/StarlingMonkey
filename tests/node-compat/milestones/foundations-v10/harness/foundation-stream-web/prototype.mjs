// ISOLATED NAMESPACE-COMPOSITION PROBE, not a registered compatibility profile.
// Native class methods are being audited separately; availability is not parity.
const ErrorCtor=Error,defineProperty=Object.defineProperty;
function selected(name){
  const value=globalThis[name];
  if(typeof value==='function')return value;
  function unavailable(){
    const error=new ErrorCtor('node:stream/web.'+name+' is unavailable in the unintegrated namespace probe');
    error.code='ERR_SM_NODE_UNSUPPORTED';error.module='node:stream/web';error.operation=name;
    error.profile='unintegrated-node22-stream-web-probe-v1';throw error;
  }
  defineProperty(unavailable,'name',{value:name,configurable:true});
  return unavailable;
}
export const ReadableStream=selected('ReadableStream');
export const ReadableStreamDefaultReader=selected('ReadableStreamDefaultReader');
export const ReadableStreamBYOBReader=selected('ReadableStreamBYOBReader');
export const ReadableStreamBYOBRequest=selected('ReadableStreamBYOBRequest');
export const ReadableByteStreamController=selected('ReadableByteStreamController');
export const ReadableStreamDefaultController=selected('ReadableStreamDefaultController');
export const TransformStream=selected('TransformStream');
export const TransformStreamDefaultController=selected('TransformStreamDefaultController');
export const WritableStream=selected('WritableStream');
export const WritableStreamDefaultWriter=selected('WritableStreamDefaultWriter');
export const WritableStreamDefaultController=selected('WritableStreamDefaultController');
export const ByteLengthQueuingStrategy=selected('ByteLengthQueuingStrategy');
export const CountQueuingStrategy=selected('CountQueuingStrategy');
export const TextEncoderStream=selected('TextEncoderStream');
export const TextDecoderStream=selected('TextDecoderStream');
export const CompressionStream=selected('CompressionStream');
export const DecompressionStream=selected('DecompressionStream');
export default {ReadableStream,ReadableStreamDefaultReader,ReadableStreamBYOBReader,ReadableStreamBYOBRequest,
  ReadableByteStreamController,ReadableStreamDefaultController,TransformStream,TransformStreamDefaultController,
  WritableStream,WritableStreamDefaultWriter,WritableStreamDefaultController,ByteLengthQueuingStrategy,CountQueuingStrategy,
  TextEncoderStream,TextDecoderStream,CompressionStream,DecompressionStream};
