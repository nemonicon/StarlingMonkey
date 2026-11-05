"""Independent completed pilot read/hash/full compact-return DATA replay only."""
from pathlib import Path
import ast,datetime,hashlib,json,os,re,stat
P=Path(__file__).resolve().parent;Z=P.parent;D=Path('/private/tmp/starling-node-compat/zlib-cost-pilot-v4');SOURCE='b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1'
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
rootrow=dict(path=str(Z/'cost-pilot-v4-root-results.json'),sha256='3f7c0b443490692e4b4a04d22ee6c83a1a84bc72d091703fa29f18cb77002e42',bytes=4270);root=data(rootrow)
need(root['rawParentExitCode']==0 and root['sourceIndexSha256']==SOURCE and root['observedParentPid']==80579,'actual completed Root pilot tuple')
auth=data(root['rootAuthority']);cfg=data(root['rootConfig']);term=data(root['externalTerminal']);close=data(root['windowCompletion']);phase=data(auth['phaseAuthority']);quiet=data(auth['quietWindowAuthority']);plan=data(auth['preparedPlan'])
need(cfg['sourceIndex']['sha256']==SOURCE and cfg['rootAction']==root['rootAuthority']and auth['sourceIndexSha256']==SOURCE and auth['phase']=='pilot-candidate'and auth['actionAllowed']is True and auth['outputRoot']==str(D)and auth['globalBudgetMs']==5400000,'exact real pilot authority/options')
need(auth['warmNPlan']is auth['warmNMatchedPlan']is None and phase['phase']=='pilot-candidate'and phase['globalBudgetMs']==auth['globalBudgetMs']and phase['preparedPlan']==auth['preparedPlan']and phase['quietWindowAuthority']==auth['quietWindowAuthority'],'no timing/matched-plan authority in actual pilot')
need(term['pid']==80579 and term['rawExitCode']==0 and term['allObservedOwnedGroupsGone']is term['parentOwnedGroupGone']is True and term['timeout']is term['forcedCleanup']is False and all(term[k]==[]for k in('signals','errors','interruptedSignals','remainingObservedPids'))and all(g['alive']is False for g in term['finalGroups']),'whole clean external pilot terminal')
need(term['authority']==root['rootAuthority']and term['stderr']['bytes']==0,'actual authority and empty complete external stderr')
for r in(term['stdout'],term['stderr']):verify(r)
stdout=[json.loads(line)for line in Path(term['stdout']['path']).read_text().splitlines()];need(len(stdout)==3 and stdout[:2]==root['rawOperationalHeartbeats']and stdout[2]==root['originalRelativePublicationRows'],'all original two heartbeats plus relative final publication')
need(all(v['event']=='codec-phase-operational-heartbeat'and v['partialObservationOnly']is True for v in stdout[:2]),'operational prefix never samples or completion')
need(close['measurementHoldReleased']is True and close['rawParentExitCode']==0 and close['externalTerminal']==root['externalTerminal']and close['originalQuietWindowAuthority']==auth['quietWindowAuthority']and close['timingAuthorized']is False,'window closed after actual terminal, no timing grant')
for key,name in(('index','index.json'),('completion','completion.json')):need(root['originalRelativePublicationRows'][key]==dict(root['actualIndex']if key=='index'else root['completion'],path=name),'relative publication identity preserved')
index=data(root['actualIndex']);completion=data(root['completion']);need(index['schemaVersion']==1 and len(index['files'])==33066,'actual complete33,066 index bound')
files={}
for r in index['files']:
 n=local(r['path']);need(n not in files,'unique actual pilot member');files[n]=r;verify(dict(r,path=str(D/n)))
actual=set();raw_pipe_modes={}
for p in D.rglob('*'):
 s=p.lstat();need(not p.is_symlink(),'no actual pilot output link')
 if p.is_file():
  name=p.relative_to(D).as_posix();pipe=name.startswith('processes/')and name.endswith(('.stdout.txt','.stderr.txt'))
  need(s.st_nlink==1,'ordinary independently linked output')
  if pipe:need(stat.S_IMODE(s.st_mode)&0o111==0,'inherited default-mode data pipe is not executable');raw_pipe_modes[name]=oct(stat.S_IMODE(s.st_mode))
  else:need(stat.S_IMODE(s.st_mode)==0o600,'explicitly private durable output mode')
  actual.add(name)
 else:need(p.is_dir()and stat.S_IMODE(s.st_mode)==0o700,'ordinary private output directory')
