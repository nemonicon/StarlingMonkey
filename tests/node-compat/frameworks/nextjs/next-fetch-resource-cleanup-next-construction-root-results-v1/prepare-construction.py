"""Bind accepted corrected build DATA to one real-Next-only INIT construction after the accepted interop gate."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
WORK = Path('/private/tmp/starling-node-compat/next-native-intl-build-fetch-cleanup825-first')
ROOT_LOGS = Path(str(WORK) + '-root-monitor')


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def checked(ref):
    path = Path(ref['path'])
    assert path.is_absolute() and path.resolve() == path and path.is_file() and path.stat().st_nlink == 1
    assert row(path) == ref
    return path


def family(ref):
    path = checked(ref)
    index = json.loads(path.read_text())
    files, directories = {'index.json'}, set()
    for item in index['files']:
        rel = Path(item['path'])
        assert not rel.is_absolute() and '..' not in rel.parts and rel.as_posix() == item['path'] and item['path'] not in files
        files.add(item['path'])
        directories.update(q.as_posix() for q in rel.parents if q != Path('.'))
        checked(dict(path=str(path.parent / rel), sha256=item['sha256'], bytes=item['bytes']))
    nodes = list(path.parent.rglob('*'))
    assert not any(p.is_symlink() for p in nodes) and all(p.is_file() or p.is_dir() for p in nodes)
    assert {p.relative_to(path.parent).as_posix() for p in nodes if p.is_file()} == files
    assert {p.relative_to(path.parent).as_posix() for p in nodes if p.is_dir()} == directories


def main():
    prior = BASE / 'next-module-fileurl-probe-root-results-v1/guard-probe-v1-construction-authority.json'
    authority = json.loads(prior.read_text())
    review_path = BASE / 'next-native-fetch-resource-cleanup-root-results-v1/actual-build-review.json'
    assert row(review_path)['sha256'] == '41857258d4da6f9fc47c8fbce60fb8818335d6ab5607c1d77f3e2c5742da3b72'
    review = json.loads(review_path.read_text())
    assert review['verifiedPassed'] is True
    assert review['state'] == 'INDEPENDENT_PORTABLE_NEXT_INTL_NATIVE_BUILD_DATA_REVIEW_PASSED_V1'
    caller = BASE / 'next-fetch-resource-cleanup-next-construction-v1'
    assert row(caller / 'index.json')['sha256'] == '7cf0b07f8025e3a3647ed827e42cc122a1903d4cc8b95525f6eed4770a13a3c8'
    family(row(caller / 'index.json'))
    plan = json.loads((caller / 'plan.json').read_text())
    family(plan['inputSourceIndex'])
    family(plan['worldSourceIndex'])
    assert set(plan['entries']) == {'real-next'}
    assert plan['expectedEngineForRootAuthority'] == review['engine'] == row(WORK / 'componentize-source/lib/starlingmonkey_embedding.wasm')
    assert plan['expectedNativeMetadataForRootAuthority'] == review['metadata'] == row(WORK / 'metadata.json')
    authority['callerIndex'] = row(caller / 'index.json')
    authority['entryMode'] = 'real-next'
    authority['runId'] = 'cleanup-476b-first'
    authority['outputRoot'] = plan['outputPrefix'] + '-real-next-' + authority['runId']
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
    # These are extra policy keys in the new selector, not implemented by the unchanged generic actor.
    assert plan['requiredCoordinatedFullBuildReviewForRootAuthority'] == row(review_path)
    assert plan['expectedNativeMetadataFixedValuesForRootAuthority'] is None
    assert plan['completeReturnedImportAuditRequired'] is True and plan['expectedReturnedImportFunctionCount'] is None
    assert metadata['metadataKind'] == plan['nativeMetadataKindRequiredInRootFixedValues']
    cleanup_index = plan['requiredCleanupSourceIndex']
    family(cleanup_index)
    cleanup_root = Path(cleanup_index['path']).parent
    cleanup = json.loads(checked(cleanup_index).read_text())
    assert cleanup['state'] == 'FETCH_RESOURCE_CLEANUP_MINIMAL_NODISCARD_SOURCE_HELD_V2'
    version = json.loads((cleanup_root / 'version-manifest.json').read_text())
    cleanup_after = plan['requiredCleanupAfterimageForRootAuthority']
    loader_after = plan['requiredInheritedModuleLoaderAfterimageForRootAuthority']
    assert version['after'] == cleanup_after and version['currentBaseLoaderSha256'] == loader_after['sha256']
    for name, ref in [('builtins/web/fetch/request-response.cpp', cleanup_after), ('runtime/script_loader.cpp', loader_after)]:
        checked(ref)
        selected = [r for r in metadata['nativePolicyInputManifest'] if r['path'] == name]
        compiled = [r for r in metadata['compiledAfterInputs'] if r['path'] == str(WORK / 'native-source' / name)]
        assert len(selected) == len(compiled) == 1
        assert all(selected[0][k] == compiled[0][k] == ref[k] for k in ['sha256', 'bytes'])
        checked(compiled[0])
    source_review_ref = plan['requiredFullBuildSourceReview']
    source_review = json.loads(checked(source_review_ref).read_text())
    assert source_review['verifiedPassed'] is True
    policy_refs = [cleanup_index, cleanup_after, loader_after, row(review_path), source_review_ref]
    # This new selector requires the completed interop profile on these exact native roles.
    # The generic constructor does not enforce this prerequisite; this Root preparer does.
    interop_ref = plan['requiredInteropRuntimeReviewForRootAuthority']
    assert interop_ref['sha256'] == '55a255e7fd932133b144e32e7c7c26ecb31ad3403a5a0b8112f13c67fef13b17'
    interop = json.loads(checked(interop_ref).read_text())
    assert interop['state'] == 'COORDINATED_INTEROP_SELECTED_PROFILE_RUNTIME_DATA_REVIEW_PASSED_V1'
    assert all(interop[key] is True for key in (
        'verifiedPassed', 'all16Passed', 'interopProfileMatched', 'oneGet',
        'cleanupGenerationSelected', 'cjsInteropSourceSelected', 'bodyDecodedEqualsResultPayload'))
    assert type(interop['caseCount']) is int and interop['caseCount'] == 16
    assert type(interop['actualGetRequests']) is int and interop['actualGetRequests'] == 1
    assert type(interop['status']) is int and interop['status'] == 200
    assert interop['engine'] == authority['engine'] and interop['nativeMetadata'] == authority['nativeMetadata']
    assert interop['fullNativeBuildReview'] == row(review_path)
    assert interop['nativeLoaderSourceSha256'] == loader_after['sha256']
    assert interop['selectedRequestResponseSha256'] == cleanup_after['sha256']
    assert interop['errors'] == []
    assert all(interop[key] is False for key in (
        'nodeControlExecuted', 'nodeCompatibilityAccepted', 'nativeResourceCountsProved',
        'allHttpCleanupProved', 'fullNextAccepted', 'fullNextAcceptance', 'adoption',
        'nodeParityProved', 'nativeTaskBranchesProved', 'postAbortCauseProved'))
    assert interop['actualPublicFetchLifecycleResult'] is None
    family(interop['sourceIndex'])
    interop_result = json.loads(checked(interop['actualResult']).read_text())
    interop_authority = json.loads(checked(interop['rootAuthority']).read_text())
    assert interop_result['rootAuthority'] == interop['rootAuthority']
    for key in ('sourceIndex', 'component', 'engine', 'nativeMetadata'):
        assert interop_result[key] == interop_authority[key] == interop[key]
    assert interop_authority['fullNativeBuildReview'] == row(review_path)
    assert interop_result['interopProfileMatched'] is True and interop_result['inputsPreserved'] is True
    assert interop_result['fixtureCopyPreserved'] is True and interop_result['observationsValid'] is True
    assert interop_result['errors'] == [] and interop_result['validation']['cases'] == 16
    response = interop_result['response']
    assert response['method'] == 'GET' and response['status'] == 200 and response['complete'] is True
    assert response['overflow'] is False and response['transportError'] is None and response['readerCleanupErrors'] == []
    assert response['body'] == interop['wholeBody']
    body = checked(interop['wholeBody']).read_bytes()
    assert len(body) == interop['bodyBytes'] == response['receivedBytes']
    assert json.loads(body) == response['payload']
    assert response['payload']['mode'] == 'interop' and response['payload']['caseCount'] == 16
    assert len(response['payload']['records']) == 16 and all(item['passed'] is True for item in response['payload']['records'])
    policy_refs.append(interop_ref)
    builder = BASE / 'next-native-portable-build-preparation-v8'
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
    authority['newSourceEvidence'].extend(policy_refs)
    assert len(authority['newSourceEvidence']) == 18
    authority['worldSourceIndex'] = plan['worldSourceIndex']
    authority['nativeProfileLabel'] = (
        'Genuine476b/22f cleanup435/387/3 full native build:80 DBrows plus '
        'separateembedding, freshlockedRust and coherent previouslybuilt SMlibrary; '
        'coordinated4185 build DATA accepted. Source445e/1fe and40ee explicitly checked.'
    )
    authority['completion'] = 'Prepared real-Next INIT construction after accepted interop16; no new component or deployed Next result yet.'
    authority['rootReview'] = (
        'One new unchanged V5 real-Next-only construction on reviewed476b/22f cleanup native build. '
        'Root enforces required4185/d0cbd fullbuild and closed445e/selected1fe/40ee '
        'through actual compiled metadata, and accepted55a interop16/oneGET on the same roles; protects all six prerequisites in18 Source roles. '
        'All31 fixedmetadata fields and39 buildroles derived from actual newfullbuild, '
        'not old2251/afb arrays. Exactthreegenericcodes,73b/1e49 real-Next V5 guest unchanged. '
        'Same61685/d30/8025/std13/2400outer1800+120inner/1GiB admission. No '
        'app/probe fixtures or ordinary export/HTTP/entropy at INIT; fullactualreturned '
        'importtuples must be audited without a131count assumption. No production '
        'promotion/network/DEBUG/GC/fault/reset/resnapshot or automaticretry.'
    )
    for ref in authority['engineBuildEvidence'] + authority['newSourceEvidence']:
        assert row(ref['path']) == ref
    assert not Path(authority['outputRoot']).exists() and not Path(authority['outputRoot']).is_symlink()
    assert not Path(authority['outputRoot'] + '-external-root').exists() and not Path(authority['outputRoot'] + '-external-root').is_symlink()
    target = HERE / 'real-next-construction-authority.json'
    with target.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    receipt = dict(state='ROOT_CLEANUP_REAL_NEXT_INIT_PREPARED_NOT_LAUNCHED_V1',
        authority=row(target), priorAuthority=row(prior), acceptedBuildReview=row(review_path),
        caller=authority['callerIndex'], inputSource=plan['inputSourceIndex'],
        inputEntry=plan['entries']['real-next'], acceptedInteropRuntimeReview=interop_ref,
        fixtureMounted=False, actorInvoked=False)
    with (HERE / 'construction-preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
