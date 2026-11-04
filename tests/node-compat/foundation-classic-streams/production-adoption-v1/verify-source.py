"""Root read-only verification of the frozen classic342 source proposal."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PACKET = HERE.parent / 'integration-candidate-v1'
EXPECTED_INDEX = '5826a3dfc8d79ebbbbd139665dd06f9f493af3aa6f48302f2865611591fcff6d'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def check(path, digest, size=None):
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    assert sha(data) == digest, path
    assert size is None or len(data) == size, path
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output')
    parser.add_argument('--installed', action='store_true')
    args = parser.parse_args()
    index = json.loads(check(PACKET/'index.json', EXPECTED_INDEX))
    for row in index['files']:
        check(PACKET/row['path'], row['sha256'], row['bytes'])
    inputs = json.loads((PACKET/'input-freeze.json').read_bytes())['inputs']
    for row in inputs:
        check(PACKET/row['path'], row['sha256'], row['bytes'])
    policy = json.loads((PACKET/'policy.json').read_bytes())
    patch_files = json.loads((PACKET/'patch-files.json').read_bytes())['files']
    assert len(patch_files) == 41
    for row in patch_files:
        check(PACKET/'source'/row['path'], row['afterSha256'], row['bytes'])
        path = REPO/row['path']
        if args.installed:
            check(path, row['afterSha256'], row['bytes'])
        elif row['beforeSha256'] is None:
            assert not path.exists(), path
        else:
            check(path, row['beforeSha256'])
    manifest = policy['expectedNativeSourceManifest'] if args.installed else policy['parentExpectedNativeSourceManifest']
    assert len(manifest) == (342 if args.installed else 306)
    for row in manifest:
        check(REPO/row['path'], row['sha256'])
    pins = json.loads((PACKET/'runtime-pins.json').read_bytes())
    assert set(pins['variants']) == {'normal-off', 'normal-runtime', 'gc-off', 'disabled-off'}
    assert all(value is None for value in pins['variants'].values())
    result = {
        'state': 'ROOT_CLASSIC342_INSTALLED_SOURCE_VERIFIED' if args.installed else 'ROOT_CLASSIC342_UNAPPLIED_SOURCE_VERIFIED',
        'checkedAtUtc': datetime.now(timezone.utc).isoformat(),
        'indexSha256': EXPECTED_INDEX, 'indexedFiles': len(index['files']),
        'inputFiles': len(inputs), 'productionPaths': len(patch_files),
        'liveNativeInputs': len(manifest), 'allRuntimePinsNull': True,
        'nativeBuildPerformed': False, 'guestPerformed': False,
        'sourceOnly': True,
    }
    with Path(args.output).open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
