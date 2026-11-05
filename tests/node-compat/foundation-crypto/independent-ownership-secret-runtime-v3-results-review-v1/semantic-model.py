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
