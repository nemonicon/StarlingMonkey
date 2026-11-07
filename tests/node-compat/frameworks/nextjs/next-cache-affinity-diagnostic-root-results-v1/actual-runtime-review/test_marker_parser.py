"""Pure synthetic DATA tests plus optional terminal-record readback; no actor."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('held_affinity_data_parser', HERE / 'marker_parser.py')
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--actual', action='store_true')
    args = cli.parse_args()
    fixtures = {'requests': [dict(id=name, method='POST' if i == 2 else 'GET', path='/api/revalidate' if i == 2 else '/api/cache') for i, name in enumerate(parser.CASES)]}
    client = dict(http=[dict(id=name, status=200, passed=True) for name in parser.CASES], passed=False)
    records = [dict(schemaVersion=1, marker=parser.MARKER, phase='request-admission', nonce=f'{i+1:032x}', ordinal=7,
        method=case['method'], pathname=case['path'], identityScope='js-global-state-epoch') for i, case in enumerate(fixtures['requests'])]
    encode = lambda rows: b''.join((json.dumps(v, separators=(',', ':')) + '\n').encode() for v in rows)
    raw = 'config ✓\n'.encode() + encode(records)
    checks = 0

    def need(value):
        nonlocal checks
        assert value is True
        checks += 1

    def refuses(callback):
        nonlocal checks
        try:
            callback()
        except (ValueError, TypeError, KeyError):
            checks += 1
        else:
            raise AssertionError('Malformed/unknown DATA was accepted')

    parsed = parser.parse(raw)
    observed = parser.correlate(parsed, client, fixtures)
    need(len(parsed['nonMarkerLines']) == 1 and parsed['nonMarkerLines'][0]['text'] == 'config ✓')
    need(parsed['markerLines'][0]['startByte'] == len('config ✓\n'.encode()))
    need(parsed['markerLines'][-1]['endByte'] == len(raw))
    need(observed['distinctObservedEpochLabels'] == 4 and observed['observedOrdinals'] == [7]*4)
    need(observed['originalClientPassed'] is False and observed['cacheCauseProven'] is False and observed['nativeStoreIdentityProven'] is False)
    same = copy.deepcopy(records)
    for i, row in enumerate(same):
        row['nonce'] = 'a'*32
        row['ordinal'] = i+1
    need(parser.correlate(parser.parse(encode(same)), client, fixtures)['distinctObservedEpochLabels'] == 1)
    for field, value in [('schemaVersion', True), ('phase', 'response-finished'), ('nonce', 'F'*32), ('nonce', '0'*31), ('ordinal', True), ('ordinal', 0), ('ordinal', 1.5), ('ordinal', 9007199254740992), ('method', 'PUT'), ('pathname', '/api/cache-other'), ('identityScope', 'native-store')]:
        rows = copy.deepcopy(records)
        rows[0][field] = value
        refuses(lambda rows=rows: parser.parse(encode(rows)))
    extra = copy.deepcopy(records);extra[0]['unknown'] = True
    refuses(lambda: parser.parse(encode(extra)))
    missing = copy.deepcopy(records);del missing[0]['ordinal']
    refuses(lambda: parser.parse(encode(missing)))
    refuses(lambda: parser.parse(encode(records).replace(b'"schemaVersion":1', b'"schemaVersion":1,"schemaVersion":1', 1)))
    escaped = encode(records).replace(parser.MARKER.encode(), b'\\u004eEXT_CACHE_AFFINITY_V1', 1)
    need(len(parser.parse(escaped)['markerLines']) == 4)
    refuses(lambda: parser.parse(escaped.replace(b'"schemaVersion":1', b'"schemaVersion":1,"schemaVersion":1', 1)))
    refuses(lambda: parser.parse(encode(records).replace(b'NEXT_CACHE_AFFINITY_V1', b'NEXT_CACHE_AFFINITY_V2', 1)))
    refuses(lambda: parser.parse(b'broken NEXT_CACHE_AFFINITY_V1\n'))
    refuses(lambda: parser.parse(b'\xff'))
    refuses(lambda: parser.parse(b'x'*(parser.MAX_BYTES+1)))
    refuses(lambda: parser.parse(b'x'*65537))
    refuses(lambda: parser.parse(b'\n'*4097))
    refuses(lambda: parser.correlate(parser.parse(encode(records[:3])), client, fixtures))
    refuses(lambda: parser.correlate(parser.parse(encode(records+[records[0]])), client, fixtures))
    wrong_order = copy.deepcopy(records);wrong_order[1], wrong_order[2] = wrong_order[2], wrong_order[1]
    refuses(lambda: parser.correlate(parser.parse(encode(wrong_order)), client, fixtures))
    duplicate = copy.deepcopy(client);duplicate['http'][1]['id'] = duplicate['http'][0]['id']
    refuses(lambda: parser.correlate(parsed, duplicate, fixtures))
    bad_client = copy.deepcopy(client);bad_client['http'][0]['passed'] = False
    refuses(lambda: parser.correlate(parsed, bad_client, fixtures))
    nonincreasing = copy.deepcopy(same);nonincreasing[1]['ordinal'] = nonincreasing[0]['ordinal']
    refuses(lambda: parser.parse(encode(nonincreasing)))
    result = dict(pureDataChecks=checks, actorOrToolOrGuestInvoked=False, syntheticDataNotRuntimeProof=True)
    if args.actual:
        work = Path('/private/tmp/starling-node-compat/next-wasmtime-deployment-full02a-cache-affinity-first')
        actual = parser.parse((work/'wasmtime.stdout.log').read_bytes())
        contract = json.loads((HERE.parents[1]/'fixture-contract.json').read_bytes())
        projection = parser.correlate(actual, json.loads((work/'client/result.json').read_bytes()), contract)
        assert projection['distinctObservedEpochLabels'] == 4 and projection['observedOrdinals'] == [7]*4
        result['actualTerminalReadback'] = projection
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
