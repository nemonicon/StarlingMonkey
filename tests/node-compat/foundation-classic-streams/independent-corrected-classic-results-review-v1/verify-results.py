#!/usr/bin/env python3
"""Independent completed-evidence reader; only Python reads and static wasm-tools.

The vector/byte-reader mechanics derive from the earlier normal-OFF reviewer,
with explicit support for RuntimeOnly's embedded adapters. No reviewed project
helper is imported or executed. Binary artifacts remain external references.
"""
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
RUNTIME = BASE / 'production-trace-runtime-activated-v1'
OUTPUT = Path('/tmp/starling-node-compat/production-classic-corrected-runtime-v1')
TOOL = Path('/tmp/starling-node-compat/improved-build/cache/wasm-tools/1448/wasm-tools')
INDEX_SHA = 'e1f87cd6a2fd09ff34055187bfb938c2b094c3fd333ef9f57b6a1eea4c175b78'
PINS_SHA = '182e8b724d94ebf73450c0ffcea81fb19b902028e2839bd2a9d1452ab7fab5eb'
AUTHORITY_SHA = 'ce88ac3495afdf97718a34f7bf2c2360613f95a91f5c193e556c87269b4a8be0'
TOOL_SHA = 'b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d'
REVIEW_SHA = 'd2ef84a640fb73dd343bbee3d0f44ca0e62b71005a06693faf74c88b79a139d1'
MODES = {'normal-off': {'engine': 'd54446dcd4071fe2c2b1db4984ead78d2fe61ceb0a0396822df8416a26921a92', 'engineBytes': 9973355, 'result': '693d202a13f4c36681f79b49c3313104b61a8dc0ba6d5da920e61dd1b3113ed3', 'resultBytes': 615515, 'completion': 'fad6dea2c0edc1939665b33c9cdbc8e0fc37627e881f8bbf2ba05d4f0c7696a4', 'published': 90, 'session': 9469, 'imports': [], 'entropy': 'off', 'gc': False}, 'normal-runtime': {'engine': 'a2fbdfcd9ec928cdec9d35e548b90ca2617ff52ae819c68bd08ad0a8c3ceffa7', 'engineBytes': 9980449, 'result': '5ee52ac76faf605ec97fc5d9070a7204b3a0147786a6fa4198f599409fa98996', 'resultBytes': 621639, 'completion': 'd0a3aa25a7f986f689c8fd71454c1e716fb7e4275b4ac92e9330e3ed6f8c23d5', 'published': 91, 'session': 38075, 'imports': ['wasi:random/random@0.2.10'], 'entropy': 'runtime-only', 'gc': False}, 'gc-off': {'engine': 'd8f2f84496854a8732648eb8a2527145b92469c13fce2bb37200468f8c23af79', 'engineBytes': 9974904, 'result': 'ead819be31fc72498737690b2c05873a67398f1a3efd02cb285c43d43cb1f30a', 'resultBytes': 615866, 'completion': '03c17798761202d381a8535e2251266b903948d80eb44215d677b86f57fa506e', 'published': 90, 'session': 47235, 'imports': [], 'entropy': 'off', 'gc': True}}

checked = {}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file(path, expected=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode), str(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), str(path)
    row = {'path': str(path), 'sha256': h.hexdigest(), 'bytes': before.st_size}
    assert expected is None or row['sha256'] == expected, str(path)
    assert size is None or row['bytes'] == size, str(path)
    if str(path) in checked:
        assert checked[str(path)] == row
    checked[str(path)] = row
    return row


def load(path, expected=None):
    row = file(path, expected)
    data = Path(path).read_bytes()
    assert digest(data) == row['sha256']
    return json.loads(data)


def local(root, name):
    relative = Path(name)
    assert not relative.is_absolute() and '..' not in relative.parts
    path = root / relative
    parent = path.parent
    while parent != root:
        assert parent != parent.parent and not parent.is_symlink()
        parent = parent.parent
    assert not root.is_symlink()
    return path


