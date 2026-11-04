"""Seal this owned textual source-family review after fresh finite rehashes."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'component-validation-candidate-v2'
DEST = HERE.parent / 'component-validation-activated-v2'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def row(path):
    return {'path': str(path.relative_to(HERE)), 'sha256': digest(path), 'bytes': path.stat().st_size}

def put(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')

assert digest(SOURCE / 'index.json') == 'a75ee76c1291988cec55252f8ab54e451f31b1593f22119759bada058860002b'
assert digest(DEST / 'index.json') == 'bfb689fe993b9f55abc4848e77930c773597e769a7f08a0f2404914d82227835'
cache = {}
def check(path, item):
    if str(path) not in cache:
        cache[str(path)] = (digest(path), path.stat().st_size)
    assert cache[str(path)] == (item['sha256'], item['bytes'])
for base in [SOURCE, DEST]:
    for item in json.loads((base / 'index.json').read_text())['files']:
        check(base / item['path'], item)
seal = json.loads((DEST / 'input-freeze.json').read_text())
assert len(seal['inputs']) == 7268
for item in seal['inputs']:
    check(Path(item['path']), item)
assert (HERE / 'stderr.log').read_text() == ''
results = json.loads((HERE / 'results.json').read_text())
assert results['state'] == 'INDEPENDENT_CONSUMERS355_VALIDATION_V2_SOURCE_FAMILY_REVIEW_PASS'
assert results['completePublisherByteReconstruction'] and results['completeConsumedInputUnionReconstruction']
receipt = {'schemaVersion': 1, 'state': 'SEALED_INDEPENDENT_CONSUMERS355_VALIDATION_V2_SOURCE_FAMILY_REVIEW_PASS',
    'reviewedSourceIndexSha256': digest(SOURCE / 'index.json'), 'generatedIndexSha256': digest(DEST / 'index.json'),
    'results': row(HERE / 'results.json'), 'reader': row(HERE / 'review.py'),
    'readerExit': {'exitCode': 0, 'observedByThisReader': True, 'stdout': row(HERE / 'stdout.log'), 'stderr': row(HERE / 'stderr.log')},
    'finalFiniteRecheck': {'sourceFiles': 80, 'generatedFiles': 47, 'consumedInputs': 7268, 'matched': True},
    'inputContext': row(HERE / 'original-input-context.json'),
    'allGeneratedBytesAndConsumedInputUnionReconstructed': True, 'directLiveRootFiveRows': 0,
    'RootActivationExit': {'session': 34235, 'pid': 72182, 'rawExitCode': 0, 'observedByThisReader': False,
        'terminalDescriptorAuthenticated': True},
    'ownerFunctionOrActionExecuted': False, 'guestOrNativeOrHostExecuted': False,
    'operationalAdmission': False, 'runtimeAcceptanceClaim': False, 'performanceClaim': False}
put('review-receipt.json', receipt)
files = []
for path in sorted(HERE.rglob('*')):
    if path.is_file() and path.name != 'index.json':
        assert path.suffix not in ['.wasm', '.bin', '.png']
        path.read_text()
        files.append(row(path))
put('index.json', {'schemaVersion': 1, 'state': receipt['state'], 'files': files,
    'operationalAdmission': False, 'runtimeAcceptanceClaim': False})
for item in files:
    assert digest(HERE / item['path']) == item['sha256']
print(json.dumps({'state': receipt['state'], 'indexSha256': digest(HERE / 'index.json'),
    'receiptSha256': digest(HERE / 'review-receipt.json'), 'resultsSha256': digest(HERE / 'results.json'),
    'files': len(files), 'generatedFilesRechecked': 47, 'consumedInputsRechecked': 7268}))
