"""Repeat the pinned successful Next component using the existing owned runner.

This workstation fixture requires its original private artifacts. It never builds
an engine, changes pins, overwrites evidence, or deploys outside localhost.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE / 'intl-component-root-results-v1/hydration-v5-runtime-authority.json'
BASE_SHA256 = 'df25982c55bad211a1d1c44ab5e324a3160b5f2d537b0c899d25702de4212c50'
RUNNER_SHA256 = '246ebcea64c366f8c06ec4f20b2a501ddb28cda75c1679aab300ca977e58a208'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True, help='Fresh lowercase identifier, at most 48 characters')
    parser.add_argument('--prepare-only', action='store_true', help='Write the request without starting Wasmtime or Chrome')
    args = parser.parse_args()
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        parser.error('Run Python with -I -B, without -O')
    if re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', args.run_id) is None:
        parser.error('Invalid --run-id')
    if digest(BASE) != BASE_SHA256:
        parser.error('Successful baseline request changed; review and repin explicitly')
    authority = json.loads(BASE.read_text())
    runner = HERE / 'wasmtime-deployment-candidate-v5/run-owned.py'
    if digest(runner) != RUNNER_SHA256:
        parser.error('Owned runner changed; review and repin explicitly')
    # Verify the selected component/tool/source descriptors before creating a
    # new request. The unchanged runner performs complete family and application
    # checks again before launch and at shutdown.
    for key in ['sourceIndex', 'plan', 'constructionResult', 'component', 'componentAudit',
                'constructionCallerIndex', 'inputEntry', 'inputSourceIndex']:
        ref = authority[key]
        path = Path(ref['path'])
        if digest(path) != ref['sha256'] or path.stat().st_size != ref['bytes']:
            parser.error('Pinned artifact changed: ' + str(path))
    plan = json.loads(Path(authority['plan']['path']).read_text())
    output = Path(plan['outputPrefix'] + '-' + args.run_id)
    outer = Path(str(output) + '-external-root')
    if output.exists() or outer.exists():
        parser.error('Run output already exists; choose a new --run-id')
    requests = Path('/private/tmp/starling-node-compat/next-regression-requests')
    requests.mkdir(mode=0o700, exist_ok=True)
    if requests.is_symlink() or requests.resolve() != requests:
        parser.error('Request directory must be a real canonical directory')
    request = requests / (args.run_id + '.json')
    authority['runId'] = args.run_id
    authority['rootReview'] = (
        'Repeat the pinned successful hydration-v5 localhost regression. '
        'Only runId differs semantically: same component, immutable application, '
        '24 HTTP/cache/strict stream assertions, two browser interactions, 20s '
        'limits, strict error gates, selected WASI imports and original owned runner. '
        'No compilation, external deployment, adoption, reset or failure filtering.'
    )
    with request.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    argv = [sys.executable, '-I', '-B', str(runner), str(request)]
    print(json.dumps({'argv': argv, 'outputRoot': str(output),
                      'observation': str(outer / 'observation.json'),
                      'prepareOnly': args.prepare_only}), flush=True)
    if args.prepare_only:
        return 0
    return subprocess.run(argv, cwd=str(HERE.parents[3]), check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
