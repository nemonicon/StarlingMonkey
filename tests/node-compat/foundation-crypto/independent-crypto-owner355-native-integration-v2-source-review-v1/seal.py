"""Seal this independent source-only review, never execute owner code."""
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent

def row(path):
    raw = path.read_bytes()
    return dict(path=path.relative_to(P).as_posix(), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))

def write(name, value):
    (P / name).write_text(json.dumps(value, indent=2) + '\n')

result = json.loads((P / 'results.json').read_bytes())
assert result['state'] == 'INDEPENDENT_CRYPTO_OWNER355_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V1'
assert result['sourceOnly'] is True and result['sourceReviewPassed'] is True and result['ownerActionsInvoked'] is False
write('review-receipt.json', dict(schemaVersion=1, state='SEALED_INDEPENDENT_CRYPTO_OWNER355_CONTEXT_API_V2_SOURCE_REVIEW_PASSED',
    sourceIndexSha256=result['sourceIndexSha256'], results=row(P / 'results.json'), reader=row(P / 'reader.py'),
    resolvedFinding=result['resolvedFinding'], originalSourceIndexSha256=result['originalSourceIndexSha256'],
    originalHoldIndexSha256=result['originalHoldIndexSha256'], sourceOnly=True, sourceReviewPassed=True,
    ownerActionsInvoked=False, nativeRuntimeOrCryptoProofIssued=False, operationalAdmission=False, sourcePromotionAllowed=False))
write('index.json', dict(schemaVersion=1, state='SEALED_INDEPENDENT_CRYPTO_OWNER355_CONTEXT_API_V2_SOURCE_REVIEW_PASSED',
    files=[row(p) for p in sorted(P.rglob('*')) if p.is_file() and p != P / 'index.json'],
    sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False, nativeRuntimeOrCryptoProofIssued=False,
    operationalAdmission=False, sourcePromotionAllowed=False))
print(json.dumps({name: row(P / name) for name in ['index.json', 'results.json', 'review-receipt.json']}))
