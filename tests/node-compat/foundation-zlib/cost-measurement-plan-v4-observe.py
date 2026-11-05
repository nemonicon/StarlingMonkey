"""Read-only collector correction: preserve relative publication rows explicitly."""
from pathlib import Path
import hashlib
import json

REPO=Path('/Users/dan/dev/StarlingMonkey')
Z=REPO/'tests/node-compat/foundation-zlib'
OUT=Path('/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v4-external-root')
PLAN=Path('/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v4')


def row(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def main():
    terminal_row=row(OUT/'terminal.json');t=json.loads((OUT/'terminal.json').read_bytes())
    assert t['rawExitCode']==0 and t['allObservedOwnedGroupsGone']is True
    assert t['timeout']is t['forcedCleanup']is False
    assert t['remainingObservedPids']==t['errors']==t['signals']==t['interruptedSignals']==[]
    assert t['stderr']['bytes']==0
    for r in [t['stdout'],t['stderr']]:assert row(r['path'])==r
    published=json.loads(Path(t['stdout']['path']).read_bytes())
    expected={'result':'prepared-plan.json','index':'index.json','completion':'completion.json'}
    assert set(published)==set(expected)
    absolute={}
    for kind,name in expected.items():
        raw=published[kind];assert set(raw)=={'path','sha256','bytes'}and raw['path']==name
        assert not (PLAN/name).is_symlink()
        absolute[kind]=dict(raw,path=str(PLAN/name))
        assert row(PLAN/name)==absolute[kind]
    assert {p.name for p in PLAN.iterdir()}==set(expected.values())
    index=json.loads((PLAN/'index.json').read_bytes());completion=json.loads((PLAN/'completion.json').read_bytes());plan=json.loads((PLAN/'prepared-plan.json').read_bytes())
    assert index==dict(schemaVersion=1,files=[published['result']])
    assert completion['result']==published['result']and completion['index']==published['index']and completion['rootAuthority']==t['authority']
    root=json.loads(Path(t['authority']['path']).read_bytes());assert row(t['authority']['path'])==t['authority']
    assert root['codecGuestPilotOrTimingAllowed']is False and root['dataPublicationAllowed']is True
    assert row(root['externalController']['path'])==root['externalController']and row(root['externalInvocation']['path'])==root['externalInvocation']
    assert plan['sourceIndexSha256']==root['sourceIndexSha256']=='b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1'
    assert len(plan['expected'])==90 and set(plan['artifacts'])=={'native-on','fflate-on','fflate-off'}
    assert plan['state']=='PREPARED_COMPACT_CODEC_MEASUREMENT_PLAN_DATA_ONLY_V1'and plan['actionAuthority']is False and plan['operationalAdmission']is False
    options_row=row(Z/'cost-measurement-plan-v4-root-options.json');options=json.loads(Path(options_row['path']).read_bytes())
    assert options['planAuthority']==t['authority']and options['sourceIndex']['sha256']==plan['sourceIndexSha256']
    report=dict(schemaVersion=1,state='ROOT_OBSERVED_READ_ONLY_CODEC_MEASUREMENT_PLAN_V4_COMPLETE_AFTER_COLLECTOR_CORRECTION',
        sourceIndex=options['sourceIndex'],sourceReview=options['sourceIndependentReview'],rootAuthority=t['authority'],rootOptions=options_row,
        externalTerminal=terminal_row,externalStdout=t['stdout'],externalStderr=t['stderr'],
        originalRelativePublishedRows=published,absoluteOutputDescriptors=absolute,preparedPlan=absolute['result'],index=absolute['index'],completion=absolute['completion'],
        actualReadOnlyParentExitCode=0,rootCallerToolSession=37441,rootCallerExitCode=1,
        rootCallerFailure='Post-publication collector resolved relative DurableOutput rows from repository cwd instead of declared plan output root.',
        collectorCorrection='Original relative rows retained unchanged; separate absolute descriptors verified under exact v4 outputRoot.',
        actionRepeated=False,allObservedOwnedGroupsGone=True,observedParentPid=t['pid'],operationalElapsedSeconds=t['operationalElapsedSeconds'],
        expectedRows=90,artifactArms=sorted(plan['artifacts']),actualFiles=3,independentPlanReview=None,
        generatedGuestCodecWorkerPilotTimingOrSourcePromotionInvoked=False,actionAuthority=False,operationalAdmission=False,runtimeAcceptanceClaim=False,
        dataCollector=row(Path(__file__).resolve()))
    with (Z/'cost-measurement-plan-v4-root-results.json').open('x')as f:f.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(result=row(Z/'cost-measurement-plan-v4-root-results.json'),preparedPlan=absolute['result'],actualReadOnlyParentExitCode=0,rootCallerExitCode=1,actionRepeated=False)))


if __name__=='__main__':main()
