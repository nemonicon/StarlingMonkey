// Positive/handled ordinary19 only; no initializer/fatal/limit/GC test workload.
import * as stream from 'node:stream';
import * as alias from 'stream';
import * as promises from 'node:stream/promises';
import * as promiseAlias from 'stream/promises';
import {Buffer} from 'node:buffer';
import {checks} from '../../production-runtime-activated-v2/harness/checks.mjs';

let calls=0;
const requireTrue=(value,message)=>{if(!value)throw new Error('CLASSIC_HTTP: '+message);};
export async function runClassic19(){
  requireTrue(stream===alias&&promises===promiseAlias,'ESM aliases');
  requireTrue(stream.default===stream.Stream&&stream.Stream.Stream===stream.Stream,'root default graph');
  requireTrue(stream.promises===promises.default,'shared promises graph');
  requireTrue(globalThis.Buffer===Buffer,'canonical Buffer');
  const ordinary=await checks(stream,promises,Buffer);
  requireTrue(ordinary.length===19,'ordinary group count');
  return {schema:1,calls:++calls,ordinary,identity:{esmAliases:true,rootDefault:true,promises:true,globalBuffer:true},
    scope:'Bounded ordinary19 only. No classic Web bridge, full API, ALS, reset or request-isolation claim.'};
}
