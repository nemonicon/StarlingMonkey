"""Dormant357 freeze; future reviewed BUILD DATA is mandatory, no metadata rewriting."""
from pathlib import Path
import hashlib,json,os,shlex,stat,subprocess

def selected_plan(frame,metadata):
 io=frame['io'];refs=frame['refs'];root=Path(refs['freezeRoot']);work=Path(refs['workRoot']);source=Path(refs['configuredSourceRoot']);ledger={r['path']:r for r in frame['buildLedger']['files']};plan=[];names=set()
 def add(row,name,role):
  io.confined(name);assert name not in names;names.add(name);io.checked(row);plan.append(dict(source=row,destination=name,role=role))
 add(frame['buildProof']['engine'],'normal-off.engine.wasm','raw-engine-DATA');add(frame['buildProof']['metadata'],'normal-off.engine.wasm.build.json','byte-exact-raw83-metadata')
 for r in frame['stage']['copies']:add(dict(path=str(source/r['path']),sha256=r['sha256'],bytes=r['bytes']),'source/'+r['path'],'current-configured-source-or-tool-DATA')
 external=Path(metadata['combinedNativeSourcePolicy']['externalConfiguredSourceRoot'])
 for r in metadata['componentizeSourceManifest']:
  p=external/r['path'];add(dict(path=str(p),sha256=r['sha256'],bytes=p.stat().st_size),'componentize-source/'+r['path'],'actual-external-embedding-source')
 # Rehash the entire BUILD ledger, but physically copy only these finite current-WORK
 # evidence roles. Old proof trees and SDK distributions are not recursively copied.
 selected={}
 for r in ledger.values():
  p=Path(r['path'])
  if p.is_relative_to(work)and(p.suffix in ['.a','.o']or p.name in ['CMakeCache.txt','compile_commands.json','build.ninja','rules.ninja','null.cpp','Cargo.toml','Cargo.lock','configdata.pm','moz-config.h','js-confdefs.h','wasi-sdk-version.txt','VERSION']):selected[r['path']]=r
 for k in ['cmakeCachePath','compileCommandsPath']:
  p=Path(metadata[k]);r=io.row(p);assert ledger.get(r['path'])==r;selected[r['path']]=r
 rust=metadata['privateRustupBootstrapPolicy']
 for r in [rust['beforeInstallRecord'],rust['settingsAtBuildCompletion']]:assert ledger.get(r['path'])==r;selected[r['path']]=r
 for r in selected.values():add(r,'build-evidence/'+Path(r['path']).relative_to(work).as_posix(),'current-WORK-library-object-or-build-DATA')
 for r in frame['ownRows']:add(r,'artifact-tools/source/'+Path(r['path']).relative_to(Path(frame['ownIndex']['path']).parent).as_posix(),'active-controller-source-capsule')
 add(refs['policy'],'build-evidence/active-policy.json','original7c5a-policy-DATA')
 for key in ['recipe','helper']:add(refs[key],'build-evidence/active-'+Path(refs[key]['path']).name,'active-original-producer-DATA')
 for role,r in dict(index=frame['root']['actualBuildReview']['index'],result=frame['root']['actualBuildReview']['result'],contract=frame['root']['actualBuildContract'],inputHashes=frame['buildProof']['inputHashes'],referenceAliases=frame['buildProof']['referenceAliases']).items():add(r,'build-proof/'+role+'.json','retained-BUILD-proof-DATA-not-relocated-family')
 peer=frame['root']['controllerSourceReview']
 for r in io.family(peer['index']):add(r,'source-review/'+Path(r['path']).relative_to(Path(peer['index']['path']).parent).as_posix(),'controller-source-peer')
 add(frame['configRow'],'provenance/config.json','new-freeze-config');add(frame['config']['rootAuthority'],'provenance/root-authority.json','new-freeze-Root-authority')
 assert len(plan)<=16384 and len({r['path']for r in selected.values()})==len(selected)
 return plan

