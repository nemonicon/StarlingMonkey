"""Real interpreter flags + inert guard DATA; no actor/tool/restorer invocation."""
from pathlib import Path
import ast
import importlib.util
import json
import sys
from types import SimpleNamespace

HERE = Path(__file__).absolute().parent
OLD = HERE.with_name('native-cargo-offline-verify-v1')
checks = 0


def check(value):
    global checks
    checks += 1
    assert value is True


def guards(path):
    tree = ast.parse(path.read_text())
    return [n.args[0] for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == 'need' and len(n.args) == 2 and isinstance(n.args[1], ast.Constant)
            and n.args[1].value in ['Python -I -B with assertions', 'private worker Python -I -B']]


spec = importlib.util.spec_from_file_location('metadata_verifier_v2_flags', HERE / 'run.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
old = guards(OLD / 'run.py'); new = guards(HERE / 'run.py')
check(len(old) == len(new) == 2)
check(__debug__ is True and sys.dont_write_bytecode is True and sys.flags.isolated == 1)
for before, after in zip(old, new):
    original = eval(compile(ast.Expression(before), '<exact-v1-flags>', 'eval'), {'sys': sys})
    corrected = eval(compile(ast.Expression(after), '<exact-v2-flags>', 'eval'), {'sys': sys})
    check(type(original) is int and original == 1)
    check(type(corrected) is bool and corrected is True)
    try:
        m.need(original, 'preserved V1 strict-identity counterexample')
    except ValueError:
        checks += 1
    else:
        raise AssertionError('Old int1 unexpectedly accepted by strict need')
    m.need(corrected, 'actual corrected -I -B predicate'); checks += 1
    for isolated, dont_write, expected in [(0, True, False), (1, False, False), (0, False, False), (1, True, True)]:
        inert = SimpleNamespace(dont_write_bytecode=dont_write, flags=SimpleNamespace(isolated=isolated))
        value = eval(compile(ast.Expression(after), '<inert-v2-flags>', 'eval'), {'sys': inert})
        check(type(value) is bool and value is expected)
# Exact finite executable delta; no changed private dispatch, command, result or ownership wire.
previous = (OLD / 'run.py').read_text()
expected = previous.replace('__debug__ and sys.dont_write_bytecode and sys.flags.isolated',
                            '__debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1')
check((HERE / 'run.py').read_text() == expected)
check((HERE / 'root-authority.template.json').read_bytes() == (OLD / 'root-authority.template.json').read_bytes())
plan = json.loads((HERE / 'plan.json').read_text()); previous_plan = json.loads((OLD / 'plan.json').read_text())
check({k: v for k, v in plan.items() if k != 'preservedV1SourceIndex'} == previous_plan)
for name in ['run.py', 'test-flags.py']: ast.parse((HERE / name).read_text()); checks += 1
print(json.dumps(dict(passed=True, checks=checks, actualInterpreter=dict(executable=sys.executable,
    isolated=sys.flags.isolated, dontWriteBytecode=sys.dont_write_bytecode),
    realCurrentFlagPredicatesEvaluated=True, cargoRestorerMonitorOrActorInvoked=False,
    originalV1FailurePreserved=True, protocolAndOperationalWireUnchanged=True)))
