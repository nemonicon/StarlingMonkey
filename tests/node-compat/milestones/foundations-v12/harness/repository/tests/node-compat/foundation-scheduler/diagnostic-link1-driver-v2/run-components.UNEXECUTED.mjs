// SOURCE-ONLY until root approves/apply/build. Raw diagnostic component runner;
// never projects a private engine into production selector/bundler admission.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,symlink} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {diagnosticPreflight,hash} from './preflight.mjs';
import {loadToolchain} from '../../toolchain.mjs';
import {loadComponentizer} from '../../componentizer.mjs';
import {decodeCliString} from './decode-cli.mjs';
import {controls} from './controls.fixture.mjs';
assert.equal(process.env.NODE_COMPAT_PRIVATE_TICK_DIAGNOSTIC_RUN,'1','UNEXECUTED proposal: explicit private run opt-in required');
const here=dirname(fileURLToPath(import.meta.url)),repository=resolve(here,'../../../..');
const frozenInputBytes=await readFile(join(here,'input-freeze.json')),frozenInputSha256=hash(frozenInputBytes);
const frozenInputs=JSON.parse(frozenInputBytes).inputs;
assert.equal(frozenInputs.length,32,'Driver v2 requires the live adapter in its pre/post source seal');
const sealedAdapter=frozenInputs.filter(row=>resolve(here,row.path)===join(repository,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'));
assert.equal(sealedAdapter.length,1);assert.equal(sealedAdapter[0].sha256,'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
async function verifyFrozenInputs(){
 assert.equal(hash(await readFile(join(here,'input-freeze.json'))),frozenInputSha256,'Input freeze changed');
 for(const entry of frozenInputs)assert.equal(hash(await readFile(resolve(here,entry.path))),entry.sha256,'Frozen diagnostic source changed: '+entry.path);
}
await verifyFrozenInputs(); // BEFORE toolchain, componentization or invocation.
const preflight=await diagnosticPreflight(),{engine,metadata}=preflight;
assert(process.env.NODE_COMPAT_TICK_OUTPUT&&process.env.NODE_COMPAT_WASMTIME);
const output=resolve(process.env.NODE_COMPAT_TICK_OUTPUT);
await mkdir(output,{recursive:false}); // Never overwrite any accepted/prior run.
await writeFile(join(output,'package.json'),'{"type":"module"}\n');
const tc=await loadToolchain(),selected=await loadComponentizer(tc);
assert.equal(selected.provenance.selection,'patched-import-i32-clock-v2');
await symlink(join(tc.directory,'node_modules'),join(output,'node_modules'));
const adapter=join(repository,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
assert.equal(hash(await readFile(adapter)),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const host=resolve(process.env.NODE_COMPAT_WASMTIME),version=spawnSync(host,['--version'],{encoding:'utf8',timeout:10000});
assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
const {transpile,componentWit}=await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco')));
const oracleBytes=await readFile(join(here,'../node-results.json'));
assert.equal(hash(oracleBytes),'7e61775b17b889f3bc0ccfae37eba8520f8f48a9b153002361019c728d7bdb18');
const nodeOracle=JSON.parse(oracleBytes);assert.equal(nodeOracle.node,'v22.14.0');
const trace=name=>{const row=nodeOracle.boundaryCases.find(r=>r.boundary===name);assert(row.passed);return row.trace;};
const phases={esm:trace('esm-initial'),task:trace('task'),job:trace('promise-job')};
const returnOracle=JSON.parse(await readFile(join(here,'tick-return-node-results.json'),'utf8'));assert.equal(returnOracle.node,'v22.14.0');assert.equal(returnOracle.reads,0);
const ordinaryWorld='package test:private-ticks; world test { export run: func() -> string; }';
const lateWorld='package test:private-ticks-late; world test { export inspect-result: func() -> string; export api: interface { run: func() -> string; } }';
const options=witWorld=>({engine,preview2Adapter:adapter,witWorld,worldName:'test',
 disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});
const packaging=[],artifacts=[],initializationFailures=[],runtimeFailures=[],pairedControls=[];
let serial=0;
async function componentizeRecorded(name,source,witWorld,{initializer=null,runtimeArgs=null,sourceName=null,instantiate=true}={}){
 await writeFile(join(output,name+'.source.mjs'),source);
 const original=selected.splicer.spliceBindings;let count=0,audit;
 selected.splicer.spliceBindings=function(...args){
  ++count;assert.equal(hash(args[0]),metadata.engineSha256);assert.deepEqual(args[1],[]);
  const result=Reflect.apply(original,this,args);
  assert.equal(count,1);assert.equal(typeof result.jsBindings,'string');
  const originalBindings=result.jsBindings;
  const amended=initializer===null?originalBindings:originalBindings+'\n'+initializer+'\n';
  audit={method:'actual-splicer.spliceBindings',calls:count,originalGlue:originalBindings,amendedGlue:amended,
   originalSha256:hash(Buffer.from(originalBindings)),amendedSha256:hash(Buffer.from(amended)),
   initializerAppended:initializer!==null,originalArgumentsUnchanged:true};
  return initializer===null?result:{...result,jsBindings:amended};
 };
 try{
  const result=await selected.componentize(source,{...options(witWorld),...(runtimeArgs===null?{}:{runtimeArgs}),...(sourceName===null?{}:{sourceName})});
  assert.equal(count,1);assert.deepEqual(result.interfaceAudit.emittedImports,[]);
  const wit=await componentWit(result.component);assert.equal(wit.split('\n').filter(x=>/^\s*import /.test(x)).length,0);
  if(witWorld===ordinaryWorld)assert.equal(wit.replace(/\s+/g,' ').trim(),'package root:component; world root { export run: func() -> string; }');
  const componentPath=join(output,name+'.component.wasm');await writeFile(componentPath,result.component);
  const jsName='ticks_'+(++serial),{files}=await transpile(result.component,{name:jsName});
  for(const[file,bytes]of Object.entries(files)){await mkdir(dirname(join(output,file)),{recursive:true});await writeFile(join(output,file),bytes);}
  const record={name,componentPath,componentSha256:hash(result.component),componentBytes:result.component.length,
   sourcePath:join(output,name+'.source.mjs'),sourceSha256:hash(Buffer.from(source)),interfaceAudit:result.interfaceAudit,emittedWit:wit,
   modulePath:join(output,jsName+'.js'),runtimeArgsRequested:runtimeArgs,sourceNameRequested:sourceName};artifacts.push(record);
  console.log(JSON.stringify({phase:'componentized',name,bytes:record.componentBytes,imports:0}));
  return {...record,...(instantiate?{instance:await import(pathToFileURL(record.modulePath))}:{})};
 }finally{
  selected.splicer.spliceBindings=original;
  if(audit){
   await writeFile(join(output,name+'.initializer.original.js'),audit.originalGlue);
   await writeFile(join(output,name+'.initializer.actual.js'),audit.amendedGlue);
   packaging.push({name,...audit,originalGlue:undefined,amendedGlue:undefined,methodRestored:selected.splicer.spliceBindings===original});
  }
 }
}
function hostCall(artifact,entry='run()',{fatal=false}={}){
 const r=spawnSync(host,['run','--invoke',entry,artifact.componentPath],{encoding:'utf8',timeout:55000,maxBuffer:8*1024*1024});
 if(fatal){assert.notEqual(r.status,0,'A fatal callback/work limit must fail the boundary');assert(r.status!==null&&!r.error);return {status:r.status,stdout:r.stdout,stderr:r.stderr};}
 assert.equal(r.status,0,r.error?.message??r.stderr);
 return {status:r.status,stdout:r.stdout,stderr:r.stderr,observed:JSON.parse(decodeCliString(r.stdout.trim()))};
}
async function expectInitFailure(name,source,marker){
 let failure;try{await componentizeRecorded(name,source,ordinaryWorld);}catch(error){failure=error;}
 assert(failure,name);assert.match(failure.message,marker,name);
 initializationFailures.push({name,sourceSha256:hash(Buffer.from(source)),error:failure.message});
}
async function expectRuntimeFailure(name,body){
 const source="import{nextTick}from'starling:test-internal-ticks';export function run(){"+body+";return 'unexpected-success'}";
 const built=await componentizeRecorded(name,source,ordinaryWorld,{instantiate:false});
 const jco=spawnSync(process.execPath,[join(here,'fatal-call-worker.mjs'),built.modulePath],{encoding:'utf8',timeout:55000,maxBuffer:8*1024*1024});
 assert.equal(jco.status,0,jco.error?.message??jco.stderr);
 const observed=JSON.parse(jco.stdout.trim().split('\n').at(-1));assert.equal(observed.failed,true);assert.equal(observed.reused,false);
 const wasmtime=hostCall(built,'run()',{fatal:true});
 const paired=pairedControls.find(row=>row.pair===name);assert(paired,'Required successful paired control');
 const marker=name==='deployed-throw'?/TICK_DEPLOYED_THROW/:name==='deployed-rejection'?/TICK_DEPLOYED_REJECTION/:/ERR_SM_NODE_SCHEDULER_LIMIT|tick checkpoint work budget exceeded/;
 runtimeFailures.push({name,pairedControl:paired.name,boundaryFailureObserved:true,originalCauseIdentityAvailable:false,
  markerTextObserved:{jco:marker.test(jco.stderr+observed.error),wasmtime:marker.test(wasmtime.stderr)},componentSha256:built.componentSha256,jco:{status:jco.status,stdout:jco.stdout,stderr:jco.stderr,observed},wasmtime,
  scope:'Boundary failure plus a successful paired control, not proof of a particular original cause from generic traps. One fresh child per backend exits; no failed instance reused or thrown-JS identity inspected'});
}
const mainTemplate=await readFile(join(here,'main.fixture.mjs'),'utf8');
const token='const ORACLE = null; // __PINNED_NODE_PHASE_ORACLE__';assert.equal(mainTemplate.split(token).length,2);
const main=await componentizeRecorded('main',mainTemplate.replace(token,'const ORACLE = '+JSON.stringify(phases)+';'),ordinaryWorld),calls=[];
function checkMain(report,index){
 assert.equal(report.passed,true);assert.equal(report.calls,index);assert.equal(report.engineResetExecuted,false);assert.equal(report.classicInitialProved,false);
 assert.deepEqual(report.initialTrace,phases.esm);assert.deepEqual(report.exported,phases.task);assert.deepEqual(report.task,phases.task);assert.deepEqual(report.job,phases.job);
 assert(report.observations.every(Boolean));assert.equal(report.fifo,5000);assert.equal(report.pendingCallbacks,4096);assert.equal(report.argumentCalls,64);assert.equal(report.noArgs,1);assert.equal(report.recovered,1);assert.equal(report.queueOnlyCompleted,true);assert.equal(report.returnGetterReads,returnOracle.reads);
}
for(let n=1;n<=3;n++){const observed=JSON.parse(await main.instance.run());checkMain(observed,n);calls.push(observed);}
const mainHost=hostCall(main);checkMain(mainHost.observed,1);assert.deepEqual(mainHost.observed,calls[0]);
// Actual supported runtimeArgs: no quote parser, source-text eval option or
// public property is invented. ComponentizeJS's appended real source path
// restores content_script_path after --eval; Engine runs the file, then smSeed().
const classicOracle=JSON.parse(await readFile(join(here,'classic-node-results.json'),'utf8'));
const classicSource=await readFile(join(here,'classic-bootstrap.fixture.js'),'utf8');
assert.equal(classicOracle.node,'v22.14.0');assert.equal(hash(Buffer.from(classicSource)),classicOracle.sourceSha256);
const classic=await componentizeRecorded('configured-classic',classicSource,ordinaryWorld,
 {runtimeArgs:'--legacy-script placeholder.js --eval smSeed()',sourceName:'classic-bootstrap.js'});
const classicJco=JSON.parse(await classic.instance.run()),classicHost=hostCall(classic);
assert.deepEqual(classicJco,classicOracle.observed);assert.deepEqual(classicHost.observed,classicOracle.observed);
const initializer=await readFile(join(here,'initializer.fixture.js'),'utf8');
const init=await componentizeRecorded('initializer',await readFile(join(here,'initializer-main.fixture.mjs'),'utf8'),ordinaryWorld,{initializer});
const initJco=JSON.parse(await init.instance.run()),initHost=hostCall(init);assert.deepEqual(initJco,{beforeContent:1,ticks:1});assert.deepEqual(initHost.observed,initJco);
const late=await componentizeRecorded('late',await readFile(join(here,'late.fixture.mjs'),'utf8'),lateWorld);
const lateJco=JSON.parse(await late.instance.inspectResult());assert.deepEqual(lateJco,{trace:['getter','tick','job','job-tick'],getters:1});
assert.deepEqual(JSON.parse(await late.instance.api.run()),lateJco);const lateHost=hostCall(late,'inspect-result()');assert.deepEqual(lateHost.observed,lateJco);
await expectInitFailure('top-invalid',"import{nextTick}from'starling:test-internal-ticks';nextTick(null);export function run(){return ''}",/callback must be callable/);
await expectInitFailure('top-throw',"import{nextTick}from'starling:test-internal-ticks';nextTick(()=>{throw new Error('TICK_TOP_THROW')});export function run(){return ''}",/TICK_TOP_THROW/);
await expectInitFailure('top-rejection',"import{nextTick}from'starling:test-internal-ticks';nextTick(async()=>{throw new Error('TICK_TOP_REJECTION')});export function run(){return ''}",/TICK_TOP_REJECTION|unhandled.*rejection/i);
// Final-bind failures use the actual public WIT-interface getter path, after
// initial ESM evaluation; no custom host or generic global callback is used.
for(const[name,statement,marker]of[
 ['late-throw',"nextTick(()=>{throw new Error('TICK_LATE_THROW')})",/TICK_LATE_THROW/],
 ['late-rejection',"nextTick(async()=>{throw new Error('TICK_LATE_REJECTION')})",/TICK_LATE_REJECTION|unhandled.*rejection/i]
]){
 const source="import{nextTick}from'starling:test-internal-ticks';export function inspectResult(){return ''}export const api={get run(){"+statement+";return inspectResult}}";
 let failure;try{await componentizeRecorded(name,source,lateWorld);}catch(error){failure=error;}
 assert(failure);assert.match(failure.message,marker);initializationFailures.push({name,sourceSha256:hash(Buffer.from(source)),error:failure.message});
}
for(const control of controls){
 const source="import{nextTick}from'starling:test-internal-ticks';export function run(){"+control.body+"}";
 const built=await componentizeRecorded(control.name,source,ordinaryWorld);
 const jco=JSON.parse(await built.instance.run()),wasmtime=hostCall(built);
 assert.deepEqual(jco,control.expected);assert.deepEqual(wasmtime.observed,control.expected);
 pairedControls.push({name:control.name,pair:control.pair,expected:control.expected,jco,wasmtime,componentSha256:built.componentSha256});
}
await expectRuntimeFailure('deployed-throw',"nextTick(()=>{throw new Error('TICK_DEPLOYED_THROW')})");
await expectRuntimeFailure('deployed-rejection',"nextTick(async()=>{throw new Error('TICK_DEPLOYED_REJECTION')})");
await expectRuntimeFailure('checkpoint-work-limit',"function repeat(){nextTick(repeat)}nextTick(repeat)");
const sourceNames=['run-components.UNEXECUTED.mjs','preflight.mjs','controls.fixture.mjs','main.fixture.mjs','initializer.fixture.js','initializer-main.fixture.mjs','late.fixture.mjs','diagnostic.cmake','test-extension.cpp','classic-bootstrap.fixture.js','classic-node-oracle.cjs','classic-node-results.json','tick-return-node-oracle.cjs','tick-return-node-results.json','fatal-call-worker.mjs','decode-cli.mjs'];
assert.equal(sourceNames.length,16);
assert.deepEqual(frozenInputs.filter(row=>sourceNames.includes(row.path)).map(row=>row.path).sort(),sourceNames.slice().sort());
assert.equal(JSON.parse(frozenInputBytes).ancestralMapping.length,24);
assert.equal(JSON.parse(frozenInputBytes).ancestralInputFreezeSha256,'c3aa23e2b1838ad4fe451e0f6243dd68b05014936db37b6baf062f44f43c9208');
await verifyFrozenInputs();
const after=await diagnosticPreflight();assert.equal(after.metadataSha256,preflight.metadataSha256);assert.deepEqual(after.checked,preflight.checked);assert.deepEqual(after.frozen,preflight.frozen);
assert.equal(artifacts.length,10);assert.equal(initializationFailures.length,5);assert.equal(runtimeFailures.length,3);assert.equal(pairedControls.length,3);
const sourceManifest=frozenInputs;
const result={schemaVersion:1,state:'private-diagnostic-link1-ordinary-components-passed',engineSha256:metadata.engineSha256,
 engineReceiptSha256:preflight.metadataSha256,sourceRoot:preflight.sourceRoot,declaredSourceInputs:preflight.checked,
 producerReceipt:metadata,frozenConfiguration:preflight.frozen,link1ConsumerVersion:'sm-private-ticks-link1-consumers-v1',driverSourceVersion:'sm-private-ticks-link1-driver-v2',consumedInputCount:32,liveAdapterSealedBeforeAfter:true,sourceInputsCheckedBeforeAfter:true,inputFreezeSha256:frozenInputSha256,componentizer:selected.provenance,testOnlyPackagingVariant:packaging,
 node:{release:process.version,binarySha256:hash(await readFile(process.execPath)),oracleSha256:hash(oracleBytes),expectedPhases:phases},
 host:{path:host,sha256:hash(await readFile(host)),version:version.stdout.trim()},artifacts,calls,mainHost,
 classic:{jco:classicJco,wasmtime:classicHost,oracle:classicOracle},initializer:{jco:initJco,wasmtime:initHost},late:{jco:lateJco,wasmtime:lateHost},initializationFailures,pairedControls,runtimeFailures,sourceManifest,
 limitations:['ESM initial contract; bundled CJS initializers follow ESM. The separate classic test proves only a subsequent configured evaluation after bootstrap capture, never first-startup priority or a Node CommonJS loader.',
 'Private diagnostic engine/records only; production admission rejects this engine. No public process/global/ALS.',
 'INIT test uses explicitly recorded generated-glue append, not a public custom-initializer option or before-jobs priority proof.',
 'The GC case removes application strong co-owners of the inline callback/object/unregistered Symbol; VM temporary retention is not instrumented. Shared identity tests remain separate; no allocator recovery or fault proof.',
 'Reset/cancellation/request teardown and post-fatal reuse remain OPEN. Negative cases are boundary-failure/discard observations with successful paired controls; generic traps may hide their original cause.',
 'No performance evidence and no transfer from prior private timings.']};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({output,state:result.state,sourcePartitions:[306,2],components:artifacts.length,initializationFailures:initializationFailures.length,runtimeFailures:runtimeFailures.length,gcStress:metadata.gcStress}));
