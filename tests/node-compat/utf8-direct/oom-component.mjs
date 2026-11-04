// Reuse all four existing genuine Buffer fault/recovery checks unchanged.
import {run as runBufferFaults} from '../oom/component.mjs';
const encoder=new TextEncoder(),encode=encoder.encode.bind(encoder);
const flat='A\u00e9\uD800\0\uFEFF',expected=[65,195,169,239,191,189,0,239,187,191];
const snapshot=encode('snapshot');
let calls=0,firstFaultBits=0;
function check(value){if(!value)throw 'private UTF8 OOM check failed';}
function equalBytes(bytes,wanted){check(bytes.length===wanted.length);for(let i=0;i<wanted.length;i++)check(bytes[i]===wanted[i]);}
function actualOOM(operation){let caught=false;try{operation();}catch(error){caught=true;check(error==='out of memory');}check(caught);}
function nonlinear(){
  // Two runtime-created flat strings exceed inline-string concatenation size.
  // The native site is armed ONLY if JS_StringIsLinear is false, and asserts
  // the real ensure-linear allocation checkpoint trips and reports OOM.
  const left=String.fromCharCode(...Array.from({length:4096},(_,index)=>65+index%26));
  const right=String.fromCharCode(...Array.from({length:4096},(_,index)=>97+index%26));
  return left+right;
}
export function run(){
  let stage=11;
  try{
    const kernel=runBufferFaults();if(kernel<0)return kernel-100;
    check(kernel===(((calls+1)<<16)|0x7ff));
    let bits=(kernel&0x7ff)|firstFaultBits;
    equalBytes(snapshot,[115,110,97,112,115,104,111,116]);
    if(calls===0){
      actualOOM(()=>encode(flat));bits|=1<<11;
      stage=12;actualOOM(()=>encode(nonlinear()));bits|=1<<12;
      firstFaultBits=bits&0x1800;
    }
    stage=13;
    for(let iteration=0;iteration<32;iteration++){
      const value=encode(flat);equalBytes(value,expected);
      const rope=nonlinear(),bytes=encode(rope);check(bytes.length===8192);
      for(let i=0;i<4096;i++){check(bytes[i]===65+i%26);check(bytes[i+4096]===97+i%26);}
    }
    bits|=1<<13;
    stage=14;
    const first=encode(flat),second=encode(flat);check(first!==second&&first.buffer!==second.buffer);
    check(first.byteOffset===0&&first.byteLength===expected.length&&first.buffer.byteLength===expected.length);
    first[0]=255;equalBytes(second,expected);equalBytes(snapshot,[115,110,97,112,115,104,111,116]);
    const marker={};let sentinel=false;try{encode({toString(){throw marker;}});}catch(error){sentinel=error===marker;}check(sentinel);
    bits|=1<<14;calls++;return(calls<<16)|bits;
  }catch(error){return-stage;}
}
