"""Root DATA review of the original fixed V4 pair. Never launches a target."""
import base64
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
stamps = {}
offline_blobs = None
offline_summary = None


def load_retained():
    """Authenticate only checkout-local copies; original paths remain lookup keys."""
    global HERE, BASE, offline_blobs, offline_summary
    local = Path(__file__).resolve().parent
    expected = json.loads(raw(local / 'retained-expectations.json'))
    index_raw = raw(local / 'raw-records/index.json')
    assert hashlib.sha256(index_raw).hexdigest() == expected['indexSHA256']
    index = json.loads(index_raw)
    rows = index['files']
    assert len(rows) == index['payloadFiles'] == expected['payloadFiles'] <= 1024
    assert sum(r['bytes'] for r in rows) == index['totalBytes'] == expected['payloadBytes'] <= 64 * 1024**2
    names = [r['path'] for r in rows]
    assert names == sorted(names) and len(set(names)) == len(names)
    root = local / 'raw-records'
    nodes = list(root.rglob('*'))
    assert all(not p.is_symlink() for p in nodes)
    assert {p.relative_to(root).as_posix() for p in nodes if p.is_file()} == set(names) | {'index.json'}
    data = {}
    for item in rows:
        rel = Path(item['path'])
        assert not rel.is_absolute() and '..' not in rel.parts and rel.as_posix() == item['path']
        content = raw(root / rel)
        assert len(content) == item['bytes'] and hashlib.sha256(content).hexdigest() == item['sha256']
        original = item['original']
        assert original['sha256'] == item['sha256'] and original['bytes'] == item['bytes']
        assert original['path'] not in data
        data[original['path']] = content
    assert len({(s[0], s[1]) for s in stamps.values()}) == len(stamps)
    HERE = Path(index['originalRoot'])
    BASE = HERE.parent
    assert data[str(HERE / 'review-runtime.py')] == raw(local / 'review-runtime.py')
    offline_blobs = data
    offline_summary = expected


def stamp(path):
    s = path.stat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def raw(path):
    path = Path(path)
    if offline_blobs is not None:
        return offline_blobs[str(path)]
    assert path.is_absolute() and path.resolve() == path and path.is_file() and not path.is_symlink()
    before = stamp(path)
    assert before[3] == 1 and 0 <= before[4] <= 20 * 1024**2
    with path.open('rb') as f:
        data = f.read(20 * 1024**2 + 1)
    assert len(data) == before[4] and before == stamp(path)
    assert path not in stamps or stamps[path] == before
    stamps[path] = before
    return data


def row(path):
    data = raw(path)
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def doc(path):
    return json.loads(raw(path))


def checked(ref):
    assert set(ref) == {'path', 'sha256', 'bytes'} and row(Path(ref['path'])) == ref
    return raw(Path(ref['path']))


