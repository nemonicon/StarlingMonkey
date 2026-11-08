"""Bind fresh full-workload/CDP-observer inputs; never launch a host or browser."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ACTOR = BASE / 'next-rsc-stream-observer-runtime-v1'
CLIENT = BASE / 'next-rsc-stream-observer-full-client-v1'
BROWSER = BASE / 'next-rsc-stream-observer-browser-v1'
ACTOR_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-runtime-v1/index.json', 'sha256': '3e842fee88622001b8fbf7857cbe877150e4087cf037af565343504b0eab18f5', 'bytes': 2360}
CLIENT_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-full-client-v1/index.json', 'sha256': '46d58a120d81453f8eaea1695df33fa1df423e1790f8fa12572e40c060ba9029', 'bytes': 1112}
BROWSER_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-browser-v1/index.json', 'sha256': 'c4dc857fdebe9d6c84a278a8ef4d7b208f294749e77fa2c7b32faf250b0c272f', 'bytes': 1623}
CONTROLLER_UNBOUND = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/run-controls.py', 'sha256': 'c78e46b9f431a5237a992b08629c07600b45b17ed179f6bc3b3fa107f4f4e017', 'bytes': 33418}
APP_REVIEW = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/actual-build-review.json'),
    sha256='9106545f606ee30b2a3a05940d97233ce3b2e867e6abcdc5c5ec84efa09ad679', bytes=22847)
ASSET_SELECTION = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/asset-selection.json'),
    sha256='05c965a6b536af21c5947ccace5d9c1cc12b129c86a5b2df42e1bb95dd2c5b4c', bytes=7350)
FAILED_FULL = dict(path=str(BASE / 'next-fs-callback-no-compress-wasmcloud-root-results-v1/actual-runtime-review.json'),
    sha256='81a9c56b5c22c284149f971ae1e6ca9cdd4d8b72d8f22e4a5b107f4aa9d3041a', bytes=81083)
BODY_CONTROL = dict(path=str(BASE / 'next-rsc-browser-body-prework-root-results-v1/actualreview.json'),
    sha256='bc79b8111d58127d501a9aa6e592e81f71742f632cba5b8f2aeacbf7459b1e49', bytes=154007)
HOST_REQUIREMENTS = [
    dict(path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', sha256='2a2d660daf7f2a6e405fc6b885c996eca0ac71dd9f52d326e06d4d602ce9352c', bytes=367696),
    dict(path='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/node_modules/playwright-core/index.js', sha256='a58fb2cec4293e7dcf73c58a179898a4f3986666451a19da4e731fa3af63265b', bytes=697),
    dict(path='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/node_modules/playwright-core/index.mjs', sha256='3d36e2132d3c8b62397d23f0bb4177336aaee503203ae2a2c90fbeb5bf3317dd', bytes=1063),
    dict(path='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/node_modules/playwright-core/package.json', sha256='8aa1c9863fa8dea324e674254158cdc79440f4124ef2d84d38053013541cb7d6', bytes=876),
    dict(path='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/package-lock.json', sha256='f8dd9d403df7dc61de13badeefa22da1e639f5eb8117537a39fa864f9a37ba8f', bytes=714),
    dict(path='/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/package.json', sha256='7b241bd7c3c2a45f0484ccd799fd5f6fa6ce517d70278a7a92f26b7b2e882661', bytes=164),
]


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    assert all(type(r) is dict for r in (ACTOR_INDEX, CLIENT_INDEX, BROWSER_INDEX, CONTROLLER_UNBOUND)), 'Source review/seals pending; no helper read or mutation'
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
        (folder / 'index.json').write_text(json.dumps(index, indent=2) + '\n')
        ref = prep.row(folder / 'index.json')
        prep.family(ref)
        return ref

    for folder, label in ((ACTOR, 'actor'), (CLIENT, 'client'), (BROWSER, 'browser')):
        with (history / (label + '-index.unbound.json')).open('xb') as out:
            out.write((folder / 'index.json').read_bytes())

    def browser_bind(p):
        assert p['actualAssetBindingsPending'] is True
        assert p['requiredActionId'] is None and p['actualActionManifest'] is None
        p.update(actualAssetBindingsPending=False, applicationInputs=app['applicationInputs'],
            actualApplicationBuildReview=APP_REVIEW, actualAssetSelectionReview=ASSET_SELECTION,
            assetSelectionHtml=assets['clientHtml'], actionsAssetSelectionHtml=assets['actionsHtml'],
            assetPins=assets['assetPins'], actionsAssetPins=assets['actionsAssetPins'],
            requiredActionId=action_id, actualActionManifest=manifest_ref)

    browser_plan = bind_plan(BROWSER, 'plan.json', 'browser', browser_bind)
    browser_ref = reseal(BROWSER)
    worker = prep.row(BROWSER / 'browser-check.mjs')

    def client_bind(p):
        assert p['actualBrowserSourceBindingPending'] is True
        assert p['sourceRequirements']['browserWorker'] is None and p['sourceRequirements']['browserSourceIndex'] is None
        p['sourceRequirements'].update(browserWorker=worker, browserSourceIndex=browser_ref)
        p['actualBrowserSourceBindingPending'] = False

    client_plan = bind_plan(CLIENT, 'plan.json', 'client', client_bind)
    assert set(client_plan['sourceRequirements']) == {'manifestReader', 'supplemental', 'portableCacheCollector', 'fixtureContract', 'browserSourceIndex', 'browserWorker'}
    client_ref = reseal(CLIENT)
    plans, preimages = {}, {}
    for arm, name in (('cloud', 'plan.json'), ('stock', 'stock-plan.json')):
        p = json.loads((ACTOR / name).read_bytes())
        assert p['prospectiveFullClientBindingsPending'] is True and p['protectedInputs'] == [] and p['sourceFamilies'] == []
        preimages[arm] = copy.deepcopy(p)
        p.update(applicationInputs=app['applicationInputs'], applicationBuildResult=app['actualResult'], applicationBuildReview=APP_REVIEW,
            applicationRootIdentityEvidence=app['applicationRootIdentityEvidence'], applicationBuildSource=app['sourceIndex'],
            clientSource=prep.row(CLIENT / 'run-contracts.mjs'), clientSourceIndex=client_ref,
            browserSource=worker, browserSourceIndex=browser_ref, prospectiveFullClientBindingsPending=False,
            bindingState='READY_FULL_CLIENT_FULL_CONTRACT', outputPrefix='/private/tmp/starling-node-compat/next-rsc-stream-observer-' + arm + '-v1',
            runId='rsc-stream-observer-' + arm + '-first')
        p['fullClientFullContract'].update(clientSourcePending=False, requiredClientIndex=client_ref,
            requiredClient=prep.row(CLIENT / 'run-contracts.mjs'), assetSelection=ASSET_SELECTION,
            browserFamily=browser_ref, clientFamily=client_ref, requiredAssetSelection=ASSET_SELECTION,
            requiredBrowserFamily=browser_ref, requiredWorker=worker)
        p['namespacePolicy']['actualOutputPrefixAndRunIdPending'] = False
        p['requiredApplicationData'].update(applicationBuildReview=APP_REVIEW, applicationBuildResult=app['actualResult'],
            applicationInputs=app['applicationInputs'], applicationRootIdentityEvidence=app['applicationRootIdentityEvidence'], applicationRoot=str(root))
        if arm == 'cloud':
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
    for ref in HOST_REQUIREMENTS + [APP_REVIEW, ASSET_SELECTION, FAILED_FULL, BODY_CONTROL, manifest_ref,
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
    binding = dict(schemaVersion=1, state='ROOT_RSC_STREAM_OBSERVER_ACTUAL_BINDINGS_V1', actorIndex=actor_ref,
        clientIndex=client_ref, browserIndex=browser_ref, cloudPlan=prep.row(ACTOR / 'plan.json'), stockPlan=prep.row(ACTOR / 'stock-plan.json'),
        applicationBuildReview=APP_REVIEW, assetSelection=ASSET_SELECTION, actualActionManifest=manifest_ref, requiredActionId=action_id,
        originalFailedFullReview=FAILED_FULL, precedingBodyControlReview=BODY_CONTROL, protectedInputs=protected,
        innerConstructionReview=prep.row(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
        compositionReview=prep.row(BASE / 'next-standard-handler-observer-root-results-v1/actual-next-v3-composition-review.json'))
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
        state='ROOT_RSC_STREAM_OBSERVER_METADATA_BOUND_NOT_RUN_V1', bindings=binding_ref, generator=prep.row(Path(__file__).resolve()),
        controller=prep.row(controller), planInverses=changes, controllerOneLiteralInverseVerified=True,
        protectedInputCount=len(protected), genuineBuildReferences=len(state['buildRefs']), genuineSourceReferences=len(state['sourceRefs']),
        originalGuardBefore=before, oldProtectedArrayCopied=False, browserSelected=True, actorsInvoked=False, fullNextAccepted=False))))


if __name__ == '__main__':
    main()
