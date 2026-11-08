#!/usr/bin/env python3
"""Finite offline raw replay. No original paths, JS, guards or marker parser are invoked."""
from pathlib import Path, PurePosixPath
import base64
import hashlib
import json
import stat
import zlib

HERE = Path(__file__).resolve().parent
MANIFEST_SHA256 = 'f3fc116836405b318691296f10f0c3a8b9978047abf0ddd448baa27f5af797f1'
LIMIT = 32 * 1024 * 1024


def require(value, message):
    if not value:
        raise ValueError(message)


def stamp(p):
    s = p.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
            s.st_mtime_ns, s.st_ctime_ns)


def read(p, size):
    before = stamp(p)
    require(p.resolve() == p and stat.S_ISREG(before[2]) and before[3] == 1 and
            before[4] == size and 0 <= size <= LIMIT, 'Bounded canonical regular file')
    b = p.read_bytes()
    require(stamp(p) == before and len(b) == size, 'Read bookend')
    return b, before


def main():
    mp = HERE / 'manifest.json'
    raw, ms = read(mp, mp.lstat().st_size)
    require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA256, 'Manifest pin')
    m = json.loads(raw)
    require(m['schemaVersion'] == 1 and m['maximumPayloadBytes'] == LIMIT, 'Schema/cap')
    by_original, stamps, inodes, copies = {}, {}, set(), set()
    total = 0
    for row in m['files']:
        rel = PurePosixPath(row['copy']['path'])
        require(not rel.is_absolute() and '..' not in rel.parts and
                str(rel).startswith('files/') and str(rel) not in copies, 'Safe copy path')
        copies.add(str(rel))
        p = HERE / str(rel)
        b, s = read(p, row['copy']['bytes'])
        require(hashlib.sha256(b).hexdigest() == row['copy']['sha256'] ==
                row['original']['sha256'] and len(b) == row['original']['bytes'], 'Bytes/hash')
        require(row['original']['path'] not in by_original and s[:2] not in inodes,
                'No duplicate original or physical alias')
        by_original[row['original']['path']] = b
        inodes.add(s[:2])
        stamps[p] = s
        total += len(b)
    require(total == m['payloadBytes'] <= LIMIT and len(m['files']) == m['fileCount'],
            'Finite totals')
    expected_files = copies | {'manifest.json', 'check.py'}
    expected_dirs = {'.'}
    for name in expected_files:
        p = PurePosixPath(name).parent
        while str(p) != '.':
            expected_dirs.add(str(p))
            p = p.parent
    actual_files, actual_dirs = set(), {'.'}
    for p in HERE.rglob('*'):
        s = p.lstat()
        require(not stat.S_ISLNK(s.st_mode), 'No symlink')
        if stat.S_ISREG(s.st_mode):
            require(s.st_nlink == 1, 'No hardlink')
            actual_files.add(p.relative_to(HERE).as_posix())
        else:
            require(stat.S_ISDIR(s.st_mode), 'No special file')
            actual_dirs.add(p.relative_to(HERE).as_posix())
    require(actual_files == expected_files and actual_dirs == expected_dirs, 'Exact membership')

    # Original absolute paths are dictionary keys only. No I/O uses them.
    roles = m['roles']

    def content(role):
        return by_original[roles[role]]

    def obj(role):
        return json.loads(content(role))

    def checked(d):
        b = by_original[d['path']]
        require(len(b) == d['bytes'] and hashlib.sha256(b).hexdigest() == d['sha256'],
                'Retained descriptor join')
        return b

    r, a, c, b = (obj(k) for k in ['result', 'authority', 'client', 'browser'])
    s, t, observation = (obj(k) for k in ['started', 'terminal', 'observation'])
    plan = obj('plan')
    checked(r['rootAuthority'])
    checked(r['sourceIndex'])
    checked(a['plan'])
    require(r['rootAuthority']['path'] == roles['authority'] and
            a['plan']['path'] == roles['plan'] and r['sourceIndex'] == a['sourceIndex'] and
            r['component'] == a['component'] and r['constructionResult'] == a['constructionResult'],
            'Current authority/source/component roles')
    require(r['client']['result']['path'] == roles['client'] and
            checked(r['client']['result']) == content('client') and c['browser'] == b and
            c['origin'] == b['origin'] == r['server']['readyOrigin'], 'Client/browser/origin roles')
    require(r['passed'] is False and c['passed'] is False and
            c['originalContractPassed'] is False and r['adoption'] is False,
            'Historical failure remains failed')
    require(a['unissued'] is False and a['browserAllowed'] is True and
            all(a[k] is False for k in ['compilerAllowed', 'componentConstructionAllowed',
                                       'externalDeploymentAllowed', 'adoptionAllowed']),
            'Recorded permission scope')
    require(s['pid'] == t['pid'] == m['originalOwnerPid'] and s['timeoutSeconds'] == 600 and
            s['authority'] == t['authority'] == r['rootAuthority'] and
            s['argv'] == [plan['node']['path'], roles['deploySource'], roles['authority']],
            'Original owner argv/authority/cap')
    require(t['rawExitCode'] == 1 and t['timeout'] is False and t['forcedCleanup'] is False and
            t['parentOwnedGroupGone'] is True and t['allObservedOwnedGroupsGone'] is True and
            all(t[k] == [] for k in ['errors', 'signals', 'interruptedSignals',
                                    'remainingObservedPids']) and
            all(x['alive'] is False and x['signalAllowed'] is False for x in t['finalGroups']),
            'Clean original nonzero owner')
    owned = [json.loads(by_original[path]) for path in m['ownedRecords']]
    require(len(owned) == len(t['observedProcesses']) and
            all(x['sequence'] == i and x['process'] == t['observedProcesses'][i]
                for i, x in enumerate(owned)), 'All owned snapshots')
    require(observation['result']['path'] == roles['result'] and
            checked(observation['result']) == content('result') and
            observation['terminal']['path'] == roles['terminal'] and
            checked(observation['terminal']) == content('terminal') and
            observation['rawExitCode'] == 1 and observation['ownedGroupsClean'] is True and
            observation['protectedInputsPreserved'] is True and observation['passed'] is False,
            'Original observation')
    rootframes = [json.loads(x) for x in content('rootStdout').splitlines()]
    require(rootframes == [{'pid': s['pid'], 'timeoutSeconds': 600}, observation] and
            content('rootStderr') == b'', 'Root two frames')
    for role in ['server', 'client']:
        for key in ['stdout', 'stderr']:
            checked(r[role][key])
    for key in ['stdout', 'stderr']:
        checked(t[key])
    capture = r['server']['stdoutCapture']
    stdout = checked(r['server']['stdout'])
    require(r['server']['stdout']['path'] == roles['guestStdout'] == capture['path'] and
            capture['state'] == 'RAW_STDOUT_CAPTURE_FINALIZED_COMPLETE_V1' and
            capture['limitBytes'] == 8388608 and
            len(stdout) <= capture['limitBytes'] and
            capture['completeWriteBytes'] == capture['lastReservedWriteCeiling'] ==
            capture['fileBytes'] == len(stdout) and
            all(capture[k] is True for k in ['pipeEof', 'fileClosed', 'fileBoundVerified',
                                            'finalized', 'complete']) and
            all(capture[k] is False for k in ['overflow', 'partialWritePossible',
                                             'unretainedBytesUnknown']) and
            capture['errors'] == [] and capture['rejectedWholeChunkBytes'] is None and
            r['server']['exit'] == {'code': 0, 'signal': None, 'error': None} and
            r['server']['sigintSent'] is True and r['server']['forcedCleanup'] is False,
            'Complete raw capture and graceful server stop')
    require(r['client']['exit'] == {'code': 1, 'signal': None, 'error': None} and
            c['browserExit'] == {'code': 1, 'signal': None}, 'Client/browser historical exits')
    require(c['cacheInvalidation']['before']['generation'] ==
            c['cacheInvalidation']['after']['generation'] == 1 and
            c['cacheInvalidation']['passed'] is False, 'Legacy cache failure')
    require(len(c['http']) == 24 and all(x['passed'] for x in c['http']) and
            c['portableCacheValidation']['passed'] is True and
            c['portableCacheValidation']['checks'] == 52 and
            c['supplementalValidation']['passed'] is True and
            c['supplementalValidation']['checks'] == 80 and c['streaming']['chunks'] == 5 and
            c['streaming']['complete'] is True, 'Recorded complementary body gate summaries')
    require(b['functionalPassed'] is True and b['passed'] is False and
            b['browserErrorFree'] is False and b['browserClosed'] is True and
            len(b['tests']) == 2 and all(x['passed'] and not x['timedOut'] for x in b['tests']),
            'Functional versus strict browser result')
    require([x['stage'] for x in b['errors']] == ['server-action-response-body',
            'server-action-response-finished', 'server-action-request-sizes'] and
            all(x['requestId'] == 7 and x['message'] == 'net::ERR_ABORTED' for x in b['errors']),
            'Three strict failures remain failed')
    post = [x for x in b['responseHeaders'] if x['test'] == 'server-action' and
            x['method'] == 'POST' and x['url'] == b['origin'] + '/actions']
    require(len(post) == 1 and post[0]['requestId'] == 7 and post[0]['status'] == 200,
            'Captured POST response')
    bc = [x for x in b['bodyCaptures'] if x['test'] == 'server-action' and x['requestId'] == 7]
    require(len(bc) == 1 and all(bc[0][k] is None for k in
            ['decodedBody', 'encodedSizes', 'wireBodySha256']), 'Unavailable POST body/sizes')
    trace = [x for x in b['trace'] if x.get('test') == 'server-action']
    request = next(x for x in trace if x['event'] == 'request' and x.get('requestId') == 7)
    response = next(x for x in trace if x['event'] == 'response' and x.get('requestId') == 7)
    nav = next(x for x in trace if x['event'] == 'main-frame-navigated' and
               x.get('url') == b['origin'] + '/action-result?value=browser-action')
    failed = next(x for x in trace if x['event'] == 'requestfailed' and x.get('requestId') == 7)
    close = next(x for x in trace if x['event'] == 'page-close')
    require(int(request['ns']) < int(response['ns']) < int(nav['ns']) < int(failed['ns']) <
            int(close['ns']), 'Single host arrival ordering')
    cdp_request = [x for x in b['cdpEvents'] if x['test'] == 'server-action' and
                   x['event'] == 'Network.requestWillBeSent' and
                   x['payload']['request']['method'] == 'POST' and
                   x['payload']['request']['url'] == b['origin'] + '/actions']
    require(len(cdp_request) == 1, 'One CDP POST candidate')
    cid = cdp_request[0]['payload']['requestId']
    cdp = [x for x in b['cdpEvents'] if x['test'] == 'server-action' and
           x['payload'].get('requestId') == cid]
    loading_failed = [x for x in cdp if x['event'] == 'Network.loadingFailed']
    require(len(loading_failed) == 1 and loading_failed[0]['payload']['canceled'] is True and
            loading_failed[0]['payload']['errorText'] == 'net::ERR_ABORTED' and
            not any(x['event'] == 'Network.loadingFinished' for x in cdp), 'CDP local outcome')
    form = base64.b64decode(b['actionPosts'][0]['bodyBase64'], validate=True)
    require(len(form) == b['actionPosts'][0]['bytes'] == 391 and
            form == cdp_request[0]['payload']['request']['postData'].encode(), 'POST form bytes')
    nm = b['netlog']
    require(nm['file']['path'] == roles['netlog'], 'NetLog role')
    n = json.loads(checked(nm['file']))
    require(nm['completeJson'] is True and nm['fsynced'] is True and nm['errors'] == [] and
            len(n['events']) == nm['eventCount'] and nm['requestedSizeMegabytes'] == 16 and
            nm['finalReadLimitBytes'] == 20971520 and nm['file']['bytes'] <= 20971520,
            'Complete retained circular JSON')
    names = {v: k for k, v in n['constants']['logEventTypes'].items()}
    phases = {v: k for k, v in n['constants']['logEventPhase'].items()}
    candidates = [(i, x) for i, x in enumerate(n['events']) if
                  names[x['type']] == 'URL_REQUEST_START_JOB' and
                  x.get('params', {}).get('method') == 'POST' and
                  x.get('params', {}).get('url') == b['origin'] + '/actions']
    require(len(candidates) == 1, 'NetLog URL/method candidate')
    index, candidate = candidates[0]
    source = [x for x in n['events'] if x['source']['id'] == candidate['source']['id']]
    send = [x for x in source if names[x['type']] == 'HTTP_TRANSACTION_SEND_REQUEST_HEADERS']
    require(len(send) == 1 and send[0]['params']['line'] ==
            'POST /actions HTTP/1.1' + chr(13) + chr(10), 'NetLog same-source send')
    negative = [x for x in source if isinstance(x.get('params'), dict) and
                isinstance(x['params'].get('net_error'), int) and x['params']['net_error'] < 0]
    require(not negative, 'Historical absence of explicit negative code on candidate source')
    ends = [x for x in source if names[x['type']] in ['CORS_REQUEST', 'REQUEST_ALIVE'] and
            phases[x['phase']] == 'PHASE_END']
    require({names[x['type']] for x in ends} == {'CORS_REQUEST', 'REQUEST_ALIVE'} and
            all(not x.get('params') for x in ends), 'Empty candidate END records')
    counts = {name: sum(x.get('params', {}).get('byte_count', 0) for x in source if
                       names[x['type']] == name) for name in
              ['URL_REQUEST_JOB_BYTES_READ', 'URL_REQUEST_JOB_FILTERED_BYTES_READ']}
    owner_review = obj('ownerReview')
    require(owner_review['actualResult'] == observation['result'] and
            owner_review['netlog']['candidateIndex'] == index and
            owner_review['netlog']['sourceLocalOnly'] == candidate['source'] and
            owner_review['netlog']['sendHeaders']['params'] == send[0]['params'] and
            owner_review['netlog']['readByteCounts'] == counts and
            owner_review['stdoutCapture']['raw'] == r['server']['stdout'], 'Held B review joins')
    marker_review = obj('markerReview')
    require(marker_review['actualResult'] == observation['result'] and
            marker_review['rawStdout'] == r['server']['stdout'] and
            marker_review['rootAuthority'] == r['rootAuthority'], 'R review provenance only')
    w = obj('worldGuard')
    require(w['unchanged'] is True and w['nativeInputsPreserved'] is True and
            w['before'] == w['after'] and w['authority'] == r['rootAuthority'] and
            w['before']['sourceIndex'] == a['worldSourceIndex'], 'Documentary world/native receipt')
    png_count = 0
    for row in m['files']:
        if row['copy']['path'].endswith('.png'):
            v = by_original[row['original']['path']]
            require(v.startswith(b'\x89PNG\r\n\x1a\n'), 'PNG signature')
            pos = 8
            seen_iend = False
            while pos < len(v):
                size = int.from_bytes(v[pos:pos + 4], 'big')
                tag = v[pos + 4:pos + 8]
                part = v[pos + 8:pos + 8 + size]
                require(len(part) == size and zlib.crc32(tag + part) & 0xffffffff ==
                        int.from_bytes(v[pos + 8 + size:pos + 12 + size], 'big'), 'PNG CRC')
                pos += 12 + size
                if tag == b'IEND':
                    require(size == 0 and pos == len(v), 'PNG terminal IEND')
                    seen_iend = True
                    break
            require(seen_iend and pos == len(v), 'Whole PNG')
            png_count += 1
    require(png_count == 2, 'Two retained screenshots')
    require(stamp(mp) == ms and all(stamp(p) == s for p, s in stamps.items()),
            'Whole current read bookends')
    print(json.dumps({'passed': True, 'files': len(m['files']), 'payloadBytes': total,
          'rawExitCode': 1, 'ownerSnapshots': len(owned), 'stdoutBytes': len(stdout),
          'completeRawStdoutCapture': True, 'browserFunctionalPassed': True,
          'browserStrictPassed': False, 'legacyCacheGeneration': [1, 1],
          'netlogEvents': len(n['events']), 'netlogPostCandidates': 1, 'screenshots': png_count,
          'markerSemanticsReplayed': False, 'omittedPayloadsRevalidated': False,
          'historicalModesAndInodesDocumentary': True, 'liveCheckoutModesObservedOnly': True,
          'originalPathsRead': False, 'fullNextAccepted': False, 'causeOrPrivateIdentityProved': False},
          sort_keys=True))


if __name__ == '__main__':
    main()
