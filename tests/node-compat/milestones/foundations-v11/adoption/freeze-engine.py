"""Freeze a completed v11 Release engine and its actual source/config/license evidence."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

engine = Path(sys.argv[1]).resolve()
label = sys.argv[2]
assert label in ['off-foundations', 'runtime-foundations', 'gc-foundations']
root = Path(__file__).resolve().parents[4]
output = Path('/tmp/starling-node-compat/foundations-v11/native-freeze')
output.mkdir(parents=True, exist_ok=True)
digest = lambda data: hashlib.sha256(data).hexdigest()
metadata_bytes = Path(str(engine) + '.build.json').read_bytes()
metadata = json.loads(metadata_bytes)
assert digest(engine.read_bytes()) == metadata['engineSha256']
assert metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE'] == 'Release'
assert metadata['oomTesting'] is False and metadata['gcStress'] == (label == 'gc-foundations')
assert metadata['sourceInputsCapturedBeforeBuild'] and metadata['buildRecipeCheckedBeforeAndAfterBuild']
assert len(metadata['sourceManifest']) == 304
assert metadata['buildRecipeSha256'] == '354cbc8c5317bf14f022fd14a9687e382b99c2141135629b56bb541ef6308754'
assert metadata['entropyPolicy'] == ('runtime-only' if label == 'runtime-foundations' else 'off')
assert metadata['eventsEnabled'] and metadata['protectedAbortListenerEnabled']
assert metadata['generatedRustProject']['cargoBuildLocked']
assert metadata['componentizeSourcesCapturedBeforeBuild']
assert metadata['observedCMakeOptions']['WEVAL'] == 'OFF'
assert metadata['observedCMakeOptions']['USE_WASM_OPT'] == 'ON'
for name in ['profileEnabled', 'pathEnabled', 'stringDecoderEnabled', 'assertEnabled', 'querystringEnabled', 'utilEnabled', 'streamWebEnabled', 'strictInitialization']:
    assert metadata[name] is True, name
assert not metadata['debuggerEnabled'] and not metadata['wptSupportEnabled']
assert len(metadata['componentizeSourceManifest']) == 3
assert metadata['strictEventExceptionPolicy']['version'] == 'sm-uncaught-event-v3-protected-abort-v2'
assert metadata['protectedAbortListenerEnabled'] == metadata['eventsEnabled']
assert metadata['protectedAbortListenerPolicy']['patchSha256'] == '0d314f14e1eba2ed5ff1eed592697d5f6fab2be37d9568281ffec43864e2c3a1'
for command in metadata['protectedAbortListenerPolicy']['actualLayoutCompileCommands'] + metadata['protectedAbortListenerPolicy']['actualEmbeddingCompileCommands']:
    assert ('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1' in command.split()) == metadata['eventsEnabled']

packet = root / 'tests/node-compat/foundation-alloc-unsafe/production-candidate-m0.11-v2/source-receipt.json'
proposal = json.loads(packet.read_text())
expected = {entry['path']: entry['sha256'] for entry in proposal['ancestry']}
changed_native = [entry for entry in proposal['changes'] if entry['path'] in expected]
assert len(changed_native) == 4
for entry in changed_native:
    assert expected[entry['path']] == entry['before']
    expected[entry['path']] = entry['after']
assert {entry['path']: entry['sha256'] for entry in metadata['sourceManifest']} == expected
core = next(entry for entry in metadata['selectedModuleManifests'] if entry['path'] == 'builtins/node-compat/export-manifest.node-v22.14.0.json')
assert core['profileVersion'] == 'sm-node-22.14.0-m0.11'
assert len(metadata['selectedModuleManifests']) == 8
source = output / 'source'
source.mkdir(exist_ok=True)
for entry in metadata['sourceManifest']:
    original = root / entry['path']
    assert digest(original.read_bytes()) == entry['sha256'], entry['path']
    target = source / entry['path']
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert digest(target.read_bytes()) == entry['sha256'], 'Mixed native freeze: ' + entry['path']
    else:
        shutil.copyfile(original, target)
recipe = root / 'tests/node-compat/build-engine.sh'
assert digest(recipe.read_bytes()) == metadata['buildRecipeSha256']
for original, target in [(recipe, output / 'build-engine.sh'),
                         (root / 'tests/node-compat/provenance/openssl-source-audit.py', output / 'openssl-source-audit.py')]:
    if target.exists():
        assert target.read_bytes() == original.read_bytes()
    else:
        shutil.copyfile(original, target)
licenses = []
for original in sorted((root / 'builtins/node-compat').rglob('*')):
    if original.is_file() and (original.name.startswith('LICENSE') or original.name.startswith('NOTICE')):
        target = source / original.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert target.read_bytes() == original.read_bytes()
        else:
            shutil.copyfile(original, target)
        licenses.append({'path': str(original.relative_to(root)), 'sha256': digest(original.read_bytes())})
build = Path(metadata['cmakeCachePath']).parent
cache = Path(metadata['cmakeCachePath']).read_bytes()
commands = Path(metadata.get('compileCommandsPath', build / 'compile_commands.json')).read_bytes()
assert digest(cache) == metadata['cmakeCacheSha256']
assert digest(commands) == metadata['compileCommandsSha256']
compile_database = json.loads(commands)
cpp_paths = [entry['path'] for entry in metadata['sourceManifest'] if entry['path'].endswith('.cpp') and entry['path'].startswith(('builtins/', 'runtime/'))]
layout = [entry['command'] for entry in compile_database if any(entry['file'].endswith('/' + path) for path in cpp_paths)]
assert len(layout) == 60 and layout == metadata['protectedAbortListenerPolicy']['actualLayoutCompileCommands']
assert len(metadata['actualEmbeddingCompileCommands']) == 1
assert metadata['actualEmbeddingCompileCommands'] == metadata['protectedAbortListenerPolicy']['actualEmbeddingCompileCommands']
assert all('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1' in command.split() for command in layout + metadata['actualEmbeddingCompileCommands'])
assert all('-DNODE_COMPAT_STRICT_INITIALIZATION=1' in command.split() for command in metadata['strictEventExceptionPolicy']['actualNativeCompileCommands'] + metadata['actualEmbeddingCompileCommands'])
cache_values = {}
for line in cache.decode().splitlines():
    if ':' in line and '=' in line.partition(':')[2]:
        key, _, encoded = line.partition(':')
        cache_values[key] = encoded.partition('=')[2]
external = Path(cache_values['CMAKE_HOME_DIRECTORY'])
for entry in metadata['componentizeSourceManifest']:
    original = external / entry['path']
    assert digest(original.read_bytes()) == entry['sha256'], entry['path']
    target = output / 'componentize-source' / entry['path']
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert digest(target.read_bytes()) == entry['sha256']
    else:
        shutil.copyfile(original, target)
dependency_copies = []
for name, original, expected_sha in [
    ('openssl-before.json', Path(metadata['openssl']['completeSourceAudit']['beforeReportPath']), metadata['openssl']['completeSourceAudit']['beforeReportSha256']),
    ('openssl-receipt.txt', Path(metadata['openssl']['receiptPath']), metadata['openssl']['receiptSha256']),
    ('Cargo.toml', Path(metadata['generatedRustProject']['manifestPath']), metadata['generatedRustProject']['manifestSha256']),
    ('Cargo.lock', Path(metadata['generatedRustProject']['lockPath']), metadata['generatedRustProject']['lockSha256']),
]:
    data = original.read_bytes()
    assert digest(data) == expected_sha, original
    target = output / (label + '-' + name)
    assert not target.exists(), target
    target.write_bytes(data)
    dependency_copies.append({'path': str(target), 'original': str(original), 'sha256': expected_sha})
assert metadata['openssl']['completeSourceAudit']['sourceFilesVerified'] == 4650
assert metadata['openssl']['completeSourceAudit']['beforeAndAfterBuild']
target_engine = output / (label + '.engine.wasm')
assert not target_engine.exists() and not Path(str(target_engine) + '.build.json').exists(), 'Never overwrite an immutable engine'
shutil.copyfile(engine, target_engine)
Path(str(target_engine) + '.build.json').write_bytes(metadata_bytes)
(output / (label + '-CMakeCache.txt')).write_bytes(cache)
(output / (label + '-compile_commands.json')).write_bytes(commands)
licenses_path = output / 'licenses.json'
if licenses_path.exists():
    assert json.loads(licenses_path.read_text())['files'] == licenses
else:
    licenses_path.write_text(json.dumps({'scope': 'Copied Node guest-source attribution; OpenSSL and SpiderMonkey archive/source evidence remains in build receipts', 'files': licenses}, indent=2) + '\n')
report = {'schema': 1, 'state': 'immutable-release-engine-frozen', 'label': label,
          'engine': str(target_engine), 'engineSha256': metadata['engineSha256'],
          'engineBytes': metadata['engineBytes'], 'receiptSha256': digest(metadata_bytes),
          'sourceRoot': str(source), 'nativeInputsVerified': len(metadata['sourceManifest']),
          'externalEmbeddingInputsVerified': len(metadata['componentizeSourceManifest']),
          'recipeSha256': metadata['buildRecipeSha256'], 'licenses': len(licenses),
          'streamWebEnabled': metadata['streamWebEnabled'], 'entropyPolicy': metadata['entropyPolicy'],
          'observedCMakeOptions': metadata['observedCMakeOptions'],
          'kernelCompileCommands': metadata['actualStreamWebKernelCompileCommands'],
          'opensslCompleteSourceProof': metadata['openssl'].get('completeSourceAudit'),
          'originalEngine': str(engine), 'originalReceiptPreserved': True,
          'coreVersion': core['profileVersion'], 'nativeChangedFromV10': 4, 'nativeUnchangedFromV10': 300,
          'actualLayoutCompileCommands': len(layout), 'actualEmbeddingCompileCommands': len(metadata['actualEmbeddingCompileCommands']),
          'dependencyEvidenceCopies': dependency_copies, 'helperSha256': digest(Path(__file__).read_bytes())}
(output / (label + '-freeze-receipt.json')).write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
