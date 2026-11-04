"""Read and validate completed ordinary HTTP artifacts; no host/guest/tool runs."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import re
import shlex
import subprocess

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = BASE.parents[2]
CAP = BASE / 'classic-http-candidate-v1'
RUNTIME = BASE / 'production-runtime-activated-v2'
ADOPTION = BASE / 'production-adoption-v1'
ROOT = Path('/tmp/starling-node-compat/production-classic-http-v1/http')
OUT = ROOT / 'http-joint'
COMPONENT = '25eb1a1c7343519318ffc5a4519bc1dbd4cc1c23755a6b8fcc3bab479ffb6c7d'
IMPORTS = ['wasi:clocks/monotonic-clock@0.2.10', 'wasi:http/types@0.2.10', 'wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10', 'wasi:random/random@0.2.10']
EXPORTS = ['wasi:http/incoming-handler@0.2.10']
verified = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checked(path, digest=None, size=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    assert digest is None or sha(data) == digest, path
    assert size is None or len(data) == size, path
    verified[str(path)] = {'path': str(path), 'sha256': sha(data), 'bytes': len(data)}
    return data


def document(path, digest=None):
    return json.loads(checked(path, digest))


def indexed(root, digest, count):
    index = document(root / 'index.json', digest)
    assert len(index['files']) == count
    for row in index['files']:
        checked(root / row['path'], row['sha256'], row['bytes'])


def main():
    assert not (HERE / 'results.json').exists()
    indexed(CAP, 'ced484750a07c7897b0e40f64da85416d32793bf083082072d304b094ceec982', 63)
    indexed(BASE / 'http-host-output-retry-candidate-v1', '89b133b5d78ae35a1c60f82d2d9d2c37fb44f7da88312efdc806f210dde5554d', 15)
    indexed(BASE / 'independent-http-prehost-verification-v1', '6aaed181e304408ce61874cbf45766aab8264f7d2391936f2c7941243d01579d', 7)
    indexed(RUNTIME, '8a1b91e73475bfb007220704e08fbe68aa0b584851f70afad5607fd6c3a10d5a', 19)
    source_bytes = checked(CAP / 'input-freeze.json', '511723ec0ef2079d3fac2f6a6f78f2fa26c3be7d15cf55f7ec03a411e028193b')
    source = json.loads(source_bytes)
    assert len(source['inputs']) == 7518
    seen = set()
    for row in source['inputs']:
        path = (CAP / row['path']).resolve()
        assert path not in seen
        seen.add(path)
        checked(path, row['sha256'], row['bytes'])
    runtime = document(RUNTIME / 'input-freeze.json', 'a1543cb718043a08ab80a5409bcc66d45c38bdc75d5ed57a04645236490e60ac')
    assert len(runtime['inputs']) == 5978 and len(runtime['toolLinks']) == 22
    for tree in runtime['toolTrees']:
        root = Path(tree['path'])
        assert not root.is_symlink() and str(root.resolve()) == tree['realPath']
        rows = []
        def visit(path):
            for entry in sorted(path.iterdir()):
                kind = 'symlink' if entry.is_symlink() else 'directory' if entry.is_dir() else 'file' if entry.is_file() else None
                assert kind
                rows.append({'path': str(entry.relative_to(root)), 'kind': kind})
                if kind == 'directory':
                    visit(entry)
        visit(root)
        assert sorted(rows, key=lambda row: row['path']) == tree['entries']
    for row in runtime['toolLinks']:
        path = Path(row['path'])
        assert path.is_symlink() and os.readlink(path) == row['linkText']
        assert str(path.resolve()) == row['resolvedTarget']
        if row['targetKind'] == 'file':
            checked(row['resolvedTarget'], row['targetSha256'], row['targetBytes'])
        else:
            assert Path(row['resolvedTarget']).is_dir()
    pins = document(ADOPTION / 'reviewed-runtime-pins-v1.json', 'c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e')
    authority = document(ADOPTION / 'root-pin-review-receipt.json', '1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56')
    assert authority['reviewedPinsSha256'] == 'c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e'
    for label, pin in pins['variants'].items():
        freeze = document(pin['freezeReceiptPath'], pin['freezeReceiptSha256'])
        assert freeze['state'] == 'immutable-release-engine-frozen' and freeze['label'] == label
        assert freeze['nativeInputsVerified'] == 342 and freeze['externalEmbeddingInputsVerified'] == 3
        assert len(freeze['copies']) == 405
        for row in freeze['copies']:
            checked(row['path'], row['sha256'], row['bytes'])
    pin = pins['variants']['normal-runtime']
    metadata = document(pin['enginePath'] + '.build.json', pin['receiptSha256'])
    assert metadata['entropyPolicy'] == 'runtime-only' and metadata['gcStress'] is False
    assert metadata['classicStreamsEnabled'] is True and metadata['oomTesting'] is False and metadata['debuggerEnabled'] is False
    assert metadata['buildRecipeSha256'] == '71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
    assert len(metadata['sourceManifest']) == 342 and len(metadata['componentizeSourceManifest']) == 3
    for row in metadata['sourceManifest']:
        checked(REPO / row['path'], row['sha256'])
        checked(Path(pin['sourceRoot']) / row['path'], row['sha256'])
    commands = document(pin['commandsPath'], pin['compileCommandsSha256'])
    native = [row for row in commands if (row['file'].startswith(str(REPO / 'builtins') + '/') or row['file'].startswith(str(REPO / 'runtime') + '/')) and row['file'].endswith('.cpp')]
    assert len(native) == 61
    for row in native:
        words = shlex.split(row['command'])
        assert '-O3' in words and '-DNDEBUG' in words and '-flto=thin' in words
        assert '-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1' in words and '-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1' in words
        assert '-DDEBUG' not in words and '-D' not in words and '-U' not in words
    strict_commands = metadata['strictEventExceptionPolicy']['actualNativeCompileCommands']
    assert len(strict_commands) == 4
    strict_sources = {str(REPO / name) for name in ['builtins/web/event/event-target.cpp', 'runtime/engine.cpp', 'runtime/event_loop.cpp', 'runtime/node_tick_queue.cpp']}
    assert {shlex.split(command)[-1] for command in strict_commands} == strict_sources
    for command in strict_commands:
        assert command in [row['command'] for row in native]
        assert '-DNODE_COMPAT_STRICT_INITIALIZATION=1' in shlex.split(command)
    assert len([row for row in native if '-DNODE_COMPAT_CLASSIC_STREAMS=1' in shlex.split(row['command'])]) == 5
    checked(pin['cachePath'], pin['cmakeCacheSha256'])
    after = checked(pin['parentEmbeddingCommandPath'], pin['parentEmbeddingCommandSha256']).decode()
    assert len(metadata['actualEmbeddingCompileCommands']) == 1
    assert metadata['actualEmbeddingCompileCommands'][0] in after
    embedded_words = shlex.split(metadata['actualEmbeddingCompileCommands'][0])
    assert '-O3' in embedded_words and '-DNDEBUG' in embedded_words
    assert '-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1' in embedded_words and '-DNODE_COMPAT_STRICT_INITIALIZATION=1' in embedded_words
    assert not any(word.startswith('-DNODE_COMPAT_CLASSIC_STREAMS') for word in embedded_words)
    final = document(ROOT / 'combined-http-results.json', 'f18fc6a46d872dcbde0748671a8d20415602f4e88539d20bd6a4fb61731f4f41')
    assert final['state'] == 'COMBINED_HTTP_BASELINE_AND_CLASSIC19_VALIDATED'
    assert final['requiresIndependentBuildAndWrapperTerminalExitZero'] is True
    assert final['sourceFilesVerified'] == source['inputs'] and len(final['artifacts']) == 18
    assert final['instanceReuseClaim'] is False and final['requestIsolationClaim'] is False
    assert final['counters'] == [[1, 1, 1], [1, 1, 1]]
    for row in final['artifacts']:
        checked(row['path'], row['sha256'], row['bytes'])
    phase_path = ADOPTION / 'http-component-phase-root-review-v1.json'
    phase_bytes = checked(phase_path, 'eb1caa1168f57f135c1b38c924ef1ce99305aa34688419edd5847e242a5f9c29')
    assert checked('/tmp/starling-node-compat/classic-http-root-reviewed-phase-v1.json') == phase_bytes
    phase = json.loads(phase_bytes)['component']
    audit = document(phase['auditPath'], phase['auditSha256'])
    component = checked(phase['componentPath'], COMPONENT, 64057853)
    assert final['sourceEntryPath'] == phase['sourceEntryPath'] == audit['httpEntry'] == str(CAP / 'capability/http-component.mjs')
    assert audit['engineSha256'] == pin['engineSha256'] == final['nativeAdmission']['engineSha256']
    assert final['nativeAdmission']['sourceFilesVerified'] == 342
    assert final['nativeAdmission']['inputClosure']['sha256'] == sha(source_bytes)
    assert audit['emittedImports'] == audit['selectedInterfaces'] == audit['allowedImports'] == IMPORTS
    assert audit['emittedExports'] == EXPORTS
    assert audit['computedLiveInputChecks']['beforeCopy'] == audit['computedLiveInputChecks']['afterCopy']
    live = audit['computedLiveInputChecks']['beforeCopy']
    assert live['files'] == 8 and live['witFiles'] == 7 and live['adapterFiles'] == 1
    for row in live['inputs']:
        checked(REPO / row['name'], row['sha256'], row['bytes'])
    reader_path = BASE / 'independent-http-prehost-verification-v1/binary_reader.py'
    checked(reader_path, 'cb32f8a20904cf866b8cc9b6585f87b3461a597dca896270238c6d5b4c008fa8')
    spec = importlib.util.spec_from_file_location('bounded_public_wasm_reader', reader_path)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    imports, exports, cores = [], [], []
    types, cursor, clock_found = {}, 0, False
    for kind, part in reader.sections(component, bytes.fromhex('0061736d0d000100')):
        if kind == 7 and not clock_found:
            count, pos = reader.uint(part, 0)
            assert count == 1
            types[cursor] = part[pos:]
            cursor += count
        elif kind == 6 and not clock_found:
            count, pos = reader.uint(part, 0)
            for _ in range(count):
                assert part[pos:pos+2] == b'\x03\x00'
                _, pos = reader.uint(part, pos+2)
                _, pos = reader.string(part, pos)
                cursor += 1
            assert pos == len(part)
        elif kind == 10:
            count, pos = reader.uint(part, 0)
            for _ in range(count):
                assert part[pos] == 0
                name, pos = reader.string(part, pos+1)
                assert part[pos] == 5
                index, pos = reader.uint(part, pos+1)
                imports.append(name)
                if name == IMPORTS[0]:
                    assert index == 5 and types[index] == bytes.fromhex('420201770400086475726174696f6e030000')
                    clock_found = True
            assert pos == len(part)
        elif kind == 11:
            count, pos = reader.uint(part, 0)
            for _ in range(count):
                assert part[pos] == 0
                name, pos = reader.string(part, pos+1)
                assert part[pos] == 5
                _, pos = reader.uint(part, pos+1)
                assert part[pos] == 0
                pos += 1
                exports.append(name)
            assert pos == len(part)
        elif kind == 1:
            cores.append({'sha256': sha(part), 'bytes': len(part), 'imports': reader.core_imports(part)})
    assert sorted(imports) == IMPORTS and exports == EXPORTS and clock_found and len(cores) == 3
    assert not any(row['module'].startswith('wasi:clocks/') or row['module'] == 'wasi_snapshot_preview1' for core in cores for row in core['imports'])
    assert cores[0]['imports'] == audit['packagingAudit']['coreImports']
    graph = document(OUT / 'component-types.json', audit['clockDependency']['componentTypeGraph']['sha256'])
    clocks = [(i, row) for i, row in enumerate(graph['interfaces']) if row.get('name') == 'monotonic-clock' and graph['packages'][row['package']]['name'] == 'wasi:clocks@0.2.10']
    assert len(clocks) == 1
    clock_index, clock = clocks[0]
    assert clock['functions'] == {} and list(clock['types']) == ['duration']
    assert graph['types'][clock['types']['duration']]['kind'] == {'type': 'u64'}
    assert audit['clockDependency']['typeOnly'] and audit['clockDependency']['callableImports'] == audit['clockDependency']['coreClockImports'] == []
    assert any(row['interface']['id'] == clock_index for row in graph['worlds'][0]['imports'].values())
    wasmtime = document(OUT / 'wasmtime-v2/wasmtime-results.json')
    wash = document(ROOT / 'http-joint-wasmcloud-results.json')
    assert wasmtime['command'] == [wasmtime['command'][0], 'serve', '--addr', '127.0.0.1:0', phase['componentPath']]
    checked(wasmtime['command'][0], 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c')
    checked(wash['host']['binaryPath'], '365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954')
    assert wash['host']['unmodifiedOfficialBinary'] and wash['host']['version'] == '2.11.0'
    checked(wash['component']['deployedPath'], COMPONENT, 64057853)
    assert wash['component']['path'] == wasmtime['command'][-1] == phase['componentPath']
    assert wash['componentAudit'] == audit
    assert wash['hostInspection']['emittedImports'] == IMPORTS and wash['hostInspection']['emittedExports'] == EXPORTS
    config = document(wash['configPath'])
    assert config == wash['configuration']
    for key in ['components', 'plugins', 'host_plugins', 'volumes']:
        assert config['dev'][key] == []
    assert config['dev']['service'] is False
    for key in ['allowedHosts', 'allowedIpNameLookups', 'allowedHostLoopbackPorts']:
        assert config['workload'][key] == wash['effectiveConfiguration']['workload'][key] == []
    assert document(wash['configInspectionCommand'][wash['configInspectionCommand'].index('--user-config')+1]) == {}
    for key in ['customHostPlugins', 'sidecars', 'volumes', 'outgoingHostAllowlist', 'ipNameLookupAllowlist', 'hostLoopbackPortAllowlist']:
        assert wash['isolation'][key] == []
    for key in ['globalInstallationModified', 'dockerUsed', 'natsUsed', 'publicListener']:
        assert wash['isolation'][key] is False
    assert wash['isolation']['isolatedXdgDirectories'] is True
    for host in [wasmtime, wash]:
        assert host['process']['stopped'] is True and host['process']['exitStatus'] == {'code': 0, 'signal': None}
        assert len(host['responses']) == 3 and host['retainedStateObserved'] is False
        for row in host['responses']:
            assert row['status'] == 200 and row['body']['componentInstanceRequestCount'] == 1
    receipt_specs = [
        ('http-wash-root-results.json', 'b1b7c0096469db0e537574299f4d036909bfff77b00994055f264d01a8070747', 'rawTerminalExitCodeObservedByRoot'),
        ('http-wasmtime-v2-root-results.json', '4399c49f99d44df79f405fb7597565df592a4482d91a114ee6d4764678dc49fa', 'rawTerminalExitCodeObservedByRoot'),
        ('http-combined-root-results.json', '5bcf66583a4364d824cf3f4f09d982d6e10136b781be3d4808a3ce8f685928a6', 'finalAuditRawTerminalExitCodeObservedByRoot')]
    for name, digest, status_key in receipt_specs:
        receipt = document(ADOPTION / name, digest)
        assert receipt[status_key] == 0 and receipt['componentSha256'] == COMPONENT
        for row in receipt['evidence']:
            checked(row['path'], row['sha256'], row['bytes'])
    failure = document(ADOPTION / 'http-wasmtime-attempt1-root-results.json')
    assert failure['rawTerminalExitCodeObservedByRoot'] == 1 and failure['passClaim'] is False
    assert failure['finalReportPublished'] is False and failure['completionPublished'] is False
    for row in failure['evidence']:
        checked(row['path'], row['sha256'], row['bytes'])
    node = '/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
    checked(node, 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
    env = dict(os.environ)
    env.pop('NODE_COMPAT_HTTP_REQUIRE_INTRINSICS', None)
    result = subprocess.run([node, str(HERE / 'check-responses.mjs')], env=env, capture_output=True, text=True)
    for name, value in [('response-check.stdout.log', result.stdout), ('response-check.stderr.log', result.stderr)]:
        with (HERE / name).open('x') as stream:
            stream.write(value)
    assert result.returncode == 0, result.stderr
    response = document(HERE / 'response-check-results.json')
    assert response['responsesChecked'] == 6
    for path, row in list(verified.items()):
        checked(path, row['sha256'], row['bytes'])
    report = {
        'schemaVersion': 1, 'state': 'INDEPENDENT_ACTUAL_COMBINED_HTTP_RESULTS_REVIEW_PASSED',
        'componentSha256': COMPONENT, 'componentBytes': 64057853,
        'finalReportSha256': 'f18fc6a46d872dcbde0748671a8d20415602f4e88539d20bd6a4fb61731f4f41',
        'sourceFilesVerified': 7518, 'toolTreesVerified': len(runtime['toolTrees']), 'toolLinksVerified': 22,
        'nativeSourcesVerified': 342, 'fourFreezeCopyCounts': [405]*4,
        'finalArtifactRecordsVerified': 18, 'responsesVerified': 6, 'requestsPerHost': 3,
        'baselineSchema': 5, 'protectedAbortGroupsPerResponse': 29, 'ordinaryClassicGroupsPerResponse': 19,
        'dataOnlyFullResponseAssertionsExitCode': result.returncode,
        'counters': [[1, 1, 1], [1, 1, 1]], 'instanceReuseClaim': False, 'requestIsolationClaim': False,
        'binaryImports': sorted(imports), 'binaryExports': exports, 'binaryClockU64TypeOnly': True,
        'embeddedCoreModules': cores, 'coreClockAndPreview1Imports': [],
        'originalSourceEntryPreserved': phase['sourceEntryPath'], 'liveWitAndAdapterInputsVerified': 8,
        'bothHostOfficialBinaryHashesVerified': True, 'bothDeployedComponentCopiesByteEqual': True,
        'observedHostCleanup': 'Persisted reports and Root-observed raw terminal receipts say stopped=true/code0; no process was started or stopped by this reader.',
        'failedWasmtimeV1Preserved': True,
        'collectorStateNote': 'checks.state overrides the pre-spread CLI label; actual state matches all data assertions and the independent outer-exit requirement remains true.',
        'executionScope': 'File/hash/config/source/static public Wasm reading and data-only assertion functions; no whole preflight, native build, componentizer, guest or target host execution.',
        'limitations': ['Ordinary classic19 plus baseline schema5/protected29 only; no full Node streams or node:http claim.',
            'Counters restart at1; repeated success establishes neither same-instance reuse nor request isolation.',
            'Known fresh callback-return then-getter and Symbol registry/description gaps remain.',
            'GC coowners, ALS/reset/cancellation, classic fatal/limits/CJS/GC and performance remain outside this HTTP proof.'],
        'verifiedFiles': sorted(verified.values(), key=lambda row: row['path'])}
    with (HERE / 'results.json').open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({key: report[key] for key in ['state', 'sourceFilesVerified', 'responsesVerified', 'finalArtifactRecordsVerified']}))


if __name__ == '__main__':
    main()
