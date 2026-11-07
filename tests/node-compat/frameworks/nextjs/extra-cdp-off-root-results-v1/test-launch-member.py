"""Read-only prepared requests and inert DATA/callbacks; never main/actor."""
import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extra_off_source', HERE / 'launch-member.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
utility = gate.load_utility()
owner = gate.load_owner(utility)
members = json.loads((HERE / 'prepared-members-v2.json').read_text())['members']
self_ref = utility.row(HERE / 'launch-member.py')
protocol = dict(state='ROOT_EXTRA_CDP_OFF_DIAGNOSTIC_DECLARED_V1', driver=self_ref, utility=gate.UTILITY,
    minimumFreeBytes=gate.MINIMUM, prerequisiteReviewIndexes=gate.PREREQUISITES,
    sharedInputs=[gate.pin(p) for p in gate.PINS], members=members)
checks = 0
assert gate.validate_protocol(protocol, self_ref, utility, owner.derive_invocation, utility.read) == members
checks += 1
for ref in gate.PREREQUISITES:
    utility.family(ref)
    checks += 1
for mutate in [
    lambda p: p.update(state='other'), lambda p: p.update(minimumFreeBytes=0),
    lambda p: p.update(driver={}), lambda p: p.update(utility={}),
    lambda p: p['prerequisiteReviewIndexes'].pop(), lambda p: p['prerequisiteReviewIndexes'].reverse(),
    lambda p: p['sharedInputs'].pop(), lambda p: p['sharedInputs'].append(p['sharedInputs'][0]),
    lambda p: p['members'].reverse(), lambda p: p['members'][0].update(arm='native'),
    lambda p: p['members'][0].update(runId='bad\n'), lambda p: p['members'][0].update(runId='../path'),
    lambda p: p['members'][1].update(runId=p['members'][0]['runId']),
    lambda p: p['members'][0]['argv'].append('--override'),
    lambda p: p['members'][0].update(cwd='/arbitrary'),
    lambda p: p['members'][0].update(outputRoot='/arbitrary'),
    lambda p: p['members'][0].update(monitorOutputRoot='/arbitrary'),
    lambda p: p['members'][0].update(observation='/arbitrary'),
    lambda p: p['members'][0].update(worldGuardReceipt='/arbitrary'),
]:
    changed = deepcopy(protocol)
    mutate(changed)
    try:
        gate.validate_protocol(changed, self_ref, utility, owner.derive_invocation, utility.read)
    except (AssertionError, KeyError, TypeError):
        checks += 1
    else:
        raise AssertionError('Invalid protocol accepted')
member = members[0]
authority = utility.read(member['authority'])
plan = utility.read(authority['plans'])
for mutate in [
    lambda a: a.update(localhostServerAllowed=None), lambda a: a.update(browserAllowed=None),
    lambda a: a.update(guestAllowed=True), lambda a: a.update(unissued=True),
    lambda a: a.update(rootLaunchMinimumFreeBytes=0), lambda a: a.update(outputRoot='/override'),
    lambda a: a['sourceIndex'].update(sha256='0'*64), lambda a: a['plans'].update(sha256='0'*64),
]:
    changed = deepcopy(authority)
    mutate(changed)
    try:
        gate.member_layout(member, changed, plan, owner.derive_invocation, utility)
    except (AssertionError, KeyError):
        checks += 1
    else:
        raise AssertionError('Invalid authority accepted')


def completion_fixture(code):
    ref = lambda p: dict(path=p, sha256='0'*64, bytes=0)
    observation = dict(state='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_OBSERVATION_V1', arm='stock',
        runId=member['runId'], outputRoot=member['outputRoot'], rawExitCode=code,
        ownedGroupsClean=True, protectedInputsPreserved=True, hostExperimentPassed=code == 0,
        guestOrNativeExecuted=False, terminal=ref(str(Path(member['monitorOutputRoot']) / 'terminal.json')),
        result=ref(str(Path(member['outputRoot']) / 'result.json')))
    terminal = dict(schemaVersion=1, rawExitCode=code, authority=member['authority'], timeout=False,
        forcedCleanup=False, parentOwnedGroupGone=True, allObservedOwnedGroupsGone=True,
        errors=[], signals=[], interruptedSignals=[], remainingObservedPids=[])
    result = dict(suite='FULL_NEXT_STOCK_ORIGINAL_MODULE_BRIDGE_HYDRATION_BROWSER_CONTROL_V1',
        prepared=True, originalApplicationInputsPreserved=True, guestExecuted=False,
        applicationModified=False, passed=code == 0)
    return observation, terminal, result


for code in [0, 1]:
    data = completion_fixture(code)
    status = utility.prior_status(member, authority, *data, None)
    assert status['functionalPassed'] is (code == 0)
    checks += 1
