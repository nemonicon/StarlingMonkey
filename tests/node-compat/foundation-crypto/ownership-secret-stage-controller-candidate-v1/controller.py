"""Dormant source-stage-only caller of the genuine0af owned-process monitor.

Standard-library authentication precedes the only custom import. This file
issues no authority and never imports the native stage/helper into this process.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import stat
import sys

REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-crypto/ownership-secret-stage-controller-candidate-v1'
INTEGRATION=REPO/'tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1'
INTEGRATION_SHA='7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108'
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
MONITOR_SHA='0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b'
SOURCE='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source'
WORK='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build'
FREEZE='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze'
JOURNAL=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-stage.json')
OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-stage-external-root')
TIMEOUT=600


def checked(row):
    assert type(row)is dict and set(row)=={'path','sha256','bytes'}
    assert type(row['bytes'])is int and row['bytes']>=0
    assert isinstance(row['sha256'],str)and len(row['sha256'])==64 and all(c in '0123456789abcdef'for c in row['sha256'])
    path=Path(row['path']);assert path.is_absolute()and '..'not in path.parts
    if str(path).startswith('/tmp/'):path=Path('/private'+str(path))
    for p in (path,*path.parents):assert not p.is_symlink(),p
    before=path.stat();assert stat.S_ISREG(before.st_mode)
    h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=path.stat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    assert h.hexdigest()==row['sha256']and before.st_size==row['bytes'];return path


def read(row):
    path=checked(row);assert row['bytes']<=32*1024*1024
    raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)


def descriptor(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    row=dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size);checked(row);return row


def family(row):
    index=read(row);root=Path(row['path']).parent;rows=[row];names=set()
    for member in index['files']:
        name=member['path']
        assert name not in names and isinstance(name,str)and name and '\\'not in name and '\0'not in name
        assert not name.startswith('/')and all(p not in ('','.','..')for p in name.split('/'))
        names.add(name);d=dict(path=str(root/name),sha256=member['sha256'],bytes=member['bytes']);checked(d);rows.append(d)
    actual=set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():actual.add(str(p.relative_to(root)))
    assert actual==names|{'index.json'};return rows


def indexed_result(pair):
    rows=family(pair['index']);assert sum(r==pair['result']for r in rows[1:])==1
    return read(pair['result']),rows


def validate_root(root,own_index,payload_peer):
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_SOURCE_STAGE_V1'
    assert root['sourceIndexSha256']==INTEGRATION_SHA and root['destination']==SOURCE
    assert root['workRoot']==WORK and root['freezeRoot']==FREEZE
    assert root['sourceStageAllowed']is True and root['variant']=='normal-off'
    for k in ['nativeBuildAllowed','freezeAllowed','engineExecutionAllowed','keyOperationsAllowed','guestAllowed','gcAllowed',
              'operationalAdmission','runtimeAcceptanceClaim','pinsAdopted','normalMutationAllowed','metadataProjectionAllowed','timingAllowed']:
        assert root[k]is False
    assert root['nativeSourceFiles']==355 and root['unchangedParentNativeFiles']==352 and root['changedNativeFiles']==3
    assert root['baseStageRows']==1403 and root['expectedStageCopies']==1424
    assert root['payloadSourceReview']==payload_peer
    assert root['externalControllerIndex']==own_index and own_index['path']==str(OWN/'index.json')
    assert root['externalControllerEntry']['path']==str(OWN/'controller.py')
    assert root['stageEntry']['path']==str(INTEGRATION/'stage.py')
    assert root['genericMonitorIndex']['path']==str(MONITOR/'index.json')and root['genericMonitorIndex']['sha256']==MONITOR_SHA
    assert root['genericMonitorEntry']['path']==str(MONITOR/'monitor.py')
    assert root['externalOutputRoot']==str(OUT)and root['stageJournal']==str(JOURNAL)
    assert root['externalParentDeadlineSeconds']==TIMEOUT
    assert root['actualStageResult']is None and root['actualStageReview']is None
    assert root['actualBuildResult']is None and root['reviewedNativePins']is None
    return True


def validate_integration_peer(value):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_INTEGRATION_SOURCE_REVIEW_PASSED_V1'
    assert value['sourceIndexSha256']==INTEGRATION_SHA and value['sourceOnly']is True and value['sourceReviewPassed']is True
    assert value['ownerActionsInvoked']is False and value['operationalAdmission']is False
    assert value['nativeSourceFiles']==355 and value['unchangedParentNativeFiles']==352 and value['changedNativeFiles']==3
    return True


def validate_controller_peer(value,own_index):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_STAGE_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert value['controllerSourceIndexSha256']==own_index['sha256']and value['integrationSourceIndexSha256']==INTEGRATION_SHA
    assert value['genericMonitorSourceIndexSha256']==MONITOR_SHA
    assert value['sourceOnly']is True and value['sourceReviewPassed']is True
    for k in ['ownerActionsInvoked','hostActionsInvoked','sourceStageActionsInvoked']:assert value[k]is False
    return True


def normal_protection(row):
    value=read(row);assert value['originalReferenceEntries']==1387 and len(value['requiredNormalFreezeMembership'])==1391
    captured=[row,value['freezeReceipt']]
    for item in value['frozenCopyEntries']:
        captured.append({k:item[k]for k in ['path','sha256','bytes']})
    for item in value['originals']:captured.extend([item['original'],item['frozen']])
    for item in captured:checked(item)
    root=Path(value['freezeReceipt']['path']).parent;actual=set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():actual.add(str(p.relative_to(root)))
    assert actual==set(value['requiredNormalFreezeMembership'])
    return captured


def expected_copies(native,tools,integration_rows):
    """Pure row merger. The path-stat/mode seam is explicit and source-only tested."""
    rows={}
    def add(name,original,sha,size,role):
        p=checked(dict(path=original,sha256=sha,bytes=size))
        row=dict(path=name,original=str(p),sha256=sha,bytes=size,sourceMode=stat.S_IMODE(p.stat().st_mode),roles=[role])
        if name in rows:
            assert all(rows[name][k]==row[k]for k in ['sha256','bytes','sourceMode'])
            rows[name]['roles'].append(role)
        else:rows[name]=row
    assert len(native)==355 and len(tools)==1051
    for r in native:add(r['path'],r['original'],r['sha256'],r['bytes'],'EXACT_SECRET_NATIVE355')
    for r in tools:add(r['path'],r['original'],r['sha256'],r['bytes'],'AUTHENTICATED_TOOL_OR_ANCESTRY')
    assert len(rows)==1403
    for r in integration_rows:
        add(str(Path(r['path']).relative_to(REPO)),r['path'],r['sha256'],r['bytes'],'OWN_SOURCE_SEAL')
    assert len(rows)==1424
    return [rows[k]for k in sorted(rows)]


def recheck(frame):
    for row in frame['captured']:checked(row)
    for row in frame['familyIndices']:family(row)
    normal_protection(frame['normalProtection'])
    for row in frame['copies']:
        p=checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']))
        assert stat.S_IMODE(p.stat().st_mode)==row['sourceMode']


def authorize(config_row):
    config=read(config_row)
    assert config['schemaVersion']==1 and config['state']=='CRYPTO_OWNER355_SECRET_STAGE_CONTROLLER_CONFIG_V1'
    root=read(config['rootAuthority']);own_index=root['externalControllerIndex']
    own_rows=family(own_index)
    assert root['externalControllerEntry']in own_rows
    refs=read(next(r for r in own_rows if r['path']==str(OWN/'references.json')))
    assert config['sourceIndex']==refs['integrationIndex']
    assert config['sourceIndex']['path']==str(INTEGRATION/'index.json')and config['sourceIndex']['sha256']==INTEGRATION_SHA
    integration_rows=family(config['sourceIndex'])
    integration_refs=read(next(r for r in integration_rows if r['path']==str(INTEGRATION/'references.json')))
    validate_root(root,own_index,integration_refs['sourcePeer'])
    assert root['stageEntry']in integration_rows
    captured=[config_row,config['rootAuthority'],*own_rows,*integration_rows]
    indices=[own_index,config['sourceIndex']]
    for item in integration_refs['families']:
        captured+=family(item['index']);indices.append(item['index'])
    for row in [integration_refs['mandatoryHistoryErratum'],integration_refs['normalProtection']]:checked(row);captured.append(row)
    normal=integration_refs['normalProtection'];captured+=normal_protection(normal)
    source_peer=root['independentSourceReview']
    if refs['actualIntegrationSourceReview']is not None:assert source_peer==refs['actualIntegrationSourceReview']
    data,rows=indexed_result(source_peer);validate_integration_peer(data);captured+=rows;indices.append(source_peer['index'])
    data,rows=indexed_result(root['externalControllerReview']);validate_controller_peer(data,own_index)
    captured+=rows;indices.append(root['externalControllerReview']['index'])
    assert root['genericMonitorIndex']==refs['monitorIndex']
    rows=family(root['genericMonitorIndex']);captured+=rows;indices.append(root['genericMonitorIndex'])
    assert root['genericMonitorEntry']in rows and root['genericMonitorEntry']==refs['monitorEntry']
    native=read(next(r for r in integration_rows if r['path']==str(INTEGRATION/'native-origins.json')))['files']
    tools=read(next(r for r in integration_rows if r['path']==str(INTEGRATION/'tool-origins.json')))['files']
    copies=expected_copies(native,tools,integration_rows)
    captured += [dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes'])for r in copies]
    frame=dict(config=config,root=root,captured=captured,familyIndices=indices,copies=copies,
               normalProtection=normal,monitor=root['genericMonitorEntry'])
    recheck(frame);return frame


def validate_terminal(terminal,authority):
    assert terminal['schemaVersion']==1 and terminal['authority']==authority
    assert terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone']is True and terminal['allObservedOwnedGroupsGone']is True
    for key in ['forcedCleanup','timeout']:assert terminal[key]is False
    for key in ['remainingObservedPids','errors','interruptedSignals','signals']:assert terminal[key]==[]
    assert terminal['stderr']['bytes']==0
    assert terminal['observedProcesses']and terminal['finalGroups']
    assert all(group['alive']is False for group in terminal['finalGroups'])
    return True


def validate_journal(value,frame):
    assert value['schemaVersion']==1 and value['state']=='SECRET_NATIVE355_SOURCE_STAGED_NOT_BUILT'
    assert value['sourceIndexSha256']==INTEGRATION_SHA and value['nativeSourceFiles']==355
    assert value['configuredSourceRoot']==SOURCE and value['workRoot']==WORK and value['freezeRoot']==FREEZE
    assert value['copies']==frame['copies']and len(value['copies'])==1424
    for key in ['nativeBuildExecuted','engineExecuted','operationalAdmission','metadataProjected']:assert value[key]is False
    expected=[['git','clone','--no-local','--no-checkout',str(REPO),SOURCE],['git','-C',SOURCE,'checkout','--detach','54b3329b3ce818fd1f244e871e9c259b63667cda']]
    assert [r['argv']for r in value['commands']]==expected
    assert all(r['returncode']==0 for r in value['commands'])
    return True


def main(config_row):
    assert __debug__ and sys.dont_write_bytecode
    assert not any(os.environ.get(k)for k in ['PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH'])
    frame=authorize(config_row);root=frame['root']
    for p in [OUT,Path(SOURCE),Path(WORK),Path(FREEZE),JOURNAL]:assert not p.exists()and not p.is_symlink()
    # Exact reviewed0af file/API, without importing its build main or changing globals.
    spec=importlib.util.spec_from_file_location('genuine_secret_stage_owned_monitor',checked(frame['monitor']))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    recheck(frame)
    OUT.mkdir(mode=0o700)
    argv=[sys.executable,'-B','-I',str(INTEGRATION/'stage.py'),INTEGRATION_SHA,json.dumps(frame['config']['rootAuthority'],separators=(',',':'))]
    try:
        terminal=module.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OUT,TIMEOUT,frame['config']['rootAuthority'])
    finally:
        recheck(frame)  # Failed/interrupted invocations retain raw monitor evidence and refuse drift.
    validate_terminal(terminal,frame['config']['rootAuthority'])
    for row in [terminal['stdout'],terminal['stderr']]:checked(row)
    journal=descriptor(JOURNAL);value=read(journal);validate_journal(value,frame)
    for row in frame['copies']:
        target=checked(dict(path=str(Path(SOURCE)/row['path']),sha256=row['sha256'],bytes=row['bytes']))
        original=checked(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']))
        assert stat.S_IMODE(target.stat().st_mode)==row['sourceMode']
        assert (target.stat().st_dev,target.stat().st_ino)!=(original.stat().st_dev,original.stat().st_ino)
    for p in [Path(WORK),Path(FREEZE)]:assert not p.exists()and not p.is_symlink()
    recheck(frame)
    print(json.dumps(dict(schemaVersion=1,state='SECRET_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1',
        actualJournal=journal,externalTerminal=descriptor(OUT/'terminal.json'),copies=1424,
        nativeSourceFiles=355,independentResultReviewRequired=True,nativeBuildExecuted=False,
        engineExecuted=False,operationalAdmission=False)),flush=True)


if __name__=='__main__':
    assert len(sys.argv)==2
    main(json.loads(sys.argv[1]))
