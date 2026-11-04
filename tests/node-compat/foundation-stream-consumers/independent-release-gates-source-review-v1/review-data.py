"""Root independent read/hash review; never imports or calls owner code."""
from pathlib import Path
import difflib, hashlib, json, os, stat

HERE = Path(__file__).resolve().parent
OWNER = HERE.parent / 'release-gates-candidate-v1'
EXPECTED = 'a74dc603f7e42384892c9f4b69a2ba131a87a80daa38da19e91bbc2c099e5372'
cache = {}
observed = {}

def digest(value):
    return hashlib.sha256(value).hexdigest()

def stable(path, expected=None, size=None):
    p = Path(path)
    assert p.is_absolute() and not p.is_symlink(), p
    before = p.stat()
    assert stat.S_ISREG(before.st_mode), p
    identity = (before.st_dev, before.st_ino, before.st_size,
                before.st_mtime_ns, before.st_ctime_ns)
    if identity not in cache:
        h = hashlib.sha256()
        with p.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(block)
        after = p.stat()
        assert identity == (after.st_dev, after.st_ino, after.st_size,
                            after.st_mtime_ns, after.st_ctime_ns), p
        cache[identity] = h.hexdigest()
    sha = cache[identity]
    assert expected is None or sha == expected, p
    assert size is None or before.st_size == size, p
    row = {'path': str(p), 'sha256': sha, 'bytes': before.st_size}
    observed[str(p)] = row
    return row

def load(path):
    return json.loads(Path(path).read_bytes())

index = load(OWNER / 'index.json')
stable(OWNER / 'index.json', EXPECTED)
for row in index['files']:
    name = Path(row['path'])
    assert not name.is_absolute() and '..' not in name.parts
    stable(OWNER / name, row['sha256'], row['bytes'])
prep = load(OWNER / 'source-inputs.preparation.json')['files']
for row in prep:
    stable(row['path'], row['sha256'], row['bytes'])

lineage = load(OWNER / 'lineage.json')
for row in lineage['native355']:
    stable(OWNER / 'snapshot' / row['path'], row['sha256'])
for a, b, changes, added in [
    ('native306', 'native342', 'delta342', 'added342'),
    ('native342', 'native350', 'delta350', 'added350'),
    ('native350', 'native355', 'delta355', 'added355'),
]:
    old = {r['path']: r['sha256'] for r in lineage[a]}
    new = {r['path']: r['sha256'] for r in lineage[b]}
    delta = {r['path']: r for r in lineage[changes]}
    assert set(new) == set(old) | set(lineage[added])
    for name, sha in old.items():
        if name in delta:
            assert delta[name]['beforeSha256'] == sha
            assert delta[name]['afterSha256'] == new[name]
        else:
            assert new[name] == sha

edits = load(OWNER / 'afterimage-proof.json')['edits']
current = {}
diffs = []
for row in reversed(edits):
    name = row['path']
    after = current.get(name, (OWNER / 'snapshot' / name).read_bytes())
    before = (OWNER / row['preimage']).read_bytes()
    assert digest(after) == row['afterSha256'] and len(after) == row['afterBytes']
    assert digest(before) == row['beforeSha256'] and len(before) == row['beforeBytes']
    diffs.append(''.join(difflib.unified_diff(before.decode().splitlines(True),
                 after.decode().splitlines(True), fromfile=row['preimage'],
                 tofile='snapshot/' + name)))
    current[name] = before

audit = load(OWNER / 'inherited-body-audit.json')
for row in audit['unchangedCaseOracleFixtureData']:
    stable(OWNER / 'snapshot' / row['path'], row['sha256'], row['bytes'])
assert len(current) == 20 and len(edits) == 23
for path, row in observed.items():
    stable(path, row['sha256'], row['bytes'])

def write(name, value):
    with (HERE / name).open('x') as stream:
        if isinstance(value, str):
            stream.write(value)
        else:
            json.dump(value, stream, indent=2)
            stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())

write('host-edits.diff', '\n'.join(reversed(diffs)))
write('rehashed-files.json', {'schemaVersion': 1, 'files': list(observed.values())})
write('data-results.json', {
    'schemaVersion': 1,
    'state': 'ROOT_INDEPENDENT_RELEASE_GATES_DATA_REVIEW_ONLY_PASSED',
    'proposalIndexSha256': EXPECTED,
    'indexedFiles': len(index['files']), 'preparationRows': len(prep),
    'uniquePhysicalHashReads': len(cache), 'observedPaths': len(observed),
    'native355Unchanged': True, 'exactReverseEdits': len(edits),
    'hostAfterimagePaths': len(current),
    'unchangedCaseOracleFixtureFiles': len(audit['unchangedCaseOracleFixtureData']),
    'sourceManualReviewComplete': False,
    'ownerModulePublisherPreflightCompilerGuestOrRuntimeInvoked': False,
    'actionsApproved': False,
})
print(json.dumps({'dataChecksPassed': True, 'indexedFiles': len(index['files']),
                  'preparationRows': len(prep), 'observedPaths': len(observed)}))
