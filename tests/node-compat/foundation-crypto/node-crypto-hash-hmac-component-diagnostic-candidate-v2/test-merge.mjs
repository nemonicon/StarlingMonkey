// Actual old/new orchestration fragments over synthetic plain host DATA only.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const here=new URL('./',import.meta.url),deriv=JSON.parse(await readFile(new URL('derivations.json',here))),change=deriv.files.find(x=>x.path==='worker.mjs').edits[0];
const before=await readFile(deriv.files.find(x=>x.path==='worker.mjs').before.path,'utf8'),after=await readFile(new URL('worker.mjs',here),'utf8');assert(before.split(change.before).length===2&&after.split(change.after).length===2);
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
const oldFn=new AsyncFunction('mode','detail','jcoChild','f','out',change.before+'\nreturn detail;');
const newFn=new AsyncFunction('mode','detail','jcoChild','f','out',change.after+'\nreturn detail;');
function initial(){return{generatedModuleImportAttempted:false,generatedModuleImported:false,ordinaryGuestCalls:0,callAttempts:0,callReturns:0,callThrows:0,stringReturns:0,comparedCalls:0,rawStrings:[],rawThrowCaptureFailures:[]};}
function child(count,throwValue,shouldThrow=false){return async(f,out,d)=>{d.generatedModuleImportAttempted=true;await Promise.resolve();d.generatedModuleImported=true;d.callAttempts=count;d.callReturns=count;d.ordinaryGuestCalls=count;d.stringReturns=count;d.comparedCalls=count;for(let n=1;n<=count;n++)d.rawStrings.push({ordinal:n,synthetic:true});if(shouldThrow)throw throwValue;return{cryptoOperationsRequested:true,namespaceIdentityScope:'synthetic Source-seam test only'};};}
let checks=0;
for(const count of [1,3]){
 const old=initial(),oldRows=old.rawStrings,observed=await oldFn('jco-worker',old,child(count));assert.equal(observed.callAttempts,0);assert.equal(observed.generatedModuleImported,false);assert.equal(observed.rawStrings,oldRows);assert.equal(observed.rawStrings.length,count);checks++;
 const current=initial(),rows=current.rawStrings,result=await newFn('jco-worker',current,child(count));for(const k of ['generatedModuleImportAttempted','generatedModuleImported','cryptoOperationsRequested'])assert.equal(result[k],true);for(const k of ['callAttempts','callReturns','ordinaryGuestCalls','stringReturns','comparedCalls'])assert.equal(result[k],count);assert.equal(result.rawStrings,rows);assert.equal(result.rawStrings.length,count);checks++;
}
for(const thrown of [null,undefined,false,'X']){
 const current=initial(),rows=current.rawStrings;let caught=false;try{await newFn('jco-worker',current,child(1,thrown,true));}catch(e){caught=true;assert.equal(e,thrown);}assert(caught&&current.generatedModuleImported&&current.callAttempts===1&&current.rawStrings===rows&&rows.length===1);checks++;
}
{const current=initial(),result=await newFn('worker',current,async()=>{throw Error('must not run');});assert.equal(result,current);assert.equal(result.callAttempts,0);checks++;}
const refs=JSON.parse(await readFile(new URL('references.json',here))),entryChange=deriv.files.find(x=>x.path==='entry.mjs').edits[1];
const entry=await readFile(new URL('entry.mjs',here),'utf8');assert.equal(entry.split(entryChange.after).length,2);
const prefix=entryChange.after.slice('assert('.length).split("&&['bundled'")[0];
const allowed=new Function('root','constructed','refs','same','return ('+prefix+');');
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);let bindingCases=0;
for(const arm of ['bundled','raw-fixture']){
 const row=refs.reusedConstructions[arm],root={arm,actualComponent:row.component,actualConstructionResult:row.result},constructed={sourceIndex:refs.constructorSourceIndex};
 assert.equal(allowed(root,constructed,refs,same),true);bindingCases++;
 const other=refs.reusedConstructions[arm==='bundled'?'raw-fixture':'bundled'];
 for(const bad of [{...root,actualComponent:other.component},{...root,actualConstructionResult:other.result}]){assert.equal(allowed(bad,constructed,refs,same),false);bindingCases++;}
 assert.equal(allowed(root,{sourceIndex:{...refs.constructorSourceIndex,sha256:'0'.repeat(64)}},refs,same),false);bindingCases++;
}
console.log(JSON.stringify({schemaVersion:1,state:'ACTUAL_AWAIT_MERGE_SOURCE_SEAM_REGRESSION_PASSED',checks,bindingCases,oldSuccessPrimitiveLossReproduced:true,newSuccessFlagsAndCountersPreserved:true,throwAndSharedArrayPreserved:true,syntheticDataOnly:true,operationalEntryOrJcoChildOrGuestOrCryptoInvoked:false}));
