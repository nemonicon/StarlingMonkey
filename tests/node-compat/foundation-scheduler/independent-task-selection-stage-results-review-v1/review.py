"""Independent finite retained DATA review; never import or invoke owner code/Git."""
from pathlib import Path
import hashlib,json,os,stat

REPO=Path('/Users/dan/dev/StarlingMonkey')
S=REPO/'tests/node-compat/foundation-scheduler'
OWN=Path(__file__).resolve().parent
SOURCE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source')
WORK=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-build')
FREEZE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze')
INTEGRATION=S/'task-selection-integration-candidate-v1'
CONTROLLER=S/'task-selection-stage-controller-candidate-v1'
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'
SOURCE_SHA='88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1'
CONTROLLER_SHA='959b3e73111f9f2286d026efc70ef671b2f037321ae159e1cb10f281ab3bfb46'
ROOT_SHA='9c7403b04a78bbbe8a0d2f6f621edcd538c72638c6d9940bdd3c5060866ab949'
observed={}
checks=0


def require(condition,reason='DATA check'):
    global checks
    checks+=1
    assert condition,reason


def canonical(path):
    path=str(path)
    return Path('/private'+path)if path.startswith('/tmp/')else Path(path)


def record(path,sha=None,size=None):
    p=canonical(path);require(p.is_absolute()and '..'not in p.parts,str(p))
    for q in(p,*p.parents):require(not q.is_symlink(),str(q))
    before=p.stat();require(stat.S_ISREG(before.st_mode),str(p));h=hashlib.sha256()
    with p.open('rb')as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    after=p.stat();require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),str(p))
    d=dict(path=str(p),sha256=h.hexdigest(),bytes=after.st_size)
    if sha is not None:require(d['sha256']==sha,str(p))
    if size is not None:require(d['bytes']==size,str(p))
    if str(p)in observed:require(observed[str(p)]==d,str(p))
    observed[str(p)]=d;return d


def verify(row):
    require(set(row)=={'path','sha256','bytes'})
    record(row['path'],row['sha256'],row['bytes']);return canonical(row['path'])


def load(path):record(path);return json.loads(Path(path).read_bytes())
def read(row):return json.loads(verify(row).read_bytes())
def descriptor(path):return record(path)