def initializer_vectors():
    prefix = "import * as stream from 'node:stream';\nimport * as promises from 'node:stream/promises';\n"
    expressions = [('compose', 'stream.compose'), ('duplexPair', 'stream.duplexPair')]
    expressions += [(name+'.'+method, 'stream.'+name+'.'+method) for name in ['Readable', 'Writable', 'Duplex'] for method in ['fromWeb', 'toWeb']]
    expressions += [('Duplex.from', 'stream.Duplex.from')]
    expressions += [('Readable.prototype.'+name, 'stream.Readable.prototype.'+name) for name in ['compose', 'map', 'filter', 'forEach', 'toArray', 'some', 'find', 'every', 'flatMap', 'drop', 'take', 'reduce', 'iterator']]
    expressions += [(name+'.prototype[Symbol.asyncDispose]', 'stream.'+name+'.prototype[Symbol.asyncDispose]') for name in ['Readable', 'Writable']]
    rows = []
    for operation, expression in expressions:
        for construct in [False, True]:
            name = re.sub('[^a-zA-Z0-9]+', '-', operation) + ('-new' if construct else '-call')
            source = prefix+'const unavailable='+expression+';\n'+('new unavailable();' if construct else 'unavailable();')+'\nexport function run(){return "unreachable";}\n'
            rows.append((name, operation, construct, operation, source))
    sink = 'new stream.Writable({write(value,encoding,callback){callback();}})'
    overloads = []
    for shape, value in [('readable', '{getReader(){}}'), ('writable', '{getWriter(){}}'), ('transform-pair', '{readable:{},writable:{}}')]:
        invocations = [
            ('callback-pipeline', 'stream.pipeline(value,'+sink+',()=>{})', 'pipeline(Web stream)'),
            ('promise-pipeline', 'promises.pipeline(value,'+sink+')', 'pipeline(Web stream)'),
            ('callback-finished', 'stream.finished(value,()=>{})', 'finished(Web stream)'),
            ('promise-finished', 'promises.finished(value)', 'finished(Web stream)'),
            ('addAbortSignal', 'stream.addAbortSignal(new AbortController().signal,value)', 'addAbortSignal(Web stream)')]
        for op, invocation, factory_op in invocations:
            name = shape+'-'+op
            source = prefix+'const value='+value+';\n'+invocation+';\nexport function run(){return "unreachable";}\n'
            rows.append((name, op, False, factory_op, source))
            overloads.append({'name': name, 'code': 'ERR_SM_NODE_UNSUPPORTED', 'operation': factory_op})
    for op, invocation in [('callback-function-stage', 'stream.pipeline(function stage(){},'+sink+',()=>{})'), ('promise-function-stage', 'promises.pipeline(function stage(){},'+sink+')')]:
        source = prefix+invocation+';\nexport function run(){return "unreachable";}\n'
        rows.append((op, op, False, 'pipeline(function stage)', source))
        overloads.append({'name': op, 'code': 'ERR_SM_NODE_UNSUPPORTED', 'operation': 'pipeline(function stage)'})
    return rows, expressions, overloads


def embedded_cores(data):
    assert data[:8] == b'\0asm\x0d\0\x01\0'
    offset = 8
    cores = []
    while offset < len(data):
        section = data[offset]
        offset += 1
        length = shift = 0
        while True:
            value = data[offset]
            offset += 1
            length |= (value & 127) << shift
            if value < 128:
                break
            shift += 7
            assert shift <= 35
        assert offset + length <= len(data)
        payload = data[offset:offset+length]
        offset += length
        if section == 1:
            assert payload[:8] == b'\0asm\x01\0\0\0'
            cores.append({'sha256': digest(payload), 'bytes': len(payload)})
    assert offset == len(data)
    return cores



def checked_index(root, expected, count=None):
    data = load(root/'index.json', expected)
    paths = {row['path'] for row in data['files']}
    assert len(paths) == len(data['files'])
    assert count is None or count == len(paths)
    for row in data['files']:
        file(local(root, row['path']), row['sha256'], row['bytes'])
    return data


def wit_for(imports):
    middle = ''.join('  import '+name+';\n' for name in imports)
    return ('package root:component;\n\nworld root {\n'+middle+ ('\n' if imports else '') +
            '  export run: func() -> string;\n}\n').encode()


def output_membership(root, published):
    actual, links = set(), []
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs+files:
            path = Path(directory)/name
            if path.is_symlink():
                links.append({'path': str(path.relative_to(root)), 'linkText': os.readlink(path),
                              'resolvedTarget': str(path.resolve(strict=True))})
            elif path.is_file():
                actual.add(str(path.relative_to(root)))
            else:
                assert path.is_dir(), path
        dirs[:] = [name for name in dirs if not (Path(directory)/name).is_symlink()]
    assert actual == published | {'completion.json'}
    assert len(links) == 1 and links[0]['path'] == 'node_modules'
    assert links[0]['linkText'] == '/tmp/starling-node-compat/native-toolchain-lock/node_modules'
    return links


