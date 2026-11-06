"""Actual83192 early recipe failure DATA, full fourcopies only, no target calls."""
from pathlib import Path
import hashlib,json,stat
P=Path(__file__).resolve().parent;K=P.parent;SOURCE=K/'node-crypto-hash-hmac-native-controller-candidate-v2';rows={};snaps={};checks=0

def need(v,m):
 global checks
 assert v,m;checks+=1

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()

def desc(p):p=Path(p);return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def ident(p):s=Path(p).lstat();return(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def checked(d):
 p=Path(d['path']);need(p.is_absolute()and p.is_file()and not p.is_symlink(),'regular exactrole')
 if str(p)in rows:need(rows[str(p)]==d and snaps[str(p)]==ident(p),'same immutable role');return p
 need(p.stat().st_size==d['bytes']and sha(p)==d['sha256'],'whole exactbytes/SHA');rows[str(p)]=d;snaps[str(p)]=ident(p);return p

def read(d):return json.loads(checked(d).read_bytes())
source= json.loads((P/'source-joins-summary.json').read_bytes());need(source['mismatchedPolicyGuardCount']==2,'bounded Source literaljoin blocker')
for d in json.loads((P/'source-input-hashes.json').read_bytes())['files']:checked(d)
report=desc(K/'node-crypto-hash-hmac-native-build-v3-root-results.json');need(report['sha256']=='97b127f882ee3a73a1397920bb273cf142fbf24415cef5a161e0461e5161dbc0'and report['bytes']==12516,'actual finalreport');r=read(report)
need(r['state']=='ROOT_OBSERVED_HASH_HMAC357_EARLY_RECIPE_FAILED_V3'and r['toolObservation']==dict(sessionId=83192,rawExitCode=1),'original actual83192 failed')
def walk(v):
 if type(v)is dict:
  if set(v)=={'path','sha256','bytes'}:checked(v)
  else:
   for a in v.values():walk(a)
 elif type(v)is list:
  for a in v:walk(a)
walk(r);need(r['controllerIndex']==source['sourceIndex']and r['sourcePeer']==source['sourcePeer'],'held e8b+552 Source contexts')
refs=json.loads((SOURCE/'references.json').read_bytes());auth=read(r['rootAuthority']);cfg=read(r['config']);inv=read(r['invocation']);walk(inv)
need(auth['controllerIndex']==cfg['controllerIndex']==inv['controllerIndex']==r['controllerIndex']and cfg['rootAuthority']==inv['rootAuthority']==r['rootAuthority']and inv['config']==r['config']and auth['phase']=='build','whole actualRoot/config/invocation contexts')
need(auth['recipe']==r['producerRecipe']==source['recipe']and auth['helper']==r['producerHelper']==source['helper']and auth['policy']==r['producerPolicy']==source['policy']and auth['buildEnvironment']==refs['buildEnvironment'],'actual ownedproducer roles, no projection')
value=read(r['actualBuildResult']);need(value['state']=='native-build-failed-or-incomplete'and value['rawChildExitCode']==value['launcherExitCode']==1 and value['status']==1 and value['childStarted']is value['lifecycleComplete']is True and value['evidenceComplete']is False,'real recipechild1 with completedlifecycle, no buildacceptance')
need(value['controllerIndex']==r['controllerIndex']and value['rootAuthority']==r['rootAuthority']and value['command']==[refs['bash']['path'],refs['recipe']['path']]and value['explicitEnvironment']==refs['buildEnvironment'],'original lifecycle/frame/environment')
for n in ['configuredSourceRoot','workRoot','freezeRoot']:need(value[n]==refs[n],'actual Source workcontext '+n)
need(value['launcherErrors']==[]and value['stopReason']is None and value['stoppedForDiskSpace']is False and value['sigtermReceived']==0 and value['temporarySigtermHandlerRestored']is True,'no lifecyclelauncher/space/signal cause')
cleanup=value['ownedGroupCleanup'];need(cleanup['complete']is True and cleanup['events']==cleanup['errors']==[]and cleanup['rawChildExitCode']==1 and cleanup['pgid']==80385,'actual original ownedrecipe group80385 cleanup')
need(value['allSourceStageOriginalAndCacheInputsPreserved']is True,'Source coupled final preservation claim')
owner=Path(refs['buildOutputRoot']);work=Path(refs['workRoot']);need(len(r['ownerOutputFiles'])==7 and len(r['partialWorkFiles'])==5,'exact7owner5workfiles')
for root,files in [(owner,r['ownerOutputFiles']),(work,r['partialWorkFiles'])]:
 need({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(files),'whole actual finite partial membership')
 for name,d in files.items():need(Path(d['path'])==root/name,'confined actual partial tuple');checked(d)
 for p in [root,*root.rglob('*')]:need(not p.is_symlink()and(p.is_dir()or p.is_file()),'no alias/specialpartial')
plan=read(refs['cachePlan']);copies=value['cacheCopiesCompleted'];need(copies==r['cacheCopiesCompleted']and len(copies)==4,'all four genuine completed cachecopies')
for i,(want,done)in enumerate(zip(plan['copies'],copies),1):
 need(done['source']==want['source']and done['sourceMode']==want['sourceMode']and done['outputMode']==want['outputMode']and done['distinctInode']is True,'same plannedcopy')
 a=checked(done['source']);b=checked(done['target']);sa=a.lstat();sb=b.lstat();need(b==work/want['target']and sa.st_size==sb.st_size and done['source']['sha256']==done['target']['sha256'],'full cachecopy content/window')
 need(stat.S_IMODE(sa.st_mode)==done['sourceMode']and stat.S_IMODE(sb.st_mode)==done['outputMode']and sb.st_nlink==1 and(sa.st_dev,sa.st_ino)!=(sb.st_dev,sb.st_ino),'actual copy modes/inode/nlink, M1 fixed')
 need(read(r['ownerOutputFiles'][f'cache-copy-{i}.json'])==done,'actual durable percopy completion')
need([x['outputMode']for x in copies]==[420,420,420,493],'three0644 archives and one0755 binary, no executable run')
fresh=read(r['freshAbiRecord']);need(fresh['state']=='ACTUAL_FRESH_HASH_HMAC357_ABI_PRECONFIGURE_PATH_OBSERVATION_V1'and fresh['configuredSourceRoot']==refs['configuredSourceRoot']and fresh['workRoot']==refs['workRoot'],'actual freshABI recordcontexts')
for n in ['sourceDirExisted','buildDirExisted','artifactExisted','compilerLauncherReuseAllowed','rustIncrementalReuseAllowed']:need(fresh[n]is False,'actual historical prerecord '+n)
source_dir=Path(fresh['sourceDir']);need(source_dir.is_dir()and(source_dir/'lib').is_dir()and {p.relative_to(source_dir).as_posix()for p in source_dir.rglob('*')}=={'lib'},'actual only sourceDir/lib after historicalfalse record')
for p in [source_dir/'.source-archive-sha256',Path(fresh['buildDir']),Path(fresh['artifact']),Path(fresh['artifact']+'.build.json'),Path(refs['freezeRoot'])]:need(not p.exists(),'no extraction/build/artifact/freeze')
need(r['buildLog']==value['buildLog']==r['ownerOutputFiles']['build.log']and r['buildLog']['bytes']==0,'whole originalbuildlog empty')
terms={n:read(r[n])for n in ['externalParentTerminal','outerTerminal']}
for n,t in terms.items():
 need(t['rawExitCode']==1 and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True and t['forcedCleanup']is t['timeout']is False and t['authority']==r['rootAuthority'],'both parent1 clean')
 for f in ['errors','signals','interruptedSignals','remainingObservedPids']:need(t[f]==[],'no parent errors/signals '+f)
 need(all(not g['alive']for g in t['finalGroups']),'all observed groups gone');checked(t['stdout']);checked(t['stderr'])
inner=terms['externalParentTerminal'];outer=terms['outerTerminal'];envelope=json.loads(checked(inner['stdout']).read_bytes());need(set(envelope)=={'output','result'}and envelope['output']==str(owner)and envelope['result']==value,'entire actual worker envelope.result equals savedfullframe')
need(json.loads(checked(outer['stdout']).read_bytes())==dict(pid=inner['pid'],timeoutSeconds=7200),'original outerstartframe only, no fabricated finalpublication')
recipe_samples=[p for t in terms.values()for p in t['observedProcesses']if p['pid']==80385];need(recipe_samples and all(p['pgid']==80385 and p['ppid']==inner['pid']for p in recipe_samples),'actual sampled owned recipe PID/group,parent; ps label is not full argv')
need(r['policyGuardLiterals']==[x['expectedLiteral']for x in source['joins']if not x['matches']]and r['actualPolicySha256']==source['policy']['sha256'],'report policyjoin matches independent actual Source audit')
need(r['originalBashExecutionTraceRetained']is False and r['causeAttributionUsesSourceAndRetainedFileProperties']is True,'Bashtrace unavailable, explicit Sourcecoupled causality')
for n in ['sourceArchiveExtracted','helperCliReached','dependencyFetchReached','configureReached','compilerStarted','engineExecuted','guestExecuted','cryptoOperationsInvoked','freezeInvoked','workloadRerun','phaseSucceeded','buildAcceptanceClaim','runtimeAcceptanceClaim','liveEvpSnapshotAdmission','operationalAdmission']:need(r[n]is False,'no unreached action/buildclaim '+n)
need(r['actualNewEngine']is r['actualNewMetadata']is r['actualMetadataFieldsObserved']is None,'no actual357native/83 sidecar')
chosen=[report,*[r[n]for n in ['rootAuthority','config','invocation','observer','externalParentTerminal','outerTerminal','externalStdout','externalStderr','outerStdout','outerStderr']],*r['ownerOutputFiles'].values(),r['freshAbiRecord']];raw=[]
for d in {d['path']:d for d in chosen}.values():
 src=checked(d);dest=P/'raw'/src.parent.name/src.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(src.read_bytes());need(sha(dest)==d['sha256'],'compact exact actualtextcopy, no binarycopy');raw.append(dict(original=d,copy=desc(dest)))
for path,v in snaps.items():need(ident(path)==v,'current Source/actual/cache identity bookend')
for root in [SOURCE,Path(source['sourcePeer']['index']['path']).parent]:need({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}=={'index.json',*[x['path']for x in json.loads((root/'index.json').read_bytes())['files']]},'final Source/peer exactmembers')
summary=dict(schemaVersion=1,state='ACTUAL83192_EARLY_RECIPE_FAILURE_DATA_VALIDATED',rootResult=report,rootAuthority=r['rootAuthority'],rootConfig=r['config'],rootInvocation=r['invocation'],observer=r['observer'],actualBuildResult=r['actualBuildResult'],externalParentTerminal=r['externalParentTerminal'],outerTerminal=r['outerTerminal'],actualOwnerFiles=r['ownerOutputFiles'],actualPartialWorkFiles=r['partialWorkFiles'],freshAbiRecord=r['freshAbiRecord'],sourceIndex=r['controllerIndex'],sourcePeer=r['sourcePeer'],producerRecipe=r['producerRecipe'],producerHelper=r['producerHelper'],producerPolicy=r['producerPolicy'],checks=checks,currentHashFiles=len(rows),currentLogicalBytes=sum(d['bytes']for d in rows.values()),completedCopyRecords=4,allFourFullBytesModesIndependentInodesAndSingleLinksVerified=True,recipeRawExitCode=1,recipeLifecycleComplete=True,recipeProcessGroup=80385,outerParentPid=outer['pid'],innerWorkerPid=inner['pid'],allOwnedGroupsGone=True,originalBashTraceRetained=False,recipeMonitorSamples=recipe_samples,fullRecipeArgvFromMonitorObserved=False,helperCliFetchCompilerNotReachedAttribution='Source-coupled inference: first silent policyguard mismatch follows actual fresh record/lib and precedes helperCLI/fetch/compiler; no exact Bashtrace',actualBuildSucceeded=False,actualNewEngine=None,actualNewMetadata=None,original552SourceReviewMissedLiteralJoin=True,sourceControlledPreservationClaim=True,independentProtectionScope='Whole e8b/552 families plus actual Root/raw/fourcache bytes/modes/inodes and currentbookends; no old mega-ledger replay',ownerActionsInvoked=False)
(P/'failure-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(P/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=list(rows.values())),indent=2)+'\n');(P/'raw-copy-ledger.json').write_text(json.dumps(dict(schemaVersion=1,files=raw),indent=2)+'\n');print(json.dumps({k:summary[k]for k in ['state','checks','currentHashFiles','currentLogicalBytes','completedCopyRecords','recipeRawExitCode','actualBuildSucceeded']}))