need(actual==set(files)|{'index.json','completion.json'}and len(actual)==33068,'complete actual33,068 membership')
need(completion['index']==dict(root['actualIndex'],path='index.json')and completion['result']==dict(root['actualResults'],path='results.json')and completion['sourceIndexSha256']==SOURCE,'whole completion tuple')
results=data(root['actualResults']);matched=data(root['matchedNPlan']);need(results['phase']=='pilot-candidate'and results['sourceIndexSha256']==SOURCE and results['rootAuthority']==root['rootAuthority']and results['sourceRecheckPassed']is True and results['controlsSubtracted']is results['metadataProjection']is results['operationalAdmission']is results['runtimeAcceptanceClaim']is results['timingAcceptanceClaim']is False,'actual parent pilot result scope')
origins=results['origins'];need(len(origins)==len(results['observations'])==results['actualWorkers']==892 and len(results['calibrations'])==60,'all892 workers/all60 calibrations')
expected={(r['arm'],r['caseId']):r for r in plan['expected']};need(len(expected)==90 and len(plan['artifacts'])==3,'all actual compact plan cases/artifacts')
requested={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'C','LC_ALL':'C','TZ':'UTC','RAYON_NUM_THREADS':'1','BINARYEN_CORES':'1','CARGO_BUILD_JOBS':'1','PYTHONDONTWRITEBYTECODE':'1'}
worker_ledger=[];observations=[];pids=set();deadline=None;allnames={'results.json','matched-n-plan.json'};total_codec_ops=0
for origin,parent_observation in zip(origins,results['observations']):
 jobid=origin['jobId'];descriptor_name='descriptors/'+jobid+'.json';need(descriptor_name in files,'actual owned compact descriptor');job=data(dict(files[descriptor_name],path=str(D/descriptor_name)));case=job['expected']['caseId'];arm=job['expected']['arm'];n=job['n'];cap=32768 if case<18 else 128
 need(job['phase']=='pilot-candidate'and job['repetition']is None and job['warmups']==3 and job['samples']==1 and type(n)is int and n>0 and n<=cap and n&(n-1)==0,'exact bounded actual pilot worker')
 need(job['expected']==expected[(arm,case)]and job['artifact']==plan['artifacts'][arm]and job['rootAuthority']==root['rootAuthority']and job['sourceIndex']==cfg['sourceIndex']and job['sourceIndexSha256']==SOURCE and job['sourceIndependentReviewIndex']==auth['sourceIndependentReview']['index']and job['preparedPlan']==auth['preparedPlan']and job['phaseAuthority']==auth['phaseAuthority']and job['quietWindowAuthority']==auth['quietWindowAuthority']and job['warmNPlan']is None,'whole worker source/plan/proof/artifact contexts')
 need(job['outputRoot']==str(D/'jobs'/jobid)and job['parentOutputRoot']==str(D)and job['workerTimeoutMs']==job['publicCallHardMs']==600000,'exact owned namespace/budget')
 base=D/'jobs'/jobid;prefix='jobs/'+jobid+'/';wi=data(dict(files[prefix+'index.json'],path=str(base/'index.json')));wc=data(dict(files[prefix+'completion.json'],path=str(base/'completion.json')));wr=data(origin['result']);terminal_name='processes/'+jobid+'.terminal.json';wt=data(dict(files[terminal_name],path=str(D/terminal_name)))
 need(origin['terminal']==terminal_name and origin['pid']==wt['pid']and wt['pid']not in pids,'all fresh actual owned PIDs');pids.add(wt['pid'])
 need(origin['result']==dict(files[prefix+'worker-results.json'],path=str(base/'worker-results.json'))and origin['component']==job['artifact']['component'],'actual indexed worker result/component')
 need(wc['state']=='CODEC_PHASE_WORKER_COMPLETE_EXTERNAL_OWNED_ZERO_REQUIRED_V1'and wc['jobId']==jobid and wc['sourceIndexSha256']==SOURCE and wc['index']==dict(files[prefix+'index.json'],path='index.json')and wc['results']==dict(origin['result'],path='worker-results.json')and wc['component']==job['artifact']['component'],'whole actual worker completion')
 mapping={r['path']:r for r in wi['files']};need(len(mapping)==len(wi['files'])==30 and all(dict(r,path=prefix+r['path'])==files[prefix+r['path']]for r in wi['files']),'all30 nested worker index members agree parent')
 started=data(dict(mapping['started.json'],path=str(base/'started.json')));need(started['jobId']==jobid and started['sourceIndex']==job['sourceIndex']and started['rootAuthority']==root['rootAuthority']and started['expected']==job['expected']and started['artifact']==job['artifact'],'actual preloader started source/expected/artifact record')
 env=started['observedEnvironment'];facts=started['platformFacts'];need(facts=={'platform':'darwin','uid':os.getuid()}and env in[requested,dict(requested,__CF_USER_TEXT_ENCODING='0x'+format(os.getuid(),'X')+':0x0:0x0')],'actual finite runtime environment after platform initialization')
 need(wt['exactEnvironment']==requested and wt['executable']=='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'and wt['args']==[str(Z/'cost-pilot-timing-candidate-v4/worker.mjs'),json.dumps(dict(files[descriptor_name],path=str(D/descriptor_name)),separators=(',',':'))]and wt['timeoutMs']==wt['publicCallTimeoutMs']==600000 and wt['parentFsyncBeforeCallAck']is True,'real owned plain Node/CLI/descriptor/watchdog request')
 if deadline is None:deadline=wt['phaseDeadlineMonotonicMs']
 need(wt['phaseDeadlineMonotonicMs']==deadline,'one fixed global phase deadline')
 schedule=model['schedule'](case,n);raws=[];jobnames={'started.json','worker-results.json'}
 for i,(name,args,label)in enumerate(schedule):
  before=f'{i:04d}-{label}-before.json';rawname=f'{i:04d}-{label}-raw.json';jobnames|={before,rawname}
  beforevalue=data(dict(mapping[before],path=str(base/before)));timed=label.startswith('control-')or label.startswith('sample-');need(beforevalue==dict(schemaVersion=1,name=name,args=args,partial=True,timed=timed),'whole before-call raw record')
  raw=data(dict(mapping[rawname],path=str(base/rawname)));need(wr['records'][i]['raw']==mapping[rawname]and raw['partial']is True,'whole durable raw descriptor origin');raws.append(raw)
 need(set(mapping)==jobnames and{p.name for p in base.iterdir()}==jobnames|{'index.json','completion.json'},'complete exact actual worker file schedule')
 observation=model['replay'](job,wr,raws,wt);need(observation==parent_observation,'entire parent observation independently replayed from typed raw strings');observations.append(observation);total_codec_ops+=wr['counts']['codecCalls']
 events=[json.loads(line)for line in verify(wt['stdout']).read_text().splitlines()];need(len(events)==29,'all14start/end plus one complete marker')
 for i,(name,args,label)in enumerate(schedule):need(events[2*i]==dict(event='cost-public-call-start',sequence=i,name=name)and events[2*i+1]==dict(event='cost-public-call-end',sequence=i,name=name),'all bounded public-call progress order')
 need(events[-1]==dict(event='cost-worker-complete',index=wc['index'],completion=dict(files[prefix+'completion.json'],path='completion.json'))and wt['stderr']['bytes']==0,'whole successful terminal progress and empty stderr')
 launch=data(dict(files['processes/'+jobid+'.launch.json'],path=str(D/'processes'/(jobid+'.launch.json'))));need(launch['exactEnvironment']==requested and launch['args']==wt['args']and launch['executable']==wt['executable']and launch['publicCallTimeoutMs']==600000 and launch['phaseDeadlineMonotonicMs']==deadline,'launch vs terminal request identical')
 for k in ('jobId','arm','comparison','caseId','n','repetition','side'):need(origin[k]==(job[k]if k not in('caseId','arm')else job['expected'][k]),'parent origin exact '+k)
 allnames.add(descriptor_name);allnames|={'processes/'+jobid+s for s in('.launch.json','.terminal.json','.stdout.txt','.stderr.txt')};allnames|={prefix+v for v in jobnames|{'index.json','completion.json'}}
 worker_ledger.append(dict(jobId=jobid,pid=wt['pid'],comparison=job['comparison'],caseId=case,arm=arm,n=n,rawPrimitiveCalls=14,codecBatchCalls=4,codecOperations=wr['counts']['codecCalls'],n1ControlOperations=6,workerResult=origin['result'],terminal=dict(files[terminal_name],path=str(D/terminal_name)),sampleNs=observation['measuredSamples'][0]['elapsedNs'],wholeProcessMs=wt['operationalElapsedMs']))
