"""Seal only this source-review packet; no owner modules are imported."""
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent

def row(path):
    raw = path.read_bytes()
    return dict(path=str(path.relative_to(P)), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))

def save(name, value):
    (P / name).write_text(json.dumps(value, indent=2) + '\n')

r = json.loads((P / 'results.json').read_bytes())
assert r['state'] == 'INDEPENDENT_CRYPTO_OWNER355_COMPONENT_SOURCE_REVIEW_PASSED_V3'
assert r['sourceOnly'] is True and r['sourceReviewPassed'] is True and r['ownerActionsInvoked'] is False
save('review-receipt.json', dict(schemaVersion=1, state='SEALED_INDEPENDENT_CRYPTO_OWNER355_COMPONENT_V3_SOURCE_REVIEW',
    componentSourceIndexSha256=r['componentSourceIndexSha256'], results=row(P / 'results.json'),
    reader=row(P / 'reader.py'), sourceCallBoundaries=row(P / 'source-call-boundaries.json'),
    sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False,
    actualComponent=None, actionAuthorityIssued=False, operationalAdmission=False, runtimeAcceptanceClaim=False))
save('index.json', dict(schemaVersion=1, state='SEALED_INDEPENDENT_CRYPTO_OWNER355_COMPONENT_V3_SOURCE_REVIEW',
    files=[row(p) for p in sorted(P.rglob('*')) if p.is_file() and p != P / 'index.json'],
    sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False))
print(json.dumps({name: row(P / name) for name in ['index.json', 'results.json', 'review-receipt.json']}))
