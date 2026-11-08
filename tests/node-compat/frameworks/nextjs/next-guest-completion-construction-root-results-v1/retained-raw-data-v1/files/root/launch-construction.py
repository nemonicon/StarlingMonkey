"""Root-owned sequential constructor launcher; no ordinary guest calls."""
import hashlib, importlib.util, json, os, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYTHON = '/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9'
MONITOR = HERE.parents[2] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'

def row(p):
    p = Path(p)
    return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)

def world_guard(authority):
    def indexed_plan(ref):
        index_path = Path(ref['path'])
        assert row(index_path) == ref
        index = json.loads(index_path.read_text())
        item = next(r for r in index['files'] if r['path'] == 'plan.json')
        plan_path = index_path.parent / 'plan.json'
        assert row(plan_path) == dict(item, path=str(plan_path))
        return json.loads(plan_path.read_text())

    caller_plan = indexed_plan(authority['callerIndex'])
    assert caller_plan['inputSourceIndex'] in authority['newSourceEvidence']
    fixture_plan = indexed_plan(caller_plan['inputSourceIndex'])
    ref = authority['worldSourceIndex']
    p = Path(ref['path'])
    assert ref == fixture_plan['worldSourceIndex']
    assert str(p.parent) == caller_plan['witDirectory'] == fixture_plan['witDirectory']
    assert p.is_absolute() and p.resolve() == p
    assert not any(x.is_symlink() for x in (p, *p.parents))
    assert row(p) == ref and p.stat().st_nlink == 1
    index = json.loads(p.read_text())
    names = [r['path'] for r in index['files']]
    assert len(names) == len(set(names))
    nodes = list(p.parent.rglob('*'))
    assert not any(x.is_symlink() for x in nodes)
    assert all(x.is_file() or x.is_dir() for x in nodes)
    assert {x.relative_to(p.parent).as_posix() for x in nodes if x.is_file()} == set(names) | {'index.json'}
    expected_dirs = set()
    for name in names:
        rel = Path(name)
        assert not rel.is_absolute() and '..' not in rel.parts
        expected_dirs.update(x.as_posix() for x in rel.parents if x != Path('.'))
    assert {x.relative_to(p.parent).as_posix() for x in nodes if x.is_dir()} == expected_dirs
    wit = []
    for item in index['files']:
        member = p.parent / item['path']
        assert member.is_file() and member.resolve() == member and member.stat().st_nlink == 1
        assert row(member) == dict(item, path=str(member))
        if member.suffix == '.wit':
            wit.append(row(member))
    assert len(wit) == 8
    assert all(item in authority['newSourceEvidence'] for item in wit)
    return dict(sourceIndex=ref, members=len(names), witFiles=8,
                exactFileAndDirectoryMembership=True, noSymlinkOrHardlinkAliases=True)

def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    kind = sys.argv[1]
    assert kind == 'guest-completion'
    authority = HERE / (kind + '-construction-authority.json')
    ar = row(authority)
    a = json.loads(authority.read_text())
    caller = Path(a['callerIndex']['path']).parent
    assert row(caller / 'index.json') == a['callerIndex']
    assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
    assert shutil.disk_usage('/private/tmp').free >= 1024**3
    before = world_guard(a)
    logs = Path(a['outputRoot'] + '-external-root')
    logs.mkdir(mode=0o700)
    spec = importlib.util.spec_from_file_location('original_owned_monitor', MONITOR)
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
    env.update(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C')
    try:
        terminal = monitor.monitor([PYTHON, '-I', '-B', str(caller/'run.py'), '--authority', str(authority), '--sha256', ar['sha256']], str(caller), env, logs, 2400, ar)
    finally:
        after = world_guard(a)
        assert row(authority) == ar
        with (logs/'world-guard.json').open('x') as handle:
            handle.write(json.dumps(dict(before=before, after=after, unchanged=before == after), indent=2)+'\n')
    print(json.dumps({k: terminal[k] for k in ('rawExitCode', 'timeout', 'forcedCleanup', 'allObservedOwnedGroupsGone', 'errors', 'signals', 'interruptedSignals')}), flush=True)
    return 0 if terminal['rawExitCode'] == 0 and not terminal['timeout'] and not terminal['forcedCleanup'] and terminal['allObservedOwnedGroupsGone'] and all(not terminal[k] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')) else 1

if __name__ == '__main__':
    raise SystemExit(main())
