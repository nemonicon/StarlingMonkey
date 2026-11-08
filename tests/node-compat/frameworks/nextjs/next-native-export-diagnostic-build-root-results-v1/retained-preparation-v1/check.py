#!/usr/bin/env python3
"""Offline copied-DATA replay only. Never imports or runs retained Source."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import stat

HERE = Path(__file__).resolve().parent
MANIFEST_SHA256 = '77248dd3ac0c123de007e9c8ba365a6b2ef4275d06e8804de14e4733380e434f'
LIMIT = 8 * 1024 * 1024


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


def clean(t):
    return (type(t['rawExitCode']) is int and t['rawExitCode'] == 0 and
            t['timeout'] is t['forcedCleanup'] is False and
            t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True and
            all(t[k] == [] for k in ('interruptedSignals', 'signals', 'errors', 'remainingObservedPids')) and
            all(g['alive'] is False for g in t['finalGroups']))


def fingerprint(rows):
    values = [{k: r[k] for k in ('role', 'path', 'sha256', 'bytes', 'mode')} for r in rows]
    values.sort(key=lambda r: (r['role'], r['path']))
    return digest(json.dumps(values, sort_keys=True, separators=(',', ':')).encode())


def main():
    require(len(os.sys.argv) == 1, 'No arguments or original-path mode')
    files, dirs, stamps = inventory()
    mp = member('manifest.json')
    require(stamps[mp][4] <= 1024**2, 'manifest bound')
    raw = bounded(mp, stamps[mp][4], stamps)
    require(digest(raw) == MANIFEST_SHA256, 'manifest pin')
    m = decode(raw)
    require(m['schemaVersion'] == 1 and m['state'] == 'RETAINED_MATERIALIZATION_AND_INSTALLED_GENERATORS_DATA_V1',
            'manifest state')
    rows = m['files']
    require(type(rows) is list and integer(m['fileCount']) and m['fileCount'] == len(rows) == 115,
            'typed file count')
    require(integer(m['payloadBytes']) and 0 <= m['payloadBytes'] <= LIMIT and
            integer(m['payloadLimitBytes']) and m['payloadLimitBytes'] == LIMIT, 'aggregate type/bound')
    # Validate ALL row sizes before opening ANY retained payload; negative later rows cannot offset a sum.
    for r in rows:
        for k in ('copy', 'original'):
            d = r[k]
            require(type(d) is dict and type(d['path']) is str and integer(d['bytes']) and
                    0 <= d['bytes'] <= LIMIT and type(d['sha256']) is str and len(d['sha256']) == 64 and
                    all(c in '0123456789abcdef' for c in d['sha256']), 'typed per-file bound/digest')
        require(r['original']['bytes'] == r['copy']['bytes'] and
                r['original']['sha256'] == r['copy']['sha256'], 'copy equality')
    require(sum(r['copy']['bytes'] for r in rows) == m['payloadBytes'] == 6123766, 'aggregate equality/bound')
    names, labels = [r['copy']['path'] for r in rows], [r['original']['path'] for r in rows]
    require(len(set(names)) == len(names) and len(set(labels)) == len(labels), 'unique rows')
    require(all(n.startswith('files/') and n.count('/') == 1 for n in names), 'copy layout')
    require(files == set(names) | {'manifest.json', 'check.py', 'README.md'} and dirs == {'.', 'files'},
            'whole current membership')
    data, descriptors = {}, {}
    for r in rows:
        b = bounded(member(r['copy']['path']), r['copy']['bytes'], stamps)
        require(digest(b) == r['copy']['sha256'], 'copied payload hash')
        data[r['original']['path']], descriptors[r['original']['path']] = b, r['original']

    def ref(d):
        require(type(d) is dict and d['path'] in data and
                descriptors[d['path']] == {k: d[k] for k in ('path', 'sha256', 'bytes')}, 'descriptor/role join')
        return data[d['path']]

    def obj(d):
        return decode(ref(d))

    def label(p):
        require(p in data, 'selected label absent')
        return decode(data[p])

    def dlabel(p):
        require(p in descriptors, 'selected descriptor absent')
        return descriptors[p]

    role = m['roles']
    result, body = label(role['actualResult']), label(role['bodyResult'])
    authority = label(role['rootAuthority'])
    gr, mr = label(role['generatorReview']), label(role['materializationReview'])
    source_index = label(role['generatorSourceIndex'])
    source_root = role['generatorSourceIndex'].rsplit('/', 1)[0]
    plan = label(source_root + '/plan.json')
    selection, summary, composition = [label(role[k]) for k in
                                      ('portableSelection', 'materializationSummary', 'composition')]
    parent = label(role['parentRoleTable'])
    require(gr['state'] == 'INDEPENDENT_NATIVE_EXPORT_DIAGNOSTIC_GENERATOR_DATA_REVIEW_PASSED_V1' and
            gr['verifiedPassed'] is gr['generatorChecksPassed'] is True, 'independent generator review')
    require(mr['verifiedPassed'] is mr['sourceOnlyMaterializationVerified'] is True, 'materialization review')
    for k in ('actualResult', 'bodyResult', 'composition', 'materializationSummary', 'portableSelection', 'rootAuthority'):
        require(gr['roles'][k] == dlabel(role[k]), 'generator review role')
    require(gr['roles']['sourceIndex'] == authority['sourceIndex'] == result['sourceIndex'] ==
            dlabel(role['generatorSourceIndex']) and gr['roles']['plan'] == authority['plan'] ==
            result['plan'] == dlabel(source_root + '/plan.json'), 'actual Source/plan joins')
    require(mr['roles']['composition'] == dlabel(role['composition']) and
            mr['roles']['sourceMaterialization'] == dlabel(role['materializationSummary']) and
            mr['roles']['baselineParentSelectedRoleTable'] == dlabel(role['parentRoleTable']), 'materialization roles')
    for k, v in gr['reviewScope'].items():
        require(v is False, 'generator review no-build/no-runtime scope')
    require(mr['scope']['copyOnly'] is True and all(v is False for k, v in mr['scope'].items() if k != 'copyOnly'),
            'materialization review scope')
    require(authority['state'] == 'ROOT_PORTABLE_NEXT_GENERATORS_AUTHORIZED_V1' and authority['unissued'] is False and
            authority['generatorChecksAllowed'] is authority['nodeHostSourceOnly'] is True and
            all(authority[k] is False for k in ('nativeBuildAllowed', 'compilerAllowed', 'cmakeAllowed',
                'cargoAllowed', 'engineAllowed', 'guestAllowed', 'networkAllowed', 'copySourceAllowed')),
            'generator-only authority')
    require(authority['portableSelection'] == dlabel(role['portableSelection']) and
            result['rootAuthority'] == dlabel(role['rootAuthority']), 'authority/selection joins')
    require(result['state'] == body['state'] == 'ACTUAL_PORTABLE_NEXT_INSTALLED_GENERATORS_CHECKED_V1' and
            result['passed'] is body['passed'] is True and result['bodyResult'] == dlabel(role['bodyResult']), 'completed result')
    require(all(result[k] == v for k, v in body.items()), 'body/final result exact common fields')
    require(all(result[k] is None for k in ('primaryError', 'finalProtectionError', 'toolProtectionError', 'outerOwnerError')),
            'preserved error fields')
    require(all(result[k] is True for k in ('sourceBeforeAfterUnchanged', 'portableInputsPreserved', 'toolInputsPreserved',
        'outerInputsPreserved', 'outerOwnedGroupsClean', 'outputCapSatisfied')) and result['nativeOrGuestExecuted'] is False,
        'recorded success and scope')
    require(result['toolInputsBefore'] == result['toolInputsAfter'] and
            result['outerToolInputsBefore'] == result['outerToolInputsAfter'], 'recorded tool equality only')

    # Reconstruct recorded role/content tables; the 825 source payloads are intentionally NOT opened.
    table = selection['files']
    require(len(table) == len({(r['role'], r['path']) for r in table}) == 825, 'whole recorded role roster')
    counts = {k: sum(r['role'] == k for r in table) for k in
              ('native-policy-source', 'build-support', 'componentize-embedding')}
    require(counts == selection['roleCounts'] == summary['roleCounts'] == plan['expectedRoleCounts'] ==
            {'native-policy-source': 435, 'build-support': 387, 'componentize-embedding': 3}, 'role counts')
    require(sum(r['bytes'] for r in table) == summary['bytes'] == mr['copiedPayloadBytes'] == 7562493 and
            fingerprint(table) == selection['roleContentSha256'] == summary['roleContentSha256'] ==
            result['roleContentSha256'] == plan['roleContentSha256'] == mr['roleContentSha256'], 'recorded full fingerprint')
    require(selection['sourceMaterialization'] == plan['materializationSummary'] == dlabel(role['materializationSummary']) and
            selection['composition'] == summary['composition'] == result['composition'] == plan['composition'] ==
            dlabel(role['composition']), 'materialization descriptor joins')
    require(result['materializationSummary'] == dlabel(role['materializationSummary']) and
            result['sourceRoot'] == selection['sourceRoot'] == plan['sourceRoot'] == composition['sourceRoot'], 'source roots')
    for doc, flags in [(selection, ('engineBuilt', 'guestExecuted', 'historicalMetadataProjected')),
                       (summary, ('compilerOrGuestExecuted', 'generatedBuildMetadataProjected')),
                       (composition, ('engineBuilt', 'guestExecuted', 'legacyMetadataProjected'))]:
        require(all(doc[k] is False for k in flags), 'recorded no-build/no-runtime flags')
    native = [r for r in table if r['role'] == 'native-policy-source']
    require(len(composition['files']) == composition['nativeSourceFiles'] == 435 and
            sorted((r['path'], r['sha256'], r['bytes']) for r in composition['files']) ==
            sorted((r['path'], r['sha256'], r['bytes']) for r in native), '435 composition equality')
    require(result['sourceBefore'] == result['sourceAfter'] == [dict(path=result['sourceRoot'] + '/' + r['path'],
        sha256=r['sha256'], bytes=r['bytes']) for r in sorted(native, key=lambda x: x['path'])], '435 recorded hash equality')
    require(result['wholePortableBefore'] == result['wholePortableAfter'] == selection['physicalRecords'] and
            len(selection['physicalRecords']) == 825 and
            result['portableDirectoriesBefore'] == result['portableDirectoriesAfter'] == selection['directoryRecords'],
            'recorded physical/namespace before-after equality (historical only)')
    directories = {'native-policy-source': 'source', 'build-support': 'build-support', 'componentize-embedding': 'componentize-source'}
    materialized_root = summary['outputRoot']
    expected_copies = {}
    for c in summary['filesCopied']:
        key = (c['role'], c['relativePath'])
        require(key not in expected_copies and c['source']['path'] == materialized_root + '/' +
                directories[c['role']] + '/' + c['relativePath'], 'recorded materialization target path')
        expected_copies[key] = c
    require(len(expected_copies) == summary['files'] == 825, '825 copy records')
    physical = {r['path']: r for r in selection['physicalRecords']}
    require(len(physical) == 825, 'unique recorded physical roster')
    for r in table:
        c = expected_copies[(r['role'], r['path'])]
        require(c['mode'] == r['mode'] and all(c['source'][k] == r[k] for k in ('sha256', 'bytes')),
                'recorded role/copy equality')
        pr = physical[c['source']['path']]
        require(pr['bytes'] == r['bytes'] and pr['mode'] == r['mode'] and pr['nlink'] == 1, 'recorded physical mode/size')
    old = {(r['role'], r['path']): r for r in parent['files']}
    new = {(r['role'], r['path']): r for r in table}
    require(set(old) == set(new), 'same parent role membership')
    changed = [k for k in new if old[k] != new[k]]
    require(set(changed) == {('componentize-embedding', 'CMakeLists.txt'),
                            ('componentize-embedding', 'embedding/embedding.cpp')} and
            mr['unchangedParentRoleRows'] == 823, 'two overlays/823 unchanged recorded rows')
    for c in mr['actualChangedRoleRows']:
        key = (c['after']['role'], c['after']['path'])
        require(c['after'] == new[key] and c['before'] == old[key], 'reviewed overlay rows')
    require(len(mr['copies']) == mr['copiedFiles'] == 825, 'review copy roster')
    for c in mr['copies']:
        expected = expected_copies[(c['role'], c['relativePath'])]
        require(c['target'] == expected['source'] and c['mode'] == expected['mode'] and
                c['targetIdentity']['nlink'] == c['donorIdentity']['nlink'] == 1 and
                (c['targetIdentity']['dev'], c['targetIdentity']['ino']) !=
                (c['donorIdentity']['dev'], c['donorIdentity']['ino']), 'documentary independent-copy identity')

    commands = [['generate-factories.mjs', '--crypto-random'], ['generate-fs-factory.mjs'],
                ['generate-startup-factory.mjs'], ['generate-module-factory.mjs'], ['generate-async-hooks-factory.mjs'],
                ['generate-vm-data-factory.mjs'], ['zlib/generate-factory.mjs', '--repository', result['sourceRoot']],
                ['zlib/generate-stream-factory.mjs'], ['next-http/generate-http-factory.mjs'],
                ['next-imports/generate-imports-factory.mjs']]
    expected_argv = [[plan['node']['path'], result['sourceRoot'] + '/builtins/node-compat/' + args[0],
                      *args[1:], '--check'] for args in commands]
    require(result['node'] == plan['node'] and len(result['commands']) == len(gr['commands']) == 10, 'ten original commands')
    require(plan['perCommandSeconds'] == 30 and plan['outerSeconds'] == 900 and
            plan['minimumFreeBytes'] == result['minimumFreeBytes'] == 67108864 and
            result['freeBytesAtAdmission'] >= 67108864 and result['continuousFreeFloorClaimed'] is False and
            plan['maxAcceptedRawStreamBytes'] == 1048576 and plan['maxAcceptedOutputBytes'] == LIMIT and
            result['byteCapsArePostCaptureAdmissionNotContinuousLimits'] is True, 'original caps/admission semantics')
    output = role['actualResult'].rsplit('/', 1)[0]
    owner_count, pids = 0, []

    def owner(start_ref, terminal_ref, owned_refs, seconds, argv):
        start, terminal = obj(start_ref), obj(terminal_ref)
        require(clean(terminal) and start['pid'] == terminal['pid'] and start['argv'] == argv and
                start['timeoutSeconds'] == seconds and start['authority'] == terminal['authority'] ==
                dlabel(role['rootAuthority']), 'original owner argv/cap/authority/cleanup')
        frames = [obj(d) for d in owned_refs]
        require([f['sequence'] for f in frames] == list(range(len(frames))) and
                [f['process'] for f in frames] == terminal['observedProcesses'] and
                any(f['process']['pid'] == terminal['pid'] for f in frames), 'complete original owned frames')
        require(ref(terminal['stderr']) == b'' and terminal['stdout']['bytes'] <= 1048576,
                'final raw stderr/stream cap')
        ref(terminal['stdout'])
        return start, terminal, len(frames)

    for i, (c, expected) in enumerate(zip(result['commands'], expected_argv)):
        prefix = output + '/command-' + str(i).zfill(2)
        owned = [dlabel(p) for p in sorted(data) if p.startswith(prefix + '/owned-')]
        start, term, n = owner(c['started'], c['terminal'], owned, 30, expected)
        pids.append(term['pid']); owner_count += n
        require(c['argv'] == expected and c['cwd'] == result['sourceRoot'] and c['rawExitCode'] == 0 and
                type(c['rawExitCode']) is int and c['ownedGroupsClean'] is True and c['monitorError'] is None and
                c['stdout'] == term['stdout'] and c['stderr'] == term['stderr'] and
                c['stdoutSha256'] == c['stdout']['sha256'] and c['stderrSha256'] == c['stderr']['sha256'], 'command outcome')
        require(label(prefix + '/record.json') == c, 'raw record/result equality')
        rc = gr['commands'][i]
        require(rc['index'] == i and rc['argv'] == expected and rc['pid'] == term['pid'] and
                rc['secondsCap'] == 30 and rc['rawExitCode'] == 0 and rc['started'] == c['started'] and
                rc['terminal'] == c['terminal'] and rc['stdout'] == c['stdout'] and rc['stderr'] == c['stderr'] and
                rc['ownedRecords'] == owned and rc['record'] == dlabel(prefix + '/record.json'), 'review command joins')
    outer = result['outerTerminal']['path'].rsplit('/', 1)[0]
    outer_owned = [dlabel(p) for p in sorted(data) if p.startswith(outer + '/owned-')]
    argv = [plan['python']['path'], '-I', '-B', source_root + '/run.py', '--worker-authority', role['rootAuthority']]
    start, terminal, n = owner(result['outerStarted'], result['outerTerminal'], outer_owned, 900, argv)
    owner_count += n
    require(result['outerStdout'] == terminal['stdout'] and result['outerStderr'] == terminal['stderr'] and
            gr['originalOwner']['started'] == result['outerStarted'] and
            gr['originalOwner']['terminal'] == result['outerTerminal'] and
            gr['originalOwner']['ownedRecords'] == outer_owned and gr['originalOwner']['pid'] == terminal['pid'],
            'outer publication/review joins')
    stdout_frames = [decode(line) for line in ref(terminal['stdout']).splitlines() if line]
    require(stdout_frames == [dict(pid=pid, timeoutSeconds=30) for pid in pids] +
            [dict(bodyResult=dlabel(role['bodyResult']), passed=True)], 'outer raw JSONL protocol')
    require(owner_count == gr['ownedRecordCount'] and gr['allTenCommandsRawZero'] is
            gr['allElevenOwnersClean'] is gr['allRawStreamHashesVerified'] is gr['allStderrEmpty'] is True,
            'derived eleven-owner summary')
    namespace_bytes = 0
    for ns in gr['capture']['namespaces']:
        prefix = ns['path'] + '/'
        names = sorted(p[len(prefix):] for p in data if p.startswith(prefix))
        require(len(names) == ns['files'] and set(names) == {n for n in m['originalDirectoryMembership'][ns['path']]
                if n not in ns['directories']}, 'complete retained raw namespace')
        namespace_bytes += sum(descriptors[p]['bytes'] for p in data if p.startswith(prefix))
    require(namespace_bytes == gr['capture']['actualAggregateBytesIncludingFinalReceipt'] ==
            result['outputBytesBeforeFinalReceipt'] + dlabel(role['actualResult'])['bytes'] and
            namespace_bytes <= LIMIT, 'actual postcapture total cap')
    # Authenticate only the TWO explicitly complete Source families. Builder is a selected witness subset.
    for key in ('generatorSourceIndex', 'materializerSourceIndex'):
        root = role[key].rsplit('/', 1)[0]
        index = label(role[key])
        for r in index['files']:
            require(dlabel(root + '/' + r['path']) == dict(r, path=root + '/' + r['path']), 'indexed Source witness')
        require({p[len(root)+1:] for p in data if p.startswith(root + '/')} ==
                {'index.json'} | {r['path'] for r in index['files']}, 'selected closed Source family')
    require(source_index['sourceOnly'] is True and m['historicalPhysicalModesAndInodesDocumentary'] is True and
            m['scope']['nativeBuildAccepted'] is m['scope']['runtimeAccepted'] is False, 'retention scope')
    require(inventory()[:2] == (files, dirs) and all(snapshot(p) == s for p, s in stamps.items()), 'whole-current bookend')
    print(json.dumps(dict(passed=True, files=len(rows), payloadBytes=m['payloadBytes'],
        generatorCommands=10, originalOwners=11, recordedOwnedFrames=owner_count,
        recordedRoleCounts=counts, recordedMaterializedFiles=825, sourcePayloadsRead=0,
        helpersOrGeneratorsExecuted=False, nativeBuildAccepted=False, runtimeAccepted=False), sort_keys=True))


if __name__ == '__main__':
    main()

