"""Pure finite authority validation; no output, runner or tool imports."""
from pathlib import Path
import hashlib
import json
import re

PINS_SHA = 'c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e'
REVIEW_SHA = '1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56'
RECIPE = '71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
LABELS = ('normal-off', 'normal-runtime', 'gc-off', 'disabled-off')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def regular(path, expected=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    if expected is not None:
        assert re.fullmatch('[0-9a-f]{64}', expected) and expected != '0' * 64
        assert sha(data) == expected, 'SHA mismatch before JSON parsing: ' + str(path)
    return data


def relative(name):
    assert isinstance(name, str) and name and '\\' not in name and '\0' not in name
    assert not Path(name).is_absolute() and all(part not in ('', '.', '..') for part in name.split('/'))
    return name


def validate_authority(pin_bytes, review_bytes):
    assert sha(pin_bytes) == PINS_SHA and sha(review_bytes) == REVIEW_SHA
    pins, review = json.loads(pin_bytes), json.loads(review_bytes)
    assert pins['schemaVersion'] == review['schemaVersion'] == 1
    assert pins['state'] == 'REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1'
    assert review['state'] == 'ROOT_REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1'
    assert review['reviewedPinsSha256'] == PINS_SHA and review['recipeSha256'] == RECIPE
    assert review['sourceFiles'] == 342 and review['runtimeAcceptanceClaim'] is False
    assert sorted(pins['variants']) == sorted(review['variants']) == sorted(review['labels']) == sorted(LABELS)
    for label in LABELS:
        pin, row = pins['variants'][label], review['variants'][label]
        assert pin['state'] == 'reviewed-real-classic-production-freeze'
        assert pin['variant'] == label and pin['sourceFiles'] == 342 and pin['recipeSha256'] == RECIPE
        assert pin['classicStreamsEnabled'] is (label != 'disabled-off') and pin['gcStress'] is (label == 'gc-off')
        assert pin['entropyPolicy'] == ('runtime-only' if label == 'normal-runtime' else 'off')
        assert len(pin['frozenFiles']) == 405
        for name in ('engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256'):
            assert pin[name] == row[name], label + '/' + name
    return pins, review


def indexed(root, expected):
    root = Path(root)
    assert root.is_dir() and not root.is_symlink(), root
    raw = regular(root / 'index.json', expected)
    document = json.loads(raw)
    assert document['schemaVersion'] == 1
    rows = document['files']
    assert isinstance(rows, list) and len(rows) == len({row['path'] for row in rows})
    for row in rows:
        path = root
        for part in relative(row['path']).split('/'):
            path /= part
            assert not path.is_symlink(), path
        assert len(regular(path, row['sha256'])) == row['bytes']
    return document, raw


def validate_runtime_receipt(index, receipt, pins, review):
    assert index['state'] == 'ACTUAL_REVIEWED_CLASSIC_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED'
    assert index['runtimeAcceptanceClaim'] is False
    assert receipt['schemaVersion'] == 1 and receipt['state'] == 'ACTUAL_REVIEWED_CLASSIC_RUNTIME_FAMILY_CREATED_NOT_EXECUTED'
    assert receipt['pinsSha256'] == PINS_SHA and receipt['rootReviewSha256'] == REVIEW_SHA
    assert receipt['recipeSha256'] == RECIPE and receipt['engineMetadataRewritten'] is False
    assert receipt['componentOrHostExecuted'] is False and receipt['runtimeAcceptanceClaim'] is False
    assert set(receipt['actualArtifacts']) == set(LABELS)
    for label in LABELS:
        assert receipt['actualArtifacts'][label] == {name: pins['variants'][label][name]
            for name in ('engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256')}
    names = {row['path'] for row in index['files']}
    assert {'runtime-preflight.mjs', 'runtime-pins.json', 'root-review-receipt.json', 'input-freeze.json', 'source-receipt.json'} <= names
    return True
