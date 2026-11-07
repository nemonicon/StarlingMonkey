"""Dormant single-GET guard probe; original0af owner, no constructor or Node control."""
from pathlib import Path
import hashlib, importlib.util, json, os, re, sys

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_bytes())


def row(path):
    path = Path(path)
    h, size = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024**2), b''):
            h.update(block)
            size += len(block)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=size)


def verify(ref):
    path = Path(ref['path'])
    assert path.is_absolute() and '..' not in path.parts and path.resolve(strict=True) == path
    assert path.is_file() and path.stat().st_nlink == 1 and row(path) == ref


def family(ref):
    verify(ref)
    root, index = Path(ref['path']).parent, read(ref['path'])
    names = {item['path']: item for item in index['files']}
    assert len(names) == len(index['files'])
    nodes = list(root.rglob('*'))
    assert all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in nodes)
    assert {p.relative_to(root).as_posix() for p in nodes if p.is_file()} == set(names) | {'index.json'}
    expected_dirs = {'.'}
    for name, item in names.items():
        rel = Path(name)
        assert not rel.is_absolute() and '..' not in rel.parts
        expected_dirs.update(str(p) for p in rel.parents)
        verify(dict(path=str(root / rel), sha256=item['sha256'], bytes=item['bytes']))
    assert {'.'} | {p.relative_to(root).as_posix() for p in nodes if p.is_dir()} == expected_dirs


def clean(terminal):
    return (terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and
            terminal['timeout'] is terminal['forcedCleanup'] is False and
            all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']))


def save(path, value):
    raw = (json.dumps(value, indent=2) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1 and len(sys.argv) == 2
    ap = Path(sys.argv[1]); verify(row(ap)); authority = row(ap); a = read(ap)
    p = read(HERE / 'plan.json')
    assert a['state'] == 'ROOT_FILE_URL_GUARD_PROBE_AUTHORIZED_V1'
    assert a['sourceIndex'] == row(HERE / 'index.json') and a['plan'] == row(HERE / 'plan.json')
    assert isinstance(a['runId'], str) and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', a['runId'])
    for key in ['ordinaryProbeAllowed', 'loopbackServeAllowed', 'fixtureStagingAllowed']:
        assert a[key] is True
    for key in ['componentConstructionAllowed', 'nodeControlAllowed', 'browserAllowed', 'appMountAllowed',
                'networkBeyondLoopbackAllowed', 'fullNextAcceptanceAllowed', 'adoptionAllowed']:
        assert a[key] is False

    def protect():
        verify(authority)
        family(a['sourceIndex'])
        for ref in p['sourceFamilies'] + a['nativeSourceFamilies']:
            family(ref)
        for key in ['node', 'wasmtime', 'monitor', 'probeEntry', 'constructionPlan', 'expectedEngine', 'expectedNativeMetadata', 'fullBuildReview', 'adapter']:
            verify(p[key])
        for key in ['engine', 'nativeMetadata', 'constructionResult', 'constructionCallerIndex', 'constructionRootStarted',
                    'constructionRootTerminal', 'constructionWorldGuard', 'constructionDataReview', 'component', 'componentAudit']:
            verify(a[key])
        for ref in a['engineBuildEvidence'] + a['nativeProtectedInputs']:
            verify(ref)

    protect()
    output = Path(p['outputPrefix'] + '-' + a['runId']); outer = Path(str(output) + '-external-root')
    assert output.is_absolute() and output.resolve(strict=False) == output and not output.exists() and not output.is_symlink()
    assert not outer.exists() and not outer.is_symlink()
    free = os.statvfs(output.parent); free_bytes = free.f_bavail * free.f_frsize
    assert free_bytes >= p['startFreeBytes'] == 1073741824
    os.umask(0o077); outer.mkdir(mode=0o700)
    save(outer / 'admission.json', dict(authority=authority, freeBytes=free_bytes, startFreeBytes=p['startFreeBytes'],
                                     commandInvoked=False, continuousDiskFloorClaimed=False))
    terminal = None; primary_error = None; protection_error = None; result = None
    try:
        verify(p['monitor'])
        spec = importlib.util.spec_from_file_location('genuine_original_guard_probe_owner', p['monitor']['path'])
        monitor = importlib.util.module_from_spec(spec); spec.loader.exec_module(monitor)
        env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
        env.update(PATH=str(Path(p['node']['path']).parent) + ':/usr/bin:/bin', LC_ALL='C', LANG='C',
                   TMPDIR=str(output / 'tmp'))
        terminal = monitor.monitor([p['node']['path'], str(HERE / 'collect.mjs'), str(ap)], p['cwd'], env,
                                   outer, p['outerSeconds'], authority)
    except BaseException as error:
        primary_error = dict(type=type(error).__name__, message=str(error))
    finally:
        try:
            protect()
        except BaseException as error:
            protection_error = dict(type=type(error).__name__, message=str(error))
        try:
            if (output / 'result.json').is_file(): result = read(output / 'result.json')
        except BaseException as error:
            if primary_error is None: primary_error = dict(type=type(error).__name__, message=str(error))
        ownership_clean = bool(terminal and clean(terminal))
        passed = bool(terminal and type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0 and ownership_clean and primary_error is None and
                      protection_error is None and result and result.get('observationsValid') is True and
                      result.get('guardProfileMatched') is True)
        observation = dict(schemaVersion=1, state='ROOT_GUARD_FILE_URL_PROBE_OBSERVATION_V1', runId=a['runId'],
                           rootAuthority=authority, sourceIndex=a['sourceIndex'], rawExitCode=terminal['rawExitCode'] if terminal else None,
                           ownedGroupsClean=ownership_clean, protectedInputsPreserved=protection_error is None,
                           primaryError=primary_error, protectionError=protection_error,
                           terminal=row(outer / 'terminal.json') if (outer / 'terminal.json').exists() else None,
                           result=row(output / 'result.json') if result else None, passed=passed,
                           guardProfileMatched=result.get('guardProfileMatched') if result else None,
                           nodeCompatibilityAccepted=False, fullNextAcceptance=False, adoption=False)
        save(outer / 'observation.json', observation)
    print(json.dumps(observation), flush=True)
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
