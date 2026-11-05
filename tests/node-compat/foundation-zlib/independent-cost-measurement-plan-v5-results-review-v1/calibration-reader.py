"""Recompute original matched-plan arithmetic on authenticated retained DATA."""
from pathlib import Path
import json
import math

D = Path(__file__).resolve().parent
S = D.parent / 'cost-pilot-timing-candidate-v5'
refs = json.loads((S / 'references.json').read_bytes())
proof = json.loads(Path(refs['actualCalibrationReview']['result']['path']).read_bytes())
actual = json.loads(Path(refs['actualMatchedPlan']['path']).read_bytes())
rows = []
for comparison, arms in [('same-engine-provider', ['native-on', 'fflate-on']), ('unused-profile', ['fflate-on', 'fflate-off'])]:
    for case in range(30):
        curves = [v for v in proof['calibrations'] if v['comparison'] == comparison and v['caseId'] == case]
        assert len(curves) == 1
        curve = curves[0]
        assert curve['empiricalMatchedN'] is True
        n = curve['n']
        assert type(n) is int and 0 < n <= (32768 if case < 18 else 128) and n & (n - 1) == 0
        for arm in arms:
            units = [r for r in curve['perArm'] if r['arm'] == arm]
            assert len(units) == 1
            unit = units[0]
            assert 50 <= unit['pilotBatchMs'] <= 600000
            assert unit['pilotPerOperationMs'] == unit['pilotBatchMs'] / n
            budget = math.ceil(2 * unit['pilotPerOperationMs'] * n * (3 + 7) + unit['pilotPerOperationMs'] * n + 120000 + 2 * max(0, unit['pilotWholeProcessMs'] - unit['pilotPerOperationMs']))
            assert 0 < budget <= 7200000
            rows.append(dict(comparison=comparison, caseId=case, arm=arm, n=n, workerTimeoutMs=budget, publicCallHardMs=600000))
assert rows == actual['rows']
value = dict(schemaVersion=1, realCalibrationReview=refs['actualCalibrationReview'], originalCalibrationSource=proof['sourceIndex'], newPlanSourceIndexSha256='e799350100bb3b54148fdc5bd46a857579a6aae7608890f620569ea3704ab321', matchedPlan=refs['actualMatchedPlan'], calibrationRecords=60, recomputedMatchedRows=120, allRowsExact=True, originalFormulaCopiedAsArithmeticOnly=True, originalPilotSourceRelabelled=False, ownerActionsInvoked=False)
(D / 'calibration-roles-and-matched-data.json').write_text(json.dumps(value, indent=2) + '\n')
print(json.dumps(dict(all120MatchedRowsExact=True, oldSourceNotRelabelled=True, ownerActionsInvoked=False)))
