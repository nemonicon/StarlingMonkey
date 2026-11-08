"""UNBOUND Root-only stock wasmCloud full-contract JSON preparation; explicit origin, no actor or port operation."""
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[4]


def read(path):
    return json.loads(Path(path).read_text())


def write_new(path, value):
    with path.open('x') as handle:
        handle.write(json.dumps(value, indent=2) + '\n')


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 3 and sys.argv[1] == '--self-origin'
    wrapper_path = HERE / 'run-full-native.py'
    spec = importlib.util.spec_from_file_location('wasmcloud_full_root_admission', wrapper_path)
    cold = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cold)
    cold.require_bound()  # No original helper/input/output/port/action before a genuine actor Source pin.
    origin = cold.canonical_self_origin(sys.argv[2])
    native_guard, world_guard = cold.context()
    row = cold.row
    actor = cold.ACTOR
    plan = read(actor / 'plan.json')
    cold.capacity(plan, 1073741824)
    ctor_dir = BASE / 'next-fetch-resource-cleanup-next-construction-root-results-v1'
    ctor_path = ctor_dir / 'real-next-construction-authority.json'
    constructor = read(ctor_path)
    root = Path(constructor['outputRoot'])
    construction_ref = row(root / 'result.json')
    construction = read(root / 'result.json')
    policy = plan['requiredExternalRootAdmission']
    ctor_review_ref = row(ctor_dir / 'actual-construction-review.json')
    assert ctor_review_ref == policy['constructionReview']
    ctor_review = read(ctor_review_ref['path'])
    assert ctor_review['state'] == 'COORDINATED_REAL_NEXT_INTEROP_COMPONENT_INIT_DATA_REVIEW_PASSED_V1'
    assert ctor_review['verifiedPassed'] is ctor_review['completeReturnedImportAuditVerified'] is True
    assert 'deployedCompletionDiagnosticObserved' not in ctor_review
    assert ctor_review['complementaryOwnerWorldReview'] == row(ctor_dir / 'actual-construction-owner-review.json')
    assert ctor_review['actualResult'] == construction_ref and ctor_review['rootAuthority'] == row(ctor_path)
    assert construction['entryMode'] == 'real-next' and construction['passed'] is True and construction['error'] is None
    assert construction['finalProtection']['unchanged'] is True
    assert len(constructor['metadataExpectedFixedValues']) == 31
    assert len(constructor['engineBuildEvidence']) == 39 and len(constructor['newSourceEvidence']) == 18
    # Build a new authority from actual constructor/build rows, not an old permission/protection array.
    authority = read(actor / 'root-authority-template.json')
    authority.update(sourceIndex=row(actor / 'index.json'), plan=row(actor / 'plan.json'),
                     runId='wasmcloud-full-476b-first', selfOrigin=origin, unissued=False,
                     coldNextGuestAllowed=True, localhostServeAllowed=True, configInspectAllowed=True,
                     fullContractClientAllowed=True, browserAllowed=True,
                     rootLaunchMinimumFreeBytes=1073741824, wrapperPython=cold.PYTHON,
                     fullNativeGuardImplementation=cold.FULL_GUARD,
                     worldGuardImplementation=cold.WORLD_GUARD,
                     rootPreparation=row(Path(__file__).resolve()), rootWrapper=row(wrapper_path),
                     constructionResult=construction_ref, constructionCallerIndex=constructor['callerIndex'],
                     constructionDataReview=ctor_review_ref)
    for key in ['component', 'componentAudit', 'inputEntry', 'inputSourceIndex', 'adapter']:
        authority[key] = construction['artifacts'][key]
    for key in ['engine', 'nativeMetadata', 'metadataExpectedFixedValues', 'engineBuildEvidence']:
        authority[key] = constructor[key]
    authority['applicationInputs'] = plan['applicationInputs']
    authority['applicationSource'] = plan['applicationSource']
    authority['wash'] = dict(path='/private/tmp/starling-node-compat/wasmcloud/bin/wash-2.11.0-aarch64-apple-darwin',
                             **plan['expectedArtifacts']['wash'])
    authority['applicationBuildDataReview'] = policy['applicationBuildReview']
    authority['applicationRootIdentityEvidence'] = policy['applicationRootIdentity']
    external = Path(str(root) + '-external-root')
    authority['constructionOuterTerminal'] = row(external / 'terminal.json')
    authority['constructionWorldGuard'] = row(external / 'world-guard.json')
    authority['worldSourceIndex'] = constructor['worldSourceIndex']
    authority['worldInputs'] = [ref for ref in constructor['newSourceEvidence'] if ref['path'].endswith('.wit')]
    assert len(authority['worldInputs']) == 8
    build = Path(authority['nativeMetadata']['path']).parent
    metadata = read(authority['nativeMetadata']['path'])
    build_result = read(build / 'result.json')
    authority['fullNativeBuildResult'] = row(build / 'result.json')
    authority['fullNativeBuildObservation'] = row(Path(str(build) + '-root-monitor') / 'observation.json')
    authority['fullNativeBuildReview'] = policy['fullNativeBuildReview']
    build_review = read(authority['fullNativeBuildReview']['path'])
    authority['fullNativeBuildSourceIndex'] = build_review['callerSourceIndex']
    authority['fullBuildGeneratedNullSource'] = row(build / 'build/starling-raw.wasm/null.cpp')
    assert build_review['verifiedPassed'] is True
    assert build_review['actualResult'] == authority['fullNativeBuildResult']
    assert build_review['engine'] == authority['engine'] and build_review['metadata'] == authority['nativeMetadata']
    authority['nativeSourceFamilies'] = [authority['fullNativeBuildSourceIndex'],
        row(BASE / 'next-native-portable-source-v6/index.json'),
        row(BASE / 'next-native-fetch-resource-cleanup-candidate-v2/index.json'),
        row(BASE / 'next-module-fileurl-interop-candidate-v2/index.json'),
        row(BASE / 'next-portable-cache-handler-candidate-v2/index.json'),
        row(BASE / 'next-portable-cache-app-build-v1/index.json')]
    refs, by_path = [], {}

    def add(ref):
        assert set(ref) == {'path', 'sha256', 'bytes'} and row(Path(ref['path'])) == ref
        if ref['path'] in by_path:
            assert by_path[ref['path']] == ref
        else:
            refs.append(ref); by_path[ref['path']] = ref

    assert len(build_result['sourceCopies']) == 825
    for copy in build_result['sourceCopies']:
        add(copy['source']); add(copy['target'])
    assert len(refs) == 1650
    for key in ['fullNativeBuildResult', 'fullNativeBuildObservation', 'fullNativeBuildReview',
                'fullBuildGeneratedNullSource', 'nativeMetadata', 'engine', 'component', 'componentAudit',
                'constructionOuterTerminal', 'constructionWorldGuard', 'worldGuardImplementation',
                'fullNativeGuardImplementation', 'wrapperPython', 'rootPreparation', 'rootWrapper',
                'constructionDataReview', 'applicationBuildDataReview', 'applicationRootIdentityEvidence']:
        add(authority[key])
    for key in ['actualLibrary', 'actualSavedFrameHeader', 'actualConfigHeader', 'actualConfdefs',
                'patchedSpiderMonkeyEvidence', 'savedFramePatchIndex', 'actualAggregateLock',
                'offlineCargoConfig', 'portableCargoSelection', 'validatedCargoProofCapsule',
                'validatedCargoProofIndex', 'sourceComposition']:
        add(metadata[key])
    app_dir = BASE / 'next-portable-cache-app-build-root-results-v1'
    additions = [ctor_path, ctor_dir / 'actual-construction-owner-review.json', root / 'result.json',
        external / 'started.json', app_dir / 'actual-build-review.json', app_dir / 'actual-build-owner-tool-review.json',
        app_dir / 'admission.json', app_dir / 'observation.json', Path(plan['applicationBuildResult']['path']),
        Path(plan['applicationInputs']['path'])]
    outer = read(external / 'terminal.json')
    additions += [Path(outer[key]['path']) for key in ['stdout', 'stderr']]
    additions += [Path(ref['path']) for ref in constructor['newSourceEvidence'] + constructor['engineBuildEvidence']]
    for command in construction['commands']:
        assert command['rawExitCode'] == 0 and command['clean'] is True
        additions += [Path(command[key]['path']) for key in ['terminal', 'stdout', 'stderr']]
    catalogue = read(BASE / 'next-portable-cache-app-build-v1/fixture-inputs.json')
    assert len(catalogue['files']) == 31
    additions += [(REPO / catalogue['repositoryFixture']) / ref['path'] for ref in catalogue['files']]
    for path in additions:
        add(row(path))
    authority['nativeProtectedInputs'] = refs
    authority['rootReview'] = ('One stock wasmCloud2.11.0 full original contract on actualD990/476b/22f and f805 app. '
        'Root supplies the sole canonical literal nondefault loopback self-origin; this preparer never selects or binds a port. '
        'Actor must bind that exact port once through effective config inspection, then release immediately before its single dev launch. '
        'Only that scheme/host/port is allowed for self HTTP; no wildcard, resolver, fallback, retry or other network grant. '
        'Fresh825 Source/target pairs and genuine31/39/18 roles, original47c full-native and b7 whole-world guards '
        'before issue and before/final actor; genuine A9256 missing diagnostic field remains absent. '
        'Original shared24HTTP/52nonce/80supp/legacy generation/stream/two strict browser gates remain unchanged; '
        'raw1 remains failure and ordinary data publication precedes validation. Two mounts, physicalreadonly app '
        '(not readonly descriptor rights), fresh ownedcache and exact3 environment entries. '
        'Cold readiness logstat is not a lifetime stdout bound; no capture-complete/privateStore/affinity/cause/reliability claim. '
        'No host modifications/new services/compiler/construction/download/install/failure overwrite or production promotion.')
    output = Path(plan['outputPrefix'] + '-' + authority['runId'])
    target = HERE / 'full-contract-runtime-authority.json'
    prep_result = HERE / 'runtime-preparation.json'
    receipt = HERE / (authority['runId'] + '-full-world-guard.json')
    for path in [output, Path(str(output) + '-external-root'), receipt, target, prep_result]:
        assert not path.exists() and not path.is_symlink()
    world = cold.admission(authority, plan, native_guard, world_guard)
    free = cold.capacity(plan, authority['rootLaunchMinimumFreeBytes'])
    write_new(target, authority)
    result = dict(state='ROOT_WASMCLOUD_FULL_CONTRACT_PREPARED_NOT_LAUNCHED_V1', authority=row(target),
                  freshSourceTargetDescriptors=1650, totalProtectedDescriptors=len(refs),
                  metadataFixedValues=31, buildEvidence=39, sourceEvidence=18,
                  world=world, selfOrigin=origin, portSelectedOrBoundByPreparer=False, freeBytesBeforeIssue=free, actorInvoked=False)
    write_new(prep_result, result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
