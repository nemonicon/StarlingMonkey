import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=p.relative_to(P).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
r=json.loads((P/'results.json').read_text());assert r['state']=='INDEPENDENT_NODE_DEVIATION_CONTRACT_DATA_VERIFIED_SOURCE_QUALIFICATION_HOLD'
write('review-receipt.json',dict(schemaVersion=1,state='SEALED_DATA_INTEGRITY_PASS_SOURCE_QUALIFICATION_HOLD',sourceIndexSha256=r['sourceIndex']['sha256'],results=row(P/'results.json'),reader=row(P/'reader.py'),sourceFinding='NODE-DEVIATION-CONTRACT-SOURCE-M1',proposalAccepted=False,ownerActionsInvoked=False,operationalAdmission=False))
write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_NODE_DEVIATION_SOURCE_DATA_REVIEW_QUALIFIED_HOLD',files=[row(p) for p in sorted(P.rglob('*')) if p.is_file() and p!=P/'index.json'],sourceOnly=True,proposalAccepted=False,ownerActionsInvoked=False))
print(json.dumps({n:row(P/n) for n in ['index.json','review-receipt.json','results.json']}))
