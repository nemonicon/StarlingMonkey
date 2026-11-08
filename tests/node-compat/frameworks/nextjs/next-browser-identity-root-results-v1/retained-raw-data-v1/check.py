"""Portable offline identity-pair DATA verification; no original paths or JS."""
import hashlib
import json
from pathlib import Path
import re
import stat
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
CONTROLS = re.compile(r'[\x00-\x08\x0a-\x1f\x7f]')


def physical(path):
    s = path.lstat()
    return s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns


def bounded(path, size=None):
    assert path.resolve() == path and not path.is_symlink()
    before = physical(path)
    assert stat.S_ISREG(before[2]) and before[3] == 1 and 0 <= before[4] <= 20 * 1024 * 1024
    if size is not None:
        assert before[4] == size
    raw = path.read_bytes()
    assert physical(path) == before and len(raw) == before[4]
    return raw


def reconstruct(browser, netlog):
    origin = browser['origin']
    u = urlsplit(origin)
    assert origin == 'http://127.0.0.1:' + str(u.port)
    target = origin + '/actions'
    posts = [p for p in browser['actionPosts'] if p['url'] == target]
    responses = [r for r in browser['responseHeaders'] if r['test'] == 'server-action' and r['method'] == 'POST' and r['url'] == target]
    assert len(posts) == len(responses) == 1
    request_headers = []
    for post in posts:
        assert isinstance(post['headers'], dict)
        values = []
        for name, value in post['headers'].items():
            assert isinstance(value, str) and not CONTROLS.search(value)
            if name.lower() == 'accept-encoding':
                values.append(value.strip(' \t').lower())
        assert values == ['identity']
        request_headers.append(dict(url=post['url'], headers=post['headers'], acceptEncodingValues=values))
    response = responses[0]
    encodings = []
    for header in response['headers']:
        assert isinstance(header['name'], str) and isinstance(header['value'], str) and not CONTROLS.search(header['value'])
        if header['name'].lower() == 'content-encoding':
            encodings.append(header)
    assert encodings == [] and response['status'] == 200
    response_encodings = [dict(test=response['test'], requestId=response['requestId'], url=response['url'], method=response['method'], status=response['status'], contentEncoding=encodings)]
    c, events = netlog['constants'], netlog['events']
    candidates = {(e['source']['type'], e['source']['id']) for e in events if e.get('source', {}).get('type') == c['logSourceType']['URL_REQUEST'] and e.get('params', {}).get('url') == target and e.get('params', {}).get('method') == 'POST'}
    assert len(candidates) == 1
    witnesses = []
    for index, event in enumerate(events):
        if event['type'] != c['logEventTypes']['HTTP_TRANSACTION_SEND_REQUEST_HEADERS'] or (event['source']['type'], event['source']['id']) not in candidates:
            continue
        params = event['params']
        assert params['line'] == 'POST /actions HTTP/1.1' + chr(13) + chr(10)
        headers = params['headers']
        assert isinstance(headers, list) and len(headers) <= 256
        assert all(isinstance(h, str) and len(h) <= 8192 and not CONTROLS.search(h) for h in headers)
        def values(name):
            return [h.split(':', 1)[1].strip(' \t').lower() for h in headers if ':' in h and h.split(':', 1)[0].lower() == name]
        ae, hosts = values('accept-encoding'), values('host')
        assert ae == ['identity'] and hosts == [u.netloc]
        witnesses.append(dict(eventIndex=index, time=event['time'], sourceId=event['source']['id'], sourceTypeId=event['source']['type'], line=params['line'], headers=headers, acceptEncodingValues=ae, hostValues=hosts, identity=True))
    assert len(witnesses) == 1
    evidence = dict(observation='explicit-send-request-headers', candidateCount=1, witnesses=witnesses, identityObserved=True, explicitContradiction=False, historyCompleteProved=False, wireBytesOrEofProved=False)
    return dict(schemaVersion=1, state='BROWSER_OUTER_IDENTITY_NEGOTIATION_GATE_V1', requestedContextExtraHTTPHeaders={'Accept-Encoding': 'identity'}, targetUrl=target, postCount=1, responseHeaderCount=1, requestHeaders=request_headers, responseEncodings=response_encodings, playwrightRequestIdentity=True, netlog=evidence, requestIdentityObserved=True, responseEncodingAbsent=True, actualNetlogNegotiationVerified=True, passed=True, failures=[], sourceScope='Retained browser metadata and explicit NetLog header records; not raw HTTP wire bytes', innerSelfFetchEncodingProved=False, nativeAppendSelectedProved=False, privateStoreIdentityProved=False, uniqueCompressionCauseProved=False, fullNextAcceptance=False)


