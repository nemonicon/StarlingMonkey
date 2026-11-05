"""Future isolated native build using unchanged recipe and owned donor lifecycle."""
from pathlib import Path
import importlib.util,json,os,sys,time
import context as C,guard
from data_io import read,write
def build(config):
    frame=guard.authorize(config,'build');root=frame['root'];work=Path(C.WORK);output=Path(C.BUILD_OUTPUT)
    assert not work.exists()and not output.exists()
    path=Path(C.TOOLS)/'build-one.py';spec=importlib.util.spec_from_file_location('gc_owned_build_lifecycle',path);lifecycle=importlib.util.module_from_spec(spec);spec.loader.exec_module(lifecycle)
    # main() is deliberately not called: its literal normal work/output paths
    # cannot isolate GC. Reuse the genuine explicit-argument lifecycle functions.
    environment=dict(frame['references']['normalBuildEnvironment']);environment.update(NODE_COMPAT_BUILD_ROOT=C.WORK,NODE_COMPAT_GC_STRESS='1',NODE_COMPAT_ARTIFACT_TAG='ko355gc1')
    free=lambda:os.statvfs(work if work.exists()else work.parent).f_bavail*os.statvfs(work if work.exists()else work.parent).f_frsize
    before=lifecycle.prepare_output(output,free);command=['bash',C.SOURCE+'/tests/node-compat/build-engine.sh']
    child_env={k:v for k,v in os.environ.items()if not k.startswith(('NODE_COMPAT_','CMAKE_PROJECT_','NAPI_RS_','WASMTIME_'))and k not in ('NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH')};child_env.update(environment)
    result=dict(schemaVersion=1,state='GC_NATIVE_BUILD_STARTED',sourceIndexSha256=frame['sourceIndex']['sha256'],rootAuthority=frame['rootAuthority'],command=command,explicitEnvironment=environment,configuredSourceRoot=C.SOURCE,workRoot=C.WORK,freeBytesBefore=before,requiredStartFreeBytes=lifecycle.REQUIRED_START_FREE,stopBelowFreeBytes=lifecycle.MINIMUM_FREE,parallelBuilds=1,rawChildExitCode=None,guestExecutionRequested=False,externalParentDeadlineSeconds=root['externalParentDeadlineSeconds'])
    assert root['externalParentDeadlineSeconds']==7200
    write(output/'launch.json',result);started=time.monotonic()
    try:
        with(output/'build.log').open('xb')as log:result.update(lifecycle.monitor_owned_command(command,C.SOURCE,child_env,log,free));log.flush();os.fsync(log.fileno())
    except BaseException as error:result.setdefault('launcherErrors',[]).append(lifecycle.error_record('launch-or-monitor',error))
    result['wallSecondsForOperationalRecordOnly']=time.monotonic()-started
    result['logSha256']=lifecycle.digest(output/'build.log')
    try:guard.recheck(frame);result['allOriginalNormalAndStageBytesPreserved']=True
    except BaseException as error:result.setdefault('finalObservationErrors',[]).append(lifecycle.error_record('normal-stage-source-recheck',error))
    lifecycle.finalize_status(result);lifecycle.publish_result(output,result,writer=lambda path,value:write(path,value))
    assert result['launcherExitCode']==0;return result
if __name__=='__main__':assert len(sys.argv)==2;build(json.loads(sys.argv[1]))
