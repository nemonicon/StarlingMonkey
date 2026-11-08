"""Finite Source/text/JSON/AST checks only; never import or run a target/helper."""
import ast
import hashlib
import json
import stat
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
OPS = ('capture-stdout.mjs', 'deploy.mjs', 'run-owned.py', 'run-contracts.mjs', 'app-policy.mjs', 'test-gates.mjs')


def read(path):
    return json.loads(path.read_bytes())


def ref(path):
    before = path.lstat()
    assert path.resolve() == path and stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    data = path.read_bytes()
    after = path.lstat()
    keys = ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    assert tuple(getattr(before, key) for key in keys) == tuple(getattr(after, key) for key in keys)
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    count = 0

    def check(value):
        nonlocal count
        assert value
        count += 1

    donor = BASE / 'next-guest-promise-completion-runtime-candidate-v1'
    plan, old = read(HERE / 'plan.json'), read(donor / 'plan.json')
    arm = plan['comparisonArm']['arm']
    selected = plan['comparisonArm']
    derivation = read(HERE / 'derivation.json')
    check(arm in ('A', 'B', 'C', 'D'))
    check(HERE.name == 'next-completion-' + arm.lower() + '-runtime-candidate-v1')
    check(derivation['arm'] == arm and derivation['donorSourceIndex'] == ref(donor / 'index.json'))
    check(derivation['donorPlan'] == ref(donor / 'plan.json'))
    for name in OPS:
        check((HERE / name).read_bytes() == (donor / name).read_bytes())
        check(derivation['copiedByteIdentical'][name] == ref(HERE / name))
    check((HERE / 'deploy.patch').read_bytes() == (donor / 'deploy.patch').read_bytes())
    check(derivation['historicalPatch'] == ref(HERE / 'deploy.patch'))
    for name in ('run-owned.py', 'test-source.py'):
        ast.parse((HERE / name).read_text())
        check(True)
    changed = {'state', 'sourceFamilies', 'protectedInputs', 'expectedComponent', 'acceptedConstructionReview',
        'cleanupConstructionSourceIndex', 'prospectiveActualBindingsPending', 'guestCompletionDiagnostic',
        'stdoutCapturePolicy', 'requiredExternalRootAdmission', 'parentCaptureUnitEvidence'}
    check(set(plan) == (set(old) - {'guestCompletionDiagnostic'}) | {'comparisonArm', 'comparisonProtocol'})
    for key in set(old) - changed:
        check(plan[key] == old[key])
    check('guestCompletionDiagnostic' not in plan)
    check(plan['sourceFamilies'][:len(old['sourceFamilies'])] == old['sourceFamilies'])
    check(plan['protectedInputs'][:len(old['protectedInputs'])] == old['protectedInputs'])
    check(ref(donor / 'index.json') in plan['sourceFamilies'])
    shared = BASE / 'next-completion-await-variants-v1'
    check(ref(shared / 'index.json') in plan['sourceFamilies'])
    check(derivation['sharedVariantsSourceIndex'] == ref(shared / 'index.json'))
    check(plan['state'] == 'DORMANT_FIXED_COMPLETION_COMPARISON_ARM_' + arm + '_SOURCE_V1')
    check(plan['stdoutCapturePolicy'] == dict(old['stdoutCapturePolicy'], helper=ref(HERE / 'capture-stdout.mjs')))
    check(plan['stdoutCapturePolicy']['maxGlobalRawBytes'] == 8388608)
    check(plan['stdoutCapturePolicy']['truncationAllowed'] is False)
    check(plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-wasmtime-deployment')
    check(plan['deadlines']['outerSeconds'] == 600)
    check(plan['browserSource']['sha256'] == 'f19d6c42ea44897ed026ba437657a9749396ee138301e5abbfaa17eb508c7ffa')
    check(plan['browserNetlogDiagnostic']['defaultCaptureMode'] is True)
    check(plan['wasmtimePolicy']['noLoggingPrefix'] is True)
    check(len(plan['selectedInterfaces']) == 13 and len(set(plan['selectedInterfaces'])) == 13)
    check(plan['selectedInterfaces'] == plan['worldFamily']['selectedInterfaces'])
    check(plan['worldFamily']['sourceIndex']['sha256'] == '802595f5a32dd93fc95c63eb95c901352ecb8da180152735982c344d6b827f58')
    check(plan['expectedExport'] == 'wasi:http/incoming-handler@0.2.10')
    check(plan['applicationInputs']['sha256'] == 'f8058b479484cf3463e1424892a74b3719136fea2e071c79eb2604558fa93ab8')
    check(plan['expectedEngine']['sha256'] == '476b1c1d7a5f8b37d2c40d17510a98dd45676994b894663d445ae2f519cc33f6')
    check(plan['expectedNativeMetadata']['sha256'] == '22f1d4561b73ce58b194afd5614368d30b16fc90f8fc7d63fe5c413916711b48')
    check(selected['responseSiteLoggerEnabled'] is (arm in ('C', 'D')))
    check(selected['explicitNeutralReturnAwait'] is (arm in ('B', 'D')))
    check(selected['cd60HolderOrChildPromiseDiagnosticSelected'] is False)
    check(selected['oldAsyncReturnAlreadyAdoptedPromise'] is True and selected['missingAwaitFix'] is False)
    check(selected['guaranteedExtraMicrotaskCount'] is None)
    check(selected['rawTokensOrSequenceArePhysicalIdentity'] is selected['wholeExportOrHostCompletionProved'] is False)
    check(selected['importCountIsAdmissionTarget'] is False)
    for key in ('actualRootGrant', 'actualTrial', 'actualRuntimeReview'):
        check(selected[key] is None)
    expected = {'A': ('next-component-entry-fixes-v5', 'guest-entry.mjs'),
        'B': ('next-completion-await-variants-v1', 'guest-entry-b.mjs'),
        'C': ('next-guest-response-completion-diagnostic-entry-v1', 'guest-entry.mjs'),
        'D': ('next-completion-await-variants-v1', 'guest-entry-d.mjs')}[arm]
    entry_dir = BASE / expected[0]
    check(selected['inputSourceIndex'] == ref(entry_dir / 'index.json'))
    check(selected['inputEntry'] == ref(entry_dir / expected[1]))
    index = read(entry_dir / 'index.json')
    member = selected['inputEntry']
    check([item for item in index['files'] if item['path'] == expected[1]] ==
          [dict(path=expected[1], sha256=member['sha256'], bytes=member['bytes'])])
    check(selected['inputSourceIndex'] in plan['protectedInputs'] and selected['inputEntry'] in plan['protectedInputs'])
    check(derivation['selectedInputSourceIndex'] == selected['inputSourceIndex'])
    check(derivation['selectedInputEntry'] == selected['inputEntry'])
    if arm in ('C', 'D'):
        check(selected['marker'] == 'NEXT_GUEST_RESPONSE_COMPLETION_V1')
        check(selected['historicalResponseMarkerContract'] == ref(BASE / 'next-guest-response-completion-diagnostic-entry-v1' / 'marker-contract.json'))
        if arm == 'D':
            check('not current' in selected['historicalMarkerContractScope'])
    else:
        check(selected['marker'] is None and selected['historicalResponseMarkerContract'] is None)
    pending = plan['prospectiveActualBindingsPending']
    check(type(pending) is bool)
    if arm in ('B', 'D'):
        check(selected['requiredReviewVariant'] == arm)
        check(selected['expectedConstructionReviewState'] == 'COORDINATED_NEXT_AWAIT_VARIANT_COMPONENT_INIT_DATA_REVIEW_PASSED_V1')
    else:
        check(pending is False)
    check(plan['prospectiveActualBindingsPending'] is selected['prospectiveActualBindingsPending'] is pending)
    check(derivation['prospectiveActualBindingsPending'] is pending)
    check(plan['requiredExternalRootAdmission'] == dict(old['requiredExternalRootAdmission'], constructionReview=plan['acceptedConstructionReview']))
    if pending:
        check(selected['requiredReviewVariant'] == arm)
        check(selected['expectedConstructionReviewState'] == 'COORDINATED_NEXT_AWAIT_VARIANT_COMPONENT_INIT_DATA_REVIEW_PASSED_V1')
        for key in ('expectedComponent', 'acceptedConstructionReview', 'cleanupConstructionSourceIndex'):
            check(plan[key] is None)
        for key in ('constructionReview', 'constructionReviewState', 'ownerReviewKey', 'ownerReview',
                    'actualResult', 'rootAuthority', 'callerIndex', 'plan', 'component', 'componentAudit',
                    'completeReturnedImportAuditVerified', 'observedReturnedImportFunctionCount'):
            check(selected[key] is None)
        check(derivation['actualConstructionReview'] is None)
    else:
        review_ref = plan['acceptedConstructionReview']
        check(ref(Path(review_ref['path'])) == review_ref)
        review = read(Path(review_ref['path']))
        check(review['verifiedPassed'] is review['completeReturnedImportAuditVerified'] is True)
        check(selected['constructionReview'] == plan['requiredExternalRootAdmission']['constructionReview'] == review_ref)
        check(selected['constructionReviewState'] == selected['expectedConstructionReviewState'] == review['state'])
        for key in ('actualResult', 'rootAuthority', 'callerIndex', 'plan', 'component', 'componentAudit', 'inputEntry', 'inputSourceIndex'):
            check(selected[key] == review[key])
        check(selected['ownerReview'] == review[selected['ownerReviewKey']])
        check(ref(Path(selected['ownerReview']['path'])) == selected['ownerReview'])
        check(plan['expectedComponent'] == {key: review['component'][key] for key in ('sha256', 'bytes')})
        check(plan['cleanupConstructionSourceIndex'] == review['callerIndex'])
        check(selected['completeReturnedImportAuditVerified'] is True)
        check(selected['observedReturnedImportFunctionCount'] == review['actualReturnedImportFunctionCount'])
        check(type(selected['observedReturnedImportFunctionCount']) is int)
        check(selected['requiredReviewVariant'] == (arm if arm in ('B', 'D') else None))
        check(derivation['actualConstructionReview'] == review_ref)
        if arm == 'A':
            check(selected['ownerReviewKey'] == 'complementaryOwnerWorldReview')
            check(review['state'] == 'COORDINATED_REAL_NEXT_INTEROP_COMPONENT_INIT_DATA_REVIEW_PASSED_V1')
            check('deployedCompletionDiagnosticObserved' not in review)
            check(selected['reviewMissingFields'] == ['deployedCompletionDiagnosticObserved'])
        elif arm == 'C':
            check(selected['ownerReviewKey'] == 'actualOwnerWorldReview')
            check(review['state'] == 'COORDINATED_GUEST_PUBLIC_COMPLETION_COMPONENT_INIT_DATA_REVIEW_PASSED_V1')
            check('deployedCompletionDiagnosticObserved' in review and review['deployedCompletionDiagnosticObserved'] is False)
        else:
            check(arm in ('B', 'D') and review['variant'] == selected['requiredReviewVariant'] == arm)
            check(review['state'] == 'COORDINATED_NEXT_AWAIT_VARIANT_COMPONENT_INIT_DATA_REVIEW_PASSED_V1')
            check(selected['ownerReviewKey'] == 'actualOwnerWorldReview')
            check(selected['reviewMissingFields'] == [])
            for key in ('ordinaryExportsInvoked', 'httpServed', 'appMountedAtInit', 'filesystemFixtureMountedAtInit',
                        'deployedFetchProbeInvoked', 'deployedImportOrFilesystemProbeInvoked',
                        'deployedCompletionDiagnosticObserved', 'runtimeAccepted', 'nodeParityProved',
                        'productionProfilePromoted'):
                check(key in review and review[key] is False)
            check(review['engine'] == plan['expectedEngine'] and review['nativeMetadata'] == plan['expectedNativeMetadata'])
            check(review['fullBuildReview'] == plan['requiredExternalRootAdmission']['fullNativeBuildReview'])
            check(review['metadataFixedValueCount'] == plan['requiredExternalRootAdmission']['metadataFixedValues'])
            check(review['buildEvidenceCount'] == plan['requiredExternalRootAdmission']['buildEvidence'])
            check(review['sourceEvidenceCount'] == plan['requiredExternalRootAdmission']['sourceEvidence'])
            for key in ('actualResult', 'rootAuthority', 'callerIndex', 'plan', 'componentAudit'):
                check(ref(Path(review[key]['path'])) == review[key])
            result = read(Path(review['actualResult']['path']))
            check(result['state'] == plan['constructionSuccessState'] and result['passed'] is True and result['error'] is None)
            for key in ('rootAuthority', 'callerIndex', 'plan'):
                check(result[key] == review[key])
            for key in ('component', 'componentAudit', 'engine', 'nativeMetadata'):
                check(result['artifacts'][key] == review[key])
            caller = read(Path(review['plan']['path']))
            check(caller['variant'] == arm and caller['entries']['real-next'] == selected['inputEntry'])
            check(caller['inputSourceIndex'] == selected['inputSourceIndex'])
            shared = read(BASE / 'next-completion-await-variants-v1' / 'plan.json')
            check(shared['entries'][arm] == shared['variants'][arm]['entry'] == selected['inputEntry'])
    for key in ('actualRootAuthority', 'actualConstructionResult', 'actualComponent', 'actualComponentAudit',
                'actualDeployment', 'constructionCallerIndex', 'inputEntry', 'inputSourceIndex', 'guestEntry',
                'runId', 'outputRoot', 'monitorOutputRoot'):
        check(plan[key] is None)
    protocol = plan['comparisonProtocol']
    check(protocol['fixedProposalOrder'] == ['Node-control-1', 'A', 'B', 'C', 'D', 'Node-control-2', 'D', 'C', 'B', 'A'])
    check(protocol['trialsPerArm'] == 2 and protocol['nodeControls'] == 2)
    check(protocol['actualSchedule'] is protocol['actualAcceptance'] is None)
    check(protocol['automaticRetry'] is protocol['replacementTrialAllowed'] is protocol['filterOrGateWaiverAllowed'] is False)
    check(protocol['allTenNamespacesDeclaredBySeparateRootDriverBeforeFirstAction'] is True)
    check(protocol['freshOwnedServerAppCacheBrowserPerTrial'] is True)
    template, parent_template = read(HERE / 'root-authority-template.json'), read(donor / 'root-authority-template.json')
    check(template == dict(parent_template, state='UNISSUED_ROOT_FIXED_COMPLETION_COMPARISON_ARM_' + arm + '_TEMPLATE_V1'))
    unit = plan['parentCaptureUnitEvidence']
    check(unit == dict(old['parentCaptureUnitEvidence'], selectedByteIdenticalHelper=ref(HERE / 'capture-stdout.mjs')))
    check(unit['unitSuiteRerunForThisCopy'] is False)
    check({key: unit['testedHelper'][key] for key in ('sha256', 'bytes')} == {key: unit['selectedByteIdenticalHelper'][key] for key in ('sha256', 'bytes')})
    for key in ('testSource', 'retainedResult', 'independentDataReview'):
        check(ref(Path(unit[key]['path'])) == unit[key])
    record = read(Path(unit['retainedResult']['path']))
    check(record['helper'] == unit['testedHelper'] and record['passed'] is True and record['caseCount'] == 9)
    check(record['wasmGuestOrWasmtimeOrNetworkExecuted'] is False)
    print(json.dumps(dict(state='FIXED_COMPARISON_RUNTIME_SOURCE_CHECKS_PASSED_V1', arm=arm,
        checks=count, passed=True, actualBindingsPending=pending, sixOperationalFilesByteIdentical=True,
        javaScriptHelperGuardNodeActorExecuted=False, helperUnitSuiteRerun=False,
        priorByteIdenticalHelperUnitCases=9, actualRuntime=None)))


if __name__ == '__main__':
    main()
