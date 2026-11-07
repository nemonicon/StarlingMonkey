"""Portable retained DATA reader. No imports of retained code or runtime tools."""
from pathlib import Path
import base64
import codecs
import copy
import gzip
import hashlib
import json
import re
from urllib.parse import urlsplit

HERE = Path(__file__).absolute().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def clean(terminal):
    return (type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0
            and terminal['timeout'] is False and terminal['forcedCleanup'] is False
            and terminal['parentOwnedGroupGone'] is True
            and terminal['allObservedOwnedGroupsGone'] is True
            and all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
            and all(g['alive'] is False for g in terminal['finalGroups']))


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


def browser_gates(browser):
    assert browser['passed'] is browser['functionalPassed'] is browser['browserErrorFree'] is True
    assert browser['browserClosed'] is True
    assert browser['errors'] == browser['failedrequests'] == browser['pageerrors'] == browser['consoleerrors'] == []
    assert browser['perTestTimeoutMs'] == 20000
    assert browser['responseCaptureDrainBeforeCloseLimitMs'] == 500
    assert browser['responseFinishedDrainAfterCloseLimitMs'] == 2000
    assert [x['id'] for x in browser['tests']] == ['client-counter', 'server-action']
    for test in browser['tests']:
        assert test['passed'] is True and test['timedOut'] is False and test['error'] is None
        assert test['captureDrainBeforeCloseComplete'] is True
        observer = test['cdpObserver']
        assert observer['stopped'] is False and observer['overflow'] is None and observer['eventsAfterStop'] == 0
    assert browser['tests'][0]['observations']['initial'] == 'NEXT_CLIENT_COUNT:0'
    assert browser['tests'][0]['observations']['afterClick'] == 'NEXT_CLIENT_COUNT:1'
    action = browser['tests'][1]['observations']
    assert action['marker'] == 'NEXT_ACTION_RESULT' and action['value'] == 'browser-action'
    assert action['actualFormPostObserved'] is True and action['builtActionIdNotHardcoded'] is True


