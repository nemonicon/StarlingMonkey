"""Seal this new textual review only; no owner source/action imports."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def doc(n):return json.loads((HERE/n).read_bytes())
assert not(HERE/'index.json').exists()
family=doc('results.json');on=doc('native-on-results.json');off=doc('native-off-results.json')
assert family['generatedFiles']==35 and family['consumedInputs']==7709 and family['concreteBlockers']==[]
assert family['futureTimingPhaseAllNull']is True and family['pairAuthorityPresent']is True
for n in [on,off]:assert n['frozenCopies']==525 and n['originalCopiesRehashed']==521 and n['nativeInputs']==342 and n['addonInputs']==2
evidence={}
for rows in [doc('evidence.json')['files'],on['verifiedFiles'],off['verifiedFiles']]:
 for row in rows:
  assert row['path']not in evidence or evidence[row['path']]==row
  evidence[row['path']]=row
raw=(json.dumps({'schemaVersion':1,'files':sorted(evidence.values(),key=lambda r:r['path']),
 'scope':'Unique path strings, not unique inodes. Binary data remains external with SHA256/size.'},indent=2)+'\n').encode()
(HERE/'all-evidence.json').write_bytes(raw)
receipt={'schemaVersion':1,'state':'INDEPENDENT_ACTUAL_COMMON_BYTE_V2_SOURCE_FAMILY_REVIEW_PASSED_NO_GUEST',
 'sourceIndexSha256':family['actualIndexSha256'],'rootReceiptSha256':'0a600573f83019ef33d566eac08b9f027bda00cb130c68be65091ee5843a4e37',
 'pairPinsSha256':family['pairPinsSha256'],'rootPairReviewSha256':family['rootPairReviewSha256'],
 'resultsSha256':sha((HERE/'results.json').read_bytes()),'nativeOnResultsSha256':sha((HERE/'native-on-results.json').read_bytes()),
 'nativeOffResultsSha256':sha((HERE/'native-off-results.json').read_bytes()),'allEvidenceSha256':sha(raw),
 'sourceFiles':35,'consumedInputs':7709,'toolTrees':2,'toolLinks':22,'nativeVariants':2,'frozenCopiesPerVariant':525,
 'originalReferencesPerVariant':521,'nativeSources':342,'diagnosticAddonSources':2,'externalEmbeddingSources':3,
 'copiedConsumedPayloads':32,'reversibleHostAfterimages':3,'reversiblePublisherEdits':5,'ownedHelperCeilingChanges':1,
 'commonNodeRows':8,'originalControlRows':6,'fourArms':4,'commonGuestCorrectnessStatus':'NOT_EXECUTED',
 'actualPairAuthorityPresent':True,'originalOnOnlyAuthorityUnchanged':True,'futureTimingPhaseAllNull':True,
 'rootReportedTerminals':family['rootReportedTerminals'],'readersExecuted':['owned pure Python source/hash/data readers only'],
 'ownerActionsOrNativeVerifiersOrNodeOrBundlesOrGuestsOrHostsOrTestsOrTimingExecutedByReviewer':False,
 'sourceAndOwnerEvidenceModified':False,'readerHistoryPreserved':True,'concreteBlockers':[],
 'timingAllowed':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'limitations':family['limitations']}
(HERE/'review-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=[]
for p in sorted(HERE.rglob('*')):
 assert not p.is_symlink()
 if not p.is_file():continue
 b=p.read_bytes();b.decode('utf8');files.append({'path':str(p.relative_to(HERE)),'sha256':sha(b),'bytes':len(b)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_COMMON_BYTE_V2_SOURCE_FAMILY_REVIEW','files':files,
 'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),'timingAllowed':False,'runtimeAcceptanceClaim':False,'performanceClaim':False}
(HERE/'index.json').write_text(json.dumps(index,indent=2)+'\n')
for row in files:
 b=(HERE/row['path']).read_bytes();assert sha(b)==row['sha256']and len(b)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],
 'resultsSha256':receipt['resultsSha256'],'allEvidencePaths':len(evidence)}))
