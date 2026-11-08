#!/usr/bin/env python3
"""Offline copied-DATA replay only. Never imports or runs retained Source."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import stat

HERE = Path(__file__).resolve().parent
MANIFEST_SHA256 = '27818022f6714ae2aa03a1608eac1354874f5b49d15dacdc659b6e655430ddad'
LIMIT = 8 * 1024 * 1024
MACRO = '-DNODE_COMPAT_NATIVE_EXPORT_DIAGNOSTIC_V1=1'


def require(value, message):
    if not value:
        raise ValueError(message)


def integer(v):
    return type(v) is int


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pairs(items):
    out = {}
    for k, v in items:
        require(k not in out, 'duplicate JSON key')
        out[k] = v
    return out


def decode(data):
    return json.loads(data.decode('utf-8', errors='strict'), object_pairs_hook=pairs)


def snapshot(path):
    s = path.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
            s.st_mtime_ns, s.st_ctime_ns)


def member(name):
    require(type(name) is str and name and '\\' not in name, 'member spelling')
    p = PurePosixPath(name)
    require(not p.is_absolute() and all(x not in ('', '.', '..') for x in name.split('/')),
            'member escape')
    q = HERE.joinpath(*p.parts)
    require(q.resolve() == q and q.is_relative_to(HERE), 'member alias')
    return q


def inventory():
    files, dirs, stamps = set(), set(), {}
    for base, children, names in os.walk(HERE, followlinks=False):
        p = Path(base)
        require(p.resolve() == p and stat.S_ISDIR(p.lstat().st_mode), 'directory alias')
        dirs.add(p.relative_to(HERE).as_posix())
        for name in children:
            require(stat.S_ISDIR((p / name).lstat().st_mode), 'non-directory member')
        for name in names:
            q = p / name
            s = snapshot(q)
            require(stat.S_ISREG(s[2]) and s[3] == 1 and q.resolve() == q,
                    'nonregular or linked member')
            files.add(q.relative_to(HERE).as_posix())
            stamps[q] = s
    require(len({s[:2] for s in stamps.values()}) == len(stamps), 'inode alias')
    return files, dirs, stamps


def bounded(path, size, stamps):
    require(integer(size) and 0 <= size <= LIMIT, 'read size')
    before = stamps[path]
    require(before[4] == size, 'size before read')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        s = os.fstat(fd)
        require((s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
                 s.st_mtime_ns, s.st_ctime_ns) == before, 'open changed')
        with os.fdopen(fd, 'rb', closefd=False) as f:
            data = f.read(size + 1)
        require(len(data) == size and snapshot(path) == before, 'read changed')
    finally:
        os.close(fd)
    return data


def main():
    require(len(os.sys.argv) == 1, 'no arguments or original-path mode')
    files, dirs, stamps = inventory()
    mp = member('manifest.json')
    require(stamps[mp][4] <= 1024 * 1024, 'manifest cap')
    raw = bounded(mp, stamps[mp][4], stamps)
    require(digest(raw) == MANIFEST_SHA256, 'manifest pin')
    m = decode(raw)
    require(m['schemaVersion'] == 1 and m['state'] == 'RETAINED_NATIVE_EXPORT_FRONTEND_DATA_V1',
            'manifest state')
    rows = m['files']
    require(type(rows) is list and integer(m['fileCount']) and m['fileCount'] == len(rows) == 52,
            'file count')
    require(integer(m['payloadBytes']) and 0 <= m['payloadBytes'] <= LIMIT and
            m['payloadLimitBytes'] == LIMIT, 'payload bound')
    # Validate every recorded size before the first payload read; negatives cannot offset totals.
    for row in rows:
        for k in ('original', 'copy'):
            d = row[k]
            require(type(d) is dict and integer(d['bytes']) and 0 <= d['bytes'] <= LIMIT,
                    'typed per-file bound')
            require(type(d['sha256']) is str and len(d['sha256']) == 64 and
                    all(c in '0123456789abcdef' for c in d['sha256']), 'digest spelling')
        require(row['original']['bytes'] == row['copy']['bytes'] and
                row['original']['sha256'] == row['copy']['sha256'], 'copy equality')
    require(sum(r['copy']['bytes'] for r in rows) == m['payloadBytes'] == 4009463,
            'aggregate bound')
    names = [r['copy']['path'] for r in rows]
    labels = [r['original']['path'] for r in rows]
    require(len(set(names)) == len(names) and len(set(labels)) == len(labels), 'duplicate rows')
    paths = [member(n) for n in names]
    require(all(n.startswith('files/') and n.count('/') == 1 for n in names), 'copy layout')
    require(files == set(names) | {'manifest.json', 'check.py', 'README.md'} and
            dirs == {'.', 'files'}, 'whole local membership')
    data, descriptors = {}, {}
    for row, path in zip(rows, paths):
        b = bounded(path, row['copy']['bytes'], stamps)
        require(digest(b) == row['copy']['sha256'], 'payload hash')
        data[row['original']['path']] = b
        descriptors[row['original']['path']] = row['original']

    def ref(d):
        require(type(d) is dict and d['path'] in data and
                descriptors[d['path']] == {k: d[k] for k in ('path', 'sha256', 'bytes')},
                'retained descriptor join')
        return data[d['path']]

    def obj(d):
        return decode(ref(d))

    def label(p):
        require(p in data, 'selected role absent')
        return decode(data[p])

    def dlabel(p):
        require(p in descriptors, 'selected descriptor absent')
        return descriptors[p]

    roles, work = m['roles'], m['workLabels']
    review = label(roles['review'])
    require(review['state'] == 'COORDINATED_NATIVE_EXPORT_DIAGNOSTIC_FRONTEND_DATA_REVIEW_PASSED_V1'
            and review['verifiedPassed'] is True and review['bothMacroModesFrontendPassed'] is True,
            'primary documentary state')
    for k, p in roles.items():
        if k in review['roles']:
            require(review['roles'][k] == dlabel(p), 'primary role')
    for row in review['finiteEvidence']:
        if row['path'] in data:
            ref(row)
        else:
            require(row in m['omittedDescriptors'], 'unaccounted omission')
    for k, v in review['scope'].items():
        require(v is (k in ('frontendOnly', 'syntaxOnly')), 'frontend scope')

    auths, results = {}, {}
    for version, expected in [('v1', 1), ('v2', 0)]:
        base = work[version]
        a = label(base + '/authority.json')
        r = label(base + '/result.json')
        auths[version], results[version] = a, r
        require(a['state'] == 'ROOT_NATIVE_EXPORT_DIAGNOSTIC_FRONTENDS_PREPARED_V1' and
                a['frontendCompilationAllowed'] is True and
                a['objectOrEngineOrGuestExecutionAllowed'] is False and
                a['secondsPerCommand'] == 120, 'frontend authority')
        require(r['state'] == 'NATIVE_EXPORT_DIAGNOSTIC_FRONTEND_RESULTS_V1' and
                r['authority'] == dlabel(base + '/authority.json') and
                r['passed'] is (expected == 0) and r['originalInputsPreserved'] is True and
                r['objectLinked'] is False and r['engineOrGuestExecuted'] is False, 'result')
        for k in ('candidate', 'cpp', 'header', 'controller', 'fullGuard', 'monitor', 'baseBuildReview'):
            ref(a[k])
        require([c['mode'] for c in a['commands']] == ['off', 'on'] and
                [c['mode'] for c in r['commands']] == ['off', 'on'], 'mode order')
        for ac, rc in zip(a['commands'], r['commands']):
            md = base + '/macro-' + ac['mode']
            start, terminal = label(md + '/started.json'), label(md + '/terminal.json')
            own = label(md + '/owned-0000.json')
            require(rc['argv'] == ac['argv'] == start['argv'] and
                    rc['terminal'] == dlabel(md + '/terminal.json') and
                    rc['rawExitCode'] == expected and rc['passed'] is (expected == 0), 'command join')
            owner(start, terminal, own, dlabel(base + '/authority.json'), expected, 120,
                  dlabel(md + '/stdout.log'), dlabel(md + '/stderr.log'))
            require(ref(terminal['stdout']) == b'', 'frontend stdout')
            err = ref(terminal['stderr'])
            require((b"fatal error: 'optional' file not found" in err) if expected else err == b'',
                    'preserved failure or clean success stderr')
        require(m['originalDirectoryMembership'][base] == sorted(
            ['authority.json', 'result.json', 'macro-off', 'macro-on'] +
            ['macro-' + mode + '/' + name for mode in ('off', 'on') for name in
             ('started.json', 'terminal.json', 'owned-0000.json', 'stdout.log', 'stderr.log')]),
            'complete historical frontend membership')

    a, old = auths['v2'], auths['v1']
    require(a['commands'] == old['commands'] and a['cpp'] == old['cpp'] and
            a['header'] == old['header'] and a['originalCommand'] == old['originalCommand'],
            'same source and commands across attempts')
    original = shlex.split(a['originalCommand'])
    require(original[-2] == '-c' and original[-1].endswith('/embedding/embedding.cpp'), 'old compile shape')
    removals = [['-MD'], ['-MT', 'CMakeFiles/builtin_componentize_embedding.dir/embedding/embedding.cpp.obj'],
                ['-MF', 'CMakeFiles/builtin_componentize_embedding.dir/embedding/embedding.cpp.obj.d'],
                ['-o', 'CMakeFiles/builtin_componentize_embedding.dir/embedding/embedding.cpp.obj']]
    require(a['removedOutputArguments'] == old['removedOutputArguments'] == removals, 'output removal policy')
    derived = list(original)
    for tokens in removals:
        at = [i for i in range(len(derived)) if derived[i:i+len(tokens)] == tokens]
        require(len(at) == 1, 'unique output removal')
        del derived[at[0]:at[0]+len(tokens)]
    derived[-1] = a['cpp']['path']
    derived[-2:-2] = ['-iquote', a['header']['path'].rsplit('/', 1)[0], '-fsyntax-only']
    off, on = a['commands'][0]['argv'], a['commands'][1]['argv']
    require(off == derived and on == off[:-2] + [MACRO] + off[-2:] and
            not any('NODE_COMPAT_NATIVE_EXPORT_DIAGNOSTIC_V1' in s for s in off) and
            on.count(MACRO) == 1 and '-fsyntax-only' in off and '--target=wasm32-wasi' in off,
            'exact derived frontend argv and sole macro difference')
    require(review['roles']['actualResult'] == dlabel(work['v2'] + '/result.json') and
            review['roles']['rootAuthority'] == dlabel(work['v2'] + '/authority.json') and
            review['priorAttempt']['actualResult'] == dlabel(work['v1'] + '/result.json') and
            review['priorAttempt']['authority'] == dlabel(work['v1'] + '/authority.json') and
            review['priorAttempt']['oldRawFailuresRemainFailed'] is True, 'review attempt joins')
    for c, rc in zip(review['commands'], results['v2']['commands']):
        t = obj(c['terminal'])
        require(c['argv'] == rc['argv'] and c['terminal'] == rc['terminal'] and
                c['rawExitCode'] == 0 and c['secondsCap'] == 120 and c['pid'] == t['pid'] and
                c['stdout'] == t['stdout'] and c['stderr'] == t['stderr'], 'review command joins')
        obj(c['started'])
        for d in c['ownedRecords']:
            obj(d)

    driver = work['driver']
    da, ds, dt, dw = [label(driver + '/' + n) for n in
                      ('authority.json', 'started.json', 'terminal.json', 'owned-0000.json')]
    expected_driver = [off[0], '--target=wasm32-wasi', '-###', '-x', 'c++', '-fsyntax-only', '/dev/null']
    require(da['argv'] == ds['argv'] == expected_driver, 'exact driver-only observation argv')
    owner(ds, dt, dw, dlabel(driver + '/authority.json'), 0, 30,
          dlabel(driver + '/stdout.log'), dlabel(driver + '/stderr.log'))
    dr = ref(dt['stderr'])
    require(ref(dt['stdout']) == b'' and b'clang version 21.1.4-wasi-sdk' in dr and
            b'"-cc1"' in dr and b'"-fsyntax-only"' in dr, 'printed driver observation')
    require(m['originalDirectoryMembership'][driver] == sorted(
        ['authority.json', 'started.json', 'terminal.json', 'owned-0000.json', 'stdout.log', 'stderr.log']),
        'driver historical membership')

    repair, inv = label(roles['sdkDirectoryRepair']), label(roles['sdkInventory'])
    require(a['sdkDirectoryRepair'] == dlabel(roles['sdkDirectoryRepair']) and
            repair['inventory'] == a['sdkInventory'] == dlabel(roles['sdkInventory']) and
            repair['state'] == 'PINNED_SDK_EMPTY_DIRECTORY_DRIFT_VERIFIED_V1', 'repair roles')
    entries = inv['entries']
    require(type(entries) is list and len({x['path'] for x in entries}) == len(entries), 'inventory membership')
    declared_files = [x for x in entries if x['kind'] == 'file']
    require(len(declared_files) == repair['hashedFiles'] == 10114 and
            sum(x['bytes'] for x in declared_files) == repair['hashedBytes'] == 366304928,
            'documentary SDK counts')
    paths = ['share/wasi-sysroot/include/c++', 'share/wasi-sysroot/include/c++/v1']
    lookup = {x['path']: x for x in entries}
    require(repair['root'] == inv['root'] and repair['missing'] == paths and
            repair['extra'] == repair['changed'] == [] and
            repair['payloadsMutated'] is False and repair['logicalMembershipAndModesRestored'] is True and
            repair['historicalDirectoryInodesNotClaimed'] is True and
            repair['archiveEmptyDirectoryWitnessTool'] == '97825a', 'documentary repair assertions')
    for p, restored in zip(paths, repair['restored']):
        oldrow = lookup[p]
        require(oldrow['kind'] == 'directory' and restored['path'] == p and
                restored['mode'] == oldrow['mode'] == 493 and restored['newPhysicalIdentity'] is True and
                (restored['dev'], restored['ino']) != (oldrow['dev'], oldrow['ino']), 'new directory identity')
    require([x['path'] for x in entries if x['path'].startswith(paths[0] + '/')] == [paths[1]],
            'documentary empty directory inventory')
    require(review['sdk']['reviewerRescannedSdkPayloads'] is False and
            review['sdk']['repair'] == dlabel(roles['sdkDirectoryRepair']) and
            review['sdk']['inventory'] == dlabel(roles['sdkInventory']), 'SDK delegation')

    native = label(roles['nativeSourceIndex'])
    require(native['payloadFiles'] == 8 and native['payloadBytes'] == 80289 and
            native['enabledByDefault'] is False, 'native Source-only family')
    source_root = roles['nativeSourceIndex'].rsplit('/', 1)[0]
    for row in native['files']:
        p = PurePosixPath(row['path'])
        require(not p.is_absolute() and '..' not in p.parts, 'indexed Source member')
        require(dlabel(source_root + '/' + row['path']) == dict(row, path=source_root + '/' + row['path']),
                'native indexed member')
    require(native['embeddingOverlay']['after'] == a['cpp'] and
            native['actualNativeBuild'] is None and native['actualFrontend'] is None,
            'historical Source cutoff stays historical')
    require(m['historicalModesAndInodesDocumentary'] is True and
            m['scope']['sdkPayloadsRehashedByCurator'] is False and
            m['scope']['runtimeAccepted'] is False, 'retention scope')
    require(inventory()[:2] == (files, dirs) and all(snapshot(p) == s for p, s in stamps.items()),
            'whole current read bookend')
    print(json.dumps({'passed': True, 'files': len(rows), 'payloadBytes': m['payloadBytes'],
                      'frontendRawCodes': [1, 1, 0, 0], 'driverRawCode': 0,
                      'sdkDeclaredFiles': 10114, 'sdkPayloadsRead': 0,
                      'compilerOrHelperExecuted': False, 'runtimeAccepted': False}, sort_keys=True))


def owner(start, terminal, owned, authority, code, seconds, stdout, stderr):
    require(start['authority'] == terminal['authority'] == authority and
            start['pid'] == terminal['pid'] and start['timeoutSeconds'] == seconds and
            terminal['rawExitCode'] == code and type(terminal['rawExitCode']) is int,
            'original owner identity/cap/code')
    for k in ('timeout', 'forcedCleanup'):
        require(terminal[k] is False, 'owner timeout or forced cleanup')
    for k in ('parentOwnedGroupGone', 'allObservedOwnedGroupsGone'):
        require(terminal[k] is True, 'groups not gone')
    for k in ('interruptedSignals', 'remainingObservedPids', 'signals', 'errors'):
        require(terminal[k] == [], 'owner errors')
    require(terminal['stdout'] == stdout and terminal['stderr'] == stderr and
            len(terminal['observedProcesses']) == 1 and owned['sequence'] == 0 and
            owned['process'] == terminal['observedProcesses'][0] and
            owned['process']['pid'] == terminal['pid'], 'original owned frame and streams')
    require(all(g['alive'] is False and g['signalAllowed'] is False for g in terminal['finalGroups']),
            'final group state')


if __name__ == '__main__':
    main()
