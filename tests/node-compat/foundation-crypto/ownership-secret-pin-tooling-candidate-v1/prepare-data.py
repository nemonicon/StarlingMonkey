"""Own original-context Source DATA binding only; never import an owner module."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
K=HERE.parent


def d(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size)


def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    assert not(HERE/'index.json').exists()
    proof=K/'independent-ownership-secret-normal-off-frozen-artifact-review-v1'
    pair=dict(index=d(proof/'index.json'),result=d(proof/'results.json'))
    assert pair['index']['sha256']=='380e07352b4266cfbbaea7dbd9ce97e8bfc87a15dcd2f60a94d69b7722920d96'
    actual=json.loads((proof/'results.json').read_bytes());root=Path(actual['frozenRoot'])
    receipt=json.loads(Path(actual['freezeReceipt']['path']).read_bytes())
    assert len(receipt['copies'])==1902 and sum(r['original']is not None for r in receipt['copies'])==1899
    copy_rows={r['path']:r for r in receipt['copies']}
    def frozen(relative):
        row=copy_rows[str(root/relative)];return{k:row[k]for k in['path','sha256','bytes']}
    contract=dict(schemaVersion=1,state='SECRET_OWNER355_FROZEN_ONLY_DATA_VERIFIER_SOURCE_CONTRACT_V1',implementationPhase='VERIFIER_ONLY_EXPORT_PIN_BOOTSTRAP_UNIMPLEMENTED',originalToolingRoot=str(HERE),
        frozenRoot=str(root),configuredSourceRoot=actual['configuredSourceRoot'],frozenSourceRoot=actual['sourceRoot'],componentizeSourceRoot=actual['componentizeSourceRoot'],workRoot=actual['workRoot'],freezerOriginalToolingRoot=actual['originalToolingRoot'],
        nativeSourceIndex=actual['nativeSourceIndexed'],freezerSourceIndex=actual['freezerSourceIndexed'],actualArtifactReview=pair,actualArtifactContract=d(proof/'result-contract.json'),actualFreezeRootObservation=actual['rootObservation'],
        freezeReceipt=actual['freezeReceipt'],engine=actual['engine'],metadata=actual['metadata'],expectedCopies=1902,expectedOriginalReferences=1899,expectedMembership=1903,nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,externalEmbeddingSources=3,selectedManifestCount=11,variant='normal-off',
        policy=frozen('source-policy.json'),sourceHelperData=frozen('source-policy-helper.py'),recipeData=frozen('build-engine.sh'),sourceAdmission=frozen('normal-off-source-admission.json'),compileCommands=frozen('normal-off-compile_commands.json'),cmakeCache=frozen('normal-off-CMakeCache.txt'),embeddingCommands=frozen('normal-off-embedding.after.commands.txt'),
        artifactProofInputLedger=actual['inputHashes'],actualBuildReview=actual['actualBuildReview'],buildReferenceLedger=actual['buildReferenceLedger'],
        expectedFrozenReceiptState='immutable-secret-owner355-normal-off-engine-frozen-v1',expectedSourceAdmissionState='ACTUAL_FINITE_SECRET_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION_V1',
        frozenVerifierImplemented=True,exportEntryImplemented=False,pinModelImplemented=False,bootstrapApiImplemented=False,sourceIndependentReview=None,rootAuthority=None,actualVerifierRun=None,actualExport=None,reviewedPins=None,bootstrapAuthority=None,runtimeAuthority=None,engineExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
    write('source-contract.json',contract)
    registry={name:frozen('tooling/repository/'+relative)for name,relative in{
        'moduleRegistry':'tests/node-compat/module-selection.mjs','manifestValidator':'builtins/node-compat/validate-manifest.mjs','manifestSchema':'builtins/node-compat/manifest.schema.json'}.items()}
    refs=dict(schemaVersion=1,state='SECRET_OWNER355_FROZEN_ONLY_VERIFIER_ORIGINAL_CONTEXT_INPUTS_V1',actualArtifactReview=pair,actualArtifactContract=contract['actualArtifactContract'],
        families=[dict(index=x,role='EXACT_SOURCE_OR_ACTUAL_PROOF_DATA_NOT_AN_ACTION_CARRIER')for x in [pair['index'],actual['nativeSourceIndexed'],actual['freezerSourceIndexed'],actual['actualBuildReview']['index']]],
        normalProtection=d(K/'ownership-gc-native-candidate-v2/normal-protection.json'),artifactProofInputLedger=actual['inputHashes'],frozenRegistrySources=registry,
        registryApiAllowedInFuture='builtinMap and validateManifest over actual full355/11 selected values after source/pin authentication',
        registryApiNotAdopted='selectedManifestsForEngine and old306/350/owner metadata selectors are not suitable for this new source',
        copiedActiveWrapperNotStandalone=True,ownerHelpersNotImported=True,rootAuthority=None,actualVerifierRun=None,actualExport=None,reviewedPins=None,actualBootstrap=None)
    write('references.json',refs)
    write('future-source-review-contract.json',dict(schemaVersion=1,requiredState='INDEPENDENT_CRYPTO_OWNER355_SECRET_FROZEN_VERIFIER_SOURCE_REVIEW_PASSED_V1',verifierSourceIndexSha256=None,nativeSourceIndexSha256=actual['nativeSourceIndexSha256'],freezerSourceIndexSha256=actual['freezerSourceIndexSha256'],actualArtifactReviewIndexSha256=pair['index']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,verifierHelpersInvoked=False,exportOrBootstrapInvoked=False,actualIndependentSourceReview=None,rootAuthority=None,issuesNoAuthority=True))
    write('future-tooling-phases.json',dict(schemaVersion=1,state='UNIMPLEMENTED_SECRET_OWNER355_EXPORT_PIN_BOOTSTRAP_ROADMAP_V1',normalOnly=True,variants={n:None for n in['normal-off','normal-runtime','gc-off','disabled-off']},actualArtifactReview=pair,verifierSourceIndependentReview=None,exportSourceImplemented=False,pinModelImplemented=False,bootstrapSourceImplemented=False,exportRootAuthority=None,actualExportCandidate=None,independentExportReview=None,newReviewedPins=None,newRootNativePinReview=None,bootstrapRootAuthority=None,actualBootstrapReview=None,runtimeAuthority=None,actionsAllowed=False,
        requires=['New original-context Source guard/caller authenticating this verifier family and380e exact contract','Independent export Source review and new Root export-only phase before any candidate output','Normal-only UNREVIEWED candidate with all three other variants NULL','Independent actual export proof before new reviewed pins/Root native review','New genuine355/11-manifest bootstrap API using frozen generic registry functions, not old engine selectors','Independent Source review and separate Root bootstrap phase plus actual retained full frames'],noOldMetadataOrStateProjection=True))
    print(json.dumps(dict(sourceDataPrepared=True,actualArtifactReview=pair['index']['sha256'],frozenCopies=1902,exportOrBootstrapImplemented=False,actionsInvoked=False)))


if __name__=='__main__':main()
