"""Bounded, read-only public-correlation DATA analysis; explicit CLI files only."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import stat
from urllib.parse import urlsplit

MIB = 1024 * 1024
MAX_TOTAL = 96 * MIB
SAFE = 9007199254740991
HEADER = 'x-next-public-request-correlation'
MARKER = 'NEXT_GUEST_RESPONSE_COMPLETION_V2'
PINNED = {
    'proposal': ('fbc52612cc86a451f4ef00399c748d5086a6fda35d9b317c2ba3a1cd3b333ea5', 12781),
    'contract': ('74709535564f1031b8238b1221ca212d37c7d7d805c6eaaf730ff94bf6d81f74', 14591),
    'guest-index': ('f8c6d52b28aa9d4cd85e9eecbf4182028cf73175595e0e6fea7fce2e3d44dca4', 3872),
    'guest-entry': ('a1d66a6e3427204f5fc0a8e2207836e71eea7b095926ce5b38e4e2ecef65c8d3', 47563),
    'browser-index': ('a2e8ca5532dfb5d57177ee0e7ea5ab6cdd039e7ac092fa5359d5fdd5ad436bd8', 3224),
    'browser-source': ('800f1feeffd75c8f07a83e4ba10c7aaa9470ab0bb45e15973ac0736ab7f38247', 30573),
    'client-index': ('9a4b59588a1fe68e06c361b74bbc2ed0ac68147a6612a951f0dadb030246636a', 3531),
    'client-source': ('4edc72d9e66468084d922e9ca0609d6db2dbdfbadf132342665d0fd9c459dd9e', 8516),
    'native-index': ('67f4eaf6eda2b2aec51e344e5ba810e6ff3c90fa3e114647b121182a03502342', 1842),
    'stock-index': ('eb286ac0f4427d9786d772bea9d72c9ddfae49a36bef0d67e157bcf5aa0bba21', 1386),
    'constructor-review': ('1dff846899ed3ba0671c875db0d2fe8e9f6afd6733038713881bfb6107774de1', 33138),
}
DATA = ['pair-plan', 'pair-result', 'native-authority', 'native-result', 'native-client',
        'native-terminal', 'native-browser', 'native-netlog', 'native-manifest',
        'native-retained-manifest', 'native-stdout', 'stock-authority', 'stock-result',
        'stock-terminal', 'stock-browser', 'stock-netlog', 'stock-manifest',
        'stock-retained-manifest']


def need(value, message):
    if not value:
        raise ValueError(message)


def stamp(path):
    s = path.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result


def parse(raw):
    def invalid(value):
        raise ValueError('Nonfinite JSON number: ' + value)
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=invalid)


def inputs(args):
    # Check aggregate size BEFORE opening any input. No descriptor path is followed.
    paths, initial, inodes = {}, {}, set()
    for name in [*PINNED, *DATA]:
        path = Path(getattr(args, name.replace('-', '_')))
        s = stamp(path)
        limit = (20 * MIB if name.endswith('-netlog') else
                 8 * MIB if name in DATA else 256 * 1024)
        if name.endswith('-manifest'):
            limit = 4096
        need(path.is_absolute() and path.resolve() == path and
             stat.S_ISREG(s[2]) and s[3] == 1 and 0 <= s[4] <= limit and
             (s[4] > 0 or name == 'native-stdout'),
             'Canonical, unique, bounded ordinary CLI file required: ' + name)
        need(s[:2] not in inodes, 'CLI physical alias: ' + name)
        inodes.add(s[:2]); paths[name] = path; initial[name] = s
    need(sum(s[4] for s in initial.values()) <= MAX_TOTAL, 'Aggregate pre-read bound')
    raw, refs = {}, {}
    for name, path in paths.items():
        s = initial[name]
        with path.open('rb') as handle:
            data = handle.read(s[4] + 1)
        need(len(data) == s[4] and stamp(path) == s, 'Input read bookend: ' + name)
        raw[name] = data
        refs[name] = dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
        if name in PINNED:
            need((refs[name]['sha256'], len(data)) == PINNED[name], 'Held Source/review pin: ' + name)
    return raw, refs, paths, initial


def match(ref, selected, label):
    need(ref == selected, 'Explicit CLI descriptor/role mismatch: ' + label)


def member(index, name, ref):
    found = [r for r in index['files'] if r['path'] == name]
    need(len(found) == 1 and found[0] == {k: v for k, v in ref.items() if k != 'path'} | {'path': name},
         'Indexed Source member: ' + name)


def clean(t):
    return (type(t.get('rawExitCode')) is int and t['rawExitCode'] in (0, 1) and
            t.get('timeout') is t.get('forcedCleanup') is False and
            t.get('parentOwnedGroupGone') is t.get('allObservedOwnedGroupsGone') is True and
            all(t.get(k) == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']) and
            all(x.get('alive') is x.get('signalAllowed') is False for x in t.get('finalGroups', [])))


def canonical_origin(value):
    need(type(value) is str, 'Origin type')
    p = urlsplit(value)
    need(p.scheme == 'http' and p.hostname == '127.0.0.1' and p.port is not None and
         0 < p.port < 65536 and value == 'http://127.0.0.1:' + str(p.port), 'Canonical loopback origin')
    return p


def manifest(value):
    need(set(value) == {'schemaVersion', 'runId', 'origin', 'headerName', 'nonceByTest'} and
         type(value['schemaVersion']) is int and value['schemaVersion'] == 1 and
         re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', value['runId']) is not None and
         value['headerName'] == HEADER and set(value['nonceByTest']) == {'client-counter', 'server-action'},
         'Exact manifest schema')
    canonical_origin(value['origin'])
    values = list(value['nonceByTest'].values())
    need(all(type(x) is str and re.fullmatch('[0-9a-f]{64}', x) for x in values) and len(set(values)) == 2,
         'Distinct exact public nonce values')


def raw_value(value):
    need(type(value) is str and len(value) <= 8192 and
         not any(ord(c) < 32 and c != '\t' or ord(c) == 127 for c in value), 'Raw header control/type bound')
    return value.strip(' \t')


def map_values(headers, name):
    need(type(headers) is dict and len(headers) <= 256, 'Finite PW header map')
    values = []
    for key, value in headers.items():
        need(type(key) is str and re.fullmatch("[!#$%&'*+.^_`|~0-9A-Za-z-]+", key), 'Header name')
        normalized = raw_value(value)
        if key.lower() == name:
            values.append(normalized)
    return values


def line_values(lines, name):
    need(type(lines) is list and len(lines) <= 256, 'Finite NetLog header lines')
    values = []
    for line in lines:
        raw_value(line)  # Validate controls BEFORE whitespace handling.
        key, colon, value = line.partition(':')
        need(colon and re.fullmatch("[!#$%&'*+.^_`|~0-9A-Za-z-]+", key), 'NetLog header field')
        if key.lower() == name:
            values.append(raw_value(value))
    return values


def netlog(document, origin, expected):
    events = document['events']; constants = document['constants']
    need(type(events) is list and len(events) <= 250000, 'Finite NetLog events')
    types, sources = constants['logEventTypes'], constants['logSourceType']
    need(type(types) is dict and type(sources) is dict and
         type(types['HTTP_TRANSACTION_SEND_REQUEST_HEADERS']) is int and type(sources['URL_REQUEST']) is int,
         'Typed NetLog constants')
    need(all(type(x) is int for x in [*types.values(), *sources.values()]) and
         len(set(types.values())) == len(types) and len(set(sources.values())) == len(sources),
         'Unambiguous NetLog type/source constants')
    target = origin + '/actions'; candidates = {}
    def identity(value):
        need(type(value) is dict and type(value.get('id')) is int and type(value.get('type')) is int,
             'Typed local NetLog source')
        return value['id'], value['type']
    for i, event in enumerate(events):
        need(type(event) is dict and type(event.get('type')) is int and type(event.get('source')) is dict,
             'NetLog event shape')
        key = identity(event['source']); params = event.get('params', {})
        need(type(params) is dict, 'NetLog params shape')
        if key[1] == sources['URL_REQUEST'] and params.get('url') == target and params.get('method') == 'POST':
            candidates.setdefault(key, []).append(i)
    witnesses = []
    if len(candidates) == 1:
        selected = next(iter(candidates))
        for i, event in enumerate(events):
            if event['type'] != types['HTTP_TRANSACTION_SEND_REQUEST_HEADERS'] or identity(event['source']) != selected:
                continue
            need(len(witnesses) < 32, 'Send-header witness bound')
            params = event.get('params', {})
            values = line_values(params.get('headers'), HEADER)
            hosts = line_values(params.get('headers'), 'host')
            witnesses.append(dict(eventIndex=i, sourceId=selected[0], sourceTypeId=selected[1],
                line=params.get('line'), headerValues=values, hostValues=hosts,
                exact=(params.get('line') == 'POST /actions HTTP/1.1\r\n' and values == [expected] and
                       hosts == [urlsplit(origin).netloc])))
    passed = len(candidates) == len(witnesses) == 1 and witnesses[0]['exact'] is True
    return dict(exactPublicSendObserved=passed, candidateCount=len(candidates),
        candidates=[dict(sourceId=k[0], sourceTypeId=k[1], witnessEventIndexes=v) for k, v in candidates.items()],
        sendHeaderWitnesses=witnesses, sourceIdsDocumentLocalOnly=True,
        historyCompleteProved=False, missingOrRedactedOrEvictedEvidenceCanPreventJoin=True)


PHASES = {'request', 'web-handler', 'response-setup', 'response-outparam', 'response-read',
          'response-write', 'output-child-dispose', 'outgoing-body-finish'}
EVENTS = {'adapter': {'adapter-enter': '-', 'adapter-read-eof': 'response-read',
          'output-child-dispose-returned': 'output-child-dispose', 'outgoing-body-finish-returned': 'outgoing-body-finish',
          'adapter-catch': None, 'adapter-post-cleanup': 'post-cleanup', 'adapter-normal-return-site': 'return-site'},
          'classic': {'classic-enter': '-', 'response-finish': '-', 'response-close': '-'}}
FIELDS = {'marker', 'version', 'sequence', 'lane', 'token', 'method', 'path', 'event', 'phase',
          'readBytes', 'readChunks', 'flags', 'caughtType', 'corrState', 'corr', 'corrCount'}
LOGGER_FIELDS = {'marker', 'version', 'sequence', 'lane', 'token', 'method', 'path', 'event'}
CAUGHT = {'undefined', 'object', 'boolean', 'number', 'string', 'symbol', 'bigint', 'function', 'null'}


def markers(data):
    records, ordinary, malformed, foreign = [], 0, [], []
    lines = data.splitlines(keepends=True)
    need(len(lines) <= 65536, 'Finite raw stdout line count')
    for n, line in enumerate(lines, 1):
        if b'NEXT_GUEST_' not in line:
            ordinary += 1; continue
        try:
            need(line.endswith(b'\n') and len(line) <= 512 and all(32 <= x <= 126 for x in line[:-1]),
                 'Marker newline/ASCII/512-byte limit')
            v = parse(line)
            if v.get('marker') != MARKER:
                foreign.append(dict(line=n, marker=v.get('marker'))); continue
            need(type(v.get('version')) is int and v['version'] == 2 and
                 type(v.get('sequence')) is int and 1 <= v['sequence'] <= 256, 'Marker version/sequence')
            if v.get('lane') == 'logger':
                need(set(v) == LOGGER_FIELDS and v['token'] == 0 and type(v['token']) is int and
                     v['method'] == v['path'] == '-' and v['event'] in {'logger-error', 'logger-truncated'},
                     'Short logger schema')
            else:
                need(set(v) == FIELDS and v['lane'] in EVENTS and v['event'] in EVENTS[v['lane']], 'Known V2 schema/event')
                need(type(v['token']) is int and 1 <= v['token'] <= SAFE and
                     type(v['readBytes']) is int and 0 <= v['readBytes'] <= SAFE and
                     type(v['readChunks']) is int and 0 <= v['readChunks'] <= SAFE and
                     type(v['flags']) is int and 0 <= v['flags'] <= 7, 'Typed finite counters/flags')
                need((v['method'], v['path']) in {('GET', '/actions'), ('POST', '/actions'), ('GET', '/action-result')},
                     'Admitted route')
                phase = EVENTS[v['lane']][v['event']]
                need(v['phase'] in PHASES if phase is None else v['phase'] == phase, 'Event Source phase')
                need(v['caughtType'] in CAUGHT | {'-'}, 'Safe caught type')
                if v['event'] == 'adapter-catch':
                    need(v['caughtType'] in CAUGHT, 'Caught branch type')
                elif v['event'] == 'adapter-post-cleanup':
                    need(v['flags'] in (0, 1, 2) and ((v['caughtType'] in CAUGHT) == bool(v['flags'] & 1)), 'Post-cleanup flags')
                else:
                    need(v['caughtType'] == '-', 'No fabricated caught type')
                if v['lane'] == 'classic' or v['event'] == 'adapter-enter':
                    need(v['readBytes'] == v['readChunks'] == v['flags'] == 0, 'Enter/classic counters')
                need(type(v['corrCount']) is int and v['corrCount'] in (0, 1, 2) and
                     v['corrState'] in {'valid', 'missing', 'invalid', 'duplicate'}, 'Correlation state/count')
                if v['corrState'] == 'valid':
                    need(v['corrCount'] == 1 and type(v['corr']) is str and re.fullmatch('[0-9a-f]{64}', v['corr']), 'Validated correlation')
                else:
                    need(v['corr'] is None and (v['corrState'] != 'missing' or v['corrCount'] == 0) and
                         (v['corrState'] != 'duplicate' or v['corrCount'] == 2) and
                         (v['corrState'] != 'invalid' or v['corrCount'] in (0, 1)), 'Unjoined correlation')
            records.append(dict(line=n, record=v))
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            malformed.append(dict(line=n, reason=type(error).__name__ + ': ' + str(error)[:160]))
    logger = [r for r in records if r['record']['lane'] == 'logger']
    groups = Counter((r['record']['lane'], r['record']['token'], r['record']['method'], r['record']['path'])
                     for r in records if r['record']['event'].endswith('-enter'))
    return dict(records=records, ordinaryLines=ordinary, malformed=malformed, foreign=foreign,
        loggerFrames=logger, diagnosticLossObserved=bool(malformed or foreign or logger),
        repeatedDescriptiveEnterGroups=[dict(lane=k[0], token=k[1], method=k[2], path=k[3], count=v)
                                       for k, v in groups.items() if v > 1],
        mergedTokensOrSequencesAreNotGloballyUnique=True, completeObservationProved=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in [*PINNED, *DATA]:
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    raw, refs, paths, initial = inputs(args)
    obj = {k: parse(v) for k, v in raw.items() if k not in {'guest-entry', 'browser-source', 'client-source', 'native-stdout'}}
    for index, name, role in [('guest-index', 'guest-entry.mjs', 'guest-entry'), ('guest-index', 'marker-contract.json', 'contract'),
                               ('browser-index', 'browser-check.mjs', 'browser-source'), ('client-index', 'run-contracts.mjs', 'client-source')]:
        member(obj[index], name, refs[role])
    need(obj['contract']['marker'] == MARKER and obj['contract']['version'] == 2 and
         obj['contract']['reviewedProposal'] == refs['proposal'], 'Held proposal/record contract')
    plan, pair = obj['pair-plan'], obj['pair-result']
    need(plan['fixedOrder'] == ['native', 'stock'] and [t['arm'] for t in plan['trials']] == ['native', 'stock'] and
         pair['plannedOrder'] == ['native', 'stock'] and [t['arm'] for t in pair['trials']] == ['native', 'stock'] and
         len(plan['trials']) == len(pair['trials']) == 2 and
         plan['automaticRetry'] is plan['replacementTrials'] is plan['oldFailuresWaived'] is False and
         pair['automaticRetry'] is pair['replacementTrials'] is False, 'One fixed pair')
    review = obj['constructor-review']
    need(review['verifiedPassed'] is review['completeReturnedImportAuditVerified'] is True and
         review['state'] == 'COORDINATED_PUBLIC_REQUEST_CORRELATION_COMPONENT_INIT_DATA_REVIEW_PASSED_V1', 'Actual INIT prerequisite')
    native = obj['native-result']; cap = native['server']['stdoutCapture']
    need(cap['state'] == 'RAW_STDOUT_CAPTURE_FINALIZED_COMPLETE_V1' and cap['limitBytes'] == 8 * MIB and
         all(cap[k] is True for k in ['complete', 'pipeEof', 'fileClosed', 'fileBoundVerified', 'finalized']) and
         all(cap[k] is False for k in ['overflow', 'partialWritePossible', 'unretainedBytesUnknown']) and cap['errors'] == [] and
         cap['fileBytes'] == cap['completeWriteBytes'] == cap['lastReservedWriteCeiling'] == len(raw['native-stdout']), 'Complete raw stdout required BEFORE marker parsing')
    match(native['server']['stdout'], refs['native-stdout'], 'final native stdout')
    need(native['server']['exit'] == {'code': 0, 'signal': None, 'error': None} and
         native['client']['exit'] in [{'code': x, 'signal': None, 'error': None} for x in (0, 1)], 'Natural completed native processes')
    match(native['client']['result'], refs['native-client'], 'native client')
    arm_reports, all_nonces = {}, []
    for i, arm in enumerate(['native', 'stock']):
        t, published = plan['trials'][i], pair['trials'][i]
        a, result, terminal, b, m = (obj[arm + '-' + k] for k in ['authority', 'result', 'terminal', 'browser', 'manifest'])
        client = obj['native-client'] if arm == 'native' else result
        need(clean(terminal) and terminal['authority'] == refs[arm + '-authority'], 'Completed clean original owner: ' + arm)
        need(published['publication']['valid'] is True and published['runId'] == t['runId'], 'Final published outcome: ' + arm)
        match(published['publication']['terminal'], refs[arm + '-terminal'], arm + ' terminal')
        match(published['publication']['result'], refs[arm + '-result'], arm + ' result')
        match(result['rootAuthority'], refs[arm + '-authority'], arm + ' authority')
        match(a['sourceIndex'], refs[arm + '-index'], arm + ' actual actor')
        match(t['actorIndex'], refs[arm + '-index'], arm + ' planned actor')
        need(a['arm'] == arm and a['runId'] == t['runId'] and a['publicRequestCorrelation'] == t['publicRequestCorrelation'] and
             a['publicRequestCorrelationAllowed'] is True, 'Root selected public literals')
        if arm == 'native':
            match(a['constructionDataReview'], refs['constructor-review'], 'actual accepted constructor review')
            for key in ['component', 'componentAudit', 'engine', 'nativeMetadata', 'inputEntry', 'inputSourceIndex']:
                need(a[key] == native[key] if key in native else True, 'Native result role: ' + key)
                need(a[key] == review[key], 'INIT selected role: ' + key)
            match(a['inputEntry'], refs['guest-entry'], 'actual guest')
            match(a['inputSourceIndex'], refs['guest-index'], 'actual guest index')
            match(native['sourceIndex'], refs['native-index'], 'native runtime selector')
        manifest(m); match(result['publicRequestCorrelation']['manifest'], refs[arm + '-manifest'], arm + ' host manifest')
        need(result['publicRequestCorrelation']['value'] == m and client['browser'] == b and b['origin'] == client['origin'] == m['origin'] and
             m['runId'] == t['runId'] and {k: m[k] for k in ['headerName', 'nonceByTest']} == t['publicRequestCorrelation'], 'Manifest/run/origin/browser roles')
        correlation = b['publicRequestCorrelation']
        need(correlation['manifest'] == m and correlation['actualGuestJoin'] is None, 'Browser manifest and unclaimed join')
        match(correlation['manifestSource'], refs[arm + '-manifest'], arm + ' observed host manifest')
        match(correlation['retainedManifest'], refs[arm + '-retained-manifest'], arm + ' retained manifest')
        need(raw[arm + '-manifest'] == raw[arm + '-retained-manifest'], 'Browser copied exact manifest bytes')
        evidence = correlation['readEvidence']
        need(evidence['canonicalRegularNlinkOne'] is evidence['readBookendsStable'] is True and evidence['initial'] == evidence['final'], 'Browser manifest read bookends')
        if arm == 'native':
            cc = client['publicRequestCorrelation']
            need(cc['manifest'] == m and cc['sameBrowserManifestSourceObserved'] is True, 'Full client manifest selection')
            match(cc['manifestSource'], refs[arm + '-manifest'], 'Native client observed manifest')
        need(b['browserClosed'] is True and b['netlog']['completeJson'] is b['netlog']['fsynced'] is True and
             b['netlog']['errors'] == [], 'Finalized browser NetLog')
        match(b['netlog']['file'], refs[arm + '-netlog'], arm + ' NetLog')
        all_nonces.extend(m['nonceByTest'].values())
        nonce = m['nonceByTest']['server-action']; target = m['origin'] + '/actions'
        need(type(b['actionPosts']) is list and len(b['actionPosts']) <= 128, 'Finite actual POST observations')
        posts = [dict(index=n, url=x['url'], values=map_values(x['headers'], HEADER))
                 for n, x in enumerate(b['actionPosts']) if x['url'] == target]
        pw = len(posts) == 1 and posts[0]['values'] == [nonce]
        configured = [x for x in b['tests'] if x['id'] == 'server-action']
        need(len(configured) == 1 and configured[0]['publicCorrelationConfiguredNonce'] == nonce, 'Actual selected test nonce')
        net = netlog(obj[arm + '-netlog'], m['origin'], nonce)
        arm_reports[arm] = dict(runId=m['runId'], origin=m['origin'], serverActionNonce=nonce,
            playwright=dict(exactPublicPostObserved=pw, targetUrl=target, postCount=len(posts), observations=posts),
            netlog=net, browserPublicPostMetadataObserved=pw and net['exactPublicSendObserved'],
            originalPassed=result['passed'], browserStrictPassed=b['passed'],
            browserFunctionalPassed=b['functionalPassed'], guestJoinApplicable=arm == 'native',
            clientCounterNonceHasNoPostJoinClaim=True)
    need(len(all_nonces) == len(set(all_nonces)) == 4, 'No nonce reuse across this fixed pair')
    marker = markers(raw['native-stdout'])
    expected = arm_reports['native']['serverActionNonce']
    frames = marker['records']; selected = [x for x in frames if x['record'].get('corr') == expected and x['record'].get('corrState') == 'valid']
    post = [x for x in selected if x['record']['method'] == 'POST' and x['record']['path'] == '/actions']
    lanes = {}
    for lane in ['adapter', 'classic']:
        observed = [x for x in post if x['record']['lane'] == lane]
        enters = [x for x in observed if x['record']['event'] == lane + '-enter']
        lanes[lane] = dict(validMatchingPostEnterCount=len(enters), uniquePublicEnterObserved=len(enters) == 1,
            enterObservations=enters, eventCounts=dict(Counter(x['record']['event'] for x in observed)), records=observed,
            publicValueGroupingOnly=True, physicalTraceOrderOrIdentityProved=False)
    marker['selectedServerAction'] = dict(nonce=expected, lanes=lanes,
        matchingValueOtherRoutes=[x for x in selected if x not in post],
        otherPostEnterObservations=[x for x in frames if x['record'].get('method') == 'POST' and x['record'].get('path') == '/actions' and
                                    x['record']['event'].endswith('-enter') and x not in post],
        uninstrumentedOrOtherNoncePostDoesNotCountAsThisNonceReplay=True)
    joined = (arm_reports['native']['browserPublicPostMetadataObserved'] and not marker['diagnosticLossObserved'] and
              all(x['uniquePublicEnterObserved'] for x in lanes.values()))
    need(all(stamp(paths[k]) == v for k, v in initial.items()), 'Final all-input read bookends')
    report = dict(schemaVersion=1, state='PUBLIC_REQUEST_CORRELATION_DATA_ANALYSIS_V1', dataParseSucceeded=True,
        inputs=refs, arms=arm_reports, nativeMarkers=marker, observedPublicPostMetadataJoin=joined,
        joinScope='Exact public nonce and cardinality at browser POST, same-local NetLog send headers, adapter-enter and classic-enter only.',
        undetectableSpoofingOrReplayExcluded=False, missingObservationsAreUnobserved=True,
        loggerSilenceDoesNotProveLosslessObservation=True, forwardedGetIsNotPost=True,
        privateStoreOrResourceIdentityProved=False, crossLaneNumericIdentityProved=False,
        postToInnerGetCausalityProved=False, completionOrHostTcpEofProved=False, uniqueCauseProved=False,
        oldFailuresWaived=False, fullNextAccepted=False, productionPromotion=False,
        relationship='R authored guest/contract and analyzer, and reviewed browser/header design. C/B independently review original outcomes/protection/owners; this report does not replace those lanes.')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
