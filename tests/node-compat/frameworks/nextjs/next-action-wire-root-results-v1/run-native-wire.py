"""Guard one Server Action transport diagnostic with native/world joins.

The dedicated Source retains its original600s owner; no construction or new
guest/host capability is introduced. This is not the24HTTP/browser contract.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent
ACTOR = HERE.parent / 'next-action-wire-native-candidate-v1'


def read(path):
    return json.loads(Path(path).read_text())


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def verify(ref):
    path = Path(ref['path'])
    assert path.is_absolute() and path.resolve() == path
    assert path.is_file() and not path.is_symlink()
    assert row(path) == ref, str(path)


def family(ref):
    verify(ref)
    index = Path(ref['path'])
    root = index.parent
    rows = read(index)['files']
    names = [item['path'] for item in rows]
    assert len(names) == len(set(names))
    nodes = list(root.rglob('*'))
    assert not any(node.is_symlink() for node in nodes)
    assert all(node.is_file() or node.is_dir() for node in nodes)
    assert {node.relative_to(root).as_posix() for node in nodes if node.is_file()} == set(names) | {'index.json'}
    directories = set()
    for item in rows:
        relative = Path(item['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        directories.update(p.as_posix() for p in relative.parents if p != Path('.'))
        path = root / relative
        assert path.stat().st_nlink == 1
        verify(dict(item, path=str(path)))
    assert {node.relative_to(root).as_posix() for node in nodes if node.is_dir()} == directories


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clean(terminal):
    return (terminal['rawExitCode'] == 0 and terminal['timeout'] is False
            and terminal['forcedCleanup'] is False and terminal['parentOwnedGroupGone'] is True
            and terminal['allObservedOwnedGroupsGone'] is True
            and all(terminal[key] == [] for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']))


def protect_full_build(authority, native):
    """Consume the genuine full-build wire; never adapt incremental metadata."""
    for key in ['fullNativeBuildResult', 'fullNativeBuildObservation', 'fullNativeBuildReview']:
        verify(authority[key])
    family(authority['fullNativeBuildSourceIndex'])
    result = read(authority['fullNativeBuildResult']['path'])
    observation = read(authority['fullNativeBuildObservation']['path'])
    review = read(authority['fullNativeBuildReview']['path'])
    assert review['state'] == 'INDEPENDENT_PORTABLE_NEXT_INTL_NATIVE_BUILD_DATA_REVIEW_PASSED_V1'
    assert review['verifiedPassed'] is True
    assert review['actualResult'] == authority['fullNativeBuildResult']
    assert review['actualRootObservation'] == authority['fullNativeBuildObservation']
    assert review['engine'] == authority['engine'] and review['metadata'] == authority['nativeMetadata']
    assert review['callerSourceIndex'] == authority['fullNativeBuildSourceIndex']
    assert review['engineOrGuestExecuted'] is review['componentConstructed'] is review['runtimeAccepted'] is review['adoption'] is False
    assert native['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1'
    assert type(native['portableBuildAdmissionVersion']) is int and native['portableBuildAdmissionVersion'] == 3
    assert (native['nativePolicyInputCount'], native['buildSupportInputCount'], native['embeddingInputCount']) == (435, 387, 3)
    assert [len(native[k]) for k in ['nativePolicyInputManifest', 'buildSupportInputManifest', 'embeddingInputManifest']] == [435, 387, 3]
    rows = native['actualCompileRows']
    assert len(rows) == len({r['file'] for r in rows}) == 80
    generated_null = Path(native['compiledSourceRoot']).parent / 'build/starling-raw.wasm/null.cpp'
    outsiders = [Path(r['file']) for r in rows if Path(native['compiledSourceRoot']) not in Path(r['file']).parents]
    assert outsiders == [generated_null]
    verify(authority['fullBuildGeneratedNullSource'])
    assert authority['fullBuildGeneratedNullSource']['path'] == str(generated_null)
    assert len(native['actualSeparateEmbeddingCompileRows']) == 1
    assert native['logicalCargoAuditDescriptorFromVerifiedCapsule'] is True
    assert native['old83MetadataProjected'] is native['engineExecuted'] is native['guestExecuted'] is native['adoption'] is False
    assert result['state'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_COMPLETED_RUNTIME_PENDING_V1'
    assert result['passed'] is True and result['primaryError'] is None and result['postCollectionErrors'] == []
    assert result['metadata'] == authority['nativeMetadata'] and result['engineCandidate'] == authority['engine']
    assert len(result['sourceCopies']) == 825
    protection = result['inputProtection']
    assert protection['unchanged'] is True and protection['errors'] == [] and protection['wholeTrees'] == 10
    assert protection['files'] == review['protectedFileDescriptorsChecked']
    assert observation['state'] == 'PORTABLE_NATIVE_BUILD_ROOT_COMPLETED_UNREVIEWED_V3'
    assert observation['workerResult'] == authority['fullNativeBuildResult']
    assert observation['completedUnreviewed'] is observation['workerReportedPassed'] is observation['ownedCleanRawZero'] is True
    assert type(observation['rawExitCode']) is int and observation['rawExitCode'] == 0
    assert observation['errors'] == [] and observation['engineOrGuestExecuted'] is False
    assert observation['originalInputProtection']['unchanged'] is True
    assert observation['originalInputProtection']['errors'] == []
    verify(observation['terminal']); terminal = read(observation['terminal']['path'])
    assert type(terminal['rawExitCode']) is int and clean(terminal)
    assert terminal['authority'] == observation['issuedAuthority']
    verify(observation['issuedAuthority']); issued = read(observation['issuedAuthority']['path'])
    verify(native['rootAuthority']); copied = read(native['rootAuthority']['path'])
    assert copied == issued and copied['callerIndex'] == authority['fullNativeBuildSourceIndex']
    assert copied['entry'] == native['recipe'] and copied['wrapperPython'] == native['wrapperPython']
    assert native['compiledSourceRoot'] == str(Path(copied['workRoot']) / 'native-source')
    assert copied['portableCargoSelection'] == native['portableCargoSelection']
    for key in ['engineOrGuestExecutionAllowed', 'freezeAllowed', 'networkAllowed', 'rustupAllowed']:
        assert copied[key] is False
    assert copied['configureAllowed'] is copied['buildAllowed'] is True
    assert result['phases'] == native['phases']
    assert [p['label'] for p in result['phases']] == ['rust-version', 'cargo-version', 'rust-sysroot', 'configure', 'build', 'ninja-commands']
    for phase in result['phases']:
        assert type(phase['rawExitCode']) is type(phase['outerRawExitCode']) is int
        assert phase['rawExitCode'] == phase['outerRawExitCode'] == 0
        assert phase['ownedGone'] is phase['innerOwnedClean'] is True
        assert phase['timeout'] is phase['forcedCleanup'] is False
        assert all(phase[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
        verify(phase['outerTerminal']); outer = read(phase['outerTerminal']['path'])
        assert type(outer['rawExitCode']) is int and clean(outer) and outer['authority'] == native['rootAuthority']
        for key in ['stdout', 'stderr']:
            verify(outer[key])
        verify(phase['workerResult']); worker = read(phase['workerResult']['path'])
        assert type(worker['rawChildExitCode']) is int and worker['rawChildExitCode'] == 0
        assert worker['lifecycleComplete'] is True and worker['stoppedForDiskSpace'] is False
        assert worker['launcherErrors'] == [] and worker['stopReason'] is None and worker['sigtermReceived'] == 0
        cleanup = worker['ownedGroupCleanup']
        assert cleanup['complete'] is True and cleanup['events'] == cleanup['errors'] == []


def check_capacity(free, required):
    assert type(free) is type(required) is int and required == 1073741824
    assert free >= required, 'Root runtime launch requires at least 1 GiB free'


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 2
    authority_path = Path(sys.argv[1]).resolve()
    authority_ref = row(authority_path)
    authority = read(authority_path)
    assert authority['state'] == 'ROOT_NEXT_WASMTIME_DEPLOYMENT_AUTHORIZED_V2'
    assert authority['sourceIndex'] == row(ACTOR / 'index.json')
    assert authority['plan'] == row(ACTOR / 'plan.json')
    actor_plan = read(ACTOR / 'plan.json')
    required_free = authority['rootLaunchMinimumFreeBytes']
    check_capacity(shutil.disk_usage(Path(actor_plan['outputPrefix']).parent).free, required_free)
    assert re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', authority['runId'])
    receipt = HERE / (authority['runId'] + '-full-world-guard.json')
    assert not receipt.exists()

    def protect():
        verify(authority_ref)
        family(authority['sourceIndex'])
        family(authority['inputSourceIndex'])
        family(authority['constructionCallerIndex'])
        for key in ['engine', 'nativeMetadata', 'constructionResult', 'component',
                    'componentAudit', 'constructionOuterTerminal', 'constructionWorldGuard',
                    'worldGuardImplementation']:
            verify(authority[key])
        for ref in authority['engineBuildEvidence'] + authority['nativeProtectedInputs']:
            verify(ref)
        for ref in authority['nativeSourceFamilies']:
            family(ref)
        construction = read(authority['constructionResult']['path'])
        caller_root = Path(authority['constructionCallerIndex']['path']).parent
        plan_member = next(item for item in read(authority['constructionCallerIndex']['path'])['files'] if item['path'] == 'plan.json')
        assert construction['plan'] == dict(plan_member, path=str(caller_root / 'plan.json'))
        constructor_plan = read(construction['plan']['path'])
        assert constructor_plan['inputSourceIndex'] == authority['inputSourceIndex']
        assert constructor_plan['entries']['real-next'] == authority['inputEntry']
        for key in ['engine', 'nativeMetadata', 'inputEntry', 'inputSourceIndex', 'component', 'componentAudit']:
            assert construction['artifacts'][key] == authority[key]
        verify(construction['rootAuthority'])
        constructor = read(construction['rootAuthority']['path'])
        assert constructor['state'] == 'ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2'
        assert constructor['entryMode'] == 'real-next' and constructor['componentizeInitAllowed'] is True
        for key in ['ordinaryExportsAllowed', 'httpServingAllowed', 'networkAllowed', 'nativeBuildAllowed',
                    'packageMutationAllowed', 'globalPinMutationAllowed', 'debugAllowed',
                    'applicationMountAtInitAllowed', 'deployedResnapshotAllowed']:
            assert constructor[key] is False
        assert constructor['callerIndex'] == authority['constructionCallerIndex']
        for key in ['engine', 'nativeMetadata', 'metadataExpectedFixedValues', 'engineBuildEvidence']:
            assert constructor[key] == authority[key]
        native = read(authority['nativeMetadata']['path'])
        protect_full_build(authority, native)
        assert native['engine'] == authority['engine']
        for key, value in authority['metadataExpectedFixedValues'].items():
            assert native[key] == value, key
        assert construction['artifacts']['engineBuildEvidence'] == authority['engineBuildEvidence']
        outer = read(authority['constructionOuterTerminal']['path'])
        assert clean(outer) and outer['authority'] == construction['rootAuthority']
        for ref in [outer['stdout'], outer['stderr']]:
            verify(ref)
        assert construction['passed'] is True and construction['error'] is None
        assert [item['label'] for item in construction['commands']] == ['componentize-init', 'component-validate', 'component-wit']
        for command in construction['commands']:
            verify(command['terminal'])
            terminal = read(command['terminal']['path'])
            assert clean(terminal) and terminal['authority'] == construction['rootAuthority']
            assert command['rawExitCode'] == 0 and command['clean'] is True
            for key in ['stdout', 'stderr']:
                assert terminal[key] == command[key]
                verify(command[key])

    protect()
    guard = load_module('reviewed_whole_world_guard', authority['worldGuardImplementation']['path'])
    world_authority = dict(callerIndex=authority['constructionCallerIndex'],
                           newSourceEvidence=[authority['inputSourceIndex'], *authority['worldInputs']],
                           worldSourceIndex=authority['worldSourceIndex'])
    before = guard.world_guard(world_authority)
    constructor_guard = read(authority['constructionWorldGuard']['path'])
    assert constructor_guard['unchanged'] is True
    assert constructor_guard['before'] == constructor_guard['after'] == before
    admission_free = shutil.disk_usage(Path(actor_plan['outputPrefix']).parent).free
    check_capacity(admission_free, required_free)
    owned = load_module('unchanged_full_next_owned_runner', ACTOR / 'run-owned.py')
    code = 1
    try:
        try:
            owned.main()
        except SystemExit as status:
            assert type(status.code) is int and status.code in (0, 1)
            code = status.code
    finally:
        after = guard.world_guard(world_authority)
        protect()
        assert after == before
        with receipt.open('x') as handle:
            handle.write(json.dumps(dict(before=before, after=after, unchanged=True,
                                        nativeInputsPreserved=True, authority=authority_ref,
                                        freeBytesAtAdmission=admission_free, minimumFreeBytes=required_free), indent=2) + '\n')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
