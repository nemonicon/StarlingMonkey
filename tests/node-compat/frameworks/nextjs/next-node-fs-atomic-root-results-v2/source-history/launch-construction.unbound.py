"""Unbound Root launcher Source for one direct node-fs-atomic V2 INIT only."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
PREPARER_SHA256 = None
PYTHON = '/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9'


def main():
    if not (__debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 2
            and sys.argv[1] == 'node-fs-atomic-v2' and type(PREPARER_SHA256) is str):
        raise ValueError('Unbound Root Source; no helper/read/output/action')
    source = HERE / 'prepare-construction.py'
    if source.resolve() != source or source.is_symlink() or source.stat().st_nlink != 1:
        raise ValueError('Preparer Source alias')
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PREPARER_SHA256:
        raise ValueError('Preparer Source changed')
    spec = importlib.util.spec_from_file_location('actual_reviewed_diagnostic_probe_root_admission', source)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    prep.bound()
    prep.require(shutil.disk_usage('/private/tmp').free >= 1024**3, 'Original1GiB constructor admission')
    path = HERE / 'node-fs-atomic-construction-authority.json'
    ar = prep.row(path)
    a = prep.document(ar)
    before = prep.admit(a)
    caller = Path(a['callerIndex']['path']).parent
    p = prep.document(prep.CALLER_PLAN)
    prep.require(p['componentizeNodeCapSeconds'] == 1800 and p['dataToolCapSeconds'] == 120,
                 'Original inner constructor caps')
    python_ref = a['metadataExpectedFixedValues']['buildToolPython']
    prep.require(python_ref['path'] == PYTHON, 'Original Python3.9 path from actual metadata')
    prep.checked(python_ref)
    prep.checked(p['pins']['monitor'])
    logs = Path(a['outputRoot'] + '-external-root')
    prep.require(not logs.exists() and not logs.is_symlink() and logs.resolve() == logs,
                 'Fresh canonical original owner output')
    # Original monitor directory is created before its first monitor call.
    logs.mkdir(mode=0o700)
    monitor = prep.original(p['pins']['monitor'], 'genuine_original_direct_probe_constructor_monitor')
    env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
    env.update(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C')
    terminal, primary, after = None, None, None
    secondary = []
    try:
        terminal = monitor.monitor([python_ref['path'], '-I', '-B', str(caller / 'run.py'), '--authority', str(path),
            '--sha256', ar['sha256']], str(caller), env, logs, 2400, ar)
    except BaseException as error:
        primary = error
    finally:
        try:
            after = prep.admit(a)
            prep.checked(ar)
            prep.checked(python_ref)
            prep.require(prep.row(source)['sha256'] == PREPARER_SHA256, 'Preparer changed')
            prep.save(logs / 'world-guard.json', dict(before=before, after=after, unchanged=before == after,
                nativeInputsPreserved=True, fullNativeGuardImplementation=prep.FULL_GUARD,
                worldGuardImplementation=prep.WORLD_GUARD))
        except BaseException as error:
            if primary is None: primary = error
            else: secondary.append(dict(name=type(error).__name__, message=str(error)[:2048]))
        try:
            clean = terminal is not None and not terminal['timeout'] and not terminal['forcedCleanup'] and terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and all(not terminal[k] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
            prep.save(logs / 'owner-result.json', dict(schemaVersion=1, state='ROOT_ATOMIC_CONSTRUCTION_OWNER_COMPLETED_UNREVIEWED_V2',
                originalOwner=None if terminal is None else terminal['pid'], rawExitCode=None if terminal is None else terminal['rawExitCode'],
                cleanOwner=clean, authority=ar, constructorGuardBefore=before, constructorGuardAfter=after,
                error=None if primary is None else dict(name=type(primary).__name__, message=str(primary)[:2048]), secondaryErrors=secondary))
        except BaseException:
            if primary is not None: raise primary
            raise
    if primary is not None: raise primary
    print(json.dumps({k: terminal[k] for k in ('rawExitCode', 'timeout', 'forcedCleanup',
        'allObservedOwnedGroupsGone', 'errors', 'signals', 'interruptedSignals')}), flush=True)
    return 0 if terminal['rawExitCode'] == 0 and not terminal['timeout'] and not terminal['forcedCleanup'] and \
        terminal['allObservedOwnedGroupsGone'] and all(not terminal[k] for k in
        ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')) else 1


if __name__ == '__main__':
    raise SystemExit(main())
