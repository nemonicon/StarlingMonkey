"""Inert acquisition DATA check. --current rehashes private inputs; no tools run."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import stat
import sys

HERE = Path(__file__).absolute().parent
SHA = '4e845cb71b4e897289312743b2e31c405a8a48720655404d82a4dce23fc43527'


def digest(data, ref):
    assert len(data) == ref['bytes'] and hashlib.sha256(data).hexdigest() == ref['sha256']


def current(ref):
    p = Path(ref['path'])
    assert p.is_absolute() and not any(x.is_symlink() for x in (p, *p.parents))
    assert stat.S_ISREG(p.lstat().st_mode) and p.stat().st_nlink == 1
    digest(p.read_bytes(), ref)


def main():
    if (HERE / 'index.json').exists():
        idx = json.loads((HERE / 'index.json').read_bytes())
        assert {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()} == {r['path'] for r in idx['files']} | {'index.json'}
        for r in idx['files']:
            digest((HERE / r['path']).read_bytes(), r)
    r = json.loads((HERE / 'acquisition-observation.json').read_bytes())
    assert r['state'] == 'APP_NPM_TOOL_ACQUISITION_PASSED_UNEXECUTED_V1' and r['passed'] is True
    assert r['nodeOrNpmExecuted'] is False and r['existingNodeUnchanged'] is True and r['existingNodeMatchesOfficialArchive'] is True
    assert r['archive']['sha256'] == r['publishedArchiveSha256'] == SHA and r['archive']['bytes'] == 24386052
    sums = (HERE / 'SHASUMS256.txt').read_bytes()
    digest(sums, r['shasums'])
    assert [line.split() for line in sums.decode().splitlines() if line.split()[1:] == ['node-v22.14.0-darwin-arm64.tar.xz']] == [[SHA, 'node-v22.14.0-darwin-arm64.tar.xz']]
    for key in ('shasumsHttp', 'archiveHttp'):
        assert r[key]['status'] == 200 and r[key]['finalUrl'].startswith('https://nodejs.org/download/release/v22.14.0/')
    assert r['npmVersion'] == '10.9.2' and r['npmFiles'] == 2379 and r['npmDirectories'] == 562 and r['npmSymlinks'] == 0 and r['npmBytes'] == 11690702
    raw = gzip.decompress((HERE / 'npm-inventory.json.gz').read_bytes())
    digest(raw, r['npmInventory'])
    inventory = json.loads(raw)
    assert inventory['root'] == r['npmRoot']
    rows = inventory['entries']
    names = [x['path'] for x in rows]
    assert len(names) == len(set(names)) == 2941
    assert sum(x['kind'] == 'file' for x in rows) == 2379 and sum(x.get('bytes', 0) for x in rows) == 11690702
    assert sum(x['kind'] == 'directory' for x in rows) == 562 and all(x['kind'] in ('file', 'directory') for x in rows)
    assert all(x['archiveMember'] == 'node-v22.14.0-darwin-arm64/lib/node_modules/npm' + ('' if x['path'] == '.' else '/' + x['path']) for x in rows)
    assert all(not Path(x['path']).is_absolute() and '..' not in Path(x['path']).parts for x in rows)
    cli = next(x for x in rows if x['path'] == 'bin/npm-cli.js')
    assert {k: cli[k] for k in ('sha256', 'bytes')} == {k: r['npmCli'][k] for k in ('sha256', 'bytes')}
    package = next(x for x in rows if x['path'] == 'package.json')
    assert {k: package[k] for k in ('sha256', 'bytes')} == {k: r['npmPackage'][k] for k in ('sha256', 'bytes')}
    assert {k: r['officialNodeMember'][k] for k in ('sha256', 'bytes')} == {k: r['existingNode'][k] for k in ('sha256', 'bytes')}
    assert r['officialNodeMember']['extracted'] is False and r['officialNodeMember']['archiveMember'] == 'node-v22.14.0-darwin-arm64/bin/node'
    assert r['existingNode']['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    assert r['startFreeBytes'] >= 1024**3 and r['endFreeBytes'] >= 1024**3 and r['privateRegularBytes'] < 128 * 1024**2 and r['endCapacityFloorPassed'] is True
    assert r['signatureVerified'] is False
    if '--current' in sys.argv:
        for key in ('archive', 'shasums', 'npmInventory', 'npmCli', 'npmPackage', 'existingNode'):
            current(r[key])
        root = Path(r['npmRoot'])
        assert {'.'} | {p.relative_to(root).as_posix() for p in root.rglob('*')} == set(names)
        for x in rows:
            p = root / x['path']
            assert not p.is_symlink() and stat.S_IMODE(p.stat().st_mode) == x['mode']
            if x['kind'] == 'file':
                current(dict(path=str(p), sha256=x['sha256'], bytes=x['bytes']))
            else:
                assert p.is_dir()
        assert json.loads(Path(r['npmPackage']['path']).read_bytes())['version'] == '10.9.2'
        s = Path(r['existingNode']['path']).stat()
        assert dict(dev=s.st_dev, ino=s.st_ino, nlink=s.st_nlink, mode=stat.S_IMODE(s.st_mode), bytes=s.st_size, mtimeNs=s.st_mtime_ns, ctimeNs=s.st_ctime_ns) == r['existingNodeBeforeIdentity']
    return dict(schemaVersion=1, state='ACTUAL_OFFICIAL_NPM_TOOL_ACQUISITION_DATA_VERIFIED_V1', verifiedEvidence=True,
                officialArchive=r['archive'], npmVersion=r['npmVersion'], npmCli=r['npmCli'], npmFiles=2379,
                npmDirectories=562, npmLinks=0, npmBytes=11690702, existingNodeMatchesOfficialUnextractedNode=True,
                existingNodeUnchanged=True, officialPublishedShasumMatched=True, openPgpSignatureVerified=False,
                acquisitionPhaseOnly=True, nodeOrNpmExecutedByAcquisition=False, npmCiOrNextBuildExecutedByAcquisition=False, appBuildProofSuppliedByAcquisition=False,
                binariesOrPackagePayloadCopiedIntoRepository=False,
                scope='Official HTTPS archive/SHASUMS, archive-derived npm inventory and finite input bookends; no package execution, full OS/toolchain hermeticity or app/runtime acceptance.')


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
