"""Root-owned three-frontend syntax check. No object/link/engine or guest."""
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'next-fs-sdk-syntax-v1'
PYTHON = Path('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9')
MONITOR = HERE.parents[1] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
OUTPUT = Path('/private/tmp/starling-node-compat/next-fs-sdk-syntax-v1-root-monitor')


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1
assert row(SOURCE / 'index.json')['sha256'] == 'c537d70fa52edc8f465353abea13f5b392065c4a06bf9e212afb3e38e0438aba'
assert row(SOURCE / 'plan.json')['sha256'] == 'f87e66776f730d05d53b582157820de7265ab89f411c09da28a8b14c3b12ed67'
assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
assert not OUTPUT.exists(); OUTPUT.mkdir(mode=0o700)
authority = json.loads((SOURCE / 'root-authority-template.json').read_text())
authority.update(state='ROOT_NEXT_FS_SDK_SYNTAX_AUTHORIZED_V1', sourcePlanIndex=row(SOURCE / 'index.json'),
                 plan=row(SOURCE / 'plan.json'), compilerSyntaxAllowed=True)
authority['reviewScope'] = 'Root checked native ownership/resource/phase code, actual owned ArrayBuffer overload and3 compiler argv; safe-constant Source v3 corrects v2 inspection blocker. Frontend permission is not semantic/runtime acceptance.'
authority['remaining'] = ['Actual direct-P2 read/stream/cwd, GC and snapshot/deployed behavior.',
                          'Nested writable cache preopen and readonly parent traversal.',
                          'Full Next composition, native link and API/host differentials.']
path = HERE / 'authority.json'
with path.open('x') as file: json.dump(authority, file, indent=2); file.write('\n')
argv = [str(PYTHON), '-B', '-I', str(SOURCE / 'run-sdk.py'), str(path)]
spec = importlib.util.spec_from_file_location('next_fs_root_owned_monitor', MONITOR)
monitor = importlib.util.module_from_spec(spec); spec.loader.exec_module(monitor)
env = {key: os.environ[key] for key in ('HOME', 'USER', 'LOGNAME') if key in os.environ}; env['PATH'] = '/usr/bin:/bin'
terminal = monitor.monitor(argv, str(HERE), env, OUTPUT, 600, row(path))
clean = (terminal['allObservedOwnedGroupsGone'] and terminal['parentOwnedGroupGone']
         and not terminal['timeout'] and not terminal['forcedCleanup']
         and all(terminal[key] == [] for key in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
result = {'schemaVersion': 1, 'state': 'ROOT_OBSERVED_NEXT_FS_SDK_SYNTAX_V1',
          'rawExitCode': terminal['rawExitCode'], 'cleanOwnedGroups': bool(clean),
          'terminal': row(OUTPUT / 'terminal.json'), 'authority': row(path), 'engineOrGuestExecuted': False}
(HERE / 'root-result.json').write_text(json.dumps(result, indent=2) + '\n'); print(json.dumps(result), flush=True)
raise SystemExit(0 if clean and terminal['rawExitCode'] == 0 else 1)
