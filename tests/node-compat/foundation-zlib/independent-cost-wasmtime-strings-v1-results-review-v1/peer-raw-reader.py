#!/usr/bin/env python3
"""Independent six-call WAVE/JSON/full-byte READ/HASH/DECODE DATA audit.

No owner helper, decoder, parser, Node, CLI, codec, Jco, guest or host is
imported or executed. Only standard-library ordinary-file data is examined.
"""
from pathlib import Path
import base64
import collections
import hashlib
import json
import stat

HERE=Path(__file__).resolve().parent
Z=HERE.parent
ROOT=Path('/tmp/starling-node-compat/zlib-cost-wasmtime-strings-v1-root')
ROOT_SHA='4e37c006e4c516febd32894dab0e310c8bad9e7073272f9f478675b623be3e0f'
PLAN_SHA='b789d795e1a81f161e962b6357289bc572a41745fee9de59e01c583482d4025e'
ORACLE_SHA='bf1312f33bc4df030b16a0f52a8018b2cf50c7dcf4fbad31699fbd9217c9fcf5'
NAMES=['identity','setup','observe','batch','checkpoint','stage','validate']
PIDS={'small-native-on':85084,'small-fflate-on':85087,'small-fflate-off':85104,'largest-native-on':85107,'largest-fflate-on':85126,'largest-fflate-off':85187}
FILES={}
FNV={}

def need(value,label):
    if not value:raise AssertionError(label)

def read(path,expected=None):
    path=Path(path);need(path.is_absolute(),'absolute file')
    canonical=str(path)
    if canonical.startswith('/tmp/'):canonical='/private/tmp/'+canonical[5:]
    need(str(path.resolve())==canonical,'only declared system tmp alias')
    for at in [path.resolve(),*list(path.resolve().parents)[:-1]]:need(not at.is_symlink(),'ordinary ancestors')
    before=path.lstat();need(stat.S_ISREG(before.st_mode),'ordinary data leaf');b=path.read_bytes();after=path.lstat()
    need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable data read')
    row={'path':str(path),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
    if expected:need(row['sha256']==expected['sha256'] and row['bytes']==expected['bytes'],'exact hash and bytes '+str(path))
    old=FILES.get(str(path));need(old is None or old==row,'same repeated data tuple');FILES[str(path)]=row;return b

def pairs(values):
    out={}
    for key,value in values:need(key not in out,'unique JSON object key');out[key]=value
    return out

def parse(value):return json.loads(value,object_pairs_hook=pairs)
def data(path,expected=None):return parse(read(path,expected))
def exact(a,b,label):need(json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':')),label)

def b64(value):
    need(isinstance(value,str),'base64 string');b=base64.b64decode(value,validate=True)
    need(base64.b64encode(b).decode()==value,'whole canonical base64');return b

def fnv(b):
    key=(len(b),hashlib.sha256(b).hexdigest())
    if key not in FNV:
        result=2166136261
        for byte in b:result=((result^byte)*16777619)&0xffffffff
        FNV[key]=result
    return FNV[key]

def fixture(name):
    if name=='small-repeat':return (b'abc123'*11)[:64]
    need(name=='large-prng','exact selected fixture name')
    result=bytearray(524288);state=0x6d2b79f5
    for index in range(len(result)):
        state=(state^((state<<13)&0xffffffff))&0xffffffff
        state=(state^(state>>17))&0xffffffff
        state=(state^((state<<5)&0xffffffff))&0xffffffff
        result[index]=state&255
    return bytes(result)

def wave_string(captured):
    need(0<len(captured)<=2097152 and captured.endswith(b'\n') and captured.count(b'\n')==1,'whole bounded typed string and one terminal LF')
    text=captured[:-1].decode('utf8','strict');need(not text.startswith('\ufeff') and len(text)>=2 and text[0]=='"' and text[-1]=='"','one quoted WAVE string')
    simple={'\\':'\\','"':'"',"'":"'",'t':'\t','n':'\n','r':'\r'};out=[];counts=collections.Counter();i=1
    while i<len(text)-1:
        ch=text[i];i+=1
        if ch=='\\':
            need(i<len(text)-1,'complete escape');kind=text[i];i+=1;counts[kind]+=1
            if kind=='u':
                need(i<len(text)-1 and text[i]=='{','brace scalar escape');i+=1;start=i
                while i<len(text)-1 and text[i]!='}':i+=1
                digits=text[start:i];need(i<len(text)-1 and 1<=len(digits)<=6 and all(x in '0123456789abcdefABCDEF' for x in digits),'one to six complete scalar hex digits')
                value=int(digits,16);need(value<=0x10ffff and not 0xd800<=value<=0xdfff,'Unicode scalar');out.append(chr(value));i+=1
            else:need(kind in simple,'finite WAVE escape');out.append(simple[kind])
        else:need(ch!='"' and ord(ch)>=0x20 and not 0xd800<=ord(ch)<=0xdfff,'ordinary WAVE scalar');out.append(ch)
    need(i==len(text)-1,'whole WAVE result consumed');return ''.join(out),dict(counts)

