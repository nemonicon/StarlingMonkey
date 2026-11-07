"""Prepare one full Next regression from genuine guarded build/INIT DATA.

JSON and file reads only. Does not import actor code or launch any process.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def row(path):
    path = Path(path)
    assert path.is_absolute() and path.resolve() == path
    assert path.is_file() and not path.is_symlink()
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def read(path):
    return json.loads(Path(path).read_text())


def write_new(path, value):
    with path.open('x') as handle:
        handle.write(json.dumps(value, indent=2) + '\n')


def main():
    prior = BASE / 'next-full-build-runtime-root-results-v1/full02a-first-runtime-authority.json'
    authority = read(prior)
    ctor_dir = BASE / 'next-module-boundary-construction-root-results-v1'
    ctor_authority = ctor_dir / 'guard-next-v1-construction-authority.json'
    constructor = read(ctor_authority)
    root = Path(constructor['outputRoot'])
    result_ref = row(root / 'result.json')
    result = read(result_ref['path'])
    ctor_review_ref = row(ctor_dir / 'actual-construction-review.json')
    ctor_review = read(ctor_review_ref['path'])
    assert ctor_review['verifiedPassed'] is True
    assert ctor_review['actualResult'] == result_ref
    assert ctor_review['rootAuthority'] == row(ctor_authority)
    assert ctor_review['guardImportBehaviorTested'] is False
    assert result['passed'] is True and result['error'] is None
    assert result['finalProtection']['unchanged'] is True
    assert result['rootAuthority'] == row(ctor_authority)
    actor = BASE / 'wasmtime-deployment-guard-candidate-v1'
    plan = read(actor / 'plan.json')
    component = result['artifacts']['component']
    assert component == ctor_review['component'] == row(component['path'])
    assert plan['expectedComponent'] == {k: component[k] for k in ['sha256', 'bytes']}
    authority['sourceIndex'] = row(actor / 'index.json')
    authority['plan'] = row(actor / 'plan.json')
    authority['constructionResult'] = result_ref
    authority['constructionCallerIndex'] = constructor['callerIndex']
    for key in ['component', 'componentAudit', 'inputEntry', 'inputSourceIndex']:
        authority[key] = result['artifacts'][key]
    for key in ['engine', 'nativeMetadata', 'metadataExpectedFixedValues', 'engineBuildEvidence']:
        authority[key] = constructor[key]
        if key != 'metadataExpectedFixedValues':
            assert result['artifacts'][key] == constructor[key]
    external = Path(str(root) + '-external-root')
    authority['constructionOuterTerminal'] = row(external / 'terminal.json')
    authority['constructionWorldGuard'] = row(external / 'world-guard.json')
    authority['runId'] = 'guard-ca84-next-requests-first'
    build = Path(authority['nativeMetadata']['path']).parent
    native = read(authority['nativeMetadata']['path'])
    build_result = read(build / 'result.json')
    authority['fullNativeBuildResult'] = row(build / 'result.json')
    authority['fullNativeBuildObservation'] = row(Path(str(build) + '-root-monitor') / 'observation.json')
    authority['fullNativeBuildReview'] = row(BASE / 'next-module-boundary-native-root-results-v1/actual-build-review.json')
    authority['fullNativeBuildSourceIndex'] = row(BASE / 'next-native-portable-build-preparation-v4/index.json')
    authority['fullBuildGeneratedNullSource'] = row(build / 'build/starling-raw.wasm/null.cpp')
    review = read(authority['fullNativeBuildReview']['path'])
    assert review['verifiedPassed'] is True
    for key, actual in [('actualResult', 'fullNativeBuildResult'), ('actualRootObservation', 'fullNativeBuildObservation'),
                        ('engine', 'engine'), ('metadata', 'nativeMetadata'), ('callerSourceIndex', 'fullNativeBuildSourceIndex')]:
        assert review[key] == authority[actual]
    assert len(build_result['sourceCopies']) == 825
    authority['nativeSourceFamilies'] = [authority['fullNativeBuildSourceIndex'],
        row(BASE / 'next-module-boundary-native-root-results-v1/source-stage-review/index.json'),
        row(BASE / 'next-module-fileurl-boundary-candidate-v1/index.json')]
    refs = []
    by_path = {}

    def add(ref):
        assert set(ref) == {'path', 'sha256', 'bytes'}
        assert row(ref['path']) == ref
        if ref['path'] in by_path:
            assert by_path[ref['path']] == ref
        else:
            by_path[ref['path']] = ref
            refs.append(ref)

    # Use actual copy records; support/embedding paths are not assumed to live
    # under the native-source directory, and no old paths are substituted.
    for copy in build_result['sourceCopies']:
        add(copy['source'])
        add(copy['target'])
    assert len(refs) == 1650
    for key in ['fullNativeBuildResult', 'fullNativeBuildObservation', 'fullNativeBuildReview',
                'fullBuildGeneratedNullSource', 'nativeMetadata']:
        add(authority[key])
    for key in ['actualLibrary', 'actualSavedFrameHeader', 'actualConfigHeader', 'actualConfdefs',
                'patchedSpiderMonkeyEvidence', 'savedFramePatchIndex', 'actualAggregateLock',
                'offlineCargoConfig', 'portableCargoSelection', 'validatedCargoProofCapsule',
                'validatedCargoProofIndex', 'sourceComposition']:
        add(native[key])
    additions = [Path(__file__).resolve(), HERE / 'run-full-native-requests.py', ctor_authority,
                 ctor_dir / 'actual-construction-review.json', ctor_dir / 'actual-owner-world-review.json',
                 ctor_dir / 'actual-package-review.json', root / 'result.json', root / 'component-audit.json',
                 external / 'terminal.json', external / 'world-guard.json']
    outer = read(external / 'terminal.json')
    additions += [Path(outer[k]['path']) for k in ['stdout', 'stderr']]
    additions += [Path(r['path']) for r in constructor['newSourceEvidence']]
    for command in result['commands']:
        assert command['rawExitCode'] == 0 and command['clean'] is True
        additions += [Path(command[k]['path']) for k in ['terminal', 'stdout', 'stderr']]
    for path in additions:
        add(row(path))
    authority['nativeProtectedInputs'] = refs
    authority['rootReview'] = (
        'One first full Next regression on genuine guarded49013f31 component/ca84 engine/e674 metadata. '
        'Same entry73b/1e49,2181-file app, standard13@0.2.10 world and all four V9 actor executables; '
        'normal BrowserV3 with extra diagnostic CDP enabled. Original24HTTP/cache1to2/five-stream/'
        'two strict-browser/80supplemental gates,600-second owner and1GiB launch guard unchanged. '
        'This evaluates a checked invalid-referrer boundary; it does not implement CJS/fileURL '
        'interop, cache coherence or an action-abort fix. Existing failures remain failed. '
        'No construction/build, new host capability, app rewrite, retry, filtering, extended cohort '
        'or production adoption. Genuine source/target refs derived from actual825 copy records; '
        'whole build tool trees were verified by build DATA review and are not rescanned here.'
    )
    output = Path(plan['outputPrefix'] + '-' + authority['runId'])
    assert not output.exists() and not Path(str(output) + '-external-root').exists()
    assert not (HERE / (authority['runId'] + '-full-world-guard.json')).exists()
    target = HERE / 'guard-ca84-first-runtime-authority.json'
    write_new(target, authority)
    receipt = dict(state='ROOT_GUARDED_NEXT_RUNTIME_AUTHORITY_PREPARED_NOT_LAUNCHED_V1',
                   priorAuthority=row(prior), authority=row(target), component=component,
                   constructionReview=ctor_review_ref, constructionResult=result_ref,
                   sourceTargetDescriptors=1650, totalProtectedDescriptors=len(refs),
                   freshBuildEvidenceCount=len(authority['engineBuildEvidence']), actorInvoked=False)
    write_new(HERE / 'runtime-preparation.json', receipt)
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
