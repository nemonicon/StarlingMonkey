"""Actual own context constants and pure parent helpers only; no parent call."""
from pathlib import Path
import ast,importlib.util,json
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('inert_combined355_own_external',P/'external.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
cases=0
def good(v):
 global cases
 assert v;cases+=1
def refuse(fn):
 global cases
 try:fn()
 except(AssertionError,KeyError,TypeError,ValueError):cases+=1
 else:raise AssertionError('pure refusal missed')
good(m.OWN==P and Path(m.__file__).resolve()==P/'external.py')
for phase in ['bundle','construct']:
 for fixture in ['resource','pure','fatal','init-fatal','clock-snapshot','surviving-interest']:
  out,external,tmp,deadline=m.phase_paths(phase,fixture);good(str(out)==m.BASE+'-'+phase+'-'+fixture and str(external)==str(out)+'-external-root'and str(tmp)==str(out)+'-tmp'and deadline==(1200 if phase=='bundle'else 2400))
for phase,fixture in [('runtime','resource'),('construct','../escape'),('bundle','resource/extra')]:refuse(lambda:m.phase_paths(phase,fixture))
env={'HOME':'/model/home','home':'preserve','CODEX_HOME':'/model/codex','NODE_OPTIONS':'--require=bad','PYTHONPATH':'bad','NAPI_RS_FORCE_WASI':'bad','NODE_COMPAT_COMPONENTIZE_MODULE':'bad'};before=dict(env);child=m.child_environment(env,Path('/model/private-tmp'),'/model/package');good(env==before and child['HOME']==env['HOME']and child['home']==env['home']and child['CODEX_HOME']==env['CODEX_HOME']and child['TMPDIR']=='/model/private-tmp'and child['NODE_COMPAT_TOOLCHAIN']=='/model/package'and all(k not in child for k in ['NODE_OPTIONS','PYTHONPATH','NAPI_RS_FORCE_WASI','NODE_COMPAT_COMPONENTIZE_MODULE']))
t=dict(rawExitCode=0,timeout=False,forcedCleanup=False,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,errors=[],signals=[],interruptedSignals=[],remainingObservedPids=[]);m.clean_terminal(t);good(True)
for k,v in [('rawExitCode',1),('rawExitCode',False),('timeout',True),('forcedCleanup',True),('parentOwnedGroupGone',False),('allObservedOwnedGroupsGone',False),('errors',['writer failure']),('signals',['SIGTERM']),('interruptedSignals',[2]),('remainingObservedPids',[99])]:refuse(lambda:m.clean_terminal({**t,k:v}))
tree=ast.parse((P/'external.py').read_text());parent=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='parent');calls=[n for n in ast.walk(parent)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='monitor'];good(len(calls)==1 and len(calls[0].args)==6)
good("root['entry']==next(r for r in rs"in(P/'external.py').read_text()and "root['externalController']==next(r for r in rs"in(P/'external.py').read_text())
print(json.dumps(dict(schemaVersion=1,passed=True,cases=cases,inertOwnModuleImport=True,actualOwnAndFileConstantsChecked=True,parentMonitorOrOwnerActions=False)))
