// SOURCE ONLY. Common controls, reported raw; never subtracted from codec time.
import {consumeFNV1a} from './fixtures.mjs';
export function createControls({Buffer}){
 return Object.freeze({
  consumeInput(input){return {bytesConsumed:input.byteLength,fnv:consumeFNV1a(input),copies:0,codecCalls:0};},
  copyInputAndConsume(input){const copied=Buffer.from(input);return {bytesConsumed:copied.byteLength,fnv:consumeFNV1a(copied),copies:1,codecCalls:0};},
  harnessNoCodec(input){return {bytesConsumed:0,declaredInputBytes:input.byteLength,tag:2166136261,copies:0,codecCalls:0};}
 });
}
