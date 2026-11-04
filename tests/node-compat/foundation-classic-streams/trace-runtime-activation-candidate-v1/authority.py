"""Pure future Root-authority parser. No engine/tool imports or output writes."""
import hashlib
import json
from pathlib import Path
import re

RECIPE = '3694c88b7d000f27e11ffcac835fe0b205b2075f5b1d8d29c61f5b0038ba1cf3'
POLICY = '891a4c53dd4a7b7d776c21003acdd12c7944c6a3eca019a1d9b2be620ed8b11c'
HELPER = '43bae8056534c1a6f384961e0b054a68d44d30030e21897bd9688a8fc8b65bc9'
FIX = '59c9233c5dd1c9f07c4da16a79abdb58abc9775b37c714f6af179e85f23f0631'
CONTRACT = 'sm-classic-trace-source-v1'
SOURCE_ROOT = Path('/tmp/starling-node-compat/classic-trace-source-v1')
FREEZE_ROOT = Path('/tmp/starling-node-compat/production-classic-trace-v1/native-freeze')
LABELS = ('normal-off', 'normal-runtime', 'gc-off', 'disabled-off')
SHA = re.compile(r'[0-9a-f]{64}')
OLD_ARTIFACTS = frozenset((
    ('b8279ee1fedc4e26b7319b6777f6a413242cee0c36169a14195f5c24c44511e4', '873c47f7d75776d836f642a971164b8751c6a53d56430c3a84f0cf3c161b8f58', '5d3738c59d65fab74eb5da1991209481772123c0f583cd06de15e90135039dcc'),
    ('1a3f4628d4f63445ec0c1a212a38f1eb3ac01fe22ea2d5d2d54f0210f388fd14', 'a0702e4a971530b635a88e8a603145e77c08ee8d3eb56b4ba8fa00d62e99bdf1', '2fa6dd02e810905ecc98d760be68817927c04c6d3e61ad3f69015da6bf650c7f'),
    ('f9f48f4f8351654a2f2859eeda944ed144ba5c334f914b7f09bec14b0a5e4236', 'ccf610ca2e1fa48bfd2b3f7377791c8619d64de1097877d4f80123b303bd88a7', '781975d0f6867164d2be1cbc8da838034ed86db453a403414b020906b3ec1d8f'),
    ('27e625a7aa483448b9c6b9b258d1f8c4e45da99c2a41f9844c1afce3924fc526', 'c4c63cb3cfbf4ccdcab147136a7ecab755f895ca83ff8f01ade8404e0fffcf37', '625056b523700e9cd901aa4366ca1719b798739141863e7d199eb213ad4617a6')))


def read_document(path, expected):
    assert isinstance(expected, str) and SHA.fullmatch(expected), 'Explicit reviewed SHA required'
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), str(path)
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected, 'Hash before parsing authority'
    return json.loads(raw), raw


def load_authority(pin_path, pin_sha, review_path, review_sha):
    pins, pin_bytes = read_document(pin_path, pin_sha)
    assert isinstance(pins, dict) and pins['schemaVersion'] == 1
    assert pins['state'] == 'REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1'
    assert pins.get('diagnosticOnly', False) is False and 'internalTickDiagnosticPolicy' not in pins
    assert sorted(pins['variants']) == sorted(LABELS)
    for label in LABELS:
        pin = pins['variants'][label]
        assert isinstance(pin, dict), 'Four actual reviewed artifacts required'
        assert pin.get('diagnosticOnly', False) is False and 'internalTickDiagnosticPolicy' not in pin
        assert pin['state'] == 'reviewed-real-classic-trace-production-freeze'
        assert pin['variant'] == label and pin['sourceFiles'] == 342
        assert pin['recipeSha256'] == RECIPE and pin['sourceContractVersion'] == CONTRACT
        assert pin['classicTraceSourcePolicy']['version'] == CONTRACT
        assert pin['classicTraceSourcePolicy']['fixSourceIndexSha256'] == FIX
        assert tuple(pin[key] for key in ('engineSha256', 'receiptSha256', 'freezeReceiptSha256')) not in OLD_ARTIFACTS, 'Old artifact tuple is not trace authority'
        assert pin['classicStreamsEnabled'] is (label != 'disabled-off')
        assert pin['gcStress'] is (label == 'gc-off')
        assert pin['entropyPolicy'] == ('runtime-only' if label == 'normal-runtime' else 'off')
        for field in ('engineSha256', 'receiptSha256', 'cmakeCacheSha256', 'compileCommandsSha256',
                      'freezeReceiptSha256', 'parentEmbeddingCommandSha256'):
            assert isinstance(pin[field], str) and SHA.fullmatch(pin[field]), field
        assert type(pin['engineBytes']) is int and pin['engineBytes'] > 0
        assert pin['freezeRoot'] == str(FREEZE_ROOT)
        assert pin['enginePath'] == str(FREEZE_ROOT / (label + '.engine.wasm'))
        assert pin['sourceRoot'] == str(FREEZE_ROOT / 'source')
        assert pin['componentizeSourceRoot'] == str(FREEZE_ROOT / 'componentize-source')
        assert pin['freezeReceiptPath'] == str(FREEZE_ROOT / (label + '-freeze-receipt.json'))
    review, review_bytes = read_document(review_path, review_sha)
    assert review['schemaVersion'] == 1
    assert review['state'] == 'ROOT_REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1'
    assert review['reviewedPinsSha256'] == pin_sha
    assert review['sourceFiles'] == 342 and review['recipeSha256'] == RECIPE
    assert review['sourceContractVersion'] == CONTRACT
    assert review['sourcePolicySha256'] == POLICY and review['sourceHelperSha256'] == HELPER
    assert review['configuredSourceRoot'] == str(SOURCE_ROOT)
    assert sorted(review['labels']) == sorted(LABELS) and sorted(review['variants']) == sorted(LABELS)
    assert review['runtimeAcceptanceClaim'] is False
    for label in LABELS:
        row, pin = review['variants'][label], pins['variants'][label]
        for field in ('engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256'):
            assert row[field] == pin[field], label + '/' + field
        for field in ('independentProofIndexSha256', 'independentProofResultSha256'):
            assert isinstance(row[field], str) and SHA.fullmatch(row[field]), field
    return pins, pin_bytes, review, review_bytes
