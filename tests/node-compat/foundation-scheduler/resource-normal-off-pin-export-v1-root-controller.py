"""Root export-only action for the reviewed resource pin-tooling source."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

REPO=Path('/Users/dan/dev/StarlingMonkey')
S=REPO/'tests/node-compat/foundation-scheduler'
SOURCE=S/'resource-pin-tooling-candidate-v1'
PEER=S/'independent-resource-pin-tooling-source-review-v1'
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
OUT=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-pin-export-external-root')


def row(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)


def family(p,expected):
    ix=row(p);assert ix['sha256']==expected;root=Path(p).parent
    value=json.loads(Path(p).read_bytes());names=set()
    for r in value['files']:
        n=r['path'];assert n not in names and not n.startswith('/')and all(x not in ('','.','..')for x in n.split('/'));names.add(n)
        assert row(root/n)==dict(r,path=str(root/n))
    assert not any(p.is_symlink()for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{'index.json'}
    return ix


def write(name,value):
    p=S/name
    with p.open('x')as f:f.write(json.dumps(value,indent=2)+'\n')
    return row(p)


def main():
    own=family(SOURCE/'index.json','c55fd0fc10854b853dc57eee77c276857399a4e086d7bac23730b95a1ce66238')
    peer_ix=family(PEER/'index.json','78376ab01221110bc7c8b0fb2d1dcbb5ae1b6f9799bde37421cdebf93231e07a')
    peer=dict(index=peer_ix,result=row(PEER/'results.json'))
    monitor_ix=family(MONITOR/'index.json','0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
    refs=json.loads((SOURCE/'references.json').read_bytes())
    root=json.loads((SOURCE/'future-root-authority.template.json').read_bytes())
    root.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_PIN_TOOLING_PHASE_V1',phase='export',toolingIndex=own,
        candidateOutput='/private/tmp/starling-node-compat/scheduler-resource-v1-pin-tooling/export-normal-off-UNREVIEWED.json',
        sourceIndependentReview=peer,actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],exportAllowed=True,
        externalController=row(Path(__file__).resolve()),externalMonitorIndex=monitor_ix,externalParentDeadlineSeconds=600,externalOutputRoot=str(OUT))
    root_row=write('resource-normal-off-pin-export-v1-root-authority.json',root)
    cfg=json.loads((SOURCE/'future-config.template.json').read_bytes());cfg.update(toolingIndex=own,rootAuthority=root_row)
    cfg_row=write('resource-normal-off-pin-export-v1-root-config.json',cfg)
    assert not OUT.exists()
    spec=importlib.util.spec_from_file_location('genuine_resource_pin_export_owned_monitor',MONITOR/'monitor.py');monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
    environment={k:v for k,v in os.environ.items()if k not in ['PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH']}
    environment['PYTHONDONTWRITEBYTECODE']='1'
    assert row(refs['python']['path'])==refs['python']
    OUT.mkdir(mode=0o700)
    terminal=monitor.monitor([refs['python']['path'],'-B','-I',str(SOURCE/'action.py'),'export',json.dumps(cfg_row,separators=(',',':'))],str(REPO),environment,OUT,600,root_row)
    assert terminal['rawExitCode']==0 and terminal['allObservedOwnedGroupsGone']is True
    assert terminal['timeout']is terminal['forcedCleanup']is False
    assert terminal['signals']==terminal['errors']==terminal['interruptedSignals']==terminal['remainingObservedPids']==[]
    assert terminal['stderr']['bytes']==0
    for r in [terminal['stdout'],terminal['stderr']]:assert row(r['path'])==r
    result=json.loads(Path(terminal['stdout']['path']).read_bytes())
    assert result['state']=='RESOURCE342_NORMAL_OFF_PIN_CANDIDATE_EXPORTED_UNREVIEWED_V1'
    assert row(result['candidate']['path'])==result['candidate']
    actual=json.loads(Path(result['candidate']['path']).read_bytes())
    assert actual['reviewRequired']is True and actual['variants']['normal-off']['reviewRequired']is True
    assert all(actual['variants'][label]is None for label in ['normal-runtime','gc-off','disabled-off'])
    assert row(root_row['path'])==root_row and row(cfg_row['path'])==cfg_row
    report=dict(schemaVersion=1,state='ROOT_OBSERVED_RESOURCE342_NORMAL_OFF_PIN_EXPORT_RAW_ZERO_UNREVIEWED_V1',toolingIndex=own,sourceReview=peer,rootAuthority=root_row,config=cfg_row,
        externalTerminal=row(OUT/'terminal.json'),rawExporterExitCode=0,allObservedOwnedGroupsGone=True,operationalElapsedSeconds=terminal['operationalElapsedSeconds'],exportResult=result,
        candidate=result['candidate'],reviewRequired=True,otherThreeVariantsNull=True,independentExportReviewRequired=True,
        engineExecuted=False,bootstrapExecuted=False,componentOrGuestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
    report_row=write('resource-normal-off-pin-export-v1-root-results.json',report)
    print(json.dumps(dict(result=report_row,candidate=result['candidate'],rawExporterExitCode=0,allObservedOwnedGroupsGone=True)),flush=True)


if __name__=='__main__':main()
