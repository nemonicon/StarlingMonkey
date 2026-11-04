import {Buffer} from 'node:buffer';
import {runCodecCases} from './codec-cases.mjs';
let calls=0;
export function run(){
  calls++;
  try{return JSON.stringify({calls,...runCodecCases({TextEncoder,Buffer})});}
  catch(error){return JSON.stringify({calls,failure:String(error),code:error?.code,stack:error?.stack});}
}
