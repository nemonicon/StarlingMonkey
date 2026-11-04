"""Read completed classic HTTP artifacts only; no tools, guest or hosts."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
from binary_reader import sections, uint, string, core_imports

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CAP = HERE.parent / 'classic-http-candidate-v1'
RUNTIME = HERE.parent / 'production-runtime-activated-v2'
ROOT = Path('/tmp/starling-node-compat/production-classic-http-v1/http')
OUT = ROOT / 'http-joint'
EXPECTED = ['wasi:clocks/monotonic-clock@0.2.10', 'wasi:http/types@0.2.10', 'wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10', 'wasi:random/random@0.2.10']
EXPORTS = ['wasi:http/incoming-handler@0.2.10']
verified = {}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def checked(path, expected=None, size=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    assert expected is None or sha(data) == expected, path
    assert size is None or len(data) == size, path
    verified[str(path)] = {'path': str(path), 'sha256': sha(data), 'bytes': len(data)}
    return data

def document(path, expected=None):
    return json.loads(checked(path, expected))

def indexed(path, expected):
    index = document(path / 'index.json', expected)
    for row in index['files']:
        checked(path / row['path'], row['sha256'], row['bytes'])
    return index

def main():
    assert not (HERE / 'results.json').exists()
    indexed(CAP, 'ced484750a07c7897b0e40f64da85416d32793bf083082072d304b094ceec982')
    indexed(RUNTIME, '8a1b91e73475bfb007220704e08fbe68aa0b584851f70afad5607fd6c3a10d5a')
    manifest = document(CAP / 'input-freeze.json', '511723ec0ef2079d3fac2f6a6f78f2fa26c3be7d15cf55f7ec03a411e028193b')
    assert len(manifest['inputs']) == 7518
    source_map = {}
    for row in manifest['inputs']:
        path = (CAP / row['path']).resolve()
        checked(path, row['sha256'], row['bytes'])
        source_map[path] = row
    runtime_seal = document(RUNTIME / 'input-freeze.json', 'a1543cb718043a08ab80a5409bcc66d45c38bdc75d5ed57a04645236490e60ac')
    assert len(runtime_seal['inputs']) == 5978
    for tree in runtime_seal['toolTrees']:
        root = Path(tree['path'])
        assert str(root.resolve()) == tree['realPath'] and not root.is_symlink()
        rows = []
        def visit(path):
            for item in sorted(path.iterdir()):
                kind = 'symlink' if item.is_symlink() else 'directory' if item.is_dir() else 'file' if item.is_file() else None
                assert kind
                rows.append({'path': str(item.relative_to(root)), 'kind': kind})
                if kind == 'directory':
                    visit(item)
        visit(root)
        assert sorted(rows, key=lambda row: row['path']) == tree['entries']
    for row in runtime_seal['toolLinks']:
        path = Path(row['path'])
        assert path.is_symlink() and os.readlink(path) == row['linkText']
        assert str(path.resolve()) == row['resolvedTarget']
        if row['targetKind'] == 'file':
            checked(row['resolvedTarget'], row['targetSha256'], row['targetBytes'])
        else:
            assert Path(row['resolvedTarget']).is_dir()
    pins = document(HERE.parent / 'production-adoption-v1/reviewed-runtime-pins-v1.json', 'c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e')
    freezes = []
    for label, pin in pins['variants'].items():
        freeze = document(pin['freezeReceiptPath'], pin['freezeReceiptSha256'])
        assert freeze['state'] == 'immutable-release-engine-frozen' and len(freeze['copies']) == 405
        for row in freeze['copies']:
            checked(row['path'], row['sha256'], row['bytes'])
        freezes.append({'label': label, 'receiptSha256': pin['freezeReceiptSha256'], 'copies': len(freeze['copies'])})
    pin = pins['variants']['normal-runtime']
    assert pin['engineSha256'] == '1a3f4628d4f63445ec0c1a212a38f1eb3ac01fe22ea2d5d2d54f0210f388fd14'
    a = document(OUT / 'component-audit.json')
    component_path = OUT / 'native-profile-http.component.wasm'
    data = checked(component_path, '25eb1a1c7343519318ffc5a4519bc1dbd4cc1c23755a6b8fcc3bab479ffb6c7d', 64057853)
    assert a['componentSha256'] == sha(data) and a['componentBytes'] == len(data) and a['componentPath'] == str(component_path)
    assert a['engineSha256'] == pin['engineSha256'] and a['engine'] == pin['enginePath']
    metadata = document(a['engineMetadataPath'], pin['receiptSha256'])
    assert metadata['entropyPolicy'] == 'runtime-only' and metadata['gcStress'] is False and metadata['classicStreamsEnabled'] is True
    bundle = checked(OUT / 'http.bundle.mjs', '2fab5aabb3aa48dff806fff8e21b202f8883cffad5eb20578bed9ad50a9c029c')
    assert a['applicationBundleSha256'] == sha(bundle)
    assert a['httpEntry'] == str(CAP / 'capability/http-component.mjs')
    for name in ['selectedInterfaces', 'allowedImports', 'emittedImports']:
        assert a[name] == EXPECTED
    assert a['emittedExports'] == EXPORTS and a['applicationBundleExports'] == ['incomingHandler']
    assert a['interfaceAudit']['state'] == 'verified-final-component' and a['interfaceAudit']['componentSha256'] == sha(data)
    assert a['interfaceAudit']['selectedInterfaces'] == a['interfaceAudit']['emittedImports'] == EXPECTED
    assert a['interfaceAudit']['unusedSelectedInterfaces'] == []
    wit = checked(OUT / 'emitted.wit').decode()
    assert wit == a['emittedWit']
    assert sorted(re.findall(r'^\s*import ([^;]+);', wit, re.M)) == EXPECTED
    assert re.findall(r'^\s*export ([^;]+);', wit, re.M) == EXPORTS
    assert checked(OUT / 'wit/profile.wit').decode() == a['worldSource']
    imports, exports, cores = [], [], []
    type_cursor, type_definitions, clock_found = 0, {}, False
    for kind, part in sections(data, bytes.fromhex('0061736d0d000100')):
        if kind == 7 and not clock_found:
            count, pos = uint(part, 0)
            assert count == 1
            type_definitions[type_cursor] = part[pos:]
            type_cursor += count
        elif kind == 6 and not clock_found:
            count, pos = uint(part, 0)
            for _ in range(count):
                assert part[pos:pos+2] == b'\x03\x00'
                _, pos = uint(part, pos+2)
                _, pos = string(part, pos)
                type_cursor += 1
            assert pos == len(part)
        elif kind == 10:
            count, pos = uint(part, 0)
            for _ in range(count):
                assert part[pos] == 0
                name, pos = string(part, pos+1)
                assert part[pos] == 5
                index, pos = uint(part, pos+1)
                imports.append(name)
                if name == EXPECTED[0]:
                    assert index == 5 and type_definitions[index] == bytes.fromhex('420201770400086475726174696f6e030000')
                    clock_found = True
            assert pos == len(part)
        elif kind == 11:
            count, pos = uint(part, 0)
            for _ in range(count):
                assert part[pos] == 0
                name, pos = string(part, pos+1)
                assert part[pos] == 5
                _, pos = uint(part, pos+1)
                assert part[pos] == 0
                pos += 1
                exports.append(name)
            assert pos == len(part)
        elif kind == 1:
            cores.append({'bytes': len(part), 'sha256': sha(part), 'imports': core_imports(part)})
    assert sorted(imports) == EXPECTED and exports == EXPORTS and clock_found and len(cores) == 3
    all_imports = [row for core in cores for row in core['imports']]
    assert not any(row['module'].startswith('wasi:clocks/') or row['module'] == 'wasi_snapshot_preview1' for row in all_imports)
    assert cores[0]['imports'] == a['packagingAudit']['coreImports']
    assert sorted({row['module'] for row in cores[0]['imports']}) == a['executableCoreInterfaces']
    assert sorted({row['module'] for row in all_imports if row['module'].startswith('wasi:')}) == EXPECTED[1:]
    raw_core = checked(OUT / 'native-profile-http.core.wasm', a['packagingAudit']['finalWrapping']['coreSha256'])
    embedded_core = next(part for kind, part in sections(data, bytes.fromhex('0061736d0d000100')) if kind == 1)
    core_sections = lambda body: [(kind, sha(part)) for kind, part in sections(body, bytes.fromhex('0061736d01000000')) if kind != 0]
    assert core_sections(raw_core) == core_sections(embedded_core)
    custom_counts = [sum(kind == 0 for kind, _ in sections(body, bytes.fromhex('0061736d01000000'))) for body in [raw_core, embedded_core]]
    graph = document(OUT / 'component-types.json', a['clockDependency']['componentTypeGraph']['sha256'])
    clock = [(i, row) for i, row in enumerate(graph['interfaces']) if row.get('name') == 'monotonic-clock' and graph['packages'][row['package']]['name'] == 'wasi:clocks@0.2.10']
    assert len(clock) == 1
    clock_index, clock = clock[0]
    assert clock['functions'] == {} and list(clock['types']) == ['duration']
    assert graph['types'][clock['types']['duration']]['kind'] == {'type': 'u64'}
    assert len(graph['worlds']) == 1 and len(graph['worlds'][0]['imports']) == 6 and len(graph['worlds'][0]['exports']) == 1
    assert any(row['interface']['id'] == clock_index for row in graph['worlds'][0]['imports'].values())
    assert a['clockDependency']['typeOnly'] and a['clockDependency']['coreClockImports'] == a['clockDependency']['callableImports'] == []
    checked(a['clockDependency']['tool']['path'], a['clockDependency']['tool']['sha256'])
    pack = document(OUT / 'packaging-audit.json')
    assert pack == a['packagingAudit'] and pack['initialBindingFeatures'] == pack['finalStubFeatures'] == ['http', 'random']
    assert pack['finalWrapping']['adapters'] == [] and not a['preview1Adapter']['usedInFinalWrapping']
    prov = a['componentizerProvenance']
    assert prov['selection'] == 'patched-import-i32-clock-v2'
    checked(prov['manifestPath'], prov['manifestSha256'])
    for row in prov['checkedFiles']:
        checked(Path(prov['modulePath']).parent.parent / row['path'], row['sha256'])
    checked(prov['lock']['path'], prov['lock']['sha256'])
    checked(a['preview1Adapter']['path'], a['preview1Adapter']['sha256'], a['preview1Adapter']['bytes'])
    before, after = a['computedLiveInputChecks']['beforeCopy'], a['computedLiveInputChecks']['afterCopy']
    assert before == after and before['state'] == 'EXACT_EIGHT_LIVE_HTTP_INPUTS_MATCH_SEAL' and before['files'] == 8
    assert before['witFiles'] == 7 and before['adapterFiles'] == 1
    for row in before['inputs']:
        path = (REPO / row['name']).resolve()
        assert source_map[path]['sha256'] == row['sha256']
        checked(path, row['sha256'], row['bytes'])
        if row['name'].endswith('package.wit'):
            checked(OUT / 'wit/deps' / Path(row['name']).parent.name / 'package.wit', row['sha256'], row['bytes'])
    inputs = document(ROOT / 'http-inputs.json')
    assert inputs['state'] == 'CLASSIC342_HTTP_INPUTS_FROZEN_BEFORE_PACKAGING'
    assert inputs['sourceInputClosure'] == a['currentProductionAdmission']['inputClosure']
    assert inputs['nativeAdmission'] == a['currentProductionAdmission'] and inputs['classicOrdinaryGroups'] == 19
    complete = document(OUT / 'production-admission-complete.json')
    assert complete['sourceInputsRecheckedAfterRun'] and complete['requiresIndependentTerminalExitZero']
    assert complete['inputClosure'] == inputs['sourceInputClosure'] and complete['engineSha256'] == pin['engineSha256']
    assert document(CAP / 'capability/component-pins.json')['component'] is None
    assert len(a['bundledModules']) == 53
    for name in a['bundledModules']:
        if name.startswith('\0'):
            assert name == '\0sm-classic-http-composer-v1'
        else:
            assert Path(name.removesuffix('.native-profile.mjs')).resolve() in source_map, name
    assert not re.search(r'createBufferModule|createEventsFacade|reference-kernel|node_modules/(?:buffer|unenv)|__require', bundle.decode())
    assert a['foundationOracles']['protectedAbort']['counts'] == {'public': 16, 'nested': 4, 'receivers': 9, 'total': 29}
    combined = a['classicCombinedHTTP']
    assert combined['schema'] == 1 and combined['ordinaryGroups'] == 19
    assert combined['nodeOracleSha256'] == '88bd20781a396e6fd178d3b014a98495fec848eb28adb81c80e7dc838f4686ce'
    for path, key in [(Path(combined['baselineEntry']), 'baselineSha256'), (CAP / 'capability/ordinary.mjs', 'ordinarySourceSha256'), (RUNTIME / 'harness/checks.mjs', 'checksSourceSha256')]:
        checked(path, combined[key])
    logs = Path('/tmp/starling-node-compat')
    assert document(logs / 'classic-http-build-v1.stdout.log') == a
    assert checked(logs / 'classic-http-build-v1.stderr.log') == b''
    assert checked(logs / 'classic-http-prepare-v1.stderr.log') == b''
    assert document(logs / 'classic-http-prepare-v1.stdout.log') == {'root': str(ROOT), 'packaged': False}
    for row in list(verified.values()):
        checked(row['path'], row['sha256'], row['bytes'])
    result = {'schemaVersion': 1, 'state': 'INDEPENDENT_CLASSIC_HTTP_PREHOST_ARTIFACT_REVIEW_PASSED',
              'verifiedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'component': {'componentPath': str(component_path), 'componentSha256': sha(data), 'componentBytes': len(data),
                            'auditSha256': sha((OUT / 'component-audit.json').read_bytes()), 'applicationBundleSha256': sha(bundle),
                            'inputsSha256': sha((ROOT / 'http-inputs.json').read_bytes()), 'sourceEntryPath': a['httpEntry'],
                            'engineSha256': pin['engineSha256'], 'engineReceiptSha256': pin['receiptSha256'],
                            'sourceInputSha256': inputs['sourceInputClosure']['sha256']},
              'sourcePacketFiles': 63, 'heldSourceInputs': 7518, 'runtimeIndexedSourceFamily': str(RUNTIME),
              'runtimeInputFiles': 5978, 'toolTrees': len(runtime_seal['toolTrees']), 'toolLinks': len(runtime_seal['toolLinks']),
              'actualFourNativeFreezes': freezes, 'nativeSources': 342, 'bundleModules': 53,
              'binaryRootImports': sorted(imports), 'binaryRootExports': exports, 'binaryClockU64DurationOnly': True,
              'clockCallableImports': [], 'clockCoreImports': [], 'embeddedCores': cores,
              'nonCustomCoreSectionsIdentical': True, 'rawAndEmbeddedCustomCounts': custom_counts,
              'liveEightCurrentlyRehashedAndRecordedBeforeAfterIdentical': True, 'ordinaryClassicGroups': 19,
              'baselineProtectedGroups': 29, 'localComponentPinStillNull': True,
              'noConcretePrehostArtifactBlockerFound': True, 'verifiedFiles': list(verified.values()),
              'reviewerGuestHostToolBuildOrRepackExecuted': False, 'runtimeAcceptanceClaim': False,
              'limitations': ['Narrow binary parser verifies concrete import/export/core and duration encodings; it does not repeat full Component Model validation.',
                              'Root observed prepare/build raw terminal0; stdout audit and empty stderr are rehashed here. No independent PID-status file is invented.',
                              'No host started or phase authority written. Root must review the actual tuple then provide its separately hashed external phase document.',
                              'Same-byte stock-host responses, stop0 and raw combined baseline/classic validations remain future gates.',
                              'No full Node streams, hidden trap cause, reset/ALS, GC owner isolation, instance reuse, request isolation or performance claim.']}
    with (HERE / 'results.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'state': result['state'], 'verifiedFiles': len(verified), 'componentSha256': sha(data), 'resultsSha256': sha((HERE / 'results.json').read_bytes())}))

if __name__ == '__main__':
    main()
