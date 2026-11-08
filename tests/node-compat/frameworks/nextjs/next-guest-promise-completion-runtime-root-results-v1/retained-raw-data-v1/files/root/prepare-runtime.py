"""Prepare one guest-promise-completion full-suite authority from actual constructor/build records; no actor."""
import hashlib
import importlib.util
import sys
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[4]


def row(path):
    path = Path(path)
    assert path.is_absolute() and path.resolve() == path and not path.is_symlink()
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def read(path):
    return json.loads(Path(path).read_text())


def write_new(path, value):
    with path.open('x') as handle:
        handle.write(json.dumps(value, indent=2) + '\n')


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    wrapper_path = HERE / 'run-full-native-requests.py'
    spec = importlib.util.spec_from_file_location('guest_completion_root_admission', wrapper_path)
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)
    native_guard, world_guard = wrapper.context()
    row = wrapper.row
    actor = wrapper.ACTOR
    actor_plan = read(actor / 'plan.json')
    wrapper.capacity(actor_plan, 1073741824)
    ctor_dir = BASE / 'next-guest-promise-completion-construction-root-results-v1'
    ctor_path = ctor_dir / 'guest-promise-completion-construction-authority.json'
    constructor = read(ctor_path)
    root = Path(constructor['outputRoot'])
    construction_ref = row(root / 'result.json')
    construction = read(root / 'result.json')
    ctor_review_ref = row(ctor_dir / 'actual-construction-review.json')
    ctor_review = read(ctor_review_ref['path'])
    assert ctor_review_ref == actor_plan['acceptedConstructionReview']
    assert ctor_review['verifiedPassed'] is True
    assert ctor_review['state'] == 'COORDINATED_GUEST_PROMISE_COMPLETION_COMPONENT_INIT_DATA_REVIEW_PASSED_V1'
    assert ctor_review['actualResult'] == construction_ref
    assert ctor_review['rootAuthority'] == row(ctor_path)
    assert construction['passed'] is True and construction['error'] is None
    assert construction['finalProtection']['unchanged'] is True
    assert ctor_review['completeReturnedImportAuditVerified'] is True
    assert construction['entryMode'] == ctor_review['entryMode'] == 'real-next'
    for key in ['callerIndex', 'plan', 'rootAuthority']:
        assert ctor_review[key] == construction[key]
    for key in ['component', 'componentAudit', 'engine', 'nativeMetadata', 'inputSourceIndex', 'inputEntry']:
        assert ctor_review[key] == construction['artifacts'][key]
    assert ctor_review['deployedCompletionDiagnosticObserved'] is False
    assert len(constructor['metadataExpectedFixedValues']) == 31
    assert len(constructor['engineBuildEvidence']) == 39
    assert len(constructor['newSourceEvidence']) == 18
    assert actor_plan['prospectiveActualBindingsPending'] is False
    app_dir = BASE / 'next-portable-cache-app-build-root-results-v1'
    app_review_ref = row(app_dir / 'actual-build-review-v2.json')
    assert app_review_ref['sha256'] == '163133f1db2d8957bfeb871a26de3c5b3f588ef303c18ae27336120ee19941e2'
    app_review = read(app_review_ref['path'])
    assert app_review['verifiedPassed'] is True
    assert app_review['state'] == 'PORTABLE_CACHE_APP_HOST_BUILD_DATA_REVIEW_PASSED_V1'
    assert app_review['sourceFiles'] == 31 and app_review['unchangedParentFiles'] == 28
    assert actor_plan['applicationBuildReview'] == app_review_ref
    assert actor_plan['applicationBuildResult'] == app_review['actualResult']
    assert actor_plan['applicationInputs'] == row(Path(actor_plan['applicationInputs']['path']))
    component = construction['artifacts']['component']
    assert component == ctor_review['component'] == row(Path(component['path']))
    assert actor_plan['expectedComponent'] == {key: component[key] for key in ['sha256', 'bytes']}
    # Fresh wire assembled explicitly; no old authority or protection array is retargeted.
    authority = dict(schemaVersion=1, state='ROOT_NEXT_WASMTIME_DEPLOYMENT_AUTHORIZED_V2', unissued=False,
        sourceIndex=row(actor / 'index.json'), plan=row(actor / 'plan.json'),
        constructionResult=construction_ref, component=component,
        componentAudit=construction['artifacts']['componentAudit'],
        localhostServeAllowed=True, actualNextGuestAllowed=True, browserAllowed=True,
        compilerAllowed=False, componentConstructionAllowed=False,
        externalDeploymentAllowed=False, adoptionAllowed=False,
        constructionCallerIndex=constructor['callerIndex'],
        constructionDataReview=ctor_review_ref, applicationBuildDataReview=app_review_ref,
        rootLaunchMinimumFreeBytes=1073741824, runId='promise-completion-476b-netlog-first',
        wrapperPython=wrapper.PYTHON, fullNativeGuardImplementation=wrapper.FULL_GUARD,
        rootPreparation=row(Path(__file__).resolve()), rootWrapper=row(wrapper_path),
        applicationSource=actor_plan['applicationSource'], applicationInputs=actor_plan['applicationInputs'],
        applicationRootIdentityEvidence=actor_plan['applicationRootIdentityEvidence'])
    for key in ['inputEntry', 'inputSourceIndex']:
        authority[key] = construction['artifacts'][key]
    for key in ['engine', 'nativeMetadata', 'metadataExpectedFixedValues', 'engineBuildEvidence']:
        authority[key] = constructor[key]
    external = Path(str(root) + '-external-root')
    authority['constructionOuterTerminal'] = row(external / 'terminal.json')
    authority['constructionWorldGuard'] = row(external / 'world-guard.json')
    authority['worldGuardImplementation'] = wrapper.WORLD_GUARD
    authority['worldSourceIndex'] = constructor['worldSourceIndex']
    authority['worldInputs'] = [ref for ref in constructor['newSourceEvidence'] if ref['path'].endswith('.wit')]
    assert len(authority['worldInputs']) == 8
    build = Path(authority['nativeMetadata']['path']).parent
    native = read(authority['nativeMetadata']['path'])
    build_result = read(build / 'result.json')
    authority['fullNativeBuildResult'] = row(build / 'result.json')
    authority['fullNativeBuildObservation'] = row(Path(str(build) + '-root-monitor') / 'observation.json')
    authority['fullNativeBuildReview'] = row(BASE / 'next-native-fetch-resource-cleanup-root-results-v1/actual-build-review.json')
    build_review = read(authority['fullNativeBuildReview']['path'])
    authority['fullNativeBuildSourceIndex'] = build_review['callerSourceIndex']
    authority['fullBuildGeneratedNullSource'] = row(build / 'build/starling-raw.wasm/null.cpp')
    assert build_review['verifiedPassed'] is True
    assert build_review['engine'] == authority['engine'] and build_review['metadata'] == authority['nativeMetadata']
    assert build_review['actualResult'] == authority['fullNativeBuildResult']
    authority['nativeSourceFamilies'] = [authority['fullNativeBuildSourceIndex'],
        row(BASE / 'next-native-portable-source-v6/index.json'),
        row(BASE / 'next-native-fetch-resource-cleanup-candidate-v2/index.json'),
        row(BASE / 'next-module-fileurl-interop-candidate-v2/index.json'),
        row(BASE / 'next-portable-cache-handler-candidate-v2/index.json'),
        row(BASE / 'next-portable-cache-app-build-v1/index.json')]
    refs, by_path = [], {}

    def add(ref):
        assert set(ref) == {'path', 'sha256', 'bytes'}
        assert row(Path(ref['path'])) == ref
        if ref['path'] in by_path:
            assert by_path[ref['path']] == ref
        else:
            refs.append(ref)
            by_path[ref['path']] = ref

    assert len(build_result['sourceCopies']) == 825
    for copy in build_result['sourceCopies']:
        add(copy['source'])
        add(copy['target'])
    assert len(refs) == 1650
    for key in ['fullNativeBuildResult', 'fullNativeBuildObservation', 'fullNativeBuildReview',
                'fullBuildGeneratedNullSource', 'nativeMetadata', 'engine', 'component', 'componentAudit',
                'wrapperPython', 'fullNativeGuardImplementation', 'worldGuardImplementation',
                'constructionDataReview', 'applicationBuildDataReview', 'applicationRootIdentityEvidence']:
        add(authority[key])
    for key in ['actualLibrary', 'actualSavedFrameHeader', 'actualConfigHeader', 'actualConfdefs',
                'patchedSpiderMonkeyEvidence', 'savedFramePatchIndex', 'actualAggregateLock',
                'offlineCargoConfig', 'portableCargoSelection', 'validatedCargoProofCapsule',
                'validatedCargoProofIndex', 'sourceComposition']:
        add(native[key])
    additions = [Path(__file__).resolve(), HERE / 'run-full-native-requests.py', ctor_path,
        ctor_dir / 'actual-construction-review.json', Path(ctor_review['actualOwnerWorldReview']['path']), root / 'result.json', root / 'component-audit.json',
        external / 'started.json', external / 'terminal.json', external / 'world-guard.json',
        Path(authority['worldGuardImplementation']['path']), app_dir / 'actual-build-review-v2.json',
        app_dir / 'actual-build-review.json', app_dir / 'actual-build-owner-tool-review.json',
        app_dir / 'standalone-root-identity.json', app_dir / 'admission.json', app_dir / 'observation.json',
        Path(actor_plan['applicationBuildResult']['path']), Path(actor_plan['applicationInputs']['path'])]
    outer = read(external / 'terminal.json')
    additions += [Path(outer[key]['path']) for key in ['stdout', 'stderr']]
    additions += [Path(ref['path']) for ref in constructor['newSourceEvidence'] + constructor['engineBuildEvidence']]
    for command in construction['commands']:
        assert command['rawExitCode'] == 0 and command['clean'] is True
        additions += [Path(command[key]['path']) for key in ['terminal', 'stdout', 'stderr']]
    catalogue_path = BASE / 'next-portable-cache-app-build-v1/fixture-inputs.json'
    catalogue = read(catalogue_path)
    assert len(catalogue['files']) == 31
    fixture_root = REPO / catalogue['repositoryFixture']
    additions += [fixture_root / ref['path'] for ref in catalogue['files']]
    additions += [Path(ref['path']) for ref in actor_plan['preservedD990FailureBaselines']]
    for path in additions:
        add(row(path))
    authority['nativeProtectedInputs'] = refs
    authority['rootReview'] = (
        'One guest-promise-completion diagnostic full Next regression only after a genuinely reviewed new Promise INIT and bound runtime Source '
        'and unchanged476b22f/f805 app. Fresh genuine825 source-target pairs and31/39/18 current '
        'constructor roles, original47c and b7a world guards before issue and before/final actor. '
        'Original52/80/24/legacy generation/five-stream/two strict browser gates remain mandatory. '
        'Defaultf19d NetLog, no identity input; standard--no-logging-prefix plus prewrite hard8MiB '
        'raw stdout capture, EOF/write/sync/close finalization before digest and later DATA. '
        'Complete capture is independent of failed application gates. Ambiguous/missing/truncated '
        'lane-local markers are unobserved, not private identity/append/TCP/cause proof. '
        'No stock run/retry/filter/nativebuild/construction/extra services/capabilities/adoption. '
        'Old D990 failed c3/f3/8151 reviews are additional protected baselines only.')
    output = Path(actor_plan['outputPrefix'] + '-' + authority['runId'])
    external_output = Path(str(output) + '-external-root')
    receipt = HERE / (authority['runId'] + '-full-world-guard.json')
    assert not output.exists() and not output.is_symlink()
    assert not external_output.exists() and not external_output.is_symlink()
    assert not receipt.exists() and not receipt.is_symlink()
    target = HERE / 'guest-promise-completion-runtime-authority.json'
    for path in [target, HERE / 'runtime-preparation.json']:
        assert not path.exists() and not path.is_symlink()
    world = wrapper.admission(authority, actor_plan, native_guard, world_guard)
    free = wrapper.capacity(actor_plan, authority['rootLaunchMinimumFreeBytes'])
    write_new(target, authority)
    result = dict(state='ROOT_GUEST_PROMISE_COMPLETION_FULL_NEXT_PREPARED_NOT_LAUNCHED_V1',
        authority=row(target), freshSourceTargetDescriptors=1650, totalProtectedDescriptors=len(refs),
        component=component, constructionReview=ctor_review_ref,
        appBuildReview=app_review_ref, metadataFixedValues=31, buildEvidence=39, sourceEvidence=18,
        world=world, freeBytesBeforeIssue=free, actorInvoked=False)
    write_new(HERE / 'runtime-preparation.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
