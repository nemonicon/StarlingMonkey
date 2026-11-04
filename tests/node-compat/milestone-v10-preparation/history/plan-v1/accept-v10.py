#!/usr/bin/env python3
"""UNEXECUTED preparation: verify bounded m10 evidence; --apply writes a NEW archive.

Default performs read-only verification/planning. Never starts a host, build,
componentizer, compiler, guest, or fault probe. Root must review before use.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import shutil
import stat

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = Path('/tmp/starling-node-compat/foundations-v10')
FREEZE = BASE / 'native-freeze'
TESTS = REPO / 'tests/node-compat'
FOCUSED = TESTS / 'foundation-add-abort/production-native-m0.10'
CORRECTION = TESTS / 'foundation-add-abort/production-adoption-m0.10/cmake-harness-correction-v1'
DESTINATION = TESTS / 'milestones/foundations-v10'
STAGE = DESTINATION.with_name('.foundations-v10-staging')
RECIPE = '354cbc8c5317bf14f022fd14a9687e382b99c2141135629b56bb541ef6308754'
HTTP_SHA = '0fcad53793003261f6f664ffadc758ae9fe3c6e1b7dd9f6599528f5a35075610'
HTTP_BYTES = 63626509
IMPORTS = sorted(['wasi:clocks/monotonic-clock@0.2.10', 'wasi:http/types@0.2.10',
                 'wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10',
                 'wasi:io/streams@0.2.10', 'wasi:random/random@0.2.10'])
ENGINES = {
    'off-foundations': '1098e7531004a4ca1b47f2ca80527a01e64cd3392d28d760da37326c08a85154',
    'runtime-foundations': 'dc5f834d84e43c34a0019176e082743e72cc9f1c284bfa3331d368d5416866a9',
    'gc-foundations': '5dc29ba071bf85ad88a25d12d17346e164391e9c40044ba2c642fe14025df4f8',
    'events-off-control': 'b2944204fafb110cc5bb182d5cc8381a2fc6704c264344bb649fa3eaca6cc762',
}
# These small already-versioned INPUTS are required for a complete 304-input
# source archive. They are not generated engines/application components.
SOURCE_BINARY_ASSETS = {
    'host-apis/wasi-0.2.0/bindings/bindings_component_type.o': 'dee3d7637a59067637e96a5b9dfe5f33f8e7675dea8caee7cc7b43ac487b3c1b',
    'host-apis/wasi-0.2.3/bindings/bindings_component_type.o': 'adeca9727f8da755e04e1954dba0de170519e953be11ebc9dea1e476d44457ca',
    'host-apis/wasi-0.2.10/bindings/bindings_component_type.o': 'c48f1ae980766fdb2decaa417fe0eaf618a56e26cb7f36c329c92a1ff60439c2',
    'host-apis/wasi-0.2.0/preview1-adapter-debug/wasi_snapshot_preview1.wasm': '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0',
    'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm': '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0',
}
LAYOUT_MACRO = '-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1'
BINARY_SUFFIXES = {'.wasm', '.cwasm', '.o', '.obj', '.a', '.so', '.dylib', '.exe', '.pyc'}
SKIP_DIRS = {'node_modules', '__pycache__', '.git', 'target'}


def sha(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def json_file(path):
    assert_regular(path)
    return json.loads(Path(path).read_text())


def assert_regular(path):
    path = Path(path)
    value = path.lstat()
    assert stat.S_ISREG(value.st_mode) and not stat.S_ISLNK(value.st_mode), path
    return value


def no_link_components(path, root):
    path, root = Path(path), Path(root)
    relative = path.relative_to(root)
    cursor = root
    assert not cursor.is_symlink(), cursor
    for part in relative.parts:
        cursor /= part
        assert not cursor.is_symlink(), cursor


def binary(path):
    path = Path(path)
    if path.suffix.lower() in BINARY_SUFFIXES:
        return True
    with open(path, 'rb') as stream:
        magic = stream.read(4)
    return magic in {b'\0asm', b'\x7fELF', b'\xcf\xfa\xed\xfe', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'MZ\x90\0'}


def entries_without_links(root, omitted):
    root = Path(root)
    assert root.is_dir() and not root.is_symlink(), root
    for parent, directories, names in os.walk(root, followlinks=False):
        retained = []
        for name in sorted(directories):
            path = Path(parent) / name
            if path.is_symlink() or name in SKIP_DIRS:
                omitted.append({'path': str(path), 'reason': 'symlink-or-generated-dependency-directory'})
            else:
                retained.append(name)
        directories[:] = retained
        for name in sorted(names):
            path = Path(parent) / name
            value = path.lstat()
            if not stat.S_ISREG(value.st_mode) or stat.S_ISLNK(value.st_mode):
                omitted.append({'path': str(path), 'reason': 'not-a-regular-nonsymlink-file'})
            else:
                yield path


def fatal_assertions(value):
    assert value['jcoChild']['status'] == 0
    assert 'EXPECTED_FATAL_DISCARD' in value['jcoChild']['stdout']
    assert value['wasmtime']['status'] != 0
    assert 'unreachable' in value['wasmtime']['stderr']


def validate():
    assert not DESTINATION.exists() and not STAGE.exists(), 'Never overwrite an accepted archive or existing staging'
    files = {
        'release-index.json': BASE / 'release-gates-v1/results.json',
        'optional-index.json': BASE / 'release-gates-v1/optional/results.json',
        'focused-evidence.json': FOCUSED / 'evidence-receipt.json',
        'http-audit.json': BASE / 'http-joint/component-audit.json',
        'wasmtime-http.json': BASE / 'http-joint/wasmtime-v2/wasmtime-results.json',
        'wasmcloud-http.json': BASE / 'http-joint-wasmcloud-results.json',
        'http-summary.json': TESTS / 'foundations/http-v10-results.json',
        'http-index.json': TESTS / 'foundations/http-v10-index.json',
        'selection.json': Path('/tmp/starling-node-compat/m0.10-source-selection.json'),
        'cmake-policy.json': CORRECTION / 'passed-configure-results.json',
        'cmake-validation.json': CORRECTION / 'validation-receipt.json',
    }
    engines = {}
    for label, digest in ENGINES.items():
        path = FREEZE / (label + '.engine.wasm.build.json')
        engine = json_file(path)
        assert engine['engineSha256'] == sha(FREEZE / (label + '.engine.wasm')) == digest
        assert engine['buildRecipeSha256'] == RECIPE
        assert engine['observedCMakeOptions']['CMAKE_BUILD_TYPE'] == 'Release'
        assert engine['observedCMakeOptions']['WEVAL'] == 'OFF'
        assert engine['observedCMakeOptions']['NODE_COMPAT_LOCKED_RUST'] == 'ON'
        assert not engine['oomTesting'] and not engine['debuggerEnabled'] and engine['strictInitialization']
        assert engine['strictEventExceptionPolicy']['version'] == 'sm-uncaught-event-v3-protected-abort-v2'
        assert engine['sourceInputsCapturedBeforeBuild'] and engine['componentizeSourcesCapturedBeforeBuild']
        assert engine['buildRecipeCheckedBeforeAndAfterBuild']
        assert sha(FREEZE / (label + '-CMakeCache.txt')) == engine['cmakeCacheSha256']
        assert sha(FREEZE / (label + '-compile_commands.json')) == engine['compileCommandsSha256']
        expected_events = label != 'events-off-control'
        assert engine['eventsEnabled'] is expected_events and engine['protectedAbortListenerEnabled'] is expected_events
        assert engine['gcStress'] is (label == 'gc-foundations')
        assert engine['entropyPolicy'] == ('runtime-only' if label == 'runtime-foundations' else 'off')
        commands = json_file(FREEZE / (label + '-compile_commands.json'))
        layout_paths = [item['path'] for item in engine['sourceManifest']
                        if item['path'].endswith('.cpp') and item['path'].startswith(('builtins/', 'runtime/'))]
        layout = [entry for entry in commands if any(entry['file'].endswith('/' + path) for path in layout_paths)]
        assert len(layout) == 60
        assert [entry['command'] for entry in layout] == engine['protectedAbortListenerPolicy']['actualLayoutCompileCommands']
        for entry in layout:
            command = entry.get('command') or ' '.join(entry['arguments'])
            assert (LAYOUT_MACRO in shlex.split(command)) is expected_events, entry['file']
        assert len(engine['actualEmbeddingCompileCommands']) == 1
        assert all((LAYOUT_MACRO in shlex.split(command)) is expected_events for command in engine['actualEmbeddingCompileCommands'])
        engines[label] = engine
        files['engine-' + label + '.json'] = path
    off = engines['off-foundations']
    assert all(engine['sourceManifest'] == off['sourceManifest'] for engine in engines.values())
    assert len(off['sourceManifest']) == 304 and len({item['path'] for item in off['sourceManifest']}) == 304
    assert all(engine['componentizeSourceManifest'] == off['componentizeSourceManifest'] for engine in engines.values())
    for item in off['sourceManifest']:
        no_link_components(FREEZE / 'source' / item['path'], FREEZE / 'source')
        no_link_components(REPO / item['path'], REPO)
        assert sha(FREEZE / 'source' / item['path']) == sha(REPO / item['path']) == item['sha256']
    for item in off['componentizeSourceManifest']:
        assert sha(FREEZE / 'componentize-source' / item['path']) == item['sha256']
    assert sha(FREEZE / 'build-engine.sh') == sha(TESTS / 'build-engine.sh') == RECIPE
    for item in json_file(FREEZE / 'licenses.json')['files']:
        assert sha(FREEZE / 'source' / item['path']) == item['sha256']

    reports = {name: json_file(path) for name, path in files.items()}
    release = reports['release-index.json']
    assert release['state'] == 'passed' and len(release['jobs']) == 8
    assert {job['name'] for job in release['jobs']} == {'core', 'allocator', 'stream-web', 'optional', 'strict-sync', 'strict-runtime', 'strict-late', 'strict-callbacks'}
    for job in release['jobs']:
        assert job['code'] == 0 and job['signal'] is None
        assert sha(Path(job['reportPath'])) == job['reportSha256']
        assert sha(Path(job['logPath'])) == job['logSha256']
        assert sha(Path(job['runner'])) == job['runnerSha256']
        if job['name'] != 'optional':
            files['release-' + job['name'] + '.json'] = Path(job['reportPath'])
        if job['name'] != 'optional':
            assert json_file(job['reportPath'])['engineSha256'] == off['engineSha256']
        assert job['emittedImports'] == []
    assert sum(job['finalComponentAudits'] for job in release['jobs'] if job['name'].startswith('strict-')) == 24
    optional = reports['optional-index.json']
    assert optional['state'] == 'passed' and len(optional['modules']) == 6 and optional['failedAttempts'] == []
    assert optional['nativeInputsVerifiedBeforeAfter'] and optional['nativeInputs'] == 304
    assert sum(module['finalComponentAudits'] for module in optional['modules']) == 10
    for module in optional['modules']:
        assert module['code'] == 0 and sha(Path(module['reportPath'])) == module['reportSha256']
        assert module['emittedImports'] == []
        files[module['name'] + '.json'] = Path(module['reportPath'])
    selection = reports['selection.json']
    assert selection['tests'] == selection['passed'] == 328 and selection['failures'] == []
    correction = reports['cmake-validation.json']
    assert correction['state'] == 'corrected-test-rerun-passed' and correction['cases'] == 19
    assert correction['recipeSha256'] == RECIPE and correction['cmakeSourceSha256'] == sha(REPO / 'cmake/builtins.cmake')
    assert sha(files['cmake-policy.json']) == correction['fullReportSha256']
    assert sha(BASE / 'cmake-policy-results.json') == correction['fullReportSha256']
    assert len(reports['cmake-policy.json']['cases']) == 19

    focused = reports['focused-evidence.json']
    assert focused['state'] == 'BOUNDED_M10_NATIVE_EVIDENCE_COMPLETE_WITH_CONFIRMED_CALLBACK_RETURN_LIMITATION'
    assert focused['allFourNativeInputManifestsIdentical'] and focused['all304FrozenAndCurrentSourcesVerified']
    assert focused['nativeSourceManifest'] == off['sourceManifest'] and focused['recipeSha256'] == RECIPE
    assert sha(FREEZE / 'licenses.json') == focused['licensesSha256']
    assert len(focused['engines']) == 4 and {item['label'] for item in focused['engines']} == set(ENGINES)
    assert len(focused['validationSourceFiles']) == 16
    assert len({item['path'] for item in focused['validationSourceFiles']}) == 16
    assert len({item['saved'] for item in focused['validationSourceFiles']}) == 16
    expected_focused_reports = {'native-off-results.json', 'native-runtime-results.json', 'native-gc-results.json',
                                'events-off-results.json', 'callback-return-results.json'}
    assert len(focused['reports']) == 5 and {item['path'] for item in focused['reports']} == expected_focused_reports
    assert len(focused['components']) == focused['counts']['emittedApplicationComponents'] == 20
    assert len({Path(item['path']).resolve() for item in focused['components']}) == 20
    assert {item['report'] for item in focused['components']} == expected_focused_reports
    for name, count in {'native-off-results.json': 8, 'native-runtime-results.json': 8, 'native-gc-results.json': 2,
                        'events-off-results.json': 1, 'callback-return-results.json': 1}.items():
        assert sum(item['report'] == name for item in focused['components']) == count, name
    assert focused['counts']['auditedPackagerComponentsCountedSeparately'] == 1
    for item in focused['engines']:
        assert item['sha256'] == ENGINES[item['label']]
        assert sha(Path(item['path'] + '.build.json')) == item['metadataSha256']
    for item in focused['validationSourceFiles']:
        assert sha(FOCUSED / item['path']) == sha(FOCUSED / item['saved']) == item['sha256']
    assert sha(FOCUSED / 'README.md') == focused['readmeSha256']
    for item in focused['reports']:
        assert sha(FOCUSED / item['path']) == sha(Path(item['externalPath'])) == item['sha256']
        files['focused-' + item['path']] = FOCUSED / item['path']
    for item in focused['components']:
        assert sha(Path(item['path'])) == item['sha256']
        assert item['emittedImports'] == (['wasi:random/random@0.2.10'] if item['report'] == 'native-runtime-results.json' else [])
    expected_counts = {'nodeDifferentialGroups': 29, 'ordinaryEntropyModes': 2, 'ordinaryRetainedJcoCalls': 18,
                       'ordinaryFreshSuccessfulWasmtime': 6, 'ordinaryRejectedInitializers': 16,
                       'ordinaryDeployedFatalJco': 10, 'ordinaryDeployedFatalWasmtime': 10,
                       'gcRetainedJco': 3, 'gcFreshSuccessfulWasmtime': 1, 'gcPublicHexRoundtripsPerCleanCall': 8,
                       'gcLatchedInitializerFailures': 1, 'gcDeployedFatalEachHost': 1,
                       'offRawImportRefusals': 2, 'offBundleAdmissionRefusals': 2, 'offBenignSuccessEachHost': 1}
    for name, expected in expected_counts.items():
        assert focused['counts'][name] == expected, name
    oracle = json_file(FOCUSED / 'source-freeze/node-results.json')
    for name, label in [('native-off-results.json', 'off-foundations'), ('native-runtime-results.json', 'runtime-foundations')]:
        report = json_file(FOCUSED / name)
        assert report['state'] == 'M10_ORDINARY_NATIVE_ADD_ABORT_LISTENER_PASSED'
        assert report['engineSha256'] == ENGINES[label] and report['publicNodeGroups']['total'] == 29
        assert report['preflight']['sourceFilesVerified'] == 304 and report['preflight']['actualLayoutCompileCommands'] == 60
        assert report['preflight']['guardNegativesAllowed'] and len(report['initializers']) == 8 and len(report['fatal']) == 5
        for group in ['main', 'aliases', 'benign']:
            assert len(report[group]['calls']) == 3
            assert [call['calls'] for call in report[group]['calls']] == [1, 2, 3]
        for observed in report['main']['calls'] + [report['main']['freshWasmtime']['observed']]:
            for field in ['publicCases', 'nestedOnceCases', 'receiverCases']:
                assert observed[field] == oracle[field], field
            assert len(observed['namespace']['names']) == 16 and observed['namespace']['defaultNamed']
            assert len(observed['profileErrors']['errors']) == 7 and observed['profileErrors']['hooks'] == 0
            assert observed['snapshot']['signalThis'] and observed['snapshot']['currentTarget']
        for failure in report['fatal']:
            fatal_assertions(failure)
    gc = json_file(FOCUSED / 'native-gc-results.json')
    assert gc['state'] == 'M10_RELEASE_MOVING_GC_COMBINED_OWNER_GATE_PASSED' and gc['engineSha256'] == ENGINES['gc-foundations']
    assert '-DNODE_COMPAT_GC_STRESS=1' in gc['actualKernelCommand']
    assert len(gc['clean']['calls']) == 3 and gc['initializer']['message']
    for call in gc['clean']['calls'] + [gc['clean']['freshWasmtime']['observed']]:
        assert call['completed'] == 8 and call['receiver'] and call['contextRestored'] and call['disposalCalls'] == 0
    fatal_assertions(gc['fatal'])
    events_off = json_file(FOCUSED / 'events-off-results.json')
    assert events_off['state'] == 'M10_ACTUAL_EVENTS_OFF_ADMISSION_PASSED'
    assert events_off['engineSha256'] == ENGINES['events-off-control'] and events_off['actualLayoutMacro'] == 'ABSENT'
    assert len(events_off['failures']) == 2 and events_off['positive']['jco'] == 'EVENTS_OFF_OK'
    assert events_off['positive']['wasmtime']['status'] == 0
    for failure in events_off['failures']:
        assert 'not admitted' in failure['bundler'] and 'Error loading module' in failure['nativeComponentization']
    # This is a required FALSE parity observation, never a pass criterion.
    gap = json_file(FOCUSED / 'callback-return-results.json')
    assert gap['state'] == 'CONFIRMED_FRESH_CALLBACK_RETURN_THEN_GETTER_COUNTEREXAMPLE'
    assert gap['observationCompleted'] is True and gap['nodeCompatibilityPassed'] is False
    assert gap['node']['observed'] == {'ordinary': 1, 'protectedSignal': 1, 'alreadyAborted': 0}
    assert gap['jco']['observed'] == gap['wasmtime']['observed'] == {'ordinary': 0, 'protectedSignal': 0, 'alreadyAborted': 0}
    symbol = focused['nodeCompatibilityLimits']['targetSymbolDisposeIdentity']
    assert symbol['node']['registryKey'] == 'nodejs.dispose' and symbol['target']['registryKey'] is None
    assert symbol['node']['sameAsNodeRegistry'] is True and symbol['target']['sameAsNodeRegistry'] is False

    http = reports['http-audit.json']
    assert http['engineSha256'] == ENGINES['runtime-foundations'] and http['protectedAbortFoundationsFixture']
    assert http['componentSha256'] == sha(Path(http['componentPath'])) == HTTP_SHA and http['componentBytes'] == HTTP_BYTES
    assert sorted(http['emittedImports']) == IMPORTS and http['emittedExports'] == ['wasi:http/incoming-handler@0.2.10']
    assert http['clockDependency']['typeOnly'] and http['clockDependency']['callableImports'] == [] and http['clockDependency']['coreClockImports'] == []
    for name in ['wasmtime-http.json', 'wasmcloud-http.json']:
        report = reports[name]
        digest = report['component']['sha256'] if name == 'wasmcloud-http.json' else report['componentSha256']
        assert digest == HTTP_SHA and len(report['responses']) == 3 and report['process']['stopped']
        assert report['process']['exitStatus'] == {'code': 0, 'signal': None}
        assert [response['body']['componentInstanceRequestCount'] for response in report['responses']] == [1, 1, 1]
        for response in report['responses']:
            assert response['status'] == 200
            body = response['body']['native']['foundations']
            assert body['schema'] == 5 and len(body['aliases']['aliases']) == 14
            for field in ['publicCases', 'nestedOnceCases', 'receiverCases']:
                assert body['protectedAbort'][field] == oracle[field]
            assert body['streamWeb']['passed'] and body['streamWeb']['iterations'] == 67 and body['streamWeb']['data'] == 26
    assert reports['wasmcloud-http.json']['host']['unmodifiedOfficialBinary']
    assert reports['wasmcloud-http.json']['host']['version'] == '2.11.0'
    assert reports['http-summary.json']['state'] == 'HTTP_V10_BOTH_UNMODIFIED_HOSTS_PASSED'
    assert reports['http-summary.json']['knownHarnessFailure']['componentFailureClaim'] is False
    assert reports['http-summary.json']['instanceReuseClaim'] is False
    assert sha(Path(reports['http-index.json']['summary']['path'])) == reports['http-index.json']['summary']['sha256']
    for item in reports['http-index.json']['files']:
        assert sha(Path(item['path'])) == item['sha256'], item['path']
    return files, reports, engines, focused, gap


def prepare_plan(files, engines):
    plan, omitted = {}, []
    def add(source, destination, required_sha=None, native_asset=None):
        source, destination = Path(source), PurePosixPath(destination)
        assert not destination.is_absolute() and '..' not in destination.parts
        assert_regular(source)
        if binary(source):
            if native_asset not in SOURCE_BINARY_ASSETS:
                omitted.append({'path': str(source), 'reason': 'generated-engine-component-or-other-binary'}); return
            assert sha(source) == SOURCE_BINARY_ASSETS[native_asset]
            assert str(destination) == 'source/' + native_asset
        digest = sha(source)
        if required_sha is not None: assert digest == required_sha, source
        key = str(destination)
        if key in plan:
            assert plan[key]['sha256'] == digest, ('archive path collision', key)
            return
        plan[key] = {'source': str(source), 'destination': key, 'sha256': digest, 'bytes': source.stat().st_size}
    def tree(root, destination):
        root = Path(root)
        for path in entries_without_links(root, omitted):
            add(path, str(PurePosixPath(destination) / path.relative_to(root).as_posix()))
    # Exactly required inputs plus seven Node attribution files, not arbitrary
    # cached sources; the five native binary assets are individually pinned.
    off = engines['off-foundations']
    for item in off['sourceManifest']:
        add(FREEZE / 'source' / item['path'], 'source/' + item['path'], item['sha256'], item['path'])
    for item in json_file(FREEZE / 'licenses.json')['files']:
        add(FREEZE / 'source' / item['path'], 'source/' + item['path'], item['sha256'])
    tree(FREEZE / 'componentize-source', 'componentize-source')
    for path in sorted(FREEZE.iterdir()):
        if path.is_file() and not path.is_symlink(): add(path, path.name)
    for name, path in files.items(): add(path, 'reports/' + name)
    # Raw before-build complete OpenSSL source inventory and original dependency
    # receipts are text provenance; native libraries/archive binaries stay external.
    for label, engine in engines.items():
        audit = engine['openssl']['completeSourceAudit']
        assert audit['beforeAndAfterBuild'] and audit['sourceFilesVerified'] == 4650
        add(Path(audit['beforeReportPath']), 'dependency-provenance/' + label + '-openssl-before.json', audit['beforeReportSha256'])
        add(Path(engine['openssl']['receiptPath']), 'dependency-provenance/' + label + '-openssl-receipt.json', engine['openssl']['receiptSha256'])
    for path in sorted((BASE / 'release-gates-v1').glob('*.log')): add(path, 'raw/release/' + path.name)
    for job in json_file(files['release-index.json'])['jobs']:
        if job['name'] == 'optional': continue
        tree(Path(job['output']), 'generated-text/' + job['name'])
    optional = json_file(files['optional-index.json'])
    for module in optional['modules']:
        tree(Path(module['output']), 'generated-text/optional/' + module['name'])
    # Copy previous reports/source snapshots as history, never as current passes.
    tree(BASE / 'release-gates-v1/optional/prior-latest', 'historical-prior-latest')
    tree(BASE / 'pre-adoption-oracles', 'pre-adoption-oracles')
    for name in ['add-abort-off', 'add-abort-runtime', 'add-abort-gc', 'events-off-admission', 'callback-return-observation']:
        tree(BASE / name, 'focused-generated-text/' + name)
    tree(BASE / 'http-joint', 'http-generated-text')
    for path in sorted(BASE.glob('http*.json')): add(path, 'raw/http/' + path.name)
    for path in sorted(BASE.glob('http*.log')): add(path, 'raw/http/' + path.name)
    wash = json_file(files['wasmcloud-http.json'])
    add(Path(wash['process']['logPath']), 'raw/http/official-wash.log')
    # Current tested source families and shared helper closure. Historical files
    # retain their labels; no claim that every copied source was executed.
    for module in ['path', 'events', 'string-decoder', 'assert', 'querystring', 'util', 'stream-web', 'add-abort']:
        tree(TESTS / ('foundation-' + module), 'harness/foundation-' + module)
    tree(TESTS / 'foundation-alloc-unsafe/installed', 'harness/foundation-alloc-unsafe/installed')
    for name in ['checks.mjs', 'node-results.json', 'demand-source.mjs']:
        add(TESTS / 'foundation-alloc-unsafe' / name, 'harness/foundation-alloc-unsafe/' + name)
    prior = TESTS / 'milestones/foundations-v9/harness'
    for old in entries_without_links(prior, omitted):
        relative = old.relative_to(prior)
        current = TESTS / relative
        if current.is_file() and not current.is_symlink(): add(current, 'harness/' + relative.as_posix())
        else: add(old, 'historical-v9-only-harness/' + relative.as_posix())
    for name in ['foundations', 'wasmcloud', 'entropy', 'provenance']:
        tree(TESTS / name, 'harness/' + name)
    tree(TESTS / 'legacy-stream-web-test-sources', 'harness/legacy-stream-web-test-sources')
    for path in sorted(TESTS.iterdir()):
        if path.is_file() and not path.is_symlink(): add(path, 'harness/' + path.name)
    known_resolved_sources = {Path(value['source']).resolve() for value in plan.values()}
    for item in json_file(files['http-index.json'])['files']:
        source = Path(item['path'])
        resolved_source = source.resolve()
        if binary(source) or resolved_source in known_resolved_sources:
            continue
        if source.is_relative_to(REPO):
            add(source, 'indexed-http-repository/' + source.relative_to(REPO).as_posix(), item['sha256'])
        elif source.is_relative_to(BASE):
            add(source, 'indexed-http-external/' + source.relative_to(BASE).as_posix(), item['sha256'])
        else:
            add(source, 'indexed-http-other/' + sha(source) + '-' + source.name, item['sha256'])
        known_resolved_sources.add(resolved_source)
    # Preserve actual HTTP input source hashes, including the unchanged handler;
    # failed first attempt was an invocation-option mistake, not a source patch.
    for item in json_file(BASE / 'http-v10-inputs.json')['sourceFiles']:
        add(REPO / item['path'], 'harness/' + str(PurePosixPath(item['path']).relative_to('tests/node-compat')), item['sha256'])
    add(REPO / 'LICENSE', 'LICENSE')
    add(HERE / 'README.md', 'acceptance-preparation/README.md')
    add(HERE / 'accept-v10.py', 'accept-v10.py')
    # No private m0.11 path may enter through a generic shared closure.
    assert all('m0.11' not in item['source'] and '/m011' not in item['source'] for item in plan.values())
    assert len([item for item in plan.values() if item['destination'].startswith('source/') and item['destination'][7:] in {entry['path'] for entry in off['sourceManifest']}]) == 304
    return plan, omitted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='After root review, copy/verify/atomically create a new milestone')
    args = parser.parse_args()
    files, reports, engines, focused, gap = validate()
    plan, omitted = prepare_plan(files, engines)
    summary = {'state': 'verified-plan-only-no-stage-created', 'files': len(plan), 'bytes': sum(item['bytes'] for item in plan.values()),
               'reports': len(files), 'nativeInputs': 304, 'nativeBinarySourceAssets': len(SOURCE_BINARY_ASSETS),
               'applicationOrEngineBinariesCopied': 0, 'destination': str(DESTINATION),
               'nodeCallbackReturnParity': False, 'nodeSymbolDisposeRegistryParity': False,
               'httpComponentSha256': HTTP_SHA, 'httpComponentBytes': HTTP_BYTES}
    if not args.apply:
        print(json.dumps(summary, indent=2)); return
    # All verification precedes first archive write. Preserve a failed stage;
    # never delete it, overwrite a checkpoint, or modify original artifacts.
    assert not DESTINATION.exists() and not STAGE.exists()
    STAGE.mkdir(parents=True)
    records = []
    for key, item in sorted(plan.items()):
        source, target = Path(item['source']), STAGE / key
        assert_regular(source)
        assert sha(source) == item['sha256'], ('source changed before copy', source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target, follow_symlinks=False)
        assert_regular(target)
        assert sha(target) == item['sha256'] and target.stat().st_size == item['bytes']
        records.append({'path': key, 'sha256': item['sha256'], 'bytes': item['bytes'], 'original': item['source']})
    # Recheck native/control source hashes after copying, before publication.
    for item in engines['off-foundations']['sourceManifest']:
        assert sha(STAGE / 'source' / item['path']) == sha(REPO / item['path']) == item['sha256']
    result = {'schema': 1, 'state': 'accepted-bounded-foundations-v10-with-confirmed-node-deviations',
              'acceptedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'starlingMonkeyBaseRevision': engines['off-foundations']['auditedBaseRevision'], 'nodeVersion': 'v22.14.0',
              'coreVersion': 'sm-node-22.14.0-m0.8', 'eventsVersion': 'sm-node-22.14.0-m0.10',
              'strictCallbackPolicy': 'sm-uncaught-event-v3-protected-abort-v2',
              'identicalNativeInputs': 304, 'recipeSha256': RECIPE,
              'engines': {label: {'sha256': engine['engineSha256'], 'bytes': engine['engineBytes']} for label, engine in engines.items()},
              'boundedFunctionalGatesPassed': True, 'completeNodeCompatibility': False,
              'callbackReturnObservationCompleted': True, 'nodeCallbackReturnParity': False,
              'callbackReturnCounterexample': {'node': gap['node']['observed'], 'jco': gap['jco']['observed'],
                                               'wasmtime': gap['wasmtime']['observed'], 'nodeCompatibilityPassed': False},
              'nodeSymbolDisposeRegistryParity': False, 'symbolDisposeIdentity': focused['nodeCompatibilityLimits']['targetSymbolDisposeIdentity'],
              'focusedCounts': focused['counts'], 'fullReports': len(files),
              'componentSha256': HTTP_SHA, 'componentBytes': HTTP_BYTES, 'emittedImports': IMPORTS,
              'emittedExports': ['wasi:http/incoming-handler@0.2.10'], 'httpRequestsPerHost': 3,
              'requestCounters': [[1, 1, 1], [1, 1, 1]], 'sameInstanceHTTPReuseEstablished': False,
              'generatedEngineOrApplicationBinariesCopied': False, 'requiredSourceBinaryAssets': SOURCE_BINARY_ASSETS,
              'copiedEvidence': records, 'omittedPaths': omitted,
              'limitations': [
                  'Confirmed FALSE Node parity: fresh ordinary/protected callback return .then getter effects are absent (Node1/1/0, native0/0/0). Throwing/rejecting thenables and async listener parity are not established.',
                  'Target Symbol.dispose is its well-known nonregistry Symbol, unlike Node Symbol.for(nodejs.dispose). No identity rewriting is claimed.',
                  'm0.10 is bounded partial compatibility; no complete Node, Buffer, EventTarget, Web/classic Stream, process, ALS or nextTick support.',
                  'Raw native alias namespaces share values/defaults but are per-specifier namespace objects.',
                  'GC evidence combines owners/callbacks/closure-held Symbol; it does not isolate prototype-only Symbol liveness or prove OOM/fault behavior.',
                  'Fatal entries require discarded instances. Successful retained scalar calls do not prove reuse after fatal execution.',
                  'HTTP counters restart1 on both hosts; instance reuse, concurrent entry, general request isolation and teardown remain unproved.',
                  'Exact six standard0.2.10 interfaces only; monotonic clock is type-only, secure entropy explicitly selected. No outgoing HTTP, DNS, sockets, TLS, filesystem or CLI capability is inferred.',
                  'Copied older templates/failures/history retain their own labels; not every archived source was executed. Initial CMake/Wasmtime harness failures are historical, not successful gates.',
                  'No private m0.11 artifact/source or performance promotion is included. Corpus-heavy HTTP size is not minimal deployment size or acceleration evidence.',
              ]}
    (STAGE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    (STAGE / 'README.md').write_text('# Bounded foundations v10 checkpoint\n\n'
        'This checkpoint preserves completed bounded gates with a confirmed Node callback-return counterexample and a Symbol.dispose registry difference. '
        'Node parity for those observations is **false**. See results.json and reports/focused-callback-return-results.json.\n\n'
        'Four Release engines share304 source inputs; generated engines/application components remain external. '
        'Five exact already-versioned host-API binary source assets are included to preserve the complete native source set. '
        'See acceptance-preparation/README.md for the reviewed acceptance plan and limitations.\n')
    # Generated summaries are separate from copiedEvidence's original-file list.
    for name in ['results.json', 'README.md']:
        assert_regular(STAGE / name)
    STAGE.rename(DESTINATION)
    print(json.dumps({**summary, 'state': result['state'], 'milestone': str(DESTINATION)}, indent=2))


if __name__ == '__main__':
    main()
