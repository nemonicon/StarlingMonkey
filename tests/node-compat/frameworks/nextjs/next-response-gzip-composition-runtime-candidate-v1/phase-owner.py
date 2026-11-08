"""One explicit Root reference/guest phase through the genuine original180 owner."""
from pathlib import Path
import importlib.util
import json
import os
import shutil
import sys

HERE = Path(__file__).resolve().parent


def main():
    assert __debug__ and sys.flags.isolated == 1 and sys.dont_write_bytecode and len(sys.argv) == 3
    spec = importlib.util.spec_from_file_location('gzip_phase_admission', HERE / 'admission.py')
    h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
    authority_path, phase = Path(sys.argv[1]), sys.argv[2]
    assert phase in ['reference', 'wire']
    a, p, ar, layout = h.context(authority_path)
    assert str(Path(sys.executable).resolve()) == p['python']['path']
    grant = a['nodeReferenceAuthority' if phase == 'reference' else 'wireAuthority']
    output = layout['referenceOwner' if phase == 'reference' else 'wireOwner']
    assert not os.path.lexists(output)
    assert shutil.disk_usage(output.parent).free >= p['minimumFreeBytes']
    os.umask(0o077); output.mkdir(mode=0o700)  # MUST precede original monitor call.
    terminal = None; primary = None; protection = None
    argv = h._models.phase_argv(p, HERE, a, phase, authority_path)
    try:
        monitor = h.load(p['monitor'], 'original_gzip_' + phase + '_owner')
        env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
        env.update(PATH=str(Path(p['node']['path']).parent) + ':/usr/bin:/bin', LANG='C', LC_ALL='C', CI='1')
        terminal = monitor.monitor(argv, p['cwd'], env, output, 180, grant)
    except BaseException as error:
        primary = dict(type=type(error).__name__, message=str(error))
    finally:
        try: h.context(authority_path)
        except BaseException as error: protection = dict(type=type(error).__name__, message=str(error))
        passed = bool(terminal and h.ownership_clean(terminal) and terminal['rawExitCode'] == 0 and primary is None and protection is None)
        observation = dict(schemaVersion=1, state='GZIP_COMPOSITION_PHASE_CAPTURE_OBSERVATION_V1', phase=phase,
            rootAuthority=ar, phaseAuthority=grant, argv=argv, origin=a['origin'],
            rawExitCode=terminal['rawExitCode'] if terminal else None, ownedGroupsClean=bool(terminal and h.ownership_clean(terminal)),
            protectedInputsPreserved=protection is None, primaryError=primary, protectionError=protection,
            terminal=h.row(output / 'terminal.json') if terminal else None, captureCompletedCleanly=passed,
            semanticPassClaimed=False, fullNextAccepted=False, adoption=False)
        h.save(output / 'observation.json', observation, fresh=True)
    print(json.dumps(observation), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
