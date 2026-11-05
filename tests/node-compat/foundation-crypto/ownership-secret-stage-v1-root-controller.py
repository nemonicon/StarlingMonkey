"""Root source-stage action only, using the reviewed controller unchanged."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

REPO=Path('/Users/dan/dev/StarlingMonkey')
K=REPO/'tests/node-compat/foundation-crypto'
CONTROLLER=K/'ownership-secret-stage-controller-candidate-v1'
PEER=K/'independent-ownership-secret-stage-controller-source-review-v1'
OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-stage-parent-external-root')


def row(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)


def family(path,expected):
    ix=row(path);assert ix['sha256']==expected
    value=json.loads(Path(path).read_bytes());root=Path(path).parent
    names=set()
    for r in value['files']:
        name=r['path'];assert name not in names and not name.startswith('/')and all(p not in ('','.','..')for p in name.split('/'))
        names.add(name);assert row(root/name)==dict(r,path=str(root/name))
    assert not any(p.is_symlink()for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{'index.json'}
    return ix


def write(name,value):
    p=K/name
    with p.open('x')as f:f.write(json.dumps(value,indent=2)+'\n')
    return row(p)


def main():
    assert __debug__ and sys.dont_write_bytecode
    own=family(CONTROLLER/'index.json','7758e1a722043a3ecc0ba6d3e95eb3a6f53ddf1dcfaa684460c801cf10e60a12')
    peer_ix=family(PEER/'index.json','ec9df97a83672f961eae721ab455bb309ff70a857be12204e8a3953ca99e5804')
    peer=dict(index=peer_ix,result=row(PEER/'results.json'))
    review=json.loads((PEER/'results.json').read_bytes())
    assert review['controllerSourceIndexSha256']==own['sha256']and review['sourceReviewPassed']is True
    refs=json.loads((CONTROLLER/'references.json').read_bytes())
    monitor_ix=refs['monitorIndex'];family(monitor_ix['path'],monitor_ix['sha256'])
    assert row(refs['monitorEntry']['path'])==refs['monitorEntry']
    root=json.loads((CONTROLLER/'root-authority.template.json').read_bytes())
    root.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_SOURCE_STAGE_V1',
        sourceStageAllowed=True,externalControllerIndex=own,
        externalControllerEntry=row(CONTROLLER/'controller.py'),externalControllerReview=peer,
        rootCaller=row(Path(__file__).resolve()),rootCallerOuterDeadlineSeconds=900,
        rootCallerOuterOutputRoot=str(OUT),rootScope='Source staging only; no compiler, native build, engine, guest, pin or runtime action')
    root_row=write('ownership-secret-stage-v1-root-authority.json',root)
    config=json.loads((CONTROLLER/'config.template.json').read_bytes());config['rootAuthority']=root_row
    config_row=write('ownership-secret-stage-v1-root-config.json',config)
    assert not OUT.exists()
    spec=importlib.util.spec_from_file_location('genuine_root_secret_stage_parent_monitor',refs['monitorEntry']['path'])
    monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
    environment={k:v for k,v in os.environ.items()if k not in ['PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH']}
    environment.update(PYTHONDONTWRITEBYTECODE='1',GIT_TERMINAL_PROMPT='0')
    OUT.mkdir(mode=0o700)
    terminal=monitor.monitor([sys.executable,'-B','-I',str(CONTROLLER/'controller.py'),json.dumps(config_row,separators=(',',':'))],str(REPO),environment,OUT,900,root_row)
    assert row(root_row['path'])==root_row and row(config_row['path'])==config_row
    assert terminal['rawExitCode']==0 and terminal['allObservedOwnedGroupsGone']is True
    assert terminal['remainingObservedPids']==terminal['errors']==terminal['signals']==terminal['interruptedSignals']==[]
    assert terminal['timeout']is terminal['forcedCleanup']is False
    assert terminal['stderr']['bytes']==0
    child_result=json.loads(Path(terminal['stdout']['path']).read_bytes())
    assert child_result['state']=='SECRET_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1'and child_result['copies']==1424
    result=dict(schemaVersion=1,state='ROOT_OBSERVED_SECRET_NATIVE355_SOURCE_STAGE_RAW_ZERO_V1',
        rootAuthority=root_row,config=config_row,controllerSourceIndex=own,controllerSourceReview=peer,
        outerTerminal=row(OUT/'terminal.json'),controllerResult=child_result,
        rawExitCode=0,allObservedOwnedGroupsGone=True,operationalElapsedSeconds=terminal['operationalElapsedSeconds'],
        independentStageReviewRequired=True,nativeBuildExecuted=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False)
    result_row=write('ownership-secret-stage-v1-root-results.json',result)
    print(json.dumps(dict(rawExitCode=0,result=result_row,copies=1424,allObservedOwnedGroupsGone=True)),flush=True)


if __name__=='__main__':main()
