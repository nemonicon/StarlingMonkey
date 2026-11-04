// Existing deployed async-reporting behavior observed separately from v1's
// synchronous event exception acceptance. This is not a support claim.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeHarness,hash} from '../foundations/native-scalar-harness.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const h=await nativeHarness({kind:'strict-event-async-observation',here,enabledField:'eventsEnabled',option:'NODE_COMPAT_EVENTS',outputVariable:'NODE_COMPAT_STRICT_EVENT_OUTPUT'});
assert.equal(h.metadata.strictEventExceptionPolicy?.version,'sm-uncaught-event-v1');
const results=[];
for(const[name,body]of[
 ['async-event-listener',"const t=new EventTarget();t.addEventListener('test',async()=>{calls++;throw new Error('ASYNC_EVENT_UNCAUGHT')});t.dispatchEvent(new Event('test'));"],
 ['queue-microtask',"queueMicrotask(()=>{calls++;throw new Error('MICROTASK_UNCAUGHT')});"],
]){
 const source='export async function run(){let calls=0;'+body+"await Promise.resolve();return JSON.stringify({calls,returnedDespiteUnhandledAsyncError:true})}";
 const fixture=await h.build(name.replaceAll('-','_'),source),instance=await h.importFixture(fixture),calls=[];
 for(let i=0;i<2;i++){const result=JSON.parse(await instance.run());assert.deepEqual(result,{calls:1,returnedDespiteUnhandledAsyncError:true});calls.push(result);}const wasmtime=h.runHost(fixture);assert.deepEqual(wasmtime.observed,calls[0]);
 // Node's default whole-process outcome is a separate scope: a queued error
 // may occur after the function's own Promise has already fulfilled.
 const nodeSource='let calls=0;'+body+"await Promise.resolve();await new Promise(resolve=>setImmediate(resolve));console.log('UNEXPECTED_NODE_SURVIVAL');";
 const node=spawnSync(process.execPath,['--input-type=module','-e',nodeSource],{encoding:'utf8',timeout:10000,maxBuffer:1024*1024});assert.notEqual(node.status,0);assert.doesNotMatch(node.stdout,/UNEXPECTED_NODE_SURVIVAL/);assert.match(node.stderr,name==='queue-microtask'?/MICROTASK_UNCAUGHT/:/ASYNC_EVENT_UNCAUGHT/);
 results.push({name,source,sourceSha256:hash(source),fixture,calls,wasmtime,nodeDefaultProcess:{source:nodeSource,status:node.status,stdout:node.stdout,stderr:node.stderr},policyGap:true});
 console.log(JSON.stringify({name,guestReturned:true,nodeProcessFatal:true}));
}
const report={schemaVersion:1,state:'existing-runtime-async-error-policy-gaps-observed',recordedAtUtc:new Date().toISOString(),...h.evidence,runnerSha256:hash(await readFile(fileURLToPath(import.meta.url))),results,limitations:['Observation only; v1 fixes synchronous event exceptions, not all runtime unhandled Promise rejections.','Node default whole-process fatal outcome does not imply the individual async function Promise rejects; these are explicitly different scopes.','No production fix/addAbortListener implementation/native introspection/DEBUG/fault input. All final component imports are empty.']};
await writeFile(join(h.output,'runtime-async-observation-results.json'),JSON.stringify(report,null,2)+'\n');await writeFile(join(here,'runtime-async-observation-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({state:report.state,cases:results.length}));
