"""Dormant combined355 retry. Own recipe/context, unchanged staged355; standard-library bootstrap."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,stat,sys,time
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/combined-native-build-controller-candidate-v2'
INTEGRATION=REPO/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1'
SOURCE_SHA='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65'
SOURCE=Path('/private/tmp/starling-node-compat/combined-native355-v1-source')
WORK=Path('/private/tmp/starling-node-compat/combined-native355-v2-build')
FREEZE=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze')
BUILD_OUTPUT=Path('/private/tmp/starling-node-compat/combined-native355-v2-normal-off-build-root')
OUT=Path('/private/tmp/starling-node-compat/combined-native355-v2-normal-off-build-external-root')
TIMEOUT=7200
START_FREE=2147483648
STOP_FREE=838860800
OBSERVER=Path('/private/tmp/starling-node-compat/combined-native355-v2-build-root-observer')
ENV_POLICY=dict(schemaVersion=1,mandatoryBeforeControllerSpawn=True,removePrefixes=['BASH_FUNC_'],removeExactNames=['BASH_ENV','ENV','SHELLOPTS','BASHOPTS','CDPATH','GLOBIGNORE'],preserveExactNames=['HOME','home','CODEX_HOME'],rootAuthorityMustBindPolicy=True,rootLauncherMustEnforcePolicy=True,actualChildMustContainNoRemovedEntries=True,recordRemovedVariableNamesOnly=True,recordEnvironmentValues=False,scope='Known inherited Bash function and startup controls; not an OS or universal environment sandbox')


def clean_environment(parent):
    removed=sorted(k for k in parent if k.startswith(tuple(ENV_POLICY['removePrefixes']))or k in ENV_POLICY['removeExactNames'])
    child={k:v for k,v in parent.items()if k not in removed}
    for k in ENV_POLICY['preserveExactNames']:assert(k in child)==(k in parent)and child.get(k)==parent.get(k)
    assert not any(k.startswith(tuple(ENV_POLICY['removePrefixes']))or k in ENV_POLICY['removeExactNames']for k in child)
    return child,removed


def require_clean_environment(parent):
    child,removed=clean_environment(parent);assert removed==[] and child==parent,'Clean launcher entry required before controller/recipe'



def checked(row):
    assert type(row)is dict and set(row)=={'path','sha256','bytes'}
    assert type(row['bytes'])is int and row['bytes']>=0
    assert isinstance(row['sha256'],str)and len(row['sha256'])==64 and all(c in '0123456789abcdef'for c in row['sha256'])
    p=Path(row['path']);assert p.is_absolute()and '..'not in p.parts
    if str(p).startswith('/tmp/'):p=Path('/private'+str(p))
    for parent in (p,*p.parents):assert not parent.is_symlink(),parent
    before=p.stat();assert stat.S_ISREG(before.st_mode);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=p.stat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    assert before.st_size==row['bytes']and h.hexdigest()==row['sha256'];return p



def descriptor(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    row=dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size);checked(row);return row



def read(row):
    p=checked(row);assert row['bytes']<=32*1024*1024
    raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)



def family(row):
    value=read(row);root=Path(row['path']).parent;rows=[row];seen=set()
    for r in value['files']:
        name=r['path'];assert isinstance(name,str)and name and name not in seen and '\\'not in name and '\0'not in name
        assert not name.startswith('/')and all(p not in ('','.','..')for p in name.split('/'))
        seen.add(name);d=dict(path=str(root/name),sha256=r['sha256'],bytes=r['bytes']);checked(d);rows.append(d)
    actual=set()
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_file():actual.add(str(p.relative_to(root)))
    assert actual==seen|{'index.json'};return rows



def indexed_result(pair):
    rows=family(pair['index']);assert sum(r==pair['result']for r in rows[1:])==1
    return read(pair['result']),rows



def validate_terminal(value,authority):
    assert value['schemaVersion']==1 and value['authority']==authority and value['rawExitCode']==0
    assert value['parentOwnedGroupGone']is True and value['allObservedOwnedGroupsGone']is True
    for k in ['forcedCleanup','timeout']:assert value[k]is False
    for k in ['remainingObservedPids','signals','errors','interruptedSignals']:assert value[k]==[]
    assert value['observedProcesses']and value['finalGroups']and all(g['alive']is False for g in value['finalGroups'])
    return True



def write(path,value):
    with Path(path).open('x')as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())



def load_actual(row,name):
    spec=importlib.util.spec_from_file_location(name,checked(row));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def absent(path):
    for p in (path,*path.parents):assert not p.is_symlink(),p
    assert not path.exists(),path


def root_model(root,own,refs):
    assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_COMBINED355_NORMAL_OFF_BUILD_RETRY_V2'
    assert root['phase']=='native-build-only'and root['variant']=='normal-off'and root['buildAllowed']is True
    assert root['sourceIndex']==refs['integrationIndex']and root['sourceIndex']['sha256']==SOURCE_SHA
    assert root['controllerIndex']==own and own['path']==str(OWN/'index.json')
    assert root['controllerEntry']['path']==str(OWN/'controller.py')
    assert root['configuredSourceRoot']==str(SOURCE)and root['workRoot']==str(WORK)and root['freezeRoot']==str(FREEZE)
    assert root['buildOutputRoot']==str(BUILD_OUTPUT)and root['externalOutputRoot']==str(OUT)
    assert root['actualStageReview']==refs['actualStageReview']and root['actualStageResult']==refs['stageResult']
    assert root['integrationSourceReview']==refs['integrationSourceReview']
    assert root['monitorIndex']==refs['monitorIndex']and root['monitorEntry']==refs['monitorEntry']
    assert root['lifecycleIndex']==refs['lifecycleIndex']and root['lifecycleEntry']==refs['lifecycleEntry']
    assert root['nativeSourceFiles']==355 and root['retainedParentNativeFiles']==348 and root['changedNativeFiles']==7
    assert root['selectedManifestCount']==11 and root['externalEmbeddingSources']==3 and root['stageCopies']==1613
    assert root['externalParentDeadlineSeconds']==TIMEOUT and root['requiredStartFreeBytes']==START_FREE and root['stopBelowFreeBytes']==STOP_FREE
    assert root['parallelBuilds']==1 and root['buildEnvironment']==refs['buildEnvironment']
    assert root['rootEnvironmentPolicy']==ENV_POLICY and root['rootLauncherRequired']is True
    assert root['rootObserverOutputRoot']==str(OBSERVER)
    assert root['retryRecipe']==refs['recipe']and root['retryPolicy']==refs['policy']and root['retryHelper']==refs['helper']
    assert root['failedBuildReview']==refs['failedBuildReview']and root['privateRustupProbeReview']==refs['privateRustupProbeReview']
    assert root['persistentPrivateRustupAutoSelfUpdateDisableRequired']is True and root['oldWorkResumeAllowed']is False
    assert root['cacheSeedCopiesAllowed']is True and root['cachePlan']==refs['cachePlan']
    assert root['privateRustupAndCargoHomesRequired']is True and root['dependencyNetworkWithinBuildAllowed']is True
    for k in ['stageAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','componentAllowed','guestAllowed','keyOperationsAllowed','gcAllowed','gcReconfigureAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:
        assert root[k]is False,k
    for k in ['actualBuildResult','actualBuildReview','actualFreezeResult','reviewedNativePins','runtimeAuthority']:assert root[k]is None,k


def stage_model(value,refs):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_COMBINED355_SOURCE_STAGE_RESULTS_REVIEW_PASSED_V1'and value['verifiedPassed']is True
    assert value['sourceIndexSha256']==SOURCE_SHA and value['controllerSourceIndexSha256']==refs['stageControllerIndex']['sha256']
    assert value['configuredSourceRoot']==str(SOURCE)and value['nativeSourceFiles']==355 and value['stageCopies']==1613
    assert value['retainedParentNativeFiles']==348 and value['changedNativeFiles']==7 and value['selectedManifestCount']==11
    for k in ['actualStageResult','externalParentTerminal','rootAuthority','rootConfig','rootObservation']:assert value[k]==refs['stageDescriptors'][k]
    assert value['actualOwnedStageWorkerExitCode']==0 and value['actualRootControllerExitCode']==0 and value['allObservedOwnedGroupsGone']is True
    assert value['externalEmbeddingSourcesCopiedInStage']==0 and value['externalEmbeddingSourceAncestry']==3
    for k in ['nativeBuildExecuted','engineExecuted','guestExecuted','operationalAdmission','grantsNativeBuildAuthority']:assert value[k]is False


def source_peer_model(value):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_COMBINED355_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V1'
    assert value['sourceIndexSha256']==SOURCE_SHA and value['sourceOnly']is value['sourceReviewPassed']is True
    assert value['nativeSourceFiles']==355 and value['retainedParentNativeFiles']==348 and value['changedNativeFiles']==7
    assert value['selectedManifestCount']==11 and value['ownerActionsInvoked']is value['operationalAdmission']is False


def controller_peer_model(value,own,refs):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_COMBINED355_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V2'
    assert value['controllerSourceIndexSha256']==own['sha256']and value['integrationSourceIndexSha256']==SOURCE_SHA
    assert value['actualStageReviewIndexSha256']==refs['actualStageReview']['index']['sha256']
    assert value['genericMonitorSourceIndexSha256']==refs['monitorIndex']['sha256']
    assert value['requiredRootEnvironmentPolicy']==ENV_POLICY
    assert value['retryRecipeSha256']==refs['recipe']['sha256']
    assert value['failedBuildReviewIndexSha256']==refs['failedBuildReview']['index']['sha256']
    assert value['privateRustupProbeReviewIndexSha256']==refs['privateRustupProbeReview']['index']['sha256']
    assert value['sourceOnly']is value['sourceReviewPassed']is True
    for k in ['ownerActionsInvoked','hostActionsInvoked','nativeBuildActionsInvoked']:assert value[k]is False


def cache_plan_model(plan):
    assert plan['schemaVersion']==1 and plan['state']=='FINITE_COMBINED355_PRIVATE_IMMUTABLE_CACHE_PLAN_V2'
    assert plan['workRoot']==str(WORK)and len(plan['copies'])==4
    assert [r['target']for r in plan['copies']]==['componentize-source.tar.gz','spidermonkey-release.tar.gz','openssl-source.tar.gz','tools/bin/cbindgen']
    assert len({r['source']['path']for r in plan['copies']})==4
    expected=[('8178fb678ec1b8a33bbf3fa8db066bffe4dbf6a92c235150f56622b44ea27e10',162093),('c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b',184568633),('dfdd77e4ea1b57ff3a6dbde6b0bdc3f31db5ac99e7fdd4eaf9e1fbb6ec2db8ce',15344831),('889aa1f25e8d0f0e4c6e304f1032c7d15c708447ce4625b0dd968ffb45b1150b',5789888)]
    assert [(r['source']['sha256'],r['source']['bytes'])for r in plan['copies']]==expected
    for r in plan['copies']:
        assert r['sourceMode']in(0o644,0o755)and r['outputMode']==r['sourceMode']
    assert plan['copies'][3]['outputMode']==0o755
    assert plan['sdkArchiveReferenceOnly']['sha256']=='2c2ed99296857e60fd14c3f40fe226231f296409502491094704089c31a16740'
    assert plan['sdkTreeOrBuildObjectsReused']is False and plan['globalRustupCargoMutationAllowed']is False


def staged_inputs(frame):
    journal=frame['stageJournal'];assert journal['state']=='COMBINED355_SOURCE_STAGED_NOT_BUILT'
    assert journal['sourceIndexSha256']==SOURCE_SHA and journal['configuredSourceRoot']==str(SOURCE)
    assert journal['copies']==journal['copiesCompleted']==frame['copyPlan']and len(journal['copies'])==1613
    target_ids=set();original_ids=set()
    for r in journal['copies']:
        name=r['path'];assert not name.startswith('/')and all(x not in ('','.','..')for x in name.split('/'))
        a=checked(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes'])).stat()
        b=checked(dict(path=str(SOURCE/name),sha256=r['sha256'],bytes=r['bytes'])).stat()
        assert stat.S_IMODE(a.st_mode)==stat.S_IMODE(b.st_mode)==r['sourceMode']and b.st_nlink==1
        old=(a.st_dev,a.st_ino);new=(b.st_dev,b.st_ino);assert old!=new and new not in target_ids
        original_ids.add(old);target_ids.add(new)
    assert len(target_ids)==1613 and not original_ids&target_ids
    assert (SOURCE/'.git/HEAD').read_text()=='54b3329b3ce818fd1f244e871e9c259b63667cda\n'


def host_tools(refs):
    # Exact finite command aliases, not a claim to seal the operating system.
    for r in refs['hostTools']:
        selected=shutil.which(r['name'],path=refs['hostPath'])
        assert selected and str(Path(selected).resolve())==r['executable']['path'],r['name']
        assert checked(r['executable']).stat().st_mode&0o111


def recheck(frame):
    for r in frame['captured']:checked(r)
    for r in frame['familyIndices']:family(r)
    staged_inputs(frame);host_tools(frame['refs'])
    for r in frame['cachePlan']['copies']:assert stat.S_IMODE(checked(r['source']).stat().st_mode)==r['sourceMode']
    for r in frame['inputModes']:assert stat.S_IMODE(checked(r['file']).stat().st_mode)==r['mode']
    for row in frame['protectedTreeInventories']:protected_tree_model(row)


def protected_tree_model(row):
    inventory=read(row);root=Path(inventory['root']);names=set()
    for r in inventory['files']:
        name=r['path'];assert name not in names and not name.startswith('/')and all(p not in('','.','..')for p in name.split('/'));names.add(name)
        p=checked(dict(path=str(root/name),sha256=r['sha256'],bytes=r['bytes']));assert stat.S_IMODE(p.stat().st_mode)==r['mode']
    actual={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}
    assert actual==names
    assert all(not p.is_symlink()for p in root.rglob('*'))


def failure_model(value,refs):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_COMBINED355_NATIVE_BUILD_BOOTSTRAP_FAILURE_REVIEW_PASSED_V1'and value['verifiedPassed']is True
    assert value['integrationSourceIndexSha256']==SOURCE_SHA and value['controllerSourceIndexSha256']==refs['parentControllerIndex']['sha256']
    assert value['rawRecipeExitCode']==value['rawOwnedWorkerExitCode']==value['rootReportedExitCode']==1
    assert value['nativeBuildSucceeded']is value['cmakeGuestCompilationReached']is value['engineArtifactProduced']is value['metadataSidecarProduced']is False
    assert value['sourceAndStageInputsPreserved']is True and value['allObservedOwnedGroupsGone']is True
    assert value['actualBuildResult']==refs['failedBuildResult']and value['rootObservation']==refs['failedBuildObservation']
    assert value['repeatOrResumeGranted']is value['newBuildAuthorityGranted']is False


def probe_model(value,refs):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_RUSTUP_PRIVATE_BOOTSTRAP_PROBE_REVIEW_PASSED_V1'and value['verifiedPassed']is True
    assert value['rawCommandCount']==6 and value['allRawExitCodesZero']is True
    for k in ['privateAutoSelfUpdateDisabled','wasm32Wasip1Installed','repeatedInstallPassed','cargoProxyPassed']:assert value[k]is True
    assert value['nativeBuildAuthorityGranted']is False


def authorize(config_row):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated==1 and Path(__file__).resolve().parent==OWN
    config=read(config_row);assert config['schemaVersion']==1 and config['state']=='COMBINED355_NORMAL_OFF_BUILD_CONFIG_V2'
    root=read(config['rootAuthority']);own=root['controllerIndex'];assert own['path']==str(OWN/'index.json')
    own_rows=family(own);assert root['controllerEntry']in own_rows
    refs=read(next(r for r in own_rows if r['path']==str(OWN/'references.json')))
    assert config['controllerIndex']==own and config['sourceIndex']==refs['integrationIndex']
    root_model(root,own,refs)
    captured=[config_row,config['rootAuthority'],*own_rows];indices=[own]
    manifest=read(next(r for r in own_rows if r['path']==str(OWN/'source-inputs.json')))
    for r in manifest['files']:checked(r);captured.append(r)
    for r in refs['families']:
        captured+=family(r);indices.append(r)
    for key,validator in [('integrationSourceReview',source_peer_model),('actualStageReview',lambda v:stage_model(v,refs))]:
        value,rows=indexed_result(refs[key]);validator(value);captured+=rows;indices.append(refs[key]['index'])
    for key,validator in [('failedBuildReview',lambda v:failure_model(v,refs)),('privateRustupProbeReview',lambda v:probe_model(v,refs))]:
        value,rows=indexed_result(refs[key]);validator(value);captured+=rows;indices.append(refs[key]['index'])
    value,rows=indexed_result(root['controllerSourceReview']);controller_peer_model(value,own,refs)
    captured+=rows;indices.append(root['controllerSourceReview']['index'])
    stage=read(refs['stageResult']);copies=read(refs['stageCopyPlan'])['files']
    plan=read(refs['cachePlan']);cache_plan_model(plan)
    for key in ['monitorEntry','lifecycleEntry']:
        assert refs[key]in captured,'Original executable must be a fully authenticated family member'
    terminal=read(refs['stageDescriptors']['externalParentTerminal']);validate_terminal(terminal,refs['stageDescriptors']['rootAuthority'])
    for key in ['stdout','stderr']:checked(terminal[key]);captured.append(terminal[key])
    assert checked(refs['pythonExecutable'])==Path(sys.executable).resolve()
    frame=dict(config=config,configDescriptor=config_row,root=root,ownIndex=own,refs=refs,captured=captured,familyIndices=indices,stageJournal=stage,copyPlan=copies,cachePlan=plan,inputModes=manifest['modeRows'],protectedTreeInventories=refs['protectedTreeInventories'])
    recheck(frame);return frame


def build_environment(parent,refs):
    blocked=('NODE_COMPAT_','CMAKE_','CARGO_','RUST','CCACHE_','SCCACHE_','CPM_','FETCHCONTENT_','NAPI_RS_','WASMTIME_','DYLD_')
    names=set(ENV_POLICY['removeExactNames'])|{'NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','BASH_ENV','ENV','LD_PRELOAD','LD_LIBRARY_PATH','CC','CXX','CPP','CFLAGS','CXXFLAGS','CPPFLAGS','LDFLAGS','AR','LD','RANLIB','CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','LIBRARY_PATH','COMPILER_PATH','GCC_EXEC_PREFIX','CONFIG_SITE'}
    env={k:v for k,v in parent.items()if not k.startswith(blocked+tuple(ENV_POLICY['removePrefixes']))and k not in names}
    env.update(refs['buildEnvironment'])
    assert env.get('HOME')==parent.get('HOME')and env.get('CODEX_HOME')==parent.get('CODEX_HOME')
    assert env['RUSTUP_HOME']==str(WORK/'rustup-home')and env['CARGO_HOME']==str(WORK/'cargo-home')
    assert env['CARGO_INCREMENTAL']=='0'and env['RUSTUP_TOOLCHAIN']=='1.88.0'
    return env


def stream_copy(source,target):
    # Stream-only seam; tested with in-memory readers/writers, no filesystem.
    digest=hashlib.sha256();size=0
    while True:
        block=source.read(1024*1024)
        if not block:break
        assert type(block)is bytes and target.write(block)==len(block)
        digest.update(block);size+=len(block)
    return dict(sha256=digest.hexdigest(),bytes=size)


def populate_cache(plan,result):
    absent(WORK);WORK.mkdir(mode=0o700)
    for r in plan['copies']:
        original=checked(r['source']);assert stat.S_IMODE(original.stat().st_mode)==r['sourceMode']
        target=WORK/r['target'];target.parent.mkdir(parents=True,exist_ok=True)
        for p in (target,*target.parents):assert not p.is_symlink()
        with original.open('rb')as src,target.open('xb')as dst:
            observed=stream_copy(src,dst);dst.flush();os.fchmod(dst.fileno(),r['outputMode']);os.fsync(dst.fileno())
        assert observed=={k:r['source'][k]for k in ['sha256','bytes']}
        actual=descriptor(target);assert actual['sha256']==r['source']['sha256']and actual['bytes']==r['source']['bytes']
        a=checked(r['source']).stat();b=target.stat();assert(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)and b.st_nlink==1 and stat.S_IMODE(b.st_mode)==r['outputMode']
        result['cacheCopiesCompleted'].append(dict(source=r['source'],target=actual,sourceMode=r['sourceMode'],outputMode=r['outputMode'],distinctInode=True))
        write(BUILD_OUTPUT/('cache-copy-'+str(len(result['cacheCopiesCompleted']))+'.json'),result['cacheCopiesCompleted'][-1])
    for p in [WORK/'rustup-home',WORK/'cargo-home']:p.mkdir(mode=0o700)


def validate_metadata(value,policy,refs):
    assert value['enginePath']==str(WORK/'artifacts'/refs['artifactBasename'])
    assert value['buildRecipeSha256']==refs['recipe']['sha256']and value['sourceManifest']==policy['expectedNativeSourceManifest']
    assert value['componentizeSourceManifest']==policy['expectedComponentizeSourceManifest']and len(value['sourceManifest'])==355
    assert len(value['selectedModuleManifests'])==11 and value['selectedModuleManifests']==policy['selectedModuleManifests']
    assert value['privateRustupBootstrapPolicy']['persistentSetting']=='disable'and value['privateRustupBootstrapPolicy']['privateHomes']==dict(rustup=str(WORK/'rustup-home'),cargo=str(WORK/'cargo-home'))
    checked(value['privateRustupBootstrapPolicy']['beforeInstallRecord']);checked(value['privateRustupBootstrapPolicy']['settingsAtBuildCompletion'])
    assert value['gcStress']is False and value['entropyPolicy']=='off'and value['oomTesting']is False
    assert value['observedCMakeOptions']==value['requestedCMakeOptions']
    for k in ['CMAKE_C_COMPILER_LAUNCHER','CMAKE_CXX_COMPILER_LAUNCHER']:assert value['observedCMakeOptions'][k]==''
    assert value['generatedRustProject']['cargoBuildLocked']is True and value['generatedRustProject']['manifestAndLockCheckedBeforeAndAfterBuild']is True
    assert value['zlibPolicy']['runtimeBackendProof']==dict(verified=False,version=None,vernum=None)
    for key in ['cmakeCachePath','compileCommandsPath']:assert value[key].startswith(str(WORK)+'/')
    sdk=[r for r in value['downloadedArchives']if Path(r['path']).name=='wasi-sdk-30.0-arm64-macos.tar.gz']
    assert len(sdk)==1 and sdk[0]['sha256']==refs['sdkArchive']['sha256']
    checked(dict(path=sdk[0]['path'],sha256=sdk[0]['sha256'],bytes=refs['sdkArchive']['bytes']))
    assert value['wasiSdkVersionFiles']and all(r['contents'].startswith('30.0\n')for r in value['wasiSdkVersionFiles'])


def worker(frame):
    require_clean_environment(dict(os.environ))
    refs=frame['refs'];absent(WORK);absent(BUILD_OUTPUT);absent(FREEZE)
    lifecycle=load_actual(refs['lifecycleEntry'],'genuine_combined355_explicit_build_lifecycle')
    assert lifecycle.REQUIRED_START_FREE==START_FREE and lifecycle.MINIMUM_FREE==STOP_FREE
    recheck(frame);os.umask(0o077)
    def free():
        p=WORK if WORK.exists()else WORK.parent;s=os.statvfs(p);return s.f_bavail*s.f_frsize
    before=lifecycle.prepare_output(BUILD_OUTPUT,free)
    command=[refs['bash']['path'],str(checked(refs['recipe']))]
    result=dict(schemaVersion=1,state='COMBINED355_NORMAL_OFF_NATIVE_BUILD_STARTED',sourceIndexSha256=SOURCE_SHA,controllerIndex=frame['ownIndex'],rootAuthority=frame['config']['rootAuthority'],actualStageReview=refs['actualStageReview'],configuredSourceRoot=str(SOURCE),workRoot=str(WORK),freezeRoot=str(FREEZE),command=command,explicitEnvironment=refs['buildEnvironment'],cacheCopiesCompleted=[],freeBytesBefore=before,requiredStartFreeBytes=START_FREE,stopBelowFreeBytes=STOP_FREE,diskSpaceSampleSeconds=1,periodicDiskFloorMonitoringRequested=True,diskFreeSamplesDuringBuildCommand=[],diskFloorChecksDuringCacheCopies='before and after the bounded four-copy population; not during individual copies',parallelBuilds=1,externalParentDeadlineSeconds=TIMEOUT,rawChildExitCode=None,engineExecuted=False,guestExecuted=False,gcReconfigureAllowed=False,operationalAdmission=False)
    write(BUILD_OUTPUT/'launch.json',result);started=time.monotonic()
    try:
        result['freeBytesBeforeCacheCopies']=free();assert result['freeBytesBeforeCacheCopies']>=START_FREE
        populate_cache(frame['cachePlan'],result)
        result['freeBytesAfterCacheCopies']=free();assert result['freeBytesAfterCacheCopies']>=START_FREE,'Need2GiB again after private cache population'
        env=build_environment(os.environ,refs)
        def build_free():
            observed=free()
            result['diskFreeSamplesDuringBuildCommand'].append(dict(monotonicSeconds=time.monotonic(),freeBytes=observed))
            return observed
        with(BUILD_OUTPUT/'build.log').open('xb')as log:
            result.update(lifecycle.monitor_owned_command(command,str(SOURCE),env,log,build_free));log.flush();os.fsync(log.fileno())
        cleanup=result.get('ownedGroupCleanup')or{}
        if cleanup.get('complete')is not True or cleanup.get('events')or cleanup.get('errors'):
            result.setdefault('finalObservationErrors',[]).append(dict(stage='inner-group-cleanliness',cleanup=cleanup))
        if result.get('rawChildExitCode')==0:
            engine=WORK/'artifacts'/refs['artifactBasename'];metadata=Path(str(engine)+'.build.json')
            value=read(descriptor(metadata));policy=read(refs['policy']);validate_metadata(value,policy,refs)
            # Genuine current355 pure shape model, never an old classifier.
            model=load_actual(refs['metadataModel'],'genuine_combined355_metadata_shape')
            observed=model.validate_metadata(value,policy,refs['policy']['sha256'],refs['helper']['sha256'],refs['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off')
            assert observed==dict(state='FINITE_COMBINED355_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=355,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
            result['engine']=descriptor(engine);result['metadata']=descriptor(metadata);result['metadataShape']=observed
    except BaseException as error:result.setdefault('launcherErrors',[]).append(lifecycle.error_record('build-cache-or-metadata',error))
    finally:
        result['wallSecondsForOperationalRecordOnly']=time.monotonic()-started
        try:
            result['freeBytesAfter']=free()
            if(BUILD_OUTPUT/'build.log').exists():result['buildLog']=descriptor(BUILD_OUTPUT/'build.log')
        except BaseException as error:result.setdefault('finalObservationErrors',[]).append(lifecycle.error_record('final-space-or-log',error))
        try:recheck(frame);result['allSourceStageOriginalAndCacheInputsPreserved']=True
        except BaseException as error:result.setdefault('finalObservationErrors',[]).append(lifecycle.error_record('final-protection-recheck',error))
        lifecycle.finalize_status(result);lifecycle.publish_result(BUILD_OUTPUT,result,writer=write)
    assert result['launcherExitCode']==0;return result


def parent(frame):
    require_clean_environment(dict(os.environ))
    preentry=read(descriptor(OBSERVER/'preentry-environment.json'))
    assert preentry['rootAuthority']==frame['config']['rootAuthority']and preentry['policy']==ENV_POLICY and preentry['requiredEntriesAbsent']is True
    for p in [WORK,FREEZE,OUT,BUILD_OUTPUT]:absent(p)
    monitor=load_actual(frame['refs']['monitorEntry'],'genuine_combined355_owned_build_monitor')
    recheck(frame);OUT.mkdir(mode=0o700)
    argv=[str(checked(frame['refs']['pythonExecutable'])),'-B','-I',str(OWN/'controller.py'),'worker',json.dumps(frame['configDescriptor'],separators=(',',':'))]
    try:terminal=monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OUT,TIMEOUT,frame['config']['rootAuthority'])
    finally:recheck(frame)
    validate_terminal(terminal,frame['config']['rootAuthority']);assert terminal['stderr']['bytes']==0
    actual=descriptor(BUILD_OUTPUT/'result.json');result=read(actual)
    assert result['rootAuthority']==frame['config']['rootAuthority']and result['sourceIndexSha256']==SOURCE_SHA
    assert result['state']=='native-build-completed-runtime-pending'and result['evidenceComplete']is True
    assert result['rawChildExitCode']==result['launcherExitCode']==0 and result['lifecycleComplete']is True
    assert result['ownedGroupCleanup']['complete']is True and result['ownedGroupCleanup']['events']==result['ownedGroupCleanup']['errors']==[]
    assert result['allSourceStageOriginalAndCacheInputsPreserved']is True and len(result['cacheCopiesCompleted'])==4
    checked(result['engine']);checked(result['metadata']);checked(result['buildLog']);recheck(frame)
    print(json.dumps(dict(schemaVersion=1,state='COMBINED355_NORMAL_OFF_BUILD_RAW_ZERO_UNREVIEWED_V2',actualBuildResult=actual,externalParentTerminal=descriptor(OUT/'terminal.json'),sourceIndexSha256=SOURCE_SHA,independentBuildReviewRequired=True,engineExecuted=False,operationalAdmission=False)),flush=True)


def launcher(frame):
    for p in [WORK,FREEZE,OUT,BUILD_OUTPUT,OBSERVER]:absent(p)
    os.umask(0o077);OBSERVER.mkdir(mode=0o700)
    child,removed=clean_environment(dict(os.environ))
    argv=[frame['refs']['pythonExecutable']['path'],'-B','-I',str(OWN/'controller.py'),'parent',json.dumps(frame['configDescriptor'],separators=(',',':'))]
    write(OBSERVER/'preentry-environment.json',dict(schemaVersion=1,state='COMBINED355_RETRY_CLEAN_PREENTRY_OBSERVATION_V2',rootAuthority=frame['config']['rootAuthority'],controllerIndex=frame['ownIndex'],policy=ENV_POLICY,removedVariableNames=removed,environmentValuesRecorded=False,requiredEntriesAbsent=True,hostHomeValuesPreserved=True,argv=argv,nativeBuildStartedByThisRecord=False,engineOrGuestExecuted=False))
    recheck(frame);os.execve(argv[0],argv,child)


def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated==1
    assert len(sys.argv)==3 and sys.argv[1]in('launcher','parent','worker')
    frame=authorize(json.loads(sys.argv[2]))
    try:
        if sys.argv[1]=='launcher':launcher(frame)
        elif sys.argv[1]=='parent':parent(frame)
        else:worker(frame)
    finally:recheck(frame)


if __name__=='__main__':main()


