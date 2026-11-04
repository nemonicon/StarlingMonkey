"""Archive completed v7 evidence; this does not execute or replace its tests."""
import datetime
import hashlib
import json
import pathlib
import shutil

repo = pathlib.Path(__file__).resolve().parents[3]
base = pathlib.Path('/tmp/starling-node-compat/foundations-v7')
freeze = base / 'native-freeze'
destination = repo / 'tests/node-compat/milestones/foundations-v7'
stage = destination.with_name('.foundations-v7-staging')
assert not destination.exists(), 'Accepted checkpoints cannot be overwritten'
if stage.exists():
    # A preceding archive assertion failed before writing any evidence. Only
    # an empty directory is removable; populated staging always requires review.
    stage.rmdir()
stage.mkdir()
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
files = {
    'engine-off.json': freeze / 'off-foundations.engine.wasm.build.json',
    'engine-runtime.json': freeze / 'runtime-foundations.engine.wasm.build.json',
    'buffer.json': base / 'buffer/results.json',
    'path.json': base / 'path/results.json',
    'events.json': base / 'events/results.json',
    'string-decoder.json': repo / 'tests/node-compat/foundation-string-decoder/native-component-results.json',
    'assert.json': repo / 'tests/node-compat/foundation-assert/native-component-results.json',
    'querystring.json': repo / 'tests/node-compat/foundation-querystring/native-component-results.json',
    'selection.json': repo / 'tests/node-compat/foundations/selection-results-v7.stdout.json',
    'cmake-policy.json': repo / 'tests/node-compat/foundations/cmake-policy-results.json',
    'string-decoder-host.json': repo / 'tests/node-compat/foundation-string-decoder/production-contract-results.json',
    'assert-host.json': repo / 'tests/node-compat/foundation-assert/native-node-results.json',
    'querystring-host.json': repo / 'tests/node-compat/foundation-querystring/native-node-results.json',
    'util.json': repo / 'tests/node-compat/foundation-util/native-component-results.json',
    'util-host.json': repo / 'tests/node-compat/foundation-util/native-node-results.json',
    'util-source.json': repo / 'tests/node-compat/foundation-util/production-source-results.json',
    'util-peer-review.json': repo / 'tests/node-compat/foundation-util/production-peer-review.json',
    'util-evidence.json': repo / 'tests/node-compat/foundation-util/native-evidence-receipt.json',
    'http-audit.json': base / 'http-joint/component-audit.json',
    'wasmtime-http.json': base / 'http-joint/wasmtime-results.json',
    'wasmcloud-http.json': base / 'wasmcloud-http-results.json',
}
reports = {name: json.loads(path.read_text()) for name, path in files.items()}
off, runtime = reports['engine-off.json'], reports['engine-runtime.json']
assert off['sourceManifest'] == runtime['sourceManifest']
assert len(off['sourceManifest']) == 293
for name in ['buffer.json', 'path.json', 'events.json', 'string-decoder.json', 'assert.json', 'querystring.json', 'util.json']:
    assert reports[name]['engineSha256'] == off['engineSha256'], name
for name in ['assert.json', 'querystring.json']:
    assert reports[name]['installedBuiltin'] is True
assert reports['util.json']['state'] == 'actual-installed-util-native-component-passed'
assert reports['string-decoder.json']['bundle']['imports'] == ['node:buffer', 'node:string_decoder']
assert reports['selection.json']['tests'] == reports['selection.json']['passed'] == 213
assert reports['selection.json']['failures'] == []
assert len(reports['cmake-policy.json']['cases']) == 17
http = reports['http-audit.json']
assert http['engineSha256'] == runtime['engineSha256'] and http['utilFoundationsFixture']
assert len(http['emittedImports']) == 6 and http['clockDependency']['typeOnly']
for name in ['wasmtime-http.json', 'wasmcloud-http.json']:
    report = reports[name]
    assert len(report['responses']) == 3
    assert report['process']['stopped'] and report['process']['exitStatus']['code'] == 0
    for response in report['responses']:
        foundations = response['body']['native']['foundations']
        assert foundations['schema'] == 3 and len(foundations['aliases']['aliases']) == 13
        assert foundations['stringDecoder']['sequences'] == 2982
        assert foundations['assert']['snapshotIdentity'] and foundations['querystring']['snapshotIdentity']
        assert foundations['util']['cases']['checks'] == 2436 and len(foundations['util']['deferred']) == 108
shutil.copytree(freeze / 'source', stage / 'source')
for entry in off['sourceManifest']:
    assert digest(stage / 'source' / entry['path']) == entry['sha256'], entry['path']
for name, path in files.items():
    shutil.copy2(path, stage / name)
