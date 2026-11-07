"""Read retained DATA only. No subprocess, network, application, or actor imports."""
import argparse
import ast
import base64
import codecs
import hashlib
import json
import math
from pathlib import Path
import re
import stat
from urllib.parse import urlsplit

HERE = Path(__file__).absolute().parent
SUITE = 'NEXT_CONCURRENT_CONTEXT_BODY_RECOVERY_V1'
UNICODE = 'concurrent-€-😀-café'
RECOVERY = 'recovered-界-✅'
CASES = [
    ('context-alpha', 'concurrent', 'GET', '/api/context', {'cookie': 'fixture_token=parallel-alpha', 'x-fixture-probe': 'probe-alpha'}, 200, {'marker': 'NEXT_CONTEXT', 'cookie': 'parallel-alpha', 'header': 'probe-alpha'}),
    ('context-beta', 'concurrent', 'GET', '/api/context', {'cookie': 'fixture_token=parallel-beta', 'x-fixture-probe': 'probe-beta'}, 200, {'marker': 'NEXT_CONTEXT', 'cookie': 'parallel-beta', 'header': 'probe-beta'}),
    ('chunked-unicode-json', 'concurrent', 'POST', '/api/json', {'content-type': 'application/json'}, 200, {'marker': 'NEXT_JSON_POST', 'value': UNICODE}),
    ('malformed-json', 'concurrent', 'POST', '/api/json', {'content-type': 'application/json'}, 400, {'marker': 'NEXT_JSON_BAD_INPUT'}),
    ('empty-context-recovery', 'recovery', 'GET', '/api/context', {}, 200, {'marker': 'NEXT_CONTEXT', 'cookie': None, 'header': None}),
    ('json-recovery', 'recovery', 'POST', '/api/json', {'content-type': 'application/json'}, 200, {'marker': 'NEXT_JSON_POST', 'value': RECOVERY}),
]


