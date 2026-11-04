"""Independent DATA model, input recheck, immutable evidence copies and seal."""
from pathlib import Path
import hashlib
import json
import os
import stat

D = Path(__file__).resolve().parent
K = D.parent
report_path = D / 'reader-results.json'
inputs_path = D / 'rehashed-inputs.json'

def need(value, message):
    if not value:
        raise ValueError(message)

def eq(a, b, message):
    need(json.dumps(a, sort_keys=True, separators=(',', ':')) == json.dumps(b, sort_keys=True, separators=(',', ':')), message)

def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result

def load(path):
    return json.loads(Path(path).read_bytes().decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON value')))

def physical(path):
    raw = str(path)
    return Path('/private' + raw) if raw == '/tmp' or raw.startswith('/tmp/') else Path(raw)

def desc(path):
    lexical = Path(path)
    actual = physical(lexical)
    need(actual.is_absolute() and str(actual) == os.path.normpath(str(actual)), 'absolute normalized path')
    for part in reversed([actual, *actual.parents]):
        need(not stat.S_ISLNK(part.lstat().st_mode), 'symlink in independent recheck: ' + str(part))
    before = actual.stat()
    need(stat.S_ISREG(before.st_mode), 'regular input')
    digest = hashlib.sha256()
    with actual.open('rb') as stream:
        while True:
            block = stream.read(4 * 1024 * 1024)
            if not block:
                break
            digest.update(block)
    after = actual.stat()
    signature = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns)
    eq(signature(before), signature(after), 'stable file while hashing')
    return {'path': str(lexical), 'sha256': digest.hexdigest(), 'bytes': after.st_size}

def write(name, value):
    path = D / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')

report = load(report_path)
refs = report['descriptors']
candidate = load(refs['candidatePins']['path'])
pins = load(refs['reviewedPins']['path'])
pin = pins['variants']['normal-off']
freeze = load(refs['freezeReceipt']['path'])
metadata = load(refs['metadata']['path'])
native = load(refs['independentNativeReviewResult']['path'])
root = load(refs['actualRootResults']['path'])
source = Path(refs['sourceIndex']['path']).parent
contract_source = load(source / 'admission-pins.json')
frozen_root = Path(pin['freezeRoot'])

# Reconstruct every candidate value from retained actual freeze/metadata DATA.
# This is a fixed independent field model, not an import/evaluation of exporter code.
expected_candidate_pin = {
    'state': 'unreviewed-crypto-owner355-freeze-pin-candidate',
    'variant': 'normal-off', 'label': 'normal-off',
    'gcStress': metadata['gcStress'], 'entropyPolicy': metadata['entropyPolicy'],
    'classicStreamsEnabled': metadata['classicStreamsEnabled'],
    'sourceContractVersion': 'sm-webcrypto-key-owner-and-prototype-guard-source-v1',
    'classicTraceSourcePolicy': metadata['classicTraceSourcePolicy'],
    'cryptoKeyOwnershipPolicy': metadata['cryptoKeyOwnershipPolicy'],
    'zlibEnabled': metadata['zlibEnabled'], 'zlibSourcePolicy': metadata['zlibSourcePolicy'],
    'runtimeBackendProof': {'verified': False, 'version': None, 'vernum': None},
    'streamConsumersEnabled': metadata['streamConsumersEnabled'],
    'streamConsumersSourcePolicy': metadata['streamConsumersSourcePolicy'],
    'sourceFiles': 355, 'recipeSha256': contract_source['productionRecipeSha256'],
    'engineBytes': freeze['engineBytes'], 'engineSha256': freeze['engineSha256'],
    'receiptSha256': freeze['receiptSha256'], 'cmakeCacheSha256': metadata['cmakeCacheSha256'],
    'compileCommandsSha256': metadata['compileCommandsSha256'],
    'freezeReceiptSha256': refs['freezeReceipt']['sha256'], 'freezeRoot': str(frozen_root),
    'enginePath': str(frozen_root / 'normal-off.engine.wasm'),
    'sourceRoot': str(frozen_root / 'source'), 'componentizeSourceRoot': str(frozen_root / 'componentize-source'),
    'cachePath': str(frozen_root / 'normal-off-CMakeCache.txt'),
    'commandsPath': str(frozen_root / 'normal-off-compile_commands.json'),
    'recipePath': str(frozen_root / 'build-engine.sh'),
    'freezeReceiptPath': str(frozen_root / 'normal-off-freeze-receipt.json'),
    'coreSources': freeze['coreSources'],
    'frozenFiles': [{key: row[key] for key in ['path', 'sha256', 'bytes']} for row in freeze['copies']],
    'parentEmbeddingCommandPath': freeze['postBuildEmbeddingEvidence']['path'],
    'parentEmbeddingCommandSha256': freeze['postBuildEmbeddingEvidence']['sha256'],
    'reviewRequired': True, 'runtimeAcceptanceClaim': False}
