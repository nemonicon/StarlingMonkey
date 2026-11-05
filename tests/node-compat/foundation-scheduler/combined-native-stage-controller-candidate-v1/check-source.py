"""Own source/data and extracted pure-model checks; no stage/Git/monitor runs."""
import ast,copy,hashlib,json,stat
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
S=REPO/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1'
checks=0
def check(ok,label):
 global checks
 assert ok,label;checks+=1
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for r in load(HERE/'input-hashes.json')['files']:
 p=Path(r['path']);check(p.is_file()and not p.is_symlink(),'regular input');check(p.stat().st_size==r['bytes']and sha(p)==r['sha256'],'hash input')
controller=(HERE/'controller.py').read_text();tree=ast.parse(controller)
functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
constants=dict(REPO=REPO,OWN=HERE,SOURCE_SHA='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65',MONITOR_SHA='0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b',DEST=Path('/private/tmp/starling-node-compat/combined-native355-v1-source'),WORK=Path('/private/tmp/starling-node-compat/combined-native355-v1-build'),FREEZE=Path('/private/tmp/starling-node-compat/combined-native355-v1-freeze'),OUT=Path('/private/tmp/starling-node-compat/combined-native355-v1-stage-external-root'),JOURNAL=Path('/private/tmp/starling-node-compat/combined-native355-v1-stage.json'),BASE='54b3329b3ce818fd1f244e871e9c259b63667cda',TIMEOUT=600,Path=Path)
pure=['safe','source_peer_model','stage_peer_model','root_model','plan_model','terminal_model','journal_model']
ns=dict(constants);exec(compile(ast.Module(body=[functions[n]for n in pure],type_ignores=[]),'<extracted-own-pure-stage-models>','exec'),ns)
# Exercise the real descriptor read boundary on the actual declared files.
# This extracts data-only functions, not authorize/stage/main or a monitor.
data_ns=dict(Path=Path,hashlib=hashlib,stat=stat,json=json)
exec(compile(ast.Module(body=[functions[n]for n in ['safe','checked','read','family']],type_ignores=[]),'<extracted-own-data-read-boundary>','exec'),data_ns)
for r in load(HERE/'input-hashes.json')['files']:
 data_ns['checked'](r);check(True,'actual regular/hash/no-symlink descriptor read boundary')
def refused(fn,label):
 try:fn()
 except(AssertionError,TypeError,KeyError,ValueError):check(True,label);return
 raise AssertionError('Must refuse '+label)
refs=load(HERE/'references.json');plan=load(HERE/'stage-copy-plan.json')['files']
sample=load(HERE/'input-hashes.json')['files'][0]
for mutate in ['sha','bytes','relative','extra']:
 r=copy.deepcopy(sample)
 if mutate=='sha':r['sha256']='0'*64
 elif mutate=='bytes':r['bytes']+=1
 elif mutate=='relative':r['path']='relative-file'
 else:r['extra']=True
 refused(lambda r=r:data_ns['checked'](r),'actual descriptor '+mutate)
for key in ['integrationIndex','monitorIndex']:
 data_ns['family'](refs[key]);check(True,'actual whole indexed family read boundary '+key)
index=load(S/'index.json');source_rows=[refs['integrationIndex']]+[dict(path=str(S/r['path']),sha256=r['sha256'],bytes=r['bytes'])for r in index['files']]
native=load(S/'native-origins.json')['files'];tools=load(S/'tool-origins.json')['files']
ns['plan_model'](plan,native,tools,source_rows);check(True,'actual1613 plan model')
for mutate in ['missing','duplicate','changed-sha','changed-role','wrong-mode','escaped']:
 value=copy.deepcopy(plan)
 if mutate=='missing':value.pop()
 elif mutate=='duplicate':value[-1]=copy.deepcopy(value[0])
 elif mutate=='changed-sha':value[0]['sha256']='a'*64
 elif mutate=='changed-role':value[0]['roles']=['FAKE_SOURCE_CONTEXT']
 elif mutate=='wrong-mode':value[0]['sourceMode']=0o7777
 else:value[0]['path']='../escaped'
 refused(lambda v=value:ns['plan_model'](v,native,tools,source_rows),'plan '+mutate)
for name in ['../x','/x','a//b','a/./b','a/../b','a\\b','a\0b','.git/config']:
 refused(lambda n=name:ns['safe'](n),'unsafe path')
