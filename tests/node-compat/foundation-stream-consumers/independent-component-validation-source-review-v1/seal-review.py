"""Seal only this owned text review after a fresh finite candidate recheck."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'component-validation-candidate-v1'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def row(path):
    return {'path': str(path.relative_to(HERE)), 'sha256': sha(path), 'bytes': path.stat().st_size}

def put(name, value):
    path = HERE / name
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')

assert sha(SOURCE / 'index.json') == '5659c2885860e1e926e20e8c59a0fac48c2869b401a7e55c190783b2dad9bf79'
index = json.loads((SOURCE / 'index.json').read_text())
inputs = json.loads((SOURCE / 'source-inputs.json').read_text())
cache = {}
for item in index['files'] + inputs['files']:
    path = Path(item['path'])
    if not path.is_absolute():
        path = SOURCE / path
    real = str(path.resolve())
    if real not in cache:
        cache[real] = (sha(path), path.stat().st_size)
    assert cache[real] == (item['sha256'], item['bytes']), str(path)
assert len(index['files']) == 65 and len(inputs['files']) == 5151
assert (HERE / 'stderr.log').read_text() == ''
result = json.loads((HERE / 'results.json').read_text())
assert result['disposition'] == 'HOLD_NO_ACTIVATION' and result['directLiveRootFiveRows'] == 0
assert all(p.suffix not in ['.wasm', '.bin', '.png'] for p in HERE.rglob('*') if p.is_file())
receipt = {
    'schemaVersion': 1,
    'state': 'SEALED_INDEPENDENT_CONSUMERS355_COMPONENT_VALIDATION_SOURCE_HOLD',
    'sourceIndex': {'path': str(SOURCE / 'index.json'), 'sha256': sha(SOURCE / 'index.json'), 'files': 65},
    'preparationManifest': {'path': str(SOURCE / 'source-inputs.json'), 'sha256': sha(SOURCE / 'source-inputs.json'), 'rows': 5151},
    'results': row(HERE / 'results.json'),
    'findings': row(HERE / 'findings.json'),
    'reader': row(HERE / 'review.py'),
    'readerExit': {'exitCode': 0, 'observedByThisReader': True, 'stdout': row(HERE / 'stdout.log'), 'stderr': row(HERE / 'stderr.log')},
    'freshFiniteSourceRecheck': {'indexedFiles': 65, 'preparationRows': 5151, 'matched': True},
    'disposition': 'HOLD_NO_ACTIVATION',
    'mandatoryFunctionalFinding': 'C355-COMP-M1',
    'retentionFinding': 'C355-COMP-M2',
    'directLiveRootFiveRows': 0,
    'nestedHistoricalPreparationRowsReinterpreted': False,
    'ownerActionOrPreflightOrBootstrapOrGuestExecuted': False,
    'runtimeAcceptanceClaim': False,
    'performanceClaim': False
}
put('review-receipt.json', receipt)
files = [row(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name != 'index.json']
put('index.json', {'schemaVersion': 1, 'state': receipt['state'], 'files': files,
                   'runtimeAcceptanceClaim': False, 'performanceClaim': False})
for item in files:
    path = HERE / item['path']
    assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes']
print(json.dumps({'state': receipt['state'], 'indexSha256': sha(HERE / 'index.json'),
    'receiptSha256': sha(HERE / 'review-receipt.json'), 'resultsSha256': sha(HERE / 'results.json'),
    'files': len(files), 'sourceFilesRechecked': 65, 'originalPreparationRowsRechecked': 5151}))
