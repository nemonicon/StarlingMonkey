"""Read-only correction for the Root caller's multi-record stdout reader."""
from pathlib import Path
import hashlib
import json
import stat

REPO=Path('/Users/dan/dev/StarlingMonkey')
K=REPO/'tests/node-compat/foundation-crypto'
OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-stage-parent-external-root')


def row(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)


def read(d):
    assert row(d['path'])==d
    return json.loads(Path(d['path']).read_bytes())


def clean(t):
    assert t['rawExitCode']==0 and t['allObservedOwnedGroupsGone']is True
    assert t['timeout']is t['forcedCleanup']is False
    assert t['remainingObservedPids']==t['errors']==t['signals']==t['interruptedSignals']==[]
    assert t['stderr']['bytes']==0
    for r in [t['stdout'],t['stderr']]:assert row(r['path'])==r


def main():
    assert __debug__
    root_row=row(K/'ownership-secret-stage-v1-root-authority.json');authority=read(root_row)
    assert row(authority['rootCaller']['path'])==authority['rootCaller']
    outer_row=row(OUT/'terminal.json');outer=read(outer_row);clean(outer)
    assert outer['authority']==root_row
    records=[json.loads(line)for line in Path(outer['stdout']['path']).read_text().splitlines()]
    assert len(records)==2 and set(records[0])=={'pid','timeoutSeconds'}
    launch,result=records
    assert launch['timeoutSeconds']==600 and result['state']=='SECRET_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1'
    inner=read(result['externalTerminal']);clean(inner)
    assert inner['pid']==launch['pid']and inner['authority']==root_row
    journal=read(result['actualJournal'])
    assert journal['state']=='SECRET_NATIVE355_SOURCE_STAGED_NOT_BUILT'
    assert journal['sourceIndexSha256']==authority['sourceIndexSha256']
    assert result['copies']==len(journal['copies'])==1424
    destination=Path(authority['destination'])
    names=set()
    for r in journal['copies']:
        name=r['path'];assert name not in names and not name.startswith('/')and all(x not in ('','.','..')for x in name.split('/'));names.add(name)
        target=destination/name;original=Path(r['original'])
        for p in [target,original]:
            assert not p.is_symlink()and p.is_file()
            assert row(p)==dict(path=str(p),sha256=r['sha256'],bytes=r['bytes'])
            assert stat.S_IMODE(p.stat().st_mode)==r['sourceMode']
        assert (target.stat().st_dev,target.stat().st_ino)!=(original.stat().st_dev,original.stat().st_ino)
    policy=json.loads((K/'ownership-secret-integration-candidate-v1/policy.json').read_bytes())
    manifest=policy['expectedNativeSourceManifest'];assert len(manifest)==355
    for r in manifest:assert row(destination/r['path'])['sha256']==r['sha256']
    assert (destination/'.git/HEAD').read_text().strip()=='54b3329b3ce818fd1f244e871e9c259b63667cda'
    assert not (destination/'.git/objects/info/alternates').exists()
    def object_inodes(root):
        return {(p.stat().st_dev,p.stat().st_ino)for p in (root/'.git/objects').rglob('*')if p.is_file()}
    source_objects=object_inodes(REPO);target_objects=object_inodes(destination)
    assert source_objects and target_objects and not source_objects.intersection(target_objects)
    refs=json.loads((K/'ownership-secret-integration-candidate-v1/references.json').read_bytes())
    protected=read(refs['normalProtection'])
    for r in protected['frozenCopyEntries']:assert row(r['path'])=={k:r[k]for k in ['path','sha256','bytes']}
    for r in protected['originals']:
        for key in ['original','frozen']:assert row(r[key]['path'])==r[key]
    frozen=Path(protected['freezeReceipt']['path']).parent
    assert {p.relative_to(frozen).as_posix()for p in frozen.rglob('*')if p.is_file()}==set(protected['requiredNormalFreezeMembership'])
    assert len(protected['originals'])==1387 and len(protected['requiredNormalFreezeMembership'])==1391
    for p in [Path(authority['workRoot']),Path(authority['freezeRoot'])]:assert not p.exists()
    observed=dict(schemaVersion=1,state='ROOT_OBSERVED_SECRET_NATIVE355_SOURCE_STAGE_COMPLETED_AFTER_REPORT_READER_CORRECTION_V1',
        rootAuthority=root_row,config=row(K/'ownership-secret-stage-v1-root-config.json'),
        controllerSourceIndex=authority['externalControllerIndex'],controllerSourceReview=authority['externalControllerReview'],
        outerTerminal=outer_row,innerTerminal=result['externalTerminal'],actualJournal=result['actualJournal'],
        rootCallerToolSession=35883,rootCallerExitCode=1,rootCallerFailure='Post-action JSON reader expected one document; monitor emitted launch and result lines.',
        actualControllerExitCode=0,actualStageExitCode=0,sourceStageRepeated=False,
        observedControllerPid=outer['pid'],observedStagePid=inner['pid'],outerOperationalSeconds=outer['operationalElapsedSeconds'],stageOperationalSeconds=inner['operationalElapsedSeconds'],
        copies=1424,nativeSourceFiles=355,copyOriginalHashModeAndDistinctInodeChecksPassed=True,allObservedOwnedGroupsGone=True,
        detachedBaseline='54b3329b3ce818fd1f244e871e9c259b63667cda',gitObjectInodesDisjoint=True,
        sourceGitObjectFiles=len(source_objects),destinationGitObjectFiles=len(target_objects),normalFrozenMembers=1391,normalOriginalReferences=1387,
        normalProtectionRechecked=True,workAndFreezeAbsent=True,reportReader=row(Path(__file__).resolve()),
        independentStageReviewRequired=True,nativeBuildExecuted=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False)
    with (K/'ownership-secret-stage-v1-root-results.json').open('x')as f:f.write(json.dumps(observed,indent=2)+'\n')
    print(json.dumps(dict(result=row(K/'ownership-secret-stage-v1-root-results.json'),actualControllerExitCode=0,actualStageExitCode=0,copies=1424,allObservedOwnedGroupsGone=True)))


if __name__=='__main__':main()
