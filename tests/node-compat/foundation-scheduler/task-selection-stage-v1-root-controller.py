"""Root source-stage action only, using genuine reviewed959b/88af entries."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
S=REPO/'tests/node-compat/foundation-scheduler'
SOURCE=S/'task-selection-stage-controller-candidate-v1'
PEER=S/'independent-task-selection-stage-controller-source-review-v1'
INTEGRATION=S/'task-selection-integration-candidate-v1'
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
OUT=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-stage-parent-external-root')

def row(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)

def family(p,expected):
 ix=row(p);assert ix['sha256']==expected;root=Path(p).parent;names=set()
 for r in json.loads(Path(p).read_bytes())['files']:
  n=r['path'];assert n not in names and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/'));names.add(n);assert row(root/n)==dict(r,path=str(root/n))
 assert not any(p.is_symlink()for p in root.rglob('*'))
 assert{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{'index.json'}
 return ix

def write(name,v):
 p=S/name
 with p.open('x')as f:f.write(json.dumps(v,indent=2)+'\n')
 return row(p)

def main():
 assert __debug__ and sys.dont_write_bytecode
 own=family(SOURCE/'index.json','959b3e73111f9f2286d026efc70ef671b2f037321ae159e1cb10f281ab3bfb46')
 peer=dict(index=family(PEER/'index.json','8c288dc166aced0a44b27255dec298faa8bedef0efe640ab8ae2dda897ea20dc'),result=row(PEER/'results.json'))
 passed=json.loads((PEER/'results.json').read_bytes());assert passed['controllerSourceIndexSha256']==own['sha256']and passed['sourceReviewPassed']is True
 family(MONITOR/'index.json','0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
 root=json.loads((SOURCE/'root-authority.template.json').read_bytes())
 root.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE_TASK_SELECTION342_SOURCE_STAGE_V1',stageAllowed=True,controllerIndex=own,controllerEntry=row(SOURCE/'controller.py'),stageEntry=row(INTEGRATION/'stage.py'),controllerSourceReview=peer,rootCaller=row(Path(__file__).resolve()),rootCallerOutputRoot=str(OUT),rootCallerDeadlineSeconds=900)
 root_row=write('task-selection-stage-v1-root-authority.json',root)
 cfg=json.loads((SOURCE/'config.template.json').read_bytes());cfg.update(controllerIndex=own,rootAuthority=root_row)
 cfg_row=write('task-selection-stage-v1-root-config.json',cfg)
 assert not OUT.exists()
 spec=importlib.util.spec_from_file_location('genuine_task_selection_root_owned_monitor',MONITOR/'monitor.py');monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
 env={k:v for k,v in os.environ.items()if k not in('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH')};env['PYTHONDONTWRITEBYTECODE']='1'
 OUT.mkdir(mode=0o700)
 terminal=monitor.monitor([sys.executable,'-B','-I',str(SOURCE/'controller.py'),json.dumps(cfg_row,separators=(',',':'))],str(REPO),env,OUT,900,root_row)
 assert terminal['rawExitCode']==0 and terminal['allObservedOwnedGroupsGone']is True
 assert terminal['timeout']is terminal['forcedCleanup']is False
 assert terminal['signals']==terminal['errors']==terminal['interruptedSignals']==terminal['remainingObservedPids']==[]
 assert terminal['stderr']['bytes']==0
 for r in(terminal['stdout'],terminal['stderr']):assert row(r['path'])==r
 records=[json.loads(line)for line in Path(terminal['stdout']['path']).read_text().splitlines()]
 assert len(records)==2 and set(records[0])=={'pid','timeoutSeconds'}
 result=records[-1];assert result['state']=='TASK_SELECTION342_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1'and result['stageSuccessful']is True
 observation=row(result['observation']);data=json.loads(Path(observation['path']).read_bytes())
 assert data['stageSuccessful']is True and data['finalProtectionRecheckPassed']is True
 assert len(data['targetObservations'])==566 and all(r['status']=='match'for r in data['targetObservations'])
 assert data['rootAuthority']==root_row
 for r in(root_row,cfg_row):assert row(r['path'])==r
 report=dict(schemaVersion=1,state='ROOT_OBSERVED_TASK_SELECTION342_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1',sourceIndex=cfg['sourceIndex'],controllerSourceIndex=own,controllerSourceReview=peer,rootAuthority=root_row,config=cfg_row,outerTerminal=row(OUT/'terminal.json'),stageObservation=observation,actualJournal=data['actualJournal'],rawControllerExitCode=0,allObservedOwnedGroupsGone=True,copies=566,nativeSourceFiles=342,nativeReplacements=3,operationalElapsedSeconds=terminal['operationalElapsedSeconds'],independentStageReviewRequired=True,buildExecuted=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
 report_row=write('task-selection-stage-v1-root-results.json',report)
 print(json.dumps(dict(result=report_row,copies=566,rawControllerExitCode=0)),flush=True)

if __name__=='__main__':main()
