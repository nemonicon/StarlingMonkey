"""Prepare and run one pristine Node redirect-browser control, without retries."""
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
BINDINGS = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-pristine-redirect-root-results-v1/runtime-bindings.json', 'sha256': '3a26e8cff03ddcc5967b04112568afc48bcd18f129fe548c15ed705e0468355e', 'bytes': 17962}
PREPARER = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'),
    sha256='4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', bytes=19784)
INNER_AUTHORITY = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/diagnostic-next-construction-authority.json'),
    sha256='23313b9b1858e22df729b379c10750cd92ba00ce4aa9bee179fc21142fdfea66', bytes=5597386)
RUN_ID = 'pristine-current-first'
PUBLIC = dict(headerName='x-next-public-request-correlation',
    nonceByTest={'client-counter': '1' * 64, 'server-action': '2' * 64})
TRUE_FLAGS = ['hostOnlyDirectStandaloneAllowed', 'localhostServeAllowed', 'browserAllowed', 'publicRequestCorrelationAllowed']
FALSE_FLAGS = ['compilerAllowed', 'nativeBuildAllowed', 'engineAllowed', 'guestAllowed',
    'componentConstructionAllowed', 'packageInstallAllowed', 'applicationSourceMutationAllowed',
    'externalDeploymentAllowed', 'adoptionAllowed']


