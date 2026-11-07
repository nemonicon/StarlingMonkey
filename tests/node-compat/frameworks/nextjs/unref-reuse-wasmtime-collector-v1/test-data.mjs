// Inert retained/synthetic DATA only. No oracle, timer, ALS, HTTP or guest action.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {compileFunction} from 'node:vm';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {assessSafety,validate,compare,parseOracle} from './comparison.mjs';
const contract=JSON.parse(await readFile(new URL('../../../async-context/unref-reuse-candidate-v1/future-runtime-contract.json',import.meta.url),'utf8'));
const raw=await readFile(new URL('./retained-node-oracle.stdout.jsonl',import.meta.url),'utf8');
const oracle=parseOracle(raw,contract),rows=[],hostCase='unref-inert-shape-test';
const copy=x=>structuredClone(x),encoded=x=>new TextEncoder().encode(JSON.stringify(x));
function test(name,body){body();rows.push({name,passed:true});}
function envelope(call=1){const collection=copy(oracle.values[call-1]);collection.boundaryMode='actual-native-private-boundaries';collection.firstHostCase=collection.requestedHostCase=hostCase;return{schemaVersion:1,marker:'NEXT_NATIVE_UNREF_REUSE_V1',call,method:'GET',collection};}
for(let call=1;call<=3;call++)test('retained host DATA native-shaped envelope '+call,()=>{
 const value=envelope(call),v=validate(value,call,contract,hostCase);assert.equal(v.callChecks,[13,20,18][call-1]);assert.equal(v.callbackChecks,[0,7,9][call-1]);
 assert.equal(assessSafety(encoded(value),200,call,contract,hostCase).safeToReuse,true);
 assert.equal(compare(value,oracle.values[call-1],call,contract,hostCase).classification,'matches-node-public-projection');
});
for(let call=1;call<=3;call++)for(const[name,change]of[
 ['missing boundary',v=>delete v.collection.boundaryMode],['wrong boundary',v=>v.collection.boundaryMode='node-public-empty-store-projection'],
 ['wrong first tag',v=>v.collection.firstHostCase='other'],['wrong requested tag',v=>v.collection.requestedHostCase='other'],
 ['wrong ordinal',v=>v.collection.ordinal=0],['wrong phase',v=>v.collection.phase='unknown'],
 ['false collection',v=>v.collection.passed=false],['nonboolean collection',v=>v.collection.passed=1],
 ['early delivery inconclusive',v=>v.collection.coverage='inconclusive-callback-before-B-entry'],
 ['owner overclaim',v=>v.collection.physicalStoreOrNativeOwnerIdentityProved=true],['unknown scope',v=>v.collection.newScope=false],
 ['empty check inventory',v=>v.collection.checks=[]],['missing check',v=>v.collection.checks.pop()],
 ['extra check',v=>v.collection.checks.push({id:'extra',passed:true})],['false check',v=>v.collection.checks[0].passed=false],
 ['nonboolean check',v=>v.collection.checks[0].passed=1],['wrong marker identity',v=>v.collection.observations[0].firstIdentity=false],
 ['wrong context label',v=>v.collection.observations[0].firstLabel='wrong'],['candidate delivered',v=>v.collection.counts.candidate=1],
 ['unknown pending count',v=>v.collection.plannedHandles.pending=99],['failure field',v=>v.collection.error={type:'null'}],
])test('strict safety/full refusal '+call+' '+name,()=>{const v=envelope(call);change(v);assert.throws(()=>validate(v,call,contract,hostCase));const s=assessSafety(encoded(v),200,call,contract,hostCase);assert.equal(s.safeToReuse,false);assert.deepEqual(s.envelope,v);assert.equal(typeof s.validationFailure.message,'string');});
test('missing distinct callback check refuses',()=>{const v=envelope(3);v.collection.callbackChecks.pop();assert.equal(assessSafety(encoded(v),200,3,contract,hostCase).safeToReuse,false);});
test('unsafe final cleanup refuses',()=>{const v=envelope(3);v.collection.finalCleanup.workloadPendingAfterClear=1;assert.equal(assessSafety(encoded(v),200,3,contract,hostCase).safeToReuse,false);});
for(const status of [400,500,503])test('whole valid envelope wrong HTTP status '+status,()=>{assert.equal(assessSafety(encoded(envelope()),status,1,contract,hostCase).safeToReuse,false);});
test('missing protected contract refuses',()=>{assert.equal(assessSafety(encoded(envelope()),200,1,undefined,hostCase).safeToReuse,false);});
test('malformed UTF8/JSON refuse',()=>{for(const b of [Uint8Array.of(255),new TextEncoder().encode('{bad')])assert.equal(assessSafety(b,200,1,contract,hostCase).safeToReuse,false);});
for(const[name,change]of[
 ['missing frame',f=>f.pop()],['wrong identity version',f=>f[0].version='v0'],['wrong first tag',f=>f[2].observed.firstHostCase='other'],
 ['missing check',f=>f[1].observed.checks.pop()],['wrong call',f=>f[2].ordinal=1],['false summary',f=>f[4].passed=false],
 ['invented ownership',f=>f[4].physicalStoreOrNativeOwnerIdentityProved=true],['wrong final cleanup',f=>f[4].finalCleanup.workloadPendingAfterClear=1],
])test('oracle DATA refusal '+name,()=>{const f=raw.trim().split('\n').map(x=>JSON.parse(x));change(f);assert.throws(()=>parseOracle(f.map(x=>JSON.stringify(x)).join('\n'),contract));});
// ACTUAL collector loop text, with inert in-memory transport/file/signal functions.
const text=await readFile(new URL('./collect.mjs',import.meta.url),'utf8');
const loop=text.slice(text.indexOf(' for(let call=1;call<=3;call++){'),text.indexOf(' result.allThreeCaptureAttemptsComplete='));
assert(loop.startsWith(' for(let call=1;call<=3;call++){')&&loop.endsWith(' }\n'));
const runLoop=compileFunction('return(async()=>{'+loop+';return result;})();',['result','fetch','origin','writeFile','row','join','output','errorData','save','assessSafety','readFile','contract','AbortSignal','plan','a']);
async function loopTest(name,failCall,transport=false){
 const result={responses:[]},files=new Map(),snapshots=[],decisions=[];let fetches=0;
 const fetch=async url=>{fetches++;assert.equal(url,'http://pure-data.invalid/unref-reuse?phase='+['A','B','C'][fetches-1]+'&case='+hostCase);if(transport&&fetches===failCall)throw Error('inert transport failure');const v=envelope(fetches);if(fetches===failCall)delete v.collection.boundaryMode;const bytes=encoded(v);return{status:200,headers:new Map([['content-type','application/json']]),arrayBuffer:async()=>bytes.buffer};};
 const write=async(path,bytes)=>{assert(!files.has(path));files.set(path,new Uint8Array(bytes));};
 const row=async path=>({path,bytes:files.get(path).length,sha256:createHash('sha256').update(files.get(path)).digest('hex')});
 const save=async()=>snapshots.push(copy(result));
 const gate=(bytes,status,call,c,tag)=>{const path='/pure-data/response-'+call+'.body';assert(files.has(path));assert(snapshots.some(s=>s.responses[call-1]?.body?.path===path));const decision=assessSafety(bytes,status,call,c,tag);decisions.push(decision);return decision;};
 await runLoop(result,fetch,'http://pure-data.invalid',write,row,join,'/pure-data',e=>({message:String(e)}),save,gate,async p=>files.get(p),contract,{timeout(ms){assert.equal(ms,10000);return{inertTestSignal:true};}},{phases:['A','B','C']},{firstHostCase:hostCase});
 assert.equal(fetches,failCall??3);assert.equal(result.responses.length,fetches);
 if(failCall){assert.equal(result.discardOwnedServerRequired,true);assert.equal(result.safetyStop.call,failCall);if(!transport){assert.equal(decisions.at(-1).safeToReuse,false);assert(result.safetyStop.validationFailure);}}
 else{assert.equal(result.safetyStop,undefined);assert(decisions.every(d=>d.safeToReuse===true));}
 rows.push({name,passed:true});
}
await loopTest('actual capture loop refuses unsafe first before request2',1);
await loopTest('actual capture loop refuses unsafe second before request3',2);
await loopTest('actual capture loop retains unsafe third and refuses comparison',3);
await loopTest('actual capture loop stops on transport failure before request3',2,true);
await loopTest('actual capture loop retains all3 on Source safety success',undefined);
assert.equal(oracle.hostCallChecks,51);assert.equal(oracle.distinctCallbackChecks,9);
console.log(JSON.stringify({passed:true,pureDataCases:rows.length,hostCallChecksRead:51,hostDistinctCallbackChecksRead:9,
 cumulativeCallbackInventories:[0,7,9],syntheticNativeShapesOnly:true,oracleReexecuted:false,collectorInvoked:false,guestOrNetworkOrTimerWorkloadInvoked:false,rows}));
