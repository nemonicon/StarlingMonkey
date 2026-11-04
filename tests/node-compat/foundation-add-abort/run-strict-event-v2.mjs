// Acceptance for the separate strict-event candidate. Historical six-case
// initialization-diagnostic.mjs and its failure report remain unchanged.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeHarness,hash} from '../foundations/native-scalar-harness.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const h=await nativeHarness({kind:'strict-event-v2',here,enabledField:'eventsEnabled',option:'NODE_COMPAT_EVENTS',outputVariable:'NODE_COMPAT_STRICT_EVENT_OUTPUT'});
assert.equal(h.metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
assert.equal(h.metadata.strictInitialization,true);assert.equal(h.metadata.oomTesting,false);
const patchSha256=hash(await readFile(join(here,'strict-event-v2.patch')));
assert.equal(h.metadata.strictEventExceptionPolicy?.patchSha256,patchSha256);
assert.equal(h.metadata.strictEventExceptionPolicy?.version,'sm-uncaught-event-v2');
const prefix="import {spawn} from 'node:child_process';\n";
const vectors=[
 ['direct','spawn();',true,/child_process\.spawn/],
 ['event-target-sync',"const t=new EventTarget();t.addEventListener('test',()=>{calls++;spawn();});t.dispatchEvent(new Event('test'));",true,/child_process\.spawn/],
 ['abort-signal-sync',"const c=new AbortController();c.signal.addEventListener('abort',()=>{calls++;spawn();});c.abort();",true,/child_process\.spawn/],
 ['event-target-async',"const t=new EventTarget();t.addEventListener('test',async()=>{calls++;spawn();});t.dispatchEvent(new Event('test'));",true,/child_process\.spawn|ERR_SM_NODE_INITIALIZATION_REJECTION/],
 ['queue-microtask','queueMicrotask(()=>{calls++;spawn();});',true,/child_process\.spawn|ERR_SM_NODE_INITIALIZATION_REJECTION/],
 ['explicitly-handled-event',"const t=new EventTarget();t.addEventListener('test',()=>{calls++;try{spawn();}catch(error){handled=error.code;}});t.dispatchEvent(new Event('test'));",false],
 ['plain-event-error',"const t=new EventTarget();t.addEventListener('test',()=>{throw new Error('PLAIN_EVENT_FIRST')});t.dispatchEvent(new Event('test'));",true,/PLAIN_EVENT_FIRST/],
 ['undefined-event-error',"const t=new EventTarget();t.addEventListener('test',()=>{throw undefined});t.dispatchEvent(new Event('test'));",true,/undefined/],
 ['null-event-error',"const t=new EventTarget();t.addEventListener('test',()=>{throw null});t.dispatchEvent(new Event('test'));",true,/null/],
 ['number-event-error',"const t=new EventTarget();t.addEventListener('test',()=>{throw 73021});t.dispatchEvent(new Event('test'));",true,/73021/],
 ['first-event-wins',"const t=new EventTarget();t.addEventListener('test',()=>{throw new Error('EVENT_ONE_FIRST')});t.addEventListener('test',()=>{throw new Error('EVENT_TWO_LATER')});t.dispatchEvent(new Event('test'));",true,/EVENT_ONE_FIRST/],
 ['event-error-from-job',"await Promise.resolve().then(()=>{const t=new EventTarget();t.addEventListener('test',()=>{spawn()});t.dispatchEvent(new Event('test'));});",true,/child_process\.spawn/],
 ['later-module-rejection',"const t=new EventTarget();t.addEventListener('test',()=>{throw new Error('LATCHED_EVENT')});t.dispatchEvent(new Event('test'));throw new Error('LATER_MODULE_REJECTION');",true,/LATCHED_EVENT/],
 ['finalizer-event-error',"const registry=new FinalizationRegistry(()=>{const t=new EventTarget();t.addEventListener('test',()=>spawn());t.dispatchEvent(new Event('test'));});function register(){registry.register({},0)}register();",true,/child_process\.spawn/],
 ['caught-primitive-event',"const t=new EventTarget();t.addEventListener('test',()=>{calls++;try{throw undefined}catch(error){handled=error===undefined?'caught-undefined':'bad'}});t.dispatchEvent(new Event('test'));",false],
 ['no-event-error','calls++;handled=\'clean\';',false],
];
const initialization=[];
for(const[name,body,reject,marker]of vectors){
 const source=prefix+'let calls=0,handled=null;\n'+body+"\nexport function run(){return JSON.stringify({calls,handled});}\n";
 let error,fixture;try{fixture=await h.build(name.replaceAll('-','_'),source);}catch(failure){error=failure.message;}
 assert.equal(!!error,reject,name);if(error&&marker)assert.match(error,marker,name);
 const record={name,source,sourceSha256:hash(source),rejected:!!error,error};
 if(fixture){const instance=await h.importFixture(fixture);record.fixture=fixture;record.calls=[JSON.parse(await instance.run()),JSON.parse(await instance.run())];record.wasmtime=h.runHost(fixture);assert.deepEqual(record.calls[0],record.calls[1]);assert.deepEqual(record.calls[0],record.wasmtime.observed);assert.deepEqual(record.calls[0],{calls:1,handled:name==='explicitly-handled-event'?'ERR_SM_NODE_UNSUPPORTED':name==='caught-primitive-event'?'caught-undefined':'clean'});}
 initialization.push(record);console.log(JSON.stringify({name,rejected:!!error}));
}
// A successful instance remains reusable; failures use isolated fresh child
// processes/host invocations and the instance is always discarded afterwards.
const cleanSource="let calls=0;export function run(){let seen=0,caught=false;const t=new EventTarget();t.addEventListener('test',()=>{seen++;try{throw undefined}catch(error){caught=error===undefined}});t.dispatchEvent(new Event('test'));return JSON.stringify({calls:++calls,seen,caught})}";
const cleanFixture=await h.build('deployed_caught_reuse',cleanSource),cleanInstance=await h.importFixture(cleanFixture),cleanCalls=[];
for(let call=1;call<=3;call++){const report=JSON.parse(await cleanInstance.run());assert.deepEqual(report,{calls:call,seen:1,caught:true});cleanCalls.push(report);}const cleanHost=h.runHost(cleanFixture);assert.deepEqual(cleanHost.observed,{calls:1,seen:1,caught:true});
const successfulReuse={fixture:cleanFixture,calls:cleanCalls,wasmtime:cleanHost};
const deployed=[];
for(const[name,thrown]of [['error',"new Error('DEPLOYED_EVENT_ERROR')"],['undefined','undefined'],['number','90217']]){
 const source=`export function run(){const t=new EventTarget();t.addEventListener('test',()=>{throw ${thrown}});t.dispatchEvent(new Event('test'));return 'must-not-return';}`;
 const fixture=await h.build('deployed_'+name,source);
 const childPath=join(h.output,'invoke-'+name+'.mjs');await writeFile(childPath,`import{run}from${JSON.stringify(fixture.modulePath)};try{await run();console.log('UNEXPECTED_SUCCESS');process.exitCode=2;}catch(error){console.log('EXPECTED_FATAL_EXPORT');}`);
 const child=spawnSync(process.execPath,[childPath],{encoding:'utf8',timeout:120000,maxBuffer:2*1024*1024});assert.equal(child.status,0,child.stderr);assert.match(child.stdout,/EXPECTED_FATAL_EXPORT/);assert.doesNotMatch(child.stdout,/UNEXPECTED_SUCCESS/);
 const host=spawnSync(process.env.NODE_COMPAT_WASMTIME,['run','--invoke','run()',fixture.componentPath],{encoding:'utf8',timeout:120000,maxBuffer:2*1024*1024});assert.notEqual(host.status,0);assert.doesNotMatch(host.stdout,/must-not-return/);
 deployed.push({name,fixture,jcoChild:{status:child.status,stdout:child.stdout,stderr:child.stderr},wasmtime:{status:host.status,stdout:host.stdout,stderr:host.stderr},policy:'Uncaught exported event failure is terminal; component instance discarded, never reused'});
 console.log(JSON.stringify({deployed:name,rejectedOnBothHosts:true}));
}
const report={schemaVersion:1,state:'private-strict-event-v2-release-acceptance-passed',recordedAtUtc:new Date().toISOString(),...h.evidence,patchSha256,runnerSha256:hash(await readFile(fileURLToPath(import.meta.url))),initialization,successfulReuse,deployed,limitations:['Private candidate only; shared production sources unchanged.','Value-only latch preserves thrown values, not the separate ExceptionStack; existing pending direct exceptions take precedence.','Capture-failure path is source-reviewed and not fault-injected.','No protected-listener/addAbortListener implementation, complete Node process/nextTick reporting or request cleanup/ALS support is implied.','Failed exports require discard; successful retained invocations do not claim safe reuse after a fatal export.','Explicit Engine::reset is source-reviewed only: no current public guest/WIT entry invokes it. Moving-GC lifetime is a separate gate.','Ordinary Release only; no DEBUG/fault/private runtime memory observation or malformed ABI carrier.']};
await writeFile(join(h.output,'strict-event-v2-results.json'),JSON.stringify(report,null,2)+'\n');await writeFile(join(here,'strict-event-v2-results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({state:report.state,initializationCases:initialization.length,deployedCases:deployed.length,output:h.output,imports:[]}));
