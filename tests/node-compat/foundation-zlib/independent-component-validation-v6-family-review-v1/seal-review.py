"""Seal this generated source HOLD. No project imports or action calls."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
assert not(HERE/'index.json').exists()
r=json.loads((HERE/'results.json').read_bytes())
assert r['generatedIndexSha256']=='8868d212f4204f9319abecbe99bd40e75eb1de1c643fcac48f496c6a0fe88fe4'
assert r['generatedIndexedFiles']==19 and r['consumedRowsRehashed']==10964
assert len(r['concreteSourceBlockers'])==1 and r['concreteSourceBlockers'][0]['id']=='ZV6-M1'
for row in r['verifiedFiles']:
 path=Path(row['path']);assert path.is_file()and not path.is_symlink();digest=hashlib.sha256()
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
 assert digest.hexdigest()==row['sha256']and path.stat().st_size==row['bytes'],path
for row in r['concreteSourceBlockers'][0]['missingPrimaryLoaders']:
 path=Path(row['resolvedGeneratedPath']);assert not path.exists()and not path.is_symlink()
receipt={key:value for key,value in r.items()if key!='verifiedFiles'}
receipt.update({'state':'INDEPENDENT_ZLIB350_GENERATED_V6_SOURCE_HOLD_NO_GUEST','resultsSha256':sha((HERE/'results.json').read_bytes()),'sourceCorrectionRequiredBeforeGuest':True})
with(HERE/'review-receipt.json').open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
files=[]
for path in sorted(HERE.rglob('*')):
 assert not path.is_symlink()
 if not path.is_file():continue
 raw=path.read_bytes();raw.decode('utf8');assert not any(line.rstrip(b' \t')!=line for line in raw.splitlines()),path
 files.append({'path':str(path.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ZLIB350_V6_FAMILY_HOLD','files':files,'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'generatedFamilyReadyForGuest':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False}
with(HERE/'index.json').open('x')as stream:json.dump(index,stream,indent=2);stream.write('\n')
for row in files:
 raw=(HERE/row['path']).read_bytes();assert sha(raw)==row['sha256']and len(raw)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],'resultsSha256':receipt['resultsSha256'],'verifiedPaths':len(r['verifiedFiles']),'blockers':1}))
