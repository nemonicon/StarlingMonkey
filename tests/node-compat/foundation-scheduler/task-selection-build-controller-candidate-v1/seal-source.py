"""Seal only this dormant Source family, without any helper/controller import."""
import hashlib,json,os
from pathlib import Path
HERE=Path(__file__).resolve().parent


def d(path):
    p=Path(path);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)


def write(name,value):
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())


def main():
    assert not(HERE/'index.json').exists()
    c=json.loads((HERE/'check-results.json').read_bytes());refs=json.loads((HERE/'references.json').read_bytes())
    assert c['state']=='TASK_SELECTION342_NORMAL_OFF_BUILD_CONTROLLER_SOURCE_CHECKS_PASSED_V1'and c['sourceOnly']is c['sourceChecksPassed']is True
    assert c['pureCases']==41 and c['pythonAstFiles']==4 and c['exactPrimitiveExtractions']==3
    for key in['ownerModulesImported','helpersInvoked','processesStarted','compilerInvoked','nativeBuildInvoked','engineExecuted','guestExecuted','operationalAdmission']:assert c[key]is False
    for r in json.loads((HERE/'input-hashes.json').read_bytes())['files']:assert d(r['path'])==r
    for key in['workRoot','freezeRoot']:assert not Path(refs[key]).exists()and not Path(refs[key]).is_symlink()
    assert not Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-root').exists()
    assert not Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-external-root').exists()
    write('results.json',dict(schemaVersion=1,state='UNAPPLIED_TASK_SELECTION342_NORMAL_OFF_BUILD_CONTROLLER_SOURCE_PREPARATION_COMPLETE_V1',sourceOnly=True,sourcePreparationPassed=True,sourceIndex=refs['sourceIndex'],sourceIndependentReview=refs['sourceReview'],actualStageReview=refs['actualStageReview'],actualStageContract=refs['actualStageContract'],actualJournal=refs['actualJournal'],stageRootObservation=refs['stageRootObservation'],monitorSourceIndex=refs['monitorIndex'],lifecycleSourceIndex=refs['lifecycleIndex'],configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],freezeRoot=refs['freezeRoot'],nativeSourceFiles=342,unchangedResourceParentFiles=339,nativeReplacements=3,externalEmbeddingSourceAncestry=3,externalEmbeddingSourcesCopiedInStage=0,expectedCompileRows=refs['expectedCompileRows'],variant='normal-off',jobs=1,buildType='Release',entropyMode='OFF',gcStress=False,oomTesting=False,checks=c,sourceChecks=d(HERE/'check-results.json'),sourceInputs=d(HERE/'input-hashes.json'),apiBindings=d(HERE/'api-bindings.json'),pureModels=d(HERE/'pure-results.json'),derivations=d(HERE/'derivations.json'),
        controllerIndependentReview=None,rootBuildAuthority=None,actualBuildResult=None,actualIndependentBuildReview=None,engine=None,metadata=None,actualNormalFreeze=None,reviewedNativePins=None,bootstrapAuthority=None,runtimeAuthority=None,
        ownerModulesImported=False,helpersInvoked=False,monitorInvoked=False,processesStarted=False,compilerInvoked=False,nativeBuildInvoked=False,engineExecuted=False,guestOrCryptoOrGcExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False,
        newArtifactCommonOrFreezerImplemented=False,normalOffFreezeAndIndependentReviewRequiredBeforeLaterVariant=True,
        limitations=['Source preparation only: independent new controller Source review and fresh Root build authority still absent','Actual stage review grants no action authority and all original stage/proof flags stay literal','Original lifecycle and monitor APIs are reused in original contexts; no old guard/build main or global rebind','Future metadata classifier is finite shape-only; full actual commands/SDK/libraries/source/Rust/engine review remains separate','No actual child process, compile, lifecycle fault or resource/selector runtime evidence from these pure checks','New source-aware freezer/pin/bootstrap/component/native all-invalid and existing baseline regressions remain future gates','No old resource engine or crypto355 proof transfers to these ABI bytes; no runtime/security/performance acceptance']))
    write('source-receipt.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_TASK_SELECTION342_NORMAL_OFF_BUILD_CONTROLLER_SOURCE_V1',result=d(HERE/'results.json'),sourceChecks=d(HERE/'check-results.json'),sourceInputs=d(HERE/'input-hashes.json'),apiBindings=d(HERE/'api-bindings.json'),preparationHistory=d(HERE/'preparation-history.json'),sourceOnly=True,controllerIndependentReview=None,rootBuildAuthority=None,actualBuildResult=None,ownerModulesImported=False,processesStarted=False,nativeBuildInvoked=False,engineExecuted=False,operationalAdmission=False))
    rows=[]
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():
            r=d(p);rows.append(dict(path=str(p.relative_to(HERE)),sha256=r['sha256'],bytes=r['bytes']))
    write('index.json',dict(schemaVersion=1,state='SEALED_TASK_SELECTION342_NORMAL_OFF_BUILD_CONTROLLER_SOURCE_FAMILY_V1',files=rows))
    assert {r['path']for r in rows}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    for r in rows:assert d(HERE/r['path'])==dict(r,path=str(HERE/r['path']))
    print(json.dumps(dict(index=d(HERE/'index.json'),result=d(HERE/'results.json'),receipt=d(HERE/'source-receipt.json'),members=len(rows))))


if __name__=='__main__':main()
