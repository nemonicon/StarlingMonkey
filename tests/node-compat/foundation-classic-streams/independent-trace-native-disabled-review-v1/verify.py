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
PACKET = HERE.parent / 'trace-integration-candidate-v1'
SOURCE = Path('/private/tmp/starling-node-compat/classic-trace-source-v1')
ROOT = Path('/tmp/starling-node-compat/production-classic-trace-v1/native-freeze')
LABELS = ('disabled-off',)
RECIPE = '3694c88b7d000f27e11ffcac835fe0b205b2075f5b1d8d29c61f5b0038ba1cf3'
POLICY = '891a4c53dd4a7b7d776c21003acdd12c7944c6a3eca019a1d9b2be620ed8b11c'
HELPER = '43bae8056534c1a6f384961e0b054a68d44d30030e21897bd9688a8fc8b65bc9'
TOOL_PINS = 'd50e7d7ad946a80c7d7f58c23395ed1bb40ab437e53fc0f84c3a64a9c16e39f1'
PACKET_INDEX = '224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b'
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
    for row in packet_index['files']:
        reader.checked(PACKET / relative(row['path']), row['sha256'], row['bytes'], PACKET)
    tools_index = {'files': [{**row, 'path': row['path'][len('artifact-tools/'):]}
                   for row in packet_index['files'] if row['path'].startswith('artifact-tools/')]}
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
    assert freeze['schema'] == 1 and freeze['state'] == 'immutable-trace-release-engine-frozen'
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
    assert len(tools['toolDependencies']) == 92
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
    assert len(copies) == len(freeze['copies']) == len(planned) == 474
    assert {name: row['sha256'] for name, row in copies.items()} == planned
    for name, row in copies.items():
        reader.checked(ROOT / name, row['sha256'], row['bytes'], ROOT)
        if row['original'] is not None:
            reader.checked(row['original'], row['sha256'], row['bytes'])
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
    rows = [row for row in database if str(Path(row['file'])).startswith((str(SOURCE / 'builtins') + '/', str(SOURCE / 'runtime') + '/')) and row['file'].endswith('.cpp')]
    mapped = {str(Path(row['file']).relative_to(SOURCE)): row['command'] for row in rows}
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
        words = command_words(command, str(SOURCE / source), runtime, enabled and source in PRIVATE, gc and source in PRIVATE)
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
    assert not any(w.startswith('-flto') for w in embedding_words)

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
    assert admission['toolDependenciesVerified'] == 92 and admission['engineBytesRead'] is False and admission['guestExecuted'] is False
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
        assert prior_pin is not None, 'GC also requires reviewed disabled-OFF anchors'
        prior = launch['normalOffFrozenBeforeGCReconfigure']
        assert prior['path'] == str(ROOT / 'disabled-off-freeze-receipt.json')
        assert prior['sha256'] == prior_pin['freezeReceiptSha256']
        assert prior['engineSha256'] == prior_pin['engineSha256']
        prior_freeze = reader.document(ROOT / 'disabled-off-freeze-receipt.json', prior['sha256'], ROOT)
        assert prior_freeze['label'] == 'disabled-off' and prior_freeze['gcStress'] is False
        assert prior_freeze['engineSha256'] == prior['engineSha256']
        reader.checked(ROOT / 'disabled-off.engine.wasm', prior['engineSha256'], prior_pin['engineBytes'], ROOT)
        reader.checked(ROOT / 'disabled-off.engine.wasm.build.json', prior_pin['metadataSha256'], anchor=ROOT)
    trace_checks(reader, metadata, freeze, policy, tools, mapped, embedding_words, launch)
    disabled_checks(reader, metadata, freeze, mapped)
    reader.finish()
    return {'schemaVersion': 1, 'state': 'INDEPENDENT_CORRECTED_TRACE_DISABLED_OFF_NATIVE_FREEZE_VERIFIED_NO_GUEST',
        'verifiedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'label': label,
        'anchors': pin, 'nativeSources': 342, 'externalSources': 3, 'nativeCommands': 61,
        'strictCommands': 4, 'privateTargetCommands': 5, 'embeddingCommands': 1, 'frozenCopies': 474,
        'classicEnabled': enabled, 'gcStress': gc, 'entropyPolicy': metadata['entropyPolicy'],
        'nativeOnlyEvidence': True, 'guestExecuted': False, 'compilerExecuted': False,
        'ninjaExecuted': False, 'producerImported': False, 'sourceAdmissionRerun': False,
        'limitations': ['Recorded finite source admission was rehashed/read, not rerun.',
            'OpenSSL complete-source audit is frozen/reconciled; 4650 original files are not reread.',
            'No component imports, exports, runtime semantics, GC safety, reset or performance verified.',
            'Disabled OFF configuration is read only from label-specific frozen copies.'],
        'verifiedFiles': sorted(reader.files.values(), key=lambda row: row['path'])}


