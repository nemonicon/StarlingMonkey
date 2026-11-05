"""Independent read/hash, AST and pure DATA review; no owner module imports."""
from pathlib import Path
import ast
import hashlib
import json
import os

REPO = Path('/Users/dan/dev/StarlingMonkey')
HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'ownership-gc-native-candidate-v2'
EXPECTED = 'ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05'
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


def walk(value, synthetic=False):
    if isinstance(value, dict):
        if {'path', 'sha256', 'bytes'} <= value.keys() and isinstance(value['path'], str) and value['path'].startswith('/'):
            if synthetic and value["path"].startswith("/synthetic-data-only/"):
                assert set(value)=={"path","sha256","bytes"}
            else:
                checked(value)
        for child in value.values():
            walk(child, synthetic)
    elif isinstance(value, list):
        for child in value:
            walk(child, synthetic)


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
assert len(index['files']) == 30
names = {row['path'] for row in index['files']}
assert len(names) == 30
assert {p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob('*') if p.is_file()} == names | {'index.json'}
documents = {}
for row in index['files']:
    checked({**row, 'path': str(SOURCE / row['path'])})
    if row['path'].endswith('.json'):
        value = json.loads((SOURCE / row['path']).read_bytes())
        documents[row['path']] = value
        walk(value, row["path"]=="context-regression-results.json" and value.get("descriptorIsSyntheticDataOnly") is True)

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
assert reads <= keys and len(reads)==13 and 'rootAuthority' in reads and 'authority' not in reads
recheck = next(n for n in guard.body if isinstance(n,ast.FunctionDef) and n.name=='recheck')
assert ast.unparse(recheck.body[0].test)=="frame['rootAuthority'] == read(frame['captured'][0])['rootAuthority']"
assert ast.unparse(recheck.body[1].test)=="frame['rootAuthority'] == frame['captured'][1]"
derivation=documents['donor-derivations.json']
derived=0
unchanged=0
for row in derivation['files']:
    original=checked(row['source']).read_text()
    new=(SOURCE/row['afterimage']).read_text()
    forward=original
    for edit in row['edits']:
        assert forward.count(edit['before'])==edit['count']
        forward=forward.replace(edit['before'],edit['after'])
    assert forward==new
    for edit in reversed(row['edits']):
        assert new.count(edit['after'])==edit['count']
        new=new.replace(edit['after'],edit['before'])
    assert new==original
    derived+=bool(row['edits'])
    unchanged+=not bool(row['edits'])
assert (derived,unchanged)==(6,12)
refs = documents['references.json']
assert not any('SOURCE' in key or 'SRC' in key for key in refs['normalBuildEnvironment'])
recipe = Path(staging['cloneSource']) / 'tests/node-compat/build-engine.sh'
assert 'repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"' in recipe.read_text()
assert 'export STARLINGMONKEY_SRC="$repo_root"' in recipe.read_text()
for destination in ('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source', '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build', '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze', '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build-root', '/private/tmp/starling-node-compat/crypto-owner355-gc-v2-stage.json'):
    assert not Path(destination).exists()

old_refs=json.loads(checked(derivation['referencesDerivation']['source']).read_bytes())
assert refs['pinnedInputs'][:len(old_refs['pinnedInputs'])]==old_refs['pinnedInputs']
assert refs['pinnedInputs'][len(old_refs['pinnedInputs']):]==derivation['referencesDerivation']['pinnedInputsAppendOnly']
for field in ('normalBuildEnvironment','normalStageReceipt','node','proposalIndex'):
    assert refs[field]==old_refs[field]
for index_row in (derivation['donorIndex'],derivation['heldReviewIndex']):
    indexed=json.loads(checked(index_row).read_bytes())
    required=[index_row,*[dict(path=str(Path(index_row['path']).parent/r['path']),sha256=r['sha256'],bytes=r['bytes'])for r in indexed['files']]]
    assert all(row in refs['pinnedInputs']for row in required)
stored=documents['context-regression-results.json']
assert stored['checks']==14 and stored['actualBodyContextReadKeys']==sorted(reads)
assert stored['ownerModulesImported']is False and stored['actualHelperOrActionInvoked']is False
write('context-fields.json',dict(providedKeys=sorted(keys),bodyReadKeys=sorted(reads),missingKeys=sorted(reads-keys),descriptorBindings=[ast.unparse(recheck.body[0]),ast.unparse(recheck.body[1])],storedOwnerPureChecksAuthenticatedNotRerun=14))
write('rehashed-inputs.json',dict(files=sorted(seen.values(),key=lambda r:r['path']),distinctPhysicalFiles=len(seen),bytes=sum(r['bytes']for r in seen.values())))
write('results.json',dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_SOURCE_REVIEW_PASSED_V2',sourceIndexSha256=EXPECTED,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,sourceIndex=descriptor(SOURCE/'index.json'),indexedMembers=30,uniquePhysicalFiles=len(seen),preparationRows=2852,derivedFiles=6,unchangedSupportCopies=12,pythonAstModules=len(trees),providedAll13BodyContextReadKeys=True,exactAuthorityDescriptorBinding=True,heldSourceAndReviewRuntimeAuthenticated=True,normalFrozenMembers=1391,normalOriginalEntries=1387,externalControllerStillRequiresReview=True,nativeOrGuestActionAllowed=False,limitations=['Bounded source/data/AST review only; stored14 pure owner checks authenticated, not rerun.','No phase/helper/Node/generated module/guest/native/GC/key action.','No actual GC artifact, pin or runtime proof; new Root phase/controller and actual result reviews remain required.']))
print(json.dumps(dict(state='PASS',uniquePhysicalFiles=len(seen),pythonAstModules=len(trees),ownerActionsInvoked=False)))
