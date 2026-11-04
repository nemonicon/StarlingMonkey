#!/usr/bin/env python3
"""Independent finite READ/HASH/DATA integrity/ownership/source review.

No owner code, Node, parser helper, CLI, Jco, codec, guest or timing action is
imported or executed. Binaries and generated JavaScript are opaque file data.
Raw-return and byte interpretations are separate independent peer readers.
"""
from pathlib import Path
import collections
import hashlib
import json
import os
import stat

HERE=Path(__file__).resolve().parent
Z=HERE.parent
OUT=Path('/private/tmp/starling-node-compat/zlib-cost-jco-correctness-v3')
SOURCE=Z/'cost-jco-correctness-candidate-v3'
SOURCE_SHA='0124b94f28b20cea7d85c8e7a2619a33099ee98ed56d4920dd5d5749da28cb8c'
INDEX_SHA='e8da5ddba338e578fb8bdce83791c563465be440c1fe8a5c39f0ff9c4105aa7e'
RESULT_SHA='ecd0ac44ecafc624471f6b2c64224facb0a087adf0a88adc30b11096cfe900d5'
AUTH_SHA='235d391b7f730899d0b8f5be31247c100d9d997f6796042f15f86ed8af07daf6'
ARMS=['native-on','fflate-on','fflate-off']
NODE={'path':'/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node','sha256':'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0','bytes':108619024}
PARENTS=[('cost-jco-correctness-candidate-v2','d2516c934df3fa8f3ecd58b187cc2bc0f28fab996ab97ada0854e4988d9befeb'),('independent-cost-jco-correctness-v2-source-review-v1','751147af6cda28a9f32b6c8e16ec22db9dc3a2b4592d38a32342f0bb99e28ecd'),('cost-component-glue-amendment-v1','cf3110b3af503fecd2408781a4dcb53b21670b74cd94e3266c4f0b86f795d794'),('cost-component-wit-amendment-v1','e7252156f464f3a73621c002d01b95fa309ebc8208934539687d54d885257caa'),('cost-component-candidate-v1','a2fa62b3ab63a6aca044aec9a83c1ff5a09edaa208eb615226a13845bf1522f9'),('cost-tooling-candidate-v3','ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8'),('cost-guest-oracle-candidate-v2','ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8'),('cost-jco-correctness-candidate-v1','610295513e79ffa3a926c466f2b07a05d465694e8ee7de706f3966052f8f305a')]
ROWS={}

def need(v,message):
    if not v:raise AssertionError(message)

def local(name):
    need(isinstance(name,str) and name and not name.startswith('/') and '\\' not in name and '\0' not in name and all(p not in ('','.','..') and len(p.encode())<=255 for p in name.split('/')),'finite local name');return name

def read(path,expected=None):
    path=Path(path);need(path.is_absolute(),'absolute input path')
    canonical=str(path)
    if canonical.startswith('/tmp/'):canonical='/private/tmp/'+canonical[5:]
    need(str(path.resolve())==canonical,'only declared tmp system alias')
    for at in [path.resolve(),*list(path.resolve().parents)[:-1]]:need(not at.is_symlink(),'ordinary input ancestors')
    before=path.lstat();need(stat.S_ISREG(before.st_mode),'ordinary input leaf')
    h=hashlib.sha256()
    with path.open('rb') as stream:
        while block:=stream.read(4*1024**2):h.update(block)
    after=path.lstat();need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable hash read')
    row={'path':str(path),'sha256':h.hexdigest(),'bytes':before.st_size}
    if expected:need(row['sha256']==expected['sha256'] and row['bytes']==expected['bytes'],'exact hash/size '+str(path))
    old=ROWS.get(str(path));need(old is None or old==row,'consistent repeated descriptor');ROWS[str(path)]=row;return row

def raw(path,expected=None):
    row=read(path,expected);value=Path(path).read_bytes();need(len(value)==row['bytes'] and hashlib.sha256(value).hexdigest()==row['sha256'],'stable second data read');return value

def pairs(values):
    out={}
    for key,value in values:need(key not in out,'unique JSON key');out[key]=value
    return out

def data(path,expected=None):return json.loads(raw(path,expected),object_pairs_hook=pairs)

