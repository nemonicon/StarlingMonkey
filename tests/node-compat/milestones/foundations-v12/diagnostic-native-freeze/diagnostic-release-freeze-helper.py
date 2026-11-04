"""Freeze a link1 diagnostic build; never compile or execute a guest.

Parent-project targets are authenticated from actual Ninja command stdout, not
invented compile-database rows. Run validateDiagnosticMetadata before freezing;
run the full diagnosticPreflight after the immutable snapshot exists.
Any partial output is preserved and must not be overwritten on retry.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import shutil
import sys


EVIDENCE_VERSION = 'ninja-parent-target-commands-before-after-v2'
EVIDENCE_SELECTION = 'exact -c source operand; shlex parsing; no shell evaluation'
OUTPUT = Path('/tmp/starling-node-compat/foundation-scheduler-link1-v1/native-freeze')
CONSUMER_PINS_SHA256 = 'd56e14625e6bff5ed586450e3ebf828ae45ac175c2a6658a35ca4c4b638d54d1'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def checked(path, expected):
    assert isinstance(expected, str) and re.fullmatch(r'[0-9a-f]{64}', expected)
    assert path.is_file() and not path.is_symlink(), path
    assert sha(path) == expected, path
    return path


def manifest(value, count):
    assert isinstance(value, list) and len(value) == count
    seen = set()
    for row in value:
        assert set(row) == {'path', 'sha256'}
        name = row['path']
        assert isinstance(name, str) and name and '\0' not in name
        assert not Path(name).is_absolute()
        assert all(part not in ('', '.', '..') for part in name.split('/'))
        assert name not in seen
        seen.add(name)
        assert re.fullmatch(r'[0-9a-f]{64}', row['sha256'])
    return value


def compiler_commands(text, source):
    selected = []
    for line in text.splitlines():
        if ' -c ' not in line:
            continue
        words = shlex.split(line)
        if '-c' not in words:
            continue
        assert words.count('-c') == 1
        index = words.index('-c')
        assert index + 1 < len(words)
        if words[index + 1] == source:
            selected.append(line)
    assert len(selected) == 1, (source, len(selected))
    return selected


def validate_command(command):
    words = shlex.split(command)
    assert '-c' in words and '-fsyntax-only' not in words
    assert '-DNDEBUG' in words and '-DDEBUG' not in words
    for flag in ('NODE_COMPAT_INTERNAL_TICKS', 'NODE_COMPAT_STRICT_INITIALIZATION',
                 'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER', 'NODE_COMPAT_ENTROPY_POLICY'):
        assert '-D' + flag + '=1' in words
    assert '-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1' not in words


def destination(path):
    assert path.is_relative_to(OUTPUT)
    cursor = path
    while cursor != OUTPUT.parent:
        assert not cursor.is_symlink(), cursor
        cursor = cursor.parent


def copy_exact(original, target, expected, shared):
    checked(original, expected)
    destination(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert shared, 'Never overwrite a frozen variant: ' + str(target)
        checked(target, expected)
    else:
        # Exclusive creation also refuses an unexpected concurrent destination.
        with original.open('rb') as source, target.open('xb') as output:
            shutil.copyfileobj(source, output, 1024 * 1024)
        checked(target, expected)
    checked(original, expected)


def validate_link1(metadata, root, consumer_pins):
    """Read all four real witnesses and revalidate pinned tools; execute no job."""
    packet = root / 'tests/node-compat/foundation-scheduler/diagnostic-producer-v3-link1'
    helper_path = checked(packet / 'link-policy.py', consumer_pins['linkHelperSha256'])
    policy_path = checked(packet / 'policy.json', consumer_pins['linkPolicySha256'])
    policy = json.loads(policy_path.read_bytes())
    link = metadata['linkerConcurrencyPolicy']
    assert link['version'] == consumer_pins['linkPolicyVersion']
    assert link['policyPath'] == str(policy_path) and link['helperPath'] == str(helper_path)
    assert link['policySha256'] == consumer_pins['linkPolicySha256']
    assert link['helperSha256'] == consumer_pins['linkHelperSha256']
    assert link['parentDiagnosticRecipeSha256'] == consumer_pins['parentDiagnosticRecipeSha256']
    assert link['parentProductionRecipeSha256'] == consumer_pins['parentProductionRecipeSha256']
    assert link['productionSourceInputs'] == 306 and link['diagnosticSourceInputs'] == 2
    assert link['nativeOrSdkSourceChanges'] is False and link['resourceBenefitMeasured'] is False
    assert link['requiredLauncherGates'] == policy['launchGates']
    assert link['requestedCMake'] == link['observedCMake'] == policy['requestedCMakeOptions']
    for key, value in policy['requestedCMakeOptions'].items():
        assert metadata['requestedCMakeOptions'][key] == metadata['observedCMakeOptions'][key] == value
    evidence = link['finalLinkCommandEvidence']
    assert evidence['version'] == consumer_pins['finalLinkEvidenceVersion']
    build = evidence['buildDirectory']
    assert evidence['collectionCommand'] == ['ninja', '-C', build, '-t', 'commands', policy['target']]
    assert Path(build).resolve() == Path(metadata['cmakeCachePath']).parent.resolve()
    assert Path(build).resolve() == Path(metadata['compileCommandsPath']).parent.resolve()
    assert evidence['exactRawBytesUnchanged'] is True and evidence['exactValidationBytesUnchanged'] is True
    rows = {}
    for key in ('before', 'after', 'validationBefore', 'validationAfter'):
        row = evidence[key]
        assert set(row) == {'path', 'sha256', 'bytes'}
        assert Path(row['path']).is_absolute()
        path = checked(Path(row['path']), row['sha256'])
        assert path.stat().st_size == row['bytes']
        rows[key] = path
    assert len({path.resolve() for path in rows.values()}) == 4
    assert rows['before'].read_bytes() == rows['after'].read_bytes()
    assert rows['validationBefore'].read_bytes() == rows['validationAfter'].read_bytes()
    validated = json.loads(rows['validationAfter'].read_bytes())
    assert validated == evidence['validated']
    assert validated['forwardedLldArgumentsAreContractOnly'] is True
    assert validated['spawnedLldArgumentsObserved'] is False and validated['threadCountsObserved'] is False
    # The producer helper is pinned source and its validate entry point only
    # reads command data, wrapper, aliases and SDK files. It has no subprocess.
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('frozen_link1_source_policy', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    work = str(Path(metadata['enginePath']).parent.parent)
    assert helper.validate(rows['before'], build, work, str(root)) == validated
    assert helper.validate(rows['after'], build, work, str(root)) == validated
    assert sha(helper_path) == consumer_pins['linkHelperSha256']
    assert sha(policy_path) == consumer_pins['linkPolicySha256']
    wrapper = checked(Path(validated['wrapper']['path']), validated['wrapper']['sha256'])
    files = [(name, rows[key], evidence[key]['sha256']) for key, name in (
        ('before', 'final-link.before.commands.txt'), ('after', 'final-link.after.commands.txt'),
        ('validationBefore', 'final-link.before.validation.json'),
        ('validationAfter', 'final-link.after.validation.json'))]
    return files, wrapper


def main():
    assert len(sys.argv) == 3, 'ENGINE diagnostic-release|diagnostic-gc'
    original_engine = Path(sys.argv[1]).absolute()
    assert not original_engine.is_symlink()
    engine = original_engine.resolve(strict=True)
    label = sys.argv[2]
    assert label in ('diagnostic-release', 'diagnostic-gc')
    root = Path(__file__).resolve().parents[4]
    packet = root / 'tests/node-compat/foundation-scheduler/diagnostic-producer-v3-link1'
    consumer = Path(__file__).resolve().parent
    consumer_pins_path = checked(consumer / 'consumer-pins.json', CONSUMER_PINS_SHA256)
    consumer_pins = json.loads(consumer_pins_path.read_bytes())
    pins_path = packet / 'pins.json'
    pins = json.loads(checked(pins_path, consumer_pins['producerPinsSha256']).read_bytes())
    assert pins['diagnosticRecipeSha256'] == consumer_pins['diagnosticRecipeSha256']
    policy_path = root / 'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json'
    policy = json.loads(checked(policy_path, pins['productionPolicySha256']).read_bytes())
    metadata_path = Path(str(engine) + '.build.json')
    metadata_digest = sha(metadata_path)
    metadata = json.loads(checked(metadata_path, metadata_digest).read_bytes())
    assert metadata['diagnosticOnly'] is True and metadata['internalTicksEnabled'] is True
    assert metadata['gcStress'] is (label == 'diagnostic-gc')
    assert metadata['entropyPolicy'] == 'off'
    assert metadata['oomTesting'] is False and metadata['debuggerEnabled'] is False
    assert metadata['wptSupportEnabled'] is False
    for key in ('profileEnabled', 'pathEnabled', 'eventsEnabled', 'stringDecoderEnabled',
                'assertEnabled', 'querystringEnabled', 'utilEnabled', 'streamWebEnabled',
                'strictInitialization', 'sourceInputsCapturedBeforeBuild',
                'componentizeSourcesCapturedBeforeBuild', 'buildRecipeCheckedBeforeAndAfterBuild'):
        assert metadata[key] is True, key
    assert metadata['generatedRustProject']['cargoBuildLocked'] is True
    assert metadata['generatedRustProject']['manifestAndLockCheckedBeforeAndAfterBuild'] is True
    checked(engine, metadata['engineSha256'])
    assert engine.stat().st_size == metadata['engineBytes']
    assert metadata['buildRecipeSha256'] == pins['diagnosticRecipeSha256']
    recipe = checked(root / 'tests/node-compat/build-diagnostic-engine.sh', pins['diagnosticRecipeSha256'])

    production = manifest(metadata['sourceManifest'], 306)
    assert sorted(production, key=lambda row: row['path']) == sorted(
        manifest(policy['expectedNativeSourceManifest'], 306), key=lambda row: row['path'])
    diagnostic = metadata['internalTickDiagnosticPolicy']
    assert diagnostic['version'] == pins['diagnosticVersion']
    assert manifest(diagnostic['sourceManifest'], 2) == manifest(pins['extraSources'], 2)
    assert diagnostic['productionSourceInputs'] == 306 and diagnostic['diagnosticSourceInputs'] == 2
    assert diagnostic['totalDeclaredNativeAndBuildInputs'] == 308
    assert diagnostic['sourceInputsCheckedBeforeAfter'] is True
    assert diagnostic['generatedInstallCheckedBeforeAfter'] is True
    assert diagnostic['testModuleIds'] == pins['testModuleIds']
    declared = production + diagnostic['sourceManifest']
    assert len({row['path'] for row in declared}) == 308
    for row in declared:
        checked(root / row['path'], row['sha256'])

    cache = checked(Path(metadata['cmakeCachePath']), metadata['cmakeCacheSha256'])
    commands = checked(Path(metadata['compileCommandsPath']), metadata['compileCommandsSha256'])
    cache_values = {}
    for line in cache.read_text().splitlines():
        key, colon, rest = line.partition(':')
        if colon and '=' in rest:
            cache_values[key] = rest.partition('=')[2]
    assert metadata['requestedCMakeOptions'] == metadata['observedCMakeOptions']
    for key, value in metadata['observedCMakeOptions'].items():
        assert cache_values.get(key) == value, key
    for key, value in {'CMAKE_BUILD_TYPE': 'Release', 'WEVAL': 'OFF', 'USE_WASM_OPT': 'ON',
                       'NODE_COMPAT_INTERNAL_TICKS': 'ON', 'NODE_COMPAT_OOM_TESTING': 'OFF',
                       'ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS': 'ON'}.items():
        assert cache_values.get(key) == value, key
    assert cache_values['NODE_COMPAT_GC_STRESS'] == ('ON' if metadata['gcStress'] else 'OFF')
    external = Path(cache_values['CMAKE_HOME_DIRECTORY'])
    embedding_sources = manifest(metadata['componentizeSourceManifest'], 3)
    assert {row['path'] for row in embedding_sources} == {
        'CMakeLists.txt', 'embedding/embedding.cpp', 'embedding/embedding.h'}
    for row in embedding_sources:
        checked(external / row['path'], row['sha256'])
    assert next(row['sha256'] for row in embedding_sources if row['path'] ==
                'embedding/embedding.cpp') == policy['embedding']['afterSha256']

    database = json.loads(commands.read_bytes())
    cpp = [row['path'] for row in production if row['path'].endswith('.cpp') and
           row['path'].startswith(('builtins/', 'runtime/'))]
    assert len(cpp) == 61
    cpp_paths = {str((root / path).resolve()) for path in cpp}
    layout_rows = [row for row in database if str(Path(row['file']).resolve()) in cpp_paths]
    assert len(layout_rows) == 61 and len({row['file'] for row in layout_rows}) == 61
    layout = [row['command'] for row in layout_rows]
    tick = metadata['internalTickPolicy']
    assert layout == tick['actualLayoutCompileCommands']
    assert layout == metadata['protectedAbortListenerPolicy']['actualLayoutCompileCommands']
    queue_commands = [row['command'] for row in layout_rows
                      if Path(row['file']).name == 'node_tick_queue.cpp']
    assert len(queue_commands) == 1 and queue_commands == tick['actualQueueCompileCommands']

    # Parent-project targets are absent from this directory-local database.
    # Authenticate the complete real Ninja stdout, then derive exact -c operands.
    evidence = diagnostic['parentTargetCommandEvidence']
    assert evidence['version'] == EVIDENCE_VERSION
    assert evidence['selection'] == EVIDENCE_SELECTION
    assert evidence['exactBytesUnchanged'] is True
    build_directory = evidence['buildDirectory']
    assert Path(build_directory).resolve() == cache.parent.resolve()
    assert evidence['collectionCommand'] == ['ninja', '-C', build_directory, '-t', 'commands',
                                             'builtin_componentize_embedding',
                                             'builtin_diagnostics_internal_ticks']
    configuration = evidence['configuration']
    assert set(configuration) == {'cmakeCache', 'compileCommands'}
    configuration_before = {}
    for key, actual_path, actual_digest in (
            ('cmakeCache', cache, metadata['cmakeCacheSha256']),
            ('compileCommands', commands, metadata['compileCommandsSha256'])):
        snapshot = configuration[key]
        assert snapshot['exactBytesUnchanged'] is True
        values = {}
        for phase in ('before', 'after'):
            row = snapshot[phase]
            assert set(row) == {'path', 'sha256', 'bytes'}
            path = checked(Path(row['path']), row['sha256'])
            values[phase] = path.read_bytes()
            assert len(values[phase]) == row['bytes']
            if phase == 'before':
                configuration_before[key] = (path, row['sha256'])
            else:
                assert path.resolve() == actual_path.resolve()
                assert row['sha256'] == actual_digest
        assert values['before'] == values['after']
        assert Path(snapshot['before']['path']).resolve() != actual_path.resolve()
    raw_paths = {}
    raw_bytes = {}
    for phase in ('before', 'after'):
        row = evidence[phase]
        assert set(row) == {'path', 'sha256', 'bytes'}
        path = checked(Path(row['path']), row['sha256'])
        raw_paths[phase] = path
        raw_bytes[phase] = path.read_bytes()
        assert len(raw_bytes[phase]) == row['bytes']
    assert raw_paths['before'].resolve() != raw_paths['after'].resolve()
    assert raw_bytes['before'] == raw_bytes['after']
    text = raw_bytes['after'].decode('utf-8')
    targets = evidence['targets']
    assert set(targets) == {'embedding', 'diagnostic'}
    embedding = targets['embedding']
    diagnostic_target = targets['diagnostic']
    assert embedding['target'] == 'builtin_componentize_embedding'
    assert diagnostic_target['target'] == 'builtin_diagnostics_internal_ticks'
    assert Path(embedding['sourcePath']).resolve() == (external / 'embedding/embedding.cpp').resolve()
    assert Path(diagnostic_target['sourcePath']).resolve() == (root / pins['extraSources'][0]['path']).resolve()
    embedding_commands = compiler_commands(text, embedding['sourcePath'])
    diagnostic_commands = compiler_commands(text, diagnostic_target['sourcePath'])
    assert embedding_commands == embedding['compileCommands'] == metadata['actualEmbeddingCompileCommands']
    assert embedding_commands == tick['actualEmbeddingCompileCommands']
    assert embedding_commands == metadata['protectedAbortListenerPolicy']['actualEmbeddingCompileCommands']
    assert diagnostic_commands == diagnostic_target['compileCommands'] == diagnostic['actualCompileCommands']
    for command in layout + embedding_commands + diagnostic_commands:
        validate_command(command)
    kernel = [row['command'] for row in layout_rows if row['file'].endswith('/builtins/node-compat/buffer.cpp')]
    assert len(kernel) == 1
    assert ('-DNODE_COMPAT_GC_STRESS=1' in shlex.split(kernel[0])) is metadata['gcStress']

    install = diagnostic['generatedBuiltinInclude']
    install_path = checked(Path(install['path']), install['sha256'])
    assert install_path.read_text() == install['contents']
    assert install['contents'].splitlines().count('NS_DEF(diagnostics::internal_ticks)') == 1
    assert Path(cache_values['INSTALL_BUILTINS']).resolve() == install_path.resolve()
    audit = metadata['openssl']['completeSourceAudit']
    assert audit['sourceFilesVerified'] == 4650 and audit['beforeAndAfterBuild'] is True
    before_audit = json.loads(checked(Path(audit['beforeReportPath']), audit['beforeReportSha256']).read_bytes())
    assert before_audit['state'] == 'verified-complete-source'
    for key, value in before_audit.items():
        assert audit[key] == value
    dependencies = [
        ('openssl-before.json', audit['beforeReportPath'], audit['beforeReportSha256']),
        ('openssl-receipt.txt', metadata['openssl']['receiptPath'], metadata['openssl']['receiptSha256']),
        ('openssl-configure.txt', metadata['openssl']['configureRecipe']['path'], metadata['openssl']['configureRecipe']['sha256']),
        ('openssl-configdata.pm', metadata['openssl']['configdata']['path'], metadata['openssl']['configdata']['sha256']),
        ('Cargo.toml', metadata['generatedRustProject']['manifestPath'], metadata['generatedRustProject']['manifestSha256']),
        ('Cargo.lock', metadata['generatedRustProject']['lockPath'], metadata['generatedRustProject']['lockSha256']),
    ]
    library = metadata['openssl']['library']
    checked(Path(library['path']), library['sha256'])
    assert Path(library['path']).stat().st_size == library['bytes']

    link_files, wrapper_path = validate_link1(metadata, root, consumer_pins)

    # Validate ALL destinations, including shared sources, before writing any
    # variant file. Exclusive creation never overwrites an existing destination.
    plan = []

    def add(original, target, digest, shared=False):
        checked(original, digest)
        destination(target)
        plan.append((original, target, digest, shared))

    add(engine, OUTPUT / (label + '.engine.wasm'), metadata['engineSha256'])
    add(metadata_path, OUTPUT / (label + '.engine.wasm.build.json'), metadata_digest)
    add(cache, OUTPUT / (label + '-CMakeCache.txt'), metadata['cmakeCacheSha256'])
    add(commands, OUTPUT / (label + '-compile_commands.json'), metadata['compileCommandsSha256'])
    for key, suffix in (('cmakeCache', '-CMakeCache.before.txt'),
                        ('compileCommands', '-compile_commands.before.json')):
        path, digest = configuration_before[key]
        add(path, OUTPUT / (label + suffix), digest)
    add(install_path, OUTPUT / (label + '-builtins.incl'), install['sha256'])
    for phase in ('before', 'after'):
        add(raw_paths[phase], OUTPUT / (label + '-parent-targets.' + phase + '.commands.txt'), evidence[phase]['sha256'])
    for name, original, digest in link_files:
        add(original, OUTPUT / (label + '-' + name), digest)
    add(wrapper_path, OUTPUT / (label + '-cxx-wrapper.txt'), metadata['linkerConcurrencyPolicy']['finalLinkCommandEvidence']['validated']['wrapper']['sha256'])
    add(checked(packet / 'policy.json', consumer_pins['linkPolicySha256']), OUTPUT / 'link-producer-policy.json', consumer_pins['linkPolicySha256'], shared=True)
    add(checked(packet / 'link-policy.py', consumer_pins['linkHelperSha256']), OUTPUT / 'link-producer-helper.py', consumer_pins['linkHelperSha256'], shared=True)
    add(consumer_pins_path, OUTPUT / 'consumer-pins.json', CONSUMER_PINS_SHA256, shared=True)
    for name, original, digest in dependencies:
        add(Path(original), OUTPUT / (label + '-' + name), digest)
    for row in declared:
        add(root / row['path'], OUTPUT / 'source' / row['path'], row['sha256'], shared=True)
    for row in embedding_sources:
        add(external / row['path'], OUTPUT / 'componentize-source' / row['path'], row['sha256'], shared=True)
    add(recipe, OUTPUT / 'build-diagnostic-engine.sh', pins['diagnosticRecipeSha256'], shared=True)
    add(pins_path, OUTPUT / 'diagnostic-pins.json', sha(pins_path), shared=True)
    add(policy_path, OUTPUT / 'source-policy.json', pins['productionPolicySha256'], shared=True)
    helper = Path(__file__).resolve()
    add(helper, OUTPUT / (label + '-freeze-helper.py'), sha(helper))
    licenses = []
    for original in sorted((root / 'builtins/node-compat').rglob('*')):
        if original.is_file() and original.name.startswith(('LICENSE', 'NOTICE')):
            name = str(original.relative_to(root))
            digest = sha(original)
            add(original, OUTPUT / 'source' / name, digest, shared=True)
            licenses.append({'path': name, 'sha256': digest})
    assert len({str(target) for _, target, _, _ in plan}) == len(plan)
    receipt = OUTPUT / (label + '-freeze-receipt.json')
    destination(receipt)
    assert not receipt.exists() and not receipt.is_symlink()
    for _, target, digest, shared in plan:
        if target.exists():
            assert shared, 'Never overwrite a frozen variant: ' + str(target)
            checked(target, digest)
    for original, target, digest, shared in plan:
        copy_exact(original, target, digest, shared)
    for original, target, digest, _ in plan:
        checked(original, digest)
        checked(target, digest)
    report = {
        'schemaVersion': 3, 'state': 'immutable-link1-diagnostic-build-frozen-not-runtime-proof',
        'consumerVersion': consumer_pins['version'],
        'label': label, 'engine': str(OUTPUT / (label + '.engine.wasm')),
        'engineSha256': metadata['engineSha256'], 'engineBytes': metadata['engineBytes'],
        'metadataSha256': metadata_digest, 'sourceRoot': str(OUTPUT / 'source'),
        'sourcePartitions': [306, 2], 'externalEmbeddingInputs': 3,
        'actualLayoutCompileCommands': 61, 'actualEmbeddingCompileCommands': 1,
        'actualDiagnosticCompileCommands': 1, 'nativeCompileDatabaseUsedForParentTargets': False,
        'parentTargetCommandEvidence': evidence,
        'parentTargetFrozenFiles': {phase: str(OUTPUT / (label + '-parent-targets.' + phase + '.commands.txt'))
                                    for phase in ('before', 'after')},
        'finalLinkCommandEvidence': metadata['linkerConcurrencyPolicy']['finalLinkCommandEvidence'],
        'finalLinkFrozenFiles': {key:str(OUTPUT / (label + '-' + name)) for key,name in [('before','final-link.before.commands.txt'),('after','final-link.after.commands.txt'),('validationBefore','final-link.before.validation.json'),('validationAfter','final-link.after.validation.json')]},
        'recipeSha256': pins['diagnosticRecipeSha256'], 'helperSha256': sha(helper),
        'pinsSha256': sha(pins_path), 'licenses': licenses,
        'copies': [{'path': str(target), 'original': str(original), 'sha256': digest,
                    'bytes': target.stat().st_size, 'shared': shared}
                   for original, target, digest, shared in plan],
        'dependencyReferences': [{'kind': 'linked-libcrypto-not-copied', **library}],
        'allCopiesRehashedBeforeReceipt': True,
        'originalEnginePreserved': True, 'guestExecutedByHelper': False,
        'resetSafeReuse': 'OPEN; cancellation and teardown not established',
    }
    with receipt.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
