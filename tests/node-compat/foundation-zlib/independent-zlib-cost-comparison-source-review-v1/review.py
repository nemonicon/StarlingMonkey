"""Independent bounded source/data review; no codec, library or owner imports."""
from pathlib import Path
import ast
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'cost-comparison-candidate-v1'
ROOT = HERE.parents[3]
EXPECTED = 'e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8'
checked = []

def sha(value):
    return hashlib.sha256(value).hexdigest()

def load(path):
    return json.loads(Path(path).read_text())

def verify(path, expected, size, role, canonical=None):
    path = Path(path)
    assert path.is_file(), str(path)
    raw = path.read_bytes()
    assert sha(raw) == expected and len(raw) == size, str(path)
    if canonical:
        assert str(path.resolve()) == canonical
    checked.append({'path': str(path), 'sha256': expected, 'bytes': size, 'role': role})
    return raw

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')

def cite(name, needle):
    path = SOURCE / name
    value = path.read_text()
    assert needle in value
    return {'path': str(path), 'sha256': sha(path.read_bytes()),
            'line': value[:value.index(needle)].count('\n') + 1, 'text': needle}

assert sha((SOURCE / 'index.json').read_bytes()) == EXPECTED
index = load(SOURCE / 'index.json')
assert len(index['files']) == 83 and len({r['path'] for r in index['files']}) == 83
for row in index['files']:
    assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
    assert not (SOURCE / row['path']).is_symlink()
    verify(SOURCE / row['path'], row['sha256'], row['bytes'], 'sealed-source')
manifest = load(SOURCE / 'input-freeze.json')
assert sha((SOURCE / 'input-freeze.json').read_bytes()) == '4c02c8a86b5b3fdf83a4b49e9f8cf3b93626a600cb70e9de5318f296c17a58e4'
assert len(manifest['inputs']) == 401 and len({r['path'] for r in manifest['inputs']}) == 401
for row in manifest['inputs']:
    assert Path(row['path']).is_absolute()
    verify(row['path'], row['sha256'], row['bytes'], 'original-source-input', row['canonicalPath'])
assert manifest['actualFuturePackagingPhysicalClosure'] is None
assert manifest['ownerHelpersInvoked'] is False and manifest['codecOrLibraryInvoked'] is False

tool = Path('/tmp/starling-node-compat/native-toolchain-lock')
package = load(tool / 'node_modules/fflate/package.json')
assert package['version'] == '0.8.3'
assert package['exports']['./browser']['import']['default'] == './esm/browser.js'
assert package['exports']['.']['node']['import']['default'] == './esm/index.mjs'
browser_path = tool / 'node_modules/fflate/esm/browser.js'
browser = browser_path.read_text()
inspection = load(SOURCE / 'fflate-source-inspection.json')
assert sha(browser_path.read_bytes()) == inspection['browserEntry']['sha256'] == 'b7ca4450b19559a1d50eb381adcee94b82449674be4cd17789d9beba7e6122a1'
assert browser_path.stat().st_size == 90922
assert not re.search(r'^\s*import\s', browser, re.M)
assert (SOURCE / 'LICENSE.fflate').read_bytes() == (tool / 'node_modules/fflate/LICENSE').read_bytes()
assert 'MIT' in (SOURCE / 'LICENSE.fflate').read_text()
expected_names = ['zlibSync', 'unzlibSync', 'gzipSync', 'gunzipSync', 'deflateSync', 'inflateSync']
assert [r['symbol'] for r in inspection['functions']] == expected_names
for row in inspection['functions']:
    match = re.search(r'^export function ' + row['symbol'] + r'\([^\n]*\) \{\n.*?^\}', browser, re.M | re.S)
    assert match is not None and match.group() == row['source'] and sha(match.group().encode()) == row['sha256']
    assert browser[:match.start()].count('\n') + 1 == row['startLine']
