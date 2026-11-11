"""Check the fixed stock wasmCloud saved sample; no original paths/tools opened."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import stat
import sys

if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
    raise RuntimeError('Use Python -I -B without optimization before payload reads')

ROOT = Path(__file__).resolve().parent / 'raw-records'
INDEX_SHA = '2c2f6e6e98ca9623608f9e8f0a1d3d3cb4d97d5bed95d8b86eefca3653eecd28'
COMPONENT_SHA = '7c22799781975b7e9c09d9df294fb1c5e3f243bb1c596d733425f98cf805f779'
ENGINE_SHA = 'e3075c14ec903831fb43dd305fb9c21eeaeb99a0d0a71c052fbda3a914faa965'
META = {'executionKind', 'nodeVersion', 'execArgv', 'nodeOptionsPresent', 'guestExecuted',
        'boundaryMode', 'nativeBoundaryClaimRequiresExternalProof'}
IDS = ['readable-pull', 'readable-cancel', 'writable-write-close', 'writable-abort',
       'transform-write-flush', 'bind-throw-reject', 'snapshot-throw-reject', 'queue-microtask']
SELECTED = {'wasi:cli/environment@0.2.10', 'wasi:cli/stdout@0.2.10', 'wasi:cli/stderr@0.2.10',
    'wasi:clocks/monotonic-clock@0.2.10', 'wasi:clocks/wall-clock@0.2.10', 'wasi:random/random@0.2.10',
    'wasi:filesystem/types@0.2.10', 'wasi:filesystem/preopens@0.2.10', 'wasi:io/error@0.2.10',
    'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10', 'wasi:http/types@0.2.10', 'wasi:http/outgoing-handler@0.2.10'}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        assert key not in result, 'duplicate JSON key'
        result[key] = value
    return result


def parsed(b):
    return json.loads(b, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def stamp(p):
    s = p.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def local(name, cap):
    p = Path(name)
    assert not p.is_absolute() and '..' not in p.parts and p.as_posix() == name
    p = ROOT / p
    before = stamp(p)
    assert p.resolve(strict=True) == p and stat.S_ISREG(before[2]) and before[3] == 1 and before[4] <= cap
    with p.open('rb') as f:
        b = f.read(cap + 1)
    assert len(b) == before[4] and stamp(p) == before
    return b


def same(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def owned(t):
    assert type(t['rawExitCode']) is int and t['rawExitCode'] == 0
    assert t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True
    assert t['timeout'] is t['forcedCleanup'] is False
    assert t['errors'] == t['signals'] == t['interruptedSignals'] == t['remainingObservedPids'] == []


def context(report):
    assert report['schemaVersion'] == 1 and report['suite'] == 'PUBLIC_ALS_WEB_STREAM_CONTEXT_OBSERVATIONS_V1'
    assert report['passed'] is report['completedAllCases'] is True
    assert report['fullNextAccepted'] is report['nativeAsyncResourceTested'] is False
    assert report['expectationsFrozen'] is report['webStreamContextComparisonPerformed'] is False
    assert [r['id'] for r in report['records']] == IDS
    assert sum(len(r['checks']) for r in report['records']) == 95
    for r in report['records']:
        assert r['fulfilled'] is r['passed'] is True and r['primarySet'] is False
        assert type(r['events']) is list and all(c['passed'] is True for c in r['checks'])
        c = r['cleanup']
        assert c['knownComplete'] is True and c['pendingTasks'] == c['heldLocks'] == c['liveDeadlineTimers'] == 0 and c['errors'] == []


def main():
    assert len(sys.argv) == 1
    raw = local('index.json', 1024**2)
    assert len(raw) == 28522 and sha(raw) == INDEX_SHA
    index = parsed(raw); rows = index['files']
    assert index['state'] == 'CLONE_CANCEL_STOCK_WASMCLOUD_PASS_RECORDS_RETAINED_V2'
    assert (index['payloadFiles'], index['retainedBytes'], index['originalBytes']) == (59, 288118, 288118)
    assert len(rows) == 59 and sum(r['bytes'] for r in rows) == 288118
    assert sum(r['original']['bytes'] for r in rows) == 288118
    assert all(type(r['bytes']) is int and 0 <= r['bytes'] <= 1024**2 for r in rows)
    data = {}; refs = {}; names = set()
    for r in rows:
        assert r['path'] not in names and r['encoding'] == 'identity'
        names.add(r['path']); b = local(r['path'], r['bytes'])
        assert len(b) == r['bytes'] == r['original']['bytes'] and sha(b) == r['sha256'] == r['original']['sha256']
        data[r['path']] = b; refs[r['path']] = r['original']
    assert {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} == names | {'index.json'}
    assert not any(p.is_symlink() for p in ROOT.rglob('*'))
    def doc(name):
        return parsed(data[name])
    for label, pid, seconds in [('prepare-clone-wasmcloud-v2', None, None), ('clone-wasmcloud-runtime-v2', 80219, 300),
                                ('clone-compare-wasmcloud-v2', 80391, 30)]:
        prefix = 'commands/' + label + '/'
        t, s, q, c = [doc(prefix + n + '.json') for n in ('terminal', 'started', 'request', 'collection')]
        owned(t)
        assert s['pid'] == t['pid'] and s['argv'] == q['argv'] and s['timeoutSeconds'] == q['seconds']
        assert s['authority'] == t['authority'] == refs[prefix + 'request.json']
        assert c['terminal'] == refs[prefix + 'terminal.json'] and c['rawExitCode'] == 0
        assert t['stdout'] == refs[prefix + 'stdout.log'] and t['stderr'] == refs[prefix + 'stderr.log']
        if pid is not None:
            assert t['pid'] == pid and q['seconds'] == seconds
    rt = doc('runtime/result.json'); request = doc('review/runtime-request.json')
    assert rt['state'] == 'LIFECYCLE_WASMCLOUD_COLLECTION_CLEAN_UNREVIEWED_V2'
    assert rt['request'] == refs['review/runtime-request.json'] and request['state'] == 'ROOT_LIFECYCLE_WASMCLOUD_RUNTIME_REQUEST_V2'
    assert request['runtimeSource'] == refs['source/run-wasmcloud.py']
    assert rt['collectionClean'] is rt['allFourBodiesCollected'] is rt['inputsPreserved'] is rt['configVerifiedBeforeDev'] is True
    assert rt['errors'] == rt['secondaryErrors'] == rt['unattemptedRequests'] == []
    assert all(rt[k] is False for k in ('semanticComparisonPerformed', 'sameStoreIdentityProved', 'applicationMounted',
                                      'guestEnvironmentConfigured', 'outgoingHostsAllowed', 'fullNextAccepted'))
    assert rt['fixedRequests'] == ['/context', '/clone-cancel', '/clone-cancel-followups', '/context'] and rt['extraHttpRequests'] == 0
    assert rt['component'] == request['component'] == index['component']
    assert rt['component']['sha256'] == COMPONENT_SHA and rt['component']['bytes'] == 37268017
    assert rt['wash'] == request['wash'] and rt['wash']['sha256'] == '365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954'
    assert rt['wash']['bytes'] == 101947952 and rt['actualHost'] == 'stock-wasmCloud-2.11.0'
    assert [c['label'] for c in rt['commands']] == ['config-show', 'wash-dev']
    logs = []
    for cmd, pid, counts in zip(rt['commands'], [80224, 80227], [[1595, 0], [42, 2352]]):
        assert cmd['pid'] == pid and cmd['returncode'] == 0 and cmd['sameProcessGroup'] is True
        assert cmd['timeout'] is cmd['forcedCleanup'] is False and cmd['argv'][0] == rt['wash']['path']
        assert len(cmd['captures']) == 2
        for c, count in zip(cmd['captures'], counts):
            assert c['complete'] is c['pipeEof'] is c['fsynced'] is c['closed'] is True
            assert c['overflow'] is c['readerStillRunning'] is False and c['errors'] == []
            assert c['observedBytes'] == c['retainedBytes'] == c['file']['bytes'] == count
            name = 'runtime/' + c['path'].rsplit('/', 1)[1]
            assert c['file'] == refs[name]
            logs.append(name)
    assert rt['captures'] == rt['commands'][1]['captures'] and rt['server'] == rt['commands'][1]
    server = rt['server']
    assert server['shutdownRequested'] is server['sigintSent'] is True and server['forcedCleanup'] is False and server['returncode'] == 0
    assert server['shutdownReason'] == 'four-fixed-calls-collected'
    shown = doc('runtime/config-show.stdout.log')
    assert shown['success'] is True and shown['data'] == rt['effectiveConfiguration']
    cfg = doc('runtime/project/.wash/config.json'); eff = rt['effectiveConfiguration']
    assert cfg == rt['configured'] and doc('runtime/empty-user-config.json') == {}
    assert rt['configFiles'] == [refs['runtime/project/.wash/config.json'], refs['runtime/empty-user-config.json']]
    assert cfg['version'] == eff['version'] == '2.11.0' and eff['build'] == cfg['build']
    assert cfg['build'] == {'command': 'test -f "$WASH_COMPONENT_PATH"', 'component_path': rt['component']['path']}
    for key in ('address', 'command', 'component_path', 'service'):
        assert eff['dev'][key] == cfg['dev'][key]
    assert eff['dev']['service'] is False and eff['dev'].get('volumes', []) == []
    assert all(eff['dev'].get(k, []) == [] for k in ('components', 'plugins', 'host_plugins'))
    assert cfg['dev']['volumes'] == cfg['dev']['components'] == cfg['dev']['plugins'] == cfg['dev']['host_plugins'] == []
    assert all(eff['workload'][k] == cfg['workload'][k] == [] for k in ('allowedHosts', 'allowedIpNameLookups', 'allowedHostLoopbackPorts'))
    assert cfg['workload']['config'] == {} and eff['workload'].get('config', {}) == {}
    assert cfg['workload']['environment'] == {'config': {}} and eff['workload']['environment'] == {}
    assert cfg['wit']['skip_fetch'] is eff['wit']['skip_fetch'] is True
    lease = rt['portLease']; readiness = rt['readiness']
    assert lease['origin'] == request['selfOrigin'] == rt['origin']
    assert lease['heldThroughConfigInspection'] is lease['singleAttempt'] is lease['releasedImmediatelyBeforeSingleDevLaunch'] is True
    assert lease['fallbackAllowed'] is False and readiness['tcpReady'] is True and readiness['httpWarmupRequests'] == 0
    assert len(readiness['postRegistrationEvents']) == 1
    for event in readiness['postRegistrationEvents']:
        name = 'runtime/wash-dev.' + event['stream'] + '.log'
        assert data[name].decode().splitlines()[event['lineNumber'] - 1] == event['line']
        assert event['address'] == rt['origin'] and 'INFO listening for HTTP requests address=' + rt['origin'] in event['line']
    assert len(rt['responses']) == 4
    for n, (response, size, route) in enumerate(zip(rt['responses'], [17379, 3041, 4691, 17379], rt['fixedRequests']), 1):
        assert response['ordinal'] == n and response['method'] == 'GET' and response['route'] == route
        assert response['status'] == 200 and response['complete'] is response['connectionClosed'] is True
        assert response['overflow'] is False and response['transportError'] is None
        assert response['body'] == refs[f'runtime/response-{n}.body'] and len(data[f'runtime/response-{n}.body']) == size
        assert [v for k, v in response['headers'] if k.lower() == 'content-length'] == [str(size)]
        # Equality concerns captured HTTP entity JSON, never HTTP wire/host identity.
        assert data[f'runtime/response-{n}.body'] == data[f'wasmtime/response-{n}.body']
    construction = doc('construction/construction-review.json')
    assert construction['passed'] is True and construction['artifacts']['component'] == rt['component']
    assert construction['engine']['sha256'] == ENGINE_SHA
    assert rt['emittedImports'] == construction['emittedImports'] and len(rt['emittedImports']) == len(set(rt['emittedImports'])) == 13
    assert set(rt['emittedImports']) == SELECTED and rt['exports'] == construction['emittedExports'] == ['wasi:http/incoming-handler@0.2.10']
    t = doc('construction/wit/terminal.json'); s = doc('construction/wit/started.json'); owned(t)
    assert s['pid'] == t['pid'] and s['argv'][-3:] == ['component', 'wit', rt['component']['path']]
    assert t['stdout'] == refs['construction/wit/stdout.log'] and t['stderr'] == refs['construction/wit/stderr.log']
    world = re.match(r'package root:component;\n\nworld root \{\n([^{}]*)\}\n', data['construction/wit/stdout.log'].decode())
    assert world is not None
    assert re.findall(r'^  import ([a-z0-9:/@.-]+);$', world[1], re.M) == rt['emittedImports']
    assert re.findall(r'^  export ([a-z0-9:/@.-]+);$', world[1], re.M) == rt['exports']
    guest = [doc(f'runtime/response-{n}.body') for n in range(1, 5)]
    node = doc('node/context.json'); context(node)
    assert node['executionKind'] == 'node-reference' and node['nodeVersion'] == 'v22.14.0' and node['execArgv'] == []
    assert node['nodeOptionsPresent'] is node['guestExecuted'] is node['nativeBoundaryClaimRequiresExternalProof'] is False
    assert node['boundaryMode'] == 'public-only'
    for envelope in (guest[0], guest[3]):
        g = envelope['collection']; context(g)
        assert envelope['marker'] == 'PUBLIC_ALS_WEB_STREAM_COMPONENT_V1' and envelope['route'] == '/context'
        assert envelope['primarySet'] is envelope['fullNextAccepted'] is False and envelope['passed'] is True
        assert g['executionKind'] == 'component-guest' and g['guestExecuted'] is g['nativeBoundaryClaimRequiresExternalProof'] is True
        assert g['boundaryMode'] == 'native-boundaries' and not any(k in g for k in ('nodeVersion', 'execArgv', 'nodeOptionsPresent'))
        assert same({k: v for k, v in node.items() if k not in META}, {k: v for k, v in g.items() if k not in META})
        refusal = envelope['publicAsyncResourceRefusal']
        assert refusal['facadeInstalled'] is False and refusal['namedAndDefaultConstructorSame'] is refusal['passed'] is True
        assert [r['binding'] for r in refusal['records']] == ['named', 'default']
        for r in refusal['records']:
            assert r['passed'] is r['threw'] is r['errorIsError'] is True and r['constructorType'] == 'function'
            assert (r['code'], r['module'], r['operation'], r['profile']) == ('ERR_SM_NODE_UNSUPPORTED', 'node:async_hooks', 'AsyncResource', 'sm-node-22.14.0-m1.0')
    for envelope, filename, marker, route in [(guest[1], 'node/clone.json', 'RESPONSE_CLONE_CANCEL_COMPONENT_OBSERVATION_V1', '/clone-cancel'),
            (guest[2], 'node/followups.json', 'RESPONSE_CLONE_CANCEL_FOLLOWUP_COMPONENT_OBSERVATION_V1', '/clone-cancel-followups')]:
        reference = doc(filename)
        assert reference['nodeVersion'] == 'v22.14.0' and reference['captureCompleted'] is True and reference['timedOut'] is False
        assert envelope['marker'] == marker and envelope['route'] == route and envelope['collectionComplete'] is True
        assert envelope['primarySet'] is envelope['fullNextAccepted'] is envelope['taskCancellationProved'] is False
        assert envelope['collection']['collectionComplete'] is True and same(reference['observation'], envelope['collection'])
    clone = guest[1]['collection']; followups = guest[2]['collection']['cases']
    assert clone['sourceCancelCalls'] == 1 and clone['sourceCancelReasons'][0]['firstElementIsFirstObject'] is True
    assert clone['sourceCancelReasons'][0]['secondElementIsSecondObject'] is True
    assert clone['snapshots'][2]['first']['state'] == 'pending'
    assert all(clone['snapshots'][4][k]['state'] == 'pending' for k in ('first', 'second'))
    assert all(v['state'] == 'fulfilled' for v in clone['cancelOutcomes'].values()) and clone['sourceGateReleased'] is True
    assert [c['id'] for c in followups] == ['both-reject-false', 'both-reject-object', 'first-cancel-survivor-eof', 'first-cancel-survivor-source-error']
    for c in followups[:2]:
        assert c['sourceCancelCalls'] == 1 and c['sourceReasons'][0]['length'] == 2
        assert c['sourceReasons'][0]['firstElementIsFirstReason'] is c['sourceReasons'][0]['secondElementIsSecondReason'] is True
        assert all(c['snapshots'][1][k]['state'] == 'pending' for k in ('first', 'second'))
        assert all(c['outcomes'][k]['state'] == 'rejected' and c['outcomes'][k]['sameReason'] is True for k in ('first', 'second'))
    assert followups[0]['rejection'] == {'type': 'boolean', 'value': False}
    for c in followups[2:]:
        assert c['sourceCancelCalls'] == 0 and c['readerReleased'] is True and c['outcomes']['first'] == {'state': 'fulfilled', 'value': {'type': 'undefined'}}
    assert followups[2]['outcomes']['terminalRead']['value']['done'] is True
    assert followups[3]['outcomes']['terminalRead']['state'] == 'rejected' and followups[3]['outcomes']['terminalRead']['sameReason'] is True
    diff = doc('review/differential-result.json')
    assert diff['state'] == 'CLONE_CANCEL_COMPONENT_NODE_DIFFERENTIAL_V2' and diff['nodeVersion'] == 'v22.14.0' and diff['passed'] is True
    assert all(c['passed'] is True and c['comparison']['differingPaths'] == [] for c in diff['contexts'])
    assert diff['clone']['passed'] is diff['clone']['allSharedObservationFieldsMatch'] is True
    assert diff['followups']['passed'] is diff['followups']['allSharedObservationFieldsMatch'] is True
    expected_inputs = [refs[n] for n in ['node/context.json', 'node/clone.json', 'node/followups.json',
        'runtime/response-1.body', 'runtime/response-2.body', 'runtime/response-3.body', 'runtime/response-4.body']]
    assert sorted(diff['inputFiles'], key=lambda r: r['path']) == sorted(expected_inputs, key=lambda r: r['path'])
    assert all(diff[k] is False for k in ('actualNativeResourceRetirementProved', 'hostInstanceIdentityProved', 'fullNextAccepted', 'productionProfilePromoted'))
    assert all(index[k] is False for k in ('binariesRetained', 'sameStoreIdentityProved', 'resourceRetirementProved', 'fullNextAccepted', 'productionPromoted'))
    print(json.dumps(dict(savedStockLifecycleSamplePassed=True, files=59, storedBytes=288118,
        originalBytes=288118, contexts=2, checksEach=95, cloneTypedEqual=True, fourFollowupsTypedEqual=True,
        wasmtimeEntityBodiesIdentical=True, configuredVolumesEnvironmentOutgoingEmpty=True,
        originalOwnersClean=True, httpBodiesComplete=4, standardImports=13, originalPathsRead=False,
        helperOrToolInvoked=False, engineOrComponentBinaryVerified=False, sameStoreIdentityProved=False,
        nativeResourceRetirementProved=False, fullNextAccepted=False, productionPromoted=False), sort_keys=True))


if __name__ == '__main__':
    main()
