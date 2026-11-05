"""Source DATA bindings only. Never imports or invokes a verifier/helper."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
K=HERE.parent
REPO=K.parents[2]


def d(path):
    p=Path(path);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)


def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def pair(name):return dict(index=d(K/name/'index.json'),result=d(K/name/'results.json'))


def main():
    assert not(HERE/'index.json').exists()
    source=K/'ownership-secret-pin-tooling-candidate-v1';peer=pair('independent-ownership-secret-frozen-verifier-source-review-v1')
    source_ix=d(source/'index.json');assert source_ix['sha256']=='e8726a1c416afc48303faa1fd25dabed6a71872d6a65ae5ac438e2685aceb7ad'
    assert peer['index']['sha256']=='7a453906d856d587c16486d81acca3c8b247c43950b447e1ebde6bf822aec8ff'
    c=json.loads((source/'source-contract.json').read_bytes());sr=json.loads((source/'references.json').read_bytes())
    monitor=K/'ownership-gc-build-controller-candidate-v1'
    refs=dict(schemaVersion=1,state='SECRET_OWNER355_READ_ONLY_VERIFIER_CALLER_ORIGINAL_CONTEXT_REFERENCES_V1',verifierSourceIndex=source_ix,verifierSourceReview=peer,verifierContract=d(source/'source-contract.json'),verifierEntry=d(source/'verifier.py'),verifierSourceInputs=d(source/'source-inputs.json'),actualArtifactReview=c['actualArtifactReview'],actualArtifactContract=c['actualArtifactContract'],artifactInputLedger=c['artifactProofInputLedger'],normalProtection=sr['normalProtection'],monitorIndex=d(monitor/'index.json'),monitorEntry=d(monitor/'monitor.py'),
        families=[dict(index=x,role='EXACT_ORIGINAL_SOURCE_OR_ACTUAL_DATA_NOT_ACTION_AUTHORITY')for x in[source_ix,peer['index'],c['actualArtifactReview']['index'],c['nativeSourceIndex'],c['freezerSourceIndex'],c['actualBuildReview']['index'],d(monitor/'index.json')]],
        frozenRoot=c['frozenRoot'],frozenSourceRoot=c['frozenSourceRoot'],configuredSourceRoot=c['configuredSourceRoot'],workRoot=c['workRoot'],engine=c['engine'],metadata=c['metadata'],freezeReceipt=c['freezeReceipt'],nativeSourceIndex=c['nativeSourceIndex'],freezerSourceIndex=c['freezerSourceIndex'],
        controllerIndependentReview=None,rootAuthority=None,actualVerifierResult=None,actualExport=None,reviewedPins=None,bootstrapAuthority=None,runtimeAuthority=None,actionsAllowed=False)
    write('references.json',refs)
    root=dict(schemaVersion=1,state=None,phase='verify-frozen-read-only',variant='normal-off',controllerIndex=None,controllerEntry=None,controllerIndependentReview=None,verifierSourceIndex=source_ix,verifierSourceReview=peer,verifierContract=refs['verifierContract'],verifierEntry=refs['verifierEntry'],actualArtifactReview=c['actualArtifactReview'],actualArtifactContract=c['actualArtifactContract'],nativeSourceIndex=c['nativeSourceIndex'],freezerSourceIndex=c['freezerSourceIndex'],engine=c['engine'],metadata=c['metadata'],freezeReceipt=c['freezeReceipt'],frozenRoot=c['frozenRoot'],outputRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-frozen-verifier-v1',externalOutputRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-frozen-verifier-v1-external-root',externalParentDeadlineSeconds=600,expectedVerifierCalls=1,verifierReadOnlyAllowed=False)
    for k in['nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','ninjaAllowed','ownerHelperAllowed','nodeAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','exportAllowed','bootstrapAllowed','componentAllowed','operationalAdmission','runtimeAcceptanceClaim','metadataProjectionAllowed','sourcePromotionAllowed','timingAllowed']:root[k]=False
    for k in['actualVerifierResult','independentActualVerifierReview','actualExport','reviewedPins','actualBootstrap','runtimeAuthority']:root[k]=None
    write('future-root-authority.template.json',root)
    write('future-config.template.json',dict(schemaVersion=1,state='SECRET_OWNER355_VERIFIER_CONTROLLER_CONFIG_V1',controllerIndex=None,rootAuthority=None))
    write('future-source-review-contract.json',dict(schemaVersion=1,requiredState='INDEPENDENT_CRYPTO_OWNER355_SECRET_VERIFIER_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=None,verifierSourceIndexSha256=source_ix['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,verifierActionsInvoked=False,actualIndependentSourceReview=None,rootAuthority=None,issuesNoAuthority=True))
    print(json.dumps(dict(sourceDataPrepared=True,newRootAuthority=None,actualVerifierResult=None,actionsInvoked=False)))


if __name__=='__main__':main()
