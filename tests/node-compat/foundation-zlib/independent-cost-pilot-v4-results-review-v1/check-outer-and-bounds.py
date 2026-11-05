"""Completed outer-run provenance and protocol-bound DATA; no process queries/actions."""
from pathlib import Path
import datetime,hashlib,json,stat
P=Path(__file__).resolve().parent;Z=P.parent;S=Z/'cost-pilot-timing-candidate-v4';seen={};checks=0
def need(v,n):
 global checks
 assert v,n;checks+=1
def row(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def verify(r):need(row(r['path'])=={k:r[k]for k in('path','sha256','bytes')},'whole exact outer/source descriptor');seen[r['path']]={k:r[k]for k in('path','sha256','bytes')};return Path(r['path'])
def data(r):return json.loads(verify(r).read_bytes())
def utc(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def family(r):
 x=data(r);base=Path(r['path']).parent;names=set()
 for v in x['files']:
  n=v['path'];need(n not in names and not n.startswith('/')and all(t not in('','.','..')for t in n.split('/')),'local unique monitor family');names.add(n);verify(dict(v,path=str(base/n)))
 need(not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names|{'index.json'},'whole monitor source family membership')
root=data(dict(path=str(Z/'cost-pilot-v4-root-results.json'),sha256='3f7c0b443490692e4b4a04d22ee6c83a1a84bc72d091703fa29f18cb77002e42',bytes=4270));auth=data(root['rootAuthority']);cfg=data(root['rootConfig']);term=data(root['externalTerminal']);quiet=data(auth['quietWindowAuthority']);phase=data(auth['phaseAuthority']);closed=data(root['windowCompletion']);verify(auth['externalController']);verify(root['reader'])
monitor=Z.parent/'foundation-crypto/ownership-gc-build-controller-candidate-v1/index.json';mr=row(monitor);need(mr['sha256']=='0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b','actual literal original monitor family');family(mr)
controller=Path(auth['externalController']['path']).read_text();need(controller.index('family(monitor_index)')<controller.index('spec.loader.exec_module(monitor)')and"argv = [node['path'], str(SOURCE / 'run.mjs'), json.dumps(config_row, separators=(',', ':'))]"in controller,'actual controller authenticates monitor before genuine invoke, exact explicit argv')
base=Path(root['externalTerminal']['path']).parent;observations=[];names=set()
for p in sorted(base.iterdir()):
 need(p.is_file()and not p.is_symlink()and p.stat().st_nlink==1,'ordinary independent external evidence');verify(row(p));names.add(p.name)
 if p.name.startswith('owned-'):
  v=json.loads(p.read_bytes());need(v['sequence']==len(observations),'consecutive ownership record sequence');observations.append(v)
need(names=={'started.json','stdout.log','stderr.log','terminal.json'}|{f'owned-{i:04d}.json'for i in range(len(observations))},'complete external evidence membership')
need([v['process']for v in observations]==term['observedProcesses']and{v['process']['pgid']for v in observations}<={v['pgid']for v in term['finalGroups']}and all(v['alive']is False for v in term['finalGroups']),'all external observed PID/group identities retained and finally gone')
started=json.loads((base/'started.json').read_bytes());need(started['pid']==term['pid']==80579 and started['timeoutSeconds']==auth['externalParentDeadlineSeconds']==7200 and started['authority']==root['rootAuthority'],'actual outer launch/terminal identity and bound')
need(started['argv']==['/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',str(S/'run.mjs'),json.dumps(root['rootConfig'],separators=(',',':'))],'actual direct existing run CLI/source/config descriptor')
need(phase['sourceIndexSha256']==quiet['sourceIndexSha256']==auth['sourceIndexSha256']and phase['runId']==quiet['runId']==auth['runId']and phase['preparedPlan']==auth['preparedPlan'],'whole original phase/window/source/plan binding')
begin=utc(quiet['startsAtUtc']);end=utc(quiet['expiresAtUtc']);start=utc(started['startedAtUtc']);finish=start+datetime.timedelta(seconds=term['operationalElapsedSeconds'])
need(begin<=start<finish<=end and end-begin==datetime.timedelta(hours=2)and quiet['selectedGlobalBudgetMs']==auth['globalBudgetMs']==5400000,'actual outer interval within original2h window;90m phase budget')
need(quiet['competingAgentWorkStopped']is quiet['rootOtherBuildRuntimeOrHashAuditsStopped']is True and quiet['backgroundDesktopAndSystemActivityControlled']is False,'coordinated work hold, no operating-system exclusivity claim')
need(closed['rootSession']==root['rootSession']==2880 and closed['observedParentPid']==80579 and closed['externalTerminal']==root['externalTerminal']and closed['rootAuthority']==root['rootAuthority']and utc(closed['observedClosedAtUtc'])>=finish and closed['measurementHoldReleased']is True and closed['timingAuthorized']is False,'actual independent closure after completed run, no timing authority')
# Exact file roles are derived from immutable source, not chosen to fit observed count.
sources={}
for n in['planner.mjs','result-collector.mjs','worker.template.mjs']:
 p=Z/'cost-pilot-timing-candidate-v1'/n;sources[n]=row(p);verify(sources[n])
guard=row(S/'parent-guard.template.mjs');verify(guard);g=Path(guard['path']).read_text();need('index.files.length<=16384'in g,'preserved original finite count blocker')
run=(S/'run-body.mjs').read_text();worker=(S/'worker-body.mjs').read_text();template=Path(sources['worker.template.mjs']['path']).read_text()
need("await write('descriptors/'+jobId+'.json'"in run and"prefix=join(output,'processes',name)"in(Z/'cost-pilot-timing-candidate-v1/owned-lifecycle.mjs').read_text(),'one descriptor and four named raw process files per worker')
need("await write(prefix+'-before.json'"in template and"await write(prefix+'-raw.json'"in template and"await output.write('started.json'"in worker and"await output.write('index.json'"in worker and"await output.write('completion.json'"in worker,'two raw files per public call plus four worker administrative files')
need("await write('calibration/'"in run and"await write('matched-n-plan.json'"in run and"await write('results.json'"in run and"await write('aggregate-observations.json'"in run,'exact parent pilot/timing extra file roles')
pilot_calls=2+3+3+1+3+2;timing_calls=2+3+3+7+3+2;pilot_per=1+4+(1+2*pilot_calls+1+2);timing_per=1+4+(1+2*timing_calls+1+2)
max_pairs=2*(18*16+12*8);max_workers=2*max_pairs;pilot_max=max_workers*pilot_per+60+2;timing_workers=2*30*3*2;timing_max=timing_workers*timing_per+2
need((pilot_calls,timing_calls,pilot_per,timing_per,max_pairs,max_workers,pilot_max,timing_workers,timing_max)==(14,20,37,49,768,1536,56894,360,17642),'protocol-derived exact finite maximum counts')
need(892*pilot_per+62==33066 and 33066>16384 and timing_max>16384,'actual pilot and complete future timing exceed preserved original bound')
need("warm.data.sourceIndexSha256===options.sourceIndex.sha256"in run,'preserved old pilot/new timing source identity equality also requires successor')
model_bound=dict(schemaVersion=1,sourceIndexSha256=auth['sourceIndexSha256'],sourceDescriptors=sources,parentGuard=guard,pilotPublicCallsPerWorker=14,timingPublicCallsPerWorker=20,rawBeforeAndReturnFilesPerCall=2,descriptorFilesPerWorker=1,rawProcessFilesPerWorker=4,workerAdministrativeFiles=4,pilotFilesPerWorker=37,timingFilesPerWorker=49,pilotParentExtraFiles=62,timingParentExtraFiles=2,smallCases=18,smallGeometricCandidates=16,largeCases=12,largeGeometricCandidates=8,comparisons=2,pilotMaximumPairs=768,pilotMaximumWorkers=1536,pilotMaximumIndexedFiles=56894,actualPilotWorkers=892,actualPilotIndexedFiles=33066,timingWorkers=360,timingMaximumIndexedFiles=17642,preservedOldConsumerIndexBound=16384,blocksUnchangedB5TimingConsumer=True,requiresDistinctOriginalPilotAndNewTimingSourceRoles=True,actualPilotSourceMustRemainUnchanged=True,noActualIndexOmissionOrProjectionAllowed=True,actualTimingOrReadOnlyPlanAuthorityGranted=False)
with(P/'timing-consumer-boundaries.json').open('x')as f:json.dump(model_bound,f,indent=2);f.write('\n')
with(P/'outer-audit.json').open('x')as f:json.dump(dict(schemaVersion=1,verifiedPassed=True,checks=checks,externalFiles=len(names),retainedProcessObservations=len(observations),wholeOriginalInvocation=True,originalWindowRespected=True,coordinatedWorkHoldOnly=True,noDesktopSystemIsolationClaim=True,allObservedGroupsTerminallyGone=True,boundaries=model_bound,ownerProcessHelperOrNodeActionsInvoked=False),f,indent=2);f.write('\n')
with(P/'outer-input-hashes.json').open('x')as f:json.dump(dict(schemaVersion=1,files=[seen[p]for p in sorted(seen)]),f,indent=2);f.write('\n')
print(json.dumps(dict(outerAuditPassed=True,checks=checks,outerFiles=len(names),observations=len(observations),maxPilotFiles=pilot_max,maxTimingFiles=timing_max,ownerActionsInvoked=False)))
