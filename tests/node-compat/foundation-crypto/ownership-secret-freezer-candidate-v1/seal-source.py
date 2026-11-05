"""Seal only this dormant Source packet; never import an owner/helper."""
import hashlib
import json
import os
from pathlib import Path

HERE=Path(__file__).resolve().parent


def descriptor(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size)


def verify(row):
    value=descriptor(row['path']);assert value==row


def write(name,value):
    with (HERE/name).open('x')as stream:
        json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())


def main():
    assert not(HERE/'index.json').exists()
    c=json.loads((HERE/'source-contract.json').read_bytes());checks=json.loads((HERE/'source-check-results.json').read_bytes())
    inputs=json.loads((HERE/'source-inputs.json').read_bytes())
    assert checks['state']=='SECRET_NORMAL_OFF_FREEZER_SOURCE_CHECKS_PASSED_V1'and checks['sourceOnly']is True and checks['sourceChecksPassed']is True
    assert checks['actualBuildLedgerRows']==25594 and checks['stageCopies1424']==1424 and checks['normalMembership1391']==1391 and checks['normalOriginalReferences1387']==1387
    assert checks['exactCommonFunctions']==12 and checks['exactForwardReverseEdits']==26 and checks['pureModels']==64
    for k in ['ownerHelpersImported','helperCommandsInvoked','nodeInvoked','compilerInvoked','freezeCopiesExecuted','engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim']:assert checks[k]is False
    for r in inputs['files']:verify(r)
    verify(inputs['separateBuildLedger'])
    ledger=json.loads(Path(inputs['separateBuildLedger']['path']).read_bytes())
    for r in ledger['files']:
        path=r['path'];canonical='/private'+path if path.startswith('/tmp/')else path
        verify(dict(path=canonical,sha256=r['sha256'],bytes=r['bytes']))
    assert c['actualBuildReview']is not None
    for k in ['rootAuthority','independentSourceReview','actualFreezeReceipt']:assert c[k]is None
    assert not Path(c['freezeRoot']).exists()and not Path(c['freezeRoot']).is_symlink()
    write('results.json',dict(schemaVersion=1,state='UNAPPLIED_SECRET_OWNER355_NORMAL_OFF_FREEZER_SOURCE_PREPARATION_COMPLETE_V1',
        sourceOnly=True,sourcePreparationPassed=True,nativeSourceIndex=c['nativeSourceIndex'],nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,externalEmbeddingSources=3,variant='normal-off',selectedManifestCount=11,
        engine=c['engine'],metadata=c['metadata'],actualBuildRootObservation=c['actualBuildRootObservation'],actualBuildReview=c['actualBuildReview'],actualBuildContract=c['actualBuildContract'],buildReferenceLedger=c['buildReferenceLedger'],
        originalToolingRoot=c['originalToolingRoot'],configuredSourceRoot=c['configuredSourceRoot'],workRoot=c['workRoot'],prospectiveFreezeRoot=c['freezeRoot'],
        activeCommonHelper=descriptor(HERE/'artifact-tools/artifact_common.py'),activeCommonRelativePath=c['activeCommonRelativePath'],activeEntry=descriptor(HERE/'freeze.py'),configuredSourceHelper=c['helper'],configuredSourceAdmission=c['buildAdmission'],
        sourceChecks=descriptor(HERE/'source-check-results.json'),sourceInputs=descriptor(HERE/'source-inputs.json'),sourceRoleAudit=descriptor(HERE/'source-role-audit.json'),pureModels=descriptor(HERE/'pure-model-results.json'),
        checks=checks,independentSourceReview=None,rootFreezeAuthority=None,actualFreezeReceipt=None,actualFrozenArtifactReview=None,reviewedNativePins=None,bootstrapAuthority=None,runtimeAuthority=None,
        ownerHelpersImported=False,helperCommandsInvoked=False,processesStarted=False,nodeInvoked=False,ninjaInvoked=False,compilerInvoked=False,freezeCopiesExecuted=False,engineExecuted=False,guestOrCryptoOrGcExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False,
        normalWorkReconfigurationAllowed=False,normalFreezeAndIndependentArtifactReviewRequiredBeforeLaterVariant=True,
        limitations=['Source-only preparation, not an independent source review or action authority','No real child process or copy-plan execution in these checks','No fresh JavaScript grammar invocation; exact reversible source/API review only','Complete BUILD ledger protects references; not all referenced SDK/static archives are copied','Copied active/donor host tools are provenance bytes, not standalone frozen execution','New frozen-only verifier, export, pin and bootstrap source are not implemented','No runtime, allocation-fault, erasure, security-completeness, reset/reuse or performance acceptance']))
    write('source-receipt.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_SECRET_NORMAL_OFF_FREEZER_SOURCE_V1',sourceOnly=True,
        result=descriptor(HERE/'results.json'),sourceChecks=descriptor(HERE/'source-check-results.json'),sourceInputs=descriptor(HERE/'source-inputs.json'),sourceRoleAudit=descriptor(HERE/'source-role-audit.json'),preparationHistory=descriptor(HERE/'preparation-history.json'),
        actualBuildReview=c['actualBuildReview'],independentSourceReview=None,rootFreezeAuthority=None,actualFreezeReceipt=None,
        ownerHelpersImported=False,processesStarted=False,nodeInvoked=False,ninjaInvoked=False,compilerInvoked=False,freezeCopiesExecuted=False,engineExecuted=False,operationalAdmission=False))
    rows=[]
    for path in sorted(HERE.rglob('*')):
        assert not path.is_symlink()
        if path.is_file():
            d=descriptor(path);rows.append(dict(path=str(path.relative_to(HERE)),sha256=d['sha256'],bytes=d['bytes']))
    write('index.json',dict(schemaVersion=1,state='SEALED_SECRET_OWNER355_NORMAL_OFF_FREEZER_SOURCE_FAMILY_V1',files=rows))
    assert {r['path']for r in rows}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    for r in rows:verify(dict(path=str(HERE/r['path']),sha256=r['sha256'],bytes=r['bytes']))
    print(json.dumps(dict(index=descriptor(HERE/'index.json'),result=descriptor(HERE/'results.json'),receipt=descriptor(HERE/'source-receipt.json'),indexedMembers=len(rows),actualFiles=len(rows)+1)))


if __name__=='__main__':main()
