"""Seal the independent source review and stored synthetic-only addendum."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def hash_file(path,digest=None,size=None):
 path=Path(path);assert path.is_file()and not path.is_symlink();value=hashlib.sha256()
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
 assert digest is None or value.hexdigest()==digest,path;assert size is None or path.stat().st_size==size,path
 return{'path':str(path.resolve()),'sha256':value.hexdigest(),'bytes':path.stat().st_size}
assert not(HERE/'index.json').exists()
r=json.loads((HERE/'results.json').read_bytes());assert r['state']=='INDEPENDENT_DISABLED_ZLIB350_VALIDATION_SOURCE_REVIEW_PASSED'
assert r['ownerIndexSha256']=='89a38793670ce6066970a6cca288abf841ba194ddd4b6eb04a56edec363f4dd2'
assert r['ownerFiles']==10 and r['preparationInputsRehashed']==11059 and r['concreteSourceBlockers']==[]
for row in r['verifiedFiles']:hash_file(row['path'],row['sha256'],row['bytes'])
external=Path('/tmp/starling-node-compat');names=['zlib-disabled-root-source-v1.stdout.log','zlib-disabled-root-source-v1.stderr.log','zlib-disabled-root-source-v1.terminal.json','zlib-disabled-root-source-v1-output/results.json']
references=[hash_file(external/name)for name in names]
terminal=json.loads((external/names[2]).read_bytes());synthetic=json.loads((external/names[3]).read_bytes())
assert terminal['sourceIndexSha256']==r['ownerIndexSha256']and terminal['rawExitCode']==0 and terminal['syntheticOnly']is True
assert terminal['argv'][1]==str(HERE.parent/'disabled-validation-candidate-v1/test-source.mjs')
assert synthetic['passed']==len(synthetic['checks'])==15 and synthetic['syntheticOnly']is True and synthetic['bootstrapOrComponentizerOrGuestOrHostExecuted']is False
assert (external/names[1]).read_bytes()==b''
addendum={'schemaVersion':1,'state':'ROOT_REPORTED_SYNTHETIC_DISABLED_SOURCE_TEST_EVIDENCE_REHASHED','sourceIndexSha256':r['ownerIndexSha256'],'reportedTerminal':0,'reportedAssertions':15,'syntheticOnly':True,'pastRootTerminalObservedByThisReader':False,'testExecutedByThisReader':False,'guestPassClaim':False,'verifiedExternalReferences':references}
with(HERE/'root-synthetic-evidence.json').open('x')as stream:json.dump(addendum,stream,indent=2);stream.write('\n')
receipt={key:value for key,value in r.items()if key!='verifiedFiles'}
receipt.update({'state':'INDEPENDENT_DISABLED_ZLIB350_SOURCE_PASS_NO_GUEST','resultsSha256':sha((HERE/'results.json').read_bytes()),'rootSyntheticEvidenceSha256':sha((HERE/'root-synthetic-evidence.json').read_bytes()),'sourceReadyForRootDisabledGuestReview':True})
with(HERE/'review-receipt.json').open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
files=[]
for path in sorted(HERE.rglob('*')):
 assert not path.is_symlink()
 if not path.is_file():continue
 raw=path.read_bytes();raw.decode('utf8');assert not any(line.rstrip(b' \t')!=line for line in raw.splitlines()),path
 files.append({'path':str(path.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_DISABLED_ZLIB350_SOURCE_REVIEW_PASS','files':files,'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'sourceReadyForRootDisabledGuestReview':True,'operationalAdmission':False,'guestOrRuntimeResultClaimed':False}
with(HERE/'index.json').open('x')as stream:json.dump(index,stream,indent=2);stream.write('\n')
for row in files:
 raw=(HERE/row['path']).read_bytes();assert sha(raw)==row['sha256']and len(raw)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],'resultsSha256':receipt['resultsSha256'],'verifiedPaths':len(r['verifiedFiles'])}))