def verify_disabled(pins, composed):
    output = OUTPUT/'disabled-off'
    root_path = BASE/'production-adoption-v1/corrected-disabled-off-component-root-results.json'
    root = load(root_path, '2dc43cf406bb12c4abd27fbdcaf50bff9d37bd4b6882dfba05889b0dba769bc7')
    assert root['rawTerminalExitCode'] == 0 and root['toolSession'] == 3145
    assert root['state'] == 'ROOT_CORRECTED_CLASSIC_DISABLED_ADMISSION_GATE_PASSED'
    for row in root['files']:
        file(row['path'],row['sha256'],row['bytes'])
    report = load(output/'results.json','be60d577cfb591946340c367b048adfa871820f42f3aaadcd592c78e8353e3f3')
    completion = load(output/'completion.json')
    assert completion['results'] == file_relative(output/'results.json','results.json')
    assert completion['state'] == 'CLASSIC_GATE_OUTPUTS_COMPLETE_REQUIRES_EXTERNAL_EXIT_ZERO'
    assert completion['reportStatus'] == report['status'] == 'FUTURE_CLASSIC_DISABLED_ADMISSION_GATE_PASSED'
    assert completion['finalAdmissionRecheckCompletedBeforeReportPublication'] is True
    assert completion['requiresIndependentTerminalExitCodeZero'] is True
    assert completion['terminalExitCodeObservedByThisHelper'] is None and completion['runtimeAcceptanceClaim'] is False
    pin = pins['variants']['disabled-off']
    assert report['pin'] == pin and completion['engineSha256'] == report['engineSha256'] == root['engineSha256'] == pin['engineSha256']
    assert pin['classicStreamsEnabled'] is False and pin['sourceContractVersion'] == 'sm-classic-trace-source-v1'
    assert report['componentizerInvoked'] is report['componentBuilt'] is report['hostExecuted'] is False
    assert root['componentizerInvoked'] is root['componentBuilt'] is root['hostExecuted'] is False
    assert report['failures'] == root['denials']
    assert len(report['failures']) == 8
    for n,row in enumerate(report['failures']):
        module=['node:stream','stream','node:stream/promises','stream/promises'][n//2]
        common=bool(n%2)
        assert row['id'] == module and row['commonJS'] is common
        # JSON.stringify on these ASCII module IDs equals compact JSON.
        quoted=json.dumps(module,separators=(',',':'))
        source=('module.exports=require('+quoted+');\n' if common else
                'import * as value from '+quoted+'; export {value};\n')
        path=output/('disabled-'+str(n)+('.cjs' if common else '.mjs'))
        assert path.read_text() == source
        file(path,row['sourceSha256'])
        assert digest(source.encode()) == row['sourceSha256']
        expected=('CommonJS require is not admitted: ' if common else 'Node builtin is not admitted by this profile: ')+module
        assert expected in row['error']
    names={r['path'] for r in completion['files']}
    assert len(names) == len(completion['files']) == 10
    for row in completion['files']:
        file(local(output,row['path']),row['sha256'],row['bytes'])
    actual={str(p.relative_to(output)) for p in output.rglob('*') if p.is_file()}
    assert actual == names | {'completion.json'}
    assert not any(p.is_symlink() for p in output.rglob('*'))
    assert completion['componentFiles'] == completion['generatedWasmFiles'] == completion['generatedJavaScriptFiles'] == []
    return {'report':file(output/'results.json'),'completion':file(output/'completion.json'),
        'publishedFilesRehashed':10,'denials':8,'exactSourcesReconstructed':True,
        'componentizerInvoked':False,'componentBuilt':False,'hostExecuted':False,
        'terminalExitEvidence':{'rootReceipt':file(root_path),'observedByRoot':0,'session':3145,'observedByThisReader':False}}


def file_relative(path,name):
    row=file(path)
    return {'path':name,'sha256':row['sha256'],'bytes':row['bytes']}


def main():
    supplement = load(HERE/'native-results.json')
    assert supplement['state'] == 'CORRECTED_CLASSIC_CURRENT_SOURCE_NATIVE_REHASH_PASSED'
    assert supplement['activatedFilesRehashed'] == 26 and supplement['consumedFilesRehashed'] == 6414
    assert supplement['toolTreesMembershipChecked'] == 2 and supplement['toolLinksRechecked'] == 22
    assert supplement['guestHostBuildTranspileOrNodeExecuted'] is False
    supplement_files = supplement['verifiedFiles']
    file(HERE/supplement_files['path'], supplement_files['sha256'], supplement_files['bytes'])
    checked_index(RUNTIME, INDEX_SHA, 26)
    checked_index(BASE/'independent-trace-runtime-family-review-v1', REVIEW_SHA)
    pins = load(RUNTIME/'runtime-pins.json', PINS_SHA)
    authority = load(RUNTIME/'root-review-receipt.json', AUTHORITY_SHA)
    composed = load(BASE/'production-adoption-v1/corrected-classic-runtime-root-results-v1.json',
        '681f81bd6649f66e7c1a8852c4816afbc4dbab3d3306a3af8b796674548aa160')
    assert composed['runtimeFamilyIndexSha256'] == INDEX_SHA
    for row in composed['files']:
        file(row['path'],row['sha256'],row['bytes'])
    oracle_path = RUNTIME/'harness/node-oracle-results.json'
    oracle = load(oracle_path)
    for row in oracle['sourceInputs']:
        file(oracle_path.parent/row['path'], row['sha256'], row['bytes'])
    file(oracle['nodeExecutable'], oracle['nodeExecutableSha256'])
    expected_path = BASE/'implementation-candidate-v1/node-final-acceptance-results.json'
    expected_record = load(expected_path)
    expected = expected_record['expected']
    assert oracle['node'] == 'v22.14.0' and oracle['versions']['node'] == '22.14.0'
    assert oracle['groupCount'] == len(expected) == 19
    assert oracle['status'] == 'NODE22_ONLY_EXACT_SINGLE_WAIT_TRANSFORM_PASSED'
    assert oracle['transform']['occurrenceCount'] == 1
    assert oracle['transform']['from'] == 'await new Promise(resolve=>process.nextTick(resolve));'
    assert oracle['transform']['to'] == 'await promises.finished(source).catch(()=>{});'
    assert oracle['transform']['byteExactReplacementVerified'] is True
    before = (BASE/'implementation-candidate-v1/checks.mjs').read_bytes()
    after = (RUNTIME/'harness/checks.mjs').read_bytes()
    old, new = (oracle['transform'][key].encode() for key in ['from', 'to'])
    assert before.count(old) == 1 and after == before.replace(old, new)
    assert oracle['transformedObserved'] == oracle['originalObserved'] == expected
    manifest = load(BASE/'implementation-candidate-v1/export-manifest.classic-streams.node-v22.14.0.json')
    vectors, expressions, overloads = initializer_vectors()
    assert len(vectors) == 65 and len(expressions) == 24 and len(overloads) == 17
    deferred = [{'operation': op, 'construct': construct, 'code': 'ERR_SM_NODE_UNSUPPORTED'}
                for op, _ in expressions for construct in [False, True]]
    limits = [{'name': name, 'boundary': boundary, 'code': 'ERR_SM_NODE_STREAM_LIMIT', 'operation': op}
              for name, boundary, op in [('writable object units', 4096, 'write'),
                ('readable byte chunks', 4096, 'push'), ('readable byte units', 16777216, 'push')]]

    def observed(value, call):
        assert value['call'] == call and value['retainedDefaultBefore'] == (65536 if call == 1 else 777)
        assert value['snapshotDefaults'] == [65536, 16]
        assert value['snapshotIdentity'] is (True if call == 1 else None)
        assert value['ordinary'] == expected and value['deferred'] == deferred and value['overloads'] == overloads
        assert value['limits'] == limits and value['nativeHex'] == '00cafeff'
        assert value['rooting'] == {'hexRounds': 8, 'streamIdentity': True, 'callbackCalls': 1, 'abortCalls': 1, 'disposedCalls': 0}
        graph = value['graph']
        assert graph['rootKeys'] == manifest['modules']['node:stream']['exports']
        assert graph['promiseKeys'] == manifest['modules']['node:stream/promises']['exports']
        assert all(graph[key] is True for key in ['aliases', 'staticCommonJS', 'globalBufferIdentity', 'namedBindingSnapshots'])
        assert graph['customPromisify'] == ['pipeline', 'finished']

    file(TOOL, TOOL_SHA)
    native_imports = ['node:buffer', 'node:events', 'node:stream', 'node:stream/promises', 'node:util']
    variants = {}
    adapter_wats = {}
    for variant, mode in MODES.items():
        output = OUTPUT/variant
        collector_path = BASE/'production-adoption-v1'/('corrected-'+variant+'-component-root-results.json')
        root = load(collector_path)
        assert root['state'] == 'ROOT_CORRECTED_CLASSIC_COMPONENT_SUITE_VERIFIED'
        assert root['rawTerminalExitCodeObservedByRoot'] == 0 and root['toolSession'] == mode['session']
        for key,value in {'ordinaryGroups':19,'deferredCallAndConstructCases':48,'overloadRefusals':17,'stateLimitCases':3,'initializerFailures':65,'retainedJcoCalls':3,'freshJcoCalls':1,'freshWasmtimeCalls':1,'deployedFatalDiscardCase':1,'deployedCleanControls':2}.items():
            assert root[key] == value
        assert root['resultSha256'] == mode['result'] and root['completionSha256'] == mode['completion']
        assert root['runtimeFamilyIndexSha256'] == INDEX_SHA
        assert root['sourceContractVersion'] == 'sm-classic-trace-source-v1'
        for stream in ['stdout','stderr']:
            log=Path('/tmp/starling-node-compat')/('classic-corrected-'+variant+'-suite-v1.'+stream+'.log')
            file(log, digest(b''), 0)
        completion = load(output/'completion.json', mode['completion'])
        report = load(output/'results.json', mode['result'])
        names = {r['path'] for r in completion['files']}
        assert len(completion['files']) == len(names) == mode['published']
        for row in completion['files']:
            file(local(output, row['path']), row['sha256'], row['bytes'])
        output_links = output_membership(output, names)
        assert completion['state'] == 'CLASSIC_GATE_OUTPUTS_COMPLETE_REQUIRES_EXTERNAL_EXIT_ZERO'
        assert completion['finalAdmissionRecheckCompletedBeforeReportPublication'] is True
        assert completion['requiresIndependentTerminalExitCodeZero'] is True
        assert completion['terminalExitCodeObservedByThisHelper'] is None
        assert completion['runtimeAcceptanceClaim'] is False
        assert completion['results'] == {'path': 'results.json', 'sha256': mode['result'], 'bytes': mode['resultBytes']}
        assert report['status'] == completion['reportStatus'] == 'FUTURE_CLASSIC_REAL_COMPONENT_GATES_PASSED'
        assert report['variant'] == completion['variant'] == variant
        assert report['engineSha256'] == completion['engineSha256'] == mode['engine']
        pin = pins['variants'][variant]
        assert report['pin'] == pin and pin['engineSha256'] == mode['engine']
        assert pin['sourceContractVersion'] == 'sm-classic-trace-source-v1'
        assert pin['classicTraceSourcePolicy']['changedNativePaths'] == 3
        assert report['sourceRoot'] == pin['sourceRoot']
        file(pin['enginePath'], mode['engine'], mode['engineBytes'])
        assert report['engineReceipt'] == load(pin['enginePath']+'.build.json', pin['receiptSha256'])
        load(pin['freezeReceiptPath'], pin['freezeReceiptSha256'])
        assert len(pin['frozenFiles']) == len({r['path'] for r in pin['frozenFiles']}) == 474
        for row in pin['frozenFiles']:
            file(row['path'], row['sha256'], row['bytes'])
        for key in ['engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256']:
            assert authority['variants'][variant][key] == pin[key]
        assert report['gcStressConfigured'] is mode['gc']
        receipt = report['engineReceipt']
        assert receipt['gcStress'] is mode['gc']
        assert receipt['oomTesting'] is False and receipt['debuggerEnabled'] is False
        assert receipt['hostApi'] == 'wasi-0.2.10' and receipt['entropyPolicy'] == mode['entropy']
        assert report['capabilityPolicy']['selectedInterfaces'] == mode['imports']
        assert report['capabilityPolicy']['entropyPolicy'] == mode['entropy']
        provenance = report['componentizerProvenance']
        assert provenance['selection'] == 'patched-import-i32-clock-v2'
        assert provenance['legacyEngineDiagnosticEnabled'] is False and provenance['debugScalarOOMDiagnostic'] is None
        file(provenance['manifestPath'], provenance['manifestSha256'])
        for patch in [provenance['patch']]+provenance['additionalPatches']:
            file(patch['path'], patch['sha256'])
        file(provenance['lock']['path'], provenance['lock']['sha256'])
        file(output/'classic.bundle.mjs', report['bundle']['sha256'])
        assert sorted(report['bundle']['imports']) == native_imports
        bundle_text = (output/'classic.bundle.mjs').read_text()
        assert sorted(re.findall(r'^import .*? from "([^"]+)";', bundle_text, re.MULTILINE)) == native_imports
        assert set(report['bundle']['moduleIds']) == {
            str(RUNTIME/'harness/checks.mjs'), str(RUNTIME/'harness/guest.mjs'),
            str(RUNTIME/'harness/cjs-bindings.cjs')+'.native-profile.mjs'}
        assert 'builtinFactory' not in bundle_text
        for row in report['selectedManifests']:
            file(Path(report['sourceRoot'])/row['path'], row['sha256'])
        assert report['selectedManifests'] == receipt['selectedModuleManifests']
        assert file(oracle_path)['sha256'] == report['oracleReceiptSha256']
        assert file(expected_path)['sha256'] == report['expectedReceiptSha256']
        assert report['ordinaryGroups'] == 19
        retained = report['snapshotAndRetained']['retained']
        assert len(retained) == 3
        for call, value in enumerate(retained, 1):
            observed(value, call)
        observed(report['snapshotAndRetained']['fresh'], 1)
        observed(report['wasmtime']['observed'], 1)
        assert report['wasmtime']['stderr'] == ''
        assert re.fullmatch('[0-9a-f]{64}',report['wasmtime']['stdoutSha256'])
        file(report['wasmtime']['path'], report['wasmtime']['sha256'])
        assert report['wasmtime']['version'] == 'wasmtime 42.0.1 (6844a83b5 2026-02-25)'
        failures = report['initializationFailures']
        assert len(failures) == 65
        for number, (row, vector) in enumerate(zip(failures, vectors)):
            name, operation, construct, factory_op, text = vector
            assert (row['name'], row['operation'], row['construct'], row['expectedFactoryOperation']) == (name, operation, construct, factory_op)
            expected_message = 'node:stream.'+factory_op+' is unavailable in sm-node-22.14.0-m0.12'
            assert row['expectedFactoryMessage'] == expected_message and expected_message in row['error']
            assert row['error'].startswith('Failed to initialize component (wizer (')
            assert 'Exception while evaluating top-level script' in row['error']
            assert set(row['imports']) <= {'node:stream', 'node:stream/promises'}
            assert digest(text.encode()) == row['sourceSha256']
            file(output/('initializer-'+str(number)+'.mjs'), row['sourceSha256'])
            assert (output/('initializer-'+str(number)+'.mjs')).read_text() == text
        fatal = report['deployedFailures']
        assert fatal['jco'] == {'status': 0, 'stdout': 'EXPECTED_FATAL_DISCARD\n', 'stderr': ''}
        assert fatal['wasmtime']['status'] == 134 and 'unreachable' in fatal['wasmtime']['stderr']
        assert 'UNEXPECTED_FATAL_RETURN' not in fatal['wasmtime']['stdout']
        assert fatal['policy'] == 'One invocation per fresh instance; terminal failure; discard, never reuse'
        child="import {run} from "+json.dumps('file://'+fatal['fixture']['modulePath'])+";\n"+"try{await run();console.log('UNEXPECTED_FATAL_RETURN');process.exitCode=2;}catch(error){console.log('EXPECTED_FATAL_DISCARD');}\n"
        assert (output/'deployed-fatal-child.mjs').read_text() == child
        file(output/'deployed_fatal.source.mjs', fatal['fixture']['sourceSha256'])
        assert (output/'deployed_fatal.source.mjs').read_text() == "import {compose} from 'node:stream';\nexport function run(){compose();return 'UNEXPECTED_FATAL_RETURN';}\n"
        assert len(report['deployedControls']) == 2
        for control in report['deployedControls']:
            kind = control['kind']
            path = output/('deployed_'+kind.replace('-', '_')+'.source.mjs')
            file(path, control['fixture']['sourceSha256'])
            control_source = path.read_text()
            assert "for(const key of ['code','module','operation','profile'])if(!Object.hasOwn(error,key))" in control_source
            assert kind in ['caught', 'handled-later'] and len(control['retainedJcoCalls']) == 3
            for call, value in enumerate(control['retainedJcoCalls'], 1):
                assert value['kind'] == kind and value['calls'] == call and value['completed'] is True
                assert value['error'] == {'code': 'ERR_SM_NODE_UNSUPPORTED', 'module': 'node:stream', 'operation': 'compose', 'profile': 'sm-node-22.14.0-m0.12'}
                if kind == 'handled-later':
                    assert value['handledAfterReaction'] is True
            assert control['freshWasmtime']['status'] == 0 and control['freshWasmtime']['stderr'] == ''
            assert control['freshWasmtime']['observed'] == control['retainedJcoCalls'][0]
            assert re.fullmatch('[0-9a-f]{64}',control['freshWasmtime']['stdoutSha256'])
        caught_source = "import * as stream from 'node:stream';\nimport * as promises from 'node:stream/promises';\nlet error;try{stream.compose();}catch(caught){error=caught;}\nif(error?.code!=='ERR_SM_NODE_UNSUPPORTED'||!Object.hasOwn(error,'code'))throw new Error('Caught initialization error contract');\nexport function run(){return 'caught-top-level-control';}\n"
        file(output/'initializer-caught-control.mjs', report['caughtInitializerControl']['sourceSha256'])
        assert (output/'initializer-caught-control.mjs').read_text() == caught_source
        assert len(completion['componentFiles']) == 5
        assert len(completion['generatedWasmFiles']) == len(completion['generatedJavaScriptFiles']) == 4
        records = [report['component'], fatal['fixture']] + [x['fixture'] for x in report['deployedControls']] + [report['caughtInitializerControl']]
        by_path = {Path(x.get('path', x.get('componentPath'))).name: x for x in records}
        assert set(by_path) == set(completion['componentFiles'])
        wit_audits = []
        wit = wit_for(mode['imports'])
        static_wit = wit + (b'package wasi:random@0.2.10 {\n  interface random {\n    get-random-bytes: func(len: u64) -> list<u8>;\n\n    get-random-u64: func() -> u64;\n  }\n}\n' if mode['imports'] else b'')
        (HERE/variant).mkdir(exist_ok=True)
        for name in completion['componentFiles']:
            fixture = by_path[name]
            component_path = output/name
            artifact = file(component_path, fixture.get('sha256', fixture.get('componentSha256')))
            assert fixture['interfaceAudit']['emittedImports'] == fixture['interfaceAudit']['selectedInterfaces'] == mode['imports']
            assert fixture['interfaceAudit']['componentSha256'] == artifact['sha256']
            root_component = next(r for r in root['components'] if Path(r['path']).name == name)
            assert root_component['sha256'] == artifact['sha256']
            assert root_component['emittedImports'] == mode['imports']
            if 'emittedWit' in fixture:
                assert fixture['emittedWit'].encode() == wit
            argv = [str(TOOL), 'component', 'wit', str(component_path)]
            result = subprocess.run(argv, capture_output=True, timeout=55)
            assert result.returncode == 0 and result.stderr == b'' and result.stdout == static_wit
            assert root_component['witSha256'] == digest(result.stdout) and root_component['wasmtoolsExitCode'] == 0
            (HERE/variant/(name+'.wit')).write_bytes(result.stdout)
            wit_audits.append({'component': artifact, 'argv': argv, 'exitCode': result.returncode,
                'witSha256': digest(result.stdout), 'imports': mode['imports'], 'export': 'run: func() -> string'})
        pairs = []
        for name in completion['generatedWasmFiles']:
            core = file(output/name)
            stem = name[:-len('.core.wasm')]
            embedded = embedded_cores((output/(stem+'.component.wasm')).read_bytes())
            assert embedded[0] == {'sha256': core['sha256'], 'bytes': core['bytes']}
            glue = output/(stem+'.js')
            glue_text = glue.read_text()
            assert "new URL('./"+name+"', import.meta.url)" in glue_text
            inline = [base64.b64decode(text+'='*((-len(text))%4))
                      for text in re.findall(r"base64Compile\('([^']+)'\)", glue_text)]
            assert embedded[1:] == [{'sha256': digest(data), 'bytes': len(data)} for data in inline]
            assert len(inline) == (2 if mode['imports'] else 0)
            assert sorted(re.findall(r'^import .*? from "([^"]+)";', glue_text, re.MULTILINE)) == (
                ['@bytecodealliance/preview2-shim/random'] if mode['imports'] else [])
            for number, data in enumerate(inline, 1):
                key = digest(data)
                if key not in adapter_wats:
                    argv = [str(TOOL), 'print', '-']
                    printed = subprocess.run(argv, input=data, capture_output=True, timeout=55)
                    assert printed.returncode == 0 and printed.stderr == b''
                    wat = printed.stdout.decode()
                    assert '(type (;0;) (func (param i64 i32)))' in wat
                    if number == 1:
                        assert '(import ' not in wat and 'call_indirect (type 0)' in wat
                    else:
                        assert re.findall(r'\(import "([^"]+)" "([^"]+)"', wat) == [('actual','0'),('shim','$imports')]
                    wat_name = 'adapter-'+key+'.wat'
                    (HERE/wat_name).write_bytes(printed.stdout)
                    adapter_wats[key] = {'binarySha256': key, 'binaryBytes': len(data), 'textPath': wat_name,
                        'textSha256': digest(printed.stdout), 'argv': argv, 'exitCode': printed.returncode,
                        'interpretation': 'Internal canonical-ABI indirection table; not an external component host capability'}
            pairs.append({'core': core, 'component': stem+'.component.wasm', 'exactEmbeddedMainCoreBytes': True,
                'embeddedCores': embedded, 'glue': str(glue), 'glueNamesMainCore': True,
                'inlineAdapterBytesEqualRemainingEmbeddedCores': True})
        file(output/'results.json', mode['result'])
        file(output/'completion.json', mode['completion'])
        variants[variant] = {
            'report': file(output/'results.json'), 'completion': file(output/'completion.json'),
            'publishedFilesRehashed': mode['published'], 'outputFileMembershipExact': True,
            'outputLinks': output_links, 'engineSha256': mode['engine'], 'engineBytes': mode['engineBytes'],
            'frozenNativeFilesRehashed': 474, 'gcStressConfigured': mode['gc'],
            'ordinaryNodeGroups': 19, 'deferredCallAndConstructCases': 48, 'overloadRefusals': 17, 'logicalLimits': 3,
            'exactInitializerSourcesAndFactoryMessages': 65, 'retainedJcoCalls': 3, 'freshJcoCalls': 1, 'freshWasmtimeCalls': 1,
            'deployedCaughtOrHandledControls': 2, 'deployedFatalFreshDiscardCases': 1, 'caughtInitializerComponentPreserved': True,
            'snapshotIdentity': {'firstAndFresh': True, 'retainedSecondAndThird': None, 'retainedDefaultBeforeSecondAndThird': 777},
            'terminalExitEvidence': {'collector': file(collector_path), 'observedByRoot': 0,
                'session': mode['session'], 'observedByThisReader': False},
            'mainWasmtimeRawStdoutPreserved':False, 'cleanControlWasmtimeRawStdoutPreserved':False, 'mainWasmtimeStdoutSha256':report['wasmtime']['stdoutSha256'],
            'structuralWitAudits': wit_audits, 'externalComponentImports': mode['imports'],
            'exactCoreComponentGlueRelations': pairs,
        }
    disabled = verify_disabled(pins,composed)
    # All three suite variants use identical application source and observable cases.
    for row in vectors:
        assert len(row) == 5
    for name in ['classic.bundle.mjs', 'deployed_fatal.source.mjs', 'deployed_caught.source.mjs',
                 'deployed_handled_later.source.mjs', 'initializer-caught-control.mjs'] + ['initializer-'+str(i)+'.mjs' for i in range(65)]:
        assert (OUTPUT/'normal-off'/name).read_bytes() == (OUTPUT/'normal-runtime'/name).read_bytes() == (OUTPUT/'gc-off'/name).read_bytes()
    file(RUNTIME/'index.json', INDEX_SHA)
    result = {
        'schemaVersion': 1, 'state': 'INDEPENDENT_CORRECTED_CLASSIC_COMPLETED_RESULTS_REVIEW_PASSED',
        'reviewedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'activatedIndex': file(RUNTIME/'index.json'), 'activatedFilesRehashed': 26,
        'currentSourceNativeReview': file(HERE/'native-results.json'),
        'consumedFilesRehashedByNativeReader': 6414, 'toolLinksRecheckedByNativeReader': 22,
        'priorFullSourceReviewIndex': file(BASE/'independent-trace-runtime-family-review-v1/index.json', REVIEW_SHA),
        'pinsSha256': PINS_SHA, 'rootAuthoritySha256': AUTHORITY_SHA,
        'composedRootReceipt': file(BASE/'production-adoption-v1/corrected-classic-runtime-root-results-v1.json'),
        'composedRootReferencesRehashed':len(composed['files']), 'disabled': disabled,
        'nodeOracleReceipt': file(oracle_path), 'nodeOracleExecutableRehashed': True,
        'nodeOracleWaitTransformReconstructed': oracle['transform'],
        'nodeOracleOriginalAndTransformedObservationsEqualExpected': True,
        'mainNativeImports': native_imports, 'variants': variants,
        'wasmTools': file(TOOL), 'internalAdapters': list(adapter_wats.values()),
        'limits': [
            'This reader performed Python reads/hashes plus static wasm-tools WIT/print only; no guest, Node, admission, build, componentization, transpile, or host invocation.',
            'The external raw terminal exit zero is Root-observed evidence, not an observation by this reader; collectors are corroboration, not source/native authority.',
            'Recorded main Wasmtime observations are compared with the sealed actual Node oracle. Main and successful clean-control Wasmtime records retain stdout digests and parsed observations, with raw stderr, but no raw stdout bytes; this reader does not independently decode those missing original streams. Fatal Wasmtime stdout/stderr and fatal Jco stdout/stderr are retained and checked. No raw observation is transferred from the separate Node11 component.',
            'The fatal Jco child catches expected failure and exits zero. Wasmtime status 134 is a generic trap whose originating error is not identified. Own error fields are checked by guest source guards and the recorded parsed observations in the two successful paired controls.',
            'GC stress is configured only for GC-OFF. Eight byte round trips retain combined JavaScript owners and callbacks; no isolated VM queue-root or prototype-key proof is established.',
            'Logical limits cover buffered stream units/chunks rather than total heap; affected streams and terminally failed instances are discarded.',
            'No full Node streams parity, performance, ALS propagation, request reuse, reset/teardown, or safe failed-instance reuse claim follows from these bounded suites.'
        ],
        'sourceContractVersion':'sm-classic-trace-source-v1', 'actualNativeSources':342, 'unchangedNativePaths':339, 'changedNativePaths':3,
        'sourceAdmissionAndCompletionSourceInspected':True,
        'readerAncestor': file(BASE/'independent-runtime-gc-component-review-v1/verify.py'),
        'guestHostOrBuildExecuted': False, 'completeNodeStreamsClaim': False,
        'performanceClaim': False, 'overallRoadmapComplete': False,
    }
    (HERE/'results.json').write_text(json.dumps(result, indent=2)+'\n')
    (HERE/'verified-files.json').write_text(json.dumps({'schemaVersion': 1,
        'files': sorted(checked.values(), key=lambda row: row['path'])}, indent=2)+'\n')
    print(json.dumps({'state': result['state'], 'variants': {k: {
        'publishedFiles': v['publishedFilesRehashed'], 'witAudits': len(v['structuralWitAudits']),
        'coreGlueRelations': len(v['exactCoreComponentGlueRelations'])} for k,v in variants.items()}}))


if __name__ == '__main__':
    main()
