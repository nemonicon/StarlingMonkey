"""Independent actual source-stage DATA reader. Never imports owner source."""
from pathlib import Path
from collections import Counter
import ast,hashlib,json,os,stat
import review_io as I
HERE=Path(__file__).resolve().parent;S=HERE.parent;REPO=S.parents[2];P=S/'resource-integration-candidate-v1';DEST=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-source')
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'
def row(p):return I.descriptor(str(p))
def load(p):return I.read(row(p))
def eq(a,b,label):I.need(json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True),label)
def write(name,value):
    with(HERE/name).open('xb')as f:f.write((json.dumps(value,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
root_row=dict(path=str(S/'resource-integration-stage-v1-root-results.json'),sha256='6691c38ddb50b2b5a6e5cf344fa6b93fa42e3b0641c76cbef40ae1f57a4b8449',bytes=2175)
r=I.read(root_row);I.verify_descriptors(r,'whole actual completed Root stage observation');I.need(r['state']=='ROOT_OBSERVED_SCHEDULER_RESOURCE342_SOURCE_STAGE_PASSED_V1'and r['rootToolSession']==52275 and r['rootObservedToolRawExitCode']==0,'actual Root completed stage tuple')
cfg=I.read(r['rootConfig']);authority=I.read(r['rootAuthority']);journal=I.read(r['actualStageResult']);terminal=I.read(r['externalParentTerminal'])
own,own_members=I.indexed(r['sourceIndex'],'complete source20e6');I.need(r['sourceIndex']['sha256']=='20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414','exact new integration source index')
peer_pair=authority['sourceIndependentReview'];_,peer_members=I.indexed(peer_pair['index'],'complete actual independent source-review family');I.need(peer_pair['result']in peer_members,'exact source review result indexed')
peer=I.read(peer_pair['result']);I.need(peer['state']=='INDEPENDENT_SCHEDULER_RESOURCE_INTEGRATION_SOURCE_REVIEW_PASSED_V1'and peer['sourceIndexSha256']==r['sourceIndex']['sha256']and peer['sourceOnly']is True and peer['sourceReviewPassed']is True and peer['ownerActionsInvoked']is False,'actual source-only peer, no action projection')
for d in load(Path(peer_pair['index']['path']).parent/'rehashed-inputs.json')['files']:I.verify(d,'all original source-peer inputs unchanged')
I.verify_descriptors(authority,'whole actual stage authority including Root controller and genuine monitor');I.indexed(authority['externalMonitorIndex'],'full genuine process-monitor family')
eq(cfg,dict(schemaVersion=1,sourceIndex=r['sourceIndex'],rootAuthority=r['rootAuthority']),'whole actual Root config')
I.need(authority['schemaVersion']==1 and authority['state']=='ROOT_REVIEWED_SCHEDULER_RESOURCE342_SOURCE_STAGE_V1'and authority['phase']=='stage'and authority['stageAllowed']is True,'actual stage-only Root phase')
for flag in ['buildAllowed','componentAllowed','guestAllowed','runtimeAcceptanceClaim','sourcePromotionAllowed']:I.need(authority[flag]is False,'closed non-stage Root action '+flag)
I.need(authority['sourceRoot']==str(DEST)and authority['baseline']==BASE and authority['nativeFiles']==342 and authority['externalEmbeddingSources']==3,'actual accepted342 and separate embedding3 future context')
eq(authority['sourceIndexSha256'],r['sourceIndex']['sha256'],'actual authority source hash');eq(authority['entry'],row(P/'stage.py'),'genuine original-context stage entry')
plan=load(P/'stage-inputs.json');policy=load(P/'policy.json');pins=load(P/'baseline-pins.json');I.verify_descriptors(pins,'actual accepted ancestry and source-review descriptors')
for name in ['resourceSource','resourceSourceReview']:I.indexed(pins[name],'actual unchanged timer ownership source/peer')
for d in load(P/'input-freeze.json')['files']:I.verify(d,'full finite source preparation closure')
accepted=I.read(pins['acceptedMetadata']);parent=I.read(pins['parentPolicy']);I.need(len(plan['files'])==467 and len(accepted['sourceManifest'])==len(policy['expectedNativeSourceManifest'])==342,'finite genuine native342 and stage467 input plan')
eq(Counter(d['role']for d in plan['files']),Counter({'accepted342-native':342,'accepted-tool-source':89,'immutable-source-proof-data':36}),'all actual stage plan roles')
eq(accepted['sourceManifest'],parent['expectedNativeSourceManifest'],'accepted342 native ancestry, no355 context');eq(accepted['componentizeSourceManifest'],pins['externalEmbeddingSources'],'separate accepted embedding3 unchanged ancestry')
native_plan=[d for d in plan['files']if d['role']=='accepted342-native'];eq([dict(path=d['target'],sha256=d['original']['sha256'])for d in native_plan],accepted['sourceManifest'],'all original accepted342 stage inputs')
old={d['path']:d['sha256']for d in accepted['sourceManifest']};new={d['path']:d['sha256']for d in policy['expectedNativeSourceManifest']};changes=plan['nativeAfterimageReplacements'];I.need(set(old)==set(new)and len(changes)==2,'exact native manifest membership preserved')
eq(sorted(p for p in old if old[p]!=new[p]),sorted(d['path']for d in changes),'exact two actual ownership native replacements')
for d in changes:I.need(old[d['path']]==d['beforeSha256']and new[d['path']]==d['afterSha256'],'actual replacement before/after origin')
targets={}
for d in plan['files']:
    name=I.member(d['target']);I.need(name not in targets,'unique original stage target');I.verify(d['original'],'all planned original stage bytes');targets[name]=d['original']
for d in [r['sourceIndex'],*own_members]:targets[P.relative_to(REPO).as_posix()+'/'+Path(d['path']).relative_to(P).as_posix()]=d
for d in changes:
    p=P/'native'/d['path'];actual=row(p);I.need(actual['sha256']==d['afterSha256']and actual['bytes']==d['bytes'],'actual indexed native afterimage');targets[d['path']]=actual
targets['tests/node-compat/build-engine.sh']=row(P/'proposed/tests/node-compat/build-engine.sh')
I.need(len(targets)==501,'exact501 actual planned copies including entire original-context packet')
expected=dict(schemaVersion=1,state='RESOURCE342_SOURCE_STAGED_UNREVIEWED_V1',sourceIndex=r['sourceIndex'],rootAuthority=r['rootAuthority'],baseline=BASE,destination=str(DEST),nativeFiles=342,nativeReplacements=2,copies=[dict(path=str(DEST/name),original=d)for name,d in sorted(targets.items())],buildOrGuestInvoked=False)
eq(journal,expected,'whole actual501-row journal reconstructed from exact source/plan/origins')
serialized=(json.dumps(expected,indent=2)+'\n').encode();I.need(hashlib.sha256(serialized).hexdigest()==r['actualStageResult']['sha256']and len(serialized)==r['actualStageResult']['bytes'],'exact whole actual stage journal bytes, no origin projection')
copy_observations=[]
for name,d in sorted(targets.items()):
    original=I.verify(d,'all actual original provenance');p=I.verify(dict(d,path=str(DEST/name)),'all actual staged copies');a=original.stat();b=p.stat()
    I.need(stat.S_IMODE(a.st_mode)==stat.S_IMODE(b.st_mode),'actual copy/original file modes equal')
    I.need((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'actual copy/original distinct inode')
    I.need(b.st_nlink==1,'actual copied source has no hardlink alias')
    copy_observations.append(dict(path=str(p),original=d,sha256=d['sha256'],bytes=d['bytes'],mode=oct(stat.S_IMODE(b.st_mode)),device=b.st_dev,inode=b.st_ino,links=b.st_nlink,originalDevice=a.st_dev,originalInode=a.st_ino))
for path,digest in new.items():I.need(row(DEST/path)['sha256']==digest,'all342 genuine final native source hashes')
eq(I.read(terminal['stdout']),journal,'whole compact raw stdout equals complete actual stage journal');I.verify_descriptors(terminal,'all actual raw terminal streams')
for key,value in dict(schemaVersion=1,pid=91561,rawExitCode=0,timeout=False,forcedCleanup=False,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True).items():eq(terminal[key],value,'actual clean parent terminal '+key)
for key in ['interruptedSignals','remainingObservedPids','signals','errors']:eq(terminal[key],[],'actual no residual/failure '+key)
eq(terminal['authority'],r['rootAuthority'],'actual terminal authority');eq(terminal['finalGroups'],[dict(pgid=91561,alive=False,signalAllowed=False)],'single observed parent group gone')
ex=Path(r['externalParentTerminal']['path']).parent;events=[]
for p in sorted(ex.iterdir()):
    I.verify(row(p),'complete actual raw external capture')
    if p.name.startswith('owned-'):event=load(p);I.need(event['sequence']==len(events),'ordered ownership events');events.append(event['process'])
eq(events,terminal['observedProcesses'],'all actual retained process identity objects');I.need(len(events)==5 and events[0]['pid']==91561 and all(p['pgid']==91561 for p in events),'five actual observed stage/Git process records')
I.exact_tree(ex,['started.json','terminal.json','stdout.log','stderr.log',*[f'owned-{n:04d}.json'for n in range(5)]])
started=load(ex/'started.json');I.need(started['pid']==91561 and started['timeoutSeconds']==2400 and started['argv'][1:4]==['-B','-I',str(P/'stage.py')],'actual bounded isolated Python stage argv');eq(I.decode(started['argv'][4].encode()),r['rootConfig'],'actual argv config binding');eq(started['authority'],r['rootAuthority'],'actual started authority')
stderr=I.verify(terminal['stderr']).read_text();I.need(stderr.startswith("Cloning into '"+str(DEST)+"'...")and 'HEAD is now at 54b3329 'in stderr and terminal['stderr']['bytes']==200,'retained completed clone/checkout diagnostic, not an empty-stderr invention')
# File-only Git metadata observation: no Git command or object parser is invoked.
git=DEST/'.git';I.need(git.is_dir()and not git.is_symlink(),'separate actual Git directory');head=row(git/'HEAD');I.verify(head,'actual detached checkout HEAD');I.need((git/'HEAD').read_text()==BASE+'\n','actual detached accepted baseline HEAD')
for name in ['commondir','objects/info/alternates','objects/info/http-alternates']:I.need(not(git/name).exists()and not(git/name).is_symlink(),'no shared Git/object alternate '+name)
git_rows={};git_ids={}
for label,root in [('stage',git/'objects'),('original',REPO/'.git/objects')]:
    rows=[];ids=set()
    for base,dirs,files in os.walk(root,followlinks=False):
        for name in dirs:I.need(not(Path(base)/name).is_symlink(),'no object directory link')
        for name in sorted(files):
            p=Path(base)/name;d=row(p);I.verify(d,'actual '+label+' Git object DATA');s=p.stat();ids.add((s.st_dev,s.st_ino));rows.append(dict(**d,relativePath=p.relative_to(root).as_posix(),device=s.st_dev,inode=s.st_ino,links=s.st_nlink))
    git_rows[label]=rows;git_ids[label]=ids
I.need(git_ids['stage'].isdisjoint(git_ids['original']),'no actual original/staged Git-object inode intersection')
for p in [P/'stage.py',Path(authority['controller']['path']),Path(authority['externalMonitorEntry']['path'])]:ast.parse(I.verify(row(p)).read_text())
stage=I.verify(authority['entry']).read_text();I.need("['git','clone','--no-local','--no-checkout',str(REPO),str(DEST)]"in stage and "['git','-C',str(DEST),'checkout','--detach',BASE]"in stage,'actual clone isolation and detached checkout APIs')
I.need(stage.index("subprocess.run(['git','clone'")<stage.index('for name,d in sorted(targets.items())')<stage.index('for d in captured:checked(d)')<stage.index("with JOURNAL.open('x')"),'actual stage copy/fsync and final input checks before exclusive journal')
I.need("out.flush();os.fsync(out.fileno())"in stage and "target.chmod(source.stat().st_mode&0o777)"in stage,'actual durable source copies and exact modes')
I.need(not Path(authority['workRoot']).exists(),'no build workRoot exists at finite stage audit')
for label,root in [('stage',git/'objects'),('original',REPO/'.git/objects')]:eq(sorted(p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()),sorted(d['relativePath']for d in git_rows[label]),'final Git object membership stable')
I.final_rehash()
write('expected-stage-journal.json',expected);write('copy-observations.json',dict(schemaVersion=1,copies=copy_observations,allHashesModesAndDistinctInodesVerified=True))
write('git-data-observations.json',dict(schemaVersion=1,detachedHead=head,baseline=BASE,gitDirectory=str(git),stageObjectFiles=git_rows['stage'],originalObjectFiles=git_rows['original'],inodeIntersectionEmpty=True,alternatesAbsent=True,gitCommandsInvokedByReviewer=False,gitObjectSemanticDecodePerformed=False))
write('rehashed-inputs.json',dict(schemaVersion=1,files=list(I.ROWS.values()),allFinalInputsStable=True,ownerActionsInvokedByReviewer=False))
write('data-results.json',dict(schemaVersion=1,state='ACTUAL_RESOURCE342_SOURCE_STAGE_DATA_AUDIT_PASSED',rootObservation=root_row,actualStageResult=r['actualStageResult'],sourceIndex=r['sourceIndex'],rootAuthority=r['rootAuthority'],rootConfig=r['rootConfig'],externalParentTerminal=r['externalParentTerminal'],sourceIndependentReview=peer_pair,copiedRows=501,initialPlanRows=467,fullSourcePacketRows=34,nativeSourceFiles=342,unchangedNativeFiles=340,nativeAfterimages=2,externalEmbeddingSourceAncestry=3,externalEmbeddingSourcesCopiedInStage=0,wholeJournalValuesAndBytesEqual=True,allCopiesOriginalsHashesModesAndDistinctInodesVerified=True,allFinalNativeHashesVerified=True,actualStageJournalStatePreserved='RESOURCE342_SOURCE_STAGED_UNREVIEWED_V1',detachedBaseline=BASE,stageGitObjectFiles=len(git_rows['stage']),originalGitObjectFiles=len(git_rows['original']),noGitObjectInodeIntersection=True,noAlternates=True,rawExitCode=0,observedProcesses=5,observedGroups=1,externalFiles=9,stderrBytes=200,stdoutBytes=terminal['stdout']['bytes'],buildWorkRootAbsent=True,physicalInputs=len(I.ROWS),readHashChecks=I.CHECKS,sourceAndStageOnly=True,reviewerOwnerActionsInvoked=False,buildInvoked=False,engineExecuted=False,componentOrGuestInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
print(json.dumps(dict(state='ACTUAL_RESOURCE342_SOURCE_STAGE_DATA_PASSED',physicalInputs=len(I.ROWS),checks=I.CHECKS,copies=501,nativeSources=342,buildInvoked=False,reviewerOwnerActionsInvoked=False)))
