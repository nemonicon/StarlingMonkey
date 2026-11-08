#!/usr/bin/env python3
"""Offline byte/JSON replay of this finite constructor corpus; never opens originals."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import stat

HERE = Path(__file__).resolve().parent
MANIFEST_SHA256 = '943f0526c7923c08c5b7860c2fc7f76c8a8a512a463bcde0226bcefb0649a8be'
LIMIT = 8 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def stamp(path):
    s = path.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
            s.st_mtime_ns, s.st_ctime_ns)


def bounded(path, size):
    before = stamp(path)
    require(path.resolve() == path and stat.S_ISREG(before[2]) and
            before[3] == 1 and before[4] == size and size <= LIMIT,
            'Not a canonical, regular, bounded independent file: ' + str(path))
    content = path.read_bytes()
    require(stamp(path) == before and len(content) == size,
            'File changed during read: ' + str(path))
    return content, before


def main():
    mp = HERE / 'manifest.json'
    raw, manifest_stamp = bounded(mp, mp.lstat().st_size)
    require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA256, 'Manifest hash')
    m = json.loads(raw)
    require(m['schemaVersion'] == 1 and m['maximumPayloadBytes'] == LIMIT,
            'Manifest version/cap')
    original_to_bytes = {}
    copied_paths = set()
    stamps = {}
    inodes = set()
    total = 0
    for row in m['files']:
        rel = PurePosixPath(row['copy']['path'])
        require(not rel.is_absolute() and '..' not in rel.parts and
                str(rel).startswith('files/') and str(rel) not in copied_paths,
                'Unsafe or duplicate copy path')
        copied_paths.add(str(rel))
        path = HERE / str(rel)
        b, s = bounded(path, row['copy']['bytes'])
        require(hashlib.sha256(b).hexdigest() == row['copy']['sha256'] ==
                row['original']['sha256'] and len(b) == row['original']['bytes'],
                'Copied bytes differ from recorded original')
        require(row['original']['path'] not in original_to_bytes and
                s[:2] not in inodes, 'Duplicate original or physical alias')
        original_to_bytes[row['original']['path']] = b
        inodes.add(s[:2])
        stamps[path] = s
        total += len(b)
    require(total == m['payloadBytes'] <= LIMIT and len(m['files']) == m['fileCount'],
            'Payload totals')
    actual_files = set()
    actual_dirs = {'.'}
    for path in HERE.rglob('*'):
        s = path.lstat()
        require(not stat.S_ISLNK(s.st_mode), 'Symlink in corpus')
        if stat.S_ISREG(s.st_mode):
            require(s.st_nlink == 1, 'Hardlink in corpus')
            actual_files.add(path.relative_to(HERE).as_posix())
        else:
            require(stat.S_ISDIR(s.st_mode), 'Special file in corpus')
            actual_dirs.add(path.relative_to(HERE).as_posix())
    expected_files = copied_paths | {'manifest.json', 'check.py'}
    expected_dirs = {'.'}
    for name in expected_files:
        p = PurePosixPath(name).parent
        while str(p) != '.':
            expected_dirs.add(str(p))
            p = p.parent
    require(actual_files == expected_files and actual_dirs == expected_dirs,
            'Exact corpus membership')

    # Absolute original paths below are documentary dictionary keys, not I/O paths.
    roles = m['roles']

    def content(role):
        return original_to_bytes[roles[role]]

    def obj(role):
        return json.loads(content(role))

    def checked(d):
        b = original_to_bytes[d['path']]
        require(len(b) == d['bytes'] and hashlib.sha256(b).hexdigest() == d['sha256'],
                'Retained descriptor join')
        return b

    r, a, p = obj('result'), obj('authority'), obj('callerPlan')
    primary = obj('primaryReview')
    require(primary['state'] ==
            'COORDINATED_PUBLIC_REQUEST_CORRELATION_COMPONENT_INIT_DATA_REVIEW_PASSED_V1' and
            primary['verifiedPassed'] is True and
            primary['completeReturnedImportAuditVerified'] is True and
            primary['rootAuthority'] == r['rootAuthority'] and
            primary['callerIndex'] == r['callerIndex'] and primary['plan'] == r['plan'] and
            primary['component'] == r['artifacts']['component'] and
            primary['componentAudit'] == r['artifacts']['componentAudit'],
            'Documentary coordinated primary review roles')
    require(primary['actualResult']['path'] == roles['result'] and
            primary['actualOwnerWorldReview']['path'] == roles['ownerReview'],
            'Primary selected result and owner roles')
    checked(primary['actualResult'])
    owner_review = json.loads(checked(primary['actualOwnerWorldReview']))
    require(owner_review['state'] ==
            'PUBLIC_REQUEST_CORRELATION_INIT_OWNER_WORLD_DATA_REVIEW_PASSED_V1' and
            owner_review['verifiedOwnerAndWorldDataPassed'] is True and
            all(owner_review[k] == primary[k] for k in
                ['actualResult', 'rootAuthority', 'callerIndex', 'plan',
                 'inputSourceIndex', 'inputEntry']), 'Genuine complementary owner wire')
    require(all(primary[k] is False for k in ['ordinaryExportsInvoked', 'httpServed',
            'appMountedAtInit', 'deployedCompletionDiagnosticObserved', 'runtimeAccepted',
            'fullNextAccepted', 'priorFailedGatesAccepted', 'privateStoreIdentityProved',
            'uniqueCauseProved', 'filesystemFixtureMountedAtInit',
            'deployedFetchProbeInvoked', 'deployedImportOrFilesystemProbeInvoked',
            'deployedPublicRequestCorrelationObserved', 'publicRequestCorrelationJoinObserved',
            'guestCorrelationNonceGeneratedAtInit', 'publicNonceManifestSuppliedAtInit',
            'nodeParityProved', 'productionProfilePromoted']), 'Primary construction-only scope')
    checked(r['rootAuthority'])
    checked(r['callerIndex'])
    checked(r['plan'])
    require(r['plan']['path'] == roles['callerPlan'] and
            r['rootAuthority']['path'] == roles['authority'] and
            r['callerIndex'] == a['callerIndex'] and r['entryMode'] == 'real-next' and
            r['passed'] is True and r['error'] is None and
            r['finalProtection'] == {'unchanged': True}, 'Constructor result roles')
    require(a['componentizeInitAllowed'] is True and a['nativeBuildReviewedForConstruction']
            is True and all(a[k] is False for k in m['forbiddenAuthorityFlags']),
            'INIT authority flags')
    require(all(r[k] is False for k in m['rawResultFalseFlags']), 'Raw result false flags')
    require(len(a['metadataExpectedFixedValues']) == 31 and
            len(a['engineBuildEvidence']) == 39 and len(a['newSourceEvidence']) == 18,
            'Recorded generation-specific role counts')
    require(r['artifacts']['inputSourceIndex'] == p['inputSourceIndex'] and
            r['artifacts']['inputEntry'] == p['entries']['real-next'] and
            p['prospectiveInputSourceBindingPending'] is False, 'Selected entry')
    checked(p['inputSourceIndex'])
    checked(p['entries']['real-next'])
    require(a['outputRoot'] == m['originalOutputRoot'] ==
            p['outputPrefix'] + '-real-next-' + a['runId'], 'Output namespace')
    ir = obj('inputRoles')
    require(ir['rootAuthority'] == r['rootAuthority'] and
            ir['callerIndex'] == r['callerIndex'] and
            ir['inputSourceIndex'] == p['inputSourceIndex'] and
            ir['oldMetadataFrameAdapted'] is False, 'Input role receipt')
    for k in ['engine', 'nativeMetadata', 'engineBuildEvidence', 'newSourceEvidence',
              'metadataExpectedFixedValues']:
        require(ir[k] == a[k], 'Authority/input role equality: ' + k)
    commands = r['commands']
    require([c['label'] for c in commands] ==
            ['componentize-init', 'component-validate', 'component-wit'], 'Three commands')
    streams = []
    pids = []
    owner_counts = []
    for n, owner in enumerate(m['owners']):
        s = json.loads(original_to_bytes[owner['started']])
        t = json.loads(original_to_bytes[owner['terminal']])
        require(s['pid'] == t['pid'] == owner['pid'] and
                s['authority'] == t['authority'] == r['rootAuthority'] and
                s['argv'] == owner['argv'] and s['timeoutSeconds'] == owner['capSeconds'],
                'Original owner admission')
        require(t['rawExitCode'] == 0 and t['timeout'] is False and
                t['forcedCleanup'] is False and t['parentOwnedGroupGone'] is True and
                t['allObservedOwnedGroupsGone'] is True and
                all(t[k] == [] for k in ['errors', 'signals', 'interruptedSignals',
                                        'remainingObservedPids']) and
                all(x['alive'] is False and x['signalAllowed'] is False
                    for x in t['finalGroups']), 'Clean original terminal')
        observations = [json.loads(original_to_bytes[x]) for x in owner['owned']]
        require(len(observations) == len(t['observedProcesses']) and
                all(v['sequence'] == i and v['process'] == t['observedProcesses'][i]
                    for i, v in enumerate(observations)), 'Complete owned snapshots')
        owner_counts.append(len(observations))
        for k in ['stdout', 'stderr']:
            streams.append(checked(t[k]))
        if n < 3:
            c = commands[n]
            require(c == json.loads(original_to_bytes[owner['observation']]) and
                    c['argv'] == s['argv'] and c['capSeconds'] == s['timeoutSeconds'] and
                    c['rawExitCode'] == 0 and c['clean'] is True and
                    c['terminal']['path'] == owner['terminal'] and
                    c['stdout'] == t['stdout'] and c['stderr'] == t['stderr'], 'Inner observation')
            checked(c['terminal'])
            pids.append({'pid': s['pid'], 'timeoutSeconds': s['timeoutSeconds']})
    require(len(streams) == 8 and all(marker not in stream for stream in streams
            for marker in [b'NEXT_GUEST_RESPONSE_COMPLETION_V1',
                           b'NEXT_GUEST_RESPONSE_COMPLETION_V2',
                           b'NEXT_GUEST_PROMISE_COMPLETION_V1']),
            'INIT captured-stream marker absence')
    frames = [json.loads(x) for x in content('outerStdout').splitlines()]
    require(frames[:3] == pids and len(frames) == 4 and frames[3]['passed'] is True and
            frames[3]['error'] is None and frames[3]['result']['path'] == roles['result'],
            'Original outer JSONL frames')
    checked(frames[3]['result'])
    require(m['rootControllerStreamsRetained'] is False and
            'rootStdout' not in roles and 'rootStderr' not in roles,
            'Separate Root controller streams were not present; none invented')
    w = obj('worldGuard')
    require(w['unchanged'] is True and w['before'] == w['after'] and
            w['before']['sourceIndex'] == a['worldSourceIndex'] and
            w['before']['members'] == 28 and w['before']['witFiles'] == 8 and
            w['before']['exactFileAndDirectoryMembership'] is True and
            w['before']['noSymlinkOrHardlinkAliases'] is True, 'Historical world receipt')
    checked(a['worldSourceIndex'])
    audit = obj('audit')
    require(audit['component'] == r['artifacts']['component'] and audit['passed'] is True and
            audit['allEmittedVersion'] == '0.2.10' and
            len(audit['emittedImports']) == len(set(audit['emittedImports'])) == 13 and
            set(audit['emittedImports']) == set(p['selectedInterfaces']) and
            audit['exports'] == ['wasi:http/incoming-handler@0.2.10'], 'World audit')
    wit = content('witStdout').decode('utf-8')
    require(re.findall(r'^\s*import (wasi:[^;]+);$', wit, re.M) == audit['emittedImports'] and
            re.findall(r'^\s*export (wasi:[^;]+);$', wit, re.M) == audit['exports'],
            'Actual preserved WIT lists')
    options = obj('requestedOptions')
    require(options['env'] == {} and options['witPath'] == p['witDirectory'] and
            options['engine'] == a['engine']['path'] and options['worldName'] == 'next-http' and
            options['preview2Adapter'] == p['pins']['adapter']['path'] and
            options['disableFeatures'] == ['fetch-event'] and options['enableFeatures'] == [] and
            options['enableAot'] is False and all(v is False for v in options['debug'].values()),
            'Requested INIT options')
    initial, configured, final = (obj('preopens' + k) for k in ['Initial', 'Configured', 'Final'])
    require(initial == {'count': 0, 'virtualNames': []} and
            configured['count'] == final['count'] == 1 and
            configured['virtualNames'] == final['virtualNames'] == [p['witDirectory']] and
            configured['hostMappings'] == {p['witDirectory']: p['witDirectory']} and
            final['mountConfigured'] is True, 'WIT-only tool parser preopens')
    require(r['artifacts']['returnedImports']['path'] == roles['returnedImports'] and
            r['artifacts']['returnedOwnShape']['path'] == roles['returnedOwnShape'],
            'Selected API return artifact roles')
    checked(r['artifacts']['returnedImports'])
    json.loads(checked(r['artifacts']['returnedOwnShape']))
    imports = obj('returnedImports')
    require(isinstance(imports, list) and all(isinstance(x, list) and len(x) == 2 and
            all(isinstance(v, str) for v in x) for x in imports), 'Returned import pair shape')
    require(len(imports) == m['observedReturnedImportTupleCount'] ==
            primary['actualReturnedImportFunctionCount'], 'Observed count, not API constant')
    require(stamp(mp) == manifest_stamp and all(stamp(path) == s for path, s in stamps.items()),
            'Final current read bookends')
    print(json.dumps({'passed': True, 'files': len(m['files']), 'payloadBytes': total,
          'owners': len(m['owners']), 'ownedRecords': owner_counts, 'innerRawExitCodes': [0, 0, 0],
          'outerRawExitCode': 0, 'capturedInitStreamsWithoutMarker': 8,
          'observedReturnedImportTuples': len(imports), 'standardInterfaces': 13,
          'originalPathsRead': False, 'historicalModesAndInodesDocumentary': True,
          'liveCheckoutModesObservedOnly': True, 'omittedPayloadsRevalidated': False,
          'deployedPublicCorrelationOrFullNextAccepted': False}, sort_keys=True))


if __name__ == '__main__':
    main()
