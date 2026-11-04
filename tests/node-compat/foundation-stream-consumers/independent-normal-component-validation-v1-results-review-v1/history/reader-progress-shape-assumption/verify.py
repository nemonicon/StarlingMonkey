"""Read/hash/decode recorded results only. No owner module or tool execution."""
from pathlib import Path
import collections
import hashlib
import json
import os
import re
import shlex
import stat

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
FAMILY = HERE.parent / 'component-validation-activated-v2'
FAMILY_SHA = 'bfb689fe993b9f55abc4848e77930c773597e769a7f08a0f2404914d82227835'
OUTPUT = Path('/tmp/starling-node-compat/consumers355-v2-normal-component-validation-v1')
ROOT_LOGS = Path('/tmp/starling-node-compat/consumers355-v2-normal-validation-v1-root')
ROOT_RECEIPT = HERE.parent / 'normal-component-validation-v1-root-results.json'
ROOT_SHA = 'ed70ae175f9652c403ce6f3772f80c4645f308194cb37d6c76750c58e5e2eae1'
ENGINE_SHA = '661ef79418ab139c9a7bcebb57eb36c17c3c398f67c80bbcd680cb95839f0c79'
COMPONENT_SHA = '77e6563604089a4a39f27443885e33015af16ea1d9c933f6431890c41b330b27'
NODE_SHA = 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
WT_SHA = 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c'
verified, cache, checks, observations = {}, {}, [], []

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def equal(actual, expected, label):
    def same(a, b):
        if type(a) is not type(b):
            return False
        if isinstance(a, dict):
            return set(a) == set(b) and all(same(a[k], b[k]) for k in a)
        if isinstance(a, list):
            return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
        return a == b
    if not same(actual, expected):
        with (HERE / 'counterexample.json').open('x') as stream:
            json.dump({'label': label, 'actual': actual, 'expected': expected}, stream, ensure_ascii=True)
            stream.write('\n')
        raise AssertionError('Full recorded value mismatch; see counterexample.json: ' + label)

