"""Actual read/hash guards on five paths, plus isolated benign FS negatives.

No operational driver import, authorize(), monitor or compiler is called.
"""
from pathlib import Path
import ast
import hashlib
import json
import os
import stat
import tempfile

HERE = Path(__file__).resolve().parent
plan = json.loads((HERE / 'plan.json').read_bytes())
tree = ast.parse((HERE / 'run-sdk-syntax.py').read_text())
names = {'descriptor', 'regular', 'identity', 'Protection', 'tree_snapshot',
         'alias_snapshot', 'absence_snapshot'}
nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
assert {n.name for n in nodes} == names
space = dict(Path=Path, hashlib=hashlib, json=json, stat=stat, os=os)
exec(compile(ast.Module(body=nodes, type_ignores=[]), 'actual-sdk-v2-read-hash-guards', 'exec'), space)
Protection = space['Protection']
guard = Protection()
ledger = guard.read(plan['references']['inputLedger'])['files']
aliases = guard.read(plan['references']['aliasInventory'])['symlinks']
source_index = guard.read(plan['references']['sourceIndex'])
assert len(source_index['files']) == 25
observations = []
for item in plan['protectedTrees']:
    root = Path(item['path'])
    rows = [r for r in ledger if Path(r['path']).is_relative_to(root)
            and '.git' not in Path(r['path']).relative_to(root).parts]
    links = [r for r in aliases if Path(r['path']).is_relative_to(root)]
    assert len(rows) == item['regularFiles'] and len(links) == item['symlinks']
    guard.tree(root, rows, links)
    observations.append(dict(path=str(root), actualGuardPassed=True, regularFiles=len(rows),
        symlinks=len(links), expectedRegularBytes=sum(r['bytes'] for r in rows), expectedKind='existing directory'))
policy = plan['absentIncludePolicies'][0]
observed_absence = guard.absent_include(policy)
observations.append(dict(path=policy['path'], actualGuardPassed=True, expectedKind='absent entry',
                         absence=observed_absence))
assert len(observations) == 5 and len(guard.files) == 12751
before_digest = hashlib.sha256(json.dumps(dict(files=guard.files, trees=guard.trees,
    aliases=guard.aliases, absences=guard.absences), sort_keys=True).encode()).hexdigest()
final = guard.recheck()
assert final['unchanged'] is True and final['absentIncludes'] == 1

cases = []
def refuse(label, callback):
    try:
        callback()
    except (AssertionError, FileNotFoundError, NotADirectoryError):
        cases.append(dict(id=label, refused=True))
    else:
        raise AssertionError(label)

# These scratch files exercise the actual functions. They are never under a
# historical include, SDK, configured Source or future compiler output path.
with tempfile.TemporaryDirectory(prefix='init-barrier-sdk-v2-path-models-',
                                 dir='/private/tmp/starling-node-compat') as tmp:
    scratch = Path(tmp)
    refuse('missing required tree is not silently treated as absent',
           lambda: Protection().tree(scratch / 'missing-required', [], []))
    empty = scratch / 'empty-present-include'
    empty.mkdir()
    refuse('empty existing include directory is not absence',
           lambda: Protection().absent_include(dict(path=str(empty), mustRemainAbsent=True)))
    file = scratch / 'present-file'
    file.write_bytes(b'not an absent path')
    refuse('present regular file is not absence',
           lambda: Protection().absent_include(dict(path=str(file), mustRemainAbsent=True)))
    alias = scratch / 'alias'
    alias.symlink_to(empty, target_is_directory=True)
    refuse('symlink target is not absent',
           lambda: Protection().absent_include(dict(path=str(alias), mustRemainAbsent=True)))
    refuse('aliased ancestor cannot hide missing leaf',
           lambda: Protection().absent_include(dict(path=str(alias / 'missing-leaf'), mustRemainAbsent=True)))
    refuse('required tree root cannot be an alias', lambda: Protection().tree(alias, [], []))
    dangling = scratch / 'dangling'
    dangling.symlink_to(scratch / 'nonexistent')
    refuse('dangling symlink is not absence',
           lambda: Protection().absent_include(dict(path=str(dangling), mustRemainAbsent=True)))
    future = scratch / 'new-parent' / 'include'
    changed = Protection()
    changed.absent_include(dict(path=str(future), mustRemainAbsent=True))
    future.parent.mkdir()
    intermediate = changed.recheck()
    assert intermediate['unchanged'] is False
    cases.append(dict(id='new intermediate directory detected on final bookend', refused=True))
    future.mkdir()
    appeared = changed.recheck()
    assert appeared['unchanged'] is False
    cases.append(dict(id='include appearance detected on final bookend', refused=True))
    scalar = scratch / 'not-directory-parent'
    scalar.write_bytes(b'x')
    refuse('regular-file ancestor refused',
           lambda: Protection().absent_include(dict(path=str(scalar / 'include'), mustRemainAbsent=True)))

assert not Path(plan['outputRoot']).exists()
assert space['absence_snapshot'](Path(policy['path'])) == observed_absence
print(json.dumps(dict(schemaVersion=1, state='ACTUAL_FIVE_PATH_GUARDS_AND_ABSENCE_NEGATIVES_PASSED_V2',
    driver=space['descriptor'](HERE / 'run-sdk-syntax.py'), plan=space['descriptor'](HERE / 'plan.json'),
    observations=observations, regularTreeFilesHashedBeforeAndAfter=12748,
    actualRegularTreeBytesBeforeAndAfter=sum(r['expectedRegularBytes'] for r in observations[:4]),
    fileIdentitySnapshotSha256=before_digest, finalProtection=final,
    negativeCases=cases, isolatedScratchRemoved=True, historicalMissingPathStillAbsent=True,
    compilerMonitorHelperEngineGuestCryptoInvoked=False,
    scope='Current path guards only; not authorize/driver main or any compiler action'), indent=2))
