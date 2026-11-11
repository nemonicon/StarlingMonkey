"""Run the ten genuine installed generator checks on the new recipe."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
WORK = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first')
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'
MONITOR_SHA = '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    utility = load(HERE / 'prepare-source.py', 'clone_cancel_source_utilities')
    materialization_ref = utility.descriptor(WORK / 'source-materialization.json')
    m = utility.read(materialization_ref)
    assert m['state'] == 'CLONE_CANCEL_825_INPUTS_MATERIALIZED_V1' and m['workRoot'] == str(WORK)
    assert (m['nativeCount'], m['supportCount'], m['embeddingCount']) == (435, 387, 3)
    assert m['changedNativePaths'] == ['builtins/web/fetch/request-response.cpp']
    assert m['recipe'] == utility.descriptor(HERE / 'prepare-source.py')
    assert len(m['copies']) == 825 and len(m['generatorCommands']) == 10
    monitor_ref = utility.descriptor(MONITOR)
    assert monitor_ref['sha256'] == MONITOR_SHA
    inputs = [materialization_ref, m['recipe'], utility.descriptor(__file__), monitor_ref,
              m['generatorNode']] + [r['target'] for r in m['copies']]
    for row in inputs:
        utility.checked(row)
    output = WORK / 'generator-checks'
    assert not os.path.lexists(output)
    output.mkdir(mode=0o700)
    env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME'] if k in os.environ}
    env.update(PATH='/usr/bin:/bin', LC_ALL='C', LANG='C', TMPDIR=str(WORK / 'tmp'))
    request = dict(schemaVersion=1, sourceMaterialization=materialization_ref,
                   commands=m['generatorCommands'], environment=env, protectedInputs=inputs)
    request_ref = utility.save(output / 'request.json', request)
    owner = load(MONITOR, 'clone_cancel_genuine_generator_owner')
    records = []
    primary = None
    try:
        for cmd in m['generatorCommands']:
            assert cmd['argv'][0] == m['generatorNode']['path'] and cmd['argv'][-1] == '--check'
            assert cmd['cwd'] == str(WORK / 'native-source') and cmd['seconds'] == 120
            folder = output / cmd['label']; folder.mkdir(mode=0o700)
            t = owner.monitor(cmd['argv'], cmd['cwd'], env, folder, cmd['seconds'], request_ref)
            clean = (t['rawExitCode'] == 0 and t['allObservedOwnedGroupsGone'] and
                     not t['timeout'] and not t['forcedCleanup'] and not t['interruptedSignals'] and
                     not t['errors'] and not t['signals'])
            row = dict(command=cmd, terminal=utility.descriptor(folder / 'terminal.json'),
                       stdout=utility.descriptor(folder / 'stdout.log'), stderr=utility.descriptor(folder / 'stderr.log'),
                       rawExitCode=t['rawExitCode'], clean=bool(clean))
            records.append(row)
            assert clean and row['stderr']['bytes'] == 0, cmd['label']
    except BaseException as error:
        primary = dict(type=type(error).__name__, message=str(error))
    verification_error = None
    unchanged = False
    try:
        unchanged = all(utility.descriptor(r['path']) == r for r in inputs)
        if not unchanged:
            raise RuntimeError('Protected generator input changed')
    except BaseException as error:
        verification_error = dict(type=type(error).__name__, message=str(error))
    passed = primary is None and unchanged and len(records) == 10
    result = dict(schemaVersion=1, state='CLONE_CANCEL_GENERATOR_CHECKS_COMPLETED_V1',
                  request=request_ref, commands=records, passed=passed,
                  primaryError=primary, verificationError=verification_error,
                  inputsUnchanged=unchanged, nativeBuildExecuted=False,
                  guestExecuted=False, freshNodeChecks=True)
    ref = utility.save(output / 'result.json', result)
    print(json.dumps(dict(result=ref, passed=passed)), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
