"""Independent completed GC runtime DATA audit. No owner/JS/crypto actions."""
from pathlib import Path
import ast,copy,json,os,re
import review_io as I
HERE=Path(__file__).resolve().parent;K=HERE.parent;S=K/'ownership-gc-runtime-candidate-v2';OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-runtime-v2')
SHA='5abe5ed812b93676bff2f09cff57099bff6d23d7ada6e5e63bbbe8152d0a0959';TAG='b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7';KEYS=['inspectCalls','runCalls','clearCalls','validateCalls','keyImportsAttempted','keyImportsFulfilled','signCalls','verifyCalls']
def row(p):return I.descriptor(str(p))
def load(p):return I.read(row(p))
def eq(a,b,label):I.need(json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True),label)
def absolute(base,d):return dict(path=str(base/I.member(d['path'])),sha256=d['sha256'],bytes=d['bytes'])
def write(name,v):
    with(HERE/name).open('xb')as f:f.write((json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
root_row=dict(path=str(K/'ownership-gc-runtime-v2-root-results.json'),sha256='a6348814708dee7d6a35c9edf38feab54a12841dd114d6a9924d545ee39c6e3b',bytes=4424)
r=I.read(root_row);I.verify_descriptors(r,'whole actual completed GC runtime Root observation');I.need(r['state']=='ROOT_OBSERVED_CRYPTO_OWNER355_GC_RUNTIME_V2_PASSED_V1'and r['rootToolSession']==52246 and r['rootObservedToolRawExitCode']==0,'actual completed Root runtime tuple')
a=I.read(r['rootAuthority']);cfg=I.read(r['rootConfig']);parent=I.read(r['actualParentResult']);completion=I.read(r['actualCompletion']);outer=I.read(r['externalParentTerminal']);source_index=row(S/'index.json');I.need(source_index['sha256']==SHA==r['sourceIndexSha256'],'genuine corrected runtimev2 source')
I.indexed(source_index,'whole actual v2 runtime source family');I.verify_descriptors(a,'whole new runtime-only Root authority');I.indexed(a['sourceIndependentReview']['index'],'whole genuine source-only peer94a2');peer=I.read(a['sourceIndependentReview']['result']);I.need(peer['state']=='INDEPENDENT_CRYPTO_OWNER355_GC_RUNTIME_SOURCE_REVIEW_PASSED_V2'and peer['sourceIndexSha256']==SHA and peer['sourceOnly']is True and peer['sourceReviewPassed']is True and peer['ownerActionsInvoked']is False,'source peer is genuine corrected v2 and not action authority')
eq(cfg,dict(schemaVersion=1,sourceIndexSha256=SHA,rootAction=r['rootAuthority']),'whole actual Root config');I.need(a['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_GC_RUNTIME_V2'and a['gcRuntimeAllowed']is True and a['nodeOracleAllowed']is True and a['publicBufferGcPressureAllowed']is True and a['boundedKeyFixtureAllowed']is True,'actual finite GC-key-runtime and host-oracle authorization')
eq(a['scenarios'],['retained','fresh','wrapper'],'exact three fresh schedules');I.need(a['workerTimeoutMs']==600000 and a['outputRoot']==str(OUT)and a['componentSha256']==r['component']['sha256']and a['engineSha256']==r['nativeEngineSha256'],'actual source/component/native/output scope')
for k in ['oomAllowed','resetAllowed','unsafePrototypeProbesAllowed','otherVariantsAllowed','wasmtimeAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim','nativeGcCountObservedClaim','isolatedRootClaim','nativeFreeOrWipeClaim']:I.need(a[k]is False,'closed additional runtime scope '+k)
refs=load(S/'references.json');I.verify_descriptors(refs,'whole source/native/artifact/expected dependency descriptors')
for d in load(S/'input-freeze.json')['files']:I.verify(d,'all finite original-context runtime/source/native/packaging/proof inputs')
I.indexed(refs['guestIndex'],'whole unchanged GC fixture7988 source');I.indexed(refs['componentSourceIndex'],'whole component source6f0f');I.indexed(refs['nativeSourceIndex'],'whole native sourceed');I.indexed(refs['heldRuntimeV1']['index'],'immutable old failed v1 SOURCE DATA only');I.indexed(refs['heldRuntimeV1']['failurePeerIndex'],'immutable prior preflight failure proof DATA only')
I.indexed(a['actualArtifactReview']['index'],'whole genuine completed GC artifactf812');artifact=I.read(a['actualArtifactReview']['result']);contract=I.read(a['actualArtifactContract']);eq(contract['artifacts'],artifact['artifacts'],'actual complete12 artifact contract and result map equal')
for k,v in contract['requiredFixedValues'].items():eq(artifact[k],v,'complete actual artifact proof fixed field '+k)
I.need(contract['reviewResult']==a['actualArtifactReview']['result']and artifact['componentSha256']==r['component']['sha256']and artifact['engineSha256']==r['nativeEngineSha256'],'exact new actual component/native proof, no normal projection')
for d in load(Path(a['actualArtifactReview']['index']['path']).parent/'rehashed-inputs.json')['files']:I.verify(d,'full prior component/native/bootstrap/build/frozen/source/library/normal closure')
I.verify_descriptors(artifact['artifacts'],'all12 actual runtime loading artifacts unchanged');I.indexed(a['externalMonitorIndex'],'whole real observed lifecycle monitor')
actual_index,index_members=I.indexed(r['actualOutputIndex'],'complete actual46-indexed runtime output',extra=('completion.json',));I.need(len(index_members)==46,'actual46 indexed and48 regular files');by={Path(d['path']).relative_to(OUT).as_posix():d for d in index_members}
eq(absolute(OUT,completion['index']),r['actualOutputIndex'],'actual parent completion index');eq(absolute(OUT,completion['result']),r['actualParentResult'],'actual parent completion result');I.need(completion['state']=='CRYPTO_OWNER355_GC_RUNTIME_COMPLETE_EXTERNAL_PARENT_ZERO_AND_REVIEW_REQUIRED','actual final completion scope')
expected=I.read(refs['expectedCompleteRecord']);eq(refs['expectedCompleteRecord'],r['expectedCompleteRecord'],'exact sealed schema2 expected record');I.need(expected['schemaVersion']==2 and expected['kind']=='crypto-owner-within-export-gc-validation-v2','truthful schema2 GC expected model')
oracle=I.read(r['nodeOracle']);oracle_expected=dict(schemaVersion=1,node='v22.14.0',tagHex=TAG,keys=[dict(format=f,type='secret',extractable=f=='jwk',algorithm=dict(name='HMAC',hash=dict(name='SHA-256'),length=160),usages=['sign','verify'],tagHex=TAG,valid=True,invalid=False)for f in ['raw','jwk']],hostTestOracleOnly=True,guestNodeCryptoExportsAdded=False);eq(oracle,oracle_expected,'whole actual pinned host Node raw/JWK oracle object and all tag bytes, not fresh crypto')
def zero():return {k:0 for k in KEYS}
def state(raw,jwk):return dict(rawRetained=raw,jwkRetained=jwk,strongApplicationKeyOwners=int(raw)+int(jwk),pendingOperationsInstrumented=False,finalizersOrWipesObserved=False)
def next_run(c,i):
    c=copy.deepcopy(c);c['runCalls']+=1
    if i<2:c['keyImportsAttempted']+=1;c['keyImportsFulfilled']+=1;c['signCalls']+=2;c['verifyCalls']+=2
    elif i==2:c['signCalls']+=4;c['verifyCalls']+=4
    else:c['signCalls']+=3;c['verifyCalls']+=2
    return c
def inspect(c):v=copy.deepcopy(expected['before']);v['counters']=copy.deepcopy(c);v['state']=state(False,False);return v
decoded=[];all_records=[];summaries=[];signature_fields=[];signature_observations=[];verify_observations=[];initial=dict(keyImportsAttempted=0,signCalls=0,verifyCalls=0,retainedKeys=0,pendingOperations=0)
for scenario,pid,count,rotations,pressure in [('retained',25459,15,3,48),('fresh',25602,7,1,16),('wrapper',25760,1,0,16)]:
    _,members=I.indexed(by[scenario+'/index.json'],'complete actual '+scenario+' worker',extra=('completion.json',));I.need(len(members)==count+1,'every public raw and result worker-indexed')
    result=I.read(by[scenario+'/results.json']);wc=I.read(by[scenario+'/completion.json']);eq(absolute(OUT/scenario,wc['index']),by[scenario+'/index.json'],'actual worker completion index');eq(absolute(OUT/scenario,wc['result']),by[scenario+'/results.json'],'actual worker completion result');I.need(wc['state']=='CRYPTO_OWNER355_GC_WORKER_COMPLETE_EXTERNAL_EXIT_ZERO_REQUIRED'and wc['scenario']==scenario,'actual complete worker state')
    wanted=[];c=zero()
    if scenario=='wrapper':
        wanted=[('validate',[],copy.deepcopy(expected))];c=copy.deepcopy(expected['after']['counters'])
    else:
        c['inspectCalls']+=1;wanted.append(('inspect',[],inspect(c)))
        for rotation in range(rotations):
            for i in range(4):
                c=next_run(c,i);v=copy.deepcopy(expected['records'][i]);v['counters']=copy.deepcopy(c);v['state']=state(True,i!=0 or c['keyImportsFulfilled']>1);wanted.append(('run',[i],v))
        c['clearCalls']+=1;v=copy.deepcopy(expected['released']);v['counters']=copy.deepcopy(c);wanted.append(('clear',[],v));c['inspectCalls']+=1;wanted.append(('inspect',[],inspect(c)))
    I.need(len(wanted)==count,'finite independent schedule/public call count');session_decoded=[]
    for number,(name,args,want)in enumerate(wanted,1):
        raw_row=by[f'{scenario}/raw/{number:03d}.json'];carrier=I.read(raw_row);I.need(set(carrier)=={'name','args','kind','returnedType','value'},'complete exact typed string carrier, no opaque/discarded values');eq({k:carrier[k]for k in ['name','args','kind','returnedType']},dict(name=name,args=args,kind='return',returnedType='string'),'actual typed public name/arguments/return')
        I.need(type(carrier['value'])is str and len(carrier['value'].encode())<=2*1024*1024,'complete bounded actual returned string');value=I.decode(carrier['value'].encode());eq(value,want,'whole typed public value including every counter/key/window/sentinel/refusal/GC field')
        session_decoded.append(dict(raw=raw_row,name=name,args=args,value=value));decoded.append(dict(scenario=scenario,raw=raw_row,name=name,args=args,value=value))
        if name=='run':all_records.append((scenario,number,value))
        elif name=='validate':all_records.extend((scenario,number,v)for v in value['records']);eq(raw_row,r['rawWrapper'],'actual complete wrapper raw carrier exact')
    result_expected=dict(schemaVersion=1,state='CRYPTO_OWNER355_GC_SESSION_COMPLETE_EXTERNAL_ZERO_REQUIRED',scenario=scenario,sourceIndexSha256=SHA,publicStringReturns=count,finalCounters=c,publicGcPressureRequestsObserved=pressure,publicGcPressureRecordsObserved=pressure,actualNativeGcCountObserved=False,allCompletePublicChecksPassed=True,asyncGuestScalarObservedAsOrdinaryString=True,generatedModuleImported=True,onlyNewGuardedComponent=True,applicationReferencesReleased=True,nativeFreeOrWipeOrIsolatedRootObserved=False,resetOrRequestReuseClaim=False,operationalAdmission=False,runtimeAcceptanceClaim=False);eq(result,result_expected,'whole exact worker final result and all source-coupled scope flags')
    t=I.read(by['processes/'+scenario+'.terminal.json']);I.verify_descriptors(t,'all actual '+scenario+' worker raw streams');I.need(t['pid']==pid and t['status']==0 and t['signal']is None and t['spawnError']is None and t['timedOut']is False and t['timeoutMs']==600000 and t['externalSignal']is None and t['signalCount']==0 and t['outputLimitExceeded']is False and t['signals']==t['errors']==[]and t['closed']is True and t['ownedGroupGone']is True and t['terminalExitZeroObserved']is True,'actual clean fresh owned worker status0; no outer-schema projection')
    I.need(t['executable']==refs['node']['path']and t['args'][0]==str(S/'worker.mjs')and t['args'][2]==scenario and t['stderr']['bytes']==0,'actual pinned worker argv/scenario/empty stderr');eq(I.decode(t['args'][1].encode()),r['rootConfig'],'actual worker config argument');eq(I.read(t['stdout']),dict(root=str(OUT/scenario),publicStringReturns=count),'whole actual worker stdout return')
    launch=I.read(by['processes/'+scenario+'.launch.json']);I.need(launch['executable']==t['executable']and launch['args']==t['args']and launch['detachedOwnedSession']is True and launch['timeoutMs']==600000,'actual fresh detached worker launch retained')
    summaries.append(dict(scenario=scenario,pid=pid,publicStrings=count,caseRecords=4*rotations if rotations else 4,pressureRequests=pressure,pressureRecordCounters=pressure,finalCounters=c,workerResult=by[scenario+'/results.json'],workerTerminal=by['processes/'+scenario+'.terminal.json']))
I.need(len(decoded)==23 and len(all_records)==20,'all23 complete public strings and20 case records')
for scenario,number,v in all_records:
    eq(v['initial'],initial,'all snapshot-local initial counters0');I.need(v['completed']is True and v['finalizerCountOrWipeProof']is False,'every ordinary case complete without native finalizer proof')
    delta=[4,4,8,0][v['caseId']];g=v['gcObservation'];I.need(g['publicGcPressureRequests']==g['publicGcPressureRecords']==delta and g['actualNativeGcCountObserved']is False and g['isolatedTemporaryRootsProved']is False,'per-run exact scoped request/record counter delta')
    def scan(x,path):
        if isinstance(x,dict):
            for k,y in x.items():
                p=path+'.'+k
                if k in ['firstSignatureHex','secondSignatureHex','positiveFullSignatureHex']:I.need(y==TAG and len(bytes.fromhex(y))==32,'entire named SignatureHex equals actual Node full tag');signature_fields.append(dict(path=p,tag=y))
                if k=='returned'and isinstance(y,dict)and y.get('type')=='ArrayBuffer':I.need(y==dict(type='ArrayBuffer',bytes=32,fullHex=TAG,fullBytesRetained=True),'every observed complete sign ArrayBuffer');signature_observations.append(dict(path=p,tag=y['fullHex']))
                if k=='returned'and isinstance(y,dict)and y.get('type')=='boolean':I.need(type(y.get('value'))is bool,'actual boolean typed observation');verify_observations.append(y['value'])
                scan(y,p)
        elif isinstance(x,list):
            for i,y in enumerate(x):scan(y,path+'['+str(i)+']')
    scan(v,f'{scenario}/raw/{number:03d}/case{v["caseId"]}')
I.need(len(signature_fields)==len(signature_observations)==45 and len(verify_observations)==45 and sum(verify_observations)==25,'45 named signatures plus45 duplicate sign observations,25true20false verify observations')
wrapper=I.read(r['rawWrapper']);wrapper_value=I.decode(wrapper['value'].encode());eq(wrapper_value,expected,'entire wrapper matches sealed schema2 typed record')
pressure=wrapper_value['pressure'];I.need(len(pressure['records'])==16 and pressure['sourceForcedHookSitesPerRecord']==6 and pressure['actualNativeGcCountObserved']is False,'only16 full wrapper pressure-byte records; six is source site count only')
phases=['before-first-sign','between-signs','before-valid-verify','after-verifies']*4
for i,d in enumerate(pressure['records']):eq(d,dict(sequence=i+1,phase=phases[i],bytes=64,encodedHex='a5'*64,decodedHex='a5'*64,forcedGcCounterObserved=False,isolatedTemporaryRootProved=False),'each actual whole64-byte public pressure encoding/decoding record')
eq(parent['expectedScopedRequests'],dict(retained=48,fresh=16,wrapper=16),'actual scoped80 request count matrix');I.need(parent['publicGcPressureRequestsObserved']==80 and sum(s['pressureRequests']for s in summaries)==80 and parent['guestKeyImports']==10 and parent['guestSignCalls']==55 and parent['guestVerifyCalls']==50,'full aggregate public counters match independent schedules')
I.need(parent['state']=='CRYPTO_OWNER355_GC_RUNTIME_COMPLETE_UNREVIEWED_V1'and parent['sourceIndexSha256']==SHA and parent['rootAction']==r['rootAuthority']and parent['component']==r['component']and parent['nodeOracle']=='node-oracle.json'and parent['publicStringReturns']==23,'genuine complete parent result/source/component/oracle tuple')
for k in ['gcVariantOnly','generatedModuleImported','asyncScalarReturnedOrdinaryStrings','threeFreshOwnedProcesses','fullRawPublicReturnsRetainedBeforeAssertions','publicBufferPressureFixtureExecuted']:I.need(parent[k]is True,'actual finite runtime scope '+k)
for k in ['actualNativeGcCountObserved','wasmtimeExecuted','oomOrResetExecuted','nativeFreeOrWipeOrIsolatedRootObserved','operationalAdmission','runtimeAcceptanceClaim']:I.need(parent[k]is False,'no unsupported native/WT/runtime-adoption claim '+k)
# Complete raw parent and observed process identity boundary, no live queries.
for k,v in dict(pid=25409,rawExitCode=0,timeout=False,forcedCleanup=False,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True).items():eq(outer[k],v,'actual clean parent '+k)
for k in ['interruptedSignals','remainingObservedPids','signals','errors']:eq(outer[k],[],'actual parent no residual/error '+k)
eq(outer['authority'],r['rootAuthority'],'actual parent Root authority');I.verify_descriptors(outer,'all actual outer raw streams');I.need(outer['stderr']['bytes']==0,'actual outer stderr empty')
ex=Path(r['externalParentTerminal']['path']).parent;events=[]
for p in sorted(ex.iterdir()):
    I.verify(row(p),'complete external captured evidence')
    if p.name.startswith('owned-'):e=load(p);I.need(e['sequence']==len(events),'ordered actual identities');events.append(e['process'])
eq(events,outer['observedProcesses'],'whole actual four process identity records');I.need([e['pid']for e in events]==[25409,25459,25602,25760]and all(e['command']==refs['node']['path']for e in events),'actual four plain pinned Node processes, no WT')
eq(outer['finalGroups'],[dict(pgid=p,alive=False,signalAllowed=False)for p in [25409,25459,25602,25760]],'all four exact observed groups gone');I.exact_tree(ex,['started.json','terminal.json','stdout.log','stderr.log',*[f'owned-{i:04d}.json'for i in range(4)]])
started=load(ex/'started.json');I.need(started['argv'][:2]==[refs['node']['path'],str(S/'run.mjs')]and started['pid']==25409 and started['timeoutSeconds']==2400,'actual bounded plain pinned parent argv');eq(I.decode(started['argv'][2].encode()),r['rootConfig'],'actual parent config argument')
eq(I.read(outer['stdout']),dict(root=str(OUT),index=completion['index'],completion=dict(path='completion.json',sha256=r['actualCompletion']['sha256'],bytes=r['actualCompletion']['bytes'])),'whole parent stdout completion return')
history=I.read(r['readerHistory']);I.need(history['correctedReaderPassed']is True,'Root data-reader qualification retained')
# Actual caller/callee source is inspected, never imported by this reviewer.
loading=I.verify(row(S/'loading.mjs')).read_text();worker_source=I.verify(row(S/'worker.mjs')).read_text();run=I.verify(row(S/'run.mjs')).read_text()
I.need("const namespace=await import(pathToFileURL(captured.rows.glue.path))"in loading and 'validateNamespace(namespace)'in loading and 'return namespace[name](...args)'in loading,'genuine actual ESM/TLA namespace import and exact direct scalar invoke protocol')
I.need(worker_source.index("await out.write('raw/'")<worker_source.index("need(typeof value==='string'")and 'await session.recheck();await frame.recheck()'in worker_source,'whole raw primitive retained before assertions and final source/artifact rechecks')
I.need("const oracle=await nodeOracle();await out.write('node-oracle.json'"in run and run.index('await nodeOracle()')<run.index('runOwnedCommand('),'actual Root host oracle runs and is retained before workers, no reviewer oracle')
ast.parse(I.verify(a['externalController']).read_text());I.final_rehash()
with(HERE/'wrapper-public-string.utf8').open('xb')as f:f.write(wrapper['value'].encode());f.flush();os.fsync(f.fileno())
write('decoded-public-returns.json',dict(schemaVersion=1,returns=decoded,allWholeTypedValuesVerified=True));write('semantic-coverage.json',dict(schemaVersion=1,sessions=summaries,namedSignatureFields=signature_fields,completeSignReturnObservations=signature_observations,verifyBooleans=verify_observations,wholeWrapperEqual=True,scopedPressureRequests=dict(retained=48,fresh=16,wrapper=16),totalScopedRequests=80,ordinaryScopedRequestsWithoutFullPressureBytes=64,wholeWrapperPressureByteRecords=16,actualNativeGcCountObserved=False))
write('rehashed-inputs.json',dict(schemaVersion=1,files=list(I.ROWS.values()),allFinalInputHashesStable=True,reviewerOwnerActionsInvoked=False))
write('data-results.json',dict(schemaVersion=1,state='ACTUAL_GC_RUNTIME_V2_FULL_TYPED_DATA_AUDIT_PASSED',rootObservation=root_row,sourceIndex=source_index,sourceIndependentReview=a['sourceIndependentReview'],actualIndex=r['actualOutputIndex'],nodeOracle=r['nodeOracle'],rawWrapper=r['rawWrapper'],expectedCompleteRecord=r['expectedCompleteRecord'],actualParentResult=r['actualParentResult'],actualCompletion=r['actualCompletion'],externalParentTerminal=r['externalParentTerminal'],rootAuthority=r['rootAuthority'],rootConfig=r['rootConfig'],actualArtifactReview=a['actualArtifactReview'],actualArtifactContract=a['actualArtifactContract'],component=r['component'],nativeEngineSha256=r['nativeEngineSha256'],nativeSourceFiles=355,wholePublicStrings=23,caseRecords=20,namedSignatureHexValues=45,completeSignReturnObservations=45,verifyObservations=45,verifyTrue=25,verifyFalse=20,keyImports=10,signAttempts=55,verifyAttempts=50,scopedPressureRequests=dict(retained=48,fresh=16,wrapper=16),totalScopedPressureRequests=80,ordinaryRequestsWithoutFullPressureBytes=64,fullWrapperPressureByteRecords=16,generatedModuleImported=True,publicBufferPressureFixtureExecuted=True,stockWasmtimeExecuted=False,actualNativeGcCountObserved=False,rootHostNodeOracleExecuted=True,reviewerCryptoOracleOrHelpersOrNodeOrGuestActionsInvoked=False,allObservedOwnedGroupsGone=True,observedProcesses=4,observedGroups=4,actualIndexedFiles=46,actualRegularFiles=48,physicalInputs=len(I.ROWS),readHashChecks=I.CHECKS,operationalAdmission=False,runtimeAcceptanceClaim=False))
print(json.dumps(dict(state='ACTUAL_GC_RUNTIME_V2_FULL_DATA_PASSED',physicalInputs=len(I.ROWS),checks=I.CHECKS,strings=23,records=20,namedSignatures=45,totalScopedPressureRequests=80,fullPressureByteRecords=16,reviewerOwnerActionsInvoked=False)))
