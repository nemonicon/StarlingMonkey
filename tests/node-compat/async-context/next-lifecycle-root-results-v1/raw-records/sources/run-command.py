"""Run one bounded, recorded command using the existing process-group owner.

This is an operational collector, not a conformance or production approval.
Each invocation needs a fresh record directory. Never overwrite failed runs.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[4]
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
MONITOR_SHA = '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'


def row(path):
    path = Path(path).resolve(strict=True)
    before = path.stat()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    after = path.stat()
    if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
        raise RuntimeError('Input changed during read: ' + str(path))
    return dict(path=str(path), sha256=digest, bytes=before.st_size)


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B, without -O')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, required=True)
    parser.add_argument('--cwd', type=Path, required=True)
    parser.add_argument('--seconds', type=int, required=True)
    parser.add_argument('--input', type=Path, action='append', default=[])
    parser.add_argument('--env', action='append', default=[])
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command or not 1 <= args.seconds <= 2400:
        raise ValueError('Explicit command and bounded deadline required')
    inputs = [row(MONITOR), row(__file__), row(command[0])] + [row(p) for p in args.input]
    if inputs[0]['sha256'] != MONITOR_SHA:
        raise RuntimeError('Existing process owner changed')
    cwd = args.cwd.resolve(strict=True)
    record = args.record.absolute()
    if record.parent.resolve(strict=True) != record.parent:
        raise ValueError('Record parent must be canonical')
    record.mkdir(mode=0o700)
    request = dict(schemaVersion=1, argv=command, cwd=str(cwd), seconds=args.seconds,
                   inputs=inputs, conformanceClaim=False, userAuthorizedRoadmapWork=True)
    request_path = record / 'request.json'
    with request_path.open('x') as handle:
        json.dump(request, handle, indent=2)
        handle.write('\n')
    spec = importlib.util.spec_from_file_location('lifecycle_process_owner', MONITOR)
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(('NODE_COMPAT_', 'NAPI_RS_')) and
           k not in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE', 'NODE_OPTIONS', 'NODE_PATH')}
    env.update(PYTHONDONTWRITEBYTECODE='1', BINARYEN_CORES='1', RAYON_NUM_THREADS='1', CARGO_BUILD_JOBS='4')
    for item in args.env:
        name, value = item.split('=', 1)
        if name in ('HOME', 'CODEX_HOME', 'NODE_OPTIONS', 'NODE_PATH', 'PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE'):
            raise ValueError('Forbidden environment override: ' + name)
        env[name] = value
    terminal = owner.monitor(command, str(cwd), env, record, args.seconds, row(request_path))
    unchanged = all(row(r['path']) == r for r in inputs)
    clean = (terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] and
             not terminal['timeout'] and not terminal['forcedCleanup'] and
             not terminal['interruptedSignals'] and not terminal['errors'] and not terminal['signals'])
    summary = dict(schemaVersion=1, terminal=row(record / 'terminal.json'), inputsUnchanged=unchanged,
                   rawExitCode=terminal['rawExitCode'], clean=bool(clean), conformanceClaim=False)
    with (record / 'collection.json').open('x') as handle:
        json.dump(summary, handle, indent=2)
        handle.write('\n')
    print(json.dumps(summary), flush=True)
    return 0 if clean and unchanged else 1


if __name__ == '__main__':
    sys.exit(main())
