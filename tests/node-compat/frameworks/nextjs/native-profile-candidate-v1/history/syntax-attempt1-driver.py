"""Root's syntax-only checks of the complete new installed Source generation.

Use genuine old compile flags as a template, with explicitly recorded new
definitions/source paths. This is not observed new CMake metadata or a build.
"""
import hashlib
import importlib.util
import json
import os
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
BASE = Path('/private/tmp/starling-node-compat')
SOURCE_ROOT = BASE / 'next-native-profile-v2'
SOURCE = SOURCE_ROOT / 'source'
OUT = BASE / 'next-combined-sdk-syntax-v1'
OLD_SOURCE = str(BASE / 'node-crypto-hash-hmac-v1-source')
OLD_WORK = BASE / 'node-crypto-hash-hmac-v3-build'
OLD_BUILD = OLD_WORK / 'engine-abi-fixed-bigint-v1-hash-hmac357-v1.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1'
DATABASE = OLD_BUILD / 'compile_commands.json'
LEDGER = BASE / 'node-crypto-hash-hmac-v3-artifact-revalidation-v2/current-input-hashes.json'
ALIASES = REPO / 'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-artifact-revalidation-candidate-v1/reference-aliases.json'
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
COMPILER = OLD_WORK / 'cache/wasi-sdk/85e6/bin/clang++'


def row(path):
    path = Path(path); data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def clean(t):
    return (t['rawExitCode'] == 0 and t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone']
            and not t['timeout'] and not t['forcedCleanup']
            and all(t[k] == [] for k in ('errors','signals','interruptedSignals','remainingObservedPids')))


assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1
assert sys.argv[1:] == ['--execute-root-authorized-frontends']
assert not OUT.exists(), 'Fresh output only; never replay a failed generation'
assert row(DATABASE)['sha256'] == '2ebb84ea6642d9c8199d8ab0bb03083d218fa19bc83f2c001d9ec97a00f1b830'
assert row(LEDGER)['sha256'] == '612818f6a319bfcc93b9583f045e3422d9f8a3a8738011ccd55026c365c520a0'
assert row(ALIASES)['sha256'] == '8592569695c33178ff12a33f8c9f7599f4d5e1c5e15541d7aa3e399074ec7649'
assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
composition = json.loads((SOURCE_ROOT / 'composition.json').read_text())
assert len(composition['files']) == 430 and not composition['engineBuilt']
installed = json.loads((SOURCE_ROOT / 'installed-checks/result.json').read_text())
assert installed['passed'] and installed['sourceBeforeAfterUnchanged'] and len(installed['commands']) == 8
inherited = json.loads(LEDGER.read_text())['files']
aliases = json.loads(ALIASES.read_text())
protected = inherited + [row(SOURCE / r['path']) for r in composition['files']]
protected += [row(p) for p in sorted((SOURCE_ROOT / 'componentize-source').rglob('*')) if p.is_file()]
protected += [row(__file__), row(SOURCE_ROOT / 'composition.json'), row(SOURCE_ROOT / 'installed-checks/result.json')]


def check_inputs():
    for r in protected:
        assert row(r['path']) == r, ('input changed', r['path'])
    assert sorted(p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob('*') if p.is_file()) == [r['path'] for r in composition['files']]
    for alias in aliases['symlinks']:
        p = Path(alias['path'])
        assert p.is_symlink() and os.readlink(p) == alias['linkText'] and str(p.resolve()) == alias['resolved'], alias


check_inputs()
database = json.loads(DATABASE.read_text())
base_entry = next(r for r in database if r['file'].endswith('/builtins/node-compat/register.cpp'))
new_definitions = ['MODULE','ASYNC_LOCAL_STORAGE','TIMERS','NEXT_PERFORMANCE','FS','NEXT_STARTUP',
                   'CRYPTO_RANDOM','NEXT_HTTP','NEXT_IMPORTS','VM_DATA','ZLIB_STREAMING']
units = ['builtins/node-compat/' + n for n in (
    'register.cpp','module-kernel.cpp','next-startup.cpp','next-http/next-http.cpp',
    'next-imports/next-imports.cpp','zlib/stream-kernel.cpp','vm-data-kernel.cpp')]
units += ['runtime/' + n for n in ('script_loader.cpp','engine.cpp','async_context_runtime.cpp',
                                 'async_context_queue.cpp','event_loop.cpp')]
