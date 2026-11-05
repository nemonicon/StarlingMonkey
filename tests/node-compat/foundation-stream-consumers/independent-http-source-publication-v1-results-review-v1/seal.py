"""Seal actual source-copy proof only; no owner imports or actions."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(P)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
r=json.loads((P/'results.json').read_bytes())
assert r['state']=='INDEPENDENT_CONSUMERS355_HTTP_SOURCE_PUBLICATION_PASSED_V1'and r['verifiedPassed']is True and r['publisherRawExitCode']==0 and r['runtimeActionsInvoked']is False
save('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CONSUMERS355_HTTP_SOURCE_PUBLICATION_REVIEW_V1',
 sourceIndexSha256=r['sourceIndexSha256'],publicationIndexSha256=r['publicationIndexSha256'],results=row(P/'results.json'),reader=row(P/'reader.py'),copyProvenance=row(P/'copy-provenance.json'),
 verifiedPassed=True,publisherRawExitCode=0,runtimeActionsInvoked=False,actionAuthorityIssued=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CONSUMERS355_HTTP_SOURCE_PUBLICATION_REVIEW_V1',files=[row(p)for p in sorted(P.rglob('*'))if p.is_file()and p!=P/'index.json'],
 verifiedPassed=True,runtimeActionsInvoked=False,actionAuthorityIssued=False))
print(json.dumps({n:row(P/n)for n in ['index.json','results.json','review-receipt.json']}))
