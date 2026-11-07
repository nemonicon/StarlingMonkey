"""Finite completed probe INIT/deployed DATA retention. No tool, target or extraction."""
from pathlib import Path
import gzip, hashlib, io, json, os, stat, tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT.parent
CTOR = Path('/private/tmp/starling-node-compat/next-module-fileurl-probe-component-v1-guard-guard-ca84-first')
RUNTIME = Path('/private/tmp/starling-node-compat/next-module-fileurl-guard-probe-v1-guard-ca84-probe-first')
FAMILIES = ['next-module-fileurl-probe-candidate-v1', 'next-module-fileurl-probe-construction-v1',
            'next-module-fileurl-probe-runtime-candidate-v1', 'regexp-unicode-probe-candidate-v1',
            'next-module-fileurl-boundary-candidate-v1', 'next-native-portable-build-preparation-v4']
ROOT_NAMES = ['construction.stderr.log', 'preparation.stdout.log', 'runtime-preparation.stderr.log',
              'first-runtime.stdout.log', 'actual-package-review.json', 'launch-construction.py',
              'construction-preparation.json', 'actual-owner-world-review.json', 'runtime-admission-review.json',
              'actual-construction-review.json', 'runtime-preparation.json', 'preparation.stderr.log',
              'construction.stdout.log', 'first-runtime.stderr.log', 'actual-runtime-review.json',
              'runtime-preparation.stdout.log', 'construction-admission-review.json', 'prepare-runtime.py',
              'guard-probe-v1-construction-authority.json', 'run-probe.py',
              'guard-ca84-probe-first-full-native-world-guard.json', 'prepare-construction.py',
              'guard-ca84-first-runtime-authority.json']


def physical(path):
    s = path.lstat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def main():
    records, payload, selected, roles = [], {}, {}, {}

    def add(path, role):
        path = Path(path)
        assert path.is_absolute() and path.resolve(strict=True) == path
        assert all(not p.is_symlink() for p in (path, *path.parents))
        before = physical(path)
        assert stat.S_ISREG(before[2]) and before[3] == 1
        data = path.read_bytes()
        assert physical(path) == before
        data.decode('utf-8'); assert b'\0' not in data
        ref = dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
        if str(path) in selected:
            old = selected[str(path)]
            assert old['original'] == ref and old['physicalBefore'] == before
            return ref
        name = 'data/' + str(len(records)).zfill(6)
        record = dict(archivePath=name, original=ref, mode=stat.S_IMODE(before[2]), physicalBefore=before, role=role)
        records.append(record); selected[str(path)] = record; payload[name] = data
        return ref

    def tree(root, role, exclude=()):
        root = Path(root)
        for path in sorted(root.rglob('*')):
            assert not path.is_symlink() and (path.is_file() or path.is_dir())
            if path.is_file() and path.name not in exclude:
                add(path, role)

    families = []
    for name in FAMILIES:
        path = BASE / name
        index = json.loads((path / 'index.json').read_bytes())
        families.append(add(path / 'index.json', 'closed-source-family-index'))
        actual = {p.relative_to(path).as_posix() for p in path.rglob('*') if p.is_file()}
        assert actual == {row['path'] for row in index['files']} | {'index.json'}
        for row in index['files']:
            ref = add(path / row['path'], 'closed-source-family-member')
            assert ref['sha256'] == row['sha256'] and ref['bytes'] == row['bytes']
    tree(CTOR, 'actual-constructor-original', exclude=('returned-component.wasm',))
    tree(Path(str(CTOR) + '-external-root'), 'actual-constructor-outer-original')
    tree(RUNTIME, 'actual-runtime-original')
    tree(Path(str(RUNTIME) + '-external-root'), 'actual-runtime-outer-original')
    for name in ROOT_NAMES:
        roles[name] = add(ROOT / name, 'root-source-authority-or-actual-review')
    ctor_result = json.loads((CTOR / 'result.json').read_bytes())
    ctor_authority = json.loads(Path(ctor_result['rootAuthority']['path']).read_bytes())
    runtime_authority = json.loads((ROOT / 'guard-ca84-first-runtime-authority.json').read_bytes())
    for ref in ctor_authority['engineBuildEvidence'] + ctor_authority['newSourceEvidence']:
        assert add(ref['path'], 'finite-native-build-evidence-or-source') == ref
    for key in ['fullBuildGuardImplementation', 'worldGuardImplementation']:
        assert add(runtime_authority[key]['path'], 'root-guard-implementation-source') == runtime_authority[key]
    plan = json.loads(Path(ctor_result['plan']['path']).read_bytes())
    roles['packageInventory'] = add(plan['packageInventory']['path'], 'tool-package-inventory-only-no-package-payload')
    roles['fullNativeMetadata'] = add(ctor_authority['nativeMetadata']['path'], 'actual-full-native-metadata-only')
    assert roles['fullNativeMetadata'] == ctor_authority['nativeMetadata']
    assert len(records) < 1000 and sum(len(value) for value in payload.values()) < 64 * 1024**2
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb', compresslevel=6, mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w', format=tarfile.USTAR_FORMAT) as archive:
            for record in records:
                data = payload[record['archivePath']]
                item = tarfile.TarInfo(record['archivePath']); item.size = len(data); item.mode = record['mode']; item.mtime = 0
                archive.addfile(item, io.BytesIO(data))
    for record in records:
        path = Path(record['original']['path'])
        assert physical(path) == record['physicalBefore'] and path.read_bytes() == payload[record['archivePath']]
    compressed = buffer.getvalue()
    index = dict(schemaVersion=1, state='UNSEALED_GUARD_PROBE_INIT_AND_RUNTIME_DATA_CAPSULE_V1',
                 bundle=dict(path='data.tar.gz', sha256=hashlib.sha256(compressed).hexdigest(), bytes=len(compressed)),
                 memberCount=len(records), logicalBytes=sum(len(value) for value in payload.values()), files=records,
                 sourceFamilies=families, roles=roles, constructorRoot=str(CTOR), runtimeRoot=str(RUNTIME),
                 allSelectedOriginalPhysicalAndContentBookendsUnchanged=True,
                 binaryApplicationPackageSdkOr825PayloadIncluded=False, recursiveArchivesIncluded=False,
                 actorOrToolOrNetworkInvoked=False, guardSafeRefusalOnly=True, nodeCompatibilityAccepted=False,
                 interopOrFullNextAccepted=False)
    for name, data in [('data.tar.gz', compressed), ('payload-index.json', (json.dumps(index, indent=2) + '\n').encode())]:
        fd = os.open(HERE / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps(dict(members=len(records), logicalBytes=index['logicalBytes'], archive=index['bundle'],
                         actorInvoked=False, selectedOriginalsUnchanged=True)))


if __name__ == '__main__':
    main()
