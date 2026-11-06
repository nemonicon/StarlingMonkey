"""Publish the completed independent Source review, not an artifact result."""
from pathlib import Path
import hashlib, json

OWN = Path(__file__).resolve().parent
SOURCE = OWN.parent / 'node-crypto-hash-hmac-artifact-revalidation-candidate-v1'
assert not (OWN / 'index.json').exists()

def read(path):
    return json.loads(Path(path).read_bytes())

def descriptor(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))

def save(name, value):
    (OWN / name).write_text(json.dumps(value, indent=2) + '\n')

checks = read(OWN / 'checks.json')
refs = read(SOURCE / 'references.json')
future = read(SOURCE / 'future-source-review-contract.json')
assert checks['state'] == 'INDEPENDENT_SOURCE_DATA_PURE_AST_REVIEW_PASSED'
assert checks['sourceIndex'] == descriptor(SOURCE / 'index.json')
assert checks['sourceIndex']['sha256'] == '175e4061a92d982ad8cefbd77d2be3e8d4b88f9906df3d186923ba64397a918e'
assert (OWN / 'reader.stderr.log').read_bytes() == b''
assert read(OWN / 'reader.stdout.log')['checks'] == checks['checks']

result = dict(future['requiredFixedValues'])
result.update(
    state=future['requiredReviewState'], sourceIndexSha256=checks['sourceIndex']['sha256'],
    reviewScope='SOURCE_READ_HASH_PURE_AST_ONLY_NOT_ACTUAL_REVALIDATION',
    sourceIndex=checks['sourceIndex'], sourceResult=descriptor(SOURCE / 'results.json'),
    sourceReceipt=descriptor(SOURCE / 'source-receipt.json'),
    sourceEntry=refs['entry'], originalFailureReview=refs['originalFailureReview'],
    originalFailureContract=refs['originalFailureContract'],
    producerControllerSourceIndex=refs['producerControllerIndex'],
    integrationSourceIndex=refs['integrationSourceIndex'],
    actualCandidateEngineData=refs['engine'], actualCandidateMetadataData=refs['metadata'],
    indexException=refs['indexException'],
    sourceDataChecks=checks['checks'], declaredBaseRows=5541,
    artifactAdditionalRows=15787, currentUniqueRehashedFiles=checks['currentUniqueRehashedFiles'],
    declaredSourceFamilies=23, completeFamiliesIncludingCandidate=24,
    currentProtectedTrees=11, currentAliases=34, activePythonAsts=6,
    independentPureCases=checks['independentPureCases'],
    retainedAuthorPureCasesAuthenticated=41, retainedAuthorChecksAuthenticated=134641,
    sourceInputLedger=checks['sourceInputLedger'], artifactInputLedger=checks['artifactInputLedger'],
    currentIndexSemanticDecode=checks['actualIndexSemanticDecode'],
    genuineP3ApiAndModuleContextsVerifiedInSource=True,
    separateArgumentContextAndAdapterProvenanceVerifiedInSource=True,
    originalRecipeExitCode=0, originalParentExitCodes=[1, 1],
    originalBuildAccepted=False, originalBuildPreservationPassed=False,
    currentArtifactAdmitted=False, compilerInvoked=False, archiveVerifierInvoked=False,
    originalBootstrapInvoked=False, originalRecheckInvoked=False,
    nativeBuildOrFreezeInvoked=False, guestExecuted=False,
    runtimeAcceptanceClaim=False, grantsAnyActionAuthority=False,
    qualifications=[
        'Source PASS only. The proposed P3 admission/helper/archive comparisons have not been executed by this review.',
        'The full current declared ledgers/families/trees/aliases were rehashed before/final; no historical global OS or all-time attestation is claimed.',
        'Original recipe0/parents1+1/preservationfalse are retained, not relabeled as a successful original BUILD.',
        'Exact current index hash+mode and742 baseline semantics are explicit; old index preimage, stat-only causality and writer remain unproved.',
        'A final-only protection failure may leave an UNREVIEWED result file. Future actual acceptance requires a genuine Root/raw0/clean/final-proof review.',
        'The future artifact contract is distinct; the old successful-BUILD wire is not satisfied or projected.',
        'Historical57-byte Rustup descriptor remains historical DATA; live107-byte settings and raw83 metadata remain separate actual inputs.',
        'Current compiler/link witnesses are DATA. INIT/live EVP, aliases, algorithms, erasure/finalizers, component/runtime and security completeness remain open.',
    ])
assert result['schemaVersion'] == 1 and result['sourceOnly'] and result['sourceReviewPassed']
save('results.json', result)

fixed = dict(future['requiredFixedValues'], sourceIndexSha256=result['sourceIndexSha256'])
save('result-contract.json', dict(
    schemaVersion=1, requiredReviewState=result['state'], requiredFixedValues=fixed,
    requiredExactDescriptors=dict(sourceIndex=result['sourceIndex'], sourceResult=result['sourceResult'],
        sourceReceipt=result['sourceReceipt'], sourceEntry=result['sourceEntry'],
        producerControllerSourceIndex=refs['producerControllerIndex'],
        integrationSourceIndex=refs['integrationSourceIndex'], originalFailureReview=refs['originalFailureReview'],
        originalFailureContract=refs['originalFailureContract'],
        actualCandidateEngineData=refs['engine'], actualCandidateMetadataData=refs['metadata']),
    requiredScope='SOURCE_ONLY_NOT_ACTUAL_REVALIDATION_OR_ACTION_AUTHORITY',
    actualRevalidationProof=None, grantsAnyActionAuthority=False))
save('reader-observation.json', dict(schemaVersion=1,
    argv=['python3', '-B', str(OWN / 'review-source.py')],
    toolReportedRawExitCode=0, stdout=descriptor(OWN / 'reader.stdout.log'),
    stderr=descriptor(OWN / 'reader.stderr.log'),
    hostPureDataAndAstOnly=True, ownedGroupObservationClaim=False,
    adapterOrAdmissionOrHelperInvoked=False))
save('review-receipt.json', dict(schemaVersion=1, sourceOnly=True,
    result=descriptor(OWN / 'results.json'), contract=descriptor(OWN / 'result-contract.json'),
    checks=descriptor(OWN / 'checks.json'), readerObservation=descriptor(OWN / 'reader-observation.json'),
    sourceIndex=result['sourceIndex'], sourceInputLedger=checks['sourceInputLedger'],
    artifactInputLedger=checks['artifactInputLedger'],
    currentUniqueRehashedFiles=checks['currentUniqueRehashedFiles'],
    historicalProofTreesCopied=False, actualRevalidationProof=None,
    ownerActionsInvoked=False, admissionOrHelperActionsInvoked=False))
rows = []
for path in sorted(OWN.rglob('*')):
    assert not path.is_symlink()
    if path.is_file():
        row = descriptor(path)
        row['path'] = path.relative_to(OWN).as_posix()
        rows.append(row)
save('index.json', dict(schemaVersion=1, state='SEALED_INDEPENDENT_SOURCE_REVIEW_ONLY_V1', files=rows))
assert {row['path'] for row in rows} | {'index.json'} == {
    path.relative_to(OWN).as_posix() for path in OWN.rglob('*') if path.is_file()}
for name in ['index.json', 'results.json', 'result-contract.json', 'review-receipt.json']:
    print(json.dumps(descriptor(OWN / name)))
