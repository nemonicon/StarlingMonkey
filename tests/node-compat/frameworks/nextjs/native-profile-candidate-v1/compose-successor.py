"""Apply finite sealed replacements to an immutable native Source generation.

Source payload composition only; no engine metadata adaptation or execution.
Usage: BASE_DIRECTORY OUTPUT_DIRECTORY REPAIR_PACKET_DIRECTORY
"""
import hashlib
import json
import sys
from pathlib import Path

inputs = {}


def read(path, expected=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    raw = path.read_bytes()
    row = dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    if expected:
        assert row['sha256'] == expected['sha256'] and row['bytes'] == expected['bytes'], path
    if str(path) in inputs:
        assert inputs[str(path)] == row, path
    inputs[str(path)] = row
    return raw


def load(path, expected=None):
    return json.loads(read(path, expected))


assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
assert len(sys.argv) == 4
base, output, packet = map(Path, sys.argv[1:])
assert base.is_absolute() and output.is_absolute() and packet.is_absolute()
assert str(output).startswith('/private/tmp/starling-node-compat/next-native-profile-')
assert not output.exists() and base != output
read(Path(__file__).resolve())
composition = load(base / 'composition.json')
assert composition['engineBuilt'] is False and composition['guestExecuted'] is False
assert composition['legacyMetadataProjected'] is False
for row in composition['inputs']:
    read(row['path'], row)
source = base / 'source'
assert str(source) == composition['sourceRoot']
files, origins = {}, {}
for row in composition['files']:
    relative = row['path']
    assert not Path(relative).is_absolute() and '..' not in Path(relative).parts
    files[relative] = read(source / relative, row)
    origins[relative] = 'Immutable base Source: ' + str(source / relative)
assert set(files) == {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
assert not any(p.is_symlink() for p in source.rglob('*'))
index = load(packet / 'index.json')
assert set(r['path'] for r in index['files']) == {p.relative_to(packet).as_posix() for p in packet.rglob('*') if p.is_file() and p != packet / 'index.json'}
for row in index['files']:
    read(packet / row['path'], row)
mapping = load(packet / 'composer-mappings.json')
assert mapping['baseInstalledSourceRoot'] == str(source)
edits = []
for row in mapping['replacements']:
    path = row['target']
    assert path in files and row['newPath'] is False and row['kind'] == 'exact-file-replacement'
    assert hashlib.sha256(files[path]).hexdigest() == row['before']['sha256']
    data = read(row['after']['path'], row['after'])
    files[path] = data
    origins[path] = 'Sealed finite repair: ' + row['after']['path']
    edits.append(row)
assert len({r['target'] for r in mapping['replacements']}) == len(mapping['replacements'])
embedding = {p: read(base / 'componentize-source' / p) for p in ['CMakeLists.txt', 'embedding/embedding.cpp', 'embedding/embedding.h']}
for row in list(inputs.values()):
    read(row['path'], row)
output.mkdir(mode=0o700)
for path, raw in sorted(files.items()):
    target = output / 'source' / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    target.chmod(0o600)
for path, raw in embedding.items():
    target = output / 'componentize-source' / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    target.chmod(0o600)
result = dict(schemaVersion=1, state='NEXT_COMBINED_SOURCE_ONLY_NOT_BUILD_METADATA',
              sourceRoot=str(output / 'source'), nativeSourceFiles=len(files),
              baseSourceComposition=inputs[str(base / 'composition.json')],
              parentFrozenEngine=composition['parentFrozenEngine'],
              parentMetadata=composition['parentMetadata'],
              files=[dict(path=p, sha256=hashlib.sha256(b).hexdigest(), bytes=len(b), origin=origins[p]) for p, b in sorted(files.items())],
              inputs=list(inputs.values()), edits=edits, engineBuilt=False,
              guestExecuted=False, selectedManifestsMustBeDerivedFresh=True,
              legacyMetadataProjected=False)
(output / 'composition.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(state=result['state'], files=len(files), inputs=len(inputs), output=str(output))))
