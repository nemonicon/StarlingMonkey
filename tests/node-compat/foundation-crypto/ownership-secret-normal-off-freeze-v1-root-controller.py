"""Root normal-only freeze action with complete owned outer/inner observations."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

K = Path(__file__).resolve().parent
REPO = K.parents[2]
SOURCE = K / 'ownership-secret-freezer-candidate-v1'
PEER = K / 'independent-ownership-secret-freezer-source-review-v1'
MONITOR = K / 'ownership-gc-build-controller-candidate-v1'
OUT = Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze-parent-external-root')


def row(path):
    path = Path(path)
    assert not any(v.is_symlink() for v in [path, *path.parents])
    before = path.stat()
    assert stat.S_ISREG(before.st_mode)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=after.st_size)


def family(root, sha):
    descriptor = row(root / 'index.json')
    assert descriptor['sha256'] == sha
    index = json.loads((root / 'index.json').read_bytes())
    names = {'index.json'}
    for value in index['files']:
        name = value['path']
        assert name not in names and name and not name.startswith('/') and '\\' not in name and all(v not in ('', '.', '..') for v in name.split('/'))
        names.add(name)
        assert row(root / name) == dict(value, path=str(root / name))
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names
    return descriptor


def write(name, value):
    path = K / ('ownership-secret-normal-off-freeze-v1-root-' + name + '.json')
    with path.open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')
        stream.flush(); os.fsync(stream.fileno())
    return row(path)


def clean(terminal):
    return terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and terminal['timeout'] is terminal['forcedCleanup'] is False and all(terminal[k] == [] for k in ['remainingObservedPids', 'errors', 'signals', 'interruptedSignals'])


def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    source = family(SOURCE, 'd0d51496e4c17215398b47b3bb0528e967e62978c49dc689cc29378e873f2bda')
    peer = dict(index=family(PEER, 'a7be2c58fee457cfbaa710411d059a8e4024df7572a01ef660e16fa195284a75'), result=row(PEER / 'results.json'))
    proof = json.loads((PEER / 'results.json').read_bytes())
    assert proof['sourceReviewPassed'] is True and proof['sourceIndexSha256'] == source['sha256'] and proof['ownerActionsInvoked'] is False
    contract = json.loads((SOURCE / 'source-contract.json').read_bytes())
    refs = json.loads((SOURCE / 'references.json').read_bytes())
    assert not OUT.exists() and not Path(contract['freezeRoot']).exists() and not Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze-external-root').exists()
    authority = json.loads((SOURCE / 'root-authority.template.json').read_bytes())
    authority.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_NORMAL_OFF_FREEZE_V1', freezerIndex=source, entry=row(SOURCE / 'freeze.py'), commonHelper=row(SOURCE / 'artifact-tools/artifact_common.py'), independentSourceReview=peer, freezeAllowed=True, externalController=row(Path(__file__).resolve()), outerDeadlineSeconds=2700)
    root = write('authority', authority)
    config = json.loads((SOURCE / 'config.template.json').read_bytes())
    config.update(freezerIndex=source, rootAuthority=root)
    config_row = write('config', config)
    monitor_index = family(MONITOR, '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
    spec = importlib.util.spec_from_file_location('genuine_secret_freeze_outer_monitor', MONITOR / 'monitor.py')
    monitor = importlib.util.module_from_spec(spec); spec.loader.exec_module(monitor)
    blocked = ['PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH', 'DYLD_INSERT_LIBRARIES', 'DYLD_LIBRARY_PATH', 'LD_PRELOAD', 'LD_LIBRARY_PATH']
    environment = {k: v for k, v in os.environ.items() if k not in blocked}
    environment['PYTHONDONTWRITEBYTECODE'] = '1'
    OUT.mkdir(mode=0o700)
    argv = [sys.executable, '-B', '-I', str(SOURCE / 'freeze.py'), 'parent', json.dumps(config_row, separators=(',', ':'))]
    terminal = monitor.monitor(argv, str(REPO), environment, OUT, 2700, root)
    inner_path = Path(authority['externalOutputRoot']) / 'terminal.json'
    inner = json.loads(inner_path.read_bytes()) if inner_path.exists() else None
    receipt_path = Path(contract['freezeRoot']) / 'normal-off-freeze-receipt.json'
    receipt_row = row(receipt_path) if receipt_path.exists() else None
    errors, copies, originals = [], 0, 0
    receipt = None
    try:
        assert clean(terminal) and inner is not None and clean(inner)
        for term in [terminal, inner]:
            assert term['authority'] == root and term['stderr']['bytes'] == 0
            for key in ['stdout', 'stderr']:
                assert row(term[key]['path']) == term[key]
        parent_records = [json.loads(v) for v in Path(terminal['stdout']['path']).read_bytes().splitlines()]
        assert parent_records[-1] == inner
        worker_records = [json.loads(v) for v in Path(inner['stdout']['path']).read_bytes().splitlines()]
        assert len(worker_records) == 1 and worker_records[0]['receiptPath'] == str(receipt_path)
        assert receipt_row is not None
        receipt = json.loads(receipt_path.read_bytes())
        assert worker_records[0]['receipt'] == receipt and receipt['state'] == contract['frozenReceiptState']
        assert receipt['engineSha256'] == contract['engine']['sha256'] and receipt['receiptSha256'] == contract['metadata']['sha256']
        assert row(receipt['engine']) == dict(contract['engine'], path=receipt['engine'])
        assert row(str(Path(contract['freezeRoot']) / 'normal-off.engine.wasm.build.json')) == dict(contract['metadata'], path=str(Path(contract['freezeRoot']) / 'normal-off.engine.wasm.build.json'))
        names = {str(receipt_path)}
        for value in receipt['copies']:
            assert value['path'] not in names; names.add(value['path'])
            assert row(value['path']) == {k: value[k] for k in ['path', 'sha256', 'bytes']}
            target = Path(value['path']); st = target.stat()
            assert stat.S_IMODE(st.st_mode) == 0o600 and st.st_nlink == 1
            if value['original'] is not None:
                original = Path(value['original'])
                assert row(original) == dict(path=str(original), sha256=value['sha256'], bytes=value['bytes'])
                assert (st.st_dev, st.st_ino) != (original.stat().st_dev, original.stat().st_ino)
                originals += 1
            copies += 1
        assert {str(p) for p in Path(contract['freezeRoot']).rglob('*') if p.is_file()} == names
    except Exception as error:
        errors.append(dict(type=type(error).__name__, partialCopyObservation=True))
    for value in [root, config_row]:
        assert row(value['path']) == value
    family(SOURCE, source['sha256']); family(PEER, peer['index']['sha256']); family(MONITOR, monitor_index['sha256'])
    success = clean(terminal) and inner is not None and clean(inner) and receipt_row is not None and errors == []
    summary = dict(schemaVersion=1, state='ROOT_OBSERVED_SECRET_OWNER355_NORMAL_OFF_FREEZE_RAW_ZERO_UNREVIEWED_V1' if success else 'ROOT_OBSERVED_SECRET_OWNER355_NORMAL_OFF_FREEZE_FAILURE_NO_ACCEPTANCE_V1', freezerSourceIndex=source, nativeSourceIndex=contract['nativeSourceIndex'], sourceReview=peer, actualBuildReview=contract['actualBuildReview'], buildReferenceLedger=contract['buildReferenceLedger'], rootAuthority=root, config=config_row, monitorSourceIndex=monitor_index, outerTerminal=row(OUT / 'terminal.json'), innerTerminal=row(inner_path) if inner is not None else None, rawOuterExitCode=terminal['rawExitCode'], rawInnerExitCode=inner['rawExitCode'] if inner else None, receipt=receipt_row, engine=contract['engine'], metadata=contract['metadata'], frozenCopiesVerified=copies, originalReferencesVerified=originals, errors=errors, normalFreezeRawZeroObserved=success, independentFrozenArtifactReviewRequired=True, nativeBuildInvoked=False, engineExecuted=False, guestExecuted=False, operationalAdmission=False, runtimeAcceptanceClaim=False)
    result = write('results', summary)
    print(json.dumps(dict(result=result, normalFreezeRawZeroObserved=success)), flush=True)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
