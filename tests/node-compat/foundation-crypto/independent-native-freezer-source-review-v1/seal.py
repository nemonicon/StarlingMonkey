import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=p.relative_to(P).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
r=json.loads((P/'results.json').read_bytes())
assert r['state']=='INDEPENDENT_CRYPTO_OWNER355_FREEZER_SOURCE_REVIEW_PASSED_V1'and r['sourceReviewPassed']is True and r['ownerActionsInvoked']is False
write('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_FREEZER_SOURCE_REVIEW_PASSED',sourceIndexSha256=r['sourceIndexSha256'],diagnosisIndexSha256=r['diagnosisIndexSha256'],results=row(P/'results.json'),reader=row(P/'reader.py'),sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,freezeExecuted=False,actualNativeArtifactAccepted=False,operationalAdmission=False))
write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_FREEZER_SOURCE_REVIEW_PASSED',files=[row(p)for p in sorted(P.rglob('*'))if p.is_file()and p!=P/'index.json'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,freezeExecuted=False,actualNativeArtifactAccepted=False,operationalAdmission=False))
print(json.dumps({n:row(P/n)for n in ('index.json','results.json','review-receipt.json')}))
