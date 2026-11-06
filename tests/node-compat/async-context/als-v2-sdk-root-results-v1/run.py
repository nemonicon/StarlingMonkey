"""Root authorizes only the reviewed13 ALS SDK syntax frontends."""
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'native-als-candidate-v2'
MONITOR = HERE.parents[1] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
PYTHON = Path('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9')
LOGS = Path('/private/tmp/starling-node-compat/native-als-v2-sdk-syntax-v1-root-monitor')


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


assert __debug__ and sys.flags.isolated == 1 and sys.dont_write_bytecode
assert row(SOURCE / 'index.json')['sha256'] == '7e4265c2278d7872d0eee610a1975b6d5750a9615cc5a526fca8266a32a9aabc'
assert row(SOURCE / 'sdk-plan.json')['sha256'] == 'a56b7e10e0dc82255874f5caa03a6315dca753ffe3c1b1bbf514d8ab684a4a41'
assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
assert not LOGS.exists()
LOGS.mkdir(mode=0o700)
authority = json.loads((SOURCE / 'sdk-root-authority-template.json').read_text())
authority.update(sourceIndex=row(SOURCE / 'index.json'), plan=row(SOURCE / 'sdk-plan.json'),
                 sourceReviewedForFrontend=True, syntaxOnlyCompilerAllowed=True)
authority['reviewScope'] = 'Root reviewed45 indexed payload hashes, actual private-ABI/realm/ownership design and all13 compiler argv for syntax-only execution; not an ALS semantic/runtime acceptance.'
authority['remaining'] = ['Actual native Promise/task propagation and tracing are unproved.',
                          'Private reaction layout and fatal metadata OOM policy require actual bounded guest tests.',
                          'No final Next composition/metadata/link or deployed snapshot/reset acceptance.']
path = HERE / 'authority.json'
with path.open('x') as file:
    json.dump(authority, file, indent=2); file.write('\n')
argv = [str(PYTHON), '-B', '-I', str(SOURCE / 'run-sdk-syntax.py'),
        '--execute-root-authorized-frontends', json.dumps(row(path), separators=(',', ':'))]
spec = importlib.util.spec_from_file_location('als_sdk_root_monitor', MONITOR)
monitor = importlib.util.module_from_spec(spec); spec.loader.exec_module(monitor)
env = {key: os.environ[key] for key in ('HOME', 'USER', 'LOGNAME') if key in os.environ}
env['PATH'] = '/usr/bin:/bin'
terminal = monitor.monitor(argv, str(HERE), env, LOGS, 2400, row(path))
clean = (terminal['allObservedOwnedGroupsGone'] and terminal['parentOwnedGroupGone']
         and not terminal['timeout'] and not terminal['forcedCleanup']
         and all(terminal[key] == [] for key in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
summary = {'schemaVersion': 1, 'state': 'ROOT_OBSERVED_ALS_V2_SDK_FRONTENDS_V1',
           'rawExitCode': terminal['rawExitCode'], 'cleanOwnedGroups': bool(clean),
           'terminal': row(LOGS / 'terminal.json'), 'authority': row(path),
           'guestOrEngineExecuted': False}
(HERE / 'root-result.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary), flush=True)
raise SystemExit(0 if clean and terminal['rawExitCode'] == 0 else 1)
