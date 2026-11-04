import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=p.relative_to(P).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
r=json.loads((P/'results.json').read_bytes());assert r['artifactReviewPassed']is True and r['runtimeAcceptanceClaim']is False and r['ownerActionsInvoked']is False
write('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_V2_NORMAL_OFF_NATIVE_ARTIFACT_REVIEW_PASSED',sourceIndexSha256=r['sourceIndexSha256'],results=row(P/'results.json'),reader=row(P/'reader.py'),readerDerivation=row(P/'reader-derivation.json'),originalCheckpoint=row(P/'normal-original-checkpoint.json'),engineSha256=r['engineSha256'],engineBytes=r['engineBytes'],metadataSha256=r['metadataSha256'],freezeReceiptSha256=r['freezeReceiptSha256'],variant='normal-off',nativeArtifactProvenancePassed=True,ownerActionsInvoked=False,reviewedEnginePinsIssued=False,runtimeAcceptanceClaim=False,operationalAdmission=False))
write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_V2_NORMAL_OFF_NATIVE_ARTIFACT_REVIEW_PASSED',files=[row(p)for p in sorted(P.rglob('*'))if p.is_file()and p!=P/'index.json'],variant='normal-off',nativeArtifactProvenancePassed=True,ownerActionsInvoked=False,runtimeAcceptanceClaim=False,operationalAdmission=False))
print(json.dumps({n:row(P/n)for n in ('index.json','results.json','review-receipt.json','normal-original-checkpoint.json')}))
