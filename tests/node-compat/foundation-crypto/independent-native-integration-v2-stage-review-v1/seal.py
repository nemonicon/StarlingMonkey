"""Seal the independent data-only source-stage review."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def row(path):
 raw=path.read_bytes();return dict(path=path.relative_to(P).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def write(name,value):(P/name).write_text(json.dumps(value,indent=2)+'\n')
r=json.loads((P/'results.json').read_bytes());assert r['actualSourceStageReviewPassed']is True
write('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_V2_ACTUAL_SOURCE_STAGE_REVIEW_PASSED',sourceIndexSha256=r['sourceIndexSha256'],rootStageResult=r['rootStageResult'],results=row(P/'results.json'),reader=row(P/'reader.py'),normalOffBuildEntry=row(P/'normal-off-build-entry.json'),sourceOnly=True,actualSourceStageReviewPassed=True,ownerActionsInvoked=False,nativeBuildOrRuntimeAcceptanceIssued=False,operationalAdmission=False))
write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_V2_ACTUAL_SOURCE_STAGE_REVIEW_PASSED',files=[row(path)for path in sorted(P.rglob('*'))if path.is_file()and path!=P/'index.json'],sourceOnly=True,actualSourceStageReviewPassed=True,ownerActionsInvoked=False,nativeBuildOrRuntimeAcceptanceIssued=False,operationalAdmission=False))
print(json.dumps({n:row(P/n)for n in ('index.json','results.json','review-receipt.json','normal-off-build-entry.json')}))
