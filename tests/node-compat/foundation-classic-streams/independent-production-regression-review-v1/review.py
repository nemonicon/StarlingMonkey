"""Read/hash and reverse-text source review only. Never imports JS or a runner."""
from pathlib import Path
import datetime
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PACKET = HERE.parent / 'production-regression-candidate-v1'
ADOPTION = HERE.parent / 'production-adoption-v1'
INDEX = '81c55887dc5e767db27477ba28f0e7a26a948435c7ddc61c70da329d4bd7f029'
ROOT_INPUTS = '6eb9fac9dfccfd44b3195f1ef26e3beac471e219b3b37b576b93a4a2bd58f3fe'
CAP_INPUTS = 'ebb6cfa82cf841f39b5b657556197ebdffef31d7c7582c06bf071b95a9e2dd1e'
PINS = 'c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e'
RECEIPT = '1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56'
RECIPE = '71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
checked = {}


def read(path, expected=None, size=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    row = {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    assert expected is None or row['sha256'] == expected, path
    assert size is None or row['bytes'] == size, path
    assert str(path) not in checked or checked[str(path)] == row, 'Input changed'
    checked[str(path)] = row
    return data


def doc(path, expected=None):
    return json.loads(read(path, expected))


index = doc(PACKET / 'index.json', INDEX)
assert len(index['files']) == 174 and index['runtimeAcceptance'] is False and index['nativeAndHTTPPins'] is None
for row in index['files']:
    read(PACKET / row['path'], row['sha256'], row['bytes'])
closures = []
for name, expected, count in [('input-freeze.json', ROOT_INPUTS, 1777), ('capability/input-freeze.json', CAP_INPUTS, 1776)]:
    path = PACKET / name
    data = doc(path, expected)
    assert data['schemaVersion'] == 1 and data['nativeSources'] == 342
    assert data['actualEnginePins'] is None and data['actualHTTPPins'] is None
    assert len(data['inputs']) == count
    names = set()
    for row in data['inputs']:
        target = (path.parent / row['path']).resolve()
        assert str(target) not in names
        names.add(str(target))
        read(target, row['sha256'], row['bytes'])
    expected_live = ['host-apis/wasi-0.2.10/wit/deps/' + name + '/package.wit' for name in
        ['wasi-cli-0.2.10', 'wasi-clocks-0.2.10', 'wasi-filesystem-0.2.10', 'wasi-http-0.2.10', 'wasi-io-0.2.10', 'wasi-random-0.2.10', 'wasi-sockets-0.2.10']]
    expected_live += ['host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm']
    assert data['liveComputedInputs'] == expected_live
    assert all(str(REPO / name) in names for name in expected_live)
    policy = doc(HERE.parent / 'integration-candidate-v1/policy.json', '137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f')
    for row in policy['expectedNativeSourceManifest']:
        assert str(REPO / row['path']) in names
        read(REPO / row['path'], row['sha256'])
    closures.append({'path': str(path), 'files': count, 'sha256': expected, 'liveComputedFiles': 8, 'actualNativeSources': 342})

records = doc(PACKET / 'derivations.json')['records']
assert len(records) == 64
reverse = []
for row in records:
    before = read(REPO / row['sourcePath'], row['beforeSha256']).decode()
    after = read(PACKET / row['destinationPath'], row['afterSha256']).decode()
    restored = after
    for edit in reversed(row['edits']):
        if edit['new'] == '':
            anchor = 'export {requireFreshOutput,hash};'
            assert restored.count(anchor) == 1
            restored = restored.replace(anchor, edit['old'] + anchor)
        else:
            count = edit.get('count', 1)
            assert restored.count(edit['new']) >= count
            restored = restored.replace(edit['new'], edit['old'], count)
    assert restored == before, row['destinationPath']
    assert row['semanticFixtureChanges'] is False
    reverse.append({'source': row['sourcePath'], 'destination': row['destinationPath'], 'exactReverse': True})

pins = doc(ADOPTION / 'reviewed-runtime-pins-v1.json', PINS)
receipt = doc(ADOPTION / 'root-pin-review-receipt.json', RECEIPT)
reference = doc(PACKET / 'activation-reference.json')
assert pins['state'] == reference['requiredPinsState'] == 'REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1'
assert receipt['state'] == reference['requiredRootReceiptState'] == 'ROOT_REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1'
assert receipt['reviewedPinsSha256'] == PINS and receipt['recipeSha256'] == RECIPE and receipt['sourceFiles'] == 342
assert list(pins['variants']) == reference['requiredVariants'] == ['normal-off', 'normal-runtime', 'gc-off', 'disabled-off']
assert reference['reviewedPinsPath'] is None and reference['rootReviewReceiptPath'] is None and reference['activatedRuntimeIndexSha256'] is None
assert reference['requiresNewReviewedActivationSibling'] is True and reference['currentPinFilesMustRemainNull'] is True and reference['consumerAdmitted'] is False
assert all(value is None for value in doc(PACKET / 'runtime-pins.json')['variants'].values())
assert doc(PACKET / 'capability/http-component-pins.json')['component'] is None
proofs = []
for label, pin in pins['variants'].items():
    claimed = receipt['variants'][label]
    assert pin['state'] == reference['requiredPinState'] == 'reviewed-real-classic-production-freeze'
    assert pin['sourceFiles'] == 342 and pin['recipeSha256'] == RECIPE and len(pin['frozenFiles']) == 405
    for name in ('engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256'):
        assert pin[name] == claimed[name]
    proof_index = doc(claimed['independentProofIndexPath'], claimed['independentProofIndexSha256'])
    observed = doc(claimed['independentProofResultPath'], claimed['independentProofResultSha256'])
    assert observed['state'] == 'INDEPENDENT_CLASSIC_NATIVE_FREEZE_VERIFIED_NO_GUEST' and observed['label'] == label
    assert observed['anchors']['engineSha256'] == pin['engineSha256']
    assert observed['anchors']['metadataSha256'] == pin['receiptSha256']
    assert observed['anchors']['freezeReceiptSha256'] == pin['freezeReceiptSha256']
    assert observed['guestExecuted'] is False
    proofs.append({'label': label, 'engineSha256': pin['engineSha256'], 'proofIndexSha256': claimed['independentProofIndexSha256'], 'nativeOnly': True})

native = read(PACKET / 'native-preflight.mjs').decode()
assert "const pin=selectClassicPin" in native and native.index('const pin=selectClassicPin') < native.index('await seal();')
assert "selectedManifestsForEngine(metadata,{sourceRoot:pin.sourceRoot})" in native
assert "sourceManifest.length,342" in native and 'INPUTS_SHA=' + repr(ROOT_INPUTS) in native
assert 'metadata.sourceManifest' in native and 'classicStreamsEnabled' in native
assert "recheck(){await regular(pinsPath,PINS_SHA);await seal();" in native
assert "No 306-to342 projection" in native
common = read(PACKET / 'common/preflight.mjs').decode()
assert common.index('const production=await classicPreflight') < common.index('const inputClosure=await verifyInputClosure')
assert "assert.equal(sha256,expectedSha256,'Replay source seal changed')" in common
assert common.index('assert.equal(sha256,expectedSha256') < common.index('JSON.parse(bytes)')
assert 'await privateRecheck();await verifyInputClosure' in common
builder = read(PACKET / 'capability/runners/http-build.mjs').decode()
assert builder.index('await verifyProductionTicks') < builder.index('await loadToolchain()')
assert builder.count('await verifyComputedLiveInputs') == 2
assert 'computedBeforeCopy' in builder and 'computedAfterCopy' in builder and 'await productionAdmission.recheck()' in builder
for path in ('run-http-wasmtime.mjs', 'run-http-wash.mjs'):
    text = read(PACKET / 'capability' / path).decode()
    assert text.index('await verifyHTTPReady()') < text.index('await import(')
http = read(PACKET / 'capability/http-contract.mjs').decode()
assert "REVIEWED_REAL_HTTP_COMPONENT_V1" in http and 'pin.engineSha256,productionPin.engineSha256' in http
assert 'await admission.recheck()' in http and 'pinsSha256' in http
scalar = read(PACKET / 'release/helpers/native-scalar-harness.mjs').decode()
assert "writeFile(join(here, 'native-component-results.json')" not in scalar
assert "writeFile(join(output, 'native-component-results.json')" in scalar
path_runner = read(PACKET / 'release/runners/path.mjs').decode()
assert 'NODE_COMPAT_PATH_ORACLE_OUTPUT: oracleOutput' in path_runner and "readFile(join(oracleOutput, 'glob-results.json'))" in path_runner

# Rehash every consumed source/evidence byte after static review. No runner is imported.
for row in list(checked.values()):
    read(row['path'], row['sha256'], row['bytes'])
result = {'schemaVersion': 1, 'state': 'INDEPENDENT_CLASSIC_REPLAY_SOURCE_REVIEW_PASSED_NO_ACTIVATION',
    'reviewedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'sourcePacketIndexSha256': INDEX,
    'sourcePacketFiles': 174, 'closures': closures, 'exactReverseProofs': 64, 'reverseProofs': reverse,
    'rootAuthority': {'pinsSha256': PINS, 'reviewReceiptSha256': RECEIPT, 'tuples': proofs, 'sourcePacketStillNull': True},
    'blockersFound': [], 'ownerRecordedChecks': {'pureChecks': 26, 'syntaxFiles': 67, 'rerunByReviewer': False},
    'sourceReviewLimits': ['Future activation sibling and its source index have not been created or admitted by this review.',
        'Native artifacts were verified separately; no current runtime result is inherited.',
        'Native/HTTP pins remain null. HTTP packaging and both-host operation remain unexecuted here.',
        'Classic19/lifecycle/API tests are separate from this inherited regression replay.'],
    'codeChanged': False, 'nativeBuildExecuted': False, 'guestExecuted': False, 'targetHostExecuted': False,
    'runtimeActivated': False, 'verifiedFiles': sorted(checked.values(), key=lambda row: row['path'])}
with (HERE / 'results.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': result['state'], 'files': len(checked), 'resultSha256': hashlib.sha256((HERE / 'results.json').read_bytes()).hexdigest()}))
