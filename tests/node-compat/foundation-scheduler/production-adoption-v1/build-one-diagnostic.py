"""Launch exactly one serial ordinary Release build with a disk-space stop.

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
output = Path('/tmp/starling-node-compat/foundation-scheduler-v1/builds') / label
output.mkdir(parents=True, exist_ok=False)
recipe = root / 'tests/node-compat/build-diagnostic-engine.sh'
pins = json.loads((root / 'tests/node-compat/foundation-scheduler/diagnostic-candidate-v1/pins.json').read_bytes())
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert digest(recipe) == pins['diagnosticRecipeSha256']
environment = {
    'NODE_COMPAT_NODE': '/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',
    'NODE_COMPAT_JOBS': '4', 'BINARYEN_CORES': '4', 'RAYON_NUM_THREADS': '4',
    'NODE_COMPAT_BUILD_TYPE': 'Release', 'NODE_COMPAT_OOM_TESTING': '0',
    'NODE_COMPAT_BUILD_ROOT': '/tmp/starling-node-compat/improved-build',
    'NODE_COMPAT_PRIVATE_TICK_BUILD': '1', 'NODE_COMPAT_INTERNAL_TICKS': '1',
    'NODE_COMPAT_ENTROPY_MODE': 'OFF',
    'NODE_COMPAT_GC_STRESS': '1' if label == 'diagnostic-gc' else '0',
    # The reviewed GC input-manifest basename reaches macOS NAME_MAX already.
    # Distinct diagnostic/stress namespaces provide identity without a tag.
    'NODE_COMPAT_ARTIFACT_TAG': '',
    **{'NODE_COMPAT_' + name: '1' for name in
       ['PATH', 'EVENTS', 'STRING_DECODER', 'ASSERT', 'QUERYSTRING', 'UTIL', 'STREAM_WEB']},
}
minimum_free = 800 * 1024 * 1024
free = lambda: os.statvfs(root).f_bavail * os.statvfs(root).f_frsize
assert free() > minimum_free + 300 * 1024 * 1024
launch = {'schemaVersion': 1, 'state': 'one-serial-release-build-launched-not-runtime-proof',
          'label': label, 'recipeSha256': digest(recipe), 'launcherSha256': digest(Path(__file__)),
          'command': ['bash', str(recipe)], 'explicitEnvironment': environment,
          'freeBytesBefore': free(), 'stopBelowFreeBytes': minimum_free,
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
(output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'output': str(output), 'status': status, 'stoppedForDiskSpace': low_space,
                  'freeBytesAfter': result['freeBytesAfter']}), flush=True)
sys.exit(1 if status else 0)
