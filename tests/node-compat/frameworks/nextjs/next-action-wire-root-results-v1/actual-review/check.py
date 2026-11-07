"""Finite wire DATA reader. No extraction, producer imports, actors or network."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import re
import stat
import struct
import tarfile
import zlib

HERE = Path(__file__).resolve().parent
MAX_ARCHIVE = 64 * 1024**2


def sha(value):
    return hashlib.sha256(value).hexdigest()


def parse(value):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            assert key not in result
            result[key] = value
        return result
    return json.loads(value, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def framing(wire):
    assert len(wire) <= 2097152
    boundary = wire.index(b'\r\n\r\n'); assert boundary <= 16384
    lines = wire[:boundary].split(b'\r\n')
    assert re.fullmatch(rb'HTTP/1\.[01] 200(?: [^\r\n]*)?', lines[0])
    headers = {}
    for line in lines[1:]:
        name, value = line.split(b':', 1)
        assert re.fullmatch(rb"[!#$%&'*+.^_`|~0-9A-Za-z-]+", name)
        assert not re.search(rb'[\x00-\x08\x0a-\x1f\x7f]', value)
        headers.setdefault(name.decode('ascii').lower(), []).append(value.strip(b' \t').decode('latin1'))
    assert headers['content-encoding'] == ['gzip']
    assert headers['content-type'][0].split(';', 1)[0].strip().lower() == 'text/x-component'
    # Both actual arms selected this profile; no close-based EOF is inferred.
    assert headers['transfer-encoding'] == ['chunked'] and 'content-length' not in headers
    rest = wire[boundary + 4:]; offset = 0; pieces = []; trailers = []
    while True:
        end = rest.index(b'\r\n', offset); line = rest[offset:end]
        assert len(line) <= 1024 and re.fullmatch(rb'[0-9A-Fa-f]+', line)
        size = int(line, 16); offset = end + 2
        if size == 0:
            while True:
                end = rest.index(b'\r\n', offset); line = rest[offset:end]; offset = end + 2
                if not line:
                    break
                assert b':' in line and len(line) <= 16384
                trailers.append(line.decode('latin1'))
            assert offset == len(rest)
            break
        assert size <= 2097152 and offset + size + 2 <= len(rest)
        pieces.append(rest[offset:offset + size]); offset += size
        assert rest[offset:offset + 2] == b'\r\n'; offset += 2
    body = b''.join(pieces); assert len(body) <= 2097152
    return body, headers, trailers


def one_gzip(encoded):
    assert 18 <= len(encoded) <= 2097152 and encoded[:3] == b'\x1f\x8b\x08'
    flags = encoded[3]; assert flags & 0xe0 == 0
    offset = 10
    if flags & 4:
        size = struct.unpack_from('<H', encoded, offset)[0]; offset += size + 2
    for mask in [8, 16]:
        if flags & mask:
            offset = encoded.index(b'\0', offset) + 1
    assert offset <= min(65536, len(encoded) - 8)
    if flags & 2:
        assert struct.unpack_from('<H', encoded, offset)[0] == zlib.crc32(encoded[:offset]) & 0xffff
        offset += 2
    engine = zlib.decompressobj(-zlib.MAX_WBITS)
    decoded = engine.decompress(encoded[offset:], 4194305)
    assert len(decoded) <= 4194304 and engine.eof and not engine.unconsumed_tail
    assert len(engine.unused_data) == 8, 'Multiple members/trailing/unknown data refused'
    crc, size = struct.unpack('<II', engine.unused_data)
    assert crc == zlib.crc32(decoded) & 0xffffffff and size == len(decoded)
    return decoded, crc, size, offset, len(encoded) - offset - 8


def clean(terminal):
    assert type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0
    assert terminal['timeout'] is terminal['forcedCleanup'] is False
    assert terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    assert all(terminal[key] == [] for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    assert all(group['alive'] is False for group in terminal['finalGroups'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current', action='store_true', help='Rehash finite retained originals only, never app/tools.')
    parser.add_argument('--draft', action='store_true', help='Explicit unsealed payload inspection before independent peer/final index.')
    args = parser.parse_args()
    sealed = (HERE / 'index.json').exists()
    if sealed:
        index = parse((HERE / 'index.json').read_bytes())
        assert {row['path'] for row in index['files']} | {'index.json'} == {
            str(path.relative_to(HERE)) for path in HERE.rglob('*') if path.is_file()}
        for row in index['files']:
            data = (HERE / row['path']).read_bytes()
            assert (sha(data), len(data)) == (row['sha256'], row['bytes'])
    else:
        assert args.draft, 'Unsealed capsule requires explicit --draft'
    assert not any(path.is_symlink() for path in HERE.rglob('*'))
    inventory = parse((HERE / 'payload-index.json').read_bytes())
    compressed = (HERE / inventory['bundle']['path']).read_bytes()
    assert (sha(compressed), len(compressed)) == (inventory['bundle']['sha256'], inventory['bundle']['bytes'])
    unzip = zlib.decompressobj(16 + zlib.MAX_WBITS)
    expanded = unzip.decompress(compressed, MAX_ARCHIVE + 1)
    assert len(expanded) <= MAX_ARCHIVE and unzip.eof and not unzip.unused_data and not unzip.unconsumed_tail
    rows = {row['archivePath']: row for row in inventory['files']}
    assert len(rows) == len(inventory['files']) == inventory['members']
    assert len({row['original']['path'] for row in rows.values()}) == len(rows)
    blobs = {}; seen = set(); end = 0
    with tarfile.open(fileobj=io.BytesIO(expanded), mode='r:') as archive:
        for member in archive:
            assert member.isfile() and member.name in rows and member.name not in seen
            assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            assert member.offset == end and member.offset_data == member.offset + 512
            row = rows[member.name]; assert member.size == row['original']['bytes'] < 8 * 1024**2
            value = archive.extractfile(member).read()
            assert (sha(value), len(value)) == (row['original']['sha256'], row['original']['bytes'])
            blobs[row['original']['path']] = value; seen.add(member.name)
            end = member.offset_data + ((member.size + 511) // 512) * 512
    assert seen == set(rows) and len(expanded) - end >= 1024 and not any(expanded[end:])
    assert sum(len(value) for value in blobs.values()) == inventory['logicalBytes']
    def data(path):
        return parse(blobs[str(path)])
    def ref(row):
        value = blobs[row['path']]; assert (sha(value), len(value)) == (row['sha256'], row['bytes']); return value
    for index in inventory['sourceFamilies']:
        family = parse(ref(index)); root = Path(index['path']).parent
        for row in family['files']: ref(dict(row, path=str(root / row['path'])))
    protocol = parse(ref(inventory['protocol']))
    assert protocol['explicitOrder'] == ['native', 'stock'] and protocol['onePostPerArm'] is protocol['requestTransportOnly'] is True
    assert protocol['automaticRetry'] is protocol['additionalSamplesAllowed'] is protocol['browserInvoked'] is protocol['priorOriginalGatesAccepted'] is protocol['uniqueCauseProved'] is False
    request = parse(ref(protocol['request'])); body = ref(protocol['requestBody'])
    assert len(body) == 391 and sha(body) == 'ad790726f5abfe2e6a62e34d47dec844f18a61c9b65520b680547a3aebcc17ab'
    assert base64.b64decode(request['bodyBase64'], validate=True) == body
    captured = parse(ref(request['capturedBrowserSource']))['actionPosts'][0]
    assert captured['headers'] == request['headers'] and captured['bodyBase64'] == request['bodyBase64'] and captured['bytes'] == 391
    summaries = []
    native_observation = None
    for arm in inventory['arms']:
        kind = arm['arm']; root = Path(arm['outputRoot']); monitor = Path(arm['monitorRoot'])
        authority = parse(ref(protocol[kind + 'Authority']))
        assert authority['browserAllowed'] is False and authority['wireClientAllowed'] is True
        assert authority['sourceIndex'] in inventory['sourceFamilies']
        source = parse(ref(authority['sourceIndex'])); actor_root = Path(authority['sourceIndex']['path']).parent
        plan_ref = authority['plan' if kind == 'native' else 'plans']; plan = parse(ref(plan_ref))
        member = next(row for row in source['files'] if row['path'] == ('plan.json' if kind == 'native' else 'plans.json'))
        assert plan_ref == dict(member, path=str(actor_root / member['path']))
        assert plan['wireSourceIndex'] == protocol['commonSourceIndex'] and protocol['commonSourceIndex'] in plan['sourceFamilies']
        assert plan['wireSourceBindingPending'] is False
        assert str(root) == protocol[kind + 'OutputRoot'] == plan['outputPrefix'] + '-' + authority['runId']
        observation = data(monitor / 'observation.json'); terminal = parse(ref(observation['terminal'])); clean(terminal)
        if kind == 'native': native_observation = observation
        started = data(monitor / 'started.json')
        assert started['pid'] == terminal['pid'] and started['authority'] == terminal['authority'] == protocol[kind + 'Authority']
        assert started['timeoutSeconds'] == protocol[kind + 'OwnerSeconds'] and started['argv'] == arm['originalArgv']
        expected = [plan['node']['path'], str(actor_root / ('deploy.mjs' if kind == 'native' else 'run-stock.mjs'))]
        expected += [protocol['nativeAuthority']['path']] if kind == 'native' else [str(root), plan['standaloneSource'], authority['runId']]
        assert started['argv'] == expected
        for key in ['stdout', 'stderr']: ref(terminal[key])
        owned = [data(path) for path in sorted(blobs) if path.startswith(str(monitor) + '/owned-') and path.endswith('.json')]
        assert [row['sequence'] for row in owned] == list(range(len(owned)))
        assert {json.dumps(row['process'], sort_keys=True) for row in owned} == {json.dumps(row, sort_keys=True) for row in terminal['observedProcesses']}
        assert observation['rawExitCode'] == 0 and observation['ownedGroupsClean'] is observation['protectedInputsPreserved'] is True
        assert observation['freeBytesAtAdmission'] >= observation['minimumFreeBytes'] == 1073741824
        result = parse(ref(observation['result'])); client = parse(ref(result['client']['result']))
        assert result['passed'] is client['passed'] is True
        assert client['state'] == 'ACTION_WIRE_TRANSPORT_PASSED_UNREVIEWED_V1'
        assert client['reactFlightParsed'] is client['applicationSemanticsValidated'] is client['fullNextAcceptance'] is client['browserInvoked'] is False
        capture = client['capture']; actual = capture['request']; origin = client['origin']
        assert re.fullmatch(r'http://127\.0\.0\.1:[1-9][0-9]{0,4}', origin)
        assert 1 <= int(origin.rsplit(':', 1)[1]) <= 65535
        assert result['client']['command'] == [plan['node']['path'], str(actor_root.parent / 'next-action-wire-candidate-v1/wire-client.mjs'), origin, str(root / 'transport')]
        assert actual['method'] == 'POST' and actual['path'] == '/actions' and actual['bodyBytes'] == 391
        assert base64.b64decode(actual['bodyBase64'], validate=True) == body
        headers = dict(request['headers']); headers.update(host=origin[7:], origin=origin, referer=origin + '/actions',
                                                          connection='keep-alive', **{'accept-encoding': 'gzip', 'content-length': '391'})
        assert actual['headers'] == headers
        wire, encoded, decoded = [ref(client[key]) for key in ['rawSocketPrefix', 'nodeHttpEncodedPrefix', 'decodedFlight']]
        independent, response_headers, trailers = framing(wire); assert independent == encoded
        decoded_check, crc, size, header_bytes, deflate_bytes = one_gzip(encoded); assert decoded_check == decoded
        node_headers = {}
        for name, value in zip(capture['rawHeaders'][::2], capture['rawHeaders'][1::2]): node_headers.setdefault(name.lower(), []).append(value.strip())
        assert node_headers == response_headers
        validation = client['validation']
        assert validation['httpMessageEof'] is validation['encodedBodiesEqual'] is validation['singleGzipMember'] is validation['normalGzipFinish'] is validation['opaqueFlightComplete'] is True
        assert validation['framing'] == 'chunked' and validation['trailers'] == trailers
        assert (validation['crc32'], validation['isize'], validation['headerBytes'], validation['deflateBytes']) == (crc, size, header_bytes, deflate_bytes)
        assert capture['errors'] == client['errors'] == [] and capture['timeout'] is False
        assert capture['rawSocketPrefixTruncated'] is capture['encodedBodyPrefixTruncated'] is False
        assert capture['droppedEvents'] == capture['omittedErrors'] == 0
        assert capture['receivedWireBytes'] == capture['retainedWireBytes'] == len(wire)
        assert capture['receivedEncodedBytes'] == capture['retainedEncodedBytes'] == len(encoded)
        assert capture['responseComplete'] is capture['httpMessageEndObserved'] is capture['rawFinalizedAfterDataListeners'] is True
        assert capture['peerSocketEndObserved'] is False
        events = capture['events']; times = [int(row['ns']) for row in events]; assert times == sorted(times)
        order = [next(number for number, row in enumerate(events) if row['event'] == name) for name in
                 ['http-message-end', 'raw-capture-finalized-after-data-listeners', 'client-owned-agent-destroy-requested', 'socket-close', 'client-owned-agent-cleanup-finished']]
        assert order == sorted(order)
        cleanup = capture['clientCleanup']
        assert cleanup['prefixesDurableBeforeCleanup'] is cleanup['validationFinishedBeforeCleanup'] is cleanup['httpMessageEndBeforeCleanup'] is cleanup['agentDestroyCalled'] is cleanup['socketCloseObserved'] is True
        assert cleanup['errors'] == [] and cleanup['socketClosedBeforeClientCleanup'] is False
        assert cleanup['clientInitiatedSocketCloseRequested'] is True
        if kind == 'native':
            assert result['server']['exit'] == dict(code=0, signal=None, error=None) and result['server']['forcedCleanup'] is False
            assert result['readonlyAppPreserved'] is result['originalInputsPreserved'] is True
            world = parse(ref(inventory['nativeWorldGuard'])); assert world['before'] == world['after'] and world['unchanged'] is world['nativeInputsPreserved'] is True
            assert world['before']['members'] == 28 and world['before']['witFiles'] == 8
            assert result['component'] == authority['component'] and result['constructionResult'] == authority['constructionResult']
            audit = parse(ref(authority['componentAudit']))
            assert audit['passed'] is True and len(audit['emittedImports']) == 13
            assert audit['component'] == authority['component'] and audit['exports'] == ['wasi:http/incoming-handler@0.2.10']
            assert all(name.endswith('@0.2.10') for name in audit['emittedImports'])
        else:
            assert result['guestExecuted'] is result['browserInvoked'] is result['fullNextAcceptance'] is False
            assert result['serverClosed'] is result['appClosed'] is result['originalApplicationInputsPreserved'] is result['copiedOriginalFilesPreserved'] is True
        summaries.append(dict(arm=kind, rawSocketBytes=len(wire), encodedBytes=len(encoded), decodedBytes=len(decoded), crc32=crc, isize=size, transportPassed=True, fullNextAcceptance=False))
    prior = parse(ref(inventory['nativeBeforeStock']))
    assert prior['protocol'] == inventory['protocol'] and prior['originalNativeRawExitCode'] == 0
    assert prior['originalNativeGroupsClean'] is prior['nativeProtectedInputsPreserved'] is prior['stockOutputAndMonitorAbsent'] is True and prior['stockActorInvoked'] is False
    assert parse(ref(prior['nativeObservation'])) == native_observation
    assert prior['nativeTerminal'] == native_observation['terminal'] and prior['nativeWorldGuard'] == inventory['nativeWorldGuard']
    if args.current:
        for row in inventory['files']:
            path = Path(row['original']['path']); info = path.lstat()
            assert stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and path.resolve() == path
            value = path.read_bytes(); assert (sha(value), len(value)) == (row['original']['sha256'], row['original']['bytes'])
    print(json.dumps(dict(portableDataPassed=True, capsuleSealed=sealed, members=len(rows), logicalBytes=inventory['logicalBytes'],
                         currentRetainedOriginalsChecked=args.current, arms=summaries, actorOrNetworkInvoked=False,
                         originalGateAcceptanceChanged=False, uniqueCauseProved=False)))


if __name__ == '__main__':
    main()
