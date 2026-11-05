"""Independent read/hash, AST and pure DATA review; no owner module imports."""
from pathlib import Path
import ast
import hashlib
import json
import os

REPO = Path('/Users/dan/dev/StarlingMonkey')
HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'ownership-gc-native-candidate-v1'
EXPECTED = '2fbc01ad04c38057b65a26f33c7afa8683022ee62c020202b9c64ac7105a605a'
seen = {}


def physical(path):
    value = str(path)
    return Path('/private' + value if value.startswith('/tmp/') else value)


def checked(row):
    path = physical(row['path'])
    assert path.is_absolute() and '..' not in path.parts
    for parent in (path, *path.parents):
        assert not parent.is_symlink(), str(parent)
    before = path.stat()
    assert path.is_file()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    assert before.st_size == row['bytes'] and digest.hexdigest() == row['sha256'], str(path)
    key = str(path)
    value = dict(path=key, sha256=digest.hexdigest(), bytes=before.st_size)
    assert key not in seen or seen[key] == value
    seen[key] = value
    return path


def descriptor(path):
    data = Path(path).read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def walk(value):
    if isinstance(value, dict):
        if {'path', 'sha256', 'bytes'} <= value.keys() and isinstance(value['path'], str) and value['path'].startswith('/'):
            checked(value)
        for child in value.values():
            walk(child)
    elif isinstance(value, list):
        for child in value:
            walk(child)


def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


index_row = descriptor(SOURCE / 'index.json')
assert index_row['sha256'] == EXPECTED
checked(index_row)
index = json.loads((SOURCE / 'index.json').read_bytes())
assert len(index['files']) == 39
names = {row['path'] for row in index['files']}
assert len(names) == 39
assert {p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob('*') if p.is_file()} == names | {'index.json'}
documents = {}
for row in index['files']:
    checked({**row, 'path': str(SOURCE / row['path'])})
    if row['path'].endswith('.json'):
        value = json.loads((SOURCE / row['path']).read_bytes())
        documents[row['path']] = value
        walk(value)

staging = documents['stage-inputs.json']
assert len(staging['files']) == 1311
assert len({r['path'] for r in staging['files']}) == 1311
for row in staging['files']:
    assert row['original']['path'] == '/private/tmp/starling-node-compat/crypto-owner-source-v2/' + row['path']
    assert checked(row['original']).stat().st_mode & 0o777 == row['mode']
protection = documents['normal-protection.json']
assert len(protection['originals']) == 1387
assert len({physical(r['original']['path']) for r in protection['originals']}) == 1378
freeze = physical(protection['freezeReceipt']['path']).parent
assert {p.relative_to(freeze).as_posix() for p in freeze.rglob('*') if p.is_file()} == set(protection['requiredNormalFreezeMembership'])
assert len(protection['requiredNormalFreezeMembership']) == 1391

trees = {p.name: ast.parse(p.read_text(), filename=str(p)) for p in SOURCE.glob('*.py')}
guard = trees['guard.py']
authorize = next(n for n in guard.body if isinstance(n, ast.FunctionDef) and n.name == 'authorize')
frame = next(n.value for n in ast.walk(authorize) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'frame' for t in n.targets))
assert isinstance(frame, ast.Call) and isinstance(frame.func, ast.Name) and frame.func.id == 'dict'
keys = {k.arg for k in frame.keywords}
freezer_wrapper = trees['freeze.py']
updates = [n for n in ast.walk(freezer_wrapper) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'frame' and n.func.attr == 'update']
assert len(updates) == 1
keys.update(k.arg for k in updates[0].keywords)
body = trees['freezer-body.py']
reads = {n.slice.value for n in ast.walk(body) if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id == 'context' and isinstance(n.slice, ast.Constant)}
assert reads - keys == {'authority'}
assert 'rootAuthority' in keys and 'authority' not in keys
model = dict.fromkeys(keys)
try:
    model['authority']
except KeyError as error:
    assert error.args == ('authority',)
else:
    raise AssertionError('Unprovided authority unexpectedly available')

