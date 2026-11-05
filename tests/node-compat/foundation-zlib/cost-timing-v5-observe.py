"""Observe retained timing files only; no worker, helper, codec or guest rerun."""
import collections
import hashlib
import json
from pathlib import Path
import stat

Z = Path(__file__).resolve().parent
OUTPUT = Path('/private/tmp/starling-node-compat/zlib-cost-timing-v5')
EXTERNAL = Path(str(OUTPUT) + '-external-root')


def row(path):
    path = Path(path); before = path.stat(); digest = hashlib.sha256()
    assert path.is_absolute() and not any(v.is_symlink() for v in [path, *path.parents]) and stat.S_ISREG(before.st_mode)
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=after.st_size)


def main():
    assert __debug__
    controller = row(EXTERNAL / 'controller-observation.json')
    assert controller['sha256'] == 'ade1be0e2560d49dd41daf5e1b990ffccac0102552196d0c84fa3a34073239b1'
    observed = json.loads(Path(controller['path']).read_bytes())
    assert observed['state'] == 'ROOT_OBSERVED_ZLIB_COST_TIMING_V5_COMPLETE_UNREVIEWED_V1' and observed['errors'] == [] and observed['finalSourceAndOriginalInputProtectionPassed'] is True
    terminal_row = observed['rawExternalTerminal']; assert row(terminal_row['path']) == terminal_row
    terminal = json.loads(Path(terminal_row['path']).read_bytes())
    assert terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] is terminal['parentOwnedGroupGone'] is True
    assert terminal['timeout'] is terminal['forcedCleanup'] is False and all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    for key in ['stdout', 'stderr']:
        assert row(terminal[key]['path']) == terminal[key]
    assert terminal['stderr']['bytes'] == 0
    publication = observed['observation']
    originals = publication['originalRelativePublishedRows']; absolute = publication['absoluteOutputDescriptors']
    for key in ['index', 'completion']:
        assert absolute[key] == dict(originals[key], path=str(OUTPUT / originals[key]['path'])) and row(absolute[key]['path']) == absolute[key]
    index = json.loads(Path(absolute['index']['path']).read_bytes())
    completion = json.loads(Path(absolute['completion']['path']).read_bytes())
    assert completion['index'] == originals['index'] and completion['sourceIndexSha256'] == observed['sourceIndex']['sha256']
    assert len(index['files']) == 17642
    names = set(); modes = collections.Counter()
    for value in index['files']:
        name = value['path']
        assert name and not name.startswith('/') and '\\' not in name and all(part not in ('', '.', '..') for part in name.split('/')) and name not in names
        names.add(name); path = OUTPUT / name
        assert row(path) == dict(value, path=str(path)) and path.stat().st_nlink == 1
        modes[oct(stat.S_IMODE(path.stat().st_mode))] += 1
    actual = {p.relative_to(OUTPUT).as_posix() for p in OUTPUT.rglob('*') if p.is_file()}
    assert actual == names | {'index.json', 'completion.json'} and len(actual) == 17644
    assert not any(p.is_symlink() for p in OUTPUT.rglob('*'))
    assert all(stat.S_IMODE(p.stat().st_mode) == 0o700 for p in [OUTPUT, *[p for p in OUTPUT.rglob('*') if p.is_dir()]])
    result_row = dict(completion['result'], path=str(OUTPUT / completion['result']['path']))
    assert result_row == publication['actualResult'] and row(result_row['path']) == result_row
    result = json.loads(Path(result_row['path']).read_bytes())
    assert result['phase'] == 'timing' and result['actualWorkers'] == 360 and result['codecBatchCalls'] == 3600 and result['rawN1ControlOperations'] == 2160
    assert result['controlsSubtracted'] is result['metadataProjection'] is result['timingAcceptanceClaim'] is False
    assert result['calibrations'] == [] and len(result['origins']) == len(result['observations']) == 360
    assert len({r['pid'] for r in result['origins']}) == len({r['jobId'] for r in result['origins']}) == 360
    assert all(v['rawExitCode'] == 0 and v['ownedGroupGone'] is v['cleanTerminal'] is v['allRawRetained'] is v['finalSourceAuditPassed'] is True and v['warmups'] == 3 and v['samples'] == 7 for v in result['observations'])
    calls = samples = 0
    for worker in (OUTPUT / 'jobs').iterdir():
        value = json.loads((worker / 'worker-results.json').read_bytes())
        assert value['phase'] == 'timing' and len(value['records']) == 20
        assert len(value['codec']) == 10 and len(value['controls']) == 6
        calls += len(value['records']); samples += sum(r['timed'] is True for r in value['codec'])
    assert calls == 7200 and samples == 2520
    aggregate_row = row(OUTPUT / 'aggregate-observations.json')
    aggregate = json.loads(Path(aggregate_row['path']).read_bytes())
    assert aggregate['workerCount'] == 360 and aggregate['codecBatchCalls'] == 3600 and aggregate['rawN1ControlOperations'] == 2160 and aggregate['controlsSubtracted'] is False
    quiet = row(Z / 'cost-timing-v5-quiet-window-completion.json')
    assert json.loads(Path(quiet['path']).read_bytes())['taskHoldReleasedAfterThisReceipt'] is True
    report = dict(schemaVersion=1, state='ROOT_OBSERVED_CODEC_TIMING_V5_COMPLETE_UNREVIEWED_V1', sourceIndex=observed['sourceIndex'], controllerSourceIndex=observed['controllerSourceIndex'], controllerObservation=controller, rootAuthority=observed['rootAuthority'], controllerConfig=observed['config'], externalParentTerminal=terminal_row, quietWindowCompletion=quiet, actualIndex=absolute['index'], actualCompletion=absolute['completion'], actualResults=result_row, actualAggregate=aggregate_row, originalJsonlHeartbeatRecords=publication['originalJsonlHeartbeatRecords'], originalRelativePublishedRows=originals, absoluteOutputDescriptors=absolute, indexedOutputFiles=17642, actualOutputFiles=17644, indexedFileModes=dict(modes), outputDirectoriesMode='0700', allOutputFilesSingleLink=True, actualTimingWorkers=360, uniqueWorkerPids=360, codecBatchCalls=3600, rawN1ControlOperations=2160, rawPublicTypedReturns=7200, measuredSamples=2520, warmupBatches=1080, allObservedOwnedGroupsGone=True, rawParentExitCode=0, rootControllerToolSession=38214, rootControllerExitCode=0, operationalElapsedSeconds=terminal['operationalElapsedSeconds'], operationalElapsedIsPerformanceMeasurement=False, sourceAndOriginalInputProtectionPassed=True, independentTimingResultsReview=None, completeTypedFNVAndAggregateReplayByRoot=False, controlSubtraction=False, backgroundDesktopAndSystemActivityControlled=False, timingAcceptanceClaim=False, operationalAdmission=False, runtimeAcceptanceClaim=False, sourcePromotionAllowed=False)
    target = Z / 'cost-timing-v5-root-results.json'
    with target.open('x') as stream:
        json.dump(report, stream, indent=2); stream.write('\n')
    print(json.dumps(dict(result=row(target), actualIndex=absolute['index'], actualResults=result_row, actualAggregate=aggregate_row, actualWorkers=360, rawPublicTypedReturns=calls)))


if __name__ == '__main__':
    main()
