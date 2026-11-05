"""Bookend source DATA and seal this independent bounded review."""
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def row(path,relative=False):
    b=path.read_bytes()
    return dict(path=str(path.relative_to(HERE))if relative else str(path),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


for name in ('audit.py','run-audit.py','seal-review.py'):
    ast.parse((HERE/name).read_text(),filename=name)
result=json.loads((HERE/'results.json').read_text())
contract=json.loads((HERE/'result-contract.json').read_text())
terminal=json.loads((HERE/'reader-evidence/terminal.json').read_text())
assert terminal['rawExitCode']==0 and result['sourceReviewPassed']is True
for key in ('ownerActionsInvoked','rustCompilerInvoked','adapterArtifactPublished','adapterPrunerExecuted','guestExecuted'):
    assert result[key]is False
assert contract['requiredState']==result['state']
assert all(result[k]==v for k,v in contract['requiredFixedValues'].items())
ledger=json.loads((HERE/'input-hashes.json').read_text())['files']
cache={}
for item in ledger:
    p=Path(item['path']);s=p.stat();identity=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode)
    assert list(identity)==item['identity'],p
    if identity not in cache:
        digest=hashlib.sha256()
        with p.open('rb')as stream:
            for b in iter(lambda:stream.read(4*1024*1024),b''):digest.update(b)
        cache[identity]=digest.hexdigest()
    assert cache[identity]==item['sha256']and s.st_size==item['bytes'],p
assert not(HERE/'index.json').exists()and not(HERE/'review-receipt.json').exists()
checkpoint=json.loads((HERE/'checkpoint.json').read_text());checkpoint.update(state='SEALED_BOUNDED_SOURCE_REVIEW_COMPLETE',verdict=result['state'])
(HERE/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
receipt=dict(schemaVersion=1,state='INDEPENDENT_CLOCK_IO_PRUNING_SOURCE_REVIEW_RECEIPT_V1',
    result=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),inputHashes=row(HERE/'input-hashes.json'),
    rawReaderTerminal=row(HERE/'reader-evidence/terminal.json'),physicalInputsRehashed=len(ledger),
    normalizedBytesInMemoryOnly=True,adapterArtifactPublished=False,ownerActionsInvoked=False)
(HERE/'review-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=sorted(p for p in HERE.rglob('*')if p.is_file())
assert not any(p.is_symlink()for p in HERE.rglob('*'))
for p in files:
    if p.suffix in('.py','.md','.json'):assert all(line==line.rstrip()for line in p.read_text().splitlines()),p
index=dict(schemaVersion=1,state='SEALED_INDEPENDENT_CLOCK_IO_PRUNING_SOURCE_REVIEW_V1',files=[row(p,True)for p in files])
(HERE/'index.json').write_text(json.dumps(index,indent=2)+'\n')
for item in index['files']:assert row(HERE/item['path'],True)==item
print(json.dumps(dict(index=row(HERE/'index.json'),members=len(files),result=row(HERE/'results.json'),
    contract=row(HERE/'result-contract.json'),receipt=row(HERE/'review-receipt.json'),allToolsTerminal=True)))
