// Host-only pure-shape/rejection/source tests. No component/host/guest is run.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdtemp,lstat,rm} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {selectActualPin,validateProductionMetadata,validatePinBoundary,RECIPE,EMBEDDING} from './admission.mjs';
import {verifyInputClosure,recheckInputSeal} from './preflight.mjs';
import {variantOptions,scalarImports,HTTP_IMPORTS,HTTP_EXPORTS,validateHTTPInterfaces} from './capabilities.mjs';
import {selectHTTPPin} from './http-contract.mjs';
import {LIVE_COMPUTED_INPUTS,requireComputedRows,validateWitPackageNames,verifyComputedLiveInputs} from './computed-inputs.mjs';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../../..');
assert(process.env.NODE_COMPAT_CAPABILITY_HOST_TEST_OUTPUT,'Set a fresh host-only JSON output path');
const reportPath=resolve(process.env.NODE_COMPAT_CAPABILITY_HOST_TEST_OUTPUT);
try{await lstat(reportPath);assert.fail('Host test output must not exist: '+reportPath);}catch(error){if(error.code!=='ENOENT')throw error;}
const hash=value=>createHash('sha256').update(value).digest('hex');
const policy=JSON.parse(await readFile(join(here,'../integration-candidate-v1/policy.json')));
const external=[{path:'embedding/embedding.cpp',sha256:EMBEDDING},{path:'embedding/embedding.h',sha256:'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e'},{path:'CMakeLists.txt',sha256:'4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8'}];
const options={gcStress:false,expectedSources:policy.expectedNativeSourceManifest,expectedExternal:external},results=[];
function test(name,run){run();results.push({name,passed:true});}
async function asyncTest(name,run){await run();results.push({name,passed:true});}
function shape(gc=false,entropyPolicy='off'){
  // Constructed FROM SCRATCH; no engine path/hash or diagnostic receipt is projected.
  const flags={CMAKE_BUILD_TYPE:'Release',WEVAL:'OFF',USE_WASM_OPT:'ON',ENABLE_BUILTIN_NODE_COMPAT:'ON',ENABLE_JS_DEBUGGER:'OFF',ENABLE_BUILTIN_WPT_SUPPORT:'OFF',NODE_COMPAT_LOCKED_RUST:'ON',NODE_COMPAT_OOM_TESTING:'OFF',NODE_COMPAT_ENTROPY_MODE:entropyPolicy==='off'?'OFF':'RUNTIME_ONLY',NODE_COMPAT_INTERNAL_TICKS:'ON',NODE_COMPAT_PATH:'ON',NODE_COMPAT_EVENTS:'ON',NODE_COMPAT_STRING_DECODER:'ON',NODE_COMPAT_ASSERT:'ON',NODE_COMPAT_QUERYSTRING:'ON',NODE_COMPAT_UTIL:'ON',NODE_COMPAT_STREAM_WEB:'ON',NODE_COMPAT_GC_STRESS:gc?'ON':'OFF'};
  return{buildRecipeSha256:RECIPE,internalTicksEnabled:true,gcStress:gc,profileEnabled:true,pathEnabled:true,eventsEnabled:true,stringDecoderEnabled:true,assertEnabled:true,querystringEnabled:true,utilEnabled:true,streamWebEnabled:true,strictInitialization:true,abiFixEnabled:true,bigIntFixEnabled:true,oomTesting:false,debuggerEnabled:false,wptSupportEnabled:false,entropyPolicy,hostApi:'wasi-0.2.10',requestedCMakeOptions:{...flags},observedCMakeOptions:{...flags},sourceManifest:structuredClone(policy.expectedNativeSourceManifest),componentizeSourceManifest:structuredClone(external),sourceInputsCapturedBeforeBuild:true,componentizeSourcesCapturedBeforeBuild:true,buildRecipeCheckedBeforeAndAfterBuild:true,generatedRustProject:{cargoBuildLocked:true,manifestAndLockCheckedBeforeAndAfterBuild:true}};
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
test('configured state cannot fill null variant',()=>assert.throws(()=>selectActualPin({schemaVersion:1,state:'REVIEWED_REAL_PRODUCTION_CAPABILITY_FREEZES_V1',variants:{'normal-off':null,'gc-off':null}},{gcStress:false}),/absent/));
test('malformed pins reject',()=>assert.throws(()=>selectActualPin([],{gcStress:false})));
test('invalid all-zero digest cannot be a pin',()=>assert.throws(()=>selectActualPin({schemaVersion:1,state:'REVIEWED_REAL_PRODUCTION_CAPABILITY_FREEZES_V1',variants:{'normal-off':{state:'reviewed-real-production-freeze',gcStress:false,entropyPolicy:'off',sourceFiles:306,recipeSha256:RECIPE,engineBytes:1,engineSha256:'0'.repeat(64)}}},{gcStress:false})));
test('pure RuntimeOnly shape is not artifact proof',()=>{const m=shape(false,'runtime-only');const p=validateProductionMetadata(m,{...options,entropyPolicy:'runtime-only'});assert.equal(p.artifactProof,false);assert.equal(p.runtimeProof,false);assert(!Object.hasOwn(m,'engineSha256'));});
test('RuntimeOnly cannot use OFF choices',()=>assert.throws(()=>validateProductionMetadata(shape(false,'runtime-only'),options)));
test('RuntimeOnly GC unavailable',()=>assert.throws(()=>validateProductionMetadata(shape(true,'runtime-only'),{...options,gcStress:true,entropyPolicy:'runtime-only'})));
test('RuntimeOnly pins remain null',()=>assert.throws(()=>selectActualPin(pins,{gcStress:false,entropyPolicy:'runtime-only'}),/unconfigured/));
test('only finite capability variants',()=>assert.throws(()=>variantOptions('unknown')));
test('OFF scalar selects none',()=>assert.deepEqual(scalarImports('off'),[]));
test('RuntimeOnly scalar selects exactly random',()=>assert.deepEqual(scalarImports('runtime-only'),['wasi:random/random@0.2.10']));
test('no ad-hoc scalar feature',()=>assert.throws(()=>scalarImports('all')));
const httpShape={entropyPolicy:'runtime-only',selectedInterfaces:[...HTTP_IMPORTS],allowedImports:[...HTTP_IMPORTS],emittedImports:[...HTTP_IMPORTS],emittedExports:[...HTTP_EXPORTS],clockDependency:{typeOnly:true,callableImports:[],coreClockImports:[]}};
test('six HTTP interfaces only pure shape',()=>validateHTTPInterfaces(httpShape));
for(const[name,change]of [
 ['outgoing HTTP',x=>x.emittedImports.push('wasi:http/outgoing-handler@0.2.10')],
 ['socket',x=>x.emittedImports.push('wasi:sockets/tcp@0.2.10')],
 ['wrong version',x=>x.emittedImports[0]='wasi:clocks/monotonic-clock@0.2.12'],
 ['clock function',x=>x.clockDependency.callableImports.push('now')],
 ['core clock function',x=>x.clockDependency.coreClockImports.push('clock_time_get')],
 ['clock not type only',x=>x.clockDependency.typeOnly=false],
 ['overbroad allowlist',x=>x.allowedImports.push('wasi:cli/environment@0.2.10')],
 ['missing selected random',x=>x.selectedInterfaces.pop()],
 ['extra export',x=>x.emittedExports.push('run')]
])test('HTTP rejects '+name,()=>{const x=structuredClone(httpShape);change(x);assert.throws(()=>validateHTTPInterfaces(x));});
const httpPins=JSON.parse(await readFile(join(here,'http-component-pins.json')));
test('HTTP component pins null before artifact reads',()=>assert.throws(()=>selectHTTPPin(httpPins,{}),/unconfigured/));
test('reviewed label cannot invent missing component',()=>assert.throws(()=>selectHTTPPin({schemaVersion:1,state:'REVIEWED_REAL_HTTP_COMPONENT_V1',component:null},{})));
test('canonical synthetic pin boundary only',()=>validatePinBoundary('/tmp/owned-pin-boundary',['/tmp/owned-pin-boundary/file.txt']));
for(const root of ['relative','/tmp/a/../b','/tmp/a//b','/tmp/a\0b'])test('reject malformed pin root '+JSON.stringify(root),()=>assert.throws(()=>validatePinBoundary(root)));
for(const child of ['/tmp/outside/file','/tmp/owned-pin-boundary/a/../b','/tmp/owned-pin-boundary/a\0b'])test('reject malformed pin child '+JSON.stringify(child),()=>assert.throws(()=>validatePinBoundary('/tmp/owned-pin-boundary',[child])));
test('HTTP unnormalized root rejected before any engine/file fields',()=>assert.throws(()=>selectHTTPPin({schemaVersion:1,state:'REVIEWED_REAL_HTTP_COMPONENT_V1',component:{state:'reviewed-real-runtime-http-component',root:'/tmp/a/../b'}},{}),/Pin root must be canonical/));
const temporary=await mkdtemp(join(tmpdir(),'starling-capability-negative-'));
let negativeChildren=0;
try{
 for(const[file,variable,variant]of [
  ['run-focused.mjs','NODE_COMPAT_ADD_ABORT_OUTPUT','normal-off'],
  ['run-focused.mjs','NODE_COMPAT_ADD_ABORT_OUTPUT','normal-runtime'],
  ['run-gc.mjs','NODE_COMPAT_ADD_ABORT_OUTPUT','gc-off'],
  ['run-getter.mjs','NODE_COMPAT_ADD_ABORT_OUTPUT','normal-off'],
  ['prepare-http.mjs','NODE_COMPAT_PRODUCTION_HTTP_ROOT',null],
  ['build-http.mjs','NODE_COMPAT_HTTP_OUTPUT',null],
  ['seal-http-component.mjs','NODE_COMPAT_PRODUCTION_HTTP_ROOT',null],
  ['audit-http.mjs','NODE_COMPAT_PRODUCTION_HTTP_RESULTS',null],
  ['run-http-wasmtime.mjs','NODE_COMPAT_HTTP_OUTPUT',null],
  ['run-http-wash.mjs','NODE_COMPAT_WASMCLOUD_OUTPUT',null],
  ['runners/http-build.mjs','NODE_COMPAT_HTTP_OUTPUT',null]
 ]){
  const output=join(temporary,'output-'+negativeChildren),env={...process.env,NODE_COMPAT_ENGINE:'/NO_ENGINE_MUST_BE_READ',NODE_COMPAT_ENGINE_SOURCE_ROOT:'/NO_SOURCE_MUST_BE_READ',NODE_COMPAT_WASMTIME:'/NO_HOST_MUST_BE_RUN',NODE_COMPAT_WASH:'/NO_WASH_MUST_BE_RUN',NODE_COMPAT_FOLLOWON_VARIANT:variant??'',NODE_COMPAT_HTTP_AUDIT:'/NO_AUDIT_MUST_BE_READ',[variable]:output};delete env.NODE_OPTIONS;
  const child=spawnSync(process.execPath,[join(here,file)],{encoding:'utf8',env,timeout:10000,maxBuffer:1024*1024});
  test('entry null-pin stop before loader/output '+file+' '+variant,()=>{assert.notEqual(child.status,0);assert.match(child.stderr,/Actual production pins are unconfigured/);assert(!/ENOENT|MODULE_NOT_FOUND|ERR_MODULE_NOT_FOUND/.test(child.stderr));});
  try{await lstat(output);assert.fail('Created output despite null pins');}catch(error){assert.equal(error.code,'ENOENT');}
  ++negativeChildren;
 }
}finally{await rm(temporary,{recursive:true});}
// Exercise only owned scratch data. No real pin, engine or packet file changes.
const scratch=await mkdtemp(join(tmpdir(),'starling-production-seal-check-'));
try{
 const manifestPath=join(scratch,'inputs.json'),pinsPath=join(scratch,'pins.json'),dataPath=join(scratch,'data.txt');
 const pinBytes=Buffer.from('{"fixtureOnly":true}\n'),originalData=Buffer.from('original');
 const originalManifest=Buffer.from(JSON.stringify({schemaVersion:1,inputs:[{path:'data.txt',sha256:hash(originalData),bytes:originalData.length}]}));
 await writeFile(pinsPath,pinBytes);await writeFile(dataPath,originalData);await writeFile(manifestPath,originalManifest);
 const originalSeal=await verifyInputClosure({manifestPath}),expectedManifestSha256=originalSeal.sha256,expectedPinsSha256=hash(pinBytes);
 const captured={pinsPath,manifestPath,expectedManifestSha256,expectedPinsSha256};
 await asyncTest('owned scratch seal succeeds without artifact admission',async()=>assert.deepEqual(await recheckInputSeal(captured),originalSeal));
 await writeFile(dataPath,'replaced');
 await asyncTest('listed bytes changed while manifest fixed rejects',async()=>assert.rejects(recheckInputSeal(captured),/data.txt/));
 const replacement=Buffer.from('replaced');
 await writeFile(manifestPath,JSON.stringify({schemaVersion:1,inputs:[{path:'data.txt',sha256:hash(replacement),bytes:replacement.length}]}));
 await asyncTest('replacement manifest and matching listed bytes rejects',async()=>assert.rejects(recheckInputSeal(captured),/Runtime input manifest changed/));
 await writeFile(manifestPath,'NOT JSON; expected digest must fail first');
 await asyncTest('manifest digest checked before parsing',async()=>assert.rejects(recheckInputSeal(captured),/Runtime input manifest changed/));
 await writeFile(manifestPath,JSON.stringify({schemaVersion:1,inputs:[{path:'NEVER_FOLLOW_THIS_MISSING_PATH',sha256:hash(replacement),bytes:replacement.length}]}));
 await asyncTest('manifest digest checked before following new rows',async()=>assert.rejects(recheckInputSeal(captured),/Runtime input manifest changed/));
 await writeFile(pinsPath,'replacement pins');
 await asyncTest('pins tamper rejects before changed manifest',async()=>assert.rejects(recheckInputSeal(captured),/Production pins changed/));
 await writeFile(pinsPath,pinBytes);await writeFile(manifestPath,originalManifest);await writeFile(dataPath,originalData);
 pinBytes.fill(0);originalSeal.sha256='mutated report object';originalSeal.path='mutated report path';
 await asyncTest('captured primitive pins and manifest digests survive returned-object mutation',async()=>assert.equal((await recheckInputSeal(captured)).sha256,expectedManifestSha256));
}finally{await rm(scratch,{recursive:true});}
const computedManifestPath=join(here,'input-freeze.json'),computedBytes=await readFile(computedManifestPath),computedRows=JSON.parse(computedBytes).inputs;
await asyncTest('all eight actual live cp/adapter inputs are sealed and unchanged',async()=>{const proof=await verifyComputedLiveInputs({manifestPath:computedManifestPath,expectedManifestSha256:hash(computedBytes),repository:repo});assert.equal(proof.files,8);});
for(const name of LIVE_COMPUTED_INPUTS)test('missing live computed input rejects '+name,()=>{const without=computedRows.filter(row=>resolve(here,row.path)!==resolve(repo,name));assert.throws(()=>requireComputedRows(without,{manifestPath:computedManifestPath,repository:repo}),/not sealed/);});
test('frozen control copy does not replace a live WIT path',()=>{const without=computedRows.filter(row=>resolve(here,row.path)!==resolve(repo,LIVE_COMPUTED_INPUTS[0]));without.push({path:'/tmp/frozen-control/package.wit',sha256:'1'.repeat(64),bytes:1});assert.throws(()=>requireComputedRows(without,{manifestPath:computedManifestPath,repository:repo}),/not sealed/);});
test('unlisted cp directory rejects',()=>assert.throws(()=>validateWitPackageNames(['unexpected'])));
await asyncTest('computed seal digest checked before following rows',async()=>assert.rejects(verifyComputedLiveInputs({manifestPath:computedManifestPath,expectedManifestSha256:'0'.repeat(64),repository:repo}),/before parsing/));
const report={schemaVersion:1,state:'HOST_ONLY_CAPABILITY_PREPARATION_CHECKS_PASSED',tests:results.length,passed:results.length,results,
 syntheticShapeOnly:true,fixedArtifactSuccessExecuted:false,actualProductionPinsExist:false,actualHTTPComponentPinsExist:false,diagnosticReceiptModifiedOrProjected:false,
 entryNegativeChildren:negativeChildren,scratchSealCases:7,computedLiveInputsVerifiedReadOnly:8,componentizerToolchainOrHostRun:false,nativeBuild:false,guestExecuted:false,oldV11FilesModified:false};
await writeFile(reportPath,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,tests:report.tests,passed:report.passed}));
