"""Actual SDK compiler, isolated source overlay, syntax only (never linked)."""
from pathlib import Path
import hashlib
import json
import shlex
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'source'
OLD_SOURCE = '/tmp/starling-node-compat/add-abort-m0.10-proposal/source'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
original_path = HERE.parents[1] / 'm0.10-proposal/syntax-results.json'
original = json.loads(original_path.read_text())
freeze = Path('/tmp/starling-node-compat/foundations-v8/native-freeze')
commands_path = freeze / 'off-compile_commands.json'
assert sha(commands_path) == original['baseCompileCommandsSha256'] == 'bc4649a72380e2c59b2eccf678765f1225476886585c1035e7de063b12aa30c8'
cases = []
for entry in original['cases']:
    args = [value.replace(OLD_SOURCE, str(SOURCE)) for value in entry['command']]
    if entry['path'].endswith('register.cpp'):
        args.append('-DNODE_COMPAT_STREAM_WEB=1')
    cases.append((entry['path'], entry['feature'], entry['strict'], args))
entry = next(e for e in json.loads(commands_path.read_text()) if e['file'].endswith('/builtins/web/event/global-event-target.cpp'))
args = []
skip = False
repo = str(HERE.parents[4])
for value in shlex.split(entry['command']):
    if skip:
        skip = False
        continue
    if value in ['-o', '-MF', '-MT', '-MQ']:
        skip = True
        continue
    if value in ['-c', '-MD', '-MMD']:
        continue
    args.append(value.replace(repo + '/', str(SOURCE) + '/'))
args[1:1] = ['-I' + str(SOURCE / 'include'), '-I' + str(SOURCE / 'runtime'), '-I' + str(SOURCE)]
args.extend(['-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1', '-fsyntax-only'])
cases.append(('builtins/web/event/global-event-target.cpp', True, True, args))
results = []
for path, selected, strict, command in cases:
    process = subprocess.run(command, capture_output=True, text=True)
    result = {'path': path, 'selected': selected, 'strict': strict, 'command': command,
              'sourceSha256': sha(SOURCE / path), 'compilerWrapperSha256': sha(Path(command[0])),
              'exitCode': process.returncode, 'stdout': process.stdout, 'stderr': process.stderr}
    results.append(result)
    if process.returncode:
        break
report = {'state': 'ACTUAL_SDK30_SM147_SYNTAX_ONLY',
          'derivedFromImmutableV8Commands': str(commands_path),
          'baseCommandSha256': sha(commands_path), 'sourceOverlay': str(SOURCE),
          'streamWebMacroAddedForRegistrationCoverage': True,
          'actualFutureNativeBuildConfiguration': False,
          'driverSha256': sha(Path(__file__)), 'cases': results,
          'linked': False, 'engineBuilt': False, 'guestExecuted': False}
(HERE / 'syntax-results.json').write_text(json.dumps(report, indent=2) + '\n')
assert len(results) == len(cases) and all(case['exitCode'] == 0 for case in results)
print(json.dumps({'syntaxCases': len(cases), 'passed': True, 'engineBuilt': False}))
