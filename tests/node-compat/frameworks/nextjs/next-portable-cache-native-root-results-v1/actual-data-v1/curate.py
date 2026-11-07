"""Retain finite terminal Native/Stock V1 DATA; no app trees, actors or imports."""
from pathlib import Path
import gzip, hashlib, io, json, os, stat, tarfile

HERE = Path(__file__).resolve().parent
NATIVE_ROOT = HERE.parent
BASE = NATIVE_ROOT.parent
STOCK_ROOT = BASE / 'next-portable-cache-stock-root-results-v1'
NATIVE = Path('/private/tmp/starling-node-compat/next-wasmtime-deployment-portable-cache-native-first')
STOCK = Path('/private/tmp/starling-node-compat/next-portable-cache-stock-v1-portable-cache-stock-first')
FAMILIES = ['next-portable-cache-native-candidate-v1', 'next-portable-cache-stock-candidate-v1',
            'next-portable-cache-http-collector-v1', 'next-portable-cache-handler-candidate-v2']


def physical(path):
    s = path.lstat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def main():
    rows, payload, originals, roles, trees, families = [], {}, {}, {}, [], []

    def add(path, role):
        path = Path(path)
        assert path.is_absolute() and path.resolve() == path and not path.is_symlink()
        assert 'server-reference-manifest' not in path.name
        assert path.suffix not in ['.wasm', '.a', '.dylib', '.gz']
        before = physical(path)
        assert stat.S_ISREG(before[2]) and before[3] == 1
        body = path.read_bytes()
        assert physical(path) == before and len(body) <= 6 * 1024 * 1024
        if path.suffix == '.png':
            assert body.startswith(b'\x89PNG\r\n\x1a\n')
        else:
            body.decode('utf8')
            assert b'\0' not in body
        ref = dict(path=str(path), sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
        if str(path) in originals:
            assert originals[str(path)]['original'] == ref
            return ref
        name = 'data/%05d' % len(rows)
        record = dict(archivePath=name, original=ref, mode=stat.S_IMODE(before[2]),
                      physicalBefore=before, role=role)
        rows.append(record); payload[name] = body; originals[str(path)] = record
        return ref

    def tree(root, omissions):
        files, directories = [], [dict(path='.', physicalBefore=physical(root))]
        for parent, names, children in os.walk(root, followlinks=False):
            parent = Path(parent)
            if parent == root:
                names[:] = [name for name in names if name not in omissions]
            for name in sorted(names):
                path = parent / name
                assert not path.is_symlink() and path.is_dir()
                directories.append(dict(path=path.relative_to(root).as_posix(), physicalBefore=physical(path)))
            for name in sorted(children):
                path = parent / name
                rel = path.relative_to(root).as_posix()
                files.append(rel); add(path, 'complete-selected-runtime-or-monitor-record')
        trees.append(dict(root=str(root), omittedTopLevelDirectories=omissions,
                          files=sorted(files), directories=sorted(directories, key=lambda x: x['path'])))

    tree(NATIVE, ['app'])
    tree(Path(str(NATIVE) + '-external-root'), [])
    tree(STOCK, ['application'])
    tree(Path(str(STOCK) + '-monitor'), [])
    for root, names, prefix in [
        (NATIVE_ROOT, ['actual-outcome-review.json', 'actual-runtime-review.json',
                      'native-first-runtime-authority.json', 'portable-cache-native-first-full-world-guard.json',
                      'prepare-runtime.py', 'run-full-native-requests.py', 'runtime-preparation.json',
                      'preparation.stdout.log', 'preparation.stderr.log', 'runtime.stdout.log', 'runtime.stderr.log'], 'native'),
        (STOCK_ROOT, ['actual-runtime-review.json', 'stock-first-runtime-authority.json', 'prepare-runtime.py',
                     'runtime-preparation.json', 'preparation.stdout.log', 'preparation.stderr.log',
                     'runtime.stdout.log', 'runtime.stderr.log'], 'stock')]:
        for name in names:
            roles[prefix + '/' + name] = add(root / name, 'fixed-root-authority-review-source-or-stream')
    for name in FAMILIES:
        index_path = BASE / name / 'index.json'
        index = json.loads(index_path.read_text())
        index_ref = add(index_path, 'closed-small-source-family-index')
        for row in index['files']:
            ref = add(index_path.parent / row['path'], 'closed-small-source-family-payload')
            assert ref['sha256'] == row['sha256'] and ref['bytes'] == row['bytes']
        families.append(index_ref)
    for name in ['fixture-contract.json']:
        roles[name] = add(BASE / name, 'fixed-fixture-contract')
    # These are descriptor/provenance records, not omitted payload revalidation.
    native_authority = json.loads((NATIVE_ROOT / 'native-first-runtime-authority.json').read_text())
    for key in ['nativeMetadata', 'constructionResult', 'componentAudit', 'constructionDataReview',
                'fullNativeBuildReview', 'applicationBuildDataReview']:
        roles[key] = add(native_authority[key]['path'], 'documentary-native-constructor-app-provenance')
    native_plan = json.loads((BASE / FAMILIES[0] / 'plan.json').read_text())
    for key in ['applicationInputs', 'applicationBuildResult']:
        roles[key] = add(native_plan[key]['path'], 'documentary-application-inventory-or-build-result')
    assert len({tuple(row['physicalBefore'][:2]) for row in rows}) == len(rows)
    for row in rows:
        path = Path(row['original']['path'])
        assert physical(path) == row['physicalBefore'] and path.read_bytes() == payload[row['archivePath']]
    for item in trees:
        for directory in item['directories']:
            assert physical(Path(item['root']) / directory['path']) == directory['physicalBefore']
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=6, mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode='w', format=tarfile.USTAR_FORMAT) as archive:
            for row in rows:
                body = payload[row['archivePath']]
                item = tarfile.TarInfo(row['archivePath']); item.size = len(body)
                item.mode = row['mode']; item.mtime = 0
                archive.addfile(item, io.BytesIO(body))
    body = buf.getvalue()
    ledger = dict(schemaVersion=1, state='UNSEALED_PORTABLE_CACHE_NATIVE_AND_STOCK_V1_FINITE_DATA',
                  bundle=dict(path='data.tar.gz', sha256=hashlib.sha256(body).hexdigest(), bytes=len(body)),
                  files=rows, trees=trees, roles=roles, sourceFamilies=families,
                  memberCount=len(rows), logicalBytes=sum(len(v) for v in payload.values()),
                  nativeRuntimeRoot=str(NATIVE), stockRuntimeRoot=str(STOCK),
                  appTreesBinariesSdk825AndBuildSecretPayloadsIncluded=False,
                  sourceAndPayloadReevaluationInvoked=False, stockV2Included=False,
                  selectedOriginalHashAndPhysicalBookendsUnchanged=True)
    for name, data in [('data.tar.gz', body), ('payload-index.json', (json.dumps(ledger, indent=2) + '\n').encode())]:
        fd = os.open(HERE / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
    print(json.dumps(dict(members=len(rows), logicalBytes=ledger['logicalBytes'], archive=ledger['bundle'],
                          actorOrSourceEvaluatorInvoked=False)))


if __name__ == '__main__':
    main()
