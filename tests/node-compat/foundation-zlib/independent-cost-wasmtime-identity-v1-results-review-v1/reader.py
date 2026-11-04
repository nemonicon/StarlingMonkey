#!/usr/bin/env python3
"""Independent READ/HASH/DATA decoder for retained identity-only records.

No owner parser, helper, Node, CLI, host, component, guest or codec is run.
Wasm/native binaries are hashed as opaque files. The new finite decoder below
operates only on retained UTF8 typed-string text, then verifies complete JSON.
"""
from pathlib import Path
import hashlib
import json
import os
import stat

HERE=Path(__file__).resolve().parent
Z=HERE.parent
OUT=Path('/tmp/starling-node-compat/zlib-cost-wasmtime-identity-v1-root')
SOURCE=Z/'cost-wasmtime-transport-candidate-v1'
SOURCE_SHA='345ce70fd42c265137fb5653bdddfa47c5fb05463c24996f011697801fb1be56'
PEER_SHA='ca663930a66e963deb7a5d725eb599c47c7d0a3537f071fd89e58039523b7fd2'
AUTH_SHA='7e79829f7921a7cbd31a6c92165e92b019abf2b753d07ae8ecd14d8cfb5c98a6'
ROOT_SHA='2fa1e262c0eb23b2294628f022b9aa49e4025ce3444f85300db1bb16d0db74f0'
ARMS=['native-on','fflate-on','fflate-off']
PIDS={'native-on':67649,'fflate-on':68741,'fflate-off':69829}
NAMES=['identity','setup','observe','batch','checkpoint','stage','validate']
ROWS={}

def need(v,message):
    if not v:raise AssertionError(message)

def local(name):
    need(isinstance(name,str) and name and not name.startswith('/') and '\\' not in name and '\0' not in name and all(x not in ('','.','..') for x in name.split('/')),'finite local name');return name

def read(path,expected=None):
    path=Path(path);need(path.is_absolute(),'absolute input path')
    canonical=str(path)
    if canonical.startswith('/tmp/'):canonical='/private/tmp/'+canonical[5:]
    need(str(path.resolve())==canonical,'only declared system tmp alias')
    for at in [path.resolve(),*list(path.resolve().parents)[:-1]]:need(not at.is_symlink(),'ordinary source ancestors')
    before=path.lstat();need(stat.S_ISREG(before.st_mode),'ordinary source leaf')
    h=hashlib.sha256()
    with path.open('rb') as stream:
        while block:=stream.read(4*1024**2):h.update(block)
    after=path.lstat();need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable source hash read')
    row={'path':str(path),'sha256':h.hexdigest(),'bytes':before.st_size}
    if expected:need(row['sha256']==expected['sha256'] and row['bytes']==expected['bytes'],'exact file tuple '+str(path))
    old=ROWS.get(str(path));need(old is None or old==row,'stable repeated descriptor');ROWS[str(path)]=row;return row

def raw(path,expected=None):
    row=read(path,expected);value=Path(path).read_bytes();need(len(value)==row['bytes'] and hashlib.sha256(value).hexdigest()==row['sha256'],'stable second data read');return value

def unique_pairs(pairs):
    out={}
    for key,value in pairs:need(key not in out,'unique JSON object key');out[key]=value
    return out

def parse_json(value):return json.loads(value,object_pairs_hook=unique_pairs)
def data(path,expected=None):return parse_json(raw(path,expected))

def index(root,digest,count=None):
    ix=read(root/'index.json');need(ix['sha256']==digest,'exact pinned index')
    v=data(root/'index.json',ix);need(v['schemaVersion']==1 and isinstance(v['files'],list),'finite indexed packet')
    if count is not None:need(len(v['files'])==count,'exact indexed member count')
    seen=set()
    for row in v['files']:
        name=local(row['path']);need(name not in seen,'unique index member');seen.add(name);read(root/name,row)
    return v,ix

def members(root):
    names=set()
    for base,dirs,files in os.walk(root,followlinks=False):
        need(all(not (Path(base)/x).is_symlink() for x in dirs),'ordinary output directories')
        for name in files:
            p=Path(base)/name;need(p.is_file() and not p.is_symlink(),'ordinary output file');names.add(p.relative_to(root).as_posix())
    return names

def write(name,value):
    target=HERE/name;target.parent.mkdir(parents=True,exist_ok=True)
    b=(json.dumps(value,indent=2)+'\n').encode() if not isinstance(value,bytes) else value
    with target.open('xb') as stream:stream.write(b);stream.flush();os.fsync(stream.fileno())

