"""Finite normal-OFF scheduler342 source/build guard; standard library only."""
from pathlib import Path
import hashlib,json,os,stat,sys

REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/resource-build-controller-candidate-v1'
PROPOSAL=REPO/'tests/node-compat/foundation-scheduler/resource-integration-candidate-v1'
SOURCE=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-source')
WORK=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-build')
BUILD_OUTPUT=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-normal-off-build-root')
EXTERNAL=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-normal-off-build-external-root')
SOURCE_SHA='20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414'
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'

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

def validate_root(root,own_index):
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_BUILD_V1'
    assert root['phase']=='build'and root['variant']=='normal-off'and root['sourceIndexSha256']==SOURCE_SHA
    assert root['buildAllowed']is True and root['gcStress']is False and root['entropyMode']=='OFF'
    assert root['configuredSourceRoot']==str(SOURCE)and root['workRoot']==str(WORK)and root['buildOutputRoot']==str(BUILD_OUTPUT)and root['externalOutputRoot']==str(EXTERNAL)
    assert root['nativeSourceFiles']==342 and root['externalEmbeddingSources']==3 and root['webTimersEnabled']is True
    assert root['externalParentDeadlineSeconds']==7200 and root['jobs']==1 and root['buildType']=='Release'and root['oomTesting']is False
    assert root['requiredStartFreeBytes']==2147483648 and root['stopBelowFreeBytes']==838860800
    assert root['controllerIndex']==own_index and own_index['path']==str(OWN/'index.json')
    assert root['controllerEntry']['path']==str(OWN/'controller.py')
    for n in('stageAllowed','gcReconfigureAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','componentAllowed','guestAllowed','engineExecutionAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'):
        assert root[n]is False
    for n in('actualBuildResult','engine','metadata','actualNormalFreeze','independentNormalFreezeReview','runtimeAction'):
        assert root[n]is None

