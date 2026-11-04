"""Seal only this independent text review; never calls the real publisher."""
from pathlib import Path
import hashlib
import json
import stat

HERE = Path(__file__).parent
CANDIDATE = HERE.parent / 'production-adoption-v1/artifact-preservation-candidate-v1'
EXPECTED = 'fb9baef5e9886c17a4d335738497adeac96e2a003ced4f14dcd35b99a2456b73'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write(name, value):
    with (HERE / name).open('x') as target:
        json.dump(value, target, indent=2)
        target.write('\n')


index_bytes = (CANDIDATE / 'index.json').read_bytes()
assert digest(index_bytes) == EXPECTED
source_index = json.loads(index_bytes)
for row in source_index['files']:
    path = CANDIDATE / row['path']
    assert stat.S_ISREG(path.lstat().st_mode)
    value = path.read_bytes()
    assert len(value) == row['bytes'] and digest(value) == row['sha256']
assert not Path('/tmp/starling-node-compat/classic-artifact-preservation-pending-v1').exists()
scratch_raw = Path('/tmp/starling-node-compat/independent-preservation-source-scratch-v1.json').read_bytes()
scratch = json.loads(scratch_raw)
assert scratch['passed'] == 44 and scratch['actualArchiveOrOwnerActionsExecuted'] is False
with (HERE / 'fresh-scratch-results.json').open('xb') as target:
    target.write(scratch_raw)
data = json.loads((HERE / 'data-checks.json').read_bytes())
assert len(data['checks']) == 11 and all(r['passed'] for r in data['checks'])
assert data['publisherMainInvoked'] is False and data['realArchiveCreated'] is False
write('fresh-check-status.json', {
    'schemaVersion': 1,
    'independentDataReaderExitCode': 0,
    'independentPlanDataGroups': 11,
    'pythonAstChecks': 6,
    'freshScratchExitCode': 0,
    'freshOwnedTinyScratchChecks': 44,
    'scratchReportSha256': digest(scratch_raw),
    'candidate23FilesRehashedAfterChecks': True,
    'candidateSourceUnchanged': True,
    'realPrivateArchiveAbsent': True,
    'publisherMainInvoked': False,
    'ownerRuntimeOrBuildActionsInvoked': False,
})
result = {
    'schemaVersion': 1,
    'state': 'INDEPENDENT_CLASSIC_PRESERVATION_PUBLISHER_SOURCE_REVIEW_PASSED',
    'publisherSourceIndexSha256': EXPECTED,
    'sourceOnly': True,
    'sourceReviewPassed': True,
    'ownerActionsInvoked': False,
    'archiveCopyExecuted': False,
    'sourcePromotionIssued': False,
    'runtimeAcceptanceClaim': False,
    'copyPlanSha256': 'cf75517e937aa0f8c14977981435b387285b59c817c679f6565749db05e1dca8',
    'candidateFilesVerified': 23,
    'candidateBytesVerified': 64351466,
    'protectedStrictDescriptors': 17884,
    'unavailableInspectionDescriptors': 1,
    'separateStatusSnapshots': 7,
    'physicalInputReferences': 18751,
    'plannedCopyObjects': 10781,
    'plannedCopyObjectKinds': {'text': 10516, 'source-binary': 5, 'wasm': 260},
    'plannedLogicalObjectBytesBeforeCapsules': 4210603396,
    'hostSdkReferenceOccurrencesNotCopied': 55,
    'selectedContextCount': 20,
    'selectedMappedTuples': 50894,
    'explicitReferenceRows': 163,
    'formalPolicySha256': '20a32c37de8fc1fe3bcbdecaa751377918d921f79ba6bcef91eb8943895eecc6',
    'laterStrategyDecisionSha256': 'bac8c7c01f27460d8756389b1e024216381d20637bfa445310bf56d25e1ce4f4',
    'actualMemoryIndependentProofIndexSha256': '14611521cb3f44d5ec0cea7ef61eb8821d8fe7f8d8a53aab197209467bca2fe5',
    'actualMemoryOutputDescriptorMembership': 599,
    'actualMemoryProofIndexedMembers': 16,
    'freshChecks': {'planDataGroups': 11, 'pythonSyntax': 6, 'ownedTinyScratch': 44},
    'concreteSourceBlockers': [],
    'physicalInputsFullyRehashedInThisReview': False,
    'actualPublisherBeforeAfterRehashAndIndependentCopyReviewStillRequired': True,
    'fullZlib350OrConsumers355ArchiveClaim': False,
    'historicalProgramsRerunnableClaim': False,
    'archiveAcceptanceIssued': False,
}
write('results.json', result)
write('review-receipt.json', {
    'schemaVersion': 1,
    'state': 'INDEPENDENT_SOURCE_REVIEW_SEALED_NO_COPY_AUTHORITY',
    'publisherSourceIndexSha256': EXPECTED,
    'resultsSha256': digest((HERE / 'results.json').read_bytes()),
    'sourceOnly': True,
    'readerPreparationHistoryRetained': True,
    'sourceOrArchiveOwnerFilesModified': False,
    'RootMustIssueSeparateExactCopyConfig': True,
    'RootMustObserveExternalExitZeroAndIndependentActualCopyReview': True,
    'sourcePromotionIssued': False,
    'archiveAcceptanceIssued': False,
})
rows = []
for path in sorted(HERE.rglob('*')):
    if path.is_dir():
        continue
    assert not path.is_symlink() and stat.S_ISREG(path.lstat().st_mode)
    if path.name == 'index.json':
        continue
    raw = path.read_bytes()
    assert b'\0' not in raw
    raw.decode('utf-8', 'strict')
    rows.append({'path': str(path.relative_to(HERE)), 'sha256': digest(raw), 'bytes': len(raw)})
assert len([r for r in rows if r['path'] == 'results.json']) == 1
write('index.json', {'schemaVersion': 1, 'state': 'SEALED_INDEPENDENT_PRESERVATION_PUBLISHER_SOURCE_REVIEW',
                     'files': rows, 'fileCount': len(rows), 'bytes': sum(r['bytes'] for r in rows),
                     'sourceOnly': True, 'archiveCopyExecuted': False})
final = (HERE / 'index.json').read_bytes()
for row in rows:
    raw = (HERE / row['path']).read_bytes()
    assert digest(raw) == row['sha256'] and len(raw) == row['bytes']
print(json.dumps({'indexSha256': digest(final), 'indexedFiles': len(rows),
                  'resultsSha256': digest((HERE / 'results.json').read_bytes()),
                  'receiptSha256': digest((HERE / 'review-receipt.json').read_bytes()),
                  'sourceOnly': True, 'realCopyExecuted': False}))
