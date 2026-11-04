"""Capture completed native-artifact TEXT evidence; never run a build or guest.

This is an exclusive archival operation. Frozen engine/source assets are hashed
as references; binary bytes and the full native-source tree are not copied.
"""
from pathlib import Path
import hashlib
import json
import re
import stat

HERE = Path(__file__).resolve().parent
PACKETS = HERE.parent
EXTERNAL = Path('/tmp/starling-node-compat')
RUN = EXTERNAL / 'production-scheduler-artifacts-v1'
FREEZE = RUN / 'native-freeze'
LABELS = ['normal-off', 'normal-runtime', 'gc-off']
RECIPE = '869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173'
copied, existing, frozen_references, variants, packet_references = [], [], [], [], []
captured_sources = {}


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(data)
    return result.hexdigest()


def regular(path):
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode) and not path.is_symlink(), path
    return info


def checked(path, expected=None, size=None):
    info = regular(path)
    value = digest(path)
    if expected is not None:
        assert value == expected, path
    if size is not None:
        assert info.st_size == size, path
    return value, info.st_size


def capture(source, destination, role, expected=None):
    regular(source)
    assert source.suffix not in ['.wasm', '.cwasm', '.a', '.o'], source
    data = source.read_bytes()
    data.decode('utf-8')
    assert b'\x00' not in data, source
    assert data[:4] not in [b'\x00asm', b'\x7fELF', b'\xcf\xfa\xed\xfe', b'\xfe\xed\xfa\xcf'], source
    value = hashlib.sha256(data).hexdigest()
    if expected is not None:
        assert value == expected, source
    target = HERE / destination
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(data)
    assert digest(target) == value == digest(source)
    row = {'path': destination, 'source': str(source), 'sha256': value,
           'bytes': len(data), 'role': role, 'byteExactTextCopy': True}
    copied.append(row)
    captured_sources[str(source)] = destination
    return row


def packet_copy(name, target, expected_index, role):
    base = PACKETS / name
    assert digest(base / 'index.json') == expected_index
    index = json.loads((base / 'index.json').read_bytes())
    for row in index['files']:
        source = base / row['path']
        checked(source, row['sha256'], row['bytes'])
        capture(source, target + '/' + row['path'], role, row['sha256'])
    capture(base / 'index.json', target + '/index.json', role + '-index', expected_index)
    packet_references.append({'packet': name, 'indexSha256': expected_index,
                              'copiedTextFiles': len(index['files']) + 1,
                              'helperOrVerifierReexecutedByAggregate': False})


assert not (HERE / 'capture-inventory.json').exists(), 'Never overwrite a completed capture'
assert not (HERE / 'index.json').exists(), 'Never modify a sealed aggregate'
for source in sorted(HERE.iterdir()):
    if source.is_file() and source.name != 'capture.py':
        value, size = checked(source)
        existing.append({'path': source.name, 'sha256': value, 'bytes': size,
                         'role': 'preexisting-root-record', 'preservedUnchanged': True})

independent = {
    'normal-off': ('production-normal-off-verification-v1', '97a5b3683c74c3465666225fc5e440660e18e25b79bd786c5c9c05ecc324bbd0'),
    'normal-runtime': ('production-normal-runtime-verification-v1', '9999f6ff4a9b2fcbf361b142ad28da4d53316336b9e20b150fe05ecb641ebe76'),
    'gc-off': ('production-gc-off-verification-v1', 'e47e5a7252835f9467dfa05248a83026b70c8aa255b1fa3eebef5a2b002c5814'),
}
for label, (name, index_sha) in independent.items():
    packet_copy(name, 'independent/' + label, index_sha, 'independent-read-only-native-artifact-verification')
packet_copy('production-artifacts-v1', 'artifact-tools',
            '85ba9c391c9b15fa8af0021a834e91c3a5930f452c28748c031f13490474c77f',
            'frozen-production-artifact-tool-packet')
packet_copy('production-pin-review-v1', 'pin-review',
            '656a88d8f0d38bcb2b9314a95f5463115c8b8f436722423e50e29939ff9e3934',
            'root-reviewed-actual-pin-data-runtime-pending')

