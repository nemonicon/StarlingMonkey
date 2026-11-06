"""Root-owned launcher for a separately issued experimental component action.

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
assert action['schemaVersion'] == 1 and action['state'] == 'ROOT_ISSUED_EXPERIMENTAL_HASH_HMAC357_ACTION_V1'
assert action['phase'] in ('bundle', 'construct', 'jco') and action['selectedInterfaces'] == []
assert action['experimentalOnly'] is True and action['publicProfileAdmission'] is False
assert action['nativeBuildAllowed'] is action['freezeAllowed'] is action['gcOomDebugAllowed'] is False
assert action['deadlineSeconds'] == 1800
own = family(action['sourceIndex'])
peer = proof(action['sourceReview'], action['sourceReviewContract'])
assert peer['sourceIndexSha256'] == action['sourceIndex']['sha256']
artifact = proof(action['artifactReview'], action['artifactContract'])
assert artifact['state'] == 'INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_READ_ONLY_REVALIDATED_ARTIFACT_REVIEW_PASSED_V1'
assert artifact['sourceIndexSha256'] == '559d600d9bedec4e319a415bcd30b984f445cfed7df2322dee25a86cba253172'
assert artifact['originalParentExitCodes'] == [1, 1] and artifact['originalBuildPreservationPassed'] is False
config = read(action['config'])
authority = read(config['rootAuthority'])
assert config['sourceIndex'] == authority['sourceIndex'] == action['sourceIndex']
assert config['phase'] == authority['phase'] == action['phase']
assert authority['artifactReview'] == action['artifactReview'] and authority['artifactContract'] == action['artifactContract']
entry = Path(action['sourceIndex']['path']).parent / 'entry.mjs'
assert any(item['path'] == 'entry.mjs' and item['sha256'] == row(entry)['sha256'] for item in own['files'])
native = [artifact['engine'], artifact['metadata']]
for item in native:
    assert row(item['path']) == item
assert native[0]['sha256'] == '9aec9297122c33b60790fcf4e1ce909db0200a426c04de98074e39046aa0f16e'
assert native[1]['sha256'] == '2b725c114a3c23e582f87213ec5de6af128416dc8f10e9a9f9d3f6cd5d0fbce6'
assert row(NODE)['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
monitor_index = row(MONITOR / 'index.json')
assert monitor_index['sha256'] == '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b'
family(monitor_index)
assert row(MONITOR / 'monitor.py')['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
external = Path(action['externalOutputRoot'])
assert not external.exists() and not Path(authority['outputRoot']).exists()
external.mkdir(mode=0o700)
argv = [str(NODE), str(entry), 'parent', json.dumps(action['config'], separators=(',', ':'))]
invocation_path = Path(action['invocationPath'])
observation_path = Path(action['observationPath'])
assert not invocation_path.exists() and not observation_path.exists()
write(invocation_path, dict(schemaVersion=1, action=action_row, actualArgv=argv,
      launcher=row(Path(__file__).resolve()), deadlineSeconds=1800, sourceIndex=action['sourceIndex'],
      sourceReview=action['sourceReview'], nativeArtifactReview=action['artifactReview']))
environment = {key: os.environ[key] for key in ('HOME', 'USER', 'LOGNAME', 'TMPDIR') if key in os.environ}
environment.update(PATH=str(NODE.parent) + ':/usr/bin:/bin:/usr/sbin:/sbin',
                   NODE_COMPAT_TOOLCHAIN=action['toolchainRoot'],
                   NODE_COMPAT_COMPONENTIZE_MODULE=action['packagerEntry'],
                   PYTHONDONTWRITEBYTECODE='1')
spec = importlib.util.spec_from_file_location('genuine0af_isolated_component_action', MONITOR / 'monitor.py')
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)
print(json.dumps(dict(event='root-experimental-action-start', phase=action['phase'], invocation=row(invocation_path))), flush=True)
terminal = monitor.monitor(argv, str(REPO), environment, external, 1800, action_row)
clean = (terminal['rawExitCode'] == 0
         and terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
         and terminal['timeout'] is terminal['forcedCleanup'] is False
         and all(terminal[key] == [] for key in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
for item in native:
    assert row(item['path']) == item
family(action['sourceIndex'])
family(action['sourceReview']['index'])
result_path = Path(authority['outputRoot']) / 'worker/result.json'
result = json.loads(result_path.read_bytes()) if result_path.is_file() else None
if clean:
    assert result['state'] == 'EXPERIMENTAL_HASH_HMAC357_DIAGNOSTIC_PHASE_COMPLETE_UNREVIEWED_V1'
    assert result['phase'] == action['phase'] and result['primaryPresent'] is False and result['finalErrors'] == []
write(observation_path, dict(schemaVersion=1, state='ROOT_OBSERVED_EXPERIMENTAL_HASH_HMAC357_ACTION_V1',
      phase=action['phase'], action=action_row, invocation=row(invocation_path),
      ownedTerminal=row(external / 'terminal.json'), rawParentExitCode=terminal['rawExitCode'],
      phaseSucceeded=clean, allOwnedGroupsGone=terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True,
      actualPhaseResult=row(result_path) if result is not None else None, nativeEngine=native[0], nativeMetadata=native[1],
      originalBuildParentExitCodes=[1, 1], originalBuildPreservationPassed=False,
      publicProfileAdmission=False, freezeOrReleaseAccepted=False, liveEvpSnapshotAdmission=False,
      experimentalOnly=True))
print(json.dumps(dict(event='root-experimental-action-terminal', phase=action['phase'], rawExitCode=terminal['rawExitCode'],
      clean=clean, rootObservation=row(observation_path))), flush=True)
raise SystemExit(0 if clean else 1)
