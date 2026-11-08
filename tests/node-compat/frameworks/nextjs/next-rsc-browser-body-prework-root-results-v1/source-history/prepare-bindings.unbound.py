"""Bind the captured Chrome body-response prework pair; no actor or host launch."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ACTOR = BASE / 'next-rsc-browser-body-prework-runtime-v1'
CLIENT = BASE / 'next-rsc-browser-body-prework-client-v1'
ACTOR_INDEX = None
CLIENT_INDEX = None
CONTROLLER_UNBOUND = None
APP_REVIEW = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/actual-build-review.json'),
    sha256='9106545f606ee30b2a3a05940d97233ce3b2e867e6abcdc5c5ec84efa09ad679', bytes=22847)
CAPTURE = dict(path=str(BASE / 'next-fs-callback-no-compress-wasmcloud-root-results-v1/identity-request-capture.json'),
    sha256='a45dea80ec6e14cad111c490d15c2af916cdc42819e5f7622991041a7e6c5daf', bytes=11055)
ASSET_SELECTION = dict(path=str(BASE / 'next-fs-callback-no-compress-root-results-v1/asset-selection.json'),
    sha256='05c965a6b536af21c5947ccace5d9c1cc12b129c86a5b2df42e1bb95dd2c5b4c', bytes=7350)
FAILED_CLOUD_REVIEW = dict(path=str(BASE / 'next-fs-callback-no-compress-wasmcloud-root-results-v1/actual-runtime-review.json'),
    sha256='81a9c56b5c22c284149f971ae1e6ca9cdd4d8b72d8f22e4a5b107f4aa9d3041a', bytes=81083)

HOST_REQUIREMENTS = [{'path': '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 'sha256': '2a2d660daf7f2a6e405fc6b885c996eca0ac71dd9f52d326e06d4d602ce9352c', 'bytes': 367696}, {'path': '/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/node_modules/playwright-core/index.js', 'sha256': 'a58fb2cec4293e7dcf73c58a179898a4f3986666451a19da4e731fa3af63265b', 'bytes': 697}, {'path': '/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/node_modules/playwright-core/index.mjs', 'sha256': '3d36e2132d3c8b62397d23f0bb4177336aaee503203ae2a2c90fbeb5bf3317dd', 'bytes': 1063}, {'path': '/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/node_modules/playwright-core/package.json', 'sha256': '8aa1c9863fa8dea324e674254158cdc79440f4124ef2d84d38053013541cb7d6', 'bytes': 876}, {'path': '/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/package-lock.json', 'sha256': 'f8dd9d403df7dc61de13badeefa22da1e639f5eb8117537a39fa864f9a37ba8f', 'bytes': 714}, {'path': '/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/package.json', 'sha256': '7b241bd7c3c2a45f0484ccd799fd5f6fa6ce517d70278a7a92f26b7b2e882661', 'bytes': 164}]
BROWSER_TOOLS = '/private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools'
IDENTITY_REVIEW = dict(path=str(BASE / 'next-rsc-identity-prework-root-results-v1/actualreview.json'),
    sha256='04f53121c8c75ae60c9dee51122bbfb2657d3abc73a9a3c5f95d00bc0c993c5d', bytes=124407)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    assert all(type(r) is dict for r in (ACTOR_INDEX, CLIENT_INDEX, CONTROLLER_UNBOUND)), 'Source peer/seals pending; no helper read or mutation'
    path = BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'
    raw = path.read_bytes()
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (
        '4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', 19784)
    spec = importlib.util.spec_from_file_location('genuine_rsc_browser_body_binding_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    state = prep.context()
    original = prep.document(prep.row(path.parent / 'diagnostic-next-construction-authority.json'))
    assert prep.authority(state) == original
    before = prep.admit(original)
    prep.family(ACTOR_INDEX)
    prep.family(CLIENT_INDEX)
    assert CONTROLLER_UNBOUND['path'] == str(HERE / 'run-controls.py')
    prep.checked(CONTROLLER_UNBOUND)
    failed = prep.document(FAILED_CLOUD_REVIEW)
    assert failed['verifiedDataReviewPassed'] is True and failed['fullContractPassed'] is False
    assert failed['fullNextAccepted'] is False
    assert Path(ACTOR_INDEX['path']) == ACTOR / 'index.json'
    assert Path(CLIENT_INDEX['path']) == CLIENT / 'index.json'
    identity_review = prep.document(IDENTITY_REVIEW)
    assert identity_review['verifiedDataReviewPassed'] is True and identity_review['fullNextAccepted'] is False
    app = prep.document(APP_REVIEW)
    assert app['state'] == 'COORDINATED_FS_CALLBACK_NO_COMPRESS_APP_BUILD_DATA_REVIEW_PASSED_V1'
    assert app['buildVersion'] == 1
    assert app['configuredCompressFalseVerified'] is True and app['effectiveStandaloneConfigCompressFalseVerified'] is True
    assert all(app[k] is True for k in ('verifiedPassed', 'verifiedDataReviewPassed',
        'sourceCacheAbsent', 'runtimeCacheMountPolicyCompatible'))
    capture = prep.document(CAPTURE)
    assert capture['verifiedDataCapturePassed'] is True and capture['method'] == 'POST' and capture['path'] == '/actions'
    assert capture['source']['applicationBuildReview'] == APP_REVIEW
    assert capture['body']['bytes'] == 391
    prep.checked(capture['body'])
    prep.checked(capture['headerEvidence'])
    assert capture['rootSelectedReplayHeaderPolicy']['removeHeaderNames'] == ['x-next-public-request-correlation']
    inventory = prep.document(app['applicationInputs'])
    root = Path(app['applicationRoot'])
    assert inventory['root'] == str(root) and inventory['symlinks'] == []
    files, directories = inventory['files'], inventory['directories']
    assert all(r['path'] != '.next/cache' and not r['path'].startswith('.next/cache/') for r in files + directories)
    assert not (root / '.next/cache').exists() and not (root / '.next/cache').is_symlink()
    count, size, dirs = len(files), sum(r['bytes'] for r in files), len(directories)
    assert count == inventory['regularFiles'] and size == inventory['bytes']
    stat = root.stat()
    identity = dict(dev=stat.st_dev, ino=stat.st_ino, mode=stat.st_mode & 0o777, nlink=stat.st_nlink)
    evidence = prep.document(app['applicationRootIdentityEvidence'])['rootIdentity']
    assert all(identity[k] == evidence[k] for k in identity)
    history = HERE / 'source-history/binding-v1'
    history.mkdir(parents=True)
    changes = []

    def preserve_index(folder, label):
        with (history / (label + '-index.unbound.json')).open('xb') as out:
            out.write((folder / 'index.json').read_bytes())

    def bind_plan(folder, filename, label, transform):
        raw = (folder / filename).read_bytes()
        old = json.loads(raw)
        with (history / (label + '-plan.unbound.json')).open('xb') as out:
            out.write(raw)
        new = copy.deepcopy(old)
        transform(new)
        keys = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
        inverse = copy.deepcopy(new)
        for k in keys:
            if k in old:
                inverse[k] = old[k]
            else:
                del inverse[k]
        assert inverse == old
        assert (history / (label + '-plan.unbound.json')).read_bytes() == raw
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

    preserve_index(CLIENT, 'client')
    preserve_index(ACTOR, 'actor')

    def bind_client(p):
        assert p['requestCapture'] is None and p['requestCaptureBindingPending'] is True
        assert set(p['sourceRequirements']) == {'requestCapture', 'requestBody', 'headerEvidence'}
        assert all(v is None for v in p['sourceRequirements'].values())
        p['requestCapture'] = CAPTURE
        p['requestCaptureBindingPending'] = False
        p['sourceRequirements'].update(requestCapture=CAPTURE,
            requestBody=capture['body'], headerEvidence=capture['headerEvidence'])

    client_plan = bind_plan(CLIENT, 'plan.json', 'client', bind_client)
    assert client_plan['hostRequirements'] == HOST_REQUIREMENTS and client_plan['browserTools'] == BROWSER_TOOLS
    assert set(client_plan['preworkSourceRequirements']) == {'donorFullClient', 'portableCacheCollector', 'supplemental', 'fixtureContract'}
    for ref in client_plan['preworkSourceRequirements'].values():
        prep.checked(ref)
    client_ref = reseal(CLIENT)
    plans = {}
    preimages = {}
    for arm, name in [('cloud', 'plan.json'), ('stock', 'stock-plan.json')]:
        p = json.loads((ACTOR / name).read_bytes())
        assert p['prospectiveRscResponseBindingsPending'] is True and p['protectedInputs'] == [] and p['sourceFamilies'] == []
        preimages[arm] = copy.deepcopy(p)
        p.update(applicationInputs=app['applicationInputs'], applicationBuildResult=app['actualResult'],
            applicationBuildReview=APP_REVIEW, applicationRootIdentityEvidence=app['applicationRootIdentityEvidence'],
            applicationBuildSource=app['sourceIndex'], clientSource=prep.row(CLIENT / 'run-client.mjs'),
            clientSourceIndex=client_ref, prospectiveRscResponseBindingsPending=False,
            bindingState='READY_RSC_RESPONSE_CONTROL', browserTools=BROWSER_TOOLS,
            outputPrefix='/private/tmp/starling-node-compat/next-rsc-browser-body-prework-' + arm + '-v1',
            runId='rsc-browser-body-' + arm + '-first')
        p['rscResponseControl'].update(clientSourcePending=False, requiredClientIndex=client_ref,
            requiredClient=prep.row(CLIENT / 'run-client.mjs'))
        p['namespacePolicy']['actualOutputPrefixAndRunIdPending'] = False
        if 'requiredApplicationData' in p:
            p['requiredApplicationData'].update(applicationBuildReview=APP_REVIEW,
                applicationBuildResult=app['actualResult'], applicationInputs=app['applicationInputs'],
                applicationRootIdentityEvidence=app['applicationRootIdentityEvidence'], applicationRoot=str(root))
        if arm == 'cloud':
            p.update(applicationSource=str(root), applicationBuildOutputRoot=str(Path(app['actualResult']['path']).parent),
                applicationRootIdentity=identity, applicationSchema=dict(name='fresh-next-standalone-root-excluded-v1',
                    sourceDirectoriesExcludeRoot=True, files=count, bytes=size, directoriesExcludingRoot=dirs,
                    ownedDirectoriesIncludingRoot=dirs + 1, additionalDirectories=[]))
        else:
            p.update(standaloneSource=str(root), applicationRootIdentity=dict(path=str(root), **identity),
                expectedApplication=dict(files=count, bytes=size, directories=dirs,
                    directoryInventoryExcludesRoot=True, symlinks=0))
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
                assert Path(value['path']).is_absolute(), 'Typed relative/URL roles require explicit selection'
                add(value)
            else:
                for k, v in value.items():
                    if k not in ('fixedWit', 'protectedInputs', 'sourceFamilies'):
                        descriptors(v)
        elif type(value) is list:
            for v in value:
                descriptors(v)

    for ref in state['buildRefs'] + state['sourceRefs'] + [prep.ENGINE, prep.NATIVE_METADATA]:
        add(ref)
    donor = prep.document(prep.row(BASE / 'next-nonredirect-action-runtime-v2/plan.json'))
    assert donor['sourceFamilies'][-2:] == [
        prep.row(BASE / 'next-nonredirect-action-app-build-v2/index.json'),
        prep.row(BASE / 'next-nonredirect-action-browser-v2/index.json')]
    # Stable Source declarations only; no prior protected-input array is reused.
    families = donor['sourceFamilies'][:-2] + [app['sourceIndex'], client_ref]
    for family in families:
        index = prep.family(family)
        add(family)
        for member in index['files']:
            add(dict(member, path=str(Path(family['path']).parent / member['path'])))
    descriptors(client_plan)
    for ref in [CAPTURE, capture['body'], capture['headerEvidence'], APP_REVIEW,
            app['actualResult'], app['actualOwnerResult'], app['applicationInputs'], app['applicationRootIdentityEvidence'],
            ASSET_SELECTION, FAILED_CLOUD_REVIEW]:
        add(ref)
    for ref in capture['source'].values():
        add(ref)
    for ref in HOST_REQUIREMENTS + [IDENTITY_REVIEW]:
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
    for arm, name in [('cloud', 'plan.json'), ('stock', 'stock-plan.json')]:
        def publish(p):
            assert p == preimages[arm]
            p.clear()
            p.update(plans[arm])
            p['sourceFamilies'] = families
            p['protectedInputs'] = protected
        bind_plan(ACTOR, name, arm, publish)
    actor_ref = reseal(ACTOR)
    binding = dict(schemaVersion=1, state='ROOT_RSC_BROWSER_BODY_PREWORK_ACTUAL_BINDINGS_V1',
        actorIndex=actor_ref, clientIndex=client_ref, cloudPlan=prep.row(ACTOR / 'plan.json'),
        stockPlan=prep.row(ACTOR / 'stock-plan.json'), applicationBuildReview=APP_REVIEW,
        requestCapture=CAPTURE, assetSelection=ASSET_SELECTION, originalFailedCloudReview=FAILED_CLOUD_REVIEW, precedingIdentityReview=IDENTITY_REVIEW, protectedInputs=protected,
        innerConstructionReview=prep.row(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
        compositionReview=prep.row(BASE / 'next-standard-handler-observer-root-results-v1/actual-next-v3-composition-review.json'))
    binding_ref = prep.save(HERE / 'runtime-bindings.json', binding)
    controller = HERE / 'run-controls.py'
    raw = prep.checked(CONTROLLER_UNBOUND).read_bytes()
    with (history / 'run-controls.unbound.py').open('xb') as out:
        out.write(raw)
    needle = b'BINDINGS = None'
    replacement = ('BINDINGS = ' + repr(binding_ref)).encode()
    assert raw.count(needle) == 1
    bound = raw.replace(needle, replacement)
    assert bound.replace(replacement, needle) == raw
    controller.write_bytes(bound)
    for ref in protected:
        prep.checked(ref)
    for ref in (actor_ref, client_ref):
        prep.family(ref)
    after = prep.admit(original)
    assert before == after
    receipt = dict(schemaVersion=1, state='ROOT_RSC_BROWSER_BODY_PREWORK_METADATA_BOUND_NOT_RUN_V1',
        bindings=binding_ref, generator=prep.row(Path(__file__).resolve()), controller=prep.row(controller),
        planInverses=changes, controllerOneLiteralInverseVerified=True,
        protectedInputCount=len(protected), originalGuardBefore=before, originalGuardAfter=after,
        genuineBuildReferences=len(state['buildRefs']), genuineSourceReferences=len(state['sourceRefs']),
        oldProtectedArrayCopied=False, browserSelected=True, browserInvoked=False, requestSent=False, fullNextAccepted=False)
    print(json.dumps(prep.save(HERE / 'source-bindings.json', receipt)))


if __name__ == '__main__':
    main()
