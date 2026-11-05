"""Independent timing compact-return DATA replay models. No filesystem/actions."""
import copy,json,math
NAMES=['identity','setup','observe','batch','checkpoint','stage','validate']
IDLE=dict(activeCaseId=None,inputSource=None,stagedValidation=None,prepared=False,retainedUntimedOutput=False)
def need(v,n):assert v,n
def keys(v,w,n):need(type(v)is dict and set(v)==set(w),n+' exact fields')
def agg(fnv,size,n):
 h=2166136261
 for i in range(n):
  for word in(fnv,size,i):h=((h^(word&0xffffffff))*16777619)&0xffffffff
 return h
def window(n):return dict(byteOffset=8,byteLength=n,backingBytes=n+16,prefix=[165]*8,suffix=[90]*8,construction='new ordinary ArrayBuffer; fixed/attached/unshared by construction')
def decode(s):
 need(type(s)is str and len(s.encode('utf-16-le'))//2<=2097152,'whole bounded returned string')
 def pairs(rows):
  d={}
  for k,v in rows:need(k not in d,'no duplicate returned key');d[k]=v
  return d
 v=json.loads(s,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in()).throw(AssertionError('nonfinite JSON')))
 need(json.dumps(v,separators=(',',':'),ensure_ascii=False)==s,'exact source JSON wire serialization')
 return v
