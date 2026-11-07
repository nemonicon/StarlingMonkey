"""Regress the pinned fresh Next app with the reviewed native/runtime guard.

Requires the original private tools, component and fresh application. Each run
retains a new request and output tree; this command does not rebuild them.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE / 'next-app-runtime-root-results-v1'
BASE = ROOT / 'fresh-app-v7-runtime-authority.json'
BASE_SHA256 = 'cea37d053f4357fc9e2e10f9eb34cbbeb70a2cb05dedaf9292f3b73693361483'
RUNNER = ROOT / 'run-full-next-fresh-app.py'
RUNNER_SHA256 = '62ec251cdea390c0d05397be09eda46cb6fb73713159605c32f49cf78ad700c4'
MINIMUM_FREE_BYTES = 1073741824


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True, help='Fresh lowercase identifier, at most 48 characters')
    parser.add_argument('--prepare-only', action='store_true', help='Write a new request without starting a runtime or browser')
    args = parser.parse_args()
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        parser.error('Run Python with -I -B, without -O')
    if re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', args.run_id) is None:
        parser.error('Invalid --run-id')
    if digest(BASE) != BASE_SHA256 or digest(RUNNER) != RUNNER_SHA256:
        parser.error('Reviewed request or guard changed; review and repin explicitly')
    authority = json.loads(BASE.read_text())
    if authority['rootLaunchMinimumFreeBytes'] != MINIMUM_FREE_BYTES:
        parser.error('Root launch capacity policy changed')
    # The guarded runner performs whole-family, native, constructor, world and
    # physical app checks before launch and at shutdown. These early checks
    # prevent preparing a request against obviously missing or changed inputs.
    for key in ['sourceIndex', 'plan', 'constructionResult', 'component', 'componentAudit',
                'constructionCallerIndex', 'inputEntry', 'inputSourceIndex', 'engine', 'nativeMetadata']:
        ref = authority[key]
        path = Path(ref['path'])
        if digest(path) != ref['sha256'] or path.stat().st_size != ref['bytes']:
            parser.error('Pinned artifact changed: ' + str(path))
    plan = json.loads(Path(authority['plan']['path']).read_text())
    for key in ['applicationBuildResult', 'applicationInputs']:
        ref = plan[key]
        path = Path(ref['path'])
        if digest(path) != ref['sha256'] or path.stat().st_size != ref['bytes']:
            parser.error('Fresh application evidence changed: ' + str(path))
    output = Path(plan['outputPrefix'] + '-' + args.run_id)
    outer = Path(str(output) + '-external-root')
    receipt = ROOT / (args.run_id + '-full-world-guard.json')
    if output.exists() or outer.exists() or receipt.exists():
        parser.error('Run output already exists; choose a new --run-id')
    free = shutil.disk_usage(output.parent).free
    if not args.prepare_only and free < MINIMUM_FREE_BYTES:
        parser.error('Root launch requires at least 1 GiB free; available bytes: ' + str(free))
    requests = Path('/private/tmp/starling-node-compat/next-fresh-app-regression-requests')
    requests.mkdir(mode=0o700, exist_ok=True)
    if requests.is_symlink() or requests.resolve() != requests:
        parser.error('Request directory must be a real canonical directory')
    request = requests / (args.run_id + '.json')
    authority['runId'] = args.run_id
    authority['rootReview'] = (
        'Fresh retained-artifact Next app regression, explicitly selected by this CLI. '
        'Same reviewed native V7/Browser V3, genuine 2181-file fresh app build/inventory, '
        '1c31 component/462 engine, complete native/constructor/world guard, original '
        '24 HTTP/cache/strict stream/two browser assertions, CDP diagnostics and strict '
        'zero-error gate with original time limits and 600s owner. '
        'Conservative Root start admission is 1GiB free, not a continuous guard or '
        'measured peak. Preparation alone does not execute or accept the app. '
        'This command runs only the native arm; it does not launch a matched control. '
        'No automatic retry, failure filter, compilation, pin/app mutation, external '
        'deployment, reset, production promotion or explanation of earlier aborts.'
    )
    with request.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    argv = [sys.executable, '-I', '-B', str(RUNNER), str(request)]
    print(json.dumps({'argv': argv, 'request': str(request), 'outputRoot': str(output),
                      'observation': str(outer / 'observation.json'),
                      'rootWorldGuardReceipt': str(receipt), 'freeBytesAtAdmission': free,
                      'minimumFreeBytes': MINIMUM_FREE_BYTES, 'prepareOnly': args.prepare_only}), flush=True)
    if args.prepare_only:
        return 0
    return subprocess.run(argv, cwd=str(HERE.parents[3]), check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
