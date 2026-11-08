"""Portable finite fixed-pair DATA reader. Never opens original descriptor paths."""
from pathlib import Path, PurePosixPath
import base64
import hashlib
import json
import math
import os
import re
import stat
import zlib

HERE = Path(__file__).resolve().parent
MANIFEST_SHA256 = 'PENDING'
LIMIT = 32 * 1024 * 1024
UNICODE, RECOVERY = 'concurrent-€-😀-café', 'recovered-界-✅'

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
        return len(a) == len(b) and all(equal(v, w) for v, w in zip(a, b))
    return a == b


def parse(body):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, 'duplicate JSON key'); out[key] = value
        return out
    def constant(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(body, object_pairs_hook=pairs, parse_constant=constant)


def sha(body):
    return hashlib.sha256(body).hexdigest()



def profile(root, result, data, fixture):
    # Bounded DATA predicates carried from the reviewed Stock V2 packet reader;
    # no producer, validator, guest, captured code or analyzer is imported.
    def obj(path): return parse(data[path])
    def blob(ref):
        body = data[ref['path']]
        need(len(body) == ref['bytes'] and sha(body) == ref['sha256'], 'body descriptor')
        return body
    def role(name):
        need(name == 'fixture-contract.json', 'sole declared fixture role')
        return fixture
    def b64(value):
        body = base64.b64decode(value, validate=True)
        need(base64.b64encode(body).decode() == value, 'canonical base64')
        return body
    def ns(value):
        need(type(value) is str and re.fullmatch('[0-9]+', value) is not None, 'finite ns')
        return int(value)
    def byte_description(row):
        body = b64(row['base64'])
        need(len(body) == row['bytes'] and sha(body) == row['sha256'], 'chunk bytes')
        return body
    # All five raw publications precede semantics; exact positive52 translation.
    capture = result['portableCache']; need(obj(root + '/portable-cache/observations.json') == capture and capture['origin'] == result['origin'], 'whole raw five')
    count = 0
    def nonce_check(value, label):
        nonlocal count
        count += 1; need(value, label)
    nonce_check(capture['schemaVersion'] == 1 and capture['marker'] == 'NEXT_PORTABLE_CACHE_HTTP_CAPTURE_V1', 'nonce schema')
    nonce_check(re.fullmatch(r'http://127\.0\.0\.1:[1-9][0-9]{0,4}', capture['origin']) is not None, 'loopback nonce origin')
    nonce_check(capture['path'] == '/api/portable-cache' and capture['requestSeconds'] == 20 and capture['deliveredBodyCap'] == 65536, 'fixed nonce protocol')
    rows = capture['records']; nonce_check(len(rows) == 5, 'exact five'); values = []
    for row, (ident, method) in zip(rows, [('portable-first','GET'),('portable-repeat','GET'),('portable-revalidate','POST'),('portable-after','GET'),('portable-after-repeat','GET')]):
        need(obj(root + '/portable-cache/' + ident + '.json') == row, 'nonce case raw publication')
        nonce_check(row['id'] == ident and row['method'] == method and row['url'] == result['origin'] + '/api/portable-cache', 'nonce identity')
        nonce_check(type(row['status']) is int and row['status'] == 200, 'nonce status')
        nonce_check(row['complete'] is True and row['overflow'] is False and row['transportError'] is None and row['cleanupErrors'] == [], 'nonce transport')
        nonce_check(type(row['receivedBytes']) is int and row['receivedBytes'] == row['retainedBytes'] and 0 <= row['receivedBytes'] <= 65536, 'nonce counts')
        headers = row['headers']; nonce_check(isinstance(headers,list) and all(isinstance(p,list) and len(p)==2 and all(isinstance(x,str) for x in p) for p in headers), 'nonce headers')
        nonce_check(dict(headers).get('content-type','').split(';')[0].strip().lower() == 'application/json', 'nonce JSON media')
        body = blob(row['body']); nonce_check(body == b64(row['bodyBase64']) and len(body) == row['retainedBytes'], 'nonce raw bytes')
        value = parse(body); nonce_check(isinstance(value,dict), 'nonce object')
        if method == 'POST': nonce_check(value == dict(marker='NEXT_PORTABLE_CACHE_REVALIDATED',tag='portable-fetch-v1'), 'nonce acknowledgement')
        else:
            nonce_check(set(value) == {'marker','nonce'} and value['marker']=='NEXT_PORTABLE_CACHE_VALUE' and isinstance(value['nonce'],str) and re.fullmatch('[0-9a-f]{64}',value['nonce']) is not None, 'nonce value'); values.append(value['nonce'])
    nonce_check(values[0] == values[1], 'first==repeat'); nonce_check(values[2] != values[0], 'after!=first'); nonce_check(values[2] == values[3], 'after==afterRepeat')
    need(count == 52 and result['portableCacheValidation']['checks'] == 52 and result['portableCacheValidation']['passed'] is True and result['portableCacheValidation']['failures'] == [], 'independent52 nonce gate')
    # Finite independent translation of all80 positive supplemental checks.
    s = result['supplemental']; need(obj(root + '/supplemental/observations.json') == s and s['origin'] == result['origin'], 'whole raw six')
    supp_count = 0
    def check(value, label):
        nonlocal supp_count
        supp_count += 1; need(value, label)
    cases = [('context-alpha','concurrent','GET','/api/context',{'cookie':'fixture_token=parallel-alpha','x-fixture-probe':'probe-alpha'},200,dict(marker='NEXT_CONTEXT',cookie='parallel-alpha',header='probe-alpha')),
             ('context-beta','concurrent','GET','/api/context',{'cookie':'fixture_token=parallel-beta','x-fixture-probe':'probe-beta'},200,dict(marker='NEXT_CONTEXT',cookie='parallel-beta',header='probe-beta')),
             ('chunked-unicode-json','concurrent','POST','/api/json',{'content-type':'application/json'},200,dict(marker='NEXT_JSON_POST',value=UNICODE)),
             ('malformed-json','concurrent','POST','/api/json',{'content-type':'application/json'},400,dict(marker='NEXT_JSON_BAD_INPUT')),
             ('empty-context-recovery','recovery','GET','/api/context',{},200,dict(marker='NEXT_CONTEXT',cookie=None,header=None)),
             ('json-recovery','recovery','POST','/api/json',{'content-type':'application/json'},200,dict(marker='NEXT_JSON_POST',value=RECOVERY))]
    check(type(s['schemaVersion']) is int and s['schemaVersion']==1 and s['suite']=='NEXT_CONCURRENT_CONTEXT_BODY_RECOVERY_V1', 'six suite')
    check(s['clientOverlapOnly'] is True and s['sameStoreOrNativeResourceIdentityClaimed'] is False and s['guestReadOrPacketChunkBoundariesClaimed'] is False, 'client-only scope')
    check(s['perRequestTimeoutMs']==20000, 'six deadline'); rows=s['observations']
    check(len(rows)==6 and len({r['id'] for r in rows})==6, 'six unique'); check(sorted(r['id'] for r in rows)==sorted(c[0] for c in cases), 'six inventory')
    need(s['completionOrder']==[r['id'] for r in rows], 'six completion/publication order')
    for ident,phase,method,path,headers,status,expected in cases:
        row=next(r for r in rows if r['id']==ident); need(obj(root+'/supplemental/'+ident+'.json')==row, 'six case record')
        check(row['phase']==phase and row['request']['method']==method and row['request']['path']==path, 'six role'); check(row['request']['headers']==headers, 'six request headers')
        check(all(row[k] is None for k in ['error','readerReleaseError','publicationError']) and row['bodyEofObserved'] is True and row['signalAborted'] is False, 'six complete/error-free')
        check(type(row['status']) is int and row['status']==status, 'six status'); check(row['body'] is not None and row['body']['path']==root+'/supplemental/'+ident+'.body', 'six body path')
        body=b64(row['bodyBase64']); check(row['body']['bytes']==len(body) and row['body']['sha256']==sha(body), 'six body hash'); need(blob(row['body'])==body, 'six physical body')
        pieces=[byte_description(c) for c in row['responseChunks']]; check(b''.join(pieces)==body, 'six all response chunks'); check(len(body)<=1048576, 'six accepted cap')
        check(equal(parse(body),expected), 'six exact JSON')
        if path=='/api/context':
            check(row['responseHeaders'].get('x-fixture-response')=='context-ok', 'six response header'); check(all(v in row['responseHeaders'].get('set-cookie','') for v in ['fixture_reply=set','HttpOnly','SameSite=lax']), 'six response cookie')
        check(ns(row['terminalNs'])>=ns(row['startedNs']), 'six ordering')
        need(ns(row['startedNs'])<=ns(row['headersNs'])<=ns(row['terminalNs']) and all(ns(row['headersNs'])<=ns(c['arrivedNs'])<=ns(row['terminalNs']) for c in row['responseChunks']), 'six header/chunk ordering')
    first=[r for r in rows if r['phase']=='concurrent']; later=[r for r in rows if r['phase']=='recovery']
    check(len(first)==4 and len(later)==2, 'phase inventory'); check(all(ns(a['startedNs'])<=ns(b['terminalNs']) for a in first for b in first), 'client overlap'); check(all(ns(r['startedNs'])>=ns(s['phaseOneTerminalNs']) for r in later), 'recovery starts later')
    uploaded=b64(s['chunkedRequest']['body']['base64']); parts=[b64(c['base64']) for c in s['chunkedRequest']['chunks']]
    expected_upload=json.dumps(dict(value=UNICODE),ensure_ascii=False,separators=(',',':')).encode()
    check(len(parts)==2 and b''.join(parts)==uploaded==expected_upload, 'Unicode request'); check(s['chunkedRequest']['splitInsideUtf8Sequence'] is True and s['chunkedRequest']['clientEnqueueBoundariesOnly'] is True and len(parts[0])==uploaded.index('€'.encode())+1, 'Euro split'); check(all(byte_description(c)==p for c,p in zip(s['chunkedRequest']['chunks'],parts)), 'upload hashes')
    head=[e for e in s['uploadEvents'] if e['event']=='head-enqueued']; tail=[e for e in s['uploadEvents'] if e['event']=='tail-enqueued']
    check(len(head)==len(tail)==1 and ns(head[0]['ns'])<=ns(tail[0]['ns']), 'two enqueue records'); check(all(e['event'] not in ['tail-error','release-error','upload-cancelled'] for e in s['uploadEvents']), 'upload no errors'); check(all(ns(r['terminalNs'])<=ns(tail[0]['ns']) for r in first if r['id']!='chunked-unicode-json'), 'tail after peers')
    need(supp_count==80 and result['supplementalValidation']['checks']==80 and result['supplementalValidation']['passed'] is True and result['supplementalValidation']['failures']==[], 'independent80 six gate')
    need(max(ns(r['terminalNs']) for r in first)<=ns(s['phaseOneTerminalNs'])<=min(ns(r['startedNs']) for r in later), 'direct terminal/recovery boundary')
    # Original24HTTP, lexical generation and strict delivered stream.
    contract=role('fixture-contract.json'); need(len(contract['requests'])==23 and len(result['http'])==24, 'original24 inventory'); bodies={}
    for expected,row in zip(contract['requests'],result['http']):
        body=data[root+'/responses/'+row['id']+'.txt']; text=body.decode('utf8'); bodies[row['id']]=text
        need(row['id']==expected['id'] and type(row['status']) is int and row['status']==expected['status'] and row['bodySha256']==sha(body) and row['bodyBytes']==len(body), 'original raw status/hash')
        need(all(v in text for v in expected.get('includes',[])), 'original markers')
        if 'json' in expected:
            value=parse(body); need(all(k in value and equal(value[k],v) for k,v in expected['json'].items()), 'original JSON subset')
        if expected.get('location'): need(row['headers'].get('location')==expected['location'], 'original redirect')
        need(all(row['headers'].get(k)==v for k,v in expected.get('responseHeaders',{}).items()) and all(v in row['headers'].get(k,'') for k,values_ in expected.get('responseHeaderIncludes',{}).items() for v in values_), 'original response headers')
        if expected.get('equalJsonTo'): need(text==bodies[expected['equalJsonTo']], 'original repeat body')
        need(row['passed'] is True and row['failures']==[], 'original request passed')
    action=result['http'][-1]; ab=data[root+'/responses/server-action-submit.txt']
    need(action['id']=='server-action-submit' and action['status']==303 and action['headers']['location']=='/action-result?value=fixture-action' and action['bodySha256']==sha(ab) and action['bodyBytes']==len(ab) and action['passed'] is True, 'actual original action303')
    names=re.findall(r'name="(\$ACTION_ID_[^"]+)"',bodies['server-action-form-ssr']); need(len(names)==1, 'actual form id derived')
    before,after=parse(bodies['cache-first']),parse(bodies['cache-after-revalidate'])
    need(equal(before,dict(marker='NEXT_CACHE_VALUE',generation=1)) and equal(after,dict(marker='NEXT_CACHE_VALUE',generation=2)) and result['cacheInvalidation']==dict(before=before,after=after,passed=True), 'legacy1to2 gate')
    chunks=obj(root+'/stream-chunks.json'); joined=b''; shell=ready=-1
    for i,row in enumerate(chunks):
        body=b64(row['base64']); need(len(body)==row['bytes'], 'raw stream chunk'); joined+=body
        if shell<0 and b'NEXT_STREAM_SHELL' in joined: shell=i
        if ready<0 and b'NEXT_STREAM_READY' in joined: ready=i
    need(len(chunks)==5 and shell==0 and ready==2 and result['streaming']==dict(chunks=5,shellChunk=0,readyChunk=2,complete=True,incrementalDeliveryObserved=True), 'strict five-chunk stream')
    return dict(nonceChecks=count, supplementalChecks=supp_count, httpRows=len(result['http']),
                cacheIncrease=result['cacheInvalidation']['passed'], streamChunks=len(chunks))

def stamp(path):
    s = path.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def bounded(path, size):
    before = stamp(path)
    need(path.resolve() == path and stat.S_ISREG(before[2]) and before[3] == 1 and
         type(size) is int and 0 <= size <= LIMIT and before[4] == size, 'bounded regular copy')
    with path.open('rb') as handle:
        s = os.fstat(handle.fileno())
        opened = (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        need(opened == before, 'opened same file')
        raw = handle.read(size + 1)
    need(len(raw) == size and stamp(path) == before, 'copy read bookends')
    return raw, before


def png(raw):
    need(raw[:8] == b'\x89PNG\r\n\x1a\n', 'PNG signature')
    pos, ended = 8, False
    while pos < len(raw):
        need(pos + 12 <= len(raw), 'PNG chunk header')
        length = int.from_bytes(raw[pos:pos+4], 'big')
        end = pos + 12 + length
        need(end <= len(raw), 'PNG chunk bound')
        need(zlib.crc32(raw[pos+4:pos+8+length]) & 0xffffffff ==
             int.from_bytes(raw[pos+8+length:end], 'big'), 'PNG CRC')
        kind = raw[pos+4:pos+8]; pos = end
        if kind == b'IEND':
            need(length == 0 and pos == len(raw), 'terminal whole PNG IEND')
            ended = True; break
    need(ended and pos == len(raw), 'whole PNG')


def main():
    mp = HERE / 'manifest.json'
    mr, ms = bounded(mp, mp.lstat().st_size)
    need(sha(mr) == MANIFEST_SHA256, 'manifest hash')
    m = parse(mr)
    need(m['schemaVersion'] == 1 and m['maximumPayloadBytes'] == LIMIT and
         type(m['files']) is list and type(m['fileCount']) is int and
         m['fileCount'] == len(m['files']) and type(m['payloadBytes']) is int and
         0 < m['payloadBytes'] <= LIMIT, 'finite corpus cap')
    need(all(type(r) is dict and type(r.get('copy')) is dict and
             type(r['copy'].get('bytes')) is int and 0 <= r['copy']['bytes'] <= LIMIT
             for r in m['files']), 'all payload sizes valid before any payload read')
    need(sum(r['copy']['bytes'] for r in m['files']) == m['payloadBytes'] <= LIMIT,
         'aggregate pre-read total')
    data, stamps, names, inodes = {}, {}, set(), set()
    for row in m['files']:
        rel = PurePosixPath(row['copy']['path'])
        need(not rel.is_absolute() and '..' not in rel.parts and str(rel).startswith('files/') and
             str(rel) not in names, 'safe unique copy path')
        p = HERE / str(rel); raw, s = bounded(p, row['copy']['bytes'])
        need(sha(raw) == row['copy']['sha256'] == row['original']['sha256'] and
             len(raw) == row['original']['bytes'], 'retained bytes equal historical original')
        need(row['original']['path'] not in data and s[:2] not in inodes, 'independent copy')
        data[row['original']['path']] = raw; stamps[p] = s; names.add(str(rel)); inodes.add(s[:2])
    need(len(data) == m['fileCount'], 'file count')
    expected_dirs = {'.'}
    for name in names | {'manifest.json', 'check.py'}:
        q = PurePosixPath(name).parent
        while str(q) != '.': expected_dirs.add(str(q)); q = q.parent
    current_files, current_dirs = set(), {'.'}
    for p in HERE.rglob('*'):
        s = p.lstat(); name = p.relative_to(HERE).as_posix()
        need(not stat.S_ISLNK(s.st_mode), 'no symlink')
        if stat.S_ISREG(s.st_mode): need(s.st_nlink == 1, 'no hardlink'); current_files.add(name)
        else: need(stat.S_ISDIR(s.st_mode), 'no special node'); current_dirs.add(name)
    need(current_files == names | {'manifest.json', 'check.py'} and current_dirs == expected_dirs,
         'exact portable membership')
    # Every absolute path below is a dictionary label, never an I/O location.
    def obj(path): return parse(data[path])
    def role(name): return obj(m['roles'][name])
    def blob(ref):
        raw = data[ref['path']]
        need(len(raw) == ref['bytes'] and sha(raw) == ref['sha256'], 'retained role descriptor')
        return raw
    for assertion in m['reviewAssertions']:
        need(role(assertion['role'])[assertion['key']] == assertion['value'], 'documentary review field')
    plan, pair, pair_authority = role('pairPlan'), role('pairResult'), role('pairAuthority')
    need(pair_authority['plan'] == m['roleDescriptors']['pairPlan'] and
         [x['arm'] for x in plan['trials']] == pair['plannedOrder'] == ['native', 'stock'] and
         len(pair['trials']) == len(plan['trials']) == 2 and
         pair['allOriginalContractsPassed'] is pair['correlationAccepted'] is pair['fullNextAccepted'] is False,
         'fixed pair and failed original aggregate')
    all_values = [v for t in plan['trials'] for v in t['publicRequestCorrelation']['nonceByTest'].values()]
    need(len(set(all_values)) == len(all_values) == 4 and
         all(type(v) is str and re.fullmatch('[0-9a-f]{64}', v) for v in all_values), 'four public values')
    for owner in m['owners']:
        s, t = obj(owner['started']), obj(owner['terminal'])
        need(s['pid'] == t['pid'] == owner['pid'] and s['argv'] == owner['argv'] and
             s['timeoutSeconds'] == owner['capSeconds'] and s['authority'] == t['authority'] == owner['authority'],
             'original owner admission')
        need(type(t['rawExitCode']) is int and t['rawExitCode'] == owner['rawExitCode'] and
             t['timeout'] is t['forcedCleanup'] is False and
             t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True and
             all(t[k] == [] for k in ['errors','signals','interruptedSignals','remainingObservedPids']) and
             all(x['alive'] is x['signalAllowed'] is False for x in t['finalGroups']), 'clean original owner')
        need(len(owner['owned']) == len(t['observedProcesses']), 'complete owned snapshots')
        for i, path in enumerate(owner['owned']):
            v = obj(path); need(v['sequence'] == i and v['process'] == t['observedProcesses'][i], 'owned raw join')
        for key in ['stdout', 'stderr']: blob(t[key])
    analysis = role('analysis')
    need(analysis['dataParseSucceeded'] is analysis['observedPublicPostMetadataJoin'] is True and
         all(analysis[k] is False for k in ['undetectableSpoofingOrReplayExcluded','privateStoreOrResourceIdentityProved',
            'crossLaneNumericIdentityProved','postToInnerGetCausalityProved','completionOrHostTcpEofProved',
            'uniqueCauseProved','oldFailuresWaived','fullNextAccepted','productionPromotion']), 'limited observed public join')
    for ref in analysis['inputs'].values(): blob(ref)
    need(sha(data[m['roles']['analyzerSource']]) ==
         'bea8ebd58b1ca8f8539273f7caade5873b4a66312507d223f7ca4fe648f6f965', 'reviewed analyzer witness')
    need(role('analysisExecution')['rawExitCode'] == 0 and data[m['roles']['analysisStderr']] == b'', 'single analysis execution record')
    profiles = []
    for i, arm in enumerate(['native', 'stock']):
        roles = m['arms'][arm]; result, client, b, a = (obj(roles[k]) for k in ['result','client','browser','authority'])
        t = plan['trials'][i]; publication = pair['trials'][i]['publication']
        need(a['runId'] == t['runId'] and a['arm'] == arm and
             a['publicRequestCorrelation'] == t['publicRequestCorrelation'] and
             result['rootAuthority'] == m['roleDescriptors'][arm+'Authority'], 'arm literal/authority')
        need(client['browser'] == b and result['passed'] == m['expectedActorPassed'][arm] and
             publication['result'] == m['roleDescriptors'][arm+'Result'] and publication['valid'] is True,
             'published arm and unchanged failure')
        summary = profile(roles['clientRoot'], client, data, role('fixtureContract'))
        need(client['errors'] == client['transportErrors'] == [], 'complete client protocol')
        origin = client['origin']; target = origin + '/actions'; header = 'x-next-public-request-correlation'
        configured = result['publicRequestCorrelation']; manifest = obj(roles['manifest'])
        need(configured['value'] == manifest and configured['manifest'] == m['roleDescriptors'][arm+'Manifest'] and
             manifest == b['publicRequestCorrelation']['manifest'] and manifest['origin'] == origin and
             manifest['runId'] == t['runId'] and
             {k:manifest[k] for k in ['headerName','nonceByTest']} == t['publicRequestCorrelation'], 'manifest authority roles')
        blob(configured['manifest']); bc = b['publicRequestCorrelation']
        need(blob(bc['manifestSource']) == blob(bc['retainedManifest']) == data[roles['manifest']], 'exact browser manifest bytes')
        expected = manifest['nonceByTest']['server-action']
        posts = [x for x in b['actionPosts'] if x['url'] == target]
        need(len(posts) == 1 and posts[0]['headers'].get(header) == expected, 'actual POST public header')
        need(len(base64.b64decode(posts[0]['bodyBase64'], validate=True)) == posts[0]['bytes'] == 391, 'actual form bytes')
        need([x['id'] for x in b['tests']] == ['client-counter','server-action'] and
             all(x['passed'] is True and x['timedOut'] is False and x['error'] is None and
                 x['captureDrainBeforeCloseComplete'] is True and
                 x['publicCorrelationConfiguredNonce'] == manifest['nonceByTest'][x['id']] for x in b['tests']),
             'two original functional tests and configured values')
        for x in b['tests']: png(blob(x['screenshot']))
        for x in b['assetBodies']: need(x['sourceMatch'] is True and x['status'] == 200, 'decoded asset pin'); blob(x['decodedBody'])
        need(len([x for x in b['assetBodies'] if x['test']=='client-counter']) == 5, 'five counter assets')
        functional = all(x['passed'] for x in b['tests'])
        errorfree = not any(b[k] for k in ['pageerrors','consoleerrors','failedrequests'])
        strict = bool(functional and errorfree and not b['errors'] and b['browserClosed'])
        need(b['functionalPassed'] is functional and b['browserErrorFree'] is errorfree and
             b['passed'] is strict and strict == m['expectedStrictPassed'][arm], 'unchanged strict browser gate')
        captures = [x for x in b['bodyCaptures'] if x['test']=='server-action' and x['method']=='POST' and x['url']==target]
        finished = [x for x in b['responseFinishedObservations'] if x['test']=='server-action' and x['method']=='POST' and x['url']==target]
        need(len(captures)==len(finished)==1, 'test-local POST role; never requestId alone')
        if strict:
            need(captures[0]['decodedBody'] is not None and len(blob(captures[0]['decodedBody']))==2963 and
                 finished[0]['completion']=='fulfilled' and finished[0]['error'] is None and
                 captures[0]['encodedSizes']['requestBodySize']==391, 'positive POST delivery observation')
        else:
            need(captures[0]['decodedBody'] is captures[0]['encodedSizes'] is None and
                 finished[0]['completion']=='requestfailed' and len(b['errors'])==3 and
                 len(b['failedrequests'])==1 and all(x['requestId']==captures[0]['requestId'] and
                 x['message']=='net::ERR_ABORTED' for x in b['errors']), 'failed POST observations preserved')
        net = b['netlog']; nj = obj(roles['netlog'])
        blob(net['file']); need(net['completeJson'] is net['fsynced'] is True and net['errors']==[] and
                               net['eventCount']==len(nj['events']), 'complete finite NetLog publication')
        ty, so = nj['constants']['logEventTypes'], nj['constants']['logSourceType']
        candidates = { (e['source']['id'],e['source']['type']) for e in nj['events']
                       if e['source']['type']==so['URL_REQUEST'] and e.get('params',{}).get('url')==target and
                       e.get('params',{}).get('method')=='POST' }
        need(len(candidates)==1, 'one document-local POST candidate')
        sid = next(iter(candidates)); sends = [e for e in nj['events'] if
            (e['source']['id'],e['source']['type'])==sid and e['type']==ty['HTTP_TRANSACTION_SEND_REQUEST_HEADERS']]
        need(len(sends)==1 and sends[0]['params']['line']=='POST /actions HTTP/1.1\r\n', 'same-local-source send witness')
        headers = sends[0]['params']['headers']
        need(all(type(x) is str and ':' in x and '\r' not in x and '\n' not in x for x in headers), 'raw header strings')
        vals = lambda key: [x.split(':',1)[1].strip(' \t') for x in headers if x.split(':',1)[0].lower()==key]
        need(vals(header)==[expected] and vals('host')==[origin.removeprefix('http://')], 'raw public header cardinality/Host')
        need(analysis['arms'][arm]['browserPublicPostMetadataObserved'] is True and
             analysis['arms'][arm]['serverActionNonce']==expected, 'actual analysis browser-public role')
        if arm=='native':
            cap = result['server']['stdoutCapture']; stdout = blob(result['server']['stdout'])
            need(all(cap[k] is True for k in ['complete','pipeEof','fileClosed','fileBoundVerified','finalized']) and
                 all(cap[k] is False for k in ['overflow','partialWritePossible','unretainedBytesUnknown']) and cap['errors']==[] and
                 len(stdout)==cap['fileBytes']==cap['completeWriteBytes']==cap['lastReservedWriteCeiling']<=cap['limitBytes']==8388608,
                 'complete native stdout before marker DATA')
            marker = analysis['nativeMarkers']; observed = []
            for n,line in enumerate(stdout.splitlines(keepends=True),1):
                if b'NEXT_GUEST_' not in line: continue
                need(line.endswith(b'\n') and len(line)<=512, 'whole bounded marker line')
                observed.append(dict(line=n,record=parse(line)))
            need(observed==marker['records'] and marker['malformed']==marker['foreign']==marker['loggerFrames']==[],
                 'all actual parsed marker records bind raw lines')
            enters = [x for x in observed if x['record']['method']=='POST' and x['record']['path']=='/actions' and
                      x['record']['event']==x['record']['lane']+'-enter']
            need(not any(x['record']['corrState'] in ['invalid','duplicate'] for x in enters), 'no ambiguous POST enters')
            counts = {lane:sum(x['record']['lane']==lane and x['record']['corrState']=='valid' and
                              x['record']['corr']==expected for x in enters) for lane in ['adapter','classic']}
            need(counts=={'adapter':1,'classic':1} and
                 marker['selectedServerAction']['cardinalityDecision']['matchingPostEnterCounts']==counts and
                 marker['selectedServerAction']['cardinalityDecision']['joined'] is True,
                 'observed public metadata cardinality; no tokens/identity/order')
        profiles.append(dict(arm=arm,strictBrowserPassed=strict,originalActorPassed=result['passed'],**summary))
    need(stamp(mp)==ms and all(stamp(p)==s for p,s in stamps.items()), 'final current-copy bookends')
    print(json.dumps(dict(passed=True,files=len(data),payloadBytes=m['payloadBytes'],profiles=profiles,
          observedPublicPostMetadataJoin=True,originalAllPassed=False,fullNextAccepted=False,
          originalsRead=False,helpersOrAnalyzerExecuted=False,omittedNativeAppPackagePayloadsRevalidated=False,
          historicalModesInodesOwnershipDocumentary=True,liveCheckoutModesObservedOnly=True,
          noPrivateIdentityCompletionOrCauseInference=True),sort_keys=True))


if __name__ == '__main__':
    main()
