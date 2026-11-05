"""Seal this dormant source family only; no owner/controller imports."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def descriptor(path):
    raw=path.read_bytes();return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))


def write(name,value):
    with (HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')


def main():
    assert not (HERE/'index.json').exists(),'Sealed sources are immutable'
    checks=json.loads((HERE/'source-check-results.json').read_bytes())
    refs=json.loads((HERE/'references.json').read_bytes())
    assert checks['state']=='SECRET_OWNED_STAGE_CONTROLLER_SOURCE_CHECKS_COMPLETE_V1'
    assert checks['nativeSourceFiles']==355 and checks['unchangedParentNativeFiles']==352 and checks['changedNativeFiles']==3
    assert checks['baseStageRows']==1403 and checks['expectedStageCopies']==1424
    for k in ['ownControllerImported','ownerHelpersImported','monitorInvoked','posixProcessDiscoveryInvoked','processesStarted','signalsSent',
              'sourceStageExecuted','nativeBuildExecuted','compilerInvoked','nodeInvoked','engineExecuted','guestOrCryptoOrGcExecuted','operationalAdmission']:
        assert checks[k]is False
    write('results.json',dict(schemaVersion=1,state='UNAPPLIED_SECRET_OWNER355_OWNED_STAGE_CONTROLLER_SOURCE_PREPARATION_COMPLETE_V1',
        sourceOnly=True,integrationSourceIndex=refs['integrationIndex'],actualIntegrationSourceReview=refs['actualIntegrationSourceReview'],
        genericMonitorSourceIndex=refs['monitorIndex'],genericMonitorEntry=refs['monitorEntry'],
        nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,baseStageRows=1403,expectedStageCopies=1424,
        sourceChecks=descriptor(HERE/'source-check-results.json'),apiBindings=descriptor(HERE/'api-bindings.json'),checks=checks,
        actualControllerSourceReview=None,rootStageAuthority=None,actualStageResult=None,actualStageReview=None,
        actualBuildResult=None,actualFreezeResult=None,reviewedNativePins=None,
        ownerHelpersImported=False,monitorInvoked=False,processesStarted=False,signalsSent=False,
        sourceStageExecuted=False,nativeBuildExecuted=False,engineExecuted=False,guestOrCryptoOrGcExecuted=False,
        operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False,
        limitations=['Dormant source only; no real owned lifecycle/stage evidence generated',
                    'Fresh independent controller source peer and Root stage action required',
                    'Source stage does not authorize native build/freeze/bootstrap/runtime']))
    write('source-receipt.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_SECRET_OWNER355_STAGE_CONTROLLER_SOURCE_V1',
        result=descriptor(HERE/'results.json'),sourceChecks=descriptor(HERE/'source-check-results.json'),
        checkedInputs=descriptor(HERE/'checked-inputs.json'),actualControllerSourceReview=None,rootStageAuthority=None,
        sourceOnly=True,ownerHelpersImported=False,processesStarted=False,signalsSent=False,operationalAdmission=False))
    rows=[]
    for path in sorted(HERE.rglob('*')):
        assert not path.is_symlink()
        if path.is_file():
            row=descriptor(path);rows.append(dict(path=str(path.relative_to(HERE)),sha256=row['sha256'],bytes=row['bytes']))
    write('index.json',dict(schemaVersion=1,state='SEALED_SECRET_OWNER355_STAGE_CONTROLLER_SOURCE_FAMILY_V1',files=rows))
    assert {r['path']for r in rows}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    for r in rows:
        row=descriptor(HERE/r['path']);assert (row['sha256'],row['bytes'])==(r['sha256'],r['bytes'])
    print(json.dumps(dict(index=descriptor(HERE/'index.json'),result=descriptor(HERE/'results.json'),
        receipt=descriptor(HERE/'source-receipt.json'),indexedMembers=len(rows),actualFiles=len(rows)+1)))


if __name__=='__main__':main()