def window(b):return {'byteOffset':8,'byteLength':len(b),'backingBytes':len(b)+16,'prefix':[165]*8,'suffix':[90]*8,'construction':'new ordinary ArrayBuffer; fixed/attached/unshared by construction'}

def counters(observes=0,stage=False):
    entries={'identity':0,'setup':1,'observe':observes,'batch':0,'checkpoint':0,'stage':1 if stage else 0,'validate':1}
    return {'publicFunctionEntries':sum(entries.values()),'perExportEntries':entries,'codecCalls':observes,'controlOperations':0}

def expected_value(job,row,inputbytes,outputbytes):
    record=job['record'];caseid=record['caseId'];stageinfo={'caseId':caseid,'streamId':record['streamId'],'provider':record['provider'],'fixture':record['fixture'],'format':record['format'],'parentDeclaredSha256':record['encodedSha256']}
    def state(source,retained=False,stage=None):return {'activeCaseId':caseid,'inputSource':source,'stagedValidation':stage,'prepared':True,'retainedUntimedOutput':retained}
    setup={'schemaVersion':1,'kind':'codec-cost-setup-v1','caseId':caseid,'caseName':row['id'],'inputSource':'node-oracle-input','input':window(inputbytes),'inputFNV1aU32':fnv(inputbytes),'parentDeclaredInputSha256':record['encodedSha256'],'oracleSha256':ORACLE_SHA,'stagedValidationCleared':True,'priorOutputCleared':True,'counters':counters(),'state':state('node-oracle-input')}
    stage={'schemaVersion':1,'kind':'codec-cost-stage-ack-v1','caseId':caseid,'streamId':record['streamId'],'provider':record['provider'],'fixture':record['fixture'],'format':record['format'],'decodedBytes':len(inputbytes),'decodedFNV1aU32':fnv(inputbytes),'parentDeclaredSha256':record['encodedSha256'],'sha256RecomputedInGuest':False,'input':window(inputbytes),'codecInvoked':False,'counters':counters(stage=True),'state':state('staged-validation',stage=stageinfo)}
    observations=[]
    for index in range(2):
        first=index==0
        ownership={'nonemptyOutputInputIndependent':True,'emptyBackingRelationRecorded':None,'previousComparable':not first,'previousFullBytesUnchanged':None if first else True,'successiveIndependentBacking':None if first else True,'mutationProbe':{'performed':not first,'reason':'no previous comparable output' if first else None,'currentFullBytesUnchanged':None if first else True,'inputFullBytesUnchanged':None if first else True,'previousRestored':None if first else True}}
        observations.append({'schemaVersion':1,'kind':'codec-cost-observation-v1','caseId':caseid,'caseName':row['id'],'provider':'native' if job['arm']=='native-on' else 'fflate','operation':row['operation'],'format':row['format'],'direction':'decode','logicalUncompressedBytes':len(outputbytes),'inputSource':'staged-validation','stage':stageinfo,'input':{**window(inputbytes),'fnv1aU32':fnv(inputbytes),'fullInputUnchanged':True},'output':{'bytes':len(outputbytes),'fnv1aU32':fnv(outputbytes),'base64':base64.b64encode(outputbytes).decode(),'byteOffset':0,'backingBytes':len(outputbytes),'isBuffer':True},'ownership':ownership,'counters':counters(index+1,True)})
    return {'schemaVersion':1,'kind':'codec-cost-validation-v1','requestKind':'crossdecode','caseId':caseid,'setup':setup,'stage':stage,'observations':observations,'withinOneOuterExport':True,'separateHostCallInterleavingProved':False,'counters':counters(2,True),'state':state('staged-validation',True,stageinfo)}

def write(name,value):
    with (HERE/name).open('x') as stream:stream.write(json.dumps(value,indent=2)+'\n')

