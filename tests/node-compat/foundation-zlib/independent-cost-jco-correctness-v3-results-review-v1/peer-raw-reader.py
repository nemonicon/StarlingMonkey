#!/usr/bin/env python3
"""Independent finite raw-return/counter/ownership DATA audit.

Reads standard JSON and byte/base64 records only. Never imports or executes any
owner module, Node, generated glue, Jco, codec, guest, CLI or timing code.
"""
from pathlib import Path
import base64
import collections
import hashlib
import json
import os

HERE=Path(__file__).resolve().parent
ROOT=Path('/private/tmp/starling-node-compat/zlib-cost-jco-correctness-v3')
Z=HERE.parent
NAMES=['identity','setup','observe','batch','checkpoint','stage','validate']
IDLE={'activeCaseId':None,'inputSource':None,'stagedValidation':None,'prepared':False,'retainedUntimedOutput':False}
ORACLE_SHA='bf1312f33bc4df030b16a0f52a8018b2cf50c7dcf4fbad31699fbd9217c9fcf5'
ROWS={};STATS=collections.Counter();FNV={};BYTE_ID={};OUTPUTS={}

def need(v,label):
    if not v:raise AssertionError(label)

def pairs(items):
    d={}
    for k,v in items:need(k not in d,'duplicate JSON field');d[k]=v
    return d

