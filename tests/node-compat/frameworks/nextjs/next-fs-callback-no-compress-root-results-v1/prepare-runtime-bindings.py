"""One-shot compression-off full-profile metadata binding; no host/client action.

Reuses the genuine FS callback browser→client→runtime binding mechanism. Every
new source family is closed before mutation. No old protected array is reused.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ACTOR = BASE / 'next-fs-callback-no-compress-runtime-v1'
BROWSER = BASE / 'next-fs-callback-no-compress-browser-v1'
CLIENT = BASE / 'next-fs-callback-no-compress-full-client-v1'
ACTOR_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-runtime-v1/index.json', 'sha256': 'dbb53054f5fc5c6dede614a01bbff064d3f3e6506b09176d1fae3039c474e6e2', 'bytes': 2054}
BROWSER_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-browser-v1/index.json', 'sha256': '8f90eb3e895057a982a3889dd758f96506226b616af75afe6175a2d14d24372c', 'bytes': 835}
CLIENT_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-full-client-v1/index.json', 'sha256': '3b0308adf526f6d48c0f35f056be14972d75e5d60a6affbb09a8a093230dbe4e', 'bytes': 684}
CONTROLLER_UNBOUND = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/run-controls.py', 'sha256': '06a24923e55bfe073ef17a9551b01ccfbf24d45dc04dbf927df513c6f27ee7d0', 'bytes': 20909}
APP_REVIEW = dict(path=str(HERE / 'actual-build-review.json'),
    sha256='9106545f606ee30b2a3a05940d97233ce3b2e867e6abcdc5c5ec84efa09ad679', bytes=22847)
ASSET_SELECTION = dict(path=str(HERE / 'asset-selection.json'),
    sha256='05c965a6b536af21c5947ccace5d9c1cc12b129c86a5b2df42e1bb95dd2c5b4c', bytes=7350)
APP_SOURCE_INDEX = dict(path=str(BASE / 'next-fs-callback-no-compress-app-build-v1/index.json'),
    sha256='5c280e4ba8f6a9eb8b27e9af41e293f22e082f1b3f17b44114019de5efec1422', bytes=6994)
CODE_FILES = ['deploy.mjs', 'run-stock.mjs', 'app-policy.mjs', 'capture-stdout.mjs', 'public-correlation.mjs']
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
    assert all(type(r) is dict for r in (ACTOR_INDEX, BROWSER_INDEX, CLIENT_INDEX, CONTROLLER_UNBOUND)), 'Source families/controller unbound; no helper read or mutation'
    path = BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'
    raw = path.read_bytes()
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (
        '4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', 19784)
    spec = importlib.util.spec_from_file_location('genuine_fs_no_compress_binding_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    state = prep.context()
    family_names = {}
    for root, ref in [(ACTOR, ACTOR_INDEX), (BROWSER, BROWSER_INDEX), (CLIENT, CLIENT_INDEX)]:
        assert ref['path'] == str(root / 'index.json')
        members = prep.family(ref)
        names = [r['path'] for r in members['files']]
        assert all(Path(name).name == name for name in names), 'Flat Source family required'
        family_names[str(root)] = names
    assert CONTROLLER_UNBOUND['path'] == str(HERE / 'run-controls.py')
    prep.checked(CONTROLLER_UNBOUND)
    BROWSER_FILES, CLIENT_FILES, ACTOR_FILES = (family_names[str(r)] for r in (BROWSER, CLIENT, ACTOR))
    original = prep.document(prep.row(path.parent / 'diagnostic-next-construction-authority.json'))
    assert prep.authority(state) == original
    before = prep.admit(original)
    app_ref, assets_ref = APP_REVIEW, ASSET_SELECTION
    app, assets = prep.document(app_ref), prep.document(assets_ref)
    assert app['state'] == 'COORDINATED_FS_CALLBACK_NO_COMPRESS_APP_BUILD_DATA_REVIEW_PASSED_V1'
    for key in ('verifiedPassed', 'verifiedDataReviewPassed', 'sourceCacheAbsent', 'runtimeCacheMountPolicyCompatible'):
        assert app[key] is True
    assert app['buildVersion'] == 1 and app['sourceIndex'] == APP_SOURCE_INDEX
    assert app['configuredCompressFalseVerified'] is True and app['effectiveStandaloneConfigCompressFalseVerified'] is True
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
    assert assets['state'] == 'FS_CALLBACK_NO_COMPRESS_MODERN_BROWSER_ASSET_SELECTION_DATA_REVIEW_PASSED_V1'
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
        assert inverse == preimage
        assert (history / (label + '-plan.unbound.json')).read_bytes() == raw
        (root / name).write_text(json.dumps(bound, indent=2) + '\n')
        metadata_changes.append(dict(role=label, changedKeys=changed,
            unbound=prep.row(history / (label + '-plan.unbound.json')),
            bound=prep.row(root / name), exactSemanticInverseVerified=True, originalBytesPreserved=True))
        return bound

    def seal(root, names, label):
        index = dict(schemaVersion=1, state='BOUND_FS_NO_COMPRESS_' + label.upper() + '_SOURCE_INDEX_V1',
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
        p.update(state='BOUND_FS_NO_COMPRESS_BROWSER_SOURCE_V1', actualAssetBindingsPending=False,
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
                outputPrefix='/private/tmp/starling-node-compat/next-fs-callback-no-compress-' + arm + '-v1',
                runId='fs-no-compress-' + arm + '-first')
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
    for name in CODE_FILES:
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
    # Explicit physical browser/config consumers; URL pins are resolved only
    # against this reviewed inventory, never through a blanket descriptor walk.
    for key in ('clientHtml', 'actionsHtml'):
        add(assets[key])
    selected_paths = {'.next/' + pin['path'][len('/_next/'):] for pin in pins}
    for selection in assets['htmlSelections'].values():
        for url in selection['excludedNoModule']:
            assert url.startswith('/_next/static/') and url.endswith('.js') and '..' not in url
            selected_paths.add('.next/' + url[len('/_next/'):])
    selected_paths.update({'.next/required-server-files.json', 'server.js'})
    for rel in sorted(selected_paths):
        member = next(r for r in files if r['path'] == rel)
        add(dict(path=str(app_root / rel), sha256=member['sha256'], bytes=member['bytes']))
    config = prep.document(prep.row(app_root / '.next/required-server-files.json'))['config']
    assert config['compress'] is False
    assert config['outputFileTracingExcludes'] == {'/api/cache': ['./.next/cache/**']}
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
    binding = dict(schemaVersion=1, state='ROOT_FS_NO_COMPRESS_ACTUAL_RUNTIME_BINDINGS_V1',
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
    literals = {'BINDINGS': binding_ref, 'REQUIRED_BROWSER_INDEX': browser_ref}
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
    receipt = dict(schemaVersion=1, state='ROOT_FS_NO_COMPRESS_METADATA_BINDINGS_ONLY_V1',
        bindings=binding_ref, controller=prep.row(controller), bindingGenerator=prep.row(Path(__file__).resolve()),
        unboundController=prep.row(history / 'run-controls.unbound.py'), twoLiteralInverseVerified=True,
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
