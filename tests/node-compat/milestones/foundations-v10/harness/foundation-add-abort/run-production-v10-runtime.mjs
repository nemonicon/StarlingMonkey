import {verifyProductionV10} from './production-v10-preflight.mjs';
// Production v10 boundary acceptance for the unchanged v1 observations and
// ordinary caught/handled-later controls. Each fatal instance is discarded.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeHarness,hash} from '../foundations/native-scalar-harness.mjs';
const productionPreflight=await verifyProductionV10();
const here=dirname(fileURLToPath(import.meta.url));
const h=await nativeHarness({kind:'production-v10-runtime',here,enabledField:'eventsEnabled',option:'NODE_COMPAT_EVENTS',outputVariable:'NODE_COMPAT_STRICT_EVENT_OUTPUT'});
assert.equal(h.metadata.strictEventExceptionPolicy?.version,'sm-uncaught-event-v3-protected-abort-v2');
assert.equal(h.metadata.strictEventExceptionPolicy.deployedUnhandledRejections,'fatal-after-drained-jobs-before-result-marshalling');
assert.equal(h.metadata.strictEventExceptionPolicy?.embeddingBoundaryPatchSha256,hash(await readFile(join(here,'componentize-strict-event-boundary-v2.patch'))));
const previous=JSON.parse(await readFile(join(here,'runtime-async-observation-results.json'))),fatal=[];
const cases=previous.results.map(x=>({name:x.name,source:x.source,unchangedV1SourceSha256:x.sourceSha256}));
cases.push({name:'unsupported-async-event',source:"import{spawn}from'node:child_process';export async function run(){const t=new EventTarget();t.addEventListener('test',async()=>spawn());t.dispatchEvent(new Event('test'));await Promise.resolve();return'unexpected'}"});
cases.push({name:'unsupported-microtask',source:"import{spawn}from'node:child_process';export async function run(){queueMicrotask(()=>spawn());await Promise.resolve();return'unexpected'}"});
cases.push({name:'unhandled-promise',source:"export async function run(){Promise.reject(new Error('UNHANDLED_RUNTIME_V2'));await Promise.resolve();return'unexpected'}"});
for(const vector of cases){
 if(vector.unchangedV1SourceSha256)assert.equal(hash(vector.source),vector.unchangedV1SourceSha256);
 const fixture=await h.build(vector.name.replaceAll('-','_'),vector.source),childPath=join(h.output,'invoke-'+vector.name+'.mjs');
 await writeFile(childPath,`import{run}from${JSON.stringify(fixture.modulePath)};try{await run();console.log('UNEXPECTED_SUCCESS');process.exitCode=2;}catch(error){console.log('EXPECTED_FATAL_EXPORT');}`);
 const child=spawnSync(process.execPath,[childPath],{encoding:'utf8',timeout:120000,maxBuffer:2*1024*1024});assert.equal(child.status,0,child.stderr);assert.match(child.stdout,/EXPECTED_FATAL_EXPORT/);assert.doesNotMatch(child.stdout,/UNEXPECTED_SUCCESS/);
 const host=spawnSync(process.env.NODE_COMPAT_WASMTIME,['run','--invoke','run()',fixture.componentPath],{encoding:'utf8',timeout:120000,maxBuffer:2*1024*1024});assert.notEqual(host.status,0);
 fatal.push({...vector,fixture,jcoChild:{status:child.status,stdout:child.stdout,stderr:child.stderr},wasmtime:{status:host.status,stdout:host.stdout,stderr:host.stderr},instancePolicy:'fatal/discard'});console.log(JSON.stringify({name:vector.name,fatalOnBothHosts:true}));
}
const controls=[];
for(const[name,body,expected]of[
 ['caught-async-event',"const t=new EventTarget();t.addEventListener('test',async()=>{seen++;try{throw new Error('caught')}catch(error){handled=error.message}});t.dispatchEvent(new Event('test'));",{seen:1,handled:'caught'}],
 ['caught-microtask',"queueMicrotask(()=>{seen++;try{throw undefined}catch(error){handled=error===undefined?'caught-undefined':'bad'}});",{seen:1,handled:'caught-undefined'}],
 ['handled-later-microtask',"const p=Promise.reject(new Error('handled-later'));queueMicrotask(()=>p.catch(error=>{seen++;handled=error.message}));",{seen:1,handled:'handled-later'}],
 ['ordinary-clean',"seen++;handled='clean';",{seen:1,handled:'clean'}],
]){
 const source="let calls=0;export async function run(){let seen=0,handled=null;"+body+"await Promise.resolve();await Promise.resolve();return JSON.stringify({calls:++calls,seen,handled})}";
 const fixture=await h.build(name.replaceAll('-','_'),source),instance=await h.importFixture(fixture),calls=[];for(let call=1;call<=3;call++){const result=JSON.parse(await instance.run());assert.deepEqual(result,{calls:call,...expected});calls.push(result);}const host=h.runHost(fixture);assert.deepEqual(host.observed,{calls:1,...expected});controls.push({name,fixture,calls,wasmtime:host});console.log(JSON.stringify({name,retainedCalls:3,freshWasmtime:true}));
}
const report={schemaVersion:1,productionPreflight,state:'production-v10-runtime-unhandled-boundary-acceptance-passed',recordedAtUtc:new Date().toISOString(),...h.evidence,runnerSha256:hash(await readFile(fileURLToPath(import.meta.url))),previousObservationSha256:hash(await readFile(join(here,'runtime-async-observation-results.json'))),fatal,controls,limitations:['Default selected-profile fatal/discard policy after all current jobs/finalizers and before returning/marshalling; not full Node process.on/unhandledRejection/async-hooks semantics.','Two original v1 observation sources are byte-identical; original v1 artifacts/reports unchanged.','Import-free components expose terminal traps at fatal boundaries; guest ERR_SM_NODE_EXECUTION_REJECTION is source-defined, with original reasons available only through a selected diagnostic reporting path.','Internal invocation/capture-failure flags are source-reviewed and not fault-injected; explicit Engine reset/cross-realm/owner teardown remain untested.','Ordinary Release only; no DEBUG/OOM/private guest memory/malformed ABI input.']};
await writeFile(join(h.output,'production-v10-runtime-results.json'),JSON.stringify(report,null,2)+'\n');await writeFile(join(here,'production-v10-runtime-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({state:report.state,fatalCases:fatal.length,retainedControlCases:controls.length,imports:[]}));
