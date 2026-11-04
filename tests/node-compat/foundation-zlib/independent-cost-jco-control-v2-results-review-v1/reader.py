"""Independent retained bytes/JSON/source reader. No owner or runtime imports."""
import base64,copy,hashlib,json,math,re,stat
from pathlib import Path
P=Path(__file__).resolve().parent;Z=P.parent
OUT=Path('/private/tmp/starling-node-compat/zlib-cost-jco-control-correctness-v2')
C=Z/'cost-jco-control-correctness-candidate-v2';D=Z/'cost-jco-control-correctness-candidate-v1'
G=Z/'cost-guest-oracle-candidate-v2';R=Z/'independent-cost-jco-correctness-v3-results-review-v1'
SOURCE='3b56608315d48d92dd8b72c9e7c73a3c179d0d2fefb9555a79cd216be45d1ff1'
ARMS=['native-on','fflate-on','fflate-off'];NAMES=['identity','setup','observe','batch','checkpoint','stage','validate']
seen={};ledger=[]
def need(value,message):
 if not value:raise AssertionError(message)
def read(path,expected=None):
 path=Path(path);before=path.lstat();need(stat.S_ISREG(before.st_mode),'Ordinary file '+str(path));h=hashlib.sha256();parts=[]
 with path.open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block);parts.append(block)
 after=path.lstat();need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'Stable data read')
 row=dict(path=str(path),sha256=h.hexdigest(),bytes=after.st_size)
 if expected:need(all(row[k]==expected[k]for k in ('sha256','bytes')),'Exact file tuple '+str(path))
 seen[str(path)]=row;return b''.join(parts)
def info(path):read(path);return seen[str(Path(path))]
def pairs(items):
 value={}
 for k,v in items:need(k not in value,'No duplicate JSON key');value[k]=v
 return value
def parse(raw):return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(AssertionError('Nonfinite JSON')))
def doc(path,expected=None):return parse(read(path,expected))
def exact(actual,expected,message):
 def same(a,b):
  if type(a)is not type(b):return False
  if isinstance(a,dict):return a.keys()==b.keys()and all(same(a[k],b[k])for k in a)
  if isinstance(a,list):return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
  return a==b
 need(same(actual,expected),message)
def local(name):
 need(isinstance(name,str)and name and not Path(name).is_absolute()and all(v not in ('','.','..')for v in name.split('/'))and '\\'not in name and '\0'not in name,'Safe local file member');return name
def indexed(base,pin):
 ix=doc(base/'index.json');need(info(base/'index.json')['sha256']==pin,'Exact source/proof index '+str(base))
 for r in ix['files']:read(base/local(r['path']),r)
 return ix
def descriptor(row):return dict(path=row['path'],sha256=row['sha256'],bytes=row['bytes'])
def write(name,value):(P/name).write_text(json.dumps(value,indent=2)+'\n')
def fnv(data):
 value=2166136261
 for b in data:value=((value^b)*16777619)&0xffffffff
 return value
def unbase(value):
 result=base64.b64decode(value,validate=True);need(base64.b64encode(result).decode()==value,'Canonical whole base64');return result
