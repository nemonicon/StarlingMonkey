"""Independent READ-ONLY review of existing ordinary Release diagnostic evidence.

No import of preflight/runner/packager and no subprocess, compiler or guest call.
Only new JSON verification receipts are written below HERE, exclusively.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shlex

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CANDIDATE = REPO/'tests/node-compat/foundation-scheduler/diagnostic-candidate-v1'
ROOT = Path('/tmp/starling-node-compat/foundation-scheduler-v2/native-freeze')
OUTPUT = Path('/tmp/starling-node-compat/foundation-scheduler-v4/ordinary-release-components-v1')
REPORT = OUTPUT/'results.json'
ENGINE_SHA = 'a49c920c83a5deb144c960f3d745f66b57754415546346c089b9f182d4b67f6b'
METADATA_SHA = 'c9bb8690ee74f08c5e62dc929870c9eb8f613e1ae694986e89b4d948c598463d'
RECIPE_SHA = '1e2f15d1aac2f86c3363390cc3c6261721a20c07fea8ca0825c68027154c0e19'
INPUT_SHA = 'c3aa23e2b1838ad4fe451e0f6243dd68b05014936db37b6baf062f44f43c9208'
verified = {}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def check_file(path, digest=None, size=None, below=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    if below:
        relative = path.relative_to(below)
        cursor = path
        while cursor != below:
            assert not cursor.is_symlink(), cursor
            cursor = cursor.parent
        assert relative.parts and '..' not in relative.parts
    value = sha(path)
    if digest:
        assert value == digest, path
    if size is not None:
        assert path.stat().st_size == size, path
    verified[str(path)] = {'path':str(path),'sha256':value,'bytes':path.stat().st_size}
    return value


def unique(rows, count):
    assert len(rows) == count and len({row['path'] for row in rows}) == count
    assert all(isinstance(row['path'],str) and re.fullmatch(r'[0-9a-f]{64}',row['sha256']) for row in rows)
    return {row['path']:row['sha256'] for row in rows}


def u32(data, offset):
    value = 0
    for shift in range(0,35,7):
        assert offset < len(data)
        byte = data[offset]
        offset += 1
        value |= (byte&127) << shift
        if not byte&128:
            assert value <= 0xffffffff
            return value,offset
    raise AssertionError('invalid section/vector u32')


def top_level_imports(path):
    # Component Model Binary.md: version/layer0d000100, section10 import vector.
    # This is a narrow section-boundary/import-count check, not a type validator.
    data = Path(path).read_bytes()
    assert data[:8] == bytes.fromhex('0061736d0d000100')
    offset, imports, sections = 8,0,0
    while offset < len(data):
        section = data[offset]
        size,start = u32(data,offset+1)
        end = start+size
        assert end <= len(data)
        if section == 10:
            count,tail = u32(data,start)
            imports += count
            assert count == 0 and tail == end
        offset = end
        sections += 1
    assert offset == len(data) and imports == 0
    return {'header':'component0d000100','topLevelImportCount':imports,'outerSections':sections,'fullTypeValidationRepeated':False}


def cli_observation(record):
    assert record['status'] == 0
    value = json.loads(record['stdout'].strip())
    if isinstance(value,str):
        value = json.loads(value)
    assert value == record['observed']
    return value


report_sha = check_file(REPORT)
r = read(REPORT)
assert r['state'] == 'private-diagnostic-ordinary-components-passed'
assert r['engineSha256'] == ENGINE_SHA and r['engineReceiptSha256'] == METADATA_SHA
assert r['declaredSourceInputs'] == {'productionNativeSources':306,'additionalDiagnosticSources':2,'totalDeclaredSourceInputs':308,'diagnosticCompileCommands':1,'layoutCompileCommands':63,'gcStress':False}
assert r['sourceInputsCheckedBeforeAfter'] is True
check_file(ROOT/'diagnostic-release.engine.wasm',ENGINE_SHA,9764903,ROOT)
check_file(ROOT/'diagnostic-release.engine.wasm.build.json',METADATA_SHA,below=ROOT)
metadata = read(ROOT/'diagnostic-release.engine.wasm.build.json')
assert metadata == r['producerReceipt']
assert metadata['diagnosticOnly'] is True and metadata['internalTicksEnabled'] is True
assert metadata['gcStress'] is False and metadata['oomTesting'] is False
assert metadata['strictInitialization'] is True and metadata['entropyPolicy'] == 'off'
assert metadata['debuggerEnabled'] is False and metadata['wptSupportEnabled'] is False
assert metadata['buildRecipeSha256'] == RECIPE_SHA
freeze_path = ROOT/'diagnostic-release-freeze-receipt.json'
check_file(freeze_path,r['frozenConfiguration']['receiptSha256'],below=ROOT)
freeze = read(freeze_path)
assert freeze['schemaVersion'] == 2 and freeze['sourcePartitions'] == [306,2]
assert freeze['engineSha256'] == ENGINE_SHA and freeze['metadataSha256'] == METADATA_SHA
assert freeze['recipeSha256'] == RECIPE_SHA and freeze['guestExecutedByHelper'] is False
assert freeze['actualLayoutCompileCommands'] == 61 and freeze['actualEmbeddingCompileCommands'] == freeze['actualDiagnosticCompileCommands'] == 1
assert freeze['nativeCompileDatabaseUsedForParentTargets'] is False
assert len(freeze['copies']) == len({row['path'] for row in freeze['copies']}) == 337
for row in freeze['copies']:
    check_file(row['path'],row['sha256'],row['bytes'],ROOT)
native = unique(metadata['sourceManifest'],306)
diag = metadata['internalTickDiagnosticPolicy']
extra = unique(diag['sourceManifest'],2)
assert not set(native)&set(extra)
policy = read(ROOT/'source-policy.json')
assert native == unique(policy['expectedNativeSourceManifest'],306)
for path,digest in (native|extra).items():
    check_file(ROOT/'source'/path,digest,below=ROOT)
for row in metadata['componentizeSourceManifest']:
    check_file(ROOT/'componentize-source'/row['path'],row['sha256'],below=ROOT)
assert unique(metadata['componentizeSourceManifest'],3).keys() == {'embedding/embedding.cpp','embedding/embedding.h','CMakeLists.txt'}
check_file(ROOT/'build-diagnostic-engine.sh',RECIPE_SHA,below=ROOT)
cache_bytes = (ROOT/'diagnostic-release-CMakeCache.txt').read_bytes()
db_bytes = (ROOT/'diagnostic-release-compile_commands.json').read_bytes()
assert cache_bytes == (ROOT/'diagnostic-release-CMakeCache.before.txt').read_bytes()
assert db_bytes == (ROOT/'diagnostic-release-compile_commands.before.json').read_bytes()
assert hashlib.sha256(cache_bytes).hexdigest() == metadata['cmakeCacheSha256'] == r['frozenConfiguration']['frozenCacheSha256']
assert hashlib.sha256(db_bytes).hexdigest() == metadata['compileCommandsSha256'] == r['frozenConfiguration']['frozenCompileCommandsSha256']
cache = {}
for line in cache_bytes.decode().splitlines():
    if re.match(r'^[^/#][^:]*:[^=]*=',line):
        key,value = line.split('=',1)
        cache[key.split(':',1)[0]] = value
for options in [metadata['requestedCMakeOptions'],metadata['observedCMakeOptions']]:
    assert all(cache[key] == value for key,value in options.items())
assert cache['CMAKE_BUILD_TYPE'] == 'Release' and cache['NODE_COMPAT_GC_STRESS'] == 'OFF'
assert cache['NODE_COMPAT_INTERNAL_TICKS'] == 'ON' and cache['ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS'] == 'ON'
configured = Path(diag['configuredSourceRoot'])
cpp = {str(configured/path) for path in native if path.endswith('.cpp') and path.startswith(('runtime/','builtins/'))}
database = json.loads(db_bytes)
layout = [row['command'] for row in database if row['file'] in cpp]
assert len(layout) == 61
assert layout == metadata['internalTickPolicy']['actualLayoutCompileCommands'] == metadata['protectedAbortListenerPolicy']['actualLayoutCompileCommands']
queue = [row['command'] for row in database if row['file'] == str(configured/'runtime/node_tick_queue.cpp')]
assert len(queue) == 1 and queue == metadata['internalTickPolicy']['actualQueueCompileCommands']
strict_paths = {str(configured/path) for path in ['builtins/web/event/event-target.cpp','runtime/engine.cpp','runtime/event_loop.cpp']}
strict = [row['command'] for row in database if row['file'] in strict_paths]+queue
assert len(strict) == 4 and strict == metadata['strictEventExceptionPolicy']['actualNativeCompileCommands']
ev = diag['parentTargetCommandEvidence']
assert freeze['parentTargetCommandEvidence'] == ev
assert ev['version'] == 'ninja-parent-target-commands-before-after-v2' and ev['exactBytesUnchanged'] is True
assert ev['collectionCommand'] == ['ninja','-C',ev['buildDirectory'],'-t','commands','builtin_componentize_embedding','builtin_diagnostics_internal_ticks']
before = (ROOT/'diagnostic-release-parent-targets.before.commands.txt').read_bytes()
after = (ROOT/'diagnostic-release-parent-targets.after.commands.txt').read_bytes()
assert before == after
for key,raw in [('before',before),('after',after)]:
    assert hashlib.sha256(raw).hexdigest() == ev[key]['sha256'] and len(raw) == ev[key]['bytes']
parent = []
for key in ['embedding','diagnostic']:
    target = ev['targets'][key]
    selected = []
    for line in after.decode().splitlines():
        args = shlex.split(line)
        if '-c' in args and args[args.index('-c')+1] == target['sourcePath']:
            selected.append(line)
    assert len(selected) == 1 and selected == target['compileCommands']
    assert selected == (metadata['actualEmbeddingCompileCommands'] if key == 'embedding' else diag['actualCompileCommands'])
    assert all(row['file'] != target['sourcePath'] for row in database)
    parent += selected
for command in layout+parent:
    args = shlex.split(command)
    assert '-c' in args and '-O3' in args and '-DNDEBUG' in args and '-fsyntax-only' not in args and '-DDEBUG' not in args
    for macro in ['NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_ENTROPY_POLICY','NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER']:
        assert '-D'+macro+'=1' in args
    assert '-DNODE_COMPAT_GC_STRESS=1' not in args and '-DNODE_COMPAT_OOM_TESTING=1' not in args
install = (ROOT/'diagnostic-release-builtins.incl').read_text()
assert install == diag['generatedBuiltinInclude']['contents']
assert install.splitlines().count('NS_DEF(diagnostics::internal_ticks)') == 1
check_file(CANDIDATE/'input-freeze.json',INPUT_SHA)
inputs = read(CANDIDATE/'input-freeze.json')['inputs']
assert len(inputs) == 24 and r['sourceManifest'] == inputs
for row in inputs:
    check_file(CANDIDATE/row['path'],row['sha256'],row['bytes'])
check_file(CANDIDATE/'index.json','e7f5febde15a0b53beef5d2e0d655d8e428c2d49ad1625513a19b21001a12286')
for row in read(CANDIDATE/'index.json')['files']:
    check_file(CANDIDATE/row['path'],row['sha256'],row['bytes'])
oracle = read(CANDIDATE/'../node-results.json')
assert r['node']['release'] == 'v22.14.0' and r['node']['binarySha256'] == oracle['nodeBinarySha256']
check_file(oracle['nodeBinary'],r['node']['binarySha256'])
check_file(CANDIDATE/'../node-results.json',r['node']['oracleSha256'])
phases = {row['boundary']:row['trace'] for row in oracle['boundaryCases']}
assert r['node']['expectedPhases'] == {'esm':phases['esm-initial'],'task':phases['task'],'job':phases['promise-job']}
expected_names = ['main','configured-classic','initializer','late','handled-throw','handled-rejection','finite-checkpoint-budget','deployed-throw','deployed-rejection','checkpoint-work-limit']
assert [row['name'] for row in r['artifacts']] == expected_names
artifact_checks = []
artifacts = {row['name']:row for row in r['artifacts']}
for row in r['artifacts']:
    check_file(row['componentPath'],row['componentSha256'],row['componentBytes'],OUTPUT)
    check_file(row['sourcePath'],row['sourceSha256'],below=OUTPUT)
    audit = row['interfaceAudit']
    assert audit['state'] == 'verified-final-component' and audit['componentSha256'] == row['componentSha256']
    assert audit['selectedInterfaces'] == audit['emittedImports'] == audit['unusedSelectedInterfaces'] == []
    assert audit['entropyPolicy'] == 'off' and not re.search(r'^\s*import\b',row['emittedWit'],re.M)
    binary = top_level_imports(row['componentPath'])
    if row['name'] == 'late':
        assert 'export inspect-result: func() -> string;' in row['emittedWit'] and 'export api: interface' in row['emittedWit']
    else:
        assert row['emittedWit'] == 'package root:component;\n\nworld root {\n  export run: func() -> string;\n}\n'
    module = Path(row['modulePath'])
    check_file(module,below=OUTPUT)
    core = module.with_name(module.stem+'.core.wasm')
    assert core.name in module.read_text()
    check_file(core,below=OUTPUT)
    artifact_checks.append({'name':row['name'],'componentSha256':row['componentSha256'],'componentBytes':row['componentBytes'],'sourceSha256':row['sourceSha256'],'binaryImportCheck':binary,'recordedWitSha256':hashlib.sha256(row['emittedWit'].encode()).hexdigest()})
assert [call['calls'] for call in r['calls']] == [1,2,3]
main_calls = r['calls']+[cli_observation(r['mainHost'])]
assert main_calls[-1]['calls'] == 1
for call in main_calls:
    assert call['passed'] is True
    assert call['initialTrace'] == phases['esm-initial'] and call['exported'] == call['task'] == phases['task'] and call['job'] == phases['promise-job']
    assert call['observations'] == [True]*6
    for key,value in {'fifo':5000,'pendingCallbacks':4096,'argumentCalls':64,'noArgs':1,'recovered':1,'returnGetterReads':0,'queueOnlyCompleted':True,'snapshotCompleted':True,'engineResetExecuted':False,'classicInitialProved':False}.items():
        assert call[key] == value
classic = read(CANDIDATE/'classic-node-results.json')
assert r['classic']['oracle'] == classic
assert r['classic']['jco'] == cli_observation(r['classic']['wasmtime']) == classic['observed']
assert classic['observed']['trace'] == phases['task'] and classic['observed']['subsequentConfiguredClassicEvaluation'] is True
assert classic['observed']['firstStartupPriorityProved'] is False and classic['observed']['globalObjectProperties'] == [False]*3
assert r['initializer']['jco'] == cli_observation(r['initializer']['wasmtime']) == {'beforeContent':1,'ticks':1}
assert r['late']['jco'] == cli_observation(r['late']['wasmtime']) == {'trace':['getter','tick','job','job-tick'],'getters':1}
assert [row['name'] for row in r['initializationFailures']] == ['top-invalid','top-throw','top-rejection','late-throw','late-rejection']
for row in r['initializationFailures']:
    check_file(OUTPUT/(row['name']+'.source.mjs'),row['sourceSha256'],below=OUTPUT)
    assert isinstance(row['error'],str) and 'Failed to initialize component' in row['error']
    assert not (OUTPUT/(row['name']+'.component.wasm')).exists()
assert [row['name'] for row in r['pairedControls']] == ['handled-throw','handled-rejection','finite-checkpoint-budget']
for row in r['pairedControls']:
    assert row['jco'] == cli_observation(row['wasmtime']) == row['expected']
    assert row['componentSha256'] == artifacts[row['name']]['componentSha256']
assert r['pairedControls'][-1]['expected'] == {'callbacks':65536}
assert [row['name'] for row in r['runtimeFailures']] == ['deployed-throw','deployed-rejection','checkpoint-work-limit']
for row in r['runtimeFailures']:
    assert row['boundaryFailureObserved'] is True and row['originalCauseIdentityAvailable'] is False
    assert row['componentSha256'] == artifacts[row['name']]['componentSha256']
    assert row['jco']['status'] == 0 and json.loads(row['jco']['stdout']) == row['jco']['observed']
    assert row['jco']['observed']['failed'] is True and row['jco']['observed']['reused'] is False
    assert row['wasmtime']['status'] != 0 and 'unreachable' in row['wasmtime']['stderr']
    assert any(control['name'] == row['pairedControl'] and control['pair'] == row['name'] for control in r['pairedControls'])
assert len(r['testOnlyPackagingVariant']) == 15 and len({row['name'] for row in r['testOnlyPackagingVariant']}) == 15
for row in r['testOnlyPackagingVariant']:
    assert row['calls'] == 1 and row['originalArgumentsUnchanged'] is True and row['methodRestored'] is True
    assert row['initializerAppended'] == (row['name'] == 'initializer')
    check_file(OUTPUT/(row['name']+'.initializer.original.js'),row['originalSha256'],below=OUTPUT)
    check_file(OUTPUT/(row['name']+'.initializer.actual.js'),row['amendedSha256'],below=OUTPUT)
    if not row['initializerAppended']:
        assert row['originalSha256'] == row['amendedSha256']
componentizer_root = Path(r['componentizer']['modulePath']).parent.parent
check_file(r['componentizer']['manifestPath'],r['componentizer']['manifestSha256'])
for row in r['componentizer']['checkedFiles']:
    check_file(componentizer_root/row['path'],row['sha256'],below=componentizer_root)
check_file(r['componentizer']['lock']['path'],r['componentizer']['lock']['sha256'])
check_file(r['host']['path'],r['host']['sha256'])
for suffix in ['stdout','stderr']:
    check_file(OUTPUT.parent/(OUTPUT.name+'.'+suffix+'.log'))
# Verify existing evidence did not change while the independent reader ran.
check_file(REPORT,report_sha)
for row in inputs:
    check_file(CANDIDATE/row['path'],row['sha256'],row['bytes'])
result = {'schemaVersion':1,'state':'INDEPENDENT_READ_ONLY_ORDINARY_RELEASE_DIAGNOSTIC_VERIFICATION_PASSED',
          'verifiedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'sourceReport':str(REPORT),'sourceReportSha256':report_sha,
          'engineSha256':ENGINE_SHA,'engineMetadataSha256':METADATA_SHA,'engineBytes':9764903,
          'gcStress':False,'oomTesting':False,'nativeSourcePartition':306,'diagnosticSourcePartition':2,
          'frozenCopiesRehashed':337,'inputFreezeSha256':INPUT_SHA,'testInputsRehashedBeforeAndAfterVerification':24,
          'runnerRecordsItsOwnInputPrePostVerification':True,
          'nativeDatabaseCompileCommands':61,'queueMemberCommands':1,'strictSubsetCommands':4,
          'parentTargetCommandsFromNinja':[1,1],'externalEmbeddingSources':3,
          'configAndParentCommandBeforeAfterBytesIdentical':True,
          'artifacts':artifact_checks,'successfulComponents':10,'zeroHostImportComponents':10,
          'retainedMainCalls':[1,2,3],'freshWasmtimeMainCall':1,'initializationFailures':5,
          'pairedSuccessfulControls':3,'freshBoundaryFailures':3,'finiteCheckpointControlCallbacks':65536,
          'verifiedFiles':list(verified.values()),'limitations':r['limitations']+[
              'Independent verification rehashed existing evidence and parsed outer import-section counts; it did not rerun a guest, compiler, packager, Node oracle, host version command or full component type validator.',
              'The driver records historical pre/post checks; this read verifies frozen code, report and current hashes without independently recreating that historical execution.',
              'Actual GC-stress flag is false: eight pending-entry hex calls and queue-only application ownership are ordinary Release observations, not forced-GC or exhaustive tracing proof.',
              'Latest accepted checkpoint remains v11; diagnostic release success does not admit public process/ALS, establish Engine reset, first-startup classic order, hidden fatal cause, or post-fatal reuse.'
          ],'guestCompilerPackagerOrNodeExecutionByVerifier':False,'liveOrFrozenInputsModified':False}
with (HERE/'results.json').open('x') as stream:
    json.dump(result,stream,indent=2)
    stream.write('\n')
index = {'state':'FROZEN_INDEPENDENT_READ_ONLY_ORDINARY_RELEASE_VERIFICATION',
         'files':[{'path':name,'sha256':sha(HERE/name),'bytes':(HERE/name).stat().st_size} for name in ['verify.py','results.json','verification-attempt-1.json','README.md']]}
with (HERE/'index.json').open('x') as stream:
    json.dump(index,stream,indent=2)
    stream.write('\n')
print(json.dumps({'state':result['state'],'resultSha256':sha(HERE/'results.json'),'indexSha256':sha(HERE/'index.json'),'verifiedFiles':len(verified),'components':10,'gcStress':False}))
