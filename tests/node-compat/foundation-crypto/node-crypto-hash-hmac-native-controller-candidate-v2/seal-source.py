"""Compact own-family seal; no owner actions or external writes."""
from pathlib import Path
import ast,hashlib,json
OWN=Path(__file__).resolve().parent
def desc(p):
 b=Path(p).read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def data(name):return json.loads((OWN/name).read_bytes())
def save(name,v):(OWN/name).write_text(json.dumps(v,indent=2)+'\n')
refs=data('references.json');checks=data('source-check-results.json');need='SOURCE_DATA_PURE_AST_CHECKS_PASSED_V2';assert checks['state']==need
for k in ['ownerHelperInvoked','authorizeInvoked','monitorInvoked','cacheCopyInvoked','nativeOrGuestOrCryptoExecuted']:assert checks[k]is False
for k in ['actualBuildReview','actualBuildContract','actualNewEngine','actualNewMetadata','actualFreezeResult','reviewedPins','bootstrapFrame','runtimeAuthority']:assert refs[k]is None
for phase in ['build','freeze']:
 root=data('future-'+phase+'-root-authority.template.json');cfg=data('future-'+phase+'-config.template.json')
 for k in ['controllerIndex','controllerEntry','controllerSourceReview','nativeBuildAllowed','freezeAllowed','readOnlySourceAdmissionAllowed','postBuildNinjaListingAllowed','actualBuildReview','actualBuildContract','actualFreezeResult','reviewedPins','bootstrapFrame','runtimeAuthority']:assert root[k]is None
 assert cfg['controllerIndex']is cfg['rootAuthority']is None
asts=[]
for p in OWN.rglob('*.py'):ast.parse(p.read_bytes(),filename=str(p));asts.append(p.relative_to(OWN).as_posix())
# Only root index is omitted. Every nested index, if ever present, is a member.
save('results.json',dict(schemaVersion=1,state='NODE_CRYPTO_HASH_HMAC357_NATIVE_CONTROLLER_SOURCE_SEALED_UNREVIEWED_V2',sourceOnly=True,sourceReviewPassed=None,integrationSourceIndex=refs['integrationSourceIndex'],integrationSourceReview=refs['integrationSourceReview'],actualStageReview=refs['actualStageReview'],actualStageContract=refs['actualStageContract'],stageJournal=refs['stageJournal'],configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],freezeRoot=refs['freezeRoot'],nativeSourceFiles=357,retainedParentNativeFiles=353,changedParentNativeFiles=2,newNativeFiles=2,externalEmbeddingSources=3,selectedManifestCount=12,rawMetadataFields=83,compileDatabaseRows=69,policyCpp=63,otherConfiguredRows=5,generatedRows=1,strictCpp=4,privateCpp=7,separateEmbeddingCpp=1,buildDeadlineSeconds=7200,freezeDeadlineSeconds=2400,defaultCopyOnly=True,auditedBorrowEnabled=False,globalHashHmacDefaultOff=True,namedExperimentalBuildHashHmacEnabled=True,sourceDataPureAstChecks=checks['checks'],uniqueCurrentRehashedInputs=checks['uniqueRehashedInputs'],declaredOriginalRows=checks['declaredOriginalRows'],completeExternalFamilies=checks['completeExternalFamilies'],pythonAstFiles=sorted(asts),requiredRootEnvironmentPolicy=data('root-environment-policy.json'),sdkPrecompilerDigestVerificationClaim=False,fullBuildReferencesPhysicallyCopied=False,perCompilerRawExitProofClaim=False,beforeInstallNestedHistoricalDescriptorRehashed=False,liveEvpFactoriesHavePhaseBarrier=False,liveEvpSnapshotAdmission=False,actualBuildReview=None,actualBuildResult=None,actualEngine=None,actualMetadata=None,actualFreezeResult=None,actualFreezeReview=None,sourceIndependentReview=None,rootAuthority=None,reviewedPins=None,bootstrapFrame=None,runtimeAuthority=None,ownerActionsInvoked=False,hostActionsInvoked=False,nativeCacheCopyInvoked=False,actualBenignFilesystemCopiesInvoked=True,benignCopyRegression=desc(OWN/'benign-copy-test-results.json'),failedBuildReview=refs['failedBuildReview'],failedBuildContract=refs['failedBuildContract'],requiredCorrection=refs['requiredCorrection'],producerRole=refs['producerRole'],producerRecipe=refs['recipe'],producerHelper=refs['helper'],producerPolicy=refs['policy'],stageDeclaredWorkRoot=refs['stageDeclaredWorkRoot'],stageDeclaredFreezeRoot=refs['stageDeclaredFreezeRoot'],nativeBuildActionsInvoked=False,freezeActionsInvoked=False,compilerInvoked=False,engineExecuted=False,guestExecuted=False,cryptoOperationsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
save('source-receipt.json',dict(schemaVersion=1,sourceOnly=True,results=desc(OWN/'results.json'),sourceChecks=desc(OWN/'source-check-results.json'),inputBoundary=desc(OWN/'source-inputs.json'),configuredTree=desc(OWN/'configured-tree.json'),apiProvenance=desc(OWN/'api-provenance.json'),preparationFailureHistory=desc(OWN/'source-preparation-failures.json'),exactDerivations=desc(OWN/'derivations.json'),benignCopyRegression=desc(OWN/'benign-copy-test-results.json'),producerGrammar=desc(OWN/'producer-grammar.json'),noActionOrAcceptanceAuthority=True))
index=dict(schemaVersion=1,state='IMMUTABLE_SOURCE_FAMILY_INDEX_V1',files=[])
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file()and p!=OWN/'index.json':r=desc(p);index['files'].append(dict(path=p.relative_to(OWN).as_posix(),sha256=r['sha256'],bytes=r['bytes']))
save('index.json',index)
print(json.dumps(dict(index=desc(OWN/'index.json'),results=desc(OWN/'results.json'),receipt=desc(OWN/'source-receipt.json'),members=len(index['files']),sourceOnly=True,allNativeActionsFalse=True)))
