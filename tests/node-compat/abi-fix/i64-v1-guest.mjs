import{echoS64,echoU64,echoSignedList,echoUnsignedList,echoRecord,echoResult}from'starling:i64-abi/identity@0.1.0';
export const localS64=value=>value;
export const localU64=value=>value;
export const constantMin=()=>-0x8000000000000000n;
export const constantMax=()=>0xffffffffffffffffn;
export const computedS64=value=>BigInt.asIntN(64,value-1n);
export const callbackS64=value=>echoS64(value);
export const callbackU64=value=>echoU64(value);
export const signedList=value=>echoSignedList(value);
export const unsignedList=value=>echoUnsignedList(value);
export function resultS64(ok,value){try{return echoResult(ok,value);}catch(error){throw error.payload;}}
export function recordCheck(){const inputs=[{signed:-0x8000000000000000n,unsigned:0xffffffffffffffffn,signedValues:new BigInt64Array([-0x8000000000000000n,-1n,0n,0x7fffffffffffffffn]),unsignedValues:new BigUint64Array([0n,0x8000000000000000n,0xffffffffffffffffn])},{signed:-1n,unsigned:0x8000000000000000n,signedValues:new BigInt64Array(),unsignedValues:new BigUint64Array()}];return JSON.stringify(inputs.map(input=>({input,observed:echoRecord(input)})),(_,v)=>typeof v==='bigint'?v+'n':ArrayBuffer.isView(v)?[...v]:v);}
