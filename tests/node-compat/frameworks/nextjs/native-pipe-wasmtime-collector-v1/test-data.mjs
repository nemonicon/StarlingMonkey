// Pure retained DATA and mutation tests. Never imports suite/oracle/collector.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {validate,compare,parseOracle} from './comparison.mjs';
import {validateNative} from './native-model.mjs';
const read=async path=>JSON.parse(await readFile(path,'utf8'));
const contract=(await read(new URL('./case-contract.json',import.meta.url))).cases;
const raw=await readFile(new URL('./retained-node-oracle.stdout.jsonl',import.meta.url),'utf8');
const oracle=parseOracle(raw,contract),rows=[];
function test(name,body){body();rows.push({name,passed:true});}
const copy=value=>structuredClone(value);
for(let call=1;call<=3;call++)test('actual retained Node DATA self-comparison '+call,()=>{assert.equal(compare(oracle.values[call-1],oracle.values[call-1],call,contract).filter(x=>x.classification==='matches-node-selected-semantics').length,12);});
const mutations=[
 v=>v.log.pop(),v=>v.closed=1,v=>v.aborts[0]=false,v=>v.locks[0]=true,
 v=>v.log.reverse(),v=>v.result.type='null',v=>v.result.type='boolean',v=>v.cancelled=0,
 v=>v.before.push('abort'),v=>v.before.reads=2,v=>v.locks[0]=false,v=>v.rejected=false,
];
for(let i=0;i<12;i++)test('real case semantic mutation '+contract[i].id,()=>{const actual=copy(oracle.values[0]);mutations[i](actual.records[i].value);const comparisons=compare(actual,oracle.values[0],1,contract);assert.equal(comparisons[i].classification,'difference-requires-review');assert.equal(comparisons.filter(x=>x.classification==='difference-requires-review').length,1);});
test('extra actual Error name remains a compared field',()=>{const a=copy(oracle.values[0]);a.records[2].value.result.name='TypeError';a.records[2].value.result.same=false;assert.equal(compare(a,oracle.values[0],1,contract)[2].classification,'difference-requires-review');});
test('missing actual optional lock-error name remains a difference',()=>{const a=copy(oracle.values[0]);delete a.records[10].value.name;assert.equal(compare(a,oracle.values[0],1,contract)[10].classification,'difference-requires-review');});
for(const marker of [false,0,null,''])test('unexpected falsy case error retained '+JSON.stringify(marker),()=>{const a=copy(oracle.values[0]);a.records[0]={id:contract[0].id,completed:false,error:{type:typeof marker,isNull:marker===null,value:marker}};const c=compare(a,oracle.values[0],1,contract)[0];assert.equal(c.classification,'difference-requires-review');assert.equal(c.actual.error.value,marker);assert.equal(compare(a,a,1,contract)[0].classification,'difference-requires-review');});
for(const[key,change]of Object.entries({ordinal:a=>a.call=2,caseCount:a=>a.caseCount=11,recordOrder:a=>a.records.reverse(),wrongBoolean:a=>a.records[9].value.before.reads=false,missingIdentity:a=>delete a.records[5].value.result.same,extraField:a=>a.records[0].value.unreviewed=true,appImported:a=>a.applicationImported=true,fullNext:a=>a.fullNextClaim=true}))test('typed/schema refusal '+key,()=>{const a=copy(oracle.values[0]);change(a);assert.throws(()=>validate(a,1,contract));});
test('object property order does not manufacture a semantic difference',()=>{const a=copy(oracle.values[0]),v=a.records[0].value;a.records[0].value={writeLocked:v.writeLocked,readLocked:v.readLocked,log:v.log};assert(compare(a,oracle.values[0],1,contract).every(x=>x.classification==='matches-node-selected-semantics'));});
for(const[name,change]of [
 ['candidate oracle',x=>x[0].candidateInstalled=true],['wrong suite',x=>x[0].suite='other'],
 ['missing frame',x=>x.pop()],['wrong ordinal',x=>x[2].call=1],['nonstring frame',x=>x[1].kind='object'],
 ['failed oracle case',x=>{const v=JSON.parse(x[1].value);v.records[0]={id:contract[0].id,completed:false,error:{type:'boolean',isNull:false,value:false}};x[1].value=JSON.stringify(v);}],
])test('oracle refusal '+name,()=>{const frames=raw.trim().split('\n').map(JSON.parse);change(frames);assert.throws(()=>parseOracle(frames.map(x=>JSON.stringify(x)).join('\n'),contract));});
// These exact retained constructor/native inputs are read as DATA only. This
// does not turn that real-next constructor into a pipe grant or execute it.
const inputs=await read(new URL('./test-inputs.json',import.meta.url));
async function checked(row){const b=await readFile(row.path);assert.equal(b.length,row.bytes);assert.equal(createHash('sha256').update(b).digest('hex'),row.sha256);return JSON.parse(b);}
const root=await checked(inputs.retainedConstructorRootAuthority),native=await checked(inputs.retainedNativeMetadata);
test('actual retained incremental metadata exact whole-field model',()=>assert.equal(validateNative(native,root,root),true));
for(const[name,change]of [
 ['engine',a=>a.engine.sha256='0'.repeat(64)],['kind',a=>a.metadataExpectedFixedValues.metadataKind='old83'],
 ['count',a=>a.metadataExpectedFixedValues.freshFrontendCompileRows=80],['missing fixed engine',a=>delete a.metadataExpectedFixedValues.engine],
 ['build evidence',a=>a.engineBuildEvidence=[]],
])test('native selection mutation '+name,()=>{const a=copy(root);change(a);assert.throws(()=>validateNative(native,a,root));});
console.log(JSON.stringify({schemaVersion:1,pureDataCases:rows.length,passed:rows.length,actualRetainedNodeRecordsRead:36,nodeGuestComparisonsPerformed:0,rows,oracleInvoked:false,guestInvoked:false,collectorInvoked:false}));
