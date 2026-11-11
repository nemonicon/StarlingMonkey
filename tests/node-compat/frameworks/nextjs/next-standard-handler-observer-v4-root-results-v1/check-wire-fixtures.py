"""Check finite V4 wire fixtures and constant placement; does not execute Wasm."""
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'next-standard-handler-return-observer-v4'


def require(value, message):
    if not value:
        raise ValueError(message)


def row(path):
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def main():
    if not (__debug__ and sys.flags.isolated and sys.dont_write_bytecode):
        raise RuntimeError('Use Python -I -B without -O')
    require(len(sys.argv) == 1, 'No arguments')
    wat_path, fixture_path = SOURCE / 'observer.wat', SOURCE / 'wire-byte-fixtures.json'
    inputs = [row(wat_path), row(fixture_path)]
    require([(x['sha256'], x['bytes']) for x in inputs] == [
        ('ca7e447508a48800580cade69e577f9b149327230b155756471c45588a51b701', 21754),
        ('f63faefb6916a6b951748f0b23771c0271c20944c08990988955f057ebabf317', 17406)], 'Frozen inputs')
    fixtures = json.loads(fixture_path.read_bytes())
    keys = ['marker', 'version', 'event', 'method', 'path', 'pathStatus',
            'snapshotStatus', 'corrState', 'corrCount', 'corr']
    states = [('missing', 0, None), ('valid', 1, 'a' * 64),
              ('invalid', 1, None), ('duplicate', 2, None)]
    paths = [('/actions', 'present-target'), ('/action-result', 'present-target'),
             (None, 'present-other'), (None, 'absent')]
    expected = []
    for method, (path, path_status), (state, count, corr) in itertools.product(
            ['GET', 'POST', 'unknown'], paths, states):
        expected.append(dict(zip(keys, ['NEXT_STANDARD_HANDLER_RETURN_OBSERVER_V4', 4,
            'inner-handler-import-returned', method, path, path_status, 'success', state, count, corr])))
    require(fixtures['normalRecords'] == expected, 'Complete ordered 3x4x4 finite wire enumeration')
    lines = [(json.dumps(x, separators=(',', ':'), ensure_ascii=True) + '\n').encode('ascii') for x in expected]
    require(fixtures['normalVariants'] == len(lines) == 48, 'Variant count')
    require(fixtures['maximumNormalBytes'] == max(map(len, lines)) == 314, 'Maximum ordinary wire size')
    require(fixtures['maximumNormalLine'].encode('ascii') in lines and
            len(fixtures['maximumNormalLine'].encode('ascii')) == 314, 'Witness of maximum')
    require(len(set(lines)) == 48 and all(len(x) <= 512 for x in lines), 'Unique bounded normal lines')
    limit = (json.dumps(dict(marker='NEXT_STANDARD_HANDLER_RETURN_OBSERVER_V4', version=4,
        event='record-limit'), separators=(',', ':')) + '\n').encode('ascii')
    require(fixtures['limitLine'].encode('ascii') == limit and fixtures['limitBytes'] == len(limit) == 89,
        'Separate limit frame')
    wat = wat_path.read_text()
    constants = []
    for match in re.finditer(r'\(data \(i32.const (\d+)\) "((?:\\[0-9a-f]{2}|[^"\\])*)"\)', wat):
        raw = re.sub(r'\\([0-9a-f]{2})', lambda m: chr(int(m[1], 16)), match[2]).encode('ascii')
        constants.append((int(match[1]), raw))
    require(len(constants) == wat.count('(data '), 'Every constant decoded')
    ordered = sorted(constants)
    require(all(a + len(raw) <= b for (a, raw), (b, _) in zip(ordered, ordered[1:])), 'No constant overlap')
    require(max(offset + len(raw) for offset, raw in constants) == 527 < 1024, 'Constants precede return areas')
    require(dict(constants)[348] == limit, 'Actual WAT limit bytes')
    require([row(wat_path), row(fixture_path)] == inputs, 'Inputs unchanged')
    result = dict(schemaVersion=1, state='ROOT_V4_INERT_WIRE_BYTE_CHECK_PASSED_V1', inputs=inputs,
        checker=row(Path(__file__).resolve()), normalVariants=48, maximumNormalBytes=314, limitBytes=89,
        constantsEndExclusive=527, constantsNonoverlapping=True, recordBufferBytes=512,
        wasmtimeInvoked=False, wasmExecuted=False, actualMissingPathTested=False,
        actualAllocatorTested=False, fullNextAccepted=False)
    output = HERE / 'wire-fixture-byte-check.json'
    with output.open('x') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
