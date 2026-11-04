"""Independent read-only source/data review; no owner modules are imported."""
from pathlib import Path
import hashlib
import json
import stat

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
OWNER = BASE / 'measurement-common-byte-domain-candidate-v1'
OLD = BASE / 'measurement-workload-candidate-v1'
PROPOSAL = BASE / 'trace-semantics-candidate-v1'
EXPECTED = 'fbf4790df0beed34511a13553d07fd9bf57a5919bcf9338db2844f5826ebbdae'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def regular(path, digest=None, size=None):
    assert stat.S_ISREG(path.lstat().st_mode) and not path.is_symlink(), path
    hasher, count = hashlib.sha256(), 0
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            hasher.update(block)
            count += len(block)
    assert digest is None or hasher.hexdigest() == digest, path
    assert size is None or count == size, path
    return {'sha256': hasher.hexdigest(), 'bytes': count}

def indexed(root, expected):
    raw = (root / 'index.json').read_bytes()
    assert sha(raw) == expected
    rows = json.loads(raw)['files']
    assert len({row['path'] for row in rows}) == len(rows)
    for row in rows:
        path = Path(row['path'])
        assert not path.is_absolute() and '..' not in path.parts
        regular(root / path, row['sha256'], row['bytes'])
    return {'sha256': expected, 'files': len(rows)}

def load(root, name):
    return json.loads((root / name).read_bytes())

