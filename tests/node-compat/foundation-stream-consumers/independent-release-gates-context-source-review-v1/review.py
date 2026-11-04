"""Root independent source/context DATA review. Never imports owner code."""
from pathlib import Path
import hashlib, json, stat

HERE = Path(__file__).resolve().parent
OWNER = HERE.parent / 'release-gates-context-amendment-v1'
BASE = HERE.parent / 'release-gates-candidate-v1'
cache, observed = {}, {}
sha = lambda b: hashlib.sha256(b).hexdigest()
load = lambda p: json.loads(p.read_bytes())

def check(path, expected, size=None):
    p = Path(path)
    assert p.is_absolute() and not p.is_symlink(), p
    before = p.stat()
    assert stat.S_ISREG(before.st_mode), p
    key = (before.st_dev, before.st_ino, before.st_size,
           before.st_mtime_ns, before.st_ctime_ns)
    if key not in cache:
        h = hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''):
                h.update(block)
        after = p.stat()
        assert key == (after.st_dev, after.st_ino, after.st_size,
                       after.st_mtime_ns, after.st_ctime_ns), p
        cache[key] = h.hexdigest()
    assert cache[key] == expected and (size is None or before.st_size == size), p
    observed[str(p)] = {'path': str(p), 'sha256': expected, 'bytes': before.st_size}

def indexed(root, expected):
    check(root / 'index.json', expected)
    x = load(root / 'index.json')
    for row in x['files']:
        assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
        check(root / row['path'], row['sha256'], row['bytes'])
    return x

own = indexed(OWNER, '9080e48fbccaf74835bfb8c8ef54c91b8df54ff5eb6e4c2cdc1c83443ad79b70')
base = indexed(BASE, 'a74dc603f7e42384892c9f4b69a2ba131a87a80daa38da19e91bbc2c099e5372')
refs = load(OWNER / 'input-freeze.json')['files']
base_refs = load(BASE / 'source-inputs.preparation.json')['files']
for row in refs + base_refs:
    check(row['path'], row['sha256'], row['bytes'])

delta = load(OWNER / 'derivations.json')
before = (BASE / 'native-preflight.template.mjs').read_text()
after = (OWNER / 'native-preflight.template.after.mjs').read_text()
current = before
for row in delta['edits']:
    assert current.count(row['before']) == 1
    current = current.replace(row['before'], row['after'], 1)
assert current == after
for row in reversed(delta['edits']):
    assert current.count(row['after']) == 1
    current = current.replace(row['after'], row['before'], 1)
assert current == before
old_runner = (BASE / 'run-gates.mjs').read_text()
new_runner = (OWNER / 'run-gates.after.mjs').read_text()
assert old_runner.replace('production-consumers355-release-gates-v1/',
                          'production-consumers355-release-gates-v2/') == new_runner
context = load(BASE / 'context.json')
manifest = load(BASE / 'lineage.json')['native355']
for row in manifest:
    for key in ['nativeConfiguredSourceRoot', 'nativeFrozenSourceRoot']:
        check(Path(context[key]) / row['path'], row['sha256'])
assert not (Path(context['nativeFrozenSourceRoot']) / 'tests').exists()
assert (Path(context['nativeConfiguredSourceRoot']) / 'tests').is_dir()
graph = load(OWNER / 'selected-closure.after.json')
assert len(graph['localModulesAndData']) == 103 and len(graph['localEdges']) == 196
for row in list(observed.values()):
    check(row['path'], row['sha256'], row['bytes'])

result = {'schemaVersion': 1, 'state': 'INDEPENDENT_CONTEXT_AMENDMENT_DATA_CHECKS_PASSED',
          'indexedFiles': len(own['files']), 'parentIndexedFiles': len(base['files']),
          'amendmentReferences': len(refs), 'parentPreparationReferences': len(base_refs),
          'observedPaths': len(observed), 'uniquePhysicalHashReads': len(cache),
          'exactReversibleTemplateEdits': len(delta['edits']),
          'bothActualNativeRootsHashMatched': len(manifest),
          'frozenMissingToolsCounterexamplePreserved': True,
          'ownerPublisherHelperPreflightCompilerGuestOrRuntimeInvoked': False}
for name, value in [('data-results.json', result),
                    ('rehashed-files.json', {'schemaVersion': 1, 'files': list(observed.values())})]:
    with (HERE / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
print(json.dumps(result))
