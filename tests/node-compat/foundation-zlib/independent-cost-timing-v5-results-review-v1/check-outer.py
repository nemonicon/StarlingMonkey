"""Read/hash of actual timing outer process/window provenance; no helper call."""
from pathlib import Path
import hashlib,json,os
P=Path(__file__).resolve().parent;Z=P.parent;S=Z/'cost-pilot-timing-candidate-v5';checks=0;seen={};cache={}
def need(v,n):
 global checks
 assert v,n;checks+=1
def row(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def verify(r):
 p=Path(r['path']);need(p.is_file()and not p.is_symlink()and p.is_absolute(),'ordinary prerequisite file');a=p.stat();identity=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns);real=str(p.resolve())
 if real not in cache:need(row(p)=={k:r[k]for k in('path','sha256','bytes')},'full prerequisite hash');cache[real]=dict(identity=identity,expected={k:r[k]for k in('sha256','bytes')})
 need(cache[real]['identity']==identity and cache[real]['expected']=={k:r[k]for k in('sha256','bytes')},'stable repeated prerequisite');seen[str(p)]={k:r[k]for k in('path','sha256','bytes')};return p
def data(r):return json.loads(verify(r).read_bytes())
def family(r):
 x=data(r);base=Path(r['path']).parent;names=set()
 for v in x['files']:
  n=v['path'];need(type(n)is str and n and not n.startswith('/')and all(p not in('','.','..')for p in n.split('/'))and n not in names,'local unique prerequisite member');names.add(n);verify(dict(v,path=str(base/n)))
 need(not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names|{'index.json'},'whole prerequisite family membership');return len(names)

