"""Finite DATA review of the three original clone-cancel full-contract runs.

Usage: python -I -B review-results.py BINDINGS_PATH BINDINGS_SHA [--output FRESH_JSON]
Never imports a project module or launches a command. The sealed binding and its
admitted construction/build/tool proofs supply ancestry; this reviewer does not
replay that admission or expand its protected-input graph. It checks the actual
generic command -> actor -> runtime authority joins and closed workload evidence.
Semantic negatives are outcomes. Missing, inconsistent or uncertain collection
is reported separately and prevents a verified three-arm data-review result.
"""
import argparse
import base64
import codecs
import hashlib
import json
from pathlib import Path
import re
import stat
import sys
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
SUITE = 'NEXT_RSC_STREAM_OBSERVER_FULL_CONTRACT_CLIENT_V1'
ORDER = ('wasmtime', 'cloud', 'stock')
CAPS = (600, 600, 300)
MAX_FILE = 24 * 1024**2
MAX_TOTAL = 256 * 1024**2
stamps, directory_stamps, observed_refs, total_read = {}, {}, {}, 0


def need(value, message):
    if value is not True:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def stamp(path):
    s = path.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
            s.st_mtime_ns, s.st_ctime_ns)


def raw(path, cap=MAX_FILE):
    global total_read
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path, 'Noncanonical input: ' + str(path))
    before = stamp(path)
    need(stat.S_ISREG(before[2]) and before[3] == 1 and 0 <= before[4] <= cap, 'Input type/link/size: ' + str(path))
    with path.open('rb') as f:
        data = f.read(cap + 1)
    need(len(data) == before[4] and before == stamp(path), 'Input changed/overflow: ' + str(path))
    need(path not in stamps or stamps[path] == before, 'Input changed between reads: ' + str(path))
    if path not in stamps:
        total_read += len(data)
        need(total_read <= MAX_TOTAL and len(stamps) < 2048, 'Finite review input bound')
    stamps[path] = before
    observed_refs[str(path)] = dict(path=str(path), sha256=digest(data), bytes=len(data))
    return data


def row(path):
    path = Path(path)
    data = raw(path)
    return dict(path=str(path), sha256=digest(data), bytes=len(data))


def document(path):
    return json.loads(raw(path))


def checked(ref):
    need(type(ref) is dict and set(ref) == {'path', 'sha256', 'bytes'}, 'Typed descriptor required')
    need(type(ref['bytes']) is int and type(ref['sha256']) is str and re.fullmatch('[0-9a-f]{64}', ref['sha256']) is not None, 'Descriptor types')
    data = raw(ref['path'])
    need(len(data) == ref['bytes'] and digest(data) == ref['sha256'], 'Descriptor content: ' + ref['path'])
    return data


def refdoc(ref):
    return json.loads(checked(ref))


