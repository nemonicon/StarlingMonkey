"""Fresh one-afterimage native build; Root executes, never the Source reviewer."""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import shlex
import stat
import sys
import time
import tomllib
import traceback

if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
    raise RuntimeError('requires unoptimized Python -I -B before input IO')

HERE = Path(__file__).resolve().parent
WORK = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first')
SELECTION = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/async-context/clone-cancel-native-build-v1/build-selection.json', 'sha256': 'cc807f6ea77a7ac951114d11ec03c952ad6cdffcdfc9d79192a48a23c41c8bcc', 'bytes': 21843}  # Root binds exactly one complete, reviewed fresh selection descriptor.
DONOR = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-build-v1/run.py', 'sha256': '45538b3b6044fab7ace00e256b86b5ef0ff8a3351c70f6f3499a9805afd139d7', 'bytes': 35651}
METADATA_KEYS = ('schemaVersion', 'metadataKind', 'sourceComposition', 'sourceRoot', 'compiledSourceRoot', 'compiledAfterInputs', 'compilerTools', 'actualRustTools', 'nativePolicyInputCount', 'nativePolicyInputManifest', 'buildSupportInputCount', 'buildSupportInputManifest', 'embeddingInputCount', 'embeddingInputManifest', 'selectedModuleManifests', 'requestedCMake', 'observedCMake', 'compileDatabase', 'actualCompileRows', 'wholeNinjaCommands', 'actualSeparateEmbeddingCompileRows', 'actualLibrary', 'actualSavedFrameHeader', 'actualConfigHeader', 'actualConfdefs', 'patchedSpiderMonkeyEvidence', 'savedFramePatchIndex', 'actualAggregateLock', 'actualRustConfiguration', 'offlineCargoConfig', 'validatedCargoAudit', 'portableCargoSelection', 'portableCargoAdmission', 'wrapperPython', 'buildToolPython', 'portableBuildAdmissionVersion', 'logicalCargoAuditDescriptorFromVerifiedCapsule', 'validatedCargoProofCapsule', 'validatedCargoProofIndex', 'toolTreeInputs', 'initialTreeProtection', 'originalExtractionWholeTreeAttestationClaimed', 'linkAndRustInputs', 'engine', 'phases', 'recipe', 'rootAuthority', 'old83MetadataProjected', 'engineExecuted', 'guestExecuted', 'adoption', 'nativeExportDiagnosticCompileEvidence')
AFTER_SHA = '0431184d4562972c98538494caf46d2b11cdf0280f51d0e7143cd8534526442e'
REL = 'builtins/web/fetch/request-response.cpp'
START_FREE = 3 * 1024**3
STOP_FREE = 1024**3
INPUTS = {}


def descriptor(path):
    p = Path(path)
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024**2), b''):
            h.update(b)
    return dict(path=str(p), sha256=h.hexdigest(), bytes=p.stat().st_size)


def checked(ref):
    p = Path(ref['path'])
    assert p.is_absolute() and p.resolve(strict=True) == p and p.is_file()
    assert descriptor(p) == {k: ref[k] for k in ('path', 'sha256', 'bytes')}, str(p)
    INPUTS[str(p)] = {k: ref[k] for k in ('path', 'sha256', 'bytes')}
    return p


def read(ref):
    assert 0 < ref['bytes'] <= 32 * 1024**2
    return json.loads(checked(ref).read_bytes())


def load(ref, name):
    spec = importlib.util.spec_from_file_location(name, checked(ref))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def utility():
    # Only generic descriptor/save/copy/tree/cache helpers are called. No old
    # validate_authority, portable/cargo admission, effective_plan or main call.
    return load(DONOR, 'pinned_native_build_generic_utilities')


