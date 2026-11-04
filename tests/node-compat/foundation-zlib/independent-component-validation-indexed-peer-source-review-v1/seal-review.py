"""Seal this independent finite source review; no owner imports or actions."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
assert not(HERE/'index.json').exists()
result=json.loads((HERE/'results.json').read_bytes())
assert result['state']=='INDEPENDENT_ZLIB350_INDEXED_PEER_SOURCE_REVIEW_PASSED'
assert result['ownerIndexSha256']=='bd66c16ce0525a23978e23e170a82cc755bdd313516e00d7e3246302f6730494'
assert result['ownerFiles']==9 and result['preparationInputsRehashed']==8901 and result['independentlyReconstructedInventoryFiles']==8904
assert result['publisherExactReversibleEdits']==4 and result['concreteSourceBlockers']==[]
for row in result['verifiedFiles']:
 path=Path(row['path']);assert path.is_file()and not path.is_symlink();digest=hashlib.sha256()
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
 assert digest.hexdigest()==row['sha256']and path.stat().st_size==row['bytes'],path
for name in['component-validation-activated-v6','component-validation-activated-v6.staging']:assert not(HERE.parent/name).exists()and not(HERE.parent/name).is_symlink()
receipt={key:value for key,value in result.items()if key!='verifiedFiles'}
receipt.update({'state':'INDEPENDENT_ZLIB350_INDEXED_PEER_SOURCE_PASS_NO_ACTIONS','resultsSha256':sha((HERE/'results.json').read_bytes()),'sourceReadyForRootActivationReview':True,'historicalOwnerEvidenceAuthenticatedNotExecuted':True})
with(HERE/'review-receipt.json').open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
files=[]
for path in sorted(HERE.rglob('*')):
 assert not path.is_symlink()
 if not path.is_file():continue
 raw=path.read_bytes();raw.decode('utf8')
 assert not any(line.rstrip(b' \t')!=line for line in raw.splitlines()),path
 files.append({'path':str(path.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ZLIB350_INDEXED_PEER_SOURCE_REVIEW_PASS','files':files,'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'sourceReadyForRootActivationReview':True,'operationalAdmission':False,'runtimeAcceptanceClaim':False}
with(HERE/'index.json').open('x')as stream:json.dump(index,stream,indent=2);stream.write('\n')
for row in files:
 raw=(HERE/row['path']).read_bytes();assert sha(raw)==row['sha256']and len(raw)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],'resultsSha256':receipt['resultsSha256'],'verifiedPaths':len(result['verifiedFiles'])}))
