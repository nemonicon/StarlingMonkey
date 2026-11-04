// Full source/metadata contract. This alone is never engine/runtime proof.
function loadContract(){
 const pinsBytes=readFileSync(new URL('./foundation-classic-streams/integration-candidate-v1/admission-pins.json',import.meta.url));
 assert.equal(hash(pinsBytes),PINS_SHA,'Unreviewed classic admission contract');
 const pins=JSON.parse(pinsBytes);
 const policyBytes=readFileSync(new URL('./foundation-classic-streams/integration-candidate-v1/policy.json',import.meta.url));
 assert.equal(hash(policyBytes),pins.policySha256);
 assert.equal(hash(readFileSync(new URL('./foundation-classic-streams/integration-candidate-v1/layer-policy.py',import.meta.url))),pins.helperSha256);
 const policy=JSON.parse(policyBytes);
 const parentPinsBytes=readFileSync(new URL('./foundation-scheduler/admission-candidate-v1/pins.json',import.meta.url));
 assert.equal(hash(parentPinsBytes),pins.parentAdmissionPinsSha256);
 const parentPolicyBytes=readFileSync(new URL('./foundation-scheduler/integration-candidate-v1/policy.json',import.meta.url));
 assert.equal(hash(parentPolicyBytes),pins.parentPolicySha256);
 assert.equal(hash(readFileSync(new URL('./foundation-scheduler/integration-candidate-v1/layer-policy.py',import.meta.url))),pins.parentHelperSha256);
 const parentPins=JSON.parse(parentPinsBytes),parent=JSON.parse(parentPolicyBytes);
 assert.deepEqual(policy.parentExpectedNativeSourceManifest,parent.expectedNativeSourceManifest);
 assert.equal(policy.parentRecipeSha256,pins.parentRecipeSha256);
 assert.equal(policy.expectedNativeSourceManifest.length,342);
 assert.equal(policy.addedSourcePaths.length,36);assert.equal(Object.keys(policy.sourceLayer).length,38);
 return{pins,policy,parentPins,parent};
}
function compose(map,parent,policy){return resolveLayer(resolveLayer(map,parent),policy);}
function hinted(metadata){return metadata.buildRecipeSha256===RECIPE_SHA||Object.hasOwn(metadata,'classicStreamsEnabled')||Object.hasOwn(metadata,'classicStreamsPolicy')||
 Object.hasOwn(metadata.requestedCMakeOptions??{},'NODE_COMPAT_CLASSIC_STREAMS')||Object.hasOwn(metadata.observedCMakeOptions??{},'NODE_COMPAT_CLASSIC_STREAMS')||
 (Array.isArray(metadata.sourceManifest)&&metadata.sourceManifest.some(row=>typeof row?.path==='string'&&row.path.startsWith('builtins/node-compat/classic-streams/'))) ||
 String(metadata.strictEventExceptionPolicy?.version).includes('classic-streams')||String(metadata.protectedAbortListenerPolicy?.version).includes('classic-streams');}
