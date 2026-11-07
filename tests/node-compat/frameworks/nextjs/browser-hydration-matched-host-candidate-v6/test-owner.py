"""Actual pure namespace selector and exact owner delta; no monitor or actor."""
from pathlib import Path
import ast
import json
import re

HERE = Path(__file__).absolute().parent
source = (HERE / 'run-owned.py').read_text()
old = (HERE.parent / 'browser-hydration-matched-host-candidate-v4/run-owned.py').read_text()
assert source.replace('next-browser-hydration-stock-v6', 'next-browser-hydration-stock-v4') == old
node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'derive_invocation')
scope = dict(Path=Path, re=re)
exec(compile(ast.Module(body=[node], type_ignores=[]), '<inert actual selector>', 'exec'), scope)
select = scope['derive_invocation']
plan = json.loads((HERE / 'plans.json').read_text())
authority = dict(state='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1', arm='stock', runId='data-only')
output, monitor, argv = select(authority, plan, HERE)
assert str(output) == '/private/tmp/starling-node-compat/next-browser-hydration-stock-v6-data-only'
assert str(monitor) == str(output) + '-monitor'
assert argv == [plan['node']['path'], str(HERE/'run-stock.mjs'), str(output), plan['standaloneSource'], plan['browserTools'], 'data-only']
checks = 4
for value in ['', 'Upper', 'x/y', 'x\n', 'a'*49, '.', '../x']:
    try:
        select(dict(authority, runId=value), plan, HERE)
    except AssertionError:
        checks += 1
    else:
        raise AssertionError('Unsafe namespace accepted')
for name in ['outputRoot', 'monitorOutputRoot', 'argv']:
    try:
        select(dict(authority, **{name: None}), plan, HERE)
    except AssertionError:
        checks += 1
    else:
        raise AssertionError('Root override accepted')
assert plan['arms']['stock']['timeoutSeconds'] == 300
print(json.dumps(dict(state='MATCHED_STOCK_V6_OWNER_SOURCE_TESTS_PASSED', checks=checks+1,
    actorOrMonitorInvoked=False, sourceOnly=True)))
