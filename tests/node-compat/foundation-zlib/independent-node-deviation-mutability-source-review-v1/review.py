"""Independent Root text/data review; no owner checker or runtime imports."""
from pathlib import Path
import difflib, hashlib, json

HERE = Path(__file__).resolve().parent
OWNER = HERE.parent / 'node-deviation-contract-mutability-amendment-v1'
BASE = HERE.parent / 'node-deviation-contract-candidate-v1'
sha = lambda b: hashlib.sha256(b).hexdigest()
load = lambda p: json.loads(p.read_bytes())
observed = {}

def check(path, expected, size):
    p = Path(path)
    assert p.is_absolute() and p.is_file() and not p.is_symlink()
    before = p.stat()
    raw = p.read_bytes()
    after = p.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
            before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size,
                                   after.st_mtime_ns, after.st_ctime_ns)
    assert len(raw) == size and sha(raw) == expected, p
    observed[str(p)] = {'path': str(p), 'sha256': expected, 'bytes': size}

own_raw = (OWNER / 'index.json').read_bytes()
assert sha(own_raw) == 'b8ec1f65316eb3ebac3d2fa582eb09cea2c568e1507f4dc9bb54ddccf659413a'
index = json.loads(own_raw)
for r in index['files']:
    check(OWNER / r['path'], r['sha256'], r['bytes'])
refs = load(OWNER / 'source-inputs.json')['files']
for r in refs:
    check(r['path'], r['sha256'], r['bytes'])
delta = load(OWNER / 'derivations.json')
for r in delta['files']:
    before = ''.join(difflib.restore(r['ndiff'], 1)).encode()
    after = ''.join(difflib.restore(r['ndiff'], 2)).encode()
    assert before == (BASE / r['path']).read_bytes()
    assert after == (OWNER / 'proposed' / r['path']).read_bytes()
    assert sha(before) == r['beforeSha256'] and sha(after) == r['afterSha256']
old = load(BASE / 'contract.proposal.json')
new = load(OWNER / 'proposed/contract.proposal.json')
old.pop('contractVersion')
new.pop('contractVersion')
old['domain'].pop('namespace')
new['domain'].pop('namespace')
assert old == new
node_rows = [r for r in refs if r['path'].endswith('/lib/zlib.js')]
assert len(node_rows) == 1
node = Path(node_rows[0]['path']).read_text()
assert 'ObjectFreeze(codes)' in node
assert 'Freezing codes is therefore **not** a difference' in (OWNER / 'README.md').read_text()
result = {'schemaVersion': 1,
          'state': 'INDEPENDENT_DEVIATION_MUTABILITY_CORRECTION_SOURCE_PASSED',
          'sourceIndexSha256': sha(own_raw), 'sourceOnly': True,
          'sourceReviewPassed': True, 'indexedFiles': len(index['files']),
          'references': len(refs), 'exactReversibleAfterimages': len(delta['files']),
          'allOtherContractValuesUnchanged': True,
          'pinnedNodeFreezesCodes': True, 'ownerCheckerOrRuntimeInvoked': False,
          'proposalOrPolicyAccepted': False, 'operationalAdmission': False,
          'scope': 'Only the bounded namespace wording correction; original data-integrity and other proposal qualifications remain separate.'}
for name, value in [('results.json', result),
                    ('rehashed-files.json', {'schemaVersion': 1, 'files': list(observed.values())})]:
    with (HERE / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
print(json.dumps(result))
