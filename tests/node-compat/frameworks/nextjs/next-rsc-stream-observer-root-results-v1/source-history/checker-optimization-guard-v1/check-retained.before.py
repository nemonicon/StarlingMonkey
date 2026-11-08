"""Saved-sample regression only. Root must bind three pins before any file IO.
Run with Python -I -B. Original absolute paths are tuple keys, never opened.
This captured cloud MUST remain strict/full failed; Node MUST remain passed.
"""
import base64
import hashlib
import json
from pathlib import Path
import re
import sys

EXPECTED_INDEX_SHA256 = None
EXPECTED_PAYLOAD_FILES = None
EXPECTED_PAYLOAD_BYTES = None


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    assert type(EXPECTED_INDEX_SHA256) is str and re.fullmatch('[0-9a-f]{64}', EXPECTED_INDEX_SHA256)
    assert type(EXPECTED_PAYLOAD_FILES) is int and 0 < EXPECTED_PAYLOAD_FILES <= 1024
    assert type(EXPECTED_PAYLOAD_BYTES) is int and 0 < EXPECTED_PAYLOAD_BYTES <= 64 * 1024 * 1024
    root = Path(__file__).resolve().parent / 'raw-records'
    stamps = {}

    def read(path, cap):
        assert path.resolve() == path and not path.is_symlink()
        a = path.stat()
        assert path.is_file() and a.st_nlink == 1 and 0 <= a.st_size <= cap
        stamp = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        raw = path.read_bytes()
        assert len(raw) == a.st_size and stamp(a) == stamp(path.stat())
        if path in stamps:
            assert stamps[path] == stamp(a)
        stamps[path] = stamp(a)
        return raw

    raw_index = read(root / 'index.json', 2 * 1024 * 1024)
    assert hashlib.sha256(raw_index).hexdigest() == EXPECTED_INDEX_SHA256
    index = json.loads(raw_index)
    rows = index['files']
    assert len(rows) == index['payloadFiles'] == EXPECTED_PAYLOAD_FILES
    assert sum(r['bytes'] for r in rows) == index['totalBytes'] == EXPECTED_PAYLOAD_BYTES
    paths = [r['path'] for r in rows]
    assert paths == sorted(paths) and len(set(paths)) == len(paths)
    for r in rows:
        rel = Path(r['path'])
        assert not rel.is_absolute() and rel.parts and all(s not in ('.', '..') for s in rel.parts)
        assert type(r['bytes']) is int and 0 <= r['bytes'] <= 20 * 1024 * 1024
        assert r['original']['bytes'] == r['bytes'] and r['original']['sha256'] == r['sha256']
    surfaces = list(root.rglob('*'))
    assert all(not p.is_symlink() for p in surfaces)
    assert {p.relative_to(root).as_posix() for p in surfaces if p.is_file()} == set(paths) | {'index.json'}
    blobs, tuples = {}, {}
    for r in rows:
        raw = read(root / r['path'], 20 * 1024 * 1024)
        assert len(raw) == r['bytes'] and hashlib.sha256(raw).hexdigest() == r['sha256']
        key = (r['original']['path'], r['sha256'], r['bytes'])
        assert key not in tuples
        blobs[r['path']], tuples[key] = raw, raw
    assert len({(s[0], s[1]) for s in stamps.values()}) == len(stamps)

    def doc(path):
        return json.loads(blobs[path])

    def refbytes(ref):
        assert set(ref) == {'path', 'sha256', 'bytes'} and type(ref['path']) is str
        return tuples[(ref['path'], ref['sha256'], ref['bytes'])]

    def b64(value):
        raw = base64.b64decode(value, validate=True)
        assert base64.b64encode(raw).decode() == value
        return raw

    def publication(ref, flags):
        assert all(flags[k] is True for k in ('complete', 'fsynced', 'closed')) and flags['errors'] == []
        assert flags['fileBytes'] == ref['bytes'] and flags['sha256'] == ref['sha256']
        return refbytes(ref)

    failed_prepare = doc('files/root/prepare-attempt1-failure.json')
    assert failed_prepare['rawExitCode'] == 1 and failed_prepare['error']['key'] == 'outerSeconds'
    assert failed_prepare['issuedPreparationOrAuthority'] is False and failed_prepare['actorsInvoked'] is False
    assert doc('files/root/prepare-correction-peer-review.json')['priorSourcePassQualified'] is True
    outcomes = {}
    for arm, pid, seconds, raw_exit, accepted in (('cloud', 67923, 600, 1, False), ('stock', 68512, 300, 0, True)):
        prefix = 'files/' + arm + '/work/'
        owner = doc('files/root/' + arm + '-owner-result.json')
        terminal, started = doc('files/' + arm + '/owner/terminal.json'), doc('files/' + arm + '/owner/started.json')
        assert owner['originalOwner'] == terminal['pid'] == started['pid'] == pid
        assert owner['rawExitCode'] == terminal['rawExitCode'] == raw_exit and started['timeoutSeconds'] == seconds
        assert owner['cleanOwner'] is owner['finalInputsPreserved'] is True and owner['error'] is None and owner['secondaryErrors'] == []
        assert terminal['timeout'] is terminal['forcedCleanup'] is False and terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
        assert all(terminal[k] == [] for k in ('signals', 'interruptedSignals', 'errors', 'remainingObservedPids'))
        assert owner['constructorGuardBefore'] == owner['constructorGuardAfter']
        assert json.loads(refbytes(owner['terminal'])) == terminal
        refbytes(terminal['stdout']); refbytes(terminal['stderr']); refbytes(owner['authority'])
        actual, client, browser = doc(prefix + 'result.json'), doc(prefix + 'client/result.json'), doc(prefix + 'client/browser/result.json')
        assert actual['rootAuthority'] == owner['authority'] and actual['passed'] is accepted
        assert client['browser'] == browser and client['suite'] == 'NEXT_RSC_STREAM_OBSERVER_FULL_CONTRACT_CLIENT_V1'
        assert actual['fullOriginalContractExecuted'] is client['fullOriginalContractExecuted'] is True
        assert actual['fullNextAccepted'] is client['fullNextAccepted'] is False and client['controlOnly'] is False
        assert client['errors'] == client['transportErrors'] == [] and len(client['http']) == 24
        for h in client['http']:
            raw = blobs[prefix + 'client/responses/' + h['id'] + '.txt']
            assert h['passed'] is True and len(raw) == h['bodyBytes'] and hashlib.sha256(raw).hexdigest() == h['bodySha256']
        assert client['portableCacheValidation']['passed'] is client['supplementalValidation']['passed'] is True
        assert client['portableCacheValidation']['checks'] == 52 and client['supplementalValidation']['checks'] == 80
        assert len(client['portableCache']['records']) == 5 and len(client['supplemental']['observations']) == 6
        for r in client['portableCache']['records']:
            raw = refbytes(r['body']); assert raw == b64(r['bodyBase64']) and r['complete'] is True and r['overflow'] is False
            assert r['transportError'] is None and r['cleanupErrors'] == [] and r['receivedBytes'] == r['retainedBytes'] == len(raw)
        for r in client['supplemental']['observations']:
            assert refbytes(r['body']) == b64(r['bodyBase64']) and r['bodyEofObserved'] is True and r['signalAborted'] is False
            assert all(r[k] is None for k in ('error', 'readerReleaseError', 'publicationError'))
        assert client['cacheInvalidation']['before']['generation'] == 1 and client['cacheInvalidation']['after']['generation'] == 2 and client['cacheInvalidation']['passed'] is True
        assert blobs['files/' + arm + '/callback/generation.json'] == b'{"schemaVersion":1,"generation":2}\n'
        chunks = doc(prefix + 'client/stream-chunks.json'); body = b''; shell = ready = -1
        for i, chunk in enumerate(chunks):
            raw = b64(chunk['base64']); assert len(raw) == chunk['bytes']; body += raw
            if shell < 0 and b'NEXT_STREAM_SHELL' in body: shell = i
            if ready < 0 and b'NEXT_STREAM_READY' in body: ready = i
        assert len(chunks) == client['streaming']['chunks'] == 3 and (shell, ready) == (0, 1)  # This saved sample only.
        assert client['streaming']['complete'] is client['streaming']['incrementalDeliveryObserved'] is True
        assert [t['id'] for t in browser['tests']] == ['client-counter', 'server-action'] and all(t['passed'] and not t['timedOut'] and not t['cdpObserver']['stopped'] for t in browser['tests'])
        assert browser['functionalPassed'] is browser['assetCapturePassed'] is browser['browserClosed'] is True and len(browser['assetBodies']) == 9
        assert browser['pageerrors'] == browser['consoleerrors'] == [] and len(browser['errors']) == (0 if accepted else 3) and len(browser['failedrequests']) == (0 if accepted else 1)
        strict = browser['functionalPassed'] and all(browser[k] == [] for k in ('pageerrors', 'consoleerrors', 'failedrequests', 'errors')) and browser['browserClosed']
        original = all(h['passed'] for h in client['http']) and client['cacheInvalidation']['passed'] and client['streaming']['complete'] and client['streaming']['incrementalDeliveryObserved'] and client['browserExit']['code'] == 0 and strict and client['errors'] == client['transportErrors'] == []
        assert browser['passed'] is browser['browserErrorFree'] is strict and strict is accepted
        assert client['originalContractPassed'] is original and client['passed'] is (original and client['portableCacheValidation']['passed'] and client['supplementalValidation']['passed']) and original is accepted
        stream = browser['resourceStreamObservation']; record = stream['observations'][0]; admission = record['admission']
        assert len(stream['observations']) == 1 and stream['finalized'] is stream['collectionComplete'] is stream['commandSuccess'] is True and stream['errors'] == []
        assert record['collectionComplete'] is record['handoffSuccessful'] is record['prefixCountConsistency'] is record['payloadsComplete'] is True and record['errors'] == []
        assert record['command']['method'] == 'Network.streamResourceContent' and record['command']['trigger'] == 'first-qualified-requestWillBeSent' and record['reply']['outcome'] == 'fulfilled'
        request_id = record['candidates'][0]['requestId']; assert len(record['candidates']) == len(record['terminals']) == 1 and record['command']['params'] == {'requestId': request_id}
        data = [e for e in browser['cdpEvents'] if e['test'] == 'server-action' and e['event'] == 'Network.dataReceived' and e['payload']['requestId'] == request_id]
        prefix_bytes = b64(record['reply']['result']['bufferedData']); assert prefix_bytes == b'' and len(data) == 1
        piece = b64(data[0]['payload']['data']); assert len(piece) == data[0]['payload']['dataLength'] == 2963 and record['countOnlyBeforeActivation'] == []
        artifact = publication(record['artifact'], record['publication']); assert artifact == prefix_bytes + piece
        assert record['body']['bytes'] == len(artifact) and record['body']['sha256'] == hashlib.sha256(artifact).hexdigest() and record['body']['contiguousFromStart'] is True
        assert [p['bytes'] for p in record['pieces']] == [0, 2963] and [p['sha256'] for p in record['pieces']] == [hashlib.sha256(prefix_bytes).hexdigest(), hashlib.sha256(piece).hexdigest()]
        assert stream['completeResourceBody'] is stream['accepted'] is record['completeBody'] is record['completeResourceBody'] is record['body']['complete'] is accepted
        terminal_event = record['terminals'][0]; assert terminal_event['payload']['requestId'] == request_id and terminal_event['event'] == ('Network.loadingFinished' if accepted else 'Network.loadingFailed')
        if not accepted: assert terminal_event['payload']['canceled'] is True and terminal_event['payload']['errorText'] == 'net::ERR_ABORTED'
        request = publication(admission['actualRequestBody'], admission['actualRequestBodyPublication']); assert len(request) == 391 and admission['passed'] is admission['CDPBodyMatchedPlaywright'] is admission['publicContextVerified'] is True
        action_id = stream['requiredActionId']; manifest = json.loads(refbytes(stream['actualActionManifest'])); action = manifest['node'][action_id]
        assert action['exportedName'] == 'submitFixture' and action['filename'] == 'app/actions/actions.js' and set(action['workers']) == {'app/actions/page'}
        post = [p for p in browser['actionPosts'] if p['url'] == client['origin'] + '/actions']; assert len(post) == 1 and b64(post[0]['bodyBase64']) == request
        reqs = [e for e in browser['cdpEvents'] if e['test'] == 'server-action' and e['event'] == 'Network.requestWillBeSent' and e['payload']['requestId'] == request_id]; assert len(reqs) == 1 and reqs[0]['payload']['request']['postData'].encode() == request
        extra = [e for e in browser['cdpEvents'] if e['test'] == 'server-action' and e['event'] == 'Network.requestWillBeSentExtraInfo' and e['payload']['requestId'] == request_id]; assert len(extra) == 1
        headers = {k.lower(): v for k, v in extra[0]['payload']['headers'].items()}; assert headers['next-action'] == action_id and headers['x-next-public-request-correlation'] == '8' * 64 and headers['origin'] == client['origin'] and headers['referer'] == post[0]['url']
        boundary = re.fullmatch(r'multipart/form-data; boundary=([A-Za-z0-9-]{1,70})', headers['content-type']).group(1)
        parts = request.decode().split('--' + boundary); assert parts.pop(0) == '' and parts.pop() == '--\r\n'
        parsed = [re.fullmatch(r'\r\nContent-Disposition: form-data; name="([^"\r\n]+)"\r\n\r\n([\s\S]*)\r\n', p) for p in parts]; assert len(parsed) == 3 and all(parsed)
        assert {p[1]: p[2] for p in parsed} == {'_1_$ACTION_ID_' + action_id: '', '_1_value': 'browser-action', '0': '["$K1"]'}
        responses = [r for r in browser['responseHeaders'] if r['method'] == 'POST']; assert len(responses) == 1 and responses[0]['status'] == 200
        headers = {h['name'].lower(): h['value'] for h in responses[0]['headers']}; assert 'content-encoding' not in headers and headers['transfer-encoding'] == 'chunked'
        body_row = [r for r in browser['bodyCaptures'] if r['method'] == 'POST'][0]; finished = [r for r in browser['responseFinishedObservations'] if r['method'] == 'POST'][0]
        if accepted: assert refbytes(body_row['decodedBody']) == artifact and body_row['bodyCompletion']['kind'] == body_row['sizesCompletion']['kind'] == finished['completion'] == 'fulfilled'
        else: assert body_row['decodedBody'] is body_row['encodedSizes'] is None and body_row['bodyCompletion']['kind'] == body_row['sizesCompletion']['kind'] == finished['completion'] == 'requestfailed'
        netlog = browser['netlog']; net = json.loads(refbytes(netlog['file'])); assert netlog['completeJson'] is netlog['fsynced'] is True and netlog['errors'] == [] and len(net['events']) == netlog['eventCount']
        if arm == 'cloud':
            assert actual['originalInputsPreserved'] is actual['readonlyAppPreserved'] is actual['configVerifiedBeforeDev'] is True and len(actual['emittedImports']) == 13 and all(s.endswith('@0.2.10') for s in actual['emittedImports'])
            for command in actual['commands'][:2]:
                capture = command['stdoutCapture']; assert command['exit'] == {'code': 0, 'signal': None, 'error': None}
                assert all(capture[k] is True for k in ('complete', 'pipeEof', 'fileClosed', 'fileBoundVerified', 'finalized')) and capture['errors'] == [] and all(capture[k] is False for k in ('overflow', 'partialWritePossible', 'unretainedBytesUnknown'))
                assert len(refbytes(command['stdout'])) == capture['fileBytes'] == capture['completeWriteBytes'] == capture['lastReservedWriteCeiling'] <= 8388608
            assert actual['server']['shutdownRequested'] is actual['server']['sigintSent'] is True and actual['server']['forcedCleanup'] is False
        else: assert actual['originalDependencyInputsPreserved'] is actual['originalApplicationInputsPreserved'] is True
        outcomes[arm] = {'fullContractPassed': accepted, 'strictPassed': strict, 'collectionComplete': True, 'resourceComplete': accepted, 'requestSha256': hashlib.sha256(request).hexdigest(), 'observedResourceSha256': hashlib.sha256(artifact).hexdigest()}
    for path, before in stamps.items():
        s = path.stat(); assert before == (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    print(json.dumps({'state': 'SAVED_RSC_STREAM_OBSERVER_REGRESSION_PASSED_V1', 'passed': True, 'payloadFiles': len(rows), 'payloadBytes': index['totalBytes'], 'arms': outcomes, 'fullNextAccepted': False, 'freshTargetsExecuted': False, 'originalPathReads': False, 'scope': 'Frozen saved sample only; cloud remains failed/incomplete. Resource bytes are not raw wire, parser/host EOF, React reader.done, private identity or cause.'}))


if __name__ == '__main__':
    main()