def run(frame,recheck):
 io=frame['io'];refs=frame['refs'];root=Path(refs['freezeRoot']);io.absent(root);s=os.statvfs(root.parent);assert s.f_bavail*s.f_frsize>=2147483648
 assert frame['root']['phase']=='freeze'and frame['buildProof'];recheck(frame);os.umask(0o077);root.mkdir(mode=0o700)
 fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);identity=os.fstat(fd);generated={};complete=False
 def same():
  s=root.lstat();held=os.fstat(fd);assert stat.S_ISDIR(s.st_mode)and stat.S_IMODE(s.st_mode)==0o700 and(s.st_dev,s.st_ino)==(identity.st_dev,identity.st_ino)==(held.st_dev,held.st_ino)
 def write(name,data):
  same();io.confined(name);p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
  for q in(p,*p.parents):assert not q.is_symlink()
  handle=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  try:
   with os.fdopen(handle,'wb',closefd=False)as f:assert f.write(data)==len(data);f.flush();os.fsync(handle)
  finally:os.close(handle)
  io.fsync_dir(p.parent);d=io.row(p);generated[name]=d;same();return d
 def json_write(name,value):return write(name,(json.dumps(value,indent=2)+'\n').encode())
 def raw_call(role,argv,timeout):
  status=None;stdout=b'';stderr=b'';timeout_seen=False;error_type=None;streams_complete=True
  try:
   p=subprocess.run(argv,cwd=refs['configuredSourceRoot'],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,check=False);status=p.returncode;stdout=p.stdout;stderr=p.stderr
  except subprocess.TimeoutExpired as e:timeout_seen=True;streams_complete=False;stdout=e.stdout or b'';stderr=e.stderr or b'';error_type='TimeoutExpired'
  except OSError as e:streams_complete=False;error_type=type(e).__name__
  out=write('helper-calls/'+role+'/stdout.log',stdout);err=write('helper-calls/'+role+'/stderr.log',stderr)
  terminal=json_write('helper-calls/'+role+'/terminal.json',dict(schemaVersion=1,role=role,argv=argv,cwd=refs['configuredSourceRoot'],timeoutSeconds=timeout,rawExitCode=status,timeout=timeout_seen,errorType=error_type,completeStreamsRetained=streams_complete,stdout=out,stderr=err,engineExecuted=False,compilerExecuted=False))
  assert status==0 and timeout_seen is False and error_type is None and streams_complete and len(stdout)<=4*1024*1024 and len(stderr)<=4*1024*1024,'Complete available streams persisted before acceptance; no clipping'
  return dict(stdout=out,stderr=err,terminal=terminal),stdout
 try:
  config=json.dumps(frame['configRow'],separators=(',',':'));argv=[refs['python']['path'],'-B','-I',str(Path(frame['ownIndex']['path']).parent/'controller.py'),'admit',config]
  admission,raw=raw_call('source-admission',argv,600);a=json.loads(raw);assert a['sourceIndexSha256']==refs['integrationSourceIndex']['sha256']and a['controllerSourceIndexSha256']==frame['ownIndex']['sha256']and a['rawMetadataFields']==83 and a['state']=='NODE_CRYPTO_HASH_HMAC357_SOURCE_ADMISSION_DATA_PASSED_V2'
  meta=io.read(frame['buildProof']['metadata']);assert a['metadata']==frame['buildProof']['metadata'];recheck(frame)
  ninja=[refs['ninja']['path'],'-C',str(Path(meta['cmakeCachePath']).parent),'-t','commands','builtin_componentize_embedding'];embedding,raw=raw_call('embedding-after',ninja,120)
  copy=frame['loadOwn']('copy_io.py');source=meta['combinedNativeSourcePolicy']['externalConfiguredSourceRoot']+'/embedding/embedding.cpp';commands=copy.embedding_command(raw,source);assert commands==meta['actualEmbeddingCompileCommands']
  plan=selected_plan(frame,meta);assert sum(r['source']['bytes']for r in plan)+838860800<=os.statvfs(root).f_bavail*os.statvfs(root).f_frsize
  plan_row=json_write('actual-copy-plan.json',dict(schemaVersion=1,copies=plan,verifiedReferencesNotAllCopied=True))
  control=json_write('normal-off-freezer-control.json',dict(schemaVersion=1,nativeSourceIndexed=refs['integrationSourceIndex'],controllerSourceIndexed=frame['ownIndex'],actualStageReview=refs['actualStageReview'],actualBuildReview=frame['root']['actualBuildReview'],rootAuthority=frame['config']['rootAuthority'],rawMetadataFields=83,rawMetadataUnchanged=True,configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],freezeRoot=str(root),privateRustupBootstrapPolicy=meta['privateRustupBootstrapPolicy'],historicalPreinstallNestedSettingsRehashed=False,liveEvpSnapshotAdmission=False,engineExecuted=False,cryptoOperationsInvoked=False))
  targets=[dict(original=Path(r['source']['path']),target=root/r['destination'],sha256=r['source']['sha256'],shared=False)for r in plan]
  receipt_path=root/'normal-off-freeze-receipt.json';same();recheck(frame);copy.validate_plan(targets,receipt_path,root);copy.execute_plan(targets,root);same();recheck(frame)
  copies=[];ids=set()
  for r in plan:
   p=root/r['destination'];d=io.row(p);s=p.stat();old=io.checked(r['source']).stat();assert s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and(s.st_dev,s.st_ino)!=(old.st_dev,old.st_ino)and(s.st_dev,s.st_ino)not in ids;ids.add((s.st_dev,s.st_ino));assert d['sha256']==r['source']['sha256']and d['bytes']==r['source']['bytes'];copies.append(dict(d,original=r['source'],role=r['role']))
  copies += [dict(r,original=None,role='fresh-raw-admission-Ninja-control-or-copy-plan')for r in generated.values()]
  receipt=dict(schemaVersion=1,state='NODE_CRYPTO_HASH_HMAC357_NORMAL_OFF_FREEZE_COMPLETE_UNREVIEWED_V2',variant='normal-off',sourceIndexSha256=refs['integrationSourceIndex']['sha256'],controllerSourceIndexSha256=frame['ownIndex']['sha256'],controllerSourceIndexed=frame['ownIndex'],nativeSourceIndexed=refs['integrationSourceIndex'],actualBuildReview=frame['root']['actualBuildReview'],actualBuildContract=frame['root']['actualBuildContract'],rootAuthority=frame['config']['rootAuthority'],controllerSourceReview=frame['root']['controllerSourceReview'],configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],sourceRoot=str(root/'source'),componentizeSourceRoot=str(root/'componentize-source'),engine=dict(frame['buildProof']['engine'],path=str(root/'normal-off.engine.wasm')),metadata=dict(frame['buildProof']['metadata'],path=str(root/'normal-off.engine.wasm.build.json')),nativeSourceFiles=357,externalEmbeddingSources=3,selectedManifestCount=12,rawMetadataFields=83,compileDatabaseRows=69,policyCpp=63,strictCpp=4,privateCpp=7,separateEmbeddingCpp=1,sourceAdmissionEvidence=admission,postBuildEmbeddingEvidence=dict(**embedding,sourcePath=source,commands=commands),freezerControl=control,copyPlan=plan_row,copies=copies,verifiedBuildInputLedger=frame['buildProof']['inputHashes'],verifiedBuildReferences=len(frame['buildLedger']['files']),verifiedReferencesNotAllCopied=True,rawMetadataUnchanged=True,rawMetadataOriginalPathsPreserved=True,historicalPreinstallNestedSettingsRehashed=False,perCompilerRawExitProofClaim=False,engineExecuted=False,guestExecuted=False,cryptoOperationsInvoked=False,liveEvpSnapshotAdmission=False,pinsAdopted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
  for p in sorted([q for q in root.rglob('*')if q.is_dir()],key=lambda q:len(q.parts),reverse=True):io.fsync_dir(p)
  same();d=json_write('normal-off-freeze-receipt.json',receipt);os.fsync(fd);same();result=frame['loadOwn']('verify_frozen.py').verify_frozen(d,frame['ownIndex']['sha256']);recheck(frame);complete=True;print(json.dumps(result),flush=True);return result
 except BaseException as error:
  try:json_write('failed-freeze.json',dict(schemaVersion=1,state='FAILED_UNACCEPTED',errorType=type(error).__name__,complete=False,availableGeneratedEvidence=generated,engineExecuted=False,cryptoOperationsInvoked=False))
  except BaseException:pass
  raise
 finally:
  try:recheck(frame);same()
  finally:os.close(fd)
