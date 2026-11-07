// Inert Source wiring tests; no Next, helper collector, server or browser runs.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const read=path=>readFile(path,'utf8');
const json=async path=>JSON.parse(await read(path));
let checks=0;const check=(v,m)=>{assert(v,m);checks++;};
const old=await read(join(here,'../browser-hydration-matched-host-candidate-v4/run-stock.mjs'));
const actor=await read(join(here,'run-stock.mjs'));
const plan=await json(join(here,'plans.json'));
const prior=await json(join(here,'../browser-hydration-matched-host-candidate-v4/plans.json'));
const rawSpan="  result.supplemental = await collectSupplemental({origin:result.origin,output:join(root,'supplemental')});\n  await save();\n  result.supplementalValidation = validateSupplemental(result.supplemental);\n  await save();\n";
const conjunction="  result.originalContractPassed = result.passed;\n  result.passed = result.originalContractPassed && result.supplementalValidation?.passed === true;\n";
const importLine="import {collectSupplemental,validateSupplemental} from '../wasmtime-deployment-candidate-v8/supplemental.mjs';\n";
const inverse=actor.replace(importLine,'').replace('next-browser-hydration-stock-v6','next-browser-hydration-stock-v4')
  .replace(rawSpan,'').replace('plan.arms.stock.browserSource.path',"join(here, 'browser-check.mjs')").replace(conjunction,'');
check(inverse===old,'exact five actor replacements preserve all original behavior');
check(actor.indexOf(rawSpan)>actor.indexOf('result.prepared = true;'),'batch follows readiness');
check(actor.indexOf(rawSpan)<actor.indexOf('for (const item of contract.requests)'),'batch precedes original23+action');
check(!rawSpan.includes('throw')&&!rawSpan.includes('if ('),'validation false does not skip original contracts');
const helper=await read(plan.supplemental.module.path);
check(createHash('sha256').update(helper).digest('hex')===plan.supplemental.module.sha256,'shared helper hash');
check(Buffer.byteLength(helper)===plan.supplemental.module.bytes,'shared helper bytes');
const v8=await json(plan.supplemental.sourceIndex.path);
const member=v8.files.find(r=>r.path==='supplemental.mjs');
check(member.sha256===plan.supplemental.module.sha256&&member.bytes===plan.supplemental.module.bytes,'indexed helper role');
check(resolve(here,'../wasmtime-deployment-candidate-v8/supplemental.mjs')===plan.supplemental.module.path,'literal import matches protected module');
check(plan.sourceFamilies.some(r=>JSON.stringify(r)===JSON.stringify(plan.supplemental.sourceIndex)),'whole V8 family protected');
check(plan.protectedInputs.some(r=>JSON.stringify(r)===JSON.stringify(plan.supplemental.module)),'helper explicitly protected');
check(plan.supplemental.cases===6&&plan.supplemental.actualRun===null,'six Source-only cases');
check(plan.supplemental.clientOverlapOnly===true&&plan.supplemental.sameStoreOrNativeResourceIdentityClaimed===false,'scope');
const restored=structuredClone(plan);
restored.state=prior.state;restored.outputPrefix=prior.outputPrefix;
restored.sourceFamilies=restored.sourceFamilies.slice(0,-2);restored.protectedInputs=restored.protectedInputs.slice(0,-1);
delete restored.supplemental;
assert.deepEqual(restored,prior);checks++;
check(plan.arms.stock.timeoutSeconds===300,'original timeout');
check(plan.arms.stock.browserSource.sha256==='e3248453ffab97305c85652b9d0e6e3a928139fe9ce01ace0bb9d0bb39ab89a7','original strict CDP browser');
check(plan.arms.stock.browserSource.path===prior.arms.stock.browserSource.path,'no browser implementation copied');
check(plan.requiredObservations.http===24&&plan.requiredObservations.browser===2,'original denominator');
check(plan.browserTimingPolicy.wholeTestTimeoutMs===20000&&plan.browserTimingPolicy.boundedCaptureDrainBeforeCloseMs===500,'original browser caps');
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
const collectCode=new AsyncFunction('collectSupplemental','validateSupplemental','save','result','root','join',rawSpan);
for(const passed of [false,true]){
  const result={origin:'http://127.0.0.1:1'},raw={six:'inert DATA'},events=[];
  await collectCode(async options=>{assert.equal(options.output,'/owned/supplemental');events.push('collect');return raw;},
    value=>{assert.equal(value,raw);assert.deepEqual(events,['collect','raw-save']);events.push('validate');return {passed};},
    async()=>{if(result.supplementalValidation===undefined){assert.equal(result.supplemental,raw);events.push('raw-save');}else events.push('validation-save');},
    result,'/owned',join);
  check(JSON.stringify(events)===JSON.stringify(['collect','raw-save','validate','validation-save']),'raw publication precedes validation');
  check(result.supplementalValidation.passed===passed,'false validation retained');
}
const finish=new Function('result',conjunction+'return result;');
for(const original of [false,true])for(const supplemental of [false,true,undefined]){
  const result=finish({passed:original,...(supplemental===undefined?{}:{supplementalValidation:{passed:supplemental}})});
  check(result.originalContractPassed===original&&result.passed===(original&&supplemental===true),'both independent gates required');
}
const template=await json(join(here,'root-authority-template.json'));
check(template.runId===null&&template.sourceIndex===null&&template.plans===null&&template.localhostServerAllowed===null&&template.browserAllowed===null&&template.unissued===true,'actual slots unissued');
console.log(JSON.stringify({state:'MATCHED_STOCK_V6_SOURCE_WIRING_CHECKS_PASSED',checks,
  sourceOnly:true,sharedHelperCollectorInvoked:false,serverOrBrowserOrAppInvoked:false}));
