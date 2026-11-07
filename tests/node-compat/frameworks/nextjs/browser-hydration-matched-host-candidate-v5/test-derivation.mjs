// Finite source/JSON checks only. Does not import any actor or owner main.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const read=p=>readFile(new URL(p,import.meta.url),'utf8');
const descriptor=async p=>{const q=new URL(p,import.meta.url),b=await readFile(q);return {path:q.pathname,sha256:createHash('sha256').update(b).digest('hex'),bytes:b.length};};
const old=JSON.parse(await read('../browser-hydration-matched-host-candidate-v4/plans.json'));
const plan=JSON.parse(await read('./plans.json'));let checks=0;
for(const name of ['run-stock.mjs','run-owned.py']){
 const donor=await read('../browser-hydration-matched-host-candidate-v4/'+name),current=await read('./'+name);
 assert.equal(donor.split('next-browser-hydration-stock-v4').length,2);
 assert.equal(current,donor.replace('next-browser-hydration-stock-v4','next-browser-hydration-stock-v5'));checks++;
}
const actor=await read('./run-stock.mjs'),donor=await read('../browser-hydration-matched-host-candidate-v4/run-stock.mjs');
assert.equal(actor.slice(actor.indexOf('const result =')),donor.slice(donor.indexOf('const result =')));checks++;
for(const name of ['root-authority-template.json','test-inputs.mjs','test-namespace.py','test-output.mjs']){
 assert.equal(await read('./'+name),await read('../browser-hydration-matched-host-candidate-v4/'+name));checks++;
}
assert.equal(await read('./browser-check.mjs'),await read('../browser-extra-cdp-off-candidate-v1/browser-check.mjs'));checks++;
const browser=await descriptor('./browser-check.mjs'),family=await descriptor('../browser-extra-cdp-off-candidate-v1/index.json');
assert.deepEqual(plan.arms.stock.browserSource,browser);assert.deepEqual(plan.extraCdpObserverFamily,family);checks+=2;
assert.deepEqual(plan.sourceFamilies.slice(0,-1),old.sourceFamilies);assert.deepEqual(plan.sourceFamilies.at(-1),family);checks++;
assert.deepEqual(plan.protectedInputs,old.protectedInputs);checks++;
const expected=structuredClone(old);expected.state='EXTRA_CDP_OFF_MATCHED_STOCK_HOST_SOURCE_ONLY_V5';expected.outputPrefix='/private/tmp/starling-node-compat/next-browser-hydration-stock-v5';
expected.sourceFamilies.push(family);expected.arms.stock.browserSource=browser;expected.extraCdpObserverFamily=family;
expected.observationalControl={extraWorkerSessionEnabled:false,playwrightBuiltinProtocolUnchanged:true,selectedDifference:'Only worker additional diagnostic CDP session is disabled; strict workload unchanged',originalCohortAcceptance:false,causeEstablished:false};
expected.preservedParentSource=await descriptor('../browser-hydration-matched-host-candidate-v4/index.json');assert.deepEqual(plan,expected);checks++;
for(const key of ['sourceReview','rootAuthority','actualComparison','runId']){assert.equal(plan[key],null);checks++;}
for(const key of ['outputRoot','monitorOutputRoot','argv','rootAuthority','actualRun']){assert.equal(plan.arms.stock[key],null);checks++;}
assert.equal(plan.arms.stock.timeoutSeconds,300);assert.equal(plan.browserTimingPolicy.wholeTestTimeoutMs,20000);assert.equal(plan.browserTimingPolicy.boundedCaptureDrainBeforeCloseMs,500);checks++;
console.log(JSON.stringify({sourceOnly:true,checks,exactOwnerAndActorNamespaceOnlyDelta:true,offWorkerAndCompleteFamilyPinned:true,strictWorkloadSuffixUnchanged:true,operationalSlotsNull:true,actorOrNetworkOrCopyInvoked:false}));