eq(candidate['variants']['normal-off'], expected_candidate_pin, 'all candidate fields match actual freeze and metadata model')
need(metadata['cryptoKeyOwnershipBuildEvidence']['installationSource']['count'] == 1, 'one captured crypto namespace')
need(len(metadata['cryptoKeyOwnershipBuildEvidence']['changedNativeCompileCommands']) == 3, 'three changed captured C++ commands')
eq(metadata['zlibPolicy']['runtimeBackendProof'], {'verified': False, 'version': None, 'vernum': None}, 'metadata backend proof closed')
eq(metadata['zlibPolicy']['codecWitness']['runtimeBackendProof'], {'verified': False, 'version': None, 'vernum': None}, 'codec witness backend proof closed')
eq(native['selectedLibcryptoArchiveSymbols']['OPENSSL_cleanse']['gnuArchiveIndexSymbol'], 'OPENSSL_cleanse', 'prior authenticated cleanse symbol')
eq(native['selectedLibcryptoArchiveSymbols']['EVP_PKEY_free']['gnuArchiveIndexSymbol'], 'EVP_PKEY_free', 'prior authenticated EVP symbol')

source_flow_notes = {
    'schemaVersion': 1,
    'allCandidateVariantFieldsReconstructedFromActualFreezeAndMetadata': True,
    'candidateVariantFieldCount': len(expected_candidate_pin),
    'retainedPinVariantFieldCount': len(pin),
    'oneCryptoInstallNamespaceAndThreeChangedCppCommands': True,
    'fullNative355ManifestAndFiveChangedPathsPreserved': True,
    'existingNativeSymbolEvidenceRehashedOnly': native['selectedLibcryptoArchiveSymbols'],
    'ordinaryOperationalSelectorRemainsClosed': True,
    'sourceEvidenceForOrdinaryClosed': desc(source / 'build-admission.mjs'),
    'readOnlyHelperExecutionScope': {
        'exporter': 'One actual Python exporter invoked genuine frozen verification; exporter retained UNREVIEWED DATA only.',
        'bootstrap': 'Actual Node entry invoked genuine JS bootstrap, including initial Python classifier and pre-return recheck, then awaited returned recheck before durable success.',
        'internalClassifiers': 'Three executions required by authenticated source control flow; individual internal Python proof objects and metadata-Node returns were not retained.',
        'targetEngine': 'Hashed as native artifact input; never launched by these exporter/bootstrap source paths.'},
    'authenticatedSourceInspection': 'Read as text only; no owner code imported or invoked by either independent reader.',
    'claimsNotMade': ['general JavaScript semantic correctness', 'independently captured internal helper process tree',
        'exact inherited child environment', 'process group gone', 'key/crypto behavior', 'runtime acceptance',
        'component construction', 'ordinary operational admission', 'performance'],
    'ownWork': {'readHashJsonDataOnly': True, 'ownerOrNodeOrCliOrEngineOrKeyCryptoGcGuestActions': False}}
write('finite-data-model-review.json', source_flow_notes)

# Retain exact copies of every new external raw capture and the principal DATA wrappers.
copies = []
named = {
    'root-results.json': refs['actualRootResults'], 'pin-export-authority.json': refs['pinExportAuthority'],
    'candidate-pins.UNREVIEWED.json': refs['candidatePins'], 'reviewed-pins.json': refs['reviewedPins'],
    'root-review.json': refs['rootReview'], 'post-reader-syntax-history.json': refs['postReaderSyntaxHistory']}
for name, row in named.items():
    eq(desc(row['path']), row, 'principal copy source hash')
    target = D / 'evidence' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as output:
        output.write(Path(row['path']).read_bytes())
    copied = desc(target)
    eq(copied['sha256'], row['sha256'], 'principal evidence exact bytes')
    eq(copied['bytes'], row['bytes'], 'principal evidence exact size')
    copies.append({'original': row, 'copy': {'path': str(target.relative_to(D)), 'sha256': copied['sha256'], 'bytes': copied['bytes']}})
