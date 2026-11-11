"""Closed-output DATA collector only: no tool, compiler or host invocation."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shlex
import sys
import traceback

if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
    raise RuntimeError('requires unoptimized Python -I -B before input IO')

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent / 'clone-cancel-native-build-v1'
WORK = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first')
OUT = WORK / 'closed-collection-v2'
OWNER = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/commands/native-build-v2')
DRIVER = {'path': str(BUILD / 'run-build.py'), 'sha256': '1cad0ccb6ffd3a5fe55f243b0c3728957e282970503f88287c8d8b59e870f3de', 'bytes': 40260}
SELECTION = {'path': str(BUILD / 'build-selection.json'), 'sha256': 'cc807f6ea77a7ac951114d11ec03c952ad6cdffcdfc9d79192a48a23c41c8bcc', 'bytes': 21843}
ORIGINAL_RESULT = {'path': str(WORK / 'result.json'), 'sha256': '54291d8dd9b7b8ed954ef996e7dbdf2e75cf46c81c70adb6516e523e42bfed7c', 'bytes': 2092519}
ORIGINAL_METADATA = {'path': str(WORK / 'metadata.json'), 'sha256': '779bd077b36a94f62091a30ec4018c008dd91b80437f1445a36632867d24f34f', 'bytes': 1158971}
OUTER_TERMINAL = {'path': str(OWNER / 'terminal.json'), 'sha256': '59f4407118302c3f57c229ab872579dc01798b635883b08af0a74aa8333974e0', 'bytes': 269166}
OUTER_COLLECTION = {'path': str(OWNER / 'collection.json'), 'sha256': '6bfcc4f6df20a7a2225b428a3d2706f08f3e4697549f652302ac49bb8f754028', 'bytes': 707}
OUTER_STARTED = {'path': str(OWNER / 'started.json'), 'sha256': 'f1407e67c1ace2d1dfbd4aa310a1abf5ed783975075c670619b30b20e14d7de2', 'bytes': 625}
OUTER_REQUEST = {'path': str(OWNER / 'request.json'), 'sha256': 'f0aed41dac9c611a2bee76b8eb8536ddff881b3d885f43fea2514a70e6335a72', 'bytes': 3224}
EMPTY = hashlib.sha256(b'').hexdigest()
GENERATED_REVIEW = {'path': str(HERE.parent / 'next-clone-cancel-native-root-results-v1/generated-tu-source-data-review.json'), 'sha256': '4f91d134d91a3d2cabe109ef9817bdd052e04f9c79646388677310aad41d9043', 'bytes': 9065}
CORE_VALIDATION = {'path': '/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/commands/validate-built-core/terminal.json', 'sha256': 'd2bcc02b0a0b712f9ef5b11ef3b6dbedd4296a93f00141b97fd0f694e95d89e6', 'bytes': 1527}
NULL_CPP = {'path': str(WORK / 'build/starling-raw.wasm/null.cpp'), 'sha256': EMPTY, 'bytes': 0}
NULL_WRITER = {'path': str(WORK / 'native-source/cmake/spidermonkey.cmake'), 'sha256': 'af02f2af5ac9d5ceeb6e6e1b63ff433f33377b52d1ec1719732f008c12ad2da7', 'bytes': 8409}
NULL_CONSUMER = {'path': str(WORK / 'native-source/cmake/build-crates.cmake'), 'sha256': '3cbf3f9f080345694c40bc329bbc56b553b137d6291eaf745213c285e5a50dab', 'bytes': 5761}
INPUTS = {}


def descriptor(path):
    p = Path(path)
    assert p.resolve(strict=True) == p and p.is_file()
    before = p.stat()
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    after = p.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(p), sha256=h.hexdigest(), bytes=after.st_size)


def checked(ref):
    assert descriptor(ref['path']) == {k: ref[k] for k in ('path', 'sha256', 'bytes')}
    INPUTS[ref['path']] = {k: ref[k] for k in ('path', 'sha256', 'bytes')}
    return Path(ref['path'])


def read(ref):
    assert ref['bytes'] <= 32 * 1024 * 1024
    return json.loads(checked(ref).read_bytes())


def module(ref, name):
    spec = importlib.util.spec_from_file_location(name, checked(ref))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def generated_translation_unit(compile_rows, rows):
    recipe = {x['target']['path'] for x in rows if x['role'] == 'native'}
    native_rows = [r for r in compile_rows if r['file'] in recipe]
    generated = [r for r in compile_rows if r['file'] not in recipe]
    assert len(compile_rows) == 80 and len(native_rows) == 79 and len(generated) == 1
    assert generated[0]['file'] == NULL_CPP['path']
    assert generated[0]['directory'] == str(WORK / 'build')
    assert generated[0]['output'] == str(WORK / 'build/starling-raw.wasm/CMakeFiles/rust-crates.dir/null.cpp.obj')
    argv = generated[0].get('arguments') or shlex.split(generated[0]['command'])
    assert argv.count('-c') == argv.count('-o') == 1
    assert argv[argv.index('-c') + 1] == NULL_CPP['path']
    assert argv[argv.index('-o') + 1] == 'starling-raw.wasm/CMakeFiles/rust-crates.dir/null.cpp.obj'
    checked(NULL_CPP)
    assert NULL_WRITER in [r['target'] for r in rows if r['role'] == 'native']
    assert NULL_CONSUMER in [r['target'] for r in rows if r['role'] == 'native']
    writer = checked(NULL_WRITER).read_text().splitlines()
    consumer = checked(NULL_CONSUMER).read_text().splitlines()
    assert writer[46].strip() == 'file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/null.cpp "")'
    assert consumer[85].strip() == 'add_library(rust-crates STATIC ${CMAKE_CURRENT_BINARY_DIR}/null.cpp)'
    return dict(source=NULL_CPP, compileRow=generated[0], writer=NULL_WRITER, writerLine=47,
                consumer=NULL_CONSUMER, consumerLine=86, emptyContentVerified=True,
                noOtherUnmappedTranslationUnitAllowed=True)


def configured(m):
    # The original read-only complete configured-TOML/lock validation is retained.
    return ORIGINAL_DRIVER_MODULE.configured(m)


def protect(driver, d, snapshots):
    for ref in list(INPUTS.values()) + list(driver.INPUTS.values()):
        checked(ref)
    for role, before in snapshots.items():
        assert d.tree_snapshot(before['root']) == before, 'selected immutable tree changed: ' + role


def phase_closure(driver, d, original):
    assert [r['label'] for r in original['phases']] == ['rust-version', 'cargo-version', 'rust-sysroot', 'configure', 'build', 'ninja-commands']
    for row in original['phases']:
        assert d.phase_succeeded(row)
        terminal = read(row['outerTerminal'])
        assert driver.clean_terminal(terminal)
        checked(terminal['stdout'])
        checked(terminal['stderr'])
        worker = read(row['workerResult'])
        assert worker['rawChildExitCode'] == 0 and worker['lifecycleComplete'] is True
        assert worker['launcherErrors'] == [] and worker['stoppedForDiskSpace'] is False
        assert worker.get('sigtermReceived') is not True and worker.get('stopReason') is None
        group = worker['ownedGroupCleanup']
        assert group['complete'] is True and group['events'] == group['errors'] == []
        checked(worker['rawCombinedLog'])


def cargo_closure(driver, original, s, m):
    review = read(original['cargoMetadataReview'])
    assert review == original['freshCargoAdmission'] and review['passed'] is True
    record = review['command']
    assert driver.clean_terminal(read(record['terminal'])) and record['clean'] is True
    checked(record['stderr'])
    data = read(record['stdout'])
    assert data['version'] == 1 and data['workspace_root'] == str(WORK / 'cargo-project')
    assert data['target_directory'] == str(WORK / 'rust-target')
    packages = data['packages']
    ids = {p['id'] for p in packages}
    assert packages and len(ids) == len(packages) and {n['id'] for n in data['resolve']['nodes']} == ids
    assert all(x in ids for n in data['resolve']['nodes'] for x in n['dependencies'])
    allowed = [WORK / 'cargo-project', WORK / 'native-source', Path(s['reusedTrees']['intl-firefox']['root']), Path(s['reusedTrees']['intl-vendor']['root'])]
    for package in packages:
        p = Path(package['manifest_path'])
        assert p.resolve(strict=True) == p and p.is_file() and any(root in p.parents for root in allowed)
    roots = [p for p in packages if p['manifest_path'] == m['cargo']['manifest']['path']]
    assert len(roots) == 1 and data['resolve']['root'] == roots[0]['id']
    assert {p['name'] for p in roots[0]['dependencies']} == {'rust-encoding', 'rust-hooks', 'rust-url', 'multipart', 'icu_capi', 'unicode-bidi-ffi'}
    assert review['sourceMaterialization'] == s['sourceMaterialization']
    return review


# Same actual derivation as the frozen original, with explicit generated-TU
# classification, new collection kind and original native-recipe provenance.
def actual_metadata(s, d, m, old, rows, manifests, trees, result):
    # All 52 values are derived for this run. Legacy capsule/authority slots are
    # explicitly absent, not populated with old receipts or invented admissions.
    native = [r for r in rows if r['role'] == 'native']
    support = [r for r in rows if r['role'] == 'support']
    embedding = [r for r in rows if r['role'] == 'embedding']
    native_manifest = [dict(path=r['relativePath'], sha256=r['target']['sha256'], bytes=r['target']['bytes']) for r in native]
    support_manifest = [dict(relativePath=r['relativePath'], mode=r['mode'], source=r['target']) for r in support]
    embedding_manifest = [dict(relativePath=r['relativePath'], mode=r['mode'], source=r['target']) for r in embedding]
    after = [descriptor(r['target']['path']) for r in native if Path(r['target']['path']).exists()]
    cache = WORK / 'build/CMakeCache.txt'
    database = WORK / 'build/compile_commands.json'
    observed = d.cache_values(cache)
    compile_rows = json.loads(database.read_bytes()) if database.exists() else None
    artifact = WORK / 'componentize-source/lib/starlingmonkey_embedding.wasm'
    result['engineCandidate'] = descriptor(artifact) if artifact.exists() else None
    result['linkInputs'] = [descriptor(p) for p in sorted((WORK / 'build').rglob('*')) if p.is_file() and (p.suffix in ('.a', '.o', '.obj', '.rsp') or p.name in ('Cargo.toml', 'Cargo.lock', 'rust-staticlib.rs'))]
    embedding_rows = None
    if result.get('wholeNinjaCommands'):
        text = checked(result['wholeNinjaCommands']).read_text()
        embedding_rows = [line for line in text.splitlines() if ' -c ' + str(WORK / 'componentize-source/embedding/embedding.cpp') in line]
    if result.get('buildCommandSucceeded'):
        try:
            with artifact.open('rb') as f:
                assert f.read(8) == b'\x00asm\x01\x00\x00\x00'
            assert len(compile_rows) == len({r['file'] for r in compile_rows}) == 80
            generated_unit = generated_translation_unit(compile_rows, rows)
            assert all(observed.get(k, {}).get('value') == v for k, v in s['cmakeFlags'].items())
            assert len(embedding_rows) == 1
            macro = 'NODE_COMPAT_NATIVE_EXPORT_DIAGNOSTIC_V1'
            definition = '-D' + macro + '=1'
            assert observed[macro] == dict(type='BOOL', value='ON') and s['cmakeFlags'][macro] == 'ON'
            assert [t for t in shlex.split(embedding_rows[0]) if macro in t] == [definition]
            assert not any(macro in t for r in compile_rows for t in (r['arguments'] if 'arguments' in r else shlex.split(r['command'])))
            assert observed.get('Rust_TOOLCHAIN_IS_RUSTUP_MANAGED', {}).get('value') not in ('TRUE', 'ON', '1')
            assert after == [r['target'] for r in native]
            result['configuredRust'] = configured(m)
            result['nativeExportDiagnosticCompileEvidence'] = dict(option=macro, requested='ON', observed=observed[macro], embeddingDefinition=definition, embeddingDefinitionOccurrences=1, separateEmbeddingCommands=1, nativeCompileRows=80, nativeRowsWithDiagnosticDefinition=0, compiledSourceAfterimagesAuthenticated=True, totalCompileRows=80, nativeRecipeCompileRows=79, generatedCompileRows=1, generatedTranslationUnits=[generated_unit])
        except BaseException as error:
            result['postCollectionErrors'].append(dict(type=type(error).__name__, message=str(error), stack=traceback.format_exc()))
    sdk = Path(s['reusedTrees']['spidermonkey']['root'])
    metadata = dict(schemaVersion=1, metadataKind='CLONE_CANCEL_NATIVE_BUILD_CLOSED_OUTPUT_COLLECTION_V2',
        sourceComposition=result.get('sourceComposition'), sourceRoot=str(WORK / 'native-source'),
        compiledSourceRoot=str(WORK / 'native-source'), compiledAfterInputs=after,
        compilerTools=s['hostTools'], actualRustTools=dict(cargo=s['cargo'], rustc=s['rustc']),
        nativePolicyInputCount=len(native), nativePolicyInputManifest=native_manifest,
        buildSupportInputCount=len(support), buildSupportInputManifest=support_manifest,
        embeddingInputCount=len(embedding), embeddingInputManifest=embedding_manifest,
        selectedModuleManifests=manifests, requestedCMake=s['cmakeFlags'], observedCMake=observed,
        compileDatabase=descriptor(database) if database.exists() else None, actualCompileRows=compile_rows,
        wholeNinjaCommands=result.get('wholeNinjaCommands'), actualSeparateEmbeddingCompileRows=embedding_rows,
        actualLibrary=descriptor(sdk / 'libspidermonkey.a'), actualSavedFrameHeader=descriptor(sdk / 'include/js/SavedFrameAPI.h'),
        actualConfigHeader=descriptor(sdk / 'include/js-config.h'), actualConfdefs=descriptor(sdk / 'include/js-confdefs.h'),
        patchedSpiderMonkeyEvidence=s['provenance']['historicalPatchedSpiderMonkeyProofRecovered'], savedFramePatchIndex=old.get('savedFramePatchIndex'),
        actualAggregateLock=m.get('cargo', {}).get('lock'), actualRustConfiguration=result.get('configuredRust'),
        offlineCargoConfig=m.get('cargo', {}).get('config'), validatedCargoAudit=result.get('cargoMetadataReview'),
        portableCargoSelection=None, portableCargoAdmission=result.get('freshCargoAdmission'),
        wrapperPython=s['wrapperPython'], buildToolPython=next(r['executable'] for r in s['hostTools'] if r['name'] == 'python3'),
        portableBuildAdmissionVersion=1, logicalCargoAuditDescriptorFromVerifiedCapsule=False,
        validatedCargoProofCapsule=None, validatedCargoProofIndex=None,
        toolTreeInputs=trees, initialTreeProtection=result.get('treeProtectionBefore'),
        originalExtractionWholeTreeAttestationClaimed=False, linkAndRustInputs=result['linkInputs'],
        engine=result.get('engineCandidate'), phases=result['phases'], recipe=DRIVER,
        rootAuthority=None, old83MetadataProjected=False, engineExecuted=False, guestExecuted=False, adoption=False,
        nativeExportDiagnosticCompileEvidence=result.get('nativeExportDiagnosticCompileEvidence'))
    assert len(metadata) == 52
    if old:
        assert set(metadata) == set(old)
    return metadata


def main():
    global ORIGINAL_DRIVER_MODULE
    assert len(sys.argv) == 1 and not os.path.lexists(OUT)
    driver = module(DRIVER, 'frozen_native_build_readonly_helpers')
    ORIGINAL_DRIVER_MODULE = driver
    d = driver.utility()
    s = read(SELECTION)
    driver.SELECTION_DOC = s
    assert s['workRoot'] == str(WORK)
    # The outer record is Root-owned publication. No build artifact is read
    # before its independently closed, clean ownership status is established.
    terminal = read(OUTER_TERMINAL)
    collection = read(OUTER_COLLECTION)
    started = read(OUTER_STARTED)
    request = read(OUTER_REQUEST)
    assert driver.terminal_quiescent(terminal) and terminal['rawExitCode'] == 1
    assert collection['terminal'] == OUTER_TERMINAL and collection['request'] == OUTER_REQUEST
    assert collection['rawExitCode'] == 1 and collection['clean'] is False
    assert collection['primaryError'] is collection['verificationError'] is None
    assert collection['inputsUnchanged'] is True and collection['collectionErrors'] == []
    assert started['pid'] == terminal['pid'] and started['timeoutSeconds'] == request['seconds'] == 7200
    assert started['authority'] == terminal['authority'] == OUTER_REQUEST
    assert started['argv'] == request['argv'] == [s['wrapperPython']['path'], '-I', '-B', DRIVER['path']]
    assert DRIVER in request['protectedInputs'] and SELECTION in request['protectedInputs']
    for ref in request['protectedInputs']:
        checked(ref)
    checked(terminal['stdout'])
    checked(terminal['stderr'])
    original = read(ORIGINAL_RESULT)
    original_metadata = read(ORIGINAL_METADATA)
    assert original['state'] == 'CLONE_CANCEL_NATIVE_BUILD_FAILED_UNACCEPTED_V1' and original['passed'] is False
    assert original['buildCommandSucceeded'] is True and original['primaryError'] is None
    assert original['ownerQuiescenceKnown'] is True and original['selection'] == SELECTION
    assert original['inputProtection']['unchanged'] is True and original['inputProtection']['errors'] == []
    assert original['inputProtection']['wholeTrees'] == 11
    errors = original['postCollectionErrors']
    assert len(errors) == 1 and errors[0]['type'] == 'AssertionError' and errors[0]['message'] == ''
    failed_expression = "assert all(r['file'] in {x['target']['path'] for x in rows} for r in compile_rows)"
    assert failed_expression in errors[0]['stack'] and 'line 431, in actual_metadata' in errors[0]['stack']
    assert original['metadata'] == ORIGINAL_METADATA and original_metadata['engine'] == original['engineCandidate']
    assert len(original_metadata) == 52 and original_metadata['nativeExportDiagnosticCompileEvidence'] is None
    assert original_metadata['phases'] == original['phases']
    phase_closure(driver, d, original)
    core_terminal = read(CORE_VALIDATION)
    assert driver.clean_terminal(core_terminal)
    core_started = read(descriptor(Path(CORE_VALIDATION['path']).parent / 'started.json'))
    assert core_started['argv'][-2:] == ['validate', original_metadata['engine']['path']]
    checked(core_terminal['stdout'])
    checked(core_terminal['stderr'])
    selected = read(s['predecessorMetadata'])
    m = read(s['sourceMaterialization'])
    assert m['predecessorWholeMetadata'] == s['predecessorMetadata'] and m['inputsUnchanged'] is True
    rows = m['copies']
    assert len(rows) == len({r['target']['path'] for r in rows}) == 825
    assert {role: sum(r['role'] == role for r in rows) for role in ('native', 'support', 'embedding')} == dict(native=435, support=387, embedding=3)
    native = {r['path']: r for r in selected['nativePolicyInputManifest']}
    support = {r['relativePath']: r for r in selected['buildSupportInputManifest']}
    embedding = {r['relativePath']: r for r in selected['embeddingInputManifest']}
    for row in rows:
        checked(row['source'])
        checked(row['target'])
        assert row['destination'] == row['target']['path']
        assert all(row['source'][k] == row['target'][k] for k in ('sha256', 'bytes'))
        if row['role'] == 'native':
            old = native[row['relativePath']]
            if row['relativePath'] == 'builtins/web/fetch/request-response.cpp':
                assert old['sha256'] == '1fe296b8472f14e50556910227b184552e0a0ac424f97a0f170c4b91cfd35fa6'
                assert row['target']['sha256'] == '0431184d4562972c98538494caf46d2b11cdf0280f51d0e7143cd8534526442e'
            else:
                assert all(row['target'][k] == old[k] for k in ('sha256', 'bytes'))
        else:
            old = (support if row['role'] == 'support' else embedding)[row['relativePath']]
            assert row['source'] == old['source'] and row['mode'] == old['mode']
        assert (Path(row['target']['path']).stat().st_mode & 0o777) == row['mode']
    expected = {r['target']['path'] for r in rows} | {original_metadata['engine']['path']}
    actual = {str(p) for root in ('native-source', 'componentize-source') for p in (WORK / root).rglob('*') if p.is_file()}
    assert expected == actual and not any(p.is_symlink() for root in ('native-source', 'componentize-source') for p in (WORK / root).rglob('*'))
    driver.validate_generators(s['generatorResult'], m)
    cargo = cargo_closure(driver, original, s, m)
    snapshots = {}
    trees = original_metadata['toolTreeInputs']
    assert set(trees) == set(s['reusedTrees']) and len(trees) == 11
    for role, spec in trees.items():
        assert spec['root'] == s['reusedTrees'][role]['root']
        expected_tree = read(spec['inventory'])
        checked(spec['provenance'])
        current = d.tree_snapshot(spec['root'])
        assert current == expected_tree
        snapshots[role] = current
    public = [r['relativePath'] for r in selected['selectedModuleManifests']['public']]
    private = [r['relativePath'] for r in selected['selectedModuleManifests']['private']]
    manifests = d.selected_manifests(dict(selectedPublicManifests=public, selectedPrivateManifests=private), WORK / 'native-source')
    assert manifests == original_metadata['selectedModuleManifests']
    proof = read(GENERATED_REVIEW)
    assert proof['closedBuildResult'] == ORIGINAL_RESULT and proof['originalMetadata'] == ORIGINAL_METADATA
    assert proof['compilePartition']['total'] == 80 and proof['compilePartition']['authenticatedRecipeMembers'] == 79
    assert proof['compilePartition']['generatedMembers'] == 1 and proof['compilePartition']['otherMembers'] == 0
    allowed_paths = {'Rust_COMPILER': s['rustc']['path'], 'Rust_CARGO': s['cargo']['path'],
        'NODE_COMPAT_INTL_LOCKFILE': m['cargo']['lock']['path'], 'NODE_COMPAT_INTL_FIREFOX_SOURCE': s['reusedTrees']['intl-firefox']['root'],
        'CPM_OpenSSL_SOURCE': str(WORK / 'private-openssl/openssl-3.0.17')}
    allowed_paths.update({'CPM_' + role + '_SOURCE': s['reusedTrees'][role]['root'] for role in ('wasi-sdk', 'binaryen', 'wasm-tools', 'wasmtime', 'weval', 'corrosion')})
    assert s['cmakeFlags'] == {**selected['requestedCMake'], **allowed_paths}
    audit = dict(buildCommandSucceeded=True, phases=original['phases'], postCollectionErrors=[],
        sourceComposition=original['sourceComposition'], configuredRust=original['configuredRust'],
        cargoMetadataReview=original['cargoMetadataReview'], freshCargoAdmission=cargo,
        treeProtectionBefore=original['treeProtectionBefore'], wholeNinjaCommands=original['wholeNinjaCommands'])
    checked(audit['sourceComposition'])
    checked(audit['treeProtectionBefore'])
    generated_translation_unit(original_metadata['actualCompileRows'], rows)
    fresh = actual_metadata(s, d, m, selected, rows, manifests, trees, audit)
    assert set(fresh) == set(original_metadata) and len(fresh) == 52
    assert audit['postCollectionErrors'] == [], 'remaining actual metadata validation failed'
    changed_fields = [key for key in fresh if fresh[key] != original_metadata[key]]
    assert set(changed_fields) == {'metadataKind', 'nativeExportDiagnosticCompileEvidence'}
    assert fresh['engine'] == original_metadata['engine'] and fresh['recipe'] == DRIVER
    generated = fresh['nativeExportDiagnosticCompileEvidence']['generatedTranslationUnits'][0]
    generated['independentSourceDataReview'] = GENERATED_REVIEW
    checked(descriptor(__file__))
    protect(driver, d, snapshots)
    all_inputs = {}
    for ref in list(INPUTS.values()) + list(driver.INPUTS.values()):
        assert ref['path'] not in all_inputs or all_inputs[ref['path']] == ref
        all_inputs[ref['path']] = ref
    # All validation precedes first publication; old files remain immutable.
    OUT.mkdir(mode=0o700)
    d.save(OUT / 'metadata.json', fresh)
    result = dict(schemaVersion=1, state='CLOSED_NATIVE_BUILD_COLLECTION_REVIEW_COMPLETED_V2',
        passed=True, collectionReviewPassed=True, nativeCommandsPassed=True,
        originalDriverPassed=False, originalOuterRawExitCode=1,
        originalFailedResult=ORIGINAL_RESULT, originalMetadata=ORIGINAL_METADATA,
        actualOuterTerminal=OUTER_TERMINAL, actualOuterCollection=OUTER_COLLECTION,
        actualOuterStarted=OUTER_STARTED, actualOuterRequest=OUTER_REQUEST,
        builderSource=DRIVER, collectorSource=descriptor(__file__), buildSelection=SELECTION,
        nativeMetadata=descriptor(OUT / 'metadata.json'), engine=fresh['engine'], metadataKeys=sorted(fresh),
        generatedSourceDataReview=GENERATED_REVIEW, generatedTranslationUnit=generated,
        totalCompileRows=80, nativeRecipeCompileRows=79, generatedCompileRows=1,
        separateEmbeddingCompileRows=1, originalFailureClassification='exclusive prebuild recipe-membership predicate rejected selected CMake generated empty TU',
        originalFailureBitsPreserved=True, originalPhaseProvenancePreserved=True,
        actualStaticCoreValidation=CORE_VALIDATION, coreEngineExecuted=False, componentValidated=False,
        protectedBuildInputs=sorted(all_inputs.values(), key=lambda r: r['path']),
        protectedSourceInputs=sorted([r['target'] for r in rows] + [NULL_CPP], key=lambda r: r['path']),
        currentInputProtection=dict(unchanged=True, files=len(all_inputs), trees=len(snapshots)),
        oldMetadataProjected=False, toolsInvoked=False, nativeRecompiled=False, guestExecuted=False, fullNextAccepted=False)
    d.save(OUT / 'result.json', result)
    print(json.dumps(dict(result=descriptor(OUT / 'result.json'), metadata=result['nativeMetadata'], collectionReviewPassed=True,
                          originalDriverPassed=False, originalOuterRawExitCode=1)), flush=True)


if __name__ == '__main__':
    main()

