"""Read finite terminal DATA only; no extraction, producer imports or actors."""
import argparse
import base64
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tarfile
import zlib

HERE = Path(__file__).resolve().parent
LEDGER_SHA = '615b28824ce5c026113fd714da2e8671a1243db1db7bbab72fc6c11415c860c3'
CASES = [('portable-first', 'GET'), ('portable-repeat', 'GET'), ('portable-revalidate', 'POST'),
         ('portable-after', 'GET'), ('portable-after-repeat', 'GET')]


def need(value, label):
    if value is not True:
        raise ValueError(label)


def equal(a, b):
    if a is None or b is None:
        return a is None and b is None
    if type(a) is bool or type(b) is bool:
        return type(a) is type(b) and a == b
    if type(a) in (int, float) and type(b) in (int, float):
        return math.isfinite(a) and math.isfinite(b) and a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return set(a) == set(b) and all(equal(v, b[k]) for k, v in a.items())
    if isinstance(a, list):
        return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    return a == b


def parse(body):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(body, object_pairs_hook=pairs, parse_constant=constant)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def descriptor(path, body):
    return dict(path=str(path), sha256=sha(body), bytes=len(body))


def physical(path):
    s = path.lstat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def regular(path):
    need(path.is_absolute() and path.resolve() == path, 'canonical current path')
    before = physical(path)
    need(stat.S_ISREG(before[2]) and before[3] == 1, 'ordinary independent file')
    body = path.read_bytes()
    need(before == physical(path), 'file read bookend')
    return body, before


def own_family(draft):
    if draft:
        need(not (HERE / 'index.json').exists(), 'draft only before seal')
        return {}
    raw, before = regular(HERE / 'index.json')
    index = parse(raw)
    expected, directories, records = {'index.json'}, {'.'}, {str(HERE / 'index.json'): before}
    for row in index['files']:
        rel = PurePosixPath(row['path'])
        need(not rel.is_absolute() and '..' not in rel.parts and str(rel) == row['path'], 'own member path')
        need(row['path'] not in expected, 'unique own member')
        expected.add(row['path']); directories.update(str(p) for p in rel.parents)
        body, identity = regular(HERE / row['path'])
        need(descriptor(row['path'], body) == row, 'own member hash/size')
        records[str(HERE / row['path'])] = identity
    files, dirs = set(), {'.'}
    for path in HERE.rglob('*'):
        need(not path.is_symlink(), 'own symlink')
        if path.is_file():
            files.add(path.relative_to(HERE).as_posix())
        else:
            need(path.is_dir(), 'own kind'); dirs.add(path.relative_to(HERE).as_posix())
    need(files == expected and dirs == directories, 'own closed membership')
    need(len({tuple(v[:2]) for v in records.values()}) == len(records), 'own inode aliases')
    return records


