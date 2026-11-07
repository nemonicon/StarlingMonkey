"""Finite retained Stock V2/VM DATA reader; no extraction, imports or actors."""
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
LEDGER_SHA = '9a759dbf37c7dbbbd901945e47823cfd976a461579b37950655a7ed54c698809'
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


def describe(path, body):
    return dict(path=str(path), sha256=sha(body), bytes=len(body))


def physical(path):
    s = path.lstat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def regular(path):
    need(path.is_absolute() and path.resolve() == path, 'canonical file path')
    before = physical(path)
    need(stat.S_ISREG(before[2]) and before[3] == 1, 'ordinary independent file')
    body = path.read_bytes(); need(before == physical(path), 'file read bookend')
    return body, before


def own_family(draft):
    if draft:
        need(not (HERE / 'index.json').exists(), 'draft only before seal')
        return {}
    body, identity = regular(HERE / 'index.json')
    index = parse(body); expected, directories = {'index.json'}, {'.'}
    records = {str(HERE / 'index.json'): identity}
    for row in index['files']:
        rel = PurePosixPath(row['path'])
        need(not rel.is_absolute() and '..' not in rel.parts and str(rel) == row['path'] and row['path'] not in expected, 'own member path')
        expected.add(row['path']); directories.update(str(p) for p in rel.parents)
        value, identity = regular(HERE / row['path'])
        need(describe(row['path'], value) == row, 'own Source/DATA descriptor')
        records[str(HERE / row['path'])] = identity
    files, dirs = set(), {'.'}
    for path in HERE.rglob('*'):
        need(not path.is_symlink(), 'own symlink')
        if path.is_file(): files.add(path.relative_to(HERE).as_posix())
        else: need(path.is_dir(), 'own kind'); dirs.add(path.relative_to(HERE).as_posix())
    need(files == expected and dirs == directories, 'own closed files/directories')
    need(len({tuple(v[:2]) for v in records.values()}) == len(records), 'own inode aliases')
    return records


