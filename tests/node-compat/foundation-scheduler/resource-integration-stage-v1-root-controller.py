"""Root stage-only caller using the existing reviewed owned-process monitor."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
S = REPO / 'tests/node-compat/foundation-scheduler'
SOURCE = S / 'resource-integration-candidate-v1'
MONITOR = REPO / 'tests/node-compat/foundation-stream-consumers/http-host-controller-candidate-v2'


def row(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def read(value):
    assert row(value['path']) == value
    return json.loads(Path(value['path']).read_bytes())


def family(path, digest):
    value = row(path)
    assert value['sha256'] == digest
    index = read(value)
    names = set()
    for member in index['files']:
        name = member['path']
        assert name not in names and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name)
        assert row(Path(path).parent / name) == dict(member, path=str(Path(path).parent / name))
    assert not any(p.is_symlink() for p in Path(path).parent.rglob('*'))
    assert {p.relative_to(Path(path).parent).as_posix() for p in Path(path).parent.rglob('*') if p.is_file()} == names | {'index.json'}
    return value


def write(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')
    return row(path)


def main():
    assert __debug__ and sys.dont_write_bytecode
    assert not any(os.environ.get(k) for k in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH'))
    source = family(SOURCE / 'index.json', '20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414')
    peer_index = family(S / 'independent-resource-integration-source-review-v1/index.json', '360732de527e5c1c554663c81c2d4b983a80530a6ef0c9503f93bfaaecaadd5d')
    peer = dict(index=peer_index, result=row(Path(peer_index['path']).parent / 'results.json'))
    passed = read(peer['result'])
    assert passed['sourceIndexSha256'] == source['sha256'] and passed['sourceReviewPassed'] is True and passed['ownerActionsInvoked'] is False
    monitor_index = family(MONITOR / 'index.json', '71b7f8e54ae2e21d6673d054a20efa7b1e00409d22d8af7c5b064ad9a6380ddf')
    output = Path('/private/tmp/starling-node-compat/scheduler-resource-v1-stage-external-root')
    for path in (output, Path('/private/tmp/starling-node-compat/scheduler-resource-v1-source'), Path('/private/tmp/starling-node-compat/scheduler-resource-v1-stage.json')):
        assert not path.exists() and not path.is_symlink()
    authority = dict(schemaVersion=1, state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_SOURCE_STAGE_V1',
                     issuedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(), phase='stage',
                     sourceIndexSha256=source['sha256'], sourceIndependentReview=peer,
                     sourceRoot='/private/tmp/starling-node-compat/scheduler-resource-v1-source',
                     workRoot='/private/tmp/starling-node-compat/scheduler-resource-v1-build',
                     baseline='54b3329b3ce818fd1f244e871e9c259b63667cda', nativeFiles=342, externalEmbeddingSources=3,
                     stageAllowed=True, buildAllowed=False, componentAllowed=False, guestAllowed=False,
                     runtimeAcceptanceClaim=False, sourcePromotionAllowed=False,
                     controller=row(Path(__file__).resolve()), entry=row(SOURCE / 'stage.py'),
                     externalMonitorIndex=monitor_index, externalMonitorEntry=row(MONITOR / 'controller.py'),
                     externalParentDeadlineSeconds=2400, externalOutputRoot=str(output),
                     scope='Exclusive fresh accepted342 reconstruction with exactly two reviewed ownership afterimages; no build or runtime action')
    authority_row = write(S / 'resource-integration-stage-v1-root-authority.json', authority)
    config = dict(schemaVersion=1, sourceIndex=source, rootAuthority=authority_row)
    config_row = write(S / 'resource-integration-stage-v1-root-config.json', config)
    spec = importlib.util.spec_from_file_location('genuine_resource_stage_owned_monitor', MONITOR / 'controller.py')
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    output.mkdir(mode=0o700)
    argv = [sys.executable, '-B', '-I', str(SOURCE / 'stage.py'), json.dumps(config_row, separators=(',', ':'))]
    terminal = monitor.monitor(argv, str(REPO), {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, output, 2400, authority_row)
    assert read(authority_row) == authority and read(config_row) == config
    assert terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] is True
    assert terminal['remainingObservedPids'] == terminal['errors'] == terminal['interruptedSignals'] == []
    assert terminal['timeout'] is False and terminal['forcedCleanup'] is False
    print(json.dumps(terminal), flush=True)


if __name__ == '__main__':
    main()
