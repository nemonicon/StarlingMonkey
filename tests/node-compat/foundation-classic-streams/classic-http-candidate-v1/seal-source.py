"""Seal this finite source proposal. No package/build/guest/host execution."""
from pathlib import Path
import hashlib
import json
import os

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REPLAY = HERE.parent / 'production-regression-candidate-v1'
RUNTIME = HERE.parent / 'production-runtime-activated-v2'
REPLAY_SHA = '81c55887dc5e767db27477ba28f0e7a26a948435c7ddc61c70da329d4bd7f029'
RUNTIME_SHA = '8a1b91e73475bfb007220704e08fbe68aa0b584851f70afad5607fd6c3a10d5a'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write_new(path, data):
    with path.open('xb') as stream:
        stream.write(data)

def encoded(document):
    return (json.dumps(document, indent=2) + '\n').encode()

def main():
    assert not (HERE / 'input-freeze.json').exists()
    source_rows = {}
    def add(path, expected=None, size=None):
        assert not Path(path).is_symlink(), path
        path = Path(path).resolve(strict=True)
        assert path.is_file() and not path.is_symlink()
        data = path.read_bytes()
        if expected is not None:
            assert sha(data) == expected, path
        if size is not None:
            assert len(data) == size, path
        boundary = REPO if path.is_relative_to(REPO) else Path('/private/tmp/starling-node-compat')
        assert path.is_relative_to(boundary) and path != boundary, path
        cursor = path
        while cursor != boundary:
            assert not cursor.is_symlink(), cursor
            cursor = cursor.parent
        row = {'path': os.path.relpath(path, HERE), 'sha256': sha(data), 'bytes': len(data),
               'boundary': os.path.relpath(boundary, HERE)}
        if path in source_rows:
            assert source_rows[path] == row
        source_rows[path] = row
    def indexed(root, expected):
        raw = (root / 'index.json').read_bytes()
        assert sha(raw) == expected
        add(root / 'index.json', expected)
        document = json.loads(raw)
        for row in document['files']:
            assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
            add(root / row['path'], row['sha256'], row['bytes'])
        return len(document['files'])
    replay_files = indexed(REPLAY, REPLAY_SHA)
    runtime_files = indexed(RUNTIME, RUNTIME_SHA)
    parent_manifests = []
    for manifest in [REPLAY / 'input-freeze.json', REPLAY / 'capability/input-freeze.json', RUNTIME / 'input-freeze.json']:
        raw = manifest.read_bytes()
        add(manifest)
        document = json.loads(raw)
        for row in document['inputs']:
            add(manifest.parent / row['path'], row['sha256'], row['bytes'])
        parent_manifests.append({'path': str(manifest.relative_to(REPO)), 'sha256': sha(raw), 'files': len(document['inputs'])})
    # Immutable previous responses are used ONLY as pure validator test data.
    fixture_root = Path('/tmp/starling-node-compat/production-scheduler-runtime-v1/http/http-joint')
    add(fixture_root / 'wasmtime-v1/wasmtime-results.json', '8856c0389de6bea514245cc8f5600356a341723c78b68cde1bc1b877b9648169')
    add(fixture_root / 'component-audit.json', 'e2d8a4732388c4e930877cb7666aa4ff65f19f6ae10dafecc3ffe7d5e3ca01fe')
    # Source packet membership is finite; evidence/history and rendered guard are
    # indexed separately. The guard authenticates its exact rendered template.
    for path in sorted(HERE.rglob('*')):
        if not path.is_file() or any(part in {'history', 'evidence', '__pycache__'} for part in path.relative_to(HERE).parts):
            continue
        if path.relative_to(HERE).as_posix() in {'capability/preflight.mjs', 'index.json', 'source-receipt.json', 'input-freeze.json'}:
            continue
        add(path)
    document = {'schemaVersion': 1, 'state': 'SEALED_CLASSIC_COMBINED_HTTP_SOURCE_INPUTS_ONLY',
                'replayIndexSha256': REPLAY_SHA, 'runtimeIndexSha256': RUNTIME_SHA,
                'parentManifests': parent_manifests, 'replayIndexedFiles': replay_files,
                'runtimeIndexedFiles': runtime_files, 'nativeSources': 342,
                'localComponentPinIsNullAndSealed': True, 'componentOrHostExecuted': False,
                'runtimeToolTreesAndLinksRecheckedByActualRuntimePreflight': True,
                'inputs': [source_rows[key] for key in sorted(source_rows)]}
    raw = encoded(document)
    template = (HERE / 'capability/preflight.template.mjs').read_text()
    assert template.count('@INPUTS_SHA@') == 1
    rendered = template.replace('@INPUTS_SHA@', sha(raw)).encode()
    # The old unsealed handoff guard is preserved in history before replacement.
    write_new(HERE / 'input-freeze.json', raw)
    (HERE / 'capability/preflight.mjs').write_bytes(rendered)
    print(json.dumps({'state': document['state'], 'sha256': sha(raw), 'inputs': len(source_rows),
                      'renderedPreflightSha256': sha(rendered)}))

if __name__ == '__main__':
    main()
