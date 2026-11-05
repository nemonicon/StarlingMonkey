"""Seal this uncompiled Source family only; no action helper/module imports."""
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
    refs=json.loads((HERE/'references.json').read_bytes());checks=json.loads((HERE/'check-results.json').read_bytes());inputs=json.loads((HERE/'source-inputs.json').read_bytes());cut=json.loads((HERE/'source-cut.json').read_bytes());tools=json.loads((HERE/'tool-cut-references.json').read_bytes());deriv=json.loads((HERE/'source-derivation.json').read_bytes())
    assert checks['state']=='CLOCK_IO_PRUNING_UNCOMPILED_SOURCE_CHECKS_PASSED_V1'and checks['sourceChecksPassed']is checks['sourceOnly']is True
    assert checks['pureCases']==27 and checks['independentBooleanPolicyCases']==672 and checks['pythonAstFiles']==5 and checks['forwardReverseFiles']==4
    for name in['normalizedArtifactPublished','adapterPrunerExecuted','normalizerWriterExecutedWithRealFilesystem','rustCompiled','rustUnitTestsExecuted','nodeOrWizerOrEngineOrComponentOrGuestExecuted','offlineReadinessProved','grantsActionAuthority']:assert checks[name]is False
    assert checks['actualNormalizedBytesComputedInMemory']is True and inputs['initialAndFinalHashesAndIdentityVerified']is True
    for row in inputs['files']:assert d(row['path'])==row
    for name in['sourceIndependentReview','rootAuthority','stageAction','buildAction','normalizationPublication','pruningAction','actualPackage','actualPrunedAdapter','componentAction','runtimeAction']:assert refs[name]is None
    write('results.json',dict(schemaVersion=1,state='UNAPPLIED_CLOCK_IO_PRUNING_UNCOMPILED_SOURCE_PREPARATION_COMPLETE_V1',sourceOnly=True,sourcePreparationPassed=True,uncompiled=True,sourceIndependentReview=None,rootAuthority=None,
        provenanceReport=refs['provenanceReport'],independentDesignNotes=refs['independentDesignNotes'],designNotesAreSourceApproval=False,originalAdapter=refs['adapter'],normalizedAdapterInMemorySha256=deriv['normalizedAdapterInputSha256'],normalizedAdapterBytes=53512,actualNormalizedBytesComputedInMemory=True,normalizedArtifactPublished=False,actualNormalizedArtifact=None,adapterPrunerExecuted=False,actualPrunedArtifact=None,
        sourceCut=d(HERE/'source-cut.json'),sourceDerivation=d(HERE/'source-derivation.json'),sourceFiles=cut['sourceFiles'],unchangedSourceFiles=267,changedSourceFiles=4,originalSourceModified=False,futureSourceRoot=cut['futureSourceRoot'],futureWorkRoot=cut['futureWorkRoot'],futurePackageRoot=cut['futurePackageRoot'],actualSourceCutStaged=False,
        ioPolicyStubTargets=dict(original=23,poll=4,streamsAndError=19),actualInputModel=dict(functionImports=63,memoryImports=1,clockImports=6,pollImports=2,presentStreamErrorTargets=11,presentStdioTargets=3),expectedPruneReplacements=14,actualPruneReplacementsObserved=False,metadataModel=d(HERE/'adapter-metadata-model.json'),instructionsDecoded=False,
        toolCutReferences=d(HERE/'tool-cut-references.json'),rustBinLibFiles=270,jsToolFiles=4862,jsToolSymlinks=21,lockedRegistryArchiveFiles=118,missingLockedRegistryArchives=tools['missingLockedRegistryArchives'],missingArchiveStatus=tools['missingArchiveStatus'],offlineReadinessProved=False,
        sourceChecks=d(HERE/'check-results.json'),sourceInputs=d(HERE/'source-inputs.json'),pureModels=d(HERE/'pure-results.json'),checks=checks,rustUnitTestDefinitions=4,rustUnitTestsExecuted=False,rustCompiled=False,normalizerWriterExecutedWithRealFilesystem=False,
        dormantBuildPlan=d(HERE/'future-build-plan.json'),ownedBuildControllerImplemented=False,hostLinkerAndSdkSelection=None,privateCargoHomePreparation=None,actualPackage=None,stageAuthority=None,buildAuthority=None,normalizationAuthority=None,pruningAuthority=None,componentAuthority=None,runtimeAuthority=None,
        oldExternalSourceOrToolsModified=False,normalOrFrozenEngineModified=False,nodeExecuted=False,wizerExecuted=False,engineExecuted=False,componentConstructed=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False,timingAllowed=False,issuesAnyActionAuthority=False,
        limitations=['Uncompiled unapplied Source only; exact Rust/WIT/CLI execution remains unobserved','In-memory normalization is Source preparation, not adapter artifact publication','Memory-only output/fd models are not real filesystem or owned lifecycle evidence','Encoded wirm pruning/function-reference rewriting and post-prune ABI require actual structural validation','Original adapter exact source/build provenance remains unresolved','271-file source cut is distinct from native engine source count; no native build or capability admission','World canonicalization/alias/dependency and general profile regressions remain future tests','Three exact locked Windows-related archives missing; activation/offline readiness unproved, not a global Source blocker','Concrete Cargo/jco plan identifies mechanisms but is not a reviewed owned controller; host linker/SDK/private cache and raw/protection gates remain open','No actual new package/normalized/pruned adapter/component/runtime/adoption/security/performance acceptance']))
    write('source-receipt.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_UNCOMPILED_CLOCK_IO_PRUNING_SOURCE_V1',result=d(HERE/'results.json'),sourceChecks=d(HERE/'check-results.json'),sourceInputs=d(HERE/'source-inputs.json'),sourceDerivation=d(HERE/'source-derivation.json'),history=d(HERE/'preparation-history.json'),sourceOnly=True,uncompiled=True,sourceIndependentReview=None,rootAuthority=None,adapterArtifactPublished=False,adapterPrunerExecuted=False,engineExecuted=False,operationalAdmission=False))
    rows=[]
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():
            row=d(p);rows.append(dict(path=str(p.relative_to(HERE)),sha256=row['sha256'],bytes=row['bytes']))
    write('index.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_UNCOMPILED_CLOCK_IO_PRUNING_SOURCE_FAMILY_V1',files=rows))
    assert {r['path']for r in rows}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    for row in rows:assert d(HERE/row['path'])==dict(row,path=str(HERE/row['path']))
    print(json.dumps(dict(index=d(HERE/'index.json'),result=d(HERE/'results.json'),receipt=d(HERE/'source-receipt.json'),members=len(rows),uncompiled=True,adapterArtifactPublished=False)))


if __name__=='__main__':main()