class Collector:
 def __init__(self,c):self.c=c;self.active=False;self.counts=dict(publicFunctionEntries=0,perExportEntries={n:0 for n in NAMES},codecCalls=0,controlOperations=0)
 def state(self):return dict(activeCaseId=self.c['caseId'],inputSource=self.c['inputSource'],stagedValidation=None,prepared=True,retainedUntimedOutput=False)if self.active else dict(IDLE)
 def commit(self,v,name,codec=0,controls=0):
  want=copy.deepcopy(self.counts);want['publicFunctionEntries']+=1;want['perExportEntries'][name]+=1;want['codecCalls']+=codec;want['controlOperations']+=controls
  keys(v['counters'],want,'counter');keys(v['counters']['perExportEntries'],NAMES,'named entries')
  need(all(type(n)is int and 0<=n<=9007199254740991 for n in [v['counters']['publicFunctionEntries'],v['counters']['codecCalls'],v['counters']['controlOperations'],*v['counters']['perExportEntries'].values()]),'exact whole integer counters')
  need(v['counters']==want and v['state']==self.state(),'whole counters/state');self.counts=want
 def identity(self,v):
  keys(v,['schemaVersion','kind','version','provider','providerSourceVersion','oracleSha256','primaryCases','controlCaseRanges','exports','snapshotState','counterMeaning','counters','state','codecPrewarmedAtSnapshot'],'identity')
  need(v['schemaVersion']==1 and v['kind']=='codec-cost-identity-v1'and v['version']=='bounded-zlib-cost-guest-v1','identity type/version')
  need(v['provider']==('native'if self.c['arm']=='native-on'else'fflate')and v['providerSourceVersion']==('registered-node-zlib-m0.13'if self.c['arm']=='native-on'else'fflate-browser-0.8.3')and v['oracleSha256']==self.c['oracleSha256'],'provider/oracle identity')
  need(v['primaryCases']==30 and v['exports']==NAMES and v['counterMeaning']=='named-function entries including internal validate calls; outer host calls are parent raw records','seven actual function identities')
  need(v['controlCaseRanges']==dict(consumeInput=[30,59],copyInputAndConsume=[60,89],harnessNoCodec=[90,119])and v['snapshotState']==dict(prepared=False,staged=False,retainedOutput=False,codecCalls=0,resources=0)and v['codecPrewarmedAtSnapshot']is False,'empty snapshot/control ranges')
  self.commit(v,'identity')
 def setup(self,v):
  c=self.c;keys(v,['schemaVersion','kind','caseId','caseName','inputSource','input','inputFNV1aU32','parentDeclaredInputSha256','oracleSha256','stagedValidationCleared','priorOutputCleared','counters','state'],'setup')
  need(v['schemaVersion']==1 and v['kind']=='codec-cost-setup-v1'and v['caseId']==c['caseId']and v['caseName']==c['caseName'],'setup exact case')
  need(v['inputSource']==c['inputSource']and v['inputFNV1aU32']==c['inputFNV']and v['parentDeclaredInputSha256']==c['parentDeclaredInputSha256']and v['oracleSha256']==c['oracleSha256']and v['input']==window(c['inputBytes']),'whole actual setup input signature/window')
  need(v['stagedValidationCleared']is v['priorOutputCleared']is True,'setup clear');self.active=True;self.commit(v,'setup')
 def batch(self,v,n):
  c=self.c;keys(v,['schemaVersion','kind','caseId','caseName','provider','operations','inputBytes','logicalUncompressedBytesPerOperation','totalLogicalUncompressedBytes','totalOutputBytes','lastOutputBytes','lastOutputFNV1aU32','aggregateFNV1aU32','outputArraysRetained','counters','state'],'codec batch')
  need(self.active and v['schemaVersion']==1 and v['kind']=='codec-cost-batch-v1'and v['caseId']==c['caseId']and v['caseName']==c['caseName']and v['provider']==('native'if c['arm']=='native-on'else'fflate')and v['operations']==n,'actual codec batch identity')
  need(v['inputBytes']==c['inputBytes']and v['logicalUncompressedBytesPerOperation']==c['logicalBytes']and v['totalLogicalUncompressedBytes']==c['logicalBytes']*n,'whole uncompressed input denominator')
  need(v['totalOutputBytes']==c['outputBytes']*n and v['lastOutputBytes']==c['outputBytes']and v['lastOutputFNV1aU32']==c['outputFNV']and v['aggregateFNV1aU32']==agg(c['outputFNV'],c['outputBytes'],n)and v['outputArraysRetained']is False,'whole compact consumed-output FNV signature')
  self.commit(v,'batch',codec=n)
 def control(self,v,id):
  c=self.c;keys(v,['schemaVersion','kind','caseId','primaryCaseId','control','operations','result','logicalUncompressedBytes','counters','state'],'control')
  name='consumeInput'if id<60 else'copyInputAndConsume'if id<90 else'harnessNoCodec'
  need(self.active and id%30==c['caseId']and v['schemaVersion']==1 and v['kind']=='codec-cost-control-v1'and v['caseId']==id and v['primaryCaseId']==c['caseId']and v['control']==name and v['operations']==1 and v['logicalUncompressedBytes']==c['logicalBytes'],'exact active N1 control')
  want=dict(bytesConsumed=0,declaredInputBytes=c['inputBytes'],tag=2166136261,copies=0,codecCalls=0)if name=='harnessNoCodec'else dict(bytesConsumed=c['inputBytes'],fnv=c['inputFNV'],copies=1 if name=='copyInputAndConsume'else 0,codecCalls=0)
  need(v['result']==want,'exact no-codec control value');self.commit(v,'batch',controls=1)
 def checkpoint(self,v):
  c=self.c;keys(v,['schemaVersion','kind','before','input','preparedAndStageAndPriorOutputCleared','counters','state','gcOrResetInvoked'],'checkpoint')
  need(v['schemaVersion']==1 and v['kind']=='codec-cost-checkpoint-v1'and v['preparedAndStageAndPriorOutputCleared']is True and v['gcOrResetInvoked']is False and v['before']==self.state(),'checkpoint state/no reset')
  need(v['input']==dict(window(c['inputBytes']),fnv1aU32=c['inputFNV'],matchesSetupFNV=True,sentinelsUnchanged=True),'complete reported input fingerprint/window/sentinels');self.active=False;self.commit(v,'checkpoint')
def schedule(id,n):
 ids=[id+30,id+60,id+90];rows=[('identity',[],'identity-before'),('setup',[id],'setup')]
 rows += [('batch',[i,1],'control-before-'+str(i))for i in ids]
 rows += [('batch',[id,n],'warmup-'+str(i))for i in range(3)]
 rows += [('batch',[id,n],'sample-'+str(i))for i in range(7)]
 rows += [('batch',[i,1],'control-after-'+str(i))for i in ids]
 return rows+[('checkpoint',[],'checkpoint'),('identity',[],'identity-after')]
