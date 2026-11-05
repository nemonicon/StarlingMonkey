"""Pure future GC-only pin selection, never synthetic metadata acceptance."""
import context as C
LABELS=('normal-off','normal-runtime','gc-off','disabled-off')
def select(document,review,pins_sha,source_sha):
    assert document['schemaVersion']==1 and document['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_BOOTSTRAP_V1'
    assert document['sourceIndexSha256']==source_sha
    assert set(document['variants'])==set(LABELS)
    assert all(document['variants'][name]is None for name in LABELS if name!='gc-off')
    pin=document['variants']['gc-off'];assert isinstance(pin,dict)and pin['variant']=='gc-off'and pin['gcStress']is True and pin['entropyPolicy']=='off'
    assert pin['sourceFiles']==355 and pin['recipeSha256']==C.RECIPE_SHA
    assert pin['sourceContractVersion']=='sm-webcrypto-key-owner-and-prototype-guard-source-v1'
    assert pin['reviewRequired']is False and pin['state']=='reviewed-crypto-owner355-native-build-for-validation'
    assert pin['runtimeBackendProof']==dict(verified=False,version=None,vernum=None)and pin['runtimeAcceptanceClaim']is False
    assert C.canonical(pin['freezeRoot'])==C.FREEZE and C.canonical(pin['sourceRoot'])==C.FREEZE+'/source'
    assert review['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PINS_V1'and review['sourceIndexSha256']==source_sha and review['reviewedPinsSha256']==pins_sha
    C.contexts(review)
    assert review['sourceFiles']==355 and review['externalSources']==3 and review['operationalAdmission']is False and review['runtimeAcceptanceClaim']is False
    for k in ['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256','independentProofIndexSha256','independentProofResultSha256']:assert review['gcOff'][k]==pin[k]
    return dict(pin)
