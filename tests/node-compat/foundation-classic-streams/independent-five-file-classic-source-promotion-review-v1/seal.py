"""Seal only the independent post-promotion proof; no owner or runtime actions."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).parent
ADOPTION=HERE.parent/'production-adoption-v1'
REPO=Path('/Users/dan/dev/StarlingMonkey')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(Path(path).read_bytes())
def write(name,value):
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
result=load(HERE/'results.json');assert result['verifiedPassed']is True and len(result['checks'])==7
review=load(ADOPTION/'five-file-corrected-classic-source-promotion-root-review-v1.json')
native=load(review['productionMetadata'][0]['path'])['sourceManifest']
mapping=load(ADOPTION/'artifact-closure-plan-v1/rollforward-map.json')
three={r['path']for r in mapping['files']if r['native']}
assert {str(Path(r['path']).relative_to(REPO))for r in review['unchangedNativeInputs']}=={r['path']for r in native}-three
acceptance=load(review['preservationAcceptance']['path'])
assert acceptance['preservationAcceptedWithinDeclaredScope']is True
assert acceptance['sourcePromotionAllowed']is False and acceptance['releaseCheckpointAccepted']is False
assert review['sourcePromotionAllowed']is True and review['consumers355OrZlib350PromotionAllowed']is False
write('review-receipt.json',{'schemaVersion':1,'state':'INDEPENDENT_EXACT_FIVE_CLASSIC_SOURCE_PROMOTION_REVIEW_COMPLETE',
    'resultsSha256':sha((HERE/'results.json').read_bytes()),
    'rootPromotionReviewSha256':'30bdf0dc728ca7fa516f6964ed4a701be4fc4dc9b8de756cf6b39cd8f14604f9',
    'rootPromotionResultSha256':'879aa3e2b4f0b60df69563839957f40b14cd0497ec33aae53078034fbdbdce7d',
    'exactFiveAfterimagesVerified':True,'unchanged339AreExactlyAllOtherNativeInputs':True,
    'all342CurrentNativeInputsMatchFourProductionMetadata':True,'privateArchive21682RehashedUnchanged':True,
    'oldZlibContextsHeld':12,'oldFiveArchivedTuplesVerified':60,'originalOldSourceHashReaderRerun':False,
    'historicalPolicyOrArchiveBooleansRewritten':False,'sourcePromotionPerformedByReviewer':False,
    'releaseAcceptanceIssued':False,'runtimeAcceptanceClaim':False,'ownerOrRuntimeActionsInvoked':False})
rows=[]
for path in sorted(HERE.rglob('*')):
    if path.is_dir():continue
    assert not path.is_symlink()
    if path.name=='index.json':continue
    raw=path.read_bytes();assert b'\0'not in raw;raw.decode('utf-8','strict')
    rows.append({'path':str(path.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
write('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_EXACT_FIVE_CLASSIC_SOURCE_PROMOTION_REVIEW',
    'files':rows,'fileCount':len(rows),'bytes':sum(r['bytes']for r in rows),
    'runtimeAcceptanceClaim':False,'releaseAcceptanceIssued':False})
for row in rows:
    raw=(HERE/row['path']).read_bytes();assert sha(raw)==row['sha256']and len(raw)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'indexedFiles':len(rows),
    'resultsSha256':sha((HERE/'results.json').read_bytes()),'receiptSha256':sha((HERE/'review-receipt.json').read_bytes())}))
