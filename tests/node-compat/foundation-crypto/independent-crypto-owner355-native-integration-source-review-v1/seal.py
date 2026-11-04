import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=p.relative_to(P).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
r=json.loads((P/'results.json').read_text());assert r['sourceReviewPassed'] is False
write('review-receipt.json',dict(schemaVersion=1,state='SEALED_CRYPTO_OWNER355_SOURCE_IDENTITY_PASS_CONTEXT_API_HOLD',sourceIndexSha256=r['sourceIndexSha256'],results=row(P/'results.json'),reader=row(P/'reader.py'),finding='CRYPTO-OWNER355-CONTEXT-API-M1',sourceIdentityAndDataIntegrityPassed=True,stageSourcePeerPassStateIssued=False,ownerActionsInvoked=False,operationalAdmission=False))
write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_NATIVE_INTEGRATION_SOURCE_REVIEW_HOLD',files=[row(p) for p in sorted(P.rglob('*')) if p.is_file() and p!=P/'index.json'],sourceOnly=True,sourceReviewPassed=False,stageSourcePeerPassStateIssued=False,ownerActionsInvoked=False))
print(json.dumps({n:row(P/n) for n in ['index.json','review-receipt.json','results.json']}))
