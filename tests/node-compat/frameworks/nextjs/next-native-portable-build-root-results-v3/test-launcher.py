"""Inert launcher policy/control-flow tests; never call run or any monitor."""
from pathlib import Path
import ast
import copy
import importlib.util
import json

HERE = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location('inert_portable_root_launcher', HERE / 'launch.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
checks = 0


def check(value):
    global checks
    assert value
    checks += 1


def refuses(call):
    global checks
    try:
        call()
    except ValueError:
        checks += 1
    else:
        raise AssertionError('Expected refusal')


draft = json.loads((HERE / 'authority.unissued.json').read_text())
before = copy.deepcopy(draft)
issued = m.issued_copy(draft)
check(draft == before)
check({k for k in issued if issued[k] != draft[k]} == {'state', 'configureAllowed', 'buildAllowed'})
check(issued['configureAllowed'] is issued['buildAllowed'] is True)
for key in ['engineOrGuestExecutionAllowed', 'freezeAllowed', 'networkAllowed', 'rustupAllowed']:
    check(issued[key] is False)
for key, value in [('state', 'ROOT_ALREADY_ISSUED'), ('configureAllowed', True), ('buildAllowed', False)]:
    bad = copy.deepcopy(draft)
    bad[key] = value
    refuses(lambda: m.issued_copy(bad))
refuses(lambda: m.capacity(3 * 1024**3 - 1, 3 * 1024**3))
m.capacity(3 * 1024**3, 3 * 1024**3)
check(True)
env = dict(HOME='/original-home', home='/lower-home', CODEX_HOME='/codex-home', USER='fixture',
           PATH='/fixture', NODE_OPTIONS='untrusted', PYTHONPATH='untrusted', TOKEN='not-forwarded')
selected = m.outer_environment(env)
check(all(selected[k] == env[k] for k in ['HOME', 'home', 'CODEX_HOME', 'USER', 'PATH']))
check(not any(k in selected for k in ['NODE_OPTIONS', 'PYTHONPATH', 'TOKEN']))
check(env['HOME'] == '/original-home' and selected['PYTHONDONTWRITEBYTECODE'] == '1')
terminal = dict(rawExitCode=0, parentOwnedGroupGone=True, allObservedOwnedGroupsGone=True,
                timeout=False, forcedCleanup=False, errors=[], signals=[], interruptedSignals=[],
                remainingObservedPids=[], finalGroups=[dict(alive=False)])
check(m.terminal_clean(terminal))
for key, value in [('rawExitCode', 1), ('rawExitCode', False), ('timeout', True), ('forcedCleanup', True),
                  ('parentOwnedGroupGone', False), ('allObservedOwnedGroupsGone', False),
                  ('errors', ['e']), ('signals', ['s']), ('interruptedSignals', [2]),
                  ('remainingObservedPids', [123]), ('finalGroups', [dict(alive=True)])]:
    bad = copy.deepcopy(terminal)
    bad[key] = value
    check(m.terminal_clean(bad) is False)
source = (HERE / 'launch.py').read_text()
tree = ast.parse(source)
run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
calls = list(ast.walk(run))
capacity_lines = sorted(n.lineno for n in calls if isinstance(n, ast.Call)
                        and isinstance(n.func, ast.Name) and n.func.id == 'capacity')
input_line = next(n.lineno for n in calls if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'inputs')
mkdir_line = next(n.lineno for n in calls if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'mkdir')
monitor_line = next(n.lineno for n in calls if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'monitor')
save_lines = [n.lineno for n in calls if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'save']
check(len(capacity_lines) == 2 and capacity_lines[0] < input_line < capacity_lines[1] < mkdir_line < min(save_lines) < monitor_line)
outer_try = next(n for n in run.body if isinstance(n, ast.Try))
check(bool(outer_try.finalbody))
final_text = '\n'.join(ast.get_source_segment(source, n) for n in outer_try.finalbody)
check('for r in protected' in final_text and 'module.portable_admission(a, plan)' in final_text)
check('module.recheck_cargo(a, plan, cargo_before)' in final_text)
check('module.save(output / \'observation.json\', result)' in final_text)
check('automaticRetry=False' in source and "plan['timeouts']['build']" in source)
print(json.dumps(dict(state='PORTABLE_ROOT_LAUNCHER_INERT_TESTS_PASSED_V3', checks=checks,
    runOrMonitorOrToolsInvoked=False, fakeExecutionPerformed=False, authorityIssued=False)))
