"""Actual terminal14463 failed cache preparation DATA; no build/helper actions."""
from pathlib import Path
import ast,hashlib,json,stat
P=Path(__file__).resolve().parent;K=P.parent;SOURCE=K/'node-crypto-hash-hmac-native-controller-candidate-v1'
checks=0;rows={};snapshots={}
def need(v,m):
 global checks
 assert v,m;checks+=1

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def desc(p):p=Path(p);return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def ident(p):s=Path(p).lstat();return(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def checked(r):
 p=Path(r['path']);need(p.is_absolute()and p.is_file()and not p.is_symlink()and p.stat().st_size==r['bytes']and sha(p)==r['sha256'],'exact immutable failure/preflight DATA');rows[str(p)]=r;snapshots[str(p)]=ident(p);return p

def read(r):return json.loads(checked(r).read_bytes())
pre=json.loads((P/'preflight-summary.json').read_bytes());ledger=json.loads((P/'input-hashes.json').read_bytes())
for r in ledger['files']:checked(r)
report=desc(K/'node-crypto-hash-hmac-native-build-v2-root-results.json');need(report['sha256']=='6fd6198ed0b85d131edc2415443664bbbccb96417b4b153d98ed40556202952c'and report['bytes']==6091,'actual final report tuple');r=read(report)
need(r['state']=='ROOT_OBSERVED_HASH_HMAC357_BUILD_PREPARATION_FAILED_V2'and r['toolObservation']==dict(sessionId=14463,rawExitCode=1),'actual terminalfailed original14463')
for n,v in r.items():
 if type(v)is dict and set(v)=={'path','sha256','bytes'}:checked(v)
need(r['controllerIndex']==pre['sourceIndex']and r['sourcePeer']==pre['sourcePeer']and r['rootAuthority']==pre['roles']['authority']and r['config']==pre['roles']['config']and r['invocation']==pre['roles']['invocation'],'same actual Rootpreflight scope')
refs=json.loads((SOURCE/'references.json').read_bytes());root=read(r['rootAuthority']);value=read(r['actualBuildResult']);launch=read(r['actualBuildLaunch'])
need(value['state']=='native-build-failed-or-incomplete'and value['launcherExitCode']==1 and value['rawChildExitCode']is None and value['cacheCopiesCompleted']==[]and value['diskFreeSamplesDuringBuildCommand']==[],'workerfailed before recipe child launch and cache recordappend')
need(value['rootAuthority']==r['rootAuthority']and value['controllerIndex']==pre['sourceIndex']and value['sourceIndexSha256']==refs['integrationSourceIndex']['sha256']and value['actualStageReview']==refs['actualStageReview']and value['explicitEnvironment']==refs['buildEnvironment'],'whole actual original lifecycle result/context')
for n in ['configuredSourceRoot','workRoot','freezeRoot']:need(value[n]==refs[n],'actual configured/work/freeze '+n)
need(value['command']==[refs['bash']['path'],refs['recipe']['path']],'intended command record only, not executed process')
need(value['launcherErrors']==[dict(stage='build-cache-or-metadata',type='AssertionError',message='')]and value['evidenceComplete']is False and value['allSourceStageOriginalAndCacheInputsPreserved']is True,'actual bounded error and preservation record')
for n in ['engineExecuted','guestExecuted','cryptoOperationsInvoked','liveEvpSnapshotAdmission','operationalAdmission','runtimeAcceptanceClaim']:need(value[n]is False,'actual closed '+n)
need(launch['state']=='NODE_CRYPTO_HASH_HMAC357_NATIVE_BUILD_STARTED_V1'and launch['rawChildExitCode']is None and launch['cacheCopiesCompleted']==[]and launch['rootAuthority']==r['rootAuthority'],'actual intended launchframe is not recipe spawn')
owner=Path(refs['buildOutputRoot']);work=Path(refs['workRoot']);need({p.relative_to(owner).as_posix()for p in owner.rglob('*')if p.is_file()}=={'launch.json','result.json'},'whole twofile owneroutput')
need({p.relative_to(work).as_posix()for p in work.rglob('*')if p.is_file()}=={'componentize-source.tar.gz'}and not any(p.is_symlink()for p in [work,*work.rglob('*')]),'whole onefile failedWORK no aliases')
for p in [owner,work]:need(p.is_dir()and stat.S_IMODE(p.lstat().st_mode)==0o700,'actual private root0700')
for p in owner.rglob('*'):
 if p.is_file():need(stat.S_IMODE(p.lstat().st_mode)==0o600 and p.lstat().st_nlink==1,'ownerprivate single-link output')
plan=read(refs['cachePlan']);first=plan['copies'][0];need(first['source']==r['sourceCacheFile']and first['target']=='componentize-source.tar.gz'and first['sourceMode']==first['outputMode']==0o644,'actual first private cacheplan')
a=checked(r['sourceCacheFile']);b=checked(r['partialWorkFile']);sa=a.lstat();sb=b.lstat();need(b==work/first['target']and r['partialWorkFile']['sha256']==r['sourceCacheFile']['sha256']and r['partialWorkFile']['bytes']==r['sourceCacheFile']['bytes']==162093,'whole original and partialcopy bytes')
need(stat.S_IMODE(sa.st_mode)==0o644 and stat.S_IMODE(sb.st_mode)==0o600 and sb.st_nlink==1 and(sa.st_dev,sa.st_ino)!=(sb.st_dev,sb.st_ino),'only copy mode assertion false: exact bytes/independentinode/singlelink')
need((0o644&~0o077)==0o600 and(0o755&~0o077)==0o700,'pure umask counterfactual, not actual target copy operation')
body=(SOURCE/'build_body.py').read_text();controller=(SOURCE/'controller.py').read_text();bt=ast.parse(body)
need("os.umask(0o077)"in body and "os.umask(0o077)"in controller and "fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,r['outputMode'])"in body and 'fchmod'not in body,'actual caller/callee mode masking with no restoringfchmod')
need(body.index("stat.S_IMODE(b.st_mode)==r['outputMode']")<body.index("result['cacheCopiesCompleted'].append(record)"),'failed mode predicate before append')
need(body.index("populate_cache(io.read(refs['cachePlan'])")<body.index("with(out/'build.log').open('xb')")<body.index('lifecycle.monitor_owned_command('),'cachephase before buildlog and original lifecycle recipe spawn')
for p in [owner/'build.log',Path(refs['enginePath']),Path(refs['enginePath']+'.build.json'),Path(refs['freezeRoot'])]:need(not p.exists(),'absent unreached log/engine/metadata/freeze')
terminals={n:read(r[n])for n in ['externalParentTerminal','outerTerminal']}
for n,t in terminals.items():
 need(t['rawExitCode']==1 and t['authority']==r['rootAuthority']and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True and t['timeout']is t['forcedCleanup']is False,'both parentraw1 clean')
 for f in ['errors','signals','interruptedSignals','remainingObservedPids']:need(t[f]==[],'no cleanup errors/signals '+f)
 need(all(not g['alive']for g in t['finalGroups']),'all observed groups gone');checked(t['stdout']);checked(t['stderr'])
inner=terminals['externalParentTerminal'];outer=terminals['outerTerminal'];need((outer['pid'],inner['pid'])==(73627,73792),'actual original parent/worker identity');worker_stdout=json.loads(checked(inner['stdout']).read_bytes());need(set(worker_stdout)=={'output','result'}and worker_stdout['output']==str(owner)and worker_stdout['result']==value,'genuine lifecycle envelope output and entire result equal saved file, no shortenedframe')
need(json.loads(checked(outer['stdout']).read_bytes())==dict(pid=inner['pid'],timeoutSeconds=7200),'outerstdout is only original monitor start, no invented final resultframe')
need('assert result'in checked(inner['stderr']).read_text()and "launcherExitCode"in checked(inner['stderr']).read_text(),'workerstderr records later launcherstatus assertion, not original mode stack')
need('AssertionError'in checked(outer['stderr']).read_text(),'parentnonzero assertion retained');need(r['originalCaughtAssertionStackRetained']is False,'original cache assertion stack notretained')
for n in ['recipeStarted','compilerStarted','buildLogCreated','newEngineObserved','newMetadataObserved','engineExecuted','guestExecuted','cryptoOperationsInvoked','freezeInvoked','workloadRerun','phaseSucceeded','buildAcceptanceClaim','runtimeAcceptanceClaim','liveEvpSnapshotAdmission','operationalAdmission']:need(r[n]is False,'no unexecuted action/proof '+n)
need(r['actualNewEngine']is r['actualNewMetadata']is r['actualMetadataFieldsObserved']is None,'no357/83 actualnative artifact claim')
raw=[]
for d in [report,*[r[n]for n in ['observer','actualBuildResult','actualBuildLaunch','externalParentTerminal','outerTerminal','externalStdout','externalStderr','outerStdout','outerStderr']]]:
 src=checked(d);dest=P/'raw/failure'/src.parent.name/src.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(src.read_bytes());need(sha(dest)==d['sha256'],'compact exact actual failure textcopy');raw.append(dict(original=d,copy=desc(dest)))
for p,v in snapshots.items():need(ident(p)==v,'final fixedSource/Root/actualfailure identitybookend')
for ix in ledger['families']:
 base=Path(ix['path']).parent;need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}=={'index.json',*[x['path']for x in json.loads(Path(ix['path']).read_bytes())['files']]},'final compact immutablefamily membership')
