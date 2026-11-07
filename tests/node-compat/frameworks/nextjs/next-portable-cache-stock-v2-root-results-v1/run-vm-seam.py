"""One owned Node22 compiler seam; no application, HTTP, browser or guest."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
SOURCE = BASE / 'next-portable-cache-stock-candidate-v2'
WORK = Path('/private/tmp/starling-node-compat/next-portable-cache-vm-seam-v2-first')
MONITOR = HERE.parents[2] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def save(path, value):
    with path.open('x') as handle:
        handle.write(json.dumps(value, indent=2) + '\n')


def check_family(ref):
    assert row(Path(ref['path'])) == ref
    root = Path(ref['path']).parent
    index = json.loads(Path(ref['path']).read_text())
    names = [item['path'] for item in index['files']]
    assert len(names) == len(set(names))
    nodes = list(root.rglob('*'))
    assert not any(path.is_symlink() for path in nodes)
    assert {str(path.relative_to(root)) for path in nodes if path.is_file()} == set(names) | {'index.json'}
    for item in index['files']:
        path = root / item['path']
        assert path.stat().st_nlink == 1 and row(path) == dict(item, path=str(path))


def main():
    source_ref = row(SOURCE / 'index.json')
    assert source_ref['sha256'] == 'df2570544358efb4e528fbf63e6b50b08209fd6299ad1f5b3de97358109a983d'
    plan_ref = row(SOURCE / 'vm-seam-plan.json')
    plan = json.loads((SOURCE / 'vm-seam-plan.json').read_text())
    witnesses = json.loads((SOURCE / 'source-references.json').read_text())
    node = witnesses['selectedNode']
    refs = [source_ref, plan_ref, row(Path(__file__).resolve()), row(MONITOR), node]
    refs += list(witnesses['localWitnesses'].values())
    assert refs[3]['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
    assert plan['rootSuggestedCapSeconds'] == 120 and len(plan['fixtures']) == 2
    assert plan['script'] == row(SOURCE / 'test-vm-seam.mjs')

    def protect():
        check_family(source_ref)
        for ref in refs:
            assert row(Path(ref['path'])) == ref

    protect()
    assert shutil.disk_usage('/private/tmp').free >= 1073741824
    assert not WORK.exists() and not WORK.is_symlink()
    os.umask(0o077)
    WORK.mkdir(mode=0o700)
    (WORK / 'tmp').mkdir(mode=0o700)
    fixtures = WORK / 'fixtures'
    fixtures.mkdir(mode=0o700)
    copies = []
    for fixture in plan['fixtures']:
        original = Path(fixture['source']['path'])
        assert row(original) == fixture['source']
        target = fixtures / fixture['relativePath']
        with target.open('xb') as handle:
            handle.write(original.read_bytes())
        target.chmod(0o444)
        assert target.stat().st_nlink == 1
        assert (original.stat().st_dev, original.stat().st_ino) != (target.stat().st_dev, target.stat().st_ino)
        copies.append(dict(source=fixture['source'], target=row(target), mode=stat.S_IMODE(target.stat().st_mode)))
    fixtures.chmod(0o555)
    result_path = WORK / 'result.json'
    argv = [node['path'], plan['script']['path'], str(fixtures), str(result_path)]
    authority_path = WORK / 'authority.json'
    save(authority_path, dict(state='ROOT_NODE22_VM_DEFAULT_LOADER_SEAM_AUTHORIZED_V2',
        sourceIndex=source_ref, seamPlan=plan_ref, argv=argv, originalOwnerSeconds=120,
        fixtures=copies, node=node, protectedInputs=refs,
        applicationOrHttpOrBrowserOrGuestAllowed=False, noNodeFlags=True))
    authority_ref = row(authority_path)
    logs = WORK / 'monitor'
    logs.mkdir(mode=0o700)
    spec = importlib.util.spec_from_file_location('original_owned_seam_monitor', MONITOR)
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    env = {key: os.environ[key] for key in ('HOME', 'USER', 'LOGNAME') if key in os.environ}
    env.update(PATH=str(Path(node['path']).parent) + ':/usr/bin:/bin', LANG='C', LC_ALL='C', TMPDIR=str(WORK / 'tmp'))
    terminal = monitor.monitor(argv, str(SOURCE), env, logs, 120, authority_ref)
    protect()
    for copied in copies:
        target = Path(copied['target']['path'])
        assert row(target) == copied['target'] and stat.S_IMODE(target.stat().st_mode) == 0o444
    clean = terminal['rawExitCode'] == 0 and not terminal['timeout'] and not terminal['forcedCleanup'] and terminal['allObservedOwnedGroupsGone'] is True
    clean = clean and all(terminal[key] == [] for key in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
    result = json.loads(result_path.read_text()) if result_path.exists() else None
    passed = bool(clean and result and result['passed'] is True and result['errors'] == [])
    observation = dict(state='ROOT_NODE22_VM_SEAM_COMPLETED_UNREVIEWED_V2',
        authority=authority_ref, terminal=row(logs / 'terminal.json'),
        result=row(result_path) if result_path.exists() else None, rawExitCode=terminal['rawExitCode'],
        clean=clean, inputsAndCopiesPreserved=True, passed=passed,
        appHttpBrowserGuestExecuted=False, stderrPreservedUnfiltered=True)
    save(WORK / 'observation.json', observation)
    print(json.dumps(observation), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
