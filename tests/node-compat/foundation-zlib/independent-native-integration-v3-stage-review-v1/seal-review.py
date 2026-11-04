from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
assert not(HERE/'index.json').exists()
result=json.loads((HERE/'results.json').read_bytes())
assert result['exactCopiedUniquePlanRows']==869 and result['rootEvidenceReferences']==41
assert result['nativeSources']==350 and result['toolRows']==522 and result['physicalMembershipExact']is True
receipt={'schemaVersion':1,'state':'INDEPENDENT_ACTUAL_ZLIB350_V3_ISOLATED_SOURCE_STAGE_REVIEW_PASSED',
 'rootReceiptSha256':result['rootReceiptSha256'],'sourceIndexSha256':result['sourceIndexSha256'],
 'sourceReviewIndexSha256':'f471ec276ce05ef3d80c90af8a30da25933663452dec2b9728ebc111a3a0013e',
 'resultsSha256':sha((HERE/'results.json').read_bytes()),'gitTreeSha256':sha((HERE/'git-tree.json').read_bytes()),
 'stageReceiptSha256':result['stageReceiptSha256'],'stageRoot':result['stageRoot'],'rootEvidenceReferences':41,
 'nativeSources':350,'toolRows':522,'nativeToolOverlap':3,'exactCopiedUniquePlanRows':869,'indexedProposalFiles':81,
 'originalPreparationInputsRehashed':2146,'preparedReferencesRelocatedOrReinterpreted':False,
 'sourceOriginalsAndCopiesExact':True,'copiesHaveIndependentInodes':True,'gitBase':result['gitBase'],
 'ordinarySeparateGitClone':True,'gitBaseRows':result['gitReadOnlyTreeRows'],'inheritedEntriesOutsideOverlaysUnchanged':result['inheritedGitEntriesUnchanged'],
 'physicalMembershipExact':True,'c92FixAndForcedIncludeBytesExact':True,'futurePinsAllFourNull':True,
 'rootReportedRawTerminals':result['rootReportedRawTerminals'],'ownerChecksAuthenticatedNotRerun':result['rootRecordedSourceChecksAuthenticatedNotRerun'],
 'reviewerActions':result['reviewerActions'],'ownerHelperStageMainTestsFactoryBootstrapNativeVerifierBuildCompilerGuestOrHostExecutedByReviewer':False,
 'nativeBuildOrRuntimeProof':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'concreteStageBlockers':[],
 'limitations':result['limitations']}
(HERE/'review-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=[]
for p in sorted(HERE.rglob('*')):
 assert not p.is_symlink()
 if not p.is_file():continue
 b=p.read_bytes();b.decode('utf8');files.append({'path':str(p.relative_to(HERE)),'sha256':sha(b),'bytes':len(b)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ZLIB350_V3_ACTUAL_STAGE_REVIEW','files':files,
 'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'nativeBuildOrRuntimeClaim':False,'runtimeAcceptanceClaim':False,'performanceClaim':False}
(HERE/'index.json').write_text(json.dumps(index,indent=2)+'\n')
for row in files:
 b=(HERE/row['path']).read_bytes();assert sha(b)==row['sha256']and len(b)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],'resultsSha256':receipt['resultsSha256']}))
