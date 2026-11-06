"""Root-owned launcher for a separately issued stock-Wasmtime diagnostic action.

The action descriptor is issued by Root after source/artifact review. This file
does not issue its own action, change native inputs, or admit a public profile.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
BASE = REPO / 'tests/node-compat/foundation-crypto'
MONITOR = BASE / 'ownership-gc-build-controller-candidate-v1'
NODE = Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')


def row(path):
    path = Path(path)
    assert path.is_absolute() and '..' not in path.parts
    for p in (path, *path.parents):
        assert not p.is_symlink(), str(p)
    a = path.stat()
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4194304), b''):
            h.update(block)
    b = path.stat()
    assert (a.st_dev, a.st_ino, a.st_mode, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (
        b.st_dev, b.st_ino, b.st_mode, b.st_size, b.st_mtime_ns, b.st_ctime_ns)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=b.st_size)


def read(descriptor):
    assert row(descriptor['path']) == descriptor and descriptor['bytes'] <= 32 * 1024 * 1024
    return json.loads(Path(descriptor['path']).read_bytes())


def family(descriptor):
    data = read(descriptor)
    base = Path(descriptor['path']).parent
    names = {'index.json'}
    for item in data['files']:
        name = item['path']
        assert name not in names and not Path(name).is_absolute()
        assert all(part not in ('', '.', '..') for part in name.split('/'))
        names.add(name)
        assert row(base / name) == dict(item, path=str(base / name))
    assert not any(p.is_symlink() for p in base.rglob('*'))
    assert names == {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
    return data


def proof(pair, contract):
    ix = family(pair['index'])
    assert any(dict(item, path=str(Path(pair['index']['path']).parent / item['path'])) == pair['result']
               for item in ix['files'])
    value, rules = read(pair['result']), read(contract)
    assert value['schemaVersion'] == 1 and value['state'] == rules['requiredReviewState']
    assert value.get('verifiedPassed', value.get('sourceReviewPassed')) is True
    for group in ('requiredFixedValues', 'requiredExactDescriptors', 'requiredVerifiedProperties'):
        for name, expected in rules.get(group, {}).items():
            assert value[name] == expected, name
    if 'requiredCoverage' in rules:
        assert value['coverage'] == rules['requiredCoverage']
    return value


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


assert len(sys.argv) == 2 and __debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1
action_row = json.loads(sys.argv[1])
action = read(action_row)
assert action['schemaVersion'] == 1 and action['state'] == 'ROOT_ISSUED_STOCK_WASMTIME_HASH_HMAC357_ACTION_V1'
assert action['experimentalOnly'] is True and action['publicProfileAdmission'] is False
assert action['deadlineSeconds'] == 1800
own = family(action['sourceIndex'])
assert action['sourceIndex']['sha256'] == '339a11fb72312f1482912eec8dbf0664258689fb0a4616165d26529cb0fee74c'
peer = read(action['sourceReview'])
assert peer['sourceOnly'] is peer['sourceReviewPassed'] is True
assert peer['sourceIndexSha256'] == action['sourceIndex']['sha256']
artifact = proof(action['artifactReview'], action['artifactContract'])
assert artifact['sourceIndexSha256'] == '559d600d9bedec4e319a415bcd30b984f445cfed7df2322dee25a86cba253172'
config = read(action['config'])
authority = read(config['rootAuthority'])
assert config['sourceIndex'] == authority['sourceIndex'] == action['sourceIndex']
assert authority['artifactReview'] == action['artifactReview']
assert authority['artifactContract'] == action['artifactContract']
jco = read(action['correctedJcoObservation'])
assert jco['phaseSucceeded'] is True and jco['rawParentExitCode'] == 0 and jco['allOwnedGroupsGone'] is True
fresh_path = Path(authority['actualFreshJcoRawReturn']['path']).parent / 'result.json'
fresh = json.loads(fresh_path.read_bytes())
assert fresh['sourceIndex']['sha256'] == '48b15d2fd8618f6cd05a2404b2b3ace3ffd422d50889e9a30d34e3d6c5236f2f'
assert fresh['primaryPresent'] is False and fresh['finalErrors'] == []
assert fresh['generatedModuleImportAttempted'] is fresh['generatedModuleImported'] is True
assert fresh['callAttempts'] == fresh['callReturns'] == fresh['stringReturns'] == fresh['comparedCalls'] == 1
assert fresh['callThrows'] == 0 and fresh['arm'] == authority['arm']
assert row(authority['actualFreshJcoRawReturn']['path']) == authority['actualFreshJcoRawReturn']
for item in (artifact['engine'], artifact['metadata'], authority['component']):
    assert row(item['path']) == item
assert row(NODE)['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
monitor_index = row(MONITOR / 'index.json')
assert monitor_index['sha256'] == '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b'
family(monitor_index)
assert row(MONITOR / 'monitor.py')['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
external = Path(action['externalOutputRoot'])
assert not external.exists() and not Path(authority['outputRoot']).exists()
external.mkdir(mode=0o700)
entry = Path(action['sourceIndex']['path']).parent / 'companion.mjs'
argv = [str(NODE), str(entry), json.dumps(action['config'], separators=(',', ':'))]
write(action['invocationPath'], dict(schemaVersion=1, action=action_row, actualArgv=argv,
      launcher=row(Path(__file__).resolve()), deadlineSeconds=1800, sourceIndex=action['sourceIndex'],
      sourceReview=action['sourceReview'], correctedJcoObservation=action['correctedJcoObservation']))
environment = {key: os.environ[key] for key in ('HOME', 'USER', 'LOGNAME', 'TMPDIR') if key in os.environ}
environment.update(PATH=str(NODE.parent) + ':/usr/bin:/bin:/usr/sbin:/sbin', PYTHONDONTWRITEBYTECODE='1')
spec = importlib.util.spec_from_file_location('genuine0af_stock_wasmtime_hash_hmac_action', MONITOR / 'monitor.py')
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)
print(json.dumps(dict(event='root-stock-wasmtime-start', action=action_row)), flush=True)
terminal = monitor.monitor(argv, str(REPO), environment, external, 1800, action_row)
clean = (terminal['rawExitCode'] == 0
         and terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
         and terminal['timeout'] is terminal['forcedCleanup'] is False
         and all(terminal[key] == [] for key in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
family(action['sourceIndex'])
assert row(action['sourceReview']['path']) == action['sourceReview']
for item in (artifact['engine'], artifact['metadata'], authority['component']):
    assert row(item['path']) == item
result_path = Path(authority['outputRoot']) / 'result.json'
result = json.loads(result_path.read_bytes()) if result_path.is_file() else None
if clean:
    assert result['state'] == 'EXPERIMENTAL_HASH_HMAC357_WASMTIME3_COMPLETE_UNREVIEWED_V1'
    assert result['primary']['present'] is False and result['finalErrors'] == []
    assert len(result['sessions']) == 3 and result['fullRawStringsCompared'] is True
write(action['observationPath'], dict(schemaVersion=1, state='ROOT_OBSERVED_STOCK_WASMTIME_HASH_HMAC357_ACTION_V1',
      action=action_row, arm=authority['arm'], invocation=row(action['invocationPath']),
      ownedTerminal=row(external / 'terminal.json'), rawParentExitCode=terminal['rawExitCode'],
      phaseSucceeded=clean, allOwnedGroupsGone=terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True,
      actualPhaseResult=row(result_path) if result is not None else None, component=authority['component'],
      correctedJcoObservation=action['correctedJcoObservation'], publicProfileAdmission=False,
      freezeOrSnapshotOrReuseOrSecurityOrCostAcceptance=False))
print(json.dumps(dict(event='root-stock-wasmtime-terminal', rawExitCode=terminal['rawExitCode'], clean=clean,
      rootObservation=row(action['observationPath']))), flush=True)
raise SystemExit(0 if clean else 1)
