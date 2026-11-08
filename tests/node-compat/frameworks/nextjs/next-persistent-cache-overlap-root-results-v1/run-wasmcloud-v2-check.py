"""Root stock wasmCloud cache controller; NULL actor pins refuse all actions."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ACTOR_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-persistent-cache-overlap-wasmcloud-v2/index.json', 'sha256': '95ca9c272803a54563f3e79945260cbd5bdd793fe59fa0ca9fc4f76369d9ed28', 'bytes': 804}
ACTOR_PLAN = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-persistent-cache-overlap-wasmcloud-v2/plan.json', 'sha256': '6e290fc0cc59f484c540502c242f86dbbbeb7c1163a881e53e27e5c96762e031', 'bytes': 14453}
PREPARER = dict(path=str(HERE / 'prepare-construction.py'),
    sha256='10e2deb598b8b065dc4ded8553dc70f1b5ad86034e8ffaf2666846d9ee1194cf', bytes=17844)
REVIEW = dict(path=str(HERE / 'actual-construction-review.json'),
    sha256='0599a450d6152b34f786db8d642a44f82bed7f5b8e03fcbed76b9f64c7d08e97', bytes=30191)
RUN_ID = 'cloud-v2-first'
FLAGS = dict(localhostServeAllowed=True, cacheSuiteAllowed=True, applicationCopyAllowed=True,
    fixtureCopyAllowed=True, writableTestRootAllowed=True, browserAllowed=False,
    guestEnvironmentAllowed=False, outgoingHttpWorkloadSelected=False, automaticRetryAllowed=False,
    nativeBuildAllowed=False, constructorAllowed=False, stockHostAllowed=True, configInspectAllowed=True,
    externalNetworkAllowed=False, newServicesAllowed=False, hostMutationAllowed=False)


def context():
    if not (__debug__ and sys.flags.isolated and sys.dont_write_bytecode and
            type(ACTOR_INDEX) is dict and type(ACTOR_PLAN) is dict):
        raise ValueError('Actor Source bindings pending; no helper import, output or action')
    import hashlib
    path = Path(PREPARER['path'])
    raw = path.read_bytes()
    if path.resolve() != path or path.is_symlink() or path.stat().st_nlink != 1 or \
            (hashlib.sha256(raw).hexdigest(), len(raw)) != (PREPARER['sha256'], PREPARER['bytes']):
        raise ValueError('Exact genuine constructor preparer Source required')
    spec = importlib.util.spec_from_file_location('genuine_cache_constructor_root_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    prep.checked(PREPARER)
    actor_index = prep.family(ACTOR_INDEX)
    actor_root = Path(ACTOR_INDEX['path']).parent
    prep.require(Path(ACTOR_INDEX['path']).name == 'index.json' and
        ACTOR_PLAN['path'] == str(actor_root / 'plan.json') and
        any(dict(row, path=str(actor_root / row['path'])) == ACTOR_PLAN for row in actor_index['files']),
        'Runtime plan is the exact indexed actor member')
    plan = prep.document(ACTOR_PLAN)
    review = prep.document(REVIEW)
    prep.require(review['state'] == 'COORDINATED_PERSISTENT_CACHE_OVERLAP_COMPONENT_INIT_DATA_REVIEW_PASSED_V1'
        and review['verifiedPassed'] is True and review['completeReturnedImportAuditVerified'] is True,
        'Genuine completed cache INIT review')
    expected = dict(component=review['component'], componentAudit=review['componentAudit'],
        constructionResult=review['actualResult'], constructionDataReview=REVIEW,
        constructionCallerIndex=review['callerSourceIndex'], constructionPlan=review['callerPlan'],
        constructionRootAuthority=review['rootAuthority'], constructionWorldGuard=review['constructionWorldGuard'])
    prep.require(plan['expectedBindings'] == expected and plan['expectedConstructorReviewState'] == review['state'],
        'Fresh genuine eight-role runtime selection')
    for ref in expected.values():
        prep.checked(ref)
    result = prep.document(review['actualResult'])
    audit = prep.document(review['componentAudit'])
    prep.require(result['passed'] is True and result['artifacts']['component'] == review['component'] and
        result['artifacts']['componentAudit'] == review['componentAudit'] and
        result['rootAuthority'] == review['rootAuthority'] and result['callerIndex'] == review['callerSourceIndex'] and
        result['plan'] == review['callerPlan'] and audit['passed'] is True and
        audit['component'] == review['component'], 'Actual new result/audit roles')
    prep.require(review['engine'] == prep.ENGINE and review['nativeMetadata'] == prep.NATIVE_METADATA and
        review['fullBuildReview'] == prep.BUILD_REVIEW and review['fullBuildSourceReview'] == prep.BUILD_SOURCE_REVIEW,
        'Existing genuine native build bindings')
    prep.require(plan['knownInputs'] == dict(engine=prep.ENGINE, nativeMetadata=prep.NATIVE_METADATA,
        fullNativeBuildReview=prep.BUILD_REVIEW, fullNativeBuildSourceReview=prep.BUILD_SOURCE_REVIEW),
        'Runtime actual native prerequisites')
    caller_plan = prep.document(prep.CALLER_PLAN)
    prep.require(plan['node'] == caller_plan['pins']['node'], 'Same pinned Node tool')
    authority = prep.document(review['rootAuthority'])
    world = prep.admit(authority)
    self_ref = prep.row(Path(__file__).resolve())
    return prep, plan, review, authority, world, self_ref


def runtime_authority(plan):
    return dict(schemaVersion=1, state='ROOT_PERSISTENT_CACHE_OVERLAP_WASMCLOUD_AUTHORIZED_V1',
        unissued=False, runId=RUN_ID, sourceIndex=ACTOR_INDEX, plan=ACTOR_PLAN,
        **plan['expectedBindings'], **plan['knownInputs'], **FLAGS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--run', action='store_true')
    args = parser.parse_args()
    prep, plan, review, construction_authority, before, self_ref = context()
    prep.require(shutil.disk_usage('/private/tmp').free >= 1024**3, 'Existing1GiB runtime floor')
    runtime = runtime_authority(plan)
    root = Path(plan['outputPrefix'] + '-' + RUN_ID)
    logs = Path(str(root) + '-external-root')
    prep.require(not root.exists() and not logs.exists() and root.resolve() == root and logs.resolve() == logs,
        'Fresh canonical runtime paths')
    path = HERE / 'cache-overlap-wasmcloud-v2-authority.json'
    if args.prepare:
        ar = prep.save(path, runtime)
        prep.save(HERE / 'wasmcloud-v2-preparation.json', dict(schemaVersion=1,
            state='ROOT_CACHE_WASMCLOUD_AUTHORITY_PREPARED_NOT_LAUNCHED_V1', authority=ar,
            controller=self_ref, actorIndex=ACTOR_INDEX, actorPlan=ACTOR_PLAN, constructionReview=REVIEW,
            constructorGuardBefore=before, actorInvoked=False, nativeBuildInvoked=False))
        prep.admit(construction_authority)
        print(json.dumps(dict(authority=ar, actorInvoked=False)))
        return 0
    ar = prep.row(path)
    prep.require(prep.document(ar) == runtime, 'Exact issued one-GET runtime authority')
    caller_plan = prep.document(prep.CALLER_PLAN)
    node, monitor_ref = caller_plan['pins']['node'], caller_plan['pins']['monitor']
    prep.checked(node)
    monitor = prep.original(monitor_ref, 'genuine_cache_runtime_original_owner')
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
            prep.family(ACTOR_INDEX)
            prep.checked(ACTOR_PLAN)
            prep.checked(REVIEW)
            prep.checked(self_ref)
            prep.checked(ar)
            protected = True
        except BaseException as error:
            if primary_set:
                secondary_errors.append(dict(stage='final-protection', name=type(error).__name__, message=str(error)[:2048]))
            else:
                primary_set, primary = True, error
    try:
        prep.save(logs / 'world-guard.json', dict(before=before, after=after, unchanged=before == after,
            nativeInputsPreserved=protected, constructorPreparer=PREPARER, controller=self_ref,
            actorIndex=ACTOR_INDEX, actorPlan=ACTOR_PLAN, constructionReview=REVIEW))
    except BaseException as error:
        if primary_set:
            secondary_errors.append(dict(stage='guard-publication', name=type(error).__name__, message=str(error)[:2048]))
        else:
            primary_set, primary = True, error
    clean = terminal is not None and not terminal['timeout'] and not terminal['forcedCleanup'] and \
        terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and all(not terminal[k] for k in
        ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
    try:
        receipt = dict(schemaVersion=1, state='ROOT_CACHE_WASMCLOUD_ONE_GET_OWNER_COMPLETED_UNREVIEWED_V1',
            rawExitCode=None if terminal is None else terminal['rawExitCode'],
            originalOwner=None if terminal is None else terminal['pid'], cleanOwner=clean,
            ownerInvocationAttempted=True, finalInputsPreserved=protected,
            invocationOrFinalizationError=None if not primary_set else dict(name=type(primary).__name__, message=str(primary)[:2048]),
            secondaryErrors=secondary_errors, authority=ar,
            terminal=prep.row(logs / 'terminal.json') if (logs / 'terminal.json').exists() else None,
            worldGuard=prep.row(logs / 'world-guard.json') if (logs / 'world-guard.json').exists() else None,
            controller=self_ref, actorIndex=ACTOR_INDEX, actorPlan=ACTOR_PLAN, constructionReview=REVIEW,
            actualRuntimeDataReviewRequired=True, fullNextAccepted=False)
        prep.save(HERE / 'wasmcloud-v2-owner-result.json', receipt)
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
