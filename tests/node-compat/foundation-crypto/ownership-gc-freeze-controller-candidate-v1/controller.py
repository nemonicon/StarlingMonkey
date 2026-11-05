"""Dormant freeze-only caller; complete standard-library authentication before custom imports."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
OWN = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-freeze-controller-candidate-v1'
NATIVE = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-native-candidate-v2'
NATIVE_SHA = 'ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05'
GENERIC = REPO / 'tests/node-compat/foundation-stream-consumers/http-host-controller-candidate-v2'
GENERIC_SHA = '71b7f8e54ae2e21d6673d054a20efa7b1e00409d22d8af7c5b064ad9a6380ddf'
SOURCE = '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source'
WORK = '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build'
FREEZE = '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze'
TOOLS = SOURCE + '/tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools'
BUILD_OUTPUT = '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build-root'
BUILD_EXTERNAL = '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build-external-root'
OUT = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze-external-root')


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


def validate_freeze_root(root, own_index):
    assert root['schemaVersion'] == 1 and root['state'] == 'ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PHASE_V1'
    assert root['phase'] == 'freeze' and root['variant'] == 'gc-off' and root['sourceIndexSha256'] == NATIVE_SHA
    assert root['freezeAllowed'] is True
    for phase in ('stage', 'build', 'export', 'bootstrap'):
        assert root[phase + 'Allowed'] is False
    for flag in ('guestAllowed', 'keyOperationsAllowed', 'prototypeWorkloadsAllowed', 'componentAllowed', 'nativeSourceChangesAllowed', 'normalMutationAllowed', 'metadataProjectionAllowed', 'operationalAdmission', 'runtimeAcceptanceClaim', 'timingAllowed'):
        assert root[flag] is False
    assert root['configuredSourceRoot'] == SOURCE and root['artifactToolsRoot'] == TOOLS
    assert root['workRoot'] == WORK and root['freezeRoot'] == FREEZE
    assert root['nativeSourceFiles'] == 355 and root['externalEmbeddingSources'] == 3
    assert root['externalParentDeadlineSeconds'] == 2400
    assert own_index['path'] == str(OWN / 'index.json') and root['externalControllerIndex'] == own_index
    assert root['externalControllerEntry']['path'] == str(OWN / 'controller.py')
    assert root['actualBuildResult']['path'] == BUILD_OUTPUT + '/result.json'
    assert root['actualBuildExternalTerminal']['path'] == BUILD_EXTERNAL + '/terminal.json'
    assert root['engine']['path'].startswith(WORK + '/artifacts/')
    assert root['metadata']['path'] == root['engine']['path'] + '.build.json'
    for key in ('reviewedGcPins', 'gcNativeRootReview', 'independentGcNativeReview', 'pinCandidateOutput'):
        assert root[key] is None


def validate_build_evidence(root, built, outer, proof, metadata):
    assert built['state'] == 'native-build-completed-runtime-pending' and built['sourceIndexSha256'] == NATIVE_SHA
    assert built['rawChildExitCode'] == 0 and built['launcherExitCode'] == 0 and built['lifecycleComplete'] is True
    assert built['ownedGroupCleanup']['complete'] is True and built['allOriginalNormalAndStageBytesPreserved'] is True
    assert built['configuredSourceRoot'] == SOURCE and built['workRoot'] == WORK and built['externalParentDeadlineSeconds'] == 7200
    assert built['rootAuthority'] == root['actualBuildRootAuthority']
    assert outer['rawExitCode'] == 0 and outer['parentOwnedGroupGone'] is True and outer['allObservedOwnedGroupsGone'] is True
    assert outer['forcedCleanup'] is False and outer['timeout'] is False and outer['remainingObservedPids'] == []
    assert outer['errors'] == [] and outer['interruptedSignals'] == [] and outer['authority'] == root['actualBuildRootAuthority']
    assert proof['schemaVersion'] == 1 and proof['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_BUILD_REVIEW_PASSED_V1'
    assert proof['verifiedPassed'] is True and proof['sourceIndexSha256'] == NATIVE_SHA and proof['variant'] == 'gc-off'
    assert proof['nativeSourceFiles'] == 355 and proof['externalEmbeddingSources'] == 3
    assert proof['configuredSourceRoot'] == SOURCE and proof['workRoot'] == WORK
    for field, root_field in (('actualBuildResult', 'actualBuildResult'), ('externalParentTerminal', 'actualBuildExternalTerminal'), ('rootBuildAuthority', 'actualBuildRootAuthority'), ('rootBuildObservation', 'actualBuildRootObservation'), ('engine', 'engine'), ('metadata', 'metadata')):
        assert proof[field] == root[root_field]
    assert proof['buildLog']['path'] == BUILD_OUTPUT + '/build.log' and proof['buildLog']['sha256'] == built['logSha256']
    assert proof['externalParentExitCode'] == 0 and proof['innerBuilderExitCode'] == 0
    for flag in ('allOwnedGroupsGone', 'noForcedCleanup', 'sourceAndNormalProtectionRechecked'):
        assert proof[flag] is True
    for flag in ('actualFreezeVerified', 'engineExecuted', 'guestKeyCryptoGcActionsInvoked', 'operationalAdmission'):
        assert proof[flag] is False
    # Raw metadata is inspected unchanged. The genuine freeze wrapper/body remains
    # responsible for full actual source/CMake/compile/library/tool admission.
    assert metadata['engineSha256'] == root['engine']['sha256'] and metadata['engineBytes'] == root['engine']['bytes']
    assert metadata['gcStress'] is True and metadata['entropyPolicy'] == 'off' and metadata['oomTesting'] is False
    assert len(metadata['sourceManifest']) == 355 and len(metadata['componentizeSourceManifest']) == 3
    assert metadata['cryptoKeyOwnershipPolicy']['sourceFiles'] == 355 and metadata['cryptoKeyOwnershipPolicy']['runtimeValidation'] is None
    assert metadata['cmakeCachePath'].startswith(WORK + '/') and metadata['compileCommandsPath'].startswith(WORK + '/')


def validate_peer(value, own_index):
    assert value['schemaVersion'] == 1 and value['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_FREEZE_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert value['controllerSourceIndexSha256'] == own_index['sha256'] and value['nativeSourceIndexSha256'] == NATIVE_SHA
    assert value['sourceOnly'] is True and value['sourceReviewPassed'] is True
    for key in ('ownerActionsInvoked', 'hostActionsInvoked', 'nativeFreezeActionsInvoked'):
        assert value[key] is False


def authorize(config_row):
    config = read(config_row)
    root = read(config['rootAuthority'])
    own_index = root['externalControllerIndex']
    validate_freeze_root(root, own_index)
    assert config['sourceIndex']['path'] == str(NATIVE / 'index.json') and config['sourceIndex']['sha256'] == NATIVE_SHA
    own_rows = family(own_index)
    assert root['externalControllerEntry'] in own_rows
    native_rows = family(config['sourceIndex'])
    captured = [config_row, config['rootAuthority'], *own_rows, *native_rows]
    family_indices = [own_index, config['sourceIndex']]
    refs = read(next(r for r in own_rows if r['path'] == str(OWN / 'references.json')))
    for item in refs['families']:
        captured += family(item['index'])
        family_indices.append(item['index'])
    for row in refs['files']:
        checked(row)
        captured.append(row)
    native_peer = root['independentSourceReview']
    assert native_peer == refs['nativeSourceReview'] and native_peer['result'] in captured
    data = read(native_peer['result'])
    assert data['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_SOURCE_REVIEW_PASSED_V2'
    assert data['sourceIndexSha256'] == NATIVE_SHA and data['sourceOnly'] is True and data['sourceReviewPassed'] is True and data['ownerActionsInvoked'] is False
    assert root['independentStageReview'] == refs['actualStageReview']
    assert root['actualStageResult'] == refs['actualStageResult'] and root['actualStageRootObservation'] == refs['actualStageRootObservation']
    stage_observation = read(root['actualStageRootObservation'])
    assert stage_observation['externalParentTerminal'] in captured
    validate_stage(root, read(root['actualStageResult']), read(root['independentStageReview']['result']), stage_observation, read(stage_observation['externalParentTerminal']))
    assert root['actualBuildRootAuthority'] == refs['buildRootAuthority']
    build_authority = read(root['actualBuildRootAuthority'])
    assert build_authority['phase'] == 'build' and build_authority['sourceIndexSha256'] == NATIVE_SHA
    # Only a separately indexed genuine BUILD-only result can fill these future roles.
    build_peer = root['independentBuildReview']
    build_peer_rows = family(build_peer['index'])
    assert build_peer['result'] in build_peer_rows
    captured += build_peer_rows
    family_indices.append(build_peer['index'])
    proof = read(build_peer['result'])
    assert proof['rootBuildConfig'] == refs['buildRootConfig']
    for role in ('actualBuildResult', 'actualBuildExternalTerminal', 'actualBuildRootObservation', 'metadata'):
        checked(root[role])
        captured.append(root[role])
    checked(proof['buildLog'])
    captured.append(proof['buildLog'])
    read(root['actualBuildRootObservation'])  # Whole original Root record, no data view/projection.
    built = read(root['actualBuildResult'])
    outer = read(root['actualBuildExternalTerminal'])
    validate_build_evidence(root, built, outer, proof, read(root['metadata']))
    # Validate authenticated build-only proof/metadata before reading engine bytes.
    checked(root['engine'])
    captured.append(root['engine'])
    for role in ('stdout', 'stderr'):
        checked(outer[role])
        captured.append(outer[role])
    assert outer['stderr']['bytes'] == 0
    peer = root['externalControllerReview']
    peer_rows = family(peer['index'])
    assert peer['result'] in peer_rows
    validate_peer(read(peer['result']), own_index)
    captured += peer_rows
    family_indices.append(peer['index'])
    assert refs['genericSourceIndex']['path'] == str(GENERIC / 'index.json') and refs['genericSourceIndex']['sha256'] == GENERIC_SHA
    monitor_row = next(r for r in captured if r['path'] == str(GENERIC / 'controller.py'))
    recheck(captured, family_indices)
    return config, root, captured, monitor_row, family_indices


def main(config_row):
    assert __debug__ and sys.dont_write_bytecode
    assert not any(os.environ.get(k) for k in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH'))
    config, root, captured, monitor_row, family_indices = authorize(config_row)
    for fresh in (OUT, Path(FREEZE)):
        assert not fresh.exists() and not fresh.is_symlink()
    spec = importlib.util.spec_from_file_location('reviewed_gc_freeze_owned_monitor', checked(monitor_row))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    recheck(captured, family_indices)
    OUT.mkdir(mode=0o700)
    environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    argv = [sys.executable, str(NATIVE / 'freeze.py'), json.dumps(config_row, separators=(',', ':'))]
    try:
        terminal = module.monitor(argv, str(REPO), environment, OUT, 2400, config['rootAuthority'])
    finally:
        recheck(captured, family_indices)
    assert terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] is True and terminal['allObservedOwnedGroupsGone'] is True
    assert terminal['remainingObservedPids'] == [] and not terminal['forcedCleanup'] and not terminal['timeout']
    assert not terminal['errors'] and not terminal['interruptedSignals']
    print(json.dumps(terminal), flush=True)


if __name__ == '__main__':
    assert len(sys.argv) == 2
    main(json.loads(sys.argv[1]))
