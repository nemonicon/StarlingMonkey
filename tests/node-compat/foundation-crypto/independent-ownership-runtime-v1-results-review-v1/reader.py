"""Independent retained-data verification. No crypto/helper/guest calls."""
import collections,copy,datetime,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;K=P.parent
OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-runtime-v1')
SOURCE='4cb0d2c37de4ed4406611e6f5cc415934043d98eb4e5f6512461d55bad349dea'
COMPONENT='842f82e8ae330580bee2d160880b5a3a35aac7c9baf357938814ecf2237a149d'
TAG='b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7'
seen={};checks=0
def need(v,m):
 global checks
 if not v:raise AssertionError(m)
 checks+=1
def row(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def verify(r,role):
 p=Path(r['path']);a=p.stat();need(p.is_file()and not p.is_symlink(),'ordinary input '+str(p));x=row(p);b=p.stat()
 need(all(x[k]==r[k]for k in ['path','sha256','bytes']),'exact bytes '+str(p))
 need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns),'stable read '+str(p))
 if str(p)in seen:need(all(seen[str(p)][k]==r[k]for k in ['path','sha256','bytes']),'consistent shared input');seen[str(p)]['roles'].add(role)
 else:seen[str(p)]={**x,'roles':{role}}
 return x
def data(r,role='data'):verify(r,role);return json.loads(Path(r['path']).read_bytes())
def local(n):need(isinstance(n,str)and n and not n.startswith('/')and '\\'not in n and '\0'not in n and all(s not in ['', '.', '..']for s in n.split('/')),'finite local path');return n
def index(r,count=None):
 x=data(r,'index');need(x['schemaVersion']==1 and isinstance(x['files'],list),'finite indexed source')
 if count is not None:need(len(x['files'])==count,'exact indexed count '+str(count))
 names=set();rows=[]
 for v in x['files']:
  n=local(v['path']);need(n not in names,'unique index member');names.add(n);rr=dict(path=str(Path(r['path']).parent/n),sha256=v['sha256'],bytes=v['bytes']);verify(rr,'indexed-member');rows.append(rr)
 return x,rows
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def exact(a,b,label):
 need(type(a)is type(b),label+' exact type')
 if isinstance(b,dict):
  need(set(a)==set(b),label+' exact keys')
  for k in b:exact(a[k],b[k],label+'.'+k)
 elif isinstance(b,list):
  need(len(a)==len(b),label+' exact array length')
  for i,(x,y)in enumerate(zip(a,b)):exact(x,y,label+'['+str(i)+']')
 else:need(a==b,label+' exact value')

root_row=dict(path=str(K/'ownership-runtime-v1-root-results.json'),sha256='6f6987944516260e701d36e9928faa4fc41e277e152e8ddbc69b11856a56ca95',bytes=7261)
root=data(root_row,'actual-Root-result')
for k in ['sourceIndex','artifactContract','rootAction','config','externalTerminal','externalLaunch','started','externalStdout','externalStderr','index','result','completion','nodeOracle']:verify(root[k],'Root-'+k)
need(root['sourceIndex']['sha256']==SOURCE,'actual source identity')
source_ix,source_rows=index(root['sourceIndex'],22)
source_freeze=data(next(r for r in source_rows if r['path'].endswith('/input-freeze.json')),'complete-original-context-source-manifest')
need(len(source_freeze['files'])==13247,'full13247 source/native/artifact refs')
for r in source_freeze['files']:verify(r,'actual-source-native-tool-artifact-input')
peer_ix,peer_rows=index(root['sourceReview']['index'],9);peer=data(root['sourceReview']['result'],'runtime-source-peer')
need(peer['state']=='INDEPENDENT_CRYPTO_OWNER355_RUNTIME_SOURCE_REVIEW_PASSED_V1'and peer['sourceIndexSha256']==SOURCE and peer['sourceReviewPassed']is True and peer['ownerActionsInvoked']is False,'exact independent runtime source peer')
art_ix,art_rows=index(root['artifactReview']['index'],17);art=data(root['artifactReview']['result'],'actual-component-review');art_contract=data(root['artifactContract'],'actual-component-contract')
need(art['state']=='INDEPENDENT_CRYPTO_OWNER355_COMPONENT_V3_ARTIFACT_REVIEW_PASSED_V1'and art['verifiedPassed']is True and art['componentSha256']==COMPONENT,'actual prior component proof')
need(all(art[k]==v for k,v in art_contract['requiredFixedValues'].items()),'whole prior artifact fixed contract unchanged')
for r in art_contract['artifacts'].values():verify(r,'actual-generated-artifact-native-tuple')
artifact_inputs=data(next(r for r in art_rows if r['path'].endswith('/rehashed-inputs.json')),'full-actual-native-artifact-closure')
for r in artifact_inputs['files']:verify(r,'native-frozen-original-and-packaging-closure')