for mutate in [
    lambda o, t, r: o.update(rawExitCode=2), lambda o, t, r: t.update(rawExitCode=True),
    lambda o, t, r: t.update(timeout=True), lambda o, t, r: t.update(forcedCleanup=True),
    lambda o, t, r: t.update(interruptedSignals=[2]), lambda o, t, r: t.update(signals=[{}]),
    lambda o, t, r: t.update(errors=['unknown']), lambda o, t, r: t.update(remainingObservedPids=[1]),
    lambda o, t, r: t.update(parentOwnedGroupGone=False), lambda o, t, r: t.update(allObservedOwnedGroupsGone=False),
    lambda o, t, r: o.update(protectedInputsPreserved=False), lambda o, t, r: t.update(authority={}),
    lambda o, t, r: r.update(originalApplicationInputsPreserved=False), lambda o, t, r: r.update(passed=False),
]:
    data = completion_fixture(0)
    mutate(*data)
    try:
        utility.prior_status(member, authority, *data, None)
    except (AssertionError, KeyError):
        checks += 1
    else:
        raise AssertionError('Unclean original completion accepted')
protocol_ref = dict(path='/inert/protocol.json', sha256='1'*64, bytes=1)
admission = dict(state='EXTRA_CDP_OFF_SINGLE_MEMBER_ADMITTED_V1', protocol=protocol_ref, driver=self_ref,
    utility=gate.UTILITY, member=member, oneCommandOnly=True, automaticNextOrRetry=False, originalCohortAcceptance=False)
completion = dict(state='EXTRA_CDP_OFF_SINGLE_CLI_RETURN_CAPTURED_V1', memberId=member['id'], rawCliExitCode=1,
    error=None, postProtectionError=None, registrySharedAndPriorRecordsPreserved=True,
    automaticNextOrRetry=False, functionalPassNotInferred=True, originalCohortAcceptance=False)
gate.prior_cli_status(member, protocol_ref, self_ref, admission, completion, 1)
checks += 1
for mutate in [
    lambda a, c: c.update(error={'unknown': True}), lambda a, c: c.update(postProtectionError={}),
    lambda a, c: c.update(registrySharedAndPriorRecordsPreserved=False),
    lambda a, c: c.update(rawCliExitCode=0), lambda a, c: c.update(rawCliExitCode=True),
    lambda a, c: a.update(protocol={}), lambda a, c: a.update(driver={}),
    lambda a, c: a.update(oneCommandOnly=False), lambda a, c: c.update(automaticNextOrRetry=True),
    lambda a, c: c.update(functionalPassNotInferred=False), lambda a, c: c.update(originalCohortAcceptance=True),
]:
    a, c = deepcopy(admission), deepcopy(completion)
    mutate(a, c)
    try:
        gate.prior_cli_status(member, protocol_ref, self_ref, a, c, 1)
    except AssertionError:
        checks += 1
    else:
        raise AssertionError('Invalid own-launcher completion accepted')
paths = gate.require_fresh(member, lambda _: False, gate.MINIMUM)
checks += 1
for free in [0, gate.MINIMUM - 1]:
    try:
        gate.require_fresh(member, lambda _: False, free)
    except AssertionError:
        checks += 1
    else:
        raise AssertionError('Low capacity accepted')
for path in paths:
    try:
        gate.require_fresh(member, lambda value: value == path, gate.MINIMUM)
    except AssertionError:
        checks += 1
    else:
        raise AssertionError('Existing or dangling output accepted')
source = (HERE / 'launch-member.py').read_text()
tree = ast.parse(source)
calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
         and isinstance(n.func.value, ast.Name) and n.func.value.id == 'subprocess' and n.func.attr == 'run']
assert len(calls) == 1 and not any(k.arg == 'shell' for k in calls[0].keywords)
seen = []
class InertSubprocess:
    @staticmethod
    def run(*args, **kwargs):
        seen.append((args, kwargs))
        return object()
eval(compile(ast.Expression(body=calls[0]), '<actual one-command expression>', 'eval'),
     dict(subprocess=InertSubprocess, selected=member, out='inert-stdout', err='inert-stderr'))
assert seen == [((member['argv'],), dict(cwd=member['cwd'], stdout='inert-stdout', stderr='inert-stderr', check=False))]
checks += 1
assert source.index('require_fresh(selected,') < source.index('logs.mkdir(mode=0o700)') < source.index('code = subprocess.run(')
checks += 1
audit = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'audit_completed')
assert not any(isinstance(n, ast.Attribute) and n.attr in ['run', 'mkdir', 'durable'] for n in ast.walk(audit))
assert "through_id='off3'" in source and 'members[:end + 1]' in source
checks += 1
print(json.dumps(dict(sourceOnly=True, checks=checks, actualPreparedV2RequestsReadOnly=True,
    exactOriginalUtilitiesAndGenuineOwnerSelectorUsed=True, syntheticCompletionDataOnly=True,
    raw1CleanRetainedAsFunctionalFailure=True, oneSubprocessExpressionWithInertCallback=True,
    actualProtocolGrantActorCopyOrRuntimeCreated=False)))
