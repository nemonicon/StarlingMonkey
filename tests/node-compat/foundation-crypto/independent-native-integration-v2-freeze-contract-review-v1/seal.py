import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=p.relative_to(P).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
r=json.loads((P/'results.json').read_bytes());assert r['freezeActionReady']is False and r['concreteExecutionBlockers']==1
write('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_V2_FREEZE_CONTRACT_HOLD',sourceIndexSha256=r['sourceIndexSha256'],results=row(P/'results.json'),sourceFindings=row(P/'source-findings.json'),nativeReviewChecklist=row(P/'native-review-checklist.json'),sourceOnly=True,freezeActionReady=False,ownerActionsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_V2_FREEZE_CONTRACT_HOLD',files=[row(p)for p in sorted(P.rglob('*'))if p.is_file()and p!=P/'index.json'],sourceOnly=True,freezeActionReady=False,ownerActionsInvoked=False,operationalAdmission=False))
print(json.dumps({n:row(P/n)for n in ('index.json','results.json','review-receipt.json','native-review-checklist.json')}))
