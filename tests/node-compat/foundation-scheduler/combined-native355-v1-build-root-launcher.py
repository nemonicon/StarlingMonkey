"""Root pre-entry guard; exec the genuine reviewed controller without a new worker."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import stat
import sys

HERE = Path(__file__).resolve()
SOURCE = Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/combined-native-build-controller-candidate-v1')
SOURCE_SHA = 'd646d2ec64aedbfa59a077abf76d0c6267d710fbc0590d9b71007f88ef740a8c'
OBSERVER = Path('/private/tmp/starling-node-compat/combined-native355-v1-build-root-observer')
POLICY = dict(schemaVersion=1, mandatoryBeforeControllerSpawn=True,
              removePrefixes=['BASH_FUNC_'],
              removeExactNames=['BASH_ENV', 'ENV', 'SHELLOPTS', 'BASHOPTS', 'CDPATH', 'GLOBIGNORE'],
              preserveExactNames=['HOME', 'home', 'CODEX_HOME'],
              rootAuthorityMustBindPolicy=True, rootLauncherMustEnforcePolicy=True,
              actualChildMustContainNoRemovedEntries=True,
              recordRemovedVariableNamesOnly=True, recordEnvironmentValues=False,
              scope='Known inherited Bash function and startup controls; not an OS or universal environment sandbox')


def clean_environment(parent):
    removed = sorted(k for k in parent if k.startswith(tuple(POLICY['removePrefixes'])) or k in POLICY['removeExactNames'])
    child = {k: v for k, v in parent.items() if k not in removed}
    assert not any(k.startswith(tuple(POLICY['removePrefixes'])) or k in POLICY['removeExactNames'] for k in child)
    for k in POLICY['preserveExactNames']:
        assert (k in child) == (k in parent) and child.get(k) == parent.get(k)
    assert parent == {**child, **{k: parent[k] for k in removed}}
    return child, removed


def checked(row):
    assert type(row) is dict and set(row) == {'path', 'sha256', 'bytes'}
    p = Path(row['path'])
    assert p.is_absolute() and '..' not in p.parts and p.is_file() and not p.is_symlink()
    a = p.stat()
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    z = p.stat()
    assert (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (z.st_dev, z.st_ino, z.st_size, z.st_mtime_ns, z.st_ctime_ns)
    assert z.st_size == row['bytes'] and h.hexdigest() == row['sha256']
    return p


def read(row):
    p = checked(row)
    assert row['bytes'] <= 32 * 1024 * 1024
    raw = p.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    return json.loads(raw)


def family(row):
    d = read(row)
    root = Path(row['path']).parent
    names = {'index.json'}
    for r in d['files']:
        n = r['path']
        assert n and not n.startswith('/') and all(p not in ('', '.', '..') for p in n.split('/')) and n not in names
        names.add(n)
        checked(dict(path=str(root / n), sha256=r['sha256'], bytes=r['bytes']))
    actual = set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():
            actual.add(p.relative_to(root).as_posix())
    assert actual == names
    return d


def write(path, value):
    raw = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb', closefd=False) as f:
            assert f.write(raw) == len(raw)
            f.flush()
            os.fsync(f.fileno())
    finally:
        os.close(fd)


def run(config_row):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    config = read(config_row)
    root = read(config['rootAuthority'])
    assert root['controllerIndex']['path'] == str(SOURCE / 'index.json')
    assert root['controllerIndex']['sha256'] == SOURCE_SHA
    assert root['rootEnvironmentPolicy'] == POLICY
    assert checked(root['rootLauncherEntry']) == HERE
    own = family(root['controllerIndex'])
    inputs_row = next(r for r in own['files'] if r['path'] == 'source-inputs.json')
    inputs = read(dict(inputs_row, path=str(SOURCE / inputs_row['path'])))
    assert len(inputs['files']) == 3403
    for r in inputs['files']:
        checked(r)
    refs_row = next(r for r in own['files'] if r['path'] == 'references.json')
    refs = read(dict(refs_row, path=str(SOURCE / refs_row['path'])))
    for r in refs['families']:
        family(r)
    peer_pair = root['controllerSourceReview']
    family(peer_pair['index'])
    peer = read(peer_pair['result'])
    assert peer['requiredRootEnvironmentPolicy'] == POLICY
    entry = checked(root['controllerEntry'])
    assert entry == SOURCE / 'controller.py'
    # The complete source/dependency closure is authenticated before this import.
    spec = importlib.util.spec_from_file_location('genuine_combined355_build_controller', str(entry))
    controller = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(controller)
    frame = controller.authorize(config_row)
    child, removed = clean_environment(dict(os.environ))
    assert OBSERVER.is_dir() and not OBSERVER.is_symlink() and stat.S_IMODE(OBSERVER.stat().st_mode) == 0o700
    for k in ['workRoot', 'externalOutputRoot', 'buildOutputRoot', 'freezeRoot']:
        assert not Path(root[k]).exists() and not Path(root[k]).is_symlink()
    argv = [frame['refs']['pythonExecutable']['path'], '-B', '-I', str(entry), 'parent', json.dumps(config_row, separators=(',', ':'))]
    assert Path(sys.executable).resolve() == Path(argv[0])
    write(OBSERVER / 'preentry-environment.json', dict(
        schemaVersion=1, state='ROOT_COMBINED355_CLEAN_PREENTRY_OBSERVATION_V1',
        rootAuthority=config['rootAuthority'], rootLauncherEntry=root['rootLauncherEntry'],
        controllerSourceReview=peer_pair, policy=POLICY, removedVariableNames=removed,
        environmentValuesRecorded=False, requiredEntriesAbsent=True, hostHomeValuesPreserved=True,
        argv=argv, configuredSourceAndWorkUnchangedBeforeExec=True,
        nativeBuildStartedByThisRecord=False, engineOrGuestExecuted=False))
    controller.recheck(frame)
    checked(root['rootLauncherEntry'])
    # Replace this process: the original parent owns its real 7200s monitor.
    os.execve(argv[0], argv, child)


if __name__ == '__main__':
    if sys.argv[1:] == ['--self-test']:
        original = {'HOME': '/preserved', 'home': '/also-preserved', 'CODEX_HOME': '/preserved-codex', 'PATH': '/pinned'}
        original.update({k: 'inert test data' for k in POLICY['removeExactNames']})
        original['BASH_FUNC_rustup%%'] = 'inert test data'
        original['BASH_FUNC_cmake%%'] = 'inert test data'
        snapshot = dict(original)
        child, removed = clean_environment(original)
        assert original == snapshot
        assert set(removed) == set(POLICY['removeExactNames']) | {'BASH_FUNC_rustup%%', 'BASH_FUNC_cmake%%'}
        assert child == {k: snapshot[k] for k in ['HOME', 'home', 'CODEX_HOME', 'PATH']}
        assert clean_environment({}) == ({}, [])
        print(json.dumps(dict(pureChecks=4, passed=True, nativeOrShellCommandsExecuted=False)))
    else:
        assert len(sys.argv) == 3 and sys.argv[1] == '--run'
        run(json.loads(sys.argv[2]))
