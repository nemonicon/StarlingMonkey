"""Curate only finite, completed full-native build text DATA; never run a producer."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import stat
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT.parent
WORK = Path('/private/tmp/starling-node-compat/next-native-intl-build-fetch-cleanup825-first')
MAX_MEMBERS = 2500
MAX_BYTES = 32 * 1024**2
MAX_ARCHIVE = 8 * 1024**2


def sha(data):
    return hashlib.sha256(data).hexdigest()


def physical(path):
    s = path.lstat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true', help='Exclusively publish the measured archive and ledger.')
    args = p.parse_args()
    rows, payload, originals, roles, trees = [], {}, {}, {}, []

    def add(name, path, role=None):
        path = Path(path)
        assert path.is_absolute() and path.resolve() == path
        assert all(not x.is_symlink() for x in (path, *path.parents))
        before = physical(path)
        assert stat.S_ISREG(before[2]) and before[3] == 1
        data = path.read_bytes()
        assert physical(path) == before
        data.decode('utf-8')
        assert b'\0' not in data
        ref = dict(path=str(path), sha256=sha(data), bytes=len(data))
        if str(path) in originals:
            row = originals[str(path)]
            assert row['original'] == ref
        else:
            assert name not in payload and not name.startswith('/') and '..' not in Path(name).parts
            row = dict(member=name, original=ref, mode=stat.S_IMODE(before[2]), physicalBefore=before)
            rows.append(row)
            originals[str(path)] = row
            payload[name] = data
        if role:
            assert role not in roles
            roles[role] = row['member']
        return json.loads(data) if path.suffix == '.json' else None

    def tree(prefix, path):
        path = Path(path)
        nodes = sorted(path.rglob('*'))
        assert not any(x.is_symlink() for x in [path, *nodes])
        assert all(x.is_file() or x.is_dir() for x in nodes)
        inventory = [(x.relative_to(path).as_posix(), 'file' if x.is_file() else 'directory') for x in nodes]
        trees.append((path, inventory))
        for x in nodes:
            if x.is_file():
                add(prefix + '/' + x.relative_to(path).as_posix(), x)

    for name in ['result.json', 'metadata.json', 'root-authority.json', 'configured-inputs.json',
                 'protection-before.json', 'environment-policy.json']:
        add('native/work/' + name, WORK / name, name[:-5])
    outer = Path(str(WORK) + '-root-monitor')
    tree('native/outer', outer)
    for key in ['terminal', 'observation', 'started']:
        roles['outer-' + key] = originals[str(outer / (key + '.json'))]['member']
    tree('native/results', WORK / 'results')
    for name in ['compile_commands.json', 'CMakeCache.txt', 'starling-raw.wasm/Cargo.toml',
                 'starling-raw.wasm/Cargo.lock', 'starling-raw.wasm/null.cpp']:
        add('native/configured/' + name, WORK / 'build' / name)
    metadata = json.loads(payload[roles['metadata']])
    authority = json.loads(payload[roles['root-authority']])
    for role, spec in authority['reusedTrees'].items():
        add('inputs/inventories/' + role + '.json', spec['inventory']['path'], 'tree-' + role)
    for key in ['portableCargoSelection', 'sourceComposition', 'patchedSpiderMonkeyEvidence',
                'offlineCargoConfig', 'actualAggregateLock']:
        add('inputs/' + key + '.json', metadata[key]['path'], 'input-' + key)
    selection = add('inputs/portableSelection.json', authority['portableSelection']['path'], 'portable-selection')
    add('inputs/sourceMaterialization.json', selection['sourceMaterialization']['path'], 'materialization')
    prepared = Path(authority['portableCargoSelection']['path']).parent.parent
    for name in ['preparation.json', 'root-authority.unissued.json']:
        add('inputs/prepared/' + name, prepared / name, 'prepared-' + name[:-5])
    families = {
        'next-native-fetch-resource-cleanup-candidate-v2': ['index.json', 'version-manifest.json'],
        'next-native-portable-source-v6': ['index.json', 'selection.json', 'materialize.py'],
        'next-native-portable-build-preparation-v8': ['index.json', 'plan.json', 'run.py', 'prepare.py', 'cargo-selection.py', 'portable.py'],
        'next-native-portable-generator-check-v6': ['index.json', 'plan.json', 'run.py'],
    }
    for family, names in families.items():
        for name in names:
            add('source-witnesses/' + family + '/' + name, BASE / family / name)
    names = ['actual-build-review.json', 'actual-build-source-review.json', 'actual-build-owner-review.json',
             'native-build-admission-review.json', 'launch.py', 'authority.unissued.json',
             'generation-preparation-inputs.json', 'assemble-draft.py', 'mapping-source-checks.json',
             'draft-assembly.json', 'draft-assembly.stdout.log', 'draft-assembly.stderr.log',
             'build.stdout.log', 'build.stderr.log', 'actual-preparation-v2-review.json',
             'actual-frontends-v3-review.json', 'generator-admission-readback-v2.json',
             'actual-generator-owner-review-v2.json', 'materialization-readback-v2.json',
             'selection-preparation-v2.json', 'preparation-config-v2.json',
             'preparation-v2.stdout.log', 'preparation-v2.stderr.log']
    for name in names:
        add('root/' + name, ROOT / name, 'root-' + name.removesuffix('.json'))
    assert len(rows) <= MAX_MEMBERS and sum(map(len, payload.values())) <= MAX_BYTES
    for row in rows:
        assert physical(Path(row['original']['path'])) == row['physicalBefore']
    for root, inventory in trees:
        nodes = sorted(root.rglob('*'))
        assert not any(x.is_symlink() for x in nodes)
        assert [(x.relative_to(root).as_posix(), 'file' if x.is_file() else 'directory') for x in nodes] == inventory
    out = dict(schemaVersion=1, state='FETCH_CLEANUP_FULL_NATIVE_FINITE_TEXT_DATA_V1',
               memberCount=len(rows), expandedBytes=sum(map(len, payload.values())),
               limits=dict(members=MAX_MEMBERS, expandedBytes=MAX_BYTES, archiveBytes=MAX_ARCHIVE),
               roles=roles, members=rows,
               selectedTrees=[dict(root=str(root), entries=inventory) for root, inventory in trees],
               allSelectedReadBookendsUnchanged=True,
               scope='Finite original text and recorded descriptors/snapshots only; no engine, SDK, library, object, package, app or825Source payloads. Selected Source files are witnesses, not recursive family closures.',
               curatorRelationship='B authored current portable materializer/builder/generator/map forks and ancestral helpers; C/R independently reviewed accepted build DATA. This retention does not independently rerun that build or its producers.',
               binariesRetained=False, sourcePayload825Retained=False, actorOrProducerInvoked=False)
    if args.write:
        raw = io.BytesIO()
        with tarfile.open(fileobj=raw, mode='w', format=tarfile.USTAR_FORMAT) as tf:
            for row in rows:
                info = tarfile.TarInfo(row['member'])
                info.size, info.mode, info.mtime = row['original']['bytes'], row['mode'], 0
                tf.addfile(info, io.BytesIO(payload[row['member']]))
        data = gzip.compress(raw.getvalue(), mtime=0)
        assert len(data) <= MAX_ARCHIVE
        out['archive'] = dict(path='data.tar.gz', sha256=sha(data), bytes=len(data))
        for name, data in [('data.tar.gz', data), ('payload-index.json', (json.dumps(out, indent=2) + '\n').encode())]:
            with (HERE / name).open('xb') as f:
                f.write(data)
    print(json.dumps({k: out[k] for k in ['state', 'memberCount', 'expandedBytes', 'limits', 'scope']} | {'archive': out.get('archive'), 'written': args.write}))


if __name__ == '__main__':
    main()