def wave_identity_string(captured):
    # This new finite reader is independent of both retained owner JS parsers.
    need(0<len(captured)<=4096 and captured.endswith(b'\n') and captured.count(b'\n')==1,'complete bounded single terminal LF record')
    text=captured[:-1].decode('utf-8','strict')
    need(not text.startswith('\ufeff') and len(text)>=2 and text[0]=='"' and text[-1]=='"','one complete quoted typed string')
    simple={'\\':'\\','"':'"',"'":"'",'t':'\t','n':'\n','r':'\r'}
    i=1;out=[];escapes={}
    while i<len(text)-1:
        c=text[i];i+=1
        if c=='\\':
            need(i<len(text)-1,'complete escape');kind=text[i];i+=1;escapes[kind]=escapes.get(kind,0)+1
            if kind=='u':
                need(i<len(text)-1 and text[i]=='{','WAVE scalar brace escape');i+=1;start=i
                while i<len(text)-1 and text[i]!='}':i+=1
                digits=text[start:i];need(i<len(text)-1 and 1<=len(digits)<=6 and all(x in '0123456789abcdefABCDEF' for x in digits),'bounded hex scalar escape')
                scalar=int(digits,16);need(scalar<=0x10ffff and not 0xd800<=scalar<=0xdfff,'Unicode scalar escape');out.append(chr(scalar));i+=1
            else:need(kind in simple,'known WAVE simple escape');out.append(simple[kind])
        else:
            need(c!='"' and ord(c)>=0x20 and not 0xd800<=ord(c)<=0xdfff,'ordinary complete string scalar');out.append(c)
    need(i==len(text)-1,'exact typed string consumption')
    value=''.join(out);need(value.encode('utf-8').decode('utf-8')==value,'lossless decoded UTF8');return value,escapes

def expected_identity(arm):
    return {'schemaVersion':1,'kind':'codec-cost-identity-v1','version':'bounded-zlib-cost-guest-v1','provider':'native' if arm=='native-on' else 'fflate','providerSourceVersion':'registered-node-zlib-m0.13' if arm=='native-on' else 'fflate-browser-0.8.3','oracleSha256':'bf1312f33bc4df030b16a0f52a8018b2cf50c7dcf4fbad31699fbd9217c9fcf5','primaryCases':30,'controlCaseRanges':{'consumeInput':[30,59],'copyInputAndConsume':[60,89],'harnessNoCodec':[90,119]},'exports':NAMES,'snapshotState':{'prepared':False,'staged':False,'retainedOutput':False,'codecCalls':0,'resources':0},'counterMeaning':'named-function entries including internal validate calls; outer host calls are parent raw records','counters':{'publicFunctionEntries':1,'perExportEntries':{name:1 if name=='identity' else 0 for name in NAMES},'codecCalls':0,'controlOperations':0},'state':{'activeCaseId':None,'inputSource':None,'stagedValidation':None,'prepared':False,'retainedUntimedOutput':False},'codecPrewarmedAtSnapshot':False}

