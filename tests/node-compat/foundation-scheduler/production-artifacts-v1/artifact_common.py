"""Data/source validation and exclusive-copy primitives. No import side effects."""
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil

if not __debug__:
    raise RuntimeError('Artifact validation requires Python assertions enabled')

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUTPUT = Path('/tmp/starling-node-compat/production-scheduler-artifacts-v1/native-freeze')
RECIPE = '869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173'
POLICY = '98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0'
HELPER = '78521feeefe299360228e5db76bfde0b11e6eeee93bd2374cd39b2fe695b610c'
EMBEDDING = '9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205'
ADAPTER = '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
LABELS = ('normal-off', 'normal-runtime', 'gc-off')

def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def checked(path, expected):
    path = Path(path)
    assert isinstance(expected, str) and re.fullmatch(r'[a-f0-9]{64}', expected)
    assert path.is_file() and not path.is_symlink(), path
    assert sha(path) == expected, path
    return path

def capture_regular(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    checksum = digest(data)
    checked(path, checksum)
    return data, checksum

def classify(metadata, label):
    assert label in LABELS
    assert isinstance(metadata, dict)
    assert 'diagnosticOnly' not in metadata or metadata['diagnosticOnly'] is False, 'Diagnostic receipts forbidden before engine use'
    assert 'internalTickDiagnosticPolicy' not in metadata, 'Diagnostic policy forbidden before engine use'
    assert metadata.get('buildRecipeSha256') == RECIPE, 'Production recipe869 required before engine use'
    assert metadata.get('syntheticMetadataOnly', False) is False, 'Synthetic metadata forbidden before engine use'
    gc = label == 'gc-off'
    entropy = 'runtime-only' if label == 'normal-runtime' else 'off'
    assert metadata.get('gcStress') is gc and metadata.get('entropyPolicy') == entropy
    return gc, entropy

def manifest(rows, count):
    assert isinstance(rows, list) and len(rows) == count
    seen = set()
    for row in rows:
        assert set(row) == {'path', 'sha256'}
        name = row['path']
        assert isinstance(name, str) and name and '\0' not in name and '\\' not in name
        assert not Path(name).is_absolute() and all(p not in ('', '.', '..') for p in name.split('/'))
        assert name not in seen and re.fullmatch(r'[a-f0-9]{64}', row['sha256'])
        seen.add(name)
    return rows

def compile_command(command, runtime):
    args = shlex.split(command)
    assert args.count('-c') == 1 and '-fsyntax-only' not in args
    assert '-O3' in args and '-DNDEBUG' in args and not any(x.startswith('-DDEBUG') for x in args)
    for flag in ('NODE_COMPAT_INTERNAL_TICKS', 'NODE_COMPAT_STRICT_INITIALIZATION',
                 'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER', 'NODE_COMPAT_ENTROPY_POLICY'):
        definitions = [x for x in args if x == '-D' + flag or x.startswith('-D' + flag + '=')]
        assert definitions == ['-D' + flag + '=1'], flag
    runtime_definitions = [x for x in args if x == '-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY' or x.startswith('-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=')]
    assert runtime_definitions == (['-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1'] if runtime else [])
    return args

def embedding_command(raw, source):
    selected = []
    for line in raw.decode('utf-8').splitlines():
        if ' -c ' not in line:
            continue
        args = shlex.split(line)
        if args.count('-c') == 1 and args[args.index('-c') + 1] == source:
            selected.append(line)
    assert len(selected) == 1, 'Need exactly one actual parent embedding compile command'
    return selected

def destination(path, output=OUTPUT):
    assert path.is_absolute() and path == Path(os.path.abspath(path))
    assert path.is_relative_to(output)
    cursor = path
    while cursor != output.parent:
        assert not cursor.is_symlink(), cursor
        parent = cursor.parent
        assert parent != cursor
        cursor = parent

def validate_plan(plan, receipt, output=OUTPUT):
    assert len({row['target'] for row in plan}) == len(plan)
    assert receipt not in {row['target'] for row in plan}
    destination(receipt, output)
    assert not receipt.exists() and not receipt.is_symlink(), 'Never overwrite a frozen receipt'
    for row in plan:
        destination(row['target'], output)
        if row.get('original') is not None:
            checked(row['original'], row['sha256'])
        else:
            assert digest(row['data']) == row['sha256']
        if row['target'].exists():
            assert row['shared'], 'Never overwrite a frozen variant'
            checked(row['target'], row['sha256'])

def execute_plan(plan, output=OUTPUT):
    for row in plan:
        target = row['target']
        destination(target, output)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert row['shared']
            checked(target, row['sha256'])
        else:
            with target.open('xb') as result:
                if row.get('original') is not None:
                    with row['original'].open('rb') as source:
                        shutil.copyfileobj(source, result, 1024 * 1024)
                else:
                    result.write(row['data'])
            checked(target, row['sha256'])
        if row.get('original') is not None:
            checked(row['original'], row['sha256'])
    for row in plan:
        checked(row['target'], row['sha256'])
        if row.get('original') is not None:
            checked(row['original'], row['sha256'])

def verify_frozen_variant(label, output=OUTPUT, return_receipt_digest=False):
    assert label in LABELS
    receipt_path = output / (label + '-freeze-receipt.json')
    destination(receipt_path, output)
    receipt_data, receipt_digest = capture_regular(receipt_path)
    receipt = json.loads(receipt_data)
    assert receipt['schema'] == 1 and receipt['state'] == 'immutable-release-engine-frozen'
    assert receipt['label'] == label and receipt['recipeSha256'] == RECIPE
    assert receipt['nativeInputsVerified'] == 306 and receipt['externalEmbeddingInputsVerified'] == 3
    assert receipt['actualLayoutCompileCommands'] == 61 and receipt['actualEmbeddingCompileCommands'] == 1
    assert receipt['actualStrictCompileCommands'] == 4
    engine = output / (label + '.engine.wasm')
    metadata_path = Path(str(engine) + '.build.json')
    metadata = json.loads(checked(metadata_path, receipt['receiptSha256']).read_bytes())
    classify(metadata, label)  # Reject diagnostic/old receipt before engine bytes.
    checked(engine, receipt['engineSha256'])
    assert engine.stat().st_size == receipt['engineBytes']
    assert metadata['engineSha256'] == receipt['engineSha256']
    assert metadata['engineBytes'] == receipt['engineBytes']
    assert len({row['path'] for row in receipt['copies']}) == len(receipt['copies'])
    inventory = {row['path']: row for row in receipt['copies']}
    for row in receipt['copies']:
        path = Path(row['path'])
        destination(path, output)
        checked(path, row['sha256'])
        assert path.stat().st_size == row['bytes']
    native = manifest(metadata['sourceManifest'], 306)
    external = manifest(metadata['componentizeSourceManifest'], 3)
    for entries, prefix in ((native, 'source'), (external, 'componentize-source')):
        for row in entries:
            assert inventory[str(output / prefix / row['path'])]['sha256'] == row['sha256']
    for name, expected in ((label + '.engine.wasm', receipt['engineSha256']),
                           (label + '.engine.wasm.build.json', receipt['receiptSha256']),
                           (label + '-CMakeCache.txt', metadata['cmakeCacheSha256']),
                           (label + '-compile_commands.json', metadata['compileCommandsSha256']),
                           ('build-engine.sh', RECIPE), ('source-policy.json', POLICY),
                           ('source-policy-helper.py', HELPER), ('tooling/wasi_snapshot_preview1.wasm', ADAPTER)):
        assert inventory[str(output / name)]['sha256'] == expected
    frozen_policy = json.loads((output / 'source-policy.json').read_bytes())
    assert sorted(native, key=lambda row: row['path']) == frozen_policy['expectedNativeSourceManifest']
    evidence = receipt['postBuildEmbeddingEvidence']
    assert evidence['version'] == 'production-after-build-parent-ninja-v1'
    assert evidence['beforeBuildCaptureExists'] is False and evidence['exitCode'] == 0
    assert inventory[evidence['path']]['sha256'] == evidence['sha256']
    assert embedding_command(Path(evidence['path']).read_bytes(), evidence['sourcePath']) == metadata['actualEmbeddingCompileCommands'] == evidence['compileCommands']
    hashes = {row['sha256'] for row in receipt['copies']}
    for value in (metadata['generatedRustProject']['manifestSha256'], metadata['generatedRustProject']['lockSha256'],
                  metadata['openssl']['receiptSha256'], metadata['openssl']['completeSourceAudit']['beforeReportSha256']):
        assert value in hashes, 'Missing frozen Rust/OpenSSL evidence'
    assert receipt['allInputsValidatedBeforeCopies'] is True and receipt['allCopiesAndOriginalsRehashed'] is True
    checked(receipt_path, receipt_digest)
    if return_receipt_digest:
        return receipt_path, receipt, metadata, receipt_digest
    return receipt_path, receipt, metadata
