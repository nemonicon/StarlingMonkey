"""Independent finite data/source reader; never imports an owner module."""
from pathlib import Path
import ast
import collections
import hashlib
import json
import os
import re
import stat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
SOURCE = FAMILY / 'component-validation-candidate-v2'
OLD = FAMILY / 'component-validation-candidate-v1'
ROOT = HERE.parents[3]
EXPECTED = 'a75ee76c1291988cec55252f8ab54e451f31b1593f22119759bada058860002b'
OLD_SHA = '5659c2885860e1e926e20e8c59a0fac48c2869b401a7e55c190783b2dad9bf79'
HOLD_SHA = '2a76b6c53901ebd61ebe4ae9da1463a047a92643f6e66a3ae2950d00665a04fb'
NATIVE_SHA = '9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378'
cache, checked, checks = {}, [], []

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def data(path):
    return Path(path).read_bytes()

def load(path):
    return json.loads(data(path))

def text(name):
    return (SOURCE / name).read_text()

def check(name, condition=True):
    assert condition, name
    checks.append(name)

def identity(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)

def digest(path):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    key = (str(path.resolve()), identity(before))
    if key not in cache:
        h = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
        assert identity(path.lstat()) == identity(before), ('changed during read', str(path))
        cache[key] = (h.hexdigest(), before.st_size)
    return cache[key]

def verify(row, base=None, role='reference'):
    path = Path(row['path'])
    if not path.is_absolute():
        assert base is not None and '..' not in path.parts
        path = base / path
    actual = digest(path)
    assert actual[0] == row['sha256'], (str(path), actual[0], row['sha256'])
    if 'bytes' in row:
        assert actual[1] == row['bytes'], str(path)
    real = row.get('realpath', row.get('realPath'))
    if real is not None:
        assert str(path.resolve()) == real, (str(path), real)
    checked.append({'path': str(path), 'sha256': actual[0], 'bytes': actual[1], 'role': role})

def indexed(base, expected, count):
    verify({'path': str(base / 'index.json'), 'sha256': expected}, role='sealed-index')
    index = load(base / 'index.json')
    assert len(index['files']) == count
    assert len({row['path'] for row in index['files']}) == count
    for row in index['files']:
        assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
        verify(row, base, 'indexed:' + base.name)
    return index

def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True)
        stream.write('\n')

def citation(name, needle):
    value = text(name)
    assert needle in value, (name, needle)
    return {'path': str(SOURCE / name), 'line': value[:value.index(needle)].count('\n') + 1,
            'sha256': digest(SOURCE / name)[0], 'needle': needle}

index = indexed(SOURCE, EXPECTED, 80)
inputs = load(SOURCE / 'source-inputs.json')
assert len(inputs['files']) == 5250 and len({r['path'] for r in inputs['files']}) == 5250
for row in inputs['files']:
    assert Path(row['path']).is_absolute()
    verify(row, role='source-preparation-reference')
check('all80IndexedAnd5250PreparationRowsExact')
before_index = indexed(OLD, OLD_SHA, 65)
hold = FAMILY / 'independent-component-validation-source-review-v1'
indexed(hold, HOLD_SHA, 17)
before_inputs = load(OLD / 'source-inputs.json')
assert len(before_inputs['files']) == 5151
new_rows = {r['path']: r for r in inputs['files']}
for row in before_inputs['files']:
    current = new_rows[row['path']]
    assert (current['sha256'], current['bytes']) == (row['sha256'], row['bytes'])
    assert 'UNCHANGED_V1_ORIGINAL_CONTEXT_PREPARATION_REFERENCE' in current['roles']
for row in load(hold / 'index.json')['files']:
    assert 'INDEXED_ONLY_V1_SOURCE_PEER_HOLD_NOT_PREPARATION' in new_rows[str(hold / row['path'])]['roles']
check('v1AndComplete17FileHoldPreservedOriginal5151ContextsNotReinterpreted')

