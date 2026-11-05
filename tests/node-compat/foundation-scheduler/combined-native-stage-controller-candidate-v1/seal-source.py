"""Seal only this dormant source/data family; never import operational code."""
from pathlib import Path
import ast
import hashlib
import json
import stat

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]

def load(path):return json.loads(Path(path).read_bytes())
def row(path):
    path=Path(path);raw=path.read_bytes()
    return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def write(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
def verify(r):
    path=Path(r['path'])
    if str(path).startswith('/tmp/'):path=Path('/private'+str(path))
    for p in (path,*path.parents):assert not p.is_symlink()
    assert stat.S_ISREG(path.stat().st_mode)
    actual=row(path);assert(actual['sha256'],actual['bytes'])==(r['sha256'],r['bytes'])
def bookend():
    inputs=load(HERE/'input-hashes.json');assert len(inputs['files'])==1637
    for r in inputs['files']:verify(r)
    copies=load(HERE/'stage-copy-plan.json')['files'];assert len(copies)==1613
    for r in copies:
        verify(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
        assert stat.S_IMODE(Path(r['original']).stat().st_mode)==r['sourceMode']
    refs=load(HERE/'references.json')
    for key in ['integrationIndex','monitorIndex']:
        index=refs[key];verify(index);root=Path(index['path']).parent;value=load(index['path'])
        names={r['path']for r in value['files']}
        assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{'index.json'}
        for p in root.rglob('*'):assert not p.is_symlink()
        for r in value['files']:verify(dict(path=str(root/r['path']),sha256=r['sha256'],bytes=r['bytes']))
    return inputs,copies,refs

assert not (HERE/'index.json').exists(),'Never rewrite a sealed source family'
inputs,copies,refs=bookend()
check=load(HERE/'source-check-results.json')
assert check['checks']>=6610 and check['controllerSha256']==row(HERE/'controller.py')['sha256']
for key in ['sourceStageExecuted','gitInvoked','monitorInvoked','producerHelperInvoked','nativeBuildExecuted','engineExecuted','guestExecuted']:assert check[key]is False
for name in ['root-authority.template.json','config.template.json']:
    assert load(HERE/name)['state'].startswith('UNISSUED_')

def citation(path,symbol,role):
    path=Path(path);tree=ast.parse(path.read_text())
    node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))and n.name==symbol)
    return dict(source=row(path),symbol=symbol,firstLine=node.lineno,lastLine=node.end_lineno,role=role)

apis=[
    citation(Path(refs['monitorEntry']['path']),'monitor','GENUINE_SIX_ARGUMENT_OWNED_API_CALLED_IN_ORIGINAL_CONTEXT_ONLY_AFTER_FULL_AUTH'),
    citation(Path(refs['publishMechanismSourceData'][0]['path']),'main','READ_ONLY_PUBLISH_MECHANISM_SOURCE_ANCESTRY_NOT_IMPORTED_OR_CALLED'),
    citation(Path(refs['publishMechanismSourceData'][1]['path']),'main','READ_ONLY_DETACHED_CLONE_AND_ORIGINAL_ROLE_MECHANISM_ANCESTRY_NOT_IMPORTED_OR_CALLED'),
]
for name in ['authorize','recheck','command','stage','journal_model','main']:
    apis.append(citation(HERE/'controller.py',name,'NEW_AUTHORED_COMBINED355_STAGE_SOURCE'))
write('api-citations.json',dict(schemaVersion=1,apis=apis,monitorApi=refs['monitorApi'],monitorDeadlineSeconds=600,oldMonitorMainInvoked=False,oldPublishEntrypointsImported=False,oldClassifierImported=False,globalRebinding=False,controllerIsByteIdenticalDonor=False))

integration_required=dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=refs['integrationIndex']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,operationalAdmission=False,nativeSourceFiles=355,retainedParentNativeFiles=348,changedNativeFiles=7,externalEmbeddingSources=3,selectedManifestCount=11,initialVariant='normal-off',privateBackendEvidenceHookEnabled=False)
controller_required=dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_SOURCE_STAGE_CONTROLLER_SOURCE_REVIEW_PASSED_V1',integrationSourceIndexSha256=refs['integrationIndex']['sha256'],genericMonitorSourceIndexSha256=refs['monitorIndex']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,sourceStageActionsInvoked=False)
write('future-source-review-contract.json',dict(schemaVersion=1,state='PROSPECTIVE_COMBINED355_STAGE_SOURCE_REVIEW_CONTRACT_V1',integrationReviewRequiredFixedValues=integration_required,controllerReviewRequiredFixedValues=controller_required,controllerReviewRequiredIndexBinding=dict(field='controllerSourceIndexSha256',mustEqual='sha256 of this complete sealed family index.json'),indexedReviewResultOccurrenceCount=1,actualIntegrationReview=None,actualControllerReview=None,actualRootAuthority=None,grantsAnyActionAuthority=False))

