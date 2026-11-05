"""New pure combined80 frame/pin contracts. No reads, imports of helpers or actions."""
import copy
LABELS=('normal-off','normal-runtime','gc-off','disabled-off')
NATIVE='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65'
FREEZER='5230be984948519000c818450ada155917097ca26f259ee37dbcc3bb36728a4b'
ENGINE='355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b'
METADATA='5f3be8851739635beaee6550ad03c7afed9e6eebb0607840ebd12e4a095354d3'
RECEIPT='9ce681402425f2bc59134bec5b48c98ee20fe15d42abf7ecaa1df920e05fded4'

def native_frame(capsule,receipt,metadata,manifests,refs,index):
 assert capsule['schemaVersion']==1 and capsule['state']=='COMBINED355_NORMAL_FREEZE_READ_ONLY_CAPSULE_VERIFIED_NOT_ACCEPTED_V1'
 assert capsule['receipt']==refs['freezeReceipt'] and capsule['engine']==refs['engine'] and capsule['metadata']==refs['metadata']
 assert capsule['copies']==len(receipt['copies'])==2596 and capsule['nativeSourceFiles']==355 and capsule['externalEmbeddingSources']==3 and capsule['selectedManifests']==11 and capsule['rawMetadataFields']==80
 assert refs['nativeSourceIndex']['sha256']==receipt['nativeSourceIndexSha256']==NATIVE and refs['freezerSourceIndex']['sha256']==receipt['freezerSourceIndexSha256']==FREEZER
 assert refs['engine']['sha256']==metadata['engineSha256']==ENGINE and refs['metadata']['sha256']==METADATA and refs['freezeReceipt']['sha256']==RECEIPT
 assert len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==len(manifests)==11
 assert refs['selectedManifestRows']==metadata['selectedModuleManifests'] and len({r['path'] for r in refs['selectedManifestRows']})==11
 assert all(type(v)is dict and type(v['modules'])is dict for v in manifests)
 assert all(v['profileVersion']==r['profileVersion'] for v,r in zip(manifests,metadata['selectedModuleManifests']))
 for field in ['configuredSourceRoot','workRoot']:
  assert receipt[field]==refs[field]==metadata['combinedNativeSourcePolicy'][field]
 assert receipt['sourceRoot']==refs['frozenSourceRoot'] and receipt['componentizeSourceRoot']==refs['componentizeSourceRoot']
 assert metadata['gcStress'] is metadata['oomTesting'] is False and metadata['entropyPolicy']=='off' and metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE']=='Release'
 assert receipt['rawMetadataBytesUnchanged'] is receipt['rawMetadataOriginalConfiguredPathsPreserved'] is True
 assert receipt['historicalPreinstallSettingsRawBytesSeparatelyRetained'] is False
 assert receipt['privateRustupBootstrapPolicy']==metadata['privateRustupBootstrapPolicy'] and metadata['privateRustupBootstrapPolicy']['settingsAtBuildCompletion']['bytes']==107
 assert metadata['zlibPolicy']['runtimeBackendProof']==receipt['runtimeBackendProof']==dict(verified=False,version=None,vernum=None)
 assert metadata['zlibErrorSemanticsPolicy']['remainingRecordedDifferences']==15 and metadata['zlibErrorSemanticsPolicy']['remainingDeviationsApproved'] is False
 for key,n in [('compileDatabaseRows',68),('policyCppCommands',62),('otherConfiguredSourceRows',5),('generatedNullCppRows',1),('separatePostBuildEmbeddingCommands',1),('actualStrictCommands',4),('actualPrivateClassicCommands',6)]:assert receipt[key]==n
 return copy.deepcopy(dict(schemaVersion=1,state='COMBINED355_FROZEN_FULL80_NATIVE_DATA_VERIFIED_NO_ACTION_AUTHORITY_V1',variant='normal-off',toolingIndex=index,nativeSourceIndex=refs['nativeSourceIndex'],retryBuildControllerIndex=refs['retryBuildControllerIndex'],freezerSourceIndex=refs['freezerSourceIndex'],activeVerifier=refs['activeVerifier'],actualFrozenReview=refs['actualFrozenReview'],verificationCapsule=capsule,engine=refs['engine'],enginePath=refs['engine']['path'],metadataDescriptor=refs['metadata'],metadata=metadata,freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=80,selectedManifestPaths=[r['path'] for r in metadata['selectedModuleManifests']],selectedManifests=manifests,configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],sourceRoot=refs['frozenSourceRoot'],frozenRoot=refs['frozenRoot'],componentizeSourceRoot=refs['componentizeSourceRoot'],rawMetadataPathsPreserved=True,privateRustupBootstrapPolicy=metadata['privateRustupBootstrapPolicy'],historical57SettingBytesSeparatelyRetained=False,verifiedOriginalReferencesNotAllPhysicallyCopied=True,runtimeBackendProof=receipt['runtimeBackendProof'],remaining15DeviationsApproved=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsActionAuthority=False))

