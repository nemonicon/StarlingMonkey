"""Own a stock-host component probe. Native/profile/Next builds are not invoked."""
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
NODE = Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'


def row(path):
    data = Path(path).read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


assert sys.dont_write_bytecode and sys.flags.isolated == 1 and __debug__
assert len(sys.argv) in (3, 4)
output, build = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
assert str(output).startswith('/private/tmp/starling-node-compat/deployment-host-') and not output.exists()
logs = Path(str(output) + '-monitor'); logs.mkdir(mode=0o700)
assert row(NODE)['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
entry = HERE / ('run-wasmcloud.mjs' if len(sys.argv) == 4 and sys.argv[3] == 'wasmcloud' else 'run-wasmtime.mjs')
argv = [str(NODE), str(entry), str(output), str(build)]
authority = {'schemaVersion': 1, 'state': 'ROOT_ACTUAL_STANDARD_WASI_HOST_PROBE_V1', 'argv': argv,
             'entry': row(entry), 'componentAudit': row(build / 'component-audit.json'),
             'node': row(NODE), 'monitor': row(MONITOR), 'timeoutSeconds': 180,
             'localhostOnly': True, 'freshOwnedFilesystem': True, 'starlingMonkeyOrNextAllowed': False}
path = logs / 'authority.json'; path.write_text(json.dumps(authority, indent=2) + '\n')
spec = importlib.util.spec_from_file_location('owned_deployment_host_monitor', MONITOR)
monitor = importlib.util.module_from_spec(spec); spec.loader.exec_module(monitor)
env = {key: os.environ[key] for key in ('HOME', 'USER', 'LOGNAME') if key in os.environ}
env['PATH'] = str(NODE.parent) + ':/usr/bin:/bin'
terminal = monitor.monitor(argv, str(REPO), env, logs, 180, row(path))
clean = (terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] and terminal['parentOwnedGroupGone']
         and not terminal['timeout'] and not terminal['forcedCleanup']
         and all(terminal[key] == [] for key in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
print(json.dumps({'passed': bool(clean), 'rawExitCode': terminal['rawExitCode'], 'terminal': row(logs / 'terminal.json')}))
raise SystemExit(0 if clean else 1)
