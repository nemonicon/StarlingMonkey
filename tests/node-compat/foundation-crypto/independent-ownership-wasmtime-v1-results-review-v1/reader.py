"""Independent retained DATA reader. Never imports or executes producer code."""
from pathlib import Path, PurePosixPath
import hashlib, json, os, re, stat

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
K = REPO / 'tests/node-compat/foundation-crypto'
OUT = Path('/private/tmp/starling-node-compat/crypto-owner355-wasmtime-v1')
SOURCE = K / 'ownership-wasmtime-candidate-v1'
ROOT_SHA = 'f840998bbecd0d640d52f0b417c58492a207025dba2d21139d6466d285d3782d'
SOURCE_SHA = '6f5d38ec7ff4df7b4eb063ec9d818b59b1f6e27005e28edb124f26a76f166256'
STATE = 'INDEPENDENT_CRYPTO_OWNER355_WASMTIME_V1_RESULTS_REVIEW_PASSED_V1'
TAG = 'b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7'
verified, observations, checks = {}, [], 0

def need(value, message):
    global checks
    checks += 1
    if not value: raise AssertionError(message)

def equal(a,b):
    return json.dumps(a,sort_keys=True,ensure_ascii=False,separators=(',',':')) == json.dumps(b,sort_keys=True,ensure_ascii=False,separators=(',',':'))

def pairs(rows):
    d = {}
    for key,value in rows:
        need(key not in d, 'duplicate JSON key '+key); d[key] = value
    return d

def loads(b):
    return json.loads(b.decode('utf-8'),object_pairs_hook=pairs,parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))

def canonical(p):
    p = Path(p)
    need(p.is_absolute(), 'absolute descriptor path')
    if str(p).startswith('/tmp/'): p = Path('/private'+str(p))
    need('..' not in p.parts, 'no lexical traversal')
    for q in [p,*p.parents]:
        s = q.lstat(); need(not stat.S_ISLNK(s.st_mode), 'no symlink '+str(q))
    return p

def signature(s): return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode)

def row(p):
    p=canonical(p); s=p.stat(); h=hashlib.sha256()
    need(stat.S_ISREG(s.st_mode), 'regular file '+str(p))
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    need(signature(s)==signature(p.stat()),'stable descriptor '+str(p))
    return dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size)

def verify(d, role='descriptor'):
    need(isinstance(d,dict) and set(['path','sha256','bytes'])<=d.keys(),'descriptor fields')
    need(isinstance(d['bytes'],int) and not isinstance(d['bytes'],bool) and d['bytes']>=0 and re.fullmatch('[a-f0-9]{64}',d['sha256']) is not None,'finite descriptor')
    p=canonical(d['path']); key=str(p)
    if key in verified:
        old=verified[key];need(old['sha256']==d['sha256'] and old['bytes']==d['bytes'],'conflicting descriptor '+key)
        need(signature(p.stat())==tuple(old['stat']),'unchanged cached input '+key)
        return p
    actual=row(p);need(actual['sha256']==d['sha256'] and actual['bytes']==d['bytes'],'hash/size '+key)
    verified[key]={**actual,'role':role,'stat':list(signature(p.stat()))};return p

def read(d,role='JSON'):
    p=verify(d,role);need(d['bytes']<=32*1024*1024,'bounded JSON/data reader');b=p.read_bytes()
    need(hashlib.sha256(b).hexdigest()==d['sha256'],'data read same hash');return loads(b)

def known(p,sha,size=None,role='pinned'):
    if size is None:size=Path(p).stat().st_size
    return read(dict(path=str(p),sha256=sha,bytes=size),role)

def descriptors(v):
    if isinstance(v,dict):
        if {'path','sha256','bytes'}<=v.keys() and isinstance(v['path'],str) and v['path'].startswith('/'):
            yield {k:v[k] for k in ['path','sha256','bytes']}
        for x in v.values():yield from descriptors(x)
    elif isinstance(v,list):
        for x in v:yield from descriptors(x)

