"""Actual inherited path guards + pure outcome predicates; no execute/auth call."""
from pathlib import Path
import copy
import importlib.util
import json
import tempfile

OWN = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('inert_als_sdk_guard_source', OWN / 'run-sdk-syntax.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def refused(callback):
    try: callback()
    except (AssertionError, FileNotFoundError): return
    raise AssertionError('Expected guard refusal')

plan = json.loads((OWN / 'sdk-plan.json').read_text())
guard = module.Protection()
ledger = guard.read(plan['references']['inputLedger'])['files']
aliases = guard.read(plan['references']['aliasInventory'])['symlinks']
counts=[]
for tree in plan['protectedTrees']:
    root=Path(tree['path'])
    rows=[r for r in ledger if Path(r['path']).is_relative_to(root) and '.git' not in Path(r['path']).relative_to(root).parts]
    links=[r for r in aliases if Path(r['path']).is_relative_to(root)]
    assert len(rows)==tree['regularFiles'] and len(links)==tree['symlinks']
    guard.tree(root,rows,links)
    counts.append({'root':str(root),'files':len(rows),'aliases':len(links)})
for policy in plan['absentIncludePolicies']: guard.absent_include(policy)
assert guard.recheck()['unchanged']

checks=0
with tempfile.TemporaryDirectory(prefix='als-v2-guard-') as name:
    root=Path(name).resolve()
    file=root/'input';file.write_bytes(b'ordinary non-secret source DATA')
    checked=module.descriptor(file);module.Protection().checked(checked);checks+=1
    refused(lambda:module.Protection().checked(dict(checked,sha256='0'*64)));checks+=1
    link=root/'alias';link.symlink_to(file)
    refused(lambda:module.Protection().checked(dict(checked,path=str(link))));checks+=1
    missing=root/'missing'/'include'
    before=module.absence_snapshot(missing);assert before['missingComponents']==[str(root/'missing'),str(missing)];checks+=1
    refused(lambda:module.absence_snapshot(file));checks+=1
    present=root/'present';present.mkdir()
    refused(lambda:module.absence_snapshot(present));checks+=1
    alias=root/'directory-alias';alias.symlink_to(root,target_is_directory=True)
    refused(lambda:module.absence_snapshot(alias/'missing'));checks+=1
    dangling=root/'dangling';dangling.symlink_to(root/'unknown')
    refused(lambda:module.absence_snapshot(dangling));checks+=1

terminal={'allObservedOwnedGroupsGone':True,'parentOwnedGroupGone':True,'forcedCleanup':False,
          'timeout':False,'signals':[],'interruptedSignals':[],'errors':[],'remainingObservedPids':[],
          'rawExitCode':0}
record={'terminal':terminal,'startedArgvMatches':True,'raw':{'started':1,'stdout':1,'stderr':1,'terminal':1},
        'commandError':None,'dependencyError':None,'protectionBefore':{'unchanged':True},'protectionAfter':{'unchanged':True}}
rows=[copy.deepcopy(record)for _ in range(13)]
assert module.frontend_passed(None,{'unchanged':True},rows);checks+=1
for key,value in [('rawExitCode',1),('timeout',True),('forcedCleanup',True),('errors',['error']),
                  ('signals',[15]),('interruptedSignals',[2]),('interruptedSignals',[15]),
                  ('remainingObservedPids',[7]),('allObservedOwnedGroupsGone',False),('parentOwnedGroupGone',False)]:
    changed=copy.deepcopy(rows);changed[0]['terminal'][key]=value
    assert not module.frontend_passed(None,{'unchanged':True},changed);checks+=1
for key,value in [('terminal',None),('startedArgvMatches',False),('raw',{}),('commandError','spawn'),
                  ('dependencyError','unobserved header'),('protectionBefore',{'unchanged':False}),('protectionAfter',{'unchanged':False})]:
    changed=copy.deepcopy(rows);changed[0][key]=value
    assert not module.frontend_passed(None,{'unchanged':True},changed);checks+=1
assert not module.frontend_passed(None,{'unchanged':False},rows);checks+=1
assert not module.frontend_passed('exception',{'unchanged':True},rows);checks+=1
assert not module.frontend_passed(None,{'unchanged':True},rows[:-1]);checks+=1
assert not module.frontend_passed(None,{'unchanged':True},rows+[record]);checks+=1
assert module.parse_dependencies('unit: first\\ path second\\\n third\n','unit')==['first path','second','third'];checks+=1
refused(lambda:module.parse_dependencies('wrong: header','unit'));checks+=1
refused(lambda:module.parse_dependencies('unit: a a','unit'));checks+=1
print(json.dumps({'schemaVersion':1,'state':'ALS_SDK_REAL_GUARD_AND_PURE_OUTCOME_CHECKS_PASSED',
                  'actualTrees':counts,'actualGuardedFiles':sum(r['files']for r in counts),
                  'actualAliases':sum(r['aliases']for r in counts),'absentIncludePolicies':len(plan['absentIncludePolicies']),
                  'syntheticChecks':checks,'finalCurrentProtection':guard.recheck(),
                  'compilerOrMonitorOrAuthenticateExecuteInvoked':False}))
