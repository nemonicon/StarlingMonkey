"""Read/hash/reconstruct activated consumer355 source. No owner code imports."""
from pathlib import Path
import ast
import hashlib
import json
import os
import re
import stat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
ROOT = HERE.parents[3]
SOURCE = FAMILY / 'component-validation-candidate-v2'
DEST = FAMILY / 'component-validation-activated-v2'
SOURCE_SHA = 'a75ee76c1291988cec55252f8ab54e451f31b1593f22119759bada058860002b'
DEST_SHA = 'bfb689fe993b9f55abc4848e77930c773597e769a7f08a0f2404914d82227835'
NATIVE_SHA = '9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378'
cache, refs = {}, []

def sha(data):
    return hashlib.sha256(data).hexdigest()

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

def encoded(value):
    return (json.dumps(value, indent=2) + '\n').encode()

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
    refs.append({'role': role, 'path': str(path), 'sha256': row['sha256'], 'bytes': row['bytes']})

def indexed(path, expected, count):
    assert digest(path / 'index.json')[0] == expected
    document = load(path / 'index.json')
    assert len(document['files']) == count
    assert len({r['path'] for r in document['files']}) == count
    for row in document['files']:
        assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
        verify(row, path, 'indexed:' + path.name)
    return document

def text(path):
    return Path(path).read_text()

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')

source_index = indexed(SOURCE, SOURCE_SHA, 80)
dest_index = indexed(DEST, DEST_SHA, 47)
peer_root = FAMILY / 'independent-component-validation-v2-source-review-v1'
indexed(peer_root, '13bc711de7653539bff7b81d9dcb6caebcdfa6dc484d8747e8169c257130655a', 9)
source_root_review = FAMILY / 'component-validation-v2-source-root-review.json'
assert digest(source_root_review)[0] == '50b1b207f377b881f00df9c9d0f647b6ea9dcfbd0462ff8314cde6d00c38a512'
source_authority = load(source_root_review)
assert source_authority['sourceIndex']['sha256'] == SOURCE_SHA
assert source_authority['sourceActivationAllowed'] is True and source_authority['runtimeActionsAllowed'] is False
for key in ['sourceIndex', 'independentSourceReview', 'nativeValidationPins', 'nativeBuildRootReview']:
    verify(source_authority[key], role='source-Root-authority')

root_receipt_path = FAMILY / 'component-validation-v2-source-activation-root-results.json'
assert digest(root_receipt_path)[0] == 'a9ae431b8c59e8ae6de101f5cb6ee22abebd5e1d94d099ae5e2babc8464845dd'
root_receipt = load(root_receipt_path)
assert root_receipt['rawExitCode'] == 0 and root_receipt['rootObservedSession'] == 34235
assert root_receipt['generatedFamilyIndex']['sha256'] == DEST_SHA
assert root_receipt['componentOrGuestExecuted'] is False and root_receipt['operationalAdmission'] is False
for row in root_receipt['references']:
    verify(row, role='Root-activation-reference')
terminal_row = next(r for r in root_receipt['references'] if r['path'].endswith('.terminal.json'))
terminal = load(terminal_row['path'])
assert terminal['rawExitCode'] == 0 and terminal['parentPid'] == 72182 and terminal['error'] is None
assert terminal['rootSourceReviewSha256'] == digest(source_root_review)[0]
assert terminal['argv'] == source_authority['plannedCommand']
assert terminal['componentOrGuestExecuted'] is False and terminal['operationalAdmission'] is False
stdout_row = next(r for r in root_receipt['references'] if r['path'].endswith('.stdout.log'))
stdout_record = json.loads(Path(stdout_row['path']).read_text())
assert stdout_record == {'output': str(DEST), 'indexSha256': DEST_SHA, 'files': 47, 'consumed': 7268, 'toolTrees': 2, 'toolLinks': 22, 'sourceOnly': True, 'guestExecuted': False}

