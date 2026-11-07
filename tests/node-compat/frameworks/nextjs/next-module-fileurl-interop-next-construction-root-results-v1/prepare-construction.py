"""Bind the accepted16-case prerequisite to unchanged real-Next INIT code."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    prior = BASE / 'next-module-fileurl-interop-probe-root-results-v1/interop-probe-v2-construction-authority.json'
    authority = json.loads(prior.read_text())
    caller = BASE / 'next-module-fileurl-interop-next-construction-v1'
    plan = json.loads((caller / 'plan.json').read_text())
    assert set(plan['entries']) == {'real-next'}
    assert plan['expectedEngineForRootAuthority'] == authority['engine']
    assert plan['expectedNativeMetadataForRootAuthority'] == authority['nativeMetadata']
    assert row(Path(authority['engine']['path'])) == authority['engine']
    assert row(Path(authority['nativeMetadata']['path'])) == authority['nativeMetadata']
    prerequisite = plan['requiredInteropRuntimeReviewForRootAuthority']
    assert prerequisite == row(Path(prerequisite['path']))
    assert prerequisite['sha256'] == '030fad8bec22f753d0436d0089d47d38014bae73cfdee911bd5d9baf4da3a226'
    review = json.loads(Path(prerequisite['path']).read_text())
    assert review['state'] == 'COORDINATED_INTEROP_SELECTED_PROFILE_RUNTIME_DATA_REVIEW_PASSED_V1'
    assert review['verifiedPassed'] is True and review['all16Passed'] is True
    assert review['interopProfileMatched'] is True
    assert review['actualGetRequests'] == 1 and review['status'] == 200
    assert review['bodyBytes'] == 7152
    assert review['nativeLoaderSourceSha256'] == '40eeb699d87b30dd3c146421f189a99848715a19b2efc83b081f0d61d3832d67'
    assert review['engine'] == authority['engine'] and review['nativeMetadata'] == authority['nativeMetadata']
    assert review['nodeParityProved'] is review['fullNextAcceptance'] is review['adoption'] is False
    for key in ['actualResult', 'rootAuthority', 'sourceIndex', 'plan', 'constructionResult',
                'constructionDataReview', 'component', 'componentAudit', 'engine', 'nativeMetadata',
                'fullNativeBuildReview', 'complementaryOutcomeReview', 'rootFullNativeWorldGuard']:
        assert row(Path(review[key]['path'])) == review[key]
    actual = json.loads(Path(review['actualResult']['path']).read_text())
    assert actual['interopProfileMatched'] is True and actual['errors'] == []
    assert actual['response']['complete'] is True and actual['response']['overflow'] is False
    assert row(Path(actual['response']['body']['path'])) == review['wholeBody'] == actual['response']['body']
    payload = json.loads(Path(actual['response']['body']['path']).read_text())
    assert payload['caseCount'] == payload['expectedCaseCount'] == len(payload['records']) == 16
    assert [record['id'] for record in payload['records']] == review['caseIds']
    assert payload['profilePassed'] is payload['exactCaseIds'] is True
    assert all(record['passed'] is True for record in payload['records'])
    authority['callerIndex'] = row(caller / 'index.json')
    authority['entryMode'] = 'real-next'
    authority['runId'] = 'next-2251-first'
    authority['outputRoot'] = plan['outputPrefix'] + '-real-next-' + authority['runId']
    # Same accepted build: keep all39 existing actual-build descriptors verbatim.
    assert len(authority['engineBuildEvidence']) == 39
    assert len(authority['metadataExpectedFixedValues']) == 31
    native = json.loads(Path(authority['nativeMetadata']['path']).read_text())
    assert all(native[key] == value for key, value in authority['metadataExpectedFixedValues'].items())
    world = Path(plan['worldSourceIndex']['path'])
    wit = sorted(world.parent.rglob('*.wit'))
    assert len(wit) == 8
    authority['newSourceEvidence'] = [plan['inputSourceIndex']] + [row(path) for path in wit] + [
        plan['worldSourceIndex'], authority['callerIndex'],
        row(BASE / 'next-native-portable-build-preparation-v6/index.json'), prerequisite]
    assert len(authority['newSourceEvidence']) == 13
    authority['worldSourceIndex'] = plan['worldSourceIndex']
    authority['completion'] = 'Unissued real-Next INIT construction on accepted2251/afb; deployed app not tested.'
    authority['rootReview'] = (
        'One real-Next INIT construction after genuine030f accepted16-case deployed interoperability DATA. '
        'Use unchanged73b/1e49 entry and three genericV6 executables, accepted2251/afb corrected40ee '
        'full435/387/3 build,80DB+separateembedding, same61685/d30/canonical8025/std13 and '
        'original2400/1800/120 caps/1GiB. All39 actual-build descriptors and31 fixedmetadata fields '
        'stay verbatim; thirteenth Source role protects actual030f prerequisite. No app/cache/fixture '
        'mount, Next bootstrap, ordinary export, deployed filesystem import/probe, HTTP, entropy or '
        'resnapshot at INIT. Existing Next cache/browser failures remain failed; no fullNode/Next or '
        'production acceptance is inferred from construction or the bounded interoperability pass.'
    )
    for ref in authority['engineBuildEvidence'] + authority['newSourceEvidence']:
        assert row(Path(ref['path'])) == ref
    output = Path(authority['outputRoot'])
    external = Path(str(output) + '-external-root')
    assert not output.exists() and not output.is_symlink()
    assert not external.exists() and not external.is_symlink()
    target = HERE / 'interop-next-v1-construction-authority.json'
    with target.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    receipt = dict(state='ROOT_INTEROP_REAL_NEXT_INIT_PREPARED_NOT_LAUNCHED_V1',
        authority=row(target), priorAuthority=row(prior), caller=authority['callerIndex'],
        prerequisite=prerequisite, inputSource=plan['inputSourceIndex'],
        inputEntry=plan['entries']['real-next'], actualBuildEvidence=39,
        fixedMetadataFields=31, newSourceEvidence=13, actorInvoked=False)
    with (HERE / 'construction-preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
