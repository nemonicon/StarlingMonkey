// Synthetic DATA validation only: no host launch, Wasm/component or guest call.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {validateResponse} from './serve.mjs';
assert.equal(process.version,'v22.14.0');
const plan=JSON.parse(await readFile(new URL('./plan.json',import.meta.url),'utf8'));
const ids=plan.recordIds;
const synthetic=()=>({marker:plan.marker,records:ids.map(id=>({id,passed:true,value:id==='http-adapter'?{method:'POST',pathname:'/dependencies',bodyBytes:21}:id==='rng-deployed-shapes'?{secretValuesRetained:false}:null})),snapshotBarriers:{deployedResetAttempted:false,deployedResnapshotAttempted:false,nativeSnapshotGuardRuntimeProof:false}});
const options={ids,method:'POST',bodyBytes:21};let count=0;
validateResponse(synthetic(),options);count++;
for(const mutate of [x=>x.marker='wrong',x=>x.records.pop(),x=>x.records.push(x.records[0]),x=>x.records[0].id=x.records[1].id,x=>x.records[2].passed=false,x=>x.records[2].passed=1,x=>x.records[2].passed='true',x=>x.records.at(-1).value.method='GET',x=>x.records.at(-1).value.bodyBytes=0,x=>x.records.at(-1).value.pathname='/other',x=>x.snapshotBarriers.deployedResetAttempted=true,x=>x.snapshotBarriers.nativeSnapshotGuardRuntimeProof=true,x=>x.records.find(y=>y.id==='rng-deployed-shapes').value.secretValuesRetained=true]){
 const value=synthetic();mutate(value);assert.throws(()=>validateResponse(value,options));count++;
}
console.log(JSON.stringify({passed:true,cases:count,syntheticDataOnly:true,actualGuestResults:null,hostLaunched:false,guestExecuted:false}));
