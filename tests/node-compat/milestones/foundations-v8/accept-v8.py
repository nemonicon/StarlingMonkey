"""Archive executed bounded v8 gates; never overwrite earlier checkpoints."""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import shutil

repo = Path(__file__).resolve().parents[3]
base = Path('/tmp/starling-node-compat/foundations-v8')
freeze = base / 'native-freeze'
destination = repo / 'tests/node-compat/milestones/foundations-v8'
stage = destination.with_name('.foundations-v8-staging')
assert not destination.exists() and not stage.exists(), 'Preserve existing evidence/staging'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
files = {
    'engine-off.json': freeze / 'off-foundations.engine.wasm.build.json',
    'engine-runtime.json': freeze / 'runtime-foundations.engine.wasm.build.json',
    'engine-gc.json': freeze / 'gc-foundations.engine.wasm.build.json',
    'buffer.json': base / 'core-native-v2/results.json',
    'allocator.json': base / 'installed-allocator/results.json',
    'allocator-gc.json': base / 'allocator-gc/results.json',
    'selection.json': base / 'selection.json',
    'cmake-policy.json': repo / 'tests/node-compat/foundations/cmake-policy-results.json',
    'optional-index.json': repo / 'tests/node-compat/foundations/v8-optional-results.json',
    'http-audit.json': base / 'http-joint/component-audit.json',
    'wasmtime-http.json': base / 'http-joint/wasmtime-results.json',
    'wasmcloud-http.json': base / 'wasmcloud-http-results.json',
}
optional = json.loads(files['optional-index.json'].read_text())
assert optional['state'] == 'passed' and len(optional['modules']) == 6
for module in optional['modules']:
    assert sha(Path(module['reportPath'])) == module['reportSha256']
    files[module['name'] + '.json'] = Path(module['reportPath'])
for name in ['sync', 'runtime', 'late', 'callback']:
    files['strict-' + name + '.json'] = repo / ('tests/node-compat/foundation-add-abort/production-v8-' + name + '-results.json')
reports = {name: json.loads(path.read_text()) for name, path in files.items()}
off, runtime, gc = [reports['engine-' + name + '.json'] for name in ['off', 'runtime', 'gc']]
assert off['sourceManifest'] == runtime['sourceManifest'] == gc['sourceManifest']
assert len(off['sourceManifest']) == 293
assert off['buildRecipeSha256'] == runtime['buildRecipeSha256'] == gc['buildRecipeSha256']
assert not off['gcStress'] and not runtime['gcStress'] and gc['gcStress']
assert not any(engine['oomTesting'] for engine in [off, runtime, gc])
for engine in [off, runtime, gc]:
    assert engine['strictEventExceptionPolicy']['version'] == 'sm-uncaught-event-v3'
    core = next(item for item in engine['selectedModuleManifests'] if item['path'].endswith('/export-manifest.node-v22.14.0.json'))
    assert core['profileVersion'] == 'sm-node-22.14.0-m0.8'
for name in ['buffer', 'allocator', 'path', 'events', 'string-decoder', 'assert', 'querystring', 'util']:
    assert reports[name + '.json']['engineSha256'] == off['engineSha256'], name
for name in ['sync', 'runtime', 'late', 'callback']:
    report = reports['strict-' + name + '.json']
    assert report['engineSha256'] == off['engineSha256'] and report['state'].endswith('passed')
assert reports['allocator.json']['installedBuiltin']
assert reports['allocator.json']['refusalChecksPerCall'] == 240
assert reports['allocator-gc.json']['engineSha256'] == gc['engineSha256']
assert len(reports['allocator-gc.json']['calls']) == 3
assert reports['allocator-gc.json']['interfaceAudit']['emittedImports'] == []
assert reports['selection.json']['tests'] == reports['selection.json']['passed'] == 213
assert reports['selection.json']['failures'] == []
assert len(reports['cmake-policy.json']['cases']) == 17
http = reports['http-audit.json']
assert http['engineSha256'] == runtime['engineSha256'] and http['utilFoundationsFixture']
assert http['coreExpectations']['coreVersion'] == 'sm-node-22.14.0-m0.8'
assert len(http['emittedImports']) == 6 and http['clockDependency']['typeOnly']
assert http['clockDependency']['callableImports'] == []
for name in ['wasmtime-http.json', 'wasmcloud-http.json']:
    report = reports[name]
    component_hash = report['component']['sha256'] if name == 'wasmcloud-http.json' else report['componentSha256']
    assert component_hash == http['componentSha256']
    assert len(report['responses']) == 3
    assert report['process']['stopped'] and report['process']['exitStatus']['code'] == 0
    for response in report['responses']:
        body = response['body']
        assert body['native']['coreVersion'] == 'sm-node-22.14.0-m0.8'
        assert body['native']['unavailableMethods'] == 91
        assert len(body['native']['foundations']['aliases']['aliases']) == 13
        assert body['native']['foundations']['util']['cases']['checks'] == 2436
