"""Inspect finite retained DATA only; no extraction, actor, imports or network."""
import argparse
import base64
import codecs
import hashlib
import io
import json
from pathlib import Path
import stat
import tarfile

HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            assert key not in result
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def clean(terminal):
    assert terminal['timeout'] is terminal['forcedCleanup'] is False
    assert terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    assert all(terminal[key] == [] for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    assert all(group['alive'] is False for group in terminal['finalGroups'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current', action='store_true', help='Also rehash only the finite retained originals, never app/tools.')
    args = parser.parse_args()
    index = parse((HERE / 'index.json').read_bytes())
    assert {row['path'] for row in index['files']} | {'index.json'} == {
        str(path.relative_to(HERE)) for path in HERE.rglob('*') if path.is_file()}
    assert not any(path.is_symlink() for path in HERE.rglob('*'))
    for row in index['files']:
        path = HERE / row['path']; data = path.read_bytes()
        assert path.stat().st_nlink == 1 and (sha(data), len(data)) == (row['sha256'], row['bytes'])
    inventory = parse((HERE / 'payload-index.json').read_bytes())
    compressed = (HERE / inventory['bundle']['path']).read_bytes()
    assert (sha(compressed), len(compressed)) == (inventory['bundle']['sha256'], inventory['bundle']['bytes'])
    rows = {row['archivePath']: row for row in inventory['files']}
    assert len(rows) == len(inventory['files']) == inventory['members']
    assert len({row['original']['path'] for row in rows.values()}) == len(rows)
    assert inventory['logicalBytes'] == sum(row['original']['bytes'] for row in rows.values()) < 64 * 1024**2
    blobs = {}; consumed = set()
    with tarfile.open(fileobj=io.BytesIO(compressed), mode='r:gz') as archive:
        for member in archive:
            assert member.isfile() and not member.issym() and not member.islnk()
            assert member.name in rows and member.name not in consumed
            assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            row = rows[member.name]; assert member.size == row['original']['bytes'] < 8 * 1024**2
            data = archive.extractfile(member).read()
            assert (sha(data), len(data)) == (row['original']['sha256'], row['original']['bytes'])
            blobs[row['original']['path']] = data; consumed.add(member.name)
    assert consumed == set(rows)
    def raw(path):
        return blobs[str(path)]
    def data(path):
        return parse(raw(path))
    def descriptor(ref):
        value = raw(ref['path']); assert (sha(value), len(value)) == (ref['sha256'], ref['bytes']); return value
    for family in inventory['sourceFamilies']:
        source = parse(descriptor(family)); root = Path(family['path']).parent
        for row in source['files']:
            descriptor(dict(row, path=str(root / row['path'])))
    for arm in inventory['arms']:
        root = Path(arm['outputRoot']); client_root = Path(arm['clientRoot']); monitor = Path(arm['monitorRoot'])
        observation = data(monitor / 'observation.json'); terminal = parse(descriptor(observation['terminal']))
        result = parse(descriptor(observation['result'])); client = result if arm['kind'] == 'stock' else parse(descriptor(result['client']['result']))
        assert type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == observation['rawExitCode'] == arm['rawExitCode']
        clean(terminal)
        assert observation['ownedGroupsClean'] is observation['protectedInputsPreserved'] is True
        started = data(monitor / 'started.json')
        assert started['authority'] == terminal['authority'] == arm['authority']
        assert started['pid'] == terminal['pid'] and started['timeoutSeconds'] == arm['timeoutSeconds']
        assert started['argv'] == arm['originalArgv']
        for key in ['stdout', 'stderr']: descriptor(terminal[key])
        owned = [data(path) for path in sorted(blobs) if path.startswith(str(monitor) + '/owned-') and path.endswith('.json')]
        assert [row['sequence'] for row in owned] == list(range(len(owned)))
        assert {json.dumps(row['process'], sort_keys=True) for row in owned} == {json.dumps(row, sort_keys=True) for row in terminal['observedProcesses']}
        assert result['passed'] is arm['strictPassed'] and client['passed'] is arm['strictPassed']
        assert len(client['http']) == 24 and all(row['passed'] is True for row in client['http'])
        for row in client['http']:
            body = raw(client_root / 'responses' / (row['id'] + '.txt'))
            assert (sha(body), len(body)) == (row['bodySha256'], row['bodyBytes'])
        cache = client['cacheInvalidation']
        assert [cache['before']['generation'], cache['after']['generation']] == arm['cacheGenerations']
        assert cache['before'] == data(client_root / 'responses/cache-first.txt')
        assert cache['after'] == data(client_root / 'responses/cache-after-revalidate.txt')
        assert cache['passed'] is arm['cachePassed']
        chunks = data(client_root / 'stream-chunks.json'); decoder = codecs.getincrementaldecoder('utf8')(); text = ''; shell = ready = -1
        for number, chunk in enumerate(chunks):
            value = base64.b64decode(chunk['base64'], validate=True); assert len(value) == chunk['bytes']; text += decoder.decode(value)
            if shell < 0 and 'NEXT_STREAM_SHELL' in text: shell = number
            if ready < 0 and 'NEXT_STREAM_READY' in text: ready = number
        text += decoder.decode(b'', final=True)
        assert (len(chunks), shell, ready) == (5, 0, 2)
        assert client['streaming'] == dict(chunks=5, shellChunk=0, readyChunk=2, complete=True, incrementalDeliveryObserved=True)
        browser = data(client_root / 'browser/result.json'); assert browser == client['browser']
        assert browser['functionalPassed'] is browser['assetCapturePassed'] is True
        assert browser['passed'] is browser['browserErrorFree'] is arm['strictPassed']
        assert [row['passed'] for row in browser['tests']] == [True, True]
        assert browser['perTestTimeoutMs'] == 20000 and browser['responseCaptureDrainBeforeCloseLimitMs'] == 500
        assert browser['cdpScope'].get('extraSessionEnabled', True) is arm['extraCdpSession']
        complete = [row for row in browser['bodyCaptures'] if row['decodedBody'] is not None]
        missing = [row for row in browser['bodyCaptures'] if row['decodedBody'] is None]
        assert len(complete) == arm['completeBodies'] and len(missing) == (0 if arm['strictPassed'] else 1)
        for row in complete:
            value = descriptor(row['decodedBody']); assert (sha(value), len(value)) == (row['decodedSha256'], row['decodedBytes'])
        if arm['strictPassed']:
            assert browser['errors'] == browser['failedrequests'] == browser['pageerrors'] == browser['consoleerrors'] == []
        else:
            assert len(browser['errors']) == 3 and len(browser['failedrequests']) == 1
            assert browser['failedrequests'][0]['requestId'] == 7 and browser['failedrequests'][0]['failure']['errorText'] == 'net::ERR_ABORTED'
            assert missing[0]['requestId'] == 7 and missing[0]['encodedSizes'] is None
            assert missing[0]['bodyCompletion']['kind'] == missing[0]['sizesCompletion']['kind'] == 'requestfailed'
            assert str(client_root / 'browser/server-action-r7.body') not in blobs
        for row in browser['tests']: assert descriptor(row['screenshot']).startswith(b'\x89PNG\r\n\x1a\n')
        if arm['kind'] == 'native':
            assert result['server']['exit'] == dict(code=0, signal=None, error=None)
            assert result['readonlyAppPreserved'] is result['originalInputsPreserved'] is True
            assert len(result['emittedImports']) == 13 and all(name.endswith('@0.2.10') for name in result['emittedImports'])
            assert client['supplementalValidation']['passed'] is True and client['supplementalValidation']['checks'] == 80
            capture = client['supplemental']; assert len(capture['observations']) == 6
            for row in capture['observations']:
                assert data(Path(capture['output']) / (row['id'] + '.json')) == row
                assert descriptor(row['body']) == base64.b64decode(row['bodyBase64'], validate=True)
        else:
            assert result['guestExecuted'] is False and result['originalApplicationInputsPreserved'] is True
    if args.current:
        for row in inventory['files']:
            path = Path(row['original']['path']); info = path.lstat()
            assert stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and path.resolve() == path
            value = path.read_bytes(); assert (sha(value), len(value)) == (row['original']['sha256'], row['original']['bytes'])
    print(json.dumps(dict(portableDataPassed=True, arms=len(inventory['arms']), archiveMembers=len(rows),
                         logicalBytes=inventory['logicalBytes'], currentOriginalsChecked=args.current,
                         runtimeAcceptanceChanged=False, actorOrNetworkInvoked=False)))


if __name__ == '__main__':
    main()