def identity(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns

def pinned(path, expected=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    key = (str(path.resolve()), identity(before))
    if key not in cache:
        h = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(block)
        assert identity(path.lstat()) == identity(before), str(path)
        cache[key] = h.hexdigest()
    digest = cache[key]
    if expected is not None:
        assert digest == expected, (str(path), digest, expected)
    if size is not None:
        assert before.st_size == size, str(path)
    row = {'path': str(path), 'sha256': digest, 'bytes': before.st_size}
    if str(path) in verified:
        assert verified[str(path)] == row
    verified[str(path)] = row
    return row

def data(path, digest=None, size=None):
    row = pinned(path, digest, size)
    value = Path(path).read_bytes()
    assert sha(value) == row['sha256'] and len(value) == row['bytes']
    return value

def document(path, digest=None, size=None):
    return json.loads(data(path, digest, size))

def descriptor(row):
    return pinned(row['path'], row['sha256'], row['bytes'])

def check(name, condition=True):
    assert condition, name
    checks.append(name)

def indexed(root, digest, count=None):
    value = document(root / 'index.json', digest)
    if count is not None:
        assert len(value['files']) == count
    assert len({r['path'] for r in value['files']}) == len(value['files'])
    for row in value['files']:
        assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
        pinned(root / row['path'], row['sha256'], row['bytes'])
    return value

def inventory(root):
    entries = []
    for current, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(current) / name
            mode = path.lstat().st_mode
            kind = 'symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file' if stat.S_ISREG(mode) else None
            assert kind, str(path)
            entries.append({'path': str(path.relative_to(root)), 'kind': kind})
    return sorted(entries, key=lambda row: row['path'])

def uleb(raw, at):
    value = 0
    for shift in range(0, 35, 7):
        assert at < len(raw)
        byte = raw[at]
        at += 1
        value |= (byte & 127) << shift
        if not byte & 128:
            return value, at
    raise AssertionError('Invalid bounded ULEB')

def sections(raw, version):
    assert raw[:8] == b'\0asm' + version
    at, result = 8, []
    while at < len(raw):
        tag = raw[at]
        size, start = uleb(raw, at + 1)
        end = start + size
        assert end <= len(raw)
        result.append((tag, raw[start:end]))
        at = end
    assert at == len(raw)
    return result

def command_source(command):
    words = shlex.split(command)
    assert words.count('-c') == 1
    return words[words.index('-c') + 1]

root = document(ROOT_RECEIPT, ROOT_SHA, 3307)
assert root['state'] == 'ROOT_CONSUMERS355_NORMAL_COMPONENT_VALIDATION_RAW_PASS_V1'
assert root['rawExitCode'] == 0 and root['engineSha256'] == ENGINE_SHA
for key in ['authority', 'sourceFamilyIndex', 'terminal', 'stdout', 'stderr', 'report', 'completion', 'outputClosure', 'component']:
    descriptor(root[key])
authority = document(root['authority']['path'], root['authority']['sha256'])
assert authority['state'] == 'ROOT_CONSUMERS355_NORMAL_COMPONENT_VALIDATION_AUTHORITY_V1'
assert authority['variant'] == 'normal-off' and authority['normalEngineSha256'] == ENGINE_SHA
assert authority['operationalAdmission'] is False and authority['gcExecutionAllowedByThisReceipt'] is False
for key in ['sourceFamilyIndex', 'independentFamilyReview', 'actualPreflight', 'nativePins']:
    descriptor(authority[key])
indexed(FAMILY, FAMILY_SHA, 47)
indexed(Path(authority['independentFamilyReview']['path']).parent, authority['independentFamilyReview']['sha256'])
indexed(HERE.parent / 'independent-component-validation-v2-source-review-v1',
        '13bc711de7653539bff7b81d9dcb6caebcdfa6dc484d8747e8169c257130655a', 9)
preflight = document(authority['actualPreflight']['path'], authority['actualPreflight']['sha256'])
assert preflight['rawExitCode'] == 0 and len(preflight['variants']) == 3
for key in ['terminal', 'stdout', 'stderr', 'previousFailureRetained', 'rootAuthority']:
    descriptor(preflight[key])
check('Rootnormalauthority/rawterminal0 and source/family/source-peer/preflight identities')

config = document(FAMILY / 'activation.json')
seal = document(FAMILY / 'input-freeze.json', 'f6bcb9e6703cc03a36b7d4949d3fcb2100caee830c04f6bc6983a625b78edd29')
assert len(seal['inputs']) == 7268 and len({r['path'] for r in seal['inputs']}) == 7268
for row in seal['inputs']:
    pinned(FAMILY / row['path'], row['sha256'], row['bytes'])
for tree in seal['toolTrees']:
    assert str(Path(tree['path']).resolve()) == tree['realPath']
    equal(inventory(Path(tree['path'])), tree['entries'], 'tool-tree membership')
for link in seal['toolLinks']:
    path = Path(link['path'])
    assert path.is_symlink() and os.readlink(path) == link['linkText'] and str(path.resolve()) == link['resolvedTarget']
    if link['targetKind'] == 'file':
        pinned(path.resolve(), link['targetSha256'], link['targetBytes'])
    else:
        assert link['targetKind'] == 'directory' and path.resolve().is_dir()
assert len(seal['toolTrees']) == 2 and len(seal['toolLinks']) == 22
for row in [config['liveAdapter']] + config['liveWit']:
    descriptor(row)
assert len(config['liveWit']) == 7 and config['liveAdapter']['bytes'] == 53512
assert config['nativeConfiguredSourceRoot'] == '/private/tmp/starling-node-compat/consumers-source-v2'
assert config['componentToolRoot'] == str(FAMILY / 'packaging-tools')
assert config['componentToolRoot'] != config['nativeConfiguredSourceRoot'] and config['operationalAdmission'] is False
check('full7268consumedsource/two tooltrees22links/LIVE8 and distinct native/tool contexts')

pins = document(FAMILY / 'reviewed-pins.json', config['pinsSha256'])
review = document(FAMILY / 'root-review.json', config['rootReviewSha256'])
assert pins['state'] == 'ROOT_REVIEWED_STREAM_CONSUMERS355_VALIDATION_BOOTSTRAP_V1'
assert review['reviewedPinsSha256'] == config['pinsSha256'] and review['sourceFiles'] == 355
assert review['operationalAdmission'] is False and pins['runtimeAcceptanceClaim'] is False
pin = pins['variants']['normal-off']
for key in ['engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256']:
    assert pin[key] == config['actual']['normal-off'][key]
assert pin['engineSha256'] == ENGINE_SHA and pin['reviewRequired'] is False
for row in pin['frozenFiles']:
    descriptor(row)
freeze = document(pin['freezeReceiptPath'], pin['freezeReceiptSha256'])
metadata = document(pin['enginePath'] + '.build.json', pin['receiptSha256'])
assert len(freeze['copies']) == len(pin['frozenFiles']) == 1164
for row in freeze['copies']:
    descriptor(row)
assert len(metadata['sourceManifest']) == freeze['nativeInputsVerified'] == 355
assert len(metadata['componentizeSourceManifest']) == freeze['externalEmbeddingInputsVerified'] == 3
for row in metadata['sourceManifest']:
    pinned(Path(freeze['sourceRoot']) / row['path'], row['sha256'])
for row in metadata['componentizeSourceManifest']:
    pinned(Path(freeze['componentizeSourceRoot']) / row['path'], row['sha256'])
assert len(freeze['toolDependencyClosure']) == 767
assert metadata['gcStress'] is False and metadata['oomTesting'] is False
assert metadata['streamConsumersEnabled'] is True and metadata['zlibEnabled'] is True
assert metadata['entropyPolicy'] == 'off'
options = metadata['observedCMakeOptions']
for key, value in {'CMAKE_BUILD_TYPE': 'Release', 'ENABLE_BUILTIN_WEB_TEXT_CODEC': 'ON', 'NODE_COMPAT_STREAM_CONSUMERS': 'ON', 'NODE_COMPAT_ZLIB': 'ON', 'NODE_COMPAT_GC_STRESS': 'OFF', 'NODE_COMPAT_OOM_TESTING': 'OFF', 'NODE_COMPAT_ENTROPY_MODE': 'OFF'}.items():
    assert options[key] == value
database = document(pin['commandsPath'], pin['compileCommandsSha256'])
commands = [row['command'] for row in database]
layout = metadata['internalTickPolicy']['actualLayoutCompileCommands']
strict = metadata['strictEventExceptionPolicy']['actualNativeCompileCommands']
private = metadata['streamConsumersPolicy']['actualPrivateTargetCompileCommands']
embedding = metadata['actualEmbeddingCompileCommands']
assert [len(layout), len(strict), len(private), len(embedding)] == [62, 4, 6, 1]
assert all(command in commands for command in layout + strict + private)
expected_private = {str(Path(config['nativeConfiguredSourceRoot']) / 'builtins/node-compat' / name) for name in ['buffer.cpp', 'register.cpp', 'entropy-policy.cpp', 'entropy-bridge.cpp', 'stream-web-kernel.cpp', 'zlib/kernel.cpp']}
actual_private = set()
for command in commands + embedding:
    words = shlex.split(command)
    assert words.count('-O3') == 1 and '-O0' not in words and '-DNDEBUG' in words
    assert not any(w.startswith(('-DNODE_COMPAT_OOM_TESTING', '-UNODE_COMPAT_OOM_TESTING', '-DNODE_COMPAT_GC_STRESS')) for w in words)
    macros = [w for w in words if w.startswith(('-DNODE_COMPAT_STREAM_CONSUMERS', '-UNODE_COMPAT_STREAM_CONSUMERS'))]
    if macros:
        assert macros == ['-DNODE_COMPAT_STREAM_CONSUMERS=1']
        actual_private.add(str(Path(command_source(command)).resolve()))
assert actual_private == expected_private
installation = metadata['streamConsumersPolicy']['installationOrder']
frozen_install = next(r for r in pin['frozenFiles'] if r['sha256'] == installation['sha256'])
installed = data(frozen_install['path'], installation['sha256']).decode()
assert installed.index('NS_DEF(builtins::web::text_codec)') < installed.index('NS_DEF(builtins::node_compat)')
assert installation['decoderBeforeNode'] is True
assert metadata['zlibPolicy']['runtimeBackendProof'] == {'verified': False, 'version': None, 'vernum': None}
check('genuine355/frozen1164/native355+external3/native62/strict4/private6/embed1/noGC/noOOM/installorder')

report = document(OUTPUT / 'results.json', root['report']['sha256'], root['report']['bytes'])
complete = document(OUTPUT / 'completion.json', '7eb8baad78bc0d4c9f1cebc8ec7a18e08e8281c7b6ef0d7f39ecb07722b42022')
assert report['state'] == 'CONSUMERS355_REGISTERED_TEXT_JSON_COMPONENT_VALIDATION_PASSED'
assert report['variant'] == 'normal-off' and report['sourceFamilyIndexSha256'] == FAMILY_SHA
assert report['nativeSourceFiles'] == 355 and report['engineSha256'] == ENGINE_SHA and report['namespacePassed'] is True
assert len(report['records']) == 190 and len(report['initializerRecords']) == 11 and report['componentizeCalls'] == 12
assert report['denials'] == [] and report['requiresIndependentTerminalExitZero'] is True
assert complete['state'] == 'CONSUMERS355_VALIDATION_OUTPUT_COMPLETE' and complete['requiresIndependentExitZero'] is True
assert complete['reportSha256'] == root['report']['sha256']
artifact_paths = set()
for row in complete['artifacts']:
    assert row['path'] not in artifact_paths and Path(row['path']).is_relative_to(OUTPUT)
    artifact_paths.add(row['path'])
    descriptor(row)
assert len(artifact_paths) == 1317
actual_inventory = inventory(OUTPUT)
regular = {str(OUTPUT / r['path']) for r in actual_inventory if r['kind'] == 'file'}
links = [str(OUTPUT / r['path']) for r in actual_inventory if r['kind'] == 'symlink']
assert regular == artifact_paths | {str(OUTPUT / 'completion.json')} and len(regular) == 1318
assert links == [str(OUTPUT / 'node_modules')]
equal(complete['outputLinks'], root['outputLinks'], 'Root/completion output link')
for row in complete['outputLinks']:
    assert os.readlink(row['path']) == row['linkText'] and str(Path(row['path']).resolve()) == row['resolvedTarget']
output_controls = document(OUTPUT / 'output-controls.json')
equal(output_controls['nodeModulesLink'], complete['outputLinks'][0], 'output-controls link')
closure = document(root['outputClosure']['path'], root['outputClosure']['sha256'])
check('exact1317completionartifacts pluscompletion and one preserved outputlink')

terminal = document(root['terminal']['path'], root['terminal']['sha256'])
equal(terminal['argv'], authority['argv'], 'actualRootcommand')
equal(terminal['selectedEnvironment'], authority['selectedEnvironment'], 'actualRootenvironment')
assert terminal['rawExitCode'] == 0 and terminal['observedByRoot'] is True
pinned(terminal['argv'][0], NODE_SHA)
external_stdout = data(root['stdout']['path'], root['stdout']['sha256']).decode()
assert data(root['stderr']['path'], root['stderr']['sha256']) == b''
stdout_rows = [json.loads(line) for line in external_stdout.splitlines()]
assert stdout_rows[-1]['state'] == report['state'] and stdout_rows[-1]['output'] == str(OUTPUT)
progress = sorted((OUTPUT / 'progress').glob('*.json'))
assert len(progress) == 432
progress_rows = [document(path) for path in progress]
assert [r['sequence'] for r in progress_rows] == list(range(1, 433))
equal(stdout_rows[:432], progress_rows, 'external stdout/durable progress')
assert len(stdout_rows) == 433
check('actualpinnedNode22 command/raw0 and all432progressrecords matchdurableexternalstdout')

component = data(root['component']['path'], COMPONENT_SHA, 13117207)
component_sections = sections(component, b'\x0d\x00\x01\x00')
imports = sum(uleb(raw, 0)[0] for tag, raw in component_sections if tag == 10)
exports = sum(uleb(raw, 0)[0] for tag, raw in component_sections if tag == 11)
assert imports == 0 and exports == 3
wit = data(OUTPUT / 'consumer_validation.emitted.wit').decode()
assert wit == report['fixture']['emittedWit'] and not re.search(r'\bimport\b', wit)
public_exports = ['run: func(index: u32) -> string', 'module-contract: func() -> string', 'ordinary-gc: func() -> string']
equal(re.findall(r'export\s+([^;]+);', wit), public_exports, 'threepublicWITexports')
core = data(OUTPUT / 'consumer_validation.core.wasm')
sections(core, b'\x01\x00\x00\x00')
assert core in component and b'consumer_validation.core.wasm' in data(OUTPUT / 'consumer_validation.js')
assert data(OUTPUT / 'consumer_validation.d.ts').decode() == '// world root:component/root\nexport function run(index: number): string;\nexport function moduleContract(): string;\nexport function ordinaryGc(): string;\n'
assert report['fixture']['componentSha256'] == COMPONENT_SHA and report['fixture']['componentBytes'] == len(component)
assert report['interfaceAudit']['emittedImports'] == [] and report['interfaceAudit']['componentSha256'] == COMPONENT_SHA
assert report['interfaceAudit'] == report['fixture']['interfaceAudit']
equal(report['bundle']['imports'], ['node:buffer', 'node:stream', 'node:stream/consumers', 'node:stream/web'], 'actualbundlefourNativeImports')
assert report['bundle']['code'].encode() == data(OUTPUT / 'guest.bundle.mjs')
assert sha(report['bundle']['code'].encode()) == report['bundle']['sha256']
assert all('/node_modules/' not in path and '/builtins/node-compat/' not in path for path in report['bundle']['moduleIds'])
assert not re.search(r'node_modules/(?:unenv|@bytecodealliance/jco-std)|function\s+createConsumersModule\b|function\s+createClassicCore\b', report['bundle']['code'])
check('actualcomponentouterimports0/public3/coreembedded/glue/dts/nativefourimportbundle')

node = document(FAMILY / 'node-oracle.json')
profiles = document(FAMILY / 'profile-oracle-ancestry.json')
extra = document(FAMILY / 'extra-node-oracle.json')
assert node['node'] == extra['node'] == 'v22.14.0'
assert len(node['cases']) == 18 and len(profiles['oldProfiles']) == 12 and len(extra['cases']) == 8
assert extra['nodeExecutableSha256'] == NODE_SHA

def snapshot(value, count):
    equal(value, {'text': 'ABC!', 'json': {'snapshot': True}, 'flush': '\ufffd', 'bufferByte': 17 + count,
                  'bufferBrand': True, 'viewOffset': 2, 'backingBytes': 7}, 'snapshot/counter')

def refusals(value):
    equal([(r['name'], r['mode']) for r in value], [(name, mode) for name in ['arrayBuffer', 'blob', 'buffer'] for mode in ['call', 'new']], 'sixrefusalordering')
    for row in value:
        expected = {'code': 'ERR_SM_NODE_UNSUPPORTED', 'module': 'node:stream/consumers', 'operation': row['name'], 'profile': 'sm-node-22.14.0-m0.14'}
        equal(row['error'], {'name': 'Error', 'fields': {k: {'own': True, 'type': 'string', 'value': v} for k, v in expected.items()}}, 'fulltypedownrefusalfields')

def module(value, count):
    assert type(value['calls']) is int and value['calls'] == count and value['gcCalls'] == 0
    names = ['arrayBuffer', 'blob', 'buffer', 'default', 'json', 'text']
    equal(value['names'], names, 'namespaceexports')
    equal(value['aliasNames'], names, 'aliasnamespaceexports')
    for key in ['canonicalCached', 'aliasCached', 'canonicalStatic', 'aliasValues', 'defaultNamed', 'defaultMutable', 'cjsDefault', 'safeAwaitNamespace', 'safeAwaitAlias', 'safeAwaitDefault', 'globalBuffer', 'namespacePrototypeNull']:
        assert value[key] is True, key
    assert value['namespaceExtensible'] is False and value['namespaceTag'] == '[object Module]'
    equal(value['defaultKeys'], ['arrayBuffer', 'blob', 'buffer', 'text', 'json'], 'defaultkeys')
    for key in ['thenType', 'aliasThenType', 'defaultThenType', 'privateFactoryType', 'privateDecoderType']:
        assert value[key] == 'undefined'
    equal(value['selectedWeb'], {'constructor': 'function', 'asyncIterator': 'function'}, 'selectedweb')
    assert value['rawGlobalReadableObservation']['passedToConsumer'] is False
    snapshot(value['snapshot'], count)
    refusals(value['initializationRefusals'])

def run(value, index, count):
    assert type(value['calls']) is int and value['calls'] == count
    assert type(value['index']) is int and value['index'] == index and value['gcCalls'] == 0
    assert value['nativeBlobInvoked'] is False
    assert set(value) == {'calls', 'gcCalls', 'index', 'kind', 'name', 'result', 'snapshot', 'refusals', 'nativeBlobInvoked'}
    snapshot(value['snapshot'], count)
    refusals(value['refusals'])
    if index < 18:
        expected, kind = node['cases'][index], 'node-differential'
    elif index < 30:
        p = index - 18
        expected = json.loads(json.dumps(profiles['oldProfiles'][p]))
        if p == 2:
            expected['result']['ownKeys'] = {'text': ['length', 'name'], 'json': ['length', 'name']}
        if p == 11:
            expected = {'name': 'registered public record exposes no factory or native dependencies', 'result': {'finiteRegisteredBindings': True, 'privateFactoryType': 'undefined', 'privateDecoderType': 'undefined'}}
        kind = 'profile'
    else:
        expected, kind = extra['cases'][index - 30], 'public-stream-and-boundary'
    assert value['kind'] == kind and value['name'] == expected['name']
    equal(value['result'], expected['result'], 'fullcase-' + str(index))
    return {'index': index, 'kind': kind, 'name': expected['name'], 'fullValueEqual': True,
            'nodeValueCompared': index < 18 or index >= 30, 'profilePolicyCompared': 18 <= index < 30}

raw_paths = sorted((OUTPUT / 'calls').glob('*.raw.txt'))
assert len(raw_paths) == 196
expected_labels, namespace_counts = [], {}
expected_labels.append(('module-before', None, 0))
for round_number in range(3):
    expected_labels.extend((f'retained-{round_number}-{i}', i, round_number * 38 + i + 1) for i in range(38))
    expected_labels.append((f'module-retained-{round_number}', None, (round_number + 1) * 38))
expected_labels.append(('fresh-module', None, 0))
expected_labels.extend((f'fresh-Jco-{i}', i, i + 1) for i in range(38))
expected_labels.append(('fresh-module-after', None, 38))
expected_labels.extend((f'fresh-Wasmtime-{i}', i, 1) for i in range(38))
assert len(expected_labels) == 196
run_index = 0
for sequence, (label, index, count) in enumerate(expected_labels, 1):
    stem = f'{sequence:04d}-{label}'
    raw_path = OUTPUT / 'calls' / (stem + '.raw.txt')
    raw = data(raw_path).decode()
    value = json.loads(raw)
    observed = document(OUTPUT / 'calls' / (stem + '.observed.json'))
    equal(observed, value, 'wholeobserved/rawequality-' + stem)
    envelope = document(OUTPUT / 'calls' / (stem + '.transport.json'))
    equal(envelope, {'type': 'string', 'codeUnits': len(raw.encode('utf-16-le', errors='surrogatepass')) // 2, 'valueStoredSeparatelyAsRawString': True}, 'typedtransport-' + stem)
    if index is None:
        module(value, count)
        namespace_counts[label] = count
    else:
        semantic = run(value, index, count)
        semantic.update({'expectedCalls': count, 'fullOutputChecked': True})
        report_row = report['records'][run_index]
        assert report_row['index'] == index and report_row['expectedCalls'] == count
        assert report_row['name'] == semantic['name'] and report_row['kind'] == semantic['kind']
        assert report_row['nodeValueCompared'] == semantic['nodeValueCompared'] and report_row['profilePolicyCompared'] == semantic['profilePolicyCompared']
        assert report_row['fullOutputChecked'] is True
        equal(report_row['rawFile'], verified[str(raw_path)], 'report/rawdescriptor')
        if label.startswith('retained-'):
            stored = document(OUTPUT / 'calls' / (stem + '.validated.json'))
            equal(stored, {k: v for k, v in semantic.items() if k != 'fullValueEqual'}, 'retainedvalidationrecord')
        run_index += 1
    observations.append({'sequence': sequence, 'label': label, 'index': index, 'expectedCalls': count,
                         'raw': verified[str(raw_path)], 'completeValueChecked': True,
                         'rawTransportType': 'string', 'namespaceObservation': index is None})
assert run_index == 190 and len(namespace_counts) == 6
check('all196fulltypedraw/observedreturns match130Nodevalue+60profilecases and6namespaceobservations')
check('allfivefull1MiBstrings/caps/iteratorcleanup/selectedWeb/classic/U8ABwindows/snapshot/refusals')

for index in range(38):
    terminal = document(OUTPUT / 'processes' / f'wasmtime-{index}.terminal.json')
    launch = document(OUTPUT / 'processes' / f'wasmtime-{index}.launch.json')
    assert terminal['args'] == ['run', '--invoke', f'run({index})', str(OUTPUT / 'consumer_validation.component.wasm')]
    assert terminal['executable'] == launch['executable'] and terminal['args'] == launch['args']
    pinned(terminal['executable'], WT_SHA)
    assert terminal['status'] == 0 and terminal['signal'] is None and terminal['spawnError'] is None
    assert terminal['timedOut'] is False and terminal['outputLimitExceeded'] is False
    assert terminal['closed'] is True and terminal['ownedGroupGone'] is True and terminal['terminalExitZeroObserved'] is True
    assert terminal['timeoutMs'] == launch['timeoutMs'] == 600000 and terminal['maxOutputBytes'] == 16777216
    inner = json.loads(data(terminal['stdout']['path'], terminal['stdout']['sha256'], terminal['stdout']['bytes']))
    assert isinstance(inner, str)
    match = next(row for row in observations if row['label'] == f'fresh-Wasmtime-{index}')
    assert inner == data(match['raw']['path']).decode()
    assert data(terminal['stderr']['path'], terminal['stderr']['sha256'], terminal['stderr']['bytes']) == b''
check('all38freshWTterminal0/ownedgroup/deadline and fullnestedstringreturns independentlydecoded')

initial_names = [f'deferred-{name}-{mode}' for name in ['arrayBuffer', 'blob', 'buffer'] for mode in ['call', 'new']] + ['awaited-text-invalid', 'unawaited-text-invalid', 'microtask-text-invalid', 'awaited-json-invalid', 'awaited-input-cap']
equal([row['name'] for row in report['initializerRecords']], initial_names, 'initializernames')
statements = [f'{name}([]);' if mode == 'call' else f'new {name}([]);' for name in ['arrayBuffer', 'blob', 'buffer'] for mode in ['call', 'new']] + ['await text([{}]);', 'text([{}]);', 'Promise.resolve().then(()=>text([{}]));', "await json(['{']);", 'await text([new Uint8Array(1048577)]);']
for name, statement, record in zip(initial_names, statements, report['initializerRecords']):
    source = "import {arrayBuffer,blob,buffer,text,json} from 'node:stream/consumers';\n" + statement + "\nexport function run(){return '';}\n"
    assert data(OUTPUT / 'initializers' / (name + '.mjs')).decode() == source
    equal(document(OUTPUT / 'initializers' / (name + '.result.json')), record, 'initializerrecord')
    assert record['rejected'] is True and record['error']['name'] == 'Error' and isinstance(record['error']['message'], str)
    assert re.fullmatch('[a-f0-9]{64}', record['sourceSha256'])
    assert record['uncaughtFieldsAcrossAbiObserved'] is False and record['causeIdentityClaim'] is False
    assert record['pairedCaughtInitializationRefusals'] == 6 and record['instanceReusedAfterFailure'] is False
check('all11freshinitializerfailurecontrols/sourcefiles/fullerrormessages retained withoutuniqueABIcauseclaim')

for key in ['vmTemporaryRootsIsolated', 'rawGlobalWebPassedToConsumer', 'nativeBlobInvoked', 'HTTPBodyCancellationOrReuseInferred', 'old293Or350RuntimeTransferred', 'operationalAdmission']:
    assert report['scope'][key] is False
assert report['scope']['noTiming'] is True and root['operationalAdmission'] is False
# Recheck every path after full source/data comparison, with no digest cache.
for row in verified.values():
    h = hashlib.sha256()
    with Path(row['path']).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    assert h.hexdigest() == row['sha256'] and Path(row['path']).stat().st_size == row['bytes'], row['path']
check('fullcapturedsource/native/tool/raw/outputpathclosure unchanged after independentreview')

result = {
    'schemaVersion': 1, 'state': 'INDEPENDENT_CONSUMERS355_NORMAL_COMPONENT_VALIDATION_ACTUAL_RESULTS_PASSED',
    'rootReceiptSha256': ROOT_SHA, 'sourceFamilyIndexSha256': FAMILY_SHA,
    'sourceCandidateIndexSha256': 'a75ee76c1291988cec55252f8ab54e451f31b1593f22119759bada058860002b',
    'rawOuterExitCode': 0, 'engineSha256': ENGINE_SHA, 'componentSha256': COMPONENT_SHA, 'componentBytes': 13117207,
    'reportSha256': root['report']['sha256'], 'completionSha256': root['completion']['sha256'],
    'publicWitExports': public_exports, 'outerHostImports': [], 'publicRunParameter': 'u32',
    'rawCallsDecoded': 196, 'typedRawEnvelopesChecked': 196, 'runRecords': 190,
    'retainedRounds': 3, 'casesPerRound': 38, 'freshJcoCases': 38, 'freshWasmtimeCases': 38,
    'nodeValueCaseGroups': 26, 'nodeValueObservations': 130, 'profilePolicyGroups': 12, 'profilePolicyObservations': 60,
    'namespaceObservations': namespace_counts, 'sixOwnFieldRefusalsPerObservation': True,
    'refusalRecordsFullyChecked': 1176, 'fullOneMiBStringsCompared': 5,
    'initializerFailures': 11, 'componentizerCalls': 12,
    'completionArtifacts': 1317, 'regularOutputFilesIncludingCompletion': 1318, 'outputLinks': 1,
    'sourceConsumedRows': 7268, 'sourceFamilyFiles': 47, 'toolTrees': 2, 'toolLinks': 22,
    'frozenCopies': 1164, 'nativeSources': 355, 'externalEmbeddingSources': 3,
    'nativeCommands': 62, 'strictCommands': 4, 'privateConsumerMacroCommands': 6, 'embeddingCommands': 1,
    'verifiedLexicalPaths': len(verified), 'uniquePhysicalVersionsHashed': len(cache),
    'checks': checks, 'passed': len(checks), 'concreteResultBlockers': [],
    'reviewerActions': 'Only Python stdlib read/streaming hashes/exact recorded JSON and bounded public Wasm decoding.',
    'ownerPreflightBootstrapVerifierFactoryBundlerComponentizerNodeCompilerGuestTargetHostOrTimingExecutedByReviewer': False,
    'gcGateProven': False, 'disabledGateProven': False, 'vmTemporaryRootsIsolated': False,
    'operationalAdmission': False, 'runtimeBackendProofTransferred': False,
    'fullNodeCompatibilityClaim': False, 'HTTPBodyCancellationReuseResetOrPerformanceClaim': False,
    'limitations': ['Twelve profile groups use the declared bounded profile policy, not full Node parity.',
                   'One Blob-specific invalid vector remains explicitly excluded; arrayBuffer/blob/buffer retain call/new refusals.',
                   'Initializer errors are generic ABI failures paired with caught controls; no unique source cause identity is inferred.',
                   'Lowered initializer bundle hashes are recorded, while the exact lowered initializer bundle bytes were not separately retained.',
                   'In-process Jco calls do not have an independent deadline/cancellation guarantee.',
                   'SelectedWeb iterable input is proved; observed raw global Web prototype is not passed to a consumer.',
                   'Retained counters are observed calls, not reset/reuse, request isolation or ownership-isolation proof.',
                   'No GC, consumer-OFF, HTTP, performance, zlib backend or operational-admission gate is transferred into this normal gate.']
}
for name, value in [('results.json', result), ('observations.json', observations), ('verified-paths.json', list(verified.values()))]:
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True)
        stream.write('\n')
print(json.dumps({'state': result['state'], 'passed': len(checks), 'rawCalls': 196, 'runs': 190,
                  'namespace': 6, 'freshWasmtime': 38, 'initializerFailures': 11,
                  'verifiedLexicalPaths': len(verified), 'reviewerGuestOrOwnerActions': False}))
