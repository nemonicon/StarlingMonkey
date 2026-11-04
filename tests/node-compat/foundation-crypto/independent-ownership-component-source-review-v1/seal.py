import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=p.relative_to(P).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
r=json.loads((P/'results.json').read_bytes());assert r['sourceReviewPassed']is False and r['requiredSourcePeerPassStateIssued']is False and r['constructionBlockers']==1
write('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_COMPONENT_SOURCE_ADAPTER_HANDOFF_HOLD',componentSourceIndexSha256=r['componentSourceIndexSha256'],results=row(P/'results.json'),reader=row(P/'reader.py'),sourceFindings=row(P/'source-findings.json'),sourceIdentityAndClosureVerified=True,sourceReviewPassed=False,requiredSourcePeerPassStateIssued=False,ownerActionsInvoked=False,actualConstructionExecuted=False,operationalAdmission=False))
write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_COMPONENT_SOURCE_ADAPTER_HANDOFF_HOLD',files=[row(p)for p in sorted(P.rglob('*'))if p.is_file()and p!=P/'index.json'],sourceOnly=True,sourceReviewPassed=False,requiredSourcePeerPassStateIssued=False,ownerActionsInvoked=False,operationalAdmission=False))
print(json.dumps({n:row(P/n)for n in ('index.json','results.json','review-receipt.json','source-findings.json')}))
