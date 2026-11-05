"""Dormant normal-OFF build body. No build/helper action occurs at import."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys,time
OWN=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/resource-build-controller-candidate-v1')
def initial(row):
    p=Path(row['path']);assert p.is_absolute()and '..'not in p.parts
    for x in(p,*p.parents):assert not x.is_symlink()
    a=p.stat();assert p.is_file();raw=p.read_bytes();b=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns)
    assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'];return raw
def build(config_row):
    assert __debug__ and sys.dont_write_bytecode
    config=json.loads(initial(config_row));ix=config['controllerIndex'];assert ix['path']==str(OWN/'index.json')
    index=json.loads(initial(ix));names=set()
    for r in index['files']:
        n=r['path'];assert n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/'))and n not in names;names.add(n);initial(dict(path=str(OWN/n),sha256=r['sha256'],bytes=r['bytes']))
    assert not any(p.is_symlink()for p in OWN.rglob('*'))
    assert{p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}==names|{'index.json'}
    spec=importlib.util.spec_from_file_location('scheduler_resource_normal_build_guard',OWN/'guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    frame=guard.authorize(config_row)
    try:
        assert not guard.WORK.exists()and not guard.WORK.is_symlink()and not guard.BUILD_OUTPUT.exists()and not guard.BUILD_OUTPUT.is_symlink()
        helper=next(r for r in frame['ownRows']if r['path']==str(OWN/'lifecycle.py'));guard.checked(helper)
        spec=importlib.util.spec_from_file_location('scheduler_resource_owned_build_lifecycle',OWN/'lifecycle.py');lifecycle=importlib.util.module_from_spec(spec);spec.loader.exec_module(lifecycle)
        guard.recheck(frame['captured'],frame['families']);assert lifecycle.REQUIRED_START_FREE==2147483648 and lifecycle.MINIMUM_FREE==838860800
        os.umask(0o077)
        free=lambda:os.statvfs(guard.WORK if guard.WORK.exists()else guard.WORK.parent).f_bavail*os.statvfs(guard.WORK if guard.WORK.exists()else guard.WORK.parent).f_frsize
        before=lifecycle.prepare_output(guard.BUILD_OUTPUT,free)
        plan=guard.read(next(r for r in frame['sourceRows']if r['path']==str(guard.PROPOSAL/'build-plan.json')))
        environment=dict(plan['explicitEnvironment']);environment.update(frame['refs']['normalEnvironmentExtra'])
        assert environment['NODE_COMPAT_BUILD_ROOT']==str(guard.WORK)and environment['NODE_COMPAT_GC_STRESS']=='0'and environment['NODE_COMPAT_ENTROPY_MODE']=='OFF'
        assert all(environment[n]=='1'for n in('NODE_COMPAT_JOBS','BINARYEN_CORES','RAYON_NUM_THREADS','CARGO_BUILD_JOBS'))
        child_env={k:v for k,v in os.environ.items()if not k.startswith(('NODE_COMPAT_','CMAKE_PROJECT_','NAPI_RS_','WASMTIME_'))and k not in('NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH')};child_env.update(environment)
        command=['bash',str(guard.SOURCE/'tests/node-compat/build-engine.sh')]
        result=dict(schemaVersion=1,state='RESOURCE342_NORMAL_OFF_NATIVE_BUILD_STARTED',variant='normal-off',resourceSourceIndexSha256=guard.SOURCE_SHA,controllerIndex=config['controllerIndex'],rootAuthority=config['rootAuthority'],command=command,configuredSourceRoot=str(guard.SOURCE),workRoot=str(guard.WORK),explicitEnvironment=environment,freeBytesBefore=before,requiredStartFreeBytes=lifecycle.REQUIRED_START_FREE,stopBelowFreeBytes=lifecycle.MINIMUM_FREE,parallelBuilds=1,rawChildExitCode=None,externalParentDeadlineSeconds=7200,gcReconfigureAllowed=False,normalOffFreezeStillRequired=True,guestExecutionRequested=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
        def write(path,value):
            with path.open('x')as out:json.dump(value,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
        write(guard.BUILD_OUTPUT/'launch.json',result);started=time.monotonic()
        try:
            with(guard.BUILD_OUTPUT/'build.log').open('xb')as log:
                result.update(lifecycle.monitor_owned_command(command,str(guard.SOURCE),child_env,log,free));log.flush();os.fsync(log.fileno())
        except BaseException as error:result.setdefault('launcherErrors',[]).append(lifecycle.error_record('launch-or-monitor',error))
        result['wallSecondsForOperationalRecordOnly']=time.monotonic()-started
        try:result['freeBytesAfter']=free();result['logSha256']=lifecycle.digest(guard.BUILD_OUTPUT/'build.log')
        except BaseException as error:result.setdefault('finalObservationErrors',[]).append(lifecycle.error_record('final-file-or-disk-observation',error))
        try:guard.recheck(frame['captured'],frame['families']);result['allSourceStageAndProofBytesPreserved']=True
        except BaseException as error:result.setdefault('finalObservationErrors',[]).append(lifecycle.error_record('final-source-stage-proof-recheck',error))
        lifecycle.finalize_status(result);lifecycle.publish_result(guard.BUILD_OUTPUT,result,writer=write)
        assert result['launcherExitCode']==0;return result
    finally:guard.recheck(frame['captured'],frame['families'])
if __name__=='__main__':assert len(sys.argv)==2;build(json.loads(sys.argv[1]))