def candidate(frame,receipt,refs,index):
 assert frame['state']=='COMBINED355_FROZEN_FULL80_NATIVE_DATA_VERIFIED_NO_ACTION_AUTHORITY_V1' and frame['toolingIndex']==index
 assert frame['engine']==refs['engine'] and frame['metadataDescriptor']==refs['metadata'] and frame['freezeReceipt']==refs['freezeReceipt']
 return copy.deepcopy(dict(schemaVersion=1,state='unreviewed-combined355-normal-off-pin-v1',reviewRequired=True,variant='normal-off',toolingIndex=index,nativeFrame=frame,engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=80,frozenFiles=[{k:r[k] for k in ('path','sha256','bytes')} for r in receipt['copies']],actualFrozenReview=refs['actualFrozenReview'],validationBootstrapOnly=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False))

def unreviewed_document(pin):
 assert pin['state']=='unreviewed-combined355-normal-off-pin-v1' and pin['reviewRequired'] is True
 return dict(schemaVersion=1,state='UNREVIEWED_COMBINED355_NORMAL_OFF_PIN_CANDIDATE_V1',toolingIndex=copy.deepcopy(pin['toolingIndex']),reviewRequired=True,variants={k:copy.deepcopy(pin) if k=='normal-off' else None for k in LABELS},validationBootstrapOnly=True,operationalAdmission=False,runtimeAcceptanceClaim=False)

def reviewed_document(value):
 """Only documented state/flag transformation, not a reviewer or action."""
 value=copy.deepcopy(value);assert value['state']=='UNREVIEWED_COMBINED355_NORMAL_OFF_PIN_CANDIDATE_V1' and value['reviewRequired'] is True
 assert set(value['variants'])==set(LABELS) and all(value['variants'][k] is None for k in LABELS if k!='normal-off')
 value['state']='ROOT_REVIEWED_COMBINED355_NORMAL_OFF_VALIDATION_PINS_V1';value['reviewRequired']=False
 pin=value['variants']['normal-off'];assert pin['state']=='unreviewed-combined355-normal-off-pin-v1' and pin['reviewRequired'] is True
 pin['state']='reviewed-combined355-normal-off-pin-v1';pin['reviewRequired']=False;return value

def select_reviewed(document,review,expected,root,refs,index):
 assert document==reviewed_document(unreviewed_document(expected))
 assert review['schemaVersion']==1 and review['state']=='ROOT_COMBINED355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V1'
 for key,value in dict(toolingIndex=index,reviewedPins=root['reviewedPins'],actualExportCandidate=root['actualExportCandidate'],independentExportReview=root['independentExportReview'],actualFrozenReview=refs['actualFrozenReview'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=80).items():assert review[key]==value
 assert review['validationBootstrapOnly'] is review['otherVariantsNull'] is True
 for key in ('engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed'):assert review[key] is False
 return copy.deepcopy(document['variants']['normal-off'])

def bootstrap_frame(pin,frame,refs,index,root_row,config_row,root):
 assert pin['nativeFrame']==frame and pin['state']=='reviewed-combined355-normal-off-pin-v1' and pin['reviewRequired'] is False
 return copy.deepcopy(dict(schemaVersion=1,state='COMBINED355_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V1',variant='normal-off',toolingIndex=index,rootAuthority=root_row,config=config_row,nativeFrame=frame,pin=pin,engine=refs['engine'],enginePath=refs['engine']['path'],metadataDescriptor=refs['metadata'],metadata=frame['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceIndex=refs['nativeSourceIndex'],retryBuildControllerIndex=refs['retryBuildControllerIndex'],freezerSourceIndex=refs['freezerSourceIndex'],actualFrozenReview=refs['actualFrozenReview'],actualExportCandidate=root['actualExportCandidate'],independentExportReview=root['independentExportReview'],reviewedPins=root['reviewedPins'],rootPinReview=root['rootPinReview'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=80,selectedManifestPaths=frame['selectedManifestPaths'],selectedManifests=frame['selectedManifests'],configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],sourceRoot=refs['frozenSourceRoot'],componentizeSourceRoot=refs['componentizeSourceRoot'],frozenRoot=refs['frozenRoot'],originalToolingRoot=refs['originalToolingRoot'],currentFrozenVerifierCalls=1,validationBootstrapOnly=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsRuntimeAuthority=False))