def validate_stage(root,staged,proof,observation,terminal):
    assert staged['schemaVersion']==1 and staged['state']=='RESOURCE342_SOURCE_STAGED_UNREVIEWED_V1'
    assert staged['sourceIndex']['sha256']==SOURCE_SHA and staged['destination']==str(SOURCE)and staged['baseline']==BASE
    assert staged['nativeFiles']==342 and staged['nativeReplacements']==2 and len(staged['copies'])==501 and staged['buildOrGuestInvoked']is False
    assert proof['schemaVersion']==1 and proof['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_SOURCE_STAGE_REVIEW_PASSED_V1'and proof['verifiedPassed']is True
    assert proof['sourceIndexSha256']==SOURCE_SHA and proof['actualStageResult']==root['actualStageResult']and proof['rootObservation']==root['actualStageRootObservation']
    assert observation['schemaVersion']==1 and observation['state']=='ROOT_OBSERVED_SCHEDULER_RESOURCE342_SOURCE_STAGE_PASSED_V1'and observation['rootObservedToolRawExitCode']==0
    assert observation['sourceIndex']==staged['sourceIndex']and observation['actualStageResult']==root['actualStageResult']and observation['configuredSourceRoot']==str(SOURCE)
    assert observation['copiedRows']==501 and observation['nativeSourceFiles']==342 and observation['nativeAfterimages']==2 and observation['unchangedNativeFiles']==340
    assert observation['buildInvoked']is False and observation['engineExecuted']is False and observation['componentOrGuestInvoked']is False
    assert terminal['rawExitCode']==0 and terminal['authority']==staged['rootAuthority']==observation['rootAuthority']
    assert terminal['parentOwnedGroupGone']is True and terminal['allObservedOwnedGroupsGone']is True and terminal['remainingObservedPids']==[]
    assert terminal['forcedCleanup']is False and terminal['timeout']is False and terminal['errors']==[]and terminal['interruptedSignals']==[]

def validate_peer(value,own_index):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert value['controllerSourceIndexSha256']==own_index['sha256']and value['resourceSourceIndexSha256']==SOURCE_SHA
    assert value['sourceOnly']is True and value['sourceReviewPassed']is True
    for n in('ownerActionsInvoked','hostActionsInvoked','nativeBuildActionsInvoked'):assert value[n]is False

def recheck(captured,families):
    for r in captured:checked(r)
    for ix in families:family(ix)

def authorize(config_row):
    assert __debug__ and sys.dont_write_bytecode
    assert not any(os.environ.get(k)for k in('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH'))
    config=read(config_row);root=read(config['rootAuthority']);own_index=config['controllerIndex'];validate_root(root,own_index)
    assert config['sourceIndex']==dict(path=str(PROPOSAL/'index.json'),sha256=SOURCE_SHA,bytes=5390)
    own=family(own_index);assert root['controllerEntry']in own
    source=family(config['sourceIndex']);captured=[config_row,config['rootAuthority'],*own,*source];indices=[own_index,config['sourceIndex']]
    refs=read(next(r for r in own if r['path']==str(OWN/'references.json')))
    for item in refs['families']:captured+=family(item['index']);indices.append(item['index'])
    for r in refs['files']:checked(r);captured.append(r)
    source_peer=refs['sourceReview'];assert root['sourceIndependentReview']==source_peer
    assert source_peer['index']in captured and source_peer['result']in captured
    p=read(source_peer['result']);assert p['state']=='INDEPENDENT_SCHEDULER_RESOURCE_INTEGRATION_SOURCE_REVIEW_PASSED_V1'and p['sourceIndexSha256']==SOURCE_SHA and p['sourceOnly']is True and p['sourceReviewPassed']is True and p['ownerActionsInvoked']is False
    # Genuine future stage proof pair; NULL refuses before any custom helper or output.
    pair=root['independentStageReview'];assert pair==refs['actualStageReview'];peers=family(pair['index']);assert pair['result']in peers;captured+=peers;indices.append(pair['index'])
    assert root['actualStageResult']==refs['actualStageResult']and root['actualStageRootObservation']==refs['actualStageRootObservation']
    staged=read(root['actualStageResult']);observation=read(root['actualStageRootObservation']);terminal_row=observation['externalParentTerminal'];assert terminal_row in captured
    validate_stage(root,staged,read(pair['result']),observation,read(terminal_row))
    # Reconstruct exactly the 501 stage targets, without reinterpreting prep paths.
    plan=read(next(r for r in source if r['path']==str(PROPOSAL/'stage-inputs.json')));targets={r['target']:r['original']for r in plan['files']}
    assert len(targets)==467
    for r in source:targets[str(PROPOSAL.relative_to(REPO))+'/'+str(Path(r['path']).relative_to(PROPOSAL))]=r
    for c in plan['nativeAfterimageReplacements']:targets[c['path']]=next(r for r in source if r['path']==str(PROPOSAL/'native'/c['path']))
    targets['tests/node-compat/build-engine.sh']=next(r for r in source if r['path']==str(PROPOSAL/'proposed/tests/node-compat/build-engine.sh'))
    assert len(targets)==501 and len({r['path']for r in staged['copies']})==501
    for item in staged['copies']:
        path=Path(item['path']);name=path.relative_to(SOURCE).as_posix();original=targets.pop(name);assert item['original']==original
        checked(original);current=dict(original,path=str(path));checked(current)
        assert path.stat().st_mode&0o777==Path(original['path']).stat().st_mode&0o777
        assert(path.stat().st_dev,path.stat().st_ino)!=(Path(original['path']).stat().st_dev,Path(original['path']).stat().st_ino)
        captured.extend([original,current])
    assert not targets
    policy=read(next(r for r in source if r['path']==str(PROPOSAL/'policy.json')))
    assert len(policy['expectedNativeSourceManifest'])==342
    for r in policy['expectedNativeSourceManifest']:
        path=SOURCE/r['path'];current=dict(path=str(path),sha256=r['sha256'],bytes=path.stat().st_size);checked(current);captured.append(current)
    own_peer=root['controllerIndependentReview'];review_rows=family(own_peer['index']);assert own_peer['result']in review_rows;validate_peer(read(own_peer['result']),own_index);captured+=review_rows;indices.append(own_peer['index'])
    recheck(captured,indices)
    return dict(config=config,root=root,captured=captured,families=indices,ownRows=own,sourceRows=source,refs=refs)