artifacts={name:row(HERE/path)for name,path in dict(controller='controller.py',stageCopyPlan='stage-copy-plan.json',inputHashes='input-hashes.json',references='references.json',rootTemplate='root-authority.template.json',configTemplate='config.template.json',sourceChecks='source-check-results.json',apiCitations='api-citations.json',futureSourceReviewContract='future-source-review-contract.json').items()}
contexts={key:load(HERE/'root-authority.template.json')[key]for key in ['configuredSourceRoot','workRoot','freezeRoot','externalOutputRoot','stageJournal']}
result=dict(schemaVersion=1,state='DORMANT_COMBINED355_SOURCE_STAGE_CONTROLLER_CANDIDATE_V1',sourceOnly=True,sourcePrepared=True,sourceChecksPassed=True,integrationSourceIndex=refs['integrationIndex'],genericMonitorSourceIndex=refs['monitorIndex'],nativeSourceFiles=355,retainedParentNativeFiles=348,changedNativeFiles=7,externalEmbeddingSources=3,selectedManifestCount=11,basePlanRows=1581,toolRows=1226,integrationFamilyRows=32,stageCopies=1613,inputRows=1637,originalIntegrationInputRows=1590,baselineRevision='54b3329b3ce818fd1f244e871e9c259b63667cda',contexts=contexts,externalParentDeadlineSeconds=600,gitCommandDeadlineSeconds=120,sourceDataAndPureModelChecks=check['checks'],actualDataDescriptorReadBoundaries=1637,actualIndexedFamilyReads=2,operationalModelsSyntheticOnly=True,artifacts=artifacts,independentIntegrationSourceReview=None,independentControllerSourceReview=None,rootAuthority=None,actualStageResult=None,actualStageReview=None,build=None,freeze=None,pins=None,bootstrap=None,runtimeAuthority=None)
for key in ['ownerActionsInvoked','hostActionsInvoked','sourceStageActionsInvoked','gitInvoked','monitorInvoked','producerHelperInvoked','nativeBuildExecuted','engineExecuted','guestExecuted','metadataProjected','privateBackendEvidenceHookEnabled','pinsAdopted','operationalAdmission','runtimeAcceptanceClaim']:result[key]=False
write('results.json',result)
write('source-contract.json',dict(schemaVersion=1,state='PROSPECTIVE_COMBINED355_STAGE_CONTROLLER_SOURCE_CONTRACT_V1',results=row(HERE/'results.json'),artifacts=artifacts,integrationSourceIndex=refs['integrationIndex'],genericMonitorSourceIndex=refs['monitorIndex'],futureIndependentSourcePeer=controller_required,controllerIndexBinding='Exact this-family index SHA, externally supplied by a separately issued Root authority',entrypoint=dict(originalContext=str(HERE),cli=['<reviewed absolute Python>','-B','-I',str(HERE/'controller.py'),'<config descriptor JSON>']),monitorApi=refs['monitorApi'],contexts=contexts,stageCopies=1613,nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,allFutureActionSlots=None,grantsAnyActionAuthority=False,notImplemented=['actual source stage and independent outcome review','owned full fresh ABI normal-OFF build','genuine frozen-only new355 artifact verifier/freezer','export/reviewed pins/bootstrap','component/runtime and other native variants','private linked backend-version fixture']))
write('source-receipt.json',dict(schemaVersion=1,state='COMBINED355_STAGE_SOURCE_PREPARED_NOT_EXECUTED_V1',results=row(HERE/'results.json'),contract=row(HERE/'source-contract.json'),controller=row(HERE/'controller.py'),integrationSourceIndex=refs['integrationIndex'],genericMonitorSourceIndex=refs['monitorIndex'],inputRows=1637,stageCopyRows=1613,sourceChecks=check['checks'],sourceOnly=True,independentSourceReview=None,rootAuthority=None,ownerActionsInvoked=False,grantsAnyActionAuthority=False))
for path in HERE.glob('*.py'):ast.parse(path.read_text())
bookend()
for path in HERE.rglob('*'):assert not path.is_symlink()
files=[dict(path=p.relative_to(HERE).as_posix(),sha256=row(p)['sha256'],bytes=p.stat().st_size)for p in sorted(HERE.rglob('*'))if p.is_file()]
write('index.json',dict(schemaVersion=1,state='SEALED_COMBINED355_SOURCE_STAGE_CONTROLLER_CANDIDATE_V1',files=files))
bookend()
index=load(HERE/'index.json')
assert {p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}=={r['path']for r in index['files']}|{'index.json'}
for r in index['files']:verify(dict(path=str(HERE/r['path']),sha256=r['sha256'],bytes=r['bytes']))
print(json.dumps(dict(index=row(HERE/'index.json'),results=row(HERE/'results.json'),contract=row(HERE/'source-contract.json'),receipt=row(HERE/'source-receipt.json'),members=len(files),inputs=1637,stageCopies=1613,sourceOnly=True,ownerActionsInvoked=False)))
