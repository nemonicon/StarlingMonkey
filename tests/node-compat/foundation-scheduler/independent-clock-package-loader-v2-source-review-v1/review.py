"""Independent Source review; no package, construction or guest API is called."""
from pathlib import Path
import hashlib
import json
import os
import stat
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'clock-package-loader-candidate-v2'
EXPECTED = 'ae82580f680be3109be7d27769360bca0ca45311f6cff04b2546a68add1aef58'
observed = {}


def read(path):
    return json.loads(Path(path).read_bytes())


def physical(path):
    return Path('/private' + path) if path.startswith('/tmp/') else Path(path)


def verify(r):
    p = physical(r['path'])
    assert p.is_file() and not p.is_symlink()
    s = p.stat()
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    assert s == p.stat() and s.st_size == r['bytes'] and h.hexdigest() == r['sha256'], str(p)
    observed[str(p)] = r


def family(ix):
    verify(ix)
    base = physical(ix['path']).parent
    expected = {'index.json'}
    for r in read(ix['path'])['files']:
        assert r['path'] not in expected and not Path(r['path']).is_absolute() and '..' not in Path(r['path']).parts
        expected.add(r['path'])
        verify(dict(r, path=str(base / r['path'])))
    actual = set()
    for p in base.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():
            actual.add(p.relative_to(base).as_posix())
    assert actual == expected


source_bytes = (SOURCE / 'index.json').read_bytes()
own = dict(path=str(SOURCE / 'index.json'), sha256=hashlib.sha256(source_bytes).hexdigest(), bytes=len(source_bytes))
assert own['sha256'] == EXPECTED
family(own)
refs = read(SOURCE / 'references.json')
inputs = read(SOURCE / 'source-inputs.json')
for r in inputs['files']:
    verify(r)
for ix in inputs['families']:
    family(ix)
derivation = read(SOURCE / 'derivations.json')
code = (SOURCE / 'loader.mjs').read_text()
reverse = code
for change in reversed(derivation['exactReversibleEdits']):
    assert reverse.count(change['after']) == 1
    reverse = reverse.replace(change['after'], change['before'])
assert len(derivation['exactReversibleEdits']) == 10
assert reverse == Path(derivation['predecessorLoader']['path']).read_text()
assert code.index('return loadGate.run(async()=>{') < code.index('const configRow=descriptor(input?.configDescriptor)')
assert code.index('loadGate.retain(()=>c.recheck())') < code.index('const config=await c.json')
assert code.index('loadGate.retain(recheck);') < code.index('import(pathToFileURL(refs.packageEntry.path))')
assert 'finally{if(retainedRecheck)await retainedRecheck();}' in code
assert 'finally{await c.recheck();}' in code and 'finally{await context.recheck();}' in code
inventory = read(refs['packageInventory']['path'])['package']
package = Path(inventory['root'])
expected = set()
for r in inventory['files']:
    p = physical(r['path'])
    assert str(p) in observed and p == package / r['relativePath']
    assert observed[str(p)]['sha256'] == r['sha256'] and observed[str(p)]['bytes'] == r['bytes']
    assert stat.S_IMODE(p.stat().st_mode) == r['mode'] and p.stat().st_nlink == 1
    expected.add(r['relativePath'])
for r in inventory['links']:
    p = package / r['path']
    assert p.is_symlink() and os.readlink(p) == r['target'] and str(p.resolve()) == r['resolvedPath']
    expected.add(r['path'])
assert {p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file() or p.is_symlink()} == expected
assert len(inventory['files']) == 4889 and len(inventory['links']) == 21 and len(refs['actualArtifacts']) == 25
for r in refs['actualArtifacts']:
    verify(r)
assert not (package / 'splicer-build.json').exists()
argv = [refs['node']['path'], str(SOURCE / 'test-pure.mjs')]
env = dict(os.environ)
env.pop('NODE_OPTIONS', None)
env.pop('NODE_PATH', None)
run = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=60)
(HERE / 'pure.stdout.log').write_bytes(run.stdout)
(HERE / 'pure.stderr.log').write_bytes(run.stderr)
(HERE / 'pure.terminal.json').write_text(json.dumps(dict(argv=argv, rawExitCode=run.returncode), indent=2) + '\n')
assert run.returncode == 0 and run.stderr == b''
pure = json.loads(run.stdout)
assert pure['checks'] == 67 and pure['actualPackageSplicerImported'] is False
assert pure['actualComponentizeOrWizerInvoked'] is False and pure['engineOrGuestExecuted'] is False
for r in list(observed.values()):
    verify(r)
family(own)
result = dict(schemaVersion=1, state='INDEPENDENT_CLOCK_PACKAGE_LOADER_SOURCE_REVIEW_PASSED_V2',
              sourceIndexSha256=EXPECTED, sourceIndex=own, sourceOnly=True, sourceReviewPassed=True,
              ownerActionsInvoked=False, hostActionsInvoked=False, packageImportOrComponentizeActionsInvoked=False,
              inertDefinitionsAndPureModelTestsOnly=True, fullDeclaredFiles=len(inputs['files']), fullDeclaredFamilies=len(inputs['families']),
              independentlyHashedFiles=len(observed), logicalBytes=sum(r['bytes'] for r in observed.values()),
              packageRegularFiles=4889, packageAliases=21, artifactDescriptors=25, exactReverseEdits=10,
              hostPureChecks=67, repeatedLoadProtectionGapCorrected=True, priorHoldPreserved=True,
              actualPackageImported=False, actualLoaderApiInvoked=False, componentizeOrWizerOrEngineOrGuestExecuted=False,
              nativeAdmissionGranted=False, actualComponentProof=None, rootAuthority=None, operationalAdmission=False,
              limitation='Source and pure models only; native caller admission, real packaging, final emitted imports and runtime need separate evidence.')
(HERE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'input-hashes.json').write_text(json.dumps(sorted(observed.values(), key=lambda r:r['path']), indent=2) + '\n')
print(json.dumps(result))
