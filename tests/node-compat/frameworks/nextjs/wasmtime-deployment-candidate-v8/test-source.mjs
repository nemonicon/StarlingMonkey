// Read-only exact derivation and inert final client gate, no target actions.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {compileFunction} from 'node:vm';
const read=name=>readFile(new URL(name,import.meta.url),'utf8');
const old=await read('../wasmtime-deployment-candidate-v7/run-contracts.mjs'),current=await read('./run-contracts.mjs');
const derivation=JSON.parse(await read('./derivation.json'));let expected=old,checks=0;
assert.equal(derivation.clientInsertions.length,3);
for(const {before,after} of derivation.clientInsertions){assert.equal(expected.split(before).length,2);expected=expected.replace(before,after);checks++;}
assert.equal(expected,current);checks++;
let inverse=current;
for(const {before,after} of [...derivation.clientInsertions].reverse()){assert.equal(inverse.split(after).length,2);inverse=inverse.replace(after,before);}
assert.equal(inverse,old);checks++;
for(const name of ['deploy.mjs','run-owned.py','app-policy.mjs']){assert.equal(await read('./'+name),await read('../wasmtime-deployment-candidate-v7/'+name));checks++;}
const marker='  const contract =';
assert.equal(current.slice(current.indexOf(marker),current.indexOf(' result.originalContractPassed=')),old.slice(old.indexOf(marker),old.indexOf(' await save();\n}',old.indexOf('finally {'))));checks++;
assert(current.indexOf('result.supplemental=await collectSupplemental')<current.indexOf('for (const item of contract.requests)'));checks++;
const gate=current.slice(current.indexOf(' result.passed=result.http.length==='),current.indexOf(' await save();\n}',current.indexOf('finally {')));
const evaluate=compileFunction(gate+'return result;',['result']);
const base={http:Array.from({length:24},()=>({passed:true})),cacheInvalidation:{passed:true},streaming:{complete:true,incrementalDeliveryObserved:true},browserExit:{code:0},browser:{passed:true},errors:[],transportErrors:[],supplementalValidation:{passed:true}};
assert.equal(evaluate(structuredClone(base)).passed,true);checks++;
for(const mutate of [x=>x.supplementalValidation.passed=false,x=>delete x.supplementalValidation,
 x=>x.http[0].passed=false,x=>x.http.pop(),x=>x.cacheInvalidation.passed=false,
 x=>x.streaming.incrementalDeliveryObserved=false,x=>x.browser.passed=false,x=>x.errors.push({}),x=>x.transportErrors.push({})]){
 const value=structuredClone(base);mutate(value);assert.equal(evaluate(value).passed,false);checks++;
}
const plan=JSON.parse(await read('./plan.json')),prior=JSON.parse(await read('../wasmtime-deployment-candidate-v7/plan.json'));
for(const key of Object.keys(prior))if(!['state','sourceFamilies'].includes(key))assert.deepEqual(plan[key],prior[key]);
assert.deepEqual(plan.sourceFamilies.slice(0,-1),prior.sourceFamilies);assert.equal(plan.supplementalConcurrentRegression.cases,6);checks++;
console.log(JSON.stringify({sourceOnly:true,checks,threeClientInsertionsOnly:true,original24AndBrowserAssertionsExact:true,
 originalActorsExact:true,supplementalFailureMakesOverallFalse:true,actualTargetOrNetworkOrCopyInvoked:false}));
