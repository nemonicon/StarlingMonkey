"""Seal this stage review only after rehashing all recorded external bytes."""
from pathlib import Path
import hashlib, json

HERE = Path(__file__).resolve().parent
def sha(data):
    return hashlib.sha256(data).hexdigest()

assert not (HERE / 'index.json').exists()
result = json.loads((HERE / 'results.json').read_bytes())
assert result['exactCopiedUniquePlanRows'] == 979 and result['rootEvidenceReferences'] == 46
assert result['nativeSources'] == 350 and result['toolRows'] == 632 and result['physicalMembershipExact'] is True
assert result['indexedProposalFiles'] == 85 and result['originalPreparationInputsRehashed'] == 2261
assert result['concreteSourceStageBlockers'] == []
for row in result['verifiedFiles']:
    path = Path(row['path']); assert path.is_file() and not path.is_symlink()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    assert digest.hexdigest() == row['sha256'] and path.stat().st_size == row['bytes'], path
receipt = {
    'schemaVersion': 1,
    'state': 'INDEPENDENT_ACTUAL_ZLIB350_V4_ISOLATED_SOURCE_STAGE_REVIEW_PASSED',
    'rootReceiptSha256': result['rootReceiptSha256'], 'sourceIndexSha256': result['sourceIndexSha256'],
    'sourceReviewIndexSha256': '31d5408eb5567f4e5e925811b33c4e8ec32ad28bb90bc3f844f23c65393145af',
    'resultsSha256': sha((HERE / 'results.json').read_bytes()), 'gitTreeSha256': sha((HERE / 'git-tree.json').read_bytes()),
    'stageReceiptSha256': result['stageReceiptSha256'], 'stageRoot': result['stageRoot'],
    'rootEvidenceReferences': 46, 'nativeSources': 350, 'toolRows': 632, 'nativeToolOverlap': 3,
    'exactCopiedUniquePlanRows': 979, 'indexedProposalFiles': 85, 'originalPreparationInputsRehashed': 2261,
    'preparedReferencesRelocatedOrReinterpreted': False, 'sourceOriginalsAndCopiesExact': True,
    'copiesHaveIndependentInodes': True, 'gitBase': result['gitBase'], 'ordinarySeparateGitClone': True,
    'gitBaseRows': result['gitReadOnlyTreeRows'], 'inheritedEntriesOutsideOverlaysUnchanged': result['inheritedGitEntriesUnchanged'],
    'physicalMembershipExact': True, 'compoundParserDescriptorFixAndForcedIncludeBytesExact': True,
    'native350AndApi40Unchanged': True, 'futurePinsAllFourNull': True,
    'rootReportedRawTerminals': result['rootReportedRawTerminals'],
    'ownerChecksAuthenticatedNotRerun': result['rootRecordedSourceChecksAuthenticatedNotRerun'],
    'oldV3SourceStageFailureEvidenceAndRawEngineRehashedUnchanged': True, 'oldV3FailureRawEngineAdmitted': False,
    'v4BuildRootPhysicalFilesCacheOnly': 4, 'v4CachePreseedTransferredNativeEngineOrMetadataOrProof': False,
    'reviewerActions': result['reviewerActions'],
    'ownerHelperStageMainTestsFactoryBootstrapNativeVerifierBuildCompilerGuestOrHostExecutedByReviewer': False,
    'nativeBuildOrRuntimeProof': False, 'runtimeAcceptanceClaim': False, 'performanceClaim': False,
    'concreteStageBlockers': [], 'limitations': result['limitations'],
    'readerPreparationCorrection': 'Duplicate source-text replacement assertion failed before reader/result creation; preserved history. Completed stage reader exit0.'}
with (HERE / 'review-receipt.json').open('x') as stream:
    json.dump(receipt, stream, indent=2); stream.write('\n')
files = []
for path in sorted(HERE.rglob('*')):
    assert not path.is_symlink()
    if not path.is_file():
        continue
    data = path.read_bytes(); data.decode('utf8')
    files.append({'path': str(path.relative_to(HERE)), 'sha256': sha(data), 'bytes': len(data)})
index = {'schemaVersion': 1, 'state': 'SEALED_INDEPENDENT_ZLIB350_V4_ACTUAL_STAGE_REVIEW',
         'files': files, 'receiptSha256': sha((HERE / 'review-receipt.json').read_bytes()),
         'nativeBuildOrRuntimeClaim': False, 'runtimeAcceptanceClaim': False, 'performanceClaim': False}
with (HERE / 'index.json').open('x') as stream:
    json.dump(index, stream, indent=2); stream.write('\n')
for row in files:
    data = (HERE / row['path']).read_bytes()
    assert sha(data) == row['sha256'] and len(data) == row['bytes']
print(json.dumps({'indexSha256': sha((HERE / 'index.json').read_bytes()), 'files': len(files),
                  'receiptSha256': index['receiptSha256'], 'resultsSha256': receipt['resultsSha256']}))
