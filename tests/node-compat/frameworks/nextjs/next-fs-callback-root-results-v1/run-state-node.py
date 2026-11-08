"""One fresh Node reference for the real-filesystem callback conformance suite."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
SUITE = BASE / 'next-fs-callback-state-tests-v1'
NODE = Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
MONITOR = BASE.parents[3] / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
OUTPUT = Path('/private/tmp/starling-node-compat/next-fs-callback-state-tests-v1-node-first')
OWNER = Path(str(OUTPUT) + '-external-root')


def row(p):
    before = p.lstat()
    assert p.resolve() == p and not p.is_symlink() and stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    body = p.read_bytes()
    after = p.lstat()
    fields = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    assert all(getattr(before, k) == getattr(after, k) for k in fields)
    return dict(path=str(p), sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))


def save(p, value):
    with p.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
    return row(p)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    index = row(SUITE / 'index.json')
    assert index['sha256'] == '888954f6ab55f21153e547c199bff89d336b8babf668a70334eca0880ba94d6f'
    metadata = json.loads((SUITE / 'index.json').read_bytes())
    refs = [index, row(NODE), row(MONITOR), row(Path(__file__).resolve())]
    assert refs[1]['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    assert refs[2]['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
    for member in metadata['files']:
        assert '/' not in member['path'] and '..' not in member['path']
        ref = dict(member, path=str(SUITE / member['path']))
        assert row(Path(ref['path'])) == ref
        refs.append(ref)
    helper = row(BASE / 'next-fs-callback-app-build-v1/fixture/app/api/cache/callback-generation.cjs')
    assert helper['sha256'] == '48186fd2099c7a3c361971784c8578473b487b95a41921ddf036e0d1b0fa63b1'
    refs.append(helper)
    assert {p.name for p in SUITE.iterdir()} == {'index.json'} | {m['path'] for m in metadata['files']}

    def protect():
        for ref in refs:
            assert row(Path(ref['path'])) == ref

    receipt = HERE / 'state-node-owner-result.json'
    authority_path = HERE / 'state-node-authority.json'
    assert all(not p.exists() and not p.is_symlink() for p in (OUTPUT, OWNER, receipt, authority_path))
    argv = [str(NODE), str(SUITE / 'run-node.cjs'), str(OUTPUT)]
    authority = save(authority_path, dict(schemaVersion=1, state='ROOT_REAL_FS_CALLBACK_STATE_NODE_REFERENCE_V1',
        argv=argv, protectedInputs=refs, ownerSeconds=120, nodeReferenceOnly=True, guestAllowed=False,
        nativeBuildAllowed=False, componentConstructionAllowed=False, automaticRetry=False))
    protect()
    spec = importlib.util.spec_from_file_location('callback_original_owner', MONITOR)
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    OWNER.mkdir(mode=0o700)
    env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
    env.update(PATH=str(NODE.parent) + ':/usr/bin:/bin', NODE_ENV='production', CI='1')
    terminal, primary, preserved = None, None, False
    secondary = []
    try:
        terminal = monitor.monitor(argv, str(BASE.parents[3]), env, OWNER, 120, authority)
    except BaseException as error:
        primary = error
    finally:
        try:
            protect()
            assert row(authority_path) == authority
            preserved = True
        except BaseException as error:
            if primary is None:
                primary = error
            else:
                secondary.append(dict(name=type(error).__name__, message=str(error)[:2048]))
        clean = terminal is not None and not terminal['timeout'] and not terminal['forcedCleanup'] and terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and all(not terminal[k] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
        try:
            report_ref = row(OUTPUT / 'report.json') if (OUTPUT / 'report.json').is_file() else None
            report = json.loads(Path(report_ref['path']).read_bytes()) if report_ref else None
            passed = primary is None and preserved and clean and terminal['rawExitCode'] == 0 and report is not None and report.get('passed') is True
            result = dict(schemaVersion=1, state='ROOT_REAL_FS_CALLBACK_STATE_NODE_COMPLETED_UNREVIEWED_V1',
                passed=passed, authority=authority, originalOwner=None if terminal is None else terminal['pid'],
                rawExitCode=None if terminal is None else terminal['rawExitCode'], cleanOwner=clean,
                finalInputsPreserved=preserved, report=report_ref,
                terminal=row(OWNER / 'terminal.json') if (OWNER / 'terminal.json').is_file() else None,
                error=None if primary is None else dict(name=type(primary).__name__, message=str(primary)[:2048]),
                secondaryErrors=secondary, guestExecuted=False, fullNextAccepted=False)
            ref = save(receipt, result)
            print(json.dumps(dict(result=ref, passed=passed, cleanOwner=clean)))
        except BaseException:
            if primary is not None:
                raise primary
            raise
    if primary is not None:
        raise primary
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
