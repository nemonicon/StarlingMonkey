"""Fresh v5 read-only plan DATA action; never launches a codec worker or pilot."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

Z = Path(__file__).resolve().parent
REPO = Z.parents[2]
SOURCE = Z / 'cost-pilot-timing-candidate-v5'
SOURCE_SHA = 'e799350100bb3b54148fdc5bd46a857579a6aae7608890f620569ea3704ab321'
MONITOR = Z.parent / 'foundation-crypto/ownership-gc-build-controller-candidate-v1'
OUT = Path('/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v5-external-root')
PLAN = Path('/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v5')


def row(path):
    path = Path(path)
    assert not any(p.is_symlink() for p in [path, *path.parents])
    before = path.stat(); h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=after.st_size)


def family(descriptor):
    assert row(descriptor['path']) == descriptor
    root = Path(descriptor['path']).parent
    value = json.loads(Path(descriptor['path']).read_bytes())
    names = {'index.json'}
    for item in value['files']:
        name = item['path']
        assert name not in names and name and not name.startswith('/') and '\\' not in name and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name)
        assert row(root / name) == dict(item, path=str(root / name))
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names
    return value


def write(name, value):
    path = Z / ('cost-measurement-plan-v5-root-' + name + '.json')
    with path.open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    return row(path)


def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and len(sys.argv) == 2
    own = row(SOURCE / 'index.json')
    assert own['sha256'] == SOURCE_SHA and own['bytes'] == 12411
    family(own)
    peer = json.loads(sys.argv[1])
    peer_index = family(peer['index'])
    result_path = Path(peer['result']['path'])
    assert dict(peer['result'], path=result_path.relative_to(Path(peer['index']['path']).parent).as_posix()) in peer_index['files']
    assert row(result_path) == peer['result']
    proof = json.loads(result_path.read_bytes())
    assert proof['schemaVersion'] == 1 and proof['state'] == 'INDEPENDENT_ZLIB_COST_PILOT_TIMING_SOURCE_REVIEW_PASSED_V1' and proof['sourceIndexSha256'] == SOURCE_SHA
    assert proof['sourceOnly'] is proof['sourceReviewPassed'] is True and proof['ownerActionsInvoked'] is False
    assert not OUT.exists() and not PLAN.exists()
    refs = json.loads((SOURCE / 'references.json').read_bytes())
    assert row(refs['node']['path']) == refs['node']
    monitor_index = row(MONITOR / 'index.json')
    assert monitor_index['sha256'] == '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b'
    family(monitor_index)
    authority = json.loads((SOURCE / 'future-plan-authority.template.json').read_bytes())
    authority.update(sourceIndexSha256=SOURCE_SHA, sourceIndependentReview=peer, dataPublicationAllowed=True, externalController=row(Path(__file__).resolve()), externalInvocation=row(Z / 'cost-measurement-plan-v5-root-invoke.mjs'), externalParentDeadlineSeconds=900, externalOutputRoot=str(OUT))
    root_row = write('authority', authority)
    options_row = write('options', dict(sourceIndex=own, sourceIndependentReview=peer, planAuthority=root_row))
    spec = importlib.util.spec_from_file_location('genuine_v5_readonly_plan_owned_monitor', MONITOR / 'monitor.py')
    monitor = importlib.util.module_from_spec(spec); spec.loader.exec_module(monitor)
    blocked = ['PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH', 'DYLD_INSERT_LIBRARIES', 'DYLD_LIBRARY_PATH', 'LD_PRELOAD', 'LD_LIBRARY_PATH']
    environment = {k: v for k, v in os.environ.items() if not k.startswith(('NODE_COMPAT_', 'NAPI_RS_')) and k not in blocked}
    environment.update(PYTHONDONTWRITEBYTECODE='1', BINARYEN_CORES='1', RAYON_NUM_THREADS='1', CARGO_BUILD_JOBS='1', NODE_COMPAT_TOOLCHAIN='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/toolchain', NODE_COMPAT_COMPONENTIZE_MODULE='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/packager/src/componentize.js')
    OUT.mkdir(mode=0o700)
    terminal = monitor.monitor([refs['node']['path'], str(Z / 'cost-measurement-plan-v5-root-invoke.mjs'), json.dumps(options_row, separators=(',', ':'))], str(REPO), environment, OUT, 900, root_row)
    errors, published, absolute = [], None, {}
    clean = terminal['allObservedOwnedGroupsGone'] is True and terminal['timeout'] is terminal['forcedCleanup'] is False and all(terminal[k] == [] for k in ['remainingObservedPids', 'errors', 'signals', 'interruptedSignals'])
    try:
        assert terminal['rawExitCode'] == 0 and clean and terminal['stderr']['bytes'] == 0 and terminal['authority'] == root_row
        for key in ['stdout', 'stderr']:
            assert row(terminal[key]['path']) == terminal[key]
        records = [json.loads(line) for line in Path(terminal['stdout']['path']).read_bytes().splitlines()]
        assert len(records) == 1
        published = records[0]
        expected = dict(result='prepared-plan.json', index='index.json', completion='completion.json')
        assert set(published) == set(expected)
        for kind, name in expected.items():
            value = published[kind]
            assert set(value) == {'path', 'sha256', 'bytes'} and value['path'] == name
            absolute[kind] = dict(value, path=str(PLAN / name))
            assert row(PLAN / name) == absolute[kind]
        assert {p.name for p in PLAN.iterdir()} == set(expected.values())
        plan = json.loads((PLAN / 'prepared-plan.json').read_bytes())
        index = json.loads((PLAN / 'index.json').read_bytes())
        completion = json.loads((PLAN / 'completion.json').read_bytes())
        assert index == dict(schemaVersion=1, files=[published['result']])
        assert completion['result'] == published['result'] and completion['index'] == published['index'] and completion['rootAuthority'] == root_row
        assert plan['state'] == 'PREPARED_COMPACT_CODEC_MEASUREMENT_PLAN_DATA_ONLY_V1' and plan['sourceIndexSha256'] == SOURCE_SHA
        assert len(plan['expected']) == 90 and set(plan['artifacts']) == {'native-on', 'fflate-on', 'fflate-off'}
        assert plan['calibrationSourceIndex']['sha256'] == 'b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1'
        assert plan['calibrationMatchedPlan']['sha256'] == 'e545f0064485d87cd1bcb919221997578b427df8499e5f8271e2e4e445ccdf3b'
        assert plan['calibrationReview'] == refs['actualCalibrationReview'] and plan['actionAuthority'] is plan['operationalAdmission'] is False
    except Exception as error:
        errors.append(dict(type=type(error).__name__, rawOutputsRetained=True))
    success = terminal['rawExitCode'] == 0 and clean and errors == []
    for value in [root_row, options_row]:
        assert row(value['path']) == value
    family(own); family(peer['index']); family(monitor_index)
    report = dict(schemaVersion=1, state='ROOT_OBSERVED_READ_ONLY_CODEC_MEASUREMENT_PLAN_V5_COMPLETE_UNREVIEWED_V1' if success else 'ROOT_OBSERVED_READ_ONLY_CODEC_MEASUREMENT_PLAN_V5_FAILURE_NO_ACCEPTANCE_V1', sourceIndex=own, sourceReview=peer, rootAuthority=root_row, rootOptions=options_row, externalTerminal=row(OUT / 'terminal.json'), externalStdout=terminal['stdout'], externalStderr=terminal['stderr'], actualReadOnlyParentExitCode=terminal['rawExitCode'], allObservedOwnedGroupsGone=clean, operationalElapsedSeconds=terminal['operationalElapsedSeconds'], originalRelativePublishedRows=published, absoluteOutputDescriptors=absolute, preparedPlan=absolute.get('result'), errors=errors, independentPlanReview=None, generatedGuestCodecWorkerPilotTimingOrSourcePromotionInvoked=False, actionAuthority=False, operationalAdmission=False, runtimeAcceptanceClaim=False)
    report_row = write('results', report)
    print(json.dumps(dict(result=report_row, rawExitCode=terminal['rawExitCode'], planDataObserved=success)), flush=True)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
