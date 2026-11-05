"""Seal this independent completed BUILD-only DATA packet; never imports owner code."""
import hashlib,json
from pathlib import Path
OWN=Path(__file__).resolve().parent;S=OWN.parent

def desc(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def load(p):return json.loads(Path(p).read_bytes())
def write(name,v):(OWN/name).write_text(json.dumps(v,indent=2)+'\n')

d=load(OWN/'data-results.json');b=load(OWN/'build-data.json');supp=load(OWN/'supplemental-data.json')
assert d['verifiedPassed']and d['checks']==1105410 and d['physicalInputFiles']==20761 and supp['verifiedPassed']
source_sha='88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1'
root=load(S/'task-selection-normal-off-build-v1-root-results.json');m=b['metadata']
source_root=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source')
primitive_donor=S/'independent-resource-normal-off-build-review-v1/review_io.py'
assert (OWN/'review_io.py').read_bytes()==primitive_donor.read_bytes()
artifacts=dict(actualBuildResult=d['actualBuildResult'],externalParentTerminal=d['externalParentTerminal'],ownedWorkerTerminal=d['ownedWorkerTerminal'],
 rootBuildAuthority=d['rootAuthority'],rootBuildConfig=d['rootConfig'],rootBuildObservation=d['rootObservation'],
 engine=d['engine'],metadata=d['metadata'],buildLog=d['buildLog'],
 sourceIndex=d['sourceIndex'],controllerSourceIndex=d['controllerSourceIndex'],
 actualCMakeCache=desc(m['cmakeCachePath']),actualCompileCommands=desc(m['compileCommandsPath']),
 actualNinja=desc(Path(m['cmakeCachePath']).parent/'build.ninja'),actualNinjaRules=desc(Path(m['cmakeCachePath']).parent/'CMakeFiles/rules.ninja'),
 sourcePolicy=desc(S/'task-selection-integration-candidate-v1/policy.json'),
 sourceHelper=desc(source_root/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1/layer-policy.py'),
 sourceRecipe=desc(source_root/'tests/node-compat/build-engine.sh'),
 buildData=desc(OWN/'build-data.json'),inputHashes=desc(OWN/'input-hashes.json'),supplement=desc(OWN/'supplemental-data.json'))
fixed=dict(schemaVersion=1,state='INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_NATIVE_BUILD_REVIEW_PASSED_V1',verifiedPassed=True,
 sourceIndexSha256=source_sha,taskSelectionSourceIndexSha256=source_sha,
 controllerSourceIndexSha256=d['controllerSourceIndex']['sha256'],variant='normal-off',nativeSourceFiles=342,
 unchangedResourceParentFiles=339,nativeReplacements=3,externalEmbeddingSources=3,selectedManifestCount=9,
 configuredSourceRoot=str(source_root),workRoot='/private/tmp/starling-node-compat/scheduler-resource-selection-v1-build',
 engineSha256=d['engine']['sha256'],metadataSha256=d['metadata']['sha256'],
 freezeInvoked=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,
 sourcePromotionAllowed=False,grantsAnyActionAuthority=False)
coverage={k:d[k]for k in ['compileDatabaseRows','policyNativeCppCommands','otherConfiguredCommands','generatedNullCommands','strictCommands','privateCommands','separateEmbeddingCommands','actualObjectFiles','linkedStaticLibraries','orderedStaticLibraryArguments','sdkAliases','opensslSourceFiles','sourceStageCopies','oldResourceStageCopies','oldResourceFrozenCopies','oldResourceOriginalEntries','outerObservedProcesses','innerObservedProcesses','actualBuildOutputFiles','lastNinjaStep','physicalInputFiles','checks']}
coverage.update(actualSelectedManifests=9,currentCopyOriginalModePairs=1067)
limitations=[
 'BUILD-only original artifact provenance; no new freeze, pin, verifier, bootstrap, component, runtime or action authority.',
 'Native all-invalid/optional selection and any timer/interest/reset/reuse semantics remain unobserved.',
 'No inheritance or projection of old resource fec7 or crypto355 artifact/runtime proofs.',
 'Compile database/Ninja rules/object bytes and aggregate native0 are retained; no separate verbose compiler/link argv/exit record is invented.',
 'Rust locked manifest/command/tool/library provenance is checked; captured tool versions are process/source-coupled, not new invocations.',
 'All20,761 ordinary input files are references, not a frozen copy closure;31 SDK symlinks and1 declared SM header hardlink are explicit.',
 'Elapsed/disk data is operational evidence, not timing/RSS/performance.',
 'Historical NULL pre-action outcomes and staged proof buildOrGuestInvoked:false remain literal; this review is a separate actual BUILD proof.'
]
result=dict(fixed,artifacts=artifacts,coverage=coverage,
 actualBuildResult=d['actualBuildResult'],externalParentTerminal=d['externalParentTerminal'],ownedWorkerTerminal=d['ownedWorkerTerminal'],
 rootBuildAuthority=d['rootAuthority'],rootBuildConfig=d['rootConfig'],rootBuildObservation=d['rootObservation'],
 engine=d['engine'],metadata=d['metadata'],buildLog=d['buildLog'],
 controllerSourceReview=root['controllerSourceReview'],actualStageReview=root['actualStageReview'],
 fullActualSourceManifest=m['sourceManifest'],fullActualExternalManifest=m['componentizeSourceManifest'],
 taskSelectionPolicy=m['taskSelectionPolicy'],resourceOwnershipPolicy=m['resourceOwnershipPolicy'],
 selectedModuleManifests=m['selectedModuleManifests'],actualSourceAndSidecarUnchanged=True,
 allObservedOwnedGroupsGone=True,rawOuterExitCode=0,rawInnerExitCode=0,rawNativeBashExitCode=0,
 signals=[],errors=[],forcedCleanup=False,timeouts=False,normalOriginalsProtected=True,
 installedDistributionAudits=d['distributions'],referenceAliases=b['referenceAliases'],declaredArchiveHardlinks=b['declaredArchiveHardlinks'],
 hostToolReferences=b['hostToolReferences'],allLinkedStaticLibraries=b['linkedLibraries'],
 actualFreezeReceipt=None,reviewedEnginePins=None,bootstrapFrame=None,component=None,runtimeProof=None,
 independentPrimitiveDonor=desc(primitive_donor),ownPrimitiveCopy=desc(OWN/'review_io.py'),
 audit=desc(OWN/'data-results.json'),reader=desc(OWN/'reader.py'),supplementalReader=desc(OWN/'read-supplement.py'),
 inputHashes=artifacts['inputHashes'],readerHistory=desc(OWN/'preparation-history.json'),
 reviewerOwnerModulesImported=False,reviewerForeignToolsOrRuntimeActionsInvoked=False,
 limitations=limitations)
write('results.json',result)
write('result-contract.json',dict(schemaVersion=1,state='TASK_SELECTION342_NORMAL_OFF_BUILD_ONLY_RESULT_CONTRACT_V1',
 requiredReviewState=fixed['state'],requiredFixedValues=fixed,requiredExactDescriptors=artifacts,requiredCoverage=coverage,
 requiredControllerSourceReview=root['controllerSourceReview'],requiredActualStageReview=root['actualStageReview'],
 requiredReferenceAliases=b['referenceAliases'],requiredDeclaredArchiveHardlinks=b['declaredArchiveHardlinks'],
 rawMetadataMustRemainByteExact=True,issuesNoActionAuthority=True,limitations=limitations))
write('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_SELECTOR342_NORMAL_OFF_BUILD_DATA_REVIEW_V1',
 result=desc(OWN/'results.json'),contract=desc(OWN/'result-contract.json'),inputHashes=artifacts['inputHashes'],
 actualRootObservation=d['rootObservation'],actualEngine=d['engine'],actualMetadata=d['metadata'],ownerActionsInvoked=False))
files=[]
for p in sorted(OWN.iterdir()):
 if p.is_file()and p.name!='index.json':
  x=desc(p);x['path']=p.name;files.append(x)
write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_SELECTOR342_NORMAL_OFF_BUILD_REVIEW_V1',files=files))
for x in files:
 actual=desc(OWN/x['path']);assert actual['sha256']==x['sha256']and actual['bytes']==x['bytes']
assert {p.name for p in OWN.iterdir()}=={x['path']for x in files}|{'index.json'}
print(json.dumps(dict(index=desc(OWN/'index.json'),result=desc(OWN/'results.json'),contract=desc(OWN/'result-contract.json'),members=len(files),inputHashes=artifacts['inputHashes'],coverage=coverage)))
