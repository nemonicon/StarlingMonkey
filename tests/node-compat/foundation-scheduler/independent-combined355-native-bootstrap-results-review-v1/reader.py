"""Independent actual combined355 bootstrap DATA reader. No owner imports/actions."""
from pathlib import Path
import ast,copy,hashlib,json,os,stat
P=Path(__file__).resolve().parent;S=P.parent;C=S/'combined-native-artifact-tooling-candidate-v1'
checks=0;seen={};identities={};raw_copies=[]
def need(v,label):
 global checks
 checks+=1
 assert v,label
def identity(p):
 s=Path(p).lstat();need(stat.S_ISREG(s.st_mode),'ordinary current file')
 return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode),s.st_nlink)
def row(p):
 p=Path(p);a=identity(p)
 if str(p)in seen:need(identities[str(p)]==a,'same captured identity');return seen[str(p)]
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 need(a==identity(p),'stable full hash read');r=dict(path=str(p),sha256=h.hexdigest(),bytes=a[2]);seen[str(p)]=r;identities[str(p)]=a;return r
def verify(r):
 need(type(r)is dict and all(k in r for k in ['path','sha256','bytes']),'descriptor DATA')
 need(row(r['path'])=={k:r[k]for k in ['path','sha256','bytes']},'exact descriptor');return Path(r['path'])
