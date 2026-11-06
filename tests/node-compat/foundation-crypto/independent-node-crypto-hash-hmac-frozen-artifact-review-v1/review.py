"""Independent actual freeze DATA reader. Never imports a freezer/verify action."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,posixpath,shlex,stat,sys,time
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
K=OWN.parent
FREEZE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-freeze')
SOURCE=K/'node-crypto-hash-hmac-freezer-candidate-v1'
checks=[];seen={};ids={};families={}
def ok(n,v):assert v,n;checks.append(n)
def physical(path):
 p=Path(path);assert p.is_absolute()and '..'not in p.parts
 if path.startswith('/tmp/'):
  assert path in ['/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/classic-streams-admission.mjs','/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/zlib-admission.mjs']
  assert os.readlink('/tmp')=='private/tmp'and str(Path('/tmp').resolve())=='/private/tmp';p=Path('/private'+path)
 for q in(p,*p.parents):assert not q.is_symlink(),q
 return p
def identity(p):
 s=p.stat();return(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def desc(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def checked(d):
 assert set(d)=={'path','sha256','bytes'};p=physical(d['path']);before=identity(p)
 assert stat.S_ISREG(before[2])and before[4]==d['bytes'];actual=desc(p)
 ok('hash '+d['path'],actual['sha256']==d['sha256']and actual['bytes']==d['bytes']and identity(p)==before)
 if d['path']in seen:assert seen[d['path']]==d and ids[d['path']]==before
 else:seen[d['path']]=d;ids[d['path']]=before
 return p
def read(d):assert d['bytes']<=32*1024**2;return json.loads(checked(d).read_bytes())
def local(p):return read(desc(p))
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def family(ix):
 value=read(ix);root=Path(ix['path']).parent;names={'index.json'};rows=[ix]
 for r in value['files']:
  n=r['path'];assert n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/'))and n not in names;names.add(n);d=dict(r,path=str(root/n));checked(d);rows.append(d)
 assert not any(p.is_symlink()for p in root.rglob('*'))
 ok('whole family '+str(root),names=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()});families[ix['path']]=ix;return rows
def fixed(p,k):
 assert p['schemaVersion']==1 and p['verifiedPassed']is True and p['state']==k['requiredReviewState']
 for group in ['requiredFixedValues','requiredExactDescriptors','requiredVerifiedProperties']:
  for key,want in k.get(group,{}).items():ok('whole contract '+key,p[key]==want)
 if 'requiredCoverage'in k:ok('whole contract coverage',p['coverage']==k['requiredCoverage'])
def proof(pair,contract):
 rows=family(pair['index']);assert pair['result']in rows and contract in rows;p=read(pair['result']);fixed(p,read(contract));return p
def pure(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 start=time.monotonic();rootrow=desc(K/'node-crypto-hash-hmac-freeze-v1-root-results.json');assert rootrow['sha256']=='f84242c4166e66f84d6fe18eff6d2f789e5bdf18bbf2ef263fb5fc76bde8e923';root=read(rootrow)
 assert root['rawParentExitCode']==0 and root['allOwnedGroupsGone']is root['freezeProcessSucceeded']is True
 receipt=read(root['actualFreezeReceipt']);assert receipt['freezerSourceIndex']==root['sourceIndex']and receipt['rootAuthority']==root['rootAuthority']
 refs=local(SOURCE/'references.json');ownrows=family(root['sourceIndex']);assert root['sourceIndex']['sha256']=='45eef4b6de1e24e450737b66cfc7216e81e39192f8be11be7e80f4312f7c9355'
 artifact=proof(refs['artifactReview'],refs['artifactContract']);source_peer=proof(root['sourceReview'],local(K/'node-crypto-hash-hmac-freeze-v1-root-authority.json')['sourceReviewContract'])
 assert source_peer['freezerSourceIndexSha256']==root['sourceIndex']['sha256']
 authority=read(root['rootAuthority']);config=read(root['rootConfig']);invocation=read(root['invocation'])
 assert config['rootAuthority']==root['rootAuthority']and config['freezerIndex']==root['sourceIndex']and authority['sourceReview']==root['sourceReview']
 for key in ['engineExecuted','guestExecuted','cryptoOperationsInvoked','liveEvpSnapshotAdmission','operationalAdmission','runtimeAcceptanceClaim']:ok('Root no acceptance '+key,root[key]is False)
 inputs=read(refs['sourceInputs'])
 for d in inputs['files']:checked(d)
 for ix in inputs['families']:family(ix)
 ledger=read(refs['artifactLedger']);assert len(ledger['files'])==21451
 for d in ledger['files']:checked(d)
 for d in read(refs['referenceAdditions'])['files']:checked(d)
 aliases=read(refs['referenceAliases'])
 for a in aliases['symlinks']:ok('alias '+a['path'],Path(a['path']).is_symlink()and os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve(strict=True))==a['resolved'])
 for a in aliases['archiveHardlinks']:
  x=Path(a['path']).stat();y=Path(a['target']).stat();ok('archive hardlink',(x.st_dev,x.st_ino)==(y.st_dev,y.st_ino))
 trees=read(refs['artifactTrees'])['trees'];assert len(trees)==11
 def trees_check():
  for t in trees:
   actual=[]
   for parent,dirs,files in os.walk(t['root'],followlinks=False):
    for name in dirs+files:
     p=Path(parent)/name;kind='symlink'if p.is_symlink()else'directory'if p.is_dir()else'file';actual.append(dict(path=p.relative_to(t['root']).as_posix(),kind=kind,mode=stat.S_IMODE(p.lstat().st_mode)))
     if kind=='file':assert str(p)in seen
   ok('whole current tree '+t['root'],sorted(actual,key=lambda r:r['path'])==t['entries'])
 trees_check()
 assert receipt['state']=='HASH_HMAC357_NORMAL_OFF_REVALIDATED_FREEZE_COMPLETE_UNREVIEWED_V1'
 for key,want in dict(nativeSourceFiles=357,externalEmbeddingSources=3,rawMetadataFields=83,selectedWholeManifests=12,stagedSourceAndToolFiles=1642,stagedEmbeddingReferences=3,compileDatabaseRows=69,policyCpp=63,privateCpp=7,strictCpp=4,separateEmbeddingCpp=1,historicalCurrentLedgerFiles=21451,referenceTrees=11,freshProducerAdmissionCalls=1,originalRecipeExitCode=0,originalParentExitCodes=[1,1]).items():ok('receipt '+key,receipt[key]==want)
 for key in ['originalBuildPreservationPassed','originalBuildAccepted','originalNinjaCommandReexecuted','originalCompilerRawExitProofClaim','liveEvpSnapshotAdmission','engineExecuted','guestExecuted','cryptoOperationsInvoked','operationalAdmission','runtimeAcceptanceClaim','pinsAdopted']:ok('receipt false '+key,receipt[key]is False)
 for key in ['fullCurrentReferenceClosureChecked','referencesNotAllPhysicallyCopied','rawMetadataUnchanged','rawMetadataOriginalPathsPreserved']:ok('receipt true '+key,receipt[key]is True)
 st=FREEZE.stat();owner=receipt['rootOwnership'];assert stat.S_IMODE(st.st_mode)==0o700 and(st.st_dev,st.st_ino)==(owner['device'],owner['inode'])
 copies={};copy_ids=set();inventory=[];originals=set()
 for r in receipt['copies']:
  d={k:r[k]for k in ['path','sha256','bytes']};p=checked(d);assert p.is_relative_to(FREEZE);name=p.relative_to(FREEZE).as_posix();s=p.stat();key=(s.st_dev,s.st_ino)
  assert name not in copies and name!='normal-off-freeze-receipt.json'and key not in copy_ids;assert s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600;copies[name]=r;copy_ids.add(key)
  old=None
  if r['original']is not None:
   q=checked(r['original']);a=q.stat();old=dict(device=a.st_dev,inode=a.st_ino,mode=stat.S_IMODE(a.st_mode),links=a.st_nlink);originals.add(str(q));assert key!=(a.st_dev,a.st_ino)and(d['sha256'],d['bytes'])==(r['original']['sha256'],r['original']['bytes'])
  inventory.append(dict(copy=d,device=s.st_dev,inode=s.st_ino,mode=stat.S_IMODE(s.st_mode),links=s.st_nlink,original=r['original'],originalIdentity=old,role=r['role']))
 actual=set()
 for p in FREEZE.rglob('*'):
  s=p.lstat();assert not p.is_symlink()
  if stat.S_ISDIR(s.st_mode):assert stat.S_IMODE(s.st_mode)==0o700
  else:assert stat.S_ISREG(s.st_mode);actual.add(p.relative_to(FREEZE).as_posix())
 ok('whole frozen membership1894',len(copies)==1893 and actual==set(copies)|{'normal-off-freeze-receipt.json'}and len(actual)==1894)
 rs=checked(root['actualFreezeReceipt']).stat();assert(rs.st_dev,rs.st_ino)not in copy_ids and rs.st_nlink==1 and stat.S_IMODE(rs.st_mode)==0o600
 def row(n):return{k:copies[n][k]for k in ['path','sha256','bytes']}
 def original_role(d):
  names=[n for n,r in copies.items()if r['original']==d];assert names,d;return row(names[0])
 def complete(prefix,ix):
  saved=row(prefix+'/index.json');assert(saved['sha256'],saved['bytes'])==(ix['sha256'],ix['bytes']);value=read(saved);names={'index.json'}
  for d in value['files']:
   assert d['path']not in names;names.add(d['path']);got=row(prefix+'/'+d['path']);assert(got['sha256'],got['bytes'])==(d['sha256'],d['bytes'])
  assert {n[len(prefix)+1:]for n in copies if n.startswith(prefix+'/')}==names
  return value
 complete('artifact-tools/source',root['sourceIndex']);complete('artifact-review',refs['artifactReview']['index']);complete('freezer-source-review',root['sourceReview']['index'])
 raw=read(root['metadata']);assert raw==read(refs['metadata'])and len(raw)==83 and root['engine']['sha256']==refs['engine']['sha256']=='9aec9297122c33b60790fcf4e1ce909db0200a426c04de98074e39046aa0f16e'
 assert row('revalidation-data/rawMetadata.json')['sha256']==root['metadata']['sha256']=='2b725c114a3c23e582f87213ec5de6af128416dc8f10e9a9f9d3f6cd5d0fbce6'
 stage=read(refs['stageJournal']);expected=[]
 def expected_add(d,name,role):expected.append(dict(source=d,destination=name,role=role))
 expected_add(refs['engine'],'normal-off.engine.wasm','unchanged-raw9aec-native-engine-DATA');expected_add(refs['metadata'],'normal-off.engine.wasm.build.json','unchanged-raw83-metadata-original-paths')
 for r in stage['copies']:expected_add(dict(path=str(Path(refs['configuredSourceRoot'])/r['path']),sha256=r['sha256'],bytes=r['bytes']),'source/'+r['path'],'current-full-staged1642-source-and-tool-DATA')
 for r in stage['embeddingDataCompleted']:expected_add(r['target'],'stage-embedding-reference/'+r['source']['path'],'historical-staged-embedding-reference-not-configured-source')
 for r in raw['componentizeSourceManifest']:
  p=Path(raw['combinedNativeSourcePolicy']['externalConfiguredSourceRoot'])/r['path'];expected_add(dict(path=str(p),sha256=r['sha256'],bytes=p.stat().st_size),'componentize-source/'+r['path'],'actual-configured-external-embedding-source')
 work=read(refs['workCopyPlan']);assert len(work['files'])==169 and work['copyBytes']==557901902
 for r in work['files']:expected_add(r['source'],r['destination'],';'.join(r['roles']))
 for d in ownrows:expected_add(d,'artifact-tools/source/'+Path(d['path']).relative_to(SOURCE).as_posix(),'complete-own-freezer-source-capsule')
 for key,name in [('producerReferences','references.json'),('activePolicy','policy.json'),('activeRecipe','build-engine.sh'),('activeHelper','layer-policy.py'),('producerAdmission','admission.py'),('producerIo','io_guard.py')]:expected_add(refs[key],'producer-source/'+name,'genuine-original-P3-producer-DATA')
 for prefix,pair in [('artifact-review',refs['artifactReview']),('freezer-source-review',root['sourceReview'])]:
  for d in family(pair['index']):expected_add(d,prefix+'/'+Path(d['path']).relative_to(Path(pair['index']['path']).parent).as_posix(),'complete-review-family-DATA-no-nested-physical-normalization')
 for role,d in dict(result=refs['artifactResult'],rawMetadata=artifact['rawMetadata'],inputHashes=refs['artifactLedger'],referenceAliases=refs['referenceAliases'],distributionData=refs['distributionData'],producerAdmission=artifact['producerAdmissionReturn']).items():expected_add(d,'revalidation-data/'+role+'.json','whole-original-read-only-revalidation-DATA')
 for role,d in dict(buildResult=refs['originalBuildResult'],rootObservation=refs['originalBuildObservation'],reviewIndex=refs['originalFailureReview']['index'],reviewResult=refs['originalFailureReview']['result'],reviewContract=refs['originalFailureContract'],failedReadOnlyRoot=refs['failedReadOnlyObservation']).items():expected_add(d,'original-failure-data/'+role+'.json','original-failed-phase-witness-DATA-not-relocated-whole-family')
 for key,name,role in [('artifactTrees','reference-closure/artifact-trees.json','complete-eleven-original-trees-DATA-not-distribution-copies'),('referenceAdditions','reference-closure/additions.json','explicit-current-tree-file-coverage-additions'),('sourceInputs','reference-closure/source-inputs.json','original-reference-protection-descriptors')]:expected_add(refs[key],name,role)
 expected_add(root['rootConfig'],'provenance/config.json','new-freeze-config');expected_add(root['rootAuthority'],'provenance/root-authority.json','new-freeze-only-Root-authority')
 actual_plan=read(receipt['copyPlan']);ok('whole independently derived1889 copy plan',actual_plan['copies']==expected and len(expected)==1889)
 for r in expected:
  got=copies[r['destination']];assert got['original']==r['source']and got['role']==r['role']
 assert sum(n.startswith('source/')for n in copies)==1642 and sum(n.startswith('componentize-source/')for n in copies)==3 and sum(n.startswith('stage-embedding-reference/')for n in copies)==3
 old=read(original_role(refs['originalBuildResult']));assert old['rawChildExitCode']==0 and old['launcherExitCode']==1 and old['evidenceComplete']is False
 original_review=proof(refs['originalFailureReview'],refs['originalFailureContract']);assert original_review['phaseSucceeded']is original_review['buildAcceptanceClaim']is False
 fresh=read(receipt['freshProducerAdmission']);historical=read(original_role(artifact['producerAdmissionReturn']));actual_revalidation=read(original_role(refs['artifactResult']))
 ok('whole fresh P3 return equals authentic historical return',fresh==historical==actual_revalidation['producerAdmission'])
 assert fresh['controllerSourceIndexSha256']==refs['producerIndex']['sha256']and fresh['sourceIndexSha256']==refs['integrationIndex']['sha256']and fresh['metadata']==refs['metadata']and fresh['rawMetadataFields']==83
 # Only authenticated pure DATA models are imported; no admission/freeze/verify.
 model=pure('independent_frozen_raw83_pure_model',checked(row('artifact-tools/source/metadata_model.py')));hm=pure('independent_frozen_hash_command_pure_model',checked(row('artifact-tools/source/hash_model.py')))
 policy=read(row('producer-source/policy.json'));producer=read(row('producer-source/references.json'))
 classified=model.validate_metadata(raw,policy,producer['policy']['sha256'],producer['helper']['sha256'],producer['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off');assert classified['nativeFiles']==357 and classified['grantsAuthority']is False
 for key,prefix,count in [('sourceManifest','source',357),('componentizeSourceManifest','componentize-source',3)]:
  assert len(raw[key])==count
  for d in raw[key]:assert row(prefix+'/'+d['path'])['sha256']==d['sha256']
 selected=[read(row('source/'+d['path']))for d in raw['selectedModuleManifests']];assert hm.validate_selected_manifests(raw,policy,selected)
 database=read(original_role(next(r['original']for r in copies.values()if r['original']is not None and r['original']['path']==raw['compileCommandsPath'])));assert len(database)==69
 commands=hm.validate_hash_hmac_commands(database,raw['actualEmbeddingCompileCommands'],Path(producer['configuredSourceRoot']),raw,policy);assert len(commands['actualPrivateHashHmacMacroCompileCommands'])==7
 link=raw['nodeCryptoHashHmacPolicy']['actualLinkEvidence'];archivepaths=[w if w.startswith('/')else posixpath.normpath(str(Path(raw['cmakeCachePath']).parent)+'/'+w)for w in link['linkArgv']if w.endswith('.a')]
 workpaths={r['source']['path']for r in work['files']};assert set(archivepaths)<=workpaths
 ninja=raw['nodeCryptoHashHmacPolicy']['actualNinjaCapture'];assert ninja['rawExitCode']==0 and not ninja['timeout'];assert link['completeNinjaLine']in checked(original_role(ninja['stdout'])).read_text().splitlines()
 pieces=[];current=[]
 for word in shlex.split(link['completeNinjaLine']):
  if word=='&&':pieces.append(current);current=[]
  else:current.append(word)
 pieces.append(current);assert pieces.count(link['linkArgv'])==1
 install=raw['nodeCryptoHashHmacPolicy']['actualInstallationOrder'];text=checked(original_role(install['source'])).read_text();assert text.count(install['cryptoNamespace'])==text.count(install['nodeNamespace'])==1 and text.index(install['cryptoNamespace'])<text.index(install['nodeNamespace'])
 assert read(row('provenance/config.json'))==config and read(row('provenance/root-authority.json'))==authority
 control=read(receipt['control']);assert control['freshProducerAdmissionCalls']==1 and control['originalBuildAccepted']is False
 attempt=read(receipt['admissionAttempt']);assert attempt['producerIndex']==refs['producerIndex']and attempt['oldBootstrapFrameClaimed']is False
 # Complete durable monitor records, not reconstructed process observations.
 outer=read(root['ownedTerminal']);inner=read(desc(Path(refs['externalRoot'])/'terminal.json'))
 raw_event_rows=0
 for label,t in [('outer',outer),('inner',inner)]:
  assert t['rawExitCode']==0 and t['allObservedOwnedGroupsGone']and t['parentOwnedGroupGone']and not t['timeout']and not t['forcedCleanup']and not t['remainingObservedPids']and not t['signals']and not t['errors']and not t['interruptedSignals']
  checked(t['stdout']);assert checked(t['stderr']).read_bytes()==b''
  assert all(g['alive']is False and g['signalAllowed']is False for g in t['finalGroups'])
  folder=Path(t['stdout']['path']).parent;events=sorted(folder.glob('owned-*.json'));assert len(events)==len(t['observedProcesses'])
  for n,event in enumerate(events):
   observed=local(event);assert observed['sequence']==n and observed['process']==t['observedProcesses'][n];raw_event_rows+=1
  started=local(folder/'started.json');assert started['pid']==t['pid']and started['timeoutSeconds']==1800
  assert started['argv'][1:3]==['-B','-I']and Path(started['argv'][3])==SOURCE/'entry.py'and started['argv'][4]==('parent'if label=='outer'else'worker')and json.loads(started['argv'][5])==root['rootConfig']
 assert raw_event_rows==303
 outer_lines=[json.loads(x)for x in checked(outer['stdout']).read_text().splitlines()];inner_lines=[json.loads(x)for x in checked(inner['stdout']).read_text().splitlines()]
 assert len(outer_lines)==2 and len(inner_lines)==1 and outer_lines[0]['pid']==inner['pid']and outer_lines[0]['timeoutSeconds']==1800
 assert outer_lines[1]['receipt']==root['actualFreezeReceipt']and outer_lines[1]['externalParentTerminal']==desc(Path(refs['externalRoot'])/'terminal.json')
 verified=inner_lines[0];assert verified['state']=='HASH_HMAC357_FROZEN_ONLY_CAPSULE_VERIFIED_NOT_ADOPTED_V1'and verified['receipt']==root['actualFreezeReceipt']and verified['engine']==root['engine']and verified['metadata']==root['metadata']and verified['copies']==1893
 assert verified['originalParentExitCodes']==[1,1]and verified['originalBuildPreservationPassed']is verified['originalBuildAccepted']is verified['helperOrAdmissionReexecuted']is False
 for path,d in list(seen.items()):ok('final hash/identity '+path,identity(checked(d))==ids[path])
 trees_check();assert (FREEZE.stat().st_dev,FREEZE.stat().st_ino)==(owner['device'],owner['inode'])
 ok('final frozen membership',{p.relative_to(FREEZE).as_posix()for p in FREEZE.rglob('*')if p.is_file()}==actual)
 save('copy-inventory.json',dict(schemaVersion=1,scope='Independently measured1893 frozen copy files and their current original identities; full receipt is separately authenticated.',files=inventory))
 save('reader-results.json',dict(schemaVersion=1,state='INDEPENDENT_HASH_HMAC357_ACTUAL_FREEZE_DATA_READER_PASSED',rootObservation=rootrow,freezeReceipt=root['actualFreezeReceipt'],checks=len(checks),uniqueRehashedFiles=len(seen),logicalBytes=sum(r['bytes']for r in seen.values()),families=len(families),frozenCopies=1893,physicalFrozenFiles=1894,copyPlanOriginalRows=1889,generatedRows=4,uniqueOriginalCopyPaths=len(originals),workWitnessFiles=169,sourceAndToolFiles=1642,configuredExternalFiles=3,historicalEmbeddingReferences=3,nativeSourceFiles=357,rawMetadataFields=83,selectedWholeManifests=12,completeLiveReferenceTrees=11,symlinkAliases=35,archiveHardlinks=1,wholeP3ReturnEqual=True,outerJsonlRecords=2,innerJsonlRecords=1,rawParentExitCodes=[0,0],rawOwnedEventRows=raw_event_rows,allOwnedGroupsGone=True,originalRecipeExitCode=0,originalParentExitCodes=[1,1],originalBuildPreservationPassed=False,originalBuildAccepted=False,independentVerifierOrAdmissionOrHelperOrEngineOrGuestRerun=False,originalsHiddenExperimentPerformed=False,elapsedOperationalSeconds=time.monotonic()-start))
 print(json.dumps(json.loads((OWN/'reader-results.json').read_bytes())))
if __name__=='__main__':main()
