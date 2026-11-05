"""Seal this source proposal only. Never import helpers or invoke a process."""
from pathlib import Path
import ast
import hashlib
import json

OWN=Path(__file__).resolve().parent
assert OWN==Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1')
def descriptor(path):
    p=Path(path);assert p.is_file()and not p.is_symlink()
    a=p.stat();raw=p.read_bytes();b=p.stat()
    assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns)
    return dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def write(name,value):
    with (OWN/name).open('x')as out:json.dump(value,out,indent=2);out.write('\n')
assert not(OWN/'index.json').exists()
freeze=json.loads((OWN/'input-freeze.json').read_bytes())
for row in freeze['files']:assert descriptor(row['path'])==row
checks=json.loads((OWN/'source-check-results.json').read_bytes())
parse=json.loads((OWN/'syntax-evidence.json').read_bytes())
assert parse['rawExitCode']==0 and parse['scriptExecuted']is False and parse['ownerHelperOrBuildOrGuestInvoked']is False
assert parse['parsedSourceSha256']==descriptor(OWN/'proposed/tests/node-compat/build-engine.sh')['sha256']
assert checks['state']=='TASK_SELECTION_INTEGRATION_SOURCE_DATA_PURE_CHECKS_PASSED_V1'
assert checks['preparationInputRows']==len(freeze['files'])==540
assert checks['actualNativeSources']==342 and checks['unchangedResourceSources']==339
assert checks['stageOrConfigureOrCompilerOrNativeInvoked']is False and checks['engineOrGuestOrRuntimeInvoked']is False
syntax=[]
for p in OWN.glob('*.py'):ast.parse(p.read_bytes());syntax.append(p.name)
policy=json.loads((OWN/'policy.json').read_bytes())
stage=json.loads((OWN/'stage-inputs.json').read_bytes())
for row in stage['files']:assert descriptor(row['original']['path'])==row['original']
results=dict(schemaVersion=1,state='UNAPPLIED_TASK_SELECTION342_INTEGRATION_SOURCE_PREPARED_V1',sourceOnly=True,sourcePreparationPassed=True,
    sourceIndexSha256=None,independentSourceReview=None,resourceSourceIndexSha256=policy['taskSelectionSourcePolicy']['parentIntegrationIndexSha256'],
    selectorSourceIndexSha256=policy['taskSelectionSourcePolicy']['sourceCandidateIndexSha256'],selectorSourceReviewIndexSha256=policy['taskSelectionSourcePolicy']['sourceReviewIndexSha256'],
    nativeSourceFiles=342,unchangedResourceParentFiles=339,nativeReplacements=3,publicModuleManifestVersion=policy['profileVersion'],
    timerOwnershipPatchPreserved=True,fullNativeRebuildRequired=True,compatibleWithResourceEngineAbi=False,
    policy=descriptor(OWN/'policy.json'),helper=descriptor(OWN/'layer-policy.py'),recipe=descriptor(OWN/'proposed/tests/node-compat/build-engine.sh'),
    sourceRoot=stage['sourceRoot'],workRoot=stage['workRoot'],freezeRoot=stage['freezeRoot'],stagePlanRows=len(stage['files']),preparationInputRows=len(freeze['files']),
    actualChecks=descriptor(OWN/'source-check-results.json'),pythonAst=sorted(syntax),recipeBashParsingPassed=True,
    prospectiveIndependentState='INDEPENDENT_SCHEDULER_TASK_SELECTION_INTEGRATION_SOURCE_REVIEW_PASSED_V1',
    sourceApplied=False,stageExecuted=False,configureExecuted=False,ownerHelpersImported=False,compilerInvoked=False,nativeBuilt=False,
    engineExecuted=False,componentExecuted=False,guestOrHostOrRuntimeInvoked=False,rootAction=None,actualStage=None,actualBuild=None,actualFreeze=None,actualNativeReview=None,
    engine=None,metadata=None,freezeReceipt=None,nativePins={'normal-off':None,'gc-off':None,'normal-runtime':None},packagingClosure=None,nativeAllInvalidFixture=None,
    operationalAdmission=False,runtimeAcceptanceClaim=False,fullResetOrReuse=False,als=False,adoptionAllowed=False,
    qualifications=['Pure command-parser positives use the real previous resource compile database as DATA; they are not observations of new compilation.',
    'Historical resource timer/task and selector SDK/source-model evidence remains separately scoped; no new C++ or native runtime action ran.',
    'Parent c55 resource pin tooling cannot admit this new source identity. New source-aware freezer/classifier/export/bootstrap and actual proofs remain required.',
    'All-invalid native component fixture is absent; interest release, task destructor/JS roots, WASI behavior and runtime progress remain unproved.'])
write('results.json',results)
write('source-receipt.json',dict(schemaVersion=1,state='TASK_SELECTION342_INTEGRATION_SOURCE_CANDIDATE_SEALED_V1',sourceOnly=True,results=descriptor(OWN/'results.json'),preparationManifest=descriptor(OWN/'input-freeze.json'),sourceChecks=descriptor(OWN/'source-check-results.json'),allPreparationRowsRehashed=True,allStagePlanRowsRehashed=True,stageOrNativeOrRuntimeActionsInvoked=False,independentReviewRequired=True,rootAuthority=None))
assert not any(p.is_symlink()for p in OWN.rglob('*'))
files=[]
for p in sorted(OWN.rglob('*')):
    if p.is_file():
        row=descriptor(p);row['path']=p.relative_to(OWN).as_posix();files.append(row)
write('index.json',dict(schemaVersion=1,state='TASK_SELECTION342_INTEGRATION_SOURCE_INDEX_V1',files=files))
print(json.dumps(dict(index=descriptor(OWN/'index.json'),results=descriptor(OWN/'results.json'),receipt=descriptor(OWN/'source-receipt.json'),members=len(files),inputs=len(freeze['files']),noOwnerActions=True)))
