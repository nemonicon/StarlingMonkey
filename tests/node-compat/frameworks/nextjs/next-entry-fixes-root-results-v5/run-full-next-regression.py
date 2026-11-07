"""Guard the unchanged 24-HTTP/2-browser runner with native and whole-world joins.

The existing runner retains its original 600-second process owner and contract.
This wrapper performs no construction and adds no guest or host capabilities.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ACTOR = HERE.parent / 'wasmtime-deployment-candidate-v5'


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


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 2
    authority_path = Path(sys.argv[1]).resolve()
    authority_ref = row(authority_path)
    authority = read(authority_path)
    assert authority['state'] == 'ROOT_NEXT_WASMTIME_DEPLOYMENT_AUTHORIZED_V2'
    assert authority['sourceIndex'] == row(ACTOR / 'index.json')
    assert authority['plan'] == row(ACTOR / 'plan.json')
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
        assert native['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1'
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
                                        nativeInputsPreserved=True, authority=authority_ref), indent=2) + '\n')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
