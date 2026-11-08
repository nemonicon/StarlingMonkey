"""Root-only Next observer deployment controller; three NULL pins refuse all operational work."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent
ACTOR_INDEX = None
ACTOR_PLAN = None
COMPOSITION_REVIEW = None
INNER_ROOT = HERE.parent / 'next-native-export-diagnostic-next-root-results-v1'
PREPARER = dict(path=str(INNER_ROOT / 'prepare-construction.py'),
    sha256='4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', bytes=19784)
INNER_AUTHORITY = dict(path=str(INNER_ROOT / 'diagnostic-next-construction-authority.json'),
    sha256='23313b9b1858e22df729b379c10750cd92ba00ce4aa9bee179fc21142fdfea66', bytes=5597386)
INNER_REVIEW = dict(path=str(INNER_ROOT / 'actual-construction-review.json'),
    sha256='5c284564e0ddefba507c5429acd98c42393d5c0f2764105a4046f0665f51e16a', bytes=22550)
COMPOSITION_REVIEW_STATE = 'COORDINATED_NEXT_STANDARD_HANDLER_OBSERVER_V3_COMPOSITION_DATA_REVIEW_PASSED_V1'
RUN_ID = 'observer-next-v3-first'
FLAGS = dict(localhostServeAllowed=True, actualNextGuestAllowed=True, browserAllowed=True,
    publicRequestCorrelationAllowed=True, standardHandlerObserverAllowed=True,
    compilerAllowed=False, componentConstructionAllowed=False, externalDeploymentAllowed=False,
    adoptionAllowed=False)
PUBLIC_CORRELATION = dict(headerName='x-next-public-request-correlation',
    nonceByTest={'client-counter': 'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc',
                 'server-action': 'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd'})


def protect(prep, refs, self_ref):
    prep.family(ACTOR_INDEX)
    for ref in refs:
        prep.checked(ref)
    plan = prep.document(ACTOR_PLAN)
    for ref in plan['sourceFamilies']:
        prep.family(ref)
    for ref in plan['protectedInputs']:
        prep.checked(ref)
    prep.checked(self_ref)


def context():
    if not (__debug__ and sys.flags.isolated and sys.dont_write_bytecode and
            type(ACTOR_INDEX) is dict and type(ACTOR_PLAN) is dict and type(COMPOSITION_REVIEW) is dict):
        raise ValueError('Actor/composition Source bindings pending; no helper import, operational output or action')
    import hashlib
    path = Path(PREPARER['path'])
    raw = path.read_bytes()
    if path.resolve() != path or path.is_symlink() or path.stat().st_nlink != 1 or \
            (hashlib.sha256(raw).hexdigest(), len(raw)) != (PREPARER['sha256'], PREPARER['bytes']):
        raise ValueError('Exact genuine Next constructor preparer Source required')
    spec = importlib.util.spec_from_file_location('genuine_next_observer_inner_constructor_root_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    prep.checked(PREPARER)
    actor_index = prep.family(ACTOR_INDEX)
    actor_root = Path(ACTOR_INDEX['path']).parent
    prep.require(actor_root == HERE.parent / 'next-standard-handler-next-runtime-v1' and
        Path(ACTOR_INDEX['path']).name == 'index.json' and
        ACTOR_PLAN['path'] == str(actor_root / 'plan.json') and
        any(dict(row, path=str(actor_root / row['path'])) == ACTOR_PLAN for row in actor_index['files']),
        'Runtime plan is the exact indexed actor member')
    plan = prep.document(ACTOR_PLAN)
    prep.require(plan['bindingState'] == 'READY_CURRENT_CORRELATED_COMPONENT_AND_CLIENT' and
        plan['prospectiveEnvelopeBindingsPending'] is False and
        plan['expectedCompositionReviewState'] == COMPOSITION_REVIEW_STATE and
        plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-wasmtime-deployment' and
        plan['deadlines']['outerSeconds'] == 600 and
        type(plan['sourceFamilies']) is list and bool(plan['sourceFamilies']) and
        type(plan['protectedInputs']) is list and bool(plan['protectedInputs']),
        'Bound current actor with original output/client contract and fresh protected roles')
    review = prep.document(COMPOSITION_REVIEW)
    prep.require(review['state'] == COMPOSITION_REVIEW_STATE and
        review['verifiedPassed'] is True and review['verifiedDataReviewPassed'] is True,
        'Genuine completed Next-envelope composition DATA review')
    for key in ('rawChildBytesVerified', 'siblingDefiningInstancesVerified',
            'sharedNominalResourceAliasesVerified', 'fieldsNominalResourceAliasesVerified',
            'metadataGetterCanonicalOptionsVerified', 'synchronousLiftLowerWithInnerPostReturnVerified',
            'innerExplicitPostReturnPreserved', 'observerManualPostReturnAbsent',
            'internalIncomingHandlerImportComposedAway', 'allFourRequestedToolStepsRawZero',
            'allFourToolStderrEmpty', 'observerNoMarkerBeforeInnerCallSourceVerified',
            'normalFieldsChildDropBeforeOwnForwardSourceVerified'):
        prep.require(review[key] is True, 'Actual Next composition proof: ' + key)
    prep.require(review['runtimeInvoked'] is False and review['runtimeAccepted'] is False and
        review['fullNextAccepted'] is False, 'Composition proof is not deployed application acceptance')
    imports = ['wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10',
        'wasi:clocks/monotonic-clock@0.2.10', 'wasi:http/types@0.2.10', 'wasi:cli/stdout@0.2.10',
        'wasi:cli/environment@0.2.10', 'wasi:clocks/wall-clock@0.2.10', 'wasi:random/random@0.2.10',
        'wasi:filesystem/types@0.2.10', 'wasi:filesystem/preopens@0.2.10', 'wasi:cli/stderr@0.2.10',
        'wasi:http/outgoing-handler@0.2.10']
    prep.require(type(review['selectedImports']) is list and len(review['selectedImports']) == 13 and
        set(review['selectedImports']) == set(imports) and
        review['selectedExports'] == ['wasi:http/incoming-handler@0.2.10'] and
        review['selectedStandardVersion'] == '0.2.10', 'Actual standard external surface')
    inner_review = prep.document(INNER_REVIEW)
    prep.require(inner_review['state'] == 'COORDINATED_NATIVE_EXPORT_DIAGNOSTIC_NEXT_COMPONENT_INIT_DATA_REVIEW_PASSED_V1' and
        inner_review['verifiedPassed'] is True and inner_review['completeReturnedImportAuditVerified'] is True and
        inner_review['rootAuthority'] == INNER_AUTHORITY and
        review['innerComponent'] == inner_review['component'] and
        review['innerConstructionReview'] == INNER_REVIEW and
        review['innerConstructionAuthority'] == INNER_AUTHORITY,
        'Genuine unchanged Next inner construction, never an envelope constructor frame')
    prep.require(plan['acceptedConstructionReview'] == INNER_REVIEW and
        plan['constructionResult'] == inner_review['actualResult'] and
        plan['constructionCallerIndex'] == inner_review['callerSourceIndex'] and
        plan['inputSourceIndex'] == inner_review['inputSourceIndex'] and
        plan['inputEntry'] == inner_review['inputEntry'] and
        plan['expectedComponent'] == {k: inner_review['component'][k] for k in ('sha256', 'bytes')} and
        plan['expectedEnvelopeBindings'] == dict(envelope=review['envelope'], compositionReview=COMPOSITION_REVIEW),
        'Separate actual inner artifact and composed serving envelope bindings')
    fixed = plan['compositionReviewFixedValues']
    prep.require(type(fixed) is dict and bool(fixed), 'Genuine nonempty composition fixed-values map')
    for key, value in fixed.items():
        prep.require(key in review and review[key] == value, 'Exact actual composition fixed value: ' + key)
    observer_root = HERE.parent / 'next-standard-handler-return-observer-v3'
    for key, name in (('observerSource', 'observer.wat'), ('observerManifest', 'manifest.json'),
            ('observerProtocol', 'protocol.json')):
        prep.require(review[key]['path'] == str(observer_root / name),
            'Selected genuine v3 observer Source member: ' + key)
    observer_protocol = prep.document(review['observerProtocol'])
    prep.require(observer_protocol['schemaVersion'] == 3 and observer_protocol['version'] == 3 and
        observer_protocol['marker'] == 'NEXT_STANDARD_HANDLER_RETURN_OBSERVER_V3' and
        observer_protocol['headerName'] == PUBLIC_CORRELATION['headerName'], 'Actual selected metadata protocol')
    observer_source_review = prep.document(review['observerSourceReview'])
    prep.require(observer_source_review['state'] == 'COORDINATED_STANDARD_HANDLER_OBSERVER_V3_COMPOSITION_DATA_REVIEW_PASSED_V1' and
        observer_source_review['verifiedPassed'] is True and observer_source_review['verifiedDataReviewPassed'] is True,
        'Genuine prior same-observer Source/composition prerequisite')
    metadata_probes = prep.document(review['observerMetadataProbeReview'])
    prep.require(metadata_probes['state'] == 'COORDINATED_STANDARD_HANDLER_METADATA_PROBES_RUNTIME_DATA_REVIEW_PASSED_V1' and
        metadata_probes['verifiedPassed'] is True and metadata_probes['verifiedDataReviewPassed'] is True and
        metadata_probes['boundedSixMetadataCasesPassed'] is True and
        metadata_probes['observerSource'] == review['observerSource'] and
        metadata_probes['observerManifest'] == review['observerManifest'] and
        metadata_probes['observerProtocol'] == review['observerProtocol'],
        'Genuine bounded six-case proof of this exact observer, not Next acceptance')
    caller_plan = prep.document(prep.CALLER_PLAN)
    prep.require(plan['node'] == caller_plan['pins']['node'] and
        plan['monitor'] == caller_plan['pins']['monitor'], 'Original pinned Node and monitor APIs')
    block = PUBLIC_CORRELATION
    prep.require(set(block) == {'headerName', 'nonceByTest'} and
        set(block['nonceByTest']) == {'client-counter', 'server-action'} and
        all(type(v) is str and re.fullmatch('[0-9a-f]{64}', v) for v in block['nonceByTest'].values()) and
        len(set(block['nonceByTest'].values())) == 2, 'Exact existing public-correlation declaration schema')
    refs = [PREPARER, INNER_AUTHORITY, INNER_REVIEW, COMPOSITION_REVIEW, ACTOR_INDEX, ACTOR_PLAN,
        plan['node'], plan['wasmtime'], plan['monitor'], plan['clientSource'], plan['browserSource'],
        plan['clientSourceIndex'], plan['browserSourceIndex'], *plan['expectedEnvelopeBindings'].values()]
    refs.extend(inner_review[key] for key in ('actualResult', 'component', 'componentAudit', 'rootAuthority',
        'callerSourceIndex', 'inputSourceIndex', 'inputEntry', 'engine', 'nativeMetadata', 'fullBuildReview'))
    refs.extend(review[key] for key in ('actualBuildResult', 'observerBinary', 'observerSource',
        'observerManifest', 'observerProtocol', 'actualSkeleton', 'observerSourceReview', 'observerMetadataProbeReview'))
    refs.append(review['externalWorld']['wit'])
    self_ref = prep.row(Path(__file__).resolve())
    protect(prep, refs, self_ref)
    construction_authority = prep.document(INNER_AUTHORITY)
    before = prep.admit(construction_authority)
    return prep, plan, review, inner_review, construction_authority, before, self_ref, refs


def runtime_authority(plan, inner_review):
    # The constructed component/audit remain the real inner artifact; only serving selects envelope.
    return dict(schemaVersion=1, state='ROOT_NEXT_PUBLIC_REQUEST_CORRELATION_AUTHORIZED_V1', unissued=False,
        runId=RUN_ID, sourceIndex=ACTOR_INDEX, plan=ACTOR_PLAN,
        component=inner_review['component'], componentAudit=inner_review['componentAudit'],
        constructionResult=inner_review['actualResult'], constructionCallerIndex=inner_review['callerSourceIndex'],
        inputSourceIndex=inner_review['inputSourceIndex'], inputEntry=inner_review['inputEntry'],
        publicRequestCorrelation=PUBLIC_CORRELATION, **plan['expectedEnvelopeBindings'], **FLAGS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--run', action='store_true')
    args = parser.parse_args()
    prep, plan, review, inner_review, construction_authority, before, self_ref, refs = context()
    prep.require(shutil.disk_usage('/private/tmp').free >= 1024**3, 'Existing1GiB runtime floor')
    runtime = runtime_authority(plan, inner_review)
    root = Path(plan['outputPrefix'] + '-' + RUN_ID)
    logs = Path(str(root) + '-external-root')
    prep.require(not root.exists() and not root.is_symlink() and not logs.exists() and not logs.is_symlink() and
        root.resolve() == root and logs.resolve() == logs, 'Fresh canonical original output/client paths')
    path = HERE / 'next-observer-runtime-authority.json'
    preparation = HERE / 'next-observer-runtime-preparation.json'
    receipt_path = HERE / 'next-observer-runtime-owner-result.json'
    if args.prepare:
        prep.require(all(not p.exists() and not p.is_symlink() for p in (path, preparation, receipt_path)),
            'Exclusive fresh Root preparation records')
        protect(prep, refs, self_ref)
        ar = prep.save(path, runtime)
        prep.save(preparation, dict(schemaVersion=1,
            state='ROOT_NEXT_STANDARD_HANDLER_OBSERVER_AUTHORITY_PREPARED_NOT_LAUNCHED_V1', authority=ar,
            controller=self_ref, actorIndex=ACTOR_INDEX, actorPlan=ACTOR_PLAN, compositionReview=COMPOSITION_REVIEW,
            innerAuthority=INNER_AUTHORITY, innerConstructionReview=INNER_REVIEW, constructorGuardBefore=before,
            publicRequestCorrelation=PUBLIC_CORRELATION, actorInvoked=False, nativeBuildInvoked=False))
        prep.admit(construction_authority)
        protect(prep, refs + [ar], self_ref)
        print(json.dumps(dict(authority=ar, actorInvoked=False)))
        return 0
    ar = prep.row(path)
    prep.require(prep.document(ar) == runtime, 'Exact issued fixed Next-observer runtime authority')
    preparation_ref = prep.row(preparation)
    prepared = prep.document(preparation_ref)
    prep.require(prepared['authority'] == ar and prepared['controller'] == self_ref and
        prepared['actorIndex'] == ACTOR_INDEX and prepared['actorPlan'] == ACTOR_PLAN and
        prepared['compositionReview'] == COMPOSITION_REVIEW and prepared['innerAuthority'] == INNER_AUTHORITY and
        prepared['innerConstructionReview'] == INNER_REVIEW and prepared['publicRequestCorrelation'] == PUBLIC_CORRELATION and
        prepared['actorInvoked'] is False and not receipt_path.exists() and not receipt_path.is_symlink(),
        'Exact exclusive preparation for this controller and run')
    protect(prep, refs + [ar, preparation_ref], self_ref)
    caller_plan = prep.document(prep.CALLER_PLAN)
    node, monitor_ref = caller_plan['pins']['node'], caller_plan['pins']['monitor']
    prep.checked(node)
    monitor = prep.original(monitor_ref, 'genuine_next_standard_handler_observer_original_owner')
    logs.mkdir(mode=0o700)
    environment = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
    environment.update(PATH=str(Path(node['path']).parent)+':/usr/bin:/bin',
        NODE_ENV='production', NEXT_TELEMETRY_DISABLED='1', CI='1')
    terminal = None
    primary_set, primary = False, None
    secondary_errors = []
    after, protected = None, False
    try:
        terminal = monitor.monitor([node['path'], str(Path(ACTOR_INDEX['path']).parent / 'deploy.mjs'), str(path)],
            str(HERE.parent.parents[3]), environment, logs, 600, ar)
    except BaseException as error:
        primary_set, primary = True, error
    finally:
        try:
            after = prep.admit(construction_authority)
            protect(prep, refs + [ar, preparation_ref], self_ref)
            protected = True
        except BaseException as error:
            if primary_set:
                secondary_errors.append(dict(stage='final-protection', name=type(error).__name__, message=str(error)[:2048]))
            else:
                primary_set, primary = True, error
    try:
        prep.save(logs / 'world-guard.json', dict(before=before, after=after, unchanged=before == after,
            nativeInputsPreserved=protected, constructorPreparer=PREPARER, controller=self_ref,
            actorIndex=ACTOR_INDEX, actorPlan=ACTOR_PLAN, compositionReview=COMPOSITION_REVIEW,
            innerAuthority=INNER_AUTHORITY, innerConstructionReview=INNER_REVIEW))
    except BaseException as error:
        if primary_set:
            secondary_errors.append(dict(stage='guard-publication', name=type(error).__name__, message=str(error)[:2048]))
        else:
            primary_set, primary = True, error
    clean = terminal is not None and not terminal['timeout'] and not terminal['forcedCleanup'] and \
        terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and all(not terminal[k] for k in
        ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
    try:
        receipt = dict(schemaVersion=1, state='ROOT_NEXT_STANDARD_HANDLER_OBSERVER_OWNER_COMPLETED_UNREVIEWED_V1',
            rawExitCode=None if terminal is None else terminal['rawExitCode'],
            originalOwner=None if terminal is None else terminal['pid'], cleanOwner=clean,
            ownerInvocationAttempted=True, finalInputsPreserved=protected,
            invocationOrFinalizationError=None if not primary_set else dict(name=type(primary).__name__, message=str(primary)[:2048]),
            secondaryErrors=secondary_errors, authority=ar,
            terminal=prep.row(logs / 'terminal.json') if (logs / 'terminal.json').exists() else None,
            worldGuard=prep.row(logs / 'world-guard.json') if (logs / 'world-guard.json').exists() else None,
            controller=self_ref, actorIndex=ACTOR_INDEX, actorPlan=ACTOR_PLAN, compositionReview=COMPOSITION_REVIEW,
            innerAuthority=INNER_AUTHORITY, innerConstructionReview=INNER_REVIEW,
            actualRuntimeDataReviewRequired=True, fullNextAccepted=False)
        prep.save(receipt_path, receipt)
        print(json.dumps(receipt))
    except BaseException:
        if primary_set:
            raise primary
        raise
    if primary_set:
        raise primary
    return 0 if clean and protected and terminal['rawExitCode'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
