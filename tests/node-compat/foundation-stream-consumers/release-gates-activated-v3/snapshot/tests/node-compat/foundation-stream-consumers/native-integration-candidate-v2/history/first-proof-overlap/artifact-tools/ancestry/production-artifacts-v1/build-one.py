"""One-job production306 launcher with bounded cleanup of its own new session only.

Importing this module launches nothing. Tests may call the lifecycle helpers
with benign Python children; main is the separately reviewed native launcher.
"""
import errno
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


RECIPE_SHA256 = '869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173'
MINIMUM_FREE = 800 * 1024 * 1024
REQUIRED_START_FREE = 2 * 1024 * 1024 * 1024


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def error_record(stage, error):
    return {'stage': stage, 'type': type(error).__name__, 'message': str(error)}


class ExternalTermination(Exception):
    pass


class OwnedSession:
    """Only constructed for the Popen this helper starts with setsid enabled."""
    def __init__(self, process):
        self.process = process
        self.pgid = process.pid
        assert self.pgid > 1 and self.pgid != os.getpgrp()
        self.gone = False
        self.events = []

    def alive(self):
        if self.gone:
            return False
        # Reap only our own leader before querying the group. A dead unreaped
        # leader is not useful group-liveness evidence after SIGKILL.
        self.process.poll()
        try:
            os.killpg(self.pgid, 0)
            return True
        except OSError as error:
            if error.errno != errno.ESRCH:
                raise
            self.gone = True
            return False

    def send(self, number):
        if self.gone:
            return
        try:
            os.killpg(self.pgid, number)
            self.events.append({'signal': number, 'result': 'sent', 'pgid': self.pgid})
        except OSError as error:
            if error.errno != errno.ESRCH:
                raise
            # A completed group is terminal: do not signal this number again.
            self.gone = True
            self.events.append({'signal': number, 'result': 'already-gone', 'pgid': self.pgid})

    def cleanup(self, term_seconds=10.0, kill_seconds=5.0, interval=0.05):
        """Escalate against the group even after its shell leader has exited."""
        problems = []
        complete = False
        try:
            if self.alive():
                self.send(signal.SIGTERM)
                deadline = time.monotonic() + term_seconds
                while self.alive() and time.monotonic() < deadline:
                    self.process.poll()  # Preserve raw leader status; not a group-liveness test.
                    time.sleep(interval)
                if self.alive():
                    self.send(signal.SIGKILL)
                    deadline = time.monotonic() + kill_seconds
                    while self.alive() and time.monotonic() < deadline:
                        self.process.poll()
                        time.sleep(interval)
            complete = not self.alive()
        except BaseException as error:
            problems.append(error_record('group-cleanup', error))
            # Even an interrupted/failed monitor must attempt bounded escalation
            # of this OWNED group; no PID lookup or other group is substituted.
            try:
                self.send(signal.SIGKILL)
            except BaseException as escalation_error:
                problems.append(error_record('group-escalation', escalation_error))
        try:
            self.process.wait(timeout=max(0.1, kill_seconds))
        except BaseException as error:
            problems.append(error_record('leader-reap', error))
        try:
            complete = not self.alive()
        except BaseException as error:
            problems.append(error_record('final-group-observation', error))
        return {'pgid': self.pgid, 'complete': complete, 'events': self.events,
                'errors': problems, 'rawChildExitCode': self.process.returncode}