def main():
    owner = indexed(OWNER, EXPECTED)
    assert owner['files'] == 28
    old = indexed(OLD, '39774bbadae98f70e777edb8801ed0ea70d50430f7193f0f4a7fce3630cca41c')
    proposal = indexed(PROPOSAL, '59c9233c5dd1c9f07c4da16a79abdb58abc9775b37c714f6af179e85f23f0631')
    raw = (OWNER / 'input-freeze.json').read_bytes()
    inputs = load(OWNER, 'input-freeze.json')['inputs']
    paths, total = {}, 0
    for row in inputs:
        path = OWNER / row['path']
        identity = str(path.resolve(strict=True))
        assert identity not in paths
        paths[identity] = row
        total += regular(path, row['sha256'], row['bytes'])['bytes']
    assert len(inputs) == len(paths) == 5417
    tool_inputs = load(OWNER, 'tool-inputs.json')['inputs']
    for row in tool_inputs:
        path = Path(row['path'])
        declared = paths[str(path.resolve(strict=True))]
        assert (declared['sha256'], declared['bytes']) == (row['sha256'], row['bytes'])
    derivation = load(OWNER, 'derivation.json')
    before = (OLD / 'workload.mjs').read_text()
    after = before
    assert sha(before.encode()) == derivation['beforeSha256'] and len(derivation['edits']) == 4
    for edit in derivation['edits']:
        assert after.count(edit['old']) == edit['count'] == 1
        after = after.replace(edit['old'], edit['new'])
    assert after.encode() == (OWNER / 'workload.mjs').read_bytes()
    assert sha(after.encode()) == derivation['afterSha256']
    for edit in reversed(derivation['edits']):
        assert after.count(edit['new']) == 1
        after = after.replace(edit['new'], edit['old'])
    assert after == before
    for name in ['node-provider.mjs', 'stock-provider.mjs']:
        assert (OWNER / name).read_bytes() == (OLD / name).read_bytes()
    node, stock, graph = [load(OWNER, 'evidence/' + name + '-results.json') for name in ['node', 'stock', 'bundle']]
    assert node['sourceSha256'] == derivation['afterSha256']
    assert node['proposedCoreSha256'] == '5c0241a73f4cdffc61d7c962bd4d1a1d2015f8fbadef59a4631b7551f9a767b9'
    assert node['nodeExecutableSha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    assert len(node['cases']) == len(stock['cases']) == 8
    old_node = load(OLD, 'evidence/node-results.json')
    old_oracles = {(row['id'], row['iterations']): row['oracle'] for row in old_node['expected']}
    summaries = []
    assert [(r['id'], r['iterations']) for r in node['cases']] == [(name, count) for name in derivation['newIds'] for count in [1, 16]]
    for a, b in zip(node['cases'], stock['cases']):
        assert (a['id'], a['iterations']) == (b['id'], b['iterations'])
        assert a['expected'] == a['proposed'] == b['expected'] == b['observed']
        assert a['proposedExact'] and b['checksumEqual'] and b['traceExact']
        observed = a['expected']
        assert len(observed['records']) == a['iterations']
        assert all(all(record['returns']) for record in observed['records'])
        original = old_oracles[(a['id'].removesuffix('-hwm-plus1'), a['iterations'])]
        assert original['unsignedChecksum'] == observed['unsignedChecksum'] and original['totalUnits'] == observed['totalUnits']
        summaries.append({'id': a['id'], 'iterations': a['iterations'], 'unsignedChecksum': observed['unsignedChecksum'], 'units': observed['totalUnits'], 'entireTraceAndResultExactAcrossThree': True})
    assert graph['imports'] == [] and graph['providerOptions'] == {} and graph['schedulerOverride'] is False
    assert len(graph['modules']) == len(set(graph['modules'])) == 102
    original_graph = load(OLD, 'evidence/bundle-results.json')['reports'][2]
    old_files = {str(OLD / name) for name in ['entry.mjs', 'workload.mjs', 'stock-provider.mjs']}
    own_files = {str(OWNER / name) for name in ['entry.mjs', 'workload.mjs', 'stock-provider.mjs']}
    assert set(original_graph['moduleIds']) - old_files == set(graph['modules']) - own_files
    assert len(set(graph['modules']) - own_files) == 99
    old_physical = {r['path']: r for r in original_graph['physicalSources'] if r['path'] not in old_files}
    new_physical = {r['path']: r for r in graph['physicalSources'] if r['path'] not in own_files}
    assert len(new_physical) == 67 and old_physical == new_physical
    old_virtual = {r['id']: r for r in original_graph['virtualSources']}
    new_virtual = {r['id']: r for r in graph['virtualSources']}
    assert len(old_virtual) == len(new_virtual) == 15 and old_virtual == new_virtual
    for row in graph['physicalSources'] + graph['sourceBeforeAfter']:
        regular(Path(row['path']), row['sha256'], row['bytes'])
    assert sha((OWNER / 'evidence/stock.bundle.mjs').read_bytes()) == graph['bundleSha256'] == stock['bundleSha256']
    assert [m for m in graph['modules'] if m.endswith('/stream/scheduler.js')] == [graph['scheduler']]
    process_edges = [r for r in graph['resolutions'] if r['request'] == 'process/']
    assert len(process_edges) == 7 and all(r['result'] == graph['scheduler'] for r in process_edges)
    original_differences = load(OLD, 'first-differences.json')
    assert len(original_differences['rows']) == 28
    future = load(OWNER, 'future-pins.json')
    assert all(future[k] is None for k in ['nativeEngine', 'canonicalEngine', 'stockEngine', 'components']) and future['timingAllowed'] is False
    postseal = indexed(BASE / 'measurement-common-byte-domain-verification-v1', 'd77f5b316945d26070f39fcd4b340feb0ec7001f89e8024a1d14e65e07538218')
    regular(OWNER / 'index.json', EXPECTED)
    result = {
        'schemaVersion': 1, 'state': 'INDEPENDENT_NARROW_COMMON_BYTE_SOURCE_DATA_REVIEW_PASSED',
        'ownerIndex': owner, 'preservedOriginalIndex': old, 'preservedProposedFixIndex': proposal, 'ownerPostsealVerification': postseal,
        'inputClosure': {'sha256': sha(raw), 'files': len(inputs), 'bytes': total, 'toolInputRows': len(tool_inputs), 'allHashesSizesAndToolMembershipMatch': True},
        'sourceDerivation': {'forwardAndReverseExact': True, 'edits': 4, 'changes': ['four separately named scenario IDs', 'source HWM=chunkBytes+1', 'PassThrough HWM=chunkBytes+1', 'sink HWM=chunkBytes+1'], 'allOtherSourceIncludingOnlineBytesChecksumsFullTracesSyncCallbackUnchanged': True},
        'hostSavedDataComparisons': summaries,
        'stockGraph': {'modules': 102, 'imports': [], 'sameProviderModuleIdentities': 99, 'samePhysicalProviderRows': 67, 'sameVirtualRows': 15, 'processEdgesToOneUntouchedStockScheduler': 7, 'providerOptions': {}, 'schedulerOverride': False},
        'originalCounterexampleRowsUnchanged': 28,
        'scopeReview': 'Legitimate separately named HWM-plus-one byte subset; does not erase the original HWM-equal traces or validate installed old canonical, object mode, UTF8/cancellation, shared-private-queue equivalence, or general Streams compatibility.',
        'futureAuthority': {'actualPinsNull': True, 'guestCheckpointBudgetVerified': False, 'timingAllowed': False},
        'blockers': [],
        'limitations': ['Node/proposed/stock results are authenticated saved host evidence, not reviewer reruns.', 'No actual native/canonical/stock component correctness, import audit, 65536 private budget, retained/fresh state, or empirical component-cost gate is proven by this packet.', 'Stock owns a distinct provider graph and queueMicrotask scheduler; no apples-to-apples scheduler claim.', 'Original raw controls must remain separately visible before any timing interpretation.'],
        'reviewerExecuted': {'ownerMains': False, 'nodeWorkload': False, 'bundleOrGenerator': False, 'nativeBuildOrGuestOrTargetHost': False, 'timing': False},
        'runtimeAcceptanceClaim': False
    }
    with (HERE / 'results.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'state': result['state'], 'ownerFiles': 28, 'inputs': len(inputs), 'exactSavedCases': len(summaries), 'blockers': 0}))

if __name__ == '__main__':
    main()
