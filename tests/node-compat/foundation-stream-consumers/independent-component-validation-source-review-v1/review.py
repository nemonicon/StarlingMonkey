"""Independent finite source/data reader. Never import candidate or execute tools."""
from pathlib import Path
import ast
import hashlib
import json
import os
import re
import stat

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'component-validation-candidate-v1'
ROOT = HERE.parents[3]
EXPECTED = '5659c2885860e1e926e20e8c59a0fac48c2869b401a7e55c190783b2dad9bf79'
cache = {}
checked = []

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
    assert path.is_file(), str(path)
    actual = digest(path)
    assert actual[0] == row['sha256'], (str(path), actual[0], row['sha256'])
    if 'bytes' in row:
        assert actual[1] == row['bytes'], str(path)
    real = row.get('realpath', row.get('realPath'))
    if real is not None:
        assert str(path.resolve()) == real, (str(path), real)
    checked.append({'role': role, 'path': str(path), 'sha256': actual[0], 'bytes': actual[1]})

def indexed(base, expected, count):
    assert digest(base / 'index.json')[0] == expected
    index = load(base / 'index.json')
    assert len(index['files']) == count
    assert len({r['path'] for r in index['files']}) == count
    for row in index['files']:
        assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
        verify(row, base, 'indexed:' + base.name)
    return index

def text(name):
    return (SOURCE / name).read_text()

def line(name, needle):
    source = text(name)
    assert needle in source, (name, needle)
    return {'path': str(SOURCE / name), 'line': source[:source.index(needle)].count('\n') + 1,
            'sha256': digest(SOURCE / name)[0], 'needle': needle}

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n')

index = indexed(SOURCE, EXPECTED, 65)
inputs = load(SOURCE / 'source-inputs.json')
assert len(inputs['files']) == 5151
for row in inputs['files']:
    assert Path(row['path']).is_absolute()
    verify(row, role='original-preparation-row')

# The five promoted live files are not consumed directly by this family.
root_five = [ROOT / p for p in [
    'builtins/node-compat/classic-streams/classic-core.generated.mjs',
    'builtins/node-compat/classic-streams/transformation-receipt.json',
    'builtins/node-compat/classic-streams/factories.generated.h',
    'tests/node-compat/build-engine.sh',
    'tests/node-compat/classic-streams-admission.mjs']]
direct_five = [row for row in inputs['files'] if Path(row['path']).resolve() in {p.resolve() for p in root_five}]
assert direct_five == []

# Authenticate the native producer and peer indexed views, never reinterpret their prep rows.
native_relative = Path('tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2')
native_original = ROOT / native_relative
native_staged = Path('/tmp/starling-node-compat/consumers-source-v2') / native_relative
native_sha = '9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378'
ni = indexed(native_original, native_sha, 59)
indexed(native_staged, native_sha, 59)
assert all(digest(native_original / r['path']) == digest(native_staged / r['path']) for r in ni['files'])
peer = HERE.parent / 'independent-native-integration-v2-source-review-v1'
indexed(peer, '283008266ff55471723d1aff05bc66c5d48663346f1d4bc90752c4278f827811', 8)

origins = load(SOURCE / 'packaging-origins.json')
assert len(origins['files']) == 20
for row in origins['files']:
    verify(row, SOURCE, 'immutable-snapshot')
    verify({**row, 'path': row['original']}, role='snapshot-exact-origin')
    assert not (SOURCE / row['path']).is_symlink()
    assert not Path(row['original']).is_symlink()

closure = load(SOURCE / 'component-tool-closure.json')
snapshot = SOURCE / 'packaging-tools'
assert closure['componentToolRoot'] == str(snapshot)
assert closure['scope']['localModules'] == 12
assert closure['scope']['selectedLocalDataAndAdapter'] == 8
for role in ['files', 'packages', 'endpoints', 'packageData']:
    for row in closure[role]:
        verify(row, role='component-closure:' + role)
