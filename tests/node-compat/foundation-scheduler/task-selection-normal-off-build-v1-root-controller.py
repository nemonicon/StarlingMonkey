"""Fresh Root native build action; generic monitoring only, no guest execution."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

S = Path(__file__).resolve().parent
REPO = S.parents[2]
SOURCE = S / 'task-selection-build-controller-candidate-v1'
PEER = S / 'independent-task-selection-build-controller-source-review-v1'
MONITOR = S.parent / 'foundation-crypto/ownership-gc-build-controller-candidate-v1'
OUT = Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-parent-external-root')


def row(path):
    path = Path(path); a = path.stat(); h = hashlib.sha256()
    assert path.is_absolute() and path.is_file() and not any(p.is_symlink() for p in [path, *path.parents])
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    b = path.stat()
    assert (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (b.st_dev, b.st_ino, b.st_size, b.st_mtime_ns, b.st_ctime_ns)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=b.st_size)


def family(root, expected):
    descriptor = row(root / 'index.json'); assert descriptor['sha256'] == expected
    index = json.loads((root / 'index.json').read_bytes()); names = {'index.json'}
    for value in index['files']:
        name = value['path']
        assert name and name not in names and not name.startswith('/') and '\\' not in name and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name); assert row(root / name) == dict(value, path=str(root / name))
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names
    return descriptor


def write(name, value):
    path = S / ('task-selection-normal-off-build-v1-root-' + name + '.json')
    with path.open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    return row(path)


def clean(terminal):
    return terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] is True and terminal['parentOwnedGroupGone'] is True and terminal['timeout'] is terminal['forcedCleanup'] is False and all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])


def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    own = family(SOURCE, 'dd69c40580cfbb8671a4e3197e65a9e7f763c96f623ee95e6d3e14aa144c980f')
    peer = dict(index=family(PEER, '17bbc355c1bb3ace3dd2ddbcfb5a69f5c7e4ae01cf25a813590293c240c2be68'), result=row(PEER / 'results.json'))
    proof = json.loads((PEER / 'results.json').read_bytes())
    assert proof['sourceReviewPassed'] is True and proof['controllerSourceIndexSha256'] == own['sha256'] and proof['nativeBuildActionsInvoked'] is False
    refs = json.loads((SOURCE / 'references.json').read_bytes())
    authority = json.loads((SOURCE / 'future-root-authority.template.json').read_bytes())
    for path in [OUT, Path(refs['workRoot']), Path(refs['freezeRoot']), Path(authority['buildOutputRoot']), Path(authority['externalOutputRoot'])]:
        assert not path.exists() and not path.is_symlink()
    authority.update(state='ROOT_REVIEWED_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_BUILD_V1', controllerIndex=own, controllerEntry=row(SOURCE / 'controller.py'), controllerIndependentReview=peer, buildAllowed=True, externalController=row(Path(__file__).resolve()), outerDeadlineSeconds=7200)
    root = write('authority', authority)
    config = json.loads((SOURCE / 'future-config.template.json').read_bytes()); config.update(controllerIndex=own, rootAuthority=root)
    config_row = write('config', config)
    monitor_index = family(MONITOR, '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
    spec = importlib.util.spec_from_file_location('genuine_selector_build_root_monitor', MONITOR / 'monitor.py')
    monitor = importlib.util.module_from_spec(spec); spec.loader.exec_module(monitor)
    blocked = ['PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH', 'DYLD_INSERT_LIBRARIES', 'DYLD_LIBRARY_PATH', 'LD_PRELOAD', 'LD_LIBRARY_PATH']
    environment = {k: v for k, v in os.environ.items() if k not in blocked}; environment['PYTHONDONTWRITEBYTECODE'] = '1'
    OUT.mkdir(mode=0o700)
    argv = [sys.executable, '-B', '-I', str(SOURCE / 'controller.py'), 'parent', json.dumps(config_row, separators=(',', ':'))]
    terminal = monitor.monitor(argv, str(REPO), environment, OUT, 7200, root)
    inner_path = Path(authority['externalOutputRoot']) / 'terminal.json'
    build_path = Path(authority['buildOutputRoot']) / 'result.json'
    inner = json.loads(inner_path.read_bytes()) if inner_path.exists() else None
    build = json.loads(build_path.read_bytes()) if build_path.exists() else None
    errors = []
    try:
        assert clean(terminal) and inner is not None and clean(inner)
        for term in [terminal, inner]:
            assert term['authority'] == root and term['stderr']['bytes'] == 0
            for key in ['stdout', 'stderr']:
                assert row(term[key]['path']) == term[key]
        records = [json.loads(line) for line in Path(terminal['stdout']['path']).read_bytes().splitlines()]
        assert records[-1] == inner
        worker = [json.loads(line) for line in Path(inner['stdout']['path']).read_bytes().splitlines()]
        assert len(worker) == 1 and worker[0]['result'] == build and worker[0]['output'] == authority['buildOutputRoot']
        assert build['state'] == 'native-build-completed-runtime-pending' and build['rawChildExitCode'] == build['launcherExitCode'] == 0
        assert build['allSourceStageAndProofBytesPreserved'] is True and build['engineExecuted'] is False
        assert build['ownedGroupCleanup']['complete'] is True and build['ownedGroupCleanup']['events'] == build['ownedGroupCleanup']['errors'] == []
        for key in ['engine', 'metadata']:
            value = build['actualMetadataObservation'][key]; assert row(value['path']) == value
        assert row(build['buildLog']['path']) == build['buildLog']
    except Exception as error:
        errors.append(dict(type=type(error).__name__, completeRawOutputsRetained=True))
    for value in [root, config_row]:
        assert row(value['path']) == value
    family(SOURCE, own['sha256']); family(PEER, peer['index']['sha256']); family(MONITOR, monitor_index['sha256'])
    success = clean(terminal) and inner is not None and clean(inner) and build is not None and errors == []
    report = dict(schemaVersion=1, state='ROOT_OBSERVED_TASK_SELECTION342_NORMAL_OFF_NATIVE_BUILD_RAW_ZERO_UNREVIEWED_V1' if success else 'ROOT_OBSERVED_TASK_SELECTION342_NORMAL_OFF_NATIVE_BUILD_FAILURE_NO_ACCEPTANCE_V1', controllerSourceIndex=own, controllerSourceReview=peer, taskSelectionSourceIndex=refs['sourceIndex'], actualStageReview=refs['actualStageReview'], rootAuthority=root, config=config_row, monitorSourceIndex=monitor_index, outerTerminal=row(OUT / 'terminal.json'), innerTerminal=row(inner_path) if inner is not None else None, actualBuildResult=row(build_path) if build is not None else None, rawOuterExitCode=terminal['rawExitCode'], rawInnerExitCode=inner['rawExitCode'] if inner else None, actualMetadataObservation=build.get('actualMetadataObservation') if build else None, buildLog=build.get('buildLog') if build else None, errors=errors, normalOffNativeBuildRawZeroObserved=success, independentBuildReviewRequired=True, freezeInvoked=False, engineExecuted=False, guestExecuted=False, operationalAdmission=False, runtimeAcceptanceClaim=False)
    result = write('results', report)
    print(json.dumps(dict(result=result, normalOffNativeBuildRawZeroObserved=success)), flush=True)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
