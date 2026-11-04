// Host-only source/negative-entry checks and redirected bounded Node oracles.
import {selectActualPin} from '../production-regression-candidate-v5/admission.mjs';
import assert from 'node:assert/strict';
import {selectDependencyIndex} from '../production-regression-candidate-v5/dependency-bindings.mjs';
import {readFile,writeFile,mkdir,lstat} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {runSerial,rejectResume} from './serial.mjs';
import {releaseJobs} from './job-plan.mjs';
import {controlEnvironment,validateModuleReport} from './preflight.mjs';
import {verifyInputClosure} from '../production-regression-candidate-v5/preflight.mjs';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
assert(process.env.NODE_COMPAT_RELEASE_HOST_TEST_OUTPUT,'Explicit fresh report output required');
const here=dirname(fileURLToPath(import.meta.url)),repository=resolve(here,'../../../..');
const reportPath=resolve(process.env.NODE_COMPAT_RELEASE_HOST_TEST_OUTPUT),output=dirname(reportPath);
assert(output.startsWith('/tmp/starling-node-compat/'));await mkdir(output,{recursive:true});
try{await lstat(reportPath);assert.fail('Fresh report path required');}catch(error){if(error.code!=='ENOENT')throw error;}
const scratch=join(output,'scratch');await mkdir(scratch);
const hash=bytes=>createHash('sha256').update(bytes).digest('hex'),checks=[];
function test(name,fn){fn();checks.push({name,passed:true});}
async function asyncTest(name,fn){await fn();checks.push({name,passed:true});}
const transformations=JSON.parse(await readFile(join(here,'runner-transformations.json')));
for(const row of transformations.files){
 let restored=await readFile(join(here,row.generated),'utf8');assert.equal(hash(restored),row.generatedSha256);
 for(const change of [...row.changes].reverse()){assert.equal(restored.split(change.after).length-1,change.count);restored=restored.split(change.after).join(change.before);}
 test('reverse all declared edits '+row.generated,()=>assert.equal(hash(restored),row.originalSha256));
 assert.equal(hash(await readFile(join(repository,row.original))),row.originalSha256);
}
const jobs=releaseJobs(here,join(scratch,'batch'));
test('exact serial eight-job plan',()=>assert.deepEqual(jobs.map(x=>x.name),['core','allocator','stream-web','optional','strict-sync','strict-runtime','strict-late','strict-callbacks']));
test('singular callback report and complete seals retained',()=>{assert.equal(jobs[7].report,'private-ticks-callback-results.json');assert(jobs.every(x=>x.completion));});
await asyncTest('serial execution never overlaps',async()=>{
 let active=0,peak=0;const order=[];
 const result=await runSerial([{name:'a'},{name:'b'},{name:'c'}],async job=>{active++;peak=Math.max(peak,active);order.push(job.name);await Promise.resolve();active--;return{code:0};});
 assert.equal(peak,1);assert.equal(result.length,3);assert.deepEqual(order,['a','b','c']);
});
await asyncTest('first failed job stops all later jobs',async()=>{const order=[];await runSerial([{name:'a'},{name:'b'},{name:'c'}],async job=>{order.push(job.name);return{code:job.name==='b'?1:0};});assert.deepEqual(order,['a','b']);});
await asyncTest('thrown job does not start next',async()=>{const order=[];await assert.rejects(runSerial([{name:'a'},{name:'b'}],async job=>{order.push(job.name);throw new Error('owned-test');}),/owned-test/);assert.deepEqual(order,['a']);});
for(const variable of ['NODE_COMPAT_RELEASE_RESUME','NODE_COMPAT_OPTIONAL_RESUME','NODE_COMPAT_RESUME'])test('no resume '+variable,()=>assert.throws(()=>rejectResume({[variable]:'1'})));
const dataPath=join(scratch,'seal-data.txt'),manifestPath=join(scratch,'seal-inputs.json');
const data=Buffer.from('owned ordinary host text');await writeFile(dataPath,data);
await writeFile(manifestPath,JSON.stringify({schemaVersion:1,inputs:[{path:'seal-data.txt',sha256:hash(data),bytes:data.length}]}));
const seal=await verifyInputClosure({manifestPath}),expectedSha256=seal.sha256;
await asyncTest('captured local seal accepts identical owned data',async()=>assert.equal((await verifyInputClosure({manifestPath,expectedSha256})).sha256,expectedSha256));
await writeFile(manifestPath,'not JSON');
await asyncTest('local seal digest checked before parsing replacement',async()=>assert.rejects(verifyInputClosure({manifestPath,expectedSha256}),/Runtime input manifest changed/));
await writeFile(manifestPath,JSON.stringify({schemaVersion:1,inputs:[{path:'NEVER_FOLLOW_THIS_MISSING_ROW',sha256:hash(data),bytes:data.length}]}));
await asyncTest('local seal digest checked before following replacement rows',async()=>assert.rejects(verifyInputClosure({manifestPath,expectedSha256}),/Runtime input manifest changed/));
const controls=JSON.parse(await readFile(join(here,'historical-controls.json')));
for(const name of ['assert','querystring','util'])test('required historical OFF selection '+name,()=>{const environment={};const selected=controlEnvironment(name,controls,environment);assert.equal(selected.engine,controls.modules[name].engine);assert.equal(Object.keys(environment).length,2);});
test('Events OFF remains opt-in as in old six replay',()=>assert.equal(controlEnvironment('events',controls,{}),null));
test('unknown historical control override rejected',()=>assert.throws(()=>controlEnvironment('assert',controls,{NODE_COMPAT_ASSERT_OFF_ENGINE:'/NOT_AN_ADMITTED_CONTROL'})));
test('Path has no invented optional-OFF flag',()=>assert.throws(()=>controlEnvironment('path',controls,{NODE_COMPAT_PATH_OFF_ENGINE:'/NO'})));
for(const name of ['path','events','string-decoder','assert','querystring','util']){
 const original=join(repository,'tests/node-compat/foundation-'+name,name==='path'?'results.json':'native-component-results.json');
 
const report=JSON.parse(await readFile(original));
 test('historical report parser shape only '+name,()=>assert(validateModuleReport(name,report,report.engineSha256).finalComponentAudits>0));
 test('report parser rejects wrong engine '+name,()=>assert.throws(()=>validateModuleReport(name,report,'NOT_AN_ENGINE_HASH')));
}
const preserved=JSON.parse(await readFile(join(here,'history/predecessor/input-freeze.json'))).preservedOldOutputs;
for(const row of preserved)assert.equal(hash(await readFile(join(repository,row.path))),row.sha256);
// Original oracle source bytes and expected outputs remain pinned by predecessor records.
// Do not execute oracle/runner mains as part of activation host preparation.
const oracleRuns=[],oracleFiles=[];
for(const row of preserved)assert.equal(hash(await readFile(join(repository,row.path))),row.sha256);
// OWN scratch selector inputs; these tests never inspect or rewrite current pin files.
for(const document of [null,[],{},
 {schemaVersion:1,state:'UNREVIEWED_PRODUCTION_PIN_CANDIDATES_V1',variants:{'normal-off':{state:'unreviewed-production-freeze-pin-candidate'}}},
 {schemaVersion:1,state:'UNCONFIGURED_ACTUAL_PRODUCTION_FREEZES_REQUIRED',variants:{'normal-off':null}}])
 test('scratch malformed/null/unreviewed production selector '+JSON.stringify(document),()=>assert.throws(()=>selectActualPin(document,{gcStress:false})));
