"""Independent retained build DATA reader. No Git, helper, compiler or engine action."""
from pathlib import Path
import hashlib,json,stat,os,struct,zlib,collections,ast,importlib.util,sys,time
sys.dont_write_bytecode=True
REPO=Path('/Users/dan/dev/StarlingMonkey');S=REPO/'tests/node-compat/foundation-scheduler';P=Path(__file__).resolve().parent;O=S/'combined-clock-diagnostics-native-integration-candidate-v3'
checks=0;rows={};identities={};families={};raw=[]
def yes(v,m='check'):
 global checks
 checks+=1
 assert v,m
def ident(s):return [s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def physical(p):
 p=Path(p);yes(p.is_absolute()and '..'not in p.parts,str(p))
 if str(p).startswith('/tmp/'):
  yes(os.readlink('/tmp')=='private/tmp'and Path('/tmp').resolve()==Path('/private/tmp'));p=Path('/private'+str(p))
 for x in [p,*p.parents]:yes(not x.is_symlink(),str(x))
 return p
def desc(p):
 p=physical(p);s=p.stat();yes(stat.S_ISREG(s.st_mode),str(p));h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 yes(ident(s)==ident(p.stat()),'unstable '+str(p));return dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size)
def checked(r):
 p=physical(r['path']);key=str(p)
 yes(set(r)=={'path','sha256','bytes'}and type(r['bytes'])is int and r['bytes']>=0,'descriptor')
 if key in rows:
  yes(rows[key]==dict(r,path=key),'conflicting '+key);yes(ident(p.stat())==identities[key],'identity '+key);return p
 yes(desc(p)==dict(r,path=key),'hash '+key);rows[key]=dict(r,path=key);identities[key]=ident(p.stat());return p
def read(r):return json.loads(checked(r).read_bytes())
def family(r):
 value=read(r);root=Path(r['path']).parent;names={'index.json'};out=[r]
 for x in value['files']:
  name=x['path'];yes(type(name)is str and not name.startswith('/')and all(t not in ('','.','..')for t in name.split('/'))and name not in names,'family name');names.add(name);rr=dict(x,path=str(root/name));checked(rr);out.append(rr)
 actual=set()
 for p in root.rglob('*'):
  yes(not p.is_symlink(),'family symlink')
  if p.is_file():actual.add(p.relative_to(root).as_posix())
 yes(names==actual,'family membership '+str(root));families[str(root)]=r;return out
def copyraw(p):
 p=Path(p);r=desc(p);q=P/'raw'/f'{len(raw):03d}'/p.name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());yes(q.read_bytes()==p.read_bytes(),'raw copy');raw.append(dict(original=r,copy=desc(q)));return r
def clean(v):
 yes(v['rawExitCode']==0 and v['parentOwnedGroupGone']is v['allObservedOwnedGroupsGone']is True,'raw clean')
 yes(v['timeout']is v['forcedCleanup']is False and all(v[k]==[]for k in ['errors','signals','interruptedSignals','remainingObservedPids']),'clean error fields')
 yes(all(x['alive']is False for x in v['finalGroups']),'groups')
rootrow=dict(path=str(S/'combined-clock-diagnostic357-build-v3-root-results.json'),sha256='ab822263e93c6f296ac2a72ed30a6660c086583abd39d5aeb3de1ef4f1d52660',bytes=3771);root=read(rootrow);own=root['sourceIndex'];family(own);refs=read(desc(O/'references.json'));family(root['sourceReviewIndex']);stageRows=family(root['actualStageReview']['index']);yes(root['actualStageReview']['result']in stageRows)
for ix in refs['families']:family(ix)
authority=read(root['rootAuthority']);cfg=read(root['rootConfig']);inv=read(root['invocation']);checked(inv['launcher']);yes(inv['sourceIndex']==own and inv['sourceReviewIndex']==root['sourceReviewIndex'])
# Original pure controller functions are used in their real source context only.
spec=importlib.util.spec_from_file_location('independent_clock357_build_data_original_pure_controller',checked(refs['controller']));c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);c.root_model(authority,own,refs,'build');c.peer_model(read(authority['sourceReview']['result']),own)
sr=read(root['actualStageReview']['result']);c.stage_review_model(sr,own,root['actualStageResult']);stage=read(root['actualStageResult']);yes(stage['state']=='CLOCK_DIAGNOSTIC357_SOURCE_STAGED_NOT_BUILT_V3')
yes(cfg['rootAuthority']==root['rootAuthority']and cfg['sourceIndex']==own and cfg['phase']=='build')
for key in ['rootAuthority','rootConfig','actualStageReview','actualStageResult']:yes(inv[key]==root[key],key)
protection=read(refs['protectedInputs']);ledgerRows=0
for lr in protection['fileLedgers']:
 for r in read(lr)['files']:checked(r);ledgerRows+=1
