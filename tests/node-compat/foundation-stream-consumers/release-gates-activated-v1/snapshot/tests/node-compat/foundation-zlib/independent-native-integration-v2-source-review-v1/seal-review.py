from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
assert not(HERE/'index.json').exists()
result=json.loads((HERE/'results.json').read_bytes());assert result['mandatoryFindings'][0]['id']=='Z350-M2'
assert result['ownerFilesRehashed']==77 and result['preparationInputsRehashed']==2048
receipt={'schemaVersion':1,'state':'INDEPENDENT_ZLIB350_V2_SOURCE_HOLD_MANDATORY_DESCRIPTOR_SHADOW_FIX',
 'ownerIndexSha256':result['ownerIndexSha256'],'mandatoryAmendmentIndexSha256':result['mandatoryAmendmentIndexSha256'],
 'resultsSha256':sha((HERE/'results.json').read_bytes()),'descriptorShapeInspectionSha256':sha((HERE/'descriptor-shape-inspection.json').read_bytes()),
 'ownerFiles':77,'preparationInputs':2048,'mandatoryAmendmentFiles':11,'mandatoryAfterimages':6,
 'exactForwardReverseDerivationRecords':result['derivationRecordsForwardAndReverse'],
 'nativeSources':350,'nativePayloadMatchesConditional56a6':True,'nativeAdds':8,'nativeParentChanges':2,'unchangedParentPaths':340,
 'mandatoryFindings':result['mandatoryFindings'],'stageOrBuildPermittedByThisReview':False,
 'originalZ350M1CorrectionPresentButFinalWitnessMalformed':True,'allOtherMechanismsApproved':False,
 'toolInventory':json.loads((HERE/'tool-inventory-clarification.json').read_bytes()),
 'pureExpectedDescriptorShapeInspectionExecuted':True,'ownerFunctionOrActionOrNativeVerifierOrCompilerOrGuestOrTestExecuted':False,
 'old3ffDafaffC65And1d0cUnchanged':True,'runtimeBackendProof':result['runtimeBackendProof'],
 'futurePinsAllFourNull':True,'operationalAdmissionOpen':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,
 'scope':result['reviewScope']}
(HERE/'review-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=[]
for p in sorted(HERE.rglob('*')):
 assert not p.is_symlink()
 if not p.is_file():continue
 b=p.read_bytes();b.decode('utf8');files.append({'path':str(p.relative_to(HERE)),'sha256':sha(b),'bytes':len(b)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ZLIB350_V2_SOURCE_HOLD','files':files,'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'stageOrBuildApproved':False,'runtimeAcceptanceClaim':False,'performanceClaim':False}
(HERE/'index.json').write_text(json.dumps(index,indent=2)+'\n')
for row in files:
 b=(HERE/row['path']).read_bytes();assert sha(b)==row['sha256']and len(b)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],'resultsSha256':receipt['resultsSha256']}))
