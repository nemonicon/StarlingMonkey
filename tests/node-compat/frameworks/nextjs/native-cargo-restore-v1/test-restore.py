"""Small Source/DATA tests only; no actual2354-file restoration or Cargo/tool action."""
import ast
import copy
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import tomllib

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('source_restore', HERE / 'restore.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def main():
    c = r.load_catalog()
    manifest = c['manifest']
    out_a = Path('/not-created-source-example-A')
    out_b = Path('/not-created-source-example-B')
    a, b = r.render(c, out_a), r.render(c, out_b)
    assert a['project/Cargo.lock'] == b['project/Cargo.lock']
    assert r.sha(a['project/Cargo.lock']) == manifest['lockSha256']
    assert a['project/rust-staticlib.rs'] == b['project/rust-staticlib.rs']
    assert a['project/Cargo.toml'] != b['project/Cargo.toml']
    assert a['offline-cargo/config.toml'] != b['offline-cargo/config.toml']
    assert tomllib.loads(a['project/Cargo.toml'].decode())['dependencies']['icu_capi']['features'] == manifest['icuCapiFeatures']
    directories, payload_rows, _ = r.payload_layout(c, out_a)
    assert len(payload_rows) == 3506 and len(directories) == 463
    cases = []

    def reject(name, fn):
        try:
            fn()
        except (ValueError, tarfile.TarError):
            cases.append(name)
        else:
            raise AssertionError('accepted invalid DATA: ' + name)

    for name in ('/absolute', '../escape', 'a/../escape', './dot', 'a//alias', '.', ''):
        reject('relative-path-' + name, lambda n=name: r.rel(n))
    corrupt = copy.deepcopy(c)
    key = manifest['bundleMembers']['project']
    corrupt['text'][key] = corrupt['text'][key].replace(b'"segmenter", "calendar"', b'"segmenter"')
    reject('icu-feature-removed', lambda: r.render(corrupt, out_a))
    corrupt = copy.deepcopy(c)
    corrupt['text'][key] = corrupt['text'][key].replace(b'[workspace]', b'[workspace]\nmembers = ["unexpected"]')
    reject('workspace-inherited', lambda: r.render(corrupt, out_a))
    corrupt = copy.deepcopy(c)
    corrupt['text'][key] = corrupt['text'][key].replace(b'ca612daf1c08c53abe07327cb3e6ef6e0a760f0c', b'0000000000000000000000000000000000000000')
    reject('git-patch-rebound', lambda: r.render(corrupt, out_a))
    for config in ({}, {'baseRoot': None, 'ffiRoot': None, 'vendor': {}, 'unexpected': True}):
        reject('donor-schema-' + str(len(config)), lambda v=config: r.donors(c, v))
    with tempfile.TemporaryDirectory(prefix='native-cargo-source-data-') as tmp:
        root = Path(tmp).resolve()
        (root / 'sub').mkdir(mode=0o700)
        body = b'small owned fixture\n'
        path = root / 'sub/file'
        path.write_bytes(body)
        path.chmod(0o600)
        rows = [dict(path='sub/file', bytes=len(body), sha256=r.sha(body), mode=0o600)]
        before = r.tree(root, rows, {'sub': 0o700}, exact_modes=True)
        r.guard_sources(before)
        path.chmod(0o644)
        reject('physical-mode-change', lambda: r.guard_sources(before))
        reject('required-output-mode', lambda: r.tree(root, rows, {'sub': 0o700}, exact_modes=True))
        path.chmod(0o600)
        (root / 'extra-empty').mkdir()
        reject('extra-empty-directory', lambda: r.tree(root, rows, {'sub': 0o700}))
        (root / 'extra-empty').rmdir()
        path.write_bytes(b'changed fixture\n')
        reject('donor-content-change', lambda: r.tree(root, rows, {'sub': 0o700}))
        path.write_bytes(body)
        alias = root / 'alias'
        alias.symlink_to(path)
        reject('symbolic-file-alias', lambda: r.read_file(alias))
        alias.unlink()
        bad_receipt = root / 'restore-result.json'
        bad_receipt.write_text(json.dumps({'schemaVersion': 1, 'state': 'NOT_A_RESTORE'}))
        rejected_ref = dict(path=str(bad_receipt), bytes=bad_receipt.stat().st_size,
                            sha256=r.sha(bad_receipt.read_bytes()))
        reject('receipt-state', lambda: r.admit_restore(rejected_ref))
        claimed = dict(schemaVersion=1, state='LOCKED_CARGO_SOURCES_RESTORED_UNCHECKED_BY_CARGO_V1',
                       passed=True, sourceOnly=True, cargoOrCompilerOrNetworkOrGuestExecuted=False,
                       error=None, finalProtectionError=None, sourceProtection={'unchanged': True},
                       actualCargoMetadata=None, actualNativeBuild=None, actualEngine=None, actualRuntime=None,
                       outputRoot=str(root), sourceIndex={'path': 'wrong-source-index'})
        bad_receipt.write_text(json.dumps(claimed))
        rejected_ref = dict(path=str(bad_receipt), bytes=bad_receipt.stat().st_size,
                            sha256=r.sha(bad_receipt.read_bytes()))
        reject('receipt-wrong-producer-source-index', lambda: r.admit_restore(rejected_ref))
        claimed['publicationError'] = False
        bad_receipt.write_text(json.dumps(claimed))
        rejected_ref = dict(path=str(bad_receipt), bytes=bad_receipt.stat().st_size,
                            sha256=r.sha(bad_receipt.read_bytes()))
        reject('receipt-falsy-publication-error', lambda: r.admit_restore(rejected_ref))
        # Exercise the real completeness helper on three tiny owned trees;
        # this is not a complete84-package restore/admission positive.
        fixture_catalog = dict(c, base=rows, ffi=rows, vendor=rows,
                               baseDirs={'sub': 0o700}, ffiDirs={'sub': 0o700}, vendorDirs={'sub': 0o700})
        fixture_catalog['manifest'] = {**manifest, 'basePrefixes': ['sub']}
        fixture_roots = []
        for name in ('tiny-base', 'tiny-ffi', 'tiny-vendor'):
            p = root / name
            (p / 'sub').mkdir(parents=True, mode=0o700)
            (p / 'sub/file').write_bytes(body)
            (p / 'sub/file').chmod(0o600)
            fixture_roots.append(p)
        configuration = {'baseRoot': str(fixture_roots[0]), 'ffiRoot': str(fixture_roots[1]),
                         'vendor': {'kind': 'tree', 'root': str(fixture_roots[2])}}
        config_file = root / 'tiny-donor-config.json'
        config_file.write_text(json.dumps(configuration))
        _, config_row = r.read_file(config_file)
        admitted = r.donors(fixture_catalog, configuration)
        bookend_value = dict(inputConfig=config_row, sourceProtection={
            'protectedMetadataRecords': c['protected'] + [config_row],
            'donorPhysicalRecords': admitted['records']})
        assert r.recorded_bookends(fixture_catalog, bookend_value)
        missing = copy.deepcopy(bookend_value)
        missing['sourceProtection']['protectedMetadataRecords'] = []
        reject('omitted-metadata-bookends', lambda: r.recorded_bookends(fixture_catalog, missing))
        missing = copy.deepcopy(bookend_value)
        missing['sourceProtection']['donorPhysicalRecords'] = []
        reject('omitted-donor-bookends', lambda: r.recorded_bookends(fixture_catalog, missing))
        policy = manifest['policy']
        selected = {'src/lib.rs': dict(bytes=3, sha256=r.sha(b'abc'), mode=0o644)}

        def tar_body(entries):
            data = io.BytesIO()
            with tarfile.open(fileobj=data, mode='w') as archive:
                for name, kind, value in entries:
                    info = tarfile.TarInfo(name)
                    if kind == 'link':
                        info.type, info.linkname = tarfile.SYMTYPE, 'elsewhere'
                        archive.addfile(info)
                    else:
                        info.size = len(value)
                        archive.addfile(info, io.BytesIO(value))
            return gzip.compress(data.getvalue(), mtime=0)

        def run(entries, selected_rows=selected, overrides=None, checksum=None, consume=None):
            raw = tar_body(entries)
            path = root / 'fixture.crate'
            path.write_bytes(raw)
            recipe = dict(name='fixture', version='0.1.0', sha256=checksum or r.sha(raw))
            return r.archive_files(path, recipe, selected_rows, {**policy, **(overrides or {})}, consume)

        valid = [('fixture-0.1.0/src/lib.rs', 'file', b'abc'), ('fixture-0.1.0/.cargo_vcs_info.json', 'file', b'{}')]
        consumed = []
        report = run(valid, consume=lambda name, data, mode: consumed.append((name, data, mode)))
        assert report['selectedFiles'] == 1 and report['excludedSafeMembers'] == ['.cargo_vcs_info.json']
        assert consumed == [('fixture-0.1.0/src/lib.rs', b'abc', 0o644)]
        reject('registry-archive-checksum', lambda: run(valid, checksum='0' * 64))
        reject('tar-traversal', lambda: run(valid + [('fixture-0.1.0/../escape', 'file', b'x')]))
        reject('tar-absolute', lambda: run(valid + [('/absolute', 'file', b'x')]))
        reject('tar-other-root', lambda: run(valid + [('elsewhere/file', 'file', b'x')]))
        reject('tar-symlink', lambda: run(valid + [('fixture-0.1.0/link', 'link', b'')]))
        reject('tar-duplicate', lambda: run(valid + [valid[0]]))
        reject('tar-case-alias', lambda: run(valid + [('fixture-0.1.0/src/LIB.rs', 'file', b'abc')]))
        reject('tar-missing-selected', lambda: run(valid[1:]))
        reject('tar-wrong-selected-bytes', lambda: run([('fixture-0.1.0/src/lib.rs', 'file', b'bad')]))
        reject('tar-uncompressed-bound-before-header-parser', lambda: run(valid, overrides={'maximumArchiveExpandedBytes': 16}))
        reject('tar-member-count-bound', lambda: run(valid, overrides={'maximumArchiveEntries': 1}))
        reject('tar-file-size-bound', lambda: run(valid, overrides={'maximumFileBytes': 2}))
    ast.parse((HERE / 'restore.py').read_text())
    print(json.dumps(dict(sourceCatalogValidated=True, sourceFiles=3502, registryArchives=75,
                          relocations=8, configRelocations=1, unchangedFinal84Lock=True,
                          smallArchiveWhitelistPositive=True, smallTreePhysicalPositive=True,
                          smallCompleteBookendPositive=True,
                          refusalCount=len(cases), refusalCases=cases,
                          actualCargoMetadata=None, actualSourceRestorationRun=False,
                          actualRestoreAdmissionPositivePending=True,
                          cargoOrCompilerOrNetworkOrGuestExecuted=False), indent=2))


if __name__ == '__main__':
    main()