proof = load(SOURCE / 'successor-derivations.json')
assert len(proof['edits']) == 8
assert collections.Counter(r['path'] for r in proof['edits']) == {'run-validation.mjs': 4, 'activate.py': 3, 'test-closure.py': 1}
roundtrips = []
for name in sorted({r['path'] for r in proof['edits']}):
    before = data(OLD / name).decode()
    value = before
    rows = [r for r in proof['edits'] if r['path'] == name]
    for row in rows:
        assert value.count(row['old']) == row['count']
        value = value.replace(row['old'], row['new'])
    assert value.encode() == data(SOURCE / name)
    for row in reversed(rows):
        for at in reversed(row['afterOffsets']):
            assert value[at:at + len(row['new'])] == row['new']
            value = value[:at] + row['old'] + value[at + len(row['new']):]
    assert value == before
    roundtrips.append({'path': name, 'edits': len(rows), 'forwardExact': True, 'offsetReverseExact': True})
unchanged = load(SOURCE / 'unchanged-v1-payloads.json')['files']
assert len(unchanged) == 53
for name in unchanged:
    assert data(SOURCE / name) == data(OLD / name), name
check('eightExactForwardAndOffsetReverseEditsAnd53UnchangedPayloads')

old_closure = load(OLD / 'component-tool-closure.json')
closure = load(SOURCE / 'component-tool-closure.json')
old_snapshot, snapshot = OLD / 'packaging-tools', SOURCE / 'packaging-tools'
old_closure['componentToolRoot'] = str(snapshot)
for row in old_closure['files']:
    assert row['path'].startswith(str(old_snapshot) + '/')
    row['path'] = str(snapshot) + row['path'][len(str(old_snapshot)):]
    row['realPath'] = row['path']
assert old_closure == closure
check('packagingClosureOnlySelfDescriptorPathRebase')

native_relative = Path('tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2')
native_original = ROOT / native_relative
native_staged = Path('/tmp/starling-node-compat/consumers-source-v2') / native_relative
native = indexed(native_original, NATIVE_SHA, 59)
indexed(native_staged, NATIVE_SHA, 59)
for row in native['files']:
    assert digest(native_original / row['path']) == digest(native_staged / row['path'])
indexed(FAMILY / 'independent-native-integration-v2-source-review-v1',
        '283008266ff55471723d1aff05bc66c5d48663346f1d4bc90752c4278f827811', 8)
toolpins = load(native_staged / 'artifact-tools/tool-pins.json')
assert len(toolpins['toolDependencies']) == 767
for row in toolpins['toolDependencies']:
    path = native_staged.parents[3] / row['path']
    verify({**row, 'path': str(path)}, role='configured355-native-tool')
check('genuine355OriginalAndStaged59Plus767ToolDependenciesAuthenticatedNotInvoked')

origins = load(SOURCE / 'packaging-origins.json')
assert len(origins['files']) == 20
for row in origins['files']:
    verify(row, SOURCE, 'packaging-snapshot')
    verify({**row, 'path': row['original']}, role='packaging-exact-original')
for group in ['files', 'packages', 'endpoints', 'packageData']:
    for row in closure[group]:
        verify(row, role='physical-component-closure:' + group)
assert [len(closure[group]) for group in ['files', 'packages', 'endpoints', 'packageData']] == [20, 4, 5, 27]
modules = {r['relativePath'] for r in closure['files'] if r['kind'] == 'local-module'}
selected_data = {r['relativePath'] for r in closure['files'] if r['kind'] != 'local-module'}
assert len(modules) == 12 and len(selected_data) == 8
pending, visited, edges, module_text = list(closure['entries']), set(), [], {}
while pending:
    name = pending.pop(0)
    if name in visited:
        continue
    visited.add(name)
    source = (snapshot / name).read_text()
    module_text[name] = source
    for match in re.finditer(r'^\s*import\b[^\n;]*?\bfrom\s*([\'"])([^\'"]+)\1\s*;?', source, re.M):
        request = match[2]
        if request.startswith('node:'):
            continue
        assert request.startswith('.')
        target = str((snapshot / name).parent.joinpath(request).resolve().relative_to(snapshot))
        edges.append({'importer': name, 'request': request, 'target': target})
        pending.append(target)
