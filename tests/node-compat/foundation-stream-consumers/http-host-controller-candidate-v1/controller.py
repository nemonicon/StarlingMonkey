"""Dormant bounded Root controller. Standard library only; importing launches nothing."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import signal
import subprocess
import sys
import time

REPO = Path('/Users/dan/dev/StarlingMonkey')
NODE = Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
NODE_SHA = 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'


def descriptor(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=path.stat().st_size)


def checked(row):
    path = Path(row['path'])
    assert path.is_absolute() and '..' not in path.parts
    physical = Path('/private' + str(path)) if str(path).startswith('/tmp/') else path
    for ancestor in (physical, *physical.parents):
        assert not ancestor.is_symlink()
    assert physical.is_file()
    before = physical.stat()
    actual = descriptor(path)
    after = physical.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    assert actual == {k: row[k] for k in ('path', 'sha256', 'bytes')}
    return path


def read(row):
    path = checked(row)
    assert row['bytes'] <= 32 * 1024 * 1024
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    return json.loads(raw)


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def snapshot():
    process = subprocess.run(['/bin/ps', '-axo', 'pid=,ppid=,pgid=,lstart=,comm='], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, check=True, env={**os.environ, 'LC_ALL': 'C'})
    return parse_snapshot(process.stdout.decode())


def parse_snapshot(text):
    rows = {}
    for line in text.splitlines():
        fields = line.split(maxsplit=8)
        assert len(fields) == 9
        pid, ppid, pgid = map(int, fields[:3])
        assert pid > 0 and ppid >= 0 and pgid >= 0
        rows[pid] = dict(pid=pid, ppid=ppid, pgid=pgid, birth=' '.join(fields[3:8]), command=fields[8])
    return rows


def identity(row):
    return row['pid'], row['pgid'], row['birth'], row['command']


def discover(rows, known, root_pid):
    added = []
    root = rows.get(root_pid)
    if root_pid not in known and root is not None:
        assert root['pgid'] == root_pid
        known[root_pid] = root
        added.append(root)
    changed = True
    while changed:
        changed = False
        for pid, row in rows.items():
            parent = rows.get(row['ppid'])
            owner = known.get(row['ppid'])
            if pid not in known and parent is not None and owner is not None and identity(parent) == identity(owner):
                known[pid] = row
                added.append(row)
                changed = True
    return added


def group_model(rows, known, root_pid):
    """Only captured new sessions or the actual Popen parent session can be signalled."""
    groups = {root_pid} | {r['pgid'] for r in known.values() if r['pid'] == r['pgid']}
    result = []
    for pgid in sorted(groups):
        members = [r for r in rows.values() if r['pgid'] == pgid]
        if not members:
            result.append(dict(pgid=pgid, alive=False, signalAllowed=False))
            continue
        matched = [r for r in members if r['pid'] in known and identity(r) == identity(known[r['pid']])]
        result.append(dict(pgid=pgid, alive=True, signalAllowed=bool(matched), matchedPids=[r['pid'] for r in matched]))
    return result


def monitor(argv, cwd, environment, output, timeout_seconds, authority, *, parent_grace_seconds=45, sample_seconds=0.2):
    """A real owned parent and observed descendants; no caller-supplied PID or group."""
    assert 0 < timeout_seconds <= 2400 and 0 < parent_grace_seconds <= 45
    assert 0 < sample_seconds <= 1 and Path(output).is_dir()
    output = Path(output)
    known, events, errors, signal_events = {}, [], [], []
    started = time.monotonic()
    interrupted = []
    old = {}
    for number in (signal.SIGTERM, signal.SIGINT):
        old[number] = signal.signal(number, lambda num, _frame: interrupted.append(num))
    child = None
    timed_out = False
    forced_cleanup = False
    try:
        with (output / 'stdout.log').open('xb') as stdout, (output / 'stderr.log').open('xb') as stderr:
            child = subprocess.Popen(argv, cwd=cwd, env=environment, stdout=stdout, stderr=stderr, start_new_session=True)
            write(output / 'started.json', dict(schemaVersion=1, pid=child.pid, argv=argv, authority=authority, timeoutSeconds=timeout_seconds, startedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
            print(json.dumps(dict(pid=child.pid, timeoutSeconds=timeout_seconds)), flush=True)

            def observe():
                rows = snapshot()
                for row in discover(rows, known, child.pid):
                    event = dict(sequence=len(events), observationMonotonicSeconds=time.monotonic(), process=row)
                    write(output / ('owned-' + str(len(events)).zfill(4) + '.json'), event)
                    events.append(event)
                return rows

            def send_owned(number, rows):
                nonlocal forced_cleanup
                for group in group_model(rows, known, child.pid):
                    if not group['alive']:
                        continue
                    if not group['signalAllowed']:
                        errors.append(dict(stage='unknown-current-group-identity', group=group))
                        continue
                    assert group['pgid'] > 1 and group['pgid'] != os.getpgrp()
                    forced_cleanup = True
                    try:
                        os.killpg(group['pgid'], number)
                        signal_events.append(dict(pgid=group['pgid'], signal=number, outcome='sent'))
                    except ProcessLookupError:
                        signal_events.append(dict(pgid=group['pgid'], signal=number, outcome='already-gone'))

            while child.poll() is None:
                observe()
                if interrupted or time.monotonic() - started >= timeout_seconds:
                    timed_out = not interrupted
                    send_owned(signal.SIGTERM, observe())
                    deadline = time.monotonic() + parent_grace_seconds
                    while child.poll() is None and time.monotonic() < deadline:
                        observe()
                        time.sleep(sample_seconds)
                    if child.poll() is None:
                        send_owned(signal.SIGKILL, observe())
                    break
                time.sleep(sample_seconds)
            child.wait(timeout=10)
            rows = observe()
            remaining = [g for g in group_model(rows, known, child.pid) if g['alive']]
            if remaining:
                send_owned(signal.SIGTERM, rows)
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline and any(g['alive'] for g in group_model(observe(), known, child.pid)):
                    time.sleep(sample_seconds)
                send_owned(signal.SIGKILL, observe())
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline and any(g['alive'] for g in group_model(observe(), known, child.pid)):
                    time.sleep(sample_seconds)
            final_groups = group_model(observe(), known, child.pid)
            for stream in (stdout, stderr):
                stream.flush()
                os.fsync(stream.fileno())
    except BaseException as error:
        errors.append(dict(stage='external-controller', name=type(error).__name__, message=str(error)[:2048]))
        if child is not None:
            # The actual Popen child is retained, never reconstructed from a PID file.
            if child.poll() is None:
                forced_cleanup = True
                child.kill()
                child.wait(timeout=10)
            try:
                send_owned(signal.SIGKILL, observe())
                time.sleep(sample_seconds)
                final_groups = group_model(observe(), known, child.pid)
            except BaseException as cleanup_error:
                errors.append(dict(stage='cleanup-observation', name=type(cleanup_error).__name__))
                final_groups = []
        else:
            final_groups = []
    finally:
        for number, handler in old.items():
            signal.signal(number, handler)
    complete = child is not None and bool(final_groups) and not any(g['alive'] for g in final_groups)
    terminal = dict(schemaVersion=1, pid=None if child is None else child.pid, rawExitCode=None if child is None else child.returncode,
        timeout=timed_out, interruptedSignals=interrupted, parentOwnedGroupGone=complete, allObservedOwnedGroupsGone=complete,
        forcedCleanup=forced_cleanup, signals=signal_events, errors=errors, finalGroups=final_groups, observedProcesses=list(known.values()),
        authority=authority, stdout=descriptor(output / 'stdout.log'), stderr=descriptor(output / 'stderr.log'),
        operationalElapsedSeconds=time.monotonic()-started, acceptanceRequiresRawZeroNoSignalsNoTimeoutAndIndependentResultReview=True)
    write(output / 'terminal.json', terminal)
    return terminal


def authorize(config_row):
    captured = [config_row]
    config = read(config_row)
    root_row = config['rootAction']
    root = read(root_row)
    captured.append(root_row)
    assert root['state'] == 'ROOT_REVIEWED_CONSUMERS355_HTTP_BOTH_HOSTS_V2'
    assert root['actionAllowed'] is True and root['hostRequestsAllowed'] is True
    assert root['variant'] == 'normal-runtime' and root['sourceFiles'] == 355
    for key in ('metadataProjection', 'operationalAdmission', 'runtimeAcceptanceClaim', 'sourcePromotionAllowed', 'wireBodyAdapterAllowed'):
        assert root[key] is False
    source_row = config['sourceIndex']
    source = read(source_row)
    assert source_row['sha256'] == root['sourceIndexSha256']
    source_dir = Path(source_row['path']).parent
    assert source_dir.parent == REPO / 'tests/node-compat/foundation-stream-consumers'
    assert source_dir.name == 'http-host-candidate-v2'
    captured.append(source_row)
    for row in source['files']:
        name = Path(row['path'])
        assert not name.is_absolute() and '..' not in name.parts
        captured.append(dict(path=str(source_dir / name), sha256=row['sha256'], bytes=row['bytes']))
    peer = root['sourceIndependentReview']
    peer_index = read(peer['index'])
    captured.append(peer['index'])
    for row in peer_index['files']:
        name = Path(row['path'])
        assert not name.is_absolute() and '..' not in name.parts
        captured.append(dict(path=str(Path(peer['index']['path']).parent / name), sha256=row['sha256'], bytes=row['bytes']))
    assert peer['result'] in captured
    result = read(peer['result'])
    assert result['state'] == 'INDEPENDENT_CONSUMERS355_HTTP_HOST_SOURCE_REVIEW_PASSED_V2'
    assert result['sourceIndexSha256'] == source_row['sha256'] and result['sourceReviewPassed'] is True and result['sourceOnly'] is True and result['ownerActionsInvoked'] is False
    controller = read(root['hostController'])
    captured.extend([root['hostController'], root['componentPhase']])
    assert controller['state'] == 'ROOT_APPROVED_CONSUMERS355_HTTP_HOST_CONTROLLER_V2'
    assert controller['entrySource'] == descriptor(Path(__file__).resolve())
    assert controller['externalParentDeadlineSeconds'] == 2400 and controller['hostExecutionAllowed'] is True
    assert controller['hostSourceIndexSha256'] == source_row['sha256'] and controller['outputRoot'] == root['outputRoot']
    assert controller['outputRoot'] == '/private/tmp/starling-node-compat/consumers355-http-both-hosts-v2'
    phase = read(root['componentPhase'])
    assert phase['state'] == 'ROOT_APPROVED_CONSUMERS355_HTTP_COMPONENT_PHASE_V2' and phase['hostExecutionAllowed'] is True
    assert phase['hostSourceIndexSha256'] == source_row['sha256'] and phase['runtimeAcceptanceClaim'] is False
    for row in captured:
        checked(row)
    checked(dict(path=str(NODE), sha256=NODE_SHA, bytes=108619024))
    return config, root, controller, captured, source_dir


def main(config_row):
    assert __debug__ and not any(os.environ.get(k) for k in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH'))
    config, root, controller, captured, source_dir = authorize(config_row)
    output = Path(controller['externalOutputRoot'])
    assert str(output) == '/private/tmp/starling-node-compat/consumers355-http-both-hosts-v2-root'
    assert not Path(root['outputRoot']).exists()
    output.mkdir(mode=0o700, exist_ok=False)
    prerequisites = read(descriptor(source_dir / 'prerequisites.json'))
    construction = read(prerequisites['constructionPrerequisites'])
    captured.append(prerequisites['constructionPrerequisites'])
    invocation = construction['invocation']
    environment = {k:v for k,v in os.environ.items() if not k.startswith(('NODE_COMPAT_', 'NAPI_RS_')) and k not in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE', 'NODE_OPTIONS', 'NODE_PATH')}
    environment.update(PYTHONDONTWRITEBYTECODE='1', BINARYEN_CORES='1', RAYON_NUM_THREADS='1', CARGO_BUILD_JOBS='1',
        NODE_COMPAT_TOOLCHAIN=invocation['toolchainRoot'], NODE_COMPAT_COMPONENTIZE_MODULE=invocation['componentizeModule'],
        NODE_COMPAT_WASMTIME=invocation['wasmtimeRealPath'], NODE_COMPAT_RELEASE_FAMILY_INDEX_SHA256=prerequisites['familyIndex']['sha256'])
    argv = [str(NODE), str(source_dir / 'run.mjs'), json.dumps(config_row, separators=(',', ':'))]
    terminal = monitor(argv, str(REPO), environment, output, 2400, config['rootAction'])
    for row in captured:
        checked(row)
    assert terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] is True and terminal['forcedCleanup'] is False and terminal['timeout'] is False and not terminal['interruptedSignals'] and not terminal['errors']
    print(json.dumps(terminal), flush=True)


if __name__ == '__main__':
    assert len(sys.argv) == 2
    main(json.loads(sys.argv[1]))
