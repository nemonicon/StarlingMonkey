"""Independent completed timing read/hash/full compact-return DATA replay only."""
from pathlib import Path
import ast,datetime,hashlib,json,os,re,stat
P=Path(__file__).resolve().parent;Z=P.parent;D=Path('/private/tmp/starling-node-compat/zlib-cost-timing-v5');SOURCE='e799350100bb3b54148fdc5bd46a857579a6aae7608890f620569ea3704ab321'
model={};exec(compile((P/'model.py').read_bytes(),str(P/'model.py'),'exec'),model)
checks=0;seen={};cache={}
def need(v,n):
 global checks
 assert v,n;checks+=1
def ident(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def row(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def verify(r):
 p=Path(r['path']);need(p.is_absolute()and p.is_file()and not p.is_symlink(),'ordinary absolute read path');real=str(p.resolve());a=p.stat()
 if real not in cache:need(row(p)=={k:r[k]for k in('path','sha256','bytes')},'whole exact file hash/size');need(ident(a)==ident(p.stat()),'stable streamed file');cache[real]=dict(expected={k:r[k]for k in('sha256','bytes')},identity=ident(a))
 else:need(cache[real]['expected']=={k:r[k]for k in('sha256','bytes')}and cache[real]['identity']==ident(a),'same repeated exact descriptor')
 seen[str(p)]={k:r[k]for k in('path','sha256','bytes')};return p
def data(r):return json.loads(verify(r).read_bytes())
def local(n):need(type(n)is str and n and not n.startswith('/')and'\\'not in n and all(v not in('','.','..')for v in n.split('/')),'finite exact local name');return n
def family(r):
 x=data(r);base=Path(r['path']).parent;names=set()
 for v in x['files']:
  n=local(v['path']);need(n not in names,'unique family member');names.add(n);verify(dict(path=str(base/n),sha256=v['sha256'],bytes=v['bytes']))
 need(not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names|{'index.json'},'complete source/proof family')
 return x
def save(n,v):
 with(P/n).open('x')as f:json.dump(v,f,indent=2);f.write('\n')

controller_row=dict(path='/private/tmp/starling-node-compat/zlib-cost-timing-v5-external-root/controller-observation.json',sha256='ade1be0e2560d49dd41daf5e1b990ffccac0102552196d0c84fa3a34073239b1',bytes=8436)
controller=data(controller_row)
auth=data(controller['rootAuthority']);controller_config=data(controller['config']);cfg=data(controller_config['runConfig']);term=data(controller['rawExternalTerminal']);phase=data(auth['phaseAuthority']);quiet=data(auth['quietWindowAuthority']);plan=data(auth['preparedPlan']);matched=data(auth['warmNMatchedPlan'])
close_row=dict(path=str(Z/'cost-timing-v5-quiet-window-completion.json'),sha256='253c79e5a2feee3a333063a78927a23c7edb67bbd4242bc32de04016c3412248',bytes=1602);close=data(close_row)
need(controller['state']=='ROOT_OBSERVED_ZLIB_COST_TIMING_V5_COMPLETE_UNREVIEWED_V1' and controller['errors']==[] and controller['finalSourceAndOriginalInputProtectionPassed']is True,'actual clean controller observation')
need(auth['state']=='ROOT_REVIEWED_ZLIB_COST_PILOT_TIMING_PHASE_V1' and auth['phase']=='timing' and auth['sourceIndexSha256']==SOURCE and auth['actionAllowed']is True and auth['outputRoot']==str(D)and auth['globalBudgetMs']==5400000,'actual timing-only authority')
need(cfg['sourceIndex']['sha256']==SOURCE and cfg['rootAction']==controller['rootAuthority'],'genuine unprojected V5 run config')
for key in ('sourceIndexSha256','phase','runId','globalBudgetMs','preparedPlan','calibrationSourceIndex','warmNPlan','warmNMatchedPlan','quietWindowAuthority'):need(phase[key]==auth[key],'whole phase binding '+key)
need(auth['calibrationSourceIndex']['sha256']=='b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1'and auth['warmNPlan']['index']['sha256']=='64472b266c9546136fda6602c5aefb15bd44497a043d5f8c2857f2e76c6137a8'and auth['warmNMatchedPlan']['sha256']=='e545f0064485d87cd1bcb919221997578b427df8499e5f8271e2e4e445ccdf3b','original B5 calibration separate from new V5')
need(plan['calibrationSourceIndex']==auth['calibrationSourceIndex']and plan['calibrationReview']==auth['warmNPlan']and plan['calibrationMatchedPlan']==auth['warmNMatchedPlan']and plan['sourceIndexSha256']==SOURCE,'fresh actual V5 plan and original calibration roles')
need(term['pid']==43889 and term['rawExitCode']==0 and term['allObservedOwnedGroupsGone']is term['parentOwnedGroupGone']is True and term['timeout']is term['forcedCleanup']is False and all(term[k]==[]for k in('signals','errors','interruptedSignals','remainingObservedPids'))and all(g['alive']is False for g in term['finalGroups']),'clean external timing parent and all owned groups')
need(term['authority']==controller['rootAuthority']and term['stderr']['bytes']==0,'authority bound empty stderr')
for r in(term['stdout'],term['stderr']):verify(r)
stdout=[json.loads(line)for line in Path(term['stdout']['path']).read_text().splitlines()];observed=controller['observation']
need(stdout[:-1]==observed['originalJsonlHeartbeatRecords']and stdout[-1]==observed['originalRelativePublishedRows'],'whole actual JSONL prefix and relative publication')
need(all(v['event']=='codec-phase-operational-heartbeat'and v['partialObservationOnly']is True for v in stdout[:-1]),'operational prefix not timed samples')
need(close['actualNodeParentExitCode']==close['actualRootControllerExitCode']==0 and close['externalParentTerminal']==controller['rawExternalTerminal']and close['controllerObservation']==controller_row and close['quietWindow']==auth['quietWindowAuthority']and close['taskHoldReleasedAfterThisReceipt']is True,'actual terminal/window closure')
absolute=observed['absoluteOutputDescriptors']
for key,name in [('index','index.json'),('completion','completion.json')]:need(dict(absolute[key],path=name)==observed['originalRelativePublishedRows'][key]and absolute[key]['path']==str(D/name),'relative vs separate confined absolute tuple')
index=data(absolute['index']);completion=data(absolute['completion']);need(index['schemaVersion']==1 and len(index['files'])==17642,'complete actual17642 output index')
files={}
for r in index['files']:
 n=local(r['path']);need(n not in files,'unique actual timing member');files[n]=r;verify(dict(r,path=str(D/n)))
actual=set();pipe_modes=set()
for p in D.rglob('*'):
 s=p.lstat();need(not p.is_symlink(),'no output symlink')
 if p.is_file():
  n=p.relative_to(D).as_posix();pipe=n.startswith('processes/')and n.endswith(('.stdout.txt','.stderr.txt'));need(s.st_nlink==1,'independently linked output')
  if pipe:need(stat.S_IMODE(s.st_mode)&0o111==0,'nonexecutable inherited raw data pipe');pipe_modes.add(oct(stat.S_IMODE(s.st_mode)))
  else:need(stat.S_IMODE(s.st_mode)==0o600,'explicit private durable data')
  actual.add(n)
 else:need(p.is_dir()and stat.S_IMODE(s.st_mode)==0o700,'private ordinary directory')
need(actual==set(files)|{'index.json','completion.json'}and len(actual)==17644,'exact actual17644 regular membership')
need(completion['index']==dict(absolute['index'],path='index.json')and completion['result']==dict(observed['actualResult'],path='results.json')and completion['sourceIndexSha256']==SOURCE,'actual completion tuple')
results=data(observed['actualResult']);aggregate=data(dict(files['aggregate-observations.json'],path=str(D/'aggregate-observations.json')))
need(results['phase']=='timing'and results['sourceIndexSha256']==SOURCE and results['rootAuthority']==controller['rootAuthority']and results['sourceRecheckPassed']is True and results['controlsSubtracted']is results['metadataProjection']is results['operationalAdmission']is results['runtimeAcceptanceClaim']is results['timingAcceptanceClaim']is False,'whole timing result identity and closed acceptance')
origins=results['origins'];need(len(origins)==len(results['observations'])==results['actualWorkers']==360 and results['calibrations']==[],'all360 units and no new pilot')
expected={(r['arm'],r['caseId']):r for r in plan['expected']};need(len(expected)==90 and len(plan['artifacts'])==3 and len(matched['rows'])==120,'complete actual90/3/120 plan')
requested={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'C','LC_ALL':'C','TZ':'UTC','RAYON_NUM_THREADS':'1','BINARYEN_CORES':'1','CARGO_BUILD_JOBS':'1','PYTHONDONTWRITEBYTECODE':'1'}
workers=[];observations=[];pids=set();deadline=None;allnames={'results.json','aggregate-observations.json'};total_codec_ops=0;control_rows=[]
for origin,parent in zip(origins,results['observations']):
 jobid=origin['jobId'];dn='descriptors/'+jobid+'.json';job=data(dict(files[dn],path=str(D/dn)));case=job['expected']['caseId'];arm=job['expected']['arm'];n=job['n'];cap=32768 if case<18 else 128
 need(job['phase']=='timing'and job['repetition']in [0,1,2]and job['warmups']==3 and job['samples']==7 and type(n)is int and 0<n<=cap and n&(n-1)==0,'exact bounded actual timing worker')
 match,=[r for r in matched['rows']if r['caseId']==case and r['arm']==arm and r['comparison']==job['comparison']]
 need(job['n']==match['n']and job['workerTimeoutMs']==match['workerTimeoutMs']and job['publicCallHardMs']==600000,'exact reviewed matched N/budget')
 need(job['expected']==expected[(arm,case)]and job['artifact']==plan['artifacts'][arm]and job['rootAuthority']==controller['rootAuthority']and job['sourceIndex']==cfg['sourceIndex']and job['sourceIndexSha256']==SOURCE and job['sourceIndependentReviewIndex']==auth['sourceIndependentReview']['index']and job['preparedPlan']==auth['preparedPlan']and job['phaseAuthority']==auth['phaseAuthority']and job['quietWindowAuthority']==auth['quietWindowAuthority']and job['warmNPlan']==auth['warmNMatchedPlan']and job['calibrationSourceIndex']==auth['calibrationSourceIndex'],'all worker source/plan/artifact/calibration relations')
 need(job['outputRoot']==str(D/'jobs'/jobid)and job['parentOutputRoot']==str(D),'owned worker namespace')
 base=D/'jobs'/jobid;prefix='jobs/'+jobid+'/';wi=data(dict(files[prefix+'index.json'],path=str(base/'index.json')));wc=data(dict(files[prefix+'completion.json'],path=str(base/'completion.json')));wr=data(origin['result']);tn='processes/'+jobid+'.terminal.json';wt=data(dict(files[tn],path=str(D/tn)))
 need(origin['terminal']==tn and origin['pid']==wt['pid']and wt['pid']not in pids,'all fresh actual PIDs');pids.add(wt['pid'])
 need(origin['result']==dict(files[prefix+'worker-results.json'],path=str(base/'worker-results.json'))and origin['component']==job['artifact']['component'],'indexed actual worker result/component')
 need(wc['state']=='CODEC_PHASE_WORKER_COMPLETE_EXTERNAL_OWNED_ZERO_REQUIRED_V1'and wc['jobId']==jobid and wc['sourceIndexSha256']==SOURCE and wc['index']==dict(files[prefix+'index.json'],path='index.json')and wc['results']==dict(origin['result'],path='worker-results.json')and wc['component']==job['artifact']['component'],'whole actual worker completion')
 mapping={r['path']:r for r in wi['files']};need(len(mapping)==len(wi['files'])==42 and all(dict(r,path=prefix+r['path'])==files[prefix+r['path']]for r in wi['files']),'all42 nested worker members match parent')
 started=data(dict(mapping['started.json'],path=str(base/'started.json')));need(started['jobId']==jobid and started['sourceIndex']==job['sourceIndex']and started['rootAuthority']==controller['rootAuthority']and started['expected']==job['expected']and started['artifact']==job['artifact'],'preloader started actual contexts')
 need(started['platformFacts']==dict(platform='darwin',uid=os.getuid())and started['observedEnvironment']in[requested,dict(requested,__CF_USER_TEXT_ENCODING='0x'+format(os.getuid(),'X')+':0x0:0x0')],'actual finite8/plusDarwin environment')
 need(wt['exactEnvironment']==requested and wt['executable']=='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'and wt['args']==[str(Z/'cost-pilot-timing-candidate-v5/worker.mjs'),json.dumps(dict(files[dn],path=str(D/dn)),separators=(',',':'))]and wt['timeoutMs']==match['workerTimeoutMs']and wt['publicCallTimeoutMs']==600000 and wt['parentFsyncBeforeCallAck']is True,'actual Node/CLI/descriptor/watchdog request')
 if deadline is None:deadline=wt['phaseDeadlineMonotonicMs']
 need(wt['phaseDeadlineMonotonicMs']==deadline,'one immutable global phase deadline')
 schedule=model['schedule'](case,n);raws=[];jobnames={'started.json','worker-results.json'}
 for i,(name,args,label)in enumerate(schedule):
  before=f'{i:04d}-{label}-before.json';rn=f'{i:04d}-{label}-raw.json';jobnames|={before,rn};timed=label.startswith('control-')or label.startswith('sample-')
  need(data(dict(mapping[before],path=str(base/before)))==dict(schemaVersion=1,name=name,args=args,partial=True,timed=timed),'full before-call record')
  raw=data(dict(mapping[rn],path=str(base/rn)));need(wr['records'][i]['raw']==mapping[rn]and raw['partial']is True,'full raw retention record origin');raws.append(raw)
 need(set(mapping)==jobnames and{p.name for p in base.iterdir()}==jobnames|{'index.json','completion.json'},'exact20call/42file schedule')
 observation=model['replay'](job,wr,raws,wt);need(observation==parent,'entire parent observation replayed from all20 typed raw strings');observations.append(observation);total_codec_ops+=wr['counts']['codecCalls']
 events=[json.loads(line)for line in verify(wt['stdout']).read_text().splitlines()];need(len(events)==41,'all20start/end plus complete marker')
 for i,(name,args,label)in enumerate(schedule):need(events[2*i]==dict(event='cost-public-call-start',sequence=i,name=name)and events[2*i+1]==dict(event='cost-public-call-end',sequence=i,name=name),'all bounded marker order')
 need(events[-1]==dict(event='cost-worker-complete',index=wc['index'],completion=dict(files[prefix+'completion.json'],path='completion.json'))and wt['stderr']['bytes']==0,'complete success marker and empty stderr')
 launch=data(dict(files['processes/'+jobid+'.launch.json'],path=str(D/'processes'/(jobid+'.launch.json'))));need(launch['exactEnvironment']==requested and launch['args']==wt['args']and launch['executable']==wt['executable']and launch['publicCallTimeoutMs']==600000 and launch['phaseDeadlineMonotonicMs']==deadline,'launch vs terminal request')
 for key in ('jobId','arm','comparison','caseId','n','repetition','side'):need(origin[key]==(job[key]if key not in('caseId','arm')else job['expected'][key]),'whole origin '+key)
 allnames.add(dn);allnames|={'processes/'+jobid+s for s in('.launch.json','.terminal.json','.stdout.txt','.stderr.txt')};allnames|={prefix+v for v in jobnames|{'index.json','completion.json'}}
 for raw,record,(_,_,label)in zip(raws,wr['records'],schedule):
  if label.startswith('control-'):control_rows.append(dict(jobId=jobid,pid=wt['pid'],comparison=job['comparison'],repetition=job['repetition'],arm=arm,caseId=case,n=1,role=label,raw=dict(record['raw'],path=str(base/record['raw']['path'])),elapsedNs=raw['elapsedNs'],value=record['value']))
 workers.append(dict(jobId=jobid,pid=wt['pid'],comparison=job['comparison'],caseId=case,arm=arm,n=n,repetition=job['repetition'],side=job['side'],rawPrimitiveCalls=20,codecBatchCalls=10,codecOperations=wr['counts']['codecCalls'],n1Controls=6,workerResult=origin['result'],terminal=dict(files[tn],path=str(D/tn)),samplesNs=[r['elapsedNs']for r in observation['measuredSamples']],controlsNs=[r['elapsedNs']for r in observation['rawControls']],wholeProcessMs=wt['operationalElapsedMs'],processResources=wr['processResources']))
ordered=[]
for comparison,arms,short in [('same-engine-provider',['native-on','fflate-on'],'provider'),('unused-profile',['fflate-on','fflate-off'],'profile')]:
 for case in range(30):
  for repetition in range(3):
   for side in (['B','A']if repetition==1 else['A','B']):
    arm=arms[0 if side=='A'else 1];jobid='timing-'+short+'-c'+str(case)+'-r'+str(repetition)+'-'+arm;ordered.append(jobid)
    value,=[v for v in observations if v['jobId']==jobid];need(value['side']==side and value['repetition']==repetition,'AB/BA/AB original side/repetition')
need(ordered==[v['jobId']for v in origins]and len(set(ordered))==360,'entire360process ABBAAB schedule no omission')
need(set(files)==allnames and len(files)==360*49+2 and results['codecBatchCalls']==3600 and results['rawN1ControlOperations']==2160,'all file/call/control counts')
need(len(control_rows)==2160,'all raw N1 control values')
for real,r in cache.items():need(ident(Path(real).stat())==r['identity'],'final stable completed output')
save('worker-ledger.json',dict(schemaVersion=1,workers=workers,rawTypedCalls=7200,codecBatchCalls=3600,codecOperations=total_codec_ops,n1Controls=2160,timedSamples=2520,warmups=1080,actualBatchPayloadArraysRetained=False,allActualCompactReturnedFNVsReplayed=True))
save('control-ledger.json',dict(schemaVersion=1,records=control_rows,operations=2160,codecCalls=0,subtracted=False))
save('replayed-observations.json',dict(schemaVersion=1,observations=observations,rawTypedCalls=7200))
save('output-audit.json',dict(schemaVersion=1,verifiedPassed=True,checks=checks,controllerObservation=controller_row,actualIndex=absolute['index'],actualCompletion=absolute['completion'],actualResults=observed['actualResult'],actualAggregate=dict(files['aggregate-observations.json'],path=str(D/'aggregate-observations.json')),rootAuthority=controller['rootAuthority'],runConfig=controller_config['runConfig'],externalTerminal=controller['rawExternalTerminal'],windowCompletion=close_row,workers=360,freshWorkerPids=360,rawTypedCalls=7200,codecBatches=3600,codecOperations=total_codec_ops,n1Controls=2160,timedSamples=2520,warmups=1080,indexedFiles=17642,regularFiles=17644,rawPipeObservedModes=sorted(pipe_modes),allContainingDirectories0700=True,heartbeats=len(stdout)-1,allRawTypedReturnsReplayed=True,ownerActionsInvoked=False))
save('output-input-hashes.json',dict(schemaVersion=1,files=[seen[p]for p in sorted(seen)]))
print(json.dumps(dict(rawDataReplayPassed=True,checks=checks,files=len(seen),workers=360,rawTypedCalls=7200,controls=2160,timedSamples=2520,ownerActionsInvoked=False)))
