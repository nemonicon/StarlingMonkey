"""Prepare both fixed nonredirect controls; run one original owner at a time."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
BINDINGS = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-nonredirect-action-root-results-v1/runtime-bindings.json', 'sha256': 'd69c6809801b8822f30d398721290bd7655faab1983f3f477b7bfc300c6a0d7f', 'bytes': 550372}
PREPARER = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'),
    sha256='4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', bytes=19784)
INNER_AUTHORITY = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/diagnostic-next-construction-authority.json'),
    sha256='23313b9b1858e22df729b379c10750cd92ba00ce4aa9bee179fc21142fdfea66', bytes=5597386)
INNER_REVIEW = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
    sha256='5c284564e0ddefba507c5429acd98c42393d5c0f2764105a4046f0665f51e16a', bytes=22550)
COMPOSITION_REVIEW = dict(path=str(BASE / 'next-standard-handler-observer-root-results-v1/actual-next-v3-composition-review.json'),
    sha256='b333fbc736e653f0a56bbe7ee031b3b943faf3e4d2ea687112659465171e2387', bytes=33472)
PUBLIC = dict(headerName='x-next-public-request-correlation',
    nonceByTest={'client-counter': 'e' * 64, 'server-action': 'f' * 64})


def context():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and type(BINDINGS) is dict, 'Unbound Source refuses helper import/action'
    path = Path(PREPARER['path'])
    raw = path.read_bytes()
    assert path.resolve() == path and not path.is_symlink() and path.stat().st_nlink == 1
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (PREPARER['sha256'], PREPARER['bytes'])
    spec = importlib.util.spec_from_file_location('genuine_nonredirect_control_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    binding = prep.document(BINDINGS)
    assert binding['state'] == 'ROOT_NONREDIRECT_ACTION_ACTUAL_RUNTIME_BINDINGS_V1'
    assert binding['compositionReview'] == COMPOSITION_REVIEW and binding['innerConstructionReview'] == INNER_REVIEW
    actor_index = prep.family(binding['actorIndex'])
    browser_index = prep.family(binding['browserIndex'])
    actor_root = Path(binding['actorIndex']['path']).parent
    browser_root = Path(binding['browserIndex']['path']).parent
    assert actor_root == BASE / 'next-nonredirect-action-runtime-v1'
    assert browser_root == BASE / 'next-nonredirect-action-browser-v1'
    for role, name in [('nativePlan', 'plan.json'), ('stockPlan', 'stock-plan.json')]:
        assert binding[role]['path'] == str(actor_root / name)
        assert any(dict(r, path=str(actor_root / r['path'])) == binding[role] for r in actor_index['files'])
    app = prep.document(binding['applicationBuildReview'])
    assert app['state'] == 'COORDINATED_NONREDIRECT_ACTION_APP_BUILD_DATA_REVIEW_PASSED_V1' and app['verifiedPassed'] is True
    inner = prep.document(INNER_REVIEW)
    assert inner['verifiedPassed'] is True and inner['rootAuthority'] == INNER_AUTHORITY
    composition = prep.document(COMPOSITION_REVIEW)
    assert composition['verifiedPassed'] is True and composition['verifiedDataReviewPassed'] is True
    assert composition['innerComponent'] == inner['component'] and composition['innerConstructionAuthority'] == INNER_AUTHORITY
    assert len(composition['selectedImports']) == 13 and all(x.endswith('@0.2.10') for x in composition['selectedImports'])
    assert composition['selectedExports'] == ['wasi:http/incoming-handler@0.2.10']
    plans = {arm: prep.document(binding[arm + 'Plan']) for arm in ('native', 'stock')}
    for arm, plan in plans.items():
        assert plan['controlOnly'] is True and plan['prospectiveNonredirectAppBindingsPending'] is False
        assert plan['applicationBuildReview'] == binding['applicationBuildReview']
        assert plan['applicationBuildResult'] == app['actualResult'] and plan['applicationInputs'] == app['applicationInputs']
        assert plan['applicationRootIdentityEvidence'] == app['applicationRootIdentityEvidence']
        assert plan['clientSourceIndex'] == binding['browserIndex'] and plan['browserSourceIndex'] == binding['browserIndex']
        for role, name in [('clientSource', 'run-browser.mjs'), ('browserSource', 'browser-check.mjs')]:
            assert plan[role]['path'] == str(browser_root / name)
            assert any(dict(r, path=str(browser_root / r['path'])) == plan[role] for r in browser_index['files'])
        assert plan['node'] == plans['native']['node'] and plan['monitor'] == plans['native']['monitor']
        prefix = Path(plan['outputPrefix'])
        assert prefix.parent == Path('/private/tmp/starling-node-compat') and prefix.resolve() == prefix
        assert plan['runId'] == ('nonredirect-native-first' if arm == 'native' else 'nonredirect-stock-first')
    self_ref = prep.row(Path(__file__).resolve())

    def protect():
        for ref in [PREPARER, INNER_AUTHORITY, INNER_REVIEW, COMPOSITION_REVIEW, BINDINGS, self_ref]:
            prep.checked(ref)
        prep.family(binding['actorIndex'])
        prep.family(binding['browserIndex'])
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


def make_authority(arm, binding, plans, inner, composition):
    common = dict(schemaVersion=1, arm=arm, runId=plans[arm]['runId'], sourceIndex=binding['actorIndex'],
        controlOnly=True, nonredirectActionControlAllowed=True, publicRequestCorrelationAllowed=True,
        publicRequestCorrelation=PUBLIC, compilerAllowed=False, nativeBuildAllowed=False,
        automaticRetry=False, replacementTrials=False, fullNextAccepted=False)
    if arm == 'native':
        return dict(common, state='ROOT_NEXT_NONREDIRECT_ACTION_NATIVE_CONTROL_AUTHORIZED_V1',
            plan=binding['nativePlan'], component=inner['component'], componentAudit=inner['componentAudit'],
            constructionResult=inner['actualResult'], constructionCallerIndex=inner['callerSourceIndex'],
            inputSourceIndex=inner['inputSourceIndex'], inputEntry=inner['inputEntry'],
            envelope=composition['envelope'], compositionReview=COMPOSITION_REVIEW,
            localhostServeAllowed=True, actualNextGuestAllowed=True, browserAllowed=True,
            standardHandlerObserverAllowed=True, componentConstructionAllowed=False,
            externalDeploymentAllowed=False, adoptionAllowed=False)
    return dict(common, state='ROOT_NEXT_NONREDIRECT_ACTION_HOST_CONTROL_AUTHORIZED_V1',
        plans=binding['stockPlan'], rootAuthorityPath=str(HERE / 'stock-authority.json'),
        localhostServerAllowed=True, browserAllowed=True, guestAllowed=False, engineAllowed=False,
        externalApplicationDeploymentAllowed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare', action='store_true')
    modes.add_argument('--run', choices=['native', 'stock'])
    args = parser.parse_args()
    prep, binding, plans, inner, composition, self_ref, protect, original, before = context()
    assert shutil.disk_usage('/private/tmp').free >= 1024**3
    prepared_path = HERE / 'control-preparation.json'
    if args.prepare:
        assert not prepared_path.exists()
        slots = []
        for arm in ('native', 'stock'):
            path = HERE / (arm + '-authority.json')
            output = Path(plans[arm]['outputPrefix'] + '-' + plans[arm]['runId'])
            assert all(not x.exists() and not x.is_symlink() for x in (path, output, Path(str(output) + '-external-root'), HERE / (arm + '-owner-result.json')))
            slots.append((arm, path, output))
        rows = []
        for arm, path, output in slots:
            rows.append(dict(arm=arm, authority=prep.save(path, make_authority(arm, binding, plans, inner, composition)),
                outputRoot=str(output), ownerOutputRoot=str(output) + '-external-root', ownerSeconds=600 if arm == 'native' else 300))
        prep.admit(original)
        protect()
        prep.save(prepared_path, dict(schemaVersion=1, state='ROOT_FIXED_NONREDIRECT_ACTION_PAIR_PREPARED_NOT_RUN_V1',
            controller=self_ref, bindings=BINDINGS, trials=rows, order=['native', 'stock'], publicRequestCorrelation=PUBLIC,
            constructorGuardBefore=before, actorsInvoked=False, automaticRetry=False, replacementTrials=False,
            oldRedirectFailuresWaived=False, fullOriginalContractExecuted=False, fullNextAccepted=False))
        print(json.dumps(dict(prepared=prep.row(prepared_path), actorsInvoked=False)))
        return 0
    arm = args.run
    prepared_ref = prep.row(prepared_path)
    prepared = prep.document(prepared_ref)
    assert prepared['controller'] == self_ref and prepared['bindings'] == BINDINGS
    assert prepared['state'] == 'ROOT_FIXED_NONREDIRECT_ACTION_PAIR_PREPARED_NOT_RUN_V1'
    assert prepared['order'] == ['native', 'stock'] and [x['arm'] for x in prepared['trials']] == ['native', 'stock']
    for item in prepared['trials']:
        expected_output = plans[item['arm']]['outputPrefix'] + '-' + plans[item['arm']]['runId']
        assert item['outputRoot'] == expected_output and item['ownerOutputRoot'] == expected_output + '-external-root'
        assert item['ownerSeconds'] == (600 if item['arm'] == 'native' else 300)
    trial = next(x for x in prepared['trials'] if x['arm'] == arm)
    ar = trial['authority']
    assert prep.document(ar) == make_authority(arm, binding, plans, inner, composition)
    if arm == 'stock':
        try:
            previous = prep.document(prep.row(HERE / 'native-owner-result.json'))
            native_trial = next(x for x in prepared['trials'] if x['arm'] == 'native')
            assert previous['controller'] == self_ref and previous['bindings'] == BINDINGS
            assert previous['authority'] == native_trial['authority']
            assert prep.document(previous['authority']) == make_authority('native', binding, plans, inner, composition)
            assert previous['cleanOwner'] and previous['finalInputsPreserved'] and previous['error'] is None
            assert previous['rawExitCode'] in (0, 1) and previous['secondaryErrors'] == []
            assert previous['constructorGuardBefore'] == previous['constructorGuardAfter'] == before
            assert previous['terminal']['path'] == str(Path(native_trial['ownerOutputRoot']) / 'terminal.json')
            native_terminal = prep.document(previous['terminal'])
            assert native_terminal['authority'] == native_trial['authority']
            assert native_terminal['pid'] == previous['originalOwner'] and native_terminal['rawExitCode'] == previous['rawExitCode']
            assert not native_terminal['timeout'] and not native_terminal['forcedCleanup']
            assert native_terminal['parentOwnedGroupGone'] and native_terminal['allObservedOwnedGroupsGone']
            assert all(not native_terminal[k] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
            native_output = Path(plans['native']['outputPrefix'] + '-' + plans['native']['runId'])
            observed = prep.document(prep.row(native_output / 'result.json'))
            assert observed['rootAuthority'] == native_trial['authority'] and observed['sourceIndex'] == binding['actorIndex']
            assert observed['servedEnvelope'] == composition['envelope']
            assert observed['originalInputsPreserved'] and observed['readonlyAppPreserved']
            assert observed['server']['stdoutCapture']['complete'] and observed['server']['shutdownRequested']
            assert not observed['server']['forcedCleanup'] and observed['server']['exit'] == dict(code=0, signal=None, error=None)
            assert observed['client']['exit']['code'] in (0, 1) and observed['client']['exit']['signal'] is None and observed['client']['exit']['error'] is None
            capture = observed['server']['stdoutCapture']
            stdout = observed['server']['stdout']
            assert stdout['path'] == capture['path'] == str(native_output / 'wasmtime.stdout.log')
            assert type(stdout['bytes']) is int and 0 <= stdout['bytes'] <= 8388608
            assert capture['limitBytes'] == 8388608 and capture['errors'] == []
            assert all(capture[k] for k in ('pipeEof', 'fileClosed', 'fileBoundVerified', 'finalized', 'complete'))
            assert all(not capture[k] for k in ('overflow', 'partialWritePossible', 'unretainedBytesUnknown'))
            assert stdout['bytes'] == capture['fileBytes'] == capture['completeWriteBytes'] == capture['lastReservedWriteCeiling']
            prep.checked(stdout)
        except BaseException as error:
            try:
                prep.save(HERE / 'stock-unattempted.json', dict(schemaVersion=1,
                    state='NONREDIRECT_STOCK_SLOT_UNATTEMPTED_NATIVE_COLLECTION_UNCERTAIN_V1',
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
    argv = ([node['path'], str(actor / 'deploy.mjs'), ar['path']] if arm == 'native' else
        [node['path'], str(actor / 'run-stock.mjs'), trial['outputRoot'], plan['standaloneSource'], plan['browserTools'], plan['runId'], ar['path']])
    monitor = prep.original(plan['monitor'], 'genuine_nonredirect_original_owner')
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
            row = dict(schemaVersion=1, state='ROOT_NONREDIRECT_ACTION_ORIGINAL_OWNER_COMPLETED_UNREVIEWED_V1', arm=arm,
                rawExitCode=None if terminal is None else terminal['rawExitCode'], originalOwner=None if terminal is None else terminal['pid'],
                cleanOwner=clean, finalInputsPreserved=preserved, error=None if primary is None else dict(name=type(primary).__name__, message=str(primary)[:2048]),
                secondaryErrors=secondary, authority=ar, controller=self_ref, bindings=BINDINGS,
                terminal=prep.row(logs / 'terminal.json') if (logs / 'terminal.json').is_file() else None,
                constructorGuardBefore=before, constructorGuardAfter=after, fullOriginalContractExecuted=False, fullNextAccepted=False)
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
