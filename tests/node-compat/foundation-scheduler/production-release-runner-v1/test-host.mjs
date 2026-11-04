// Host-only source/negative-entry checks and redirected bounded Node oracles.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {runSerial,rejectResume} from './serial.mjs';
import {releaseJobs} from './job-plan.mjs';
import {controlEnvironment,validateModuleReport} from './preflight.mjs';
import {verifyInputClosure} from '../production-regression-candidate-v3/preflight.mjs';
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
const entries=['run-path','run-events','run-string-decoder','run-assert','run-querystring','run-util','run-optional','run-release'];
for(const name of entries){
 const childOutput=join(scratch,name),environment={...process.env,NODE_COMPAT_ENGINE:'/NO_ENGINE_MUST_BE_READ',NODE_COMPAT_ENGINE_SOURCE_ROOT:'/NO_SOURCE_MUST_BE_READ',NODE_COMPAT_WASMTIME:'/NO_HOST_MUST_BE_RUN',NODE_COMPAT_TOOLCHAIN:'/NO_TOOLCHAIN_MUST_LOAD',NODE_COMPAT_PRODUCTION_RELEASE_OUTPUT:childOutput,NODE_COMPAT_OPTIONAL_OUTPUT:childOutput};
 for(const module of ['PATH','EVENTS','STRING_DECODER','ASSERT','QUERYSTRING','UTIL'])environment['NODE_COMPAT_'+module+'_OUTPUT']=childOutput;
 delete environment.NODE_OPTIONS;
 const result=spawnSync(process.execPath,[join(here,name+'.mjs')],{encoding:'utf8',env:environment,timeout:10000,maxBuffer:1024*1024});
 await writeFile(join(output,name+'.negative.log'),result.stderr);
 test('null pins before loader/output '+name,()=>{assert.notEqual(result.status,0);assert.match(result.stderr,/Actual production pins are unconfigured/);assert(!/ENOENT|MODULE_NOT_FOUND|ERR_MODULE_NOT_FOUND/.test(result.stderr));});
 try{await lstat(childOutput);assert.fail('Null pins created output');}catch(error){assert.equal(error.code,'ENOENT');}
}

const preserved=JSON.parse(await readFile(join(here,'input-freeze.json'))).preservedOldOutputs;
for(const row of preserved)assert.equal(hash(await readFile(join(repository,row.path))),row.sha256);
const oracleOutput=join(output,'path-oracles');await mkdir(oracleOutput);
const oracleRuns=[];
for(const[file,flags]of [['semantic.mjs',[]],['glob.mjs',['--expose-internals']]]){
 const result=spawnSync(process.execPath,[...flags,join(here,'oracles',file)],{encoding:'utf8',env:{...process.env,NODE_COMPAT_PATH_ORACLE_OUTPUT:oracleOutput},timeout:30000,maxBuffer:4*1024*1024});
 await writeFile(join(output,file+'.stdout'),result.stdout);await writeFile(join(output,file+'.stderr'),result.stderr);
 assert.equal(result.status,0,result.stderr||result.stdout);oracleRuns.push({file,flags,status:result.status,stdout:result.stdout,stderr:result.stderr});
 checks.push({name:'complete redirected bounded Node Path oracle '+file,passed:true});
}
const oracleFiles=[];
for(const name of ['lexical-vectors.json','semantic-results.json','glob-vectors.json','glob-differences.json','glob-results.json']){
 const bytes=await readFile(join(oracleOutput,name)),old=await readFile(join(repository,'tests/node-compat/foundation-path',name));
 test('redirected oracle bytes match preserved output '+name,()=>assert.equal(hash(bytes),hash(old)));
 oracleFiles.push({path:join(oracleOutput,name),sha256:hash(bytes),bytes:bytes.length});
}
for(const row of preserved)assert.equal(hash(await readFile(join(repository,row.path))),row.sha256);
const report={schemaVersion:1,state:'HOST_ONLY_RELEASE_RUNNER_PREPARATION_CHECKS_PASSED',node:process.version,nodeSha256:hash(await readFile(process.execPath)),
 tests:checks.length,passed:checks.length,checks,negativeEntries:8,oracleRuns,oracleFiles,preservedOldOutputsUnchanged:preserved,
 generatedFilesReverseToOriginal:transformations.files.length,
 actualProductionPinsExist:false,positiveFixedArtifactPathExecuted:false,oldReportsReusedAsRuntimePasses:false,
 compilerToolchainComponentizerWasmtimeOrGuestRun:false,scope:'Source proof, negative entry children, pure serial/control/report checks and original bounded Node Path oracles only'};
await writeFile(reportPath,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,tests:checks.length,negativeEntries:8,pathOracles:2,reportPath}));
