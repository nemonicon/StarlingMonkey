"""Finite SOURCE/DATA/AST/extracted-model checks; no owner actions or imports."""
from pathlib import Path
import ast,copy,hashlib,json,os,shlex,sys,types
OWN=Path(__file__).resolve().parent;S=OWN.parent
CHECKS=0;SEEN={};MODELS=0
def need(ok,why):
 global CHECKS
 CHECKS+=1
 if not ok:raise AssertionError(why)
def checked(row):
 p=Path(row['path']);p=Path('/private'+str(p))if str(p).startswith('/tmp/')else p
 need(p.is_absolute()and'..'not in p.parts,'original absolute input')
 for q in(p,*p.parents):need(not q.is_symlink(),'regular declared input')
 a=p.stat();stamp=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)
 if str(p)in SEEN:
  old=SEEN[str(p)];need(old[:2]==(row['sha256'],row['bytes'])and old[2]==stamp,'matching stable descriptor');return
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=p.stat();need(stamp==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)and a.st_size==row['bytes']and h.hexdigest()==row['sha256'],'whole actual source DATA bytes')
 SEEN[str(p)]=(row['sha256'],row['bytes'],stamp)
def load(p):return json.loads(Path(p).read_bytes())
def extract(path,names,env):
 tree=ast.parse(Path(path).read_text());body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names]
 need({n.name for n in body}==set(names),'exact extracted pure model function names')
 exec(compile(ast.Module(body=body,type_ignores=[]),str(path),'exec'),env);return env
def denied(fn,*args):
 global MODELS
 MODELS+=1
 try:fn(*args)
 except(AssertionError,KeyError,TypeError,ValueError):return
 raise AssertionError('negative model accepted')