config = load(DEST / 'activation.json')
seal = load(DEST / 'input-freeze.json')
receipt = load(DEST / 'source-receipt.json')
pins = load(DEST / 'reviewed-pins.json')
native_review = load(DEST / 'root-review.json')
assert len(seal['inputs']) == 7268
assert len({r['path'] for r in seal['inputs']}) == 7268
for row in seal['inputs']:
    assert Path(row['path']).is_absolute()
    verify(row, role='actual-consumed-input')
    if 'boundary' in row:
        assert row['boundary'] == str(DEST)
        path = Path(row['path'])
        path.relative_to(DEST)
        while path != DEST:
            assert not path.is_symlink()
            path = path.parent

native = Path(config['bootstrapRoot'])
original_native = ROOT / native.relative_to('/private/tmp/starling-node-compat/consumers-source-v2')
native_index = indexed(native, NATIVE_SHA, 59)
assert indexed(original_native, NATIVE_SHA, 59) == native_index
assert str(native.parents[3]) == '/private/tmp/starling-node-compat/consumers-source-v2'
assert config['nativeConfiguredSourceRoot'] == str(native.parents[3])
assert config['componentToolRoot'] == str(DEST / 'packaging-tools')
assert config['componentToolRoot'] != config['nativeConfiguredSourceRoot']
assert config['bootstrapIndexSha256'] == NATIVE_SHA
assert config['sourceProposalIndexSha256'] == SOURCE_SHA
assert config['operationalAdmission'] is False and config['engineMetadataRewritten'] is False
assert digest(DEST / 'reviewed-pins.json')[0] == 'bdbad8c1065dea3fd354baed68d33301613e653111432d2cbdc12637eae99e89' == config['pinsSha256']
assert digest(DEST / 'root-review.json')[0] == '22fe078bc90d13d0ce3313a6fbabd1b22ec0b611ecba5596232d4473992b7ba0' == config['rootReviewSha256']
assert pins['sourceFiles'] == native_review['sourceFiles'] == 355
assert pins['externalSources'] == native_review['externalSources'] == 3
assert native_review['runtimeBackendProof'] == {'verified': False, 'version': None, 'vernum': None}
assert not pins['metadataBackendProofRewritten'] and not pins['operationalAdmission']
assert pins['variants']['normal-runtime'] is None and config['actual']['normal-runtime'] is None
expected_engine = {'normal-off': '661ef79418ab139c9a7bcebb57eb36c17c3c398f67c80bbcd680cb95839f0c79',
    'gc-off': 'b378dea3bafa01d3b85728883d20c1e61a8a22807f2614cb6eceeb615da910e7',
    'disabled-off': '81ffa152cf1bbdc7dbd59d7390478964be1a0ae213f636710692c2a08c3e5110'}
