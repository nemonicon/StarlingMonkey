"""Run one pinned fresh-app Node control with a fresh retained namespace.

Requires the original private tools and app. No automatic cohort or retry runs.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE / 'next-browser-reliability-root-results-v1'
BASE = ROOT / 'stock-v4-runtime-authority.json'
BASE_SHA256 = '38d30468405a73f2a8e96c9925d73454cbf6c1342b6853fe81174a8f715421ed'
RUNNER = HERE / 'browser-hydration-matched-host-candidate-v4/run-owned.py'
RUNNER_SHA256 = '595d286fde1f98d59305b7403e6c3a63b4a786ccff82c8cbc0229b569ceb4965'
MINIMUM_FREE_BYTES = 1073741824


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True, help='Fresh lowercase identifier, at most 48 characters')
    parser.add_argument('--prepare-only', action='store_true', help='Write a new request without starting Node or Chrome')
    args = parser.parse_args()
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        parser.error('Run Python with -I -B, without -O')
    if re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', args.run_id) is None:
        parser.error('Invalid --run-id')
    if digest(BASE) != BASE_SHA256 or digest(RUNNER) != RUNNER_SHA256:
        parser.error('Reviewed control request or owner changed; review and repin explicitly')
    authority = json.loads(BASE.read_text())
    if authority['rootLaunchMinimumFreeBytes'] != MINIMUM_FREE_BYTES:
        parser.error('Root launch capacity policy changed')
    for key in ['sourceIndex', 'plans']:
        ref = authority[key]
        path = Path(ref['path'])
        if digest(path) != ref['sha256'] or path.stat().st_size != ref['bytes']:
            parser.error('Pinned control input changed: ' + str(path))
    plan = json.loads(Path(authority['plans']['path']).read_text())
    for key in ['node', 'monitor', 'applicationBuildResult', 'applicationInputs']:
        ref = plan[key]
        path = Path(ref['path'])
        if digest(path) != ref['sha256'] or path.stat().st_size != ref['bytes']:
            parser.error('Pinned control prerequisite changed: ' + str(path))
    authority['runId'] = args.run_id
    # Reuse the reviewed owner's actual pure selector. Importing this dormant
    # Python tool does not invoke its monitor, Node, Chrome or an app copy.
    spec = importlib.util.spec_from_file_location('reviewed_fresh_stock_owner', RUNNER)
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    output, monitor, actor_argv = owner.derive_invocation(authority, plan, RUNNER.parent)
    if any(path.exists() or path.is_symlink() for path in [output, monitor]):
        parser.error('Run output already exists; choose a new --run-id')
    free = shutil.disk_usage(output.parent).free
    if not args.prepare_only and free < MINIMUM_FREE_BYTES:
        parser.error('Root launch requires at least 1 GiB free; available bytes: ' + str(free))
    requests = Path('/private/tmp/starling-node-compat/next-fresh-app-control-requests')
    requests.mkdir(mode=0o700, exist_ok=True)
    if requests.is_symlink() or requests.resolve() != requests:
        parser.error('Request directory must be a real canonical directory')
    request_dir_stat = requests.stat()
    if request_dir_stat.st_uid != os.getuid() or request_dir_stat.st_mode & 0o777 != 0o700:
        parser.error('Request directory must be owned by this user with mode 0700')
    request = requests / (args.run_id + '.json')
    with os.fdopen(os.open(request, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    argv = [sys.executable, '-I', '-B', str(RUNNER), 'stock', str(request)]
    print(json.dumps({'argv': argv, 'actorArgv': actor_argv, 'request': str(request),
                      'outputRoot': str(output), 'monitorOutputRoot': str(monitor),
                      'observation': str(monitor / 'observation.json'),
                      'freeBytesAtAdmission': free, 'minimumFreeBytes': MINIMUM_FREE_BYTES,
                      'prepareOnly': args.prepare_only}), flush=True)
    if args.prepare_only:
        return 0
    return subprocess.run(argv, cwd=str(HERE.parents[3]), check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
