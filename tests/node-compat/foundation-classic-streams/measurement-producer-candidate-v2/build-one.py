"""One-job diagnostic launcher; no import-time build. Root calls main separately."""
import sys
sys.dont_write_bytecode=True
import json,os,time,importlib.util
from pathlib import Path
from benchmark_common import HERE,REPO,RECIPE,LABELS,OUTPUT,checked,tool_dependencies,capture_addons,layer,sha,require_source_root,verify_frozen
_spec=importlib.util.spec_from_file_location('benchmark_parent_launcher_lifecycle',HERE/'ancestry/build-one.py')
_parent=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_parent)
prepare_output=_parent.prepare_output
monitor_owned_command=_parent.monitor_owned_command
publish_result=_parent.publish_result
finalize_status=_parent.finalize_status
error_record=_parent.error_record

def main():
    assert __debug__ and len(sys.argv)==4,'LABEL EXPECTED_PACKET_INDEX_SHA256 EXPLICIT_SOURCE_ROOT'
    label,index_sha,source_root=sys.argv[1:];assert label in LABELS
    from importlib.util import spec_from_file_location,module_from_spec
    spec=spec_from_file_location('benchmark_verified_packet',HERE/'verify-packet.py');module=module_from_spec(spec);spec.loader.exec_module(module);module.verify(index_sha)
    recipe=checked(HERE/'build-classic-benchmark-engine.sh',RECIPE)
    require_source_root(source_root)
    layer().validate_sources(REPO);capture_addons();tool_dependencies(REPO)
    if label=='benchmark-classic-off':verify_frozen('benchmark-classic-on') # Freeze the first variant before reconfiguration.
    work=Path('/tmp/starling-node-compat/classic-benchmark-trace-v2-build')
    output=OUTPUT.parent/'builds'/label
    environment={'NODE_COMPAT_NODE':'/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',
      'NODE_COMPAT_JOBS':'1','BINARYEN_CORES':'1','RAYON_NUM_THREADS':'1','CARGO_BUILD_JOBS':'1',
      'NODE_COMPAT_BUILD_TYPE':'Release','NODE_COMPAT_GC_STRESS':'0','NODE_COMPAT_OOM_TESTING':'0','NODE_COMPAT_BUILD_ROOT':str(work),
      'NODE_COMPAT_ABI_FIX':'1','NODE_COMPAT_BIGINT_FIX':'1','NODE_COMPAT_INTERNAL_TICKS':'1','NODE_COMPAT_ENTROPY_MODE':'OFF',
      'NODE_COMPAT_CLASSIC_STREAMS':'1'if label=='benchmark-classic-on'else'0','NODE_COMPAT_ARTIFACT_TAG':'',
      **{'NODE_COMPAT_'+name:'1'for name in ('PATH','EVENTS','STRING_DECODER','ASSERT','QUERYSTRING','UTIL','STREAM_WEB')}}
    free=lambda:os.statvfs(work if work.exists()else work.parent).f_bavail*os.statvfs(work if work.exists()else work.parent).f_frsize
    try:free_before=prepare_output(output,free)
    except BaseException as error:
        print(json.dumps({'state':'not-launched','error':error_record('precondition',error)}),flush=True);return 1
    result={'schemaVersion':1,'state':'diagnostic-build-not-started','label':label,'command':['bash',str(recipe),index_sha,str(REPO)],
      'recipeSha256':RECIPE,'sourceIndexSha256':index_sha,'explicitEnvironment':environment,'requiredStartFreeBytes':2147483648,
      'stopBelowFreeBytes':838860800,'freeBytesBefore':free_before,'guestExecutionRequested':False,'parallelBuilds':1,'rawChildExitCode':None}
    started=time.monotonic()
    try:
        with(output/'launch.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
        with(output/'build.log').open('xb')as log:
            child={key:value for key,value in os.environ.items()if not key.startswith(('NODE_COMPAT_','CMAKE_PROJECT_'))and key!='NODE_OPTIONS'};child.update(environment)
            result.update(monitor_owned_command(result['command'],REPO,child,log,free))
    except BaseException as error:result.setdefault('launcherErrors',[]).append(error_record('launch-record-or-log',error))
    result['wallSecondsOperationalOnly']=time.monotonic()-started
    try:result['freeBytesAfter']=free();result['logSha256']=sha(output/'build.log')
    except BaseException as error:result.setdefault('finalObservationErrors',[]).append(error_record('final-observation',error))
    finalize_status(result);publish_result(output,result);return result['launcherExitCode']
if __name__=='__main__':sys.exit(main())
