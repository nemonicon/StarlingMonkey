def typed_same(a,b):
    if type(a)is not type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys()and all(typed_same(a[k],b[k])for k in a)
    if isinstance(a,list):return len(a)==len(b)and all(typed_same(x,y)for x,y in zip(a,b))
    return a==b


def main():
    s=HERE.parent;root_row=row(s/'combined-native355-v1-build-root-results.json')
    need(root_row['sha256']=='282d46aee7bcee35cffe08126a91f96dd6e870da4da0b0a476fac1bfc06b03c6'and root_row['bytes']==19946,'Held exact Root failure observation')
    root=read(root_row);observer=Path('/private/tmp/starling-node-compat/combined-native355-v1-build-root-observer')
    need(Path(root_row['path']).read_bytes()==(observer/'root-observation.json').read_bytes(),'Entire external/retained Root report byte-equal');row(observer/'root-observation.json')
    need(root['state']=='ROOT_OBSERVED_COMBINED355_NATIVE_BUILD_RUSTUP_FAILURE_V1'and root['rootToolObservation']['sessionId']==64007 and root['rootToolObservation']['exitCode']==1,'Root-reported actual tool failure, not success')
    for d in descriptors(root):file(d)
    source_index=row(SOURCE/'index.json');need(source_index['sha256']==SOURCE_SHA,'Actual d646 controller Source')
    family(source_index);refs=read(row(SOURCE/'references.json'));inputs=read(row(SOURCE/'source-inputs.json'))
    need(len(inputs['files'])==len(inputs['modeRows'])==3403 and len(refs['families'])==8,'Complete finite controller protection closure')
    ledger={r['path']:r for r in inputs['files']};need(len(ledger)==3403,'Unique protected physical inputs')
    for d in inputs['files']:file(d)
    for m in inputs['modeRows']:
        file(m['file']);need(stat.S_IMODE(Path(m['file']['path']).lstat().st_mode)==m['mode'],'Every declared original input mode exact')
    for ix in refs['families']:family(ix)
    cfg=read(root['rootConfig']);authority=read(root['rootAuthority']);peer=proof(root['controllerSourceReview']);invocation=read(root['invocation']);preentry=read(root['preentryEnvironment'])
    need(root['controllerIndex']==source_index==authority['controllerIndex']==cfg['controllerIndex']and root['sourceIndex']==refs['integrationIndex']==authority['sourceIndex']==cfg['sourceIndex'],'Actual Source/integration/config roles')
    need(peer['schemaVersion']==1 and peer['state']=='INDEPENDENT_COMBINED355_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1'and peer['sourceOnly']is peer['sourceReviewPassed']is True and peer['controllerSourceIndexSha256']==SOURCE_SHA,'Actual conditional Source peer17aa')
    policy=peer['requiredRootEnvironmentPolicy']
    need(typed_same(policy,authority['rootEnvironmentPolicy'])and typed_same(policy,preentry['policy'])and typed_same(policy,invocation['rootEnvironmentPolicy']),'Conditional peer clean-entry requirement actually bound')
    need(authority['rootLauncherEntry']==root['rootLauncherEntry']==preentry['rootLauncherEntry']and root['rootLauncherEntry']['sha256']=='dfbc3a7442c2eb4608977b4e1ff4457347bd1416afa6079a81c755625567252b','Actual clean-entry launcher Source')
    need(preentry['state']=='ROOT_COMBINED355_CLEAN_PREENTRY_OBSERVATION_V1'and preentry['removedVariableNames']==[]and preentry['requiredEntriesAbsent']is preentry['hostHomeValuesPreserved']is True and preentry['environmentValuesRecorded']is False,'Actual preentry: entries absent, no values dumped, home values preserved')
    need(preentry['rootAuthority']==root['rootAuthority']and preentry['controllerSourceReview']==root['controllerSourceReview'],'Whole preentry proof/Root binding')
    need(authority['buildAllowed']is True and authority['privateRustupAndCargoHomesRequired']is True and authority['dependencyNetworkWithinBuildAllowed']is True,'Exact new native-build bootstrap scope')
    for key in ['stageAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','componentAllowed','guestAllowed','keyOperationsAllowed','gcAllowed','gcReconfigureAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:
        need(authority[key]is False,'No other Root authority '+key)
    checkpoint('Held Root282d/controllerd646/integration08bf/conditional17aa/launcherdfbc; all3403 hashes/modes/eight fixed families and clean preentry policy verified')

    stage=read(refs['stageResult']);copy_plan=read(refs['stageCopyPlan'])['files'];configured=Path(authority['configuredSourceRoot'])
    need(stage['copies']==stage['copiesCompleted']==copy_plan and len(copy_plan)==1613,'Actual complete stage1613 context retained')
    target_ids=set();original_ids=set()
    for m in copy_plan:
        original=dict(path=m['original'],sha256=m['sha256'],bytes=m['bytes']);target=dict(original,path=str(configured/m['path']))
        file(original);file(target);a,b=ident(Path(original['path'])),ident(Path(target['path']))
        need(a[5]==b[5]==m['sourceMode']and b[6]==1 and a[:2]!=b[:2],'Current original/stage Source bytes/modes/distinct inode')
        need(b[:2]not in target_ids,'All stage targets independent');target_ids.add(b[:2]);original_ids.add(a[:2])
    need(not(target_ids&original_ids)and(configured/'.git/HEAD').read_text()=='54b3329b3ce818fd1f244e871e9c259b63667cda\n','Stage Source and originals disjoint; original detached baseline preserved')
    need(not(configured/'.git/objects/info/alternates').exists(),'No alternate Git object store in configured Source')
    for host in refs['hostTools']:
        file(host['executable']);need(str(Path(host['selectedAlias']).resolve())==host['executable']['path'],'Exact selected original host-tool alias')
    checkpoint('All1613 staged/original files and Source modes/inodes, detached baseline, no alternates, exact finite host-tool aliases preserved; no Git invoked')

    actual=read(root['actualBuildResult']);launch=read(row(Path(root['actualBuildResult']['path']).parent/'launch.json'));work=Path(authority['workRoot']);out=Path(root['actualBuildResult']['path']).parent;external=Path(authority['externalOutputRoot'])
    need(actual['state']=='native-build-failed-or-incomplete'and actual['evidenceComplete']is False and actual['rawChildExitCode']==actual['status']==actual['launcherExitCode']==1,'Failure frame remains literal failed/raw1/evidenceCompletefalse')
    need(actual['lifecycleComplete']is actual['childStarted']is actual['temporarySigtermHandlerRestored']is actual['allSourceStageOriginalAndCacheInputsPreserved']is True,'Lifecycle and final finite protection complete')
    need(actual['stoppedForDiskSpace']is False and actual['stopReason']is None and actual['sigtermReceived']==0 and actual['launcherErrors']==[],'Not a disk stop/termination/launcher error')
    need(actual['ownedGroupCleanup']==dict(pgid=84463,complete=True,events=[],errors=[],rawChildExitCode=1),'Actual inner Bash group cleanup natural/raw1')
    need(actual['command']==[refs['bash']['path'],str(configured/'tests/node-compat/build-engine.sh')]and actual['explicitEnvironment']==refs['buildEnvironment']==authority['buildEnvironment'],'Exact captured outer recipe command and explicit environment')
    for key in ['RUSTUP_HOME','CARGO_HOME']:need(actual['explicitEnvironment'][key]==str(work/('rustup-home'if key=='RUSTUP_HOME'else'cargo-home')),'Private Rust homes '+key)
    need(actual['explicitEnvironment']['RUSTUP_TOOLCHAIN']=='1.88.0'and actual['parallelBuilds']==1,'Pinned1.88 and one-job build request')
    need(launch['state']=='COMBINED355_NORMAL_OFF_NATIVE_BUILD_STARTED'and launch['cacheCopiesCompleted']==[]and launch['rawChildExitCode']is None,'Durable pre-copy pre-command launch retained')
    for key in ['sourceIndexSha256','controllerIndex','rootAuthority','command','explicitEnvironment','configuredSourceRoot','workRoot','freezeRoot']:
        need(typed_same(launch[key],actual[key]),'Same before/after actual launch role '+key)
    cache=read(refs['cachePlan']);need(len(cache['copies'])==len(actual['cacheCopiesCompleted'])==4,'Exactly four bounded immutable cache seeds')
    for i,(m,observed)in enumerate(zip(cache['copies'],actual['cacheCopiesCompleted']),1):
        file(m['source']);file(observed['target']);need(observed['source']==m['source']and observed['target']['path']==str(work/m['target'])and observed['sourceMode']==m['sourceMode']and observed['outputMode']==m['outputMode'],'Actual cache plan tuple '+str(i))
        a,b=ident(Path(m['source']['path'])),ident(Path(observed['target']['path']));need(a[:2]!=b[:2]and b[6]==1 and a[5]==m['sourceMode']and b[5]==m['outputMode'],'Cache modes/nlink/independent inode')
        need(m['source']['sha256']==observed['target']['sha256']and m['source']['bytes']==observed['target']['bytes'],'Cache original/output whole bytes equal')
        need(read(row(out/('cache-copy-'+str(i)+'.json')))==observed,'Per-copy durable raw descriptor')
    samples=actual['diskFreeSamplesDuringBuildCommand'];need(len(samples)==34 and all(type(x['freeBytes'])is int and x['freeBytes']>=838860800 for x in samples),'Complete34 periodic disk samples above stop floor')
    need(all(a['monotonicSeconds']<b['monotonicSeconds']for a,b in zip(samples,samples[1:]))and min(x['freeBytes']for x in samples)==root['minimumObservedBuildFreeBytes'],'Disk sample ordering/exact retained minimum')
    for key in ['freeBytesBefore','freeBytesBeforeCacheCopies','freeBytesAfterCacheCopies']:need(actual[key]>=2147483648,'2GiB boundary guard '+key)
    need(actual['externalParentDeadlineSeconds']==7200 and actual['requiredStartFreeBytes']==2147483648 and actual['stopBelowFreeBytes']==838860800,'Requested owned/disk bounds exact')
    checkpoint('Whole failed/lifecycle-complete frame; pre-command launch;four cache copies/equal original hashes/distinct inodes/modes;34 disk samples and boundary guards')

    terminal=read(root['externalParentTerminal']);started=read(row(external/'started.json'))
    need(terminal['rawExitCode']==1 and terminal['pid']==84433 and terminal['authority']==root['rootAuthority'],'Owned worker84433 raw1 exact Root')
    need(terminal['parentOwnedGroupGone']is terminal['allObservedOwnedGroupsGone']is True and terminal['timeout']is terminal['forcedCleanup']is False,'External failed worker exited/cleaned without timeout')
    for key in ['interruptedSignals','remainingObservedPids','signals','errors']:need(terminal[key]==[],'No actual lifecycle '+key)
    need({g['pgid']for g in terminal['finalGroups']}=={84433,84463}and all(g['alive']is False for g in terminal['finalGroups']),'Both observed owned groups gone')
    processes=terminal['observedProcesses'];need(len(processes)==12,'Complete twelve observed processes')
    events=[]
    for p in sorted(external.glob('owned-*.json')):events.append(read(row(p)))
    need([x['sequence']for x in events]==list(range(12))and[x['process']for x in events]==processes,'All durable ownership records exactly match terminal')
    need(any(x['pid']==84536 and x['command']=='rustup'for x in processes),'Actual rustup process observed')
    rustcs=[x for x in processes if x['command'].endswith('/toolchains/1.88.0-aarch64-apple-darwin/bin/rustc')]
    need(len(rustcs)==1 and rustcs[0]['pid']==84788 and rustcs[0]['ppid']==84536,'Private rustc process observed; do not claim no compiler executable ran')
    cfg_json=json.dumps(root['rootConfig'],separators=(',',':'))
    need(started['argv']==[refs['pythonExecutable']['path'],'-B','-I',str(SOURCE/'controller.py'),'worker',cfg_json]and started['timeoutSeconds']==7200 and started['authority']==root['rootAuthority'],'Durable whole worker argv/deadline/Root')
    raw=Path(terminal['stdout']['path']).read_bytes();file(terminal['stdout']);file(terminal['stderr']);lines=raw.decode('utf-8','strict').splitlines()
    need(len(lines)==1 and typed_same(json.loads(lines[0]),dict(output=str(out),result=actual)),'Whole worker stdout contains complete unshortened failure frame')
    need('assert result[\'launcherExitCode\']==0'in Path(terminal['stderr']['path']).read_text(),'Owned worker refusal follows durable failure publication')
    root_stdout=Path(root['rootStdout']['path']).read_text().splitlines();need(len(root_stdout)==1 and json.loads(root_stdout[0])==dict(pid=84433,timeoutSeconds=7200),'Root whole stdout has only owned launch; no success envelope')
    need("value['rawExitCode']==0"in Path(root['rootStderr']['path']).read_text(),'Root parent refuses actual nonzero worker instead of accepting partial result')
    checkpoint('Full raw result envelope and strict worker/parent refusals; twelve ownership records/two groups gone; Rustup and private rustc observed with no signal/timeout')

    log=Path(root['buildLog']['path']).read_bytes();need(root['buildLog']==actual['buildLog']and hashlib.sha256(log).hexdigest()=='5a9607ffded3063cc8c79fa6537e6d6c0f08f53df0772dcbcf7c50d4ed335b06'and len(log)==789,'Complete build log exact789B')
    text=log.decode('utf-8','strict');need('1.88.0-aarch64-apple-darwin installed - rustc 1.88.0'in text and "error: rustup is not installed at '"+str(work/'cargo-home')+"'"in text,'Exact installed-toolchain then private manager/bootstrap refusal')
    recipe=Path(refs['recipe']['path']).read_text();need(recipe==Path(configured/'tests/node-compat/build-engine.sh').read_text()and 'set -euo pipefail'in recipe,'Exact configured recipe/error propagation')
    install='rustup toolchain install 1.88.0 --profile minimal';target='rustup target add --toolchain 1.88.0 wasm32-wasip1'
    need(recipe.index(install)<recipe.index(target)<recipe.index('cmake -S'),'Pinned install then target then later CMake Source order')
    need(recipe.splitlines()[263]==install and recipe.splitlines()[264]==target,'Exact Source command line264/265; not a separately captured Rustup argv trace')
    private=read(root['privateBootstrapState']);settings=Path(private['rustupSettings']['path']).read_bytes();file(private['rustupSettings'])
    need(private['cargoHome']==str(work/'cargo-home')and private['cargoHomeBinExists']is False and tree(work/'cargo-home')==[],'Private Cargo home actually empty; no manager/proxies there')
    need(private['privateToolchains']==['1.88.0-aarch64-apple-darwin']and settings==b'version = "12"\ndefault_toolchain = "1.88.0-aarch64-apple-darwin"\n\n[overrides]\n','Actual private toolchain/settings unchanged; auto_self_update not configured')
    components=work/'rustup-home/toolchains/1.88.0-aarch64-apple-darwin/lib/rustlib/components';file(row(components));need(components.read_text().splitlines()==['cargo-aarch64-apple-darwin','rust-std-aarch64-apple-darwin','rustc-aarch64-apple-darwin'],'Three private host components installed; wasm target absent')
    rustup=next(x['executable']for x in refs['hostTools']if x['name']=='rustup');manager=Path(rustup['path']).read_bytes();need(rustup['sha256']=='63752a1919a3a4793173ec70f8f212621a7ce38ba6a246095984482f4de20f9f'and b'rustup/1.29.3 (curl)'in manager and b'Current crate version: 1.29.3'in manager,'Pinned manager/compiled version literals, no version CLI invoked')
    work_names=tree(work);need(len(work_names)==755,'Full finite failed work-tree snapshot')
    for n in work_names:file(row(work/n))
    need(not any(p.name.startswith('engine-')for p in work.iterdir())and list((work/'artifacts').iterdir())==[],'No CMake engine builddir or native artifact files')
    need(not(work/'artifacts'/refs['artifactBasename']).exists()and not Path(str(work/'artifacts'/refs['artifactBasename'])+'.build.json').exists()and not Path(authority['freezeRoot']).exists(),'No engine/sidecar/freeze artifact exists')
    checkpoint('Exact789B log/private empty Cargo home/1.88 host toolchain/settings;755-file failed work snapshot; no CMake engine dir/engine/sidecar/freeze')

    launcher=Path(root['rootLauncherEntry']['path']).read_text();controller=Path(authority['controllerEntry']['path']).read_text()
    for p in [Path(root['rootLauncherEntry']['path']),Path(authority['controllerEntry']['path']),Path(refs['lifecycleEntry']['path'])]:ast.parse(p.read_bytes())
    need('child = {k: v for k, v in parent.items() if k not in removed}'in launcher and "for k in POLICY['preserveExactNames']"in launcher and 'child.get(k) == parent.get(k)'in launcher,'Source-coupled clean env copy/home-value preservation')
    need(launcher.index("write(OBSERVER / 'preentry-environment.json'")<launcher.index('os.execve(argv[0], argv, child)'),'Actual preentry fsynced before genuine controller replacement')
    need("env['RUSTUP_HOME']==str(WORK/'rustup-home')and env['CARGO_HOME']==str(WORK/'cargo-home')"in controller,'Actual private-home build environment, no host home rebind')
    need("if result.get('rawChildExitCode')==0:"in controller and controller.index("if result.get('rawChildExitCode')==0:")<controller.index("model=load_actual(refs['metadataModel']"),'Metadata classifier only after raw0; failure never reaches native admission')
    copies=[]
    for pair in root['retainedEvidenceCopies']:
        a,b=pair['original'],pair['retained'];file(a);file(b);need(a['sha256']==b['sha256']and a['bytes']==b['bytes']and ident(Path(a['path']))[:2]!=ident(Path(b['path']))[:2],'Complete retained failure copy')
        copies.append(pair)
    need(len(copies)==27,'All27 raw-evidence copies')
    retained=s/'combined-native355-v1-build-root-evidence';need(len(tree(retained))==28,'Twenty-seven raw copies plus retained settings file')
    extra=[n for n in tree(retained)if str(retained/n)not in{p['retained']['path']for p in copies}];need(len(extra)==1,'Exactly one extra settings DATA copy')
    extra_row=row(retained/extra[0]);need(extra_row['sha256']==private['rustupSettings']['sha256']and extra_row['bytes']==78,'Whole retained private settings copy')
    for key in ['failedOutputsRetained','compilerBuildDirectoryAbsent','engineArtifactAbsent','metadataSidecarAbsent','lifecycleComplete','ownedCleanupComplete','allObservedOwnedGroupsGone','allSourceStageOriginalAndCacheInputsPreserved']:need(root[key]is True,'Actual Root scope '+key)
    for key in ['repeatOrResumeGranted','engineOrGuestExecuted','operationalAdmission','runtimeAcceptanceClaim','stoppedForDiskSpace']:need(root[key]is False,'Failure grants no action '+key)
    checkpoint('Environment/home claims qualified as Source+preentry evidence, not full-home attestation; conditional metadata branch not entered;27 raw copies plus settings exact')

    for path,(_,i)in seen.items():need(ident(Path(path))==i,'Final observed identity stable')
    for ix in [source_index,root['controllerSourceReview']['index']]+refs['families']:
        v=json.loads(Path(ix['path']).read_bytes());need(tree(Path(ix['path']).parent)==sorted(['index.json']+[m['path']for m in v['files']]),'Final fixed-family membership')
    need(tree(work)==work_names,'Final preserved failed private work membership')
    observed=sorted((x[0]for x in seen.values()),key=lambda d:d['path'])
    evidence=dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_BOOTSTRAP_FAILURE_DATA_AUDIT_PASSED_V1',checks=check_count,observedFiles=len(observed),observedLogicalBytes=sum(d['bytes']for d in observed),observedDescriptorVectorSha256=hashlib.sha256(json.dumps(observed,sort_keys=True,separators=(',',':')).encode()).hexdigest(),rootObservation=root_row,actualBuildResult=root['actualBuildResult'],preentryEnvironment=root['preentryEnvironment'],rootAuthority=root['rootAuthority'],rootConfig=root['rootConfig'],rootLauncherEntry=root['rootLauncherEntry'],controllerIndex=source_index,integrationIndex=refs['integrationIndex'],controllerSourceReview=root['controllerSourceReview'],actualStageReview=refs['actualStageReview'],externalParentTerminal=root['externalParentTerminal'],buildLog=root['buildLog'],privateBootstrapState=root['privateBootstrapState'],rustupManager=rustup,rustupSettings=private['rustupSettings'],declaredInputLedger=row(SOURCE/'source-inputs.json'),retainedCopies=copies,
        coverage=dict(controllerProtectedFiles=3403,protectedModes=3403,fixedContextFamilies=8,stageCopiesRechecked=1613,cacheCopies=4,observedProcesses=12,observedOwnedGroups=2,periodicDiskSamples=34,rawEvidenceCopies=27,retainedSettingsCopies=1,failedWorkFiles=755,privateHostToolchains=1,privateHostComponents=3,engineArtifacts=0,metadataSidecars=0),
        failingOuterRecipeCommand=actual['command'],sourceInferredRustupCommand=['rustup','toolchain','install','1.88.0','--profile','minimal'],rustupSubcommandArgvSeparatelyCaptured=False,
        diagnosis='Log/private state and exact1.29.3 primary Source support post-install self-update NotSelfInstalled at private CARGO_HOME; inner argv is Source/control-flow inference, not an argv trace.',
        rustupCompiledVersionLiterals='1.29.3',privateRustcProcessObserved=True,privateRustcPurposeSourceInferred='version display after installation, not guest compilation',
        homeEnvironmentPreservationSourceCoupled=True,entireHomeFilesystemAttested=False,oldFailureRootsPreserved=True,reviewerReadHashDataOnly=True,readerOwnerHelperRustupCliDependencyNetworkInstallBuildEngineOrGuestActions=False,checkedSections=checks,nativeBuildSucceeded=False,engineOrGuestExecuted=False,operationalAdmission=False)
    with(HERE/'input-hashes.json').open('x')as f:json.dump(dict(schemaVersion=1,files=observed,observedDataOnly=True),f,indent=2);f.write('\n')
    wr=[]
    for n in work_names:
        d=seen[str(work/n)][0];wr.append(dict(d,path=n,mode=stat.S_IMODE((work/n).lstat().st_mode)))
    with(HERE/'failed-work-inventory.json').open('x')as f:json.dump(dict(schemaVersion=1,root=str(work),files=wr,observedFailureDataOnly=True,compilerToolchainAdoptionGranted=False),f,indent=2);f.write('\n')
    with(HERE/'audit-results.json').open('x')as f:json.dump(evidence,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(passed=True,checks=check_count,observedFiles=len(observed),observedLogicalBytes=evidence['observedLogicalBytes'],nativeBuildSucceeded=False,reviewerActions=0)))


if __name__=='__main__':main()
