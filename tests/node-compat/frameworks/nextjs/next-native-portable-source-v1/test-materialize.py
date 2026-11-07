"""Finite source-copy tests; only Python, JSON, hashes and owned text files."""
from pathlib import Path
import argparse
import collections
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).absolute().parent
REPO = HERE.parents[4]
spec = importlib.util.spec_from_file_location('portable_source_under_test', HERE / 'materialize.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-metadata', type=Path)
    parser.add_argument('--delta-metadata', type=Path)
    args = parser.parse_args()
    assert bool(args.baseline_metadata) == bool(args.delta_metadata)
    checks = []

    def check(ok, name):
        if not ok:
            raise AssertionError(name)
        checks.append(name)

    def refuse(operation, name):
        try:
            operation()
        except (ValueError, FileExistsError):
            checks.append(name)
            return
        raise AssertionError('Accepted: ' + name)

    selection, rows, inputs = m.selection(REPO)
    for r in rows:
        r['donorPath'] = str(REPO / r['repositoryDonor'])
    check(len(rows) == 825 and sum(r['bytes'] for r in rows) == 7530166, 'whole825 input boundary')
    check(collections.Counter(r['role'] for r in rows) == m.COUNTS, '435native/387support/3embedding')
    before = {p: x.copy() for p, x in inputs.items()}
    summary = m.run(REPO)
    check(summary['outputRoot'] is None and summary['state'] == 'NEXT_PORTABLE_SOURCE_DONORS_CHECKED_V1', 'default no-output check')
    historical = json.loads((HERE / 'historical-comparison.json').read_text())
    check(m.fingerprint(rows) == historical['roleContentSha256'], 'historically checked fullrole table')
    actual_matched = False
    if args.baseline_metadata:
        b, br = m.read_file(args.baseline_metadata, historical['baselineMetadata'])
        d, dr = m.read_file(args.delta_metadata, historical['deltaMetadata'])
        base = json.loads(b)
        delta = json.loads(d)
        expected = {}
        for r in base['nativePolicyInputManifest']:
            expected[('native-policy-source', r['path'])] = (r['sha256'], r['bytes'])
        expected[('native-policy-source', 'builtins/node-compat/module-kernel.cpp')] = tuple(delta['actualAfterimage'][k] for k in ('sha256', 'bytes'))
        for role, key in [('build-support', 'buildSupportInputManifest'), ('componentize-embedding', 'embeddingInputManifest')]:
            for r in base[key]:
                expected[(role, r['relativePath'])] = (r['source']['sha256'], r['source']['bytes'])
        actual = {(r['role'], r['path']): (r['sha256'], r['bytes']) for r in rows}
        check(actual == expected, 'all825 genuine actual preconfigured roles/path/hash/bytes match')
        check(base['nativePolicyInputCount'] == 435 and delta['freshFrontendCompileRows'] == 1
              and delta['virtualOriginalSource']['sha256'] == next(r['sha256'] for r in base['nativePolicyInputManifest'] if r['path'] == 'builtins/node-compat/module-kernel.cpp'), 'real incremental source parent join')
        actual_matched = True
    for bad in ['', '.', '../x', '/absolute', 'a//b', 'a/../b', 'a\\b', 'a\0b']:
        refuse(lambda: m.relative(bad), 'relative refusal ' + repr(bad))

    with tempfile.TemporaryDirectory(prefix='next-native-portable-source-test-', dir='/private/tmp') as temp:
        root = Path(temp)
        out = root / 'output'
        result = m.run(REPO, out)
        m.verify_output(out, rows)
        check(result['state'] == 'NEXT_PORTABLE_SOURCE_MATERIALIZED_V1', 'fresh complete source copy')
        check({p.name for p in out.iterdir()} == set(m.ROLES.values()) | {'composition.json', 'source-materialization.json'}, 'exact root manifests/layout')
        comp = json.loads((out / 'composition.json').read_text())
        check(comp['nativeSourceFiles'] == len(comp['files']) == 435 and not comp['engineBuilt']
              and not comp['legacyMetadataProjected'] and comp['sourceRoot'] == str(out / 'source'), 'honest new composition paths/no build')
        receipt = json.loads((out / 'source-materialization.json').read_text())
        check(len(receipt['filesCopied']) == 825 and receipt['roleContentSha256'] == summary['roleContentSha256'], 'whole materialization manifest')
        snapshot = (out / 'source-materialization.json').read_bytes()
        refuse(lambda: m.run(REPO, out), 'overwrite refused')
        check((out / 'source-materialization.json').read_bytes() == snapshot, 'overwrite refusal preserves prior output')
        alias = root / 'alias'
        alias.symlink_to(out, target_is_directory=True)
        refuse(lambda: m.run(REPO, alias), 'output symlink refused')
        refuse(lambda: m.run(REPO, alias / 'nested'), 'symlink ancestor refused')
        refuse(lambda: m.run(REPO, Path('relative-output')), 'relative output refused')
        (out / 'unindexed.txt').write_text('extra')
        refuse(lambda: m.verify_output(out, rows), 'extra root file refused')
        (out / 'unindexed.txt').unlink()
        victim = out / m.ROLES[rows[0]['role']] / rows[0]['path']
        saved = victim.read_bytes()
        victim.write_bytes(saved + b'changed')
        refuse(lambda: m.verify_output(out, rows), 'changed output bytes refused')
        victim.write_bytes(saved)
        oldmode = victim.stat().st_mode & 0o777
        victim.chmod(0o777)
        refuse(lambda: m.verify_output(out, rows), 'changed output mode refused')
        victim.chmod(oldmode)
        victim.unlink()
        # Hardlink only owned scratch: never change a repository donor's nlink.
        hardlink_source = root / 'owned-hardlink-source'
        hardlink_source.write_bytes(saved)
        os.link(hardlink_source, victim)
        refuse(lambda: m.verify_output(out, rows), 'output hardlink refused')
        victim.unlink()
        victim.write_bytes(saved)
        victim.chmod(oldmode)

        # A genuine relocated finite repository closure, without private paths.
        relocated = root / 'relocated-repository'
        for name in sorted({str(Path(r['path']).relative_to(REPO)) for r in inputs.values()}):
            target = relocated / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / name, target)
        script = relocated / m.REL / 'materialize.py'
        child = subprocess.run([sys.executable, '-I', '-B', str(script)], cwd=str(root), capture_output=True, timeout=30)
        check(child.returncode == 0 and child.stderr == b'', 'real relocated CLI default read-only')
        check(json.loads(child.stdout)['roleContentSha256'] == summary['roleContentSha256'], 'relocated allinput content equality')
        destination = root / 'relocated-output'
        child = subprocess.run([sys.executable, '-I', '-B', str(script), '--output', str(destination)], cwd=str(root), capture_output=True, timeout=30)
        check(child.returncode == 0 and child.stderr == b'', 'real relocated CLI fresh text copy')
        check(json.loads(child.stdout)['outputRoot'] == str(destination), 'relocated output owns new paths')
        relspec, relrows, _ = m.selection(relocated)
        for r in relrows:
            r['donorPath'] = str(relocated / r['repositoryDonor'])
        m.verify_output(destination, relrows)
        check(all(str(relocated) in r['path'] for r in json.loads((destination / 'composition.json').read_text())['inputs']), 'new composition records relocated actual inputs')
        donor = relocated / rows[0]['repositoryDonor']
        original = donor.read_bytes()
        donor.write_bytes(original + b'changed')
        refuse(lambda: m.selection(relocated), 'changed real donor refused')
        donor.write_bytes(original)
        link = root / 'donor-hardlink'
        os.link(donor, link)
        refuse(lambda: m.selection(relocated), 'hardlinked real donor refused')
        link.unlink()
        donor.unlink()
        donor.symlink_to(Path(rows[0]['donorPath']))
        refuse(lambda: m.selection(relocated), 'symlink real donor refused')
    m.recheck(before)
    return dict(schemaVersion=1, passed=True, checks=len(checks), cases=checks,
                all825ActualDeclaredInputsMatched=actual_matched,
                roleContentSha256=summary['roleContentSha256'], donorInputsUnchanged=True,
                relocatedCliAndFreshTextCopiesPassed=True, ownedTemporaryCopiesRemoved=True,
                compilerToolCargoNetworkOrGuestExecuted=False)


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
