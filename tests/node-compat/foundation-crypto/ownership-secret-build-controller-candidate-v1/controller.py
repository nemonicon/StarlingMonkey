"""Dormant parent/worker source for one separately authorized normal-OFF build.

Only standard-library code is loaded until the whole source/stage/protection
capsule is authenticated. No artifact_common, native guard or old main is used.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import stat
import sys
import time

REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-crypto/ownership-secret-build-controller-candidate-v1'
INTEGRATION=REPO/'tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1'
INTEGRATION_SHA='7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108'
SOURCE='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source'
WORK='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build'
FREEZE='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze'
BUILD_OUTPUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-normal-off-build-root')
OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-normal-off-build-external-root')
TIMEOUT=7200


def checked(row):
    assert type(row)is dict and set(row)=={'path','sha256','bytes'}
    assert type(row['bytes'])is int and row['bytes']>=0
    assert isinstance(row['sha256'],str)and len(row['sha256'])==64 and all(c in '0123456789abcdef'for c in row['sha256'])
    p=Path(row['path']);assert p.is_absolute()and '..'not in p.parts
    if str(p).startswith('/tmp/'):p=Path('/private'+str(p))
    for parent in (p,*p.parents):assert not parent.is_symlink(),parent
    before=p.stat();assert stat.S_ISREG(before.st_mode);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=p.stat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    assert before.st_size==row['bytes']and h.hexdigest()==row['sha256'];return p


def descriptor(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    row=dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size);checked(row);return row


def read(row):
    p=checked(row);assert row['bytes']<=32*1024*1024
    raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)


def family(row):
    value=read(row);root=Path(row['path']).parent;rows=[row];seen=set()
    for r in value['files']:
        name=r['path'];assert isinstance(name,str)and name and name not in seen and '\\'not in name and '\0'not in name
        assert not name.startswith('/')and all(p not in ('','.','..')for p in name.split('/'))
        seen.add(name);d=dict(path=str(root/name),sha256=r['sha256'],bytes=r['bytes']);checked(d);rows.append(d)
    actual=set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():actual.add(str(p.relative_to(root)))
    assert actual==seen|{'index.json'};return rows


def indexed_result(pair):
    rows=family(pair['index']);assert sum(r==pair['result']for r in rows[1:])==1
    return read(pair['result']),rows


def validate_terminal(value,authority):
    assert value['schemaVersion']==1 and value['authority']==authority and value['rawExitCode']==0
    assert value['parentOwnedGroupGone']is True and value['allObservedOwnedGroupsGone']is True
    for k in ['forcedCleanup','timeout']:assert value[k]is False
    for k in ['remainingObservedPids','signals','errors','interruptedSignals']:assert value[k]==[]
    assert value['observedProcesses']and value['finalGroups']and all(g['alive']is False for g in value['finalGroups'])
    return True


def validate_root(root,own,refs):
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_NORMAL_OFF_BUILD_V1'
    assert root['phase']=='build'and root['variant']=='normal-off'and root['buildAllowed']is True
    assert root['sourceIndexSha256']==INTEGRATION_SHA and root['configuredSourceRoot']==SOURCE
    assert root['workRoot']==WORK and root['freezeRoot']==FREEZE
    assert root['buildOutputRoot']==str(BUILD_OUTPUT)and root['externalOutputRoot']==str(OUT)
    assert root['nativeSourceFiles']==355 and root['unchangedParentNativeFiles']==352 and root['changedNativeFiles']==3
    assert root['stageCopies']==1424 and root['externalParentDeadlineSeconds']==TIMEOUT
    assert root['externalControllerIndex']==own and own['path']==str(OWN/'index.json')
    assert root['externalControllerEntry']['path']==str(OWN/'controller.py')
    assert root['workerEntry']==root['externalControllerEntry']and root['workerMode']=='worker'
    assert root['integrationSourceReview']==refs['integrationSourceReview']
    assert root['actualStageReview']==refs['actualStageReview']and refs['actualStageReview']is not None
    assert root['stageRootObservation']==refs['stageRootObservation']and root['actualStageJournal']==refs['actualStageJournal']
    assert root['genericMonitorEntry']==refs['monitorEntry']and root['genericMonitorIndex']==refs['monitorIndex']
    assert root['lifecycleEntry']==refs['lifecycleEntry']and root['lifecycleSourceIndex']==refs['lifecycleSourceIndex']
    assert root['buildEnvironment']==refs['buildEnvironment']
    assert root['parallelBuilds']==1 and root['requiredStartFreeBytes']==2147483648 and root['stopBelowFreeBytes']==838860800
    for k in ['stageAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','componentAllowed','guestAllowed',
              'keyOperationsAllowed','gcAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission',
              'runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:
        assert root[k]is False
    for k in ['actualBuildResult','actualBuildReview','actualFreezeResult','reviewedNativePins','bootstrapAuthority','runtimeAuthority']:assert root[k]is None
    return True


def validate_source_peer(value):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_INTEGRATION_SOURCE_REVIEW_PASSED_V1'
    assert value['sourceIndexSha256']==INTEGRATION_SHA and value['sourceOnly']is True and value['sourceReviewPassed']is True
    assert value['ownerActionsInvoked']is False and value['operationalAdmission']is False
    assert value['nativeSourceFiles']==355 and value['unchangedParentNativeFiles']==352 and value['changedNativeFiles']==3


def validate_stage(value,root_result,refs):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_SOURCE_STAGE_REVIEW_PASSED_V1'and value['verifiedPassed']is True
    assert value['sourceIndexSha256']==INTEGRATION_SHA and value['configuredSourceRoot']==SOURCE
    assert value['nativeSourceFiles']==355 and value['unchangedParentNativeFiles']==352 and value['changedNativeFiles']==3
    for k in ['actualJournal','rootObservation','outerTerminal','innerTerminal','rootAuthority','rootConfig']:assert value[k]==refs['stageDescriptors'][k]
    assert value['actualControllerExitCode']==0 and value['actualStageExitCode']==0
    assert root_result['actualControllerExitCode']==0 and root_result['actualStageExitCode']==0 and root_result['sourceStageRepeated']is False
    # The historical report caller failed AFTER the successful stage. Never relabel that status.
    assert root_result['rootCallerExitCode']==1 and value['rootReportedCallerExitCode']==1
    return True


def validate_controller_peer(value,own,refs):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert value['controllerSourceIndexSha256']==own['sha256']and value['integrationSourceIndexSha256']==INTEGRATION_SHA
    assert value['actualStageReviewIndexSha256']==refs['actualStageReview']['index']['sha256']
    assert value['genericMonitorSourceIndexSha256']==refs['monitorIndex']['sha256']
    assert value['sourceOnly']is True and value['sourceReviewPassed']is True
    for k in ['ownerActionsInvoked','hostActionsInvoked','nativeBuildActionsInvoked']:assert value[k]is False


def normal_protection(row):
    value=read(row);assert value['originalReferenceEntries']==1387 and len(value['requiredNormalFreezeMembership'])==1391
    rows=[row,value['freezeReceipt']]
    rows += [{k:r[k]for k in ['path','sha256','bytes']}for r in value['frozenCopyEntries']]
    for r in value['originals']:rows.extend([r['original'],r['frozen']])
    for r in rows:checked(r)
    root=Path(value['freezeReceipt']['path']).parent;names=set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():names.add(str(p.relative_to(root)))
    assert names==set(value['requiredNormalFreezeMembership']);return rows


def validate_stage_copies(journal):
    assert journal['state']=='SECRET_NATIVE355_SOURCE_STAGED_NOT_BUILT'and journal['sourceIndexSha256']==INTEGRATION_SHA
    assert journal['configuredSourceRoot']==SOURCE and journal['workRoot']==WORK and journal['freezeRoot']==FREEZE
    assert journal['nativeSourceFiles']==355 and len(journal['copies'])==1424
    assert len({r['path']for r in journal['copies']})==1424
    for r in journal['copies']:
        p=Path(r['path']);assert not p.is_absolute()and all(x not in ('','.','..')for x in r['path'].split('/'))
        original=checked(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
        target=checked(dict(path=str(Path(SOURCE)/r['path']),sha256=r['sha256'],bytes=r['bytes']))
        assert stat.S_IMODE(original.stat().st_mode)==stat.S_IMODE(target.stat().st_mode)==r['sourceMode']
        assert (original.stat().st_dev,original.stat().st_ino)!=(target.stat().st_dev,target.stat().st_ino)


def recheck(frame):
    for r in frame['captured']:checked(r)
    for r in frame['familyIndices']:family(r)
    normal_protection(frame['normalProtection'])
    validate_stage_copies(frame['stageJournal'])


def authorize(config_row):
    config=read(config_row);assert config['schemaVersion']==1 and config['state']=='SECRET_OWNER355_NORMAL_OFF_BUILD_CONFIG_V1'
    root=read(config['rootAuthority']);own=root['externalControllerIndex'];own_rows=family(own)
    assert root['externalControllerEntry']in own_rows
    refs=read(next(r for r in own_rows if r['path']==str(OWN/'references.json')))
    validate_root(root,own,refs)
    assert config['sourceIndex']==refs['integrationIndex']and config['sourceIndex']['sha256']==INTEGRATION_SHA
    captured=[config_row,config['rootAuthority'],*own_rows];indices=[own]
    for item in refs['families']:
        captured+=family(item['index']);indices.append(item['index'])
    assert refs['monitorEntry']in captured and refs['lifecycleEntry']in captured
    for r in refs['files']:checked(r);captured.append(r)
    source_rows=family(config['sourceIndex']);captured+=source_rows;indices.append(config['sourceIndex'])
    ir=read(next(r for r in source_rows if r['path']==str(INTEGRATION/'references.json')))
    for item in ir['families']:
        captured+=family(item['index']);indices.append(item['index'])
    captured.append(ir['mandatoryHistoryErratum']);checked(ir['mandatoryHistoryErratum'])
    data,rows=indexed_result(refs['integrationSourceReview']);validate_source_peer(data);captured+=rows;indices.append(refs['integrationSourceReview']['index'])
    assert refs['actualStageReview']is not None
    data,rows=indexed_result(refs['actualStageReview']);captured+=rows;indices.append(refs['actualStageReview']['index'])
    root_result=read(refs['stageRootObservation']);validate_stage(data,root_result,refs)
    for key in ['outerTerminal','innerTerminal']:
        terminal=read(refs['stageDescriptors'][key])
        validate_terminal(terminal,refs['stageDescriptors']['rootAuthority'])
        for k in ['stdout','stderr']:checked(terminal[k]);captured.append(terminal[k])
    data,rows=indexed_result(root['externalControllerReview']);validate_controller_peer(data,own,refs)
    captured+=rows;indices.append(root['externalControllerReview']['index'])
    normal=ir['normalProtection'];captured+=normal_protection(normal)
    journal=read(refs['actualStageJournal']);validate_stage_copies(journal)
    for r in journal['copies']:
        captured.extend([dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']),dict(path=str(Path(SOURCE)/r['path']),sha256=r['sha256'],bytes=r['bytes'])])
    for r in [refs['monitorEntry'],refs['lifecycleEntry'],refs['node']]:checked(r);captured.append(r)
    recipe=Path(SOURCE)/'tests/node-compat/build-engine.sh'
    checked(dict(path=str(recipe),sha256=refs['recipe']['sha256'],bytes=refs['recipe']['bytes']))
    frame=dict(config=config,root=root,refs=refs,ownIndex=own,captured=captured,familyIndices=indices,
               normalProtection=normal,stageJournal=journal)
    recheck(frame);return frame


def write(path,value):
    with Path(path).open('x')as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())


def load_actual(row,name):
    spec=importlib.util.spec_from_file_location(name,checked(row));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def validate_new_metadata(value,policy,refs):
    assert value['buildRecipeSha256']==refs['recipe']['sha256']
    assert value['sourceManifest']==policy['expectedNativeSourceManifest']and len(value['sourceManifest'])==355
    assert len(value['componentizeSourceManifest'])==3 and value['hostApi']=='wasi-0.2.10'
    assert value['gcStress']is False and value['entropyPolicy']=='off'and value['oomTesting']is False
    for k in ['profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled',
              'streamWebEnabled','internalTicksEnabled','classicStreamsEnabled','zlibEnabled','streamConsumersEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled']:assert value[k]is True
    for k in ['debuggerEnabled','wptSupportEnabled']:assert value[k]is False
    assert value['cryptoSecretFailureSourcePolicy']==policy['cryptoSecretFailureSourcePolicy']
    evidence=value['cryptoSecretFailureBuildEvidence'];assert evidence['currentSourceManifestValidated']is True and len(evidence['changedNativeCompileCommands'])==2
    assert evidence['faultInjectionObserved']is False and evidence['runtimeValidation']is None
    assert value['cryptoKeyOwnershipPolicy']==policy['cryptoKeyOwnershipSourcePolicy']
    assert value['internalTickPolicy']['policyFileSha256']==refs['policy']['sha256']and value['internalTickPolicy']['helperSha256']==refs['helper']['sha256']
    assert value['observedCMakeOptions']==value['requestedCMakeOptions']
    for k,v in [('CMAKE_BUILD_TYPE','Release'),('NODE_COMPAT_GC_STRESS','OFF'),('NODE_COMPAT_ENTROPY_MODE','OFF'),('NODE_COMPAT_OOM_TESTING','OFF'),('NODE_COMPAT_LOCKED_RUST','ON')]:assert value['observedCMakeOptions'][k]==v
    assert value['generatedRustProject']['cargoBuildLocked']is True and value['generatedRustProject']['manifestAndLockCheckedBeforeAndAfterBuild']is True
    assert value['zlibPolicy']['runtimeBackendProof']==dict(verified=False,version=None,vernum=None)
    assert value['zlibSelectedCodecInput']['archive']['sha256']=='298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc'
    for k in ['cmakeCachePath','compileCommandsPath']:assert value[k].startswith(WORK+'/')
    return True


def worker(frame):
    refs=frame['refs'];root=frame['root']
    for p in [Path(WORK),BUILD_OUTPUT]:assert not p.exists()and not p.is_symlink()
    lifecycle=load_actual(refs['lifecycleEntry'],'genuine_secret_build_explicit_lifecycle')
    # This original constant remains original. Its main/old common is never selected.
    assert lifecycle.RECIPE_SHA256==refs['lifecycleDormantRecipeSha256']
    assert lifecycle.REQUIRED_START_FREE==2147483648 and lifecycle.MINIMUM_FREE==838860800
    recheck(frame)
    work=Path(WORK)
    free=lambda:os.statvfs(work if work.exists()else work.parent).f_bavail*os.statvfs(work if work.exists()else work.parent).f_frsize
    before=lifecycle.prepare_output(BUILD_OUTPUT,free)
    environment={k:v for k,v in os.environ.items()if not k.startswith(('NODE_COMPAT_','CMAKE_PROJECT_','NAPI_RS_','WASMTIME_'))and k not in ('NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH')}
    environment.update(refs['buildEnvironment'])
    command=['bash',SOURCE+'/tests/node-compat/build-engine.sh']
    result=dict(schemaVersion=1,family='secret-owner355-normal-off-build-v1',sourceIndexSha256=INTEGRATION_SHA,
        controllerSourceIndexSha256=frame['ownIndex']['sha256'],rootAuthority=frame['config']['rootAuthority'],actualStageReview=refs['actualStageReview'],
        configuredSourceRoot=SOURCE,workRoot=WORK,freezeRoot=FREEZE,command=command,explicitEnvironment=refs['buildEnvironment'],
        freeBytesBefore=before,requiredStartFreeBytes=lifecycle.REQUIRED_START_FREE,stopBelowFreeBytes=lifecycle.MINIMUM_FREE,
        parallelBuilds=1,rawChildExitCode=None,guestExecutionRequested=False,engineExecuted=False,operationalAdmission=False,
        donorLifecycleEntry=refs['lifecycleEntry'],donorMainInvoked=False,donorDormantRecipeSha256=lifecycle.RECIPE_SHA256,
        actualRecipeSha256=refs['recipe']['sha256'],normalOffFrozenBeforeGCReconfigure=None)
    write(BUILD_OUTPUT/'launch.json',result);started=time.monotonic()
    try:
        with (BUILD_OUTPUT/'build.log').open('xb')as log:
            result.update(lifecycle.monitor_owned_command(command,SOURCE,environment,log,free))
            log.flush();os.fsync(log.fileno())
        cleanup=result.get('ownedGroupCleanup')or{}
        if cleanup.get('events')or cleanup.get('errors')or cleanup.get('complete')is not True:
            result.setdefault('finalObservationErrors',[]).append(dict(stage='inner-owned-group-cleanliness',events=cleanup.get('events'),errors=cleanup.get('errors')))
        if result.get('rawChildExitCode')==0:
            engine=Path(WORK)/'artifacts'/refs['artifactBasename'];meta=Path(str(engine)+'.build.json')
            data=read(descriptor(meta));policy=json.loads((INTEGRATION/'policy.json').read_bytes());validate_new_metadata(data,policy,refs)
            result['engine']=descriptor(engine);result['metadata']=descriptor(meta)
    except BaseException as error:result.setdefault('launcherErrors',[]).append(lifecycle.error_record('build-or-metadata-observation',error))
    finally:
        result['nativeBuildCommandStarted']=result.get('childStarted',False)
        result['wallSecondsForOperationalRecordOnly']=time.monotonic()-started
        try:result['freeBytesAfter']=free();result['logSha256']=lifecycle.digest(BUILD_OUTPUT/'build.log')
        except BaseException as error:result.setdefault('finalObservationErrors',[]).append(lifecycle.error_record('disk-log-final-observation',error))
        try:recheck(frame);result['allOriginalNormalAndStageBytesPreserved']=True
        except BaseException as error:result.setdefault('finalObservationErrors',[]).append(lifecycle.error_record('normal-stage-source-recheck',error))
        lifecycle.finalize_status(result);lifecycle.publish_result(BUILD_OUTPUT,result,writer=write)
    assert result['launcherExitCode']==0;return result


def parent(frame):
    for p in [OUT,Path(WORK),BUILD_OUTPUT]:assert not p.exists()and not p.is_symlink()
    monitor=load_actual(frame['refs']['monitorEntry'],'genuine_secret_build_outer_monitor')
    recheck(frame);OUT.mkdir(mode=0o700)
    argv=[sys.executable,'-B','-I',str(OWN/'controller.py'),'worker',json.dumps(frame['configDescriptor'],separators=(',',':'))]
    try:terminal=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OUT,TIMEOUT,frame['config']['rootAuthority'])
    finally:recheck(frame)
    validate_terminal(terminal,frame['config']['rootAuthority'])
    assert terminal['stderr']['bytes']==0
    result=read(descriptor(BUILD_OUTPUT/'result.json'))
    assert result['rawChildExitCode']==0 and result['launcherExitCode']==0 and result['lifecycleComplete']is True
    assert result['state']=='native-build-completed-runtime-pending'and result['evidenceComplete']is True
    assert result['rootAuthority']==frame['config']['rootAuthority']and result['sourceIndexSha256']==INTEGRATION_SHA
    assert result['ownedGroupCleanup']['complete']is True and result['ownedGroupCleanup']['events']==[]and result['ownedGroupCleanup']['errors']==[]
    assert result['explicitEnvironment']==frame['refs']['buildEnvironment']and result['allOriginalNormalAndStageBytesPreserved']is True
    print(json.dumps(dict(schemaVersion=1,state='SECRET_NORMAL_OFF_BUILD_RAW_ZERO_UNREVIEWED_V1',actualBuildResult=descriptor(BUILD_OUTPUT/'result.json'),
        externalTerminal=descriptor(OUT/'terminal.json'),independentBuildReviewRequired=True,engineExecuted=False,operationalAdmission=False)),flush=True)


def main():
    assert __debug__ and sys.dont_write_bytecode and len(sys.argv)==3 and sys.argv[1]in ('parent','worker')
    assert not any(os.environ.get(k)for k in ['PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH'])
    config_row=json.loads(sys.argv[2]);frame=authorize(config_row);frame['configDescriptor']=config_row
    try:
        if sys.argv[1]=='parent':parent(frame)
        else:worker(frame)
    finally:
        recheck(frame)  # Includes import/output/pre-launch and result-reader failure paths.


if __name__=='__main__':main()
