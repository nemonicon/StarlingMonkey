import assert from 'node:assert/strict';
import {readFile,open} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {join,dirname} from 'node:path';
import {pathToFileURL} from 'node:url';
const Z='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-zlib',OUT='/tmp/starling-node-compat/zlib-cost-wasmtime-strings-v1-root';
const hash=b=>createHash('sha256').update(b).digest('hex');
const desc=async path=>{const b=await readFile(path);return{path,sha256:hash(b),bytes:b.length};};
async function checked(d){assert.deepEqual(await desc(d.path),d);return JSON.parse(await readFile(d.path,'utf8'));}
async function indexed(path,sha){const d=await desc(path);assert.equal(d.sha256,sha);const ix=await checked(d);for(const r of ix.files){const a=await desc(join(dirname(path),r.path));assert.equal(a.sha256,r.sha256);assert.equal(a.bytes,r.bytes);}return d;}
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
const peer=join(Z,'independent-cost-jco-correctness-v3-results-review-v1');const correctnessIndex=await indexed(join(peer,'index.json'),'e03bb0db65f6009e86a6d55e4553e820d143c702128976efc5ef47e092548083');
const contractRow=await desc(join(peer,'result-contract.json'));assert.equal(contractRow.sha256,'25411f2ecb278c1eeda7b27a0aafa47b29cc3d9a53221a327e9e5c94002936f1');const contract=await checked(contractRow),reviewRow=await desc(join(peer,'results.json')),review=await checked(reviewRow);
for(const[k,v]of Object.entries(contract.requiredFixedValues))assert.deepEqual(review[k],v,k);
const streamsRow=contract.requiredExactDescriptors.actualEncoderStreams,streams=await checked(streamsRow);assert.equal(streams.primary.length,45);assert.equal(streams.off.length,15);
const source=join(Z,'cost-wasmtime-transport-candidate-v1');const sourceIndex=await indexed(join(source,'index.json'),'345ce70fd42c265137fb5653bdddfa47c5fb05463c24996f011697801fb1be56');
const {invocation,argvAccounting}=await import(pathToFileURL(join(source,'scalar-transport.mjs')));
const modelRow=await desc(join(Z,'cost-all-provider-argv-model-v1-root-data.json'));assert.equal(modelRow.sha256,'7ce260e887792279f4fb7a19a5f8c0bd9dea2a04e7fa54afa5d50d8535227a6f');const model=await checked(modelRow);
const actual=[...streams.primary,...streams.off],jobs=[],wasmtime='/private/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime',environment={RAYON_NUM_THREADS:'1'};
for(const role of['small','largest'])for(const arm of['native-on','fflate-on','fflate-off']){
 const id=role==='small'?'node-22.14.0.small-repeat.gzip':model.largest[arm].candidates[0],record=actual.find(v=>v.streamId===id);assert(record);assert.equal(hash(Buffer.from(record.encodedBase64,'base64')),record.encodedSha256);
 const component=contract.requiredComponents[arm];assert.deepEqual(await desc(component.path),component);
 const request=JSON.stringify({schemaVersion:1,kind:'crossdecode',caseId:record.caseId,stageRecord:record});const expression=invocation('validate',[request]);
 const argv=[wasmtime,'run','--invoke',expression,component.path],accounting=argvAccounting({argv,environment,argMax:1048576});assert(accounting.strictlyBelowArgMax);
 if(role==='largest')assert.equal(accounting.totalBytes,model.largest[arm].maxTotalBytes);
 jobs.push({name:role+'-'+arm,role,arm,component,record,request,requestSha256:hash(request),expressionSha256:hash(expression),argv,environment,accounting});
}
const plan={schemaVersion:1,state:'SIX_REVIEWED_COST_WASMTIME_STRING_CALLS_PREPARED_UNEXECUTED_V1',correctnessReview:{index:correctnessIndex,result:reviewRow,contract:contractRow},actualEncoderStreams:streamsRow,transportSource:sourceIndex,allProviderModel:modelRow,sourceIndependentReview:{index:await desc(join(Z,'independent-cost-wasmtime-transport-source-review-v1/index.json')),result:await desc(join(Z,'independent-cost-wasmtime-transport-source-review-v1/results.json'))},actualComponentReviews:contract.requiredActualComponentReviews,jobs,rootExportAuthority:null,wasmtimeExecuted:false,timing:false};
const path=join(OUT,'plan.json'),h=await open(path,'wx');try{await h.writeFile(JSON.stringify(plan,null,2)+'\n');await h.sync();}finally{await h.close();}
console.log(JSON.stringify({plan:await desc(path),jobs:jobs.map(v=>({name:v.name,streamId:v.record.streamId,argvTotal:v.accounting.totalBytes}))}));
