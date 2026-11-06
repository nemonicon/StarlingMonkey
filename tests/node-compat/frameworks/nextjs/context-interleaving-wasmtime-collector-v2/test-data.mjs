// Pure retained/synthetic DATA mutations only, not ALS/timer/oracle execution.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {compileFunction} from 'node:vm';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {assessSafety as oldAssessSafety,validate as oldValidate} from '../context-interleaving-wasmtime-collector-v1/comparison.mjs';
import {assessSafety,validate,validateCollection,compare,parseOracle} from './comparison.mjs';
const contract=JSON.parse(await readFile(new URL('./control-contract.json',import.meta.url),'utf8')).controls;
const raw=await readFile(new URL('./retained-node-oracle.stdout.jsonl',import.meta.url),'utf8');
const oracle=parseOracle(raw,contract),rows=[];
const copy=x=>structuredClone(x);
function test(name,body){body();rows.push({name,passed:true});}
function envelope(call=1){const collection=copy(oracle.values[call-1]);collection.boundaryMode='actual-native-private-boundaries';return{schemaVersion:1,marker:'NEXT_NATIVE_CONTEXT_INTERLEAVING_V1',call,method:'GET',collection};}
const encoded=x=>new TextEncoder().encode(JSON.stringify(x));
for(let call=1;call<=3;call++)test('synthetic consumer shape from retained Node public DATA '+call,()=>{const value=envelope(call);assert.equal(validate(value,call,contract).assertions,153);assert(compare(value,oracle.values[call-1],call,contract).every(x=>x.classification==='matches-node-public-projection'));});
for(let i=0;i<5;i++)for(const bad of [false,0])test('literal boolean refusal '+contract[i].id+' '+bad,()=>{const value=envelope();value.collection.records[i].assertions[0].passed=bad;assert.throws(()=>validate(value,1,contract));assert.equal(assessSafety(encoded(value),200,1,contract).safeToReuse,false);});
let edgeTests=0;
for(let i=0;i<5;i++)for(const edge of contract[i].requiredEdges)test('partial-order reversal '+contract[i].id+' '+edge.join('<'),()=>{const value=envelope(),r=value.collection.records[i],a=r.events.indexOf(edge[0]),b=r.events.indexOf(edge[1]);[r.events[a],r.events[b]]=[r.events[b],r.events[a]];assert.throws(()=>validate(value,1,contract),/partial-order/);edgeTests++;});
test('independent event ordering is not a total-order gate',()=>{const value=envelope(),r=value.collection.records[0];let found=false;for(let i=0;i<r.events.length-1&&!found;i++){const changed=copy(value),events=changed.collection.records[0].events;[events[i],events[i+1]]=[events[i+1],events[i]];try{validate(changed,1,contract);assert(compare(changed,oracle.values[0],1,contract).every(x=>x.classification==='matches-node-public-projection'));found=true;}catch{}}assert(found);});
test('assertion ordering remains raw but public projection sorts it',()=>{const value=envelope();value.collection.records[0].assertions.reverse();assert(compare(value,oracle.values[0],1,contract).every(x=>x.classification==='matches-node-public-projection'));});
for(const[name,change]of [
 ['missing assertion',v=>v.collection.records[0].assertions.pop()],['renamed assertion',v=>v.collection.records[0].assertions[0].id='unknown'],
 ['duplicate assertion',v=>v.collection.records[0].assertions[0]=copy(v.collection.records[0].assertions[1])],['unknown event',v=>v.collection.records[0].events.push('unknown')],
 ['missing edge',v=>v.collection.records[0].requiredEdges.pop()],['wrong native mode',v=>v.collection.boundaryMode='node-public-empty-store-projection'],
 ['caller ordinal',v=>v.collection.call=2],['method',v=>v.method='POST'],['ownership overclaim',v=>v.collection.nativeOwnerIdentityOrTeardownProved=true],
 ['failure field cannot be filtered',v=>v.collection.records[0].error={type:'null'}],
])test('full validation refusal '+name,()=>{const value=envelope();change(value);assert.throws(()=>validate(value,1,contract));});
for(const passed of [false,0,null,undefined])test('failed/unknown safety gate '+String(passed),()=>{const value=envelope();value.collection.passed=passed;value.collection.error={type:'null'};const s=assessSafety(encoded(value),500,1,contract);assert.equal(s.safeToReuse,false);assert.deepEqual(s.envelope,JSON.parse(JSON.stringify(value)));});
test('positive self-report with failure field still discards',()=>{const value=envelope();value.collection.error={type:'boolean',value:false};assert.equal(assessSafety(encoded(value),200,1,contract).safeToReuse,false);});
test('malformed and invalid UTF8 refuse reuse',()=>{assert.equal(assessSafety(new TextEncoder().encode('{bad'),200,1,contract).safeToReuse,false);assert.equal(assessSafety(Uint8Array.of(255),200,1,contract).safeToReuse,false);});
test('wrong status and transport-envelope uncertainty refuse reuse',()=>{const v=envelope();assert.equal(assessSafety(encoded(v),503,1,contract).safeToReuse,false);v.marker='unknown';assert.equal(assessSafety(encoded(v),200,1,contract).safeToReuse,false);});
for(const[name,change]of [
 ['six frames not seven',f=>f.pop()],['wrong original variant',f=>f[0].variant='node-sealed-facade'],['bad original ordinal',f=>f[0].call=3],
 ['failed summary',f=>f[6].passed=false],['invented native parity',f=>f[6].nativeBoundaryParityClaimed=true],
 ['false facade assertion',f=>f[3].observed.records[0].assertions[0].passed=false],
])test('oracle refusal '+name,()=>{const f=raw.trim().split('\n').map(x=>JSON.parse(x));change(f);assert.throws(()=>parseOracle(f.map(x=>JSON.stringify(x)).join('\n'),contract));});
// Concrete old-pass/new-refuse witnesses from C's held-f35 review.
for(const[name,change]of [
 ['missing boundaryMode',v=>delete v.collection.boundaryMode],
 ['native owner overclaim',v=>v.collection.nativeOwnerIdentityOrTeardownProved=true],
 ['empty assertion inventory',v=>v.collection.records[0].assertions=[]],
 ['missing required edge',v=>v.collection.records[0].requiredEdges.pop()],
])test('actual V1 safety counterexample '+name,()=>{const v=envelope();change(v);assert.equal(oldAssessSafety(encoded(v),200,1).safeToReuse,true);assert.throws(()=>oldValidate(v,1,contract));assert.throws(()=>validate(v,1,contract));const a=assessSafety(encoded(v),200,1,contract);assert.equal(a.safeToReuse,false);assert.deepEqual(a.envelope,v);assert.equal(typeof a.validationFailure.message,'string');assert.equal(typeof a.validationFailure.stack,'string');});
for(const[name,change]of [
 ['wrong boundary',v=>v.collection.boundaryMode='node-public-empty-store-projection'],
 ['missing logical flag',v=>delete v.collection.logicalBranchesOnly],
 ['false logical flag',v=>v.collection.logicalBranchesOnly=false],
 ['missing HTTP scope flag',v=>delete v.collection.actualHttpResourceConcurrencyProved],
 ['true HTTP scope flag',v=>v.collection.actualHttpResourceConcurrencyProved=true],
 ['extra unknown scope',v=>v.collection.unknownScope=true],
 ['missing assertion',v=>v.collection.records[0].assertions.pop()],
 ['extra assertion ID',v=>v.collection.records[0].assertions.push({id:'unknown',passed:true})],
 ['reversed edge',v=>{const r=v.collection.records[0],[a,b]=r.requiredEdges[0],i=r.events.indexOf(a),j=r.events.indexOf(b);[r.events[i],r.events[j]]=[r.events[j],r.events[i]];}],
])test('strict safety and full validator refusal '+name,()=>{const v=envelope();change(v);assert.throws(()=>validate(v,1,contract));const a=assessSafety(encoded(v),200,1,contract);assert.equal(a.safeToReuse,false);assert(a.validationFailure);assert.deepEqual(a.envelope,v);});
test('valid envelope non200 still refuses',()=>{const v=envelope();validate(v,1,contract);assert.equal(assessSafety(encoded(v),500,1,contract).safeToReuse,false);});
test('absent protected contract refuses instead of allowing reuse',()=>{const a=assessSafety(encoded(envelope()),200,1,undefined);assert.equal(a.safeToReuse,false);assert(a.validationFailure);});
// Exercise the ACTUAL V2 capture-loop text with inert in-memory transport/files,
// no host network, filesystem writes, timer, server or oracle invocation. Only
// the loop is compiled; none of collect.mjs's action-bearing top level runs.
const collector=await readFile(new URL('./collect.mjs',import.meta.url),'utf8');
const loop=collector.slice(collector.indexOf(' for(let call=1;call<=3;call++){'),collector.indexOf(' result.allThreeCaptureAttemptsComplete='));
assert(loop.startsWith(' for(let call=1;call<=3;call++){')&&loop.endsWith(' }\n'));
const runLoop=compileFunction('return (async()=>{'+loop+';return result;})();',['result','fetch','origin','writeFile','row','join','output','errorData','save','assessSafety','readFile','contract','AbortSignal']);
async function loopTest(name,failedCall){
 const result={responses:[]},files=new Map(),snapshots=[],decisions=[];let fetches=0;
 const fetch=async url=>{fetches++;assert.equal(url,'http://pure-data.invalid/context-interleaving?call='+fetches);const v=envelope(fetches);if(fetches===failedCall)delete v.collection.boundaryMode;const bytes=encoded(v);return{status:200,headers:new Map([['content-type','application/json']]),arrayBuffer:async()=>bytes.buffer};};
 const write=async(path,bytes)=>{assert(!files.has(path));files.set(path,new Uint8Array(bytes));};
 const row=async path=>({path,bytes:files.get(path).length,sha256:createHash('sha256').update(files.get(path)).digest('hex')});
 const save=async()=>snapshots.push(copy(result));
 const gate=(bytes,status,call,c)=>{const path='/pure-data/response-'+call+'.body';assert(files.has(path));assert(snapshots.some(s=>s.responses[call-1]?.body?.path===path));const a=assessSafety(bytes,status,call,c);decisions.push(a);return a;};
 await runLoop(result,fetch,'http://pure-data.invalid',write,row,join,'/pure-data',e=>({message:String(e)}),save,gate,async path=>files.get(path),contract,{timeout(ms){assert.equal(ms,10000);return{inertTestSignal:true};}});
 assert.equal(fetches,failedCall??3);assert.equal(result.responses.length,fetches);
 if(failedCall){assert.equal(result.discardOwnedServerRequired,true);assert.equal(result.safetyStop.call,failedCall);assert(result.safetyStop.validationFailure);assert.equal(decisions.at(-1).safeToReuse,false);}
 else{assert.equal(result.safetyStop,undefined);assert(decisions.every(x=>x.safeToReuse));}
 rows.push({name,passed:true});
}
await loopTest('actual capture loop stops before second request on unknown first state',1);
await loopTest('actual capture loop stops before third request on unknown second state',2);
await loopTest('actual capture loop retains all three only on strict safety success',undefined);

assert.equal(oracle.hostAssertionsVerified,918);
console.log(JSON.stringify({schemaVersion:1,pureDataCases:rows.length,passed:rows.length,requiredEdgeReversals:edgeTests,hostAssertionsRead:918,syntheticNativeShapes:3,actualGuestAssertionsVerified:0,rows,oracleInvoked:false,collectorInvoked:false,guestInvoked:false}));
