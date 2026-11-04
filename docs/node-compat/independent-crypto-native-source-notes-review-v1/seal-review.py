"""Seal only this text source-note review after a fresh finite rehash."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'crypto-native-source-notes-v1'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def row(path):return {'path':str(path.relative_to(HERE)),'sha256':sha(path),'bytes':path.stat().st_size}
def put(name,value):
 with(HERE/name).open('x')as stream:stream.write(json.dumps(value,indent=2)+'\n')
assert sha(SOURCE/'index.json')=='570d84e05d89ed70e1fbee6b039fc3608a422257c2cc7cb8742c95a6f844303c'
index=json.loads((SOURCE/'index.json').read_text());source=json.loads((SOURCE/'source-inputs.json').read_text())
assert len(index['files'])==2 and len(source['files'])==11
for item in index['files']+source['files']:
 path=Path(item['path']);path=path if path.is_absolute()else SOURCE/path
 assert sha(path)==item['sha256']and path.stat().st_size==item['bytes']
assert(HERE/'stderr.log').read_text()==''
result=json.loads((HERE/'results.json').read_text());assert result['sourceClaims']['CryptoKeyClassOpsHaveNoRegisteredFinalizer']
receipt={'schemaVersion':1,'state':'SEALED_INDEPENDENT_CRYPTO_NATIVE_SOURCE_NOTES_REVIEW_PASS_OWNERSHIP_BLOCKER_CONFIRMED',
 'notesIndexSha256':sha(SOURCE/'index.json'),'indexedMembersRehashed':2,'sourcePinsRehashed':11,
 'results':row(HERE/'results.json'),'reader':row(HERE/'review.py'),
 'readerExit':{'exitCode':0,'observedByThisReader':True,'stdout':row(HERE/'stdout.log'),'stderr':row(HERE/'stderr.log')},
 'sourceAccuracy':'PASS','futureKeyReuse':'HOLD_UNTIL_REAL_OWNERSHIP_AND_FINALIZER_DESIGN',
 'runtimeLeakOrGcOrCryptoProof':False,'nativeSourceEdited':False,'ownerOrCryptoOrGuestExecuted':False,'operationalAdmission':False}
put('review-receipt.json',receipt)
files=[]
for path in sorted(HERE.rglob('*')):
 if path.is_file()and path.name!='index.json':path.read_text();files.append(row(path))
put('index.json',{'schemaVersion':1,'state':receipt['state'],'files':files,'operationalAdmission':False,'performanceClaim':False})
for item in files:assert sha(HERE/item['path'])==item['sha256']
print(json.dumps({'state':receipt['state'],'indexSha256':sha(HERE/'index.json'),'receiptSha256':sha(HERE/'review-receipt.json'),
 'resultsSha256':sha(HERE/'results.json'),'files':len(files),'sourcePinsRechecked':11}))
