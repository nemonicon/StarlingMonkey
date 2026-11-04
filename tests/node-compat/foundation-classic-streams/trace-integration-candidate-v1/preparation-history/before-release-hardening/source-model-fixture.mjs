// SYNTHETIC SOURCE-MODEL INPUT ONLY. Never an engine/build/runtime receipt.
// Required `actual*`/`*BeforeBuild` field names below describe parser-test inputs,
// not events which occurred. No compiler is executed, engine bytes/path/hash is
// supplied, or production admission is called. validateClassicSourceAdmission
// must reject syntheticMetadataOnly:true before considering this model.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const copy=value=>JSON.parse(JSON.stringify(value));
const on=value=>value?'ON':'OFF';
async function json(url){const bytes=await readFile(url);return{bytes,value:JSON.parse(bytes)};}
function layer(map,policy){
  return Object.fromEntries(Object.entries(map).map(([path,digest])=>{
    const change=policy.sourceLayer[path];
    if(!change)return[path,digest];
    assert.equal(change.beforeSha256,digest,'Synthetic source ancestry mismatch: '+path);
    return[path,change.afterSha256];
  }));
}

export async function fixture({sourceRoot,classic=true,ticks=true,web=true,events=true,
  stringDecoder=true,entropy='off',gc=false}={}) {
  for(const value of [classic,ticks,web,events,stringDecoder,gc])assert.equal(typeof value,'boolean');
  assert(['off','runtime-only'].includes(entropy));
  // Deliberately do not reject classic-without-prerequisites or runtime+GC here:
  // those are useful negative inputs for validateClassicSourceModel itself.
  const [{bytes:pinsBytes,value:pins},{bytes:policyBytes,value:policy},
    {bytes:parentPinsBytes,value:parentPins},{bytes:parentBytes,value:parent}]=await Promise.all([
      json(new URL('./admission-pins.json',import.meta.url)),
      json(new URL('./policy.json',import.meta.url)),
      json(new URL('../../foundation-scheduler/admission-candidate-v1/pins.json',import.meta.url)),
      json(new URL('../../foundation-scheduler/integration-candidate-v1/policy.json',import.meta.url)),
    ]);
  assert.equal(hash(policyBytes),pins.policySha256);
  assert.equal(hash(parentPinsBytes),pins.parentAdmissionPinsSha256);
  assert.equal(hash(parentBytes),pins.parentPolicySha256);
  assert.equal(policy.parentRecipeSha256,pins.parentRecipeSha256);
  assert.deepEqual(policy.parentExpectedNativeSourceManifest,parent.expectedNativeSourceManifest);
  assert.equal(policy.expectedNativeSourceManifest.length,342);
  assert.equal(policy.addedSourcePaths.length,36);
  assert.equal(policy.privateTargetCpp.length,5);

  const strictSources=layer(layer(parentPins.parentStrict.nativeSourceSha256,parent),policy);
  for(const path of ['runtime/node_tick_queue.cpp','runtime/node_tick_queue.h'])
    strictSources[path]=parent.sourceLayer[path].afterSha256;
  const protectedSources=layer(layer(parentPins.parentProtected.sourceSha256,parent),policy);
  const allCpp=policy.expectedNativeSourceManifest.filter(row=>row.path.endsWith('.cpp')&&/^(builtins|runtime)\//.test(row.path)).map(row=>row.path);
  assert.equal(allCpp.length,61);
  const activeCpp=allCpp.filter(path=>(ticks||path!=='runtime/node_tick_queue.cpp')&&(web||path!=='builtins/node-compat/stream-web-kernel.cpp'));
  function command(path){
    const flags=['-O3','-DNDEBUG','-DNODE_COMPAT_STRICT_INITIALIZATION=1','-DNODE_COMPAT_ENTROPY_POLICY=1'];
    if(ticks)flags.push('-DNODE_COMPAT_INTERNAL_TICKS=1');
    if(events)flags.push('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1');
    if(web&&path.startsWith('builtins/node-compat/'))flags.push('-DNODE_COMPAT_STREAM_WEB=1');
    if(classic&&policy.privateTargetCpp.includes(path))flags.push('-DNODE_COMPAT_CLASSIC_STREAMS=1');
    if(entropy==='runtime-only')flags.push('-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1');
    if(gc&&policy.privateTargetCpp.includes(path))flags.push('-DNODE_COMPAT_GC_STRESS=1');
    // An intentionally non-executable path, no shell command evaluation and no
    // -fsyntax-only masquerading as a production compile command.
    return '/synthetic/NOT-A-COMPILER/clang++ '+flags.join(' ')+
      ' -c /synthetic/NO-BUILD/source/'+path+' -o /synthetic/NO-BUILD/objects/'+path+'.o';
  }
  const layout=new Map(activeCpp.map(path=>[path,command(path)]));
  const embedding=[command('embedding/embedding.cpp')];
  const privateCommands=policy.privateTargetCpp.filter(path=>layout.has(path)).map(path=>layout.get(path));
  assert.equal(privateCommands.length,web?5:4);
  const strictCpp=Object.keys(strictSources).filter(path=>path.endsWith('.cpp')&&(ticks||path!=='runtime/node_tick_queue.cpp'));
  assert.equal(strictCpp.length,ticks?4:3);
  const registration=[layout.get('builtins/node-compat/register.cpp')];

  const options={CMAKE_BUILD_TYPE:'Release',WEVAL:'OFF',USE_WASM_OPT:'ON',
    ENABLE_BUILTIN_NODE_COMPAT:'ON',ENABLE_JS_DEBUGGER:'OFF',ENABLE_BUILTIN_WPT_SUPPORT:'OFF',
    NODE_COMPAT_LOCKED_RUST:'ON',NODE_COMPAT_OOM_TESTING:'OFF',
    NODE_COMPAT_PATH:'ON',NODE_COMPAT_EVENTS:on(events),NODE_COMPAT_STRING_DECODER:on(stringDecoder),
    NODE_COMPAT_ASSERT:'ON',NODE_COMPAT_QUERYSTRING:'ON',NODE_COMPAT_UTIL:'ON',
    NODE_COMPAT_STREAM_WEB:on(web),NODE_COMPAT_GC_STRESS:on(gc),NODE_COMPAT_INTERNAL_TICKS:on(ticks),
    NODE_COMPAT_CLASSIC_STREAMS:on(classic),NODE_COMPAT_ENTROPY_MODE:entropy==='off'?'OFF':'RUNTIME_ONLY'};
  const tickPolicy={version:policy.version,enabled:ticks,sourcePolicyInstalled:true,
    parentRecipeSha256:policy.parentRecipeSha256,
    parentNativeManifestCanonicalSha256:policy.parentNativeManifestCanonicalSha256,
    parentPrivateTickPolicyFileSha256:pins.parentPolicySha256,parentPrivateTickHelperSha256:pins.parentHelperSha256,
    nativePatchSha256:policy.nativePatchSha256,embeddingPatchSha256:policy.embedding.patchSha256,
    embeddingBeforeSha256:policy.embedding.beforeSha256,embeddingAfterSha256:policy.embedding.afterSha256,
    policyFileSha256:pins.policySha256,helperSha256:pins.helperSha256,sourceLayer:copy(policy.sourceLayer),
    limits:copy(parent.limits),addsExternalCapabilities:false,publicProcessModule:false,
    resetSafeReuse:'OPEN; cancellation and teardown not established',requestedCMake:on(ticks),observedCMake:on(ticks),
    actualLayoutCompileCommands:[...layout.values()],actualEmbeddingCompileCommands:[...embedding],
    actualQueueCompileCommands:ticks?[layout.get('runtime/node_tick_queue.cpp')]:[]};
  const classicPolicy={version:policy.classicPolicyVersion,enabled:classic,policyFileSha256:pins.policySha256,
    helperSha256:pins.helperSha256,parentRecipeSha256:policy.parentRecipeSha256,
    parentSourceManifestCanonicalSha256:policy.parentNativeManifestCanonicalSha256,
    nativePatchSha256:policy.nativePatchSha256,addedSourcePaths:copy(policy.addedSourcePaths),moduleManifest:policy.classicManifest,
    requestedCMake:on(classic),observedCMake:on(classic),addsExternalCapabilities:false,publicProcessModule:false,
    actualPrivateTargetCompileCommands:[...privateCommands],actualRegistrationCompileCommands:[...registration]};
  const strictPolicy={version:policy.strictPolicyVersion,parentSourcePolicy:copy(parentPins.parentStrict),
    patchSha256:parentPins.parentStrict.patchSha256,basePolicy:copy(parentPins.parentStrict.basePolicy),
    embeddingBoundaryPatchSha256:parentPins.parentStrict.embeddingBoundaryPatchSha256,
    nativeSourceSha256:strictSources,actualNativeCompileCommands:strictCpp.map(path=>layout.get(path))};
  const protectedPolicy={version:policy.protectedPolicyVersion,parentSourcePolicy:copy(parentPins.parentProtected),
    enabled:events,sourceSha256:protectedSources,patchSha256:parentPins.parentProtected.patchSha256,
    strictPolicyVersion:strictPolicy.version,prerequisiteCMakeOptions:copy(parentPins.prerequisiteCMakeOptions),
    actualLayoutCompileCommands:[...layout.values()],actualEmbeddingCompileCommands:[...embedding]};
  const tickPatch={name:parent.version+'-boundary',sha256:parent.embedding.patchSha256,
    baseRevision:parentPins.componentizeJsRevision,applied:true,files:['embedding/embedding.cpp']};

  const metadata={syntheticMetadataOnly:true,
    syntheticNotice:'PARSER TEST INPUT ONLY: /synthetic compiler strings and required true model fields are not build, patch, source-capture or execution attestations.',
    buildRecipeSha256:pins.productionRecipeSha256,classicStreamsEnabled:classic,internalTicksEnabled:ticks,
    profileEnabled:true,strictInitialization:true,abiFixEnabled:true,bigIntFixEnabled:true,
    oomTesting:false,debuggerEnabled:false,wptSupportEnabled:false,
    pathEnabled:true,eventsEnabled:events,stringDecoderEnabled:stringDecoder,assertEnabled:true,
    querystringEnabled:true,utilEnabled:true,streamWebEnabled:web,gcStress:gc,entropyPolicy:entropy,
    requestedCMakeOptions:copy(options),observedCMakeOptions:copy(options),hostApi:'wasi-0.2.10',
    generatedRustProject:{syntheticMetadataOnly:true,cargoBuildLocked:true,manifestAndLockCheckedBeforeAndAfterBuild:true},
    sourceInputsCapturedBeforeBuild:true,componentizeSourcesCapturedBeforeBuild:true,buildRecipeCheckedBeforeAndAfterBuild:true,
    classicTraceSourcePolicy:copy(policy.classicTraceSourcePolicy),
    sourceManifest:copy(policy.expectedNativeSourceManifest),strictEventExceptionPolicy:strictPolicy,
    protectedAbortListenerPolicy:protectedPolicy,protectedAbortListenerEnabled:events,
    internalTickPolicy:tickPolicy,classicStreamsPolicy:classicPolicy,
    componentizeSourceManifest:parentPins.parentExternalSourceManifest.map(row=>({...row,
      sha256:row.path==='embedding/embedding.cpp'?policy.embedding.afterSha256:row.sha256})),
    componentizeJsRevision:parentPins.componentizeJsRevision,
    componentizeJsPatches:[...copy(parentPins.parentPatchChain),tickPatch],
    actualEmbeddingCompileCommands:[...embedding],actualRegistrationCompileCommands:[...registration],
    actualStreamWebKernelCompileCommands:web?[layout.get('builtins/node-compat/stream-web-kernel.cpp')]:[]};
  // No validator import/call here: the caller must first create and verify the
  // complete staged342 source root. Negative tests can mutate this plain model.
  return{syntheticMetadataOnly:true,metadata,
    sourceRoot:resolve(sourceRoot??fileURLToPath(new URL('./source/',import.meta.url))),
    parentProtectedSources:copy(parentPins.parentProtected.sourceSha256),
    parentProtectedPatch:parentPins.parentProtected.patchSha256,
    contractInputs:{admissionPinsSha256:hash(pinsBytes),policySha256:hash(policyBytes),
      parentAdmissionPinsSha256:hash(parentPinsBytes),parentPolicySha256:hash(parentBytes)},
    scope:'Synthetic source-model positive/negative fixture; no engine identifier, artifact, build or runtime proof'};
}