def monitor_owned_command(command, cwd, environment, log, free_bytes,
                          minimum_free=MINIMUM_FREE, interval=1.0,
                          term_seconds=10.0, kill_seconds=5.0):
    """Always return lifecycle status, including startup/monitor/cleanup errors."""
    process = None
    owner = None
    problems = []
    stop_reason = None
    cleanup = None
    low_space = False
    cleanup_started = False
    spawning = True
    term_count = 0
    previous_term_handler = None
    handler_installed = False
    handler_restored = False

    def receive_term(_number, _frame):
        nonlocal term_count
        term_count += 1
        # Repeated cancellation is recorded, but cannot interrupt bounded group
        # cleanup and orphan its new-session children.
        if not cleanup_started and not spawning and term_count == 1:
            raise ExternalTermination('launcher received SIGTERM')

    try:
        previous_term_handler = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGTERM, receive_term)
        handler_installed = True
        process = subprocess.Popen(command, cwd=cwd, env=environment, stdout=log,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        owner = OwnedSession(process)
        # Do not interrupt Popen between child creation and ownership handoff.
        # A TERM recorded during those few setup steps cancels immediately now.
        spawning = False
        if term_count:
            raise ExternalTermination('launcher received SIGTERM during child setup')
        # Popen returns only after the child setsid/exec setup succeeds. Never
        # derive a signal target from an unrelated queried process or a caller.
        try:
            assert os.getpgid(process.pid) == process.pid
            assert os.getsid(process.pid) == process.pid
        except ProcessLookupError:
            pass  # Leader may already have exited; owned descendants can remain.
        while process.poll() is None:
            if free_bytes() < minimum_free:
                low_space = True
                stop_reason = 'disk-space-stop'
                break
            time.sleep(interval)
    except BaseException as error:
        stop_reason = ('external-signal-stop' if isinstance(error, ExternalTermination)
                       else 'launcher-or-monitor-error')
        problems.append(error_record('launch-or-monitor', error))
    finally:
        cleanup_started = True
        if owner is not None:
            try:
                cleanup = owner.cleanup(term_seconds, kill_seconds)
                problems.extend(cleanup['errors'])
            except BaseException as error:
                problems.append(error_record('cleanup-finalization', error))
        raw_status = process.returncode if process is not None else None
        if term_count and stop_reason is None:
            stop_reason = 'external-signal-stop'
        if handler_installed:
            try:
                signal.signal(signal.SIGTERM, previous_term_handler)
                handler_restored = True
            except BaseException as error:
                problems.append(error_record('restore-sigterm-handler', error))
    return {'rawChildExitCode': raw_status, 'status': raw_status,
            'stoppedForDiskSpace': low_space, 'stopReason': stop_reason,
            'sigtermReceived': term_count, 'temporarySigtermHandlerRestored': handler_restored,
            'ownedGroupCleanup': cleanup, 'launcherErrors': problems,
            'childStarted': process is not None,
            'lifecycleComplete': cleanup is not None and cleanup['complete'] and raw_status is not None}


def prepare_output(output, free_bytes, required=REQUIRED_START_FREE):
    before = free_bytes()
    if before < required:
        raise RuntimeError('Need at least 2 GiB available before retry')
    output.mkdir(parents=True, exist_ok=False)
    return before


def publish_result(output, result, stream=sys.stdout, writer=None):
    """Keep the complete status on stdout even if fresh result storage fills."""
    try:
        if writer is None:
            with (output / 'result.json').open('x') as target:
                json.dump(result, target, indent=2)
                target.write('\n')
        else:
            writer(output / 'result.json', result)
    except OSError as error:
        result['resultFileWriteError'] = error_record('result-file-write', error)
        result['evidenceComplete'] = False
        result['launcherExitCode'] = 1
        result['state'] = 'native-build-failed-or-evidence-incomplete'
    print(json.dumps({'output': str(output), 'result': result}), file=stream, flush=True)


def finalize_status(result):
    succeeded = (result.get('rawChildExitCode') == 0 and result.get('lifecycleComplete') is True
                 and not result.get('stoppedForDiskSpace') and not result.get('launcherErrors')
                 and not result.get('sigtermReceived') and not result.get('finalObservationErrors'))
    result['state'] = 'native-build-completed-runtime-pending' if succeeded else 'native-build-failed-or-incomplete'
    result['launcherExitCode'] = 0 if succeeded else 1
    result['evidenceComplete'] = succeeded


def main():
    if not __debug__:
        raise RuntimeError('Launcher validation requires Python assertions enabled')
    assert len(sys.argv) == 2
    label = sys.argv[1]
    assert label in ('normal-off', 'normal-runtime', 'gc-off')
    sys.dont_write_bytecode = True
    from artifact_common import OUTPUT, verify_frozen_variant
    root = Path(__file__).resolve().parents[4]
    work = Path('/tmp/starling-node-compat/improved-build')
    output = Path('/tmp/starling-node-compat/production-scheduler-artifacts-v1/builds') / label
    recipe = root / 'tests/node-compat/build-engine.sh'
    assert digest(recipe) == RECIPE_SHA256
    prior = None
    if label == 'gc-off':
        prior_path, prior_receipt, prior_metadata = verify_frozen_variant('normal-off')
        assert prior_metadata['gcStress'] is False and prior_metadata['entropyPolicy'] == 'off'
        prior = {'path': str(prior_path), 'sha256': digest(prior_path), 'engineSha256': prior_receipt['engineSha256']}
    environment = {
        'NODE_COMPAT_NODE': '/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',
        'NODE_COMPAT_JOBS': '1', 'BINARYEN_CORES': '1', 'RAYON_NUM_THREADS': '1',
        'CARGO_BUILD_JOBS': '1', 'NODE_COMPAT_BUILD_TYPE': 'Release',
        'NODE_COMPAT_OOM_TESTING': '0', 'NODE_COMPAT_BUILD_ROOT': str(work),
        'NODE_COMPAT_ABI_FIX': '1', 'NODE_COMPAT_BIGINT_FIX': '1',
        'NODE_COMPAT_INTERNAL_TICKS': '1',
        'NODE_COMPAT_ENTROPY_MODE': 'RUNTIME_ONLY' if label == 'normal-runtime' else 'OFF',
        'NODE_COMPAT_GC_STRESS': '1' if label == 'gc-off' else '0',
        'NODE_COMPAT_ARTIFACT_TAG': 'p306v1',
        **{'NODE_COMPAT_' + name: '1' for name in
           ('PATH', 'EVENTS', 'STRING_DECODER', 'ASSERT', 'QUERYSTRING', 'UTIL', 'STREAM_WEB')},
    }
    free = lambda: os.statvfs(work).f_bavail * os.statvfs(work).f_frsize
    try:
        free_before = prepare_output(output, free)
    except BaseException as error:
        print(json.dumps({'output': str(output), 'state': 'not-launched',
                          'rawChildExitCode': None, 'error': error_record('precondition', error)}), flush=True)
        return 1
    started = time.monotonic()
    result = {'schemaVersion': 2, 'state': 'native-build-not-started', 'label': label,
              'recipeSha256': digest(recipe), 'launcherSha256': digest(Path(__file__)),
              'command': ['bash', str(recipe)], 'explicitEnvironment': environment,
              'freeBytesBefore': free_before, 'requiredStartFreeBytes': REQUIRED_START_FREE,
              'stopBelowFreeBytes': MINIMUM_FREE, 'guestExecutionRequested': False,
              'parallelBuilds': 1, 'rawChildExitCode': None,
              'normalOffFrozenBeforeGCReconfigure': prior, 'freezeRoot': str(OUTPUT)}
    try:
        with (output / 'launch.json').open('x') as target:
            json.dump(result, target, indent=2)
            target.write('\n')
        with (output / 'build.log').open('xb') as log:
            child_environment = {key: value for key, value in os.environ.items()
                                 if not key.startswith(('NODE_COMPAT_', 'CMAKE_PROJECT_')) and key != 'NODE_OPTIONS'}
            child_environment.update(environment)
            result.update(monitor_owned_command(result['command'], root,
                          child_environment, log, free))
    except BaseException as error:
        result.setdefault('launcherErrors', []).append(error_record('launch-record-or-log', error))
    result['wallSecondsForOperationalRecordOnly'] = time.monotonic() - started
    try:
        result['freeBytesAfter'] = free()
    except BaseException as error:
        result.setdefault('finalObservationErrors', []).append(error_record('final-disk-observation', error))
    try:
        result['logSha256'] = digest(output / 'build.log')
    except BaseException as error:
        result.setdefault('finalObservationErrors', []).append(error_record('final-log-hash', error))
    finalize_status(result)
    publish_result(output, result)
    return result['launcherExitCode']


if __name__ == '__main__':
    sys.exit(main())
