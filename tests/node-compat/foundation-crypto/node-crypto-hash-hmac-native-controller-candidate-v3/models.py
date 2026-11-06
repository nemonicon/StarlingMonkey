"""Pure genuine357/83 phase contracts. No frame or metadata projection."""
SOURCE_SHA='7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429'
STAGE_SHA='ed0a32411eb33c5a1ab56ba96d27123fa3e83c31e962ebe81fbcaf066b1b4fbe'
STAGE_STATE='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_RESULTS_REVIEW_PASSED_V2'
BUILD_STATE='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_NATIVE_BUILD_RESULTS_REVIEW_PASSED_V3'
COUNTS=dict(nativeSourceFiles=357,retainedParentNativeFiles=353,changedParentNativeFiles=2,newNativeFiles=2,externalEmbeddingSources=3,selectedManifestCount=12,rawMetadataFields=83,policyCpp=63,compileDatabaseRows=69,strictCpp=4,privateCpp=7,separateEmbeddingCpp=1)

def stage(value,refs):
 assert value['state']==STAGE_STATE and value['schemaVersion']==1 and value['verifiedPassed']is True
 assert value['sourceIndexSha256']==value['integrationSourceIndexSha256']==SOURCE_SHA and value['controllerSourceIndexSha256']==STAGE_SHA
 for name in ['nativeSourceFiles','retainedParentNativeFiles','changedParentNativeFiles','newNativeFiles','externalEmbeddingSources','selectedManifestCount']:assert value[name]==COUNTS[name]
 assert value['configuredSourceRoot']==refs['configuredSourceRoot']
 assert value['workRoot']==refs['stageDeclaredWorkRoot']and value['freezeRoot']==refs['stageDeclaredFreezeRoot']
 assert value['actualJournal']==refs['stageJournal']and value['coverage']['copiedSourceFiles']==1642 and value['coverage']['copiedEmbeddingReferenceFiles']==3
 assert value['baselineRevision']=='54b3329b3ce818fd1f244e871e9c259b63667cda'and value['reachableBaselineCommits']==1 and value['tagAndRemoteRefs']==[]
 for name in ['nativeBuildExecuted','engineExecuted','guestExecuted','cryptoOperationsInvoked','metadataProjected','operationalAdmission','runtimeAcceptanceClaim','grantsBuildOrAnyActionAuthority']:assert value[name]is False
 assert value['actualNewEngine']is value['actualNewMetadata']is None


