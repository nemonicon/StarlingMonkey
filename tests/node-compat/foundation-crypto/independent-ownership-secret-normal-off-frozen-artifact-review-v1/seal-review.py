"""Seal only this independent DATA packet; never imports owner tooling."""
import hashlib
import json
from pathlib import Path

OWN = Path(__file__).resolve().parent
K = OWN.parent
F = Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze')


def desc(p):
    p = Path(p).resolve()
    data = p.read_bytes()
    return dict(path=str(p), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def load(p):
    return json.loads(Path(p).read_bytes())


def write(name, value):
    (OWN / name).write_text(json.dumps(value, indent=2) + '\n')


root_path = K / 'ownership-secret-normal-off-freeze-v1-root-results.json'
root = load(root_path)
r = load(root['receipt']['path'])
a = load(OWN / 'audit.json')
assert a['state'] == 'INDEPENDENT_SECRET_NORMAL_OFF_FROZEN_DATA_AUDIT_COMPLETED_V1'
assert a['checks'] == 275080 and a['inventory']['copies'] == 1902
fixed = dict(schemaVersion=1,
    state='INDEPENDENT_CRYPTO_OWNER355_SECRET_NORMAL_OFF_NATIVE_ARTIFACT_REVIEW_PASSED_V1',
    verifiedPassed=True,
    nativeSourceIndexSha256=root['nativeSourceIndex']['sha256'],
    freezerSourceIndexSha256=root['freezerSourceIndex']['sha256'],
    nativeSourceFiles=355, unchangedParentNativeFiles=352, changedNativeFiles=3,
    externalEmbeddingSources=3, selectedManifestCount=11, variant='normal-off',
    engineSha256=root['engine']['sha256'], metadataSha256=root['metadata']['sha256'],
    freezeReceiptSha256=root['receipt']['sha256'],
    configuredSourceRoot=r['configuredSourceRoot'], sourceRoot=r['sourceRoot'],
    frozenRoot=str(F), componentizeSourceRoot=r['componentizeSourceRoot'],
    originalToolingRoot=r['originalToolingRoot'], workRoot=str(Path(root['engine']['path']).parents[1]),
    engineExecuted=False, guestExecuted=False, gcExecuted=False,
    operationalAdmission=False, runtimeAcceptanceClaim=False, sourcePromotionAllowed=False,
    nativePinsAdopted=False, grantsAnyActionAuthority=False,
    frozenOnlyVerifierAvailable=False, frozenOnlyExportOrBootstrapAvailable=False,
    reviewerOwnerModulesImported=False, reviewerHelpersOrRuntimeActionsInvoked=False)
artifacts = dict(engine=desc(r['engine']), metadata=desc(str(r['engine']) + '.build.json'),
    freezeReceipt=root['receipt'], actualBuildEngine=root['engine'], actualBuildMetadata=root['metadata'],
    nativeSourceIndex=root['nativeSourceIndex'], freezerSourceIndex=root['freezerSourceIndex'],
    actualFreezeRootAuthority=root['rootAuthority'], actualFreezeConfig=root['config'],
    rootObservation=desc(root_path), externalParentTerminal=root['outerTerminal'],
    ownedFreezerTerminal=root['innerTerminal'],
    activeFreezer=desc(r['activeFreezerTooling']['path']), donorFreezerData=desc(r['donorFreezerTooling']['path']),
    freezerControl=desc(r['freezerSourceCorrection']['path']), sourceAdmission=desc(r['sourceAdmission']['path']),
    embeddingAfterListing=desc(r['postBuildEmbeddingEvidence']['path']),
    actualCMakeCache=desc(F / 'normal-off-CMakeCache.txt'), actualCompileCommands=desc(F / 'normal-off-compile_commands.json'),
    actualLinkedLibcrypto=desc(F / 'normal-off-libcrypto.a'),
    buildReferenceLedger=root['buildReferenceLedger'])
coverage = dict(frozenCopies=1902, originalReferenceEntries=1899, distinctOriginalPaths=1535,
    actualFrozenFiles=1903, sourceStageCopies=1424, currentToolClosureRows=1424,
    buildReferencesRehashed=25594, checkedUniquePaths=26247, nativeCompileCommands=62,
    otherConfiguredSourceCommands=5, generatedNullCommands=1, compileDatabaseRows=68,
    strictPolicyCompileCommands=4, privateCompileCommands=6, embeddingCompileCommands=1,
    selectedCodecHeaders=4, retainedCodecWitnessFiles=9, selectedMozSymbolDefinitions=7,
    uniqueLinkedArchiveReferences=29, orderedArchiveArguments=30,
    auditedOpenSslSourceFiles=4650, rawReadonlyHelperCalls=2,
    protectedNormalCopies=1390, protectedNormalFiles=1391, protectedNormalOriginalEntries=1387)
limitations = [
    'Physical provenance copies are not a complete copy of all25594 original build references.',
    'SDK/archive/distribution semantic audits are inherited only from the exact6a0c build proof; its full ledger is freshly rehashed.',
    'No frozen-only verifier/export/pin/bootstrap tooling has been reviewed or run for this new cut; copied controls retain original contexts.',
    'No engine/guest/crypto/GC/fault/erasure/security-complete/runtime/performance proof or action authority.',
    'Runtime codec backend proof remains verified:false/version:null/vernum:null.',
    'Historical normal modes are observed0644/0755; new private freeze modes0600/0700 are separate.',
    'Raw helper observations are after-build admission/listing only, not independently observed compiler or CMake terminals.'
]
result = dict(fixed, artifacts=artifacts, coverage=coverage, engine=artifacts['engine'],
    metadata=artifacts['metadata'], freezeReceipt=artifacts['freezeReceipt'],
    actualBuildEngine=root['engine'], actualBuildMetadata=root['metadata'],
    nativeSourceIndexed=root['nativeSourceIndex'], freezerSourceIndexed=root['freezerSourceIndex'],
    actualFreezeRootAuthority=root['rootAuthority'], actualFreezeConfig=root['config'],
    rootObservation=artifacts['rootObservation'], externalParentTerminal=root['outerTerminal'],
    ownedFreezerTerminal=root['innerTerminal'], actualBuildReview=root['actualBuildReview'],
    freezerSourceReview=root['sourceReview'], buildReferenceLedger=root['buildReferenceLedger'],
    runtimeBackendProof=r['runtimeBackendProof'], processRawZeroClean=True,
    externalParentExitCode=0, rawFreezerExitCode=0, allObservedOwnedGroupsGone=True,
    signals=[], errors=[], forcedCleanup=False, timeout=False,
    rawReadonlyHelperCalls=a['rawHelpers'], nativePoliciesUnchangedFromActualMetadata=True,
    normalOriginalsAndFrozenMembershipProtected=True,
    audit=desc(OWN / 'audit.json'), inputHashes=desc(OWN / 'input-hashes.json'),
    reader=desc(OWN / 'read-artifact.py'), readerHistory=desc(OWN / 'reader-history.json'),
    checks=a['checks'], limitations=limitations)
write('results.json', result)
contract = dict(schemaVersion=1, state='SECRET_OWNER355_NORMAL_OFF_FROZEN_ARTIFACT_RESULT_CONTRACT_V1',
    requiredReviewState=fixed['state'], requiredFixedValues=fixed,
    requiredExactDescriptors=artifacts, artifacts=artifacts, requiredCoverage=coverage,
    requiredActualBuildReview=root['actualBuildReview'], requiredFreezerSourceReview=root['sourceReview'],
    requiredRuntimeBackendProof=r['runtimeBackendProof'],
    sourceContext='Original configured/build/tool contexts preserved; frozen copies are DATA, not execution-root projection.',
    limitations=limitations, issuesNoAuthority=True)
write('result-contract.json', contract)
write('review-receipt.json', dict(schemaVersion=1,
    state='SEALED_INDEPENDENT_SECRET_NORMAL_OFF_FROZEN_ARTIFACT_DATA_REVIEW_V1',
    result=desc(OWN / 'results.json'), contract=desc(OWN / 'result-contract.json'),
    source=root['nativeSourceIndex'], freezer=root['freezerSourceIndex'],
    actualReceipt=root['receipt'], audit=desc(OWN / 'audit.json'), inputHashes=desc(OWN / 'input-hashes.json'),
    ownerActionsInvoked=False))
files = []
for p in sorted(OWN.rglob('*')):
    if p.is_file() and p.name != 'index.json':
        d = desc(p)
        d['path'] = str(p.relative_to(OWN))
        files.append(d)
write('index.json', dict(schemaVersion=1, state='SEALED_INDEPENDENT_SECRET_NORMAL_OFF_FROZEN_ARTIFACT_REVIEW_FAMILY_V1', files=files))
for row in files:
    actual = desc(OWN / row['path'])
    assert (actual['sha256'], actual['bytes']) == (row['sha256'], row['bytes'])
assert set(p.name for p in OWN.iterdir()) == set(row['path'] for row in files) | {'index.json'}
print(json.dumps(dict(index=desc(OWN / 'index.json'), result=desc(OWN / 'results.json'), contract=desc(OWN / 'result-contract.json'), members=len(files))))
