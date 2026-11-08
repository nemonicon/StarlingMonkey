"""Prepare the fixed cloud then bridged-Node Chrome-body-RSC prework response probes; run one original owner at a time."""
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
BINDINGS = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-rsc-browser-body-prework-root-results-v1/runtime-bindings.json', 'sha256': '9e3df491e3c124d6b7ed9e06c85c0bceba37cb162d3084737b49b20e84d5b25c', 'bytes': 583175}
PREPARER = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'),
    sha256='4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', bytes=19784)
INNER_AUTHORITY = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/diagnostic-next-construction-authority.json'),
    sha256='23313b9b1858e22df729b379c10750cd92ba00ce4aa9bee179fc21142fdfea66', bytes=5597386)
INNER_REVIEW = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
    sha256='5c284564e0ddefba507c5429acd98c42393d5c0f2764105a4046f0665f51e16a', bytes=22550)
COMPOSITION_REVIEW = dict(path=str(BASE / 'next-standard-handler-observer-root-results-v1/actual-next-v3-composition-review.json'),
    sha256='b333fbc736e653f0a56bbe7ee031b3b943faf3e4d2ea687112659465171e2387', bytes=33472)
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


def context():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and type(BINDINGS) is dict, 'Unbound Source refuses helper import/action'
    path = Path(PREPARER['path'])
    raw = path.read_bytes()
    assert path.resolve() == path and not path.is_symlink() and path.stat().st_nlink == 1
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (PREPARER['sha256'], PREPARER['bytes'])
    spec = importlib.util.spec_from_file_location('genuine_rsc_response_control_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    binding = prep.document(BINDINGS)
    assert binding['state'] == 'ROOT_RSC_BROWSER_BODY_PREWORK_ACTUAL_BINDINGS_V1'
    assert binding['compositionReview'] == COMPOSITION_REVIEW and binding['innerConstructionReview'] == INNER_REVIEW
    assert binding['applicationBuildReview'] == REQUIRED_APP_REVIEW
    actor_index = prep.family(binding['actorIndex'])
    client_index = prep.family(binding['clientIndex'])
    client_root = Path(binding['clientIndex']['path']).parent
    assert client_root == BASE / 'next-rsc-browser-body-prework-client-v1'
    client_plan_ref = next(dict(r, path=str(client_root / r['path'])) for r in client_index['files'] if r['path'] == 'plan.json')
    client_plan = prep.document(client_plan_ref)
    assert client_plan['suite'] == 'NEXT_RSC_BROWSER_BODY_PREWORK_CLIENT_V1'
    assert client_plan['nodeArgc'] == 6 and client_plan['controlOnly'] is True
    assert client_plan['fullOriginalContractExecuted'] is False
    assert client_plan['requiredApplicationReview'] == REQUIRED_APP_REVIEW
    assert client_plan['bodyLimitBytes'] == 4 * 1024 * 1024
    assert client_plan['resultLimitBytes'] == 16 * 1024 * 1024
    assert client_plan['browserTools'] == '/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools'
    assert len(client_plan['hostRequirements']) == 6
    for ref in client_plan['hostRequirements']:
        prep.checked(ref)
    assert client_plan['httpTimeoutMs'] == 20000 and client_plan['cleanupTimeoutMs'] == 2000
    prework_requirements = client_plan['preworkSourceRequirements']
    assert set(prework_requirements) == {'donorFullClient', 'portableCacheCollector', 'supplemental', 'fixtureContract'}
    prework_module = client_plan['preworkModule']
    assert prework_module['path'] == str(client_root / 'prework.mjs')
    assert any(dict(r, path=str(client_root / r['path'])) == prework_module for r in client_index['files'])
    requirements = client_plan['sourceRequirements']
    assert set(requirements) == {'requestCapture', 'requestBody', 'headerEvidence'}
    assert client_plan['requestCapture'] == binding['requestCapture'] == requirements['requestCapture']
    protected = {ref['path']: ref for ref in binding['protectedInputs']}
    assert len(protected) == len(binding['protectedInputs'])
    for ref in [*requirements.values(), *prework_requirements.values()]:
        prep.checked(ref)
        assert protected[ref['path']] == ref, 'Every external client consumer is protected before/final'
    actor_root = Path(binding['actorIndex']['path']).parent
    assert actor_root == BASE / 'next-rsc-browser-body-prework-runtime-v1'
    for role, name in [('cloudPlan', 'plan.json'), ('stockPlan', 'stock-plan.json')]:
        assert binding[role]['path'] == str(actor_root / name)
        assert any(dict(r, path=str(actor_root / r['path'])) == binding[role] for r in actor_index['files'])
    app = prep.document(binding['applicationBuildReview'])
    assert app['state'] == 'COORDINATED_FS_CALLBACK_NO_COMPRESS_APP_BUILD_DATA_REVIEW_PASSED_V1' and app['verifiedPassed'] is True
    assert app['verifiedDataReviewPassed'] is True and app['buildVersion'] == 1
    for key in ('sourceCacheAbsent', 'runtimeCacheMountPolicyCompatible', 'configuredCompressFalseVerified', 'effectiveStandaloneConfigCompressFalseVerified'):
        assert app[key] is True
    inner = prep.document(INNER_REVIEW)
    assert inner['verifiedPassed'] is True and inner['rootAuthority'] == INNER_AUTHORITY
    composition = prep.document(COMPOSITION_REVIEW)
    assert composition['verifiedPassed'] is True and composition['verifiedDataReviewPassed'] is True
    assert composition['innerComponent'] == inner['component'] and composition['innerConstructionAuthority'] == INNER_AUTHORITY
    assert len(composition['selectedImports']) == 13 and all(x.endswith('@0.2.10') for x in composition['selectedImports'])
    assert composition['selectedExports'] == ['wasi:http/incoming-handler@0.2.10']
    plans = {arm: prep.document(binding[arm + 'Plan']) for arm in ('cloud', 'stock')}
    for arm, plan in plans.items():
        assert plan['controlOnly'] is True and plan['prospectiveRscResponseBindingsPending'] is False
        assert plan['rscResponseControl']['clientSourcePending'] is False
        assert plan['rscResponseControl']['requiredClientIndex'] == binding['clientIndex']
        assert plan['rscResponseControl']['requiredClient'] == plan['clientSource']
        assert plan['applicationBuildReview'] == binding['applicationBuildReview']
        assert plan['applicationBuildResult'] == app['actualResult'] and plan['applicationInputs'] == app['applicationInputs']
        assert plan['applicationRootIdentityEvidence'] == app['applicationRootIdentityEvidence']
        assert plan['clientSourceIndex'] == binding['clientIndex']
        assert plan['clientSource']['path'] == str(client_root / 'run-client.mjs')
        assert any(dict(r, path=str(client_root / r['path'])) == plan['clientSource'] for r in client_index['files'])
        assert plan['node'] == plans['cloud']['node'] and plan['monitor'] == plans['cloud']['monitor']
        prefix = Path(plan['outputPrefix'])
        assert prefix.parent == Path('/private/tmp/starling-node-compat') and prefix.resolve() == prefix
        assert plan['runId'] == ('rsc-browser-body-cloud-first' if arm == 'cloud' else 'rsc-browser-body-stock-first')
        assert str(prefix) == '/private/tmp/starling-node-compat/next-rsc-browser-body-prework-' + arm + '-v1'
        assert plan['runId'] == plan['namespacePolicy']['plannedRunId']
        assert str(prefix) == plan['namespacePolicy']['plannedOutputPrefix']
        assert plan['browserTools'] == client_plan['browserTools']
    assert plans['cloud']['applicationSchema']['additionalDirectories'] == []
    assert plans['cloud']['applicationSchema']['ownedDirectoriesIncludingRoot'] == plans['cloud']['applicationSchema']['directoriesExcludingRoot'] + 1
    assert plans['cloud']['selfOrigin'] is None and plans['cloud']['outerSeconds'] == 600
    assert plans['stock']['outerSeconds'] == 300
    assert client_plan['allowedOutputPolicies'] == [dict(runId=plans[arm]['runId'], output=plans[arm]['outputPrefix'] + '-' + plans[arm]['runId'] + '/client') for arm in ('cloud', 'stock')]
    assert plans['cloud']['applicationSource'] == app['applicationRoot']
    assert plans['stock']['standaloneSource'] == app['applicationRoot']
    self_ref = prep.row(Path(__file__).resolve())

    def protect():
        for ref in [PREPARER, INNER_AUTHORITY, INNER_REVIEW, COMPOSITION_REVIEW, BINDINGS, self_ref]:
            prep.checked(ref)
        prep.family(binding['actorIndex'])
        prep.family(binding['clientIndex'])
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
        controlOnly=True, rscResponseControlAllowed=True, publicRequestCorrelationAllowed=True,
        publicRequestCorrelation=PUBLIC, compilerAllowed=False, nativeBuildAllowed=False,
        automaticRetry=False, replacementTrials=False, fullNextAccepted=False)
    if arm == 'cloud':
        return dict(common, state='ROOT_NEXT_RSC_BROWSER_BODY_CLOUD_AUTHORIZED_V1',
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
    return dict(common, state='ROOT_NEXT_RSC_BROWSER_BODY_HOST_AUTHORIZED_V1',
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
        prep.save(prepared_path, dict(schemaVersion=1, state='ROOT_FIXED_RSC_BROWSER_BODY_PREWORK_PAIR_PREPARED_NOT_RUN_V1',
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
    assert prepared['state'] == 'ROOT_FIXED_RSC_BROWSER_BODY_PREWORK_PAIR_PREPARED_NOT_RUN_V1'
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
            assert [r['label'] for r in observed['commands']] == ['config-show', 'wash-dev', 'response-client']
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
            # Publication/collection gates only: strict semantic false remains a valid collected slot.
            client_ref = observed['client']['result']
            assert client_ref['path'] == str(cloud_output / 'client/result.json')
            assert type(client_ref['bytes']) is int and 0 < client_ref['bytes'] <= 16 * 1024 * 1024
            client = prep.document(client_ref)
            assert client['suite'] == 'NEXT_RSC_BROWSER_BODY_PREWORK_CLIENT_V1'
            assert client['controlOnly'] is True and client['fullOriginalContractExecuted'] is False
            assert observed['fullOriginalContractExecuted'] is False and client['fullNextAccepted'] is False
            assert client['responseProbeExecuted'] is True and observed['responseProbeExecuted'] is True
            assert type(client['passed']) is bool
            # Non-browser prework is a collected prerequisite, never an original full/browser acceptance claim.
            preceding = client['precedingWorkload']
            assert preceding['executed'] is True and preceding['collectionComplete'] is True
            assert type(preceding['passed']) is bool
            prework_ref = preceding['result']
            assert prework_ref['path'] == str(cloud_output / 'client/prework-result.json')
            assert type(prework_ref['bytes']) is int and 0 < prework_ref['bytes'] <= 16 * 1024 * 1024
            prework_publication = preceding['publication']
            assert all(prework_publication[k] is True for k in ('complete', 'fsynced', 'closed'))
            assert prework_publication['fileBytes'] == prework_ref['bytes']
            assert prework_publication['sha256'] == prework_ref['sha256'] and prework_publication['errors'] == []
            prework = prep.document(prework_ref)
            assert prework['suite'] == 'NEXT_RSC_PREBROWSER_WORKLOAD_V1'
            assert prework['executed'] is True and prework['collectionComplete'] is True
            assert prework['passed'] is preceding['passed']
            assert prework['fullOriginalContractExecuted'] is False and prework['browserExecuted'] is False
            assert prework['errors'] == []
            assert prework['transportErrors'] == []
            assert prework['publicManifestUsed'] is False and prework['fullNextAccepted'] is False
            frame = prework['collectionFrame']
            assert [frame[k] for k in ('httpRecords', 'portableRecords', 'supplementalRecords')] == [24, 5, 6]
            assert all(frame[k] is True for k in ('allHttpBodiesPublished', 'allPortableCollected', 'allSupplementalCollected', 'streamCapturePublished'))
            raw_files = prework['rawFiles']
            assert type(raw_files) is list and 0 < len(raw_files) <= 128
            assert all(type(r['bytes']) is int and 0 <= r['bytes'] <= 8 * 1024 * 1024 for r in raw_files)
            assert sum(r['bytes'] for r in raw_files) <= 32 * 1024 * 1024
            raw_by_path = {r['path']: r for r in raw_files}
            assert len(raw_by_path) == len(raw_files)
            client_output = cloud_output / 'client'
            for r in raw_files:
                rel = Path(r['path']).relative_to(client_output)
                assert rel.as_posix() in ('stream-chunks.json', 'prework-progress.json') or rel.parts[0] in ('responses', 'portable-cache', 'supplemental')
                prep.checked(r)
            http = prework['http']
            prework_client_plan = prep.document(prep.row(Path(binding['clientIndex']['path']).with_name('plan.json')))
            contract = prep.document(prework_client_plan['preworkSourceRequirements']['fixtureContract'])
            assert [r['id'] for r in http] == [r['id'] for r in contract['requests']] + ['server-action-submit']
            for r in http:
                body = raw_by_path[str(client_output / 'responses' / (r['id'] + '.txt'))]
                assert body['bytes'] == r['bodyBytes'] and body['sha256'] == r['bodySha256']
            portable = prework['portableCache']['records']
            assert len(portable) == 5
            portable_validation = prework['portableCacheValidation']
            assert type(portable_validation['checks']) is int and portable_validation['checks'] >= 0
            assert frame['portableChecks'] == portable_validation['checks']
            for r in portable:
                assert r['complete'] is True and r['overflow'] is False
                assert r['transportError'] is None and r['cleanupErrors'] == []
                assert r['receivedBytes'] == r['retainedBytes'] == r['body']['bytes'] <= 65536
                assert raw_by_path[r['body']['path']] == r['body']
            supplemental = prework['supplemental']['observations']
            assert len(supplemental) == 6
            supplemental_validation = prework['supplementalValidation']
            assert type(supplemental_validation['checks']) is int and supplemental_validation['checks'] >= 0
            assert frame['supplementalChecks'] == supplemental_validation['checks']
            for r in supplemental:
                assert r['bodyEofObserved'] is True and r['signalAborted'] is False
                assert r['error'] is r['readerReleaseError'] is r['publicationError'] is None
                assert r['body']['bytes'] <= 1024 * 1024
                assert raw_by_path[r['body']['path']] == r['body']
            chunks = prep.document(raw_by_path[str(client_output / 'stream-chunks.json')])
            assert type(chunks) is list and len(chunks) >= 1
            assert type(frame['streamChunks']) is int and type(prework['streaming']['chunks']) is int
            assert len(chunks) == frame['streamChunks'] == prework['streaming']['chunks']
            if prework['passed']:
                assert portable_validation['checks'] == 52 and supplemental_validation['checks'] == 80
                assert portable_validation['passed'] is True and supplemental_validation['passed'] is True
                assert all(r['passed'] is True for r in http)
                assert prework['cacheInvalidation']['passed'] is True
                assert prework['streaming']['complete'] is True and prework['streaming']['incrementalDeliveryObserved'] is True
            # A known failed browser read remains failed; collection is a separate gate.
            assert client['collectionComplete'] is True and client['browserClosed'] is True
            assert client['collectionErrors'] == [] and client['requestFidelityVerified'] is True
            fetch, body, network = client['browserFetch'], client['bodyRead'], client['networkTerminal']
            assert fetch['attempted'] is True and fetch['settled'] is True
            assert fetch['outcome'] in ('fulfilled', 'rejected')
            assert body['outcome'] in ('fulfilled', 'rejected', 'unattempted')
            assert body['postReadLimitBytes'] == 4 * 1024 * 1024 and body['allocationPrebounded'] is False
            assert network['kind'] in ('loadingFinished', 'loadingFailed')
            assert type(network['requestId']) is str and network['requestId']
            assert type(network['payload']) is dict and network['payload']['requestId'] == network['requestId']
            body_ref, body_publication = client['browserBody'], client['browserBodyPublication']
            if body['outcome'] == 'fulfilled':
                assert body['attempted'] is True and fetch['outcome'] == 'fulfilled'
                assert body_ref['path'] == str(cloud_output / 'client/browser-body.bin')
                assert type(body_ref['bytes']) is int and 0 <= body_ref['bytes'] <= 4 * 1024 * 1024
                assert body['bytes'] == body_ref['bytes']
                assert all(body_publication[k] is True for k in ('complete', 'fsynced', 'closed'))
                assert body_publication['fileBytes'] == body_ref['bytes'] and body_publication['sha256'] == body_ref['sha256']
                assert body_publication['errors'] == []
                prep.checked(body_ref)
            else:
                assert body_ref is None and body_publication is None and body['bytes'] is None
            if client['passed']:
                assert preceding['passed'] is True and client['requestFidelityVerified'] is True
                assert fetch['outcome'] == body['outcome'] == 'fulfilled' and network['kind'] == 'loadingFinished'
                assert fetch['response']['status'] == 200 and fetch['response']['redirected'] is False
                assert all(h['name'].lower() != 'content-encoding' for h in fetch['response']['headers'])
            assert client['publicationFile'] == str(cloud_output / 'client/publication.json')
            publication_ref = prep.row(Path(client['publicationFile']))
            assert 0 < publication_ref['bytes'] <= 65536
            publication = prep.document(publication_ref)
            assert publication['schemaVersion'] == 1 and publication['state'] == 'RSC_HTTP_RESPONSE_CLIENT_PUBLICATION_COMPLETE_V1'
            assert publication['complete'] is True and publication['errors'] == []
            result_publication = publication['resultPublication']
            assert all(result_publication[key] is True for key in ('complete', 'fsynced', 'closed'))
            assert type(result_publication['fileBytes']) is int and result_publication['fileBytes'] == client_ref['bytes']
            assert result_publication['sha256'] == client_ref['sha256'] and result_publication['errors'] == []
            assert publication['result'] == client_ref and publication['browserBody'] == body_ref
            assert publication['browserBodyPublication'] == body_publication
            assert publication['responseProbeExecuted'] is True and publication['collectionComplete'] is True
            assert publication['browserClosed'] is True
            # The summary is emitted only after the receipt fsync/close; it is an external ordered publication witness.
            summary_ref = observed['client']['stdout']
            assert summary_ref['path'] == str(cloud_output / 'response-client.stdout.log')
            assert 0 < summary_ref['bytes'] <= 65536
            summary_bytes = prep.checked(summary_ref).read_bytes()
            prep.checked(summary_ref)
            lines = summary_bytes.decode('utf8').splitlines()
            assert len(lines) == 1
            summary = json.loads(lines[0])
            assert summary['state'] == 'RSC_HTTP_RESPONSE_CLIENT_TERMINAL_PUBLISHED_V1'
            assert summary['suite'] == client['suite'] and summary['result'] == client_ref and summary['publication'] == publication_ref
            assert summary['passed'] is client['passed'] and summary['responseProbeExecuted'] is True
            assert summary['collectionComplete'] is True and summary['browserClosed'] is True
            assert type(summary['collectionErrors']) is int and summary['collectionErrors'] == 0


        except BaseException as error:
            try:
                prep.save(HERE / 'stock-unattempted.json', dict(schemaVersion=1,
                    state='RSC_BROWSER_BODY_STOCK_SLOT_UNATTEMPTED_CLOUD_COLLECTION_UNCERTAIN_V1',
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
    monitor = prep.original(plan['monitor'], 'genuine_rsc_response_original_owner')
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
            row = dict(schemaVersion=1, state='ROOT_RSC_BROWSER_BODY_PREWORK_ORIGINAL_OWNER_COMPLETED_UNREVIEWED_V1', arm=arm,
                rawExitCode=None if terminal is None else terminal['rawExitCode'], originalOwner=None if terminal is None else terminal['pid'],
                cleanOwner=clean, finalInputsPreserved=preserved, error=None if primary is None else dict(name=type(primary).__name__, message=str(primary)[:2048]),
                secondaryErrors=secondary, authority=ar, controller=self_ref, bindings=BINDINGS,
                terminal=prep.row(logs / 'terminal.json') if (logs / 'terminal.json').is_file() else None,
                constructorGuardBefore=before, constructorGuardAfter=after, responseProbeExecutionClaimedByOwnerReceipt=False, fullOriginalContractExecutionClaimedByOwnerReceipt=False, fullNextAccepted=False)
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
