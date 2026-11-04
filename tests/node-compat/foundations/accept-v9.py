"""Freeze passed bounded m0.9 gates. Preserve all earlier checkpoints."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil

repo = Path(__file__).resolve().parents[3]
base = Path('/tmp/starling-node-compat/foundations-v9')
freeze = base / 'native-freeze'
destination = repo / 'tests/node-compat/milestones/foundations-v9'
stage = destination.with_name('.foundations-v9-staging')
assert not destination.exists() and not stage.exists(), 'Never overwrite a freeze or failed staging'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
files = {
    'engine-control.json': freeze / 'control-stream-off.engine.wasm.build.json',
    'engine-off.json': freeze / 'off-foundations.engine.wasm.build.json',
    'engine-runtime.json': freeze / 'runtime-foundations.engine.wasm.build.json',
    'buffer.json': base / 'release-gates-v1/core/results.json',
    'allocator.json': base / 'release-gates-v1/allocator/results.json',
    'selection.json': base / 'selection.json',
    'cmake-policy.json': base / 'cmake-policy-results.json',
    'release-index.json': base / 'release-gates-v1/results.json',
    'optional-index.json': base / 'release-gates-v1/optional/results.json',
    'stream-web.json': base / 'stream-web-native/results.json',
    'stream-native-guard.json': repo / 'tests/node-compat/foundation-stream-web/production-candidate/native-controller-off-results.json',
    'stream-off-admission.json': base / 'off-module-admission/results.json',
    'http-audit.json': base / 'http-joint/component-audit.json',
    'wasmtime-http.json': base / 'http-joint/wasmtime-results.json',
    'wasmcloud-http.json': base / 'wasmcloud-http-results.json',
}
release = json.loads(files['release-index.json'].read_text())
assert release['state'] == 'passed' and len(release['jobs']) == 7
for job in release['jobs']:
    assert job['code'] == 0 and sha(Path(job['reportPath'])) == job['reportSha256']
optional = json.loads(files['optional-index.json'].read_text())
assert optional['state'] == 'passed' and len(optional['modules']) == 6
assert sum(entry['finalComponentAudits'] for entry in optional['modules']) == 10
for module in optional['modules']:
    assert sha(Path(module['reportPath'])) == module['reportSha256']
    files[module['name'] + '.json'] = Path(module['reportPath'])
for name in ['sync', 'runtime', 'late', 'callback']:
    folder = 'callbacks' if name == 'callback' else name
    files['strict-' + name + '.json'] = base / ('release-gates-v1/strict-' + folder + '/production-v9-' + name + '-results.json')
reports = {name: json.loads(path.read_text()) for name, path in files.items()}
control, off, runtime = [reports['engine-' + name + '.json'] for name in ['control', 'off', 'runtime']]
assert control['sourceManifest'] == off['sourceManifest'] == runtime['sourceManifest']
assert len(off['sourceManifest']) == 302
assert off['buildRecipeSha256'] == control['buildRecipeSha256'] == runtime['buildRecipeSha256'] == '6ccabace68b5951bba98b1f713accb405d4a3ed18b3668bcd1d952a93e564677'
assert not control['streamWebEnabled'] and off['streamWebEnabled'] and runtime['streamWebEnabled']
assert not control['actualStreamWebKernelCompileCommands']
assert len(off['actualStreamWebKernelCompileCommands']) == len(runtime['actualStreamWebKernelCompileCommands']) == 1
for name, engine in [('control-stream-off', control), ('off-foundations', off), ('runtime-foundations', runtime)]:
    assert sha(freeze / (name + '.engine.wasm')) == engine['engineSha256']
    assert sha(freeze / (name + '-CMakeCache.txt')) == engine['cmakeCacheSha256']
    assert sha(freeze / (name + '-compile_commands.json')) == engine['compileCommandsSha256']
    assert not engine['gcStress'] and not engine['oomTesting'] and not engine['debuggerEnabled']
    assert engine['strictEventExceptionPolicy']['version'] == 'sm-uncaught-event-v3'
    assert engine['componentizeSourceManifest'] == off['componentizeSourceManifest']
for item in off['sourceManifest']:
    assert sha(freeze / 'source' / item['path']) == item['sha256']
for name in ['buffer', 'allocator', 'path', 'events', 'string-decoder', 'assert', 'querystring', 'util', 'stream-web']:
    assert reports[name + '.json']['engineSha256'] == off['engineSha256'], name
for name in ['sync', 'runtime', 'late', 'callback']:
    report = reports['strict-' + name + '.json']
    assert report['engineSha256'] == off['engineSha256'] and report['state'].endswith('passed')
assert reports['stream-native-guard.json']['engineSha256'] == control['engineSha256']
assert reports['stream-native-guard.json']['state'] == 'executed-corrected-native-off'
assert reports['stream-off-admission.json']['engineSha256'] == control['engineSha256']
assert len(reports['stream-off-admission.json']['results']) == 2
stream = reports['stream-web.json']
assert stream['state'] == 'executed-installed-native' and len(stream['calls']) == 3
assert len(stream['topLevelFailures']) == 7 and stream['component']['interfaceAudit']['emittedImports'] == []
assert reports['allocator.json']['refusalChecksPerCall'] == 240
assert reports['selection.json']['tests'] == reports['selection.json']['passed'] == 320
assert reports['selection.json']['failures'] == [] and len(reports['cmake-policy.json']['cases']) == 19
http = reports['http-audit.json']
assert http['engineSha256'] == runtime['engineSha256'] and http['streamWebFoundationsFixture']
assert len(http['emittedImports']) == 6 and http['clockDependency']['typeOnly']
assert not http['clockDependency']['callableImports'] and not http['clockDependency']['coreClockImports']
for name in ['wasmtime-http.json', 'wasmcloud-http.json']:
    report = reports[name]
    component_hash = report['component']['sha256'] if name == 'wasmcloud-http.json' else report['componentSha256']
    assert component_hash == http['componentSha256'] and len(report['responses']) == 3
    assert report['process']['stopped'] and report['process']['exitStatus']['code'] == 0
    for response in report['responses']:
        body = response['body']
        assert body['native']['coreVersion'] == 'sm-node-22.14.0-m0.8'
        f = body['native']['foundations']
        assert f['schema'] == 4 and len(f['aliases']['aliases']) == 14
        assert f['streamWeb']['passed'] and f['streamWeb']['iterations'] == 67 and f['streamWeb']['data'] == 26

# Archive exact native sources, configurations, original sidecars, source audits
# and licenses. Binary paths/hashes remain in receipts; don't commit engines.
shutil.copytree(freeze / 'source', stage / 'source')
shutil.copytree(freeze / 'componentize-source', stage / 'componentize-source')
for path in sorted(freeze.iterdir()):
    if path.is_file() and not path.name.endswith('.engine.wasm'):
        shutil.copy2(path, stage / path.name)
for name, path in files.items():
    shutil.copy2(path, stage / name)
for path in [base / 'engine-builds.json', base / 'engine-source-index.json', base / 'generator-check.log']:
    shutil.copy2(path, stage / path.name)
for module in ['path', 'events', 'string-decoder', 'assert', 'querystring', 'util', 'stream-web']:
    shutil.copytree(repo / 'tests/node-compat' / ('foundation-' + module), stage / 'harness' / ('foundation-' + module))
shutil.copytree(repo / 'tests/node-compat/foundation-alloc-unsafe/installed', stage / 'harness/foundation-alloc-unsafe/installed')
for name in ['checks.mjs', 'node-results.json', 'demand-source.mjs']:
    shutil.copy2(repo / 'tests/node-compat/foundation-alloc-unsafe' / name, stage / 'harness/foundation-alloc-unsafe' / name)
# Keep the preceding archive's shared helper coverage, adding new closure inputs.
paths = [str(path.relative_to(repo / 'tests/node-compat/milestones/foundations-v8/harness'))
         for path in (repo / 'tests/node-compat/milestones/foundations-v8/harness').rglob('*') if path.is_file()]
paths += ['legacy-stream-web-receipts.json', 'legacy-stream-web-test-receipt.json', 'wasi-0.2.10-interfaces.json',
          'foundations/http-v9.mjs', 'foundations/assert-stream-web-report.mjs',
          'foundations/run-v9-optional-regressions.mjs', 'foundations/run-v9-release-gates.mjs']
paths += [str(path.relative_to(repo / 'tests/node-compat')) for path in
          (repo / 'tests/node-compat/foundation-add-abort').glob('*production-v9*') if path.is_file()]
paths += ['foundation-add-abort/production-v8-preflight.mjs', 'foundation-add-abort/strict-event-v3.patch',
          'foundation-add-abort/componentize-strict-event-boundary-v2.patch',
          'foundation-add-abort/runtime-async-observation-results.json']
for name in sorted(set(paths)):
    source, target = repo / 'tests/node-compat' / name, stage / 'harness' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
shutil.copy2(repo / 'LICENSE', stage / 'LICENSE')
shutil.copy2(Path(__file__), stage / 'accept-v9.py')
records = [dict(path=str(path.relative_to(stage)), sha256=sha(path), bytes=path.stat().st_size)
           for path in sorted(stage.rglob('*')) if path.is_file()]
result = dict(schema=1, state='accepted-bounded-foundations-v9',
    acceptedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    starlingMonkeyBaseRevision=off['auditedBaseRevision'], nodeVersion='v22.14.0',
    coreVersion='sm-node-22.14.0-m0.8', streamWebVersion='sm-node-22.14.0-m0.9',
    strictCallbackPolicy='sm-uncaught-event-v3',
    engines={name: dict(sha256=engine['engineSha256'], bytes=engine['engineBytes'])
             for name, engine in [('streamWebOffControl', control), ('entropyOff', off), ('runtimeOnly', runtime)]},
    identicalCompiledSources=302, completeNativeSourceArchive='source',
    fullReports=len(files), componentSha256=http['componentSha256'], componentBytes=http['componentBytes'],
    emittedImports=http['emittedImports'], emittedExports=http['emittedExports'],
    httpRequestsPerHost=3, dynamicBareAliases=14, clockTypeOnly=True,
    requestCounters=[[response['body']['componentInstanceRequestCount'] for response in reports[name]['responses']]
                     for name in ['wasmtime-http.json', 'wasmcloud-http.json']],
    sameInstanceHTTPReuseEstablished=False, copiedEvidence=records,
    limitations=[
        'Bounded partial profile; no complete Node, Buffer, Web Streams or classic Stream compatibility.',
        'UTF8/fixed-attached-unshared/local-layout/min1 stream adapters; signal, proxy, code/arity and other manifest gaps remain.',
        'Compression/decompression constructors are explicit import-only call/new errors; no native compression transform runs.',
        'No new forced-GC or genuine allocation-failure proof for v9; earlier exact-engine gates remain separate.',
        'Strict-v3 sources are unchanged; getter timing/receiver/reentrant event parity and full teardown remain separate.',
        'No production ALS, tick queue, classic streams, Node compression/crypto or optional Node I/O variants.',
        'Corpus-heavy HTTP size is not minimal deployment size or acceleration evidence; private allocator experiment is excluded.',
        'Both stock local hosts pass; instance reuse, request isolation and concurrent reentry are not established.',
        'Copied source-stage templates and audit histories retain their own untested/historical labels; not every archived file was executed.',
    ])
(stage / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
stage.rename(destination)
print(json.dumps({'milestone': str(destination), 'copiedFiles': len(records),
    'fullReports': len(files), 'componentSha256': http['componentSha256']}, indent=2))
