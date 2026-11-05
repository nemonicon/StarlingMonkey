"""Root validation-only pins and separate read-only CLI/API bootstrap action."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import os

REPO=Path('/Users/dan/dev/StarlingMonkey')
S=REPO/'tests/node-compat/foundation-scheduler'
SOURCE=S/'resource-pin-tooling-candidate-v1'
SOURCE_PEER=S/'independent-resource-pin-tooling-source-review-v1'
EXPORT_PEER=S/'independent-resource-normal-off-pin-export-review-v1'
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
PREFIX=Path('/private/tmp/starling-node-compat')


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
    p=S/name
    with p.open('x')as f:f.write(json.dumps(value,indent=2)+'\n')
    return row(p)


def clean(t,authority):
    assert t['authority']==authority and t['rawExitCode']==0 and t['allObservedOwnedGroupsGone']is True
    assert t['timeout']is t['forcedCleanup']is False
    assert t['remainingObservedPids']==t['errors']==t['signals']==t['interruptedSignals']==[]
    assert t['stderr']['bytes']==0
    for r in [t['stdout'],t['stderr']]:assert row(r['path'])==r


def main():
    own=family(SOURCE/'index.json','c55fd0fc10854b853dc57eee77c276857399a4e086d7bac23730b95a1ce66238')
    source_peer=dict(index=family(SOURCE_PEER/'index.json','78376ab01221110bc7c8b0fb2d1dcbb5ae1b6f9799bde37421cdebf93231e07a'),result=row(SOURCE_PEER/'results.json'))
    export_peer=dict(index=family(EXPORT_PEER/'index.json','b552683cac7b0e95d5f68bfddb6e8b539282fb64a848521e8f4db29f449cfcc0'),result=row(EXPORT_PEER/'results.json'))
    proof=json.loads((EXPORT_PEER/'results.json').read_bytes());assert proof['verifiedPassed']is True and proof['rawExporterExitCode']==0
    candidate=proof['candidate'];assert row(candidate['path'])==candidate
    assert candidate['sha256']=='9387992565714b300ea083577758cc7f4e9723bd05c43c4db12aae6b3db45256'
    original=json.loads(Path(candidate['path']).read_bytes());pins=copy.deepcopy(original)
    pins.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_VALIDATION_PINS_V1',reviewRequired=False)
    pins['variants']['normal-off'].update(state='reviewed-scheduler-resource342-normal-off-freeze-v1',reviewRequired=False)
    restored=copy.deepcopy(pins);restored['state']=original['state'];restored['reviewRequired']=original['reviewRequired'];restored['variants']['normal-off']['state']=original['variants']['normal-off']['state'];restored['variants']['normal-off']['reviewRequired']=True
    assert restored==original and all(pins['variants'][k]is None for k in ['normal-runtime','gc-off','disabled-off'])
    pin_row=write('reviewed-resource-normal-off-native-pins-v1.json',pins)
    review=json.loads((SOURCE/'future-root-pin-review.template.json').read_bytes())
    review.update(reviewedPinsSha256=pin_row['sha256'],toolingIndex=own,actualExportCandidate=candidate,independentExportReview=export_peer)
    review_row=write('reviewed-resource-normal-off-native-pin-root-review-v1.json',review)
    refs=json.loads((SOURCE/'references.json').read_bytes())
    root=json.loads((SOURCE/'future-root-authority.template.json').read_bytes())
    root.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_PIN_TOOLING_PHASE_V1',phase='bootstrap',toolingIndex=own,sourceIndependentReview=source_peer,
        actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],actualExportCandidate=candidate,independentExportReview=export_peer,
        reviewedPins=pin_row,rootPinReview=review_row,bootstrapAllowed=True,externalController=row(Path(__file__).resolve()),externalNodeCaller=row(S/'resource-normal-off-bootstrap-v1-root-invoke.mjs'))
    root_row=write('resource-normal-off-bootstrap-v1-root-authority.json',root)
    cfg=json.loads((SOURCE/'future-config.template.json').read_bytes());cfg.update(toolingIndex=own,rootAuthority=root_row)
    cfg_row=write('resource-normal-off-bootstrap-v1-root-config.json',cfg)
    family(MONITOR/'index.json','0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
    spec=importlib.util.spec_from_file_location('genuine_resource_readonly_bootstrap_monitor',MONITOR/'monitor.py');monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
    environment={k:v for k,v in os.environ.items()if k not in ['PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH']}
    environment['PYTHONDONTWRITEBYTECODE']='1'
    for k in ['python','node']:assert row(refs[k]['path'])==refs[k]
    outputs=[]
    commands=[('cli',[refs['python']['path'],'-B','-I',str(SOURCE/'action.py'),'bootstrap',json.dumps(cfg_row,separators=(',',':'))]),('api',[refs['node']['path'],str(S/'resource-normal-off-bootstrap-v1-root-invoke.mjs'),json.dumps(cfg_row,separators=(',',':'))])]
    for name,argv in commands:
        out=PREFIX/('scheduler-resource-v1-bootstrap-'+name+'-external-root');out.mkdir(mode=0o700)
        terminal=monitor.monitor(argv,str(REPO),environment,out,900,root_row);clean(terminal,root_row)
        frame=json.loads(Path(terminal['stdout']['path']).read_bytes());assert frame['state']=='RESOURCE342_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V1'
        outputs.append(dict(kind=name,terminal=row(out/'terminal.json'),stdout=terminal['stdout'],frame=frame))
    assert outputs[0]['frame']==outputs[1]['frame']
    frame=outputs[0]['frame'];assert frame['metadataDescriptor']==refs['metadata']and frame['engine']==refs['engine']and len(frame['selectedManifests'])==9
    assert frame['pin']==pins['variants']['normal-off']and frame['engineExecuted']is False and frame['componentOrGuestExecuted']is False
    for r in [root_row,cfg_row,pin_row,review_row,candidate]:assert row(r['path'])==r
    summary=dict(schemaVersion=1,state='ROOT_OBSERVED_RESOURCE342_NORMAL_OFF_READONLY_CLI_AND_API_BOOTSTRAP_RAW_ZERO_V1',rootAuthority=root_row,config=cfg_row,reviewedPins=pin_row,rootPinReview=review_row,sourceIndex=own,sourceReview=source_peer,exportReview=export_peer,
        cliTerminal=outputs[0]['terminal'],apiTerminal=outputs[1]['terminal'],cliWholeFrame=outputs[0]['stdout'],apiWholeFrame=outputs[1]['stdout'],wholeFramesEqual=True,selectedManifestCount=9,engine=refs['engine'],metadata=refs['metadata'],
        actualPythonBootstrapCalls=4,apiInitialPlusInternalAndExplicitRecheck=True,allObservedOwnedGroupsGone=True,independentBootstrapReviewRequired=True,engineExecuted=False,componentOrGuestExecuted=False,runtimeAcceptanceClaim=False,operationalAdmission=False)
    report=write('resource-normal-off-bootstrap-v1-root-results.json',summary)
    print(json.dumps(dict(result=report,wholeFramesEqual=True,actualPythonBootstrapCalls=4)),flush=True)


if __name__=='__main__':main()
