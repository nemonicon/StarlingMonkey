"""Root read-only prerequisite audit and compact DATA publication only."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

REPO=Path('/Users/dan/dev/StarlingMonkey')
Z=REPO/'tests/node-compat/foundation-zlib'
SOURCE=Z/'cost-pilot-timing-candidate-v4'
PEER=Z/'independent-cost-pilot-timing-v4-source-review-v1'
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
OUT=Path('/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v4-external-root')


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
    p=Z/name
    with p.open('x')as f:f.write(json.dumps(value,indent=2)+'\n')
    return row(p)


def main():
    own=family(SOURCE/'index.json','b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1')
    peer_ix=family(PEER/'index.json','19594c5930f8c274fe20a03aa7dbe18c329417618815a00dbfcabf8da30633b7')
    peer=dict(index=peer_ix,result=row(PEER/'results.json'))
    review=json.loads((PEER/'results.json').read_bytes());assert review['sourceIndexSha256']==own['sha256']and review['ownerActionsInvoked']is False
    family(MONITOR/'index.json','0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
    root=json.loads((SOURCE/'future-plan-authority.template.json').read_bytes())
    root.update(sourceIndexSha256=own['sha256'],sourceIndependentReview=peer,dataPublicationAllowed=True,
        externalController=row(Path(__file__).resolve()),externalInvocation=row(Z/'cost-measurement-plan-v4-root-invoke.mjs'),externalParentDeadlineSeconds=900,externalOutputRoot=str(OUT))
    root_row=write('cost-measurement-plan-v4-root-authority.json',root)
    options_row=write('cost-measurement-plan-v4-root-options.json',dict(sourceIndex=own,sourceIndependentReview=peer,planAuthority=root_row))
    assert not OUT.exists()and not Path(root['outputRoot']).exists()
    refs=json.loads((SOURCE/'references.json').read_bytes());assert row(refs['node']['path'])==refs['node']
    spec=importlib.util.spec_from_file_location('genuine_readonly_codec_plan_owned_monitor',MONITOR/'monitor.py');monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
    environment={k:v for k,v in os.environ.items()if not k.startswith(('NODE_COMPAT_','NAPI_RS_'))and k not in ['PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH']}
    environment.update(PYTHONDONTWRITEBYTECODE='1',BINARYEN_CORES='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='1',NODE_COMPAT_TOOLCHAIN='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/toolchain',NODE_COMPAT_COMPONENTIZE_MODULE='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/packager/src/componentize.js')
    OUT.mkdir(mode=0o700)
    terminal=monitor.monitor([refs['node']['path'],str(Z/'cost-measurement-plan-v4-root-invoke.mjs'),json.dumps(options_row,separators=(',',':'))],str(REPO),environment,OUT,900,root_row)
    assert terminal['rawExitCode']==0 and terminal['allObservedOwnedGroupsGone']is True
    assert terminal['timeout']is terminal['forcedCleanup']is False
    assert terminal['remainingObservedPids']==terminal['errors']==terminal['signals']==terminal['interruptedSignals']==[]
    assert terminal['stderr']['bytes']==0
    for r in [terminal['stdout'],terminal['stderr']]:assert row(r['path'])==r
    published=json.loads(Path(terminal['stdout']['path']).read_bytes())
    for r in published.values():assert row(r['path'])==r
    plan=json.loads(Path(published['result']['path']).read_bytes())
    assert len(plan['expected'])==90 and set(plan['artifacts'])=={'native-on','fflate-on','fflate-off'}
    assert plan['sourceIndexSha256']==own['sha256']and plan['actionAuthority']is False
    report=dict(schemaVersion=1,state='ROOT_OBSERVED_READ_ONLY_CODEC_MEASUREMENT_PLAN_V4_COMPLETE_UNREVIEWED',sourceIndex=own,sourceReview=peer,rootAuthority=root_row,rootOptions=options_row,externalTerminal=row(OUT/'terminal.json'),rawParentExitCode=0,allObservedOwnedGroupsGone=True,operationalElapsedSeconds=terminal['operationalElapsedSeconds'],published=published,preparedPlan=published['result'],expectedRows=90,artifactArms=sorted(plan['artifacts']),independentPlanReview=None,generatedGuestCodecWorkerPilotTimingOrSourcePromotionInvoked=False,actionAuthority=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
    report_row=write('cost-measurement-plan-v4-root-results.json',report)
    print(json.dumps(dict(result=report_row,preparedPlan=published['result'],rawParentExitCode=0)),flush=True)


if __name__=='__main__':main()
