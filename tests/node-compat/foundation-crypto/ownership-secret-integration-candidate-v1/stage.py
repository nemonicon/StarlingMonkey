"""Dormant source publisher derived from the parent355 stage's actual operations.

Standard-library bootstrap only. No native/helper/recipe/build API is imported.
The action entry is not invoked in source preparation.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ORIGINAL = Path('/Users/dan/dev/StarlingMonkey')
DEST = Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source')
WORK = Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build')
FREEZE = Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze')
JOURNAL = DEST.parent / 'crypto-owner355-secret-v1-stage.json'
BASE = '54b3329b3ce818fd1f244e871e9c259b63667cda'
PEER_STATE = 'INDEPENDENT_CRYPTO_OWNER355_SECRET_INTEGRATION_SOURCE_REVIEW_PASSED_V1'


def safe(name):
    assert isinstance(name, str) and name and not name.startswith('/')
    assert '\\' not in name and '\0' not in name and all(p not in ('', '.', '..') for p in name.split('/'))
    return name


def regular(row):
    path = Path(row['path'])
    assert path.is_absolute() and '..' not in path.parts
    if str(path).startswith('/tmp/'):
        path = Path('/private' + str(path))
    for p in (path, *path.parents):
        assert not p.is_symlink(), p
    before = path.stat()
    assert stat.S_ISREG(before.st_mode) and before.st_size == row['bytes']
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    assert h.hexdigest() == row['sha256'], path
    return path


def read(row):
    path = regular(row)
    assert row['bytes'] <= 32 * 1024 * 1024
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    return json.loads(raw)


def indexed(row):
    value = read(row)
    base = Path(row['path']).parent
    rows, names = [row], set()
    for entry in value['files']:
        name = safe(entry['path'])
        assert name not in names
        names.add(name)
        d = dict(path=str(base / name), sha256=entry['sha256'], bytes=entry['bytes'])
        regular(d)
        rows.append(d)
    actual = set()
    for path in base.rglob('*'):
        assert not path.is_symlink()
        if path.is_file():
            actual.add(str(path.relative_to(base)))
    assert actual == names | {'index.json'}, (actual - names, names - actual)
    return value, rows


def authority_model(root, expected, payload_peer):
    """Pure model; an unissued template with NULLs cannot pass this gate."""
    assert root['schemaVersion'] == 1 and root['state'] == 'ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_SOURCE_STAGE_V1'
    assert root['sourceIndexSha256'] == expected and root['destination'] == str(DEST)
    assert root['workRoot'] == str(WORK) and root['freezeRoot'] == str(FREEZE)
    assert root['sourceStageAllowed'] is True
    for key in ['nativeBuildAllowed','freezeAllowed','engineExecutionAllowed','keyOperationsAllowed',
                'guestAllowed','gcAllowed','operationalAdmission','runtimeAcceptanceClaim','pinsAdopted']:
        assert root[key] is False
    assert root['payloadSourceReview'] == payload_peer
    assert isinstance(root['independentSourceReview'], dict)
    return True


def authorize(descriptor, expected, refs):
    root = read(descriptor)
    authority_model(root, expected, refs['sourcePeer'])
    pair = root['independentSourceReview']
    _, rows = indexed(pair['index'])
    assert sum(row == pair['result'] for row in rows[1:]) == 1
    result = read(pair['result'])
    assert result['schemaVersion'] == 1 and result['state'] == PEER_STATE
    assert result['sourceIndexSha256'] == expected and result['sourceOnly'] is True
    assert result['sourceReviewPassed'] is True and result['ownerActionsInvoked'] is False
    return root


def normal_protection(refs):
    value = read(refs['normalProtection'])
    assert value['originalReferenceEntries'] == 1387 and len(value['requiredNormalFreezeMembership']) == 1391
    regular(value['freezeReceipt'])
    for row in value['frozenCopyEntries']:
        regular(row)
    for row in value['originals']:
        regular(row['original'])
        regular(row['frozen'])
    root = Path(value['freezeReceipt']['path']).parent
    actual = set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():
            actual.add(str(p.relative_to(root)))
    assert actual == set(value['requiredNormalFreezeMembership'])
    return True


def inputs(expected):
    own = dict(path=str(HERE/'index.json'), sha256=expected, bytes=(HERE/'index.json').stat().st_size)
    _, own_rows = indexed(own)  # Entire own family before reading any action input.
    refs = json.loads((HERE/'references.json').read_bytes())
    for family in refs['families']:
        indexed(family['index'])
    regular(refs['mandatoryHistoryErratum'])
    normal_protection(refs)
    rows = {}
    def add(relative, original, checksum, size, role):
        safe(relative)
        d = dict(path=original, sha256=checksum, bytes=size)
        p = regular(d)
        row = dict(path=relative, original=str(p), sha256=checksum, bytes=size,
                   sourceMode=stat.S_IMODE(p.stat().st_mode), roles=[role])
        if relative in rows:
            assert all(rows[relative][k] == row[k] for k in ['sha256','bytes','sourceMode'])
            rows[relative]['roles'].append(role)
        else:
            rows[relative] = row
    native = json.loads((HERE/'native-origins.json').read_bytes())['files']
    assert len(native) == 355
    for row in native:
        add(row['path'], row['original'], row['sha256'], row['bytes'], 'EXACT_SECRET_NATIVE355')
    for row in json.loads((HERE/'tool-origins.json').read_bytes())['files']:
        add(row['path'], row['original'], row['sha256'], row['bytes'], 'AUTHENTICATED_TOOL_OR_ANCESTRY')
    for row in own_rows:
        add(str(Path(row['path']).relative_to(ORIGINAL)), row['path'], row['sha256'], row['bytes'], 'OWN_SOURCE_SEAL')
    return refs, [rows[k] for k in sorted(rows)]


def main():
    assert __debug__ and len(sys.argv) == 3, 'OWN_INDEX_SHA EXACT_ROOT_STAGE_AUTHORITY_DESCRIPTOR_JSON'
    assert HERE == ORIGINAL/'tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1'
    expected = sys.argv[1]
    assert len(expected) == 64 and all(c in '0123456789abcdef' for c in expected)
    descriptor = json.loads(sys.argv[2])
    refs, rows = inputs(expected)
    authorize(descriptor, expected, refs)  # Before any output or Git call.
    for path in [DEST, WORK, FREEZE, JOURNAL]:
        assert not path.exists() and not path.is_symlink(), path
    assert shutil.disk_usage(DEST.parent).free >= 2 * 1024**3
    result = dict(schemaVersion=1, state='SECRET_SOURCE_STAGE_STARTED', sourceIndexSha256=expected,
        configuredSourceRoot=str(DEST), workRoot=str(WORK), freezeRoot=str(FREEZE), commands=[],
        nativeBuildExecuted=False, engineExecuted=False, operationalAdmission=False)
    try:
        for command in [['git','clone','--no-local','--no-checkout',str(ORIGINAL),str(DEST)],
                        ['git','-C',str(DEST),'checkout','--detach',BASE]]:
            process = subprocess.run(command, capture_output=True, timeout=120)
            result['commands'].append(dict(argv=command, returncode=process.returncode,
                stdout=process.stdout.decode('utf-8'), stderr=process.stderr.decode('utf-8')))
            assert process.returncode == 0
        assert not (DEST/'.git/objects/info/alternates').exists()
        for row in rows:
            p = regular(dict(path=row['original'], sha256=row['sha256'], bytes=row['bytes']))
            assert stat.S_IMODE(p.stat().st_mode) == row['sourceMode']
            target = DEST
            for part in row['path'].split('/'):
                target /= part
                assert not target.is_symlink()
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('wb' if target.exists() else 'xb') as stream:
                stream.write(p.read_bytes())
                stream.flush()
                os.fsync(stream.fileno())
            target.chmod(row['sourceMode'])
            assert target.stat().st_ino != p.stat().st_ino or target.stat().st_dev != p.stat().st_dev
            regular(dict(path=str(target), sha256=row['sha256'], bytes=row['bytes']))
        after_refs, after_rows = inputs(expected)
        assert after_refs == refs and after_rows == rows
        authorize(descriptor, expected, refs)
        result.update(state='SECRET_NATIVE355_SOURCE_STAGED_NOT_BUILT', copies=rows,
                      nativeSourceFiles=355, metadataProjected=False)
    except BaseException as error:
        result.update(state='SECRET_SOURCE_STAGE_FAILED_OR_PARTIAL_RETAINED', errorType=type(error).__name__)
        try:
            after_refs, after_rows = inputs(expected)
            assert after_refs == refs and after_rows == rows
            authorize(descriptor, expected, refs)
            result['failureInputRecheckPassed'] = True
        except BaseException as recheck:
            result['failureInputRecheckPassed'] = False
            result['failureInputRecheckError'] = type(recheck).__name__
        raise
    finally:
        with JOURNAL.open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
