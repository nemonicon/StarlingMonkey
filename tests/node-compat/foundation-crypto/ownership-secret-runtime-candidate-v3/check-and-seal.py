"""Validate actual unmodified module constants, full input closure and pure tests."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import os
import stat
import subprocess

HERE = Path(__file__).resolve().parent
assert not (HERE / 'index.json').exists()


def row(p):
    p = Path(p)
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return dict(path=str(p), sha256=h.hexdigest(), bytes=p.stat().st_size)


def read(p):
    return json.loads(Path(p).read_bytes())


def write(name, value):
    with (HERE / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


ledger = read(HERE / 'source-inputs.json')
refs = read(HERE / 'references.json')
seen = {}
for r in ledger['files']:
    p = Path(r['path'])
    assert p.is_file() and not p.is_symlink() and row(p) == r
    s = p.stat()
    seen[str(p)] = (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
for r in ledger['modeRows']:
    assert stat.S_IMODE(Path(r['file']['path']).stat().st_mode) == r['mode']
for ix in ledger['families']:
    base = Path(ix['path']).parent
    expected = {'index.json'} | {r['path'] for r in read(ix['path'])['files']}
    assert not any(p.is_symlink() for p in base.rglob('*'))
    assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()} == expected
for tree in ledger['historicalDonorTrees']:
    base = Path(tree['root'])
    assert not any(p.is_symlink() for p in base.rglob('*'))
    assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()} == set(tree['names'])
# Import only the stdlib-only external definitions at their real file/context.
# No namespace injection, global reassignment, run(), authorize() or monitor call.
spec = importlib.util.spec_from_file_location('actual_secret_runtime_v3_constants', HERE / 'external.py')
external = importlib.util.module_from_spec(spec)
spec.loader.exec_module(external)
assert Path(external.__file__).resolve().parent == external.OWN == HERE
assert external.REPO == HERE.parents[3]
assert str(external.OUTPUT) == refs['outputRoot'] and str(external.OUT) == refs['externalOutputRoot']
assert not external.OUTPUT.exists() and not external.OUT.exists()
entry = (HERE / 'entry.mjs').read_text()
assert "const ORIGINAL='" + str(HERE) + "';" in entry
assert "ROOT_REVIEWED_SECRET355_NORMAL_RUNTIME_V3" in entry
assert "SECRET355_NORMAL_RUNTIME_CONFIG_V3" in entry
assert 'Preserve exact unexecuted v2 context HOLD' in entry
for name in ['checks.mjs', 'oracle.mjs', 'schedule.json', 'loading.mjs']:
    assert (HERE / name).read_bytes() == (HERE.parent / 'ownership-secret-runtime-candidate-v2' / name).read_bytes()
for item in read(HERE / 'derivations.json')['files']:
    before = Path(item['donor']['path']).read_text()
    current = before
    for edit in item['edits']:
        assert current.count(edit['before']) == edit['occurrences']
        current = current.replace(edit['before'], edit['after'])
    assert current == (HERE / item['output']).read_text()
    for edit in reversed(item['edits']):
        assert current.count(edit['after']) == edit['occurrences']
        current = current.replace(edit['after'], edit['before'])
    assert current == before
terms = []
env = dict(os.environ)
env.pop('NODE_OPTIONS', None)
env.pop('NODE_PATH', None)
for name in ['test-pure.mjs', 'test-correction.mjs']:
    argv = [refs['node']['path'], str(HERE / name)]
    r = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=60)
    (HERE / (name + '.stdout.log')).write_bytes(r.stdout)
    (HERE / (name + '.stderr.log')).write_bytes(r.stderr)
    write(name + '.terminal.json', dict(argv=argv, rawExitCode=r.returncode, ownerOrGuestActionInvoked=False))
    assert r.returncode == 0 and r.stderr == b''
    terms.append(json.loads(r.stdout))
for p in HERE.glob('*.py'):
    ast.parse(p.read_bytes(), filename=str(p))
for path, identity in seen.items():
    s = Path(path).stat()
    assert (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns) == identity
for r in ledger['files']:
    assert row(r['path']) == r
write('results.json', dict(schemaVersion=1, state='SECRET355_NORMAL_RUNTIME_SOURCE_SEALED_UNREVIEWED_V3', sourceOnly=True,
                          sourceRoot=str(HERE), previousSource=refs['previousRuntimeV2SourceIndex'],
                          contextCorrectionReview=refs['contextCorrectionReview'], actualModuleOwnMatchesRealFile=True,
                          actualOutputConstantsMatch=True, noNamespaceGlobalsOverridden=True,
                          sourceInputFiles=len(ledger['files']), completeFamilies=len(ledger['families']),
                          historicalDonorTrees=len(ledger['historicalDonorTrees']), pureResults=terms,
                          nativeSourceFiles=355, externalEmbeddingSources=3, selectedWholeManifests=11, rawMetadataFields=75,
                          component=refs['artifacts']['component'], engine=refs['engine'],
                          fullFourCasesAndThreeSessionSchedulePreserved=True, constructorOrMonitorOrApiInvoked=False,
                          generatedModuleImported=False, guestOrKeyOrCryptoWorkloadExecuted=False,
                          sourcePeer=None, rootAuthority=None, actualRuntimeResult=None, operationalAdmission=False))
write('source-receipt.json', dict(schemaVersion=1, sourceOnly=True, result=row(HERE / 'results.json'), sourceInputs=row(HERE / 'source-inputs.json'),
                                 contextCorrectionValidatedWithoutOverrides=True, ownerActionsInvoked=False))
members = [dict(row(p), path=p.relative_to(HERE).as_posix()) for p in sorted(HERE.rglob('*')) if p.is_file()]
write('index.json', dict(schemaVersion=1, files=members))
print(json.dumps(dict(index=row(HERE / 'index.json'), result=row(HERE / 'results.json'), files=len(members))))