for r in read(protection['frozenCopyInventory'])['files']:
 checked(r['copy']);yes(stat.S_IMODE(Path(r['copy']['path']).stat().st_mode)==r['mode'])
 if r['original']is not None:checked(r['original'])
for r in protection['files']:checked(r)
for r in protection['modeRows']:checked(r['file']);yes(stat.S_IMODE(Path(r['file']['path']).stat().st_mode)==r['mode'])
for r in protection['aliases']:yes(Path(r['path']).is_symlink()and os.readlink(r['path'])==r['linkText']and str(Path(r['path']).resolve())==r['resolved'])
for r in protection['archiveHardlinks']:yes(os.path.samefile(r['path'],r['target']))
for k in ['pythonExecutable','bash','git','node','sdkArchive']:checked(refs[k])
for r in refs['hostTools']:checked(r['executable'])
b=read(root['actualBuildResult']);yes(b['sourceIndex']==own and b['rootAuthority']==root['rootAuthority']and b['config']==root['rootConfig']);yes(b['actualStageReview']==root['actualStageReview']and b['actualStageResult']==root['actualStageResult'])
for k in ['childStarted','lifecycleComplete','temporarySigtermHandlerRestored','allSourceStageOriginalAndCacheInputsPreserved','evidenceComplete']:yes(b[k]is True,k)
for k in ['engineExecuted','guestExecuted','clockRuntimeInvoked','operationalAdmission','stoppedForDiskSpace']:yes(b[k]is False,k)
yes(b['rawChildExitCode']==b['status']==b['launcherExitCode']==0 and b['sigtermReceived']==0 and b['stopReason']is None and b['launcherErrors']==[])
yes(b['ownedGroupCleanup']['complete']is True and b['ownedGroupCleanup']['events']==b['ownedGroupCleanup']['errors']==[]and b['ownedGroupCleanup']['rawChildExitCode']==0)
yes(b['freeBytesBefore']>=b['requiredStartFreeBytes']==2147483648 and b['stopBelowFreeBytes']==838860800 and b['freeBytesAfter']>=838860800 and b['externalParentDeadlineSeconds']==7200)
yes(b['rawMetadataFields']==82 and b['nativeSourceFiles']==357 and b['externalEmbeddingSources']==3 and b['selectedWholeManifests']==11 and b['explicitBuildEnvironment']==refs['buildEnvironment'])
yes(b['engine']==root['engine']and b['metadata']==root['metadata']);checked(root['engine']);checked(root['metadata']);checked(b['buildLog'])
source=Path(b['configuredSourceRoot']);work=Path(b['workRoot']);yes(str(source)==refs['contexts']['sourceRoot']and str(work)==refs['contexts']['workRoot']);yes(not Path(refs['contexts']['freezeRoot']).exists())
# Current original/copy targets and their fixed original roles.
plan=read(refs['copyPlan'])['files'];yes(stage['copiesCompleted']==plan and len(plan)==1583);targetids=set()
for r in plan:
 p=checked(dict(path=str(source/r['path']),sha256=r['sha256'],bytes=r['bytes']));origin=checked(r['origin']);s=p.stat();a=origin.stat();key=(s.st_dev,s.st_ino)
 yes(stat.S_IMODE(s.st_mode)==stat.S_IMODE(a.st_mode)==r['mode']and s.st_nlink==1 and key!=(a.st_dev,a.st_ino)and key not in targetids);targetids.add(key)
