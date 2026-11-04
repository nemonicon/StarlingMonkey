"""Seal only this owned source/host-evidence packet; no JS/native/guest mains."""
from pathlib import Path
import hashlib
import json
import os

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
EXTERNAL = Path('/tmp/starling-node-compat')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path, expected=None, size=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    assert expected is None or sha(data) == expected, path
    assert size is None or len(data) == size, path
    return data


def first(a, b, path='$'):
    if type(a) is not type(b):
        return {'path': path, 'node': a, 'other': b}
    if isinstance(a, dict):
        if a.keys() != b.keys():
            return {'path': path, 'nodeKeys': list(a), 'otherKeys': list(b)}
        for key in a:
            result = first(a[key], b[key], path+'.'+key)
            if result:
                return result
    elif isinstance(a, list):
        for i, (left, right) in enumerate(zip(a, b)):
            result = first(left, right, path+'['+str(i)+']')
            if result:
                return result
        if len(a) != len(b):
            return {'path': path+'.length', 'node': len(a), 'other': len(b)}
    elif a != b:
        return {'path': path, 'node': a, 'other': b}


def write(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(value if isinstance(value, bytes) else (json.dumps(value, indent=2)+'\n').encode())


def main():
    assert not (HERE / 'index.json').exists()
    node_path = EXTERNAL / 'classic-measurement-workload-node-v4/node-results.json'
    node_bytes = read(node_path)
    node = json.loads(node_bytes)
    for name, digest in node['sourceHashes'].items():
        read(HERE/name, digest)
    stock_path = EXTERNAL / 'classic-measurement-workload-stock-v1/stock-results.json'
    stock_bytes = read(stock_path)
    stock = json.loads(stock_bytes)
    bundle_path = EXTERNAL / 'classic-measurement-workload-bundles-v4/bundle-results.json'
    bundle_bytes = read(bundle_path)
    bundles = json.loads(bundle_bytes)
    assert len(node['expected']) == len(stock['comparisons']) == 20
    assert len(node['canonicalHostCounterexamples']) == len(stock['traceCounterexamples']) == 14
    assert bundles['canonicalFactoryHeaderExact'] and bundles['stockSchedulerOverride'] is False
    assert [len(row['imports']) for row in bundles['reports']] == [6, 4, 0]
    assert len(bundles['sourceInputsCheckedBeforeAfter']) == 407
    units = {'pipeline-view-64': 8192, 'pipeline-copy-64': 8192,
             'pipeline-view-524288': 4194304, 'pipeline-copy-524288': 4194304,
             'fragmented-utf8': 48, 'object-backpressure': 64, 'handled-cancellation': 4,
             'checksum-input-only': 8192, 'byte-input-and-copy-construction-only': 4194304,
             'stream-construction-and-clean-close-only': 0}
    for row in node['expected']:
        value = row['oracle']
        assert value['totalUnits'] == units[row['id']] * row['iterations']
        assert value['unsignedChecksum'] == value['checksum'] % (2**32)
        assert len(value['records']) == row['iterations']
        assert all(record['units'] == units[row['id']] and len(record['events']) <= 4096 and record['callbacks'] <= 128 for record in value['records'])
    differences = []
    for row in node['canonicalHostCounterexamples']:
        oracle = node['expected'][row['oracleIndex']]['oracle']
        assert oracle['unsignedChecksum'] == row['observed']['unsignedChecksum']
        differences.append({'provider': 'canonical-with-real-Node-dependencies-and-nextTick', 'id': row['id'], 'iterations': row['iterations'],
            'oracleIndex': row['oracleIndex'], 'checksum': oracle['unsignedChecksum'], 'firstDifference': first(oracle, row['observed'])})
    for i, row in enumerate(stock['comparisons']):
        assert not row.get('failed') and row['checksumEqual']
        if not row['exactTraceEqual']:
            differences.append({'provider': 'actual-locked-stock-Jco-host-bundle', 'id': row['id'], 'iterations': row['iterations'],
                'oracleIndex': i, 'checksum': node['expected'][i]['oracle']['unsignedChecksum'], 'firstDifference': first(node['expected'][i]['oracle'], row['observed'])})
    old = HERE / 'first-differences.json'
    if old.exists():
        write('history/node-success-v3-before-explicit-encoding/first-differences-original-copy.json', old.read_bytes())
        old.unlink()  # Only replace this owned, unsealed summary; old bytes retained above.
    write('first-differences.json', {'schemaVersion': 1, 'state': 'EXACT_NODE22_HOST_TRACE_COUNTEREXAMPLES_RETAINED_NOT_NORMALIZED',
        'nodeOraclePath': str(node_path), 'nodeOracleSha256': sha(node_bytes), 'stockReportSha256': sha(stock_bytes),
        'canonicalCases': 14, 'stockCases': 14, 'rows': differences, 'actualGuestExecuted': False, 'timingAllowed': False})
    for name, value in [('evidence/node-results.json', node_bytes), ('evidence/stock-results.json', stock_bytes), ('evidence/bundle-results.json', bundle_bytes)]:
        write(name, value)
    sources = []
    for row in bundles['reports']:
        data = read(row['bundlePath'], row['bundleSha256'], row['bundleBytes'])
        write('evidence/bundles/'+row['arm']+'.mjs', data)
        for source in row['physicalSources']:
            read(source['path'], source['sha256'], source['bytes'])
            sources.append(source)
    # Stock execution used the immediately previous source-identical bundle.
    assert stock['bundleSha256'] == next(row for row in bundles['reports'] if row['arm'] == 'stock')['bundleSha256']
    write('evidence/source-test-results.json', read(EXTERNAL / 'classic-measurement-workload-source-checks-v1.json'))
    for prefix in ['classic-measurement-workload-node-v4', 'classic-measurement-workload-bundles-v4', 'classic-measurement-workload-stock-v1']:
        for suffix in ['stdout.log', 'stderr.log']:
            write('evidence/'+prefix+'.'+suffix, read(EXTERNAL / (prefix+'.'+suffix)))
    packages = {}
    tool_root = Path('/tmp/starling-node-compat/native-toolchain-lock/node_modules').resolve()
    for source in sources:
        path = Path(source['path']).resolve()
        if not path.is_relative_to(tool_root):
            continue
        cursor = path.parent
        while cursor.is_relative_to(tool_root) and not (cursor/'package.json').is_file():
            cursor = cursor.parent
        if not (cursor/'package.json').is_file():
            continue
        raw = read(cursor/'package.json')
        package = json.loads(raw)
        notices = []
        for entry in sorted(cursor.iterdir()):
            if entry.is_file() and not entry.is_symlink() and entry.name.lower().startswith(('license', 'licence', 'copying', 'notice')):
                data = read(entry)
                target = 'licenses/'+package['name'].replace('/', '__')+'/'+entry.name
                if not (HERE/target).exists():
                    write(target, data)
                notices.append({'path': str(entry), 'sha256': sha(data), 'bytes': len(data), 'copy': target})
        packages[package['name']] = {'name': package['name'], 'version': package.get('version'), 'license': package.get('license'),
            'metadataPath': str(cursor/'package.json'), 'metadataSha256': sha(raw), 'notices': notices, 'topLevelNoticeMissing': not notices}
    jco = tool_root/'@bytecodealliance/jco/package.json'
    jco_bytes = read(jco)
    packages['@bytecodealliance/jco'] = {'name': '@bytecodealliance/jco', 'version': json.loads(jco_bytes)['version'],
        'license': json.loads(jco_bytes)['license'], 'metadataPath': str(jco), 'metadataSha256': sha(jco_bytes), 'notices': [],
        'topLevelNoticeMissing': True, 'scope': 'Host provider/bundler API; missing top-level license text remains explicit'}
    write('provider-notices.json', {'schemaVersion': 1, 'state': 'ACTUAL_REACHABLE_STOCK_PROVIDER_METADATA_AND_NOTICE_FILES', 'packages': sorted(packages.values(), key=lambda row: row['name'])})
    rows = {}
    def add(path, expected=None, size=None, role='consumed-source-or-host-evidence'):
        path = Path(path).resolve()
        data = read(path, expected, size)
        key = os.path.relpath(path, HERE)
        row = {'path': key, 'sha256': sha(data), 'bytes': len(data), 'role': role}
        if key in rows:
            assert rows[key]['sha256'] == row['sha256'] and rows[key]['bytes'] == row['bytes']
        rows[key] = row
    extension = BASE / 'measurement-extension-candidate-v1'
    index_bytes = read(extension/'index.json', '69d61ebd61a93d5c34f56b4c4d2fd5d0988b07495ce5636df102a543a036d0aa')
    add(extension/'index.json')
    for row in json.loads(index_bytes)['files']:
        add(extension/row['path'], row['sha256'], row['bytes'])
    extension_manifest = read(extension/'input-freeze.json', 'ffaa680b9e30eb26499c335e041ba650f384866ae7d11792a7d4ebcb0df8519b')
    for row in json.loads(extension_manifest)['inputs']:
        add(extension/row['path'], row['sha256'], row['bytes'], 'parent342-extension-source-ancestry')
    tools = json.loads(read(HERE/'tool-inputs.json'))
    for row in tools['inputs']:
        add(row['path'], row['sha256'], row['bytes'], 'pinned-existing-host-tool-or-provider-file')
    for package in packages.values():
        add(package['metadataPath'], package['metadataSha256'], role='actual-provider-package-metadata')
        for notice in package['notices']:
            add(notice['path'], notice['sha256'], notice['bytes'], 'actual-provider-notice')
    for row in sources:
        add(row['path'], row['sha256'], row['bytes'], 'actual-bundled-reachable-physical-source')
    for path in sorted(HERE.rglob('*')):
        if path.is_file():
            add(path)
    write('input-freeze.json', {'schemaVersion': 1, 'state': 'CLASSIC_MEASUREMENT_WORKLOAD_SOURCE_HOST_EVIDENCE_INPUTS_ONLY',
        'inputs': sorted(rows.values(), key=lambda row: row['path']), 'guestOrNativeOrTargetHostOrTimingExecuted': False})
    write('source-receipt.json', {'schemaVersion': 1, 'state': 'SOURCE_AND_NODE_HOST_WORKLOAD_ORACLES_CAPTURED_COUNTEREXAMPLES_BLOCK_TIMING',
        'nodeVersion': '22.14.0', 'nodeExecutableSha256': node['nodeExecutableSha256'],
        'ordinaryScenarios': 7, 'rawControls': 3, 'iterationBounds': [1, 16], 'nodeCases': 20,
        'canonicalExactOutputAndChecksumCases': 20, 'canonicalTraceCounterexamples': 14, 'stockExactChecksumCases': 20, 'stockTraceCounterexamples': 14,
        'sourceContractChecks': 16, 'bundleGraphs': 3, 'bundleModuleCounts': [len(row['moduleIds']) for row in bundles['reports']],
        'canonicalFactoryHeaderExact': True, 'actualStockResolverAndReachableGraph': True, 'schedulerOverride': False,
        'sourceInputSha256': sha(read(HERE/'input-freeze.json')), 'sourceInputFiles': len(rows), 'futureNativeAndComponentPins': None,
        'actualGuestBudgetVerified': False, 'checkpointLimit': 65536, 'checkpointLimitRaised': False,
        'guestOrComponentOrNativeOrTargetHostExecuted': False, 'timingExecuted': False, 'timingAllowed': False,
        'failedHostAttemptsPreserved': 2, 'live342OrStockSchedulerChanged': False,
        'scope': 'Ordinary Node host/source observations only; no new native, component, portability, snapshot, reset, GC or performance evidence.'})
    indexed = []
    for path in sorted(HERE.rglob('*')):
        if path.is_file():
            data = read(path)
            indexed.append({'path': str(path.relative_to(HERE)), 'sha256': sha(data), 'bytes': len(data)})
    write('index.json', {'schemaVersion': 1, 'state': 'SEALED_CLASSIC_WORKLOAD_SOURCE_AND_NODE_HOST_COUNTEREXAMPLES_NO_TIMING', 'files': indexed})
    print(json.dumps({'indexSha256': sha(read(HERE/'index.json')), 'files': len(indexed), 'inputFiles': len(rows), 'timingAllowed': False}))


if __name__ == '__main__':
    main()
