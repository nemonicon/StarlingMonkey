"""Pure finite pin DATA model. Never reads an engine, helper, proof or Root authority."""
import copy
SOURCE_SHA='20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414'
FREEZER_SHA='f88db73e4541e72bf37fa1c2a684257a737fde1dc685a34f00335ebc0705b072'
ENGINE_SHA='fec7a900f0c04815e3609d2f9a5ed94056d854bd1a8f241bf74cb5f3f475a704'
META_SHA='51fbc0a06ed2e06c24e6d1fd3190873a5a3190657cfe2d74bf44ff4128b0e80e'
RECEIPT_SHA='b96f801de68175e8d2a652468a07c93f03ed85f6a9cbaca1f0a33710b3a08d86'
LABELS=('normal-off','normal-runtime','gc-off','disabled-off')
def candidate(receipt,metadata,refs,tooling_index):
 assert receipt['variant']=='normal-off'and receipt['resourceSourceIndexSha256']==SOURCE_SHA and receipt['freezerSourceIndexSha256']==FREEZER_SHA
 assert receipt['engine']['sha256']==metadata['engineSha256']==ENGINE_SHA and receipt['metadata']['sha256']==META_SHA and refs['freezeReceipt']['sha256']==RECEIPT_SHA
 assert receipt['nativeInputsVerified']==len(metadata['sourceManifest'])==342 and receipt['externalEmbeddingInputsVerified']==len(metadata['componentizeSourceManifest'])==3
 assert receipt['selectedManifestCount']==len(metadata['selectedModuleManifests'])==9 and metadata['gcStress']is False and metadata['entropyPolicy']=='off'and metadata['oomTesting']is False
 assert metadata['resourceOwnershipPolicy']['nativeRuntimeValidation']is None and receipt['configuredSourceRoot']==refs['configuredSourceRoot']and receipt['sourceRoot']==refs['frozenSourceRoot']and receipt['componentizeSourceRoot']==refs['componentizeSourceRoot']
 return copy.deepcopy(dict(state='unreviewed-scheduler-resource342-normal-off-freeze-v1',reviewRequired=True,variant='normal-off',resourceSourceIndexSha256=SOURCE_SHA,freezerSourceIndexSha256=FREEZER_SHA,toolingIndex=tooling_index,enginePath=receipt['engine']['path'],engineSha256=ENGINE_SHA,engineBytes=receipt['engine']['bytes'],metadataPath=receipt['metadata']['path'],metadataSha256=META_SHA,metadataBytes=receipt['metadata']['bytes'],freezeReceipt=refs['freezeReceipt'],configuredSourceRoot=refs['configuredSourceRoot'],sourceRoot=refs['frozenSourceRoot'],componentizeSourceRoot=refs['componentizeSourceRoot'],nativeSourceFiles=342,externalEmbeddingSources=3,sourceManifest=metadata['sourceManifest'],componentizeSourceManifest=metadata['componentizeSourceManifest'],selectedModuleManifests=metadata['selectedModuleManifests'],resourceOwnershipPolicy=metadata['resourceOwnershipPolicy'],classicTraceSourcePolicy=metadata['classicTraceSourcePolicy'],gcStress=False,entropyPolicy='off',oomTesting=False,buildRecipeSha256=metadata['buildRecipeSha256'],actualArtifactReview=refs['actualArtifactReview'],frozenFiles=[{k:r[k]for k in('path','sha256','bytes')}for r in receipt['copies']],validationBootstrapOnly=True,operationalAdmission=False,runtimeAcceptanceClaim=False))
def unreviewed_document(pin):
 assert pin['state']=='unreviewed-scheduler-resource342-normal-off-freeze-v1'and pin['reviewRequired']is True
 return dict(schemaVersion=1,state='UNREVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_PIN_CANDIDATE_V1',resourceSourceIndexSha256=SOURCE_SHA,freezerSourceIndexSha256=FREEZER_SHA,toolingIndex=copy.deepcopy(pin['toolingIndex']),reviewRequired=True,variants={name:copy.deepcopy(pin)if name=='normal-off'else None for name in LABELS},validationBootstrapOnly=True,operationalAdmission=False,runtimeAcceptanceClaim=False)
def select_reviewed(document,review,expected,reviewed_sha,export_row,export_review):
 assert document['schemaVersion']==1 and document['state']=='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_VALIDATION_PINS_V1'and document['reviewRequired']is False
 assert document['resourceSourceIndexSha256']==SOURCE_SHA and document['freezerSourceIndexSha256']==FREEZER_SHA and document['toolingIndex']==expected['toolingIndex']
 assert set(document['variants'])==set(LABELS)and all(document['variants'][n]is None for n in LABELS if n!='normal-off')
 pin=copy.deepcopy(document['variants']['normal-off']);assert pin['state']=='reviewed-scheduler-resource342-normal-off-freeze-v1'and pin['reviewRequired']is False
 pin['state']='unreviewed-scheduler-resource342-normal-off-freeze-v1';pin['reviewRequired']=True;assert pin==expected,'Only genuine reviewed state/flag differs from actual candidate; no tuple/metadata projection'
 assert document['validationBootstrapOnly']is True and document['operationalAdmission']is False and document['runtimeAcceptanceClaim']is False
 assert review['schemaVersion']==1 and review['state']=='ROOT_SCHEDULER_RESOURCE342_NORMAL_OFF_VALIDATION_PIN_REVIEW_V1'and review['reviewedPinsSha256']==reviewed_sha
 assert review['resourceSourceIndexSha256']==SOURCE_SHA and review['freezerSourceIndexSha256']==FREEZER_SHA and review['toolingIndex']==expected['toolingIndex']
 assert review['actualExportCandidate']==export_row and review['independentExportReview']==export_review and review['actualArtifactReview']==expected['actualArtifactReview']
 assert review['engineSha256']==ENGINE_SHA and review['metadataSha256']==META_SHA and review['freezeReceiptSha256']==RECEIPT_SHA
 assert review['validationBootstrapOnly']is True and review['otherVariantsNull']is True and review['operationalAdmission']is False and review['runtimeAcceptanceClaim']is False
 return copy.deepcopy(document['variants']['normal-off'])