assert visited == modules and len(edges) == 13
key = lambda row: json.dumps(row, separators=(',', ':'))
assert sorted(edges, key=key) == sorted(closure['staticImportEdges'], key=key)
inactive = {r['path'] for r in closure['inactiveLazyReads']}
assert len(inactive) == 12
urls = []
for name, source in module_text.items():
    for match in re.finditer(r'new URL\(([\'"])([^\'"]+)\1,\s*import\.meta\.url\)', source):
        request = match[2]
        target_path = (snapshot / name).parent.joinpath(request).resolve()
        if request == '../../':
            assert target_path == snapshot
            continue
        target = str(target_path.relative_to(snapshot))
        assert target in selected_data or target in inactive
        urls.append({'importer': name, 'request': request, 'target': target,
                     'usage': 'selected-import-time' if target in selected_data else 'inactive-selector-only'})
assert len(urls) == 24 and sorted(urls, key=key) == sorted(closure['relativeDataReads'], key=key)
assert {r['target'] for r in urls if r['usage'] == 'inactive-selector-only'} == inactive
for row in closure['packages']:
    assert load(row['path'])['version'] == row['version']
assert [r['version'] for r in closure['packages']] == ['0.23.0', '1.40.0', '1.2.16', '0.23.0']
provenance_path = Path('/tmp/starling-node-compat/import-abi-clock-v2-build/package/splicer-build.json')
provenance = load(provenance_path)
assert provenance['packagingVersion'] == 'componentize-js-0.23.0+sm-import-i32.v1+sm-clock-errno.v1'
assert len(provenance['checkedFiles']) == 26
for row in provenance['checkedFiles']:
    verify(row, provenance_path.parent, 'selected-splicer-provenance')
check('actual12Modules13Edges8SelectedData4Packages5Endpoints27ProvenanceInputs')

context = load(SOURCE / 'tool-context.json')
assert len(context['toolTrees']) == 2 and len(context['toolLinks']) == 22 and len(context['inputs']) == 4892
tree_files = 0
for tree in context['toolTrees']:
    base = Path(tree['path'])
    assert str(base.resolve()) == tree['realPath']
    observed = []
    for current, dirs, files in os.walk(base, followlinks=False):
        for name in dirs + files:
            path = Path(current) / name
            mode = path.lstat().st_mode
            kind = 'symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file' if stat.S_ISREG(mode) else None
            assert kind
            observed.append({'path': str(path.relative_to(base)), 'kind': kind})
            if kind == 'file':
                tree_files += 1
    assert sorted(observed, key=lambda r: r['path']) == tree['entries']
assert tree_files == 4890
for row in context['toolLinks']:
    path = Path(row['path'])
    assert path.is_symlink() and os.readlink(path) == row['linkText']
    assert str(path.resolve()) == row['resolvedTarget']
    if row['targetKind'] == 'file':
        assert digest(path.resolve()) == (row['targetSha256'], row['targetBytes'])
    else:
        assert row['targetKind'] == 'directory' and path.resolve().is_dir()
for row in context['inputs']:
    verify(row, role='tool-tree-and-invocation-binary')
outside = [r['path'] for r in context['inputs'] if not any(Path(r['path']).resolve().is_relative_to(Path(t['realPath'])) for t in context['toolTrees'])]
assert outside == [context['invocation']['nodeRealPath'], context['invocation']['wasmtimeRealPath']]
check('exactTwoToolTrees22Links4890RegularFilesPlusNodeAndWasmtime')

five = {ROOT / name for name in [
    'builtins/node-compat/classic-streams/classic-core.generated.mjs',
    'builtins/node-compat/classic-streams/transformation-receipt.json',
    'builtins/node-compat/classic-streams/factories.generated.h',
    'tests/node-compat/build-engine.sh', 'tests/node-compat/classic-streams-admission.mjs']}
