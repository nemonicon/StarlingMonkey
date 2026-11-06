"""Independent completed export DATA review; no verifier/model/API/phase execution."""
from pathlib import Path
import hashlib,json,os,stat,sys,time
OWN=Path(__file__).resolve().parent;S=OWN.parent
SOURCE=S/'combined-native-artifact-tooling-candidate-v1'
OUTPUT=Path('/private/tmp/starling-node-compat/combined-native355-artifact-tooling-v1-export-normal-off')
INNER=Path(str(OUTPUT)+'-external-root');OUTER=Path(str(OUTPUT)+'-root-caller')
ROOT_SHA='7f121aeddf233184db1b044dc84526751ed96799d9dad35a36b853c0914b8fbd'
captured={};identities={};families={};checks=0
def need(v,label):
 global checks
 assert v,label
 checks+=1
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def physical(p):return Path('/private'+p)if p.startswith('/tmp/')else Path(p)
def sig(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode),s.st_nlink)
def verify(r):
 need(type(r)is dict and set(r)=={'path','sha256','bytes'},'exact descriptor')
 p=physical(r['path']);need(p.is_absolute()and str(p)==os.path.normpath(str(p)),'canonical original path')
 for q in(p,*p.parents):need(not q.is_symlink(),'ordinary canonical reference')
 a=p.stat();need(stat.S_ISREG(a.st_mode)and a.st_size==r['bytes'],'regular exact-size reference')
 if r['path']in captured:need(captured[r['path']]==r and identities[r['path']]==sig(a),'stable repeated original');return p
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 need(sig(a)==sig(p.stat())and h.hexdigest()==r['sha256'],'stable whole reference SHA');captured[r['path']]=dict(r);identities[r['path']]=sig(a);return p
def data(r):return json.loads(verify(r).read_bytes())
def family(r):
 value=data(r);base=Path(r['path']).parent;names={'index.json'};rows=[r]
 for item in value['files']:
  name=item['path'];need(name not in names and not name.startswith('/')and '\\'not in name and all(p not in('','.','..')for p in name.split('/')),'unique confined member');names.add(name);row=dict(item,path=str(base/name));verify(row);rows.append(row)
 need(not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names,'complete exact family');families[r['path']]=r;return rows
def tree(row):
 root=Path(row['root']);need(root.is_dir()and not root.is_symlink()and stat.S_IMODE(root.stat().st_mode)==row['mode'],'protected actual root')
 files=set();links={}
 for p in root.rglob('*'):
  name=p.relative_to(root).as_posix()
  if p.is_symlink():links[name]=os.readlink(p)
  elif p.is_file():files.add(name)
 need(files==set(row['files'])and links==row['links'],'protected exact original membership/declared links')
