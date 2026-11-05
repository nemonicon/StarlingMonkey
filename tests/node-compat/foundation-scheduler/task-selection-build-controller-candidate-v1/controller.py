"""Dormant selector342 normal-OFF parent/worker. Standard-library bootstrap only."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys,time

REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/task-selection-build-controller-candidate-v1'
PROPOSAL=REPO/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1'
SOURCE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source')
WORK=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-build')
FREEZE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze')
OUTPUT=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-root')
EXTERNAL=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-external-root')
SOURCE_SHA='88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1'
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'
ARTIFACT='starlingmonkey_embedding.abi-i32-i64-v1.resource-selection-v1.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.selectionv1.wasm'


def checked(row):
    assert type(row)is dict and set(row)=={'path','sha256','bytes'}
    assert type(row['path'])is str and type(row['bytes'])is int and row['bytes']>=0
    assert type(row['sha256'])is str and len(row['sha256'])==64 and all(c in '0123456789abcdef'for c in row['sha256'])
    path=Path(row['path']);assert path.is_absolute()and '..'not in path.parts
    physical=Path('/private'+str(path))if str(path).startswith('/tmp/')else path
    for p in (physical,*physical.parents):assert not p.is_symlink()
    a=physical.stat();assert stat.S_ISREG(a.st_mode);digest=hashlib.sha256()
    with physical.open('rb')as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):digest.update(block)
    b=physical.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns)
    assert a.st_size==row['bytes']and digest.hexdigest()==row['sha256'];return path


def read(row):
    assert row['bytes']<=32*1024*1024
    raw=checked(row).read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)


def family(row):
    index=read(row);root=Path(row['path']).parent;rows=[row];names=set()
    assert index['schemaVersion']==1 and type(index['files'])is list and 0<len(index['files'])<=2048
    for item in index['files']:
        n=item['path'];assert n and not n.startswith('/')and '\\'not in n and all(x not in('','.','..')for x in n.split('/'))and n not in names;names.add(n)
        r=dict(path=str(root/n),sha256=item['sha256'],bytes=item['bytes']);checked(r);rows.append(r)
    assert not any(p.is_symlink()for p in root.rglob('*'))
    assert{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{'index.json'}
    return rows


def descriptor(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    r=dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size);checked(r);return r


def validate_root(root,index,refs):
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_BUILD_V1'
    assert root['phase']=='build'and root['variant']=='normal-off'and root['sourceIndexSha256']==SOURCE_SHA
    assert root['buildAllowed']is True and root['gcStress']is False and root['entropyMode']=='OFF'
    assert root['configuredSourceRoot']==str(SOURCE)and root['workRoot']==str(WORK)and root['freezeRoot']==str(FREEZE)
    assert root['buildOutputRoot']==str(OUTPUT)and root['externalOutputRoot']==str(EXTERNAL)
    assert root['nativeSourceFiles']==342 and root['unchangedResourceParentFiles']==339 and root['nativeReplacements']==3 and root['externalEmbeddingSources']==3 and root['webTimersEnabled']is True
    assert root['externalParentDeadlineSeconds']==7200 and root['jobs']==1 and root['buildType']=='Release'and root['oomTesting']is False
    assert root['requiredStartFreeBytes']==2147483648 and root['stopBelowFreeBytes']==838860800
    assert root['controllerIndex']==index and index['path']==str(OWN/'index.json')and root['controllerEntry']['path']==str(OWN/'controller.py')
    assert root['sourceIndependentReview']==refs['sourceReview']and root['independentStageReview']==refs['actualStageReview']and root['stageContract']==refs['actualStageContract']
    assert root['actualJournal']==refs['actualJournal']and root['stageRootObservation']==refs['stageRootObservation']
    for key in['stageAllowed','gcReconfigureAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','componentAllowed','guestAllowed','engineExecutionAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']:assert root[key]is False
    for key in['actualBuildResult','engine','metadata','actualNormalFreeze','independentNormalFreezeReview','runtimeAction']:assert root[key]is None


def validate_stage(proof,contract,refs):
    assert proof['schemaVersion']==1 and proof['state']=='INDEPENDENT_SCHEDULER_TASK_SELECTION342_SOURCE_STAGE_REVIEW_PASSED_V1'and proof['verifiedPassed']is True
    assert proof['sourceIndexSha256']==SOURCE_SHA and proof['controllerSourceIndexSha256']=='959b3e73111f9f2286d026efc70ef671b2f037321ae159e1cb10f281ab3bfb46'
    assert proof['nativeSourceFiles']==342 and proof['unchangedResourceParentNativeFiles']==339 and proof['nativeReplacements']==3 and proof['configuredSourceRoot']==str(SOURCE)
    assert proof['actualControllerExitCode']==proof['actualStageExitCode']==0 and proof['allObservedOwnedGroupsGone']is True
    assert contract['requiredReviewState']==proof['state']and proof['coverage']==contract['requiredCoverage']
    for k,v in contract['requiredFixedValues'].items():assert proof[k]==v
    for k,v in contract['requiredExactDescriptors'].items():assert proof[k]==v
    for k,name in [('actualJournal','actualJournal'),('rootObservation','stageRootObservation'),('outerTerminal','stageOuterTerminal'),('innerTerminal','stageInnerTerminal'),('rootAuthority','stageRootAuthority'),('rootConfig','stageRootConfig'),('stageObservation','stageObservation')]:assert proof[k]==refs[name]
    for k in['buildExecuted','engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim','grantsActionAuthority']:assert proof[k]is False


def validate_peer(peer,index):
    assert peer['schemaVersion']==1 and peer['state']=='INDEPENDENT_SCHEDULER_TASK_SELECTION342_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert peer['controllerSourceIndexSha256']==index['sha256']and peer['taskSelectionSourceIndexSha256']==SOURCE_SHA
    assert peer['sourceOnly']is True and peer['sourceReviewPassed']is True
    for k in['ownerActionsInvoked','hostActionsInvoked','nativeBuildActionsInvoked']:assert peer[k]is False


def proof(pair):
    rows=family(pair['index']);assert pair['result']in rows;return read(pair['result']),rows


def protect_resource(refs):
    receipt=read(refs['resourceFreezeReceipt']);assert receipt['nativeInputsVerified']==342 and len(receipt['copies'])==666
    captured=[refs['resourceFreezeReceipt']];originals=0
    for r in receipt['copies']:
        p=checked({k:r[k]for k in['path','sha256','bytes']});assert stat.S_IMODE(p.stat().st_mode)==0o600
        captured.append({k:r[k]for k in['path','sha256','bytes']})
        if r['original']is not None:checked(r['original']);captured.append(r['original']);originals+=1
    assert originals==663
    frozen=Path(refs['resourceFreezeReceipt']['path']).parent
    assert not any(p.is_symlink()for p in frozen.rglob('*'))
    assert{str(p.relative_to(frozen))for p in frozen.rglob('*')if p.is_file()}=={str(Path(r['path']).relative_to(frozen))for r in receipt['copies']}|{'normal-off-freeze-receipt.json'}
    stage=read(refs['resourceStage']);assert len(stage['copies'])==501;captured.append(refs['resourceStage'])
    for r in stage['copies']:
        a=r['original'];b=dict(a,path=r['path']);checked(a);checked(b);captured.extend([a,b])
    return captured


def recheck(frame):
    for row in frame['captured']:checked(row)
    for index in frame['families']:family(index)
    protect_resource(frame['refs'])
    for row in frame['copyRows']:
        a=checked(row['original']);b=checked(row['target'])
        assert stat.S_IMODE(a.stat().st_mode)==stat.S_IMODE(b.stat().st_mode)==row['mode']
        assert(a.stat().st_dev,a.stat().st_ino)!=(b.stat().st_dev,b.stat().st_ino)
    assert(SOURCE/'.git/HEAD').read_text()==BASE+'\n'and not(SOURCE/'.git/objects/info/alternates').exists()
    assert not(SOURCE/'.git/commondir').exists()and not FREEZE.exists()and not FREEZE.is_symlink()


def authorize(config_row):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    assert not any(os.environ.get(k)for k in['PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH'])
    config=read(config_row);assert config['schemaVersion']==1
    index=config['controllerIndex'];assert index['path']==str(OWN/'index.json')
    own=family(index);refs=read(next(r for r in own if r['path']==str(OWN/'references.json')))
    root=read(config['rootAuthority']);validate_root(root,index,refs);assert root['controllerEntry']in own and config['sourceIndex']==refs['sourceIndex']
    source=family(config['sourceIndex']);captured=[config_row,config['rootAuthority'],*own,*source];indices=[index,config['sourceIndex']]
    for f in refs['families']:captured+=family(f['index']);indices.append(f['index'])
    source_peer,rows=proof(refs['sourceReview']);captured+=rows
    assert source_peer['state']=='INDEPENDENT_SCHEDULER_TASK_SELECTION_INTEGRATION_SOURCE_REVIEW_PASSED_V1'and source_peer['sourceIndexSha256']==SOURCE_SHA and source_peer['sourceOnly']is True and source_peer['sourceReviewPassed']is True and source_peer['ownerActionsInvoked']is False
    stage_peer,rows=proof(refs['actualStageReview']);captured+=rows
    assert refs['actualStageContract']in rows and refs['actualStageInputLedger']in rows
    validate_stage(stage_peer,read(refs['actualStageContract']),refs)
    ledger=read(refs['actualStageInputLedger']);assert len(ledger['files'])==2570
    for r in ledger['files']:checked(r);captured.append(r)
    for name in['actualJournal','stageRootObservation','stageOuterTerminal','stageInnerTerminal','stageRootAuthority','stageRootConfig','stageObservation','resourceFreezeReceipt','resourceStage','monitorEntry','lifecycleEntry','node']:
        checked(refs[name]);captured.append(refs[name])
    baseline=read(next(r for r in source if r['path']==str(PROPOSAL/'baseline-pins.json')))
    for ix in baseline['families'].values():captured+=family(ix);indices.append(ix)
    preparation=read(next(r for r in source if r['path']==str(PROPOSAL/'input-freeze.json')));assert len(preparation['files'])==540
    for r in preparation['files']:checked(r);captured.append(r)
    plan=read(next(r for r in source if r['path']==str(PROPOSAL/'stage-inputs.json')));targets={r['target']:r['original']for r in plan['files']};assert len(targets)==len(plan['files'])==533
    for r in source:targets[str(PROPOSAL.relative_to(REPO))+'/'+str(Path(r['path']).relative_to(PROPOSAL))]=r
    for c in plan['nativeAfterimageReplacements']:targets[c['path']]=next(r for r in source if r['path']==str(PROPOSAL/'native'/c['path']))
    targets['tests/node-compat/build-engine.sh']=next(r for r in source if r['path']==str(PROPOSAL/'proposed/tests/node-compat/build-engine.sh'))
    journal=read(refs['actualJournal']);observation=read(refs['stageObservation']);assert len(targets)==566
    assert journal['copies']==[dict(path=str(SOURCE/n),original=r)for n,r in sorted(targets.items())]
    assert journal['sourceIndex']==config['sourceIndex']and journal['nativeFiles']==342 and journal['nativeReplacements']==3 and journal['buildOrGuestInvoked']is False
    assert len(observation['targetObservations'])==566 and observation['stageSuccessful']is True and observation['finalProtectionRecheckPassed']is True
    observed={r['path']:r for r in observation['targetObservations']};copy_rows=[]
    for name,original in sorted(targets.items()):
        target=dict(original,path=str(SOURCE/name));checked(original);checked(target);captured.extend([original,target]);o=observed[target['path']]
        assert o['expected']==original and o['status']=='match'and o['distinctInode']is True and o['expectedMode']==o['mode']
        copy_rows.append(dict(original=original,target=target,mode=o['mode']))
    policy=read(next(r for r in source if r['path']==str(PROPOSAL/'policy.json')));assert len(policy['expectedNativeSourceManifest'])==342
    for r in policy['expectedNativeSourceManifest']:
        p=SOURCE/r['path'];row=dict(path=str(p),sha256=r['sha256'],bytes=p.stat().st_size);checked(row);captured.append(row)
    assert policy['taskSelectionSourcePolicy']['requiresFullNativeRebuild']is True and policy['taskSelectionSourcePolicy']['compatibleWithParentEngineAbi']is False
    model=next(r for r in source if r['path']==str(PROPOSAL/'native-admission-model.py'));configured_model=dict(model,path=str(SOURCE/PROPOSAL.relative_to(REPO)/'native-admission-model.py'));checked(configured_model);captured.append(configured_model)
    peer,rows=proof(root['controllerIndependentReview']);validate_peer(peer,index);captured+=rows;indices.append(root['controllerIndependentReview']['index'])
    captured+=protect_resource(refs)
    frame=dict(config=config,configDescriptor=config_row,root=root,refs=refs,captured=captured,families=indices,copyRows=copy_rows,sourceRows=source,ownRows=own,metadataModel=configured_model,externalSources=baseline['externalEmbeddingSources'])
    recheck(frame);return frame


def load_actual(row,name):
    path=checked(row);spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def environment(frame):
    plan=read(next(r for r in frame['sourceRows']if r['path']==str(PROPOSAL/'build-plan.json')))
    env=dict(plan['explicitEnvironment']);env.update(frame['refs']['normalEnvironmentExtra'])
    assert env['NODE_COMPAT_BUILD_ROOT']==str(WORK)and env['NODE_COMPAT_GC_STRESS']=='0'and env['NODE_COMPAT_ENTROPY_MODE']=='OFF'and env['NODE_COMPAT_BUILD_TYPE']=='Release'and env['NODE_COMPAT_OOM_TESTING']=='0'
    assert all(env[k]=='1'for k in['NODE_COMPAT_JOBS','BINARYEN_CORES','RAYON_NUM_THREADS','CARGO_BUILD_JOBS'])
    assert env['NODE_COMPAT_ARTIFACT_TAG']=='selectionv1'
    assert env['NODE_COMPAT_NODE']==frame['refs']['node']['path']
    inherited={k:v for k,v in os.environ.items()if not k.startswith(('NODE_COMPAT_','CMAKE_PROJECT_','NAPI_RS_','WASMTIME_'))and k not in['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH']}
    inherited.update(env);return env,inherited


def parent(frame):
    for p in[EXTERNAL,OUTPUT,WORK,FREEZE]:assert not p.exists()and not p.is_symlink()
    monitor=load_actual(frame['refs']['monitorEntry'],'genuine_selector342_owned_monitor');recheck(frame);EXTERNAL.mkdir(mode=0o700)
    argv=[sys.executable,'-B','-I',str(OWN/'controller.py'),'worker',json.dumps(frame['configDescriptor'],separators=(',',':'))]
    try:terminal=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},EXTERNAL,7200,frame['config']['rootAuthority'])
    finally:recheck(frame)
    assert terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone']is True and terminal['allObservedOwnedGroupsGone']is True
    assert terminal['timeout']is False and terminal['forcedCleanup']is False
    for k in['errors','signals','interruptedSignals','remainingObservedPids']:assert terminal[k]==[]
    assert terminal['stderr']['bytes']==0
    print(json.dumps(terminal),flush=True)


def write(path,value):
    with Path(path).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())


def metadata_observation(frame):
    engine=WORK/'artifacts'/ARTIFACT;sidecar=Path(str(engine)+'.build.json');raw=descriptor(sidecar);metadata=read(raw)
    policy_row=next(r for r in frame['sourceRows']if r['path']==str(PROPOSAL/'policy.json'));helper_row=next(r for r in frame['sourceRows']if r['path']==str(PROPOSAL/'layer-policy.py'));recipe_row=next(r for r in frame['sourceRows']if r['path']==str(PROPOSAL/'proposed/tests/node-compat/build-engine.sh'))
    model=load_actual(frame['metadataModel'],'genuine_configured_selector342_metadata_shape_model')
    shape=model.validate_metadata(metadata,read(policy_row),policy_row['sha256'],helper_row['sha256'],recipe_row['sha256'],frame['externalSources'],'normal-off')
    assert shape==dict(state='FINITE_RESOURCE_TASK_SELECTION342_METADATA_SHAPE_ONLY',nativeFiles=342,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
    assert metadata['enginePath']==str(engine)and metadata['engineBytes']>0
    actual=descriptor(engine);assert actual['sha256']==metadata['engineSha256']and actual['bytes']==metadata['engineBytes']
    with engine.open('rb')as stream:assert stream.read(8)==b'\0asm\x01\0\0\0'
    return dict(engine=actual,metadata=raw,finiteShapeOnly=shape,actualIndependentBuildReview=None,engineExecuted=False)


def validate_lifecycle_zero(result):
    """New caller requires no descendant cleanup signals even after shell raw0."""
    assert result['rawChildExitCode']==result['status']==0 and result['lifecycleComplete']is True
    assert result['childStarted']is True and result['stoppedForDiskSpace']is False and result['stopReason']is None
    assert result['sigtermReceived']==0 and result['temporarySigtermHandlerRestored']is True and result['launcherErrors']==[]
    cleanup=result['ownedGroupCleanup']
    assert cleanup['complete']is True and cleanup['rawChildExitCode']==0 and cleanup['events']==[]and cleanup['errors']==[]


def worker(frame):
    for p in[OUTPUT,WORK,FREEZE]:assert not p.exists()and not p.is_symlink()
    lifecycle=load_actual(frame['refs']['lifecycleEntry'],'genuine_original_resource_build_lifecycle')
    assert lifecycle.REQUIRED_START_FREE==2147483648 and lifecycle.MINIMUM_FREE==838860800
    recheck(frame);os.umask(0o077)
    free=lambda:os.statvfs(WORK if WORK.exists()else WORK.parent).f_bavail*os.statvfs(WORK if WORK.exists()else WORK.parent).f_frsize
    before=lifecycle.prepare_output(OUTPUT,free);explicit,child_env=environment(frame)
    command=['bash',str(SOURCE/'tests/node-compat/build-engine.sh')]
    result=dict(schemaVersion=1,state='TASK_SELECTION342_NORMAL_OFF_NATIVE_BUILD_STARTED',variant='normal-off',taskSelectionSourceIndexSha256=SOURCE_SHA,controllerIndex=frame['config']['controllerIndex'],rootAuthority=frame['config']['rootAuthority'],configuredSourceRoot=str(SOURCE),workRoot=str(WORK),command=command,explicitEnvironment=explicit,nativeSourceFiles=342,unchangedResourceParentFiles=339,nativeReplacements=3,externalEmbeddingSources=3,freeBytesBefore=before,requiredStartFreeBytes=lifecycle.REQUIRED_START_FREE,stopBelowFreeBytes=lifecycle.MINIMUM_FREE,parallelBuilds=1,rawChildExitCode=None,externalParentDeadlineSeconds=7200,gcReconfigureAllowed=False,normalOffFreezeStillRequired=True,guestExecutionRequested=False,engineExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
    write(OUTPUT/'launch.json',result);started=time.monotonic()
    try:
        with(OUTPUT/'build.log').open('xb')as log:
            result.update(lifecycle.monitor_owned_command(command,str(SOURCE),child_env,log,free));log.flush();os.fsync(log.fileno())
    except BaseException as error:result.setdefault('launcherErrors',[]).append(lifecycle.error_record('launch-or-monitor',error))
    result['wallSecondsForOperationalRecordOnly']=time.monotonic()-started
    try:result['freeBytesAfter']=free();result['buildLog']=descriptor(OUTPUT/'build.log')
    except BaseException as error:result.setdefault('finalObservationErrors',[]).append(lifecycle.error_record('final-file-or-disk-observation',error))
    try:
        recheck(frame);result['allSourceStageAndProofBytesPreserved']=True
        if result.get('rawChildExitCode')==0 and result.get('lifecycleComplete')is True and not result.get('launcherErrors'):
            validate_lifecycle_zero(result)
            result['actualMetadataObservation']=metadata_observation(frame)
    except BaseException as error:result.setdefault('finalObservationErrors',[]).append(lifecycle.error_record('final-source-or-new-metadata-observation',error))
    lifecycle.finalize_status(result);lifecycle.publish_result(OUTPUT,result,writer=write)
    assert result['launcherExitCode']==0;return result


def main():
    assert Path(__file__).resolve().parent==OWN and len(sys.argv)==3 and sys.argv[1]in('parent','worker')
    frame=authorize(json.loads(sys.argv[2]))
    try:
        if sys.argv[1]=='parent':parent(frame)
        else:worker(frame)
    finally:recheck(frame)


if __name__=='__main__':main()