for name in ['builtins/node-compat/zlib/kernel.cpp','tests/node-compat/example.mjs']:
 check(ns['safe'](name)==name,'safe source path')
own=dict(path=str(HERE/'index.json'),sha256='a'*64,bytes=1)
root=load(HERE/'root-authority.template.json')
refused(lambda:ns['root_model'](root,own,refs),'unissued actual Root template')
root.update(state='ROOT_REVIEWED_COMBINED355_SOURCE_STAGE_V1',phase='source-stage-only',sourceStageAllowed=True,stageControllerIndex=own,stageControllerEntry=dict(path=str(HERE/'controller.py'),sha256='b'*64,bytes=1),gitBinary=dict(path='/synthetic/git',sha256='c'*64,bytes=1))
ns['root_model'](root,own,refs);check(True,'synthetic Root model shape only')
root_negatives=[]
for key,value in [('sourceStageAllowed',False),('configuredSourceRoot','/wrong'),('workRoot','/old-work'),('freezeRoot','/old-freeze'),('baselineRevision','d1f8'),('nativeSourceFiles',342),('retainedParentNativeFiles',352),('changedNativeFiles',3),('basePlanRows',1403),('expectedStageCopies',1424),('externalParentDeadlineSeconds',7200),('privateBackendEvidenceHookEnabled',True),('nativeBuildAllowed',True),('guestAllowed',True),('metadataProjectionAllowed',True),('operationalAdmission',True),('actualStageResult',{'fake':True})]:
 value_root=copy.deepcopy(root);value_root[key]=value;refused(lambda v=value_root:ns['root_model'](v,own,refs),'Root '+key);root_negatives.append(key)
source_peer=dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=constants['SOURCE_SHA'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,operationalAdmission=False,nativeSourceFiles=355,retainedParentNativeFiles=348,changedNativeFiles=7,externalEmbeddingSources=3,selectedManifestCount=11,initialVariant='normal-off',privateBackendEvidenceHookEnabled=False)
ns['source_peer_model'](source_peer);check(True,'synthetic integration peer shape only')
for key,value in [('state','OLD_CRYPTO_OR342_PEER'),('sourceIndexSha256','d'*64),('sourceReviewPassed',False),('nativeSourceFiles',342),('retainedParentNativeFiles',352),('changedNativeFiles',3),('ownerActionsInvoked',True)]:
 v=copy.deepcopy(source_peer);v[key]=value;refused(lambda v=v:ns['source_peer_model'](v),'source peer '+key)
stage_peer=dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_SOURCE_STAGE_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=own['sha256'],integrationSourceIndexSha256=constants['SOURCE_SHA'],genericMonitorSourceIndexSha256=constants['MONITOR_SHA'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,sourceStageActionsInvoked=False)
ns['stage_peer_model'](stage_peer,own);check(True,'synthetic controller peer shape only')
for key,value in [('controllerSourceIndexSha256','e'*64),('genericMonitorSourceIndexSha256','f'*64),('sourceReviewPassed',False),('sourceStageActionsInvoked',True)]:
 v=copy.deepcopy(stage_peer);v[key]=value;refused(lambda v=v:ns['stage_peer_model'](v,own),'controller peer '+key)
authority=dict(path='/synthetic/Root.json',sha256='b'*64,bytes=1)
terminal=dict(authority=authority,rawExitCode=0,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,timeout=False,forcedCleanup=False,interruptedSignals=[],remainingObservedPids=[],signals=[],errors=[],stderr=dict(bytes=0),observedProcesses=[dict(pid=1)],finalGroups=[dict(alive=False)])
ns['terminal_model'](terminal,authority);check(True,'synthetic terminal model')
for key,value in [('rawExitCode',1),('timeout',True),('forcedCleanup',True),('allObservedOwnedGroupsGone',False),('signals',[1]),('errors',[1]),('remainingObservedPids',[1])]:
 v=copy.deepcopy(terminal);v[key]=value;refused(lambda v=v:ns['terminal_model'](v,authority),'terminal '+key)