cachePlan=read(refs['cachePlan'])['copies'];yes(len(b['cacheCopiesCompleted'])==len(cachePlan)==4)
for actual,want in zip(b['cacheCopiesCompleted'],cachePlan):
 yes(actual['source']==want['source']and actual['mode']==want['outputMode']and actual['target']['path']==str(work/want['target']));p=checked(actual['source']);q=checked(actual['target']);a=p.stat();s=q.stat();yes(stat.S_IMODE(s.st_mode)==want['outputMode']and s.st_nlink==1 and(s.st_dev,s.st_ino)!=(a.st_dev,a.st_ino));yes(actual['source']['sha256']==actual['target']['sha256'])
# Full before/after DIRC semantic, flags/extensions and real retained stat data.
pre=checked(b['gitIndexPreimage']).read_bytes();after=checked(b['gitIndexAfterRecipe']['file']).read_bytes();yes(c.parse_index(pre)==b['gitIndexBeforeRecipe']['parsed']);yes(c.parse_index(after)==b['gitIndexAfterRecipe']['parsed']);yes(hashlib.sha256(pre).hexdigest()==b['gitIndexBeforeRecipe']['file']['sha256']);comparison=c.index_stat_only(b['gitIndexBeforeRecipe'],b['gitIndexAfterRecipe']);yes(comparison==b['gitIndexComparison']);yes(comparison['semanticsAndFlagsExtensionsUnchanged']is True)
p=source/'.git/index';s=p.stat();yes(stat.S_IMODE(s.st_mode)==b['gitIndexAfterRecipe']['mode']==0o600 and s.st_nlink==1 and(s.st_dev,s.st_ino)==(b['gitIndexAfterRecipe']['device'],b['gitIndexAfterRecipe']['inode']))
# Staged private Git config/HEAD/shallow/objects remain protected. User Git historical claims are not transferred.
for key in ['stagedGitConfig','stagedGitHead','stagedGitShallow']:checked(stage[key])
for r in stage['stagedGitObjects']:
 p=checked(r['file']);s=p.stat();yes(stat.S_IMODE(s.st_mode)==r['mode']and s.st_nlink==r['links']and(s.st_dev,s.st_ino)==(r['device'],r['inode']))
yes(sorted(str(p)for p in(source/'.git/objects').rglob('*')if p.is_file())==sorted(r['file']['path']for r in stage['stagedGitObjects']))
yes((source/'.git/HEAD').read_text()==c.BASE+'\n'and(source/'.git/shallow').read_text()==c.BASE+'\n'and not(source/'.git/objects/info/alternates').exists())
# Current configured file set = retained742 BASE union1583 overlay; baseline blobs were independently proved by stage peer.
base={r['path']:r for r in stage['baselineTreeFilesBeforeOverlay']};overlay={r['path']for r in plan};actual=set()
for p in source.rglob('*'):
 rel=p.relative_to(source).as_posix()
 if rel=='.git'or rel.startswith('.git/'):continue
 if p.is_symlink():yes(rel in c.DOCUMENT_LINKS and os.readlink(p)==c.DOCUMENT_LINKS[rel]);actual.add(rel)
 elif p.is_file():actual.add(rel)
yes(actual==set(base)|overlay)
# Raw two monitors and whole parent publication transport.
inner=Path(refs['contexts']['buildOutputRoot']);outer=Path(root['ownedTerminal']['path']).parent
for folder,cap,role in [(inner,7200,'build-worker'),(outer,inv['outerDeadlineSeconds'],'build-parent')]:
 t=read(desc(folder/'terminal.json'));clean(t);yes(t['authority']==root['rootAuthority']);start=read(desc(folder/'started.json'));yes(start['timeoutSeconds']==cap and start['authority']==root['rootAuthority']);yes(start['argv'][:4]==inv['actualArgv'][:4]and start['argv'][4]==role and json.loads(start['argv'][5])==root['rootConfig'])
 for key in ['stdout','stderr']:checked(t[key]);copyraw(t[key]['path'])
 yes(Path(t['stderr']['path']).read_bytes()==b'');copyraw(folder/'terminal.json');copyraw(folder/'started.json')
 for p in sorted(folder.glob('owned-*.json')):checked(desc(p))
 if folder==inner:
  frames=[json.loads(line)for line in Path(t['stdout']['path']).read_text().splitlines()];yes(len(frames)==1 and frames[0]==dict(output=str(Path(root['actualBuildResult']['path']).parent),result=b),'whole lifecycle result frame')
 else:
  lines=[json.loads(x)for x in Path(t['stdout']['path']).read_text().splitlines()];yes(len(lines)==2 and lines[0]['timeoutSeconds']==7200 and lines[0]['pid']==read(desc(inner/'started.json'))['pid']);yes(lines[1]['actualResult']==root['actualBuildResult']and lines[1]['externalParentTerminal']==desc(inner/'terminal.json')and lines[1]['state']=='CLOCK_DIAGNOSTIC357_PHASE_RAW_ZERO_UNREVIEWED_V3')
