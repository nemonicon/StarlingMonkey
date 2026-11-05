"""Root construction-only caller; genuine candidate and existing owned monitor."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
K = REPO / 'tests/node-compat/foundation-crypto'
SOURCE = K / 'ownership-gc-component-candidate-v1'
MONITOR = REPO / 'tests/node-compat/foundation-stream-consumers/http-host-controller-candidate-v2'


def row(path):
    raw = Path(path).read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def read(value):
    assert row(value['path']) == value
    return json.loads(Path(value['path']).read_bytes())


def family(value):
    index = read(value)
    root = Path(value['path']).parent
    names = set()
    for member in index['files']:
        name = member['path']
        assert name not in names and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name)
        assert row(root / name) == dict(member, path=str(root / name))
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'index.json'}


def write(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')
    return row(path)


def main(peers):
    assert __debug__ and sys.dont_write_bytecode
    assert not any(os.environ.get(k) for k in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH'))
    source = row(SOURCE / 'index.json')
    assert source['sha256'] == '6f0faf4b61af8fd8addffbb2948af847d2f772b401629b0fb9213ba4b2ccf0db'
    family(source)
    for name in ('sourcePeer', 'bootstrapPeer'):
        pair = peers[name]
        family(pair['index'])
        assert read(pair['result'])
        assert any(dict(member, path=str(Path(pair['index']['path']).parent / member['path'])) == pair['result'] for member in read(pair['index'])['files'])
    source_peer = read(peers['sourcePeer']['result'])
    assert source_peer['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_COMPONENT_SOURCE_REVIEW_PASSED_V1'
    assert source_peer['componentSourceIndexSha256'] == source['sha256'] and source_peer['sourceOnly'] is True
    assert source_peer['sourceReviewPassed'] is True and source_peer['ownerActionsInvoked'] is False
    bootstrap_peer = read(peers['bootstrapPeer']['result'])
    assert bootstrap_peer['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_BOOTSTRAP_REVIEW_PASSED_V1' and bootstrap_peer['verifiedPassed'] is True
    observation = row(K / 'ownership-gc-v2-bootstrap-v1-root-results.json')
    assert observation['sha256'] == '2413d02c374015c4d6391473f15fc0bc1eec802116b1af7e0cd60cd079abe29b'
    assert bootstrap_peer['bootstrapRootObservation'] == observation
    config = row(K / 'ownership-gc-v2-bootstrap-v1-root-config.json')
    assert bootstrap_peer['bootstrapConfig'] == config
    authority = read(row(SOURCE / 'future-component-authority.template.json'))
    authority.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_GC_COMPONENT_CONSTRUCTION_V1',
                     issuedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     componentSourceIndexSha256=source['sha256'], sourceIndependentReview=peers['sourcePeer'],
                     componentBuildAllowed=True, componentInitializationAllowed=True,
                     reviewedGcPins=row(K / 'reviewed-ownership-gc-v2-native-pins-v1.json'),
                     gcNativeRootReview=row(K / 'reviewed-ownership-gc-v2-native-pin-root-review-v1.json'),
                     gcBootstrapConfig=config, actualBootstrapObservation=observation, actualBootstrapReview=peers['bootstrapPeer'],
                     scope='Whole GC guest component construction and initialization only; no ordinary/key/GC-pressure export calls')
    output = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-component-v1-external-root')
    assert not output.exists() and not Path(authority['outputRoot']).exists()
    monitor_index = row(MONITOR / 'index.json')
    assert monitor_index['sha256'] == '71b7f8e54ae2e21d6673d054a20efa7b1e00409d22d8af7c5b064ad9a6380ddf'
    family(monitor_index)
    authority.update(externalController=row(Path(__file__).resolve()), externalMonitorIndex=monitor_index,
                     externalMonitorEntry=row(MONITOR / 'controller.py'), externalParentDeadlineSeconds=2400,
                     externalOutputRoot=str(output))
    authority_row = write(K / 'ownership-gc-component-v1-root-authority.json', authority)
    root_config = dict(schemaVersion=1, componentSourceIndexSha256=source['sha256'], rootAction=authority_row)
    config_row = write(K / 'ownership-gc-component-v1-root-config.json', root_config)
    prerequisite = read(row(SOURCE / 'prerequisites.json'))
    packaging = read(prerequisite['packagingMap'])
    assert row(prerequisite['node']['path']) == prerequisite['node']
    environment = {k: v for k, v in os.environ.items() if not k.startswith(('NODE_COMPAT_', 'NAPI_RS_'))}
    environment.update(PYTHONDONTWRITEBYTECODE='1', BINARYEN_CORES='1', RAYON_NUM_THREADS='1', CARGO_BUILD_JOBS='1',
                       NODE_COMPAT_TOOLCHAIN=packaging['toolchainRoot'],
                       NODE_COMPAT_COMPONENTIZE_MODULE=packaging['packagerRoot'] + '/src/componentize.js')
    spec = importlib.util.spec_from_file_location('genuine_gc_component_owned_monitor', MONITOR / 'controller.py')
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    output.mkdir(mode=0o700)
    argv = [prerequisite['node']['path'], str(SOURCE / 'build.mjs'), json.dumps(config_row, separators=(',', ':'))]
    terminal = monitor.monitor(argv, str(REPO), environment, output, 2400, authority_row)
    assert read(authority_row) == authority and read(config_row) == root_config
    assert terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] is True
    assert terminal['remainingObservedPids'] == terminal['errors'] == terminal['interruptedSignals'] == []
    assert terminal['timeout'] is False and terminal['forcedCleanup'] is False
    print(json.dumps(terminal), flush=True)


if __name__ == '__main__':
    assert len(sys.argv) == 2
    main(json.loads(sys.argv[1]))
