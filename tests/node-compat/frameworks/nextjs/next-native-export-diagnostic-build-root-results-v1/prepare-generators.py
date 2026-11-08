"""Prepare one fresh generator-only authority; never launch generators here."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
GEN = HERE.parent / 'next-native-export-diagnostic-generators-v1'
INDEX_SHA = 'fa8be7350830330a78dc5d503581796281a6a18bf1a34d02a8518e3061ba34c2'
PLAN_SHA = '739331c0a323652dc4715123b943b2da208d475262d4830f6c8b7c58b30eb941'
SELECTION_SHA = 'f5d37ea06100c32bdfcf95d99562ccee1f228a426db4da013858680e80d5a16c'


def row(path):
    path = Path(path)
    assert path.is_absolute() and path.resolve() == path
    assert not any(p.is_symlink() for p in (path, *path.parents))
    before = path.stat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    data = path.read_bytes()
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_mode, before.st_nlink,
            before.st_size, before.st_mtime_ns, before.st_ctime_ns) == \
           (after.st_dev, after.st_ino, after.st_mode, after.st_nlink,
            after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def write_new(path, value):
    data = (json.dumps(value, indent=2) + '\n').encode()
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    return row(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    index_ref, plan_ref, selection_ref = [row(p) for p in
        [GEN / 'index.json', GEN / 'plan.json', HERE / 'portable-selection.json']]
    assert index_ref['sha256'] == INDEX_SHA and index_ref['bytes'] == 3795
    assert plan_ref['sha256'] == PLAN_SHA and plan_ref['bytes'] == 3559
    assert selection_ref['sha256'] == SELECTION_SHA and selection_ref['bytes'] == 1025706
    index = json.loads((GEN / 'index.json').read_bytes())
    names = [r['path'] for r in index['files']]
    assert len(names) == len(set(names)) == 7
    assert {p.name for p in GEN.iterdir()} == {'index.json', *names}
    refs = [index_ref, plan_ref, selection_ref]
    for member in index['files']:
        assert Path(member['path']).name == member['path']
        actual = row(GEN / member['path'])
        assert actual == dict(member, path=str(GEN / member['path']))
        refs.append(actual)
    authority = dict(schemaVersion=1, state='ROOT_PORTABLE_NEXT_GENERATORS_AUTHORIZED_V1',
        sourceIndex=index_ref, plan=plan_ref, portableSelection=selection_ref,
        runId='native-export-diag-first', generatorChecksAllowed=True, nodeHostSourceOnly=True,
        nativeBuildAllowed=False, compilerAllowed=False, cmakeAllowed=False, cargoAllowed=False,
        engineAllowed=False, guestAllowed=False, networkAllowed=False, copySourceAllowed=False,
        unissued=False, rootReview='Fresh genuine 825-file selection; ten unchanged Node --check commands only. '
        'Original 30-second command and 900-second owner ceilings; no old authority or proof retargeted.')
    result = dict(state='ROOT_DIAGNOSTIC_GENERATOR_AUTHORITY_PREVIEW_V1', authority=authority,
        generatorOrCompilerOrGuestInvoked=False, oldAuthorityRetargeted=False)
    if args.write:
        target, receipt = HERE / 'generator-authority.json', HERE / 'generator-preparation.json'
        assert not target.exists() and not target.is_symlink()
        assert not receipt.exists() and not receipt.is_symlink()
        authority_ref = write_new(target, authority)
        spec = importlib.util.spec_from_file_location('genuine_diagnostic_generator_preparation', GEN / 'run.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        admitted, plan, admitted_ref, output, outer, selected = module.bootstrap(target)
        assert admitted == authority and admitted_ref == authority_ref
        assert not output.exists() and not output.is_symlink()
        assert not outer.exists() and not outer.is_symlink()
        assert len(selected['files']) == len(selected['physicalRecords']) == 825
        result.update(state='ROOT_DIAGNOSTIC_GENERATOR_AUTHORITY_PREPARED_V1',
            authority=authority_ref, outputRoot=str(output), monitorOutputRoot=str(outer),
            files=len(selected['files']), roleCounts=selected['roleCounts'],
            roleContentSha256=selected['roleContentSha256'])
        write_new(receipt, result)
    for ref in refs:
        assert row(ref['path']) == ref
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