def selection():
    assert SELECTION is not None, 'Root selection descriptor is unbound'
    s = read(SELECTION)
    assert s['schemaVersion'] == 1 and s['state'] == 'CLONE_CANCEL_NATIVE_BUILD_SELECTION_DATA_V1' and s['workRoot'] == str(WORK)
    assert WORK.resolve() == WORK and WORK.is_dir()
    assert descriptor(Path(sys.executable).resolve()) == s['wrapperPython']
    assert s['monitor']['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
    assert s['lifecycle']['sha256'] == '54557e22b4cd1c99cdc67c6dc8ff55826fae0d47a6b6481b72019c9480e5293d'
    return s


def clean_terminal(t):
    return (t['rawExitCode'] == 0 and t['parentOwnedGroupGone'] is True and
            t['allObservedOwnedGroupsGone'] is True and t['timeout'] is False and
            t['forcedCleanup'] is False and t['errors'] == [] and t['signals'] == [] and
            t['interruptedSignals'] == [] and t['remainingObservedPids'] == [])


def phase_quiescent(record):
    return (record['ownedGone'] is True and record['innerOwnedClean'] is True and
            record['timeout'] is False and record['forcedCleanup'] is False and
            record['errors'] == record['signals'] == record['interruptedSignals'] == record['remainingObservedPids'] == [])


def source_rows(m, old):
    assert m['state'] == 'CLONE_CANCEL_825_INPUTS_MATERIALIZED_V1' and m['workRoot'] == str(WORK)
    assert m['inputsUnchanged'] is True and m['previousMetadataProjected'] is False
    assert (m['nativeCount'], m['supportCount'], m['embeddingCount']) == (435, 387, 3)
    assert m['changedNativePaths'] == [REL] and len(m['copies']) == 825
    native = {r['path']: r for r in old['nativePolicyInputManifest']}
    support = {r['relativePath']: r for r in old['buildSupportInputManifest']}
    embedding = {r['relativePath']: r for r in old['embeddingInputManifest']}
    assert (len(native), len(support), len(embedding)) == (435, 387, 3)
    seen = set()
    for row in m['copies']:
        rel = Path(row['relativePath'])
        assert not rel.is_absolute() and '..' not in rel.parts and rel.as_posix() == row['relativePath']
        role = row['role']
        base = WORK / ('componentize-source' if role == 'embedding' else 'native-source')
        assert row['destination'] == str(base / rel) and row['target']['path'] == row['destination']
        assert row['destination'] not in seen
        seen.add(row['destination'])
        assert row['source']['sha256'] == row['target']['sha256'] and row['source']['bytes'] == row['target']['bytes']
        if role == 'native':
            predecessor = native[rel.as_posix()]
            if rel.as_posix() == REL:
                assert predecessor['sha256'] == '1fe296b8472f14e50556910227b184552e0a0ac424f97a0f170c4b91cfd35fa6'
                assert row['target']['sha256'] == AFTER_SHA and row['target']['bytes'] == 130742
            else:
                assert all(row['target'][k] == predecessor[k] for k in ('sha256', 'bytes'))
        else:
            assert role in ('support', 'embedding')
            predecessor = (support if role == 'support' else embedding)[rel.as_posix()]
            assert row['source'] == predecessor['source'] and row['mode'] == predecessor['mode']
        checked(row['source'])
        checked(row['target'])
        st = Path(row['target']['path']).stat()
        assert st.st_nlink == 1 and stat.S_IMODE(st.st_mode) == row['mode']
    assert seen == {str(p) for root in ('native-source', 'componentize-source') for p in (WORK / root).rglob('*') if p.is_file()}
    assert not any(p.is_symlink() for root in ('native-source', 'componentize-source') for p in (WORK / root).rglob('*'))
    for ref in m['cargo'].values():
        if isinstance(ref, dict) and {'path', 'sha256', 'bytes'} <= ref.keys():
            checked(ref)
    return m['copies']


def validate_generators(ref, m):
    g = read(ref)
    assert g['state'] == 'CLONE_CANCEL_GENERATOR_CHECKS_COMPLETED_V1' and g['passed'] is True
    assert g['inputsUnchanged'] is True and g['primaryError'] is None and g['verificationError'] is None
    request = read(g['request'])
    assert request['sourceMaterialization'] == SELECTION_DOC['sourceMaterialization']
    assert len(g['commands']) == len(m['generatorCommands']) == 10
    for record, expected in zip(g['commands'], m['generatorCommands']):
        assert record['command'] == expected and record['clean'] is True and record['rawExitCode'] == 0
        assert clean_terminal(read(record['terminal']))
        checked(record['stdout'])
        checked(record['stderr'])
        assert record['stderr']['bytes'] == 0 and record['stderr']['sha256'] == hashlib.sha256(b'').hexdigest()
        assert expected['argv'][0] == m['generatorNode']['path'] and expected['argv'][-1] == '--check'
        assert expected['cwd'] == str(WORK / 'native-source') and expected['seconds'] == 120
    checked(m['generatorNode'])
    return g


def expected_tree(role, spec, tool_result, rust_result, corrosion_result, sdk_result):
    root = spec['root']
    if role in ('intl-firefox', 'intl-vendor'):
        expected = read(spec['inventory'])
        checked(spec['provenance'])
        assert expected['root'] == root
        return expected
    if role in ('rust', 'corrosion'):
        doc = rust_result if role == 'rust' else corrosion_result
        assert doc['state'] == 'PRIVATE_TOOL_SOURCE_RECOVERY_VERIFIED_V1' and doc['inputsPreserved'] is True
        assert doc['errors'] == doc['secondaryErrors'] == [] and doc['root'] == root
        return dict(root=root, rootIdentity=doc['rootIdentity'], entries=doc['entries'])
    if role == 'spidermonkey':
        assert sdk_result['state'] == 'EXACT_SELECTED_SPIDERMONKEY_SDK_RECOVERED_DATA_V1' and sdk_result['passed'] is True
        assert sdk_result['root'] == root and sdk_result['files'] == 596 and sdk_result['directories'] == 13
        assert sdk_result['selectedLibraryPreserved'] is True and sdk_result['vanillaLibrarySelected'] is False
        expected = read(sdk_result['inventory'])
        assert expected['root'] == root
        return expected
    matches = [r for r in tool_result['tools'] if r['role'] == role]
    assert len(matches) == 1 and matches[0]['root'] == root
    entries = []
    root_row = None
    for row in matches[0]['rows']:
        if row['relativePath'] == '':
            root_row = row
            continue
        value = dict(path=row['relativePath'], mode=row['mode'], kind='directory' if row['kind'] == 'dir' else row['kind'])
        if row['kind'] == 'file':
            value.update(sha256=row['sha256'], bytes=row['bytes'])
        elif row['kind'] == 'symlink':
            value['target'] = row['link']
        else:
            assert row['kind'] == 'dir', 'unexpected hardlink in selected six archives'
        entries.append(value)
    assert root_row is not None
    return dict(root=root, rootIdentity=dict(mode=root_row['mode']), entries=entries)


def environment(s):
    env = {k: os.environ[k] for k in ('HOME', 'home', 'CODEX_HOME', 'USER', 'LOGNAME') if k in os.environ}
    roots = s['reusedTrees']
    dirs = [str(WORK / 'tools/bin'), str(Path(s['rustc']['path']).parent), str(Path(roots['wasi-sdk']['root']) / 'bin')]
    dirs += list(dict.fromkeys(str(Path(x['executable']['path']).parent) for x in s['hostTools']))
    env.update(CARGO_BUILD_JOBS='1', MAKEFLAGS='-j1', CARGO_INCREMENTAL='0', CCACHE_DISABLE='1', SCCACHE_DISABLE='1', PATH=':'.join(dirs) + ':/usr/bin:/bin', RUSTC=s['rustc']['path'], CARGO_HOME=str(WORK / 'cargo-home'), CARGO_TARGET_DIR=str(WORK / 'rust-target'), CARGO_NET_OFFLINE='true', CARGO_NET_GIT_FETCH_WITH_CLI='false', CPM_SOURCE_CACHE=str(WORK / 'cache'), STARLINGMONKEY_SRC=str(WORK / 'native-source'), SPIDERMONKEY_BINARIES=roots['spidermonkey']['root'], HOST_API='wasi-0.2.10', WPT_ROOT=str(WORK / 'wpt-unused'), TMPDIR=str(WORK / 'tmp'), LC_ALL='C', LANG='C', GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_SYSTEM='/dev/null', GIT_CONFIG_NOSYSTEM='1', GIT_TEMPLATE_DIR=str(WORK / 'git-template'), GIT_CONFIG_COUNT='3', GIT_CONFIG_KEY_0='core.hooksPath', GIT_CONFIG_VALUE_0=str(WORK / 'git-hooks'), GIT_CONFIG_KEY_1='core.fsmonitor', GIT_CONFIG_VALUE_1='false', GIT_CONFIG_KEY_2='maintenance.auto', GIT_CONFIG_VALUE_2='false', GIT_OPTIONAL_LOCKS='0')
    return env


def commands(s):
    cmake = next(t['executable']['path'] for t in s['hostTools'] if t['name'] == 'cmake')
    ninja = next(t['executable']['path'] for t in s['hostTools'] if t['name'] == 'ninja')
    return [
        ('rust-version', [s['rustc']['path'], '--version', '--verbose'], 120),
        ('cargo-version', [s['cargo']['path'], '--version', '--verbose'], 120),
        ('rust-sysroot', [s['rustc']['path'], '--print', 'sysroot'], 120),
        ('configure', [cmake, '-S', str(WORK / 'componentize-source'), '-B', str(WORK / 'build'), '-G', 'Ninja', *['-D' + k + '=' + v for k, v in s['cmakeFlags'].items()]], 2400),
        ('build', [cmake, '--build', str(WORK / 'build'), '--target', 'starlingmonkey_embedding', '--parallel', '1', '--', '-d', 'keeprsp'], 7200),
        ('ninja-commands', [ninja, '-C', str(WORK / 'build'), '-t', 'commands'], 120)]


def phase_worker(packet_path):
    s = selection()
    d = utility()
    packet = read(descriptor(packet_path))
    assert packet['selection'] == SELECTION and packet['entry'] == descriptor(__file__)
    expected = next(c for c in commands(s) if c[0] == packet['label'])
    assert packet['argv'] == expected[1] and packet['cwd'] == str(WORK)
    assert packet['environment'] == environment(s)
    out = WORK / 'results' / packet['label']
    assert packet['output'] == str(out) and out.resolve() == out and out.is_dir()
    life = load(s['lifecycle'], 'genuine_native_disk_lifecycle')
    assert life.MINIMUM_FREE == 800 * 1024**2 and life.REQUIRED_START_FREE == 2 * 1024**3
    samples = []
    def free():
        statv = os.statvfs(WORK)
        size = statv.f_bavail * statv.f_frsize
        samples.append(dict(monotonic=time.monotonic(), bytes=size))
        return size
    with (out / 'command.combined.log').open('xb') as log:
        result = life.monitor_owned_command(packet['argv'], str(WORK), packet['environment'], log, free, minimum_free=STOP_FREE)
        log.flush()
        os.fsync(log.fileno())
    result.update(argv=packet['argv'], diskSamples=samples, rawCombinedLog=descriptor(out / 'command.combined.log'))
    d.save(out / 'worker-result.json', result)
    print(json.dumps(result), flush=True)
    cleanup = result.get('ownedGroupCleanup') or {}
    clean = (cleanup.get('complete') is True and not cleanup.get('events') and not cleanup.get('errors') and not result.get('sigtermReceived') and result.get('stopReason') is None)
    return 0 if result['rawChildExitCode'] == 0 and result['lifecycleComplete'] and clean and not result['launcherErrors'] and not result['stoppedForDiskSpace'] else 1


def phase(owner, s, d, label, argv, env, seconds):
    fs = os.statvfs(WORK)
    assert fs.f_bavail * fs.f_frsize >= STOP_FREE
    out = WORK / 'results' / label
    out.mkdir(mode=0o700)
    d.save(out / 'packet.json', dict(selection=SELECTION, entry=descriptor(__file__), label=label, argv=argv, cwd=str(WORK), environment=env, output=str(out)))
    owned = out / 'owned-monitor'
    owned.mkdir(mode=0o700)
    t = owner.monitor([s['wrapperPython']['path'], '-I', '-B', str(Path(__file__).resolve()), '--worker-packet', str(out / 'packet.json')], str(WORK), env, owned, seconds, SELECTION)
    worker = read(descriptor(out / 'worker-result.json')) if (out / 'worker-result.json').exists() else None
    inner = worker.get('ownedGroupCleanup') or {} if worker else {}
    inner_clean = bool(worker and inner.get('complete') is True and not inner.get('events') and not inner.get('errors') and not worker.get('launcherErrors') and not worker.get('sigtermReceived') and worker.get('stopReason') is None)
    record = dict(label=label, argv=argv, innerOwnedClean=inner_clean, rawExitCode=None if worker is None else worker['rawChildExitCode'], outerTerminal=descriptor(owned / 'terminal.json'), workerResult=descriptor(out / 'worker-result.json') if worker else None, outerRawExitCode=t['rawExitCode'], ownedGone=t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone'], timeout=t['timeout'], forcedCleanup=t['forcedCleanup'], errors=t['errors'], signals=t['signals'], interruptedSignals=t['interruptedSignals'], remainingObservedPids=t['remainingObservedPids'])
    d.save(out / 'phase.json', record)
    return record


def cargo_metadata(owner, s, d, m, env):
    out = WORK / 'results' / 'cargo-metadata'
    out.mkdir(mode=0o700)
    manifest = m['cargo']['manifest']
    argv = [s['cargo']['path'], 'metadata', '--locked', '--offline', '--format-version', '1', '--manifest-path', manifest['path']]
    t = owner.monitor(argv, str(WORK / 'cargo-project'), env, out, 600, SELECTION)
    record = dict(argv=argv, terminal=descriptor(out / 'terminal.json'), stdout=descriptor(out / 'stdout.log'), stderr=descriptor(out / 'stderr.log'), clean=clean_terminal(t))
    d.save(out / 'phase.json', record)
    assert clean_terminal(t), 'fresh offline Cargo metadata owner failed'
    actual = read(record['stdout'])
    assert actual['version'] == 1 and actual['workspace_root'] == str(WORK / 'cargo-project')
    assert actual['target_directory'] == str(WORK / 'rust-target')
    packages = actual['packages']
    assert packages and len({p['id'] for p in packages}) == len(packages)
    ids = {p['id'] for p in packages}
    assert {n['id'] for n in actual['resolve']['nodes']} == ids
    assert all(dep in ids for n in actual['resolve']['nodes'] for dep in n['dependencies'])
    allowed = [WORK / 'cargo-project', WORK / 'native-source', Path(s['reusedTrees']['intl-firefox']['root']), Path(s['reusedTrees']['intl-vendor']['root'])]
    for package in packages:
        p = Path(package['manifest_path'])
        assert p.resolve(strict=True) == p and p.is_file() and any(root in p.parents for root in allowed)
    roots = [p for p in packages if p['manifest_path'] == manifest['path']]
    assert len(roots) == 1 and actual['resolve']['root'] == roots[0]['id']
    reference = tomllib.loads(checked(manifest).read_text())
    assert set(reference['dependencies']) == {'rust-encoding', 'rust-hooks', 'rust-url', 'multipart', 'icu_capi', 'unicode-bidi-ffi'}
    assert {p['name'] for p in roots[0]['dependencies']} == set(reference['dependencies'])
    review = dict(schemaVersion=1, state='FRESH_LOCKED_OFFLINE_CARGO_METADATA_REVIEW_V1', passed=True,
        command=record, sourceMaterialization=s['sourceMaterialization'], manifest=manifest,
        lock=m['cargo']['lock'], config=m['cargo']['config'], packages=len(packages),
        resolveNodes=len(actual['resolve']['nodes']), declaredDependencies=sorted(reference['dependencies']),
        allPackageManifestPathsUnderSelectedSources=True, oldCapsuleProjected=False,
        oldInstallationOrAuthorityClaimed=False)
    d.save(WORK / 'cargo-metadata-review.json', review)
    return review


def configured(m):
    root = WORK / 'build' / 'starling-raw.wasm'
    expected = tomllib.loads(checked(m['cargo']['manifest']).read_text())
    actual = tomllib.loads((root / 'Cargo.toml').read_text())
    assert expected['dependencies']['unicode-bidi-ffi'].get('features', []) == []
    expected['dependencies']['unicode-bidi-ffi']['features'] = []
    assert actual == expected, 'configured aggregate differs from authenticated fresh manifest'
    lock = descriptor(root / 'Cargo.lock')
    assert all(lock[k] == m['cargo']['lock'][k] for k in ('sha256', 'bytes'))
    assert actual['workspace'] == {} and actual['lib'] == {'crate-type': ['staticlib'], 'path': 'rust-staticlib.rs'}
    assert actual['dependencies']['icu_capi']['default-features'] is False
    assert actual['dependencies']['icu_capi']['features'] == ['any_provider', 'compiled_data', 'segmenter', 'calendar']
    return dict(lock=lock, manifest=descriptor(root / 'Cargo.toml'), dependencyNames=list(actual['dependencies']), fullNonPathSemanticsVerified=True, basePathsBoundToCopiedNativeSources=True)


def preflight(s, d):
    old = read(s['predecessorMetadata'])
    assert len(old) == 52 and old['engine']['sha256'] == '237c4e5ace16d6ad20f00e2da08501e6948e29056a5d2aad2a25e55bc894453a'
    m = read(s['sourceMaterialization'])
    assert m['predecessorWholeMetadata'] == s['predecessorMetadata']
    rows = source_rows(m, old)
    validate_generators(s['generatorResult'], m)
    assert s['hostTools'] == old['compilerTools'] and len(s['hostTools']) == 11
    for row in s['hostTools']:
        checked(row['executable'])
    for key in ('cbindgen', 'cpmModule', 'monitor', 'lifecycle', 'wrapperPython', 'cargo', 'rustc'):
        checked(s[key])
    assert s['cbindgen']['sha256'] == '889aa1f25e8d0f0e4c6e304f1032c7d15c708447ce4625b0dd968ffb45b1150b'
    assert s['cpmModule']['sha256'] == '2020b4fc42dba44817983e06342e682ecfc3d2f484a581f11cc5731fbe4dce8a'
    tools = read(s['toolRecoveryResult'])
    assert tools['state'] == 'NATIVE_TOOL_RECOVERY_MATERIALIZED_AND_INVENTORIED_V2' and tools['inputsPreserved'] is True
    assert tools['errors'] == tools['secondaryErrors'] == [] and len(tools['tools']) == 6
    assert tools['toolCommandsExecuted'] is False and tools['nativeBuildExecuted'] is False
    rust = read(s['rustRecoveryResult'])
    corrosion = read(s['corrosionRecoveryResult'])
    sdk = read(s['sdkRecoveryResult'])
    required = {'intl-firefox', 'intl-vendor', 'wasi-sdk', 'binaryen', 'wasm-tools', 'wasmtime', 'weval', 'openssl', 'rust', 'corrosion', 'spidermonkey'}
    assert set(s['reusedTrees']) == required
    snapshots = {}
    for role, spec in s['reusedTrees'].items():
        expected = expected_tree(role, spec, tools, rust, corrosion, sdk)
        actual = d.tree_snapshot(spec['root'])
        assert content(d, expected) == content(d, actual), 'selected tree differs: ' + role
        snapshots[role] = actual
    assert s['cargo']['path'] == str(Path(s['reusedTrees']['rust']['root']) / 'bin/cargo')
    assert s['rustc']['path'] == str(Path(s['reusedTrees']['rust']['root']) / 'bin/rustc')
    flags = s['cmakeFlags']
    assert set(flags) == set(old['requestedCMake'])
    relocated = {'Rust_COMPILER': s['rustc']['path'], 'Rust_CARGO': s['cargo']['path'],
        'NODE_COMPAT_INTL_LOCKFILE': m['cargo']['lock']['path'],
        'NODE_COMPAT_INTL_FIREFOX_SOURCE': s['reusedTrees']['intl-firefox']['root'],
        'CPM_OpenSSL_SOURCE': str(WORK / 'private-openssl/openssl-3.0.17')}
    relocated.update({'CPM_' + role + '_SOURCE': s['reusedTrees'][role]['root'] for role in ('wasi-sdk', 'binaryen', 'wasm-tools', 'wasmtime', 'weval', 'corrosion')})
    assert flags == {**old['requestedCMake'], **relocated}, 'CMake change beyond explicit path relocation'
    config = tomllib.loads(checked(m['cargo']['config']).read_text())
    assert config['source']['intl-vendor']['directory'] == s['reusedTrees']['intl-vendor']['root']
    sdkroot = Path(s['reusedTrees']['spidermonkey']['root'])
    sdkfiles = {r['path']: r for r in snapshots['spidermonkey']['entries'] if r['kind'] == 'file'}
    for name, oldkey in [('libspidermonkey.a', 'actualLibrary'), ('include/js/SavedFrameAPI.h', 'actualSavedFrameHeader'), ('include/js-config.h', 'actualConfigHeader'), ('include/js-confdefs.h', 'actualConfdefs')]:
        assert all(sdkfiles[name][k] == old[oldkey][k] for k in ('sha256', 'bytes'))
    with (sdkroot / 'libspidermonkey.a').open('rb') as f:
        assert f.read(8) == b'!<arch>\n'
    assert re.search(r'^#define JS_HAS_SAVEDFRAME_IS_EVAL 1$', (sdkroot / 'include/js/SavedFrameAPI.h').read_text(), re.M)
    assert re.search(r'^#[ \t]*define[ \t]+JS_HAS_INTL_API[ \t]+1[ \t]*$', (sdkroot / 'include/js-config.h').read_text(), re.M)
    public = [x['relativePath'] for x in old['selectedModuleManifests']['public']]
    private = [x['relativePath'] for x in old['selectedModuleManifests']['private']]
    manifests = d.selected_manifests(dict(selectedPublicManifests=public, selectedPrivateManifests=private), WORK / 'native-source')
    assert [r['wholeManifest'] for r in manifests['public']] == [r['wholeManifest'] for r in old['selectedModuleManifests']['public']]
    assert [r['wholeManifest'] for r in manifests['private']] == [r['wholeManifest'] for r in old['selectedModuleManifests']['private']]
    return old, m, rows, snapshots, manifests


def recheck_files():
    for row in list(INPUTS.values()):
        checked(row)


def fresh_openssl(d, source_root, expected):
    target = WORK / 'private-openssl' / 'openssl-3.0.17'
    target.mkdir(parents=True, mode=0o700)
    for row in expected['entries']:
        relative = d.confined(row['path'])
        path = target / relative
        if row['kind'] == 'directory':
            path.mkdir(parents=True, exist_ok=True, mode=0o700)
        else:
            assert row['kind'] == 'file'
            d.copy_exclusive(dict(path=str(Path(source_root) / relative), sha256=row['sha256'], bytes=row['bytes']), path, row['mode'])
    # Apply directory modes only after child files are copied.
    for row in sorted(expected['entries'], key=lambda r: -len(Path(r['path']).parts)):
        if row['kind'] == 'directory':
            os.chmod(target / row['path'], row['mode'])
    os.chmod(target, expected['rootIdentity']['mode'])
    actual = d.tree_snapshot(target)
    normalized = copy.deepcopy(expected)
    normalized['root'] = str(target)
    assert content(d, actual) == content(d, normalized)
    return dict(sourceRoot=source_root, copiedRoot=str(target), freshPrivateCopy=True, rawBeforeCPMPatch=actual)


def content(d, tree):
    value = d.tree_content(tree)
    value['entries'] = sorted(value['entries'], key=lambda r: r['path'])
    return value


def actual_metadata(s, d, m, old, rows, manifests, trees, result):
    # All 52 values are derived for this run. Legacy capsule/authority slots are
    # explicitly absent, not populated with old receipts or invented admissions.
    native = [r for r in rows if r['role'] == 'native']
    support = [r for r in rows if r['role'] == 'support']
    embedding = [r for r in rows if r['role'] == 'embedding']
    native_manifest = [dict(path=r['relativePath'], sha256=r['target']['sha256'], bytes=r['target']['bytes']) for r in native]
    support_manifest = [dict(relativePath=r['relativePath'], mode=r['mode'], source=r['target']) for r in support]
    embedding_manifest = [dict(relativePath=r['relativePath'], mode=r['mode'], source=r['target']) for r in embedding]
    after = [descriptor(r['target']['path']) for r in native if Path(r['target']['path']).exists()]
    cache = WORK / 'build/CMakeCache.txt'
    database = WORK / 'build/compile_commands.json'
    observed = d.cache_values(cache)
    compile_rows = json.loads(database.read_bytes()) if database.exists() else None
    artifact = WORK / 'componentize-source/lib/starlingmonkey_embedding.wasm'
    result['engineCandidate'] = descriptor(artifact) if artifact.exists() else None
    result['linkInputs'] = [descriptor(p) for p in sorted((WORK / 'build').rglob('*')) if p.is_file() and (p.suffix in ('.a', '.o', '.obj', '.rsp') or p.name in ('Cargo.toml', 'Cargo.lock', 'rust-staticlib.rs'))]
    embedding_rows = None
    if result.get('wholeNinjaCommands'):
        text = checked(result['wholeNinjaCommands']).read_text()
        embedding_rows = [line for line in text.splitlines() if ' -c ' + str(WORK / 'componentize-source/embedding/embedding.cpp') in line]
    if result.get('buildCommandSucceeded'):
        try:
            with artifact.open('rb') as f:
                assert f.read(8) == b'\x00asm\x01\x00\x00\x00'
            assert len(compile_rows) == len({r['file'] for r in compile_rows}) == 80
            assert all(r['file'] in {x['target']['path'] for x in rows} for r in compile_rows)
            assert all(observed.get(k, {}).get('value') == v for k, v in s['cmakeFlags'].items())
            assert len(embedding_rows) == 1
            macro = 'NODE_COMPAT_NATIVE_EXPORT_DIAGNOSTIC_V1'
            definition = '-D' + macro + '=1'
            assert observed[macro] == dict(type='BOOL', value='ON') and s['cmakeFlags'][macro] == 'ON'
            assert [t for t in shlex.split(embedding_rows[0]) if macro in t] == [definition]
            assert not any(macro in t for r in compile_rows for t in (r['arguments'] if 'arguments' in r else shlex.split(r['command'])))
            assert observed.get('Rust_TOOLCHAIN_IS_RUSTUP_MANAGED', {}).get('value') not in ('TRUE', 'ON', '1')
            assert after == [r['target'] for r in native]
            result['configuredRust'] = configured(m)
            result['nativeExportDiagnosticCompileEvidence'] = dict(option=macro, requested='ON', observed=observed[macro], embeddingDefinition=definition, embeddingDefinitionOccurrences=1, separateEmbeddingCommands=1, nativeCompileRows=80, nativeRowsWithDiagnosticDefinition=0, compiledSourceAfterimagesAuthenticated=True)
        except BaseException as error:
            result['postCollectionErrors'].append(dict(type=type(error).__name__, message=str(error), stack=traceback.format_exc()))
    sdk = Path(s['reusedTrees']['spidermonkey']['root'])
    metadata = dict(schemaVersion=1, metadataKind='CLONE_CANCEL_NATIVE_BUILD_ACTUAL_V1',
        sourceComposition=result.get('sourceComposition'), sourceRoot=str(WORK / 'native-source'),
        compiledSourceRoot=str(WORK / 'native-source'), compiledAfterInputs=after,
        compilerTools=s['hostTools'], actualRustTools=dict(cargo=s['cargo'], rustc=s['rustc']),
        nativePolicyInputCount=len(native), nativePolicyInputManifest=native_manifest,
        buildSupportInputCount=len(support), buildSupportInputManifest=support_manifest,
        embeddingInputCount=len(embedding), embeddingInputManifest=embedding_manifest,
        selectedModuleManifests=manifests, requestedCMake=s['cmakeFlags'], observedCMake=observed,
        compileDatabase=descriptor(database) if database.exists() else None, actualCompileRows=compile_rows,
        wholeNinjaCommands=result.get('wholeNinjaCommands'), actualSeparateEmbeddingCompileRows=embedding_rows,
        actualLibrary=descriptor(sdk / 'libspidermonkey.a'), actualSavedFrameHeader=descriptor(sdk / 'include/js/SavedFrameAPI.h'),
        actualConfigHeader=descriptor(sdk / 'include/js-config.h'), actualConfdefs=descriptor(sdk / 'include/js-confdefs.h'),
        patchedSpiderMonkeyEvidence=s['provenance']['historicalPatchedSpiderMonkeyProofRecovered'], savedFramePatchIndex=old.get('savedFramePatchIndex'),
        actualAggregateLock=m.get('cargo', {}).get('lock'), actualRustConfiguration=result.get('configuredRust'),
        offlineCargoConfig=m.get('cargo', {}).get('config'), validatedCargoAudit=result.get('cargoMetadataReview'),
        portableCargoSelection=None, portableCargoAdmission=result.get('freshCargoAdmission'),
        wrapperPython=s['wrapperPython'], buildToolPython=next(r['executable'] for r in s['hostTools'] if r['name'] == 'python3'),
        portableBuildAdmissionVersion=1, logicalCargoAuditDescriptorFromVerifiedCapsule=False,
        validatedCargoProofCapsule=None, validatedCargoProofIndex=None,
        toolTreeInputs=trees, initialTreeProtection=result.get('treeProtectionBefore'),
        originalExtractionWholeTreeAttestationClaimed=False, linkAndRustInputs=result['linkInputs'],
        engine=result.get('engineCandidate'), phases=result['phases'], recipe=descriptor(__file__),
        rootAuthority=None, old83MetadataProjected=False, engineExecuted=False, guestExecuted=False, adoption=False,
        nativeExportDiagnosticCompileEvidence=result.get('nativeExportDiagnosticCompileEvidence'))
    assert len(metadata) == 52
    if old:
        assert set(metadata) == set(old)
    return metadata


def main():
    global SELECTION_DOC
    s = selection()
    SELECTION_DOC = s
    d = utility()
    for name in ('results', 'build', 'metadata.json', 'result.json', 'protected-trees', 'private-openssl', 'build-composition.json'):
        assert not os.path.lexists(WORK / name), 'refuse existing build output: ' + name
    fs = os.statvfs(WORK)
    assert fs.f_bavail * fs.f_frsize >= START_FREE
    os.umask(0o077)
    (WORK / 'results').mkdir(mode=0o700)
    checked(descriptor(__file__))
    result = dict(schemaVersion=1, state='CLONE_CANCEL_NATIVE_BUILD_RUNNING_V1', selection=SELECTION,
        sourceMaterialization=s['sourceMaterialization'], phases=[], primaryError=None, ownerQuiescenceKnown=True,
        postCollectionErrors=[], inputProtection=None, engineOrGuestExecuted=False, adoption=False)
    old, m, rows, before, manifests, trees = {}, {}, [], {}, None, {}
    owner = None
    env = None
    try:
        old, m, rows, before, manifests = preflight(s, d)
        checked(old['savedFramePatchIndex'])
        checked(s['provenance']['historicalPatchedSpiderMonkeyProofRecovered'])
        (WORK / 'protected-trees').mkdir(mode=0o700)
        for role, snapshot in before.items():
            p = WORK / 'protected-trees' / (role + '.json')
            d.save(p, snapshot)
            trees[role] = dict(root=s['reusedTrees'][role]['root'], inventory=descriptor(p), provenance=s['reusedTrees'][role]['provenance'])
            if 'archive' in s['reusedTrees'][role]:
                trees[role]['archive'] = s['reusedTrees'][role]['archive']
        d.save(WORK / 'protection-before.json', before)
        result['treeProtectionBefore'] = descriptor(WORK / 'protection-before.json')
        comp = dict(schemaVersion=1, state='ACTUAL_ONE_AFTERIMAGE_NATIVE_COMPOSITION_V1',
            sourceRoot=str(WORK / 'native-source'), nativeSourceFiles=435,
            files=[dict(path=r['relativePath'], sha256=r['target']['sha256'], bytes=r['target']['bytes']) for r in rows if r['role'] == 'native'],
            inputs=[s['sourceMaterialization'], s['predecessorMetadata']], oneChangedNativePath=REL,
            actualAfterimageSHA256=AFTER_SHA, oldCompositionRetargeted=False)
        d.save(WORK / 'build-composition.json', comp)
        result['sourceComposition'] = descriptor(WORK / 'build-composition.json')
        for name in ('tools/bin', 'rust-target', 'cache/cpm', 'wpt-unused'):
            (WORK / name).mkdir(parents=True, mode=0o700, exist_ok=True)
        copy1 = d.copy_exclusive(s['cbindgen'], WORK / 'tools/bin/cbindgen', 0o755)
        copy2 = d.copy_exclusive(s['cpmModule'], WORK / 'cache/cpm/CPM_0.42.0.cmake', 0o600)
        checked(copy1['target'])
        checked(copy2['target'])
        result['privateOpenSSL'] = fresh_openssl(d, s['reusedTrees']['openssl']['root'], before['openssl'])
        env = environment(s)
        d.save(WORK / 'environment-policy.json', dict(environment=env, privateCargoHome=True, offline=True, rustupInvoked=False))
        owner = load(s['monitor'], 'genuine_original_native_build_owner')
        recheck_files()
        result['ownerQuiescenceKnown'] = False
        review = cargo_metadata(owner, s, d, m, env)
        result['ownerQuiescenceKnown'] = True
        result['freshCargoAdmission'] = review
        result['cargoMetadataReview'] = descriptor(WORK / 'cargo-metadata-review.json')
        recheck_files()
        for label, argv, seconds in commands(s)[:-1]:
            recheck_files()
            result['ownerQuiescenceKnown'] = False
            record = phase(owner, s, d, label, argv, env, seconds)
            result['phases'].append(record)
            result['ownerQuiescenceKnown'] = phase_quiescent(record)
            recheck_files()
            assert d.phase_succeeded(record), label + ' failed'
            text = (WORK / 'results' / label / 'command.combined.log').read_text()
            if label == 'rust-version':
                assert re.search(r'^release: 1\.88\.0$', text, re.M)
            elif label == 'cargo-version':
                assert text.startswith('cargo 1.88.0 ')
            elif label == 'rust-sysroot':
                assert text.strip() == s['reusedTrees']['rust']['root']
            elif label == 'configure':
                result['configuredRust'] = configured(m)
        result['buildCommandSucceeded'] = True
    except BaseException as error:
        result['primaryError'] = dict(type=type(error).__name__, message=str(error), stack=traceback.format_exc())
    finally:
        if owner is not None and result['ownerQuiescenceKnown'] is True and (WORK / 'build/build.ninja').exists():
            try:
                label, argv, seconds = commands(s)[-1]
                result['ownerQuiescenceKnown'] = False
                record = phase(owner, s, d, label, argv, env, seconds)
                result['phases'].append(record)
                result['ownerQuiescenceKnown'] = phase_quiescent(record)
                log = WORK / 'results' / label / 'command.combined.log'
                if log.exists():
                    result['wholeNinjaCommands'] = descriptor(log)
                assert d.phase_succeeded(record), 'ninja commands harvest failed'
            except BaseException as error:
                result['postCollectionErrors'].append(dict(type=type(error).__name__, message=str(error), stack=traceback.format_exc()))
        try:
            metadata = actual_metadata(s, d, m, old, rows, manifests, trees, result)
            d.save(WORK / 'metadata.json', metadata)
            result['metadata'] = descriptor(WORK / 'metadata.json')
        except BaseException as error:
            result['postCollectionErrors'].append(dict(type=type(error).__name__, message=str(error), stack=traceback.format_exc()))
            # Preserve a truthful incomplete 52-slot frame if even raw metadata
            # collection fails. Unknown facts remain None and cannot pass.
            incomplete = dict.fromkeys(METADATA_KEYS)
            incomplete.update(schemaVersion=1, metadataKind='CLONE_CANCEL_NATIVE_BUILD_ACTUAL_INCOMPLETE_V1',
                recipe=descriptor(__file__), requestedCMake=s['cmakeFlags'], phases=result['phases'],
                rootAuthority=None, old83MetadataProjected=False, engineExecuted=False,
                guestExecuted=False, adoption=False, logicalCargoAuditDescriptorFromVerifiedCapsule=False,
                originalExtractionWholeTreeAttestationClaimed=False)
            try:
                d.save(WORK / 'metadata.json', incomplete)
                result['metadata'] = descriptor(WORK / 'metadata.json')
            except BaseException as publication_error:
                result['postCollectionErrors'].append(dict(type=type(publication_error).__name__, message=str(publication_error), stack=traceback.format_exc()))
        protection_errors = []
        try:
            # Membership was proved once before build; expected new engine/build
            # outputs do not belong to the immutable 825-target input set.
            recheck_files()
            for role, snapshot in before.items():
                assert d.tree_snapshot(s['reusedTrees'][role]['root']) == snapshot, 'selected tree changed: ' + role
        except BaseException as error:
            protection_errors.append(dict(type=type(error).__name__, message=str(error), stack=traceback.format_exc()))
        result['inputProtection'] = dict(files=len(INPUTS), wholeTrees=len(before), unchanged=not protection_errors, errors=protection_errors, currentBeforeFinalOnly=True)
        result['passed'] = result.get('buildCommandSucceeded') is True and result['primaryError'] is None and not result['postCollectionErrors'] and not protection_errors
        result['state'] = 'CLONE_CANCEL_NATIVE_BUILD_COMPLETED_RUNTIME_PENDING_V1' if result['passed'] else 'CLONE_CANCEL_NATIVE_BUILD_FAILED_UNACCEPTED_V1'
        try:
            d.save(WORK / 'result.json', result)
        except BaseException:
            if result['primaryError'] is not None:
                print(json.dumps(dict(resultWriteFailed=True, wholeResult=result)), flush=True)
            raise
    print(json.dumps(dict(result=descriptor(WORK / 'result.json'), passed=result['passed'], engine=result.get('engineCandidate'), metadata=result.get('metadata'))), flush=True)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker-packet')
    args = parser.parse_args()
    raise SystemExit(phase_worker(args.worker_packet) if args.worker_packet else main())
