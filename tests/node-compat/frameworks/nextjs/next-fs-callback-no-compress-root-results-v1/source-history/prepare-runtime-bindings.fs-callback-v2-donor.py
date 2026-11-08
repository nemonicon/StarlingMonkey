"""Root-only one-shot FS-callback V2 metadata binding; no actor or tool launch.

Derives the genuine current-full prepare-bindings-v2 mechanism. The new browser,
full client and runtime families are bound in that order, without index cycles.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ACTOR = BASE / 'next-fs-callback-runtime-v1'
BROWSER = BASE / 'next-fs-callback-browser-v1'
CLIENT = BASE / 'next-fs-callback-full-client-v1'
APP_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-fs-callback-root-results-v2/actual-build-review.json', 'sha256': '4a6f03cefbed841af163f62f2ef4cc226a025d84379c7cb7f2a33a541e0b147c', 'bytes': 18599}
ASSET_SELECTION = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-fs-callback-root-results-v2/asset-selection.json', 'sha256': '257e18684b90a46afdb117165b3209ef6899e1e8c2a7e8fee41e06030309b621', 'bytes': 6964}
APP_SOURCE_INDEX = dict(path=str(BASE / 'next-fs-callback-app-build-v2/index.json'),
    sha256='f62aa5cb40f91795c5d98f1fea5cac3ce50d8d4a8767033b46b2439c7aadea93', bytes=6834)
BROWSER_FILES = ['README.md', 'browser-check.mjs', 'manifest.mjs', 'plan.json', 'run-browser.mjs']
CLIENT_FILES = ['README.md', 'client.patch', 'plan.json', 'run-contracts.mjs']
ACTOR_FILES = ['app-policy.mjs', 'capture-stdout.mjs', 'deploy.mjs', 'plan.json',
    'public-correlation.mjs', 'run-stock.mjs', 'stock-plan.json']
UNBOUND_SOURCE_FILES = {'next-fs-callback-browser-v1': [('README.md',
                                  '318437a6fa9fe74fb34787921a536b183f87f1f4cef816b380b7bfcd8b28c32c',
                                  1234),
                                 ('browser-check.mjs',
                                  '01caabc8dae9f684d7e7c9f70b413223811fd06fba3be546ce733c153d37072b',
                                  32170),
                                 ('manifest.mjs',
                                  'c495c2c6dcb23eec800bcb090da8f765994a645a35596f8ddf144b0527b0921f',
                                  3886),
                                 ('plan.json',
                                  '60a5d0257394fb4a743668a7cf2855f60bfed742d803013523d72a05d2a3a999',
                                  3057),
                                 ('run-browser.mjs',
                                  'de868ee6c24d1d339ecbc39d2e5f959f58d1c46e1548224a1505ebc5e1e2cde0',
                                  3560)],
 'next-fs-callback-full-client-v1': [('README.md',
                                      '0838acd323d59be980b9bc06b6fa4a1289a2133b1d8ea60eb3cc49b0d02816df',
                                      1904),
                                     ('client.patch',
                                      '82639b5286849f8c36ddb3c58067e025ac0c983fb6032b2d7f3bde0e61e7a5f6',
                                      4145),
                                     ('plan.json',
                                      'a0dbc7730293a5cab364c2b1d517156b11e3b56af2562a202d669e64fd9bffd8',
                                      3925),
                                     ('run-contracts.mjs',
                                      '18907bb15074455236c343b904d4de0af5030a66b4bb7009e5d596706ed8c53d',
                                      9606)],
 'next-fs-callback-runtime-v1': [('app-policy.mjs',
                                  'd835be43d9e048785a7cbc5bffbacced646f1ac52847079d7fc9798822f585dc',
                                  2759),
                                 ('capture-stdout.mjs',
                                  'bedbbf2146373c0b9f2e65b81454a4d9d4db26e1c259eb4617496d7033218781',
                                  5050),
                                 ('deploy.mjs',
                                  '2aeb6a4e35096b68a22236827472026ab90b392c2b6ac828a46b33daa1ce77cf',
                                  31279),
                                 ('plan.json',
                                  'ddade21e3639624b1f9d41c28d9eac9bc7f6c9c4b23095616b97b916c9c9991a',
                                  14658),
                                 ('public-correlation.mjs',
                                  'bd9ce823c8c1bd38feb58dd8eb205b2216387cee9aeb29fea82fb18e43ce24f2',
                                  2300),
                                 ('run-stock.mjs',
                                  '33c988cf1508667eb8d9abd4cf75754c807a23ba8aef42d085a2ece3c8882379',
                                  18937),
                                 ('stock-plan.json',
                                  'c0a74acad0998774ab1c19b33f3b10cbc1ba802ee3523d0c119ea269cc4286f8',
                                  5105)]}
CONTROLLER_UNBOUND = dict(path=str(HERE / 'run-controls.py'),
    sha256='ee03309d3f8709c31d072c2fcd6e99e47d86ddaf171c97215a76c32c2399d22b', bytes=19838)
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
    # First operation: no preparer read/import, DATA output or mutation unbound.
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    assert type(APP_REVIEW) is dict and type(ASSET_SELECTION) is dict, 'Unbound actual app/asset DATA'
    path = BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'
    raw = path.read_bytes()
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (
        '4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', 19784)
    spec = importlib.util.spec_from_file_location('genuine_fs_callback_binding_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    state = prep.context()
    for folder, members in UNBOUND_SOURCE_FILES.items():
        for name, sha256, size in members:
            prep.checked(dict(path=str(BASE / folder / name), sha256=sha256, bytes=size))
    prep.checked(CONTROLLER_UNBOUND)
    original = prep.document(prep.row(path.parent / 'diagnostic-next-construction-authority.json'))
    assert prep.authority(state) == original
    before = prep.admit(original)
    app_ref, assets_ref = APP_REVIEW, ASSET_SELECTION
    app, assets = prep.document(app_ref), prep.document(assets_ref)
    assert app['state'] == 'COORDINATED_FS_CALLBACK_APP_BUILD_DATA_REVIEW_PASSED_V1'
    for key in ('verifiedPassed', 'verifiedDataReviewPassed', 'sourceCacheAbsent', 'runtimeCacheMountPolicyCompatible'):
        assert app[key] is True
    assert app['buildVersion'] == 2 and app['sourceIndex'] == APP_SOURCE_INDEX
    prep.family(APP_SOURCE_INDEX)
    inventory = prep.document(app['applicationInputs'])
    app_root = Path(app['applicationRoot'])
    assert app_root.is_absolute() and app_root.resolve() == app_root and not app_root.is_symlink()
    assert str(app_root) == inventory['root'] and inventory['schemaVersion'] == 1
    files, directories = inventory['files'], inventory['directories']
    assert type(files) is list and type(directories) is list and inventory['symlinks'] == []
    for rows in (files, directories):
        assert len({r['path'] for r in rows}) == len(rows)
        for row in rows:
            p = Path(row['path'])
            assert not p.is_absolute() and p.parts and all(x not in ('', '.', '..') for x in p.parts)
            assert p.as_posix() == row['path']
            assert row['path'] != '.next/cache' and not row['path'].startswith('.next/cache/')
    assert '.next' in {r['path'] for r in directories}
    assert not {r['path'] for r in files} & {r['path'] for r in directories}
    file_count, byte_count, directory_count = len(files), sum(r['bytes'] for r in files), len(directories)
    assert file_count > 0 and type(inventory['regularFiles']) is int and inventory['regularFiles'] == file_count
    assert type(inventory['bytes']) is int and inventory['bytes'] == byte_count
    assert all(type(r['bytes']) is int and r['bytes'] >= 0 for r in files)
    try:
        (app_root / '.next/cache').lstat()
    except FileNotFoundError:
        pass
    else:
        raise AssertionError('Source cache path must be absent; no V1 filtering or weakened mount policy')
    root_stat = app_root.stat()
    assert app_root.is_dir()
    root_identity = dict(dev=root_stat.st_dev, ino=root_stat.st_ino,
        mode=root_stat.st_mode & 0o777, nlink=root_stat.st_nlink)
    evidence = prep.document(app['applicationRootIdentityEvidence'])['rootIdentity']
    assert all(root_identity[k] == evidence[k] for k in root_identity)
    assert assets['schemaVersion'] == 1 and assets['verifiedPassed'] is True
    assert assets['state'] == 'FS_CALLBACK_V2_MODERN_BROWSER_ASSET_SELECTION_DATA_REVIEW_PASSED_V1'
    for key, value in [('applicationBuildReview', app_ref), ('actualBuildResult', app['actualResult']),
            ('applicationInputs', app['applicationInputs']),
            ('applicationRootIdentityEvidence', app['applicationRootIdentityEvidence']),
            ('applicationRoot', str(app_root))]:
        assert assets[key] == value
    assert assets['actionsScriptsAreExactClientSubset'] is True
    assert assets['allSelectedAndExcludedScriptsInventoryAndPhysicalHashVerified'] is True
    assert assets['currentSelectedFileAndRootBookendsStable'] is True
    pins, action_pins = assets['assetPins'], assets['actionsAssetPins']
    assert type(pins) is list and 0 < len(pins) <= 64 and type(action_pins) is list and action_pins
    assert len({p['path'] for p in pins}) == len(pins)
    assert len({p['path'] for p in action_pins}) == len(action_pins)
    assert all(p in pins for p in action_pins)
    for pin in pins:
        assert set(pin) == {'path', 'sha256', 'bytes'} and pin['path'].startswith('/_next/static/')
        assert pin['path'].endswith('.js') and '..' not in pin['path'] and '?' not in pin['path'] and '#' not in pin['path']
        rel = '.next/' + pin['path'][len('/_next/'):]
        member = next(r for r in files if r['path'] == rel)
        assert (member['sha256'], member['bytes']) == (pin['sha256'], pin['bytes'])
    for key in ('clientHtml', 'actionsHtml'):
        prep.checked(assets[key])

    history = HERE / 'source-history' / 'runtime-binding-v1'
    history.parent.mkdir(mode=0o700, exist_ok=True)
    history.mkdir(mode=0o700)  # One shot: preimages are never overwritten.
    metadata_changes = []

    def preserve_family(root, names, label):
        assert {p.name for p in root.iterdir()} in (set(names), set(names) | {'index.json'})
        if (root / 'index.json').exists():
            prep.family(prep.row(root / 'index.json'))
            with (history / (label + '-index.unbound.json')).open('xb') as out:
                out.write((root / 'index.json').read_bytes())
        else:
            prep.save(history / (label + '-payloads.unbound.json'), dict(schemaVersion=1,
                actualIndexBefore=None, files=[prep.row(root / name) for name in names]))

    for root, names, label in [(BROWSER, BROWSER_FILES, 'browser'),
            (CLIENT, CLIENT_FILES, 'client'), (ACTOR, ACTOR_FILES, 'runtime')]:
        preserve_family(root, names, label)

    def bind_plan(root, name, label, transform):
        raw = (root / name).read_bytes()
        preimage = json.loads(raw)
        with (history / (label + '-plan.unbound.json')).open('xb') as out:
            out.write(raw)
        bound = copy.deepcopy(preimage)
        transform(bound)
        changed = sorted(k for k in set(bound) | set(preimage) if bound.get(k) != preimage.get(k))
        inverse = copy.deepcopy(bound)
        for key in changed:
            if key in preimage:
                inverse[key] = preimage[key]
            else:
                del inverse[key]
        assert inverse == preimage and (json.dumps(inverse, indent=2) + '\n').encode() == raw
        (root / name).write_text(json.dumps(bound, indent=2) + '\n')
        metadata_changes.append(dict(role=label, changedKeys=changed,
            unbound=prep.row(history / (label + '-plan.unbound.json')),
            bound=prep.row(root / name), exactByteInverseVerified=True))
        return bound

    def seal(root, names, label):
        index = dict(schemaVersion=1, state='BOUND_FS_CALLBACK_' + label.upper() + '_SOURCE_INDEX_V1',
            files=[dict(path=name, sha256=prep.row(root / name)['sha256'], bytes=prep.row(root / name)['bytes'])
                for name in names])
        (root / 'index.json').write_text(json.dumps(index, indent=2) + '\n')
        ref = prep.row(root / 'index.json')
        prep.family(ref)
        return ref

    def browser_bind(p):
        assert p['actualAssetBindingsPending'] is True
        for key in ('applicationInputs', 'assetSelectionHtml', 'actionsAssetSelectionHtml',
                'assetPins', 'actionsAssetPins', 'actualAssetSelectionReview', 'actualApplicationBuildReview'):
            assert p[key] is None
        p.update(state='BOUND_FS_CALLBACK_BROWSER_SOURCE_V1', actualAssetBindingsPending=False,
            applicationInputs=app['applicationInputs'], assetSelectionHtml=assets['clientHtml'],
            actionsAssetSelectionHtml=assets['actionsHtml'], assetPins=pins, actionsAssetPins=action_pins,
            actualAssetSelectionReview=assets_ref, actualApplicationBuildReview=app_ref)
        p['newApplicationContract'].update(newApplicationVersionPending=False,
            actualApplicationVersion=app['buildVersion'], actualApplicationSourceIndex=APP_SOURCE_INDEX)

    bind_plan(BROWSER, 'plan.json', 'browser', browser_bind)
    browser_ref = seal(BROWSER, BROWSER_FILES, 'browser')

    def client_bind(p):
        assert p['sourceRequirements']['browserSourceIndex'] is None and p['actualBrowserSourceBindingPending'] is True
        assert p['newApplicationContract']['actualApplicationBuildReview'] is None
        p['sourceRequirements']['browserSourceIndex'] = browser_ref
        p['newApplicationContract']['actualApplicationBuildReview'] = app_ref
        p['actualBrowserSourceBindingPending'] = False

    client_plan = bind_plan(CLIENT, 'plan.json', 'client', client_bind)
    client_ref = seal(CLIENT, CLIENT_FILES, 'full_client')
    plans = {}
    for arm, name in [('native', 'plan.json'), ('stock', 'stock-plan.json')]:
        def runtime_bind(p):
            assert p['prospectiveFsCallbackAppBindingsPending'] is True
            assert p['protectedInputs'] == [] and p['sourceFamilies'] == []
            assert p['fsCallbackFullControl']['fullClientSourcePending'] is True
            p.update(applicationInputs=app['applicationInputs'], applicationBuildResult=app['actualResult'],
                applicationBuildReview=app_ref, applicationRootIdentityEvidence=app['applicationRootIdentityEvidence'],
                applicationBuildSource=APP_SOURCE_INDEX, clientSource=prep.row(CLIENT / 'run-contracts.mjs'),
                browserSource=prep.row(BROWSER / 'browser-check.mjs'), clientSourceIndex=client_ref,
                browserSourceIndex=browser_ref, prospectiveFsCallbackAppBindingsPending=False,
                bindingState='READY_FS_CALLBACK_FULL_CONTRACT',
                outputPrefix='/private/tmp/starling-node-compat/next-fs-callback-' + arm + '-v1',
                runId='fs-callback-' + arm + '-first')
            p['requiredApplicationData'].update(applicationBuildReview=app_ref,
                applicationBuildResult=app['actualResult'], applicationInputs=app['applicationInputs'],
                applicationRootIdentityEvidence=app['applicationRootIdentityEvidence'], applicationRoot=str(app_root))
            p['fsCallbackFullControl'].update(assetSelection=assets_ref, browserFamily=browser_ref,
                clientFamily=client_ref, requiredFullClientIndex=client_ref,
                requiredFullClient=prep.row(CLIENT / 'run-contracts.mjs'), fullClientSourcePending=False,
                requiredAssetSelection=assets_ref, requiredBrowserFamily=browser_ref,
                requiredWorker=prep.row(BROWSER / 'browser-check.mjs'))
            p['namespacePolicy']['actualOutputPrefixAndRunIdPending'] = False
            if arm == 'native':
                p.update(applicationSource=str(app_root), applicationBuildOutputRoot=str(Path(app['actualResult']['path']).parent),
                    applicationRootIdentity=root_identity,
                    applicationSchema=dict(name='fresh-next-standalone-root-excluded-v1', sourceDirectoriesExcludeRoot=True,
                        files=file_count, bytes=byte_count, directoriesExcludingRoot=directory_count,
                        ownedDirectoriesIncludingRoot=directory_count + 2, additionalDirectories=['.next/cache']))
            else:
                p.update(standaloneSource=str(app_root), applicationRootIdentity=dict(path=str(app_root), **root_identity),
                    expectedApplication=dict(files=file_count, bytes=byte_count, directories=directory_count,
                        directoryInventoryExcludesRoot=True, symlinks=0))
        # Runtime protection is assembled before these two plans are published.
        pre = json.loads((ACTOR / name).read_bytes())
        runtime_bind(pre)
        plans[arm] = pre

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
    # Stable Source-family declarations, not any predecessor protected array.
    donor = prep.document(prep.row(BASE / 'next-nonredirect-action-runtime-v2/plan.json'))
    assert donor['sourceFamilies'][-2:] == [
        prep.row(BASE / 'next-nonredirect-action-app-build-v2/index.json'),
        prep.row(BASE / 'next-nonredirect-action-browser-v2/index.json')]
    families = donor['sourceFamilies'][:-2] + [APP_SOURCE_INDEX, browser_ref, client_ref]
    for family in families:
        members = prep.family(family)
        add(family)
        for member in members['files']:
            add(dict(member, path=str(Path(family['path']).parent / member['path'])))
    # All six physical full-client dependencies, including the bare contract.
    assert set(client_plan['sourceRequirements']) == {'manifestReader', 'supplemental',
        'portableCacheCollector', 'fixtureContract', 'browserSourceIndex', 'browserWorker'}
    for requirement in client_plan['sourceRequirements'].values():
        add(requirement)
    for name in ACTOR_FILES:
        if name not in ('plan.json', 'stock-plan.json'):
            add(prep.row(ACTOR / name))  # Exclude mutable plan/index cycles.
    for p in plans.values():
        descriptors(p)
        if 'fixedWit' in p:
            for member in p['fixedWit']['files']:
                add(dict(member, path=str(Path(p['fixedWit']['sourceDirectory']) / member['path'])))
    assert len(HOST_REQUIREMENTS) == 6
    for ref in HOST_REQUIREMENTS:
        add(ref)
    for ref in [app_ref, app['actualResult'], app['actualOwnerResult'], app['applicationInputs'],
            app['applicationRootIdentityEvidence'], assets_ref]:
        add(ref)
    protected = sorted(refs.values(), key=lambda r: r['path'])
    for arm, name in [('native', 'plan.json'), ('stock', 'stock-plan.json')]:
        def publish_runtime(p):
            assert p['prospectiveFsCallbackAppBindingsPending'] is True and p['protectedInputs'] == []
            p.clear()
            p.update(plans[arm])
            p['sourceFamilies'] = families
            p['protectedInputs'] = protected
        bind_plan(ACTOR, name, arm, publish_runtime)
    actor_ref = seal(ACTOR, ACTOR_FILES, 'runtime')
    binding = dict(schemaVersion=1, state='ROOT_FS_CALLBACK_ACTUAL_RUNTIME_BINDINGS_V1',
        actorIndex=actor_ref, browserIndex=browser_ref, clientIndex=client_ref,
        nativePlan=prep.row(ACTOR / 'plan.json'), stockPlan=prep.row(ACTOR / 'stock-plan.json'),
        applicationBuildReview=app_ref,
        innerConstructionReview=prep.row(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
        compositionReview=prep.row(BASE / 'next-standard-handler-observer-root-results-v1/actual-next-v3-composition-review.json'),
        assetSelection=assets_ref, protectedInputs=protected)
    binding_ref = prep.save(HERE / 'runtime-bindings.json', binding)
    controller = HERE / 'run-controls.py'
    controller_preimage = controller.read_bytes()
    with (history / 'run-controls.unbound.py').open('xb') as out:
        out.write(controller_preimage)
    controller_bound = controller_preimage
    literals = {'BINDINGS': binding_ref, 'REQUIRED_APP_REVIEW': app_ref, 'REQUIRED_BROWSER_INDEX': browser_ref}
    for name, value in literals.items():
        needle = (name + ' = None').encode()
        assert controller_bound.count(needle) == 1
        controller_bound = controller_bound.replace(needle, (name + ' = ' + repr(value)).encode())
    inverse = controller_bound
    for name, value in literals.items():
        inverse = inverse.replace((name + ' = ' + repr(value)).encode(), (name + ' = None').encode())
    assert inverse == controller_preimage
    controller.write_bytes(controller_bound)
    for ref in protected:
        prep.checked(ref)
    for family in (browser_ref, client_ref, actor_ref):
        prep.family(family)
    after = prep.admit(original)
    assert before == after
    receipt = dict(schemaVersion=1, state='ROOT_FS_CALLBACK_METADATA_BINDINGS_ONLY_V1',
        bindings=binding_ref, controller=prep.row(controller), bindingGenerator=prep.row(Path(__file__).resolve()),
        unboundController=prep.row(history / 'run-controls.unbound.py'), threeLiteralInverseVerified=True,
        planMetadataInverses=metadata_changes, protectedInputCount=len(protected),
        genuineBuildReferences=len(state['buildRefs']), genuineSourceReferences=len(state['sourceRefs']),
        actualApplicationSchema=dict(files=file_count, bytes=byte_count, directoriesExcludingRoot=directory_count),
        sourceCacheAbsent=True, originalConstructorGuardBefore=before, originalConstructorGuardAfter=after,
        clientSourceRequirementsExplicitlyIncluded=sorted(client_plan['sourceRequirements']),
        hostToolRequirementsExplicitlySelected=HOST_REQUIREMENTS,
        oldProtectedArrayReused=False, actorExecuted=False, compilerInvoked=False,
        newPortedApplicationContract=True, oldGlobalCallbackFailureWaived=False,
        fullOriginalContractExecuted=False, fullNextAccepted=False)
    print(json.dumps(prep.save(HERE / 'runtime-source-bindings.json', receipt)))


if __name__ == '__main__':
    main()