def context():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and type(BINDINGS) is dict, 'Unbound Source refuses helper import or action'
    path = Path(PREPARER['path'])
    raw = path.read_bytes()
    assert path.resolve() == path and not path.is_symlink() and path.stat().st_nlink == 1
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (PREPARER['sha256'], PREPARER['bytes'])
    spec = importlib.util.spec_from_file_location('genuine_pristine_redirect_source_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    b = prep.document(BINDINGS)
    assert b['state'] == 'ROOT_CURRENT_PRISTINE_REDIRECT_ACTUAL_BINDINGS_V1'
    actor_root = BASE / 'next-pristine-redirect-runtime-v1'
    browser_root = BASE / 'next-pristine-redirect-browser-v1'
    assert b['actorIndex']['path'] == str(actor_root / 'index.json')
    assert b['browserIndex']['path'] == str(browser_root / 'index.json')
    actor_index, browser_index = prep.family(b['actorIndex']), prep.family(b['browserIndex'])
    assert b['actorPlan']['path'] == str(actor_root / 'plan.json')
    assert any(dict(r, path=str(actor_root / r['path'])) == b['actorPlan'] for r in actor_index['files'])
    plan = prep.document(b['actorPlan'])
    for role, name in [('clientSource', 'run-browser.mjs'), ('browserWorker', 'browser-check.mjs')]:
        assert plan[role]['path'] == str(browser_root / name)
        assert any(dict(r, path=str(browser_root / r['path'])) == plan[role] for r in browser_index['files'])
    assert plan['clientSourceIndex'] == b['browserIndex'] and plan['browserIndex'] == b['browserIndex']
    app = prep.document(b['applicationBuildReview'])
    assert app['state'] == 'COORDINATED_NONREDIRECT_ACTION_APP_BUILD_DATA_REVIEW_PASSED_V1' and app['verifiedPassed'] is True
    assert plan['applicationBuildReview'] == b['applicationBuildReview']
    assert plan['applicationInputs'] == app['applicationInputs'] and plan['applicationBuildResult'] == app['actualResult']
    assert plan['applicationRootIdentityEvidence'] == app['applicationRootIdentityEvidence']
    assert plan['applicationSource'] == app['applicationRoot']
    assert plan['outerSeconds'] == 600 and plan['minimumLaunchFreeBytes'] == 1073741824
    prefix = Path(plan['outputPrefix'])
    assert prefix.parent == Path('/private/tmp/starling-node-compat') and prefix.resolve() == prefix
    assert plan['runId'] == RUN_ID
    self_ref = prep.row(Path(__file__).resolve())

    def protect():
        for ref in [PREPARER, INNER_AUTHORITY, BINDINGS, self_ref]:
            prep.checked(ref)
        prep.family(b['actorIndex'])
        prep.family(b['browserIndex'])
        for ref in b['protectedInputs'] + plan['protectedInputs']:
            prep.checked(ref)
        for ref in plan['sourceFamilies']:
            prep.family(ref)

    protect()
    original = prep.document(INNER_AUTHORITY)
    before = prep.admit(original)
    return prep, b, plan, self_ref, protect, original, before


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare', action='store_true')
    modes.add_argument('--run', action='store_true')
    args = parser.parse_args()
    prep, b, plan, self_ref, protect, original, before = context()
    assert shutil.disk_usage('/private/tmp').free >= plan['minimumLaunchFreeBytes']
    output = Path(plan['outputPrefix'] + '-' + RUN_ID)
    logs = Path(str(output) + '-external-root')
    authority_path, preparation, receipt = HERE / 'authority.json', HERE / 'preparation.json', HERE / 'owner-result.json'
    for path in (output, logs):
        assert path.resolve() == path and not path.exists() and not path.is_symlink()
    authority = dict(schemaVersion=1, state='ROOT_NEXT_PRISTINE_REDIRECT_BROWSER_CONTROL_AUTHORIZED_V1',
        runId=RUN_ID, sourceIndex=b['actorIndex'], plan=b['actorPlan'], publicRequestCorrelation=PUBLIC,
        **{k: True for k in TRUE_FLAGS}, **{k: False for k in FALSE_FLAGS})
    if args.prepare:
        assert all(not p.exists() and not p.is_symlink() for p in (authority_path, preparation, receipt))
        ar = prep.save(authority_path, authority)
        prep.admit(original)
        protect()
        prep.save(preparation, dict(schemaVersion=1, state='ROOT_PRISTINE_REDIRECT_PREPARED_NOT_RUN_V1',
            controller=self_ref, bindings=BINDINGS, authority=ar, constructorGuardBefore=before,
            outputRoot=str(output), ownerOutputRoot=str(logs), originalOwnerSeconds=600,
            actorInvoked=False, automaticRetry=False, replacementTrials=False,
            oldFailuresWaived=False, fullOriginalContractExecuted=False, fullNextAccepted=False))
        print(json.dumps(dict(prepared=prep.row(preparation), actorInvoked=False)))
        return 0
    ar, pr = prep.row(authority_path), prep.row(preparation)
    assert prep.document(ar) == authority
    p = prep.document(pr)
    assert p['state'] == 'ROOT_PRISTINE_REDIRECT_PREPARED_NOT_RUN_V1'
    assert p['controller'] == self_ref and p['bindings'] == BINDINGS and p['authority'] == ar
    assert p['outputRoot'] == str(output) and p['ownerOutputRoot'] == str(logs) and p['originalOwnerSeconds'] == 600
    assert p['actorInvoked'] is False and not receipt.exists() and not receipt.is_symlink()
    protect()
    monitor = prep.original(plan['monitor'], 'genuine_pristine_redirect_original_owner')
    node = plan['node']
    env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
    env.update(PATH=str(Path(node['path']).parent) + ':/usr/bin:/bin', LANG='C', LC_ALL='C', NODE_ENV='production', NEXT_TELEMETRY_DISABLED='1', CI='1')
    logs.mkdir(mode=0o700)
    terminal, primary, after, preserved = None, None, None, False
    secondary = []
    try:
        terminal = monitor.monitor([node['path'], str(Path(b['actorIndex']['path']).parent / 'control.mjs'), ar['path']],
            plan['cwd'], env, logs, 600, ar)
    except BaseException as error:
        primary = error
    finally:
        try:
            after = prep.admit(original)
            protect()
            prep.checked(ar)
            prep.checked(pr)
            preserved = True
        except BaseException as error:
            if primary is None:
                primary = error
            else:
                secondary.append(dict(name=type(error).__name__, message=str(error)[:2048]))
        clean = terminal is not None and not terminal['timeout'] and not terminal['forcedCleanup'] and terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone'] and all(not terminal[k] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
        try:
            record = dict(schemaVersion=1, state='ROOT_PRISTINE_REDIRECT_OWNER_COMPLETED_UNREVIEWED_V1',
                rawExitCode=None if terminal is None else terminal['rawExitCode'], originalOwner=None if terminal is None else terminal['pid'],
                cleanOwner=clean, finalInputsPreserved=preserved, error=None if primary is None else dict(name=type(primary).__name__, message=str(primary)[:2048]),
                secondaryErrors=secondary, authority=ar, preparation=pr, bindings=BINDINGS, controller=self_ref,
                terminal=prep.row(logs / 'terminal.json') if (logs / 'terminal.json').is_file() else None,
                constructorGuardBefore=before, constructorGuardAfter=after,
                fullOriginalContractExecuted=False, fullNextAccepted=False)
            rr = prep.save(receipt, record)
            print(json.dumps(dict(receipt=rr, rawExitCode=record['rawExitCode'], cleanOwner=clean)))
        except BaseException:
            if primary is not None:
                raise primary
            raise
    if primary is not None:
        raise primary
    return 0 if clean and preserved and terminal['rawExitCode'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
