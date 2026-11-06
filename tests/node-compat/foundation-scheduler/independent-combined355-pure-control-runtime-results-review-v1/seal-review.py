"""Final exact-membership publication of independent DATA audit; no actions."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
assert not (P/'index.json').exists()
def row(f):
 b=f.read_bytes();return dict(path=str(f.resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
a=json.loads((P/'audit-results.json').read_text());result=json.loads((P/'results.json').read_text());contract=json.loads((P/'result-contract.json').read_text());assert result['state']==contract['requiredReviewState']and result['verifiedPassed']is True
for key,v in contract['requiredFixedValues'].items():assert result[key]==v and type(result[key])is type(v)
for key,v in contract['requiredExactDescriptors'].items():assert result[key]==v
assert result['coverage']==contract['requiredCoverage']
base=Path(a['runtimeIndex']['path']).parent;ix=json.loads((base/'index.json').read_text());names={'index.json','completion.json'}|{r['path']for r in ix['files']};assert names=={f.relative_to(base).as_posix()for f in base.rglob('*')if f.is_file()}
for d in ix['files']:
 b=(base/d['path']).read_bytes();assert len(b)==d['bytes']and hashlib.sha256(b).hexdigest()==d['sha256']
(P/'source-receipt.json').write_text(json.dumps(dict(schemaVersion=1,state='INDEPENDENT_ACTUAL_PRELIMINARY_PURE_DATA_REVIEW_SEALED_V1',rootObservation=a['rootObservation'],actualRuntimeIndex=a['runtimeIndex'],results=row(P/'results.json'),contract=row(P/'result-contract.json'),actualPublicationFinalHashesAndMembershipUnchanged=True,actualRuntimeRerun=False,historyTreesCopied=False,reviewerOperationalActionsInvoked=False,allToolsTerminal=True),indent=2)+'\n')
files=[]
for f in sorted(P.rglob('*')):
 assert not f.is_symlink()
 if f.is_file():files.append(dict(row(f),path=f.relative_to(P).as_posix()))
(P/'index.json').write_text(json.dumps(dict(schemaVersion=1,files=files),indent=2)+'\n')
print(json.dumps(dict(index=row(P/'index.json'),result=row(P/'results.json'),contract=row(P/'result-contract.json'),receipt=row(P/'source-receipt.json'),indexed=len(files),actual=len(files)+1,actualTextCopies=66)))
