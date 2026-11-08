"""Bind one stock wasmCloud full-profile Source closure; no host/client launch."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ACTOR = BASE / 'next-fs-callback-no-compress-wasmcloud-v1'
CLIENT = BASE / 'next-fs-callback-no-compress-wasmcloud-client-v1'
ACTOR_INDEX = None
CLIENT_INDEX = None
CONTROLLER_UNBOUND = None
APP_REVIEW = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/actual-build-review.json'),
    sha256='9106545f606ee30b2a3a05940d97233ce3b2e867e6abcdc5c5ec84efa09ad679', bytes=22847)
ASSET_SELECTION = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/asset-selection.json'),
    sha256='05c965a6b536af21c5947ccace5d9c1cc12b129c86a5b2df42e1bb95dd2c5b4c', bytes=7350)
APP_INDEX = dict(path=str(BASE / 'next-fs-callback-no-compress-app-build-v1/index.json'),
    sha256='5c280e4ba8f6a9eb8b27e9af41e293f22e082f1b3f17b44114019de5efec1422', bytes=6994)
BROWSER_INDEX = dict(path=str(BASE / 'next-fs-callback-no-compress-browser-v1/index.json'),
    sha256='83071f52e7106755164d7880fda21f50afdacfed323e1b01d5275be6d52a6863', bytes=839)
INNER_REVIEW = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
    sha256='5c284564e0ddefba507c5429acd98c42393d5c0f2764105a4046f0665f51e16a', bytes=22550)
COMPOSITION_REVIEW = dict(path=str(BASE / 'next-standard-handler-observer-root-results-v1/actual-next-v3-composition-review.json'),
    sha256='b333fbc736e653f0a56bbe7ee031b3b943faf3e4d2ea687112659465171e2387', bytes=33472)
PRIOR_FULL_REVIEW = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/actual-runtime-review.json'),
    sha256='e19aaa2dc4fb028836265597ec9dcbe3942b9ee194b076f602b27717cd157c89', bytes=129557)
HOST_REQUIREMENTS = [
    dict(path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        sha256='2a2d660daf7f2a6e405fc6b885c996eca0ac71dd9f52d326e06d4d602ce9352c', bytes=367696),
    dict(path='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/node_modules/playwright-core/index.js',
        sha256='a58fb2cec4293e7dcf73c58a179898a4f3986666451a19da4e731fa3af63265b', bytes=697),
    dict(path='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/node_modules/playwright-core/index.mjs',
        sha256='3d36e2132d3c8b62397d23f0bb4177336aaee503203ae2a2c90fbeb5bf3317dd', bytes=1063),
    dict(path='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/node_modules/playwright-core/package.json',
        sha256='8aa1c9863fa8dea324e674254158cdc79440f4124ef2d84d38053013541cb7d6', bytes=876),
    dict(path='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/package-lock.json',
        sha256='f8dd9d403df7dc61de13badeefa22da1e639f5eb8117537a39fa864f9a37ba8f', bytes=714),
    dict(path='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/package.json',
        sha256='7b241bd7c3c2a45f0484ccd799fd5f6fa6ce517d70278a7a92f26b7b2e882661', bytes=164),
]


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    assert all(type(r) is dict for r in (ACTOR_INDEX, CLIENT_INDEX, CONTROLLER_UNBOUND)), 'Unbound Source: no helper read or mutation'
    path = BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'
    raw = path.read_bytes()
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (
        '4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', 19784)
    spec = importlib.util.spec_from_file_location('genuine_no_compress_cloud_binding_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    state = prep.context()
    original = prep.document(prep.row(path.parent / 'diagnostic-next-construction-authority.json'))
    assert prep.authority(state) == original
    before = prep.admit(original)
    actor_index = prep.family(ACTOR_INDEX)
    prep.family(CLIENT_INDEX)
    assert ACTOR_INDEX['path'] == str(ACTOR / 'index.json')
    assert CLIENT_INDEX['path'] == str(CLIENT / 'index.json')
    assert CONTROLLER_UNBOUND['path'] == str(HERE / 'run-control.py')
    prep.checked(CONTROLLER_UNBOUND)
    prep.family(APP_INDEX)
    browser_index = prep.family(BROWSER_INDEX)
    worker = prep.row(Path(BROWSER_INDEX['path']).with_name('browser-check.mjs'))
    assert worker['sha256'] == '01caabc8dae9f684d7e7c9f70b413223811fd06fba3be546ce733c153d37072b'
    assert any(dict(m, path=str(Path(BROWSER_INDEX['path']).parent / m['path'])) == worker for m in browser_index['files'])
    app, assets = prep.document(APP_REVIEW), prep.document(ASSET_SELECTION)
    assert app['state'] == 'COORDINATED_FS_CALLBACK_NO_COMPRESS_APP_BUILD_DATA_REVIEW_PASSED_V1'
    assert app['buildVersion'] == 1 and app['sourceIndex'] == APP_INDEX
    for key in ('verifiedPassed', 'verifiedDataReviewPassed', 'sourceCacheAbsent',
            'runtimeCacheMountPolicyCompatible', 'configuredCompressFalseVerified',
            'effectiveStandaloneConfigCompressFalseVerified'):
        assert app[key] is True
    prior = prep.document(PRIOR_FULL_REVIEW)
    assert all(prior[k] is True for k in ('verifiedPassed', 'verifiedDataReviewPassed',
        'nativeFullContractPassed', 'stockFullContractPassed', 'allFullContractsPassed'))
    assert prior['fullNextAccepted'] is False
    inventory = prep.document(app['applicationInputs'])
    root = Path(app['applicationRoot'])
    assert root.is_absolute() and root.resolve() == root and not root.is_symlink()
    assert str(root) == inventory['root'] and inventory['schemaVersion'] == 1
    files, directories = inventory['files'], inventory['directories']
    assert type(files) is list and type(directories) is list and inventory['symlinks'] == []
    for rows in (files, directories):
        assert len({r['path'] for r in rows}) == len(rows)
        for r in rows:
            p = Path(r['path'])
            assert not p.is_absolute() and p.parts and all(x not in ('', '.', '..') for x in p.parts)
            assert p.as_posix() == r['path']
            assert r['path'] != '.next/cache' and not r['path'].startswith('.next/cache/')
    assert '.next' in {r['path'] for r in directories}
    assert not {r['path'] for r in files} & {r['path'] for r in directories}
    count, size, dirs = len(files), sum(r['bytes'] for r in files), len(directories)
    assert count > 0 and count == inventory['regularFiles'] and size == inventory['bytes']
    assert all(type(r['bytes']) is int and r['bytes'] >= 0 for r in files)
    try:
        (root / '.next/cache').lstat()
    except FileNotFoundError:
        pass
    else:
        raise AssertionError('Source cache must be absent, without artifact filtering')
    st = root.stat()
    identity = dict(dev=st.st_dev, ino=st.st_ino, mode=st.st_mode & 0o777, nlink=st.st_nlink)
    evidence = prep.document(app['applicationRootIdentityEvidence'])['rootIdentity']
    assert all(identity[k] == evidence[k] for k in identity)
    assert assets['state'] == 'FS_CALLBACK_NO_COMPRESS_MODERN_BROWSER_ASSET_SELECTION_DATA_REVIEW_PASSED_V1'
    assert assets['verifiedPassed'] is True
    for key, value in [('applicationBuildReview', APP_REVIEW), ('actualBuildResult', app['actualResult']),
            ('applicationInputs', app['applicationInputs']), ('applicationRootIdentityEvidence', app['applicationRootIdentityEvidence']),
            ('applicationRoot', str(root))]:
        assert assets[key] == value
    assert all(assets[k] is True for k in ('actionsScriptsAreExactClientSubset',
        'allSelectedAndExcludedScriptsInventoryAndPhysicalHashVerified', 'currentSelectedFileAndRootBookendsStable'))
    browser_plan = prep.document(prep.row(Path(BROWSER_INDEX['path']).with_name('plan.json')))
    assert browser_plan['actualAssetBindingsPending'] is False
    assert browser_plan['actualApplicationBuildReview'] == APP_REVIEW
    assert browser_plan['actualAssetSelectionReview'] == ASSET_SELECTION
    assert browser_plan['applicationInputs'] == app['applicationInputs']
    assert browser_plan['assetSelectionHtml'] == assets['clientHtml']
    assert browser_plan['actionsAssetSelectionHtml'] == assets['actionsHtml']
    assert browser_plan['assetPins'] == assets['assetPins'] and browser_plan['actionsAssetPins'] == assets['actionsAssetPins']
    client_plan = prep.document(prep.row(CLIENT / 'plan.json'))
    assert client_plan['suite'] == 'NEXT_FS_NO_COMPRESS_WASMCLOUD_FULL_CONTRACT_CLIENT_V1'
    assert client_plan['controlOnly'] is False and client_plan['actualBrowserSourceBindingPending'] is False
    requirements = client_plan['sourceRequirements']
    assert set(requirements) == {'manifestReader', 'supplemental', 'portableCacheCollector',
        'fixtureContract', 'browserSourceIndex', 'browserWorker'}
    assert requirements['browserSourceIndex'] == BROWSER_INDEX and requirements['browserWorker'] == worker
    assert client_plan['newApplicationContract']['actualApplicationBuildReview'] == APP_REVIEW
    cloud_output = '/private/tmp/starling-node-compat/next-fs-callback-no-compress-wasmcloud-v1'
    run_id = 'fs-no-compress-wasmcloud-first'
    assert client_plan['allowedOutputPolicies'] == [dict(runId=run_id, output=cloud_output + '-' + run_id + '/client')]
    plan_path = ACTOR / 'plan.json'
    plan_raw = plan_path.read_bytes()
    old = json.loads(plan_raw)
    assert old['protectedInputs'] == [] and old['sourceFamilies'] == []
    assert old['prospectiveFsCallbackAppBindingsPending'] is True
    assert old['fsCallbackFullControl']['fullClientSourcePending'] is True
    assert old['requiredPrerequisites']['applicationBuildReview'] == APP_REVIEW
    assert old['requiredPrerequisites']['assetSelection'] == ASSET_SELECTION
    assert old['requiredPrerequisites']['innerConstructionReview'] == INNER_REVIEW
    assert old['requiredPrerequisites']['compositionReview'] == COMPOSITION_REVIEW
    plan = copy.deepcopy(old)
    plan.update(applicationInputs=app['applicationInputs'], applicationBuildResult=app['actualResult'],
        applicationBuildReview=APP_REVIEW, applicationRootIdentityEvidence=app['applicationRootIdentityEvidence'],
        applicationBuildSource=APP_INDEX, applicationSource=str(root),
        applicationBuildOutputRoot=str(Path(app['actualResult']['path']).parent),
        applicationRootIdentity=identity,
        applicationSchema=dict(name='fresh-next-standalone-root-excluded-v1', sourceDirectoriesExcludeRoot=True,
            files=count, bytes=size, directoriesExcludingRoot=dirs, ownedDirectoriesIncludingRoot=dirs + 1,
            additionalDirectories=[]), clientSource=prep.row(CLIENT / 'run-contracts.mjs'),
        clientSourceIndex=CLIENT_INDEX, browserSource=worker, browserSourceIndex=BROWSER_INDEX,
        bindingState='READY_FS_CALLBACK_FULL_CONTRACT', prospectiveFsCallbackAppBindingsPending=False,
        outputPrefix=cloud_output, runId=run_id)
    plan['requiredApplicationData'].update(applicationBuildReview=APP_REVIEW,
        applicationBuildResult=app['actualResult'], applicationInputs=app['applicationInputs'],
        applicationRootIdentityEvidence=app['applicationRootIdentityEvidence'], applicationRoot=str(root))
    plan['fsCallbackFullControl'].update(assetSelection=ASSET_SELECTION, browserFamily=BROWSER_INDEX,
        clientFamily=CLIENT_INDEX, requiredFullClientIndex=CLIENT_INDEX,
        requiredFullClient=plan['clientSource'], fullClientSourcePending=False,
        requiredAssetSelection=ASSET_SELECTION, requiredBrowserFamily=BROWSER_INDEX, requiredWorker=worker)
    plan['namespacePolicy']['actualOutputPrefixAndRunIdPending'] = False
    assert plan['namespacePolicy']['plannedOutputPrefix'] == cloud_output
    assert plan['namespacePolicy']['plannedRunId'] == run_id
    assert plan['selfOrigin'] is None, 'Origin is issued later by Root, only in authority'
    refs = {}

    def add(ref):
        prep.checked(ref)
        if ref['path'] in refs:
            assert refs[ref['path']] == ref
        refs[ref['path']] = ref

    def descriptors(value):
        if type(value) is dict:
            if set(value) == {'path', 'sha256', 'bytes'}:
                assert Path(value['path']).is_absolute(), 'Relative/URL role requires explicit selection'
                add(value)
            else:
                for key, item in value.items():
                    if key not in ('fixedWit', 'protectedInputs', 'sourceFamilies'):
                        descriptors(item)
        elif type(value) is list:
            for item in value:
                descriptors(item)

    for ref in state['buildRefs'] + state['sourceRefs'] + [prep.ENGINE, prep.NATIVE_METADATA]:
        add(ref)
    donor = prep.document(prep.row(BASE / 'next-nonredirect-action-runtime-v2/plan.json'))
    assert donor['sourceFamilies'][-2:] == [
        prep.row(BASE / 'next-nonredirect-action-app-build-v2/index.json'),
        prep.row(BASE / 'next-nonredirect-action-browser-v2/index.json')]
    families = donor['sourceFamilies'][:-2] + [APP_INDEX, BROWSER_INDEX, CLIENT_INDEX]
    for family in families:
        index = prep.family(family)
        add(family)
        for member in index['files']:
            add(dict(member, path=str(Path(family['path']).parent / member['path'])))
    for ref in requirements.values():
        add(ref)
    # Actor plan/index are the only mutable members; all other Source stays exact.
    for member in actor_index['files']:
        if member['path'] != 'plan.json':
            add(dict(member, path=str(ACTOR / member['path'])))
    descriptors(plan)
    for member in plan['fixedWit']['files']:
        add(dict(member, path=str(Path(plan['fixedWit']['sourceDirectory']) / member['path'])))
    assert len(plan['fixedWit']['files']) == 8 and len(HOST_REQUIREMENTS) == 6
    for ref in HOST_REQUIREMENTS:
        add(ref)
    for ref in [APP_REVIEW, ASSET_SELECTION, app['actualResult'], app['actualOwnerResult'],
            app['applicationInputs'], app['applicationRootIdentityEvidence'], INNER_REVIEW,
            COMPOSITION_REVIEW, PRIOR_FULL_REVIEW]:
        add(ref)
    add(prep.row(HERE / 'host-preflight.json'))
    for key in ('clientHtml', 'actionsHtml'):
        add(assets[key])
    physical = set()
    for pin in assets['assetPins']:
        assert set(pin) == {'path', 'sha256', 'bytes'}
        assert pin['path'].startswith('/_next/static/') and pin['path'].endswith('.js') and '..' not in pin['path']
        rel = '.next/' + pin['path'][len('/_next/'):]
        member = next(r for r in files if r['path'] == rel)
        assert (pin['sha256'], pin['bytes']) == (member['sha256'], member['bytes'])
        physical.add(rel)
    for selection in assets['htmlSelections'].values():
        for url in selection['excludedNoModule']:
            assert url.startswith('/_next/static/') and url.endswith('.js') and '..' not in url
            physical.add('.next/' + url[len('/_next/'):])
    physical.update({'.next/required-server-files.json', 'server.js'})
    for rel in sorted(physical):
        member = next(r for r in files if r['path'] == rel)
        add(dict(path=str(root / rel), sha256=member['sha256'], bytes=member['bytes']))
    config = prep.document(prep.row(root / '.next/required-server-files.json'))['config']
    assert config['compress'] is False and config['outputFileTracingExcludes'] == {'/api/cache': ['./.next/cache/**']}
    plan['sourceFamilies'] = families
    plan['protectedInputs'] = sorted(refs.values(), key=lambda r: r['path'])
    changed = sorted(k for k in set(old) | set(plan) if old.get(k) != plan.get(k))
    inverse = copy.deepcopy(plan)
    for key in changed:
        if key in old:
            inverse[key] = old[key]
        else:
            del inverse[key]
    assert inverse == old
    history = HERE / 'source-history/runtime-binding-v1'
    history.mkdir(parents=True)
    for filename, data in [('actor-index.unbound.json', Path(ACTOR_INDEX['path']).read_bytes()),
            ('plan.unbound.json', plan_raw), ('run-control.unbound.py', prep.checked(CONTROLLER_UNBOUND).read_bytes())]:
        with (history / filename).open('xb') as out:
            out.write(data)
    assert (history / 'plan.unbound.json').read_bytes() == plan_raw
    plan_path.write_text(json.dumps(plan, indent=2) + '\n')
    sealed = copy.deepcopy(actor_index)
    for member in sealed['files']:
        actual = prep.row(ACTOR / member['path'])
        member.update(sha256=actual['sha256'], bytes=actual['bytes'])
    Path(ACTOR_INDEX['path']).write_text(json.dumps(sealed, indent=2) + '\n')
    actor_ref = prep.row(Path(ACTOR_INDEX['path']))
    prep.family(actor_ref)
    binding = dict(schemaVersion=1, state='ROOT_FS_NO_COMPRESS_WASMCLOUD_ACTUAL_BINDINGS_V1',
        actorIndex=actor_ref, plan=prep.row(plan_path), clientIndex=CLIENT_INDEX, browserIndex=BROWSER_INDEX,
        applicationBuildReview=APP_REVIEW, assetSelection=ASSET_SELECTION,
        innerConstructionReview=INNER_REVIEW, compositionReview=COMPOSITION_REVIEW,
        priorWasmtimeNodeProfileReview=PRIOR_FULL_REVIEW, protectedInputs=plan['protectedInputs'])
    binding_ref = prep.save(HERE / 'runtime-bindings.json', binding)
    controller = HERE / 'run-control.py'
    unbound = (history / 'run-control.unbound.py').read_bytes()
    needle = b'BINDINGS = None'
    replacement = ('BINDINGS = ' + repr(binding_ref)).encode()
    assert unbound.count(needle) == 1
    bound = unbound.replace(needle, replacement)
    assert bound.replace(replacement, needle) == unbound
    controller.write_bytes(bound)
    for ref in plan['protectedInputs']:
        prep.checked(ref)
    for ref in (actor_ref, CLIENT_INDEX, BROWSER_INDEX):
        prep.family(ref)
    after = prep.admit(original)
    assert before == after
    receipt = dict(schemaVersion=1, state='ROOT_FS_NO_COMPRESS_WASMCLOUD_BOUND_NOT_RUN_V1',
        bindings=binding_ref, generator=prep.row(Path(__file__).resolve()), controller=prep.row(controller),
        sourceController=CONTROLLER_UNBOUND, planPreimage=prep.row(history / 'plan.unbound.json'),
        planChangedKeys=changed, exactSemanticInverseVerified=True, originalPlanBytesPreserved=True,
        controllerOneLiteralByteInverseVerified=True, protectedInputCount=len(plan['protectedInputs']),
        genuineBuildReferences=len(state['buildRefs']), genuineSourceReferences=len(state['sourceRefs']),
        originalConstructorGuardBefore=before, originalConstructorGuardAfter=after,
        sourceCacheAbsent=True, actorInvoked=False, originSelected=False, oldProtectedArrayReused=False,
        fullNextAccepted=False)
    print(json.dumps(prep.save(HERE / 'source-bindings.json', receipt)))


if __name__ == '__main__':
    main()
