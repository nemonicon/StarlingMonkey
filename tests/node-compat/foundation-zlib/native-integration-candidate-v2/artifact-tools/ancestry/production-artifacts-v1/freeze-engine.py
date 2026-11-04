"""Freeze one completed production869 variant. main is never run by source tests."""
import sys
sys.dont_write_bytecode = True
import datetime
import importlib.util
import json
from pathlib import Path
import subprocess
from artifact_common import (HERE, REPO, OUTPUT, RECIPE, POLICY, HELPER, EMBEDDING, ADAPTER,
                             classify, checked, sha, digest, manifest, compile_command,
                             embedding_command, validate_plan, execute_plan)

NODE = '/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'

def main():
    assert len(sys.argv) in (3, 4), 'ENGINE normal-off|normal-runtime|gc-off [EXACT_SOURCE_ROOT]'
    original_engine = Path(sys.argv[1]).absolute()
    label = sys.argv[2]
    source_root = Path(sys.argv[3]).resolve(strict=True) if len(sys.argv) == 4 else REPO
    metadata_path = Path(str(original_engine) + '.build.json')
    metadata_bytes = checked(metadata_path, sha(metadata_path)).read_bytes()
    metadata = json.loads(metadata_bytes)
    # No output creation, engine stat/read or Ninja call precedes this gate.
    gc, entropy = classify(metadata, label)
    assert source_root == REPO, 'Only the actual configured repository is supported; no path projection'
    runtime = entropy == 'runtime-only'
    recipe = checked(REPO / 'tests/node-compat/build-engine.sh', RECIPE)
    policy_path = checked(HERE.parent / 'integration-candidate-v1/policy.json', POLICY)
    helper_path = checked(HERE.parent / 'integration-candidate-v1/layer-policy.py', HELPER)
    policy = json.loads(policy_path.read_bytes())
    native = manifest(metadata['sourceManifest'], 306)
    assert sorted(native, key=lambda x: x['path']) == policy['expectedNativeSourceManifest']
    spec = importlib.util.spec_from_file_location('production_artifact_source_policy', helper_path)
    layer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(layer)
    layer.validate_sources(source_root, native)
    # Existing finite selector is actually called. It reads source metadata only.
    admission_command = [NODE, str(HERE / 'metadata-admission.mjs'), str(metadata_path), label, str(source_root)]
    admission_process = subprocess.run(admission_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    admission = json.loads(admission_process.stdout)
    assert admission['state'] == 'ACTUAL_FINITE_SOURCE_SELECTOR_PASSED_NO_ENGINE_EXECUTION'
    assert admission['sourceFiles'] == 306 and admission['engineBytesRead'] is False

    cache_path = checked(Path(metadata['cmakeCachePath']), metadata['cmakeCacheSha256'])
    build = cache_path.parent
    db_path = checked(Path(metadata.get('compileCommandsPath', build / 'compile_commands.json')), metadata['compileCommandsSha256'])
    cache = {}
    for line in cache_path.read_text().splitlines():
        key, colon, rest = line.partition(':')
        if colon and '=' in rest:
            cache[key] = rest.partition('=')[2]
    assert metadata['requestedCMakeOptions'] == metadata['observedCMakeOptions']
    for key, value in metadata['observedCMakeOptions'].items():
        assert cache.get(key) == value, key
    required = {'CMAKE_BUILD_TYPE': 'Release', 'WEVAL': 'OFF', 'USE_WASM_OPT': 'ON',
                'NODE_COMPAT_ENTROPY_MODE': 'RUNTIME_ONLY' if runtime else 'OFF',
                'NODE_COMPAT_INTERNAL_TICKS': 'ON', 'NODE_COMPAT_GC_STRESS': 'ON' if gc else 'OFF',
                'NODE_COMPAT_OOM_TESTING': 'OFF', 'ENABLE_BUILTIN_WPT_SUPPORT': 'OFF',
                'ENABLE_JS_DEBUGGER': 'OFF', 'NODE_COMPAT_LOCKED_RUST': 'ON'}
    for key, value in required.items():
        assert cache.get(key) == value, key
    assert not cache.get('CMAKE_PROJECT_ComponentizeJS_INCLUDE', ''), 'No diagnostic CMake extension'
    assert cache.get('ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS', 'OFF') == 'OFF'
    database = json.loads(db_path.read_bytes())
    cpp = {row['path'] for row in native if row['path'].endswith('.cpp') and row['path'].startswith(('builtins/', 'runtime/'))}
    assert len(cpp) == 61
    rows = [row for row in database if any(row['file'].endswith('/' + name) for name in cpp)]
    assert len(rows) == len({row['file'] for row in rows}) == 61
    layout = [row['command'] for row in rows]
    assert layout == metadata['internalTickPolicy']['actualLayoutCompileCommands']
    assert layout == metadata['protectedAbortListenerPolicy']['actualLayoutCompileCommands']
    queue = [row['command'] for row in rows if row['file'].endswith('/runtime/node_tick_queue.cpp')]
    assert len(queue) == 1 and queue == metadata['internalTickPolicy']['actualQueueCompileCommands']
    strict_paths = ('/runtime/engine.cpp', '/runtime/event_loop.cpp', '/runtime/node_tick_queue.cpp', '/builtins/web/event/event-target.cpp')
    strict = [row['command'] for row in rows if row['file'].endswith(strict_paths)]
    assert len(strict) == 4 and sorted(strict) == sorted(metadata['strictEventExceptionPolicy']['actualNativeCompileCommands'])
    assert not any(row['file'].endswith('/embedding/embedding.cpp') for row in database), 'Parent embedding is not a native JSON row'
    external = Path(cache['CMAKE_HOME_DIRECTORY'])
    external_sources = manifest(metadata['componentizeSourceManifest'], 3)
    assert {row['path'] for row in external_sources} == {'embedding/embedding.cpp', 'embedding/embedding.h', 'CMakeLists.txt'}
    assert next(row['sha256'] for row in external_sources if row['path'] == 'embedding/embedding.cpp') == EMBEDDING
    for row in external_sources:
        checked(external / row['path'], row['sha256'])
    ninja_command = ['ninja', '-C', str(build), '-t', 'commands', 'builtin_componentize_embedding']
    ninja = subprocess.run(ninja_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    embedding = embedding_command(ninja.stdout, str(external / 'embedding/embedding.cpp'))
    assert embedding == metadata['actualEmbeddingCompileCommands']
    assert embedding == metadata['internalTickPolicy']['actualEmbeddingCompileCommands']
    assert embedding == metadata['protectedAbortListenerPolicy']['actualEmbeddingCompileCommands']
    layer.validate_compilation(database, embedding, True, source_root)
    for command in layout + embedding:
        compile_command(command, runtime)
    kernel = [row['command'] for row in rows if row['file'].endswith('/builtins/node-compat/buffer.cpp')]
    assert len(kernel) == 1 and ('-DNODE_COMPAT_GC_STRESS=1' in compile_command(kernel[0], runtime)) is gc
    # Only after actual finite metadata/source/command checks may engine bytes be read.
    engine = checked(original_engine, metadata['engineSha256'])
    assert engine.stat().st_size == metadata['engineBytes']
    with engine.open('rb') as stream:
        assert stream.read(8) == b'\0asm\x01\0\0\0', 'Expected a core Wasm engine artifact'
    audit = metadata['openssl']['completeSourceAudit']
    assert audit['sourceFilesVerified'] == 4650 and audit['beforeAndAfterBuild'] is True
    before_audit = json.loads(checked(Path(audit['beforeReportPath']), audit['beforeReportSha256']).read_bytes())
    assert before_audit['state'] == 'verified-complete-source'
    for key, value in before_audit.items():
        assert audit[key] == value
    rust = metadata['generatedRustProject']
    assert rust['cargoBuildLocked'] is True and rust['manifestAndLockCheckedBeforeAndAfterBuild'] is True
    lock = checked(Path(rust['lockPath']), rust['lockSha256'])
    assert sha(lock) == sha(source_root / 'runtime/crates/staticlib-template/Cargo.lock')
    library = metadata['openssl']['library']
    checked(Path(library['path']), library['sha256'])
    assert Path(library['path']).stat().st_size == library['bytes']
    adapter = checked(REPO / 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm', ADAPTER)
    assert adapter.stat().st_size == 53512
    dependencies = [
        ('openssl-before.json', audit['beforeReportPath'], audit['beforeReportSha256']),
        ('openssl-receipt.txt', metadata['openssl']['receiptPath'], metadata['openssl']['receiptSha256']),
        ('openssl-configure.txt', metadata['openssl']['configureRecipe']['path'], metadata['openssl']['configureRecipe']['sha256']),
        ('openssl-configdata.pm', metadata['openssl']['configdata']['path'], metadata['openssl']['configdata']['sha256']),
        ('Cargo.toml', rust['manifestPath'], rust['manifestSha256']), ('Cargo.lock', rust['lockPath'], rust['lockSha256']),
    ]
    plan = []
    def add(original, name, expected, shared=False):
        path = checked(Path(original), expected)
        plan.append({'original': path, 'target': OUTPUT / name, 'sha256': expected, 'shared': shared})
    def generated(data, name):
        plan.append({'original': None, 'data': data, 'target': OUTPUT / name, 'sha256': digest(data), 'shared': False})
    add(engine, label + '.engine.wasm', metadata['engineSha256'])
    add(metadata_path, label + '.engine.wasm.build.json', digest(metadata_bytes))
    add(cache_path, label + '-CMakeCache.txt', metadata['cmakeCacheSha256'])
    add(db_path, label + '-compile_commands.json', metadata['compileCommandsSha256'])
    generated(ninja.stdout, label + '-embedding.after.commands.txt')
    generated(admission_process.stdout, label + '-source-admission.json')
    for name, original, expected in dependencies:
        add(original, label + '-' + name, expected)
    for row in native:
        add(source_root / row['path'], 'source/' + row['path'], row['sha256'], True)
    for row in external_sources:
        add(external / row['path'], 'componentize-source/' + row['path'], row['sha256'], True)
    add(recipe, 'build-engine.sh', RECIPE, True)
    add(policy_path, 'source-policy.json', POLICY, True)
    add(helper_path, 'source-policy-helper.py', HELPER, True)
    add(adapter, 'tooling/wasi_snapshot_preview1.wasm', ADAPTER, True)
    licenses = []
    for original in sorted((source_root / 'builtins/node-compat').rglob('*')):
        if original.is_file() and original.name.startswith(('LICENSE', 'NOTICE')):
            name = str(original.relative_to(source_root))
            add(original, 'source/' + name, sha(original), True)
            licenses.append({'path': name, 'sha256': sha(original)})
    for name in ['freeze-engine.py', 'artifact_common.py', 'metadata-admission.mjs']:
        add(HERE / name, 'artifact-tools/' + name, sha(HERE / name), True)
    receipt_path = OUTPUT / (label + '-freeze-receipt.json')
    validate_plan(plan, receipt_path)  # ALL inputs/destinations checked before any copy.
    execute_plan(plan)
    receipt = {'schema': 1, 'state': 'immutable-release-engine-frozen', 'label': label,
        'engine': str(OUTPUT / (label + '.engine.wasm')), 'engineSha256': metadata['engineSha256'],
        'engineBytes': metadata['engineBytes'], 'receiptSha256': digest(metadata_bytes),
        'sourceRoot': str(OUTPUT / 'source'), 'componentizeSourceRoot': str(OUTPUT / 'componentize-source'),
        'nativeInputsVerified': 306, 'externalEmbeddingInputsVerified': 3, 'recipeSha256': RECIPE,
        'actualLayoutCompileCommands': 61, 'actualStrictCompileCommands': 4, 'actualEmbeddingCompileCommands': 1,
        'entropyPolicy': entropy, 'gcStress': gc, 'coreVersion': admission['coreExpectations']['coreVersion'],
        'coreSources': admission['coreExpectations']['sourceHashes'], 'licenses': licenses,
        'observedCMakeOptions': metadata['observedCMakeOptions'], 'originalEngine': str(engine),
        'originalMetadataPath': str(metadata_path), 'originalReceiptPreserved': True,
        'postBuildEmbeddingEvidence': {'version': 'production-after-build-parent-ninja-v1',
            'command': ninja_command, 'exitCode': ninja.returncode, 'stderr': ninja.stderr.decode(),
            'path': str(OUTPUT / (label + '-embedding.after.commands.txt')), 'sha256': digest(ninja.stdout),
            'bytes': len(ninja.stdout), 'sourcePath': str(external / 'embedding/embedding.cpp'),
            'compileCommands': embedding, 'beforeBuildCaptureExists': False},
        'sourceAdmission': {'path': str(OUTPUT / (label + '-source-admission.json')), 'sha256': digest(admission_process.stdout), 'command': admission_command},
        'toolingInputs': [{'role': 'live-preview1-adapter-copy', 'original': str(adapter),
            'path': str(OUTPUT / 'tooling/wasi_snapshot_preview1.wasm'), 'sha256': ADAPTER, 'bytes': 53512,
            'additionalNativeInput': False, 'doesNotReplaceLiveRuntimeSeal': True}],
        'copies': [{'path': str(row['target']), 'original': str(row['original']) if row['original'] else None,
                    'sha256': row['sha256'], 'bytes': row['target'].stat().st_size, 'shared': row['shared']} for row in plan],
        'dependencyReferences': [{'kind': 'linked-libcrypto-not-copied', **library}],
        'allInputsValidatedBeforeCopies': True, 'allCopiesAndOriginalsRehashed': True,
        'partialOutputOnFailure': 'Preserved; no receipt or pin export implies acceptance',
        'helperSha256': sha(Path(__file__)), 'guestExecutedByHelper': False}
    with receipt_path.open('x') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'receiptPath': str(receipt_path), 'receipt': receipt}))

if __name__ == '__main__':
    main()
