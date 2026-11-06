import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {validateNative} from './native-model.mjs';
import {compare} from './comparison.mjs';
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const p=await read(new URL('./plan.json',import.meta.url)),n=await read(p.nativeMetadata.path),contract=(await read(new URL('./case-contract.json',import.meta.url))).cases;
validateNative(n,p);let checks=1;
for(const mutate of [x=>x.metadataKind='EXPERIMENTAL_NEXT_NATIVE_BUILD_ACTUAL_V1',x=>x.buildSupportInputCount=386,x=>x.actualCompileRows.pop(),x=>x.actualSeparateEmbeddingCompileRows=[],x=>x.old83MetadataProjected=true,x=>x.requestedCMake.SPIDERMONKEY_INTL='OFF',x=>x.actualAggregateLock.sha256='0'.repeat(64)]){const x=structuredClone(n);mutate(x);assert.throws(()=>validateNative(x,p));checks++;}
const frames=(await readFile(new URL('../regexp-unicode-probe-root-results-v1/node-owned/stdout.log',import.meta.url),'utf8')).trim().split('\n').map(JSON.parse);
for(let call=1;call<=3;call++){const v=JSON.parse(frames[call].value);assert(compare(v,v,call,contract).every(x=>x.classification==='matches-node-selected-semantics'));checks++;
const bad=structuredClone(v),r=bad.records.find(x=>x.compiled);r.compiled=false;r.error={valueType:'object',isNull:false,name:{type:'string',value:'SyntaxError'},code:{type:'undefined'}};assert(compare(bad,v,call,contract).some(x=>x.classification==='difference-requires-review'));checks++;}
console.log(JSON.stringify({passed:true,checks,retainedDataOnly:true,oracleInvoked:false,guestExecuted:false}));