action=data(root['rootAction'],'actual-normal-only-authority');config=data(root['config'],'actual-Root-config')
need(action['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_NORMAL_RUNTIME_V1'and action['sourceIndexSha256']==SOURCE and action['normalRuntimeAllowed']is True and action['nodeOracleAllowed']is True and action['componentSha256']==COMPONENT,'new normal-key+host-oracle authority/source/component')
for k in ['gcAllowed','oomAllowed','resetAllowed','otherVariantsAllowed','wasmtimeAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim']:need(action[k]is False,'no extra action authority '+k)
need(action['sourceIndependentReview']==root['sourceReview']and action['actualArtifactReview']==root['artifactReview']and action['actualArtifactContract']==root['artifactContract'],'Root exact source/artifact prerequisites')
need(config['sourceIndexSha256']==SOURCE and config['rootAction']==root['rootAction'],'actual private config')
terminal=data(root['externalTerminal'],'external-parent-terminal')
need(terminal['pid']==9872 and terminal['rawExitCode']==0 and terminal['timeout']is False and terminal['parentOwnedGroupGone']is True and terminal['deadlineSeconds']==2400,'external raw0/clean/whole-parent bound')
for k in ['stdout','stderr']:verify(terminal[k],'parent-'+k)
need(terminal['stderr']['bytes']==0 and terminal['authority']==root['rootAction']and terminal['config']==root['config'],'full parent raw streams and Root/config identity')
need(terminal['argv'][1]==str(K/'ownership-runtime-candidate-v1/run.mjs')and json.loads(terminal['argv'][2])==root['config'],'actual parent entry/config caller')
started=data(root['started'],'external-started');need(started['pid']==9872 and started['argv']==terminal['argv'],'external launch/terminal identity')
ix,rows=index(root['index'],46);by={str(Path(r['path']).relative_to(OUT)):r for r in rows}
actual={str(p.relative_to(OUT))for p in OUT.rglob('*')if p.is_file()};need(actual==set(by)|{'index.json','completion.json'}and len(actual)==48,'complete46-indexed48-actual output closure')
need(not any(p.is_symlink()for p in OUT.rglob('*'))and all(p.stat().st_nlink==1 for p in OUT.rglob('*')if p.is_file()),'all output ordinary single-link paths')
result=data(root['result'],'actual-parent-result');completion=data(root['completion'],'actual-parent-completion')
for k,r in [('index',root['index']),('result',root['result'])]:need(completion[k]==dict(r,path=Path(r['path']).name),'exact parent completion '+k)
exact(json.loads(Path(terminal['stdout']['path']).read_bytes()),dict(root=str(OUT),index=completion['index'],completion=dict(path='completion.json',sha256=root['completion']['sha256'],bytes=root['completion']['bytes'])),'whole parent stdout')
need(result['sourceIndexSha256']==SOURCE and result['rootAction']==root['rootAction']and result['component']==art_contract['artifacts']['component'],'actual result source/Root/component binding')

algorithm=dict(name='HMAC',hash=dict(name='SHA-256'),length=160)
expected_oracle=dict(schemaVersion=1,node='v22.14.0',tagHex=TAG,keys=[dict(format=f,type='secret',extractable=f=='jwk',algorithm=algorithm,usages=['sign','verify'],tagHex=TAG,valid=True,invalid=False)for f in ['raw','jwk']],hostTestOracleOnly=True,guestNodeCryptoExportsAdded=False)
oracle=data(root['nodeOracle'],'actual-host-Node-oracle');exact(oracle,expected_oracle,'whole actual Node22 oracle')
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

ledger=[];all_runs=[];terminals=[];observed=collections.Counter();session_info=[]
need([s['scenario']for s in root['sessions']]==['retained','fresh','wrapper'],'actual three-session order')
for s in root['sessions']:
 scenario=s['scenario'];expected,final=expectations(scenario);base=OUT/scenario
 wc=data(by[scenario+'/completion.json'],'worker-completion');wirow=by[scenario+'/index.json'];wi,wrows=index(wirow,len(expected)+1)
 need({Path(r['path']).relative_to(base).as_posix()for r in wrows}=={f'raw/{i:03}.json'for i in range(1,len(expected)+1)}|{'results.json'},'exact raw/result nested inventory')
 for k,r in [('index',wirow),('result',s['result'])]:need(wc[k]==dict(r,path=Path(r['path']).name),'exact worker completion '+scenario+' '+k)
 wt=data(s['terminal'],'owned-'+scenario+'-terminal');terminals.append(wt)
 for k,v in dict(status=0,signal=None,spawnError=None,timedOut=False,externalSignal=None,outputLimitExceeded=False,closed=True,ownedGroupGone=True,terminalExitZeroObserved=True).items():need(wt[k]==v,'clean terminal '+scenario+' '+k)
 need(wt['errors']==[]and wt['signals']==[]and wt['timeoutMs']==600000 and wt['maxOutputBytes']==16777216 and wt['pid']==s['pid'],'full bounded worker outcome '+scenario)
 need(wt['args']==[str(K/'ownership-runtime-candidate-v1/worker.mjs'),json.dumps(root['config'],separators=(',',':')),scenario],'actual worker caller/config/scenario '+scenario)
 for k in ['stdout','stderr']:verify(wt[k],'actual-'+scenario+'-'+k)
 need(wt['stderr']['bytes']==0,'full worker stderr empty')
 exact(json.loads(Path(wt['stdout']['path']).read_bytes()),dict(root=str(base),publicStringReturns=len(expected)),'whole worker stdout '+scenario)
 wr=data(s['result'],'worker-result-'+scenario)
 exact(wr,dict(schemaVersion=1,state='CRYPTO_OWNER355_NORMAL_SESSION_COMPLETE_EXTERNAL_ZERO_REQUIRED',scenario=scenario,sourceIndexSha256=SOURCE,publicStringReturns=len(expected),finalCounters=final,allCompletePublicChecksPassed=True,asyncGuestScalarObservedAsOrdinaryString=True,generatedModuleImported=True,onlyNewGuardedComponent=True,applicationReferencesReleased=True,nativeFreeOrWipeOrIsolatedRootObserved=False,resetOrRequestReuseClaim=False,operationalAdmission=False,runtimeAcceptanceClaim=False),'complete worker result '+scenario)
 for i,(name,args,value)in enumerate(expected,1):
  rr=by[f'{scenario}/raw/{i:03}.json'];raw=data(rr,'whole-typed-raw-return')
  need(set(raw)=={'name','args','kind','returnedType','value'}and type(raw['value'])is str,'whole typed primitive string envelope')
  exact({k:v for k,v in raw.items()if k!='value'},dict(name=name,args=args,kind='return',returnedType='string'),'raw caller/type '+scenario+str(i))
  decoded=json.loads(raw['value']);exact(decoded,value,'whole decoded '+scenario+'/'+str(i))
  runs=[decoded]if name=='run'else decoded['records']if name=='validate'else []
  all_runs.extend(runs)
  ledger.append(dict(scenario=scenario,ordinal=i,name=name,args=args,raw=rr,codeUnits=len(raw['value'].encode('utf-16-le'))//2,wholeStringSha256Utf8=hashlib.sha256(raw['value'].encode()).hexdigest(),decoded=decoded,exactIndependentExpectationMatched=True))
 session_info.append(dict(scenario=scenario,pid=wt['pid'],terminal=s['terminal'],result=s['result'],index=wirow,completion=by[scenario+'/completion.json'],rawReturns=len(expected),finalCounters=final))
need(len({t['pid']for t in terminals})==3 and all(t['pid']!=terminal['pid']for t in terminals),'three distinct owned workers separate from parent')
for r in all_runs:
 observed['runRecords']+=1
 for o in r['observations']:
  if o['phase']=='returned'and o['operation']=='sign':
   exact(o['returned'],TAG_RETURN,'full signature typed return');observed['full32ByteSignatures']+=1
  if o['phase']=='returned'and o['operation']=='verify':observed['verificationBooleans']+=1;observed['verifyTrue'if o['returned']['value']else 'verifyFalse']+=1
  if o['operation']in ['prototype-sign','prototype-verify','ordinary-invalid-key']:observed['nativePromiseTypeErrorRefusals']+=1
  if o['phase']=='returned'and o['operation']=='importKey':observed['keyImportReturns']+=1
 if r['caseId']==3:observed['prototypeGetterRefusals']+=len(r['result']['getters']);observed['noConstructorRefusals']+=1
totals=dict(rawPublicStrings=len(ledger),**dict(observed),guestKeyImports=sum(s['finalCounters']['keyImportsFulfilled']for s in session_info),guestSignAttempts=sum(s['finalCounters']['signCalls']for s in session_info),guestVerifyAttempts=sum(s['finalCounters']['verifyCalls']for s in session_info))
need(totals==dict(rawPublicStrings=23,runRecords=20,keyImportReturns=10,full32ByteSignatures=45,verificationBooleans=45,verifyTrue=25,verifyFalse=20,nativePromiseTypeErrorRefusals=15,prototypeGetterRefusals=20,noConstructorRefusals=5,guestKeyImports=10,guestSignAttempts=55,guestVerifyAttempts=50),'independently decoded full coverage totals')
need(result['publicStringReturns']==23 and result['guestKeyImports']==10 and result['guestSignCalls']==55 and result['guestVerifyCalls']==50,'parent totals match decoded evidence')
save('per-call-ledger.json',dict(schemaVersion=1,calls=ledger,wholeStringsDecoded=True,expectedBuiltIndependently=True))
save('decoded-coverage-and-refusals.json',dict(schemaVersion=1,totals=totals,sessions=session_info,
 refusalExpectedShape=guard_result(),refusalMessagesAreNativeSourceCoupledNotNodeErrorParity=True,
 fullNodeOracle=oracle,fullTagHex=TAG,tagBytes=32,reviewerHmacOrCryptoComputed=False))
save('rehashed-inputs.json',dict(schemaVersion=1,files=[dict(r,roles=sorted(r['roles']))for r in sorted(seen.values(),key=lambda r:r['path'])],ownerActionsInvoked=False))
save('data-results.json',dict(schemaVersion=1,dataReviewPassed=True,rootResult=root_row,sourceIndex=root['sourceIndex'],sourceReview=root['sourceReview'],
 sourceIndexSha256=SOURCE,componentSha256=COMPONENT,component=art_contract['artifacts']['component'],artifacts=art_contract['artifacts'],artifactReview=root['artifactReview'],artifactContract=root['artifactContract'],
 rootAction=root['rootAction'],config=root['config'],actualIndex=root['index'],actualResult=root['result'],actualCompletion=root['completion'],nodeOracle=root['nodeOracle'],externalParentTerminal=root['externalTerminal'],sessions=session_info,
 actualIndexedFiles=46,actualRegularFiles=48,sourceMembers=22,preparationRows=13247,uniqueInputsRehashed=len(seen),coverage=totals,
 allWholePrimitiveStringsDecoded=True,allFullFieldsMatchIndependentExpectedRecords=True,actualNodeOracleFullFieldsMatchSuccessfulGuestSemantics=True,
 externalParentExitCode=0,allThreeOwnedWorkersRawZeroClean=True,generatedModuleImported=True,asyncGuestScalarObservedAsOrdinaryStrings=True,
 normalOnly=True,sourceGuardedPrototypeRefusalsObserved=True,positiveControlsBeforePrototypeCases=True,applicationHolderReleaseObserved=True,
 stockWasmtimeExecuted=False,gcExecuted=False,oomExecuted=False,resetExecuted=False,finalizerFreeWipeOrIsolatedRootObserved=False,
 nativeGlobalCountersInstrumented=False,runtimeAcceptanceClaim=False,operationalAdmission=False,timingAllowed=False,
 reviewerReadHashDecodeOnly=True,reviewerHelpersPreflightNodeOracleGeneratedModuleKeyCryptoGuestWorkerNativeHostActionsInvoked=False,checks=checks))
print(json.dumps(dict(dataReviewPassed=True,coverage=totals,uniqueInputs=len(seen),checks=checks)))
