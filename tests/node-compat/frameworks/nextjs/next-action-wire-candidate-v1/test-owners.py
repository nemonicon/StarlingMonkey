"""Read-only/inert actual-owner selectors/guards; never call main or a monitor."""
import ast
import importlib.util
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
checks = 0


def need(value):
    global checks
    assert value is True
    checks += 1


def refuses(fn):
    caught = False
    try:
        fn()
    except (AssertionError, KeyError, TypeError, ValueError):
        caught = True
    need(caught)


def load(name):
    path = BASE / name / 'run-owned.py'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Only definitions; main is not invoked.
    return module


for name, plan_file, native in [('next-action-wire-native-candidate-v1', 'plan.json', True),
                                 ('next-action-wire-stock-candidate-v1', 'plans.json', False)]:
    root = BASE / name; owner = load(name)
    plan = json.loads((root / plan_file).read_text())
    authority = dict(runId='source-fixture')
    if not native:
        authority.update(state='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1', arm='stock')
    args = (authority, plan, root, Path('/private/tmp/source-only-authority.json')) if native else (authority, plan, root)
    output, monitor, argv = owner.derive_invocation(*args)
    need(str(output) == plan['outputPrefix'] + '-source-fixture')
    need(str(monitor) == str(output) + ('-external-root' if native else '-monitor'))
    need(argv == ([plan['node']['path'], str(root / 'deploy.mjs'), '/private/tmp/source-only-authority.json'] if native else
                  [plan['node']['path'], str(root / 'run-stock.mjs'), str(output), plan['standaloneSource'], 'source-fixture']))
    for run_id in ['', '../escape', 'bad\n', 'A', 'a' * 49, False, None]:
        old = authority['runId']; authority['runId'] = run_id
        refuses(lambda: owner.derive_invocation(*args)); authority['runId'] = old
    for key in ['outputRoot', 'monitorOutputRoot', 'argv']:
        authority[key] = None; refuses(lambda: owner.derive_invocation(*args)); del authority[key]
    for value in [1073741824, 1073741825]:
        owner.require_capacity(value); need(True)
    for value in [1073741823, 0, -1, True, 1073741824.0, None, '1073741824']:
        refuses(lambda: owner.require_capacity(value))
    tree = ast.parse((root / 'run-owned.py').read_text())
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
    clean = next(node.value for node in ast.walk(main) if isinstance(node, ast.Assign)
                 and any(isinstance(target, ast.Name) and target.id == 'clean' for target in node.targets))
    terminal = dict(parentOwnedGroupGone=True, allObservedOwnedGroupsGone=True, timeout=False, forcedCleanup=False,
                    errors=[], signals=[], interruptedSignals=[], remainingObservedPids=[], rawExitCode=1)
    need(eval(compile(ast.Expression(clean), '<actual-clean-guard>', 'eval'), {'terminal': terminal}) is True)
    for key in ['parentOwnedGroupGone', 'allObservedOwnedGroupsGone', 'timeout', 'forcedCleanup', 'errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
        changed = dict(terminal); changed[key] = False if key.endswith('Gone') else (True if key in ['timeout', 'forcedCleanup'] else ['failure'])
        need(eval(compile(ast.Expression(clean), '<actual-clean-guard>', 'eval'), {'terminal': changed}) is False)
    need('600,' in (root / 'run-owned.py').read_text() if native else "monitor_output,300," in (root / 'run-owned.py').read_text())
    need('wireClientAllowed' in (root / 'run-owned.py').read_text())
    need("['browserAllowed'] is False" in (root / 'run-owned.py').read_text())
    source = (root / ('deploy.mjs' if native else 'run-stock.mjs')).read_text()
    need('../next-action-wire-candidate-v1/wire-client.mjs' in source)
    need('browserInvoked:false' in source and 'fullNextAcceptance:false' in source)
    need('run-contracts.mjs' not in source and 'browser-check.mjs' not in source)
    need('wireSourceBindingPending' in plan)
    need(plan['requiredObservations']['exactActionPosts'] == 1 and plan['requiredObservations']['browser'] is False)
    if native:
        donor = (BASE / 'wasmtime-deployment-extra-cdp-off-candidate-v1/deploy.mjs').read_text()
        for start, stop in [('async function entrySelection()', 'const output=resolve('),
                            ('async function prepareReadonlyCopy()', 'try{\n await prepareReadonlyCopy();'),
                            ('finally{\n if(lease)', ' result.passed=')]:
            need(source[source.index(start):source.index(stop)] == donor[donor.index(start):donor.index(stop)])
        need((root / 'app-policy.mjs').read_bytes() == (BASE / 'wasmtime-deployment-extra-cdp-off-candidate-v1/app-policy.mjs').read_bytes())
    else:
        donor = (BASE / 'browser-hydration-matched-host-candidate-v5/run-stock.mjs').read_text()
        start='  const moduleObservations = {};'; stop="  const contract = JSON.parse(await readFile(join(here, '../fixture-contract.json')));"
        # The original module/bridge setup remains exact except the truthful
        # kernel-owned listener record added after port selection.
        prior=donor[donor.index(start):donor.index(stop)]
        current=source[source.index(start):source.index('  const args=[join(here,')]
        current=current.replace("  assert.equal(server.address().address,'127.0.0.1');\n", '').replace("\n  result.portLease={host:'127.0.0.1',port,kernelAssignedExclusiveListener:true,heldThroughRequest:true,fallbackAllowed:false};", '')
        need(current == prior)

print(json.dumps(dict(sourceOnly=True, checks=checks, actualOwnerGuardsEvaluated=True,
                      actorMonitorCopyNetworkOrRequestInvoked=False)))
