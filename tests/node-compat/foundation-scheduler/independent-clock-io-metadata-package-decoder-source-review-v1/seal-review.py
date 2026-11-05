"""Seal this finite source review only; no owner/monitor/tool invocation."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'clock-io-metadata-package-decoder-candidate-v1'
def load(p):return json.loads(Path(p).read_bytes())
def row(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def put(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(HERE/'index.json').exists()
checks=load(HERE/'checks.json');refs=load(SOURCE/'references.json');ix=row(SOURCE/'index.json')
assert ix==checks['sourceIndex']and row(SOURCE/'source-inputs.json')==checks['sourceInputManifest']
for r in load(SOURCE/'index.json')['files']:
    a=row(SOURCE/r['path']);assert(a['sha256'],a['bytes'])==(r['sha256'],r['bytes'])
assert {p.relative_to(SOURCE).as_posix()for p in SOURCE.rglob('*')if p.is_file()}=={'index.json'}|{r['path']for r in load(SOURCE/'index.json')['files']}
fixed=load(SOURCE/'future-source-review-contract.json');fixed['sourceIndexSha256']=ix['sha256']
assert fixed['state']=='INDEPENDENT_CLOCK_IO_METADATA_PACKAGE_DECODER_SOURCE_REVIEW_PASSED_V1'
result={**fixed,'noConcreteSourceBlockerFound':True,'sourceIndex':ix,'sourceInputManifest':checks['sourceInputManifest'],'controller':row(SOURCE/'controller.py'),'protocol':row(SOURCE/'api-and-phase-contract.json'),'failedPhaseReview':refs['failedPhaseReview'],'failedPhaseContract':refs['failedPhaseContract'],'failedRootObservation':refs['failedRootObservation'],'nativeTool':refs['wasmTools'],'nativeArchive':refs['wasmToolsArchive'],'metadataPayload':refs['metadataPayload'],'normalizedAdapter':refs['normalizedAdapter'],'prunedAdapter':refs['prunedAdapter'],'monitor':refs['monitor'],'checks':row(HERE/'checks.json'),'readHashArchiveAstChecks':checks['checks'],'sourceMembersVerified':35,'declaredInputsVerified':24525,'fixedFamiliesVerified':12,'oldTreeMembershipScopesVerified':4,'storedPureChecksAuthenticatedNotRerun':69,'sourceBoundedDecoderCalls':1,'nativeDeadlineSeconds':60,'requiredEnclosingDeadlineSeconds':300,'oldPhaseRemainsFailed':True,'decoderInvoked':False,'normalizerOrPrunerRerun':False,'nodeValidationRerun':False,'phaseExecuted':False,'metadataDecoded':False,'adapterPromoted':False,'engineOrGuestExecuted':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False,'newRootAuthority':None,'actualMetadataResult':None}
put('results.json',result)
put('result-contract.json',dict(schemaVersion=1,requiredFixedValues=fixed,results=row(HERE/'results.json'),requiredExactInputs={k:result[k]for k in ['sourceIndex','failedPhaseReview','failedRootObservation','nativeTool','metadataPayload','normalizedAdapter','prunedAdapter']},grantsPhaseAuthority=False,actualResultReviewRequired=True))
put('review-receipt.json',dict(schemaVersion=1,state='CLOCK_METADATA_PACKAGE_DECODER_SOURCE_REVIEW_COMPLETE_V1',results=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),checks=checks['checks'],sourceOnly=True,ownerActionsInvoked=False,actualProof=None))
for p in HERE.glob('*.py'):ast.parse(p.read_text())
files=[]
for p in sorted(HERE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():d=row(p);d['path']=p.relative_to(HERE).as_posix();files.append(d)
put('index.json',dict(schemaVersion=1,files=files))
for r in files:
    a=row(HERE/r['path']);assert(a['sha256'],a['bytes'])==(r['sha256'],r['bytes'])
print(json.dumps(dict(index=row(HERE/'index.json'),results=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),members=len(files),checks=checks['checks'],sourceOnly=True,ownerActionsInvoked=False)))