assert [len(closure[k]) for k in ['files', 'packages', 'endpoints', 'packageData']] == [20, 4, 5, 27]
modules = {r['relativePath'] for r in closure['files'] if r['kind'] == 'local-module'}
data = {r['relativePath'] for r in closure['files'] if r['kind'] != 'local-module'}
assert len(modules) == 12 and len(data) == 8
edges = []
visited = set()
pending = list(closure['entries'])
texts = {}
while pending:
    name = pending.pop(0)
    if name in visited:
        continue
    visited.add(name)
    source = (snapshot / name).read_text()
    texts[name] = source
    for match in re.finditer(r'^\s*import\b[^\n;]*?\bfrom\s*([\'"])([^\'"]+)\1\s*;?', source, re.M):
        request = match[2]
        if request.startswith('node:'):
            continue
        assert request.startswith('.')
        target = (snapshot / name).parent.joinpath(request).resolve().relative_to(snapshot)
        target = str(target)
        edges.append({'importer': name, 'request': request, 'target': target})
        pending.append(target)
assert visited == modules
key = lambda r: json.dumps(r, separators=(',', ':'))
assert sorted(edges, key=key) == sorted(closure['staticImportEdges'], key=key)
assert len(edges) == 13
inactive = {r['path'] for r in closure['inactiveLazyReads']}
assert len(inactive) == 12
urls = []
for name, source in texts.items():
    for match in re.finditer(r'new URL\(([\'"])([^\'"]+)\1,\s*import\.meta\.url\)', source):
        request = match[2]
        target_path = (snapshot / name).parent.joinpath(request).resolve()
        if request == '../../':
            assert target_path == snapshot
            continue
        target = str(target_path.relative_to(snapshot))
        assert target in data or target in inactive
        urls.append({'importer': name, 'request': request, 'target': target,
                     'usage': 'selected-import-time' if target in data else 'inactive-selector-only'})
assert sorted(urls, key=key) == sorted(closure['relativeDataReads'], key=key)
assert len(urls) == 24
assert {r['target'] for r in urls if r['usage'] == 'inactive-selector-only'} == inactive
for row in closure['packages']:
    package = load(row['path'])
    assert package['version'] == row['version']
assert [r['version'] for r in closure['packages']] == ['0.23.0', '1.40.0', '1.2.16', '0.23.0']
provenance_path = Path('/tmp/starling-node-compat/import-abi-clock-v2-build/package/splicer-build.json')
provenance = load(provenance_path)
assert provenance['packagingVersion'] == 'componentize-js-0.23.0+sm-import-i32.v1+sm-clock-errno.v1'
assert len(provenance['checkedFiles']) == 26
for row in provenance['checkedFiles']:
    verify(row, provenance_path.parent, 'package-splicer-provenance')

context = load(SOURCE / 'tool-context.json')
assert len(context['toolTrees']) == 2 and len(context['toolLinks']) == 22 and len(context['inputs']) == 4892
tree_file_count = 0
for tree in context['toolTrees']:
    base = Path(tree['path'])
    assert str(base.resolve()) == tree['realPath']
    actual = []
    for current, dirs, files in os.walk(base, followlinks=False):
        for name in dirs + files:
            path = Path(current) / name
            mode = path.lstat().st_mode
            kind = 'symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file'
            actual.append({'path': str(path.relative_to(base)), 'kind': kind})
            if kind == 'file':
                tree_file_count += 1
    assert sorted(actual, key=lambda r: r['path']) == tree['entries']
assert tree_file_count == 4890
for row in context['toolLinks']:
    path = Path(row['path'])
    assert path.is_symlink() and os.readlink(path) == row['linkText']
    assert str(path.resolve()) == row['resolvedTarget']
    if row['targetKind'] == 'file':
        assert path.resolve().is_file()
        assert digest(path.resolve()) == (row['targetSha256'], row['targetBytes'])
    else:
        assert row['targetKind'] == 'directory' and path.resolve().is_dir()
for row in context['inputs']:
    verify(row, role='tool-context-file')

# Independently reconstruct the finite fixture derivations as text/data, not imports.
family = SOURCE.parent
original = (family / 'node-checks.mjs').read_text()
node_report = load(family / 'node-results.json')
assert digest(family / 'node-checks.mjs')[0] == node_report['sources']['node-checks.mjs']
differential = original[:original.index('export async function blobChecks(consumers) {')]
for old in ["const BlobCtor = Blob;\n", "const BufferCtor = globalThis.Buffer;\n", ",new BlobCtor(['a'])"]:
    assert differential.count(old) == 1
    differential = differential.replace(old, '')
