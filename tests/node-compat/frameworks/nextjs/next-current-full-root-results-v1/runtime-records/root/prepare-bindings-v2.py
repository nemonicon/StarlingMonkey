"""Root-only, one-shot metadata binding for the current comprehensive pair.

No compiler, component construction, server or browser is invoked here. The
original constructor's complete native/source/world admission remains intact.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ACTOR = BASE / 'next-current-full-runtime-v1'
BROWSER = BASE / 'next-pristine-redirect-browser-v1'
CLIENT = BASE / 'next-current-full-client-v1'
APP_RECORDS = BASE / 'next-nonredirect-action-root-results-v2'
PRISTINE = BASE / 'next-pristine-redirect-root-results-v1'


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    path = BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'
    raw = path.read_bytes()
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (
        '4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', 19784)
    spec = importlib.util.spec_from_file_location('genuine_current_full_binding_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    state = prep.context()
    original = prep.document(prep.row(path.parent / 'diagnostic-next-construction-authority.json'))
    assert prep.authority(state) == original
    before = prep.admit(original)

    app_ref = prep.row(APP_RECORDS / 'actual-build-review.json')
    assert app_ref['sha256'] == '80c59d47d087c45fd011d950fd38b3ac4de418d13e7cd7d5bfdfe39807502c7f'
    app = prep.document(app_ref)
    assert app['verifiedPassed'] is True
    inventory = prep.document(app['applicationInputs'])
    app_root = Path(app['applicationRoot'])
    root_stat = app_root.stat()
    root_identity = dict(dev=root_stat.st_dev, ino=root_stat.st_ino,
        mode=root_stat.st_mode & 0o777, nlink=root_stat.st_nlink)
    evidence = prep.document(app['applicationRootIdentityEvidence'])['rootIdentity']
    assert all(root_identity[k] == evidence[k] for k in root_identity)
    assert str(app_root) == inventory['root']
    assert inventory['regularFiles'] == 2196 and inventory['bytes'] == 48800578
    assert len(inventory['directories']) == 431
    browser_ref = prep.row(BROWSER / 'index.json')
    assert browser_ref['sha256'] == '7c3a7d87fac27f2cb1bf2820f8c11cc6ddf692509853ecb711330f0a0048ac28'
    prep.family(browser_ref)
    client_ref = prep.row(CLIENT / 'index.json')
    prep.family(client_ref)
    assets_ref = prep.row(PRISTINE / 'asset-selection.json')
    assert assets_ref['sha256'] == '8490ec64d37c4054983c66cb727c877a17bde4fe6325bc0b8429ad6e2de8c01c'

    # Genuine Source metadata is retained before the only permitted binding.
    history = HERE / 'source-history' / 'binding-v2'
    history.mkdir(mode=0o700, exist_ok=True)
    index = json.loads((ACTOR / 'index.json').read_bytes())
    prep.family(prep.row(ACTOR / 'index.json'))
    controller = HERE / 'run-controls.py'
    controller_preimage = controller.read_bytes()
    assert controller_preimage.count(b'BINDINGS = None') == 1
    (history / 'index.unbound.json').write_bytes((ACTOR / 'index.json').read_bytes())
    (history / 'run-controls.unbound.py').write_bytes(controller_preimage)
    plans = {}
    preimages = {}
    for arm, name in [('native', 'plan.json'), ('stock', 'stock-plan.json')]:
        p = json.loads((ACTOR / name).read_bytes())
        assert p['prospectiveCurrentFullAppBindingsPending'] is True
        assert p['protectedInputs'] == []
        preimages[arm] = copy.deepcopy(p)
        prep.save(history / (arm + '-plan.unbound.json'), p)
        p.update(applicationInputs=app['applicationInputs'], applicationBuildResult=app['actualResult'],
            applicationBuildReview=app_ref, applicationRootIdentityEvidence=app['applicationRootIdentityEvidence'],
            applicationBuildSource=prep.row(BASE / 'next-nonredirect-action-app-build-v2/index.json'),
            clientSource=prep.row(CLIENT / 'run-contracts.mjs'), browserSource=prep.row(BROWSER / 'browser-check.mjs'),
            clientSourceIndex=client_ref, browserSourceIndex=browser_ref,
            prospectiveCurrentFullAppBindingsPending=False,
            bindingState='READY_CURRENT_FULL_CONTRACT_CONTROL',
            outputPrefix='/private/tmp/starling-node-compat/next-current-full-' + arm + '-v1',
            runId='current-full-' + arm + '-first')
        p['currentFullControl']['assetSelection'] = assets_ref
        p['currentFullControl']['browserFamily'] = browser_ref
        p['currentFullControl']['clientFamily'] = client_ref
        p['currentFullControl']['requiredFullClientIndex'] = client_ref
        p['currentFullControl']['requiredFullClient'] = prep.row(CLIENT / 'run-contracts.mjs')
        p['currentFullControl']['fullClientSourcePending'] = False
        p['namespacePolicy']['actualOutputPrefixAndRunIdPending'] = False
        if arm == 'native':
            p.update(applicationSource=str(app_root), applicationBuildOutputRoot=str(Path(app['actualResult']['path']).parent),
                applicationRootIdentity=root_identity,
                applicationSchema=dict(name='fresh-next-standalone-root-excluded-v1', sourceDirectoriesExcludeRoot=True,
                    files=2196, bytes=48800578, directoriesExcludingRoot=431, ownedDirectoriesIncludingRoot=433,
                    additionalDirectories=['.next/cache']))
        else:
            p.update(standaloneSource=str(app_root), applicationRootIdentity=dict(path=str(app_root), **root_identity),
                expectedApplication=dict(files=2196, bytes=48800578, directories=431,
                    directoryInventoryExcludesRoot=True, symlinks=0))
        plans[arm] = p

    # Fresh union of consumed descriptor roles and genuine constructor evidence.
    # No predecessor protected-input array is copied or rewritten. Asset URLs
    # stay typed in the selected browser family, never treated as host paths.
    refs = {}

    def add(ref):
        prep.checked(ref)
        if ref['path'] in refs:
            assert refs[ref['path']] == ref
        refs[ref['path']] = ref

    def descriptors(value):
        if type(value) is dict:
            if set(value) == {'path', 'sha256', 'bytes'}:
                assert Path(value['path']).is_absolute(), 'Relative/URL role must be selected explicitly'
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
    # Original runtime-family declarations, unchanged byte-for-byte, are Source
    # dependencies rather than substituted predecessor execution receipts.
    donor = prep.document(prep.row(BASE / 'next-nonredirect-action-runtime-v2/plan.json'))
    assert donor['sourceFamilies'][-2:] == [
        prep.row(BASE / 'next-nonredirect-action-app-build-v2/index.json'),
        prep.row(BASE / 'next-nonredirect-action-browser-v2/index.json')]
    families = donor['sourceFamilies'][:-2] + [
        prep.row(BASE / 'next-nonredirect-action-app-build-v2/index.json'), browser_ref, client_ref]
    for family in families:
        members = prep.family(family)
        add(family)
        for member in members['files']:
            add(dict(member, path=str(Path(family['path']).parent / member['path'])))
    # Family membership protects this manifest, not its external consumers.
    # Select all six declared filesystem requirements explicitly into the graph.
    client_plan = prep.document(prep.row(CLIENT / 'plan.json'))
    assert type(client_plan['sourceRequirements']) is dict and len(client_plan['sourceRequirements']) == 6
    for requirement in client_plan['sourceRequirements'].values():
        add(requirement)
    for p in plans.values():
        descriptors(p)
        if 'fixedWit' in p:
            for member in p['fixedWit']['files']:
                add(dict(member, path=str(Path(p['fixedWit']['sourceDirectory']) / member['path'])))
    host = prep.document(prep.row(PRISTINE / 'runtime-bindings.json'))
    for ref in host['protectedInputs']:
        if '/browser-tools/' in ref['path'] or ref['path'].startswith('/Applications/Google Chrome.app/'):
            add(ref)
    for ref in [app_ref, app['applicationInputs'], app['actualResult'], app['applicationRootIdentityEvidence'], assets_ref]:
        add(ref)
    protected = sorted(refs.values(), key=lambda r: r['path'])
    changes = []
    for arm, name in [('native', 'plan.json'), ('stock', 'stock-plan.json')]:
        p = plans[arm]
        p['sourceFamilies'] = families
        p['protectedInputs'] = protected
        changed = sorted(k for k in set(p) | set(preimages[arm]) if p.get(k) != preimages[arm].get(k))
        inverse = copy.deepcopy(p)
        for key in changed:
            if key in preimages[arm]:
                inverse[key] = preimages[arm][key]
            else:
                del inverse[key]
        assert inverse == preimages[arm]
        (ACTOR / name).write_text(json.dumps(p, indent=2) + '\n')
        changes.append(dict(arm=arm, changedKeys=changed,
            unbound=prep.row(history / (arm + '-plan.unbound.json')), bound=prep.row(ACTOR / name), inverseVerified=True))
    for member in index['files']:
        if member['path'] in ('plan.json', 'stock-plan.json'):
            ref = prep.row(ACTOR / member['path'])
            member.update(sha256=ref['sha256'], bytes=ref['bytes'])
    (ACTOR / 'index.json').write_text(json.dumps(index, indent=2) + '\n')
    actor_ref = prep.row(ACTOR / 'index.json')
    prep.family(actor_ref)
    binding = dict(schemaVersion=1, state='ROOT_CURRENT_FULL_ACTUAL_RUNTIME_BINDINGS_V1',
        actorIndex=actor_ref, browserIndex=browser_ref, clientIndex=client_ref,
        nativePlan=prep.row(ACTOR / 'plan.json'), stockPlan=prep.row(ACTOR / 'stock-plan.json'),
        applicationBuildReview=app_ref,
        innerConstructionReview=prep.row(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
        compositionReview=prep.row(BASE / 'next-standard-handler-observer-root-results-v1/actual-next-v3-composition-review.json'),
        assetSelection=assets_ref, protectedInputs=protected)
    binding_ref = prep.save(HERE / 'runtime-bindings.json', binding)
    bound_controller = controller_preimage.replace(b'BINDINGS = None', ('BINDINGS = ' + repr(binding_ref)).encode())
    controller.write_bytes(bound_controller)
    assert bound_controller.replace(('BINDINGS = ' + repr(binding_ref)).encode(), b'BINDINGS = None') == controller_preimage
    after = prep.admit(original)
    assert before == after
    receipt = dict(schemaVersion=1, state='ROOT_CURRENT_FULL_METADATA_BINDINGS_ONLY_V1',
        bindings=binding_ref, controller=prep.row(controller), bindingGenerator=prep.row(Path(__file__).resolve()),
        unboundController=prep.row(history / 'run-controls.unbound.py'), oneDescriptorInverseVerified=True,
        planMetadataInverses=changes, protectedInputCount=len(protected),
        genuineBuildReferences=len(state['buildRefs']), genuineSourceReferences=len(state['sourceRefs']),
        constructorGuardBefore=before, constructorGuardAfter=after, actorExecuted=False,
        clientSourceRequirementsExplicitlyIncluded=sorted(client_plan['sourceRequirements']),
        metadataCorrection='Explicit external client consumers after held first preparation; zero actors/trials before correction',
        compilerInvoked=False, fullOriginalContractExecuted=False, fullNextAccepted=False)
    result = prep.save(HERE / 'source-bindings.json', receipt)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
