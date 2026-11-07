"""Read/AST/data invariants only. No actor, tool, helper or traffic invocation."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / 'wasmtime-deployment-extra-cdp-off-candidate-v1'
ENTRY = HERE.parent / 'next-cache-affinity-diagnostic-entry-v1'
CTOR = HERE.parent / 'next-cache-affinity-diagnostic-construction-v1'


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    checks = 0

    def need(value, label):
        nonlocal checks
        assert value is True, label
        checks += 1

    before = json.loads((PRIOR / 'plan.json').read_bytes())
    plan = json.loads((HERE / 'plan.json').read_bytes())
    need(set(plan) == set(before) | {'preservedExtraCdpOffDeployment'}, 'only ancestry key added')
    need({k for k in plan if plan[k] != before.get(k)} == {'state', 'sourceFamilies', 'expectedComponent', 'preservedExtraCdpOffDeployment'}, 'exact four plan changes')
    need(plan['preservedExtraCdpOffDeployment'] == row(PRIOR / 'index.json'), 'exact held donor')
    need(plan['sourceFamilies'] == before['sourceFamilies'] + [row(PRIOR / 'index.json'), row(ENTRY / 'index.json'), row(CTOR / 'index.json')], 'exact indexed ancestry/entry/constructor additions')
    derivation = json.loads((HERE / 'derivation.json').read_bytes())
    binding = derivation['actualConstructorBinding']
    review_path = Path(binding['review']['path'])
    need(row(review_path) == binding['review'], 'actual constructor DATA review descriptor')
    review = json.loads(review_path.read_bytes())
    need(review['verifiedPassed'] is True and review['ordinaryExportsInvoked'] is False and review['runtimeAccepted'] is False, 'INIT-only DATA review scope')
    need(binding['component'] == review['component'] and binding['result'] == review['actualResult'], 'genuine artifact/result join')
    need(plan['expectedComponent'] == {k: review['component'][k] for k in ['sha256', 'bytes']}, 'actual fingerprint bound after genuine constructor')
    need(plan['expectedComponent'] == dict(sha256='811459eae1424a03fa29ae95259c731be11a8c50e99ceb3f34286dda698f3736', bytes=37222602), 'exact first affinity component')
    need(before['expectedComponent'] == dict(sha256='4afeeb76ebf54f10c263dfbc36dd6a074d5aae6ee53b022df3245998c89292e8', bytes=37218693), 'old fingerprint retained as ancestry only')
    for name in ['deploy.mjs', 'run-owned.py', 'run-contracts.mjs', 'app-policy.mjs']:
        need((HERE / name).read_bytes() == (PRIOR / name).read_bytes(), name + ' exact donor bytes')
    client = (HERE / 'run-contracts.mjs').read_bytes()
    need(b"from '../wasmtime-deployment-candidate-v8/supplemental.mjs'" in client, 'same physical shared helper')
    need(b"../native-extra-cdp-off-candidate-v1/browser-check.mjs" in client, 'same native off browser')
    need(not (HERE / 'supplemental.mjs').exists() and not (HERE / 'browser-check.mjs').exists(), 'no helper/browser duplication')
    need(b'after.generation > before.generation' in client, 'cacheincrease assertion unchanged')
    need(b'result.originalContractPassed&&result.supplementalValidation?.passed===true' in client, 'strict combined gate remains')
    deploy = (HERE / 'deploy.mjs').read_bytes()
    need(b'plan.expectedComponent' in deploy, 'actor still requires exact fingerprint')
    for key in ['protectedInputs', 'requiredObservations', 'supplementalConcurrentRegression', 'wasmtimePolicy', 'deadlines', 'shutdown', 'selectedInterfaces', 'expectedExport', 'fixedWit', 'applicationSource', 'applicationInputs', 'applicationBuildResult', 'applicationRootIdentity', 'applicationSchema', 'readonlyApp', 'writableCache', 'node', 'wasmtime', 'monitor', 'browserTools', 'outputPrefix']:
        need(plan[key] == before[key], key + ' unchanged')
    need(plan['deadlines']['outerSeconds'] == 600 and plan['wasmtimePolicy']['maxInstanceReuseCount'] == 128, 'same owner/host reuse')
    need(len(plan['selectedInterfaces']) == 13 and all(x.endswith('@0.2.10') for x in plan['selectedInterfaces']), 'standard13 unchanged')
    for key in ['actualRootAuthority', 'actualConstructionResult', 'actualComponent', 'actualComponentAudit', 'actualDeployment', 'constructionCallerIndex', 'inputSourceIndex', 'inputEntry', 'runId', 'outputRoot', 'monitorOutputRoot']:
        need(plan[key] is None, key + ' late NULL')
    ast.parse((HERE / 'run-owned.py').read_text())
    print(json.dumps(dict(sourceOnly=True, inertSourceChecks=checks, actorOrHelperOrEntropyInvoked=False,
        expectedComponentPending=False, actualSlotsNull=True, indexWritten=False)))


if __name__ == '__main__':
    main()
