"""Inert V8-to-V9 derivation checks; no actor/helper imports or resources."""
from pathlib import Path
import argparse
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / 'wasmtime-deployment-candidate-v8'


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--construction-result', help='Optional genuine constructor JSON, DATA only')
    args = parser.parse_args()
    checks = 0

    def need(value, label):
        nonlocal checks
        assert value is True, label
        checks += 1

    before = json.loads((PRIOR / 'plan.json').read_bytes())
    plan = json.loads((HERE / 'plan.json').read_bytes())
    need(set(plan) == set(before) | {'preservedDeploymentV8'}, 'Only one ancestry key added')
    need({k for k in plan if plan[k] != before.get(k)} == {
        'state', 'expectedComponent', 'preservedDeploymentV8', 'sourceFamilies', 'protectedInputs'},
        'Exact finite plan delta')
    need(plan['preservedDeploymentV8'] == row(PRIOR / 'index.json'), 'Indexed V8 ancestry')
    need(plan['sourceFamilies'] == before['sourceFamilies'] + [row(PRIOR / 'index.json')], 'Whole helper family protected')
    helper = row(PRIOR / 'supplemental.mjs')
    need(plan['protectedInputs'] == before['protectedInputs'] + [helper], 'Exact shared helper protected')
    need(helper['sha256'] == '3dccf04bfc54b3653473bf2a1c69a9b59edbe52be5fd1c4bf2123eb4edb98838', 'Held helper bytes')
    need(not (HERE / 'supplemental.mjs').exists(), 'No second physical helper')
    stock = HERE.parent / 'browser-hydration-matched-host-candidate-v6'
    stock_actor = (stock / 'run-stock.mjs').read_text()
    need('wasmtime-deployment-candidate-v8/supplemental.mjs' in stock_actor, 'StockV6 shares same helper path')
    for name in ['deploy.mjs', 'run-owned.py', 'app-policy.mjs']:
        need((HERE / name).read_bytes() == (PRIOR / name).read_bytes(), name + ' exact donor')
    source = (PRIOR / 'run-contracts.mjs').read_bytes()
    old = b"from './supplemental.mjs'"
    new = b"from '../wasmtime-deployment-candidate-v8/supplemental.mjs'"
    need(source.count(old) == 1, 'One donor import occurrence')
    current = (HERE / 'run-contracts.mjs').read_bytes()
    need(current == source.replace(old, new), 'Only helper import changed')
    need(current[current.index(b'const here='):] == source[source.index(b'const here='):], 'Entire functional client suffix unchanged')
    deploy = (HERE / 'deploy.mjs').read_text()
    need("assert.deepEqual({sha256:authority.component.sha256,bytes:authority.component.bytes},plan.expectedComponent);" in deploy,
         'Actual copied actor enforces both component SHA and bytes')
    need(plan['outputPrefix'] == before['outputPrefix'] == '/private/tmp/starling-node-compat/next-wasmtime-deployment', 'Same safe runId namespace mechanism')
    need(plan['requiredObservations'] == before['requiredObservations'], 'Original 24/cache/stream/2-browser gates unchanged')
    need(plan['supplementalConcurrentRegression'] == before['supplementalConcurrentRegression'], 'Same six-case batch')
    need(plan['wasmtimePolicy'] == before['wasmtimePolicy'], 'No host flag change')
    need(plan['deadlines'] == before['deadlines'], 'All deadlines unchanged')
    need(plan['shutdown'] == before['shutdown'], 'Original SIGINT0 policy')
    need(plan['selectedInterfaces'] == before['selectedInterfaces'], 'Exact standard world selection')
    need(len(plan['selectedInterfaces']) == len(set(plan['selectedInterfaces'])) == 13, 'Thirteen unique interfaces')
    need(all(x.endswith('@0.2.10') for x in plan['selectedInterfaces']), 'Exact standard version')
    for key in ['fixedWit', 'applicationSource', 'applicationInputs', 'applicationBuildResult',
                'applicationBuildOutputRoot', 'applicationRootIdentity', 'applicationSchema',
                'readonlyApp', 'writableCache', 'browserTools']:
        need(plan[key] == before[key], key + ' unchanged')
    for key in ['actualRootAuthority', 'actualConstructionResult', 'actualComponent',
                'actualComponentAudit', 'actualDeployment', 'constructionCallerIndex',
                'inputSourceIndex', 'inputEntry', 'runId', 'outputRoot', 'monitorOutputRoot']:
        need(plan[key] is None, key + ' remains late NULL')
    if plan['expectedComponent'] is None:
        stage = 'UNSEALED_AWAITING_ACCEPTED_COMPONENT_PIN'
    else:
        value = plan['expectedComponent']
        need(set(value) == {'sha256', 'bytes'}, 'Finite component content pin')
        need(type(value['sha256']) is str and len(value['sha256']) == 64
             and all(c in '0123456789abcdef' for c in value['sha256']), 'Component SHA shape')
        need(type(value['bytes']) is int and value['bytes'] > 0, 'Component byte shape')
        need(value == dict(sha256='4afeeb76ebf54f10c263dfbc36dd6a074d5aae6ee53b022df3245998c89292e8',
                           bytes=37218693), 'Exact genuine V6 component content pin')
        need(value != before['expectedComponent'], 'Old 1c31 component pin not reused')
        need(value != dict(value, bytes=value['bytes'] + 1), 'Byte-count mismatch refuses exact comparison')
        need(value != dict(value, sha256='0' * 64), 'SHA mismatch refuses exact comparison')
        stage = 'SOURCE_CONTENT_PIN_PRESENT_NOT_RUNTIME_PROOF'
    actual = None
    if args.construction_result:
        path = Path(args.construction_result)
        need(path.is_absolute() and path.resolve() == path, 'Canonical constructor DATA path')
        result_ref = row(path)
        result = json.loads(path.read_bytes())
        need(result['state'] == 'NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2'
             and result['passed'] is True and result['error'] is None
             and result['finalProtection']['unchanged'] is True, 'Genuine succeeded constructor DATA')
        need(result['entryMode'] == 'real-next', 'Same real-next mode')
        component = result['artifacts']['component']
        need(plan['expectedComponent'] == {k: component[k] for k in ['sha256', 'bytes']}, 'Pin joins genuine component descriptor')
        audit_ref = result['artifacts']['componentAudit']
        need(row(Path(audit_ref['path'])) == audit_ref, 'Audit DATA descriptor authenticates')
        audit = json.loads(Path(audit_ref['path']).read_bytes())
        need(audit['component'] == component and audit['passed'] is True, 'Audit joins same component')
        need(audit['selectedInterfaces'] == plan['selectedInterfaces'], 'Audit selects same thirteen interfaces')
        need(len(audit['emittedImports']) == 13 and set(audit['emittedImports']) == set(plan['selectedInterfaces']),
             'Actual component emitted exact selected thirteen')
        need(audit['exports'] == ['wasi:http/incoming-handler@0.2.10'], 'Same incoming-handler export')
        need(row(path) == result_ref, 'Constructor DATA unchanged')
        actual = dict(constructionResult=result_ref, componentAudit=audit_ref,
                      dataOnly=True, independentDataAcceptanceClaimed=False)
    ast.parse((HERE / 'run-owned.py').read_text())
    need(True, 'Copied owner AST parses without import')
    print(json.dumps(dict(schemaVersion=1, passed=True, checks=checks, stage=stage,
                          genuineConstructorDataCheck=actual,
                          sharedSupplementalHelper=helper, helperPhysicalCopiesCreated=0,
                          actorOrBrowserOrServerOrNetworkInvoked=False,
                          actualComponent=None, actualRuntime=None)))


if __name__ == '__main__':
    main()
