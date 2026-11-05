"""Extracted pure contract seams only; no controller/module/API action import."""
import ast,copy,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
DONOR=REPO/'tests/node-compat/foundation-scheduler/combined-native-stage-controller-candidate-v1'
INTEGRATION=REPO/'tests/node-compat/foundation-scheduler/independent-combined355-native-integration-source-review-v1'
text=(DONOR/'controller.py').read_text()
names={'source_peer_model','stage_peer_model','terminal_model'}
scope=dict(SOURCE_SHA='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65',MONITOR_SHA='0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
exec(compile(ast.Module(body=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<real-extracted-contract-models>','exec'),scope)
checks=0
def passed():
    global checks
    checks+=1
def refused(fn):
    try:fn()
    except (AssertionError,KeyError,TypeError):passed();return
    raise AssertionError('Negative contract accepted')
integration=json.loads((INTEGRATION/'results.json').read_text())
controller=json.loads((HERE/'results.json').read_text())
own=controller['sourceIndex']
scope['source_peer_model'](integration);passed()
scope['stage_peer_model'](controller,own);passed()
for source,name,field,value in [(integration,'source_peer_model','nativeSourceFiles',342),(integration,'source_peer_model','operationalAdmission',True),(integration,'source_peer_model','sourceIndexSha256','0'*64),(controller,'stage_peer_model','controllerSourceIndexSha256','0'*64),(controller,'stage_peer_model','sourceStageActionsInvoked',True),(controller,'stage_peer_model','genericMonitorSourceIndexSha256','0'*64)]:
    v=copy.deepcopy(source);v[field]=value
    refused(lambda v=v,name=name:scope[name](v,*([own] if name=='stage_peer_model' else [])))
authority=dict(path='/synthetic/no-file/Root.json',sha256='0'*64,bytes=1)
terminal=dict(authority=authority,rawExitCode=0,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,timeout=False,forcedCleanup=False,interruptedSignals=[],remainingObservedPids=[],signals=[],errors=[],stderr=dict(bytes=0),observedProcesses=[dict(pid=1)],finalGroups=[dict(alive=False)])
scope['terminal_model'](terminal,authority);passed()
for field,value in [('rawExitCode',1),('timeout',True),('forcedCleanup',True),('parentOwnedGroupGone',False),('allObservedOwnedGroupsGone',False),('remainingObservedPids',[1]),('errors',[{}]),('signals',[{}]),('interruptedSignals',[2]),('stderr',dict(bytes=1)),('observedProcesses',[]),('finalGroups',[])]:
    v=copy.deepcopy(terminal);v[field]=value;refused(lambda v=v:scope['terminal_model'](v,authority))
v=copy.deepcopy(terminal);v['finalGroups'][0]['alive']=True;refused(lambda:scope['terminal_model'](v,authority))
print(json.dumps(dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_REAL_PURE_PEER_AND_TERMINAL_CONTRACTS_PASSED',checks=checks,realReviewResultShapesChecked=2,syntheticTerminalsOnly=True,ownerModulesImported=False,ownerActionsInvoked=False)))
