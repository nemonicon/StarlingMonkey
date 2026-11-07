"""Finite Source/text-DATA binding checks; no actor, guard, JavaScript or binary loads."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'next-fetch-resource-lifecycle-runtime-candidate-v1'
CODE = ['admission.py', 'control.mjs', 'guest-http.mjs', 'io.mjs', 'models.py', 'phase-owner.py', 'run-owned.py']
TEMPLATES = ['root-authority.template.json', 'phase-authority.template.json']
CHECKS = 0


def check(value, message):
    global CHECKS
    if value is not True:
        raise ValueError(message)
    CHECKS += 1


def read(path):
    return json.loads(Path(path).read_bytes())


def descriptor(path):
    data = Path(path).read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def text(ref):
    # Deliberately no component/engine/tool binary reads, no recursive closure.
    check(Path(ref['path']).suffix in ['.json', '.py', '.mjs'], 'only explicit Source/text DATA')
    check(descriptor(ref['path']) == ref, 'genuine text descriptor')
    return read(ref['path']) if Path(ref['path']).suffix == '.json' else None


def main():
    old, plan = read(OLD / 'plan.json'), read(HERE / 'plan.json')
    check(plan['preservedUnboundRuntimeSourceIndex'] == descriptor(OLD / 'index.json'), 'preserved unbound Source')
    for name in CODE + TEMPLATES:
        check((HERE / name).read_bytes() == (OLD / name).read_bytes(), 'unchanged code/template ' + name)
    for name in ['admission.py', 'models.py', 'phase-owner.py', 'run-owned.py', 'test-source.py']:
        ast.parse((HERE / name).read_text(), filename=name)
    check(plan['prospectiveActualBindingsPending'] is False and plan['prospectiveConstructorContractOnly'] is False, 'genuine binding readiness')
    check(old['prospectiveActualBindingsPending'] is True and all(x is None for x in old['expectedBindings'].values()), 'prior remains unbound')
    changed = {'state', 'prospectiveActualBindingsPending', 'prospectiveConstructorContractOnly', 'expectedBindings', 'sourceFamilies', 'preservedUnboundRuntimeSourceIndex'}
    check(set(plan) == set(old) | {'preservedUnboundRuntimeSourceIndex'}, 'only declared new plan field')
    check({k for k in old if plan[k] != old[k]} == changed - {'preservedUnboundRuntimeSourceIndex'}, 'exact finite plan delta')
    check(plan['outputPrefix'] == old['outputPrefix'] and plan['controllerSeconds'] == 600 and plan['nodeReferenceSeconds'] == plan['guestOwnerSeconds'] == 180, 'same prefix and original owner sequence')
    check(plan['directServerExpectedExitCode'] == 130 and plan['requestSeconds'] == 120, 'direct control130 and HTTP120 unchanged')
    bindings = plan['expectedBindings']
    check(set(bindings) == set(old['expectedBindings']) and len(bindings) == 15, 'same15binding roles')
    for ref in bindings.values():
        check(type(ref) is dict and set(ref) == {'path','sha256','bytes'} and type(ref['bytes']) is int and ref['bytes'] > 0, 'plain actual descriptor')
    review = text(bindings['constructionDataReview'])
    result = text(bindings['constructionResult'])
    ctor = text(result['rootAuthority'])
    cp = text(bindings['constructionPlan'])
    build_review = text(bindings['fullNativeBuildReview'])
    build_result = text(bindings['fullNativeBuildResult'])
    build_observation = text(bindings['fullNativeBuildObservation'])
    native = text(bindings['nativeMetadata'])
    check(review['state'] == plan['prospectiveConstructorReviewState'] and review['verifiedPassed'] is review['completeReturnedImportAuditVerified'] is True, 'accepted actual lifecycle review wire')
    aliases = {'actualResult':'constructionResult','callerIndex':'constructionCallerIndex','plan':'constructionPlan','component':'component','componentAudit':'componentAudit','engine':'engine','nativeMetadata':'nativeMetadata','fullBuildReview':'fullNativeBuildReview'}
    for reviewed, key in aliases.items():
        check(review[reviewed] == bindings[key], 'actual review role ' + key)
    check(review['rootAuthority'] == result['rootAuthority'] and review['inputSourceIndex'] == plan['probeSourceIndex'] and review['inputEntry'] == plan['probeEntry'], 'genuine result/unchanged probe roles')
    check(result['passed'] is True and result['error'] is None and result['entryMode'] == ctor['entryMode'] == 'lifecycle' and result['finalProtection']['unchanged'] is True, 'actual INIT-only success')
    check(result['callerIndex'] == bindings['constructionCallerIndex'] and result['plan'] == bindings['constructionPlan'], 'actual constructor caller/plan')
    check(cp['entries'] == {'lifecycle':plan['probeEntry']} and cp['inputSourceIndex'] == plan['probeSourceIndex'], 'only exact lifecycle selector')
    check(plan['sourceFamilies'] == old['sourceFamilies'] + [plan['preservedUnboundRuntimeSourceIndex'], bindings['constructionCallerIndex']], 'append-only Source ancestry')
    for key in ['component','componentAudit','engine','nativeMetadata']:
        check(result['artifacts'][key] == bindings[key], 'actual artifact role ' + key)
    check(ctor['engine'] == bindings['engine'] and ctor['nativeMetadata'] == bindings['nativeMetadata'], 'actual fresh native constructor inputs')
    imports = text(review['returnedImports'])
    check(result['artifacts']['returnedImports'] == review['returnedImports'] and type(imports) is list and type(review['actualReturnedImportFunctionCount']) is int and review['actualReturnedImportFunctionCount'] > 0 and review['actualReturnedImportFunctionCount'] == len(imports), 'actual observed complete import count, no fixed131 gate')
    for key in ['ordinaryExportsInvoked','httpServed','appMountedAtInit','filesystemFixtureMountedAtInit','deployedFetchProbeInvoked','runtimeAccepted','nodeParityProved','productionProfilePromoted']:
        check(review[key] is False, 'INIT scope ' + key)
    check(build_review['verifiedPassed'] is True and build_review['actualResult'] == bindings['fullNativeBuildResult'] and build_review['metadata'] == bindings['nativeMetadata'], 'accepted full-build roles')
    check(build_review['engine'] == bindings['engine'] and build_review['actualRootObservation'] == bindings['fullNativeBuildObservation'], 'full-build actual engine/outer')
    check(build_result['passed'] is True and build_result['metadata'] == bindings['nativeMetadata'] and build_result['engineCandidate'] == bindings['engine'], 'actual full-build result')
    check(build_observation['workerResult'] == bindings['fullNativeBuildResult'] and build_observation['ownedCleanRawZero'] is True, 'actual build observation')
    check(native['engine'] == bindings['engine'] and native['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1' and bindings['fullNativeBuildSourceIndex'] == plan['requiredBuildSourceIndex'], 'whole genuine metadata generation')
    cleanup = next(x for x in native['nativePolicyInputManifest'] if x['path'] == 'builtins/web/fetch/request-response.cpp')
    check(cleanup['sha256'] == plan['requiredSelectedRequestResponseAfterimage']['sha256'] and cleanup['bytes'] == plan['requiredSelectedRequestResponseAfterimage']['bytes'], 'actual selected corrected cleanup TU')
    audit = text(bindings['componentAudit'])
    check(audit['passed'] is True and audit['component'] == bindings['component'] and audit['entryMode'] == 'lifecycle', 'actual component audit')
    check(set(audit['emittedImports']) == set(plan['selectedInterfaces']) and len(audit['emittedImports']) == len(set(audit['emittedImports'])) == 13 and audit['allEmittedVersion'] == '0.2.10', 'exact standard13 audit')
    start, terminal, world = (text(bindings[k]) for k in ['constructionRootStarted','constructionRootTerminal','constructionWorldGuard'])
    check(start['pid'] == terminal['pid'] and start['authority'] == terminal['authority'] == result['rootAuthority'] and start['timeoutSeconds'] == 2400, 'actual original constructor owner')
    check(type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0 and terminal['timeout'] is terminal['forcedCleanup'] is False and terminal['errors'] == [], 'raw0/no timeout/error')
    check(terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True, 'constructor clean groups')
    check(world['unchanged'] is True and world['before'] == world['after'] and world['before']['sourceIndex'] == plan['worldSourceIndex'], 'whole unchanged canonical world')
    check(world['before']['members'] == 28 and world['before']['witFiles'] == 8, 'world28/8 unchanged')
    check(all(plan[k] is None for k in ['actualRootAuthority','actualControl','actualNodeReference','actualGuest','actualResults']), 'runtime actuals unissued/unobserved')
    print(json.dumps(dict(state='BOUND_LIFECYCLE_RUNTIME_SOURCE_TEXT_CHECKS_PASSED_V2', checks=CHECKS,
          pythonASTs=5, byteIdenticalCodeModules=len(CODE), byteIdenticalTemplates=len(TEMPLATES), actualBindingCount=15,
          actualImportCountHardcoded=False, javascriptParsedOrExecuted=False, guardsOrActorsInvoked=False,
          engineOrComponentBinaryRead=False, publicLifecycleRuntimeAccepted=False)))


if __name__ == '__main__':
    main()
