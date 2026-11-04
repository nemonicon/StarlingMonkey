import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=p.relative_to(P).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
r=json.loads((P/'results.json').read_text());assert r['state']=='INDEPENDENT_ACTUAL_COST_COMPONENT_V2_GLUE_FAILURE_VERIFIED'
write('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_COMPONENT_V2_GLUE_FAILURE_ATTRIBUTION',results=row(P/'results.json'),reader=row(P/'reader.py'),rootReceiptSha256=r['rootReceipt']['sha256'],sourceIndexSha256=r['sourceIndex']['sha256'],ownerActionsInvoked=False,componentAccepted=False,inputRehashCount=r['uniqueInputsRehashed']))
write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_COMPONENT_V2_FAILURE_REVIEW',files=[row(p) for p in sorted(P.rglob('*')) if p.is_file() and p!=P/'index.json'],componentAccepted=False,ownerActionsInvoked=False))
print(json.dumps({n:row(P/n) for n in ['index.json','review-receipt.json','results.json']}))
