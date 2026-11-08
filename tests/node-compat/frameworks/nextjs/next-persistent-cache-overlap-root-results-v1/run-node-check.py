"""Run the fixed real-FS cache suite with the existing original-process owner."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = BASE.parents[3]
APP = Path('/private/tmp/starling-node-compat/next-portable-cache-app-build-v1-first/application/.next/standalone')
INVENTORY = APP.parents[2] / 'application-inputs.json'
NODE = Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
SUITE = BASE / 'next-persistent-cache-overlap-tests-v1'
PINS = {
    NODE: ('e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0', 108619024),
    MONITOR: ('86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe', 15094),
    INVENTORY: ('f8058b479484cf3463e1424892a74b3719136fea2e071c79eb2604558fa93ab8', 660805),
    SUITE / 'cache-cases.cjs': ('51de8ea2ef5795570c53ad2fec1d38025146e0ecbeb2cc65b9749a9cd4e1f26d', 18223),
    SUITE / 'run-node.cjs': ('de6eb4da445b65e417e23b5e03144367c12d03f6a71845e0da8b2274a7287b05', 2441),
    SUITE / 'README.md': ('7229e316aab0bce6474d2ff0a8e0f2d597c583294feefd83cf760628c85b99bd', 5277),
}


def digest(body):
    return hashlib.sha256(body).hexdigest()


def regular(path):
    before = path.lstat()
    assert path.resolve() == path and stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    body = path.read_bytes()
    after = path.lstat()
    fields = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    assert all(getattr(before, k) == getattr(after, k) for k in fields) and len(body) == before.st_size
    return body


def pin(path, expected):
    body = regular(path)
    assert (digest(body), len(body)) == expected, str(path)
    return dict(path=str(path), sha256=expected[0], bytes=expected[1])


def write(path, obj):
    with path.open('x') as stream:
        json.dump(obj, stream, indent=2)
        stream.write('\n')


def application_snapshot(inventory):
    assert inventory['root'] == str(APP) and inventory['symlinks'] == []
    assert APP.resolve() == APP and APP.is_dir() and not APP.is_symlink()
    expected_files = {row['path'] for row in inventory['files']}
    expected_dirs = {row['path'] for row in inventory['directories']}
    actual_files, actual_dirs = set(), set()
    for root, dirs, files in os.walk(APP, followlinks=False):
        for name in dirs:
            child = Path(root) / name
            assert not child.is_symlink() and child.is_dir() and child.resolve() == child
            actual_dirs.add(child.relative_to(APP).as_posix())
        for name in files:
            actual_files.add((Path(root) / name).relative_to(APP).as_posix())
    assert actual_files == expected_files and actual_dirs == expected_dirs
    bookends, total = [], 0
    for row in inventory['files']:
        rel = PurePosixPath(row['path'])
        assert not rel.is_absolute() and '..' not in rel.parts and rel.as_posix() == row['path']
        path = APP / rel
        body = regular(path)
        assert len(body) == row['bytes'] and digest(body) == row['sha256']
        s = path.stat()
        bookends.append([row['path'], s.st_dev, s.st_ino, s.st_mtime_ns, s.st_size, stat.S_IMODE(s.st_mode)])
        total += len(body)
    assert len(bookends) == inventory['regularFiles'] == 2186 and total == inventory['bytes'] == 48755844
    return dict(files=len(bookends), bytes=total, directories=len(actual_dirs),
                bookendSha256=digest(json.dumps(bookends, separators=(',', ':')).encode()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    assert re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', args.run_id)
    assert __debug__ and not any(os.environ.get(k) for k in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH'))
    launcher = Path(__file__).resolve()
    launcher_bytes = regular(launcher)
    protected_pins = {**PINS, launcher: (digest(launcher_bytes), len(launcher_bytes))}
    protected = [pin(path, value) for path, value in protected_pins.items()]
    inventory = json.loads(INVENTORY.read_bytes())
    before = application_snapshot(inventory)
    root = Path('/private/tmp/starling-node-compat') / ('cache-overlap-node-v1-' + args.run_id)
    retained = HERE / 'runs' / args.run_id
    assert not root.exists() and not retained.exists()
    root.mkdir(mode=0o700)
    owner = root / 'owner'
    owner.mkdir(mode=0o700)
    argv = [str(NODE), str(SUITE / 'run-node.cjs'), str(APP), str(root / 'data')]
    action = dict(schemaVersion=1, state='ROOT_FIXED_REAL_FS_CACHE_NODE_CHECK_V1', argv=argv,
                  protectedInputs=protected, application=before, timeoutSeconds=120,
                  nodeReferenceOnly=True, guestExecuted=False, originalApplicationGatesWaived=False)
    write(root / 'request.json', action)
    authority = dict(path=str(root / 'request.json'), sha256=digest((root / 'request.json').read_bytes()),
                     bytes=(root / 'request.json').stat().st_size)
    spec = importlib.util.spec_from_file_location('cache_check_original_owner', MONITOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    environment = {k: v for k, v in os.environ.items() if k not in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE', 'NODE_OPTIONS', 'NODE_PATH')}
    environment.update(NODE_ENV='production', PYTHONDONTWRITEBYTECODE='1')
    terminal = module.monitor(argv, str(REPO), environment, owner, 120, authority)
    after = application_snapshot(inventory)
    assert before == after
    assert protected == [pin(path, value) for path, value in protected_pins.items()]
    retained.parent.mkdir(exist_ok=True)
    retained.mkdir(mode=0o755)
    shutil.copy2(root / 'request.json', retained / 'request.json')
    shutil.copytree(owner, retained / 'owner')
    report_path = root / 'data/result.json'
    report = json.loads(regular(report_path)) if report_path.exists() else None
    if report is not None:
        shutil.copy2(report_path, retained / 'result.json')
    clean = terminal['rawExitCode'] == 0 and not terminal['timeout'] and not terminal['interruptedSignals'] and not terminal['forcedCleanup'] and not terminal['signals'] and not terminal['errors'] and terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone']
    passed = clean and report is not None and report.get('passed') is True
    result = dict(schemaVersion=1, state='ROOT_REAL_FS_CACHE_NODE_CHECK_COMPLETED_V1', passed=passed,
                  originalOwner=terminal['pid'], rawExitCode=terminal['rawExitCode'], cleanOwner=clean,
                  applicationBefore=before, applicationAfter=after, protectedInputsUnchanged=True,
                  reportAssertions=None if report is None else report.get('assertions'),
                  reportCases=None if report is None else len(report.get('cases', [])),
                  nodeReferenceOnly=True, guestExecuted=False, fullNextAccepted=False,
                  sourceOrFullApplicationPromotion=False)
    write(retained / 'root-result.json', result)
    print(json.dumps(result))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
