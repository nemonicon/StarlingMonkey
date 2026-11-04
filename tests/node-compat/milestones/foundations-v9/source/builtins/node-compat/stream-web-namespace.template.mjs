// UNINSTALLED explicit ESM template. The private record import below is an
// internal guest binding to be supplied by reviewed registration, not a host
// interface, available embedding API or production module in this repository.
import record from 'node-compat:stream-web-native-record';
import {createStreamWebModule} from './stream-web.mjs';
const moduleRecord=createStreamWebModule(record);
export const ByteLengthQueuingStrategy=moduleRecord.ByteLengthQueuingStrategy;
export const CompressionStream=moduleRecord.CompressionStream;
export const CountQueuingStrategy=moduleRecord.CountQueuingStrategy;
export const DecompressionStream=moduleRecord.DecompressionStream;
export const ReadableByteStreamController=moduleRecord.ReadableByteStreamController;
export const ReadableStream=moduleRecord.ReadableStream;
export const ReadableStreamBYOBReader=moduleRecord.ReadableStreamBYOBReader;
export const ReadableStreamBYOBRequest=moduleRecord.ReadableStreamBYOBRequest;
export const ReadableStreamDefaultController=moduleRecord.ReadableStreamDefaultController;
export const ReadableStreamDefaultReader=moduleRecord.ReadableStreamDefaultReader;
export const TextDecoderStream=moduleRecord.TextDecoderStream;
export const TextEncoderStream=moduleRecord.TextEncoderStream;
export const TransformStream=moduleRecord.TransformStream;
export const TransformStreamDefaultController=moduleRecord.TransformStreamDefaultController;
export const WritableStream=moduleRecord.WritableStream;
export const WritableStreamDefaultController=moduleRecord.WritableStreamDefaultController;
export const WritableStreamDefaultWriter=moduleRecord.WritableStreamDefaultWriter;
export default moduleRecord.default;
