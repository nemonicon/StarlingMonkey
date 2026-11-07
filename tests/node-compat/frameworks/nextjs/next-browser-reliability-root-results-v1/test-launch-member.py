"""Read-only Source joins and synthetic completion DATA; no main/actor called."""
import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('inert_member_source',HERE/'launch-member.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
members=json.loads((HERE/'prepared-members.json').read_text())['members']
self_ref=gate.row(HERE/'launch-member.py');checks=0
prerequisite=dict(path=str(HERE.parent/'next-app-runtime-root-results-v1/first-pair-review/index.json'),
 sha256='83988ce92d3c5bed1779a7d348a7dbc59f6843945bbc4145a7708d92b1b6689c',bytes=1712)
registry=dict(state='ROOT_NEXT_BROWSER_COHORT_PREDECLARED_V1',launcher=self_ref,minimumFreeBytes=gate.MINIMUM,
 prerequisiteReviewIndex=prerequisite,sharedInputs=[gate.pin(p) for p in gate.PINS],members=members)
# This is in-memory test DATA, never a registry or grant publication.
assert gate.validate_registry(registry,self_ref)==members;checks+=1
gate.family(prerequisite);checks+=1
for change in [
 lambda r:r.update(state='other'),lambda r:r.update(minimumFreeBytes=0),
 lambda r:r['launcher'].update(sha256='0'*64),lambda r:r['members'].reverse(),
 lambda r:r['members'][1].update(runId=r['members'][0]['runId']),
 lambda r:r['members'][0].update(runId='bad\n'),lambda r:r['members'][0].update(arm='native'),
 lambda r:r['members'][0]['argv'].append('--other'),lambda r:r['members'][0].update(outputRoot='/arbitrary'),
 lambda r:r['members'][1].update(worldGuardReceipt='/arbitrary'),lambda r:r['members'][0].update(observation='/arbitrary'),
 lambda r:r['sharedInputs'].pop(),lambda r:r['members'][0].update(cwd='/arbitrary'),
]:
    r=deepcopy(registry);change(r)
    try:gate.validate_registry(r,self_ref)
    except (AssertionError,KeyError):checks+=1
    else:raise AssertionError('Accepted registry mutation')
for member in [members[0],members[1]]:
    authority=gate.read(member['authority']);plan=gate.read(authority['plans'] if member['arm']=='stock' else authority['plan'])
    gate.member_layout(member,authority,plan);checks+=1
    a=deepcopy(authority)
    if member['arm']=='stock':a['guestAllowed']=True
    else:a['component']['sha256']='0'*64
    try:gate.member_layout(member,a,plan)
    except AssertionError:checks+=1
    else:raise AssertionError('Accepted authority mutation')
def fixture(member,code=0):
    authority=gate.read(member['authority']);ref=lambda p:dict(path=p,sha256='0'*64,bytes=0)
    obs=dict(rawExitCode=code,ownedGroupsClean=True,protectedInputsPreserved=True,
      terminal=ref(str(Path(member['monitorOutputRoot'])/'terminal.json')),result=ref(str(Path(member['outputRoot'])/'result.json')),
      runId=member['runId'],outputRoot=member['outputRoot'])
    terminal=dict(schemaVersion=1,rawExitCode=code,authority=member['authority'],timeout=False,forcedCleanup=False,
      parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,errors=[],signals=[],interruptedSignals=[],remainingObservedPids=[])
    if member['arm']=='stock':
        obs.update(state='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_OBSERVATION_V1',arm='stock',hostExperimentPassed=code==0,guestOrNativeExecuted=False)
        result=dict(suite='FULL_NEXT_STOCK_ORIGINAL_MODULE_BRIDGE_HYDRATION_BROWSER_CONTROL_V1',prepared=True,
          originalApplicationInputsPreserved=True,guestExecuted=False,applicationModified=False,passed=code==0)
        world=None
    else:
        obs.update(state='ROOT_NEXT_WASMTIME_DEPLOYMENT_OBSERVATION_V2',passed=code==0)
        result=dict(state='NEXT_WASMTIME_DEPLOYMENT_CONTRACTS_PASSED_UNREVIEWED_V2' if code==0 else 'NEXT_WASMTIME_DEPLOYMENT_FAILED_UNACCEPTED_V2',
          passed=code==0,originalInputsPreserved=True,readonlyAppPreserved=True,rootAuthority=member['authority'],sourceIndex=authority['sourceIndex'],
          component=authority['component'],runId=member['runId'],server=dict(shutdownRequested=True,sigintSent=True,forcedCleanup=False,exit=dict(code=0,signal=None,error=None)))
        world=dict(before=dict(sourceIndex=authority['worldSourceIndex']),after=dict(sourceIndex=authority['worldSourceIndex']),
          unchanged=True,nativeInputsPreserved=True,authority=member['authority'])
    return authority,obs,terminal,result,world
for member in [members[0],members[1]]:
    for code in [0,1]:
        status=gate.prior_status(member,*fixture(member,code));assert status['functionalPassed']==(code==0);checks+=1
    for change in [
      lambda a,o,t,r,w:o.update(rawExitCode=2),lambda a,o,t,r,w:t.update(rawExitCode=True),
      lambda a,o,t,r,w:t.update(timeout=True),lambda a,o,t,r,w:t.update(forcedCleanup=True),
      lambda a,o,t,r,w:t.update(interruptedSignals=[2]),lambda a,o,t,r,w:t.update(errors=['unknown']),
      lambda a,o,t,r,w:t.update(signals=[{}]),lambda a,o,t,r,w:t.update(remainingObservedPids=[1]),
      lambda a,o,t,r,w:t.update(allObservedOwnedGroupsGone=False),lambda a,o,t,r,w:o.update(protectedInputsPreserved=False),
      lambda a,o,t,r,w:t.update(authority={}),lambda a,o,t,r,w:o['terminal'].update(path='/arbitrary'),
      lambda a,o,t,r,w:r.update(passed=False),
    ]:
        data=fixture(member);change(*data)
        try:gate.prior_status(member,*data)
        except (AssertionError,KeyError):checks+=1
        else:raise AssertionError('Accepted unsafe completion')
member=members[1]
for change in [lambda a,o,t,r,w:w.update(unchanged=False),lambda a,o,t,r,w:w.update(nativeInputsPreserved=False),
 lambda a,o,t,r,w:w.update(after={}),lambda a,o,t,r,w:r.update(readonlyAppPreserved=False),
 lambda a,o,t,r,w:r['server']['exit'].update(signal='SIGKILL')]:
    data=fixture(member);change(*data)
    try:gate.prior_status(member,*data)
    except AssertionError:checks+=1
    else:raise AssertionError('Accepted native protection mutation')
cohort_ref=dict(path='/inert/cohort.json',sha256='1'*64,bytes=1);member=members[0]
admission=dict(state='COHORT_SINGLE_MEMBER_ADMITTED_V1',cohort=cohort_ref,launcher=self_ref,member=member,oneCommandOnly=True,automaticNextOrRetry=False)
completion=dict(state='COHORT_SINGLE_CLI_RETURN_CAPTURED_V1',memberId=member['id'],error=None,registrySharedAndPriorRecordsPreserved=True,
 rawCliExitCode=0,automaticNextOrRetry=False,functionalPassNotInferred=True)
gate.prior_cli_status(member,cohort_ref,self_ref,admission,completion,0);checks+=1
for change in [lambda a,c:c.update(error={'unknown':True}),lambda a,c:c.update(registrySharedAndPriorRecordsPreserved=False),
 lambda a,c:c.update(rawCliExitCode=1),lambda a,c:c.update(rawCliExitCode=False),lambda a,c:a.update(cohort={}),
 lambda a,c:a.update(oneCommandOnly=False),lambda a,c:c.update(memberId='other')]:
    a=deepcopy(admission);c=deepcopy(completion);change(a,c)
    try:gate.prior_cli_status(member,cohort_ref,self_ref,a,c,0)
    except AssertionError:checks+=1
    else:raise AssertionError('Accepted prior launcher error/protection mismatch')
for member in [members[0],members[1]]:
    gate.require_fresh(member,lambda _:False,gate.MINIMUM);checks+=1
    try:gate.require_fresh(member,lambda _:False,gate.MINIMUM-1)
    except AssertionError:checks+=1
    else:raise AssertionError('Accepted low space')
    for selected in [member['outputRoot'],member['monitorOutputRoot'],str(gate.HERE/(member['id']+'-launcher'))]+([member['worldGuardReceipt']] if member['worldGuardReceipt'] else []):
        try:gate.require_fresh(member,lambda p:p==selected,gate.MINIMUM)
        except AssertionError:checks+=1
        else:raise AssertionError('Accepted existing output/receipt/admission')
missing=deepcopy(members[0]);missing['observation']=str(HERE/'deliberately-uncreated-observation-test.json')
try:gate.prior_records(missing,cohort_ref,self_ref)
except FileNotFoundError:checks+=1
else:raise AssertionError('Unexpected original future member data exists')
source=(HERE/'launch-member.py').read_text();tree=ast.parse(source)
calls=[x for x in ast.walk(tree) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and isinstance(x.func.value,ast.Name) and x.func.value.id=='subprocess' and x.func.attr=='run']
assert len(calls)==1 and not any(k.arg=='shell' for k in calls[0].keywords);checks+=1
assert source.index('require_fresh(selected,')<source.index("logs.mkdir(mode=0o700)")<source.index('code=subprocess.run(');checks+=1
print(json.dumps(dict(sourceOnly=True,checks=checks,actualPreparedInputsReadOnly=True,completionFixturesSynthetic=True,
                     raw1RemainsFunctionalFailure=True,ownCliProtectionFailureRefuses=True,
                     actualRegistryOrGrantOrActorOrCopyOrRuntimeCreated=False)))
