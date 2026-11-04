#!/usr/bin/env python3
"""Prepare an exclusive PENDING archive. Root acceptance is a separate action.

Uses the nonsymlink, binary-source whitelist, before/after hash and atomic-stage
copy pattern of accept-v11.py. No compiler, tool, oracle, application or host runs.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TESTS = REPO / 'tests/node-compat'
PACKETS = TESTS / 'foundation-scheduler'
PARENT = TESTS / 'milestones/foundations-v11'
DESTINATION = TESTS / 'milestones/foundations-v12'
STAGE = DESTINATION.with_name('.foundations-v12-pending-staging')
EXTERNAL = Path('/tmp/starling-node-compat').resolve()
PROD = EXTERNAL / 'production-scheduler-artifacts-v1/native-freeze'
DIAG = EXTERNAL / 'foundation-scheduler-link1-v1/native-freeze'
RUNTIME = EXTERNAL / 'production-scheduler-runtime-v1'
RECIPE = '869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173'
BINARY_SUFFIXES = {'.wasm', '.cwasm', '.o', '.obj', '.a', '.so', '.dylib', '.exe', '.pyc', '.zip', '.gz', '.tar', '.bin'}
plan, omitted, references, source_maps, packet_refs, report_refs = {}, [], {}, [], [], []


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def regular(path):
    info = Path(path).lstat()
    assert stat.S_ISREG(info.st_mode) and not stat.S_ISLNK(info.st_mode), path
    return info


def check(path, expected=None, size=None):
    path = Path(path)
    info = regular(path)
    digest = sha(path)
    if expected is not None:
        assert digest == expected, path
    if size is not None:
        assert info.st_size == size, path
    return digest, info.st_size


def load(path, expected=None):
    check(path, expected)
    return json.loads(Path(path).read_bytes())


def no_links(path, root):
    path, root = Path(path), Path(root)
    relative = path.relative_to(root)
    cursor = root
    assert not cursor.is_symlink(), root
    for part in relative.parts:
        cursor /= part
        assert not cursor.is_symlink(), cursor


def binary(path):
    if path.suffix.lower() in BINARY_SUFFIXES:
        return True
    data = path.read_bytes()
    if b'\0' in data:
        return True
    try:
        data.decode('utf-8')
    except UnicodeDecodeError:
        return True
    return False


def add(source, destination, expected=None, size=None, native_asset=None, role='text-evidence'):
    source = Path(source)
    destination = PurePosixPath(destination)
    assert not destination.is_absolute() and '..' not in destination.parts
    digest, count = check(source, expected, size)
    if binary(source):
        if native_asset is None:
            references[str(source)] = {'path': str(source), 'sha256': digest, 'bytes': count,
                                       'role': role, 'binaryBytesCopied': False}
            return None
        assert native_asset in ASSETS and digest == ASSETS[native_asset]
        assert str(destination) == 'source/' + native_asset
    row = {'source': str(source), 'destination': str(destination), 'sha256': digest,
           'bytes': count, 'role': role, 'requiredNativeBinarySourceAsset': native_asset}
    if str(destination) in plan:
        assert plan[str(destination)]['sha256'] == digest, ('Destination collision', destination)
    else:
        plan[str(destination)] = row
    return str(destination)


def tree(root, target, role):
    root = Path(root)
    assert root.is_dir() and not root.is_symlink(), root
    for parent, dirs, names in os.walk(root, followlinks=False):
        retained = []
        for name in sorted(dirs):
            path = Path(parent) / name
            if path.is_symlink() or name in ['node_modules', '.git', 'target', '__pycache__']:
                omitted.append({'path': str(path), 'reason': 'symlink-or-generated-dependency-directory'})
            else:
                retained.append(name)
        dirs[:] = retained
        for name in sorted(names):
            path = Path(parent) / name
            if path.is_symlink() or not path.is_file():
                omitted.append({'path': str(path), 'reason': 'not-regular-nonsymlink'})
            else:
                add(path, str(PurePosixPath(target) / path.relative_to(root).as_posix()), role=role)


def packet(name, expected):
    base = PACKETS / name
    index = load(base / 'index.json', expected)
    for row in index['files']:
        relative = PurePosixPath(row['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        no_links(base / row['path'], base)
        add(base / row['path'], 'packets/' + name + '/' + row['path'], row['sha256'], row['bytes'], role='exact-indexed-packet-text')
    add(base / 'index.json', 'packets/' + name + '/index.json', expected, role='exact-packet-index')
    packet_refs.append({'packet': name, 'indexSha256': expected, 'indexedFiles': len(index['files'])})


def consumed_source(path, digest, size, role):
    """Only a finite manifest/index row grants per-file copy permission."""
    path = Path(path).resolve()
    check(path, digest, size)
    if path.is_relative_to(REPO):
        relative = path.relative_to(REPO).as_posix()
        if relative in NATIVE and NATIVE[relative] == digest:
            destination = 'source/' + relative
        else:
            destination = add(path, 'harness/repository/' + relative, digest, size, role=role)
    elif path.is_relative_to(PROD):
        relative = path.relative_to(PROD).as_posix()
        destination = add(path, 'native-freeze/' + relative, digest, size, role=role)
    elif path.is_relative_to(DIAG):
        relative = path.relative_to(DIAG).as_posix()
        destination = add(path, 'diagnostic-native-freeze/' + relative, digest, size, role=role)
    elif any(path.is_relative_to(EXTERNAL / ('foundations-v' + str(v) + '/native-freeze')) for v in [5, 6, 7, 10]):
        relative = path.relative_to(EXTERNAL).as_posix()
        destination = add(path, 'historical-controls/' + relative, digest, size, role=role)
    elif path == EXTERNAL / 'native-toolchain-lock/node_modules/readable-stream/lib/internal/streams/buffer_list.js':
        destination = add(path, 'external-source-provenance/readable-stream/buffer_list.js', digest, size, role='caller-demand-source-data-not-stream-compatibility')
    elif path.is_relative_to(RUNTIME):
        destination = add(path, 'generated-text/' + path.relative_to(RUNTIME).as_posix(), digest, size, role=role)
    else:
        # Known host/tool/runtime binaries are hash references, never copy permission.
        if binary(path):
            destination = add(path, 'unused-binary-placeholder', digest, size, role=role)
        else:
            raise AssertionError(('Unclassified finite text witness', path, role))
    source_maps.append({'original': str(path), 'sha256': digest, 'bytes': size,
                        'archivePath': destination, 'role': role,
                        'referenceOnly': destination is None})


def main():
    global ASSETS, NATIVE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-pending', action='store_true')
    parser.add_argument('--expected-plan')
    args = parser.parse_args()
    assert not DESTINATION.exists() and not STAGE.exists(), 'Never overwrite an archive or failed stage'
    pins = load(HERE / 'pins.json')
    ASSETS = pins['requiredSourceBinaryAssets']
    parent = load(PARENT / 'results.json', pins['parentV11ResultsSha256'])
    assert ASSETS == parent['sourceBinaryAssets'] and len(ASSETS) == 5
    for row in parent['copiedEvidence']:
        no_links(PARENT / row['path'], PARENT)
        check(PARENT / row['path'], row['sha256'], row['bytes'])
    parent_reference = {'path': '../foundations-v11/results.json', 'sha256': pins['parentV11ResultsSha256'],
                        'copiedEvidenceFilesRehashed': len(parent['copiedEvidence']),
                        'historicalNotNewRuntimeEvidence': True}

    metadata = load(PROD / 'normal-off.engine.wasm.build.json')
    NATIVE = {row['path']: row['sha256'] for row in metadata['sourceManifest']}
    assert len(NATIVE) == 306 and sha(TESTS / 'build-engine.sh') == RECIPE
    for path, digest in NATIVE.items():
        no_links(PROD / 'source' / path, PROD / 'source')
        check(REPO / path, digest)
        add(PROD / 'source' / path, 'source/' + path, digest, native_asset=path if path in ASSETS else None, role='current-compiled-native-source')
    engines = {}
    for label in ['normal-off', 'normal-runtime', 'gc-off']:
        receipt_path = PROD / (label + '-freeze-receipt.json')
        receipt = load(receipt_path)
        current = load(PROD / (label + '.engine.wasm.build.json'), receipt['receiptSha256'])
        assert current['sourceManifest'] == metadata['sourceManifest']
        assert current['componentizeSourceManifest'] == metadata['componentizeSourceManifest']
        assert current['buildRecipeSha256'] == RECIPE and current['gcStress'] == (label == 'gc-off')
        assert current['entropyPolicy'] == ('runtime-only' if label == 'normal-runtime' else 'off')
        assert current['internalTicksEnabled'] and not current.get('diagnosticOnly', False)
        assert len(receipt['copies']) == 335
        for row in receipt['copies']:
            path = Path(row['path']).resolve();no_links(path, PROD);check(path, row['sha256'], row['bytes'])
            relative = path.relative_to(PROD).as_posix()
            if relative.startswith('source/'):
                source_path = relative[len('source/'):]
                if source_path not in NATIVE:
                    add(path, relative, row['sha256'], row['bytes'], role='native-attribution-text')
            else:
                add(path, 'native-freeze/' + relative, row['sha256'], row['bytes'], role='actual-frozen-native-configuration-or-binary-reference')
        add(receipt_path, 'native-freeze/' + receipt_path.name, role='original-production-freeze-receipt')
        engines[label] = {'path': receipt['engine'], 'sha256': receipt['engineSha256'], 'bytes': receipt['engineBytes'],
                          'metadataSha256': receipt['receiptSha256'], 'freezeReceiptSha256': sha(receipt_path),
                          'gcStress': current['gcStress'], 'entropyPolicy': current['entropyPolicy'], 'nativeInputs': 306,
                          'externalEmbeddingInputs': 3, 'frozenInventoryEntries': 335}

    diagnostic = {}
    for label in ['diagnostic-release', 'diagnostic-gc']:
        receipt_path = DIAG / (label + '-freeze-receipt.json')
        receipt = load(receipt_path)
        current = load(DIAG / (label + '.engine.wasm.build.json'), receipt['metadataSha256'])
        assert current['sourceManifest'] == metadata['sourceManifest']
        assert current['componentizeSourceManifest'] == metadata['componentizeSourceManifest']
        assert current['diagnosticOnly'] is True and len(current['internalTickDiagnosticPolicy']['sourceManifest']) == 2
        assert receipt['sourcePartitions'] == [306, 2] and len(receipt['copies']) == 345
        for row in receipt['copies']:
            path = Path(row['path']).resolve();no_links(path, DIAG);check(path, row['sha256'], row['bytes'])
            relative = path.relative_to(DIAG).as_posix()
            if relative.startswith('source/'):
                source_path = relative[len('source/'):]
                if source_path in NATIVE:
                    assert NATIVE[source_path] == row['sha256']
                else:
                    add(path, 'diagnostic-source/' + source_path, row['sha256'], row['bytes'], role='diagnostic-only-extra-source')
            else:
                add(path, 'diagnostic-native-freeze/' + relative, row['sha256'], row['bytes'], role='diagnostic-configuration-or-external-binary-reference')
        add(receipt_path, 'diagnostic-native-freeze/' + receipt_path.name, role='original-diagnostic-freeze-receipt')
        diagnostic[label] = {'path': receipt['engine'], 'sha256': receipt['engineSha256'], 'bytes': receipt['engineBytes'],
                             'metadataSha256': receipt['metadataSha256'], 'freezeReceiptSha256': sha(receipt_path),
                             'sourcePartitions': [306, 2], 'productionAdmission': False}

    for name, digest in pins['packets'].items():
        packet(name, digest)
    # Complete tested local closure, including computed fixtures/aliases/oracles.
    for name, count in [('production-regression-candidate-v5', 667), ('production-followon-off-v3', 755),
                        ('production-release-runner-v3', 1442), ('production-followon-capability-v3', 778),
                        ('diagnostic-link1-driver-v2', 32)]:
        base = PACKETS / name
        manifest = load(base / 'input-freeze.json')
        assert len(manifest['inputs']) == count
        for row in manifest['inputs']:
            consumed_source(base / row['path'], row['sha256'], row['bytes'], name + '-consumed-input')

    runtime_root = PACKETS / 'production-runtime-v1'
    tree(runtime_root, 'runtime-root-receipts', 'completed-root-runtime-record')
    production_verification = load(PACKETS / 'production-runtime-verification-v1/results.json')
    focused_verification = load(PACKETS / 'production-focused-runtime-verification-v1/results.json')
    http = load(runtime_root / 'http-final-results.json', '99a8799a1649285d5d544dc63d9a1dc046fc32e8fb3d90a1a9ee151740b6d1fe')
    load(runtime_root / 'http-final-root-results.json', pins['httpFinalRootResultsSha256'])
    post_http = load(PACKETS / 'production-http-posthost-verification-v1/results.json', pins['httpPostHostResultsSha256'])
    assert production_verification['actualComponents'] == 40 and production_verification['currentProductionEngineComponents'] == 39
    assert focused_verification['actualComponents'] == 20 and focused_verification['nodeCompatibilityPassed'] is False
    assert post_http['componentSha256'] == http['component']['sha256'] == 'ccc87ae3f9a00195ae243fa1077a07f9cd68e5ad3a8220708400187eee7a2ba6'
    assert post_http['sameComponentBytesOnBothHosts'] is True and post_http['clockBinaryAndTypeGraphDurationOnlyU64'] is True
    for row in post_http['verifiedFiles']:
        consumed_source(row['path'], row['sha256'], row['bytes'], 'http-posthost-checked-input-or-artifact')
    for row in http['artifacts']:
        consumed_source(row['path'], row['sha256'], row['bytes'], 'http-exact-final-artifact')
    # Completed generated text, source bodies and host configuration; no app Wasm.
    tree(RUNTIME, 'generated-text', 'completed-production-runtime-generated-text')
    link_summary = load(PACKETS / 'link1-execution-v1/execution-summary.json')
    assert len(link_summary['variants']) == 2 and sum(row['components'] for row in link_summary['variants']) == 20
    for row in link_summary['variants']:
        load(row['componentReportPath'], row['componentReportSha256'])
    # Actual external BufferList was used only as pinned caller-demand excerpts.
    package = EXTERNAL / 'native-toolchain-lock/node_modules/readable-stream'
    for name in ['package.json', 'LICENSE']:
        add(package / name, 'external-source-provenance/readable-stream/' + name, role='caller-package-license-and-version')
    for name in ['package.json', 'package-lock.json']:
        add(TESTS / 'toolchain' / name, 'toolchain/' + name, role='pinned-host-toolchain-dependency-lock')
    tree(REPO / 'docs/node-compat', 'docs/node-compat', 'original-and-current-architecture-contract-documents')
    add(REPO / 'docs/src/developer/node-compat.md', 'docs/developer-node-compat.md')
    add(REPO / 'progress.md', 'docs/progress.md', role='tracker-snapshot-before-acceptance')
    add(REPO / 'LICENSE', 'LICENSE')
    for path in HERE.iterdir():
        if path.is_file():
            add(path, 'archive-preparation/' + path.name, role='pending-archive-producer-and-actual-pins')
    assert sum('source/' + path in plan for path in NATIVE) == 306
    assert sum(row['requiredNativeBinarySourceAsset'] is not None for row in plan.values()) == 5
    prior_native = {row['path']: row['sha256'] for row in load(PARENT / 'off-foundations.engine.wasm.build.json')['sourceManifest']}
    ancestry = {'unchanged': sum(prior_native.get(path) == digest for path, digest in NATIVE.items()),
                'changed': [{'path': path, 'before': prior_native[path], 'after': digest} for path, digest in NATIVE.items() if path in prior_native and prior_native[path] != digest],
                'added': [path for path in NATIVE if path not in prior_native], 'removed': [path for path in prior_native if path not in NATIVE]}
    assert ancestry['unchanged'] == 299 and len(ancestry['changed']) == 5 and len(ancestry['added']) == 2 and not ancestry['removed']
    ordered = [plan[key] for key in sorted(plan)]
    plan_sha = hashlib.sha256(json.dumps(ordered, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    summary = {'state': 'VALIDATED_V12_PENDING_COPY_PLAN_NOT_ACCEPTED', 'planSha256': plan_sha, 'files': len(ordered),
               'bytes': sum(row['bytes'] for row in ordered), 'nativeInputs': 306, 'externalEmbeddingInputs': 3,
               'currentProductionEngines': 3, 'privateDiagnosticEngines': 2, 'requiredNativeBinarySourceAssets': 5}
    if not args.prepare_pending:
        print(json.dumps(summary, indent=2))
        return
    assert args.expected_plan == plan_sha, 'Exact read-only plan digest required'
    STAGE.mkdir(parents=True)
    copied = []
    for row in ordered:
        source, target = Path(row['source']), STAGE / row['destination']
        check(source, row['sha256'], row['bytes'])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target, follow_symlinks=False)
        check(target, row['sha256'], row['bytes'])
        copied.append({'path': row['destination'], 'sha256': row['sha256'], 'bytes': row['bytes'],
                       'original': row['source'], 'role': row['role']})
    for path, digest in NATIVE.items():
        check(STAGE / 'source' / path, digest);check(REPO / path, digest)
    for row in copied:
        check(STAGE / row['path'], row['sha256'], row['bytes'])
    result = {'schema': 1, 'state': 'pending-root-acceptance-bounded-foundations-v12', 'pendingAcceptance': True,
              'accepted': False, 'preparedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'nodeVersion': 'v22.14.0', 'coreVersion': 'sm-node-22.14.0-m0.11', 'eventsVersion': 'sm-node-22.14.0-m0.10',
              'publicAPIVersionsAdvancedByCheckpoint': False, 'privateTicksDefaultOn': False,
              'publicNextTickProcessOrALSProvided': False, 'currentEngines': engines, 'privateDiagnosticEngines': diagnostic,
              'identicalCurrentNativeInputs': 306, 'externalEmbeddingInputs': 3, 'nativeAncestryFromV11': ancestry,
              'parentReference': parent_reference, 'recipeSha256': RECIPE, 'readOnlyPlanSha256': plan_sha,
              'productionAndControlApplications': 61, 'currentProductionApplications': 60, 'historicalControlApplications': 1,
              'diagnosticApplicationsSeparateFromProduction': 20, 'totalApplicationsIncludingDiagnostics': 81,
              'freshOffSerialJobs': 8, 'optionalFoundations': 6, 'sameEnginePriorPassReuse': 0,
              'nodeCallbackReturnParity': False, 'callbackReturnCounterexample': {'node': [1, 1, 0], 'native': [0, 0, 0]},
              'nodeSymbolDisposeRegistryParity': False, 'prototypeOnlySymbolRootingProved': False,
              'queueExclusiveVMOwnershipProved': False, 'explicitEngineResetProved': False,
              'httpComponentSha256': post_http['componentSha256'], 'httpComponentBytes': post_http['componentBytes'],
              'emittedHTTPImports': post_http['binaryImports'], 'httpRequestsEachHost': 3,
              'clockTypeOnly': True, 'sameInstanceHTTPReuseEstablished': False, 'performanceTransferred': False,
              'sourceBinaryAssets': ASSETS, 'generatedEngineOrApplicationBinariesCopied': False,
              'packetReferences': packet_refs, 'copiedEvidence': copied, 'finiteInputMappings': source_maps,
              'externalBinaryReferences': list(references.values()), 'omittedPaths': omitted,
              'limitations': ['Complete Node/Buffer/EventTarget/stream/process compatibility is not claimed.',
                  'Getter parity is false; only ordinary returned-object getters, not throwing/rejecting thenables, were observed.',
                  'Symbol.dispose registry identity differs; GC combines owners and does not isolate prototype-only symbol or VM-temporary liveness.',
                  'Fatal instances are discarded; Engine reset, ALS/AsyncResource and request teardown remain unproved.',
                  'Configured classic and appended INIT diagnostic probes do not prove first-ever startup priority.',
                  'Diagnostic engines/modules are rejected by production admission and are not public process APIs.',
                  'HTTP counters1/1/1 do not prove reuse/isolation; the monotonic-clock dependency is type-only.',
                  'No outgoing HTTP, filesystem, DNS, sockets, TLS, process behavior or current performance advantage follows.',
                  'No compiler, guest, oracle, packager or host was executed by archive preparation.']}
    (STAGE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    (STAGE / 'README.md').write_text('# Foundations v12 — PENDING ROOT ACCEPTANCE\n\n'
        'This complete evidence archive is UNACCEPTED. Root must independently rehash its index and record any acceptance. '
        'Three production306 engines and two private diagnostic306+2 engines remain distinct. '
        'Fresh production/control applications total61 (60 current+1 historical), with20 diagnostic applications separate. '
        'Public module versions remain corem0.11/Eventsm0.10; private ticks defaultOFF and no public process.nextTick/ALS API is provided.\n\n'
        'Known getter parity remains FALSE (Node1/1/0 vsnative0/0/0); disposal-symbol registry identity differs. '
        'GC/queue ownership, reset, failure-discard and lifecycle limits remain explicit in results.json and the copied verification packets. '
        'Same HTTP component ccc87ae3... passed3requests perstockhost; counters1/1/1 do not establish reuse. '
        'Six standard0.2.10 dependencies include a type-only clock and selected random. No performance claim is transferred.\n\n'
        'All306 current native inputs, separate embedding3, exact configurations/licenses/dependency receipts, tested harness/input closures, '
        'raw source/log/report/host configuration evidence and immutable packet references are copied with hashes. '
        'Engines/components/cores/libraries remain external; only five exact versioned host-API binary SOURCE assets are included. '
        'The v11 archive is rehashed as parent and unchanged. This preparation executes no application or host.\n')
    rows = []
    for path in sorted(STAGE.rglob('*')):
        assert not path.is_symlink(), path
        if path.is_file():
            rows.append({'path': path.relative_to(STAGE).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size})
    (STAGE / 'index.json').write_text(json.dumps({'schemaVersion': 1, 'state': 'PENDING_ROOT_ACCEPTANCE_COMPLETE_V12_COPY_INDEX',
        'pendingAcceptance': True, 'accepted': False, 'files': rows}, indent=2) + '\n')
    for row in rows:
        check(STAGE / row['path'], row['sha256'], row['bytes'])
    STAGE.rename(DESTINATION)
    print(json.dumps({**summary, 'state': result['state'], 'archive': str(DESTINATION),
                      'resultsSha256': sha(DESTINATION / 'results.json'), 'indexSha256': sha(DESTINATION / 'index.json')}, indent=2))


if __name__ == '__main__':
    main()
