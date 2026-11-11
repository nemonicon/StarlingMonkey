"""Bind fresh full-workload/CDP-observer inputs; never launch a host or browser."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ACTOR = BASE / 'next-rsc-stream-observer-v4-runtime-v2'
CLIENT = BASE / 'next-rsc-stream-observer-v4-full-client-v2'
BROWSER = BASE / 'next-rsc-stream-observer-v4-browser-v1'
ACTOR_INDEX = None
CLIENT_INDEX = None
BROWSER_INDEX = None
CONTROLLER_UNBOUND = None
APP_REVIEW = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/actual-build-review.json'),
    sha256='9106545f606ee30b2a3a05940d97233ce3b2e867e6abcdc5c5ec84efa09ad679', bytes=22847)
ASSET_SELECTION = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/asset-selection.json'),
    sha256='05c965a6b536af21c5947ccace5d9c1cc12b129c86a5b2df42e1bb95dd2c5b4c', bytes=7350)
FAILED_FULL = dict(path=str(BASE / 'next-fs-callback-no-compress-wasmcloud-root-results-v1/actual-runtime-review.json'),
    sha256='81a9c56b5c22c284149f971ae1e6ca9cdd4d8b72d8f22e4a5b107f4aa9d3041a', bytes=81083)
BODY_CONTROL = dict(path=str(BASE / 'next-rsc-browser-body-prework-root-results-v1/actualreview.json'),
    sha256='bc79b8111d58127d501a9aa6e592e81f71742f632cba5b8f2aeacbf7459b1e49', bytes=154007)
SELECTED_HOST_TOOLS = None
CONSTRUCTION_ARTIFACT_PREFLIGHT = None
COMPOSITION_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/actual-next-v4-composition-review.json', 'sha256': '730c2698578692e35789918930d6be1cf8fb837a4e5362bcef5b802919795c2f', 'bytes': 9900}
OBSERVER_COMPOSITION_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/actual-v4-composition-review.json', 'sha256': '214c1d9bcfd1858666d460afe72811b858fc8018e9f5e4bfb9519d8ddbe04224', 'bytes': 11140}
METADATA_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/actual-metadata-runtime-review.json', 'sha256': '61bb6690df9cf8fef3c455314352a95816a20bc01920909b75632bf5333c47c8', 'bytes': 7272}


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




def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Requires nonoptimized isolated Python with bytecode disabled')
    assert all(type(r) is dict for r in (ACTOR_INDEX, CLIENT_INDEX, BROWSER_INDEX, CONTROLLER_UNBOUND, SELECTED_HOST_TOOLS, CONSTRUCTION_ARTIFACT_PREFLIGHT)), 'Source review/seals pending; no helper read or mutation'
    helper = BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'
    raw = helper.read_bytes()
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == ('4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', 19784)
    spec = importlib.util.spec_from_file_location('genuine_stream_observer_binding_admission', helper)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    state = prep.context()
    original = prep.document(prep.row(helper.parent / 'diagnostic-next-construction-authority.json'))
    assert prep.authority(state) == original
    before = prep.admit(original)
    for folder, index in ((ACTOR, ACTOR_INDEX), (CLIENT, CLIENT_INDEX), (BROWSER, BROWSER_INDEX)):
        assert index['path'] == str(folder / 'index.json')
        prep.family(index)
    assert CONTROLLER_UNBOUND['path'] == str(HERE / 'run-controls.py')
    prep.checked(CONTROLLER_UNBOUND)
    composition, observer_composition, metadata_review = composition_evidence(prep)
    # Close the actor's actual historical constructor artifactBookend inputs before any owner can be issued.
    # The Root preflight receipt is authenticated provenance; fresh checked(ref) below is the admission.
    prep.checked(CONSTRUCTION_ARTIFACT_PREFLIGHT)
    inner_review_ref = prep.row(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json')
    assert (inner_review_ref['sha256'], inner_review_ref['bytes']) == ('5c284564e0ddefba507c5429acd98c42393d5c0f2764105a4046f0665f51e16a', 22550)
    inner_review = prep.document(inner_review_ref)
    construction = prep.document(inner_review['actualResult'])
    audit = prep.document(inner_review['componentAudit'])
    assert construction['state'] == 'NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2' and construction['passed'] is True
    assert construction['artifacts']['component'] == inner_review['component'] and construction['artifacts']['componentAudit'] == inner_review['componentAudit']
    assert audit['component'] == inner_review['component'] and audit['passed'] is True
    constructor_bookend_refs = [inner_review['actualResult'], inner_review['component'], inner_review['componentAudit'],
        construction['rootAuthority'], construction['callerIndex'], construction['plan'], *construction['artifacts']['engineBuildEvidence']]
    for key in ('engine', 'nativeMetadata', 'inputSourceIndex', 'inputEntry', 'adapter', 'returnedImports', 'returnedOwnShape'):
        constructor_bookend_refs.append(construction['artifacts'][key])
    for key in ('validateTerminal', 'witTerminal'):
        terminal_ref = audit[key]
        terminal = prep.document(terminal_ref)
        assert terminal['rawExitCode'] == 0 and not terminal['timeout'] and not terminal['forcedCleanup']
        assert terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone']
        assert all(not terminal[key] for key in ('signals', 'errors', 'interruptedSignals', 'remainingObservedPids'))
        constructor_bookend_refs.extend((terminal_ref, terminal['stdout'], terminal['stderr']))
    for ref in constructor_bookend_refs:
        prep.checked(ref)
    selected_host = prep.document(SELECTED_HOST_TOOLS)
    assert selected_host['state'] == 'ROOT_V4_BROWSER_TOOL_SELECTION_PASSED_NOT_BROWSER_EXECUTED_V1' and selected_host['passed'] is True
    assert selected_host['chromeVersion'] == '157.0.8103.39' and selected_host['playwrightVersion'] == '1.64.1'
    assert selected_host['fullWorkloadInvoked'] is False and len(selected_host['hostRequirements']) == 6 and len(selected_host['playwrightPackageFiles']) == 115
    assert len({r['path'] for r in selected_host['playwrightPackageFiles']}) == 115
    failed, body = prep.document(FAILED_FULL), prep.document(BODY_CONTROL)
    assert failed['verifiedDataReviewPassed'] is True and failed['fullContractPassed'] is False and failed['fullNextAccepted'] is False
    assert body['verifiedDataReviewPassed'] is True and body['fullNextAccepted'] is False
    app, assets = prep.document(APP_REVIEW), prep.document(ASSET_SELECTION)
    assert app['state'] == 'COORDINATED_FS_CALLBACK_NO_COMPRESS_APP_BUILD_DATA_REVIEW_PASSED_V1' and app['buildVersion'] == 1
    for key in ('verifiedPassed', 'verifiedDataReviewPassed', 'sourceCacheAbsent', 'runtimeCacheMountPolicyCompatible', 'configuredCompressFalseVerified', 'effectiveStandaloneConfigCompressFalseVerified'):
        assert app[key] is True
    assert assets['verifiedPassed'] is True and assets['applicationBuildReview'] == APP_REVIEW
    assert assets['applicationInputs'] == app['applicationInputs'] and assets['applicationRoot'] == app['applicationRoot']
    inventory = prep.document(app['applicationInputs'])
    root = Path(app['applicationRoot'])
    assert inventory['root'] == str(root) and inventory['symlinks'] == []
    files, directories = inventory['files'], inventory['directories']
    assert all(r['path'] != '.next/cache' and not r['path'].startswith('.next/cache/') for r in files + directories)
    assert not (root / '.next/cache').exists() and not (root / '.next/cache').is_symlink()
    count, size, dirs = len(files), sum(r['bytes'] for r in files), len(directories)
    assert count == inventory['regularFiles'] and size == inventory['bytes']
    st = root.stat()
    identity = dict(dev=st.st_dev, ino=st.st_ino, mode=st.st_mode & 0o777, nlink=st.st_nlink)
    evidence = prep.document(app['applicationRootIdentityEvidence'])['rootIdentity']
    assert all(identity[k] == evidence[k] for k in identity)
    manifest_member = next(r for r in files if r['path'] == '.next/server/server-reference-manifest.json')
    manifest_ref = dict(path=str(root / manifest_member['path']), sha256=manifest_member['sha256'], bytes=manifest_member['bytes'])
    manifest = prep.document(manifest_ref)
    assert type(manifest['node']) is dict and manifest['edge'] == {}
    targets = [(key, value) for key, value in manifest['node'].items()
        if value['exportedName'] == 'submitFixture' and value['filename'] == 'app/actions/actions.js']
    assert len(targets) == 1
    action_id, action = targets[0]
    assert set(action['workers']) == {'app/actions/page'}
    history = HERE / 'source-history/binding-v1'
    history.mkdir(parents=True)
    changes = []

    def bind_plan(folder, filename, label, transform):
        raw = (folder / filename).read_bytes()
        old = json.loads(raw)
        with (history / (label + '-plan.unbound.json')).open('xb') as out:
            out.write(raw)
        new = copy.deepcopy(old)
        transform(new)
        keys = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
        inverse = copy.deepcopy(new)
        for key in keys:
            if key in old:
                inverse[key] = old[key]
            else:
                del inverse[key]
        assert inverse == old and (history / (label + '-plan.unbound.json')).read_bytes() == raw
        (folder / filename).write_text(json.dumps(new, indent=2) + '\n')
        changes.append(dict(role=label, changedKeys=keys, exactSemanticInverseVerified=True, originalBytesPreserved=True,
            before=prep.row(history / (label + '-plan.unbound.json')), after=prep.row(folder / filename)))
        return new

    def reseal(folder):
        index = json.loads((folder / 'index.json').read_bytes())
        for member in index['files']:
            actual = prep.row(folder / member['path'])
            member.update(sha256=actual['sha256'], bytes=actual['bytes'])
        index['payloadFiles'] = len(index['files'])
        index['payloadBytes'] = sum(member['bytes'] for member in index['files'])
        (folder / 'index.json').write_text(json.dumps(index, indent=2) + '\n')
        ref = prep.row(folder / 'index.json')
        prep.family(ref)
        return ref

    with (history / 'actor-index.unbound.json').open('xb') as out:
        out.write((ACTOR / 'index.json').read_bytes())
    browser_ref, client_ref = BROWSER_INDEX, CLIENT_INDEX
    browser_plan = prep.document(prep.row(BROWSER / 'plan.json'))
    worker = prep.row(BROWSER / 'browser-check.mjs')
    assert browser_plan['actualAssetBindingsPending'] is False
    for key, value in (('applicationInputs', app['applicationInputs']), ('actualApplicationBuildReview', APP_REVIEW),
            ('actualAssetSelectionReview', ASSET_SELECTION), ('assetSelectionHtml', assets['clientHtml']),
            ('actionsAssetSelectionHtml', assets['actionsHtml']), ('assetPins', assets['assetPins']),
            ('actionsAssetPins', assets['actionsAssetPins']), ('requiredActionId', action_id), ('actualActionManifest', manifest_ref)):
        assert browser_plan[key] == value
    client_plan = prep.document(prep.row(CLIENT / 'plan.json'))
    assert client_plan['suite'] == 'NEXT_RSC_STREAM_OBSERVER_FULL_CONTRACT_CLIENT_V1' and client_plan['actualBrowserSourceBindingPending'] is False
    assert set(client_plan['sourceRequirements']) == {'manifestReader', 'supplemental', 'portableCacheCollector', 'fixtureContract', 'browserSourceIndex', 'browserWorker'}
    assert client_plan['sourceRequirements']['browserWorker'] == worker and client_plan['sourceRequirements']['browserSourceIndex'] == browser_ref
    assert client_plan['allowedOutputPolicies'] == [dict(runId='rsc-stream-observer-v4-' + arm + '-second',
        output='/private/tmp/starling-node-compat/next-rsc-stream-observer-v4-' + arm + '-v2-rsc-stream-observer-v4-' + arm + '-second/client') for arm in ('cloud', 'stock')]
    plans, preimages = {}, {}
    for arm, name in (('cloud', 'plan.json'), ('stock', 'stock-plan.json')):
        p = json.loads((ACTOR / name).read_bytes())
        assert p['prospectiveFullClientBindingsPending'] is True and p['protectedInputs'] == [] and p['sourceFamilies'] == []
        preimages[arm] = copy.deepcopy(p)
        p.update(applicationInputs=app['applicationInputs'], applicationBuildResult=app['actualResult'], applicationBuildReview=APP_REVIEW,
            applicationRootIdentityEvidence=app['applicationRootIdentityEvidence'], applicationBuildSource=app['sourceIndex'],
            clientSource=prep.row(CLIENT / 'run-contracts.mjs'), clientSourceIndex=client_ref,
            browserSource=worker, browserSourceIndex=browser_ref, browserTools=selected_host['browserTools'], selectedHostTools=SELECTED_HOST_TOOLS, constructionArtifactBookendPreflight=CONSTRUCTION_ARTIFACT_PREFLIGHT, prospectiveFullClientBindingsPending=False,
            bindingState='READY_FULL_CLIENT_FULL_CONTRACT', outputPrefix='/private/tmp/starling-node-compat/next-rsc-stream-observer-v4-' + arm + '-v2',
            runId='rsc-stream-observer-v4-' + arm + '-second')
        p['fullClientFullContract'].update(clientSourcePending=False, requiredClientIndex=client_ref,
            requiredClient=prep.row(CLIENT / 'run-contracts.mjs'), assetSelection=ASSET_SELECTION,
            browserFamily=browser_ref, clientFamily=client_ref, requiredAssetSelection=ASSET_SELECTION,
            requiredBrowserFamily=browser_ref, requiredWorker=worker)
        p['namespacePolicy']['actualOutputPrefixAndRunIdPending'] = False
        p['requiredApplicationData'].update(applicationBuildReview=APP_REVIEW, applicationBuildResult=app['actualResult'],
            applicationInputs=app['applicationInputs'], applicationRootIdentityEvidence=app['applicationRootIdentityEvidence'], applicationRoot=str(root))
        if arm == 'cloud':
            assert p['prospectiveEnvelopeBindingsPending'] is True and p['compositionReviewFixedValues'] is None
            assert p['expectedEnvelopeBindings'] == dict(envelope=None, compositionReview=None)
            p.update(prospectiveEnvelopeBindingsPending=False,
                expectedEnvelopeBindings=dict(envelope=composition['envelope'], compositionReview=COMPOSITION_REVIEW),
                expectedCompositionReviewState=composition['state'], compositionReviewFixedValues={key: composition[key] for key in
                    ('state', 'verifiedPassed', 'verifiedDataReviewPassed', 'envelope', 'observerBinary', 'innerComponent',
                     'innerConstructionReview', 'innerConstructionAuthority', 'actualCompositionResult', 'observerCompositionReview',
                     'metadataRuntimeReview', 'rawChildBytesVerified', 'siblingDefiningInstancesVerified', 'sharedNominalResourceAliasesVerified',
                     'fieldsNominalResourceAliasesVerified', 'metadataGetterCanonicalOptionsVerified', 'synchronousLiftLowerWithInnerPostReturnVerified',
                     'innerExplicitPostReturnPreserved', 'observerManualPostReturnAbsent', 'internalIncomingHandlerImportComposedAway',
                     'allFourRequestedToolStepsRawZero', 'allFourToolStderrEmpty', 'finalInputsPreserved', 'selectedImports', 'selectedExports', 'selectedStandardVersion')})
            p['standardHandlerObserver'].update({key: composition[key] for key in ('observerSource', 'observerManifest', 'observerProtocol', 'observerCompositionReview', 'metadataRuntimeReview')})
            p['standardHandlerObserver'].update(observerCompositionReviewState=observer_composition['state'], metadataRuntimeReviewState=metadata_review['state'])
            p.update(applicationSource=str(root), applicationBuildOutputRoot=str(Path(app['actualResult']['path']).parent),
                applicationRootIdentity=identity, applicationSchema=dict(name='fresh-next-standalone-root-excluded-v1',
                    sourceDirectoriesExcludeRoot=True, files=count, bytes=size, directoriesExcludingRoot=dirs,
                    ownedDirectoriesIncludingRoot=dirs + 1, additionalDirectories=[]))
        else:
            p.update(standaloneSource=str(root), applicationRootIdentity=dict(path=str(root), **identity),
                expectedApplication=dict(files=count, bytes=size, directories=dirs, directoryInventoryExcludesRoot=True, symlinks=0))
        plans[arm] = p
    refs = {}

    def add(ref):
        prep.checked(ref)
        if ref['path'] in refs:
            assert refs[ref['path']] == ref
        refs[ref['path']] = ref

    def descriptors(value):
        if type(value) is dict:
            if set(value) == {'path', 'sha256', 'bytes'}:
                assert Path(value['path']).is_absolute(), 'URL/relative roles require explicit inventory selection'
                add(value)
            else:
                for key, member in value.items():
                    if key not in ('fixedWit', 'protectedInputs', 'sourceFamilies'):
                        descriptors(member)
        elif type(value) is list:
            for member in value:
                descriptors(member)

    for ref in constructor_bookend_refs + [CONSTRUCTION_ARTIFACT_PREFLIGHT]:
        add(ref)
    for ref in state['buildRefs'] + state['sourceRefs'] + [prep.ENGINE, prep.NATIVE_METADATA]:
        add(ref)
    donor = prep.document(prep.row(BASE / 'next-nonredirect-action-runtime-v2/plan.json'))
    assert donor['sourceFamilies'][-2:] == [prep.row(BASE / 'next-nonredirect-action-app-build-v2/index.json'), prep.row(BASE / 'next-nonredirect-action-browser-v2/index.json')]
    families = donor['sourceFamilies'][:-2] + [app['sourceIndex'], browser_ref, client_ref]
    for family in families:
        index = prep.family(family)
        add(family)
        for member in index['files']:
            add(dict(member, path=str(Path(family['path']).parent / member['path'])))
    descriptors(client_plan)
    for key in ('applicationInputs', 'actualApplicationBuildReview', 'actualAssetSelectionReview', 'assetSelectionHtml', 'actionsAssetSelectionHtml', 'actualActionManifest'):
        add(browser_plan[key])
    for pin in browser_plan['assetPins'] + browser_plan['actionsAssetPins']:
        rel = '.next/' + pin['path'].removeprefix('/_next/')
        member = next(r for r in files if r['path'] == rel)
        assert (member['sha256'], member['bytes']) == (pin['sha256'], pin['bytes'])
        add(dict(path=str(root / rel), sha256=pin['sha256'], bytes=pin['bytes']))
    for proof_document in (composition, observer_composition, metadata_review):
        # Only actual top-level artifact roles and WIT descriptors are runtime dependencies.
        for value in proof_document.values():
            if type(value) is dict and set(value) == {'path', 'sha256', 'bytes'}:
                add(value)
        for role in ('externalWorld', 'observerWorld'):
            if role in proof_document:
                add(proof_document[role]['wit'])
    for ref in selected_host['hostRequirements'] + selected_host['playwrightPackageFiles'] + [SELECTED_HOST_TOOLS, COMPOSITION_REVIEW, OBSERVER_COMPOSITION_REVIEW, METADATA_REVIEW, APP_REVIEW, ASSET_SELECTION, FAILED_FULL, BODY_CONTROL, manifest_ref,
            app['actualResult'], app['actualOwnerResult'], app['applicationInputs'], app['applicationRootIdentityEvidence']]:
        add(ref)
    for p in plans.values():
        descriptors(p)
        if 'fixedWit' in p:
            for member in p['fixedWit']['files']:
                add(dict(member, path=str(Path(p['fixedWit']['sourceDirectory']) / member['path'])))
    for member in prep.document(ACTOR_INDEX)['files']:
        if member['path'] not in ('plan.json', 'stock-plan.json'):
            add(dict(member, path=str(ACTOR / member['path'])))
    for rel in ('.next/required-server-files.json', 'server.js'):
        member = next(r for r in files if r['path'] == rel)
        add(dict(path=str(root / rel), sha256=member['sha256'], bytes=member['bytes']))
    assert prep.document(prep.row(root / '.next/required-server-files.json'))['config']['compress'] is False
    protected = sorted(refs.values(), key=lambda r: r['path'])
    for arm, name in (('cloud', 'plan.json'), ('stock', 'stock-plan.json')):
        def publish(p):
            assert p == preimages[arm]
            p.clear()
            p.update(plans[arm])
            p['sourceFamilies'], p['protectedInputs'] = families, protected
        bind_plan(ACTOR, name, arm, publish)
    actor_ref = reseal(ACTOR)
    binding = dict(schemaVersion=1, state='ROOT_RSC_STREAM_OBSERVER_V4_ACTUAL_BINDINGS_V2', actorIndex=actor_ref,
        clientIndex=client_ref, browserIndex=browser_ref, cloudPlan=prep.row(ACTOR / 'plan.json'), stockPlan=prep.row(ACTOR / 'stock-plan.json'),
        applicationBuildReview=APP_REVIEW, assetSelection=ASSET_SELECTION, actualActionManifest=manifest_ref, requiredActionId=action_id,
        originalFailedFullReview=FAILED_FULL, precedingBodyControlReview=BODY_CONTROL, protectedInputs=protected,
        innerConstructionReview=prep.row(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
        compositionReview=COMPOSITION_REVIEW, observerCompositionReview=OBSERVER_COMPOSITION_REVIEW, metadataRuntimeReview=METADATA_REVIEW, selectedHostTools=SELECTED_HOST_TOOLS, constructionArtifactBookendPreflight=CONSTRUCTION_ARTIFACT_PREFLIGHT)
    binding_ref = prep.save(HERE / 'runtime-bindings.json', binding)
    controller = HERE / 'run-controls.py'
    raw = prep.checked(CONTROLLER_UNBOUND).read_bytes()
    with (history / 'run-controls.unbound.py').open('xb') as out:
        out.write(raw)
    needle, replacement = b'BINDINGS = None', ('BINDINGS = ' + repr(binding_ref)).encode()
    assert raw.count(needle) == 1
    bound = raw.replace(needle, replacement)
    assert bound.replace(replacement, needle) == raw
    controller.write_bytes(bound)
    for ref in protected:
        prep.checked(ref)
    for ref in (actor_ref, client_ref, browser_ref):
        prep.family(ref)
    assert prep.admit(original) == before
    print(json.dumps(prep.save(HERE / 'source-bindings.json', dict(schemaVersion=1,
        state='ROOT_RSC_STREAM_OBSERVER_V4_METADATA_BOUND_NOT_RUN_V2', bindings=binding_ref, generator=prep.row(Path(__file__).resolve()),
        controller=prep.row(controller), planInverses=changes, controllerOneLiteralInverseVerified=True,
        constructorArtifactBookendReferenceCount=len({r['path'] for r in constructor_bookend_refs}), constructorArtifactBookendPreflight=CONSTRUCTION_ARTIFACT_PREFLIGHT,
        protectedInputCount=len(protected), genuineBuildReferences=len(state['buildRefs']), genuineSourceReferences=len(state['sourceRefs']),
        originalGuardBefore=before, oldProtectedArrayCopied=False, browserSelected=True, browserInvoked=False, immutableBrowserAndClientResealed=False, selectedHostPackageFiles=len(selected_host['playwrightPackageFiles']), actorsInvoked=False, fullNextAccepted=False))))


if __name__ == '__main__':
    main()