export function validateClassicSourceModel(metadata,{sourceRoot,parentProtectedSources,parentProtectedPatch}={}){
 assert(metadata&&typeof metadata==='object'&&!Array.isArray(metadata));
 assert((metadata.diagnosticOnly===undefined||metadata.diagnosticOnly===false)&&!Object.hasOwn(metadata,'internalTickDiagnosticPolicy'),'Diagnostic engines are never classic production');
 const{pins,policy,parentPins,parent}=loadContract();
 assert.equal(metadata.buildRecipeSha256,pins.productionRecipeSha256);
 assert.equal(typeof metadata.classicStreamsEnabled,'boolean');const enabled=metadata.classicStreamsEnabled;
 assert.equal(typeof metadata.internalTicksEnabled,'boolean');const ticksEnabled=metadata.internalTicksEnabled;
 for(const field of['profileEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled'])assert.equal(metadata[field],true,field);
 for(const field of['oomTesting','debuggerEnabled','wptSupportEnabled'])assert.equal(metadata[field],false,field);
 for(const[field,option]of[['pathEnabled','NODE_COMPAT_PATH'],['eventsEnabled','NODE_COMPAT_EVENTS'],['stringDecoderEnabled','NODE_COMPAT_STRING_DECODER'],
  ['assertEnabled','NODE_COMPAT_ASSERT'],['querystringEnabled','NODE_COMPAT_QUERYSTRING'],['utilEnabled','NODE_COMPAT_UTIL'],['streamWebEnabled','NODE_COMPAT_STREAM_WEB'],
  ['gcStress','NODE_COMPAT_GC_STRESS'],['internalTicksEnabled','NODE_COMPAT_INTERNAL_TICKS'],['classicStreamsEnabled','NODE_COMPAT_CLASSIC_STREAMS']]){
  assert.equal(typeof metadata[field],'boolean',field);for(const map of['requestedCMakeOptions','observedCMakeOptions'])assert.equal(metadata[map]?.[option],metadata[field]?'ON':'OFF');}
 if(enabled)for(const field of['eventsEnabled','stringDecoderEnabled','internalTicksEnabled'])assert.equal(metadata[field],true,'Classic prerequisite '+field);
 for(const[option,value]of Object.entries({CMAKE_BUILD_TYPE:'Release',WEVAL:'OFF',USE_WASM_OPT:'ON',ENABLE_BUILTIN_NODE_COMPAT:'ON',ENABLE_JS_DEBUGGER:'OFF',
  ENABLE_BUILTIN_WPT_SUPPORT:'OFF',NODE_COMPAT_LOCKED_RUST:'ON',NODE_COMPAT_OOM_TESTING:'OFF'}))for(const field of['requestedCMakeOptions','observedCMakeOptions'])assert.equal(metadata[field]?.[option],value);
 assert(['off','runtime-only'].includes(metadata.entropyPolicy));for(const field of['requestedCMakeOptions','observedCMakeOptions'])assert.equal(metadata[field].NODE_COMPAT_ENTROPY_MODE,metadata.entropyPolicy==='off'?'OFF':'RUNTIME_ONLY');
 assert(!(metadata.gcStress&&metadata.entropyPolicy==='runtime-only'),'RuntimeOnly+GC is outside this finite producer');
 assert.equal(metadata.hostApi,'wasi-0.2.10');assert.equal(metadata.generatedRustProject?.cargoBuildLocked,true);assert.equal(metadata.generatedRustProject?.manifestAndLockCheckedBeforeAndAfterBuild,true);
 for(const field of['sourceInputsCapturedBeforeBuild','componentizeSourcesCapturedBeforeBuild','buildRecipeCheckedBeforeAndAfterBuild'])assert.equal(metadata[field],true);
 const current=entries(metadata.sourceManifest);assert.equal(current.length,342);assert.deepEqual(current,entries(policy.expectedNativeSourceManifest));
 const immediate=current.filter(row=>!policy.addedSourcePaths.includes(row.path)).map(row=>({path:row.path,sha256:policy.sourceLayer[row.path]?.beforeSha256??row.sha256}));
 assert.equal(immediate.length,306);assert.deepEqual(immediate,entries(parent.expectedNativeSourceManifest));
 assert.equal(sourceDigest(immediate),policy.parentNativeManifestCanonicalSha256);
 const original=immediate.filter(row=>parent.sourceLayer[row.path]?.beforeSha256!==null).map(row=>({path:row.path,sha256:parent.sourceLayer[row.path]?.beforeSha256??row.sha256}));
 assert.equal(original.length,304);assert.equal(sourceDigest(original),parent.parentNativeManifestCanonicalSha256);
 const root=resolve(sourceRoot);assert(!lstatSync(root).isSymbolicLink());
 for(const row of current){let path=root;for(const part of row.path.split('/')){path=join(path,part);assert(!lstatSync(path).isSymbolicLink());}assert.equal(hash(readFileSync(path)),row.sha256,'Actual342 source '+row.path);}
 const strict=metadata.strictEventExceptionPolicy,protectedPolicy=metadata.protectedAbortListenerPolicy,ticks=metadata.internalTickPolicy,classic=metadata.classicStreamsPolicy;
 assert.equal(strict?.version,policy.strictPolicyVersion);assert.equal(protectedPolicy?.version,policy.protectedPolicyVersion);
 assert.deepEqual(strict.parentSourcePolicy,parentPins.parentStrict);assert.deepEqual(protectedPolicy.parentSourcePolicy,parentPins.parentProtected);
 assert.deepEqual(parentProtectedSources,parentPins.parentProtected.sourceSha256);assert.equal(parentProtectedPatch,parentPins.parentProtected.patchSha256);
 for(const key of['patchSha256','basePolicy','embeddingBoundaryPatchSha256'])assert.deepEqual(strict[key],parentPins.parentStrict[key]);
 const strictSources=compose(parentPins.parentStrict.nativeSourceSha256,parent,policy);
 for(const name of['runtime/node_tick_queue.cpp','runtime/node_tick_queue.h'])strictSources[name]=parent.sourceLayer[name].afterSha256;
 assert.deepEqual(strict.nativeSourceSha256,strictSources);assert.deepEqual(protectedPolicy.sourceSha256,compose(parentPins.parentProtected.sourceSha256,parent,policy));
 assert.equal(protectedPolicy.patchSha256,parentPins.parentProtected.patchSha256);assert.equal(protectedPolicy.strictPolicyVersion,strict.version);
 assert.equal(protectedPolicy.enabled,metadata.eventsEnabled);assert.equal(metadata.protectedAbortListenerEnabled,metadata.eventsEnabled);
 assert.deepEqual(protectedPolicy.prerequisiteCMakeOptions,parentPins.prerequisiteCMakeOptions);
 const external=parentPins.parentExternalSourceManifest.map(row=>({...row,sha256:row.path==='embedding/embedding.cpp'?policy.embedding.afterSha256:row.sha256}));
 assert.deepEqual(metadata.componentizeSourceManifest,external);assert.equal(metadata.componentizeJsRevision,parentPins.componentizeJsRevision);
 const tickPatch={name:parent.version+'-boundary',sha256:parent.embedding.patchSha256,baseRevision:parentPins.componentizeJsRevision,applied:true,files:['embedding/embedding.cpp']};
 assert.deepEqual(normalizedPatches(metadata.componentizeJsPatches),[...parentPins.parentPatchChain,tickPatch]);
 assert.equal(ticks?.version,policy.version);assert.equal(ticks.enabled,ticksEnabled);assert.equal(ticks.sourcePolicyInstalled,true);
 for(const[field,value]of Object.entries({parentRecipeSha256:policy.parentRecipeSha256,parentNativeManifestCanonicalSha256:policy.parentNativeManifestCanonicalSha256,
  parentPrivateTickPolicyFileSha256:pins.parentPolicySha256,parentPrivateTickHelperSha256:pins.parentHelperSha256,nativePatchSha256:policy.nativePatchSha256,
  embeddingPatchSha256:policy.embedding.patchSha256,embeddingBeforeSha256:policy.embedding.beforeSha256,embeddingAfterSha256:policy.embedding.afterSha256,
  policyFileSha256:pins.policySha256,helperSha256:pins.helperSha256}))assert.equal(ticks[field],value,field);
 assert.deepEqual(ticks.sourceLayer,policy.sourceLayer);assert.deepEqual(ticks.limits,parent.limits);assert.equal(ticks.addsExternalCapabilities,false);assert.equal(ticks.publicProcessModule,false);
 assert.equal(ticks.resetSafeReuse,'OPEN; cancellation and teardown not established');assert.equal(ticks.requestedCMake,ticksEnabled?'ON':'OFF');assert.equal(ticks.observedCMake,ticks.requestedCMake);
 assert.equal(classic?.version,policy.classicPolicyVersion);assert.equal(classic.enabled,enabled);assert.equal(classic.policyFileSha256,pins.policySha256);assert.equal(classic.helperSha256,pins.helperSha256);
 assert.equal(classic.parentRecipeSha256,policy.parentRecipeSha256);assert.equal(classic.parentSourceManifestCanonicalSha256,policy.parentNativeManifestCanonicalSha256);
 assert.equal(classic.nativePatchSha256,policy.nativePatchSha256);assert.deepEqual(classic.addedSourcePaths,policy.addedSourcePaths);assert.equal(classic.moduleManifest,policy.classicManifest);
 assert.equal(classic.requestedCMake,enabled?'ON':'OFF');assert.equal(classic.observedCMake,classic.requestedCMake);assert.equal(classic.addsExternalCapabilities,false);assert.equal(classic.publicProcessModule,false);
 const cpp=current.filter(row=>row.path.endsWith('.cpp')&&/^(builtins|runtime)\//.test(row.path)).map(row=>row.path);assert.equal(cpp.length,61);
 const active=cpp.filter(path=>(ticksEnabled||path!=='runtime/node_tick_queue.cpp')&&(metadata.streamWebEnabled||path!=='builtins/node-compat/stream-web-kernel.cpp'));
 const layout=new Map();assert(Array.isArray(ticks.actualLayoutCompileCommands));
 function command(source,candidates){const path=compiled(source,candidates,ticksEnabled,metadata.eventsEnabled,metadata.streamWebEnabled);const tokens=words(source);
  assert(tokens.includes('-O3')&&tokens.includes('-DNDEBUG')&&!tokens.includes('-UNDEBUG')&&!tokens.some(x=>x.startsWith('-DDEBUG')));
  macro(tokens,'NODE_COMPAT_CLASSIC_STREAMS',enabled&&policy.privateTargetCpp.includes(path));macro(tokens,'NODE_COMPAT_ENTROPY_RUNTIME_ONLY',metadata.entropyPolicy==='runtime-only');
  macro(tokens,'NODE_COMPAT_ENTROPY_POLICY',true);macro(tokens,'NODE_COMPAT_GC_STRESS',metadata.gcStress&&policy.privateTargetCpp.includes(path));return path;}
 for(const row of ticks.actualLayoutCompileCommands){const path=command(row,cpp);assert(!layout.has(path));layout.set(path,row);}
 assert.deepEqual([...layout.keys()].sort(),active.sort());assert.deepEqual(protectedPolicy.actualLayoutCompileCommands,ticks.actualLayoutCompileCommands);
 const embedding=ticks.actualEmbeddingCompileCommands;assert(Array.isArray(embedding)&&embedding.length===1);command(embedding[0],['embedding/embedding.cpp']);
 assert.deepEqual(metadata.actualEmbeddingCompileCommands,embedding);assert.deepEqual(protectedPolicy.actualEmbeddingCompileCommands,embedding);
 assert.deepEqual(ticks.actualQueueCompileCommands,ticksEnabled?[layout.get('runtime/node_tick_queue.cpp')]:[]);
 assert.deepEqual(metadata.actualStreamWebKernelCompileCommands,metadata.streamWebEnabled?[layout.get('builtins/node-compat/stream-web-kernel.cpp')]:[]);
 const strictCpp=Object.keys(strictSources).filter(path=>path.endsWith('.cpp')&&(ticksEnabled||path!=='runtime/node_tick_queue.cpp'));
 assert.deepEqual([...strict.actualNativeCompileCommands].sort(),strictCpp.map(path=>layout.get(path)).sort());
 const privateCommands=policy.privateTargetCpp.filter(path=>layout.has(path)).map(path=>layout.get(path));assert.equal(privateCommands.length,metadata.streamWebEnabled?5:4);
 assert.deepEqual([...classic.actualPrivateTargetCompileCommands].sort(),privateCommands.sort());
 assert.deepEqual(classic.actualRegistrationCompileCommands,[layout.get('builtins/node-compat/register.cpp')]);assert.deepEqual(metadata.actualRegistrationCompileCommands,classic.actualRegistrationCompileCommands);
 return Object.freeze({branch:policy.version,classicStreamsEnabled:enabled,internalTicksEnabled:ticksEnabled,sourceInputs:342,
  selectedClassicManifest:enabled?policy.classicManifest:null,runtimeOrGuestExecutionProof:false,resetSafeReuse:'OPEN'});
}
export function validateClassicSourceAdmission(metadata,options){
 assert(metadata&&typeof metadata==='object');
 if(!hinted(metadata))return null;
 assert(metadata.syntheticMetadataOnly===undefined||metadata.syntheticMetadataOnly===false,'Synthetic source models never enter production admission');
 return validateClassicSourceModel(metadata,options);
}