def main():
    manifest = json.loads(bounded(HERE / 'manifest.json'))
    assert manifest['copiedFileCount'] == len(manifest['files']) == 90
    assert manifest['copiedPayloadBytes'] == sum(r['copied']['bytes'] for r in manifest['files']) == 5625171 <= manifest['maximumPayloadBytes'] == 33554432
    payloads, original_rows, ids = {}, {}, set()
    for item in manifest['files']:
        copied, original = item['copied'], item['original']
        rel = Path(copied['relativePath'])
        assert not rel.is_absolute() and '..' not in rel.parts and rel.parts[0] == 'files'
        assert copied['relativePath'] not in payloads and original['path'] not in original_rows
        data = bounded(HERE / rel, copied['bytes'])
        assert hashlib.sha256(data).hexdigest() == copied['sha256'] == original['sha256']
        assert copied['bytes'] == original['bytes'] and copied['mode'] == original['mode']
        identity = physical(HERE / rel)[:2]
        assert identity not in ids
        ids.add(identity)
        payloads[copied['relativePath']] = data
        original_rows[original['path']] = item
        if rel.suffix == '.png':
            assert data.startswith(b'\x89PNG\r\n\x1a\n')
    checker = manifest['checker']
    assert checker['relativePath'] == 'check.py'
    assert hashlib.sha256(bounded(HERE / 'check.py', checker['bytes'])).hexdigest() == checker['sha256']
    assert {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()} == set(payloads) | {'manifest.json', 'check.py'}
    actual_dirs = {p.relative_to(HERE).as_posix() for p in [HERE, *HERE.rglob('*')] if p.is_dir()}
    assert actual_dirs == {d['relativePath'] for d in manifest['copiedDirectories']}
    assert all(not (HERE / d).is_symlink() for d in actual_dirs)
    def load(rel):
        return json.loads(payloads['files/' + rel])
    def original(ref):
        # Historical paths are immutable DATA keys; never retarget or read them.
        item = original_rows[ref['path']]
        assert {k: item['original'][k] for k in ['path', 'sha256', 'bytes']} == ref
        return payloads[item['copied']['relativePath']]
    protocol = load('root/protocol.json')
    assert protocol['contextExtraHTTPHeaders'] == {'Accept-Encoding': 'identity'}
    outcomes = {}
    for arm, seconds, code, count in [('native', 600, 1, 16), ('stock', 300, 0, 13)]:
        browser = load(arm + '/browser/result.json')
        host = load('native/client/result.json' if arm == 'native' else 'stock/actor/result.json')
        actor = load(arm + '/actor/result.json')
        authority = json.loads(original(protocol[arm + 'Authority']))
        assert browser['origin'] == host['origin']
        assert host['browserArgv'][1] == protocol['sharedBrowserWorker']['path']
        assert host['browserArgv'][2:4] == ['--origin', browser['origin']]
        assert browser['functionalPassed'] is browser['browserClosed'] is browser['assetCapturePassed'] is True
        assert len(browser['tests']) == 2 and all(t['passed'] is True and t['timedOut'] is False for t in browser['tests'])
        free = not (browser['pageerrors'] or browser['consoleerrors'] or browser['failedrequests'])
        strict = free and not browser['errors'] and browser['browserClosed']
        assert browser['browserErrorFree'] == free and browser['passed'] == strict == (arm == 'stock')
        assert actor['passed'] == host['passed'] == strict
        assert host['cacheInvalidation']['passed'] == (arm == 'stock')
        assert host['cacheInvalidation']['before']['generation'] == 1 and host['cacheInvalidation']['after']['generation'] == (1 if arm == 'native' else 2)
        if arm == 'native':
            assert len(browser['errors']) == 3 and all(e['message'] == 'net::ERR_ABORTED' for e in browser['errors'])
        else:
            assert browser['errors'] == browser['failedrequests'] == []
        netlog = json.loads(original(browser['netlog']['file']))
        assert netlog['constants']['logCaptureMode'] == 'Default'
        assert browser['netlog']['completeJson'] is browser['netlog']['fsynced'] is True and browser['netlog']['errors'] == []
        assert len(netlog['events']) == browser['netlog']['eventCount']
        reconstructed = reconstruct(browser, netlog)
        assert reconstructed == browser['identityNegotiation'] == host['browser']['identityNegotiation']
        start, terminal, observation = [load(arm + '/owner/' + name + '.json') for name in ['started', 'terminal', 'observation']]
        assert start['timeoutSeconds'] == seconds and start['pid'] == terminal['pid']
        assert start['authority'] == terminal['authority'] == protocol[arm + 'Authority']
        assert terminal['rawExitCode'] == code and terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
        assert terminal['timeout'] is terminal['forcedCleanup'] is False and terminal['operationalElapsedSeconds'] < seconds
        assert all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
        assert all(group['alive'] is group['signalAllowed'] is False for group in terminal['finalGroups'])
        assert len(terminal['observedProcesses']) == count
        for i, process in enumerate(terminal['observedProcesses']):
            owned = load(arm + '/owner/owned-' + str(i).zfill(4) + '.json')
            assert owned['sequence'] == i and owned['process'] == process
        original(terminal['stdout'])
        original(terminal['stderr'])
        assert json.loads(original(observation['result'])) == actor
        assert json.loads(original(observation['terminal'])) == terminal
        assert observation['rawExitCode'] == code and observation['ownedGroupsClean'] is observation['protectedInputsPreserved'] is True
        frames = [json.loads(line) for line in payloads['files/root/' + arm + '.stdout.log'].splitlines() if line]
        assert frames == [dict(pid=start['pid'], timeoutSeconds=seconds), observation] and payloads['files/root/' + arm + '.stderr.log'] == b''
        outcomes[arm] = dict(rawExitCode=code, identityNegotiation=True, strictBrowserPassed=strict, legacyCachePassed=host['cacheInvalidation']['passed'], netlogEvents=len(netlog['events']))
    world = load('root/cleanup-476b-identity-native-first-full-world-guard.json')
    native_authority = json.loads(original(protocol['nativeAuthority']))
    assert world['authority'] == protocol['nativeAuthority'] and world['before'] == world['after']
    assert world['unchanged'] is world['nativeInputsPreserved'] is True
    assert world['before']['sourceIndex'] == native_authority['worldSourceIndex'] and world['before']['members'] == 28 and world['before']['witFiles'] == 8
    primary = load('root/actual-runtime-review.json')
    assert primary['verifiedDataReviewPassed'] is primary['actualOuterIdentityNegotiationVerifiedBoth'] is True
    assert primary['nativeExperimentPassed'] is False and primary['stockHostExperimentPassed'] is True
    assert primary['priorFailedGatesAccepted'] is primary['uniqueCauseProved'] is primary['innerSelfFetchEncodingProved'] is False
    print(json.dumps(dict(passed=True, state='PORTABLE_OFFLINE_OUTER_IDENTITY_RAW_DATA_VERIFIED_V1', copiedFiles=90, copiedBytes=5625171, outcomes=outcomes, originalPathsRead=False, jsGateAnalyzerOrActorInvoked=False, historicalModesAndInodesDocumentary=True, observedCheckoutFileModes=sorted({stat.S_IMODE((HERE / name).stat().st_mode) for name in payloads}), innerSelfFetchEncodingProved=False, privateStoreIdentityProved=False, uniqueCauseProved=False, priorFailedGatesAccepted=False, fullNextAcceptance=False)))


if __name__ == '__main__':
    main()