for(const document of [null,{},
 {schemaVersion:1,state:'UNCONFIGURED_SEALED_PARENT_INDICES_REQUIRED',commonIndexSha256:null},
 {schemaVersion:1,state:'REVIEWED_SEALED_PARENT_INDICES_V1',commonIndexSha256:null},
 {schemaVersion:1,state:'REVIEWED_SEALED_PARENT_INDICES_V1',commonIndexSha256:'not-a-digest'},
 {schemaVersion:1,state:'REVIEWED_SEALED_PARENT_INDICES_V1',commonIndexSha256:'0'.repeat(64)}])
 test('scratch unresolved/malformed dependency binding '+JSON.stringify(document),()=>assert.throws(()=>selectDependencyIndex(document,'commonIndexSha256')));
const report={schemaVersion:1,state:'HOST_ONLY_ACTIVATION_RELEASE_SOURCE_CHECKS_PASSED',node:process.version,nodeSha256:hash(await readFile(process.execPath)),
 tests:checks.length,passed:checks.length,checks,negativeEntries:0,oracleRuns,oracleFiles,preservedOldOutputsUnchanged:preserved,
 generatedFilesReverseToOriginal:transformations.files.length,
 checkedInPinsUsedByNegativeTests:false,positiveFixedArtifactPathExecuted:false,oldReportsReusedAsRuntimePasses:false,
 compilerToolchainComponentizerWasmtimeOrGuestRun:false,scope:'Source proof, pure serial/control/report/source checks; no main or Node oracle executed'};
await writeFile(reportPath,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,tests:checks.length,negativeEntries:0,pathOracles:0,reportPath}));
