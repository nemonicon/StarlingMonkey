// Ordinary Release/public-API diagnostic. This observes a policy gap; it does
// not install addAbortListener or change the exception/reporting mechanism.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeHarness,hash} from '../foundations/native-scalar-harness.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const h=await nativeHarness({kind:'add-abort',here,enabledField:'eventsEnabled',option:'NODE_COMPAT_EVENTS',outputVariable:'NODE_COMPAT_ADD_ABORT_OUTPUT'});
assert.equal(h.metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
assert.equal(h.metadata.observedCMakeOptions.WEVAL,'OFF');
assert.equal(h.metadata.strictInitialization,true);
assert.equal(h.metadata.oomTesting,false);
const prefix="import {spawn} from 'node:child_process';\n";
const vectors=[
  {name:'direct',body:'spawn();',mustReject:true},
  {name:'event-target-sync',body:"const t=new EventTarget();t.addEventListener('test',()=>{calls++;spawn();});t.dispatchEvent(new Event('test'));",mustReject:false,policyGap:true},
  {name:'abort-signal-sync',body:'const c=new AbortController();c.signal.addEventListener(\'abort\',()=>{calls++;spawn();});c.abort();',mustReject:false,policyGap:true},
  {name:'event-target-async',body:"const t=new EventTarget();t.addEventListener('test',async()=>{calls++;spawn();});t.dispatchEvent(new Event('test'));",mustReject:true},
  {name:'queue-microtask',body:'queueMicrotask(()=>{calls++;spawn();});',mustReject:true},
  {name:'explicitly-handled-event',body:"const t=new EventTarget();t.addEventListener('test',()=>{calls++;try{spawn();}catch(error){handled=error.code;}});t.dispatchEvent(new Event('test'));",mustReject:false},
];
const results=[];
for(const vector of vectors){
  const source=prefix+'let calls=0,handled=null;\n'+vector.body+"\nconst completedAfterDispatch=true;export function run(){return JSON.stringify({calls,handled,completedAfterDispatch});}\n";
  let fixture,error;
  try{fixture=await h.build(vector.name.replaceAll('-','_'),source);}catch(failure){error=failure.message;}
  const record={name:vector.name,source,sourceSha256:hash(source),expectedCurrentRejection:vector.mustReject,rejected:!!error,policyGap:!!vector.policyGap&&!error,error};
  assert.equal(record.rejected,vector.mustReject,vector.name+' changed: reassess and preserve the old diagnostic record');
  if(error)assert.match(error,/child_process\.spawn|ERR_SM_NODE_INITIALIZATION_REJECTION/);
  if(fixture){
    const instance=await h.importFixture(fixture);
    record.fixture=fixture;record.jco=JSON.parse(await instance.run());record.wasmtime=h.runHost(fixture);
    const expected={calls:1,handled:vector.name==='explicitly-handled-event'?'ERR_SM_NODE_UNSUPPORTED':null,completedAfterDispatch:true};
    assert.deepEqual(record.jco,expected);assert.deepEqual(record.wasmtime.observed,expected);
  }
  results.push(record);console.log(JSON.stringify({name:record.name,rejected:record.rejected,policyGap:record.policyGap}));
}
const runnerBytes=await readFile(fileURLToPath(import.meta.url));
const report={schemaVersion:1,state:'ordinary-release-initializer-event-exception-gap-reproduced',recordedAtUtc:new Date().toISOString(),...h.evidence,runnerSha256:hash(runnerBytes),results,
 limitations:['This diagnostic preserves current observed failures; it is not an addAbortListener implementation or acceptance gate.','Synchronous unhandled event callbacks are swallowed by the existing dispatcher even with strictInitialization=true; no production fix is installed.','All operations use valid public EventTarget/AbortSignal/Promise APIs; no DEBUG, fault simulation, private runtime binding, raw guest memory or malformed ABI input.','Accepted fixtures have zero imports and are invoked through ordinary string WIT exports in Jco and stock Wasmtime; rejected fixtures never instantiate.']};
await writeFile(join(h.output,'initialization-results.json'),JSON.stringify(report,null,2)+'\n');
await writeFile(join(here,'initialization-results.json'),JSON.stringify(report,null,2)+'\n');
await writeFile(join(h.output,'initialization-diagnostic.executed.mjs'),runnerBytes);
console.log(JSON.stringify({state:report.state,output:h.output,cases:results.length,policyGaps:results.filter(x=>x.policyGap).length}));