stage.mkdir()
shutil.copytree(freeze / 'source', stage / 'source')
for item in off['sourceManifest']:
    assert sha(stage / 'source' / item['path']) == item['sha256']
for name, path in files.items():
    shutil.copy2(path, stage / name)
for name in ['build-engine.sh', 'openssl-source-audit.py', 'off-CMakeCache.txt',
             'off-compile_commands.json', 'runtime-CMakeCache.txt', 'runtime-compile_commands.json',
             'gc-CMakeCache.txt', 'gc-compile_commands.json', 'off-freeze-receipt.json',
             'gc-freeze-receipt.json', 'engines-index.json']:
    shutil.copy2(freeze / name, stage / name)
shutil.copytree(freeze / 'componentize-source', stage / 'componentize-source')
# Preserve the earlier harness list and the changed/new v8 entry points.
tree = ast.parse((Path(__file__).with_name('accept-v7.py')).read_text())
paths = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
             and any(isinstance(target, ast.Name) and target.id == 'harness_paths' for target in node.targets))
paths += ['run.mjs', 'core-expectations.mjs', 'toolchain.mjs', 'componentizer.mjs',
          'capability-policy.mjs', 'oracle.mjs', 'fixtures/component.mjs', 'fixtures/static-require.cjs',
          'optimization/intrinsics-checks.mjs', 'foundations/http-v8.mjs',
          'foundations/run-v8-optional-regressions.mjs']
for name in sorted(set(paths)):
    target = stage / 'harness' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo / 'tests/node-compat' / name, target)
for source, target in [
    (repo / 'tests/node-compat/foundation-add-abort/production-v8-source-freeze', stage / 'strict-evidence'),
    (repo / 'tests/node-compat/foundation-alloc-unsafe/installed', stage / 'allocator-evidence')]:
    shutil.copytree(source, target)
for name in ['LICENSE', 'builtins/node-compat/LICENSE.assert', 'builtins/node-compat/LICENSE.querystring',
             'builtins/node-compat/LICENSE.events', 'builtins/node-compat/LICENSE.string-decoder',
             'builtins/node-compat/LICENSE.util', 'builtins/node-compat/path-vendor/LICENSES.txt']:
    target = stage / 'licenses' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo / name, target)
shutil.copy2(Path(__file__), stage / 'accept-v8.py')
records = [dict(path=str(path.relative_to(stage)), sha256=sha(path), bytes=path.stat().st_size)
           for path in sorted(stage.rglob('*')) if path.is_file()]
result = dict(schema=1, state='accepted-bounded-foundations-v8',
    acceptedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    starlingMonkeyBaseRevision=off['auditedBaseRevision'], nodeVersion='v22.14.0',
    coreVersion='sm-node-22.14.0-m0.8', strictCallbackPolicy='sm-uncaught-event-v3',
    engines={name: dict(sha256=engine['engineSha256'], bytes=engine['engineBytes'])
             for name, engine in [('off', off), ('runtimeOnly', runtime), ('gcTest', gc)]},
    identicalCompiledSources=293, completeNativeSourceArchive='source',
    componentSha256=http['componentSha256'], componentBytes=http['componentBytes'],
    emittedImports=http['emittedImports'], emittedExports=http['emittedExports'],
    httpRequestsPerHost=3, clockTypeOnly=True,
    requestCounters=[[response['body']['componentInstanceRequestCount'] for response in reports[name]['responses']]
                     for name in ['wasmtime-http.json', 'wasmcloud-http.json']],
    sameInstanceHTTPReuseEstablished=False, copiedEvidence=records,
    limitations=[
        'Bounded modules/overloads only; no complete Node or Buffer compatibility.',
        'Registration getter timing, listener receiver parity, explicit reset and complete teardown remain separate.',
        'New allocator is zeroed/fresh/no-pool; limits/coercions differ from Node.',
        'Ordinary Release moving-GC gate is not allocation-failure or exhaustive GC evidence.',
        'Earlier kernel allocator scopes remain separate; stopped newer private diagnostic stays unverified.',
        'No installed stream/web, classic streams, production ALS, compression, Node crypto or optional Node I/O variants.',
        'Corpus-heavy HTTP size is not minimal deployment size; two local hosts do not prove production reuse/isolation.',
        'New matched allocator timing/memory execution is not part of this checkpoint.',
    ])
(stage / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
stage.rename(destination)
print(json.dumps({'milestone': str(destination), 'copiedFiles': len(records),
    'fullReports': len(files), 'componentSha256': http['componentSha256']}, indent=2))
