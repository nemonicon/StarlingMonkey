"""Independent read/hash/AST/pure review. Never imports owner/controller/monitor."""
from pathlib import Path
import ast
import collections
import copy
import hashlib
import json
import stat

OWN=Path(__file__).resolve().parent
REPO=OWN.parents[3]
SOURCE=OWN.parent/'task-selection-stage-controller-candidate-v1'
EXPECTED='959b3e73111f9f2286d026efc70ef671b2f037321ae159e1cb10f281ab3bfb46'
checks=0;read_rows={}
def check(value):
 global checks
 assert value
 checks+=1
def descriptor(path):
 p=Path(path);check(p.is_absolute())
 physical=Path('/private'+str(p))if str(p).startswith('/tmp/')else p
 for parent in(physical,*physical.parents):check(not parent.is_symlink())
 a=physical.stat();check(stat.S_ISREG(a.st_mode));h=hashlib.sha256();n=0
 with physical.open('rb')as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk);n+=len(chunk)
 b=physical.stat();check((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns))
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def checked(row):
 check(descriptor(row['path'])==row);check(read_rows.setdefault(row['path'],row)==row);return Path(row['path'])
def load(row):return json.loads(checked(row).read_bytes())
def family(row):
 index=load(row);root=Path(row['path']).parent;names={'index.json'};rows=[row]
 for f in index['files']:
  check(f['path']not in names and f['path']and not f['path'].startswith('/')and all(p not in('','.','..')for p in f['path'].split('/')));names.add(f['path'])
  d=dict(f,path=str(root/f['path']));checked(d);rows.append(d)
 check(not any(p.is_symlink()for p in root.rglob('*')))
 check({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names);return rows
source_index=descriptor(SOURCE/'index.json');check(source_index['sha256']==EXPECTED);source_rows=family(source_index)
refs=load(next(r for r in source_rows if r['path']==str(SOURCE/'references.json')))
declared=load(next(r for r in source_rows if r['path']==str(SOURCE/'input-hashes.json')))
check(len(declared['files'])==1933 and len({r['path']for r in declared['files']})==1933)
for r in declared['files']:checked(r)
for r in(refs['integrationIndex'],refs['integrationReview']['index'],refs['monitorIndex'],refs['resourceArtifactReview']['index']):family(r)
check(refs['integrationIndex']['sha256']=='88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1')
integration=Path(refs['integrationIndex']['path']).parent
integration_rows=family(refs['integrationIndex'])
before=load(next(r for r in integration_rows if r['path']==str(integration/'input-freeze.json')))
for r in before['files']:checked(r)
baseline=load(next(r for r in integration_rows if r['path']==str(integration/'baseline-pins.json')))
for ix in baseline['families'].values():family(ix)

text=(SOURCE/'controller.py').read_text();tree=ast.parse(text)
nodes={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
funcs={k:ast.get_source_segment(text,n)for k,n in nodes.items()}
derivation=load(next(r for r in source_rows if r['path']==str(SOURCE/'data-io-derivation.json')))
donor=checked(derivation['donor']).read_text();old={n.name:ast.get_source_segment(donor,n)for n in ast.parse(donor).body if isinstance(n,ast.FunctionDef)}
for row in derivation['functions']:
 check(funcs[row['name']]==old[row['name']]==row['text']);check(hashlib.sha256(row['text'].encode()).hexdigest()==row['sha256'])

# These are extracted pure functions only, not authorize/recheck/main, not an
# import of the controller, and not a new stage/monitor/owned-filesystem action.
scope={'Path':Path,'REPO':REPO,'OWN':SOURCE,'INTEGRATION':integration}
for node in tree.body:
 if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
  try:scope[node.targets[0].id]=ast.literal_eval(node.value)
  except(ValueError,TypeError):
   if isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Name)and node.value.func.id=='Path'and len(node.value.args)==1 and isinstance(node.value.args[0],ast.Constant):scope[node.targets[0].id]=Path(node.value.args[0].value)
names=['descriptor','merge_targets','root_model','controller_peer_model','terminal_model']
exec(compile(ast.Module(body=[nodes[n]for n in names],type_ignores=[]),'<independent-extracted-pure-models>','exec'),scope)
negatives=0
def rejects(fn):
 global negatives
 try:fn()
 except(AssertionError,KeyError,TypeError,ValueError,StopIteration):checks_before=True
 else:raise AssertionError('Invalid pure shape accepted')
 negatives+=1;check(checks_before)
plan=json.loads((integration/'stage-inputs.json').read_bytes());targets=scope['merge_targets'](plan,integration_rows)
check(len(targets)==566)
independent={r['target']:r['original']for r in plan['files']};check(len(independent)==533)
for r in integration_rows:independent[str(integration.relative_to(REPO)/Path(r['path']).relative_to(integration))]=r
for c in plan['nativeAfterimageReplacements']:
 independent[c['path']]=next(r for r in integration_rows if r['path']==str(integration/'native'/c['path']))
independent['tests/node-compat/build-engine.sh']=next(r for r in integration_rows if r['path']==str(integration/'proposed/tests/node-compat/build-engine.sh'))
check(targets==independent and len(targets)==566)
mode_counts=collections.Counter()
for row in targets.values():p=checked(row);mode_counts[oct(stat.S_IMODE(p.stat().st_mode)&0o777)]+=1
for mutation in('missing','duplicate','escape','wrong-afterimage'):
 bad=copy.deepcopy(plan)
 if mutation=='missing':bad['files'].pop()
 if mutation=='duplicate':bad['files'][1]['target']=bad['files'][0]['target']
 if mutation=='escape':bad['files'][0]['target']='../escape'
 if mutation=='wrong-afterimage':bad['nativeAfterimageReplacements'][0]['afterSha256']='0'*64
 rejects(lambda bad=bad:scope['merge_targets'](bad,integration_rows))
template=json.loads((SOURCE/'root-authority.template.json').read_bytes())
cfg=dict(controllerIndex=source_index)
rejects(lambda:scope['root_model'](template,cfg,refs))
issued=copy.deepcopy(template);issued.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE_TASK_SELECTION342_SOURCE_STAGE_V1',stageAllowed=True,controllerIndex=source_index,controllerEntry=next(r for r in source_rows if r['path']==str(SOURCE/'controller.py')),stageEntry=next(r for r in integration_rows if r['path']==str(integration/'stage.py')))
scope['root_model'](issued,cfg,refs);check(True)
for name in('buildAllowed','freezeAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','gcAllowed','runtimeAcceptanceClaim','sourcePromotionAllowed','operationalAdmission','metadataProjectionAllowed','timingAllowed'):
 bad=copy.deepcopy(issued);bad[name]=True;rejects(lambda bad=bad:scope['root_model'](bad,cfg,refs))
for name,value in(('expectedCopies',565),('nativeSourceFiles',355),('sourceRoot','/old/source'),('deadlineSeconds',601),('actualStage',{})):
 bad=copy.deepcopy(issued);bad[name]=value;rejects(lambda bad=bad:scope['root_model'](bad,cfg,refs))
peer_shape=dict(schemaVersion=1,state='INDEPENDENT_TASK_SELECTION_STAGE_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=EXPECTED,integrationSourceIndexSha256=refs['integrationIndex']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,stageActionsInvoked=False)
scope['controller_peer_model'](peer_shape,source_index);check(True)
for name,value in(('controllerSourceIndexSha256','0'*64),('integrationSourceIndexSha256','0'*64),('ownerActionsInvoked',True),('hostActionsInvoked',True),('stageActionsInvoked',True)):
 bad=dict(peer_shape,**{name:value});rejects(lambda bad=bad:scope['controller_peer_model'](bad,source_index))
terminal=dict(authority={'syntheticOnly':True},rawExitCode=0,allObservedOwnedGroupsGone=True,parentOwnedGroupGone=True,timeout=False,forcedCleanup=False,remainingObservedPids=[],signals=[],errors=[],interruptedSignals=[],stderr={'bytes':97})
scope['terminal_model'](terminal,terminal['authority']);check(True)
for name,value in(('rawExitCode',1),('timeout',True),('forcedCleanup',True),('signals',['SIGTERM']),('errors',['error']),('remainingObservedPids',[123]),('allObservedOwnedGroupsGone',False)):
 bad=dict(terminal,**{name:value});rejects(lambda bad=bad:scope['terminal_model'](bad,terminal['authority']))

receipt=load(refs['resourceFreezeReceipt']);check(len(receipt['copies'])==666)
originals=0
for row in receipt['copies']:
 checked({k:row[k]for k in('path','sha256','bytes')});check(stat.S_IMODE(Path(row['path']).stat().st_mode)==0o600)
 if row['original']is not None:checked(row['original']);originals+=1
check(originals==663)
freeze_root=Path(refs['resourceFreezeReceipt']['path']).parent
check({str(p)for p in freeze_root.rglob('*')if p.is_file()}=={r['path']for r in receipt['copies']}|{refs['resourceFreezeReceipt']['path']})
stage=load(refs['resourceStage']);check(len(stage['copies'])==501)
for row in stage['copies']:checked(dict(row['original'],path=row['path']));checked(row['original'])

main=funcs['main'];authorize=funcs['authorize'];observe=funcs['observe_targets'];protection=funcs['capture_protection']
check(main.index('frame=authorize(config_row)')<main.index("spec=importlib.util.spec_from_file_location("))
check(main.count('spec.loader.exec_module(monitor)')==1)
check("monitor.monitor([sys.executable,'-B','-I',str(INTEGRATION/'stage.py'),json.dumps(config_row,separators=(',',':'))],str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OUT,600,frame['config']['rootAuthority'])"in main)
check(main.index('terminal_model(terminal,')<main.index('journal_row=dict('))
check("last=Path(terminal['stdout']['path']).read_text().splitlines()[-1];assert json.loads(last)==journal"in main)
check("assert(SOURCE/'.git/HEAD').read_text().strip()==BASE"in main and "not(SOURCE/'.git/objects/info/alternates').exists()"in main)
check("for p in(WORK,FREEZE):assert not p.exists()"in main)
check('failure=failure or error'in main and "with(OUT/'stage-observation.json').open('x')"in main and 'os.fsync(out.fileno())'in main)
check("if not result['stageSuccessful']:result['state']='TASK_SELECTION_STAGE_FAILED_OR_PARTIAL_UNACCEPTED_V1'"in main)
check("for r in targets.values():checked(r);captured.append(r)"in authorize)
check('modes={name:stat.S_IMODE(checked(r).stat().st_mode)&0o777'in authorize)
check("if any(q.is_symlink()for q in(p,*p.parents))"in observe)
for status in('missing','symlink-refused','nonregular-refused','size-mismatch','content-mode-or-inode-mismatch'):check(status in observe)
check("value['status']='match'if h==r['sha256']and value['mode']==value['expectedMode']and value['distinctInode']"in observe)
check('capture_protection(frame[\'refs\'])'in funcs['recheck'])
check('global 'not in text and 'setattr('not in text and 'sys.modules'not in text)
monitor=checked(refs['monitorEntry']).read_text();ast.parse(monitor);check('def monitor(argv, cwd, environment, output, timeout_seconds, authority,'in monitor and '0 < timeout_seconds <= 7200'in monitor)
check('allObservedOwnedGroupsGone=complete'in monitor and "stdout=descriptor(output / 'stdout.log'), stderr=descriptor(output / 'stderr.log')"in monitor)
for p in SOURCE.glob('*.py'):ast.parse(p.read_bytes());check(True)
for name in('sourceRoot','workRoot','freezeRoot','externalOutputRoot','stageJournal'):check(not Path(template[name]).exists()and not Path(template[name]).is_symlink())

audit=dict(schemaVersion=1,state='INDEPENDENT_TASK_SELECTION_STAGE_CONTROLLER_DATA_PURE_AUDIT_PASSED',checks=checks,declaredInputs=1933,uniqueReadHashInputs=len(read_rows),sourceMembers=12,stageTargets=566,baseTargets=533,integrationSealRows=33,nativeSourceFiles=342,nativeReplacements=3,protectedFrozenCopies=666,protectedFrozenOriginalReferences=663,protectedConfiguredCopies=501,plannedOriginalModeCounts=dict(mode_counts),pureNegativeCases=negatives,ownerReportedFilesystemModelCases=8,reviewerFilesystemModelsInvoked=False,controllerOrMonitorOrStageInvoked=False,gitOrCompilerOrEngineOrGuestInvoked=False)
(OWN/'data-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
(OWN/'checked-inputs.json').write_text(json.dumps(dict(schemaVersion=1,files=sorted(read_rows.values(),key=lambda r:r['path'])),indent=2)+'\n')
print(json.dumps(audit))
