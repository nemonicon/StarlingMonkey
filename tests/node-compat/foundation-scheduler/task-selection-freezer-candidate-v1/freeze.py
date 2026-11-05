"""Explicit selector342 freeze body. Only called with this entry's genuine Frame."""
from pathlib import Path
import hashlib,json,os,stat,subprocess

def admission_model(value,frame,g):
 assert value['schemaVersion']==1 and value['state']=='TASK_SELECTION342_NORMAL_OFF_BUILD_SOURCE_ADMISSION_PASSED_V1'and value['variant']=='normal-off'
 assert value['taskSelectionSourceIndexSha256']==g.SOURCE_SHA and value['freezerSourceIndexSha256']==frame['config']['freezerIndex']['sha256']
 assert value['configuredSourceRoot']==str(g.SOURCE)and value['configuredLayerRoot']==str(g.SOURCE/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1')
 assert value['metadata']==frame['refs']['metadata']and value['sourceManifest']==frame['metadata']['sourceManifest']and value['externalSourceManifest']==frame['metadata']['componentizeSourceManifest']
 assert value['selectedManifestRows']==frame['metadata']['selectedModuleManifests']and value['selectedManifests']==frame['refs']['selectedManifestValues']and len(value['selectedManifests'])==9
 assert value['taskSelectionPolicy']==frame['metadata']['taskSelectionPolicy']and value['resourceOwnershipPolicy']==frame['metadata']['resourceOwnershipPolicy']
 for k,n in dict(sourceFiles=342,externalSources=3,selectedManifestCount=9,compileDatabaseRows=67,policyCppCommands=61,otherConfiguredSourceRows=5,generatedNullCppRows=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=5).items():assert value[k]==n
 assert value['metadataClassifier']==dict(state='FINITE_RESOURCE_TASK_SELECTION342_METADATA_SHAPE_ONLY',nativeFiles=342,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
 assert value['engineHashedAsGuardData']is True and value['engineExecuted']is False and value['operationalAdmission']is False and value['runtimeAcceptanceClaim']is False

def freeze(frame,g):
 g.require_frame(frame);g.recheck(frame);root=g.FREEZE;fd=None
 try:
  assert not root.exists()and not root.is_symlink();space=os.statvfs(root.parent);assert space.f_bavail*space.f_frsize>=2147483648
  io=g.load_own(frame,'copy_io.py');plan=g.read(next(r for r in frame['ownRows']if r['path']==str(g.OWN/'capture-plan.json')))
  os.umask(0o077);root.mkdir(mode=0o700);fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);identity=os.fstat(fd)
  def same_root():
   s=root.lstat();held=os.fstat(fd);assert stat.S_ISDIR(s.st_mode)and not root.is_symlink()and stat.S_IMODE(s.st_mode)==0o700 and(s.st_dev,s.st_ino)==(identity.st_dev,identity.st_ino)==(held.st_dev,held.st_ino)
  generated={}
  def write(name,data):
   same_root();path=root/name;io.destination(path,root);path.parent.mkdir(parents=True,exist_ok=True)
   with path.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
   d=dict(path=str(path),sha256=io.digest(data),bytes=len(data));g.checked(d);same_root();generated[name]=d;return d
  def raw_call(role,argv,timeout):
   status=None;stdout=b'';stderr=b'';timed_out=False;error_type=None;complete=True
   try:
    completed=subprocess.run(argv,cwd=str(g.SOURCE),env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,check=False)
    status=completed.returncode;stdout=completed.stdout;stderr=completed.stderr
   except subprocess.TimeoutExpired as error:
    timed_out=True;complete=False;stdout=error.stdout or b'';stderr=error.stderr or b'';error_type='TimeoutExpired'
   except OSError as error:
    complete=False;error_type=type(error).__name__
   # Save all available bytes and terminal before status/size/JSON assertions.
   out=write('helper-calls/'+role+'/stdout.log',stdout);err=write('helper-calls/'+role+'/stderr.log',stderr)
   terminal=write('helper-calls/'+role+'/terminal.json',(json.dumps(dict(schemaVersion=1,role=role,argv=argv,cwd=str(g.SOURCE),timeoutSeconds=timeout,rawExitCode=status,timedOut=timed_out,errorType=error_type,capturedStreamsComplete=complete,stdout=out,stderr=err,postBuildOnly=True,compilerExecuted=False,engineExecuted=False),indent=2)+'\n').encode())
   assert status==0 and not timed_out and complete and error_type is None and len(stdout)<=4*1024*1024 and len(stderr)<=4*1024*1024,'All available streams retained, no clipping/timeout/error acceptance'
   return dict(stdout=out,stderr=err,terminal=terminal),stdout
  config_json=json.dumps(frame['configRow'],separators=(',',':'))
  admission_argv=[frame['refs']['python']['path'],'-B','-I',str(g.OWN/'entry.py'),'admit',config_json]
  admission,admission_raw=raw_call('source-admission',admission_argv,600)
  value=json.loads(admission_raw.decode('utf8'),object_pairs_hook=g.unique);admission_model(value,frame,g);g.recheck(frame)
  meta=frame['metadata'];build=Path(meta['cmakeCachePath']).parent;ninja=frame['refs']['ninja'];g.checked(ninja)
  ninja_argv=[ninja['path'],'-C',str(build),'-t','commands','builtin_componentize_embedding']
  evidence,raw=raw_call('embedding-after',ninja_argv,120)
  embedding=io.embedding_command(raw,frame['refs']['externalSourceRoot']+'/embedding/embedding.cpp');assert embedding==meta['actualEmbeddingCompileCommands']
  for r in frame['database']:
   names=[p['path']for p in meta['sourceManifest']if p['path'].endswith('.cpp')and p['path'].startswith(('builtins/','runtime/'))and r['file']==str(g.SOURCE/p['path'])]
   if names:io.compile_command(r['command'],False,names[0],True,False)
  io.compile_command(embedding[0],False,'embedding/embedding.cpp',True,False)
  control=dict(schemaVersion=1,state='ACTUAL_TASK_SELECTION342_FREEZER_CONTROL_CAPTURE_V1',nativeSourceIndexed=frame['config']['taskSelectionSourceIndex'],freezerSourceIndexed=frame['config']['freezerIndex'],rootAuthority=frame['config']['rootAuthority'],sourceIndependentReview=frame['root']['sourceIndependentReview'],actualBuildReview=frame['refs']['actualBuildReview'],actualBuildInputLedger=frame['refs']['buildInputLedger'],configuredSourceRoot=str(g.SOURCE),workRoot=str(g.WORK),freezeRoot=str(root),activeEntry=next(r for r in frame['ownRows']if r['path']==str(g.OWN/'entry.py')),activeBody=next(r for r in frame['ownRows']if r['path']==str(g.OWN/'freeze.py')),genuineAdmissionModel=frame['refs']['configuredModel'],genuineAdmissionLayer=frame['refs']['configuredLayer'],rawMetadataUnchanged=True,engineHashedOnlyAsData=True,engineExecuted=False)
  control_row=write('normal-off-freezer-control.json',(json.dumps(control,indent=2)+'\n').encode())
  planned=[];origins={};destinations=set()
  def add(row,name,role):
   g.checked(row);assert name and not name.startswith('/')and '\\'not in name and all(p not in('','.','..')for p in name.split('/'))and name not in destinations;destinations.add(name)
   planned.append(dict(original=Path(row['path']),target=root/name,sha256=row['sha256'],shared=False));origins[name]=dict(source=row,role=role)
  for r in plan['copies']:add(r['source'],r['destination'],r['role'])
  for r in frame['ownRows']:add(r,'artifact-tools/source/'+str(Path(r['path']).relative_to(g.OWN)),'new-selector-freezer-source-capsule')
  peer=frame['root']['sourceIndependentReview']
  for r in g.family(peer['index']):add(r,'artifact-tools/source-review/'+str(Path(r['path']).relative_to(Path(peer['index']['path']).parent)),'new-freezer-source-review')
  add(frame['configRow'],'provenance/freeze-config.json','new-freeze-config');add(frame['config']['rootAuthority'],'provenance/freeze-root-authority.json','new-freeze-authority')
  receipt_path=root/'normal-off-freeze-receipt.json';g.recheck(frame);same_root();io.validate_plan(planned,receipt_path,root);io.execute_plan(planned,root);same_root();g.recheck(frame)
  copies=[];inodes=set()
  for name,v in origins.items():
   path=root/name;s=path.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600
   ident=(s.st_dev,s.st_ino);assert ident not in inodes and ident!=(Path(v['source']['path']).stat().st_dev,Path(v['source']['path']).stat().st_ino);inodes.add(ident)
   copies.append(dict(path=str(path),sha256=v['source']['sha256'],bytes=v['source']['bytes'],original=v['source'],role=v['role']))
  for name,d in generated.items():copies.append(dict(d,original=None,role='fresh-source-admission-Ninja-or-control-data'))
  # Directory entries, not only file contents, reach durable storage.
  for directory in sorted([p for p in root.rglob('*')if p.is_dir()],key=lambda p:len(p.parts),reverse=True):
   assert not directory.is_symlink();handle=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
   try:os.fsync(handle)
   finally:os.close(handle)
  os.fsync(fd);same_root()
  receipt=dict(schemaVersion=1,state='SCHEDULER_TASK_SELECTION342_NORMAL_OFF_NATIVE_FREEZE_COMPLETE_UNREVIEWED_V1',variant='normal-off',taskSelectionSourceIndexSha256=g.SOURCE_SHA,freezerSourceIndexSha256=frame['config']['freezerIndex']['sha256'],nativeSourceIndexed=frame['config']['taskSelectionSourceIndex'],freezerSourceIndexed=frame['config']['freezerIndex'],rootAuthority=frame['config']['rootAuthority'],sourceIndependentReview=frame['root']['sourceIndependentReview'],actualBuildReview=frame['refs']['actualBuildReview'],configuredSourceRoot=str(g.SOURCE),workRoot=str(g.WORK),sourceRoot=str(root/'source'),componentizeSourceRoot=str(root/'componentize-source'),engine=dict(frame['refs']['engine'],path=str(root/'normal-off.engine.wasm')),metadata=dict(frame['refs']['metadata'],path=str(root/'normal-off.engine.wasm.build.json')),rawMetadataBytesUnchanged=True,rawMetadataOriginalConfiguredPathsPreserved=True,taskSelectionPolicy=meta['taskSelectionPolicy'],resourceOwnershipPolicy=meta['resourceOwnershipPolicy'],nativeInputsVerified=342,unchangedResourceParentFiles=339,nativeReplacements=3,externalEmbeddingInputsVerified=3,selectedManifestCount=9,compileDatabaseRows=67,policyCppCommands=61,otherConfiguredSourceRows=5,generatedNullCppRows=1,embeddingRowsInCompileDatabase=0,separatePostBuildEmbeddingCommands=1,actualStrictCommands=4,actualPrivateClassicCommands=5,sourceAdmissionEvidence=admission,postBuildEmbeddingEvidence=dict(**evidence,sourcePath=frame['refs']['externalSourceRoot']+'/embedding/embedding.cpp',commands=embedding,beforeBuildCaptureExists=False),freezerControl=control_row,staticLibrariesPhysicallyCopied=29,copies=copies,verifiedBuildInputLedger=frame['refs']['buildInputLedger'],verifiedOriginalReferenceCount=20761,verifiedReferencesNotAllCopied=True,verifiedSdkAliases=frame['refs']['sdkAliases'],declaredArchiveHardlinks=frame['refs']['declaredArchiveHardlinks'],sdkAliasesNotCopiedAsLinks=True,allInputsValidatedBeforeHelperImports=True,allInputsValidatedBeforeCopies=True,allCopiesAndOriginalsRehashed=True,receiptRequiresExternalParentZeroAndIndependentReview=True,nativeAllInvalidRuntimeValidation=None,resourceNativeRuntimeValidation=None,gcReconfigureAllowed=False,reviewedEnginePins=None,engineExecuted=False,bootstrapExecuted=False,componentOrGuestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
  receipt_row=write('normal-off-freeze-receipt.json',(json.dumps(receipt,indent=2)+'\n').encode());os.fsync(fd);same_root()
  verified=g.load_own(frame,'verify.py').verify_frozen(receipt_row,frame['config']['freezerIndex']['sha256']);g.recheck(frame);same_root();return verified
 finally:
  try:g.recheck(frame)
  finally:
   if fd is not None:os.close(fd)
