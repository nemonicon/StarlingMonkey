"""Frozen-only DATA verifier. No original input/helper imports or engine calls."""
from pathlib import Path
import hashlib,json,os,re,shlex,stat,sys
FREEZE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze')
SOURCE_SHA='88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1'
ENGINE='f6a775f019ca48bb6b9a46a88364aa51a2691101a9e79325848afb5504c3034f'
META='8219b7aaea6f5a311ccd9e2d038edcd213663078f9ff18917c155dfeb51dde4f'
def checked(row):
 assert type(row)is dict and set(row)=={'path','sha256','bytes'}and type(row['path'])is str and row['path'].startswith('/')and str(Path(row['path']))==row['path']and '..'not in Path(row['path']).parts and '\\'not in row['path']and '\0'not in row['path']
 assert type(row['bytes'])is int and row['bytes']>=0 and re.fullmatch('[a-f0-9]{64}',row['sha256'])
 p=Path(row['path'])
 for q in(p,*p.parents):assert not q.is_symlink()
 a=p.stat();assert stat.S_ISREG(a.st_mode);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)and a.st_size==row['bytes']and h.hexdigest()==row['sha256'];return p
def frozen_json(row):
 assert row['bytes']<=32*1024*1024;return json.loads(checked(row).read_bytes())
def receipt_model(r,expected_source):
 assert r['schemaVersion']==1 and r['state']=='SCHEDULER_TASK_SELECTION342_NORMAL_OFF_NATIVE_FREEZE_COMPLETE_UNREVIEWED_V1'and r['variant']=='normal-off'
 assert r['taskSelectionSourceIndexSha256']==SOURCE_SHA and r['nativeSourceIndexed']['sha256']==SOURCE_SHA and r['freezerSourceIndexSha256']==r['freezerSourceIndexed']['sha256']==expected_source
 assert r['engine']['sha256']==ENGINE and r['metadata']['sha256']==META and r['nativeInputsVerified']==342 and r['unchangedResourceParentFiles']==339 and r['nativeReplacements']==3 and r['externalEmbeddingInputsVerified']==3 and r['selectedManifestCount']==9
 for k,n in dict(compileDatabaseRows=67,policyCppCommands=61,otherConfiguredSourceRows=5,generatedNullCppRows=1,embeddingRowsInCompileDatabase=0,separatePostBuildEmbeddingCommands=1,actualStrictCommands=4,actualPrivateClassicCommands=5,staticLibrariesPhysicallyCopied=29,verifiedOriginalReferenceCount=20761).items():assert r[k]==n
 for k in('rawMetadataBytesUnchanged','rawMetadataOriginalConfiguredPathsPreserved','allInputsValidatedBeforeHelperImports','allInputsValidatedBeforeCopies','allCopiesAndOriginalsRehashed','receiptRequiresExternalParentZeroAndIndependentReview','verifiedReferencesNotAllCopied','sdkAliasesNotCopiedAsLinks'):assert r[k]is True
 for k in('gcReconfigureAllowed','engineExecuted','bootstrapExecuted','componentOrGuestExecuted','operationalAdmission','runtimeAcceptanceClaim'):assert r[k]is False
 assert r['nativeAllInvalidRuntimeValidation']is None and r['resourceNativeRuntimeValidation']is None and r['reviewedEnginePins']is None
