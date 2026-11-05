"""Pure secret355 normal-only pin DATA; no reads, helpers or actions."""
import copy

LABELS=('normal-off','normal-runtime','gc-off','disabled-off')
NATIVE='7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108'
VERIFIER='e8726a1c416afc48303faa1fd25dabed6a71872d6a65ae5ac438e2685aceb7ad'
ENGINE='901c7ba55cf48d0dc2b74e6a8f75f41d215a95946aeb89afcf592d576b60a1a7'
META='cbf9301361b68933a4ec465a70270db1969f40c79e0ee89476d89d52e5ed15c8'
RECEIPT='da2588f4bbf4494547944afec2f9ae275a7257593e054500fb64751ac9eba5c2'

def candidate(frame,receipt,refs,index):
    assert frame['schemaVersion']==1 and frame['state']=='SECRET_OWNER355_FROZEN_BYTES_AND_METADATA_VERIFIED_NO_ACTION_AUTHORITY_V1'
    assert frame['variant']=='normal-off' and frame['nativeSourceIndex']==refs['nativeSourceIndex'] and frame['nativeSourceIndex']['sha256']==NATIVE
    assert refs['verifierSourceIndex']['sha256']==VERIFIER
    for key,sha in [('engine',ENGINE),('metadataDescriptor',META),('freezeReceipt',RECEIPT)]:assert frame[key]['sha256']==sha
    assert frame['engine']==refs['engine'] and frame['metadataDescriptor']==refs['metadata'] and frame['freezeReceipt']==refs['freezeReceipt']
    metadata=frame['metadata'];assert len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3
    assert len(metadata['selectedModuleManifests'])==len(frame['selectedManifests'])==11
    assert [r['path'] for r in metadata['selectedModuleManifests']]==frame['selectedManifestPaths']
    # Core and module manifests keep their complete, distinct original objects.
    assert all(type(v)is dict and type(v['modules'])is dict for v in frame['selectedManifests'])
    assert frame['runtimeBackendProof']==dict(verified=False,version=None,vernum=None)
    for key in ['engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim','grantsActionAuthority']:assert frame[key]is False
    assert metadata['gcStress']is False and metadata['entropyPolicy']=='off' and metadata['oomTesting']is False
    assert receipt['engineSha256']==ENGINE and receipt['receiptSha256']==META and receipt['label']=='normal-off'
    assert len(receipt['copies'])==1902 and len({r['path'] for r in receipt['copies']})==1902
    assert sum(r['original']is not None for r in receipt['copies'])==1899
    for key in ['configuredSourceRoot','sourceRoot','componentizeSourceRoot']:assert receipt[key]==frame[key]
    assert frame['configuredSourceRoot']==refs['configuredSourceRoot'] and frame['sourceRoot']==refs['frozenSourceRoot']
    assert frame['componentizeSourceRoot']==refs['componentizeSourceRoot'] and frame['workRoot']==refs['workRoot']
    assert frame['verifierOriginalToolingRoot']==refs['verifierOriginalToolingRoot'] and frame['freezerOriginalToolingRoot']==refs['freezerOriginalToolingRoot']
    return copy.deepcopy(dict(schemaVersion=3,state='unreviewed-secret-owner355-normal-off-pin-v3',reviewRequired=True,variant='normal-off',
        toolingIndex=index,nativeSourceIndex=refs['nativeSourceIndex'],freezerSourceIndex=refs['freezerSourceIndex'],verifierSourceIndex=refs['verifierSourceIndex'],
        engine=refs['engine'],metadataDescriptor=refs['metadata'],freezeReceipt=refs['freezeReceipt'],enginePath=refs['engine']['path'],
        nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,verifierFrame=frame,
        frozenFiles=[{k:r[k] for k in ['path','sha256','bytes']} for r in receipt['copies']],
        actualVerifierReview=refs['actualVerifierReview'],actualFrozenArtifactReview=refs['actualArtifactReview'],
        validationBootstrapOnly=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False))

