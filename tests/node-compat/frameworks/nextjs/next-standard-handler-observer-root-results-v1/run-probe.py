"""Root one-GET standard-handler return probe; NULL actor pins refuse all actions."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ACTOR_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-standard-handler-return-probe-runtime-v1/index.json', 'sha256': 'c418a6d0eb0871af41ed10d88d0a0573de49f857c507279906278e1a6c74905b', 'bytes': 821}
ACTOR_PLAN = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-standard-handler-return-probe-runtime-v1/plan.json', 'sha256': 'eafa796cbac5743bcf1df1847bc352191ef6d5076ceabfeabc12a31ddd7dc1fd', 'bytes': 10162}
INNER_ROOT = HERE.parent / 'next-native-export-diagnostic-probe-root-results-v1'
PREPARER = dict(path=str(INNER_ROOT / 'prepare-construction.py'),
    sha256='62142edc1a76bd7c47bc482737c16faa2364cde898ffb790aebf8a8ebf0859ef', bytes=17890)
INNER_AUTHORITY = dict(path=str(INNER_ROOT / 'diagnostic-probe-construction-authority.json'),
    sha256='4548cc3f0627fc338986119ac223b81c43468e097ecf9eba64dff8d5fd2a586d', bytes=5596754)
REVIEW = dict(path=str(HERE / 'actual-composition-review.json'),
    sha256='1c1f8bae049e78d77dc1cfc0a46c5c877c5b355dc6b4e9ae8a4bc38ffcd729aa', bytes=22551)
RUN_ID = 'return-probe-first'
FLAGS = dict(localhostServeAllowed=True, probeAllowed=True, browserAllowed=False,
    guestEnvironmentAllowed=False, outgoingHttpWorkloadSelected=False, automaticRetryAllowed=False,
    mountsAllowed=False, constructorAllowed=False, nativeBuildAllowed=False)


def protect(prep, refs, self_ref):
    prep.family(ACTOR_INDEX)
    for ref in refs:
        prep.checked(ref)
    prep.checked(self_ref)


def context():
    if not (__debug__ and sys.flags.isolated and sys.dont_write_bytecode and
            type(ACTOR_INDEX) is dict and type(ACTOR_PLAN) is dict):
        raise ValueError('Actor Source bindings pending; no helper import, output or action')
    import hashlib
    path = Path(PREPARER['path'])
    raw = path.read_bytes()
    if path.resolve() != path or path.is_symlink() or path.stat().st_nlink != 1 or \
            (hashlib.sha256(raw).hexdigest(), len(raw)) != (PREPARER['sha256'], PREPARER['bytes']):
        raise ValueError('Exact genuine inner probe constructor preparer Source required')
    spec = importlib.util.spec_from_file_location('genuine_inner_probe_constructor_root_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    prep.checked(PREPARER)
    actor_index = prep.family(ACTOR_INDEX)
    actor_root = Path(ACTOR_INDEX['path']).parent
    prep.require(actor_root == HERE.parent / 'next-standard-handler-return-probe-runtime-v1' and
        Path(ACTOR_INDEX['path']).name == 'index.json' and
        ACTOR_PLAN['path'] == str(actor_root / 'plan.json') and
        any(dict(row, path=str(actor_root / row['path'])) == ACTOR_PLAN for row in actor_index['files']),
        'Runtime plan is the exact indexed actor member')
    plan = prep.document(ACTOR_PLAN)
    prep.require(plan['prospectiveCompositionBindingsPending'] is False and
        plan['ownerSeconds'] == 180 and plan['stdoutLimitBytes'] == 8388608,
        'Bound one-GET actor with original owner and capture bounds')
    review = prep.document(REVIEW)
    prep.require(review['state'] == 'COORDINATED_STANDARD_HANDLER_OBSERVER_V2_COMPOSITION_DATA_REVIEW_PASSED_V1'
        and review['verifiedPassed'] is True and review['verifiedDataReviewPassed'] is True,
        'Genuine completed composition DATA review')
    for key in ('rawChildBytesVerified', 'siblingDefiningInstancesVerified',
            'sharedNominalResourceAliasesVerified', 'synchronousLiftLowerWithInnerPostReturnVerified',
            'innerExplicitPostReturnPreserved', 'observerManualPostReturnAbsent',
            'internalIncomingHandlerImportComposedAway', 'allSevenRequestedToolStepsRawZero',
            'allSevenToolStderrEmpty'):
        prep.require(review[key] is True, 'Actual composition proof: ' + key)
    prep.require(review['runtimeInvoked'] is False and review['runtimeAccepted'] is False and
        review['fullNextAccepted'] is False, 'Composition review is not runtime acceptance')
    imports = ['wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10',
        'wasi:clocks/monotonic-clock@0.2.10', 'wasi:http/types@0.2.10', 'wasi:cli/stdout@0.2.10',
        'wasi:cli/environment@0.2.10', 'wasi:clocks/wall-clock@0.2.10', 'wasi:random/random@0.2.10',
        'wasi:filesystem/types@0.2.10', 'wasi:filesystem/preopens@0.2.10', 'wasi:cli/stderr@0.2.10',
        'wasi:http/outgoing-handler@0.2.10']
    prep.require(review['selectedImports'] == imports and
        review['selectedExports'] == ['wasi:http/incoming-handler@0.2.10'] and
        review['selectedStandardVersion'] == '0.2.10', 'Actual standard external surface')
    expected_inner = dict(innerComponent=review['innerComponent'],
        innerConstructionReview=review['innerConstructionReview'],
        innerConstructionAuthority=review['innerConstructionAuthority'])
    prep.require(plan['knownInnerInputs'] == expected_inner and
        expected_inner['innerConstructionAuthority'] == INNER_AUTHORITY and
        plan['expectedEnvelopeBindings'] == dict(envelope=review['envelope'], compositionReview=REVIEW),
        'Separate original inner and actual composed envelope roles')
    fixed = plan['compositionReviewFixedValues']
    prep.require(type(fixed) is dict and bool(fixed), 'Genuine nonempty composition fixed-values map')
    for key, value in fixed.items():
        prep.require(key in review and review[key] == value, 'Exact actual composition fixed value: ' + key)
    for key in ('observerSource', 'observerManifest', 'observerProtocol'):
        prep.require(plan[key] == review[key], 'Selected reviewed observer role: ' + key)
    inner_review = prep.document(expected_inner['innerConstructionReview'])
    prep.require(inner_review['state'] == 'COORDINATED_NATIVE_EXPORT_DIAGNOSTIC_PROBE_COMPONENT_INIT_DATA_REVIEW_PASSED_V1'
        and inner_review['verifiedPassed'] is True and inner_review['completeReturnedImportAuditVerified'] is True
        and inner_review['component'] == expected_inner['innerComponent']
        and inner_review['rootAuthority'] == INNER_AUTHORITY,
        'Genuine unchanged inner construction, not an envelope constructor frame')
    caller_plan = prep.document(prep.CALLER_PLAN)
    prep.require(plan['node'] == caller_plan['pins']['node'] and
        plan['monitor'] == caller_plan['pins']['monitor'], 'Original pinned Node and monitor APIs')
    refs = [PREPARER, REVIEW, INNER_AUTHORITY, ACTOR_INDEX, ACTOR_PLAN,
        *expected_inner.values(), *plan['expectedEnvelopeBindings'].values(),
        plan['node'], plan['wasmtime'], plan['monitor'], plan['caseContract']]
    refs.extend(review[key] for key in ('actualBuildResult', 'observerBinary', 'innerComponentAudit',
        'structureReview', 'observerSource', 'observerManifest', 'observerProtocol', 'actualSkeleton'))
    refs.append(review['externalWorld']['wit'])
    self_ref = prep.row(Path(__file__).resolve())
    protect(prep, refs, self_ref)
    authority = prep.document(INNER_AUTHORITY)
    world = prep.admit(authority)
    return prep, plan, review, authority, world, self_ref, refs


def runtime_authority(plan):
    return dict(schemaVersion=1, state='ROOT_STANDARD_HANDLER_RETURN_PROBE_RUNTIME_AUTHORIZED_V1',
        unissued=False, runId=RUN_ID, sourceIndex=ACTOR_INDEX, plan=ACTOR_PLAN,
        **plan['knownInnerInputs'], **plan['expectedEnvelopeBindings'], **FLAGS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--run', action='store_true')
    args = parser.parse_args()
    prep, plan, review, construction_authority, before, self_ref, refs = context()
    prep.require(shutil.disk_usage('/private/tmp').free >= 1024**3, 'Existing1GiB runtime floor')
    runtime = runtime_authority(plan)
    root = Path(plan['outputPrefix'] + '-' + RUN_ID)
    logs = Path(str(root) + '-external-root')
    prep.require(not root.exists() and not root.is_symlink() and not logs.exists() and not logs.is_symlink() and
        root.resolve() == root and logs.resolve() == logs,
        'Fresh canonical runtime paths')
    path = HERE / 'return-probe-runtime-authority.json'
    preparation = HERE / 'return-probe-runtime-preparation.json'
    receipt_path = HERE / 'return-probe-runtime-owner-result.json'
    if args.prepare:
        prep.require(all(not p.exists() and not p.is_symlink() for p in
            (path, preparation, receipt_path)), 'Exclusive fresh Root preparation records')
        protect(prep, refs, self_ref)
        ar = prep.save(path, runtime)
        prep.save(preparation, dict(schemaVersion=1,
            state='ROOT_STANDARD_HANDLER_RETURN_PROBE_AUTHORITY_PREPARED_NOT_LAUNCHED_V1', authority=ar,
            controller=self_ref, actorIndex=ACTOR_INDEX, actorPlan=ACTOR_PLAN, compositionReview=REVIEW, innerAuthority=INNER_AUTHORITY,
            constructorGuardBefore=before, actorInvoked=False, nativeBuildInvoked=False))
        prep.admit(construction_authority)
        protect(prep, refs + [ar], self_ref)
        print(json.dumps(dict(authority=ar, actorInvoked=False)))
        return 0
    ar = prep.row(path)
    prep.require(prep.document(ar) == runtime, 'Exact issued one-GET runtime authority')
    preparation_ref = prep.row(preparation)
    prepared = prep.document(preparation_ref)
    prep.require(prepared['authority'] == ar and prepared['controller'] == self_ref and
        prepared['actorIndex'] == ACTOR_INDEX and prepared['actorPlan'] == ACTOR_PLAN and
        prepared['compositionReview'] == REVIEW and prepared['innerAuthority'] == INNER_AUTHORITY and
        prepared['actorInvoked'] is False and not receipt_path.exists() and not receipt_path.is_symlink(),
        'Exact exclusive preparation for this controller and run')
    protect(prep, refs + [ar, preparation_ref], self_ref)
    caller_plan = prep.document(prep.CALLER_PLAN)
    node, monitor_ref = caller_plan['pins']['node'], caller_plan['pins']['monitor']
    prep.checked(node)
    monitor = prep.original(monitor_ref, 'genuine_return_probe_runtime_original_owner')
    logs.mkdir(mode=0o700)
    environment = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
    environment.update(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C')
    terminal = None
    primary_set, primary = False, None
    secondary_errors = []
    after, protected = None, False
    try:
        terminal = monitor.monitor([node['path'], str(Path(ACTOR_INDEX['path']).parent / 'run.mjs'),
            '--authority', str(path)], str(HERE.parent.parents[3]), environment, logs, 180, ar)
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
            actorIndex=ACTOR_INDEX, actorPlan=ACTOR_PLAN, compositionReview=REVIEW, innerAuthority=INNER_AUTHORITY))
    except BaseException as error:
        if primary_set:
            secondary_errors.append(dict(stage='guard-publication', name=type(error).__name__, message=str(error)[:2048]))
        else:
            primary_set, primary = True, error
    clean = terminal is not None and not terminal['timeout'] and not terminal['forcedCleanup'] and \
        terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and all(not terminal[k] for k in
        ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
    try:
        receipt = dict(schemaVersion=1, state='ROOT_STANDARD_HANDLER_RETURN_PROBE_OWNER_COMPLETED_UNREVIEWED_V1',
            rawExitCode=None if terminal is None else terminal['rawExitCode'],
            originalOwner=None if terminal is None else terminal['pid'], cleanOwner=clean,
            ownerInvocationAttempted=True, finalInputsPreserved=protected,
            invocationOrFinalizationError=None if not primary_set else dict(name=type(primary).__name__, message=str(primary)[:2048]),
            secondaryErrors=secondary_errors, authority=ar,
            terminal=prep.row(logs / 'terminal.json') if (logs / 'terminal.json').exists() else None,
            worldGuard=prep.row(logs / 'world-guard.json') if (logs / 'world-guard.json').exists() else None,
            controller=self_ref, actorIndex=ACTOR_INDEX, actorPlan=ACTOR_PLAN, compositionReview=REVIEW, innerAuthority=INNER_AUTHORITY,
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
