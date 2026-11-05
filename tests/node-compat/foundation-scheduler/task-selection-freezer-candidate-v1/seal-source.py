"""Seal this source proposal only; never runs freezer/helper/checker entry points."""
import hashlib,json
from pathlib import Path
OWN=Path(__file__).resolve().parent
def desc(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def load(p):return json.loads(Path(p).read_bytes())
def write(name,v):(OWN/name).write_text(json.dumps(v,indent=2)+'\n')
def main():
 refs=load(OWN/'references.json');e=load(OWN/'evidence/final/results.json');plan=load(OWN/'capture-plan.json')
 assert e['sourceOnly']and not e['actualAdmissionHelperExecuted']and not e['genuineLayerOrModelImported']and not e['freezerInvoked']and e['fullBuildLedgerRows']==20761
 history=load(OWN/'preparation-history.json');history.update(checkpointState='COMPLETED_SOURCE_ONLY_NO_ACTION',pausedForUserCommitRequest=False,sourceReadyForReviewOrExecution=False,sourceReadyForIndependentReview=True,remaining=[],allToolsTerminalAtCheckpoint=True);write('preparation-history.json',history)
 write('results.json',dict(schemaVersion=1,state='SOURCE_ONLY_TASK_SELECTION342_NORMAL_OFF_FREEZER_CANDIDATE_VALIDATED_NOT_EXECUTED_V1',sourceOnly=True,sourceValidationPassed=True,independentSourceReview=None,taskSelectionSourceIndex=refs['taskSelectionSourceIndex'],actualBuildReview=refs['actualBuildReview'],actualBuildContract=refs['actualBuildContract'],actualEngineData=refs['engine'],actualMetadataData=refs['metadata'],fullBuildInputLedger=refs['buildInputLedger'],fullBuildInputRows=20761,configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],freezeRoot=refs['freezeRoot'],nativeSourceFiles=342,unchangedResourceParentFiles=339,nativeReplacements=3,externalEmbeddingSources=3,selectedManifestCount=9,compileDatabaseRows=67,policyCppCommands=61,otherConfiguredSourceRows=5,generatedNullCppRows=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=5,baseCopyRows=plan['baseCopies'],baseCopyBytes=plan['baseCopyBytes'],dynamicActualCopyCount=None,originalInputsAuthenticatedBeforeCustomImports=True,genuineConfiguredAdmissionApisPreserved=True,metadataRewritten=False,oldNativeOrMetadataProjection=False,helperGlobalsRebound=False,fullRawHelperCapturesBeforeAssertions=True,readOnlyHelpersSourceOnly=True,frozenOnlyVerifierSourcePrepared=True,externalOwnedMonitorSeconds=2400,sourceAdmissionSeconds=600,ninjaCommandsSeconds=120,startFreeBytes=2147483648,stopBelowFreeBytes=838860800,evidence=desc(OWN/'evidence/final/results.json'),sourceIndependentReview=None,rootAuthority=None,actualFreeze=None,actualFrozenArtifactReview=None,export=None,reviewedPins=None,bootstrap=None,runtimeAuthority=None,ownerModulesOrOperationalHelpersInvoked=False,nativeFreezeActionsInvoked=False,engineExecuted=False,componentOrGuestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
 write('source-receipt.json',dict(schemaVersion=1,state='SEALED_SELECTOR342_NORMAL_OFF_FREEZER_SOURCE_RECEIPT_NOT_ACTION_V1',sourceValidation=desc(OWN/'results.json'),evidence=desc(OWN/'evidence/final/results.json'),references=desc(OWN/'references.json'),inputFreeze=desc(OWN/'input-freeze.json'),derivations=desc(OWN/'derivations.json'),apiBindings=desc(OWN/'api-bindings.json'),taskSelectionSourceIndex=refs['taskSelectionSourceIndex'],actualBuildReview=refs['actualBuildReview'],actualFreeze=None,operationalAdmission=False))
 files=[]
 for p in sorted(OWN.rglob('*')):
  if p.is_file()and p.name!='index.json':
   d=desc(p);d['path']=str(p.relative_to(OWN));files.append(d)
 assert not any(p.is_symlink()for p in OWN.rglob('*'))
 write('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_TASK_SELECTION342_NORMAL_OFF_FREEZER_V1',files=files,actualRootAuthority=None,actualFreeze=None,reviewedPins=None,bootstrap=None,runtimeAuthority=None))
 for d in files:
  actual=desc(OWN/d['path']);assert actual['sha256']==d['sha256']and actual['bytes']==d['bytes']
 assert{str(p.relative_to(OWN))for p in OWN.rglob('*')if p.is_file()}=={d['path']for d in files}|{'index.json'}
 print(json.dumps(dict(index=desc(OWN/'index.json'),result=desc(OWN/'results.json'),receipt=desc(OWN/'source-receipt.json'),members=len(files),preparationInputs=len(load(OWN/'input-freeze.json')['files']),sourceChecks=e['checks'],pureModels=e['pureModelCases'],astFiles=e['pythonAstFiles'])))
if __name__=='__main__':main()