differential = differential.replace('export async function textChecks(consumers) {', 'export async function textChecks(consumers, selected = null) {')
differential = differential.replace('  async function check(name, run) { cases.push({name,result:await run()}); }',
    '  let index=0; async function check(name, run) { const current=index++; if(selected===null||selected===current)cases.push({name,result:await run()}); }')
assert differential == text('differential.mjs')
expected_cases = json.loads(json.dumps(node_report['text']))
invalid = next(r for r in expected_cases if r['name'] == 'invalid byte chunks reject with error type and code')
assert len(invalid['result']) == 6
invalid['result'] = invalid['result'][:5]
node_oracle = load(SOURCE / 'node-oracle.json')
assert len(expected_cases) == 18 and expected_cases == node_oracle['cases']
assert node_oracle['sourceReportSha256'] == digest(family / 'node-results.json')[0]
profiles = (family / 'metadata-v2/component-checks.mjs').read_text()
profiles = profiles.replace("import { createConsumersModule, CONTRACT_VERSION, MAX_BYTE_INPUT, MAX_CHUNKS, MAX_OUTPUT_CODE_UNITS, MAX_STRING_INPUT_CODE_UNITS } from './create-module.mjs';", "import { CONTRACT_VERSION, MAX_BYTE_INPUT, MAX_CHUNKS, MAX_OUTPUT_CODE_UNITS, MAX_STRING_INPUT_CODE_UNITS } from './profile-contract.mjs';")
profiles = profiles.replace('export async function profileChecks(prototype){', 'export async function profileChecks(prototype, selected = null){')
profiles = profiles.replace('  const cases=[];async function group(name,run){cases.push({name,result:await run()});}', '  const cases=[];let index=0;async function group(name,run){const current=index++;if(selected===null||selected===current)cases.push({name,result:await run()});}')
profiles = profiles.replace('    // Bundling can lower the isolated ESM namespace. Record its actual shape;\n    // this is not proof of a future registered native Module Namespace Object.', "    // This fixture imports the actual registered native namespace; no facade is bundled.\n    check(Apply(Tag,prototype,[])==='[object Module]'&&GetProto(prototype)===null&&!Object.isExtensible(prototype),'registered namespace shape');")
at = profiles.index("  await group('factory does not install globals or expose dependencies',()=>{")
end = profiles.index('\n  return cases;', at)
profiles = profiles[:at] + "  await group('registered public record exposes no factory or native dependencies',()=>{\n    equal(OwnKeys(prototype).sort(),['arrayBuffer','blob','buffer','default','json','text'],'finite registered public exports');\n    check(prototype.createConsumersModule===undefined&&prototype.TextDecoder===undefined&&prototype.kernel===undefined,'private factory/dependency absent');\n    return{finiteRegisteredBindings:true,privateFactoryType:'undefined',privateDecoderType:'undefined'};\n  });" + profiles[end:]
assert profiles == text('profiles.mjs')
ancestry = load(SOURCE / 'profile-oracle-ancestry.json')
old_profiles = load(family / 'prototype-node-results.json')
assert ancestry['oldProfiles'] == old_profiles['profiles'] and len(ancestry['oldProfiles']) == 12
assert ancestry['oldNodeOnlyProfileReportSha256'] == digest(family / 'prototype-node-results.json')[0]
extra = load(SOURCE / 'extra-node-oracle.json')
extra_cases = extra.get('cases', extra.get('groups'))
assert isinstance(extra_cases, list) and len(extra_cases) == 8

