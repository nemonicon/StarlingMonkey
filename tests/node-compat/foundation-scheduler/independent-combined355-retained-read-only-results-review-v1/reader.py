"""Independent actual combined355 retained read-only DATA reader. No owner imports/actions."""
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
rootrow=dict(path=str(S/'combined-native355-artifact-v1-read-only-root-results.json'),sha256='7f0e89475c9e9029344bf3776ca08b52f1c23b39addc16479ec68cc74e44512c',bytes=4947)
r=read(rootrow);need(r['state']=='ROOT_OBSERVED_COMBINED355_RETAINED_READ_ONLY_ZERO_UNREVIEWED_V1'and r['toolObservation']['sessionId']==43356 and r['toolObservation']['rawExitCode']==0,'actual Root read-only tool terminal')
ix=r['toolingIndex'];need(ix['sha256']=='c365e6089688f62f028580e86b14db80bb434ba7b4ac45ae341e851c11913a7b','genuine c365');members=family(ix);need(len(members)==31,'full Source31');refs=load(C/'references.json');declared=load(C/'source-inputs.json')
for x in declared['files']:verify(x)
root=read(r['rootAuthority']);cfg=read(r['config']);invocation=read(r['invocation']);callertext=verify(r['caller']).read_text()
need(cfg==dict(schemaVersion=1,state='COMBINED355_NATIVE_READ_ONLY_BOOTSTRAP_CONFIG_V1',toolingIndex=ix,rootAuthority=r['rootAuthority']),'actual distinct read-only config')
need(root['state']=='ROOT_REVIEWED_COMBINED355_READ_ONLY_BOOTSTRAP_V1'and root['toolingIndex']==ix and root['actualFrozenReview']==refs['actualFrozenReview']and root['actualBootstrapReview']==r['actualBootstrapReview']and root['readOnlyAdmissionAllowed']is True,'actual read-only Root roles')
for k in ['exportAllowed','bootstrapActionAllowed','nativeBuildAllowed','nativeFreezeAllowed','ninjaAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','componentAllowed','sourcePromotionAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:need(root[k]is False,'no extra read-only permission '+k)
peer=proof(root['sourceIndependentReview']);need(peer['state']=='INDEPENDENT_COMBINED355_NATIVE_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V1'and peer['toolingSourceIndexSha256']==ix['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True,'actual c365 Source peer')
for k in ['ownerActionsInvoked','hostActionsInvoked','exportOrBootstrapActionsInvoked']:need(peer[k]is False,'Source-only peer')
bootcontract=row(S/'independent-combined355-native-bootstrap-results-review-v1/result-contract.json');bootproof=contract(r['actualBootstrapReview'],bootcontract);need(bootproof['toolingSourceIndexSha256']==ix['sha256']and bootproof['state']=='INDEPENDENT_COMBINED355_NORMAL_OFF_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1','actualfa45 bootstrap DATA prerequisite');bootstrap=read(bootproof['bootstrapFrame'])
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
base=Path('/private/tmp/starling-node-compat/combined-native355-retained-read-only-v1');external=Path(str(base)+'-external-root')
exact_tree(base,{'calls/001.data.json','calls/002.data.json','calls/001.shape.json','calls/002.shape.json','results.json'},private=True)
terminal=read(r['externalTerminal']);clean(terminal,r['rootAuthority'],54826);need({x['pgid']for x in terminal['finalGroups']}=={54826}and len(terminal['observedProcesses'])==1 and terminal['observedProcesses'][0]['pid']==54826,'one actual Node and one clean group')
exact_tree(external,{'terminal.json','stdout.log','stderr.log','started.json','owned-0000.json','environment-policy.json'})
start=load(external/'started.json');event=load(external/'owned-0000.json');need(event['sequence']==0 and same(event['process'],terminal['observedProcesses'][0]),'whole ownership event')
need(invocation['rootAuthority']==r['rootAuthority']and invocation['config']==r['config']and invocation['caller']==r['caller']and invocation['deadlineSeconds']==1200 and invocation['apiReadHashOnly']is True and invocation['engineOrGuestAllowed']is False,'actual caller invocation roles')
expectedargv=[refs['node']['path'],r['caller']['path'],json.dumps(r['config'],separators=(',',':')),str(base)];need(invocation['actualArgv']==start['argv']==expectedargv and start['pid']==54826 and start['authority']==r['rootAuthority']and start['timeoutSeconds']==1200,'full actual Node argv, plain execArgv/deadline')
verify(refs['node']);need(terminal['stdout']==r['rawStdout']and terminal['stderr']==r['rawStderr'],'actual raw streams')
need(read(r['rawStdout'])==dict(calls=2,recheckCalls=3,completeUnreviewed=True,engineExecuted=False),'whole raw stdout summary')
environment=read(r['environmentPolicy']);need(environment==dict(keys=['HOME','LOGNAME','PATH','PYTHONDONTWRITEBYTECODE','TMPDIR','USER'],valuesRetained=False),'selected environment names; values not attested')
data=[read(x)for x in r['actualReturnData']];shapes=[read(x)for x in r['actualReturnShapes']];need(len(data)==len(shapes)==2 and same(data[0],data[1])and same(shapes[0],shapes[1]),'both complete fresh record DATA and shape equal')
expectedverification=dict(schemaVersion=1,kind='current-read-hash-verification-v1',config=r['config'],rootAuthority=r['rootAuthority'],sourceIndex=ix,fullMetadataFields=80,selectedWholeManifests=11,helperInvocations=0,processesSpawned=0,filesCreated=0,engineExecuted=False,guestExecuted=False,operationalAdmission=False)
expecteddata=dict(schemaVersion=1,kind='retained-combined355-bootstrap-v1',sourceIndex=ix,actualReview=r['actualBootstrapReview'],bootstrap=bootstrap,currentVerification=expectedverification)
need(same(data[0],expecteddata)and len(data[0])==6,'entire six returned DATA fields equal independent expected model; historical40 unchanged')
shape={k:dict(type=t,enumerable=True,writable=False,configurable=False)for k,t in [('schemaVersion','number'),('kind','string'),('sourceIndex','object'),('actualReview','object'),('bootstrap','object'),('currentVerification','object'),('recheck','function')]};need(same(shapes[0],dict(shape=shape,callableRecheckSerialized=False,allOtherReturnedDataRetained=True)),'whole seven own descriptors with genuine function shape, no serialized callable admission')
need(len(bootstrap['metadata'])==80 and bootstrap['nativeSourceFiles']==355 and bootstrap['externalEmbeddingSources']==3 and len(bootstrap['selectedManifests'])==11 and bootstrap['currentFrozenVerifierCalls']==1,'full80/355+3/11 historical1 remains DATA')
need(bootstrap['nativeFrame']['verificationCapsule']['state']=='COMBINED355_NORMAL_FREEZE_READ_ONLY_CAPSULE_VERIFIED_NOT_ACCEPTED_V1'and bootstrap['nativeFrame']['runtimeBackendProof']==dict(verified=False,version=None,vernum=None),'no unaccepted capsule/backend relabel')
actual=read(r['actualResult']);expectedactual=dict(schemaVersion=1,state='ROOT_COMBINED355_RETAINED_READ_ONLY_API_COMPLETE_UNREVIEWED_V1',config=r['config'],sourceIndex=ix,actualReview=r['actualBootstrapReview'],calls=2,freshRechecks=2,recheckCalls=3,wholeHistoricalBootstrapDataEqual=True,currentHelperInvocations=0,currentProcessesSpawnedByApi=0,currentFilesCreatedByApi=0,currentVerificationDataSeparateFromHistoricalBootstrap=True,fullMetadataFields=80,nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,engineExecuted=False,guestExecuted=False,componentBuilt=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
need(same(actual,expectedactual),'whole actual results DATA')
api=verify(next(x for x in members if x['path']==str(C/'bootstrap.mjs'))).read_text()
need(api.count('export async function combinedNativeBootstrapPreflight(')==1 and 'import('not in api and 'spawn('not in api and 'execFile('not in api and 'writeFile('not in api,'actual read/hash API contains no helper/process/package/writer call')
need('const recheck=async()=>{await c.recheck();'in api and 'finally{try{await c.recheck();}'in api and 'return Object.freeze({'in api,'fresh own recheck and final/failure guards')
need(callertext.count('await api.combinedNativeBootstrapPreflight({configDescriptor:config})')==2 and callertext.count('await first.recheck()')==2 and callertext.count('await second.recheck()')==1,'actual Source-coupled twoAPI+threeownrechecks')
need("assert.notEqual(first.recheck,second.recheck)"in callertext and "const data=Object.fromEntries(Object.entries(frame).filter(([k])=>k!=='recheck'))"in callertext and "await write('calls/'+n+'.data.json',data)"in callertext,'callable identity/freshness and all DATA observed before assertions')
need(callertext.index("await write('calls/'+n+'.data.json',data)")<callertext.index('assert.deepEqual(Reflect.ownKeys(frame)'),'raw returned DATA retained before shape assertions')
need('apiRow=index.files.find' in callertext and callertext.index('await checked({...apiRow')<callertext.index('const api=await import('),'actual Root caller checked c365 API bytes before import')
for k in ['rootAuthority','config','invocation','caller','actualResult','externalTerminal','rawStdout','rawStderr','environmentPolicy']:retained(k+'.json'if k not in ['caller','rawStdout','rawStderr']else k+('.mjs'if k=='caller'else'.log'),r[k])
for n,d in enumerate(r['actualReturnData'],1):retained('call-'+str(n)+'.data.json',d)
for n,d in enumerate(r['actualReturnShapes'],1):retained('call-'+str(n)+'.shape.json',d)
for n in ['started.json','owned-0000.json']:retained(n,row(external/n))
retained('root-results.json',rootrow)
for path,d in list(seen.items()):
 p=Path(path);need(identity(p)==identities[path],'current final input identity');h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 need(h.hexdigest()==d['sha256'],'current final bytes unchanged')
for t in protection['trees']:exact_tree(t['root'],t['files'],t['links'])
exact_tree(F,names,private=True);exact_tree(base,{'calls/001.data.json','calls/002.data.json','calls/001.shape.json','calls/002.shape.json','results.json'},private=True)
coverage=dict(toolingSourceMembers=31,returnedRecords=2,returnedDataFields=6,returnedOwnPropertyDescriptors=7,freshRecheckFunctions=2,sourceCoupledRecheckCalls=3,historicalBootstrapFields=40,fullMetadataFields=80,nativeSources=355,externalEmbeddingSources=3,selectedWholeManifests=11,currentApiHelperInvocations=0,currentApiProcessesSpawned=0,currentApiFilesCreated=0,historicalBootstrapVerifierCalls=1,observerCreatedOutputFiles=5,ownedGroups=1,compactRows=2618,expandedBuildRows=20816,inheritedFamilies=15,frozenCopies=2596,frozenMembershipFiles=2597,stagedOriginalPairs=1613,originalAliases=31,originalArchiveHardlinks=1,currentUniqueReferences=len(seen),actualRawTextCopies=len(raw_copies))
state='INDEPENDENT_COMBINED355_RETAINED_READ_ONLY_RESULTS_REVIEW_PASSED_V1'
fixed=dict(schemaVersion=1,verifiedPassed=True,toolingSourceIndexSha256=ix['sha256'],nativeSourceFiles=355,externalEmbeddingSources=3,fullMetadataFields=80,selectedManifestCount=11,rawReadOnlyExitCode=0,allObservedOwnedGroupsGone=True,wholeReturnedDataEqual=True,currentApiHelperInvocations=0,currentApiProcessesSpawned=0,currentApiFilesCreated=0,historicalBootstrapVerifierCalls=1,engineExecuted=False,guestExecuted=False,componentBuilt=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
direct={k:r[k]for k in ['toolingIndex','actualBootstrapReview','rootAuthority','config','invocation','caller','actualResult','externalTerminal','rawStdout','rawStderr']};direct.update(sourcePeer=root['sourceIndependentReview'],rootObservation=rootrow,actualBootstrapContract=bootcontract,retainedData=r['actualReturnData'][0],retainedDataRecords=r['actualReturnData'],retainedShape=r['actualReturnShapes'][0],retainedShapes=r['actualReturnShapes'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'])
limits=['Independent read/hash/DATA review only; no retained API/recheck/helper/verifier/monitor, package/engine/guest or phase called by reviewer.','Owner actual API was invoked twice and returned two distinct frozen frames/functions, with three own rechecks, as evidenced by authenticated observer Source and clean raw completion. This is Source-coupled identity/call accounting, not serialized callable proof or independent native instrumentation.','All six returned DATA fields compare exactly, including entire40-field historical bootstrap frame, raw80metadata/native355+3/all11 manifests and unchanged NOT_ACCEPTED capsule. The seventh own property is an actual function descriptor; no callable serialization/admission claim.','Current API helper/process/write counts0 are scoped to API calls; the host observer wrote five evidence files and its Node process was genuinely launched. Historical operational bootstrap verifier1 remains DATA and is not recast as this read-only action.','Full fixed native/frozen/source protection currently rehashed using existing2618/20816/15 boundaries and modes/inodes/aliases. Actual-time protection comes from authenticated API control flow and clean operation; no invented separate time-bookend attestation.','Selected environment names and actual plain Node argv are retained; global OS/environment attestation is not claimed. No component construction, ordinary runtime, keys/crypto/GC/free/wipe/reset/ALS/isolated-root/host reuse/performance/adoption acceptance.']
save('boundary-review.json',dict(schemaVersion=1,compactInputBoundary=refs['compactInputBoundary'],expandedBuildInputLedger=refs['reviewedBuildInputLedger'],inheritedFamilies=refs['inheritedFamilies'],frozenCopyInventory=refs['frozenCopyInventory'],freezerProtection=refs['freezerProtection'],referenceAliasWitness=refs['referenceAliasWitness'],coverage=coverage,currentProtectionRehashed=True,historicalTreesRecopied=False))
save('raw-copies.json',dict(schemaVersion=1,files=raw_copies,allWholeBytesPreserved=True))
save('results.json',dict(**fixed,state=state,**direct,coverage=coverage,readOnlyDataReview=True,checks=checks,wholeHistoricalBootstrapDataEqual=True,freshRecheckFunctions=2,recheckCalls=3,ownerRetainedApiInvoked=True,ownerActionsInvoked=False,hostActionsInvoked=False,reviewerApiRecheckHelperVerifierOrEngineInvoked=False,callableSerializationClaim=False,actualComponentProof=None,runtimeAuthority=None,materialFindings=[],limitations=limits))
save('result-contract.json',dict(schemaVersion=1,requiredReviewState=state,requiredFixedValues=fixed,requiredExactDescriptors=direct,requiredCoverage=coverage,issuesAnyActionAuthority=False))
(P/'README.md').write_text('Independent actual combined355 retained read-only API DATA review\n\nBounded DATA PASS; no reviewer API/helper/process or engine actions. Two whole returned records and seven-property descriptor shapes, exact historical/current separation and clean raw ownership verified.\n\n'+'\n\n'.join(limits)+'\n')
save('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_COMBINED355_RETAINED_READ_ONLY_DATA_REVIEW_V1',result=row(P/'results.json'),contract=row(P/'result-contract.json'),rootObservation=rootrow,allOriginalBytesPreserved=True,reviewerOperationalActions=False))
files=[]
for q in sorted(P.rglob('*')):
 if q.is_file():d=row(q);files.append(dict(d,path=q.relative_to(P).as_posix()))
save('index.json',dict(schemaVersion=1,files=files))
for name in ['index.json','results.json','result-contract.json','receipt.json']:print(json.dumps(row(P/name)))
print(json.dumps(dict(sealed=True,indexed=len(files),checks=checks,coverage=coverage,reviewerOperationalActions=False)))
