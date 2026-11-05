"""Seal this independent DATA packet only; no owner imports or actions."""
import hashlib
import json
from pathlib import Path

OWN = Path(__file__).resolve().parent
S = OWN.parent
BASE = Path('/private/tmp/starling-node-compat')


def desc(p):
    p=Path(p).resolve(); data=p.read_bytes()
    return dict(path=str(p),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))


def load(p): return json.loads(Path(p).read_bytes())
def write(name,value): (OWN/name).write_text(json.dumps(value,indent=2)+'\n')


a=load(OWN/'data-audit.json'); g=load(OWN/'binary-import-graph.json')
assert a['verifiedPassed'] and a['checks']==64758 and a['uniquePaths']==6610
pure=BASE/'scheduler-resource-component-v1-pure'
timer=BASE/'scheduler-resource-component-v1-resource'
source=desc(S/'resource-component-candidate-v1/index.json')
refs=load(S/'resource-component-candidate-v1/references.json')
pure_root=load(S/'resource-component-pure-v1-root-results.json')
timer_root=load(S/'resource-component-resource-v1-root-results.json')
pure_artifacts={
 'component':desc(pure/'worker/component.wasm'),
 'core':desc(pure/'worker/transpiled/scheduler_resource.core.wasm'),
 'glue':desc(pure/'worker/transpiled/scheduler_resource.js'),
 'dts':desc(pure/'worker/transpiled/scheduler_resource.d.ts'),
 'packageJson':desc(pure/'worker/transpiled/package.json'),
 'emittedWit':desc(pure/'worker/emitted.wit'),
 'transpileMetadata':desc(pure/'worker/transpile-metadata.json'),
 'interfaceAudit':desc(pure/'worker/interface-audit.json'),
 'publicAbiAudit':desc(pure/'worker/public-abi-static-audit.json'),
 'bundle':desc(pure/'worker/bundled-guest.mjs'),
 'bundleGraph':desc(pure/'worker/bundle-graph.json'),
 'workerIndex':desc(pure/'worker/index.json'),
 'workerCompletion':desc(pure/'worker/completion.json'),
 'parentResult':desc(pure/'results.json'),
 'outputIndex':desc(pure/'index.json'),
 'outputCompletion':desc(pure/'completion.json'),
 'externalParentTerminal':pure_root['externalTerminal'],
 'ownedWorkerTerminal':desc(pure/'processes/componentize.terminal.json'),
 'rootAuthority':pure_root['rootAuthority'],
 'constructionConfig':pure_root['config']}
timer_artifacts={
 'component':desc(timer/'worker/component.wasm'),
 'emittedWit':desc(timer/'worker/emitted.wit'),
 'preAdmissionCapture':desc(timer/'worker/pre-final-interface-audit.json'),
 'rejectionTransport':desc(timer/'worker/construction-rejection-transport.json'),
 'workerFailure':desc(timer/'worker/failure.json'),
 'parentFailure':desc(timer/'failure.json'),
 'bundle':desc(timer/'worker/bundled-guest.mjs'),
 'bundleGraph':desc(timer/'worker/bundle-graph.json'),
 'componentOptions':desc(timer/'worker/component-options.json'),
 'externalParentTerminal':timer_root['externalTerminal'],
 'ownedWorkerTerminal':desc(timer/'processes/componentize.terminal.json'),
 'rootAuthority':timer_root['rootAuthority'],
 'constructionConfig':timer_root['config']}
