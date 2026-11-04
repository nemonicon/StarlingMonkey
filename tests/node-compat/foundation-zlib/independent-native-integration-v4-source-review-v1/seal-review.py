"""Seal only this independent textual review after a final external rehash."""
from pathlib import Path
import hashlib, json

HERE = Path(__file__).resolve().parent

def sha(data):
    return hashlib.sha256(data).hexdigest()

assert not (HERE / 'index.json').exists()
value = json.loads((HERE / 'results.json').read_bytes())
assert value['ownerIndexSha256'] == 'd384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
assert value['ownerFiles'] == 85 and value['preparationInputs'] == 2261
assert value['toolRows'] == 632 and value['futureStageUniquePlanRows'] == 979
assert value['concreteSourceBlockers'] == []
assert value['ownerImportsTestsActionsStageBuildCompilerNativeVerifierPreflightGuestHostOrTimingExecutedByReviewer'] is False
for row in value['verifiedFiles']:
    path = Path(row['path']); assert path.is_file() and not path.is_symlink()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    assert digest.hexdigest() == row['sha256'] and path.stat().st_size == row['bytes'], path
receipt = {
    'schemaVersion': 1,
    'state': 'INDEPENDENT_ZLIB350_V4_SCOPED_SOURCE_REVIEW_PASSED',
    'ownerIndexSha256': value['ownerIndexSha256'],
    'ownerSourceReceiptSha256': value['sourceReceiptSha256'],
    'ownerPatchSha256': value['patchSha256'],
    'resultsSha256': sha((HERE / 'results.json').read_bytes()),
    'mandatoryCompoundAmendmentIndexSha256': value['mandatoryCompoundAmendmentIndexSha256'],
    'parentV3IndexSha256': value['parentV3IndexSha256'],
    'priorFailureRootReceiptSha256': value['failureRootReceiptSha256'],
    'priorFailureIndependentIndexSha256': 'c319335168016fcc40ec2b04548e82a3fd171972dcc3a488f30bbb0ffcecb4ce',
    'priorM1HoldIndexSha256': 'dafaff07578be6f62883ddf0815c023f4ba0e12b0c5b1e6ab5899d4f0edb474c',
    'priorM2HoldIndexSha256': '89bc84d69c17b3959105ef1776c3275981b3bdace2aca7de64a355a1e6aabe1b',
    'ownerFiles': 85, 'preparationInputs': 2261, 'mandatoryAmendmentFiles': 8,
    'native350AndApi40Unchanged': True, 'toolRows': 632, 'nativeToolOverlap': 3, 'futureStageUniquePlanRows': 979,
    'exactForwardReverseDerivationRecords': value['exactForwardReverseDerivationRecords'],
    'onlyCodecFunctionChanged': value['onlyCodecFunctionChanged'],
    'actualFullCapture': value['actualFullCapture'],
    'storedParserRegressionChecksAuthenticatedNotRerun': 26,
    'actualHistoricalCompileSyntaxCommandDataRecords': 64,
    'recipeSha256': value['recipeSha256'], 'policySha256': value['policySha256'], 'helperSha256': value['helperSha256'],
    'futurePinsAllFourNull': True, 'operationalAdmissionOpen': False, 'runtimeBackendProof': value['runtimeBackendProof'],
    'oldFailureRawEngineNotAdmitted': True, 'rootOuterBuildStatusObservedByThisReader': False,
    'ownerImportsTestsActionsStageBuildCompilerNativeVerifierPreflightGuestHostOrTimingExecutedByReviewer': False,
    'newStageBuildFreezeLinkRuntimeGuestOrHostEvidenceClaim': False,
    'oldSealedPacketsOrCurrentCheckoutsModified': False,
    'concreteSourceBlockers': [], 'runtimeAcceptanceClaim': False, 'performanceClaim': False,
    'readerCorrectionHistory': 'One textual-diff universal-newline assumption; exact source bytes already matched. No owner changes.',
    'scope': value['scope'], 'limitations': value['limitations']}
with (HERE / 'review-receipt.json').open('x') as stream:
    json.dump(receipt, stream, indent=2); stream.write('\n')
files = []
for path in sorted(HERE.rglob('*')):
    assert not path.is_symlink()
    if not path.is_file():
        continue
    data = path.read_bytes(); data.decode('utf8')
    files.append({'path': str(path.relative_to(HERE)), 'sha256': sha(data), 'bytes': len(data)})
index = {'schemaVersion': 1, 'state': 'SEALED_INDEPENDENT_ZLIB350_V4_SCOPED_SOURCE_REVIEW',
         'files': files, 'receiptSha256': sha((HERE / 'review-receipt.json').read_bytes()),
         'runtimeAcceptanceClaim': False, 'performanceClaim': False}
with (HERE / 'index.json').open('x') as stream:
    json.dump(index, stream, indent=2); stream.write('\n')
for row in files:
    data = (HERE / row['path']).read_bytes()
    assert sha(data) == row['sha256'] and len(data) == row['bytes']
print(json.dumps({'indexSha256': sha((HERE / 'index.json').read_bytes()), 'files': len(files),
                  'receiptSha256': index['receiptSha256'], 'resultsSha256': receipt['resultsSha256']}))
