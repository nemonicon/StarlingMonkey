"""Replay the selected Node reference DATA; never invoke Node or a component."""
import argparse
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent


def physical(path):
    s = path.stat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current', action='store_true')
    args = parser.parse_args()
    index = json.loads((HERE / 'retained-index.json').read_text())
    members = index['members']
    assert len(members) == index['memberCount'] == 15
    assert sum(r['original']['bytes'] for r in members) == index['bytes']
    assert len({r['path'] for r in members}) == len({r['original']['path'] for r in members}) == len(members)
    expected = {r['path'] for r in members}
    assert {p.relative_to(HERE).as_posix() for p in (HERE / 'retained').rglob('*') if p.is_file()} == expected
    by_original = {}
    before = []
    for r in members:
        relative = Path(r['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        path = HERE / relative
        assert path.resolve() == path and not path.is_symlink() and path.stat().st_nlink == 1
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == r['original']['sha256'] and len(data) == r['original']['bytes']
        assert stat.S_IMODE(path.stat().st_mode) == r['mode']
        by_original[r['original']['path']] = (r['original'], data)
        if args.current:
            original = Path(r['original']['path'])
            assert original.resolve() == original and all(not p.is_symlink() for p in (original, *original.parents))
            snapshot = physical(original)
            assert stat.S_ISREG(snapshot[2]) and snapshot[3] == 1 and stat.S_IMODE(snapshot[2]) == r['mode']
            assert original.read_bytes() == data and physical(original) == snapshot
            before.append((original, snapshot))

    def obj(name):
        return json.loads((HERE / 'retained' / name).read_text())

    def ref(value):
        descriptor, data = by_original[value['path']]
        assert descriptor == value
        return data

    result = obj('result.json')
    authority = obj('authority.json')
    terminal = obj('owned-monitor/terminal.json')
    started = obj('owned-monitor/started.json')
    assert result['passed'] is result['ownedClean'] is result['fixturesPreserved'] is True
    assert result['guestExecuted'] is result['guardOrInteropAccepted'] is False
    assert type(result['rawExitCode']) is type(terminal['rawExitCode']) is int
    assert result['rawExitCode'] == terminal['rawExitCode'] == 0
    assert terminal['timeout'] is terminal['forcedCleanup'] is False
    assert terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    assert all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    assert ref(result['authority']) == ref(terminal['authority']) == (HERE / 'retained/authority.json').read_bytes()
    assert ref(result['terminal']) == (HERE / 'retained/owned-monitor/terminal.json').read_bytes()
    assert started['pid'] == terminal['pid'] and started['authority'] == terminal['authority']
    assert started['timeoutSeconds'] == authority['capSeconds'] == 120
    assert authority['node']['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    assert started['argv'] == [authority['node']['path'], authority['control']['path'], str(Path(result['authority']['path']).parent / 'fixtures')]
    assert ref(terminal['stderr']) == b''
    output = json.loads(ref(terminal['stdout']))
    assert output['node'] == 'v22.14.0'
    for key in ['builtinJoinSame', 'naturalFileUrlImportSucceeded', 'defaultSameRequireExports', 'repeatedNamespaceSame', 'cacheLoaded', 'namespacePrototypeNull', 'hostCanonicalFileUrlUsedInsteadOfGuestProbePath']:
        assert output[key] is True
    assert output['namespaceOwnNames'] == ['default']
    assert output['guardRefusalIsNodeParity'] is output['interopProfileFullParityClaimed'] is False
    assert len(authority['fixtures']) == 8
    for copy in authority['fixtures']:
        assert ref(copy['target']) and copy['source']['sha256'] == copy['target']['sha256']
    snapshots = [obj('owned-monitor/' + p.name) for p in sorted((HERE / 'retained/owned-monitor').glob('owned-*.json'))]
    assert [r['sequence'] for r in snapshots] == list(range(len(snapshots)))
    assert [r['process'] for r in snapshots] == terminal['observedProcesses']
    for original, snapshot in before:
        assert physical(original) == snapshot
    print(json.dumps(dict(state='PINNED_NODE_FILEURL_REFERENCE_DATA_REPLAY_PASSED_V1', members=len(members),
        currentOriginals=args.current, naturalImportSucceeded=True, guestExecuted=False, guardOrInteropAccepted=False)))


if __name__ == '__main__':
    main()
