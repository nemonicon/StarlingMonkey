"""Seal this finite read-only review, preserving the existing raw evidence."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
OUTPUT = Path('/tmp/starling-node-compat/consumers355-v2-normal-component-validation-v1')
FAMILY = HERE.parent / 'component-validation-activated-v2'
ROOT_RECEIPT = HERE.parent / 'normal-component-validation-v1-root-results.json'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def ref(path):
    return {'path': str(path.relative_to(HERE)), 'sha256': sha(path), 'bytes': path.stat().st_size}

assert not (HERE / 'index.json').exists()
result = json.loads((HERE / 'results.json').read_bytes())
assert result['state'] == 'INDEPENDENT_CONSUMERS355_NORMAL_COMPONENT_VALIDATION_ACTUAL_RESULTS_PASSED'
assert result['concreteResultBlockers'] == []
assert (HERE / 'stderr.log').read_bytes() == b''
stdout = json.loads((HERE / 'stdout.log').read_bytes())
assert stdout['reviewerGuestOrOwnerActions'] is False and stdout['rawCalls'] == 196
assert sha(ROOT_RECEIPT) == result['rootReceiptSha256']
root = json.loads(ROOT_RECEIPT.read_bytes())
assert root['rawExitCode'] == 0
for key in ['report', 'completion', 'terminal', 'component']:
    assert sha(root[key]['path']) == root[key]['sha256']
assert sha(FAMILY / 'index.json') == result['sourceFamilyIndexSha256']
evidence = HERE / 'evidence'
evidence.mkdir()
copies = {
    'root-results.json': ROOT_RECEIPT,
    'normal-results.json': Path(root['report']['path']),
    'completion.json': Path(root['completion']['path']),
    'root-terminal.json': Path(root['terminal']['path']),
    'emitted.wit': OUTPUT / 'consumer_validation.emitted.wit',
    'consumer_validation.d.ts': OUTPUT / 'consumer_validation.d.ts',
}
for name, source in copies.items():
    raw = source.read_bytes()
    with (evidence / name).open('xb') as stream:
        stream.write(raw)
    assert sha(evidence / name) == sha(source)
receipt = {
    'schemaVersion': 1,
    'state': 'SEALED_INDEPENDENT_CONSUMERS355_NORMAL_COMPONENT_VALIDATION_RESULTS_PASSED',
    'rootReceiptSha256': result['rootReceiptSha256'],
    'sourceFamilyIndexSha256': result['sourceFamilyIndexSha256'],
    'engineSha256': result['engineSha256'],
    'componentSha256': result['componentSha256'],
    'componentBytes': result['componentBytes'],
    'results': ref(HERE / 'results.json'),
    'reader': ref(HERE / 'verify.py'),
    'readerExit': {'exitCode': 0, 'observedByThisReader': True,
                   'stdout': ref(HERE / 'stdout.log'), 'stderr': ref(HERE / 'stderr.log')},
    'rootRawExitCode': 0,
    'fullRawCallsDecoded': 196,
    'runRecords': 190,
    'namespaceObservations': 6,
    'freshWasmtimeWholeReturnsDecoded': 38,
    'initializerFailures': 11,
    'outputRegularFiles': 1318,
    'outputLinks': 1,
    'verifiedLexicalPaths': result['verifiedLexicalPaths'],
    'concreteResultBlockers': [],
    'ownerOrGuestActionsInvokedByReviewer': False,
    'separateGCAndOFFGatesTransferred': False,
    'operationalAdmission': False,
    'fullNodeCompatibilityOrResetReuseOrPerformanceClaim': False,
    'actualAcceptanceOrSourcePromotionIssued': False,
}
with (HERE / 'review-receipt.json').open('x') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
files = [ref(path) for path in sorted(HERE.rglob('*')) if path.is_file() and path.name != 'index.json']
with (HERE / 'index.json').open('x') as stream:
    json.dump({'schemaVersion': 1,
               'state': 'SEALED_INDEPENDENT_CONSUMERS355_NORMAL_COMPONENT_VALIDATION_RESULTS_PASSED',
               'files': files, 'ownerActionsInvoked': False, 'operationalAdmission': False}, stream, indent=2)
    stream.write('\n')
print(json.dumps({'indexSha256': sha(HERE / 'index.json'), 'files': len(files),
                  'receiptSha256': sha(HERE / 'review-receipt.json'),
                  'resultsSha256': sha(HERE / 'results.json'), 'ownerActionsInvoked': False}))
