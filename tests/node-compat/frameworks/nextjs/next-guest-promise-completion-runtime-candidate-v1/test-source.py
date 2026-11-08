"""Read-only scaffold/late-binding Source checks; no helper, JS or guard execution."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def read(path):
    return json.loads(path.read_text())


def ref(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    count = 0

    def check(value):
        nonlocal count
        assert value
        count += 1

    donor = BASE / 'next-guest-completion-runtime-candidate-v1'
    plan, old = read(HERE / 'plan.json'), read(donor / 'plan.json')
    derivation = read(HERE / 'derivation.json')
    for name in ['capture-stdout.mjs', 'deploy.mjs', 'run-owned.py', 'run-contracts.mjs', 'app-policy.mjs', 'test-gates.mjs']:
        check((HERE / name).read_bytes() == (donor / name).read_bytes())
        check(derivation['copiedByteIdentical'][name] == ref(HERE / name))
    check((HERE / 'deploy.patch').read_bytes() == (donor / 'deploy.patch').read_bytes())
    for name in ['run-owned.py', 'test-source.py']:
        ast.parse((HERE / name).read_text())
        check(True)
    for key in ['outputPrefix', 'requiredObservations', 'deadlines', 'shutdown', 'selectedInterfaces',
                'fixedWit', 'portableCacheProfile', 'browserSource', 'browserNetlogDiagnostic',
                'applicationSchema', 'expectedEngine', 'expectedNativeMetadata', 'applicationInputs',
                'applicationBuildReview', 'preservedD990FailureBaselines', 'wasmtimePolicy', 'worldFamily']:
        check(plan[key] == old[key])
    check(plan['sourceFamilies'][:len(old['sourceFamilies'])] == old['sourceFamilies'])
    check(plan['protectedInputs'][:len(old['protectedInputs'])] == old['protectedInputs'])
    check(plan['stdoutCapturePolicy'] == dict(old['stdoutCapturePolicy'], helper=ref(HERE / 'capture-stdout.mjs')))
    check(plan['stdoutCapturePolicy']['maxGlobalRawBytes'] == 8388608)
    check(plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-wasmtime-deployment')
    check(plan['browserSource']['sha256'] == 'f19d6c42ea44897ed026ba437657a9749396ee138301e5abbfaa17eb508c7ffa')
    entry = BASE / 'next-guest-promise-completion-diagnostic-entry-v1'
    diag = plan['guestCompletionDiagnostic']
    check(diag['inputSourceIndex'] == ref(entry / 'index.json'))
    check(diag['inputEntry'] == ref(entry / 'guest-entry.mjs'))
    check(diag['contract'] == ref(entry / 'marker-contract.json'))
    check(diag['marker'] == 'NEXT_GUEST_PROMISE_COMPLETION_V1')
    check(diag['importCountIsAdmissionTarget'] is False)
    check(diag['oldAsyncReturnAlreadyAdopted'] is True and diag['missingAwaitFix'] is False)
    check(diag['guaranteedExtraMicrotaskCount'] is None)
    check(diag['crossLaneOrInstanceTokenJoinAllowed'] is False)
    for key in ['actualRootGrant', 'actualDeployment', 'actualTraceReview']:
        check(diag[key] is None)
    if plan['prospectiveActualBindingsPending']:
        for key in ['expectedComponent', 'acceptedConstructionReview', 'cleanupConstructionSourceIndex']:
            check(plan[key] is None)
        for key in ['callerIndex', 'plan', 'actualResult', 'component', 'componentAudit', 'constructionReview',
                    'constructionReviewState', 'completeReturnedImportAuditVerified', 'observedReturnedImportFunctionCount']:
            check(diag[key] is None)
        check(plan['requiredExternalRootAdmission']['constructionReview'] is None)
    else:
        review_ref = plan['acceptedConstructionReview']
        check(ref(Path(review_ref['path'])) == review_ref)
        review = read(Path(review_ref['path']))
        check(review['verifiedPassed'] is review['completeReturnedImportAuditVerified'] is True)
        check(diag['constructionReview'] == plan['requiredExternalRootAdmission']['constructionReview'] == review_ref)
        check(diag['constructionReviewState'] == review['state'])
        for key in ['callerIndex', 'plan', 'actualResult', 'component', 'componentAudit', 'inputEntry', 'inputSourceIndex']:
            check(diag[key] == review[key])
        check(plan['expectedComponent'] == {key:review['component'][key] for key in ['sha256', 'bytes']})
        check(plan['cleanupConstructionSourceIndex'] == review['callerIndex'])
    for key in ['actualRootAuthority', 'actualConstructionResult', 'actualComponent', 'actualComponentAudit', 'actualDeployment']:
        check(plan[key] is None)
    unit = plan['parentCaptureUnitEvidence']
    check(unit['testedHelperCodeByteIdentical'] is True and unit['unitSuiteRerunForThisCopy'] is False)
    check(unit['selectedByteIdenticalHelper'] == ref(HERE / 'capture-stdout.mjs'))
    check({key:unit['testedHelper'][key] for key in ['sha256','bytes']} ==
          {key:unit['selectedByteIdenticalHelper'][key] for key in ['sha256','bytes']})
    record = read(Path(unit['retainedResult']['path']))
    check(ref(Path(unit['retainedResult']['path'])) == unit['retainedResult'])
    check(record['helper'] == unit['testedHelper'] and record['passed'] is True and record['caseCount'] == 9)
    check(record['wasmGuestOrWasmtimeOrNetworkExecuted'] is False)
    print(json.dumps(dict(state='PROMISE_RUNTIME_SOURCE_SCAFFOLD_CHECKS_PASSED_V1', checks=count,
        prospectiveActualBindingsPending=plan['prospectiveActualBindingsPending'], passed=True,
        javaScriptHelperGuardNodeActorExecuted=False, helperUnitSuiteRerun=False,
        priorByteIdenticalHelperUnitCases=9, actualNewRuntime=None)))


if __name__ == '__main__':
    main()