# The actual pinned diagnostic branches determine the mismatch without executing a bundler.
driver = text('run-validation.mjs')
bundler_name = 'packaging-tools/tests/node-compat/profile-bundler.mjs'
bundler = text(bundler_name)
assert 'CommonJS require is not admitted: ${specifier}' in bundler
assert 'Node builtin is not admitted by this profile: ${source}' in bundler
assert 'assert(failure&&/Node builtin is not admitted by this profile:/.test(failure.message))' in driver
denials = []
for specifier in ['node:stream/consumers', 'stream/consumers']:
    for kind in ['default-esm', 'named-esm', 'namespace-esm', 'literal-cjs']:
        message = ('CommonJS require is not admitted: ' if kind == 'literal-cjs' else 'Node builtin is not admitted by this profile: ') + specifier
        accepted = bool(re.search('Node builtin is not admitted by this profile:', message))
        denials.append({'specifier': specifier, 'kind': kind, 'actualPinnedDiagnosticTemplateResult': message,
                        'oldDriverMatcherAccepts': accepted, 'pureTemplateEvaluationOnly': True})
assert sum(not r['oldDriverMatcherAccepts'] for r in denials) == 2
assert driver.index("assert.equal(typeof raw,'string')") < driver.index('rawFile=await save(')
assert 'selectedManifestsForEngine(' not in driver
assert 'builtinManifests:admission.selectedManifests' in driver
for name in ['component.mjs', 'consumer.cjs', 'differential.mjs', 'profiles.mjs', 'extras.mjs', 'initializers.mjs', 'disabled-fixtures.mjs']:
    assert not re.search(r'Buffer\.from\(\s*\[', text(name)), name
for name in ['activate.py', 'capture-tool-context.py', 'prepare-source.py', 'prepare-tool-capture.py', 'seal-source.py', 'test-closure.py']:
    ast.parse(text(name), filename=name)
authority = load(SOURCE / 'future-authority.json')
assert len(authority['variants']) == 4 and all(v is None for v in authority['variants'].values())
assert not authority['operationalAdmission'] and not authority['sourceActivationExecuted']
assert not (SOURCE.parent / 'component-validation-activated-v1').exists()
owner_evidence = {name: load(SOURCE / ('evidence/' + name + '.json')) for name in ['source-results', 'closure-results', 'syntax-results']}
assert owner_evidence['source-results']['passed'] == 64
assert owner_evidence['closure-results']['passed'] == 13
assert len(owner_evidence['syntax-results']['commands']) == 31
assert all(r['exitCode'] == 0 for r in owner_evidence['syntax-results']['commands'])

citations = {
    'oldDriverDenialMatcher': line('run-validation.mjs', 'assert(failure&&/Node builtin is not admitted by this profile:/.test(failure.message))'),
    'cjsDiagnostic': line(bundler_name, 'CommonJS require is not admitted: ${specifier}'),
    'esmDiagnostic': line(bundler_name, 'Node builtin is not admitted by this profile: ${source}'),
    'literalCjsFixture': line('disabled-fixtures.mjs', "kind:'literal-cjs'"),
    'rawTypeBeforeRetention': line('run-validation.mjs', "assert.equal(typeof raw,'string')"),
    'genuineBootstrap': line('runtime-preflight.template.mjs', 'consumersBootstrapPreflight'),
    'providedManifestBundle': line('run-validation.mjs', 'builtinManifests:admission.selectedManifests'),
    'publicWit': line('run-validation.mjs', 'export run: func(index: u32) -> string'),
}
findings = [
    {'id': 'C355-COMP-M1', 'severity': 'mandatory-fix', 'disposition': 'HOLD_BEFORE_ACTIVATION',
     'title': 'Correct CJS refusals are rejected by the OFF driver diagnostic assertion',
     'detail': 'Both literal-CJS fixtures take the pinned bundler CommonJS refusal branch. The driver accepts only the ESM diagnostic prefix, so a correct CJS refusal fails the source-defined OFF gate before componentization.',
     'evidence': ['oldDriverDenialMatcher', 'cjsDiagnostic', 'esmDiagnostic', 'literalCjsFixture'],
     'fixtureRows': [r for r in denials if not r['oldDriverMatcherAccepts']], 'runtimeReproductionClaim': False},
    {'id': 'C355-COMP-M2', 'severity': 'retention-gap', 'disposition': 'FIX_IN_SUCCESSOR',
     'title': 'Nonstring Jco transport values would fail before raw retention',
     'detail': 'observed() checks typeof raw before saving raw.txt. The declared current exports return strings, so this is a failure-evidence retention gap, not a demonstrated guest ABI or semantic failure. A typed envelope before the type guard must avoid inspecting opaque values.',
     'evidence': ['rawTypeBeforeRetention'], 'runtimeReproductionClaim': False}]
