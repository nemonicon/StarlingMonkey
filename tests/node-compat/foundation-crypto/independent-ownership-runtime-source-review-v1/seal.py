"""Seal this source peer only; imports no author module."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(P)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
r=json.loads((P/'results.json').read_bytes())
assert r['state']=='INDEPENDENT_CRYPTO_OWNER355_RUNTIME_SOURCE_REVIEW_PASSED_V1'and r['sourceOnly']is True and r['sourceReviewPassed']is True and r['ownerActionsInvoked']is False
save('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_RUNTIME_SOURCE_REVIEW_V1',sourceIndexSha256=r['sourceIndexSha256'],
 results=row(P/'results.json'),reader=row(P/'reader.py'),scheduleAndBoundaries=row(P/'schedule-and-boundaries.json'),sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,
 actionAuthorityIssued=False,actualRuntime=None,operationalAdmission=False,runtimeAcceptanceClaim=False))
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_RUNTIME_SOURCE_REVIEW_V1',files=[row(p)for p in sorted(P.rglob('*'))if p.is_file()and p!=P/'index.json'],
 sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,actionAuthorityIssued=False))
print(json.dumps({n:row(P/n)for n in ['index.json','results.json','review-receipt.json']}))
