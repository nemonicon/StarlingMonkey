"""Seal only this finite source preparation; no producer/helper imports/actions."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def descriptor(path):
    raw=path.read_bytes()
    return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))


def write(name,value):
    with (HERE/name).open('x') as f:
        json.dump(value,f,indent=2);f.write('\n')


def main():
    assert not (HERE/'index.json').exists(), 'Never reseal a held family'
    checks=json.loads((HERE/'source-check-results.json').read_bytes())
    assert checks['state']=='SECRET_OWNER355_INTEGRATION_SOURCE_CHECKS_COMPLETE_V1'
    assert checks['nativeSourceFiles']==355 and checks['unchangedNativeSources']==352 and checks['correctedAfterimages']==3
    assert checks['sourceOnly']is True and checks['ownerActionsInvoked']is False
    assert checks['actualCustomCodeModules']==7
    for k in ['helperImported','compilerInvoked','nodeInvoked','stageExecuted','nativeBuildExecuted','engineExecuted','guestOrCryptoOrGcExecuted','operationalAdmission']:
        assert checks[k]is False
    refs=json.loads((HERE/'references.json').read_bytes())
    assert refs['sourcePeer']['index']['sha256']=='b8ca947b55514affbf6d2a1dc3e79813e19629cebf52903482105326bf1fdc3d'
    write('results.json',dict(schemaVersion=1,state='UNAPPLIED_CRYPTO_OWNER355_SECRET_INTEGRATION_SOURCE_PREPARATION_COMPLETE_V1',
        sourceOnly=True,nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,
        parent355SourceIndex=refs['families'][0]['index'],payloadSourceIndex=refs['families'][1]['index'],
        payloadSourcePeer=refs['sourcePeer'],sourceChecks=descriptor(HERE/'source-check-results.json'),
        callerBindings=descriptor(HERE/'caller-bindings.json'),phasePlan=descriptor(HERE/'phase-plan.json'),
        normalProtection=refs['normalProtection'],checks=checks,
        integrationSourceReview=None,rootActivation=None,actualStage=None,actualBuild=None,actualFreeze=None,
        actualPins=None,actualBootstrap=None,actualComponent=None,actualRuntime=None,actualFaultValidation=None,
        implementedSource=['exact355 policy/native origins','derived355 helper','normal-OFF recipe','explicit build-source validator','dormant source stage','finite input/phase plans'],
        unimplementedSource=['external owned stage/build controllers','current artifact common/classifier/freezer','pin/export/bootstrap successors','later runtime-entropy and GC variants'],
        ownerActionsInvoked=False,helperImported=False,compilerInvoked=False,nodeInvoked=False,
        stageExecuted=False,nativeBuildExecuted=False,freezeExecuted=False,engineExecuted=False,
        guestOrCryptoOrGcExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,
        sourcePromotionAllowed=False,securityCompleteClaim=False))
    write('source-receipt.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_SECRET_OWNER355_SOURCE_PREPARATION_V1',
        result=descriptor(HERE/'results.json'),sourceChecks=descriptor(HERE/'source-check-results.json'),
        inputHashes=descriptor(HERE/'checked-inputs.json'),derivations=descriptor(HERE/'derivations.json'),
        nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,
        independentSourceReview=None,rootActivation=None,sourcePreparationOnly=True,
        ownerActionsInvoked=False,operationalAdmission=False,securityCompleteClaim=False,
        scope='Own stdlib source/read/hash/AST/pure preparation only; real stage/build/freeze/export/bootstrap/compiler/Node/engine/guest/crypto/GC not invoked'))
    files=[]
    for path in sorted(HERE.rglob('*')):
        assert not path.is_symlink()
        if path.is_file():
            d=descriptor(path);files.append(dict(path=str(path.relative_to(HERE)),sha256=d['sha256'],bytes=d['bytes']))
    write('index.json',dict(schemaVersion=1,state='SEALED_SECRET_OWNER355_INTEGRATION_SOURCE_FAMILY_V1',files=files))
    index=json.loads((HERE/'index.json').read_bytes())
    assert len(index['files'])==len(files)
    assert {r['path']for r in files}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    for row in files:
        d=descriptor(HERE/row['path']);assert (d['sha256'],d['bytes'])==(row['sha256'],row['bytes'])
    print(json.dumps(dict(index=descriptor(HERE/'index.json'),result=descriptor(HERE/'results.json'),
        receipt=descriptor(HERE/'source-receipt.json'),indexedMembers=len(files),actualFiles=len(files)+1)))


if __name__=='__main__':
    main()
