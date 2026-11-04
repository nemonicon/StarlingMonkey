"""Stdlib-only source/authority guard. Importing this file performs no action."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

ORIGINAL = Path('/Users/dan/dev/StarlingMonkey')
OWN = ORIGINAL / 'tests/node-compat/foundation-crypto/native-freezer-source-amendment-v1'
DONOR = ORIGINAL / 'tests/node-compat/foundation-crypto/native-integration-candidate-v2'
DONOR_SHA = '68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575'
CONFIGURED = Path('/private/tmp/starling-node-compat/crypto-owner-source-v2')
STAGED = CONFIGURED / 'tests/node-compat/foundation-crypto/native-integration-candidate-v2'
FROZEN = Path('/private/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')
ADMISSION_STATE = 'ACTUAL_FINITE_CRYPTO_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'
PEER_STATE = 'INDEPENDENT_CRYPTO_OWNER355_FREEZER_SOURCE_REVIEW_PASSED_V1'


def safe(relative):
    assert isinstance(relative, str) and relative and '\0' not in relative and '\\' not in relative
    assert not relative.startswith('/') and all(p not in ('', '.', '..') for p in relative.split('/'))
    return relative


def regular(path, expected=None, size=None):
    path = Path(path)
    assert path.is_absolute() and path == Path(os.path.abspath(path))
    # /tmp is accepted only through the fixed physical /private/tmp contexts.
    for parent in (path, *path.parents):
        assert not parent.is_symlink(), parent
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1, path
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_mode) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_mode)
    checksum = value.hexdigest()
    if expected is not None:
        assert re.fullmatch(r'[a-f0-9]{64}', expected) and checksum == expected, path
    if size is not None:
        assert type(size) is int and size >= 0 and before.st_size == size
    return {'path': str(path), 'sha256': checksum, 'bytes': before.st_size}


def descriptor(row):
    assert set(row) == {'path', 'sha256', 'bytes'}
    return regular(row['path'], row['sha256'], row['bytes'])


def indexed(index_descriptor):
    ix = descriptor(index_descriptor)
    data = json.loads(Path(ix['path']).read_bytes())
    base = Path(ix['path']).parent
    rows = [ix]
    seen = set()
    for row in data['files']:
        name = safe(row['path'])
        assert name not in seen
        seen.add(name)
        rows.append(regular(base / name, row['sha256'], row['bytes']))
    return data, rows


def validate_admission(value):
    assert value['state'] == ADMISSION_STATE
    assert value['sourceFiles'] == 355 and value['engineBytesRead'] is False


def validate_authority_data(authority, own_sha, peer):
    assert authority['schemaVersion'] == 1 and authority['state'] == 'ROOT_REVIEWED_CRYPTO_OWNER355_FREEZER_CORRECTION_V1'
    assert authority['amendmentSourceIndexSha256'] == own_sha
    assert authority['donorSourceIndexSha256'] == DONOR_SHA
    assert authority['configuredSourceRoot'] == str(CONFIGURED)
    assert authority['stagedArtifactToolsRoot'] == str(STAGED / 'artifact-tools')
    assert authority['freezeRoot'] == str(FROZEN)
    assert authority['freezeAllowed'] is True and authority['engineExecutionAllowed'] is False
    assert authority['operationalAdmission'] is False and authority['runtimeAcceptanceClaim'] is False
    assert authority['label'] in ('normal-off', 'normal-runtime', 'gc-off', 'disabled-off')
    assert peer['schemaVersion'] == 1 and peer['state'] == PEER_STATE
    assert peer['sourceIndexSha256'] == own_sha and peer['sourceOnly'] is True
    assert peer['sourceReviewPassed'] is True and peer['ownerActionsInvoked'] is False
    return authority['label']


def validate_receipt_roles(receipt, active_sha, donor_sha):
    inventory = {os.path.realpath(row['path']): row for row in receipt['copies']}
    assert len(inventory) == len(receipt['copies'])
    active, donor = receipt['activeFreezerTooling'], receipt['donorFreezerTooling']
    assert active['role'] == 'ACTUAL_ACTIVE_CORRECTED_FREEZER' and active['sha256'] == active_sha == receipt['helperSha256']
    assert donor['role'] == 'IMMUTABLE_STAGED_DONOR_DATA_NOT_ACTIVE' and donor['sha256'] == donor_sha
    assert active['path'] != donor['path'] and active_sha != donor_sha
    assert active['path'] == str(FROZEN / 'artifact-tools/freeze-engine.py')
    assert donor['path'] == str(FROZEN / 'artifact-tools/donor-data/freeze-engine.py')
    assert inventory[active['path']]['sha256'] == active_sha
    assert inventory[donor['path']]['sha256'] == donor_sha


def recheck(context):
    for row in context['captured']:
        descriptor(row)


def authorize(entry, args):
    assert __debug__ and len(args) == 2, 'OWN_INDEX_SHA EXACT_ROOT_AUTHORITY_DESCRIPTOR_JSON'
    assert Path(entry) == OWN / 'freeze-engine.py'
    assert sys.flags.isolated == 1, 'Use python3 -I; no caller import search path'
    for name in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE', 'NODE_OPTIONS', 'NODE_PATH'):
        assert not os.environ.get(name), name
    own_sha, authority_json = args
    own_descriptor = regular(OWN / 'index.json', own_sha)
    own, own_rows = indexed(own_descriptor)
    donor_descriptor = regular(DONOR / 'index.json', DONOR_SHA)
    donor, donor_rows = indexed(donor_descriptor)
    assert len(donor['files']) == 44
    authority_descriptor = descriptor(json.loads(authority_json))
    authority = json.loads(Path(authority_descriptor['path']).read_bytes())
    peer_pair = authority['independentSourceReview']
    peer_index, peer_rows = indexed(peer_pair['index'])
    peer_descriptor = descriptor(peer_pair['result'])
    assert sum(row == peer_descriptor for row in peer_rows[1:]) == 1
    peer = json.loads(Path(peer_descriptor['path']).read_bytes())
    label = validate_authority_data(authority, own_sha, peer)
    assert CONFIGURED.is_dir() and not CONFIGURED.is_symlink()
    staged_rows = [regular(STAGED / 'index.json', DONOR_SHA)]
    for row in donor['files']:
        staged_rows.append(regular(STAGED / safe(row['path']), row['sha256'], row['bytes']))
    pins_path = STAGED / 'artifact-tools/tool-pins.json'
    pins = json.loads(pins_path.read_bytes())
    assert pins['nativeSources'] == 355 and pins['reviewedEnginePins'] is None
    assert len(pins['toolDependencies']) == 922
    tool_rows = [regular(CONFIGURED / safe(row['path']), row['sha256'], row['bytes']) for row in pins['toolDependencies']]
    metadata_descriptor = descriptor(authority['metadata'])
    metadata = json.loads(Path(metadata_descriptor['path']).read_bytes())
    engine = authority['engine']
    assert set(engine) == {'path', 'sha256', 'bytes'}
    assert Path(engine['path']).is_absolute() and '\0' not in engine['path'] and '\\' not in engine['path']
    assert Path(engine['path']) == Path(os.path.abspath(engine['path']))
    assert metadata_descriptor['path'] == engine['path'] + '.build.json'
    assert metadata['engineSha256'] == engine['sha256'] and metadata['engineBytes'] == engine['bytes']
    assert metadata['buildRecipeSha256'] == pins['recipeSha256']
    assert not (FROZEN / (label + '-freeze-receipt.json')).exists()
    captured = own_rows + donor_rows + peer_rows + [authority_descriptor] + staged_rows + tool_rows + [metadata_descriptor]
    context = {'label': label, 'enginePath': engine['path'], 'metadata': metadata_descriptor,
               'configuredSourceRoot': str(CONFIGURED), 'artifactToolsRoot': str(STAGED / 'artifact-tools'),
               'freezeRoot': str(FROZEN), 'active': regular(entry),
               'donor': regular(STAGED / 'artifact-tools/freeze-engine.py'),
               'authority': authority_descriptor, 'peerIndex': peer_pair['index'], 'peerResult': peer_descriptor,
               'sourceIndex': own_descriptor, 'captured': captured,
               'capsules': own_rows + donor_rows + peer_rows + [authority_descriptor]}
    recheck(context)
    return context
