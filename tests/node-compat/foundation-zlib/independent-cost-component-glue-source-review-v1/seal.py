import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=p.relative_to(P).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
r=json.loads((P/'results.json').read_text());assert r['state']=='INDEPENDENT_ZLIB_COST_COMPONENT_SOURCE_REVIEW_PASSED_V1'
write('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_EXACT_EMPTY_JCO_HELPER_SOURCE_REVIEW_PASS',sourceIndexSha256=r['componentSourceIndexSha256'],witParentIndexSha256=r['componentWitSourceIndexSha256'],baseIndexSha256=r['componentBaseSourceIndexSha256'],results=row(P/'results.json'),reader=row(P/'reader.py'),sourceOnly=True,ownerActionsInvoked=False,inputRehashCount=r['uniqueInputsRehashed'],componentAccepted=False))
write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_COST_COMPONENT_GLUE_SOURCE_REVIEW_PASS',files=[row(p) for p in sorted(P.rglob('*')) if p.is_file() and p!=P/'index.json'],sourceOnly=True,ownerActionsInvoked=False,componentAccepted=False))
print(json.dumps({n:row(P/n) for n in ['index.json','review-receipt.json','results.json']}))
