"""One owned pinned-Node reference run; no engine or guest execution."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
AUTHORITY = HERE / 'node-oracle-authority.json'


def row(path):
    path = Path(path)
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    authority = json.loads(AUTHORITY.read_text())
    ar = row(AUTHORITY)
    assert authority['state'] == 'ROOT_NATIVE_PIPE_NODE_ORACLE_AUTHORIZED_V1'
    assert authority['nodeOracleAllowed'] is True
    assert all(authority[k] is False for k in ['nativeBuildAllowed', 'guestAllowed', 'browserAllowed', 'externalDeploymentAllowed'])

    def protect():
        assert row(AUTHORITY) == ar
        for ref in [authority['node'], authority['monitor'], authority['sourceIndex']]:
            assert row(ref['path']) == ref
        index_path = Path(authority['sourceIndex']['path'])
        index = json.loads(index_path.read_text())
        names = [r['path'] for r in index['files']]
        assert len(names) == len(set(names))
        assert set(names) | {'index.json'} == {p.relative_to(index_path.parent).as_posix() for p in index_path.parent.rglob('*') if p.is_file()}
        for ref in index['files']:
            path = index_path.parent / ref['path']
            assert not path.is_symlink() and path.resolve() == path
            assert row(path) == dict(ref, path=str(path))

    protect()
    output = Path(authority['outputRoot'])
    output.mkdir(mode=0o700)
    spec = importlib.util.spec_from_file_location('original_owned_pipe_oracle_monitor', authority['monitor']['path'])
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
    env.update(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C')
    source = Path(authority['sourceIndex']['path']).parent
    terminal = monitor.monitor([authority['node']['path'], str(source / 'node-oracle.mjs')], str(source), env, output, 60, ar)
    protect()
    clean = terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and not terminal['timeout'] and not terminal['forcedCleanup'] and all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    assert clean and (output / 'stderr.log').read_bytes() == b''
    lines = [json.loads(x) for x in (output / 'stdout.log').read_text().splitlines()]
    assert len(lines) == 4
    assert lines[0]['kind'] == 'node-oracle-identity' and lines[0]['node'] == 'v22.14.0'
    assert lines[0]['candidateInstalled'] is False and lines[0]['guestExecuted'] is False
    ids = json.loads((source / 'cases.mjs').read_text().split('Object.freeze(', 1)[1].split(');', 1)[0])
    for call, line in enumerate(lines[1:], 1):
        assert line['call'] == call and line['kind'] == 'string'
        value = json.loads(line['value'])
        assert value['call'] == call and value['caseCount'] == len(ids) == 12
        assert [r['id'] for r in value['records']] == ids
        assert all(r['completed'] is True for r in value['records'])
    observation = dict(schemaVersion=1, state='ACTUAL_NATIVE_PIPE_NODE_ORACLE_CAPTURED_V1', passed=True,
                       oracleRecordsCaptured=36, calls=3, casesPerCall=12, guestExecuted=False,
                       authority=ar, sourceIndex=authority['sourceIndex'], terminal=row(output / 'terminal.json'),
                       stdout=row(output / 'stdout.log'), stderr=row(output / 'stderr.log'),
                       cleanOwnedShutdown=True, sourceInputsPreserved=True)
    with (output / 'observation.json').open('x') as handle:
        handle.write(json.dumps(observation, indent=2) + '\n')
    print(json.dumps(observation), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
