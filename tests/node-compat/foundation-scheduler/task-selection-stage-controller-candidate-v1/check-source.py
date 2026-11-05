"""Read/hash, extracted guard models and owned filesystem fixtures only."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,stat,sys
HERE=Path(__file__).resolve().parent
SEED=HERE.parents[1]/'foundation-crypto/independent-ownership-secret-integration-source-review-v1'

def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))

def main():
 assert __debug__ and sys.dont_write_bytecode and not(HERE/'index.json').exists()
 assert row(SEED/'index.json')['sha256']=='8665997e4edab561a0e0e63235104b8e358072995725002704f25e4499dfca45'
 for r in json.loads((SEED/'index.json').read_bytes())['files']:assert row(SEED/r['path'])==dict(r,path=str(SEED/r['path']))
 spec=importlib.util.spec_from_file_location('genuine_source_preparation_reader',SEED/'read-source.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
 refs=json.loads((HERE/'references.json').read_bytes())
 for r in [refs['integrationIndex'],refs['integrationReview']['index'],refs['monitorIndex'],refs['resourceArtifactReview']['index']]:reader.family(r)
 integration=Path(refs['integrationIndex']['path']).parent
 ix=json.loads((integration/'index.json').read_bytes());rows=[refs['integrationIndex'],*[dict(r,path=str(integration/r['path']))for r in ix['files']]]
 for r in json.loads((integration/'input-freeze.json').read_bytes())['files']:reader.regular(r)
 for r in json.loads((integration/'baseline-pins.json').read_bytes())['families'].values():reader.family(r)
 text=(HERE/'controller.py').read_text();tree=ast.parse(text)
 deriv=json.loads((HERE/'data-io-derivation.json').read_bytes());donor=reader.regular(deriv['donor']).read_text()
 actual={n.name:ast.get_source_segment(text,n)for n in tree.body if isinstance(n,ast.FunctionDef)}
 old={n.name:ast.get_source_segment(donor,n)for n in ast.parse(donor).body if isinstance(n,ast.FunctionDef)}
 for r in deriv['functions']:reader.need(r['text']==actual[r['name']]==old[r['name']],'exact genuine inline I/O function')
 constants={}
 for n in tree.body:
  if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
   try:constants[n.targets[0].id]=ast.literal_eval(n.value)
   except ValueError:pass
 repo=HERE.parents[3]
 env=dict(constants,Path=Path,json=json,stat=stat,hashlib=hashlib,REPO=repo,OWN=HERE,INTEGRATION=integration,SOURCE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source'),WORK=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-build'),FREEZE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze'),JOURNAL=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-stage.json'),OUT=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-stage-external-root'))
 names=['descriptor','merge_targets','root_model','controller_peer_model','terminal_model','observe_targets']
 defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names];assert len(defs)==len(names)
 exec(compile(ast.Module(body=defs,type_ignores=[]),'<extracted stage models; no controller activation>','exec'),env)
 plan=json.loads((integration/'stage-inputs.json').read_bytes());targets=env['merge_targets'](plan,rows);reader.need(len(targets)==566,'actual566 data targets')
 for r in targets.values():reader.regular(r)
 modes={name:stat.S_IMODE(Path(r['path']).stat().st_mode)&0o777 for name,r in targets.items()}
 def refuses(fn):
  try:fn()
  except(AssertionError,KeyError,TypeError,StopIteration,ValueError):reader.need(True,'invalid pure model refused')
  else:reader.need(False,'invalid pure model accepted')
 for mutation in ['missing','escape','duplicate','wrongafter']:
  p=copy.deepcopy(plan)
  if mutation=='missing':p['files'].pop()
  if mutation=='escape':p['files'][0]['target']='../escape'
  if mutation=='duplicate':p['files'][1]['target']=p['files'][0]['target']
  if mutation=='wrongafter':p['nativeAfterimageReplacements'][0]['afterSha256']='0'*64
  refuses(lambda p=p:env['merge_targets'](p,rows))
 root=json.loads((HERE/'root-authority.template.json').read_bytes());own=dict(path=str(HERE/'index.json'),sha256='a'*64,bytes=1);config=dict(controllerIndex=own)
 refuses(lambda:env['root_model'](root,config,refs))
 issued=copy.deepcopy(root);issued.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE_TASK_SELECTION342_SOURCE_STAGE_V1',stageAllowed=True,controllerIndex=own,controllerEntry={'path':str(HERE/'controller.py')},stageEntry={'path':str(integration/'stage.py')})
 env['root_model'](issued,config,refs);reader.need(True,'pure future Root shape only')
 for k in ['buildAllowed','freezeAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','gcAllowed','runtimeAcceptanceClaim','sourcePromotionAllowed','operationalAdmission','metadataProjectionAllowed','timingAllowed']:
  bad=dict(issued,**{k:True});refuses(lambda:env['root_model'](bad,config,refs))
 terminal=dict(authority={'syntheticOnly':True},rawExitCode=0,allObservedOwnedGroupsGone=True,parentOwnedGroupGone=True,timeout=False,forcedCleanup=False,remainingObservedPids=[],signals=[],errors=[],interruptedSignals=[],stderr={'bytes':97})
 env['terminal_model'](terminal,terminal['authority']);reader.need(True,'legitimate Git stderr allowed and retained')
 for k,v in [('rawExitCode',1),('timeout',True),('forcedCleanup',True),('signals',['SIGTERM']),('remainingObservedPids',[123]),('allObservedOwnedGroupsGone',False)]:
  bad=dict(terminal,**{k:v});refuses(lambda:env['terminal_model'](bad,terminal['authority']))
 # Exact extracted observer in owned scratch data, never the real controller context.
 scratch=Path('/private/tmp/starling-node-compat/task-selection-stage-controller-model-v1');scratch.mkdir();source=scratch/'source';source.mkdir();original=scratch/'original';original.write_bytes(b'data');original.chmod(0o640)
 env['SOURCE']=source;model={'target':row(original)};expected={'target':0o640};target=source/'target'
 def observe(status):reader.need(env['observe_targets'](model,expected)[0]['status']==status,'partial observer '+status)
 observe('missing');target.write_bytes(b'data');target.chmod(0o640);observe('match')
 target.write_bytes(b'dat');observe('size-mismatch');target.write_bytes(b'xxxx');observe('content-mode-or-inode-mismatch')
 target.write_bytes(b'data');target.chmod(0o600);observe('content-mode-or-inode-mismatch');target.unlink();target.symlink_to(original);observe('symlink-refused');target.unlink()
 os.link(original,target);observe('content-mode-or-inode-mismatch');target.unlink();target.mkdir();observe('nonregular-refused');target.rmdir()
 receipt=reader.load(refs['resourceFreezeReceipt']);reader.need(len(receipt['copies'])==666,'actual frozen666')
 originals=0
 for r in receipt['copies']:
  reader.regular({k:r[k]for k in ['path','sha256','bytes']});reader.need(stat.S_IMODE(Path(r['path']).stat().st_mode)==0o600,'private frozen mode')
  if r['original']is not None:reader.regular(r['original']);originals+=1
 reader.need(originals==663,'actual original663; three generated rows have no original')
 stage=reader.load(refs['resourceStage']);reader.need(len(stage['copies'])==501,'protected configured501')
 for r in stage['copies']:reader.regular(dict(r['original'],path=r['path']));reader.regular(r['original'])
 for p in HERE.glob('*.py'):ast.parse(p.read_bytes(),filename=str(p));reader.need(True,'Python grammar')
 reader.need(text.index('frame=authorize(config_row)')<text.index("spec=importlib.util.spec_from_file_location('genuine_task_selection_stage_monitor'"),'full auth before only custom import')
 reader.need('targetObservations' in text and "with(OUT/'stage-observation.json').open('x')"in text and 'finalProtectionRecheckPassed'in text,'partial/failure observations durably retained')
 for p in ['scheduler-resource-selection-v1-source','scheduler-resource-selection-v1-build','scheduler-resource-selection-v1-freeze','scheduler-resource-selection-v1-stage-external-root']:reader.need(not(Path('/private/tmp/starling-node-compat')/p).exists(),'real phase remains absent')
 result=dict(schemaVersion=1,state='UNAPPLIED_TASK_SELECTION_STAGE_CONTROLLER_SOURCE_CHECKS_PASSED_V1',sourceOnly=True,checks=reader.checks,uniqueReadHashInputs=len(reader.checked),stageTargets=566,protectedFrozenFiles=666,protectedOriginals=663,protectedConfiguredCopies=501,partialFilesystemModelCases=8,ownerActionsInvoked=False,monitorOrStageInvoked=False,gitOrCompilerOrNodeInvoked=False,engineOrGuestInvoked=False,operationalAdmission=False)
 (HERE/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n')
 (HERE/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=[{k:v for k,v in r.items()if k!='identity'}for r in reader.checked.values()]),indent=2)+'\n')
 print(json.dumps(dict(checks=reader.checks,inputs=len(reader.checked),stageTargets=566,partialModelCases=8)))

if __name__=='__main__':main()
