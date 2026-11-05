"""Read-only frozen capsule checks; no helper/bootstrap/selector/engine execution."""
from pathlib import Path
import hashlib,json,os,shlex,stat,sys
FREEZE=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-freeze')
ENGINE='fec7a900f0c04815e3609d2f9a5ed94056d854bd1a8f241bf74cb5f3f475a704'
META='51fbc0a06ed2e06c24e6d1fd3190873a5a3190657cfe2d74bf44ff4128b0e80e'
def checked(row):
 p=Path(row['path']);assert type(row['path'])is str and row['path'].startswith('/')and str(p)==row['path']and '..'not in p.parts
 for a in(p,*p.parents):assert not a.is_symlink()
 before=p.stat();assert stat.S_ISREG(before.st_mode);h=hashlib.sha256()
 with p.open('rb')as stream:
  for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
 after=p.stat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
 assert before.st_size==row['bytes']and h.hexdigest()==row['sha256'];return p
def receipt_model(r):
 assert r['schemaVersion']==1 and r['state']=='SCHEDULER_RESOURCE342_NORMAL_OFF_NATIVE_FREEZE_COMPLETE_UNREVIEWED_V1'and r['variant']=='normal-off'
 assert r['resourceSourceIndexSha256']=='20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414'
 assert r['engine']['sha256']==ENGINE and r['metadata']['sha256']==META and r['nativeInputsVerified']==342 and r['externalEmbeddingInputsVerified']==3 and r['selectedManifestCount']==9
 assert r['compileDatabaseRows']==67 and r['policyCppCommands']==61 and r['otherConfiguredSourceRows']==5 and r['generatedNullCppRows']==1 and r['embeddingRowsInCompileDatabase']==0 and r['separatePostBuildEmbeddingCommands']==1
 assert r['actualStrictCommands']==4 and r['actualPrivateClassicCommands']==5 and r['staticLibrariesPhysicallyCopied']==29
 assert r['rawMetadataBytesUnchanged']is True and r['rawMetadataOriginalConfiguredPathsPreserved']is True and r['receiptRequiresExternalParentZeroAndIndependentReview']is True
 assert r['allInputsValidatedBeforeCopies']is True and r['allCopiesAndOriginalsRehashed']is True
 for k in('gcReconfigureAllowed','engineExecuted','bootstrapExecuted','componentOrGuestExecuted','operationalAdmission','runtimeAcceptanceClaim'):assert r[k]is False
 assert r['resourceNativeRuntimeValidation']is None and r['reviewedEnginePins']is None
