"""Dormant build-only caller; standard-library authentication precedes custom imports."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
OWN = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
NATIVE = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-native-candidate-v2'
NATIVE_SHA = 'ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05'
SOURCE = '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source'
WORK = '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build'
FREEZE = '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze'
TOOLS = SOURCE + '/tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools'
OUT = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build-external-root')


def checked(row):
    assert type(row) is dict and set(row) == {'path', 'sha256', 'bytes'}
    assert type(row['path']) is str and type(row['bytes']) is int and row['bytes'] >= 0
    assert type(row['sha256']) is str and len(row['sha256']) == 64 and all(c in '0123456789abcdef' for c in row['sha256'])
    path = Path(row['path'])
    assert path.is_absolute() and '..' not in path.parts
    physical = Path('/private' + str(path)) if str(path).startswith('/tmp/') else path
    for ancestor in (physical, *physical.parents):
        assert not ancestor.is_symlink()
    before = physical.stat()
    assert physical.is_file()
    digest = hashlib.sha256()
    with physical.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    after = physical.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    assert before.st_size == row['bytes'] and digest.hexdigest() == row['sha256']
    return path


def read(row):
    assert row['bytes'] <= 32 * 1024 * 1024
    path = checked(row)
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    return json.loads(raw)


def family(row):
    index = read(row)
    root = Path(row['path']).parent
    rows = [row]
    names = set()
    for member in index['files']:
        name = member['path']
        assert name not in names and name and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name)
        child = dict(path=str(root / name), sha256=member['sha256'], bytes=member['bytes'])
        checked(child)
        rows.append(child)
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'index.json'}
    return rows


def recheck(captured, family_indices):
    for row in captured:
        checked(row)
    for row in family_indices:
        family(row)


def validate_build_root(root, own_index):
    assert root['schemaVersion'] == 1 and root['state'] == 'ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PHASE_V1'
    assert root['phase'] == 'build' and root['variant'] == 'gc-off' and root['sourceIndexSha256'] == NATIVE_SHA
    assert root['buildAllowed'] is True
    for phase in ('stage', 'freeze', 'export', 'bootstrap'):
        assert root[phase + 'Allowed'] is False
    for flag in ('guestAllowed', 'keyOperationsAllowed', 'prototypeWorkloadsAllowed', 'componentAllowed', 'nativeSourceChangesAllowed', 'normalMutationAllowed', 'metadataProjectionAllowed', 'operationalAdmission', 'runtimeAcceptanceClaim', 'timingAllowed'):
        assert root[flag] is False
    assert root['configuredSourceRoot'] == SOURCE and root['artifactToolsRoot'] == TOOLS
    assert root['workRoot'] == WORK and root['freezeRoot'] == FREEZE
    assert root['nativeSourceFiles'] == 355 and root['externalEmbeddingSources'] == 3
    assert root['externalParentDeadlineSeconds'] == 7200
    assert root['externalControllerEntry']['path'] == str(OWN / 'controller.py')
    assert own_index['path'] == str(OWN / 'index.json') and root['externalControllerIndex'] == own_index
    # Later phases/pins are not manufactured by a successful compile/link.
    for key in ('actualBuildResult', 'actualBuildExternalTerminal', 'engine', 'metadata', 'reviewedGcPins', 'gcNativeRootReview', 'independentGcNativeReview', 'pinCandidateOutput'):
        assert root[key] is None


def validate_stage(root, staged, stage_peer, root_observation, external_terminal):
    assert staged['state'] == 'CRYPTO_OWNER355_GC_SOURCE_STAGE_COMPLETE_UNREVIEWED_V1'
    assert staged['sourceIndexSha256'] == NATIVE_SHA and staged['destination'] == SOURCE
    assert stage_peer['schemaVersion'] == 1 and stage_peer['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_SOURCE_STAGE_REVIEW_PASSED_V1'
    assert stage_peer['verifiedPassed'] is True and stage_peer['actualStageResult'] == root['actualStageResult']
    assert stage_peer['sourceIndexSha256'] == NATIVE_SHA and stage_peer['configuredSourceRoot'] == SOURCE
    assert stage_peer['rootResult'] == root['actualStageRootObservation']
    assert stage_peer['externalParentTerminal'] == root_observation['externalParentTerminal']
    assert root_observation['actualStageResult'] == root['actualStageResult'] and root_observation['rootObservedToolRawExitCode'] == 0
    assert root_observation['sourceIndex']['sha256'] == NATIVE_SHA and root_observation['configuredSourceRoot'] == SOURCE
    assert external_terminal['rawExitCode'] == 0 and external_terminal['parentOwnedGroupGone'] is True and external_terminal['allObservedOwnedGroupsGone'] is True
    assert external_terminal['forcedCleanup'] is False and external_terminal['timeout'] is False
    assert external_terminal['errors'] == [] and external_terminal['interruptedSignals'] == [] and external_terminal['remainingObservedPids'] == []
    assert external_terminal['authority'] == root_observation['rootAuthority']


def validate_peer(value, own_index):
    assert value['schemaVersion'] == 1 and value['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert value['controllerSourceIndexSha256'] == own_index['sha256'] and value['nativeSourceIndexSha256'] == NATIVE_SHA
    assert value['sourceOnly'] is True and value['sourceReviewPassed'] is True
    for key in ('ownerActionsInvoked', 'hostActionsInvoked', 'nativeBuildActionsInvoked'):
        assert value[key] is False


def authorize(config_row):
    config = read(config_row)
    root = read(config['rootAuthority'])
    own_index = root['externalControllerIndex']
    validate_build_root(root, own_index)
    assert config['sourceIndex']['path'] == str(NATIVE / 'index.json') and config['sourceIndex']['sha256'] == NATIVE_SHA
    own_rows = family(own_index)
    assert root['externalControllerEntry'] in own_rows
    native_rows = family(config['sourceIndex'])
    captured = [config_row, config['rootAuthority'], *own_rows, *native_rows]
    family_indices = [own_index, config['sourceIndex']]
    refs = read(next(r for r in own_rows if r['path'] == str(OWN / 'references.json')))
    # Fixed complete donor families and genuine source-stage proof capsules are DATA.
    for item in refs['families']:
        captured += family(item['index'])
        family_indices.append(item['index'])
    for row in refs['files']:
        checked(row)
        captured.append(row)
    assert root['independentSourceReview'] == refs['nativeSourceReview']
    native_peer = root['independentSourceReview']
    assert native_peer['index'] in captured and native_peer['result'] in captured
    data = read(native_peer['result'])
    assert data['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_SOURCE_REVIEW_PASSED_V2'
    assert data['sourceIndexSha256'] == NATIVE_SHA and data['sourceOnly'] is True and data['sourceReviewPassed'] is True and data['ownerActionsInvoked'] is False
    assert root['independentStageReview'] == refs['actualStageReview']
    assert root['actualStageResult'] == refs['actualStageResult'] and root['actualStageRootObservation'] == refs['actualStageRootObservation']
    stage_peer = read(root['independentStageReview']['result'])
    root_observation = read(root['actualStageRootObservation'])
    terminal_row = root_observation['externalParentTerminal']
    assert terminal_row in captured
    validate_stage(root, read(root['actualStageResult']), stage_peer, root_observation, read(terminal_row))
    peer = root['externalControllerReview']
    peer_rows = family(peer['index'])
    assert peer['result'] in peer_rows
    validate_peer(read(peer['result']), own_index)
    captured += peer_rows
    family_indices.append(peer['index'])
    monitor_row = next(r for r in own_rows if r['path'] == str(OWN / 'monitor.py'))
    recheck(captured, family_indices)
    return config, root, captured, monitor_row, family_indices


def main(config_row):
    assert __debug__ and not any(os.environ.get(k) for k in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH'))
    assert sys.dont_write_bytecode  # Require PYTHONDONTWRITEBYTECODE=1; never write into sealed source.
    config, root, captured, monitor_row, family_indices = authorize(config_row)
    # No work-directory adoption or cache/source rewrite: genuine build.py owns its paths.
    assert not OUT.exists() and not OUT.is_symlink()
    for fresh in (Path(WORK), Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build-root')):
        assert not fresh.exists() and not fresh.is_symlink()
    spec = importlib.util.spec_from_file_location('reviewed_gc_build_owned_monitor_7200', checked(monitor_row))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    recheck(captured, family_indices)
    OUT.mkdir(mode=0o700)
    environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    argv = [sys.executable, str(NATIVE / 'build.py'), json.dumps(config_row, separators=(',', ':'))]
    try:
        terminal = module.monitor(argv, str(REPO), environment, OUT, 7200, config['rootAuthority'])
    finally:
        # Source/proof drift also refuses a failed or interrupted invocation.
        recheck(captured, family_indices)
    assert terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] is True and terminal['allObservedOwnedGroupsGone'] is True
    assert terminal['remainingObservedPids'] == [] and not terminal['forcedCleanup'] and not terminal['timeout']
    assert not terminal['errors'] and not terminal['interruptedSignals']
    print(json.dumps(terminal), flush=True)


if __name__ == '__main__':
    assert len(sys.argv) == 2
    main(json.loads(sys.argv[1]))
