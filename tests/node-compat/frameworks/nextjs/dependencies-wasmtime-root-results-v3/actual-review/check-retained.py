"""Portable, read-only DATA check. Standard library only; no workload calls."""
from pathlib import Path
import gzip, hashlib, json, re
HERE = Path(__file__).resolve().parent
def load(path):
    return json.loads(path.read_bytes())
index = load(HERE/'index.json')
expected = {row['path'] for row in index['files']}
actual = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p != HERE/'index.json'}
assert expected == actual, 'Closed indexed membership'
for row in index['files']:
    p = HERE/row['path']
    assert not p.is_symlink() and '..' not in p.relative_to(HERE).parts
    raw = p.read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], row['path']
mapping = load(HERE/'copy-map.json')
assert mapping['originalsBeforeFinalUnchanged'] is True
for row in mapping['files']:
    raw = (HERE/row['copy']).read_bytes()
    if row['compression'] == 'gzip':
        raw = gzip.decompress(raw)
    else:
        assert row['compression'] == 'none'
    original = row['original']
    assert len(raw) == original['bytes'] and hashlib.sha256(raw).hexdigest() == original['sha256'], row['copy']
ids = ['fs-and-commonjs-json', 'commonjs-execution', 'native-aliases', 'buffer-concat-codecs',
       'als-await', 'als-next-tick', 'als-immediate', 'als-timer', 'als-snapshot-bind',
       'als-exit', 'als-disable', 'vm-real-js-copyout', 'zlib-sync', 'zlib-transform',
       'rng-deployed-shapes', 'http-adapter']
def response(request, folder):
    raw = (folder/('response-'+str(request['ordinal'])+'.body')).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == request['rawBody']['sha256']
    body = json.loads(raw)
    assert body == request['body'] and request['status'] == 200 and request['passed'] is True
    assert body['marker'] == 'NEXT_NATIVE_DEPENDENCIES_OK'
    records = body['records']
    assert [r['id'] for r in records] == ids
    assert all(r['passed'] is True for r in records)
    assert set(records[0]['value']) == {'buildId'} and isinstance(records[0]['value']['buildId'], str) and records[0]['value']['buildId']
    for i in (1, 2, 4, 5, 6, 7, 8, 9, 10, 12, 13):
        assert records[i]['value'] is True
    assert records[3]['value'] == '616263' and records[11]['value'] == 'dependency:vm'
    assert records[14]['value'] == dict(bytes=8, filled=8, uuidVersion=4, secretValuesRetained=False)
    assert records[15]['value'] == dict(method=request['method'], pathname='/dependencies', bodyBytes=21 if request['method']=='POST' else 0)
    barriers = body['snapshotBarriers']
    assert barriers['deployedResetAttempted'] is False and barriers['deployedResnapshotAttempted'] is False
    assert barriers['nativeSnapshotGuardRuntimeProof'] is False
    return len(records)
review = load(HERE/'review.json')
assert review['reviewerWorkloadExecutions'] is False and review['fullNextAccepted'] is False
assert review['sameInstanceIdentityProved'] is False and review['snapshotResetOrGcProof'] is False
assert review['binaryCopies'] == 0 and review['fullApplicationCopies'] == 0
counts = []
for run in review['runs']:
    folder = HERE/run['id']
    result = load(folder/'result.json')
    terminal = load(folder/'monitor/terminal.json')
    observation = load(folder/'monitor/observation.json')
    assert observation['result'] == run['originalResult']
    assert terminal['rawExitCode'] == run['rawMonitorExit']
    assert terminal['parentOwnedGroupGone'] is True and terminal['allObservedOwnedGroupsGone'] is True
    assert terminal['timeout'] is False and terminal['forcedCleanup'] is False
    assert all(terminal[k] == [] for k in ('signals', 'interruptedSignals', 'remainingObservedPids', 'errors'))
    assert all(g['alive'] is False and g['signalAllowed'] is False for g in terminal['finalGroups'])
    assert result['server']['exit'] == dict(code=0, signal=None, error=None)
    assert result['server']['forcedCleanup'] is False and result['server']['sigintSent'] is True
    assert result['originalInputsPreserved'] is True and result['readonlyCopyPreserved'] is True
    assert observation['finalProtectionErrors'] == []
    assert [r['status'] for r in result['requests']] == run['statuses']
    entry = (folder/'input-entry.mjs').read_text()
    assert re.findall(r"check\('([^']+)'", entry) == ids
    count = sum(response(r, folder) for r in result['requests'] if r['status'] == 200)
    if run['id'] == 'normal-eof-pass':
        assert result['passed'] is True and result['errors'] == [] and observation['passed'] is True
        assert terminal['rawExitCode'] == 0 and result['semanticChecksPassed'] is True
        assert [r['method'] for r in result['requests']] == ['GET', 'GET', 'POST']
        assert run['statuses'] == [200, 200, 200] and count == 48
    else:
        assert result['passed'] is False and observation['passed'] is False
        assert terminal['rawExitCode'] == 1 and result['errors']
        assert any('not valid JSON' in e['message'] for e in result['errors'])
        stderr = (folder/'wasmtime.stderr.log').read_text()
        assert 'Dependency probe failed: als-snapshot-bind' in stderr if run['id']=='als-oracle-failure' else 'WASI HTTP stream failure: undefined' in stderr
        assert (run['statuses'],count) == ([500],0) if run['id']=='als-oracle-failure' else (run['statuses'],count) == ([200,200,500],32)
    counts.append(dict(id=run['id'], statuses=run['statuses'], retainedPassingRecords=count, rawMonitorExit=terminal['rawExitCode']))
oracle = load(HERE/'inputs/default-node-als-profile-models.json')
assert oracle['nodeVersion'] == 'v22.14.0' and oracle['nodeExecArgv'] == [] and oracle['nodeOptionsPresent'] is False
assert oracle['alsOracle']['oldMarkerPredicate'] is False
assert all(value is True for value in oracle['alsOracle']['corrected'].values())
assert oracle['alsOracle']['separateExitUndefined'] is True
print(json.dumps(dict(passed=True, indexedFiles=len(expected), retainedTextCopies=len(mapping['files']),
                     baselineControls=16, baselineResponses=3, baselineRecords=48, runs=counts,
                     workloadExecutions=False, fullNextAccepted=False,
                     sameInstanceIdentityProved=False, snapshotResetOrGcProof=False)))