derivation = documents['freezer-derivations.json']
text = (SOURCE / 'freezer-body.py').read_text()
assert text.startswith(derivation['prefix'])
text = text[len(derivation['prefix']):]
for edit in reversed(derivation['edits']):
    assert text.count(edit['after']) == edit['count']
    text = text.replace(edit['after'], edit['before'])
old = checked(derivation['source']).read_text()
assert text == old[old.index(derivation['extractStart']):old.index(derivation['extractEnd'])]
export = documents['export-derivations.json']
text = (SOURCE / 'export-body.py').read_text().split('\n', 1)[1]
assert text.count(export['after']) == 1
old = checked(export['source']).read_text()
assert text.replace(export['after'], export['before']) == old[old.index(export['extractStart']):old.index(export['extractEnd'])]
refs = documents['references.json']
assert not any('SOURCE' in key or 'SRC' in key for key in refs['normalBuildEnvironment'])
recipe = Path(staging['cloneSource']) / 'tests/node-compat/build-engine.sh'
assert 'repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"' in recipe.read_text()
assert 'export STARLINGMONKEY_SRC="$repo_root"' in recipe.read_text()
for destination in ('/private/tmp/starling-node-compat/crypto-owner355-gc-v1-source', '/private/tmp/starling-node-compat/crypto-owner355-gc-v1-build', '/private/tmp/starling-node-compat/crypto-owner355-gc-v1-freeze', '/private/tmp/starling-node-compat/crypto-owner355-gc-v1-build-root', '/private/tmp/starling-node-compat/crypto-owner355-gc-v1-stage.json'):
    assert not Path(destination).exists()

finding = dict(id='GC-NATIVE-FRAME-M1', severity='blocking', sourceOnly=True, observedActualFailure=False,
    guardSource=str(SOURCE / 'guard.py'), wrapperSource=str(SOURCE / 'freeze.py'), freezerSource=str(SOURCE / 'freezer-body.py'),
    providedAuthorityKey='rootAuthority', requiredMissingKey='authority',
    effect='Source-deterministic KeyError in correction-proof construction after read-only admission/Ninja helpers and before execute_plan; no actual phase invoked.',
    correction='Use the actual rootAuthority descriptor consistently in a thin sealed successor, preserve donor reversibility, and add a complete context-key/binding regression. Re-review before native actions.')
write('findings.json', [finding])
write('context-fields.json', dict(providedKeys=sorted(keys), directFreezerReads=sorted(reads), unprovidedKeys=sorted(reads-keys), sourceCoupledPureLookupRejected=True))
write('rehashed-inputs.json', dict(files=sorted(seen.values(), key=lambda r:r['path']), distinctPhysicalFiles=len(seen), bytes=sum(r['bytes'] for r in seen.values())))
write('results.json', dict(schemaVersion=1, state='INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_SOURCE_REVIEW_HELD_V1', sourceIndexSha256=EXPECTED, sourceOnly=True, sourceReviewPassed=False, ownerActionsInvoked=False,
    sourceIndex=index_row, indexedSourceMembers=39, actualSourceFiles=40, inputRows=len(documents['input-freeze.json']['files']), distinctPhysicalFiles=len(seen), pythonAstModules=len(trees), freezerExactReversals=len(derivation['edits']), exportExactReversals=1,
    normalOriginalEntries=1387, normalUniqueOriginals=1378, normalFreezeMembership=1391, stagedRows=1311, sourceRootEnvironmentOverrideConcernRefuted=True,
    findings=['GC-NATIVE-FRAME-M1'], sourceAdoptionAllowed=False, nativeStageBuildFreezeExportBootstrapAllowed=False, guestGcKeyOrComponentAllowed=False,
    limitations=['Static source/data review and pure context-key model only; no owner tests or phase entry imported.', 'External controller remains an additional implementation/review gate.', 'No GC native artifact or runtime behavior is established.']))
print(json.dumps(dict(state='HOLD', findings=['GC-NATIVE-FRAME-M1'], distinctPhysicalFiles=len(seen), pythonAstModules=len(trees), ownerActionsInvoked=False)))
