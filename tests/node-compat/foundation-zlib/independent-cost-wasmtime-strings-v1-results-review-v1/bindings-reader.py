#!/usr/bin/env python3
"""Independent READ/HASH/DATA source, plan, model and process review.

No owner proof helper, decoder, Node, CLI, codec, Jco, component or guest runs.
Request text and final WAVE expressions are independently constructed as DATA.
The independent peer reader decodes retained output and verifies full bytes.
"""
from pathlib import Path
import base64
import hashlib
import json
import os
import stat

HERE=Path(__file__).resolve().parent
Z=HERE.parent
OUT=Path('/tmp/starling-node-compat/zlib-cost-wasmtime-strings-v1-root')
CORRECT=Z/'independent-cost-jco-correctness-v3-results-review-v1'
SOURCE=Z/'cost-wasmtime-transport-candidate-v1'
ARMS=['native-on','fflate-on','fflate-off']
JOBS=[role+'-'+arm for role in ['small','largest'] for arm in ARMS]
PIDS=[85084,85087,85104,85107,85126,85187]
ROOT_SHA='4e37c006e4c516febd32894dab0e310c8bad9e7073272f9f478675b623be3e0f'
AUTH_SHA='91d57160e07d55cbae8819fec1ff5625ebd1dca1098d4d6d2a0f4cb9d2e917f5'
PLAN_SHA='b789d795e1a81f161e962b6357289bc572a41745fee9de59e01c583482d4025e'
MODEL_SHA='7ce260e887792279f4fb7a19a5f8c0bd9dea2a04e7fa54afa5d50d8535227a6f'
ROWS={}

def need(v,label):
    if not v:raise AssertionError(label)

def local(name):
    need(isinstance(name,str) and name and not name.startswith('/') and '\\' not in name and '\0' not in name and all(x not in ('','.','..') for x in name.split('/')),'finite local name');return name

def read(path,expected=None):
    path=Path(path);need(path.is_absolute(),'absolute path')
    canonical=str(path)
    if canonical.startswith('/tmp/'):canonical='/private/tmp/'+canonical[5:]
    need(str(path.resolve())==canonical,'only declared system tmp alias')
    for at in [path.resolve(),*list(path.resolve().parents)[:-1]]:need(not at.is_symlink(),'ordinary ancestors')
    before=path.lstat();need(stat.S_ISREG(before.st_mode),'ordinary file')
    h=hashlib.sha256()
    with path.open('rb') as stream:
        while block:=stream.read(4*1024**2):h.update(block)
    after=path.lstat();need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable file hash')
    row={'path':str(path),'sha256':h.hexdigest(),'bytes':before.st_size}
    if expected:need(row['sha256']==expected['sha256'] and row['bytes']==expected['bytes'],'exact tuple '+str(path))
    old=ROWS.get(str(path));need(old is None or old==row,'consistent repeated file tuple');ROWS[str(path)]=row;return row

def raw(path,expected=None):
    row=read(path,expected);value=Path(path).read_bytes();need(len(value)==row['bytes'] and hashlib.sha256(value).hexdigest()==row['sha256'],'stable data read');return value

def pairs(values):
    out={}
    for key,value in values:need(key not in out,'unique JSON key');out[key]=value
    return out

def data(path,expected=None):return json.loads(raw(path,expected),object_pairs_hook=pairs)
def exact(a,b):return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))

def indexed(root,digest,count=None):
    ix=read(root/'index.json');need(ix['sha256']==digest,'pinned finite index')
    v=data(root/'index.json',ix);need(v['schemaVersion']==1 and isinstance(v['files'],list),'finite indexed data')
    if count is not None:need(len(v['files'])==count,'exact indexed member count')
    names=set()
    for row in v['files']:
        name=local(row['path']);need(name not in names,'unique indexed member');names.add(name);read(root/name,row)
    return v,ix

