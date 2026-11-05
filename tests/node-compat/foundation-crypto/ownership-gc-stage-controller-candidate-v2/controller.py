"""Dormant stage-only caller of the actual generic owned Root monitor API."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
OWN = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-stage-controller-candidate-v2'
NATIVE = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-native-candidate-v2'
GENERIC = REPO / 'tests/node-compat/foundation-stream-consumers/http-host-controller-candidate-v2'
GENERIC_SHA = '71b7f8e54ae2e21d6673d054a20efa7b1e00409d22d8af7c5b064ad9a6380ddf'
NATIVE_SHA = 'ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05'
OUT = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-stage-root')


def checked(row):
    path = Path(row['path'])
    assert path.is_absolute() and '..' not in path.parts
    physical = Path('/private' + str(path)) if str(path).startswith('/tmp/') else path
    for ancestor in (physical, *physical.parents):
        assert not ancestor.is_symlink()
    before = physical.stat()
    digest = hashlib.sha256()
    with physical.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    after = physical.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    assert physical.is_file() and before.st_size == row['bytes'] and digest.hexdigest() == row['sha256']
    return path


def read(row):
    assert row['bytes'] <= 32 * 1024 * 1024
    path = checked(row)
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    return json.loads(raw)


def family(row):
    index = read(row)
    rows = [row]
    names = set()
    for member in index['files']:
        name = member['path']
        assert name not in names and name and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name)
        child = dict(path=str(Path(row['path']).parent / name), sha256=member['sha256'], bytes=member['bytes'])
        checked(child)
        rows.append(child)
    return rows


def main(config_row):
    assert __debug__ and not any(os.environ.get(k) for k in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH'))
    config = read(config_row)
    root = read(config['rootAuthority'])
    assert root['state'] == 'ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PHASE_V1' and root['phase'] == 'stage'
    assert root['stageAllowed'] is True and root['variant'] == 'gc-off' and root['sourceIndexSha256'] == NATIVE_SHA
    for phase in ('build', 'freeze', 'export', 'bootstrap'):
        assert root[phase + 'Allowed'] is False
    for flag in ('guestAllowed', 'keyOperationsAllowed', 'prototypeWorkloadsAllowed', 'componentAllowed', 'nativeSourceChangesAllowed', 'normalMutationAllowed', 'metadataProjectionAllowed', 'operationalAdmission', 'runtimeAcceptanceClaim', 'timingAllowed'):
        assert root[flag] is False
    assert config['sourceIndex']['path'] == str(NATIVE/'index.json') and config['sourceIndex']['sha256'] == NATIVE_SHA
    assert root['externalControllerEntry']['path'] == str(OWN/'controller.py')
    checked(root['externalControllerEntry'])
    own_index = root['externalControllerIndex']
    assert own_index['path'] == str(OWN/'index.json')
    captured = [config_row, config['rootAuthority'], *family(own_index), *family(config['sourceIndex'])]
    generic_index = root['genericMonitorIndex']
    assert generic_index['path'] == str(GENERIC/'index.json') and generic_index['sha256'] == GENERIC_SHA
    generic_rows = family(generic_index)
    captured += generic_rows
    peer = root['externalControllerReview']
    peer_rows = family(peer['index'])
    assert peer['result'] in peer_rows
    reviewed = read(peer['result'])
    assert reviewed['sourceOnly'] is True and reviewed['sourceReviewPassed'] is True and reviewed['hostActionsInvoked'] is False
    assert reviewed['httpControllerSourceIndexSha256'] == GENERIC_SHA and reviewed['gcStageControllerSourceIndexSha256'] == own_index['sha256']
    captured += peer_rows
    native_peer = root['independentSourceReview']
    peer_rows = family(native_peer['index'])
    assert native_peer['result'] in peer_rows
    reviewed = read(native_peer['result'])
    assert reviewed['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_SOURCE_REVIEW_PASSED_V2' and reviewed['sourceIndexSha256'] == NATIVE_SHA and reviewed['sourceReviewPassed'] is True
    captured += peer_rows
    monitor_row = next(r for r in generic_rows if r['path'] == str(GENERIC/'controller.py'))
    spec = importlib.util.spec_from_file_location('actual_reviewed_generic_owned_monitor', checked(monitor_row))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Actual standard-library module and explicit API; no binding or global changes.
    for row in captured:
        checked(row)
    assert not OUT.exists() and not Path(root['configuredSourceRoot']).exists()
    assert root['configuredSourceRoot'] == '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source'
    assert root['externalParentDeadlineSeconds'] == 600
    OUT.mkdir(mode=0o700)
    environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'}
    argv = [sys.executable, str(NATIVE/'stage.py'), json.dumps(config_row, separators=(',', ':'))]
    terminal = module.monitor(argv, str(REPO), environment, OUT, 600, config['rootAuthority'])
    for row in captured:
        checked(row)
    assert terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] is True and not terminal['forcedCleanup'] and not terminal['timeout'] and not terminal['errors'] and not terminal['interruptedSignals']
    print(json.dumps(terminal), flush=True)


if __name__ == '__main__':
    assert len(sys.argv) == 2
    main(json.loads(sys.argv[1]))
