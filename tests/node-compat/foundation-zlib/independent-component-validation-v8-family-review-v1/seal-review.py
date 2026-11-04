"""Seal the independent generated-v8 source review. No project imports/actions."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
assert not(HERE/'index.json').exists()
r=json.loads((HERE/'results.json').read_bytes())
assert r['state']=='INDEPENDENT_ZLIB350_GENERATED_V8_FAMILY_SOURCE_REVIEW_PASSED'
assert r['generatedIndexSha256']=='8af9a2137b93802ae2f09e30219ad416675a9b10fdac1cdbcc18e48e937a9e56'
assert r['generatedIndexedFiles']==21 and r['consumedRowsIndependentlyReconstructedAndRehashed']==11107 and r['concreteSourceBlockers']==[]
assert r['guestOnlyThreeSupportedUint8ArrayInputChanges']is True and r['unchangedIndexedPayloadFilesFromV7']==17
for row in r['verifiedFiles']:
 path=Path(row['path']);assert path.is_file()and not path.is_symlink();digest=hashlib.sha256()
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
 assert digest.hexdigest()==row['sha256']and path.stat().st_size==row['bytes'],path
receipt={key:value for key,value in r.items()if key!='verifiedFiles'}
receipt.update({'state':'INDEPENDENT_ZLIB350_GENERATED_V8_SOURCE_FAMILY_PASS_NO_GUEST','resultsSha256':sha((HERE/'results.json').read_bytes()),'sourceReadyForRootGuestReview':True,'pastActivationOrHostRegressionObservedByReader':False})
with(HERE/'review-receipt.json').open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
files=[]
for path in sorted(HERE.rglob('*')):
 assert not path.is_symlink()
 if not path.is_file():continue
 raw=path.read_bytes();raw.decode('utf8');assert not any(line.rstrip(b' \t')!=line for line in raw.splitlines()),path
 files.append({'path':str(path.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ZLIB350_GENERATED_V8_SOURCE_FAMILY_PASS','files':files,'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'sourceReadyForRootGuestReview':True,'operationalAdmission':False,'guestOrRuntimeResultClaimed':False}
with(HERE/'index.json').open('x')as stream:json.dump(index,stream,indent=2);stream.write('\n')
for row in files:
 raw=(HERE/row['path']).read_bytes();assert sha(raw)==row['sha256']and len(raw)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],'resultsSha256':receipt['resultsSha256'],'verifiedPaths':len(r['verifiedFiles'])}))
