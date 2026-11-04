// Host-only pure-shape/rejection/source tests. No component/host/guest is run.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdtemp,lstat,rm} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {selectActualPin,validateProductionMetadata,RECIPE,EMBEDDING} from './admission.mjs';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../../..');
const hash=value=>createHash('sha256').update(value).digest('hex');
const policy=JSON.parse(await readFile(join(here,'../integration-candidate-v1/policy.json')));
const external=[{path:'embedding/embedding.cpp',sha256:EMBEDDING},{path:'embedding/embedding.h',sha256:'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e'},{path:'CMakeLists.txt',sha256:'4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8'}];
const options={gcStress:false,expectedSources:policy.expectedNativeSourceManifest,expectedExternal:external},results=[];
function test(name,run){run();results.push({name,passed:true});}
function shape(gc=false){
  // Constructed FROM SCRATCH; no engine path/hash or diagnostic receipt is projected.
  const flags={CMAKE_BUILD_TYPE:'Release',WEVAL:'OFF',USE_WASM_OPT:'ON',ENABLE_BUILTIN_NODE_COMPAT:'ON',ENABLE_JS_DEBUGGER:'OFF',ENABLE_BUILTIN_WPT_SUPPORT:'OFF',NODE_COMPAT_LOCKED_RUST:'ON',NODE_COMPAT_OOM_TESTING:'OFF',NODE_COMPAT_ENTROPY_MODE:'OFF',NODE_COMPAT_INTERNAL_TICKS:'ON',NODE_COMPAT_PATH:'ON',NODE_COMPAT_EVENTS:'ON',NODE_COMPAT_STRING_DECODER:'ON',NODE_COMPAT_ASSERT:'ON',NODE_COMPAT_QUERYSTRING:'ON',NODE_COMPAT_UTIL:'ON',NODE_COMPAT_STREAM_WEB:'ON',NODE_COMPAT_GC_STRESS:gc?'ON':'OFF'};
  return{buildRecipeSha256:RECIPE,internalTicksEnabled:true,gcStress:gc,profileEnabled:true,pathEnabled:true,eventsEnabled:true,stringDecoderEnabled:true,assertEnabled:true,querystringEnabled:true,utilEnabled:true,streamWebEnabled:true,strictInitialization:true,abiFixEnabled:true,bigIntFixEnabled:true,oomTesting:false,debuggerEnabled:false,wptSupportEnabled:false,entropyPolicy:'off',hostApi:'wasi-0.2.10',requestedCMakeOptions:{...flags},observedCMakeOptions:{...flags},sourceManifest:structuredClone(policy.expectedNativeSourceManifest),componentizeSourceManifest:structuredClone(external),sourceInputsCapturedBeforeBuild:true,componentizeSourcesCapturedBeforeBuild:true,buildRecipeCheckedBeforeAndAfterBuild:true,generatedRustProject:{cargoBuildLocked:true,manifestAndLockCheckedBeforeAndAfterBuild:true}};
}
for(const gcStress of [false,true])test('pure shape only normal/gc '+gcStress,()=>{const result=validateProductionMetadata(shape(gcStress),{...options,gcStress});assert.equal(result.artifactProof,false);assert.equal(result.runtimeProof,false);});
for(const value of [null,[],true,'metadata',{}])test('malformed metadata '+JSON.stringify(value),()=>assert.throws(()=>validateProductionMetadata(value,options)));
for(const[name,mutate]of[
 ['synthetic runtime label',m=>{m.syntheticMetadataOnly=true;}],['diagnostic policy even undefined',m=>{m.internalTickDiagnosticPolicy=undefined;}],
 ['diagnostic only',m=>{m.diagnosticOnly=true;}],['old recipe',m=>{m.buildRecipeSha256=policy.parentRecipeSha256;}],
 ['duplicate source',m=>{m.sourceManifest[1]=m.sourceManifest[0];}],['malformed digest',m=>{m.sourceManifest[0].sha256='not-sha';}],
 ['source traversal',m=>{m.sourceManifest[0].path='../escape';}],['missing source',m=>{m.sourceManifest.pop();}],
 ['missing requested flag',m=>{delete m.requestedCMakeOptions.NODE_COMPAT_INTERNAL_TICKS;}],['mismatched GC flag',m=>{m.observedCMakeOptions.NODE_COMPAT_GC_STRESS='ON';}],
 ['unselected optional',m=>{m.eventsEnabled=false;}],['wrong embedding',m=>{m.componentizeSourceManifest[0].sha256=policy.embedding.beforeSha256;}],
 ['unlocked Rust',m=>{m.generatedRustProject.cargoBuildLocked=false;}],['unconfirmed source before/after',m=>{m.sourceInputsCapturedBeforeBuild=false;}],
])test(name,()=>{const metadata=shape();mutate(metadata);assert.throws(()=>validateProductionMetadata(metadata,options));});
const actualV11=JSON.parse(await readFile('/tmp/starling-node-compat/foundations-v11/native-freeze/off-foundations.engine.wasm.build.json'));
test('known actual v11 is not current production',()=>assert.throws(()=>validateProductionMetadata(actualV11,options),/production recipe/));
const actualDiagnostic=JSON.parse(await readFile('/tmp/starling-node-compat/foundation-scheduler-v2/native-freeze/diagnostic-release.engine.wasm.build.json'));
test('known actual a49 diagnostic rejected without projection',()=>{assert.equal(actualDiagnostic.engineSha256,'a49c920c83a5deb144c960f3d745f66b57754415546346c089b9f182d4b67f6b');assert.throws(()=>validateProductionMetadata(actualDiagnostic,options),/Diagnostic engine rejected/);});
const pins=JSON.parse(await readFile(join(here,'pins.json')));
for(const gcStress of [false,true])test('checked-in null pins reject '+gcStress,()=>assert.throws(()=>selectActualPin(pins,{gcStress}),/unconfigured/));
test('configured state cannot fill null variant',()=>assert.throws(()=>selectActualPin({schemaVersion:1,state:'REVIEWED_REAL_PRODUCTION_FREEZES_V1',variants:{'normal-off':null,'gc-off':null}},{gcStress:false}),/absent/));
test('malformed pins reject',()=>assert.throws(()=>selectActualPin([],{gcStress:false})));
test('invalid all-zero digest cannot be a pin',()=>assert.throws(()=>selectActualPin({schemaVersion:1,state:'REVIEWED_REAL_PRODUCTION_FREEZES_V1',variants:{'normal-off':{state:'reviewed-real-production-freeze',gcStress:false,sourceFiles:306,recipeSha256:RECIPE,engineBytes:1,engineSha256:'0'.repeat(64)}}},{gcStress:false})));
const temporary=await mkdtemp(join(tmpdir(),'starling-production-regression-negative-'));
try{
 for(const[file,variable]of [['run-core.mjs','NODE_COMPAT_OUTPUT'],['run-allocator.mjs','NODE_COMPAT_INSTALLED_ALLOCATOR_OUTPUT'],['run-allocator-gc.mjs','NODE_COMPAT_ALLOCATOR_GC_OUTPUT']]){
  const output=join(temporary,file);const env={...process.env,NODE_COMPAT_ENGINE:'/NO_ENGINE_MUST_BE_READ',NODE_COMPAT_ENGINE_SOURCE_ROOT:'/NO_SOURCE_MUST_BE_READ',NODE_COMPAT_WASMTIME:'/NO_HOST_MUST_BE_RUN',[variable]:output};delete env.NODE_OPTIONS;
  const child=spawnSync(process.execPath,[join(here,file)],{encoding:'utf8',env,timeout:10000,maxBuffer:1024*1024});
  test('entry fails before loaders/output '+file,()=>{assert.notEqual(child.status,0);assert.match(child.stderr,/Actual production pins are unconfigured/);assert(!/ENOENT|MODULE_NOT_FOUND|ERR_MODULE_NOT_FOUND/.test(child.stderr));});
  try{await lstat(output);assert.fail('Entry created output despite null pins');}catch(error){assert.equal(error.code,'ENOENT');}
 }
}finally{await rm(temporary,{recursive:true});}
const transformations=JSON.parse(await readFile(join(here,'runner-transformations.json')));
for(const row of transformations.runners){let restored=await readFile(join(here,row.generated),'utf8');assert.equal(hash(restored),row.generatedSha256);
 for(const change of [...row.changes].reverse()){assert.equal(restored.split(change.after).length-1,change.count);restored=restored.split(change.after).join(change.before);}
 test('declared edits exactly restore old bytes '+row.name,()=>assert.equal(hash(restored),row.originalSha256));
 assert.equal(hash(await readFile(join(repo,row.original))),row.originalSha256);
}
const oldGC=await readFile(join(repo,'tests/node-compat/foundation-alloc-unsafe/installed/run-gc-v11.mjs'),'utf8'),newGC=await readFile(join(here,'runners/allocator-gc.mjs'),'utf8');
const guest=text=>text.slice(text.indexOf('const source=`')+'const source=`'.length,text.indexOf('`;\nconst adapter'));
test('allocator GC guest template byte-identical',()=>assert.equal(guest(newGC),guest(oldGC)));
const report={schemaVersion:1,state:'HOST_ONLY_PREPARATION_CHECKS_PASSED',tests:results.length,passed:results.length,results,
 syntheticShapeOnly:true,fixedArtifactSuccessExecuted:false,actualProductionPinsExist:false,diagnosticReceiptModifiedOrProjected:false,
 entryNegativeChildren:3,componentizerToolchainOrHostRun:false,nativeBuild:false,guestExecuted:false,oldV11FilesModified:false};
await writeFile(join(here,'test-results.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,tests:report.tests,passed:report.passed}));
