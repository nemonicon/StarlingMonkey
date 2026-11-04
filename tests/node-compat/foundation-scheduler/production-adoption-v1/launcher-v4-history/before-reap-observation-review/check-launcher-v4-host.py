"""Benign host-Python lifecycle checks only; no producer/compiler/guest call."""
import errno
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'build-one-diagnostic-v4.py'
spec = importlib.util.spec_from_file_location('diagnostic_launcher_v4', SOURCE)
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)  # main guard: no build is launched.
OUTPUT = HERE / 'launcher-v4-host-checks-v2'
OUTPUT.mkdir(exist_ok=False)
results = []


def checked(condition, name):
    assert condition, name


with tempfile.TemporaryDirectory(prefix='sm-launcher-v4-own-') as temporary:
    root = Path(temporary)
    forbidden_output = root / 'insufficient' / 'must-not-exist'
    try:
        launcher.prepare_output(forbidden_output, lambda: 0)
        raise AssertionError('Capacity guard should fail')
    except RuntimeError:
        checked(not forbidden_output.parent.exists(), 'no capacity-side directory')
    existing = root / 'existing'
    existing.mkdir()
    (existing / 'marker').write_text('unchanged')
    try:
        launcher.prepare_output(existing, lambda: launcher.REQUIRED_START_FREE)
        raise AssertionError('Collision should fail')
    except FileExistsError:
        checked((existing / 'marker').read_text() == 'unchanged', 'collision bytes')
    results.append({'name': 'capacity-and-output-collision', 'passed': True,
                    'directoryCreatedOnInsufficientCapacity': False})

    # Both children stay in this ONE new session/group. The leader exits0 on
    # TERM while its grandchild deliberately ignores TERM until KILL (or its
    # five-second safety exit). No unrelated process/group is signalled.
    grandchild_ready = root / 'grandchild-ready'
    leader_ready = root / 'leader-ready'
    grandchild = (
        "import os,signal,time;from pathlib import Path;"
        "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
        f"Path({str(grandchild_ready)!r}).write_text(str(os.getpid()));"
        "time.sleep(5)"
    )
    leader = (
        "import os,signal,subprocess,sys,time;from pathlib import Path;"
        "signal.signal(signal.SIGTERM,lambda *_:sys.exit(0));"
        f"child=subprocess.Popen([sys.executable,'-c',{grandchild!r}]);"
        f"Path({str(leader_ready)!r}).write_text(str(os.getpid()));"
        "time.sleep(5)"
    )
    with (OUTPUT / 'leader-grandchild.log').open('xb') as log:
        record = launcher.monitor_owned_command(
            [sys.executable, '-c', leader], root, dict(os.environ), log,
            lambda: 0 if grandchild_ready.exists() and leader_ready.exists() else 10**12,
            minimum_free=1, interval=0.01, term_seconds=0.2, kill_seconds=2)
    checked(record['rawChildExitCode'] == 0, 'raw leader exit0 retained after TERM')
    checked(record['stoppedForDiskSpace'] is True, 'disk stop recorded')
    signals = [item['signal'] for item in record['ownedGroupCleanup']['events']]
    checked(signal.SIGTERM in signals and signal.SIGKILL in signals,
            'KILL issued despite already exited leader')
    checked(record['ownedGroupCleanup']['complete'], 'owned group gone after KILL')
    results.append({'name': 'leader-exits-grandchild-survives-term', 'passed': True,
                    'leaderPid': int(leader_ready.read_text()),
                    'grandchildPid': int(grandchild_ready.read_text()), **record})

    # Real ESRCH from a completed group is benign and terminal. This test only
    # uses a child started here with start_new_session=True.
    with (OUTPUT / 'already-exited.log').open('xb') as log:
        child = subprocess.Popen([sys.executable, '-c', 'pass'], cwd=root,
                                 stdout=log, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        owner = launcher.OwnedSession(child)
        checked(child.wait(timeout=3) == 0, 'own quick child completed')
        owner.send(signal.SIGTERM)
        checked(owner.gone, 'ESRCH closes completed group')
        event_count = len(owner.events)
        owner.send(signal.SIGKILL)
        checked(len(owner.events) == event_count, 'never signal a closed group again')
        cleanup = owner.cleanup(term_seconds=0.1, kill_seconds=0.1)
    checked(cleanup['complete'] and cleanup['rawChildExitCode'] == 0, 'completed group status')
    results.append({'name': 'already-exited-group-esrch', 'passed': True, 'cleanup': cleanup})

    monitor_ready = root / 'monitor-ready'
    sleeper = ('import time;from pathlib import Path;'
               f'Path({str(monitor_ready)!r}).write_text("ready");time.sleep(5)')

    def failed_monitor():
        if monitor_ready.exists():
            raise RuntimeError('EXPECTED_BENIGN_MONITOR_ERROR')
        return 10**12

    with (OUTPUT / 'monitor-error.log').open('xb') as log:
        record = launcher.monitor_owned_command(
            [sys.executable, '-c', sleeper], root, dict(os.environ), log,
            failed_monitor, minimum_free=1, interval=0.01,
            term_seconds=0.2, kill_seconds=2)
    checked(record['rawChildExitCode'] == -signal.SIGTERM, 'raw child signal retained')
    checked(record['stopReason'] == 'launcher-or-monitor-error', 'monitor failure finalized')
    checked(any('EXPECTED_BENIGN_MONITOR_ERROR' in item['message']
                for item in record['launcherErrors']), 'original monitor error retained')
    checked(record['ownedGroupCleanup']['complete'], 'monitor-error child group cleaned')
    stream = io.StringIO()

    def full_disk(_path, _result):
        raise OSError(errno.ENOSPC, 'EXPECTED_SIMULATED_RESULT_WRITE_ENOSPC')

    launcher.publish_result(root, record, stream=stream, writer=full_disk)
    published = json.loads(stream.getvalue())['result']
    checked(published['rawChildExitCode'] == -signal.SIGTERM, 'stdout raw child status')
    checked(published['resultFileWriteError']['type'] == 'OSError', 'ENOSPC recorded')
    results.append({'name': 'monitor-error-and-simulated-enospc-finalization',
                    'passed': True, 'published': published})

    # External cancellation reaches a launcher in its own new session. Its
    # monitored child starts a separate owned session and ignores TERM, so a
    # repeated TERM arrives while bounded cleanup is still running.
    cancel_ready = root / 'cancel-child-ready'
    cancel_result = root / 'cancel-result.json'
    cancel_script = root / 'cancel-worker.py'
    code = ('import os,signal,time;from pathlib import Path;'
            'signal.signal(signal.SIGTERM,signal.SIG_IGN);'
            f'Path({str(cancel_ready)!r}).write_text(str(os.getpid()));time.sleep(5)')
    cancel_script.write_text(
        'import importlib.util,json,os,signal,sys\nfrom pathlib import Path\n'
        'sys.dont_write_bytecode=True\n'
        f'spec=importlib.util.spec_from_file_location("own_launcher",{str(SOURCE)!r})\n'
        'm=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)\n'
        'saved=signal.getsignal(signal.SIGTERM)\n'
        f'with Path({str(OUTPUT / "cancel-child.log")!r}).open("xb") as log:\n'
        f' r=m.monitor_owned_command([sys.executable,"-c",{code!r}],Path({str(root)!r}),dict(os.environ),log,lambda:10**12,minimum_free=1,interval=0.01,term_seconds=0.4,kill_seconds=2)\n'
        'r["handlerRestoredObserved"]=signal.getsignal(signal.SIGTERM)==saved\n'
        f'Path({str(cancel_result)!r}).write_text(json.dumps(r))\n'
    )
    with (OUTPUT / 'cancel-worker.log').open('xb') as log:
        worker = subprocess.Popen([sys.executable, str(cancel_script)], cwd=root,
                                  stdout=log, stderr=subprocess.STDOUT,
                                  start_new_session=True)
        try:
            deadline = time.monotonic() + 3
            while not cancel_ready.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            checked(cancel_ready.exists(), 'owned cancellation child ready')
            os.kill(worker.pid, signal.SIGTERM)
            time.sleep(0.05)
            os.kill(worker.pid, signal.SIGTERM)
            checked(worker.wait(timeout=5) == 0, 'SIGTERM worker finalized')
        finally:
            if worker.poll() is None:
                try:
                    os.killpg(worker.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                worker.wait(timeout=3)
    record = json.loads(cancel_result.read_text())
    checked(record['sigtermReceived'] == 2, 'repeated TERM recorded')
    checked(record['stopReason'] == 'external-signal-stop', 'TERM stop classified')
    checked(record['rawChildExitCode'] == -signal.SIGKILL, 'raw ignored-TERM child KILL retained')
    checked(record['ownedGroupCleanup']['complete'], 'external TERM child group gone')
    checked(record['temporarySigtermHandlerRestored'] and record['handlerRestoredObserved'],
            'previous TERM handler restored')
    results.append({'name': 'external-and-repeated-sigterm-finalization', 'passed': True, **record})

    evidence_error = {'rawChildExitCode': 0, 'lifecycleComplete': True,
                      'finalObservationErrors': [{'stage': 'final-log-hash', 'message': 'EXPECTED_MISSING_LOG'}]}
    launcher.finalize_status(evidence_error)
    checked(evidence_error['rawChildExitCode'] == 0 and evidence_error['launcherExitCode'] == 1,
            'raw success retained but incomplete evidence fails launcher')
    checked(evidence_error['evidenceComplete'] is False, 'missing observation not completed')
    results.append({'name': 'final-observation-error-classification', 'passed': True,
                    'observed': evidence_error})

report = {'schemaVersion': 1, 'state': 'BENIGN_HOST_PYTHON_LIFECYCLE_CHECKS_PASSED',
          'launcherSha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'checkSourceSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'checks': results, 'ownNewSessionChildrenOnly': True,
          'compilerOrNativeProducerOrGuestOrNetworkExecuted': False,
          'diskFilled': False, 'enospcSimulatedOnly': True,
          'notRuntimeCompatibilityOrBuildAcceptance': True}
(OUTPUT / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'state': report['state'], 'checks': len(results),
                  'launcherSha256': report['launcherSha256'], 'output': str(OUTPUT)}))