def trace_checks(reader, metadata, freeze, policy, tools, mapped, embedding_words, launch):
    contract = policy['classicTraceSourcePolicy']
    assert metadata['classicTraceSourcePolicy'] == freeze['classicTraceSourcePolicy'] == contract
    assert contract['version'] == 'sm-classic-trace-source-v1'
    old = reader.document(HERE.parent / 'integration-candidate-v1/policy.json', contract['previousPolicySha256'], REPO)
    old_native, native = inventory(old['expectedNativeSourceManifest'], 342), inventory(policy['expectedNativeSourceManifest'], 342)
    assert set(old_native) == set(native)
    delta = {name for name in native if native[name] != old_native[name]}
    changes = {row['path']: row for row in contract['changes']}
    assert len(delta) == 3 and delta == set(changes)
    assert sum(native[name] == old_native[name] for name in native) == 339
    assert policy['strictPolicyVersion'] == old['strictPolicyVersion'] == contract['strictPolicyVersionUnchanged']
    assert policy['protectedPolicyVersion'] == old['protectedPolicyVersion'] == contract['protectedPolicyVersionUnchanged']
    assert policy['embedding'] == old['embedding'] and policy['nativePatchSha256'] == old['nativePatchSha256']
    assert contract['profileVersion'] == policy['profileVersion'] == 'sm-node-22.14.0-m0.12'
    assert contract['moduleSurfaceChanged'] is contract['nativeBoundaryAbiChanged'] is contract['schedulerChanged'] is False
    assert contract['rawVendorFilesChanged'] == 0 and contract['newHostInterfaces'] == []
    for name, row in changes.items():
        assert old_native[name] == row['beforeSha256'] and native[name] == row['afterSha256']
        reader.checked(ROOT / 'source' / name, row['afterSha256'], row['afterBytes'], ROOT)
        reader.checked(PACKET / 'ancestry/native-before' / name, row['beforeSha256'], row['beforeBytes'], PACKET)
    fix = HERE.parent / 'trace-semantics-candidate-v1'
    idx = reader.document(fix / 'index.json', contract['fixSourceIndexSha256'], REPO)
    for row in idx['files']:
        reader.checked(fix / relative(row['path']), row['sha256'], row['bytes'], fix)
    reader.checked(fix / 'canonical-3file.UNAPPLIED.patch', contract['sourceDeltaPatchSha256'], anchor=fix)
    reader.checked(fix / 'transformation-proof.json', contract['transformationProofSha256'], anchor=fix)
    review = HERE.parent / 'independent-trace-semantics-source-review-v1'
    review_idx = reader.document(review / 'index.json', contract['independentFixSourceReviewIndexSha256'], REPO)
    for row in review_idx['files']:
        reader.checked(review / relative(row['path']), row['sha256'], row['bytes'], review)
    # The captured before-build manifests are bytes from the completed disabled-OFF
    # build namespace, compared with its after-build metadata. No reconstruction.
    work = Path(metadata['enginePath']).parent.parent
    stem = Path(metadata['enginePath']).name.removesuffix('.wasm')
    before_native = reader.document(work / ('source-inputs-' + stem + '.json'), metadata['sourceInputManifestSha256'])
    before_ext = reader.document(work / ('componentize-native-inputs-' + stem + '.json'), metadata['componentizeInputManifestSha256'])
    assert before_native == metadata['sourceManifest'] and before_ext == metadata['componentizeSourceManifest']
    assert metadata['sourceInputsCapturedBeforeBuild'] and metadata['componentizeSourcesCapturedBeforeBuild']
    # Reconstruct the checked-in C++ literal from the canonical corrected core
    # and facade, using only Python text operations, not a JS parser/evaluator.
    classic = ROOT / 'source/builtins/node-compat/classic-streams'
    core = (classic / 'classic-core.generated.mjs').read_text()
    facade = (classic / 'classic-streams.mjs').read_text()
    dep = "import {createClassicCore} from './classic-core.generated.mjs';\n"
    assert facade.count(dep) == 1
    facade = re.sub(r'^export function ', 'function ', facade.replace(dep, ''), flags=re.M)
    core_script = re.sub(r'^export function ', 'function ', core, flags=re.M)
    manifest = reader.document(classic / 'export-manifest.classic-streams.node-v22.14.0.json', policy['classicManifestSha256'], ROOT)
    compact = json.dumps(manifest, ensure_ascii=False, separators=(',', ':'))
    canonical_sha = digest((core + '\0' + facade + '\0' + compact).encode())
    factory = "(function(dependencies){\n'use strict';\n" + core_script + '\n' + facade + '\nreturn createClassicStreams(dependencies);\n})'
    header = '// Generated source-only classic candidate; do not edit.\n// Canonical-source SHA-256: ' + canonical_sha + '\nstatic constexpr const char kClassicStreamsFactorySource[] = R"SM_NODE_PROFILE(' + factory + ')SM_NODE_PROFILE";\n'
    assert reader.checked(classic / 'factories.generated.h', native['builtins/node-compat/classic-streams/factories.generated.h'], anchor=ROOT, capture=True) == header.encode()
    semantics = reader.document(classic / 'transformation-receipt.json', native['builtins/node-compat/classic-streams/transformation-receipt.json'], ROOT)
    assert semantics['generatedSha256'] == digest(core.encode()) == '5c0241a73f4cdffc61d7c962bd4d1a1d2015f8fbadef59a4631b7551f9a767b9'
    assert semantics['sourceGraphFiles'] == len(semantics['rawSources']) == len(semantics['transformations']) == 24
    for row in semantics['rawSources']:
        reader.checked(classic / 'vendor' / relative(row['path']), row['sha256'], row['bytes'], ROOT)
    # Preserve source-stage annotations: "uncompiled" is a historical source
    # annotation, not rewritten to manufacture actual runtime acceptance.
    semantic = freeze['semanticSourceProvenance']
    base = ROOT / 'tooling/repository/tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1'
    assert semantic['correctedReceiptAnnotationBase'] == str(base)
    assert semantic['primaryPinsPath'] == str(base / semantics['node22WritableSemanticDelta']['primaryPins'])
    primary = reader.document(semantic['primaryPinsPath'], semantic['primaryPinsSha256'], ROOT)
    assert primary['release'] == 'v22.14.0' and primary['sourceOnly'] is True
    assert len(primary['sources']) == 3
    for row in primary['sources']:
        assert row['url'].startswith('https://raw.githubusercontent.com/nodejs/node/v22.14.0/')
        reader.checked(base / relative(row['path']), row['sha256'], row['bytes'], ROOT)
    reader.checked(semantic['nodeMitNoticePath'], semantic['nodeMitNoticeSha256'], anchor=ROOT)
    assert semantic['nodeMitNoticeSha256'] == native['builtins/node-compat/classic-streams/LICENSE.node']
    # Archive and SDK/header versions are provenance reads, never executed.
    sdk = metadata['wasiSdkVersionFiles']
    assert len(sdk) == 1 and '30.0\n' in sdk[0]['contents'] and 'llvm-version: 21.1.4\n' in sdk[0]['contents']
    assert reader.checked(sdk[0]['path'], capture=True).decode() == sdk[0]['contents']
    definitions = set()
    for cmd in list(mapped.values()) + metadata['actualEmbeddingCompileCommands']:
        words = shlex.split(cmd)
        assert words.count('-include') == 1
        definitions.add(words[words.index('-include') + 1])
        assert [x for x in words if x.startswith('-O')] == ['-O3']
    assert len(definitions) == 1
    for path in definitions:
        data = reader.checked(path, capture=True).decode()
        assert not re.search(r'^\s*#\s*define\s+DEBUG(?:\s|$)', data, re.M)
    for row in metadata['componentizeJsPatches']:
        assert row['applied'] is True and row['files'] == ['embedding/embedding.cpp']
        reader.checked(row['path'], row['sha256'])
    # Core Wasm header is a static file check only.
    assert reader.checked(ROOT / 'disabled-off.engine.wasm', freeze['engineSha256'], freeze['engineBytes'], ROOT, capture=True)[:8] == b'\0asm\x01\0\0\0'
    assert launch['requiredStartFreeBytes'] == 2 * 1024**3 and launch['stopBelowFreeBytes'] == 800 * 1024**2
    assert launch['guestExecutionRequested'] is False and launch['stoppedForDiskSpace'] is False
    build_log = reader.checked(ROOT.parent / 'builds/disabled-off/build.log', launch['logSha256'], capture=True).decode()
    assert '[107/107]' in build_log
    for stem in ('build', 'freeze'):
        for stream in ('stdout', 'stderr'):
            path = Path('/tmp/starling-node-compat/classic-trace-disabled-off-' + stem + '-v1.' + stream + '.log')
            reader.checked(path)
    # Reconcile actual source-admission command with the source captured by
    # the production project. The stored positive result is read, never run.
    admission = freeze['sourceAdmission']
    assert admission['command'] == ['/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node', str(SOURCE / 'tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/artifact-tools/metadata-admission.mjs'), freeze['originalMetadataPath'], 'disabled-off', str(SOURCE)]

