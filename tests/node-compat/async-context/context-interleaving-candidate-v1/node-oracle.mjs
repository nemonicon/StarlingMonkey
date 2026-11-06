import assert from 'node:assert/strict';
import {AsyncLocalStorage,AsyncResource} from 'node:async_hooks';
import {installAsyncResourceFacade} from '../async-resource-candidate-v1/async-resource.mjs';
import {collectContextInterleaving,contextPublicProjection} from './cases.mjs';
import {createNodeReference} from './node-reference.mjs';
assert.equal(process.version,'v22.14.0');
assert.equal(process.env.NODE_OPTIONS,undefined);
assert(!process.execArgv.includes('--experimental-async-context-frame'));
const root={AsyncLocalStorage,AsyncResource};installAsyncResourceFacade(root);
const runs=[];
for(const [variant,Resource] of [['node-original',AsyncResource],['node-sealed-facade',root.AsyncResource]]){
  const backend=createNodeReference(Resource),raw=[];
  for(const call of [1,2,3]){
    const result=await collectContextInterleaving(backend,call);
    raw.push(result);console.log(JSON.stringify({kind:'whole-collection',variant,call,observed:result}));
    assert.equal(result.passed,true,JSON.stringify(result));contextPublicProjection(result);
  }
  runs.push({variant,raw});
}
for(let i=0;i<3;i++)assert.deepEqual(contextPublicProjection(runs[0].raw[i]),contextPublicProjection(runs[1].raw[i]));
console.log(JSON.stringify({schemaVersion:1,state:'CONTEXT_INTERLEAVING_NODE22_REFERENCE_AND_SEALED_FACADE_HOST_PASSED_V1',passed:true,
  collections:6,controlsPerCollection:5,variants:runs.map(r=>r.variant),calls:[1,2,3],
  selectedAssertionCounts:runs[0].raw[0].records.map(r=>({id:r.id,assertions:r.assertions.length})),
  publicProjectionMatched:true,nativeBoundaryParityClaimed:false,guestOrEngineExecuted:false,
  maxPlannedWaits:Math.max(...runs.flatMap(r=>r.raw.map(x=>x.peakPlannedWaits)))}));
