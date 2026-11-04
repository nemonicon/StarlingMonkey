// No Buffer operation, fault hook, host capability or imported binding.
const text='constant ASCII / é / 🐒';
export const run=()=>text;
export const signed=()=>-2147483648;
export const unsigned=()=>0xffffffff;
export const floating=()=>Math.PI;
export const byteList=()=>new Uint8Array([0,1,2,127,128,254,255]);
export const rawStringInspectJson=()=>JSON.stringify({text,length:text.length,codes:Array.from(text,value=>value.codePointAt(0))});
export const stringLength=()=>text.length;
export function stringDigest(){let result=0;for(let i=0;i<text.length;i++)result=(Math.imul(result,31)+text.charCodeAt(i))>>>0;return result;}
