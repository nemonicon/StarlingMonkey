"""Read/hash the complete declared closure. Does not import any owner module."""
from pathlib import Path
import hashlib
import json
import os

HERE = Path(__file__).resolve().parent


def identity(s):
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def main():
    assert not (HERE / 'index.json').exists()
    ledger = json.loads((HERE / 'source-inputs.json').read_bytes())
    refs = json.loads((HERE / 'references.json').read_bytes())
    declared_rows = {r['path']: r for r in ledger['files']}
    seen = {}
    total = 0
    for row in ledger['files']:
        p = Path(row['path'])
        assert p.is_absolute() and p.is_file() and not p.is_symlink() and str(p) not in seen
        before = p.stat()
        h = hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
                h.update(chunk)
        after = p.stat()
        assert identity(before) == identity(after)
        assert after.st_size == row['bytes'] and h.hexdigest() == row['sha256'], str(p)
        seen[str(p)] = identity(after)
        total += after.st_size
    for ix in ledger['families']:
        p = Path(ix['path'])
        members = json.loads(p.read_bytes())['files']
        expected = {'index.json'} | {r['path'] for r in members}
        actual = set()
        for base, directories, names in os.walk(p.parent, followlinks=False):
            for name in directories:
                assert not (Path(base) / name).is_symlink()
            for name in names:
                a = Path(base) / name
                assert a.is_file() and not a.is_symlink()
                actual.add(a.relative_to(p.parent).as_posix())
        assert actual == expected, str(p)
        assert str(p) in seen
        for row in members:
            a = p.parent / row['path']
            assert str(a) in seen
            assert a.stat().st_size == row['bytes']
            declared = declared_rows[str(a)]
            assert row['sha256'] == declared['sha256'] and row['bytes'] == declared['bytes']
    metadata = json.loads(Path(refs['metadata']['path']).read_bytes())
    history = json.loads(Path(refs['actualRetainedRecordData']['path']).read_bytes())['historicalBootstrap']
    assert len(metadata) == 75 and len(metadata['sourceManifest']) == 355
    assert len(metadata['componentizeSourceManifest']) == 3 and len(history['selectedManifests']) == 11
    assert metadata == history['metadata']
    assert metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE'] == 'Release'
    assert metadata['cryptoKeyOwnershipPolicy']['version'] == 'sm-webcrypto-key-owner-and-prototype-guard-source-v1'
    assert metadata['cryptoSecretFailureSourcePolicy']['version'] == 'sm-webcrypto-secret-failure-owner-source-v2'
    assert refs['outputRoot'].endswith('secret-component-v2') and not Path(refs['outputRoot']).exists()
    assert refs['externalRoot'].endswith('secret-component-v2-external-root') and not Path(refs['externalRoot']).exists()
    for path, expected in seen.items():
        assert identity(Path(path).stat()) == expected, path
    result = dict(schemaVersion=1, sourceOnly=True, files=len(seen), families=len(ledger['families']), logicalBytes=total,
                  fullHashesPassed=True, fullFamilyMembershipPassed=True, finalIdentitiesPassed=True,
                  nativeMetadataFields=75, nativeSourceFiles=355, externalEmbeddingSources=3, selectedWholeManifests=11,
                  constructorOrPackagerOrGuestInvoked=False)
    (HERE / 'closure-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
