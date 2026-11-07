"""Portable DATA reader for one separately granted direct Node control."""
from pathlib import Path
from urllib.parse import urlsplit
import base64
import codecs
import gzip
import hashlib
import json

HERE = Path(__file__).absolute().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def contract(record, body, expected, previous):
    text = body.decode('utf8')
    assert record['status'] == expected['status']
    assert all(x in text for x in expected.get('includes', []))
    if 'location' in expected:
        assert record['headers']['location'] == expected['location']
    if 'json' in expected:
        value = json.loads(text)
        assert all(value[k] == v for k, v in expected['json'].items())
    for key, value in expected.get('responseHeaders', {}).items():
        assert record['headers'][key] == value
    for key, values in expected.get('responseHeaderIncludes', {}).items():
        assert all(v in record['headers'][key] for v in values)
    if expected.get('equalJsonTo'):
        assert body == previous[expected['equalJsonTo']]


def main():
    index = json.loads((HERE / 'index.json').read_text())
    assert {r['path'] for r in index['files']} == {
        str(p.relative_to(HERE)) for p in HERE.rglob('*')
        if p.is_file() and p != HERE / 'index.json'
    }
    for r in index['files']:
        b = (HERE / r['path']).read_bytes()
        assert sha(b) == r['sha256'] and len(b) == r['bytes']
    manifest = json.loads((HERE / 'evidence-index.json').read_text())
    z = (HERE / 'evidence.json.gz').read_bytes()
    assert sha(z) == manifest['bundle']['sha256'] and len(z) == manifest['bundle']['bytes']
    expanded = gzip.decompress(z)
    assert len(expanded) == manifest['expandedBytes'] < 15 * 1024**2
    blobs = {h: base64.b64decode(v, validate=True)
             for h, v in json.loads(expanded)['blobs'].items()}
    assert len(blobs) == manifest['uniqueBlobs']
    assert all(sha(b) == h for h, b in blobs.items())
    rows = {r['path']: r for r in manifest['files']}
    assert len(rows) == manifest['payloads'] == len(manifest['files']) == 143
    assert sum(r['bytes'] for r in rows.values()) == manifest['bytes']
    assert all(not n.startswith('/') and '..' not in Path(n).parts for n in rows)
    assert all(len(blobs[r['sha256']]) == r['bytes'] for r in rows.values())

    def raw(name):
        return blobs[rows[name]['sha256']]

    def read(name):
        return json.loads(raw(name))

    def ref(r):
        names = [n for n, v in rows.items() if v['origin'] == r['path']]
        assert names, r['path']
        assert all(rows[n]['sha256'] == r['sha256'] and rows[n]['bytes'] == r['bytes']
                   for n in names)
        return raw(names[0])

    result = read('actual/result.json')
    assert sha(raw('actual/result.json')) == '13b50c79f408cb5f43329d5efc6078b822d3b3311cd04eea856e515cba56be02'
    assert result['state'] == 'NEXT_DIRECT_STANDALONE_CONTROL_PASSED_UNREVIEWED_V1'
    assert result['passed'] is True and result['errors'] == []
    authority = read('root/direct-v2-first-authority.json')
    source = 'sources/direct-standalone-control-candidate-v2/'
    plan = read(source + 'plan.json')
    assert ref(result['rootAuthority']) == raw('root/direct-v2-first-authority.json')
    assert ref(result['sourceIndex']) == raw(source + 'index.json')
    assert ref(result['plan']) == raw(source + 'plan.json')
    assert authority['sourceIndex'] == result['sourceIndex'] and authority['plan'] == result['plan']
    assert authority['runId'] == result['runId'] == 'engine462-direct-standalone-first'
    assert authority['unissued'] is False
    assert all(authority[k] is True for k in [
        'hostOnlyDirectStandaloneAllowed', 'localhostServeAllowed', 'browserAllowed'])
    assert all(authority[k] is False for k in [
        'compilerAllowed', 'nativeBuildAllowed', 'engineAllowed', 'guestAllowed',
        'componentConstructionAllowed', 'packageInstallAllowed', 'applicationSourceMutationAllowed',
        'externalDeploymentAllowed', 'adoptionAllowed'])
    assert not any(k in authority for k in ['argv', 'outputRoot', 'monitorOutputRoot', 'environment'])

    for family in {n.split('/')[1] for n in rows if n.startswith('sources/')}:
        prefix = 'sources/' + family + '/'
        j = read(prefix + 'index.json')
        assert {n.removeprefix(prefix) for n in rows if n.startswith(prefix)} == {
            'index.json', *[r['path'] for r in j['files']]}
        for r in j['files']:
            assert sha(raw(prefix + r['path'])) == r['sha256']
            assert len(raw(prefix + r['path'])) == r['bytes']

    terminal = read('monitor/terminal.json')
    started = read('monitor/started.json')
    observation = read('monitor/observation.json')
    assert type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0
    assert terminal['timeout'] is terminal['forcedCleanup'] is False
    assert terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    assert all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    assert all(g['alive'] is False for g in terminal['finalGroups'])
    assert started['authority'] == terminal['authority'] == result['rootAuthority']
    assert started['pid'] == terminal['pid']
    assert started['timeoutSeconds'] == plan['outerSeconds'] == 600
    actor_root = str(Path(result['sourceIndex']['path']).parent)
    assert started['argv'] == [plan['node']['path'], actor_root + '/control.mjs', result['rootAuthority']['path']]
    assert ref(terminal['stdout']) == raw('monitor/stdout.log')
    assert ref(terminal['stderr']) == raw('monitor/stderr.log') == b''
    owned = [read(n) for n in rows if n.startswith('monitor/owned-')]
    assert len(owned) == 16 and sorted(x['sequence'] for x in owned) == list(range(16))
    assert {json.dumps(x['process'], sort_keys=True) for x in owned} == {
        json.dumps(x, sort_keys=True) for x in terminal['observedProcesses']}
    assert observation['rawExitCode'] == 0 and observation['passed'] is True
    assert observation['ownedGroupsClean'] is observation['protectedInputsPreserved'] is True
    assert observation['error'] is None and observation['guestExecuted'] is observation['adoption'] is False
    assert ref(observation['terminal']) == raw('monitor/terminal.json')
    assert ref(observation['result']) == raw('actual/result.json')
    cli = [json.loads(line) for line in raw('root/first-cli.stdout.log').splitlines()]
    assert cli == [dict(pid=started['pid'], timeoutSeconds=600), observation]
    assert raw('root/first-cli.stderr.log') == b''
    assert observation['freeBytesAtAdmission'] == 1286488064 >= plan['minimumLaunchFreeBytes'] == 1073741824
    assert observation['continuousDiskGuardClaimed'] is False

    output = result['outputRoot']
    assert output == plan['outputPrefix'] + '-' + result['runId']
    origin = result['portLease']['origin']
    u = urlsplit(origin)
    assert u.scheme == 'http' and u.hostname == '127.0.0.1' and u.port == result['portLease']['port']
    assert result['portLease']['singleAttempt'] is result['portLease']['releasedBeforeSingleSpawn'] is True
    assert result['portLease']['fallbackAllowed'] is False
    server = result['server']
    assert server['argv'] == [plan['node']['path'], output + '/app/server.js']
    assert server['cwd'] == output + '/app'
    env = server['environment']
    assert set(env) == {'HOME', 'USER', 'LOGNAME', 'PATH', 'LANG', 'LC_ALL', 'CI',
                        'PORT', 'HOSTNAME', 'NODE_ENV', 'NEXT_TELEMETRY_DISABLED', 'TMPDIR'}
    assert env['PORT'] == str(u.port) and env['HOSTNAME'] == '127.0.0.1'
    assert env['NODE_ENV'] == 'production' and env['TMPDIR'] == output + '/tmp'
    assert not any(k in env for k in ['NODE_OPTIONS', 'NODE_PATH', 'NEXT_MANUAL_SIG_HANDLE', 'NODE_CHANNEL_FD'])
    assert server['shutdownRequested'] is server['sigintSent'] is True
    assert server['forcedCleanup'] is False and server['expectedSignalExit'] == 130
    assert server['exit'] == dict(code=130, signal=None, error=None)
    assert server['pid'] in {x['pid'] for x in terminal['observedProcesses']}
    assert server['stdout'] and ref(server['stdout']) == raw('actual/server.stdout.log')
    assert ref(server['stderr']) == raw('actual/server.stderr.log') == b''
    server_lines = raw('actual/server.stdout.log').decode().splitlines()
    assert result['readiness'] == dict(
        exactListenerEvents=[dict(stream='stdout', line=next(x for x in server_lines if x.strip().startswith('- Local:')), origin=origin)],
        tcpConnect=True, extraHttpRequests=0, applicationHandlersInitializedObserved=False,
        sourceRequestWaitsForHandlersPromise=True, readyLogIsNotHandlerCompletion=True)
    assert origin in result['readiness']['exactListenerEvents'][0]['line']
    assert result['client']['argv'] == [plan['node']['path'], actor_root + '/run-contracts.mjs',
        origin, output + '/client', plan['browserTools'], result['runId']]
    assert result['client']['environment'] == env and result['client']['cwd'] == output
    assert result['client']['exit'] == dict(code=0, signal=None, error=None)
    assert ref(result['client']['stdout']) == raw('actual/client.stdout.log')
    assert ref(result['client']['stderr']) == raw('actual/client.stderr.log') == b''
    assert result['client']['pid'] in {x['pid'] for x in terminal['observedProcesses']}
    parent_frame = json.loads(raw('monitor/stdout.log'))
    assert parent_frame == dict(state=result['state'], passed=True, serverExit=server['exit'], errors=[])
    assert all(result[k] is True for k in ['contractsPassed', 'copyInitiallyVerified', 'originalInputsPreserved', 'ownedFinalInventoryRecorded'])
    assert all(result[k] is False for k in ['guestExecuted', 'engineExecuted', 'moduleProviderOrHttpBridgeUsed', 'applicationSourceModified', 'adoption'])

    client = read('actual/client/result.json')
    assert ref(result['client']['result']) == raw('actual/client/result.json')
    assert client['origin'] == origin and client['passed'] is True
    assert client['errors'] == client['transportErrors'] == []
    spec = read('inputs/fixture-contract.json')
    requests = {r['id']: r for r in spec['requests']}
    assert len(requests) == 23
    assert [r['id'] for r in client['http']] == [*requests, 'server-action-submit']
    previous = {}
    for r in client['http']:
        assert r['passed'] is True
        b = raw('actual/client/responses/' + r['id'] + '.txt')
        assert sha(b) == r['bodySha256'] and len(b) == r['bodyBytes']
        if r['id'] in requests:
            contract(r, b, requests[r['id']], previous)
        else:
            assert r['status'] == 303 and r['headers']['location'] == '/action-result?value=fixture-action'
        previous[r['id']] = b
    assert client['cacheInvalidation']['passed'] is True
    assert client['cacheInvalidation']['before']['generation'] == 1
    assert client['cacheInvalidation']['after']['generation'] == 2
    chunks = read('actual/client/stream-chunks.json')
    decoder = codecs.getincrementaldecoder('utf8')()
    text = ''
    shell = ready = -1
    for i, c in enumerate(chunks):
        b = base64.b64decode(c['base64'], validate=True)
        assert len(b) == c['bytes']
        text += decoder.decode(b)
        if shell < 0 and 'NEXT_STREAM_SHELL' in text:
            shell = i
        if ready < 0 and 'NEXT_STREAM_READY' in text:
            ready = i
    text += decoder.decode(b'', final=True)
    assert len(chunks) == 5 and shell == 0 and ready == 2
    assert client['streaming'] == dict(chunks=5, shellChunk=0, readyChunk=2, complete=True, incrementalDeliveryObserved=True)

    browser = read('actual/client/browser/result.json')
    assert browser == client['browser'] and browser['origin'] == origin
    assert all(browser[k] is True for k in ['passed', 'functionalPassed', 'browserErrorFree', 'browserClosed', 'assetCapturePassed'])
    assert all(browser[k] == [] for k in ['errors', 'failedrequests', 'pageerrors', 'consoleerrors'])
    assert client['browserExit'] == dict(code=0, signal=None)
    assert client['browserArgv'] == [plan['node']['path'], plan['browserWorker']['path'], '--origin', origin,
        '--tools', plan['browserTools'], '--output', output + '/client/browser']
    assert ref(plan['browserWorker']) == raw('sources/browser-hydration-candidate-v3/browser-check.mjs')
    assert browser['perTestTimeoutMs'] == 20000
    assert browser['responseCaptureDrainBeforeCloseLimitMs'] == 500 and browser['responseFinishedDrainAfterCloseLimitMs'] == 2000
    assert len(browser['tests']) == 2
    for test in browser['tests']:
        assert test['passed'] is True and test['timedOut'] is False and test['error'] is None
        assert test['captureDrainBeforeCloseComplete'] is True and test['cdpObserver']['stopped'] is False
        assert test['cdpEnabledBeforeFirstAppRequest'] is True
        assert ref(test['screenshot']).startswith(b'\x89PNG\r\n\x1a\n')
    assert len(browser['assetBodies']) == 9 and len(browser['bodyCaptures']) == 10
    assets = {}
    for asset in browser['assetBodies']:
        assert asset['sourceMatch'] is True and asset['status'] == 200
        b = ref(asset['decodedBody'])
        assert sha(b) == asset['decodedSha256'] and len(b) == asset['decodedBytes']
        assets[(asset['test'], urlsplit(asset['url']).path)] = (sha(b), len(b))
    pins = read('sources/browser-hydration-candidate-v3/asset-pins.json')['assets']
    assert len(pins) == 5
    assert all(assets[('client-counter', p['path'])] == (p['sha256'], p['bytes']) for p in pins)
    for capture in browser['bodyCaptures']:
        b = ref(capture['decodedBody'])
        assert len(b) == capture['decodedBytes'] and sha(b) == capture['decodedSha256']
        assert capture['bodyCompletion']['kind'] == capture['sizesCompletion']['kind'] == 'fulfilled'
    post = next(x for x in browser['bodyCaptures'] if x['method'] == 'POST')
    assert len(ref(post['decodedBody'])) == 2963
    assert all(x['completion'] == 'fulfilled' and x['error'] is None for x in browser['responseFinishedObservations'])
    assert len(browser['cdpEvents']) == 83 == sum(t['cdpObserver']['events'] for t in browser['tests'])
    assert all(x['identityProved'] is False for x in browser['cdpCorrelations'])
    events = [x for x in browser['cdpEvents'] if x['test'] == 'server-action']
    request = next(x for x in events if x['event'] == 'Network.requestWillBeSent' and x['payload']['request']['method'] == 'POST')
    transport = [x for x in events if x['payload'].get('requestId') == request['payload']['requestId']]
    assert not any(x['event'] == 'Network.loadingFailed' for x in transport)
    assert len([x for x in transport if x['event'] == 'Network.loadingFinished']) == 1
    assert sum(x['payload']['dataLength'] for x in transport if x['event'] == 'Network.dataReceived') == 2963

    inputs = read('inputs/application-inputs.json')
    build = read('inputs/result.json')
    assert ref(plan['applicationInputs']) == raw('inputs/application-inputs.json')
    assert ref(plan['applicationBuildResult']) == raw('inputs/result.json')
    assert inputs == build['applicationInventory'] and build['applicationInventoryDescriptor'] == plan['applicationInputs']
    assert build['passed'] is build['originalInputsPreserved'] is True and build['errors'] == []
    assert build['actualBuildId'] == 'c2R8ovhEoFinJh6IvlO5M'
    assert inputs['regularFiles'] == len(inputs['files']) == 2181
    assert inputs['bytes'] == sum(r['bytes'] for r in inputs['files']) == 48714867
    assert len(inputs['directories']) == 425 and inputs['symlinks'] == []
    assert result['sourceRootIdentity'] == plan['applicationRootIdentity']
    assert result['applicationCopy'] == dict(files=2181, bytes=48714867, directoriesIncludingRoot=426,
        independentRootAndFileInodes=True, modesEqual=True, copyFlag='COPYFILE_FICLONE', reflinkActuallyUsed=None,
        initialMembershipExact=True, finalWholeCopyImmutabilityClaimed=False)
    assert browser['actionPosts'][0]['headers']['next-action'] in build['actualActionIds']['node']
    final = read('actual/owned-app-final-inventory.json')
    assert ref(result['ownedFinalInventory']) == raw('actual/owned-app-final-inventory.json')
    assert final['sourceModesRetainedInitially'] is True and final['wholeCopyImmutable'] is False
    assert len(final['files']) == 2218 and len(final['directories']) == 455
    filemap = {r['relativePath']: r for r in final['files']}
    assert len(filemap) == 2218 and len(set(final['directories'])) == 455
    for r in inputs['files']:
        t = filemap[r['path']]
        assert all(r[k] == t[k] for k in ['sha256', 'bytes', 'mode'])
        assert t['path'] == output + '/app/' + r['path'] and t['nlink'] == 1
        assert (t['dev'], t['ino']) != (r['dev'], r['ino'])
    expected_dirs = {'.', *[r['path'] for r in inputs['directories']]}
    extras = set(filemap) - {r['path'] for r in inputs['files']}
    extra_dirs = set(final['directories']) - expected_dirs
    assert len(extras) == 37 and len(extra_dirs) == 29
    assert all(n.startswith(('.next/cache/', '.next/server/route-cache/')) for n in extras)
    protected = {r['path']: r for r in plan['protectedInputs']}
    for relative in ['server.js', 'node_modules/next/dist/server/lib/start-server.js']:
        t = filemap[relative]
        r = protected[plan['applicationSource'] + '/' + relative]
        assert (t['sha256'], t['bytes']) == (r['sha256'], r['bytes'])
    audit = json.loads((HERE / 'current-copy-audit.json').read_text())
    assert audit['sourceRoot'] == result['sourceRootIdentity']
    assert audit['sourceFiles'] == 2181 and audit['sourceDirectoriesIncludingRoot'] == 426
    assert audit['ownedFinalFiles'] == 2218 and audit['ownedFinalDirectoriesIncludingRoot'] == 455
    assert set(audit['ownedExtraFiles']) == extras and set(audit['ownedExtraDirectories']) == extra_dirs
    assert audit['sourceListedIdentityModeMembershipAndBytesUnchanged'] is audit['ownedCurrentAllRecordedHashesModesAndIdentitiesMatch'] is True
    assert audit['ownedSourceListedFilesBytesAndModesUnchanged'] is audit['ownedSourceListedFilesIndependentInodes'] is True
    assert audit['wholeOwnedCopyImmutable'] is False and audit['actorsOrRetriesInvokedByCurator'] is False
    assert audit['protectedInputDescriptorsRehashed'] == plan['protectedInputs']

    negative = read('prior-cohort/review.json')
    assert negative['strictCohortGatePassed'] is False and negative['failedMembers'] == ['p3-stock']
    assert negative['rawCodes'] == [0, 0, 0, 0, 1, 0] and negative['plannedDenominator'] == 6
    review = json.loads((HERE / 'review.json').read_text())
    assert review['dataValidated'] is review['actualControlPassed'] is True
    assert review['sampleCount'] == 1 and review['oldCohortStrictGateRemainsFalse'] is True
    assert review['comparisonIsNewSeparateSampleNotReplacementOrRetry'] is True
    assert review['abortCauseExplained'] is review['generalReliabilityOrPromotionClaimed'] is review['adoption'] is False
    assert review['curatorExecutedActorsOrRetry'] is review['guestExecuted'] is review['engineExecuted'] is False
    originals = json.loads((HERE / 'final-originals-check.json').read_text())
    assert originals['logicalRowsRehashed'] == 143 and originals['allCapturedOriginalBytesAndHashesUnchanged'] is True
    assert originals['actorsOrRetriesExecuted'] is False
    print(json.dumps(dict(dataValidated=True, actualControlPassed=True, sampleCount=1,
        httpPassed=24, browserFunctionalPassed=2, strictBrowserPassed=True, cacheGeneration=[1, 2],
        streamChunks=5, shellChunkIndex=0, readyChunkIndex=2, cdpEvents=83,
        controllerRawExitCode=0, plannedServerSigintExitCode=130, ownedGroupsClean=True,
        retainedPayloads=143, oldCohortStrictGateRemainsFalse=True, failedCohortMember='p3-stock',
        replacementRetryOrCauseClaimed=False, guestOrEngineExecuted=False,
        curatorActorOrRetryExecuted=False, privateOriginalsRequired=False, adoption=False)))


if __name__ == '__main__':
    main()
