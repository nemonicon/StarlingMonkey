"""Seal only this new textual independent review packet after successful readers."""
from pathlib import Path
import hashlib,json

HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def doc(name):return json.loads((HERE/name).read_bytes())
assert not (HERE/'index.json').exists() and not (HERE/'review-receipt.json').exists()
source=doc('source-results.json');native=doc('native-results.json');actual=doc('results.json')
assert source['generatedFiles']==22 and source['consumedInputs']==7542 and source['frozenCopies']==525
assert native['frozenCopies']==525 and native['originalCopiesRehashed']==521 and native['nativeInputs']==342 and native['addonInputs']==2
assert actual['individualReturnedObservations']==105 and actual['wasmtimeRawIndependentlyDoubleDecoded']==21 and actual['completionFiles']==632
assert actual['rootReportedRawTerminal']['observedByThisReader'] is False
evidence={}
for rows in [doc('source-evidence.json')['files'],native['verifiedFiles'],doc('verified-paths.json')['files']]:
    for row in rows:
        assert set(row)=={'path','sha256','bytes'}
        assert row['path'] not in evidence or evidence[row['path']]==row
        evidence[row['path']]=row
external=(json.dumps({'schemaVersion':1,'files':sorted(evidence.values(),key=lambda x:x['path']),
 'scope':'Unique path strings, not unique inodes; all binary artifacts remain external hash/size references.'},indent=2)+'\n').encode()
(HERE/'evidence.json').write_bytes(external)
receipt={'schemaVersion':1,'state':'INDEPENDENT_ACTUAL_WORKLOAD_V2_FULL_TWENTY_AND_FOURTEEN_REVIEW_PASSED',
 'rootReceiptSha256':actual['rootReceiptSha256'],'sourceIndexSha256':actual['sourceIndexSha256'],
 'sourcePeerIndexSha256':'c30b596aa67d91297b93273a65f38529a67d4c5e2a79dfcad5659bf338528407',
 'resultsSha256':sha((HERE/'results.json').read_bytes()),'sourceResultsSha256':sha((HERE/'source-results.json').read_bytes()),
 'nativeResultsSha256':sha((HERE/'native-results.json').read_bytes()),'externalEvidenceSha256':sha(external),
 'sourceFiles':22,'consumedInputs':7542,'toolTrees':2,'toolLinks':22,'frozenCopies':525,'recordedOriginalsRehashed':521,
 'nativeSources':342,'diagnosticAddonSources':2,'externalEmbeddingSources':3,
 'outputCompletionFiles':632,'componentOccurrences':1,'componentSha256':actual['componentSha256'],
 'componentBytes':actual['componentBytes'],'engineSha256':actual['engineSha256'],'emittedImports':[],
 'workloadRows':20,'boundaryObservationsPerBoundaryReturn':14,'retainedRotations':3,'freshJcoRotations':1,
 'freshWasmtimeCalls':21,'returnedRecords':105,'independentlyDecodedJcoRawReturns':84,'independentlyDoubleDecodedWasmtimeRawReturns':21,
 'processTerminalRecordsIncludingVersion':22,'progressRecords':322,'rootReportedRawTerminal':actual['rootReportedRawTerminal'],
 'actionsExecutedByReviewer':['owned pure Python file/hash/source/data readers','pinned static wasm-tools component wit'],
 'runtimeOrGuestOrNodeOrNativeOrOwnerActionOrPreflightOrTestsExecutedByReviewer':False,
 'sourceAndOwnerEvidenceModified':False,'oldResultsReused':False,'readerHistoryPreserved':True,
 'nativeQueueCounterVisibility':False,'scheduledCallbacksScope':'Original explicit workload counter only; no native queue/work/empty instrumentation.',
 'runtimeAcceptanceClaim':False,'performanceClaim':False,'gcOrRootIsolationClaim':False,'resetAlsOrRequestReuseClaim':False,
 'limitations':actual['limitations']}
(HERE/'review-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=[]
for path in sorted(HERE.rglob('*')):
    assert not path.is_symlink(),path
    if not path.is_file():continue
    raw=path.read_bytes();raw.decode('utf-8')
    assert path.name!='index.json'
    files.append({'path':str(path.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
index={'schemaVersion':1,'state':'SEALED_INDEPENDENT_ACTUAL_WORKLOAD_V2_RESULTS_REVIEW',
 'files':files,'receiptSha256':sha((HERE/'review-receipt.json').read_bytes()),
 'runtimeAcceptanceClaim':False,'performanceClaim':False}
raw=(json.dumps(index,indent=2)+'\n').encode();(HERE/'index.json').write_bytes(raw)
for row in files:
    raw=(HERE/row['path']).read_bytes();assert sha(raw)==row['sha256'] and len(raw)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'receiptSha256':index['receiptSha256'],
 'resultsSha256':receipt['resultsSha256'],'sourceResultsSha256':receipt['sourceResultsSha256'],'nativeResultsSha256':receipt['nativeResultsSha256'],
 'externalPathStrings':len(evidence)}))
