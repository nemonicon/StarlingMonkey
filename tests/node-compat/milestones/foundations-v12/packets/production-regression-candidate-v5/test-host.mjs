// Host-only pure-shape/rejection/source tests. No component/host/guest is run.
import assert from 'node:assert/strict';
import {selectDependencyIndex} from './dependency-bindings.mjs';
import {readFile,writeFile,mkdtemp,lstat,rm} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {selectActualPin,validateProductionMetadata,RECIPE,EMBEDDING} from './admission.mjs';
import {verifyInputClosure,recheckInputSeal} from './preflight.mjs';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../../..');
assert(process.env.NODE_COMPAT_REGRESSION_HOST_TEST_OUTPUT,'Set a fresh host-only JSON output path');
const reportPath=resolve(process.env.NODE_COMPAT_REGRESSION_HOST_TEST_OUTPUT);
try{await lstat(reportPath);assert.fail('Host test output must not exist: '+reportPath);}catch(error){if(error.code!=='ENOENT')throw error;}
const hash=value=>createHash('sha256').update(value).digest('hex');
const policy=JSON.parse(await readFile(join(here,'../integration-candidate-v1/policy.json')));
const external=[{path:'embedding/embedding.cpp',sha256:EMBEDDING},{path:'embedding/embedding.h',sha256:'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e'},{path:'CMakeLists.txt',sha256:'4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8'}];
const options={gcStress:false,expectedSources:policy.expectedNativeSourceManifest,expectedExternal:external},results=[];
function test(name,run){run();results.push({name,passed:true});}
async function asyncTest(name,run){await run();results.push({name,passed:true});}
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
// OWN scratch document; independent of current/future checked-in production pins.
const pins={schemaVersion:1,state:'UNCONFIGURED_ACTUAL_PRODUCTION_FREEZES_REQUIRED',variants:{'normal-off':null,'gc-off':null}};
for(const gcStress of [false,true])test('OWN scratch null pins reject '+gcStress,()=>assert.throws(()=>selectActualPin(pins,{gcStress}),/unconfigured/));
test('configured state cannot fill null variant',()=>assert.throws(()=>selectActualPin({schemaVersion:1,state:'REVIEWED_REAL_PRODUCTION_FREEZES_V1',variants:{'normal-off':null,'gc-off':null}},{gcStress:false}),/absent/));
test('malformed pins reject',()=>assert.throws(()=>selectActualPin([],{gcStress:false})));
test('invalid all-zero digest cannot be a pin',()=>assert.throws(()=>selectActualPin({schemaVersion:1,state:'REVIEWED_REAL_PRODUCTION_FREEZES_V1',variants:{'normal-off':{state:'reviewed-real-production-freeze',gcStress:false,sourceFiles:306,recipeSha256:RECIPE,engineBytes:1,engineSha256:'0'.repeat(64)}}},{gcStress:false})));
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
const liveAdapter=join(repo,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
await asyncTest('actual LIVE adapter bytes match pinned source data; no runtime manifest claimed',async()=>assert.equal(hash(await readFile(liveAdapter)),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'));
const ownedAdapterRoot=await mkdtemp(join(tmpdir(),'starling-common-v5-adapter-'));
try{
 const adapterPath=join(ownedAdapterRoot,'adapter.wasm'),manifestPath=join(ownedAdapterRoot,'inputs.json'),original=Buffer.from('owned-adapter-data');
 const manifest=Buffer.from(JSON.stringify({schemaVersion:1,inputs:[{path:'adapter.wasm',sha256:hash(original),bytes:original.length}]}));
 await writeFile(manifestPath,manifest);
 await asyncTest('missing OWN adapter is refused by actual closure checker',async()=>assert.rejects(verifyInputClosure({manifestPath,expectedSha256:hash(manifest)}),{code:'ENOENT'}));
 await writeFile(adapterPath,'tampered-adapter');
 await asyncTest('tampered OWN adapter is refused by actual closure checker',async()=>assert.rejects(verifyInputClosure({manifestPath,expectedSha256:hash(manifest)}),/adapter.wasm/));
}finally{await rm(ownedAdapterRoot,{recursive:true});}
const transformations=JSON.parse(await readFile(join(here,'runner-transformations.json')));
for(const row of transformations.runners){let restored=await readFile(join(here,row.generated),'utf8');assert.equal(hash(restored),row.generatedSha256);
 for(const change of [...row.changes].reverse()){assert.equal(restored.split(change.after).length-1,change.count);restored=restored.split(change.after).join(change.before);}
 test('declared edits exactly restore old bytes '+row.name,()=>assert.equal(hash(restored),row.originalSha256));
 assert.equal(hash(await readFile(join(repo,row.original))),row.originalSha256);
}
const oldGC=await readFile(join(repo,'tests/node-compat/foundation-alloc-unsafe/installed/run-gc-v11.mjs'),'utf8'),newGC=await readFile(join(here,'runners/allocator-gc.mjs'),'utf8');
const guest=text=>text.slice(text.indexOf('const source=`')+'const source=`'.length,text.indexOf('`;\nconst adapter'));
test('allocator GC guest template byte-identical',()=>assert.equal(guest(newGC),guest(oldGC)));

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
const reviewedPinBytes=await readFile(join(here,'pins.json'));
test('current production pins are byte-exact Root-reviewed data',()=>assert.equal(hash(reviewedPinBytes),'ed0d6f548ac354ce6ef0ab97c5162ece7091a4e22c81fdd3910665c0bbb21bea'));
const reviewedDocument=JSON.parse(reviewedPinBytes);
for(const gcStress of [false,true])test('reviewed production selector shape only '+gcStress,()=>{const pin=selectActualPin(reviewedDocument,{gcStress});assert.equal(pin.sourceFiles,306);});
const report={schemaVersion:1,state:'HOST_ONLY_ACTIVATION_SOURCE_CHECKS_PASSED',tests:results.length,passed:results.length,results,
 syntheticShapeOnly:true,fixedArtifactSuccessExecuted:false,checkedInPinsUsedByNegativeTests:false,diagnosticReceiptModifiedOrProjected:false,
 entryNegativeChildren:0,scratchSealCases:7,ownedAdapterNegativeCases:2,liveAdapterReadOnlyChecks:1,finalInputManifestChecked:false,componentizerToolchainOrHostRun:false,nativeBuild:false,guestExecuted:false,oldV11FilesModified:false};
await writeFile(reportPath,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,tests:report.tests,passed:report.passed}));
