"""Root authorizes only the reviewed13 corrected ALS SDK syntax frontends."""
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'native-als-candidate-v3'
MONITOR = HERE.parents[1] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
PYTHON = Path('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9')
LOGS = Path('/private/tmp/starling-node-compat/native-als-v3-sdk-syntax-v1-root-monitor')


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


assert __debug__ and sys.flags.isolated == 1 and sys.dont_write_bytecode
assert row(SOURCE / 'index.json')['sha256'] == '44d7baf5c61e305d76ff5469f395235cdee0ca80c852714204f4c446d8bc66bc'
assert row(SOURCE / 'sdk-plan.json')['sha256'] == 'cbb48b94cc3d1aec8df403e6241f7fb4d73a5cc63946d7af6776567506d1e4aa'
assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
assert not LOGS.exists()
LOGS.mkdir(mode=0o700)
authority = json.loads((SOURCE / 'sdk-root-authority-template.json').read_text())
authority.update(sourceIndex=row(SOURCE / 'index.json'), plan=row(SOURCE / 'sdk-plan.json'),
                 sourceReviewedForFrontend=True, syntaxOnlyCompilerAllowed=True)
authority['reviewScope'] = 'Root reviewed the compact V3 correction and its whole V2 parent, the two exact actual-SDK repairs and preserved13 syntax-only commands; not an ALS semantic/runtime acceptance.'
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
summary = {'schemaVersion': 1, 'state': 'ROOT_OBSERVED_ALS_V3_SDK_FRONTENDS_V1',
           'rawExitCode': terminal['rawExitCode'], 'cleanOwnedGroups': bool(clean),
           'terminal': row(LOGS / 'terminal.json'), 'authority': row(path),
           'guestOrEngineExecuted': False}
(HERE / 'root-result.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary), flush=True)
raise SystemExit(0 if clean and terminal['rawExitCode'] == 0 else 1)
