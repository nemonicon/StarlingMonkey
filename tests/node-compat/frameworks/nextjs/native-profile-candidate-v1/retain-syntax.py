"""Retain actual joined syntax raw outputs and authenticate .d inputs as data."""
import hashlib
import json
import shlex
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path('/private/tmp/starling-node-compat')
LIVE = BASE / 'next-combined-sdk-syntax-v2'
PROFILE = BASE / 'next-native-profile-v2'
OUT = HERE / 'syntax-results-v2'
OUT.mkdir()
copies = []


def row(path):
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def copy(path, target):
    before = row(path)
    dst = OUT / target; dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, dst)
    assert row(path) == before and row(dst)['sha256'] == before['sha256']
    copies.append({'original': str(path), 'file': str(target), 'sha256': before['sha256'], 'bytes': before['bytes']})


result = json.loads((LIVE / 'result.json').read_text())
assert result['passed'] and len(result['terminals']) == 13
composition = json.loads((PROFILE / 'composition.json').read_text())
inherited = json.loads((BASE / 'node-crypto-hash-hmac-v3-artifact-revalidation-v2/current-input-hashes.json').read_text())
allowed = {str(Path(r['path']).resolve()): r['sha256'] for r in inherited['files']}
allowed.update({str((PROFILE / 'source' / r['path']).resolve()): r['sha256'] for r in composition['files']})
dependencies = []
for unit in result['terminals']:
    identity = unit['id']; terminal = unit['terminal']
    assert terminal['rawExitCode'] == 0 and terminal['stdout']['bytes'] == terminal['stderr']['bytes'] == 0
    assert terminal['allObservedOwnedGroupsGone'] and terminal['parentOwnedGroupGone']
    assert not terminal['timeout'] and not terminal['forcedCleanup']
    assert all(terminal[k] == [] for k in ('errors','signals','interruptedSignals','remainingObservedPids'))
    for file in ('started.json','terminal.json','stdout.log','stderr.log'):
        copy(LIVE / identity / file, Path(identity) / file)
    depfile = LIVE / (identity + '.d')
    copy(depfile, Path(identity) / 'dependencies.d')
    text = depfile.read_text().replace('\\\n', ' ')
    target, separator, tail = text.partition(':')
    assert separator and target.strip() == identity
    for name in shlex.split(tail):
        path = Path(name).resolve(strict=True)
        actual = row(path)
        assert allowed.get(str(path)) == actual['sha256'], ('not a before-authenticated dependency', identity, name)
        dependencies.append({'unit': identity, 'reportedPath': name, 'resolvedPath': str(path), 'sha256': actual['sha256']})
for name in ('plan.json','authority.json','result.json'):
    copy(LIVE / name, Path(name))
copy(PROFILE / 'composition.json', Path('composition.json'))
copy(PROFILE / 'installed-checks/result.json', Path('installed/result.json'))
for p in sorted((PROFILE / 'installed-checks').iterdir()):
    if p.suffix in ('.stdout','.stderr'): copy(p, Path('installed') / p.name)
summary = {'schemaVersion': 1, 'state': 'ACTUAL_NEXT430_THIRTEEN_FRONTEND_PORTABLE_EVIDENCE',
           'passed': True, 'compilerUnits': 13, 'nativeSourceFiles': 430,
           'copies': copies, 'dependencies': dependencies,
           'dependencyObservations': len(dependencies), 'uniqueResolvedDependencies': len({r['resolvedPath'] for r in dependencies}),
           'protectedOriginalFiles': result['protectedFiles'],
           'beforeAfterUnchanged': result['sourceAndInheritedInputsBeforeAfterUnchanged'],
           'engineBuilt': False, 'guestExecuted': False,
           'qualification': 'Actual SDK syntax only. Full original input ledger is descriptor-referenced, not copied here. Dependency values authenticated against that before/final-protected ledger and actual430 Source; no compiler replay.'}
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({'passed': True, 'copies': len(copies), 'dependencies': len(dependencies),
                  'uniqueDependencies': summary['uniqueResolvedDependencies'], 'engineBuilt': False}))
