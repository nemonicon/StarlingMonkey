"""Seal the bounded source HOLD without importing or invoking the publisher."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
assert not(HERE/'index.json').exists()
r=json.loads((HERE/'results.json').read_bytes())
assert r['ownerIndexSha256']=='f6f0e1916d02445a0c7e2fc60b0b31b26ef19aef210d59a9964ba77dfcefdee9'
assert r['ownerFiles']==9 and r['preparationInputs']==8877 and r['publisherExactReversibleEdits']==4
assert len(r['concreteSourceBlockers'])==1 and r['concreteSourceBlockers'][0]['id']=='ZVCTX-M2'
for row in r['verifiedFiles']:
 path=Path(row['path']);assert path.is_file()and not path.is_symlink();h=hashlib.sha256()
 with path.open('rb')as source:
  for block in iter(lambda:source.read(1024*1024),b''):h.update(block)
 assert h.hexdigest()==row['sha256']and path.stat().st_size==row['bytes'],path
receipt={k:v for k,v in r.items()if k!='verifiedFiles'}
receipt['state']='INDEPENDENT_ZLIB_VALIDATION_PREPARATION_CONTEXT_SOURCE_HOLD_NO_ACTIVATION'
receipt['resultsSha256']=sha((HERE/'results.json').read_bytes())
receipt['activationApproved']=False
receipt['readerCorrectionHistory']='First reader expected an absent-path/FileNotFoundError traceback; corrected to actual direct regular() AssertionError and finite availability table. Preserved history; no owner changes.'
with(HERE/'review-receipt.json').open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
files=[]
for path in sorted(HERE.rglob('*')):
 assert not path.is_symlink()
 if not path.is_file():continue
 raw=path.read_bytes();raw.decode('utf8');files.append({'path':str(path.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ZLIB_PREPARATION_CONTEXT_SOURCE_HOLD','files':files,'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'activationApproved':False,'operationalAdmission':False}
with(HERE/'index.json').open('x')as stream:json.dump(index,stream,indent=2);stream.write('\n')
for row in files:
 raw=(HERE/row['path']).read_bytes();assert sha(raw)==row['sha256']and len(raw)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],'resultsSha256':receipt['resultsSha256']}))
