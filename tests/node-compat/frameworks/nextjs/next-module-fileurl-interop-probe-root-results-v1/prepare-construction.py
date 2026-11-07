"""Bind accepted corrected build DATA to one interop-only INIT construction."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
WORK = Path('/private/tmp/starling-node-compat/next-native-intl-build-interop-rooted825-first')
ROOT_LOGS = Path(str(WORK) + '-root-monitor')


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    prior = BASE / 'next-module-fileurl-probe-root-results-v1/guard-probe-v1-construction-authority.json'
    authority = json.loads(prior.read_text())
    review_path = BASE / 'next-module-fileurl-interop-native-root-results-v2/actual-build-review.json'
    assert row(review_path)['sha256'] == 'b9aad169f6cb91d9dfacc2484a122f977a9407182f46b889e7439e995842fafa'
    review = json.loads(review_path.read_text())
    assert review['verifiedPassed'] is True
    assert review['state'] == 'INDEPENDENT_PORTABLE_NEXT_INTL_NATIVE_BUILD_DATA_REVIEW_PASSED_V1'
    caller = BASE / 'next-module-fileurl-interop-probe-construction-v2'
    plan = json.loads((caller / 'plan.json').read_text())
    assert set(plan['entries']) == {'interop'}
    assert plan['expectedEngineForRootAuthority'] == review['engine'] == row(WORK / 'componentize-source/lib/starlingmonkey_embedding.wasm')
    assert plan['expectedNativeMetadataForRootAuthority'] == review['metadata'] == row(WORK / 'metadata.json')
    authority['callerIndex'] = row(caller / 'index.json')
    authority['entryMode'] = 'interop'
    authority['runId'] = 'interop-2251-first'
    authority['outputRoot'] = plan['outputPrefix'] + '-interop-' + authority['runId']
    authority['engine'] = review['engine']
    authority['nativeMetadata'] = review['metadata']
    metadata = json.loads((WORK / 'metadata.json').read_text())
    fixed_keys = list(authority['metadataExpectedFixedValues'])
    assert len(fixed_keys) == 31
    authority['metadataExpectedFixedValues'] = {key: metadata[key] for key in fixed_keys}
    assert metadata['engine'] == authority['engine']
    assert metadata['nativePolicyInputCount'] == 435
    assert metadata['buildSupportInputCount'] == 387
    assert metadata['embeddingInputCount'] == 3
    assert metadata['engineExecuted'] is False and metadata['guestExecuted'] is False
    builder = BASE / 'next-native-portable-build-preparation-v6'
    # These are fresh actual-build roles, not substituted path strings in old DATA.
    evidence_paths = [
        WORK / 'result.json', ROOT_LOGS / 'observation.json', review_path,
        ROOT_LOGS / 'authority.issued.json', ROOT_LOGS / 'terminal.json',
        ROOT_LOGS / 'started.json', ROOT_LOGS / 'stdout.log', ROOT_LOGS / 'stderr.log',
        WORK / 'build/compile_commands.json',
        WORK / 'results/ninja-commands/command.combined.log', WORK / 'protection-before.json',
        builder / 'run.py', builder / 'index.json', builder / 'plan.json',
        WORK / 'configured-inputs.json',
    ]
    for phase in ('rust-version', 'cargo-version', 'rust-sysroot', 'configure', 'build', 'ninja-commands'):
        phase_root = WORK / 'results' / phase
        evidence_paths.extend([
            phase_root / 'owned-monitor/terminal.json', phase_root / 'worker-result.json',
            phase_root / 'owned-monitor/stdout.log', phase_root / 'owned-monitor/stderr.log',
        ])
    authority['engineBuildEvidence'] = [row(path) for path in evidence_paths]
    assert len(authority['engineBuildEvidence']) == 39
    assert review['actualResult'] == authority['engineBuildEvidence'][0]
    assert review['actualRootObservation'] == authority['engineBuildEvidence'][1]
    assert review['issuedAuthority'] == authority['engineBuildEvidence'][3]
    assert review['outerOwner']['terminal'] == authority['engineBuildEvidence'][4]
    assert review['recipe'] == authority['engineBuildEvidence'][11]
    assert review['callerSourceIndex'] == authority['engineBuildEvidence'][12]
    world = Path(plan['worldSourceIndex']['path'])
    wit = sorted(world.parent.rglob('*.wit'))
    assert len(wit) == 8
    authority['newSourceEvidence'] = [plan['inputSourceIndex']] + [row(path) for path in wit] + [
        plan['worldSourceIndex'], authority['callerIndex'], row(builder / 'index.json')]
    assert len(authority['newSourceEvidence']) == 12
    authority['worldSourceIndex'] = plan['worldSourceIndex']
    authority['nativeProfileLabel'] = (
        'Genuine corrected40ee RootedString435/387/3 full native build:80 DB rows '
        '(79C++/1C including generatedempty null.cpp), separateembeddingC++, '
        'freshlockedRust and previouslybuilt pinnedSpiderMonkey library; build DATA b9aa accepted.'
    )
    authority['completion'] = 'Unissued interop16 INIT construction; no component or deployed behavior yet.'
    authority['rootReview'] = (
        'One interop-only INIT construction from accepted2251/afb corrected40ee full build, '
        'new sealed CtorV2 and unchangedc355/a53 sixteen-case contract. The heldf3/failed25c '
        'constructor remains unexecuted and unchanged. Three genericV6 executables, '
        'private61685/d30/canonical8025/std13, original2400/1800/120 caps and1GiB start. '
        'No application/fixture mount, Next bootstrap, ordinary export, deployed import, '
        'filesystem probe, HTTP or entropy at INIT. Actual deployed behavior requires '
        'separate accepted construction DATA and a future one-GET runtime authority.'
    )
    for ref in authority['engineBuildEvidence'] + authority['newSourceEvidence']:
        assert row(ref['path']) == ref
    assert not Path(authority['outputRoot']).exists()
    assert not Path(authority['outputRoot'] + '-external-root').exists()
    target = HERE / 'interop-probe-v2-construction-authority.json'
    with target.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    receipt = dict(state='ROOT_INTEROP16_PROBE_INIT_PREPARED_NOT_LAUNCHED_V2',
        authority=row(target), priorAuthority=row(prior), acceptedBuildReview=row(review_path),
        caller=authority['callerIndex'], inputSource=plan['inputSourceIndex'],
        inputEntry=plan['entries']['interop'], fixtureMounted=False, actorInvoked=False)
    with (HERE / 'construction-preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
