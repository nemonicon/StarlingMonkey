// Read-only Source and inert callbacks/data. No browser/server/resource actions.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {compileFunction} from 'node:vm';
const read=name=>readFile(new URL(name,import.meta.url),'utf8');
const donor=await read('../browser-hydration-candidate-v3/browser-check.mjs');
const source=await read('./browser-check.mjs'),delta=JSON.parse(await read('./derivation.json'));
let expected=donor,checks=0;
assert.equal(delta.edits.length,3);
for(const {before,after} of delta.edits){assert.equal(expected.split(before).length,2);expected=expected.replace(before,after);checks++;}
assert.equal(source,expected);checks++;
let inverse=source;
for(const {before,after} of [...delta.edits].reverse()){assert.equal(inverse.split(after).length,2);inverse=inverse.replace(after,before);}
assert.equal(inverse,donor);checks++;
assert.equal(source.slice(source.indexOf("  await test('client-counter'")),donor.slice(donor.indexOf("  await test('client-counter'")));checks++;
assert.equal(source.slice(source.indexOf('function createNetworkObserver('),source.indexOf('let sequence=')),donor.slice(donor.indexOf('function createNetworkObserver('),donor.indexOf('let sequence=')));checks++;
for(const name of ['observer-core.mjs','test-observer.mjs','asset-pins.json']){assert.equal(await read('./'+name),await read('../browser-hydration-candidate-v3/'+name));checks++;}
for(const needle of ['newCDPSession(',"cdp.send(","cdp.on("]){assert(!source.includes(needle));checks++;}
const setup=source.slice(source.indexOf("      mark('extra-cdp-disabled');"),source.indexOf('      const observations=await body(page,mark,snapshot);'));
const calls=[],record={},context={newCDPSession(){throw Error('Extra diagnostic session must never be created');}};
compileFunction(setup,['mark','trace','id','phase','record','context'])(x=>calls.push(['mark',x]),(...x)=>calls.push(['trace',...x]),'server-action','unchanged-before-body',record,context);
assert.deepEqual(record,{cdpEnabledBeforeFirstAppRequest:false,extraCDPSessionEnabled:false});
assert.deepEqual(calls,[['mark','extra-cdp-disabled'],['trace','server-action','unchanged-before-body','extra-cdp-disabled',{extraSessionEnabled:false,playwrightBuiltinProtocolUnchanged:true,interception:false}]]);checks++;
const pins=JSON.parse(source.match(/const assetPins=(.*);\n/)[1]);assert.equal(pins.length,5);
const gate=source.slice(source.indexOf('  const counterAssets='),source.indexOf('  result.finished='));
const evaluate=compileFunction(gate+'return result;',['result','assetPins','URL']);
const base={assetBodies:pins.map(p=>({test:'client-counter',url:'http://inert.invalid'+p.path,sourceMatch:true})),errors:[],tests:[{passed:true},{passed:true}],pageerrors:[],consoleerrors:[],failedrequests:[],browserClosed:true};
assert.equal(evaluate(structuredClone(base),pins,URL).passed,true);checks++;
for(const mutate of [x=>x.errors.push({message:'body unavailable'}),x=>x.failedrequests.push({failure:{errorText:'net::ERR_ABORTED'}}),x=>x.pageerrors.push({}),x=>x.consoleerrors.push({}),x=>x.tests[1].passed=false,x=>x.browserClosed=false,x=>x.assetBodies.pop(),x=>x.assetBodies[0].sourceMatch=false,x=>x.assetBodies.push(x.assetBodies[0])]){
 const value=structuredClone(base);mutate(value);assert.equal(evaluate(value,pins,URL).passed,false);checks++;
}
const plan=JSON.parse(await read('./plan.json'));assert.equal(plan.extraDiagnosticSessionEnabled,false);assert.equal(plan.playwrightBuiltinProtocolUnchanged,true);
for(const key of ['actualRootAuthority','actualRuntime','actualComparison'])assert.equal(plan[key],null);
console.log(JSON.stringify({sourceOnly:true,checks,exactThreeSpanDerivation:true,extraSessionNeverCreated:true,allFunctionalAndStrictFailureGatesPreserved:true,playwrightBuiltinProtocolNotDisabled:true,actorBrowserServerNetworkOrCopyInvoked:false}));