def parse(b):return json.loads(b,object_pairs_hook=pairs)
def eq(a,b,label):need(json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':')),label)
def keys(v,names,label):need(isinstance(v,dict) and set(v)==set(names),label+' exact keys')
def read(path,expected=None):
    p=Path(path);need(p.is_file() and not p.is_symlink(),'regular data file')
    b=p.read_bytes();d={'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
    if expected:need(d['sha256']==expected['sha256'] and d['bytes']==expected['bytes'],'data tuple '+str(p))
    old=ROWS.get(str(p));need(old is None or old==d,'stable repeated descriptor');ROWS[str(p)]=d;return b
def data(path,expected=None):return parse(read(path,expected))
def fnv(b):
    sha=hashlib.sha256(b).hexdigest();key=(sha,len(b))
    if key not in FNV:
        value=2166136261
        for x in b:value=((value^x)*16777619)&0xffffffff
        FNV[key]=value
    return FNV[key]
def whole(s,n):
    need(isinstance(s,str),'base64 string');b=base64.b64decode(s,validate=True)
    need(len(b)==n and base64.b64encode(b).decode()==s,'canonical complete base64');return b
def window(b):return {'byteOffset':8,'byteLength':len(b),'backingBytes':len(b)+16,'prefix':[165]*8,'suffix':[90]*8,'construction':'new ordinary ArrayBuffer; fixed/attached/unshared by construction'}
def hashbytes(b):return hashlib.sha256(b).hexdigest()
def output(v):
    keys(v,['bytes','fnv1aU32','base64','byteOffset','backingBytes','isBuffer'],'output')
    b=whole(v['base64'],v['bytes']);need(v['fnv1aU32']==fnv(b) and v['isBuffer'] is True,'complete output FNV/Buffer')
    need(type(v['byteOffset']) is int and v['byteOffset']>=0 and type(v['backingBytes']) is int and v['backingBytes']>=v['byteOffset']+len(b),'output public window bounds');return b

class State:
    def __init__(self,arm,cases,fixtures,nodeinputs):
        self.arm=arm;self.provider='native' if arm=='native-on' else 'fflate';self.cases=cases;self.fixtures=fixtures;self.node=nodeinputs
        self.count={'publicFunctionEntries':0,'perExportEntries':{n:0 for n in NAMES},'codecCalls':0,'controlOperations':0}
        self.active=None;self.prior=None
    def state(self):
        if self.active is None:return dict(IDLE)
        return {'activeCaseId':self.active['row']['index'],'inputSource':self.active['source'],'stagedValidation':self.active['stage'],'prepared':True,'retainedUntimedOutput':self.prior is not None}
    def step(self,name,codec=0):
        self.count['publicFunctionEntries']+=1;self.count['perExportEntries'][name]+=1;self.count['codecCalls']+=codec
        STATS['named_entries']+=1;STATS['codec_calls']+=codec;STATS['named_'+name]+=1
    def counts(self,v):
        keys(v,['publicFunctionEntries','perExportEntries','codecCalls','controlOperations'],'counter shape');keys(v['perExportEntries'],NAMES,'entry counters')
        need(all(type(x) is int and 0<=x<=9007199254740991 for x in [v['publicFunctionEntries'],v['codecCalls'],v['controlOperations'],*v['perExportEntries'].values()]),'ordinary exact integer counters')
        eq(v,self.count,'all full cumulative counters');STATS['counter_objects_checked']+=1
    def initial_input(self,caseid):
        row=self.cases[caseid]
        if row['direction']=='encode':return self.fixtures[row['fixture']],'raw-fixture',None
        rec=self.node[caseid];return whole(rec['encodedBase64'],rec['encodedBytes']),'node-oracle-input',rec['encodedSha256']
    def identity(self,v):
        self.step('identity')
        expected={'schemaVersion':1,'kind':'codec-cost-identity-v1','version':'bounded-zlib-cost-guest-v1','provider':self.provider,'providerSourceVersion':'registered-node-zlib-m0.13' if self.arm=='native-on' else 'fflate-browser-0.8.3','oracleSha256':ORACLE_SHA,'primaryCases':30,'controlCaseRanges':{'consumeInput':[30,59],'copyInputAndConsume':[60,89],'harnessNoCodec':[90,119]},'exports':NAMES,'snapshotState':{'prepared':False,'staged':False,'retainedOutput':False,'codecCalls':0,'resources':0},'counterMeaning':'named-function entries including internal validate calls; outer host calls are parent raw records','counters':self.count,'state':IDLE,'codecPrewarmedAtSnapshot':False}
        eq(v,expected,'entire identity value');self.counts(v['counters']);STATS['identity_empty_snapshots']+=1
    def setup(self,v,caseid):
        self.step('setup');row=self.cases[caseid];b,source,parent=self.initial_input(caseid)
        self.active={'row':row,'bytes':b,'source':source,'stage':None};self.prior=None
        expected={'schemaVersion':1,'kind':'codec-cost-setup-v1','caseId':caseid,'caseName':row['id'],'inputSource':source,'input':window(b),'inputFNV1aU32':fnv(b),'parentDeclaredInputSha256':parent,'oracleSha256':ORACLE_SHA,'stagedValidationCleared':True,'priorOutputCleared':True,'counters':self.count,'state':self.state()}
        eq(v,expected,'entire setup/input/state');self.counts(v['counters']);STATS['setup_inputs_checked']+=1
    def stage(self,v,rec):
        need(self.active is not None,'setup before stage');self.step('stage');row=self.active['row'];caseid=row['index']
        need(row['direction']=='decode' and rec['caseId']==caseid and rec['fixture']==row['fixture'] and rec['format']==row['format'],'stage case association')
        need(rec['schemaVersion']==1 and rec['kind']=='codec-cost-stage-v1' and rec['streamId']==rec['provider']+'.'+rec['fixture']+'.'+rec['format'],'stage protocol identity')
        b=whole(rec['encodedBase64'],rec['encodedBytes']);need(0<len(b)<=1048576 and fnv(b)==rec['encodedFNV1aU32'] and hashbytes(b)==rec['encodedSha256'],'stage entire input hash/FNV')
        stage={'caseId':caseid,'streamId':rec['streamId'],'provider':rec['provider'],'fixture':rec['fixture'],'format':rec['format'],'parentDeclaredSha256':rec['encodedSha256']}
        self.active={'row':row,'bytes':b,'source':'staged-validation','stage':stage};self.prior=None
        expected={'schemaVersion':1,'kind':'codec-cost-stage-ack-v1','caseId':caseid,'streamId':rec['streamId'],'provider':rec['provider'],'fixture':rec['fixture'],'format':rec['format'],'decodedBytes':len(b),'decodedFNV1aU32':fnv(b),'parentDeclaredSha256':rec['encodedSha256'],'sha256RecomputedInGuest':False,'codecInvoked':False,'input':window(b),'counters':self.count,'state':self.state()}
        eq(v,expected,'entire stage ack/input/state');self.counts(v['counters']);STATS['stage_inputs_checked']+=1
    def observe(self,v,caseid):
        need(self.active is not None and self.active['row']['index']==caseid,'active observation');self.step('observe',1);row=self.active['row'];b=self.active['bytes']
        keys(v,['schemaVersion','kind','caseId','caseName','provider','operation','format','direction','logicalUncompressedBytes','inputSource','stage','input','output','ownership','counters'],'observation')
        static={'schemaVersion':1,'kind':'codec-cost-observation-v1','caseId':caseid,'caseName':row['id'],'provider':self.provider,'operation':row['operation'],'format':row['format'],'direction':row['direction'],'logicalUncompressedBytes':row['logicalUncompressedBytesPerOperation'],'inputSource':self.active['source'],'stage':self.active['stage'],'input':dict(window(b),fnv1aU32=fnv(b),fullInputUnchanged=True)}
        eq({k:v[k] for k in static},static,'all observation case/input/stage fields');out=output(v['output'])
        if row['direction']=='decode':need(out==self.fixtures[row['fixture']],'full decoded fixture bytes')
        own=v['ownership'];keys(own,['nonemptyOutputInputIndependent','emptyBackingRelationRecorded','previousComparable','previousFullBytesUnchanged','successiveIndependentBacking','mutationProbe'],'ownership')
        keys(own['mutationProbe'],['performed','reason','currentFullBytesUnchanged','inputFullBytesUnchanged','previousRestored'],'probe')
        need(own['nonemptyOutputInputIndependent'] is (True if out else None),'nonempty-only input/output backing statement')
        if out:need(own['emptyBackingRelationRecorded'] is None,'no empty backing statement for nonempty output');STATS['nonempty_observations']+=1
        else:
            keys(own['emptyBackingRelationRecorded'],['sharesInputBacking','isolationClaim'],'empty backing');need(type(own['emptyBackingRelationRecorded']['sharesInputBacking']) is bool and own['emptyBackingRelationRecorded']['isolationClaim'] is False,'zero bytes has no isolation claim');STATS['empty_observations_no_isolation_claim']+=1
        if self.prior is None:
            eq({k:own[k] for k in ['previousComparable','previousFullBytesUnchanged','successiveIndependentBacking','mutationProbe']},{'previousComparable':False,'previousFullBytesUnchanged':None,'successiveIndependentBacking':None,'mutationProbe':{'performed':False,'reason':'no previous comparable output','currentFullBytesUnchanged':None,'inputFullBytesUnchanged':None,'previousRestored':None}},'first observation no prior claim');STATS['first_observations']+=1
        else:
            need(out==self.prior and own['previousComparable'] is True and own['previousFullBytesUnchanged'] is True,'whole adjacent prior/current bytes stable');STATS['full_prior_stability_pairs']+=1
            if out:
                need(own['successiveIndependentBacking'] is True,'nonempty successive backing independence')
                eq(own['mutationProbe'],{'performed':True,'reason':None,'currentFullBytesUnchanged':True,'inputFullBytesUnchanged':True,'previousRestored':True},'reported full mutation/restoration isolation probe');STATS['nonempty_mutation_probe_reports_checked']+=1
            else:
                need(own['successiveIndependentBacking'] is None,'empty successive backing no claim')
                eq(own['mutationProbe'],{'performed':False,'reason':'empty output has no addressable mutation','currentFullBytesUnchanged':None,'inputFullBytesUnchanged':None,'previousRestored':None},'empty output no mutation probe');STATS['empty_pairs_no_mutation_claim']+=1
        self.counts(v['counters']);self.prior=out;STATS['full_observation_outputs_checked']+=1;return out
    def batch(self,v,caseid,expected_output):
        need(self.active is not None and self.active['row']['index']==caseid,'active batch');self.step('batch',1);row=self.active['row'];b=self.active['bytes'];f=fnv(expected_output);aggregate=2166136261
        for n in (f,len(expected_output),0):aggregate=((aggregate^(n&0xffffffff))*16777619)&0xffffffff
        self.prior=None
        expected={'schemaVersion':1,'kind':'codec-cost-batch-v1','caseId':caseid,'caseName':row['id'],'provider':self.provider,'operations':1,'inputBytes':len(b),'logicalUncompressedBytesPerOperation':row['logicalUncompressedBytesPerOperation'],'totalLogicalUncompressedBytes':row['logicalUncompressedBytesPerOperation'],'totalOutputBytes':len(expected_output),'lastOutputBytes':len(expected_output),'lastOutputFNV1aU32':f,'aggregateFNV1aU32':aggregate,'outputArraysRetained':False,'counters':self.count,'state':self.state()}
        eq(v,expected,'whole untimed N1 batch compact result');self.counts(v['counters']);STATS['untimed_batch_n1']+=1
    def checkpoint(self,v):
        self.step('checkpoint');before=self.state();inp=None
        if self.active is not None:inp=dict(window(self.active['bytes']),fnv1aU32=fnv(self.active['bytes']),matchesSetupFNV=True,sentinelsUnchanged=True)
        self.active=None;self.prior=None
        expected={'schemaVersion':1,'kind':'codec-cost-checkpoint-v1','before':before,'input':inp,'preparedAndStageAndPriorOutputCleared':True,'counters':self.count,'state':IDLE,'gcOrResetInvoked':False}
        eq(v,expected,'whole public checkpoint cleanup/no reset');self.counts(v['counters']);STATS['idle_checkpoints']+=1
    def validate(self,v,req):
        self.step('validate');caseid=req['caseId'];keys(v,['schemaVersion','kind','requestKind','caseId','setup','stage','observations','withinOneOuterExport','separateHostCallInterleavingProved','counters','state'],'validation wrapper')
        need(v['schemaVersion']==1 and v['kind']=='codec-cost-validation-v1' and v['requestKind']==req['kind'] and v['caseId']==caseid and v['withinOneOuterExport'] is True and v['separateHostCallInterleavingProved'] is False,'within-one-export wrapper bound')
        self.setup(v['setup'],caseid)
        if req['kind']=='crossdecode':self.stage(v['stage'],req['stageRecord'])
        else:need(v['stage'] is None,'primary wrapper no staged input')
        need(isinstance(v['observations'],list) and len(v['observations'])==2,'two complete nested observations')
        a=self.observe(v['observations'][0],caseid);b=self.observe(v['observations'][1],caseid)
        self.counts(v['counters']);eq(v['state'],self.state(),'entire within-export final state');STATS['within_export_validate_pairs']+=1;return a,b

def main():
    result=data(ROOT/'results.json',{'sha256':'ecd0ac44ecafc624471f6b2c64224facb0a087adf0a88adc30b11096cfe900d5','bytes':20237274})
    cases=data(Z/'cost-jco-correctness-candidate-v2/cases.json',{'sha256':'8cd13aba27fb1dbb5ab731204c04ebb474a59a69816b7de46ba6a24e9255dcbf','bytes':9579})
    oracle=data(result['oracle']['path'],result['oracle']);fixtures={x['id']:whole(x['base64'],x['bytes']) for x in oracle['rawFixtures']};node={x['caseId']:x for x in oracle['encodedStreams']}
    for x in oracle['rawFixtures']:need(hashbytes(fixtures[x['id']])==x['sha256'] and fnv(fixtures[x['id']])==x['fnv1aU32'],'oracle fixture retained bytes')
    jobcounts=collections.Counter();rawcounts=collections.Counter();pids=set();collected_primary=[];collected_main=[];collected_off=[];jobrows=[]
    for origin in result['origins']:
        job=origin['job'];jobcounts[job['kind']]+=1;root=Path(origin['workerResults']['path']).parent;w=data(origin['workerResults']['path'],origin['workerResults']);complete=data(origin['workerCompletion']['path'],origin['workerCompletion']);ix=data(root/'index.json')
        need(w['job']==job and w['jobName']==root.name and w['generatedModuleImported'] is True and w['initializationCompletedByModuleTLA'] is True and w['externalWasiImports']==[] and w['timing'] is False and w['resetOrCrossProcessReuseProved'] is False,'raw worker result identity/no reuse')
        need(complete['state']=='JCO_CORRECTNESS_JOB_COMPLETE_EXTERNAL_OWNED_EXIT_ZERO_REQUIRED' and complete['sourceIndexSha256']==result['correctnessSourceIndexSha256'] and complete['componentSha256']==origin['component']['sha256'],'complete actual worker binding')
        read(root/'index.json',complete['index']);read(root/'results.json',complete['results'])
        inventory={x['path']:x for x in ix['files']};need(len(inventory)==len(ix['files']),'unique worker index');need(set(inventory)|{'index.json','completion.json'}=={p.name for p in root.iterdir() if p.is_file()},'exact worker file membership')
        need(not any('counterexample' in name or 'failure' in name or name.endswith('-throw.json') for name in inventory),'no failed/partial worker accepted')
        terminal=data(origin['ownedTerminal']);pid=terminal['pid'];need(pid not in pids,'distinct worker PID');pids.add(pid)
        for k in ['signal','spawnError','externalSignal']:need(terminal[k] is None,'clean owned terminal optional')
        need(terminal['status']==0 and terminal['timedOut'] is False and terminal['timeoutMs']==600000 and terminal['signalCount']==0 and terminal['outputLimitExceeded'] is False and terminal['signals']==[] and terminal['errors']==[] and terminal['closed'] is True and terminal['ownedGroupGone'] is True and terminal['terminalExitZeroObserved'] is True,'raw owned clean zero/cleanup')
        descriptor=parse(terminal['args'][1]);desc=data(descriptor['path'],descriptor)
        need(desc['job']==job and desc['jobName']==root.name and desc['outputRoot']==str(root) and desc['parentOutputRoot']==str(ROOT) and desc['correctnessSourceIndexSha256']==result['correctnessSourceIndexSha256'] and desc['artifact']['component']==origin['component'],'actual worker argument/data descriptor binding')
        for key in ['stdout','stderr']:read(terminal[key]['path'],terminal[key])
        need(terminal['stderr']['bytes']==0,'empty owned worker stderr');stdout=data(terminal['stdout']['path'],terminal['stdout']);eq(stdout,{'index':complete['index'],'completion':{'path':'completion.json','sha256':origin['workerCompletion']['sha256'],'bytes':origin['workerCompletion']['bytes']}},'actual owned worker output exact completion')
        state=State(job['arm'],cases,fixtures,node);rawnames=[]
        def call(prefix,name,args):
            before=data(root/(prefix+'-before.json'),inventory[prefix+'-before.json']);eq(before,{'schemaVersion':1,'exportName':name,'args':args,'partial':True},'exact retained external call args')
            transport=data(root/(prefix+'-raw.json'),inventory[prefix+'-raw.json']);keys(transport,['schemaVersion','exportName','returned','partial'],'raw transport')
            need(transport['schemaVersion']==1 and transport['exportName']==name and transport['partial'] is True,'preserved raw transport status')
            typed=transport['returned'];keys(typed,['type','value','codeUnits','fullPrimitiveCaptured'],'full scalar primitive');s=typed['value'];need(typed['type']=='string' and isinstance(s,str) and typed['fullPrimitiveCaptured'] is True and typed['codeUnits']==len(s.encode('utf-16-le'))//2<=2097152,'full untruncated string return/UTF16 units')
            v=parse(s);need(json.dumps(v,separators=(',',':'),ensure_ascii=False)==s,'entire complete compact JSON return');rawnames.append(prefix+'-raw.json');rawcounts[name]+=1;STATS['raw_strings']+=1;STATS['raw_utf16_code_units']+=typed['codeUnits'];STATS['raw_json_bytes']+=len(s.encode('utf-8'));STATS['maximum_raw_code_units']=max(STATS['maximum_raw_code_units'],typed['codeUnits'])
            return v
        state.identity(call('call-identity','identity',[]))
        sequences=[(rot,cid,'call-rotation'+str(rot)+'-case'+str(cid).zfill(2)) for rot in range(3 if job['kind']=='retained-primary' else 1) for cid in (job['caseIds'] if job['kind']=='retained-primary' else [job['caseId']])] if job['kind'] in ['retained-primary','fresh-primary'] else [(None,job['stream']['caseId'],'call')]
        records=[]
        for rotation,caseid,prefix in sequences:
            state.setup(call(prefix+'-setup','setup',[caseid]),caseid)
            if 'stream' in job:state.stage(call(prefix+'-stage','stage',[json.dumps(job['stream'],separators=(',',':'))]),job['stream'])
            a=state.observe(call(prefix+'-observe1','observe',[caseid]),caseid);b=state.observe(call(prefix+'-observe2','observe',[caseid]),caseid)
            state.batch(call(prefix+'-untimed-batchN1','batch',[caseid,1]),caseid,a);state.checkpoint(call(prefix+'-checkpoint1','checkpoint',[]))
            req={'schemaVersion':1,'kind':'crossdecode' if 'stream' in job else 'primary','caseId':caseid}
            if 'stream' in job:req['stageRecord']=job['stream']
            pair=state.validate(call(prefix+'-validate','validate',[json.dumps(req,separators=(',',':'))]),req)
            need(pair==(a,b),'entire separate-host-call/within-export returned bytes agree');STATS['separate_vs_validate_full_pairs']+=1
            state.checkpoint(call(prefix+'-checkpoint2','checkpoint',[]));need(state.state()==IDLE,'every sequence ends publicly idle')
            rec=data(root/(prefix+'-complete.json'),inventory[prefix+'-complete.json']);eq(rec['publicCounters'],state.count,'record cumulative counters');eq(rec['checkpointState'],IDLE,'record idle checkpoint')
            if 'stream' not in job:
                need(rec['caseId']==caseid and rec['rotation']==rotation and rec['arm']==job['arm'] and rec['untimedBatchN1'] is True and rec['withinExportPairCompared'] is True and rec['priorOutputStabilityReportedAndChecked'] is True,'primary coverage association')
                key=(job['arm'],caseid);digest=(len(a),hashbytes(a));need(key not in OUTPUTS or OUTPUTS[key]==digest,'all retained/fresh complete bytes deterministic within provider');OUTPUTS[key]=digest;collected_primary.append(dict(rec,kind=job['kind']))
            else:
                need(rec['decoder']==job['arm'] and rec['streamId']==job['stream']['streamId'] and rec['provider']==job['stream']['provider'] and rec['caseId']==caseid and rec['fullRawFixtureEqual'] is True and rec['adjacentFullPairChecked'] is True and rec['priorOutputStabilityReportedAndChecked'] is True,'guest edge coverage association')
                (collected_main if job['kind']=='main-crossdecode' else collected_off).append(rec)
            records.append(rec)
        indexed_raw=[x['path'] for x in ix['files'] if x['path'].endswith('-raw.json')];eq(indexed_raw,rawnames,'complete ordered raw-call inventory; no unreviewed call')
        if 'stream' not in job:eq(w['observed']['records'],records,'all worker primary summaries bound to full raw data')
        else:eq(w['observed'],records[0],'guest worker summary bound to full raw data')
        jobrows.append({'jobName':root.name,'kind':job['kind'],'arm':job['arm'],'pid':pid,'rawReturns':len(rawnames),'finalCounters':state.count,'finalState':state.state(),'ownedRawZeroClean':True})
    eq(jobcounts,{'retained-primary':3,'fresh-primary':90,'main-crossdecode':90,'off-guest-crossdecode':45},'all228 owned jobs')
    eq(result['primary'],collected_primary,'entire360 aggregate primary records')
    eq([x for x in result['mainEdges'] if x['decoder']!='node-22.14.0'],collected_main,'all90 main guest edges bound to workers')
    eq(result['offGuestEdges'],collected_off,'all45 off guest edges bound to workers')
    need(STATS['raw_strings']==3828 and STATS['named_entries']==5448 and STATS['codec_calls']==2475 and len(collected_primary)==360 and len(collected_main)==90 and len(collected_off)==45 and len(OUTPUTS)==90,'exact finite totals')
    note={'schemaVersion':1,'state':'INDEPENDENT_JCO_V3_RAW_COUNTER_OWNERSHIP_DATA_REVIEW_PASSED_V1','verifiedPassed':True,'reviewer':'/root/cost_component_results_review/full_correctness_raw_counter_audit','resultSourceSha256':hashbytes(read(ROOT/'results.json')),'workerJobs':228,'jobKinds':dict(jobcounts),'distinctWorkerPids':len(pids),'allOwnedWorkersRawZeroNoTimeoutCleanClosedGroupGone':True,'rawTypedStringReturns':3828,'rawReturnsByExport':dict(rawcounts),'namedEntriesIncludingNestedValidateCalls':5448,'codecCallsAcrossFullBoundedSchedule':2475,'controlOperations':0,'allRawStringsCompleteAndUtf16LengthsExact':True,'allCountersIndependentlyRecomputedFromCallSequence':True,'allSetupStageInputsFullHashFnvAndSentinelWindowsVerified':True,'allObservationOutputsCanonicallyDecodedAndFnvChecked':True,'fullDecodedFixtureBytesChecked':True,'allSeparateAndWithinExportPairsWholeBytesEqual':True,'allRetainedAndFreshCaseOutputsWholeBytesDeterministicWithinProvider':True,'allSequencesEndInPublicIdleCheckpoint':True,'totals':dict(STATS),'allAggregatePrimaryAndGuestEdgeRecordsReconciled':True,'primaryRecords':360,'mainGuestEdges':90,'offGuestEdges':45,'rawTransportPartialFlagPreserved':True,'partialFlagScope':'Raw per-call records intentionally retain partial=true before collector validation; complete worker/index/owned raw-zero evidence and this independent whole-data audit are required for acceptance. No partial worker accepted.','ownershipScope':'Complete returned bytes, input/sentinel metadata, prior/current pair equality and instrumented mutation/restoration report fields checked for every observation. Guest heap aliasing and old retained heap contents are not independently observable from the host after exit; those probe reports are interpreted only in the authenticated pinned guest source context. Empty outputs make no isolation/mutation claim.','hostIndependentlyInspectedGuestHeapAliasing':False,'intermediateGuestValuesIndependentlyCapturedAsPrimitiveStrings':True,'reviewerOwnerNodeParserHelperCliJcoCodecGuestOrTimingExecuted':False,'performanceClaim':False,'wasmtimeLargestTransportProved':False,'runtimeAcceptanceClaim':False,'operationalAdmission':False,'sourcePromotionAllowed':False,'timingAllowed':False,'uniqueDataFilesRehashed':len(ROWS),'jobs':jobrows,'files':list(ROWS.values())}
    with (HERE/'peer-raw-review.json').open('x') as stream:stream.write(json.dumps(note,indent=2)+'\n')
    print(json.dumps({k:note[k] for k in ['state','rawTypedStringReturns','namedEntriesIncludingNestedValidateCalls','codecCallsAcrossFullBoundedSchedule','uniqueDataFilesRehashed','totals']}))

if __name__=='__main__':main()
