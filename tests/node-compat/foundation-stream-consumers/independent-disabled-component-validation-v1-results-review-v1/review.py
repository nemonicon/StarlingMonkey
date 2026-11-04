"""Data/static-binary review of completed disabled355 results; no runtime calls."""
from pathlib import Path
import hashlib
import json
import os
import re
import stat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
SOURCE = FAMILY / 'component-validation-activated-v2'
OUT = Path('/tmp/starling-node-compat/consumers355-v2-disabled-component-validation-v1')
FAMILY_SHA = 'bfb689fe993b9f55abc4848e77930c773597e769a7f08a0f2404914d82227835'
ENGINE_SHA = '81ffa152cf1bbdc7dbd59d7390478964be1a0ae213f636710692c2a08c3e5110'
cache, checked = {}, []

def digest(path):
    path = Path(path)
    info = path.stat()
    key = (str(path.resolve()), info.st_size, info.st_mtime_ns)
    if key not in cache:
        h = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(block)
        cache[key] = (h.hexdigest(), info.st_size)
    return cache[key]

def load(path):
    return json.loads(Path(path).read_text())

def verify(row, base=None, role='file'):
    path = Path(row['path'])
    if not path.is_absolute():
        assert base is not None
        path = base / path
    assert path.is_file() and not path.is_symlink(), str(path)
    assert digest(path) == (row['sha256'], row['bytes']), str(path)
    real = row.get('realPath', row.get('realpath'))
    if real is not None:
        assert str(path.resolve()) == real
    checked.append({'role': role, 'path': str(path), 'sha256': row['sha256'], 'bytes': row['bytes']})

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')

root_path = FAMILY / 'disabled-component-validation-v1-root-results.json'
assert digest(root_path) == ('3cd407e5cd591e15cc4f65546478cc2befdd91703f2bb2bd9111340335339844', 3227)
root = load(root_path)
for key in ['authority', 'sourceFamilyIndex', 'terminal', 'stdout', 'stderr', 'report', 'completion', 'outputClosure', 'component']:
    verify(root[key], role='Root-reference:' + key)
assert root['rawExitCode'] == 0 and root['engineSha256'] == ENGINE_SHA
authority = load(root['authority']['path'])
terminal = load(root['terminal']['path'])
assert terminal['rawExitCode'] == 0 and terminal['observedByRoot'] is True and terminal['pid'] == 76515
assert terminal['argv'] == authority['argv']
assert terminal['selectedEnvironment'] == authority['selectedEnvironment']
assert authority['variant'] == 'disabled-off' and authority['freshOutput'] == str(OUT)
assert authority['engineSha256'] == ENGINE_SHA and authority['consumerOffZlibOn'] is True
assert authority['componentAndGuestValidationAllowed'] is True and authority['timingAllowed'] is False
assert authority['gcExecutionAllowed'] is False and authority['operationalAdmission'] is False
for key in ['sourceFamilyIndex', 'independentFamilyReview', 'actualPreflight']:
    verify(authority[key], role='Root-runtime-authority:' + key)
for key in ['stdout', 'stderr']:
    verify(terminal[key], role='Root-terminal-stream')
assert Path(root['stderr']['path']).read_bytes() == b''
stdout_lines = [json.loads(line) for line in Path(root['stdout']['path']).read_text().splitlines() if line.strip()]
assert stdout_lines[-1] == {'state': 'CONSUMERS355_DISABLED_MODULE_AND_SMOKE_VALIDATION_PASSED', 'output': str(OUT), 'imports': []}

# Authenticate current source/native/tool closure without executing its verifier.
assert digest(SOURCE / 'index.json')[0] == FAMILY_SHA
index = load(SOURCE / 'index.json')
assert len(index['files']) == 47
for row in index['files']:
    verify(row, SOURCE, 'current-source-index')
family_proof = FAMILY / 'independent-component-validation-v2-family-review-v1'
assert digest(family_proof / 'index.json')[0] == 'e894a968f4c5ea20731d8ab5d539b6a3f23368ee522821aefee7957894990722'
for row in load(family_proof / 'index.json')['files']:
    verify(row, family_proof, 'inherited-family-proof')
