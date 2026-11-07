"""Pure retained-JSON checks, no imports of target JS, HTTP or native code.

CLI needs --capture (guest raw JSON) and --node-reference (independent actual
Node raw JSON). Neither a Node owner raw0 nor HTTP200 is semantic acceptance.
"""
from pathlib import Path
import argparse
import json
import re

CASE_IDS = ['read-eof-metadata', 'bodyall-text', 'bodyall-json', 'bodyall-arraybuffer',
            'repeat-read-eof', 'clone-one-cancel-other-drain',
            'direct-reader-cancel-pending', 'direct-reader-cancel-after-read']
JSON_VALUE = {'marker': 'NEXT_JSON_GET', 'query': 'lifecycle-v1'}
HEALTH_VALUE = {'marker': 'NEXT_HEALTH_OK', 'ok': True}
JSON_BYTES = b'{"marker":"NEXT_JSON_GET","query":"lifecycle-v1"}'
HEALTH_BYTES = b'{"marker":"NEXT_HEALTH_OK","ok":true}'
EOF = {'done': True, 'valueUndefined': True, 'hex': None}

def need(value, label):
    if value is not True: raise ValueError(label)

def exact(a, b, label):
    if type(a) is bytes or type(b) is bytes:
        need(type(a) is bytes and type(b) is bytes and a == b, label)
        return
    need(json.dumps(a, sort_keys=True, separators=(',', ':')) ==
         json.dumps(b, sort_keys=True, separators=(',', ':')), label)

def origin(value):
    need(type(value) is str and re.fullmatch(r'http://127\.0\.0\.1:([1-9][0-9]{0,4})', value) is not None,
         'explicit canonical loopback origin')
    port = int(value.rsplit(':', 1)[1]); need(1 <= port <= 65535 and port != 80, 'canonical explicit port')

def metadata(value, target, used):
    need(type(value) is dict, 'metadata record')
    exact(value.get('status'), 200, 'HTTP status')
    exact(value.get('bodyUsed'), used, 'public bodyUsed')
    exact(value.get('url'), target, 'actual final response URL')
    mime = value.get('contentType')
    need(type(mime) is str and mime.split(';', 1)[0].strip().lower() == 'application/json', 'content type')

def fulfilled(value):
    exact(value, {'fulfilled': True, 'valueUndefined': True}, 'normal public settlement')

def raw_bytes(value):
    need(type(value) is str and len(value) <= 8192 and len(value) % 2 == 0 and
         re.fullmatch('[0-9a-f]*', value) is not None, 'bounded exact byte hex')
    return bytes.fromhex(value)

def prefix(part, expected, allow_done=True):
    need(type(part) is dict and type(part.get('done')) is bool, 'read result type')
    if part['done']:
        need(allow_done, 'nonempty first read'); exact(part, EOF, 'canonical EOF')
    else:
        exact(part.get('valueUndefined'), False, 'nonterminal byte read')
        chunk = raw_bytes(part.get('hex'))
        need(len(chunk) > 0 and expected.startswith(chunk), 'observed first chunk prefix')

def drained(row, expected):
    exact(row.get('complete'), True, 'complete public EOF')
    exact(raw_bytes(row.get('hex')), expected, 'complete exact surviving bytes')
    exact(row.get('receivedBytes'), len(expected), 'public received bytes')
    exact(row.get('eof'), EOF, 'actual EOF result')
    fulfilled(row.get('closed'))
    parts = row.get('parts')
    need(type(parts) is list and all(type(n) is int and n > 0 for n in parts) and
         sum(parts) == len(expected), 'chunk accounting, no required partition')

