// Pure DATA/source-delta checks only. No host, component or guest invocation.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const read=async name=>readFile(new URL(name,import.meta.url),'utf8');
const derivation=JSON.parse(await read('./derivation.json'));let cases=0;
for(const row of derivation.files){let text=await read('./'+row.path);for(const edit of [...row.edits].reverse()){assert.equal(text.split(edit.after).length,2);text=text.replace(edit.after,edit.before);cases++;}assert.equal(text,await readFile(row.parent.path,'utf8'));cases++;}
const source=await read('./serve.mjs');assert(!source.includes('p.engine')&&!source.includes('p.nativeMetadata'));cases++;
const start=source.indexOf("assert.equal(native.metadataKind,'EXPERIMENTAL_NEXT_NATIVE_BUILD_ACTUAL_V1')"),end=source.indexOf('\n assert.equal(audit.state',start);assert(start>0&&end>start);
const check=Function('assert','native','a',source.slice(start,end));
const engine={path:'/not-executed/synthetic-engine',sha256:'a'.repeat(64),bytes:8};
const value=()=>({metadataKind:'EXPERIMENTAL_NEXT_NATIVE_BUILD_ACTUAL_V1',engine,nativePolicyInputCount:435,embeddingInputCount:3,buildSupportInputCount:386,old83MetadataProjected:false,engineExecuted:false,guestExecuted:false,adoption:false,selectedModuleManifests:{public:Array(22),private:Array(2)}});
check(assert,value(),{engine});cases++;
for(const mutate of [x=>x.engine={...engine,sha256:'b'.repeat(64)},x=>x.nativePolicyInputCount=83,x=>x.embeddingInputCount=2,x=>x.old83MetadataProjected=true,x=>x.adoption=true]){const v=value();mutate(v);assert.throws(()=>check(assert,v,{engine}));cases++;}
console.log(JSON.stringify({passed:true,cases,syntheticDataOnly:true,unknownFutureEngineAcceptedOnlyByExactAuthorityAndConstructionMatch:true,hostLaunched:false,guestExecuted:false}));
