"""Independent complete-closure/derivation and inert model review. No guest call."""
from pathlib import Path
import hashlib
import json
import os
import stat
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'ownership-secret-runtime-candidate-v2'
seen = {}


def read(p):
    return json.loads(Path(p).read_bytes())


def descriptor(p):
    p = Path(p)
    b = p.read_bytes()
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


def verify(r):
    p = Path(r['path'])
    assert p.is_file() and not p.is_symlink()
    a = p.stat()
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    z = p.stat()
    identity = lambda s:(s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_mode, s.st_nlink)
    assert identity(a) == identity(z) and z.st_size == r['bytes'] and h.hexdigest() == r['sha256'], str(p)
    seen[str(p)] = r


def family(ix):
    verify(ix)
    base = Path(ix['path']).parent
    names = {'index.json'}
    for r in read(ix['path'])['files']:
        assert r['path'] not in names and not Path(r['path']).is_absolute() and '..' not in Path(r['path']).parts
        names.add(r['path'])
        verify(dict(r, path=str(base / r['path'])))
    actual = set()
    for p in base.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():
            actual.add(p.relative_to(base).as_posix())
    assert actual == names, str(base)


own = descriptor(SOURCE / 'index.json')
assert own['sha256'] == 'c37bab3384cbdc03705730dfa515467995d543d9ac415d36604106c51c09bf4e'
family(own)
refs = read(SOURCE / 'references.json')
ledger = read(SOURCE / 'source-inputs.json')
assert len(ledger['files']) == 34094 and len(ledger['families']) == 32
for r in ledger['files']:
    verify(r)
for r in ledger['modeRows']:
    assert stat.S_IMODE(Path(r['file']['path']).stat().st_mode) == r['mode']
for ix in ledger['families']:
    family(ix)
assert len(ledger['historicalDonorTrees']) == 1
for tree in ledger['historicalDonorTrees']:
    base = Path(tree['root'])
    assert not any(p.is_symlink() for p in base.rglob('*'))
    assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()} == set(tree['names'])
    assert 'source-receipt.json' in tree['names']
    assert str(base / 'source-receipt.json') in seen
for item in read(SOURCE / 'derivations.json')['files']:
    before = Path(item['donor']['path']).read_bytes()
    after = (SOURCE / item['output']).read_bytes()
    current = before
    for edit in reversed(item['edits']):
        at = edit['beforeOffset']
        raw = edit['before'].encode()
        assert current[at:at + len(raw)] == raw
        current = current[:at] + edit['after'].encode() + current[at + len(raw):]
    assert current == after, item['output']
    for edit in reversed(item['edits']):
        at = edit['afterOffset']
        raw = edit['after'].encode()
        assert current[at:at + len(raw)] == raw
        current = current[:at] + edit['before'].encode() + current[at + len(raw):]
    assert current == before
assert (SOURCE / 'schedule.json').read_bytes() == (SOURCE.parent / 'ownership-secret-runtime-candidate-v1/schedule.json').read_bytes()
for name in ['oracle.mjs', 'checks.mjs']:
    assert (SOURCE / name).read_bytes() == (SOURCE.parent / 'ownership-runtime-candidate-v1' / name).read_bytes()
held = read(refs['heldRuntimeSourceReview']['result']['path'])
assert held['sourceReviewPassed'] is False and held['sourceIndexSha256'] == refs['parentRuntimeSourceIndex']['sha256']
proof = read(refs['actualArtifactReview']['result']['path'])
assert proof['verifiedPassed'] and proof['nativeSourceFiles'] == 355 and proof['externalEmbeddingSources'] == 3
assert proof['selectedManifestCount'] == 11 and proof['fullMetadataFields'] == 75
assert proof['artifacts'] == refs['artifacts'] and proof['engineSha256'] == refs['engine']['sha256']
body = (SOURCE / 'runtime-body.mjs').read_text()
assert '(sequence.captureFailures??=[]).push(failure)' in body
assert 'if(thrown)throw value; // Even falsy/primitive/frozen X' in body
assert body.count("name:'failure.json'") == 2 and 'await diagnosticWrite(' in body
assert 'No missing raw or diagnostic failure' in body
assert "for(const scenario of ['retained','fresh','wrapper'])" in body
assert "scenario==='retained'?3:1" in body and 'id<4' in body
assert 'finally{await out.close();}' in body and body.count('finalErrors=await finalProtection(') == 2
terms = []
env = dict(os.environ)
env.pop('NODE_OPTIONS', None)
env.pop('NODE_PATH', None)
for name in ['test-pure.mjs', 'test-correction.mjs']:
    argv = [refs['node']['path'], str(SOURCE / name)]
    run = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=60)
    (HERE / (name + '.stdout.log')).write_bytes(run.stdout)
    (HERE / (name + '.stderr.log')).write_bytes(run.stderr)
    term = dict(argv=argv, rawExitCode=run.returncode, ownerOrGuestApiInvoked=False)
    (HERE / (name + '.terminal.json')).write_text(json.dumps(term, indent=2) + '\n')
    assert run.returncode == 0 and run.stderr == b''
    terms.append(json.loads(run.stdout))
for r in list(seen.values()):
    verify(r)
family(own)
result = dict(schemaVersion=1, state='INDEPENDENT_CRYPTO_OWNER355_SECRET_RUNTIME_SOURCE_REVIEW_PASSED_V2',
              sourceIndexSha256=own['sha256'], sourceIndex=own, sourceOnly=True, sourceReviewPassed=True,
              ownerActionsInvoked=False, hostActionsInvoked=False, runtimeActionsInvoked=False,
              inertHostModelProcessesInvoked=2, pureResults=terms, declaredFiles=len(ledger['files']),
              completeFamilies=len(ledger['families']), historicalDonorTrees=1, hashedPaths=len(seen),
              fullDerivationPassed=True, originalGuestThrowPreservedOnWriterFailure=True,
              diagnosticWriterFailuresDoNotReplaceOriginal=True, fullFourCasesAndOracleSchedulePreserved=True,
              nativeSourceFiles=355, externalEmbeddingSources=3, fullMetadataFields=75, selectedWholeManifests=11,
              actualComponent=refs['artifacts']['component'], engine=refs['engine'],
              actualRuntimeProof=None, runtimeAuthority=None, operationalAdmission=False,
              limitation='Source and host-only models; no generated module, application component, key or crypto workload executed. Filesystem failure cannot guarantee durable diagnostics; opaque throw values are not represented in full.')
(HERE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'input-hashes.json').write_text(json.dumps(sorted(seen.values(), key=lambda r:r['path']), indent=2) + '\n')
print(json.dumps(result))
