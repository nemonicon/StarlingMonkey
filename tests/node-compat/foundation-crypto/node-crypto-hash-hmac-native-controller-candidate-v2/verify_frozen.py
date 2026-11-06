"""Read/hash-only357 frozen capsule verifier. No originals, helper or engine access.
Active verifier self-authentication is outside FREEZE when invoked by controller;
all payload/model reads below are confined to the frozen tree.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,re,shlex,stat,sys
FREEZE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v2-freeze')
SOURCE_SHA='7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429'

def checked(r):
 assert type(r)is dict and set(r)=={'path','sha256','bytes'}and type(r['bytes'])is int and r['bytes']>=0 and re.fullmatch('[a-f0-9]{64}',r['sha256'])
 p=Path(r['path']);assert p.is_absolute()and not r['path'].startswith('//')and str(p)==r['path']and p.is_relative_to(FREEZE)and '..'not in p.parts and '\\'not in str(p)
 for q in(p,*p.parents):assert not q.is_symlink()
 before=p.stat();assert stat.S_ISREG(before.st_mode);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 after=p.stat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
 assert before.st_size==r['bytes']and h.hexdigest()==r['sha256'];return p

def read(r):assert r['bytes']<=32*1024*1024;return json.loads(checked(r).read_bytes())

def verify_frozen(receipt_row,expected_controller):
 assert __debug__ and sys.dont_write_bytecode and re.fullmatch('[a-f0-9]{64}',expected_controller)
 assert receipt_row['path']==str(FREEZE/'normal-off-freeze-receipt.json');r=read(receipt_row)
 assert r['schemaVersion']==1 and r['state']=='NODE_CRYPTO_HASH_HMAC357_NORMAL_OFF_FREEZE_COMPLETE_UNREVIEWED_V2'and r['variant']=='normal-off'
 assert r['sourceIndexSha256']==r['nativeSourceIndexed']['sha256']==SOURCE_SHA and r['controllerSourceIndexSha256']==r['controllerSourceIndexed']['sha256']==expected_controller
 for k,n in dict(nativeSourceFiles=357,externalEmbeddingSources=3,selectedManifestCount=12,rawMetadataFields=83,compileDatabaseRows=69,policyCpp=63,strictCpp=4,privateCpp=7,separateEmbeddingCpp=1).items():assert r[k]==n
 for k in ['verifiedReferencesNotAllCopied','rawMetadataUnchanged','rawMetadataOriginalPathsPreserved']:assert r[k]is True
 for k in ['historicalPreinstallNestedSettingsRehashed','perCompilerRawExitProofClaim','engineExecuted','guestExecuted','cryptoOperationsInvoked','liveEvpSnapshotAdmission','pinsAdopted','operationalAdmission','runtimeAcceptanceClaim']:assert r[k]is False
 root_stat=FREEZE.stat();copies={};ids=set()
 for item in r['copies']:
  d={k:item[k]for k in ['path','sha256','bytes']};p=checked(d);name=p.relative_to(FREEZE).as_posix();assert name not in copies and name!='normal-off-freeze-receipt.json';s=p.stat();assert stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and(s.st_dev,s.st_ino)not in ids;ids.add((s.st_dev,s.st_ino));copies[name]=item
 actual=set()
 for p in FREEZE.rglob('*'):
  s=p.lstat();assert not p.is_symlink()
  if stat.S_ISDIR(s.st_mode):assert stat.S_IMODE(s.st_mode)==0o700
  else:assert stat.S_ISREG(s.st_mode);actual.add(p.relative_to(FREEZE).as_posix())
 assert actual==set(copies)|{'normal-off-freeze-receipt.json'}and stat.S_IMODE(root_stat.st_mode)==0o700
 rs=checked(receipt_row).stat();assert rs.st_nlink==1 and stat.S_IMODE(rs.st_mode)==0o600 and(rs.st_dev,rs.st_ino)not in ids
 def row(name):return{k:copies[name][k]for k in ['path','sha256','bytes']}
 ix=row('artifact-tools/source/index.json');assert ix['sha256']==expected_controller;index=read(ix);names=set()
 for item in index['files']:
  name=item['path'];assert name and not name.startswith('/')and all(x not in('','.','..')for x in name.split('/'))and name not in names;names.add(name);saved=row('artifact-tools/source/'+name);assert saved['sha256']==item['sha256']and saved['bytes']==item['bytes']
 assert {n.removeprefix('artifact-tools/source/')for n in copies if n.startswith('artifact-tools/source/')}==names|{'index.json'}
 selfrow=next(v for v in index['files']if v['path']=='verify_frozen.py');active=Path(__file__).resolve();assert active.stat().st_size==selfrow['bytes']and hashlib.sha256(active.read_bytes()).hexdigest()==selfrow['sha256']
 def pure(name):
  p=checked(row('artifact-tools/source/'+name));s=importlib.util.spec_from_file_location('frozen357_'+name.replace('.','_'),p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 refs=read(row('artifact-tools/source/references.json'));policy=read(row('build-evidence/active-policy.json'));meta=read(r['metadata']);checked(r['engine'])
 result=read(row('build-proof/result.json'));contract=read(row('build-proof/contract.json'));assert row('build-proof/result.json')['sha256']==r['actualBuildReview']['result']['sha256']and row('build-proof/contract.json')['sha256']==r['actualBuildContract']['sha256']
 assert result['state']==contract['requiredReviewState']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_NATIVE_BUILD_RESULTS_REVIEW_PASSED_V2'and result['verifiedPassed']is True
 for group in ['requiredFixedValues','requiredExactDescriptors','requiredVerifiedProperties']:
  for k,v in contract.get(group,{}).items():assert result[k]==v
 if 'requiredCoverage'in contract:assert result['coverage']==contract['requiredCoverage']
 pure('models.py').build_proof(result,contract,r['controllerSourceIndexed'],refs)
 assert r['engine']['sha256']==result['engine']['sha256']and r['metadata']['sha256']==result['metadata']['sha256']
 assert meta['enginePath']==result['engine']['path']and len(meta)==83
 observed=pure('metadata_model.py').validate_metadata(meta,policy,refs['policy']['sha256'],refs['helper']['sha256'],refs['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off');assert observed['nativeFiles']==357 and observed['grantsAuthority']is False
 assert r['sourceRoot']==str(FREEZE/'source')and r['componentizeSourceRoot']==str(FREEZE/'componentize-source')
 for key,prefix in [('sourceManifest','source'),('componentizeSourceManifest','componentize-source')]:
  for item in meta[key]:assert row(prefix+'/'+item['path'])['sha256']==item['sha256']
 selected=[]
 for item in meta['selectedModuleManifests']:
  d=row('source/'+item['path']);assert d['sha256']==item['sha256'];v=read(d);assert v['profileVersion']==item['profileVersion'];selected.append(v)
 hm=pure('hash_model.py');hm.validate_selected_manifests(meta,policy,selected)
 originals={}
 for name,item in copies.items():
  if item['original']is not None:originals.setdefault(item['original']['path'],[]).append(name)
 def original_row(d):
  choices=originals[d['path']];assert choices
  for name in choices:
   if copies[name]['original']==d:return row(name)
  raise AssertionError('Missing exact frozen original descriptor')
 dbdesc=next(copies[n]['original']for n in copies if copies[n]['original']and copies[n]['original']['path']==meta['compileCommandsPath']);database=read(original_row(dbdesc));assert len(database)==69
 hm.validate_hash_hmac_commands(database,meta['actualEmbeddingCompileCommands'],Path(refs['configuredSourceRoot']),meta,policy)
 ledger=read(row('build-proof/inputHashes.json'));assert len(ledger['files'])==r['verifiedBuildReferences']and r['verifiedBuildInputLedger']==result['inputHashes']
 plan=read(r['copyPlan']);assert plan['verifiedReferencesNotAllCopied']is True
 for item in plan['copies']:
  saved=copies[item['destination']];assert saved['original']==item['source']and saved['role']==item['role']and saved['sha256']==item['source']['sha256']and saved['bytes']==item['source']['bytes']
 rust=meta['privateRustupBootstrapPolicy']
 # Preserve old before-install JSON as DATA, without dereferencing its nested historical settings row.
 for d in [rust['beforeInstallRecord'],rust['settingsAtBuildCompletion']]:checked(original_row(d))
 for role,key in [('source-admission','sourceAdmissionEvidence'),('embedding-after','postBuildEmbeddingEvidence')]:
  e=r[key];t=read(e['terminal']);assert t['role']==role and t['stdout']==e['stdout']and t['stderr']==e['stderr']and t['rawExitCode']==0 and t['timeout']is False and t['errorType']is None and t['completeStreamsRetained']is True and t['engineExecuted']is t['compilerExecuted']is False;checked(e['stdout']);checked(e['stderr'])
 admission=read(r['sourceAdmissionEvidence']['stdout']);assert admission['sourceIndexSha256']==SOURCE_SHA and admission['controllerSourceIndexSha256']==expected_controller and admission['metadata']==result['metadata']and admission['state']=='NODE_CRYPTO_HASH_HMAC357_SOURCE_ADMISSION_DATA_PASSED_V2'
 e=r['postBuildEmbeddingEvidence'];commands=[]
 for line in checked(e['stdout']).read_text().splitlines():
  w=shlex.split(line)
  if w.count('-c')==1 and w[w.index('-c')+1]==e['sourcePath']:commands.append(line)
 assert commands==e['commands']==meta['actualEmbeddingCompileCommands']and len(commands)==1
 control=read(r['freezerControl']);assert control['rawMetadataFields']==83 and control['nativeSourceIndexed']==r['nativeSourceIndexed']and control['controllerSourceIndexed']==r['controllerSourceIndexed']and control['actualBuildReview']==r['actualBuildReview']and control['rootAuthority']==r['rootAuthority']
 assert(FREEZE.stat().st_dev,FREEZE.stat().st_ino)==(root_stat.st_dev,root_stat.st_ino);checked(receipt_row)
 return dict(schemaVersion=1,state='NODE_CRYPTO_HASH_HMAC357_FROZEN_CAPSULE_VERIFIED_NOT_ACCEPTED_V2',receipt=receipt_row,engine=r['engine'],metadata=r['metadata'],copies=len(copies),nativeSourceFiles=357,externalEmbeddingSources=3,selectedManifestCount=12,rawMetadataFields=83,originalReferencesReexecuted=False,independentActualFreezeReviewRequired=True,liveEvpSnapshotAdmission=False,engineExecuted=False,cryptoOperationsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
if __name__=='__main__':
 assert len(sys.argv)==3;print(json.dumps(verify_frozen(json.loads(sys.argv[2]),sys.argv[1])),flush=True)
