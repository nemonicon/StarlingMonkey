"""Prepare one native then one Node transport control; never launch either."""
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
    native_base = BASE / 'next-full-build-runtime-root-results-v1/full02a-first-runtime-authority.json'
    stock_base = BASE / 'extra-cdp-off-root-results-v1/off1-authority-v2.json'
    native = json.loads(native_base.read_text())
    stock = json.loads(stock_base.read_text())
    native_source = BASE / 'next-action-wire-native-candidate-v1'
    stock_source = BASE / 'next-action-wire-stock-candidate-v1'
    common = BASE / 'next-action-wire-candidate-v1'
    native_plan = json.loads((native_source / 'plan.json').read_text())
    stock_plan = json.loads((stock_source / 'plans.json').read_text())
    native['sourceIndex'] = row(native_source / 'index.json')
    native['plan'] = row(native_source / 'plan.json')
    native['runId'] = 'full02a-action-wire-native-first'
    native['browserAllowed'] = False
    native['wireClientAllowed'] = True
    native['rootReview'] = (
        'One separately predeclared exact captured-POST HTTP/gzip EOF diagnostic '
        'on unchanged4afe component/full02a engine/9e960 metadata/V5 entry/fresh2181 '
        'app/world13. One common bounded Nodehttp client; no browser/navigation. '
        'All capture/framing/dechunk/gzip CRC/ISIZE/end/error/cap/cleanup checks '
        'are mandatory and partial bytes retained. This does not execute or '
        'accept the24HTTP/cache/stream/2browser/supplemental contract. Same '
        'original600-second owner/1GiB admission/native/copy/world protections. '
        'No guest/native/host/app modification, constructor, retry, failure '
        'waiver, private Store ID, unique cause or production adoption.'
    )
    assert native_plan['expectedComponent'] == {k: native['component'][k] for k in ['sha256', 'bytes']}
    additions = [HERE / 'run-native-wire.py', Path(__file__).resolve()]
    assert not any(row(p)['path'] in {r['path'] for r in native['nativeProtectedInputs']} for p in additions)
    native['nativeProtectedInputs'] += [row(p) for p in additions]
    stock['sourceIndex'] = row(stock_source / 'index.json')
    stock['plans'] = row(stock_source / 'plans.json')
    stock['runId'] = 'node22-action-wire-first'
    stock['browserAllowed'] = False
    stock['wireClientAllowed'] = True
    stock['rootReview'] = (
        'One separately predeclared matchedNode22.14 transport control after the '
        'native member has terminal clean ownership/protection. Same fresh2181 '
        'app, de7f Moduleprovider/HTTPbridge preparation and common exact391B '
        'capturedPOST client/protocol. No browser/navigation. Captured header '
        'substitutions and diagnostic additions are explicitly disclosed in '
        'common Source; do not infer unobserved browser wire headers. Mandatory '
        'framing/dechunk/gzip EOF/CRC/ISIZE/error/cap/cleanup checks preserve '
        'partial bytes. Original300-second owner/1GiB admission, fresh copy/cache '
        'and input protections. Transport-only result; no fullNext acceptance, '
        'guest/native/engine/compiler/deployment action, retry or cause proof.'
    )
    native_output = Path(native_plan['outputPrefix'] + '-' + native['runId'])
    stock_output = Path(stock_plan['outputPrefix'] + '-' + stock['runId'])
    targets = [HERE / 'native-authority.json', HERE / 'stock-authority.json', HERE / 'protocol.json']
    for path in targets + [native_output, Path(str(native_output) + '-external-root'),
                            stock_output, Path(str(stock_output) + '-monitor'),
                            HERE / (native['runId'] + '-full-world-guard.json')]:
        assert not path.exists() and not path.is_symlink(), str(path)
    for path, value in zip(targets[:2], [native, stock]):
        with path.open('x') as handle:
            handle.write(json.dumps(value, indent=2) + '\n')
    protocol = dict(
        schemaVersion=1, state='ROOT_ONE_NATIVE_ONE_NODE_ACTION_WIRE_PROTOCOL_V1',
        commonSourceIndex=row(common / 'index.json'),
        commonPlan=row(common / 'plan.json'), request=row(common / 'request.json'),
        requestBody=row(common / 'request-body.bin'),
        nativeBaseAuthority=row(native_base), stockBaseAuthority=row(stock_base),
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
