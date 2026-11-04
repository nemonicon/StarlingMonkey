import {Buffer} from 'node:buffer';
import {runCodecCases} from './codec-cases.mjs';
import {runProductionCodecExtras,runEncodeIntoSourcePolicy} from './production-extra-cases.mjs';

// Ordinary snapshot-created output, retained across valid component calls.
const encoder=new TextEncoder(),snapshot=encoder.encode('snapshot\0\u00e9');
const snapshotBacking=snapshot.buffer;
const wanted=[115,110,97,112,115,104,111,116,0,195,169];
let calls=0;
function checkSnapshot(){
  if(snapshot.buffer!==snapshotBacking||snapshot.byteOffset!==0||snapshot.length!==wanted.length||snapshotBacking.byteLength!==wanted.length)throw new Error('snapshot output view relationship');
  for(let index=0;index<wanted.length;index++)if(snapshot[index]!==wanted[index])throw new Error('snapshot output bytes');
}
checkSnapshot();
export function run(){
  calls++;
  try{
    checkSnapshot();
    const baseline=runCodecCases({TextEncoder,Buffer});
    const extras=runProductionCodecExtras({TextEncoder,Buffer});
    const sourcePolicy=runEncodeIntoSourcePolicy({TextEncoder,expectedPolicy:'starling-coerce'});
    checkSnapshot();
    const independent=encoder.encode('snapshot\0\u00e9');
    if(independent.buffer===snapshotBacking)throw new Error('snapshot output ownership');
    return JSON.stringify({calls,baseline,extras,sourcePolicy,snapshot:{bytes:wanted.length,backingIdentityPreserved:true,offset:0,independentOutput:true}});
  }catch(error){return JSON.stringify({calls,failure:String(error),code:error?.code,stack:error?.stack});}
}