def require(value, message):
    if value is not True:
        raise ValueError(message)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def loads(value):
    def unique(pairs):
        result = {}
        for key, item in pairs:
            require(key not in result, 'duplicate JSON key: ' + key)
            result[key] = item
        return result
    return json.loads(value, object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON: ' + x)))


def b64(value):
    require(isinstance(value, str), 'Base64 must be text')
    data = base64.b64decode(value, validate=True)
    require(base64.b64encode(data).decode() == value, 'noncanonical Base64')
    return data


def ns(value):
    require(isinstance(value, str) and re.fullmatch('[0-9]+', value) is not None, 'invalid nanosecond string')
    return int(value)


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf8')


def bytes_description(description):
    data = b64(description['base64'])
    require(type(description['bytes']) is int and description['bytes'] == len(data)
            and description['sha256'] == sha(data), 'inline byte descriptor mismatch')
    return data


def valid_error(value):
    return (isinstance(value, dict) and set(value) == {'thrownType', 'name', 'message', 'code', 'stack'}
            and isinstance(value['thrownType'], str) and isinstance(value['message'], str)
            and all(value[k] is None or isinstance(value[k], str) for k in ['name', 'stack'])
            and (value['code'] is None or isinstance(value['code'], str)
                 or (type(value['code']) in (int, float) and math.isfinite(value['code']))))


def capture_integrity(raw, reader=None):
    """Valid retained failure data can pass integrity while strict semantics fail."""
    require(type(raw['schemaVersion']) is int and raw['schemaVersion'] == 1 and raw['suite'] == SUITE, 'capture suite')
    require(raw['clientOverlapOnly'] is True and raw['sameStoreOrNativeResourceIdentityClaimed'] is False
            and raw['guestReadOrPacketChunkBoundariesClaimed'] is False, 'capture scope')
    require(raw['perRequestTimeoutMs'] == 20000, 'capture timeout')
    origin = urlsplit(raw['origin'])
    require(origin.scheme == 'http' and origin.hostname == '127.0.0.1' and origin.port is not None
            and raw['origin'] == 'http://127.0.0.1:' + str(origin.port), 'capture origin')
    output = Path(raw['output'])
    require(output.is_absolute() and '..' not in output.parts and str(output) == raw['output'], 'capture output path')
    observations = raw['observations']
    ids = [r['id'] for r in observations]
    require(len(ids) == len(set(ids)) == 6 and set(ids) == {s[0] for s in CASES}, 'capture inventory')
    require(raw['completionOrder'] == ids, 'completion order/publication order')
    for record in observations:
        require(ns(record['terminalNs']) >= ns(record['startedNs']), 'terminal precedes start')
        for key in ['error', 'readerReleaseError', 'publicationError']:
            require(record[key] is None or valid_error(record[key]), 'invalid typed error')
        require(type(record['bodyEofObserved']) is bool and type(record['signalAborted']) is bool, 'capture booleans')
        if record['status'] is None:
            require(record['error'] is not None and record['body'] is None and record['bodyBase64'] is None
                    and record['headersNs'] is None and record['responseHeaders'] is None
                    and record['responseChunks'] == [] and record['bodyEofObserved'] is False, 'pre-response failure shape')
        else:
            require(type(record['status']) is int and 100 <= record['status'] <= 599, 'response status')
            require(ns(record['startedNs']) <= ns(record['headersNs']) <= ns(record['terminalNs']), 'response header order')
            require(isinstance(record['responseHeaders'], dict), 'response headers')
            data = b64(record['bodyBase64'])
            require(record['body'] == dict(path=str(output / (record['id'] + '.body')), sha256=sha(data), bytes=len(data)), 'whole/partial body descriptor')
            pieces = [bytes_description(c) for c in record['responseChunks']]
            require(b''.join(pieces) == data, 'received chunks differ from published prefix')
            times = [ns(c['arrivedNs']) for c in record['responseChunks']]
            require(times == sorted(times) and all(ns(record['headersNs']) <= t <= ns(record['terminalNs']) for t in times), 'response chunk order')
            require(record['bodyEofObserved'] is True or record['error'] is not None, 'missing EOF without original read error')
            if reader:
                require(reader.ref(record['body']) == data, 'physical response prefix')
        if reader:
            require(reader.read(output / (record['id'] + '.json')) == record, 'per-case JSON mismatch')
    require(ns(raw['completedNs']) >= max(ns(r['terminalNs']) for r in observations), 'completion time')
    if reader:
        require(reader.read(output / 'observations.json') == raw, 'whole raw publication mismatch')
    return dict(captureIntegrityPassed=True, outcomes=6,
                partialOrFailedOutcomes=sum(r['error'] is not None or not r['bodyEofObserved'] for r in observations))


def supplemental_semantics(raw):
    """Independent finite translation of pinned 3dcc validateSupplemental (80 positive checks)."""
    failures, checks = [], 0
    def check(value, message):
        nonlocal checks
        checks += 1
        if value is not True:
            failures.append(message)
    try:
        check(type(raw['schemaVersion']) is int and raw['schemaVersion'] == 1 and raw['suite'] == SUITE, 'suite/schema')
        check(raw['clientOverlapOnly'] is True and raw['sameStoreOrNativeResourceIdentityClaimed'] is False and raw['guestReadOrPacketChunkBoundariesClaimed'] is False, 'scope')
        check(raw['perRequestTimeoutMs'] == 20000, 'request deadline')
        rows = raw['observations']
        check(len(rows) == 6 and len({r['id'] for r in rows}) == 6, 'six unique outcomes')
        check(sorted(r['id'] for r in rows) == sorted(s[0] for s in CASES), 'exact case inventory')
        for ident, phase, method, path, headers, status, expected in CASES:
            r = next((r for r in rows if r['id'] == ident), None)
            if r is None:
                check(False, ident + ':missing')
                continue
            check(r['phase'] == phase and r['request']['method'] == method and r['request']['path'] == path, ident + ':request role')
            check(r['request']['headers'] == headers, ident + ':request context headers')
            check(r['error'] is None and r['readerReleaseError'] is None and r['publicationError'] is None and r['bodyEofObserved'] is True and r['signalAborted'] is False, ident + ':complete/error-free capture')
            check(type(r['status']) is int and r['status'] == status, ident + ':status')
            check(r['body'] is not None and r['body']['path'] == str(Path(raw['output']) / (ident + '.body')), ident + ':body path')
            data = b64(r['bodyBase64'])
            check(r['body']['bytes'] == len(data) and r['body']['sha256'] == sha(data), ident + ':whole raw body')
            pieces = [bytes_description(c) for c in r['responseChunks']]
            check(b''.join(pieces) == data, ident + ':all received response chunks')
            check(len(data) <= 1048576, ident + ':accepted body size')
            check(loads(data.decode('utf8')) == expected, ident + ':exact JSON')
            if path == '/api/context':
                check(r['responseHeaders'].get('x-fixture-response') == 'context-ok', ident + ':response context')
                check(all(s in r['responseHeaders'].get('set-cookie', '') for s in ['fixture_reply=set', 'HttpOnly', 'SameSite=lax']), ident + ':response cookie')
            check(ns(r['terminalNs']) >= ns(r['startedNs']), ident + ':client ordering')
        first = [r for r in rows if r['phase'] == 'concurrent']
        later = [r for r in rows if r['phase'] == 'recovery']
        check(len(first) == 4 and len(later) == 2, 'phase inventory')
        check(all(ns(a['startedNs']) <= ns(b['terminalNs']) for a in first for b in first), 'four client requests overlap before completion')
        check(all(ns(r['startedNs']) >= ns(raw['phaseOneTerminalNs']) for r in later), 'recovery starts after complete first batch')
        body = b64(raw['chunkedRequest']['body']['base64'])
        parts = [b64(c['base64']) for c in raw['chunkedRequest']['chunks']]
        check(len(parts) == 2 and b''.join(parts) == body == json_bytes({'value': UNICODE}), 'exact chunked Unicode request')
        check(raw['chunkedRequest']['splitInsideUtf8Sequence'] is True and raw['chunkedRequest']['clientEnqueueBoundariesOnly'] is True and len(parts[0]) == body.index('€'.encode()) + 1, 'client split inside Euro UTF8 sequence')
        check(all(bytes_description(c) == p for c, p in zip(raw['chunkedRequest']['chunks'], parts)), 'request chunk hashes')
        head = [e for e in raw['uploadEvents'] if e['event'] == 'head-enqueued']
        tail = [e for e in raw['uploadEvents'] if e['event'] == 'tail-enqueued']
        check(len(head) == len(tail) == 1 and ns(head[0]['ns']) <= ns(tail[0]['ns']), 'two actual client enqueue observations')
        check(all(e['event'] not in ['tail-error', 'release-error', 'upload-cancelled'] for e in raw['uploadEvents']), 'upload ended without cancellation')
        check(all(ns(r['terminalNs']) <= ns(tail[0]['ns']) for r in first if r['id'] != 'chunked-unicode-json'), 'tail held until three peers terminal')
    except (KeyError, TypeError, ValueError, StopIteration, IndexError) as error:
        check(False, 'schema/validation error: ' + str(error))
    return dict(passed=not failures, checks=checks, failures=failures)


def additional_ordering(raw):
    first = [r for r in raw['observations'] if r['phase'] == 'concurrent']
    later = [r for r in raw['observations'] if r['phase'] == 'recovery']
    require(len(first) == 4 and len(later) == 2, 'direct phase inventory')
    require(max(ns(r['terminalNs']) for r in first) <= ns(raw['phaseOneTerminalNs'])
            <= min(ns(r['startedNs']) for r in later), 'direct first-terminal/recovery boundary')
    require(max(ns(r['startedNs']) for r in first) <= min(ns(r['terminalNs']) for r in first), 'direct client overlap')
    # These deterministic request bytes were not all tested by the original validator.
    by_id = {r['id']: r for r in raw['observations']}
    require(bytes_description(raw['chunkedRequest']['body']) == json_bytes({'value': UNICODE}), 'whole request descriptor')
    for ident, data in [('malformed-json', b'{bad-concurrent'), ('json-recovery', json_bytes({'value': RECOVERY}))]:
        require(bytes_description(by_id[ident]['request']['body']) == data, 'request input bytes: ' + ident)
    require(by_id['chunked-unicode-json']['request']['body'] == dict(kind='controlled-two-chunk-ReadableStream', **raw['chunkedRequest']['body']), 'request stream descriptor')
    return True


class Reader:
    """Authenticate every consumed file, then rehash it at the final bookend."""
    def __init__(self):
        self.files = {}
        self.families = {}
        self.trees = {}

    def data(self, value):
        path = Path(value)
        require(path.is_absolute() and str(path) == str(value) and path.resolve() == path, 'canonical physical path required')
        info = path.stat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and not path.is_symlink(), 'nonregular/aliased input')
        digest = hashlib.sha256()
        with path.open('rb') as handle:
            while True:
                piece = handle.read(1048576)
                if not piece:
                    break
                digest.update(piece)
        identity = (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        post = path.stat()
        require((post.st_dev, post.st_ino, post.st_mode, post.st_nlink, post.st_size, post.st_mtime_ns, post.st_ctime_ns) == identity, 'input changed during read')
        entry = (dict(path=str(path), sha256=digest.hexdigest(), bytes=info.st_size), identity)
        require(str(path) not in self.files or self.files[str(path)] == entry, 'input changed across reads')
        self.files[str(path)] = entry
        return entry[0]

    def ref(self, reference):
        require(set(reference) == {'path', 'sha256', 'bytes'} and isinstance(reference['path'], str)
                and type(reference['bytes']) is int and reference['bytes'] >= 0
                and isinstance(reference['sha256'], str) and re.fullmatch('[0-9a-f]{64}', reference['sha256']) is not None
                and self.data(reference['path']) == reference, 'descriptor mismatch: ' + str(reference.get('path')))
        return Path(reference['path']).read_bytes()

    def read(self, path):
        self.data(path)
        require(Path(path).stat().st_size <= 32 * 1048576, 'oversized JSON input')
        return loads(Path(path).read_bytes())

    def json_ref(self, reference):
        return loads(self.ref(reference))

    def family(self, reference):
        self.families[reference['path']] = reference
        index = self.json_ref(reference)
        root = Path(reference['path']).parent
        require(Path(reference['path']).name == 'index.json', 'family root index')
        names = [r['path'] for r in index['files']]
        require(len(names) == len(set(names)) and 'index.json' not in names, 'family member inventory')
        dirs = set()
        for item in index['files']:
            relative = Path(item['path'])
            require(not relative.is_absolute() and '..' not in relative.parts and str(relative) == item['path'], 'confined family member')
            dirs.update(str(p) for p in relative.parents if p != Path('.'))
            self.ref(dict(item, path=str(root / relative)))
        nodes = list(root.rglob('*'))
        require(not any(p.is_symlink() for p in nodes), 'family symlink')
        require({str(p.relative_to(root)) for p in nodes if p.is_file()} == set(names) | {'index.json'}, 'family exact files (including nested indices)')
        require({str(p.relative_to(root)) for p in nodes if p.is_dir()} == dirs, 'family exact directories')
        require(all(p.is_file() or p.is_dir() for p in nodes), 'family special file')
        return index

    def finish(self):
        for reference in list(self.families.values()):
            self.family(reference)
        for root, expected in self.trees.items():
            require(tree_snapshot(Path(root)) == expected, 'source tree identity/membership final bookend')
        for path in list(self.files):
            self.data(path)
        return len(self.files)


def pure_functions(reader, roles):
    reader.family(roles['pureReaderIndex'])
    source = reader.ref(roles['pureReader']).decode()
    names = {'clean', 'contract', 'browser_gates'}
    definitions = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name in names]
    require({n.name for n in definitions} == names, 'pure reader APIs')
    scope = {'json': json}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), roles['pureReader']['path'], 'exec', optimize=0), scope)
    return scope


