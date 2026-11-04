"""Future exclusive source stage only. No producer/SDK/crypto/helper is imported."""
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
DEST = Path('/tmp/starling-node-compat/crypto-owner-source-v1')
BASE_COMMIT = '54b3329b3ce818fd1f244e871e9c259b63667cda'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe(name):
    assert isinstance(name, str) and name and not name.startswith('/') and '\\' not in name and '\0' not in name
    assert all(p not in ('', '.', '..') for p in name.split('/'))
    return name


def checked(path, checksum, size=None):
    p = Path(path)
    s = p.lstat()
    assert stat.S_ISREG(s.st_mode) and not p.is_symlink(), p
    data = p.read_bytes()
    assert digest(data) == checksum and (size is None or len(data) == size), p
    return data


def collect(expected):
    own_raw = checked(HERE / 'index.json', expected)
    own = json.loads(own_raw)
    rows = {}

    def add(name, original, checksum, size, role):
        safe(name)
        raw = checked(original, checksum, size)
        row = {'path': name, 'original': str(original), 'sha256': checksum,
               'bytes': len(raw), 'sourceMode': stat.S_IMODE(Path(original).lstat().st_mode), 'roles': [role]}
        if name in rows:
            assert rows[name]['sha256'] == checksum and rows[name]['bytes'] == len(raw)
            rows[name]['roles'].append(role)
        else:
            rows[name] = row

    native = json.loads((HERE / 'native-origins.json').read_bytes())
    assert len(native['files']) == 355
    for row in native['files']:
        raw = checked(row['original'], row['sha256'])
        add(row['path'], row['original'], row['sha256'], len(raw), 'EXACT_NEW_NATIVE355')
    tools = json.loads((HERE / 'tool-origins.json').read_bytes())['files']
    pins = json.loads((HERE / 'artifact-tools/tool-pins.json').read_bytes())['toolDependencies']
    assert {r['path']: (r['sha256'], r['bytes']) for r in tools} == {r['path']: (r['sha256'], r['bytes']) for r in pins}
    for row in tools:
        add(row['path'], row['original'], row['sha256'], row['bytes'], 'PINNED_BUILD_TOOL_OR_SOURCE_ANCESTRY')
    prefix = str(HERE.relative_to(ORIGINAL))
    add(prefix + '/index.json', HERE / 'index.json', expected, len(own_raw), 'OWN_SOURCE_SEAL')
    for row in own['files']:
        add(prefix + '/' + safe(row['path']), HERE / row['path'], row['sha256'], row['bytes'], 'OWN_SOURCE_SEAL')
    return {'schemaVersion': 1, 'state': 'CRYPTO_OWNER355_EXACT_STAGE_INPUT_PLAN',
            'destination': str(DEST), 'baseCommit': BASE_COMMIT, 'nativeFiles': 355,
            'toolRows': len(tools), 'files': [rows[k] for k in sorted(rows)],
            'preparationManifestsInterpreted': False, 'stageExecuted': False}


def authority(descriptor, expected):
    review = json.loads(checked(descriptor['path'], descriptor['sha256'], descriptor['bytes']))
    assert review['schemaVersion'] == 1 and review['state'] == 'ROOT_REVIEWED_CRYPTO_OWNER355_SOURCE_STAGE_V1'
    assert review['sourceIndexSha256'] == expected and review['destination'] == str(DEST)
    assert review['sourceStageAllowed'] is True and review['nativeBuildOrRuntimeAllowed'] is False
    pair = review['independentSourceReview']
    ix = json.loads(checked(pair['index']['path'], pair['index']['sha256'], pair['index']['bytes']))
    result_raw = checked(pair['result']['path'], pair['result']['sha256'], pair['result']['bytes'])
    root = Path(pair['index']['path']).parent
    hits = 0
    for row in ix['files']:
        path = root / safe(row['path'])
        checked(path, row['sha256'], row['bytes'])
        if path == Path(pair['result']['path']):
            assert row['sha256'] == pair['result']['sha256'] and row['bytes'] == pair['result']['bytes']
            hits += 1
    assert hits == 1
    result = json.loads(result_raw)
    assert result['schemaVersion'] == 1 and result['state'] == 'INDEPENDENT_CRYPTO_OWNER355_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V1'
    assert result['sourceIndexSha256'] == expected and result['sourceOnly'] is True
    assert result['sourceReviewPassed'] is True and result['ownerActionsInvoked'] is False
    return review


def main():
    assert __debug__ and len(sys.argv) == 3, 'OWN_SOURCE_INDEX_SHA EXACT_ROOT_STAGE_AUTHORITY_DESCRIPTOR_JSON'
    assert HERE == ORIGINAL / 'tests/node-compat/foundation-crypto/native-integration-candidate-v1'
    expected = sys.argv[1]
    assert len(expected) == 64
    descriptor = json.loads(sys.argv[2])
    authority(descriptor, expected)  # Exact Root/peer authority before any output.
    plan = collect(expected)
    assert not DEST.exists() and not DEST.is_symlink()
    assert shutil.disk_usage(DEST.parent).free >= 2 * 1024 ** 3
    journal = DEST.parent / 'crypto-owner-source-v1-publication.json'
    assert not journal.exists() and not journal.is_symlink()
    result = {'schemaVersion': 1, 'state': 'SOURCE_STAGE_STARTED', 'sourceIndexSha256': expected,
              'destination': str(DEST), 'nativeBuildOrCryptoOrGuestExecuted': False, 'commands': []}
    try:
        for command in [['git', 'clone', '--no-local', '--no-checkout', str(ORIGINAL), str(DEST)],
                        ['git', '-C', str(DEST), 'checkout', '--detach', BASE_COMMIT]]:
            process = subprocess.run(command, capture_output=True, timeout=120)
            result['commands'].append({'argv': command, 'returncode': process.returncode,
                                       'stdout': process.stdout.decode(), 'stderr': process.stderr.decode()})
            assert process.returncode == 0
        assert not (DEST / '.git/objects/info/alternates').exists()
        for row in plan['files']:
            data = checked(row['original'], row['sha256'], row['bytes'])
            assert stat.S_IMODE(Path(row['original']).lstat().st_mode) == row['sourceMode']
            target = DEST
            for part in row['path'].split('/'):
                target /= part
                assert not target.is_symlink()
            target.parent.mkdir(parents=True, exist_ok=True)
            # Existing files belong exclusively to the new clone; originals are
            # never modified, redirected or used as writable destinations.
            with target.open('wb' if target.exists() else 'xb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            target.chmod(row['sourceMode'])
            checked(target, row['sha256'], row['bytes'])
        after = collect(expected)
        assert plan == after
        authority(descriptor, expected)
        for row in plan['files']:
            checked(DEST / row['path'], row['sha256'], row['bytes'])
        result.update(state='NEW_CRYPTO_OWNER355_SOURCE_STAGED_NOT_BUILT', files=len(plan['files']),
                      nativeFiles=355, toolRows=plan['toolRows'], metadataProjected=False,
                      preparationManifestsInterpreted=False, operationalAdmission=False)
    except BaseException as error:
        result.update(state='SOURCE_STAGE_FAILED_OR_PARTIAL_RETAINED', errorType=type(error).__name__)
        raise
    finally:
        with journal.open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
