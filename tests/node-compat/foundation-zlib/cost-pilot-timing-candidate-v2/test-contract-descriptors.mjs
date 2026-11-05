// Genuine current contract DATA/read-hash regression only. No admission action.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureProofDescriptors,descriptorReadPlan,verifyDescriptorList,PINNED_LARGE_ROWS,MAX_REGULAR_BYTES} from './contract-descriptors.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),refs=JSON.parse(await readFile(join(HERE,'references.json')));
let checks=0;const check=fn=>{fn();checks++;},reject=fn=>check(()=>assert.throws(fn));
const unique=new Map(),families=[];
for(const key of['fullCorrectness','stockWasmtimeStrings','actualControlsProof']){
 const proof=refs[key],result=JSON.parse(await readFile(proof.result.path)),contract=JSON.parse(await readFile(proof.contract.path));
 const rows=captureProofDescriptors(result,contract);families.push({key,result:proof.result,contract:proof.contract,descriptorCount:rows.length});
 for(const row of rows)unique.set(JSON.stringify(row),row);
}
const rows=[...unique.values()],large=rows.filter(r=>r.bytes>MAX_REGULAR_BYTES);
check(()=>assert.equal(rows.length,91));check(()=>assert.equal(large.length,1));check(()=>assert.equal(large[0].sha256,PINNED_LARGE_ROWS[0].sha256));check(()=>assert.equal(large[0].bytes,108619024));
check(()=>assert.equal(descriptorReadPlan(large[0]).mode,'streamed-pinned-executable'));
check(()=>assert.equal(descriptorReadPlan({...large[0],path:large[0].path.replace('/private/tmp/','/tmp/')}).mode,'streamed-pinned-executable'));
reject(()=>descriptorReadPlan({...large[0],sha256:'0'.repeat(64)}));reject(()=>descriptorReadPlan({...large[0],bytes:large[0].bytes-1}));reject(()=>descriptorReadPlan({...large[0],path:large[0].path+'-other'}));
reject(()=>descriptorReadPlan({path:'/private/tmp/unlisted-large-binary',sha256:'a'.repeat(64),bytes:MAX_REGULAR_BYTES+1}));reject(()=>descriptorReadPlan({...large[0],bytes:-1}));
const mutable=rows.map(r=>({...r})),pending=verifyDescriptorList(mutable);mutable[0].path='/private/tmp/redirect-after-first-await';mutable.pop();
const captured=await pending;check(()=>assert.equal(captured.rows.length,91));check(()=>assert.equal(captured.plans.filter(p=>p.mode==='streamed-pinned-executable').length,1));
await captured.recheck();checks++;
const guard=await readFile(join(HERE,'parent-guard.template.mjs'),'utf8');
check(()=>assert.equal((guard.match(/await verifyContractDescriptor\(row\)/g)??[]).length,2));
check(()=>assert(guard.includes('referenced=[...captureProofDescriptors(v,c)]')));
check(()=>assert(!guard.includes('for(const row of referenced)await regular(row')));
console.log(JSON.stringify({schemaVersion:1,state:'ACTUAL_NESTED_CONTRACT_DESCRIPTOR_READ_HASH_AND_RECHECK_PASSED_V2',checks,
 families,actualUniqueDescriptors:rows.length,actualReferencedBytes:rows.reduce((sum,r)=>sum+r.bytes,0),
 regularDescriptorCount:captured.plans.filter(p=>p.mode==='bounded-regular').length,
 streamedLargeDescriptorCount:1,streamedPinnedNode:large[0],actualInitialAndPrivateRecheckPassed:true,
 actualCurrentLargeRowsComplete:true,unknownOversizedRolePathHashSizeRefused:true,callerLoopAndRecheckSourceRegressionPassed:true,
 wholeExecutableBufferOrTextReportLoaded:false,readHashFunctionsOnly:true,
 preflightAdmissionHelperWorkerGuestProviderCodecNativeJcoWasmtimePilotTimingExecuted:false,operationalAdmission:false}));
