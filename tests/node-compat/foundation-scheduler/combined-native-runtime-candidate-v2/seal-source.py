"""Source publication only; no operational imports/actions."""
from pathlib import Path
import ast,json,hashlib
P=Path(__file__).resolve().parent
assert not (P/'index.json').exists()
def row(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
for f in P.glob('*.py'):ast.parse(f.read_text(),filename=str(f))
checks=json.loads((P/'source-check-results.json').read_text());pure=json.loads((P/'checks-final/pure.stdout.log').read_text());fatal=json.loads((P/'checks-final/fatal-classification.stdout.log').read_text());assert fatal['passed']and fatal['fatalCallbackGateSatisfied']is False;context=json.loads((P/'checks-final/context.stdout.log').read_text());closure=json.loads((P/'checks-final/closure.stdout.log').read_text())
terminals=[json.loads(f.read_text())for f in sorted((P/'checks-final').glob('*.terminal.json'))];assert len(terminals)==16 and all(t['rawExitCode']==0 for t in terminals);assert pure['checks']>=140 and checks['checks']>77000
write('results.json',dict(schemaVersion=1,state='COMBINED355_NATIVE_RUNTIME_SOURCE_PREPARED_NO_ACTION_AUTHORITY_V2',sourceOnly=True,authorSourceChecksPassed=True,independentSourceReview=None,rootAuthority=None,sourceChecks=checks,pureChecks=pure,fatalClassificationChecks=fatal,contextChecks=context,moduleClosure=closure,fullMetadataFields=80,nativeSourceFiles=355,externalEmbeddingSources=3,selectedWholeManifests=11,parentNativeApiPlanned=True,childNativeApiInvocations=0,childNativeFrameReturned=False,mappingThenIndependentReviewBeforeGeneratedImport=True,acceptedArtifactIds=['pure','resource','clock-snapshot','surviving-interest','fatal'],otherArtifactReviewSlotsPending=False,initFatalAcceptedComponent=False,initFatalRuntimeBranchImplemented=False,allSixFixturesAccepted=False,all17GatesSatisfied=False,nativeOffsetInterestDropOrTeardownProved=False,syntaxCheckerUsed=True,hostPureModelsExecuted=True,nativeApiInvoked=False,jcoCompilerApiInvoked=False,generatedModuleImported=False,ordinaryGuestExportsInvoked=False,nodeOracleInvoked=False,stockWasmtimeExecuted=False,workerOrMonitorInvoked=False,expectedCallbackFailureProved=False,fatalCallbackGateSatisfied=False,genericFatalObservationsCauseInconclusive=True,current355NativeCallbackDiagnosticAvailable=False,failedPositiveChildParentRegistrationMayBeIncomplete=True,failureReceiptBestEffort=True,completeFailedIndexGuaranteed=False,ownerActionsInvoked=False,hostRuntimeActionsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,actualMappedProof=None,actualRuntimeProof=None))
write('source-receipt.json',dict(schemaVersion=1,state='SOURCE_SEALED_FOR_INDEPENDENT_REVIEW_NOT_ACTIVATED_V2',results=row(P/'results.json'),sourceCheckResults=row(P/'source-check-results.json'),sourceInputs=row(P/'source-inputs.json'),childInputs=row(P/'child-inputs.json'),remainingGates=row(P/'remaining-gates.json'),requirementsReference='Original lifecycleV2 all17 retained; new native357 diagnostics excluded',controls='All Root/action/independent-source/mapped/runtime slots NULL; no actual runtime outputs created',historicalSourceFilesEdited=False))
files=[]
for f in sorted(P.rglob('*')):
 assert not f.is_symlink()
 if f.is_file():files.append(dict(row(f),path=f.relative_to(P).as_posix()))
write('index.json',dict(schemaVersion=1,files=files))
print(json.dumps(dict(index=row(P/'index.json'),result=row(P/'results.json'),receipt=row(P/'source-receipt.json'),members=len(files))))
