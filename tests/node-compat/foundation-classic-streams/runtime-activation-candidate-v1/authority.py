"""Pure authority parsing. No engine/tool imports or output creation."""
import hashlib
import json
from pathlib import Path
import re

RECIPE = '71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
LABELS = ('normal-off', 'normal-runtime', 'gc-off', 'disabled-off')
SHA = re.compile(r'[0-9a-f]{64}')

def read_document(path, expected):
    assert isinstance(expected, str) and SHA.fullmatch(expected), 'Explicit reviewed SHA-256 required'
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected, 'Document digest changed before parsing'
    return json.loads(data), data

def load_authority(pin_path, pin_sha, review_path, review_sha):
    pins, pin_bytes = read_document(pin_path, pin_sha)
    assert pins['schemaVersion'] == 1
    assert pins['state'] == 'REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1', 'Null/unreviewed exports cannot activate'
    assert sorted(pins['variants']) == sorted(LABELS)
    for label in LABELS:
        pin = pins['variants'][label]
        assert isinstance(pin, dict), 'All four actual reviewed pins are required'
        assert pin['state'] == 'reviewed-real-classic-production-freeze'
        assert pin['variant'] == label and pin['sourceFiles'] == 342 and pin['recipeSha256'] == RECIPE
        assert pin['classicStreamsEnabled'] is (label != 'disabled-off')
        assert pin['gcStress'] is (label == 'gc-off')
        assert pin['entropyPolicy'] == ('runtime-only' if label == 'normal-runtime' else 'off')
        for field in ('engineSha256', 'receiptSha256', 'cmakeCacheSha256', 'compileCommandsSha256', 'freezeReceiptSha256', 'parentEmbeddingCommandSha256'):
            assert isinstance(pin[field], str) and SHA.fullmatch(pin[field]), field
    review, review_bytes = read_document(review_path, review_sha)
    assert review['schemaVersion'] == 1
    assert review['state'] == 'ROOT_REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1'
    assert review['reviewedPinsSha256'] == pin_sha
    assert review['sourceFiles'] == 342 and review['recipeSha256'] == RECIPE
    assert sorted(review['labels']) == sorted(LABELS)
    assert sorted(review['variants']) == sorted(LABELS)
    assert review['runtimeAcceptanceClaim'] is False
    for label in LABELS:
        row, pin = review['variants'][label], pins['variants'][label]
        for field in ('engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256'):
            assert row[field] == pin[field], 'Root review/pin mismatch: ' + label + '/' + field
        for field in ('independentProofIndexSha256', 'independentProofResultSha256'):
            assert isinstance(row[field], str) and SHA.fullmatch(row[field]), field
    return pins, pin_bytes, review, review_bytes
