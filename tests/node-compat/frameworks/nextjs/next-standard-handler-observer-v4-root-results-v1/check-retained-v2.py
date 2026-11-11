"""Check saved V4 component probes using only this repository packet; no host replay."""
import hashlib
import json
from pathlib import Path
import sys
import stat

INDEX_SHA = '28b1c1e17053afa9ee63519a5ef2c19d6bb9aafae0e77d77618b7c1d88a9a66a'


def require(value, message):
    if not value:
        raise ValueError(message)


def stamp(path):
    s = path.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def bounded_read(path, maximum, exact=None):
    require(path.resolve() == path and not any(p.is_symlink() for p in (path, *path.parents)), 'Canonical ancestry')
    before = stamp(path)
    require(stat.S_ISREG(before[2]) and before[3] == 1 and 0 <= before[4] <= maximum, 'Bounded independent regular file')
    require(exact is None or before[4] == exact, 'Declared file size before read')
    with path.open('rb') as handle:
        raw = handle.read(maximum + 1)
    require(len(raw) == before[4] and stamp(path) == before, 'Stable bounded read')
    return raw


def check():
    if not (__debug__ and sys.flags.isolated and sys.dont_write_bytecode):
        raise RuntimeError('Use Python -I -B without -O')
    require(len(sys.argv) == 1, 'No arguments')
    root = Path(__file__).resolve().parent / 'raw-records'
    raw_index = bounded_read(root / 'index.json', 65536)
    require(hashlib.sha256(raw_index).hexdigest() == INDEX_SHA, 'Pinned saved packet')
    index = json.loads(raw_index)
    require(len(index['files']) == index['payloadFiles'] == 70, 'Exact packet count')
    require(all(type(r['bytes']) is int and 0 <= r['bytes'] <= 4 * 1024**2 for r in index['files']), 'Declared per-file bounds')
    require(sum(r['bytes'] for r in index['files']) == index['totalBytes'] <= 16 * 1024**2, 'Declared aggregate bound')
    rows, originals, stamps = {}, {}, {}
    for row in index['files']:
        name = row['path']
        part = Path(name)
        require(not part.is_absolute() and '..' not in part.parts and name not in rows, 'Safe unique path')
        path = root / part
        require(not path.is_symlink() and path.is_file() and path.stat().st_nlink == 1, 'Regular copied file')
        raw = bounded_read(path, 4 * 1024**2, row['bytes'])
        stamps[name] = stamp(path)
        require(len(raw) == row['bytes'] <= 4 * 1024**2 and hashlib.sha256(raw).hexdigest() == row['sha256'], 'Saved bytes: ' + name)
        require(all(row[k] == row['original'][k] for k in ('sha256', 'bytes')), 'Copied/original descriptor equality')
        rows[name] = raw
        originals[row['original']['path']] = row
    require(sum(len(x) for x in rows.values()) == index['totalBytes'] == 2233749, 'Exact total bytes')
    nodes = list(root.rglob('*'))
    require(all(not p.is_symlink() for p in nodes), 'No linked packet nodes')
    require({p.relative_to(root).as_posix() for p in nodes if p.is_file()} == set(rows) | {'index.json'}, 'Closed saved file set')

    def raw_ref(ref):
        entry = originals.get(ref['path'])
        require(entry is not None and entry['original'] == ref, 'Saved typed reference')
        return rows[entry['path']]

    def doc(name):
        return json.loads(rows['files/' + name])

    plan, result = doc('proofs/plan.json'), doc('work/result.json')
    receipt, terminal = doc('proofs/owner-receipt.json'), doc('owner/terminal.json')
    authority, started = doc('proofs/authority.json'), doc('owner/started.json')
    guard, composition = doc('owner/world-guard.json'), doc('proofs/composition-review.json')
    require(receipt['rawExitCode'] == terminal['rawExitCode'] == 0 and receipt['cleanOwner'] and receipt['finalInputsPreserved'], 'Clean successful original owner')
    require(receipt['originalOwner'] == terminal['pid'] == started['pid'] == 22795 and started['timeoutSeconds'] == 900, 'Original owner identity and budget')
    for key in ('timeout', 'forcedCleanup', 'errors', 'signals', 'interruptedSignals', 'remainingObservedPids'):
        require(not terminal[key], 'Owner cleanup: ' + key)
    require(terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'], 'Owned process groups gone')
    require(receipt['invocationOrFinalizationError'] is None and not receipt['secondaryErrors'], 'No finalization uncertainty')
    require(guard['before'] == guard['after'] and guard['unchanged'] and guard['nativeInputsPreserved'], 'Original construction inputs preserved')
    require(json.loads(raw_ref(result['rootAuthority'])) == authority and terminal['authority'] == result['rootAuthority'], 'Actual authority joins')
    require(json.loads(raw_ref(result['plan'])) == plan and result['envelope'] == authority['envelope'] == composition['envelope'], 'Separate envelope runtime role')
    require(result['innerComponent'] == authority['innerComponent'] == composition['innerComponent'], 'Original inner retained')
    require(composition['verifiedPassed'] and composition['verifiedDataReviewPassed'] and len(composition['selectedImports']) == 13, 'Recorded composition proof')
    require(all(x.endswith('@0.2.10') for x in composition['selectedImports']) and composition['selectedExports'] == ['wasi:http/incoming-handler@0.2.10'], 'Recorded standard surface')
    ids = ['post-actions-valid', 'post-actions-missing', 'post-other-valid', 'post-actions-query-valid',
           'post-actions-duplicate', 'post-actions-uppercase', 'head-actions-unknown']
    require([x['id'] for x in plan['cases']] == result['declaredCases'] == result['attemptedCases'] == ids, 'Fixed seven cases')
    require(not result['unattemptedCases'] and not result['errors'] and len(result['cases']) == 7, 'Complete fixed suffix')
    summaries = []
    for slot, (expected, summary) in enumerate(zip(plan['cases'], result['cases']), 1):
        prefix = 'work/' + str(slot).zfill(2) + '-' + expected['id'] + '/'
        case = doc(prefix + 'result.json')
        require(json.loads(raw_ref(summary['actualResult'])) == case, 'Published case result')
        require({k:v for k,v in summary.items() if k != 'actualResult'} == case, 'Summary matches individual result')
        require(case['declaredCase'] == expected and case['caseId'] == expected['id'] and case['slot'] == slot, 'Case declaration')
        require(not case['errors'] and not case['semanticErrors'] and case['originalInputsPreserved'], 'No case uncertainty')
        for key in ('collectionCompletedCleanly', 'metadataAccepted', 'probeResponseAccepted', 'passed'):
            require(case[key] is True, 'Case acceptance: ' + key)
        server, capture, http = case['server'], case['stdoutCapture'], case['http']
        require(server['spawnAttempts'] == 1 and server['shutdownRequested'] and server['sigintSent'] and not server['forcedCleanup'], 'One host, normal shutdown')
        require(server['shutdownReason'] == 'case-collection-finished' and server['exit'] == dict(code=0, signal=None, error=None), 'Host exit')
        require(server['argv'] == [plan['wasmtime']['path'], 'serve', '--no-logging-prefix', '--addr', '127.0.0.1:' + str(case['portLease']['port']), '-S', 'cli=y,tcp=n,udp=n,allow-ip-name-lookup=n', '--max-instance-reuse-count', '128', '--idle-instance-timeout', '60s', result['envelope']['path']], 'Actual host arguments')
        require(case['readiness'] == dict(exactListener=True, tcpOnly=True, httpWarmupRequests=0), 'TCP-only readiness')
        require(capture['complete'] and capture['pipeEof'] and capture['fileClosed'] and capture['finalized'] and capture['fileBoundVerified'], 'Complete durable stdout')
        for key in ('overflow', 'partialWritePossible', 'unretainedBytesUnknown', 'errors'):
            require(not capture[key], 'Capture uncertainty: ' + key)
        raw = raw_ref(case['stdout'])
        require(len(raw) == capture['fileBytes'] == capture['completeWriteBytes'] <= 512, 'Bounded complete metadata line')
        metadata = json.loads(raw)
        require(raw == (json.dumps(metadata, separators=(',', ':')) + '\n').encode('ascii'), 'Canonical metadata bytes')
        require(list(metadata) == plan['recordKeys'] and metadata == expected['expectedRecord'] == case['observedMetadata'], 'Exact typed metadata')
        body = raw_ref(http['body'])
        require(http['status'] == expected['expectedStatus'] == 405 and http['complete'] and http['requestClosed'] and http['error'] is None and not http['overflow'] and not http['unretainedTailUnknown'], 'Complete expected HTTP result')
        require(http['bytes'] == len(body) and http['method'] == expected['method'] and http['path'] == expected['path'], 'HTTP request/body provenance')
        headers = ['Host', '127.0.0.1:' + str(case['portLease']['port']), 'Connection', 'close', 'Content-Length', '0']
        for value in expected['headerValues']:
            headers += [plan['headerName'], value]
        require(http['requestRawHeaders'] == headers, 'Exact sent header values')
        if expected['expectedBodyPolicy'] == 'empty-http-head':
            require(expected['method'] == 'HEAD' and body == b'', 'HEAD has no wire body')
        else:
            require(expected['expectedBodyPolicy'] == 'exact-json' and json.loads(body) == expected['expectedResponse'], 'Expected diagnostic POST JSON')
        require(rows['files/' + prefix + 'wasmtime.stderr.log'] == ('Serving HTTP on ' + case['portLease']['origin'] + '/\n').encode(), 'Final stderr listener record')
        summaries.append(dict(caseId=case['caseId'], metadata=metadata, status=405, bodyBytes=len(body), passed=True))
    require(all(result[k] is True for k in ('driverCompletedAllDeclaredCases', 'allCollectionsCompletedCleanly', 'allDeclaredMetadataAndResponsesAccepted', 'originalInputsPreserved', 'passed')), 'Aggregate result')
    require(result['fullNextAccepted'] is False and receipt['fullNextAccepted'] is False, 'No Next acceptance upgrade')
    require(all(stamp(root / name) == value for name, value in stamps.items()), 'Final payload bookends')
    require(bounded_read(root / 'index.json', 65536) == raw_index, 'Final index bookend')
    return dict(schemaVersion=1, state='V4_RETAINED_METADATA_PROBES_CHECK_PASSED_V1', payloadFiles=70,
        totalBytes=2233749, originalOwner=22795, metadataCasesPassed=7, cases=summaries,
        replayedHosts=False, openedOriginalPaths=False, allocatorOrAbsentPathExecuted=False,
        nextWorkloadExecuted=False, oldV3JoinUpgraded=False, fullNextAccepted=False)


if __name__ == '__main__':
    print(json.dumps(check()))
