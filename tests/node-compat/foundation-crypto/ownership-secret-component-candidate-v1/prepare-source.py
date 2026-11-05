"""Author the new construction Source/DATA only; no JS/helper/tool is evaluated."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
K=HERE.parent
def row(path):
    p=Path(path);assert p.is_file()and not p.is_symlink();h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def read(p):return json.loads(Path(p).read_bytes())
def write(n,v):(HERE/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def descriptors(v):
    if type(v)is dict:
        if set(v)=={'path','sha256','bytes'}:yield v
        else:
            for x in v.values():yield from descriptors(x)
    elif type(v)is list:
        for x in v:yield from descriptors(x)
def main():
    assert not(HERE/'index.json').exists(),'Sealed Source requires a successor'
    retained=K/'ownership-secret-retained-bootstrap-candidate-v1';r=read(retained/'references.json');base=read(retained/'source-inputs.json')
    proof=K/'independent-ownership-secret-retained-preflight-results-review-v1';pair=dict(index=row(proof/'index.json'),result=row(proof/'results.json'))
    assert pair['index']['sha256']=='d80e114275a9e69f557568a9266b680ce0829dbda62f345192974c384eef421e'
    result=read(pair['result']['path']);record=read(result['recordData']['path']);history=record['historicalBootstrap']
    donor=K/'ownership-component-candidate-v1';packmap=row(donor/'packaging-context.json');package=read(packmap['path'])
    guest=K/'ownership-validation-candidate-v1';context=read(guest/'integration-contract.json');scope=read(guest/'scope-and-followons.json')
    refs=dict(schemaVersion=1,state='SOURCE_ONLY_SECRET355_COMPONENT_CONSTRUCTION_REFERENCES_V1',originalRoot=str(HERE),
        retainedSourceIndex=row(retained/'index.json'),retainedApi=row(retained/'retained-bootstrap.mjs'),
        retainedSourcePeer=result['sourceIndependentReview'],actualRetainedPreflightReview=pair,actualRetainedPreflightContract=row(proof/'result-contract.json'),actualRetainedRecordData=result['recordData'],actualHistoricalBootstrapReview=r['actualBootstrapReview'],
        priorReadOnlyConfigData=result['rootConfig'],priorReadOnlyAuthorityData=result['rootAuthority'],
        engine=r['engine'],metadata=r['metadata'],freezeReceipt=r['freezeReceipt'],node=r['node'],
        guest=row(HERE/'guest.mjs'),wit=row(HERE/'public-abi.wit'),manifestSchema=row(Path(history['sourceRoot'])/'builtins/node-compat/manifest.schema.json'),
        packagingMap=packmap,packagingHelper=row(donor/'packaging.mjs'),durableHelper=row(donor/'durable.mjs'),abiHelper=row(donor/'abi.mjs'),
        guestSourceIndex=row(guest/'index.json'),guestSourcePeer=read(donor/'prerequisites.json')['guestReview'],
        monitor=dict(path=str(K/'ownership-gc-build-controller-candidate-v1/monitor.py'),sha256='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe',bytes=15094),
        physicalRoles=dict(configuredSourceRoot=history['configuredSourceRoot'],frozenNativeSourceRoot=history['sourceRoot'],frozenEmbeddingSourceRoot=history['componentizeSourceRoot'],nativeWorkRoot=history['workRoot'],packagingRoot=package['packagingRoot'],toolchainRoot=package['toolchainRoot'],packagerRoot=package['packagerRoot']),
        currentVerificationFields=sorted(record['currentVerification']),
        outputRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-component-v1',externalRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-component-v1-external-root',
        componentSourcePeer=None,rootAuthority=None,actualComponent=None,actualRuntimeAuthority=None)
    write('references.json',refs)
    files={x['path']:x for x in base['files']};families={x['path']:x for x in base['families']}
    for ix in [refs['retainedSourceIndex'],refs['retainedSourcePeer']['index'],pair['index'],row(donor/'index.json'),row(K/'ownership-component-candidate-v3/index.json'),refs['guestSourceIndex'],refs['guestSourcePeer']['index']]:families[ix['path']]=ix
    for ix in families.values():
        assert row(ix['path'])==ix;files[ix['path']]=ix
        for m in read(ix['path'])['files']:
            d=dict(m,path=str(Path(ix['path']).parent/m['path']));assert row(d['path'])==d;files[d['path']]=d
    for d in descriptors(refs):assert row(d['path'])==d;files[d['path']]=d
    publication=package['publicationIndex'];assert row(publication['path'])==publication;files[publication['path']]=publication
    for m in package['files']:
        d=dict(path=str(Path(package['publicationRoot'])/m['path']),sha256=m['sha256'],bytes=m['bytes']);assert row(d['path'])==d;files[d['path']]=d
    # Own files are in the future own family, not this external ledger.
    for path in list(files):
        if str(Path(path).parent)==str(HERE):del files[path]
    write('source-inputs.json',dict(schemaVersion=1,files=sorted(files.values(),key=lambda d:d['path']),families=list(families.values()),completeDeclaredRuntimeIntake=True,allSourceAndProtectionBeforeFirstCustomImport=True,oldCostOrNativeActionStatesConsumed=False,preparationOnly=True))
    write('future-validation-workload.json',dict(schemaVersion=1,state='SOURCE_ONLY_FULL_SECRET355_OWNER_VALIDATION_REQUIREMENTS_V1',ordinaryCases=scope['ordinaryCases'],normalSchedule=context['normalSchedule'],proposedGuestAbi=context['proposedGuestAbi'],fullInheritedFutureRequirements=context['futureRuntimeRequirements'],
        actualConstructionNativeContext='New7eb/901c/CBF/da258 complete355 manifest, inherited owner/prototype policy plus actual secret-failure-v2 three-file layer. Old68b/36bd/c3fb context is ancestry DATA only.',
        prototypeProbePrecondition='Only the real reviewed guarded901c artifact, matching full current355 sourceManifest and its inherited owner guard plus new352+3 secret-failure layer. Never old unsafe prototype artifact.',
        case3MayBeOmitted=False,allRetainedAndFreshRawReturnsRequired=True,fullTagBytesAndBooleansAndCountersRequired=True,constructingComponentDoesNotCompleteRuntimeValidation=True,
        noKeyOrCryptoOrAsyncWorkAtInit=True,publicNodeCryptoAdmitted=False,globalWebCryptoOnly=True,noDebugOomFaultGcResetAllowed=True,
        untouchedFixtureScopeLimits=scope['knownLimits'],hmacDoesNotExerciseRsaEcAllocationFailures=True,rootRuntimeAuthority=None,actualComponentReview=None,actualRuntimeResults=None,operationalAdmission=False))
    denied=['ordinaryGuestExportsAllowed','keyOrCryptoOperationsAllowed','gcPressureAllowed','originalOneShotApiAllowed','originalHelperAllowed','historicalCallableAllowed','normalOrGcBuildAllowed','metadataProjectionAllowed','otherVariantsAllowed','generatedModuleImportAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']
    write('future-root-authority.template.json',dict(schemaVersion=1,state=None,phase=None,sourceIndex=None,entry=None,sourceIndependentReview=None,componentBuildAllowed=None,componentInitializationAllowed=None,retainedReadOnlyApiAllowed=None,
        actualRetainedPreflightReview=pair,retainedConfig=None,variant='normal-off',engineSha256=r['engine']['sha256'],nativeSourceFiles=355,outputRoot=refs['outputRoot'],externalRoot=refs['externalRoot'],enclosingNodeDeadlineSeconds=1800,enclosingPhaseDeadlineSeconds=2400,maxComponentBytes=67108864,actualComponentReview=None,actualRuntimeAuthority=None,**{k:False for k in denied}))
    write('future-config.template.json',dict(schemaVersion=1,state='SECRET355_COMPONENT_CONFIG_V1',sourceIndex=None,rootAuthority=None))
    write('future-source-review-contract.json',dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_COMPONENT_SOURCE_REVIEW_PASSED_V1',componentSourceIndexSha256=None,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,actualComponentProof=None))
    write('enclosing-monitor-contract.json',dict(schemaVersion=1,state='SOURCE_ONLY_SECRET355_COMPONENT_ENCLOSING_ROOT_MONITOR_V1',monitor=refs['monitor'],api='monitor(argv,cwd,environment,output,timeout_seconds,authority)',
        futureArgv=[r['node']['path'],str(HERE/'build.mjs'),'CONFIG_DESCRIPTOR_JSON'],nodeDeadlineSeconds=1800,wholeRootDeadlineSeconds=2400,
        requiredEnvironment=dict(NODE_COMPAT_TOOLCHAIN=package['toolchainRoot'],NODE_COMPAT_COMPONENTIZE_MODULE=str(Path(package['packagerRoot'])/'src/componentize.js')),
        requiredEvidence='Full external raw streams/durable started+owned records+terminal, exact actual argv, raw0/no timeout/no forced cleanup/no errors/signals/all owned processes/groups gone before any artifact acceptance. Existing original0af API only; no invented loader or PID.',
        actualRootAuthority=None,actualInvocation=None,actualTerminal=None,grantsAnyAction=False))
    (HERE/'build.mjs').write_bytes((HERE/'caller-primitives.mjs').read_bytes()+(HERE/'caller-body.mjs').read_bytes())
    print(json.dumps(dict(sourceOnly=True,files=len(files),families=len(families),wholeSelectedManifests=11,guestByteExact=row(HERE/'guest.mjs')['sha256']=='26e48b2117eb232cb20c232f4c94b0bba1f359a9be0806629819e2caf9508c45',actions=0)))
if __name__=='__main__':main()