def indexed(d,extra=(),label='family'):
    p=verify(d,label+' index');v=read(d);need(v['schemaVersion']==1 and isinstance(v['files'],list),'index shape')
    names=[]
    for r in v['files']:
        name=r['path'];rel=PurePosixPath(name)
        need(not rel.is_absolute() and str(rel)==name and all(x not in ('','.','..') for x in name.split('/')) and '\\' not in name,'safe member path')
        need(name not in names,'unique index member');names.append(name)
        verify({**r,'path':str(p.parent/name)},label+' member')
    actual=[]
    for base,dirs,files in os.walk(p.parent,followlinks=False):
        for name in dirs:need(not (Path(base)/name).is_symlink(),'no member directory symlink')
        for name in files:
            f=canonical(Path(base)/name);need(f.is_file(),'regular membership');actual.append(f.relative_to(p.parent).as_posix())
    need(set(actual)==set(names)|{'index.json'}|set(extra),'exact '+label+' membership')
    observations.append(dict(family=str(p.parent),indexedFiles=len(names),actualFiles=len(actual)))
    return v

def walk_rows(v,role):
    for d in descriptors(v):verify(d,role)

def wave(raw):
    need(len(raw)<=16777216,'whole raw pipe cap');s=raw.decode('utf-8','strict')
    need(s.endswith('\n') and not s.endswith('\n\n'),'one terminal LF');s=s[:-1]
    need(len(s)>=2 and s[0]=='"' and s[-1]=='"','one typed WAVE string');out=[];i=1
    while i<len(s)-1:
        ch=s[i];i+=1
        if ch=='\\':
            need(i<len(s)-1,'complete escape');e=s[i];i+=1
            if e=='u':
                need(i<len(s)-1 and s[i]=='{','WAVE braced unicode');end=s.find('}',i+1);digits=s[i+1:end]
                need(i<end<len(s)-1 and re.fullmatch('[0-9a-fA-F]{1,6}',digits) is not None,'bounded unicode digits');cp=int(digits,16);i=end+1
                need(cp<=0x10ffff and not 0xd800<=cp<=0xdfff,'unicode scalar');out.append(chr(cp))
            else:
                escapes={'\\':'\\','"':'"',"'":"'",'t':'\t','r':'\r','n':'\n'}
                need(e in escapes,'pinned WAVE escape');out.append(escapes[e])
        else:
            cp=ord(ch);need(ch!='"' and cp>31 and not 0x7f<=cp<=0x9f and not 0xd800<=cp<=0xdfff,'raw scalar');out.append(ch)
    value=''.join(out);need(len(value.encode('utf-16-le'))//2<=2097152,'decoded wire bound');return value

COUNTERS=['inspectCalls','runCalls','clearCalls','validateCalls','keyImportsAttempted','keyImportsFulfilled','signCalls','verifyCalls']
INITIAL=dict(keyImportsAttempted=0,signCalls=0,verifyCalls=0,retainedKeys=0,pendingOperations=0)
READS=dict.fromkeys(['algorithmName','dataByteLength','dataPrimitive','dataString','signatureByteLength','signaturePrimitive'],0)
def owner(raw,jwk):return dict(rawRetained=raw,jwkRetained=jwk,strongApplicationKeyOwners=int(raw)+int(jwk),pendingOperationsInstrumented=False,finalizersOrWipesObserved=False)
def error(message):return dict(thrownType='object',typeError=True,name='TypeError',message=message)
def refusal(op):return dict(kind='native-promise-rejection',error=error('crypto.subtle.'+op+': key must be a CryptoKey object'))
def inspect(c):return dict(schemaVersion=1,kind='crypto-owner-inspect-v1',initial=INITIAL,counters=c.copy(),state=owner(False,False),globalCryptoKeyInstalled=True,constructorStable=True,cryptoOperationsAtSnapshot=0,fullNativeOwnershipOrZeroizationObserved=False)
def operation(extractable):
    return dict(key=dict(instanceOfGlobalCryptoKey=True,globalConstructorStable=True,type='secret',extractable=extractable,algorithm=dict(name='HMAC',hash=dict(name='SHA-256'),length=160),usages=['sign','verify']),firstSignatureHex=TAG,secondSignatureHex=TAG,signatureBytes=32,priorFullBytesStable=True,independentNonemptyBacking=True,mutationRestored=True,valid=True,invalid=False,inputBeforeHex='a5'*8+'4869205468657265'+'a5'*8,inputAfterHex='a5'*8+'4869205468657265'+'a5'*8,inputWindow=dict(byteOffset=8,byteLength=8,backingBytes=24),signatureBeforeHex='a5'*8+TAG+'a5'*8,signatureAfterHex='a5'*8+TAG+'a5'*8)
def observations_for(id):
    def obs(op,phase,ret):return dict(operation=op,phase=phase,returned=ret)
    def exercise():
        a=[]
        for op,ret in [('sign',dict(type='ArrayBuffer',bytes=32,fullHex=TAG,fullBytesRetained=True))]*2+[('verify',dict(type='boolean',value=True)),('verify',dict(type='boolean',value=False))]:
            a.extend([obs(op,'before',dict(type='undefined')),obs(op,'returned',ret)])
        return a
    if id<2:return [obs('importKey','before',dict(type='undefined')),obs('importKey','returned',dict(type='object',opaque=True,fullOpaqueValueClaim=False))]+exercise()
    if id==2:return exercise()+exercise()
    return [dict(operation='prototype-sign',phase='returned',record=refusal('sign'),reads=READS),dict(operation='prototype-verify',phase='returned',record=refusal('verify'),reads=READS),*exercise()[:2],obs('verify','before',dict(type='undefined')),obs('verify','returned',dict(type='boolean',value=True)),dict(operation='ordinary-invalid-key',phase='returned',record=refusal('sign'))]
def expected():
    c=dict.fromkeys(COUNTERS,0);entry=c.copy();c['validateCalls']=1;c['inspectCalls']=1;before=inspect(c);records=[]
    for id in range(4):
        c['runCalls']+=1
        if id<2:c['keyImportsAttempted']+=1;c['keyImportsFulfilled']+=1
        c['signCalls'] += [2,2,4,3][id];c['verifyCalls'] += [2,2,4,2][id]
        if id==0:result=dict(format='raw',importInputPreserved=True,callerKeyBytesChangedAfterImport=True,callerBackingHex='a5'*8+'00'*20+'a5'*8,operations=operation(False))
        elif id==1:result=dict(format='jwk',importInputPreserved=True,callerJwkChangedAfterImport=True,operations=operation(True))
        elif id==2:result=dict(format='retained-pair',raw=operation(False),jwk=operation(True),strongApplicationOwners=True)
        else:result=dict(signRefusal=refusal('sign'),verifyRefusal=refusal('verify'),signConversionReads=READS,verifyConversionReads=READS,positiveAlgorithmReads=1,positiveVerifyAlgorithmReads=1,positiveFullSignatureHex=TAG,ordinaryInvalid=refusal('sign'),getters=[dict(name=n,error=error("Method '"+n+" get' called on receiver that's not an instance of CryptoKey")) for n in ['algorithm','extractable','type','usages']],constructorError=error("CryptoKey builtin can't be instantiated directly"),onlyNewGuardedArtifactAllowed=True,uniqueNativeErrorCauseInferred=False)
        records.append(dict(schemaVersion=1,kind='crypto-owner-run-v1',caseId=id,completed=True,result=result,observations=observations_for(id),initial=INITIAL,counters=c.copy(),state=owner(True,id!=0),gcOrEntropyRequested=False,finalizerCountOrWipeProof=False))
    c['clearCalls']=1;released=dict(schemaVersion=1,kind='crypto-owner-clear-v1',initial=INITIAL,counters=c.copy(),state=owner(False,False),applicationReferencesReleased=True,collectionOrNativeFreeOrWipeObserved=False)
    c['inspectCalls']=2
    return dict(schemaVersion=1,kind='crypto-owner-within-export-validation-v1',entryCounters=entry,entryState=owner(False,False),before=before,records=records,released=released,after=inspect(c),withinOneOuterExport=True,separateHostCallInterleavingProved=False,finalizerOrWipeObserved=False)

def write(name,value,raw=False):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    b=value if raw else (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
    with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
    return row(p)

def main():
    root=known(K/'ownership-wasmtime-v1-root-results.json',ROOT_SHA,10035)
    source=indexed(root['sourceIndex'],extra=['source-receipt.json'],label='WT source');need(root['sourceIndex']['sha256']==SOURCE_SHA,'source seal')
    source_receipt=read(row(SOURCE/'source-receipt.json'))
    need(equal(source_receipt['index'],{**root['sourceIndex'],'path':'index.json'}) and source_receipt['sourceMembers']==30 and source_receipt['inputRows']==13425,'nonindexed source receipt index/closure binding')
    walk_rows(root,'Root actual binding')
    refs=loads((SOURCE/'references.json').read_bytes());freeze=loads((SOURCE/'input-freeze.json').read_bytes());need(len(freeze['files'])==13425,'complete finite source closure')
    need(len({r['path'] for r in freeze['files']})==13425,'unique original source rows')
    for r in freeze['files']:verify(r,r['role'])
    for key in ['sourceReview','normalReview','artifactReview']:
        family=root[key];idx=indexed(family['index'],extra=['review-receipt.json'] if key=='sourceReview' else [],label=key);data=read(family['result']);walk_rows(data,key+' result closure')
        need(any(x['path']=='results.json' and x['sha256']==family['result']['sha256'] and x['bytes']==family['result']['bytes'] for x in idx['files']),'indexed review result')
        if key=='sourceReview':
            need(data['sourceReviewPassed'] is True and data['sourceIndexSha256']==SOURCE_SHA and data['ownerActionsInvoked'] is False,'source peer scope')
            receipt=read(row(Path(family['index']['path']).parent/'review-receipt.json'));need(equal(receipt['index'],{**family['index'],'path':'index.json'}),'source peer nonindexed receipt index binding')
        else:
            contract=read(refs['normalContract' if key=='normalReview' else 'artifactContract']);walk_rows(contract,key+' contract closure')
            for n,v in contract['requiredFixedValues'].items():need(equal(data[n],v),'prior fixed '+n)
            if 'requiredCoverage' in contract:need(equal(data['coverage'],contract['requiredCoverage']),'normal full finite coverage unchanged')
            indexed(data['actualIndex'],extra=['completion.json'],label=key+' actual output')
            if key=='normalReview':normal=data
            else:artifact=data
    walk_rows(refs,'source critical reference');need(equal(normal['artifacts'],artifact['artifacts']) and equal(refs['artifacts'],artifact['artifacts']),'complete actual artifact tuple')
    native=read(artifact['nativeFreeze']);need(native['nativeInputsVerified']==355 and len(native['copies'])==1390,'exact accepted normal355 freeze closure')
    for copy in native['copies']:
        verify(copy,'native frozen copy')
        if copy.get('original'):verify(dict(path=copy['original'],sha256=copy['sha256'],bytes=copy['bytes']),'native original copy source')
    frozen_root=canonical(artifact['nativeFreeze']['path']).parent
    frozen_files={str(p) for p in frozen_root.rglob('*') if p.is_file()}
    need(frozen_files=={str(canonical(r['path'])) for r in native['copies']}|{str(canonical(artifact['nativeFreeze']['path']))},'all1391 frozen native members exact')
    metadata=read(refs['artifacts']['metadata']);policy=metadata['cryptoKeyOwnershipPolicy']
    need(metadata['engineSha256']==refs['artifacts']['engine']['sha256'] and metadata['engineBytes']==10002820 and metadata['gcStress'] is False and metadata['oomTesting'] is False,'normal actual native engine binding')
    need(policy['sourceFiles']==355 and policy['unchangedParentFiles']==350 and policy['changedSourceFiles']==5 and policy['exactComposedEdits']==20 and policy['runtimeValidation'] is None,'metadata source-only historical proof unchanged')
    idx=indexed(root['index'],extra=['completion.json'],label='actual WT output');need(len(idx['files'])==23,'23 output rows')
    completion=read(root['completion']);need(equal(completion['index'],{**root['index'],'path':'index.json'}) and equal(completion['result'],{**root['result'],'path':'results.json'}),'index/completion coupling')
    need(completion['state']=='CRYPTO_OWNER355_STOCK_WT_COMPLETE_EXTERNAL_PARENT_ZERO_AND_INDEPENDENT_REVIEW_REQUIRED','unreviewed completion kept')
    result=read(root['result']);authority=read(root['rootAction']);config=read(root['config']);terminal=read(root['externalTerminal']);started=read(root['started'])
    need(equal(config,dict(schemaVersion=1,sourceIndexSha256=SOURCE_SHA,rootAction=root['rootAction'])),'config exact')
    need(authority['sourceIndexSha256']==SOURCE_SHA and equal(authority['externalController'],root['externalLaunch']),'genuine source and launch authority')
    need(authority['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_STOCK_WASMTIME_V1' and authority['action']=='stock-wasmtime-validate' and authority['wasmtimeValidateAllowed'] is True,'genuine WT-only Root action')
    need(equal(authority['sourceIndependentReview'],root['sourceReview']),'action source peer binding')
    for name in ['normalReview','normalContract','artifactReview','artifactContract']:need(equal(authority[name],refs[name]),'action prior proof binding '+name)
    need(authority['variant']=='normal-off' and authority['componentSha256']==refs['artifacts']['component']['sha256'] and authority['outputRoot']==str(OUT) and authority['freshProcesses']==3 and authority['invocation']=='validate()' and authority['workerTimeoutMs']==600000 and authority['maxPipeBytes']==16777216 and authority['externalParentDeadlineSeconds']==2400,'exact finite action parameters')
    for key in ['nodeOracleAllowed','generatedJsAllowed','gcAllowed','oomAllowed','resetAllowed','otherVariantsAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim']:need(authority[key] is False,'bounded action '+key)
    need(terminal['rawExitCode']==0 and terminal['timeout'] is False and terminal['parentOwnedGroupGone'] is True and terminal['pid']==15457 and terminal['deadlineSeconds']==2400,'external parent raw success')
    need(equal(terminal['authority'],root['rootAction']) and equal(terminal['config'],root['config']) and equal(terminal['stdout'],root['externalStdout']) and equal(terminal['stderr'],root['externalStderr']),'external raw references')
    need(equal(started['argv'],terminal['argv']) and started['pid']==terminal['pid'],'started/terminal ownership')
    need(terminal['argv'][:2]==[refs['node']['path'],str(SOURCE/'run.mjs')] and equal(loads(terminal['argv'][2].encode()),root['config']),'exact parent argv')
    need(equal(started['selectedEnvironment'],dict(PYTHONDONTWRITEBYTECODE='1',BINARYEN_CORES='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='1')),'retained selected environment')
    need(root['externalStderr']['bytes']==0,'empty external stderr')
    baseline=read(refs['normalWrapper']);need(baseline['name']=='validate' and equal(baseline['args'],[]) and baseline['kind']=='return' and baseline['returnedType']=='string','actual normal complete string wrapper')
    model=expected();need(equal(loads(baseline['value'].encode()),model),'normal wrapper matches independent complete expected record')
    oracle=read(refs['nodeOracle']);oracle_expected=dict(schemaVersion=1,node='v22.14.0',tagHex=TAG,keys=[dict(format=f,type='secret',extractable=e,algorithm=dict(name='HMAC',hash=dict(name='SHA-256'),length=160),usages=['sign','verify'],tagHex=TAG,valid=True,invalid=False) for f,e in [('raw',False),('jwk',True)]],hostTestOracleOnly=True,guestNodeCryptoExportsAdded=False)
    need(equal(oracle,oracle_expected) and equal(read({**refs['nodeOracle'],'path':str(OUT/'node-oracle-reference.json')}),oracle),'whole retained oracle fields; no rerun')
    coverage=dict(rawPublicStrings=0,wholeDecodedBytes=0,runRecords=0,keyImportReturns=0,guestKeyImports=0,guestSignAttempts=0,guestVerifyAttempts=0,full32ByteSignatures=0,verificationBooleans=0,verifyTrue=0,verifyFalse=0,nativePromiseTypeErrorRefusals=0,prototypeGetterRefusals=0,noConstructorRefusals=0)
    sessions=[]
    args=['run','--invoke','validate()',refs['artifacts']['component']['path']]
    for ordinal,session in enumerate(root['sessions'],1):
        need(session['ordinal']==ordinal and session['pid']==[16735,17913,17995][ordinal-1],'fresh ordinal/PID')
        t=read(session['terminal']);walk_rows(t,'owned raw pipe')
        need(t['status']==0 and t['signal'] is None and t['spawnError'] is None and t['timedOut'] is False and t['externalSignal'] is None and t['signalCount']==0 and t['outputLimitExceeded'] is False and t['closed'] is True and t['ownedGroupGone'] is True and t['terminalExitZeroObserved'] is True and equal(t['signals'],[]) and equal(t['errors'],[]),'clean raw owned terminal')
        need(t['pid']==session['pid'] and t['timeoutMs']==600000 and t['maxOutputBytes']==16777216 and t['executable']==refs['wasmtime']['path'] and equal(t['args'],args),'actual literal zero-argument CLI')
        launch=loads((OUT/f'processes/validate-{ordinal}.launch.json').read_bytes());need(launch['detachedOwnedSession'] is True and launch['executable']==t['executable'] and equal(launch['args'],args) and launch['completed'] is False,'fresh launch is not terminal completion')
        argv=loads((OUT/f'validate-{ordinal}-argv.json').read_bytes());a=argv['accounting'];argument=[len(s.encode())+1 for s in [t['executable'],*args]]
        need(equal(argv['executable'],refs['wasmtime']) and equal(argv['args'],args) and equal(a['argumentBytes'],argument),'exact argv byte lengths')
        need(a['environmentBytes']==4228 and a['pointerBytes']==680 and a['totalBytes']==sum(argument)+4228+680==5108 and a['argMax']==1048576 and a['strictlyBelowArgMax'] is True,'retained argv accounting arithmetic')
        need(argv['fullEnvironmentValuesRetained'] is False and a['perArgumentLimit'] is None and a['kernelPaddingAndPerArgumentSemanticsNotProved'] is True and a['runtimeFeasibilityProved'] is False,'argument accounting scope')
        need(t['stderr']['bytes']==0 and t['stdout']['bytes']==17517,'whole pipes')
        raw=verify(session['rawStdout']).read_bytes();value=wave(raw);decoded=read(session['decodedString']);record=loads(value.encode())
        need(value.encode()==baseline['value'].encode(),'whole decoded UTF8 bytes equal actual normal wrapper')
        need(decoded['value']==value and decoded['ordinal']==ordinal and decoded['kind']=='whole-WAVE-scalar-string' and decoded['decodedBeforeSemanticAssertions'] is True,'independently decoded whole retained string')
        for n,target in [('rawStdout','stdout'),('rawStderr','stderr')]:need(equal(decoded[n],t[target]),'decoded raw descriptor')
        need(equal(decoded['terminal'],session['terminal']) and equal(record,read(session['record'])) and equal(record,model),'all fields exact independent expected record')
        coverage['rawPublicStrings']+=1;coverage['wholeDecodedBytes']+=len(value.encode());coverage['runRecords']+=len(record['records'])
        end=record['after']['counters']
        for dest,src in [('guestKeyImports','keyImportsAttempted'),('guestSignAttempts','signCalls'),('guestVerifyAttempts','verifyCalls')]:coverage[dest]+=end[src]
        for run in record['records']:
            for ob in run['observations']:
                if ob['phase']!='returned':continue
                if ob['operation']=='sign':coverage['full32ByteSignatures']+=1
                elif ob['operation']=='verify':coverage['verificationBooleans']+=1;coverage['verifyTrue' if ob['returned']['value'] else 'verifyFalse']+=1
                elif ob['operation']=='importKey':coverage['keyImportReturns']+=1
                else:coverage['nativePromiseTypeErrorRefusals']+=1
            if run['caseId']==3:coverage['prototypeGetterRefusals']+=len(run['result']['getters']);coverage['noConstructorRefusals']+=1
        sessions.append(dict(ordinal=ordinal,pid=session['pid'],terminal=session['terminal'],rawStdout=session['rawStdout'],rawStderr=session['rawStderr'],decodedString=session['decodedString'],record=session['record'],rawExitCode=0,ownedGroupGone=True,completeDecodedUtf8Sha256=hashlib.sha256(value.encode()).hexdigest(),completeDecodedUtf8Bytes=len(value.encode()),wholeNormalWrapperBytesEqual=True,allIndependentExpectedFieldsEqual=True))
        write(f'decoded/validate-{ordinal}.txt',value.encode(),raw=True)
    need(equal(coverage,dict(rawPublicStrings=3,wholeDecodedBytes=47187,runRecords=12,keyImportReturns=6,guestKeyImports=6,guestSignAttempts=33,guestVerifyAttempts=30,full32ByteSignatures=27,verificationBooleans=27,verifyTrue=15,verifyFalse=12,nativePromiseTypeErrorRefusals=9,prototypeGetterRefusals=12,noConstructorRefusals=3)),'complete bounded coverage')
    need(result['sourceIndexSha256']==SOURCE_SHA and equal(result['component'],refs['artifacts']['component']) and equal(result['wasmtime'],refs['wasmtime']),'result real tuples')
    need(result['state']=='CRYPTO_OWNER355_STOCK_WASMTIME_VALIDATE_COMPLETE_UNREVIEWED_V1' and equal(result['rootAction'],root['rootAction']),'original unreviewed receipt not relabeled')
    for name in ['allWholeFieldsMatchActualNormalWrapper','samePreviouslyAuditedComponent','oneOuterExportPerProcess']:need(result[name] is True,'actual bounded result '+name)
    for name in ['separateHostCallInterleavingProved','processOrRequestReuseProved','generatedJsImported','nodeOracleRerun','gcOomResetExecuted','finalizerFreeWipeOrIsolatedRootObserved','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:need(result[name] is False,'actual result scope '+name)
    need(equal(result['emittedImports'],[]) and equal(artifact['emittedImports'],[]),'prior static imports audit only, no new binary WIT decode')
    need(result['outerPublicStrings']==3 and result['withinExportRunRecords']==12 and result['guestKeyImports']==6 and result['guestSignAttempts']==33 and result['guestVerifyAttempts']==30,'actual count receipt joins')
    for i,s in enumerate(result['sessions']):need(s['pid']==sessions[i]['pid'] and equal(s['terminal'],sessions[i]['terminal']) and equal(s['record'],sessions[i]['record']),'result session binding')
    # Newly hash every input again. Cached checks alone do not serve as final rehash.
    for p,d in list(verified.items()):
        final=row(p);need(final['sha256']==d['sha256'] and final['bytes']==d['bytes'],'final input rehash '+p)
    for d in [root['externalTerminal'],root['externalLaunch'],root['started'],root['externalStdout'],root['externalStderr'],root['rootAction'],root['config'],dict(path=str(K/'ownership-wasmtime-v1-root-results.json'),sha256=ROOT_SHA,bytes=10035),root['index'],root['result'],root['completion']]:
        write('evidence/root/'+Path(d['path']).name,verify(d).read_bytes(),raw=True)
    for r in idx['files']:write('evidence/actual/'+r['path'],(OUT/r['path']).read_bytes(),raw=True)
    write('expected-complete-record.json',model)
    write('decoded-coverage.json',dict(coverage=coverage,sessions=sessions,expectedFullTagHex=TAG,fullTagBytes=32,oracleReexecuted=False,opaqueNativeKeyNotFullyInspected=True))
    write('rehashed-inputs.json',dict(schemaVersion=1,files=list(verified.values()),freshFinalRehash=True,symlinksAccepted=False,tmpAliasOnly='/tmp -> /private/tmp'))
    write('family-membership.json',dict(schemaVersion=1,families=observations))
    fixed=dict(schemaVersion=1,state=STATE,verifiedPassed=True,sourceIndexSha256=SOURCE_SHA,componentSha256=refs['artifacts']['component']['sha256'],nativeEngineSha256=refs['artifacts']['engine']['sha256'],nativeSourceFiles=355,normalOnly=True,boundedStockWasmtimeFixturePassed=True,actualIndexedFiles=23,actualRegularFiles=25,externalParentExitCode=0,allThreeFreshOwnedWasmtimeWorkersRawZeroClean=True,oneOuterExportPerFreshProcess=True,allWholePrimitiveStringsIndependentlyDecoded=True,wholeDecodedUtf8BytesMatchActualNormalWrapper=True,allFullFieldsMatchIndependentExpectedRecords=True,stockWasmtimeExecuted=True,keyOperationsInvokedByRootFixture=True,generatedModuleImportedInThisPhase=False,nodeOracleRerunInThisPhase=False,gcExecuted=False,oomExecuted=False,resetExecuted=False,applicationHolderReleaseObserved=True,separateHostCallInterleavingProved=False,processOrRequestReuseProved=False,finalizerFreeWipeOrIsolatedRootObserved=False,nativeGlobalCountersInstrumented=False,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,reviewerReadHashDecodeOnly=True,reviewerOwnerHelpersPreflightNodeCliGeneratedJsWasmtimeGuestCryptoNativeActionsInvoked=False,actionAuthorityIssued=False,futureActionAuthority=None)
    exact=dict(rootResult=dict(path=str(K/'ownership-wasmtime-v1-root-results.json'),sha256=ROOT_SHA,bytes=10035),sourceIndex=root['sourceIndex'],rootAction=root['rootAction'],config=root['config'],actualIndex=root['index'],actualResult=root['result'],actualCompletion=root['completion'],externalParentTerminal=root['externalTerminal'],externalLaunch=root['externalLaunch'],externalStarted=root['started'],externalStdout=root['externalStdout'],externalStderr=root['externalStderr'],normalWrapper=refs['normalWrapper'],nodeOracle=refs['nodeOracle'],node=refs['node'],wasmtime=refs['wasmtime'],normalContract=refs['normalContract'],artifactContract=refs['artifactContract'])
    write('data-results.json',dict(**fixed,coverage=coverage,sessions=sessions,requiredExactDescriptors=exact,artifacts=refs['artifacts'],sourceReview=root['sourceReview'],normalReview=root['normalReview'],artifactReview=root['artifactReview'],sourceMembers=len(source['files']),sourceClosureRows=13425,uniqueInputsRehashed=len(verified),freshFinalInputRehash=True,checks=checks,concreteBlockers=[]))
    print(json.dumps(dict(state='INDEPENDENT_DATA_REVIEW_FINISHED',checks=checks,uniqueInputsRehashed=len(verified),sourceClosureRows=13425,coverage=coverage)))

if __name__=='__main__':main()
