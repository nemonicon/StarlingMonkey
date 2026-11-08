"""Prepare current full-suite NetLog grants as JSON only; never launch either arm."""
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


def main():
    native_base = BASE / 'next-fetch-resource-cleanup-next-runtime-root-results-v2/cleanup-next-runtime-authority.json'
    stock_base = BASE / 'next-portable-cache-stock-v2-root-results-v1/stock-first-runtime-authority.json'
    native_base_ref, native = pinned(native_base,
        '98a39cc9697d8d2b92a650cdd1e61bcfdd99fa8bf7a4e8a4a2574b2c918b71b9', 530938)
    stock_base_ref, stock = pinned(stock_base,
        '8a110639edeefb14983265cb87d9acc40cfe9ed1dc0e3cf19b3030825084857c', 2057)
    native_source = BASE / 'next-browser-netlog-native-candidate-v1'
    stock_source = BASE / 'next-browser-netlog-stock-candidate-v1'
    common = BASE / 'next-browser-netlog-candidate-v1'
    native_index_ref, native_index = pinned(native_source / 'index.json',
        'e697c715a1c7b94c86eb91f00777d6015e23e9f2d081dae715467cc352637d59', 2382)
    stock_index_ref, stock_index = pinned(stock_source / 'index.json',
        'db0b4eb35513fe9445fa7baabfaa23937976ceab5391ac4663fe68caf9f79f8c', 2094)
    common_index_ref, common_index = pinned(common / 'index.json',
        'c7be23d9dbdd8a956ccb7507d640aadbd7da3a05d46c76bb5b6ac2e75d8f46d5', 2029)
    native_plan_ref, native_plan = indexed(native_source, native_index, 'plan.json')
    stock_plan_ref, stock_plan = indexed(stock_source, stock_index, 'plans.json')
    common_plan_ref, common_plan = indexed(common, common_index, 'plan.json')
    worker_ref, analyser_ref = common_plan['worker'], common_plan['analyser']
    assert row(worker_ref['path']) == worker_ref and row(analyser_ref['path']) == analyser_ref
    assert native_plan['browserSource'] == stock_plan['arms']['stock']['browserSource'] == worker_ref
    for plan in [native_plan, stock_plan]:
        assert plan['netlogSourceIndex'] == common_index_ref
        assert plan['netlogSourceBindingPending'] is False
    assert native_plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-wasmtime-deployment'
    assert stock_plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-portable-cache-stock-v2'

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
    native['runId'] = 'cleanup-476b-netlog-native-first'
    stock['runId'] = 'portable-cache-netlog-stock-first'
    for authority in [native, stock]:
        assert re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', authority['runId'])
    # Full-suite API permission values remain exactly those of the genuine
    # current parents. In particular browser is TRUE; no wire-false template.
    for key in ['localhostServeAllowed', 'actualNextGuestAllowed', 'browserAllowed']:
        assert native[key] is True
    for key in ['compilerAllowed', 'componentConstructionAllowed', 'externalDeploymentAllowed', 'adoptionAllowed']:
        assert native[key] is False
    for key in ['localhostServerAllowed', 'browserAllowed']:
        assert stock[key] is True
    for key in ['compilerAllowed', 'nativeBuildAllowed', 'guestAllowed', 'engineAllowed', 'externalApplicationDeploymentAllowed']:
        assert stock[key] is False
    assert 'wireClientAllowed' not in native and 'wireClientAllowed' not in stock
    assert native['rootLaunchMinimumFreeBytes'] == 1073741824
    additions = [HERE / 'run-full-native-requests.py', Path(__file__).resolve()]
    assert not any(row(path)['path'] in {ref['path'] for ref in protected_prefix} for path in additions)
    native['nativeProtectedInputs'] = protected_prefix + [row(path) for path in additions]
    assert native['nativeProtectedInputs'][:-2] == protected_prefix
    native['rootReview'] = (
        'One separate full unchangedD990/476b22f/f805 regression with strictBrowser2 '
        'and default Chrome NetLog diagnostic. Original fiveNonce52/all24HTTP/legacy '
        'cache1to2/five-stream/80supplemental/strict-body-error gates stay mandatory; '
        'same600-second owner/1GiB/full-native+whole-world guards. Genuine31 fixed '
        'metadata/39 build/18 Source and all825 source-target pairs remain unchanged. '
        'NetLog only adds2startupflags and bounded normal-close retention. No browser '
        'assertion waiver, originalfailure acceptance, new capability, retry, private '
        'native identity, unique cause or production adoption.'
    )
    stock['rootReview'] = (
        'One separate matched Node22.14 full regression after native terminal clean '
        'ownership/protection. Samef805 app, held StockV2 public default-loader provider '
        'and owned cache-parent prerequisite; same shared strictBrowser+NetLog worker '
        'and all fiveNonce52/24HTTP/cache1to2/stream/80supplemental gates. Original '
        '300-second owner/1GiB, default isolated Chrome profile/CDP/assertions remain. '
        'Host reference stays outsideguest profile; customCJS/mainESM caches distinct. '
        'No oldfailure waiver, retry, guest/native/compiler/deployment permission '
        'or unique cause proof.'
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
        schemaVersion=1, state='ROOT_ONE_NATIVE_ONE_NODE_STRICT_BROWSER_NETLOG_PROTOCOL_V1',
        commonSourceIndex=common_index_ref, commonPlan=common_plan_ref,
        sharedBrowserWorker=worker_ref, dataAnalyser=analyser_ref,
        nativeBaseAuthority=native_base_ref, stockBaseAuthority=stock_base_ref,
        nativeAuthority=row(targets[0]), stockAuthority=row(targets[1]),
        nativeGuard=row(HERE / 'run-full-native-requests.py'), preparer=row(Path(__file__).resolve()),
        explicitOrder=['native', 'stock'], nativeOutputRoot=str(native_output),
        stockOutputRoot=str(stock_output), nativeOwnerSeconds=600, stockOwnerSeconds=300,
        minimumFreeBytes=1073741824, originalFullSuiteGatesRequired=True,
        strictBrowserRequired=True, defaultCaptureOnly=True,
        requestedChromeCircularCapMegabytes=16, finalFileReadMaximumBytes=20971520,
        browserAssertionWaiver=False, actualNativeRuntime=None, actualStockRuntime=None,
        priorOriginalGatesAccepted=False, uniqueCauseProved=False,
        automaticRetry=False, additionalSamplesAllowed=False,
        stockRequiresPriorNativeTerminalCleanupAndProtection=True,
    )
    with targets[2].open('x') as handle:
        handle.write(json.dumps(protocol, indent=2) + '\n')
    receipt = dict(state='ROOT_DEFAULT_NETLOG_FULL_SUITE_PROTOCOL_PREPARED_NOT_LAUNCHED',
        protocol=row(targets[2]), nativeAuthority=row(targets[0]),
        stockAuthority=row(targets[1]), actorInvoked=False)
    with (HERE / 'preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
