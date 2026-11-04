// Exact old/new validation blocks; no codec/provider functions execute.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {Buffer} from 'node:buffer';
import {base64,bytesEqual,requireValue} from '../cost-guest-oracle-candidate-v2/contract.mjs';
import {ownedWindow,unchangedWindow} from '../cost-guest-oracle-candidate-v2/owned-window.mjs';
import {captureUntimedOutput,requirePriorOutputUnchanged} from '../cost-guest-oracle-candidate-v2/output-stability.mjs';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
async function predicate(name,pin){
 const root=new URL('../'+name+'/',import.meta.url),indexRaw=await readFile(new URL('index.json',root));assert.equal(hash(indexRaw),pin);
 const index=JSON.parse(indexRaw),row=index.files.find(value=>value.path==='runtime.mjs'),raw=await readFile(new URL('runtime.mjs',root));assert.equal(hash(raw),row.sha256);
 const source=raw.toString(),start=source.indexOf('  const previousComparable='),end=source.indexOf('  const result=',start);assert(start>0&&end>start);const block=source.slice(start,end);assert(!block.includes('invoke(')&&!block.includes('provider.'));
 return new Function('priorOutput','output','active','inputBefore','caseId','bytesEqual','unchangedWindow','requireValue','requirePriorOutputUnchanged','const nonempty=output.length>0;\n'+block+'\nreturn {previousComparable,independentBacking,mutationProbe,previousFullBytesUnchanged:typeof previousFullBytesUnchanged===\'undefined\'?null:previousFullBytesUnchanged};');
}
const old=await predicate('cost-guest-oracle-candidate-v1','473c997933b5df6560896c58d8dd79cb426a81d0730d24892b93d3edaa75a046');
const fixed=await predicate('cost-guest-oracle-candidate-v2','ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8');
const records=[];
for(const changedIndex of [0,1,63]){
 const original=Uint8Array.from({length:64},(_,i)=>i),prior=new Uint8Array(original),current=new Uint8Array(original),snapshot=captureUntimedOutput(0,prior,base64(prior));
 prior[changedIndex]^=255;
 const input=Uint8Array.of(7,8),window=ownedWindow(Buffer,input),args=[snapshot,current,{window},new Uint8Array(input),0,bytesEqual,unchangedWindow,requireValue,requirePriorOutputUnchanged];
 const oldResult=old(...args);assert(oldResult.independentBacking&&oldResult.mutationProbe.previousRestored);
 assert.throws(()=>fixed(...args),/full prior output changed/);assert(!bytesEqual(prior,original));
 records.push({changedIndex,legacyAccepted:true,fixedRejected:true,wholePriorBytesWereCorrupted:true});
}
for(const length of [0,64]){
 const previous=Uint8Array.from({length},(_,i)=>i),current=new Uint8Array(previous),snapshot=captureUntimedOutput(0,previous,base64(previous)),input=Uint8Array.of(7,8),window=ownedWindow(Buffer,input);
 const result=fixed(snapshot,current,{window},new Uint8Array(input),0,bytesEqual,unchangedWindow,requireValue,requirePriorOutputUnchanged);
 assert.equal(result.previousFullBytesUnchanged,true);assert(bytesEqual(previous,current));
}
await writeFile(process.argv[2],JSON.stringify({schemaVersion:1,state:'PURE_SOURCE_PRIOR_OUTPUT_STABILITY_REGRESSION_CLOSED',records,unchangedAndEmptyChecks:2,codecOrProviderCalls:0,actualCodecDefectClaim:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({regressions:3,oldAccepted:true,fixedRejected:true,codecCalls:0}));
