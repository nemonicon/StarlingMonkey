"""Root one-job normal-OFF build action; no engine or guest execution."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

REPO=Path('/Users/dan/dev/StarlingMonkey')
K=REPO/'tests/node-compat/foundation-crypto'
SOURCE=K/'ownership-secret-build-controller-candidate-v1'
PEER=K/'independent-ownership-secret-build-controller-source-review-v1'
MONITOR=K/'ownership-gc-build-controller-candidate-v1'
OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-normal-off-build-parent-external-root')


def row(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)


def family(p,expected):
    ix=row(p);assert ix['sha256']==expected;root=Path(p).parent;names=set()
    for r in json.loads(Path(p).read_bytes())['files']:
        n=r['path'];assert n not in names and not n.startswith('/')and all(x not in ('','.','..')for x in n.split('/'));names.add(n)
        assert row(root/n)==dict(r,path=str(root/n))
    assert not any(p.is_symlink()for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{'index.json'}
    return ix


def write(name,value):
    p=K/name
    with p.open('x')as f:f.write(json.dumps(value,indent=2)+'\n')
    return row(p)


def main():
    assert __debug__ and sys.dont_write_bytecode
    own=family(SOURCE/'index.json','c9573e416c76350a6ab169b0d5ddb2938883e9698620759b4285ee7a2fde3643')
    peer_ix=family(PEER/'index.json','65caf5b04b5045e1b9915c490b5972d25a208eb380e8d9e458db5a026b2dbd3a')
    peer=dict(index=peer_ix,result=row(PEER/'results.json'))
    review=json.loads((PEER/'results.json').read_bytes());assert review['controllerSourceIndexSha256']==own['sha256']and review['sourceReviewPassed']is True
    family(MONITOR/'index.json','0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
    root=json.loads((SOURCE/'root-authority.template.json').read_bytes())
    entry=row(SOURCE/'controller.py')
    root.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_NORMAL_OFF_BUILD_V1',buildAllowed=True,
        externalControllerIndex=own,externalControllerEntry=entry,workerEntry=entry,externalControllerReview=peer,
        rootCaller=row(Path(__file__).resolve()),rootCallerOutputRoot=str(OUT),rootCallerDeadlineSeconds=7200)
    root_row=write('ownership-secret-normal-off-build-v1-root-authority.json',root)
    cfg=json.loads((SOURCE/'config.template.json').read_bytes());cfg['rootAuthority']=root_row
    cfg_row=write('ownership-secret-normal-off-build-v1-root-config.json',cfg)
    assert not OUT.exists()
    spec=importlib.util.spec_from_file_location('genuine_secret_normal_build_parent_monitor',MONITOR/'monitor.py');monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
    environment={k:v for k,v in os.environ.items()if k not in ['PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH']}
    environment['PYTHONDONTWRITEBYTECODE']='1'
    OUT.mkdir(mode=0o700)
    terminal=monitor.monitor([sys.executable,'-B','-I',str(SOURCE/'controller.py'),'parent',json.dumps(cfg_row,separators=(',',':'))],str(REPO),environment,OUT,7200,root_row)
    assert terminal['rawExitCode']==0 and terminal['allObservedOwnedGroupsGone']is True
    assert terminal['timeout']is terminal['forcedCleanup']is False
    assert terminal['remainingObservedPids']==terminal['errors']==terminal['signals']==terminal['interruptedSignals']==[]
    assert terminal['stderr']['bytes']==0
    for r in [terminal['stdout'],terminal['stderr']]:assert row(r['path'])==r
    records=[json.loads(line)for line in Path(terminal['stdout']['path']).read_text().splitlines()]
    assert len(records)==2 and set(records[0])=={'pid','timeoutSeconds'}
    result=records[1];assert result['state']=='SECRET_NORMAL_OFF_BUILD_RAW_ZERO_UNREVIEWED_V1'
    actual=result['actualBuildResult'];assert row(actual['path'])==actual
    build=json.loads(Path(actual['path']).read_bytes())
    assert build['rawChildExitCode']==build['launcherExitCode']==0 and build['lifecycleComplete']is True
    assert build['ownedGroupCleanup']['complete']is True and build['ownedGroupCleanup']['events']==build['ownedGroupCleanup']['errors']==[]
    for key in ['engine','metadata']:assert row(build[key]['path'])==build[key]
    for r in [root_row,cfg_row]:assert row(r['path'])==r
    report=dict(schemaVersion=1,state='ROOT_OBSERVED_SECRET_NORMAL_OFF_BUILD_RAW_ZERO_REVIEW_PENDING_V1',rootAuthority=root_row,config=cfg_row,
        controllerSourceIndex=own,controllerSourceReview=peer,outerTerminal=row(OUT/'terminal.json'),controllerSummary=result,actualBuildResult=actual,
        engine=build['engine'],metadata=build['metadata'],rawControllerExitCode=0,rawBuildExitCode=0,allObservedOwnedGroupsGone=True,
        operationalElapsedSeconds=terminal['operationalElapsedSeconds'],independentBuildReviewRequired=True,
        nativeSourceFiles=355,changedNativeFiles=3,normalOffOnly=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
    report_row=write('ownership-secret-normal-off-build-v1-root-results.json',report)
    print(json.dumps(dict(result=report_row,engine=build['engine'],rawBuildExitCode=0,allObservedOwnedGroupsGone=True)),flush=True)


if __name__=='__main__':main()
