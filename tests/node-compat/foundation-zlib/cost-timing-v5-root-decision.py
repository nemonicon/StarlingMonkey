"""Bespoke read-only cost decision; no old proof helper or execution/adoption grant."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
PROOF = HERE / 'independent-cost-timing-v5-results-review-v1'


def row(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    h = hashlib.sha256()
    before = path.stat()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(data)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=after.st_size)


def verify(value):
    assert row(value['path']) == value
    return value


def read(value):
    verify(value)
    return json.loads(Path(value['path']).read_bytes())


def main():
    index = row(PROOF / 'index.json')
    assert index['sha256'] == '434ee6c7ba86d2009320884e6654ed10f68ba7e552f996f6c8e0f93b3ad483e5'
    family = read(index)
    names = {'index.json'}
    for item in family['files']:
        assert not Path(item['path']).is_absolute() and '..' not in Path(item['path']).parts
        names.add(item['path'])
        verify(dict(item, path=str(PROOF / item['path'])))
    assert len(family['files']) == 52
    assert {str(p.relative_to(PROOF)) for p in PROOF.rglob('*') if p.is_file()} == names
    result_row = row(PROOF / 'results.json')
    contract_row = row(PROOF / 'result-contract.json')
    assert result_row['sha256'] == '9cd3ef5717b72ed9b63a8c8187d0dd4776af94cf60c33db4b06a0d589a4242a3'
    assert contract_row['sha256'] == '5db7f9a8824f1783b981a875f26ace8cbd6c19aa5f7e813a5faa0fb092a0355a'
    result = read(result_row)
    contract = read(contract_row)
    assert result['schemaVersion'] == 1 and result['state'] == contract['requiredReviewState']
    assert result['verifiedPassed'] is True and contract['grantsExecutionOrAdoptionAuthority'] is False
    for key, value in contract['requiredFixedValues'].items():
        assert result[key] == value
    assert result['coverage'] == contract['requiredCoverage']
    for key, value in contract['requiredExactDescriptors'].items():
        assert result[key] == value
        verify(value)
    # Explicit timing role here; never send the new DATA to the old pilot-only helper.
    actual_index = read(result['actualIndex'])
    assert len(actual_index['files']) == 17642
    assert result['actualCalibrationReview'] == contract['requiredOriginalCalibrationReview']
    assert result['actualPreparedPlanReview'] == contract['requiredFreshV5PlanReview']
    for role in ('requiredOriginalCalibrationReview', 'requiredFreshV5PlanReview'):
        for value in contract[role].values():
            verify(value)
    for name, value in contract['requiredComponents'].items():
        assert result['artifacts'][name]['component'] == value
        verify(value)
    sizes = result['componentBytes']
    assert sizes == {name: value['bytes'] for name, value in contract['requiredComponents'].items()}
    provider, unused = result['numericalFindings']
    assert provider['comparison'] == 'same-engine-provider' and provider['aShorterByMedian'] == 27 and provider['bShorterByMedian'] == 3
    assert unused['comparison'] == 'unused-profile' and unused['pairDirections']['crosses-or-equals1'] == 24
    decision = dict(schemaVersion=1, state='ROOT_BOUNDED_CODEC_COST_DECISION_CONTINUE_NATIVE_CANDIDATE_NO_ADOPTION_V1',
        independentReview=dict(index=index, result=result_row, contract=contract_row), decisionSource=row(Path(__file__).resolve()),
        empiricalCostDataGate='passed for these exact artifacts and workload; no new execution',
        engineeringDecision='Continue the bounded synchronous native codec candidate through compatibility, combined-engine, host, preservation and release/adoption gates. Keep optional profile disabled by default until acceptance.',
        automaticProviderDispatchAdded=False, providerFindings=provider, unusedProfileFindings=unused,
        componentBytes=sizes, nativeMinusFflateOnBytes=sizes['native-on']-sizes['fflate-on'],
        nativeMinusFflateOffBytes=sizes['native-on']-sizes['fflate-off'], unusedNativeProfileIncrementBytes=sizes['fflate-on']-sizes['fflate-off'],
        resourceFindings=result['resourceFindings'], universalNativeSpeedup=False, statisticalSignificanceClaim=False,
        guestMemoryReductionEstablished=False, codecOnlyAllocationReductionEstablished=False, isolatedStartupReductionEstablished=False,
        correlatedSamplesPooled=False, controlsSubtracted=False,
        outstanding=['Resolve or explicitly bound all22 Node error deviations and source-coupled VERNUM.',
                     'Preserve six-sync-operation manifest, unsupported-operation behavior, input/output limits and no-import default.',
                     'Validate the actually selected combined engine on both target hosts and full release/preservation suites.',
                     'Measure guest allocation/high-water memory and isolated startup if claiming those benefits.',
                     'Reassess empirical cost if engine, codec/options, transport or workload changes.',
                     'Complete archive and independent adoption/acceptance gates before source promotion.'],
        genericPilotProofHelperModified=False, newReusableTimingProofApiAdmitted=False,
        limitations=result['limitations'], engineOrWorkerExecuted=False, operationalAdmission=False,
        sourcePromotionAllowed=False, runtimeAcceptanceClaim=False, fullRoadmapComplete=False)
    output = HERE / 'cost-timing-v5-root-decision.json'
    with output.open('x') as stream:
        json.dump(decision, stream, indent=2)
        stream.write('\n')
    print(json.dumps(row(output)))


if __name__ == '__main__':
    main()
