#!/usr/bin/env python3
"""Supplementary independent stored authority/closure hashes; no owner imports."""
import hashlib,json,stat
from pathlib import Path
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
SOURCE=BASE/'measurement-execution-activated-v2'
COLLECTOR=BASE/'measurement-stock-composition-candidate-v1'
def checked(path,digest,size=None):
 p=Path(path);before=p.lstat();assert stat.S_ISREG(before.st_mode)and not p.is_symlink()
 h=hashlib.sha256()
 with p.open('rb')as src:
  for block in iter(lambda:src.read(1024*1024),b''):h.update(block)
 after=p.lstat();assert(before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
 assert h.hexdigest()==digest and(size is None or before.st_size==size),str(p)
def read(path,digest):checked(path,digest);raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest;return json.loads(raw)
stock=read('/tmp/starling-node-compat/production-common-byte-stock-only-v1/stock-correctness-results.json','a83093eeae1c4ae3e4931d29744ed99ea9f993c7ac3a9cc18359324be7d9b373')
auth=stock['reviewedThreeArmAuthority'];three=read(auth['path'],auth['sha256'])
assert three['schemaVersion']==1 and three['state']=='ROOT_REVIEWED_COMMON_BYTE_THREE_ARMS_FOR_STOCK_ONLY_COMPOSITION_V1'
assert three['sourceFamilyIndexSha256']=='1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612'
assert three['pairPinsSha256']=='f36268516df72ac5b0d5b5ae8fd808d1ce94d40ca364dc533c522fe399b2681e'
assert three['failedParentRawOuterExit']==1 and three['wholeFailedParentPassed']is three['runtimeAcceptanceClaim']is three['timingAllowed']is False
assert three['arms']==['native-on','canonical-on','canonical-off']
failure=read(BASE/'production-adoption-v1/common-byte-v2-stock-graph-failure-root-results.json',three['failedParentRootReceiptSha256'])
assert three['completedArmRecords']==failure['completedArmRecords']
checked(three['independentProofIndexPath'],'bf9fa2a619a92fe6e84b63df8a7650276aa2b13b5d41205835563051b5c3d2ef')
checked(three['independentProofResultPath'],'dbcc5fe7b6fe87595499c423119477567ab8fd794f38d04f3aeb203b88e95d19')
composition=read('/tmp/starling-node-compat/production-common-byte-composition-v1/composition-results.json','b63039855c75bfd6e8d1f38c46eb38d7c4c441a2604a7c283c40d55ee6e167c6')
assert composition['threeArmAuthority']==auth
collector=read(COLLECTOR/'index.json','257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da')
manifest_row=next(row for row in collector['files']if row['path']=='input-freeze.json')
manifest=read(COLLECTOR/'input-freeze.json',manifest_row['sha256']);assert len(manifest['inputs'])==9163
for row in manifest['inputs']:
 p=Path(row['path']);checked(p if p.is_absolute()else COLLECTOR/p,row['sha256'],row['bytes'])
for row in collector['files']:checked(COLLECTOR/row['path'],row['sha256'],row['bytes'])
result={'schemaVersion':1,'state':'EXPLICIT_ACTUAL_THREE_ARM_AUTHORITY_AND_COLLECTOR_CLOSURE_RECHECK_PASSED','authority':auth,'completedArmDescriptorsExact':True,'independentOriginalThreeArmProofIndexAndResultRehashed':True,'compositionUsesSameAuthority':True,'collectorInputRows':9163,'collectorIndexedFiles':20,'oldParentRemainsRawOne':True,'timingAllowed':False,'ownerHelpersOrActionExecuted':False}
with(HERE/'authority-and-closure-checks.json').open('x')as out:json.dump(result,out,indent=2);out.write('\n')
print(json.dumps({'state':result['state'],'collectorInputs':9163}))
