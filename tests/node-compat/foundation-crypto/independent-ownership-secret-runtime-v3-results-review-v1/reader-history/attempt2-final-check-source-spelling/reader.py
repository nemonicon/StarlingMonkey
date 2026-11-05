"""Independent guarded secret355 Jco runtime DATA only; no producer/crypto execution."""
from pathlib import Path
import ast,collections,copy,hashlib,json,os,stat
P=Path(__file__).resolve().parent;K=P.parent;OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-runtime-v3');S=K/'ownership-secret-runtime-candidate-v3';TAG='b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7';checks=0;seen={};identities={};copies=[]
def need(v,m):
 global checks
 checks+=1
 assert v,m
def ident(p):
 s=p.lstat();need(stat.S_ISREG(s.st_mode),'ordinary input');return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode))
def row(p):
 p=Path(p);a=ident(p)
 if str(p)in seen:need(a==identities[str(p)],'captured identity stable');return seen[str(p)]
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 need(a==ident(p),'stable streamed current file');r=dict(path=str(p),sha256=h.hexdigest(),bytes=a[2]);seen[str(p)]=r;identities[str(p)]=a;return r
def verify(r,label='input'):
 q=row(r['path']);need(all(q[k]==r[k]for k in ['path','sha256','bytes']),'exact '+label);return Path(r['path'])
def data(r,label='DATA'):
 p=verify(r,label);return json.loads(p.read_bytes())
def load(p):return data(row(p))
def local(n):need(type(n)is str and n and not n.startswith('/')and '\\'not in n and '\0'not in n and all(s not in['','.','..']for s in n.split('/')),'confined name');return n
def tree(root,names):
 root=Path(root);actual=set()
 for q in root.rglob('*'):
  need(not q.is_symlink(),'ordinary exact family tree')
  if q.is_file():actual.add(q.relative_to(root).as_posix())
 need(actual==set(names),'whole tree membership')
def index(r,extras=()):
 x=data(r,'index');need(x['schemaVersion']==1 and 0<len(x['files'])<=2048,'finite indexed members');rows=[];names={'index.json',*extras};base=Path(r['path']).parent
 for m in x['files']:
  n=local(m['path']);need(n not in names,'unique member');names.add(n);d=dict(m,path=str(base/n));verify(d,'indexed file');rows.append(d)
 tree(base,names);return x,rows
def proof(pair):
 _,rows=index(pair['index']);need(pair['result']in rows,'result indexed exactly once');return data(pair['result'])
def descriptors(v):
 if isinstance(v,dict):
  if set(v)=={'path','sha256','bytes'}:yield v
  else:
   for x in v.values():yield from descriptors(x)
 elif isinstance(v,list):
  for x in v:yield from descriptors(x)
def exact(a,b,label):
 need(type(a)is type(b),label+' exact type')
 if isinstance(b,dict):
  need(set(a)==set(b),label+' exact keys')
  for k in b:exact(a[k],b[k],label+'.'+k)
 elif isinstance(b,list):
  need(len(a)==len(b),label+' exact list length')
  for n,(x,y)in enumerate(zip(a,b)):exact(x,y,label+'['+str(n)+']')
 else:need(a==b,label+' exact value')
def save(n,v):
 q=P/n;need(not q.exists(),'new reviewer output only');q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(v,indent=2)+'\n')
