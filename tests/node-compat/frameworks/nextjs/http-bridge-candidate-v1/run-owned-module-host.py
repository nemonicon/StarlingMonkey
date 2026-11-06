"""Own the full Next candidate-CJS-loader host experiment (no native/guest action)."""
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
NODE = Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
SOURCE = '/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/application/.next/standalone'


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1
assert len(sys.argv) in (2, 3)
assert row(NODE)['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
output = Path(sys.argv[1])
assert str(output).startswith('/private/tmp/starling-node-compat/next-http-bridge-module-')
monitor_output = Path(str(output) + '-monitor')
assert not output.exists() and not monitor_output.exists()
argv = [str(NODE), str(HERE / 'run-module-host.mjs'), str(output), SOURCE] + sys.argv[2:]
monitor_output.mkdir(mode=0o700)
authority = {'schemaVersion': 1, 'state': 'ROOT_FULL_NEXT_CANDIDATE_MODULE_HOST_TEST_V1',
             'actualArgv': argv, 'entry': row(HERE / 'run-module-host.mjs'),
             'bridge': row(HERE / 'bridge.mjs'), 'provider': row(HERE / 'module-host-provider.mjs'),
             'moduleCore': row(HERE / '../../../foundation-module/node-module-candidate-v1/module-core.mjs'),
             'node': row(NODE), 'monitor': row(MONITOR), 'timeoutSeconds': 300,
             'freshOwnedApplicationCopy': True, 'localhostHttpAllowed': True,
             'guestExecutionAllowed': False, 'nativeCompilerAllowed': False}
authority_path = monitor_output / 'root-authority.json'
with authority_path.open('x') as file:
    json.dump(authority, file, indent=2)
    file.write('\n')
spec = importlib.util.spec_from_file_location('owned_module_host_monitor', MONITOR)
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)
env = {key: os.environ[key] for key in ('HOME', 'USER', 'LOGNAME') if key in os.environ}
env.update(PATH=str(NODE.parent) + ':/usr/bin:/bin', NODE_ENV='production', NEXT_TELEMETRY_DISABLED='1', CI='1')
terminal = monitor.monitor(argv, str(REPO), env, monitor_output, 300, row(authority_path))
clean = (terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone']
         and terminal['allObservedOwnedGroupsGone'] and not terminal['forcedCleanup']
         and not terminal['timeout'] and all(terminal[key] == [] for key in
             ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
print(json.dumps({'state': 'ROOT_OBSERVED_NEXT_CANDIDATE_MODULE_HOST_TEST',
                  'rawExitCode': terminal['rawExitCode'], 'clean': clean,
                  'terminal': row(monitor_output / 'terminal.json'),
                  'result': row(output / 'result.json') if (output / 'result.json').exists() else None}), flush=True)
raise SystemExit(0 if clean else 1)