def retained(draft):
    own = own_family(draft)
    raw, _ = regular(HERE / 'payload-index.json')
    need(sha(raw) == LEDGER_SHA, 'exact ledger')
    ledger = parse(raw)
    need(ledger['memberCount'] == 228 and ledger['logicalBytes'] == 8953230, 'finite selection')
    raw, _ = regular(HERE / ledger['bundle']['path'])
    need(descriptor(ledger['bundle']['path'], raw) == ledger['bundle'], 'archive hash/size')
    decoder = zlib.decompressobj(31)
    body = decoder.decompress(raw, 16 * 1024 * 1024)
    need(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail and len(body) < 16 * 1024 * 1024, 'one bounded complete gzip')
    rows = ledger['files']; names = [row['archivePath'] for row in rows]
    need(names == ['data/%05d' % i for i in range(228)], 'exact ordered archive names')
    need(len({row['original']['path'] for row in rows}) == 228, 'unique original paths')
    data = {}; end = 0; png = 0
    with tarfile.open(fileobj=io.BytesIO(body), mode='r:') as archive:
        members = archive.getmembers()
        need([item.name for item in members] == names, 'complete TAR membership')
        for item, row in zip(members, rows):
            need(item.isfile() and not item.pax_headers and not item.linkname, 'ordinary TAR member')
            need(item.mode == row['mode'] and item.uid == item.gid == item.mtime == 0, 'TAR mode/owner')
            value = archive.extractfile(item).read()
            need(descriptor(row['original']['path'], value) == row['original'], 'all original hashes/lengths')
            path = Path(row['original']['path'])
            need('server-reference-manifest' not in path.name and path.suffix not in ['.wasm', '.a', '.dylib', '.gz'], 'omitted binary/secret payload policy')
            if path.suffix == '.png':
                need(value.startswith(b'\x89PNG\r\n\x1a\n'), 'PNG signature'); png += 1
            else:
                value.decode('utf8'); need(b'\0' not in value, 'selected text')
            data[str(path)] = value
            end = item.offset_data + ((item.size + 511) // 512) * 512
        need(not any(body[end:]) and len(body) % 512 == 0, 'only TAR zero padding')
    need(png == 2 and sum(len(v) for v in data.values()) == ledger['logicalBytes'], 'PNG/logical scope')
    need(ledger['appTreesBinariesSdk825AndBuildSecretPayloadsIncluded'] is False and ledger['stockV2Included'] is False and ledger['sourceAndPayloadReevaluationInvoked'] is False, 'retention scope')
    return ledger, data, own


def semantics(ledger, data):
    def obj(path):
        return parse(data[str(path)])
    def blob(ref):
        body = data[ref['path']]
        need(descriptor(ref['path'], body) == {k: ref[k] for k in ['path', 'sha256', 'bytes']}, 'retained descriptor join')
        return body
    def refobj(ref):
        return parse(blob(ref))
    def role(name):
        return refobj(ledger['roles'][name])
    def b64(value):
        body = base64.b64decode(value, validate=True)
        need(base64.b64encode(body).decode() == value, 'canonical base64')
        return body
    def nanos(value):
        need(isinstance(value, str) and re.fullmatch('[0-9]+', value) is not None, 'ASCII nanosecond string')
        return int(value)
    nroot, sroot = ledger['nativeRuntimeRoot'], ledger['stockRuntimeRoot']
    native, stock = obj(nroot + '/result.json'), obj(sroot + '/result.json')
    client = refobj(native['client']['result'])
    nr, no, sr = role('native/actual-runtime-review.json'), role('native/actual-outcome-review.json'), role('stock/actual-runtime-review.json')
    need(nr['verificationPassed'] is True and no['verifiedOutcomeAndAppCopyDataConsistent'] is True and sr['verifiedDataConsistent'] is True, 'closed DATA reviews')
    need(refobj(nr['actualResult']) == native and refobj(nr['actualClient']) == client and refobj(sr['actualResult']) == stock, 'reviews bind original bytes')
    need(nr['complementaryOutcomeCopyAndCacheStorageReview'] == ledger['roles']['native/actual-outcome-review.json'], 'complementary lane binding')
    # Exact small Source closures are checked as bytes; no module is imported/evaluated.
    sources = {}
    for index_ref in ledger['sourceFamilies']:
        index = refobj(index_ref); root = Path(index_ref['path']).parent
        expected = {str(root / row['path']) for row in index['files']} | {str(root / 'index.json')}
        need({path for path in data if Path(path).is_relative_to(root)} == expected, 'retained small Source exact family')
        for row in index['files']:
            blob(dict(row, path=str(root / row['path'])))
        sources[root.name] = (index_ref, index)
    native_index = sources['next-portable-cache-native-candidate-v1'][0]
    stock_index = sources['next-portable-cache-stock-candidate-v1'][0]
    helper_index = sources['next-portable-cache-http-collector-v1'][0]
    np = obj(str(Path(native_index['path']).parent / 'plan.json'))
    sp = obj(str(Path(stock_index['path']).parent / 'plans.json'))
    na = role('native/native-first-runtime-authority.json'); sa = role('stock/stock-first-runtime-authority.json')
    need(na['sourceIndex'] == native_index and sa['sourceIndex'] == stock_index, 'actual Source generation')
    need(na['plan'] == descriptor(str(Path(native_index['path']).parent / 'plan.json'), data[str(Path(native_index['path']).parent / 'plan.json')]), 'native plan bytes')
    need(sa['plans'] == descriptor(str(Path(stock_index['path']).parent / 'plans.json'), data[str(Path(stock_index['path']).parent / 'plans.json')]), 'stock plan bytes')
    need(helper_index in np['sourceFamilies'] and helper_index in sp['sourceFamilies'] and native_index in sp['sourceFamilies'], 'one shared helper/browser Source')
    need(native['rootAuthority'] == nr['rootAuthority'] == ledger['roles']['native/native-first-runtime-authority.json'] and sr['rootAuthority'] == ledger['roles']['stock/stock-first-runtime-authority.json'], 'Root authority joins')
    need(np['applicationInputs'] == sp['applicationInputs'] == ledger['roles']['applicationInputs'], 'same fresh inventory')
    inventory = role('applicationInputs')
    need(len(inventory['files']) == inventory['regularFiles'] == 2186 and inventory['bytes'] == 48755844 and len(inventory['directories']) == 427, 'fresh app schema')
    need(role('applicationBuildDataReview')['verifiedPassed'] is True and role('applicationBuildDataReview')['sourceFiles'] == 31 and role('applicationBuildDataReview')['unchangedParentFiles'] == 28, 'accepted host build record')
    need(refobj(np['applicationBuildResult']) == role('applicationBuildResult') and np['applicationBuildResult'] == sp['applicationBuildResult'], 'actual build result descriptor')
    # Original owners: raw1 is a clean failure, never a pass or a forced-cleanup waiver.
    def owner(root, expected_pid, cap, authority, argv, expected_result):
        started, terminal, observation = obj(root + '/started.json'), obj(root + '/terminal.json'), obj(root + '/observation.json')
        need(started['pid'] == terminal['pid'] == expected_pid and started['timeoutSeconds'] == cap and started['argv'] == argv, 'original argv/cap/pid')
        need(started['authority'] == terminal['authority'] == authority, 'original owner authority')
        need(type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 1, 'original raw1 retained')
        need(terminal['timeout'] is terminal['forcedCleanup'] is False and terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True, 'observed clean ownership')
        need(all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']), 'no cleanup/errors/signals')
        need(all(row['alive'] is row['signalAllowed'] is False for row in terminal['finalGroups']), 'final groups gone')
        owned = sorted(path for path in data if path.startswith(root + '/owned-'))
        snapshots = [obj(path) for path in owned]
        need([row['sequence'] for row in snapshots] == list(range(len(snapshots))) and [row['process'] for row in snapshots] == terminal['observedProcesses'], 'all original owned frames')
        for key in ['stdout', 'stderr']:
            blob(terminal[key])
        need(observation['terminal'] == descriptor(root + '/terminal.json', data[root + '/terminal.json']) and refobj(observation['result']) == expected_result, 'original completion descriptors')
        need(observation['rawExitCode'] == 1 and observation['ownedGroupsClean'] is observation['protectedInputsPreserved'] is True, 'original failure/protection')
        return observation, len(snapshots)
    no_outer, nframes = owner(nroot + '-external-root', 87752, 600, native['rootAuthority'], [np['node']['path'], str(Path(native_index['path']).parent / 'deploy.mjs'), native['rootAuthority']['path']], native)
    so_outer, sframes = owner(sroot + '-monitor', 88210, 300, sr['rootAuthority'], [sp['node']['path'], str(Path(stock_index['path']).parent / 'run-stock.mjs'), sroot, inventory['root'], sp['browserTools'], sa['runId']], stock)
    need(no_outer['passed'] is False and so_outer['hostExperimentPassed'] is False and so_outer['guestOrNativeExecuted'] is False, 'neither trial accepted')
    need(nframes == 16 and sframes == 1 and native['originalInputsPreserved'] is native['readonlyAppPreserved'] is True and stock['originalApplicationInputsPreserved'] is True, 'original preservation records')
    # Shared five-case semantics translated into Python, including failed-body readback.
    def nonce(c, client_root):
        capture = c['portableCache']; need(obj(client_root + '/portable-cache/observations.json') == capture, 'whole raw-five publication')
        checks, failures, nonces = 0, [], {}
        def check(value, label):
            nonlocal checks
            checks += 1
            if value is not True:
                failures.append(label)
        check(capture['schemaVersion'] == 1 and capture['marker'] == 'NEXT_PORTABLE_CACHE_HTTP_CAPTURE_V1', 'capture schema')
        check(capture['origin'] == c['origin'] and re.fullmatch(r'http://127\.0\.0\.1:[1-9][0-9]{0,4}', c['origin']) is not None, 'loopback origin')
        check(capture['path'] == '/api/portable-cache' and capture['requestSeconds'] == 20 and capture['deliveredBodyCap'] == 65536, 'fixed protocol')
        rows = capture['records']; check(len(rows) == 5, 'exact five outcomes')
        for row, (ident, method) in zip(rows, CASES):
            need(obj(client_root + '/portable-cache/' + ident + '.json') == row, 'per-case raw record')
            body = blob(row['body']); need(body == b64(row['bodyBase64']), 'physical raw prefix/base64')
            check(row['id'] == ident and row['method'] == method and row['url'] == c['origin'] + '/api/portable-cache', ident + ' identity')
            check(type(row['status']) is int and row['status'] == 200, ident + ' status')
            check(row['complete'] is True and row['overflow'] is False and row['transportError'] is None and row['cleanupErrors'] == [], ident + ' transport/cleanup')
            check(type(row['receivedBytes']) is int and 0 <= row['receivedBytes'] <= 65536 and row['retainedBytes'] == row['receivedBytes'], ident + ' complete byte counts')
            headers = row['headers']; valid_headers = isinstance(headers, list) and all(isinstance(p, list) and len(p) == 2 and all(isinstance(x, str) for x in p) for p in headers)
            check(valid_headers, ident + ' fetch-exposed headers')
            check(valid_headers and dict(headers).get('content-type', '').split(';')[0].strip().lower() == 'application/json', ident + ' JSON media type')
            check(len(body) == row['retainedBytes'] and len(body) <= 65536 and row['body']['sha256'] == sha(body), ident + ' raw body integrity')
            try:
                value = parse(body.decode('utf8'))
                check(isinstance(value, dict), ident + ' JSON object')
                if method == 'POST':
                    check(equal(value, dict(marker='NEXT_PORTABLE_CACHE_REVALIDATED', tag='portable-fetch-v1')), ident + ' acknowledgement')
                else:
                    valid = isinstance(value, dict) and set(value) == {'marker', 'nonce'} and value['marker'] == 'NEXT_PORTABLE_CACHE_VALUE' and isinstance(value['nonce'], str) and re.fullmatch('[0-9a-f]{64}', value['nonce']) is not None
                    check(valid, ident + ' exact marker/nonce'); nonces[ident] = value['nonce'] if valid else None
            except (ValueError, UnicodeError, TypeError, KeyError):
                check(False, ident + ' complete UTF8/JSON body')
        first, repeat, after, last = [nonces.get(k) for k in ['portable-first', 'portable-repeat', 'portable-after', 'portable-after-repeat']]
        check(isinstance(first, str) and first == repeat, 'first equals repeat')
        check(isinstance(after, str) and after != first, 'after differs from first')
        check(isinstance(after, str) and after == last, 'after equals after-repeat')
        actual = c['portableCacheValidation']
        need(actual['passed'] is (not failures) and actual['checks'] == checks and actual['failures'] == failures, 'independent nonce gate equals recorded gate')
        return dict(passed=not failures, checks=checks, cases=5, statuses=[r['status'] for r in rows], deliveredBytes=[len(blob(r['body'])) for r in rows])
    nnonce, snonce = nonce(client, nroot + '/client'), nonce(stock, sroot)
    need(nnonce['passed'] is True and nnonce['checks'] == 52 and snonce['passed'] is False and snonce['checks'] == 47, 'positive native/failed stock nonce boundary')
    need(all(blob(row['body']) == b'Internal Server Error' for row in stock['portableCache']['records']), 'stock five original500 bodies')
    # All six raw responses/chunks and the deterministic context/body/recovery contract.
    expected_supp = {'context-alpha': (200, dict(marker='NEXT_CONTEXT', cookie='parallel-alpha', header='probe-alpha')),
                     'context-beta': (200, dict(marker='NEXT_CONTEXT', cookie='parallel-beta', header='probe-beta')),
                     'chunked-unicode-json': (200, dict(marker='NEXT_JSON_POST', value='concurrent-€-😀-café')),
                     'malformed-json': (400, dict(marker='NEXT_JSON_BAD_INPUT')),
                     'empty-context-recovery': (200, dict(marker='NEXT_CONTEXT', cookie=None, header=None)),
                     'json-recovery': (200, dict(marker='NEXT_JSON_POST', value='recovered-界-✅'))}
    for c, root, positive in [(client, nroot + '/client', True), (stock, sroot, False)]:
        s = c['supplemental']; need(obj(root + '/supplemental/observations.json') == s and s['origin'] == c['origin'], 'whole six publication')
        rows = s['observations']; need(len(rows) == 6 and {r['id'] for r in rows} == set(expected_supp), 'exact six inventory')
        need(s['completionOrder'] == [r['id'] for r in rows] and s['clientOverlapOnly'] is True and s['sameStoreOrNativeResourceIdentityClaimed'] is False, 'six scope/publication order')
        for row in rows:
            body = blob(row['body']); need(body == b64(row['bodyBase64']) and obj(root + '/supplemental/' + row['id'] + '.json') == row, 'six whole physical body/record')
            pieces = [b64(x['base64']) for x in row['responseChunks']]
            need(b''.join(pieces) == body and all(len(v) == x['bytes'] and sha(v) == x['sha256'] for v, x in zip(pieces, row['responseChunks'])), 'every six response chunk')
            need(row['bodyEofObserved'] is True and row['signalAborted'] is False and all(row[k] is None for k in ['error', 'readerReleaseError', 'publicationError']), 'six transport captured')
            need(nanos(row['startedNs']) <= nanos(row['headersNs']) <= nanos(row['terminalNs']), 'six header/terminal ordering')
            if positive:
                status, expected = expected_supp[row['id']]
                need(type(row['status']) is int and row['status'] == status and equal(parse(body), expected), 'independent six exact JSON/status')
                if 'context' in row['id']:
                    need(row['responseHeaders']['x-fixture-response'] == 'context-ok' and all(x in row['responseHeaders']['set-cookie'] for x in ['fixture_reply=set', 'HttpOnly', 'SameSite=lax']), 'context response headers')
            else:
                need(row['status'] == 500 and body == b'Internal Server Error', 'stock six500 retained')
        first = [r for r in rows if r['phase'] == 'concurrent']; later = [r for r in rows if r['phase'] == 'recovery']
        need(len(first) == 4 and len(later) == 2 and max(nanos(r['startedNs']) for r in first) <= min(nanos(r['terminalNs']) for r in first), 'client overlap only')
        need(max(nanos(r['terminalNs']) for r in first) <= nanos(s['phaseOneTerminalNs']) <= min(nanos(r['startedNs']) for r in later), 'recovery follows complete first batch')
        uploaded = b64(s['chunkedRequest']['body']['base64']); pieces = [b64(r['base64']) for r in s['chunkedRequest']['chunks']]
        need(b''.join(pieces) == uploaded == '{"value":"concurrent-€-😀-café"}'.encode() and len(pieces[0]) == uploaded.index('€'.encode()) + 1, 'exact Unicode request split')
        validation = c['supplementalValidation']
        need(validation['passed'] is positive and validation['checks'] == (80 if positive else 14), 'reported finite validator gate retained')
    contract = role('fixture-contract.json')
    def baseline(c, root, native_arm):
        rows = c['http']; expected = contract['requests']; need(len(expected) == 23 and len(rows) == (24 if native_arm else 23), 'observed baseline count')
        passed = 0
        for item, row in zip(expected, rows):
            body = data[root + '/responses/' + row['id'] + '.txt']; text = body.decode('utf8')
            need(row['id'] == item['id'] and row['bodyBytes'] == len(body) and row['bodySha256'] == sha(body), 'baseline raw identity/hash')
            accepted = row['status'] == item['status'] and all(value in text for value in item.get('includes', []))
            if item.get('location'):
                accepted = accepted and row['headers'].get('location') == item['location']
            if 'json' in item:
                try:
                    value = parse(body); accepted = accepted and all(k in value and equal(value[k], v) for k, v in item['json'].items())
                except (ValueError, TypeError):
                    accepted = False
            accepted = accepted and all(row['headers'].get(k) == v for k, v in item.get('responseHeaders', {}).items())
            accepted = accepted and all(v in row['headers'].get(k, '') for k, values in item.get('responseHeaderIncludes', {}).items() for v in values)
            if item.get('equalJsonTo'):
                accepted = accepted and body == data[root + '/responses/' + item['equalJsonTo'] + '.txt']
            need(row['passed'] is accepted, 'independent original HTTP expectation'); passed += accepted
        if native_arm:
            row = rows[-1]; body = data[root + '/responses/server-action-submit.txt']
            need(row['id'] == 'server-action-submit' and row['status'] == 303 and row['headers']['location'] == '/action-result?value=fixture-action' and row['passed'] is True and row['bodySha256'] == sha(body), 'actual action303')
            passed += 1
        return passed
    need(baseline(client, nroot + '/client', True) == 24 and baseline(stock, sroot, False) == 1, 'native24/stock1 observed HTTP outcomes')
    need(all(r['status'] == 500 for r in stock['http'] if r['id'] != 'public-asset'), 'stock22baseline500')
    need(all(key not in stock for key in ['cacheInvalidation', 'streaming', 'browser', 'browserExit']), 'stock later gates unobserved, not passes')
    need(len(stock['errors']) == 1 and '0 !== 1' in stock['errors'][0]['message'], 'original terminal form assertion')
    need(sr['unobserved'] == ['server-action-submit', 'cacheInvalidation-comparison', 'strict-stream', 'browser-test1', 'browser-test2'], 'explicit unobserved list')
    need(b'ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING' in data[sroot + '-monitor/stderr.log'], 'original stock harness diagnostic retained')
    before = parse(data[nroot + '/client/responses/cache-first.txt']); after = parse(data[nroot + '/client/responses/cache-after-revalidate.txt'])
    need(before == after == dict(marker='NEXT_CACHE_VALUE', generation=1) and client['cacheInvalidation'] == dict(before=before, after=after, passed=False), 'legacy1to1 remains failed')
    chunks = obj(nroot + '/client/stream-chunks.json'); text = ''; shell = ready = -1
    for i, row in enumerate(chunks):
        value = b64(row['base64']); need(len(value) == row['bytes'], 'stream raw chunk bytes'); text += value.decode('utf8')
        if shell < 0 and 'NEXT_STREAM_SHELL' in text: shell = i
        if ready < 0 and 'NEXT_STREAM_READY' in text: ready = i
    need(len(chunks) == 5 and shell == 0 and ready == 2 and client['streaming'] == dict(chunks=5, shellChunk=0, readyChunk=2, complete=True, incrementalDeliveryObserved=True), 'strict stream order')
    browser = obj(nroot + '/client/browser/result.json'); need(browser == client['browser'], 'whole browser raw record')
    need(len(browser['tests']) == 2 and all(t['passed'] is True and t['timedOut'] is False and t['error'] is None for t in browser['tests']), 'two functional checks')
    for test in browser['tests']:
        need(blob(test['screenshot']).startswith(b'\x89PNG\r\n\x1a\n'), 'screenshots retained')
    pins = parse(re.search(rb'const assetPins=(\[.*?\]);', blob(np['browserSource'])).group(1))
    pins = {p['path']: p for p in pins}; paths = set()
    for row in browser['assetBodies']:
        body = blob(row['decodedBody']); pin = row['expected']; need(pin == pins[pin['path']] and sha(body) == pin['sha256'] and len(body) == pin['bytes'] and row['sourceMatch'] is True, 'five actual decoded asset pins')
        paths.add(pin['path'])
    need(len(browser['assetBodies']) == 9 and len(pins) == 5 and paths == set(pins), 'nine decoded asset captures')
    need(browser['pageerrors'] == browser['consoleerrors'] == [] and len(browser['failedrequests']) == 1 and len(browser['errors']) == 3, 'strict failures not filtered')
    failure = browser['failedrequests'][0]
    need(failure['requestId'] == 7 and failure['method'] == 'POST' and failure['failure']['errorText'] == 'net::ERR_ABORTED', 'original action7 failure')
    need({r['stage'] for r in browser['errors']} == {'server-action-response-body', 'server-action-response-finished', 'server-action-request-sizes'} and all(r['requestId'] == 7 for r in browser['errors']), 'three original missing-completion errors')
    need(browser['functionalPassed'] is True and browser['passed'] is browser['browserErrorFree'] is False and client['browserExit'] == dict(code=1, signal=None), 'functional versus strict browser gate')
    # Retained cache12 records are actual physical afterimages, not a future race guarantee.
    cache = native['cacheInventory']; need(len(cache) == 12 and all(r['mode'] == 0o644 for r in cache), 'observed0644 cache files')
    epoch = {}; entries = []
    for row in cache:
        wrapper = refobj(row); need(wrapper['schemaVersion'] == 1 and sha(wrapper['payload'].encode()) == wrapper['sha256'], 'cache envelope')
        payload = parse(wrapper['payload'])
        if '/epochs/' in row['path']:
            need(payload['tag'] not in epoch, 'unique epoch'); epoch[payload['tag']] = payload['epoch']
        else:
            entries.append(payload)
    need(len(epoch) == 10 and len(entries) == 2, 'two FETCH/ten epochs')
    for entry in entries:
        need(entry['epochs'] == [epoch[t] for t in entry['tags']] and entry['value']['kind'] == 'FETCH', 'current tagged FETCH records')
    need(no['cacheStorage']['rootMode'] == '0700' and no['cacheStorage']['observedFileModes'] == '0644' and no['cacheStorage']['sourceRequestedFileMode'] == '0600', 'permission limitation preserved')
    world = role('native/portable-cache-native-first-full-world-guard.json')
    need(world['before'] == world['after'] and world['before']['members'] == 28 and world['before']['witFiles'] == 8 and world['unchanged'] is world['nativeInputsPreserved'] is True, 'whole-world documentary guard')
    need(world['before']['sourceIndex'] == na['worldSourceIndex'], 'exact canonical world role')
    need(world['authority'] == native['rootAuthority'] and world['minimumFreeBytes'] == 1073741824 and world['freeBytesAtAdmission'] >= world['minimumFreeBytes'], 'Root1GiB authority record')
    metadata = role('nativeMetadata')
    need(metadata['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1' and len(metadata['actualCompileRows']) == 80 and len(metadata['actualSeparateEmbeddingCompileRows']) == 1, 'full native80+1 documentary rows')
    need([metadata[k] for k in ['nativePolicyInputCount', 'buildSupportInputCount', 'embeddingInputCount']] == [435, 387, 3], '825 documentary composition')
    for key, value in na['metadataExpectedFixedValues'].items():
        need(equal(metadata[key], value), 'genuine full fixed metadata ' + key)
    need(len(na['metadataExpectedFixedValues']) == 31 and len(na['engineBuildEvidence']) == 39 and len(na['nativeProtectedInputs']) == 1778 and len({r['path'] for r in na['nativeProtectedInputs']}) == 1778, 'protected documentary counts')
    need(na['engine'] == metadata['engine'] == nr['engine'] and na['nativeMetadata'] == ledger['roles']['nativeMetadata'] and na['component'] == native['component'] == nr['component'], 'actual full engine/component roles')
    for key in ['fullNativeBuildReview', 'constructionDataReview', 'applicationBuildDataReview']:
        need(ledger['roles'][key] == na[key], 'exact Root review role ' + key)
    need(role('fullNativeBuildReview')['verifiedPassed'] is True and role('constructionDataReview')['verifiedPassed'] is True, 'accepted build/INIT DATA records')
    need(client['originalContractPassed'] is client['passed'] is native['passed'] is stock['originalContractPassed'] is stock['passed'] is False, 'all original and overall gates remain failed')
    return dict(nativeNonce=nnonce, stockNonce=snonce, nativeHttpPassed=24, stockHttpObserved=23,
                stockHttpPassed=1, nativeSupplementalPassed=True, stockSupplementalPassed=False,
                nativeStreamPassed=True, nativeLegacyCachePassed=False, nativeBrowserFunctionalPassed=2,
                nativeStrictBrowserPassed=False, stockActionStreamBrowserUnobserved=True,
                originalRawExitCodes=[1, 1], originalOwnerCaps=[600, 300], originalOwnedFrames=[nframes, sframes],
                wholeWorldMembers=28, witFiles=8, cacheFiles=12,
                appBinarySdk825AndBuildSecretPayloadsIncluded=False,
                underlyingOmittedProtectedPayloadBytesRevalidated=False,
                stockV2Included=False, matchedPairAccepted=False, fullNextAcceptance=False,
                actorOrProducerOrSourceEvaluatorInvoked=False)


def current(ledger):
    records = {}
    for row in ledger['files']:
        path = Path(row['original']['path']); body, identity = regular(path)
        need(descriptor(path, body) == row['original'] and identity == row['physicalBefore'] and stat.S_IMODE(identity[2]) == row['mode'], 'current selected original')
        records[str(path)] = identity
    for tree in ledger['trees']:
        root = Path(tree['root']); files, directories = set(), {'.'}
        for parent, names, children in os.walk(root, followlinks=False):
            parent = Path(parent)
            if parent == root:
                names[:] = [name for name in names if name not in tree['omittedTopLevelDirectories']]
            for name in names + children:
                path = parent / name; need(not path.is_symlink(), 'selected tree symlink')
                if path.is_dir(): directories.add(path.relative_to(root).as_posix())
                else: need(path.is_file(), 'selected tree kind'); files.add(path.relative_to(root).as_posix())
        need(files == set(tree['files']) and directories == {r['path'] for r in tree['directories']}, 'current included tree exact membership')
        for row in tree['directories']:
            path = root / row['path']; need(physical(path) == row['physicalBefore'], 'current selected directory'); records[str(path)] = row['physicalBefore']
    need(len({tuple(v[:2]) for v in records.values()}) == len(records), 'current inode aliases')
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', action='store_true', help='unsealed DATA only')
    parser.add_argument('--current', action='store_true', help='also read only finite selected originals; app trees remain omitted')
    args = parser.parse_args()
    ledger, data, own = retained(args.draft)
    before = current(ledger) if args.current else {}
    result = semantics(ledger, data)
    for path, identity in {**own, **before}.items():
        need(physical(Path(path)) == identity, 'final physical bookend')
    print(json.dumps(dict(state='FINITE_NATIVE_AND_FAILED_STOCK_V1_CAPTURE_DATA_CONSISTENT', dataConsistent=True,
                         capsuleSealed=not args.draft, members=228, currentOriginalsChecked=228 if args.current else 0,
                         scope=result), sort_keys=True))


if __name__ == '__main__':
    main()
