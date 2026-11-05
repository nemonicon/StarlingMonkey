"""Exact accepted342 lifecycle segments only; no admission read or old launcher main."""
import errno

import hashlib

import json

import os

from pathlib import Path

import signal

import subprocess

import sys

import time

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

if __name__ == "__main__":
    raise RuntimeError("Use the separately reviewed scheduler normal-OFF build caller")
