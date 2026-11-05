"""Read-only actual combined355 source stage DATA audit; no owner imports."""
from pathlib import Path
import hashlib,json,stat

REPO=Path('/Users/dan/dev/StarlingMonkey');S=REPO/'tests/node-compat/foundation-scheduler'
A=S/'combined-native-integration-candidate-v1';B=S/'combined-native-stage-controller-candidate-v1'
OUT=Path(__file__).resolve().parent
DEST=Path('/private/tmp/starling-node-compat/combined-native355-v1-source')
CAP=Path('/private/tmp/starling-node-compat/combined-native355-v1-stage-external-root')
OBS=Path('/private/tmp/starling-node-compat/combined-native355-v1-stage-root-observer')
JOURNAL=Path('/private/tmp/starling-node-compat/combined-native355-v1-stage.json')
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'
checks=0;inputs={};aliases={};memberships={}
def check(v,label):
    global checks
    assert v,label;checks+=1
def d(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def physical(p):
    p=Path(p);check(p.is_absolute() and '..'not in p.parts,'absolute path')
    return Path('/private'+str(p)) if str(p).startswith('/tmp/') else p
def verify(row):
    r={k:row[k]for k in ['path','sha256','bytes']};p=physical(r['path'])
    for q in (p,*p.parents):check(not q.is_symlink(),'no symlink '+str(q))
    t=p.stat();check(stat.S_ISREG(t.st_mode)and t.st_size==r['bytes'],'regular size '+str(p))
    identity=(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns,stat.S_IMODE(t.st_mode),t.st_nlink)
    if str(p)not in inputs:check(d(p)['sha256']==r['sha256'],'full hash '+str(p));inputs[str(p)]=(r,identity)
    else:
        old,i=inputs[str(p)];check((old['sha256'],old['bytes'],i)==(r['sha256'],r['bytes'],identity),'consistent repeated physical role')
    aliases.setdefault(str(p),set()).add(r['path']);return p
def read(row):return json.loads(verify(row).read_bytes())
def load(p):return read(d(p))
def tree(root):
    rows=[]
    for p in sorted(root.rglob('*')):
        check(not p.is_symlink(),'tree no links '+str(p))
        if p.is_file():rows.append(p.relative_to(root).as_posix())
    return rows
def family(row):
    p=verify(row);v=read(row);root=p.parent;names=[];rows=[row]
    for f in v['files']:
        n=f['path'];check(not n.startswith('/')and all(x not in ('','.','..')for x in n.split('/')),'safe family member')
        r=dict(path=str(root/n),sha256=f['sha256'],bytes=f['bytes']);verify(r);names.append(n);rows.append(r)
    check(len(names)==len(set(names))and set(tree(root))==set(names)|{'index.json'},'complete indexed family')
    memberships[str(root)]=set(names)|{'index.json'};return rows
def git_objects(root):
    directory=root/'.git/objects';check(directory.is_dir()and not directory.is_symlink(),'real Git object directory')
    rows=[]
    for p in sorted(directory.rglob('*')):
        check(not p.is_symlink(),'Git object no symlink')
        if p.is_file():
            t=p.stat();rows.append(dict(path=p.relative_to(directory).as_posix(),device=t.st_dev,inode=t.st_ino,bytes=t.st_size,mode=stat.S_IMODE(t.st_mode)))
    return rows
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

jr=dict(path=str(JOURNAL),sha256='937907513bf5829d20a46f169964ae6d0b8ef94b62f799c8cbe7c38197f7a59e',bytes=1707498)
tr=dict(path=str(CAP/'terminal.json'),sha256='bb257e1227371d9380cad510e344351e899ff0c585f73e36df4ce6c192cdc901',bytes=2388)
j=read(jr);terminal=read(tr)
root=read(j['rootAuthority']);config=load(S/'combined-native355-v1-stage-root-config.json');invocation=load(S/'combined-native355-v1-stage-root-invocation.json')
for key in ['sourceIndex','stageControllerIndex','genericMonitorIndex']:family(root[key])
for key in ['integrationSourceReview','stageControllerReview']:
    rows=family(root[key]['index']);check(sum(r==root[key]['result']for r in rows[1:])==1,'review result indexed once');v=read(root[key]['result']);check(v['sourceOnly']is v['sourceReviewPassed']is True and v['ownerActionsInvoked']is False,'actual source peer pass')
check(root['sourceIndex']['sha256']=='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65','real combined source')
check(root['stageControllerIndex']['sha256']=='b1a21da1c0b925de8a7ccfb55113bff7487662051f95ba21d95b75e494864f1a','real stage controller')
check(root['state']=='ROOT_REVIEWED_COMBINED355_SOURCE_STAGE_V1'and root['phase']=='source-stage-only'and root['sourceStageAllowed']is True,'finite genuine Root phase')
for key in ['nativeBuildAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','keyOperationsAllowed','guestAllowed','gcAllowed','timingAllowed','normalMutationAllowed','metadataProjectionAllowed','privateBackendEvidenceHookEnabled','pinsAdopted','operationalAdmission','runtimeAcceptanceClaim']:check(root[key]is False,'closed '+key)
check(config['rootAuthority']==j['rootAuthority']==invocation['authority'],'actual authority identity')
check(config['sourceIndex']==root['sourceIndex']and config['controllerIndex']==root['stageControllerIndex'],'actual config contexts')
check(invocation['config']==d(S/'combined-native355-v1-stage-root-config.json'),'literal root invocation config')
verify(root['pythonExecutable']);verify(root['gitBinary']);verify(root['stageControllerEntry']);verify(root['genericMonitorEntry'])
check(invocation['argv']==[root['pythonExecutable']['path'],'-B','-I',root['stageControllerEntry']['path'],json.dumps(invocation['config'],separators=(',',':'))],'actual isolated controller argv')
for source in (A,B):
    for r in load(source/'input-hashes.json')['files']:verify(r)
plan=load(B/'stage-copy-plan.json')['files'];native=load(A/'native-origins.json')['files'];tools=load(A/'tool-origins.json')['files'];policy=load(A/'policy.json')
check(len(plan)==len({r['path']for r in plan})==1613,'exact target1613')
check(j['copies']==j['copiesCompleted']==plan and j['copiedFiles']==1613,'whole direct journal copy equality')
check(j['state']=='COMBINED355_SOURCE_STAGED_NOT_BUILT'and j['schemaVersion']==1,'actual journal state')
check(j['sourceIndexSha256']==root['sourceIndex']['sha256']and j['controllerIndex']==root['stageControllerIndex'],'actual source/current stage identities')
check(j['configuredSourceRoot']==str(DEST)==root['configuredSourceRoot'],'configured original root')
for k in ['workRoot','freezeRoot']:
    check(j[k]==root[k] and not Path(j[k]).exists()and not Path(j[k]).is_symlink(),'future '+k+' absent')
check(j['baselineRevision']==j['detachedHead']==BASE and verify(d(DEST/'.git/HEAD')).read_text()==BASE+'\n','actual detached baseline54b')
verify(d(DEST/'.git/config'))
check(not (DEST/'.git/objects/info/alternates').exists() and not (DEST/'.git/objects/info/alternates').is_symlink(),'no alternate object storage')
check(not DEST.is_symlink()and stat.S_IMODE(DEST.stat().st_mode)==0o700,'private actual source root')
for key in ['nativeBuildExecuted','engineExecuted','guestExecuted','metadataProjected','privateBackendEvidenceHookEnabled','operationalAdmission']:check(j[key]is False,'actual closed '+key)
check((j['nativeSourceFiles'],j['retainedParentNativeFiles'],j['changedNativeFiles'],j['externalEmbeddingSources'],j['selectedManifestCount'])==(355,348,7,3,11),'actual source counts')
original_objects=git_objects(REPO);staged_objects=git_objects(DEST)
object_ids={(r['device'],r['inode'])for r in original_objects};staged_object_ids={(r['device'],r['inode'])for r in staged_objects}
check(not object_ids&staged_object_ids,'current Git object inode independence')
copies=[];original_ids=set();target_ids=set()
for r in plan:
    original=verify(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']));target=verify(dict(path=str(DEST/r['path']),sha256=r['sha256'],bytes=r['bytes']))
    o=original.stat();t=target.stat();oi=(o.st_dev,o.st_ino);ti=(t.st_dev,t.st_ino)
    check(stat.S_IMODE(o.st_mode)==stat.S_IMODE(t.st_mode)==r['sourceMode'],'exact source/target mode')
    check(t.st_nlink==1 and ti!=oi and ti not in target_ids,'independent single-linked unique target')
    original_ids.add(oi);target_ids.add(ti)
    copies.append(dict(path=r['path'],original=r['original'],sha256=r['sha256'],bytes=r['bytes'],mode=r['sourceMode'],originalDevice=o.st_dev,originalInode=o.st_ino,targetDevice=t.st_dev,targetInode=t.st_ino,targetLinks=t.st_nlink))
check(not target_ids&(original_ids|object_ids|staged_object_ids),'no copied target aliases original or Git objects')
check(len(native)==355 and len(tools)==1226 and len(plan)-len(native)-len(tools)==32,'native/tool/family stage roles')
for manifest,value in zip(policy['selectedModuleManifests'],policy['selectedManifestValues']):check(load(DEST/manifest['path'])==value,'actual whole selected manifest')
check(len(policy['selectedModuleManifests'])==11,'actual full manifest count11')
check(terminal['authority']==j['rootAuthority']and terminal['rawExitCode']==0 and terminal['timeout']is terminal['forcedCleanup']is False,'authentic owned raw0')
for k in ['interruptedSignals','remainingObservedPids','signals','errors']:check(terminal[k]==[],'clean terminal '+k)
check(terminal['parentOwnedGroupGone']is terminal['allObservedOwnedGroupsGone']is True and terminal['finalGroups'] and all(g['alive']is False for g in terminal['finalGroups']),'retained all observed groups gone')
worker_raw=verify(terminal['stdout']).read_bytes();check(verify(terminal['stderr']).stat().st_size==0,'worker stderr empty')
worker=[json.loads(s)for s in worker_raw.splitlines()];check(worker==[dict(journal=jr,state=j['state'],copiedFiles=1613)],'full worker one-row stdout')
parent_rows=[json.loads(s)for s in verify(d(OBS/'stdout.log')).read_bytes().splitlines()];check(verify(d(OBS/'stderr.log')).stat().st_size==0,'Root observer stderr empty')
check(len(parent_rows)==2 and parent_rows[0]==dict(pid=terminal['pid'],timeoutSeconds=600),'Root stdout launch prefix separate')
end=parent_rows[1];check(end['state']=='COMBINED355_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1'and end['actualStageResult']==jr and end['externalTerminal']==tr and end['copiedFiles']==1613,'whole final parent stage envelope')
started=load(CAP/'started.json');check(started['authority']==j['rootAuthority']and started['pid']==terminal['pid']and started['timeoutSeconds']==600,'owned launch identity')
check(started['argv']==[root['pythonExecutable']['path'],'-B','-I',root['stageControllerEntry']['path'],'--stage-worker',json.dumps(invocation['config'],separators=(',',':'))],'genuine owned worker arguments')
events=[]
for p in sorted(CAP.glob('owned-*.json')):
    v=load(p);check(v['sequence']==len(events),'owned ordered observation');events.append(v)
check([e['process']for e in events]==terminal['observedProcesses'],'every raw owned process equals terminal')
check(any(e['process']['pid']==terminal['pid']for e in events),'owned root process observed')
expected_commands=[[root['gitBinary']['path'],'clone','--no-local','--no-checkout',str(REPO),str(DEST)],[root['gitBinary']['path'],'-C',str(DEST),'checkout','--detach',BASE]]
check([r['argv']for r in j['commands']]==expected_commands,'both literal actual Git commands')
for r in j['commands']:
    check(r['returncode']==0 and r['timedOut']is False and r['timeoutSeconds']==120,'actual Git raw0 with bound')
    for k in ['stdout','stderr']:verify(r[k])
    v=read(r['terminal']);check(v=={**{k:x for k,x in r.items()if k!='terminal'},'rawStreamsRetainedBeforeAssertions':True},'raw full Git terminal equals journal')
progress=[json.loads(s)for s in verify(j['progress']).read_bytes().splitlines()]
check(len(progress)==1616 and progress[0]==dict(event='authenticated-stage-start',sourceIndexSha256=root['sourceIndex']['sha256'],plannedCopies=1613),'progress start/count')
check([p['record']for p in progress if p['event']=='git-command-returned']==j['commands'],'raw Git progress equality')
copied=[p for p in progress if p['event']=='copy-verified'];check(len(copied)==1613,'all copies progress')
for i,(p,r)in enumerate(zip(copied,plan)):check(p==dict(event='copy-verified',count=i+1,path=r['path'],sha256=r['sha256'],bytes=r['bytes']),'ordered full copy progress')
actual_capture=set(tree(CAP));expected_capture={'started.json','terminal.json','stdout.log','stderr.log','stage-commands/progress.jsonl'}|{p.name for p in CAP.glob('owned-*.json')}|{f'stage-commands/{i}/{n}'for i in range(2)for n in ['stdout.log','stderr.log','terminal.json']}
check(actual_capture==expected_capture,'complete actual capture membership')
memberships[str(CAP)]=actual_capture;memberships[str(OBS)]=set(tree(OBS))
root_descriptor=dict(path=str(S/'combined-native355-v1-stage-root-results.json'),sha256='53c53d52a511aa33fefcd5ad6000bd302c3df928f26223f74a4b83ac5b41d799',bytes=13593)
root_report=read(root_descriptor)
check(verify(dict(path=str(OBS/'root-observation.json'),sha256=root_descriptor['sha256'],bytes=root_descriptor['bytes'])).read_bytes()==verify(root_descriptor).read_bytes(),'whole Root observation retained byte exact')
check(root_report['state']=='ROOT_OBSERVED_COMBINED355_SOURCE_STAGE_ZERO_UNREVIEWED_V1' and root_report['actualStageResult']==jr and root_report['externalParentTerminal']==tr,'Root actual direct tuples')
check(root_report['rootAuthority']==j['rootAuthority'] and root_report['rootConfig']==invocation['config'] and root_report['invocation']==d(S/'combined-native355-v1-stage-root-invocation.json'),'Root actual authority/config/invocation')
check(root_report['rootToolObservation']==dict(kind='exec_command/write_stdin terminal observation, not a fabricated process log',sessionId=63390,exitCode=0),'Root tool observation role not invented outer log')
check(root_report['copiedFiles']==1613 and root_report['nativeSourceFiles']==355 and root_report['selectedManifestCount']==11 and root_report['allObservedOwnedGroupsGone']is True,'Root summary actual counts')
for k in ['nativeBuildExecuted','engineOrGuestExecuted','operationalAdmission','runtimeAcceptanceClaim']:check(root_report[k]is False,'Root closed '+k)
retained=[]
check(len(root_report['retainedEvidenceCopies'])==20,'twenty retained raw text copies')
for pair in root_report['retainedEvidenceCopies']:
    original=verify(pair['original']);saved=verify(pair['retained'])
    check(original.read_bytes()==saved.read_bytes(),'whole raw retained copy equals actual')
    a=original.stat();b=saved.stat();check((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'retained raw file independent inode')
    retained.append(saved.relative_to(S/'combined-native355-v1-stage-root-evidence').as_posix())
check(set(tree(S/'combined-native355-v1-stage-root-evidence'))==set(retained),'exact retained raw evidence membership')
memberships[str(S/'combined-native355-v1-stage-root-evidence')]=set(retained)
for path,(r,identity)in inputs.items():
    p=Path(path);t=p.stat();check((t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns,stat.S_IMODE(t.st_mode),t.st_nlink)==identity,'final input identity/mode/link')
    check(d(p)['sha256']==r['sha256'],'final full input hash')
for path,names in memberships.items():check(set(tree(Path(path)))==names,'final complete family/capture membership')
check(git_objects(REPO)==original_objects and git_objects(DEST)==staged_objects,'current Git observation stability')
write(OUT/'input-hashes.json',dict(schemaVersion=1,files=[dict(**r,physicalPath=p,originalDescriptorPaths=sorted(aliases[p]),mode=i[-2],links=i[-1])for p,(r,i)in sorted(inputs.items())]))
write(OUT/'copy-review.json',dict(schemaVersion=1,files=copies,filesCount=1613,allHashesModesAndIndependentInodes=True))
write(OUT/'git-isolation-review.json',dict(schemaVersion=1,detachedHead=BASE,originalObjects=original_objects,stagedObjects=staged_objects,objectsInodeDisjoint=True,objectContentDecoded=False,originalPreStageObjectsRawTableRetained=False,limit='Source asserts pre/post Git identity equality; independent reader checks current disjoint object observations and detached HEAD, not historical object bytes.'))
write(OUT/'audit-data.json',dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_ACTUAL_STAGE_DATA_AUDIT_PASSED',checks=checks,uniqueInputFiles=len(inputs),inputBytes=sum(r['bytes']for r,i in inputs.values()),actualStageResult=jr,externalParentTerminal=tr,rootAuthority=j['rootAuthority'],rootConfig=invocation['config'],rootObservation=root_descriptor,rootInvocation=d(S/'combined-native355-v1-stage-root-invocation.json'),parentStdout=d(OBS/'stdout.log'),parentStderr=d(OBS/'stderr.log'),stageCopies=1613,ownedObservedProcesses=len(events),progressRows=len(progress),retainedRawCopies=20,sourceFiles=355,selectedManifestCount=11,sourceBaseline=BASE,rawControllerParentJsonRows=2,rawWorkerJsonRows=1,ownerActionsInvoked=False,gitHelperStageBuildEngineGuestInvoked=False))
print((OUT/'audit-data.json').read_text())
