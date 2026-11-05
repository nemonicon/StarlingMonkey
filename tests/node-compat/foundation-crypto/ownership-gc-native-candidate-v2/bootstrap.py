"""Future read-only actual GC bootstrap, no engine execution or global rebinding."""
from pathlib import Path
import json,subprocess,sys
import context as C,guard
from data_io import indexed,read,regular
from pin_model import select
def bootstrap(config):
    frame=guard.authorize(config,'bootstrap');root=frame['root'];pins_row=root['reviewedGcPins'];review_row=root['gcNativeRootReview']
    document=read(pins_row);review=read(review_row);pin=select(document,review,pins_row['sha256'],frame['sourceIndex']['sha256'])
    pair=root['independentGcNativeReview'];_,proof_rows=indexed(pair['index']);proof=read(pair['result'])
    assert sum(r==pair['result']for r in proof_rows)==1 and proof['state']=='INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_ARTIFACT_REVIEW_PASSED_V1'and proof['verifiedPassed']is True
    assert proof['sourceIndexSha256']==frame['sourceIndex']['sha256']and proof['nativeSourceFiles']==355 and proof['variant']=='gc-off'
    assert proof['engineSha256']==pin['engineSha256']and proof['freezeReceiptSha256']==pin['freezeReceiptSha256']
    assert pair['index']['sha256']==pin['independentProofIndexSha256']and pair['result']['sha256']==pin['independentProofResultSha256']
    assert pair['index']['path']==pin['independentProofIndexPath']and pair['result']['path']==pin['independentProofResultPath']
    frame['captured'] += [pins_row,review_row,*proof_rows]
    common=guard.load_common(frame)
    receipt_path,receipt,metadata,receipt_sha=common.verify_frozen_variant('gc-off',output=Path(C.FREEZE),return_receipt_digest=True)
    C.metadata_model(metadata)
    assert receipt_sha==pin['freezeReceiptSha256']and str(receipt_path)==pin['freezeReceiptPath']
    for field in ['engineSha256','engineBytes','receiptSha256']:assert receipt[field]==pin[field]
    assert pin['frozenFiles']==[{k:r[k]for k in ['path','sha256','bytes']}for r in receipt['copies']]
    for field,name in [('enginePath','gc-off.engine.wasm'),('sourceRoot','source'),('componentizeSourceRoot','componentize-source'),('cachePath','gc-off-CMakeCache.txt'),('commandsPath','gc-off-compile_commands.json'),('recipePath','build-engine.sh')]:assert pin[field]==str(Path(C.FREEZE)/name)
    for field in ['gcStress','entropyPolicy','classicStreamsEnabled','zlibEnabled','streamConsumersEnabled','classicTraceSourcePolicy','cryptoKeyOwnershipPolicy','zlibSourcePolicy','streamConsumersSourcePolicy','cmakeCacheSha256','compileCommandsSha256']:assert pin[field]==metadata[field]
    assert pin['coreSources']==receipt['coreSources']and pin['parentEmbeddingCommandPath']==receipt['postBuildEmbeddingEvidence']['path']and pin['parentEmbeddingCommandSha256']==receipt['postBuildEmbeddingEvidence']['sha256']
    regular(frame['references']['node'])
    command=[C.NODE,C.TOOLS+'/metadata-admission.mjs',C.FREEZE+'/gc-off.engine.wasm.build.json','gc-off',C.SOURCE]
    p=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=55);admission=json.loads(p.stdout);guard.validate_admission(admission)
    manifests=[]
    for name in admission['selectedManifestPaths']:
        r=next(r for r in metadata['sourceManifest']if r['path']==name);path=Path(C.FREEZE)/'source'/name
        # Authentic stored manifests, without fabricating a configured/frozen root.
        common.checked(path,r['sha256']);manifests.append(json.loads(path.read_bytes()))
    _,final_receipt,final_metadata,final_sha=common.verify_frozen_variant('gc-off',output=Path(C.FREEZE),return_receipt_digest=True)
    assert final_sha==receipt_sha and final_receipt==receipt and final_metadata==metadata,'Full actual GC freeze changed during selector/manifest reads'
    guard.recheck(frame)
    return dict(schemaVersion=1,state='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_BOOTSTRAP_PASSED_V1',variant='gc-off',sourceIndexSha256=frame['sourceIndex']['sha256'],enginePath=pin['enginePath'],sourceRoot=pin['sourceRoot'],configuredSourceRoot=str(common.REPO),pin=pin,metadata=metadata,selectedManifests=manifests,manifestPaths=admission['selectedManifestPaths'],reviewedPinsSha256=pins_row['sha256'],rootReviewSha256=review_row['sha256'],runtimeBackendProof=dict(verified=False,version=None,vernum=None),validationBootstrapOnly=True,operationalAdmission=False,guestExecuted=False)
if __name__=='__main__':assert len(sys.argv)==2;print(json.dumps(bootstrap(json.loads(sys.argv[1]))))