def root(value,own,refs,policy):
 assert value['schemaVersion']==1 and value['state']=='ROOT_REVIEWED_NODE_CRYPTO_HASH_HMAC357_NATIVE_PHASE_V3'
 phase=value['phase'];assert phase in ['build','freeze']and value['variant']=='normal-off'
 assert value['controllerIndex']==own and value['controllerEntry']['path']==refs['controllerEntryPath']
 assert value['integrationSourceIndex']==refs['integrationSourceIndex']and value['actualStageReview']==refs['actualStageReview']
 assert value['rootEnvironmentPolicy']==policy and value['rootLauncherRequired']is True
 for key in ['configuredSourceRoot','workRoot','freezeRoot']:assert value[key]==refs[key]
 assert value['stageDeclaredWorkRoot']==refs['stageDeclaredWorkRoot']and value['stageDeclaredFreezeRoot']==refs['stageDeclaredFreezeRoot']
 assert value['failedBuildReview']==refs['failedBuildReview']and value['producerRole']==refs['producerRole']
 assert value['buildEnvironment']==refs['buildEnvironment']and value['cachePlan']==refs['cachePlan']and value['recipe']==refs['recipe']and value['helper']==refs['helper']and value['policy']==refs['policy']
 assert value['monitorEntry']==refs['monitorEntry']and value['lifecycleEntry']==refs['lifecycleEntry']and value['parallelBuilds']==1 and value['requiredStartFreeBytes']==2147483648 and value['stopBelowFreeBytes']==838860800
 assert value['nativeBuildAllowed']is(phase=='build')and value['freezeAllowed']is(phase=='freeze')
 assert value['readOnlySourceAdmissionAllowed']is(phase=='freeze')and value['postBuildNinjaListingAllowed']is(phase=='freeze')
 assert value['externalParentDeadlineSeconds']==(7200 if phase=='build'else 2400)
 assert value['externalOutputRoot']==refs['buildExternalRoot'if phase=='build'else'freezeExternalRoot']
 assert value['buildOutputRoot']==refs['buildOutputRoot']and value['rootObserverOutputRoot']==refs['observerBase']+'-'+phase
 for key in ['nativeSourceFiles','externalEmbeddingSources','selectedManifestCount','rawMetadataFields']:assert value[key]==COUNTS[key]
 assert value['hashHmacEnabled']is True and value['auditedBorrowEnabled']is False and value['entropyPolicy']=='off'and value['defaultCopyOnly']is True
 for key in ['debugAllowed','gcAllowed','oomAllowed','borrowAllowed','engineExecutionAllowed','keyOrCryptoAllowed','guestAllowed','componentAllowed','exportAllowed','bootstrapAllowed','globalMutationAllowed','metadataProjectionAllowed','liveEvpSnapshotAdmission','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:assert value[key]is False
 if phase=='build':assert value['actualBuildReview']is value['actualBuildContract']is None
 else:assert value['actualBuildReview']and value['actualBuildContract']
 for key in ['actualFreezeResult','actualFreezeReview','reviewedPins','bootstrapFrame','runtimeAuthority']:assert value[key]is None


def peer(value,own,refs,policy):
 assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_NATIVE_CONTROLLER_SOURCE_REVIEW_PASSED_V3'
 assert value['controllerSourceIndexSha256']==own['sha256']and value['integrationSourceIndexSha256']==SOURCE_SHA
 assert value['actualStageReviewIndexSha256']==refs['actualStageReview']['index']['sha256']and value['requiredRootEnvironmentPolicy']==policy
 assert value['producerRecipeSha256']==refs['recipe']['sha256']and value['producerHelperSha256']==refs['helper']['sha256']and value['producerPolicySha256']==refs['policy']['sha256']
 assert value['failedBuildReviewIndexSha256']==refs['failedBuildReview']['index']['sha256']
 assert value['allOwnedProducerHashGuardsJoined']is True
 assert value['actualBenignCopyModeRegressionPassed']is True
 assert value['sourceOnly']is value['sourceReviewPassed']is True
 for key in ['ownerActionsInvoked','hostActionsInvoked','nativeBuildActionsInvoked','freezeActionsInvoked','cryptoOperationsInvoked']:assert value[key]is False


def build_proof(value,contract,own,refs):
 assert value['schemaVersion']==1 and value['state']==BUILD_STATE and value['verifiedPassed']is True
 assert value['sourceIndexSha256']==SOURCE_SHA and value['controllerSourceIndexSha256']==own['sha256']
 for key in ['nativeSourceFiles','externalEmbeddingSources','selectedManifestCount','rawMetadataFields']:assert value[key]==COUNTS[key]
 assert value['configuredSourceRoot']==refs['configuredSourceRoot']and value['workRoot']==refs['workRoot']and value['variant']=='normal-off'
 assert value['actualBuildResult']['path']==refs['buildOutputRoot']+'/result.json'
 assert value['engine']['path']==refs['enginePath']and value['metadata']['path']==refs['enginePath']+'.build.json'
 assert value['metadataSha256']==value['metadata']['sha256']and value['engineSha256']==value['engine']['sha256']
 assert value['inputHashes']and value['referenceAliases']and value['allOwnedProcessesRawZeroAndGone']is True
 for key in ['engineExecuted','guestExecuted','cryptoOperationsInvoked','operationalAdmission','runtimeAcceptanceClaim','freezeAuthorityGranted']:assert value[key]is False


def cache_plan(plan,refs):
 assert plan['schemaVersion']==1 and plan['state']=='FINITE_HASH_HMAC357_PRIVATE_IMMUTABLE_CACHE_PLAN_V3'and plan['workRoot']==refs['workRoot']
 assert plan['privateRustupHome']==refs['workRoot']+'/rustup-home'and plan['privateCargoHome']==refs['workRoot']+'/cargo-home'
 assert len(plan['copies'])==4 and[r['target']for r in plan['copies']]==['componentize-source.tar.gz','spidermonkey-release.tar.gz','openssl-source.tar.gz','tools/bin/cbindgen']
 assert len({r['source']['path']for r in plan['copies']})==4
 assert[r['outputMode']for r in plan['copies']]==[0o644,0o644,0o644,0o755]and all(r['sourceMode']==r['outputMode']for r in plan['copies'])
 assert plan['sdkTreeOrBuildObjectsReused']is plan['globalRustupCargoMutationAllowed']is False and plan['sdkArchiveReferenceOnly']==refs['sdkArchive']


def failure(value,refs):
 assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_BUILD_V3_FAILURE_REVIEW_PASSED_V1'and value['verifiedPassed']is True
 assert value['controllerSourceIndexSha256']==refs['parentControllerIndex']['sha256']
 assert value['actualBuildSucceeded']is value['phaseSucceeded']is value['buildAcceptanceClaim']is False
 assert value['reviewedOutcome']=='EARLY_RECIPE_FAILED_STALE_POLICY_DIGEST_GUARD'and value['verifiedFailureData']is True
 for k in ['engineExecuted','guestExecuted','cryptoOperationsInvoked','freezeInvoked','operationalAdmission','runtimeAcceptanceClaim','grantsAnyActionAuthority','compilerStarted']:assert value[k]is False
 assert value['coverage']['completedCacheCopies']==4 and value['coverage']['actualWorkFiles']==5 and value['coverage']['recipeRawExitCode']==1 and value['coverage']['staleShellPolicyGuardJoins']==2
 assert value['actualNewEngine']is value['actualNewMetadata']is None