for prefix, terminal_key in [('pin-export', 'pinExportTerminal'), ('bootstrap', 'bootstrapTerminal')]:
    directory = Path(refs[terminal_key]['path']).parent
    for path in sorted(directory.iterdir()):
        original = desc(path)
        target = D / 'evidence' / prefix / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as output:
            output.write(path.read_bytes())
        copied = desc(target)
        eq(copied['sha256'], original['sha256'], 'raw evidence exact bytes')
        eq(copied['bytes'], original['bytes'], 'raw evidence exact size')
        copies.append({'original': original, 'copy': {'path': str(target.relative_to(D)), 'sha256': copied['sha256'], 'bytes': copied['bytes']}})
write('evidence-copies.json', copies)

result_contract = {
    'schemaVersion': 1, 'state': report['state'], 'verifiedPassed': True,
    'variant': 'normal-off', 'normalOnly': True,
    'nativeProducerIndexSha256': report['sourceIndexSha256'],
    'sourceIndex': refs['sourceIndex'], 'configuredSourceIndex': refs['configuredSourceIndex'],
    'independentSourceReviewIndex': refs['independentSourceReviewIndex'],
    'reviewedPins': refs['reviewedPins'], 'rootNativeReview': refs['rootReview'],
    'candidatePins': refs['candidatePins'], 'candidateRemainsUnreviewedData': True,
    'independentNativeReview': {'index': refs['independentNativeReviewIndex'], 'result': refs['independentNativeReviewResult']},
    'actualRootResults': refs['actualRootResults'], 'pinExportAuthority': refs['pinExportAuthority'],
    'externalPinExportTerminal': refs['pinExportTerminal'], 'externalBootstrapTerminal': refs['bootstrapTerminal'],
    'actualJsBootstrapResult': refs['bootstrapResult'], 'actualJsBootstrapFrame': refs['frameData'],
    'bootstrapEntrySource': refs['bootstrapEntrySource'], 'nodeBinary': refs['nodeBinary'],
    'configuredSourceRoot': report['configuredSourceRoot'], 'sourceRoot': report['frozenSourceRoot'],
    'contextsAreDistinct': True, 'contextApiFindingM1ResolvedInSource': True,
    'engine': refs['engine'], 'metadata': refs['metadata'], 'freezeReceipt': refs['freezeReceipt'],
    'priorNativeDescriptorOriginalSpellings': {'engine': refs['nativeReviewEngineOriginalSpelling'],
        'metadata': refs['nativeReviewMetadataOriginalSpelling'], 'freezeReceipt': refs['nativeReviewFreezeReceiptOriginalSpelling']},
    'nativeDescriptorAliasComparison': 'Only system /tmp -> /private/tmp; exact hash and byte count; original primitive spellings preserved.',
    'sourceFiles': 355, 'externalEmbeddingSources': 3, 'unchangedParentNativePaths': 350,
    'changedNativePaths': report['changedNativePaths'], 'composedNativeEditsBoundByPriorProof': 20,
    'frozenCopies': 1390, 'actualFrozenRegularFiles': 1391, 'configuredToolDependencies': 922,
    'nativePriorInputRowsRehashed': 8821, 'sourcePeerInputRowsRehashed': 1711,
    'sourcePreparationRowsRehashed': 1323, 'selectedManifestCount': 11,
    'allCandidateVariantFieldsMatchActualFreezeAndMetadata': True,
    'perVariantChangesExactly': report['perVariantChangesExactly'],
    'topLevelReviewedWrapperAddedSeparately': True, 'otherVariantsNull': True,
    'fullReturnedMetadataAndPinAndSelectedManifestsVerified': True,
    'pinExportRawExitCode': 0, 'bootstrapRawExitCode': 0,
    'pinExportTimedOut': False, 'bootstrapTimedOut': False,
    'pinExportStderrBytes': 0, 'bootstrapStderrBytes': 0,
    'rawPinExportPid': 89088, 'rawBootstrapPid': 91553,
    'actualGenuineJsBootstrapPassed': True, 'actualReturnedRecheckPassed': True,
    'validationBootstrapOnly': True, 'readOnlyBootstrapOnly': True,
    'rootPythonExporterExecuted': True, 'rootNodeBootstrapExecuted': True,
    'rootReadOnlyAdmissionHelpersInvoked': True,
    'internalClassifierCallsSupportedByAuthenticatedSourceAndFinalOutcome': 3,
    'internalHelperObjectsSeparatelyRetained': False,
    'completeInheritedEnvironmentRetained': False, 'processGroupGoneProbeRetained': False,
    'internalHelperEvidenceScope': report['internalHelperRechecksEvidence'],
    'reviewerReadHashJsonDataOnly': True,
    'reviewerOwnerHelpersNodeCliEngineKeyCryptoGcComponentGuestOrHostActions': False,
    'rootTargetEngineKeyCryptoGcComponentGuestOrHostFixtureActions': False,
    'positiveKeyOperationsInvoked': False, 'keyBehaviorAccepted': False,
    'runtimeBackendProof': {'verified': False, 'version': None, 'vernum': None},
    'ordinaryOperationalAdmission': False, 'operationalAdmission': False, 'runtimeAcceptanceClaim': False,
    'sourcePromotionAllowed': False, 'performanceClaim': False, 'timingAllowed': False,
    'futureComponentRootAuthority': None, 'futureKeyCryptoGcAuthority': None, 'futureOperationalApproval': None,
    'followOnGate': 'Any component construction or key/crypto/GC/guest action requires its own reviewed source closure and separate new Root authority.',
    'notAComponentOrKeyRuntimeProof': True,
    'scope': 'Exact normal-OFF native build-input pin derivation plus actual genuine read-only JS bootstrap/recheck; no ordinary operational or key/crypto runtime acceptance.'}
