"""Root caller for the reviewed finite three-session GC runtime phase."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
K = REPO / 'tests/node-compat/foundation-crypto'
SOURCE = K / 'ownership-gc-runtime-candidate-v2'
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


def main(peer):
    assert __debug__ and sys.dont_write_bytecode
    assert not any(os.environ.get(k) for k in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH'))
    source = row(SOURCE / 'index.json')
    assert source['sha256'] == '5abe5ed812b93676bff2f09cff57099bff6d23d7ada6e5e63bbbe8152d0a0959'
    family(source)
    family(peer['index'])
    assert any(dict(r, path=str(Path(peer['index']['path']).parent / r['path'])) == peer['result'] for r in read(peer['index'])['files'])
    passed = read(peer['result'])
    assert passed['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_RUNTIME_SOURCE_REVIEW_PASSED_V2'
    assert passed['sourceIndexSha256'] == source['sha256'] and passed['sourceOnly'] is True
    assert passed['sourceReviewPassed'] is True and passed['ownerActionsInvoked'] is False
    artifact_dir = K / 'independent-ownership-gc-component-results-review-v1'
    artifact_index = row(artifact_dir / 'index.json')
    assert artifact_index['sha256'] == 'f812eeec5fc53a3b289f970add2f3d1a9a52df71462f18767baeac81b090a195'
    family(artifact_index)
    artifact_pair = dict(index=artifact_index, result=row(artifact_dir / 'results.json'))
    artifact = read(artifact_pair['result'])
    assert artifact['verifiedPassed'] is True and artifact['componentSourceIndexSha256'] == '6f0faf4b61af8fd8addffbb2948af847d2f772b401629b0fb9213ba4b2ccf0db'
    assert artifact['componentSha256'] == '52d99f4e95860b686d896c88f39b2fa5734eabeb433f48545ba814b2e45ce5f1'
    contract = row(artifact_dir / 'result-contract.json')
    assert contract['sha256'] == '4b2b689721eddb81def51361637ae1d38c7bb0bad9f0e07022f8cf54d40f4a61'
    assert read(contract)['artifacts'] == artifact['artifacts']
    root = read(row(SOURCE / 'future-root-authority.template.json'))
    root.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_GC_RUNTIME_V2', issuedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                sourceIndexSha256=source['sha256'], componentSha256=artifact['componentSha256'],
                sourceIndependentReview=peer, actualArtifactReview=artifact_pair, actualArtifactContract=contract,
                gcRuntimeAllowed=True, nodeOracleAllowed=True, publicBufferGcPressureAllowed=True, boundedKeyFixtureAllowed=True,
                scope='Three fresh finite retained/fresh/wrapper sessions; complete typed HMAC and GC schema2 returns; no OOM/reset/unsafe probes or native GC-count claim')
    external = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-runtime-v2-external-root')
    assert not external.exists() and not Path(root['outputRoot']).exists()
    monitor_index = row(MONITOR / 'index.json')
    assert monitor_index['sha256'] == '71b7f8e54ae2e21d6673d054a20efa7b1e00409d22d8af7c5b064ad9a6380ddf'
    family(monitor_index)
    root.update(externalController=row(Path(__file__).resolve()), externalMonitorIndex=monitor_index,
                externalMonitorEntry=row(MONITOR / 'controller.py'), externalParentDeadlineSeconds=2400, externalOutputRoot=str(external))
    root_row = write(K / 'ownership-gc-runtime-v2-root-authority.json', root)
    config = dict(schemaVersion=1, sourceIndexSha256=source['sha256'], rootAction=root_row)
    config_row = write(K / 'ownership-gc-runtime-v2-root-config.json', config)
    references = read(row(SOURCE / 'references.json'))
    node = references['node']
    assert row(node['path']) == node
    environment = {k: v for k, v in os.environ.items() if not k.startswith(('NODE_COMPAT_', 'NAPI_RS_'))}
    environment.update(PYTHONDONTWRITEBYTECODE='1', BINARYEN_CORES='1', RAYON_NUM_THREADS='1', CARGO_BUILD_JOBS='1')
    spec = importlib.util.spec_from_file_location('genuine_gc_runtime_owned_monitor', MONITOR / 'controller.py')
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    external.mkdir(mode=0o700)
    argv = [node['path'], str(SOURCE / 'run.mjs'), json.dumps(config_row, separators=(',', ':'))]
    terminal = monitor.monitor(argv, str(REPO), environment, external, 2400, root_row)
    assert read(root_row) == root and read(config_row) == config
    assert terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] is True
    assert terminal['remainingObservedPids'] == terminal['errors'] == terminal['interruptedSignals'] == []
    assert terminal['timeout'] is False and terminal['forcedCleanup'] is False
    print(json.dumps(terminal), flush=True)


if __name__ == '__main__':
    assert len(sys.argv) == 2
    main(json.loads(sys.argv[1]))
