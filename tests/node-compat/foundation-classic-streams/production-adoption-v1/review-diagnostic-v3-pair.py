"""Create separate Root pair authority from actual independently reviewed freezes."""
from pathlib import Path
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
SOURCE = Path('/private/tmp/starling-node-compat/classic-benchmark-trace-v2-source')
FREEZE = Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze')
EXPORT = Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-unreviewed-pair-pins.json')
PROOFS = {
    'benchmark-classic-on': ('independent-measurement-producer-v3-on-native-review-v1',
        'c05afb8d47edfec5e024578583c9b166d44f94edc44093b9a828352d8abbd019',
        '7ca727b194211debcbbc2eb4f2a404d723665490003b1fa0e9e715843389b3e4'),
    'benchmark-classic-off': ('independent-measurement-producer-v3-off-native-review-v1',
        'ca2debb8964c7722503c1e398a0f69c04bfa008c1b9560ce842dfca7896e777e',
        '2e936a751b4c8400f9c2a8f666c92c7a4d9ca55201f3d8544cbd73ab8560063a'),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def checked(path, expected, size=None):
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected, path
    assert size is None or len(data) == size, path
    return data

terminal = json.loads(Path('/tmp/starling-node-compat/classic-benchmark-v3-pair-export-v1.terminal.json').read_bytes())
assert terminal['returncode'] == 0
export_sha = sha(EXPORT)
pins = json.loads(EXPORT.read_bytes())
assert pins['state'] == 'UNREVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_PIN_CANDIDATES_V3'
old = {
    HERE / 'reviewed-diagnostic-v3-on-pins.json': '2e9811a54b03733d7d4dde0b42f66831a9b97da2c2f26313f078443dc329165c',
    HERE / 'diagnostic-v3-on-root-review-receipt.json': '9681578ea64c826f72baa1e1bff1533af276ff27d6dda52c5bf1dbe064697001',
}
for path, digest in old.items():
    checked(path, digest)
variants, counts = {}, {}
for label, pin in pins['variants'].items():
    name, index_sha, result_sha = PROOFS[label]
    proof = BASE / name
    index = json.loads(checked(proof / 'index.json', index_sha))
    assert any(row['sha256'] == result_sha for row in index['files'])
    for row in index['files']:
        checked(proof / row['path'], row['sha256'], row['bytes'])
    receipt = json.loads(checked(FREEZE / (label + '-freeze-receipt.json'), pin['freezeReceiptSha256']))
    assert len(receipt['copies']) == 525
    originals = 0
    for row in receipt['copies']:
        checked(Path(row['path']), row['sha256'], row['bytes'])
        if row['original'] is not None:
            checked(Path(row['original']), row['sha256'], row['bytes'])
            originals += 1
    assert originals == 521
    metadata = json.loads(checked(FREEZE / (label + '.engine.wasm.build.json'), pin['metadataSha256']))
    assert metadata['diagnosticOnly'] is True and metadata['gcStress'] is False
    assert len(metadata['sourceManifest']) == 342
    for row in metadata['sourceManifest']:
        checked(SOURCE / row['path'], row['sha256'])
    checked(FREEZE / (label + '.engine.wasm'), pin['engineSha256'], pin['engineBytes'])
    assert pin['sourceFiles'] == 342 and pin['addonFiles'] == 2
    pin['state'] = 'reviewed-classic-trace-benchmark-diagnostic-freeze'
    pin['reviewRequired'] = False
    variants[label] = {key: pin[key] for key in ('engineSha256', 'engineBytes', 'metadataSha256', 'freezeReceiptSha256')}
    variants[label].update(independentProofIndexSha256=index_sha, independentProofResultSha256=result_sha)
    counts[label] = {'copies': 525, 'originalReferences': originals, 'metadataSourceRows': 342, 'proofFiles': len(index['files'])}
pins['state'] = 'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V3'
pins['requiresIndependentReviewAndSeparateRootAuthority'] = False
pin_path = HERE / 'reviewed-diagnostic-v3-pair-pins.json'
review_path = HERE / 'diagnostic-v3-pair-root-review-receipt.json'
assert not pin_path.exists() and not review_path.exists()
with pin_path.open('x') as stream:
    json.dump(pins, stream, indent=2)
    stream.write('\n')
review = {'schemaVersion': 1, 'state': 'ROOT_REVIEWED_COMMON_BYTE_DIAGNOSTIC_PAIR_V1',
    'reviewedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'reviewedPinsSha256': sha(pin_path), 'sourceIndexSha256': '46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc',
    'recipeSha256': 'd98d1129db0a55abe18c2b96e7fe314ab27d6bc9a2ef481abed3f07d996fbba6',
    'sourceContractVersion': 'sm-classic-trace-source-v1', 'sourceFiles': 342, 'addonFiles': 2,
    'externalEmbeddingFiles': 3, 'declaredConfiguredSourceRoot': '/tmp/starling-node-compat/classic-benchmark-trace-v2-source',
    'canonicalDiagnosticSourceRoot': str(SOURCE), 'variants': variants, 'freshRootRechecks': counts,
    'originalUnreviewedExport': {'path': str(EXPORT), 'sha256': export_sha},
    'existingOnOnlyAuthorityUnchanged': True, 'runtimeAcceptanceClaim': False, 'timingAllowed': False,
    'performanceClaim': False,
    'earlierReaderFailure': {'rootCommandChunk': 'b9c6d0', 'exitCode': 1,
        'reason': 'Reader treated a generated receipt copy with original=null as a filesystem path. No authority was written; four generated copies per variant have no original file.'}}
with review_path.open('x') as stream:
    json.dump(review, stream, indent=2)
    stream.write('\n')
assert sha(EXPORT) == export_sha
for path, digest in old.items():
    checked(path, digest)
print(json.dumps({'pairPinsSha256': sha(pin_path), 'pairRootReviewSha256': sha(review_path), 'timingAllowed': False}))
