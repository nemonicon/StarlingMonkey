"""Assemble one guard probe authority from genuine reviewed build/INIT records."""
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
    actor = BASE / 'next-module-fileurl-probe-runtime-candidate-v1'
    plan = read(actor / 'plan.json')
    authority = read(actor / 'root-authority.template.json')
    prior_path = BASE / 'next-module-boundary-runtime-root-results-v1/guard-ca84-first-runtime-authority.json'
    prior = read(prior_path)
    ctor_path = HERE / 'guard-probe-v1-construction-authority.json'
    ctor = read(ctor_path)
    root = Path(ctor['outputRoot'])
    result = read(root / 'result.json')
    review = read(HERE / 'actual-construction-review.json')
    assert review['verifiedPassed'] is result['passed'] is True
    assert review['actualResult'] == row(root / 'result.json')
    assert review['rootAuthority'] == result['rootAuthority'] == row(ctor_path)
    assert result['finalProtection']['unchanged'] is True and result['error'] is None
    authority.update(state='ROOT_FILE_URL_GUARD_PROBE_AUTHORIZED_V1', sourceIndex=row(actor / 'index.json'),
        plan=row(actor / 'plan.json'), runId='guard-ca84-probe-first', ordinaryProbeAllowed=True,
        loopbackServeAllowed=True, fixtureStagingAllowed=True)
    for key in ['engine', 'nativeMetadata', 'metadataExpectedFixedValues', 'engineBuildEvidence']:
        assert ctor[key] == prior[key]
        authority[key] = ctor[key]
    authority['constructionResult'] = row(root / 'result.json')
    authority['constructionCallerIndex'] = ctor['callerIndex']
    authority['constructionDataReview'] = row(HERE / 'actual-construction-review.json')
    authority['component'] = result['artifacts']['component']
    authority['componentAudit'] = result['artifacts']['componentAudit']
    for key, expected in [('expectedComponent', 'component'), ('expectedComponentAudit', 'componentAudit'),
                          ('expectedConstructionResult', 'constructionResult'),
                          ('expectedConstructionDataReview', 'constructionDataReview')]:
        assert plan[key] == authority[expected]
    external = Path(str(root) + '-external-root')
    for key, name in [('constructionRootStarted', 'started.json'), ('constructionRootTerminal', 'terminal.json'),
                      ('constructionWorldGuard', 'world-guard.json')]:
        authority[key] = row(external / name)
    for key in ['fullNativeBuildResult', 'fullNativeBuildObservation', 'fullNativeBuildReview',
                'fullNativeBuildSourceIndex', 'fullBuildGeneratedNullSource', 'worldSourceIndex', 'nativeSourceFamilies']:
        authority[key] = prior[key]
    authority['newSourceEvidence'] = ctor['newSourceEvidence']
    authority['fullBuildGuardImplementation'] = row(BASE / 'next-full-build-runtime-root-results-v1/run-full-native-requests.py')
    authority['worldGuardImplementation'] = prior['worldGuardImplementation']
    refs = list(prior['nativeProtectedInputs'])
    by_path = {r['path']: r for r in refs}
    assert len(by_path) == len(refs) == 1700
    additions = [Path(__file__).resolve(), HERE / 'run-probe.py', ctor_path,
        HERE / 'actual-construction-review.json', HERE / 'actual-owner-world-review.json', HERE / 'actual-package-review.json',
        root / 'result.json', root / 'component-audit.json', external / 'started.json',
        external / 'terminal.json', external / 'world-guard.json',
        Path(authority['fullBuildGuardImplementation']['path']), Path(authority['worldGuardImplementation']['path'])]
    outer = read(external / 'terminal.json')
    additions += [Path(outer[k]['path']) for k in ['stdout', 'stderr']]
    additions += [Path(r['path']) for r in ctor['newSourceEvidence']]
    for command in result['commands']:
        assert command['rawExitCode'] == 0 and command['clean'] is True
        additions += [Path(command[k]['path']) for k in ['terminal', 'stdout', 'stderr']]
    appended = []
    for path in additions:
        ref = row(path)
        if ref['path'] in by_path:
            assert by_path[ref['path']] == ref
        else:
            refs.append(ref)
            appended.append(ref)
            by_path[ref['path']] = ref
    for ref in refs:
        assert row(ref['path']) == ref
    authority['nativeProtectedInputs'] = refs
    authority['rootReview'] = dict(fullNativeAndWholeWorldGuardsRequired=True,
        priorProtectedInputsPreservedVerbatim=1700, appendedGenuineProbeDescriptors=len(appended),
        policy='One guard-only GET with eight fresh physical fixtures and checked fbc1 native loader. '
        'Original0af180/1GiB/WT42/default host flags, no app/browser/Node control/build/construction/retry. '
        'Existing full-native/world functions run before/final without rebinding; no metadata projection. '
        'Earlier Next cache/browser failures remain recorded. A guard-profile pass is safe refusal, not Node parity.')
    output = Path(plan['outputPrefix'] + '-' + authority['runId'])
    assert not output.exists() and not output.is_symlink()
    assert not Path(str(output) + '-external-root').exists() and not Path(str(output) + '-external-root').is_symlink()
    target = HERE / 'guard-ca84-first-runtime-authority.json'
    with target.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    receipt = dict(state='ROOT_SINGLE_GUARD_PROBE_RUNTIME_PREPARED_NOT_LAUNCHED_V1',
        authority=row(target), priorAuthority=row(prior_path), originalProtectedDescriptors=1700,
        appendedProtectedDescriptors=appended, totalProtectedDescriptors=len(refs), actorInvoked=False)
    with (HERE / 'runtime-preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ['state', 'authority', 'originalProtectedDescriptors', 'totalProtectedDescriptors', 'actorInvoked']}))


if __name__ == '__main__':
    main()
