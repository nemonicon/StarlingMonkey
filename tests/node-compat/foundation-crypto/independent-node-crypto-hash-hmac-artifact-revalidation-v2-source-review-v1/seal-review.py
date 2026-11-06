"""Compact Source peer publication only; no operational module import."""
from pathlib import Path
import hashlib, json
OWN = Path(__file__).resolve().parent
SOURCE = OWN.parent / 'node-crypto-hash-hmac-artifact-revalidation-candidate-v2'
assert not (OWN / 'index.json').exists()
def read(path): return json.loads(Path(path).read_bytes())
def desc(path):
    path = Path(path); data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
def save(name, value): (OWN / name).write_text(json.dumps(value, indent=2)+'\n')
checks = read(OWN / 'checks.json'); refs = read(SOURCE / 'references.json')
future = read(SOURCE / 'future-source-review-contract.json')
assert checks['state'] == 'INDEPENDENT_V2_SOURCE_GENUINE_GUARD_PURE_AST_PASSED'
assert checks['sourceIndex'] == desc(SOURCE / 'index.json')
assert checks['sourceIndex']['sha256'] == '559d600d9bedec4e319a415bcd30b984f445cfed7df2322dee25a86cba253172'
assert checks['actualGenuineGuardReadRows'] == checks['currentUniqueRehashedFiles'] == 21437
assert checks['recordedCheckedRows'] == 21328 and checks['selectedTmpAliasDescriptors'] == 2
assert checks['genuineGuardNegativeCases'] == 44 and checks['independentPureCases'] == 26
assert (OWN / 'reader.stderr.log').read_bytes() == b''
assert read(OWN / 'reader.stdout.log')['checks'] == checks['checks']
result = dict(future['requiredFixedValues'])
result.update(state=future['requiredReviewState'], sourceIndexSha256=checks['sourceIndex']['sha256'],
    reviewScope='SOURCE_GENUINE_READ_GUARD_PURE_AST_ONLY_NO_ACTUAL_REVALIDATION',
    sourceIndex=checks['sourceIndex'], sourceResult=desc(SOURCE / 'results.json'),
    sourceReceipt=desc(SOURCE / 'source-receipt.json'), sourceEntry=refs['entry'],
    producerControllerSourceIndex=refs['producerControllerIndex'], integrationSourceIndex=refs['integrationSourceIndex'],
    originalFailureReview=refs['originalFailureReview'], originalFailureContract=refs['originalFailureContract'],
    failedReadOnlyDataReview=refs['failedReadOnlyDataReview'], failedReadOnlyRootObservation=refs['failedReadOnlyRootObservation'],
    priorSourceReviewIndex=refs['priorSourceReviewIndex'], parentAdapterIndex=refs['parentAdapterIndex'],
    actualCandidateEngineData=refs['engine'], actualCandidateMetadataData=refs['metadata'], indexException=refs['indexException'],
    currentUniqueRehashedFiles=21437, completeFamiliesIncludingCandidate=27,
    actualGenuineGuardReadRows=21437, genuineGuardNegativeCases=44, independentPureCases=26,
    activePythonAsts=6, currentProtectedTrees=11, baseAliases=34, systemTmpAliasObservedSeparately=True,
    baseSourceLedger=refs['baseSourceInputs'], baseArtifactLedger=refs['baseArtifactInputs'],
    additionalSourceLedger=checks['additionalSourceLedger'], currentIndexSemanticDecode=checks['actualIndexSemanticDecode'],
    priorPeerMissExplicit=True, priorPeerMiss=checks['priorReviewerMiss'],
    originalRecipeExitCode=0, originalParentExitCodes=[1,1], originalBuildAccepted=False,
    originalBuildPreservationPassed=False, oldReadOnlyAttemptAccepted=False,
    descriptorLogicalPathsRewritten=False, operationalEntryImported=False,
    actualDescriptorReadUtilityEvaluated=True, originalBootstrapInvoked=False,
    originalRecheckInvoked=False, archiveVerifierInvoked=False, compilerInvoked=False,
    guestExecuted=False, currentArtifactAdmitted=False, runtimeAcceptanceClaim=False,
    grantsAnyActionAuthority=False,
    qualifications=[
      'The genuine authenticated descriptor-read definitions were evaluated, not the adapter module/operational functions.',
      'Current inputs/families/trees/aliases were checked before/final; no all-time/global OS guarantee is claimed.',
      'The619de reader accepted a system alias that the175e entry rejected. That reviewer miss and actual19977 failed no-payload observation remain explicit.',
      'Original recipe0/parents1+1/preservationfalse and currentbfbb0600 index exception remain unchanged; no stat-only/writer/preimage proof is claimed.',
      'New Root/raw0/clean/final evidence and independent actual artifact review are still required; result-file existence cannot establish success.',
      'No native or public profile admission, snapshots, crypto outputs, alias identity, erasure, component, runtime or adoption safety is established.',
    ])
save('results.json', result)
fixed = dict(future['requiredFixedValues'], sourceIndexSha256=result['sourceIndexSha256'])
save('result-contract.json', dict(schemaVersion=1, requiredReviewState=result['state'], requiredFixedValues=fixed,
    requiredExactDescriptors=dict(sourceIndex=result['sourceIndex'], sourceResult=result['sourceResult'], sourceReceipt=result['sourceReceipt'],
      sourceEntry=refs['entry'], producerControllerSourceIndex=refs['producerControllerIndex'],
      integrationSourceIndex=refs['integrationSourceIndex'], originalFailureReview=refs['originalFailureReview'],
      failedReadOnlyDataReview=refs['failedReadOnlyDataReview'], failedReadOnlyRootObservation=refs['failedReadOnlyRootObservation'],
      parentAdapterIndex=refs['parentAdapterIndex'], priorSourceReviewIndex=refs['priorSourceReviewIndex']),
    actualRevalidationProof=None, grantsAnyActionAuthority=False))
save('reader-observation.json', dict(schemaVersion=1, argv=['python3','-B',str(OWN/'review-source.py')],
    toolReportedRawExitCode=0, stdout=desc(OWN/'reader.stdout.log'), stderr=desc(OWN/'reader.stderr.log'),
    hostReadHashPureAstOnly=True, operationalModuleOrFunctionInvoked=False, ownedGroupObservationClaim=False))
save('preparation-history.json', dict(schemaVersion=1, state='SEALED_INDEPENDENT_SOURCE_REVIEW_ONLY',
    priorPeerMissExplicit=True, operationalEntryOrApiInvoked=False))
save('review-receipt.json', dict(schemaVersion=1, sourceOnly=True, result=desc(OWN/'results.json'),
    contract=desc(OWN/'result-contract.json'), checks=desc(OWN/'checks.json'), readerObservation=desc(OWN/'reader-observation.json'),
    sourceIndex=result['sourceIndex'], reviewedInputRows=21437, genuineGuardReadRows=21437,
    historicalProofTreesCopied=False, actualRevalidationProof=None, ownerActionsInvoked=False))
rows=[]
for path in sorted(OWN.rglob('*')):
    assert not path.is_symlink()
    if path.is_file():
        row=desc(path); row['path']=path.relative_to(OWN).as_posix(); rows.append(row)
save('index.json', dict(schemaVersion=1, state='SEALED_INDEPENDENT_SOURCE_REVIEW_ONLY_V2', files=rows))
assert {r['path'] for r in rows}|{'index.json'} == {p.relative_to(OWN).as_posix() for p in OWN.rglob('*') if p.is_file()}
for name in ['index.json','results.json','result-contract.json','review-receipt.json']:
    print(json.dumps(desc(OWN/name)))
