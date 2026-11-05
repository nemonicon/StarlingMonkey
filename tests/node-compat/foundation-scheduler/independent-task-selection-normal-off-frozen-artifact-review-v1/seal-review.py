"""Rehash only DATA and seal this independent review; no owner module import."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def descriptor(path, relative=False):
    data = path.read_bytes()
    return dict(path=str(path.relative_to(HERE)) if relative else str(path),
                sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


for name in ('reader.py', 'run-review.py', 'seal-review.py'):
    ast.parse((HERE / name).read_text(), filename=name)
result = json.loads((HERE / 'results.json').read_text())
contract = json.loads((HERE / 'result-contract.json').read_text())
terminal = json.loads((HERE / 'reader-evidence/terminal.json').read_text())
assert result['verifiedPassed'] is True and terminal['rawExitCode'] == 0
assert contract['artifacts'] == contract['requiredExactDescriptors'] == result['artifacts']
assert contract['requiredCoverage'] == result['coverage']
assert result['engineExecuted'] is result['operationalAdmission'] is result['runtimeAcceptanceClaim'] is False
cache = {}
ledger = json.loads((HERE / 'input-hashes.json').read_text())['files']
for row in ledger:
    path = Path(row['path'])
    st = path.lstat()
    identity = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns, st.st_mode)
    assert list(identity) == row['identity'], path
    if identity not in cache:
        digest = hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
                digest.update(chunk)
        cache[identity] = digest.hexdigest()
    assert cache[identity] == row['sha256'] and st.st_size == row['bytes'], path
for row in result['artifacts'].values():
    assert descriptor(Path(row['path'])) == row
for name in ('index.json', 'review-receipt.json'):
    assert not (HERE / name).exists(), 'new review seal only'
checkpoint = json.loads((HERE / 'checkpoint.json').read_text())
checkpoint.update(state='ACTUAL_FROZEN_DATA_REVIEW_COMPLETE_SEALED', verdict=result['state'],
                  noOwnerOrRuntimeActionsInvoked=True)
(HERE / 'checkpoint.json').write_text(json.dumps(checkpoint, indent=2) + '\n')
receipt = dict(schemaVersion=1, state='INDEPENDENT_SELECTOR342_NORMAL_OFF_FROZEN_DATA_REVIEW_RECEIPT_V1',
    result=descriptor(HERE / 'results.json'), contract=descriptor(HERE / 'result-contract.json'),
    ledger=descriptor(HERE / 'input-hashes.json'), rawReaderTerminal=descriptor(HERE / 'reader-evidence/terminal.json'),
    physicalInputPathsRehashed=len(ledger), allInputIdentitiesAndModesUnchanged=True,
    ownerOrRuntimeActionsInvoked=False, grantsAnyActionAuthority=False)
(HERE / 'review-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
files = sorted(p for p in HERE.rglob('*') if p.is_file())
assert not any(p.is_symlink() for p in HERE.rglob('*'))
for p in files:
    if p.suffix in ('.py', '.md', '.json'):
        assert all(line == line.rstrip() for line in p.read_text().splitlines()), p
index = dict(schemaVersion=1, state='SEALED_INDEPENDENT_SELECTOR342_NORMAL_OFF_FROZEN_ARTIFACT_DATA_REVIEW_V1',
             files=[descriptor(p, True) for p in files])
(HERE / 'index.json').write_text(json.dumps(index, indent=2) + '\n')
for row in index['files']:
    assert descriptor(HERE / row['path'], True) == row
print(json.dumps(dict(index=descriptor(HERE / 'index.json'), members=len(files),
    result=descriptor(HERE / 'results.json'), contract=descriptor(HERE / 'result-contract.json'),
    receipt=descriptor(HERE / 'review-receipt.json'), allToolsTerminal=True)))