write('result-contract.json', result_contract)
result_contract_row = desc(D / 'result-contract.json')
results = dict(report)
results['resultContract'] = result_contract_row
results['allCandidateVariantFieldsReconstructedFromActualFreezeAndMetadata'] = True
results['otherVariantsNull'] = True
results['positiveKeyOperationsInvoked'] = False
results['uniqueInputsRehashed'] = len(load(inputs_path))
results['dataModelReview'] = desc(D / 'finite-data-model-review.json')
results['evidenceCopies'] = desc(D / 'evidence-copies.json')
write('results.json', results)

readme = """This packet verifies the exact normal-OFF CryptoOwner355 pin derivation and retained actual read-only JavaScript bootstrap/recheck. Root's Python exporter (PID 89088) and Node bootstrap entry (PID 91553) each returned raw0, with no timeout and empty stderr. The actual UNREVIEWED candidate remains unchanged. Every candidate variant field was independently reconstructed from the accepted native freeze/metadata DATA. The reviewed variant differs only in state, reviewRequired and four independent-proof fields; its top-level reviewed wrapper is separately added. Normal-runtime, gc-off and disabled-off remain null.

The reader rehashed all 8,821 native-review ledger rows, the 21-member native review, the 44-member source proposal, the 8-member context-API source review and its 1,711 rows, all 1,323 original preparation rows, 922 configured tool dependencies, the actual native355 plus three embedding-source bindings, and all 1,390 frozen copies with exact 1,391-file membership. The complete returned metadata and pin match authenticated files, and every one of the 11 complete returned manifests matches frozen native source. Exactly five native replacements and 350 unchanged parent paths are retained. The prior native symbol evidence was authenticated as DATA; no symbol tool/compiler/verifier was rerun.

The actual primitive configured root is /private/tmp/starling-node-compat/crypto-owner-source-v2. The separate frozen source root is /tmp/starling-node-compat/production-crypto-owner-v2/native-freeze/source. Both are preserved. Native review descriptors used /private/tmp for the same frozen files; only the system /tmp alias is compared, alongside exact SHA256 and size. The source fixes context-API finding CRYPTO-OWNER355-CONTEXT-API-M1 and does not relabel the immutable v1 HOLD. An initial independent-reader path-spelling assumption is retained under history; it wrote no result or input ledger before correction.

Root invoked genuine read-only Python and Node admission helpers. Authenticated source requires an initial classifier, its pre-return recheck, and the caller's awaited returned recheck before durable success. The individual internal helper objects and metadata-Node returns were not separately retained. Their checks are supported by exact source control flow, raw clean final outcome and the complete retained frame/result, not separate raw per-helper captures. Launch source filters the documented environment variables, but no full inherited environment or process-group-gone probe is retained. The elapsed numbers are operational bookkeeping only. Root's separate post-reader SyntaxError is preserved as pre-I/O preparation history and is not an actual bootstrap failure.

The independent reviewer used new Python standard-library read/hash/JSON DATA readers and inspected owner source as text. No owner script, helper, Node, CLI, compiler, native engine, key/crypto/GC operation, component, guest or target host fixture was invoked by this review. Root's Node bootstrap execution is explicitly distinct from the reviewer's actions. This is a bounded pin/bootstrap proof, not general JavaScript semantics, engine/key behavior, finalizer/erasure, request reuse, runtime acceptance, performance or ordinary operational admission. Backend proof remains false/null/null. All future component/key/crypto/GC/operational action slots remain null; follow-on work needs its own reviewed source and separate Root authority.

Use result-contract.json as the stable finite consumer contract. Rehash this packet's index and all referenced original descriptors; the source/proof packet itself grants no action authority. Existing sealed files were read only. Evidence copies preserve every new external capture and the principal pin/Root wrappers byte-for-byte.
"""
with (D / 'README.md').open('x') as output:
    output.write(readme)