def family(index):
    v=read(index);base=Path(index['path']).parent;names=set();rows=[index]
    require(v['schemaVersion']==1)
    for entry in v['files']:
        n=entry['path'];require(n and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/'))and n not in names)
        names.add(n);row=dict(path=str(base/n),sha256=entry['sha256'],bytes=entry['bytes']);verify(row);rows.append(row)
    actual=set()
    for path in base.rglob('*'):
        require(not path.is_symlink(),str(path))
        if path.is_file():actual.add(str(path.relative_to(base)))
    require(actual==names|{'index.json'},str(base));return rows


def proof(pair,state,field,sha):
    rows=family(pair['index']);require(pair['result']in rows)
    value=read(pair['result']);require(value['state']==state and value[field]==sha)
    require(value['schemaVersion']==1 and value['sourceOnly']is True and value['sourceReviewPassed']is True and value['ownerActionsInvoked']is False)
    return value


def inventory(path):
    names=[]
    for p in path.rglob('*'):
        require(not p.is_symlink(),str(p))
        if p.is_file():names.append(str(p.relative_to(path)))
    return sorted(names)


def monitor_data(directory,root_authority,config,entry,timeout,pid,expected_names):
    require(set(inventory(directory))==set(expected_names),str(directory)+' inventory')
    files=[descriptor(directory/name)for name in sorted(expected_names)]
    started=load(directory/'started.json');terminal=load(directory/'terminal.json')
    require(started['schemaVersion']==terminal['schemaVersion']==1)
    require(started['pid']==terminal['pid']==pid and started['authority']==terminal['authority']==root_authority)
    argv=started['argv'];require(len(argv)==5 and argv[1:3]==['-B','-I']and argv[3]==entry['path'])
    require(json.loads(argv[4])==config and argv[4]==json.dumps(config,separators=(',',':')))
    require(started['timeoutSeconds']==timeout)
    require(terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone']is True and terminal['allObservedOwnedGroupsGone']is True)
    require(terminal['timeout']is False and terminal['forcedCleanup']is False)
    for key in['signals','errors','interruptedSignals','remainingObservedPids']:require(terminal[key]==[])
    for key in['stdout','stderr']:
        verify(terminal[key]);require(terminal[key]['path']==str(directory/(key+'.log')))
    owned=[load(directory/name)for name in sorted(expected_names)if name.startswith('owned-')]
    require([r['sequence']for r in owned]==list(range(len(owned))))
    require([r['process']for r in owned]==terminal['observedProcesses'])
    require(all(type(r['observationMonotonicSeconds'])in(int,float)and r['observationMonotonicSeconds']>=0 for r in owned))
    require([r['observationMonotonicSeconds']for r in owned]==sorted(r['observationMonotonicSeconds']for r in owned))
    processes=terminal['observedProcesses'];require(len({r['pid']for r in processes})==len(processes))
    require(processes[0]['pid']==processes[0]['pgid']==pid)
    known={pid}
    for process in processes[1:]:
        require(process['ppid']in known,repr(process));known.add(process['pid'])
    require({r['pgid']for r in processes}=={r['pgid']for r in terminal['finalGroups']})
    for group in terminal['finalGroups']:require(group['alive']is False and group['signalAllowed']is False)
    return terminal,files


def main():
    require(not(OWN/'index.json').exists(),'never alter an existing seal')
    root_row=descriptor(S/'task-selection-stage-v1-root-results.json');require(root_row['sha256']==ROOT_SHA and root_row['bytes']==2845)
    report=read(root_row);require(report['state']=='ROOT_OBSERVED_TASK_SELECTION342_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1')
    require(report['sourceIndex']['sha256']==SOURCE_SHA and report['controllerSourceIndex']['sha256']==CONTROLLER_SHA)
    source_rows=family(report['sourceIndex']);family(report['controllerSourceIndex'])
    refs=load(CONTROLLER/'references.json');authority=read(report['rootAuthority']);config=read(report['config'])
    require(authority['state']=='ROOT_REVIEWED_SCHEDULER_RESOURCE_TASK_SELECTION342_SOURCE_STAGE_V1'and authority['stageAllowed']is True)
    require(config==dict(schemaVersion=1,controllerIndex=report['controllerSourceIndex'],sourceIndex=report['sourceIndex'],rootAuthority=report['rootAuthority']))
    require(authority['sourceIndexSha256']==SOURCE_SHA and authority['controllerIndex']==report['controllerSourceIndex'])
    require(authority['controllerSourceReview']==report['controllerSourceReview'])
    require(authority['sourceIndependentReview']==refs['integrationReview']and authority['controllerSourceReview']['index']['sha256']=='8c288dc166aced0a44b27255dec298faa8bedef0efe640ab8ae2dda897ea20dc')
    proof(authority['sourceIndependentReview'],'INDEPENDENT_SCHEDULER_TASK_SELECTION_INTEGRATION_SOURCE_REVIEW_PASSED_V1','sourceIndexSha256',SOURCE_SHA)
    controller_peer=proof(authority['controllerSourceReview'],'INDEPENDENT_TASK_SELECTION_STAGE_CONTROLLER_SOURCE_REVIEW_PASSED_V1','controllerSourceIndexSha256',CONTROLLER_SHA)
    require(controller_peer['integrationSourceIndexSha256']==SOURCE_SHA and controller_peer['hostActionsInvoked']is False and controller_peer['stageActionsInvoked']is False)
    require(authority['rootCaller']==descriptor(S/'task-selection-stage-v1-root-controller.py'))
    require(authority['controllerEntry']==descriptor(CONTROLLER/'controller.py')and authority['stageEntry']==descriptor(INTEGRATION/'stage.py'))
    require(authority['monitorIndex']==refs['monitorIndex']and authority['monitorEntry']==refs['monitorEntry'])
    family(refs['monitorIndex']);verify(refs['monitorEntry'])
    require(authority['sourceRoot']==str(SOURCE)and authority['workRoot']==str(WORK)and authority['freezeRoot']==str(FREEZE)and authority['baseline']==BASE)
    require(authority['nativeSourceFiles']==342 and authority['nativeReplacements']==3 and authority['expectedCopies']==566)
    for key in['buildAllowed','freezeAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','gcAllowed','runtimeAcceptanceClaim','sourcePromotionAllowed','operationalAdmission','metadataProjectionAllowed','timingAllowed']:require(authority[key]is False)
    for key in['actualStage','actualStageReview','actualBuild','actualFreeze','actualNativeReview','actualComponentReview']:require(authority[key]is None)
    require(all(value is None for value in authority['nativePins'].values()))
    baseline=load(INTEGRATION/'baseline-pins.json')
    for index in baseline['families'].values():family(index)
    for key in['parentPolicy','parentHelper','parentRecipe','resourceMetadata','resourceFreezeReceipt']:verify(baseline[key])
    require(refs['resourceFreezeReceipt']==baseline['resourceFreezeReceipt']and authority['resourceFreezeReceipt']==refs['resourceFreezeReceipt'])
    family(refs['resourceArtifactReview']['index']);artifact=read(refs['resourceArtifactReview']['result'])
    require(artifact['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_NORMAL_OFF_FROZEN_ARTIFACT_REVIEW_PASSED_V1'and artifact['verifiedPassed']is True and artifact['nativeSourceFiles']==342)
    require(authority['resourceArtifactReview']==refs['resourceArtifactReview'])
    preparation=load(INTEGRATION/'input-freeze.json');require(len(preparation['files'])==540)
    for r in preparation['files']:verify(r)
    # Independently reconstruct exact finite targets; no owner merge function.
    plan=load(INTEGRATION/'stage-inputs.json');targets={}
    for item in plan['files']:
        name=item['target'];require(name not in targets and not name.startswith('/')and all(p not in('','.','..')for p in name.split('/')))
        verify(item['original']);targets[name]=item['original']
    require(len(targets)==533)
    for r in source_rows:targets[str(INTEGRATION.relative_to(REPO))+'/'+str(Path(r['path']).relative_to(INTEGRATION))]=r
    require(len(targets)==566)
    require(len(plan['nativeAfterimageReplacements'])==3)
    for change in plan['nativeAfterimageReplacements']:
        r=descriptor(INTEGRATION/'native'/change['path']);require(r['sha256']==change['afterSha256']and r['bytes']==change['bytes']);targets[change['path']]=r
    targets['tests/node-compat/build-engine.sh']=descriptor(INTEGRATION/'proposed/tests/node-compat/build-engine.sh')
    require(len(targets)==566 and plan['sourceRoot']==str(SOURCE)and plan['workRoot']==str(WORK)and plan['freezeRoot']==str(FREEZE))
    journal=read(report['actualJournal']);require(journal['state']=='RESOURCE_TASK_SELECTION342_SOURCE_STAGED_UNREVIEWED_V1')
    require(journal['sourceIndex']==report['sourceIndex']and journal['rootAuthority']==report['rootAuthority']and journal['baseline']==BASE)
    require(journal['destination']==str(SOURCE)and journal['workRoot']==str(WORK)and journal['freezeRoot']==str(FREEZE))
    require(journal['nativeFiles']==342 and journal['nativeReplacements']==3 and journal['buildOrGuestInvoked']is False)
    require(journal['copies']==[dict(path=str(SOURCE/name),original=r)for name,r in sorted(targets.items())])
    observation=read(report['stageObservation'])
    expected_observations=[];copy_inventory=[]
    for name,r in sorted(targets.items()):
        original=verify(r);target=SOURCE/name;record(target,r['sha256'],r['bytes']);a=original.stat();b=target.stat()
        mode=stat.S_IMODE(a.st_mode);require(mode==stat.S_IMODE(b.st_mode),str(target))
        require((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),str(target))
        expected_observations.append(dict(path=str(target),expected=r,status='match',bytes=b.st_size,mode=mode,sha256=r['sha256'],distinctInode=True,expectedMode=mode))
        copy_inventory.append(dict(target=descriptor(target),original=r,mode=mode,originalInode=a.st_ino,targetInode=b.st_ino,originalDevice=a.st_dev,targetDevice=b.st_dev))
    require(observation==dict(schemaVersion=1,state='TASK_SELECTION342_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1',sourceIndex=report['sourceIndex'],rootAuthority=report['rootAuthority'],partialObservationOnly=True,stageSuccessful=True,buildExecuted=False,engineExecuted=False,operationalAdmission=False,actualJournal=report['actualJournal'],targetObservations=expected_observations,finalProtectionRecheckPassed=True))
    # The complete actual342 native manifest, with exactly339 old resource hashes.
    policy=load(INTEGRATION/'policy.json');parent_policy=read(baseline['parentPolicy'])
    before={r['path']:r['sha256']for r in parent_policy['expectedNativeSourceManifest']};after={r['path']:r['sha256']for r in policy['expectedNativeSourceManifest']}
    require(len(before)==len(after)==342 and before.keys()==after.keys())
    require(sum(before[n]==after[n]for n in before)==339)
    require(sorted(n for n in before if before[n]!=after[n])==sorted(r['path']for r in plan['nativeAfterimageReplacements']))
    for name,sha in after.items():record(SOURCE/name,sha)
    require(after['builtins/web/timers.cpp']=='0024d009d11aab0705789f5d72fd8ec87deec9c44bdd8b913d970257aaadc9e4')
    require(policy['taskSelectionSourcePolicy']['requiresFullNativeRebuild']is True and policy['taskSelectionSourcePolicy']['compatibleWithParentEngineAbi']is False)
    # Prior original/configured/frozen artifacts remain fixed. Modes are qualified.
    receipt=read(refs['resourceFreezeReceipt']);require(receipt['nativeInputsVerified']==342 and len(receipt['copies'])==666)
    frozen_root=Path(refs['resourceFreezeReceipt']['path']).parent;frozen_names=set();original_count=0
    old_modes=[]
    for r in receipt['copies']:
        frozen={k:r[k]for k in['path','sha256','bytes']};p=verify(frozen);require(stat.S_IMODE(p.stat().st_mode)==0o600)
        frozen_names.add(str(p.relative_to(frozen_root)))
        if r['original']is not None:
            o=verify(r['original']);original_count+=1
            old_modes.append(dict(path=str(o),currentMode=stat.S_IMODE(o.stat().st_mode),fixedHistoricalModeClaimed=False))
    require(original_count==663 and set(inventory(frozen_root))==frozen_names|{'normal-off-freeze-receipt.json'})
    old_stage=read(refs['resourceStage']);require(len(old_stage['copies'])==501)
    for r in old_stage['copies']:
        original=verify(r['original']);copy=verify(dict(r['original'],path=r['path']))
        old_modes.extend([dict(path=str(p),currentMode=stat.S_IMODE(p.stat().st_mode),fixedHistoricalModeClaimed=False)for p in(original,copy)])
    # Complete retained raw process evidence; no live query or signal.
    outer_dir=Path(report['outerTerminal']['path']).parent;inner_dir=Path(authority['externalOutputRoot'])
    outer_names=['started.json','stdout.log','stderr.log','terminal.json']+['owned-'+str(i).zfill(4)+'.json'for i in range(29)]
    inner_names=['started.json','stdout.log','stderr.log','terminal.json','stage-observation.json']+['owned-'+str(i).zfill(4)+'.json'for i in range(6)]
    outer,outer_files=monitor_data(outer_dir,report['rootAuthority'],report['config'],authority['controllerEntry'],900,95581,outer_names)
    inner,inner_files=monitor_data(inner_dir,report['rootAuthority'],report['config'],authority['stageEntry'],600,95641,inner_names)
    require(report['outerTerminal']==descriptor(outer_dir/'terminal.json'))
    require(report['stageObservation']==descriptor(inner_dir/'stage-observation.json'))
    require(outer['stderr']['bytes']==0 and inner['stderr']['bytes']==210)
    require((inner_dir/'stderr.log').read_text()=="Cloning into '"+str(SOURCE)+"'...\nHEAD is now at 54b3329 fix: Replace malformed UTF-8 and strip BOM in Response and Request `text()` and `json()` (#348)\n")
    outer_records=[json.loads(line)for line in(outer_dir/'stdout.log').read_text().splitlines()]
    inner_records=[json.loads(line)for line in(inner_dir/'stdout.log').read_text().splitlines()]
    require(outer_records==[dict(pid=95641,timeoutSeconds=600),dict(state=observation['state'],stageSuccessful=True,observation=report['stageObservation']['path'],independentResultReviewRequired=True)])
    require(inner_records==[journal])
    require(report['rawControllerExitCode']==0 and report['allObservedOwnedGroupsGone']is True and report['copies']==566)
    require(report['operationalElapsedSeconds']==outer['operationalElapsedSeconds'])
    for k in['buildExecuted','engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim']:require(report[k]is False)
    # Detached Git storage/provenance checked as files only, never running Git.
    git=SOURCE/'.git';require(git.is_dir()and not git.is_symlink())
    head=descriptor(git/'HEAD');require((git/'HEAD').read_text()==BASE+'\n')
    require(not(git/'objects/info/alternates').exists()and not(git/'commondir').exists()and not(git/'gitdir').exists())
    config_text=(git/'config').read_text();record(git/'config');require(str(REPO)in config_text and 'worktree'not in config_text and 'alternates'not in config_text)
    source_objects={}
    for p in(REPO/'.git/objects').rglob('*'):
        if p.is_file():source_objects[(p.stat().st_dev,p.stat().st_ino)]=str(p)
    object_inventory=[]
    for p in sorted((git/'objects').rglob('*')):
        require(not p.is_symlink())
        if p.is_file():
            a=p.stat();require((a.st_dev,a.st_ino)not in source_objects and a.st_nlink==1,str(p))
            object_inventory.append(dict(path=str(p),bytes=a.st_size,device=a.st_dev,inode=a.st_ino,nlink=a.st_nlink))
    require(object_inventory,'clone has independent object files')
    require(SOURCE!=REPO and not SOURCE.is_relative_to(REPO)and not REPO.is_relative_to(SOURCE))
    for p in[WORK,FREEZE]:require(not p.exists()and not p.is_symlink(),str(p))
    git_evidence=dict(schemaVersion=1,sourceRoot=str(SOURCE),repositoryRoot=str(REPO),detachedHead=head,baseline=BASE,noAlternates=True,noCommonDirOrGitdirRedirect=True,objectFiles=object_inventory,sourceObjectFilesCompared=len(source_objects),allObjectInodesDistinctFromRepository=True,allCloneObjectLinkCountsOne=True,gitInvokedByReviewer=False,packContentsNotDecoded=True)
    # Rehash every finite content input after all reconstruction checks.
    snapshots=list(observed.values())
    for r in snapshots:verify(r)
    write('input-hashes.json',dict(schemaVersion=1,files=snapshots,finalRehashPassed=True,canonicalTmpAliasNormalizationOnly=True))
    write('copy-review.json',dict(schemaVersion=1,copies=copy_inventory,expected533Plus33Targets=566,newNativeFiles=342,unchangedResourceParentNativeFiles=339,nativeReplacements=plan['nativeAfterimageReplacements']))
    write('git-isolation-review.json',git_evidence)
    write('old-protection-mode-observations.json',dict(schemaVersion=1,oldStageCopies=501,frozenCopies=666,frozenOriginalReferences=663,frozenMembership=667,frozenModeFixed=0o600,otherModesCurrentObservationsOnly=True,modes=old_modes))
    write('external-evidence.json',dict(schemaVersion=1,outerFiles=outer_files,innerFiles=inner_files,outerTerminal=report['outerTerminal'],innerTerminal=descriptor(inner_dir/'terminal.json'),wholeOuterRecords=outer_records,wholeInnerJournalEqualsRetainedJournal=True,outerObservedProcesses=len(outer['observedProcesses']),innerObservedProcesses=len(inner['observedProcesses']),allObservedOwnedGroupsGone=True,liveProcessQueryOrSignalByReviewer=False))
    values=dict(schemaVersion=1,state='INDEPENDENT_SCHEDULER_TASK_SELECTION342_SOURCE_STAGE_REVIEW_PASSED_V1',verifiedPassed=True,sourceIndexSha256=SOURCE_SHA,controllerSourceIndexSha256=CONTROLLER_SHA,nativeSourceFiles=342,unchangedResourceParentNativeFiles=339,nativeReplacements=3,configuredSourceRoot=str(SOURCE),workRoot=str(WORK),freezeRoot=str(FREEZE),actualControllerExitCode=0,actualStageExitCode=0,allObservedOwnedGroupsGone=True,buildExecuted=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsActionAuthority=False)
    descriptors=dict(actualJournal=report['actualJournal'],rootObservation=root_row,outerTerminal=report['outerTerminal'],innerTerminal=descriptor(inner_dir/'terminal.json'),rootAuthority=report['rootAuthority'],rootConfig=report['config'],stageObservation=report['stageObservation'])
    coverage=dict(stagePlanBase=533,completeSourceFamilyCopies=33,actualCopies=566,nativeSourceFiles=342,unchangedResourceParentNativeFiles=339,nativeReplacements=3,oldStageCopies=501,frozenCopies=666,frozenOriginalReferences=663,frozenMembership=667,outerRawJsonRecords=2,innerRawJsonRecords=1,outerObservedProcesses=len(outer['observedProcesses']),innerObservedProcesses=len(inner['observedProcesses']))
    write('results.json',dict(**values,**descriptors,coverage=coverage,sourceIndex=report['sourceIndex'],controllerSourceIndex=report['controllerSourceIndex'],integrationSourceReview=authority['sourceIndependentReview'],controllerSourceReview=authority['controllerSourceReview'],resourceArtifactReview=refs['resourceArtifactReview'],checks=checks,uniqueContentInputs=len(snapshots),reviewerScope='Independent read/hash/retained JSON and filesystem DATA only',ownerHelpersImported=False,stageOrGitOrBuildCommandsInvokedByReviewer=False,processQueriesOrSignalsInvokedByReviewer=False,
        qualifications=['Actual SOURCE stage only; no build/freeze/native artifact proof','partialObservationOnly remains true in actual controller observation; complete matching journal independently checked here','All566 copy modes match retained observations and current originals; old666 frozen modes fixed0600, other old501/663 protection is hash/size with current modes separately retained','Detached HEAD and independent object storage verified as files; Git pack contents and baseline whole worktree were not independently decoded','Actual optional-return ABI requires full new native rebuild; old resource engine cannot stand in for selector engine','No runtime/all-invalid fixture, full reset/reuse, ALS, security or performance acceptance']))
    write('result-contract.json',dict(schemaVersion=1,requiredReviewState=values['state'],requiredFixedValues=values,requiredCoverage=coverage,requiredExactDescriptors=descriptors,sourceStageOnly=True,nextBuildActionAuthority=None,issuesNoAuthority=True))
    print(json.dumps(dict(verifiedPassed=True,checks=checks,uniqueContentInputs=len(snapshots),copies=566,outerPid=95581,stagePid=95641)))


def write(name,value):
    with(OWN/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())


if __name__=='__main__':main()