def retained(draft):
    own = own_family(draft)
    body, _ = regular(HERE / 'payload-index.json')
    need(sha(body) == LEDGER_SHA, 'exact retained ledger')
    ledger = parse(body)
    need(ledger['memberCount'] == 137 and ledger['logicalBytes'] == 1859557, 'finite original selection')
    body, _ = regular(HERE / ledger['bundle']['path'])
    need(describe(ledger['bundle']['path'], body) == ledger['bundle'], 'gzip descriptor')
    decoder = zlib.decompressobj(31); rawtar = decoder.decompress(body, 4 * 1024 * 1024)
    need(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail and len(rawtar) < 4 * 1024 * 1024, 'one complete bounded gzip member')
    rows = ledger['files']; names = [r['archivePath'] for r in rows]
    need(names == ['data/%05d' % i for i in range(137)] and len({r['original']['path'] for r in rows}) == 137, 'unique exact ordered members')
    data, pngs, end = {}, 0, 0
    with tarfile.open(fileobj=io.BytesIO(rawtar), mode='r:') as archive:
        members = archive.getmembers(); need([m.name for m in members] == names, 'complete TAR membership')
        for item, row in zip(members, rows):
            need(item.isfile() and not item.linkname and not item.pax_headers and item.uid == item.gid == item.mtime == 0 and item.mode == row['mode'], 'ordinary TAR mode/owner')
            value = archive.extractfile(item).read()
            need(describe(row['original']['path'], value) == row['original'], 'every original hash/length')
            if Path(row['original']['path']).suffix == '.png':
                need(value.startswith(b'\x89PNG\r\n\x1a\n'), 'PNG signature'); pngs += 1
            else:
                value.decode('utf8'); need(b'\0' not in value, 'text/tiny Source scope')
            need('server-reference-manifest' not in Path(row['original']['path']).name and Path(row['original']['path']).suffix not in ['.wasm', '.a', '.dylib', '.gz'], 'no binary/build-secret payload')
            data[row['original']['path']] = value
            end = item.offset_data + ((item.size + 511) // 512) * 512
        need(not any(rawtar[end:]) and len(rawtar) % 512 == 0, 'TAR zero padding only')
    need(pngs == 2 and sum(map(len, data.values())) == ledger['logicalBytes'], 'PNG/logical bytes')
    need(ledger['applicationPayloadExceptTwelveCacheFilesIncluded'] is False and ledger['toolSdkEngineNodePayloadIncluded'] is False and ledger['actorOrValidatorOrSourceEvaluated'] is False and ledger['sourceWitnessesAreNotRecursiveFamilyClosure'] is True, 'finite retention scope')
    return ledger, data, own


def semantics(ledger, data):
    def obj(path): return parse(data[str(path)])
    def blob(ref):
        body = data[ref['path']]
        need(describe(ref['path'], body) == {k: ref[k] for k in ['path', 'sha256', 'bytes']}, 'retained descriptor join')
        return body
    def refobj(ref): return parse(blob(ref))
    def role(name): return refobj(ledger['roles'][name])
    def b64(value):
        body = base64.b64decode(value, validate=True)
        need(base64.b64encode(body).decode() == value, 'canonical base64'); return body
    def ns(value):
        need(isinstance(value, str) and re.fullmatch('[0-9]+', value) is not None, 'ASCII nanosecond string'); return int(value)
    def byte_description(row):
        body = b64(row['base64']); need(type(row['bytes']) is int and len(body) == row['bytes'] and sha(body) == row['sha256'], 'inline byte descriptor'); return body
    root, monitor, seam = ledger['controlRoot'], ledger['controlMonitor'], ledger['seamRoot']
    result = obj(root + '/result.json'); vm = obj(seam + '/result.json')
    review, vm_review = role('actual-runtime-review.json'), role('actual-vm-seam-review.json')
    authority, vm_authority = role('stock-first-runtime-authority.json'), obj(seam + '/authority.json')
    need(review['verifiedDataConsistent'] is review['hostControlSamplePassed'] is True and vm_review['verifiedPassed'] is True, 'closed factual reviews')
    need(refobj(review['actualResult']) == result and refobj(vm_review['actualResult']) == vm, 'reviews bind actual results')
    need(review['rootAuthority'] == ledger['roles']['stock-first-runtime-authority.json'] and vm_review['rootAuthority'] == describe(seam + '/authority.json', data[seam + '/authority.json']), 'Root authority roles')
    need(authority['vmSeamDataReview'] == review['requiredVmSeamDataReview'] == ledger['roles']['actual-vm-seam-review.json'] and authority['vmSeamResult'] == review['requiredVmSeamResult'] == vm_review['actualResult'], 'real VM prerequisite joined')
    index_ref = ledger['roles']['next-portable-cache-stock-candidate-v2/index.json']
    plan_ref = ledger['roles']['next-portable-cache-stock-candidate-v2/plans.json']
    plan = refobj(plan_ref)
    need(authority['sourceIndex'] == vm_authority['sourceIndex'] == review['sourceIndex'] == index_ref and authority['plans'] == review['plans'] == plan_ref, 'genuine V2 Source generation')
    # These are finite indexed witnesses, not recursive Source-family closure.
    for name, ref in ledger['roles'].items():
        if '/' not in name or name.endswith('/index.json'): continue
        folder, relative = name.split('/', 1)
        index_name = folder + '/index.json'
        if index_name not in ledger['roles']: continue
        source = role(index_name); member = next(r for r in source['files'] if r['path'] == relative)
        need(blob(ref) == data[ref['path']] and member['sha256'] == ref['sha256'] and member['bytes'] == ref['bytes'], 'indexed Source witness')
    need(authority['localhostServerAllowed'] is authority['browserAllowed'] is True and all(authority[k] is False for k in ['compilerAllowed', 'nativeBuildAllowed', 'guestAllowed', 'engineAllowed', 'externalApplicationDeploymentAllowed']), 'exact Root permissions')
    need(vm_authority['applicationOrHttpOrBrowserOrGuestAllowed'] is False and vm_authority['noNodeFlags'] is True, 'VM-only grant')

    def owner(where, pid, cap, auth_ref, argv, observation_path):
        started, terminal = obj(where + '/started.json'), obj(where + '/terminal.json')
        need(type(started['pid']) is int and started['pid'] == terminal['pid'] == pid and started['timeoutSeconds'] == cap and started['argv'] == argv, 'original pid/cap/argv')
        need(started['authority'] == terminal['authority'] == auth_ref and type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0, 'original authority/raw0')
        need(terminal['timeout'] is terminal['forcedCleanup'] is False and terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']), 'original clean ownership')
        need(all(r['alive'] is r['signalAllowed'] is False for r in terminal['finalGroups']), 'final groups gone')
        names = sorted(p for p in data if p.startswith(where + '/owned-')); snapshots = [obj(p) for p in names]
        need([r['sequence'] for r in snapshots] == list(range(len(snapshots))) and [r['process'] for r in snapshots] == terminal['observedProcesses'], 'all owned frames')
        for key in ['stdout', 'stderr']: blob(terminal[key])
        observation = obj(observation_path)
        need(observation['terminal'] == describe(where + '/terminal.json', data[where + '/terminal.json']) and observation['rawExitCode'] == 0, 'original observation terminal')
        return observation, len(snapshots), terminal
    stock_argv = [plan['node']['path'], str(Path(index_ref['path']).parent / 'run-stock.mjs'), root, plan['applicationSource'], plan['browserTools'], authority['runId']]
    observation, frames, terminal = owner(monitor, 92341, 300, review['rootAuthority'], stock_argv, monitor + '/observation.json')
    need(frames == 14 and observation['ownedGroupsClean'] is observation['protectedInputsPreserved'] is observation['hostExperimentPassed'] is True and observation['guestOrNativeExecuted'] is False and refobj(observation['result']) == result, 'actual stock owner completion')
    vm_observation, vm_frames, vm_terminal = owner(seam + '/monitor', 91470, 120, vm_review['rootAuthority'], vm_authority['argv'], seam + '/observation.json')
    need(vm_frames == 1 and vm_observation['clean'] is vm_observation['passed'] is vm_observation['inputsAndCopiesPreserved'] is True and vm_observation['appHttpBrowserGuestExecuted'] is False and refobj(vm_observation['result']) == vm, 'actual VM completion')
    need(vm['passed'] is True and vm['errors'] == [] and vm['oldExpectedError']['code'] == 'ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING' and vm['oldExpectedError']['name'] == 'TypeError', 'real old VM error retained')
    expected_class = dict(defaultSameAsRealNodeRequire=True, repeatedNamespaceIdentity=True, constructedValue='main-loader:7', candidateSynchronousRequireIsSeparate=True)
    need(equal(vm['newDefaultClass'], expected_class) and vm['noHttpNextBrowserOrGuest'] is True and vm['node'] == result['node'] == 'v22.14.0', 'real new VM class/cache observations')
    need(vm['oldSnapshot']['cachedModules'] == 1 and vm['newSnapshot']['cachedModules'] == 2 and vm['oldSnapshot']['compiled'] == [seam + '/fixtures/driver.cjs'] and vm['newSnapshot']['compiled'] == [seam + '/fixtures/driver.cjs', seam + '/fixtures/target.cjs'], 'separate candidate synchronous cache')
    for row in vm_authority['fixtures']:
        need(blob(row['source']) == blob(row['target']) and row['mode'] == 0o444, 'exact two VM fixtures')
    need(len(vm_authority['fixtures']) == len(vm['fixtures']) == 2 and b'ExperimentalWarning' in blob(vm_terminal['stderr']), 'VM warning retained, not filtered')
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
    # Both actual DOM interactions, full strict zero-error gate and ten decoded bodies.
    b=obj(root+'/browser/result.json'); need(b==result['browser'] and b['origin']==result['origin'], 'whole browser record')
    need(len(b['tests'])==2 and all(t['passed'] is True and t['timedOut'] is False and t['error'] is None for t in b['tests']), 'two functional tests')
    tests={t['id']:t for t in b['tests']}; co=tests['client-counter']['observations']; ao=tests['server-action']['observations']
    need(co['initial']=='NEXT_CLIENT_COUNT:0' and co['afterClick']=='NEXT_CLIENT_COUNT:1' and co['hydratedClickObserved'] is True, 'hydrated increment')
    need(ao['marker']=='NEXT_ACTION_RESULT' and ao['value']=='browser-action' and ao['url']==result['origin']+'/action-result?value=browser-action' and ao['actualFormPostObserved'] is True and ao['hiddenInputNames']==names, 'actual browser action')
    for test in b['tests']: need(blob(test['screenshot']).startswith(b'\x89PNG\r\n\x1a\n'), 'PNG retained')
    need(all(b[k]==[] for k in ['pageerrors','consoleerrors','failedrequests','errors']) and b['browserClosed'] is b['ephemeralContexts'] is True and b['userProfileUsed'] is False and b['perTestTimeoutMs']==20000 and b['responseCaptureDrainBeforeCloseLimitMs']==500, 'strict browser zero errors/caps')
    worker=blob(ledger['roles']['next-portable-cache-native-candidate-v1/browser-check.mjs'])
    pins={p['path']:p for p in parse(re.search(rb'const assetPins=(\[.*?\]);',worker).group(1))}; paths=set()
    for row in b['assetBodies']:
        pin=row['expected']; body=blob(row['decodedBody']); need(pin==pins[pin['path']] and sha(body)==pin['sha256'] and len(body)==pin['bytes'] and row['sourceMatch'] is True and row['status']==200, 'exact decoded asset pin'); paths.add(pin['path'])
    need(len(pins)==5 and paths==set(pins) and len(b['assetBodies'])==9 and len(b['bodyCaptures'])==10, 'five pins/nine JS/ten decoded bodies')
    for row in b['bodyCaptures']:
        blob(row['decodedBody']); need(row['bodyCompletion']['kind']=='fulfilled' and row['bodyCompletion']['underlyingPromiseHandled'] is True, 'body fulfilled')
    post=next(r for r in b['bodyCaptures'] if r['method']=='POST' and r['url']==result['origin']+'/actions')
    need(post['status']==200 and post['decodedBody']['bytes']==2963 and post['encodedSizes'] is not None, 'complete captured action body, no wire-EOF inference')
    need(all(r['completion']=='fulfilled' and r['error'] is None and r['underlyingPromiseHandled'] is True for r in b['responseFinishedObservations']), 'all finished observations fulfilled')
    need(b['passed'] is b['functionalPassed'] is b['assetCapturePassed'] is b['browserErrorFree'] is True and result['browserExit']==dict(code=0,signal=None), 'strict browser gate')
    # Exactly twelve retained cache files; all other app bytes remain omitted.
    cache_refs=review['currentPortableBackendRecords']; need(len(cache_refs)==12 and all(r['mode']==0o644 for r in cache_refs), 'actual cache records/modes')
    epochs={}; entries=[]
    for row in cache_refs:
        wrapper=refobj(row); need(wrapper['schemaVersion']==1 and sha(wrapper['payload'].encode())==wrapper['sha256'], 'cache envelope')
        value=parse(wrapper['payload'])
        if '/epochs/' in row['path']: need(value['tag'] not in epochs, 'unique epoch'); epochs[value['tag']]=value['epoch']
        else: entries.append(value)
    need(len(epochs)==10 and len(entries)==2, 'two FETCH entries/ten epochs')
    for entry in entries:
        need(entry['epochs']==[epochs[t] for t in entry['tags']] and entry['value']['kind']=='FETCH', 'current tag epochs')
        value=parse(entry['value']['data']['body'])
        need(equal(value,after) if value['marker']=='NEXT_CACHE_VALUE' else value==dict(marker='NEXT_PORTABLE_CACHE_VALUE',nonce=values[2]), 'final cache value equals actual after response')
    correction=role('cache-mode-source-correction.json'); need(correction['sourceFacts']['explicitChildDirectoryModeRequested'] is correction['sourceFacts']['explicitFileModeRequested'] is False and correction['allRecordedGateResultsUnchanged'] is True, 'source-mode erratum retained')
    handler=blob(ledger['roles']['next-portable-cache-handler-candidate-v2/cache-handler.cjs'])
    need(b'mkdirSync(p);' in handler and b"writeFileSync(pending, bytes, { flag: 'wx' });" in handler, 'actual c101 mode-free calls')
    need(result['ownedPortableCacheParent']==dict(path=str(Path(ledger['ownedCacheRoot']).parent),mode=0o700,createdAfterOwnedReset=True), 'launcher private parent record')
    comparison=role('action-comparison.json')
    need(comparison['verifiedFiniteDataConsistent'] is True and all(comparison[k] is False for k in ['nativeStrictBrowserOrLegacyFailureAccepted','stockV1FailureReclassified','uniqueCauseProven','fullNextOrMatchedPairAccepted','rawNativeBodySynthesized']), 'comparison documentary scope')
    need(result['prepared'] is result['passed'] is result['originalContractPassed'] is result['originalApplicationInputsPreserved'] is True and result['guestExecuted'] is False and result['errors']==result['transportErrors']==[], 'one stock sample passed, original preservation')
    need(review['nativeOverallOrMatchedPairAccepted'] is review['oldV1FailureOrNativeFailuresReclassified'] is review['causeOrReliabilityOrStoreIdentityInferred'] is review['fullNextAcceptance'] is review['adoption'] is False, 'no native/failure/parity promotion')
    return dict(vmOwnerCap=120,stockOwnerCap=300,originalRawExitCodes=[0,0],ownedFrames=[vm_frames,frames],
                vmOldErrorRetained=True,vmNewClassObservationsMatched=True,nonceChecks=52,supplementalChecks=80,
                originalHttpPassed=24,legacyGeneration=[1,2],strictStreamChunks=5,strictBrowserTests=2,
                decodedBrowserBodies=10,pinnedAssets=5,cacheFiles=12,modeCorrectionRetained=True,
                underlyingAppNodeSdkOrNativePayloadsRevalidated=False,sourceWitnessesNotWholeClosures=True,
                nativeOrOldFailuresAccepted=False,causeOrReliabilityOrFullNextOrAdoptionProved=False,
                actorOrSourceEvaluatorInvoked=False)


def current(ledger):
    records={}
    for row in ledger['files']:
        path=Path(row['original']['path']); body,identity=regular(path)
        need(describe(path,body)==row['original'] and identity==row['physicalBefore'] and stat.S_IMODE(identity[2])==row['mode'], 'current selected original')
        records[str(path)]=identity
    for tree in ledger['trees']:
        root=Path(tree['root']); files=set(); dirs=set()
        for parent,names,children in os.walk(root,followlinks=False):
            parent=Path(parent); dirs.add(parent.relative_to(root).as_posix())
            names[:]=[n for n in names if (parent/n).relative_to(root).as_posix() not in tree['excludedSubtrees']]
            for name in names+children:
                path=parent/name; need(not path.is_symlink(), 'selected current tree symlink')
                if path.is_file(): files.add(path.relative_to(root).as_posix())
                else: need(path.is_dir(), 'selected current kind')
        need(files==set(tree['files']) and dirs=={r['path'] for r in tree['directories']}, 'included tree exact membership')
        for row in tree['directories']:
            path=root/row['path']; need(physical(path)==row['physicalBefore'], 'current included directory'); records[str(path)]=row['physicalBefore']
    parent=ledger['cacheParentWitness']; path=Path(parent['path']); need(physical(path)==parent['physicalBefore'] and stat.S_IMODE(parent['physicalBefore'][2])==0o700, 'cache parent0700 physical witness'); records[str(path)]=parent['physicalBefore']
    need(len({tuple(v[:2]) for v in records.values()})==len(records), 'current selected inode aliases')
    return records


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft',action='store_true',help='only before final index publication')
    parser.add_argument('--current',action='store_true',help='also read only137 selected originals/cache12 and included rosters')
    args=parser.parse_args(); ledger,data,own=retained(args.draft); before=current(ledger) if args.current else {}
    outcome=semantics(ledger,data)
    for path,identity in {**own,**before}.items(): need(physical(Path(path))==identity, 'final physical bookend')
    print(json.dumps(dict(state='RETAINED_STOCK_V2_AND_VM_DATA_CONSISTENT_V1',dataConsistent=True,capsuleSealed=not args.draft,
                         members=137,currentOriginalsChecked=137 if args.current else 0,scope=outcome),sort_keys=True))


if __name__=='__main__':
    main()
