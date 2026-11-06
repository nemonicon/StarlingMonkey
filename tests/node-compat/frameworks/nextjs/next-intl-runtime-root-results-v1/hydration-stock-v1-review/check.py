"""Read-only portable DATA checker. Never starts Node, a server or a guest."""
from pathlib import Path
import base64
import codecs
import hashlib
import json
import re
import struct
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    data = Path(path).read_bytes()
    return dict(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def family(root):
    rows = read(root / 'index.json')['files']
    assert len(rows) == len({r['path'] for r in rows})
    actual = set()
    for path in root.rglob('*'):
        assert not path.is_symlink()
        if path.is_file() and path != root / 'index.json':
            actual.add(path.relative_to(root).as_posix())
    assert actual == {r['path'] for r in rows}
    for row in rows:
        relative = Path(row['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        assert digest(root / relative) == {k: row[k] for k in ('sha256', 'bytes')}
    return len(rows), sum(r['bytes'] for r in rows)


def main():
    assert __debug__
    members, payload_bytes = family(HERE)
    portable = read(HERE / 'portable-files.json')
    refs = {}
    for row in portable['files']:
        original, copy = row['original'], row['copy']
        assert digest(HERE / copy['path']) == {k: original[k] for k in ('sha256', 'bytes')}
        assert {k: copy[k] for k in ('sha256', 'bytes')} == {k: original[k] for k in ('sha256', 'bytes')}
        refs.setdefault(original['path'], []).append(row)

    def checked(ref):
        rows = refs[ref['path']]
        assert all(row['original'] == ref for row in rows)
        return HERE / rows[0]['copy']['path']

    for name in ['control', 'browser']:
        family(HERE / 'source' / name)
    authority = read(HERE / 'root-authority.json')
    assert authority['state'] == 'ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1'
    assert authority['arm'] == 'stock'
    assert authority['localhostServerAllowed'] is authority['browserAllowed'] is True
    for key in ['compilerAllowed', 'nativeBuildAllowed', 'guestAllowed', 'engineAllowed', 'externalApplicationDeploymentAllowed']:
        assert authority[key] is False
    assert checked(authority['sourceIndex']) == HERE / 'source/control/index.json'
    assert checked(authority['plans']) == HERE / 'source/control/plans.json'
    plan = read(checked(authority['plans']))
    result = read(HERE / 'actual/result.json')
    browser = read(HERE / 'actual/browser/result.json')
    terminal = read(HERE / 'monitor/terminal.json')
    observation = read(HERE / 'monitor/observation.json')
    started = read(HERE / 'monitor/started.json')
    assert terminal['rawExitCode'] == observation['rawExitCode'] == 0
    assert terminal['timeout'] is terminal['forcedCleanup'] is False
    assert terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
        assert terminal[key] == []
    assert checked(terminal['authority']) == HERE / 'root-authority.json'
    assert started['authority'] == terminal['authority']
    assert started['pid'] == terminal['pid'] and started['timeoutSeconds'] == 300
    assert started['argv'] == plan['arms']['stock']['argv']
    assert checked(terminal['stdout']) == HERE / 'monitor/stdout.log'
    assert checked(terminal['stderr']) == HERE / 'monitor/stderr.log'
    assert (HERE / 'monitor/stderr.log').read_bytes() == b''
    assert checked(observation['terminal']) == HERE / 'monitor/terminal.json'
    assert checked(observation['result']) == HERE / 'actual/result.json'
    assert observation['ownedGroupsClean'] is observation['protectedInputsPreserved'] is observation['hostExperimentPassed'] is True
    stdout_lines = (HERE / 'monitor/stdout.log').read_text().splitlines()
    json_frames = [json.loads(x) for x in stdout_lines if x.startswith('{')]
    assert len(json_frames) == 2
    assert json_frames[0]['passed'] is json_frames[0]['functionalPassed'] is json_frames[0]['browserErrorFree'] is True
    assert json_frames[1]['state'] == 'FULL_NEXT_HOST_MESSAGE_BRIDGE_PASSED'
    assert json_frames[1]['http'] == json_frames[1]['passedHttp'] == 24
    assert result['node'] == 'v22.14.0' and result['installed'] == {'next': '16.4.5', 'react': '19.3.1', 'react-dom': '19.3.1'}
    assert result['guestExecuted'] is result['applicationModified'] is False
    assert result['prepared'] is result['passed'] is result['originalApplicationInputsPreserved'] is True
    assert result['errors'] == result['transportErrors'] == []
    assert result['browser'] == browser
    assert digest(checked(result['harness'])) == digest(HERE / 'source/control/run-stock.mjs')
    app = result['applicationCopy']
    assert app['files'] == 2218 and app['bytes'] == 48808299
    assert app['byteIdentical'] is app['independentInodes'] is app['modesEqual'] is True
    assert app['copyFlag'] == 'COPYFILE_FICLONE' and app['reflinkActuallyUsed'] is None
    contract = read(HERE / 'fixture-contract.json')
    assert len(result['http']) == len(contract['requests']) + 1 == 24
    bodies = {}
    for spec, actual in zip(contract['requests'], result['http'][:-1]):
        assert actual['id'] == spec['id'] and actual['status'] == spec['status']
        path = HERE / 'actual/responses' / (spec['id'] + '.txt')
        assert digest(path) == {'sha256': actual['bodySha256'], 'bytes': actual['bodyBytes']}
        body = path.read_text()
        bodies[spec['id']] = body
        for marker in spec.get('includes', []):
            assert marker in body
        if 'location' in spec:
            assert actual['headers']['location'] == spec['location']
        if 'json' in spec:
            value = json.loads(body)
            assert all(value.get(k) == v for k, v in spec['json'].items())
        for key, value in spec.get('responseHeaders', {}).items():
            assert actual['headers'].get(key) == value
        for key, values in spec.get('responseHeaderIncludes', {}).items():
            assert all(v in actual['headers'].get(key, '') for v in values)
        if 'equalJsonTo' in spec:
            assert body == bodies[spec['equalJsonTo']]
        assert actual['passed'] is True and actual['failures'] == []
    names = re.findall(r'name="(\$ACTION_ID_[^"]+)"', bodies['server-action-form-ssr'])
    assert len(names) == 1
    action = result['http'][-1]
    assert action['id'] == 'server-action-submit' and action['status'] == 303 and action['passed'] is True
    assert action['headers']['location'] == '/action-result?value=fixture-action'
    assert digest(HERE / 'actual/responses/server-action-submit.txt') == {'sha256': action['bodySha256'], 'bytes': action['bodyBytes']}
    before, after = json.loads(bodies['cache-first']), json.loads(bodies['cache-after-revalidate'])
    assert before['generation'] == 1 and after['generation'] == 2
    assert result['cacheInvalidation'] == dict(before=before, after=after, passed=True)
    chunks = read(HERE / 'actual/stream-chunks.json')
    decoder = codecs.getincrementaldecoder('utf-8')()
    full, text, shell, ready = b'', '', -1, -1
    for index, chunk in enumerate(chunks):
        data = base64.b64decode(chunk['base64'], validate=True)
        assert len(data) == chunk['bytes']
        full += data
        text += decoder.decode(data)
        if shell < 0 and 'NEXT_STREAM_SHELL' in text:
            shell = index
        if ready < 0 and 'NEXT_STREAM_READY' in text:
            ready = index
    text += decoder.decode(b'', final=True)
    assert (len(chunks), shell, ready) == (5, 0, 2)
    assert full == (HERE / 'derived/stream-complete.html').read_bytes()
    assert result['streaming'] == dict(chunks=5, shellChunk=0, readyChunk=2, complete=True, incrementalDeliveryObserved=True)
    assert result['browserExit'] == dict(code=0, signal=None)
    assert browser['suite'] == 'nextjs-hydration-browser-diagnostic-v1'
    assert browser['perTestTimeoutMs'] == 20000 and browser['playwrightVersion'] == '1.64.1'
    assert browser['browserVersion'] == '156.0.8078.81'
    assert browser['passed'] is browser['functionalPassed'] is browser['browserErrorFree'] is browser['browserClosed'] is browser['assetCapturePassed'] is True
    for key in ['pageerrors', 'consoleerrors', 'failedrequests', 'errors']:
        assert browser[key] == []
    assert len(browser['tests']) == 2 and {r['id'] for r in browser['tests']} == {'client-counter', 'server-action'}
    for test in browser['tests']:
        assert test['passed'] is True and test['timedOut'] is False and test['error'] is None
        assert test['elapsedMs'] < 20000 and test['captureDrainBeforeCloseComplete'] is True
        png = checked(test['screenshot']).read_bytes()
        assert png[:8] == b'\x89PNG\r\n\x1a\n' and all(struct.unpack('>II', png[16:24]))
        readiness = test['observations']['readiness']
        assert readiness['ready'] is True and readiness['handlerInvoked'] is False
        key = 'buttonProps' if test['id'] == 'client-counter' else 'formProps'
        assert len(readiness[key]) == 1
        prop = readiness[key][0]
        assert prop['ownData'] is prop['memberOwnData'] is True and prop['memberType'] == 'function'
    counter, action = browser['tests']
    assert counter['observations']['initial'] == 'NEXT_CLIENT_COUNT:0' and counter['observations']['afterClick'] == 'NEXT_CLIENT_COUNT:1'
    assert action['observations']['value'] == 'browser-action' and action['observations']['marker'] == 'NEXT_ACTION_RESULT'
    assert action['observations']['builtActionIdNotHardcoded'] is action['observations']['actualFormPostObserved'] is True
    assert len(browser['actionPosts']) == 1
    post = browser['actionPosts'][0]
    raw_post = base64.b64decode(post['bodyBase64'], validate=True)
    assert len(raw_post) == post['bytes'] == 391 and b'browser-action' in raw_post
    assert post['headers']['next-action'] == names[0].removeprefix('$ACTION_ID_')
    assert len(browser['responseFinishedObservations']) == len(browser['responseHeaders']) == 14
    assert all(x['error'] is None for x in browser['responseFinishedObservations'])
    trace = browser['trace']
    requests = {(x['test'], x['requestId']): x for x in trace if x['event'] == 'request'}
    assert len(requests) == 14 and not any(x['event'] == 'requestfailed' for x in trace)
    for key, request in requests.items():
        events = [x for x in trace if (x.get('test'), x.get('requestId')) == key]
        assert all(sum(x['event'] == kind for x in events) == 1 for kind in ['response', 'requestfinished', 'response.finished'])
        assert next(x for x in events if x['event'] == 'response.finished')['error'] is None
    for name, click in [('client-counter', 'client-click'), ('server-action', 'action-submit-and-navigation')]:
        phases = [x for x in trace if x['test'] == name and x['event'] == 'phase']
        assert sum(x['phase'] == click for x in phases) == 1
        click_sequence = next(x['sequence'] for x in phases if x['phase'] == click)
        assert any(x['test'] == name and x['event'] == 'load' and x['sequence'] < click_sequence for x in trace)
    assert len(browser['bodyCaptures']) == 10 and len(browser['assetBodies']) == 9
    for capture in browser['bodyCaptures']:
        assert 'bodyError' not in capture and 'sizesError' not in capture
        assert digest(checked(capture['decodedBody'])) == {'sha256': capture['decodedSha256'], 'bytes': capture['decodedBytes']}
        assert capture['wireBodySha256'] is None
        assert capture['encodedSizes']['responseBodySize'] > 0
        if 'expected' in capture:
            assert capture['sourceMatch'] is True
            assert capture['decodedSha256'] == capture['expected']['sha256'] and capture['decodedBytes'] == capture['expected']['bytes']
    assert len([c for c in browser['assetBodies'] if c['test'] == 'client-counter']) == 5
    # Exact same worker and nine static bytes versus raw native result witnesses.
    native = read(HERE / 'comparison/native-client-result.json')
    nb = read(HERE / 'comparison/native-browser-result.json')
    assert native['browser'] == nb
    worker_hash = digest(HERE / 'source/control/browser-check.mjs')
    assert worker_hash == digest(HERE / 'source/browser/browser-check.mjs') == digest(HERE / 'comparison/native-browser-worker.mjs')
    assert native['browserArgv'][1] == portable['files'][next(i for i, x in enumerate(portable['files']) if x['copy']['path'] == 'comparison/native-browser-worker.mjs')]['original']['path']
    def static_map(b):
        return {(x['test'], urlsplit(x['url']).path): (x['decodedSha256'], x['decodedBytes']) for x in b['assetBodies']}
    assert static_map(browser) == static_map(nb) and len(static_map(browser)) == 9
    old = read(HERE / 'history/failed-v4-browser.json')
    assert old['passed'] is False and old['tests'][0]['timedOut'] is True
    assert old['failedrequests'][0]['failure']['errorText'] == 'net::ERR_ABORTED'
    summary = dict(state='STOCK_NODE_HYDRATION_CONTROL_DATA_REVIEW_PASSED_V1', portableFiles=len(portable['files']),
        http=24, cache=[1, 2], streamChunks=5, shellChunk=0, readyChunk=2, browserPassed=2, decodedBodiesVerified=10, staticResponsesSourceMatched=9,
        matchedBrowserWorkerSha256=worker_hash['sha256'], matchedNativeStaticResponses=9, rawExitCode=0, ownedGroupsClean=True,
        sourceAuthorRelationshipDeclared=True, nativeAcceptanceOwnedBySeparateReview=True, oldFailedV4Reclassified=False, wireBodyShaClaim=False)
    assert summary == read(HERE / 'results.json')['verifiedSummary']
    print(json.dumps(dict(summary, indexedPayloads=members, payloadBytes=payload_bytes), sort_keys=True))


if __name__ == '__main__':
    main()
