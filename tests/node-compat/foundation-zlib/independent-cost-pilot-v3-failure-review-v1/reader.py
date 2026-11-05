"""Finite failed-pilot read/hash/source audit. No helper, worker, guest or process action."""
from pathlib import Path
import hashlib,json,stat

HERE=Path(__file__).resolve().parent;Z=HERE.parent
CHECKPOINT=Z/'cost-pilot-v3-failure-root-checkpoint-v1'
OUT=Path('/private/tmp/starling-node-compat/zlib-cost-pilot-v3')
EXTERNAL=Path('/private/tmp/starling-node-compat/zlib-cost-pilot-v3-external-root')
rows={};checks=0
def need(v,label):
 global checks
 checks+=1
 if not v:raise AssertionError(label)
def row(p):
 p=Path(p);s=p.lstat();need(stat.S_ISREG(s.st_mode),'regular leaf')
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 z=p.lstat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable read')
 return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
def verify(d,base=None):
 p=Path(d['path'])
 if not p.is_absolute():need(base is not None and '..'not in p.parts,'declared relative context');p=base/p
 v=rows.get(str(p))
 if v is None:v=row(p);rows[str(p)]=v
 need((v['sha256'],v['bytes'])==(d['sha256'],d['bytes']),'exact hash/bytes '+str(p));return p
def load(p):
 p=Path(p);d=row(p);rows[str(p)]=d;return json.loads(p.read_text())
def family(d):
 p=verify(d);v=load(p);names=[r['path']for r in v['files']];need(len(names)==len(set(names)),'unique family members')
 for r in v['files']:verify(r,p.parent)
 need({q.relative_to(p.parent).as_posix()for q in p.parent.rglob('*')if q.is_file()}==set(names)|{'index.json'},'exact indexed family membership')
 return v
ix=load(CHECKPOINT/'index.json');family(row(CHECKPOINT/'index.json'))
root=load(CHECKPOINT/'root-results.json');need(row(CHECKPOINT/'root-results.json')['sha256']=='e7e6e2d2f3dde3396fc00116f2e61722b6a858ed1a95595293aa7f142884bbcc','actual Root checkpoint record')
need(len(root['copies'])==12 and len(ix['files'])==14,'twelve evidence copies/fourteen indexed checkpoint members')
copy_names=[];originals=[]
for d in root['copies']:
 original=verify(d['original']);copy=verify(d['copy'],CHECKPOINT)
 need(original.read_bytes()==copy.read_bytes(),'byte-exact original/copy')
 need((original.stat().st_dev,original.stat().st_ino)!=(copy.stat().st_dev,copy.stat().st_ino),'distinct copy inodes')
 copy_names.append(d['copy']['path']);originals.append(str(original))