def clean_status(terminal):
    """Cleanup is independent of raw exit; admission additionally requires int raw0."""
    return (terminal['timeout'] is False and terminal['forcedCleanup'] is False
            and terminal['parentOwnedGroupGone'] is True and terminal['allObservedOwnedGroupsGone'] is True
            and all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
            and all(g['alive'] is False for g in terminal['finalGroups']))


def monitor_records(reader, terminal_ref, authority_ref, argv=None, cap=None):
    terminal = reader.json_ref(terminal_ref)
    require(type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0 and clean_status(terminal), 'monitor raw0/clean required')
    require(terminal['schemaVersion'] == 1 and terminal['authority'] == authority_ref, 'monitor authority')
    root = Path(terminal_ref['path']).parent
    started = reader.read(root / 'started.json')
    require(started['schemaVersion'] == 1 and started['authority'] == authority_ref and started['pid'] == terminal['pid'], 'original started identity')
    if argv is not None:
        require(started['argv'] == argv, 'original started argv')
    if cap is not None:
        require(type(started['timeoutSeconds']) is int and started['timeoutSeconds'] == cap, 'original monitor cap')
    for key in ['stdout', 'stderr']:
        require(terminal[key]['path'] == str(root / (key + '.log')), 'raw monitor stream role')
        reader.ref(terminal[key])
    owned = [reader.read(p) for p in sorted(root.glob('owned-*.json'))]
    require([x['sequence'] for x in owned] == list(range(len(owned))), 'original owned record sequence')
    require({json.dumps(x['process'], sort_keys=True) for x in owned} == {json.dumps(x, sort_keys=True) for x in terminal['observedProcesses']}, 'original owned process inventory')
    require(any(p['pid'] == terminal['pid'] for p in terminal['observedProcesses']), 'original owned parent recorded')
    return terminal, started


