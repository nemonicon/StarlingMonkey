"""Root: retain the completed V4 pair's finite evidence, not application/build trees.

Only run after both original owners have stopped and their final data is reviewed.
Absolute source paths in the resulting index are provenance keys for offline checks.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = HERE / 'raw-records'


def stamp(path):
    s = path.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def read(path, cap=20 * 1024**2):
    assert path.is_absolute() and path.resolve() == path
    before = stamp(path)
    assert stat.S_ISREG(before[2]) and before[3] == 1 and 0 <= before[4] <= cap
    with path.open('rb') as f:
        raw = f.read(cap + 1)
    assert len(raw) == before[4] and stamp(path) == before
    return raw


def row(path):
    raw = read(path)
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def document(path):
    return json.loads(read(path))


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use nonoptimized Python -I -B; checks must remain enabled')
    assert not ROOT.exists()
    preparation = document(HERE / 'control-preparation.json')
    binding = document(HERE / 'runtime-bindings.json')
    sources = []
    paths = set()

    def select(path, destination):
        path = Path(path)
        if str(path) in paths:
            return
        assert type(destination) is str and not Path(destination).is_absolute() and '..' not in Path(destination).parts
        paths.add(str(path))
        sources.append((path, 'files/' + destination))

    for trial in preparation['trials']:
        arm = trial['arm']
        owner = document(HERE / (arm + '-owner-result.json'))
        assert owner['cleanOwner'] and owner['finalInputsPreserved'] and owner['error'] is None
        assert owner['secondaryErrors'] == [] and type(owner['rawExitCode']) is int and owner['rawExitCode'] in (0, 1)
        work, owned = Path(trial['outputRoot']), Path(trial['ownerOutputRoot'])
        terminal = document(owned / 'terminal.json')
        assert terminal['pid'] == owner['originalOwner'] and terminal['rawExitCode'] == owner['rawExitCode']
        assert not terminal['timeout'] and not terminal['forcedCleanup']
        assert terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone']
        assert all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
        for path in sorted(owned.rglob('*')):
            assert not path.is_symlink()
            if path.is_file():
                select(path, arm + '/owner/' + path.relative_to(owned).as_posix())
        # Deliberately exclude copies of the app, caches and host compilation caches.
        for path in sorted(work.iterdir()):
            if path.is_file():
                select(path, arm + '/work/' + path.name)
        for path in sorted((work / 'client').rglob('*')):
            assert not path.is_symlink()
            if path.is_file():
                select(path, arm + '/work/' + path.relative_to(work).as_posix())
        if arm == 'cloud':
            select(work / 'project/.wash/config.json', arm + '/work/project/.wash/config.json')
        actual = document(work / 'result.json')
        if arm == 'cloud':
            generations = [Path(r['path']) for r in actual['cacheInventory'] if r['path'].endswith('/generation.json')]
        else:
            generations = sorted((work / 'application/.next/cache').rglob('generation.json'))
        assert len(generations) == 1
        select(generations[0], arm + '/callback/generation.json')

    # Capture Root decisions and execution receipts as they exist at this cut.
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.suffix in ('.json', '.py', '.md', '.stdout', '.stderr', '.log'):
            select(path, 'root/' + path.name)
    for key in ('actorIndex', 'clientIndex', 'browserIndex'):
        index_path = Path(binding[key]['path'])
        assert row(index_path) == binding[key]
        index = document(index_path)
        select(index_path, 'source/' + index_path.parent.name + '/index.json')
        for item in index['files']:
            path = index_path.parent / item['path']
            assert row(path) == dict(item, path=str(path))
            select(path, 'source/' + index_path.parent.name + '/' + item['path'])
    client = document(Path(binding['clientIndex']['path']).with_name('plan.json'))
    for key, ref in client['sourceRequirements'].items():
        assert row(Path(ref['path'])) == ref
        select(ref['path'], 'consumer-inputs/' + key + '/' + Path(ref['path']).name)
    browser = document(Path(binding['browserIndex']['path']).with_name('plan.json'))
    # Current action manifest and exact composition are small prerequisite evidence.
    for label, ref in [('action-manifest', browser['actualActionManifest']),
                       ('next-composition', binding['compositionReview'])]:
        assert row(Path(ref['path'])) == ref
        select(ref['path'], 'proofs/' + label + '.json')
    tools = document(Path(binding['selectedHostTools']['path']))
    select(binding['selectedHostTools']['path'], 'proofs/browser-tool-selection.json')
    tuple_command = document(HERE / 'public-tuple-command.json')
    select(tuple_command['analyzer']['path'], 'analysis/admit-v4-public-tuple.py')
    for command in tools['commands']:
        for stream in ('stdout', 'stderr'):
            ref = command[stream]
            assert row(Path(ref['path'])) == ref
            select(ref['path'], 'host-tools/' + command['label'] + '.' + stream)

    assert 0 < len(sources) <= 1024 and len({relative for _, relative in sources}) == len(sources)
    ROOT.mkdir()
    records, total = [], 0
    for path, relative in sorted(sources, key=lambda item: item[1]):
        raw = read(path)
        total += len(raw)
        assert total <= 64 * 1024**2
        ref = dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        dest = ROOT / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('xb') as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        assert read(dest) == raw and row(path) == ref
        records.append(dict(path=relative, sha256=ref['sha256'], bytes=ref['bytes'], original=ref))
    index = dict(schemaVersion=1, state='RETAINED_V4_FULL_RUNTIME_PAIR_DATA_V1', originalRoot=str(HERE),
                 files=records, payloadFiles=len(records), totalBytes=total,
                 scope='Saved original pair; no fresh runtime or wider compatibility acceptance',
                 omitted=['application copies', 'build trees', 'host caches', 'Playwright package bytes'],
                 fullNextAccepted=False)
    with (ROOT / 'index.json').open('x') as f:
        json.dump(index, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(index=row(ROOT / 'index.json'), payloadFiles=len(records), totalBytes=total)))


if __name__ == '__main__':
    main()