normal_freeze_sha = digest(FREEZE / 'normal-off-freeze-receipt.json')
for label, steps in zip(LABELS, [107, 107, 16]):
    build = RUN / 'builds' / label
    result = json.loads((build / 'result.json').read_bytes())
    assert result['rawChildExitCode'] == result['launcherExitCode'] == result['status'] == 0
    assert result['lifecycleComplete'] is True and result['evidenceComplete'] is True
    assert result['ownedGroupCleanup']['complete'] is True
    assert result['guestExecutionRequested'] is False
    assert result['recipeSha256'] == RECIPE
    observed = re.findall(r'^\[(\d+)/(\d+)\]', (build / 'build.log').read_text(), re.M)
    assert observed and observed[-1] == (str(steps), str(steps))
    for name in ['launch.json', 'result.json', 'build.log']:
        capture(build / name, 'launchers/' + label + '/' + name, 'completed-native-launcher-evidence',
                result['logSha256'] if name == 'build.log' else None)
    for phase in ['launch', 'freeze']:
        for suffix in ['stdout.json', 'stderr.txt']:
            source = EXTERNAL / ('production-' + label + '-' + phase + '-v1.' + suffix)
            capture(source, 'raw/' + label + '/' + phase + '.' + suffix, 'exact-completed-tool-output')
    receipt_path = FREEZE / (label + '-freeze-receipt.json')
    receipt_sha, _ = checked(receipt_path)
    receipt = json.loads(receipt_path.read_bytes())
    metadata_path = FREEZE / (label + '.engine.wasm.build.json')
    metadata_sha, _ = checked(metadata_path, receipt['receiptSha256'])
    metadata = json.loads(metadata_path.read_bytes())
    assert receipt['schema'] == 1 and receipt['state'] == 'immutable-release-engine-frozen'
    assert receipt['nativeInputsVerified'] == len(metadata['sourceManifest']) == 306
    assert receipt['externalEmbeddingInputsVerified'] == len(metadata['componentizeSourceManifest']) == 3
    assert receipt['actualLayoutCompileCommands'] == 61
    assert receipt['actualStrictCompileCommands'] == 4 and receipt['actualEmbeddingCompileCommands'] == 1
    assert metadata.get('diagnosticOnly', False) is False and 'internalTickDiagnosticPolicy' not in metadata
    assert metadata['oomTesting'] is False and metadata['internalTicksEnabled'] is True
    assert metadata['gcStress'] == (label == 'gc-off')
    assert metadata['entropyPolicy'] == ('runtime-only' if label == 'normal-runtime' else 'off')
    assert receipt['recipeSha256'] == metadata['buildRecipeSha256'] == RECIPE
    assert metadata['generatedRustProject']['cargoBuildLocked'] is True
    assert metadata['openssl']['completeSourceAudit']['sourceFilesVerified'] == 4650
    assert metadata['openssl']['completeSourceAudit']['beforeAndAfterBuild'] is True
    evidence = receipt['postBuildEmbeddingEvidence']
    assert evidence['version'] == 'production-after-build-parent-ninja-v1'
    assert evidence['beforeBuildCaptureExists'] is False and len(evidence['compileCommands']) == 1
    assert len(receipt['copies']) == 335
    assert len({row['path'] for row in receipt['copies']}) == 335
    for row in receipt['copies']:
        path = Path(row['path'])
        relative = path.relative_to(FREEZE)
        assert not any(part == '..' for part in relative.parts)
        current = path
        while current != FREEZE:
            assert not current.is_symlink(), current
            current = current.parent
        value, size = checked(path, row['sha256'], row['bytes'])
        is_binary = path.suffix in ['.wasm', '.cwasm', '.a', '.o']
        native_source = relative.parts[0] == 'source'
        # Full source306 remains in the immutable external inventory. Copy only
        # licenses from that partition, plus all separate text evidence.
        copy_text = not is_binary and (not native_source or '/LICENSE' in relative.as_posix())
        if copy_text and str(path) not in captured_sources:
            capture(path, 'native-freeze-text/' + relative.as_posix(),
                    'exact-frozen-configuration-dependency-policy-or-external-source-text', value)
        frozen_references.append({**row, 'label': label, 'aggregateRehashed': True,
                                  'copiedIntoAggregate': str(path) in captured_sources,
                                  'aggregateTextPath': captured_sources.get(str(path)),
                                  'referenceKind': 'binary-reference-only' if is_binary else
                                  'native-source-reference-only' if not copy_text else 'copied-text',
                                  'originalMutableBuildPathRehashed': False})
    capture(receipt_path, 'native-freeze-text/' + receipt_path.name, 'exact-completed-freeze-receipt', receipt_sha)
    root_native = json.loads((HERE / (label + '-native-results.json')).read_bytes())
    assert root_native['engineSha256'] == receipt['engineSha256']
    assert root_native['metadataSha256'] == metadata_sha and root_native['nativeSteps'] == steps
    assert digest(HERE / (label + '-engine.build.json')) == metadata_sha
    assert digest(HERE / (label + '-freeze-receipt.json')) == receipt_sha
    prereq = result.get('normalOffFrozenBeforeGCReconfigure')
    if label == 'gc-off':
        assert prereq['sha256'] == normal_freeze_sha
        assert prereq['engineSha256'] == json.loads((FREEZE / 'normal-off-freeze-receipt.json').read_bytes())['engineSha256']
    else:
        assert prereq is None
    review = json.loads((PACKETS / independent[label][0] / 'results.json').read_bytes())
    assert review['engineSha256'] == receipt['engineSha256']
    assert review['engineMetadataSha256'] == metadata_sha and review['freezeReceiptSha256'] == receipt_sha
    variants.append({'label': label, 'enginePath': receipt['engine'], 'engineSha256': receipt['engineSha256'],
                     'engineBytes': receipt['engineBytes'], 'metadataSha256': metadata_sha,
                     'freezeReceiptSha256': receipt_sha, 'nativeBuildSteps': steps,
                     'launcherExitCode': 0, 'freezerToolExitCode': 0,
                     'frozenInventoryEntriesRehashed': 335, 'nativeInputs': 306, 'externalEmbeddingInputs': 3,
                     'nativeCommands': 61, 'strictCommands': 4, 'parentEmbeddingCommands': 1,
                     'embeddingCapture': 'after-build-only', 'normalOffFreezePrerequisite': prereq,
                     'independentResultsSha256': digest(PACKETS / independent[label][0] / 'results.json'),
                     'independentIndexSha256': independent[label][1],
                     'gcStress': metadata['gcStress'], 'entropyPolicy': metadata['entropyPolicy'],
                     'linkedDependencyReferencesRecordedNotRead': receipt['dependencyReferences']})

