#!/usr/bin/env python3
"""Offline retained-DATA verification; no embedded original path is opened."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys

MANIFEST_SHA256 = 'b26cbdb1cfc62ffad88a042ee3aae1101cc6f7cede79d96ab52745ad2b4c9891'
MAX_PAYLOAD = 8 * 1024 * 1024
MAX_MANIFEST = 2 * 1024 * 1024
CASE_IDS = ['none', 'valid', 'missing', 'invalid', 'duplicate',
            'wrong-enum-string', 'wrong-enum-object', 'wrong-value-object',
            'wrong-arity', 'short', 'uppercase', 'newline', 'nonhex',
            'repeated-same', 'repeated-different', 'rope', 'after-observe-allocation']


def require(value, message):
    if not value:
        raise ValueError(message)


def pairs(rows):
    value = {}
    for k, v in rows:
        require(k not in value, 'Duplicate JSON key')
        value[k] = v
    return value


def loads(data):
    return json.loads(data, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return set(a) == set(b) and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def integer(v, low, high):
    return type(v) is int and low <= v <= high


class Copies:
    def __init__(self, root):
        self.root = root
        self.stamps = {}
        self.inodes = {}
        self.raw = {}
        self.rows = {}

    def path(self, relative):
        require(type(relative) is str, 'Copy path type')
        p = PurePosixPath(relative)
        require(not p.is_absolute() and p.parts and
                all(x not in ['', '.', '..'] for x in p.parts) and str(p) == relative,
                'Unsafe copy path')
        q = self.root.joinpath(*p.parts)
        require(q.resolve() == q and self.root in q.parents, 'Symlink or escaping copy')
        return q

    def stamp(self, q):
        s = q.lstat()
        require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1 and
                stat.S_IMODE(s.st_mode) in [0o644, 0o755], 'Portable regular single-link file')
        k = (s.st_dev, s.st_ino)
        require(k not in self.inodes or self.inodes[k] == str(q), 'Copy inode alias')
        self.inodes[k] = str(q)
        value = (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
                 s.st_mtime_ns, s.st_ctime_ns)
        require(str(q) not in self.stamps or self.stamps[str(q)] == value, 'File changed')
        self.stamps[str(q)] = value
        return value

    def read(self, relative, limit):
        q = self.path(relative)
        before = self.stamp(q)
        require(before[4] <= limit, 'Pre-read file byte fence')
        with q.open('rb') as f:
            opened = os.fstat(f.fileno())
            require((opened.st_dev, opened.st_ino, opened.st_size) == before[:2] + (before[4],),
                    'Opened copy identity')
            data = f.read(limit + 1)
            require(os.fstat(f.fileno()).st_size == before[4], 'Open-file size changed')
        require(len(data) == before[4] and self.stamp(q) == before, 'Read bookend')
        return data

    def ref(self, ref):
        require(type(ref) is dict and set(ref) == {'path', 'sha256', 'bytes'}, 'Ref schema')
        # The absolute historical path is a dictionary key only, never passed to Path/open.
        require(type(ref['path']) is str and ref['path'] in self.rows, 'Unretained original descriptor')
        row = self.rows[ref['path']]
        require(same(ref, row['original']), 'Original role descriptor mismatch')
        return self.raw[row['copy']['path']]

    def document(self, ref):
        return loads(self.ref(ref))

    def finish(self):
        for q, before in list(self.stamps.items()):
            require(self.stamp(Path(q)) == before, 'Final copy bookend')


def clean_owner(t):
    require(integer(t['rawExitCode'], 0, 0), 'Original owner raw zero')
    require(t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True and
            t['timeout'] is t['forcedCleanup'] is False, 'Original owner cleanup')
    require(all(t[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']),
            'Original owner errors/signals')
    require(all(g['alive'] is g['signalAllowed'] is False for g in t['finalGroups']), 'Final group remains')


def original_owner(c, original_root, expected_argv, cap, authority):
    def ref(name):
        return c.rows[original_root + '/' + name]['original']
    s = c.document(ref('started.json'))
    t = c.document(ref('terminal.json'))
    clean_owner(t)
    require(s['pid'] == t['pid'] and s['argv'] == expected_argv and
            s['timeoutSeconds'] == cap and s['authority'] == t['authority'] == authority,
            'Original owner start/terminal/authority/argv')
    rows = sorted((p, x) for p, x in c.rows.items()
                  if p.startswith(original_root + '/owned-') and p.endswith('.json'))
    records = [c.document(x['original']) for _, x in rows]
    require([x['sequence'] for x in records] == list(range(len(records))) and
            [x['process'] for x in records] == t['observedProcesses'], 'Exact owned records')
    require(len({x['pid'] for x in t['observedProcesses']}) == len(records), 'Duplicate owned PID')
    for key in ['stdout', 'stderr']:
        c.ref(t[key])
    return s, t, len(records)


def native_records(stdout, expected, case_id, native, fixture):
    require(stdout.isascii() and (not stdout or stdout.endswith(b'\n')), 'Complete ASCII stdout lines')
    records = []
    maximum = 0
    for line in stdout.splitlines(keepends=True):
        require(line.endswith(b'\n') and b'\r' not in line and len(line) <= 512 and
                all(32 <= b <= 126 for b in line[:-1]), 'Native ASCII/512-byte line')
        r = loads(line)
        require(type(r) is dict and set(r) == set(native['record']['fields']), 'Native record fields')
        require(r['marker'] == native['record']['marker'] and same(r['version'], 1) and
                r['event'] == native['record']['event'], 'Native version/event')
        require(r['status'] in native['record']['statuses'] and
                integer(r['observations'], 1, 2) and r['method'] in native['record']['method'] and
                r['path'] in native['record']['path'] and r['reason'] in native['record']['reasons'],
                'Native fixed-value grammar')
        if r['status'] == 'single-valid':
            require(same(r['corrCount'], 1) and type(r['corr']) is str and
                    re.fullmatch('[0-9a-f]{64}', r['corr']) is not None and r['reason'] == '-',
                    'Single valid fixed snapshot')
        else:
            require(r['corrCount'] is r['corr'] is None, 'Unavailable/ambiguous clears snapshot')
        records.append(r)
        maximum = max(maximum, len(line))
    require(len(records) == (1 if expected['required'] else 0), 'Case native cardinality')
    if not expected['required']:
        require(case_id == 'none' and stdout == b'', 'Bounded no-observation case')
        return records, maximum
    r = records[0]
    wanted = {k: v for k, v in expected.items() if k not in ['required', 'allowedRecords']}
    require(all(same(r.get(k), v) for k, v in wanted.items()), 'Exact native case contract')
    if 'allowedRecords' in expected:
        require(any(all(same(r.get(k), v) for k, v in x.items())
                    for x in expected['allowedRecords']), 'Declared rope alternatives only')
    # Literal observe arguments in indexed c06d and original controller Source; NOT GET metadata.
    route = ('POST', '/actions')
    if case_id in ['missing', 'duplicate']:
        route = ('GET', '/actions')
    elif case_id == 'invalid':
        route = ('GET', '/action-result')
    elif case_id in ['wrong-enum-string', 'wrong-enum-object', 'wrong-arity',
                     'repeated-same', 'repeated-different']:
        route = ('-', '-')
    require((r['method'], r['path']) == route, 'Source static argument route')
    if r['status'] == 'single-valid':
        require(r['corr'] == fixture['valid'], 'Copied fixture value')
    return records, maximum


def main():
    require(len(sys.argv) == 1, 'No path arguments; copies adjacent to this reader only')
    root = Path(__file__).absolute().parent
    require(root.resolve() == root, 'Canonical corpus directory')
    c = Copies(root)
    manifest_data = c.read('manifest.json', MAX_MANIFEST)
    require(hashlib.sha256(manifest_data).hexdigest() == MANIFEST_SHA256, 'Pinned manifest')
    m = loads(manifest_data)
    require(m['schemaVersion'] == 1 and m['state'] == 'RETAINED_NATIVE_EXPORT_DIAGNOSTIC_PROBE_RUNTIME_DATA_V1',
            'Manifest version/state')
    require(integer(m['payloadFiles'], 1, 2000) and integer(m['payloadBytes'], 0, MAX_PAYLOAD) and
            m['payloadLimitBytes'] == MAX_PAYLOAD and len(m['files']) == m['payloadFiles'], 'Corpus limits')
    # Validate EVERY declared size and aggregate before opening ANY payload.
    total = 0
    copy_paths = set()
    for row in m['files']:
        old, new = row['original'], row['copy']
        require(type(old) is type(new) is dict and set(old) == set(new) == {'path', 'sha256', 'bytes'},
                'Manifest descriptor schema')
        require(type(old['path']) is str and old['path'].startswith('/') and old['path'] not in c.rows,
                'Distinct historical absolute labels')
        require(type(new['path']) is str and new['path'].startswith('payload/') and new['path'] not in copy_paths,
                'Distinct copied payload path')
        c.path(new['path'])
        require(integer(old['bytes'], 0, MAX_PAYLOAD) and same(old['bytes'], new['bytes']) and
                type(old['sha256']) is str and re.fullmatch('[0-9a-f]{64}', old['sha256']) and
                old['sha256'] == new['sha256'], 'Per-row byte/hash fence')
        total += new['bytes']
        require(total <= MAX_PAYLOAD, 'Aggregate byte fence')
        copy_paths.add(new['path'])
        c.rows[old['path']] = row
    require(total == m['payloadBytes'], 'Declared aggregate bytes')
    expected_files = copy_paths | {'manifest.json', 'check.py', 'README.md'}
    before_members = {}
    for q in sorted(root.rglob('*')):
        require(not q.is_symlink() and q.resolve() == q, 'Namespace symlink')
        s = q.lstat()
        if stat.S_ISREG(s.st_mode):
            before_members[str(q.relative_to(root))] = ('file', s.st_dev, s.st_ino, s.st_mode)
        else:
            require(stat.S_ISDIR(s.st_mode) and stat.S_IMODE(s.st_mode) == 0o755, 'Portable directory')
            before_members[str(q.relative_to(root))] = ('directory', s.st_dev, s.st_ino, s.st_mode)
    require({k for k, v in before_members.items() if v[0] == 'file'} == expected_files, 'Closed file namespace')
    expected_dirs = {str(p) for x in expected_files for p in PurePosixPath(x).parents if str(p) != '.'}
    require({k for k, v in before_members.items() if v[0] == 'directory'} == expected_dirs, 'Closed directory namespace')
    c.read('check.py', 128 * 1024)
    c.read('README.md', 64 * 1024)
    for row in m['files']:
        v = row['copy']
        data = c.read(v['path'], v['bytes'])
        require(len(data) == v['bytes'] and hashlib.sha256(data).hexdigest() == v['sha256'], 'Copied byte hash')
        c.raw[v['path']] = data
    require(len(m['namespaces']) == 19, 'Whole work, outer and17 case namespaces')
    for n in m['namespaces']:
        prefix = n['originalRoot'] + '/'
        files = sorted(p[len(prefix):] for p in c.rows if p.startswith(prefix))
        require(files == n['files'], 'Complete original namespace retained as labels')
        dirs = sorted({str(p) for x in files for p in PurePosixPath(x).parents if str(p) != '.'})
        require(dirs == n['directories'], 'Original directory namespace documentary closure')
    for family in m['sourceFamilies']:
        index = c.document(family['index'])
        parent = family['index']['path'].rsplit('/', 1)[0]
        members = [dict(x, path=parent + '/' + x['path']) for x in index['files']]
        require(same(members, family['members']), 'Genuine indexed Source membership')
        for v in members:
            c.ref(v)  # Bytes only; Source is never evaluated/imported.
    role = m['roles']
    a = c.document(role['authority'])
    p = c.document(role['runtimePlan'])
    contract = c.document(role['caseContract'])
    native = c.document(role['nativeProtocol'])
    result = c.document(role['actualResult'])
    primary = c.document(role['primaryReview'])
    owner = c.document(role['ownerReview'])
    construction = c.document(role['constructionReview'])
    build = c.document(role['fullBuildReview'])
    require(primary['state'] == 'COORDINATED_NATIVE_EXPORT_DIAGNOSTIC_DIRECT_PROBE_RUNTIME_DATA_REVIEW_PASSED_V1' and
            primary['verifiedPassed'] is primary['verifiedPrimaryDataPassed'] is primary['directProbeRuntimeAccepted'] is True,
            'Held primary direct-probe-only verdict')
    require(owner['state'] == 'INDEPENDENT_NATIVE_EXPORT_DIAGNOSTIC_PROBE_RUNTIME_OWNER_CAPTURE_DATA_REVIEW_PASSED_V1' and
            owner['verifiedPassed'] is owner['verifiedOwnerAndCaptureDataPassed'] is True, 'Held owner verdict')
    require(primary['actualResult'] == owner['actualResult'] == role['actualResult'] and
            primary['rootAuthority'] == owner['rootAuthority'] == role['authority'] and
            primary['actualOwnerCaptureReview'] == role['ownerReview'], 'Final review joins')
    require(primary['acceptedConstructionReview'] == a['constructionDataReview'] == role['constructionReview'] and
            primary['fullBuildReview'] == a['fullNativeBuildReview'] == role['fullBuildReview'] and
            construction['verifiedPassed'] is construction['completeReturnedImportAuditVerified'] is build['verifiedPassed'] is True,
            'Retained accepted construction/build delegations')
    for key in ['component', 'engine', 'nativeMetadata']:
        require(primary[key] == owner[key] == construction[key] == a[key], 'Genuine artifact role without payload retarget')
    require(a['sourceIndex'] == role['runtimeSourceIndex'] == primary['actorSourceIndex'] and
            a['plan'] == role['runtimePlan'] == primary['actorPlan'] and a['controller'] == role['controller'] and
            p['caseContract'] == role['caseContract'] == primary['caseContract'] and
            contract['nativeProtocol'] == role['nativeProtocol'] == primary['nativeProtocol'], 'Exact selected Source roles')
    require(a['state'] == 'ROOT_NATIVE_EXPORT_DIAGNOSTIC_PROBE_RUNTIME_AUTHORIZED_V1' and
            a['unissued'] is False and a['perCaseCollectionAllowed'] is True, 'Historical actual authority')
    require(all(a[k] is False for k in ['nativeBuildAllowed', 'constructorAllowed', 'browserAllowed',
            'applicationMountAllowed', 'guestEnvironmentAllowed', 'outgoingHttpWorkloadSelected', 'automaticRetryAllowed']),
            'Bounded direct-probe permissions')
    require(p['sourceIndex'] is None and p['prospectiveArtifactBindingsPending'] is False and
            p['perCaseOwnerSeconds'] == 90 and p['outerOwnerSeconds'] == 1800 and p['stdoutLimitBytes'] == MAX_PAYLOAD and
            p['positiveMarkerWaitSeconds'] == 10 and p['httpSeconds'] == 20 and p['httpBodyBytes'] == 4096,
            'Original runtime limits and late own-index policy')
    require(a['caseIds'] == p['fixedCaseIds'] == CASE_IDS == [x['id'] for x in contract['cases']] and
            [x['caseId'] for x in result['cases']] == CASE_IDS, 'Fixed17 order/no retry')
    require(result['rootAuthority'] == role['authority'] and result['error'] is None and
            result['unattemptedCaseIds'] == [] and result['finalProtection'] == {'unchanged': True} and
            result['collectionCompleted'] is result['allCasesPassed'] is result['passed'] is True,
            'Actual complete collection')
    require(all(primary[k] is False for k in ['fullNextAccepted', 'runtimeAccepted', 'nodeParityProved',
            'productionProfilePromoted', 'privateIdentityProved', 'nativeExportOrHostCompletionProved',
            'causeProved', 'universalHarmlessnessProved', 'authorizesFutureAction']), 'No broadened acceptance')
    observation = c.document(role['actualRootObservation'])
    protection = c.document(role['rootProtection'])
    require(protection == observation['finalProtection'] ==
            {'unchanged': True, 'sourceAndNativeAndWorldReadmitted': True}, 'Actual final guard receipt')
    # Direct explicit joins; no helper/guard/Source function is called.
    require(observation['rootAuthority'] == role['authority'] and observation['workerResult'] == role['actualResult'] and
            observation['cleanOwner'] is observation['passed'] is True and observation['ownerError'] is None and
            observation['terminal'] == role['outerTerminal'] and primary['actualRootObservation'] == role['actualRootObservation'],
            'Outer observation/terminal/final result')
    outer_root = role['outerStarted']['path'].rsplit('/', 1)[0]
    worker_root = role['actualResult']['path'].rsplit('/', 1)[0]
    old_start = c.document(role['outerStarted'])
    # Python canonical binary is selected in the actual started argv; retain that exact vector.
    outer_argv = [old_start['argv'][0], '-I', '-B', role['controller']['path'], '--worker']
    require(old_start['argv'][0] == '/opt/homebrew/Cellar/python@3.11/3.11.10/Frameworks/Python.framework/Versions/3.11/bin/python3.11',
            'Pinned original outer Python')
    outer_s, outer_t, owned_count = original_owner(c, outer_root, outer_argv, 1800, role['authority'])
    require(owner['constructionWorldGuard'] == a['constructionWorldGuard'] == role['constructionWorldGuard'], 'Actual world role')
    world = c.document(role['constructionWorldGuard'])
    require(world['before'] == world['after'] and world['unchanged'] is world['nativeInputsPreserved'] is True and
            world['before']['sourceIndex'] == p['worldSourceIndex'] and world['before']['witFiles'] == 8 and
            len(p['selectedInterfaces']) == 13 and all(x.endswith('@0.2.10') for x in p['selectedInterfaces']),
            'Held whole-world delegation')
    audit = c.document(role['componentAudit'])
    require(audit['passed'] is True and audit['component'] == a['component'] and
            set(audit['emittedImports']) <= set(p['selectedInterfaces']) and
            audit['exports'] == ['wasi:http/incoming-handler@0.2.10'], 'Reviewed standard incoming-only world')
    host_pids, case_pids, records_all, summaries = [], [], [], []
    stdout_bytes = body_bytes = stderr_bytes = maximum_line = 0
    require(len(primary['cases']) == len(owner['cases']) == 17, 'Final review case cardinality')
    outer_processes = {x['pid']: x for x in outer_t['observedProcesses']}
    for i, case in enumerate(contract['cases']):
        cid = case['id']
        folder = worker_root + '/case-%02d-%s' % (i, cid)
        item = result['cases'][i]
        raw_ref = c.rows[folder + '/data/case-result.json']['original']
        raw = c.document(raw_ref)
        analysis_ref = c.rows[folder + '/analysis.json']['original']
        analysis = c.document(analysis_ref)
        require(same(item['analysis'], analysis) and item['ownerInvocationAttempted'] is item['cleanOwner'] is True and
                item['ownerError'] is None and analysis['rawResult'] == raw_ref, 'Actual per-case result/analysis')
        argv = [a['node']['path'], role['runtimeSourceIndex']['path'].rsplit('/', 1)[0] + '/run-case.mjs',
                '--authority', role['authority']['path'], '--case', str(i)]
        start, terminal, count = original_owner(c, folder, argv, 90, role['authority'])
        owned_count += count
        case_pids.append(start['pid'])
        require(item['terminal'] == c.rows[folder + '/terminal.json']['original'], 'Per-case terminal role')
        server = raw['server']
        require(raw['caseIndex'] == i and raw['caseId'] == cid and raw['rootAuthority'] == role['authority'] and
                raw['origin'] == a['origin'] and raw['errors'] == [] and raw['collectionCompleted'] is True and
                raw['semanticValidationInvoked'] is raw['storeIdentityProved'] is raw['nativeExportOrHostCompletionProved'] is False,
                'Raw per-case control result')
        expected_server_argv = [a['wasmtime']['path'], 'serve', '--no-logging-prefix', '--addr', a['origin'][7:],
                                '-S', 'cli=y,tcp=n,udp=n,allow-ip-name-lookup=n', '--max-instance-reuse-count', '128',
                                '--idle-instance-timeout', '60s', a['component']['path']]
        require(server['argv'] == expected_server_argv and server['freshProcess'] is True and server['spawnAttempts'] == 1 and
                server['shutdownRequested'] is server['sigintSent'] is True and server['forcedCleanup'] is False and
                server['shutdownReason'] == 'case-collected' and server['exit'] == {'code': 0, 'signal': None, 'error': None},
                'One fresh standard host/normal SIGINT zero')
        host_pids.append(server['pid'])
        node_rows = [x for x in terminal['observedProcesses'] if x['pid'] == start['pid']]
        host_rows = [x for x in terminal['observedProcesses'] if x['pid'] == server['pid']]
        require(len(node_rows) == len(host_rows) == 1 and node_rows[0]['ppid'] == outer_s['pid'] and
                node_rows[0]['pgid'] == host_rows[0]['pgid'] == start['pid'] and
                host_rows[0]['ppid'] == start['pid'] and host_rows[0]['command'] == a['wasmtime']['path'], 'Original child ownership')
        require(all(outer_processes[x['pid']] == x for x in terminal['observedProcesses']), 'Outer observed original case children')
        require(raw['readiness'] == {'exactListener': True, 'tcpConnectOnly': True, 'httpWarmupRequests': 0}, 'No HTTP warmup')
        capture = raw['stdoutCapture']
        require(capture['state'] == 'RAW_STDOUT_CAPTURE_FINALIZED_COMPLETE_V1' and capture['limitBytes'] == MAX_PAYLOAD and
                all(capture[k] is True for k in ['pipeEof', 'fileClosed', 'fileBoundVerified', 'finalized', 'complete']) and
                all(capture[k] is False for k in ['overflow', 'partialWritePossible', 'unretainedBytesUnknown']) and
                capture['errors'] == [] and capture['rejectedWholeChunkBytes'] is None, 'Final capture before semantic parse')
        stdout = c.ref(raw['stdout'])
        require(raw['stdout'] == analysis['stdout'] and capture['path'] == raw['stdout']['path'] and
                len(stdout) == capture['fileBytes'] == capture['completeWriteBytes'] == capture['lastReservedWriteCeiling'] <= MAX_PAYLOAD,
                'Final capture byte/hash ceiling')
        hist = c.rows[raw['stdout']['path']]['originalPhysical']
        require(all(capture['finalIdentity'][k] == hist['bytes' if k == 'size' else k]
                    for k in ['dev', 'ino', 'mode', 'nlink', 'size']) and
                all(capture['initialIdentity'][k] == capture['finalIdentity'][k]
                    for k in ['dev', 'ino', 'mode', 'nlink']) and capture['initialIdentity']['size'] == 0,
                'Historical original named-file identity (never copied inode identity)')
        require(raw['stderrFinalDigestDeferredToOriginalOwnerTerminal'] is True and
                raw['stderrPath'] == analysis['stderr']['path'], 'Stderr digest follows original terminal')
        stderr = c.ref(analysis['stderr'])
        h = raw['http']
        require(h['method'] == case['request']['method'] == 'GET' and h['path'] == case['request']['path'] and
                h['status'] == case['expectedHttpStatus'] == 200 and h['complete'] is True and h['error'] is None and
                h['overflow'] is h['unretainedTailUnknown'] is False and h['body'] == analysis['body'], 'HTTP capture contract')
        body_raw = c.ref(h['body'])
        require(len(body_raw) == h['bodyBytes'] <= 4096 and body_raw.isascii(), 'Bounded ASCII response')
        body = loads(body_raw)
        wanted_body = dict(contract['responseCommon'], case='/' + cid,
                           allocatedBytes=524288 if cid == 'after-observe-allocation' else 0,
                           constructedStringExpression=cid == 'rope')
        require(same(body, wanted_body) and same(body, analysis['response']), 'All typed response fixture fields')
        records, line_max = native_records(stdout, case['expectedNativeRecord'], cid, native, contract['fixedFixtureValues'])
        require(same(records, analysis['nativeRecords']) and analysis['passed'] is True and analysis['errors'] == [],
                'Independent semantics equal retained controller analysis')
        mpc = raw['markerPresenceControl']
        require(mpc['required'] is (i != 0) and mpc['observed'] is (i != 0) and
                mpc['deadlineReached'] is mpc['semanticInterpretation'] is False, 'Presence control only')
        if i == 0:
            require(mpc['noneQuietMilliseconds'] == 100, 'Bounded none quiet interval')
        cp, op = primary['cases'][i], owner['cases'][i]
        require(cp['caseIndex'] == i and cp['caseId'] == cid and cp['caseResult'] == raw_ref and
                cp['body'] == h['body'] and cp['stdout'] == raw['stdout'] and cp['stderr'] == analysis['stderr'] and
                same(cp['response'], body) and same(cp['nativeRecords'], records) and
                cp['ownerTerminal'] == item['terminal'] and cp['allContractFieldsMatched'] is cp['staticArgumentRouteMatched'] is True,
                'Primary case independent DATA joins')
        require(op['caseIndex'] == i and op['caseId'] == cid and op['rawCaseResult'] == raw_ref and
                op['controllerAnalysis'] == analysis_ref and same(op['server'], server) and
                same(op['stdoutCapture'], capture) and op['stdout'] == raw['stdout'] and op['finalStderr'] == analysis['stderr'],
                'Complementary original owner/capture case joins')
        records_all.extend(records)
        stdout_bytes += len(stdout)
        body_bytes += len(body_raw)
        stderr_bytes += len(stderr)
        maximum_line = max(maximum_line, line_max)
        summaries.append(dict(caseIndex=i, caseId=cid, nativeRecords=len(records),
                              nativeStatus=records[0]['status'] if records else None,
                              nativeReason=records[0]['reason'] if records else None,
                              httpStatus=h['status'], ownerRawExitCode=terminal['rawExitCode']))
    require(len(set(host_pids)) == len(set(case_pids)) == 17 and not set(host_pids) & set(case_pids), 'Fresh original PIDs')
    require(len(records_all) == primary['nativeRecordCount'] == 16 and
            stdout_bytes == primary['completeRawStdoutBytes'] == owner['summary']['stdoutRawBytes'] and
            body_bytes == primary['responseBodyBytes'] == owner['summary']['httpBodyBytes'] and
            stderr_bytes == owner['summary']['stderrRawBytes'] and maximum_line == primary['maximumNativeLineBytes'] and
            owned_count == owner['summary']['ownedRecords'], 'Derived aggregate boundaries')
    c.finish()
    after_members = {}
    for q in root.rglob('*'):
        require(not q.is_symlink() and q.resolve() == q, 'Final namespace symlink')
        s = q.lstat()
        kind = 'file' if stat.S_ISREG(s.st_mode) else 'directory'
        require(stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode), 'Final namespace node type')
        after_members[str(q.relative_to(root))] = (kind, s.st_dev, s.st_ino, s.st_mode)
    require(after_members == before_members, 'Final closed namespace bookend')
    print(json.dumps(dict(schemaVersion=1, state='RETAINED_NATIVE_EXPORT_DIAGNOSTIC_PROBE_RUNTIME_DATA_CHECK_PASSED_V1',
                         passed=True, payloadFiles=m['payloadFiles'], payloadBytes=total,
                         originalOwners=18, ownedRecords=owned_count, caseCount=17, nativeRecordCount=len(records_all),
                         stdoutBytes=stdout_bytes, stderrBytes=stderr_bytes, responseBodyBytes=body_bytes,
                         maximumNativeLineBytes=maximum_line, cases=summaries,
                         originalPathsOpened=False, sourceOrHelperEvaluated=False, targetsInvoked=False,
                         directProbeSampleChecked=True, fullNextAccepted=False, privateIdentityProved=False,
                         nativeExportOrHostCompletionProved=False, causeProved=False,
                         originalModesAndIdentitiesHistoricalOnly=True), indent=2))


if __name__ == '__main__':
    main()
