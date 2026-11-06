"""SDK30/SM147 syntax for the actual new CJS kernel; no link or guest action."""
import hashlib
import importlib.util
import json
import os
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'node-module-candidate-v1'
V2 = HERE.parent / 'node-module-candidate-v2'
BUILD = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build')
DB = BUILD / 'engine-abi-fixed-bigint-v1-hash-hmac357-v1.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1/compile_commands.json'
CLANG = BUILD / 'cache/wasi-sdk/85e6/bin/clang++'
MONITOR = HERE.parents[1] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


assert __debug__ and sys.flags.isolated == 1 and sys.dont_write_bytecode
assert len(sys.argv) == 2
output = Path(sys.argv[1]).resolve()
assert str(output).startswith('/private/tmp/starling-node-compat/node-module-sdk-')
assert not output.exists()
assert row(BASE / 'index.json')['sha256'] == '29f603f7652acabef8adfa12217c70cec177d8aaf07f177f0d09031f2a99009e'
assert row(V2 / 'index.json')['sha256'] == 'c69350e3ed12574b2a21b0a5c224d9e16c70c5ec725c3da3b14c1ad860812687'
assert row(DB)['sha256'] == '2ebb84ea6642d9c8199d8ab0bb03083d218fa19bc83f2c001d9ec97a00f1b830'
assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
commands = [item for item in json.loads(DB.read_text()) if item['file'].endswith('/builtins/node-compat/buffer.cpp')]
assert len(commands) == 1
command = commands[0]
original = shlex.split(command['command'])
flags, position = [], 1
while position < len(original):
    token = original[position]
    if token in ('-o', '-c', '-MF', '-MT'):
        position += 2
    elif token in ('-MD', '-MMD'):
        position += 1
    else:
        flags.append(token)
        position += 1
assert '-DNDEBUG' in flags and '--target=wasm32-wasi' in flags
assert not any('DEBUG=' in arg or 'GC_STRESS' in arg or 'OOM_TESTING' in arg or arg.startswith('@') for arg in flags)
inputs = {name: row(path) for name, path in (
    ('kernel', BASE / 'module-kernel.cpp'), ('scriptLoaderHeader', BASE / 'after/runtime/script_loader.h'),
    ('entropyHeader', BASE / 'after/include/node-compat-entropy.h'), ('sourceIndex', V2 / 'index.json'),
    ('database', DB), ('compiler', CLANG), ('driver', Path(__file__).resolve()))}
output.mkdir(mode=0o700)
argv = [str(CLANG), '-DNODE_COMPAT_MODULE=1', '-I' + str(BASE / 'after/runtime'),
        '-I' + str(BASE / 'after/include'), *flags, '-fsyntax-only', '-MD', '-MF', str(output / 'dependencies.d'),
        '-MT', 'node-module-kernel-syntax', str(BASE / 'module-kernel.cpp')]
authority = {'schemaVersion': 1, 'state': 'ROOT_NODE_MODULE_KERNEL_SDK_SYNTAX_V1',
             'inputs': inputs, 'originalCommand': command, 'argv': argv, 'timeoutSeconds': 60,
             'scope': 'New module kernel plus explicit new declaration headers, inherited genuine native target flags; not a built CMake module command.',
             'objectAllowed': False, 'linkAllowed': False, 'guestAllowed': False}
authority_path = output / 'authority.json'
authority_path.write_text(json.dumps(authority, indent=2) + '\n')
spec = importlib.util.spec_from_file_location('module_sdk_owned_monitor', MONITOR)
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)
env = {key: os.environ[key] for key in ('HOME', 'USER', 'LOGNAME') if key in os.environ}
env['PATH'] = '/usr/bin:/bin'
terminal = monitor.monitor(argv, command['directory'], env, output, 60, row(authority_path))
preserved = all(row(Path(item['path'])) == item for item in inputs.values())
clean = (terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone']
         and not terminal['timeout'] and not terminal['forcedCleanup']
         and all(terminal[key] == [] for key in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
dependencies = []
if (output / 'dependencies.d').exists():
    target, paths = (output / 'dependencies.d').read_text().replace('\\\n', '').split(':', 1)
    assert target == 'node-module-kernel-syntax'
    dependencies = [row(Path(command['directory']) / path) for path in shlex.split(paths)]
result = {'schemaVersion': 1, 'state': 'NODE_MODULE_ACTUAL_KERNEL_SDK_SYNTAX_V1',
          'passed': bool(terminal['rawExitCode'] == 0 and clean and preserved), 'rawExitCode': terminal['rawExitCode'],
          'ownedGroupsClean': bool(clean), 'declaredInputsPreserved': preserved,
          'authority': row(authority_path), 'terminal': row(output / 'terminal.json'),
          'dependenciesCapturedAfterCompile': dependencies,
          'limitations': 'No whole-SDK before/after preservation proof; registration, script-loader implementation, linking and guest execution untested.',
          'objectBuilt': False, 'engineLinked': False, 'guestExecuted': False}
(output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': result['passed'], 'rawExitCode': terminal['rawExitCode'],
                  'dependencies': len(dependencies), 'result': row(output / 'result.json')}), flush=True)
raise SystemExit(0 if result['passed'] else 1)