def parse(raw):
 def pairs(items):
  d={}
  for k,v in items:need(k not in d,'no duplicate JSON key');d[k]=v
  return d
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(AssertionError('nonfinite JSON')))
def read(r):return parse(verify(r).read_bytes())
def load(p):return read(row(p))
def same(a,b):
 if type(a)is not type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys()and all(same(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
 return a==b
def exact_tree(root,names,links=None,private=False):
 root=Path(root);s=root.lstat();need(stat.S_ISDIR(s.st_mode),'ordinary root');actual=set();found={}
 if private:need(stat.S_IMODE(s.st_mode)==0o700,'private root')
 for p in root.rglob('*'):
  n=p.relative_to(root).as_posix();s=p.lstat()
  if stat.S_ISLNK(s.st_mode):found[n]=os.readlink(p)
  elif stat.S_ISREG(s.st_mode):
   actual.add(n)
   if private:need(stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1,'private independent member')
  else:
   need(stat.S_ISDIR(s.st_mode),'ordinary directory')
   if private:need(stat.S_IMODE(s.st_mode)==0o700,'private subdirectory')
 need(actual==set(names)and found==(links or{}),'complete exact membership')
def family(ix):
 v=read(ix);base=Path(ix['path']).parent;names={'index.json'};rows=[]
 need(v['schemaVersion']==1 and type(v['files'])is list,'schema1 indexed family')
 for m in v['files']:
  n=m['path'];need(n not in names and n and not n.startswith('/')and '\\'not in n and all(x not in('','.','..')for x in n.split('/')),'unique confined member');names.add(n);r=dict(path=str(base/n),sha256=m['sha256'],bytes=m['bytes']);verify(r);rows.append(r)
 exact_tree(base,names);return rows
def proof(pair):
 rows=family(pair['index']);need(rows.count(pair['result'])==1,'result indexed exactly once');return read(pair['result'])
def contract(pair,desc):
 p=proof(pair);v=read(desc)
 need(p['state']==v['requiredReviewState']and p['verifiedPassed']is True,'real prerequisite DATA PASS')
 for group in ['requiredFixedValues','requiredExactDescriptors']:
  for k,x in v[group].items():need(same(p[k],x),'whole prerequisite '+k)
 need(same(p['coverage'],v['requiredCoverage']),'whole prerequisite coverage');return p
def clean(t,authority,pid):
 need(t['schemaVersion']==1 and type(t['rawExitCode'])is int and t['rawExitCode']==0 and t['pid']==pid and t['authority']==authority,'actual clean raw0/identity')
 for k in ['timeout','forcedCleanup']:need(t[k]is False,'no '+k)
 for k in ['parentOwnedGroupGone','allObservedOwnedGroupsGone']:need(t[k]is True,'actual '+k)
 for k in ['errors','signals','interruptedSignals','remainingObservedPids']:need(t[k]==[],'no '+k)
 need(len(t['finalGroups'])>0 and all(x['alive']is False and x['signalAllowed']is False for x in t['finalGroups']),'all recorded groups gone')
 need(t['stderr']['bytes']==0,'no stderr');verify(t['stdout']);verify(t['stderr'])
def save(name,value):
 p=P/name;need(not p.exists(),'new review file only');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def retained(name,r):
 raw=verify(r).read_bytes();q=P/'raw'/name;q.parent.mkdir(exist_ok=True);need(not q.exists()or q.read_bytes()==raw,'existing reviewer copy stays exact');q.write_bytes(raw)if not q.exists()else None;out=row(q);need((out['sha256'],out['bytes'])==(r['sha256'],r['bytes']),'whole raw bytes preserved');raw_copies.append(dict(original=r,copy=out))
root_result=dict(path=str(S/'combined-native355-artifact-v1-bootstrap-root-results.json'),sha256='e5a9448767f1c77e419066dbeef1a2b7361d4de52038989bb4e1e35a9718682c',bytes=7696)
r=read(root_result);need(r['state']=='ROOT_OBSERVED_COMBINED355_VALIDATION_BOOTSTRAP_ZERO_UNREVIEWED_V1'and r['toolObservation']['sessionId']==10796 and r['toolObservation']['rawExitCode']==0,'Root actual observed terminal')
ix=r['toolingIndex'];need(ix['sha256']=='c365e6089688f62f028580e86b14db80bb434ba7b4ac45ae341e851c11913a7b','genuine c365');members=family(ix);need(len(members)==31,'whole31 Source members');refs=load(C/'references.json');declared=load(C/'source-inputs.json')
for x in declared['files']:verify(x)
peer=proof(r['sourcePeer']);need(peer['toolingSourceIndexSha256']==ix['sha256']and peer['state']=='INDEPENDENT_COMBINED355_NATIVE_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V1'and peer['sourceOnly']is peer['sourceReviewPassed']is True,'genuine separate Source peer')
for k in ['ownerActionsInvoked','hostActionsInvoked','exportOrBootstrapActionsInvoked']:need(peer[k]is False,'Source-only peer')
frozen=contract(refs['actualFrozenReview'],refs['actualFrozenContract']);need(r['actualFrozenReview']==refs['actualFrozenReview'],'actual frozen proof bound')
exp=proof(r['independentExportReview']);need(exp['state']=='INDEPENDENT_COMBINED355_NORMAL_OFF_PIN_EXPORT_REVIEW_PASSED_V1'and exp['verifiedPassed']is True and exp['toolingSourceIndexSha256']==ix['sha256']and exp['candidate']==r['actualExportCandidate']and exp['actualFrozenReview']==refs['actualFrozenReview'],'genuine independent export result')
for k in ['engineExecuted','bootstrapExecuted','operationalAdmission','runtimeAcceptanceClaim']:need(exp[k]is False,'export bounded historical scope')
need(exp['rawExporterExitCode']==0 and exp['wholeCandidateAndRawJsonEqual']is exp['otherVariantsNull']is True,'complete genuine exported candidate')
compact=read(refs['compactInputBoundary']);ledger=read(refs['reviewedBuildInputLedger']);need(len(compact['files'])==2618 and len(ledger['files'])==20816 and compact['reviewedBuildInputLedger']==refs['reviewedBuildInputLedger']and compact['reviewedInheritedFamilies']==refs['inheritedFamilies']and compact['historicalTreesRecopied']is False,'fixed scoped reference boundaries')
for x in compact['files']+ledger['files']:verify(x)
for x in refs['inheritedFamilies']:family(x)
need(len(refs['inheritedFamilies'])==15,'fifteen inherited families')
inv=read(refs['frozenCopyInventory']);F=Path(refs['frozenRoot']);names={'normal-off-freeze-receipt.json'};inodes=set()
for x in inv['files']:
 a=verify(x['copy']).stat();n=Path(x['copy']['path']).relative_to(F).as_posix();need(n not in names and a.st_nlink==1 and stat.S_IMODE(a.st_mode)==0o600 and(a.st_dev,a.st_ino)not in inodes,'independent private frozen copy');names.add(n);inodes.add((a.st_dev,a.st_ino))
 if x['original']is not None:
  b=verify(x['original']).stat();need((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'original/copy separate inode')
need(len(inv['files'])==2596 and inv['wholeMembershipFiles']==len(names)==2597,'whole2596copies2597membership');exact_tree(F,names,private=True)
protection=read(refs['freezerProtection']);need(len(protection['files'])==20816 and len(protection['modePairs'])==1613,'actual original and stage pair boundaries')
for x in protection['files']:
 s=verify(x['descriptor']).stat();need(stat.S_IMODE(s.st_mode)==x['mode']and s.st_nlink==x['nlink'],'protected original mode/nlink')
for x in protection['modePairs']:
 a=verify(x['copy']).stat();b=verify(x['original']).stat();need(stat.S_IMODE(a.st_mode)==x['copyMode']and stat.S_IMODE(b.st_mode)==x['originalMode']and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'stage pair hash/modes/inode')
for t in protection['trees']:need(stat.S_IMODE(Path(t['root']).stat().st_mode)==t['mode'],'current protected root mode');exact_tree(t['root'],t['files'],t['links'])
aliases=read(refs['referenceAliasWitness'])
for x in aliases['symlinks']:need(Path(x['path']).is_symlink()and os.readlink(x['path'])==x['linkText']and str(Path(x['path']).resolve())==x['resolved'],'declared alias')
for x in aliases['archiveHardlinks']:need(os.path.samefile(x['path'],x['target'])and x['sameInode']is True,'declared archive hardlink')
need(refs['activeVerifier']in family(refs['freezerSourceIndex'])and refs['monitorEntry']in family(refs['monitorIndex']),'genuine original verifier/monitor contexts')
root=read(r['rootAuthority']);cfg=read(r['config']);invocation=read(r['invocation']);pinreview=read(r['rootPinReview'])
need(cfg==dict(schemaVersion=1,state='COMBINED355_NATIVE_ARTIFACT_CONFIG_V1',phase='bootstrap',toolingIndex=ix,rootAuthority=r['rootAuthority']),'exact actual CLI config')
need(root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_COMBINED355_NATIVE_ARTIFACT_PHASE_V1'and root['phase']=='bootstrap'and root['toolingIndex']==ix and root['sourceIndependentReview']==r['sourcePeer'],'issued actual bootstrap Root')
for k in ['actualFrozenReview','actualExportCandidate','independentExportReview','reviewedPins','rootPinReview']:need(root[k]==r[k],'Root direct role '+k)
for k in ['engine','metadata','freezeReceipt','nativeSourceIndex','freezerSourceIndex','configuredSourceRoot','frozenSourceRoot','workRoot']:need(root[k]==refs[k],'full original role '+k)
need(root['bootstrapAllowed']is root['frozenReadOnlyVerifierAllowed']is True and root['exportAllowed']is False and root['expectedFrozenVerifierCalls']==1 and root['externalParentDeadlineSeconds']==600 and root['actualBootstrapReview']is root['runtimeAuthority']is None,'exact narrow bootstrap grant')
for k in ['nativeBuildAllowed','nativeFreezeAllowed','ninjaAllowed','gcReconfigureAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','componentAllowed','sourcePromotionAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:need(root[k]is False,'no extra Root permission '+k)
base=Path(root['outputRoot']);external=Path(root['externalOutputRoot']);caller=Path(str(base)+'-root-caller')
need(str(base)=='/private/tmp/starling-node-compat/combined-native355-artifact-tooling-v1-bootstrap-normal-off'and external==Path(str(base)+'-external-root'),'genuine original phase roots')
phase_names={'bootstrap-frame.json','native-frame.json','whole-verifier-capsule.json','controller-observation.json','raw-terminal-observed.json'};exact_tree(base,phase_names,private=True)
outer=read(r['outerTerminal']);inner=read(r['externalTerminal']);clean(outer,r['rootAuthority'],50367);clean(inner,r['rootAuthority'],50636)
need(outer['stdout']==r['parentStdout']and outer['stderr']==r['parentStderr']and inner['stdout']==r['rawBootstrapStdout'],'actual complete stream descriptors')
need({x['pgid']for x in outer['finalGroups']}=={50367,50636}and{x['pgid']for x in inner['finalGroups']}=={50636},'exact owned groups')

def monitor_inventory(directory,terminal,extras):
 names={'terminal.json','stdout.log','stderr.log','started.json'}|set(extras)
 for n,process in enumerate(terminal['observedProcesses']):
  name='owned-'+str(n).zfill(4)+'.json';names.add(name);event=load(directory/name);need(event['sequence']==n and same(event['process'],process)and type(event['observationMonotonicSeconds'])in(int,float),'whole contiguous sampled ownership event');retained(directory.name+'-'+name,row(directory/name))
 exact_tree(directory,names);need(stat.S_IMODE(directory.stat().st_mode)==0o700,'private monitor directory');
 for name in names:
  mode=(directory/name).stat();need(stat.S_IMODE(mode.st_mode)in[0o600,0o644]and mode.st_nlink==1,'actual monitor regular file mode/nlink')
 return load(directory/'started.json')
outerstart=monitor_inventory(caller,outer,['environment-policy.json','root-child-return.json']);innerstart=monitor_inventory(external,inner,[])
need(outerstart['pid']==50367 and innerstart['pid']==50636 and outerstart['timeoutSeconds']==1200 and innerstart['timeoutSeconds']==600 and outerstart['authority']==innerstart['authority']==r['rootAuthority'],'both real launch records/deadlines')
for process in outer['observedProcesses'][2:]:need(process['ppid']==50367 and process['pgid']==50367 and process['command']in['(ps)','/bin/ps'],'additional sampled rows are monitor ps helpers, not native/guest jobs')

processes={x['pid']:x for x in outer['observedProcesses']};need(50367 in processes and 50636 in processes and processes[50636]['ppid']==50367 and processes[50636]['pgid']==50636,'actual parent-child ownership')
parent_records=[parse(x)for x in verify(r['parentStdout']).read_bytes().splitlines()];need(len(parent_records)==2 and parent_records[0]==dict(pid=50636,timeoutSeconds=600)and parent_records[1]==r['actualParentReturn']==dict(observation=r['controllerObservation'],completeUnreviewed=True),'whole two parent JSONL records')
need(load(caller/'root-child-return.json')==dict(schemaVersion=1,rawExitCode=0,terminal=r['outerTerminal']),'actual root monitor return')
environment=read(r['environmentPolicy']);need(environment['schemaVersion']==1 and environment['valuesRetained']is False and environment['keys']==['HOME','LOGNAME','PATH','PYTHONDONTWRITEBYTECODE','TMPDIR','USER'],'actual selected environment names')
verify(invocation['rootLauncher']);verify(invocation['python']);verify(invocation['entry']);need(invocation['rootAuthority']==r['rootAuthority']and invocation['rootConfig']==r['config']and invocation['sourcePeer']==r['sourcePeer']and invocation['toolingIndex']==ix and invocation['python']==refs['python']and invocation['entry']in members,'actual invocation/source identities')
argv=[refs['python']['path'],'-B','-I',str(C/'artifact_tooling.py'),'parent','bootstrap','--config-descriptor',json.dumps(r['config'],separators=(',',':'))];need(outerstart['argv']==argv and innerstart['argv']==[argv[0],'-B','-I',argv[3],'worker',*argv[5:]],'full actual parent/worker launch argv');need(invocation['actualArgv']==argv and invocation['ownedWorkerDeadlineSeconds']==600 and invocation['outerParentDeadlineSeconds']==1200 and invocation['engineOrGuestExecutionAllowed']is False,'real outer argv/paired deadlines')
observation=read(r['controllerObservation']);rawstatus=read(r['rawTerminalObservation']);need(rawstatus==dict(schemaVersion=1,terminal=r['externalTerminal'],stdout=inner['stdout'],stderr=inner['stderr'],interpretationPending=True),'durable raw status/streams before assertions')
expectedob=dict(schemaVersion=1,state='COMBINED355_ARTIFACT_PHASE_COMPLETE_UNREVIEWED_V1',phase='bootstrap',toolingIndex=ix,rootAuthority=r['rootAuthority'],config=r['config'],actualFrozenReview=refs['actualFrozenReview'],rawTerminal=r['externalTerminal'],rawExitCode=0,completePhaseReturn=r['bootstrapFrame'],nativeFrame=r['nativeFrame'],verifierCapsule=r['verifierCapsule'],sourceAndOriginalProtectionRechecked=True,errors=[],requiresIndependentActualReview=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
need(same(observation,expectedob),'whole controller result, final Source guard outcome')
frame=read(r['bootstrapFrame']);native=read(r['nativeFrame']);capsule=read(r['verifierCapsule']);metadata=read(refs['metadata']);receipt=read(refs['freezeReceipt']);candidate=read(r['actualExportCandidate']);pins=read(r['reviewedPins'])
need(same(frame,read(inner['stdout'])),'WHOLE pretty frame equals compact raw JSON, no trimming/subsetting')
need(native==read(exp['nativeFrame'])and capsule==read(exp['verifierCapsule'])and capsule==read(refs['historicalVerifierCapsule']),'actual native/capsule whole equality with export and historical verifier')
need(capsule['state']=='COMBINED355_NORMAL_FREEZE_READ_ONLY_CAPSULE_VERIFIED_NOT_ACCEPTED_V1'and capsule['receipt']==refs['freezeReceipt']and capsule['engine']==refs['engine']and capsule['metadata']==refs['metadata'],'unchanged NOT_ACCEPTED capsule')
need(len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==11,'full80/native355+3/11')
manifests=[]
for x in metadata['selectedModuleManifests']:
 p=Path(refs['frozenSourceRoot'])/x['path'];d=row(p);need(d['sha256']==x['sha256'],'whole selected manifest SHA');manifests.append(read(d))
expectednative=dict(schemaVersion=1,state='COMBINED355_FROZEN_FULL80_NATIVE_DATA_VERIFIED_NO_ACTION_AUTHORITY_V1',variant='normal-off',toolingIndex=ix,nativeSourceIndex=refs['nativeSourceIndex'],retryBuildControllerIndex=refs['retryBuildControllerIndex'],freezerSourceIndex=refs['freezerSourceIndex'],activeVerifier=refs['activeVerifier'],actualFrozenReview=refs['actualFrozenReview'],verificationCapsule=capsule,engine=refs['engine'],enginePath=refs['engine']['path'],metadataDescriptor=refs['metadata'],metadata=metadata,freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=80,selectedManifestPaths=[x['path']for x in metadata['selectedModuleManifests']],selectedManifests=manifests,configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],sourceRoot=refs['frozenSourceRoot'],frozenRoot=refs['frozenRoot'],componentizeSourceRoot=refs['componentizeSourceRoot'],rawMetadataPathsPreserved=True,privateRustupBootstrapPolicy=metadata['privateRustupBootstrapPolicy'],historical57SettingBytesSeparatelyRetained=False,verifiedOriginalReferencesNotAllPhysicallyCopied=True,runtimeBackendProof=receipt['runtimeBackendProof'],remaining15DeviationsApproved=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsActionAuthority=False)
need(same(native,expectednative),'every field of native frame independently rebuilt from actual retained DATA')
need(metadata['enginePath']!=native['enginePath']and metadata['combinedNativeSourcePolicy']['workRoot']==refs['workRoot']and receipt['rawMetadataBytesUnchanged']is receipt['rawMetadataOriginalConfiguredPathsPreserved']is True,'original metadata physical paths retained, no role projection')
need(metadata['gcStress']is metadata['oomTesting']is False and metadata['entropyPolicy']=='off'and metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE']=='Release','real normal Release OFF')
need(native['runtimeBackendProof']==dict(verified=False,version=None,vernum=None)and metadata['zlibErrorSemanticsPolicy']['remainingRecordedDifferences']==15 and metadata['zlibErrorSemanticsPolicy']['remainingDeviationsApproved']is False,'remaining native/backend limits not relabeled')
need(metadata['privateRustupBootstrapPolicy']['settingsAtBuildCompletion']['bytes']==107 and receipt['historicalPreinstallSettingsRawBytesSeparatelyRetained']is False,'actual107 settings vs historical unretained57 DATA')
expectedpin=dict(schemaVersion=1,state='unreviewed-combined355-normal-off-pin-v1',reviewRequired=True,variant='normal-off',toolingIndex=ix,nativeFrame=native,engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=80,frozenFiles=[{k:x[k]for k in ['path','sha256','bytes']}for x in receipt['copies']],actualFrozenReview=refs['actualFrozenReview'],validationBootstrapOnly=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
expectedcandidate=dict(schemaVersion=1,state='UNREVIEWED_COMBINED355_NORMAL_OFF_PIN_CANDIDATE_V1',toolingIndex=ix,reviewRequired=True,variants={k:copy.deepcopy(expectedpin)if k=='normal-off'else None for k in ['normal-off','normal-runtime','gc-off','disabled-off']},validationBootstrapOnly=True,operationalAdmission=False,runtimeAcceptanceClaim=False)
need(same(candidate,expectedcandidate),'whole original UNREVIEWED candidate independently reconstructed')
reviewed=copy.deepcopy(candidate);reviewed['state']='ROOT_REVIEWED_COMBINED355_NORMAL_OFF_VALIDATION_PINS_V1';reviewed['reviewRequired']=False;reviewed['variants']['normal-off']['state']='reviewed-combined355-normal-off-pin-v1';reviewed['variants']['normal-off']['reviewRequired']=False
need(same(reviewed,pins),'only exact four reviewed state/flag changes, ALL other fields unchanged')
expectedreview=dict(schemaVersion=1,state='ROOT_COMBINED355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V1',toolingIndex=ix,reviewedPins=r['reviewedPins'],actualExportCandidate=r['actualExportCandidate'],independentExportReview=r['independentExportReview'],actualFrozenReview=refs['actualFrozenReview'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=80,validationBootstrapOnly=True,otherVariantsNull=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False,changedPaths=['state','reviewRequired','variants.normal-off.state','variants.normal-off.reviewRequired'],allOtherCandidateFieldsUnchanged=True)
need(same(pinreview,expectedreview),'whole exact new Root validation pin review')
expectedframe=dict(schemaVersion=1,state='COMBINED355_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V1',variant='normal-off',toolingIndex=ix,rootAuthority=r['rootAuthority'],config=r['config'],nativeFrame=native,pin=pins['variants']['normal-off'],engine=refs['engine'],enginePath=refs['engine']['path'],metadataDescriptor=refs['metadata'],metadata=metadata,freezeReceipt=refs['freezeReceipt'],nativeSourceIndex=refs['nativeSourceIndex'],retryBuildControllerIndex=refs['retryBuildControllerIndex'],freezerSourceIndex=refs['freezerSourceIndex'],actualFrozenReview=refs['actualFrozenReview'],actualExportCandidate=r['actualExportCandidate'],independentExportReview=r['independentExportReview'],reviewedPins=r['reviewedPins'],rootPinReview=r['rootPinReview'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=80,selectedManifestPaths=native['selectedManifestPaths'],selectedManifests=manifests,configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],sourceRoot=refs['frozenSourceRoot'],componentizeSourceRoot=refs['componentizeSourceRoot'],frozenRoot=refs['frozenRoot'],originalToolingRoot=refs['originalToolingRoot'],currentFrozenVerifierCalls=1,validationBootstrapOnly=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsRuntimeAuthority=False)
need(same(frame,expectedframe)and len(frame)==40,'every bootstrap DATA field independently rebuilt, no operational model invoked')
# Static evidence explains actual tool-controlled scope; it is not another call.
py=verify(invocation['entry']).read_text();launcher=verify(invocation['rootLauncher']).read_text();vtext=verify(refs['activeVerifier']).read_text();pt=ast.parse(py);ast.parse(launcher);ast.parse(vtext)
worker=next(n for n in pt.body if isinstance(n,ast.FunctionDef)and n.name=='worker');calls=[n for n in ast.walk(worker)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='verify_frozen'];need(len(calls)==1 and len(calls[0].args)==2,'one source-coupled actual verifier invocation, no call-counter proof')
need("Path(helper.__file__).resolve()==Path(f['refs']['activeVerifier']['path'])"in py and "helper.FREEZE==Path(f['refs']['frozenRoot'])"in py and 'helper.HERE'not in py and 'helper.FROZEN'not in py,'genuine original verifier self-auth context, no rebinding')
need(py.index("write(out/'raw-terminal-observed.json'")<py.index("clean_terminal(terminal,f['rootRow'])")<py.index("value=json.loads(Path(terminal['stdout']['path']).read_bytes())"),'raw full stream/terminal retention before clean/parse')
need('finally:f[\'capture\'].recheck()'in py and 'finally:c.recheck()'in py and 'sourceAndOriginalProtectionRechecked=protected'in py,'actual Source-controlled initial/final/failure protection')
need("env={k:os.environ[k] for k in ['HOME','USER','LOGNAME','TMPDIR'] if k in os.environ}"in launcher and "PATH='/usr/bin:/bin:/usr/sbin:/sbin',PYTHONDONTWRITEBYTECODE='1'"in launcher,'selected environment recipe, home copied unchanged; values not attested')
for k in ['bootstrapFrame','nativeFrame','verifierCapsule','controllerObservation','rawTerminalObservation','rootAuthority','config','invocation','rootPinReview','parentStdout','parentStderr','environmentPolicy','outerTerminal','externalTerminal']:
 retained(k+'.json'if k not in ['parentStdout','parentStderr']else k+'.log',r[k])
retained('rawBootstrapStdout.log',r['rawBootstrapStdout']);retained('rawBootstrapStderr.log',inner['stderr']);retained('root-results.json',root_result);retained('outer-started.json',row(caller/'started.json'));retained('inner-started.json',row(external/'started.json'));retained('root-child-return.json',row(caller/'root-child-return.json'))
# Final DATA rehash records current stability, distinct from owner-time bookends.
for path,expected in list(seen.items()):
 p=Path(path);need(identity(p)==identities[path],'all current input identities stable');h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 need(h.hexdigest()==expected['sha256'],'all current bytes stable at final reader boundary')
for t in protection['trees']:exact_tree(t['root'],t['files'],t['links'])
exact_tree(base,phase_names,private=True);exact_tree(F,names,private=True)
coverage=dict(toolingSourceMembers=31,producerOutputFiles=5,rawBootstrapStrings=1,bootstrapFields=40,fullMetadataFields=80,nativeSourceFiles=355,externalEmbeddingSources=3,selectedWholeManifests=11,frozenCopies=2596,frozenMembershipFiles=2597,compactRows=2618,expandedBuildRows=20816,inheritedFamilies=15,stagedOriginalPairs=1613,originalAliases=len(aliases['symlinks']),originalArchiveHardlinks=len(aliases['archiveHardlinks']),compileDatabaseRows=68,policyCppCommands=62,otherConfiguredCommands=5,generatedNullCommands=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=6,outerParentJsonlRecords=2,outerOwnershipRecords=len(outer['observedProcesses']),innerOwnershipRecords=len(inner['observedProcesses']),sourceCoupledVerifierCalls=1,actualRawTextCopies=len(raw_copies),currentUniqueReferences=len(seen))
fixed=dict(schemaVersion=1,verifiedPassed=True,toolingSourceIndexSha256=ix['sha256'],nativeSourceFiles=355,externalEmbeddingSources=3,fullMetadataFields=80,selectedManifestCount=11,rawBootstrapExitCode=0,rawParentExitCode=0,allObservedOwnedGroupsGone=True,wholeFrameMatchesRawStdout=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
direct={k:r[k]for k in ['bootstrapFrame','nativeFrame','verifierCapsule','actualFrozenReview','rootAuthority','config','controllerObservation','externalTerminal','reviewedPins','rootPinReview','actualExportCandidate','independentExportReview']};direct.update(toolingIndex=ix,sourcePeer=r['sourcePeer'],rootObservation=root_result,outerTerminal=r['outerTerminal'],invocation=r['invocation'],rawBootstrapStdout=r['rawBootstrapStdout'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceIndex=refs['nativeSourceIndex'],freezerSourceIndex=refs['freezerSourceIndex'])
limits=['Independent READ/HASH/DATA review only. Reader did not import/invoke owner model/helper/verifier/monitor/API, tool, export/bootstrap phase, engine, component, guest or key workload. No new pin/output transition performed by reader.','Actual owner bootstrap called the original5230 frozen verifier once by reviewed Source control flow, preserving real __file__ self-auth outside frozen payload; not an independently instrumented call count or all-reads-frozen assertion. It was not the retained read-only JS API.','Complete raw bootstrap JSON equals the whole40-field pretty frame. Native frame retains all80 metadata fields and355+3 sources/all11 whole manifests, original configured/work/frozen paths and unchanged NOT_ACCEPTED capsule.','All four documented reviewed state/flag changes only; three other variants remain NULL. These are validation-only pins, not normal production adoption or engine/runtime authority.','Actual-time original/source protection is evidenced by reviewed Source control flow and clean controller outcome; current reviewer rehash/modes/inodes/membership checks are a later independent boundary, not a separate owner-time attestation.','107-byte current private Rustup settings are retained; historical nested57-byte preinstall digest remains historical DATA with no separately retained raw57 claim. Backend proof false/null/null and15 zlib deviations remain unapproved.','Root tool raw0 is a reported exec terminal, not another process log. Outer/inner durable raw0 groups/streams were independently checked. Selected environment names/recipe are retained; complete original environment values are not independently attested.','No retained read-only API result, component construction/admission, runtime correctness, GC/free/wipe/isolated-root/reset/ALS/host reuse/performance or security-completion claim follows.']
save('boundary-review.json',dict(schemaVersion=1,coverage=coverage,compactInputBoundary=refs['compactInputBoundary'],expandedBuildInputLedger=refs['reviewedBuildInputLedger'],inheritedFamilies=refs['inheritedFamilies'],frozenCopyInventory=refs['frozenCopyInventory'],freezerProtection=refs['freezerProtection'],referenceAliasWitness=refs['referenceAliasWitness'],currentProtectionRehashed=True,historicalTreesRecopied=False,actualTimeProtectionEvidence='Reviewed Source control flow plus actual clean outcome; no separate per-read ledger at operation time'))
save('raw-copies.json',dict(schemaVersion=1,files=raw_copies,allWholeBytesPreserved=True))
state='INDEPENDENT_COMBINED355_NORMAL_OFF_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1'
save('results.json',dict(**fixed,state=state,**direct,coverage=coverage,readOnlyDataReview=True,checks=checks,wholeBootstrapFrameReconstructedIndependently=True,wholeNativeFrameReconstructedIndependently=True,exactPinChangedPaths=pinreview['changedPaths'],otherVariantsNull=True,producerIndexOrCompletionExists=False,observedOwnerFrozenVerifierInvoked=True,ownerRetainedJsApiInvoked=False,reviewerOperationalActionsInvoked=False,ownerActionsInvoked=False,hostActionsInvoked=False,reviewerHelperVerifierMonitorApiOrModelInvoked=False,actualReadOnlyResult=None,componentAuthority=None,runtimeAuthority=None,materialFindings=[],limitations=limits))
save('result-contract.json',dict(schemaVersion=1,requiredReviewState=state,requiredFixedValues=fixed,requiredExactDescriptors=direct,requiredCoverage=coverage,issuesActionOrRuntimeAuthority=False))
(P/'README.md').write_text('Independent actual combined355 validation bootstrap DATA review\n\nBounded PASS: whole actual raw frame, native/full80/355+3/11 values, exact four pin-state/flag changes, process cleanup and fixed current protection verified. No owner function or tool invoked by reviewer.\n\n'+'\n\n'.join(limits)+'\n')
save('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_COMBINED355_NATIVE_BOOTSTRAP_DATA_REVIEW_V1',result=row(P/'results.json'),contract=row(P/'result-contract.json'),rootObservation=root_result,allOriginalBytesPreserved=True,reviewerOperationalActions=False))
files=[]
for q in sorted(P.rglob('*')):
 if q.is_file():d=row(q);files.append(dict(d,path=q.relative_to(P).as_posix()))
save('index.json',dict(schemaVersion=1,files=files))
for n in ['index.json','results.json','result-contract.json','receipt.json']:print(json.dumps(row(P/n)))
print(json.dumps(dict(sealed=True,members=len(files),checks=checks,coverage=coverage,reviewerActions=False)))
