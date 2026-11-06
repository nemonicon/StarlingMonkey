"""Bounded Source review publication only; no author/operational entry is called."""
from pathlib import Path
import json,hashlib,ast
O=Path(__file__).resolve().parent;S=O.parent/'combined-native-runtime-candidate-v2'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def desc(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def read(p):return json.loads(p.read_bytes())
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def need(v,m):
 if not v:raise AssertionError(m)
need(not(O/'index.json').exists(),'fresh Source review root')
source_index=desc(S/'index.json');need(source_index['sha256']=='1cda0bd6ae2f0d1a5cde1502bd58842cde06580e3249e9ae94135d6cf8b55f36'and source_index['bytes']==30102,'actual final Source tuple')
si=read(S/'index.json');names={'index.json'}
for r in si['files']:
 p=S/r['path'];need(desc(p)==dict(r,path=str(p)),'every final owner Source byte stable');names.add(r['path'])
need({p.relative_to(S).as_posix()for p in S.rglob('*')if p.is_file()}==names and len(names)==176,'exact whole held Source membership; no self-writing author tests')
for p in O.glob('*.py'):ast.parse(p.read_text())
intake=read(O/'intake-summary.json');need(intake['sourceIndex']==source_index and intake['derivationFiles']==28 and intake['exactForwardInverseEdits']==70,'independent declared Source intake')
evidence={}
for key in ['intake-2','independent-pure','author-pure','author-fatal-cases','actual-own-context','source-module-closure']:
 base=O/'evidence'/key;terminal=read(base/'terminal.json');need(terminal['rawExitCode']==0 and(base/'stderr.log').read_bytes()==b'','all final read/pure/context/AST checks raw0');evidence[key]=dict(stdout=desc(base/'stdout.log'),stderr=desc(base/'stderr.log'),terminal=desc(base/'terminal.json'))
pure=read(O/'evidence/independent-pure/stdout.log');need(pure['checks']==68 and pure['legacyExpectedAndUnrelatedAccepted']==2 and pure['expectedCallbackFailureProved']is pure['fatalCallbackGateSatisfied']is False and pure['getterReads']==0,'meaningful actual capture/cause counterexamples')
closure=read(O/'evidence/source-module-closure/stdout.log');prepared=read(S/'results.json');need(closure==prepared['moduleClosure']and closure['ownModules']==12 and len(closure['staticEdges'])==24,'actual imported module inventory matches declared authenticated graph')
for k in ['nativeApiInvoked','jcoCompilerApiInvoked','generatedModuleImported','ordinaryGuestExportsInvoked','nodeOracleInvoked','stockWasmtimeExecuted','workerOrMonitorInvoked','expectedCallbackFailureProved','fatalCallbackGateSatisfied','current355NativeCallbackDiagnosticAvailable','allSixFixturesAccepted','all17GatesSatisfied']:
 need(prepared[k]is False,'Source scope remains closed '+k)
need(prepared['rootAuthority']is prepared['independentSourceReview']is prepared['actualMappedProof']is prepared['actualRuntimeProof']is None,'new activation and results remainNULL')
need(prepared['failureReceiptBestEffort']is True and prepared['completeFailedIndexGuaranteed']is False,'explicit inherited failure receipt limit')
fixed=dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_NATIVE_RUNTIME_SOURCE_REVIEW_PASSED_V2',sourceIndexSha256=source_index['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False,rootAuthorityIssued=False,actualRuntimeProof=None)
result=dict(fixed,sourceIndex=source_index,sourceResult=desc(S/'results.json'),sourceReceipt=desc(S/'source-receipt.json'),sourceIndependentReviewRequiredContract=desc(S/'future-source-review-contract.json'),fullMetadataFields=80,nativeSourceFiles=355,externalEmbeddingSources=3,selectedWholeManifests=11,declaredSourceIntake=desc(O/'intake-summary.json'),readHashChecks=intake['checks'],currentFullHashFiles=intake['currentFullHashFiles'],currentLogicalBytes=intake['currentLogicalBytes'],currentFamilies=intake['currentFamilies'],exactForwardInverseFiles=28,exactForwardInverseEdits=70,childNativeApiInvocations=0,childNativeFrameReturned=False,mappingThenIndependentReviewBeforeGeneratedImport=True,parentOnlyGenuineC365Api=True,positiveResourceCoverage=dict(rawPublicStrings=35,runRecords=49,callbackObservations=98,newIds=322),acceptedArtifactIds=['pure','resource','fatal','clock-snapshot','surviving-interest'],initFatalAcceptedComponent=False,allSixFixturesAccepted=False,all17GatesSatisfied=False,expectedCallbackFailureProved=False,fatalCallbackGateSatisfied=False,genericJcoFatalCause='inconclusive',fatalGatePassContractExposed=False,wasmtimeSourceMarkerRequirementPreserved=True,current355NativeCallbackDiagnosticAvailable=False,failedPositiveChildParentRegistrationMayBeIncomplete=True,failureReceiptBestEffort=True,completeFailedIndexGuaranteed=False,independentPureChecks=68,authorPureChecksReplayed=164,authorFatalCasesReplayed=42,actualOwnContextChecks=13,ownModuleCount=12,staticImportEdges=24,actualOperationalActionsByReviewer=False,hostPureAndAstOnly=True,authorSelfWritingSourceCheckerInvoked=False,evidence=evidence,limitations=['Only Source review; no actual mapped/runtime output/authority','Generic armed throw/trap/SIGABRT observation is cause-inconclusive/unaccepted, never expected callback proof','WT diagnostic requirement stays source-specific; no invented current355 diagnostic channel','Failed positive child physical raw can remain outside parent registry; failure.json best-effort, no guaranteed complete failed index','Worker finally unproved after abort; parent final/native Source audit is separate','No full17/native offset/interest/drop/teardown/GC/reset/reuse/ALS/fullNext/performance/adoption proof'])
write(O/'results.json',result)
write(O/'result-contract.json',dict(schemaVersion=1,requiredReviewState=fixed['state'],requiredFixedValues={k:v for k,v in fixed.items()if k!='state'},requiredExactDescriptors={k:result[k]for k in ['sourceIndex','sourceResult','sourceReceipt','declaredSourceIntake']},scope='SOURCE-only bounded genuineV2 fatal-cause correction and unchanged complete positive harness; no actual runtime permission',issuesAnyActionOrRuntimeAuthority=False))
write(O/'receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_COMBINED355_RUNTIME_V2_SOURCE_REVIEW_V1',sourceIndex=source_index,result=desc(O/'results.json'),contract=desc(O/'result-contract.json'),fullCurrentDeclaredBoundaryRehashed=True,ownerSourceExactMembership=True,newSourceOrRootActionIssued=False,reviewerHostPureAndAstOnly=True,allTargetActionsInvoked=False,ownIndexExcludesOnlyOwnRootIndex=True,history=desc(O/'reader-history.json')))
payloads=[p for p in sorted(O.rglob('*'))if p.is_file()and p not in [O/'index.json',O/'member-ledger.json']]
write(O/'member-ledger.json',dict(schemaVersion=1,scope='all own payloads except this ledger and own root index; nested index files remain included',files=[dict(path=p.relative_to(O).as_posix(),sha256=sha(p),bytes=p.stat().st_size)for p in payloads]))
files=[p for p in sorted(O.rglob('*'))if p.is_file()and p!=O/'index.json'];need(not any(p.is_symlink()for p in O.rglob('*')),'ordinary own source review members')
index=dict(schemaVersion=1,files=[dict(path=p.relative_to(O).as_posix(),sha256=sha(p),bytes=p.stat().st_size)for p in files]);write(O/'index.json',index)
need({p.relative_to(O).as_posix()for p in O.rglob('*')if p.is_file()}=={'index.json',*[r['path']for r in index['files']]},'exact closed own publication')
for r in index['files']:need(desc(O/r['path'])==dict(r,path=str(O/r['path'])),'every own final byte matches')
print(json.dumps(dict(index=desc(O/'index.json'),result=desc(O/'results.json'),contract=desc(O/'result-contract.json'),receipt=desc(O/'receipt.json'),indexedFiles=len(files),actualFiles=len(files)+1,logicalBytes=sum(p.stat().st_size for p in O.rglob('*')if p.is_file())),indent=2))
