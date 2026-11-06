"""Validate complete retained Node controls; no crypto/fixture rerun."""
from pathlib import Path
import hashlib
import json
import os
import re

R = Path('/Users/dan/dev/StarlingMonkey')
K = R / 'tests/node-compat/foundation-crypto'
P = K / 'node-crypto-hash-hmac-runtime-fixtures-v2'
OUT = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-node-oracle-v1')


def row(path):
    p = Path(path)
    b = p.read_bytes()
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


def read(path):
    return json.loads(Path(path).read_bytes())


def digest(value):
    assert value['outcome']['kind'] == 'return'
    v = value['outcome']['observed']
    assert v['type'] == 'string' and re.fullmatch('[a-f0-9]{64}', v['value'])
    assert value['cleanup'] == {'attempted': False}
    return v['value']


authority = row(K / 'node-crypto-hash-hmac-node-oracle-v1-root-authority.json')
terminal = row(OUT / 'terminal.json')
t = read(terminal['path'])
assert t['authority'] == authority and t['rawExitCode'] == 0
assert t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True
assert t['timeout'] is t['forcedCleanup'] is False
for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
    assert t[key] == []
stdout, stderr = row(OUT / 'stdout.log'), row(OUT / 'stderr.log')
assert t['stdout'] == stdout and t['stderr'] == stderr
frames = [json.loads(x) for x in (OUT / 'stdout.log').read_text().splitlines()]
assert len(frames) == 4
assert frames[0]['kind'] == 'host-node-identity' and frames[0]['version'] == 'v22.14.0'
assert frames[0]['hostProviderOnly'] is True and frames[0]['guestProviderProof'] is False
manifest = read(P / 'manifest.json')
values = []
for n, frame in enumerate(frames[1:], 1):
    assert frame['sequence'] == n and frame['name'] == 'run' and frame['kind'] == 'return'
    assert frame['observed']['type'] == 'string'
    v = json.loads(frame['observed']['value'])
    assert v['schemaVersion'] == 1 and v['kind'] == 'node-sha256-hash-hmac-ordinary-v1' and v['calls'] == n
    assert [x['id'] for x in v['nodeComparable']] == manifest['nodeComparableCases']
    assert len(v['nodeComparable']) == 20 and len(v['profilePolicy']) == 8
    assert all('unexpectedFixtureThrow' not in x for x in v['nodeComparable'])
    cases = {x['id']: x['value'] for x in v['nodeComparable']}
    for vector in manifest['knownHashVectors'] + manifest['knownHmacVectors']:
        c = cases[vector['id']]
        assert c['expectedHex'] == vector['expectedHex'] == digest(c['actual'])
    c = cases['hash-unicode-surrogate']
    assert c['messageUtf8Hex'] == c['expectedUtf8Hex'] == 'c3a9f09d849eefbfbd'
    digest(c['actual'])
    c = cases['hash-partition-abc']
    assert digest(c['actual']) == c['expectedHex']
    for length in [55, 56, 63, 64, 65]:
        c = cases['hash-block-' + str(length)]
        assert len(c['messageHex']) == length * 2 and digest(c['whole']) == digest(c['partitioned'])
    c = cases['hash-nonzero-window-copy']
    assert c['expectedMessageHex'] == '616263'
    assert digest(c['actual']) == digest(c['bufferWindow']) == c['expectedHex']
    for key in ['sameReceiver', 'sentinelsPreserved', 'bufferInputIsBuffer', 'bufferSameReceiver', 'bufferSentinelsPreserved']:
        assert c[key] is True
    assert c['afterCallerMutationHex'] == c['bufferAfterCallerMutationHex'] == 'd1787878e2'
    c = cases['hash-output-ownership']
    assert c['priorStableAfterSecond'] is c['secondStableAfterFirstMutation'] is True
    for name, expected in [('first', c['expectedFirstHex']), ('second', c['expectedSecondHex'])]:
        value = c[name]['outcome']['observed']
        assert c[name]['outcome']['kind'] == 'return' and c[name]['cleanup'] == {'attempted': False}
        assert value == dict(type='Buffer', bytes=32, hex=expected)
    digest(cases['hmac-empty']['actual'])
    c = cases['hmac-key-window-snapshot']
    assert digest(c['actual']) == c['expectedHex']
    assert c['callerUnchangedAfterCreate'] is c['sentinelsPreserved'] is True
    assert c['callerAfterMutationHex'] == '00' * 20
    for name in ['terminal-hash', 'terminal-hmac']:
        c = cases[name]
        assert digest(c['actual']) == c['terminal']['first']
        assert c['terminal']['updateAfter']['kind'] == 'throw'
        assert c['terminal']['updateAfter']['error']['code'] == 'ERR_CRYPTO_HASH_FINALIZED'
    c = cases['terminal-hash']['terminal']
    assert c['repeated']['kind'] == 'throw' and c['repeated']['error']['code'] == 'ERR_CRYPTO_HASH_FINALIZED'
    c = cases['terminal-hmac']['terminal']
    assert c['repeatedHex'] == dict(kind='return', observed=dict(type='string', value=''))
    assert c['repeatedBuffer'] == dict(kind='return', observed=dict(type='Buffer', bytes=0, hex=''))
    assert v['limits']['moduleInitCryptoCalls'] == 0
    assert v['limits']['stateCreationOnlyInsideOrdinaryRun'] is True
    values.append(v)
assert values[0]['nodeComparable'] == values[1]['nodeComparable'] == values[2]['nodeComparable']
raw_strings = [f['observed']['value'].encode('utf8') for f in frames[1:]]
report = dict(schemaVersion=1, state='ROOT_NODE22_HASH_HMAC_ORACLE_CAPTURED_VALIDATED_UNREVIEWED_V1',
    toolObservation=dict(chunkId='290f3e', rawExitCode=0), sourceIndex=row(P / 'index.json'),
    rootAuthority=authority, invocation=row(K / 'node-crypto-hash-hmac-node-oracle-v1-root-invocation.json'),
    terminal=terminal, stdout=stdout, stderr=stderr, observer=row(Path(__file__).resolve()),
    identity=frames[0], rawStringCount=3, comparableRecordsPerCall=20,
    totalComparableObservations=60, separatelyCapturedPolicyRecords=24,
    originalScalarUtf8=[dict(bytes=len(b), sha256=hashlib.sha256(b).hexdigest()) for b in raw_strings],
    comparableWholeRecordsEqualAcrossCalls=True, allSelectedKnownAnswersAndBoundariesPassed=True,
    completeRawStringsRetained=True, observedCalls=[1, 2, 3],
    unicodeSurrogateExpectedHex=digest(next(x['value'] for x in values[0]['nodeComparable'] if x['id'] == 'hash-unicode-surrogate')['actual']),
    emptyHmacExpectedHex=digest(next(x['value'] for x in values[0]['nodeComparable'] if x['id'] == 'hmac-empty')['actual']),
    policyNamespaceDescriptorsAndProviderConstantsKeptSeparate=True,
    hostHashHmacExecuted=True, guestExecuted=False, engineExecuted=False,
    nativeProfileValidated=False, runtimeAcceptanceClaim=False, operationalAdmission=False,
    requiresIndependentDataReview=True)
path = K / 'node-crypto-hash-hmac-node-oracle-v1-root-results.json'
with path.open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
    stream.flush()
    os.fsync(stream.fileno())
print(json.dumps(dict(rootResult=row(path), observations=60, guestValidated=False)))
