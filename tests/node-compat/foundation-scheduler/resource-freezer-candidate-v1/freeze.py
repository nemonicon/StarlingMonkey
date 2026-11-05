"""Dormant finite normal342 freezer. No helper/action occurs merely by importing it."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,subprocess,sys
OWN=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/resource-freezer-candidate-v1')
def initial(row):
 p=Path(row['path']);assert type(row['path'])is str and row['path'].startswith('/')and str(p)==row['path']and '..'not in p.parts
 for q in(p,*p.parents):assert not q.is_symlink()
 a=p.stat();assert p.is_file();b=p.read_bytes();z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 assert len(b)==row['bytes']and hashlib.sha256(b).hexdigest()==row['sha256'];return b
def own_bootstrap(config_row):
 assert __debug__ and sys.dont_write_bytecode
 cfg=json.loads(initial(config_row));ix=cfg['freezerIndex'];assert ix['path']==str(OWN/'index.json');value=json.loads(initial(ix));names=set()
 for r in value['files']:
  n=r['path'];assert n and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/'))and n not in names;names.add(n);initial(dict(path=str(OWN/n),sha256=r['sha256'],bytes=r['bytes']))
 assert not any(p.is_symlink()for p in OWN.rglob('*'))
 assert{p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}==names|{'index.json'}
 spec=importlib.util.spec_from_file_location('resource342_freeze_guard',OWN/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);return g,g.authorize(config_row)
def freeze(config_row):
 g,frame=own_bootstrap(config_row);root=g.FREEZE;fd=None
 try:
  assert not root.exists()and not root.is_symlink();space=os.statvfs(root.parent);assert space.f_bavail*space.f_frsize>=2147483648
  spec=importlib.util.spec_from_file_location('resource342_explicit_copy_functions',OWN/'copy_io.py');io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)
  plan_data=g.read(next(r for r in frame['ownRows']if r['path']==str(OWN/'capture-plan.json')));g.recheck(frame)
  os.umask(0o077);root.mkdir(mode=0o700);fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);identity=os.fstat(fd)
  def same_root():
   s=root.lstat();held=os.fstat(fd);assert stat.S_ISDIR(s.st_mode)and not root.is_symlink()and stat.S_IMODE(s.st_mode)==0o700 and(s.st_dev,s.st_ino)==(identity.st_dev,identity.st_ino)==(held.st_dev,held.st_ino)
  generated={}
  def write(name,data):
   same_root();path=root/name;io.destination(path,root);path.parent.mkdir(parents=True,exist_ok=True)
   with path.open('xb')as out:out.write(data);out.flush();os.fsync(out.fileno())
   d=dict(path=str(path),sha256=io.digest(data),bytes=len(data));g.checked(d);same_root();generated[name]=d;return d
  meta=frame['metadata'];build=Path(meta['cmakeCachePath']).parent;ninja=frame['refs']['ninja'];g.checked(ninja)
  argv=[ninja['path'],'-C',str(build),'-t','commands','builtin_componentize_embedding'];status=None;stdout=b'';stderr=b'';timed_out=False
  try:
   completed=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120,check=False);status=completed.returncode;stdout=completed.stdout;stderr=completed.stderr
  except subprocess.TimeoutExpired as error:
   timed_out=True;stdout=error.stdout or b'';stderr=error.stderr or b''
  finally:
   write('normal-off-embedding.after.stdout.txt',stdout);write('normal-off-embedding.after.stderr.txt',stderr)
   write('normal-off-embedding.after.terminal.json',(json.dumps(dict(schemaVersion=1,argv=argv,rawExitCode=status,timedOut=timed_out,capturedStreamsComplete=not timed_out,postBuildOnly=True,compilerExecutedByThisCommand=False,engineExecuted=False),indent=2)+'\n').encode())
  assert status==0 and not timed_out and len(stdout)<=4*1024*1024 and len(stderr)<=4*1024*1024,'Full available command streams retained; no clipping or timeout acceptance'
  external=frame['refs']['externalSourceRoot'];embedding=io.embedding_command(stdout,external+'/embedding/embedding.cpp');assert embedding==meta['actualEmbeddingCompileCommands']
  frame['layer'].validate_classic_compilation(frame['database'],embedding,g.SOURCE,meta)
  cpp={r['path']for r in meta['sourceManifest']if r['path'].endswith('.cpp')and r['path'].startswith(('builtins/','runtime/'))};assert len(cpp)==61
  for r in frame['database']:
   names=[p for p in cpp if r['file']==str(g.SOURCE/p)]
   if names:io.compile_command(r['command'],False,names[0],True,False)
  io.compile_command(embedding[0],False,'embedding/embedding.cpp',True,False)
  # Only after the full raw metadata/source/cache/command gates touch engine bytes.
  g.checked(frame['refs']['engine']);frame['captured'].append(frame['refs']['engine'])
  with Path(frame['refs']['engine']['path']).open('rb')as wasm:assert wasm.read(8)==b'\0asm\x01\0\0\0'
  planned=[];origins={};destinations=set()
  def add(row,name,role):
   g.checked(row);assert name and not name.startswith('/')and '\\'not in name and all(p not in('','.','..')for p in name.split('/'))and name not in destinations;destinations.add(name)
   planned.append(dict(original=Path(row['path']),target=root/name,sha256=row['sha256'],shared=False));origins[name]=dict(source=row,role=role)
  for r in plan_data['copies']:add(r['source'],r['destination'],r['role'])
  for r in frame['ownRows']:add(r,'artifact-tools/source/'+str(Path(r['path']).relative_to(OWN)),'new-freezer-source-capsule')
  peer=frame['root']['sourceIndependentReview']
  for r in g.family(peer['index']):add(r,'artifact-tools/source-review/'+str(Path(r['path']).relative_to(Path(peer['index']['path']).parent)),'new-freezer-source-review')
  add(config_row,'provenance/freeze-config.json','new-freeze-config');add(frame['config']['rootAuthority'],'provenance/freeze-root-authority.json','new-freeze-authority')
  receipt_path=root/'normal-off-freeze-receipt.json';same_root();g.recheck(frame);io.validate_plan(planned,receipt_path,root);io.execute_plan(planned,root);same_root();g.recheck(frame)
  copies=[]
  for name,entry in origins.items():
   path=root/name;s=path.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600
   assert(s.st_dev,s.st_ino)!=(Path(entry['source']['path']).stat().st_dev,Path(entry['source']['path']).stat().st_ino)
   copies.append(dict(path=str(path),sha256=entry['source']['sha256'],bytes=entry['source']['bytes'],original=entry['source'],role=entry['role']))
  for name,d in generated.items():copies.append(dict(d,original=None,role='fresh-post-build-Ninja-output'))
  receipt=dict(schemaVersion=1,state='SCHEDULER_RESOURCE342_NORMAL_OFF_NATIVE_FREEZE_COMPLETE_UNREVIEWED_V1',variant='normal-off',resourceSourceIndexSha256=g.SOURCE_SHA,freezerSourceIndexSha256=frame['config']['freezerIndex']['sha256'],rootAuthority=frame['config']['rootAuthority'],configuredSourceRoot=str(g.SOURCE),sourceRoot=str(root/'source'),componentizeSourceRoot=str(root/'componentize-source'),engine=dict(frame['refs']['engine'],path=str(root/'normal-off.engine.wasm')),metadata=dict(frame['refs']['metadata'],path=str(root/'normal-off.engine.wasm.build.json')),rawMetadataBytesUnchanged=True,rawMetadataOriginalConfiguredPathsPreserved=True,nativeInputsVerified=342,externalEmbeddingInputsVerified=3,selectedManifestCount=9,compileDatabaseRows=67,policyCppCommands=61,otherConfiguredSourceRows=5,generatedNullCppRows=1,embeddingRowsInCompileDatabase=0,separatePostBuildEmbeddingCommands=1,actualStrictCommands=4,actualPrivateClassicCommands=5,postBuildEmbeddingEvidence=dict(stdout=generated['normal-off-embedding.after.stdout.txt'],stderr=generated['normal-off-embedding.after.stderr.txt'],terminal=generated['normal-off-embedding.after.terminal.json'],sourcePath=external+'/embedding/embedding.cpp',commands=embedding,beforeBuildCaptureExists=False),staticLibrariesPhysicallyCopied=29,copies=copies,verifiedBuildReferenceLedger=frame['refs']['buildInputLedger'],verifiedOriginalReferenceCount=plan_data['verifiedReferenceCount'],verifiedReferencesNotAllCopied=True,verifiedSdkAliases=frame['refs']['sdkAliases'],sdkAliasesNotCopiedAsLinks=True,allInputsValidatedBeforeCopies=True,allCopiesAndOriginalsRehashed=True,receiptRequiresExternalParentZeroAndIndependentReview=True,resourceNativeRuntimeValidation=None,gcReconfigureAllowed=False,reviewedEnginePins=None,engineExecuted=False,bootstrapExecuted=False,componentOrGuestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
  write('normal-off-freeze-receipt.json',(json.dumps(receipt,indent=2)+'\n').encode());same_root()
  spec=importlib.util.spec_from_file_location('resource342_frozen_read_only_verifier',OWN/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);result=v.verify_frozen(g.descriptor(generated['normal-off-freeze-receipt.json']))
  same_root();g.recheck(frame);return result
 finally:
  try:g.recheck(frame)
  finally:
   if fd is not None:os.close(fd)
if __name__=='__main__':assert len(sys.argv)==2;print(json.dumps(freeze(json.loads(sys.argv[1]))),flush=True)
