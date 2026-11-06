"""Pure new read-only phase contracts. No old BUILD-success adaptation."""
STATE='ROOT_REVIEWED_HASH_HMAC357_READ_ONLY_ARTIFACT_REVALIDATION_V2'
PEER='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_ARTIFACT_REVALIDATION_SOURCE_REVIEW_PASSED_V2'
NO_PERMISSIONS=['nativeBuildAllowed','recipeAllowed','compilerAllowed','ninjaAllowed','gitAllowed','engineExecutionAllowed','guestAllowed','cryptoAllowed','componentAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','gcAllowed','oomAllowed','debugAllowed','liveEvpSnapshotAdmission','operationalAdmission','runtimeAcceptanceClaim']
def root(v,own,refs):
 assert v['schemaVersion']==1 and v['state']==STATE and v['adapterIndex']==own and v['entry']==refs['entry']
 assert v['producerControllerIndex']==refs['producerControllerIndex']and v['originalFailureReview']==refs['originalFailureReview']and v['originalFailureContract']==refs['originalFailureContract']
 assert v['configuredSourceRoot']==refs['configuredSourceRoot']and v['workRoot']==refs['workRoot']and v['freezeRoot']==refs['freezeRoot']
 assert v['outputRoot']==refs['outputRoot']and v['externalOutputRoot']==refs['externalOutputRoot']
 assert v['readOnlySourceAdmissionAllowed']is True and v['ownedEvidencePublicationAllowed']is True
 assert v['tmpAliasPolicy']==refs['tmpAliasPolicy']and v['failedReadOnlyRootObservation']==refs['failedReadOnlyRootObservation']
 assert v['indexException']==refs['indexException']and v['expectedEngine']==refs['engine']and v['expectedMetadata']==refs['metadata']
 assert v['monitorEntry']==refs['monitorEntry']and v['monitorIndex']==refs['monitorIndex']and v['deadlineSeconds']==600
 assert v['nativeSourceFiles']==357 and v['externalEmbeddingSources']==3 and v['selectedWholeManifests']==12 and v['rawMetadataFields']==83
 assert all(v[k]is False for k in NO_PERMISSIONS)
 assert v['actualRevalidationResult']is v['actualIndependentArtifactReview']is v['futureFreezeAuthority']is None
def peer(v,own,refs):
 assert v['schemaVersion']==1 and v['state']==PEER and v['sourceIndexSha256']==own['sha256']
 assert v['producerControllerSourceIndexSha256']==refs['producerControllerIndex']['sha256']and v['integrationSourceIndexSha256']==refs['integrationSourceIndex']['sha256']
 assert v['originalFailureReviewIndexSha256']==refs['originalFailureReview']['index']['sha256']
 assert v['sourceOnly']is v['sourceReviewPassed']is True
 for k in ['ownerActionsInvoked','hostActionsInvoked','admissionOrHelperActionsInvoked','engineExecuted','cryptoOperationsInvoked']:assert v[k]is False
 assert v['actualRevalidationProof']is None and v['tmpAliasPolicy']==refs['tmpAliasPolicy']and v['actualCheckedGuardAllInputsPassed']is True
 assert v['recordedCheckedRows']==21328 and v['selectedTmpAliasDescriptors']==2 and v['otherSymlinkAncestorsRejected']is True
def result(v,refs):
 assert v['schemaVersion']==1 and v['state']=='NODE_CRYPTO_HASH_HMAC357_READ_ONLY_ARTIFACT_REVALIDATED_UNREVIEWED_V2'
 assert v['producerControllerIndex']==refs['producerControllerIndex']and v['engine']==refs['engine']and v['metadata']==refs['metadata']
 assert v['originalBuildResult']==refs['originalBuildResult']and v['originalRecipeExitCode']==0 and v['originalParentExitCodes']==[1,1]
 assert v['originalBuildPreservationPassed']is False and v['originalBuildAccepted']is False
 assert v['currentInputBookendsPassed']is True and v['indexException']==refs['indexException']
 assert v['currentIndexSemantics']['pathModeOidStageEqualBaseline']is True
 assert v['producerAdmission']['controllerSourceIndexSha256']==refs['producerControllerIndex']['sha256']
 assert v['producerAdmission']['state']=='NODE_CRYPTO_HASH_HMAC357_SOURCE_ADMISSION_DATA_PASSED_V3'
 assert v['rawMetadataFields']==83 and v['nativeSourceFiles']==357 and v['externalEmbeddingSources']==3 and v['selectedWholeManifests']==12
 for k in ['engineExecuted','guestExecuted','cryptoOperationsInvoked','freezeInvoked','operationalAdmission','runtimeAcceptanceClaim','originalResultRewritten','grantsAnyActionAuthority']:assert v[k]is False