family_result = load(family_proof / 'results.json')
assert family_result['completePublisherByteReconstruction'] and family_result['completeConsumedInputUnionReconstruction']
assert family_result['generatedIndexSha256'] == FAMILY_SHA
seal = load(SOURCE / 'input-freeze.json')
assert len(seal['inputs']) == 7268
for row in seal['inputs']:
    verify(row, role='current-consumed-input')
    if 'boundary' in row:
        assert row['boundary'] == str(SOURCE)
        path = Path(row['path'])
        path.relative_to(SOURCE)
        while path != SOURCE:
            assert not path.is_symlink()
            path = path.parent
tree_files = 0
for tree in seal['toolTrees']:
    base = Path(tree['path'])
    assert str(base.resolve()) == tree['realPath']
    actual = []
    for current, dirs, files in os.walk(base, followlinks=False):
        for name in dirs + files:
            path = Path(current) / name
            mode = path.lstat().st_mode
            kind = 'symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file'
            actual.append({'path': str(path.relative_to(base)), 'kind': kind})
            tree_files += kind == 'file'
    assert sorted(actual, key=lambda r: r['path']) == tree['entries']
assert len(seal['toolTrees']) == 2 and len(seal['toolLinks']) == 22 and tree_files == 4890
for row in seal['toolLinks']:
    path = Path(row['path'])
    assert path.is_symlink() and os.readlink(path) == row['linkText'] and str(path.resolve()) == row['resolvedTarget']
    if row['targetKind'] == 'file':
        assert digest(path.resolve()) == (row['targetSha256'], row['targetBytes'])
    else:
        assert row['targetKind'] == 'directory' and path.resolve().is_dir()
config = load(SOURCE / 'activation.json')
assert config['actual']['disabled-off']['engineSha256'] == ENGINE_SHA
assert config['nativeConfiguredSourceRoot'] == '/private/tmp/starling-node-compat/consumers-source-v2'
assert config['componentToolRoot'] == str(SOURCE / 'packaging-tools')
pin = load(SOURCE / 'reviewed-pins.json')['variants']['disabled-off']
assert pin['engineSha256'] == ENGINE_SHA and pin['streamConsumersEnabled'] is False and pin['zlibEnabled'] is True
assert pin['gcStress'] is False and pin['entropyPolicy'] == 'off' and pin['sourceFiles'] == 355
assert pin['runtimeBackendProof'] == {'verified': False, 'version': None, 'vernum': None}
assert len(pin['frozenFiles']) == 1164
for row in pin['frozenFiles']:
    verify(row, role='actual-disabled-native-frozen-copy')
for path_key, hash_key in [('independentProofIndexPath', 'independentProofIndexSha256'), ('independentProofResultPath', 'independentProofResultSha256')]:
    path = Path(pin[path_key])
    verify({'path': str(path), 'sha256': pin[hash_key], 'bytes': path.stat().st_size}, role='inherited-disabled-native-proof')
metadata = load(next(r['path'] for r in pin['frozenFiles'] if r['sha256'] == pin['receiptSha256']))
assert len(metadata['sourceManifest']) == 355 and len(metadata['componentizeSourceManifest']) == 3
assert metadata['streamConsumersEnabled'] is False and metadata['zlibEnabled'] is True and metadata['gcStress'] is False
assert metadata['debuggerEnabled'] is False and metadata['oomTesting'] is False
selected = []
for row in metadata['selectedModuleManifests']:
    path = Path(pin['sourceRoot']) / row['path']
    assert digest(path)[0] == row['sha256']
    selected.append(load(path))
core = None
for manifest in selected:
    for name, module in manifest['modules'].items():
        assert name not in ['node:stream/consumers', 'stream/consumers']
        assert 'stream/consumers' not in module['aliases']
        if name == 'node:child_process':
            assert core is None
            core = manifest
assert core is not None and 'node:buffer' in core['modules']
assert any('node:zlib' in m['modules'] for m in selected)
expected_namespace = sorted(core['modules']['node:child_process']['exports'])
for row in [config['liveAdapter']] + config['liveWit']:
    verify(row, role='live-adapter-or-wit')
assert config['liveAdapter']['sha256'] == '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'

