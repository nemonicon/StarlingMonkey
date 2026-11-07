"""Prepare exactly one stock Node control with the existing matched-host wire."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def row(path):
    path = Path(path)
    assert path.is_absolute() and path.resolve() == path and not path.is_symlink()
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    actor = BASE / 'next-portable-cache-stock-candidate-v1'
    plan = json.loads((actor / 'plans.json').read_text())
    app_ref = row(BASE / 'next-portable-cache-app-build-root-results-v1/actual-build-review-v2.json')
    assert app_ref['sha256'] == '163133f1db2d8957bfeb871a26de3c5b3f588ef303c18ae27336120ee19941e2'
    app = json.loads(Path(app_ref['path']).read_text())
    assert app['verifiedPassed'] is True and app['sourceFiles'] == 31
    assert app['state'] == 'PORTABLE_CACHE_APP_HOST_BUILD_DATA_REVIEW_PASSED_V1'
    assert plan['applicationBuildReview'] == app_ref
    helper = plan['sharedPortableCacheCollectorSourceIndex']
    assert helper == row(Path(helper['path']))
    assert helper['sha256'] == 'a7b401d505ab5a679a1b09c14471053a332d99c27f08dd1e965e852ad63b731d'
    assert plan['arms']['stock']['timeoutSeconds'] == 300
    for ref in plan['protectedInputs']:
        assert row(Path(ref['path'])) == ref
    run_id = 'portable-cache-stock-first'
    output = Path(plan['outputPrefix'] + '-' + run_id)
    monitor = Path(str(output) + '-monitor')
    assert not output.exists() and not output.is_symlink()
    assert not monitor.exists() and not monitor.is_symlink()
    authority = dict(schemaVersion=1, state='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1',
        arm='stock', runId=run_id, sourceIndex=row(actor / 'index.json'),
        plans=row(actor / 'plans.json'), localhostServerAllowed=True, browserAllowed=True,
        compilerAllowed=False, nativeBuildAllowed=False, guestAllowed=False,
        engineAllowed=False, externalApplicationDeploymentAllowed=False,
        applicationBuildDataReview=app_ref,
        rootReview='One first stock Node22.14 control on genuine new2186-file app and shared fixed-five '
        'nonce collector, same normal browser/assertions and all24/cachegen/stream/strict2/supp6 '
        'gates. Original300-second owner and private fresh output; no retry, filtering, '
        'cohort extension, compiler, native engine, guest or production permission.')
    target = HERE / 'stock-first-runtime-authority.json'
    with target.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    receipt = dict(state='ROOT_PORTABLE_CACHE_STOCK_CONTROL_PREPARED_NOT_LAUNCHED_V1',
        authority=row(target), appBuildReview=app_ref, sharedCollector=helper,
        originalOwnerSeconds=300, actorInvoked=False)
    with (HERE / 'runtime-preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