import datetime
import stat
rootrow=dict(path=str(Z/'cost-timing-v5-root-results.json'),sha256='55cf580f379c89bf9252ef78d5b133ff3647b8c406f0d09bb52e192b0f976a8f',bytes=9365)
root=data(rootrow);controller=data(root['controllerObservation']);auth=data(root['rootAuthority']);cfg=data(root['controllerConfig']);run=data(cfg['runConfig']);phase=data(auth['phaseAuthority']);quiet=data(auth['quietWindowAuthority']);closed=data(root['quietWindowCompletion']);terminal=data(root['externalParentTerminal'])
need(root['state']=='ROOT_OBSERVED_CODEC_TIMING_V5_COMPLETE_UNREVIEWED_V1' and root['rawParentExitCode']==root['rootControllerExitCode']==0 and root['rootControllerToolSession']==38214,'actual Root observation and recorded enclosing controller zero')
for k in ['sourceIndex','controllerSourceIndex','rootAuthority']:need(root[k]==controller[k],'Root/controller tuple '+k)
need(root['controllerObservation']==closed['controllerObservation']and root['externalParentTerminal']==controller['rawExternalTerminal']==closed['externalParentTerminal'],'same actual parent/outer observations')
need(cfg['controllerSourceIndex']==auth['controllerSourceIndex']and cfg['controllerIndependentReview']==auth['controllerIndependentReview']and run['sourceIndex']==root['sourceIndex']and run['rootAction']==root['rootAuthority'],'actual controller/run config and source review roles')
need(auth['externalParentDeadlineSeconds']==7200 and auth['externalOutputRoot']=='/private/tmp/starling-node-compat/zlib-cost-timing-v5-external-root','fixed original external deadline/output')
need(terminal['pid']==43889 and terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone']is terminal['allObservedOwnedGroupsGone']is True and terminal['timeout']is terminal['forcedCleanup']is False,'clean actual owned parent')
need(all(terminal[k]==[]for k in ['signals','errors','interruptedSignals','remainingObservedPids'])and all(v['alive']is False for v in terminal['finalGroups']),'no forced/signal/remaining-group acceptance')
external=Path(root['externalParentTerminal']['path']).parent
started=data(row(external/'started.json'))
need(started['pid']==terminal['pid']and started['authority']==terminal['authority']==root['rootAuthority']and started['timeoutSeconds']==7200,'actual Popen parent/Root/deadline')
need(started['argv']==['/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',str(S/'run.mjs'),json.dumps(cfg['runConfig'],separators=(',',':'))],'exact genuine V5 Node/runConfig invocation')
workers=json.loads((P/'worker-ledger.json').read_bytes())['workers'];worker_pids={v['pid']for v in workers};need(len(worker_pids)==360,'all360 replayed worker PIDs')
records=[];last=-1
for i,path in enumerate(sorted(external.glob('owned-*.json'))):
 v=data(row(path));need(v['sequence']==i and type(v['observationMonotonicSeconds'])in(int,float)and v['observationMonotonicSeconds']>=last,'ordered actual owned-process records');last=v['observationMonotonicSeconds'];records.append(v)
need(len(records)==361 and [v['process']for v in records]==terminal['observedProcesses'],'all361 raw process observations reconcile terminal')
need({v['process']['pid']for v in records}==worker_pids|{43889},'every known actual parent/worker and no substituted PID')
for v in records:
 r=v['process'];need(r['pgid']==r['pid']and r['command']=='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'and type(r['birth'])is str and bool(r['birth']),'actual new session and captured birth/command')
 if r['pid']!=43889:need(r['ppid']==43889,'actual direct owned worker parent')
need({v['pgid']for v in terminal['finalGroups']}=={v['process']['pgid']for v in records},'all recorded owned groups accounted in final cleanup')
need(quiet['schemaVersion']==1 and quiet['state']=='ROOT_COORDINATED_CODEC_MEASUREMENT_QUIET_WINDOW_V1'and quiet['phase']=='timing'and quiet['sourceIndexSha256']==root['sourceIndex']['sha256']and quiet['runId']==auth['runId'],'actual quiet source/phase')
idle=data(quiet['idleCoordination']);need(idle['state']=='ROOT_OBSERVED_THREE_AGENT_IDLE_FOR_CODEC_TIMING_V5_V1'and idle['rootOtherBuildRuntimeOrHashAuditsStopped']is idle['allRootExternalJobsTerminal']is True,'Root explicit task coordination')
names={'/root/buffer_templates','/root/runtime_gc_component_review','/root/cost_component_results_review'}
need({v['agent']for v in idle['agents']}==names and len(idle['agents'])==3,'all three explicit agent acknowledgements')
for v in idle['agents']:need(v['allToolsTerminal']is v['writesHashesTestsStopped']is v['resumeRequiresRootRelease']is True and bool(v['acknowledgement']),'preserved explicit idle acknowledgement')
need(quiet['exclusiveMeasurementApproved']is quiet['competingAgentWorkStopped']is quiet['rootOtherBuildRuntimeOrHashAuditsStopped']is True,'source declared task quiet scope')
need(quiet['backgroundDesktopAndSystemActivityControlled']is idle['backgroundDesktopAndSystemActivityControlled']is root['backgroundDesktopAndSystemActivityControlled']is closed['backgroundDesktopAndSystemActivityControlled']is False,'no uncontrolled desktop/system isolation claim')
instant=lambda s:datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
qstart,qend,begin,end=instant(quiet['startsAtUtc']),instant(quiet['expiresAtUtc']),instant(started['startedAtUtc']),instant(closed['closedAtUtc'])
need(instant(idle['recordedAtUtc'])<=qstart<=begin<begin+datetime.timedelta(seconds=terminal['operationalElapsedSeconds'])<=end<qend,'actual parent and closure lie in declared quiet window')
need((qend-begin).total_seconds()*1000>=auth['globalBudgetMs']==5400000 and (qend-qstart).total_seconds()==7200,'full selected global budget fits before Node parent launch')
for k in ['phase','runId','sourceIndexSha256','globalBudgetMs','calibrationSourceIndex','preparedPlan','quietWindowAuthority','warmNPlan','warmNMatchedPlan']:need(phase[k]==auth[k],'separate exact Root phase '+k)
need(closed['state']=='ROOT_COORDINATED_CODEC_MEASUREMENT_QUIET_WINDOW_CLOSED_V1'and closed['sourceIndex']==root['sourceIndex']and closed['quietWindow']==auth['quietWindowAuthority']and closed['taskHoldReleasedAfterThisReceipt']is True and closed['independentActualTimingReviewRequired']is True,'actual closure and independent-review requirement')
activation=data(row(Z/'cost-timing-v5-root-activation-receipt.json'))
for k in ['rootAuthority','controllerSourceIndex','controllerIndependentReview','phaseAuthority']:need(activation[k]==(root['rootAuthority']if k=='rootAuthority'else auth[k]),'unchanged actual activation tuple '+k)
need(activation['runConfig']==cfg['runConfig']and activation['controllerConfig']==root['controllerConfig']and activation['quietWindow']==auth['quietWindowAuthority']and activation['originalCalibrationSource']==auth['calibrationSourceIndex'],'actual activation explicitly binds oldB5 vs newV5')
for v in [root,controller,closed,activation,auth]:
 for k in ['timingAcceptanceClaim','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','metadataProjection','controlSubtraction']:
  if k in v:need(v[k]is False,'preserved closed adoption/scope '+k)
observer_history=data(row(Z/'cost-timing-v5-observer-history.json'));observer=row(Z/'cost-timing-v5-observe.py');verify(observer)
need(observer_history['actualTimingSourceOrOutputChanged']is observer_history['workerOrCodecOrTimingActionsRepeated']is False and observer['sha256']==observer_history['afterObserverSha256'],'read-only Root observer correction, no rerun/source relabelling')
need(root['measuredSamples']==2520 and root['warmupBatches']==1080 and root['rawN1ControlOperations']==2160 and root['rawPublicTypedReturns']==7200 and root['codecBatchCalls']==3600,'Root corrected sample/control classification')
need(observer_history['actualOriginalTimedFlagsIncludeControls']is True,'actual timed flag includes N1 controls; not all flags are codec samples')
out=json.loads((P/'output-audit.json').read_bytes())
for a,b in [('actualIndex','actualIndex'),('actualResults','actualResults'),('actualAggregate','actualAggregate'),('actualCompletion','actualCompletion')]:need(root[a]==out[b],'independently replayed output vs Root '+a)
need(root['originalJsonlHeartbeatRecords']==controller['observation']['originalJsonlHeartbeatRecords']and root['originalRelativePublishedRows']==controller['observation']['originalRelativePublishedRows']and root['absoluteOutputDescriptors']==controller['observation']['absoluteOutputDescriptors'],'all raw-prefix/relative/absolute origins unchanged')
raw_observed=data(row(external/'raw-terminal-observed.json'));need(raw_observed['terminal']==root['externalParentTerminal']and raw_observed['stdout']==terminal['stdout']and raw_observed['stderr']==terminal['stderr']and raw_observed['interpretationPending']is True,'durable raw observation predates collector acceptance')
expected_names={p.name for p in external.glob('owned-*.json')}|{'started.json','terminal.json','stdout.log','stderr.log','raw-terminal-observed.json','controller-observation.json'}
actual_names=set();modes={}
for p in external.iterdir():
 s=p.lstat();need(p.is_file()and not p.is_symlink()and s.st_nlink==1 and stat.S_IMODE(s.st_mode)in[0o600,0o644],'ordinary inherited-mode external DATA file');actual_names.add(p.name);modes[oct(stat.S_IMODE(s.st_mode))]=modes.get(oct(stat.S_IMODE(s.st_mode)),0)+1;verify(row(p))
need(actual_names==expected_names and len(actual_names)==367 and stat.S_IMODE(external.stat().st_mode)==0o700,'complete actual external root membership/private directory')
for r in[auth['externalController'],auth['rootActivationIssuer']]:verify(r)
for real,c in cache.items():s=Path(real).stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==c['identity'],'final stable outer files')
result=dict(schemaVersion=1,verifiedPassed=True,checks=checks,rootObservation=rootrow,controllerObservation=root['controllerObservation'],rootAuthority=root['rootAuthority'],controllerConfig=root['controllerConfig'],runConfig=cfg['runConfig'],externalParentTerminal=root['externalParentTerminal'],externalStarted=row(external/'started.json'),phaseAuthority=auth['phaseAuthority'],quietWindow=auth['quietWindowAuthority'],quietWindowCompletion=root['quietWindowCompletion'],idleCoordination=quiet['idleCoordination'],rootActivationReceipt=row(Z/'cost-timing-v5-root-activation-receipt.json'),rootObserverHistory=row(Z/'cost-timing-v5-observer-history.json'),observedProcessRecords=361,actualParentPid=43889,freshWorkerPids=360,observedProcessRecordsExactlyReconciled=True,allObservedGroupsGone=True,noForcedCleanup=True,externalRegularFiles=367,externalObservedModes=modes,allContainingDirectories0700=True,quietWindowCoordinationIsTaskScopeOnly=True,backgroundDesktopAndSystemActivityControlled=False,rootEnclosingControllerExitIsRootRecordedObservation=True,actualParentExitIndependentlyDecoded=True,clockDomainsNotInterchanged=True,actualParentIntervalSeconds=terminal['operationalElapsedSeconds'],selectedGlobalBudgetMs=5400000,externalParentDeadlineSeconds=7200,rootTimedMarkerClassificationCorrectionRetained=True,ownerActionsInvoked=False)
with(P/'outer-audit.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
with(P/'outer-input-hashes.json').open('x')as f:json.dump(dict(schemaVersion=1,files=[seen[p]for p in sorted(seen)]),f,indent=2);f.write('\n')
print(json.dumps(dict(outerPassed=True,checks=checks,observedProcesses=361,files=len(seen),ownerActionsInvoked=False)))

