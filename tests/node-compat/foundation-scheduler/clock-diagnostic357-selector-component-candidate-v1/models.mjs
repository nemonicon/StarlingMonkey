// Pure caller models. No engine, package, fixture or diagnostic API calls.
import assert from 'node:assert/strict';
export const SELECTED=Object.freeze(['wasi:clocks/wall-clock@0.2.10','wasi:clocks/monotonic-clock@0.2.10','wasi:io/poll@0.2.10']);
export const DISABLED=Object.freeze(['fetch-event','http','random','stdio']);
export function rootModel(r,own,refs){
 assert(r.schemaVersion===1&&r.state==='ROOT_REVIEWED_PRIVATE_CLOCK357_SELECTOR_CONSTRUCTION_V1');assert.deepEqual(r.sourceIndex,own);assert(r.sourceReviewedByRoot===true&&r.externalOwnedMonitorRequired===true&&r.freshOwnedNodeProcessRequired===true&&r.deadlineSeconds===1800);
 assert.deepEqual(r.engine,refs.engine);assert.deepEqual(r.metadata,refs.metadata);assert.deepEqual(r.nativeBuildReview,refs.nativeBuildReview);assert.deepEqual(r.nativeBuildContract,refs.nativeBuildContract);
 assert.deepEqual(r.selectedInterfaces,SELECTED);assert.deepEqual(r.disableFeatures,DISABLED);
 assert(r.packageInitializationAllowed===true&&r.componentConstructionAllowed===true&&r.engineInitializationDuringConstructionAllowed===true);
 for(const k of ['ordinaryGuestExportsAllowed','nativeSelectorProbeAllowed','clockRuntimeAllowed','cryptoAllowed','nativeBuildAllowed','freezeAllowed','publicProfileAdmission','snapshotOrReuseAcceptance','securityOrCostAcceptance','operationalAdmission'])assert(r[k]===false,k);
 assert(typeof r.outputRoot==='string'&&r.outputRoot.startsWith(refs.outputPrefix)&&r.privateTemporaryRoot===r.outputRoot+'-tmp');
 assert(r.sourceReview&&r.sourceReviewContract);assert(r.actualComponent===null&&r.actualRuntime===null);
}
export function nativeModel(p,m,refs,manifest,spec){
 assert(p.schemaVersion===1&&p.verifiedPassed===true&&p.state==='INDEPENDENT_CLOCK_DIAGNOSTIC357_NORMAL_OFF_NATIVE_BUILD_REVIEW_PASSED_V3');
 assert(p.sourceIndexSha256===refs.nativeProducerIndex.sha256&&p.nativeSourceFiles===357&&p.externalEmbeddingSources===3&&p.rawMetadataFields===82&&p.selectedWholeManifests===11);
 assert.deepEqual(p.engine,refs.engine);assert.deepEqual(p.metadata,refs.metadata);assert(p.rawRecipeExitCode===0&&p.rawWorkerExitCode===0&&p.rawOuterExitCode===0&&p.currentOriginalProtectionPassed===true&&p.allObservedOwnedGroupsGone===true);
 assert(p.engineOrGuestOrClockRuntimeInvoked===false&&p.operationalAdmission===false);
 assert(Object.keys(m).length===82&&m.engineSha256===refs.engine.sha256&&m.sourceManifest.length===357&&m.componentizeSourceManifest.length===3&&m.selectedModuleManifests.length===11);
 assert.deepEqual(p.metadataClassification,{state:'FINITE_CLOCK_DIAGNOSTIC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V2',nativeFiles:357,rawMetadataFields:82,engineRead:false,runtimeAccepted:false,grantsAuthority:false});
 assert.deepEqual(Object.keys(m).sort(),spec.expectedRawMetadataFields.slice().sort());assert.deepEqual(m.sourceManifest,spec.expectedNativeSourceManifest);assert.deepEqual(m.componentizeSourceManifest,spec.expectedComponentizeSourceManifest);assert.deepEqual(m.clockLifecycleDiagnosticSourcePolicy,spec.diagnosticSourcePolicy);
 assert(m.gcStress===false&&m.oomTesting===false&&m.debuggerEnabled===false&&m.entropyPolicy==='off');
 for(const field of ['requestedCMakeOptions','observedCMakeOptions'])for(const key of ['NODE_COMPAT_LIFECYCLE_DIAGNOSTICS','ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE','ENABLE_BUILTIN_WEB_PERFORMANCE'])assert(m[field][key]==='ON');
 assert(m.clockLifecycleDiagnosticSourcePolicy.privateBuiltin===manifest.moduleId&&m.clockLifecycleDiagnosticSourcePolicy.version===manifest.sourcePolicyVersion);
 const install=m.clockLifecycleDiagnosticBuildEvidence.actualInstallation;assert(install.namespace==='NS_DEF(diagnostics::clock_lifecycle)'&&install.count===1&&install.performanceTargetEnabled===true);
 assert(m.clockLifecycleDiagnosticBuildEvidence.actualSharedCompileCommands.length===7&&m.clockLifecycleDiagnosticBuildEvidence.nativeClockOrSelectorRuntimeInvoked===false);
 assert(m.sourceManifest.find(r=>r.path===manifest.cpp.path)?.sha256===manifest.cpp.sha256);
 assert.deepEqual(manifest.exports,['snapshot','clockStateV2','probeAllInvalidV2','default']);assert(manifest.privateDiagnosticOnly===true&&manifest.publicBuiltinMapAdmission===false);
}
export function witSurface(wit){
 assert(typeof wit==='string');const exports=[...wit.matchAll(/^\s*export\s+([^;]+);/gm)].map(m=>m[1].replace(/\s+/g,' ').trim()).sort();
 assert.deepEqual(exports,['clock-state: func() -> string','run: func(count: u32) -> string','snapshot: func() -> string']);return exports;
}
export function diagnostic(value){
 const type=typeof value;if(value===null||type==='string'||type==='boolean')return{type,value};if(type==='undefined')return{type};if(type==='number')return Number.isFinite(value)?{type,value}:{type,nonfinite:String(value)};
 const out={type,opaque:true,ownData:{}};
 try{for(const[k,d]of Object.entries(Object.getOwnPropertyDescriptors(value)))if(Object.hasOwn(d,'value')&&['name','message','stack','code','status','signal'].includes(k)){const v=d.value;if(v===null||['string','boolean'].includes(typeof v)||typeof v==='number'&&Number.isFinite(v))out.ownData[k]=v;}}catch{out.inspectionIncomplete=true;}return out;
}
