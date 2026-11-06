"""Own revalidated-artifact freeze. Uses genuine P3 admission and generic copies.
No BUILD-success facade or old freeze/bootstrap frame is constructed.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,traceback

def ownership_model(current,held,expected):
    assert stat.S_ISDIR(current.st_mode)and stat.S_IMODE(current.st_mode)==0o700
    assert(current.st_dev,current.st_ino)==expected==(held.st_dev,held.st_ino)
    return True

def selected_plan(frame,metadata):
    io=frame['io'];refs=frame['refs'];source=Path(refs['configuredSourceRoot']);work=Path(refs['workRoot']);plan=[];seen=set()
    def add(d,name,role):
        assert name and not name.startswith('/')and all(p not in('','.','..')for p in name.split('/'))and '\\'not in name and name not in seen
        seen.add(name);io.checked(d);plan.append(dict(source=d,destination=name,role=role))
    add(refs['engine'],'normal-off.engine.wasm','unchanged-raw9aec-native-engine-DATA')
    add(refs['metadata'],'normal-off.engine.wasm.build.json','unchanged-raw83-metadata-original-paths')
    stage=io.read(refs['stageJournal']);assert stage['state']=='NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGED_NOT_BUILT_V2'and len(stage['copies'])==1642
    for r in stage['copies']:add(dict(path=str(source/r['path']),sha256=r['sha256'],bytes=r['bytes']),'source/'+r['path'],'current-full-staged1642-source-and-tool-DATA')
    assert len(stage['embeddingDataCompleted'])==3
    for r in stage['embeddingDataCompleted']:add(r['target'],'stage-embedding-reference/'+r['source']['path'],'historical-staged-embedding-reference-not-configured-source')
    external=Path(metadata['combinedNativeSourcePolicy']['externalConfiguredSourceRoot'])
    for r in metadata['componentizeSourceManifest']:
        p=external/r['path'];add(dict(path=str(p),sha256=r['sha256'],bytes=p.stat().st_size),'componentize-source/'+r['path'],'actual-configured-external-embedding-source')
    for r in io.read(refs['workCopyPlan'])['files']:add(r['source'],r['destination'],';'.join(r['roles']))
    for r in frame['ownRows']:add(r,'artifact-tools/source/'+Path(r['path']).relative_to(Path(frame['own']['path']).parent).as_posix(),'complete-own-freezer-source-capsule')
    # Original P3 references, policy/helper/recipe and their unchanged owner identity
    # remain separate DATA roles, never new own admission/authentication states.
    for key,name in [('producerReferences','references.json'),('activePolicy','policy.json'),('activeRecipe','build-engine.sh'),('activeHelper','layer-policy.py'),('producerAdmission','admission.py'),('producerIo','io_guard.py')]:add(refs[key],'producer-source/'+name,'genuine-original-P3-producer-DATA')
    for prefix,pair,contract in [('artifact-review',refs['artifactReview'],refs['artifactContract']),('freezer-source-review',frame['root']['sourceReview'],frame['root']['sourceReviewContract'])]:
        for r in io.family(pair['index']):add(r,prefix+'/'+Path(r['path']).relative_to(Path(pair['index']['path']).parent).as_posix(),'complete-review-family-DATA-no-nested-physical-normalization')
    actual=io.read(refs['artifactResult'])
    payloads=dict(result=refs['artifactResult'],rawMetadata=frame['proof']['rawMetadata'],inputHashes=refs['artifactLedger'],referenceAliases=refs['referenceAliases'],distributionData=refs['distributionData'],producerAdmission=frame['proof']['producerAdmissionReturn'])
    for role,d in payloads.items():add(d,'revalidation-data/'+role+'.json','whole-original-read-only-revalidation-DATA')
    for role,d in dict(buildResult=refs['originalBuildResult'],rootObservation=refs['originalBuildObservation'],reviewIndex=refs['originalFailureReview']['index'],reviewResult=refs['originalFailureReview']['result'],reviewContract=refs['originalFailureContract'],failedReadOnlyRoot=refs['failedReadOnlyObservation']).items():add(d,'original-failure-data/'+role+'.json','original-failed-phase-witness-DATA-not-relocated-whole-family')
    add(refs['artifactTrees'],'reference-closure/artifact-trees.json','complete-eleven-original-trees-DATA-not-distribution-copies')
    add(refs['referenceAdditions'],'reference-closure/additions.json','explicit-current-tree-file-coverage-additions')
    add(refs['sourceInputs'],'reference-closure/source-inputs.json','original-reference-protection-descriptors')
    add(frame['configRow'],'provenance/config.json','new-freeze-config')
    add(frame['config']['rootAuthority'],'provenance/root-authority.json','new-freeze-only-Root-authority')
    assert len(plan)<=4096 and len(seen)==len(plan)
    for item in metadata['selectedModuleManifests']:assert 'source/'+item['path']in seen
    return plan

def run(frame,recheck):
    io=frame['io'];refs=frame['refs'];root=Path(refs['freezeRoot'])
    assert not root.exists()and not root.is_symlink();assert os.statvfs(root.parent).f_bavail*os.statvfs(root.parent).f_frsize>=2147483648
    recheck(frame);os.umask(0o077);root.mkdir(mode=0o700)
    fd=os.open(str(root),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);held=os.fstat(fd)
    frame.update(freezeHandle=fd,freezeIdentity=(held.st_dev,held.st_ino),creationAllowed=True)
    generated={}
    def write(name,data):
        recheck_owner();io.confined(name);p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
        for q in(p,*p.parents):assert not q.is_symlink()
        with p.open('xb')as f:os.fchmod(f.fileno(),0o600);assert f.write(data)==len(data);f.flush();os.fsync(f.fileno())
        io.fsync_dir(p.parent);d=io.row(p);generated[name]=d;recheck_owner();return d
    def json_write(name,value):return write(name,(json.dumps(value,indent=2)+'\n').encode())
    def recheck_owner():
        ownership_model(root.lstat(),os.fstat(fd),frame['freezeIdentity'])
    try:
        attempt=json_write('admission-attempt.json',dict(schemaVersion=1,argumentContextKind='NEW_FREEZE_ARGUMENT_CONTEXT_ORIGINAL_P3_OWNER_V1',producerIndex=refs['producerIndex'],producerReferences=refs['producerReferences'],newRootAuthority=frame['config']['rootAuthority'],oldBootstrapFrameClaimed=False,callback='New freeze-owned current recheck; permits this exclusive created root, never the old freeze-absent callback',engineExecuted=False,cryptoOperationsInvoked=False))
        recheck(frame)
        # Genuine existing original API/owner/whole refs. No old controller
        # bootstrap, successfulBUILD model, or revalidation bootstrap is called.
        admission=load(refs['producerAdmission'],'genuine_original_P3_admission',io)
        argument=dict(io=io,refs=io.read(refs['producerReferences']),ownIndex=refs['producerIndex'])
        returned=admission.admit(argument,lambda unused:recheck(frame))
        whole=json_write('producer-admission-return.json',returned) # whole raw DATA before assertions
        assert returned==io.read(frame['proof']['producerAdmissionReturn'])
        assert returned['controllerSourceIndexSha256']==refs['producerIndex']['sha256']and returned['rawMetadataFields']==83 and returned['metadata']==refs['metadata']
        meta=io.read(refs['metadata']);plan=selected_plan(frame,meta)
        assert sum(r['source']['bytes']for r in plan)+838860800<=os.statvfs(root).f_bavail*os.statvfs(root).f_frsize
        plan_row=json_write('actual-copy-plan.json',dict(schemaVersion=1,copies=plan,fullReferenceClosureVerifiedBeforeAndAfter=True,referencesNotAllPhysicallyCopied=True))
        control=json_write('freezer-control.json',dict(schemaVersion=1,freezerSourceIndex=frame['own'],producerIndex=refs['producerIndex'],artifactReview=refs['artifactReview'],artifactContract=refs['artifactContract'],originalRecipeExitCode=0,originalParentExitCodes=[1,1],originalBuildPreservationPassed=False,originalBuildAccepted=False,indexException=refs['indexException'],rawMetadataUnchanged=True,rawMetadataOriginalPathsPreserved=True,freshProducerAdmissionCalls=1,originalNinjaCommandReexecuted=False,fullReferenceFiles=len(frame['captured']),elevenDistributionAndSourceTreesChecked=True,allLiveReferencesPhysicallyCopied=False,engineExecuted=False,cryptoOperationsInvoked=False,liveEvpSnapshotAdmission=False))
        copies=load(frame['ownByName']['copy_io.py'],'own_generic_P3_copy_with_explicit_fchmod',io)
        targets=[dict(original=Path(r['source']['path']),target=root/r['destination'],sha256=r['source']['sha256'],shared=False)for r in plan]
        receipt_path=root/'normal-off-freeze-receipt.json';copies.validate_plan(targets,receipt_path,root)
        recheck(frame);recheck_owner();copies.execute_plan(targets,root);recheck_owner();recheck(frame)
        rows=[];identities=set()
        for r in plan:
            target=root/r['destination'];d=io.row(target);s=target.stat();old=io.checked(r['source']).stat()
            assert s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and(s.st_dev,s.st_ino)!=(old.st_dev,old.st_ino)and(s.st_dev,s.st_ino)not in identities
            identities.add((s.st_dev,s.st_ino));assert(d['sha256'],d['bytes'])==(r['source']['sha256'],r['source']['bytes'])
            rows.append(dict(d,original=r['source'],role=r['role']))
        rows += [dict(d,original=None,role='new-freeze-admission-control-or-plan-DATA')for d in generated.values()]
        receipt=dict(schemaVersion=1,state='HASH_HMAC357_NORMAL_OFF_REVALIDATED_FREEZE_COMPLETE_UNREVIEWED_V1',variant='normal-off',freezerSourceIndex=frame['own'],producerIndex=refs['producerIndex'],integrationIndex=refs['integrationIndex'],artifactReview=refs['artifactReview'],artifactContract=refs['artifactContract'],rootAuthority=frame['config']['rootAuthority'],sourceReview=frame['root']['sourceReview'],rootOwnership=dict(device=held.st_dev,inode=held.st_ino,mode=0o700,exclusiveRootCreated=True,rootHandleNoFollow=True),configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],freezeRoot=str(root),sourceRoot=str(root/'source'),componentizeSourceRoot=str(root/'componentize-source'),engine=dict(refs['engine'],path=str(root/'normal-off.engine.wasm')),metadata=dict(refs['metadata'],path=str(root/'normal-off.engine.wasm.build.json')),rawMetadataFields=83,nativeSourceFiles=357,externalEmbeddingSources=3,stagedSourceAndToolFiles=1642,stagedEmbeddingReferences=3,selectedWholeManifests=12,compileDatabaseRows=69,policyCpp=63,strictCpp=4,privateCpp=7,separateEmbeddingCpp=1,originalRecipeExitCode=0,originalParentExitCodes=[1,1],originalBuildPreservationPassed=False,originalBuildAccepted=False,indexException=refs['indexException'],copyPlan=plan_row,control=control,admissionAttempt=attempt,freshProducerAdmission=whole,freshProducerAdmissionCalls=1,originalNinjaCommandReexecuted=False,copies=rows,currentReferenceFiles=len(frame['captured']),historicalCurrentLedger=refs['artifactLedger'],historicalCurrentLedgerFiles=21451,referenceTrees=11,fullCurrentReferenceClosureChecked=True,referencesNotAllPhysicallyCopied=True,rawMetadataUnchanged=True,rawMetadataOriginalPathsPreserved=True,originalCompilerRawExitProofClaim=False,liveEvpSnapshotAdmission=False,engineExecuted=False,guestExecuted=False,cryptoOperationsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False,pinsAdopted=False)
        for d in sorted([p for p in root.rglob('*')if p.is_dir()],key=lambda p:len(p.parts),reverse=True):assert stat.S_IMODE(d.stat().st_mode)==0o700;io.fsync_dir(d)
        receipt_row=json_write('normal-off-freeze-receipt.json',receipt);os.fsync(fd)
        verified=load(frame['ownByName']['verify_frozen.py'],'own_frozen_only_hash357_verifier',io).verify_frozen(receipt_row,frame['own']['sha256'])
        recheck(frame);print(json.dumps(verified),flush=True);return verified
    except BaseException as error:
        try:json_write('failed-freeze.json',dict(schemaVersion=1,state='FAILED_UNACCEPTED',errorType=type(error).__name__,message=str(error),traceback=traceback.format_exc(),availableGeneratedEvidence=generated,engineExecuted=False,cryptoOperationsInvoked=False,operationalAdmission=False))
        except BaseException:pass
        raise
    finally:
        try:recheck(frame)
        finally:os.close(fd);frame['freezeHandle']=None

def load(r,name,io):
    spec=importlib.util.spec_from_file_location(name,io.checked(r));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
