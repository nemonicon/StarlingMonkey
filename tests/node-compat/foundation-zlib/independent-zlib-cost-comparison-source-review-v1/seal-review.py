"""Seal only this owned textual source review after a fresh bounded rehash."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'cost-comparison-candidate-v1'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def row(path):
    return {'path': str(path.relative_to(HERE)), 'sha256': digest(path), 'bytes': path.stat().st_size}

def put(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')

assert digest(SOURCE / 'index.json') == 'e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8'
source_index = json.loads((SOURCE / 'index.json').read_text())
manifest = json.loads((SOURCE / 'input-freeze.json').read_text())
assert len(source_index['files']) == 83 and len(manifest['inputs']) == 401
for item in source_index['files'] + manifest['inputs']:
    path = Path(item['path'])
    if not path.is_absolute():
        path = SOURCE / path
    assert digest(path) == item['sha256'] and path.stat().st_size == item['bytes']
assert (HERE / 'stderr.log').read_text() == ''
result = json.loads((HERE / 'results.json').read_text())
assert result['sourceDisposition'] == 'PASS_BOUNDED_PROPOSAL_ONLY' and result['actionDisposition'] == 'HELD_NO_ACTIONS'
receipt = {'schemaVersion': 1, 'state': 'SEALED_INDEPENDENT_ZLIB_COST_COMPARISON_SOURCE_PROPOSAL_PASS_ACTIONS_HELD',
    'reviewedIndexSha256': digest(SOURCE / 'index.json'), 'reviewedSourceFiles': 83, 'reviewedInputRows': 401,
    'inputManifestSha256': digest(SOURCE / 'input-freeze.json'), 'finalFiniteRehashMatched': True,
    'results': row(HERE / 'results.json'), 'reader': row(HERE / 'review.py'),
    'readerExit': {'exitCode': 0, 'observedByThisReader': True, 'stdout': row(HERE / 'stdout.log'), 'stderr': row(HERE / 'stderr.log')},
    'sourceDisposition': 'PASS_BOUNDED_PROPOSAL_ONLY', 'actionDisposition': 'HELD_NO_ACTIONS',
    'ownerActionOrLibraryOrCodecExecuted': False, 'runtimeOrPerformanceProofClaim': False,
    'newPairAuthority': None, 'operationalAdmission': False}
put('review-receipt.json', receipt)
files = []
for path in sorted(HERE.rglob('*')):
    if path.is_file() and path.name != 'index.json':
        path.read_text()
        files.append(row(path))
put('index.json', {'schemaVersion': 1, 'state': receipt['state'], 'files': files,
    'runtimeAcceptanceClaim': False, 'performanceClaim': False})
for item in files:
    assert digest(HERE / item['path']) == item['sha256']
print(json.dumps({'state': receipt['state'], 'indexSha256': digest(HERE / 'index.json'),
    'receiptSha256': digest(HERE / 'review-receipt.json'), 'resultsSha256': digest(HERE / 'results.json'),
    'files': len(files), 'sourceFilesRechecked': 83, 'sourceInputsRechecked': 401}))