def decoded(value, cap=8 * 1024**2):
    need(type(value) is str and len(value) <= ((cap + 2) // 3) * 4, 'Base64 bound/type')
    data = base64.b64decode(value, validate=True)
    need(len(data) <= cap and base64.b64encode(data).decode() == value, 'Canonical bounded base64')
    return data


def typed_equal(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(typed_equal(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(typed_equal(x, y) for x, y in zip(a, b))
    return a == b


class Checks:
    def __init__(self):
        self.count, self.failures = 0, []

    def add(self, value, label):
        self.count += 1
        if value is not True:
            self.failures.append(label)

    def result(self):
        return dict(passed=not self.failures, checks=self.count, failures=self.failures)


def validator_agreement(actual, expected, name):
    need(actual['passed'] is expected['passed'] and type(actual['checks']) is int and
         actual['checks'] == expected['checks'], name + ' published validation disagrees')
    need(type(actual['failures']) is list and bool(actual['failures']) is bool(expected['failures']), name + ' published failure classification')


def portable(capture):
    c = Checks()
    c.add(capture.get('schemaVersion') == 1 and capture.get('marker') == 'NEXT_PORTABLE_CACHE_HTTP_CAPTURE_V1', 'capture schema')
    origin = capture['origin']; u = urlsplit(origin)
    c.add(u.scheme == 'http' and u.hostname == '127.0.0.1' and u.port is not None and 1 <= u.port <= 65535 and origin == 'http://127.0.0.1:' + str(u.port), 'loopback origin')
    c.add(capture.get('path') == '/api/portable-cache' and capture.get('requestSeconds') == 20 and capture.get('deliveredBodyCap') == 65536, 'fixed protocol')
    records, nonces = capture['records'], {}
    c.add(len(records) == 5, 'exact five outcomes')
    need(len(records) == 5, 'Portable collection lacks five records')
    roles = [('portable-first', 'GET'), ('portable-repeat', 'GET'), ('portable-revalidate', 'POST'), ('portable-after', 'GET'), ('portable-after-repeat', 'GET')]
    for i, ((name, method), r) in enumerate(zip(roles, records)):
        c.add(r['id'] == name and r['method'] == method and r['url'] == origin + '/api/portable-cache', name + ' identity')
        c.add(type(r['status']) is int and r['status'] == 200, name + ' status')
        transport = r['complete'] is True and r['overflow'] is False and r['transportError'] is None and r['cleanupErrors'] == []
        c.add(transport, name + ' transport/cleanup'); need(transport, name + ' uncertain transport/cleanup')
        c.add(type(r['receivedBytes']) is int and 0 <= r['receivedBytes'] <= 65536 and r['retainedBytes'] == r['receivedBytes'], name + ' complete byte counts')
        headers = r['headers']
        valid = type(headers) is list and all(type(p) is list and len(p) == 2 and all(type(v) is str for v in p) for p in headers)
        c.add(valid, name + ' fetch-exposed headers')
        media = next((v for k, v in headers if k.lower() == 'content-type'), '') if valid else ''
        c.add(valid and media.split(';', 1)[0].strip().lower() == 'application/json', name + ' JSON media type')
        body = checked(r['body']); need(body == decoded(r['bodyBase64'], 65536), name + ' body publication/base64')
        need(r['receivedBytes'] == r['retainedBytes'] == len(body), name + ' retained byte counts')
        c.add(len(body) == r['retainedBytes'] and len(body) <= 65536 and r['body']['bytes'] == len(body) and r['body']['sha256'] == digest(body), name + ' raw body integrity')
        try:
            value = json.loads(body.decode('utf8'))
            c.add(type(value) is dict, name + ' JSON object')
            if method == 'POST':
                c.add(type(value) is dict and value == {'marker': 'NEXT_PORTABLE_CACHE_REVALIDATED', 'tag': 'portable-fetch-v1'}, name + ' acknowledgement')
            else:
                valid_nonce = type(value) is dict and set(value) == {'marker', 'nonce'} and value['marker'] == 'NEXT_PORTABLE_CACHE_VALUE' and type(value['nonce']) is str and re.fullmatch('[0-9a-f]{64}', value['nonce']) is not None
                c.add(valid_nonce, name + ' exact marker/nonce'); nonces[i] = value['nonce'] if valid_nonce else None
        except (ValueError, UnicodeError, TypeError):
            c.add(False, name + ' complete UTF8/JSON body')
    c.add(type(nonces.get(0)) is str and nonces[0] == nonces.get(1), 'first equals repeat')
    c.add(type(nonces.get(3)) is str and nonces[3] != nonces.get(0), 'after differs from first')
    c.add(type(nonces.get(3)) is str and nonces[3] == nonces.get(4), 'after equals after-repeat')
    return c.result()


def supplemental(capture):
    c = Checks(); items = capture['observations']
    unicode_value, recovery_value = 'concurrent-€-😀-café', 'recovered-界-✅'
    specs = [
        ('context-alpha', 'concurrent', 'GET', '/api/context', {'cookie': 'fixture_token=parallel-alpha', 'x-fixture-probe': 'probe-alpha'}, 200, {'marker': 'NEXT_CONTEXT', 'cookie': 'parallel-alpha', 'header': 'probe-alpha'}),
        ('context-beta', 'concurrent', 'GET', '/api/context', {'cookie': 'fixture_token=parallel-beta', 'x-fixture-probe': 'probe-beta'}, 200, {'marker': 'NEXT_CONTEXT', 'cookie': 'parallel-beta', 'header': 'probe-beta'}),
        ('chunked-unicode-json', 'concurrent', 'POST', '/api/json', {'content-type': 'application/json'}, 200, {'marker': 'NEXT_JSON_POST', 'value': unicode_value}),
        ('malformed-json', 'concurrent', 'POST', '/api/json', {'content-type': 'application/json'}, 400, {'marker': 'NEXT_JSON_BAD_INPUT'}),
        ('empty-context-recovery', 'recovery', 'GET', '/api/context', {}, 200, {'marker': 'NEXT_CONTEXT', 'cookie': None, 'header': None}),
        ('json-recovery', 'recovery', 'POST', '/api/json', {'content-type': 'application/json'}, 200, {'marker': 'NEXT_JSON_POST', 'value': recovery_value})]
    c.add(capture['schemaVersion'] == 1 and capture['suite'] == 'NEXT_CONCURRENT_CONTEXT_BODY_RECOVERY_V1', 'suite/schema')
    c.add(capture['clientOverlapOnly'] is True and capture['sameStoreOrNativeResourceIdentityClaimed'] is False and capture['guestReadOrPacketChunkBoundariesClaimed'] is False, 'scope')
    c.add(capture['perRequestTimeoutMs'] == 20000, 'request deadline')
    c.add(len(items) == 6 and len({r['id'] for r in items}) == 6, 'six unique outcomes')
    c.add(sorted(r['id'] for r in items) == sorted(s[0] for s in specs), 'exact case inventory')
    need(len(items) == 6 and {r['id'] for r in items} == {s[0] for s in specs}, 'Incomplete supplemental collection')
    for name, phase, method, path, headers, status, expected in specs:
        r = next(r for r in items if r['id'] == name)
        c.add(r['phase'] == phase and r['request']['method'] == method and r['request']['path'] == path, name + ':request role')
        c.add(r['request']['headers'] == headers, name + ':request context headers')
        complete = all(r[k] is None for k in ('error', 'readerReleaseError', 'publicationError')) and r['bodyEofObserved'] is True and r['signalAborted'] is False
        c.add(complete, name + ':complete/error-free capture'); need(complete, name + ' uncertain response capture')
        c.add(type(r['status']) is int and r['status'] == status, name + ':status')
        c.add(r['body']['path'] == str(Path(capture['output']) / (name + '.body')), name + ':body path')
        body = checked(r['body']); need(body == decoded(r['bodyBase64'], 1048576), name + ' published body')
        c.add(r['body']['bytes'] == len(body) and r['body']['sha256'] == digest(body), name + ':whole raw body')
        pieces = [decoded(p['base64'], 1048576) for p in r['responseChunks']]
        c.add(b''.join(pieces) == body and all(len(b) == p['bytes'] and digest(b) == p['sha256'] for b, p in zip(pieces, r['responseChunks'])), name + ':all received response chunks')
        c.add(len(body) <= 1048576, name + ':accepted body size')
        try:
            value = json.loads(body.decode('utf8')); c.add(typed_equal(value, expected), name + ':exact JSON')
        except (ValueError, UnicodeError):
            c.add(False, 'schema/validation error in ' + name)
            return c.result()  # The genuine validator's outer catch ends validation.
        if path == '/api/context':
            c.add(r['responseHeaders'].get('x-fixture-response') == 'context-ok', name + ':response context')
            c.add(all(s in r['responseHeaders'].get('set-cookie', '') for s in ('fixture_reply=set', 'HttpOnly', 'SameSite=lax')), name + ':response cookie')
        c.add(type(r['startedNs']) is str and type(r['terminalNs']) is str and r['startedNs'].isdigit() and r['terminalNs'].isdigit() and int(r['terminalNs']) >= int(r['startedNs']), name + ':client ordering')
    first = [r for r in items if r['phase'] == 'concurrent']; later = [r for r in items if r['phase'] == 'recovery']
    c.add(len(first) == 4 and len(later) == 2, 'phase inventory')
    c.add(all(int(a['startedNs']) <= int(b['terminalNs']) for a in first for b in first), 'four client requests overlap before completion')
    c.add(all(int(r['startedNs']) >= int(capture['phaseOneTerminalNs']) for r in later), 'recovery starts after complete first batch')
    request = capture['chunkedRequest']; body = decoded(request['body']['base64']); parts = [decoded(p['base64']) for p in request['chunks']]
    expected = json.dumps({'value': unicode_value}, ensure_ascii=False, separators=(',', ':')).encode()
    c.add(len(parts) == 2 and b''.join(parts) == body == expected, 'exact chunked Unicode request')
    c.add(request['splitInsideUtf8Sequence'] is True and request['clientEnqueueBoundariesOnly'] is True and len(parts[0]) == body.index('€'.encode()) + 1, 'client split inside Euro UTF8 sequence')
    c.add(all(digest(p) == r['sha256'] and len(p) == r['bytes'] for p, r in zip(parts, request['chunks'])), 'request chunk hashes')
    head = [e for e in capture['uploadEvents'] if e['event'] == 'head-enqueued']; tail = [e for e in capture['uploadEvents'] if e['event'] == 'tail-enqueued']
    c.add(len(head) == len(tail) == 1 and int(head[0]['ns']) <= int(tail[0]['ns']), 'two actual client enqueue observations')
    c.add(all(e['event'] not in ('tail-error', 'release-error', 'upload-cancelled') for e in capture['uploadEvents']), 'upload ended without cancellation')
    c.add(len(tail) == 1 and all(int(r['terminalNs']) <= int(tail[0]['ns']) for r in first if r['id'] != 'chunked-unicode-json'), 'tail held until three peers terminal')
    return c.result()


def http_contract(client, root, contract):
    items, bodies, outcomes = client['http'], {}, []
    need(len(contract['requests']) == 23 and len(items) == 24, 'Original HTTP inventory incomplete')
    need([r['id'] for r in items] == [r['id'] for r in contract['requests']] + ['server-action-submit'], 'HTTP IDs/order')
    for spec, item in zip(contract['requests'] + [dict(id='server-action-submit', status=303, location='/action-result?value=fixture-action')], items):
        data = raw(root / 'responses' / (item['id'] + '.txt'), 4 * 1024**2)
        need(len(data) == item['bodyBytes'] and digest(data) == item['bodySha256'], 'HTTP body integrity: ' + item['id'])
        text = data.decode('utf8'); headers = item['headers']; failures = []
        if type(item['status']) is not int or item['status'] != spec['status']: failures.append('status')
        if not all(s in text for s in spec.get('includes', [])): failures.append('includes')
        if 'location' in spec and headers.get('location') != spec['location']: failures.append('location')
        if 'json' in spec:
            try:
                value = json.loads(text)
                if not all(k in value and typed_equal(value[k], v) for k, v in spec['json'].items()): failures.append('JSON subset')
            except (ValueError, TypeError): failures.append('JSON parse')
        if not all(headers.get(k) == v for k, v in spec.get('responseHeaders', {}).items()): failures.append('response headers')
        if not all(v in headers.get(k, '') for k, values in spec.get('responseHeaderIncludes', {}).items() for v in values): failures.append('response header includes')
        if 'equalJsonTo' in spec and text != bodies.get(spec['equalJsonTo']): failures.append('repeat body equality')
        passed = not failures; need(item['passed'] is passed, 'Published HTTP predicate disagrees: ' + item['id'])
        bodies[item['id']] = text; outcomes.append(dict(id=item['id'], passed=passed, failures=failures))
    before, after = json.loads(bodies['cache-first']), json.loads(bodies['cache-after-revalidate'])
    need(typed_equal(client['cacheInvalidation']['before'], before) and typed_equal(client['cacheInvalidation']['after'], after), 'Cache bodies/publication disagree')
    need(type(before['generation']) is int and type(after['generation']) is int, 'Generation numeric type')
    generation = after['generation'] > before['generation']
    need(client['cacheInvalidation']['passed'] is generation, 'Published generation predicate disagrees')
    return outcomes, dict(before=before['generation'], after=after['generation'], passed=generation, exactlyOneToTwo=before['generation'] == 1 and after['generation'] == 2)


def streaming(client, root):
    chunks = document(root / 'stream-chunks.json'); decoder = codecs.getincrementaldecoder('utf8')(errors='replace')
    need(type(chunks) is list and len(chunks) <= 65536, 'Stream chunk inventory bound')
    text, shell, ready, size = '', -1, -1, 0
    for i, r in enumerate(chunks):
        b = decoded(r['base64']); need(len(b) == r['bytes'], 'Stream chunk length'); size += len(b)
        need(size <= 8 * 1024**2, 'Stream body bound'); text += decoder.decode(b)
        if shell < 0 and 'NEXT_STREAM_SHELL' in text: shell = i
        if ready < 0 and 'NEXT_STREAM_READY' in text: ready = i
    text += decoder.decode(b'', final=True)
    value = dict(chunks=len(chunks), shellChunk=shell, readyChunk=ready, complete='NEXT_STREAM_SHELL' in text and 'NEXT_STREAM_READY' in text, incrementalDeliveryObserved=ready > shell and shell >= 0)
    need(typed_equal(client['streaming'], value), 'Published stream predicate disagrees')
    return value


def publication(ref, proof):
    data = checked(ref)
    need(all(proof[k] is True for k in ('complete', 'fsynced', 'closed')) and proof['errors'] == [], 'Publication incomplete')
    need(proof['fileBytes'] == len(data) and proof['sha256'] == ref['sha256'], 'Publication bytes/hash')
    return data


def resource(browser, browser_plan):
    value = browser['resourceStreamObservation']
    need(value['finalized'] is True, 'Resource observation not finalized')
    records = value['observations']; need(len(records) == 1, 'Resource observer cardinality')
    r = records[0]; admission = r['admission']
    body = publication(r['artifact'], r['publication'])
    if admission['actualRequestBody'] is not None:
        request = publication(admission['actualRequestBody'], admission['actualRequestBodyPublication'])
    else:
        request = None
    need(len(body) <= 4194304 and len(r['pieces']) <= 65536 and len(r['events']) <= 1024, 'Resource observer bounds')
    need(len(body) == r['body']['bytes'] and digest(body) == r['body']['sha256'], 'Resource artifact/model bytes')
    need(len(r['candidates']) == len(r['terminals']) == 1 and r['command'] is not None and r['reply'] is not None, 'Resource candidate/terminal/command unavailable')
    rid = r['candidates'][0]['requestId']; terminal = r['terminals'][0]
    need(r['command']['method'] == 'Network.streamResourceContent' and r['command']['params'] == {'requestId': rid}, 'Resource command/request join')
    need(terminal['event'] in ('Network.loadingFinished', 'Network.loadingFailed') and terminal['payload']['requestId'] == rid, 'Resource known terminal')
    events = [e for e in browser['cdpEvents'] if e['test'] == 'server-action' and e['payload'].get('requestId') == rid]
    terminals = [e for e in events if e['event'] in ('Network.loadingFinished', 'Network.loadingFailed')]
    need(len(terminals) == 1 and terminals[0]['event'] == terminal['event'] and terminals[0]['payload'] == terminal['payload'], 'Independent CDP terminal join')
    if admission['passed']:
        requests = [e for e in events if e['event'] == 'Network.requestWillBeSent']; extras = [e for e in events if e['event'] == 'Network.requestWillBeSentExtraInfo']
        need(len(requests) == len(extras) == 1 and request is not None, 'Admitted request unique body/ExtraInfo')
        actual = requests[0]['payload']['request']; observed = {k.lower(): v for k, v in extras[0]['payload']['headers'].items()}
        need(actual['method'] == 'POST' and actual['url'] == r['target']['url'] and actual['postData'].encode() == request, 'CDP actual request body')
        need(observed[r['target']['headerName']] == r['target']['nonce'] and observed['next-action'] == admission['currentActionId'], 'Root nonce/action header join')
        need(admission['currentActionId'] == browser_plan['requiredActionId'], 'Selected genuine action ID')
        need(admission['CDPBodyMatchedPlaywright'] is True and admission['publicContextVerified'] is True and admission['multipart']['valid'] is True, 'Request admission flags')
        need(admission['multipart']['sha256'] == digest(request) and admission['multipart']['bytes'] == len(request), 'Actual multipart body descriptor')
        posts = [p for p in browser['actionPosts'] if p['url'] == actual['url']]
        need(len(posts) == 1 and decoded(posts[0]['bodyBase64'], 65536) == request, 'Independent Playwright request body join')
    uncertain = any(e['collectionUncertain'] is True for e in r['errors'])
    command_success = r['handoffSuccessful'] is True and r['reply']['outcome'] == 'fulfilled'
    if command_success and not uncertain:
        prefix = decoded(r['reply']['result']['bufferedData'], 4194304)
        payloads = [e for e in events if e['event'] == 'Network.dataReceived' and 'data' in e['payload']]
        suffix = [decoded(e['payload']['data'], 4194304) for e in payloads]
        need(all(len(b) == e['payload']['dataLength'] for b, e in zip(suffix, payloads)), 'Actual streamed payload lengths')
        need(prefix + b''.join(suffix) == body, 'Actual CDP buffered-prefix + payload assembly')
        need(len(prefix) == sum(e['dataLength'] for e in r['countOnlyBeforeActivation']), 'Buffered prefix/count comparison')
    collection = bool(r['command'] and r['reply'] and len(r['terminals']) == 1 and admission['passed'] and not uncertain)
    complete = command_success and not uncertain and terminal['event'] == 'Network.loadingFinished' and admission['passed'] is True
    need(r['collectionComplete'] is collection and r['commandSuccess'] is command_success and r['completeResourceBody'] is complete and r['completeBody'] is complete, 'Resource model predicates disagree')
    top_collection = browser['browserClosed'] is True and collection and r['publication']['complete'] is True and value['errors'] == []
    need(value['collectionComplete'] is top_collection and value['commandSuccess'] is command_success and value['completeResourceBody'] is complete and value['accepted'] is (top_collection and complete), 'Resource top-level predicates disagree')
    return dict(collectionComplete=top_collection, commandSuccess=command_success, completeResourceBody=complete, terminal=terminal['event'], artifact=r['artifact'], requestBody=admission['actualRequestBody'], errors=r['errors'], admissionPassed=admission['passed'])


def browser_review(browser, client, browser_plan):
    need([t['id'] for t in browser['tests']] == ['client-counter', 'server-action'], 'Original UI test inventory')
    need(browser['browserClosed'] is True and all(t['timedOut'] is False and t['cdpObserver']['stopped'] is False for t in browser['tests']), 'Browser lifecycle/observer uncertainty')
    need(browser['playwrightVersion'] == '1.64.1' and browser['browserVersion'] == '157.0.8103.39', 'Pinned browser versions')
    functional = all(t['passed'] is True for t in browser['tests'])
    error_free = all(browser[k] == [] for k in ('pageerrors', 'consoleerrors', 'failedrequests'))
    strict = functional and error_free and browser['errors'] == [] and browser['browserClosed'] is True
    need(browser['functionalPassed'] is functional and browser['browserErrorFree'] is error_free and browser['passed'] is strict, 'Original strict browser predicates disagree')
    need(browser['assetSelection']['assetPins'] == browser_plan['assetPins'] and browser['assetSelection']['actionsAssetPins'] == browser_plan['actionsAssetPins'], 'Actual asset selection/plan')
    assets = [a for a in browser['assetBodies'] if a['test'] == 'client-counter']; matches = []
    for a in browser['assetBodies']:
        b = checked(a['decodedBody']); pin = a['expected']
        match = len(b) == pin['bytes'] and digest(b) == pin['sha256']
        need(len(b) == a['decodedBytes'] and digest(b) == a['decodedSha256'] and a['sourceMatch'] is match, 'Decoded asset bytes/predicate')
    for pin in browser_plan['assetPins']:
        matches.append(sum(urlsplit(a['url']).path == pin['path'] and a['sourceMatch'] is True for a in assets) == 1)
    assets_passed = len(assets) == len(browser_plan['assetPins']) and all(matches)
    need(browser['assetCapturePassed'] is assets_passed, 'Published asset conjunction disagrees')
    for a in browser['bodyCaptures']:
        if a['decodedBody'] is not None:
            b = checked(a['decodedBody']); need(len(b) == a['decodedBytes'] and digest(b) == a['decodedSha256'], 'Browser decoded body integrity')
    net = browser['netlog']; data = json.loads(checked(net['file']))
    need(net['completeJson'] is True and net['fsynced'] is True and net['errors'] == [] and net['eventCount'] == len(data['events']), 'Closed NetLog retention')
    manifest = refdoc(browser_plan['actualActionManifest'])
    actions = [(key, value) for key, value in manifest.get('node', {}).items() if value.get('filename') == 'app/actions/actions.js' and value.get('exportedName') == 'submitFixture' and 'app/actions/page' in value.get('workers', {})]
    need(len(actions) == 1 and actions[0][0] == browser_plan['requiredActionId'], 'Actual selected action manifest')
    observation = resource(browser, browser_plan)
    return dict(functionalPassed=functional, assetsPassed=assets_passed, strictPassed=strict, uiPassed=sum(t['passed'] is True for t in browser['tests']), browserErrors={k: browser[k] for k in ('pageerrors', 'consoleerrors', 'failedrequests', 'errors')}, resource=observation)


def owner_review(trial, plan, authority_ref):
    root = Path(trial['ownerOutputRoot']); request_ref = row(root / 'request.json')
    request, started, terminal, collection = [document(root / name) for name in ('request.json', 'started.json', 'terminal.json', 'collection.json')]
    arm = trial['arm']; work = trial['outputRoot']
    expected = [plan['node']['path'], trial['actor']['path']]
    if arm == 'stock': expected += [work, plan['standaloneSource'], plan['browserTools'], trial['runId']]
    expected.append(authority_ref['path'])
    need(request['argv'] == expected and started['argv'] == expected and request['seconds'] == started['timeoutSeconds'] == trial['outerSeconds'], 'Generic owner actual argv/deadline')
    need(started['authority'] == terminal['authority'] == request_ref and terminal['pid'] == started['pid'], 'Generic request -> original owner join')
    need(authority_ref in request['inputs'], 'Generic request must protect actual runtime authority')
    need(terminal['rawExitCode'] in (0, 1) and type(terminal['rawExitCode']) is int and collection['rawExitCode'] == terminal['rawExitCode'], 'Original raw exit (semantic 0/1 only)')
    need(terminal['parentOwnedGroupGone'] is True and terminal['allObservedOwnedGroupsGone'] is True and terminal['timeout'] is False and terminal['forcedCleanup'] is False, 'Original owner not clean/quiescent')
    need(all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')), 'Original owner interruption/cleanup errors')
    need(collection['terminal'] == row(root / 'terminal.json') and collection['inputsUnchanged'] is True, 'Generic collection/final-input preservation')
    need(collection['clean'] is (terminal['rawExitCode'] == 0), 'Generic clean flag includes semantic raw0, unlike ownership-only status')
    checked(terminal['stdout']); checked(terminal['stderr'])
    return dict(originalOwner=terminal['pid'], outerSeconds=trial['outerSeconds'], rawExitCode=terminal['rawExitCode'], cleanOwnership=True, finalInputsPreserved=True, request=request_ref, started=row(root / 'started.json'), terminal=row(root / 'terminal.json'), collection=row(root / 'collection.json'))


def stdout_capture(capture, ref):
    need(all(capture[k] is True for k in ('complete', 'pipeEof', 'fileClosed', 'fileBoundVerified', 'finalized')), 'Host stdout incomplete')
    need(all(capture[k] is False for k in ('overflow', 'partialWritePossible', 'unretainedBytesUnknown')) and capture['errors'] == [], 'Host stdout uncertainty')
    data = checked(ref)
    need(len(data) == capture['fileBytes'] == capture['completeWriteBytes'] == capture['lastReservedWriteCeiling'], 'Host stdout byte accounting')


def actor_cleanup(arm, actual, client, work):
    need(actual['fullOriginalContractExecuted'] is client['fullOriginalContractExecuted'] and actual['fullNextAccepted'] is False and actual['controlOnly'] is False, 'Actor actual full-scope flag')
    if arm == 'stock':
        need(actual['control'] == client and actual['controlClientResult'] == row(work / 'client/result.json'), 'Matched Node client publication')
        need(actual['originalDependencyInputsPreserved'] is True and actual['originalApplicationInputsPreserved'] is True, 'Matched Node final inputs')
        need(actual['prepared'] is True and actual['transportErrors'] == [], 'Matched Node preparation/transport')
        exit_record = actual['controlClientExit']
    else:
        need(actual['originalInputsPreserved'] is True and actual['readonlyAppPreserved'] is True, 'Guest final input/app preservation')
        need(actual['client']['result'] == row(work / 'client/result.json'), 'Guest client publication')
        exit_record = actual['client']['exit']; checked(actual['client']['stdout']); checked(actual['client']['stderr'])
        server = actual['server']
        need(server['exit'] == {'code': 0, 'signal': None, 'error': None} and server['shutdownRequested'] is True and server['sigintSent'] is True and server['forcedCleanup'] is False, 'Normal host SIGINT shutdown')
        stdout_capture(server['stdoutCapture'], server['stdout'])
        if arm == 'cloud':
            need(actual['configVerifiedBeforeDev'] is True and actual['readiness']['tcpConnect'] is True and actual['readiness']['workloadRegistered'] is True and actual['readiness']['extraHttpRequests'] == 0, 'Stock cloud config/registration/TCP')
            need([c['label'] for c in actual['commands']] == ['config-show', 'wash-dev', 'full-contract-client'], 'Stock cloud actual command inventory')
            for command in actual['commands'][:2]:
                need(command['exit'] == {'code': 0, 'signal': None, 'error': None} and command['timeout'] is False and command['forcedCleanup'] is False, 'Stock cloud direct CLI/cleanup')
                stdout_capture(command['stdoutCapture'], command['stdout']); raw(command['stderrPath'], 8 * 1024**2)
            configured, effective = actual['configured'], actual['effectiveConfiguration']
            want_volumes = [{'host_path': str(work / 'app'), 'guest_path': '/app'}, {'host_path': str(work / 'cache'), 'guest_path': '/app/.next/cache'}]
            need(configured['dev']['volumes'] == want_volumes and configured['dev']['service'] is False, 'Exactly owned app/cache mounts')
            env = {'STARLING_NEXT_ORIGIN': client['origin'], 'NODE_ENV': 'production', 'NEXT_TELEMETRY_DISABLED': '1'}
            need(configured['workload']['environment'] == {'config': env} and configured['workload']['allowedHosts'] == [client['origin'] + '/'], 'Exact guest environment/self-origin egress')
            need(configured['workload']['allowedIpNameLookups'] == configured['workload']['allowedHostLoopbackPorts'] == [], 'No additional cloud lookup/loopback permissions')
            need(effective['version'] == configured['version'] == '2.11.0' and effective['build'] == configured['build'], 'Stock cloud effective build')
            for k in ('address', 'command', 'component_path', 'service', 'volumes'): need(effective['dev'][k] == configured['dev'][k], 'Stock cloud effective dev.' + k)
            for k in ('components', 'plugins', 'host_plugins'): need(effective['dev'].get(k, []) == [], 'Unexpected cloud dev capability')
            for k in ('allowedHosts', 'allowedIpNameLookups', 'allowedHostLoopbackPorts'): need(effective['workload'][k] == configured['workload'][k], 'Stock cloud workload.' + k)
            need(effective['workload'].get('config', {}) == {} and effective['workload']['environment']['config'] == configured['workload']['environment']['config'] and effective['wit']['skip_fetch'] is True, 'Stock cloud effective environment/config')
        else:
            checked(server['stderr'])
    need(type(exit_record['code']) is int and exit_record['code'] in (0, 1) and exit_record['signal'] is None and exit_record.get('error') is None, 'Client actual terminal incomplete')
    need(exit_record['code'] == (0 if client['passed'] else 1), 'Client status/passed mismatch')


def callback_state(arm, work, expected):
    parent = work / ('application/.next/cache' if arm == 'stock' else 'cache')
    root = parent / 'app-callback-generation-v1'
    need(root.resolve(strict=True) == root, 'Callback namespace canonical')
    before = stamp(root); need(stat.S_ISDIR(before[2]), 'Callback namespace directory')
    names = sorted(p.name for p in root.iterdir())
    need(names == ['generation.json'], 'Callback namespace must contain only committed state; pending/unknown members refuse')
    path = root / 'generation.json'; data = raw(path, 128)
    match = re.fullmatch(rb'\{"schemaVersion":1,"generation":([1-9][0-9]*)\}\n', data)
    need(match is not None and 1 <= int(match[1]) <= 1000000 and int(match[1]) == expected, 'Canonical physical callback generation agrees with HTTP result')
    need(before == stamp(root), 'Callback namespace changed')
    directory_stamps[root] = before
    return dict(namespace=str(root), members=names, pendingAbsent=True, state=row(path), generation=int(match[1]),
                namespacePhysical=dict(dev=before[0], ino=before[1], mode=stat.S_IMODE(before[2]), nlink=before[3]),
                observationScope='Closed owned namespace snapshot only; no crash durability, CAS or private resource identity claim')


def review_arm(trial, binding):
    arm = trial['arm']; work = Path(trial['outputRoot']); client_root = work / 'client'
    need(trial['runId'] == 'clone-cancel-full-' + arm + '-first' and trial['outputPrefix'] == '/private/tmp/starling-node-compat/next-clone-cancel-full-' + arm + '-v1', 'Fixed trial namespace')
    need(str(work) == trial['outputPrefix'] + '-' + trial['runId'], 'Fixed output root')
    need(trial['plan'] == binding['plans'][arm], 'Trial plan/binding join')
    plan = refdoc(trial['plan']); checked(trial['actor'])
    authority_ref = row(Path(trial['authorityPath'])); authority = refdoc(authority_ref)
    need(authority['plans' if arm == 'stock' else 'plan'] == trial['plan'] and authority['sourceIndex'] == binding['runtimeIndex'], 'Authority actual plan/Source index')
    for k in ('constructionReview', 'constructionResult', 'constructionRequest', 'engineAdmission', 'component', 'envelope', 'compositionReview'):
        need(authority[k] == binding[k], 'Authority genuine role: ' + k)
    owner = owner_review(trial, plan, authority_ref)
    actual, client, browser = [document(p) for p in (work / 'result.json', client_root / 'result.json', client_root / 'browser/result.json')]
    need(actual['rootAuthority'] == authority_ref, 'Actor actual runtime authority')
    need(client['suite'] == SUITE and client['controlOnly'] is False and client['fullNextAccepted'] is False and client['browser'] == browser, 'Current full-client/browser wire')
    need(client['errors'] == [] and client['transportErrors'] == [], 'Incomplete original client collection')
    need(client['fullOriginalContractExecuted'] is True, 'Actual original workload not fully collected')
    client_plan = document(Path(plan['clientSource']['path']).parent / 'plan.json')
    need(client_plan['sourceRequirements']['browserSourceIndex'] == binding['browserIndex'], 'Client selected actual browser index')
    for ref in client_plan['sourceRequirements'].values(): checked(ref)
    contract = refdoc(client_plan['sourceRequirements']['fixtureContract'])
    browser_plan = document(Path(plan['browserSource']['path']).parent / 'plan.json')
    http, generation = http_contract(client, client_root, contract)
    portable_result, supplemental_result = portable(client['portableCache']), supplemental(client['supplemental'])
    validator_agreement(client['portableCacheValidation'], portable_result, 'portable')
    validator_agreement(client['supplementalValidation'], supplemental_result, 'supplemental')
    stream = streaming(client, client_root); ui = browser_review(browser, client, browser_plan)
    need(client['browserExit']['signal'] is None and client['browserExit']['code'] == (0 if ui['strictPassed'] else 1), 'Browser raw status/strict outcome')
    original = all(h['passed'] for h in http) and generation['passed'] and stream['complete'] and stream['incrementalDeliveryObserved'] and client['browserExit']['code'] == 0 and ui['strictPassed']
    full = original and portable_result['passed'] and supplemental_result['passed']
    need(client['originalContractPassed'] is original and client['passed'] is full, 'Original/full conjunction publication disagrees')
    actor_cleanup(arm, actual, client, work)
    need(actual['passed'] is full and owner['rawExitCode'] == (0 if actual['passed'] else 1), 'Actor/original-owner outcome mismatch')
    result = dict(collectionVerified=ui['resource']['collectionComplete'], semanticPassed=full, originalContractPassed=original,
                  actualResult=row(work / 'result.json'), clientResult=row(client_root / 'result.json'), browserResult=row(client_root / 'browser/result.json'), owner=owner,
                  http=http, httpPassed=sum(r['passed'] for r in http), httpTotal=len(http), portable=portable_result, supplemental=supplemental_result,
                  generation=generation, streaming=stream, browser=ui, callbackState=callback_state(arm, work, generation['after']), actorErrors=actual['errors'], fullOriginalContractExecuted=True, fullNextAccepted=False)
    if not result['collectionVerified']: result['collectionErrors'] = ['Resource observer collection uncertain/incomplete']
    else: result['collectionErrors'] = []
    return result


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B, without -O; refused before payload reads')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bindings', type=Path); parser.add_argument('sha256')
    parser.add_argument('--output', type=Path, default=HERE / 'actual-runtime-review.json')
    args = parser.parse_args()
    need(re.fullmatch('[0-9a-f]{64}', args.sha256) is not None, 'Binding SHA256 required')
    binding_bytes = raw(args.bindings); need(digest(binding_bytes) == args.sha256, 'Actual binding SHA mismatch')
    binding = json.loads(binding_bytes)
    need(binding['state'] == 'ROOT_CLONE_CANCEL_NEXT_FULL_ACTUAL_BINDINGS_V1', 'Actual binding state')
    need([a['arm'] for a in binding['arms']] == list(ORDER) and [a['outerSeconds'] for a in binding['arms']] == list(CAPS), 'Fixed three-arm order/deadlines')
    results = {}
    for trial in binding['arms']:
        try:
            results[trial['arm']] = review_arm(trial, binding)
        except Exception as error:
            results[trial['arm']] = dict(collectionVerified=False, semanticPassed=None,
                collectionErrors=[dict(type=type(error).__name__, message=str(error))], fullNextAccepted=False)
    need(all(stamp(p) == before for p, before in stamps.items()) and all(stamp(p) == before for p, before in directory_stamps.items()), 'Final review input bookend changed')
    verified = all(r['collectionVerified'] for r in results.values())
    result = dict(schemaVersion=1, state='ROOT_CLONE_CANCEL_NEXT_FULL_DATA_REVIEW_COMPLETED_V1', verifiedDataReviewPassed=verified,
        actualReviewer=row(Path(__file__).resolve()), runtimeBindings=dict(path=str(args.bindings), sha256=args.sha256, bytes=len(binding_bytes)),
        fixedOrder=list(ORDER), arms=results, allFullContractsPassed=verified and all(r['semanticPassed'] is True for r in results.values()),
        delegatedAncestry={k: binding[k] for k in ('runtimeIndex', 'clientIndex', 'browserIndex', 'constructionReview', 'engineAdmission', 'compositionReview', 'hostToolRevalidation', 'appReview', 'assetSelection')},
        reviewedInputs=list(observed_refs.values()),
        preservedOriginalFailures=True, runtimeFixCausalityClaimed=False, privateIdentityProved=False, fullNextAccepted=False,
        scope=['Three fixed original-owner samples; no retries or fresh execution', 'Portable/supplemental predicates independently recomputed; JS exception-message text not compared',
               'Deep construction/build/tool protection is delegated to the actual sealed binding and admission proofs',
               'CDP resource completion is observer evidence, not wire identity, React EOF, same-Store reuse or host-cause proof',
               'No reliability, cost, clean-machine, lifecycle-retirement or production promotion claim'])
    need(args.output.is_absolute() and args.output.parent.resolve(strict=True) == args.output.parent, 'Canonical fresh output parent')
    with args.output.open('x') as f:
        json.dump(result, f, indent=2, ensure_ascii=False); f.write('\n')
    print(json.dumps(dict(review=row(args.output), verifiedDataReviewPassed=verified,
        arms={k: {n: r.get(n) for n in ('collectionVerified', 'semanticPassed', 'httpPassed')} for k, r in results.items()}, fullNextAccepted=False)))
    return 0 if verified else 1


if __name__ == '__main__':
    sys.exit(main())
