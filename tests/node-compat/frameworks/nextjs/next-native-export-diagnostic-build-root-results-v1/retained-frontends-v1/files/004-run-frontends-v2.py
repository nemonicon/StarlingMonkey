"""Root-owned macro-off/on embedding frontend checks; no linking or guest calls."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import stat
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
WORK = Path('/private/tmp/starling-node-compat/next-native-export-diagnostic-frontend-v2-first')
OLD = Path('/private/tmp/starling-node-compat/next-native-intl-build-fetch-cleanup825-first')
CANDIDATE = dict(path=str(BASE / 'next-native-export-public-correlation-candidate-v1/index.json'),
    sha256='6ed5a7ceabb308a163707dcb95d2b7f3ab521513cceea9837ebb70b741bfca9b', bytes=3805)
FULL = dict(path=str(BASE / 'next-full-build-runtime-root-results-v1/run-full-native-requests.py'),
    sha256='47c9cab9461a63aa12b38e6f4e8cae3cc714270c370a313fab571f53991cdfe0', bytes=14500)
MONITOR = dict(path=str(BASE.parents[1] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'),
    sha256='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe', bytes=15094)
SDK_REPAIR = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-build-root-results-v1/sdk-empty-directory-repair.json', 'sha256': '8584fd28e54f14b9950f20c925329705ecfe8b1c241935fe43db6032f478257e', 'bytes': 1170}
SDK_UTILITY = dict(path=str(BASE / 'next-native-portable-build-preparation-v8/run.py'), sha256='d4e6a2aab5ef3aab17792446e1b73a6c61fd6ab053efc618a1e8842c591d8a01', bytes=34416)
MACRO = 'NODE_COMPAT_NATIVE_EXPORT_DIAGNOSTIC_V1'


def stamp(path):
    s = path.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def row(path):
    path = Path(path)
    before = stamp(path)
    assert path.is_absolute() and path.resolve() == path and stat.S_ISREG(before[2]) and before[3] == 1
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    assert stamp(path) == before
    return dict(path=str(path), sha256=h.hexdigest(), bytes=before[4])


def verify(ref):
    assert row(ref['path']) == ref


def read(ref):
    verify(ref)
    value = json.loads(Path(ref['path']).read_bytes())
    verify(ref)
    return value


def family(ref):
    value = read(ref); root = Path(ref['path']).parent
    names = [r['path'] for r in value['files']]
    assert len(names) == len(set(names))
    dirs = set()
    for r in value['files']:
        rel = Path(r['path']); assert not rel.is_absolute() and '..' not in rel.parts
        dirs.update(str(p) for p in rel.parents if p != Path('.'))
        verify(dict(r, path=str(root / rel)))
    nodes = list(root.rglob('*'))
    assert not any(p.is_symlink() for p in nodes) and all(p.is_file() or p.is_dir() for p in nodes)
    assert {str(p.relative_to(root)) for p in nodes if p.is_file()} == set(names) | {'index.json'}
    assert {str(p.relative_to(root)) for p in nodes if p.is_dir()} == dirs


def original(name, ref):
    verify(ref)
    spec = importlib.util.spec_from_file_location(name, ref['path'])
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    verify(ref)
    return module


def save(path, value):
    with Path(path).open('x') as handle:
        handle.write(json.dumps(value, indent=2) + '\n')


def clean(terminal):
    return (terminal['rawExitCode'] == 0 and type(terminal['rawExitCode']) is int and
        terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and
        terminal['timeout'] is terminal['forcedCleanup'] is False and
        all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true'); args = parser.parse_args()
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    family(CANDIDATE)
    metadata_ref = row(OLD / 'metadata.json')
    assert metadata_ref['sha256'] == '22f1d4561b73ce58b194afd5614368d30b16fc90f8fc7d63fe5c413916711b48'
    metadata = read(metadata_ref)
    repair = read(SDK_REPAIR)
    sdk_spec = metadata['toolTreeInputs']['wasi-sdk']
    assert repair['root'] == sdk_spec['root'] and repair['logicalMembershipAndModesRestored'] is True
    assert repair['missing'] == ['share/wasi-sysroot/include/c++', 'share/wasi-sysroot/include/c++/v1']
    assert repair['changed'] == repair['extra'] == [] and repair['payloadsMutated'] is False
    sdk_utility = original('genuine_sdk_inventory_frontend_v2', SDK_UTILITY)
    sdk_before = sdk_utility.authenticate_tree(sdk_spec)
    review_ref = row(BASE / 'next-native-fetch-resource-cleanup-root-results-v1/actual-build-review.json')
    assert review_ref['sha256'] == '41857258d4da6f9fc47c8fbce60fb8818335d6ab5607c1d77f3e2c5742da3b72'
    review = read(review_ref)
    cpp = row(Path(CANDIDATE['path']).with_name('embedding.cpp'))
    assert cpp['sha256'] == '62376b242d9ee4349363a3985c2c394fba940db74e73c03515249df84164db25'
    header = row(OLD / 'componentize-source/embedding/embedding.h')
    assert any(copy['target'] == header for copy in read(row(OLD / 'result.json'))['sourceCopies'])
    roles = dict(engine=metadata['engine'], nativeMetadata=metadata_ref,
        fullNativeBuildResult=row(OLD / 'result.json'),
        fullNativeBuildObservation=row(Path(str(OLD) + '-root-monitor') / 'observation.json'),
        fullNativeBuildReview=review_ref, fullNativeBuildSourceIndex=review['callerSourceIndex'],
        fullBuildGeneratedNullSource=row(OLD / 'build/starling-raw.wasm/null.cpp'))
    full = original('genuine_full_build_frontend_diagnostic_guard', FULL)
    full.protect_full_build(roles, metadata)
    lines = metadata['actualSeparateEmbeddingCompileRows']; assert len(lines) == 1
    tokens = shlex.split(lines[0]); assert tokens[-2:] == ['-c', str(OLD / 'componentize-source/embedding/embedding.cpp')]
    assert not any(MACRO in s for s in tokens)
    compiler = Path(tokens[0]); links = []
    current = compiler
    while current.is_symlink():
        target = os.readlink(current); links.append(dict(path=str(current), target=target))
        current = current.parent / target if not Path(target).is_absolute() else Path(target)
    compiler_ref = row(current.resolve())
    stripped, removed = [], []; i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in ['-o', '-MT', '-MF']:
            assert i + 1 < len(tokens); removed.append(tokens[i:i+2]); i += 2
        elif token == '-MD':
            removed.append([token]); i += 1
        else:
            assert not token.startswith('-M') and not token.startswith('-o')
            stripped.append(token); i += 1
    obj = 'CMakeFiles/builtin_componentize_embedding.dir/embedding/embedding.cpp.obj'
    assert removed == [['-MD'], ['-MT', obj], ['-MF', obj + '.d'], ['-o', obj]]
    assert stripped[-2] == '-c'; stripped[-1] = cpp['path']
    stripped[-2:-2] = ['-iquote', str(Path(header['path']).parent), '-fsyntax-only']
    commands = [dict(mode=mode, argv=stripped[:-2] +
        (['-D' + MACRO + '=1'] if mode == 'on' else []) + stripped[-2:]) for mode in ['off', 'on']]
    assert all(cmd['argv'][-2:] == ['-c', cpp['path']] for cmd in commands)
    self_ref = row(Path(__file__).resolve())
    proof = dict(state='ROOT_NATIVE_EXPORT_DIAGNOSTIC_FRONTENDS_PREPARED_V1', candidate=CANDIDATE,
        cpp=cpp, header=header, baseMetadata=metadata_ref, baseBuildReview=review_ref,
        originalCommand=lines[0], removedOutputArguments=removed, compiler=compiler_ref,
        compilerSymlinks=links, controller=self_ref, fullGuard=FULL, monitor=MONITOR,
        fullBuildRoles=roles, commands=commands, secondsPerCommand=120, frontendCompilationAllowed=True,
        sdkDirectoryRepair=SDK_REPAIR, sdkAdmissionUtility=SDK_UTILITY, sdkInventory=sdk_spec['inventory'],
        objectOrEngineOrGuestExecutionAllowed=False)

    def protect():
        family(CANDIDATE)
        verify(SDK_REPAIR); verify(SDK_UTILITY)
        assert sdk_utility.authenticate_tree(sdk_spec) == sdk_before
        for ref in [cpp, header, metadata_ref, review_ref, compiler_ref, self_ref, FULL, MONITOR]:
            verify(ref)
        for link in links:
            p = Path(link['path']); assert p.is_symlink() and os.readlink(p) == link['target'] and p.resolve() == Path(compiler_ref['path'])
        full.protect_full_build(roles, metadata)

    protect()
    if not args.run:
        print(json.dumps(proof, indent=2)); return 0
    assert shutil.disk_usage(WORK.parent).free >= 1024**3
    assert not WORK.exists() and not WORK.is_symlink()
    WORK.mkdir(mode=0o700); save(WORK / 'authority.json', proof); authority_ref = row(WORK / 'authority.json')
    monitor = original('genuine_diagnostic_frontend_monitor', MONITOR)
    env = {k:os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
    env.update(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C')
    results = []
    try:
        for cmd in commands:
            protect(); verify(authority_ref)
            output = WORK / ('macro-' + cmd['mode']); output.mkdir(mode=0o700)
            terminal = monitor.monitor(cmd['argv'], str(WORK), env, output, 120, authority_ref)
            results.append(dict(mode=cmd['mode'], argv=cmd['argv'], terminal=row(output / 'terminal.json'),
                rawExitCode=terminal['rawExitCode'], passed=clean(terminal)))
            protect(); verify(authority_ref)
    finally:
        protect(); verify(authority_ref)
        save(WORK / 'result.json', dict(state='NATIVE_EXPORT_DIAGNOSTIC_FRONTEND_RESULTS_V1',
            authority=authority_ref, commands=results, passed=len(results) == 2 and all(r['passed'] for r in results),
            originalInputsPreserved=True, objectLinked=False, engineOrGuestExecuted=False))
    print(json.dumps(read(row(WORK / 'result.json')), indent=2))
    return 0 if len(results) == 2 and all(r['passed'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
