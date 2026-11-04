#!/usr/bin/env python3
"""Read/hash/JSON-only contract checks. No JS, codec, helpers or child processes."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent


def checked(row):
    p = Path(row['path'])
    before = p.lstat()
    assert stat.S_ISREG(before.st_mode) and not p.is_symlink(), str(p)
    data = p.read_bytes()
    after = p.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    assert len(data) == row['bytes']
    assert hashlib.sha256(data).hexdigest() == row['sha256'], str(p)
    return data


def validate(contract, ledger):
    assert contract['state'] == 'SOURCE_ONLY_UNAPPROVED_ZLIB_M0_13_NODE_DEVIATION_CONTRACT'
    for key in ['actionsExecuted', 'operationalAdmission', 'sourcePromotionIssued',
                'runtimeAcceptanceClaim', 'performanceClaim', 'errorParityClaim']:
        assert contract[key] is False, key
    for key in ['actionAuthority', 'approvedDecision', 'enginePins']:
        assert contract[key] is None, key
    assert contract['sourceOnly'] is True
    rows = contract['rows']
    assert len(rows) == 22
    assert len({r['index'] for r in rows}) == 22
    assert len({r['id'] for r in rows}) == 22
    original = {r['index']: r for r in ledger['rows']}
    assert set(original) == {r['index'] for r in rows}
    groups = {i: g for g in contract['groups'] for i in g['indices']}
    assert len(groups) == sum(len(g['indices']) for g in contract['groups']) == 22
    for r in rows:
        unchanged = {k: v for k, v in r.items() if k != 'proposedDisposition'}
        assert unchanged == original[r['index']], r['id']
        d = r['proposedDisposition']
        assert d['decisionState'] == 'UNAPPROVED_SOURCE_PROPOSAL'
        g = groups[r['index']]
        assert d['group'] == g['id'] and d['classification'] == g['classification']
        assert d['validationExpectation'] == g['proposal']
        assert 'message' not in r['profileErrorAsObserved']
    errno = [r for r in rows if r['comparisonDifferences'] == ['error.errno']]
    assert [r['index'] for r in errno] == [7, 10, 24, 27, 41, 44]
    assert len(rows) - len(errno) == 16
    assert sum(r['sourceDeviationValuePreserved'] is None for r in rows) == 11
    assert contract['counts'] == {
        'differentCases': 22, 'outcomeOrCode': 16, 'additionalErrnoOnly': 6,
        'originalNullDeviationDifferentCases': 11,
        'knownSuccessfulByteObservationsInPriorReview': 138,
        'constantDifferencesSeparateFrom22': 1}
    assert contract['constantDeviation']['unchangedHistoricalRuntimeBackendProof'] == {
        'verified': False, 'version': None, 'vernum': None}
    assert contract['constantDeviation']['node'] == 4865
    assert contract['constantDeviation']['observedProfile'] == 4880
    assert contract['constantDeviation']['sourceCoupledInferenceOnly'] is True
    assert contract['domain']['inputBytesMax'] == 1048576
    assert contract['domain']['outputBytesMax'] == 16777216


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    contract = json.loads((HERE / 'contract.proposal.json').read_text())
    inputs = json.loads((HERE / 'source-inputs.json').read_text())['files']
    assert len({r['path'] for r in inputs}) == len(inputs)
    captured = {r['path']: checked(r) for r in inputs}
    ledger = json.loads(captured[contract['sourceLedger']['path']])
    validate(contract, ledger)
    node_path = contract['rows'][0]['citations']['nodeOracle']['path']
    node = json.loads(captured[node_path])
    assert node['node'] == 'v22.14.0'
    assert node['nodeExecutableSha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    observed = 0
    for row in contract['rows']:
        assert node['cases'][row['index']]['id'] == row['id']
        assert node['cases'][row['index']]['node'] == row['nodeOutcomeAndErrorAsRecorded']
        for citation in row['citations']['guestRawObservations']:
            raw = json.loads(captured[citation['path']])
            assert raw['index'] == row['index'] and raw['id'] == row['id']
            assert raw['outcome'] == 'error'
            assert raw['error'] == row['profileErrorAsObserved']
            assert raw['partialOutputPublished'] is False and raw['inputImmutable'] is True
            fields = raw['error']['fields']
            if fields['errno']['own']:
                assert fields['errno']['type'] == 'number'
                number = fields['errno']['value']
                assert isinstance(number, int) and not isinstance(number, bool) and math.isfinite(number)
                assert fields['operation'] == {'own': False, 'type': 'undefined', 'value': None}
            else:
                assert fields['operation']['own'] and fields['operation']['type'] == 'string'
            observed += 1
        assert len(row['citations']['guestRawObservations']) == row['observationCount']
    # Each check rejects an actual contract-integrity regression, not codec behavior.
    negative = []
    mutations = {
        'missing-observed-difference': lambda x: x['rows'].pop(),
        'duplicate-row': lambda x: x['rows'].__setitem__(1, copy.deepcopy(x['rows'][0])),
        'rewrite-historical-null-deviation': lambda x: x['rows'][0].__setitem__('sourceDeviationValuePreserved', 'accepted'),
        'invent-unrecorded-guest-message': lambda x: x['rows'][0]['profileErrorAsObserved'].__setitem__('message', 'invented'),
        'unrecognized-classification': lambda x: x['rows'][0]['proposedDisposition'].__setitem__('classification', 'NODE_PARITY_PASSED'),
        'invent-action-authority': lambda x: x.__setitem__('actionAuthority', {}),
        'rewrite-historical-backend-proof': lambda x: x['constantDeviation']['unchangedHistoricalRuntimeBackendProof'].__setitem__('verified', True),
    }
    for name, mutate in mutations.items():
        changed = copy.deepcopy(contract)
        mutate(changed)
        try:
            validate(changed, ledger)
        except (AssertionError, KeyError):
            negative.append(name)
        else:
            raise AssertionError(name + ' unexpectedly admitted')
    for row in inputs:
        assert checked(row) == captured[row['path']]
    report = {
        'schemaVersion': 1, 'state': 'SOURCE_DATA_CONTRACT_CHECKS_PASSED',
        'inputFilesRehashedBeforeAndAfter': len(inputs),
        'unchangedLedgerRows': 22, 'actualErrorRawRecordsCompared': observed,
        'nodeOracleCasesCompared': 22, 'negativeCasesRejected': negative,
        'sourceOnly': True, 'codecLibraryNodeGuestOrHelperExecuted': False,
        'operationalAdmission': False, 'sourcePromotionIssued': False,
        'runtimeAcceptanceClaim': False, 'performanceClaim': False,
    }
    target = Path(args.output)
    with target.open('x') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
