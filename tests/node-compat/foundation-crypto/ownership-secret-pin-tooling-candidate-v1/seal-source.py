"""Seal the verifier-first Source milestone. No verifier/export/bootstrap action."""
from pathlib import Path
import hashlib,json,os
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
    c=json.loads((HERE/'source-contract.json').read_bytes());checks=json.loads((HERE/'check-results.json').read_bytes());inputs=json.loads((HERE/'source-inputs.json').read_bytes())
    assert checks['state']=='SECRET_OWNER355_FROZEN_VERIFIER_SOURCE_CHECKS_PASSED_V1'and checks['sourceChecksPassed']is True and checks['sourceOnly']is True
    assert checks['pureCases']==32 and checks['pythonAstFiles']==5 and checks['exactPureFunctions']==4 and checks['metadataPredicateForwardReverseEdits']==4
    for k in['ownerModulesImported','fullVerifierInvoked','helpersInvoked','nodeInvoked','ninjaInvoked','copyOrExportInvoked','bootstrapInvoked','engineExecuted','guestExecuted','operationalAdmission','exportPinBootstrapImplemented']:assert checks[k]is False
    for row in inputs['files']:assert d(row['path'])==row
    assert d(inputs['artifactProofLedger']['path'])==inputs['artifactProofLedger']
    ledger=json.loads(Path(inputs['artifactProofLedger']['path']).read_bytes())
    for row in ledger['files']:
        path=row['path'];path='/private'+path if path.startswith('/tmp/')else path
        assert d(path)==dict(row,path=path)
    for k in['sourceIndependentReview','rootAuthority','actualVerifierRun','actualExport','reviewedPins','bootstrapAuthority','runtimeAuthority']:assert c[k]is None
    write('results.json',dict(schemaVersion=1,state='UNAPPLIED_SECRET_OWNER355_FROZEN_VERIFIER_FIRST_SOURCE_PREPARATION_COMPLETE_V1',sourceOnly=True,sourcePreparationPassed=True,implementationPhase=c['implementationPhase'],nativeSourceIndex=c['nativeSourceIndex'],freezerSourceIndex=c['freezerSourceIndex'],actualArtifactReview=c['actualArtifactReview'],actualArtifactContract=c['actualArtifactContract'],actualFreezeRootObservation=c['actualFreezeRootObservation'],nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,externalEmbeddingSources=3,selectedManifestCount=11,variant='normal-off',engine=c['engine'],metadata=c['metadata'],freezeReceipt=c['freezeReceipt'],frozenCopies=1902,frozenOriginalReferenceStrings=1899,frozenMembership=1903,configuredSourceRoot=c['configuredSourceRoot'],frozenSourceRoot=c['frozenSourceRoot'],componentizeSourceRoot=c['componentizeSourceRoot'],workRoot=c['workRoot'],freezerOriginalToolingRoot=c['freezerOriginalToolingRoot'],verifierOriginalToolingRoot=str(HERE),sourceChecks=d(HERE/'check-results.json'),sourceInputs=d(HERE/'source-inputs.json'),sourceBoundary=d(HERE/'source-boundary-audit.json'),derivations=d(HERE/'derivations.json'),pureModels=d(HERE/'pure-results.json'),checks=checks,
        frozenVerifierSourceImplemented=True,fullVerifierInvoked=False,actualVerifierRun=None,exportEntryImplemented=False,pinModelImplemented=False,bootstrapApiImplemented=False,sourceIndependentReview=None,rootAuthority=None,actualExportCandidate=None,reviewedPins=None,actualBootstrap=None,runtimeAuthority=None,
        ownerModulesImported=False,helpersInvoked=False,nodeInvoked=False,ninjaInvoked=False,copyOrExportInvoked=False,bootstrapInvoked=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False,
        limitations=['Verifier-first Source milestone only: no export entry, pin model or bootstrap API','Full verifier function remains unexecuted; only extracted predicates and independent Data checks ran','A future separately reviewed caller must authenticate this Source family/contract and new Root phase before helper use','Payload core does not reopen original/configured/build pointers; preparation separately protects all original and old-normal inputs','Not every original SDK/archive/build reference is frozen; exact6a0c/380e historical semantic provenance stays distinct','No old selectors or metadata/state/path/global projection, engine/guest/key/GC/fault/erasure/runtime/security/performance acceptance']))
    write('source-receipt.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_SECRET_OWNER355_FROZEN_VERIFIER_FIRST_SOURCE_V1',result=d(HERE/'results.json'),sourceChecks=d(HERE/'check-results.json'),sourceInputs=d(HERE/'source-inputs.json'),sourceBoundary=d(HERE/'source-boundary-audit.json'),history=d(HERE/'preparation-history.json'),sourceOnly=True,fullVerifierInvoked=False,exportPinBootstrapImplemented=False,sourceIndependentReview=None,rootAuthority=None,engineExecuted=False,operationalAdmission=False))
    rows=[]
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():
            row=d(p);rows.append(dict(path=str(p.relative_to(HERE)),sha256=row['sha256'],bytes=row['bytes']))
    write('index.json',dict(schemaVersion=1,state='SEALED_SECRET_OWNER355_FROZEN_VERIFIER_FIRST_SOURCE_FAMILY_V1',files=rows))
    assert {r['path']for r in rows}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    for row in rows:assert d(HERE/row['path'])==dict(row,path=str(HERE/row['path']))
    print(json.dumps(dict(index=d(HERE/'index.json'),result=d(HERE/'results.json'),receipt=d(HERE/'source-receipt.json'),members=len(rows),implementationPhase=c['implementationPhase'])))


if __name__=='__main__':main()