native_summaries = {}
for label, expected in expected_engine.items():
    pin = pins['variants'][label]
    assert pin['engineSha256'] == expected
    assert {k: pin[k] for k in ['engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256']} == config['actual'][label]
    assert len(pin['frozenFiles']) == 1164 and pin['sourceFiles'] == 355
    assert pin['sourceRoot'] == '/tmp/starling-node-compat/production-consumers-v1/native-freeze/source'
    assert pin['streamConsumersEnabled'] == (label != 'disabled-off')
    assert pin['zlibEnabled'] is True and pin['gcStress'] == (label == 'gc-off') and pin['entropyPolicy'] == 'off'
    assert pin['runtimeBackendProof'] == {'verified': False, 'version': None, 'vernum': None}
    for row in pin['frozenFiles']:
        verify(row, role='native-frozen-copy:' + label)
    assert digest(pin['freezeReceiptPath'])[0] == pin['freezeReceiptSha256']
    metadata_row = next(r for r in pin['frozenFiles'] if r['sha256'] == pin['receiptSha256'])
    metadata = load(metadata_row['path'])
    assert len(metadata['sourceManifest']) == 355 and len(metadata['componentizeSourceManifest']) == 3
    assert metadata['engineSha256'] == expected and metadata['streamConsumersEnabled'] == (label != 'disabled-off')
    assert metadata['zlibEnabled'] is True and metadata['gcStress'] == (label == 'gc-off')
    assert metadata['entropyPolicy'] == 'off' and metadata['debuggerEnabled'] is False and metadata['oomTesting'] is False
    assert next(r for r in metadata['sourceManifest'] if r['path'] == 'builtins/web/text-codec/text-decoder.cpp')['sha256'] == '4697d8951a724d92e7550d48bd10cd2652d4d789797dc90ad8401216e9a4512c'
    verify({'path': pin['independentProofIndexPath'], 'sha256': pin['independentProofIndexSha256'], 'bytes': Path(pin['independentProofIndexPath']).stat().st_size}, role='native-inherited-independent-proof')
    verify({'path': pin['independentProofResultPath'], 'sha256': pin['independentProofResultSha256'], 'bytes': Path(pin['independentProofResultPath']).stat().st_size}, role='native-inherited-independent-proof')
    native_summaries[label] = {'engineSha256': expected, 'engineBytes': pin['engineBytes'], 'frozenCopies': 1164,
        'sources': 355, 'externalSources': 3, 'consumersEnabled': pin['streamConsumersEnabled'], 'zlibEnabled': True,
        'gcStress': pin['gcStress'], 'entropyPolicy': 'off', 'runtimeBackendProof': pin['runtimeBackendProof']}

