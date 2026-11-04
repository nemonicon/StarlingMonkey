"""Freeze a completed v10 Release engine and its actual source/config/license evidence."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

engine = Path(sys.argv[1]).resolve()
label = sys.argv[2]
assert label in ['events-off-control', 'off-foundations', 'runtime-foundations', 'gc-foundations']
root = Path(__file__).resolve().parents[4]
output = Path('/tmp/starling-node-compat/foundations-v10/native-freeze')
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
assert metadata['strictEventExceptionPolicy']['version'] == 'sm-uncaught-event-v3-protected-abort-v2'
assert metadata['protectedAbortListenerEnabled'] == metadata['eventsEnabled']
assert metadata['protectedAbortListenerPolicy']['patchSha256'] == '0d314f14e1eba2ed5ff1eed592697d5f6fab2be37d9568281ffec43864e2c3a1'
for command in metadata['protectedAbortListenerPolicy']['actualLayoutCompileCommands'] + metadata['protectedAbortListenerPolicy']['actualEmbeddingCompileCommands']:
    assert ('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1' in command.split()) == metadata['eventsEnabled']

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
commands = Path(metadata['compileCommandsPath']).read_bytes()
assert digest(cache) == metadata['cmakeCacheSha256']
assert digest(commands) == metadata['compileCommandsSha256']
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
          'originalEngine': str(engine), 'originalReceiptPreserved': True}
(output / (label + '-freeze-receipt.json')).write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