def verify_frozen(receipt_row):
 assert __debug__ and sys.dont_write_bytecode
 assert receipt_row['path']==str(FREEZE/'normal-off-freeze-receipt.json');r=json.loads(checked(receipt_row).read_bytes());receipt_model(r)
 before=FREEZE.lstat();assert stat.S_ISDIR(before.st_mode)and stat.S_IMODE(before.st_mode)==0o700 and not FREEZE.is_symlink()
 copies={}
 for item in r['copies']:
  path=Path(item['path']);name=path.relative_to(FREEZE).as_posix();assert name and all(p not in('','.','..')for p in name.split('/'))and name not in copies
  checked({k:item[k]for k in('path','sha256','bytes')});s=path.lstat();assert s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600;copies[name]=item
 actual=set()
 for path in FREEZE.rglob('*'):
  s=path.lstat();assert not path.is_symlink()
  if stat.S_ISDIR(s.st_mode):assert stat.S_IMODE(s.st_mode)==0o700
  else:assert stat.S_ISREG(s.st_mode);actual.add(path.relative_to(FREEZE).as_posix())
 assert actual==set(copies)|{'normal-off-freeze-receipt.json'}
 # Interpret only the copied own INDEX and finite plan; never relocated prep paths.
 frozen_index=FREEZE/'artifact-tools/source/index.json';assert hashlib.sha256(frozen_index.read_bytes()).hexdigest()==r['freezerSourceIndexSha256']
 for item in json.loads(frozen_index.read_bytes())['files']:
  assert copies['artifact-tools/source/'+item['path']]['sha256']==item['sha256']and copies['artifact-tools/source/'+item['path']]['bytes']==item['bytes']
 capture=json.loads((FREEZE/'artifact-tools/source/capture-plan.json').read_bytes())
 for item in capture['copies']:
  c=copies[item['destination']];assert c['original']==item['source']and c['role']==item['role']and c['sha256']==item['source']['sha256']and c['bytes']==item['source']['bytes']
 assert r['engine']['path']==str(FREEZE/'normal-off.engine.wasm')and r['metadata']['path']==str(FREEZE/'normal-off.engine.wasm.build.json')
 metadata=json.loads(checked(r['metadata']).read_bytes());checked(r['engine'])
 assert metadata['engineSha256']==ENGINE and metadata['engineBytes']==r['engine']['bytes']and metadata['gcStress']is False and metadata['entropyPolicy']=='off'and len(metadata['sourceManifest'])==342 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==9
 assert metadata['resourceOwnershipPolicy']['nativeRuntimeValidation']is None and metadata['resourceOwnershipPolicy']['fullResetOrReuse']is False
 for key,prefix in [('sourceManifest','source'),('componentizeSourceManifest','componentize-source')]:
  for row in metadata[key]:assert copies[prefix+'/'+row['path']]['sha256']==row['sha256']
 assert len([r for r in copies.values()if r['role']=='selected-static-library'])==29
 assert copies['tooling/wasi_snapshot_preview1.wasm']['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'and copies['tooling/wasi_snapshot_preview1.wasm']['bytes']==53512
 e=r['postBuildEmbeddingEvidence'];assert e['beforeBuildCaptureExists']is False and e['commands']==metadata['actualEmbeddingCompileCommands']and len(e['commands'])==1
 for field,name in [('stdout','normal-off-embedding.after.stdout.txt'),('stderr','normal-off-embedding.after.stderr.txt'),('terminal','normal-off-embedding.after.terminal.json')]:assert{key:copies[name][key]for key in('path','sha256','bytes')}==e[field]
 selected=[]
 for line in checked(e['stdout']).read_text().splitlines():
  if' -c 'in line:
   words=shlex.split(line)
   if words.count('-c')==1 and words[words.index('-c')+1]==e['sourcePath']:selected.append(line)
 assert selected==e['commands']
 t=json.loads(checked(e['terminal']).read_bytes());assert t['rawExitCode']==0 and t['timedOut']is False and t['capturedStreamsComplete']is True and t['postBuildOnly']is True and t['compilerExecutedByThisCommand']is False and t['engineExecuted']is False
 source_refs=json.loads((FREEZE/'artifact-tools/source/references.json').read_bytes());assert t['argv']==[source_refs['ninja']['path'],'-C',str(Path(metadata['cmakeCachePath']).parent),'-t','commands','builtin_componentize_embedding']
 assert r['verifiedSdkAliases']==source_refs['sdkAliases']and r['sdkAliasesNotCopiedAsLinks']is True
 after=FREEZE.lstat();assert(before.st_dev,before.st_ino)==(after.st_dev,after.st_ino);checked(receipt_row)
 return dict(schemaVersion=1,state='RESOURCE342_NORMAL_FREEZE_READ_ONLY_CAPSULE_VERIFIED_NOT_ACCEPTED_V1',receipt=receipt_row,engine=r['engine'],metadata=r['metadata'],copies=len(copies),nativeSourceFiles=342,externalEmbeddingSources=3,selectedManifests=9,originalBuildReferencesNotReexecuted=True,requiresExternalParentZeroAndIndependentReview=True,engineExecuted=False,bootstrapExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
if __name__=='__main__':assert len(sys.argv)==2;print(json.dumps(verify_frozen(json.loads(sys.argv[1]))),flush=True)
