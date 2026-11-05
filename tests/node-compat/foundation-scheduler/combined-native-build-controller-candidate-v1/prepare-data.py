"""Populate SOURCE descriptor/templates only. Never copies caches or runs tools."""
from pathlib import Path
import hashlib,json,os,shutil,stat
P=Path(__file__).resolve().parent;REPO=P.parents[3];S=P.parent
A=S/'combined-native-integration-candidate-v1';STAGE=S/'independent-combined355-source-stage-results-review-v1'
SOURCE=Path('/private/tmp/starling-node-compat/combined-native355-v1-source');WORK=Path('/private/tmp/starling-node-compat/combined-native355-v1-build')
def d(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def load(p):return json.loads(Path(p).read_bytes())
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def pair(p):return dict(index=d(p/'index.json'),result=d(p/'results.json'))
old=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build')
copies=[]
for target in ['componentize-source.tar.gz','spidermonkey-release.tar.gz','openssl-source.tar.gz','tools/bin/cbindgen']:
    p=old/target;mode=stat.S_IMODE(p.stat().st_mode);copies.append(dict(source=d(p),target=target,sourceMode=mode,outputMode=mode))
sdk=next(old.glob('engine-*/_deps/wasi-sdk-subbuild/wasi-sdk-populate-prefix/src/wasi-sdk-30.0-arm64-macos.tar.gz'))
cache=dict(schemaVersion=1,state='FINITE_COMBINED355_PRIVATE_IMMUTABLE_CACHE_PLAN_V1',workRoot=str(WORK),copies=copies,totalCopyBytes=sum(r['source']['bytes']for r in copies),sdkArchiveReferenceOnly=d(sdk),sdkTreeOrBuildObjectsReused=False,globalRustupCargoMutationAllowed=False,privateRustupHome=str(WORK/'rustup-home'),privateCargoHome=str(WORK/'cargo-home'),networkScope='Future real recipe may populate only new private CPM/Rustup/Cargo caches; archive pins and completed actual provenance remain required.',sdkReuseLimit='SDK archive is an authenticated original reference, not seeded or redirected; actual new CPM downloaded archive must have identical SHA and bytes. Existing extracted SDK/build trees are never copied.')
write(P/'cache-plan.json',cache)
monitor=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
life=S/'resource-build-controller-candidate-v1'
stage=load(STAGE/'results.json');stage_root=load(S/'combined-native355-v1-stage-root-authority.json')
node=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
host_path=':'.join([str(node.parent),'/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin','/Users/dan/.cargo/bin','/opt/homebrew/bin','/usr/bin','/bin','/usr/sbin','/sbin'])
host=[]
for name in ['bash','python3','cmake','ninja','rustup','cargo','rustc','curl','tar','patch','make','perl','git','node']:
    selected=shutil.which(name,path=host_path);assert selected,name;host.append(dict(name=name,selectedAlias=selected,executable=d(Path(selected).resolve())))
env=dict(PATH=str(WORK/'tools/bin')+':'+host_path,NODE_COMPAT_BUILD_ROOT=str(WORK),NODE_COMPAT_NODE=str(node),NODE_COMPAT_JOBS='1',NODE_COMPAT_GC_STRESS='0',NODE_COMPAT_ABI_FIX='1',NODE_COMPAT_BIGINT_FIX='1',NODE_COMPAT_OOM_TESTING='0',NODE_COMPAT_BUILD_TYPE='Release',NODE_COMPAT_ENTROPY_MODE='OFF',NODE_COMPAT_ARTIFACT_TAG='combined355v1',BINARYEN_CORES='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='1',CARGO_INCREMENTAL='0',CCACHE_DISABLE='1',SCCACHE_DISABLE='1',RUSTUP_HOME=str(WORK/'rustup-home'),CARGO_HOME=str(WORK/'cargo-home'),RUSTUP_TOOLCHAIN='1.88.0')
for flag in ['PATH','EVENTS','STRING_DECODER','ASSERT','QUERYSTRING','UTIL','STREAM_WEB','INTERNAL_TICKS','CLASSIC_STREAMS','ZLIB','STREAM_CONSUMERS']:env['NODE_COMPAT_'+flag]='1'
refs=dict(schemaVersion=1,state='COMBINED355_NORMAL_OFF_BUILD_SOURCE_REFERENCES_V1',integrationIndex=d(A/'index.json'),integrationSourceReview=pair(S/'independent-combined355-native-integration-source-review-v1'),stageControllerIndex=d(S/'combined-native-stage-controller-candidate-v1/index.json'),actualStageReview=pair(STAGE),stageDescriptors={k:stage[k]for k in ['actualStageResult','externalParentTerminal','rootAuthority','rootConfig','rootObservation']},stageResult=stage['actualStageResult'],stageCopyPlan=d(S/'combined-native-stage-controller-candidate-v1/stage-copy-plan.json'),monitorIndex=d(monitor/'index.json'),monitorEntry=d(monitor/'monitor.py'),lifecycleIndex=d(life/'index.json'),lifecycleEntry=d(life/'lifecycle.py'),cachePlan=d(P/'cache-plan.json'),sdkArchive=d(sdk),node=d(node),pythonExecutable=stage_root['pythonExecutable'],bash=next(r['executable']for r in host if r['name']=='bash'),hostPath=host_path,hostTools=host,buildEnvironment=env,recipe=d(SOURCE/'tests/node-compat/build-engine.sh'),policy=d(SOURCE/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/policy.json'),helper=d(SOURCE/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/layer-policy.py'),metadataModel=d(SOURCE/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/native-admission-model.py'),artifactBasename='starlingmonkey_embedding.abi-i32-i64-v1.combined355-v1.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1.combined355v1.wasm',controllerSourceReview=None,rootBuildAuthority=None,actualBuildResult=None,operationalAdmission=False)
families=[A,S/'combined-native-stage-controller-candidate-v1',S/'independent-combined355-native-integration-source-review-v1',S/'independent-combined355-stage-controller-source-review-v1',STAGE,monitor,life,S/'independent-resource-build-controller-source-review-v1']
refs['families']=[d(p/'index.json')for p in families]
write(P/'references.json',refs)
files={}
def add(r):
    r={k:r[k]for k in ['path','sha256','bytes']}
    if r['path']in files:assert files[r['path']]==r
    files[r['path']]=r
for r in load(STAGE/'input-hashes.json')['files']:add(r)
for p in families:
    add(d(p/'index.json'))
    for r in load(p/'index.json')['files']:add(dict(path=str(p/r['path']),sha256=r['sha256'],bytes=r['bytes']))
for r in copies:add(r['source'])
for r in host:add(r['executable'])
for r in [refs['sdkArchive'],refs['node'],refs['pythonExecutable'],d(REPO/'tests/node-compat/foundation-crypto/ownership-secret-build-controller-candidate-v1/controller.py')]:add(r)
rows=sorted(files.values(),key=lambda r:r['path'])
write(P/'source-inputs.json',dict(schemaVersion=1,role='COMPLETE_FINITE_ACTUAL_STAGE_ORIGINAL_AND_CONFIGURED_INPUTS_PLUS_EXPLICIT_BUILD_DEPENDENCIES',files=rows,modeRows=[dict(file=r,mode=stat.S_IMODE(Path(r['path']).stat().st_mode))for r in rows],originalContextsPreserved=True,operatingSystemEntireFilesystemSealed=False))
root=dict(schemaVersion=1,state='UNISSUED_COMBINED355_NORMAL_OFF_BUILD_ROOT_AUTHORITY_V1',phase=None,variant='normal-off',buildAllowed=False,sourceIndex=refs['integrationIndex'],controllerIndex=None,controllerEntry=None,controllerSourceReview=None,integrationSourceReview=refs['integrationSourceReview'],actualStageReview=refs['actualStageReview'],actualStageResult=refs['stageResult'],monitorIndex=refs['monitorIndex'],monitorEntry=refs['monitorEntry'],lifecycleIndex=refs['lifecycleIndex'],lifecycleEntry=refs['lifecycleEntry'],configuredSourceRoot=str(SOURCE),workRoot=str(WORK),freezeRoot='/private/tmp/starling-node-compat/combined-native355-v1-freeze',buildOutputRoot='/private/tmp/starling-node-compat/combined-native355-v1-normal-off-build-root',externalOutputRoot='/private/tmp/starling-node-compat/combined-native355-v1-normal-off-build-external-root',nativeSourceFiles=355,retainedParentNativeFiles=348,changedNativeFiles=7,selectedManifestCount=11,externalEmbeddingSources=3,stageCopies=1613,externalParentDeadlineSeconds=7200,requiredStartFreeBytes=2147483648,stopBelowFreeBytes=838860800,parallelBuilds=1,buildEnvironment=env,cacheSeedCopiesAllowed=False,cachePlan=refs['cachePlan'],privateRustupAndCargoHomesRequired=True,dependencyNetworkWithinBuildAllowed=False)
for key in ['stageAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','componentAllowed','guestAllowed','keyOperationsAllowed','gcAllowed','gcReconfigureAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:root[key]=False
for key in ['actualBuildResult','actualBuildReview','actualFreezeResult','reviewedNativePins','runtimeAuthority']:root[key]=None
write(P/'root-authority.template.json',root)
write(P/'config.template.json',dict(schemaVersion=1,state='COMBINED355_NORMAL_OFF_BUILD_CONFIG_V1',controllerIndex=None,sourceIndex=refs['integrationIndex'],rootAuthority=None))
write(P/'future-source-review-contract.json',dict(schemaVersion=1,state='PROSPECTIVE_COMBINED355_BUILD_SOURCE_REVIEW_CONTRACT_V1',requiredState='INDEPENDENT_COMBINED355_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1',requiredFixedValues=dict(schemaVersion=1,integrationSourceIndexSha256=refs['integrationIndex']['sha256'],actualStageReviewIndexSha256=refs['actualStageReview']['index']['sha256'],genericMonitorSourceIndexSha256=refs['monitorIndex']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeBuildActionsInvoked=False),requiredOwnIndexBinding='controllerSourceIndexSha256 must equal this complete sealed family index.json SHA256',actualPeer=None,grantsAnyActionAuthority=False))
print(json.dumps(dict(state='SOURCE_DATA_PREPARATION_ONLY',sourceInputs=len(rows),cacheCopies=4,cacheCopyBytes=cache['totalCopyBytes'],sdkVersion30=True,actualStageReview=refs['actualStageReview'],ownerActionsInvoked=False)))