units += ['builtins/web/timers.cpp']
plan = []
for relative in units:
    original = next((r for r in database if r['file'] == OLD_SOURCE + '/' + relative), base_entry)
    words = shlex.split(original['command'])
    argv, removed = [str(COMPILER)], []
    i = 1
    while i < len(words):
        word = words[i]
        if word in ('-o','-MF','-MT','-MQ'):
            removed.extend(words[i:i+2]); i += 2; continue
        if word in ('-c','-MD','-MMD','-MP') or word == original['file']:
            removed.append(word); i += 1; continue
        argv.append(word.replace(OLD_SOURCE, str(SOURCE))); i += 1
    for definition in new_definitions:
        flag = '-DNODE_COMPAT_' + definition + '=1'
        if flag not in argv: argv.append(flag)
    if '-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1' not in argv: argv.append('-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1')
    argv += ['-I' + str(SOURCE / 'builtins/node-compat'), '-I' + str(SOURCE / 'builtins/web')]
    identity = relative.replace('/', '-').replace('.cpp','')
    argv += ['-fsyntax-only','-MD','-MF',str(OUT / (identity + '.d')),'-MT',identity,'-x','c++',str(SOURCE / relative)]
    assert '-c' not in argv and '-o' not in argv and argv.count('-fsyntax-only') == 1
    plan.append({'id': identity, 'relativePath': relative, 'actualTemplate': original,
                 'removed': removed, 'argv': argv, 'cwd': original['directory'], 'timeoutSeconds': 120})
OUT.mkdir(mode=0o700)
(OUT / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
authority = {'schemaVersion': 1, 'state': 'ROOT_JOINED_NEXT430_SDK_FRONTENDS_AUTHORIZED_V1',
             'sourceComposition': row(SOURCE_ROOT / 'composition.json'), 'installedCheck': row(SOURCE_ROOT / 'installed-checks/result.json'),
             'driver': row(__file__), 'plan': row(OUT / 'plan.json'), 'compiler': row(COMPILER),
             'monitor': row(MONITOR), 'protectedFiles': len(protected), 'declaredAliases': len(aliases['symlinks']),
             'nativeFrontendUnits': len(plan), 'perUnitTimeoutSeconds': 120,
             'objectLinkEngineGuestAllowed': False, 'scope': 'actual full installed Source, requested syntax definitions only; no new build metadata'}
(OUT / 'authority.json').write_text(json.dumps(authority, indent=2) + '\n')
spec = importlib.util.spec_from_file_location('owned_joined_next_syntax_monitor', MONITOR)
monitor = importlib.util.module_from_spec(spec); spec.loader.exec_module(monitor)
env = {k: os.environ[k] for k in ('HOME','USER','LOGNAME') if k in os.environ}
env.update(PATH='/usr/bin:/bin', TMPDIR=str(OUT / 'tmp'))
(OUT / 'tmp').mkdir()
terminals, error, final_unchanged = [], None, False
try:
    for unit in plan:
        terminal = monitor.monitor(unit['argv'], unit['cwd'], env, OUT / unit['id'], 120, row(OUT / 'authority.json'))
        terminals.append({'id': unit['id'], 'terminal': terminal})
        print(json.dumps({'id': unit['id'], 'rawExitCode': terminal['rawExitCode']}), flush=True)
finally:
    try: check_inputs(); final_unchanged = True
    except Exception as ex: error = {'type': type(ex).__name__, 'message': str(ex)}
    result = {'schemaVersion': 1, 'state': 'ACTUAL_JOINED_NEXT430_SDK_SYNTAX_RESULT_V1',
              'passed': len(terminals) == len(plan) and all(clean(r['terminal']) for r in terminals) and final_unchanged,
              'terminals': terminals, 'protectedFiles': len(protected), 'sourceAndInheritedInputsBeforeAfterUnchanged': final_unchanged,
              'inputProtectionError': error, 'nativeOrGuestExecuted': False, 'objectOrLinkProduced': False,
              'dependencyFilesRetained': True, 'dependencyHashReview': 'separate data-only postcheck required'}
    (OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': result['passed'], 'units': len(terminals), 'output': str(OUT)}), flush=True)
raise SystemExit(0 if result['passed'] else 1)
