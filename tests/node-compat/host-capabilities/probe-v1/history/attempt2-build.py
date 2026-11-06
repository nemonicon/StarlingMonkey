"""Build a small actual standard-WASI probe; no StarlingMonkey/profile adoption."""
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SDK = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build/cache/wasi-sdk/85e6')
TOOLS = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build/cache/wasm-tools/1448/wasm-tools')
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


assert __debug__ and sys.flags.isolated == 1 and sys.dont_write_bytecode
assert len(sys.argv) == 2
output = Path(sys.argv[1]).resolve()
assert str(output).startswith('/private/tmp/starling-node-compat/deployment-probe-')
assert not output.exists()
output.mkdir(mode=0o700)
source = output / 'source'; source.mkdir()
wit = output / 'wit'; wit.mkdir()
shutil.copytree(REPO / 'host-apis/wasi-0.2.10/wit/deps', wit / 'deps')
shutil.copyfile(HERE / 'profile.wit', wit / 'profile.wit')
shutil.copyfile(HERE / 'probe.c', source / 'probe.c')
bindings = REPO / 'host-apis/wasi-0.2.10/bindings'
shutil.copyfile(bindings / 'bindings.h', source / 'bindings.h')
original = (bindings / 'bindings.c').read_text()
cli = '__attribute__((__export_name__("wasi:cli/run@0.2.10#run")))'
http = '__attribute__((__export_name__("wasi:http/incoming-handler@0.2.10#handle")))'
force = '// Ensure that the *_component_type.o object is linked in'
assert original.count(cli) == original.count(http) == original.count(force) == 1
start, end = original.index(cli), original.index(http)
derived = original[:start] + original[end:]
derived = derived[:derived.index(force)]
(source / 'bindings.c').write_text(derived)
spec = importlib.util.spec_from_file_location('deployment_probe_monitor', MONITOR)
monitor = importlib.util.module_from_spec(spec); spec.loader.exec_module(monitor)
assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
env = {key: os.environ[key] for key in ('HOME', 'USER', 'LOGNAME') if key in os.environ}
env['PATH'] = '/usr/bin:/bin'
commands = [
    [str(SDK / 'bin/clang'), '--target=wasm32-wasi', '-std=c17', '-O2', '-DNDEBUG',
     '-Wall', '-Werror', '-ffunction-sections', '-fdata-sections', '-nostartfiles',
     '-Wl,--no-entry', '-Wl,--gc-sections', str(source / 'probe.c'), str(source / 'bindings.c'),
     '-o', str(output / 'probe.core.wasm')],
    [str(TOOLS), 'component', 'embed', str(wit), '--world', 'profile', str(output / 'probe.core.wasm'), '-o', str(output / 'probe.embedded.wasm')],
    [str(TOOLS), 'component', 'new', str(output / 'probe.embedded.wasm'), '-o', str(output / 'probe.component.wasm')],
    [str(TOOLS), 'validate', str(output / 'probe.component.wasm')],
    [str(TOOLS), 'component', 'wit', str(output / 'probe.component.wasm')],
    [str(TOOLS), 'print', str(output / 'probe.core.wasm')],
]
authority = {'schemaVersion': 1, 'state': 'ROOT_STANDARD_WASI_DEPLOYMENT_PROBE_BUILD_V1',
             'source': row(HERE / 'probe.c'), 'world': row(HERE / 'profile.wit'),
             'generatedBindingsBefore': row(bindings / 'bindings.c'), 'generatedHeader': row(bindings / 'bindings.h'),
             'derivedBindings': row(source / 'bindings.c'), 'compiler': row(SDK / 'bin/clang'), 'wasmTools': row(TOOLS),
             'commands': commands, 'derivedRule': 'Remove unused CLI run export wrapper and old-world force-link paragraph; keep all standard ABI implementations unchanged and embed selected WIT metadata separately.',
             'guestOrHostExecutionAllowed': False, 'starlingMonkeyEngineChanged': False}
authority_path = output / 'build-authority.json'
authority_path.write_text(json.dumps(authority, indent=2) + '\n')
steps = []
for number, argv in enumerate(commands):
    logs = output / ('step-' + str(number)); logs.mkdir()
    terminal = monitor.monitor(argv, str(output), env, logs, 120, row(authority_path))
    clean = (terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone']
             and terminal['parentOwnedGroupGone'] and not terminal['timeout'] and not terminal['forcedCleanup']
             and all(terminal[key] == [] for key in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
    steps.append({'argv': argv, 'terminal': row(logs / 'terminal.json'), 'passed': bool(clean)})
    (output / 'build-steps.json').write_text(json.dumps(steps, indent=2) + '\n')
    if not clean:
        print(json.dumps({'passed': False, 'failedStep': number, 'rawExitCode': terminal['rawExitCode'], 'stderr': str(logs / 'stderr.log')}))
        raise SystemExit(1)
wit_text = (output / 'step-4/stdout.log').read_text()
core_text = (output / 'step-5/stdout.log').read_text()
imports = sorted(line.strip()[7:-1] for line in wit_text.splitlines() if line.strip().startswith('import '))
exports = sorted(line.strip()[7:-1] for line in wit_text.splitlines() if line.strip().startswith('export '))
allowed = sorted(line.strip()[7:-1] for line in (HERE / 'profile.wit').read_text().splitlines() if line.strip().startswith('import '))
assert set(imports) <= set(allowed)
assert exports == ['wasi:http/incoming-handler@0.2.10']
assert 'wasi_snapshot_preview1' not in core_text
assert all(row(HERE / name)['sha256'] == authority[key]['sha256'] for name, key in [('probe.c', 'source'), ('profile.wit', 'world')])
result = {'schemaVersion': 1, 'state': 'ACTUAL_STANDARD_WASI_DEPLOYMENT_PROBE_COMPONENT_V1',
          'passed': True, 'component': row(output / 'probe.component.wasm'), 'core': row(output / 'probe.core.wasm'),
          'imports': imports, 'exports': exports, 'unusedSelectedInterfaces': sorted(set(allowed) - set(imports)),
          'preview1Imports': False, 'adapterUsed': False, 'steps': steps,
          'guestExecuted': False, 'starlingMonkeyEngine': False, 'nextApplication': False}
(output / 'component-audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