def fixture(name,size):
 if name=='empty':return b''
 if 'repeat'in name:return(b'abc123'*((size+5)//6))[:size]
 state=0x6d2b79f5;out=bytearray(size)
 for i in range(size):
  state=(state^(state<<13))&0xffffffff;state=(state^(state>>17))&0xffffffff;state=(state^(state<<5))&0xffffffff;out[i]=state&255
 return bytes(out)
def walk_descriptors(value):
 if isinstance(value,dict):
  if set(value)=={'path','sha256','bytes'}:read(value['path'],value)
  else:
   for child in value.values():walk_descriptors(child)
 elif isinstance(value,list):
  for child in value:walk_descriptors(child)
def main():
 root_path=Z/'cost-jco-control-v2-root-results.json';root=doc(root_path,dict(sha256='9b22479ed02f7ff0c21b790243c949997f6b2c7a09fa293983ae5d38db692dde',bytes=4314));walk_descriptors(root)
 need(root['rootSessionId']==4837,'Actual Root session4837')
 terminal=doc(root['actualParentTerminal']['path'],root['actualParentTerminal']);walk_descriptors(terminal)
 need(terminal['pid']==96423 and terminal['rawExitCode']==0 and terminal['timeout']is False,'Retained parent96423/raw0/no timeout')
 need(terminal['stderr']['bytes']==0 and terminal['stdout']['bytes']==251,'Complete parent251-byte stdout/empty stderr')
 exact(parse(read(terminal['stdout']['path'])),dict(index=dict(path='index.json',sha256=root['index']['sha256'],bytes=root['index']['bytes']),completion=dict(path='completion.json',sha256=root['completion']['sha256'],bytes=root['completion']['bytes'])),'Whole parent stdout actual index/completion')
 config=doc(root['config']['path'],root['config']);authority=doc(root['rootAuthority']['path'],root['rootAuthority'])
 need(config['controlSourceIndexSha256']==authority['controlSourceIndexSha256']==SOURCE and config['rootAction']==root['rootAuthority'],'Actual exact config/authority/source')
 need(authority['state']=='ROOT_REVIEWED_ZLIB_COST_JCO_CONTROL_CORRECTNESS_V2'and authority['actionAllowed']is True and authority['ordinaryGuestControlCallsAllowed']is True,'Actual separate controlV2 authority')
 need(all(authority[k]is False for k in ['codecCallsAllowed','nodeCodecCallsAllowed','observeStageValidateAllowed','wasmtimeAllowed','pilotOrTimingAllowed','operationalAdmission','runtimeAcceptanceClaim','metadataProjection']),'No expanded action authority')
 indexed(C,SOURCE);indexed(Z/'independent-cost-jco-control-v2-source-review-v1','20cb3efa4c7b54da0e36ef1a62cdbf2bfb482e93b70c56e987fbfdc6366bbdeb')
 indexed(D,'ad0d651fdb8653a8a708514131bad52cf8cc05b657c6cefd92604aca3c3f7a23');indexed(Z/'independent-cost-jco-control-source-review-v1','d6f72a454fd7c8def6042827eb3a139312bb89a996db1d32e224d24e2467bb58')
 indexed(Z/'independent-cost-jco-control-v1-failure-review-v1','534f2d86cb10776600089143609dc96c63c2e0a02bd8a6e3376f3ef9111429a5')
 indexed(G,'ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8')
 indexed(R,'e03bb0db65f6009e86a6d55e4553e820d143c702128976efc5ef47e092548083')
 prior_contract=doc(R/'result-contract.json');need(info(R/'result-contract.json')['sha256']=='25411f2ecb278c1eeda7b27a0aafa47b29cc3d9a53221a327e9e5c94002936f1','Pinned complete prior254 contract')
 prior=doc(R/'results.json')
 for k,v in prior_contract['requiredFixedValues'].items():exact(prior[k],v,'Prior fixed '+k)
 for k,v in prior_contract['requiredCoverage'].items():exact(prior['coverage'][k],v,'Prior coverage '+k)
 need(prior['controlOperations']==0 and prior['executedControlWorkloads']is False,'Prior actual228 proof remains control0')
 for d in prior_contract['requiredExactDescriptors'].values():read(d['path'],d)
 component_proofs={}
 for arm,pair in prior_contract['requiredActualComponentReviews'].items():
  indexed(Path(pair['index']['path']).parent,pair['index']['sha256']);proof=doc(pair['result']['path'],pair['result']);component_proofs[arm]=proof
  need(proof['state']=='INDEPENDENT_ZLIB_COST_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'and proof['arm']==arm and proof['component']==prior_contract['requiredComponents'][arm],'Actual unchanged component artifact proof '+arm)
  for name in ['component','glue','core','dts','wit','transpileMetadata','packageJson','code','nativeEngine','metadata','actualBuildAuthority','externalParentTerminal','ownedWorkerTerminal','workerIndex','workerCompletion','parentResult','workerResult']:read(proof[name]['path'],proof[name])
  need(proof['emittedImports']==[]and len(proof['emittedAbi'])==7,'Existing actual seven-scalar zero-import component proof')
  need(read(proof['packageJson']['path'])==b'{"type":"module"}\n','Actual module package classification')
 # Full current output closure, with no pass-shaped omissions or hidden files.
 parent_index=doc(OUT/'index.json',root['index']);parent=doc(OUT/'results.json',root['results']);complete=doc(OUT/'completion.json',root['completion'])
 need(parent_index['schemaVersion']==1 and len(parent_index['files'])==1480,'Actual1480 indexed rows')
 indexed_rows={}
 for r in parent_index['files']:
  name=local(r['path']);need(name not in indexed_rows,'Unique current index member');indexed_rows[name]=r;read(OUT/name,r)
 need(sum(r['bytes']for r in indexed_rows.values())==2513957,'Whole2513957 indexed bytes')
 actual_files=set()
 for q in OUT.rglob('*'):
  need(not q.is_symlink(),'No output symlink')
  if q.is_file():need(q.stat().st_nlink==1,'Ordinary single-link output');actual_files.add(q.relative_to(OUT).as_posix())
 need(actual_files==set(indexed_rows)|{'index.json','completion.json'}and len(actual_files)==1482,'Exact1482 physical files')
 exact(complete,dict(schemaVersion=1,state='CONTROLS_COMPLETE_EXTERNAL_PARENT_ZERO_AND_REVIEW_REQUIRED_V2',results={k:root['results'][k]for k in ['sha256','bytes']}|{'path':'results.json'},index={k:root['index'][k]for k in ['sha256','bytes']}|{'path':'index.json'},sourceIndexSha256=SOURCE),'Exact current parent completion and final hashes')
 need(parent['controlSourceIndexSha256']==SOURCE and parent['rootAction']==root['rootAuthority']and parent['state']=='UNTIMED_ZLIB_JCO_CONTROLS_COMPLETE_PENDING_INDEPENDENT_REVIEW_V2','Actual new parent source/results')
 need(parent['pilotPrerequisitesSatisfied']is False and parent['timingAllowed']is False and parent['stockWasmtimeExecuted']is False and parent['operationalAdmission']is False and parent['runtimeAcceptanceClaim']is False,'Literal parent phase/admission flags remain false')
 oracle_row=prior_contract['requiredExactDescriptors']['oracle'];oracle=doc(oracle_row['path'],oracle_row);cases=doc(Z/'cost-jco-correctness-candidate-v2/cases.json');need(len(cases)==30 and len(oracle['rawFixtures'])==5 and len(oracle['encodedStreams'])==15,'Complete30case/5raw/15encoded input corpus')
 raw_fixtures={}
 for r in oracle['rawFixtures']:
  b=unbase(r['base64']);need(len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256']and fnv(b)==r['fnv1aU32'],'Whole oracle raw fixture bytes/hash/FNV');need(b==fixture(r['id'],r['bytes']),'Independent deterministic fixture bytes');raw_fixtures[r['id']]=b
 streams={}
 for r in oracle['encodedStreams']:
  b=unbase(r['encodedBase64']);need(0<len(b)==r['encodedBytes']<=1048576 and hashlib.sha256(b).hexdigest()==r['encodedSha256']and fnv(b)==r['encodedFNV1aU32'],'Whole pinned Node encoded input bytes/hash/FNV');streams[r['caseId']]=(r,b)
 facts=[]
 for n,c in enumerate(cases):
  need(c['index']==n and oracle['cases'][n]['caseId']==n and oracle['cases'][n]['caseName']==c['id'],'Exact case association')
  if c['direction']=='encode':b=raw_fixtures[c['fixture']];source='raw-fixture';parent_sha=None
  else:
   s,b=streams[n];need(s['fixture']==c['fixture']and s['format']==c['format']and s['provider']=='node-22.14.0','Exact decoder input association');source='node-oracle-input';parent_sha=s['encodedSha256']
  facts.append(dict(index=n,caseName=c['id'],fixture=c['fixture'],direction=c['direction'],format=c['format'],logicalUncompressedBytes=c['logicalUncompressedBytesPerOperation'],inputBytes=len(b),inputSha256=hashlib.sha256(b).hexdigest(),inputFNV1aU32=fnv(b),inputSource=source,parentDeclaredInputSha256=parent_sha))
 final_counts=dict(publicFunctionEntries=242,perExportEntries=dict(identity=2,setup=30,observe=0,batch=180,checkpoint=30,stage=0,validate=0),codecCalls=0,controlOperations=180)
 arm_reports=[];pids=[];all_terminal_rows=[];all_worker_result_rows=[];all_worker_completion_rows=[]
 for arm,origin in zip(ARMS,parent['origins']):
  need(origin['arm']==arm and origin['component']==prior_contract['requiredComponents'][arm],'Exact fresh arm origin/component')
  ar=OUT/'jobs'/arm;results=doc(origin['result']['path'],origin['result']);done=doc(origin['completion']['path'],origin['completion']);ix=doc(ar/'index.json');ixrow=info(ar/'index.json');all_worker_result_rows.append(origin['result']);all_worker_completion_rows.append(origin['completion'])
  need(done['sourceIndexSha256']==SOURCE and done['component']==origin['component']and done['index']['sha256']==ixrow['sha256']and done['index']['bytes']==ixrow['bytes']and done['results']['sha256']==origin['result']['sha256']and done['results']['bytes']==origin['result']['bytes'],'Current arm index/result/completion tuple')
  need(len(ix['files'])==486 and len({r['path']for r in ix['files']})==486,'Exact486 current arm members')
  for r in ix['files']:read(ar/local(r['path']),r);need(indexed_rows['jobs/'+arm+'/'+r['path']]==dict(path='jobs/'+arm+'/'+r['path'],sha256=r['sha256'],bytes=r['bytes']),'Arm nested index matches outer index')
  need({q.relative_to(ar).as_posix()for q in ar.rglob('*')if q.is_file()}=={r['path']for r in ix['files']}|{'index.json','completion.json'},'Exact488 arm file membership')
  worker_terminal=doc(origin['ownedTerminal']);all_terminal_rows.append(info(origin['ownedTerminal']));pids.append(worker_terminal['pid'])
  for k,v in dict(status=0,signal=None,spawnError=None,timedOut=False,externalSignal=None,outputLimitExceeded=False,closed=True,ownedGroupGone=True,terminalExitZeroObserved=True,errors=[]).items():exact(worker_terminal[k],v,'Actual owned terminal field '+k)
  need(worker_terminal['timeoutMs']==600000 and worker_terminal['maxOutputBytes']==16777216,'Actual operational bounds')
  for name in ['stdout','stderr']:read(worker_terminal[name]['path'],worker_terminal[name])
  need(worker_terminal['stderr']['bytes']==0,'Actual worker stderr empty')
  stdout=parse(read(worker_terminal['stdout']['path']));exact(stdout,dict(index=done['index'],completion=dict(path='completion.json',sha256=origin['completion']['sha256'],bytes=origin['completion']['bytes'])),'Complete actual worker stdout result')
  launch=doc(OUT/'processes'/(arm+'.launch.json'));need(launch['executable']==worker_terminal['executable']and launch['args']==worker_terminal['args'],'Actual launch/terminal command tuple')
  need(launch['args'][0]==str(D/'worker.mjs'),'Exact unchanged worker used')
  private_row=parse(launch['args'][1]);private=doc(private_row['path'],private_row);need(private_row==info(OUT/'descriptors'/(arm+'.json')),'Exact new private descriptor')
  need(private['controlSourceIndexSha256']==SOURCE and private['parentOutputRoot']==str(OUT)and private['outputRoot']==str(ar)and private['arm']==arm and len(private['criticalFiles'])==559,'Fresh current source/root/arm/private559 source tuple')
  for r in private['criticalFiles']:read(r['path'],r)
  for name in ['oracle','cases']:read(private[name]['path'],private[name])
  need(private['oracle']==oracle_row and private['artifact']['component']==origin['component'],'Same actual reviewed oracle/component, not relabelled pass')
  for name in ['component','glue','core','dts','wit','transpileMetadata','packageJson']:exact(private['artifact'][name],component_proofs[arm][name],'Same complete artifact '+name)
  started=doc(ar/'started.json');need(started['sourceIndexSha256']==SOURCE and started['component']==origin['component']and started['codecAllowed']is False,'Actual fresh worker start scope')
  need(len(results['records'])==242 and results['controlSourceIndexSha256']==SOURCE and results['arm']==arm and results['component']==origin['component'],'Full242 returned records')
  exact(results['counts'],final_counts,'Final exact per-export counters')
  need(results['generatedModuleImported']is True and results['initializationCompletedByModuleTLA']is True and results['externalWasiImports']==[]and results['internalCopyOwnershipInspected']is False and results['emptyInputIsolationClaim']is False and results['timing']is False,'Actual bounded guest import and ownership/timing limits')
  counts=dict(publicFunctionEntries=0,perExportEntries=dict.fromkeys(NAMES,0),codecCalls=0,controlOperations=0);active=None;sequence=[]
  sequence.append(('identity',[],'identity-before',None,None))
  for n in range(30):
   sequence.append(('setup',[n],'setup-'+str(n),n,None))
   for base in [30,60,90]:
    for repeat in range(2):sequence.append(('batch',[base+n,1],'control-'+str(base+n)+'-repeat-'+str(repeat),n,repeat))
   sequence.append(('checkpoint',[],'checkpoint-'+str(n),n,None))
  sequence.append(('identity',[],'identity-after',None,None))
  def state():return dict(activeCaseId=active,inputSource=facts[active]['inputSource']if active is not None else None,stagedValidation=None,prepared=active is not None,retainedUntimedOutput=False)
  def window(n):return dict(byteOffset=8,byteLength=facts[n]['inputBytes'],backingBytes=facts[n]['inputBytes']+16,prefix=[165]*8,suffix=[90]*8,construction='new ordinary ArrayBuffer; fixed/attached/unshared by construction')
  for seq,(name,args,label,primary,repeat)in enumerate(sequence):
   rec=results['records'][seq];need(rec['exportName']==name and rec['args']==args and rec['label']==label,'Exact complete call order/args '+arm+'/'+str(seq));base=str(seq).zfill(4)+'-'+label
   exact(doc(ar/(base+'-before.json')),dict(schemaVersion=1,exportName=name,args=args,partial=True),'Exact pre-call durable record')
   need(rec['raw']['path']==base+'-raw.json','Raw exact source-derived filename');raw=doc(ar/rec['raw']['path'],rec['raw']);need(set(raw)=={'schemaVersion','exportName','returned','partial'},'Exact raw envelope fields')
   need(raw['schemaVersion']==1 and raw['exportName']==name and raw['partial']is True,'Raw partial flag means durable before later acceptance')
   returned=raw['returned'];need(set(returned)=={'type','value','codeUnits','fullPrimitiveCaptured'}and returned['type']=='string'and returned['fullPrimitiveCaptured']is True and returned['codeUnits']==len(returned['value'].encode('utf-16-le'))//2,'Whole exact primitive string')
   value=parse(returned['value']);exact(value,rec['value'],'Double-decoded raw string equals stored decoded record')
   counts['publicFunctionEntries']+=1;counts['perExportEntries'][name]+=1
   if name=='identity':
    expected=dict(schemaVersion=1,kind='codec-cost-identity-v1',version='bounded-zlib-cost-guest-v1',provider='native'if arm=='native-on'else'fflate',providerSourceVersion='registered-node-zlib-m0.13'if arm=='native-on'else'fflate-browser-0.8.3',oracleSha256=oracle_row['sha256'],primaryCases=30,controlCaseRanges=dict(consumeInput=[30,59],copyInputAndConsume=[60,89],harnessNoCodec=[90,119]),exports=NAMES,snapshotState=dict(prepared=False,staged=False,retainedOutput=False,codecCalls=0,resources=0),counterMeaning='named-function entries including internal validate calls; outer host calls are parent raw records',counters=copy.deepcopy(counts),state=state(),codecPrewarmedAtSnapshot=False)
   elif name=='setup':
    active=primary;f=facts[primary];expected=dict(schemaVersion=1,kind='codec-cost-setup-v1',caseId=primary,caseName=f['caseName'],inputSource=f['inputSource'],input=window(primary),inputFNV1aU32=f['inputFNV1aU32'],parentDeclaredInputSha256=f['parentDeclaredInputSha256'],oracleSha256=oracle_row['sha256'],stagedValidationCleared=True,priorOutputCleared=True,counters=copy.deepcopy(counts),state=state())
   elif name=='batch':
    need(active==primary and rec['primaryCaseId']==primary and rec['controlId']==args[0]and rec['repeat']==repeat,'Exact active setup/control/repetition identity');counts['controlOperations']+=1;f=facts[primary];control='consumeInput'if args[0]<60 else'copyInputAndConsume'if args[0]<90 else'harnessNoCodec'
    control_result=dict(bytesConsumed=0,declaredInputBytes=f['inputBytes'],tag=2166136261,copies=0,codecCalls=0)if control=='harnessNoCodec'else dict(bytesConsumed=f['inputBytes'],fnv=f['inputFNV1aU32'],copies=1 if control=='copyInputAndConsume'else 0,codecCalls=0)
    expected=dict(schemaVersion=1,kind='codec-cost-control-v1',caseId=args[0],primaryCaseId=primary,control=control,operations=1,result=control_result,logicalUncompressedBytes=f['logicalUncompressedBytes'],counters=copy.deepcopy(counts),state=state())
   else:
    before=state();input_record=window(primary)|dict(fnv1aU32=facts[primary]['inputFNV1aU32'],matchesSetupFNV=True,sentinelsUnchanged=True);active=None;expected=dict(schemaVersion=1,kind='codec-cost-checkpoint-v1',before=before,input=input_record,preparedAndStageAndPriorOutputCleared=True,counters=copy.deepcopy(counts),state=state(),gcOrResetInvoked=False)
   exact(value,expected,'Every full public return matches independent expectation '+arm+'/'+str(seq))
   ledger.append(dict(arm=arm,sequence=seq,exportName=name,args=args,primaryCaseId=primary,repeat=repeat,raw=dict(path=str(ar/rec['raw']['path']),sha256=rec['raw']['sha256'],bytes=rec['raw']['bytes']),wholePrimitiveStringDecoded=True,fullPublicDataMatched=True,inputFacts=facts[primary]if primary is not None else None,privateGuestHeapBytesInspected=False))
  exact(counts,final_counts,'Independent final count reconstruction')
  arm_reports.append(dict(arm=arm,pid=worker_terminal['pid'],component=origin['component'],rawReturns=242,setupCases=30,distinctControlCases=90,controlOperations=180,codecCalls=0,perExportEntries=counts['perExportEntries'],ownedRawExitCode=0,ownedGroupGone=True,result=origin['result'],completion=origin['completion'],ownedTerminal=info(origin['ownedTerminal'])))
 need(len(set(pids))==3 and set(pids)=={96940,96961,97099},'Three distinct actual fresh Node workers')
 need(len(ledger)==726 and sum(r['exportName']=='batch'for r in ledger)==540,'All726 returns/540 controls decoded')
 expected_summary=dict(armSessions=3,setupCases=90,distinctControlCases=270,adjacentRepetitions=2,controlOperations=540,rawPrimitiveStringReturns=726,codecCalls=0)
 for k,v in expected_summary.items():exact(parent[k],v,'Exact parent summary '+k)
 # Source-coupled exclusion, not hidden native-global instrumentation.
 guest_source=read(G/'runtime.mjs').decode();start=guest_source.index("if(selected.kind!=='codec')");end=guest_source.index('\n  let aggregateFNV',start);branch=guest_source[start:end]
 need('controls[selected.kind](active.window.input)'in branch and 'controlOperations++'in branch and 'invoke('not in branch and 'provider.methods'not in branch,'Authenticated branch does not call provider workload')
 old_root=doc(root['oldActualV1Failure']['path'],root['oldActualV1Failure']);old_out=Path('/private/tmp/starling-node-compat/zlib-cost-jco-control-correctness-v1');need({q.relative_to(old_out).as_posix()for q in old_out.rglob('*')if q.is_file()}=={'failure.json','descriptors/native-on.json'},'Old failed v1 two-file output preserved')
 for d in old_root['partialFiles']:read(d['path'],d)
 coverage=dict(armSessions=3,freshOwnedWorkers=3,rawPrimitiveStringReturns=726,setupCases=90,distinctControlCases=270,controlOperations=540,consumeInputOperations=180,copyInputAndConsumeOperations=180,harnessNoCodecOperations=180,identityCalls=6,setupCalls=90,batchCalls=540,checkpointCalls=90,observeCalls=0,stageCalls=0,validateCalls=0,codecCalls=0,operationsPerControlBatch=1,adjacentRepetitions=2)
 out=dict(schemaVersion=1,state='INDEPENDENT_ZLIB_COST_JCO_CONTROL_V2_RESULTS_REVIEW_PASSED_V1',verifiedPassed=True,controlSourceIndexSha256=SOURCE,sourceReviewIndexSha256=root['independentSourceReview']['index']['sha256'],priorCorrectnessReviewIndexSha256='e03bb0db65f6009e86a6d55e4553e820d143c702128976efc5ef47e092548083',priorCorrectnessContractSha256='25411f2ecb278c1eeda7b27a0aafa47b29cc3d9a53221a327e9e5c94002936f1',componentSourceIndexSha256='cf3110b3af503fecd2408781a4dcb53b21670b74cd94e3266c4f0b86f795d794',guestSourceIndexSha256='ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8',toolingSourceIndexSha256='ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8',sourcePublicationIndexSha256='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b',oracleSha256=oracle_row['sha256'],rootReceipt=info(root_path),actualIndex=root['index'],actualResult=root['results'],actualCompletion=root['completion'],externalParentTerminal=root['actualParentTerminal'],rootAuthority=root['rootAuthority'],config=root['config'],oracle=oracle_row,coverage=coverage,arms=arm_reports,allRawPrimitiveStringsCompleteAndDecoded=True,allFullPublicReturnExpectationsMatched=True,independentExpectedInputBytesAndFnvComputed=True,sourceCoupledNoProviderWorkloadPathVerified=True,allThreeOwnedWorkersRawZeroClean=True,externalParentExitCode=0,actualIndexedFiles=1480,actualRegularFiles=1482,actualIndexedBytes=2513957,priorControlOperations=0,oldV1FailureAndSourceReviewsUnchanged=True,independentGuestInputHeapInspection=False,internalCopiedBackingInspected=False,globalNativeCodecInstrumentation=False,stockWasmtimeExecuted=False,nodeCodecExecutedByThisAction=False,pilotPrerequisitesSatisfied=False,timingAllowed=False,operationalAdmission=False,runtimeAcceptanceClaim=False,actionAuthorityIssuedByReviewer=False,reviewerReadHashDecodeDataOnly=True,reviewerHelpersPreflightNodeJcoWorkerGuestCodecNativeHostTimingActionsInvoked=False,uniqueInputFilesRehashed=len(seen),limitations=['Public whole-return/control/state/counter correctness only; reported FNV/sentinels are not a private guest-heap byte read.','Copy count is source-coupled observable evidence; internal copied backing is not exposed or inspected.','codecCalls0 combines guest counters and authenticated branch source, not hidden global native instrumentation.','Three guest control kinds atN1 are proved; other future host controls or higherN behavior are not implied.','Parent/child raw0 events are authenticated saved records, not terminals directly observed by this reader.','Old228 correctness/control0 and v1 failure are preserved; neither is relabelled as this new execution.','Source action literal pilotPrerequisitesSatisfied:false remains false. Separate source gates/Root phase/quiet-window authority are required before pilots or timing.','No performance/capacity/heap/GC/root isolation/reset/reuse or operational acceptance claim.'])
 out.update(sourceOnly=False,actualControlWorkloadsExecuted=True,armSessions=3,rawPrimitiveStringReturns=726,controlOperations=540,codecCalls=0,actualOutputRoot=str(OUT),requiredComponents=prior_contract['requiredComponents'],requiredActualComponentReviews=prior_contract['requiredActualComponentReviews'])
 write('per-call-ledger.json',ledger);write('expected-input-facts.json',facts);write('rehashed-inputs.json',[seen[k]for k in sorted(seen)]);write('results.json',out)
 print(json.dumps(dict(state=out['state'],rawReturns=len(ledger),controls=540,files=len(seen))))
if __name__=='__main__':main()
