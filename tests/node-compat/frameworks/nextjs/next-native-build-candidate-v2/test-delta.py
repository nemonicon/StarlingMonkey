"""Pure exact-delta tests; one benign temp publication with a fake monitor.
Never invokes main, phase_worker, imported utilities, subprocess or build tools.
"""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,tempfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('own_next_build_v2_pure',HERE/'run.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
checks=[]
def check(value,label):
 assert value,label;checks.append(label)
def digest(path):
 b=Path(path).read_bytes();return dict(path=str(Path(path).resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
d=json.loads((HERE/'derivation.json').read_bytes())
for key in ['parentSourceIndex','parentRunner','parentPlan']:check(digest(d[key]['path'])==d[key],key+' exact inherited descriptor')
parent=Path(d['parentRunner']['path']);source=(HERE/'run.py').read_text();reverse=source
for edit in reversed(d['runnerEdits']):
 check(reverse.count(edit['after'])==1,'unique inverse '+str(len(checks)))
 reverse=reverse.replace(edit['after'],edit['before'])
check(reverse==parent.read_text(),'whole runner reconstructs exact immutable v1')
plan=json.loads((HERE/'plan.json').read_bytes());original=json.loads(Path(d['parentPlan']['path']).read_bytes());expected=copy.deepcopy(original)
expected['state']='DORMANT_EXPERIMENTAL_NEXT_NATIVE_BUILD_PLAN_V2';expected['cmakeFlags']['NODE_COMPAT_CLASSIC_STREAMS_TOWEB']='ON'
check(plan==expected,'whole plan has exactly version and ToWeb changes')
check((HERE/'root-authority.template.json').read_bytes()==(parent.parent/'root-authority.template.json').read_bytes(),'authority wire unchanged; own entry/plan still required')
prior=dict(os.environ)
try:
 os.environ.update(CARGO_BUILD_JOBS='99',MAKEFLAGS='-j99',CARGO_INCREMENTAL='1',CCACHE_DISABLE='0',SCCACHE_DISABLE='0',BASH_ENV='/not/executed',BASH_FUNC_irrelevant='not executable')
 env=runner.clean_environment(plan,Path('/private/tmp/pure-work'),Path('/private/tmp/pure-source'),Path('/private/tmp/pure-sm'),Path('/private/tmp/pure-sdk'))
 for key,value in dict(CARGO_BUILD_JOBS='1',MAKEFLAGS='-j1',CARGO_INCREMENTAL='0',CCACHE_DISABLE='1',SCCACHE_DISABLE='1').items():check(env[key]==value,'clean fixed '+key)
 check('BASH_ENV'not in env and not any(k.startswith('BASH_FUNC_')for k in env),'startup controls absent')
 for key in ['HOME','home','CODEX_HOME']:
  if key in prior:check(env[key]==prior[key],'preserve '+key)
finally:
 os.environ.clear();os.environ.update(prior)
baseline=dict(rawExitCode=0,outerRawExitCode=0,ownedGone=True,innerOwnedClean=True,timeout=False,forcedCleanup=False,errors=[],signals=[],interruptedSignals=[],remainingObservedPids=[])
check(runner.phase_succeeded(baseline),'complete clean raw0 passes')
for key,value in [('rawExitCode',1),('outerRawExitCode',1),('ownedGone',False),('innerOwnedClean',False),('timeout',True),('forcedCleanup',True),('errors',['retained error']),('signals',[{'signal':15}]),('interruptedSignals',[2]),('remainingObservedPids',[123])]:
 row=copy.deepcopy(baseline);row[key]=value;check(not runner.phase_succeeded(row),'reject '+key+' even with other fields clean')
for key in ['signals','interruptedSignals','remainingObservedPids']:
 for value in [None,False]:
  row=copy.deepcopy(baseline);row[key]=value;check(not runner.phase_succeeded(row),'reject malformed '+key+str(value))
 row=copy.deepcopy(baseline);del row[key]
 try:runner.phase_succeeded(row)
 except KeyError:checks.append('missing '+key+' refuses')
 else:raise AssertionError('missing terminal array accepted')
# Test the real phase publication seam, replacing only its monitor argument
# with an inert fake that writes DATA; no real monitor/module is imported.
with tempfile.TemporaryDirectory(prefix='next-build-v2-data-only-')as temporary:
 work=Path(temporary).resolve();(work/'results').mkdir();(work/'root-authority.json').write_text('{}\n')
 class FakeMonitor:
  def monitor(self,argv,cwd,environment,output,timeout,authority):
   check(argv[3]==str(HERE/'run.py') and '--worker-packet'in argv,'phase uses genuine v2 entry')
   row=dict(rawExitCode=0,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,timeout=False,forcedCleanup=False,errors=[],signals=[{'pid':1,'signal':15}],interruptedSignals=[2],remainingObservedPids=[123])
   runner.save(output/'terminal.json',row)
   runner.save(output.parent/'worker-result.json',dict(rawChildExitCode=0,ownedGroupCleanup=dict(complete=True,events=[],errors=[]),launcherErrors=[],sigtermReceived=False,stopReason=None))
   return row
 p=dict(disk=dict(stopBytes=0),hostTools=[dict(name='python3',executable=dict(path='/not-executed/python3'))])
 record=runner.phase(FakeMonitor(),{},p,work,'benign-data-publication',['not-executed'],{},1)
 for key,value in dict(signals=[{'pid':1,'signal':15}],interruptedSignals=[2],remainingObservedPids=[123]).items():check(record[key]==value,'real phase retains '+key)
 check(json.loads((work/'results/benign-data-publication/phase.json').read_bytes())==record,'whole real phase record durably retained')
 check(not runner.phase_succeeded(record),'real raw0 publication with monitor events refuses')
tree=ast.parse(source)
calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='phase_succeeded']
check(len(calls)==2,'ordinary commands and Ninja harvest use same gate')
check('monitor.monitor('in source and 'life.monitor_owned_command('in source,'original utility API calls unchanged')
print(json.dumps(dict(schemaVersion=1,passed=True,checks=len(checks),cases=checks,hostPureOnly=True,benignTempDataOnly=True,monitorInvoked=False,subprocessInvoked=False,nativeBuildOrCompilerInvoked=False,guestExecuted=False)))
