"""Root-only issuer and outer observer for the reviewed clock tool build.

An issued Source-controller peer is an explicit input, never manufactured here.
"""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = HERE / 'clock-io-pruning-candidate-v1'
CONTROLLER = HERE / 'clock-io-build-controller-candidate-v1'
SOURCE_PEER = HERE / 'independent-clock-io-pruning-source-review-v1'
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
OBSERVER = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build-root-observer')
ROOTS = [Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-' + name)
         for name in ('source', 'build', 'package', 'build-external-root')]


def row(path):
    path = Path(path)
    assert path.is_absolute() and path.is_file() and not path.is_symlink()
    digest = hashlib.sha256()
    before = path.stat()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(data)
    after = path.stat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns) == (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    return dict(path=str(path),sha256=digest.hexdigest(),bytes=after.st_size)


def read(value):
    assert row(value['path']) == value
    return json.loads(Path(value['path']).read_bytes())


def family(index, sha=None):
    if sha is not None:
        assert index['sha256'] == sha
    value = read(index)
    base = Path(index['path']).parent
    names = {'index.json'}
    for item in value['files']:
        name = item['path']
        assert name not in names and not Path(name).is_absolute() and '..' not in Path(name).parts
        names.add(name)
        assert row(base/name) == dict(item,path=str(base/name))
    assert not any(path.is_symlink() for path in base.rglob('*'))
    assert {str(path.relative_to(base)) for path in base.rglob('*') if path.is_file()} == names
    return value


def save(path, value):
    with path.open('x') as stream:
        json.dump(value,stream,indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    return row(path)


def authenticate(peer):
    source = row(SOURCE/'index.json')
    controller = row(CONTROLLER/'index.json')
    family(source,'55338bc0e5e0f47ed473ccd283ed1eae70183f081abb8f6a61e5c8001711945f')
    family(controller,'064003004505c71b5cc28aef92fd929a0165d6cf3b69eb73bd935f9932dc72c8')
    source_peer = dict(index=row(SOURCE_PEER/'index.json'),result=row(SOURCE_PEER/'results.json'))
    family(source_peer['index'],'c9fa3ef3d25804b04c44747a45dbb547d4c6df39391e826e57a053474c735805')
    proof = read(source_peer['result'])
    assert proof['sourceIndexSha256'] == source['sha256'] and proof['sourceReviewPassed'] is True
    peer_index = family(peer['index'])
    assert peer['result'] in [dict(item,path=str(Path(peer['index']['path']).parent/item['path'])) for item in peer_index['files']]
    proof = read(peer['result'])
    assert proof['schemaVersion'] == 1 and proof['state'] == 'INDEPENDENT_CLOCK_IO_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert proof['controllerSourceIndexSha256'] == controller['sha256'] and proof['sourceIndexSha256'] == source['sha256']
    assert proof['sourceOnly'] is proof['sourceReviewPassed'] is True
    for name in ('ownerActionsInvoked','hostActionsInvoked','buildActionsInvoked'):
        assert proof[name] is False
    monitor = row(MONITOR/'index.json')
    family(monitor,'0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
    return source,controller,source_peer


def issue(peer):
    source,controller,source_peer = authenticate(peer)
    for path in [*ROOTS,OBSERVER]:
        assert not path.exists() and not path.is_symlink()
    root = read(row(CONTROLLER/'future-root-authority.template.json'))
    assert root['state'] is root['phase'] is root['controllerIndex'] is None
    root.update(state='ROOT_REVIEWED_CLOCK_IO_TOOLS_BUILD_V1',phase='build-clock-io-tools',
                sourceIndex=source,controllerIndex=controller,controllerEntry=row(CONTROLLER/'controller.py'),
                sourceReview=source_peer,controllerReview=peer,rootOuterController=row(Path(__file__).resolve()),
                rootOuterDeadlineSeconds=7200,rootObserverOutput=str(OBSERVER),
                issuedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    allowed = {'stageAllowed','privateVendorAllowed','downloadThreeLockedArchivesAllowed','rustBuildAndUnitTestsAllowed',
               'jcoToolPackagingAllowed','prunerRefusalUnitTestAllowed'}
    for key in list(root):
        if key.endswith('Allowed') or key in ('operationalAdmission','runtimeAcceptanceClaim'):
            assert root[key] is None
            root[key] = key in allowed
    authority = save(HERE/'clock-io-tools-build-v1-root-authority.json',root)
    config = read(row(CONTROLLER/'future-config.template.json'))
    config.update(state='CLOCK_IO_BUILD_CONTROLLER_CONFIG_V1',controllerIndex=controller,rootAuthority=authority)
    print(json.dumps(save(HERE/'clock-io-tools-build-v1-root-config.json',config)))


def run(config_descriptor):
    config = read(config_descriptor)
    authority = read(config['rootAuthority'])
    source,controller,source_peer = authenticate(authority['controllerReview'])
    assert authority['rootOuterController'] == row(Path(__file__).resolve())
    assert config['controllerIndex'] == controller and authority['sourceReview'] == source_peer
    for path in [*ROOTS,OBSERVER]:
        assert not path.exists() and not path.is_symlink()
    context = read(row(CONTROLLER/'host-context.json'))
    assert row(context['python']['path']) == context['python']
    spec = importlib.util.spec_from_file_location('genuine_original_clock_tools_root_monitor',MONITOR/'monitor.py')
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    os.umask(0o077)
    OBSERVER.mkdir(mode=0o700)
    argv = [context['python']['path'],'-B','-I',str(CONTROLLER/'controller.py'),'parent',json.dumps(config_descriptor,separators=(',',':'))]
    terminal = monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OBSERVER,7200,config['rootAuthority'])
    assert read(row(OBSERVER/'terminal.json')) == terminal
    authenticate(authority['controllerReview'])
    for key in ('stdout','stderr'):
        assert row(terminal[key]['path']) == terminal[key]
    clean = (terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] is True
        and terminal['parentOwnedGroupGone'] is True and terminal['timeout'] is terminal['forcedCleanup'] is False
        and terminal['signals'] == [] and terminal['errors'] == [] and terminal['interruptedSignals'] == []
        and terminal['remainingObservedPids'] == [])
    value = dict(schemaVersion=1,state='ROOT_OBSERVED_CLOCK_IO_TOOL_BUILD_PARENT_ZERO_UNREVIEWED_V1' if clean else 'ROOT_OBSERVED_CLOCK_IO_TOOL_BUILD_FAILED_UNACCEPTED_V1',
        sourceIndex=source,controllerIndex=controller,rootAuthority=config['rootAuthority'],config=config_descriptor,
        terminal=row(OBSERVER/'terminal.json'),stdout=terminal['stdout'],stderr=terminal['stderr'],rawParentExitCode=terminal['rawExitCode'],
        allObservedOwnedGroupsGone=terminal['allObservedOwnedGroupsGone'],cleanOwnedCleanup=clean,independentArtifactReview=None,
        validAdapterPruningRun=False,adapterPublished=False,applicationEngineOrGuestExecuted=False,
        operationalAdmission=False,runtimeAcceptanceClaim=False)
    print(json.dumps(save(OBSERVER/'root-observation.json',value)))
    return 0 if clean else 1


if __name__ == '__main__':
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    assert len(sys.argv) == 3 and sys.argv[1] in ('issue','run')
    if sys.argv[1] == 'issue':
        issue(json.loads(sys.argv[2]))
    else:
        raise SystemExit(run(json.loads(sys.argv[2])))
