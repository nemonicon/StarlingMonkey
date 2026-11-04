from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
assert not(HERE/'index.json').exists()
result=json.loads((HERE/'results.json').read_bytes())
assert result['ownerIndexSha256']=='3929e24d4fe423dc388d3706b975c4704739943b7fcf78c49feb8fda79e03710'
assert result['ownerFiles']==81 and result['preparationInputs']==2146 and result['descriptorShadowM2Resolved']is True
assert result['toolRows']==522 and result['futureStageUniquePlanRows']==869 and result['concreteSourceBlockers']==[]
receipt={'schemaVersion':1,'state':'INDEPENDENT_ZLIB350_V3_SCOPED_SOURCE_SUCCESSOR_REVIEW_PASSED',
 'ownerIndexSha256':result['ownerIndexSha256'],'ownerSourceReceiptSha256':'b671f267e9117b2a638f4f707b5b718620fb3918dac9d16b355097b933fd06e8',
 'ownerPatchSha256':'50316b30121d7068c2bb729557aeb651deb5720648d96bd09a479f6bd8b60024',
 'resultsSha256':sha((HERE/'results.json').read_bytes()),'mandatoryDescriptorAmendmentIndexSha256':result['mandatoryDescriptorAmendmentIndexSha256'],
 'priorHoldIndexSha256':'89bc84d69c17b3959105ef1776c3275981b3bdace2aca7de64a355a1e6aabe1b',
 'ownerFiles':81,'preparationInputs':2146,'mandatoryAmendmentFiles':6,'exactCodecIdentifierChanges':2,
 'descriptorShadowM2Resolved':True,'previousIncludeM1CorrectionRetained':True,
 'native350AndApi40Unchanged':True,'toolRows':522,'nativeToolOverlap':3,'futureStageUniquePlanRows':869,
 'recipeSha256':result['recipeSha256'],'policySha256':result['policySha256'],'helperSha256':result['helperSha256'],
 'storedMockedRegressionChecksAuthenticatedNotRerun':7,'actualCompileSyntaxCommandDataRecords':64,
 'futurePinsAllFourNull':True,'operationalAdmissionOpen':False,'runtimeBackendProof':result['runtimeBackendProof'],
 'nativeStageBuildFreezeGuestLinkRuntimeOrHostEvidenceClaim':False,
 'ownerImportsHelpersTestsActionsNativeVerifiersPreflightsCompilersGuestsHostsOrTimingExecutedByReviewer':False,
 'oldSealedPacketsOrCurrentCheckoutsModified':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,
 'concreteSourceBlockers':[],'scope':result['scope'],'limitations':result['limitations']}
(HERE/'review-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=[]
for p in sorted(HERE.rglob('*')):
 assert not p.is_symlink()
 if not p.is_file():continue
 b=p.read_bytes();b.decode('utf8');files.append({'path':str(p.relative_to(HERE)),'sha256':sha(b),'bytes':len(b)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ZLIB350_V3_SCOPED_SOURCE_REVIEW','files':files,
 'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'runtimeAcceptanceClaim':False,'performanceClaim':False}
(HERE/'index.json').write_text(json.dumps(index,indent=2)+'\n')
for row in files:
 b=(HERE/row['path']).read_bytes();assert sha(b)==row['sha256']and len(b)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],'resultsSha256':receipt['resultsSha256']}))