# Reconstruct the publisher's complete input union and generated bytes independently.
publisher = ast.parse(text(SOURCE / 'activate.py'))
payload = None
for statement in publisher.body:
    if isinstance(statement, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PAYLOAD' for t in statement.targets):
        payload = ast.literal_eval(statement.value)
assert isinstance(payload, list) and len(payload) == 20
expected_inputs = {}
def add(path, expected_hash=None, expected_bytes=None):
    path = Path(path).absolute()
    actual = digest(path)
    if expected_hash is not None:
        assert actual == (expected_hash, expected_bytes)
    row = {'path': str(path), 'sha256': actual[0], 'bytes': actual[1]}
    assert str(path) not in expected_inputs or expected_inputs[str(path)] == row
    expected_inputs[str(path)] = row
for base, document in [(SOURCE, source_index), (original_native, native_index), (native, native_index)]:
    add(base / 'index.json')
    for row in document['files']:
        add(base / row['path'], row['sha256'], row['bytes'])
source_inputs = load(SOURCE / 'source-inputs.json')
assert len(source_inputs['files']) == 5250
for row in source_inputs['files']:
    add(row['path'], row['sha256'], row['bytes'])
pins_path = Path(source_authority['nativeValidationPins']['path'])
review_path = Path(source_authority['nativeBuildRootReview']['path'])
add(pins_path, config['pinsSha256'], pins_path.stat().st_size)
add(review_path, config['rootReviewSha256'], review_path.stat().st_size)
for label in expected_engine:
    for row in pins['variants'][label]['frozenFiles']:
        add(row['path'], row['sha256'], row['bytes'])
context = load(SOURCE / 'tool-context.json')
for row in context['inputs']:
    add(row['path'], row['sha256'], row['bytes'])
tool_pins = load(native / 'artifact-tools/tool-pins.json')
assert len(tool_pins['toolDependencies']) == 767
for row in tool_pins['toolDependencies']:
    add(native.parents[3] / row['path'], row['sha256'], row['bytes'])
live = load(SOURCE / 'live-inputs.json')
assert live['adapter']['sha256'] == '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0' and live['adapter']['bytes'] == 53512
assert len(live['wit']) == 7
for row in [live['adapter']] + live['wit']:
    add(row['path'], row['sha256'], row['bytes'])
closure = load(SOURCE / 'component-tool-closure.json')
old_snapshot, new_snapshot = str(SOURCE / 'packaging-tools'), str(DEST / 'packaging-tools')
assert closure['componentToolRoot'] == old_snapshot
closure['componentToolRoot'] = new_snapshot
for row in closure['files']:
    assert row['path'].startswith(old_snapshot + '/')
    row['path'] = new_snapshot + row['path'][len(old_snapshot):]
    row['realPath'] = row['path']
closure_raw = encoded(closure)
assert closure_raw == (DEST / 'component-tool-closure.json').read_bytes()
actual = {label: {k: pins['variants'][label][k] for k in ['engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256']} for label in ['normal-off', 'gc-off', 'disabled-off']}
actual['normal-runtime'] = None
expected_config = {'schemaVersion': 1, 'state': 'ROOT_REVIEWED_CONSUMERS355_COMPONENT_VALIDATION_SOURCE_V1',
    'sourceProposalIndexSha256': SOURCE_SHA, 'bootstrapRoot': str(native), 'bootstrapIndexSha256': NATIVE_SHA,
    'pinsSha256': config['pinsSha256'], 'rootReviewSha256': config['rootReviewSha256'], 'actual': actual,
    'nativeConfiguredSourceRoot': '/private/tmp/starling-node-compat/consumers-source-v2', 'componentToolRoot': new_snapshot,
    'componentToolClosureSha256': sha(closure_raw), 'liveAdapter': live['adapter'], 'liveWit': live['wit'],
    'operationalAdmission': False, 'engineMetadataRewritten': False}
config_raw = encoded(expected_config)
assert config_raw == (DEST / 'activation.json').read_bytes()
published = {name: (SOURCE / name).read_bytes() for name in payload}
origins = load(SOURCE / 'packaging-origins.json')
assert len(origins['files']) == 20
for row in origins['files']:
    published[row['path']] = (SOURCE / row['path']).read_bytes()
published.update({'activation.json': config_raw, 'component-tool-closure.json': closure_raw,
    'reviewed-pins.json': pins_path.read_bytes(), 'root-review.json': review_path.read_bytes()})
assert len(published) == 44
for name, value in published.items():
    path = str(DEST / name)
    expected_inputs[path] = {'path': path, 'sha256': sha(value), 'bytes': len(value), 'boundary': str(DEST)}
expected_seal = {'schemaVersion': 1, 'state': 'CONSUMERS355_ACTIVATED_SOURCE_TOOL_AND_NATIVE_CONSUMED_SEAL',
    'inputs': [expected_inputs[p] for p in sorted(expected_inputs)], 'toolTrees': context['toolTrees'],
    'toolLinks': context['toolLinks'], 'invocation': context['invocation']}
assert len(expected_inputs) == 7268
seal_raw = encoded(expected_seal)
assert seal_raw == (DEST / 'input-freeze.json').read_bytes()
compiled = published['runtime-preflight.template.mjs'].decode().replace('@CONFIG_SHA@', sha(config_raw)).replace('@INPUTS_SHA@', sha(seal_raw)).encode()
published['runtime-preflight.mjs'] = compiled
published['input-freeze.json'] = seal_raw
expected_receipt = {'schemaVersion': 1, 'state': 'ROOT_REVIEWED_CONSUMERS355_VALIDATION_SOURCE_FAMILY_CREATED_NOT_EXECUTED',
    'sourceProposalIndexSha256': SOURCE_SHA, 'nativeProposalIndexSha256': NATIVE_SHA, 'pinsSha256': config['pinsSha256'],
    'rootReviewSha256': config['rootReviewSha256'], 'inputFreezeSha256': sha(seal_raw), 'componentToolClosureSha256': sha(closure_raw),
    'nativeConfiguredSourceRoot': config['nativeConfiguredSourceRoot'], 'componentToolRoot': new_snapshot,
    'frozenNativeRoot': '/tmp/starling-node-compat/production-consumers-v1/native-freeze', 'originalPreparationRoot': str(SOURCE),
    'packagingSnapshotRebasedWithoutNativeMetadataChange': True, 'actual': actual, 'componentOrGuestExecuted': False, 'operationalAdmission': False}
published['source-receipt.json'] = encoded(expected_receipt)
assert len(published) == 47
assert set(published) == {r['path'] for r in dest_index['files']}
for name, value in published.items():
    assert value == (DEST / name).read_bytes(), name
assert encoded({'schemaVersion': 1, 'state': 'ROOT_REVIEWED_CONSUMERS355_VALIDATION_SOURCE_FAMILY_NOT_EXECUTED',
    'files': [{'path': name, 'sha256': sha(value), 'bytes': len(value)} for name, value in sorted(published.items())],
    'runtimeAcceptanceClaim': False}) == (DEST / 'index.json').read_bytes()

# Recheck the physical activated loader/data graph, not just native tool rows.
snapshot = DEST / 'packaging-tools'
assert len(closure['files']) == 20
for kind in ['files', 'packages', 'endpoints', 'packageData']:
    for row in closure[kind]:
        verify(row, role='physical-packaging:' + kind)
modules = {r['relativePath'] for r in closure['files'] if r['kind'] == 'local-module'}
active_data = {r['relativePath'] for r in closure['files'] if r['kind'] != 'local-module'}
assert len(modules) == 12 and len(active_data) == 8
pending, visited, edges, texts = list(closure['entries']), set(), [], {}
while pending:
    name = pending.pop(0)
    if name in visited:
        continue
    visited.add(name)
    value = text(snapshot / name)
    texts[name] = value
    for match in re.finditer(r'^\s*import\b[^\n;]*?\bfrom\s*([\'"])([^\'"]+)\1\s*;?', value, re.M):
        request = match[2]
        if request.startswith('node:'):
            continue
        assert request.startswith('.')
        target = str((snapshot / name).parent.joinpath(request).resolve().relative_to(snapshot))
        edges.append({'importer': name, 'request': request, 'target': target})
        pending.append(target)
json_key = lambda r: json.dumps(r, separators=(',', ':'))
assert visited == modules and len(edges) == 13
assert sorted(edges, key=json_key) == sorted(closure['staticImportEdges'], key=json_key)
inactive = {r['path'] for r in closure['inactiveLazyReads']}
assert len(inactive) == 12
urls = []
for name, value in texts.items():
    for match in re.finditer(r'new URL\(([\'"])([^\'"]+)\1,\s*import\.meta\.url\)', value):
        request = match[2]
        target_path = (snapshot / name).parent.joinpath(request).resolve()
        if request == '../../':
            assert target_path == snapshot
            continue
        target = str(target_path.relative_to(snapshot))
        assert target in active_data or target in inactive
        urls.append({'importer': name, 'request': request, 'target': target,
            'usage': 'selected-import-time' if target in active_data else 'inactive-selector-only'})
assert len(urls) == 24 and sorted(urls, key=json_key) == sorted(closure['relativeDataReads'], key=json_key)
assert [len(closure[k]) for k in ['packages', 'endpoints', 'packageData']] == [4, 5, 27]
tree_files = 0
for tree in seal['toolTrees']:
    base = Path(tree['path'])
    assert str(base.resolve()) == tree['realPath']
    entries = []
    for current, dirs, files in os.walk(base, followlinks=False):
        for name in dirs + files:
            path = Path(current) / name
            mode = path.lstat().st_mode
            kind = 'symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file'
            entries.append({'path': str(path.relative_to(base)), 'kind': kind})
            tree_files += kind == 'file'
    assert sorted(entries, key=lambda r: r['path']) == tree['entries']
assert len(seal['toolTrees']) == 2 and len(seal['toolLinks']) == 22 and tree_files == 4890
for row in seal['toolLinks']:
    path = Path(row['path'])
    assert path.is_symlink() and os.readlink(path) == row['linkText'] and str(path.resolve()) == row['resolvedTarget']
    assert any(path.resolve().is_relative_to(Path(t['realPath'])) if hasattr(path, 'is_relative_to') else str(path.resolve()).startswith(t['realPath'] + '/') for t in seal['toolTrees'])
    if row['targetKind'] == 'file':
        assert path.resolve().is_file() and digest(path.resolve()) == (row['targetSha256'], row['targetBytes'])
    else:
        assert row['targetKind'] == 'directory' and path.resolve().is_dir()

root_five = {str((ROOT / p).resolve()) for p in ['builtins/node-compat/classic-streams/classic-core.generated.mjs',
    'builtins/node-compat/classic-streams/transformation-receipt.json', 'builtins/node-compat/classic-streams/factories.generated.h',
    'tests/node-compat/build-engine.sh', 'tests/node-compat/classic-streams-admission.mjs']}
assert not [r for r in seal['inputs'] if str(Path(r['path']).resolve()) in root_five]
assert not [r for r in source_inputs['files'] if str(Path(r['path']).resolve()) in root_five]

driver = text(DEST / 'run-validation.mjs')
assert 'const diagnostic=assertDisabledDenial(row,failure)' in driver
assert driver.index("transportFile=await save('calls/'+id+'.transport.json',transportReturnEnvelope(raw))") < driver.index("assert.equal(typeof raw,'string')")
assert driver.index("rawFile=await save('calls/'+id+'.raw.txt',raw)") < driver.index("assert.equal(typeof raw,'string')")
assert 'selectedManifestsForEngine(' not in driver and 'builtinManifests:admission.selectedManifests' in driver
assert 'export run: func(index: u32) -> string' in driver
assert 'export module-contract: func() -> string' in driver and 'export ordinary-gc: func() -> string' in driver
assert 'selectedInterfaces:[]' in driver and 'assert.deepEqual(interfaceAudit.emittedImports,[])' in driver
assert 'records.length,190' in driver and 'initializerRecords.length,11' in driver and 'denials.length,8' in driver
assert 'GC requires explicit reviewed normal namespace/corpus proof' in driver
assert 'sourceFamilyIndexSha256,indexSha' in driver and 'normalEngineSha256,admission.normalEngineSha256' in driver
for name in payload:
    assert (DEST / name).read_bytes() == (SOURCE / name).read_bytes()
for name in ['component.mjs', 'consumer.cjs', 'differential.mjs', 'profiles.mjs', 'extras.mjs', 'initializers.mjs', 'disabled-fixtures.mjs']:
    assert not re.search(r'Buffer\.from\(\s*\[', text(DEST / name)), name
assert 'opaque-unexpected-transport-type' in text(DEST / 'transport-return.mjs')
assert 'propertiesRead:false' in text(DEST / 'transport-return.mjs')
assert 'reasons.every(reason=>reason===expected)' in text(DEST / 'denial-checks.mjs')
assert 'config.nativeConfiguredSourceRoot,resolve(config.bootstrapRoot' in compiled.decode()
assert 'metadata.sourceManifest.length,355' in compiled.decode()
assert 'consumersBootstrapPreflight' in compiled.decode() and 'await recheck();return Object.freeze' in compiled.decode()

write('original-input-context.json', {'schemaVersion': 1, 'sourceInputRoot': str(SOURCE),
    'sourceInputManifest': {'path': str(SOURCE / 'source-inputs.json'), 'sha256': digest(SOURCE / 'source-inputs.json')[0], 'rows': 5250},
    'activatedInputManifest': {'path': str(DEST / 'input-freeze.json'), 'sha256': sha(seal_raw), 'rows': 7268},
    'nativeConfiguredSourceRoot': config['nativeConfiguredSourceRoot'], 'nativeOriginalPreparationRoot': str(original_native),
    'frozenSourceRoot': '/tmp/starling-node-compat/production-consumers-v1/native-freeze/source',
    'componentToolRoot': new_snapshot, 'nativeNestedPreparationRowsReinterpreted': False,
    'nativeToolInventoryUsedAsPackagingAuthority': False, 'directLiveRootFiveRows': 0,
    'originalInputContext7268': seal['inputs']})
write('checked-reference-ledger.json', {'schemaVersion': 1, 'rows': refs, 'uniqueHashedPhysicalFiles': len(cache)})
result = {'schemaVersion': 1, 'state': 'INDEPENDENT_CONSUMERS355_VALIDATION_V2_SOURCE_FAMILY_REVIEW_PASS',
    'generatedIndexSha256': DEST_SHA, 'generatedFiles': 47, 'consumedRows': 7268,
    'sourceProposalIndexSha256': SOURCE_SHA, 'sourceProposalFiles': 80, 'sourceProposalOriginalReferences': 5250,
    'sourcePeerIndexSha256': '13bc711de7653539bff7b81d9dcb6caebcdfa6dc484d8747e8169c257130655a',
    'completePublisherByteReconstruction': True, 'completeConsumedInputUnionReconstruction': True,
    'reconstructedGeneratedBoundaryRows': 44, 'primitiveSelfBinding': {'configSha256': sha(config_raw), 'inputFreezeSha256': sha(seal_raw), 'compiledTemplateExact': True},
    'native': native_summaries, 'RuntimeOnly': None, 'nativeProducerIndexSha256': NATIVE_SHA,
    'nativeOriginalAndStageIndexedFiles': 59, 'stagedNativeToolFiles': 767,
    'physicalPackaging': {'localModules': 12, 'staticEdges': 13, 'selectedDataAndAdapter': 8,
        'relativeDataUrls': 24, 'inactiveLazySelectorsNotCalled': 12, 'packages': 4, 'endpoints': 5, 'packageProvenanceFiles': 27,
        'toolTrees': 2, 'toolLinks': 22, 'regularTreeFiles': 4890},
    'liveAdapterAndWit': {'adapterSha256': live['adapter']['sha256'], 'adapterBytes': 53512, 'witRows': 7},
    'contextsDistinctAndActual': True, 'directLiveRootFiveRows': 0,
    'corpusUnchangedFromReviewedSource': {'cases': 38, 'nodeOriginal': 18, 'profiles': 12, 'extraNode': 8,
        'normalPlannedRecords': 190, 'initializers': 11, 'combinedOwnerGcPlannedRecords': 4, 'offDenials': 8, 'offSmokePlannedRecords': 5},
    'M1DiagnosticFixActive': True, 'M2TransportRetentionFixActive': True, 'gcExplicitNormalResultGateRetained': True,
    'RootActivation': {'session': 34235, 'pid': 72182, 'rawExitCode': 0, 'observedByThisReader': False,
        'receiptSha256': digest(root_receipt_path)[0], 'terminalDescriptorRehashed': True, 'stdoutParsed': True},
    'execution': {'readerOnly': True, 'ownerModulesImported': False, 'ownerActionsOrPreflightsOrBootstrapExecuted': False,
        'factoryOrBundlerOrComponentizerOrCompilerExecuted': False, 'guestOrTargetHostOrTimingExecuted': False},
    'operationalAdmission': False, 'runtimeAcceptanceClaim': False, 'findings': [],
    'scope': ['Generated source publication only; native runtimeBackendProof remains false/null/null.',
        'No current component, emitted import audit, guest, codec or consumer correctness result is inferred from this publication.',
        'Future components must emit imports[] with exact public scalar exports under authenticated driver checks.',
        'No old350 or293 runtime/source metadata projection, old Root context rebasing, or old runtime pass transfer.',
        'Combined-owner GC only; no isolated-root, reset, request reuse, HTTP, full Node or performance claim.',
        'Finite pinned-source regex import/data scan; package endpoint files and recorded resolution paths authenticated without a live resolver.']}
write('results.json', result)
print(json.dumps({'state': result['state'], 'generatedFiles': 47, 'consumedRows': 7268, 'publisherBytesExact': True,
    'physicalModules': 12, 'directLiveRootFiveRows': 0, 'ownerActionsExecuted': False}))
