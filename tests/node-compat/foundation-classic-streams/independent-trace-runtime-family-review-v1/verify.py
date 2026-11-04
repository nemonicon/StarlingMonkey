"""Read/hash/data verification only. Imports no project or artifact helper."""
from pathlib import Path
import hashlib
import json
import os
import re
import shlex
import stat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
BASE = FAMILY / 'production-trace-runtime-activated-v1'
ACTIVATED = 'e1f87cd6a2fd09ff34055187bfb938c2b094c3fd333ef9f57b6a1eea4c175b78'
PINS = '182e8b724d94ebf73450c0ffcea81fb19b902028e2839bd2a9d1452ab7fab5eb'
REVIEW = 'ce88ac3495afdf97718a34f7bf2c2360613f95a91f5c193e556c87269b4a8be0'
RECIPE = '3694c88b7d000f27e11ffcac835fe0b205b2075f5b1d8d29c61f5b0038ba1cf3'
SOURCE_ROOT = Path('/tmp/starling-node-compat/classic-trace-source-v1')
seen = {}


def sha(data): return hashlib.sha256(data).hexdigest()


def read(path, expected=None, size=None):
    path = Path(os.path.abspath(path)); before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    data = path.read_bytes(); after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    checksum = sha(data)
    if expected is not None: assert checksum == expected, str(path)
    if size is not None: assert len(data) == size, str(path)
    row = {'path': str(path), 'sha256': checksum, 'bytes': len(data)}
    assert str(path) not in seen or seen[str(path)] == row
    seen[str(path)] = row
    return data


def doc(path, expected=None): return json.loads(read(path, expected))


def below(root, path):
    assert path != root and path.is_relative_to(root)
    assert root.is_dir() and not root.is_symlink()
    while path != root:
        assert not path.is_symlink(), str(path); path = path.parent


def indexed(root, expected, count):
    index = doc(root / 'index.json', expected)
    assert len(index['files']) == count
    assert len({row['path'] for row in index['files']}) == count
    for row in index['files']:
        path = Path(os.path.abspath(root / row['path'])); below(root, path)
        read(path, row['sha256'], row['bytes'])
    return index


def membership(root):
    rows = []
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            path = Path(base) / name; mode = path.lstat().st_mode
            kind = 'symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file' if stat.S_ISREG(mode) else None
            assert kind, str(path); rows.append({'path': str(path.relative_to(root)), 'kind': kind})
        dirs[:] = [name for name in dirs if not (Path(base) / name).is_symlink()]
    return sorted(rows, key=lambda row: row['path'])


