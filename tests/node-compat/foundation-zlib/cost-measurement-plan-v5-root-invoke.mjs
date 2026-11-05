// Root read-only DATA caller; no worker, codec or timing entry is used.
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const descriptor=JSON.parse(process.argv[2]);
const raw=await readFile(descriptor.path);
if(raw.length!==descriptor.bytes||createHash('sha256').update(raw).digest('hex')!==descriptor.sha256)throw Error('Root options changed');
const options=JSON.parse(raw);
const {preparePlan}=await import('./cost-pilot-timing-candidate-v5/prepare-plan.mjs');
const result=await preparePlan(options);
const after=await readFile(descriptor.path);
if(!after.equals(raw))throw Error('Root options changed after read-only plan');
console.log(JSON.stringify(result));
