"""Finite byte/JSON Source checks, without JavaScript parsing, guards or actors."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DONOR = HERE.parent / 'next-portable-cache-native-candidate-v1'
CODE = ['app-policy.mjs','deploy.mjs','browser-check.mjs','run-owned.py','run-contracts.mjs','test-gates.mjs']
COUNT = 0


def check(value, message):
    global COUNT
    if value is not True:
        raise ValueError(message)
    COUNT += 1


def read(path):
    return json.loads(Path(path).read_bytes())


def descriptor(path):
    data = Path(path).read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    old, plan = read(DONOR/'plan.json'), read(HERE/'plan.json')
    check(plan['preservedPortableCacheNativeV1'] == descriptor(DONOR/'index.json'), 'closed donor')
    for name in CODE:
        check((HERE/name).read_bytes() == (DONOR/name).read_bytes(), 'exact donor bytes ' + name)
    changed = {'state','sourceFamilies','protectedInputs','outputPrefix','expectedComponent','acceptedConstructionReview','expectedEngine','expectedNativeMetadata','browserSource'}
    added = {'preservedPortableCacheNativeV1','prospectiveActualBindingsPending','cleanupConstructionSourceIndex','requiredCurrentInteropRuntimeReview'}
    check(set(plan) == set(old) | added, 'only finite added plan fields')
    check({k for k in old if plan[k] != old[k]} == changed, 'only declared existing plan deltas')
    check(plan['sourceFamilies'] == old['sourceFamilies'] + [plan['preservedPortableCacheNativeV1'], plan['cleanupConstructionSourceIndex']], 'append-only Source ancestry')
    check(plan['protectedInputs'][:len(old['protectedInputs'])] == old['protectedInputs'], 'old protection prefix unchanged')
    check(plan['requiredCurrentInteropRuntimeReview'] in plan['protectedInputs'][len(old['protectedInputs']):], 'current generation interoperability evidence protected')
    check(plan['browserSource'] == descriptor(HERE/'browser-check.mjs'), 'same browser code, own physical copy')
    for key in ['portableCacheProfile','supplementalConcurrentRegression','requiredObservations','applicationInputs','applicationBuildResult','applicationBuildReview','applicationRootIdentity','applicationSchema','applicationRootIdentityEvidence','readonlyApp','writableCache','wasmtimePolicy','deadlines','shutdown','listener']:
        check(plan[key] == old[key], 'unchanged contract/application/policy ' + key)
    check(plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-fetch-resource-cleanup-next', 'fresh output namespace')
    check(all(plan[k] is None for k in ['actualRootAuthority','actualConstructionResult','actualComponent','actualComponentAudit','actualDeployment']), 'no runtime action or observations')
    check(descriptor(plan['cleanupConstructionSourceIndex']['path']) == plan['cleanupConstructionSourceIndex'], 'held cleanup constructor Source index')
    caller = read(plan['cleanupConstructionSourceIndex']['path'])
    cp = read(Path(plan['cleanupConstructionSourceIndex']['path']).parent/'plan.json')
    check(cp['entries'].keys() == {'real-next'} and cp['entries']['real-next']['sha256'].startswith('1e49dd') and cp['inputSourceIndex']['sha256'].startswith('73b583'), 'unchanged real-Next guest selector')
    check(plan['requiredCurrentInteropRuntimeReview'] == cp['requiredInteropRuntimeReviewForRootAuthority'], 'current55a descriptor selected by genuine caller')
    check(plan['expectedEngine'] == cp['expectedEngineForRootAuthority'] and plan['expectedNativeMetadata'] == cp['expectedNativeMetadataForRootAuthority'], 'accepted current476b/22f native generation')
    check(any(x['path'] == 'plan.json' and descriptor(Path(plan['cleanupConstructionSourceIndex']['path']).parent/'plan.json') == dict(x,path=str(Path(plan['cleanupConstructionSourceIndex']['path']).parent/'plan.json')) for x in caller['files']), 'indexed actual caller plan')
    pending = plan['prospectiveActualBindingsPending']
    if pending:
        check(plan['acceptedConstructionReview'] is None, 'accepted review remains pending')
        check(plan['expectedComponent'] is None or (set(plan['expectedComponent']) == {'sha256','bytes'} and type(plan['expectedComponent']['bytes']) is int and plan['expectedComponent']['bytes'] > 0), 'component pin may bind actual INIT before review, no invented review')
    else:
        review = read(plan['acceptedConstructionReview']['path'])
        check(descriptor(plan['acceptedConstructionReview']['path']) == plan['acceptedConstructionReview'], 'actual construction review bytes')
        check(review['verifiedPassed'] is True and review['entryMode'] == 'real-next', 'accepted genuine real-Next INIT')
        check(review['callerIndex'] == plan['cleanupConstructionSourceIndex'] and review['engine'] == plan['expectedEngine'] and review['nativeMetadata'] == plan['expectedNativeMetadata'], 'current constructor/native role joins')
        check(plan['expectedComponent'] == {k:review['component'][k] for k in ['sha256','bytes']}, 'actual component pin, no metadata projection')
        check(plan['acceptedConstructionReview'] in plan['protectedInputs'], 'accepted actual review protected')
    print(json.dumps(dict(state='FETCH_CLEANUP_NEXT_RUNTIME_SOURCE_BYTE_JSON_CHECKS_PASSED_V1',checks=COUNT,
          codeFilesByteIdentical=6,constructorBindingPending=pending,javascriptParsedOrExecuted=False,
          guardsOrActorsInvoked=False,engineOrComponentPayloadRead=False,actualNextRuntimeAccepted=False)))


if __name__ == '__main__':
    main()
