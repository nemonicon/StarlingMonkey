"""Retain a finite set of completed guarded-build text DATA; never run tools."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import stat
import tarfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
WORK = Path('/private/tmp/starling-node-compat/next-native-intl-build-guard825-first')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def physical(path):
    s = path.stat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def main():
    records = []
    payload = {}
    roles = {}
    originals = {}

    def add(name, path, role=None):
        path = Path(path)
        assert path.is_absolute() and path.resolve() == path
        assert all(not p.is_symlink() for p in (path, *path.parents))
        before = physical(path)
        assert stat.S_ISREG(before[2]) and before[3] == 1
        data = path.read_bytes()
        assert physical(path) == before
        data.decode('utf-8')
        assert b'\0' not in data
        ref = dict(path=str(path), sha256=digest(data), bytes=len(data))
        if str(path) in originals:
            prior = originals[str(path)]
            assert prior['original'] == ref
            if role:
                roles[role] = prior['member']
            return
        assert name not in payload
        entry = dict(member=name, original=ref, mode=stat.S_IMODE(before[2]), physicalBefore=before)
        records.append(entry)
        originals[str(path)] = entry
        payload[name] = data
        if role:
            roles[role] = name

    def tree(prefix, root):
        root = Path(root)
        nodes = sorted(root.rglob('*'))
        assert not any(p.is_symlink() for p in nodes)
        assert all(p.is_file() or p.is_dir() for p in nodes)
        for path in nodes:
            if path.is_file():
                add(prefix + '/' + path.relative_to(root).as_posix(), path)

    for name in ['result.json', 'metadata.json', 'root-authority.json', 'configured-inputs.json',
                 'protection-before.json', 'environment-policy.json']:
        add('native/work/' + name, WORK / name, name.removesuffix('.json'))
    outer = Path(str(WORK) + '-root-monitor')
    tree('native/outer', outer)
    roles['outer-terminal'] = originals[str(outer / 'terminal.json')]['member']
    roles['outer-observation'] = originals[str(outer / 'observation.json')]['member']
    tree('native/results', WORK / 'results')
    for name in ['compile_commands.json', 'CMakeCache.txt', 'starling-raw.wasm/Cargo.toml',
                 'starling-raw.wasm/Cargo.lock', 'starling-raw.wasm/null.cpp']:
        add('native/configured/' + name, WORK / 'build' / name)
    native = json.loads(payload[roles['metadata']])
    authority = json.loads(payload[roles['root-authority']])
    for role, entry in authority['reusedTrees'].items():
        add('inputs/tree-inventories/' + role + '.json', Path(entry['inventory']['path']))
    for key in ['portableCargoSelection', 'sourceComposition', 'patchedSpiderMonkeyEvidence']:
        add('inputs/' + key + '.json', Path(native[key]['path']))
    for family in ['next-module-fileurl-boundary-candidate-v1', 'next-native-portable-source-v2',
                   'next-native-portable-build-preparation-v4', 'next-native-portable-generator-check-v2']:
        root = BASE / family
        index = json.loads((root / 'index.json').read_text())
        add('source/' + family + '/index.json', root / 'index.json')
        for item in index['files']:
            assert not Path(item['path']).is_absolute() and '..' not in Path(item['path']).parts
            add('source/' + family + '/' + item['path'], root / item['path'])
            assert originals[str(root / item['path'])]['original'] == dict(item, path=str(root / item['path']))
    for name in ['actual-build-review.json', 'actual-build-source-review.json', 'actual-build-primary-lane.json',
                 'review-build-data.py', 'launch.py', 'build.stdout.log', 'build.stderr.log']:
        add('root/' + name, HERE.parent / name, name.removesuffix('.json'))
    assert len(records) <= 4000 and sum(len(v) for v in payload.values()) <= 64 * 1024**2
    archive_bytes = io.BytesIO()
    with gzip.GzipFile(fileobj=archive_bytes, mode='wb', mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode='w') as tf:
            for item in records:
                data = payload[item['member']]
                info = tarfile.TarInfo(item['member'])
                info.size = len(data)
                info.mode = item['mode']
                info.mtime = 0
                tf.addfile(info, io.BytesIO(data))
    for item in records:
        assert physical(Path(item['original']['path'])) == item['physicalBefore']
    data = archive_bytes.getvalue()
    index = dict(schemaVersion=1, state='GUARDED_FULL_NATIVE_BUILD_FINITE_TEXT_DATA_V1',
        archive=dict(path='data.tar.gz', sha256=digest(data), bytes=len(data)),
        memberCount=len(records), expandedBytes=sum(len(v) for v in payload.values()),
        roles=roles, members=records, allReadPhysicalBookendsUnchanged=True,
        binariesRetained=False, sourcePayload825Retained=False, toolsExecuted=False,
        scope='Selected original text DATA only; engine/library/tool binaries and825 source payloads excluded.')
    for name, content in [('data.tar.gz', data), ('payload-index.json', (json.dumps(index, indent=2) + '\n').encode())]:
        with (HERE / name).open('xb') as handle:
            handle.write(content)
    print(json.dumps({k: index[k] for k in ['state', 'archive', 'memberCount', 'expandedBytes', 'scope']}))


if __name__ == '__main__':
    main()
