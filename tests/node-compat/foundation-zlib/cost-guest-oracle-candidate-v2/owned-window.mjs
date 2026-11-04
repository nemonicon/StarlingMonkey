// Only ordinary source-created ArrayBuffer/Buffer windows. No memory probes.
import {requireValue,MAX_INPUT,bytesEqual} from './contract.mjs';
export function ownedWindow(Buffer,bytes){
 requireValue(bytes instanceof Uint8Array&&bytes.byteLength<=MAX_INPUT,'ordinary bounded bytes');
 const backing=new ArrayBuffer(bytes.byteLength+16),all=new Uint8Array(backing);all.fill(0xa5,0,8);all.fill(0x5a,8+bytes.byteLength);
 const input=Buffer.from(backing,8,bytes.byteLength);new Uint8Array(backing,8,bytes.byteLength).set(bytes);
 requireValue(Buffer.isBuffer(input)&&input.buffer===backing&&input.byteOffset===8&&input.byteLength===bytes.byteLength,'owned fixed attached unshared Buffer window');
 return{input,all};
}
export function windowMetadata(value){return{byteOffset:value.input.byteOffset,byteLength:value.input.byteLength,backingBytes:value.input.buffer.byteLength,prefix:[...value.all.subarray(0,8)],suffix:[...value.all.subarray(value.all.length-8)],construction:'new ordinary ArrayBuffer; fixed/attached/unshared by construction'};}
export function unchangedWindow(value,expected=null){return(expected===null||bytesEqual(value.input,expected))&&value.all.subarray(0,8).every(byte=>byte===0xa5)&&value.all.subarray(value.all.length-8).every(byte=>byte===0x5a);}