def validate_authority(authority, template, arm):
    require(re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', authority['runId']) is not None, 'safe Root runId')
    # Root may select a fresh runId and review prose; permissions, fixed roles, fields and pins cannot drift.
    require(set(authority) == set(template), arm + ':authority field inventory')
    require(strict_data_equal({k: v for k, v in authority.items() if k not in ['runId', 'rootReview']},
            {k: v for k, v in template.items() if k not in ['runId', 'rootReview']}), arm + ':authority/source/policy joins')
    require(isinstance(authority['rootReview'], str) and bool(authority['rootReview']), 'Root review prose')


def tree_snapshot(root):
    nodes = [root, *root.rglob('*')]
    require(root.resolve() == root and not any(p.is_symlink() for p in nodes), 'physical source tree')
    require(all(p.is_file() or p.is_dir() for p in nodes), 'source tree special file')
    return {str(p.relative_to(root)): (p.is_dir(), p.stat().st_dev, p.stat().st_ino,
            stat.S_IMODE(p.stat().st_mode), p.stat().st_nlink) for p in nodes}


def current_app_source(reader, plan, inventory):
    root = Path(inventory['root'])
    require(str(root) == plan.get('applicationSource', plan.get('standaloneSource')), 'same current app root')
    snapshot = tree_snapshot(root)
    require({name for name, row in snapshot.items() if not row[0]} == {r['path'] for r in inventory['files']}, 'original app exact files')
    require({name for name, row in snapshot.items() if row[0]} == {'.'} | {r['path'] for r in inventory['directories']}, 'original app exact directories')
    expected_root = plan['applicationRootIdentity']
    for key, value in expected_root.items():
        if key != 'path':
            require(dict(zip(['directory', 'dev', 'ino', 'mode', 'nlink'], snapshot['.']))[key] == value, 'app source root identity')
    for row in inventory['files']:
        require(reader.data(root / row['path']) == {k: row[k] for k in ['sha256', 'bytes']} | {'path': str(root / row['path'])}, 'original app file bytes')
        require(snapshot[row['path']][1:] == tuple(row[k] for k in ['dev', 'ino', 'mode', 'nlink']), 'original app file modes/identity')
    for row in inventory['directories']:
        require(snapshot[row['path']][1:4] == tuple(row[k] for k in ['dev', 'ino', 'mode']), 'original app directory identity')
    require(str(root) not in reader.trees or reader.trees[str(root)] == snapshot, 'app tree changed across arms')
    reader.trees[str(root)] = snapshot


def runtime_paths(plan, run_id, arm):
    require(arm in ['native', 'stock'] and isinstance(run_id, str)
            and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', run_id) is not None, 'runtime arm/safe runId')
    expected_prefix = '/private/tmp/starling-node-compat/' + ('next-wasmtime-deployment' if arm == 'native' else 'next-browser-hydration-stock-v6')
    require(plan['outputPrefix'] == expected_prefix, 'fixed selected output prefix')
    output = Path(plan['outputPrefix'] + '-' + run_id)
    return output, Path(str(output) + ('-external-root' if arm == 'native' else '-monitor'))


def js_json_equal(left, right):
    # JSON.stringify equality must not collapse Python bool with numeric 0/1.
    if type(left) is bool or type(right) is bool:
        return type(left) is type(right) and left == right
    if left is None or right is None:
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, list):
        return len(left) == len(right) and all(js_json_equal(a, b) for a, b in zip(left, right))
    if isinstance(left, dict):
        return list(left) == list(right) and all(js_json_equal(left[k], right[k]) for k in left)
    return left == right


def strict_data_equal(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return set(left) == set(right) and all(strict_data_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(strict_data_equal(a, b) for a, b in zip(left, right))
    return left == right


def original_contract(reader, client, root, pure, roles):
    require(client['passed'] is client['originalContractPassed'] is True, 'reported original/combined pass')
    require(client['errors'] == client['transportErrors'] == [], 'original client errors')
    expected = reader.json_ref(roles['fixtureContract'])['requests']
    require(len(expected) == 23 and [r['id'] for r in client['http']] == [r['id'] for r in expected] + ['server-action-submit'], 'original exact24 HTTP inventory')
    previous = {}
    for number, record in enumerate(client['http']):
        body = Path(root / 'responses' / (record['id'] + '.txt'))
        descriptor = reader.data(body)
        require(record['passed'] is True and descriptor['sha256'] == record['bodySha256'] and descriptor['bytes'] == record['bodyBytes'], 'original whole HTTP body')
        require(record.get('failures', []) == [], 'original retained HTTP failures')
        data = body.read_bytes()
        if number < 23:
            pure['contract'](record, data, expected[number], previous)
            if 'json' in expected[number]:
                actual = loads(data.decode('utf8'))
                require(all(k in actual and js_json_equal(actual[k], value) for k, value in expected[number]['json'].items()), 'JS-type-exact fixture JSON subset')
        else:
            require(record['status'] == 303 and record['headers']['location'] == '/action-result?value=fixture-action', 'actual action POST contract')
        previous[record['id']] = data
    action_ids = re.findall(rb'name="\$ACTION_ID_([^"]+)"', previous['server-action-form-ssr'])
    require(len(action_ids) == 1, 'one actual generated action ID')
    cache = client['cacheInvalidation']
    require(strict_data_equal(cache['before'], loads(previous['cache-first'])) and strict_data_equal(cache['after'], loads(previous['cache-after-revalidate'])), 'cache raw bodies/result equality')
    require(cache['passed'] is True and type(cache['before']['generation']) is int and type(cache['after']['generation']) is int
            and cache['after']['generation'] > cache['before']['generation'], 'unchanged cache invalidation')
    chunks = reader.read(root / 'stream-chunks.json')
    decoder = codecs.getincrementaldecoder('utf8')()
    text, shell, ready = '', -1, -1
    for i, chunk in enumerate(chunks):
        data = b64(chunk['base64'])
        require(chunk['bytes'] == len(data), 'stream chunk bytes')
        text += decoder.decode(data)
        if shell < 0 and 'NEXT_STREAM_SHELL' in text:
            shell = i
        if ready < 0 and 'NEXT_STREAM_READY' in text:
            ready = i
    text += decoder.decode(b'', final=True)
    require(ready > shell >= 0, 'unchanged strict incremental stream')
    require(client['streaming'] == dict(chunks=len(chunks), shellChunk=shell, readyChunk=ready, complete=True, incrementalDeliveryObserved=True), 'stream raw/result equality')
    require(client['browserExit'] == dict(code=0, signal=None), 'browser worker raw0')
    browser = reader.read(root / 'browser' / 'result.json')
    require(client['browser'] == browser, 'browser publication')
    pure['browser_gates'](browser)
    bodies = {}
    for item in browser['bodyCaptures']:
        require(Path(item['decodedBody']['path']).parent == root / 'browser', 'actual browser body role')
        data = reader.ref(item['decodedBody'])
        require(item['decodedBytes'] == len(data) and item['decodedSha256'] == sha(data), 'browser decoded body bytes')
        require(item['bodyCompletion']['kind'] == item['sizesCompletion']['kind'] == 'fulfilled', 'strict browser capture completion')
        require(all(item[k]['requestFailedTerminal'] is None and item[k]['underlyingPromiseHandled'] is True
                    for k in ['bodyCompletion', 'sizesCompletion']), 'browser failure terminal/observer completion')
        bodies[(item['test'], item['url'])] = item
    pins = reader.json_ref(roles['assetPins'])['assets']
    seen = set()
    for asset in browser['assetBodies']:
        require(asset['sourceMatch'] is True and asset['status'] == 200, 'strict browser asset source')
        body = bodies[(asset['test'], asset['url'])]
        require((asset['decodedBytes'], asset['decodedSha256']) == (body['decodedBytes'], body['decodedSha256']), 'asset/body capture join')
        for pin in pins:
            if asset['test'] == 'client-counter' and urlsplit(asset['url']).path == pin['path']:
                require((asset['decodedSha256'], asset['decodedBytes']) == (pin['sha256'], pin['bytes']), 'exact fresh asset pin')
                seen.add(pin['path'])
    require(seen == {p['path'] for p in pins} and len(seen) == 5, 'all five asset bodies')
    for test in browser['tests']:
        require(reader.ref(test['screenshot']).startswith(b'\x89PNG\r\n\x1a\n'), 'retained screenshot')
    require(len(browser['actionPosts']) == 1, 'one actual browser action request')
    post = browser['actionPosts'][0]
    post_body = b64(post['bodyBase64'])
    require(post['headers']['next-action'] == action_ids[0].decode() and post['bytes'] == len(post_body)
            and b'browser-action' in post_body, 'dynamic browser action identity/value bytes')
    require(not any(e['event'] == 'Network.loadingFailed' for e in browser['cdpEvents']), 'strict CDP failed request')
    require(len(browser['cdpEvents']) == sum(t['cdpObserver']['events'] for t in browser['tests']), 'all diagnostic events retained')
    require(all(x['identityProved'] is False for x in browser['cdpCorrelations']), 'CDP/PW identity limit')
    return dict(http=24, browser=2, cache=True, strictStream=True, allFiveAssetPins=True)


def native_joins(reader, authority, result, world_path, plan, fixed):
    require(result['passed'] is result['contractsPassed'] is result['originalInputsPreserved'] is result['readonlyAppPreserved'] is True, 'native pass/protection')
    require(result['errors'] == [] and result['adoption'] is False, 'native errors/adoption')
    require(result['applicationBuildResult'] == plan['applicationBuildResult'] and result['applicationInputs'] == plan['applicationInputs'], 'native actual app roles')
    require(result['sourceIndex'] == authority['sourceIndex'] and result['rootAuthority'] == reader.data(authority_path := Path(result['rootAuthority']['path'])), 'native source/authority role')
    for role, expected in [('component', fixed['componentSha256']), ('engine', fixed['engineSha256']), ('nativeMetadata', fixed['nativeMetadataSha256']), ('constructionResult', fixed['constructorSha256'])]:
        require(authority[role]['sha256'] == expected, 'fixed native role: ' + role)
        reader.ref(authority[role])
    require(authority['component']['bytes'] == fixed['componentBytes'], 'fixed component size')
    for role in ['inputEntry', 'inputSourceIndex', 'constructionCallerIndex', 'worldSourceIndex']:
        reader.ref(authority[role])
    require(authority['inputSourceIndex']['sha256'] == fixed['entrySourceSha256'] and authority['constructionCallerIndex']['sha256'] == fixed['constructorSourceSha256'], 'entry/caller source')
    require(authority['worldSourceIndex']['sha256'] == fixed['worldSourceSha256'], 'world Source pin')
    for reference in authority['nativeSourceFamilies'] + [authority['inputSourceIndex'], authority['constructionCallerIndex'], authority['worldSourceIndex']]:
        reader.family(reference)
    for reference in authority['nativeProtectedInputs'] + authority['engineBuildEvidence'] + authority['worldInputs']:
        reader.ref(reference)
    construction = reader.json_ref(authority['constructionResult'])
    require(construction['passed'] is True and construction['error'] is None and construction['finalProtection']['unchanged'] is True, 'genuine construction complete')
    require(construction['callerIndex'] == authority['constructionCallerIndex'], 'constructor actual caller')
    constructor_plan = reader.json_ref(construction['plan'])
    require(constructor_plan['inputSourceIndex'] == authority['inputSourceIndex'] and constructor_plan['entries']['real-next'] == authority['inputEntry']
            and constructor_plan['worldSourceIndex'] == authority['worldSourceIndex'], 'constructor exact plan roles')
    for role in ['component', 'componentAudit', 'engine', 'nativeMetadata', 'inputEntry', 'inputSourceIndex', 'engineBuildEvidence']:
        require(construction['artifacts'][role] == authority[role], 'actual API artifact join: ' + role)
    for role in ['component', 'componentAudit', 'inputEntry', 'inputSourceIndex', 'constructionResult']:
        require(result[role] == authority[role], 'native output artifact role: ' + role)
    constructor_auth = reader.json_ref(construction['rootAuthority'])
    require(constructor_auth['state'] == 'ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2' and constructor_auth['entryMode'] == 'real-next' and constructor_auth['componentizeInitAllowed'] is True, 'real constructor authority')
    require(constructor_auth['callerIndex'] == authority['constructionCallerIndex'], 'constructor authority caller')
    for key in ['ordinaryExportsAllowed', 'httpServingAllowed', 'networkAllowed', 'nativeBuildAllowed', 'packageMutationAllowed', 'globalPinMutationAllowed', 'debugAllowed', 'applicationMountAtInitAllowed', 'deployedResnapshotAllowed']:
        require(constructor_auth[key] is False, 'constructor restricted permission')
    for key in ['engine', 'nativeMetadata', 'metadataExpectedFixedValues', 'engineBuildEvidence']:
        require(constructor_auth[key] == authority[key], 'constructor native selection')
    monitor_records(reader, authority['constructionOuterTerminal'], construction['rootAuthority'], cap=2400)
    require([c['label'] for c in construction['commands']] == ['componentize-init', 'component-validate', 'component-wit'], 'three actual constructor phases')
    for command, cap in zip(construction['commands'], [1800, 120, 120]):
        terminal, _ = monitor_records(reader, command['terminal'], construction['rootAuthority'], command['argv'], cap)
        require(type(command['rawExitCode']) is int and command['rawExitCode'] == 0 and command['clean'] is True, 'actual constructor phase raw0')
        require(all(command[k] == terminal[k] for k in ['stdout', 'stderr']), 'constructor phase streams')
    audit = reader.json_ref(authority['componentAudit'])
    require(audit['schemaVersion'] == 1 and audit['state'] == 'NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1' and audit['passed'] is True, 'component audit state')
    require(audit['component'] == authority['component'] and audit['exports'] == ['wasi:http/incoming-handler@0.2.10'], 'actual component/export')
    require(audit['emittedImports'] == result['emittedImports'] and result['selectedInterfaces'] == plan['selectedInterfaces'], 'emitted import capture')
    require(set(audit['emittedImports']) == set(plan['selectedInterfaces']) and len(set(plan['selectedInterfaces'])) == 13
            and audit['noExternalPreview1OrCustomImports'] is True and all(x.endswith('@0.2.10') for x in audit['emittedImports']), 'same actual standard13')
    metadata = reader.json_ref(authority['nativeMetadata'])
    require(metadata['metadataKind'] == fixed['nativeKind'] and metadata['engine'] == authority['engine'], 'genuine new metadata kind')
    require(all(metadata[k] == v for k, v in authority['metadataExpectedFixedValues'].items()), 'full fixed native metadata fields')
    world = reader.read(world_path)
    ctor_world = reader.json_ref(authority['constructionWorldGuard'])
    require(world['unchanged'] is world['nativeInputsPreserved'] is True and world['authority'] == reader.data(authority_path), 'runtime world protection')
    require(world['before'] == world['after'] == ctor_world['before'] == ctor_world['after'] and ctor_world['unchanged'] is True, 'whole world before/final/constructor equality')
    expected = dict(sourceIndex=authority['worldSourceIndex'], members=28, witFiles=8, exactFileAndDirectoryMembership=True, noSymlinkOrHardlinkAliases=True)
    require(world['before'] == expected, 'whole external world contract')
    server = result['server']
    require(server['exit'] == dict(code=0, signal=None, error=None) and server['forcedCleanup'] is False
            and server['shutdownRequested'] is server['sigintSent'] is True, 'actual planned native server SIGINT0')
    for item in [server, result['client']]:
        reader.ref(item['stdout']); reader.ref(item['stderr'])
    require(result['client']['exit'] == dict(code=0, signal=None, error=None), 'actual full client raw0')
    command = server['command']
    output = Path(result['outputRoot'])
    origin = server['readyOrigin']
    require(origin == result['portLease']['origin'] and result['portLease']['fallbackAllowed'] is False, 'single leased loopback listener')
    port = result['portLease']['port']
    require(origin == 'http://127.0.0.1:' + str(port), 'canonical listener origin')
    require(command == [plan['wasmtime']['path'], 'serve', '--addr', '127.0.0.1:' + str(port),
        '-S', 'cli=y,tcp=n,udp=n,allow-ip-name-lookup=n', '--env', 'STARLING_NEXT_ORIGIN=' + origin,
        '--env', 'NODE_ENV=production', '--env', 'NEXT_TELEMETRY_DISABLED=1',
        '--dir', str(output / 'app') + '::/app', '--dir', str(output / 'cache') + '::/app/.next/cache',
        '--max-instance-reuse-count', '128', '--idle-instance-timeout', '60s', authority['component']['path']], 'actual selected stock Wasmtime command')


def pair(native_observation, stock_observation, native_world_guard):
    reader = Reader()
    policy = reader.read(HERE / 'policy.json')
    roles, fixed = policy['roles'], policy['fixed']
    for key in ['nativeSource', 'stockSource', 'browserSource']:
        reader.family(roles[key])
    for reference in roles.values():
        reader.ref(reference)
    pure = pure_functions(reader, roles)
    arms = {}
    for arm, path in [('native', native_observation), ('stock', stock_observation)]:
        observation = reader.read(path)
        plan = reader.json_ref(roles[arm + 'Plan'])
        require(observation['passed' if arm == 'native' else 'hostExperimentPassed'] is True
                and observation['protectedInputsPreserved'] is observation['ownedGroupsClean'] is True, arm + ':original owned acceptance/protection')
        require(observation['state'] == ('ROOT_NEXT_WASMTIME_DEPLOYMENT_OBSERVATION_V2' if arm == 'native' else 'ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_OBSERVATION_V1'), 'original observation state')
        terminal_ref = observation['terminal']
        terminal = reader.json_ref(terminal_ref)
        authority_ref = terminal['authority']
        authority = reader.json_ref(authority_ref)
        validate_authority(authority, reader.json_ref(roles[arm + 'AuthorityTemplate']), arm)
        require(authority['sourceIndex'] == roles[arm + 'Source'] and authority['plan' if arm == 'native' else 'plans'] == roles[arm + 'Plan'], 'actual selected Source and plan')
        run_id = authority['runId']
        output, monitor = runtime_paths(plan, run_id, arm)
        require(str(path) == str(monitor / 'observation.json') and terminal_ref['path'] == str(monitor / 'terminal.json'), 'actual runtime observation namespace')
        require(observation['runId'] == run_id and observation['outputRoot'] == str(output), 'actual Root output selection')
        if arm == 'stock':
            require(observation['monitorOutputRoot'] == str(monitor) and observation['arm'] == 'stock'
                    and observation['guestOrNativeExecuted'] is False, 'stock original observer scope')
        source = Path(roles[arm + 'Source']['path']).parent
        argv = ([plan['node']['path'], str(source / 'deploy.mjs'), authority_ref['path']] if arm == 'native'
                else [plan['node']['path'], str(source / 'run-stock.mjs'), str(output), plan['standaloneSource'], plan['browserTools'], run_id])
        monitor_records(reader, terminal_ref, authority_ref, argv, 600 if arm == 'native' else 300)
        require(type(observation['rawExitCode']) is int and observation['rawExitCode'] == terminal['rawExitCode'] == 0, 'original observation raw0')
        require(observation['result']['path'] == str(output / 'result.json'), 'actual output result role')
        result = reader.json_ref(observation['result'])
        require(result['passed'] is True, arm + ':reported full result')
        for reference in plan['sourceFamilies']:
            reader.family(reference)
        for reference in plan['protectedInputs']:
            reader.ref(reference)
        app = reader.json_ref(plan['applicationInputs'])
        build = reader.json_ref(plan['applicationBuildResult'])
        require(build['passed'] is True and build['errors'] == [] and app == build['applicationInventory'], 'genuine same fresh application inventory/build')
        require(app['regularFiles'] == 2181 and app['bytes'] == 48714867 and len(app['directories']) == 425 and app['symlinks'] == [], 'exact fresh2181 app schema')
        current_app_source(reader, plan, app)
        if arm == 'native':
            require(str(native_world_guard) == str(HERE.parent / 'next-app-request-isolation-root-results-v1' / (run_id + '-full-world-guard.json')), 'actual world receipt namespace')
            require(result['rootAuthority'] == authority_ref, 'native original authority identity')
            native_joins(reader, authority, result, native_world_guard, plan, fixed)
            require(result['client']['result']['path'] == str(output / 'client' / 'result.json'), 'native client publication')
            client = reader.json_ref(result['client']['result'])
            client_root = output / 'client'
            require(client['suite'] == 'ACTUAL_NEXT_WASMTIME_FULL_CONTRACT_CLIENT_V2'
                    and client['origin'] == result['server']['readyOrigin'], 'native actual full client identity')
            require(result['client']['command'] == [plan['node']['path'], str(source / 'run-contracts.mjs'),
                    client['origin'], str(client_root), plan['browserTools'], run_id], 'native original client argv')
        else:
            require(result['guestExecuted'] is False and result['prepared'] is True and result['originalApplicationInputsPreserved'] is True, 'stock genuine host-only protection')
            client, client_root = result, output
        require(client['node'] == 'v22.14.0', 'pinned Node client version')
        require(client['supplemental']['output'] == str(client_root / 'supplemental'), 'actual supplemental directory')
        raw = client['supplemental']
        require(raw['origin'] == client['origin'], 'supplemental/original client origin equality')
        integrity = capture_integrity(raw, reader)
        validation = supplemental_semantics(raw)
        require(validation['passed'] is True and validation['checks'] == 80, 'independent strict supplemental semantics')
        additional_ordering(raw)
        reported = client['supplementalValidation']
        require(reported['passed'] is True and reported['checks'] == validation['checks'] and reported['failures'] == [], 'reported/recomputed supplemental conjunction')
        gates = original_contract(reader, client, client_root, pure, roles)
        arms[arm] = dict(supplementalChecks=validation['checks'], capture=integrity, original=gates,
                         # Compare only deterministic response values, preserving all raw elsewhere.
                         values={r['id']: loads(b64(r['bodyBase64']).decode('utf8')) for r in raw['observations']})
    require(arms['native']['values'] == arms['stock']['values'], 'selected six-case differential')
    count = reader.finish()
    return dict(schemaVersion=1, pairAdmission=True, actualPairVerified=True, arms=arms,
                consumedFilesBookended=count, actorOrNetworkExecuted=False, adoption=False,
                noStoreOrNativeOwnerIdentityClaimed=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    capture = sub.add_parser('capture')
    capture.add_argument('--input', required=True)
    actual = sub.add_parser('pair')
    actual.add_argument('--native-observation', required=True)
    actual.add_argument('--stock-observation', required=True)
    actual.add_argument('--native-world-guard', required=True)
    args = parser.parse_args(argv)
    try:
        if args.mode == 'capture':
            raw = loads(Path(args.input).read_bytes())
            if 'raw' in raw:
                require(raw.get('fakeServerOnly') is True, 'only explicitly labelled retained Source tests may wrap raw')
                raw = raw['raw']
            result = capture_integrity(raw)
            semantic = supplemental_semantics(raw)
            extra = False
            if semantic['passed']:
                extra = additional_ordering(raw)
            result.update(schemaVersion=1, mode='capture', strictSupplementalPassed=semantic['passed'],
                          validation=semantic, strengthenedOrderingPassed=extra, pairAdmission=False,
                          originalOwnerOrApplicationGatesVerified=False, actorOrNetworkExecuted=False)
        else:
            result = pair(args.native_observation, args.stock_observation, args.native_world_guard)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as error:
        print(json.dumps(dict(schemaVersion=1, mode=args.mode, pairAdmission=False, error=type(error).__name__ + ': ' + str(error), actorOrNetworkExecuted=False)))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
