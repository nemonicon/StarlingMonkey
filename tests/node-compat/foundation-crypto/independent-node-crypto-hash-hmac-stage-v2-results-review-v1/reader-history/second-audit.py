"""Independent DATA reader. No owner imports, Git, subprocesses, stage, or native actions."""
from pathlib import Path
import hashlib,json,stat,os,shlex,ast
P=Path(__file__).resolve().parent; R=Path('/Users/dan/dev/StarlingMonkey'); K=R/'tests/node-compat/foundation-crypto'
S=K/'node-crypto-hash-hmac-stage-candidate-v2'; I=K/'node-crypto-hash-hmac-native-integration-candidate-v1'
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'; checks=0; observed={}; families={}
def yes(v,m='check'):
 global checks
 checks+=1
 assert v,m
def identity(p):
 s=p.lstat();return [s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def row(p):
 p=Path(p); before=identity(p);yes(stat.S_ISREG(before[2]),str(p));h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 yes(identity(p)==before,'changed during read '+str(p))
 v=dict(path=str(p),sha256=h.hexdigest(),bytes=before[4]);old=observed.get(str(p));yes(old is None or old['descriptor']==v,'inconsistent '+str(p));observed[str(p)]=dict(descriptor=v,identity=before);return v
def check(v):
 yes(set(v)>=set(('path','sha256','bytes')),'descriptor');p=Path(v['path'])
 if str(p) in observed:
  yes(identity(p)==observed[str(p)]['identity'],'changed '+str(p));got=observed[str(p)]['descriptor']
 else:got=row(p)
 yes(got=={k:v[k]for k in ('path','sha256','bytes')},'hash '+str(p));return p
def load(v):return json.loads(check(v).read_bytes())
def direct(p):return load(row(p))
def family(v):
 p=check(v); ix=json.loads(p.read_bytes());yes(ix['schemaVersion']==1)
 rr=[dict(x,path=str(p.parent/x['path']))for x in ix['files']];names=[x['path']for x in rr];yes(len(names)==len(set(names)))
 actual={str(x)for x in p.parent.rglob('*')if x.is_file()};yes(actual==set(names)|{str(p)},'family membership '+str(p))
 for x in rr:check(x)
 families[str(p)]=v;return [v,*rr]
def descriptors(v):
 if isinstance(v,dict):
  if set(v)>=set(('path','sha256','bytes'))and isinstance(v['bytes'],int):yield v
  else:
   for x in v.values():yield from descriptors(x)
 elif isinstance(v,list):
  for x in v:yield from descriptors(x)
def write(name,v):
 p=P/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n');return row(p)
rootrow=dict(path=str(K/'node-crypto-hash-hmac-stage-v2-root-results.json'),sha256='d033ece83df9623cb5428d76384d9b0915abe78ac236dba1c1e7d66d5408ea43',bytes=3491)
root=load(rootrow);yes(root['toolObservation']==dict(sessionId=37816,rawExitCode=0))
for v in descriptors(root):check(v)
j=load(root['stageJournal']);a=load(root['rootAuthority']);c=load(root['config']);inv=load(root['invocation']);D=Path(j['configuredSourceRoot']);OUT=Path(a['externalOutputRoot'])
yes(root['controllerIndex']==c['controllerIndex']==a['stageControllerIndex']==inv['sourceController']==j['controllerIndex']);yes(c['rootAuthority']==root['rootAuthority']==j['rootAuthority'])
yes(c['sourceIndex']==a['sourceIndex']==inv['integrationSource']);yes(a['integrationSourceReview']==inv['integrationPeer']);yes(a['stageControllerReview']==root['sourcePeer']==inv['sourcePeer'])
for v in descriptors(a):check(v)
for v in descriptors(inv):check(v)
for v in [root['controllerIndex'],a['sourceIndex'],a['genericMonitorIndex'],a['integrationSourceReview']['index'],a['stageControllerReview']['index']]:family(v)
for pair in [a['integrationSourceReview'],a['stageControllerReview']]:yes(pair['result'] in family(pair['index']))
peer=load(root['sourcePeer']['result']);yes(peer['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_STAGE_SOURCE_REVIEW_PASSED_V2'and peer['sourceOnly']and peer['sourceReviewPassed'])
inputs=direct(S/'input-hashes.json');yes(len(inputs['files'])==2779 and len(inputs['families'])==13)
for x in inputs['files']:check(x)
for x in inputs['families']:family(x)
ii=direct(I/'input-hashes.json');yes(len(ii['files'])==2622)
for x in ii['files']:check(x)
plan=direct(S/'stage-copy-plan.json');yes(len(plan['files'])==1642 and len(plan['embeddingData'])==3)
yes(j['copies']==j['copiesCompleted']==plan['files']);yes(j['copiedSourceFiles']==1642 and j['copiedEmbeddingDataFiles']==3)
for key,n in [('nativeSourceFiles',357),('retainedParentNativeFiles',353),('changedParentNativeFiles',2),('newNativeFiles',2),('externalEmbeddingSources',3),('selectedManifestCount',12)]:yes(j[key]==a[key]==n)
yes(j['state']=='NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGED_NOT_BUILT_V2'and j['initialVariant']=='normal-off')
for key in ['nativeBuildExecuted','engineExecuted','guestExecuted','cryptoOperationsInvoked','metadataProjected','operationalAdmission']:yes(j[key] is False)
for key in ['nativeBuildAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','keyOperationsAllowed','cryptoOperationsAllowed','guestAllowed','gcAllowed','borrowAllowed','timingAllowed','normalMutationAllowed','metadataProjectionAllowed','privateBackendEvidenceHookEnabled','pinsAdopted','operationalAdmission','runtimeAcceptanceClaim']:yes(a[key] is False)
for key in ['workRoot','freezeRoot']:yes(j[key]==a[key]and not Path(j[key]).exists())
yes(j['activeProducerOriginal']==str(I/'build-engine.sh')and j['activeHelperOriginal']==str(I/'layer-policy.py')and j['stagedSourceFamilyRole']=='DATA_ONLY')
source_ids=set();target_ids=set();targets=set()
for x in plan['files']:
 name=x['path'];yes(not Path(name).is_absolute()and '..'not in Path(name).parts and name not in targets);targets.add(name)
 orig=check(dict(path=x['original'],sha256=x['sha256'],bytes=x['bytes']));p=check(dict(path=str(D/name),sha256=x['sha256'],bytes=x['bytes']));si=orig.stat();st=p.stat();yes(stat.S_IMODE(si.st_mode)==x['sourceMode']);yes(stat.S_IMODE(st.st_mode)==x['targetMode']==0o600 and st.st_nlink==1);yes((si.st_dev,si.st_ino)!=(st.st_dev,st.st_ino));source_ids.add((si.st_dev,si.st_ino));yes((st.st_dev,st.st_ino)not in target_ids);target_ids.add((st.st_dev,st.st_ino))
for expected,x in zip(plan['embeddingData'],j['embeddingDataCompleted']):
 yes(x['source']==expected and x['role']=='REFERENCE_DATA_NOT_CONFIGURED_EXTERNAL_BUILD_SOURCE');orig=check(dict(path=expected['original'],sha256=expected['sha256'],bytes=expected['bytes']));p=check(x['target']);yes(str(p)==str(OUT/'embedding-reference'/expected['path']));yes(row(p)['sha256']==expected['sha256']and p.stat().st_size==expected['bytes']);yes(stat.S_IMODE(p.stat().st_mode)==0o600 and p.stat().st_nlink==1);yes((p.stat().st_dev,p.stat().st_ino)!=(orig.stat().st_dev,orig.stat().st_ino))
origprotect=load(j['originalProtection'])
for path,ident in origprotect.items():yes(identity(Path(path))==ident,'actual original stat '+path)
# Current hashes for every persisted original identity must have a source-authenticated descriptor.
yes(set(origprotect)<=set(observed),'unhashed original protection')
for key in ['allCopiedHashesModesAndDistinctInodesVerified','gitObjectInodesDisjoint','sourceOriginalInputsRechecked','originalGitObjectHashesAndIdentityUnchanged','finalOriginalGitProtectionPassed','finalInputProtectionPassed']:yes(j[key] is True)
yes(j['originalRepositoryConfig']==row(R/'.git/config'))
# Parse only retained raw Git responses, never invoke Git.
cmd=j['commands'];yes(len(cmd)==8)
prefix=[a['gitBinary']['path'],'--no-replace-objects']
for k,v in a['baselineGitPolicy']['clientConfig']:prefix+=['-c',k+'='+v]
upload=shlex.join(prefix+['-c','uploadpack.allowAnySHA1InWant=true','upload-pack'])
expected=[prefix+['init','--template='+a['baselineGitPolicy']['templateRoot'],'--object-format=sha1','--initial-branch=stage-baseline',str(D)],prefix+['-C',str(D),'fetch','--no-tags','--depth=1','--no-recurse-submodules','--no-auto-maintenance','--no-write-commit-graph','--upload-pack='+upload,R.as_uri(),BASE],prefix+['-C',str(D),'checkout','--detach',BASE],prefix+['-C',str(D),'rev-list','--count','HEAD'],prefix+['-C',str(D),'ls-tree','-r','-z','--full-tree',BASE]]
expected += [prefix+['-C',str(D),'cat-file','blob',x['gitObject']]for x in j['baselineDocumentationLinks']]
rawcopies=[]
for n,(x,argv)in enumerate(zip(cmd,expected)):
 yes(x['argv']==argv and x['cwd']==a['baselineGitPolicy']['commandCwd']);yes(x['timeoutSeconds']==120 and x['returncode']==0 and x['timedOut'] is False)
 yes(x['environmentPolicy']==dict(removedNames=[],valuesRecorded=False,userHomeVariablesPreserved=True,globalAndSystemConfigEntrypointsDisabled=True,exportedShellFunctionsRemoved=True))
 t=load(x['terminal']);yes(t==dict({k:v for k,v in x.items()if k!='terminal'},rawStreamsRetainedBeforeAssertions=True))
 for key in ['stdout','stderr','terminal']:check(x[key]);rawcopies.append(x[key])
yes(check(cmd[3]['stdout']).read_bytes()==b'1\n')
tr={}
raw=check(cmd[4]['stdout']).read_bytes();yes(raw.endswith(b'\0'))
for record in raw.split(b'\0')[:-1]:
 info,name=record.split(b'\t',1);mode,kind,oid=info.decode().split(' ');name=name.decode();yes(name not in tr);tr[name]=dict(mode=mode,kind=kind,object=oid)
pre=j['baselineOverlayPreimages'];yes(len(pre)==234 and len({x['path']for x in pre})==234);yes({x['path']for x in pre}==set(targets)&set(tr))
for x in pre:yes(x['gitTreeEntry']==tr[x['path']]and x['gitTreeEntry']['kind']=='blob'and x['ownedFreshBaselineCheckoutOnly'] is True and x['actual']['path']==str(D/x['path']))
links={x['path']:x['linkText']for x in j['baselineDocumentationLinks']};actual_links={str(p.relative_to(D)):os.readlink(p)for p in D.rglob('*')if p.is_symlink()};yes(actual_links==links and len(links)==3)
for x in j['baselineDocumentationLinks']:
 b=check(x['gitBlobRaw']).read_bytes();yes(b.decode()==x['linkText']and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['gitObject']==tr[x['path']]['object']);yes(x['consumedBySourceOrTools'] is False)
bo=j['baselineGitObservation'];yes(bo['reachableCommits']==1 and bo['tagAndRemoteRefs']==[]and bo['detachedHead']==BASE and bo['exactPackObjectSetClaim']is False and bo['transientPackByteCapClaim']is False)
for x in descriptors(bo):check(x)
yes((D/'.git/HEAD').read_bytes()==(BASE+'\n').encode());yes((D/'.git/shallow').read_bytes()==(BASE+'\n').encode());yes(not any(p.is_file()for p in (D/'.git/refs').rglob('*')));yes(not (D/'.git/objects/info/alternates').exists());yes(not (D/'.git/packed-refs').exists())
objects=[]
for p in sorted((D/'.git/objects').rglob('*')):
 yes(not p.is_symlink())
 if p.is_file():
  s=p.stat();d=row(p);objects.append(dict(path=p.relative_to(D/'.git/objects').as_posix(),device=s.st_dev,inode=s.st_ino,bytes=s.st_size,mode=stat.S_IMODE(s.st_mode),links=s.st_nlink,sha256=d['sha256']));yes((s.st_dev,s.st_ino)not in source_ids);yes(s.st_nlink==1)
yes(objects==j['stagedGitObjects']and sum(x['bytes']for x in objects)==857258==j['stagedGitObjectBytes'])
for folder in ['empty-template','disabled-hooks']:
 p=OUT/'git-policy'/folder;yes(p.is_dir()and not list(p.iterdir())and stat.S_IMODE(p.stat().st_mode)==0o700)
progress=[json.loads(x)for x in check(j['progress']).read_text().splitlines()];yes(progress[0]==dict(event='authenticated-stage-start',sourceIndexSha256=j['sourceIndexSha256'],plannedSourceCopies=1642,embeddingDataCopies=3))
yes([x['record']for x in progress if x['event']=='git-command-returned']==cmd)
yes([x['preimage']for x in progress if x['event']=='authorized-baseline-preimage']==pre)
yes([dict(event='source-copy-verified',count=n,path=x['path'])for n,x in enumerate(plan['files'],1)]==[x for x in progress if x['event']=='source-copy-verified']);yes(len(progress)==1885)
# Parent whole raw transport and actual durable terminal envelopes.
outer=load(root['outerTerminal']);inner=load(root['externalTerminal'])
for term in [outer,inner]:
 yes(term['authority']==root['rootAuthority']and term['rawExitCode']==0)
 for key in ['timeout','forcedCleanup']:yes(term[key]is False)
 for key in ['interruptedSignals','remainingObservedPids','signals','errors']:yes(term[key]==[])
 yes(term['parentOwnedGroupGone']and term['allObservedOwnedGroupsGone']and all(x['alive']is False for x in term['finalGroups']))
 yes(check(term['stderr']).read_bytes()==b'')
 for key in ['stdout','stderr']:rawcopies.append(term[key])
 rawcopies.append(row(Path(term['stdout']['path']).parent/'started.json'))
 rawcopies.append(row(Path(term['stdout']['path']).parent/'terminal.json'))
yes(outer['pid']==30967 and inner['pid']==31020)
worker=json.loads(check(inner['stdout']).read_bytes());yes(worker==dict(journal=root['stageJournal'],state=j['state'],copiedSourceFiles=1642,copiedEmbeddingDataFiles=3))
parent=[json.loads(x)for x in check(outer['stdout']).read_text().splitlines()];yes(len(parent)==2 and parent[0]==dict(pid=31020,timeoutSeconds=600));pr=parent[1];yes(pr['actualStageResult']==root['stageJournal']and pr['externalTerminal']==root['externalTerminal']and pr['state']=='NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V2');yes(pr['nativeBuildExecuted']is False and pr['engineExecuted']is False and pr['operationalAdmission']is False)
innerstart=direct(OUT/'started.json');outerstart=direct(Path(root['outerTerminal']['path']).parent/'started.json');yes(innerstart['timeoutSeconds']==600 and outerstart['timeoutSeconds']==1200)
yes(outerstart['argv']==inv['actualArgv']);yes(innerstart['argv'][:4]==inv['actualArgv'][:4]and innerstart['argv'][4]=='--stage-worker'and json.loads(innerstart['argv'][5])==root['config'])
# Authenticate complete raw monitor directories; process snapshots are DATA, not current OS attestation.
monitorfiles=[]
for folder in [OUT,Path(root['outerTerminal']['path']).parent]:
 for p in sorted(folder.rglob('*')):
  yes(not p.is_symlink())
  if p.is_file():monitorfiles.append(row(p))
# Parse actual native/manifests without running validator or loading facade.
native=direct(I/'native-origins.json')['files'];yes(len(native)==357 and len({x['path']for x in native})==357)
for x in native:yes(any(y['path']==x['path']and y['sha256']==x['sha256']and y['bytes']==x['bytes']for y in plan['files']))
manifestpaths=[x for x in native if x['path'].endswith('manifest.json')];yes(len(manifestpaths)==12)
for x in manifestpaths:direct(D/x['path'])
# Recheck all current observed identities. Actual-time Source flags remain source/controlflow evidence.
for path,x in list(observed.items()):yes(identity(Path(path))==x['identity'],'final observed identity '+path)
write('input-hashes.json',dict(schemaVersion=1,scope='Finite current stage/source/monitor/original/copy DATA; no recursive historical receipt discovery',files=[x['descriptor']for _,x in sorted(observed.items())]))
write('source-families.json',dict(schemaVersion=1,families=list(families.values())))
copyrows=[]
for n,x in enumerate(rawcopies):
 src=check(x);dst=P/'raw'/str(n).zfill(3)/src.name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes());yes(row(dst)['sha256']==x['sha256']);copyrows.append(dict(original=x,copy=row(dst)))
write('raw-copy-manifest.json',dict(schemaVersion=1,files=copyrows,scope='Only finite actual Git/parent full text streams/terminals/starts; no historical tree copies'))
write('data-check-results.json',dict(schemaVersion=1,passed=True,checks=checks,currentObservedFiles=len(observed),sourceFamilies=len(families),originalProtectionRows=len(origprotect),copiedSourceFiles=1642,copiedEmbeddingDataFiles=3,nativeSourceFiles=357,externalEmbeddingSources=3,selectedWholeManifests=12,baselinePreimages=234,gitCommands=8,sourceProgressRecords=len(progress),stagedGitObjectLogicalBytes=857258,rawTextCopies=len(copyrows),rawParentExitCodes=[0,0],reviewerOwnerFunctionsInvoked=False,reviewerGitCommandsInvoked=False,reviewerNativeOrGuestActionsInvoked=False))
print(json.dumps(dict(passed=True,checks=checks,files=len(observed),families=len(families),copies=1645,rawCopies=len(copyrows))))
