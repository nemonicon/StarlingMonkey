"""Own SOURCE/DATA preparation only; never import donor/helper/controller code."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
S=HERE.parent
REPO=S.parents[2]


def d(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size)


def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def pair(name):
    p=S/name;return dict(index=d(p/'index.json'),result=d(p/'results.json'))


def main():
    assert not(HERE/'index.json').exists()
    source=S/'task-selection-integration-candidate-v1'
    stage=pair('independent-task-selection-stage-results-review-v1')
    assert stage['index']['sha256']=='54fcdb9187a0100b9cf149f9635fb7fa45dc7bb964b7d0975f059ecc1981e766'
    actual=json.loads(Path(stage['result']['path']).read_bytes())
    lifecycle=S/'resource-build-controller-candidate-v1'
    monitor=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
    source_index=d(source/'index.json');assert source_index['sha256']=='88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1'
    lifecycle_index=d(lifecycle/'index.json');assert lifecycle_index['sha256'].startswith('f751')
    refs=dict(schemaVersion=1,state='TASK_SELECTION342_NORMAL_OFF_BUILD_ORIGINAL_CONTEXT_REFERENCES_V1',sourceIndex=source_index,
        sourceReview=pair('independent-task-selection-integration-source-review-v1'),actualStageReview=stage,
        actualStageContract=d(S/'independent-task-selection-stage-results-review-v1/result-contract.json'),actualStageInputLedger=d(S/'independent-task-selection-stage-results-review-v1/input-hashes.json'),
        actualJournal=actual['actualJournal'],stageRootObservation=actual['rootObservation'],stageOuterTerminal=actual['outerTerminal'],stageInnerTerminal=actual['innerTerminal'],stageRootAuthority=actual['rootAuthority'],stageRootConfig=actual['rootConfig'],stageObservation=actual['stageObservation'],
        resourceFreezeReceipt=d('/private/tmp/starling-node-compat/scheduler-resource-v1-freeze/normal-off-freeze-receipt.json'),resourceStage=d('/private/tmp/starling-node-compat/scheduler-resource-v1-stage.json'),
        monitorIndex=d(monitor/'index.json'),monitorEntry=d(monitor/'monitor.py'),lifecycleIndex=lifecycle_index,lifecycleEntry=d(lifecycle/'lifecycle.py'),
        configuredSourceRoot='/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source',workRoot='/private/tmp/starling-node-compat/scheduler-resource-selection-v1-build',freezeRoot='/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze',
        node=d('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'),
        expectedCompileRows=dict(database=67,policyNativeCpp=61,otherConfigured=5,generatedNull=1,strict=4,privateClassic=5,embeddingSeparate=1),externalEmbeddingSourceAncestry=3,externalEmbeddingSourcesCopiedInStage=0,
        normalEnvironmentExtra=dict(NODE_COMPAT_NODE='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',NODE_COMPAT_ARTIFACT_TAG='selectionv1',BINARYEN_CORES='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='1'),
        controllerIndependentReview=None,rootBuildAuthority=None,actualBuildResult=None,engine=None,metadata=None,freezeReceipt=None,reviewedPins=None,operationalAdmission=False)
    refs['families']=[dict(index=index,role='ORIGINAL_INDEXED_SOURCE_OR_ACTUAL_PREREQUISITE_DATA')for index in [source_index,refs['sourceReview']['index'],stage['index'],d(S/'task-selection-stage-controller-candidate-v1/index.json'),d(S/'independent-task-selection-stage-controller-source-review-v1/index.json'),lifecycle_index,refs['monitorIndex']]]
    write('references.json',refs)
    root=dict(schemaVersion=1,state=None,phase='build',variant='normal-off',sourceIndexSha256=source_index['sha256'],configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],freezeRoot=refs['freezeRoot'],buildOutputRoot='/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-root',externalOutputRoot='/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-external-root',nativeSourceFiles=342,unchangedResourceParentFiles=339,nativeReplacements=3,externalEmbeddingSources=3,webTimersEnabled=True,gcStress=False,entropyMode='OFF',externalParentDeadlineSeconds=7200,jobs=1,buildType='Release',oomTesting=False,requiredStartFreeBytes=2147483648,stopBelowFreeBytes=838860800,controllerIndex=None,controllerEntry=None,controllerIndependentReview=None,sourceIndependentReview=refs['sourceReview'],independentStageReview=stage,stageContract=refs['actualStageContract'],actualJournal=refs['actualJournal'],stageRootObservation=refs['stageRootObservation'],buildAllowed=False)
    for k in ['stageAllowed','gcReconfigureAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','componentAllowed','guestAllowed','engineExecutionAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']:root[k]=False
    for k in ['actualBuildResult','engine','metadata','actualNormalFreeze','independentNormalFreezeReview','runtimeAction']:root[k]=None
    write('future-root-authority.template.json',root)
    write('future-config.template.json',dict(schemaVersion=1,sourceIndex=source_index,controllerIndex=None,rootAuthority=None))
    write('future-source-review-contract.json',dict(schemaVersion=1,requiredState='INDEPENDENT_SCHEDULER_TASK_SELECTION342_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=None,taskSelectionSourceIndexSha256=source_index['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeBuildActionsInvoked=False,actualIndependentSourceReview=None,rootAuthority=None,issuesNoAuthority=True))
    print(json.dumps(dict(sourceDataPrepared=True,actualStageReview=stage['index']['sha256'],newRootAuthority=None,actionsInvoked=False)))


if __name__=='__main__':main()
