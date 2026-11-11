"""Root's fixed outer owner for the native build; no guest is executed."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ROOT = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first')
OUTPUT = ROOT / 'commands/native-build'
RUNNER_SHA = '1cad0ccb6ffd3a5fe55f243b0c3728957e282970503f88287c8d8b59e870f3de'
SELECTION_SHA = 'cc807f6ea77a7ac951114d11ec03c952ad6cdffcdfc9d79192a48a23c41c8bcc'
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
MONITOR_SHA = '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'


def row(path):
    path = Path(path)
    assert path.resolve(strict=True) == path and path.is_file()
    before = path.stat(); raw = path.read_bytes(); after = path.stat()
    assert (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def save(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    return row(path)


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode or len(sys.argv) != 1:
        raise RuntimeError('Use Python -I -B without optimization or arguments')
    runner = row(HERE / 'run-build.py'); selected = row(HERE / 'build-selection.json')
    owner_ref = row(MONITOR)
    assert runner['sha256'] == RUNNER_SHA and runner['bytes'] == 40260
    assert selected['sha256'] == SELECTION_SHA and selected['bytes'] == 21843
    assert owner_ref['sha256'] == MONITOR_SHA and owner_ref['bytes'] == 15094
    selection = json.loads(Path(selected['path']).read_bytes())
    python = row(Path(selection['wrapperPython']['path']))
    assert python == selection['wrapperPython'] and row(Path(sys.executable).resolve()) == python
    inputs = [runner, selected, owner_ref, python, row(Path(__file__).resolve()),
              row(HERE / 'prepare-source.py'), row(HERE / 'run-generators.py')]
    for ref in (selection['lifecycle'],):
        assert row(Path(ref['path'])) == ref; inputs.append(ref)
    assert OUTPUT.parent.resolve() == OUTPUT.parent and OUTPUT.parent.is_dir()
    OUTPUT.mkdir(mode=0o700)
    env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
    env.update(PATH='/usr/bin:/bin', PYTHONDONTWRITEBYTECODE='1')
    argv = [python['path'], '-I', '-B', runner['path']]
    request = dict(schemaVersion=1, state='ROOT_FIXED_NATIVE_BUILD_OWNER_REQUEST_V1',
                   argv=argv, cwd=str(REPO), environment=env, seconds=10800,
                   protectedInputs=inputs, configureCapSeconds=2400, buildCapSeconds=7200,
                   nativeBuildAllowed=True, guestExecutionAllowed=False)
    request_ref = save(OUTPUT / 'request.json', request)
    spec = importlib.util.spec_from_file_location('genuine_native_outer_owner', MONITOR)
    owner = importlib.util.module_from_spec(spec); spec.loader.exec_module(owner)
    terminal = None; primary = None; verification_error = None; unchanged = False
    try:
        terminal = owner.monitor(argv, str(REPO), env, OUTPUT, 10800, request_ref)
    except BaseException as error:
        primary = dict(type=type(error).__name__, message=str(error))
    try:
        unchanged = all(row(Path(ref['path'])) == ref for ref in inputs)
        assert unchanged, 'Native wrapper protected input changed'
    except BaseException as error:
        verification_error = dict(type=type(error).__name__, message=str(error))
    clean = bool(terminal and terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] and
                 terminal['allObservedOwnedGroupsGone'] and not terminal['timeout'] and not terminal['forcedCleanup'] and
                 not terminal['interruptedSignals'] and not terminal['errors'] and not terminal['signals'] and
                 not terminal['remainingObservedPids'])
    terminal_ref = None; collection_errors = []
    try:
        if (OUTPUT / 'terminal.json').is_file():
            terminal_ref = row(OUTPUT / 'terminal.json')
        elif terminal is not None:
            raise FileNotFoundError('Original monitor returned without its terminal publication')
    except BaseException as error:
        collection_errors.append(dict(type=type(error).__name__, message=str(error)))
    result = dict(schemaVersion=1, request=request_ref, terminal=terminal_ref,
                  rawExitCode=terminal['rawExitCode'] if terminal else None,
                  primaryError=primary, verificationError=verification_error,
                  inputsUnchanged=unchanged, clean=clean, collectionErrors=collection_errors,
                  guestConformanceClaim=False)
    try:
        result_ref = save(OUTPUT / 'collection.json', result)
    except BaseException as error:
        print(json.dumps(dict(collectionPublicationFailed=True, result=result,
                              publicationError=dict(type=type(error).__name__, message=str(error)))),
              file=sys.stderr, flush=True)
        return 1
    print(json.dumps(dict(collection=result_ref, rawExitCode=result['rawExitCode'], clean=clean,
                          inputsUnchanged=unchanged, guestConformanceClaim=False)), flush=True)
    return 0 if clean and unchanged and primary is None and verification_error is None and not collection_errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
