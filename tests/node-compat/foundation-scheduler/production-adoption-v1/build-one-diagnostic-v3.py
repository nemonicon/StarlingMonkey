"""Launch one corrected-producer ordinary Release build with a disk-space stop.

Not a benchmark. Build logs and fresh launch/result records remain external.
No componentizer or guest runtime is invoked by this launcher.
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[4]
label = sys.argv[1]
assert label in ['diagnostic-release', 'diagnostic-gc']
output = Path('/tmp/starling-node-compat/foundation-scheduler-v3/builds') / label
recipe = root / 'tests/node-compat/build-diagnostic-engine.sh'
pins = json.loads((root / 'tests/node-compat/foundation-scheduler/diagnostic-producer-v2/pins.json').read_bytes())
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert digest(recipe) == pins['diagnosticRecipeSha256']
environment = {
    'NODE_COMPAT_NODE': '/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',
    'NODE_COMPAT_JOBS': '1', 'BINARYEN_CORES': '1', 'RAYON_NUM_THREADS': '1',
    'NODE_COMPAT_BUILD_TYPE': 'Release', 'NODE_COMPAT_OOM_TESTING': '0',
    'NODE_COMPAT_BUILD_ROOT': '/tmp/starling-node-compat/improved-build',
    'NODE_COMPAT_PRIVATE_TICK_BUILD': '1', 'NODE_COMPAT_INTERNAL_TICKS': '1',
    'NODE_COMPAT_ENTROPY_MODE': 'OFF',
    'NODE_COMPAT_GC_STRESS': '1' if label == 'diagnostic-gc' else '0',
    # Only normal Release has space for a short fresh evidence tag. The GC
    # input-manifest basename reaches macOS NAME_MAX even without a tag.
    'NODE_COMPAT_ARTIFACT_TAG': 'r3' if label == 'diagnostic-release' else '',
    **{'NODE_COMPAT_' + name: '1' for name in
       ['PATH', 'EVENTS', 'STRING_DECODER', 'ASSERT', 'QUERYSTRING', 'UTIL', 'STREAM_WEB']},
}
minimum_free = 800 * 1024 * 1024
free = lambda: os.statvfs(root).f_bavail * os.statvfs(root).f_frsize
required_start_free = 2 * 1024 * 1024 * 1024
assert free() >= required_start_free, 'Need at least 2 GiB available before retry'
output.mkdir(parents=True, exist_ok=False)
launch = {'schemaVersion': 1, 'state': 'one-serial-release-build-launched-not-runtime-proof',
          'label': label, 'recipeSha256': digest(recipe), 'launcherSha256': digest(Path(__file__)),
          'command': ['bash', str(recipe)], 'explicitEnvironment': environment,
          'freeBytesBefore': free(), 'requiredStartFreeBytes': required_start_free, 'stopBelowFreeBytes': minimum_free,
          'guestExecutionRequested': False, 'parallelBuilds': 1}
(output / 'launch.json').write_text(json.dumps(launch, indent=2) + '\n')
started = time.monotonic()
low_space = False
with (output / 'build.log').open('xb') as log:
    process = subprocess.Popen(launch['command'], cwd=root, env={**os.environ, **environment},
                               stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        while process.poll() is None:
            if free() < minimum_free:
                low_space = True
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                break
            time.sleep(1)
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
        status = process.wait()
result = {**launch, 'state': 'native-build-failed' if status else 'native-build-completed-runtime-pending',
          'status': status, 'stoppedForDiskSpace': low_space, 'freeBytesAfter': free(),
          'wallSecondsForOperationalRecordOnly': time.monotonic() - started,
          'logSha256': digest(output / 'build.log')}
try:
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
except OSError as error:
    result['resultFileWriteError'] = str(error)
# Preserve the native status on the tool's stdout even if the filesystem fills.
print(json.dumps({'output': str(output), 'result': result}), flush=True)
sys.exit(1 if status else 0)
