"""Finite terminal failed-build and frontend-only DATA retention. Never invokes a target."""
from pathlib import Path
import gzip, hashlib, io, json, os, stat, tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT.parent
SECOND = BASE / 'next-module-fileurl-interop-native-root-results-v2'
FAILED = Path('/private/tmp/starling-node-compat/next-native-intl-build-interop825-first')
SYNTAX = Path('/private/tmp/starling-node-compat/next-module-fileurl-interop-v2-syntax-first')
FAMILIES = ['next-module-fileurl-interop-candidate-v1', 'next-module-fileurl-interop-candidate-v2',
            'next-native-portable-source-v3', 'next-native-portable-source-v4',
            'next-native-portable-build-preparation-v5', 'next-native-portable-build-preparation-v6']
FIRST_NAMES = ['actual-build-failure-review.json', 'review-build-failure-data.py',
 'failure-review.stdout.log', 'failure-review.stderr.log', 'actual-preparation-review.json',
 'native-build-admission-review.json', 'authority.unissued.json', 'launch.py',
 'build.stdout.log', 'build.stderr.log', 'portable-selection.json']
SECOND_NAMES = ['run-syntax.py', 'syntax-inputs.json', 'syntax-admission-review.json',
 'syntax.stdout.log', 'syntax.stderr.log', 'actual-syntax-review.json', 'portable-selection.json',
 'root-all825-source-readback.json', 'readback-source.py', 'readback-source.stderr.log',
 'materialization-admission.json', 'materialization.stdout.log', 'materialization.stderr.log',
 'prepare-selection.py', 'selection-preparation.json', 'selection.stdout.log', 'selection.stderr.log',
 'source-check.stdout.log', 'source-check.stderr.log']


def physical(path):
    s = path.lstat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def main():
    rows, blobs, paths, roles = [], {}, {}, {}
    def add(path, role):
        path = Path(path)
        assert path.is_absolute() and path.resolve(strict=True) == path
        assert not any(p.is_symlink() for p in [path, *path.parents])
        before = physical(path); assert stat.S_ISREG(before[2]) and before[3] == 1
        value = path.read_bytes(); assert physical(path) == before
        value.decode('utf-8'); assert b'\0' not in value
        ref = dict(path=str(path), sha256=hashlib.sha256(value).hexdigest(), bytes=len(value))
        if str(path) in paths:
            assert paths[str(path)]['original'] == ref and paths[str(path)]['physicalBefore'] == before
            return ref
        name = 'data/' + str(len(rows)).zfill(6)
        row = dict(archivePath=name, original=ref, mode=stat.S_IMODE(before[2]), physicalBefore=before, role=role)
        rows.append(row); blobs[name] = value; paths[str(path)] = row
        return ref
    def tree(root, role):
        for path in sorted(root.rglob('*')):
            assert not path.is_symlink() and (path.is_file() or path.is_dir())
            if path.is_file(): add(path, role)
    def reference(row, role):
        assert add(row['path'], role) == row
    families = []
    for name in FAMILIES:
        root = BASE / name; index = json.loads((root / 'index.json').read_bytes())
        families.append(add(root / 'index.json', 'closed-source-index'))
        assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == {r['path'] for r in index['files']} | {'index.json'}
        for row in index['files']:
            ref = add(root / row['path'], 'closed-source-member')
            assert (ref['sha256'], ref['bytes']) == (row['sha256'], row['bytes'])
    for name in ['result.json', 'metadata.json', 'protection-before.json', 'root-authority.json',
                 'environment-policy.json', 'configured-inputs.json']:
        roles['failed/' + name] = add(FAILED / name, 'actual-failed-build-data')
    for rel in ['build/compile_commands.json', 'build/CMakeCache.txt', 'build/build.ninja',
                'build/starling-raw.wasm/Cargo.toml', 'build/starling-raw.wasm/Cargo.lock', 'cargo-home/config.toml',
                'native-source/runtime/script_loader.cpp', 'build/cxx-wrapper']:
        roles['failed/' + rel] = add(FAILED / rel, 'selected-failure-configuration-or-source')
    tree(FAILED / 'results', 'complete-original-six-phase-data')
    tree(Path(str(FAILED) + '-root-monitor'), 'complete-original-root-owned-data')
    tree(SYNTAX, 'complete-original-frontend-only-data')
    for name in FIRST_NAMES: roles['root1/' + name] = add(ROOT / name, 'finite-first-root-record')
    for name in SECOND_NAMES: roles['root2/' + name] = add(SECOND / name, 'finite-second-root-record')
    metadata = json.loads((FAILED / 'metadata.json').read_bytes())
    authority = json.loads((FAILED / 'root-authority.json').read_bytes())
    for role, item in authority['reusedTrees'].items():
        reference(item['inventory'], 'recorded-tool-inventory-only-no-payload')
    for parent in [ROOT, SECOND]:
        selection = json.loads((parent / 'portable-selection.json').read_bytes())
        for key in ['composition', 'sourceMaterialization']:
            reference(selection[key], 'actual-source-materialization-record-only')
    syntax_input = json.loads((SECOND / 'syntax-inputs.json').read_bytes())
    for row in syntax_input['selectedSdkApiHeaders']:
        reference(row, 'selected-actual-sdk-header-source')
    reference(syntax_input['originalMonitor'], 'original-owner-source')
    current_loader = Path(syntax_input['argv'][-1])
    roles['selectedCorrectedLoader'] = add(current_loader, 'selected-corrected-source-only-not825-tree')
    assert len(rows) < 5000 and sum(len(v) for v in blobs.values()) < 128 * 1024**2
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode='wb', compresslevel=6, mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode='w', format=tarfile.USTAR_FORMAT) as archive:
            for row in rows:
                value = blobs[row['archivePath']]
                member = tarfile.TarInfo(row['archivePath']); member.size = len(value); member.mode = row['mode']; member.mtime = 0
                archive.addfile(member, io.BytesIO(value))
    for row in rows:
        p = Path(row['original']['path'])
        assert physical(p) == row['physicalBefore'] and p.read_bytes() == blobs[row['archivePath']]
    value = output.getvalue()
    index = dict(schemaVersion=1, state='UNSEALED_FAILED_INTEROP_BUILD_AND_FRONTEND_DATA_CAPSULE_V1',
      bundle=dict(path='data.tar.gz', sha256=hashlib.sha256(value).hexdigest(), bytes=len(value)),
      files=rows, memberCount=len(rows), logicalBytes=sum(len(v) for v in blobs.values()),
      sourceFamilies=families, roles=roles, failedBuildRoot=str(FAILED), syntaxRoot=str(SYNTAX),
      failedRoot=str(ROOT), syntaxRootRecords=str(SECOND),
      selectedOriginalsBeforeAndFinalHashAndPhysicalBookendsUnchanged=True,
      binaryOrComplete825PackageSdkPayloadTreeIncluded=False, recursiveArchivesIncluded=False,
      futureGeneratorOrFutureBuildRecordsIncluded=False, failedBuildAccepted=False,
      syntaxOnlyAccepted=True, nativeFullBuildOrEngineOrGuestAccepted=False, actorOrNetworkInvoked=False)
    for name, data in [('data.tar.gz', value), ('payload-index.json', (json.dumps(index, indent=2)+'\n').encode())]:
        fd = os.open(HERE / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(members=len(rows), logicalBytes=index['logicalBytes'], archive=index['bundle'], actorInvoked=False)))


if __name__ == '__main__': main()
