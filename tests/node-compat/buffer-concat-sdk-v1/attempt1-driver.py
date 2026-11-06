"""One actual SDK30/SM147 syntax check; no object, link, engine or guest action."""
import hashlib
import importlib.util
import json
import os
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = HERE.parent / 'buffer-concat-candidate-v1'
BUILD = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build')
DB = BUILD / 'engine-abi-fixed-bigint-v1-hash-hmac357-v1.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1/compile_commands.json'
CLANG = BUILD / 'cache/wasi-sdk/85e6/bin/clang++'
MONITOR = HERE.parent / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


assert __debug__ and sys.flags.isolated == 1 and sys.dont_write_bytecode
assert len(sys.argv) == 2
output = Path(sys.argv[1]).resolve()
assert str(output).startswith('/private/tmp/starling-node-compat/buffer-concat-sdk-')
assert not output.exists()
assert row(SOURCE / 'index.json')['sha256'] == '1c7b431e3b131a11fc4edba0f83a25b8e0eb5891c67e37e8a1a18ca24a0ba155'
assert row(DB)['sha256'] == '2ebb84ea6642d9c8199d8ab0bb03083d218fa19bc83f2c001d9ec97a00f1b830'
assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
source_rows = json.loads((SOURCE / 'index.json').read_text())['files']
for item in source_rows:
    assert all(row(SOURCE / item['path'])[key] == item[key] for key in ('sha256', 'bytes'))
commands = [item for item in json.loads(DB.read_text()) if item['file'].endswith('/builtins/node-compat/buffer.cpp')]
assert len(commands) == 1
command = commands[0]
original = shlex.split(command['command'])
args, index = [], 1
while index < len(original):
    token = original[index]
    if token in ('-o', '-c', '-MF', '-MT'):
        index += 2
    elif token in ('-MD', '-MMD'):
        index += 1
    else:
        args.append(token)
        index += 1
assert '-DNDEBUG' in args and '--target=wasm32-wasi' in args
assert not any('DEBUG=' in arg or 'GC_STRESS' in arg or 'OOM_TESTING' in arg or arg.startswith('@') for arg in args)
source = SOURCE / 'native/builtins/node-compat/buffer.cpp'
output.mkdir(mode=0o700)
argv = [str(CLANG), *args, '-fsyntax-only', '-MD', '-MF', str(output / 'dependencies.d'),
        '-MT', 'buffer-concat-syntax', str(source)]
authority = {'schemaVersion': 1, 'state': 'ROOT_BUFFER_CONCAT_SDK_SYNTAX_V1',
             'sourceIndex': row(SOURCE / 'index.json'), 'source': row(source),
             'database': row(DB), 'originalCommand': command, 'argv': argv,
             'compiler': row(CLANG), 'monitor': row(MONITOR), 'timeoutSeconds': 60,
             'nativeObjectAllowed': False, 'linkAllowed': False, 'guestAllowed': False}
authority_path = output / 'authority.json'
authority_path.write_text(json.dumps(authority, indent=2) + '\n')
spec = importlib.util.spec_from_file_location('concat_sdk_owned_monitor', MONITOR)
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)
env = {key: os.environ[key] for key in ('HOME', 'USER', 'LOGNAME') if key in os.environ}
env['PATH'] = '/usr/bin:/bin'
terminal = monitor.monitor(argv, command['directory'], env, output, 60, row(authority_path))
preserved = all(row(path)[key] == before[key] for path, before in
                ((source, authority['source']), (DB, authority['database']), (CLANG, authority['compiler'])))
clean = (terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone']
         and terminal['allObservedOwnedGroupsGone'] and not terminal['timeout']
         and not terminal['forcedCleanup'] and all(terminal[key] == [] for key in
             ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
dependencies = []
if (output / 'dependencies.d').exists():
    text = (output / 'dependencies.d').read_text().replace('\\\n', '')
    target, paths = text.split(':', 1)
    assert target == 'buffer-concat-syntax'
    dependencies = [row(Path(command['directory']) / path) for path in shlex.split(paths)]
result = {'schemaVersion': 1, 'state': 'BUFFER_CONCAT_ACTUAL_SDK_SYNTAX_RESULT_V1',
          'passed': bool(clean and preserved), 'sourceCompilerDatabasePreserved': preserved,
          'rawExitCode': terminal['rawExitCode'], 'ownedGroupsClean': clean,
          'authority': row(authority_path), 'terminal': row(output / 'terminal.json'),
          'dependenciesCapturedAfterCompile': dependencies,
          'scope': 'Actual fsyntax-only; dependency hashes captured after compile, not a whole-SDK before/after preservation proof',
          'objectBuilt': False, 'engineLinked': False, 'guestExecuted': False}
(output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': result['passed'], 'rawExitCode': terminal['rawExitCode'],
                  'dependencies': len(dependencies), 'result': row(output / 'result.json')}), flush=True)
raise SystemExit(0 if result['passed'] else 1)
