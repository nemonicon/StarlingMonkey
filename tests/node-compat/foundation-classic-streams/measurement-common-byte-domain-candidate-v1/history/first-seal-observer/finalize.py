"""Read/seal this finite source/Node-host proposal only; no target execution."""
from pathlib import Path
import hashlib
import json
import os

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path, expected=None, size=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    assert expected is None or sha(data) == expected, path
    assert size is None or len(data) == size, path
    return data


def put(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(value if isinstance(value, bytes) else (json.dumps(value, indent=2)+'\n').encode())


def main():
    baseline = BASE / 'measurement-workload-candidate-v1'
    proof = json.loads(read(HERE/'derivation.json'))
    before = read(baseline/'workload.mjs', proof['beforeSha256']).decode()
    after = before
    assert len(proof['edits']) == 4
    for edit in proof['edits']:
        assert after.count(edit['old']) == edit['count'] == 1
        after = after.replace(edit['old'], edit['new'])
    assert after.encode() == read(HERE/'workload.mjs', proof['afterSha256'])
    for edit in reversed(proof['edits']):
        assert after.count(edit['new']) == 1
        after = after.replace(edit['new'], edit['old'])
    assert after == before
    for name in ['node-provider.mjs', 'stock-provider.mjs']:
        assert read(HERE/name) == read(baseline/name)
    root = Path('/tmp/starling-node-compat')
    paths = {
        'node': root/'classic-common-byte-node-v1/node-results.json',
        'stock': root/'classic-common-byte-stock-v1/stock-results.json',
        'bundle': root/'classic-common-byte-bundle-v1/bundle-results.json'}
    node, stock, graph = [json.loads(read(paths[key])) for key in ['node', 'stock', 'bundle']]
    assert node['sourceSha256'] == proof['afterSha256']
    assert len(node['cases']) == len(stock['cases']) == 8
    assert [row['iterations'] for row in node['cases']] == [1, 16]*4
    old_node = json.loads(read(baseline/'evidence/node-results.json'))
    old_oracles = {(row['id'], row['iterations']): row['oracle'] for row in old_node['expected']}
    for a, b in zip(node['cases'], stock['cases']):
        assert a['expected'] == a['proposed'] == b['expected'] == b['observed']
        assert a['proposedExact'] and b['checksumEqual'] and b['traceExact']
        old = old_oracles[(a['id'].removesuffix('-hwm-plus1'), a['iterations'])]
        assert old['unsignedChecksum'] == a['expected']['unsignedChecksum']
        assert old['totalUnits'] == a['expected']['totalUnits']
        assert all(all(record['returns']) for record in a['expected']['records'])
    assert len(graph['modules']) == 102 and graph['imports'] == [] and graph['schedulerOverride'] is False and graph['providerOptions'] == {}
    old_graph = json.loads(read(baseline/'evidence/bundle-results.json'))['reports'][2]
    old_files = {str(baseline/name) for name in ['entry.mjs', 'workload.mjs', 'stock-provider.mjs']}
    new_files = {str(HERE/name) for name in ['entry.mjs', 'workload.mjs', 'stock-provider.mjs']}
    old_modules = set(old_graph['moduleIds']) - old_files
    new_modules = set(graph['modules']) - new_files
    assert old_modules == new_modules and len(old_modules) == 99
    old_physical = {row['path']: row for row in old_graph['physicalSources'] if row['path'] not in old_files}
    new_physical = {row['path']: row for row in graph['physicalSources'] if row['path'] not in new_files}
    assert old_physical == new_physical
    assert old_graph['virtualSources'] == graph['virtualSources']
    scheduler_ids = [value for value in graph['modules'] if value.endswith('/stream/scheduler.js')]
    assert scheduler_ids == [graph['scheduler']]
    process_edges = [row for row in graph['resolutions'] if row['request'] == 'process/']
    assert len(process_edges) == 7 and all(row['result'] == graph['scheduler'] for row in process_edges)
    put('stock-subgraph-identity.json', {'schemaVersion': 1, 'state': 'UNCHANGED_STOCK_PROVIDER_SUBGRAPH_EXCLUDING_EXPLICIT_WORKLOAD_FILES',
        'unchangedModuleIdentities': 99, 'physicalProviderSources': len(new_physical), 'virtualSourceIdentitiesAndBytesUnchanged': True,
        'explicitPathDifferencesOnly': {'old': sorted(old_files), 'new': sorted(new_files)},
        'schedulerIdentities': scheduler_ids, 'readableStreamProcessEdges': process_edges})
    for key, path in paths.items():
        put('evidence/'+key+'-results.json', read(path))
    put('evidence/stock.bundle.mjs', read(graph['bundlePath'], graph['bundleSha256']))
    for prefix in ['classic-common-byte-node-v1', 'classic-common-byte-bundle-v1', 'classic-common-byte-stock-v1']:
        for suffix in ['stdout.log', 'stderr.log']:
            put('evidence/'+prefix+'.'+suffix, read(root/(prefix+'.'+suffix)))
    rows = {}
    def add(path, expected=None, size=None):
        path = Path(path).resolve()
        data = read(path, expected, size)
        key = os.path.relpath(path, HERE)
        row = {'path': key, 'sha256': sha(data), 'bytes': len(data)}
        assert key not in rows or rows[key] == row
        rows[key] = row
    parents = [('measurement-workload-candidate-v1', '39774bbadae98f70e777edb8801ed0ea70d50430f7193f0f4a7fce3630cca41c'),
               ('trace-semantics-candidate-v1', '59c9233c5dd1c9f07c4da16a79abdb58abc9775b37c714f6af179e85f23f0631')]
    for name, expected in parents:
        directory = BASE/name
        index_bytes = read(directory/'index.json', expected)
        add(directory/'index.json', expected)
        for row in json.loads(index_bytes)['files']:
            add(directory/row['path'], row['sha256'], row['bytes'])
        for row in json.loads(read(directory/'input-freeze.json'))['inputs']:
            add(directory/row['path'], row['sha256'], row['bytes'])
    for row in graph['physicalSources'] + graph['sourceBeforeAfter']:
        add(row['path'], row['sha256'], row['bytes'])
    for path in paths.values():
        add(path)
    for path in sorted(HERE.rglob('*')):
        if path.is_file():
            add(path)
    put('input-freeze.json', {'schemaVersion': 1, 'state': 'NEW_NARROW_COMMON_BYTE_SOURCE_HOST_EVIDENCE_ONLY', 'inputs': sorted(rows.values(), key=lambda row: row['path'])})
    put('source-receipt.json', {'schemaVersion': 1, 'state': 'NARROW_NODE_HOST_COMMON_DOMAIN_PROPOSED_NOT_TIMING_AUTHORITY',
        'parametersExplored': ['source/pass/sink HWM=chunkBytes+1; original synchronous completion'],
        'newByteScenarioIds': proof['newIds'], 'iterations': [1, 16], 'nodeProposedStockExactCases': 8,
        'onlineExactBytesAndFullTraces': True, 'stockProviderAndSchedulerUnchanged': True,
        'original39774AndAll28CounterexamplesUnchanged': True, 'live342AndNativePinsUnchanged': True,
        'sourceReverseEdits': 4, 'stockBundleImports': [], 'stockProviderModuleIdentitiesUnchanged': 99,
        'futureEngineAndComponentPins': None, 'actualComponentCorrectnessRequiredBeforeTiming': True,
        'checkpointBudget': 65536, 'budgetRaised': False, 'actualGuestBudgetVerified': False,
        'guestOrNativeOrTargetHostOrComponentizerExecuted': False, 'timingPerformed': False, 'timingAllowed': False,
        'sourceInputSha256': sha(read(HERE/'input-freeze.json')), 'sourceInputFiles': len(rows)})
    files = []
    for path in sorted(HERE.rglob('*')):
        if path.is_file():
            data = read(path)
            files.append({'path': str(path.relative_to(HERE)), 'sha256': sha(data), 'bytes': len(data)})
    put('index.json', {'schemaVersion': 1, 'state': 'SEALED_SOURCE_ONLY_NARROW_BYTE_COMMON_DOMAIN_HOST_PROPOSAL', 'files': files})
    print(json.dumps({'indexSha256': sha(read(HERE/'index.json')), 'files': len(files), 'inputs': len(rows), 'exactCases': 8, 'timingAllowed': False}))


if __name__ == '__main__':
    main()
