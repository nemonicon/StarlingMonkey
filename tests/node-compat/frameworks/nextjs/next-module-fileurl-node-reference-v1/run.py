"""One owned pinned-Node reference, with fresh physical fixture copies."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'next-module-fileurl-probe-candidate-v1'
OUTPUT = Path('/private/tmp/starling-node-compat/next-module-fileurl-node-reference-v1-first')
NODE = Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
MONITOR = HERE.parents[2] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    assert row(NODE)['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
    # The actual monitor descriptor below is checked before any copy/process.
    assert not OUTPUT.exists() and not OUTPUT.is_symlink()
    assert shutil.disk_usage(OUTPUT.parent).free >= 1073741824
    index = json.loads((SOURCE / 'index.json').read_text())
    assert row(SOURCE / 'index.json')['sha256'] == 'c355260ccfffd59a5d31468ee26cd4c40d3fd3aeaad37dfe75024c0f37ca018b'
    for item in index['files']:
        assert row(SOURCE / item['path']) == dict(item, path=str(SOURCE / item['path']))
    plan = json.loads((SOURCE / 'plan.json').read_text())
    os.umask(0o077)
    OUTPUT.mkdir(mode=0o700)
    fixture_root = OUTPUT / 'fixtures'
    fixture_root.mkdir(mode=0o700)
    copies = []
    for item in plan['fixtureFiles']:
        source = Path(item['source']['path'])
        assert row(source) == item['source']
        target = fixture_root / item['relativePath']
        assert target.parent == fixture_root
        with target.open('xb') as handle:
            handle.write(source.read_bytes())
        target.chmod(0o444)
        assert target.stat().st_nlink == 1 and (source.stat().st_dev, source.stat().st_ino) != (target.stat().st_dev, target.stat().st_ino)
        assert row(target)['sha256'] == item['source']['sha256']
        copies.append(dict(source=item['source'], target=row(target), mode=0o444))
    fixture_root.chmod(0o555)
    authority = dict(state='ROOT_PINNED_NODE_CJS_FILEURL_REFERENCE_V1', sourceIndex=row(SOURCE / 'index.json'),
        control=row(HERE / 'control.cjs'), launcher=row(Path(__file__).resolve()), node=row(NODE), monitor=row(MONITOR),
        fixtures=copies, guestExecuted=False, networkAllowed=False, capSeconds=120,
        scope='Natural genuine CJS import(node:path/fileURL), canonical host fixture URL; no guest path emulation or full-profile parity.')
    authority_path = OUTPUT / 'authority.json'
    with authority_path.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    logs = OUTPUT / 'owned-monitor'
    logs.mkdir(mode=0o700)
    spec = importlib.util.spec_from_file_location('genuine_reference_owned_monitor', MONITOR)
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
    env.update(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C')
    terminal = monitor.monitor([str(NODE), str(HERE / 'control.cjs'), str(fixture_root)], str(HERE), env, logs, 120, row(authority_path))
    clean = terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    clean = clean and terminal['timeout'] is terminal['forcedCleanup'] is False
    clean = clean and all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    for copy in copies:
        target = Path(copy['target']['path'])
        assert row(target) == copy['target'] and target.stat().st_mode & 0o777 == copy['mode']
    assert fixture_root.stat().st_mode & 0o777 == 0o555
    assert row(HERE / 'control.cjs') == authority['control'] and row(Path(__file__).resolve()) == authority['launcher']
    result = dict(state='PINNED_NODE_FILEURL_REFERENCE_COMPLETED_DATA_PENDING_V1',
        authority=row(authority_path), terminal=row(logs / 'terminal.json'), rawExitCode=terminal['rawExitCode'],
        ownedClean=clean, fixturesPreserved=True, passed=terminal['rawExitCode'] == 0 and clean,
        guestExecuted=False, guardOrInteropAccepted=False)
    with (OUTPUT / 'result.json').open('x') as handle:
        handle.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
