// Ordinary valid public fixtures, preserving v2 counterexamples before a fix.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeHarness,hash} from '../foundations/native-scalar-harness.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const h=await nativeHarness({kind:'strict-event-v2-counterexamples',here,enabledField:'eventsEnabled',option:'NODE_COMPAT_EVENTS',outputVariable:'NODE_COMPAT_STRICT_EVENT_OUTPUT'});
assert.equal(h.metadata.strictEventExceptionPolicy?.version,'sm-uncaught-event-v2');
const oracle=JSON.parse(await readFile(join(here,'node-callback-oracle-results.json'))),cases=[];
for(const[name,source,expected]of[
 ['registration-getter',"let reads=0,caught=false,registered=false;const t=new EventTarget();try{t.addEventListener('test',{get handleEvent(){reads++;throw new Error('GETTER_REGISTRATION')}});registered=true}catch(error){caught=error.message==='GETTER_REGISTRATION'}export function run(){return JSON.stringify({reads,caught,registered})}",{reads:0,caught:false,registered:true}],
 ['dispatch-getter',"let reads=0,armed=false,dispatchCaught=false,second=0;const t=new EventTarget();t.addEventListener('test',{get handleEvent(){reads++;if(armed)throw new Error('GETTER_DISPATCH');return()=>{}}});t.addEventListener('test',()=>second++);armed=true;try{t.dispatchEvent(new Event('test'))}catch{dispatchCaught=true}export function run(){return JSON.stringify({reads,dispatchCaught,second})}",{reads:1,dispatchCaught:true,second:0}],
 ['direct-finalizer',"import{spawn}from'node:child_process';let seen=0;const registry=new FinalizationRegistry(()=>{seen++;spawn()});function register(){registry.register({},0)}register();export function run(){return JSON.stringify({seen,componentizedDespiteUnsupportedCallback:true})}",{seen:1,componentizedDespiteUnsupportedCallback:true}],
]){
 const fixture=await h.build(name.replaceAll('-','_'),source),instance=await h.importFixture(fixture),calls=[];for(let call=0;call<2;call++){const observed=JSON.parse(await instance.run());assert.deepEqual(observed,expected);calls.push(observed);}const host=h.runHost(fixture);assert.deepEqual(host.observed,expected);
 cases.push({name,fixture,calls,wasmtime:host,nodeOracle:oracle.cases.find(x=>x.name===name),counterexample:true,comparisonScope:name==='direct-finalizer'?'Node throws a sentinel Error; guest calls an unsupported API. Comparison is callback error reporting, not identical error codes.':'Getter timing, caller catch behavior and continuation order use ordinary public EventTarget operations.'});console.log(JSON.stringify({name,componentizationAccepted:true,counterexample:true}));
}
const report={schemaVersion:1,state:'ordinary-v2-callback-policy-counterexamples-observed',recordedAtUtc:new Date().toISOString(),...h.evidence,runnerSha256:hash(await readFile(fileURLToPath(import.meta.url))),nodeOracleSha256:hash(await readFile(join(here,'node-callback-oracle-results.json'))),cases,limitations:['Known-gap observation, not a compatibility acceptance result or production fix.','Direct FinalizationRegistry callback error is still dumped and cleared during initialization; v2 does not constitute complete strict initialization.','Node reads object-listener handleEvent during validation and uses an async dispatch wrapper; Starling reads it at dispatch and propagates getter failure synchronously.','No fault/DEBUG/private guest memory/malformed ABI inputs; accepted components have zero imports.']};
await writeFile(join(h.output,'callback-counterexamples-v2-results.json'),JSON.stringify(report,null,2)+'\n');await writeFile(join(here,'callback-counterexamples-v2-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({state:report.state,cases:cases.length,imports:[]}));
