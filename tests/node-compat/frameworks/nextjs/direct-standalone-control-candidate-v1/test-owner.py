"""Genuine AST-extracted selector/monitor call, inert DATA; never call main."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import re
HERE=Path(__file__).resolve().parent
source=(HERE/'run-owned.py').read_text();tree=ast.parse(source);plan=json.loads((HERE/'plan.json').read_text())
derive_node=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='derive')
scope={'Path':Path,'re':re};exec(compile(ast.Module(body=[derive_node],type_ignores=[]),'<actual pure derive>','exec'),scope);derive=scope['derive'];checks=0
base=dict(schemaVersion=1,state='ROOT_NEXT_DIRECT_STANDALONE_CONTROL_AUTHORIZED_V1',runId='direct-test')
for k in ['hostOnlyDirectStandaloneAllowed','localhostServeAllowed','browserAllowed']:base[k]=True
for k in ['compilerAllowed','nativeBuildAllowed','engineAllowed','guestAllowed','componentConstructionAllowed','packageInstallAllowed','applicationSourceMutationAllowed','externalDeploymentAllowed','adoptionAllowed']:base[k]=False
for value in ['a','0','x'*48]:
 a=dict(base,runId=value);out,outer=derive(a,plan);assert str(out)==plan['outputPrefix']+'-'+value and str(outer)==str(out)+'-external-root';checks+=1
for value in [None,False,0,'','x'*49,'x\n','../x','x/y','x\\y','é','A']:
 try:derive(dict(base,runId=value),plan)
 except (AssertionError,TypeError):checks+=1
 else:raise AssertionError('accepted bad runId')
for change in [lambda a:a.update(schemaVersion=True),lambda a:a.update(state='other'),lambda a:a.update(guestAllowed=True),lambda a:a.update(browserAllowed=False),lambda a:a.update(argv=[]),lambda a:a.update(outputRoot='/other'),lambda a:a.update(environment={})]:
 a=deepcopy(base);change(a)
 try:derive(a,plan)
 except AssertionError:checks+=1
 else:raise AssertionError('accepted bad Root scope')
for change in [lambda p:p.update(outputPrefix='/other'),lambda p:p.update(outerSeconds=300),lambda p:p.update(minimumLaunchFreeBytes=0)]:
 p=deepcopy(plan);change(p)
 try:derive(base,p)
 except AssertionError:checks+=1
 else:raise AssertionError('accepted changed policy')
main=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='main')
calls=[x for x in ast.walk(main)if isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)and x.func.attr=='monitor'];assert len(calls)==1
seen=[]
class InertMonitor:
 def monitor(self,*args):seen.append(args);return 'inert'
env={'HOME':'/inert-home'};ref={'inert':'authority'};outer=Path('/inert-outer');auth=Path('/inert-authority')
value=eval(compile(ast.Expression(body=calls[0]),'<actual six-argument call>','eval'),dict(monitor=InertMonitor(),p=plan,HERE=HERE,authpath=auth,env=env,outer=outer,ref=ref))
assert value=='inert'and seen==[([plan['node']['path'],str(HERE/'control.mjs'),str(auth)],plan['cwd'],env,outer,600,ref)];checks+=1
assert source.index('free>=')<source.index('outer.mkdir')<source.index('terminal=monitor.monitor');checks+=1
assert 'finally:'in source and 'protect();preserved=True'in source;checks+=1
print(json.dumps(dict(sourceOnly=True,checks=checks,actualOwnerAstExcerpts=True,actualMonitorOrMkdirOrActorInvoked=False)))
