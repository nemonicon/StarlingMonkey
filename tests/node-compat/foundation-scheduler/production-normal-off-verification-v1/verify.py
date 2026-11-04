"""Independent read-only production artifact verification; execute no Wasm.

The separately recorded host Node source-admission invocation uses the pinned
live helper with the frozen metadata/source root. This reader imports no tool
freezer/preflight and performs no native build, package or guest operation.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shlex

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ROOT = Path('/tmp/starling-node-compat/production-scheduler-artifacts-v1/native-freeze')
BUILD = ROOT.parent/'builds/normal-off'
EXEC = REPO/'tests/node-compat/foundation-scheduler/production-execution-v1'
ENGINE = '6e5bc2ca3b3e3f7dccaa887003bc292e8a7abfbc5260691d1cda0114640dae84'
METADATA = 'f91625a5b3260fcd68ca60aa932019063692aa1e8ce86945ae022c8eba157150'
FREEZE = '86b5d78c81e97b33389302fe296e589863850bcc3aa60ce7f4ac5e52a2d33d7a'
RECIPE = '869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173'
POLICY = '98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0'
ADAPTER = '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
NODE = Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
verified = {}


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024),b''):
            value.update(chunk)
    return value.hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def checked(path, digest=None, size=None, frozen=False):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(),path
    if frozen:
        path.relative_to(ROOT)
        cursor = path
        while cursor != ROOT.parent:
            assert not cursor.is_symlink(),cursor
            cursor = cursor.parent
    value = sha(path)
    assert digest is None or value == digest,path
    assert size is None or path.stat().st_size == size,path
    verified[str(path)] = dict(path=str(path),sha256=value,bytes=path.stat().st_size)
    return value


def inventory(rows,count):
    assert len(rows) == count and len({row['path'] for row in rows}) == count
    for row in rows:
        assert set(row) == {'path','sha256'}
        assert row['path'] and not Path(row['path']).is_absolute()
        assert all(part not in ['','.','..'] for part in row['path'].split('/'))
        assert re.fullmatch('[0-9a-f]{64}',row['sha256'])
    return {row['path']:row['sha256'] for row in rows}


engine_path = ROOT/'normal-off.engine.wasm'
metadata_path = ROOT/'normal-off.engine.wasm.build.json'
freeze_path = ROOT/'normal-off-freeze-receipt.json'
checked(engine_path,ENGINE,9759293,True)
assert engine_path.open('rb').read(8) == bytes.fromhex('0061736d01000000')
checked(metadata_path,METADATA,frozen=True)
checked(freeze_path,FREEZE,frozen=True)
m,f = read(metadata_path),read(freeze_path)
assert m['engineSha256'] == f['engineSha256'] == ENGINE
assert m['engineBytes'] == f['engineBytes'] == 9759293
assert f['receiptSha256'] == METADATA and f['recipeSha256'] == RECIPE
assert f['schema'] == 1 and f['state'] == 'immutable-release-engine-frozen'
assert f['label'] == 'normal-off' and f['gcStress'] is False and f['entropyPolicy'] == 'off'
assert f['nativeInputsVerified'] == 306 and f['externalEmbeddingInputsVerified'] == 3
assert f['actualLayoutCompileCommands'] == 61 and f['actualStrictCompileCommands'] == 4
assert f['actualEmbeddingCompileCommands'] == 1
assert len(f['copies']) == len({row['path'] for row in f['copies']}) == 335
copies = {row['path']:row for row in f['copies']}
for row in f['copies']:
    checked(row['path'],row['sha256'],row['bytes'],True)
assert m.get('diagnosticOnly',False) is False and 'internalTickDiagnosticPolicy' not in m
assert m.get('syntheticMetadataOnly',False) is False
assert m['buildRecipeSha256'] == RECIPE and m['gcStress'] is False and m['entropyPolicy'] == 'off'
assert m['internalTicksEnabled'] is True and m['strictInitialization'] is True
for key in ['profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','abiFixEnabled','bigIntFixEnabled','sourceInputsCapturedBeforeBuild','componentizeSourcesCapturedBeforeBuild','buildRecipeCheckedBeforeAndAfterBuild']:
    assert m[key] is True,key
for key in ['oomTesting','debuggerEnabled','wptSupportEnabled']:
    assert m[key] is False,key
assert m['hostApi'] == 'wasi-0.2.10'
assert m['internalTickPolicy']['version'] == 'sm-private-ticks-source-v1'
assert m['internalTickPolicy']['resetSafeReuse'].startswith('OPEN')
assert m['internalTickPolicy']['publicProcessModule'] is False
assert m['strictEventExceptionPolicy']['version'] == 'sm-uncaught-event-v3-protected-abort-v2-private-ticks-v1'
assert m['protectedAbortListenerPolicy']['version'] == 'sm-protected-abort-listener-v2-private-ticks-source-v1'

native = inventory(m['sourceManifest'],306)
checked(ROOT/'source-policy.json',POLICY,frozen=True)
policy = read(ROOT/'source-policy.json')
assert native == inventory(policy['expectedNativeSourceManifest'],306)
for path,digest in native.items():
    frozen = ROOT/'source'/path
    assert copies[str(frozen)]['sha256'] == digest
    checked(frozen,digest,frozen=True)
external = inventory(m['componentizeSourceManifest'],3)
assert external == {'embedding/embedding.cpp':'9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205',
                    'embedding/embedding.h':'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e',
                    'CMakeLists.txt':'4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8'}
for path,digest in external.items():
    checked(ROOT/'componentize-source'/path,digest,frozen=True)
checked(ROOT/'build-engine.sh',RECIPE,frozen=True)
checked(ROOT/'source-policy-helper.py','78521feeefe299360228e5db76bfde0b11e6eeee93bd2374cd39b2fe695b610c',frozen=True)

# Configuration and command evidence are read ONLY from frozen label copies.
cache_path = ROOT/'normal-off-CMakeCache.txt'
db_path = ROOT/'normal-off-compile_commands.json'
checked(cache_path,m['cmakeCacheSha256'],frozen=True)
checked(db_path,m['compileCommandsSha256'],frozen=True)
cache = {}
for line in cache_path.read_text().splitlines():
    key,colon,tail = line.partition(':')
    if colon and '=' in tail:
        cache[key] = tail.partition('=')[2]
assert m['requestedCMakeOptions'] == m['observedCMakeOptions']
for key,value in m['requestedCMakeOptions'].items():
    assert cache[key] == value,key
for key,value in {'CMAKE_BUILD_TYPE':'Release','WEVAL':'OFF','USE_WASM_OPT':'ON','NODE_COMPAT_LOCKED_RUST':'ON','NODE_COMPAT_INTERNAL_TICKS':'ON','NODE_COMPAT_GC_STRESS':'OFF','NODE_COMPAT_ENTROPY_MODE':'OFF','NODE_COMPAT_OOM_TESTING':'OFF'}.items():
    assert cache[key] == value,key
assert not cache.get('CMAKE_PROJECT_ComponentizeJS_INCLUDE','')
assert cache.get('ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS','OFF') == 'OFF'
assert '--threads=1' not in cache.get('CMAKE_EXE_LINKER_FLAGS','')
database = read(db_path)
cpp = {str(REPO/path) for path in native if path.endswith('.cpp') and path.startswith(('builtins/','runtime/'))}
assert len(cpp) == 61
rows = [row for row in database if row['file'] in cpp]
assert len(rows) == len({row['file'] for row in rows}) == 61
layout = [row['command'] for row in rows]
assert layout == m['internalTickPolicy']['actualLayoutCompileCommands'] == m['protectedAbortListenerPolicy']['actualLayoutCompileCommands']
queue = [row['command'] for row in rows if row['file'].endswith('/runtime/node_tick_queue.cpp')]
assert len(queue) == 1 and queue == m['internalTickPolicy']['actualQueueCompileCommands']
strict_paths = ['/runtime/engine.cpp','/runtime/event_loop.cpp','/runtime/node_tick_queue.cpp','/builtins/web/event/event-target.cpp']
strict = [row['command'] for row in rows if any(row['file'].endswith(path) for path in strict_paths)]
assert len(strict) == 4 and sorted(strict) == sorted(m['strictEventExceptionPolicy']['actualNativeCompileCommands'])
ev = f['postBuildEmbeddingEvidence']
assert ev['version'] == 'production-after-build-parent-ninja-v1' and ev['beforeBuildCaptureExists'] is False
assert ev['exitCode'] == 0 and ev['stderr'] == ''
assert ev['command'] == ['ninja','-C',str(Path(m['cmakeCachePath']).parent),'-t','commands','builtin_componentize_embedding']
checked(ev['path'],ev['sha256'],ev['bytes'],True)
assert ev['path'] == str(ROOT/'normal-off-embedding.after.commands.txt')
embedding = []
for line in Path(ev['path']).read_text().splitlines():
    args = shlex.split(line)
    if args.count('-c') == 1 and args[args.index('-c')+1] == ev['sourcePath']:
        embedding.append(line)
assert len(embedding) == 1 and embedding == ev['compileCommands'] == m['actualEmbeddingCompileCommands']
assert embedding == m['internalTickPolicy']['actualEmbeddingCompileCommands'] == m['protectedAbortListenerPolicy']['actualEmbeddingCompileCommands']
assert not any(row['file'] == ev['sourcePath'] for row in database)
for command in layout+embedding:
    args = shlex.split(command)
    assert args.count('-c') == 1 and '-O3' in args and '-DNDEBUG' in args
    assert '-fsyntax-only' not in args and not any(arg.startswith('-DDEBUG') for arg in args)
    for macro in ['NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER','NODE_COMPAT_ENTROPY_POLICY']:
        assert [arg for arg in args if arg == '-D'+macro or arg.startswith('-D'+macro+'=')] == ['-D'+macro+'=1']
    assert not any(arg.startswith('-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY') or arg.startswith('-DNODE_COMPAT_GC_STRESS') or arg.startswith('-DNODE_COMPAT_OOM_TESTING') for arg in args)

rust = m['generatedRustProject']
assert rust['cargoBuildLocked'] is True and rust['manifestAndLockCheckedBeforeAndAfterBuild'] is True
checked(ROOT/'normal-off-Cargo.toml',rust['manifestSha256'],frozen=True)
checked(ROOT/'normal-off-Cargo.lock',rust['lockSha256'],frozen=True)
assert native['runtime/crates/staticlib-template/Cargo.lock'] == rust['lockSha256'] == rust['versionedLockSha256']
assert rust['actualCargoBuildCommands'] and all('--release --locked' in command for command in rust['actualCargoBuildCommands'])
audit = m['openssl']['completeSourceAudit']
assert audit['beforeAndAfterBuild'] is True and audit['sourceFilesVerified'] == 4650
checked(ROOT/'normal-off-openssl-before.json',audit['beforeReportSha256'],frozen=True)
before = read(ROOT/'normal-off-openssl-before.json')
assert before['state'] == 'verified-complete-source' and before['unexpectedFiles'] == before['missingFiles'] == []
for key,value in before.items():
    assert audit[key] == value,key
for name,digest in [('receipt.txt',m['openssl']['receiptSha256']),('configure.txt',m['openssl']['configureRecipe']['sha256']),('configdata.pm',m['openssl']['configdata']['sha256'])]:
    checked(ROOT/('normal-off-openssl-'+name),digest,frozen=True)
assert f['dependencyReferences'] == [{'kind':'linked-libcrypto-not-copied',**m['openssl']['library']}]
for row in f['licenses']:
    checked(ROOT/'source'/row['path'],row['sha256'],frozen=True)
assert len(f['licenses']) == 7
assert native['host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'] == ADAPTER
checked(ROOT/'tooling/wasi_snapshot_preview1.wasm',ADAPTER,53512,True)
checked(REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm',ADAPTER,53512)
assert f['toolingInputs'][0]['additionalNativeInput'] is False and f['toolingInputs'][0]['doesNotReplaceLiveRuntimeSeal'] is True

tool_hashes = {'freeze-engine.py':'05beb8f30ff0869d012f22847db0ea379c51ed843b19104aa8346b7c6f69d246',
               'artifact_common.py':'fafc84a81f4e2c450a6f1b2224516f513074ba62a0ffe2cd7af2d78a8f1f15f0',
               'metadata-admission.mjs':'c6e742218c400aff7dbd54c923949a743272e04a36c74e2583e32a34cdd569e8'}
for name,digest in tool_hashes.items():
    checked(ROOT/'artifact-tools'/name,digest,frozen=True)
    checked(REPO/'tests/node-compat/foundation-scheduler/production-artifacts-v1'/name,digest)
assert f['allInputsValidatedBeforeCopies'] is True and f['allCopiesAndOriginalsRehashed'] is True
assert f['guestExecutedByHelper'] is False

# Bind complete actual launcher/build and Root freezer provenance, without
# dereferencing any mutable original normal configuration path from metadata.
native_result = read(EXEC/'normal-off-native-results.json')
assert native_result['rawNativeExitCode'] == native_result['launcherToolExitCode'] == 0
assert native_result['engineSha256'] == ENGINE and native_result['metadataSha256'] == METADATA
launcher_path = BUILD/'result.json'
checked(launcher_path,native_result['launcherResultSha256'])
launch = read(launcher_path)
assert launch['rawChildExitCode'] == launch['status'] == launch['launcherExitCode'] == 0
assert launch['state'] == 'native-build-completed-runtime-pending'
assert launch['lifecycleComplete'] is True and launch['evidenceComplete'] is True
assert launch['launcherErrors'] == [] and launch['ownedGroupCleanup']['complete'] is True
assert launch['recipeSha256'] == RECIPE and launch['label'] == 'normal-off'
assert launch['explicitEnvironment']['NODE_COMPAT_GC_STRESS'] == '0' and launch['explicitEnvironment']['NODE_COMPAT_ENTROPY_MODE'] == 'OFF'
assert all(launch['explicitEnvironment'][key] == '1' for key in ['NODE_COMPAT_JOBS','BINARYEN_CORES','RAYON_NUM_THREADS','CARGO_BUILD_JOBS'])
checked(BUILD/'build.log',launch['logSha256'])
assert '[107/107]' in (BUILD/'build.log').read_text()
for name in ['normal-off-native-results.json','normal-off-freeze-results.json','launcher-root-review.json']:
    checked(EXEC/name)
assert read(EXEC/'normal-off-freeze-results.json')['freezeReceiptSha256'] == FREEZE
for name,digest in [('normal-off-build.log',launch['logSha256']),('normal-off-engine.build.json',METADATA),('normal-off-freeze-receipt.json',FREEZE),('normal-off-result.json',native_result['launcherResultSha256'])]:
    checked(EXEC/name,digest)
checked(EXEC/'normal-off-launch.json')
assert read(EXEC/'normal-off-launch.json') == read(BUILD/'launch.json')
checked(BUILD/'launch.json')
checked(EXEC/'normal-off-freeze.stderr.txt',hashlib.sha256(b'').hexdigest(),0)
checked(EXEC/'normal-off-freeze.stdout.json')
assert read(EXEC/'normal-off-freeze.stdout.json') == {'receiptPath':str(freeze_path),'receipt':f}

recorded_source_admission = read(ROOT/'normal-off-source-admission.json')
assert recorded_source_admission['state'] == 'ACTUAL_FINITE_SOURCE_SELECTOR_PASSED_NO_ENGINE_EXECUTION'
assert recorded_source_admission['sourceFiles'] == 306 and recorded_source_admission['selectedManifestCount'] == 8
assert recorded_source_admission['coreExpectations']['sourceHashes'] == f['coreSources']
for path,key in [('tests/node-compat/module-selection.mjs','selectorSourceSha256'),('tests/node-compat/private-ticks-admission.mjs','admissionSourceSha256')]:
    checked(REPO/path,recorded_source_admission[key])
checked(NODE,'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
checked(HERE/'selector.stdout.json')
checked(HERE/'selector.stderr.txt',hashlib.sha256(b'').hexdigest(),0)
host = read(HERE/'selector.stdout.json')
assert host['state'] == recorded_source_admission['state']
assert host['options'] == {'gcStress':False,'entropyPolicy':'off'}
assert host['sourceRoot'] == str(ROOT/'source')
assert host['sourceFiles'] == 306 and host['selectedManifestCount'] == 8
assert host['coreExpectations'] == recorded_source_admission['coreExpectations']
assert host['engineBytesRead'] is False and host['guestExecuted'] is False
assert host['policySha256'] == POLICY
pins = {}
for name in ['production-regression-candidate-v4','production-followon-capability-v2']:
    path = REPO/'tests/node-compat/foundation-scheduler'/name/'pins.json'
    checked(path)
    document = read(path)
    assert document['state'] == 'UNCONFIGURED_ACTUAL_PRODUCTION_FREEZES_REQUIRED'
    assert all(value is None for value in document['variants'].values())
    pins[name] = document['state']

# Final hash sweep covers every original read path in this verifier, not mutable
# original build configuration paths. Writes occur only in this new packet.
for row in list(verified.values()):
    checked(row['path'],row['sha256'],row['bytes'])
result = dict(schemaVersion=1,state='INDEPENDENT_READ_ONLY_PRODUCTION_NORMAL_OFF_ARTIFACT_VERIFICATION_PASSED',
    verifiedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),engineSha256=ENGINE,engineMetadataSha256=METADATA,
    engineBytes=9759293,freezeReceiptSha256=FREEZE,frozenCopiesRehashed=335,nativeSourceInputs=306,externalEmbeddingInputs=3,
    nativeCommands=61,strictCommands=4,queueCommands=1,separateEmbeddingCommands=1,
    postBuildEmbeddingRawSha256=ev['sha256'],beforeBuildEmbeddingCaptureExists=False,
    gcStress=False,entropyPolicy='off',diagnosticEngine=False,coreVersion=f['coreVersion'],
    selectedManifests=8,actualFiniteSelectorExecutedAsHostJavaScript=True,engineOrWasmExecutedBySelector=False,
    immutableLabelConfigurationUsed=True,originalNormalCacheOrCompileDatabaseRead=False,
    liveAndToolingAdapterSha256=ADAPTER,lockedRustEvidenceVerified=True,opensslFrozenEvidenceFiles=4,
    opensslCompleteSourceAuditCountRecorded=4650,independentOpenSsl4650SourceReauditPerformed=False,
    linkedLibcryptoReference=f['dependencyReferences'][0],linkedLibcryptoOriginalReadByVerifier=False,
    licensesVerified=7,consumerPinStates=pins,reviewedPinsCreated=False,
    verifiedFiles=list(verified.values()),limitations=[
        'This is actual production engine/config/source provenance, not guest/component/Node compatibility acceptance.',
        'The only executed operation was pinned host Node metadata/source admission against frozen metadata/source with the exact original live helper; no engine, Wasm, compiler, linker, package or host runtime was executed.',
        'Frozen artifact-tools files are byte evidence, not relocatable runnable modules; their relative imports intentionally require the original sealed source location.',
        'OpenSSL four-file frozen evidence and recorded4650-source audit are bound; this verifier does not repeat the full source/archive audit or read the original referenced libcrypto archive.',
        'Original sidecars retain historical mutable build paths. This verifier never opens original normal CMakeCache/compile_commands paths or reruns Ninja.',
        'Only after-build parent Ninja evidence exists for production recipe869; no before capture is fabricated.',
        'Actual reviewed pins, fresh full release/focused/GC/HTTP gates and explicit activation are still required. No reset/ALS/request cleanup, public process, memory or performance claim follows.'
    ],nativeGuestRepackOrNinjaExecutedByVerifier=False,liveOrFrozenInputsModified=False,productionCompatibilityAcceptanceClaimed=False)
with (HERE/'results.json').open('x') as stream:
    json.dump(result,stream,indent=2);stream.write('\n')
names = ['verify.py','README.md','selector-command.json','selector.stdout.json','selector.stderr.txt','results.json']
index = dict(state='FROZEN_INDEPENDENT_READ_ONLY_PRODUCTION_NORMAL_OFF_VERIFICATION',files=[dict(path=name,sha256=sha(HERE/name),bytes=(HERE/name).stat().st_size) for name in names])
with (HERE/'index.json').open('x') as stream:
    json.dump(index,stream,indent=2);stream.write('\n')
print(json.dumps(dict(state=result['state'],resultSha256=sha(HERE/'results.json'),indexSha256=sha(HERE/'index.json'),verifiedPaths=len(verified))))