need(set(copy_names)=={r['path']for r in ix['files']}-{'README.md','root-results.json'},'all checkpoint evidence covered once')
need({str(p)for p in OUT.rglob('*')if p.is_file()}=={p for p in originals if str(OUT)+'/'in p},'exact six original partial-output files')
need({str(p)for p in EXTERNAL.rglob('*')if p.is_file()}=={p for p in originals if str(EXTERNAL)+'/'in p},'exact six external files')
need(all(not p.is_symlink()for base in [CHECKPOINT,OUT,EXTERNAL]for p in base.rglob('*')),'no evidence symlinks')
failure=load(OUT/'failure.json');need(failure['completedOrigins']==[]and failure['postFailureSourceAuditPassed']is True,'no completed origins/retained post-failure audit report')
need(not any((OUT/name).exists()for name in ['results.json','index.json','completion.json','matched-n-plan.json','calibration']),'no successful phase/calibration artifacts')
need((OUT/'jobs').is_dir()and list((OUT/'jobs').iterdir())==[],'empty jobs directory/no durable worker output')
terminal=load(EXTERNAL/'terminal.json');started=load(EXTERNAL/'started.json')
need(terminal['pid']==started['pid']==root['parentPid']==35821,'actual parent identity')
need(terminal['rawExitCode']==root['rawExitCode']==1 and terminal['timeout']is False and terminal['forcedCleanup']is False,'actual failed parent without timeout/forced cleanup')
need(terminal['allObservedOwnedGroupsGone']is True and terminal['parentOwnedGroupGone']is True,'saved owned lifetimes gone')
need(terminal['signals']==terminal['errors']==terminal['interruptedSignals']==terminal['remainingObservedPids']==[],'no recorded signals/errors/current PIDs')
need({r['pgid']for r in terminal['finalGroups']}=={35821,37184}and all(r['alive']is False for r in terminal['finalGroups']),'two actual final groups gone')
for d in [terminal['stdout'],terminal['stderr'],terminal['authority']]:verify(d)
need(verify(terminal['stdout']).read_bytes()==b'','empty parent stdout')
stderr=verify(terminal['stderr']).read_text();need('actual clean owned child, no failure/partial adoption'in stderr and 'run-body.mjs:43:'in stderr,'actual parent rejection stack')
owned=[load(EXTERNAL/f'owned-{i:04d}.json')for i in range(2)]
need([v['process']['pid']for v in owned]==[35821,37184],'two retained observed process origins')
job='pilot-provider-c0-n1-native-on';launch=load(OUT/'processes'/f'{job}.launch.json');child=load(OUT/'processes'/f'{job}.terminal.json')
need(child['pid']==37184 and child['status']==1 and child['signal']is None and child['spawnError']is None,'actual first child exit1')
need(child['timedOut']is False and child['externalSignal']is None and child['signalCount']==0 and child['signals']==child['errors']==[]and child['ownedGroupGone']is True,'no child timeout/signal/error and group gone')
for key in ['stdout','stderr']:need(verify(child[key]).read_bytes()==b'','complete empty child '+key)
need(child['args']==launch['args']and child['executable']==launch['executable'],'actual raw launcher argv')
need(child['timeoutMs']==600000 and child['maxOutputBytes']==1048576 and child['publicCallTimeoutMs']==600000,'original bounded child limits')
need(child['exactEnvironment']==launch['exactEnvironment']and child['cwd']==launch['cwd'],'retained exact child env/cwd')
input_row=json.loads(child['args'][1]);descriptor=load(verify(input_row))
need(descriptor['jobId']==job and descriptor['n']==1 and descriptor['expected']['caseId']==0 and descriptor['expected']['arm']=='native-on','exact first native/case0/N1 descriptor')
need(descriptor['phase']=='pilot-candidate'and descriptor['comparison']=='same-engine-provider'and descriptor['side']=='A'and descriptor['samples']==1 and descriptor['warmups']==3,'original first pilot unit')
need(descriptor['sourceIndex']==root['sourceIndex'],'exact actual v3 source tuple')
source=family(root['sourceIndex']);source_root=Path(root['sourceIndex']['path']).parent
for name,sha,size in [('cost-pilot-timing-candidate-v1','55db1fc3895a0dbd10ca07e08c59bd68da8edeb9793632c8e05cb41704c5135b',15141),('cost-pilot-timing-candidate-v2','1a294044a4f2414d35fdd817dae95598c2e079aa64a9044737f4791aefe630a2',4460)]:family(dict(path=str(Z/name/'index.json'),sha256=sha,bytes=size))
dependencies=load(source_root/'runtime-dependencies.json')
for d in dependencies['files']:verify(d)
authority=load(verify(root['rootAuthority']));quiet=load(verify(root['quietWindowAuthority']));phase=load(verify(descriptor['phaseAuthority']));plan=load(verify(descriptor['preparedPlan']))
family(authority['sourceIndependentReview']['index']);verify(authority['sourceIndependentReview']['result'])
need(authority['sourceIndexSha256']==descriptor['sourceIndexSha256']==plan['sourceIndexSha256'],'actual source/plan/Root identity')
need(terminal['authority']==root['rootAuthority']==descriptor['rootAuthority'],'actual Root descriptor through child')
need(authority['phase']=='pilot-candidate'and authority['warmNPlan']is None and authority['warmNMatchedPlan']is None,'no warm-N authority')
need(quiet['runId']==phase['runId']==authority['runId']==root['runId'],'separate actual window/run tuple')
need(root['quietWindowClosed']is True and root['matchedPlanProduced']is False,'actual failed phase/window closure observation')
config_row=json.loads(started['argv'][2]);config=load(verify(config_row));need(config['rootAction']==root['rootAuthority']and config['sourceIndex']==root['sourceIndex'],'actual original parent config')
worker=source_root/'worker.mjs';body=source_root/'worker-body.mjs';run=source_root/'run-body.mjs'
worker_text=worker.read_text();body_text=body.read_text();run_text=run.read_text()
need('.catch(()=>{process.exitCode=1;});'in worker_text,'source explicitly discards worker bootstrap rejection')
need(body_text.index('workerDescriptorModel(v);')<body_text.index('DurableOutput.create(v.outputRoot)')<body_text.index("await output.write('started.json'")<body_text.index('session=await loadTimingSession(v.artifact)'), 'pre-output guards→job record→loader order')
need("origins.push("in run_text and run_text.index('actual clean owned child, no failure/partial adoption')<run_text.index('origins.push('),'first nonzero child rejected before origin adoption')
findings=dict(diagnosticGap=dict(file=row(worker),line=worker_text[:worker_text.index('.catch(()=>{process.exitCode=1;});')].count('\n')+1,
    finding='CLI catch discards the original rejection; status1 and empty streams do not identify the failing gate/module. No worker-owned failure writer exists before successful job-output creation.'),
    preOutputBoundary=dict(file=row(body),guardStartLine=body_text[:body_text.index('const inputRow=')].count('\n')+1,
    jobOutputCreationLine=body_text[:body_text.index('DurableOutput.create(v.outputRoot)')].count('\n')+1,
    loaderLine=body_text[:body_text.index('session=await loadTimingSession(v.artifact)')].count('\n')+1,
    finding='Absence of a job record localizes evidence to pre-durable-worker state. It does not retain a precise startup exception or prove a codec call occurred.'),
    exactStartupCauseProved=False,codecExecutionObserved=False,noPerformanceOrAcceptanceConclusion=True)
report=dict(schemaVersion=1,state='INDEPENDENT_CODEC_PILOT_V3_FAILED_EVIDENCE_VERIFIED_NO_RESULT_ACCEPTANCE_V1',checks=checks,
    copiedEvidenceFiles=12,checkpointIndexedFiles=14,checkpointActualFiles=15,originalPartialFiles=6,originalExternalFiles=6,
    parentRawExitCode=1,workerRawExitCode=1,workerPid=37184,parentPid=35821,workerStdoutBytes=0,workerStderrBytes=0,
    completedOrigins=0,matchedPlanProduced=False,observedProcesses=2,allObservedGroupsGone=True,noTimeoutSignalsForcedCleanup=True,
    sourceFamiliesVerified=3,runtimeDependencyFiles=len(dependencies['files']),distinctHashedFiles=len(rows),
    sourceFindings=findings,ownerHelpersWorkersGeneratedImportsGuestCryptoCodecRuntimeOrProcessControlActionsInvoked=False)
with(HERE/'data-audit.json').open('x')as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(dict(audit=row(HERE/'data-audit.json'),checks=checks,files=len(rows),startupCauseProved=False,actionsInvoked=False)))
