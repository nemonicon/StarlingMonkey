"""Root host-only caller for three reviewed literal stock-Wasmtime exports."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
K = REPO / 'tests/node-compat/foundation-crypto'
SOURCE = K / 'ownership-gc-wasmtime-candidate-v1'
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


def main():
    assert __debug__ and sys.dont_write_bytecode
    blocked = ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH', 'JCO_DEBUG',
               'DYLD_INSERT_LIBRARIES', 'DYLD_LIBRARY_PATH', 'RUST_LOG', 'RUST_BACKTRACE')
    assert not any(os.environ.get(k) for k in blocked)
    assert not any(k.startswith('WASMTIME_') for k in os.environ)
    source = row(SOURCE / 'index.json')
    assert source['sha256'] == 'c5d3ea491e81db5fad6c02e244bcc0cf784c8135a6ab1d5e552326f4f2e1ec35'
    family(source)
    peer_dir = K / 'independent-ownership-gc-wasmtime-source-review-v1'
    peer_index = row(peer_dir / 'index.json')
    assert peer_index['sha256'] == '486ddaa96c8a087f3ae1bd9a35622d67c005bbd3a1f2ca3a04b7cb9dec3f556a'
    family(peer_index)
    peer = dict(index=peer_index, result=row(peer_dir / 'results.json'))
    passed = read(peer['result'])
    assert passed['sourceIndexSha256'] == source['sha256'] and passed['sourceReviewPassed'] is True and passed['ownerActionsInvoked'] is False
    jco_dir = K / 'independent-ownership-gc-runtime-v2-results-review-v1'
    jco_index = row(jco_dir / 'index.json')
    assert jco_index['sha256'] == '35218a210caca4fc6c832e40c08e532cd8e8f6c46c29e9ca6d702ed61f687828'
    family(jco_index)
    jco = dict(index=jco_index, result=row(jco_dir / 'results.json'))
    jco_result = read(jco['result'])
    assert jco_result['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_RUNTIME_RESULTS_REVIEW_PASSED_V2' and jco_result['verifiedPassed'] is True
    contract = row(jco_dir / 'result-contract.json')
    assert contract['sha256'] == '0388578bc602c5638cbe7aae9c72ffd19cd28e956a514a8584e1100882a730a5'
    assert read(contract)['requiredCoverage'] == jco_result['coverage']
    root = read(row(SOURCE / 'future-root-authority.template.json'))
    root.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_GC_STOCK_WASMTIME_V1',
                issuedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(), sourceIndexSha256=source['sha256'],
                wasmtimeValidateAllowed=True, publicBufferGcPressureAllowed=True, boundedKeyFixtureAllowed=True,
                sourceIndependentReview=peer, jcoGcReview=jco, jcoGcContract=contract,
                externalController=row(Path(__file__).resolve()),
                scope='Three fresh stock Wasmtime42 validate() calls; whole actual GC Jco wrapper equality and typed records; no new algorithm, reset, OOM, reuse or performance claim')
    external = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-wasmtime-v1-external-root')
    assert not external.exists() and not Path(root['outputRoot']).exists()
    monitor_index = row(MONITOR / 'index.json')
    assert monitor_index['sha256'] == '71b7f8e54ae2e21d6673d054a20efa7b1e00409d22d8af7c5b064ad9a6380ddf'
    family(monitor_index)
    root.update(externalMonitorIndex=monitor_index, externalMonitorEntry=row(MONITOR / 'controller.py'), externalOutputRoot=str(external))
    root_row = write(K / 'ownership-gc-wasmtime-v1-root-authority.json', root)
    config = dict(schemaVersion=1, sourceIndexSha256=source['sha256'], rootAction=root_row)
    config_row = write(K / 'ownership-gc-wasmtime-v1-root-config.json', config)
    refs = read(row(SOURCE / 'references.json'))
    assert row(refs['node']['path']) == refs['node'] and row(refs['wasmtime']['path']) == refs['wasmtime']
    environment = {k: v for k, v in os.environ.items() if not k.startswith(('NODE_COMPAT_', 'NAPI_RS_'))}
    environment.update(PYTHONDONTWRITEBYTECODE='1', BINARYEN_CORES='1', RAYON_NUM_THREADS='1', CARGO_BUILD_JOBS='1')
    spec = importlib.util.spec_from_file_location('genuine_gc_wt_owned_monitor', MONITOR / 'controller.py')
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    external.mkdir(mode=0o700)
    argv = [refs['node']['path'], str(SOURCE / 'run.mjs'), json.dumps(config_row, separators=(',', ':'))]
    terminal = monitor.monitor(argv, str(REPO), environment, external, 2400, root_row)
    assert read(root_row) == root and read(config_row) == config
    assert terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] is True
    assert terminal['remainingObservedPids'] == terminal['errors'] == terminal['interruptedSignals'] == []
    assert terminal['timeout'] is False and terminal['forcedCleanup'] is False
    print(json.dumps(terminal), flush=True)


if __name__ == '__main__':
    main()
