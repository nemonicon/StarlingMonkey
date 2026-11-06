// Pure current-combined355 runtime contracts. No module/process/guest import.
import {isDeepStrictEqual as same} from 'node:util';
import {createHash} from 'node:crypto';
export const need=(v,m)=>{if(!v)throw Error(m);};
export const sha=b=>createHash('sha256').update(b).digest('hex');
export const IDS=Object.freeze(['pure','resource','fatal','init-fatal','clock-snapshot','surviving-interest']);
export const CLOCKS=Object.freeze(['wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:io/poll@0.2.10']);
export const sorted=a=>[...a].sort();
export function phaseModel(r,own,refs,fixture,phase){
 need(r?.schemaVersion===1&&r.state==='ROOT_REVIEWED_COMBINED355_NATIVE_RUNTIME_PHASE_V3'&&same(r.sourceIndex,own)&&r.phase===phase,'Genuine own runtime phase/Source');
 need(['map','run','fatal'].includes(phase)&&r.fixtureId===fixture.id&&r.worldName===fixture.worldName&&same(r.fixtureSource,fixture.source)&&same(r.fixtureWit,fixture.wit),'Exact held fixture/phase');
 need(r.nativeSourceFiles===355&&r.externalEmbeddingSources===3&&r.fullMetadataFields===80&&r.selectedWholeManifests===11&&same(r.nativeEngine,refs.nativeEngine)&&same(r.nativeMetadata,refs.nativeMetadata),'Current full80/355+3/11 context');
 need(same(r.nativeReadOnlyConfig,refs.readOnlyConfig)&&same(r.actualBootstrapReview,refs.actualBootstrapReview)&&same(r.actualReadOnlyReview,refs.actualReadOnlyReview)&&r.nativeReadOnlyApiAllowed===true,'Actual combined retained API prerequisites');
 need(r.outputRoot===refs.outputBase+'-'+fixture.id+'-'+phase&&r.externalOutputRoot===r.outputRoot+'-external-root','Fixed fresh perfixture/phase roots');
 need(r.mappingOnlyAllowed===(phase==='map')&&r.jcoCompilerHelpersAllowed===(phase==='map'),'No accidental compiler/application phase mixing');
 const ordinary=phase==='run'||phase==='fatal';need(r.generatedApplicationImportAllowed===ordinary&&r.ordinaryGuestExportsAllowed===ordinary&&r.stockWasmtimeAllowed===ordinary,'Only separately reviewed mapped ordinary phase');
 need(r.nodePureOracleAllowed===(phase==='run'&&fixture.id==='pure')&&r.standardShimWorkerThreadsAllowed===ordinary,'Only pure Node oracle and real standard shim workers');
 need(r.requiredExternalParentDeadlineSeconds===1200&&r.childDeadlineMs===180000&&r.maxOutputBytes===16777216,'Finite genuine external/child ownership bounds');
 need(r.wallClockCoarseAllowanceMs===1&&r.clockAdjustmentPolicy==='inconclusive-if-host-wall-clock-decreases'&&r.performanceTimeOriginEpochAssumed===false,'Explicit1ms coarse allowance, no epoch/clock-adjustment fiction');
 need(r.expectedFatalCallbackAcceptanceAllowed===false&&r.current355NativeCallbackDiagnosticAvailable===false,'No invented current355 diagnostic or fatal gate permission');need(same(r.selectedInterfaces,fixture.selectedInterfaces),'Explicit catalogue interface selection, actual emitted graph checked independently');
 for(const k of ['componentConstructionAllowed','nativeBuildAllowed','nativeFreezeAllowed','keyOrCryptoAllowed','gcOrFaultActionsAllowed','debugOrUnsafeResetAllowed','customHostServicesAllowed','adapterPromotionAllowed','metadataProjectionAllowed','nativeDiagnosticVariantAllowed','fullClockProfileAcceptance','runtimeAcceptanceClaim','operationalAdmission','timingAllowed'])need(r[k]===false,'No extra phase '+k);
 if(phase==='map')need(r.actualMappedReview===null&&r.actualMappedContract===null,'No invented mapping result');
 if(ordinary)need(r.actualMappedReview&&r.actualMappedContract,'Independent actual mapped DATA before generated import');
 if(phase==='fatal')need(fixture.id==='fatal'&&r.actualResourceRuntimeReview&&r.actualResourceRuntimeContract,'Actual same-lineage handled-error seven-case positive prerequisite');

 if(phase==='run')need(['pure','resource','clock-snapshot','surviving-interest'].includes(fixture.id),'Finite ordinary positive fixtures');return true;
}
export function artifactModel(p,contract,refs,fixture,root){
 need(p?.schemaVersion===1&&p.verifiedPassed===true&&p.state===contract.requiredReviewState&&p.state==='INDEPENDENT_COMBINED355_'+fixture.id.replaceAll('-','_').toUpperCase()+'_COMPONENT_ARTIFACT_REVIEW_PASSED_V1','Actual perfixture artifact DATA review, not Source proposal');
 need(p.fixtureId===fixture.id&&p.componentSourceIndexSha256===refs.callerSourceIndex.sha256&&p.nativeSourceFiles===355&&p.externalEmbeddingSources===3&&p.fullMetadataFields===80&&p.selectedWholeManifests===11,'Whole current artifact/native Source generation');
 need(p.engineSha256===refs.nativeEngine.sha256&&p.metadataSha256===refs.nativeMetadata.sha256&&same(p.artifacts,contract.artifacts)&&same(p.artifacts.fixtureSource,fixture.source)&&same(p.artifacts.fixtureWit,fixture.wit),'Exact artifact map/held physical fixture');
 need(p.componentSha256===p.artifacts.component.sha256&&same(p.artifacts.nativeEngine,refs.nativeEngine)&&same(p.artifacts.nativeMetadata,refs.nativeMetadata),'Actual reviewed component/frozen binary tuple');
 need(same(sorted(p.publicAbiFunctions),sorted(fixture.exports.map(x=>x.name)))&&same(sorted(p.emittedImports),sorted(root.expectedEmittedImports))&&p.emittedImports.every(x=>fixture.selectedInterfaces.includes(x)),'Exact perfixture ABI/import graph; no generic clock API assumption');
 need(same(p.publicAbiSignatures,fixture.exports.map(x=>({name:x.name,params:x.arguments,result:x.result}))),'Whole actual scalar ABI parameter types, not function names alone');
 if(fixture.id==='pure')need(p.emittedImports.length===0,'Pure remains imports[]');
 if(fixture.id==='resource')need(same(sorted(p.emittedImports),sorted(CLOCKS)),'Resource exact three reviewed standard interfaces');
 for(const k of ['ordinaryGuestExportsInvoked','generatedApplicationModuleImported','keyOrCryptoWorkloadsInvoked','operationalAdmission','runtimeAcceptanceClaim'])need(p[k]===false,'Artifact construction-only '+k);
 need(p.binaryGraph&&p.generatedFiles&&p.artifacts.allGeneratedFiles.length>0,'Whole original component graph/generated loading tuple required');return true;
}
export function mappingOptions(refs,id){return{name:'combined_'+id.replaceAll('-','_'),wasiShim:false,map:{'wasi:clocks/*':refs.shimClocksUrl+'#*','wasi:io/*':refs.shimIoUrl+'#*'}};}
export function namespaceModel(ns,fixture){
 need(ns&&typeof ns==='object'&&Object.getPrototypeOf(ns)===null&&same(Object.getOwnPropertyNames(ns).sort(),[...fixture.exports.map(x=>x.name),'_util'].sort()),'Actual ESM namespace before then/property coercion');
 for(const x of fixture.exports)need(typeof ns[x.name]==='function'&&ns[x.name].length===x.arguments.length,'Exact synchronous scalar function/arity '+x.name);
 need(ns._util&&Object.getPrototypeOf(ns._util)===Object.prototype&&Reflect.ownKeys(ns._util).length===0,'Exact empty terminal Jco helper');return true;
}
export function scalarArguments(fixture,name,args){const exp=fixture.exports.find(x=>x.name===name);need(exp&&Array.isArray(args)&&args.length===exp.arguments.length,'Exact actual public ABI');if(name==='run'&&fixture.id==='resource')need(Number.isInteger(args[0])&&args[0]>=0&&args[0]<7,'Only sevenu32 case IDs');else need(args.length===0,'Sole no-argument scalar');return true;}
export function pureResult(raw,call){need(typeof raw==='string','Complete pure scalar');const v=JSON.parse(raw);need(same(v,{schemaVersion:1,initial:0,calls:call,hex:'c3a92201',timerRequested:false}),'Full pure record/counter/Buffer bytes');return v;}
export function realtimeBracket(v,before,after,allowance=1){
 need(Number.isSafeInteger(before)&&Number.isSafeInteger(after)&&allowance===1,'Recorded host wall bracket/coarse policy');need(after>=before,'Inconclusive decreasing host clock: refuse timing acceptance');
 for(const sample of [v.before,v.after])for(const name of ['dateNow','dateObject'])need(sample[name]>=before-allowance&&sample[name]<=after+allowance,'Live wall-time sample within explicit coarse host bracket');
 return{policy:'whole-host-call-bracket-plus1ms-coarse-allowance',before,after,allowanceMs:1,performanceTimeOriginEpochAssumed:false,nativeOffsetResumptionProved:false};
}
export function terminalModel(t,{failureObservation=false}={}){
 need(t?.closed===true&&t.ownedGroupGone===true&&t.spawnError===null&&t.timedOut===false&&t.externalSignal===null&&t.outputLimitExceeded===false&&t.errors.length===0&&t.signals.length===0&&t.signalCount===0,'Actual complete owned close/no timeout/signalling/overflow');
 if(!failureObservation)need(t.status===0&&t.signal===null&&t.terminalExitZeroObserved===true,'Actual raw0 positive');
 else need((Number.isInteger(t.status)&&t.status!==0&&t.signal===null||t.status===null&&t.signal==='SIGABRT')&&t.terminalExitZeroObserved===false,'Fresh bounded fatal observation; timeout/kill is not expected failure');return true;
}
export function fatalJcoObservation(t,marker,typed,caught,component,own){
 terminalModel(t,{failureObservation:true});need(marker?.state==='COMBINED355_FATAL_PUBLIC_CALL_ARMED_V3'&&same(marker.sourceIndex,own)&&same(marker.component,component)&&marker.fixtureId==='fatal'&&marker.name==='run'&&same(marker.args,[])&&marker.moduleImportCompleted===true&&marker.publicExportAboutToBeInvoked===true,'Durable actual post-import/pre-call marker');
 if(typed!==null)need(typed.schemaVersion===1&&typed.sequence===1&&typed.name==='run'&&same(typed.args,[])&&typed.kind==='throw','No ordinary return accepted as fatal');
 if(caught!==null)need(caught.capture?.captureFailures?.length===0,'Capture failure never fatal evidence');
 if(t.signal!=='SIGABRT')need(typed!==null&&caught?.capture?.attempted===1&&caught.capture.written===1,'Caught throw wholly retained; raw1 alone never enough');
 return{reachedBeforeCallMarker:true,typedThrowRetained:typed!==null,nativeAbortObserved:t.signal==='SIGABRT',workerFinallyExecutionProved:false,observedInvocationFailure:true,callbackCause:'inconclusive',expectedCallbackFailureProved:false,fatalCallbackGateSatisfied:false,nativeCallbackReachedObserved:false,uniqueOriginalJsErrorIdentityProved:false};
}
