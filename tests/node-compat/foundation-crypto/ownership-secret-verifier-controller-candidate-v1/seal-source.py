"""Seal only this Source caller family; never import or run action modules."""
from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent


def d(path):
    p=Path(path);assert p.is_file()and not p.is_symlink();a=p.stat();h=hashlib.sha256()
    with p.open('rb')as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)


def write(name,value):
    with(HERE/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())


def main():
    assert not(HERE/'index.json').exists()
    refs=json.loads((HERE/'references.json').read_bytes());checks=json.loads((HERE/'check-results.json').read_bytes());inputs=json.loads((HERE/'source-inputs.json').read_bytes())
    assert checks['state']=='SECRET_OWNER355_READ_ONLY_VERIFIER_CONTROLLER_SOURCE_CHECKS_PASSED_V1'and checks['sourceOnly']is checks['sourceChecksPassed']is True
    assert checks['pureCases']==38 and checks['pythonAstFiles']==4
    for key in['controllerOrHelperOrMonitorImported','processesStarted','fullVerifierInvoked','nodeOrNinjaInvoked','copyExportBootstrapOrEngineInvoked','operationalAdmission']:assert checks[key]is False
    for key in['actualRootAuthority','actualVerifierResult']:assert checks[key]is None
    for key in['controllerIndependentReview','rootAuthority','actualVerifierResult','actualExport','reviewedPins','bootstrapAuthority','runtimeAuthority']:assert refs[key]is None
    assert refs['actionsAllowed']is False and inputs['allObservedInputsRehashedFinally']is True
    for row in inputs['files']:assert d(row['path'])==row
    assert inputs['artifactInputLedger']==refs['artifactInputLedger']and d(refs['artifactInputLedger']['path'])==refs['artifactInputLedger']
    ledger=json.loads(Path(refs['artifactInputLedger']['path']).read_bytes());assert len(ledger['files'])==inputs['artifactInputLedgerRows']
    for row in ledger['files']:assert d(row['path'])==row
    write('results.json',dict(schemaVersion=1,state='UNAPPLIED_SECRET_OWNER355_READ_ONLY_VERIFIER_CONTROLLER_SOURCE_PREPARATION_COMPLETE_V1',sourceOnly=True,sourcePreparationPassed=True,
        verifierSourceIndex=refs['verifierSourceIndex'],verifierSourceReview=refs['verifierSourceReview'],actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],nativeSourceIndex=refs['nativeSourceIndex'],freezerSourceIndex=refs['freezerSourceIndex'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],monitorIndex=refs['monitorIndex'],monitorEntry=refs['monitorEntry'],
        nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,externalEmbeddingSources=3,selectedManifestCount=11,variant='normal-off',frozenCopies=1902,frozenMembership=1903,frozenOriginalReferenceStrings=1899,oldNormalMembers=1391,oldNormalOriginalReferences=1387,
        originalVerifierContext=str(Path(refs['verifierEntry']['path']).parent),configuredSourceRoot=refs['configuredSourceRoot'],frozenRoot=refs['frozenRoot'],frozenSourceRoot=refs['frozenSourceRoot'],workRoot=refs['workRoot'],
        callerSourceImplemented=True,controllerSourceIndependentReview=None,rootAuthority=None,expectedCallsPerFutureWorker=1,externalParentDeadlineSeconds=600,monitorCleanupGraceAdditional=True,
        sourceChecks=d(HERE/'check-results.json'),sourceInputs=d(HERE/'source-inputs.json'),apiAndBoundaryAudit=d(HERE/'api-and-boundary-audit.json'),pureModels=d(HERE/'pure-results.json'),checks=checks,
        controllerOrHelperOrMonitorImported=False,processesStarted=False,fullVerifierInvoked=False,actualVerifierResult=None,independentActualVerifierReview=None,exporterImplemented=False,pinModelImplemented=False,bootstrapImplemented=False,actualExport=None,reviewedPins=None,actualBootstrap=None,runtimeAuthority=None,
        nodeOrNinjaInvoked=False,ownerHelperInvoked=False,engineExecuted=False,guestExecuted=False,keyOperationsInvoked=False,gcPressureInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False,timingAllowed=False,issuesAnyActionAuthority=False,
        limitations=['Source preparation only; no complete controller/verifier/helper/monitor import or real process action','Memory-only injected seams are not actual lifecycle or full-verifier evidence','Actual helper payload is FROZEN-only by reviewed source flow; caller preservation separately reads original DATA; no syscall isolation claim','Complete raw streams and whole returned JSON required for future success; partial/missing failures are unaccepted','600-second worker deadline has original bounded cleanup grace and excludes caller authentication/collection','Original metadata/context/state bytes are preserved; no relocation or global rebinding','Exporter/pin/bootstrap remain absent and require a separate reviewed successor','No engine/guest/key/GC/fault/security/adoption/runtime/performance acceptance']))
    write('source-receipt.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_SECRET_OWNER355_READ_ONLY_VERIFIER_CONTROLLER_SOURCE_V1',result=d(HERE/'results.json'),sourceChecks=d(HERE/'check-results.json'),sourceInputs=d(HERE/'source-inputs.json'),apiAndBoundaryAudit=d(HERE/'api-and-boundary-audit.json'),history=d(HERE/'preparation-history.json'),sourceOnly=True,controllerSourceIndependentReview=None,rootAuthority=None,actualVerifierResult=None,fullVerifierInvoked=False,processesStarted=False,exportPinBootstrapImplemented=False,engineExecuted=False,operationalAdmission=False))
    rows=[]
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():
            row=d(p);rows.append(dict(path=str(p.relative_to(HERE)),sha256=row['sha256'],bytes=row['bytes']))
    write('index.json',dict(schemaVersion=1,state='SEALED_SECRET_OWNER355_READ_ONLY_VERIFIER_CONTROLLER_SOURCE_FAMILY_V1',files=rows))
    assert {r['path']for r in rows}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    for row in rows:assert d(HERE/row['path'])==dict(row,path=str(HERE/row['path']))
    print(json.dumps(dict(index=d(HERE/'index.json'),result=d(HERE/'results.json'),receipt=d(HERE/'source-receipt.json'),members=len(rows),fullVerifierInvoked=False,actualVerifierResult=None)))


if __name__=='__main__':main()