curves=[];selected=[];ordered=[]
for comparison,arms,short in [('same-engine-provider',['native-on','fflate-on'],'provider'),('unused-profile',['fflate-on','fflate-off'],'profile')]:
 for case in range(30):
  name='calibration/'+comparison+'-c'+str(case)+'.json';allnames.add(name);calibration=data(dict(files[name],path=str(D/name)));curve=calibration['curve'];need(curve and all(p['comparison']==comparison and p['caseId']==case for p in curve),'all actual curve identities')
  for pair in curve:
   want=[]
   for side,arm in zip(['A','B'],arms):
    id='pilot-'+short+'-c'+str(case)+'-n'+str(pair['n'])+'-'+arm;found=[o for o in observations if o['jobId']==id];need(len(found)==1 and found[0]['side']==side,'one actual paired arm');want.append(found[0]);ordered.append(id)
   need(pair['arms']==want,'whole actual pair from raw replay')
  value=model['select_curve'](curve,case,comparison);need(value==calibration['selected'],'first both>=50 exact selected curve');selected.append(value);curves.append(dict(comparison=comparison,caseId=case,candidates=len(curve),winningN=value['n'],earlierPairsBelowBothTarget=True,selected=value))
need(ordered==[v['jobId']for v in origins]and len(ordered)==len(set(ordered))==892,'all original comparison/case/N/A-B order; no skipped or reused process')
need(selected==results['calibrations']and matched['state']=='ACTUAL_MATCHED_N_PLAN_DATA_V1'and matched['rows']==model['matched'](selected)and len(matched['rows'])==120 and matched['independentReviewStillRequired']is True,'full actual matched N/budget plan independently recomputed')
need(set(files)==allnames and len(files)==892*37+62,'all per-worker/parent source-derived file roles; no omitted files')
need(results['rawN1ControlOperations']==892*6==5352 and results['codecBatchCalls']==892*4==3568,'pilot counts distinct from timing protocol')
save('worker-ledger.json',dict(schemaVersion=1,workers=worker_ledger,rawPrimitiveCalls=12488,codecBatchCalls=3568,codecOperations=total_codec_ops,n1ControlOperations=5352,actualBatchOutputPayloadBytesRetained=False,allCompactReturnedFNVsReplayed=True))
save('curve-ledger.json',dict(schemaVersion=1,curves=curves,calibrations=selected,matchedRows=matched['rows'],controlsSubtracted=False,performanceConclusion=False))
save('output-audit.json',dict(schemaVersion=1,verifiedPassed=True,checks=checks,rootObservation=rootrow,actualIndex=root['actualIndex'],actualCompletion=root['completion'],actualResults=root['actualResults'],matchedPlan=root['matchedNPlan'],rootAuthority=root['rootAuthority'],rootConfig=root['rootConfig'],externalTerminal=root['externalTerminal'],windowCompletion=root['windowCompletion'],actualWorkers=892,rawTypedCalls=12488,n1Controls=5352,codecBatchCalls=3568,codecOperations=total_codec_ops,calibratedCases=60,matchedRows=120,actualIndexedFiles=33066,actualFiles=33068,rawPipeObservedModes=sorted(set(raw_pipe_modes.values())),rawPipeFiles=len(raw_pipe_modes),rawPipeModeExplicitInInheritedSource=False,allContainingDirectories0700=True,originalHeartbeats=stdout[:2],allActualRawTypedReturnsReplayed=True,allMatchedNReviewed=True,ownerActionsInvoked=False))
save('output-input-hashes.json',dict(schemaVersion=1,files=[seen[p]for p in sorted(seen)]))
print(json.dumps(dict(outputReplayPassed=True,checks=checks,files=len(seen),workers=892,rawCalls=12488,curves=60,matchedRows=120,ownerActionsInvoked=False)))
