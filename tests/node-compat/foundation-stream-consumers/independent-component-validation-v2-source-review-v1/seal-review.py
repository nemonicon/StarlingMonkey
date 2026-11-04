"""Seal only this independent review after a fresh finite source recheck."""
from pathlib import Path
import hashlib
import json
import stat

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'component-validation-candidate-v2'
EXPECTED = 'a75ee76c1291988cec55252f8ab54e451f31b1593f22119759bada058860002b'

def sha(path):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink()
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return h.hexdigest(), before.st_size

def ref(path):
    digest, size = sha(path)
    return {'path': str(path.relative_to(HERE)), 'sha256': digest, 'bytes': size}

assert not (HERE / 'index.json').exists()
assert sha(SOURCE / 'index.json')[0] == EXPECTED
index = json.loads((SOURCE / 'index.json').read_bytes())
assert len(index['files']) == 80
for row in index['files']:
    assert sha(SOURCE / row['path']) == (row['sha256'], row['bytes'])
inputs = json.loads((SOURCE / 'source-inputs.json').read_bytes())
assert len(inputs['files']) == 5250
for row in inputs['files']:
    assert sha(row['path']) == (row['sha256'], row['bytes'])
assert not SOURCE.with_name('component-validation-activated-v2').exists()
assert not SOURCE.with_name('component-validation-activated-v2').is_symlink()
results = json.loads((HERE / 'results.json').read_bytes())
assert results['disposition'] == 'PASS_SOURCE_ONLY_NO_ACTIVATION'
assert results['remainingConcreteSourceBlockers'] == []
assert (HERE / 'stderr.log').read_bytes() == b''
stdout = json.loads((HERE / 'stdout.log').read_bytes())
assert stdout['remainingConcreteSourceBlockers'] == 0 and stdout['ownerActionsInvoked'] is False
receipt = {
    'schemaVersion': 1,
    'state': 'SEALED_INDEPENDENT_CONSUMERS355_COMPONENT_VALIDATION_V2_SOURCE_REVIEW_PASSED',
    'disposition': results['disposition'],
    'sourceIndex': {'path': str(SOURCE / 'index.json'), 'sha256': EXPECTED, 'files': 80},
    'preparationManifest': {'path': str(SOURCE / 'source-inputs.json'),
                            'sha256': sha(SOURCE / 'source-inputs.json')[0], 'rows': 5250},
    'results': ref(HERE / 'results.json'),
    'reader': ref(HERE / 'review.py'),
    'readerExit': {'exitCode': 0, 'observedByThisReader': True,
                   'stdout': ref(HERE / 'stdout.log'), 'stderr': ref(HERE / 'stderr.log')},
    'freshFiniteSourceRecheck': {'indexedFiles': 80, 'preparationRows': 5250, 'matched': True},
    'closedPriorFindingIds': ['C355-COMP-M1', 'C355-COMP-M2'],
    'remainingConcreteSourceBlockers': [],
    'ownerActionOrPreflightOrBootstrapOrGuestExecuted': False,
    'operationalAdmission': False,
    'runtimeAcceptanceClaim': False,
    'performanceClaim': False,
}
with (HERE / 'review-receipt.json').open('x') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
files = [ref(path) for path in sorted(HERE.rglob('*')) if path.is_file() and path.name != 'index.json']
with (HERE / 'index.json').open('x') as stream:
    json.dump({'schemaVersion': 1,
               'state': 'SEALED_INDEPENDENT_CONSUMERS355_COMPONENT_VALIDATION_V2_SOURCE_REVIEW_PASSED',
               'files': files, 'ownerActionsInvoked': False, 'runtimeAcceptanceClaim': False}, stream, indent=2)
    stream.write('\n')
print(json.dumps({'indexSha256': sha(HERE / 'index.json')[0],
                  'receiptSha256': sha(HERE / 'review-receipt.json')[0],
                  'resultsSha256': sha(HERE / 'results.json')[0], 'files': len(files),
                  'sourceFreshRecheck': '80/5250', 'ownerActionsInvoked': False}))