v=copy.deepcopy(terminal);v['finalGroups'][0]['alive']=True;refused(lambda:ns['terminal_model'](v,authority),'remaining group alive')
frame=dict(root=root,config=dict(rootAuthority=authority),copies=plan)
commands=[dict(argv=['/synthetic/git','clone','--no-local','--no-checkout',str(REPO),str(constants['DEST'])],returncode=0,timedOut=False,timeoutSeconds=120),dict(argv=['/synthetic/git','-C',str(constants['DEST']),'checkout','--detach',constants['BASE']],returncode=0,timedOut=False,timeoutSeconds=120)]
journal=dict(schemaVersion=1,state='COMBINED355_SOURCE_STAGED_NOT_BUILT',sourceIndexSha256=constants['SOURCE_SHA'],copies=plan,copiesCompleted=plan,copiedFiles=1613,rootAuthority=authority,controllerIndex=own,configuredSourceRoot=str(constants['DEST']),workRoot=str(constants['WORK']),freezeRoot=str(constants['FREEZE']),baselineRevision=constants['BASE'],detachedHead=constants['BASE'],nativeSourceFiles=355,retainedParentNativeFiles=348,changedNativeFiles=7,externalEmbeddingSources=3,selectedManifestCount=11,commands=commands)
for key in ['nativeBuildExecuted','engineExecuted','guestExecuted','metadataProjected','privateBackendEvidenceHookEnabled','operationalAdmission']:journal[key]=False
for key in ['allCopiedHashesModesAndDistinctInodesVerified','gitObjectInodesDisjoint','sourceOriginalInputsRechecked','originalGitObjectIdentityUnchanged']:journal[key]=True
ns['journal_model'](journal,frame);check(True,'synthetic journal model')
for key,value in [('state','OLD_STAGE_RESULT'),('copiedFiles',1424),('nativeSourceFiles',342),('metadataProjected',True),('privateBackendEvidenceHookEnabled',True),('detachedHead','d1f8')]:
 v=copy.deepcopy(journal);v[key]=value;refused(lambda v=v:ns['journal_model'](v,frame),'journal '+key)
v=copy.deepcopy(journal);v['commands'][0]['argv'].remove('--no-local');refused(lambda:ns['journal_model'](v,frame),'clone no-local required')
v=copy.deepcopy(journal);v['commands'][1]['returncode']=1;refused(lambda:ns['journal_model'](v,frame),'checkout raw1 refused')
for row in plan:
 p=Path(row['original']);check(stat.S_IMODE(p.stat().st_mode)==row['sourceMode'],'source mode unchanged')
main=''.join(controller.splitlines(True)[functions['main'].lineno-1:functions['main'].end_lineno])
check(main.index('frame=authorize(config_row)')<main.index('spec=importlib.util.spec_from_file_location'),'complete authorize before custom import')
check('module.monitor(argv,str(REPO),{**os.environ' in main and ',OUT,TIMEOUT,'in main,'genuine six argument monitor API')
check('finally:recheck(frame)'in main,'failed command final input recheck')
check("'--stage-worker'"in main and "'-B','-I'"in main,'isolated child same source entry')
check('checked(root[\'pythonExecutable\'])==Path(sys.executable).resolve()'in controller,'actual Python identity binding')
check("'--no-local','--no-checkout'"in controller and "'checkout','--detach',BASE"in controller,'genuine clone operations')
check('s.st_nlink==1' in controller and 'not in original_ids'in controller,'copy ownership checked before truncation')
check("record['stdout']=durable"in controller and "record['terminal']=durable"in controller,'raw command evidence before assertions')
check('module.monitor('in controller and '.load_common('not in controller and 'layer-policy.py'not in controller,'no producer/helper/classifier imports')
check(all(not p.exists()and not p.is_symlink()for p in[constants['DEST'],constants['WORK'],constants['FREEZE'],constants['OUT'],constants['JOURNAL']]),'no stage/work/freeze/output created')
for p in HERE.glob('*.py'):ast.parse(p.read_text());check(True,'Python AST '+p.name)
result=dict(schemaVersion=1,state='COMBINED355_STAGE_SOURCE_DATA_AND_PURE_MODELS_PASSED',checks=checks,stageCopyRows=1613,sourceOriginalInputs=1590,ownInputRows=1637,operationalModelsSyntheticOnly=True,actualDataReadBoundaryInvoked=True,actualDataDescriptorReads=1637,actualIndexedFamilyReads=2,rootCounterexamples=root_negatives,controllerSha256=sha(HERE/'controller.py'),sourceStageExecuted=False,gitInvoked=False,monitorInvoked=False,producerHelperInvoked=False,nativeBuildExecuted=False,engineExecuted=False,guestExecuted=False)
(HERE/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