report = load(OUT / 'results.json')
completion = load(OUT / 'completion.json')
assert report['state'] == 'CONSUMERS355_DISABLED_MODULE_AND_SMOKE_VALIDATION_PASSED'
assert report['variant'] == 'disabled-off' and report['sourceFamilyIndexSha256'] == FAMILY_SHA
assert report['engineSha256'] == ENGINE_SHA and report['nativeSourceFiles'] == 355
assert report['componentizeCalls'] == 1 and report['namespacePassed'] is False
assert len(report['records']) == 5 and len(report['denials']) == 8 and report['initializerRecords'] == []
assert report['scope']['normalRecordsExecuted'] == 0 and report['scope']['ordinaryCombinedOwnerGcOnly'] is False
assert report['scope']['HTTPBodyCancellationOrReuseInferred'] is False and report['scope']['operationalAdmission'] is False
assert completion['reportSha256'] == digest(OUT / 'results.json')[0]
assert completion['state'] == 'CONSUMERS355_VALIDATION_OUTPUT_COMPLETE' and completion['requiresIndependentExitZero'] is True
assert len(completion['artifacts']) == 59 and len(completion['outputLinks']) == 1
for row in completion['artifacts']:
    verify(row, role='completion-artifact')
physical_files, links = [], []
for current, dirs, files in os.walk(OUT, followlinks=False):
    for name in dirs + files:
        path = Path(current) / name
        if path.is_symlink():
            links.append(str(path))
        elif path.is_file():
            physical_files.append(str(path))
assert set(physical_files) == {r['path'] for r in completion['artifacts']} | {str(OUT / 'completion.json')}
assert len(physical_files) == 60 and links == [str(OUT / 'node_modules')]
for row in completion['outputLinks']:
    path = Path(row['path'])
    assert os.readlink(path) == row['linkText'] and str(path.resolve()) == row['resolvedTarget']
    assert row == load(OUT / 'output-controls.json')['nodeModulesLink']
root_closure = load(root['outputClosure']['path'])
assert root_closure['regularFiles'] == 60 and root_closure['links'] == completion['outputLinks']
assert {r['path'] for r in root_closure['files']} == set(physical_files)
for row in root_closure['files']:
    verify(row, role='Root-complete-output-closure')