write('diagnostic-template-ledger.json', {'schemaVersion': 1, 'rows': denials, 'bundlerExecuted': False})
write('findings.json', {'schemaVersion': 1, 'disposition': 'HOLD_NO_ACTIVATION', 'findings': findings, 'citations': citations})
write('checked-reference-ledger.json', {'schemaVersion': 1, 'rows': checked, 'uniquePhysicalFiles': len(cache),
    'nestedOriginalPreparationRowsReinterpreted': False, 'directLiveRootFiveRows': direct_five})
results = {'schemaVersion': 1, 'state': 'INDEPENDENT_CONSUMERS355_COMPONENT_VALIDATION_SOURCE_REVIEW_HOLD',
    'reviewedIndexSha256': EXPECTED, 'reviewedFiles': 65, 'originalPreparationReferences': 5151,
    'sourceFilesAndReferencesHashExact': True, 'nativeProducerOriginalAndStagedIndexedFiles': 59,
    'nativeProducerIndexSha256': native_sha, 'sourcePeerIndexedFiles': 8,
    'physicalSnapshot': {'modules': 12, 'localStaticEdges': 13, 'selectedDataAndAdapter': 8,
        'relativeDataUrls': 24, 'explicitInactiveLazyReadsNotCalled': 12, 'packages': 4,
        'resolverEndpointFiles': 5, 'packageProvenanceFiles': 27},
    'toolClosure': {'trees': 2, 'links': 22, 'regularTreeFiles': 4890, 'toolInputsIncludingInvocationBinaries': 4892},
    'corpus': {'nodeGroups': 18, 'boundedProfileGroups': 12, 'additionalPublicNodeGroups': 8,
        'totalCases': 38, 'plannedNormalReturnedRecords': 190, 'initializerControls': 11,
        'combinedOwnerGcReturnedRecords': 4, 'offDenials': 8, 'offSmokeReturnedRecords': 5,
        'differentialAndProfileAfterimagesIndependentlyReconstructed': True,
        'excludedNodeBlobVector': 1, 'old293RuntimeProofTransferred': False},
    'directLiveRootFiveRows': 0, 'liveRootFivePromotionChangesThisFiniteClosure': False,
    'rootFiveScope': 'Only direct consumed source rows and physical snapshot origins inspected; historical descriptor bytes are not followed or relabelled.',
    'futureNativeTuples': authority['variants'], 'futureActivatedOutputAbsentAtReview': True,
    'ownerStoredChecksAuthenticatedNotRerun': {'source': 64, 'physical': 13, 'syntax': 31},
    'mandatoryFindings': ['C355-COMP-M1'], 'retentionFindings': ['C355-COMP-M2'],
    'additionalDemonstratedFunctionalBlockers': [], 'disposition': 'HOLD_NO_ACTIVATION',
    'execution': {'readerOnly': True, 'ownerModulesImported': False, 'ownerActionsOrTestsExecuted': False,
        'bootstrapOrPreflightExecuted': False, 'compilerOrFactoryOrComponentizerExecuted': False,
        'guestOrHostOrTimingExecuted': False},
    'limits': ['No current guest or native correctness claim from synthetic/source checks.',
        'Normal190, GC4 and OFF5 are plans, not observed runtime records.',
        'GC ownership is combined only; no isolated VM rooting or reset claim.',
        'No performance, full Node compatibility, acceptance or operational admission claim.',
        'Pinned-source finite import/data regex closure is not a general JavaScript parser proof.',
        'Resolver endpoint bytes, package JSON, and captured resolution paths were checked without invoking a Node resolver.'],
    'findings': findings, 'citations': citations}
write('results.json', results)
print(json.dumps({'state': results['state'], 'sourceFiles': 65, 'preparationRows': 5151,
    'directLiveRootFiveRows': 0, 'physicalModules': 12, 'treeFiles': tree_file_count,
    'mandatoryFindings': 1, 'retentionFindings': 1, 'ownerActionsExecuted': False}))
