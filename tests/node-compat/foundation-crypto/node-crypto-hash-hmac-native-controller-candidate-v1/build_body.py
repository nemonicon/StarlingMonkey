"""Dormant experimental357 COPY build using genuine original f751 lifecycle."""
from pathlib import Path
import hashlib,importlib.util,os,stat,time
START_FREE=2147483648
STOP_FREE=838860800

def load(row,name,io):
 spec=importlib.util.spec_from_file_location(name,io.checked(row));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def build_environment(parent,refs):
 prefixes=('NODE_COMPAT_','NODE_CRYPTO_','CMAKE_','CARGO_','RUST','CCACHE_','SCCACHE_','CPM_','FETCHCONTENT_','NAPI_RS_','WASMTIME_','DYLD_','GIT_','BASH_FUNC_')
 names={'NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','BASH_ENV','ENV','SHELLOPTS','BASHOPTS','CDPATH','GLOBIGNORE','LD_PRELOAD','LD_LIBRARY_PATH','CC','CXX','CPP','CFLAGS','CXXFLAGS','CPPFLAGS','LDFLAGS','AR','LD','RANLIB','CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','LIBRARY_PATH','COMPILER_PATH','GCC_EXEC_PREFIX','CONFIG_SITE'}
 env={k:v for k,v in parent.items()if not k.startswith(prefixes)and k not in names};env.update(refs['buildEnvironment'])
 for key in ['HOME','home','CODEX_HOME']:assert(key in env)==(key in parent)and env.get(key)==parent.get(key)
 assert env['NODE_COMPAT_CRYPTO_HASH_HMAC']=='1'and env['NODE_CRYPTO_AUDITED_BORROW']=='0'and env['CARGO_INCREMENTAL']=='0'and env['RUSTUP_TOOLCHAIN']=='1.88.0'
 assert env['RUSTUP_HOME']==refs['workRoot']+'/rustup-home'and env['CARGO_HOME']==refs['workRoot']+'/cargo-home'
 return env

def stream_copy(source,target):
 h=hashlib.sha256();size=0
 while True:
  block=source.read(1048576)
  if not block:break
  assert type(block)is bytes and target.write(block)==len(block);h.update(block);size+=len(block)
 return dict(sha256=h.hexdigest(),bytes=size)

def populate_cache(plan,result,work,output,io):
 io.absent(work);work.mkdir(mode=0o700)
 for r in plan['copies']:
  original=io.checked(r['source']);a=original.stat();assert stat.S_IMODE(a.st_mode)==r['sourceMode']
  name=io.confined(r['target']);target=work/name;target.parent.mkdir(parents=True,exist_ok=True)
  for p in(target,*target.parents):assert not p.is_symlink()
  fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,r['outputMode'])
  try:
   with original.open('rb')as src,os.fdopen(fd,'wb',closefd=False)as dst:
    actual=stream_copy(src,dst);dst.flush();os.fsync(fd)
  finally:os.close(fd)
  assert actual=={k:r['source'][k]for k in ['sha256','bytes']};d=io.row(target);b=target.stat()
  assert(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)and b.st_nlink==1 and stat.S_IMODE(b.st_mode)==r['outputMode']
  record=dict(source=r['source'],target=d,sourceMode=r['sourceMode'],outputMode=r['outputMode'],distinctInode=True);result['cacheCopiesCompleted'].append(record);io.write(output/('cache-copy-'+str(len(result['cacheCopiesCompleted']))+'.json'),record)
 for name in ['rustup-home','cargo-home']:(work/name).mkdir(mode=0o700)
 io.fsync_dir(work)

def run(frame,recheck):
 io=frame['io'];refs=frame['refs'];work=Path(refs['workRoot']);out=Path(refs['buildOutputRoot'])
 for p in [work,out,Path(refs['freezeRoot'])]:io.absent(p)
 lifecycle=load(refs['lifecycleEntry'],'original_f751_hash_hmac357_build_lifecycle',io)
 assert lifecycle.REQUIRED_START_FREE==START_FREE and lifecycle.MINIMUM_FREE==STOP_FREE
 recheck(frame);os.umask(0o077)
 def free():
  s=os.statvfs(work if work.exists()else work.parent);return s.f_bavail*s.f_frsize
 before=lifecycle.prepare_output(out,free)
 command=[refs['bash']['path'],str(io.checked(refs['recipe']))]
 result=dict(schemaVersion=1,state='NODE_CRYPTO_HASH_HMAC357_NATIVE_BUILD_STARTED_V1',sourceIndexSha256=refs['integrationSourceIndex']['sha256'],controllerIndex=frame['ownIndex'],rootAuthority=frame['config']['rootAuthority'],actualStageReview=refs['actualStageReview'],configuredSourceRoot=refs['configuredSourceRoot'],workRoot=str(work),freezeRoot=refs['freezeRoot'],command=command,explicitEnvironment=refs['buildEnvironment'],cacheCopiesCompleted=[],freeBytesBefore=before,requiredStartFreeBytes=START_FREE,stopBelowFreeBytes=STOP_FREE,diskSpaceSampleSeconds=1,diskFreeSamplesDuringBuildCommand=[],diskFloorChecksDuringCacheCopies='before and after four immutable cache copies; not during each copy',externalParentDeadlineSeconds=7200,parallelBuilds=1,rawChildExitCode=None,engineExecuted=False,guestExecuted=False,cryptoOperationsInvoked=False,liveEvpSnapshotAdmission=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
 io.write(out/'launch.json',result);started=time.monotonic()
 try:
  assert free()>=START_FREE;populate_cache(io.read(refs['cachePlan']),result,work,out,io);assert free()>=START_FREE
  env=build_environment(os.environ,refs)
  def build_free():
   observed=free();result['diskFreeSamplesDuringBuildCommand'].append(dict(monotonicSeconds=time.monotonic(),freeBytes=observed));return observed
  with(out/'build.log').open('xb')as log:
   result.update(lifecycle.monitor_owned_command(command,refs['configuredSourceRoot'],env,log,build_free));log.flush();os.fsync(log.fileno())
  cleanup=result.get('ownedGroupCleanup')or{}
  if cleanup.get('complete')is not True or cleanup.get('events')or cleanup.get('errors'):result.setdefault('finalObservationErrors',[]).append(dict(stage='inner-group-cleanliness',cleanup=cleanup))
  if result.get('rawChildExitCode')==0:
   # This API reads the new raw83 sidecar and real current commands. No engine run.
   module=frame['loadOwn']('admission.py');observed=module.admit(frame,recheck)
   result.update(engine=io.row(Path(refs['enginePath'])),metadata=io.row(Path(refs['enginePath']+'.build.json')),metadataShape=observed['metadataClassifier'],sourceAdmission=observed)
 except BaseException as error:result.setdefault('launcherErrors',[]).append(lifecycle.error_record('build-cache-or-metadata',error))
 finally:
  result['wallSecondsForOperationalRecordOnly']=time.monotonic()-started
  try:
   result['freeBytesAfter']=free()
   if(out/'build.log').exists():result['buildLog']=io.row(out/'build.log')
  except BaseException as error:result.setdefault('finalObservationErrors',[]).append(lifecycle.error_record('final-log-or-disk',error))
  try:recheck(frame);result['allSourceStageOriginalAndCacheInputsPreserved']=True
  except BaseException as error:result.setdefault('finalObservationErrors',[]).append(lifecycle.error_record('final-protection',error))
  lifecycle.finalize_status(result);lifecycle.publish_result(out,result,writer=io.write)
 assert result['launcherExitCode']==0;return result