# Verify the actual eight refusal categories, exact specifiers and fixture sources.
denial_audit = []
for i, record in enumerate(report['denials']):
    specifier = ['node:stream/consumers', 'stream/consumers'][i // 4]
    kind = ['default-esm', 'named-esm', 'namespace-esm', 'literal-cjs'][i % 4]
    category = 'cjs' if kind == 'literal-cjs' else 'esm'
    reason = ('CommonJS require is not admitted: ' if category == 'cjs' else 'Node builtin is not admitted by this profile: ') + specifier
    assert record['index'] == i and record['id'] == specifier and record['kind'] == kind
    assert record['beforeAnyComponentization'] is True and record['error']['name'] == 'Error'
    reasons = re.findall(r'(?:Node builtin is not admitted by this profile:|CommonJS require is not admitted:) [^\s"\'`()]+', record['error']['message'])
    assert reasons and all(r == reason for r in reasons)
    assert record['diagnostic'] == {'category': category, 'expectedReason': reason, 'actualReasons': reasons}
    assert record == load(OUT / 'denials' / (str(i) + '.json'))
    quoted = json.dumps(specifier)
    if kind == 'default-esm':
        files = {'entry.mjs': 'import c from ' + quoted + '; export function run(){return typeof c;}'}
    elif kind == 'named-esm':
        files = {'entry.mjs': 'import {text} from ' + quoted + '; export function run(){return typeof text;}'}
    elif kind == 'namespace-esm':
        files = {'entry.mjs': 'import * as c from ' + quoted + '; export function run(){return typeof c;}'}
    else:
        files = {'entry.mjs': "import c from './literal.cjs'; export function run(){return typeof c;}",
            'literal.cjs': 'module.exports=require(' + quoted + ');'}
    for name, value in files.items():
        assert (OUT / 'denials' / str(i) / name).read_text() == value
    denial_audit.append({'index': i, 'specifier': specifier, 'kind': kind, 'category': category,
        'exactReason': reason, 'allActualReasons': reasons, 'beforeComponentization': True})

expected_bytes = {'sharedHex': '090203', 'copyHex': '010203', 'viewHex': '0203', 'sharedBacking': True,
    'sharedOffset': 2, 'viewBacking': True, 'viewOffset': 3, 'copyIndependent': True, 'globalBuffer': True}
expected_fields = {key: {'own': True, 'type': 'string', 'value': value} for key, value in {
    'code': 'ERR_SM_NODE_UNSUPPORTED', 'module': 'node:child_process', 'operation': 'exec', 'profile': core['profileVersion']}.items()}
record_audit = []
for record, count in zip(report['records'], [1, 2, 3, 1, 1]):
    raw_path = Path(record['rawFile']['path'])
    verify(record['rawFile'], role='raw-return')
    verify(record['transportFile'], role='typed-transport-return')
    raw = raw_path.read_text()
    value = json.loads(raw)
    assert value == record['value'] == load(raw_path.with_name(raw_path.name.replace('.raw.txt', '.observed.json')))
    envelope = load(record['transportFile']['path'])
    assert envelope == {'type': 'string', 'codeUnits': len(raw.encode('utf-16-le')) // 2, 'valueStoredSeparatelyAsRawString': True}
    assert value['calls'] == count and value['bytes'] == expected_bytes and value['snapshot']['bytes'] == expected_bytes
    for fields in [value['call'], value['construction'], value['snapshot']['call'], value['snapshot']['construction']]:
        assert fields == expected_fields
    assert value['namespace'] == expected_namespace and value['defaultNamed'] is True and value['allCallable'] is True
    assert value['thenType'] == value['defaultThenType'] == 'undefined'
    record_audit.append({'id': record['id'], 'calls': count, 'rawFile': record['rawFile'],
        'transportFile': record['transportFile'], 'fullDecodedValue': value})
wt_terminal = load(OUT / 'processes/wasmtime-smoke.terminal.json')
assert wt_terminal['status'] == 0 and wt_terminal['signal'] is None and wt_terminal['spawnError'] is None
assert wt_terminal['timedOut'] is False and wt_terminal['outputLimitExceeded'] is False and wt_terminal['externalSignal'] is None
assert wt_terminal['terminalExitZeroObserved'] and wt_terminal['ownedGroupGone'] and wt_terminal['closed']
assert wt_terminal['signals'] == [] and wt_terminal['errors'] == [] and wt_terminal['timeoutMs'] == 600000
for key in ['stdout', 'stderr']:
    verify(wt_terminal[key], role='fresh-Wasmtime-raw-stream')
assert Path(wt_terminal['stderr']['path']).read_bytes() == b''
wt_stdout = Path(wt_terminal['stdout']['path']).read_text()
wt_inner = json.loads(wt_stdout.strip())
assert isinstance(wt_inner, str) and wt_inner == Path(report['records'][4]['rawFile']['path']).read_text()
assert json.loads(wt_inner) == report['records'][4]['value']
assert wt_terminal['args'] == ['run', '--invoke', 'run()', str(OUT / 'consumer_off_smoke.component.wasm')]
assert digest(wt_terminal['executable'])[0] == 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c'

# Static component/core parsing: never instantiate either binary.
def uleb(data, offset):
    value, shift = 0, 0
    while True:
        byte = data[offset]
        offset += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, offset
        shift += 7
        assert shift <= 35

def sections(data, header):
    assert data[:8] == header
    offset, rows = 8, []
    while offset < len(data):
        kind = data[offset]
        size, start = uleb(data, offset + 1)
        assert start + size <= len(data)
        rows.append((kind, start, data[start:start + size]))
        offset = start + size
    assert offset == len(data)
    return rows

component = (OUT / 'consumer_off_smoke.component.wasm').read_bytes()
core_binary = (OUT / 'consumer_off_smoke.core.wasm').read_bytes()
component_sections = sections(component, b'\0asm\x0d\0\x01\0')
assert not [r for r in component_sections if r[0] == 10]
assert [r[2] for r in component_sections if r[0] == 1] == [core_binary]
assert [r[2] for r in component_sections if r[0] == 7] == [bytes.fromhex('0140000073')]
assert [r[2] for r in component_sections if r[0] == 11] == [bytes.fromhex('01000372756e010000')]
core_sections = sections(core_binary, b'\0asm\x01\0\0\0')
assert [r[2] for r in core_sections if r[0] == 2] == [b'\0']
export_bytes = next(r[2] for r in core_sections if r[0] == 7)
number, offset = uleb(export_bytes, 0)
core_exports = []
for _ in range(number):
    size, offset = uleb(export_bytes, offset)
    name = export_bytes[offset:offset + size].decode()
    offset += size
    kind = export_bytes[offset]
    index_value, offset = uleb(export_bytes, offset + 1)
    core_exports.append({'name': name, 'kind': kind, 'index': index_value})
assert offset == len(export_bytes)
assert {'memory', 'run', 'cabi_post_run', 'cabi_realloc'} <= {r['name'] for r in core_exports}
glue = (OUT / 'consumer_off_smoke.js').read_text()
assert re.findall(r"new URL\('([^']+\.core\.wasm)', import.meta.url\)", glue) == ['./consumer_off_smoke.core.wasm']
assert 'postReturn0 = exports0.cabi_post_run' in glue and 'exports0Run = exports0.run' in glue and 'export { run,' in glue
assert (OUT / 'consumer_off_smoke.d.ts').read_text().strip().endswith('export function run(): string;')
wit = (OUT / 'consumer_off_smoke.emitted.wit').read_text()
assert wit == report['fixture']['emittedWit'] and not re.search(r'\bimport\b', wit)
assert re.findall(r'export\s+\w+:\s*func\([^;]+;', wit) == ['export run: func() -> string;']
assert report['interfaceAudit'] == report['fixture']['interfaceAudit']
assert report['interfaceAudit']['emittedImports'] == [] and report['interfaceAudit']['selectedInterfaces'] == []
assert digest(OUT / 'consumer_off_smoke.component.wasm') == ('404f905c300f1754f452b3c44fe2ea9c5a1aae12ff835864d510e0e45b04ef64', 13046739)
assert report['fixture']['componentSha256'] == report['interfaceAudit']['componentSha256'] == digest(OUT / 'consumer_off_smoke.component.wasm')[0]
assert digest((OUT / 'consumer_off_smoke.core.wasm'))[1] == 13046462
assert report['bundle']['imports'] == ['node:buffer', 'node:child_process']
assert hashlib.sha256(report['bundle']['code'].encode()).hexdigest() == report['bundle']['sha256']
assert not re.search(r'createConsumersModule|function\s+createClassicCore|node_modules/(?:unenv|@bytecodealliance/jco-std)', report['bundle']['code'])
assert all('/builtins/node-compat/' not in name and '/node_modules/' not in name for name in report['bundle']['moduleIds'])
smoke_match = re.search(r'export const smokeSource=`([\s\S]*)`;\s*$', (SOURCE / 'disabled-fixtures.mjs').read_text())
assert smoke_match is not None and smoke_match[1] == (OUT / 'consumer-off-smoke.mjs').read_text()

progress = [load(p) for p in sorted((OUT / 'progress').glob('*.json'))]
assert len(progress) == 13 and [r['sequence'] for r in progress] == list(range(1, 14))
assert progress[0]['event'] == 'validation-started' and progress[0]['consumerEnabled'] is False
assert [r['componentizeCalls'] for r in progress if r['event'] == 'componentize-before'] == [1]
assert len([r for r in progress if r['event'] == 'call-before']) == len([r for r in progress if r['event'] == 'call-returned']) == 5
assert next(i for i, r in enumerate(progress) if r['event'] == 'wasmtime-terminal') < next(i for i, r in enumerate(progress) if r['event'] == 'call-returned' and r['id'].endswith('fresh-Wasmtime-smoke'))

write('denial-audit.json', {'schemaVersion': 1, 'rows': denial_audit, 'esm': 6, 'literalCjs': 2, 'allBeforeComponentization': True})
write('full-smoke-observations.json', {'schemaVersion': 1, 'rows': record_audit, 'allRawParsedIndependently': True,
    'freshWasmtimeRawStdoutFullyDoubleDecoded': True, 'callbackSupplied': False, 'callbackBehaviorClaim': False})
write('binary-static-audit.json', {'schemaVersion': 1, 'componentSha256': digest(OUT / 'consumer_off_smoke.component.wasm')[0],
    'componentBytes': len(component), 'publicImports': [], 'publicExport': 'run: func() -> string',
    'publicFunctionTypePayloadHex': '0140000073', 'publicExportPayloadHex': '01000372756e010000',
    'sections': [{'id': k, 'start': start, 'bytes': len(raw)} for k, start, raw in component_sections],
    'embeddedCoreIsExactlyPublishedJcoCore': True, 'coreSha256': digest(OUT / 'consumer_off_smoke.core.wasm')[0],
    'coreBytes': len(core_binary), 'coreImportCount': 0, 'coreExportsForGlueRelationOnly': core_exports,
    'glueCoreReferenceAndRunPostReturnBindingChecked': True, 'instantiationOrPrivateMemoryRead': False})
write('checked-reference-ledger.json', {'schemaVersion': 1, 'rows': checked, 'uniquePhysicalFilesHashed': len(cache)})
result = {'schemaVersion': 1, 'state': 'INDEPENDENT_CONSUMERS355_DISABLED_COMPONENT_VALIDATION_V1_RESULTS_PASS',
    'rootReceiptSha256': digest(root_path)[0], 'sourceFamilyIndexSha256': FAMILY_SHA,
    'reportSha256': digest(OUT / 'results.json')[0], 'completionSha256': digest(OUT / 'completion.json')[0],
    'regularOutputFiles': 60, 'completionArtifactRows': 59, 'outputLinks': 1,
    'component': {'sha256': digest(OUT / 'consumer_off_smoke.component.wasm')[0], 'bytes': len(component),
        'publicImports': [], 'publicExports': ['run: func() -> string'], 'matchingJcoCore': True, 'coreBytes': len(core_binary)},
    'denials': {'total': 8, 'esm': 6, 'literalCjs': 2, 'exactCategoryAndSpecifierChecked': True,
        'allBeforeAnyComponentization': True, 'fixtureSourceBytesReconstructed': True},
    'smoke': {'returnedRecords': 5, 'retainedCounters': [1, 2, 3], 'freshJcoCounter': 1, 'freshWasmtimeCounter': 1,
        'fullRawAndObservedValuesDecoded': True, 'typedTransportEnvelopesChecked': True,
        'freshWasmtimeFullRawStdoutDoubleDecoded': True, 'BufferCopiesViewsOffsetsAndGlobalIdentity': True,
        'callAndNewOwnFourStringRefusalFieldsAtSnapshotAndRuntime': True,
        'callbackSupplied': False, 'callbackInvocationOrNonInvocationClaim': False,
        'childProcessNamespaceDefaultNamedAndNoThen': True},
    'sourceAndNative': {'sourceFiles': 47, 'consumedRowsRehashed': 7268, 'nativeSources': 355, 'externalEmbeddingSources': 3,
        'engineSha256': ENGINE_SHA, 'consumerEnabled': False, 'zlibEnabled': True, 'gcStress': False, 'entropyPolicy': 'off',
        'actualDisabledFrozenFilesRehashed': 1164, 'toolTrees': 2, 'toolLinks': 22, 'regularToolFiles': 4890,
        'disabledNativeProofIndexSha256': pin['independentProofIndexSha256'],
        'disabledNativeProofResultSha256': pin['independentProofResultSha256'],
        'fullPublisherDerivationInheritedExactProofIndex': 'e894a968f4c5ea20731d8ab5d539b6a3f23368ee522821aefee7957894990722',
        'runtimeBackendProof': pin['runtimeBackendProof']},
    'RootOuterExit': {'session': 88048, 'pid': 76515, 'rawExitCode': 0, 'observedByThisReader': False,
        'terminalArgvEnvironmentAndStreamsAuthenticated': True},
    'freshWasmtimeTerminal': {'status': 0, 'signal': None, 'timedOut': False, 'ownedGroupGone': True,
        'stdoutRetained': True, 'stderrEmpty': True, 'observedByThisReader': False},
    'execution': {'readOnlyPythonAndStaticBinaryData': True, 'ownerFunctionOrActionInvoked': False,
        'runtimeOrGuestOrNativeOrHostExecuted': False, 'nodeOrWasmtimeOrWasmToolsExecuted': False},
    'scope': {'positiveConsumerCasesExecutedByThisDisabledReport': 0, 'consumerNamespacePositiveClaim': False,
        'gcOrRootIsolationClaim': False, 'backendOrTlsOrHttpOrRequestReuseClaim': False,
        'operationalAdmission': False, 'performanceClaim': False, 'fullNodeCompatibilityOrNewAcceptanceClaim': False},
    'findings': []}
write('results.json', result)
print(json.dumps({'state': result['state'], 'regularFiles': 60, 'links': 1, 'denials': 8,
    'fullRawSmokes': 5, 'freshWasmtimeDoubleDecoded': True, 'componentImports': [], 'reviewerRuntimeActions': False}))
