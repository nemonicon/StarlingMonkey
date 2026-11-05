"""Own source DATA preparation; never import a controller/helper or run a build."""
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
K=HERE.parent


def d(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size)


def w(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    assert not (HERE/'index.json').exists()
    integration=K/'ownership-secret-integration-candidate-v1'
    source_peer=K/'independent-ownership-secret-integration-source-review-v1'
    stage_peer=K/'independent-ownership-secret-stage-results-review-v1'
    monitor=K/'ownership-gc-build-controller-candidate-v1'
    lifecycle=K/'native-integration-candidate-v2'
    stage_result=K/'ownership-secret-stage-v1-root-results.json'
    assert d(integration/'index.json')['sha256']=='7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108'
    assert d(stage_peer/'index.json')['sha256']=='41f8a49f6a46ff35631a8f5eb90f1682ced2052f3a27076aca12cfc68e72ffec'
    assert d(stage_result)['sha256']=='417fbe749e08f2dbd41d4a27e8ce1149e5e2721d5e3441872439896595aee67a'
    stage=json.loads((stage_peer/'results.json').read_bytes())
    pair=lambda p:dict(index=d(p/'index.json'),result=d(p/'results.json'))
    stage_descriptors={k:stage[k]for k in ['actualJournal','rootObservation','outerTerminal','innerTerminal','rootAuthority','rootConfig']}
    environment=json.loads((integration/'phase-plan.json').read_bytes())['normalOffBuild']['environment']
    environment.update(BINARYEN_CORES='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='1',NODE_COMPAT_ARTIFACT_TAG='secret355v1')
    node=d(Path(environment['NODE_COMPAT_NODE']))
    assert node['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'and node['bytes']==108619024
    refs=dict(schemaVersion=1,state='SECRET_NORMAL_OFF_BUILD_CONTROLLER_SOURCE_REFERENCES_V1',
        integrationIndex=d(integration/'index.json'),integrationSourceReview=pair(source_peer),
        actualStageReview=pair(stage_peer),actualStageReviewContract=d(stage_peer/'result-contract.json'),
        stageRootObservation=d(stage_result),actualStageJournal=stage['actualJournal'],stageDescriptors=stage_descriptors,
        monitorIndex=d(monitor/'index.json'),monitorEntry=d(monitor/'monitor.py'),
        lifecycleSourceIndex=d(lifecycle/'index.json'),lifecycleEntry=d(lifecycle/'artifact-tools/build-one.py'),
        lifecycleDormantRecipeSha256=json.loads((lifecycle/'admission-pins.json').read_bytes())['productionRecipeSha256'],
        recipe=d(integration/'proposed/tests/node-compat/build-engine.sh'),node=node,buildEnvironment=environment,
        policy=d(integration/'policy.json'),helper=d(integration/'layer-policy.py'),
        artifactBasename='starlingmonkey_embedding.abi-i32-i64-v1.secretfailure-v1.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1.secret355v1.wasm',
        families=[dict(index=d(p/'index.json'),role='AUTHENTICATED_ORIGINAL_SOURCE_OR_ACTUAL_STAGE_DATA')for p in [integration,source_peer,stage_peer,monitor,lifecycle]],
        files=list(stage_descriptors.values()),actualControllerSourceReview=None,rootBuildAuthority=None,
        activeArtifactCommon=None,activeFreezer=None,operationalAdmission=False)
    w('references.json',refs)
    root=dict(schemaVersion=1,state='UNISSUED_ROOT_SECRET_OWNER355_NORMAL_OFF_BUILD_TEMPLATE_V1',phase='build',variant='normal-off',
        sourceIndexSha256=refs['integrationIndex']['sha256'],configuredSourceRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source',
        workRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build',freezeRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze',
        buildOutputRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-normal-off-build-root',
        externalOutputRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-normal-off-build-external-root',
        nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,stageCopies=1424,externalParentDeadlineSeconds=7200,
        externalControllerIndex=None,externalControllerEntry=None,workerEntry=None,workerMode='worker',externalControllerReview=None,
        integrationSourceReview=refs['integrationSourceReview'],actualStageReview=refs['actualStageReview'],
        stageRootObservation=refs['stageRootObservation'],actualStageJournal=refs['actualStageJournal'],
        genericMonitorEntry=refs['monitorEntry'],genericMonitorIndex=refs['monitorIndex'],
        lifecycleEntry=refs['lifecycleEntry'],lifecycleSourceIndex=refs['lifecycleSourceIndex'],buildEnvironment=environment,
        parallelBuilds=1,requiredStartFreeBytes=2147483648,stopBelowFreeBytes=838860800,buildAllowed=False)
    for k in ['stageAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','componentAllowed','guestAllowed',
              'keyOperationsAllowed','gcAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:root[k]=False
    for k in ['actualBuildResult','actualBuildReview','actualFreezeResult','reviewedNativePins','bootstrapAuthority','runtimeAuthority']:root[k]=None
    w('root-authority.template.json',root)
    w('config.template.json',dict(schemaVersion=1,state='SECRET_OWNER355_NORMAL_OFF_BUILD_CONFIG_V1',sourceIndex=refs['integrationIndex'],rootAuthority=None))
    api=[]
    tree=ast.parse((lifecycle/'artifact-tools/build-one.py').read_bytes())
    for name in ['prepare_output','monitor_owned_command','finalize_status','publish_result']:
        f=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name)
        api.append(dict(name=name,positionalParameters=[n.arg for n in f.args.args],keywordOnlyParameters=[n.arg for n in f.args.kwonlyargs]))
    w('api-bindings.json',dict(schemaVersion=1,sourceOnly=True,lifecycleEntry=refs['lifecycleEntry'],actualExplicitLifecycleApis=api,
        lifecycleMainInvoked=False,lifecycleGlobalsRebound=False,donorRecipeConstantRole='Authenticated original DATA, used only to prove original module context; not the new actual recipe identity',
        actualNewRecipe=refs['recipe'],monitorEntry=refs['monitorEntry'],
        newParentWorkerCli='python -B -I controller.py parent|worker EXACT_CONFIG_DESCRIPTOR_JSON',
        actualStagePeer=refs['actualStageReview'],normalFreezeRequiredBeforeLaterGc=True,
        currentNativeBuildExecuted=False,activeArtifactCommon=None,activeFreezer=None))
    print(json.dumps(dict(prepared=True,sourceOnly=True,actualStagePeer=refs['actualStageReview']['index'],rootAuthority=None)))


if __name__=='__main__':main()