def unreviewed_document(pin):
    assert pin['state']=='unreviewed-secret-owner355-normal-off-pin-v3' and pin['reviewRequired']is True
    return dict(schemaVersion=3,state='UNREVIEWED_SECRET_OWNER355_NORMAL_OFF_PIN_CANDIDATE_V3',toolingIndex=copy.deepcopy(pin['toolingIndex']),
        reviewRequired=True,variants={k:copy.deepcopy(pin) if k=='normal-off' else None for k in LABELS},
        validationBootstrapOnly=True,operationalAdmission=False,runtimeAcceptanceClaim=False)

def reviewed_document(unreviewed):
    """Pure documented state/flag derivation, NOT review or authority issuance."""
    value=copy.deepcopy(unreviewed)
    assert value['state']=='UNREVIEWED_SECRET_OWNER355_NORMAL_OFF_PIN_CANDIDATE_V3' and value['reviewRequired']is True
    assert set(value['variants'])==set(LABELS) and all(value['variants'][k]is None for k in LABELS if k!='normal-off')
    value['state']='ROOT_REVIEWED_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PINS_V3';value['reviewRequired']=False
    pin=value['variants']['normal-off'];assert pin['state']=='unreviewed-secret-owner355-normal-off-pin-v3' and pin['reviewRequired']is True
    pin['state']='reviewed-secret-owner355-normal-off-pin-v3';pin['reviewRequired']=False
    return value

def select_reviewed(document,review,expected,reviewed_row,export_row,export_review,refs):
    assert document==reviewed_document(unreviewed_document(expected)), 'Only four documented state/flag values may differ; no metadata/frame/path projection'
    assert review['schemaVersion']==3 and review['state']=='ROOT_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V3'
    for key,value in dict(toolingIndex=expected['toolingIndex'],reviewedPins=reviewed_row,actualExportCandidate=export_row,
                          independentExportReview=export_review,actualVerifierReview=refs['actualVerifierReview'],actualFrozenArtifactReview=refs['actualArtifactReview'],
                          engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11).items():assert review[key]==value
    assert review['validationBootstrapOnly']is True and review['otherVariantsNull']is True
    for key in ['engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed']:assert review[key]is False
    return copy.deepcopy(document['variants']['normal-off'])

def bootstrap_frame(pin,verified,refs,index,root_row,config_row,reviewed_row,pin_review_row,export_row,export_review):
    assert pin['verifierFrame']==verified and pin['state']=='reviewed-secret-owner355-normal-off-pin-v3' and pin['reviewRequired']is False
    return copy.deepcopy(dict(schemaVersion=3,state='SECRET_OWNER355_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V3',variant='normal-off',
        toolingIndex=index,rootAuthority=root_row,config=config_row,nativeSourceIndex=refs['nativeSourceIndex'],freezerSourceIndex=refs['freezerSourceIndex'],
        verifierSourceIndex=refs['verifierSourceIndex'],actualVerifierReview=refs['actualVerifierReview'],actualFrozenArtifactReview=refs['actualArtifactReview'],
        actualExportCandidate=export_row,independentExportReview=export_review,reviewedPins=reviewed_row,rootPinReview=pin_review_row,
        pin=pin,verifierFrame=verified,nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,
        enginePath=refs['engine']['path'],engine=refs['engine'],metadataDescriptor=refs['metadata'],freezeReceipt=refs['freezeReceipt'],
        metadata=verified['metadata'],selectedManifests=verified['selectedManifests'],selectedManifestPaths=verified['selectedManifestPaths'],
        originalToolingRoot=refs['originalToolingRoot'],configuredSourceRoot=refs['configuredSourceRoot'],sourceRoot=refs['frozenSourceRoot'],
        frozenRoot=refs['frozenRoot'],componentizeSourceRoot=refs['componentizeSourceRoot'],workRoot=refs['workRoot'],
        currentCompleteVerifierCalls=1,rawFrameRetained=True,validationBootstrapOnly=True,engineExecuted=False,guestExecuted=False,
        operationalAdmission=False,runtimeAcceptanceClaim=False,grantsRuntimeAuthority=False))
