"""Numerical DATA analysis of retained observations; no benchmark/helper calls."""
from pathlib import Path
import csv
import json

P = Path(__file__).resolve().parent
D = Path('/private/tmp/starling-node-compat/zlib-cost-timing-v5')
observations = json.loads((P / 'replayed-observations.json').read_bytes())['observations']
actual = json.loads((D / 'aggregate-observations.json').read_bytes())
plan = json.loads(Path('/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v5/prepared-plan.json').read_bytes())
cases = {(v['arm'], v['caseId']): v for v in plan['expected']}


def median(values):
    ordered = sorted(values)
    assert len(ordered) in (3, 7)
    return ordered[len(ordered) // 2]


groups, comparisons, process_rows = [], [], []
for comparison, arms in [('same-engine-provider', ['native-on', 'fflate-on']), ('unused-profile', ['fflate-on', 'fflate-off'])]:
    for case in range(30):
        selected = [v for v in observations if v['comparison'] == comparison and v['caseId'] == case]
        assert len(selected) == 6
        arm_groups, arm_stats = [], []
        for arm in arms:
            workers = [v for v in selected if v['arm'] == arm]
            assert len(workers) == 3 and {v['repetition'] for v in workers} == {0, 1, 2}
            units, process_stats = [], []
            for worker in workers:
                ns = [int(v['elapsedNs']) for v in worker['measuredSamples']]
                assert len(ns) == 7 and all(n > 0 for n in ns)
                middle = median(ns)
                unit = dict(n=worker['n'], withinWorkerMedianMs=middle / 1e6, allSevenSamples=worker['measuredSamples'], processResources=worker['processResources'], inputBytesPerOperation=worker['inputBytesPerOperation'], outputBytesPerOperation=worker['outputBytesPerOperation'], compressedBytesPerOperation=worker['compressedBytesPerOperation'], compressedToRawRatio=worker['compressedToRawRatio'])
                units.append(unit)
                resource = worker['processResources']
                row = dict(comparison=comparison, caseId=case, caseName=cases[(arm, case)]['caseName'], arm=arm, repetition=worker['repetition'], side=worker['side'], jobId=worker['jobId'], pid=worker['pid'], n=worker['n'], samplesNs=ns, withinWorkerMedianNs=middle, sampleMinNs=min(ns), sampleMaxNs=max(ns), operationsPerSecond=worker['n'] * 1e9 / middle, uncompressedBytesPerSecond=None if worker['logicalUncompressedBytesPerOperation'] == 0 else worker['logicalUncompressedBytesPerOperation'] * worker['n'] * 1e9 / middle, logicalUncompressedBytesPerOperation=worker['logicalUncompressedBytesPerOperation'], inputBytesPerOperation=worker['inputBytesPerOperation'], outputBytesPerOperation=worker['outputBytesPerOperation'], compressedBytesPerOperation=worker['compressedBytesPerOperation'], processMaxRssKilobytes=resource['nodePublicMaxRssKilobytes'], processRssBoundaryBytes=[v['rssBytes'] for v in resource['boundarySamples']], combinedReviewedEsmTlaLoadNs=int(resource['reviewedEsmTlaLoadNs']), wholeProcessMs=worker['wholeProcessMs'], controlsNs=[int(v['elapsedNs']) for v in worker['rawControls']])
                process_stats.append(row)
                process_rows.append(row)
            arm_groups.append(dict(arm=arm, independentFreshProcessUnits=units, pooledWithinWorkerSamplesTreatedIndependent=False))
            medians = [v['withinWorkerMedianNs'] for v in process_stats]
            middle = median(medians)
            e = cases[(arm, case)]
            arm_stats.append(dict(arm=arm, n=workers[0]['n'], direction=e['direction'], processUnits=process_stats, medianOfThreeProcessMedianNs=middle, processMedianMinNs=min(medians), processMedianMaxNs=max(medians), operationsPerSecond=workers[0]['n'] * 1e9 / middle, uncompressedBytesPerSecond=None if e['logicalBytes'] == 0 else e['logicalBytes'] * workers[0]['n'] * 1e9 / middle, inputBytesPerOperation=e['inputBytes'], outputBytesPerOperation=e['outputBytes'], logicalUncompressedBytesPerOperation=e['logicalBytes'], component=plan['artifacts'][arm]['component'], processMaxRssKilobytes=[v['processMaxRssKilobytes'] for v in process_stats], combinedReviewedEsmTlaLoadNs=[v['combinedReviewedEsmTlaLoadNs'] for v in process_stats]))
        groups.append(dict(comparison=comparison, caseId=case, arms=arm_groups))
        A, B = arm_stats
        assert A['n'] == B['n']
        paired = []
        for repetition in range(3):
            a, = [v for v in A['processUnits'] if v['repetition'] == repetition]
            b, = [v for v in B['processUnits'] if v['repetition'] == repetition]
            paired.append(dict(repetition=repetition, order='BA' if repetition == 1 else 'AB', aJobId=a['jobId'], bJobId=b['jobId'], aProcessMedianNs=a['withinWorkerMedianNs'], bProcessMedianNs=b['withinWorkerMedianNs'], bElapsedOverAElapsed=b['withinWorkerMedianNs'] / a['withinWorkerMedianNs']))
        ratios = [v['bElapsedOverAElapsed'] for v in paired]
        comparisons.append(dict(comparison=comparison, caseId=case, caseName=cases[(arms[0], case)]['caseName'], direction=A['direction'], n=A['n'], A=A, B=B, paired=paired, ratioMeaning='B elapsed divided by A elapsed; above1 means A used less observed batch time', ratioOfArmMedianNs=B['medianOfThreeProcessMedianNs'] / A['medianOfThreeProcessMedianNs'], medianOfThreePairedRatios=median(ratios), pairedRatioMin=min(ratios), pairedRatioMax=max(ratios), pairedDirection='all-A-shorter' if all(r > 1 for r in ratios) else 'all-B-shorter' if all(r < 1 for r in ratios) else 'crosses-or-equals1', controlSubtraction=False, statisticalSignificanceClaim=False))
recomputed = dict(schemaVersion=1, groups=groups, workerCount=360, codecBatchCalls=3600, rawN1ControlOperations=2160, controlsSubtracted=False, sameEngineProviderAndUnusedProfileSeparate=True, guestHeapOrCapacityClaim=False, universalPerformanceWinClaim=False)
assert recomputed == actual
assert len(process_rows) == 360 and len(comparisons) == 60
for filename, value in [('recomputed-aggregate.json', recomputed), ('paired-statistics.json', dict(schemaVersion=1, comparisons=comparisons, independentProcessUnitsPerArm=3, correlatedSamplesPerProcess=7, controlsSubtracted=False, codecBatchPayloadArraysRetained=False, statisticalSignificanceClaim=False)), ('process-statistics.json', dict(schemaVersion=1, processes=process_rows, processScope='whole Node process including source authentication and loader overhead; not guest heap'))]:
    (P / filename).write_text(json.dumps(value, indent=2) + '\n')
with (P / 'paired-statistics.csv').open('w') as stream:
    fields = ['comparison', 'caseId', 'caseName', 'direction', 'n', 'A', 'B', 'aMedianBatchMs', 'bMedianBatchMs', 'ratioBOverA', 'medianPairedRatio', 'minPairedRatio', 'maxPairedRatio', 'pairedDirection', 'logicalBytesPerOperation', 'aOutputBytes', 'bOutputBytes', 'aMedianProcessMaxRssReportedKB', 'bMedianProcessMaxRssReportedKB']
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    for r in comparisons:
        a, b = r['A'], r['B']
        writer.writerow(dict(comparison=r['comparison'], caseId=r['caseId'], caseName=r['caseName'], direction=r['direction'], n=r['n'], A=a['arm'], B=b['arm'], aMedianBatchMs=a['medianOfThreeProcessMedianNs'] / 1e6, bMedianBatchMs=b['medianOfThreeProcessMedianNs'] / 1e6, ratioBOverA=r['ratioOfArmMedianNs'], medianPairedRatio=r['medianOfThreePairedRatios'], minPairedRatio=r['pairedRatioMin'], maxPairedRatio=r['pairedRatioMax'], pairedDirection=r['pairedDirection'], logicalBytesPerOperation=a['logicalUncompressedBytesPerOperation'], aOutputBytes=a['outputBytesPerOperation'], bOutputBytes=b['outputBytesPerOperation'], aMedianProcessMaxRssReportedKB=median(a['processMaxRssKilobytes']), bMedianProcessMaxRssReportedKB=median(b['processMaxRssKilobytes'])))
summary = []
for name in ['same-engine-provider', 'unused-profile']:
    rows = [v for v in comparisons if v['comparison'] == name]
    summary.append(dict(comparison=name, A=rows[0]['A']['arm'], B=rows[0]['B']['arm'], ratioBOverARange=[min(v['ratioOfArmMedianNs'] for v in rows), max(v['ratioOfArmMedianNs'] for v in rows)], aShorterByMedian=sum(v['ratioOfArmMedianNs'] > 1 for v in rows), bShorterByMedian=sum(v['ratioOfArmMedianNs'] < 1 for v in rows), pairDirections={k:sum(v['pairedDirection'] == k for v in rows) for k in ['all-A-shorter', 'all-B-shorter', 'crosses-or-equals1']}, smallestRatios=[dict(caseId=v['caseId'], caseName=v['caseName'], ratio=v['ratioOfArmMedianNs'], pairedRange=[v['pairedRatioMin'],v['pairedRatioMax']]) for v in sorted(rows, key=lambda v:v['ratioOfArmMedianNs'])[:3]], largestRatios=[dict(caseId=v['caseId'], caseName=v['caseName'], ratio=v['ratioOfArmMedianNs'], pairedRange=[v['pairedRatioMin'],v['pairedRatioMax']]) for v in sorted(rows, key=lambda v:v['ratioOfArmMedianNs'])[-3:]]))
result = dict(schemaVersion=1, actualAggregateWholeObjectMatched=True, comparisonCases=60, workers=360, timedSamples=2520, warmups=1080, n1Controls=2160, processMediansNotPooled=True, summaries=summary, componentBytes={arm:plan['artifacts'][arm]['component']['bytes'] for arm in plan['artifacts']}, emptyLogicalRowsHaveNullByteThroughput=True, ownerActionsInvoked=False)
(P / 'numerical-audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
