"""Finite DATA-only review of the fixed disconnect/recovery three-arm probe.
No project helper import, target execution or deep upstream build replay.
CLI: Python -I -B review-probe.py BINDINGS_PATH BINDINGS_SHA --output FRESH_JSON.
Primitive stable-read/typed-equality/capture checks derive from reviewed871d
Source; workload/outcome validation below is specific to this new probe.
raw() is the sole payload-read seam for a later repository-copy map.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import sys
from urllib.parse import urlsplit
HERE = Path(__file__).resolve().parent
SUITE = 'NEXT_DISCONNECT_RECOVERY_CLIENT_V1'
ORDER = ('wasmtime','cloud','stock')
MAX_FILE = 24*1024**2
MAX_TOTAL = 512*1024**2
stamps, observed_refs, total_read = {}, {}, 0

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


def typed_equal(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(typed_equal(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(typed_equal(x, y) for x, y in zip(a, b))
    return a == b


def stdout_capture(capture, ref):
    need(all(capture[k] is True for k in ('complete', 'pipeEof', 'fileClosed', 'fileBoundVerified', 'finalized')), 'Host stdout incomplete')
    need(all(capture[k] is False for k in ('overflow', 'partialWritePossible', 'unretainedBytesUnknown')) and capture['errors'] == [], 'Host stdout uncertainty')
    data = checked(ref)
    need(len(data) == capture['fileBytes'] == capture['completeWriteBytes'] == capture['lastReservedWriteCeiling'], 'Host stdout byte accounting')

def published(ref, proof, complete=None):
    data = checked(ref)
    need(proof['fsynced'] is True and proof['closed'] is True and proof['errors'] == [], 'Publication sync/close/errors')
    need(proof['fileBytes'] == len(data) and proof['sha256'] == digest(data), 'Publication SHA/byte count')
    need(type(proof['complete']) is bool and (complete is None or proof['complete'] is complete), 'Publication completeness meaning')
    return data

def body_predicates(case, data, headers, cycle, call):
    failures = []
    def check(ok, label):
        if ok is not True: failures.append(label)
    check(call['request']['finishObserved'], 'request finish observed; no peer-acknowledgment claim')
    check(call['response']['statusCode'] == (400 if case == 'json-malformed' else 200), 'expected response status')
    check('content-encoding' not in headers, 'expected absent response Content-Encoding; no decoder used')
    stream = None
    if case == 'stream-disconnect':
        intent = call['intentionalDisconnect']; errors = call['request']['errors'] + call['response']['errors'] + call['connection']['errors']
        check(intent['triggered'] and intent['localDestroyInvoked'] and intent['firstChunkBytes'] > 0, 'actual first-body close was invoked')
        check(all(e['sequence'] > (intent['intentSequence'] or 0) and e['code'] in ('ECONNRESET','ERR_STREAM_PREMATURE_CLOSE','ERR_STREAM_DESTROYED','ERR_SOCKET_CLOSED') for e in errors), 'no pre-intent or unrelated transport errors')
        need(intent['httpIncompleteAtIntent'] is (intent['completeAtIntent'] is False and intent['endObservedAtIntent'] is False), 'Intent incomplete flag')
    else:
        check(call['httpComplete'], 'normal request requires parsed complete HTTP entity and consumer end')
        if case == 'stream-complete':
            # Markers are ASCII. Searching cumulative bytes has the same first
            # marker-event indices as the producer's incremental UTF8 decoder.
            cumulative = b''; shell = ready = -1
            for i, chunk in enumerate(call['capture']['chunks']):
                cumulative += data[chunk['offset']:chunk['offset'] + chunk['bytes']]
                if shell < 0 and b'NEXT_STREAM_SHELL' in cumulative: shell = i
                if ready < 0 and b'NEXT_STREAM_READY' in cumulative: ready = i
            text = data.decode('utf8', errors='replace')
            shell_at,ready_at=text.find('NEXT_STREAM_SHELL'),text.find('NEXT_STREAM_READY')
            stream = dict(chunks=len(call['capture']['chunks']),shellChunk=shell,readyChunk=ready,shellPosition=-1 if shell_at < 0 else len(text[:shell_at].encode('utf-16-le'))//2,readyPosition=-1 if ready_at < 0 else len(text[:ready_at].encode('utf-16-le'))//2,incrementalDeliveryObserved=ready > shell and shell >= 0)
            need(typed_equal(call['streaming'], stream), 'Published stream evidence')
            check(stream['shellPosition'] >= 0 and stream['readyPosition'] > stream['shellPosition'], 'SHELL before READY markers')
            check(stream['incrementalDeliveryObserved'], 'SHELL observed in an earlier client body event than READY')
        else:
            try: value = json.loads(data.decode('utf8'))
            except (ValueError, UnicodeError): value = None; check(False, 'complete UTF8 JSON expected')
            expected = ({'marker':'NEXT_JSON_BAD_INPUT'} if case == 'json-malformed' else
                {'marker':'NEXT_FS_CRYPTO','text':'nextjs-runtime-fixture\n','sha256':'6bb4bb9103d951dce4f9ff0ebaeee7e91d610226c5661630d59824f0d958b928'} if case == 'fs-crypto' else
                {'marker':'NEXT_CONTEXT','cookie':cycle['cookie'] if case == 'context-set' else None,'header':cycle['probe'] if case == 'context-set' else None})
            check(typed_equal(value, expected), 'exact expected JSON keys and values')
            if case.startswith('context-'):
                check(headers.get('x-fixture-response') == 'context-ok', 'context response header')
                cookies = headers.get('set-cookie')
                check(type(cookies) is list and any(all(s in cookie for s in ('fixture_reply=set','HttpOnly','SameSite=lax')) for cookie in cookies), 'context response cookie')
    return failures, stream

def call_review(call, stored, cycle, case, client_root, limits, origin):
    name = cycle['label'] + '-' + case
    need(call['schemaVersion'] == 1 and call['id'] == name and call['caseId'] == case and type(call['cycleIndex']) is int and call['cycleIndex'] == cycle['index'] and call['phase'] == cycle['phase'], 'Fixed call identity/order')
    need(stored['id'] == name and stored['result']['path'] == str(client_root / 'calls' / (name + '.json')), 'Call publication role')
    need(typed_equal(json.loads(published(stored['result'], stored['publication'], True)), call), 'Per-call JSON versus final result')
    body_ref = call['body']; need(body_ref['path'] == str(client_root / 'calls' / (name + '.body')), 'Call body role')
    data = published(body_ref, call['bodyPublication'])
    need(len(data) <= limits['bodyLimitBytes'], 'Call body cap')
    request, response, connection, capture, intent = (call[k] for k in ('request','response','connection','capture','intentionalDisconnect'))
    method = 'POST' if case == 'json-malformed' else 'GET'
    path = '/stream' if case.startswith('stream-') else '/api/json' if case == 'json-malformed' else '/api/fs-crypto' if case == 'fs-crypto' else '/api/context'
    headers = {'accept':'*/*','accept-encoding':'identity','connection':'close'}
    if case == 'json-malformed': headers.update({'content-type':'application/json','content-length':'4'})
    if case == 'context-set': headers.update({'cookie':'fixture_token=' + cycle['cookie'],'x-fixture-probe':cycle['probe']})
    need(call['method'] == method and call['path'] == path and request['url'] == origin + path and request['headers'] == headers, 'Actual frozen request method/path/headers')
    need(request['bodyBytes'] == (4 if method == 'POST' else 0) and request['bodySha256'] == (digest(b'{bad') if method == 'POST' else None), 'Actual declared request body')
    for obj, fields in [(request,('attempted','created','finishObserved','closeObserved')),(response,('received','complete','readableEnded','endObserved','abortedObserved','closeObserved')),(connection,('socketAssigned','socketEndObserved','socketCloseObserved','cleanupRequested','cleanupCompleted')),(capture,('overflow','unretainedBytesUnknown','allObservedBytesRetained'))]:
        need(all(type(obj[k]) is bool for k in fields), 'Typed call observation booleans')
    need(connection['socketCloseHadError'] is None or type(connection['socketCloseHadError']) is bool, 'Typed socket close outcome')
    for obj in (request,response,connection):
        need(type(obj['errors']) is list and len(obj['errors']) <= 16 and all(type(e) is dict and type(e['sequence']) is int and type(e['ns']) is str and e['ns'].isdigit() and (e['code'] is None or type(e['code']) is str) for e in obj['errors']), 'Typed retained transport errors')
    need(type(call['startedNs']) is str and call['startedNs'] == '0' and type(call['terminalNs']) is str and call['terminalNs'].isdigit(), 'Call timing scope')
    need(call['observationCutoff']['ns'] == call['terminalNs'] and call['observationCutoff']['reason'] in ('all-owned-close-observed','cleanup-timeout-unknown-owned-close'), 'Fixed observation cutoff')
    need(len(call['events']) <= 128 and len(capture['chunks']) <= limits['chunkLimit'], 'Call event/chunk bounds')
    rows = call['events'] + capture['chunks']; need(all(type(r['sequence']) is int and r['sequence'] > 0 and type(r['ns']) is str and r['ns'].isdigit() and int(r['ns']) <= int(call['terminalNs']) for r in rows), 'Observed event sequence/timing types')
    need(len({r['sequence'] for r in rows}) == len(rows), 'Event/chunk sequence uniqueness')
    offset = metadata_bytes = 0
    for chunk in capture['chunks']:
        need(type(chunk['offset']) is int and type(chunk['bytes']) is int and chunk['offset'] == offset and chunk['bytes'] >= 0, 'Contiguous retained chunk offsets')
        part = data[offset:offset + chunk['bytes']]; need(len(part) == chunk['bytes'] and digest(part) == chunk['sha256'], 'Actual retained chunk bytes')
        offset += len(part); metadata_bytes += len(json.dumps(chunk,separators=(',',':'),ensure_ascii=False).encode())
    need(offset == len(data) == capture['retainedBytes'] and type(capture['observedBytes']) is int and capture['observedBytes'] >= len(data) and metadata_bytes <= limits['metadataLimitBytes'], 'Body/chunk/metadata accounting')
    all_observed = not capture['overflow'] and not capture['unretainedBytesUnknown'] and capture['observedBytes'] == len(data)
    need(capture['allObservedBytesRetained'] is all_observed and call['bodyPublication']['complete'] is all_observed, 'Saved-prefix versus all-observed capture flag')
    if call['observationCutoff']['reason'] == 'cleanup-timeout-unknown-owned-close': need(capture['unretainedBytesUnknown'] is True and connection['cleanupCompleted'] is False, 'Abandoned cleanup is uncertain')
    need(intent['configured'] is (case == 'stream-disconnect') and intent['guestCancellationObserved'] is False, 'Intent scope')
    if intent['triggered']:
        need(case == 'stream-disconnect' and len(capture['chunks']) > 0 and intent['firstChunkBytes'] == capture['chunks'][0]['bytes'] and intent['firstChunkBytes'] > 0, 'First actual body Buffer intent')
        e = [e for e in call['events'] if e['kind'] == 'intentional-close-after-first-actual-body-buffer']
        need(len(e) == 1 and e[0]['sequence'] == intent['intentSequence'] and e[0]['bytes'] == intent['firstChunkBytes'] and e[0]['sequence'] > capture['chunks'][0]['sequence'], 'Intent event evidence')
        need(all(type(intent[k]) is bool for k in ('completeAtIntent','readableEndedAtIntent','endObservedAtIntent','localDestroyInvoked')), 'Intent parser/read observations')
    need(type(call['deadline']['exceeded']) is bool and type(call['deadline']['limitMs']) is int and 1 <= call['deadline']['limitMs'] <= limits['httpTimeoutMs'], 'Declared per-call deadline')
    response_headers = response['headers'] or {}; need(type(response_headers) is dict, 'Response headers object')
    raw_headers = response['rawHeaders']; need(type(raw_headers) is list and len(raw_headers) <= 256 and len(raw_headers) % 2 == 0 and all(type(v) is str for v in raw_headers), 'Retained raw response headers')
    for key in ('content-length','content-encoding','x-fixture-response'):
        values = [raw_headers[i+1] for i in range(0,len(raw_headers),2) if raw_headers[i].lower() == key]
        if len(values) == 1: need(response_headers.get(key) == values[0], 'Exposed critical header versus raw header')
        if not values: need(key not in response_headers, 'Unexpected exposed critical header')
    cookies=[raw_headers[i+1] for i in range(0,len(raw_headers),2) if raw_headers[i].lower() == 'set-cookie']
    if cookies: need(response_headers.get('set-cookie') == cookies, 'Exposed response cookies versus actual raw headers')
    cl = response_headers.get('content-length'); valid_cl = cl is None or type(cl) is str and re.fullmatch('0|[1-9][0-9]*',cl) is not None and int(cl) <= 9007199254740991
    cl_matches = None if cl is None else valid_cl and int(cl) == len(data)
    need(response['declaredContentLength'] == cl and response['contentLengthMatches'] is cl_matches, 'Actual Content-Length accounting')
    http_complete = not call['deadline']['exceeded'] and request['finishObserved'] and connection['socketCloseHadError'] is False and response['received'] and response['complete'] and response['readableEnded'] and response['endObserved'] and not response['abortedObserved'] and response['errors'] == request['errors'] == connection['errors'] == [] and valid_cl and (cl is None or cl_matches is True)
    collection = request['created'] and request['closeObserved'] and connection['socketAssigned'] and connection['socketCloseObserved'] and connection['cleanupCompleted'] and (not response['received'] or response['closeObserved']) and all_observed and call['bodyPublication']['complete'] is True and call['collectionErrors'] == []
    need(call['httpComplete'] is http_complete and call['collectionComplete'] is collection, 'Independent HTTP-completion versus collection flags')
    failures, stream = body_predicates(case,data,response_headers,cycle,call)
    need(call['validationErrors'] == failures and call['passed'] is (collection and not failures), 'Actual semantic predicate recomputation')
    return dict(id=name,phase=cycle['phase'],caseId=case,collectionComplete=collection,cleanupComplete=connection['cleanupCompleted'],httpComplete=http_complete,passed=call['passed'],body=body_ref,bodyBytes=len(data),intentional=case == 'stream-disconnect',completeAtIntent=intent['completeAtIntent'],readableEndedAtIntent=intent['readableEndedAtIntent'],abortedObserved=response['abortedObserved'],deadlineExceeded=call['deadline']['exceeded'],transportErrors={k:obj['errors'] for k,obj in [('request',request),('response',response),('socket',connection)]},validationErrors=failures,streaming=stream)

def client_review(client, receipt, root, plan):
    need(client['suite'] == receipt['suite'] == SUITE and client['controlOnly'] is receipt['controlOnly'] is True and client['fullOriginalContractExecuted'] is receipt['fullOriginalContractExecuted'] is False and client['fullNextAccepted'] is receipt['fullNextAccepted'] is False, 'Probe-only capability flags')
    need(type(client['warmupCycles']) is type(client['measuredCycles']) is type(client['plannedCalls']) is int and client['warmupCycles'] == 3 and client['measuredCycles'] == 16 and client['plannedCalls'] == 114 and typed_equal(client['limits'],plan['limits']), 'Fixed typed cycle/cap declarations')
    need(typed_equal(client['limits'],dict(httpTimeoutMs=20000,cleanupTimeoutMs=2000,bodyLimitBytes=4194304,chunkLimit=65536,metadataLimitBytes=262144,resultBytes=16777216,clientTimeoutMs=180000)), 'Source-declared protocol limits')
    need(client['sourceRequirements'] == plan['sourceRequirements'], 'Client actual Source role')
    for value in client['sourceRequirements'].values(): checked(value)
    need(client['scope']['sameStoreOrInstanceReuseProved'] is client['scope']['resourceRetirementProved'] is client['scope']['guestCancellationObserved'] is False, 'No private identity/retirement/cancel claim')
    need(receipt['state'] == 'NEXT_DISCONNECT_RECOVERY_CLIENT_PUBLICATION_V1' and receipt['calls'] == client['callRecords'], 'Final receipt/call references')
    cases = ('stream-complete','stream-disconnect','json-malformed','context-set','context-empty','fs-crypto')
    cycles = plan['cycles']; need(len(cycles) == 19 and len(client['calls']) <= 114 and len(client['callRecords']) == len(client['calls']), 'Bounded actual inventory')
    for i,c in enumerate(cycles): need(typed_equal(c,dict(index=i,phase='warmup' if i < 3 else 'measured',label=('warmup-' if i < 3 else 'measured-') + str(i).zfill(3),cookie='alpha-' + str(i).zfill(3),probe='probe-value-' + str(i).zfill(3))), 'Frozen independent cycle inputs')
    origin = client['origin']; u = urlsplit(origin); need(u.scheme == 'http' and u.hostname == '127.0.0.1' and u.port is not None and origin == 'http://127.0.0.1:' + str(u.port), 'Canonical actual origin')
    outcomes = [call_review(call,record,cycles[i//6],cases[i%6],root,plan['limits'],origin) for i,(call,record) in enumerate(zip(client['calls'],client['callRecords']))]
    need(client['unattemptedCalls'] == 114 - len(outcomes), 'Explicit unattempted suffix')
    need(len(client['cycles']) <= 19, 'Actual cycle prefix bound')
    for i,actual in enumerate(client['cycles']):
        observed = [r for r in outcomes if r['id'].startswith(cycles[i]['label'] + '-')]
        expected = dict(cycles[i],callIds=[r['id'] for r in observed],collectionComplete=len(observed) == 6 and all(r['collectionComplete'] for r in observed),passed=len(observed) == 6 and all(r['collectionComplete'] and r['passed'] for r in observed))
        need(typed_equal(actual,expected), 'Actual cycle summary recomputation')
    executed = any(c['request']['created'] for c in client['calls']); cleanup = bool(outcomes) and all(c['cleanupComplete'] for c in outcomes)
    complete = len(outcomes) == 114 and len(client['cycles']) == 19 and all(c['collectionComplete'] for c in client['cycles']) and client['collectionErrors'] == []
    passed = complete and all(c['passed'] for c in outcomes)
    for key,value in [('probeExecuted',executed),('cleanupComplete',cleanup),('collectionComplete',complete),('passed',passed)]: need(client[key] is value and receipt[key] is value, 'Client/receipt flag: ' + key)
    need(client['errors'] == client['collectionErrors'] and client['validationErrors'] == [dict(id=c['id'],errors=c['validationErrors']) for c in outcomes if not c['passed']], 'Top failure inventory')
    intents = [c for c in outcomes if c['intentional']]
    return dict(probeExecuted=executed,collectionComplete=complete,cleanupComplete=cleanup,passed=passed,calls=outcomes,callCount=len(outcomes),normalCalls=sum(not c['intentional'] for c in outcomes),intentionalCalls=len(intents),unattemptedCalls=client['unattemptedCalls'],firstBodyAlreadyComplete=sum(c['completeAtIntent'] is True for c in intents),firstBodyNotYetComplete=sum(c['completeAtIntent'] is False for c in intents),collectionErrors=client['collectionErrors'])

def owned_trial(trial, plan, authority_ref):
    root = Path(trial['ownerOutputRoot']); request_ref = row(root/'request.json')
    request, started, terminal, collection = [document(root/name) for name in ('request.json','started.json','terminal.json','collection.json')]
    argv = request['argv']; need(len(argv) == (7 if trial['arm'] == 'stock' else 3) and argv[0] == plan['node']['path'], 'Actor CLI shape')
    actor_arg = Path(argv[1]); need('..' not in actor_arg.parts, 'Actor path traversal')
    actor_role = str(actor_arg if actor_arg.is_absolute() else Path(request['cwd'])/actor_arg)
    need(actor_role == trial['actor']['path'] and argv[-1] == authority_ref['path'], 'Actual generic argv actor/authority roles')
    if trial['arm'] == 'stock': need(argv[2:6] == [trial['outputRoot'],plan['standaloneSource'],plan['browserTools'],trial['runId']], 'Matched Node actual argv')
    need(started['argv'] == argv and started['authority'] == terminal['authority'] == request_ref and started['pid'] == terminal['pid'], 'Original generic request/owner join')
    need(request['seconds'] == started['timeoutSeconds'] == trial['outerSeconds'] and authority_ref in request['inputs'] and trial['actor'] in request['inputs'], 'Original authority input/deadline')
    need(type(terminal['rawExitCode']) is int and terminal['rawExitCode'] in (0,1) and collection['rawExitCode'] == terminal['rawExitCode'], 'Semantic raw0/1 owner outcome')
    need(terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and terminal['timeout'] is terminal['forcedCleanup'] is False and all(terminal[k] == [] for k in ('errors','signals','interruptedSignals','remainingObservedPids')), 'Original owned cleanup/quiescence')
    need(collection['inputsUnchanged'] is True and collection['terminal'] == row(root/'terminal.json') and collection['clean'] is (terminal['rawExitCode'] == 0), 'Final inputs/generic collection')
    stdout = checked(terminal['stdout']); checked(terminal['stderr'])
    return dict(originalOwner=terminal['pid'],seconds=trial['outerSeconds'],rawExitCode=terminal['rawExitCode'],cleanOwnership=True,request=request_ref,terminal=row(root/'terminal.json'),stdout=terminal['stdout'],stderr=terminal['stderr']),stdout

def host_cleanup(arm, actual, client, work):
    if arm == 'stock':
        need(actual['prepared'] is True and actual['originalDependencyInputsPreserved'] is actual['originalApplicationInputsPreserved'] is True, 'Matched Node preparation/input cleanup')
        need(type(actual['transportErrors']) is list and len(actual['transportErrors']) <= 114, 'Bounded matched Node transport outcomes')
        for error in actual['transportErrors']:
            need(type(error) is dict and set(error) == {'url','name','message','stack'} and all(type(error[k]) is str for k in error), 'Typed exact matched Node transport error')
            need(error['url'].startswith('/') and len(error['url']) <= 2048 and len(error['name']) <= 1024 and len(error['message']) <= 65536 and len(error['stack']) <= 262144, 'Matched Node transport diagnostic bounds')
        need(actual['control'] == client and actual['controlClientResult'] == row(work/'client/result.json'), 'Matched Node actual client publication')
        exit_record = actual['controlClientExit']; logs = []
    else:
        need(actual['originalInputsPreserved'] is actual['readonlyAppPreserved'] is True and actual['client']['result'] == row(work/'client/result.json'), 'Guest client/final inputs')
        exit_record = actual['client']['exit']; checked(actual['client']['stdout']); checked(actual['client']['stderr'])
        server = actual['server']; need(server['shutdownRequested'] is server['sigintSent'] is True and server['forcedCleanup'] is False and server['exit'] == dict(code=0,signal=None,error=None), 'Normal host SIGINT cleanup')
        stdout_capture(server['stdoutCapture'],server['stdout']); logs = [server['stdout']]
        if arm == 'wasmtime': checked(server['stderr']); logs.append(server['stderr'])
        else:
            need(actual['configVerifiedBeforeDev'] is True and actual['readiness']['workloadRegistered'] is actual['readiness']['tcpConnect'] is True and actual['readiness']['extraHttpRequests'] == 0, 'Stock cloud config/readiness (no HTTP warmup)')
            need([c['label'] for c in actual['commands']] == ['config-show','wash-dev','full-contract-client'], 'Inherited actual command labels; label is not full-suite execution')
            for c in actual['commands'][:2]:
                need(c['exit'] == dict(code=0,signal=None,error=None) and c['timeout'] is c['forcedCleanup'] is False, 'Stock cloud direct command cleanup')
                stdout_capture(c['stdoutCapture'],c['stdout']); logs += [c['stdout'],row(Path(c['stderrPath']))]
            want,got = actual['configured'],actual['effectiveConfiguration']
            need(got['version'] == want['version'] == '2.11.0' and got['build'] == want['build'], 'Stock cloud effective build')
            for key in ('address','command','component_path','service','volumes'): need(got['dev'][key] == want['dev'][key], 'Stock cloud effective dev ' + key)
            need(want['dev']['volumes'] == [dict(host_path=str(work/'app'),guest_path='/app'),dict(host_path=str(work/'cache'),guest_path='/app/.next/cache')], 'Exactly app/cache mounts')
            need(want['workload']['environment'] == {'config':dict(STARLING_NEXT_ORIGIN=client['origin'],NODE_ENV='production',NEXT_TELEMETRY_DISABLED='1')} and want['workload']['allowedHosts'] == [client['origin']+'/'] and want['workload']['allowedIpNameLookups'] == want['workload']['allowedHostLoopbackPorts'] == [], 'Exact self-origin egress/three guest environment values')
            for key in ('components','plugins','host_plugins'): need(got['dev'].get(key,[]) == [], 'No additional cloud dev capability')
            for key in ('allowedHosts','allowedIpNameLookups','allowedHostLoopbackPorts'): need(got['workload'][key] == want['workload'][key], 'Cloud effective workload ' + key)
            need(got['workload'].get('config',{}) == {} and got['workload']['environment']['config'] == want['workload']['environment']['config'] and got['wit']['skip_fetch'] is True, 'Cloud effective guest configuration')
    need(exit_record['code'] == (0 if client['passed'] else 1) and exit_record['signal'] is None and exit_record.get('error') is None, 'Client status versus semantic outcome')
    if arm == 'stock' or client['passed']: need(actual['errors'] == [], 'Actor cleanup/publication error')
    else:
        stage = 'deployment-or-control' if arm == 'wasmtime' else 'wasmcloud-full-deployment-or-control'
        need(len(actual['errors']) == 1 and actual['errors'][0].get('stage') == stage and actual['errors'][0].get('name') == 'AssertionError', 'Only known probe control assertion allowed for semantic raw1')
    return logs

def diagnostic_census(refs, arm):
    # Literal closed-log observations only. Counts are not request identities,
    # signal/trap attribution, resource retirement or a universal error parser.
    tokens={'requestAbortedOccurrences':'Request aborted','mozallocAbortRedirections':'Redirecting call to abort() to mozalloc_abort','workerWasmBacktraceMarkers':'worker error: error while executing at wasm backtrace:','wasmBacktraceOccurrences':'wasm backtrace','hyperIncompleteMessageOccurrences':'hyper::Error(IncompleteMessage)'}
    files=[];totals={key:0 for key in tokens};seen=set()
    for ref in refs:
        if ref['path'] in seen: continue
        seen.add(ref['path']);data=checked(ref);text=data.decode('utf8',errors='replace');counts={key:text.count(token) for key,token in tokens.items()}
        for key,value in counts.items(): totals[key]+=value
        files.append(dict(file=ref,counts=counts,decode='UTF8 replacement for literal census; original bytes/hash retained'))
    observed=any(totals[key]>0 for key in ('requestAbortedOccurrences','mozallocAbortRedirections','workerWasmBacktraceMarkers','wasmBacktraceOccurrences'))
    return dict(files=files,counts=totals,hostAbortDiagnosticsPresent=observed,guestAbortDiagnosticsPresent=arm!='stock' and observed,nativeLifecycleAccepted=False,absenceWouldProveRetirement=False,requestIdentityOrCauseInferred=False)

def review_trial(trial,binding):
    arm=trial['arm']; work=Path(trial['outputRoot']); root=work/'client'
    need(trial['runId'] == 'disconnect-recovery-'+arm+'-first' and trial['outputPrefix'] == '/private/tmp/starling-node-compat/next-disconnect-recovery-'+arm+'-v1' and str(work) == trial['outputPrefix']+'-'+trial['runId'], 'Fresh exact probe namespace')
    need(trial['plan'] == binding['plans'][arm], 'Actual selected arm plan'); plan=refdoc(trial['plan']);checked(trial['actor'])
    auth_ref=row(Path(trial['authorityPath'])); authority=refdoc(auth_ref)
    need(authority['plans' if arm == 'stock' else 'plan'] == trial['plan'] and authority['sourceIndex'] == binding['runtimeIndex'], 'Runtime authority plan/Source roles')
    need(authority['controlOnly'] is True and authority['browserAllowed'] is False and authority['rscStreamObserverAllowed'] is False and authority['disconnectRecoveryProbeAllowed'] is True, 'Probe authority capability scope')
    for key in ('constructionReview','constructionResult','constructionRequest','engineAdmission','component','envelope','compositionReview'): need(authority[key] == binding[key], 'Actual admitted prerequisite role ' + key)
    owner,outer_stdout=owned_trial(trial,plan,auth_ref)
    actual=document(work/'result.json');client=document(root/'result.json');receipt_ref=row(root/'publication.json');receipt=refdoc(receipt_ref)
    need(actual['rootAuthority'] == auth_ref and actual['controlOnly'] is True and actual['fullOriginalContractExecuted'] is actual['fullNextAccepted'] is actual['browserInvoked'] is False, 'Actor actual probe-only fields')
    need(receipt['result'] == row(root/'result.json') and typed_equal(json.loads(published(receipt['result'],receipt['resultPublication'],True)),client), 'Durable whole result receipt')
    client_plan=document(Path(plan['clientSource']['path']).parent/'plan.json'); outcomes=client_review(client,receipt,root,client_plan)
    for actor_key,client_key in [('probeExecuted','probeExecuted'),('probeCollectionComplete','collectionComplete'),('probeCleanupComplete','cleanupComplete')]: need(actual[actor_key] is client[client_key], 'Actor copied actual completion field')
    logs=host_cleanup(arm,actual,client,work)
    diagnostics=diagnostic_census(logs if logs else [owner['stdout'],owner['stderr']],arm)
    summary_raw=outer_stdout if arm == 'stock' else checked(actual['client']['stdout']);summaries=[]
    for line in summary_raw.splitlines():
        try: value=json.loads(line)
        except (ValueError,UnicodeError): continue
        if type(value) is dict and value.get('suite') == SUITE and 'publication' in value: summaries.append(value)
    need(len(summaries) == 1,'One actual durable client stdout summary');summary=summaries[0]
    need(summary['result'] == receipt['result'] and summary['publication'] == receipt_ref and all(summary[k] is client[k] for k in ('probeExecuted','collectionComplete','cleanupComplete','passed')) and summary['errors'] == len(client['errors']), 'Terminal client summary/receipt')
    transport_errors=actual['transportErrors'] if arm == 'stock' else []
    actor_passed=client['passed'] and not actual['errors'] and not transport_errors
    need(actual['passed'] is actor_passed and owner['rawExitCode'] == (0 if actor_passed else 1), 'Original actor/owner outcome including host transport failures')
    return dict(verifiedDataReviewPassed=True,outputRoot=str(work),ownerOutputRoot=trial['ownerOutputRoot'],owner=owner,actualResult=row(work/'result.json'),clientResult=row(root/'result.json'),clientPublication=receipt_ref,hostLogs=logs,probe=outcomes,diagnostics=diagnostics,actorErrors=actual['errors'],actorTransportErrors=transport_errors,actorTransportErrorCount=len(transport_errors),transportErrorRequestIdentityInferred=False,passed=actor_passed,clientObservationsPassed=client['passed'],functionalRecoveryPassed=actor_passed,guestAbortDiagnosticsPresent=diagnostics['guestAbortDiagnosticsPresent'],nativeLifecycleAccepted=False,fullOriginalContractExecuted=False,fullNextAccepted=False)

def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode: raise RuntimeError('Use Python -I -B, without -O; refused before data reads')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('bindings',type=Path);parser.add_argument('sha256');parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    binding_bytes=raw(args.bindings);need(digest(binding_bytes) == args.sha256,'Actual binding SHA');binding=json.loads(binding_bytes)
    need(binding['state'] == 'ROOT_DISCONNECT_RECOVERY_ACTUAL_BINDINGS_V1' and [a['arm'] for a in binding['arms']] == list(ORDER) and [a['outerSeconds'] for a in binding['arms']] == [600,600,300],'Fixed probe binding/order/caps')
    arms={}
    for trial in binding['arms']:
        try: arms[trial['arm']]=review_trial(trial,binding)
        except FileNotFoundError as error: arms[trial['arm']]=dict(verifiedDataReviewPassed=False,passed=None,missingOrUnattempted=True,errors=[str(error)],fullNextAccepted=False)
        except Exception as error: arms[trial['arm']]=dict(verifiedDataReviewPassed=False,passed=None,errors=[dict(type=type(error).__name__,message=str(error))],fullNextAccepted=False)
    need(all(stamp(p) == value for p,value in stamps.items()),'Final review input bookend')
    verified=all(a['verifiedDataReviewPassed'] for a in arms.values())
    result=dict(schemaVersion=1,state='ROOT_DISCONNECT_RECOVERY_DATA_REVIEW_COMPLETED_V1',verifiedDataReviewPassed=verified,allClientObservationsPassed=verified and all(a['clientObservationsPassed'] is True for a in arms.values()),allFunctionalRecoveryPassed=verified and all(a['passed'] is True for a in arms.values()),guestAbortDiagnosticsPresent=any(a.get('guestAbortDiagnosticsPresent',False) for a in arms.values()),nativeLifecycleAccepted=False,actualReviewer=row(Path(__file__).resolve()),runtimeBindings=dict(path=str(args.bindings),sha256=args.sha256,bytes=len(binding_bytes)),fixedOrder=list(ORDER),arms=arms,reviewedInputs=list(observed_refs.values()),delegatedPrerequisites={k:binding[k] for k in ('constructionReview','engineAdmission','compositionReview','hostToolRevalidation','appReview')},oldFailuresPreserved=True,sameStoreOrResourceRetirementProved=False,guestCancellationObserved=False,fullOriginalContractExecuted=False,fullNextAccepted=False,
        limits=['Fixed3warmup+16measured cycles; no retry or adaptive growth','Functional recovery is separate from literal abort/backtrace diagnostics; raw0 is not lifecycle acceptance','Local first-body close and parser flags do not prove peer truncation or guest cancellation','Known negative protocol/semantic outcomes stay negative; missing/uncertain capture is separate','No deep30k build closure replay, fullNext, promotion, reliability or cost claim'])
    need(args.output.is_absolute() and args.output.parent.resolve(strict=True) == args.output.parent,'Canonical fresh output parent')
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(review=row(args.output),verifiedDataReviewPassed=verified,arms={k:dict(passed=v['passed'],verified=v['verifiedDataReviewPassed']) for k,v in arms.items()},fullNextAccepted=False)))
    return 0 if verified else 1

if __name__ == '__main__': sys.exit(main())