def terminal(t,authority):
 need(type(t['rawExitCode'])is int and t['rawExitCode']==0 and t['authority']==authority,'raw0/exact authority')
 need(t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True and t['timeout']is t['forcedCleanup']is False,'both groups clean/no timeout/force')
 need(all(t[k]==[]for k in('errors','signals','remainingObservedPids','interruptedSignals'))and t['finalGroups']and all(g['alive']is False for g in t['finalGroups']),'complete no-signal final groups')
 need(verify(t['stderr']).read_bytes()==b'','empty full stderr');verify(t['stdout'])
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 start=time.monotonic();need(OWN.name=='independent-combined355-native-pin-export-results-review-v1'and OWN==Path(__file__).resolve().parent,'genuine actual reader context')
 rootrow=desc(S/'combined-native355-artifact-v1-export-root-results.json');need(rootrow['sha256']==ROOT_SHA and rootrow['bytes']==5676,'actual Root terminal handoff');root=data(rootrow)
 need(root['toolObservation']==dict(sessionId=40725,rawExitCode=0,kind='Actual exec-command terminal observation'),'Root raw0 tool evidence, no fabricated process log')
 ownrows=family(root['toolingIndex']);peerrows=family(root['sourcePeer']['index']);need(root['sourcePeer']['result']in peerrows,'Source peer result indexed')
 peer=data(root['sourcePeer']['result']);need(peer['sourceReviewPassed']is True and peer['toolingSourceIndexSha256']==root['toolingIndex']['sha256'],'exact independently reviewed Sourcec365')
 refs=data(next(r for r in ownrows if r['path']==str(SOURCE/'references.json')));inputs=data(next(r for r in ownrows if r['path']==str(SOURCE/'source-inputs.json')))
 for r in inputs['files']:verify(r)
 frozen_rows=family(refs['actualFrozenReview']['index']);need(refs['actualFrozenReview']['result']in frozen_rows and refs['actualFrozenContract']in frozen_rows,'genuine frozen proof/contract indexed')
 frozen=data(refs['actualFrozenReview']['result']);fc=data(refs['actualFrozenContract'])
 for group in('requiredFixedValues','requiredExactDescriptors'):
  for k,v in fc[group].items():need(frozen[k]==v,'whole frozen contract '+k)
 need(frozen['coverage']==fc['requiredCoverage'],'full frozen coverage')
 compact=data(refs['compactInputBoundary']);ledger=data(refs['reviewedBuildInputLedger']);need(len(compact['files'])==2618 and len(ledger['files'])==20816 and len(refs['inheritedFamilies'])==15,'fixed declared provenance, no recursive expansion')
 for r in compact['files']+ledger['files']:verify(r)
 for r in refs['inheritedFamilies']:family(r)
 protection=data(refs['freezerProtection'])
 for r in protection['files']:
  s=verify(r['descriptor']).stat();need(stat.S_IMODE(s.st_mode)==r['mode']and s.st_nlink==r['nlink'],'every original mode/link count')
 for r in protection['modePairs']:
  a,b=verify(r['copy']).stat(),verify(r['original']).stat();need(stat.S_IMODE(a.st_mode)==r['copyMode']and stat.S_IMODE(b.st_mode)==r['originalMode']and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'1613 staged original-copy relationships')
 for r in protection['trees']:tree(r)
 aliases=data(refs['referenceAliasWitness']);need(len(aliases['symlinks'])==31 and len(aliases['archiveHardlinks'])==1,'declared aliases/hardlink count')
 for r in aliases['symlinks']:
  p=Path(r['path']);need(p.is_symlink()and os.readlink(p)==r['linkText']and str(p.resolve())==r['resolved'],'literal SDK alias')
 for r in aliases['archiveHardlinks']:
  a,b=Path(r['path']).stat(),Path(r['target']).stat();need((a.st_dev,a.st_ino)==(b.st_dev,b.st_ino)and r['sameInode']is True,'original archive hardlink')
 receipt=data(refs['freezeReceipt']);metadata=data(refs['metadata']);inventory=data(refs['frozenCopyInventory']);need(len(receipt['copies'])==len(inventory['files'])==2596 and inventory['wholeMembershipFiles']==2597,'full frozen2596/2597')
 expected_frozen={Path(refs['freezeReceipt']['path']).name};frozen_inodes=set()
 for r in inventory['files']:
  p=verify(r['copy']);name=p.relative_to(refs['frozenRoot']).as_posix();need(name not in expected_frozen,'unique frozen row');expected_frozen.add(name);s=p.stat();ident=(s.st_dev,s.st_ino);need(s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and ident not in frozen_inodes,'independent frozen regular private file');frozen_inodes.add(ident)
  if r['original']is not None:
   a=verify(r['original']).stat();need(ident!=(a.st_dev,a.st_ino),'frozen/original independent inode')
 frozendirs=Path(refs['frozenRoot']);need(not any(p.is_symlink()for p in frozendirs.rglob('*'))and{p.relative_to(frozendirs).as_posix()for p in frozendirs.rglob('*')if p.is_file()}==expected_frozen,'complete frozen membership')
 candidate=data(root['candidate']);frame=data(root['nativeFrame']);capsule=data(root['verifierCapsule']);old_capsule=data(refs['historicalVerifierCapsule'])
 need(capsule==old_capsule and capsule['state']=='COMBINED355_NORMAL_FREEZE_READ_ONLY_CAPSULE_VERIFIED_NOT_ACCEPTED_V1'and capsule['copies']==2596,'full genuine verifier capsule retains NOT_ACCEPTED')
 manifests=[]
 for r in metadata['selectedModuleManifests']:
  p=Path(refs['frozenSourceRoot'])/r['path'];v=data(dict(path=str(p),sha256=r['sha256'],bytes=p.stat().st_size));need(type(v['modules'])is dict and v['profileVersion']==r['profileVersion'],'whole manifest value/profile');manifests.append(v)
 need(len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(manifests)==11,'full80/355/3/11 raw context')
 expected_frame=dict(schemaVersion=1,state='COMBINED355_FROZEN_FULL80_NATIVE_DATA_VERIFIED_NO_ACTION_AUTHORITY_V1',variant='normal-off',toolingIndex=root['toolingIndex'],nativeSourceIndex=refs['nativeSourceIndex'],retryBuildControllerIndex=refs['retryBuildControllerIndex'],freezerSourceIndex=refs['freezerSourceIndex'],activeVerifier=refs['activeVerifier'],actualFrozenReview=refs['actualFrozenReview'],verificationCapsule=capsule,engine=refs['engine'],enginePath=refs['engine']['path'],metadataDescriptor=refs['metadata'],metadata=metadata,freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=80,selectedManifestPaths=[r['path']for r in metadata['selectedModuleManifests']],selectedManifests=manifests,configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],sourceRoot=refs['frozenSourceRoot'],frozenRoot=refs['frozenRoot'],componentizeSourceRoot=refs['componentizeSourceRoot'],rawMetadataPathsPreserved=True,privateRustupBootstrapPolicy=metadata['privateRustupBootstrapPolicy'],historical57SettingBytesSeparatelyRetained=False,verifiedOriginalReferencesNotAllPhysicallyCopied=True,runtimeBackendProof=receipt['runtimeBackendProof'],remaining15DeviationsApproved=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsActionAuthority=False)
 need(frame==expected_frame,'every complete native-frame field reconstructed from actual frozen DATA')
 expected_pin=dict(schemaVersion=1,state='unreviewed-combined355-normal-off-pin-v1',reviewRequired=True,variant='normal-off',toolingIndex=root['toolingIndex'],nativeFrame=frame,engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=80,frozenFiles=[{k:r[k]for k in('path','sha256','bytes')}for r in receipt['copies']],actualFrozenReview=refs['actualFrozenReview'],validationBootstrapOnly=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
 expected_candidate=dict(schemaVersion=1,state='UNREVIEWED_COMBINED355_NORMAL_OFF_PIN_CANDIDATE_V1',toolingIndex=root['toolingIndex'],reviewRequired=True,variants={k:expected_pin if k=='normal-off'else None for k in('normal-off','normal-runtime','gc-off','disabled-off')},validationBootstrapOnly=True,operationalAdmission=False,runtimeAcceptanceClaim=False)
 need(candidate==expected_candidate,'whole candidate every field/2596 rows/only normal-off, no state projection')
 need(metadata['enginePath']!=frame['enginePath']and metadata['enginePath'].startswith(refs['workRoot']+'/')and frame['enginePath'].startswith(refs['frozenRoot']+'/'),'original raw enginePath preserved separately from frozen engine')
 observation=data(root['controllerObservation']);rawobs=data(root['rawTerminalObservation']);authority=data(root['rootAuthority']);config=data(root['config']);invocation=data(root['invocation']);verify(invocation['rootLauncher'])
 need(authority['phase']=='export'and authority['toolingIndex']==config['toolingIndex']==root['toolingIndex']and config['rootAuthority']==root['rootAuthority']and authority['sourceIndependentReview']==root['sourcePeer'],'actual Root/Source/phase roles')
 need(authority['exportAllowed']is authority['frozenReadOnlyVerifierAllowed']is True and authority['bootstrapAllowed']is authority['engineExecutionAllowed']is authority['guestAllowed']is authority['operationalAdmission']is False,'export+verifier only')
 inner=data(root['externalTerminal']);outer=data(root['outerTerminal']);terminal(inner,root['rootAuthority']);terminal(outer,root['rootAuthority'])
 inner_start=data(desc(INNER/'started.json'));outer_start=data(desc(OUTER/'started.json'));cfgarg=json.dumps(root['config'],separators=(',',':'))
 base=[refs['python']['path'],'-B','-I',str(SOURCE/'artifact_tooling.py')]
 need(outer_start['argv']==base+['parent','export','--config-descriptor',cfgarg]==invocation['actualArgv']and inner_start['argv']==base+['worker','export','--config-descriptor',cfgarg],'genuine parent/worker literal argv')
 need(outer_start['pid']==outer['pid']==46729 and inner_start['pid']==inner['pid']==47096 and outer_start['timeoutSeconds']==1200 and inner_start['timeoutSeconds']==600,'actual PIDs/deadlines from records')
 parent_lines=[json.loads(line)for line in verify(root['parentStdout']).read_text().splitlines()];need(parent_lines==[root['monitorLaunch'],root['actualParentReturn']]and parent_lines[0]==dict(pid=inner['pid'],timeoutSeconds=600),'whole launch+observation parent JSONL')
 need(verify(root['parentStderr']).read_bytes()==b'','complete empty parent stderr');raw_stdout=verify(root['rawCandidateStdout']).read_bytes();need(root['rawCandidateStdout']==inner['stdout']and json.loads(raw_stdout)==candidate,'whole raw compact candidate JSON equals full pretty file value')
 need(observation['phase']=='export'and observation['state']=='COMBINED355_ARTIFACT_PHASE_COMPLETE_UNREVIEWED_V1'and observation['toolingIndex']==root['toolingIndex']and observation['rootAuthority']==root['rootAuthority']and observation['config']==root['config']and observation['actualFrozenReview']==refs['actualFrozenReview'],'actual controller provenance')
 for key in('completePhaseReturn','nativeFrame','verifierCapsule','rawTerminal'):need(observation[key]==root[{'completePhaseReturn':'candidate','nativeFrame':'nativeFrame','verifierCapsule':'verifierCapsule','rawTerminal':'externalTerminal'}[key]],'actual observation descriptor '+key)
 need(observation['rawExitCode']==0 and observation['sourceAndOriginalProtectionRechecked']is True and observation['errors']==[],'observed successful final protection')
 need(rawobs==dict(schemaVersion=1,terminal=root['externalTerminal'],stdout=inner['stdout'],stderr=inner['stderr'],interpretationPending=True),'raw terminal retention before interpretation')
 need(inner['pid']in{p['pid']for p in outer['observedProcesses']}and next(p for p in inner['observedProcesses']if p['pid']==inner['pid'])['ppid']==outer['pid'],'worker ownership joins')
 commands={p['command']for p in outer['observedProcesses']};need(commands=={'(ps)','/bin/ps','/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python'},'sampled Python and monitor ps helpers, no sampled engine command')
 output_names={'whole-verifier-capsule.json','native-frame.json','candidate-UNREVIEWED.json','raw-terminal-observed.json','controller-observation.json'};need({p.name for p in OUTPUT.iterdir()}==output_names,'exact five producer files; no producer index/completion')
 copies=[]
 for lane,basepath in [('actual',OUTPUT),('inner-monitor',INNER),('outer-monitor',OUTER)]:
  need(basepath.is_dir()and not basepath.is_symlink()and stat.S_IMODE(basepath.stat().st_mode)==0o700,'private actual root')
  for p in sorted(basepath.rglob('*')):
   need(not p.is_symlink(),'actual evidence no symlinks')
   if not p.is_file():continue
   r=desc(p);verify(r);target=OWN/'evidence'/lane/p.relative_to(basepath);target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb')as f:f.write(verify(r).read_bytes());f.flush();os.fsync(f.fileno())
   os.chmod(target,0o600);need(desc(target)['sha256']==r['sha256'],'exact actual text evidence copy');copies.append(dict(original=r,copy=desc(target)))
 for name,r in [('root-results',rootrow),('authority',root['rootAuthority']),('config',root['config']),('invocation',root['invocation'])]:
  target=OWN/'evidence'/(name+'.json')
  with target.open('xb')as f:f.write(verify(r).read_bytes());f.flush();os.fsync(f.fileno())
  os.chmod(target,0o600);copies.append(dict(original=r,copy=desc(target)))
 for path in captured:need(identities[path]==sig(physical(path).stat()),'all fixed current references stable at completion')
 for r in ownrows:need(desc(Path(r['path']))==r,'Sourcec365 unchanged at completion')
 save('raw-copy-map.json',dict(schemaVersion=1,copies=copies,onlyActualPhaseTextCopied=True,inheritedTreesCopied=False))
 save('checks.json',dict(schemaVersion=1,passed=True,checks=checks,currentUniqueReferences=len(captured),currentLogicalBytes=sum(r['bytes']for r in captured.values()),fixedCompactRows=2618,fixedBuildOriginalRows=20816,inheritedFamilies=15,allAuthenticatedFamilies=len(families),frozenCopies=2596,frozenMembership=2597,stagedCopyOriginalPairs=len(protection['modePairs']),originalReferenceAliases=31,originalArchiveHardlinks=1,metadataFields=80,nativeSources=355,externalSources=3,wholeManifests=11,producerFiles=5,producerIndexOrCompletion=False,actualRawTextCopies=len(copies),sourceParentPid=outer['pid'],workerPid=inner['pid'],outerObservedProcesses=len(outer['observedProcesses']),outerOwnedGroups=len(outer['finalGroups']),innerOwnedGroups=len(inner['finalGroups']),rawWorkerBytes=len(raw_stdout),prettyCandidateBytes=root['candidate']['bytes'],wholeParsedJsonEqual=True,rawAndPrettyBytesClaimedIdentical=False,allCurrentReferencesStable=True,verifierCallsEvidence='Exactly one worker source call plus retained whole return and clean raw0; not an independent function-call trace',actualTimeProtectionEvidence='Authenticated Source final control flow+raw0 and independent current fixed-boundary hashes; no per-read historical snapshots',ownerActionsInvoked=False,hostActionsInvoked=False,verifierOrApiOrPhaseOrEngineInvoked=False,elapsedReadSeconds=time.monotonic()-start))
 save('references.json',dict(schemaVersion=1,rootResult=rootrow,toolingIndex=root['toolingIndex'],sourcePeer=root['sourcePeer'],rootAuthority=root['rootAuthority'],config=root['config'],invocation=root['invocation'],candidate=root['candidate'],nativeFrame=root['nativeFrame'],verifierCapsule=root['verifierCapsule'],controllerObservation=root['controllerObservation'],externalTerminal=root['externalTerminal'],outerTerminal=root['outerTerminal'],rawCandidateStdout=root['rawCandidateStdout'],parentStdout=root['parentStdout'],parentStderr=root['parentStderr'],actualFrozenReview=refs['actualFrozenReview'],actualFrozenContract=refs['actualFrozenContract'],freezeReceipt=refs['freezeReceipt'],engine=refs['engine'],metadata=refs['metadata'],nativeSourceIndex=refs['nativeSourceIndex'],retryBuildControllerIndex=refs['retryBuildControllerIndex'],freezerSourceIndex=refs['freezerSourceIndex'],activeVerifier=refs['activeVerifier'],futureExportReviewContract=desc(SOURCE/'future-export-review-contract.json'),compactBoundary=refs['compactInputBoundary'],buildOriginalLedger=refs['reviewedBuildInputLedger'],frozenCopyInventory=refs['frozenCopyInventory']))
 print(json.dumps(dict(passed=True,checks=checks,references=len(captured),rawCopies=len(copies),actions=False)),flush=True)
if __name__=='__main__':
 assert sys.dont_write_bytecode
 try:main()
 except BaseException as error:save('reader-failure-'+str(time.time_ns())+'.json',dict(schemaVersion=1,name=type(error).__name__,message=str(error),checksCompleted=checks,actionsInvoked=False));raise
