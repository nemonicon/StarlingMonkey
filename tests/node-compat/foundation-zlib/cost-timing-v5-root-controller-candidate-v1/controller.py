"""Dormant timing-only Root caller; standard bootstrap before custom imports."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import stat
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def row(path):
    path = Path(path)
    assert path.is_absolute() and not path.is_symlink() and path.is_file()
    before = path.stat()
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    after = path.stat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    assert identity(before) == identity(after)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=after.st_size)


def read(value):
    captured = {k: value[k] for k in ['path', 'sha256', 'bytes']}
    assert row(captured['path']) == captured and captured['bytes'] <= 64 * 1024 * 1024
    raw = Path(captured['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == captured['sha256'] and len(raw) == captured['bytes']
    return json.loads(raw)


def family(value):
    index = read(value)
    root, names = Path(value['path']).parent, {'index.json'}
    assert root == HERE or root.parent == HERE.parent
    assert index['schemaVersion'] == 1 and 0 < len(index['files']) <= 1024
    for item in index['files']:
        name = item['path']
        assert name not in names and name and not name.startswith('/') and '\\' not in name and '\0' not in name and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name)
        assert row(root / name) == dict(item, path=str(root / name))
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names
    return index


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    return row(path)


def bootstrap(config_row):
    config = read(config_row)
    own = config['controllerSourceIndex']
    assert own['path'] == str(HERE / 'index.json')
    family(own)
    peer = config['controllerIndependentReview']
    index = family(peer['index'])
    result = read(peer['result'])
    member = dict(peer['result'], path=Path(peer['result']['path']).relative_to(Path(peer['index']['path']).parent).as_posix())
    assert index['files'].count(member) == 1
    assert result['schemaVersion'] == 1 and result['state'] == 'INDEPENDENT_ZLIB_COST_TIMING_V5_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert result['controllerSourceIndexSha256'] == own['sha256']
    assert result['sourceOnly'] is result['sourceReviewPassed'] is True and result['ownerActionsInvoked'] is False
    # Every own guard/model byte and the source peer authenticated before either
    # custom module executes. No sys.path/sys.modules/global path rebinding.
    spec = importlib.util.spec_from_file_location('authenticated_timing_v5_guard', HERE / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    return guard


def collect(guard, admitted, terminal, external):
    M, root, capture = guard.M, admitted['root'], admitted['capture']
    for key in ['stdout', 'stderr']:
        assert row(terminal[key]['path']) == terminal[key]
    write(external / 'raw-terminal-observed.json', dict(schemaVersion=1, terminal=row(external / 'terminal.json'), stdout=terminal['stdout'], stderr=terminal['stderr'], interpretationPending=True))
    M.clean_terminal(terminal)
    M.need(terminal['authority'] == admitted['rootRow'] and terminal['stderr']['bytes'] == 0, 'actual clean authority-bound terminal and empty stderr')
    prefixes, published = M.publication_lines(Path(terminal['stdout']['path']).read_bytes())
    output = Path(M.TIMING_OUT)
    absolute = {key: dict(value, path=str(output / value['path'])) for key, value in published.items()}
    index = capture.read(absolute['index'])
    completion = capture.read(absolute['completion'])
    M.need(index['schemaVersion'] == 1 and len(index['files']) == 17642, 'all original360 workers full output index, no subset')
    names = set()
    for value in index['files']:
        name = guard.local(value['path'])
        M.need(name not in names, 'unique complete timing output member')
        names.add(name)
        capture.file(dict(value, path=str(output / name)))
    guard.exact_tree(output, names | {'index.json', 'completion.json'})
    capture.families.append((output, names | {'index.json', 'completion.json'}))
    M.need(completion['state'] == 'CODEC_PHASE_COMPLETE_EXTERNAL_PARENT_ZERO_AND_REVIEW_REQUIRED_V1' and completion['sourceIndexSha256'] == M.SOURCE_SHA and completion['index'] == published['index'], 'original relative completion/source binding')
    result_row = dict(completion['result'], path=str(output / guard.local(completion['result']['path'])))
    M.need(index['files'].count(completion['result']) == 1, 'result indexed once')
    result = capture.read(result_row)
    M.need(result['schemaVersion'] == 1 and result['state'] == 'CODEC_COST_PHASE_COMPLETE_UNREVIEWED_EXTERNAL_ZERO_AND_INDEPENDENT_REVIEW_REQUIRED_V1' and result['phase'] == 'timing' and result['sourceIndexSha256'] == M.SOURCE_SHA, 'genuine new timing record, still unreviewed')
    M.need(result['actualWorkers'] == 360 and result['codecBatchCalls'] == 3600 and result['rawN1ControlOperations'] == 2160 and result['calibrations'] == [], 'unchanged full schedule/no new pilot')
    M.need(result['calibrationSourceIndex'] == admitted['refs']['originalCalibrationSource'] and result['actualCalibrationReview'] == admitted['refs']['pilotReview'] and result['actualMatchedPlan'] == admitted['refs']['matchedPlan'], 'original B5 provenance unchanged')
    M.need(result['rootAuthority'] == admitted['rootRow'] and result['sourceRecheckPassed'] is result['allOwnedWorkersRawZeroClean'] is True, 'actual parent source/worker observations')
    M.need(result['controlsSubtracted'] is result['metadataProjection'] is result['operationalAdmission'] is result['runtimeAcceptanceClaim'] is result['timingAcceptanceClaim'] is False, 'no acceptance/projection/subtraction')
    M.need({r['jobId'] for r in result['origins']} == M.timing_jobs() and len(result['origins']) == len(result['observations']) == 360 and len({r['pid'] for r in result['origins']}) == 360, 'all360 fresh named workers')
    return dict(originalJsonlHeartbeatRecords=prefixes, originalRelativePublishedRows=published, absoluteOutputDescriptors=absolute, actualResult=result_row, indexedOutputFiles=17642, actualTimingWorkers=360, independentFullRawTimingReviewRequired=True)


def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and len(sys.argv) == 2
    config_row = json.loads(sys.argv[1])
    guard = bootstrap(config_row)
    admitted = guard.authorize(config_row, time.time_ns() // 1000000)
    M = guard.M
    output, external = Path(M.TIMING_OUT), Path(M.EXTERNAL_OUT)
    assert not output.exists() and not output.is_symlink() and not external.exists() and not external.is_symlink()
    available = os.statvfs('/private/tmp/starling-node-compat')
    M.need(available.f_bavail * available.f_frsize >= 2 * 1024 ** 3, '2GiB launch disk floor; V5 retains800MiB periodic stop')
    M.scopes(admitted['root'], admitted['phase'], admitted['quiet'], admitted['refs'], time.time_ns() // 1000000)
    # Generic actual monitor API, authenticated in its real original source
    # context. Its HTTP/GC-specific main/authorize functions are never called.
    spec = importlib.util.spec_from_file_location('genuine_0af_timing_owned_monitor', admitted['refs']['monitorEntry']['path'])
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    admitted['capture'].recheck()
    external.mkdir(mode=0o700)
    identity = external.stat()
    env = M.environment(dict(os.environ))
    terminal, observed, errors, post_audit = None, None, [], False
    try:
        argv = [admitted['refs']['node']['path'], admitted['refs']['entry']['path'], json.dumps(admitted['runRow'], separators=(',', ':'))]
        terminal = monitor.monitor(argv, str(REPO), env, external, 7200, admitted['rootRow'])
        observed = collect(guard, admitted, terminal, external)
    except BaseException as error:
        errors.append(dict(stage='controller-or-collection', type=type(error).__name__, rawEvidenceLocationsUnchanged=True, evidenceCompletenessRequiresActualFileVerification=True))
    finally:
        try:
            admitted['capture'].recheck()
            post_audit = True
        except BaseException as error:
            errors.append(dict(stage='final-or-failure-source-protection', type=type(error).__name__))
    actual = external.lstat()
    M.need(not external.is_symlink() and stat.S_ISDIR(actual.st_mode) and stat.S_IMODE(actual.st_mode) == 0o700 and (actual.st_dev, actual.st_ino) == (identity.st_dev, identity.st_ino), 'same owned private external root before report')
    success = observed is not None and post_audit and errors == []
    report = dict(schemaVersion=1, state='ROOT_OBSERVED_ZLIB_COST_TIMING_V5_COMPLETE_UNREVIEWED_V1' if success else 'ROOT_OBSERVED_ZLIB_COST_TIMING_V5_FAILED_UNACCEPTED_V1', controllerSourceIndex=read(config_row)['controllerSourceIndex'], sourceIndex=admitted['refs']['sourceIndex'], config=admitted['configRow'], rootAuthority=admitted['rootRow'], rawExternalTerminal=None if terminal is None else row(external / 'terminal.json'), rawExternalStdout=None if terminal is None else terminal['stdout'], rawExternalStderr=None if terminal is None else terminal['stderr'], observation=observed, errors=errors, finalSourceAndOriginalInputProtectionPassed=post_audit, independentTimingResultsReview=None, timingAcceptanceClaim=False, operationalAdmission=False, runtimeAcceptanceClaim=False, sourcePromotionAllowed=False)
    report_row = write(external / 'controller-observation.json', report)
    print(json.dumps(dict(observation=report_row, actualParentExitCode=None if terminal is None else terminal['rawExitCode'], completeUnreviewed=success)), flush=True)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