summary=dict(schemaVersion=1,state='ACTUAL14463_CACHE_PREPARATION_FAILURE_DATA_VALIDATED',rootResult=report,actualBuildResult=r['actualBuildResult'],actualBuildLaunch=r['actualBuildLaunch'],externalParentTerminal=r['externalParentTerminal'],outerTerminal=r['outerTerminal'],partialWorkFile=r['partialWorkFile'],sourceCacheFile=r['sourceCacheFile'],observer=r['observer'],preflightEvidence=desc(P/'preflight-summary.json'),checks=checks,currentHashFiles=len(rows),currentLogicalBytes=sum(x['bytes']for x in rows.values()),sourceRequestedMode=0o644,sourceObservedMode=0o644,requestedOutputMode=0o644,observedOutputMode=0o600,copyBytes=162093,copyHashMatchesOriginal=True,distinctInode=True,singleLink=True,completedCacheRecords=0,rawRecipeChildExitCode=None,workerLauncherExitCode=1,outerExitCode=1,innerExitCode=1,originalCaughtModeAssertionStackRetained=False,causeAttribution='Source-coupled inference from actual umask077/open0644/no-fchmod/order and retained exactbytes/independentinode/nlink1/mode0600; not an observed original assertion stack',recipeCompilerEngineOrCryptoStarted=False,actualBuildSucceeded=False,sourceControlledPreservationClaim=True,independentPreservationScope='253 compact Root/Source/peer/directrole files and7 families rehashed; original worker fullSource guard claim is Source-coupled, no historical mega-ledger replay',allOwnedGroupsGone=True,noForcedCleanupTimeoutSignalsErrors=True,sourceOnlyCounts357_3_12_83RemainRequirements=True,noOwnerActions=True)
(P/'actual-failure-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(P/'failure-input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=list(rows.values())),indent=2)+'\n');(P/'failure-raw-copy-ledger.json').write_text(json.dumps(dict(schemaVersion=1,files=raw),indent=2)+'\n');print(json.dumps({k:summary[k]for k in ['state','checks','currentHashFiles','currentLogicalBytes','observedOutputMode','completedCacheRecords','actualBuildSucceeded']}))
