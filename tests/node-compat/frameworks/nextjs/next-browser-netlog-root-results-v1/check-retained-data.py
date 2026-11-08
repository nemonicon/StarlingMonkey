"""Portable checkout DATA reader; historical modes/inodes remain documentary."""
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent / 'retained-raw-data-v1'
MAX = 32 * 1024 * 1024


def physical(path):
    s = path.lstat()
    return s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns


def bounded(path, size=None):
    assert path.resolve() == path and not path.is_symlink()
    before = physical(path)
    assert stat.S_ISREG(before[2]) and before[3] == 1 and 0 <= before[4] <= MAX
    if size is not None:
        assert before[4] == size
    data = path.read_bytes()
    assert physical(path) == before and len(data) == before[4]
    return data


def dependencies(value):
    if isinstance(value, dict):
        return [(v['id'], v['type']) for k, v in value.items() if k == 'source_dependency'] + [
            d for k, v in value.items() if k != 'source_dependency' for d in dependencies(v)]
    if isinstance(value, list):
        return [d for v in value for d in dependencies(v)]
    return []


def main():
    manifest_data = bounded(HERE / 'manifest.json')
    assert len(manifest_data) <= 2 * 1024 * 1024
    assert hashlib.sha256(manifest_data).hexdigest() == '056dabc2681f3caa8e857a1ae5fdf2a3c8b70b934226ce4063364b724574904f'
    manifest = json.loads(manifest_data)
    assert manifest['copiedFileCount'] == len(manifest['files']) == 92
    assert manifest['copiedPayloadBytes'] == sum(r['copied']['bytes'] for r in manifest['files']) == 5601728 <= manifest['maximumPayloadBytes'] == MAX
    payloads, by_original, identities = {}, {}, set()
    for row in manifest['files']:
        copied, original = row['copied'], row['original']
        rel = Path(copied['relativePath'])
        assert not rel.is_absolute() and '..' not in rel.parts and rel.parts[0] == 'files'
        assert copied['relativePath'] not in payloads and original['path'] not in by_original
        data = bounded(HERE / rel, copied['bytes'])
        assert hashlib.sha256(data).hexdigest() == copied['sha256'] == original['sha256']
        assert copied['bytes'] == original['bytes'] and copied['mode'] == original['mode']
        identity = physical(HERE / rel)[:2]
        assert identity not in identities
        identities.add(identity)
        payloads[copied['relativePath']] = data
        by_original[original['path']] = row
        if rel.suffix == '.png':
            assert data.startswith(b'\x89PNG\r\n\x1a\n')
    checker = manifest['checker']
    assert checker['relativePath'] == 'check.py'
    assert checker['sha256'] == '994835237060bb987a9b7487b71f834653df613a2f9d070d8bb91e5e1cc2a046' and checker['bytes'] == 10627
    checker_data = bounded(HERE / 'check.py', checker['bytes'])
    assert hashlib.sha256(checker_data).hexdigest() == checker['sha256']
    actual_files = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}
    assert actual_files == set(payloads) | {'manifest.json', 'check.py'}
    actual_dirs = {p.relative_to(HERE).as_posix() for p in [HERE, *HERE.rglob('*')] if p.is_dir()}
    assert actual_dirs == {d['relativePath'] for d in manifest['copiedDirectoryModes']}
    for d in manifest['copiedDirectoryModes']:
        path = HERE / d['relativePath']
        assert not path.is_symlink() and path.is_dir() and d['mode'] == 0o700
    observed_modes = dict(files=sorted({stat.S_IMODE((HERE / rel).stat().st_mode) for rel in payloads}), directories=sorted({stat.S_IMODE((HERE / d).stat().st_mode) for d in actual_dirs}))

    def load(rel):
        return json.loads(payloads['files/' + rel])

    def original(ref):
        # Literal historical paths are DATA lookup keys, never filesystem reads.
        row = by_original[ref['path']]
        assert {k: row['original'][k] for k in ['path', 'sha256', 'bytes']} == ref
        return json.loads(payloads[row['copied']['relativePath']])

    protocol = load('root/protocol.json')
    outcomes = {}
    for arm, seconds, expected_exit, owned_count in [('native', 600, 1, 15), ('stock', 300, 0, 12)]:
        browser = load(arm + '/browser/result.json')
        host = load('native/client/result.json' if arm == 'native' else 'stock/actor/result.json')
        root_result = load(arm + '/actor/result.json')
        origin = browser['origin']
        assert origin == host['origin']
        assert host['browserArgv'][1] == protocol['sharedBrowserWorker']['path']
        assert host['browserArgv'][2:4] == ['--origin', origin]
        assert host['browserArgv'][-2:] == ['--output', str(Path(protocol[arm + 'OutputRoot']) / ('client/browser' if arm == 'native' else 'browser'))]
        assert browser['functionalPassed'] is True and len(browser['tests']) == 2
        assert all(t['passed'] is True and t['timedOut'] is False for t in browser['tests'])
        error_free = not (browser['pageerrors'] or browser['consoleerrors'] or browser['failedrequests'])
        strict = error_free and not browser['errors'] and browser['browserClosed']
        assert browser['browserErrorFree'] == error_free and browser['passed'] == strict
        assert strict == (arm == 'stock') and host['passed'] == root_result['passed'] == strict
        assert host['cacheInvalidation']['before']['generation'] == 1
        assert host['cacheInvalidation']['after']['generation'] == (1 if arm == 'native' else 2)
        assert host['cacheInvalidation']['passed'] == (arm == 'stock')
        if arm == 'native':
            assert len(browser['errors']) == 3 and all(e['message'] == 'net::ERR_ABORTED' for e in browser['errors'])
        else:
            assert browser['errors'] == browser['failedrequests'] == []
        netlog = original(browser['netlog']['file'])
        analysis = load('root/' + arm + '-netlog-analysis.json')
        assert analysis['input'] == browser['netlog']['file'] and analysis['targetUrl'] == origin + '/actions'
        assert netlog['constants']['logCaptureMode'] == 'Default'
        events, c = netlog['events'], netlog['constants']
        assert len(events) == analysis['totalEvents'] == browser['netlog']['eventCount']
        names = {v: k for k, v in c['logEventTypes'].items()}
        types = {v: k for k, v in c['logSourceType'].items()}
        phases = {v: k for k, v in c['logEventPhase'].items()}
        errors = {v: k for k, v in c['netError'].items()}
        witnesses, edges = {}, []
        for i, event in enumerate(events):
            key = event['source']['id'], event['source']['type']
            params = event.get('params', {})
            if types[key[1]] == 'URL_REQUEST' and params.get('url') == origin + '/actions' and params.get('method') == 'POST':
                witnesses.setdefault(key, []).append(i)
            for target in dependencies(params):
                edges.append(dict(eventIndex=i, sourceId=key[0], sourceTypeId=key[1], dependencySourceId=target[0], dependencySourceTypeId=target[1]))
        assert len(witnesses) == analysis['candidateCount'] == 1
        key = next(iter(witnesses))
        assert analysis['candidates'] == [dict(sourceId=key[0], sourceTypeId=key[1], witnessEventIndexes=witnesses[key])]
        related = [e for e in edges if (e['sourceId'], e['sourceTypeId']) == key or (e['dependencySourceId'], e['dependencySourceTypeId']) == key]
        assert related == analysis['explicitDependencyEdges']
        selected = {key}
        for edge in related:
            selected |= {(edge['sourceId'], edge['sourceTypeId']), (edge['dependencySourceId'], edge['dependencySourceTypeId'])}
        rebuilt, codes = [], []
        for i, event in enumerate(events):
            identity = event['source']['id'], event['source']['type']
            if identity not in selected:
                continue
            params = event.get('params', {})
            rebuilt.append(dict(index=i, time=event['time'], eventTypeId=event['type'], eventType=names[event['type']], phaseId=event['phase'], phase=phases[event['phase']], sourceId=identity[0], sourceTypeId=identity[1], sourceType=types[identity[1]], params=params))
            if 'net_error' in params:
                code = params['net_error']
                codes.append(dict(eventIndex=i, sourceId=identity[0], sourceTypeId=identity[1], eventType=names[event['type']], time=event['time'], code=code, name=errors[code], isNegativeCode=code < 0))
        assert rebuilt == analysis['selectedEvents'] and codes == analysis['explicitNetErrors']
        assert not any(code['isNegativeCode'] for code in codes) and analysis['negativeNetErrorObserved'] is False
        assert analysis['historyCompleteProved'] is analysis['completeRequestLifecycleProved'] is analysis['uniqueCauseProved'] is False
        start, terminal, observation = [load(arm + '/owner/' + name + '.json') for name in ['started', 'terminal', 'observation']]
        assert start['timeoutSeconds'] == seconds and start['pid'] == terminal['pid']
        assert start['authority'] == terminal['authority'] == protocol[arm + 'Authority']
        assert terminal['rawExitCode'] == expected_exit and terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
        assert terminal['timeout'] is terminal['forcedCleanup'] is False
        assert all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
        assert observation['rawExitCode'] == expected_exit and observation['ownedGroupsClean'] is observation['protectedInputsPreserved'] is True
        assert len(terminal['observedProcesses']) == owned_count
        for i, proc in enumerate(terminal['observedProcesses']):
            owned = load(arm + '/owner/owned-' + str(i).zfill(4) + '.json')
            assert owned['sequence'] == i and owned['process'] == proc
        original(observation['terminal'])
        original(observation['result'])
        outcomes[arm] = dict(rawExitCode=expected_exit, strictBrowserPassed=strict, legacyCachePassed=host['cacheInvalidation']['passed'], netlogEvents=len(events), postCandidates=1, selectedNegativeCodeObserved=False)
    correction = load('root/analysis-authoring-origin-correction.json')
    wrong = load('root/native-netlog-analysis-wrong-origin.json')
    assert correction['actualOrigin'] == load('native/browser/result.json')['origin']
    assert wrong['targetUrl'] == correction['wrongOrigin'] + '/actions' and wrong['candidateCount'] == 0
    assert wrong['input'] == load('native/browser/result.json')['netlog']['file']
    assert correction['targetOrBrowserRerun'] is False
    original(correction['correctedReport'])
    original(correction['originSource'])
    print(json.dumps(dict(passed=True, state='OFFLINE_FINITE_NETLOG_RAW_DATA_VERIFIED_V1', copiedFiles=92, copiedBytes=5601728, outcomes=outcomes, originalsRead=False, historicalOriginalAndCopiedModesAndInodesDocumentary=True, historicalModesRequiredAtCheckout=False, observedCheckoutModes=observed_modes, heldAnalyserImportedOrInvoked=False, actorOrNetworkInvoked=False, netlogEofOrCauseProved=False, priorFailedGatesAccepted=False)))


if __name__ == '__main__':
    main()
