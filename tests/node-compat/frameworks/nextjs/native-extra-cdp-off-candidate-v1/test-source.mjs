// Inert Source/callback/error-gate checks; no browser or resource entrypoints.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {compileFunction} from 'node:vm';
const read=name=>readFile(new URL(name,import.meta.url),'utf8');
const prior=await read('../browser-hydration-candidate-v3/browser-check.mjs');
const source=await read('./browser-check.mjs');
const delta=JSON.parse(await read('./derivation.json'));
let checks=0,expected=prior;
assert.equal(delta.edits.length,4);checks++;
for(const edit of delta.edits){assert.equal(expected.split(edit.before).length,2);expected=expected.replace(edit.before,edit.after);checks++;}
assert.equal(source,expected);checks++;
let inverse=source;
for(const edit of [...delta.edits].reverse()){assert.equal(inverse.split(edit.after).length,2);inverse=inverse.replace(edit.after,edit.before);}
assert.equal(inverse,prior);checks++;
assert.equal(source.slice(source.indexOf("  await test('client-counter'")),prior.slice(prior.indexOf("  await test('client-counter'")));checks++;
assert.equal(source.slice(source.indexOf('function createNetworkObserver('),source.indexOf('let sequence=')),prior.slice(prior.indexOf('function createNetworkObserver('),prior.indexOf('let sequence=')));checks++;
assert.equal(await read('./asset-pins.json'),await read('../browser-hydration-candidate-v3/asset-pins.json'));checks++;
for(const needle of ['newCDPSession(', 'cdp.send(', 'cdp.on(']){assert(!source.includes(needle));checks++;}
assert(source.includes('wasmBrowserRun:true,targetRuntimeProvenance:'));checks++;
assert(source.includes('actual Wasm execution and component identity require parent Root host/artifact evidence'));checks++;
const setup=source.slice(source.indexOf("      mark('extra-cdp-disabled');"),source.indexOf('      const observations=await body(page,mark,snapshot);'));
const calls=[],record={},context={newCDPSession(){throw Error('Extra session must not be allocated');}};
compileFunction(setup,['mark','trace','id','phase','record','context'])(x=>calls.push(['mark',x]),(...x)=>calls.push(['trace',...x]),'server-action','before-body',record,context);
assert.deepEqual(record,{cdpEnabledBeforeFirstAppRequest:false,extraCDPSessionEnabled:false});checks++;
assert.deepEqual(calls,[['mark','extra-cdp-disabled'],['trace','server-action','before-body','extra-cdp-disabled',{extraSessionEnabled:false,playwrightBuiltinProtocolUnchanged:true,interception:false}]]);checks++;
const pins=JSON.parse(source.match(/const assetPins=(.*);\n/)[1]);assert.equal(pins.length,5);checks++;
const gate=source.slice(source.indexOf('  const counterAssets='),source.indexOf('  result.finished='));
const evaluate=compileFunction(gate+'return result;',['result','assetPins','URL']);
const base={assetBodies:pins.map(p=>({test:'client-counter',url:'http://inert.invalid'+p.path,sourceMatch:true})),errors:[],tests:[{passed:true},{passed:true}],pageerrors:[],consoleerrors:[],failedrequests:[],browserClosed:true};
assert.equal(evaluate(structuredClone(base),pins,URL).passed,true);checks++;
for(const change of [x=>x.errors.push({message:'body unavailable'}),x=>x.failedrequests.push({failure:{errorText:'net::ERR_ABORTED'}}),x=>x.pageerrors.push({}),x=>x.consoleerrors.push({}),x=>x.tests[1].passed=false,x=>x.browserClosed=false,x=>x.assetBodies.pop(),x=>x.assetBodies[0].sourceMatch=false,x=>x.assetBodies.push(x.assetBodies[0])]){
 const value=structuredClone(base);change(value);assert.equal(evaluate(value,pins,URL).passed,false);checks++;
}
const plan=JSON.parse(await read('./plan.json'));
assert.equal(plan.targetArm,'native');assert.equal(plan.wasmBrowserRun,true);assert.equal(plan.actualNativeExecutionRequiresParentEvidence,true);checks++;
assert.equal(plan.extraDiagnosticSessionEnabled,false);assert.equal(plan.playwrightBuiltinProtocolUnchanged,true);checks++;
for(const key of ['actualRootAuthority','actualRuntime','actualComparison']){assert.equal(plan[key],null);checks++;}
console.log(JSON.stringify({sourceOnly:true,checks,exactFourSpanDerivation:true,extraSessionNeverAllocated:true,allFunctionalAndStrictFailureGatesUnchanged:true,nativeArmTelemetryRequiresParentProof:true,actorBrowserServerNetworkOrCopyInvoked:false}));