assert not any(Path(r['path']) in five for r in inputs['files'])
assert not any(Path(r['original']) in five for r in origins['files'])
live = load(SOURCE / 'live-inputs.json')
assert live['adapter']['sha256'] == '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
assert live['adapter']['bytes'] == 53512 and len(live['wit']) == 7
for row in [live['adapter']] + live['wit']:
    verify(row, role='live-adapter-and-seven-wit')
    assert row['path'] in new_rows
check('liveEightRetainedNoDirectPromotedRootFiveReads')

bundler = text('packaging-tools/tests/node-compat/profile-bundler.mjs')
templates = {}
for kind, prefix in [('esm', 'Node builtin is not admitted by this profile:'), ('cjs', 'CommonJS require is not admitted:')]:
    values = [m[1] for m in re.finditer(r'throw new Error\(`([^`]+)`\)', bundler) if m[1].startswith(prefix)]
    assert len(values) == 1
    templates[kind] = values[0]
assert templates == {'esm': 'Node builtin is not admitted by this profile: ${source}', 'cjs': 'CommonJS require is not admitted: ${specifier}'}
helper = text('denial-checks.mjs')
assert "'default-esm':'esm','named-esm':'esm','namespace-esm':'esm','literal-cjs':'cjs'" in helper
assert 'reasons.length>0&&reasons.every(reason=>reason===expected)' in helper
reason_re = re.compile(r'(?:Node builtin is not admitted by this profile:|CommonJS require is not admitted:) [^\s\"\'`()]+')
denials = []
for specifier in ['node:stream/consumers', 'stream/consumers']:
    for kind in ['default-esm', 'named-esm', 'namespace-esm', 'literal-cjs']:
        category = 'cjs' if kind == 'literal-cjs' else 'esm'
        expected = templates[category].replace('${specifier}' if category == 'cjs' else '${source}', specifier)
        accepted = lambda message: bool((rows := reason_re.findall(message))) and all(r == expected for r in rows)
        assert accepted(expected) and accepted('Build failed\n' + expected + '\n' + expected)
        assert not accepted('SyntaxError: unrelated fixture failure')
        other_category = templates['esm' if category == 'cjs' else 'cjs'].replace('${source}' if category == 'cjs' else '${specifier}', specifier)
        assert not accepted(other_category)
        other_id = 'stream/consumers' if specifier == 'node:stream/consumers' else 'node:stream/consumers'
        assert not accepted(expected.replace(specifier, other_id))
        assert not accepted(expected + '-extra') and not accepted(expected + '\n' + other_category)
        denials.append({'id': specifier, 'kind': kind, 'category': category, 'expectedReason': expected,
                       'exactAndWrappedAcceptedByIndependentFinitePredicate': True,
                       'wrongCategoryIdUnrelatedMixedAndLongerIdRejected': True})
driver, carrier = text('run-validation.mjs'), text('transport-return.mjs')
assert "assert.equal(denials.length,8);assert.equal(componentizeCalls,0)" in driver
observed = driver[driver.index('async function observed('):driver.index('const host=resolve(')]
assert observed.index('transportReturnEnvelope(raw)') < observed.index("assert.equal(typeof raw,'string')") < observed.index('JSON.parse(raw)')
assert "if(typeof raw==='string')rawFile=await save('calls/'+id+'.raw.txt',raw)" in observed
assert observed.index(".raw.txt',raw") < observed.index("assert.equal(typeof raw,'string')")
assert "return{id,value,rawFile,transportFile}" in observed
assert "const type=typeof value;" in carrier
assert carrier.index("if(type==='string')") < carrier.index("if(value===null)") < carrier.index("if(type==='undefined')")
assert "decimal:value.toString()" in carrier and "if(type==='bigint')" in carrier
opaque = carrier[carrier.index("return{type,kind:'opaque-unexpected-transport-type'"):]
assert opaque == "return{type,kind:'opaque-unexpected-transport-type',fullPrimitiveValueCaptured:false,propertiesRead:false};\n}\n"
assert 'JSON.stringify' not in carrier and 'getPrototypeOf' not in carrier and 'Reflect.' not in carrier
check('M1ExactFiniteKindsAndSpecifierReasonsAndEightBeforeComponentizerProtocol')
check('M2TypedEnvelopeBeforeAssertionValidRawUnchangedOpaqueNoPropertyReads')

