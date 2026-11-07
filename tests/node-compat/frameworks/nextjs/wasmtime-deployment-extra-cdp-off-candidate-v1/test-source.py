"""Read-only diagnostic derivation tests; no actor/helper imports or resources."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / 'wasmtime-deployment-candidate-v9'
BROWSER = HERE.parent / 'native-extra-cdp-off-candidate-v1'


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    checks = 0

    def need(value, label):
        nonlocal checks
        assert value is True, label
        checks += 1

    prior = json.loads((PRIOR / 'plan.json').read_bytes())
    plan = json.loads((HERE / 'plan.json').read_bytes())
    need(set(plan) == set(prior) | {'preservedDeploymentV9'}, 'Only ancestry key added')
    need({k for k in plan if plan[k] != prior.get(k)} == {
        'state', 'sourceFamilies', 'protectedInputs', 'preservedDeploymentV9'}, 'Exact four plan changes')
    need(plan['preservedDeploymentV9'] == row(PRIOR / 'index.json'), 'V9 ancestry binds')
    need(plan['sourceFamilies'] == prior['sourceFamilies'] + [row(PRIOR / 'index.json'), row(BROWSER / 'index.json')], 'Both new indexed protections bind')
    need(plan['protectedInputs'] == prior['protectedInputs'] + [row(BROWSER / 'browser-check.mjs')], 'Exact diagnostic worker protected')
    for name in ['deploy.mjs', 'run-owned.py', 'app-policy.mjs']:
        need((HERE / name).read_bytes() == (PRIOR / name).read_bytes(), name + ' byte-identical')
    old = b'../browser-hydration-candidate-v3/browser-check.mjs'
    new = b'../native-extra-cdp-off-candidate-v1/browser-check.mjs'
    before = (PRIOR / 'run-contracts.mjs').read_bytes()
    current = (HERE / 'run-contracts.mjs').read_bytes()
    need(before.count(old) == 1, 'Exactly one browser path literal')
    need(current == before.replace(old, new), 'No other client byte changes')
    need(b"from '../wasmtime-deployment-candidate-v8/supplemental.mjs'" in current, 'Same physical supplemental helper')
    need(not (HERE / 'supplemental.mjs').exists(), 'Helper not copied')
    need(plan['expectedComponent'] == prior['expectedComponent'] == dict(
        sha256='4afeeb76ebf54f10c263dfbc36dd6a074d5aae6ee53b022df3245998c89292e8', bytes=37218693), 'Exact same genuine component')
    for key in ['outputPrefix', 'requiredObservations', 'supplementalConcurrentRegression',
                'wasmtimePolicy', 'deadlines', 'shutdown', 'selectedInterfaces', 'expectedExport',
                'fixedWit', 'applicationSource', 'applicationInputs', 'applicationBuildResult',
                'applicationRootIdentity', 'applicationSchema', 'readonlyApp', 'writableCache',
                'node', 'wasmtime', 'monitor', 'browserTools']:
        need(plan[key] == prior[key], key + ' unchanged')
    need(plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-wasmtime-deployment', 'Same safe namespace derivation')
    for key in ['actualRootAuthority', 'actualConstructionResult', 'actualComponent',
                'actualComponentAudit', 'actualDeployment', 'constructionCallerIndex',
                'inputSourceIndex', 'inputEntry', 'runId', 'outputRoot', 'monitorOutputRoot']:
        need(plan[key] is None, key + ' remains late NULL')
    browser = json.loads((BROWSER / 'plan.json').read_bytes())
    need(browser['extraDiagnosticSessionEnabled'] is False and browser['playwrightBuiltinProtocolUnchanged'] is True,
         'Only extra observer session disabled')
    need(browser['wasmBrowserRun'] is True and browser['actualNativeExecutionRequiresParentEvidence'] is True,
         'Native arm retains parent-proof obligation')
    need(browser['priorFailureAcceptance'] is False, 'Old failure not accepted')
    ast.parse((HERE / 'run-owned.py').read_text())
    print(json.dumps(dict(schemaVersion=1, passed=True, checks=checks, sourceOnly=True,
                          actorOrBrowserOrServerOrNetworkInvoked=False,
                          priorFailureAcceptance=False, actualRuntime=None)))


if __name__ == '__main__':
    main()
