"""One bounded host-Node in-memory model test; no Next or cache filesystem."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'next-portable-cache-handler-candidate-v1'
OUTPUT = Path('/private/tmp/starling-node-compat/next-portable-cache-model-v1-first')
NODE = Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
MONITOR = HERE.parents[2] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def write_new(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


def main():
    assert row(NODE)['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
    assert not OUTPUT.exists() and not OUTPUT.is_symlink()
    nodes = sorted(SOURCE.iterdir())
    assert len(nodes) == 7 and all(p.is_file() and not p.is_symlink() and p.stat().st_nlink == 1 for p in nodes)
    refs = [row(p) for p in nodes]
    os.umask(0o077)
    OUTPUT.mkdir(mode=0o700)
    (OUTPUT / 'tmp').mkdir(mode=0o700)
    authority = dict(state='ROOT_BOUNDED_NODE_IN_MEMORY_CACHE_MODEL_V1', node=row(NODE), monitor=row(MONITOR),
        controller=row(Path(__file__).resolve()), frozenSourceInputs=refs, capSeconds=120,
        hostModelOnly=True, actualCacheFilesystemAllowed=False, actualNextAllowed=False,
        actualEntropyAllowed=False, compilerOrGuestAllowed=False,
        scope='Audited explicit in-memory CommonJS dependency fakes; actual Source reads and native Node SHA only. No OS sandbox/network-denial attestation.')
    path = OUTPUT / 'authority.json'
    write_new(path, authority)
    logs = OUTPUT / 'owned-monitor'
    logs.mkdir(mode=0o700)
    spec = importlib.util.spec_from_file_location('genuine_model_original_owned_monitor', MONITOR)
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
    env.update(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C', TMPDIR=str(OUTPUT / 'tmp'))
    terminal = monitor.monitor([str(NODE), str(SOURCE / 'test-handler.cjs')], str(SOURCE), env, logs, 120, row(path))
    protection = all(row(Path(ref['path'])) == ref for ref in refs)
    clean = terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    clean = clean and terminal['timeout'] is terminal['forcedCleanup'] is False
    clean = clean and all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    clean = clean and all(group['alive'] is False for group in terminal['finalGroups'])
    result = dict(state='BOUNDED_NODE_CACHE_MODEL_COMPLETED_DATA_PENDING_V1', authority=row(path),
        terminal=row(logs / 'terminal.json'), rawExitCode=terminal['rawExitCode'], ownedClean=clean,
        frozenSourceInputsPreserved=protection, passed=terminal['rawExitCode'] == 0 and clean and protection,
        actualCacheFilesystemUsed=False, actualNextLoaded=False, guestInvoked=False,
        wasiOrWholeNextAccepted=False)
    write_new(OUTPUT / 'result.json', result)
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
