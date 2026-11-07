"""Actual AST excerpts with inert paths/monitor callback; no filesystem action."""
import ast
import json
from pathlib import Path, PurePosixPath
import re

HERE=Path(__file__).resolve().parent
text=(HERE/'run-owned.py').read_text();tree=ast.parse(text)
helper=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='derive_invocation')
plan=json.loads((HERE/'plans.json').read_text());checks=0
def make(path_type=Path):
    scope={'Path':path_type,'re':re}
    exec(compile(ast.Module(body=[helper],type_ignores=[]),'<actual pure selector>','exec'),scope)
    return scope['derive_invocation']
derive=make();base={'state':'ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1','arm':'stock','runId':'pair-1-node'}
for value in ['a','0','x'*48,'pair-3-node']:
    a=dict(base,runId=value);output,monitor,argv=derive(a,plan,HERE)
    assert str(output)==plan['outputPrefix']+'-'+value and str(monitor)==str(output)+'-monitor'
    assert argv==[plan['node']['path'],str(HERE/'run-stock.mjs'),str(output),plan['standaloneSource'],plan['browserTools'],value]
    checks+=1
# The unchanged native runId alphabet allows this spelling collision. The
# exclusive collision block below must refuse it, never choose another path.
_,first_monitor,_=derive(dict(base,runId='pair'),plan,HERE)
second_output,_,_=derive(dict(base,runId='pair-monitor'),plan,HERE)
assert first_monitor==second_output;checks+=1
bad=[None,False,0,[],{},'', 'x'*49,'../x','x/y','x\\y','x\n','\nx','é','A','x.y',' x','x ','x\x00','a\tb','-x','_x','$(echo x)']
for value in bad:
    try:derive(dict(base,runId=value),plan,HERE)
    except (AssertionError,TypeError):checks+=1
    else:raise AssertionError(('accepted runId',repr(value)))
for change in [lambda a:a.pop('runId'),lambda a:a.update(state='other'),lambda a:a.update(arm='selected'),
               lambda a:a.update(outputRoot='/arbitrary'),lambda a:a.update(monitorOutputRoot=None),lambda a:a.update(argv=[])]:
    a=dict(base);change(a)
    try:derive(a,plan,HERE)
    except (AssertionError,KeyError):checks+=1
    else:raise AssertionError('accepted invalid authority')
for change in [lambda p:p.update(outputPrefix='/arbitrary'),lambda p:p['arms']['stock'].update(outputRoot='/arbitrary'),lambda p:p['arms']['stock'].update(timeoutSeconds=301)]:
    p=json.loads(json.dumps(plan));change(p)
    try:derive(base,p,HERE)
    except AssertionError:checks+=1
    else:raise AssertionError('accepted plan override')
main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
start=next(i for i,x in enumerate(main.body) if isinstance(x,ast.Assign) and isinstance(x.value,ast.Call) and isinstance(x.value.func,ast.Name) and x.value.func.id=='derive_invocation')
block=main.body[start:start+3] # Actual derive, collision assertion, exclusive mkdir.
assert isinstance(block[1],ast.Assert) and isinstance(block[2],ast.Expr)
class InertPath:
    state={};calls=[]
    def __init__(self,value):self.value=str(value)
    def __str__(self):return self.value
    def __truediv__(self,value):return InertPath(str(PurePosixPath(self.value)/value))
    def exists(self):return self.state.get(self.value,{}).get('exists',False)
    def is_symlink(self):return self.state.get(self.value,{}).get('symlink',False)
    def mkdir(self,mode):
        self.calls.append((self.value,mode))
        if self.state.get(self.value,{}).get('race',False):raise FileExistsError('inert collision')
fake_derive=make(InertPath)
for target,kind in [('output','exists'),('monitor','exists'),('output','symlink'),('monitor','symlink'),('monitor','race'),(None,None)]:
    prefix=plan['outputPrefix']+'-'+base['runId'];path=prefix+('-monitor' if target=='monitor' else '')
    InertPath.state={} if target is None else {path:{kind:True}};InertPath.calls=[]
    scope={'authority':base,'plan':plan,'HERE':InertPath(HERE),'derive_invocation':fake_derive}
    failed=False
    try:exec(compile(ast.Module(body=block,type_ignores=[]),'<actual collision block>','exec'),scope)
    except (AssertionError,FileExistsError):failed=True
    assert failed==(target is not None)
    if kind!='race' and target is not None:assert InertPath.calls==[]
    if target is None:assert InertPath.calls==[(prefix+'-monitor',0o700)]
    checks+=1
# Exercise the genuine six-argument CALL EXPRESSION with an inert callback only.
call=next(x.value for x in main.body if isinstance(x,ast.Assign) and isinstance(x.value,ast.Call) and isinstance(x.value.func,ast.Attribute) and x.value.func.attr=='monitor')
seen=[]
class InertMonitor:
    def monitor(self,*args):seen.append(args);return 'inert-return'
output,monitor,argv=derive(base,plan,HERE);authority_ref={'inertAuthorityDigest':'kept'}
value=eval(compile(ast.Expression(body=call),'<actual monitor-call expression>','eval'),dict(monitor=InertMonitor(),argv=argv,plan=plan,env={'inert':'environment'},monitor_output=monitor,authority_ref=authority_ref))
assert value=='inert-return' and seen==[(argv,plan['cwd'],{'inert':'environment'},monitor,300,authority_ref)];checks+=1
assert text.count('verify(authority_ref)')==2
print(json.dumps(dict(sourceOnly=True,namespaceChecks=checks,actualAstExcerpts=True,rawOrDanglingCollisionsRefuse=True,
                     argvAndOriginalSixArgumentCallChecked=True,actualMonitorOrPathMkdirOrActorInvoked=False)))