# Reconstruct inherited fixture afterimages independently as text, not imports.
original = (FAMILY / 'node-checks.mjs').read_text()
node_report = load(FAMILY / 'node-results.json')
assert digest(FAMILY / 'node-checks.mjs')[0] == node_report['sources']['node-checks.mjs']
differential = original[:original.index('export async function blobChecks(consumers) {')]
for fragment in ["const BlobCtor = Blob;\n", "const BufferCtor = globalThis.Buffer;\n", ",new BlobCtor(['a'])"]:
    assert differential.count(fragment) == 1
    differential = differential.replace(fragment, '')
differential = differential.replace('export async function textChecks(consumers) {', 'export async function textChecks(consumers, selected = null) {')
differential = differential.replace('  async function check(name, run) { cases.push({name,result:await run()}); }',
    '  let index=0; async function check(name, run) { const current=index++; if(selected===null||selected===current)cases.push({name,result:await run()}); }')
assert differential == text('differential.mjs')
node_expected = json.loads(json.dumps(node_report['text']))
invalid = next(r for r in node_expected if r['name'] == 'invalid byte chunks reject with error type and code')
assert len(invalid['result']) == 6
invalid['result'] = invalid['result'][:5]
node_oracle = load(SOURCE / 'node-oracle.json')
assert len(node_expected) == 18 and node_expected == node_oracle['cases']
assert node_oracle['sourceReportSha256'] == digest(FAMILY / 'node-results.json')[0]
assert len(load(SOURCE / 'profile-oracle-ancestry.json')['oldProfiles']) == 12
assert len(load(SOURCE / 'extra-node-oracle.json')['cases']) == 8
for name in ['component.mjs', 'consumer.cjs', 'differential.mjs', 'profiles.mjs', 'extras.mjs', 'initializers.mjs', 'disabled-fixtures.mjs']:
    assert not re.search(r'Buffer\.from\(\s*\[', text(name)), name
assert "import required from './consumer.cjs'" in text('component.mjs')
assert "const snapshotText=await consumers.text" in text('component.mjs')
assert "passedToConsumer:false" in text('component.mjs') and "vmTemporaryRootsIsolated:false" in text('component.mjs')
check('unchanged38CasesOraclesAndFiniteU8ABSnapshotPublicGCAndNoBlobVector')

authority = load(SOURCE / 'future-authority.json')
assert len(authority['variants']) == 4 and all(v is None for v in authority['variants'].values())
for key in ['reviewedPinsPath', 'reviewedPinsSha256', 'rootReviewPath', 'rootReviewSha256']:
    assert authority[key] is None
assert authority['operationalAdmission'] is False and authority['runtimeAcceptanceClaim'] is False
preflight = text('runtime-preflight.mjs')
assert 'throw new Error(' in preflight and 'import ' not in preflight
assert not (FAMILY / 'component-validation-activated-v2').exists() and not (FAMILY / 'component-validation-activated-v2').is_symlink()
template, activation, consumed = text('runtime-preflight.template.mjs'), text('activate.py'), text('consumed.mjs')
assert 'consumersBootstrapPreflight' in template and 'native.metadata.sourceManifest.length,355' in template
assert 'selectedManifestsForEngine(' not in template + driver
assert 'metadata.sourceManifest=' not in template + driver
assert 'builtinManifests:admission.selectedManifests' in driver
assert template.index('assert(config.actual[variant]') < template.index('await verifyConsumedSeal') < template.index('await import(')
assert driver.index('await validationPreflight') < driver.index('const output=') < driver.index('loadToolchain()')
assert 'original==staged' in activation and "'component-validation-activated-v2'" in activation
assert consumed.index("assert.equal(hash(raw), expectedManifestSha") < consumed.index('const document = JSON.parse(raw)')
assert 'async function recheck(){await regular' in template and 'await verifyConsumedSeal(here,INPUTS_SHA' in template
assert driver.index('await admission.recheck();await live();const report=') < driver.index("await save('results.json'") < driver.index("await save('completion.json'")
assert 'requiresIndependentTerminalExitZero:true' in driver and 'requiresIndependentExitZero:true' in driver
assert "timeoutMs:600000" in driver and 'result.terminalExitZeroObserved&&result.ownedGroupGone' in driver
assert "sourceFamilyIndexSha256,indexSha" in driver and "records.length,190" in driver
check('nullAuthorityBeforeLoadersFreshOutputAndGenuine355NotProjected350OperationalGuard')
check('capturedManifestAndConfigRecheckFullCompletionAndExternalRawExitRequired')

