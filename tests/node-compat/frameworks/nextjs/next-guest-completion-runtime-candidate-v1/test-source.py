"""Read-only text/JSON/AST checks; never import JS, helpers, guards or producers."""
import ast
import difflib
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

    donor = BASE / 'next-browser-netlog-native-candidate-v1'
    root = BASE / 'next-guest-completion-runtime-root-results-v1'
    plan, old = read(HERE / 'plan.json'), read(donor / 'plan.json')
    derivation = read(HERE / 'derivation.json')
    for name in ['run-owned.py', 'run-contracts.mjs', 'app-policy.mjs', 'test-gates.mjs']:
        check((HERE / name).read_bytes() == (donor / name).read_bytes())
        check(derivation['copiedByteIdentical'][name] == ref(HERE / name))
    for name in ['run-owned.py', 'test-source.py']:
        ast.parse((HERE / name).read_text())
        count += 1
    for name in ['prepare-runtime.py', 'run-full-native-requests.py']:
        ast.parse((root / name).read_text())
        count += 1
    deploy = (HERE / 'deploy.mjs').read_text()
    helper = (HERE / 'capture-stdout.mjs').read_text()
    expected = ''.join(difflib.unified_diff((donor / 'deploy.mjs').read_text().splitlines(keepends=True),
        deploy.splitlines(keepends=True), fromfile='next-browser-netlog-native-candidate-v1/deploy.mjs',
        tofile='next-guest-completion-runtime-candidate-v1/deploy.mjs'))
    check((HERE / 'deploy.patch').read_text() == expected)
    check(ref(HERE / 'deploy.mjs') == derivation['reviewedDeployAfterimage'])
    check(ref(HERE / 'capture-stdout.mjs') == plan['stdoutCapturePolicy']['helper'])
    check(helper.index('ceiling>limitBytes') < helper.index('await handle.writeFile(chunk)'))
    check('await handle.sync();}catch(error)' in helper and 'await handle.close();state.fileClosed=true;' in helper)
    check("stdio:['ignore',pipeStdout?'pipe':out.fd,err.fd]" in deploy)
    check("pipeStdout=id==='wasmtime'" in deploy)
    check("['serve','--no-logging-prefix','--addr'" in deploy)
    check('hostExit!==null&&hostCaptureOutcome?.finalized' in deploy)
    check("if(result.client.shutdownRequested===true)" in deploy)
    check('result.passed=hostCaptureOutcome?.complete===true&&' in deploy)
    check('NEXT_GUEST_RESPONSE_COMPLETION_V1' not in deploy + helper)
    check(plan['outputPrefix'] == old['outputPrefix'] == '/private/tmp/starling-node-compat/next-wasmtime-deployment')
    for key in ['requiredObservations', 'deadlines', 'shutdown', 'selectedInterfaces', 'fixedWit',
                'portableCacheProfile', 'browserSource', 'browserNetlogDiagnostic', 'applicationSchema',
                'expectedEngine', 'expectedNativeMetadata', 'applicationInputs', 'applicationBuildReview']:
        check(plan[key] == old[key])
    check(plan['sourceFamilies'][:len(old['sourceFamilies'])] == old['sourceFamilies'])
    check(plan['protectedInputs'][:len(old['protectedInputs'])] == old['protectedInputs'])
    check([item['sha256'][:4] for item in plan['preservedD990FailureBaselines']] == ['c3a8', 'f3d7', '8151'])
    review = plan['acceptedConstructionReview']
    check(ref(Path(review['path'])) == review)
    actual = read(Path(review['path']))
    check(actual['verifiedPassed'] is actual['completeReturnedImportAuditVerified'] is True)
    check(actual['state'] == 'COORDINATED_GUEST_PUBLIC_COMPLETION_COMPONENT_INIT_DATA_REVIEW_PASSED_V1')
    check(plan['expectedComponent'] == {key:actual['component'][key] for key in ['sha256', 'bytes']})
    for key in ['inputSourceIndex', 'inputEntry', 'callerIndex', 'plan', 'actualResult', 'component', 'componentAudit']:
        check(plan['guestCompletionDiagnostic'][key] == actual[key])
    check(plan['guestCompletionDiagnostic']['importCountIsAdmissionTarget'] is False)
    check(actual['deployedCompletionDiagnosticObserved'] is actual['runtimeAccepted'] is False)
    for key in ['actualRootAuthority', 'actualConstructionResult', 'actualComponent', 'actualComponentAudit', 'actualDeployment']:
        check(plan[key] is None)
    unit = plan['parentCaptureUnitEvidence']
    for key in ['testSource', 'retainedResult', 'independentDataReview']:
        check(ref(Path(unit[key]['path'])) == unit[key])
    record = read(Path(unit['retainedResult']['path']))
    check(record['passed'] is True and record['caseCount'] == len(record['records']) == 9)
    check(all(item['passed'] is True for item in record['records']))
    check(record['helper'] == plan['stdoutCapturePolicy']['helper'])
    check(record['wasmGuestOrWasmtimeOrNetworkExecuted'] is False)
    check(unit['rootExecuted'] is True and unit['authorExecuted'] is unit['guestOrOrchestrationExecuted'] is False)
    wrapper = (root / 'run-full-native-requests.py').read_text()
    preparation = (root / 'prepare-runtime.py').read_text()
    check('native.protect_full_build(a, metadata)' in wrapper)
    check('current = world.world_guard(world_authority)' in wrapper)
    check('before = admission(a, plan, native, world)' in wrapper and 'after = admission(a, plan, native, world)' in wrapper)
    check('world = wrapper.admission(authority, actor_plan, native_guard, world_guard)' in preparation)
    check("for copy in build_result['sourceCopies']:" in preparation and "assert len(refs) == 1650" in preparation)
    check('98a39cc9' not in preparation and 'D990 artifact' not in preparation)
    template = read(HERE / 'root-authority-template.json')
    for key in ['localhostServeAllowed', 'actualNextGuestAllowed', 'browserAllowed']:
        check(template[key] is None)
    print(json.dumps(dict(state='SOURCE_TEXT_JSON_AST_CHECKS_PASSED_V1', checks=count,
        passed=True, javaScriptOrHelperExecuted=False, guardsOrActorsExecuted=False,
        rootHelperUnitCases=9, rootRuntimeExecuted=False)))


if __name__ == '__main__':
    main()