def replay(job,result,raws,terminal):
 need(terminal['status']==0 and terminal['closed']is terminal['ownedGroupGone']is terminal['terminalExitZeroObserved']is True and terminal['timedOut']is terminal['outputLimitExceeded']is False and terminal['signal']is terminal['spawnError']is terminal['externalSignal']is None and terminal['errors']==terminal['signals']==[],'whole clean owned worker terminal')
 need(result['state']=='CODEC_COST_PHASE_WORKER_UNREVIEWED_RAW_AND_EXTERNAL_ZERO_REQUIRED_V1'and result['schemaVersion']==1,'actual worker result type')
 for key,want in dict(jobId=job['jobId'],phase=job['phase'],arm=job['expected']['arm'],caseId=job['expected']['caseId'],n=job['n'],repetition=job['repetition'],side=job['side'],comparison=job['comparison']).items():need(result[key]==want,'worker identity '+key)
 rows=schedule(job['expected']['caseId'],job['n']);need(len(result['records'])==len(raws)==len(rows)==20,'all20 full primitive records')
 c=Collector(job['expected']);samples=[];controls=[];codec=[]
 for i,((name,args,label),record,raw)in enumerate(zip(rows,result['records'],raws)):
  need(record['name']==raw['name']==name and record['args']==raw['args']==args and raw['schemaVersion']==1,'whole call order/arguments')
  r=raw['returned'];need(r['type']=='string'and r['fullPrimitiveCaptured']is True and r['codeUnits']==len(r['value'].encode('utf-16-le'))//2 and'thrown'not in raw,'full typed success primitive')
  value=decode(r['value']);need(value==record['value'],'whole parsed record equals retained raw string')
  ns=raw['elapsedNs'];need(type(ns)is str and ns.isdigit()and ns[0]!='0'and 0<int(ns)<=600000000000 and ns==record['elapsedNs']and raw['clockFailure']is None,'positive full-unit retained nanoseconds')
  timed=label.startswith('control-')or label.startswith('sample-');need(raw['timed']is record['timed']is timed,'separate controls/sample vs warmups')
  if name=='identity':c.identity(value)
  elif name=='setup':c.setup(value)
  elif name=='checkpoint':c.checkpoint(value)
  elif args[0]>=30:c.control(value,args[0]);controls.append(dict(role='control-before'if label.startswith('control-before')else'control-after',id=args[0],elapsedNs=ns,result=value['result']))
  else:c.batch(value,job['n']);codec.append(dict(record,role='sample'if label.startswith('sample')else'warmup'))
  if label.startswith('sample'):
   seconds=float(int(ns))/1e9;samples.append(dict(elapsedNs=ns,operationsPerSecond=job['n']/seconds,uncompressedBytesPerSecond=None if job['expected']['logicalBytes']==0 else job['expected']['logicalBytes']*job['n']/seconds,unit='uncompressed fixture bytes for encode and decode',controlSubtraction=False))
 need(result['counts']==c.counts and c.counts['codecCalls']==job['n']*10 and c.counts['controlOperations']==6,'exact final counters and no control codec calls')
 need(result['controls']==[r for r in result['records']if r['name']=='batch'and r['args'][0]>=30]and result['codec']==codec,'all duplicate control/codec record arrays preserve whole raw records')
 need(result['finalSourceAuditPassed']is True and result['controlSubtraction']is result['guestHeapBytesOrCapacityClaim']is False and result['wholeNodeProcessRssScopeOnly']is True,'final source and honest scope')
 p=result['processResources'];labels=['after-source-authentication-before-loader','after-reviewed-esm-tla-load','after-final-source-audit'];need(len(p['boundarySamples'])==3 and [x['label']for x in p['boundarySamples']]==labels,'three public process boundary labels')
 need(all(type(v['rssBytes'])is int and v['rssBytes']>0 and type(v['nodePublicMaxRssKilobytes'])is int and v['nodePublicMaxRssKilobytes']>0 for v in p['boundarySamples']),'positive process-only RSS data')
 need(p['reviewedEsmTlaLoadNs'].isdigit()and 0<int(p['reviewedEsmTlaLoadNs'])<=7200000000000 and p['nodePublicMaxRssKilobytes']>=max(v['nodePublicMaxRssKilobytes']for v in p['boundarySamples']),'bounded combined load/maxRSS')
 need(p['maxRssUnits']=='Node22 resourceUsage API kilobytes'and p['rssUnits']=='bytes'and p['wholeNodeProcessOnly']is p['includesAuthenticationAndLoaderOverhead']is True and p['parentHugeProofAndOracleReportsLoaded']is p['guestHeapOrCapacityClaim']is p['continuousRssSamplingClaim']is p['physicallyColdStartupClaim']is False,'honest whole-process resource scope')
 e=job['expected'];compressed=e['outputBytes']if e['direction']=='encode'else e['inputBytes']
 return dict(schemaVersion=1,jobId=job['jobId'],pid=terminal['pid'],phase=job['phase'],comparison=job['comparison'],repetition=job['repetition'],side=job['side'],arm=e['arm'],caseId=e['caseId'],n=job['n'],direction=e['direction'],inputBytesPerOperation=e['inputBytes'],outputBytesPerOperation=e['outputBytes'],logicalUncompressedBytesPerOperation=e['logicalBytes'],compressedBytesPerOperation=compressed,compressedToRawRatio=None if e['logicalBytes']==0 else compressed/e['logicalBytes'],warmups=3,samples=7,freshOwnedProcess=True,sampleMs=None,measuredSamples=samples,rawControls=controls,counts=c.counts,rawExitCode=0,ownedGroupGone=True,cleanTerminal=True,allRawRetained=True,finalSourceAuditPassed=True,wholeProcessMs=terminal['operationalElapsedMs'],processResources=p,controlSubtraction=False)
def select_curve(curve,case,comparison):
 cap=32768 if case<18 else 128;need(0<len(curve)<=int(math.log2(cap))+1,'bounded curve')
 winner=None
 for i,p in enumerate(curve):
  need(p['caseId']==case and p['comparison']==comparison and p['n']==2**i and p['n']<=cap and winner is None,'complete geometric curve; no postwinner pair')
  a=p['arms'];need(len(a)==2 and all(v['n']==p['n']and v['caseId']==case and v['warmups']==3 and v['samples']==1 and v['freshOwnedProcess']is True and v['rawExitCode']==0 and v['ownedGroupGone']is v['cleanTerminal']is v['allRawRetained']is v['finalSourceAuditPassed']is True and 0<v['sampleMs']<=600000 and v['sampleMs']<=v['wholeProcessMs']<=7200000 for v in a),'valid actual pilot pair')
  if all(v['sampleMs']>=50 for v in a):winner=p
 need(winner is not None,'both actual arms reached50 within cap')
 return dict(comparison=comparison,caseId=case,n=winner['n'],targetMs=50,perArm=[dict(arm=v['arm'],pilotBatchMs=v['sampleMs'],pilotPerOperationMs=v['sampleMs']/winner['n'],pilotWholeProcessMs=v['wholeProcessMs'])for v in winner['arms']],empiricalMatchedN=True,authorizesTiming=False)
def matched(calibrations):
 rows=[]
 for comparison,arms in [('same-engine-provider',['native-on','fflate-on']),('unused-profile',['fflate-on','fflate-off'])]:
  for case in range(30):
   values=[v for v in calibrations if v['comparison']==comparison and v['caseId']==case];need(len(values)==1,'one complete matched case');v=values[0]
   for arm in arms:
    u,=[u for u in v['perArm']if u['arm']==arm];per=u['pilotPerOperationMs'];n=v['n'];budget=math.ceil(2*per*n*(3+7)+per*n+120000+2*max(0,u['pilotWholeProcessMs']-per));need(0<budget<=7200000,'unclipped original worker budget')
    rows.append(dict(comparison=comparison,caseId=case,arm=arm,n=n,workerTimeoutMs=budget,publicCallHardMs=600000))
 return rows
