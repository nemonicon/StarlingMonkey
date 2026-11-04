"""Seal only this owned textual result review after fresh source/output rehashes."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'component-validation-activated-v2'
OUT = Path('/tmp/starling-node-compat/consumers355-v2-disabled-component-validation-v1')

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def row(path):
    return {'path': str(path.relative_to(HERE)), 'sha256': digest(path), 'bytes': path.stat().st_size}

def put(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')

assert digest(SOURCE / 'index.json') == 'bfb689fe993b9f55abc4848e77930c773597e769a7f08a0f2404914d82227835'
source_index = json.loads((SOURCE / 'index.json').read_text())
inputs = json.loads((SOURCE / 'input-freeze.json').read_text())['inputs']
completion = json.loads((OUT / 'completion.json').read_text())
assert len(source_index['files']) == 47 and len(inputs) == 7268 and len(completion['artifacts']) == 59
seen = {}
def check(path, item):
    if str(path) not in seen:
        seen[str(path)] = (digest(path), path.stat().st_size)
    assert seen[str(path)] == (item['sha256'], item['bytes'])
for item in source_index['files']:
    check(SOURCE / item['path'], item)
for item in inputs + completion['artifacts']:
    check(Path(item['path']), item)
assert digest(OUT / 'completion.json') == '21decf63ce266134eb6666b081bc261c914193d2f4d4ce01e10f78f2cb3e25a6'
assert (HERE / 'stderr.log').read_text() == ''
result = json.loads((HERE / 'results.json').read_text())
assert result['state'] == 'INDEPENDENT_CONSUMERS355_DISABLED_COMPONENT_VALIDATION_V1_RESULTS_PASS'
receipt = {'schemaVersion': 1, 'state': 'SEALED_INDEPENDENT_CONSUMERS355_DISABLED_COMPONENT_VALIDATION_V1_RESULTS_PASS',
    'results': row(HERE / 'results.json'), 'reader': row(HERE / 'review.py'),
    'readerExit': {'exitCode': 0, 'observedByThisReader': True, 'stdout': row(HERE / 'stdout.log'), 'stderr': row(HERE / 'stderr.log')},
    'RootOuterExit': {'session': 88048, 'pid': 76515, 'rawExitCode': 0, 'observedByThisReader': False},
    'freshWasmtimeExit': {'status': 0, 'observedByThisReader': False, 'fullRawStdoutDecodedByThisReader': True},
    'finalFiniteRecheck': {'sourceFiles': 47, 'consumedRows': 7268, 'completionArtifactRows': 59, 'completionFile': 1, 'matched': True},
    'actualDenials': 8, 'fullRawSmokeRecordsDecoded': 5, 'staticComponentImports': [], 'staticPublicExports': ['run: func() -> string'],
    'callbackObservationClaim': False, 'positiveConsumerOrGcOrBackendProofTransferred': False,
    'reviewerOwnerOrRuntimeOrNativeActionsExecuted': False, 'operationalAdmission': False,
    'performanceClaim': False, 'newAcceptanceClaim': False}
put('review-receipt.json', receipt)
files = []
for path in sorted(HERE.rglob('*')):
    if path.is_file() and path.name != 'index.json':
        path.read_text()
        files.append(row(path))
put('index.json', {'schemaVersion': 1, 'state': receipt['state'], 'files': files,
    'operationalAdmission': False, 'performanceClaim': False, 'newAcceptanceClaim': False})
for item in files:
    assert digest(HERE / item['path']) == item['sha256']
print(json.dumps({'state': receipt['state'], 'indexSha256': digest(HERE / 'index.json'),
    'receiptSha256': digest(HERE / 'review-receipt.json'), 'resultsSha256': digest(HERE / 'results.json'),
    'files': len(files), 'sourceFilesRechecked': 47, 'consumedRowsRechecked': 7268, 'outputFilesRechecked': 60}))
