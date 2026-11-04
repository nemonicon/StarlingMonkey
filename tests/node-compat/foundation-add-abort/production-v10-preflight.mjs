// Fail-closed admission for a newly frozen ordinary m0.10 ON/entropy-OFF engine.
// Accepted v8 pins/results remain immutable. This performs no component work.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {PRODUCTION_V8_PINS as base} from './production-v8-preflight.mjs';
import {nativePreflight} from '../foundation-stream-web/production-candidate/native-preflight.mjs';
const here=dirname(fileURLToPath(import.meta.url));
export async function verifyProductionV10(){
  const pins=JSON.parse(await readFile(join(here,'production-v10-pins.json')));
  assert.equal(pins.state,'new-native-build-reviewed');
  const {engine,sourceRoot,metadata,hash,safetyAudit}=await nativePreflight({streamWebEnabled:true});
  assert.equal(metadata.engineSha256,pins.engineSha256);
  assert.equal(hash(await readFile(engine+'.build.json')),pins.receiptSha256);
  assert.equal(metadata.engineBytes,pins.engineBytes);
  assert.equal(metadata.sourceManifest.length,pins.nativeInputs);
  assert.equal(metadata.strictInitialization,true);assert.equal(metadata.debuggerEnabled,false);
  assert.equal(metadata.gcStress,false);assert.equal(metadata.wptSupportEnabled,false);
  assert.equal(metadata.abiFixEnabled,true);assert.equal(metadata.bigIntFixEnabled,true);
  assert.equal(metadata.hostApi,'wasi-0.2.10');assert.equal(metadata.generatedRustProject.cargoBuildLocked,true);
  assert.equal(metadata.buildRecipeSha256,pins.recipeSha256);
  for(const flag of ['sourceInputsCapturedBeforeBuild','componentizeSourcesCapturedBeforeBuild','buildRecipeCheckedBeforeAndAfterBuild'])
    assert.equal(metadata[flag],true,flag);
  const options={CMAKE_BUILD_TYPE:'Release',WEVAL:'OFF',USE_WASM_OPT:'ON',ENABLE_BUILTIN_NODE_COMPAT:'ON',
    ENABLE_JS_DEBUGGER:'OFF',ENABLE_BUILTIN_WPT_SUPPORT:'OFF',NODE_COMPAT_LOCKED_RUST:'ON',
    NODE_COMPAT_ENTROPY_MODE:'OFF',NODE_COMPAT_GC_STRESS:'OFF',NODE_COMPAT_OOM_TESTING:'OFF',
    NODE_COMPAT_PATH:'ON',NODE_COMPAT_EVENTS:'ON',NODE_COMPAT_STRING_DECODER:'ON',NODE_COMPAT_ASSERT:'ON',
    NODE_COMPAT_QUERYSTRING:'ON',NODE_COMPAT_UTIL:'ON',NODE_COMPAT_STREAM_WEB:'ON'};
  for(const[key,value]of Object.entries(options))assert.equal(metadata.observedCMakeOptions[key],value,key);
  const core=metadata.selectedModuleManifests.find(entry=>entry.path==='builtins/node-compat/export-manifest.node-v22.14.0.json');
  assert.equal(core?.sha256,base.coreManifestSha256);assert.equal(core.profileVersion,'sm-node-22.14.0-m0.8');
  const policy=metadata.strictEventExceptionPolicy;
  assert.equal(policy.version,'sm-uncaught-event-v3-protected-abort-v2');assert.equal(policy.patchSha256,base.nativePatchSha256);
  assert.deepEqual(policy.basePolicy,{version:'sm-uncaught-event-v3',patchSha256:base.nativePatchSha256,nativeSourceSha256:base.nativeSourceSha256});
  const expectedNative={...base.nativeSourceSha256,'builtins/web/event/event-target.cpp':pins.protectedSources['builtins/web/event/event-target.cpp']};
  const protectedPolicy=metadata.protectedAbortListenerPolicy;
  assert.equal(metadata.protectedAbortListenerEnabled,true);assert.equal(protectedPolicy?.enabled,true);
  assert.equal(protectedPolicy.version,'sm-protected-abort-listener-v2');
  assert.equal(protectedPolicy.strictPolicyVersion,policy.version);assert.equal(protectedPolicy.patchSha256,pins.protectedPatchSha256);
  assert.deepEqual(protectedPolicy.sourceSha256,pins.protectedSources);
  for(const[path,sha256]of Object.entries(pins.protectedSources))assert.equal(metadata.sourceManifest.find(entry=>entry.path===path)?.sha256,sha256,path);
  assert.deepEqual(protectedPolicy.prerequisiteCMakeOptions,{ENABLE_BUILTIN_WEB_EVENT:'ON',ENABLE_BUILTIN_WEB_ABORT:'ON',ENABLE_BUILTIN_WEB_QUEUE_MICROTASK:'ON'});
  assert(protectedPolicy.actualLayoutCompileCommands.length>0);assert(protectedPolicy.actualEmbeddingCompileCommands.length>0);
  for(const command of [...protectedPolicy.actualLayoutCompileCommands,...protectedPolicy.actualEmbeddingCompileCommands])assert(command.split(/\s+/).includes('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1'));
  for(const suffix of ['/builtins/web/event/event-target.cpp','/builtins/web/abort/abort-signal.cpp','/builtins/node-compat/register.cpp'])assert(protectedPolicy.actualLayoutCompileCommands.some(command=>command.includes(suffix)));
  assert.equal(policy.embeddingBoundaryPatchSha256,base.boundaryPatchSha256);
  assert.equal(policy.deployedUnhandledRejections,'fatal-after-drained-jobs-before-result-marshalling');
  assert.deepEqual(policy.nativeSourceSha256,expectedNative);
  for(const[path,sha256]of Object.entries(expectedNative))
    assert.equal(metadata.sourceManifest.find(entry=>entry.path===path)?.sha256,sha256,path);
  assert.equal(metadata.componentizeSourceManifest.find(entry=>entry.path==='embedding/embedding.cpp')?.sha256,base.embeddingSourceSha256);
  assert.equal(policy.actualNativeCompileCommands.length,3);
  for(const path of Object.keys(base.nativeSourceSha256).filter(path=>path.endsWith('.cpp'))){
    const commands=policy.actualNativeCompileCommands.filter(command=>command.endsWith('/'+path));
    assert.equal(commands.length,1);assert(commands[0].split(/\s+/).includes('-DNODE_COMPAT_STRICT_INITIALIZATION=1'));
  }
  assert(metadata.actualEmbeddingCompileCommands.length>0);
  assert(metadata.actualEmbeddingCompileCommands.every(command=>command.split(/\s+/).includes('-DNODE_COMPAT_STRICT_INITIALIZATION=1')));
  const freeze=dirname(engine);
  assert.equal(hash(await readFile(join(freeze,pins.cacheFilename))),metadata.cmakeCacheSha256);
  assert.equal(hash(await readFile(join(freeze,pins.compileCommandsFilename))),metadata.compileCommandsSha256);
  return {schemaVersion:1,state:'production-v10-receipt-and-source-preflight-passed',
    engine,engineSha256:pins.engineSha256,receiptSha256:pins.receiptSha256,sourceRoot,sourceFilesVerified:pins.nativeInputs,
    coreProfile:core.profileVersion,strictPolicy:policy.version,recipeSha256:pins.recipeSha256,
    unchangedStrictV3RuntimeAndEmbedding:true,reviewedEventTargetExtension:protectedPolicy.version,nativeStrictTranslationUnits:3,
    frozenConfigurationDigestsVerified:true,safetyAudit,scope:'Read-only new engine and exact layered strict-v3/protected-abort source admission; no runtime proof inferred.'};
}