assert 'if (o.mtime != 0)' in browser and 'new Date(o.mtime || Date.now())' in browser
assert 'opt.level == null ? 6 : opt.level' in browser
adapter_path = tool / 'node_modules/@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/zlib.js'
assert 'import * as host from "jco:node/zlib@0.1.0";' in adapter_path.read_text()
jco_types = (tool / 'node_modules/@bytecodealliance/jco/dist/bundle.d.ts').read_text()
assert 'bundleComponentChunk(entryPath: string, options?: BundleComponentSourceOptions)' in jco_types
assert 'aliases?:' in jco_types and 'external?:' in jco_types and 'plugins?:' in jco_types and 'config?:' in jco_types

fixtures = load(SOURCE / 'fixtures.json')
assert fixtures['encodedFixtures'] is None and fixtures['NodeCrossDecodeProof'] is None
assert len(fixtures['fixtures']) == 5
raw_audit = []
for row in fixtures['fixtures']:
    size, pattern = row['bytes'], row['pattern']
    if pattern == 'empty':
        assert size == 0
        data = b''
    elif pattern == 'repeat-abc123':
        data = (b'abc123' * ((size + 5) // 6))[:size]
    else:
        assert pattern == 'xorshift32-low-byte' and row['seed'] == 0x6d2b79f5
        output, state = bytearray(), row['seed']
        for _ in range(size):
            state = (state ^ (state << 13)) & 0xffffffff
            state = (state ^ (state >> 17)) & 0xffffffff
            state = (state ^ (state << 5)) & 0xffffffff
            output.append(state & 255)
        data = bytes(output)
    fnv = 2166136261
    for byte in data:
        fnv = ((fnv ^ byte) * 16777619) & 0xffffffff
    assert len(data) == row['bytes'] and sha(data) == row['rawSha256'] and fnv == row['rawFNV1aU32']
    assert row['statisticalIncompressibilityClaim'] is False
    raw_audit.append({'id': row['id'], 'bytes': len(data), 'sha256': sha(data), 'fnv1aU32': fnv,
                      'computedWith': 'Python raw fixture logic only; no codec invoked'})
protocol = load(SOURCE / 'protocol.json')
operations = [('deflateSync', 'zlibSync', 'zlib', 'encode'), ('inflateSync', 'unzlibSync', 'zlib', 'decode'),
    ('gzipSync', 'gzipSync', 'gzip', 'encode'), ('gunzipSync', 'gunzipSync', 'gzip', 'decode'),
    ('deflateRawSync', 'deflateSync', 'raw', 'encode'), ('inflateRawSync', 'inflateSync', 'raw', 'decode')]
assert protocol['operationMap'] == [{'native': a, 'fflateBrowser': b, 'format': c, 'direction': d} for a, b, c, d in operations]
expected_cases = [{'id': 'codec-v1.' + f['id'] + '.' + op, 'fixture': f['id'], 'operation': op,
    'format': fmt, 'direction': direction, 'logicalUncompressedBytesPerOperation': f['bytes'],
    'timingNMax': 128 if f['bytes'] > 64 else 32768, 'encodedInputOracle': None, 'providerOutputOracle': None}
    for f in fixtures['fixtures'] for op, _, fmt, direction in operations]
assert protocol['cases'] == expected_cases and len(expected_cases) == protocol['caseCount'] == 30
assert protocol['caps'] == {'allCodecInputsBytes': 1048576, 'allCodecOutputsBytes': 16777216,
    'rawFixtureBytesMax': 524288, 'everyActualEncodingMustFitDecodeInputCap': True}
assert protocol['nativeOptions'] is None and protocol['fflateEncoderInternalOptions'] == {'level': 6}
assert protocol['fflateGzipInternalOptions'] == {'level': 6, 'mtime': 0}
assert protocol['validDomainOnly'] and not protocol['encodedByteIdentityRequired']
assert protocol['fullUntimedCorrectness']['encoderStreams'] == 3 * 3 * 5 == 45
assert protocol['fullUntimedCorrectness']['crossDecoderEdges'] == 3 * 3 * 3 * 5 == 135
assert protocol['sampling']['timedWorkersIfAll30CasesAdmitted'] == 30 * 2 * 2 * 3 == 360
assert protocol['sampling']['order'] == 'AB/BA/AB' and protocol['sampling']['warmups'] == 3 and protocol['sampling']['samplesPerTimedWorker'] == 7
assert protocol['measurement']['emptyByteThroughput'] is None and protocol['measurement']['emptyOutputRatio'] is None
assert not protocol['measurement']['controlsSubtracted']
assert protocol['measurement']['controls'] == ['consume-input', 'copy-input-and-consume', 'harness-no-codec']

selector = load(SOURCE / 'selector-snapshot.json')
assert len(selector['files']) == 27 and selector['selectedCatalogSize'] == 10
assert selector['PythonAncestryTreeOrPackagingClosureComplete'] is False
stage = Path('/tmp/starling-node-compat/zlib-source-v4')
snapshot = SOURCE / 'selector-snapshot'
known = set()
for row in selector['files']:
    verify(row['originalPath'], row['sha256'], row['bytes'], 'actual-stage-selector-origin', row['canonicalOriginalPath'])
    verify(SOURCE / row['snapshotPath'], row['sha256'], row['bytes'], 'exclusive-selector-copy')
    known.add(str(Path(row['originalPath']).resolve()))
edges = []
for row in selector['files']:
    relative = str(Path(row['originalPath']).relative_to(stage))
    if not relative.endswith('.mjs'):
        continue
    for match in re.finditer(r'(?:from\s*|new URL\()([\'"])(\.[^\'"]+)\1', (SOURCE / row['snapshotPath']).read_text()):
        request = match[2]
        target = (Path(row['originalPath']).parent / request).resolve()
        if relative == 'tests/node-compat/module-selection.mjs' and request == '../../':
            assert target == stage.resolve()
            edges.append({'importer': relative, 'request': request, 'kind': 'configured-repository-directory', 'resolvedSnapshotPath': 'selector-snapshot'})
        else:
            assert str(target) in known
            edges.append({'importer': relative, 'request': request, 'kind': 'exact-file-import-or-data',
                'resolvedSnapshotPath': str(Path('selector-snapshot') / target.relative_to(stage.resolve()))})
assert len(edges) == 23 and edges == selector['literalImportAndDataEdges']

facts = load(SOURCE / 'existing-native-facts.DATA-ONLY.json')
assert len(facts['variants']) == 2 and len(facts['sourceManifest350']) == 350
assert facts['newCostEnginePins'] is None and facts['newBackendAdmission'] is None and facts['existingFactsPromoteNoRuntimeBackendBoolean']
for row in facts['variants']:
    metadata = load(row['metadata']['path'])
    assert len(metadata['sourceManifest']) == row['nativeInputs'] == 350
    assert metadata['engineSha256'] == row['engineSha256'] and metadata['engineBytes'] == row['engineBytes']
    assert metadata['gcStress'] is False and metadata['entropyPolicy'] == 'off' and row['costPairAdmission'] is False
    assert metadata['zlibEnabled'] == (row['label'] == 'normal-off')
    assert len(load(row['freezeReceipt']['path'])['copies']) == row['freezeCopyRecords'] == 1024
    for item in metadata['sourceManifest']:
        path = Path(row['sourceRoot']) / item['path']
        assert sha(path.read_bytes()) == item['sha256']
    assert metadata['sourceManifest'] == facts['sourceManifest350']

providers = (SOURCE / 'providers.template.mjs').read_text()
assert 'Reflect.apply(selected[name],undefined,[input])' in providers
assert 'const fixed=Object.freeze({level:6}),gzip=Object.freeze({level:6,mtime:0})' in providers
assert 'output.byteLength===0||output.buffer!==input.buffer' in providers
assert 'Buffer.from(output.buffer,output.byteOffset,output.byteLength)' in providers
assert 'output instanceof Uint8Array&&output.byteLength<=maxOutput' in providers
assert 'POST-allocation check is not native allocation-limit/error parity' in providers
assert '@PINNED_FFLATE_BROWSER_ENTRY@' in (SOURCE / 'comparand-entry.template.mjs').read_text()
facade = Path('/tmp/starling-node-compat/production-zlib-v4/native-freeze/source/builtins/node-compat/zlib/facade.mjs').read_text()
assert "if (options === undefined) return MAX_OUTPUT" in facade
assert "key !== 'maxOutputLength'" in facade and 'const MAX_INPUT = 1024 * 1024' in facade
assert 'const MAX_OUTPUT = 16 * 1024 * 1024' in facade
for name in ['prepare-source.py', 'seal-source.py']:
    ast.parse((SOURCE / name).read_text(), filename=name)
authority = load(SOURCE / 'future-authority.json')
for key in ['rootReview', 'pairPins', 'correctnessProof', 'packagingPhysicalClosure', 'actualComponentTuples', 'actualEmittedABI', 'quietWindow']:
    assert authority[key] is None
assert not authority['actionsAllowed'] and not authority['timingAllowed'] and not authority['operationalAdmissionAllowed']
cli = load(SOURCE / 'cli-plan.json')
assert all(value is None for value in cli['entries'].values()) and cli['sourceCLIImplemented'] is False and cli['actionsAllowed'] is False
context = load(SOURCE / 'packaging-context-plan.json')
assert context['freshPackagingToolRoot'] is None and context['physicalConsumedClosure'] is None and context['newExplicitDiagnosticCostGate'] is None
assert context['allOldZlibContextsHeld'] and context['no350To355Projection'] and context['noRootLiveOldFiveFallback']
assert context['existingNativeToolClosureAloneSufficient'] is False
root_five = {str(ROOT / path) for path in ['builtins/node-compat/classic-streams/classic-core.generated.mjs',
    'builtins/node-compat/classic-streams/transformation-receipt.json', 'builtins/node-compat/classic-streams/factories.generated.h',
    'tests/node-compat/build-engine.sh', 'tests/node-compat/classic-streams-admission.mjs']}
assert not [r for r in manifest['inputs'] if r['canonicalPath'] in root_five]
stored_initial = load(SOURCE / 'source-checks.json')
stored_final = load(SOURCE / 'final-source-checks.json')
stored_syntax = load(SOURCE / 'syntax-checks.json')
assert stored_initial['count'] == 5 and all(r['passed'] for r in stored_initial['checks'])
assert stored_final['passed'] == 9 and all(r['passed'] for r in stored_final['checks'])
assert len(stored_syntax['nodeChecks']) == 4 and all(r['exitCode'] == 0 for r in stored_syntax['nodeChecks'])
assert stored_syntax['pythonAstChecks'] == 2

citations = {'nativeOptions': cite('providers.template.mjs', 'Reflect.apply(selected[name],undefined,[input])'),
    'fflateSettings': cite('providers.template.mjs', 'level:6,mtime:0'),
    'ownership': cite('providers.template.mjs', 'output.byteLength===0||output.buffer!==input.buffer'),
    'sharedBufferView': cite('providers.template.mjs', 'Buffer.from(output.buffer,output.byteOffset,output.byteLength)'),
    'postAllocationLimit': cite('providers.template.mjs', 'POST-allocation check'),
    'browserEntry': cite('comparand-entry.template.mjs', '@PINNED_FFLATE_BROWSER_ENTRY@'),
    'combinedCopyControl': cite('controls.template.mjs', 'const copied=Buffer.from(input)'),
    'futureGate': cite('packaging-context-plan.json', 'FRESH_CONTEXT_IMPLEMENTATION_REQUIRED_BEFORE_ANY_ACTION')}
clarification = {'schemaVersion': 1, 'sourceAuthorClarification':
    'Construction/copy/consume means the combined Buffer.from(input)+consume control, plus separately observed setup construction. There is no standalone construction-only control.',
    'sourceEvidence': ['controls.template.mjs:copyInputAndConsume', 'protocol.json:measurement.controls'],
    'ownerSourceEditedByReviewer': False, 'newControlOrExecutionClaim': False}
write('control-scope-clarification.json', clarification)
write('raw-fixture-audit.json', {'schemaVersion': 1, 'rows': raw_audit, 'codecOrLibraryExecuted': False})
write('checked-reference-ledger.json', {'schemaVersion': 1, 'rows': checked, 'nativeNestedPreparationDescriptorsFollowed': False})
result = {'schemaVersion': 1, 'state': 'INDEPENDENT_ZLIB_COST_COMPARISON_SOURCE_PROPOSAL_PASS_ACTIONS_HELD',
    'sourceIndexSha256': EXPECTED, 'sourceFiles': 83, 'inputManifestSha256': sha((SOURCE / 'input-freeze.json').read_bytes()),
    'originalInputRows': 401, 'hashExact': True, 'fixturesIndependentlyRecomputed': 5, 'primaryCaseRowsReconstructed': 30,
    'operationMappings': protocol['operationMap'], 'caps': protocol['caps'], 'validDomainOnly': True,
    'ownership': {'ordinaryFixedAttachedUnsharedWindowsRequiredByFutureCorrectness': True, 'nonemptyProviderOutputMustNotAliasInput': True,
        'providerOutputBufferViewShared': True, 'emptyAddressableByteIsolationClaim': False,
        'nativeInputStagingAndNativeOutputToJsCopyIncluded': True, 'fflatePostAllocationCapNotResourceParity': True,
        'unavoidableMinimalCopyOrPerformanceWinClaim': False},
    'comparisons': protocol['comparisons'], 'samplingPlan': protocol['sampling'],
    'futureCorrectness': {'encoderOutputs': 45, 'crossDecoderEdges': 135, 'encodedOraclesStillNull': True,
        'threeRetainedRotationsFreshJcoFreshWasmtimeRequired': True, 'actualEncodedStreamsBeforeDecodeCapRequired': True},
    'browserComparand': {'version': '0.8.3', 'browserEntrySha256': inspection['browserEntry']['sha256'],
        'exactSixFunctionSegmentsChecked': True, 'MITLicenseExact': True, 'nativeOptions': None,
        'fflateEncoderOptions': {'level': 6}, 'fflateGzipOptions': {'level': 6, 'mtime': 0},
        'selectedSyncTransitiveBundleAndWorkerExclusionNotYetProven': True,
        'customJcoNodeZlibAdapterExcluded': True},
    'physicalSelectorSnapshot': {'files': 27, 'literalEdges': 23, 'selectedManifests': 10,
        'actualStaged350OriginsExact': True, 'oneDirectoryEdgeSeparatelyTyped': True,
        'completePythonAncestryOrPackagingClosureClaim': False},
    'existingNativeFacts': {'sourceFiles': 350, 'twoMetadataAndFreezeDescriptorsChecked': True,
        'native1024CopyClosureNotRepeatedHere': True, 'newPairAuthority': None, 'backendBooleanPromoted': False,
        '350To355Projection': False},
    'newAuthority': authority, 'cliEntries': cli['entries'], 'directLiveRootFiveRows': 0,
    'storedOwnerChecksAuthenticatedNotRerun': {'initialDataGroups': 5, 'finalSourceChecks': 9, 'nodeParseOnly': 4, 'pythonAst': 2},
    'sourceAuthorControlsClarification': clarification['sourceAuthorClarification'],
    'findings': [], 'sourceDisposition': 'PASS_BOUNDED_PROPOSAL_ONLY', 'actionDisposition': 'HELD_NO_ACTIONS',
    'execution': {'readHashPythonRawFixtureComputationAndAstOnly': True, 'ownerFunctionsImported': False,
        'codecOrFflateOrNodeOracleExecuted': False, 'bundleOrPreflightOrNativeOrGuestOrHostOrTimingExecuted': False},
    'citations': citations,
    'limits': ['This is an intentionally unwired design and templates, not an executable activation or readiness proof.',
        'Actual packaging closure, context-aware diagnostic350 gate, real Node streams/oracles, emitted ABI, publisher/worker/collector and correctness remain prerequisites.',
        'Fixed gzip mtime0 selects an untaken Date branch by source logic; actual bundle capability/import elimination is not yet proven.',
        'The output cap in the FF wrapper is checked after allocation and gives no malformed-input/resource-limit/error parity.',
        'No encoded-byte identity, speed advantage, statistical significance, cold-start, private heap, memory-grow or full Node compatibility claim.',
        'Old held contexts are data references only and are not called or declared rerunnable.']}
write('results.json', result)
print(json.dumps({'state': result['state'], 'sourceFiles': 83, 'originalInputs': 401, 'fixtures': 5, 'cases': 30,
    'selectorFiles': 27, 'literalEdges': 23, 'actionsExecuted': False}))