result=dict(schemaVersion=1,
 state='INDEPENDENT_RESOURCE342_COMPONENT_RESULTS_AND_CLOCK_POLICY_FAILURE_REVIEW_PASSED_V1',
 verifiedPassed=True,reviewScope='Pure construction artifact DATA PASS and rejected timer construction/failure/graph DATA verified; separate scopes.',
 componentSourceIndexSha256=source['sha256'],resourceSourceIndexSha256=refs['resourceSourceIndex']['sha256'],
 nativeSourceFiles=342,externalEmbeddingSources=3,selectedManifestCount=9,
 nativeEngine=refs['engine'],nativeMetadata=refs['metadata'],
 sourceIndex=source,sourceReview=pure_root['sourceReview'],controllerSourceIndex=pure_root['controllerSourceIndex'],
 controllerSourceReview=pure_root['controllerSourceReview'],actualBootstrapReview=refs['actualBootstrapReview'],
 configuredSourceRoot=refs['configuredSourceRoot'],frozenSourceRoot=refs['frozenSourceRoot'],
 packagingRoot=refs['packagingRoot'],toolchainRoot=refs['toolchainRoot'],packagerRoot=refs['packagerRoot'],
 pureArtifactReviewPassed=True,pureConstructionAdmissionPassed=True,pureRawParentExitCode=0,pureRawWorkerExitCode=0,
 purePublicAbiFunctions=['run'],purePublicAbi=dict(run='() -> string'),pureJsHelper='exact terminal empty _util',
 pureEmittedImports=[],pureCoreImports=[],pureEmbeddedCoreByteIdenticalToTranspiledCore=True,
 pureGeneratedLoadingProtocolObserved='Direct ESM/TLA; await $init; same-directory core URL and node:fs/promises source. No import executed.',
 pureArtifacts=pure_artifacts,pureActualFiles=27,
 timerFailureVerified=True,timerConstructionAdmissionPassed=False,timerRawParentExitCode=1,timerRawWorkerExitCode=1,
 timerWholeComponentCapturedBeforeAdmission=True,timerArtifactIndependentRuntimeOrLoadingPass=False,
 timerSelectedInterfaces=a['fixtures']['resource']['selectedInterfaces'],timerEmittedImports=a['fixtures']['resource']['emittedImports'],
 timerUnexpectedInterfaces=sorted(set(a['fixtures']['resource']['emittedImports'])-set(a['fixtures']['resource']['selectedInterfaces'])),
 timerArtifacts=timer_artifacts,timerActualFiles=16,timerIndexedOrCompleted=False,timerTranspiled=False,
 timerBinaryRootFunctionCounts={i['name']:len(i['functions']) for i in g['resource']['rootImports']},
 timerResourceOnlyRootInterfaces=['wasi:io/error@0.2.10'],
 resourceOnlyDoesNotMeanNoDestructorBinding=True,
 timerCoreModuleBytes=[m['moduleBytes'] for m in g['resource']['modules']],
 preview1ClockBinding='core0.clock_time_get -> core2 table shim slot5 -> core3 element fixup -> core1.clock_time_get',
 adapterWallClockBinding='core1.wall-clock.now -> core2 slot6 -> core3 fixup -> root wall-clock@0.2.10.now',
 adapterStreamWriteBinding='core1.blocking-write-and-flush -> core2 slot7 -> core3 fixup -> root streams@0.2.10 method',
 independentlyEstablishedStrictPolicyMismatch=True,exactOpaqueThrownErrorCauseProved=False,
 sourcePolicyWidened=False,adapterFullBinaryEqualsRetainedCoreClaim=False,
 rootClockFailurePacket=a['rootClockFailurePacket'],actualStubWasiSource=a['actualStubWasiSource'],
 graph=desc(OWN/'binary-import-graph.json'),decoder=desc(OWN/'binary-graph.py'),
 audit=desc(OWN/'data-audit.json'),reader=desc(OWN/'read-evidence.py'),inputHashes=desc(OWN/'input-hashes.json'),
 readerHistory=desc(OWN/'reader-history.json'),clockPruningProposal=desc(OWN/'clock-pruning-decision.json'),
 checks=a['checks'],uniquePaths=a['uniquePaths'],sourceInputs=5399,physicalPackagingFiles=4934,toolLinks=22,
 protectedNativeFrozenCopies=666,protectedNativeOriginalEntries=663,
 wholeRawRecordsVerified=True,allObservedOwnedGroupsGone=True,signals=[],forcedCleanup=False,timeouts=False,
 initializationExecutedByComponentization=True,ordinaryGuestExportsInvoked=False,generatedModuleImported=False,
 timerRuntimeInvoked=False,asyncScalarRuntimeProved=False,reviewerOwnerModulesImported=False,
 reviewerForeignToolsOrRuntimeActionsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False,
 sourcePromotionAllowed=False,performanceClaim=False,grantsAnyActionAuthority=False,
 limitations=[
  'Pure construction proof does not establish run() return values or any ordinary export/async runtime behavior.',
  'Timer component is rejected under unchanged strict2; captured bytes are not admitted construction or runtime artifacts.',
  'Bindings are static topology, not observed execution of clock/stdio/stream/error functions or internal adapter branch reachability.',
  'io/error is resource-only in explicit WIT functions, but its destructor is canonically bound.',
  'Finite decoder is not a general WebAssembly validator; no engine/adapter code or data payload decoded, only generated table shims.',
  'Actual selected adapter source role is authenticated; optimized core1 is not claimed byte-identical to full53512 adapter.',
  'Exact opaque thrown object cause is unobserved; strict policy mismatch is independently demonstrated.',
  'Future pruning/Date/wall-clock profile and all runtime/action authorities remain unissued.'
 ])
