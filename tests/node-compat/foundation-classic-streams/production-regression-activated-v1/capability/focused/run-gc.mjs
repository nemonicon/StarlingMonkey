import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {harness} from './harness.mjs';
import {hash} from './preflight.mjs';
const h=await harness({gcStress:true});assert.equal(h.metadata.entropyPolicy,'off');
const kernel=h.metadata.protectedAbortListenerPolicy.actualLayoutCompileCommands.filter(command=>command.includes('/builtins/node-compat/buffer.cpp'));
assert.equal(kernel.length,1);assert(kernel[0].split(/\s+/).includes('-DNODE_COMPAT_GC_STRESS=1'));
const oracle=JSON.parse(await readFile(new URL('./node-results.json',import.meta.url)));
const bundle=await h.bundle(join(h.here,'gc-component.mjs'),['node:buffer','node:events']);
const fixture=await h.build('abort_m11_gc',bundle.code),instance=await h.importFixture(fixture),calls=[];
function validate(value,count){assert.deepEqual(value,{calls:count,completed:8,receiver:true,contextRestored:true,disposalCalls:0,order:['ordinary','protected','ordinary-once','ordinary'],snapshot:{before:count===1?0:1,after:1},nestedOnceCases:oracle.nestedOnceCases});}
for(let count=1;count<=3;count++){const value=JSON.parse(await instance.run());validate(value,count);calls.push(value);}const fresh=h.freshHost(fixture);validate(fresh.observed,1);
const prefix="import{Buffer}from'node:buffer';import{addAbortListener}from'node:events';";
const loops="for(let i=0;i<8;i++){if(Buffer.from('00017fff80','hex').toString('hex')!=='00017fff80')throw Error('hex mismatch');completed++;}";
const initializer=prefix+"let completed=0;const c=new AbortController();addAbortListener(c.signal,()=>{throw{toString(){return'M11_ROOTED_AFTER_'+completed}}});c.abort();"+loops+"export function run(){return'must-not-return'}";
const initial=await h.expectInitialization('abort_m11_gc_latched_init',initializer,/M11_ROOTED_AFTER_8/);
const fatal=await h.fatal('abort_m11_gc_latched_fatal',prefix+"export function run(){let completed=0;const c=new AbortController();addAbortListener(c.signal,()=>{throw{toString(){return'M11_DEPLOYED_ROOTED_AFTER_'+completed}}});c.abort();"+loops+"return'must-not-return'}");
await h.finish();const report={state:'NEW_CLASSIC342_RELEASE_MOVING_GC_COMBINED_OWNER_GATE_PASSED',recordedAtUtc:new Date().toISOString(),...h.evidence,
 runnerSha256:hash(await readFile(fileURLToPath(import.meta.url))),actualKernelCommand:kernel[0],clean:{fixture,calls,freshWasmtime:fresh},initializer:initial,fatal,
 scope:'Existing Release Buffer kernel JS::NonIncrementalGC(Shrink) boundaries only; eight valid hex roundtrips per clean invocation with signal/protected/ordinary/once/disposers/receiver and callback values alive, then post-GC protected registration/disposal/nested once tests.',
 limits:['Combined owners/callback/key behavior is verified; the factory closure also owns the Symbol, so this does not isolate prototype-only Symbol liveness.','The initializer reports its first latched object after eight valid roundtrips; deployed fatal calls prove failure/discard, not thrown-object identity across WIT.','Event.currentTarget/this restoration is not ALS or AsyncResource propagation.','No DEBUG/OOM/fault/private GC metadata/raw memory/malformed ABI or old prototype path. No performance claim.']};
await h.save(report);console.log(JSON.stringify({state:report.state,engineSha256:report.engineSha256,retainedCalls:3,freshSuccessfulWasmtime:1,roundtripsPerCall:8,imports:fixture.emittedImports,output:h.output},null,2));