def members(root):
    names=set()
    for base,dirs,files in os.walk(root,followlinks=False):
        need(all(not (Path(base)/x).is_symlink() for x in dirs),'ordinary output directories')
        for name in files:
            p=Path(base)/name;need(p.is_file() and not p.is_symlink(),'ordinary output files');names.add(p.relative_to(root).as_posix())
    return names

def quote_wave(value):
    # Every current record is ASCII JSON/base64. This independent DATA encoder
    # nevertheless handles scalar controls explicitly, without an owner helper.
    out=['"']
    for c in value:
        n=ord(c);need(not 0xd800<=n<=0xdfff,'Unicode scalar request')
        if c in ('"','\\'):out.extend(['\\',c])
        elif n<0x20:out.append('\\u{'+format(n,'x')+'}')
        else:out.append(c)
    out.append('"');return ''.join(out)

def request_for(record):
    request=json.dumps({'schemaVersion':1,'kind':'crossdecode','caseId':record['caseId'],'stageRecord':record},separators=(',',':'),ensure_ascii=False)
    return request,'validate('+quote_wave(request)+')'

def accounting(argv,environment):
    arg=[len(v.encode())+1 for v in argv];env=sum(len((k+'='+v).encode())+1 for k,v in environment.items());pointers=8*(len(argv)+len(environment)+2);total=sum(arg)+env+pointers
    return {'argumentBytes':arg,'environmentBytes':env,'pointerBytes':pointers,'totalBytes':total,'argMax':1048576,'strictlyBelowArgMax':total<1048576,'perArgumentLimit':None,'allArgumentsBelowKnownLimit':None,'kernelPaddingAndPerArgumentSemanticsNotProved':True,'runtimeFeasibilityProved':False}

def write(name,value):
    with (HERE/name).open('x') as stream:stream.write(json.dumps(value,indent=2)+'\n')

