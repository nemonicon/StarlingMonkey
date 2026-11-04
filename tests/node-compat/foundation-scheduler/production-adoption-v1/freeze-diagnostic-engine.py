"""Freeze one real Release diagnostic build; this helper does not run guests.

Run the separate diagnostic preflight before and after freezing. Original build
paths remain in the byte-identical sidecar as provenance, not current paths.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(path, expected):
    assert path.is_file() and not path.is_symlink(), path
    assert sha(path) == expected, path
    return path


def copy_exact(original, target, expected, shared=False):
    checked(original, expected)
    target.parent.mkdir(parents=True, exist_ok=True)
    assert not target.is_symlink(), target
    if target.exists():
        assert shared, 'Never overwrite a frozen variant: ' + str(target)
        checked(target, expected)
    else:
        shutil.copyfile(original, target)
        checked(target, expected)


engine = Path(sys.argv[1]).resolve(strict=True)
label = sys.argv[2]
assert label in ['diagnostic-release', 'diagnostic-gc']
root = Path(__file__).resolve().parents[4]
output = Path('/tmp/starling-node-compat/foundation-scheduler-v1/native-freeze')
assert not output.is_symlink()
packet = root / 'tests/node-compat/foundation-scheduler/diagnostic-candidate-v1'
pins = json.loads((packet / 'pins.json').read_bytes())
policy = json.loads((packet.parent / 'integration-candidate-v1/policy.json').read_bytes())
metadata_path = Path(str(engine) + '.build.json')
metadata = json.loads(metadata_path.read_bytes())
assert metadata['diagnosticOnly'] is True
assert metadata['internalTicksEnabled'] is True
assert metadata['gcStress'] == (label == 'diagnostic-gc')
assert metadata['entropyPolicy'] == 'off'
assert metadata['oomTesting'] is False and metadata['debuggerEnabled'] is False
assert metadata['wptSupportEnabled'] is False
assert metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE'] == 'Release'
assert metadata['observedCMakeOptions']['WEVAL'] == 'OFF'
assert metadata['observedCMakeOptions']['USE_WASM_OPT'] == 'ON'
assert metadata['observedCMakeOptions']['NODE_COMPAT_INTERNAL_TICKS'] == 'ON'
for key in ['profileEnabled', 'pathEnabled', 'eventsEnabled', 'stringDecoderEnabled',
            'assertEnabled', 'querystringEnabled', 'utilEnabled', 'streamWebEnabled',
            'strictInitialization', 'sourceInputsCapturedBeforeBuild',
            'componentizeSourcesCapturedBeforeBuild', 'buildRecipeCheckedBeforeAndAfterBuild']:
    assert metadata[key] is True, key
assert metadata['generatedRustProject']['cargoBuildLocked'] is True
assert metadata['generatedRustProject']['manifestAndLockCheckedBeforeAndAfterBuild'] is True
assert sha(engine) == metadata['engineSha256']
assert engine.stat().st_size == metadata['engineBytes']
assert metadata['buildRecipeSha256'] == pins['diagnosticRecipeSha256']
recipe = checked(root / 'tests/node-compat/build-diagnostic-engine.sh', pins['diagnosticRecipeSha256'])
assert len(metadata['sourceManifest']) == 306
assert sorted(metadata['sourceManifest'], key=lambda row: row['path']) == sorted(
    policy['expectedNativeSourceManifest'], key=lambda row: row['path'])
diagnostic = metadata['internalTickDiagnosticPolicy']
assert diagnostic['version'] == pins['diagnosticVersion']
assert diagnostic['sourceManifest'] == pins['extraSources']
assert diagnostic['productionSourceInputs'] == 306
assert diagnostic['diagnosticSourceInputs'] == 2
assert diagnostic['totalDeclaredNativeAndBuildInputs'] == 308
assert diagnostic['sourceInputsCheckedBeforeAfter'] is True
assert diagnostic['generatedInstallCheckedBeforeAfter'] is True
declared = metadata['sourceManifest'] + diagnostic['sourceManifest']
assert len({row['path'] for row in declared}) == 308
for row in declared:
    assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
    checked(root / row['path'], row['sha256'])

cache = checked(Path(metadata['cmakeCachePath']), metadata['cmakeCacheSha256'])
commands = checked(Path(metadata['compileCommandsPath']), metadata['compileCommandsSha256'])
cache_values = {}
for line in cache.read_text().splitlines():
    key, colon, rest = line.partition(':')
    if colon and '=' in rest:
        cache_values[key] = rest.partition('=')[2]
external = Path(cache_values['CMAKE_HOME_DIRECTORY'])
assert len(metadata['componentizeSourceManifest']) == 3
for row in metadata['componentizeSourceManifest']:
    checked(external / row['path'], row['sha256'])
assert next(row['sha256'] for row in metadata['componentizeSourceManifest']
            if row['path'] == 'embedding/embedding.cpp') == policy['embedding']['afterSha256']

database = json.loads(commands.read_bytes())
cpp = [row['path'] for row in declared if row['path'].endswith('.cpp') and
       row['path'].startswith(('builtins/', 'runtime/'))]
layout = [row['command'] for row in database if any(row['file'].endswith('/' + path) for path in cpp)]
assert len(layout) == 61
tick = metadata['internalTickPolicy']
assert layout == tick['actualLayoutCompileCommands']
assert layout == metadata['protectedAbortListenerPolicy']['actualLayoutCompileCommands']
assert len(tick['actualQueueCompileCommands']) == 1
assert len(tick['actualEmbeddingCompileCommands']) == 1
assert len(diagnostic['actualCompileCommands']) == 1
assert metadata['actualEmbeddingCompileCommands'] == tick['actualEmbeddingCompileCommands']
for command in layout + tick['actualEmbeddingCompileCommands'] + diagnostic['actualCompileCommands']:
    tokens = command.split()
    assert '-c' in tokens and '-fsyntax-only' not in tokens and '-DDEBUG' not in tokens
    for flag in ['NODE_COMPAT_INTERNAL_TICKS', 'NODE_COMPAT_STRICT_INITIALIZATION',
                 'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER']:
        assert '-D' + flag + '=1' in tokens
install = diagnostic['generatedBuiltinInclude']
install_path = checked(Path(install['path']), install['sha256'])
assert install_path.read_text() == install['contents']
assert install['contents'].splitlines().count('NS_DEF(diagnostics::internal_ticks)') == 1

dependencies = [
    ('openssl-before.json', metadata['openssl']['completeSourceAudit']['beforeReportPath'],
     metadata['openssl']['completeSourceAudit']['beforeReportSha256']),
    ('openssl-receipt.txt', metadata['openssl']['receiptPath'], metadata['openssl']['receiptSha256']),
    ('Cargo.toml', metadata['generatedRustProject']['manifestPath'], metadata['generatedRustProject']['manifestSha256']),
    ('Cargo.lock', metadata['generatedRustProject']['lockPath'], metadata['generatedRustProject']['lockSha256']),
]
assert metadata['openssl']['completeSourceAudit']['sourceFilesVerified'] == 4650
assert metadata['openssl']['completeSourceAudit']['beforeAndAfterBuild'] is True
for _, original, expected in dependencies:
    checked(Path(original), expected)

# Prevalidate all variant destinations before copying. A failed/partial freeze
# is preserved for review and must use a new output namespace for a retry.
targets = [(engine, output / (label + '.engine.wasm'), metadata['engineSha256']),
           (metadata_path, output / (label + '.engine.wasm.build.json'), sha(metadata_path)),
           (cache, output / (label + '-CMakeCache.txt'), sha(cache)),
           (commands, output / (label + '-compile_commands.json'), sha(commands)),
           (install_path, output / (label + '-builtins.incl'), sha(install_path))]
targets += [(Path(original), output / (label + '-' + name), expected)
            for name, original, expected in dependencies]
receipt = output / (label + '-freeze-receipt.json')
assert not receipt.exists()
assert all(not target.exists() and not target.is_symlink() for _, target, _ in targets)
for original, target, expected in targets:
    copy_exact(original, target, expected)
for row in declared:
    copy_exact(root / row['path'], output / 'source' / row['path'], row['sha256'], shared=True)
for row in metadata['componentizeSourceManifest']:
    copy_exact(external / row['path'], output / 'componentize-source' / row['path'], row['sha256'], shared=True)
copy_exact(recipe, output / 'build-diagnostic-engine.sh', pins['diagnosticRecipeSha256'], shared=True)
copy_exact(packet / 'pins.json', output / 'diagnostic-pins.json', sha(packet / 'pins.json'), shared=True)
licenses = []
for original in sorted((root / 'builtins/node-compat').rglob('*')):
    if original.is_file() and original.name.startswith(('LICENSE', 'NOTICE')):
        path = str(original.relative_to(root))
        copy_exact(original, output / 'source' / path, sha(original), shared=True)
        licenses.append({'path': path, 'sha256': sha(original)})
report = {'schemaVersion': 1, 'state': 'immutable-diagnostic-release-build-frozen-not-runtime-proof',
          'label': label, 'engine': str(targets[0][1]), 'engineSha256': metadata['engineSha256'],
          'engineBytes': metadata['engineBytes'], 'metadataSha256': sha(metadata_path),
          'sourceRoot': str(output / 'source'), 'sourcePartitions': [306, 2],
          'externalEmbeddingInputs': 3, 'actualLayoutCompileCommands': len(layout),
          'actualEmbeddingCompileCommands': 1, 'actualDiagnosticCompileCommands': 1,
          'recipeSha256': pins['diagnosticRecipeSha256'], 'helperSha256': sha(Path(__file__)),
          'licenses': licenses, 'copies': [{'path': str(target), 'original': str(original), 'sha256': expected}
                                         for original, target, expected in targets],
          'originalEnginePreserved': True, 'guestExecutedByHelper': False,
          'resetSafeReuse': 'OPEN; cancellation and teardown not established'}
receipt.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
