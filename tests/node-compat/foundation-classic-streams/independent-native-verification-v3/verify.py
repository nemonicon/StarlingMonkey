"""Independent frozen-byte reader; no producer imports, subprocesses or Wasm.

Default pins are null. Actual invocation needs a separately reviewed pins file
and its externally supplied SHA, then creates a fresh result only after checks.
Mutable original cache/database paths in metadata are never dereferenced.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import shlex
import stat
import sys

if not __debug__:
    raise RuntimeError('Verification requires Python assertions enabled')

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PACKET = HERE.parent / 'integration-candidate-v1'
ROOT = Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze')
LABELS = ('normal-off', 'normal-runtime', 'gc-off', 'disabled-off')
RECIPE = '71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
POLICY = '137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f'
HELPER = 'f4a303250ac979206f0c2b358f4dd16d2a5e3a3e3007200901dedba8576b9a1e'
TOOL_PINS = 'f68267eff5126af83c099346d07e5befbf6261ed4ca245e14a68f292f32087e3'
PACKET_INDEX = '5826a3dfc8d79ebbbbd139665dd06f9f493af3aa6f48302f2865611591fcff6d'
TOOLS_INDEX = 'b3404af2d65929903577b5d1bc989218ec30e2e8daa0c1e012a2b8bbb21f9731'
ADAPTER = '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
EXTERNAL = {
    'embedding/embedding.cpp': '9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205',
    'embedding/embedding.h': 'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e',
    'CMakeLists.txt': '4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8',
}
STRICT = {'runtime/engine.cpp', 'runtime/event_loop.cpp', 'runtime/node_tick_queue.cpp',
          'builtins/web/event/event-target.cpp'}
PRIVATE = {'builtins/node-compat/' + name + '.cpp' for name in
           ('buffer', 'entropy-bridge', 'entropy-policy', 'register', 'stream-web-kernel')}
OLD_LICENSES = {
    'builtins/node-compat/LICENSE.assert': '631987b7616a325a5b97566c232418481ddf7dbb5ecadefb991e791876cc2599',
    'builtins/node-compat/LICENSE.events': '631987b7616a325a5b97566c232418481ddf7dbb5ecadefb991e791876cc2599',
    'builtins/node-compat/LICENSE.querystring': '631987b7616a325a5b97566c232418481ddf7dbb5ecadefb991e791876cc2599',
    'builtins/node-compat/LICENSE.stream-web': '21a82bbee91262a076c2e34533d51d73475d55e889f1c42cf884c86b2a0d5773',
    'builtins/node-compat/LICENSE.string-decoder': '21a82bbee91262a076c2e34533d51d73475d55e889f1c42cf884c86b2a0d5773',
    'builtins/node-compat/LICENSE.util': '36ad6fecf56b110df1453be95d352040f2ad0defcf2e5be1321b4cef353a33da',
    'builtins/node-compat/path-vendor/LICENSES.txt': '0012fedcfc3f90565375c6cd9e9cd2e3bb75502b9ea740b98b45126cf6af1565',
}
OPENSSL_LICENSE = '7d5450cb2d142651b8afa315b5f238efc805dad827d91ba367d8516bc9d49e7a'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def hash_text(value):
    assert isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) and value != '0' * 64
    return value


def relative(value):
    assert isinstance(value, str) and value and '\\' not in value and '\0' not in value
    assert not Path(value).is_absolute() and all(part not in ('', '.', '..') for part in value.split('/'))
    return value


def inventory(rows, count=None):
    assert isinstance(rows, list) and (count is None or len(rows) == count)
    result = {}
    for row in rows:
        assert set(row) == {'path', 'sha256'}
        name = relative(row['path'])
        assert name not in result
        result[name] = hash_text(row['sha256'])
    return result


def macro(words, name, enabled):
    assert '-D' not in words and '-U' not in words, 'Split macro operands are not admitted'
    actual = [word for word in words if word == '-D' + name or word.startswith('-D' + name + '=')]
    assert actual == (['-D' + name + '=1'] if enabled else []), name
    assert '-U' + name not in words, name


def command_words(command, source, runtime, classic, gc, require_thin_lto=True):
    words = shlex.split(command)
    assert words.count('-c') == 1 and words[words.index('-c') + 1] == source
    assert words.count('-o') == 1 and '-fsyntax-only' not in words
    assert '-O3' in words and '-DNDEBUG' in words and '-UNDEBUG' not in words
    assert not any(word.startswith('-DDEBUG') for word in words)
    assert '--target=wasm32-wasi' in words
    if require_thin_lto:
        assert '-flto=thin' in words
    for name in ('NODE_COMPAT_INTERNAL_TICKS', 'NODE_COMPAT_STRICT_INITIALIZATION',
                 'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER', 'NODE_COMPAT_ENTROPY_POLICY'):
        macro(words, name, True)
    macro(words, 'NODE_COMPAT_ENTROPY_RUNTIME_ONLY', runtime)
    macro(words, 'NODE_COMPAT_CLASSIC_STREAMS', classic)
    macro(words, 'NODE_COMPAT_GC_STRESS', gc)
    macro(words, 'NODE_COMPAT_OOM_TESTING', False)
    return words


class Reader:
    def __init__(self):
        self.files = {}

    def checked(self, path, checksum=None, size=None, anchor=None, capture=False):
        path = Path(path)
        assert path.is_absolute() and '..' not in path.parts
        if anchor is not None:
            anchor = Path(anchor)
            path.relative_to(anchor)
            cursor = path
            while True:
                assert not cursor.is_symlink(), cursor
                if cursor == anchor:
                    break
                cursor = cursor.parent
            assert anchor.is_dir()
        before = path.lstat()
        assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), path
        value = hashlib.sha256()
        chunks = [] if capture else None
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                value.update(chunk)
                if capture:
                    chunks.append(chunk)
        after = path.lstat()
        stable = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
        assert stable(before) == stable(after), path
        checksum = hash_text(checksum) if checksum is not None else None
        assert checksum is None or value.hexdigest() == checksum, path
        assert size is None or after.st_size == size, path
        row = {'path': str(path), 'sha256': value.hexdigest(), 'bytes': after.st_size}
        assert str(path) not in self.files or self.files[str(path)] == row, 'Input changed between reads'
        self.files[str(path)] = row
        return b''.join(chunks) if capture else row

    def document(self, path, checksum=None, anchor=None):
        return json.loads(self.checked(path, checksum, anchor=anchor, capture=True))

    def finish(self):
        for row in list(self.files.values()):
            self.checked(row['path'], row['sha256'], row['bytes'])


def reviewed_pin(reader, path, expected_sha, label):
    assert label in LABELS
    document = reader.document(path, expected_sha)
    # Deliberately distinct from producer-exported UNREVIEWED candidates and
    # from consumer activation pins. A reviewer supplies this reader's anchors.
    assert document['schemaVersion'] == 1
    assert document['state'] == 'REVIEWED_ACTUAL_CLASSIC_FREEZE_INPUTS_V1', 'Actual artifact anchors have not been reviewed'
    assert set(document['variants']) == set(LABELS)
    pin = document['variants'][label]
    assert isinstance(pin, dict), 'Actual artifact anchors are still null'
    assert set(pin) == {'engineSha256', 'engineBytes', 'metadataSha256', 'freezeReceiptSha256', 'launcherResultSha256'}
    for name, value in pin.items():
        if name == 'engineBytes':
            assert type(value) is int and value > 0
        else:
            hash_text(value)
    return pin


def verify(reader, label, pin, prior_pin=None):
    runtime, gc, enabled = label == 'normal-runtime', label == 'gc-off', label != 'disabled-off'
    packet_index = reader.document(PACKET / 'index.json', PACKET_INDEX, REPO)
    tools_index = reader.document(PACKET / 'artifact-tools/index.json', TOOLS_INDEX, REPO)
    for index, base in ((packet_index, PACKET), (tools_index, PACKET / 'artifact-tools')):
        for row in index['files']:
            reader.checked(base / relative(row['path']), row['sha256'], row['bytes'], base)
    tools = reader.document(PACKET / 'artifact-tools/tool-pins.json', TOOL_PINS, REPO)
    policy = reader.document(PACKET / 'policy.json', POLICY, REPO)
    assert tools['nativeSources'] == 342 and tools['externalSources'] == 3
    assert tools['reviewedEnginePins'] is None and policy['requiredHostInterfaces'] == []
    native = inventory(policy['expectedNativeSourceManifest'], 342)
    cpp = {name for name in native if name.endswith('.cpp') and name.startswith(('runtime/', 'builtins/'))}
    assert len(cpp) == 61 and set(policy['privateTargetCpp']) == PRIVATE

    # Only fixed frozen label paths are used, including after later GC reuse.
    meta_path = ROOT / (label + '.engine.wasm.build.json')
    freeze_path = ROOT / (label + '-freeze-receipt.json')
    metadata = reader.document(meta_path, pin['metadataSha256'], ROOT)
    freeze = reader.document(freeze_path, pin['freezeReceiptSha256'], ROOT)
    assert metadata['buildRecipeSha256'] == RECIPE
    assert metadata.get('diagnosticOnly', False) is False and 'internalTickDiagnosticPolicy' not in metadata
    assert metadata.get('syntheticMetadataOnly', False) is False
    for key in ('profileEnabled', 'pathEnabled', 'eventsEnabled', 'stringDecoderEnabled', 'assertEnabled',
                'querystringEnabled', 'utilEnabled', 'streamWebEnabled', 'internalTicksEnabled', 'strictInitialization',
                'abiFixEnabled', 'bigIntFixEnabled', 'sourceInputsCapturedBeforeBuild',
                'componentizeSourcesCapturedBeforeBuild', 'buildRecipeCheckedBeforeAndAfterBuild'):
        assert metadata[key] is True, key
    for key in ('oomTesting', 'debuggerEnabled', 'wptSupportEnabled'):
        assert metadata[key] is False, key
    assert metadata['classicStreamsEnabled'] is enabled and metadata['gcStress'] is gc
    assert metadata['entropyPolicy'] == ('runtime-only' if runtime else 'off')
    assert metadata['hostApi'] == 'wasi-0.2.10'
    assert inventory(metadata['sourceManifest'], 342) == native
    assert inventory(metadata['componentizeSourceManifest'], 3) == EXTERNAL
    assert freeze['schema'] == 1 and freeze['state'] == 'immutable-release-engine-frozen'
    for key, expected in {'label': label, 'recipeSha256': RECIPE, 'nativeInputsVerified': 342,
            'externalEmbeddingInputsVerified': 3, 'actualLayoutCompileCommands': 61,
            'actualStrictCompileCommands': 4, 'actualEmbeddingCompileCommands': 1,
            'actualClassicPrivateCompileCommands': 5, 'gcStress': gc,
            'classicStreamsEnabled': enabled, 'entropyPolicy': metadata['entropyPolicy'],
            'engineSha256': pin['engineSha256'], 'engineBytes': pin['engineBytes'],
            'receiptSha256': pin['metadataSha256']}.items():
        assert freeze[key] == expected, key
    assert freeze['engine'] == str(ROOT / (label + '.engine.wasm'))
    assert freeze['sourceRoot'] == str(ROOT / 'source')
    assert freeze['componentizeSourceRoot'] == str(ROOT / 'componentize-source')
    assert metadata['engineSha256'] == pin['engineSha256'] and metadata['engineBytes'] == pin['engineBytes']

    planned = {}
    def expect(name, checksum):
        assert name not in planned or planned[name] == checksum
        planned[name] = hash_text(checksum)

    for name, checksum in native.items():
        expect('source/' + name, checksum)
    for name, checksum in EXTERNAL.items():
        expect('componentize-source/' + name, checksum)
    for name, checksum in {'build-engine.sh': RECIPE, 'source-policy.json': POLICY,
                          'source-policy-helper.py': HELPER, 'tooling/wasi_snapshot_preview1.wasm': ADAPTER}.items():
        expect(name, checksum)
    assert len(tools['toolDependencies']) == 23
    for row in tools['toolDependencies']:
        expect('tooling/repository/' + relative(row['path']), row['sha256'])
    assert freeze['toolDependencyClosure'] == [{
        'sourcePath': row['path'], 'path': str(ROOT / 'tooling/repository' / row['path']),
        'sha256': row['sha256'], 'bytes': row['bytes']} for row in tools['toolDependencies']]
    tool_names = ('build-one.py', 'freeze-engine.py', 'artifact_common.py', 'metadata-admission.mjs',
                  'export-pin-candidate.py', 'tool-pins.json', 'parent-inputs.json')
    tool_rows = {row['path']: row for row in tools_index['files']}
    for name in tool_names:
        expect('artifact-tools/' + name, tool_rows[name]['sha256'])
    ancestry = {name: row for name, row in tool_rows.items() if name.startswith('ancestry/production-artifacts-v1/')}
    assert len(ancestry) == 5
    for name, row in ancestry.items():
        expect('artifact-tools/' + name, row['sha256'])
    license_map = {**OLD_LICENSES, **{name: value for name, value in native.items()
                                   if Path(name).name.startswith(('LICENSE', 'NOTICE'))}}
    assert len(license_map) == 9
    expected_licenses = dict(license_map, **{'dependency-licenses/openssl-LICENSE.txt': OPENSSL_LICENSE})
    assert {row['path']: row['sha256'] for row in freeze['licenses']} == expected_licenses
    assert len(freeze['licenses']) == 10
    for name, checksum in license_map.items():
        expect('source/' + name, checksum)
    expect('dependency-licenses/openssl-LICENSE.txt', OPENSSL_LICENSE)

    cache_name, db_name = label + '-CMakeCache.txt', label + '-compile_commands.json'
    expect(cache_name, metadata['cmakeCacheSha256'])
    expect(db_name, metadata['compileCommandsSha256'])
    expect(label + '.engine.wasm', pin['engineSha256'])
    expect(label + '.engine.wasm.build.json', pin['metadataSha256'])
    ev, admission_ref = freeze['postBuildEmbeddingEvidence'], freeze['sourceAdmission']
    expect(label + '-embedding.after.commands.txt', ev['sha256'])
    expect(label + '-source-admission.json', admission_ref['sha256'])
    rust, openssl = metadata['generatedRustProject'], metadata['openssl']
    audit = openssl['completeSourceAudit']
    dep = {'Cargo.toml': rust['manifestSha256'], 'Cargo.lock': rust['lockSha256'],
           'openssl-before.json': audit['beforeReportSha256'], 'openssl-receipt.txt': openssl['receiptSha256'],
           'openssl-configure.txt': openssl['configureRecipe']['sha256'],
           'openssl-configdata.pm': openssl['configdata']['sha256'], 'libcrypto.a': openssl['library']['sha256']}
    for name, checksum in dep.items():
        expect(label + '-' + name, checksum)
    copies = {str(Path(row['path']).relative_to(ROOT)): row for row in freeze['copies']}
    assert len(copies) == len(freeze['copies']) == len(planned) == 405
    assert {name: row['sha256'] for name, row in copies.items()} == planned
    for name, row in copies.items():
        reader.checked(ROOT / name, row['sha256'], row['bytes'], ROOT)
        assert row['shared'] is (not name.startswith(label + '-') and not name.startswith(label + '.'))
    # Engine byte read is now justified by fixed pins + exact source membership.
    with (ROOT / (label + '.engine.wasm')).open('rb') as stream:
        assert stream.read(8) == b'\0asm\x01\0\0\0'

    cache = {}
    for line in (ROOT / cache_name).read_text().splitlines():
        key, colon, tail = line.partition(':')
        if colon and '=' in tail:
            assert key not in cache
            cache[key] = tail.partition('=')[2]
    assert metadata['requestedCMakeOptions'] == metadata['observedCMakeOptions'] == freeze['observedCMakeOptions']
    for key, value in metadata['observedCMakeOptions'].items():
        assert cache[key] == value, key
    required = {'CMAKE_BUILD_TYPE': 'Release', 'WEVAL': 'OFF', 'USE_WASM_OPT': 'ON',
        'ENABLE_BUILTIN_NODE_COMPAT': 'ON', 'NODE_COMPAT_LOCKED_RUST': 'ON', 'NODE_COMPAT_INTERNAL_TICKS': 'ON',
        'NODE_COMPAT_GC_STRESS': 'ON' if gc else 'OFF', 'NODE_COMPAT_CLASSIC_STREAMS': 'ON' if enabled else 'OFF',
        'NODE_COMPAT_ENTROPY_MODE': 'RUNTIME_ONLY' if runtime else 'OFF', 'NODE_COMPAT_OOM_TESTING': 'OFF',
        'ENABLE_JS_DEBUGGER': 'OFF', 'ENABLE_BUILTIN_WPT_SUPPORT': 'OFF',
        **{'NODE_COMPAT_' + name: 'ON' for name in ('PATH', 'EVENTS', 'STRING_DECODER', 'ASSERT', 'QUERYSTRING', 'UTIL', 'STREAM_WEB')}}
    for key, value in required.items():
        assert cache[key] == value, key
    assert not cache.get('CMAKE_PROJECT_ComponentizeJS_INCLUDE', '')
    assert cache.get('ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS', 'OFF') == 'OFF'
    assert '--threads=1' not in cache.get('CMAKE_EXE_LINKER_FLAGS', '')
    database = reader.document(ROOT / db_name, metadata['compileCommandsSha256'], ROOT)
    rows = [row for row in database if str(Path(row['file'])).startswith((str(REPO / 'builtins') + '/', str(REPO / 'runtime') + '/')) and row['file'].endswith('.cpp')]
    mapped = {str(Path(row['file']).relative_to(REPO)): row['command'] for row in rows}
    assert len(mapped) == len(rows) == 61 and set(mapped) == cpp
    layout = [row['command'] for row in rows]
    ticks, strict, protected, classic = [metadata[name] for name in
        ('internalTickPolicy', 'strictEventExceptionPolicy', 'protectedAbortListenerPolicy', 'classicStreamsPolicy')]
    assert ticks['version'] == policy['version'] and ticks['enabled'] is True
    assert ticks['addsExternalCapabilities'] is False and ticks['publicProcessModule'] is False
    assert ticks['resetSafeReuse'].startswith('OPEN')
    assert strict['version'] == policy['strictPolicyVersion']
    assert protected['version'] == policy['protectedPolicyVersion'] and protected['strictPolicyVersion'] == strict['version']
    assert classic['version'] == policy['classicPolicyVersion'] and classic['enabled'] is enabled
    for obj in (ticks, classic):
        assert obj['policyFileSha256'] == POLICY and obj['helperSha256'] == HELPER
        assert obj['nativePatchSha256'] == policy['nativePatchSha256']
    assert classic['addsExternalCapabilities'] is False and classic['publicProcessModule'] is False
    assert classic['moduleManifest'] == policy['classicManifest']
    assert ticks['sourceLayer'] == policy['sourceLayer'] and ticks['limits'] == policy['limits']
    assert ticks['embeddingAfterSha256'] == EXTERNAL['embedding/embedding.cpp']
    parent_pins = reader.document(ROOT / 'tooling/repository/tests/node-compat/foundation-scheduler/admission-candidate-v1/pins.json', anchor=ROOT)
    assert strict['parentSourcePolicy'] == parent_pins['parentStrict']
    assert protected['parentSourcePolicy'] == parent_pins['parentProtected']
    strict_names = set(parent_pins['parentStrict']['nativeSourceSha256']) | {'runtime/node_tick_queue.cpp', 'runtime/node_tick_queue.h'}
    assert strict['nativeSourceSha256'] == {name: native[name] for name in strict_names}
    assert protected['sourceSha256'] == {name: native[name] for name in parent_pins['parentProtected']['sourceSha256']}
    assert strict['patchSha256'] == parent_pins['parentStrict']['patchSha256']
    assert protected['patchSha256'] == parent_pins['parentProtected']['patchSha256']
    assert ticks['actualLayoutCompileCommands'] == protected['actualLayoutCompileCommands'] == layout
    assert ticks['actualQueueCompileCommands'] == [mapped['runtime/node_tick_queue.cpp']]
    assert sorted(strict['actualNativeCompileCommands']) == sorted(mapped[name] for name in STRICT)
    assert sorted(classic['actualPrivateTargetCompileCommands']) == sorted(mapped[name] for name in PRIVATE)
    assert metadata['actualRegistrationCompileCommands'] == classic['actualRegistrationCompileCommands'] == [mapped['builtins/node-compat/register.cpp']]
    for source, command in mapped.items():
        words = command_words(command, str(REPO / source), runtime, enabled and source in PRIVATE, gc and source in PRIVATE)
        macro(words, 'NODE_COMPAT_STREAM_WEB', source in PRIVATE)
    assert ev['version'] == 'production-after-build-parent-ninja-v1' and ev['beforeBuildCaptureExists'] is False
    assert ev['exitCode'] == 0 and ev['stderr'] == ''
    assert ev['command'] == ['ninja', '-C', str(Path(metadata['cmakeCachePath']).parent), '-t', 'commands', 'builtin_componentize_embedding']
    assert ev['path'] == str(ROOT / (label + '-embedding.after.commands.txt'))
    source = str(Path(cache['CMAKE_HOME_DIRECTORY']) / 'embedding/embedding.cpp')
    assert ev['sourcePath'] == source
    raw = reader.checked(ev['path'], ev['sha256'], ev['bytes'], ROOT, capture=True).decode()
    embedding = []
    for line in raw.splitlines():
        words = shlex.split(line)
        if words.count('-c') == 1 and words[words.index('-c') + 1] == source:
            embedding.append(line)
    assert len(embedding) == 1 and embedding == ev['compileCommands'] == metadata['actualEmbeddingCompileCommands']
    assert embedding == ticks['actualEmbeddingCompileCommands'] == protected['actualEmbeddingCompileCommands']
    assert not any(row['file'] == source for row in database)
    embedding_words = command_words(embedding[0], source, runtime, False, False, require_thin_lto=False)
    macro(embedding_words, 'NODE_COMPAT_STREAM_WEB', False)

    assert rust['cargoBuildLocked'] is True and rust['manifestAndLockCheckedBeforeAndAfterBuild'] is True
    assert rust['lockSha256'] == rust['versionedLockSha256'] == native['runtime/crates/staticlib-template/Cargo.lock']
    assert rust['actualCargoBuildCommands'] and all('--release --locked' in value for value in rust['actualCargoBuildCommands'])
    assert audit['beforeAndAfterBuild'] is True and audit['sourceFilesVerified'] == 4650
    assert audit['receiptSha256'] == openssl['receiptSha256'] and audit['sourceDirectory'] == openssl['sourceDir']
    before = reader.document(ROOT / (label + '-openssl-before.json'), audit['beforeReportSha256'], ROOT)
    assert before['state'] == 'verified-complete-source' and before['missingFiles'] == before['unexpectedFiles'] == []
    for key, value in before.items():
        assert audit[key] == value
    assert freeze['dependencyReferences'] == [{'kind': 'linked-libcrypto-frozen-copy', **openssl['library'], 'frozenPath': str(ROOT / (label + '-libcrypto.a'))}]
    assert copies[label + '-libcrypto.a']['bytes'] == openssl['library']['bytes']
    assert native['host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'] == ADAPTER
    assert copies['tooling/wasi_snapshot_preview1.wasm']['bytes'] == 53512
    assert freeze['toolingInputs'][0]['additionalNativeInput'] is False
    assert freeze['toolingInputs'][0]['doesNotReplaceLiveRuntimeSeal'] is True
    assert freeze['helperSha256'] == tool_rows['freeze-engine.py']['sha256']
    assert freeze['originalReceiptPreserved'] is True and freeze['allInputsValidatedBeforeCopies'] is True
    assert freeze['allCopiesAndOriginalsRehashed'] is True and freeze['guestExecutedByHelper'] is False
    admission = reader.document(ROOT / (label + '-source-admission.json'), admission_ref['sha256'], ROOT)
    assert admission_ref['path'] == str(ROOT / (label + '-source-admission.json'))
    assert admission['state'] == 'ACTUAL_FINITE_CLASSIC_SOURCE_SELECTOR_PASSED_NO_ENGINE_EXECUTION'
    assert admission['label'] == label and admission['sourceFiles'] == 342
    assert admission['options'] == {'gcStress': gc, 'entropyPolicy': metadata['entropyPolicy'], 'classicStreamsEnabled': enabled}
    assert admission['policySha256'] == POLICY and admission['toolPinsSha256'] == TOOL_PINS
    assert admission['toolDependenciesVerified'] == 23 and admission['engineBytesRead'] is False and admission['guestExecuted'] is False
    assert admission['selectedManifestCount'] == (9 if enabled else 8)
    assert admission['coreExpectations']['coreVersion'] == freeze['coreVersion'] == 'sm-node-22.14.0-m0.11'
    assert admission['coreExpectations']['allocUnsafePolicy'] == 'zeroed-no-pool-direct-u8-v1'
    assert admission['coreExpectations']['sourceHashes'] == freeze['coreSources']
    for name, field in [('tests/node-compat/module-selection.mjs', 'selectorSourceSha256'), ('tests/node-compat/classic-streams-admission.mjs', 'admissionSourceSha256')]:
        assert admission[field] == next(row['sha256'] for row in tools['toolDependencies'] if row['path'] == name)

    launch_root = ROOT.parent / 'builds' / label
    launch = reader.document(launch_root / 'result.json', pin['launcherResultSha256'], launch_root)
    assert launch['state'] == 'native-build-completed-runtime-pending'
    assert launch['rawChildExitCode'] == launch['status'] == launch['launcherExitCode'] == 0
    assert launch['label'] == label and launch['recipeSha256'] == RECIPE
    assert launch['evidenceComplete'] is True and launch['lifecycleComplete'] is True
    assert launch['ownedGroupCleanup']['complete'] is True and launch['launcherErrors'] == []
    reader.checked(launch_root / 'build.log', launch['logSha256'], anchor=launch_root)
    env = launch['explicitEnvironment']
    for key in ('NODE_COMPAT_JOBS', 'BINARYEN_CORES', 'RAYON_NUM_THREADS', 'CARGO_BUILD_JOBS'):
        assert env[key] == '1'
    assert env['NODE_COMPAT_CLASSIC_STREAMS'] == ('1' if enabled else '0')
    assert env['NODE_COMPAT_GC_STRESS'] == ('1' if gc else '0')
    assert env['NODE_COMPAT_ENTROPY_MODE'] == ('RUNTIME_ONLY' if runtime else 'OFF')
    assert env['NODE_COMPAT_INTERNAL_TICKS'] == '1' and env['NODE_COMPAT_OOM_TESTING'] == '0'
    if gc:
        # The launcher preserves a prior OFF receipt/engine digest before reuse.
        assert prior_pin is not None, 'GC also requires reviewed normal-OFF anchors'
        prior = launch['normalOffFrozenBeforeGCReconfigure']
        assert prior['path'] == str(ROOT / 'normal-off-freeze-receipt.json')
        assert prior['sha256'] == prior_pin['freezeReceiptSha256']
        assert prior['engineSha256'] == prior_pin['engineSha256']
        prior_freeze = reader.document(ROOT / 'normal-off-freeze-receipt.json', prior['sha256'], ROOT)
        assert prior_freeze['label'] == 'normal-off' and prior_freeze['gcStress'] is False
        assert prior_freeze['engineSha256'] == prior['engineSha256']
        reader.checked(ROOT / 'normal-off.engine.wasm', prior['engineSha256'], prior_pin['engineBytes'], ROOT)
        reader.checked(ROOT / 'normal-off.engine.wasm.build.json', prior_pin['metadataSha256'], anchor=ROOT)
    reader.finish()
    return {'schemaVersion': 1, 'state': 'INDEPENDENT_CLASSIC_NATIVE_FREEZE_VERIFIED_NO_GUEST',
        'verifiedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'label': label,
        'anchors': pin, 'nativeSources': 342, 'externalSources': 3, 'nativeCommands': 61,
        'strictCommands': 4, 'privateTargetCommands': 5, 'embeddingCommands': 1, 'frozenCopies': 405,
        'classicEnabled': enabled, 'gcStress': gc, 'entropyPolicy': metadata['entropyPolicy'],
        'nativeOnlyEvidence': True, 'guestExecuted': False, 'compilerExecuted': False,
        'ninjaExecuted': False, 'producerImported': False, 'sourceAdmissionRerun': False,
        'limitations': ['Recorded finite source admission was rehashed/read, not rerun.',
            'OpenSSL complete-source audit is frozen/reconciled; 4650 original files are not reread.',
            'No component imports, exports, runtime semantics, GC safety, reset or performance verified.',
            'Normal OFF configuration is read only from label-specific frozen copies.'],
        'verifiedFiles': sorted(reader.files.values(), key=lambda row: row['path'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('label', choices=LABELS)
    parser.add_argument('--pins', type=Path, default=HERE / 'actual-pins.json')
    parser.add_argument('--pins-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    reader = Reader()
    # Fail before artifact paths/output creation when actual pins remain null.
    pin = reviewed_pin(reader, args.pins.absolute(), hash_text(args.pins_sha256), args.label)
    prior_pin = reviewed_pin(reader, args.pins.absolute(), args.pins_sha256, 'normal-off') if args.label == 'gc-off' else None
    output = args.output.absolute()
    assert output.is_relative_to(HERE) and not output.exists() and not output.is_symlink()
    result = verify(reader, args.label, pin, prior_pin)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'state': result['state'], 'output': str(output), 'files': len(reader.files)}))


if __name__ == '__main__':
    main()
