"""Reported process resource and raw control DATA; no heap/codec/host actions."""
from pathlib import Path
import json

P = Path(__file__).resolve().parent
rows = json.loads((P / 'paired-statistics.json').read_bytes())['comparisons']
def mid(values):
    assert len(values) == 3
    return sorted(values)[1]
resource_rows, control_rows, summaries = [], [], []
for r in rows:
    a, b = r['A'], r['B']
    resource_rows.append(dict(comparison=r['comparison'], caseId=r['caseId'], caseName=r['caseName'], n=r['n'], A=a['arm'], B=b['arm'], aMaxRssReportedKilobytes=a['processMaxRssKilobytes'], bMaxRssReportedKilobytes=b['processMaxRssKilobytes'], bMedianMaxRssOverA=mid(b['processMaxRssKilobytes']) / mid(a['processMaxRssKilobytes']), aCombinedLoadNs=a['combinedReviewedEsmTlaLoadNs'], bCombinedLoadNs=b['combinedReviewedEsmTlaLoadNs'], aBoundaryRssBytes=[v['processRssBoundaryBytes'] for v in a['processUnits']], bBoundaryRssBytes=[v['processRssBoundaryBytes'] for v in b['processUnits']]))
    for arm in [a,b]:
        labels = ['consume-before','copy-consume-before','harness-before','consume-after','copy-consume-after','harness-after']
        assert all(len(v['controlsNs']) == 6 for v in arm['processUnits'])
        control_rows.append(dict(comparison=r['comparison'], caseId=r['caseId'], caseName=r['caseName'], arm=arm['arm'], n=1, primaryMatchedN=r['n'], labels=labels, threeProcessControlsNs=[v['controlsNs'] for v in arm['processUnits']], medianAcrossThreeProcessesByControlNs=[mid([v['controlsNs'][i] for v in arm['processUnits']]) for i in range(6)], primaryBatchMedianNs=arm['medianOfThreeProcessMedianNs'], controlsSubtracted=False))
for comp in ['same-engine-provider','unused-profile']:
    values=[v for v in resource_rows if v['comparison']==comp]
    ratios=[v['bMedianMaxRssOverA'] for v in values]
    summaries.append(dict(comparison=comp, bOverAReportedMaxRssRatioRange=[min(ratios),max(ratios)], casesBReportedMaxRssHigher=sum(v>1 for v in ratios), casesBReportedMaxRssLower=sum(v<1 for v in ratios), ratiosCross1=min(ratios)<1<max(ratios)))
components=json.loads((P/'numerical-audit.json').read_bytes())['componentBytes']
value=dict(schemaVersion=1, resourceScope='reported whole Node process: source authentication, parser/binding/load, runtime and host evidence overhead; not guest heap or codec-only allocation', maxRssUnit='kilobytes as reported and labelled by Node22 resourceUsage API', boundaryRssUnit='bytes', loadScope='combined artifact hashes/parser/binding/direct ESM top-level initialization/instantiation/post-load hashes; no separate compile/instantiate or physically cold startup claim', caseRows=resource_rows, summaries=summaries, componentsBytes=components, sameFflateBundleProfileOnMinusOffComponentBytes=components['fflate-on']-components['fflate-off'], differentProviderSameEngineFflateMinusNativeComponentBytes=components['fflate-on']-components['native-on'], guestHeapCapacityAllocatorOrNativeGcCountObserved=False, ownerActionsInvoked=False)
(P/'resource-audit.json').write_text(json.dumps(value,indent=2)+'\n')
(P/'control-statistics.json').write_text(json.dumps(dict(schemaVersion=1,caseArmRows=control_rows,totalRawN1Controls=2160,threeBeforeAndThreeAfterPerWorker=True,controlsSubtracted=False,controlSevenSampleArms=False,controlTimingsNotEquivalentToCodecOnlyOverhead=True),indent=2)+'\n')
print(json.dumps(dict(resourceCases=len(resource_rows),controlCaseArms=len(control_rows),resourceSummaries=summaries,components=components,ownerActionsInvoked=False)))
