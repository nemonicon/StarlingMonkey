"""One-shot Root binding of the captured-request HTTP diagnostic.

Only original read/admission helpers run here. No server, client, browser,
compiler or component constructor is launched.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ACTOR = BASE / 'next-rsc-response-runtime-v1'
CLIENT = BASE / 'next-rsc-response-client-v1'
ACTOR_INDEX = None
CLIENT_INDEX = None
APP_REVIEW = dict(path=str(BASE / 'next-fs-callback-root-results-v2/actual-build-review.json'),
    sha256='4a6f03cefbed841af163f62f2ef4cc226a025d84379c7cb7f2a33a541e0b147c', bytes=18599)
CAPTURE = dict(path=str(HERE / 'request-capture.json'),
    sha256='050c528ff1ec2ff52918fcf1f4a973ba32dca967490ff0925874daa84c4f36fc', bytes=9062)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    assert type(ACTOR_INDEX) is dict and type(CLIENT_INDEX) is dict, 'Source peer/seals pending; no helper read or mutation'
    path = BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'
    raw = path.read_bytes()
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (
        '4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', 19784)
    spec = importlib.util.spec_from_file_location('genuine_rsc_response_binding_admission', path)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    state = prep.context()
    original = prep.document(prep.row(path.parent / 'diagnostic-next-construction-authority.json'))
    assert prep.authority(state) == original
    before = prep.admit(original)
    prep.family(ACTOR_INDEX)
    prep.family(CLIENT_INDEX)
    assert Path(ACTOR_INDEX['path']) == ACTOR / 'index.json'
    assert Path(CLIENT_INDEX['path']) == CLIENT / 'index.json'
    app = prep.document(APP_REVIEW)
    assert app['state'] == 'COORDINATED_FS_CALLBACK_APP_BUILD_DATA_REVIEW_PASSED_V1'
    assert app['buildVersion'] == 2
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
        assert inverse == old and (json.dumps(inverse, indent=2) + '\n').encode() == raw
        (folder / filename).write_text(json.dumps(new, indent=2) + '\n')
        changes.append(dict(role=label, changedKeys=keys, exactByteInverseVerified=True,
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
    client_ref = reseal(CLIENT)
    plans = {}
    preimages = {}
    for arm, name in [('native', 'plan.json'), ('stock', 'stock-plan.json')]:
        p = json.loads((ACTOR / name).read_bytes())
        assert p['prospectiveRscResponseBindingsPending'] is True and p['protectedInputs'] == [] and p['sourceFamilies'] == []
        preimages[arm] = copy.deepcopy(p)
        p.update(applicationInputs=app['applicationInputs'], applicationBuildResult=app['actualResult'],
            applicationBuildReview=APP_REVIEW, applicationRootIdentityEvidence=app['applicationRootIdentityEvidence'],
            applicationBuildSource=app['sourceIndex'], clientSource=prep.row(CLIENT / 'run-client.mjs'),
            clientSourceIndex=client_ref, prospectiveRscResponseBindingsPending=False,
            bindingState='READY_RSC_RESPONSE_CONTROL', browserTools='reserved-unused',
            outputPrefix='/private/tmp/starling-node-compat/next-rsc-response-' + arm + '-v1',
            runId='rsc-response-' + arm + '-first')
        p['rscResponseControl'].update(clientSourcePending=False, requiredClientIndex=client_ref,
            requiredClient=prep.row(CLIENT / 'run-client.mjs'))
        p['namespacePolicy']['actualOutputPrefixAndRunIdPending'] = False
        if arm == 'native':
            p.update(applicationSource=str(root), applicationBuildOutputRoot=str(Path(app['actualResult']['path']).parent),
                applicationRootIdentity=identity, applicationSchema=dict(name='fresh-next-standalone-root-excluded-v1',
                    sourceDirectoriesExcludeRoot=True, files=count, bytes=size, directoriesExcludingRoot=dirs,
                    ownedDirectoriesIncludingRoot=dirs + 2, additionalDirectories=['.next/cache']))
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
            app['actualResult'], app['actualOwnerResult'], app['applicationInputs'], app['applicationRootIdentityEvidence']]:
        add(ref)
    for ref in capture['source'].values():
        add(ref)
    for p in plans.values():
        descriptors(p)
        if 'fixedWit' in p:
            for member in p['fixedWit']['files']:
                add(dict(member, path=str(Path(p['fixedWit']['sourceDirectory']) / member['path'])))
    for name in ('deploy.mjs', 'run-stock.mjs', 'app-policy.mjs', 'capture-stdout.mjs', 'public-correlation.mjs'):
        add(prep.row(ACTOR / name))
    protected = sorted(refs.values(), key=lambda r: r['path'])
    for arm, name in [('native', 'plan.json'), ('stock', 'stock-plan.json')]:
        def publish(p):
            assert p == preimages[arm]
            p.clear()
            p.update(plans[arm])
            p['sourceFamilies'] = families
            p['protectedInputs'] = protected
        bind_plan(ACTOR, name, arm, publish)
    actor_ref = reseal(ACTOR)
    binding = dict(schemaVersion=1, state='ROOT_RSC_RESPONSE_ACTUAL_RUNTIME_BINDINGS_V1',
        actorIndex=actor_ref, clientIndex=client_ref, nativePlan=prep.row(ACTOR / 'plan.json'),
        stockPlan=prep.row(ACTOR / 'stock-plan.json'), applicationBuildReview=APP_REVIEW,
        requestCapture=CAPTURE, protectedInputs=protected,
        innerConstructionReview=prep.row(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
        compositionReview=prep.row(BASE / 'next-standard-handler-observer-root-results-v1/actual-next-v3-composition-review.json'))
    binding_ref = prep.save(HERE / 'runtime-bindings.json', binding)
    controller = HERE / 'run-controls.py'
    raw = controller.read_bytes()
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
    receipt = dict(schemaVersion=1, state='ROOT_RSC_RESPONSE_METADATA_BOUND_NOT_RUN_V1',
        bindings=binding_ref, generator=prep.row(Path(__file__).resolve()), controller=prep.row(controller),
        planInverses=changes, controllerOneLiteralInverseVerified=True,
        protectedInputCount=len(protected), originalGuardBefore=before, originalGuardAfter=after,
        genuineBuildReferences=len(state['buildRefs']), genuineSourceReferences=len(state['sourceRefs']),
        oldProtectedArrayCopied=False, browserSelected=False, requestSent=False, fullNextAccepted=False)
    print(json.dumps(prep.save(HERE / 'source-bindings.json', receipt)))


if __name__ == '__main__':
    main()