for name in ['build-engine.sh', 'openssl-source-audit.py']:
    shutil.copy2(freeze / name, stage / name)
harness_paths = [
    'module-selection.mjs', 'module-selection-test.mjs', 'profile-bundler.mjs',
    'foundations/http-v7.mjs', 'foundations/assert-http-report.mjs',
    'foundations/native-scalar-harness.mjs', 'foundations/cmake-policy-test.py',
    'wasmcloud/build-http.mjs', 'wasmcloud/test-wasmtime-http.mjs', 'wasmcloud/run-host.mjs',
    'foundation-string-decoder/native-component.mjs', 'foundation-string-decoder/native-aliases.mjs',
    'foundation-string-decoder/native-require.cjs', 'foundation-string-decoder/decoder-cases.mjs',
    'foundation-string-decoder/component-corpus.json', 'foundation-string-decoder/run-native-component.mjs',
    'foundation-string-decoder/production-contract-tests.mjs',
    'foundation-assert/native-component.mjs', 'foundation-assert/native-require.cjs',
    'foundation-assert/checks.mjs', 'foundation-assert/run-native-component.mjs', 'foundation-assert/run-native-node.mjs',
    'foundation-querystring/native-component.mjs', 'foundation-querystring/native-require.cjs',
    'foundation-querystring/checks.mjs', 'foundation-querystring/run-native-component.mjs',
    'foundation-querystring/run-native-node.mjs',
    'foundation-util/native-component.mjs', 'foundation-util/native-dynamic.mjs',
    'foundation-util/native-require.cjs', 'foundation-util/component-cases.mjs',
    'foundation-util/prototype-scope.mjs', 'foundation-util/run-native-component.mjs',
    'foundation-util/run-native-node.mjs', 'foundation-util/production-test.mjs',
]
for name in harness_paths:
    source, target = repo / 'tests/node-compat' / name, stage / 'harness' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
# Accompany the archived sources with noncompiled project/vendor licenses.
license_paths = ['LICENSE', 'builtins/node-compat/LICENSE.assert', 'builtins/node-compat/LICENSE.querystring',
                 'builtins/node-compat/LICENSE.events', 'builtins/node-compat/LICENSE.string-decoder',
                 'builtins/node-compat/LICENSE.util', 'builtins/node-compat/path-vendor/LICENSES.txt']
for name in license_paths:
    target = stage / 'licenses' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo / name, target)
shutil.copy2(pathlib.Path(__file__), stage / 'accept-v7.py')
records = [dict(path=str(path.relative_to(stage)), sha256=digest(path), bytes=path.stat().st_size)
           for path in sorted(stage.rglob('*')) if path.is_file()]
result = dict(
    schema=1, acceptedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    state='accepted-bounded-foundations-v7', starlingMonkeyBaseRevision=off['auditedBaseRevision'], nodeVersion='v22.14.0',
    engineOFF=dict(sha256=off['engineSha256'], bytes=off['engineBytes']),
    engineRuntime=dict(sha256=runtime['engineSha256'], bytes=runtime['engineBytes']),
    identicalCompiledSources=293, actualRegistrationFlagsVerified=True, completeNativeSourceArchive='source',
    componentSha256=http['componentSha256'], componentBytes=http['componentBytes'],
    emittedImports=http['emittedImports'], emittedExports=http['emittedExports'], clockTypeOnly=True,
    httpRequestsPerHost=3,
    requestCounters=[[item['body']['componentInstanceRequestCount'] for item in reports[name]['responses']]
                     for name in ['wasmtime-http.json', 'wasmcloud-http.json']],
    sameInstanceHTTPReuseEstablished=False, copiedEvidence=records,
    limitations=[
        'Bounded partial modules only; complete Node/Buffer/StringDecoder/Assert/Querystring/Util compatibility is not claimed.',
        'The corpus-heavy HTTP component is a correctness artifact, not a minimal-size/performance result.',
        'Shared-input/cross-realm/fatal-decoder lifecycle and Rust allocator-abort limitations remain as the manifests specify.',
        'No new GC stress or allocation-failure gate; prior accepted Buffer allocator scopes remain separate and stopped newer private OOM gate stays unverified.',
        'No production ALS/classic streams/stream-web/compression/crypto or optional process/filesystem/socket/NodeHTTP variants added.',
        'Two stock local hosts, not production-cluster portability or request isolation proof.',
        'Weval performance experiment retains its separate frozen-v5 source and gates.',
    ])
(stage / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
stage.rename(destination)
print(json.dumps(dict(milestone=str(destination), copiedFiles=len(records), fullReports=len(files),
                      componentSha256=http['componentSha256'], componentBytes=http['componentBytes']), indent=2))
