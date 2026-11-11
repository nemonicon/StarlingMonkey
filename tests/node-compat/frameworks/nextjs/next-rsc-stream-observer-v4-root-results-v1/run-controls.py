"""Prepare the fixed cloud then bridged-Node full workload and CDP resource observations; run one original owner at a time."""
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
BINDINGS = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-v4-root-results-v1/runtime-bindings.json', 'sha256': 'dcc5e0b7156a2f9b4d66faed7ab8e7102187e1ce24268ac111c8b8d5d03455d8', 'bytes': 622407}
PREPARER = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'),
    sha256='4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', bytes=19784)
INNER_AUTHORITY = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/diagnostic-next-construction-authority.json'),
    sha256='23313b9b1858e22df729b379c10750cd92ba00ce4aa9bee179fc21142fdfea66', bytes=5597386)
INNER_REVIEW = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
    sha256='5c284564e0ddefba507c5429acd98c42393d5c0f2764105a4046f0665f51e16a', bytes=22550)
COMPOSITION_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/actual-next-v4-composition-review.json', 'sha256': '730c2698578692e35789918930d6be1cf8fb837a4e5362bcef5b802919795c2f', 'bytes': 9900}
OBSERVER_COMPOSITION_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/actual-v4-composition-review.json', 'sha256': '214c1d9bcfd1858666d460afe72811b858fc8018e9f5e4bfb9519d8ddbe04224', 'bytes': 11140}
METADATA_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/actual-metadata-runtime-review.json', 'sha256': '61bb6690df9cf8fef3c455314352a95816a20bc01920909b75632bf5333c47c8', 'bytes': 7272}
PUBLIC = dict(headerName='x-next-public-request-correlation',
    nonceByTest={'client-counter': '7' * 64, 'server-action': '8' * 64})


# Required existing reviewed DATA/Source, not issued runtime bindings.
REQUIRED_APP_REVIEW = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/actual-build-review.json'),
    sha256='9106545f606ee30b2a3a05940d97233ce3b2e867e6abcdc5c5ec84efa09ad679', bytes=22847)


def canonical_origin(value):
    assert type(value) is str and value.startswith('http://127.0.0.1:')
    port = value.removeprefix('http://127.0.0.1:')
    assert port.isascii() and port.isdecimal() and port == str(int(port))
    assert 1 <= int(port) <= 65535 and int(port) != 80
    assert value == 'http://127.0.0.1:' + str(int(port))
    return value


ASSET_SELECTION = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/asset-selection.json'), sha256='05c965a6b536af21c5947ccace5d9c1cc12b129c86a5b2df42e1bb95dd2c5b4c', bytes=7350)


def composition_evidence(prep):
    composition = prep.document(COMPOSITION_REVIEW)
    assert composition['state'] == 'COORDINATED_NEXT_STANDARD_HANDLER_OBSERVER_V4_COMPOSITION_DATA_REVIEW_PASSED_V1'
    for key in ('verifiedPassed', 'verifiedDataReviewPassed', 'rawChildBytesVerified', 'siblingDefiningInstancesVerified',
            'sharedNominalResourceAliasesVerified', 'fieldsNominalResourceAliasesVerified', 'metadataGetterCanonicalOptionsVerified',
            'synchronousLiftLowerWithInnerPostReturnVerified', 'innerExplicitPostReturnPreserved', 'observerManualPostReturnAbsent',
            'internalIncomingHandlerImportComposedAway', 'allFourRequestedToolStepsRawZero', 'allFourToolStderrEmpty', 'finalInputsPreserved'):
        assert composition[key] is True
    for key in ('runtimeInvoked', 'runtimeAccepted', 'fullNextAccepted', 'oldV3JoinUpgraded'):
        assert composition[key] is False
    assert composition['observerCompositionReview'] == OBSERVER_COMPOSITION_REVIEW and composition['metadataRuntimeReview'] == METADATA_REVIEW
    observer, metadata = prep.document(OBSERVER_COMPOSITION_REVIEW), prep.document(METADATA_REVIEW)
    assert observer['state'] == 'COORDINATED_STANDARD_HANDLER_OBSERVER_V4_COMPOSITION_DATA_REVIEW_PASSED_V1'
    for key in ('verifiedPassed', 'verifiedDataReviewPassed', 'allSevenRequestedToolStepsRawZero', 'allSevenToolStderrEmpty',
            'observerNoMarkerBeforeInnerCallSourceVerified', 'normalFieldsChildDropBeforeOwnForwardSourceVerified',
            'correlationSnapshotIndependentOfMethodAndPathSourceVerified'):
        assert observer[key] is True
    for key in ('observerBinary', 'observerSource', 'observerManifest', 'observerProtocol'):
        assert observer[key] == composition[key]
    assert metadata['state'] == 'COORDINATED_STANDARD_HANDLER_OBSERVER_V4_METADATA_DATA_REVIEW_PASSED_V1'
    for key in ('verifiedPassed', 'verifiedDataReviewPassed', 'allCollectionsCompletedCleanly', 'actualMetadataBehaviorProved', 'runtimeAccepted', 'cleanOwner', 'finalInputsPreserved'):
        assert metadata[key] is True
    assert metadata['metadataCasesPassed'] == len(metadata['caseResults']) == 7
    assert metadata['rawExitCode'] == 0 and metadata['originalOwnerSeconds'] == 900
    assert metadata['compositionReview'] == OBSERVER_COMPOSITION_REVIEW and metadata['observerBinary'] == composition['observerBinary']
    assert metadata['envelope'] == observer['envelope']
    for key in ('nextWorkloadExecuted', 'fullNextAccepted', 'oldV3JoinUpgraded', 'allocatorOrAbsentPathExecuted', 'recordLimitExecuted'):
        assert metadata[key] is False
    return composition, observer, metadata


