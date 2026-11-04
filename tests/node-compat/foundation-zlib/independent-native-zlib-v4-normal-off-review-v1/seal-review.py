"""Seal this textual actual-native review after a fresh external-byte rehash."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
assert not(HERE/'index.json').exists()
result=json.loads((HERE/'results.json').read_bytes())
assert result['engineSha256']=='fb16568958f4948cb78aa53818637535b88a0d87a25eb74923798fdc80cac1e6'and result['engineBytes']==9995295
assert result['freezeReceiptSha256']=='e5e705c886392bc5db137581b3492d72080e101460ec670f27281a1dbd964f11'
assert result['frozenCopiesObserved']==1024 and result['originalCopiesRehashed']==1022
assert result['nativeSources']==350 and result['externalEmbeddingSources']==3 and result['toolDependencyRows']==632
assert result['nativeCompileCommands']==62 and result['strictCompileCommands']==4 and result['privateCompileCommands']==6 and result['separateNoLtoEmbeddingCompileCommands']==1
assert result['opensslCompleteSourcesIndependentlyRehashed']==4650 and result['concreteBlockers']==[]
for row in result['verifiedFiles']:
 path=Path(row['path']);assert path.is_file()and not path.is_symlink();value=hashlib.sha256()
 with path.open('rb')as source:
  for block in iter(lambda:source.read(1024*1024),b''):value.update(block)
 assert value.hexdigest()==row['sha256']and path.stat().st_size==row['bytes'],path
receipt={'schemaVersion':1,'state':'INDEPENDENT_ZLIB_V4_NORMAL_OFF_NATIVE_BUILD_FREEZE_REVIEW_PASSED',
 'sourceIndexSha256':result['sourceIndexSha256'],'rootReceiptSha256':result['rootReceiptSha256'],
 'rootReportedRawTerminals':{'buildSession':69972,'buildExit':0,'freezeSession':30705,'freezeExit':0,'verifySession':85956,'verifyExit':0,'observedByThisReader':False},
 'engineSha256':result['engineSha256'],'engineBytes':result['engineBytes'],'metadataSha256':result['metadataSha256'],'freezeReceiptSha256':result['freezeReceiptSha256'],
 'resultsSha256':sha((HERE/'results.json').read_bytes()),'recipeSha256':result['recipeSha256'],'policySha256':result['policySha256'],'helperSha256':result['helperSha256'],
 'frozenCopiesObserved':1024,'originalCopiesRehashed':1022,'nativeSources':350,'externalEmbeddingSources':3,'toolDependencyRows':632,'originalContextPreparationInputs':2261,
 'nativeCompileCommands':62,'strictCompileCommands':4,'privateCompileCommands':6,'separateNoLtoEmbeddingCompileCommands':1,
 'codecWitnessFiles':9,'rawLinkCaptureBytes':result['rawLinkCaptureBytes'],'rawLinkSelectedLineOneBased':107,'rawLinkResponseFiles':0,'rawLinkSameOutputProved':True,
 'selectedArchiveSha256':result['selectedArchiveSha256'],'selectedArchiveBytes':538170426,'selectedHeaderCount':4,'mozZSymbolDefinitions':7,
 'opensslCompleteSourcesIndependentlyRehashed':4650,'rootEvidenceReferences':14,
 'sourceAdmissionRecordAuthenticatedNotRerun':True,'normalOperationalAdmissionOpen':False,'runtimeBootstrapPinsNull':True,'runtimeBackendProof':result['runtimeBackendProof'],
 'ownerImportsHelpersTestsNativeVerifiersNinjaNmCompilerGuestsHostsOrTimingExecuted':False,
 'oldSealedPacketsOrCheckoutsModified':False,'oldV3UnadmittedOutputPromoted':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'concreteBlockers':[],
 'scope':'Completed normal-OFF native build/freeze only; no other350 variant, codec execution or public component/runtime approval.',
 'limitations':result['limitations']}
with(HERE/'review-receipt.json').open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
files=[]
for path in sorted(HERE.rglob('*')):
 assert not path.is_symlink()
 if not path.is_file():continue
 data=path.read_bytes();data.decode('utf8');files.append({'path':str(path.relative_to(HERE)),'sha256':sha(data),'bytes':len(data)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ZLIB_V4_NORMAL_OFF_NATIVE_BUILD_FREEZE_REVIEW','files':files,'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'runtimeAcceptanceClaim':False,'performanceClaim':False}
with(HERE/'index.json').open('x')as stream:json.dump(index,stream,indent=2);stream.write('\n')
for row in files:
 data=(HERE/row['path']).read_bytes();assert sha(data)==row['sha256']and len(data)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],'resultsSha256':receipt['resultsSha256']}))