for path in SOURCE.glob('*.py'):
    ast.parse(data(path), filename=str(path))
owner_counts = {}
for name, expected in [('source', 64), ('correction', 80), ('closure', 13)]:
    report = load(SOURCE / ('evidence/' + name + '-results.json'))
    assert report['passed'] == expected
    owner_counts[name] = expected
syntax = load(SOURCE / 'evidence/syntax-results.json')
assert syntax['passed'] == len(syntax['commands']) == 35
for row in syntax['commands']:
    assert row['exitCode'] == 0 and row['stderr'] == ''
    assert digest(SOURCE / row['path'])[0] == row['sourceSha256']
owner_counts['syntax'] = 35
check('owner64Plus80Plus13And35SyntaxAuthenticatedNotRerunPythonAstParsed')

citations = {
    'finiteDenialKinds': citation('denial-checks.mjs', 'const kinds='),
    'allReasonsExact': citation('denial-checks.mjs', 'reasons.length>0&&reasons.every'),
    'pinnedEsmReason': citation('packaging-tools/tests/node-compat/profile-bundler.mjs', 'Node builtin is not admitted by this profile: ${source}'),
    'pinnedCjsReason': citation('packaging-tools/tests/node-compat/profile-bundler.mjs', 'CommonJS require is not admitted: ${specifier}'),
    'eightBeforeComponentization': citation('run-validation.mjs', 'assert.equal(denials.length,8);assert.equal(componentizeCalls,0)'),
    'typedBeforeAssertion': citation('run-validation.mjs', 'transportFile=await save('),
    'opaqueCarrier': citation('transport-return.mjs', "kind:'opaque-unexpected-transport-type'"),
    'genuine355Bootstrap': citation('runtime-preflight.template.mjs', 'consumersBootstrapPreflight'),
    'nullGate': citation('runtime-preflight.mjs', 'NULL future authority'),
    'publicAbi': citation('run-validation.mjs', 'export run: func(index: u32) -> string'),
    'normalBeforeGc': citation('run-validation.mjs', 'GC requires explicit reviewed normal namespace/corpus proof'),
    'completion': citation('run-validation.mjs', "await save('completion.json'"),
}
results = {
    'schemaVersion': 1,
    'state': 'INDEPENDENT_CONSUMERS355_COMPONENT_VALIDATION_V2_SOURCE_REVIEW_PASSED',
    'disposition': 'PASS_SOURCE_ONLY_NO_ACTIVATION',
    'reviewedSourceIndexSha256': EXPECTED,
    'indexedFiles': 80,
    'preparationRows': 5250,
    'uniquePhysicalFileVersionsHashed': len(cache),
    'sourceChecks': checks,
    'closedPriorFindings': [
        {'id': 'C355-COMP-M1', 'status': 'closed-in-v2-source', 'observedRuntimeReproduction': False,
         'basis': 'Exact fixture kind/specifier maps to the actual pinned ESM/CJS templates; every parsed denial reason must match. All8 fixtures and zero componentizer boundary unchanged.'},
        {'id': 'C355-COMP-M2', 'status': 'closed-in-v2-source', 'observedRuntimeReproduction': False,
         'basis': 'Typed envelope saved before string assertion; valid raw path/body unchanged. Objects/functions/symbols only opaque typeof, never properties or coercion.'}],
    'remainingConcreteSourceBlockers': [],
    'v1AndHold': {'sourceIndexSha256': OLD_SHA, 'sourceFiles': 65, 'holdIndexSha256': HOLD_SHA,
                  'holdFiles': 17, 'originalPreparationRows': 5151, 'allUnchanged': True,
                  'nestedHistoricalPreparationRowsReinterpreted': False},
    'derivations': {'edits': 8, 'roundtrips': roundtrips, 'unchangedV1Payloads': len(unchanged),
                    'packagingDescriptorRebaseOnly': True},
    'native': {'sourceFiles': 355, 'originalAndStagedProducerIndexSha256': NATIVE_SHA,
               'producerFilesPerContext': 59, 'actualConfiguredTools': 767,
               'futureTuples': authority['variants'], 'metadataProjected': False,
               'operationalAdmission': False, 'bootstrapExecuted': False},
    'physicalClosure': {'packagingModules': 12, 'moduleEdges': 13, 'selectedDataAndAdapter': 8,
                        'relativeDataUrls': 24, 'inactiveLazyReadsNotCalled': 12,
                        'packages': 4, 'endpoints': 5, 'packageProvenanceInputs': 27,
                        'toolTrees': 2, 'toolLinks': 22, 'regularTreeFiles': 4890,
                        'invocationBinaries': 2, 'toolRows': 4892,
                        'liveAdapterAndWit': 8, 'directLiveRootFiveReads': 0},
    'corpusPlansNotRuntimePasses': {'differentialGroups': 18, 'profileGroups': 12,
                                  'additionalNodeGroups': 8, 'totalGuestCases': 38,
                                  'normalReturnedRecords': 190, 'initializerFailures': 11,
                                  'gcReturnedRecordsBehindNormalAuthority': 4,
                                  'offDenialsBeforeComponentization': 8, 'offSmokeReturns': 5,
                                  'allGuestAndOracleBytesUnchanged': True,
                                  'publicRunParameterType': 'u32', 'nativeBlobInvoked': False},
    'ownerReportsAuthenticatedNotRerun': owner_counts,
    'futureActivatedV2Absent': True,
    'execution': {'readerSourceDataAndPythonAstOnly': True, 'ownerModuleImported': False,
                  'ownerTestsOrActionsExecuted': False, 'activationExecuted': False,
                  'preflightOrBootstrapOrVerifierExecuted': False,
                  'factoryOrBundlerOrComponentizerOrCompilerExecuted': False,
                  'guestOrTargetHostOrTimingExecuted': False},
    'limits': [
        'No consumer component/runtime correctness or acceptance from this source review.',
        'Existing355 native artifacts require a separate explicit Root authority and activation; checked-in slots remain null.',
        'Finite import/URL regex reconstruction is for these exact12 source files, not a general JS parser.',
        'Endpoint/package/captured-resolution bytes checked without executing Node package resolution.',
        'Opaque object/function/symbol transport values are not fully captured or inspected.',
        'In-process Jco calls have no deadline or cancellation guarantee; owned Wasmtime child keeps600second bound.',
        'GC retains application/closure owners; VMtemporaryroots, reset, HTTPbody cancellation and reuse are not proved.',
        'No Blob implementation, rawglobalWeb auto-adaptation, fullNode compatibility, performance or operational-admission claim.',
        'Source publisher is an owned fresh-path workflow, not a hostile concurrent-filesystem race guarantee.'
    ],
    'citations': citations,
}
write('diagnostic-template-ledger.json', {'schemaVersion': 1, 'rows': denials,
                                       'basis': 'Independent Python finite reconstruction of exact pinned templates and predicate; no JS/bundler execution.'})
write('checked-reference-ledger.json', {'schemaVersion': 1, 'rows': checked,
                                      'uniquePhysicalFileVersionsHashed': len(cache),
                                      'historicalPreparationContextsReinterpreted': False})
write('results.json', results)
print(json.dumps({'state': results['state'], 'indexedFiles': 80, 'preparationRows': 5250,
                  'physicalVersionsHashed': len(cache), 'checks': len(checks),
                  'priorFindingsClosed': 2, 'remainingConcreteSourceBlockers': 0,
                  'ownerActionsInvoked': False}))
