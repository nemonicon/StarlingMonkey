"""Bounded read-only DATA parser. Nonmarker output is retained, never a gate waiver."""
import argparse
import hashlib
import json
from pathlib import Path
import re

MARKER = 'NEXT_CACHE_AFFINITY_V1'
KEYS = {'schemaVersion', 'marker', 'phase', 'nonce', 'ordinal', 'method', 'pathname', 'identityScope'}
CASES = ['cache-first', 'cache-repeat', 'cache-revalidate', 'cache-after-revalidate']
MAX_BYTES = 1024 * 1024


def require(value, message):
    if not value:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def parse(stdout):
    require(type(stdout) is bytes and len(stdout) <= MAX_BYTES, 'stdout DATA size/type bound')
    stdout.decode('utf-8', errors='strict')
    lines = stdout.splitlines(keepends=True)
    require(len(lines) <= 4096, 'stdout line count bound')
    markers, other = [], []
    offset = 0
    seen = {}
    for number, encoded in enumerate(lines, 1):
        line = encoded.decode('utf-8', errors='strict')
        require(len(encoded) <= 65536, 'stdout single-line bound')
        bare = line.removesuffix('\n').removesuffix('\r')
        row = dict(lineNumber=number, startByte=offset, endByte=offset + len(encoded),
                   bytes=len(encoded), rawLineSha256=hashlib.sha256(encoded).hexdigest())
        offset += len(encoded)
        value = None
        if bare.lstrip().startswith('{'):
            value = json.loads(bare, object_pairs_hook=unique_object,
                parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
        marker = value.get('marker') if type(value) is dict else None
        if marker != MARKER:
            require(not (type(marker) is str and marker.startswith('NEXT_CACHE_AFFINITY')) and
                    'NEXT_CACHE_AFFINITY' not in bare, 'unknown/malformed affinity record')
            other.append(dict(row, text=bare))
            continue
        require(len(bare) <= 512, 'marker line bound')
        require(type(value) is dict and set(value) == KEYS, 'marker exact schema')
        require(type(value['schemaVersion']) is int and value['schemaVersion'] == 1, 'marker schema version')
        require(value['marker'] == MARKER and value['phase'] == 'request-admission', 'marker/phase')
        require(type(value['nonce']) is str and re.fullmatch('[0-9a-f]{32}', value['nonce']) is not None, 'nonce format')
        require(type(value['ordinal']) is int and 1 <= value['ordinal'] <= 9007199254740991, 'safe ordinal')
        require((value['method'], value['pathname']) in [('GET', '/api/cache'), ('POST', '/api/revalidate')], 'selected method/path')
        require(value['identityScope'] == 'js-global-state-epoch', 'identity scope')
        previous = seen.get(value['nonce'])
        require(previous is None or value['ordinal'] > previous, 'repeated token ordinal is ambiguous/nonincreasing')
        seen[value['nonce']] = value['ordinal']
        markers.append(dict(row, record=value))
    return dict(schemaVersion=1, marker=MARKER, stdoutBytes=len(stdout),
                stdoutSha256=hashlib.sha256(stdout).hexdigest(), markerLines=markers,
                nonMarkerLines=other, originalLineCount=len(lines), rawOutputFiltered=False)


def correlate(parsed, client, contract):
    require(len(parsed['markerLines']) == 4, 'exact four fixture marker admissions required')
    require(type(client) is dict and type(contract) is dict and type(client['http']) is list and
            type(contract['requests']) is list and len(client['http']) <= 64 and len(contract['requests']) <= 64,
            'bounded client/fixture case arrays')
    fixtures = {v['id']: v for v in contract['requests']}
    actual = {v['id']: v for v in client['http']}
    require(len(fixtures) == len(contract['requests']) and len(actual) == len(client['http']), 'duplicate fixture/client case ID')
    require(all(case in fixtures and case in actual for case in CASES), 'missing fixture/client cache case')
    positions = [next(i for i, v in enumerate(client['http']) if v['id'] == case) for case in CASES]
    require(positions == sorted(positions) and len(set(positions)) == 4, 'client cache contract order')
    correlated = []
    for case, line, position in zip(CASES, parsed['markerLines'], positions):
        fixture, record = fixtures[case], line['record']
        require((record['method'], record['pathname']) == (fixture['method'], fixture['path']), 'marker order/method/path differs from fixture')
        require(actual[case]['status'] == 200 and actual[case]['passed'] is True, 'cache HTTP case functional record')
        correlated.append(dict(case=case, clientHttpArrayIndex=position, lineNumber=line['lineNumber'],
                               startByte=line['startByte'], endByte=line['endByte'],
                               nonce=record['nonce'], ordinal=record['ordinal'],
                               method=record['method'], pathname=record['pathname']))
    tokens = [v['nonce'] for v in correlated]
    ordinals = [v['ordinal'] for v in correlated]
    return dict(schemaVersion=1, cases=correlated, distinctObservedEpochLabels=len(set(tokens)),
                observedOrdinals=ordinals, allObservedOrdinalsEqual=len(set(ordinals)) == 1,
                correlationScope='Recorded stdout line order plus unchanged sequential fixture contract order; no shared request-ID or cross-clock equality.',
                nativeStoreIdentityProven=False, cacheCauseProven=False, cacheCoherenceProven=False,
                originalRuntimeGateUnchanged=True, originalClientPassed=client['passed'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stdout', type=Path, required=True)
    parser.add_argument('--client', type=Path, required=True)
    parser.add_argument('--contract', type=Path, required=True)
    args = parser.parse_args()
    require(args.stdout.stat().st_size <= MAX_BYTES, 'stdout file bound before read')
    require(args.client.stat().st_size <= 16*MAX_BYTES and args.contract.stat().st_size <= MAX_BYTES, 'client/contract file bounds before read')
    parsed = parse(args.stdout.read_bytes())
    correlated = correlate(parsed, json.loads(args.client.read_bytes()), json.loads(args.contract.read_bytes()))
    print(json.dumps(dict(parsed=parsed, correlation=correlated), indent=2))
