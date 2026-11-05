"""Root owned controller for actual read-only JS bootstrap observation only."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
K = REPO / 'tests/node-compat/foundation-crypto'
MONITOR = REPO / 'tests/node-compat/foundation-stream-consumers/http-host-controller-candidate-v2'
OUT = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-bootstrap-api-v1-external-root')


def row(path):
    raw = Path(path).read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def read(descriptor):
    assert row(descriptor['path']) == descriptor
    return json.loads(Path(descriptor['path']).read_bytes())


def main():
    assert __debug__ and sys.dont_write_bytecode
    assert not any(os.environ.get(k) for k in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH'))
    monitor_index = row(MONITOR / 'index.json')
    assert monitor_index['sha256'] == '71b7f8e54ae2e21d6673d054a20efa7b1e00409d22d8af7c5b064ad9a6380ddf'
    index = read(monitor_index)
    names = set()
    for member in index['files']:
        assert member['path'] not in names
        names.add(member['path'])
        assert row(MONITOR / member['path']) == dict(member, path=str(MONITOR / member['path']))
    assert {p.relative_to(MONITOR).as_posix() for p in MONITOR.rglob('*') if p.is_file()} == names | {'index.json'}
    assert not any(p.is_symlink() for p in MONITOR.rglob('*'))
    cli_terminal = row(Path('/private/tmp/starling-node-compat/crypto-owner355-gc-pin-tooling-v1-bootstrap-external-root/terminal.json'))
    terminal = read(cli_terminal)
    assert terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] is True
    assert terminal['remainingObservedPids'] == [] and terminal['errors'] == []
    assert terminal['timeout'] is False and terminal['forcedCleanup'] is False
    assert terminal['interruptedSignals'] == []
    frame = read(terminal['stdout'])
    assert frame['state'] == 'ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_BOOTSTRAP_PASSED_V1'
    assert frame['operationalAdmission'] is False and frame['guestExecuted'] is False
    config = row(K / 'ownership-gc-v2-bootstrap-v1-root-config.json')
    assert config['sha256'] == 'd4e0f9915150e29fd5d1bbd940870e25c16a7573485863be4c1022263c131107'
    node = dict(path='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',
                sha256='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0', bytes=108619024)
    assert row(node['path']) == node
    assert not OUT.exists() and not Path('/private/tmp/starling-node-compat/crypto-owner355-gc-bootstrap-api-v1').exists()
    authority = dict(schemaVersion=1, state='ROOT_APPROVED_CRYPTO_OWNER355_GC_BOOTSTRAP_API_OBSERVATION_V1',
                     issuedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     entry=row(K / 'ownership-gc-v2-bootstrap-v1-observe.mjs'), controller=row(Path(__file__).resolve()),
                     node=node, bootstrapConfig=config, actualCliTerminal=cli_terminal,
                     externalMonitorIndex=monitor_index, externalMonitorEntry=row(MONITOR / 'controller.py'),
                     externalParentDeadlineSeconds=2400, externalOutputRoot=str(OUT),
                     outputRoot='/private/tmp/starling-node-compat/crypto-owner355-gc-bootstrap-api-v1',
                     bootstrapApiAllowed=True, engineExecuted=False, guestAllowed=False,
                     keyOperationsAllowed=False, gcWorkloadAllowed=False, operationalAdmission=False,
                     scope='Genuine JS GC bootstrap API plus its internal and explicit stable rechecks; read-only native verification only')
    authority_path = K / 'ownership-gc-v2-bootstrap-v1-api-root-authority.json'
    with authority_path.open('x') as stream:
        stream.write(json.dumps(authority, indent=2) + '\n')
    authority_row = row(authority_path)
    spec = importlib.util.spec_from_file_location('genuine_reviewed_gc_api_monitor', MONITOR / 'controller.py')
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    OUT.mkdir(mode=0o700)
    argv = [node['path'], authority['entry']['path'], json.dumps(authority_row, separators=(',', ':'))]
    result = monitor.monitor(argv, str(REPO), {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, OUT, 2400, authority_row)
    assert read(authority_row) == authority
    assert result['rawExitCode'] == 0 and result['allObservedOwnedGroupsGone'] is True
    assert result['remainingObservedPids'] == [] and result['errors'] == []
    assert result['timeout'] is False and result['forcedCleanup'] is False and result['interruptedSignals'] == []
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