def validate(capture, executor):
    need(type(capture) is dict, 'capture type')
    exact(capture.get('schemaVersion'), 1, 'schema')
    exact(capture.get('executor'), executor, 'Source-reported executor')
    base = capture.get('origin'); origin(base)
    exact(capture.get('caseIds'), CASE_IDS, 'predeclared eight-case order')
    exact(capture.get('allCasesAttempted'), True, 'all cases attempted')
    target = base + '/api/json?q=lifecycle-v1'
    exact(capture.get('expectedJsonUrl'), target, 'configured target')
    if executor == 'guest-global-fetch': exact(capture.get('call'), 1, 'single deployed collection')
    rows = capture.get('records')
    need(type(rows) is list and len(rows) == 8, 'exact record denominator')
    exact([row.get('id') for row in rows], CASE_IDS, 'record order')
    for row in rows:
        exact(row.get('error'), None, 'case error retained as failure')
        exact(row.get('cleanupErrors'), [], 'cleanup errors retained as failure')
        exact(row.get('captureLogError'), None, 'capture log error')
        o = row.get('observations'); need(type(o) is dict, 'observations')
        if row['id'] == 'repeat-read-eof':
            items = o.get('responses'); need(type(items) is list and len(items) == 4, 'four finite repetitions')
            for ordinal, item in enumerate(items, 1):
                exact(item.get('ordinal'), ordinal, 'repeat ordinal')
                metadata(item.get('before'), base + '/api/health', False)
                drained(item, HEALTH_BYTES); metadata(item.get('after'), base + '/api/health', True)
            continue
        metadata(o.get('before'), target, False); metadata(o.get('after'), target, True)
        if row['id'] in ['read-eof-metadata', 'clone-one-cancel-other-drain']:
            drained(o, JSON_BYTES)
        if row['id'].startswith('bodyall-'):
            second = o.get('secondRead')
            need(type(second) is dict and second.get('fulfilled') is False and
                 second.get('error', {}).get('isTypeError') is True, 'second body consumption rejects TypeError')
            if row['id'] == 'bodyall-text': exact(o.get('value'), JSON_BYTES.decode(), 'text bytes')
            elif row['id'] == 'bodyall-json': exact(o.get('value'), JSON_VALUE, 'typed JSON value')
            else: exact(raw_bytes(o.get('hex')), JSON_BYTES, 'arrayBuffer bytes')
        if row['id'] == 'clone-one-cancel-other-drain':
            metadata(o.get('cloneBefore'), target, False); metadata(o.get('cloneAfter'), target, True)
            fulfilled(o.get('cancel')); fulfilled(o.get('canceledClosed'))
        if row['id'].startswith('direct-reader-cancel-'):
            fulfilled(o.get('cancel')); fulfilled(o.get('closed'))
            exact(o.get('readAfterCancel'), EOF, 'closed read after cancel')
            if row['id'].endswith('-pending'):
                pending = o.get('pendingRead'); need(type(pending) is dict and pending.get('fulfilled') is True, 'pending read settles')
                prefix(pending.get('part'), JSON_BYTES)
            else: prefix(o.get('firstRead'), JSON_BYTES, allow_done=False)
    return {'executor': executor, 'cases': 8, 'fetches': 11, 'publicObservableProfilePassed': True,
            'nativeResourcesOrTaskBranchesProved': False}

def compare(guest, reference):
    a = validate(guest, 'guest-global-fetch'); b = validate(reference, 'node22-global-fetch')
    exact(guest['origin'], reference['origin'], 'same actual control origin')
    # Exact expected body/JSON semantics are checked independently above. Neither
    # transport headers, chunk partition, cancellation timing nor error text is compared.
    return dict(schemaVersion=1, passed=True, guest=a, nodeReference=b,
                actualOwnersAndPinsStillRequireRootReview=True,
                resourceCountsProved=False, allHttpCleanupProved=False,
                nativePostAbortCauseProved=False, fullNextAccepted=False, adoption=False)

def read(path):
    data = Path(path).read_bytes(); need(len(data) <= 262144, 'accepted capture cap')
    return json.loads(data)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', required=True)
    parser.add_argument('--node-reference', required=True)
    args = parser.parse_args()
    print(json.dumps(compare(read(args.capture), read(args.node_reference)), sort_keys=True))

if __name__ == '__main__': main()
