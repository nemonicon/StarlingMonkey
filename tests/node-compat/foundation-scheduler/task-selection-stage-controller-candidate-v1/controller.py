"""Dormant owned source-stage controller. No custom import before authorization."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys

def descriptor(row):
 assert type(row)is dict and set(row)=={'path','sha256','bytes'}
 assert type(row['path'])is str and row['path'].startswith('/')and not row['path'].startswith('//')and str(Path(row['path']))==row['path']and '\\'not in row['path']and '\0'not in row['path']and '..'not in row['path'].split('/')
 assert type(row['bytes'])is int and row['bytes']>=0 and type(row['sha256'])is str and len(row['sha256'])==64 and all(c in'0123456789abcdef'for c in row['sha256'])
 return dict(row)

def checked(row):
 row=descriptor(row);p=Path(row['path']);physical=Path('/private'+str(p))if str(p).startswith('/tmp/')else p
 for q in(physical,*physical.parents):assert not q.is_symlink()
 a=physical.stat();assert stat.S_ISREG(a.st_mode);d=hashlib.sha256()
 with physical.open('rb')as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):d.update(chunk)
 b=physical.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns)
 assert a.st_size==row['bytes']and d.hexdigest()==row['sha256'];return p

def read(row):
 assert row['bytes']<=32*1024*1024;raw=checked(row).read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'];return json.loads(raw)

def family(row):
 x=read(row);base=Path(row['path']).parent;rows=[row];names=set()
 assert x['schemaVersion']==1 and 0<len(x['files'])<=2048
 for r in x['files']:
  n=r['path'];assert n and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/'))and n not in names;names.add(n);d=dict(path=str(base/n),sha256=r['sha256'],bytes=r['bytes']);checked(d);rows.append(d)
 assert not any(p.is_symlink()for p in base.rglob('*'))
 assert{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names|{'index.json'};return rows

REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/task-selection-stage-controller-candidate-v1'
INTEGRATION=REPO/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1'
SOURCE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source')
WORK=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-build')
FREEZE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze')
JOURNAL=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-stage.json')
OUT=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-stage-external-root')
INTEGRATION_SHA='88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1'
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'

def merge_targets(plan,own_rows):
 targets={}
 for r in plan['files']:
  name=r['target'];assert name and not name.startswith('/')and '\\'not in name and '\0'not in name and all(p not in('','.','..')for p in name.split('/'))and name not in targets
  targets[name]=descriptor(r['original'])
 assert len(targets)==533
 for r in own_rows:targets[str(INTEGRATION.relative_to(REPO))+'/'+str(Path(r['path']).relative_to(INTEGRATION))]=descriptor(r)
 for change in plan['nativeAfterimageReplacements']:
  r=next(r for r in own_rows if r['path']==str(INTEGRATION/'native'/change['path']));assert r['sha256']==change['afterSha256'];targets[change['path']]=descriptor(r)
 targets['tests/node-compat/build-engine.sh']=next(r for r in own_rows if r['path']==str(INTEGRATION/'proposed/tests/node-compat/build-engine.sh'))
 assert len(targets)==566 and len(plan['nativeAfterimageReplacements'])==3
 return targets

def root_model(root,config,refs):
 assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_SCHEDULER_RESOURCE_TASK_SELECTION342_SOURCE_STAGE_V1'
 assert root['sourceIndexSha256']==INTEGRATION_SHA and root['sourceRoot']==str(SOURCE)and root['workRoot']==str(WORK)and root['freezeRoot']==str(FREEZE)and root['baseline']==BASE
 assert root['stageAllowed']is True and root['nativeSourceFiles']==342 and root['nativeReplacements']==3 and root['expectedCopies']==566
 assert root['sourceIndependentReview']==refs['integrationReview']
 assert root['controllerIndex']==config['controllerIndex']and root['controllerIndex']['path']==str(OWN/'index.json')
 assert root['controllerEntry']['path']==str(OWN/'controller.py')and root['stageEntry']['path']==str(INTEGRATION/'stage.py')
 assert root['monitorIndex']==refs['monitorIndex']and root['monitorEntry']==refs['monitorEntry']
 assert root['externalOutputRoot']==str(OUT)and root['stageJournal']==str(JOURNAL)and root['deadlineSeconds']==600
 assert root['resourceArtifactReview']==refs['resourceArtifactReview']and root['resourceFreezeReceipt']==refs['resourceFreezeReceipt']
 for k in('buildAllowed','freezeAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','gcAllowed','runtimeAcceptanceClaim','sourcePromotionAllowed','operationalAdmission','metadataProjectionAllowed','timingAllowed'):assert root[k]is False
 assert root['actualStage']is None and root['actualStageReview']is None

def controller_peer_model(value,index):
 assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_TASK_SELECTION_STAGE_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
 assert value['controllerSourceIndexSha256']==index['sha256']and value['integrationSourceIndexSha256']==INTEGRATION_SHA
 assert value['sourceOnly']is True and value['sourceReviewPassed']is True
 for k in('ownerActionsInvoked','hostActionsInvoked','stageActionsInvoked'):assert value[k]is False

def indexed_result(pair):
 rows=family(pair['index']);assert pair['result']in rows
 return read(pair['result']),rows

def capture_protection(refs):
 receipt=read(refs['resourceFreezeReceipt']);assert receipt['nativeInputsVerified']==342 and len(receipt['copies'])==666
 rows=[refs['resourceFreezeReceipt']]
 originals=0
 for r in receipt['copies']:
  rows.append({k:r[k]for k in('path','sha256','bytes')})
  assert stat.S_IMODE(Path(r['path']).stat().st_mode)==0o600
  if r['original']is not None:rows.append(descriptor(r['original']));originals+=1
 assert originals==663
 root=Path(refs['resourceFreezeReceipt']['path']).parent
 assert not any(p.is_symlink()for p in root.rglob('*'))
 assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}=={Path(r['path']).relative_to(root).as_posix()for r in receipt['copies']}|{'normal-off-freeze-receipt.json'}
 stage=read(refs['resourceStage']);assert len(stage['copies'])==501
 for r in stage['copies']:rows += [dict(r['original'],path=r['path']),descriptor(r['original'])]
 for r in rows:checked(r)
 return rows

def recheck(frame):
 for r in frame['captured']:checked(r)
 for r in frame['families']:family(r)
 for name,r in frame['targets'].items():assert stat.S_IMODE(checked(r).stat().st_mode)&0o777==frame['modes'][name]
 capture_protection(frame['refs'])

def authorize(config_row):
 config=read(config_row);assert config['schemaVersion']==1 and config['controllerIndex']['path']==str(OWN/'index.json')
 own=family(config['controllerIndex']);refs=read(next(r for r in own if r['path']==str(OWN/'references.json')))
 root=read(config['rootAuthority']);root_model(root,config,refs)
 assert root['controllerEntry']in own and config['sourceIndex']==refs['integrationIndex']and config['sourceIndex']['sha256']==INTEGRATION_SHA
 integration=family(config['sourceIndex']);assert root['stageEntry']in integration
 captured=[config_row,config['rootAuthority'],*own,*integration];families=[config['controllerIndex'],config['sourceIndex']]
 value,rows=indexed_result(refs['integrationReview']);captured+=rows;families.append(refs['integrationReview']['index'])
 assert value['state']=='INDEPENDENT_SCHEDULER_TASK_SELECTION_INTEGRATION_SOURCE_REVIEW_PASSED_V1'and value['sourceIndexSha256']==INTEGRATION_SHA and value['sourceOnly']is True and value['sourceReviewPassed']is True and value['ownerActionsInvoked']is False
 value,rows=indexed_result(root['controllerSourceReview']);controller_peer_model(value,config['controllerIndex']);captured+=rows;families.append(root['controllerSourceReview']['index'])
 value,rows=indexed_result(refs['resourceArtifactReview']);captured+=rows;families.append(refs['resourceArtifactReview']['index'])
 assert value['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_NORMAL_OFF_FROZEN_ARTIFACT_REVIEW_PASSED_V1'and value['verifiedPassed']is True and value['nativeSourceFiles']==342
 monitor=family(refs['monitorIndex']);assert refs['monitorEntry']in monitor;captured+=monitor;families.append(refs['monitorIndex'])
 preparation=read(next(r for r in integration if r['path']==str(INTEGRATION/'input-freeze.json')))
 for r in preparation['files']:checked(r);captured.append(r)
 baseline=read(next(r for r in integration if r['path']==str(INTEGRATION/'baseline-pins.json')))
 for f in baseline['families'].values():captured+=family(f);families.append(f)
 plan=read(next(r for r in integration if r['path']==str(INTEGRATION/'stage-inputs.json')));targets=merge_targets(plan,integration)
 for r in targets.values():checked(r);captured.append(r)
 captured+=capture_protection(refs)
 modes={name:stat.S_IMODE(checked(r).stat().st_mode)&0o777 for name,r in targets.items()}
 frame=dict(config=config,root=root,refs=refs,captured=captured,families=families,targets=targets,modes=modes)
 recheck(frame);return frame

def observe_targets(targets,modes):
 # Partial observations are never interpreted as a successful copy journal.
 records=[]
 for name,r in sorted(targets.items()):
  p=SOURCE/name;value=dict(path=str(p),expected=r,status='missing')
  if any(q.is_symlink()for q in(p,*p.parents)):value['status']='symlink-refused'
  elif p.exists():
   s=p.stat();value.update(bytes=s.st_size,mode=stat.S_IMODE(s.st_mode))
   if not stat.S_ISREG(s.st_mode):value['status']='nonregular-refused'
   elif s.st_size!=r['bytes']:value['status']='size-mismatch'
   else:
    h=hashlib.sha256(p.read_bytes()).hexdigest();original=Path(r['path']).stat()
    value.update(sha256=h,distinctInode=(s.st_dev,s.st_ino)!=(original.st_dev,original.st_ino),expectedMode=modes[name])
    value['status']='match'if h==r['sha256']and value['mode']==value['expectedMode']and value['distinctInode']else'content-mode-or-inode-mismatch'
  records.append(value)
 return records

def terminal_model(t,authority):
 assert t['authority']==authority and t['rawExitCode']==0 and t['allObservedOwnedGroupsGone']is True and t['parentOwnedGroupGone']is True
 assert t['timeout']is t['forcedCleanup']is False
 for k in('remainingObservedPids','signals','errors','interruptedSignals'):assert t[k]==[]
 # Git legitimately writes clone/checkout progress to stderr; retain all bytes.

def main(config_row):
 assert __debug__ and sys.dont_write_bytecode and Path(__file__).resolve().parent==OWN
 for k in('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH'):assert not os.environ.get(k)
 frame=authorize(config_row)
 for p in(SOURCE,WORK,FREEZE,JOURNAL,OUT):assert not p.exists()and not p.is_symlink()
 assert os.statvfs(SOURCE.parent).f_bavail*os.statvfs(SOURCE.parent).f_frsize>=2*1024**3
 spec=importlib.util.spec_from_file_location('genuine_task_selection_stage_monitor',checked(frame['refs']['monitorEntry']));monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
 recheck(frame);OUT.mkdir(mode=0o700)
 result=dict(schemaVersion=1,state='TASK_SELECTION_STAGE_FAILED_OR_PARTIAL_UNACCEPTED_V1',sourceIndex=frame['config']['sourceIndex'],rootAuthority=frame['config']['rootAuthority'],partialObservationOnly=True,stageSuccessful=False,buildExecuted=False,engineExecuted=False,operationalAdmission=False)
 failure=None
 try:
  terminal=monitor.monitor([sys.executable,'-B','-I',str(INTEGRATION/'stage.py'),json.dumps(config_row,separators=(',',':'))],str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OUT,600,frame['config']['rootAuthority'])
  terminal_model(terminal,frame['config']['rootAuthority'])
  for r in(terminal['stdout'],terminal['stderr']):checked(r)
  journal_row=dict(path=str(JOURNAL),sha256=hashlib.sha256(JOURNAL.read_bytes()).hexdigest(),bytes=JOURNAL.stat().st_size);journal=read(journal_row)
  assert journal['state']=='RESOURCE_TASK_SELECTION342_SOURCE_STAGED_UNREVIEWED_V1'and journal['sourceIndex']==frame['config']['sourceIndex']and journal['rootAuthority']==frame['config']['rootAuthority']
  expected=[dict(path=str(SOURCE/k),original=v)for k,v in sorted(frame['targets'].items())]
  assert journal['copies']==expected and len(expected)==566 and journal['nativeFiles']==342 and journal['nativeReplacements']==3 and journal['buildOrGuestInvoked']is False
  last=Path(terminal['stdout']['path']).read_text().splitlines()[-1];assert json.loads(last)==journal
  assert(SOURCE/'.git/HEAD').read_text().strip()==BASE and not(SOURCE/'.git/objects/info/alternates').exists()
  for p in(WORK,FREEZE):assert not p.exists()
  result.update(state='TASK_SELECTION342_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1',stageSuccessful=True,actualJournal=journal_row)
 except BaseException as error:
  failure=error;result['failureType']=type(error).__name__
 finally:
  try:
   result['targetObservations']=observe_targets(frame['targets'],frame['modes'])
   if result['stageSuccessful']:assert all(r['status']=='match'for r in result['targetObservations'])
  except BaseException as error:result['observationFailureType']=type(error).__name__;failure=failure or error;result['stageSuccessful']=False
  try:recheck(frame);result['finalProtectionRecheckPassed']=True
  except BaseException as error:result['finalProtectionRecheckPassed']=False;result['recheckFailureType']=type(error).__name__;failure=failure or error;result['stageSuccessful']=False
  if not result['stageSuccessful']:result['state']='TASK_SELECTION_STAGE_FAILED_OR_PARTIAL_UNACCEPTED_V1'
  with(OUT/'stage-observation.json').open('x')as out:json.dump(result,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
 if failure:raise failure
 print(json.dumps(dict(state=result['state'],stageSuccessful=True,observation=str(OUT/'stage-observation.json'),independentResultReviewRequired=True)),flush=True)

if __name__=='__main__':
 assert len(sys.argv)==2
 main(json.loads(sys.argv[1]))