def absolute(base,d):return dict(d,path=str(base/d['path']))
root_row=dict(path=str(K/'ownership-secret-runtime-v3-root-results.json'),sha256='50ba6dd0dcf10119b631e7449ba19f2870186770abe2d20a84a931583c5348fa',bytes=5419);root=data(root_row);SOURCE=root['sourceIndex']['sha256'];need(SOURCE=='1f357d3a2513fc8a823db4c770963bb5638783f61918ce6f68fa3c3d940ff24c','actual new V3 source')
for r in descriptors(root):verify(r,'actual Root binding')
_,source_rows=index(root['sourceIndex']);refs=load(S/'references.json');inputs=load(S/'source-inputs.json');need(len(inputs['files'])==34167 and len(inputs['modeRows'])==34167 and len(inputs['families'])==35,'actual complete V3 declared protection34167/35')
for r in inputs['files']:verify(r,'entire Source/native/frozen/package/proof protection')
for r in inputs['modeRows']:need(ident(Path(r['file']['path']))[5]==r['mode'],'all protected input modes')
for r in inputs['families']:index(r)
for t in inputs['historicalDonorTrees']:tree(t['root'],t['names'])
peer=proof(root['sourcePeer']);need(peer['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_RUNTIME_SOURCE_REVIEW_PASSED_V3'and peer['sourceIndexSha256']==SOURCE and peer['sourceOnly']is peer['sourceReviewPassed']is True and peer['ownerActionsInvoked']is peer['hostActionsInvoked']is peer['runtimeActionsInvoked']is False,'actual independent V3 Source peer')
A=data(root['rootAuthority']);cfg=data(root['rootConfig']);need(cfg['state']=='SECRET355_NORMAL_RUNTIME_CONFIG_V3'and cfg['sourceIndex']==root['sourceIndex']and cfg['rootAuthority']==root['rootAuthority'],'whole actual Source/config/authority context')
need(A['state']=='ROOT_REVIEWED_SECRET355_NORMAL_RUNTIME_V3'and A['phase']=='guarded-normal-runtime'and A['sourceIndex']==root['sourceIndex']and A['sourceIndependentReview']==root['sourcePeer']and A['entry']in source_rows and A['externalController']in source_rows,'actual V3 entry/Root/peer ownership')
for k in ['runtimeWorkloadAllowed','nodeOracleAllowed','retainedReadOnlyApiAllowed','guardedPrototypeCase3Allowed']:need(A[k]is True,'actual finite permit '+k)
for k in ['originalOneShotApiAllowed','originalHelperAllowed','historicalCallableAllowed','nativeBuildAllowed','nativeFreezeAllowed','componentBuildAllowed','gcAllowed','gcPressureAllowed','oomAllowed','faultInjectionAllowed','unsafeResetAllowed','wasmtimeAllowed','otherVariantsAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:need(A[k]is False,'closed other phase '+k)
need(A['actualRuntimeReview']is None and A['nativeSourceFiles']==355 and A['externalEmbeddingSources']==3 and A['fullMetadataFields']==75 and A['selectedManifestCount']==11 and A['variant']=='normal-off','real355/3/75/11 context')
need(A['outputRoot']==str(OUT)and A['externalParentDeadlineSeconds']==2400 and A['workerTimeoutMs']==600000 and A['scenarios']==['retained','fresh','wrapper'],'fixed actual bounded schedule')
art=proof(A['actualArtifactReview']);contract=data(A['actualArtifactContract']);need(art['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_COMPONENT_V2_ARTIFACT_REVIEW_PASSED_V1'and art['verifiedPassed']is True and art['componentSha256']==A['componentSha256']=='c067000d2612088ce430be124de0efeccd4ba12d287b858d9aca2a429c425f30'and art['engineSha256']==A['engineSha256']=='901c7ba55cf48d0dc2b74e6a8f75f41d215a95946aeb89afcf592d576b60a1a7','actual c067/901 component/native')
for k,v in contract['requiredFixedValues'].items():exact(art[k],v,'actual component proof '+k)
exact(art['artifacts'],contract['artifacts'],'complete actual artifact map');exact(art['artifacts'],refs['artifacts'],'exact runtime component artifact map');need(art['emittedImports']==[]and sorted(art['publicAbiFunctions'])==['clear','inspect','run','validate'],'four zero-import scalar functions')
for r in refs['artifacts'].values():verify(r,'actual unchanged loading artifact')
metadata=data(refs['metadata']);need(len(metadata)==75 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3,'whole raw75 original metadata')
# Frame/API DATA is retained separately from callable. Recheck current protections,
# never replay historical helpers or deserialize a function as executable authority.
original=load(Path(refs['actualRetainedRecordData']['path']));record=load(OUT/'retained-record-data.json');shape=load(OUT/'retained-record-shape.json');exact(record,original,'complete actual retained record versus genuine prior record DATA')
need(len(record['historicalBootstrap'])==41 and len(record['historicalBootstrap']['metadata'])==75 and len(record['historicalBootstrap']['selectedManifests'])==11,'whole41-field historical bootstrap plus11 manifests')
need(record['historicalBootstrap']['metadata']==metadata and record['historicalBootstrap']['engine']==refs['engine'],'actual original metadata/native frame no role projection')
for k in ['helperInvocations','originalApiInvocations','historicalRecheckInvocations','processesSpawned','filesCreated']:need(record['currentVerification'][k]==0,'readonly scope current zero '+k)
need(record['currentVerification']['protectedFileRows']==28256 and record['currentVerification']['retainedTreeScopes']==8,'whole current API verification shape')
expected_shape={k:dict(type=('number'if k=='schemaVersion'else'string'if k=='kind'else'object'),writable=False,configurable=False,enumerable=True)for k in record};expected_shape['recheck']=dict(type='function',writable=False,configurable=False,enumerable=True);exact(shape,expected_shape,'whole genuine frozen data/callable property descriptors; no callable serialization')
ix,rows=index(root['actualRuntimeIndex'],extras=('completion.json',));need(len(rows)==54,'actual54 indexed members');by={str(Path(r['path']).relative_to(OUT)):r for r in rows};need(len(by)==54,'all actual member roles unique')
result=data(root['actualRuntimeResults']);completion=data(root['actualRuntimeCompletion']);need(absolute(OUT,completion['index'])==root['actualRuntimeIndex']and absolute(OUT,completion['result'])==root['actualRuntimeResults'],'whole actual parent completion')
need(result['sourceIndexSha256']==SOURCE and result['rootAction']==root['rootAuthority']and result['component']==refs['artifacts']['component']and result['finalProtectionErrors']==[],'actual parent Source/Root/component/final checks')
node_oracle_row=by['node-oracle.json']
"""Pure independent typed DATA model from prior independent reader; no crypto computation."""
algorithm=dict(name='HMAC',hash=dict(name='SHA-256'),length=160)
expected_oracle=dict(schemaVersion=1,node='v22.14.0',tagHex=TAG,keys=[dict(format=f,type='secret',extractable=f=='jwk',algorithm=algorithm,usages=['sign','verify'],tagHex=TAG,valid=True,invalid=False)for f in ['raw','jwk']],hostTestOracleOnly=True,guestNodeCryptoExportsAdded=False)
oracle=data(node_oracle_row,'actual-host-Node-oracle');exact(oracle,expected_oracle,'whole actual Node22 oracle')
need(len(bytes.fromhex(TAG))==32,'full32-byte known-answer constant retained; no HMAC computed by reviewer')
INITIAL=dict(keyImportsAttempted=0,signCalls=0,verifyCalls=0,retainedKeys=0,pendingOperations=0)
def zero():return dict(inspectCalls=0,runCalls=0,clearCalls=0,validateCalls=0,keyImportsAttempted=0,keyImportsFulfilled=0,signCalls=0,verifyCalls=0)
def state(raw=False,jwk=False):return dict(rawRetained=raw,jwkRetained=jwk,strongApplicationKeyOwners=int(raw)+int(jwk),pendingOperationsInstrumented=False,finalizersOrWipesObserved=False)
def key(extractable):return dict(instanceOfGlobalCryptoKey=True,globalConstructorStable=True,type='secret',extractable=extractable,algorithm=algorithm,usages=['sign','verify'])
def operation(extractable):
 return dict(key=key(extractable),firstSignatureHex=TAG,secondSignatureHex=TAG,signatureBytes=32,priorFullBytesStable=True,independentNonemptyBacking=True,mutationRestored=True,valid=True,invalid=False,inputBeforeHex='a5'*8+'4869205468657265'+'a5'*8,inputAfterHex='a5'*8+'4869205468657265'+'a5'*8,inputWindow=dict(byteOffset=8,byteLength=8,backingBytes=24),signatureBeforeHex='a5'*8+TAG+'a5'*8,signatureAfterHex='a5'*8+TAG+'a5'*8)
def error(message):return dict(thrownType='object',typeError=True,name='TypeError',message=message)
def refusal(which):return dict(kind='native-promise-rejection',error=error('crypto.subtle.'+which+': key must be a CryptoKey object'))
READS=dict(algorithmName=0,dataByteLength=0,dataPrimitive=0,dataString=0,signatureByteLength=0,signaturePrimitive=0)
def guard_result():
 return dict(signRefusal=refusal('sign'),verifyRefusal=refusal('verify'),signConversionReads=READS,verifyConversionReads=READS,positiveAlgorithmReads=1,positiveVerifyAlgorithmReads=1,positiveFullSignatureHex=TAG,ordinaryInvalid=refusal('sign'),getters=[dict(name=n,error=error("Method '"+n+" get' called on receiver that's not an instance of CryptoKey"))for n in ['algorithm','extractable','type','usages']],constructorError=error("CryptoKey builtin can't be instantiated directly"),onlyNewGuardedArtifactAllowed=True,uniqueNativeErrorCauseInferred=False)
def obs_call(name,value):return [dict(operation=name,phase='before',returned=dict(type='undefined')),dict(operation=name,phase='returned',returned=value)]
TAG_RETURN=dict(type='ArrayBuffer',bytes=32,fullHex=TAG,fullBytesRetained=True)
def exercise_observations():return obs_call('sign',TAG_RETURN)+obs_call('sign',TAG_RETURN)+obs_call('verify',dict(type='boolean',value=True))+obs_call('verify',dict(type='boolean',value=False))
def next_run(c,id):
 c=copy.deepcopy(c);c['runCalls']+=1
 if id<2:c['keyImportsAttempted']+=1;c['keyImportsFulfilled']+=1;c['signCalls']+=2;c['verifyCalls']+=2
 elif id==2:c['signCalls']+=4;c['verifyCalls']+=4
 else:c['signCalls']+=3;c['verifyCalls']+=2
 return c
def run_record(id,c):
 if id==0:res=dict(format='raw',importInputPreserved=True,callerKeyBytesChangedAfterImport=True,callerBackingHex='a5'*8+'00'*20+'a5'*8,operations=operation(False));obs=obs_call('importKey',dict(type='object',opaque=True,fullOpaqueValueClaim=False))+exercise_observations()
 elif id==1:res=dict(format='jwk',importInputPreserved=True,callerJwkChangedAfterImport=True,operations=operation(True));obs=obs_call('importKey',dict(type='object',opaque=True,fullOpaqueValueClaim=False))+exercise_observations()
 elif id==2:res=dict(format='retained-pair',raw=operation(False),jwk=operation(True),strongApplicationOwners=True);obs=exercise_observations()+exercise_observations()
 else:
  res=guard_result();obs=[dict(operation='prototype-sign',phase='returned',record=refusal('sign'),reads=READS),dict(operation='prototype-verify',phase='returned',record=refusal('verify'),reads=READS)]+obs_call('sign',TAG_RETURN)+obs_call('verify',dict(type='boolean',value=True))+[dict(operation='ordinary-invalid-key',phase='returned',record=refusal('sign'))]
 return dict(schemaVersion=1,kind='crypto-owner-run-v1',caseId=id,completed=True,result=res,observations=obs,initial=INITIAL,counters=c,state=state(True,id!=0 or c['keyImportsFulfilled']>1),gcOrEntropyRequested=False,finalizerCountOrWipeProof=False)
def inspect_record(c):return dict(schemaVersion=1,kind='crypto-owner-inspect-v1',initial=INITIAL,counters=copy.deepcopy(c),state=state(),globalCryptoKeyInstalled=True,constructorStable=True,cryptoOperationsAtSnapshot=0,fullNativeOwnershipOrZeroizationObserved=False)
def clear_record(c):return dict(schemaVersion=1,kind='crypto-owner-clear-v1',initial=INITIAL,counters=copy.deepcopy(c),state=state(),applicationReferencesReleased=True,collectionOrNativeFreeOrWipeObserved=False)
def expectations(scenario):
 c=zero();calls=[]
 if scenario=='wrapper':
  entry=zero();c['validateCalls']+=1;c['inspectCalls']+=1;before=inspect_record(c);records=[]
  for id in range(4):c=next_run(c,id);records.append(run_record(id,copy.deepcopy(c)))
  c['clearCalls']+=1;released=clear_record(c);c['inspectCalls']+=1;after=inspect_record(c)
  value=dict(schemaVersion=1,kind='crypto-owner-within-export-validation-v1',entryCounters=entry,entryState=state(),before=before,records=records,released=released,after=after,withinOneOuterExport=True,separateHostCallInterleavingProved=False,finalizerOrWipeObserved=False)
  return [('validate',[],value)],c
 c['inspectCalls']+=1;calls.append(('inspect',[],inspect_record(c)))
 for rotation in range(3 if scenario=='retained'else 1):
  for id in range(4):c=next_run(c,id);calls.append(('run',[id],run_record(id,copy.deepcopy(c))))
 c['clearCalls']+=1;calls.append(('clear',[],clear_record(c)));c['inspectCalls']+=1;calls.append(('inspect',[],inspect_record(c)))
 return calls,c
def decode_public(s):
 def unique(pairs):
  d={}
  for k,v in pairs:need(k not in d,'no duplicate public JSON field');d[k]=v
  return d
 return json.loads(s,object_pairs_hook=unique,parse_constant=lambda s:(_ for _ in()).throw(AssertionError('nonfinite public value')))
ledger=[];all_runs=[];summaries=[];terminals=[];observed=collections.Counter()
need([s['scenario']for s in result['sessions']]==['retained','fresh','wrapper'],'whole ordered sessions')
for session in result['sessions']:
 scenario=session['scenario'];expected,final=expectations(scenario);base=OUT/scenario;_,members=index(by[scenario+'/index.json'],extras=('completion.json',));need(len(members)==len(expected)+3,'all raw/result/fullrecord/shape worker-indexed')
 need({Path(r['path']).relative_to(base).as_posix()for r in members}=={f'raw/{n:03d}.json'for n in range(1,len(expected)+1)}|{'results.json','retained-record-data.json','retained-record-shape.json'},'exact current worker membership')
 wc=data(by[scenario+'/completion.json']);need(wc['scenario']==scenario and wc['state']=='SECRET355_NORMAL_WORKER_COMPLETE_EXTERNAL_EXIT_ZERO_REQUIRED_V3'and absolute(base,wc['index'])==by[scenario+'/index.json']and absolute(base,wc['result'])==session['result'],'whole worker completion bindings')
 exact(data(by[scenario+'/retained-record-data.json']),record,'whole per-worker actual readonly record DATA');exact(data(by[scenario+'/retained-record-shape.json']),shape,'whole per-worker record descriptor shape')
 wr=data(session['result']);expected_result=dict(schemaVersion=1,state='SECRET355_NORMAL_SESSION_COMPLETE_EXTERNAL_ZERO_REQUIRED_V3',scenario=scenario,sourceIndexSha256=SOURCE,component=refs['artifacts']['component'],publicStringReturns=len(expected),rawCallAttempts=len(expected),rawRecordsWritten=len(expected),finalCounters=final,allCompletePublicChecksPassed=True,fullRawBeforeAssertions=True,generatedModuleImported=True,asyncGuestScalarObservedAsOrdinaryString=True,onlyNewGuardedSecret355Component=True,applicationReferencesReleased=True,nativeFreeOrWipeOrIsolatedRootObserved=False,resetOrRequestReuseClaim=False,gcOrOomOrFaultOrPressureExecuted=False,finalProtectionErrors=[],operationalAdmission=False,runtimeAcceptanceClaim=False);exact(wr,expected_result,'whole complete worker result '+scenario)
 t=data(session['terminal']);terminals.append(t)
 for k,v in dict(schemaVersion=1,name=scenario,executable=refs['node']['path'],status=0,signal=None,spawnError=None,timedOut=False,timeoutMs=600000,externalSignal=None,signalCount=0,outputLimitExceeded=False,maxOutputBytes=16777216,signals=[],errors=[],closed=True,ownedGroupGone=True,terminalExitZeroObserved=True,validationCompleted=False,runtimeAcceptanceClaim=False).items():exact(t[k],v,'actual owned worker '+scenario+' '+k)
 exact(t['args'],[str(S/'entry.mjs'),'worker',json.dumps(root['rootConfig'],separators=(',',':')),scenario],'genuine actual own entry/config/scenario argv')
 launch=data(by['processes/'+scenario+'.launch.json']);need(launch['executable']==t['executable']and launch['args']==t['args']and launch['timeoutMs']==600000 and launch['maxOutputBytes']==16777216 and launch['detachedOwnedSession']is True and launch['completed']is False,'actual pre-call launch historical record')
 for k in ['stdout','stderr']:verify(t[k],'full actual worker '+k)
 need(t['stderr']['bytes']==0,'worker stderr empty');exact(json.loads(Path(t['stdout']['path']).read_bytes()),dict(root=str(base),publicStringReturns=len(expected)),'whole worker stdout')
 for n,(name,args,value)in enumerate(expected,1):
  rr=by[f'{scenario}/raw/{n:03d}.json'];raw=data(rr,'complete actual typed return');need(set(raw)=={'schemaVersion','name','args','kind','observed'},'complete new V3 typed carrier')
  exact({k:v for k,v in raw.items()if k!='observed'},dict(schemaVersion=1,name=name,args=args,kind='return'),'exact typed call/arguments/order')
  need(set(raw['observed'])=={'type','value'}and raw['observed']['type']=='string'and type(raw['observed']['value'])is str,'actual ordinary string, no coercion/await/opaque substitute')
  string=raw['observed']['value'];need(len(string)<=2097152 and string.isascii(),'complete bounded actual ASCII fixture output');decoded=decode_public(string);exact(decoded,value,'every full typed public field '+scenario+'/'+str(n));runs=[decoded]if name=='run'else decoded['records']if name=='validate'else[];all_runs+=runs;ledger.append(dict(scenario=scenario,ordinal=n,name=name,args=args,raw=rr,wholeStringSha256Utf8=hashlib.sha256(string.encode()).hexdigest(),utf8Bytes=len(string.encode()),decoded=decoded,wholeIndependentModelMatched=True))
 summaries.append(dict(scenario=scenario,pid=t['pid'],rawPublicStrings=len(expected),caseRecords=12 if scenario=='retained' else 4,finalCounters=final,result=session['result'],terminal=session['terminal'],index=by[scenario+'/index.json'],completion=by[scenario+'/completion.json']))
for r in all_runs:
 observed['runRecords']+=1
 for o in r['observations']:
  if o['phase']=='returned'and o['operation']=='sign':exact(o['returned'],TAG_RETURN,'whole sign observation full32bytes');observed['full32ByteSignatures']+=1
  if o['phase']=='returned'and o['operation']=='verify':observed['verificationBooleans']+=1;observed['verifyTrue'if o['returned']['value']else'verifyFalse']+=1
  if o['operation']in ['prototype-sign','prototype-verify','ordinary-invalid-key']:observed['nativePromiseTypeErrorRefusals']+=1
  if o['phase']=='returned'and o['operation']=='importKey':observed['keyImportReturns']+=1
 if r['caseId']==3:observed['prototypeGetterRefusals']+=len(r['result']['getters']);observed['noConstructorRefusals']+=1
 # Named signature fields duplicate captured returns; neither is an extra call.
 def sigs(v):
  if isinstance(v,dict):
   for k,x in v.items():
    if k in ['firstSignatureHex','secondSignatureHex','positiveFullSignatureHex']:need(x==oracle['tagHex']==TAG and len(bytes.fromhex(x))==32,'all complete named32byte signature fields');observed['namedSignatureFields']+=1
    sigs(x)
  elif isinstance(v,list):
   for x in v:sigs(x)
 sigs(r)
coverage=dict(rawPublicStrings=len(ledger),caseRecords=len(all_runs),guestKeyImports=sum(s['finalCounters']['keyImportsFulfilled']for s in summaries),guestSignAttempts=sum(s['finalCounters']['signCalls']for s in summaries),guestVerifyAttempts=sum(s['finalCounters']['verifyCalls']for s in summaries),successfulFullGuestTagsCompared=observed['full32ByteSignatures'],namedSignatureFields=observed['namedSignatureFields'],verificationBooleans=observed['verificationBooleans'],verifyTrue=observed['verifyTrue'],verifyFalse=observed['verifyFalse'],nativePromiseTypeErrorRefusals=observed['nativePromiseTypeErrorRefusals'],prototypeGetterRefusals=observed['prototypeGetterRefusals'],noConstructorRefusals=observed['noConstructorRefusals'])
exact(coverage,dict(rawPublicStrings=23,caseRecords=20,guestKeyImports=10,guestSignAttempts=55,guestVerifyAttempts=50,successfulFullGuestTagsCompared=45,namedSignatureFields=45,verificationBooleans=45,verifyTrue=25,verifyFalse=20,nativePromiseTypeErrorRefusals=15,prototypeGetterRefusals=20,noConstructorRefusals=5),'independently derived finite full coverage')
need(len(terminals)==3 and len({x['pid']for x in terminals})==3,'three fresh owned workers')
expected_parent=dict(schemaVersion=1,state='SECRET355_NORMAL_RUNTIME_COMPLETE_UNREVIEWED_V3',sourceIndexSha256=SOURCE,rootAction=root['rootAuthority'],component=refs['artifacts']['component'],nodeOracle='node-oracle.json',sessions=result['sessions'],publicStringReturns=23,guestCaseRecords=20,guestKeyImports=10,guestSignAttempts=55,guestVerifyAttempts=50,successfulGuestSignatureFullBytesCompared=45,normalOnly=True,generatedModuleImported=True,threeFreshOwnedNodeProcesses=True,fullRawPublicReturnsRetainedBeforeAssertions=True,wasmtimeExecuted=False,gcOrOomOrFaultOrPressureOrResetExecuted=False,nativeFreeOrWipeOrIsolatedRootObserved=False,finalProtectionErrors=[],operationalAdmission=False,runtimeAcceptanceClaim=False);exact(result,expected_parent,'whole actual parent result')
T=data(root['ownedNodeTerminal']);ext=Path(root['ownedNodeTerminal']['path']).parent;need(T['pid']==22906 and T['rawExitCode']==0 and T['parentOwnedGroupGone']is T['allObservedOwnedGroupsGone']is True and T['timeout']is T['forcedCleanup']is False,'actual parent raw0/clean groups')
for k in ['remainingObservedPids','signals','errors','interruptedSignals']:need(T[k]==[],'parent clean '+k)
need(T['authority']==root['rootAuthority'],'parent authority descriptor')
for k in ['stdout','stderr']:verify(T[k],'complete parent raw stream')
pids=[22906]+[t['pid']for t in terminals];exact([p['pid']for p in T['observedProcesses']],pids,'whole ordered observed parent/worker PIDs');need(all(p['command']==refs['node']['path']and p['pgid']==p['pid']for p in T['observedProcesses']),'four pinned Node POSIX groups, no Wasmtime')
exact(T['finalGroups'],[dict(pgid=p,alive=False,signalAllowed=False)for p in pids],'all four groups gone without signals')
events=[load(p)for p in sorted(ext.glob('owned-*.json'))];exact([v['sequence']for v in events],list(range(4)),'whole owned journal order');exact([v['process']for v in events],T['observedProcesses'],'complete actual ownership identity records');tree(ext,['started.json','terminal.json','stdout.log','stderr.log',*[f'owned-{n:04d}.json'for n in range(4)]])
started=load(ext/'started.json');need(started['pid']==22906 and started['timeoutSeconds']==2400 and started['authority']==root['rootAuthority'],'actual outer Node cap/authority');exact(started['argv'],[refs['node']['path'],str(S/'entry.mjs'),'parent',json.dumps(root['rootConfig'],separators=(',',':'))],'whole exact pinned parent argv')
lines=[decode_public(s)for s in Path(T['stdout']['path']).read_text().splitlines()];need(len(lines)==20 and T['stderr']['bytes']==0,'whole parent19heartbeat+completion rawstdout and empty stderr')
for scenario,count in [('retained',6),('fresh',6),('wrapper',7)]:
 h=[x for x in lines[:-1]if x.get('name')==scenario];need(len(h)==count,'whole operational heartbeat count '+scenario)
 for x in h:need(set(x)=={'event','name','elapsedMs','stdoutBytes','stderrBytes','partialObservationOnly'}and x['event']=='secret355-normal-operational-heartbeat'and x['stdoutBytes']==x['stderrBytes']==0 and x['partialObservationOnly']is True,'complete unmodified operational partial heartbeat')
 need(all(a['elapsedMs']<b['elapsedMs']for a,b in zip(h,h[1:])),'ordered operational heartbeat timestamps')
exact(lines[-1],dict(root=str(OUT),index=completion['index'],completion=dict(path='completion.json',sha256=root['actualRuntimeCompletion']['sha256'],bytes=root['actualRuntimeCompletion']['bytes'])),'whole final Node parent return')
parentlines=[json.loads(s)for s in Path(root['parentStdout']['path']).read_text().splitlines()];need(len(parentlines)==2 and parentlines[0]==dict(pid=22906,timeoutSeconds=2400)and parentlines[1]==root['actualReturnEnvelope']and root['parentStderr']['bytes']==0,'whole separate Root caller launch+return JSONL')
env=data(root['environmentPolicy']);exact(env,dict(selectedEnvironment=refs['requiredPackagingEnvironment'],removedNames=[],homeValuesPreserved=True,wholeEnvironmentRetained=False),'Root names/selected2env scope only')
need(root['toolObservation']==dict(sessionId=37217,rawExitCode=0,kind='Actual exec-command terminal observation'),'actual Root-reported tool terminal; no invented extra process')
# Current full physical package protection: every4934 file and22link, not a loader call.
pm=load(Path(refs['packagingMap']['path']));pack=Path(pm['publicationRoot']);need(pack.stat().st_dev==pm['rootIdentity']['device']and pack.stat().st_ino==pm['rootIdentity']['inode']and stat.S_IMODE(pack.stat().st_mode)==0o700,'original package root current identity/mode')
files={r['path']:r for r in pm['files']};links={r['destination']:r for r in pm['links']};pf=set();pl=set()
for prefix in pm['roleRoots']:
 for p in(pack/prefix).rglob('*'):
  n=p.relative_to(pack).as_posix();s=p.lstat()
  if p.is_symlink():need(n in links and os.readlink(p)==links[n]['newLinkText']and p.resolve()==pack/links[n]['mappedTarget'],'actual original package link');pl.add(n)
  elif p.is_dir():need(stat.S_IMODE(s.st_mode)==0o700,'package directory modes')
  else:r=files[n];need(s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['mode'],'package regular inode/mode');verify(dict(path=str(p),sha256=r['sha256'],bytes=r['bytes']));pf.add(n)
need(pf==set(files)and pl==set(links)and len(pf)==4934 and len(pl)==22,'whole current package4934+22')
# Inspect actual module assignments/caller/callee without importing producer code.
ast.parse(verify(A['externalController']).read_text());external=Path(A['externalController']['path']).read_text();need("OWN=REPO/'tests/node-compat/foundation-crypto/ownership-secret-runtime-candidate-v3'"in external and 'Path(__file__).resolve().parent==OWN'in external,'actual correct original V3 external constant/path guard')
body=(S/'runtime-body.mjs').read_text();loading=(S/'loading.mjs').read_text();need("const namespace=await import(pathToFileURL(captured.rows.glue.path))"in loading and 'return namespace[name](...args)'in loading,'actual ESM/TLA real direct scalar invoke Source')
need(body.index("await write('raw/'")<body.index("need(typeof value==='string'")and "if(thrown)throw value"in body and 'await frame.recheck()'in body,'raw before assertions, original-throw and final protection Source')
need("const oracle=await nodeOracle();await out.write('node-oracle.json'"in body,'actual retained host oracle produced in parent; no reviewer oracle computation')
# Retain all actual raw records, frames, terminal/stream/caller bytes independently.
def retain(p,n):
 p=Path(p);a=row(p);q=P/'raw-evidence'/n;need(not q.exists(),'fresh independent copy');q.parent.mkdir(parents=True,exist_ok=True)
 with q.open('xb')as f:f.write(p.read_bytes());f.flush();os.fsync(f.fileno())
 os.chmod(q,0o600);b=row(q);need(a['bytes']==b['bytes']and a['sha256']==b['sha256']and ident(p)[:2]!=ident(q)[:2],'whole independently retained bytes');copies.append(dict(original=a,copy=b,distinctInode=True))
for name,base in [('actual',OUT),('external',ext),('caller',Path(root['parentStdout']['path']).parent)]:
 for p in sorted(base.rglob('*')):
  if p.is_file():retain(p,Path(name)/p.relative_to(base))
for r in [root_row,root['rootAuthority'],root['rootConfig'],root['invocation']]:retain(r['path'],Path('root')/Path(r['path']).name)
for p,i in list(identities.items()):need(ident(Path(p))==i,'independent current identity final bookend')
inputs_ledger=[seen[k]for k in sorted(seen)if not Path(k).is_relative_to(P)]
save('input-hashes.json',dict(schemaVersion=1,files=inputs_ledger));save('raw-copy-map.json',dict(schemaVersion=1,files=copies,allWholeBytes=True,allIndependentCopyInodes=True));save('per-call-ledger.json',dict(schemaVersion=1,calls=ledger,wholeTypedValuesChecked=True,allFullFieldsMatchIndependentModel=True));save('semantic-coverage.json',dict(schemaVersion=1,coverage=coverage,sessions=summaries,nodeOracle=oracle,fullTagHex=TAG,tagBytes=32,reviewerCryptoOrOracleInvoked=False))
model_donor=K/'independent-ownership-runtime-v1-results-review-v1/reader.py';save('reader-provenance.json',dict(schemaVersion=1,independentSemanticModelDonor=row(model_donor),pureModelCopy=row(P/'semantic-model.py'),sourceRole='Pure independent DATA model only; no owner helpers imported or executed',newCarrierAndActualSourcesIndependentlyValidated=True))
fixed=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_NORMAL_RUNTIME_RESULTS_REVIEW_PASSED_V1',verifiedPassed=True,sourceIndexSha256=SOURCE,componentSha256=A['componentSha256'],engineSha256=A['engineSha256'],nativeSourceFiles=355,externalEmbeddingSources=3,fullMetadataFields=75,selectedManifestCount=11,rawPublicStrings=23,caseRecords=20,guestKeyImports=10,guestSignAttempts=55,guestVerifyAttempts=50,successfulFullGuestTagsCompared=45,threeFreshOwnedNodeProcesses=True,allFourCasesReviewed=True,allRawTypedBeforeAssertionsReviewed=True,allSourceNativeApiPackageProtectionReviewed=True,generatedModuleImported=True,rootHostNodeOracleExecuted=True,stockWasmtimeExecuted=False,publicGcPressureFixtureExecuted=False,actualNativeGcCountObserved=False,requestOrProcessReuseClaim=False,nativeFreeOrWipeOrIsolatedRootObserved=False,operationalAdmission=False,runtimeAcceptanceClaim=False,reviewerOracleApiGeneratedModuleGuestOrHostActionsInvoked=False)
direct=dict(actualIndex=root['actualRuntimeIndex'],actualResults=root['actualRuntimeResults'],actualCompletion=root['actualRuntimeCompletion'],rootAuthority=root['rootAuthority'],rootConfig=root['rootConfig'],rootObservation=root_row,externalParentTerminal=root['ownedNodeTerminal'],nodeOracle=node_oracle_row,rawWrapper=by['wrapper/raw/001.json'],fullRetainedRecordData=by['retained-record-data.json'],fullRetainedRecordShape=by['retained-record-shape.json'],sourceIndex=root['sourceIndex'],sourcePeer=root['sourcePeer'],actualArtifactReview=A['actualArtifactReview'],actualArtifactContract=A['actualArtifactContract'],inputHashes=row(P/'input-hashes.json'),rawCopyMap=row(P/'raw-copy-map.json'))
coverage.update(actualIndexedFiles=54,actualRegularFiles=56,ownedNodeProcesses=4,ownedGroups=4,sourceProtectedFiles=34167,sourceProtectedModes=34167,sourceFamilies=35,packageRegularFiles=4934,packageLinks=22,actualRetainedDataFields=6,retainedRecordPropertyDescriptors=7,historicalBootstrapFields=41,currentReadonlyProtectedFiles=28256,currentReadonlyTreeScopes=8,currentActualInputFiles=len(inputs_ledger),rawEvidenceCopies=len(copies))
limits=[
 'Finite ordinary Jco/Node component execution only:23 actual complete scalar strings/20case records across retained15,fresh7,wrapper1. Each full decoded object matched an independently constructed exact typed model;45 complete32-byte signatures match retained actual Node/RFC tag without reviewer crypto computation.',
 'All four guarded cases including case3 prototype/key/constructor TypeError refusals and before-conversion controls are included.55sign/50verify are public guest attempted-call counters;45 successful signature returns and45verify booleans(25true20false) are full observed values. Duplicate named signature/observation fields are not additional operations.',
 'Same module retains public keys across rotations in the retained worker. This is not proof of request/process reuse safety, isolated temporary roots, native handle frees/finalizers/wipes/erasure, allocation fault handling, full algorithms or security completeness. No GC/pressure/OOM/fault/unsafeReset or old unsafe prototype artifact was used.',
 'Full historical41-field bootstrap retains its original engineExecuted:false and historical verifier call counts. Current read-only record API has sixDATA properties plus a fresh own recheck callable descriptor; its zero helper/API/process/write counters describe only current read/hash scope, not the enclosing key-runtime action. No function is serialized as executable authority. Actual runtime imported and executed the reviewed c067 component.',
 'Current complete34167 declared files/modes,35families, historical donor inventory and package4934+22 are independently rehashed. Actual action pre/final protection is supported by reviewed Source control flow, whole returned record DATA, clean0 and no recorded protection errors; no new standalone per-recheck snapshot or full host/environment attestation is invented.',
 'Environment evidence retains only selected2packaging variables, removedNames[] and Root-reported home-preservation flag; whole environment was not retained. Parent PID22906 plus three fresh worker identities/groups have durable clean terminals. Root exec-session37217 raw0 is retained as Root-reported tool observation.',
 'Outer Node stdout has19partial operational heartbeats plus final completion; separate Root caller stdout has2records. Whole streams are retained without parsing away partial evidence. Durations are operational, not benchmarks.',
 'Current Jco Root wasmtimeAllowed:false remains unchanged. No stockWasmtime, fresh host transport, new component construction, runtime adoption or operational admission follows from this DATA proof; a separately reviewed host Source and new Root host authority are required.'
]
save('results.json',{**fixed,**direct,'artifacts':refs['artifacts'],'coverage':coverage,'checks':checks,'sessions':summaries,'allObservedOwnedGroupsGone':True,'rawParentNodeExitCode':0,'rootToolExitCodeReported':0,'actualRetainedReadOnlyApiInvoked':True,'actualOriginalOneShotApiOrHelperInvoked':False,'actualHostAuthority':None,'runtimeAdoptionAuthority':None,'limitations':limits})
save('result-contract.json',dict(schemaVersion=1,requiredReviewState=fixed['state'],requiredFixedValues=fixed,requiredCoverage=coverage,requiredExactDescriptors=direct,artifacts=refs['artifacts'],wholePublicWrapper=expectations('wrapper')[0][0][2],issuesHostOrRuntimeAdoptionAuthority=False,limitationsMustBePreserved=limits))
(P/'README.md').write_text('Independent guarded secret355 runtime V3 DATA review\n\nBounded PASS: all23 complete typed public strings/20case records,45 full signatures, full retained Node oracle, counters/refusals/windows/metadata and actual parent+3fresh workers are verified. Native355+3/75rawfields/11manifests and real c067/901 roles remain unchanged.\n\n'+ '\n\n'.join(limits)+'\n')
save('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_SECRET355_NORMAL_RUNTIME_V3_DATA_REVIEW_V1',result=row(P/'results.json'),contract=row(P/'result-contract.json'),inputHashes=row(P/'input-hashes.json'),rawCopyMap=row(P/'raw-copy-map.json'),reviewerOnlyReadHashPureData=True,noProducerSourceOrOutputsModified=True,operationalAdmission=False))
files=[]
for q in sorted(P.rglob('*')):
 if q.is_file():r=row(q);files.append(dict(r,path=q.relative_to(P).as_posix()))
save('index.json',dict(schemaVersion=1,files=files))
for n in ['index.json','results.json','result-contract.json','receipt.json','input-hashes.json']:print(json.dumps(row(P/n)))
print(json.dumps(dict(sealed=True,members=len(files),checks=checks,inputFiles=len(inputs_ledger),rawCopies=len(copies),reviewerActions=False)))