def verify_frozen(receipt_row,expected_source):
 assert __debug__ and sys.dont_write_bytecode and re.fullmatch('[a-f0-9]{64}',expected_source)
 assert receipt_row['path']==str(FREEZE/'normal-off-freeze-receipt.json');r=frozen_json(receipt_row);receipt_model(r,expected_source)
 before=FREEZE.lstat();assert stat.S_ISDIR(before.st_mode)and stat.S_IMODE(before.st_mode)==0o700 and not FREEZE.is_symlink()
 copies={};inodes=set()
 for item in r['copies']:
  path=Path(item['path']);name=path.relative_to(FREEZE).as_posix();assert name and all(p not in('','.','..')for p in name.split('/'))and name not in copies
  checked({k:item[k]for k in('path','sha256','bytes')});s=path.lstat();identity=(s.st_dev,s.st_ino)
  assert identity not in inodes and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600;inodes.add(identity);copies[name]=item
 actual=set()
 for path in FREEZE.rglob('*'):
  s=path.lstat();assert not path.is_symlink()
  if stat.S_ISDIR(s.st_mode):assert stat.S_IMODE(s.st_mode)==0o700
  else:assert stat.S_ISREG(s.st_mode);actual.add(path.relative_to(FREEZE).as_posix())
 receipt_stat=Path(receipt_row['path']).stat();assert actual==set(copies)|{'normal-off-freeze-receipt.json'}and stat.S_IMODE(receipt_stat.st_mode)==0o600 and receipt_stat.st_nlink==1 and(receipt_stat.st_dev,receipt_stat.st_ino)not in inodes
 # Externally supplied own source SHA, saved own index and actual executing
 # verifier bytes agree, whether this exact file is original or frozen.
 frozen_index=FREEZE/'artifact-tools/source/index.json';assert hashlib.sha256(frozen_index.read_bytes()).hexdigest()==expected_source
 index=json.loads(frozen_index.read_bytes());names=set()
 for item in index['files']:
  name=item['path'];assert name and not name.startswith('/')and all(p not in('','.','..')for p in name.split('/'))and name not in names;names.add(name)
  saved=copies['artifact-tools/source/'+name];assert saved['sha256']==item['sha256']and saved['bytes']==item['bytes']
 verifier=next(x for x in index['files']if x['path']=='verify.py');self_path=Path(__file__).resolve();assert hashlib.sha256(self_path.read_bytes()).hexdigest()==verifier['sha256']and self_path.stat().st_size==verifier['bytes']
 capture=json.loads((FREEZE/'artifact-tools/source/capture-plan.json').read_bytes())
 for item in capture['copies']:
  c=copies[item['destination']];assert c['original']==item['source']and c['role']==item['role']and c['sha256']==item['source']['sha256']and c['bytes']==item['source']['bytes']
 assert r['engine']['path']==str(FREEZE/'normal-off.engine.wasm')and r['metadata']['path']==str(FREEZE/'normal-off.engine.wasm.build.json')
 metadata=frozen_json(r['metadata']);checked(r['engine']);policy=json.loads((FREEZE/'build-evidence/task-selection-policy.json').read_bytes())
 assert metadata['engineSha256']==ENGINE and metadata['engineBytes']==r['engine']['bytes']and metadata['gcStress']is False and metadata['entropyPolicy']=='off'and metadata['sourceManifest']==policy['expectedNativeSourceManifest']and len(metadata['sourceManifest'])==342 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==9
 assert r['taskSelectionPolicy']==metadata['taskSelectionPolicy']and r['resourceOwnershipPolicy']==metadata['resourceOwnershipPolicy']and metadata['taskSelectionPolicy']['sourcePolicy']==policy['taskSelectionSourcePolicy']
 assert metadata['taskSelectionPolicy']['nativeAllInvalidRuntimeValidation']is None and metadata['taskSelectionPolicy']['fullResetOrReuse']is False
 for key,prefix in(('sourceManifest','source'),('componentizeSourceManifest','componentize-source')):
  for row in metadata[key]:assert copies[prefix+'/'+row['path']]['sha256']==row['sha256']
 assert len([x for x in copies.values()if x['role']=='selected-static-library'])==29
 assert copies['tooling/wasi_snapshot_preview1.wasm']['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'and copies['tooling/wasi_snapshot_preview1.wasm']['bytes']==53512
 refs=json.loads((FREEZE/'artifact-tools/source/references.json').read_bytes())
 assert r['verifiedSdkAliases']==refs['sdkAliases']and r['declaredArchiveHardlinks']==refs['declaredArchiveHardlinks']
 selected=[]
 for row in metadata['selectedModuleManifests']:
  p=FREEZE/'source'/row['path'];assert copies['source/'+row['path']]['sha256']==row['sha256'];value=json.loads(p.read_bytes());assert value['profileVersion']==row['profileVersion'];selected.append(value)
 for role,e in(('source-admission',r['sourceAdmissionEvidence']),('embedding-after',r['postBuildEmbeddingEvidence'])):
  for k in('stdout','stderr','terminal'):assert{k2:copies['helper-calls/'+role+'/'+{'stdout':'stdout.log','stderr':'stderr.log','terminal':'terminal.json'}[k]][k2]for k2 in('path','sha256','bytes')}==e[k]
  t=frozen_json(e['terminal']);assert t['rawExitCode']==0 and t['timedOut']is False and t['errorType']is None and t['capturedStreamsComplete']is True and t['compilerExecuted']is False and t['engineExecuted']is False and t['role']==role and t['stdout']==e['stdout']and t['stderr']==e['stderr']and t['cwd']==refs['configuredSourceRoot']
 a=frozen_json(r['sourceAdmissionEvidence']['stdout']);assert a['state']=='TASK_SELECTION342_NORMAL_OFF_BUILD_SOURCE_ADMISSION_PASSED_V1'and a['taskSelectionSourceIndexSha256']==SOURCE_SHA and a['freezerSourceIndexSha256']==expected_source and a['metadata']==refs['metadata']and a['sourceManifest']==metadata['sourceManifest']and a['taskSelectionPolicy']==metadata['taskSelectionPolicy']and a['resourceOwnershipPolicy']==metadata['resourceOwnershipPolicy']and a['selectedManifestRows']==metadata['selectedModuleManifests']and a['selectedManifests']==selected and a['engineHashedAsGuardData']is True and a['engineExecuted']is False and a['operationalAdmission']is False and a['runtimeAcceptanceClaim']is False
 for k,n in dict(sourceFiles=342,externalSources=3,selectedManifestCount=9,compileDatabaseRows=67,policyCppCommands=61,otherConfiguredSourceRows=5,generatedNullCppRows=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=5).items():assert a[k]==n
 assert a['metadataClassifier']==dict(state='FINITE_RESOURCE_TASK_SELECTION342_METADATA_SHAPE_ONLY',nativeFiles=342,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
 admission_terminal=frozen_json(r['sourceAdmissionEvidence']['terminal']);assert admission_terminal['argv']==[refs['python']['path'],'-B','-I',str(Path(r['freezerSourceIndexed']['path']).parent/'entry.py'),'admit',json.dumps(copies['provenance/freeze-config.json']['original'],separators=(',',':'))]
 e=r['postBuildEmbeddingEvidence'];assert e['beforeBuildCaptureExists']is False and e['commands']==metadata['actualEmbeddingCompileCommands']and len(e['commands'])==1
 commands=[]
 for line in checked(e['stdout']).read_text().splitlines():
  if' -c 'in line:
   words=shlex.split(line)
   if words.count('-c')==1 and words[words.index('-c')+1]==e['sourcePath']:commands.append(line)
 assert commands==e['commands'];t=frozen_json(e['terminal']);assert t['argv']==[refs['ninja']['path'],'-C',str(Path(metadata['cmakeCachePath']).parent),'-t','commands','builtin_componentize_embedding']
 control=frozen_json(r['freezerControl']);assert control['nativeSourceIndexed']==r['nativeSourceIndexed']and control['freezerSourceIndexed']==r['freezerSourceIndexed']and control['actualBuildReview']==r['actualBuildReview']and control['engineExecuted']is False
 after=FREEZE.lstat();assert(before.st_dev,before.st_ino)==(after.st_dev,after.st_ino);checked(receipt_row)
 return dict(schemaVersion=1,state='TASK_SELECTION342_NORMAL_FREEZE_READ_ONLY_CAPSULE_VERIFIED_NOT_ACCEPTED_V1',receipt=receipt_row,engine=r['engine'],metadata=r['metadata'],copies=len(copies),nativeSourceFiles=342,externalEmbeddingSources=3,selectedManifests=9,originalBuildReferencesNotReexecuted=True,requiresExternalParentZeroAndIndependentReview=True,engineExecuted=False,bootstrapExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
if __name__=='__main__':
 assert len(sys.argv)==3
 print(json.dumps(verify_frozen(json.loads(sys.argv[2]),sys.argv[1])),flush=True)