def main():
    index = indexed(BASE, ACTIVATED, 26)
    assert index['state'] == 'ACTUAL_REVIEWED_CLASSIC_TRACE_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED'
    assert index['runtimeAcceptanceClaim'] is False
    entries = membership(BASE)
    assert {row['path'] for row in entries if row['kind'] == 'file'} == {row['path'] for row in index['files']} | {'index.json'}
    assert not any(row['kind'] == 'symlink' for row in entries)
    receipt = doc(BASE / 'source-receipt.json')
    seal = doc(BASE / 'input-freeze.json', receipt['inputFreezeSha256'])
    assert seal['state'] == 'REVIEWED_CLASSIC_TRACE_WHOLE_CONSUMED_INPUT_SEAL'
    assert len(seal['inputs']) == receipt['consumedFiles'] == 6414
    inputs = {}
    for row in seal['inputs']:
        path = Path(os.path.abspath(BASE / row['path']))
        assert path not in inputs; inputs[path] = row
        if 'boundary' in row: below(Path(os.path.abspath(BASE / row['boundary'])), path)
        read(path, row['sha256'], row['bytes'])
    assert len(seal['toolTrees']) == 2 and len(seal['toolLinks']) == receipt['toolLinks'] == 22
    actual_links = set(); tool_files = 0; roots = []; canonical = []
    for tree in seal['toolTrees']:
        root = Path(tree['path']); assert str(root.resolve(strict=True)) == tree['realPath']
        assert membership(root) == tree['entries']; roots.append(root); canonical.append(root.resolve())
        for row in tree['entries']:
            path = root / row['path']
            if row['kind'] == 'file': assert path in inputs; tool_files += 1
            elif row['kind'] == 'symlink': actual_links.add(path)
    links = set()
    for row in seal['toolLinks']:
        path = Path(row['path']); assert path not in links; links.add(path)
        assert any(path.is_relative_to(root) for root in roots)
        assert path.is_symlink() and os.readlink(path) == row['linkText']
        target = path.resolve(strict=True); assert str(target) == row['resolvedTarget']
        assert any(target == root or target.is_relative_to(root) for root in canonical)
        assert row['targetKind'] == ('directory' if target.is_dir() else 'file')
        if target.is_file(): read(target, row['targetSha256'], row['targetBytes'])
    assert links == actual_links
    source_candidate = FAMILY / 'trace-runtime-activation-candidate-v1'
    indexed(source_candidate, '693057a3f90e911e331d8e79f7242816e8f09b354fb78ba4c79f7c18f69649ab', 34)
    indexed(FAMILY / 'independent-trace-runtime-activation-source-review-v1', 'a45cc10742d37be2d0eb28bd53e76e763b58a8337f1dc51216eddeb4fcfc5965', 3)
    integration = FAMILY / 'trace-integration-candidate-v1'
    indexed(integration, '224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b', 159)
    policy = doc(integration / 'policy.json', '891a4c53dd4a7b7d776c21003acdd12c7944c6a3eca019a1d9b2be620ed8b11c')
    pins = doc(BASE / 'runtime-pins.json', PINS); review = doc(BASE / 'root-review-receipt.json', REVIEW)
    assert pins['state'] == 'REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1'
    assert review['state'] == 'ROOT_REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1'
    assert review['reviewedPinsSha256'] == receipt['pinsSha256'] == PINS
    assert receipt['rootReviewSha256'] == REVIEW
    assert receipt['recipeSha256'] == review['recipeSha256'] == RECIPE
    assert receipt['sourceContractVersion'] == review['sourceContractVersion'] == 'sm-classic-trace-source-v1'
    assert receipt['configuredSourceRoot'] == review['configuredSourceRoot'] == str(SOURCE_ROOT)
    native = {}
    for label, pin in pins['variants'].items():
        assert pin['state'] == 'reviewed-real-classic-trace-production-freeze'
        assert pin['variant'] == label and pin['sourceContractVersion'] == 'sm-classic-trace-source-v1'
        assert pin['classicTraceSourcePolicy'] == policy['classicTraceSourcePolicy']
        assert pin['recipeSha256'] == RECIPE and pin['sourceFiles'] == 342
        assert pin['gcStress'] is (label == 'gc-off') and pin['classicStreamsEnabled'] is (label != 'disabled-off')
        assert pin['entropyPolicy'] == ('runtime-only' if label == 'normal-runtime' else 'off')
        for key in ('engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256'):
            assert pin[key] == receipt['actualArtifacts'][label][key] == review['variants'][label][key]
        for row in pin['frozenFiles']:
            path = Path(row['path']); consumed = inputs[path]
            assert consumed['sha256'] == row['sha256'] and consumed['bytes'] == row['bytes']
        assert len(pin['frozenFiles']) == 474
        freeze = doc(pin['freezeReceiptPath'], pin['freezeReceiptSha256'])
        metadata = doc(pin['enginePath'] + '.build.json', pin['receiptSha256'])
        read(pin['enginePath'], pin['engineSha256'], pin['engineBytes'])
        assert freeze['state'] == 'immutable-trace-release-engine-frozen'
        assert len(freeze['copies']) == 474 and metadata['classicTraceSourcePolicy'] == policy['classicTraceSourcePolicy']
        assert metadata['sourceManifest'] == policy['expectedNativeSourceManifest']
        assert metadata['strictEventExceptionPolicy']['version'] == policy['strictPolicyVersion']
        assert metadata['protectedAbortListenerPolicy']['version'] == policy['protectedPolicyVersion']
        assert metadata.get('diagnosticOnly', False) is False and 'internalTickDiagnosticPolicy' not in metadata
        for row in metadata['sourceManifest']:
            read(Path(pin['sourceRoot']) / row['path'], row['sha256'])
        assert len(metadata['componentizeSourceManifest']) == 3
        for row in metadata['componentizeSourceManifest']:
            read(Path(pin['componentizeSourceRoot']) / row['path'], row['sha256'])
        db = doc(pin['commandsPath'], pin['compileCommandsSha256'])
        native_paths = {row['path'] for row in metadata['sourceManifest'] if row['path'].endswith('.cpp') and row['path'].startswith(('builtins/', 'runtime/'))}
        commands = [row['command'] for row in db if any(row['file'].endswith('/' + name) for name in native_paths)]
        assert len(commands) == 61 and commands == metadata['internalTickPolicy']['actualLayoutCompileCommands']
        parent_raw = read(pin['parentEmbeddingCommandPath'], pin['parentEmbeddingCommandSha256']).decode()
        parent = []
        for line in parent_raw.splitlines():
            if ' -c ' in line:
                args = shlex.split(line)
                if args.count('-c') == 1 and args[args.index('-c') + 1].endswith('/embedding/embedding.cpp'): parent.append(line)
        assert len(parent) == 1 and parent == metadata['actualEmbeddingCompileCommands']
        assert freeze['postBuildEmbeddingEvidence']['beforeBuildCaptureExists'] is False
        assert freeze['actualStrictCompileCommands'] == 4 and freeze['actualClassicPrivateCompileCommands'] == 5
        native[label] = {'engineSha256': pin['engineSha256'], 'frozenFiles': 474, 'nativeSources': 342,
                         'nativeCommands': 61, 'strictCommands': 4, 'privateCommands': 5, 'separateAfterOnlyEmbedding': 1}
    expected_replacements = {'PINS_SHA': PINS, 'INPUTS_SHA': receipt['inputFreezeSha256'], 'RECIPE_SHA': RECIPE,
        'SELECTOR_SHA': sha(read(SOURCE_ROOT / 'tests/node-compat/module-selection.mjs')),
        'ADMISSION_SHA': sha(read(SOURCE_ROOT / 'tests/node-compat/classic-streams-admission.mjs')), 'ROOT_REVIEW_SHA': REVIEW}
    template = read(BASE / 'runtime-preflight.template.mjs').decode(); compiled = template
    for key, value in expected_replacements.items(): compiled = compiled.replace('@' + key + '@', value)
    assert not re.search(r'@[A-Z_]+@', compiled)
    assert compiled.encode() == read(BASE / 'runtime-preflight.mjs')
    payload = source_candidate / 'payload'
    for path in sorted(payload.rglob('*')):
        if path.is_file(): assert read(path) == read(BASE / path.relative_to(payload))
    for name in ('runtime-contract.mjs', 'runtime-preflight.template.mjs', 'consumed.mjs', 'fresh-gates.json'):
        assert read(source_candidate / name) == read(BASE / name)
    context = seal['sourceContext']
    assert context['actualConfiguredRoot'] == str(SOURCE_ROOT) and context['preparation1175RelocatedOrFollowed'] is False
    for row in context['canonicalSourceMappings']:
        assert inputs[Path(row['afterPath'])]['sha256'] == row['afterSha256']
        read(row['beforePath'], row['beforeSha256']); read(row['afterPath'], row['afterSha256'])
    for row in policy['expectedNativeSourceManifest']: read(SOURCE_ROOT / row['path'], row['sha256'])
    tool_pins = doc(integration / 'artifact-tools/tool-pins.json')
    assert len(tool_pins['toolDependencies']) == 92
    for row in tool_pins['toolDependencies']: read(SOURCE_ROOT / row['path'], row['sha256'], row['bytes'])
    assert receipt['engineMetadataRewritten'] is receipt['componentOrHostExecuted'] is receipt['runtimeAcceptanceClaim'] is False
    indexed(BASE, ACTIVATED, 26)
    result = {'schemaVersion': 1, 'state': 'INDEPENDENT_GENERATED_CORRECTED_TRACE_RUNTIME_FAMILY_VERIFIED_NO_EXECUTION',
        'familyIndexSha256': ACTIVATED, 'indexedFamilyFiles': 26, 'consumedInputs': 6414,
        'toolTrees': 2, 'toolLinks': 22, 'toolFiles': tool_files, 'native': native,
        'exactCandidatePayloadsAndSixPlaceholderRendering': True,
        'actualCorrectedStagedSource342AndTool92': True, 'preparationContextPreserved': True,
        'projectHelpersImported': False, 'nativePreflightOrActivationOrGuestOrHostOrToolchainExecuted': False,
        'runtimeAcceptanceClaim': False, 'concreteBlockers': [], 'uniqueReadFiles': len(seen)}
    with (HERE / 'results.json').open('x') as out: json.dump(result, out, indent=2); out.write('\n')
    with (HERE / 'checked-inputs.json').open('x') as out: json.dump({'schemaVersion': 1, 'files': list(sorted(seen.values(), key=lambda row: row['path']))}, out, indent=2); out.write('\n')
    print(json.dumps(result))


if __name__ == '__main__': main()
