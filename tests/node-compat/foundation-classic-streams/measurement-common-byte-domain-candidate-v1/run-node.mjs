// Finite ordinary Node-host comparison only, not a guest or timing run.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createWorkload,scenarioIds} from './workload.mjs';
import * as nodeProvider from './node-provider.mjs';
import * as proposed from './canonical-proposed-provider.mjs';
assert.equal(process.version,'v22.14.0');assert(!process.env.NODE_OPTIONS);
const hash=b=>createHash('sha256').update(b).digest('hex'),here=dirname(fileURLToPath(import.meta.url));
assert.equal(hash(await readFile(process.execPath)),'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0');
const out=resolve(process.env.NODE_COMPAT_COMMON_BYTE_OUTPUT??'');assert(out.startsWith('/tmp/starling-node-compat/'));
try{await lstat(out);assert.fail('Choose fresh output');}catch(e){if(e.code!=='ENOENT')throw e;}await mkdir(out,{recursive:true});
const oracle=createWorkload(nodeProvider),candidate=createWorkload(proposed),cases=[];
for(const id of scenarioIds)for(const iterations of [1,16]){const setup=oracle.setup(id);assert.equal(candidate.setup(id),setup);const expected=await oracle.run(iterations,{trace:true}),observed=await candidate.run(iterations,{trace:true});cases.push({id,iterations,setup,expected,proposed:observed,proposedExact:JSON.stringify(expected)===JSON.stringify(observed)});}
await writeFile(join(out,'node-results.json'),JSON.stringify({schemaVersion:1,state:'NARROW_BYTE_DOMAIN_NODE_PROPOSED_MODEL_OBSERVATIONS',parameter:'explicit HWM chunkBytes+1 on source/pass/sink; synchronous completion',cases,
 sourceSha256:hash(await readFile(join(here,'workload.mjs'))),proposedCoreSha256:hash(await readFile(join(here,'../trace-semantics-candidate-v1/proposed/classic-core.generated.mjs'))),nodeExecutableSha256:hash(await readFile(process.execPath)),
 original39774Changed:false,stockProviderOrSchedulerModified:false,guestOrNativeOrTimingExecuted:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({cases:cases.length,proposedExact:cases.filter(row=>row.proposedExact).length,out}));
