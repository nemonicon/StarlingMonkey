"""Seal the completed read/hash/pure review. No operational functions invoked."""
from pathlib import Path
import ast,hashlib,json
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'node-crypto-hash-hmac-freezer-candidate-v1'
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists()
r=read(OWN/'reader-results.json');ix=desc(SOURCE/'index.json');assert ix==r['sourceIndex']and ix['sha256']=='45eef4b6de1e24e450737b66cfc7216e81e39192f8be11be7e80f4312f7c9355'
assert r['checks']==50353 and r['uniqueCurrentFiles']==21501 and r['completeTrees']==11 and r['declaredFamilies']==30 and r['noEntryOrAuthorizeAdmitHelperFreezeVerifyActionMonitorCompilerEngineGuestCalled']is True
assert(OWN/'reader.stderr.log').read_bytes()==b''
for row in read(ix['path'])['files']:assert desc(SOURCE/row['path'])==dict(row,path=str(SOURCE/row['path']))
refs=read(SOURCE/'references.json');future=read(SOURCE/'future-source-review-contract.json')
value=dict(future['requiredFixedValues']);value.update(state=future['requiredReviewState'],freezerSourceIndexSha256=ix['sha256'],freezerSourceIndex=ix,sourceOnly=True,sourceReviewPassed=True,verifiedPassed=True,reader=desc(OWN/'reader-results.json'),artifactReview=refs['artifactReview'],artifactContract=refs['artifactContract'],producerIndex=refs['producerIndex'],engine=refs['engine'],metadata=refs['metadata'],originalRecipeExitCode=0,originalParentExitCodes=[1,1],originalBuildPreservationPassed=False,originalBuildAccepted=False,currentInputFilesVerified=21501,declaredCurrentInputFiles=21475,declaredFamiliesVerified=30,completeReferenceTreesVerified=11,symlinkAliasesVerified=35,archiveHardlinksVerified=1,currentIndexBaselineEntries=742,originalIndexPreimageRetained=False,indexStatOnlyDeltaProved=False,exactIndexWriterProved=False,fullRawMetadataFields83=True,genuineOriginalP3OwnerPreserved=True,newCreatedRootAwareCallbackReviewed=True,wholeReturnPersistedBeforeAssertions=True,frozenOnlyPhysicalPathBoundaryReviewed=True,originalWorkPathsOpenedByFrozenVerifier=False,allReferencesPhysicallyCopiedClaim=False,actualFrozenVerifierExecuted=False,actualProducerAdmissionExecuted=False,actualFreeze=None,actualFrozenReview=None,sourceReviewGrantsActionAuthority=False,publicProfileAdmission=False,liveEvpSnapshotAdmission=False,runtimeAcceptanceClaim=False,qualifications=['Source review only: all operational root/config/actual-freeze gates remain unissued.','Original failed BUILD outcome and index exception remain DATA; the corrected a39 proof is a distinct current read-only artifact review.','All169 WORK witnesses and1642+3+3 planned roles were read/checked as Source DATA; no copy/freezer/verify action was run.','Frozen-only validation checks copied roles, models and historical reference DATA; it does not reopen uncopied original SDK/distribution paths.','Active verifier self-authentication is a consumer obligation outside the frozen payload.','Failure publication is best-effort; a failed writer can leave partial output and no complete failure index is promised.','Disk checks are boundary samples, not continuous space reservation; original0af1800s remains a separate Root-owned operation.','INIT live-EVP snapshots, finalizers/erasure, full crypto/namespace/profile/reuse/security/cost acceptance remain open.'])
save('results.json',value)
fixed=dict(future['requiredFixedValues']);fixed.update(state=future['requiredReviewState'],freezerSourceIndexSha256=ix['sha256'],sourceReviewGrantsActionAuthority=False,originalRecipeExitCode=0,originalParentExitCodes=[1,1],originalBuildPreservationPassed=False,originalBuildAccepted=False,actualFrozenVerifierExecuted=False,actualProducerAdmissionExecuted=False,liveEvpSnapshotAdmission=False,runtimeAcceptanceClaim=False)
save('result-contract.json',dict(schemaVersion=1,requiredReviewState=future['requiredReviewState'],requiredFixedValues=fixed,requiredExactDescriptors=dict(freezerSourceIndex=ix,artifactReview=refs['artifactReview'],artifactContract=refs['artifactContract'],producerIndex=refs['producerIndex'],engine=refs['engine'],metadata=refs['metadata']),sourceReviewGrantsActionAuthority=False))
save('source-receipt.json',dict(schemaVersion=1,result=desc(OWN/'results.json'),contract=desc(OWN/'result-contract.json'),reader=desc(OWN/'reader-results.json'),readerStdout=desc(OWN/'reader.stdout.json'),readerStderr=desc(OWN/'reader.stderr.log'),ownerSourceIndex=ix,operationalActionsInvoked=False))
for p in OWN.glob('*.py'):ast.parse(p.read_bytes())
rows=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():row=desc(p);row['path']=p.relative_to(OWN).as_posix();rows.append(row)
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_FREEZER_SOURCE_REVIEW_NO_ACTION_AUTHORITY_V1',files=rows))
assert {r['path']for r in rows}|{'index.json'}=={p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}
for n in ['index.json','results.json','result-contract.json']:print(json.dumps(desc(OWN/n)))