for stem in ['production-pin-candidate-normal-off-v1', 'production-pin-candidates-all-v1']:
    for suffix in ['.json', '.stdout.json', '.stderr.txt']:
        capture(EXTERNAL / (stem + suffix), 'raw/exports/' + stem + suffix,
                'preserved-unreviewed-export-candidate-or-exact-export-output')
partial = json.loads((HERE / 'normal-off-unreviewed-pin-candidate.json').read_bytes())
all_candidates = json.loads((HERE / 'all-unreviewed-pin-candidates.json').read_bytes())
assert partial['state'] == all_candidates['state'] == 'UNREVIEWED_PRODUCTION_PIN_CANDIDATES_V1'
assert partial['variants']['normal-runtime'] is None and partial['variants']['gc-off'] is None
assert all(all_candidates['variants'][label]['state'] == 'unreviewed-production-freeze-pin-candidate' for label in LABELS)
for row in existing:
    assert digest(HERE / row['path']) == row['sha256'] and regular(HERE / row['path']).st_size == row['bytes']

inventory = {'schemaVersion': 1, 'state': 'COMPLETED_NATIVE_ARTIFACT_TEXT_CAPTURE_RUNTIME_EXCLUDED',
             'preservedPreexistingRootRecords': existing, 'byteExactTextCopies': copied,
             'frozenExternalInventoryReferences': frozen_references,
             'packetReferences': packet_references,
             'externalInventoryEntriesRehashed': len(frozen_references),
             'uniqueFrozenExternalPathsRehashed': len({row['path'] for row in frozen_references}),
             'binaryBytesCopied': 0, 'all306NativeSourcesCopiedAgain': False,
             'nativeBuildGuestHostOrVerifierExecutedByCapture': False}
with (HERE / 'capture-inventory.json').open('x') as stream:
    json.dump(inventory, stream, indent=2)
    stream.write('\n')
summary = {'schemaVersion': 1, 'state': 'PRODUCTION_NATIVE_ARTIFACTS_COMPLETE_RUNTIME_ACCEPTANCE_EXCLUDED',
           'variants': variants, 'recipeSha256': RECIPE,
           'preexistingRootRecordsPreserved': len(existing), 'additionalTextCopies': len(copied),
           'frozenInventoryReferencesRehashed': len(frozen_references),
           'openssl4650SourceAuditRecorded': True, 'openssl4650SourceReauditByCapture': False,
           'binaryBytesCopied': 0, 'partialAndAllUnreviewedExportsPreserved': True,
           'runtimeAcceptanceClaim': False, 'performanceMemoryOrStartupClaim': False,
           'engineGuestHostCompilerOrVerifierExecutedByCapture': False,
           'runtimeReceipts': 'Separate production-runtime-v1 packet; not evidence in this aggregate'}
with (HERE / 'execution-summary.json').open('x') as stream:
    json.dump(summary, stream, indent=2)
    stream.write('\n')
logs = [row for row in copied + existing if any(word in row['path'] for word in
        ['build.log', 'stdout', 'stderr', '.commands.txt'])]
with (HERE / 'log-inventory.json').open('x') as stream:
    json.dump({'schemaVersion': 1, 'state': 'EXACT_FULL_TEXT_LOGS_NOT_EXCERPTS', 'files': logs}, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': summary['state'], 'preservedRootRecords': len(existing),
                  'textCopies': len(copied), 'frozenReferencesRehashed': len(frozen_references),
                  'binaryBytesCopied': 0}))
