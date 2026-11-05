"""Own DATA preparation only; no controller/helper imports or actions."""
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
K=HERE.parent


def desc(path):
    raw=path.read_bytes();return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))


def write(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    assert not (HERE/'index.json').exists()
    integration=K/'ownership-secret-integration-candidate-v1'
    monitor=K/'ownership-gc-build-controller-candidate-v1'
    peer=K/'independent-ownership-secret-integration-source-review-v1'
    assert desc(integration/'index.json')['sha256']=='7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108'
    assert desc(monitor/'index.json')['sha256']=='0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b'
    assert desc(peer/'index.json')['sha256']=='8665997e4edab561a0e0e63235104b8e358072995725002704f25e4499dfca45'
    integration_peer=dict(index=desc(peer/'index.json'),result=desc(peer/'results.json'))
    refs=dict(schemaVersion=1,integrationIndex=desc(integration/'index.json'),
        monitorIndex=desc(monitor/'index.json'),monitorEntry=desc(monitor/'monitor.py'),
        actualIntegrationSourceReview=integration_peer,
        actualIntegrationSourceReviewContract=desc(peer/'result-contract.json'),
        actualControllerSourceReview=None,rootStageAuthority=None,
        sourceStageExecuted=False,operationalAdmission=False,
        families=[dict(index=desc(p/'index.json'),role='IMMUTABLE_SOURCE_DATA')for p in [integration,monitor,peer]])
    write('references.json',refs)
    expected=dict(schemaVersion=1,state='UNISSUED_ROOT_SECRET_OWNER355_OWNED_STAGE_TEMPLATE_V1',
        sourceIndexSha256=refs['integrationIndex']['sha256'],destination='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source',
        workRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build',
        freezeRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze',variant='normal-off',
        nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,baseStageRows=1403,expectedStageCopies=1424,
        payloadSourceReview=json.loads((integration/'references.json').read_bytes())['sourcePeer'],
        independentSourceReview=integration_peer,externalControllerIndex=None,externalControllerEntry=None,
        externalControllerReview=None,stageEntry=desc(integration/'stage.py'),
        genericMonitorIndex=refs['monitorIndex'],genericMonitorEntry=refs['monitorEntry'],
        externalOutputRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-stage-external-root',
        stageJournal='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-stage.json',externalParentDeadlineSeconds=600,
        actualStageResult=None,actualStageReview=None,actualBuildResult=None,reviewedNativePins=None,
        sourceStageAllowed=False,nativeBuildAllowed=False,freezeAllowed=False,engineExecutionAllowed=False,
        keyOperationsAllowed=False,guestAllowed=False,gcAllowed=False,operationalAdmission=False,
        runtimeAcceptanceClaim=False,pinsAdopted=False,normalMutationAllowed=False,metadataProjectionAllowed=False,timingAllowed=False)
    write('root-authority.template.json',expected)
    write('config.template.json',dict(schemaVersion=1,state='CRYPTO_OWNER355_SECRET_STAGE_CONTROLLER_CONFIG_V1',
        sourceIndex=refs['integrationIndex'],rootAuthority=None))
    monitor_ast=ast.parse((monitor/'monitor.py').read_bytes())
    fn=next(n for n in monitor_ast.body if isinstance(n,ast.FunctionDef)and n.name=='monitor')
    write('api-bindings.json',dict(schemaVersion=1,sourceOnly=True,
        monitorEntry=refs['monitorEntry'],monitorIndex=refs['monitorIndex'],
        monitorPositionalParameters=[n.arg for n in fn.args.args],monitorKeywordOnlyParameters=[n.arg for n in fn.args.kwonlyargs],
        actualCall='module.monitor(argv,str(REPO),environment,OUT,600,config.rootAuthority)',
        childArgv=['sys.executable','-B','-I',str(integration/'stage.py'),refs['integrationIndex']['sha256'],'JSON(config.rootAuthority)'],
        childApi='genuine7eb8 stage.py expects program + own SHA + exact Root authority descriptor JSON',
        controllerAuthorityIssued=False,oldBuildMainInvoked=False,monitorGlobalsRebound=False,
        stageSourceScope=dict(nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,
            baseStageRows=1403,integrationIndexedMembers=24,integrationIndexRows=1,baseOwnOverlap=4,expectedCopies=1424),
        actualSourceReview=integration_peer,actualControllerSourceReview=None,
        prerequisite='Fresh Root stage authority and separately indexed exact new controller source peer before any action'))
    print(json.dumps(dict(prepared=True,sourceDataOnly=True,actualControllerPeer=None,rootAuthority=None)))


if __name__=='__main__':main()
