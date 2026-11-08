"""Prepare then run one stock wasmCloud compression-off full-contract owner.

Source derivative of the reviewed no-compress run-controls.unbound.py (06a24923,
20909 bytes). Root alone may bind/execute this file. No port is reserved across
preparation and launch: the actor must lease the issued origin once or fail.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
BINDINGS = None
PREPARER = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'),
    sha256='4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', bytes=19784)
INNER_AUTHORITY = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/diagnostic-next-construction-authority.json'),
    sha256='23313b9b1858e22df729b379c10750cd92ba00ce4aa9bee179fc21142fdfea66', bytes=5597386)
INNER_REVIEW = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
    sha256='5c284564e0ddefba507c5429acd98c42393d5c0f2764105a4046f0665f51e16a', bytes=22550)
COMPOSITION_REVIEW = dict(path=str(BASE / 'next-standard-handler-observer-root-results-v1/actual-next-v3-composition-review.json'),
    sha256='b333fbc736e653f0a56bbe7ee031b3b943faf3e4d2ea687112659465171e2387', bytes=33472)
APP_REVIEW = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/actual-build-review.json'),
    sha256='9106545f606ee30b2a3a05940d97233ce3b2e867e6abcdc5c5ec84efa09ad679', bytes=22847)
ASSET_SELECTION = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/asset-selection.json'),
    sha256='05c965a6b536af21c5947ccace5d9c1cc12b129c86a5b2df42e1bb95dd2c5b4c', bytes=7350)
BROWSER_INDEX = dict(path=str(BASE / 'next-fs-callback-no-compress-browser-v1/index.json'),
    sha256='83071f52e7106755164d7880fda21f50afdacfed323e1b01d5275be6d52a6863', bytes=839)
WORKER = dict(path=str(BASE / 'next-fs-callback-no-compress-browser-v1/browser-check.mjs'),
    sha256='01caabc8dae9f684d7e7c9f70b413223811fd06fba3be546ce733c153d37072b', bytes=32170)
OUTPUT_PREFIX = '/private/tmp/starling-node-compat/next-fs-callback-no-compress-wasmcloud-v1'
RUN_ID = 'fs-no-compress-wasmcloud-first'
PUBLIC = dict(headerName='x-next-public-request-correlation',
    nonceByTest={'client-counter': '7' * 64, 'server-action': '8' * 64})


def canonical_origin(value):
    assert type(value) is str and value.startswith('http://127.0.0.1:')
    port = value.removeprefix('http://127.0.0.1:')
    assert port.isascii() and port.isdecimal() and port == str(int(port))
    assert 1 <= int(port) <= 65535 and int(port) != 80
    assert value == 'http://127.0.0.1:' + str(int(port))
    return value


def context():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and type(BINDINGS) is dict, 'Unbound Source refuses helper import/action'
    path = Path(PREPARER['path'])
    raw = path.read_bytes()
    assert path.resolve() == path and not path.is_symlink() and path.stat().st_nlink == 1
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (PREPARER['sha256'], PREPARER['bytes'])
    spec = importlib.util.spec_from_file_location('genuine_no_compress_cloud_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    binding = prep.document(BINDINGS)
    assert binding['state'] == 'ROOT_FS_NO_COMPRESS_WASMCLOUD_ACTUAL_BINDINGS_V1'
    assert binding['applicationBuildReview'] == APP_REVIEW and binding['assetSelection'] == ASSET_SELECTION
    assert binding['innerConstructionReview'] == INNER_REVIEW and binding['compositionReview'] == COMPOSITION_REVIEW
    assert binding['browserIndex'] == BROWSER_INDEX
    actor_root = BASE / 'next-fs-callback-no-compress-wasmcloud-v1'
    client_root = BASE / 'next-fs-callback-no-compress-wasmcloud-client-v1'
    assert Path(binding['actorIndex']['path']).parent == actor_root
    assert Path(binding['clientIndex']['path']).parent == client_root
    actor_index = prep.family(binding['actorIndex'])
    client_index = prep.family(binding['clientIndex'])
    browser_index = prep.family(BROWSER_INDEX)
    assert binding['plan']['path'] == str(actor_root / 'plan.json')
    assert any(dict(r, path=str(actor_root / r['path'])) == binding['plan'] for r in actor_index['files'])
    plan = prep.document(binding['plan'])
    client_plan_ref = next(dict(r, path=str(client_root / r['path'])) for r in client_index['files'] if r['path'] == 'plan.json')
    client_plan = prep.document(client_plan_ref)
    assert client_plan['suite'] == 'NEXT_FS_NO_COMPRESS_WASMCLOUD_FULL_CONTRACT_CLIENT_V1'
    assert client_plan['controlOnly'] is False and client_plan['actualBrowserSourceBindingPending'] is False
    assert client_plan['allowedOutputPolicies'] == [dict(runId=RUN_ID, output=OUTPUT_PREFIX + '-' + RUN_ID + '/client')]
    requirements = client_plan['sourceRequirements']
    assert set(requirements) == {'manifestReader', 'supplemental', 'portableCacheCollector', 'fixtureContract', 'browserSourceIndex', 'browserWorker'}
    assert requirements['browserSourceIndex'] == BROWSER_INDEX and requirements['browserWorker'] == WORKER
    protected = {r['path']: r for r in binding['protectedInputs']}
    assert len(protected) == len(binding['protectedInputs']) and protected
    for ref in requirements.values():
        prep.checked(ref)
        assert protected[ref['path']] == ref, 'Every full-client consumer must be protected'
    app = prep.document(APP_REVIEW)
    assert app['state'] == 'COORDINATED_FS_CALLBACK_NO_COMPRESS_APP_BUILD_DATA_REVIEW_PASSED_V1'
    assert app['verifiedPassed'] is True and app['verifiedDataReviewPassed'] is True
    for key in ('sourceCacheAbsent', 'runtimeCacheMountPolicyCompatible', 'configuredCompressFalseVerified', 'effectiveStandaloneConfigCompressFalseVerified'):
        assert app[key] is True
    assets = prep.document(ASSET_SELECTION)
    assert assets['verifiedPassed'] is True and assets['applicationBuildReview'] == APP_REVIEW
    assert assets['actualBuildResult'] == app['actualResult'] and assets['applicationInputs'] == app['applicationInputs']
    assert assets['applicationRootIdentityEvidence'] == app['applicationRootIdentityEvidence']
    assert assets['applicationRoot'] == app['applicationRoot']
    browser_root = Path(BROWSER_INDEX['path']).parent
    browser_plan_ref = next(dict(r, path=str(browser_root / r['path'])) for r in browser_index['files'] if r['path'] == 'plan.json')
    browser_plan = prep.document(browser_plan_ref)
    assert browser_plan['actualAssetBindingsPending'] is False
    for key, expected in [('applicationInputs', app['applicationInputs']), ('actualApplicationBuildReview', APP_REVIEW),
            ('actualAssetSelectionReview', ASSET_SELECTION), ('assetSelectionHtml', assets['clientHtml']),
            ('actionsAssetSelectionHtml', assets['actionsHtml']), ('assetPins', assets['assetPins']), ('actionsAssetPins', assets['actionsAssetPins'])]:
        assert browser_plan[key] == expected
    inner = prep.document(INNER_REVIEW)
    assert inner['verifiedPassed'] is True and inner['completeReturnedImportAuditVerified'] is True
    assert inner['rootAuthority'] == INNER_AUTHORITY
    composition = prep.document(COMPOSITION_REVIEW)
    assert composition['state'] == 'COORDINATED_NEXT_STANDARD_HANDLER_OBSERVER_V3_COMPOSITION_DATA_REVIEW_PASSED_V1'
    assert composition['verifiedPassed'] is True and composition['verifiedDataReviewPassed'] is True
    assert composition['innerComponent'] == inner['component'] and composition['innerComponentAudit'] == inner['componentAudit']
    assert composition['innerConstructionAuthority'] == INNER_AUTHORITY and composition['innerConstructionReview'] == INNER_REVIEW
    interfaces = composition['selectedImports']
    assert len(interfaces) == len(set(interfaces)) == 13 and all(x.endswith('@0.2.10') for x in interfaces)
    assert composition['selectedExports'] == ['wasi:http/incoming-handler@0.2.10']
    assert sorted(plan['selectedInterfaces']) == sorted(interfaces)
    assert plan['bindingState'] == 'READY_FS_CALLBACK_FULL_CONTRACT' and plan['controlOnly'] is False
    assert plan['expectedAuthorityState'] == 'ROOT_NEXT_FS_NO_COMPRESS_WASMCLOUD_AUTHORIZED_V1'
    assert plan['expectedClientSuite'] == client_plan['suite'] == plan['fsCallbackFullControl']['expectedClientSuite']
    assert plan['outerSeconds'] == 600 and plan['selfOrigin'] is None
    assert plan['namespacePolicy']['plannedOutputPrefix'] == OUTPUT_PREFIX
    assert plan['namespacePolicy']['plannedRunId'] == RUN_ID
    assert plan['prospectiveFsCallbackAppBindingsPending'] is False and plan['prospectiveEnvelopeBindingsPending'] is False
    assert plan['fsCallbackFullControl']['fullClientSourcePending'] is False
    assert plan['fsCallbackFullControl']['requiredFullClientIndex'] == binding['clientIndex']
    assert plan['fsCallbackFullControl']['requiredFullClient'] == plan['clientSource']
    assert plan['clientSourceIndex'] == binding['clientIndex'] and plan['browserSourceIndex'] == BROWSER_INDEX
    assert plan['browserSource'] == WORKER
    assert plan['clientSource']['path'] == str(client_root / 'run-contracts.mjs')
    assert any(dict(r, path=str(client_root / r['path'])) == plan['clientSource'] for r in client_index['files'])
    assert any(dict(r, path=str(browser_root / r['path'])) == WORKER for r in browser_index['files'])
    assert plan['applicationBuildReview'] == APP_REVIEW and plan['applicationBuildResult'] == app['actualResult']
    assert plan['applicationInputs'] == app['applicationInputs'] and plan['applicationSource'] == app['applicationRoot']
    assert plan['applicationRootIdentityEvidence'] == app['applicationRootIdentityEvidence']
    assert plan['acceptedConstructionReview'] == INNER_REVIEW
    assert plan['expectedComponent'] == {k: inner['component'][k] for k in ('sha256', 'bytes')}
    assert plan['expectedEnvelopeBindings'] == dict(envelope=composition['envelope'], compositionReview=COMPOSITION_REVIEW)
    assert plan['outputPrefix'] == OUTPUT_PREFIX and plan['runId'] == RUN_ID
    for ref in plan['protectedInputs']:
        assert protected[ref['path']] == ref
    self_ref = prep.row(Path(__file__).resolve())

    def protect():
        for ref in [PREPARER, INNER_AUTHORITY, INNER_REVIEW, COMPOSITION_REVIEW, APP_REVIEW, ASSET_SELECTION, BROWSER_INDEX, BINDINGS, self_ref]:
            prep.checked(ref)
        for ref in [binding['actorIndex'], binding['clientIndex'], BROWSER_INDEX, *plan['sourceFamilies']]:
            prep.family(ref)
        for ref in binding['protectedInputs']:
            prep.checked(ref)
        for key in ('node', 'monitor', 'wash'):
            prep.checked(plan[key])

    protect()
    original = prep.document(INNER_AUTHORITY)
    before = prep.admit(original)
    return prep, binding, plan, inner, composition, self_ref, protect, original, before


def make_authority(binding, plan, inner, composition, origin):
    return dict(schemaVersion=1, state='ROOT_NEXT_FS_NO_COMPRESS_WASMCLOUD_AUTHORIZED_V1',
        unissued=False, runId=RUN_ID, selfOrigin=canonical_origin(origin), sourceIndex=binding['actorIndex'], plan=binding['plan'],
        controlOnly=False, fsCallbackFullSuiteAllowed=True, publicRequestCorrelationAllowed=True, publicRequestCorrelation=PUBLIC,
        standardHandlerObserverAllowed=True, localhostServeAllowed=True, actualNextGuestAllowed=True, browserAllowed=True,
        stockHostAllowed=True, configInspectAllowed=True, guestEnvironmentAllowed=True, outgoingHttpWorkloadSelected=True,
        compilerAllowed=False, nativeBuildAllowed=False, componentConstructionAllowed=False, externalDeploymentAllowed=False,
        adoptionAllowed=False, hostMutationAllowed=False, automaticRetryAllowed=False, newServicesAllowed=False,
        automaticRetry=False, replacementTrials=False, fullNextAccepted=False,
        component=inner['component'], componentAudit=inner['componentAudit'], constructionResult=inner['actualResult'],
        constructionCallerIndex=inner['callerSourceIndex'], inputSourceIndex=inner['inputSourceIndex'], inputEntry=inner['inputEntry'],
        envelope=composition['envelope'], compositionReview=COMPOSITION_REVIEW)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare', action='store_true')
    modes.add_argument('--run', action='store_true')
    args = parser.parse_args()
    prep, binding, plan, inner, composition, self_ref, protect, original, before = context()
    assert shutil.disk_usage('/private/tmp').free >= 1024**3
    output = Path(OUTPUT_PREFIX + '-' + RUN_ID)
    logs = Path(str(output) + '-external-root')
    authority_path = HERE / 'control-authority.json'
    prepared_path = HERE / 'control-preparation.json'
    receipt = HERE / 'owner-result.json'
    if args.prepare:
        assert all(not p.exists() and not p.is_symlink() for p in (output, logs, authority_path, prepared_path, receipt))
        # One ephemeral choice; this socket is closed before publishing the authority.
        # The interval until the actor's own exact lease is an unreserved race.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as selected:
            selected.bind(('127.0.0.1', 0))
            host, port = selected.getsockname()
            assert host == '127.0.0.1'
            origin = canonical_origin('http://127.0.0.1:' + str(port))
        ar = prep.save(authority_path, make_authority(binding, plan, inner, composition, origin))
        assert prep.admit(original) == before
        protect()
        prep.save(prepared_path, dict(schemaVersion=1, state='ROOT_FS_NO_COMPRESS_WASMCLOUD_PREPARED_NOT_RUN_V1',
            controller=self_ref, bindings=BINDINGS, authority=ar, outputRoot=str(output), ownerOutputRoot=str(logs), ownerSeconds=600,
            selfOrigin=origin, portSelectionSocketClosedBeforeAuthorityPublication=True, portReservationOrHandoffGuaranteed=False,
            actorMustLeaseExactOriginOnce=True, fallbackAllowed=False, constructorGuardBefore=before,
            actorsInvoked=False, automaticRetry=False, replacementTrials=False, fullOriginalContractExecuted=False, fullNextAccepted=False))
        print(json.dumps(dict(prepared=prep.row(prepared_path), actorsInvoked=False)))
        return 0
    prepared_ref = prep.row(prepared_path)
    prepared = prep.document(prepared_ref)
    assert prepared['controller'] == self_ref and prepared['bindings'] == BINDINGS
    assert prepared['state'] == 'ROOT_FS_NO_COMPRESS_WASMCLOUD_PREPARED_NOT_RUN_V1'
    assert prepared['outputRoot'] == str(output) and prepared['ownerOutputRoot'] == str(logs) and prepared['ownerSeconds'] == 600
    assert prepared['portReservationOrHandoffGuaranteed'] is False and prepared['fallbackAllowed'] is False
    ar = prepared['authority']
    assert ar['path'] == str(authority_path)
    assert prep.document(ar) == make_authority(binding, plan, inner, composition, prepared['selfOrigin'])
    assert all(not p.exists() and not p.is_symlink() for p in (output, logs, receipt))
    node = plan['node']
    actor = Path(binding['actorIndex']['path']).parent
    argv = [node['path'], str(actor / 'deploy.mjs'), ar['path']]
    monitor = prep.original(plan['monitor'], 'genuine_no_compress_cloud_original_owner')
    env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
    env.update(PATH=str(Path(node['path']).parent) + ':/usr/bin:/bin', NODE_ENV='production', NEXT_TELEMETRY_DISABLED='1', CI='1')
    logs.mkdir(mode=0o700)
    terminal, primary, after, preserved = None, None, None, False
    secondary = []
    try:
        terminal = monitor.monitor(argv, plan['cwd'], env, logs, 600, ar)
    except BaseException as error:
        primary = error
    finally:
        try:
            after = prep.admit(original)
            assert after == before
            protect()
            prep.checked(ar)
            prep.checked(prepared_ref)
            preserved = True
        except BaseException as error:
            if primary is None:
                primary = error
            else:
                secondary.append(dict(name=type(error).__name__, message=str(error)[:2048]))
        clean = terminal is not None and not terminal['timeout'] and not terminal['forcedCleanup'] and terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and all(not terminal[k] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
        try:
            result = dict(schemaVersion=1, state='ROOT_FS_NO_COMPRESS_WASMCLOUD_ORIGINAL_OWNER_COMPLETED_UNREVIEWED_V1',
                rawExitCode=None if terminal is None else terminal['rawExitCode'], originalOwner=None if terminal is None else terminal['pid'],
                cleanOwner=clean, finalInputsPreserved=preserved, error=None if primary is None else dict(name=type(primary).__name__, message=str(primary)[:2048]),
                secondaryErrors=secondary, authority=ar, controller=self_ref, bindings=BINDINGS,
                terminal=prep.row(logs / 'terminal.json') if (logs / 'terminal.json').is_file() else None,
                constructorGuardBefore=before, constructorGuardAfter=after,
                fullOriginalContractExecutionClaimedByOwnerReceipt=False, fullNextAccepted=False)
            rr = prep.save(receipt, result)
            print(json.dumps(dict(receipt=rr, rawExitCode=result['rawExitCode'], cleanOwner=clean)))
        except BaseException:
            if primary is not None:
                raise primary
            raise
    if primary is not None:
        raise primary
    return 0 if clean and preserved and terminal['rawExitCode'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