def main():
    rootpath=Z/'cost-wasmtime-strings-v1-root-results.json';rootbytes=read(rootpath);need(hashlib.sha256(rootbytes).hexdigest()==ROOT_SHA and len(rootbytes)==24523,'exact Root result bytes');root=parse(rootbytes)
    plan=data(root['plan']['path'],root['plan']);need(hashlib.sha256(read(root['plan']['path'])).hexdigest()==PLAN_SHA,'exact plan bytes')
    aggregate=data(root['actualAggregateTerminal']['path'],root['actualAggregateTerminal']);need(len(aggregate['records'])==6,'six raw process records')
    cases=data(Z/'cost-jco-correctness-candidate-v2/cases.json');need(len(cases)==30,'thirty exact case definitions')
    oraclepath=Z/'reviewed-cost-node-oracle-v3/node-oracle.json';oraclebytes=read(oraclepath);need(hashlib.sha256(oraclebytes).hexdigest()==ORACLE_SHA,'exact reviewed oracle');oracle=parse(oraclebytes)
    read(Z/'cost-guest-oracle-candidate-v2/runtime.mjs');read(Z/'cost-guest-oracle-candidate-v2/fixtures.mjs')
    catalog=data(root['actualEncoderStreams']['path'],root['actualEncoderStreams']);allrecords=catalog['primary']+catalog['off'];records={x['streamId']:x for x in allrecords}
    need(len(records)==60 and len(root['observed'])==len(plan['jobs'])==6,'six calls use actual sixty-record data catalog')
    rawfixtures={x['id']:x for x in oracle['rawFixtures']};nodeinputs={x['caseId']:x for x in oracle['encodedStreams']};jobs={x['name']:x for x in plan['jobs']};proofs=[];rawtotal=decodedtotal=0;pidset=set();roles=collections.Counter()
    for observed,record in zip(root['observed'],aggregate['records']):
        name=observed['job'];job=jobs[name];role=job['role'];arm=job['arm'];roles[role]+=1
        need(name in PIDS and observed['pid']==record['pid']==PIDS[name] and record['pid'] not in pidset,'six exact distinct Root PID records');pidset.add(record['pid'])
        terminal=data(observed['terminal']['path'],observed['terminal']);exact(terminal,record,'raw aggregate/standalone record equality')
        need(terminal['rawExitCode']==observed['actualRawExitCode']==0 and terminal['timeout'] is False and terminal['spawnError'] is None and terminal['ownedGroupGone'] is True and terminal['ordinaryExport']=='validate' and terminal['typedResultParsed'] is False and terminal['timing'] is False,'clean immutable unparsed validate capture')
        need(observed['arm']==record['arm']==arm and observed['role']==record['role']==role,'job/role/arm equality')
        staged=job['record'];case=cases[staged['caseId']];need(case['index']==staged['caseId'] and case['fixture']==staged['fixture'] and case['direction']=='decode' and case['format']==staged['format']=='gzip','exact selected decode cases')
        exact(staged,records[staged['streamId']],'full actual encoder record');exact(staged,nodeinputs[staged['caseId']],'setup uses same actual Node-oracle input')
        compressed=b64(staged['encodedBase64']);need(len(compressed)==staged['encodedBytes'] and fnv(compressed)==staged['encodedFNV1aU32'] and hashlib.sha256(compressed).hexdigest()==staged['encodedSha256'],'whole staged compressed bytes/hash/FNV')
        request={'schemaVersion':1,'kind':'crossdecode','caseId':staged['caseId'],'stageRecord':staged};exact(parse(job['request']),request,'full string argument request')
        need(job['request']==json.dumps(request,separators=(',',':')) and hashlib.sha256(job['request'].encode()).hexdigest()==job['requestSha256'],'whole exact request string')
        launch=data(observed['launch']['path'],observed['launch']);expression=launch['argv'][3];need(expression.startswith('validate(') and expression.endswith(')'),'actual validate expression')
        decoded_request,inputescapes=wave_string((expression[9:-1]+'\n').encode());need(decoded_request==job['request'],'independently decoded WAVE input is exact whole request')
        output=fixture(staged['fixture']);oraw=rawfixtures[staged['fixture']];need(b64(oraw['base64'])==output and len(output)==oraw['bytes'] and hashlib.sha256(output).hexdigest()==oraw['sha256'] and fnv(output)==oraw['fnv1aU32'],'independently reconstructed fixture matches reviewed oracle bytes')
        capture=read(observed['rawStdout']['path'],observed['rawStdout']);need(read(observed['rawStderr']['path'],observed['rawStderr'])==b'','empty actual raw stderr');decoded,escapes=wave_string(capture);value=parse(decoded);expected=expected_value(job,case,compressed,output)
        exact(value,expected,'every inner JSON field/counter/stage/state/ownership value');need(decoded==json.dumps(expected,separators=(',',':')),'whole inner text preserved without normalization')
        need(decoded.encode()==read(observed['decodedString']['path'],observed['decodedString']),'independent decoded string equals Root afterimage');exact(value,data(observed['decodedValue']['path'],observed['decodedValue']),'independent JSON equals Root afterimage')
        need(len(observed['fullOutputBytes'])==2 and observed['expectedRawBytes']==len(output) and observed['wholeFixtureBytesAndCountersVerified'] is True,'two complete retained outputs expected')
        for index,descriptor in enumerate(observed['fullOutputBytes']):need(read(descriptor['path'],descriptor)==output==b64(value['observations'][index]['output']['base64']),'complete output binary / JSON / fixture equality')
        need(observed['record']=={key:staged[key] for key in ['streamId','caseId','encodedBytes','encodedSha256']},'observed encoded-record identity')
        expected_raw,expected_decoded=(6232,5665) if role=='small' else (1404206,1403639)
        need(len(capture)==expected_raw and len(decoded.encode())==expected_decoded,'exact complete raw and decoded sizes');rawtotal+=len(capture);decodedtotal+=len(decoded.encode())
        proofs.append({'job':name,'arm':arm,'role':role,'pid':terminal['pid'],'rawStdout':observed['rawStdout'],'terminal':observed['terminal'],'record':observed['record'],'rawBytes':len(capture),'decodedUtf8Bytes':len(decoded.encode()),'decodedUtf16CodeUnits':len(decoded.encode('utf-16-le'))//2,'independentDecodedStringSha256':hashlib.sha256(decoded.encode()).hexdigest(),'completeOuterResultConsumed':True,'exactWholeInnerJsonAndText':True,'independentInputWaveStringEqualsExactRequest':True,'inputBytes':len(compressed),'inputSha256':hashlib.sha256(compressed).hexdigest(),'inputFnv1aU32':fnv(compressed),'fixtureBytes':len(output),'fixtureSha256':hashlib.sha256(output).hexdigest(),'fixtureFnv1aU32':fnv(output),'fullOutputPayloadsVerified':2,'counters':value['counters'],'finalGuestState':value['state'],'allStageInputWindowSentinelMetadataExact':True,'inputAndPriorStabilityReportsExact':True,'mutationAndRestorationReportExact':True,'outerObservedEscapeCounts':escapes,'inputObservedEscapeCounts':inputescapes,'separateHostCallInterleavingProved':False,'checkpointOrResetCalled':False,'rootOrdinaryExportExecuted':'validate','rootCodecCalls':2,'reviewerCodecCalls':0})
    need(dict(roles)=={'small':3,'largest':3},'exact two roles across three arms')
    report={'schemaVersion':1,'state':'INDEPENDENT_SIX_STOCK_WASMTIME_STRING_RAW_JSON_BYTE_COUNTER_REVIEW_PASSED_V1','verifiedPassed':True,'reviewer':'/root/cost_component_results_review/wt_strings_raw_audit','rootResultSha256':ROOT_SHA,'planSha256':PLAN_SHA,'actualFreshProcesses':6,'actualOuterValidateCalls':6,'actualGuestCodecCalls':12,'actualNamedEntriesIncludingValidateInternals':30,'controlOperations':0,'rawTypedReturnsIndependentlyDecoded':6,'fullOutputPayloadsCompared':12,'rawStdoutBytesDecoded':rawtotal,'decodedUtf8Bytes':decodedtotal,'allWholeInnerJsonFieldsAndTextCompared':True,'allInputArgumentWaveStringsIndependentlyDecoded':True,'allInputCompressedBytesShaFnvAndCanonicalBase64Verified':True,'independentFixtureDefinitionsComparedWithOracle':2,'stageAndSentinelWindowsVerified':6,'withinExportAdjacentWholeOutputPairsEqual':6,'nonemptyPriorStabilityMutationRestorationReportsExact':6,'rootFinalStatePreparedAndRetained':True,'rootCheckpointOrResetCalls':0,'independentPostExitGuestHeapAliasingInspection':False,'ownershipScope':'Full returned bytes, exact input windows/sentinels and instrumented prior/mutation/restoration fields checked against pinned guest source; guest heap aliasing is not inspected after exit. Final state remains prepared/staged with retained output because no checkpoint/reset was called.','jobs':proofs,'reviewMode':'READ/HASH/DECODE DATA only','reviewerOwnerHelperNodeParserCliCodecJcoGuestOrHostActionsExecuted':False,'deflateBitstreamsDecodedByReviewer':False,'generalWaveParserProof':False,'separateHostCallInterleavingProved':False,'componentReuseProved':False,'portablePerArgumentLimitProved':False,'generalResourceOrRuntimeFeasibilityProved':False,'executedControlWorkloads':False,'actualBatchControlProofPending':True,'runtimeAcceptanceClaim':False,'operationalAdmission':False,'sourcePromotionAllowed':False,'timingAllowed':False,'uniqueInputFilesRehashed':len(FILES)}
    write('peer-raw-review.json',report);write('peer-raw-inputs.json',{'schemaVersion':1,'files':list(FILES.values())});print(json.dumps({'review':'passed','returns':6,'outputs':12,'uniqueInputFiles':len(FILES)}))

if __name__=='__main__':main()
