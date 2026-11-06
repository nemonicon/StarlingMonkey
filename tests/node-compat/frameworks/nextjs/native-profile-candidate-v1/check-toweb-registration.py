"""Actual final registrar frontend for the ToWeb-only Source successor."""
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
BASE = Path('/private/tmp/starling-node-compat')
PROFILE = BASE / 'next-native-profile-v3'
PARENT = BASE / 'next-native-profile-v2'
OUT = BASE / 'next-toweb-registration-sdk-v1'
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'


def row(p):
    p = Path(p); b = p.read_bytes()
    return {'path': str(p), 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}


assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1
assert sys.argv[1:] == ['--execute-root-authorized-frontend'] and not OUT.exists()
composition = json.loads((PROFILE / 'composition.json').read_text())
parent = json.loads((PARENT / 'composition.json').read_text())
assert len(composition['files']) == 432 and len(parent['files']) == 430
original = {r['path']: r['sha256'] for r in parent['files']}
changed = [r['path'] for r in composition['files'] if original.get(r['path']) != r['sha256']]
assert changed == ['builtins/node-compat/classic-streams/export-manifest.classic-toweb.node-v22.14.0.json',
                   'builtins/node-compat/classic-streams/toweb-factories.generated.h',
                   'builtins/node-compat/register.cpp', 'cmake/builtins.cmake'], changed
prior = json.loads((BASE / 'next-combined-sdk-syntax-v2/result.json').read_text()); assert prior['passed']
installed = json.loads((PROFILE / 'installed-checks/result.json').read_text()); assert installed['passed']
oldplan = json.loads((BASE / 'next-combined-sdk-syntax-v2/plan.json').read_text())
unit = next(r for r in oldplan if r['relativePath'] == 'builtins/node-compat/register.cpp')
argv = [s.replace(str(PARENT), str(PROFILE)).replace(str(BASE / 'next-combined-sdk-syntax-v2'), str(OUT)) for s in unit['argv']]
assert '-DNODE_COMPAT_CLASSIC_STREAMS_TOWEB=1' not in argv
argv.insert(1, '-DNODE_COMPAT_CLASSIC_STREAMS_TOWEB=1')
assert '-c' not in argv and '-o' not in argv and argv.count('-fsyntax-only') == 1
assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
ledger = json.loads((BASE / 'node-crypto-hash-hmac-v3-artifact-revalidation-v2/current-input-hashes.json').read_text())['files']
protected = ledger + [row(PROFILE / 'source' / r['path']) for r in composition['files']]
protected += [row(__file__), row(PROFILE / 'composition.json'), row(PROFILE / 'installed-checks/result.json')]


def check():
    for r in protected: assert row(r['path']) == r, r['path']
    assert sorted(p.relative_to(PROFILE / 'source').as_posix() for p in (PROFILE / 'source').rglob('*') if p.is_file()) == [r['path'] for r in composition['files']]


check()
OUT.mkdir(mode=0o700); (OUT / 'command').mkdir(); (OUT / 'tmp').mkdir()
authority = {'schemaVersion': 1, 'state': 'ROOT_NEXT432_TOWEB_REGISTRATION_SDK_AUTHORIZED_V1',
             'composition': row(PROFILE / 'composition.json'), 'parentThirteenResult': row(BASE / 'next-combined-sdk-syntax-v2/result.json'),
             'installedCheck': row(PROFILE / 'installed-checks/result.json'), 'driver': row(__file__),
             'changedPaths': changed, 'argv': argv, 'timeoutSeconds': 120, 'objectLinkEngineGuestAllowed': False}
(OUT / 'authority.json').write_text(json.dumps(authority, indent=2) + '\n')
spec = importlib.util.spec_from_file_location('original_toweb_syntax_monitor', MONITOR)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
env.update(PATH='/usr/bin:/bin', TMPDIR=str(OUT / 'tmp'))
t = m.monitor(argv, unit['cwd'], env, OUT / 'command', 120, row(OUT / 'authority.json'))
check()
passed = (t['rawExitCode'] == 0 and t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone']
          and not t['timeout'] and not t['forcedCleanup']
          and all(t[k] == [] for k in ('errors','signals','interruptedSignals','remainingObservedPids')))
result = {'schemaVersion': 1, 'state': 'ACTUAL_NEXT432_FINAL_REGISTRAR_SDK_RESULT_V1',
          'passed': bool(passed), 'nativeSourceFiles': 432, 'actualNewFrontends': 1,
          'parentThirteenResult': authority['parentThirteenResult'], 'onlyNativeCppChanged': 'builtins/node-compat/register.cpp',
          'changedPaths': changed, 'terminal': t, 'beforeAfterProtectedFiles': len(protected),
          'beforeAfterUnchanged': True, 'engineOrGuestExecuted': False}
(OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': passed, 'actualNewFrontends': 1, 'rawExitCode': t['rawExitCode'], 'result': row(OUT / 'result.json')}))
raise SystemExit(0 if passed else 1)
