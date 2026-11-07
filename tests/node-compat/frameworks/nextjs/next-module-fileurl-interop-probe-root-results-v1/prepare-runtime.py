"""Derive one interop GET authority from genuine reviewed construction/build DATA."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def read(path):
    return json.loads(Path(path).read_text())


def main():
    actor = BASE / 'next-module-fileurl-interop-probe-runtime-candidate-v1'
    plan = read(actor / 'plan.json')
    assert plan['prospectiveActualBindingsPending'] is False
    authority = read(actor / 'root-authority.template.json')
    ctor_path = HERE / 'interop-probe-v2-construction-authority.json'
    ctor = read(ctor_path)
    root = Path(ctor['outputRoot'])
    result = read(root / 'result.json')
    review = read(HERE / 'actual-construction-review.json')
    assert review['verifiedPassed'] is result['passed'] is True
    assert review['actualResult'] == row(root / 'result.json')
    assert review['rootAuthority'] == result['rootAuthority'] == row(ctor_path)
    assert result['entryMode'] == 'interop'
    assert result['finalProtection']['unchanged'] is True and result['error'] is None
    authority.update(state='ROOT_FILE_URL_INTEROP_PROBE_AUTHORIZED_V1', sourceIndex=row(actor / 'index.json'),
        plan=row(actor / 'plan.json'), runId='interop-2251-probe-first', ordinaryProbeAllowed=True,
        loopbackServeAllowed=True, fixtureStagingAllowed=True)
    for key in ['engine', 'nativeMetadata', 'metadataExpectedFixedValues', 'engineBuildEvidence']:
        authority[key] = ctor[key]
    authority['constructionResult'] = row(root / 'result.json')
    authority['constructionCallerIndex'] = ctor['callerIndex']
    authority['constructionDataReview'] = row(HERE / 'actual-construction-review.json')
    authority['component'] = result['artifacts']['component']
    authority['componentAudit'] = result['artifacts']['componentAudit']
    for key, expected in [('expectedComponent', 'component'), ('expectedComponentAudit', 'componentAudit'),
                          ('expectedConstructionResult', 'constructionResult'),
                          ('expectedConstructionDataReview', 'constructionDataReview'),
                          ('expectedEngine', 'engine'), ('expectedNativeMetadata', 'nativeMetadata')]:
        assert plan[key] == authority[expected]
    assert plan['constructionCallerIndex'] == ctor['callerIndex']
    external = Path(str(root) + '-external-root')
    for key, name in [('constructionRootStarted', 'started.json'), ('constructionRootTerminal', 'terminal.json'),
                      ('constructionWorldGuard', 'world-guard.json')]:
        authority[key] = row(external / name)
    build = Path(authority['nativeMetadata']['path']).parent
    native = read(authority['nativeMetadata']['path'])
    build_result = read(build / 'result.json')
    authority['fullNativeBuildResult'] = row(build / 'result.json')
    authority['fullNativeBuildObservation'] = row(Path(str(build) + '-root-monitor') / 'observation.json')
    authority['fullNativeBuildReview'] = plan['fullBuildReview']
    build_review = read(authority['fullNativeBuildReview']['path'])
    authority['fullNativeBuildSourceIndex'] = build_review['callerSourceIndex']
    authority['fullBuildGeneratedNullSource'] = row(build / 'build/starling-raw.wasm/null.cpp')
    assert build_review['verifiedPassed'] is True
    for key, actual in [('actualResult', 'fullNativeBuildResult'), ('actualRootObservation', 'fullNativeBuildObservation'),
                        ('engine', 'engine'), ('metadata', 'nativeMetadata')]:
        assert build_review[key] == authority[actual]
    assert len(build_result['sourceCopies']) == 825
    authority['nativeSourceFamilies'] = [authority['fullNativeBuildSourceIndex'],
        row(BASE / 'next-native-portable-source-v4/index.json'),
        row(BASE / 'next-module-fileurl-interop-candidate-v2/index.json')]
    authority['worldSourceIndex'] = ctor['worldSourceIndex']
    authority['newSourceEvidence'] = ctor['newSourceEvidence']
    authority['fullBuildGuardImplementation'] = row(BASE / 'next-full-build-runtime-root-results-v1/run-full-native-requests.py')
    authority['worldGuardImplementation'] = row(BASE / 'peer-disconnect-root-results-v3/launch-peer-v3-construction.py')
    refs = []
    by_path = {}

    def add(ref):
        assert set(ref) == {'path', 'sha256', 'bytes'}
        assert row(ref['path']) == ref
        if ref['path'] in by_path:
            assert by_path[ref['path']] == ref
        else:
            refs.append(ref)
            by_path[ref['path']] = ref

    # Fresh actual copy records, including support and embedding destinations.
    # No old nativeProtectedInputs array or path substitution is consumed.
    for copy in build_result['sourceCopies']:
        add(copy['source'])
        add(copy['target'])
    assert len(refs) == 1650
    for key in ['fullNativeBuildResult', 'fullNativeBuildObservation', 'fullNativeBuildReview',
                'fullBuildGeneratedNullSource', 'nativeMetadata', 'engine']:
        add(authority[key])
    for key in ['actualLibrary', 'actualSavedFrameHeader', 'actualConfigHeader', 'actualConfdefs',
                'patchedSpiderMonkeyEvidence', 'savedFramePatchIndex', 'actualAggregateLock',
                'offlineCargoConfig', 'portableCargoSelection', 'validatedCargoProofCapsule',
                'validatedCargoProofIndex', 'sourceComposition']:
        add(native[key])
    additions = [Path(__file__).resolve(), HERE / 'run-probe.py', ctor_path,
        HERE / 'actual-construction-review.json', HERE / 'actual-owner-world-review.json', HERE / 'actual-package-review.json',
        root / 'result.json', root / 'component-audit.json', external / 'started.json',
        external / 'terminal.json', external / 'world-guard.json',
        Path(authority['fullBuildGuardImplementation']['path']), Path(authority['worldGuardImplementation']['path'])]
    outer = read(external / 'terminal.json')
    additions += [Path(outer[key]['path']) for key in ['stdout', 'stderr']]
    additions += [Path(ref['path']) for ref in ctor['newSourceEvidence'] + ctor['engineBuildEvidence']]
    for command in result['commands']:
        assert command['rawExitCode'] == 0 and command['clean'] is True
        additions += [Path(command[key]['path']) for key in ['terminal', 'stdout', 'stderr']]
    for path in additions:
        add(row(path))
    authority['nativeProtectedInputs'] = refs
    authority['rootReview'] = dict(fullNativeAndWholeWorldGuardsRequired=True,
        freshActualSourceTargetDescriptors=1650, totalProtectedDescriptors=len(refs),
        policy='One interop-only GET with eight fresh physical fixtures and corrected40ee/2251 native loader. '
        'Original180s/1GiB/Wasmtime42/default flags and16-case contract unchanged. '
        'No app/browser/Node control/build/construction/retry. Genuine existing full-native/world '
        'functions before/final without rebinding or metadata projection. Earlier Next/cache/browser '
        'failures remain failed. A probe pass establishes only the declared interoperability subset.')
    output = Path(plan['outputPrefix'] + '-' + authority['runId'])
    external_output = Path(str(output) + '-external-root')
    guard_receipt = HERE / (authority['runId'] + '-full-native-world-guard.json')
    assert not output.exists() and not output.is_symlink()
    assert not external_output.exists() and not external_output.is_symlink()
    assert not guard_receipt.exists() and not guard_receipt.is_symlink()
    target = HERE / 'interop-2251-first-runtime-authority.json'
    with target.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    receipt = dict(state='ROOT_SINGLE_INTEROP_PROBE_RUNTIME_PREPARED_NOT_LAUNCHED_V1',
        authority=row(target), sourceTargetDescriptors=1650,
        totalProtectedDescriptors=len(refs), actorInvoked=False)
    with (HERE / 'runtime-preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
