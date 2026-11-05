"""Original-context DATA bindings only; no owner/helper imports or actions."""
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
    c=json.loads((HERE/'source-contract.json').read_bytes())
    stage=K/'independent-ownership-secret-stage-results-review-v1'
    monitor=K/'ownership-gc-build-controller-candidate-v1'
    donor=K/'ownership-gc-freezer-helper-amendment-v1'
    native=K/'ownership-secret-integration-candidate-v1'
    ir=json.loads((native/'references.json').read_bytes())
    report=json.loads(Path(c['actualBuildRootObservation']['path']).read_bytes())
    files=[c['actualBuildRootObservation'],report['rootAuthority'],report['config'],report['outerTerminal'],report['actualBuildResult'],report['controllerSummary']['externalTerminal']]
    refs=dict(schemaVersion=1,state='SECRET_NORMAL_OFF_FREEZER_ORIGINAL_CONTEXT_REFERENCES_V1',
        monitorIndex=d(monitor/'index.json'),monitorEntry=d(monitor/'monitor.py'),
        donorBody=d(donor/'freezer-body.py'),nativeSourceIndex=c['nativeSourceIndex'],
        actualStageJournal=json.loads((stage/'results.json').read_bytes())['actualJournal'],
        actualBuildReview=c['actualBuildReview'],actualBuildContract=c['actualBuildContract'],buildReferenceLedger=c['buildReferenceLedger'],
        normalProtection=ir['normalProtection'],node=d('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'),
        families=[dict(index=d(p/'index.json'),role='ORIGINAL_SOURCE_OR_ACTUAL_PREREQUISITE_DATA')for p in [native,stage,monitor,donor,K/'native-integration-candidate-v2',K/'ownership-secret-build-controller-candidate-v1']],
        files=files,sourceIndependentReview=None,rootFreezeAuthority=None,actualFreezeReceipt=None,
        activeCommonRelativePath=c['activeCommonRelativePath'],activeHelperRole='ACTUAL_NEW_ORIGINAL_CONTEXT_HELPER_NOT_AN_OLD_STAGED_COMMON',
        verifiedBuildReferencesNotAllCopied=True,pinsOrRuntimeAuthority=None,operationalAdmission=False)
    if c['actualBuildReview']is not None:
        refs['families'].append(dict(index=c['actualBuildReview']['index'],role='ACTUAL_INDEPENDENT_BUILD_DATA'))
        aliases_path=Path(c['actualBuildReview']['index']['path']).parent/'reference-aliases.json'
        aliases=json.loads(aliases_path.read_bytes())
        ninja=[r['resolved']for r in aliases['hostToolReferences']if r['role']=='CMAKE_MAKE_PROGRAM']
        assert len(ninja)==1
        refs['ninja']=ninja[0]
        refs['files'] += [d(aliases_path),refs['ninja']]
    w('references.json',refs)
    root=dict(schemaVersion=1,state='UNISSUED_ROOT_SECRET_NORMAL_OFF_FREEZE_TEMPLATE_V1',phase='freeze',variant='normal-off',
        freezerIndex=None,nativeSourceIndex=c['nativeSourceIndex'],configuredSourceRoot=c['configuredSourceRoot'],workRoot=c['workRoot'],freezeRoot=c['freezeRoot'],
        originalToolingRoot=c['originalToolingRoot'],externalOutputRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze-external-root',
        entry=None,workerMode='worker',commonHelper=None,engine=c['engine'],metadata=c['metadata'],
        actualBuildReview=c['actualBuildReview'],actualBuildContract=c['actualBuildContract'],buildReferenceLedger=c['buildReferenceLedger'],
        buildRootObservation=c['actualBuildRootObservation'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,
        externalParentDeadlineSeconds=2400,genericMonitorIndex=refs['monitorIndex'],independentSourceReview=None,freezeAllowed=False)
    for k in ['buildAllowed','exportAllowed','bootstrapAllowed','gcAllowed','normalMutationAllowed','metadataProjectionAllowed','engineExecutionAllowed','componentAllowed','guestAllowed','keyOrCryptoAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:root[k]=False
    for k in ['actualFreezeReceipt','independentFrozenArtifactReview','reviewedNativePins','runtimeAuthority']:root[k]=None
    w('root-authority.template.json',root)
    w('config.template.json',dict(schemaVersion=1,state='SECRET_NORMAL_OFF_FREEZER_CONFIG_V1',nativeSourceIndex=c['nativeSourceIndex'],freezerIndex=None,rootAuthority=None))
    w('future-source-review-contract.json',dict(schemaVersion=1,state='PROSPECTIVE_SECRET_NORMAL_OFF_FREEZER_SOURCE_REVIEW_V1',
        requiredState='INDEPENDENT_CRYPTO_OWNER355_SECRET_FREEZER_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=None,nativeSourceIndexSha256=c['nativeSourceIndex']['sha256'],
        actualBuildReviewIndexSha256=None if c['actualBuildReview']is None else c['actualBuildReview']['index']['sha256'],
        requiredFixedValues=dict(schemaVersion=1,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeFreezeActionsInvoked=False),
        actualIndependentSourceReview=None,rootFreezeAuthority=None,actualFreezeReceipt=None,issuesNoAuthority=True))
    print(json.dumps(dict(sourceDataPrepared=True,actualBuildReviewBound=c['actualBuildReview']is not None,rootAuthority=None)))


if __name__=='__main__':main()
