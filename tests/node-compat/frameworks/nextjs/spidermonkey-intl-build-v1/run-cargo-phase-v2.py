"""Run one explicitly selected Cargo metadata/vendor phase; no compilation.
Existing owned-process and disk-floor monitors surround the actual command.
V2 always attempts final protection and failure publication after an operational
or collector exception. The outer operational budget includes worker startup;
original monitor cleanup is additional. V1 instead allowed seconds+60 before
that cleanup; its bytes and the actual Cargo101 outcome remain unchanged.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
MONITOR = ('tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py', '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe')
LIFE = ('tests/node-compat/foundation-scheduler/resource-build-controller-candidate-v1/lifecycle.py', '54557e22b4cd1c99cdc67c6dc8ff55826fae0d47a6b6481b72019c9480e5293d')


def row(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024**2), b''):
            h.update(block)
    return dict(path=str(path), bytes=path.stat().st_size, sha256=h.hexdigest())


def read(ref):
    assert row(ref['path']) == ref
    return json.loads(Path(ref['path']).read_text())


def save(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def load(path, sha, name):
    assert row(path)['sha256'] == sha
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def packet(path):
    value = json.loads(Path(path).read_text())
    authority = read(value['authority'])
    assert authority['state'] == 'ROOT_CARGO_METADATA_VENDOR_PHASE_V1'
    assert row(Path(__file__).resolve()) == authority['caller']
    plan = read(authority['plan'])
    assert plan['helperSource'] == authority['helper']
    command = next(x for x in plan['commands'] if x['id'] == authority['phase'])
    assert command == value['command']
    assert command['argv'][1] in ('metadata', 'vendor')
    assert type(command['seconds']) is int and 0 < command['seconds'] <= 600
    assert authority['nativeCompilationAllowed'] is False and authority['guestExecutionAllowed'] is False
    return value, authority, plan, command


def invoke(path):
    value, authority, plan, command = packet(path)
    work = Path(plan['work'])
    with (work / command['stdout']).open('xb') as out, (work / command['stderr']).open('xb') as err:
        process = subprocess.run(command['argv'], cwd=command['cwd'], env=command['environment'], stdout=out, stderr=err)
    save(Path(value['output']) / 'cargo-status.json', dict(rawCargoExitCode=process.returncode))
    return 0 if process.returncode == 0 else 1


def worker(path):
    value, authority, plan, command = packet(path)
    life = load(REPO / LIFE[0], LIFE[1], 'actual_cargo_disk_monitor')
    out = Path(value['output'])
    samples = []

    def free():
        n = shutil.disk_usage(plan['work']).free
        samples.append(n)
        return n

    with (out / 'launcher.log').open('xb') as log:
        result = life.monitor_owned_command([sys.executable, '-B', '-I', str(Path(__file__).resolve()), '--invoke', str(path)],
                                           plan['work'], command['environment'], log, free, minimum_free=2 * 1024**3)
    result['diskSamplesBytes'] = samples
    save(out / 'worker-result.json', result)
    cleanup = result.get('ownedGroupCleanup') or {}
    return 0 if (result['rawChildExitCode'] == 0 and result['lifecycleComplete'] and not result['stopReason'] and not result['sigtermReceived'] and
                 not result['launcherErrors'] and cleanup.get('complete') and not cleanup.get('events') and not cleanup.get('errors')) else 1


def main(authority_path):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    ar = row(authority_path)
    authority = read(ar)
    # Refuse an unissued/wrong Root before any custom module import.
    assert authority['schemaVersion'] == 1 and authority['state'] == 'ROOT_CARGO_METADATA_VENDOR_PHASE_V1'
    assert row(Path(__file__).resolve()) == authority['caller']
    assert authority['nativeCompilationAllowed'] is False and authority['guestExecutionAllowed'] is False
    plan = read(authority['plan'])
    assert plan['helperSource'] == authority['helper'] and plan['nativeCompilationAllowed'] is False
    assert row(authority['helper']['path']) == authority['helper']
    command = next(x for x in plan['commands'] if x['id'] == authority['phase'])
    assert command['argv'][1] in ('metadata', 'vendor')
    assert type(command['seconds']) is int and 0 < command['seconds'] <= 600
    output = Path(authority['output'])
    assert output.is_absolute() and '..' not in output.parts and not output.is_symlink()
    assert not output.exists() and output.parent == Path(plan['work']) / 'phases'
    result = dict(schemaVersion=1, callerVersion=2, phase=authority['phase'], authority=ar,
                  rawCargoExitCode=None, terminal=None, sourceProtection=None,
                  nativeOrGuestExecuted=False, passed=False, errors=[],
                  timeoutPolicy=dict(outerOperationalSeconds=command['seconds'], workerStartupIncluded=True,
                                     cleanup='Original owned monitor bounded cleanup is additional to the operational deadline',
                                     preservedV1OuterOperationalSeconds=command['seconds'] + 60,
                                     preservedV1Additional60WasOperationalBudget=True))
    helper = None
    terminal = None
    output_created = False
    operational_checks_passed = False

    def failed(stage, error):
        record = dict(stage=stage, type=type(error).__name__, message=str(error),
                      traceback=''.join(traceback.format_exception(type(error), error, error.__traceback__)))
        result['errors'].append(record)
        result.setdefault('error', record)
        result['passed'] = False

    try:
        output.mkdir()
        output_created = True
        save(output / 'packet.json', dict(authority=ar, command=command, output=str(output)))
        helper = load(authority['helper']['path'], authority['helper']['sha256'], 'held_cargo_resolver')
        assert command['environment']['HOME'] == os.environ['HOME']
        assert shutil.disk_usage(plan['work']).free >= 3 * 1024**3
        if authority['phase'] != 'resolve-online':
            previous = read(authority['previousResult'])
            audit = read(authority['previousAudit'])
            assert previous['passed'] is True and previous['rawCargoExitCode'] == 0
            assert audit['lockPolicyPassed'] is True
            if authority['phase'].startswith('metadata-offline'):
                assert audit['mozillaPatchedBidiRustAndManifestMatch'] is True
                assert audit['vendorChecksums']['allRecordedChecksumsMatch'] is True
        result['beforeSourceProtection'] = helper.recheck(plan['work'])
        outer = output / 'owned-monitor'
        outer.mkdir()
        monitor = load(REPO / MONITOR[0], MONITOR[1], 'actual_cargo_owned_monitor')
        # This is the complete worker/invoke operational budget, not a budget
        # plus another minute of operation. Original monitor cleanup remains.
        terminal = monitor.monitor([sys.executable, '-B', '-I', str(Path(__file__).resolve()), '--worker', str(output / 'packet.json')],
                                   plan['work'], command['environment'], outer, command['seconds'], ar)
        result['terminal'] = row(outer / 'terminal.json')
        status = output / 'cargo-status.json'
        if status.exists():
            result['rawCargoExitCode'] = json.loads(status.read_text())['rawCargoExitCode']
        for name in ('stdout', 'stderr'):
            path = Path(plan['work']) / command[name]
            result[name] = row(path) if path.exists() else None
        assert result['rawCargoExitCode'] == 0 and terminal['rawExitCode'] == 0
        assert terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and not terminal['timeout'] and not terminal['forcedCleanup']
        assert all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
        inner = json.loads((output / 'worker-result.json').read_text())
        cleanup = inner['ownedGroupCleanup']
        assert inner['rawChildExitCode'] == 0 and inner['lifecycleComplete'] and not inner['stopReason'] and not inner['sigtermReceived']
        assert not inner['launcherErrors'] and cleanup['complete'] and not cleanup['events'] and not cleanup['errors']
        operational_checks_passed = True
    except BaseException as error:
        failed('operation-or-collection', error)
    finally:
        # Retain whatever exists even when monitor(), status parsing or a
        # stream descriptor raised. Collection errors never skip final checks.
        for key, path in [('terminal', output / 'owned-monitor/terminal.json'),
                          ('workerResult', output / 'worker-result.json'),
                          ('cargoStatus', output / 'cargo-status.json'),
                          ('stdout', Path(plan['work']) / command['stdout']),
                          ('stderr', Path(plan['work']) / command['stderr'])]:
            try:
                result[key] = row(path) if path.exists() else None
            except BaseException as error:
                failed('final-collection-' + key, error)
        try:
            status = output / 'cargo-status.json'
            if status.exists():
                result['rawCargoExitCode'] = json.loads(status.read_text())['rawCargoExitCode']
        except BaseException as error:
            failed('final-cargo-status', error)
        result['finalSourceProtectionAttempted'] = helper is not None
        try:
            if helper is None:
                raise RuntimeError('Authenticated helper was unavailable before operation; source protection is not claimed')
            result['sourceProtection'] = helper.recheck(plan['work'])
            assert row(Path(__file__).resolve()) == authority['caller']
            assert read(ar) == authority and read(authority['plan']) == plan
            assert row(authority['helper']['path']) == authority['helper']
            result['callerAuthorityPlanHelperUnchanged'] = True
        except BaseException as error:
            failed('final-source-protection', error)
        result['passed'] = operational_checks_passed and not result['errors'] and result['sourceProtection'] is not None
        result['resultPublicationAttempted'] = output_created
        if output_created:
            try:
                save(output / 'result.json', result)
            except BaseException as error:
                failed('result-publication', error)
                # Exclusive secondary publication never overwrites a partial
                # result. Full stdout is another retained failure channel.
                try:
                    save(output / 'failure-publication.json', result)
                except BaseException as secondary:
                    failed('secondary-failure-publication', secondary)
        print(json.dumps(result), flush=True)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] in ('--invoke', '--worker'):
        raise SystemExit(invoke(sys.argv[2]) if sys.argv[1] == '--invoke' else worker(sys.argv[2]))
    assert len(sys.argv) == 2
    raise SystemExit(main(Path(sys.argv[1])))
