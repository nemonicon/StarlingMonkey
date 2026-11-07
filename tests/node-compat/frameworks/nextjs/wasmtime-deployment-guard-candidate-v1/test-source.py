"""Finite read/AST invariants. No actor, constructor, tool or helper invocation."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / 'wasmtime-deployment-candidate-v9'
GUARD = HERE.parent / 'next-module-fileurl-boundary-candidate-v1'
CTOR = HERE.parent / 'next-module-boundary-construction-v1'


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
    need(set(plan) == set(before) | {'preservedDeploymentV9'}, 'only ancestry key added')
    need({k for k in plan if plan[k] != before.get(k)} ==
         {'state', 'sourceFamilies', 'expectedComponent', 'preservedDeploymentV9'}, 'four plan deltas')
    need(plan['preservedDeploymentV9'] == row(PRIOR / 'index.json'), 'exact held V9')
    need(plan['sourceFamilies'] == before['sourceFamilies'] +
         [row(PRIOR / 'index.json'), row(GUARD / 'index.json'), row(CTOR / 'index.json')],
         'exact append-only Source families')
    derivation = json.loads((HERE / 'derivation.json').read_bytes())
    binding = derivation['actualConstructorBinding']
    need(binding is not None and derivation['artifactFingerprintPendingGenuineConstructorDataReview'] is False,
         'real constructor DATA precedes binding')
    need(row(Path(binding['review']['path'])) == binding['review'], 'actual review descriptor')
    review = json.loads(Path(binding['review']['path']).read_bytes())
    need(review['verifiedPassed'] is True and review['ordinaryExportsInvoked'] is False and
         review['runtimeAccepted'] is False, 'review is INIT-only')
    need(binding['component'] == review['component'] and binding['result'] == review['actualResult'] and
         binding['componentAudit'] == review['componentAudit'], 'actual typed return/result/audit joins')
    need(binding['engine'] == review['engine'] and binding['nativeMetadata'] == review['nativeMetadata'],
         'new native pair distinct from component')
    need(plan['expectedComponent'] == {k: review['component'][k] for k in ['sha256', 'bytes']} ==
         dict(sha256='49013f31195b0bf94c26188898c7d6a6d09db7c7dba14ba8550255b0dc9bac50', bytes=37217436),
         'genuine new fingerprint')
    need(before['expectedComponent']['sha256'].startswith('4afeeb76') and
         plan['expectedComponent'] != before['expectedComponent'], 'old artifact only ancestry')
    for name in ['deploy.mjs', 'run-owned.py', 'run-contracts.mjs', 'app-policy.mjs']:
        need((HERE / name).read_bytes() == (PRIOR / name).read_bytes(), name + ' exact donor')
    client = (HERE / 'run-contracts.mjs').read_bytes()
    need(b"from '../wasmtime-deployment-candidate-v8/supplemental.mjs'" in client,
         'same physical shared supplemental helper')
    need(b'../browser-hydration-candidate-v3/browser-check.mjs' in client,
         'same normal Browser V3')
    need(b'native-extra-cdp-off' not in client, 'no CDP-off worker selected')
    need(not (HERE / 'supplemental.mjs').exists() and not (HERE / 'browser-check.mjs').exists(),
         'no helper/browser duplication')
    need(b'after.generation > before.generation' in client, 'strict cache increase retained')
    need(b'result.originalContractPassed&&result.supplementalValidation?.passed===true' in client,
         'original and supplemental gates both required')
    for key in ['protectedInputs', 'requiredObservations', 'supplementalConcurrentRegression',
                'wasmtimePolicy', 'deadlines', 'shutdown', 'selectedInterfaces', 'expectedExport',
                'fixedWit', 'applicationSource', 'applicationInputs', 'applicationBuildResult',
                'applicationRootIdentity', 'applicationSchema', 'readonlyApp', 'writableCache',
                'node', 'wasmtime', 'monitor', 'browserTools', 'outputPrefix']:
        need(plan[key] == before[key], key + ' unchanged')
    need(plan['deadlines']['outerSeconds'] == 600 and plan['wasmtimePolicy']['maxInstanceReuseCount'] == 128,
         'same owner and reuse caps')
    need(plan['requiredObservations'] == dict(http=24, browser=2, cacheInvalidation=True,
         strictStreaming='readyChunk>shellChunk>=0'), 'all original observations')
    need(len(plan['selectedInterfaces']) == 13 and all(v.endswith('@0.2.10') for v in plan['selectedInterfaces']),
         'standard13 unchanged')
    need(plan['supplementalConcurrentRegression']['cases'] == 6 and
         plan['supplementalConcurrentRegression']['perRequestTimeoutMs'] == 20000,
         'same supplemental batch')
    for key in ['actualRootAuthority', 'actualConstructionResult', 'actualComponent', 'actualComponentAudit',
                'actualDeployment', 'constructionCallerIndex', 'inputSourceIndex', 'inputEntry', 'runId',
                'outputRoot', 'monitorOutputRoot']:
        need(plan[key] is None, key + ' late null')
    ast.parse((HERE / 'run-owned.py').read_text())
    ast.parse((HERE / 'test-source.py').read_text())
    print(json.dumps(dict(sourceOnly=True, inertSourceChecks=checks, fourExecutableBytesIdentical=True,
                         actualComponentFingerprintBound=True, actualOperationalSlotsNull=True,
                         actorConstructorToolOrHelperInvoked=False, indexWritten=False)))


if __name__ == '__main__':
    main()
