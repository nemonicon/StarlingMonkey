"""Root v2 issuer/outer observer; original0af monitor, unchanged selector342 freeze."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = HERE / 'task-selection-freezer-candidate-v1'
PEER = HERE / 'independent-task-selection-freezer-source-review-v1'
MONITOR = HERE.parent / 'foundation-crypto/ownership-gc-build-controller-candidate-v1'
FREEZE = Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze')
EXTERNAL = Path(str(FREEZE) + '-external-root')
OBSERVER = Path(str(FREEZE) + '-root-observer-v2')


def row(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(data)
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=path.stat().st_size)


def read(descriptor):
    assert row(descriptor['path']) == descriptor
    return json.loads(Path(descriptor['path']).read_bytes())


def family(path, sha):
    descriptor = row(path)
    assert descriptor['sha256'] == sha
    value = read(descriptor)
    names = {'index.json'}
    for item in value['files']:
        assert not Path(item['path']).is_absolute() and '..' not in Path(item['path']).parts
        assert item['path'] not in names
        names.add(item['path'])
        assert row(path.parent / item['path']) == dict(item, path=str(path.parent / item['path']))
    assert {str(p.relative_to(path.parent)) for p in path.parent.rglob('*') if p.is_file()} == names
    return descriptor


def authenticate():
    family(MONITOR / 'index.json', '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
    source = family(SOURCE / 'index.json', '83c07efa19f56c0ad725212bf63dfac4b70ca1ed225b7737174e7357f15737e8')
    peer = family(PEER / 'index.json', '6c2af2c76f7669fe3f4d5b7c8b1bf231d02b228d0c2b43ae91cc454b2eb5b6eb')
    result = read(row(PEER / 'results.json'))
    assert result['state'] == 'INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1'
    assert result['freezerSourceIndexSha256'] == source['sha256'] and result['sourceOnly'] is result['sourceReviewPassed'] is True
    for key in ('ownerActionsInvoked', 'hostActionsInvoked', 'nativeFreezeActionsInvoked'):
        assert result[key] is False
    return source, dict(index=peer, result=row(PEER / 'results.json'))


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    return row(path)


def issue():
    source, peer = authenticate()
    for root in (FREEZE, EXTERNAL, OBSERVER):
        assert not root.exists() and not root.is_symlink()
    root = read(row(SOURCE / 'future-root-authority.template.json'))
    assert root['phase'] is root['freezeAllowed'] is root['readOnlySourceAdmissionAllowed'] is root['postBuildNinjaCommandsAllowed'] is None
    root.update(state='ROOT_REVIEWED_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FREEZE_V1', phase='freeze',
                freezerIndex=source, entry=row(SOURCE / 'entry.py'), sourceIndependentReview=peer,
                freezeAllowed=True, readOnlySourceAdmissionAllowed=True, postBuildNinjaCommandsAllowed=True,
                rootOuterController=row(Path(__file__).resolve()), rootOuterDeadlineSeconds=3000,
                rootObserverOutput=str(OBSERVER), rootOuterMonitor=row(MONITOR / 'monitor.py'), priorRootObserverPreconditionFailure='task-selection-freeze-root-observer-failure-v1/terminal.json', issuedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    authority = save(HERE / 'task-selection-normal-off-freeze-v2-root-authority.json', root)
    config = read(row(SOURCE / 'future-config.template.json'))
    config.update(freezerIndex=source, rootAuthority=authority)
    print(json.dumps(save(HERE / 'task-selection-normal-off-freeze-v2-root-config.json', config)))


def run(config_descriptor):
    source, peer = authenticate()
    config = read(config_descriptor)
    root = read(config['rootAuthority'])
    assert root['rootOuterController'] == row(Path(__file__).resolve())
    assert root['sourceIndependentReview'] == peer and config['freezerIndex'] == source
    for path in (FREEZE, EXTERNAL, OBSERVER):
        assert not path.exists() and not path.is_symlink()
    refs = read(row(SOURCE / 'references.json'))
    assert row(refs['python']['path']) == refs['python']
    spec = importlib.util.spec_from_file_location('genuine_selector342_freeze_monitor_outer', MONITOR / 'monitor.py')
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    os.umask(0o077)
    OBSERVER.mkdir(mode=0o700)
    argv = [refs['python']['path'], '-B', '-I', str(SOURCE / 'entry.py'), 'parent', json.dumps(config_descriptor, separators=(',', ':'))]
    terminal = monitor.monitor(argv, str(REPO), {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, OBSERVER, 3000, config['rootAuthority'])
    assert read(row(OBSERVER / 'terminal.json')) == terminal
    authenticate()
    for key in ('stdout', 'stderr'):
        assert row(terminal[key]['path']) == terminal[key]
    clean = (terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] is True
             and terminal['parentOwnedGroupGone'] is True and terminal['timeout'] is False
             and terminal['forcedCleanup'] is False and terminal['signals'] == []
             and terminal['errors'] == [] and terminal['interruptedSignals'] == []
             and terminal['remainingObservedPids'] == [])
    result = dict(schemaVersion=1, state='ROOT_OBSERVED_SELECTOR342_FREEZE_PARENT_ZERO_UNREVIEWED_V1' if clean else 'ROOT_OBSERVED_SELECTOR342_FREEZE_FAILED_UNACCEPTED_V1',
        sourceIndex=source, sourceReview=peer, rootAuthority=config['rootAuthority'], config=config_descriptor,
        rawParentTerminal=row(OBSERVER / 'terminal.json'), rawParentStdout=terminal['stdout'], rawParentStderr=terminal['stderr'],
        rawParentExitCode=terminal['rawExitCode'], cleanOwnedCleanup=clean, sourceAndPeerRehashed=True,
        independentArtifactReview=None, reviewedPins=None, engineExecuted=False, operationalAdmission=False, runtimeAcceptanceClaim=False)
    print(json.dumps(save(OBSERVER / 'root-observation.json', result)))
    return 0 if clean else 1


if __name__ == '__main__':
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    if sys.argv[1:] == ['issue']:
        issue()
    else:
        assert len(sys.argv) == 3 and sys.argv[1] == 'run'
        raise SystemExit(run(json.loads(sys.argv[2])))