def disabled_checks(reader, metadata, freeze, mapped):
    assert metadata['classicStreamsEnabled'] is False and metadata['internalTicksEnabled'] is True
    assert metadata['entropyPolicy'] == 'off' and metadata['gcStress'] is False
    for command in list(mapped.values()) + metadata['actualEmbeddingCompileCommands']:
        words = shlex.split(command)
        macro(words, 'NODE_COMPAT_CLASSIC_STREAMS', False)
        macro(words, 'NODE_COMPAT_INTERNAL_TICKS', True)
        macro(words, 'NODE_COMPAT_ENTROPY_RUNTIME_ONLY', False)
    manifest_records = metadata['selectedModuleManifests']
    assert len(manifest_records) == len({row['path'] for row in manifest_records}) == 8
    names = set()
    for row in manifest_records:
        assert 'classic-streams/' not in row['path']
        document = reader.document(ROOT / 'source' / relative(row['path']), row['sha256'], ROOT)
        assert document['profileVersion'] == row['profileVersion']
        names.update(document['modules'])
    assert 'node:stream' not in names and 'node:stream/promises' not in names
    assert freeze['observedCMakeOptions']['NODE_COMPAT_CLASSIC_STREAMS'] == 'OFF'
    assert metadata['classicStreamsPolicy']['requestedCMake'] == metadata['classicStreamsPolicy']['observedCMake'] == 'OFF'
    admission = reader.document(ROOT / 'disabled-off-source-admission.json', freeze['sourceAdmission']['sha256'], ROOT)
    assert admission['selectedManifestCount'] == 8
    assert admission['classicSourceAdmission']['classicStreamsEnabled'] is False
    assert admission['classicSourceAdmission']['internalTicksEnabled'] is True
    assert admission['classicSourceAdmission']['sourceInputs'] == 342


