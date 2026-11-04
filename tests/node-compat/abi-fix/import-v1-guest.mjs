import { echoU32, constantU32, echoS32, echoF32, echoF64, echoU64, echoS64, echoList, echoPayload, echoResult } from 'starling:import-abi/identity@0.1.0';
export const directU32 = value => echoU32(value);
export const constantHigh = () => echoU32(0x80000000);
export const constantMax = () => echoU32(0xffffffff);
export const computedU32 = value => echoU32((value + 0x80000000) >>> 0);
export const helperConstant = () => constantU32();
export const directS32 = value => echoS32(value);
export const directF32 = value => echoF32(value);
export const directF64 = value => echoF64(value);
export const directU64 = value => echoU64(value);
export const directS64 = value => echoS64(value);
export const listU32 = value => echoList(value);
export function recordCheck() {
  const values = [{unsigned:0xffffffff,signed:-2147483648,float32:Math.fround(Math.PI),float64:-123.5,large:0xffffffffffffffffn,negative:0x7fffffffffffffffn},{unsigned:0x80000000,signed:-1,float32:-0,float64:Infinity,large:0x8000000000000000n,negative:1n}];
  return JSON.stringify(values.map(value => ({input:value,observed:echoPayload(value)})), (_,value)=>typeof value==='bigint'?value+'n':typeof value==='number'?(Object.is(value,-0)?'-0':Number.isFinite(value)?value:String(value)):value);
}
export function resultU32(ok, value) { try { return echoResult(ok, value); } catch (error) { throw error.payload; } }
