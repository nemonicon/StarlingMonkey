"""Own dormant SOURCE preparation seal; never import a controller/helper."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def d(p):
    b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def w(name,value):
    with (HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')


def main():
    assert not (HERE/'index.json').exists()
    checks=json.loads((HERE/'source-check-results.json').read_bytes())
    refs=json.loads((HERE/'references.json').read_bytes())
    assert checks['state']=='SECRET_NORMAL_OFF_BUILD_CONTROLLER_SOURCE_CHECKS_COMPLETE_V1'
    assert checks['nativeSourceFiles']==355 and checks['unchangedParentNativeFiles']==352 and checks['changedNativeFiles']==3
    assert checks['actualStageCopies']==1424 and refs['actualStageReview']is not None
    for key in ['ownerHelpersImported','controllerImported','monitorInvoked','processesStarted','signalsSent','configureOrCompilerInvoked','nodeInvoked','nativeBuildExecuted','engineExecuted','guestOrCryptoOrGcExecuted','operationalAdmission']:assert checks[key]is False
    w('results.json',dict(schemaVersion=1,state='UNAPPLIED_SECRET_OWNER355_NORMAL_OFF_BUILD_CONTROLLER_SOURCE_PREPARATION_COMPLETE_V1',
        sourceOnly=True,integrationSourceIndex=refs['integrationIndex'],actualIntegrationSourceReview=refs['integrationSourceReview'],actualStageReview=refs['actualStageReview'],
        actualStageJournal=refs['actualStageJournal'],stageRootObservation=refs['stageRootObservation'],genericMonitorIndex=refs['monitorIndex'],lifecycleSourceIndex=refs['lifecycleSourceIndex'],
        actualRecipe=refs['recipe'],nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,stageCopies=1424,
        checks=checks,sourceChecks=d(HERE/'source-check-results.json'),apiBindings=d(HERE/'api-bindings.json'),
        actualControllerSourceReview=None,rootBuildAuthority=None,actualBuildResult=None,actualBuildReview=None,actualFreeze=None,reviewedNativePins=None,bootstrapAuthority=None,runtimeAuthority=None,
        ownerHelpersImported=False,monitorInvoked=False,processesStarted=False,signalsSent=False,nativeBuildExecuted=False,configureOrCompilerInvoked=False,nodeInvoked=False,
        engineExecuted=False,guestOrCryptoOrGcExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False,
        newArtifactCommonOrFreezerImplemented=False,normalFreezeRequiredBeforeLaterGc=True,
        limitations=['Source-only: no new process/compile/build result','Real stage outcome does not grant a build action','New Root and independently indexed controller source peer are mandatory','New metadata check is preliminary; full future actual BUILD-only evidence review remains required','Artifact common/freezer/pin/bootstrap/runtime source and actions stay separate']))
    w('source-receipt.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_SECRET_NORMAL_OFF_BUILD_CONTROLLER_SOURCE_V1',
        result=d(HERE/'results.json'),sourceChecks=d(HERE/'source-check-results.json'),checkedInputs=d(HERE/'checked-inputs.json'),
        preparationHistory=d(HERE/'preparation-history.json'),sourceOnly=True,actualControllerSourceReview=None,rootBuildAuthority=None,
        ownerHelpersImported=False,processesStarted=False,configureOrCompilerInvoked=False,engineExecuted=False,operationalAdmission=False))
    rows=[]
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():
            r=d(p);rows.append(dict(path=str(p.relative_to(HERE)),sha256=r['sha256'],bytes=r['bytes']))
    w('index.json',dict(schemaVersion=1,state='SEALED_SECRET_OWNER355_BUILD_CONTROLLER_SOURCE_FAMILY_V1',files=rows))
    assert {r['path']for r in rows}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    for r in rows:
        v=d(HERE/r['path']);assert(v['sha256'],v['bytes'])==(r['sha256'],r['bytes'])
    print(json.dumps(dict(index=d(HERE/'index.json'),result=d(HERE/'results.json'),receipt=d(HERE/'source-receipt.json'),indexedMembers=len(rows),actualFiles=len(rows)+1)))


if __name__=='__main__':main()