def decode(value):
    data = base64.b64decode(value, validate=True)
    assert base64.b64encode(data).decode() == value
    return data


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use nonoptimized Python -I -B; checks must remain enabled')
    assert sys.argv[1:] in ([], ['--retained'])
    if sys.argv[1:] == ['--retained']:
        load_retained()
    preparation = doc(HERE / 'control-preparation.json')
    binding = doc(HERE / 'runtime-bindings.json')
    composition = json.loads(checked(binding['compositionReview']))
    assert [t['arm'] for t in preparation['trials']] == ['cloud', 'stock']
    results = {}
    for trial in preparation['trials']:
        arm, work = trial['arm'], Path(trial['outputRoot'])
        owner = doc(HERE / (arm + '-owner-result.json'))
        terminal = json.loads(checked(owner['terminal']))
        started = doc(Path(trial['ownerOutputRoot']) / 'started.json')
        assert owner['authority'] == trial['authority'] and owner['originalOwner'] == terminal['pid'] == started['pid']
        assert started['timeoutSeconds'] == trial['ownerSeconds'] == (600 if arm == 'cloud' else 300)
        assert owner['rawExitCode'] == terminal['rawExitCode'] and type(terminal['rawExitCode']) is int
        assert terminal['rawExitCode'] in (0, 1)
        assert owner['cleanOwner'] and owner['finalInputsPreserved'] and owner['error'] is None and owner['secondaryErrors'] == []
        assert owner['constructorGuardBefore'] == owner['constructorGuardAfter']
        assert terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone']
        assert not terminal['timeout'] and not terminal['forcedCleanup']
        assert all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
        checked(terminal['stdout']); checked(terminal['stderr']); checked(owner['authority'])
        actual, client, browser = doc(work / 'result.json'), doc(work / 'client/result.json'), doc(work / 'client/browser/result.json')
        assert actual['rootAuthority'] == owner['authority']
        assert json.loads(checked(owner['authority']))['sourceIndex'] == binding['actorIndex']
        assert client['browser'] == browser and client['errors'] == client['transportErrors'] == []
        assert actual['fullOriginalContractExecuted'] is client['fullOriginalContractExecuted'] is True
        assert actual['fullNextAccepted'] is client['fullNextAccepted'] is False
        assert len(client['http']) == 24
        for request in client['http']:
            body = raw(work / 'client/responses' / (request['id'] + '.txt'))
            assert len(body) == request['bodyBytes'] and hashlib.sha256(body).hexdigest() == request['bodySha256']
        for item in client['portableCache']['records']:
            body = checked(item['body'])
            assert body == decode(item['bodyBase64']) and item['complete'] and not item['overflow']
            assert item['transportError'] is None and item['cleanupErrors'] == []
            assert item['receivedBytes'] == item['retainedBytes'] == len(body)
        for item in client['supplemental']['observations']:
            assert checked(item['body']) == decode(item['bodyBase64']) and item['bodyEofObserved'] and not item['signalAborted']
            assert all(item[k] is None for k in ('error', 'readerReleaseError', 'publicationError'))
        chunks = doc(work / 'client/stream-chunks.json')
        body, shell, ready = b'', -1, -1
        for i, chunk in enumerate(chunks):
            piece = decode(chunk['base64']); assert len(piece) == chunk['bytes']; body += piece
            if shell < 0 and b'NEXT_STREAM_SHELL' in body: shell = i
            if ready < 0 and b'NEXT_STREAM_READY' in body: ready = i
        assert (len(chunks), shell, ready) == (client['streaming']['chunks'], client['streaming']['shellChunk'], client['streaming']['readyChunk'])
        assert client['streaming']['complete'] is (shell >= 0 and ready >= 0)
        assert client['streaming']['incrementalDeliveryObserved'] is (ready > shell and shell >= 0)
        assert [t['id'] for t in browser['tests']] == ['client-counter', 'server-action']
        assert browser['functionalPassed'] is all(t['passed'] for t in browser['tests'])
        assert all(not t['timedOut'] and not t['cdpObserver']['stopped'] for t in browser['tests'])
        assert browser['browserClosed'] and browser['browserVersion'] == '157.0.8103.39' and browser['playwrightVersion'] == '1.64.1'
        strict = browser['functionalPassed'] and all(browser[k] == [] for k in ('pageerrors', 'consoleerrors', 'failedrequests', 'errors')) and browser['browserClosed']
        assert browser['browserErrorFree'] is all(browser[k] == [] for k in ('pageerrors', 'consoleerrors', 'failedrequests'))
        assert browser['passed'] is strict
        original = all(h['passed'] for h in client['http']) and client['cacheInvalidation']['passed'] and client['streaming']['complete'] and client['streaming']['incrementalDeliveryObserved'] and client['browserExit']['code'] == 0 and strict
        full = original and client['portableCacheValidation']['passed'] and client['supplementalValidation']['passed']
        assert client['originalContractPassed'] is original and client['passed'] is full
        stream = browser['resourceStreamObservation']
        assert stream['finalized'] and stream['collectionComplete'] and stream['errors'] == [] and len(stream['observations']) == 1
        record = stream['observations'][0]
        assert record['collectionComplete'] and record['admission']['passed'] and record['admission']['errors'] == []
        artifacts = {}
        for role, ref, publication in [('request', record['admission']['actualRequestBody'], record['admission']['actualRequestBodyPublication']),
                                       ('resource', record['artifact'], record['publication'])]:
            data = checked(ref)
            assert all(publication[k] for k in ('complete', 'fsynced', 'closed')) and publication['errors'] == []
            assert publication['fileBytes'] == len(data) and publication['sha256'] == ref['sha256']
            artifacts[role] = ref
        assert len(record['candidates']) == len(record['terminals']) == 1
        request_id = record['candidates'][0]['requestId']
        assert record['command']['method'] == 'Network.streamResourceContent' and record['command']['params'] == dict(requestId=request_id)
        assert record['terminals'][0]['payload']['requestId'] == request_id
        assert stream['accepted'] is (stream['collectionComplete'] and stream['completeResourceBody'])
        netlog = json.loads(checked(browser['netlog']['file']))
        assert browser['netlog']['completeJson'] and browser['netlog']['fsynced'] and browser['netlog']['errors'] == []
        assert browser['netlog']['eventCount'] == len(netlog['events'])
        if arm == 'cloud':
            assert actual['sourceIndex'] == binding['actorIndex']
            assert actual['servedEnvelope'] == composition['envelope']
            assert actual['originalInputsPreserved'] and actual['readonlyAppPreserved'] and actual['configVerifiedBeforeDev']
            assert sorted(actual['emittedImports']) == sorted(composition['selectedImports']) and len(actual['emittedImports']) == 13
            assert all(value.endswith('@0.2.10') for value in actual['emittedImports'])
            server = actual['server']
            assert server['shutdownRequested'] and server['sigintSent'] and not server['forcedCleanup']
            assert server['exit'] == dict(code=0, signal=None, error=None)
            capture = server['stdoutCapture']
            assert all(capture[k] for k in ('complete', 'pipeEof', 'fileClosed', 'fileBoundVerified', 'finalized'))
            assert all(not capture[k] for k in ('overflow', 'partialWritePossible', 'unretainedBytesUnknown')) and capture['errors'] == []
            assert len(checked(server['stdout'])) == capture['fileBytes'] == capture['completeWriteBytes'] == capture['lastReservedWriteCeiling']
        else:
            assert actual['originalDependencyInputsPreserved'] and actual['originalApplicationInputsPreserved']
        results[arm] = dict(actualResult=row(work / 'result.json'), ownerResult=row(HERE / (arm + '-owner-result.json')),
            clientResult=row(work / 'client/result.json'), browserResult=row(work / 'client/browser/result.json'),
            originalOwner=owner['originalOwner'], ownerSeconds=trial['ownerSeconds'], rawExitCode=terminal['rawExitCode'],
            cleanOwner=True, finalInputsPreserved=True, actorPassed=actual['passed'], actorErrors=actual['errors'],
            httpPassed=sum(h['passed'] for h in client['http']), httpTotal=len(client['http']),
            portable=client['portableCacheValidation'], supplemental=client['supplementalValidation'],
            cache=client['cacheInvalidation'], streaming=client['streaming'], uiPassed=sum(t['passed'] for t in browser['tests']),
            assetsPassed=browser['assetCapturePassed'], strictPassed=strict, fullContractPassed=full,
            browserErrors={k: browser[k] for k in ('pageerrors', 'consoleerrors', 'failedrequests', 'errors')},
            resourceCollectionComplete=stream['collectionComplete'], resourceCommandSuccess=stream['commandSuccess'],
            resourceComplete=stream['completeResourceBody'], resourceTerminal=record['terminals'][0], artifacts=artifacts)
    assert all(stamp(p) == before for p, before in stamps.items())
    result = dict(schemaVersion=1, state='ROOT_V4_FULL_PAIR_DATA_REVIEW_COMPLETED_V1', verifiedDataReviewPassed=True,
        actualReviewer=row(HERE / 'review-runtime.py'), runtimeBindings=row(HERE / 'runtime-bindings.json'),
        compositionReview=binding['compositionReview'], browserToolSelection=row(HERE / 'browser-tool-selection.json'),
        arms=results, fixedOrder=['cloud', 'stock'], fullOriginalContractExecuted=True,
        allFullContractsPassed=all(r['fullContractPassed'] for r in results.values()),
        oldFailuresWaived=False, browserChangedFromOldSample=True, runtimeFixClaimed=False,
        privateIdentityProved=False, fullNextAccepted=False,
        limits=['One fixed sample per arm', 'Chrome157 differs from historical Chrome156',
                'Public-tuple admission is separately reviewed', 'No lifecycle, clean-machine, performance or production acceptance'])
    path = HERE / 'actual-runtime-review.json'
    if offline_blobs is not None:
        assert result == doc(path), 'Recomputed saved review must match the original review exactly'
        assert all(stamp(p) == before for p, before in stamps.items())
        print(json.dumps(dict(state='SAVED_V4_FULL_PAIR_REGRESSION_PASSED_V1', passed=True,
            payloadFiles=offline_summary['payloadFiles'], payloadBytes=offline_summary['payloadBytes'],
            arms={k: {n: r[n] for n in ('rawExitCode', 'strictPassed', 'fullContractPassed', 'resourceComplete')} for k, r in results.items()},
            originalPathReads=False, freshTargetsExecuted=False, fullNextAccepted=False)))
        return
    with path.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps(dict(review=row(path), arms={k: {n: r[n] for n in ('rawExitCode', 'strictPassed', 'fullContractPassed', 'resourceComplete')} for k, r in results.items()})))


if __name__ == '__main__':
    main()
