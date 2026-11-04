"""Read completed public trace evidence/binaries only; never run a component."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = BASE.parents[2]
SOURCE = BASE / 'stream-trace-regression-candidate-v1'
RUNTIME = BASE / 'production-runtime-activated-v3'
OUTPUT = Path('/tmp/starling-node-compat/production-classic-stream-trace-v1')
ADOPTION = BASE / 'production-adoption-v1'
checked = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path, digest=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    after = path.lstat()
    assert (before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns)
    assert digest is None or sha(data) == digest, path
    assert size is None or len(data) == size, path
    checked[str(path)] = {'path': str(path), 'sha256': sha(data), 'bytes': len(data)}
    return data


def document(path, digest=None):
    return json.loads(read(path, digest))


def indexed(root, digest):
    index = document(root / 'index.json', digest)
    for row in index['files']:
        read(root / row['path'], row['sha256'], row['bytes'])
    return len(index['files'])


def main():
    root = document(ADOPTION / 'stream-trace-component-root-results.json', 'e53ded5e9cf00546bfab45f1603c7a3e529c33d86f975cf36271db48d8eeb6a2')
    assert root['rawTerminalExitCodeObservedByRoot'] == 0 and root['toolSession'] == 80465
    assert root['nodeCompatibilityPassed'] is False and root['hostModelEqualsActualGuest'] is True
    assert len(root['evidence']) == 11 and len(root['links']) == 1
    for row in root['evidence']:
        read(row['path'], row['sha256'], row['bytes'])
    for row in root['links']:
        path = Path(row['path'])
        assert path.is_symlink() and os.readlink(path) == row['target']
        assert path.resolve() == Path(row['target']).resolve() and path.is_dir()
    assert indexed(SOURCE, '636dfc0561891ff23f028b19289693aa77452fc25e8c5b415f1bf4a191afe7ac') == 15
    indexed(BASE / 'independent-stream-trace-source-review-v1', '0736abc17f880fd9416bf03b0f0346a1b49092d12a3337574241c8d784f4c28a')
    source_bytes = read(SOURCE / 'input-freeze.json', 'b6b4e79f4c13f2e844a8361618e2038d4aa176ad62dd1566a5c44b2f32ee6a3b')
    source = json.loads(source_bytes)
    assert len(source['inputs']) == 6015
    seen = set()
    for row in source['inputs']:
        path = (SOURCE / row['path']).resolve()
        assert path not in seen
        seen.add(path)
        read(path, row['sha256'], row['bytes'])
    template = read(SOURCE / 'preflight.template.mjs').decode()
    assert template.replace('@INPUTS_SHA@', sha(source_bytes)) == read(SOURCE / 'preflight.mjs').decode()
    assert indexed(RUNTIME, '7e9520e0859b939a8586e6d0cfa1fe376a3ace75a2624dd777d5825bbf91cf66') == 19
    runtime = document(RUNTIME / 'input-freeze.json')
    assert len(runtime['inputs']) == 6000 and len(runtime['toolLinks']) == 22
    for tree in runtime['toolTrees']:
        path = Path(tree['path'])
        assert not path.is_symlink() and str(path.resolve()) == tree['realPath']
        rows = []
        def visit(directory):
            for child in sorted(directory.iterdir()):
                kind = 'symlink' if child.is_symlink() else 'directory' if child.is_dir() else 'file' if child.is_file() else None
                assert kind
                rows.append({'path': str(child.relative_to(path)), 'kind': kind})
                if kind == 'directory':
                    visit(child)
        visit(path)
        assert sorted(rows, key=lambda row: row['path']) == tree['entries']
    for row in runtime['toolLinks']:
        path = Path(row['path'])
        assert path.is_symlink() and os.readlink(path) == row['linkText'] and str(path.resolve()) == row['resolvedTarget']
        if row['targetKind'] == 'file':
            read(row['resolvedTarget'], row['targetSha256'], row['targetBytes'])
    pins = document(ADOPTION / 'reviewed-runtime-pins-v1.json', 'c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e')
    document(ADOPTION / 'root-pin-review-receipt.json', '1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56')
    for pin in pins['variants'].values():
        freeze = document(pin['freezeReceiptPath'], pin['freezeReceiptSha256'])
        assert freeze['nativeInputsVerified'] == 342 and freeze['externalEmbeddingInputsVerified'] == 3 and len(freeze['copies']) == 405
        for row in freeze['copies']:
            read(row['path'], row['sha256'], row['bytes'])
    pin = pins['variants']['normal-off']
    assert pin['engineSha256'] == 'b8279ee1fedc4e26b7319b6777f6a413242cee0c36169a14195f5c24c44511e4'
    metadata = document(pin['enginePath']+'.build.json', pin['receiptSha256'])
    assert metadata['entropyPolicy'] == 'off' and metadata['gcStress'] is False and metadata['classicStreamsEnabled'] is True
    assert metadata['debuggerEnabled'] is False and metadata['oomTesting'] is False
    assert len(metadata['sourceManifest']) == 342
    for row in metadata['sourceManifest']:
        read(REPO / row['path'], row['sha256'])
        read(Path(pin['sourceRoot']) / row['path'], row['sha256'])
    # The reviewed semantics fix is still separate; current source is the old core.
    assert sha(read(REPO / 'builtins/node-compat/classic-streams/classic-core.generated.mjs')) == 'ba39701153094c6481464fa3f45a7afd87e6d41d673026e8008e12f2693802bf'
    completion = document(OUTPUT / 'completion.json', '6a4fd457732cc560db4449f5fcbf4bb4cd0fbafe05a0ec9e11fbbdd22d67d178')
    assert completion['state'] == 'CLASSIC_GATE_OUTPUTS_COMPLETE_REQUIRES_EXTERNAL_EXIT_ZERO'
    assert completion['requiresIndependentTerminalExitCodeZero'] and completion['terminalExitCodeObservedByThisHelper'] is None
    assert completion['finalAdmissionRecheckCompletedBeforeReportPublication'] is True
    assert completion['componentFiles'] == ['stream-trace.component.wasm']
    assert completion['generatedWasmFiles'] == ['stream_trace.core.wasm']
    assert len(completion['files']) == 8
    for row in completion['files']:
        assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
        read(OUTPUT / row['path'], row['sha256'], row['bytes'])
    report = document(OUTPUT / 'results.json', completion['results']['sha256'])
    assert report['status'] == 'REAL_COMPONENT_PUBLIC_STREAM_TRACE_OBSERVATIONS_COMPLETE'
    assert report['nodeCompatibilityPassed'] is False and report['hostModelEqualsActualGuest'] is True
    assert report['engineSha256'] == pin['engineSha256'] and report['engineReceiptSha256'] == pin['receiptSha256'] and report['nativeSources'] == 342
    assert report['requiresIndependentTerminalExitCodeZero'] is True
    assert report['interfaceAudit']['emittedImports'] == report['interfaceAudit']['selectedInterfaces'] == []
    wit = read(OUTPUT / 'emitted.wit').decode()
    assert wit == report['emittedWit'] == 'package root:component;\n\nworld root {\n  export run: func() -> string;\n}\n'
    reader_path = BASE / 'independent-http-prehost-verification-v1/binary_reader.py'
    read(reader_path, 'cb32f8a20904cf866b8cc9b6585f87b3461a597dca896270238c6d5b4c008fa8')
    spec = importlib.util.spec_from_file_location('public_component_sections', reader_path)
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    component = read(report['componentPath'], 'f896b7c2f9450ce54d7791ca86a60a38ce6df9bf7c363b00dd42d030ff5f4827', 12933484)
    parts = list(helpers.sections(component, bytes.fromhex('0061736d0d000100')))
    assert not [body for kind, body in parts if kind == 10]
    assert [body.hex() for kind, body in parts if kind == 7] == ['0140000073']  # one () -> string component function type
    assert [body.hex() for kind, body in parts if kind == 11] == ['01000372756e010000']  # one run function export
    cores = [body for kind, body in parts if kind == 1]
    assert len(cores) == 1 and cores[0] == read(OUTPUT / 'stream_trace.core.wasm')
    core_imports = helpers.core_imports(cores[0])
    assert not any(row['module'].startswith('wasi:') or row['module'] == 'wasi_snapshot_preview1' for row in core_imports)
    glue = read(OUTPUT / 'stream_trace.js').decode()
    assert 'stream_trace.core.wasm' in glue
    assert report['bundleImports'] == ['node:stream', 'node:buffer']
    assert report['sourceModules'] == [str(SOURCE/'cases.mjs'), str(SOURCE/'guest.mjs')]
    read(OUTPUT / 'guest.bundle.mjs', report['bundleSha256'])
    oracle = document(SOURCE / 'node-results.json', report['nodeOracleSha256'])
    assert oracle['groups'] == 8 and oracle['node'] == 'v22.14.0'
    assert report['nodeObserved'] == oracle['nodeObserved']
    retained = report['retained']
    assert len(retained) == 3 and [row['calls'] for row in retained] == [1, 2, 3]
    observations = retained[0]['observed']
    assert observations == oracle['hostModelObserved'] and len(observations) == 8
    assert report['freshJco'] == retained[0] == report['wasmtime']['observed']
    assert report['wasmtime']['status'] == 0 and report['wasmtime']['stderr'] == ''
    # This fixture's public CLI string is standard JSON syntax and wholly ASCII.
    stdout = report['wasmtime']['stdout']
    assert stdout.isascii() and json.loads(json.loads(stdout)) == retained[0]
    read(report['wasmtime']['path'], 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c')
    for result in retained + [report['freshJco'], report['wasmtime']['observed']]:
        assert result['observed'] == observations and result['snapshot'] == {'bytes': 64, 'checksum': 151852933}
        for row in result['observed']:
            assert row['inputBytes'] == row['bytes'] == 64 and row['checksum'] == 151852933
            assert row['writeCalls'] == row['callbackCalls'] == 1 and len(row['events']) < 128
            if row['kind'] == 'writable':
                assert row['finish'] == row['close'] == 1
            else:
                assert all(value == 1 for value in row['counts'].values())
    differences = [{'id': node['id'], 'node': node, 'guest': guest} for node, guest in zip(oracle['nodeObserved'], observations) if node != guest]
    assert differences == report['differences']
    ids = ['writable-sync-hwm64', 'writable-sync-hwm63', 'passthrough-pipeline-sync', 'passthrough-pipeline-microtask']
    assert [row['id'] for row in differences] == root['differenceIds'] == ids
    for row in differences[:2]:
        assert row['node']['accepted'] is True and row['guest']['accepted'] is False
    for row in differences[2:]:
        assert row['node']['events'].index(['source', 'end']) < row['node']['events'].index(['source', 'finish'])
        assert row['guest']['events'].index(['source', 'finish']) < row['guest']['events'].index(['source', 'end'])
    packager = report['packager']
    assert packager['selection'] == 'patched-import-i32-clock-v2' and packager['legacyEngineDiagnosticEnabled'] is False and packager['debugScalarOOMDiagnostic'] is None
    read(packager['manifestPath'], packager['manifestSha256'])
    package_root = Path(packager['modulePath']).parent.parent
    for row in packager['checkedFiles']:
        read(package_root / row['path'], row['sha256'])
    read(packager['lock']['path'], packager['lock']['sha256'])
    for path, row in list(checked.items()):
        read(path, row['sha256'], row['bytes'])
    result = {'schemaVersion': 1, 'state': 'INDEPENDENT_ACTUAL_STREAM_TRACE_COUNTEREXAMPLES_VERIFIED_NOT_NODE_PARITY',
        'componentSha256': report['componentSha256'], 'componentBytes': report['componentBytes'],
        'rootReceiptSha256': 'e53ded5e9cf00546bfab45f1603c7a3e529c33d86f975cf36271db48d8eeb6a2',
        'rootRawTerminalExitZeroObservedByRoot': True, 'regularRootEvidenceFiles': 11, 'outputSymlinkChecked': 1,
        'sourceIndexedFiles': 15, 'sourceInputsRehashed': 6015, 'runtimeInputs': 6000, 'toolTrees': 2, 'toolLinks': 22,
        'nativeSources': 342, 'fourFrozenCopyCounts': [405]*4, 'currentOldSemanticsCoreUnchanged': True,
        'publicBinaryImports': [], 'publicBinaryExports': ['run:func()->string'], 'emittedWitExact': True,
        'embeddedCoreEqualsJcoCore': True, 'coreImports': core_imports,
        'retainedCallNumbers': [1, 2, 3], 'freshJcoAndFreshWasmtimeCall': 1, 'observationsPerCall': 8,
        'allFiveRecordedObservationArraysEqual': True, 'publicWasmtimeStringIndependentlyDecoded': True,
        'actualNodeGapIds': ids, 'hostModelEqualsActualGuest': True, 'nodeCompatibilityPassed': False,
        'scope': 'Completed valid-input observation, not compatibility or fix acceptance. Minimal source-PassThrough event order is distinct from the larger benchmark middle-pass topology.',
        'executedComponentOrGuestOrNodeOrNativeOrHostOrPackaging': False,
        'knownLimits': ['Only8 ordinary64byte cases;14 full-workload gaps are not all reproduced by this component.',
            'No reset/ALS/reuse/GC/total-heap or performance claim; successful retained calls are explicit only.',
            'Reviewed source semantics fix remains unapplied; current342/four frozen pins/producer are unchanged.'],
        'verifiedFiles': sorted(checked.values(), key=lambda row: row['path'])}
    with (HERE / 'results.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({key: result[key] for key in ['state', 'sourceInputsRehashed', 'observationsPerCall', 'actualNodeGapIds']}))


if __name__ == '__main__':
    main()
