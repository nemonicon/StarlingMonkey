"""Additional independent physical membership/provenance checks; no owner imports."""
from pathlib import Path
import hashlib, json, os, stat

HERE = Path(__file__).resolve().parent
OWNER = HERE.parent / 'release-gates-candidate-v1'
load = lambda name: json.loads((OWNER / name).read_bytes())
digest = lambda raw: hashlib.sha256(raw).hexdigest()
origins = load('snapshot-origins.json')['files']
edits = load('afterimage-proof.json')['edits']
first, last = {}, {}
for row in edits:
    first.setdefault(row['path'], row)
    last[row['path']] = row
for row in origins:
    name = row['relativePath']
    raw = (OWNER / 'snapshot' / name).read_bytes()
    assert digest(raw) == (last[name]['afterSha256'] if name in last else row['sha256'])
    original = Path(row['originalPath']).read_bytes()
    assert digest(original) == row['sha256'] and len(original) == row['bytes']
    if name in first:
        assert first[name]['beforeSha256'] == row['sha256']
assert len(origins) == 1677 and len(last) == 20
actual = set(str(p.relative_to(OWNER / 'snapshot')) for p in (OWNER / 'snapshot').rglob('*') if p.is_file())
assert actual == {r['relativePath'] for r in origins}

tools = load('tool-context.json')
for tree in tools['toolTrees']:
    root = Path(tree['path'])
    assert str(root.resolve()) == tree['realPath']
    found = []
    for base, ds, ns in os.walk(root, followlinks=False):
        for name in ds + ns:
            p = Path(base) / name
            s = p.lstat()
            kind = 'symlink' if stat.S_ISLNK(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'file' if stat.S_ISREG(s.st_mode) else None
            assert kind is not None
            found.append({'path': str(p.relative_to(root)), 'kind': kind})
    assert sorted(found, key=lambda r: r['path']) == tree['entries']
for row in tools['toolLinks']:
    p = Path(row['path'])
    assert p.is_symlink() and os.readlink(p) == row['linkText']
    assert str(p.resolve()) == row['resolvedTarget']
    assert any(p.resolve().is_relative_to(Path(t['realPath'])) for t in tools['toolTrees'])
    if row['targetKind'] == 'file':
        raw = p.read_bytes()
        assert digest(raw) == row['targetSha256'] and len(raw) == row['targetBytes']

graph = load('selected-closure.json')
for row in graph['localModulesAndData']:
    p = OWNER / row['path']
    raw = p.read_bytes()
    assert digest(raw) == row['sha256'] and len(raw) == row['bytes']
for row in graph['localEdges']:
    assert (OWNER / row['importer']).parent.joinpath(row['request']).resolve() == (OWNER / row['target']).resolve()
result = {'schemaVersion': 1, 'state': 'INDEPENDENT_PHYSICAL_PROVENANCE_CHECKS_PASSED',
          'snapshotOrigins': len(origins), 'unchangedOrigins': len(origins) - len(last),
          'physicalToolTrees': len(tools['toolTrees']), 'toolLinks': len(tools['toolLinks']),
          'localModulesAndData': len(graph['localModulesAndData']),
          'localEdges': len(graph['localEdges']), 'ownerActionsInvoked': False}
with (HERE / 'extra-results.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps(result))