write('review-receipt.json', {
    'schemaVersion': 1, 'state': 'SEALED_INDEPENDENT_CRYPTO_OWNER355_NORMAL_OFF_PIN_AND_JS_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1',
    'result': desc(D / 'results.json'), 'resultContract': result_contract_row,
    'actualRootResults': refs['actualRootResults'], 'reviewedPins': refs['reviewedPins'],
    'sourceIndex': refs['sourceIndex'], 'independentNativeReviewIndex': refs['independentNativeReviewIndex'],
    'verifiedPassed': True, 'readHashDataOnly': True, 'rootHelpersDidExecute': True,
    'positiveKeyOperationsInvoked': False, 'operationalAdmission': False, 'runtimeAcceptanceClaim': False,
    'futureActionAuthority': None})

inputs = load(inputs_path)
need(len(inputs) == 9214 and len({row['path'] for row in inputs}) == len(inputs), 'exact finite unique input ledger')
for row in inputs:
    eq(desc(row['path']), row, 'final original input rehash: ' + row['path'])
for copy in copies:
    eq(desc(copy['original']['path']), copy['original'], 'final evidence original rehash')
    copied = desc(D / copy['copy']['path'])
    eq({key: copied[key] for key in ['sha256', 'bytes']},
       {key: copy['copy'][key] for key in ['sha256', 'bytes']}, 'final evidence copy rehash')
write('verification.json', {
    'schemaVersion': 1, 'state': 'INDEPENDENT_PIN_BOOTSTRAP_FINAL_INPUT_REHASH_AND_DATA_MODEL_PASSED_V1',
    'uniqueOriginalInputsRehashed': len(inputs), 'allOriginalDescriptorsStable': True,
    'allCandidateFieldsReconstructed': True, 'exactEvidenceCopies': len(copies),
    'nativeAndSourceIndexedMembershipPassed': True, 'actualExternalCaptureMembershipPassed': True,
    'frozenMembershipPassed': True, 'ownerActionsInvoked': False, 'operationalAdmission': False})

members = []
for path in sorted(D.rglob('*')):
    if path.is_file():
        row = desc(path)
        members.append({'path': str(path.relative_to(D)), 'sha256': row['sha256'], 'bytes': row['bytes']})
write('index.json', {'schemaVersion': 1,
    'state': 'SEALED_INDEPENDENT_CRYPTO_OWNER355_NORMAL_OFF_PIN_AND_JS_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1',
    'files': members, 'verifiedPassed': True, 'readHashDataOnly': True,
    'operationalAdmission': False, 'runtimeAcceptanceClaim': False, 'futureActionAuthority': None})
index = load(D / 'index.json')
eq(sorted([row['path'] for row in index['files']] + ['index.json']),
   sorted(str(path.relative_to(D)) for path in D.rglob('*') if path.is_file()), 'final independent exact membership')
for row in index['files']:
    actual = desc(D / row['path'])
    eq(actual['sha256'], row['sha256'], 'sealed independent member SHA')
    eq(actual['bytes'], row['bytes'], 'sealed independent member size')
print(json.dumps({'index': desc(D / 'index.json'), 'result': desc(D / 'results.json'),
    'resultContract': desc(D / 'result-contract.json'), 'indexedFiles': len(members),
    'actualRegularFiles': len(members) + 1, 'uniqueOriginalInputs': len(inputs), 'state': report['state']}))