write('results.json',result)
write('result-contract.json',dict(schemaVersion=1,
 state='RESOURCE_COMPONENT_AND_CLOCK_FAILURE_DATA_RESULT_CONTRACT_V1',
 requiredReviewState=result['state'],
 requiredFixedValues={k:result[k]for k in[
  'schemaVersion','verifiedPassed','componentSourceIndexSha256','resourceSourceIndexSha256','nativeSourceFiles',
  'pureArtifactReviewPassed','pureConstructionAdmissionPassed','timerFailureVerified','timerConstructionAdmissionPassed',
  'pureRawParentExitCode','pureRawWorkerExitCode','timerRawParentExitCode','timerRawWorkerExitCode',
  'ordinaryGuestExportsInvoked','generatedModuleImported','timerRuntimeInvoked','sourcePolicyWidened','operationalAdmission',
  'runtimeAcceptanceClaim','grantsAnyActionAuthority']},
 requiredPureArtifacts=pure_artifacts,requiredRejectedTimerArtifacts=timer_artifacts,
 requiredPureEmittedImports=[],requiredTimerSelectedInterfaces=result['timerSelectedInterfaces'],
 requiredTimerEmittedImports=result['timerEmittedImports'],requiredNativeEngine=refs['engine'],requiredNativeMetadata=refs['metadata'],
 graph=result['graph'],clockPruningProposal=result['clockPruningProposal'],
 artifactScopesMustRemainSeparate=True,issuesNoActionAuthority=True))
write('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_RESOURCE_COMPONENT_AND_CLOCK_FAILURE_DATA_REVIEW_V1',
 result=desc(OWN/'results.json'),contract=desc(OWN/'result-contract.json'),graph=result['graph'],
 inputHashes=result['inputHashes'],actualPureRootObservation=a['fixtures']['pure']['rootObservation'],
 actualRejectedTimerRootObservation=a['fixtures']['resource']['rootObservation'],ownerActionsInvoked=False))
files=[]
for p in sorted(OWN.iterdir()):
 if p.is_file() and p.name!='index.json':
  d=desc(p);d['path']=p.name;files.append(d)
write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_RESOURCE_COMPONENT_RESULTS_AND_CLOCK_FAILURE_REVIEW_V1',files=files))
for row in files:
 actual=desc(OWN/row['path']);assert actual['sha256']==row['sha256']and actual['bytes']==row['bytes']
assert {p.name for p in OWN.iterdir()}=={r['path']for r in files}|{'index.json'}
print(json.dumps(dict(index=desc(OWN/'index.json'),result=desc(OWN/'results.json'),contract=desc(OWN/'result-contract.json'),members=len(files))))
