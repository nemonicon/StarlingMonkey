"""Seal this read-only GC result review; no artifact/tool action is imported."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
OUTPUT=Path('/tmp/starling-node-compat/consumers355-v2-gc-component-validation-v1')
ROOT=HERE.parent/'gc-component-validation-v1-root-results.json'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def ref(path):return{'path':str(path.relative_to(HERE)),'sha256':sha(path),'bytes':path.stat().st_size}
assert not(HERE/'index.json').exists()
result=json.loads((HERE/'results.json').read_bytes())
assert result['state']=='INDEPENDENT_CONSUMERS355_COMBINED_OWNER_GC_ACTUAL_RESULTS_PASSED'and result['concreteResultBlockers']==[]
assert(HERE/'stderr.log').read_bytes()==b''
stdout=json.loads((HERE/'stdout.log').read_bytes());assert stdout['rawCalls']==6 and stdout['reviewerOwnerActions']is False
assert sha(ROOT)==result['rootReceiptSha256']
root=json.loads(ROOT.read_bytes());assert root['rawExitCode']==0
for key in ['report','completion','component','terminal','authority','reviewedNormalBridge']:
    assert sha(root[key]['path'])==root[key]['sha256']
copies={'root-results.json':ROOT,'gc-results.json':Path(root['report']['path']),'completion.json':Path(root['completion']['path']),'root-terminal.json':Path(root['terminal']['path']),'gc-authority.json':Path(root['authority']['path']),'reviewed-normal-bridge.json':Path(root['reviewedNormalBridge']['path']),'emitted.wit':OUTPUT/'consumer_validation.emitted.wit','consumer_validation.d.ts':OUTPUT/'consumer_validation.d.ts','wasmtime-ordinary-gc.stdout.txt':OUTPUT/'processes/wasmtime-ordinary-gc.stdout.txt','wasmtime-ordinary-gc.terminal.json':OUTPUT/'processes/wasmtime-ordinary-gc.terminal.json'}
for path in sorted((OUTPUT/'calls').glob('*.raw.txt')):copies['calls/'+path.name]=path
evidence=HERE/'evidence';evidence.mkdir()
for name,source in copies.items():
    target=evidence/name;target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb')as stream:stream.write(source.read_bytes())
    assert sha(target)==sha(source)
receipt={'schemaVersion':1,'state':'SEALED_INDEPENDENT_CONSUMERS355_COMBINED_OWNER_GC_RESULTS_PASSED','rootReceiptSha256':result['rootReceiptSha256'],'reviewedNormalBridgeSha256':result['reviewedNormalBridgeSha256'],'sourceFamilyIndexSha256':result['sourceFamilyIndexSha256'],'engineSha256':result['engineSha256'],'componentSha256':result['componentSha256'],'componentBytes':result['componentBytes'],'results':ref(HERE/'results.json'),'reader':ref(HERE/'verify.py'),'readerExit':{'exitCode':0,'observedByThisReader':True,'stdout':ref(HERE/'stdout.log'),'stderr':ref(HERE/'stderr.log')},'rootRawExitCode':0,'fullRawCallsDecoded':6,'gcRecords':4,'retainedGcCounters':[1,2,3],'freshWasmtimeCounter':1,'namespaceObservations':2,'outputRegularFiles':47,'outputLinks':1,'verifiedLexicalPaths':result['verifiedLexicalPaths'],'concreteResultBlockers':[],'strongCombinedOwnersOnly':True,'actualGCCountMeasured':False,'vmTemporaryRootsIsolated':False,'ownerOrGuestActionsInvokedByReviewer':False,'operationalAdmission':False,'fullNodeResetReuseHTTPOrPerformanceClaim':False,'actualAcceptanceOrSourcePromotionIssued':False}
with(HERE/'review-receipt.json').open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
files=[ref(path)for path in sorted(HERE.rglob('*'))if path.is_file()and path.name!='index.json']
with(HERE/'index.json').open('x')as stream:json.dump({'schemaVersion':1,'state':'SEALED_INDEPENDENT_CONSUMERS355_COMBINED_OWNER_GC_RESULTS_PASSED','files':files,'ownerActionsInvoked':False,'operationalAdmission':False},stream,indent=2);stream.write('\n')
print(json.dumps({'indexSha256':sha(HERE/'index.json'),'files':len(files),'receiptSha256':sha(HERE/'review-receipt.json'),'resultsSha256':sha(HERE/'results.json'),'ownerActionsInvoked':False}))
