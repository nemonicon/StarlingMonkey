"""Dormant combined355 source stage and owned caller; stdlib bootstrap only.

The original preparation context remains authoritative. No producer/helper,
metadata classifier, build, freezer, engine or guest is imported or executed.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
if not __debug__:raise RuntimeError('Stage policy assertions must remain enabled')

REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/combined-native-stage-controller-candidate-v1'
SOURCE_FAMILY=REPO/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1'
SOURCE_SHA='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65'
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
MONITOR_SHA='0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b'
DEST=Path('/private/tmp/starling-node-compat/combined-native355-v1-source')
WORK=Path('/private/tmp/starling-node-compat/combined-native355-v1-build')
FREEZE=Path('/private/tmp/starling-node-compat/combined-native355-v1-freeze')
OUT=Path('/private/tmp/starling-node-compat/combined-native355-v1-stage-external-root')
JOURNAL=Path('/private/tmp/starling-node-compat/combined-native355-v1-stage.json')
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'
TIMEOUT=600


def safe(name):
    assert isinstance(name,str)and name and not name.startswith('/')and '\\'not in name and '\0'not in name
    assert all(p not in ('','.','..')for p in name.split('/'))and name.split('/')[0]!='.git'
    return name


def checked(row):
    assert type(row)is dict and set(row)=={'path','sha256','bytes'}
    assert type(row['bytes'])is int and row['bytes']>=0
    assert isinstance(row['sha256'],str)and len(row['sha256'])==64 and all(c in '0123456789abcdef'for c in row['sha256'])
    path=Path(row['path']);assert path.is_absolute()and '..'not in path.parts
    # Only the platform's declared /tmp alias is normalized for I/O. The
    # original descriptor strings and preparation manifests are never rewritten.
    if str(path).startswith('/tmp/'):path=Path('/private'+str(path))
    for p in (path,*path.parents):assert not p.is_symlink(),p
    before=path.stat();assert stat.S_ISREG(before.st_mode)and before.st_size==row['bytes']
    h=hashlib.sha256()
    with path.open('rb')as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    after=path.stat()
    assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    assert h.hexdigest()==row['sha256'];return path


def read(row):
    p=checked(row);assert row['bytes']<=32*1024*1024
    raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)


def descriptor(path):
    path=Path(path)
    if str(path).startswith('/tmp/'):path=Path('/private'+str(path))
    for p in (path,*path.parents):assert not p.is_symlink()
    assert stat.S_ISREG(path.stat().st_mode)
    h=hashlib.sha256()
    with path.open('rb')as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    row=dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size);checked(row);return row


def family(row):
    value=read(row);root=Path(row['path']).parent;rows=[row];names=set()
    for item in value['files']:
        name=safe(item['path']);assert name not in names;names.add(name)
        d=dict(path=str(root/name),sha256=item['sha256'],bytes=item['bytes']);checked(d);rows.append(d)
    actual=set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():actual.add(p.relative_to(root).as_posix())
    assert actual==names|{'index.json'};return value,rows


def indexed_result(pair):
    _,rows=family(pair['index']);assert sum(r==pair['result']for r in rows[1:])==1
    return read(pair['result']),rows


def source_peer_model(value):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_COMBINED355_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V1'
    assert value['sourceIndexSha256']==SOURCE_SHA and value['sourceOnly']is True and value['sourceReviewPassed']is True
    assert value['ownerActionsInvoked']is False and value['operationalAdmission']is False
    assert value['nativeSourceFiles']==355 and value['retainedParentNativeFiles']==348 and value['changedNativeFiles']==7
    assert value['externalEmbeddingSources']==3 and value['selectedManifestCount']==11
    assert value['initialVariant']=='normal-off'and value['privateBackendEvidenceHookEnabled']is False


def stage_peer_model(value,own):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_COMBINED355_SOURCE_STAGE_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert value['controllerSourceIndexSha256']==own['sha256']and value['integrationSourceIndexSha256']==SOURCE_SHA
    assert value['genericMonitorSourceIndexSha256']==MONITOR_SHA
    assert value['sourceOnly']is True and value['sourceReviewPassed']is True
    for key in ['ownerActionsInvoked','hostActionsInvoked','sourceStageActionsInvoked']:assert value[key]is False


def root_model(value,own,refs):
    assert value['schemaVersion']==1 and value['state']=='ROOT_REVIEWED_COMBINED355_SOURCE_STAGE_V1'
    assert value['phase']=='source-stage-only'and value['sourceStageAllowed']is True
    assert value['sourceIndex']==refs['integrationIndex']and value['sourceIndex']['sha256']==SOURCE_SHA
    assert value['stageControllerIndex']==own and value['stageControllerEntry']['path']==str(OWN/'controller.py')
    assert value['configuredSourceRoot']==str(DEST)and value['workRoot']==str(WORK)and value['freezeRoot']==str(FREEZE)
    assert value['externalOutputRoot']==str(OUT)and value['stageJournal']==str(JOURNAL)
    assert value['baselineRevision']==BASE and value['externalParentDeadlineSeconds']==TIMEOUT
    assert value['nativeSourceFiles']==355 and value['retainedParentNativeFiles']==348 and value['changedNativeFiles']==7
    assert value['externalEmbeddingSources']==3 and value['selectedManifestCount']==11 and value['initialVariant']=='normal-off'
    assert value['basePlanRows']==1581 and value['integrationFamilyRows']==32 and value['expectedStageCopies']==1613
    assert value['genericMonitorIndex']==refs['monitorIndex']and value['genericMonitorEntry']==refs['monitorEntry']
    for key in ['nativeBuildAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','keyOperationsAllowed','guestAllowed','gcAllowed','timingAllowed','normalMutationAllowed','metadataProjectionAllowed','privateBackendEvidenceHookEnabled','pinsAdopted','operationalAdmission','runtimeAcceptanceClaim']:assert value[key]is False
    for key in ['actualStageResult','actualStageReview','actualBuildResult','reviewedNativePins','runtimeAuthority']:assert value[key]is None


def plan_model(rows,native,tools,integration_rows):
    assert len(native)==355 and len(tools)==1226 and len(rows)==1613
    assert len({r['path']for r in rows})==1613
    expected={r['path']:(r['original'],r['sha256'],r['bytes'],[r.get('role','AUTHENTICATED_COMBINED_BUILD_TOOL_OR_ANCESTRY'),'EXACT_08BF_STAGE_INPUT_PLAN_ROW'])for r in native+tools}
    assert len(expected)==1581
    for r in integration_rows:
        name=Path(r['path']).relative_to(REPO).as_posix();assert name not in expected
        expected[name]=(r['path'],r['sha256'],r['bytes'],['EXACT_COMBINED_INTEGRATION_SEALED_FAMILY_DATA'])
    assert len(expected)==1613
    for r in rows:
        safe(r['path']);assert (r['original'],r['sha256'],r['bytes'],r['roles'])==expected[r['path']]
        assert type(r['sourceMode'])is int and 0<=r['sourceMode']<=0o777
        assert isinstance(r['roles'],list)and r['roles']
    assert sum(r.get('role','').startswith('UNCHANGED_GENUINE_SECRET355')for r in native)==348


def recheck(frame):
    for row in frame['captured']:checked(row)
    for row in frame['familyIndices']:family(row)
    for row in frame['copies']:
        p=checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']))
        assert stat.S_IMODE(p.stat().st_mode)==row['sourceMode']


def authorize(config_row):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated==1 and Path(__file__).resolve().parent==OWN
    config=read(config_row);assert config['schemaVersion']==1 and config['state']=='COMBINED355_SOURCE_STAGE_CONFIG_V1'
    root=read(config['rootAuthority']);own=root['stageControllerIndex']
    assert own['path']==str(OWN/'index.json')
    _,own_rows=family(own);assert root['stageControllerEntry']in own_rows
    refs=read(next(r for r in own_rows if r['path']==str(OWN/'references.json')))
    root_model(root,own,refs)
    own_inputs=read(next(r for r in own_rows if r['path']==str(OWN/'input-hashes.json')))
    assert own_inputs['sourceOriginalInputRows']==1590 and len(own_inputs['files'])==1637
    assert config['sourceIndex']==refs['integrationIndex']and config['controllerIndex']==own
    source,source_rows=family(refs['integrationIndex']);assert len(source_rows)==32
    captured=[config_row,config['rootAuthority'],*own_rows,*source_rows];indices=[own,refs['integrationIndex']]
    for row in own_inputs['files']:checked(row)
    captured+=own_inputs['files']
    value,rows=indexed_result(root['integrationSourceReview']);source_peer_model(value);captured+=rows;indices.append(root['integrationSourceReview']['index'])
    value,rows=indexed_result(root['stageControllerReview']);stage_peer_model(value,own);captured+=rows;indices.append(root['stageControllerReview']['index'])
    _,monitor_rows=family(refs['monitorIndex']);assert refs['monitorEntry']in monitor_rows
    captured+=monitor_rows;indices.append(refs['monitorIndex'])
    declared=read(next(r for r in source_rows if r['path']==str(SOURCE_FAMILY/'input-hashes.json')))
    assert len(declared['files'])==1590
    for row in declared['files']:checked(row)
    captured+=declared['files']
    plan=read(next(r for r in own_rows if r['path']==str(OWN/'stage-copy-plan.json')))
    native=read(next(r for r in source_rows if r['path']==str(SOURCE_FAMILY/'native-origins.json')))['files']
    tools=read(next(r for r in source_rows if r['path']==str(SOURCE_FAMILY/'tool-origins.json')))['files']
    plan_model(plan['files'],native,tools,source_rows)
    for row in plan['files']:captured.append(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']))
    for key in ['gitBinary','pythonExecutable']:checked(root[key]);captured.append(root[key])
    assert all(checked(root[key]).stat().st_mode&0o111 for key in ['gitBinary','pythonExecutable'])
    assert checked(root['pythonExecutable'])==Path(sys.executable).resolve()
    assert root['gitBinary']['path']==str(checked(root['gitBinary']))and Path(root['gitBinary']['path']).name=='git'
    frame=dict(config=config,root=root,captured=captured,familyIndices=indices,copies=plan['files'])
    recheck(frame);return frame


def absent(path):
    path=Path(path)
    for p in (path,*path.parents):assert not p.is_symlink(),p
    assert not path.exists(),path


def fsync_directory(path):
    fd=os.open(str(path),os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def durable(path,data):
    with Path(path).open('xb')as f:
        assert f.write(data)==len(data);f.flush();os.fchmod(f.fileno(),0o600);os.fsync(f.fileno())
    fsync_directory(Path(path).parent)
    return descriptor(path)


def progress(path,value):
    with Path(path).open('ab')as f:
        data=(json.dumps(value,separators=(',',':'))+'\n').encode();assert f.write(data)==len(data);f.flush();os.fsync(f.fileno())


def git_objects(root):
    directory=Path(root)/'.git/objects';assert directory.is_dir()and not directory.is_symlink()
    rows=[]
    for p in sorted(directory.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():
            s=p.stat();rows.append(dict(path=p.relative_to(directory).as_posix(),device=s.st_dev,inode=s.st_ino,bytes=s.st_size,mode=stat.S_IMODE(s.st_mode)))
    return rows


def git_environment():
    # Only child Git execution overrides are removed. User home variables stay
    # unchanged; no global config or original repository setting is rewritten.
    env={k:v for k,v in os.environ.items()if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',GIT_CONFIG_COUNT='0',GIT_TERMINAL_PROMPT='0')
    return env


def command(argv,folder):
    assert not folder.exists();folder.mkdir(mode=0o700)
    record=dict(argv=argv,timeoutSeconds=120,returncode=None,timedOut=False)
    stdout=stderr=b''
    try:
        child=subprocess.run(argv,capture_output=True,timeout=120,env=git_environment())
        stdout,stderr=child.stdout,child.stderr;record['returncode']=child.returncode
    except subprocess.TimeoutExpired as error:
        stdout=error.stdout or b'';stderr=error.stderr or b'';record['timedOut']=True
    finally:
        record['stdout']=durable(folder/'stdout.log',stdout);record['stderr']=durable(folder/'stderr.log',stderr)
        record['terminal']=durable(folder/'terminal.json',(json.dumps({**record,'rawStreamsRetainedBeforeAssertions':True},indent=2)+'\n').encode())
    return record


def partial_targets(rows):
    observed=[]
    for row in rows:
        target=DEST/row['path']
        if target.is_symlink():observed.append(dict(path=row['path'],type='symlink-refused'));continue
        if target.is_file():
            actual=descriptor(target);s=target.stat()
            observed.append(dict(path=row['path'],actual=actual,mode=stat.S_IMODE(s.st_mode),device=s.st_dev,inode=s.st_ino,matchesExpected=(actual['sha256'],actual['bytes'])==(row['sha256'],row['bytes'])))
    return observed


def stage(frame):
    for p in [DEST,WORK,FREEZE,JOURNAL]:absent(p)
    assert OUT.is_dir()and not OUT.is_symlink()and stat.S_IMODE(OUT.stat().st_mode)==0o700
    commands=OUT/'stage-commands';absent(commands);commands.mkdir(mode=0o700)
    progress_path=commands/'progress.jsonl';durable(progress_path,b'')
    progress(progress_path,dict(event='authenticated-stage-start',sourceIndexSha256=SOURCE_SHA,plannedCopies=1613))
    assert shutil.disk_usage(DEST.parent).free>=2*1024**3
    original_git=git_objects(REPO);original_ids={(r['device'],r['inode'])for r in original_git}
    for row in frame['copies']:
        p=checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']));s=p.stat();original_ids.add((s.st_dev,s.st_ino))
    result=dict(schemaVersion=1,state='COMBINED355_SOURCE_STAGE_STARTED',sourceIndexSha256=SOURCE_SHA,controllerIndex=frame['root']['stageControllerIndex'],rootAuthority=frame['config']['rootAuthority'],configuredSourceRoot=str(DEST),workRoot=str(WORK),freezeRoot=str(FREEZE),baselineRevision=BASE,commands=[],copiesCompleted=[],nativeSourceFiles=355,retainedParentNativeFiles=348,changedNativeFiles=7,externalEmbeddingSources=3,selectedManifestCount=11,nativeBuildExecuted=False,engineExecuted=False,guestExecuted=False,metadataProjected=False,privateBackendEvidenceHookEnabled=False,operationalAdmission=False)
    try:
        # Git accepts an existing empty destination. Creating it privately here
        # is part of the authorized stage, never source preparation.
        DEST.mkdir(mode=0o700)
        git=frame['root']['gitBinary']['path']
        for index,argv in enumerate([[git,'clone','--no-local','--no-checkout',str(REPO),str(DEST)],[git,'-C',str(DEST),'checkout','--detach',BASE]]):
            recorded=command(argv,commands/str(index));result['commands'].append(recorded)
            progress(progress_path,dict(event='git-command-returned',index=index,record=recorded))
            assert recorded['returncode']==0 and not recorded['timedOut']
        DEST.chmod(0o700);assert stat.S_IMODE(DEST.stat().st_mode)==0o700 and (DEST/'.git/HEAD').read_text()==BASE+'\n'
        absent(DEST/'.git/objects/info/alternates')
        staged_git=git_objects(DEST);assert not original_ids&{(r['device'],r['inode'])for r in staged_git}
        for row in frame['copies']:
            p=checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']));assert stat.S_IMODE(p.stat().st_mode)==row['sourceMode']
            target=DEST
            for part in safe(row['path']).split('/'):
                target/=part;assert not target.is_symlink()
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():
                s=target.stat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and(s.st_dev,s.st_ino)not in original_ids
            data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256']and len(data)==row['bytes']
            with target.open('wb'if target.exists()else'xb')as f:
                assert f.write(data)==len(data);f.flush();os.fchmod(f.fileno(),row['sourceMode']);os.fsync(f.fileno())
            actual=checked(dict(path=str(target),sha256=row['sha256'],bytes=row['bytes']));s=actual.stat()
            assert(s.st_dev,s.st_ino)not in original_ids and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==row['sourceMode']
            result['copiesCompleted'].append(row)
            progress(progress_path,dict(event='copy-verified',count=len(result['copiesCompleted']),path=row['path'],sha256=row['sha256'],bytes=row['bytes']))
        target_ids=[]
        for row in frame['copies']:
            p=checked(dict(path=str(DEST/row['path']),sha256=row['sha256'],bytes=row['bytes']));s=p.stat();target_ids.append((s.st_dev,s.st_ino));assert stat.S_IMODE(s.st_mode)==row['sourceMode']and s.st_nlink==1
            origin=checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes'])).stat();assert(s.st_dev,s.st_ino)!=(origin.st_dev,origin.st_ino)
        assert len(target_ids)==len(set(target_ids))==1613 and not set(target_ids)&original_ids
        assert git_objects(REPO)==original_git
        recheck(frame);absent(WORK);absent(FREEZE)
        for p in sorted({DEST,*[ (DEST/r['path']).parent for r in frame['copies']]},key=lambda p:len(p.parts),reverse=True):fsync_directory(p)
        result.update(state='COMBINED355_SOURCE_STAGED_NOT_BUILT',copies=frame['copies'],copiedFiles=1613,allCopiedHashesModesAndDistinctInodesVerified=True,detachedHead=BASE,gitObjectInodesDisjoint=True,sourceOriginalInputsRechecked=True,originalGitObjectIdentityUnchanged=True)
    except BaseException as error:
        result.update(state='COMBINED355_SOURCE_STAGE_FAILED_OR_PARTIAL_RETAINED',errorType=type(error).__name__)
        try:result['partialTargets']=partial_targets(frame['copies'])
        except BaseException as partial:result['partialObservationError']=type(partial).__name__
        try:recheck(frame);result['failureInputRecheckPassed']=True
        except BaseException as check:result['failureInputRecheckPassed']=False;result['failureInputRecheckError']=type(check).__name__
        raise
    finally:
        result['progress']=descriptor(progress_path)
        durable(JOURNAL,(json.dumps(result,indent=2)+'\n').encode())
        print(json.dumps(dict(journal=descriptor(JOURNAL),state=result['state'],copiedFiles=len(result['copiesCompleted']))),flush=True)


def terminal_model(value,authority):
    assert value['authority']==authority and value['rawExitCode']==0
    assert value['parentOwnedGroupGone']is True and value['allObservedOwnedGroupsGone']is True
    for key in ['timeout','forcedCleanup']:assert value[key]is False
    for key in ['interruptedSignals','remainingObservedPids','signals','errors']:assert value[key]==[]
    assert value['stderr']['bytes']==0 and value['observedProcesses']and value['finalGroups']
    assert all(g['alive']is False for g in value['finalGroups'])


def journal_model(value,frame):
    assert value['schemaVersion']==1 and value['state']=='COMBINED355_SOURCE_STAGED_NOT_BUILT'and value['sourceIndexSha256']==SOURCE_SHA
    assert value['copies']==value['copiesCompleted']==frame['copies']and value['copiedFiles']==1613
    assert value['rootAuthority']==frame['config']['rootAuthority']and value['controllerIndex']==frame['root']['stageControllerIndex']
    for key in ['configuredSourceRoot','workRoot','freezeRoot']:
        assert value[key]==frame['root'][key]
    assert value['baselineRevision']==value['detachedHead']==BASE
    assert value['nativeSourceFiles']==355 and value['retainedParentNativeFiles']==348 and value['changedNativeFiles']==7
    assert value['externalEmbeddingSources']==3 and value['selectedManifestCount']==11
    for key in ['nativeBuildExecuted','engineExecuted','guestExecuted','metadataProjected','privateBackendEvidenceHookEnabled','operationalAdmission']:assert value[key]is False
    for key in ['allCopiedHashesModesAndDistinctInodesVerified','gitObjectInodesDisjoint','sourceOriginalInputsRechecked','originalGitObjectIdentityUnchanged']:assert value[key]is True
    git=frame['root']['gitBinary']['path']
    expected=[[git,'clone','--no-local','--no-checkout',str(REPO),str(DEST)],[git,'-C',str(DEST),'checkout','--detach',BASE]]
    assert [row['argv']for row in value['commands']]==expected
    assert all(row['returncode']==0 and row['timedOut']is False and row['timeoutSeconds']==120 for row in value['commands'])


def main(config_row,worker=False):
    frame=authorize(config_row)
    if worker:stage(frame);return
    try:
        for p in [DEST,WORK,FREEZE,OUT,JOURNAL]:absent(p)
        # Import only the genuine authenticated monitor API, never its old main.
        spec=importlib.util.spec_from_file_location('genuine_combined355_stage_monitor',checked(frame['root']['genericMonitorEntry']))
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);recheck(frame)
        OUT.mkdir(mode=0o700)
        argv=[str(checked(frame['root']['pythonExecutable'])),'-B','-I',str(OWN/'controller.py'),'--stage-worker',json.dumps(config_row,separators=(',',':'))]
        terminal=module.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OUT,TIMEOUT,frame['config']['rootAuthority'])
        terminal_model(terminal,frame['config']['rootAuthority'])
        for row in [terminal['stdout'],terminal['stderr']]:checked(row)
        journal=descriptor(JOURNAL);value=read(journal)
        journal_model(value,frame)
        assert not DEST.is_symlink()and stat.S_IMODE(DEST.stat().st_mode)==0o700
        for recorded in value['commands']:
            for key in ['stdout','stderr','terminal']:checked(recorded[key])
            assert read(recorded['terminal'])=={**{k:v for k,v in recorded.items()if k!='terminal'},'rawStreamsRetainedBeforeAssertions':True}
        checked(value['progress'])
        for row in frame['copies']:
            p=checked(dict(path=str(DEST/row['path']),sha256=row['sha256'],bytes=row['bytes']));s=p.stat();assert stat.S_IMODE(s.st_mode)==row['sourceMode']and s.st_nlink==1
            original=checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes'])).stat();assert(s.st_dev,s.st_ino)!=(original.st_dev,original.st_ino)
        recheck(frame);absent(WORK);absent(FREEZE)
        print(json.dumps(dict(schemaVersion=1,state='COMBINED355_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1',sourceIndexSha256=SOURCE_SHA,actualStageResult=journal,externalTerminal=descriptor(OUT/'terminal.json'),copiedFiles=1613,nativeSourceFiles=355,independentResultReviewRequired=True,nativeBuildExecuted=False,engineExecuted=False,operationalAdmission=False)),flush=True)
    finally:recheck(frame)


if __name__=='__main__':
    assert len(sys.argv)in[2,3]
    if len(sys.argv)==3:assert sys.argv[1]=='--stage-worker';main(json.loads(sys.argv[2]),True)
    else:main(json.loads(sys.argv[1]))
