"""Final source-derivation and whole finite DATA input stability check only."""
from pathlib import Path
import ast
import hashlib
import json
import stat

P = Path(__file__).resolve().parent


def row(path):
    path = Path(path)
    a = path.lstat()
    assert stat.S_ISREG(a.st_mode) and not path.is_symlink()
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    b = path.lstat()
    identity = lambda s: (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert identity(a) == identity(b)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=b.st_size)


derivation = json.loads((P/'model-derivation.json').read_bytes())
assert row(derivation['donorIndex']['path']) == derivation['donorIndex']
assert row(derivation['donorModel']['path']) == derivation['donorModel']
assert row(P/'model.py') == derivation['afterimage']
original = Path(derivation['donorModel']['path']).read_text()
value, steps = original, []
for edit in derivation['edits']:
    assert value.count(edit['before']) == edit['count'] == 1
    position = value.index(edit['before'])
    value = value[:position] + edit['after'] + value[position+len(edit['before']):]
    steps.append(dict(edit=edit,afterOffset=position))
assert value == (P/'model.py').read_text()
for step in reversed(steps):
    e, position = step['edit'], step['afterOffset']
    assert value[position:position+len(e['after'])] == e['after']
    value = value[:position] + e['before'] + value[position+len(e['after']):]
assert value == original
assert len(steps) == 7
actual_aggregate = Path('/private/tmp/starling-node-compat/zlib-cost-timing-v5/aggregate-observations.json')
assert json.loads(actual_aggregate.read_bytes()) == json.loads((P/'recomputed-aggregate.json').read_bytes())
grammar = []
for path in sorted(P.glob('*.py')):
    ast.parse(path.read_bytes(), filename=str(path))
    grammar.append(path.name)
rows = {}
counts = {}
for filename in ['output-input-hashes.json','prerequisite-input-hashes.json','outer-input-hashes.json']:
    files = json.loads((P/filename).read_bytes())['files']
    counts[filename] = len(files)
    for value in files:
        expected = {k:value[k]for k in ['path','sha256','bytes']}
        assert Path(expected['path']).is_absolute()
        assert rows.setdefault(expected['path'],expected) == expected
logical_bytes = 0
for expected in rows.values():
    assert row(expected['path']) == expected
    logical_bytes += expected['bytes']
ledger = dict(schemaVersion=1,files=[rows[path]for path in sorted(rows)],inputGroups=counts,sourceAndOutputRowsUnchanged=True,ownerActionsInvoked=False)
(P/'input-hashes.json').write_text(json.dumps(ledger,indent=2)+'\n')
report = dict(schemaVersion=1,state='FINAL_ACTUAL_TIMING_DATA_STABILITY_AND_DERIVATIONS_PASSED',uniquePaths=len(rows),logicalBytes=logical_bytes,groups=counts,modelExactForwardAndOffsetReverse=True,modelEdits=7,modelDonor=derivation['donorModel'],derivationSteps=steps,aggregateWholeJsonMatched=True,aggregateByteSerializationAlsoEqual=actual_aggregate.read_bytes()==(P/'recomputed-aggregate.json').read_bytes(),pythonAstFiles=grammar,ownerActionsInvoked=False,benchmarkOrHelperOrGuestRerun=False)
(P/'final-stability.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(finalStabilityPassed=True,paths=len(rows),logicalBytes=logical_bytes,modelEdits=7,pythonAstFiles=len(grammar),ownerActionsInvoked=False)))
