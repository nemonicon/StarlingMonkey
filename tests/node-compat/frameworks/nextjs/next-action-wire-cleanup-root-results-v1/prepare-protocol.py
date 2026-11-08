"""Prepare current-cohort wire grants as JSON only; never launch either arm."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def row(path):
    path = Path(path)
    assert path.is_absolute() and path.resolve() == path and not path.is_symlink()
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def read_ref(ref):
    assert set(ref) == {'path', 'sha256', 'bytes'} and row(ref['path']) == ref
    return json.loads(Path(ref['path']).read_text())


def pinned(path, sha256, size):
    ref = dict(path=str(path), sha256=sha256, bytes=size)
    return ref, read_ref(ref)


def indexed(root, index, name):
    member = next(item for item in index['files'] if item['path'] == name)
    ref = dict(member, path=str(root / name))
    return ref, read_ref(ref)


def wire_permissions(authority, template, allowed):
    # Permission values come from the wire template, never the browser parent.
    keys = {key for key in template if key.endswith('Allowed')}
    assert {key for key in authority if key.endswith('Allowed')} <= keys
    assert {key for key in keys if template[key] is None} == set(allowed)
    for key in keys:
        authority[key] = True if key in allowed else template[key]
        assert type(authority[key]) is bool
    assert authority['browserAllowed'] is False
    authority['state'] = template['state']
    authority['rootLaunchMinimumFreeBytes'] = template['rootLaunchMinimumFreeBytes']
    assert authority['rootLaunchMinimumFreeBytes'] == 1073741824
    authority['actualRuntime'] = None
    authority['unissued'] = False  # Only this explicitly invoked JSON preparation issues it.


def main():
    native_base = BASE / 'next-fetch-resource-cleanup-next-runtime-root-results-v2/cleanup-next-runtime-authority.json'
    stock_base = BASE / 'next-portable-cache-stock-v2-root-results-v1/stock-first-runtime-authority.json'
    native_base_ref, native = pinned(native_base,
        '98a39cc9697d8d2b92a650cdd1e61bcfdd99fa8bf7a4e8a4a2574b2c918b71b9', 530938)
    stock_base_ref, stock = pinned(stock_base,
        '8a110639edeefb14983265cb87d9acc40cfe9ed1dc0e3cf19b3030825084857c', 2057)
    native_source = BASE / 'next-action-wire-cleanup-native-candidate-v1'
    stock_source = BASE / 'next-action-wire-cleanup-stock-candidate-v1'
    common = BASE / 'next-action-wire-cleanup-candidate-v1'
    native_index_ref, native_index = pinned(native_source / 'index.json',
        '2e33f8de6e15a73242e14c81e6bd5b01254a2fb74876f26084a028a39cad14a5', 3174)
    stock_index_ref, stock_index = pinned(stock_source / 'index.json',
        '2c95a071496dabf3b2b8e021e037edc6df023a6c10c8ebacb5c2704531b6be67', 3012)
    common_index_ref, common_index = pinned(common / 'index.json',
        '596792c505f0bee0d11fcb5fa0681468ad5bc7b9b5d4ac22f3ffb67fc16a2292', 3029)
    native_plan_ref, native_plan = indexed(native_source, native_index, 'plan.json')
    stock_plan_ref, stock_plan = indexed(stock_source, stock_index, 'plans.json')
    _, native_template = indexed(native_source, native_index, 'root-authority.template.json')
    _, stock_template = indexed(stock_source, stock_index, 'root-authority.template.json')
    common_plan_ref, _ = indexed(common, common_index, 'plan.json')
    request_ref, request = indexed(common, common_index, 'request.json')
    body_ref = row(common / 'request-body.bin')
    assert body_ref == dict(next(item for item in common_index['files']
        if item['path'] == 'request-body.bin'), path=str(common / 'request-body.bin'))
    assert body_ref['sha256'] == 'cc609fbe813753e8cc29ec04c0e6bb243c7c656c22338943553d83221ef71f99'
    assert body_ref['bytes'] == 391
    for plan in [native_plan, stock_plan]:
        assert plan['wireSourceIndex'] == common_index_ref
        assert plan['wireSourceBindingPending'] is False
    assert native_plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-action-wire-native-v1'
    assert stock_plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-action-wire-stock-v1'

    # Same-generation genuine parent records: no path replacement or projection.
    construction = read_ref(native['constructionResult'])
    constructor = read_ref(construction['rootAuthority'])
    review = read_ref(native['constructionDataReview'])
    assert review['verifiedPassed'] is review['completeReturnedImportAuditVerified'] is True
    assert review['state'] == 'COORDINATED_REAL_NEXT_INTEROP_COMPONENT_INIT_DATA_REVIEW_PASSED_V1'
    for key, value in [('actualResult', native['constructionResult']),
                       ('rootAuthority', construction['rootAuthority']),
                       ('component', native['component']), ('engine', native['engine']),
                       ('nativeMetadata', native['nativeMetadata'])]:
        assert review[key] == value
    assert native_plan['acceptedConstructionReview'] == native['constructionDataReview']
    assert native_plan['expectedComponent'] == {key: native['component'][key] for key in ['sha256', 'bytes']}
    assert native_plan['expectedEngine'] == native['engine']
    assert native_plan['expectedNativeMetadata'] == native['nativeMetadata']
    assert len(constructor['metadataExpectedFixedValues']) == review['metadataFixedValueCount'] == 31
    assert len(constructor['engineBuildEvidence']) == review['buildEvidenceCount'] == 39
    assert len(constructor['newSourceEvidence']) == review['sourceEvidenceCount'] == 18
    for key in ['metadataExpectedFixedValues', 'engineBuildEvidence', 'engine', 'nativeMetadata']:
        assert native[key] == constructor[key]
    metadata = read_ref(native['nativeMetadata'])
    assert all(metadata[key] == value for key, value in native['metadataExpectedFixedValues'].items())
    build_result = read_ref(native['fullNativeBuildResult'])
    assert build_result['passed'] is True and len(build_result['sourceCopies']) == 825
    source_target = [copy[key] for copy in build_result['sourceCopies'] for key in ['source', 'target']]
    protected_prefix = list(native['nativeProtectedInputs'])
    assert len(source_target) == len({ref['path'] for ref in source_target}) == 1650
    assert protected_prefix[:1650] == source_target and len(protected_prefix) == 1781
    assert all(ref in protected_prefix for ref in constructor['newSourceEvidence'] + constructor['engineBuildEvidence'])
    assert native['fullNativeBuildReview'] == review['fullBuildReview']
    assert native['applicationBuildDataReview'] == native_plan['applicationBuildReview'] == stock_plan['applicationBuildReview']
    assert stock['applicationBuildDataReview'] == native['applicationBuildDataReview']
    stock_parent_plan = read_ref(stock['plans'])
    for key in ['applicationInputs', 'applicationBuildResult', 'hostVmDynamicImportPolicy']:
        assert stock_plan[key] == stock_parent_plan[key]
    assert stock_plan['applicationInputs'] == native_plan['applicationInputs']

    native['sourceIndex'], native['plan'] = native_index_ref, native_plan_ref
    stock['sourceIndex'], stock['plans'] = stock_index_ref, stock_plan_ref
    native['runId'] = 'cleanup-476b-action-wire-native-first'
    stock['runId'] = 'cleanup-node22-action-wire-stock-first'
    for authority in [native, stock]:
        assert re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', authority['runId'])
    wire_permissions(native, native_template,
        ['localhostServeAllowed', 'actualNextGuestAllowed', 'wireClientAllowed'])
    wire_permissions(stock, stock_template, ['localhostServerAllowed', 'wireClientAllowed'])
    native['wholeWorldAndFullNativeRootGuardRequired'] = native_template['wholeWorldAndFullNativeRootGuardRequired']
    assert native['wholeWorldAndFullNativeRootGuardRequired'] is True
    additions = [HERE / 'run-native-wire.py', Path(__file__).resolve()]
    assert not any(row(path)['path'] in {ref['path'] for ref in protected_prefix} for path in additions)
    native['nativeProtectedInputs'] = protected_prefix + [row(path) for path in additions]
    assert native['nativeProtectedInputs'][:-2] == protected_prefix
    native['rootReview'] = (
        'One current captured391B POST transport-only diagnostic on unchangedD990/476b22f '
        'and f805 app/std13, original600-second owner/1GiB/full-native and whole-world '
        'guards. Same genuine31 fixed metadata values/39 build/18 Source evidence and '
        'all825 source-target pairs retained without path retargeting. Mandatory raw '
        'capture/framing/dechunk/single-gzip CRC/ISIZE/EOF/error/cap/cleanup gates. No '
        'browser, fullNext acceptance, failure waiver, retry, new capability or cause proof.'
    )
    stock['rootReview'] = (
        'One matched Node22.14 prepared-host transport control after native terminal '
        'clean ownership/protection; samef805 app/current391B POST/common client. Held '
        'StockV2 public default-loader provider and owned cache-parent prerequisite '
        'remain, outside guest profile and with distinct customCJS/mainESM caches. '
        'Original300-second owner/1GiB and all HTTP/gzip/EOF/error/cap gates. No browser, '
        'fullNext acceptance, original failure waiver, retry or unique cause proof.'
    )
    native_output = Path(native_plan['outputPrefix'] + '-' + native['runId'])
    stock_output = Path(stock_plan['outputPrefix'] + '-' + stock['runId'])
    targets = [HERE / 'native-authority.json', HERE / 'stock-authority.json', HERE / 'protocol.json']
    for path in targets + [HERE / 'preparation.json', native_output,
            Path(str(native_output) + '-external-root'), stock_output,
            Path(str(stock_output) + '-monitor'),
            HERE / (native['runId'] + '-full-world-guard.json')]:
        assert not path.exists() and not path.is_symlink(), str(path)
    for path, value in zip(targets[:2], [native, stock]):
        with path.open('x') as handle:
            handle.write(json.dumps(value, indent=2) + '\n')
    protocol = dict(
        schemaVersion=1, state='ROOT_ONE_NATIVE_ONE_NODE_ACTION_WIRE_PROTOCOL_V1',
        commonSourceIndex=common_index_ref, commonPlan=common_plan_ref,
        request=request_ref, requestBody=body_ref,
        nativeBaseAuthority=native_base_ref, stockBaseAuthority=stock_base_ref,
        nativeAuthority=row(targets[0]), stockAuthority=row(targets[1]),
        nativeGuard=row(HERE / 'run-native-wire.py'), preparer=row(Path(__file__).resolve()),
        explicitOrder=['native', 'stock'], nativeOutputRoot=str(native_output),
        stockOutputRoot=str(stock_output), nativeOwnerSeconds=600, stockOwnerSeconds=300,
        minimumFreeBytes=1073741824, onePostPerArm=True,
        requestTransportOnly=True, browserInvoked=False,
        priorOriginalGatesAccepted=False, uniqueCauseProved=False,
        automaticRetry=False, additionalSamplesAllowed=False,
        stockRequiresPriorNativeTerminalCleanupAndProtection=True,
    )
    with targets[2].open('x') as handle:
        handle.write(json.dumps(protocol, indent=2) + '\n')
    receipt = dict(state='ROOT_ACTION_WIRE_PROTOCOL_PREPARED_NOT_LAUNCHED',
        protocol=row(targets[2]), nativeAuthority=row(targets[0]),
        stockAuthority=row(targets[1]), actorInvoked=False)
    with (HERE / 'preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
