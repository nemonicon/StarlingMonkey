// Pure retained/synthetic DATA mutations only, not ALS/timer/oracle execution.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {assessSafety,validate,validateCollection,compare,parseOracle} from './comparison.mjs';
const contract=JSON.parse(await readFile(new URL('./control-contract.json',import.meta.url),'utf8')).controls;
const raw=await readFile(new URL('./retained-node-oracle.stdout.jsonl',import.meta.url),'utf8');
const oracle=parseOracle(raw,contract),rows=[];
const copy=x=>structuredClone(x);
function test(name,body){body();rows.push({name,passed:true});}
function envelope(call=1){const collection=copy(oracle.values[call-1]);collection.boundaryMode='actual-native-private-boundaries';return{schemaVersion:1,marker:'NEXT_NATIVE_CONTEXT_INTERLEAVING_V1',call,method:'GET',collection};}
const encoded=x=>new TextEncoder().encode(JSON.stringify(x));
for(let call=1;call<=3;call++)test('synthetic consumer shape from retained Node public DATA '+call,()=>{const value=envelope(call);assert.equal(validate(value,call,contract).assertions,153);assert(compare(value,oracle.values[call-1],call,contract).every(x=>x.classification==='matches-node-public-projection'));});
for(let i=0;i<5;i++)for(const bad of [false,0])test('literal boolean refusal '+contract[i].id+' '+bad,()=>{const value=envelope();value.collection.records[i].assertions[0].passed=bad;assert.throws(()=>validate(value,1,contract));assert.equal(assessSafety(encoded(value),200,1).safeToReuse,false);});
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
for(const passed of [false,0,null,undefined])test('failed/unknown safety gate '+String(passed),()=>{const value=envelope();value.collection.passed=passed;value.collection.error={type:'null'};const s=assessSafety(encoded(value),500,1);assert.equal(s.safeToReuse,false);assert.deepEqual(s.envelope,JSON.parse(JSON.stringify(value)));});
test('positive self-report with failure field still discards',()=>{const value=envelope();value.collection.error={type:'boolean',value:false};assert.equal(assessSafety(encoded(value),200,1).safeToReuse,false);});
test('malformed and invalid UTF8 refuse reuse',()=>{assert.equal(assessSafety(new TextEncoder().encode('{bad'),200,1).safeToReuse,false);assert.equal(assessSafety(Uint8Array.of(255),200,1).safeToReuse,false);});
test('wrong status and transport-envelope uncertainty refuse reuse',()=>{const v=envelope();assert.equal(assessSafety(encoded(v),503,1).safeToReuse,false);v.marker='unknown';assert.equal(assessSafety(encoded(v),200,1).safeToReuse,false);});
for(const[name,change]of [
 ['six frames not seven',f=>f.pop()],['wrong original variant',f=>f[0].variant='node-sealed-facade'],['bad original ordinal',f=>f[0].call=3],
 ['failed summary',f=>f[6].passed=false],['invented native parity',f=>f[6].nativeBoundaryParityClaimed=true],
 ['false facade assertion',f=>f[3].observed.records[0].assertions[0].passed=false],
])test('oracle refusal '+name,()=>{const f=raw.trim().split('\n').map(x=>JSON.parse(x));change(f);assert.throws(()=>parseOracle(f.map(x=>JSON.stringify(x)).join('\n'),contract));});
assert.equal(oracle.hostAssertionsVerified,918);
console.log(JSON.stringify({schemaVersion:1,pureDataCases:rows.length,passed:rows.length,requiredEdgeReversals:edgeTests,hostAssertionsRead:918,syntheticNativeShapes:3,actualGuestAssertionsVerified:0,rows,oracleInvoked:false,collectorInvoked:false,guestInvoked:false}));
