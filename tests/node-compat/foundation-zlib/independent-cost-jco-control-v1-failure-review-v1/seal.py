import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=p.relative_to(P).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
r=json.loads((P/'results.json').read_bytes());assert r['failureAuditPassed']is True and r['ownedWorkersLaunched']==0 and r['reviewerReadHashSourceOnly']is True
write('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_ZLIB_COST_JCO_CONTROL_V1_PRE_WORKER_FAILURE_REVIEW',sourceIndexSha256=r['sourceIndexSha256'],rootFailureReceipt=r['rootFailureReceipt'],results=row(P/'results.json'),reader=row(P/'reader.py'),requiredCorrection=row(P/'required-correction-contract.json'),failureAuditPassed=True,ownerActionsInvoked=False,newControlResultsPublished=False,operationalAdmission=False))
write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_ZLIB_COST_JCO_CONTROL_V1_PRE_WORKER_FAILURE_REVIEW',files=[row(p)for p in sorted(P.rglob('*'))if p.is_file()and p!=P/'index.json'],failureAuditPassed=True,ownerActionsInvoked=False,newControlResultsPublished=False,operationalAdmission=False))
print(json.dumps({n:row(P/n)for n in ('index.json','results.json','review-receipt.json','required-correction-contract.json')}))