ANCHORS = {
    'engineSha256': '89a4c37638fad063b127b07c9e2ea95c3a3cc73ffce31c0e301ee23a8893f9a9',
    'engineBytes': 9759216,
    'metadataSha256': '270e2332e9b8d0ac54aa5baaa580a30d07a3de893796916ebef97df46fcb52e4',
    'freezeReceiptSha256': 'fa827b0c2c96c6facaf59064722b679d95be46dc7f79f245fe0e35872fc98bec',
    'launcherResultSha256': '14e80e0e4a0646d1beb8bbd72fc6cffc7d0119b27524781e28e23d94574f0725',
}
if __name__ == '__main__':
    assert len(sys.argv) == 1, 'This reader is finite to the first corrected disabled-OFF freeze.'
    reader = Reader()
    result = verify(reader, 'disabled-off', ANCHORS)
    result['correctedSourceContract'] = 'sm-classic-trace-source-v1'
    result['traceDelta'] = {'changed': 3, 'unchanged': 339, 'rawVendorChanged': 0, 'schedulerChanged': False}
    result['toolDependencies'] = 92
    result['originalCopiesRehashed'] = sum(row['original'] is not None for row in json.loads((ROOT / 'disabled-off-freeze-receipt.json').read_bytes())['copies'])
    result['runtimeAcceptance'] = False
    result['limitations'] += ['Historical source-only/uncompiled annotations are preserved as original provenance, not runtime evidence.',
        'This reader is restricted to disabled-OFF; no enabled OFF, RuntimeOnly, GC or performance acceptance transfers.',
        'Raw command/config provenance is after-build capture except the separately authenticated pre-build source manifests.',
        'SDK js-confdefs bytes and recorded version file were read; no compiler or linker was invoked.']
    target = HERE / 'results.json'
    with target.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps({'state': result['state'], 'paths': len(reader.files), 'copies': 474, 'runtimeAcceptance': False}))