# Current metadata/distribution readers add genuinely measured files, never projected parent manifests.
md=read(desc(P/'metadata-review.json'));dist=read(desc(P/'distribution-review.json'));yes(md['passed']is dist['verifiedPassed']is True)
for r in md['extraInputs']+dist['extraInputs']:checked(r)
aliases=protection['aliases']+dist['referenceAliases']
for a in aliases:yes(Path(a['path']).is_symlink()and os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve())==a['resolved'])
for a in dist['archiveHardlinks']:yes(os.path.samefile(a['path'],a['target']))
m=read(root['metadata']);rust=m['privateRustupBootstrapPolicy'];before=read(rust['beforeInstallRecord']);settings=checked(rust['settingsAtBuildCompletion']);yes(settings.stat().st_size==107 and 'auto_self_update = "disable"'in settings.read_text()and rust['oldFailedWorkResumed']is False)
yes(before['privateHomes']==rust['privateHomes']if 'privateHomes'in before else True)
# Final full declared current hashes/modes/inodes, families, aliases. This is later than Source action bookends.
for r in list(rows.values()):yes(desc(r['path'])==r and ident(Path(r['path']).stat())==identities[r['path']],'final '+r['path'])
for ix in list(families.values()):family(ix)
for a in aliases:yes(os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve())==a['resolved'])
for r in protection['modeRows']:yes(stat.S_IMODE(Path(r['file']['path']).stat().st_mode)==r['mode'])
for a in protection['archiveHardlinks']+dist['archiveHardlinks']:yes(os.path.samefile(a['path'],a['target']))
for r in md['extraInputs']+dist['extraInputs']:yes(desc(r['path'])==r)
summary=dict(schemaVersion=1,passed=True,checks=checks,uniqueAuthenticatedFiles=len(rows),closedFamilies=len(families),fullCurrentHashModeIdentityBeforeFinalPassed=True,copyPlanRows=1583,nativeSources=357,toolCopies=1226,externalEmbeddingReferences=3,rawMetadataFields=82,wholeManifests=11,cacheCopies=4,stagedGitIndexComparison=comparison,userRepositoryGitHistoricalScopeNotTransferred=True,privateRustupSettingsBytes=107,freeBytesBefore=b['freeBytesBefore'],freeBytesAfter=b['freeBytesAfter'],rawRecipeExitCode=0,rawWorkerExitCode=0,rawOuterExitCode=0,allOwnedGroupsGone=True,currentAliases=len(aliases),newDistributionAliases=len(dist['referenceAliases']),newDistributionHardlinks=len(dist['archiveHardlinks']),helperOrRecheckOrBuildOrEngineOrGuestInvoked=False)
(P/'protection-review.json').write_text(json.dumps(summary,indent=2)+'\n');(P/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=sorted(rows.values(),key=lambda r:r['path'])),indent=2)+'\n');(P/'reference-aliases.json').write_text(json.dumps(dict(schemaVersion=1,files=aliases,archiveHardlinks=protection['archiveHardlinks']+dist['archiveHardlinks']),indent=2)+'\n');(P/'raw-copy-manifest.json').write_text(json.dumps(dict(schemaVersion=1,files=raw),indent=2)+'\n');print(json.dumps(summary))
