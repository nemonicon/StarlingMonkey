"""Root-owned sequential constructor launcher; no ordinary guest calls."""
import hashlib, importlib.util, json, os, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYTHON = '/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9'
MONITOR = HERE.parents[2] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'

def row(p):
    p = Path(p)
    return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)

def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    kind = sys.argv[1]
    assert kind in ('regexp', 'stacktrace', 'dependencies', 'real-next')
    authority = HERE / (kind + '-construction-authority.json')
    ar = row(authority)
    a = json.loads(authority.read_text())
    caller = Path(a['callerIndex']['path']).parent
    assert row(caller / 'index.json') == a['callerIndex']
    assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
    assert shutil.disk_usage('/private/tmp').free >= 1024**3
    logs = Path(a['outputRoot'] + '-external-root')
    logs.mkdir(mode=0o700)
    spec = importlib.util.spec_from_file_location('original_owned_monitor', MONITOR)
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
    env.update(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C')
    terminal = monitor.monitor([PYTHON, '-I', '-B', str(caller/'run.py'), '--authority', str(authority), '--sha256', ar['sha256']], str(caller), env, logs, 2400, ar)
    print(json.dumps({k: terminal[k] for k in ('rawExitCode', 'timeout', 'forcedCleanup', 'allObservedOwnedGroupsGone', 'errors', 'signals', 'interruptedSignals')}), flush=True)
    return 0 if terminal['rawExitCode'] == 0 and not terminal['timeout'] and not terminal['forcedCleanup'] and terminal['allObservedOwnedGroupsGone'] and all(not terminal[k] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')) else 1

if __name__ == '__main__':
    raise SystemExit(main())