def main():
    index = json.loads((HERE / 'index.json').read_text())
    assert {r['path'] for r in index['files']} == {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name != 'index.json'}
    for row in index['files']:
        value = (HERE / row['path']).read_bytes()
        assert sha(value) == row['sha256'] and len(value) == row['bytes']
    manifest = json.loads((HERE / 'evidence-index.json').read_text())
    compressed = (HERE / 'evidence.json.gz').read_bytes()
    assert sha(compressed) == manifest['bundle']['sha256'] and len(compressed) == manifest['bundle']['bytes']
    expanded = gzip.decompress(compressed)
    assert len(expanded) == manifest['expandedBytes'] < 20 * 1024**2
    blobs = {key: base64.b64decode(value, validate=True) for key, value in json.loads(expanded)['blobs'].items()}
    assert len(blobs) == manifest['uniqueBlobs']
    assert all(sha(value) == key for key, value in blobs.items())
    rows = {r['path']: r for r in manifest['files']}
    assert len(rows) == len(manifest['files']) == manifest['payloads']
    assert sum(r['bytes'] for r in rows.values()) == manifest['bytes']
    assert all(not name.startswith('/') and '..' not in Path(name).parts for name in rows)
    assert all(len(blobs[r['sha256']]) == r['bytes'] for r in rows.values())

    def raw(name):
        return blobs[rows[name]['sha256']]

    def read(name):
        return json.loads(raw(name))

    def ref(reference):
        names = [name for name, value in rows.items() if value['origin'] == reference['path']]
        assert names
        for name in names:
            assert rows[name]['sha256'] == reference['sha256'] and rows[name]['bytes'] == reference['bytes']
        return raw(names[0])

    review = json.loads((HERE / 'review.json').read_text())
    assert review['passed'] is True and review['originalV5AbortRemainsUnresolved'] is True
    assert review['curatorRanActorOrNetworkOrEngine'] is False and review['adoption'] is False
    source_prefixes = sorted({name.split('/')[1] for name in rows if name.startswith('sources/')})
    for family in source_prefixes:
        prefix = 'sources/' + family + '/'
        family_index = read(prefix + 'index.json')
        assert {n.removeprefix(prefix) for n in rows if n.startswith(prefix)} == {'index.json'} | {r['path'] for r in family_index['files']}
        for value in family_index['files']:
            b = raw(prefix + value['path'])
            assert sha(b) == value['sha256'] and len(b) == value['bytes']
    native = read('actual/native/result.json')
    stock = read('actual/stock/result.json')
    assert sha(raw('actual/stock/result.json')) == '1e02e58340d753ea18f91e584ceaf7d5d165abb939e1125febf1515e5615341e'
    assert sha(raw('actual/native/result.json')) == '650e7a91b972d6915cc03a82bdae487357b18c0d7f6ce01b5761696e1b3533cd'
    assert ref(review['stockResult']) == raw('actual/stock/result.json')
    assert ref(review['nativeResult']) == raw('actual/native/result.json')
    clients = {'stock': stock, 'native': read('actual/native/client/result.json')}
    spec = read('bindings/fixture-contract.json')
    expected = {r['id']: r for r in spec['requests']}
    assert len(expected) == 23
    pins = read('sources/browser-hydration-candidate-v3/asset-pins.json')['assets']
    asset_sets, post_bodies, cdp_counts = {}, {}, {}
    for label, client in clients.items():
        prefix = 'actual/stock/' if label == 'stock' else 'actual/native/client/'
        assert client['passed'] is True and client['errors'] == client['transportErrors'] == []
        assert len(client['http']) == 24 and all(r['passed'] is True for r in client['http'])
        assert [r['id'] for r in client['http']] == list(expected) + ['server-action-submit']
        previous = {}
        for record in client['http']:
            body = raw(prefix + 'responses/' + record['id'] + '.txt')
            assert sha(body) == record['bodySha256'] and len(body) == record['bodyBytes']
            if record['id'] in expected:
                contract(record, body, expected[record['id']], previous)
            else:
                assert record['status'] == 303 and record['headers']['location'] == '/action-result?value=fixture-action'
            previous[record['id']] = body
        ids = re.findall(rb'name="(\$ACTION_ID_[^"]+)"', previous['server-action-form-ssr'])
        assert len(ids) == 1 and ids[0].decode().removeprefix('$ACTION_ID_') == '40ca0bda6c41d5a4ff46cda3035ad9babb89d96900'
        cache = client['cacheInvalidation']
        assert cache['passed'] is True and cache['before']['generation'] == 1 and cache['after']['generation'] == 2
        chunks = read(prefix + 'stream-chunks.json')
        decoder = codecs.getincrementaldecoder('utf8')()
        text, shell, ready = '', -1, -1
        for i, chunk in enumerate(chunks):
            b = base64.b64decode(chunk['base64'], validate=True)
            assert len(b) == chunk['bytes']
            text += decoder.decode(b)
            if shell < 0 and 'NEXT_STREAM_SHELL' in text:
                shell = i
            if ready < 0 and 'NEXT_STREAM_READY' in text:
                ready = i
        text += decoder.decode(b'', final=True)
        assert len(chunks) == 5 and shell == 0 and ready == 2
        assert client['streaming'] == dict(chunks=5, shellChunk=0, readyChunk=2, complete=True, incrementalDeliveryObserved=True)
        assert client['browserExit'] == dict(code=0, signal=None)
        browser = client['browser']
        assert browser == read(prefix + 'browser/result.json')
        browser_gates(browser)
        assert len(browser['assetBodies']) == 9 and len(browser['bodyCaptures']) == 10
        actual_assets = {}
        for body in browser['bodyCaptures']:
            captured = ref(body['decodedBody'])
            assert len(captured) == body['decodedBytes'] and sha(captured) == body['decodedSha256']
            assert body['bodyCompletion']['kind'] == body['sizesCompletion']['kind'] == 'fulfilled'
            if body['method'] == 'POST':
                assert len(captured) == 2963
                post_bodies[label] = sha(captured)
        for asset in browser['assetBodies']:
            actual_assets[(asset['test'], urlsplit(asset['url']).path)] = (asset['decodedSha256'], asset['decodedBytes'])
            assert asset['sourceMatch'] is True and asset['status'] == 200
        assert all(actual_assets[('client-counter', p['path'])] == (p['sha256'], p['bytes']) for p in pins)
        asset_sets[label] = actual_assets
        for test in browser['tests']:
            assert ref(test['screenshot']).startswith(b'\x89PNG\r\n\x1a\n')
        assert len(browser['actionPosts']) == 1 and browser['actionPosts'][0]['bytes'] == 391
        post = browser['actionPosts'][0]
        assert post['headers']['next-action'] == '40ca0bda6c41d5a4ff46cda3035ad9babb89d96900'
        assert b'browser-action' in base64.b64decode(post['bodyBase64'])
        events = browser['cdpEvents']
        assert not [e for e in events if e['event'] == 'Network.loadingFailed']
        assert len(events) == sum(t['cdpObserver']['events'] for t in browser['tests'])
        assert all(x['identityProved'] is False for x in browser['cdpCorrelations'])
        cdp_counts[label] = len(events)
        events = [e for e in events if e['test'] == 'server-action']
        request = [e for e in events if e['event'] == 'Network.requestWillBeSent' and e['payload']['request']['method'] == 'POST']
        assert len(request) == 1
        request_id = request[0]['payload']['requestId']
        transport = [e for e in events if e['payload'].get('requestId') == request_id]
        finished = [e for e in transport if e['event'] == 'Network.loadingFinished']
        navigation = [e for e in events if e['event'] == 'Page.navigatedWithinDocument' and '/action-result?' in e['payload']['url']]
        assert len(finished) == len(navigation) == 1 and navigation[0]['payload']['navigationType'] == 'historyApi'
        assert int(finished[0]['arrivalNs']) < int(navigation[0]['arrivalNs'])
        assert sum(e['payload']['dataLength'] for e in transport if e['event'] == 'Network.dataReceived') == 2963
    assert asset_sets['stock'] == asset_sets['native']

    for label, cap in [('stock', 300), ('native', 600)]:
        terminal = read('monitors/' + label + '/terminal.json')
        started = read('monitors/' + label + '/started.json')
        observation = read('monitors/' + label + '/observation.json')
        assert clean(terminal) and started['timeoutSeconds'] == cap
        assert started['authority'] == terminal['authority'] and started['pid'] == terminal['pid']
        assert ref(terminal['stdout']) == raw('monitors/' + label + '/stdout.log')
        assert ref(terminal['stderr']) == raw('monitors/' + label + '/stderr.log')
        assert observation['passed' if label == 'native' else 'hostExperimentPassed'] is True
        assert observation['protectedInputsPreserved'] is True and observation['ownedGroupsClean'] is True
        owned = [read(name) for name in rows if name.startswith('monitors/' + label + '/owned-')]
        assert sorted(x['sequence'] for x in owned) == list(range(len(owned)))
        assert {json.dumps(x['process'], sort_keys=True) for x in owned} == {json.dumps(x, sort_keys=True) for x in terminal['observedProcesses']}
    assert stock['guestExecuted'] is False and stock['originalApplicationInputsPreserved'] is True
    assert native['passed'] is True and native['originalInputsPreserved'] is native['readonlyAppPreserved'] is True
    assert native['errors'] == [] and native['server']['forcedCleanup'] is False
    assert native['server']['exit'] == dict(code=0, signal=None, error=None)
    assert native['server']['shutdownRequested'] is native['server']['sigintSent'] is True
    authority = json.loads(ref(native['rootAuthority']))
    assert native['component'] == authority['component'] == review['nativeComponent']
    assert native['component']['sha256'] == '1c3108d2fdce72a1bfa8cc64a0e6e0645acd71223b26b6dc11d037d4a95efe83'
    construction = read('constructor/result.json')
    audit = read('constructor/component-audit.json')
    assert construction['passed'] is True and construction['error'] is None and construction['finalProtection']['unchanged'] is True
    for key in ['component', 'componentAudit', 'inputEntry', 'inputSourceIndex', 'engine', 'nativeMetadata']:
        assert construction['artifacts'][key] == authority[key]
    assert construction['callerIndex'] == authority['constructionCallerIndex']
    for command, cap in zip(construction['commands'], [1800, 120, 120]):
        terminal = json.loads(ref(command['terminal']))
        started = read('constructor/' + command['label'] + '/started.json')
        assert clean(terminal) and started['timeoutSeconds'] == cap and started['argv'] == command['argv']
        for key in ['stdout', 'stderr']:
            assert terminal[key] == command[key]
            ref(command[key])
    selected = read('sources/wasmtime-deployment-candidate-v7/plan.json')['selectedInterfaces']
    assert len(set(selected)) == 13 and set(audit['emittedImports']) == set(selected)
    assert audit['exports'] == ['wasi:http/incoming-handler@0.2.10']
    assert all(x.endswith('@0.2.10') for x in audit['emittedImports']) and audit['noExternalPreview1OrCustomImports'] is True
    receipt = read('root/engine462-fresh-app-v7-first-full-world-guard.json')
    constructor_world = read('bindings/constructor-world.json')
    assert receipt['unchanged'] is receipt['nativeInputsPreserved'] is True
    assert receipt['before'] == receipt['after'] == constructor_world['before'] == constructor_world['after']
    assert receipt['before']['members'] == 28 and receipt['before']['witFiles'] == 8
    assert receipt['before']['exactFileAndDirectoryMembership'] is receipt['before']['noSymlinkOrHardlinkAliases'] is True
    metadata = read('bindings/native-metadata.json')
    assert metadata['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1'
    assert metadata['engine'] == authority['engine']
    for key, value in authority['metadataExpectedFixedValues'].items():
        assert metadata[key] == value
    inventory = read('bindings/fresh-app-inputs.json')
    build = read('bindings/fresh-app-build-result.json')
    assert inventory == build['applicationInventory'] and build['passed'] is True and build['errors'] == []
    assert inventory['regularFiles'] == 2181 and inventory['bytes'] == 48714867 and len(inventory['directories']) == 425
    assert inventory['symlinks'] == [] and not any(x['path'] == '.' for x in inventory['directories'])
    physical = json.loads((HERE / 'current-copy-audit.json').read_text())['policies']
    assert all(x['listedFilesHashed'] == 2181 and x['listedFileBytesAndModeIdentityPolicyMatched'] is True for x in physical.values())
    assert physical['source']['directoriesIncludingRoot'] == 426 and physical['source']['extraFiles'] == []
    assert physical['native']['directoriesIncludingRoot'] == 427 and physical['native']['extraFiles'] == []
    assert physical['native']['extraDirectories'] == ['.next/cache']
    assert len(physical['stock']['extraFiles']) == 37 and physical['stock']['directoriesIncludingRoot'] == 455
    assert any(x['path'].startswith('.next/server/route-cache/') for x in physical['stock']['extraFiles'])
    admission = read('root/stock-v3-launch-admission.json')
    assert admission['freeBytes'] >= admission['minimumFreeBytes'] == 1073741824 and admission['continuousDiskGuardClaimed'] is False
    cli = [json.loads(line) for line in raw('root/native-v7-first-cli.stdout.log').decode().splitlines()]
    assert cli[0]['prepareOnly'] is False and cli[0]['freeBytesAtAdmission'] >= cli[0]['minimumFreeBytes'] == 1073741824
    assert cli[-1]['passed'] is True and cli[-1]['rawExitCode'] == 0
    # Finite mutations of the exact predicates; no actor or fault workload.
    negative = copy.deepcopy(read('monitors/native/terminal.json'))
    negative['interruptedSignals'] = [2]
    assert not clean(negative)
    negative = copy.deepcopy(clients['native']['browser'])
    negative['failedrequests'] = [{'failure': {'errorText': 'net::ERR_ABORTED'}}]
    try:
        browser_gates(negative)
    except AssertionError:
        pass
    else:
        raise AssertionError('Accepted strict browser failure')
    print(json.dumps(dict(passed=True, retainedPayloads=manifest['payloads'], sourceFamilies=len(source_prefixes),
                          actualTrials=2, httpPerArm=24, browsersPerArm=2, cdpEvents=cdp_counts,
                          nineDecodedScriptBodiesEqual=True, actionBodies=post_bodies,
                          appBinaryOrToolRequired=False, actorOrNetworkExecutedByReader=False,
                          originalV5AbortUnresolved=True, adoption=False)))


if __name__ == '__main__':
    main()