def members(root):
    out=set()
    for base,dirs,files in os.walk(root,followlinks=False):
        need(all(not (Path(base)/x).is_symlink() for x in dirs),'ordinary owned output directories')
        for name in files:
            p=Path(base)/name;need(p.is_file() and not p.is_symlink(),'ordinary owned output files');out.add(p.relative_to(root).as_posix())
    return out

def indexed(root,digest=None,count=None,membership_extra=None):
    ix=read(root/'index.json')
    if digest:need(ix['sha256']==digest,'pinned index')
    value=data(root/'index.json',ix);need(value['schemaVersion']==1 and isinstance(value['files'],list) and value['files'],'finite populated index')
    if count is not None:need(len(value['files'])==count,'exact indexed count')
    names=set();absolute=[]
    for row in value['files']:
        name=local(row['path']);need(name not in names,'unique indexed member');names.add(name);read(root/name,row);absolute.append({'path':str(root/name),'sha256':row['sha256'],'bytes':row['bytes']})
    if membership_extra is not None:need(members(root)==names|set(membership_extra),'exact full indexed membership')
    return value,ix,absolute

def write(name,value):
    with (HERE/name).open('x') as stream:stream.write(json.dumps(value,indent=2)+'\n')

def review():
    root_path=Z/'cost-jco-correctness-v3-root-results.json';rootrow=read(root_path);need(rootrow['sha256']=='8a9a21419ac391b66e96bc69a18aab40460e87f235a2110c1e765e802356a21d' and rootrow['bytes']==2834,'actual Root result pinned')
    root=data(root_path,rootrow)
    for key in ('actualParentTerminal','externalLaunchSource','rootAuthority','config','index','completion','result'):read(root[key]['path'],root[key])
    need(root['rootSessionId']==86618 and root['actualOutputRoot']==str(OUT) and root['sourceIndexSha256']==SOURCE_SHA,'actual Root run source/output')
    parent=data(root['actualParentTerminal']['path'],root['actualParentTerminal'])
    need(parent['pid']==49994 and parent['rawExitCode']==0 and parent['timeout'] is False and parent['deadlineSeconds']==7500 and parent['timingAllowed'] is False,'actual external parent raw0/no timeout')
    for key in ('stdout','stderr'):read(parent[key]['path'],parent[key])
    need(raw(parent['stderr']['path'])==b'','actual external parent stderr empty')
    need(parent['argv'][:2]==[NODE['path'],str(SOURCE/'run.mjs')] and data(root['config']['path'],root['config'])=={'correctnessSourceIndexSha256':SOURCE_SHA,'rootAction':root['rootAuthority']} and json.loads(parent['argv'][2])==root['config'] and parent['config']==root['config'] and parent['authority']==root['rootAuthority'],'external actual source/config/authority argv')
    auth=data(root['rootAuthority']['path'],root['rootAuthority']);need(read(root['rootAuthority']['path'])['sha256']==AUTH_SHA and auth['state']=='ROOT_REVIEWED_ZLIB_COST_JCO_CORRECTNESS_V3' and auth['action']=='untimed-jco-correctness' and auth['actionAllowed'] is True and auth['correctnessSourceIndexSha256']==SOURCE_SHA,'dedicated current actual correctness authority')
    for key,val in {'outputRoot':str(OUT),'workerTimeoutMs':600000,'retainedRotations':3,'primaryCases':30,'primaryEncoderStreams':45,'primaryCrossdecodeEdges':135,'ffOffEncodings':15,'ffOffNodeEdges':15,'ffOffGuestEdges':45,'nativeInputs':350,'nodeMatrixCodecCallsAllowed':True,'ordinaryGuestCallsAllowed':True,'metadataProjection':False,'operationalAdmission':False,'sourcePromotionAllowed':False,'pilotOrTimingAllowed':False,'stockWasmtimeExecutionAllowed':False}.items():need(auth[key]==val,'finite exact Root correctness scope '+key)
    actual_index,indexrow,indexedrows=indexed(OUT,INDEX_SHA,11440,{'index.json','completion.json'})
    need(sum(x['bytes'] for x in actual_index['files'])==712222394,'all actual indexed byte total')
    resultrow=read(OUT/'results.json');need(resultrow['sha256']==RESULT_SHA and resultrow['bytes']==20237274,'complete actual result pinned')
    result=data(OUT/'results.json',resultrow);completion=data(OUT/'completion.json')
    need(result['state']=='UNTIMED_ZLIB_COST_JCO_CORRECTNESS_COMPLETE_PENDING_INDEPENDENT_REVIEW_V3' and result['correctnessSourceIndexSha256']==SOURCE_SHA and result['rootAction']==root['rootAuthority'],'preserve raw pending-review result state/source')
    need(completion=={'schemaVersion':1,'state':'UNTIMED_JCO_CORRECTNESS_COMPLETE_EXTERNAL_PARENT_ZERO_AND_REVIEW_REQUIRED_V3','results':{'path':'results.json','sha256':resultrow['sha256'],'bytes':resultrow['bytes']},'index':{'path':'index.json','sha256':indexrow['sha256'],'bytes':indexrow['bytes']},'sourceIndexSha256':SOURCE_SHA,'timingAllowed':False,'operationalAdmission':False},'exact actual completion/result/index/source binding')
    lines=raw(parent['stdout']['path']).decode('utf-8','strict').splitlines();need(lines,'retained parent stdout')
    final=json.loads(lines[-1]);need(final=={'index':completion['index'],'completion':{'path':'completion.json','sha256':read(OUT/'completion.json')['sha256'],'bytes':read(OUT/'completion.json')['bytes']}},'actual final external return descriptor')
    for line in lines[:-1]:
        item=json.loads(line);need(item['event']=='untimed-correctness-operational-heartbeat' and item['partialObservationOnly'] is True,'operational heartbeat only, not timing proof')
    source,sourceix,critical=indexed(SOURCE,SOURCE_SHA,26)
    for name,digest in PARENTS:
        _,_,rows=indexed(Z/name,digest);critical.extend(rows)
    critical.append(root['rootAuthority']);need(len(critical)==505 and len({x['path'] for x in critical})==505,'complete exact original source/donor/old HOLD/control tuple')
    peer=auth['sourceIndependentReview'];peerroot=Path(peer['index']['path']).parent
    indexed(peerroot,'abeb157af8334c4b14fba007b238b464ca30a6e8c3ef7ffc010eacb5cd50aa5a',5)
    peer_value=data(peer['result']['path'],peer['result']);need(peer_value['state']=='INDEPENDENT_ZLIB_COST_JCO_CORRECTNESS_SOURCE_REVIEW_PASSED_V3' and peer_value['correctnessSourceIndexSha256']==SOURCE_SHA and peer_value['sourceOnly'] is True and peer_value['ownerActionsInvoked'] is False,'independent exact v3 source review')
    for row in data(peerroot/'verified-files.json')['files']:read(row['path'],row)
    for name in ['cost-jco-correctness-candidate-v3','cost-jco-correctness-candidate-v2']:
        preparation=data(Z/name/'input-freeze.json');need(preparation['runtimeActivationOrActionSeal'] is False,'old preparation contexts remain source DATA')
        for row in preparation['files']:read(row['path'],row)
    component_review=Z/'independent-cost-component-v3-results-review-v1'
    indexed(component_review,'9ab82077a47c3935a7bc1accec1cbcc385ef35c7c3bf1134b7dc9f81ca0d9893',26)
    for row in data(component_review/'rehashed-common-inputs.json')['files']:read(row['path'],row)
    artifacts={}
    for arm in ARMS:
        proof=auth['actualComponentReviews'][arm];indexed(Path(proof['index']['path']).parent,proof['index']['sha256'],3)
        artifact=data(proof['result']['path'],proof['result']);need(artifact['state']=='INDEPENDENT_ZLIB_COST_COMPONENT_ARTIFACT_REVIEW_PASSED_V1' and artifact['verifiedPassed'] is True and artifact['arm']==arm and artifact['emittedImports']==[],'same successful actual component artifact')
        need(artifact['actualBuildAuthority']==auth['componentBuildAuthorities'][arm] and artifact['component']==result['components'][arm] and artifact['oracleSha256']==result['oracle']['sha256'],'actual artifact/build/native/oracle tuple')
        for key in ['component','glue','core','dts','wit','transpileMetadata','packageJson','code','nativeEngine','metadata','actualBuildAuthority','externalParentTerminal','ownedWorkerTerminal','workerIndex','workerCompletion','parentResult','workerResult']:read(artifact[key]['path'],artifact[key])
        for row in data(Path(proof['index']['path']).parent/'rehashed-inputs.json')['files']:read(row['path'],row)
        metadata=data(artifact['metadata']['path'],artifact['metadata']);need(len(metadata['sourceManifest'])==350 and len(metadata['componentizeSourceManifest'])==3 and metadata['hostApi']=='wasi-0.2.10' and metadata['zlibPolicy']['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None},'actual genuine350 metadata remains standard and unprojected')
        artifacts[arm]=artifact
    read(NODE['path'],NODE);read(auth['oracle']['path'],auth['oracle']);need(result['oracle']==auth['oracle'],'same actual reviewed Node oracle')
    expected_names={('retained-'+arm) for arm in ARMS}|{('fresh-'+arm+'-'+str(case).zfill(2)) for arm in ARMS for case in range(30)}|{('edge-'+arm+'-'+str(case).zfill(2)) for arm in ARMS for case in range(45)}
    need(len(result['origins'])==228 and members(OUT/'descriptors')=={x+'.json' for x in expected_names} and members(OUT/'jobs')=={name+'/'+item for name in expected_names for item in members(OUT/'jobs'/name)},'all and only finite expected job directories/descriptors')
    need({x.name for x in (OUT/'jobs').iterdir()}==expected_names,'228 exact job directory names')
    pidset=set();names=set();kinds=collections.Counter();worker_evidence=[]
    observed_primary=[];observed_main=[];observed_off=[]
    for origin in result['origins']:
        resultpath=Path(origin['workerResults']['path']);jobroot=resultpath.parent;name=jobroot.name;names.add(name);job=origin['job'];arm=job['arm'];need(name in expected_names and jobroot==OUT/'jobs'/name and arm in ARMS,'finite exact worker job namespace')
        kinds[job['kind']]+=1
        descriptorrow=read(OUT/'descriptors'/(name+'.json'));descriptor=data(descriptorrow['path'],descriptorrow)
        need(descriptor['state']=='PARENT_AUDITED_ZLIB_COST_JCO_WORKER_V2' and descriptor['parentAuditedActualComponents'] is True and descriptor['correctnessSourceIndexSha256']==SOURCE_SHA and descriptor['componentSourceIndexSha256']==auth['componentSourceIndexSha256'] and descriptor['parentOutputRoot']==str(OUT) and descriptor['outputRoot']==str(jobroot) and descriptor['jobName']==name and descriptor['job']==job and descriptor['criticalFiles']==critical,'inherited wire name binds exact v3 action/source and complete505 tuples')
        need(descriptor['oracle']==auth['oracle'] and descriptor['artifact']=={'parentAuditedActualComponent':True,**{key:artifacts[arm][key] for key in ['component','glue','core','dts','wit','transpileMetadata','packageJson']}},'worker exact current actual artifact/oracle')
        read(descriptor['cases']['path'],descriptor['cases'])
        terminalpath=OUT/'processes'/(name+'.terminal.json');need(origin['ownedTerminal']==str(terminalpath),'exact owned terminal path')
        terminal=data(terminalpath);launch=data(OUT/'processes'/(name+'.launch.json'))
        need(terminal['schemaVersion']==1 and terminal['name']==name and terminal['pid'] not in pidset,'unique owned process identity');pidset.add(terminal['pid'])
        for key,val in {'status':0,'signal':None,'spawnError':None,'timedOut':False,'timeoutMs':600000,'externalSignal':None,'signalCount':0,'outputLimitExceeded':False,'maxOutputBytes':16777216,'signals':[],'errors':[],'closed':True,'ownedGroupGone':True,'terminalExitZeroObserved':True,'runtimeAcceptanceClaim':False}.items():need(terminal[key]==val,'clean raw owned terminal '+key)
        args=[str(Z/'cost-jco-correctness-candidate-v2/worker.mjs'),json.dumps(descriptorrow,separators=(',',':'))]
        need(terminal['executable']==NODE['path'] and terminal['args']==args and launch['executable']==NODE['path'] and launch['args']==args and launch['detachedOwnedSession'] is True and launch['timeoutMs']==600000,'authentic fresh owned worker descriptor argv')
        for key in ['stdout','stderr']:read(terminal[key]['path'],terminal[key])
        need(raw(terminal['stderr']['path'])==b'','owned worker stderr empty')
        worker=data(resultpath,origin['workerResults']);complete=data(jobroot/'completion.json',origin['workerCompletion']);windex,wix,_=indexed(jobroot,None,None,{'index.json','completion.json'})
        need(worker['state']=='UNTIMED_ZLIB_COST_JCO_JOB_COMPLETE_UNREVIEWED_V2' and worker['job']==job and worker['jobName']==name and worker['correctnessSourceIndexSha256']==SOURCE_SHA and worker['componentSourceIndexSha256']==auth['componentSourceIndexSha256'] and worker['component']==artifacts[arm]['component'] and worker['generatedModuleImported'] is True and worker['initializationCompletedByModuleTLA'] is True and worker['externalWasiImports']==[] and worker['resetOrCrossProcessReuseProved'] is False and worker['timing'] is False,'actual preserved donor wire result binds v3 job/source/module')
        need(complete['state']=='JCO_CORRECTNESS_JOB_COMPLETE_EXTERNAL_OWNED_EXIT_ZERO_REQUIRED' and complete['sourceIndexSha256']==SOURCE_SHA and complete['componentSha256']==artifacts[arm]['component']['sha256'] and complete['timing'] is False and complete['index']=={'path':'index.json','sha256':wix['sha256'],'bytes':wix['bytes']} and complete['results']=={'path':'results.json','sha256':origin['workerResults']['sha256'],'bytes':origin['workerResults']['bytes']},'worker complete/index/result/source/component binding')
        need(json.loads(raw(terminal['stdout']['path']))=={'index':complete['index'],'completion':{'path':'completion.json','sha256':origin['workerCompletion']['sha256'],'bytes':origin['workerCompletion']['bytes']}},'actual owned worker final stdout descriptor')
        need(origin['component']==artifacts[arm]['component'] and origin['ownedRawExitCode']==0 and origin['actualFreshOwnedProcess'] is True,'outer actual fresh process provenance')
        value=worker['observed']
        if job['kind'] in ['retained-primary','fresh-primary']:
            need(value['arm']==arm and len(value['records'])==(90 if job['kind']=='retained-primary' else 1),'actual primary worker count')
            observed_primary.extend([{**row,'kind':job['kind']} for row in value['records']])
        elif job['kind']=='main-crossdecode':observed_main.append(value)
        elif job['kind']=='off-guest-crossdecode':observed_off.append(value)
        else:raise AssertionError('unknown actual worker kind')
        worker_evidence.append({'jobName':name,'job':job,'pid':terminal['pid'],'rawOwnedStatus':0,'ownedGroupGone':True,'descriptor':descriptorrow,'terminal':read(terminalpath),'workerIndex':wix,'workerResult':origin['workerResults'],'workerCompletion':origin['workerCompletion'],'component':origin['component'],'allWorkerIndexedFilesRehashed':len(windex['files'])})
    need(names==expected_names and len(pidset)==228 and dict(kinds)=={'retained-primary':3,'fresh-primary':90,'main-crossdecode':90,'off-guest-crossdecode':45},'complete exact fresh owned job coverage')
    need(result['primary']==observed_primary and result['mainEdges'][45:]==observed_main and result['offGuestEdges']==observed_off,'root summaries are exact whole actual child observations')
    expected_primary={(arm,case,rotation,'retained-primary') for arm in ARMS for case in range(30) for rotation in range(3)}|{(arm,case,0,'fresh-primary') for arm in ARMS for case in range(30)}
    actual_primary={(x['arm'],x['caseId'],x['rotation'],x['kind']) for x in result['primary']};need(len(result['primary'])==len(actual_primary)==360 and actual_primary==expected_primary,'360 exact primary tuples no omissions/duplicates')
    need(result['coverage']=={'primaryObservations':360,'mainCrossdecodeEdges':135,'offEncodings':15,'offNodeEdges':15,'offGuestEdges':45,'coverageOnlyNotRuntimeProof':True,'timing':False},'preserve raw declared coverage counter scope')
    for key,val in {'allNewOwnedWorkersCompletedZero':True,'wasmtimeExecuted':False,'pilotOrTimingExecuted':False,'metadataProjection':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False}.items():need(result[key]==val,'actual result bounded execution scope')
    controls=[x['publicCounters']['controlOperations'] for x in result['primary']+result['mainEdges'][45:]+result['offGuestEdges']];need(len(controls)==495 and set(controls)=={0},'control workloads explicitly unexecuted')
    streams=data(OUT/'actual-encoder-streams.json');need(len(streams['primary'])==45 and len(streams['off'])==15 and len(streams['origins'])==93,'actual encoder catalog bound to primary jobs only')
    need(streams['origins']==[{key:origin[key] for key in ['job','workerResults','component']} for origin in result['origins'][:93]],'encoder origins exact original retained/fresh jobs')
    evidence=HERE/'evidence';evidence.mkdir(exist_ok=True)
    for name,path in [('root-results.json',root_path),('parent-terminal.json',Path(root['actualParentTerminal']['path'])),('parent-stdout.log',Path(parent['stdout']['path'])),('parent-stderr.log',Path(parent['stderr']['path'])),('external-launch.py',Path(root['externalLaunchSource']['path'])),('root-authority.json',Path(root['rootAuthority']['path']))]:
        with (evidence/name).open('xb') as stream:stream.write(raw(path))
    write('worker-ownership-review.json',{'schemaVersion':1,'state':'INDEPENDENT_ALL228_ACTUAL_WORKER_ORIGINS_AND_BINDINGS_VERIFIED','ownedWorkers':228,'uniqueWorkerPids':228,'jobKinds':dict(kinds),'workers':worker_evidence,'rootSummariesExactlyMatchChildResults':True,'criticalFilesPerWorker':505,'workerInternalV2NamesArePreservedV3BoundWireData':True,'rootJcoGuestAndNodeCodecExecution':True,'reviewerOwnerActionsInvoked':False,'runtimeAcceptanceClaim':False})
    write('bindings-review.json',{'schemaVersion':1,'state':'INDEPENDENT_JCO_V3_ACTUAL_INTEGRITY_SOURCE_ARTIFACT_NATIVE_BINDINGS_PASSED','rootAggregate':rootrow,'externalParentTerminal':root['actualParentTerminal'],'externalParentExitCode':0,'actualIndex':indexrow,'actualResult':resultrow,'actualCompletion':read(OUT/'completion.json'),'indexedFiles':11440,'actualRegularFiles':11442,'indexedBytes':712222394,'exactFullMembership':True,'correctnessSourceIndex':sourceix,'sourceIndependentReview':peer,'sourceCriticalRowsPerWorker':505,'allActualWorkerDescriptorsAndSourcesMatch':True,'actualComponentReviews':auth['actualComponentReviews'],'nativeInputs':350,'oracle':result['oracle'],'node':NODE,'components':result['components'],'actualEncoderStreams':read(OUT/'actual-encoder-streams.json'),'exactPrimaryTuples':360,'exactOwnedWorkers':228,'actualNodeEdges':60,'actualGuestCrossdecodeWorkers':135,'executedControlWorkloads':False,'controlOperations':0,'actualBatchControlProofPending':True,'untimedCodecBatchN1IsSeparateFromControls':True,'allControlProtocolDefinitionsSourceBound':True,'rootOrdinaryGuestJcoAndNodeCodecActionsExecuted':True,'reviewerReadHashDataOnly':True,'reviewerWorkerNodeParserHelperCliCodecJcoGuestOrTimingExecuted':False,'wasmtimeExecutedByThisAction':False,'stockWasmtimeSmallStringArgumentProofPending':True,'stockWasmtimeLargestRecordProofPending':True,'pilotTimingPrerequisitesSatisfied':False,'metadataProjection':False,'operationalAdmission':False,'sourcePromotionAllowed':False,'runtimeAcceptanceClaim':False,'timingAllowed':False,'uniqueLexicalInputTuplesRehashed':len(ROWS)})
    write('bindings-rehashed-inputs.json',{'schemaVersion':1,'files':list(ROWS.values())})
    print(json.dumps({'bindings':'passed','files':11440,'workers':228,'uniqueLexicalInputs':len(ROWS)}))

if __name__=='__main__':review()
