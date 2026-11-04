"""Read-only hash/data/reverse-proof review; never imports owner modules."""
from pathlib import Path
import hashlib
import json
import stat

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
OWNER = BASE / 'stream-trace-regression-candidate-v2'
PARENT = BASE / 'stream-trace-regression-candidate-v1'
EXPECTED = '5b40a987b3a2bba08b3192c8a3e3b80a16a32d8de2019c4ecdc9406d3733ef30'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def regular(path, digest=None, size=None):
    assert stat.S_ISREG(path.lstat().st_mode) and not path.is_symlink(), path
    h = hashlib.sha256()
    count = 0
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            h.update(block)
            count += len(block)
    if digest is not None:
        assert h.hexdigest() == digest, path
    if size is not None:
        assert count == size, path
    return {'sha256': h.hexdigest(), 'bytes': count}

def indexed(root, expected):
    raw = (root / 'index.json').read_bytes()
    assert sha(raw) == expected
    document = json.loads(raw)
    seen = set()
    total = 0
    for row in document['files']:
        assert row['path'] not in seen
        seen.add(row['path'])
        relative = Path(row['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        total += regular(root / relative, row['sha256'], row['bytes'])['bytes']
    return {'indexSha256': expected, 'files': len(seen), 'bytes': total}

def main():
    owner = indexed(OWNER, EXPECTED)
    assert owner['files'] == 43
    parent = indexed(PARENT, '636dfc0561891ff23f028b19289693aa77452fc25e8c5b415f1bf4a191afe7ac')
    assert parent['files'] == 15
    raw = (OWNER / 'input-freeze.json').read_bytes()
    closure = json.loads(raw)
    seen = set()
    total = 0
    for row in closure['inputs']:
        path = OWNER / row['path']
        canonical = str(path.resolve(strict=True))
        assert canonical not in seen
        seen.add(canonical)
        total += regular(path, row['sha256'], row['bytes'])['bytes']
    assert len(seen) == 6062
    live_adapter = (BASE.parents[2] / 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm').resolve()
    assert str(live_adapter) in seen
    adapter = regular(live_adapter, '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0', 53512)
    proof = json.loads((OWNER / 'transformation-proof.json').read_bytes())
    assert len(proof['records']) == 3
    reversals = []
    for row in proof['records']:
        before, after = (PARENT / row['path']).read_bytes(), (OWNER / row['path']).read_bytes()
        assert sha(before) == row['beforeSha256'] and sha(after) == row['afterSha256']
        reverse = after.decode()
        for edit in reversed(row['edits']):
            assert reverse.count(edit['new']) == edit['occurrences']
            reverse = reverse.replace(edit['new'], edit['old'])
        assert reverse.encode() == before
        reversals.append({'path': row['path'], 'edits': len(row['edits']), 'reverseExact': True})
    for row in proof['unchanged']:
        assert (PARENT / row['path']).read_bytes() == (OWNER / row['path']).read_bytes()
        regular(OWNER / row['path'], row['sha256'])
    template = (OWNER / 'preflight.template.mjs').read_text()
    assert (OWNER / 'preflight.mjs').read_text() == template.replace('@INPUTS_SHA@', sha(raw))
    oracle = json.loads((OWNER / 'node-results.json').read_bytes())
    old = json.loads((PARENT / 'node-results.json').read_bytes())
    assert oracle['node'] == 'v22.14.0' and oracle['groups'] == 11
    assert oracle['nodeObserved'][:8] == old['nodeObserved']
    assert oracle['hostModelObserved'][:8] == old['hostModelObserved']
    objects, model = oracle['nodeObserved'][8:], oracle['hostModelObserved'][8:]
    encodings = [{'type': 'undefined'}, {'type': 'object', 'value': None}, {'type': 'string', 'value': 'utf8'}]
    assert [row['encoding'] for row in objects] == encodings
    assert [row['encoding'] for row in model] == [{'type': 'string', 'value': 'utf8'}] * 3
    assert objects[2] == model[2]
    for rows in [objects, model]:
        for i, row in enumerate(rows):
            assert row['accepted'] and row['samePayload'] and row['valueId'] == 1 and row['payloadKeys'] == ['id']
            assert row['writeCalls'] == row['hookCallbackCalls'] == row['finish'] == row['close'] == 1
            assert row['userWriteCallbackCalls'] == (0 if i == 0 else 1)
    expected_gaps = [row['id'] for row in old['differences']] + ['object-one-argument', 'object-callback-overload']
    assert [row['id'] for row in oracle['differences']] == expected_gaps
    for name, digest in oracle['sourcePins'].items():
        regular(OWNER / name, digest)
    encoding_report = BASE / 'trace-semantics-candidate-v1/encoding-results.json'
    coordinate = json.loads(encoding_report.read_bytes())
    assert coordinate['expected'][0]['observed'][0]['encoding'] == {'type': 'undefined'}
    assert coordinate['expected'][-1]['observed'] == [{'type': 'null'}]
    assert coordinate['expected'][2]['observed'][0]['encoding'] == {'type': 'string', 'value': 'utf8'}
    source_evidence = json.loads((OWNER / 'evidence/source-test-results.json').read_bytes())
    syntax_evidence = json.loads((OWNER / 'evidence/syntax-results.json').read_bytes())
    assert source_evidence['passed'] == 14 and syntax_evidence['count'] == 10
    assert all(row['exitCode'] == 0 for row in syntax_evidence['checks'])
    # Rehash the owner index after all input reads. No owner code was executed.
    regular(OWNER / 'index.json', EXPECTED)
    result = {
        'schemaVersion': 1,
        'state': 'INDEPENDENT_SOURCE_AND_SAVED_DATA_REVIEW_PASSED_NO_ACTION_MAINS',
        'owner': owner, 'preservedV1': parent,
        'inputClosure': {'sha256': sha(raw), 'files': len(seen), 'bytes': total, 'allHashesAndSizesMatch': True},
        'liveAdapter': adapter, 'reverseProofs': reversals,
        'unchangedFiles': [row['path'] for row in proof['unchanged']],
        'renderedPreflightMatchesTemplate': True,
        'originalEightNodeAndHostModelRecordsExact': True,
        'objectEncodings': encodings,
        'objectHookCallbackCounts': [row['hookCallbackCalls'] for row in objects],
        'objectUserCallbackCounts': [row['userWriteCallbackCalls'] for row in objects],
        'payloadIdentityValueKeysAndLifecycleChecked': True,
        'noNullInput': True,
        'hostModelGapIds': expected_gaps,
        'encodingReportCoordination': {'path': str(encoding_report.relative_to(BASE)), **regular(encoding_report), 'sameUnderlyingObservedValuesDifferentNullCarrier': True},
        'ownerEvidenceReadNotRerun': {'sourceChecks': 14, 'syntaxChecks': 10, 'nodeCases': 11},
        'manualSourceReview': {
            'preflight': 'Fixed input hash checked before JSON rows; fixed runtime index and exact b827/873c production guard delegated; captured recheck remains unchanged.',
            'driver': 'Only finite case-count/per-kind/report edits. Node differences remain data; no model parity forced. Same run()->string/zero-import request and emitted-WIT audit, three retained and fresh Jco/Wasmtime checks.',
            'publication': 'Final admission recheck precedes publishCompletion. Existing exclusive tracked writer hashes result/component/core/glue; external raw exit0 remains mandatory.',
            'sourceScope': 'No new host service, private hook, scheduler/semantic fix, native/policy/receipt change. No unusual input, invalid receiver, Proxy, fault or fatal operation.'
        },
        'blockers': [],
        'limitations': ['Saved Node/oracle data authenticated, not independently rerun.', 'Future eleven-case component has not been executed by this review.', 'Parity may remain false and is reported rather than required; retained calls do not prove Engine.reset or isolation.', 'No runtime/build/guest/host/performance or complete Streams compatibility claim.'],
        'reviewerInvocations': {'ownerMains': False, 'nodeOracleOrSourceTests': False, 'nativePreflight': False, 'componentizerOrGuestOrTargetHost': False, 'nativeBuildOrCompiler': False},
        'runtimeAcceptanceClaim': False
    }
    with (HERE / 'results.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'state': result['state'], 'ownerFiles': owner['files'], 'inputFiles': len(seen), 'blockers': 0}))

if __name__ == '__main__':
    main()