def context():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Requires nonoptimized isolated Python with bytecode disabled')
    assert type(BINDINGS) is dict, 'Unbound Source refuses helper import/action'
    path = Path(PREPARER['path'])
    raw = path.read_bytes()
    assert path.resolve() == path and not path.is_symlink() and path.stat().st_nlink == 1
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (PREPARER['sha256'], PREPARER['bytes'])
    spec = importlib.util.spec_from_file_location('genuine_stream_observer_full_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    binding = prep.document(BINDINGS)
    assert binding['state'] == 'ROOT_RSC_STREAM_OBSERVER_V4_ACTUAL_BINDINGS_V1'
    assert binding['compositionReview'] == COMPOSITION_REVIEW and binding['innerConstructionReview'] == INNER_REVIEW
    assert binding['applicationBuildReview'] == REQUIRED_APP_REVIEW and binding['assetSelection'] == ASSET_SELECTION
    selected_host = prep.document(binding['selectedHostTools'])
    assert selected_host['passed'] is True and selected_host['fullWorkloadInvoked'] is False
    assert selected_host['chromeVersion'] == '157.0.8103.39' and selected_host['playwrightVersion'] == '1.64.1'
    assert len(selected_host['hostRequirements']) == 6 and len(selected_host['playwrightPackageFiles']) == 115
    actor_root, client_root, browser_root = (BASE / name for name in ('next-rsc-stream-observer-v4-runtime-v1', 'next-rsc-stream-observer-v4-full-client-v1', 'next-rsc-stream-observer-v4-browser-v1'))
    indices = {}
    for role, folder in (('actorIndex', actor_root), ('clientIndex', client_root), ('browserIndex', browser_root)):
        assert binding[role]['path'] == str(folder / 'index.json')
        indices[role] = prep.family(binding[role])
    def member(role, filename):
        folder = Path(binding[role]['path']).parent
        return next(dict(row, path=str(folder / row['path'])) for row in indices[role]['files'] if row['path'] == filename)
    client_plan = prep.document(member('clientIndex', 'plan.json'))
    browser_plan = prep.document(member('browserIndex', 'plan.json'))
    worker = member('browserIndex', 'browser-check.mjs')
    assert client_plan['suite'] == 'NEXT_RSC_STREAM_OBSERVER_FULL_CONTRACT_CLIENT_V1'
    assert client_plan['controlOnly'] is False and client_plan['actualBrowserSourceBindingPending'] is False
    requirements = client_plan['sourceRequirements']
    assert set(requirements) == {'manifestReader', 'supplemental', 'portableCacheCollector', 'fixtureContract', 'browserSourceIndex', 'browserWorker'}
    assert requirements['browserSourceIndex'] == binding['browserIndex'] and requirements['browserWorker'] == worker
    protected = {row['path']: row for row in binding['protectedInputs']}
    assert len(protected) == len(binding['protectedInputs']) and protected
    for ref in [binding['selectedHostTools'], *selected_host['hostRequirements'], *selected_host['playwrightPackageFiles']]:
        prep.checked(ref)
        assert protected[ref['path']] == ref
    for ref in requirements.values():
        prep.checked(ref)
        assert protected[ref['path']] == ref
    app, assets = prep.document(REQUIRED_APP_REVIEW), prep.document(ASSET_SELECTION)
    assert app['state'] == 'COORDINATED_FS_CALLBACK_NO_COMPRESS_APP_BUILD_DATA_REVIEW_PASSED_V1' and app['buildVersion'] == 1
    for key in ('verifiedPassed', 'verifiedDataReviewPassed', 'sourceCacheAbsent', 'runtimeCacheMountPolicyCompatible', 'configuredCompressFalseVerified', 'effectiveStandaloneConfigCompressFalseVerified'):
        assert app[key] is True
    assert assets['verifiedPassed'] is True and assets['applicationBuildReview'] == REQUIRED_APP_REVIEW
    assert assets['applicationInputs'] == app['applicationInputs'] and assets['applicationRoot'] == app['applicationRoot']
    assert browser_plan['actualAssetBindingsPending'] is False
    for key, value in (('applicationInputs', app['applicationInputs']), ('actualApplicationBuildReview', REQUIRED_APP_REVIEW), ('actualAssetSelectionReview', ASSET_SELECTION), ('assetSelectionHtml', assets['clientHtml']), ('actionsAssetSelectionHtml', assets['actionsHtml']), ('assetPins', assets['assetPins']), ('actionsAssetPins', assets['actionsAssetPins']), ('actualActionManifest', binding['actualActionManifest']), ('requiredActionId', binding['requiredActionId'])):
        assert browser_plan[key] == value
    policy = browser_plan['resourceStreamObservationPolicy']
    assert policy['version'] == 1 and policy['commandTrigger'] == 'first-qualified-requestWillBeSent'
    assert [policy[k] for k in ('bodyLimitBytes', 'chunkLimit', 'metadataEventLimit', 'metadataBytes')] == [4194304, 65536, 1024, 262144]
    assert protected[binding['actualActionManifest']['path']] == binding['actualActionManifest']
    manifest = prep.document(binding['actualActionManifest'])
    action = manifest['node'][binding['requiredActionId']]
    assert action['exportedName'] == 'submitFixture' and action['filename'] == 'app/actions/actions.js'
    assert set(action['workers']) == {'app/actions/page'}
    inner = prep.document(INNER_REVIEW)
    composition, observer_composition, metadata_review = composition_evidence(prep)
    assert binding['observerCompositionReview'] == OBSERVER_COMPOSITION_REVIEW and binding['metadataRuntimeReview'] == METADATA_REVIEW
    assert inner['verifiedPassed'] is True and inner['rootAuthority'] == INNER_AUTHORITY and inner['completeReturnedImportAuditVerified'] is True
    assert composition['verifiedPassed'] is True and composition['verifiedDataReviewPassed'] is True
    assert composition['innerComponent'] == inner['component'] and composition['innerConstructionAuthority'] == INNER_AUTHORITY
    assert len(composition['selectedImports']) == 13 and all(x.endswith('@0.2.10') for x in composition['selectedImports'])
    assert composition['selectedExports'] == ['wasi:http/incoming-handler@0.2.10']
    plans = {arm: prep.document(binding[arm + 'Plan']) for arm in ('cloud', 'stock')}
    for arm, plan in plans.items():
        assert binding[arm + 'Plan'] == member('actorIndex', 'plan.json' if arm == 'cloud' else 'stock-plan.json')
        assert plan['bindingState'] == 'READY_FULL_CLIENT_FULL_CONTRACT' and plan['controlOnly'] is False
        assert plan['prospectiveFullClientBindingsPending'] is False and plan['fullClientFullContract']['clientSourcePending'] is False
        assert plan['expectedClientSuite'] == client_plan['suite'] == plan['fullClientFullContract']['expectedClientSuite']
        assert plan['fullClientFullContract']['requiredClientIndex'] == binding['clientIndex']
        assert plan['fullClientFullContract']['requiredClient'] == plan['clientSource'] == member('clientIndex', 'run-contracts.mjs')
        assert plan['clientSourceIndex'] == binding['clientIndex'] and plan['browserSourceIndex'] == binding['browserIndex'] and plan['browserSource'] == worker
        assert plan['applicationBuildReview'] == REQUIRED_APP_REVIEW and plan['applicationBuildResult'] == app['actualResult']
        assert plan['applicationInputs'] == app['applicationInputs'] and plan['applicationRootIdentityEvidence'] == app['applicationRootIdentityEvidence']
        assert plan['node'] == plans['cloud']['node'] and plan['monitor'] == plans['cloud']['monitor']
        assert plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-rsc-stream-observer-v4-' + arm + '-v1'
        assert plan['runId'] == 'rsc-stream-observer-v4-' + arm + '-first'
        assert plan['namespacePolicy']['plannedOutputPrefix'] == plan['outputPrefix'] and plan['namespacePolicy']['plannedRunId'] == plan['runId']
        if arm == 'cloud':
            assert plan['outerSeconds'] == 600
        assert plan['browserTools'] == selected_host['browserTools'] and plan['selectedHostTools'] == binding['selectedHostTools']
    assert client_plan['allowedOutputPolicies'] == [dict(runId=plans[arm]['runId'], output=plans[arm]['outputPrefix'] + '-' + plans[arm]['runId'] + '/client') for arm in ('cloud', 'stock')]
    assert plans['cloud']['applicationSchema']['additionalDirectories'] == []
    assert plans['cloud']['applicationSchema']['ownedDirectoriesIncludingRoot'] == plans['cloud']['applicationSchema']['directoriesExcludingRoot'] + 1
    assert plans['cloud']['selfOrigin'] is None and plans['cloud']['applicationSource'] == app['applicationRoot']
    assert plans['stock']['standaloneSource'] == app['applicationRoot']
    assert sorted(plans['cloud']['selectedInterfaces']) == sorted(composition['selectedImports'])
    self_ref = prep.row(Path(__file__).resolve())
    def protect():
        for ref in (PREPARER, INNER_AUTHORITY, INNER_REVIEW, COMPOSITION_REVIEW, OBSERVER_COMPOSITION_REVIEW, METADATA_REVIEW, REQUIRED_APP_REVIEW, ASSET_SELECTION, BINDINGS, self_ref):
            prep.checked(ref)
        for role in ('actorIndex', 'clientIndex', 'browserIndex'):
            prep.family(binding[role])
        for ref in binding['protectedInputs']:
            prep.checked(ref)
        for plan in plans.values():
            for ref in plan['sourceFamilies']:
                prep.family(ref)
            for ref in plan['protectedInputs']:
                prep.checked(ref)
    protect()
    authority = prep.document(INNER_AUTHORITY)
    before = prep.admit(authority)
    return prep, binding, plans, inner, composition, self_ref, protect, authority, before


def make_authority(arm, binding, plans, inner, composition, origin=None):
    common = dict(schemaVersion=1, arm=arm, runId=plans[arm]['runId'], sourceIndex=binding['actorIndex'],
        controlOnly=False, fullClientFullContractAllowed=True, rscStreamObserverAllowed=True, publicRequestCorrelationAllowed=True,
        publicRequestCorrelation=PUBLIC, compilerAllowed=False, nativeBuildAllowed=False,
        automaticRetry=False, replacementTrials=False, fullNextAccepted=False)
    if arm == 'cloud':
        return dict(common, state='ROOT_NEXT_RSC_STREAM_OBSERVER_V4_CLOUD_AUTHORIZED_V1',
            plan=binding['cloudPlan'], component=inner['component'], componentAudit=inner['componentAudit'],
            constructionResult=inner['actualResult'], constructionCallerIndex=inner['callerSourceIndex'],
            inputSourceIndex=inner['inputSourceIndex'], inputEntry=inner['inputEntry'],
            envelope=composition['envelope'], compositionReview=COMPOSITION_REVIEW,
            localhostServeAllowed=True, actualNextGuestAllowed=True, browserAllowed=True,
            selfOrigin=canonical_origin(origin), stockHostAllowed=True, configInspectAllowed=True,
            guestEnvironmentAllowed=True, outgoingHttpWorkloadSelected=True,
            hostMutationAllowed=False, automaticRetryAllowed=False, newServicesAllowed=False,
            standardHandlerObserverAllowed=True, componentConstructionAllowed=False,
            externalDeploymentAllowed=False, adoptionAllowed=False)
    return dict(common, state='ROOT_NEXT_RSC_STREAM_OBSERVER_V4_HOST_AUTHORIZED_V1',
        plans=binding['stockPlan'], rootAuthorityPath=str(HERE / 'stock-authority.json'),
        localhostServerAllowed=True, browserAllowed=True, guestAllowed=False, engineAllowed=False,
        externalApplicationDeploymentAllowed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare', action='store_true')
    modes.add_argument('--run', choices=['cloud', 'stock'])
    args = parser.parse_args()
    prep, binding, plans, inner, composition, self_ref, protect, original, before = context()
    assert shutil.disk_usage('/private/tmp').free >= 1024**3
    prepared_path = HERE / 'control-preparation.json'
    if args.prepare:
        assert not prepared_path.exists() and not prepared_path.is_symlink()
        slots = []
        for arm in ('cloud', 'stock'):
            path = HERE / (arm + '-authority.json')
            output = Path(plans[arm]['outputPrefix'] + '-' + plans[arm]['runId'])
            assert all(not x.exists() and not x.is_symlink() for x in (path, output, Path(str(output) + '-external-root'), HERE / (arm + '-owner-result.json')))
            slots.append((arm, path, output))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as selected:
            selected.bind(('127.0.0.1', 0))
            host, port = selected.getsockname()
            assert host == '127.0.0.1'
            cloud_origin = canonical_origin('http://127.0.0.1:' + str(port))
        # Closed selection socket is not a reservation/handoff; cloud must lease it once.
        rows = []
        for arm, path, output in slots:
            rows.append(dict(arm=arm, authority=prep.save(path, make_authority(arm, binding, plans, inner, composition, cloud_origin)),
                outputRoot=str(output), ownerOutputRoot=str(output) + '-external-root', ownerSeconds=600 if arm == 'cloud' else 300))
        assert prep.admit(original) == before
        protect()
        prep.save(prepared_path, dict(schemaVersion=1, state='ROOT_FIXED_RSC_STREAM_OBSERVER_V4_FULL_PAIR_PREPARED_NOT_RUN_V1',
            controller=self_ref, bindings=BINDINGS, trials=rows, order=['cloud', 'stock'], publicRequestCorrelation=PUBLIC,
            cloudSelfOrigin=cloud_origin, portSelectionSocketClosedBeforeAuthorityPublication=True,
            portReservationOrHandoffGuaranteed=False, actorMustLeaseExactOriginOnce=True, fallbackAllowed=False,
            constructorGuardBefore=before, actorsInvoked=False, automaticRetry=False, replacementTrials=False,
            oldRedirectFailuresWaived=False, fullOriginalContractExecuted=False, fullNextAccepted=False))
        print(json.dumps(dict(prepared=prep.row(prepared_path), actorsInvoked=False)))
        return 0
    arm = args.run
    prepared_ref = prep.row(prepared_path)
    prepared = prep.document(prepared_ref)
    assert prepared['controller'] == self_ref and prepared['bindings'] == BINDINGS
    assert prepared['state'] == 'ROOT_FIXED_RSC_STREAM_OBSERVER_V4_FULL_PAIR_PREPARED_NOT_RUN_V1'
    assert prepared['portReservationOrHandoffGuaranteed'] is False and prepared['fallbackAllowed'] is False
    assert prepared['order'] == ['cloud', 'stock'] and [x['arm'] for x in prepared['trials']] == ['cloud', 'stock']
    for item in prepared['trials']:
        expected_output = plans[item['arm']]['outputPrefix'] + '-' + plans[item['arm']]['runId']
        assert item['outputRoot'] == expected_output and item['ownerOutputRoot'] == expected_output + '-external-root'
        assert item['ownerSeconds'] == (600 if item['arm'] == 'cloud' else 300)
    trial = next(x for x in prepared['trials'] if x['arm'] == arm)
    ar = trial['authority']
    cloud_origin = prepared['cloudSelfOrigin']
    assert prep.document(ar) == make_authority(arm, binding, plans, inner, composition, cloud_origin)
    if arm == 'stock':
        try:
            previous = prep.document(prep.row(HERE / 'cloud-owner-result.json'))
            cloud_trial = next(x for x in prepared['trials'] if x['arm'] == 'cloud')
            assert previous['controller'] == self_ref and previous['bindings'] == BINDINGS
            assert previous['authority'] == cloud_trial['authority']
            assert prep.document(previous['authority']) == make_authority('cloud', binding, plans, inner, composition, cloud_origin)
            assert previous['cleanOwner'] and previous['finalInputsPreserved'] and previous['error'] is None
            assert type(previous['rawExitCode']) is int and previous['rawExitCode'] in (0, 1) and previous['secondaryErrors'] == []
            assert previous['constructorGuardBefore'] == previous['constructorGuardAfter'] == before
            assert previous['terminal']['path'] == str(Path(cloud_trial['ownerOutputRoot']) / 'terminal.json')
            cloud_terminal = prep.document(previous['terminal'])
            assert cloud_terminal['authority'] == cloud_trial['authority']
            assert cloud_terminal['pid'] == previous['originalOwner'] and cloud_terminal['rawExitCode'] == previous['rawExitCode']
            assert not cloud_terminal['timeout'] and not cloud_terminal['forcedCleanup']
            assert cloud_terminal['parentOwnedGroupGone'] and cloud_terminal['allObservedOwnedGroupsGone']
            assert all(not cloud_terminal[k] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
            cloud_output = Path(plans['cloud']['outputPrefix'] + '-' + plans['cloud']['runId'])
            observed = prep.document(prep.row(cloud_output / 'result.json'))
            assert observed['rootAuthority'] == cloud_trial['authority'] and observed['sourceIndex'] == binding['actorIndex']
            assert observed['servedEnvelope'] == composition['envelope']
            assert observed['originalInputsPreserved'] and observed['readonlyAppPreserved']
            assert observed['server']['stdoutCapture']['complete'] is True and observed['server']['shutdownRequested'] is True and observed['server']['sigintSent'] is True
            assert not observed['server']['forcedCleanup'] and observed['server']['exit'] == dict(code=0, signal=None, error=None)
            assert type(observed['client']['exit']['code']) is int and observed['client']['exit']['code'] in (0, 1) and observed['client']['exit']['signal'] is None and observed['client']['exit']['error'] is None
            assert observed['configVerifiedBeforeDev'] is True
            assert observed['readiness']['workloadRegistered'] is True and observed['readiness']['tcpConnect'] is True
            assert observed['readiness']['extraHttpRequests'] == 0
            assert observed['portLease']['origin'] == cloud_origin and observed['portLease']['fallbackAllowed'] is False
            assert [r['label'] for r in observed['commands']] == ['config-show', 'wash-dev', 'full-contract-client']
            assert observed['commands'][1] == observed['server']
            for command in observed['commands'][:2]:
                assert command['exit'] == dict(code=0, signal=None, error=None)
                assert command['timeout'] is False and command['forcedCleanup'] is False
                cc = command['stdoutCapture']
                assert cc['limitBytes'] == 8388608 and cc['errors'] == []
                assert all(cc[k] is True for k in ('pipeEof', 'fileClosed', 'fileBoundVerified', 'finalized', 'complete'))
                assert all(cc[k] is False for k in ('overflow', 'partialWritePossible', 'unretainedBytesUnknown'))
                assert command['stdout']['path'] == cc['path'] == str(cloud_output / (command['label'] + '.stdout.log'))
                assert command['stdout']['bytes'] == cc['fileBytes'] == cc['completeWriteBytes'] == cc['lastReservedWriteCeiling']
                prep.checked(command['stdout'])
                assert command['stderrPath'] == str(cloud_output / (command['label'] + '.stderr.log'))
                assert command['stderrFinalDigestDeferredToOriginalOwnerTerminal'] is True
                # Original600 terminal above proves descendant quiescence before this read.
                prep.row(Path(command['stderrPath']))
            show = prep.document(observed['commands'][0]['stdout'])
            assert show['success'] is True and show['data'] == observed['effectiveConfiguration']
            wanted, effective = observed['configured'], observed['effectiveConfiguration']
            assert wanted['build'] == effective['build'] and wanted['version'] == effective['version'] == '2.11.0'
            for key in ('address', 'command', 'component_path', 'service', 'volumes'):
                assert wanted['dev'][key] == effective['dev'][key]
            assert wanted['dev']['component_path'] == composition['envelope']['path']
            assert wanted['dev']['volumes'] == [dict(host_path=str(cloud_output / 'app'), guest_path='/app'), dict(host_path=str(cloud_output / 'cache'), guest_path='/app/.next/cache')]
            assert effective['workload']['allowedHosts'] == wanted['workload']['allowedHosts'] == [cloud_origin + '/']
            assert effective['workload']['allowedIpNameLookups'] == effective['workload']['allowedHostLoopbackPorts'] == []
            assert effective['workload']['environment']['config'] == dict(STARLING_NEXT_ORIGIN=cloud_origin, NODE_ENV='production', NEXT_TELEMETRY_DISABLED='1')
            capture = observed['server']['stdoutCapture']
            stdout = observed['server']['stdout']
            assert stdout['path'] == capture['path'] == str(cloud_output / 'wash-dev.stdout.log')
            assert type(stdout['bytes']) is int and 0 <= stdout['bytes'] <= 8388608
            assert capture['limitBytes'] == 8388608 and capture['errors'] == []
            assert all(capture[k] for k in ('pipeEof', 'fileClosed', 'fileBoundVerified', 'finalized', 'complete'))
            assert all(not capture[k] for k in ('overflow', 'partialWritePossible', 'unretainedBytesUnknown'))
            assert stdout['bytes'] == capture['fileBytes'] == capture['completeWriteBytes'] == capture['lastReservedWriteCeiling']
            prep.checked(stdout)
            # Original semantics and added observation are independent. A collected strict failure remains failed.
            client_ref = observed['client']['result']
            assert client_ref['path'] == str(cloud_output / 'client/result.json')
            client = prep.document(client_ref)
            assert client['suite'] == 'NEXT_RSC_STREAM_OBSERVER_FULL_CONTRACT_CLIENT_V1'
            assert client['controlOnly'] is False and client['fullOriginalContractExecuted'] is True
            assert observed['fullOriginalContractExecuted'] is True and client['fullNextAccepted'] is False
            assert type(client['passed']) is bool and client['errors'] == [] and client['transportErrors'] == []
            assert type(client['browserExit']['code']) is int and client['browserExit']['code'] in (0, 1) and client['browserExit']['signal'] is None
            contract_ref = prep.document(prep.row(Path(binding['clientIndex']['path']).with_name('plan.json')))['sourceRequirements']['fixtureContract']
            contract = prep.document(contract_ref)
            assert [r['id'] for r in client['http']] == [r['id'] for r in contract['requests']] + ['server-action-submit']
            for row in client['http']:
                ref = prep.row(cloud_output / 'client/responses' / (row['id'] + '.txt'))
                assert ref['bytes'] == row['bodyBytes'] and ref['sha256'] == row['bodySha256']
            portable = client['portableCache']['records']
            assert len(portable) == 5
            for row in portable:
                assert row['complete'] and not row['overflow'] and row['transportError'] is None and row['cleanupErrors'] == []
                assert row['receivedBytes'] == row['retainedBytes'] == row['body']['bytes'] <= 65536
                prep.checked(row['body'])
            supplemental = client['supplemental']['observations']
            assert len(supplemental) == 6
            for row in supplemental:
                assert row['bodyEofObserved'] and not row['signalAborted']
                assert row['error'] is row['readerReleaseError'] is row['publicationError'] is None
                prep.checked(row['body'])
            chunks = prep.document(prep.row(cloud_output / 'client/stream-chunks.json'))
            assert type(chunks) is list and len(chunks) == client['streaming']['chunks'] and len(chunks) >= 1
            browser_ref = prep.row(cloud_output / 'client/browser/result.json')
            browser = prep.document(browser_ref)
            assert client['browser'] == browser and browser['browserClosed'] is True and type(browser['passed']) is bool
            assert [r['id'] for r in browser['tests']] == ['client-counter', 'server-action']
            assert all(r['timedOut'] is False and r['cdpObserver']['stopped'] is False for r in browser['tests'])
            netlog = browser['netlog']
            assert netlog['completeJson'] is True and netlog['fsynced'] is True and netlog['errors'] == []
            netlog_ref = netlog['file']
            assert netlog_ref['path'] == str(cloud_output / 'client/browser/netlog.json')
            assert type(netlog_ref['bytes']) is int and 0 < netlog_ref['bytes'] <= 20 * 1024 * 1024
            prep.checked(netlog_ref)
            netlog_data = json.loads(Path(netlog_ref['path']).read_bytes())
            prep.checked(netlog_ref)
            assert type(netlog_data) is dict and type(netlog_data['constants']) is dict and type(netlog_data['events']) is list
            assert netlog['eventCount'] == len(netlog_data['events'])
            stream = browser['resourceStreamObservation']
            assert stream['finalized'] is True and stream['collectionComplete'] is True and stream['errors'] == []
            assert len(stream['observations']) == 1
            record = stream['observations'][0]
            assert record['collectionComplete'] is True and record['admission']['passed'] is True
            assert record['admission']['errors'] == []
            assert record['admission']['currentActionId'] == binding['requiredActionId']
            assert record['admission']['CDPBodyMatchedPlaywright'] is True and record['admission']['publicContextVerified'] is True
            request_body = record['admission']['actualRequestBody']
            request_publication = record['admission']['actualRequestBodyPublication']
            assert request_body['path'] == str(cloud_output / 'client/browser/resource-stream-request.bin')
            assert type(request_body['bytes']) is int and 0 < request_body['bytes'] <= 65536
            assert all(request_publication[k] is True for k in ('complete', 'fsynced', 'closed'))
            assert request_publication['fileBytes'] == request_body['bytes'] and request_publication['sha256'] == request_body['sha256']
            assert request_publication['errors'] == []
            prep.checked(request_body)
            assert record['admission']['multipart']['valid'] is True
            assert record['admission']['multipart']['bytes'] == request_body['bytes'] and record['admission']['multipart']['sha256'] == request_body['sha256']
            assert len(record['candidates']) == len(record['terminals']) == 1
            request_id = record['candidates'][0]['requestId']
            assert record['admission']['cdpRequestId'] == request_id
            assert record['command']['method'] == 'Network.streamResourceContent' and record['command']['params'] == dict(requestId=request_id)
            assert record['command']['trigger'] == 'first-qualified-requestWillBeSent'
            assert record['reply']['outcome'] in ('fulfilled', 'rejected')
            assert record['terminals'][0]['event'] in ('Network.loadingFinished', 'Network.loadingFailed')
            assert record['terminals'][0]['payload']['requestId'] == request_id
            assert all(not row['collectionUncertain'] for row in record['errors'])
            assert type(stream['commandSuccess']) is bool and stream['commandSuccess'] is record['commandSuccess']
            assert type(stream['completeResourceBody']) is bool and stream['completeResourceBody'] is record['completeResourceBody']
            assert stream['accepted'] is (stream['collectionComplete'] and stream['completeResourceBody'])
            artifact, publication = record['artifact'], record['publication']
            assert artifact['path'] == str(cloud_output / 'client/browser/resource-stream-observed.bin')
            assert type(artifact['bytes']) is int and 0 <= artifact['bytes'] <= 4194304
            assert record['body']['bytes'] == artifact['bytes'] and record['body']['sha256'] == artifact['sha256']
            assert all(publication[k] is True for k in ('complete', 'fsynced', 'closed')) and publication['errors'] == []
            assert publication['fileBytes'] == artifact['bytes'] and publication['sha256'] == artifact['sha256']
            prep.checked(artifact)
            if stream['completeResourceBody']:
                assert stream['commandSuccess'] and record['payloadsComplete'] and record['handoffSuccessful']
                assert record['prefixCountConsistency'] is True and record['terminals'][0]['event'] == 'Network.loadingFinished'
            # No original strict/browser/network error is waived by resource bytes or a new positive flag.



        except BaseException as error:
            try:
                prep.save(HERE / 'stock-unattempted.json', dict(schemaVersion=1,
                    state='RSC_STREAM_OBSERVER_V4_STOCK_SLOT_UNATTEMPTED_CLOUD_COLLECTION_UNCERTAIN_V1',
                    error=dict(name=type(error).__name__, message=str(error)[:2048]), bindings=BINDINGS,
                    automaticRetry=False, replacementTrials=False, fullNextAccepted=False))
            except BaseException:
                raise error
            raise
    logs = Path(trial['ownerOutputRoot'])
    receipt = HERE / (arm + '-owner-result.json')
    assert all(not x.exists() and not x.is_symlink() for x in (Path(trial['outputRoot']), logs, receipt))
    plan = plans[arm]
    node = plan['node']
    actor = Path(binding['actorIndex']['path']).parent
    argv = ([node['path'], str(actor / 'deploy.mjs'), ar['path']] if arm == 'cloud' else
        [node['path'], str(actor / 'run-stock.mjs'), trial['outputRoot'], plan['standaloneSource'], plan['browserTools'], plan['runId'], ar['path']])
    monitor = prep.original(plan['monitor'], 'genuine_stream_observer_original_owner')
    env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
    env.update(PATH=str(Path(node['path']).parent) + ':/usr/bin:/bin', NODE_ENV='production', NEXT_TELEMETRY_DISABLED='1', CI='1')
    logs.mkdir(mode=0o700)
    terminal, primary, after, preserved = None, None, None, False
    secondary = []
    try:
        terminal = monitor.monitor(argv, plan['cwd'], env, logs, trial['ownerSeconds'], ar)
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
            row = dict(schemaVersion=1, state='ROOT_RSC_STREAM_OBSERVER_V4_FULL_ORIGINAL_OWNER_COMPLETED_UNREVIEWED_V1', arm=arm,
                rawExitCode=None if terminal is None else terminal['rawExitCode'], originalOwner=None if terminal is None else terminal['pid'],
                cleanOwner=clean, finalInputsPreserved=preserved, error=None if primary is None else dict(name=type(primary).__name__, message=str(primary)[:2048]),
                secondaryErrors=secondary, authority=ar, controller=self_ref, bindings=BINDINGS,
                terminal=prep.row(logs / 'terminal.json') if (logs / 'terminal.json').is_file() else None,
                constructorGuardBefore=before, constructorGuardAfter=after, observerExecutionClaimedByOwnerReceipt=False, fullOriginalContractExecutionClaimedByOwnerReceipt=False, fullNextAccepted=False)
            rr = prep.save(receipt, row)
            print(json.dumps(dict(receipt=rr, rawExitCode=row['rawExitCode'], cleanOwner=clean)))
        except BaseException:
            if primary is not None:
                raise primary
            raise
    if primary is not None:
        raise primary
    return 0 if clean and preserved and terminal['rawExitCode'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