def review():
    rootpath=Z/'cost-wasmtime-strings-v1-root-results.json';rootrow=read(rootpath);need(rootrow['sha256']==ROOT_SHA and rootrow['bytes']==24523,'actual Root strings aggregate pinned')
    root=data(rootpath,rootrow);need(root['state']=='ROOT_OBSERVED_SIX_STOCK_WASMTIME42_SMALL_AND_LARGEST_STRING_VALIDATIONS_FULL_BYTES_V1' and root['rootSessionId']==37792,'actual finite strings result')
    for key in ['authority','plan','preparationSource','captureSource','parserSource','actualAggregateTerminal','transportSource','allSixtyProviderModel','actualEncoderStreams','stockWasmtime']:read(root[key]['path'],root[key])
    auth=data(root['authority']['path'],root['authority']);plan=data(root['plan']['path'],root['plan']);model=data(root['allSixtyProviderModel']['path'],root['allSixtyProviderModel'])
    need(read(root['authority']['path'])['sha256']==AUTH_SHA and read(root['plan']['path'])['sha256']==PLAN_SHA and read(root['allSixtyProviderModel']['path'])['sha256']==MODEL_SHA,'exact authority/plan/old model binding')
    need(auth['state']=='ROOT_AUTHORIZED_SIX_STOCK_WASMTIME42_COST_STRING_VALIDATIONS_V1' and auth['plan']==root['plan'] and auth['allowedExports']==['validate'] and auth['approvedJobs']==JOBS and auth['actualInvocations']==6 and auth['codecCallsPerWithinExportValidation']==2 and auth['exactChildEnvironment']=={'RAYON_NUM_THREADS':'1'} and auth['timeoutSecondsPerJob']==300 and auth['guestCodecCallsAllowed'] is True,'exact separately authorized six validate actions')
    for key in ['jcoOrHostNodeCodecCallsAllowed','nativeBuildOrComponentRebuildAllowed','timingAllowed','sourcePromotionAllowed','operationalAdmission']:need(auth[key] is False,'no broadened action authority')
    need(plan['state']=='SIX_REVIEWED_COST_WASMTIME_STRING_CALLS_PREPARED_UNEXECUTED_V1' and plan['rootExportAuthority'] is None and plan['wasmtimeExecuted'] is False and plan['timing'] is False,'historical prepared plan remains unmodified DATA')
    need(plan['correctnessReview']==root['correctnessReview']==auth['correctnessReview'] and plan['transportSource']==root['transportSource'] and plan['actualEncoderStreams']==root['actualEncoderStreams'] and plan['allProviderModel']==root['allSixtyProviderModel'],'whole plan proof tuple')
    correctness_index,correctness_ix=indexed(CORRECT,'e03bb0db65f6009e86a6d55e4553e820d143c702128976efc5ef47e092548083',22)
    review=data(root['correctnessReview']['result']['path'],root['correctnessReview']['result']);contract=data(root['correctnessReview']['contract']['path'],root['correctnessReview']['contract'])
    need(read(root['correctnessReview']['contract']['path'])['sha256']=='25411f2ecb278c1eeda7b27a0aafa47b29cc3d9a53221a327e9e5c94002936f1','accepted exact correctness contract')
    for key,value in contract['requiredFixedValues'].items():need(exact(review[key],value),'exact accepted correctness field '+key)
    need(exact(review['coverage'],contract['requiredCoverage']) and exact(review['components'],contract['requiredComponents']) and exact(review['actualComponentReviews'],contract['requiredActualComponentReviews']),'accepted complete correctness coverage/artifacts')
    for key,row in contract['requiredExactDescriptors'].items():need(review[key]==row,'required correctness descriptor binding');read(row['path'],row)
    actual_root=Path(review['actualIndex']['path']).parent;actual_index,_=indexed(actual_root,review['actualIndex']['sha256'],11440)
    need(members(actual_root)=={x['path'] for x in actual_index['files']}|{'index.json','completion.json'},'full actual correctness family membership remains exact')
    for row in data(CORRECT/'bindings-rehashed-inputs.json')['files']:read(row['path'],row)
    source,sourceix=indexed(SOURCE,'345ce70fd42c265137fb5653bdddfa47c5fb05463c24996f011697801fb1be56',29)
    peer=plan['sourceIndependentReview'];peerroot=Path(peer['index']['path']).parent
    indexed(peerroot,'ca663930a66e963deb7a5d725eb599c47c7d0a3537f071fd89e58039523b7fd2',5)
    source_review=data(peer['result']['path'],peer['result']);need(source_review['sourceOnly'] is True and source_review['sourceReviewPassed'] is True and source_review['ownerActionsInvoked'] is False,'transport source proof remains source-only')
    for row in data(SOURCE/'input-freeze.json')['files']:read(row['path'],row)
    need(plan['actualComponentReviews']==contract['requiredActualComponentReviews'],'exact successful current component proof descriptors')
    artifacts={}
    for arm,proof in plan['actualComponentReviews'].items():
        indexed(Path(proof['index']['path']).parent,proof['index']['sha256'],3);v=data(proof['result']['path'],proof['result'])
        need(v['state']=='INDEPENDENT_ZLIB_COST_COMPONENT_ARTIFACT_REVIEW_PASSED_V1' and v['verifiedPassed'] is True and v['arm']==arm and v['component']==review['components'][arm] and v['emittedImports']==[],'same accepted actual component/import facts')
        for key in ['component','glue','core','dts','wit','transpileMetadata','packageJson','code','nativeEngine','metadata','actualBuildAuthority','externalParentTerminal','ownedWorkerTerminal','workerIndex','workerCompletion','parentResult','workerResult']:read(v[key]['path'],v[key])
        artifacts[arm]=v
    host=read(root['stockWasmtime']['path'],root['stockWasmtime']);need(host==auth['wasmtime'] and host['sha256']=='a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c' and host['bytes']==50820352,'exact stock Wasmtime host')
    need(raw(SOURCE/'evidence/version.stdout.txt')==b'wasmtime 42.0.1 (6844a83b5 2026-02-25)\n','retained pinned stock host version')
    streams=data(root['actualEncoderStreams']['path'],root['actualEncoderStreams']);records=streams['primary']+streams['off'];need(len(streams['primary'])==45 and len(streams['off'])==15 and len({x['streamId'] for x in records})==60,'complete60 actual accepted stream records')
    need(model['state']=='ROOT_ALL_SIXTY_ACTUAL_ENCODER_RECORDS_ARGV_MODEL_DATA_ONLY_V1' and model['correctnessIndependentAcceptance']=='PENDING' and model['pureDataEncodingOnly'] is True and model['wasmtimeOrGuestOrCodecOrWorkerExecuted'] is False and model['actualLargestRecordTransportProved'] is False and model['rootExportAuthority'] is None,'old model pending/pre-execution statements preserved as historical DATA')
    need(model['actualEncoderStreams']==root['actualEncoderStreams'] and model['sourceIndex']==root['transportSource'] and model['exactProposedFutureChildEnvironment']=={'RAYON_NUM_THREADS':'1'} and model['argMax']==1048576 and model['compressedProviderRecords']==60 and model['proposedDecoderComponents']==review['components'],'old model exact source/catalog/environment/component data')
    recomputed=[];by_id={};env={'RAYON_NUM_THREADS':'1'}
    for record in records:
        encoded=base64.b64decode(record['encodedBase64'],validate=True);need(len(encoded)==record['encodedBytes'] and hashlib.sha256(encoded).hexdigest()==record['encodedSha256'] and base64.b64encode(encoded).decode()==record['encodedBase64'],'whole actual encoded record DATA')
        request,expression=request_for(record);perarm={arm:accounting([host['path'],'run','--invoke',expression,review['components'][arm]['path']],env) for arm in ARMS}
        row={**{key:record[key] for key in ['streamId','provider','fixture','format','caseId','encodedBytes','encodedSha256']},'requestCodeUnits':len(request.encode('utf-16-le'))//2,'requestBytes':len(request.encode()),'expressionBytes':len(expression.encode()),'expressionSha256':hashlib.sha256(expression.encode()).hexdigest(),'perArm':perarm}
        recomputed.append(row);by_id[record['streamId']]={'record':record,'request':request,'expression':expression,'row':row}
    need(recomputed==model['models'],'independent exact all60 final request/WAVE/180argv models')
    largest={}
    for arm in ARMS:
        maximum=max(x['perArm'][arm]['totalBytes'] for x in recomputed);candidates=[x['streamId'] for x in recomputed if x['perArm'][arm]['totalBytes']==maximum];largest[arm]={'maxTotalBytes':maximum,'candidates':candidates}
        need(candidates==['node-22.14.0.large-prng.gzip'],'unique maximum final request across60 current records')
    need(largest==model['largest'],'complete independent maximum model')
    aggregate=data(root['actualAggregateTerminal']['path'],root['actualAggregateTerminal']);need(aggregate['state']=='SIX_FRESH_STOCK_WASMTIME_STRING_VALIDATIONS_RAW_ZERO_UNPARSED' and aggregate['authority']==root['authority'] and aggregate['plan']==root['plan'] and aggregate['typedResultsParsed'] is False and aggregate['timing'] is False,'preserve completed raw unparsed terminal')
    need(len(plan['jobs'])==len(aggregate['records'])==len(root['observed'])==6 and [x['name'] for x in plan['jobs']]==JOBS and [x['job'] for x in root['observed']]==JOBS,'exact six expected jobs')
    expected_members={'plan.json','prepare.mjs','launch.py','parse.mjs','terminal.json'}|{name+'/'+file for name in JOBS for file in ['stdout.log','stderr.log','launch.json','terminal.json','decoded-string.txt','decoded-value.json','output-0.bin','output-1.bin']}
    need(members(OUT)==expected_members,'full exact53-file external membership')
    job_rows=[]
    for i,(job,observed,record) in enumerate(zip(plan['jobs'],root['observed'],aggregate['records'])):
        arm=job['arm'];role=job['role'];name=job['name'];selected='node-22.14.0.small-repeat.gzip' if role=='small' else largest[arm]['candidates'][0];v=by_id[selected]
        need(job['record']==v['record'] and job['request']==v['request'] and job['requestSha256']==hashlib.sha256(v['request'].encode()).hexdigest() and job['expressionSha256']==v['row']['expressionSha256'],'exact full request/record/hash/independent WAVE expression')
        argv=[host['path'],'run','--invoke',v['expression'],review['components'][arm]['path']];audit=accounting(argv,env)
        need(job['argv']==argv and job['environment']==env and job['accounting']==audit and job['component']==review['components'][arm],'full actual argv/environment/model/component')
        for key in ['component','rawStdout','rawStderr','terminal','launch','decodedString','decodedValue']:read(observed[key]['path'],observed[key])
        for row in observed['fullOutputBytes']:read(row['path'],row)
        terminal=data(observed['terminal']['path'],observed['terminal']);launch=data(observed['launch']['path'],observed['launch'])
        need(terminal==record and terminal['pid']==observed['pid']==PIDS[i] and terminal['rawExitCode']==observed['actualRawExitCode']==0 and terminal['spawnError'] is None and terminal['timeout'] is False and terminal['deadlineSeconds']==300 and terminal['ownedGroupGone'] is True,'actual fresh raw0/no error/no timeout/group gone')
        need(terminal['authority']==root['authority'] and terminal['component']==observed['component']==job['component'] and terminal['ordinaryExport']=='validate' and terminal['typedResultParsed'] is False and terminal['timing'] is False,'exact actual component/action/export scope')
        need(terminal['stdout']==observed['rawStdout'] and terminal['stderr']==observed['rawStderr'] and terminal['launch']==observed['launch'] and raw(observed['rawStderr']['path'])==b'','raw stream/capture crossbindings')
        need(launch=={'argv':argv,'environment':env,'accounting':audit,'plan':root['plan'],'job':name,'expressionSha256':job['expressionSha256'],'component':job['component']},'exact full launch record bytes interpreted as DATA')
        need(observed['argvAccounting']==audit and observed['record']=={key:v['record'][key] for key in ['streamId','caseId','encodedBytes','encodedSha256']},'Root selected record/byte model matches independent maximum')
        need(observed['actualLargestArgumentBytesAccepted']==(audit['argumentBytes'][3] if role=='largest' else None),'bounded actual accepted argument, not a portable limit')
        need(observed['rawStdout']['bytes']==(6232 if role=='small' else 1404206),'full expected stdout lengths')
        job_rows.append({'job':name,'arm':arm,'role':role,'pid':terminal['pid'],'component':job['component'],'record':observed['record'],'rawExitCode':0,'ownedGroupGone':True,'terminal':observed['terminal'],'launch':observed['launch'],'rawStdout':observed['rawStdout'],'rawStderr':observed['rawStderr'],'requestSha256':job['requestSha256'],'expressionSha256':job['expressionSha256'],'argvAccounting':audit,'actualArgumentBytesIncludingNulAccepted':audit['argumentBytes'][3],'elapsedOperationalSecondsOnly':terminal['elapsedSeconds']})
    need(root['actualFreshProcesses']==6 and root['actualOuterValidateCalls']==6 and root['actualGuestCodecCalls']==12 and root['fullOutputPayloadsCompared']==12 and root['smallStringArgumentPassedOnAllThree'] is True and root['maximumActualSixtyRecordRequestPassedOnAllThree'] is True and root['actualOsArgvSpawnAndWaveStringParsingObserved'] is True,'bounded actual process/transport outcome')
    for key in ['allFutureOrOneMiBEncodedRecordsSupportedClaim','portablePerArgumentLimitProved','separateHostCallInterleavingProved','componentReuseProved','timingExecuted','operationalAdmission','runtimeAcceptanceClaim']:need(root[key] is False,'no larger proof/authority transfer')
    evidence=HERE/'evidence';evidence.mkdir(exist_ok=True)
    for name,path in [('root-results.json',rootpath),('authority.json',Path(root['authority']['path'])),('aggregate-terminal.json',Path(root['actualAggregateTerminal']['path'])),('capture-source.py',Path(root['captureSource']['path'])),('preparation-source.mjs',Path(root['preparationSource']['path'])),('owner-parser-source.mjs',Path(root['parserSource']['path']))]:
        with (evidence/name).open('xb') as stream:stream.write(raw(path))
    parser=raw(root['parserSource']['path']).decode();need('await h.sync()' in parser and 'rawDurablyRetained:true' in parser and parser.index('await h.sync()')<parser.index('parseScalarStringOutput'),'retained Root parser source orders fsync before pure decode')
    write('all-sixty-model-review.json',{'schemaVersion':1,'state':'INDEPENDENT_ALL60_CURRENT_RECORD_FULL_REQUEST_WAVE_ARGV_MODELS_VERIFIED_V1','originalDataModel':root['allSixtyProviderModel'],'originalPendingLabelPreserved':'PENDING','separateAcceptedCorrectnessReview':root['correctnessReview'],'actualEncoderStreams':root['actualEncoderStreams'],'recordCount':60,'decoderComponentModels':180,'exactEnvironment':env,'independentModels':recomputed,'largest':largest,'allSixtyActualRecordsExecutedByWasmtime':False,'actualMaximumRequestExecutedOnThreeArms':True,'generalKernelOrPerArgumentLimitProved':False,'runtimeFeasibilityBeyondExactRecordedCallsProved':False,'ownerHelperOrCliInvoked':False})
    write('bindings-review.json',{'schemaVersion':1,'state':'INDEPENDENT_SIX_STOCK_WASMTIME_STRING_SOURCE_PLAN_MODEL_PROCESS_BINDINGS_VERIFIED_V1','rootAggregate':rootrow,'authority':root['authority'],'plan':root['plan'],'correctnessReview':root['correctnessReview'],'transportSource':root['transportSource'],'sourceIndependentReview':plan['sourceIndependentReview'],'actualEncoderStreams':root['actualEncoderStreams'],'actualComponentReviews':plan['actualComponentReviews'],'components':review['components'],'stockWasmtime':host,'externalFilesVerified':53,'actualFreshProcesses':6,'actualOuterValidateCalls':6,'actualGuestCodecCalls':12,'observed':job_rows,'allSixtyFullRequestModelsIndependentlyRecomputed':True,'largest':largest,'historicalPendingModelAndPreparedPlanUnchanged':True,'acceptedCorrectnessSeparatelyAuthenticated':True,'rootStockWasmtimeGuestCodecCallsExecuted':True,'reviewerReadHashDataOnly':True,'reviewerOwnerHelperNodeCliCodecJcoGuestOrHostActionsInvoked':False,'allSixtyRecordsExecutedByWasmtime':False,'portablePerArgumentLimitProved':False,'separateHostCallInterleavingProved':False,'componentReuseProved':False,'executedControlWorkloads':False,'actualBatchControlProofPending':True,'pilotTimingPrerequisitesSatisfied':False,'newBinaryWitDecodeExecuted':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False,'sourcePromotionAllowed':False,'timingAllowed':False,'uniqueLexicalInputTuplesRehashed':len(ROWS)})
    write('bindings-rehashed-inputs.json',{'schemaVersion':1,'files':list(ROWS.values())})
    print(json.dumps({'bindings':'passed','currentRecords':60,'actualJobs':6,'uniqueLexicalInputTuplesRehashed':len(ROWS)}))

if __name__=='__main__':review()
