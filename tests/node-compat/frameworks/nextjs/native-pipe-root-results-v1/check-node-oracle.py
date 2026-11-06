"""Portable DATA check of captured Node records; never launches a workload."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / 'oracle-capture'


def read(path):
    return json.loads(path.read_text())


def check_bytes(path, ref):
    assert not path.is_symlink() and path.is_file(), path
    data = path.read_bytes()
    assert len(data) == ref['bytes'] and hashlib.sha256(data).hexdigest() == ref['sha256'], path


def main():
    index = read(RAW / 'index.json')
    assert index['guestComparisonPerformed'] is False
    assert index['capturedCalls'] == 3 and index['capturedRecords'] == 36
    assert {r['path'] for r in index['files']} | {'index.json'} == {p.name for p in RAW.iterdir()}
    for ref in index['files']:
        assert Path(ref['path']).name == ref['path']
        check_bytes(RAW / ref['path'], ref)
    executed = HERE / 'launch-oracle.executed-v1.py'
    assert hashlib.sha256(executed.read_bytes()).hexdigest() == index['executedDriverSha256']
    authority = read(HERE / 'node-oracle-authority.json')
    assert authority['state'] == 'ROOT_NATIVE_PIPE_NODE_ORACLE_AUTHORIZED_V1'
    assert authority['nodeOracleAllowed'] is True
    for key in ['nativeBuildAllowed', 'guestAllowed', 'browserAllowed', 'externalDeploymentAllowed']:
        assert authority[key] is False
    assert authority['node']['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    source = HERE.parent / 'native-pipe-regression-v1'
    assert authority['sourceIndex']['sha256'] == index['sourceIndexSha256']
    check_bytes(source / 'index.json', authority['sourceIndex'])
    for ref in read(source / 'index.json')['files']:
        check_bytes(source / ref['path'], ref)
    observation = read(RAW / 'observation.json')
    assert observation['passed'] is True and observation['guestExecuted'] is False
    assert observation['cleanOwnedShutdown'] is True and observation['sourceInputsPreserved'] is True
    check_bytes(HERE / 'node-oracle-authority.json', observation['authority'])
    for key, filename in [('terminal', 'terminal.json'), ('stdout', 'stdout.log'), ('stderr', 'stderr.log')]:
        check_bytes(RAW / filename, observation[key])
    terminal = read(RAW / 'terminal.json')
    assert terminal['rawExitCode'] == 0
    assert terminal['parentOwnedGroupGone'] is True and terminal['allObservedOwnedGroupsGone'] is True
    assert terminal['timeout'] is False and terminal['forcedCleanup'] is False
    for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
        assert terminal[key] == []
    assert (RAW / 'stderr.log').read_bytes() == b''
    ids = json.loads((source / 'cases.mjs').read_text().split('Object.freeze(', 1)[1].split(');', 1)[0])
    lines = [json.loads(line) for line in (RAW / 'stdout.log').read_text().splitlines()]
    assert len(lines) == 4 and lines[0]['node'] == 'v22.14.0'
    assert lines[0]['candidateInstalled'] is False and lines[0]['guestExecuted'] is False
    for call, line in enumerate(lines[1:], 1):
        assert line['call'] == call and line['kind'] == 'string'
        value = json.loads(line['value'])
        assert value['suite'] == 'NATIVE_SIGNAL_PIPE_REGRESSION_V1'
        assert value['applicationImported'] is False and value['fullNextClaim'] is False
        assert value['call'] == call and value['caseCount'] == len(ids) == 12
        assert [r['id'] for r in value['records']] == ids
        assert all(r['completed'] is True for r in value['records'])
    print(json.dumps(dict(state='NODE_PIPE_REFERENCE_DATA_VERIFIED_V1', calls=3,
                          capturedRecords=36, guestComparisonPerformed=False,
                          originalLabelMistakePreserved=True, targetExecutedByReader=False)))


if __name__ == '__main__':
    main()
