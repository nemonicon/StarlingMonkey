"""Read-only plan by default; a future bound Root grant owns exactly one controller."""
from pathlib import Path
import importlib.util
import json
import os
import shutil
import sys

HERE = Path(__file__).resolve().parent


def helper():
    spec = importlib.util.spec_from_file_location('gzip_runtime_admission', HERE / 'admission.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def main():
    assert __debug__ and sys.flags.isolated == 1 and sys.dont_write_bytecode
    h = helper()
    if len(sys.argv) == 1:
        p = h.read(HERE / 'plan.json')
        print(json.dumps(dict(sourceOnly=True, actionsAllowed=False,
            prospectiveActualBindingsPending=p['prospectiveActualBindingsPending'], ownerInvoked=False)))
        return 0
    assert len(sys.argv) == 2
    authority_path = Path(sys.argv[1]); a, p, ar, layout = h.context(authority_path)
    assert str(Path(sys.executable).resolve()) == p['python']['path']
    assert not any(os.path.lexists(path) for path in layout.values())
    assert shutil.disk_usage(layout['output'].parent).free >= p['minimumFreeBytes']
    before = h.native_guard(a, p)
    os.umask(0o077)
    # Original monitor requires the output directory already to exist.
    layout['outer'].mkdir(mode=0o700)
    h.save(layout['outer'] / 'admission.json', dict(authority=ar, freeBytes=shutil.disk_usage(layout['output'].parent).free,
        minimumFreeBytes=p['minimumFreeBytes'], continuousDiskFloorClaimed=False, commandInvoked=False), fresh=True)
    terminal = None; primary = None; protection = None; result = None; world_after = None
    try:
        monitor = h.load(p['monitor'], 'original_gzip_controller_owner')
        env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
        env.update(PATH=str(Path(p['node']['path']).parent) + ':/usr/bin:/bin', LANG='C', LC_ALL='C', CI='1')
        terminal = monitor.monitor([p['node']['path'], str(HERE / 'control.mjs'), str(authority_path)], p['cwd'],
                                   env, layout['outer'], 600, ar)
    except BaseException as error:
        primary = dict(type=type(error).__name__, message=str(error))
    finally:
        try:
            h.context(authority_path)
            world_after = h.native_guard(a, p)
            assert world_after == before
        except BaseException as error:
            protection = dict(type=type(error).__name__, message=str(error))
        try:
            if (layout['output'] / 'result.json').is_file(): result = h.read(layout['output'] / 'result.json')
        except BaseException as error:
            if primary is None: primary = dict(type=type(error).__name__, message=str(error))
        passed = bool(terminal and h.ownership_clean(terminal) and terminal['rawExitCode'] == 0 and primary is None and protection is None and result and result['passed'] is True)
        observation = dict(schemaVersion=1, state='GZIP_COMPOSITION_CONTROLLER_OBSERVATION_V1', rootAuthority=ar,
            runId=a['runId'], sourceIndex=a['sourceIndex'], rawExitCode=terminal['rawExitCode'] if terminal else None,
            ownedGroupsClean=bool(terminal and h.ownership_clean(terminal)), protectedInputsPreserved=protection is None,
            primaryError=primary, protectionError=protection,
            terminal=h.row(layout['outer'] / 'terminal.json') if terminal else None,
            result=h.row(layout['output'] / 'result.json') if result else None,
            worldBefore=before, worldAfter=world_after, worldUnchanged=world_after == before,
            passed=passed, publicProfileOnly=True, nativeResourceCountsProved=False, fullNextAccepted=False, adoption=False)
        h.save(layout['outer'] / 'observation.json', observation, fresh=True)
    print(json.dumps(observation), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