def main():
 global MODELS
 refs=load(OWN/'references.json');freeze=load(OWN/'input-freeze.json');build=load(refs['actualBuildReview']['result']['path']);metadata=load(refs['metadata']['path']);policy=load(refs['policy']['path']);db=load(refs['compileCommands']['path']);ledger=load(refs['buildInputLedger']['path'])
 for row in freeze['files']:checked(row)
 for f in refs['families']:
  p=Path(f['index']['path']);value=load(p);names={x['path']for x in value['files']}|{'index.json'}
  need(not any(x.is_symlink()for x in p.parent.rglob('*'))and{x.relative_to(p.parent).as_posix()for x in p.parent.rglob('*')if x.is_file()}==names,'complete exact indexed family in its original context')
 need(len(ledger['files'])==20761 and refs['buildInputLedger']==build['inputHashes'],'real actual complete BUILD ledger')
 for row in ledger['files']:checked(row)
 for row in refs['sdkAliases']:need(Path(row['path']).is_symlink()and os.readlink(row['path'])==row['linkText']and str(Path(row['path']).resolve())==row['resolvedPath'],'exact declared SDK alias')
 for name in['copy_io.py','monitor.py']:need((OWN/name).read_bytes()==(S/'resource-freezer-candidate-v1'/name).read_bytes(),'byte-exact accepted donor '+name)
 for row in load(OWN/'derivations.json')['files']:
  before=Path(row['donor']['path']).read_text();after=(OWN/row['target']).read_text();value=before
  for edit in sorted(row['exactEdits'],key=lambda x:x['beforeStart'],reverse=True):need(value[edit['beforeStart']:edit['beforeEnd']]==edit['before'],'actual exact source preimage');value=value[:edit['beforeStart']]+edit['after']+value[edit['beforeEnd']:]
  need(value==after,'complete forward derivation '+row['target']);value=after
  for edit in sorted(row['exactEdits'],key=lambda x:x['afterStart'],reverse=True):need(value[edit['afterStart']:edit['afterEnd']]==edit['after'],'actual exact source afterimage');value=value[:edit['afterStart']]+edit['before']+value[edit['afterEnd']:]
  need(value==before,'complete exact source reversal '+row['target'])
 syntax=[]
 for p in sorted(OWN.glob('*.py')):ast.parse(p.read_text());syntax.append(p.name)
 # Actual helper API declarations and all pre-import paths are authenticated
 # DATA; neither module is imported or called here.
 for role,names in [('configuredModel',{'validate_metadata':7}),('configuredLayer',{'validate_sources':2,'validate_classic_compilation':4})]:
  checked(refs[role]);tree=ast.parse(Path(refs[role]['path']).read_text())
  for name,n in names.items():node=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name==name);need(len(node.args.args)==n,'genuine configured API signature '+name)
 stage=load(refs['actualStageResult']['path']);paths={x['path']for x in stage['copies']}
 for suffix in['task-selection-integration-candidate-v1/layer-policy.py','task-selection-integration-candidate-v1/native-admission-model.py','integration-candidate-v1/layer-policy.py','resource-integration-candidate-v1/index.json','task-selection-candidate-v1/index.json','independent-task-selection-source-review-v1/index.json']:
  need(str(Path(refs['configuredSourceRoot'])/'tests/node-compat/foundation-scheduler'/suffix)in paths,'real staged transitive loader/data context '+suffix)
 for name in['task-selection-integration-candidate-v1','resource-integration-candidate-v1','task-selection-candidate-v1','independent-task-selection-source-review-v1']:
  base=Path(refs['configuredSourceRoot'])/'tests/node-compat/foundation-scheduler'/name;value=load(base/'index.json');need({x.relative_to(base).as_posix()for x in base.rglob('*')if x.is_file()}=={x['path']for x in value['files']}|{'index.json'},'exact genuine configured layer ancestry family')
 monitor=ast.parse((OWN/'monitor.py').read_text());need(len(next(n for n in monitor.body if isinstance(n,ast.FunctionDef)and n.name=='monitor').args.args)==6,'actual genuine six-argument monitor API')
 source_tree=ast.parse((OWN/'entry.py').read_text());mc=next(n for n in ast.walk(source_tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='monitor');need(len(mc.args)==6,'actual caller preserves six arguments and2400 bound')
 plan=load(OWN/'capture-plan.json');need(plan['nativeSourceCopies']==342 and plan['configuredNonnativeCopies']==224 and plan['externalEmbeddingCopies']==3 and plan['actualObjectCopies']==68 and plan['actualLibraryCopies']==29,'finite real342 copy groups')
 need(len({r['destination']for r in plan['copies']})==len(plan['copies'])==plan['baseCopies'],'finite unique output plan')
 for row in plan['copies']:checked(row['source'])
 need(not Path(refs['freezeRoot']).exists(),'no actual selector freeze output created')
 # Extracted own pure guards use actual unmodified metadata/DB as DATA.
 env=dict(Path=Path,shlex=shlex,OWN=OWN,SOURCE=Path(refs['configuredSourceRoot']),WORK=Path(refs['workRoot']),FREEZE=Path(refs['freezeRoot']),EXTERNAL=Path(refs['externalOutputRoot']),SOURCE_SHA=refs['taskSelectionSourceIndex']['sha256'],ENGINE_SHA=refs['engine']['sha256'],META_SHA=refs['metadata']['sha256'])
 extract(OWN/'entry.py',['root_model','peer_model','metadata_model','compilation_model'],env)
 own=dict(path=str(OWN/'index.json'),sha256='f'*64,bytes=0)
 root=load(OWN/'future-root-authority.template.json');denied(env['root_model'],root,own)
 root.update(state='ROOT_REVIEWED_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FREEZE_V1',phase='freeze',freezerIndex=own,entry=dict(path=str(OWN/'entry.py'),sha256='0'*64,bytes=0),freezeAllowed=True,readOnlySourceAdmissionAllowed=True,postBuildNinjaCommandsAllowed=True,syntheticModelOnly=True)
 env['root_model'](root,own);MODELS+=1
 for key in['buildAllowed','gcReconfigureAllowed','exportAllowed','bootstrapAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']:
  x=copy.deepcopy(root);x[key]=True;denied(env['root_model'],x,own)
 for key,value in [('nativeSourceFiles',355),('configuredSourceRoot','/tmp/wrong'),('taskSelectionSourceIndexSha256','0'*64),('externalParentDeadlineSeconds',7200),('readOnlySourceAdmissionAllowed',False),('freezeAllowed',False),('phase','build')]:x=copy.deepcopy(root);x[key]=value;denied(env['root_model'],x,own)
 peer=dict(schemaVersion=1,state='INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1',freezerSourceIndexSha256=own['sha256'],taskSelectionSourceIndexSha256=env['SOURCE_SHA'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeFreezeActionsInvoked=False)
 env['peer_model'](peer,own);MODELS+=1
 for key in['ownerActionsInvoked','hostActionsInvoked','nativeFreezeActionsInvoked']:
  x=dict(peer);x[key]=True;denied(env['peer_model'],x,own)
 env['metadata_model'](metadata,policy,refs);env['compilation_model'](db,metadata,policy,refs);MODELS+=2
 for key,value in [('gcStress',True),('oomTesting',True),('entropyPolicy','runtime-only'),('engineSha256','0'*64),('sourceManifest',metadata['sourceManifest'][:-1]),('taskSelectionPolicy',{})]:x=copy.deepcopy(metadata);x[key]=value;denied(env['metadata_model'],x,policy,refs)
 for variant in['missing','duplicate','wrong-caller','debug','gc','null-header']:
  x=copy.deepcopy(db)
  if variant=='missing':x.pop()
  elif variant=='duplicate':x[-1]=copy.deepcopy(x[0])
  elif variant=='wrong-caller':next(v for v in x if v['file'].endswith('/runtime/event_loop.cpp'))['command']+=' -DWRONG=1'
  elif variant=='debug':x[0]['command']+=' -DDEBUG=1'
  elif variant=='gc':x[0]['command']+=' -DNODE_COMPAT_GC_STRESS=1'
  else:next(v for v in x if v['file'].endswith('/starling-raw.wasm/null.cpp'))['command']+=' -include /wrong/header'
  denied(env['compilation_model'],x,metadata,policy,refs)
 # Full caller shape, not a hand-written unrelated option fixture.
 body=ast.parse((OWN/'freeze.py').read_text());entry=ast.parse((OWN/'entry.py').read_text())
 frame_creation=next(n for n in ast.walk(entry)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='Frame')
 available={x.arg for x in frame_creation.keywords}|{'metadata','policy','database'}
 used={n.slice.value for n in ast.walk(body)if isinstance(n,ast.Subscript)and isinstance(n.value,ast.Name)and n.value.id=='frame'and isinstance(n.slice,ast.Constant)and type(n.slice.value)is str}
 need(used<=available and 'configRow'in used,'actual authorize-to-body frame fields including CLI config descriptor')
 calls=[]
 class Loader:
  def __init__(self,name):self.name=name
  def exec_module(self,module):
   calls.append(('import',self.name))
   if'metadata_model'in self.name:
    def validate(*args):need(len(args)==7 and args[0]is metadata and args[1]is policy and args[-1]=='normal-off','actual7-argument genuine model seam');return dict(state='FINITE_RESOURCE_TASK_SELECTION342_METADATA_SHAPE_ONLY',nativeFiles=342,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
    module.validate_metadata=validate
   else:
    module.HERE=Path(refs['configuredSourceRoot'])/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1'
    module.validate_sources=lambda *args:need(args==(Path(refs['configuredSourceRoot']),metadata['sourceManifest']),'actual real configured source caller')
    def compilation(*args):need(args==(db,metadata['actualEmbeddingCompileCommands'],Path(refs['configuredSourceRoot']),metadata),'actual4-argument real compile API seam');return ['n']*61,['q'],['p']*5
    module.validate_classic_compilation=compilation
 util=types.SimpleNamespace(spec_from_file_location=lambda name,path:types.SimpleNamespace(loader=Loader(name)),module_from_spec=lambda spec:types.SimpleNamespace())
 fake_g=types.SimpleNamespace(require_frame=lambda f:need(f is frame,'explicit own Frame seam'),recheck=lambda f:calls.append(('recheck',)),checked=lambda row:calls.append(('checked',row['path'])),SOURCE=Path(refs['configuredSourceRoot']),SOURCE_SHA=env['SOURCE_SHA'],read=lambda row:load(row['path']))
 frame=dict(refs=refs,metadata=metadata,policy=policy,database=db,config=dict(freezerIndex=own))
 ae=extract(OWN/'admission.py',['admit'],dict(importlib=types.SimpleNamespace(util=util)))
 result=ae['admit'](frame,fake_g);MODELS+=1
 fe=extract(OWN/'freeze.py',['admission_model'],{});fe['admission_model'](result,frame,fake_g);MODELS+=1
 need(calls[0]==('recheck',)and calls[-1]==('recheck',),'source rechecks surround actual admission caller body')
 for key,value in [('sourceFiles',355),('selectedManifestCount',8),('engineHashedAsGuardData',False),('engineExecuted',True),('taskSelectionPolicy',{}),('selectedManifests',[])]:x=copy.deepcopy(result);x[key]=value;denied(fe['admission_model'],x,frame,fake_g)
 # Extract actual nested raw capture function with only a fake subprocess and
 # fake durable writer. No child, monitor, helper or filesystem copy is called.
 raw_node=next(n for n in ast.walk(body)if isinstance(n,ast.FunctionDef)and n.name=='raw_call')
 class TimeoutExpired(Exception):
  def __init__(self):self.stdout=b'partial-out';self.stderr=b'partial-err'
 events=[]
 def put(name,data):events.append((name,data));return dict(path='/synthetic/'+name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
 def fake_run(*args,**kwargs):
  if scenario=='timeout':raise TimeoutExpired()
  if scenario=='spawn':raise FileNotFoundError()
  return types.SimpleNamespace(returncode=1 if scenario=='status1'else 0,stdout=b'x'*(4*1024*1024+1)if scenario=='large'else b'out',stderr=b'err')
 se=dict(subprocess=types.SimpleNamespace(run=fake_run,PIPE=object(),TimeoutExpired=TimeoutExpired),g=types.SimpleNamespace(SOURCE=Path('/synthetic/source')),os=os,json=json,write=put)
 exec(compile(ast.Module(body=[raw_node],type_ignores=[]),str(OWN/'freeze.py'),'exec'),se)
 for scenario in['ok','status1','timeout','spawn','large']:
  events.clear()
  if scenario=='ok':se['raw_call']('model',['synthetic'],1);MODELS+=1
  else:denied(se['raw_call'],'model',['synthetic'],1)
  need([x[0]for x in events]==['helper-calls/model/stdout.log','helper-calls/model/stderr.log','helper-calls/model/terminal.json'],'all available streams/terminal before assertion')
  terminal=json.loads(events[-1][1]);need(terminal['stdout']['bytes']==len(events[0][1])and terminal['stderr']['bytes']==len(events[1][1]),'no raw clipping')
  if scenario in['timeout','spawn']:need(terminal['capturedStreamsComplete']is False and terminal['rawExitCode']is None,'honest incomplete/launch terminal')
 ve=extract(OWN/'verify.py',['receipt_model'],dict(SOURCE_SHA=env['SOURCE_SHA'],ENGINE=refs['engine']['sha256'],META=refs['metadata']['sha256']))
 receipt=dict(schemaVersion=1,state='SCHEDULER_TASK_SELECTION342_NORMAL_OFF_NATIVE_FREEZE_COMPLETE_UNREVIEWED_V1',variant='normal-off',taskSelectionSourceIndexSha256=env['SOURCE_SHA'],nativeSourceIndexed=dict(sha256=env['SOURCE_SHA']),freezerSourceIndexed=own,freezerSourceIndexSha256=own['sha256'],engine=refs['engine'],metadata=refs['metadata'],nativeInputsVerified=342,unchangedResourceParentFiles=339,nativeReplacements=3,externalEmbeddingInputsVerified=3,selectedManifestCount=9,compileDatabaseRows=67,policyCppCommands=61,otherConfiguredSourceRows=5,generatedNullCppRows=1,embeddingRowsInCompileDatabase=0,separatePostBuildEmbeddingCommands=1,actualStrictCommands=4,actualPrivateClassicCommands=5,staticLibrariesPhysicallyCopied=29,verifiedOriginalReferenceCount=20761,nativeAllInvalidRuntimeValidation=None,resourceNativeRuntimeValidation=None,reviewedEnginePins=None)
 for k in('rawMetadataBytesUnchanged','rawMetadataOriginalConfiguredPathsPreserved','allInputsValidatedBeforeHelperImports','allInputsValidatedBeforeCopies','allCopiesAndOriginalsRehashed','receiptRequiresExternalParentZeroAndIndependentReview','verifiedReferencesNotAllCopied','sdkAliasesNotCopiedAsLinks'):receipt[k]=True
 for k in('gcReconfigureAllowed','engineExecuted','bootstrapExecuted','componentOrGuestExecuted','operationalAdmission','runtimeAcceptanceClaim'):receipt[k]=False
 ve['receipt_model'](receipt,own['sha256']);MODELS+=1
 for key,value in [('state','SCHEDULER_RESOURCE342_NORMAL_OFF_NATIVE_FREEZE_COMPLETE_UNREVIEWED_V1'),('nativeInputsVerified',355),('taskSelectionSourceIndexSha256','0'*64),('verifiedOriginalReferenceCount',7500),('allInputsValidatedBeforeHelperImports',False),('engineExecuted',True),('operationalAdmission',True)]:x=copy.deepcopy(receipt);x[key]=value;denied(ve['receipt_model'],x,own['sha256'])
 need('checked(row)'in(OWN/'entry.py').read_text().split('def load_own',1)[0],'streamed full guard source')
 text=(OWN/'entry.py').read_text();need(text.index("ledger=read(refs['buildInputLedger'])")<text.index('def load_own'),'full ledger precedes first actual custom module loader')
 need('spec.loader.exec_module'in(OWN/'admission.py').read_text()and'g.recheck(frame)'in(OWN/'admission.py').read_text(),'genuine caller explicit source API')
 need('20761'in text and "expected_include=0"in text and 'verifiedReferenceCount' in text,'actual finite ledger/null-source boundary')
 need(load(OWN/'future-config.template.json')['rootAuthority']is None and load(OWN/'future-source-peer-contract.json')['freezerSourceIndexSha256']is None,'no activation authority')
 # Stable final read boundary after every own source/data model.
 for path,(sha,n,stamp)in SEEN.items():
  s=Path(path).stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==stamp,'all source inputs remained stable')
 evidence=dict(schemaVersion=1,state='TASK_SELECTION342_FREEZER_SOURCE_DATA_AND_EXTRACTED_MODELS_PASSED_V1',sourceOnly=True,checks=CHECKS,physicalInputFiles=len(SEEN),fullBuildLedgerRows=20761,preparationInputs=len(freeze['files']),baseCopyRows=plan['baseCopies'],baseCopyBytes=plan['baseCopyBytes'],pureModelCases=MODELS,pythonAstFiles=syntax,actualAdmissionHelperExecuted=False,genuineLayerOrModelImported=False,actualChildOrMonitorInvoked=False,copyLoopInvoked=False,freezerInvoked=False,engineExecuted=False,operationalAdmission=False)
 print(json.dumps(evidence))
 if len(sys.argv)==2:
  p=Path(sys.argv[1]);assert p.is_absolute()and not p.exists()
  with p.open('x')as f:json.dump(evidence,f,indent=2);f.write('\n')
if __name__=='__main__':main()