def review():
    rootpath=Z/'cost-wasmtime-identity-v1-root-results.json';rootrow=read(rootpath);need(rootrow['sha256']==ROOT_SHA and rootrow['bytes']==11270,'actual identity result pinned')
    root=data(rootpath,rootrow);need(root['state']=='ROOT_OBSERVED_THREE_FRESH_STOCK_WASMTIME42_COST_IDENTITY_TYPED_STRINGS_V1' and root['rootSessionId']==25871,'Root identity result scope')
    for key in ('rootAuthority','transportSource','actualAggregateTerminal','externalLaunchSource','typedParserSource','wasmtime'):read(root[key]['path'],root[key])
    auth=data(root['rootAuthority']['path'],root['rootAuthority']);need(read(root['rootAuthority']['path'])['sha256']==AUTH_SHA,'separate identity action authority pinned')
    need(auth['state']=='ROOT_AUTHORIZED_STOCK_WASMTIME42_THREE_COST_IDENTITIES_V1' and auth['allowedExports']==['identity'] and auth['invocationExpression']=='identity()' and auth['invocationsPerArm']==1 and auth['arms']==ARMS and auth['exactChildEnvironment']=={'RAYON_NUM_THREADS':'1'} and auth['timeoutSecondsPerArm']==300 and auth['expectedEmittedImports']==[],'exact finite identity authority')
    for key in ('guestCodecCallsAllowed','jcoExecutionAllowed','nativeBuildAllowed','componentRebuildAllowed','timingAllowed','sourcePromotionAllowed','operationalAdmission'):need(auth[key] is False,'identity authority does not extend action scope')
    source,sourceix=index(SOURCE,SOURCE_SHA,29)
    need(auth['transportSource']==root['transportSource'] and root['transportSource']['sha256']==SOURCE_SHA and auth['sourceIndependentReview']==root['sourceIndependentReview'],'authority/current source peer binding')
    peerroot=Path(auth['sourceIndependentReview']['index']['path']).parent
    peer,peerix=index(peerroot,PEER_SHA,5);peervalue=data(auth['sourceIndependentReview']['result']['path'],auth['sourceIndependentReview']['result'])
    need(peervalue['state']=='INDEPENDENT_ZLIB_COST_WASMTIME_TRANSPORT_SOURCE_REVIEW_PASSED_V1' and peervalue['sourceOnly'] is True and peervalue['sourceReviewPassed'] is True and peervalue['ownerActionsInvoked'] is False and peervalue['sourceIndexSha256']==SOURCE_SHA,'source proof remains source only')
    freeze=data(SOURCE/'input-freeze.json');need(len(freeze['files'])==52 and freeze['runtimeActionSeal'] is False,'source preparation context finite/not action authority')
    for row in freeze['files']:read(row['path'],row)
    host=read(root['wasmtime']['path'],root['wasmtime']);need(host==auth['wasmtime'] and host['sha256']=='a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c' and host['bytes']==50820352,'actual stock host bytes')
    need(raw(SOURCE/'evidence/version.stdout.txt')==b'wasmtime 42.0.1 (6844a83b5 2026-02-25)\n','retained pinned version observation')
    artifactroot=Z/'independent-cost-component-v3-results-review-v1';_,artifactix=index(artifactroot,'9ab82077a47c3935a7bc1accec1cbcc385ef35c7c3bf1134b7dc9f81ca0d9893',26)
    common=data(artifactroot/'rehashed-common-inputs.json')['files']
    for row in common:read(row['path'],row)
    aggregate=data(root['actualAggregateTerminal']['path'],root['actualAggregateTerminal'])
    need(aggregate['state']=='THREE_STOCK_WASMTIME_IDENTITY_RAW_ZERO_UNPARSED' and len(aggregate['records'])==3 and aggregate['typedResultsParsed'] is False and aggregate['codecCalls']==0 and aggregate['stringArgumentsTested'] is False and aggregate['timing'] is False and aggregate['authority']==root['rootAuthority'],'immutable raw terminal remains unparsed diagnostic record')
    need([x['arm'] for x in root['observed']]==ARMS and [x['arm'] for x in aggregate['records']]==ARMS,'exactly three expected arm records')
    expected_members={'launch.py','parse.mjs','terminal.json'}|{arm+'/'+name for arm in ARMS for name in ['launch.json','terminal.json','stdout.log','stderr.log','decoded-string.txt','decoded-value.json']}
    need(members(OUT)==expected_members,'full retained external output membership')
    evidence=HERE/'evidence';evidence.mkdir()
    for name,path in [('root-results.json',rootpath),('root-authority.json',Path(root['rootAuthority']['path'])),('aggregate-terminal.json',Path(root['actualAggregateTerminal']['path'])),('launch.py',Path(root['externalLaunchSource']['path'])),('owner-parse.mjs',Path(root['typedParserSource']['path']))]:write('evidence/'+name,raw(path))
    actual=[]
    descriptors=['component','glue','core','dts','wit','transpileMetadata','packageJson','code','nativeEngine','metadata','actualBuildAuthority','externalParentTerminal','ownedWorkerTerminal','workerIndex','workerCompletion','parentResult','workerResult']
    for observed,record in zip(root['observed'],aggregate['records']):
        arm=observed['arm'];proof=auth['artifactReviews'][arm];proofroot=Path(proof['index']['path']).parent
        index(proofroot,proof['index']['sha256'],3);artifact=data(proof['result']['path'],proof['result'])
        need(artifact['state']=='INDEPENDENT_ZLIB_COST_COMPONENT_ARTIFACT_REVIEW_PASSED_V1' and artifact['verifiedPassed'] is True and artifact['arm']==arm and artifact['emittedImports']==[],'unchanged successful actual component artifact proof')
        for key in descriptors:read(artifact[key]['path'],artifact[key])
        for row in data(proofroot/'rehashed-inputs.json')['files']:read(row['path'],row)
        for key in ('component','rawStdout','rawStderr','terminal','launch','decodedString','decodedValue'):read(observed[key]['path'],observed[key])
        terminal=data(observed['terminal']['path'],observed['terminal']);launch=data(observed['launch']['path'],observed['launch'])
        need(terminal==record and terminal['pid']==observed['pid']==PIDS[arm] and terminal['rawExitCode']==observed['rawExitCode']==0 and terminal['timeout'] is False and terminal['deadlineSeconds']==300 and terminal['ownedGroupGone'] is True and terminal['cleanupSignals']==[],'actual raw0/no timeout/clean group record')
        need(terminal['authority']==root['rootAuthority'] and terminal['component']==observed['component']==artifact['component'] and terminal['ordinaryExport']=='identity' and terminal['codecExportInvoked'] is False and terminal['typedResultParsed'] is False and terminal['timing'] is False,'raw actual component/authority/export scope')
        need(terminal['launch']==observed['launch'] and terminal['stdout']==observed['rawStdout'] and terminal['stderr']==observed['rawStderr'],'raw standalone/aggregate/root stream crossbindings')
        argv=[host['path'],'run','--invoke','identity()',artifact['component']['path']];env={'RAYON_NUM_THREADS':'1'}
        need(launch['argv']==argv and launch['exactEnvironment']==env==auth['exactChildEnvironment']==root['exactChildEnvironment'],'exact full actual argv and child environment')
        argument_bytes=[len(x.encode('utf-8'))+1 for x in argv];envbytes=sum(len((k+'='+v).encode('utf-8'))+1 for k,v in env.items());pointerbytes=8*(len(argv)+len(env)+2);total=sum(argument_bytes)+envbytes+pointerbytes
        need(launch['argumentBytes']==argument_bytes and launch['environmentBytes']==envbytes and launch['pointerBytes']==pointerbytes and launch['totalBytes']==total and launch['observedArgMax']==1048576 and total<1048576 and launch['perArgumentLimitProved'] is False and launch['largestRecordFeasibilityProved'] is False,'independent finite argv/NUL/environment/64bit pointer arithmetic')
        account={'argumentBytes':argument_bytes,'environmentBytes':envbytes,'pointerBytes':pointerbytes,'totalBytes':total,'argMax':1048576,'strictlyBelowArgMax':True,'perArgumentLimit':None,'allArgumentsBelowKnownLimit':None,'kernelPaddingAndPerArgumentSemanticsNotProved':True,'runtimeFeasibilityProved':False}
        need(observed['argvAccounting']==account,'source accounting not promoted to broad feasibility')
        captured=raw(observed['rawStdout']['path'],observed['rawStdout']);need(raw(observed['rawStderr']['path'])==b'','actual stderr empty')
        # Retain and fsync the independent byte copies before this review's own
        # decode; the original Root raw terminals retain typedResultParsed=false.
        for name,key in [('stdout.log','rawStdout'),('stderr.log','rawStderr'),('launch.json','launch'),('terminal.json','terminal')]:write('evidence/'+arm+'.'+name,raw(observed[key]['path'],observed[key]))
        decoded,escapes=wave_identity_string(raw(evidence/(arm+'.stdout.log')))
        value=parse_json(decoded);expected=expected_identity(arm)
        need(value==expected and decoded==json.dumps(expected,separators=(',',':'),ensure_ascii=False),'complete inner JSON value and exact unnormalized returned string')
        need(decoded.encode('utf-8')==raw(observed['decodedString']['path'],observed['decodedString']) and value==data(observed['decodedValue']['path'],observed['decodedValue']),'independent decode equals retained owner afterimages')
        need(observed['counters']==expected['counters'] and observed['snapshotState']==expected['snapshotState'] and observed['codecCalls']==0 and observed['actualFreshProcess'] is True and observed['typedWaveStringDecoded'] is True,'actual independent counters and empty snapshot')
        write(arm+'/decoded-string.txt',decoded.encode('utf-8'));write(arm+'/decoded-value.json',value)
        item={'arm':arm,'pid':terminal['pid'],'rawExitCode':0,'timeout':False,'ownedGroupGone':True,'component':artifact['component'],'nativeEngine':artifact['nativeEngine'],'artifactReview':proof,'rawStdout':observed['rawStdout'],'rawStderr':observed['rawStderr'],'terminal':observed['terminal'],'launch':observed['launch'],'rawBytes':len(captured),'decodedUtf8Bytes':len(decoded.encode('utf-8')),'independentlyDecodedTypedString':True,'exactCompleteIdentityValue':True,'counters':expected['counters'],'snapshotState':expected['snapshotState'],'guestState':expected['state'],'rootOrdinaryExportExecuted':'identity','rootCodecCalls':0,'rootControlOperations':0,'encounteredOuterEscapes':escapes,'argvAccounting':account,'emittedImportsFromExistingArtifactReview':[],'freshBinaryWitDecoded':False,'elapsedOperationalSecondsOnly':terminal['elapsedSeconds']}
        write(arm+'/review.json',item);actual.append(item)
    launcher=raw(root['externalLaunchSource']['path']).decode();owner_parser=raw(root['typedParserSource']['path']).decode()
    need('env=env,stdout=stdout,stderr=stderr,start_new_session=True' in launcher and 'os.fsync(f.fileno())' in launcher and "'typedResultParsed':False" in launcher,'raw launch/terminal retention source ordering')
    need('await h.sync()' in owner_parser and 'rawDurablyRetained:true' in owner_parser and owner_parser.index('await h.sync()')<owner_parser.index('helper.parseScalarStringOutput'),'retained owner source fsync-before-decode order')
    need(root['emittedImportsFromExistingArtifactReviews']==[] and root['actualOrdinaryExport']=='identity' and root['actualCallsPerFreshComponent']==1,'identity only observation boundary')
    for key in ('stringArgumentsTested','stageValidateOrCodecCallsExecuted','largestRecordTransportProved','separateHostCallInterleavingProved','componentReuseProved','timingExecuted','operationalAdmission','runtimeAcceptanceClaim'):need(root[key] is False,'no broader action/proof transfer')
    write('results.json',{'schemaVersion':1,'state':'INDEPENDENT_ZLIB_COST_STOCK_WASMTIME42_IDENTITY_RESULTS_VERIFIED_V1','verifiedPassed':True,'rootAggregate':rootrow,'rootAuthority':root['rootAuthority'],'transportSourceIndex':sourceix,'sourceIndependentReviewIndex':peerix,'componentArtifactReviewIndex':artifactix,'stockWasmtime':host,'actualIdentityModes':actual,'actualFreshProcesses':3,'actualRootOrdinaryIdentityCalls':3,'actualNoArgumentIdentityTypedStringReturnIndependentlyDecoded':True,'actualIdentityReturnJsonAndCountersExact':True,'codecCalls':0,'controlOperations':0,'allSnapshotsAndGuestStatesEmpty':True,'emittedImportsFromExistingArtifactReviews':[],'newBinaryWitDecodeExecuted':False,'originalUnparsedRawTerminalPreserved':True,'independentRawCopiesRetainedAndFsyncedBeforeReviewDecode':True,'ownerFsyncBeforeDecodeSupportedByAuthenticatedSourceOrdering':True,'durabilityIndependentlyMeasured':False,'originalTransportSourceFilesRehashed':29,'originalSourcePreparationRowsRehashed':52,'componentCommonContextRowsRehashed':len(common),'uniqueLexicalInputTuplesRehashed':len(ROWS),'reviewerReadHashDataOnly':True,'reviewerOwnerParsersHelpersNodeCliHostsComponentsGuestsOrCodecsInvoked':False,'rootIdentityGuestExportsExecuted':True,'stringArgumentsTested':False,'stageValidateOrCodecCallsExecuted':False,'largestRecordTransportProved':False,'separateHostCallInterleavingProved':False,'componentReuseProved':False,'generalWaveParserProof':False,'kernelAndPerArgumentLimitsProved':False,'broadRuntimeFeasibilityProved':False,'runtimeAcceptanceClaim':False,'ordinary350Admission':'CLOSED','operationalAdmission':False,'sourcePromotionAllowed':False,'timingAllowed':False,'actionAuthorityIssuedByReviewer':False,'scope':'Three separately authorized fresh stock Wasmtime identity() calls only: current artifact/source/native/host/authority binding, complete retained typed-string decoding, exact empty state and entry/call counters. No string-argument, codec, largest-record, interleaving, reuse, correctness schedule or performance proof.'})
    write('rehashed-inputs.json',{'schemaVersion':1,'files':list(ROWS.values())})
    print(json.dumps({'review':'passed','arms':3,'uniqueLexicalInputTuplesRehashed':len(ROWS)}))

if __name__=='__main__':review()
