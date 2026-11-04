// Pure/ordinary source-contract negatives; no workload run, artifact or loader.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import * as provider from './node-provider.mjs';
import {createWorkload,scenarioIds} from './workload.mjs';
const here=dirname(fileURLToPath(import.meta.url)),checks=[];
const pass=name=>checks.push(name),workload=createWorkload(provider);
assert.equal(scenarioIds.length,10);assert.equal(new Set(scenarioIds).size,10);pass('finite seven scenarios plus three controls');
assert.throws(()=>workload.setup('unknown'),/Unknown finite/);pass('unknown setup refused');
await assert.rejects(workload.run(1),/Use setup/);pass('run before setup refused');
workload.setup('pipeline-view-64');
for(const n of [0,17,-1,1.5,NaN,Infinity]){await assert.rejects(workload.run(n),/finite1..16/);pass('invalid iteration bound '+String(n));}
const source=await readFile(join(here,'workload.mjs'),'utf8');
assert(source.includes('events.length<4096'));assert(source.includes('callbacks<=128'));assert(source.includes('if(eof)return;while(index<chunks)'));pass('explicit trace/callback/EOF bounds');
assert(source.includes('Exact output byte mismatch')&&source.includes('Exact decoded text mismatch')&&source.includes('Exact object value/order mismatch'));pass('online exact output equality retained');
assert(!/Buffer\.(?:concat|copy)|\.fromWeb\(|\.toWeb\(/.test(source));pass('no deferred byte copy/concat or Web bridge calls');
const plan=JSON.parse(await readFile(join(here,'component-plan.json'))),pins=JSON.parse(await readFile(join(here,'future-pins.json')));
assert.equal(plan.reviewedNativePins,null);assert.equal(plan.reviewedComponentPins,null);assert.equal(pins.benchmarkClassicOn,null);assert.equal(pins.benchmarkClassicOff,null);assert.equal(plan.currentTimingAllowed,false);pass('future pins null and timing unavailable');
assert.equal(plan.callbackCheckpointLimit,65536);assert.equal(plan.budgetMayBeRaised,false);assert.equal(plan.actualGuestBudgetProof,false);pass('actual checkpoint cap retained; host counts are not guest proof');
const runner=await readFile(join(here,'run-node.mjs'),'utf8');assert(!runner.includes('assert.deepEqual(observed,oracle)'));assert(runner.includes('JSON.stringify(observed)!==JSON.stringify(oracle)'));pass('exact bounded data comparison avoids formatted large diff');
const bundle=await readFile(join(here,'bundle-source.mjs'),'utf8');assert(bundle.includes('nodeBuiltinPlugin({imports:[],exports:[]},{})'));assert(!bundle.includes('streamSchedulerModule:'));pass('actual Jco API/options preserve stock scheduler');
const output=resolve(process.env.NODE_COMPAT_CLASSIC_WORKLOAD_SOURCE_TEST_OUTPUT??'');assert(output.startsWith('/tmp/starling-node-compat/'));
const result={schemaVersion:1,state:'CLASSIC_WORKLOAD_SOURCE_CONTRACT_CHECKS_PASSED',checks:checks.length,passed:checks.length,observations:checks,
 workloadRunOrComponentOrGuestOrTargetHostExecuted:false,sourceSha256:createHash('sha256').update(source).digest('hex')};
await writeFile(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:result.state,checks:checks.length,output}));
