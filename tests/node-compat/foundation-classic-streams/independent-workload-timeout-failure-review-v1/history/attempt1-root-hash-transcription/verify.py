#!/usr/bin/env python3
"""Read-only evidence reader. No owner imports, subprocesses, or target calls."""
import hashlib
import json
import os
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
SOURCE = FAMILY / 'measurement-correctness-activated-v1'
OUTPUT = Path('/tmp/starling-node-compat/production-classic-corrected-workload-v1')
TMP = Path('/tmp/starling-node-compat')
ROOT = FAMILY / 'production-adoption-v1/workload-timeout-attempt1-root-results.json'
seen = {}

def checked(path, expected=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode), str(path)
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), str(path)
    value = digest.hexdigest()
    if expected is not None:
        assert value == expected, str(path)
    if size is not None:
        assert before.st_size == size, str(path)
    seen[str(path)] = {'path': str(path), 'sha256': value, 'bytes': before.st_size}
    return value

def load(path):
    checked(path)
    return json.loads(Path(path).read_bytes())

def uleb(data, position):
    value = shift = 0
    while True:
        byte = data[position]
        position += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, position
        shift += 7
        assert shift < 64

def name(data, position):
    length, position = uleb(data, position)
    return data[position:position + length].decode('utf8'), position + length

checked(ROOT, 'e816556489c1affb4c10b0d4dd19e87a5550e9b0db16bc92a97737c4876497661')
root = load(ROOT)
assert root['rawTerminalExitCode'] == 1 and root['toolSession'] == 90660
assert root['originalTimedOutCaseUnknown'] is True
assert root['fullCorrectnessPassed'] is False
assert root['timeoutMilliseconds'] == 55000
assert len(root['files']) == 19
for row in root['files']:
    checked(row['path'], row['sha256'], row['bytes'])

checked(SOURCE / 'index.json', '4728c3651ff356a8ddba0cde84a091d840c232c0ff258bda0c615baaefc33f49')
index = load(SOURCE / 'index.json')
assert len(index['files']) == 21
for row in index['files']:
    checked(SOURCE / row['path'], row['sha256'], row['bytes'])
source_receipt = load(SOURCE / 'source-receipt.json')
assert source_receipt['parentCorrectnessIndexSha256'] == '138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da'
assert source_receipt['mandatoryReportingIndexSha256'] == '0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350'
checked(FAMILY / 'measurement-correctness-candidate-v1/index.json', source_receipt['parentCorrectnessIndexSha256'])
checked(FAMILY / 'measurement-correctness-reporting-amendment-v1/index.json', source_receipt['mandatoryReportingIndexSha256'])
assert source_receipt['pinsSha256'] == checked(SOURCE / 'reviewed-pins.json')
assert source_receipt['rootReviewSha256'] == checked(SOURCE / 'root-review-receipt.json')
seal = load(SOURCE / 'input-freeze.json')
assert len(seal['inputs']) == 7489 and len(seal['toolLinks']) == 22
# This failure reader authenticates the sealed manifest bytes; it does not rerun
# its 7,489-row/tool-tree admission. The actual native frozen inventory below is
# independently rehashed, including all recorded originals.
actual = source_receipt['actualON']
freeze_root = Path(actual['freezeRoot'])
engine = freeze_root / 'benchmark-classic-on.engine.wasm'
checked(engine, actual['engineSha256'], actual['engineBytes'])
checked(Path(str(engine) + '.build.json'), actual['metadataSha256'])
freeze_path = freeze_root / 'benchmark-classic-on-freeze-receipt.json'
checked(freeze_path, actual['freezeReceiptSha256'])
freeze = load(freeze_path)
metadata = load(Path(str(engine) + '.build.json'))
assert len(freeze['copies']) == 525
assert len(metadata['sourceManifest']) == 342
assert len(metadata['componentizeSourceManifest']) == 3
assert metadata['classicBenchmarkDiagnosticPolicy']['addonInputs'] == 2
assert metadata['classicStreamsEnabled'] is True and metadata['gcStress'] is False
assert metadata['diagnosticOnly'] is True and metadata['oomTesting'] is False
assert metadata['debuggerEnabled'] is False and metadata['entropyPolicy'] == 'off'
assert metadata['engineSha256'] == actual['engineSha256']
for row in freeze['copies']:
    checked(row['path'], row['sha256'], row['bytes'])
    checked(row['original'], row['sha256'], row['bytes'])

driver = (SOURCE / 'component-driver.mjs').read_text()
retained_pos = driver.index('const retained=[];for(let round=0;round<3;round++)')
fresh_pos = driver.index('freshJco=await oneRotation(fresh,1,')
wt_pos = driver.index('const wasmtime=[];')
status_pos = driver.index('assert.equal(actual.status,0,actual.error?.message??actual.stderr);')
save_pos = driver.index('wasmtime.push(')
publish_pos = driver.index('await publishCompletion(')
assert retained_pos < fresh_pos < wt_pos < status_pos < save_pos < publish_pos
assert "timeout:55000,maxBuffer:16*1024*1024" in driver
assert driver.index('const report=') > save_pos
assert 'writeCounterexample' not in driver[status_pos:driver.index('const value=JSON.parse', status_pos)]
assert not any(OUTPUT.glob('*results*'))
assert not any(OUTPUT.glob('*completion*'))
assert not (OUTPUT / 'correctness-counterexample.json').exists()
regular = sorted(path.name for path in OUTPUT.iterdir() if path.is_file() and not path.is_symlink())
assert regular == sorted(['classic-correctness.component.wasm', 'classic_correctness.core.wasm', 'classic_correctness.d.ts', 'classic_correctness.js', 'emitted.wit', 'guest.bundle.mjs', 'package.json'])
assert (OUTPUT / 'node_modules').is_symlink()
partial_link = {'path': str(OUTPUT / 'node_modules'), 'linkText': os.readlink(OUTPUT / 'node_modules')}
stderr = (TMP / 'classic-corrected-workload-guest-v1.stderr.log').read_text()
assert 'ETIMEDOUT' in stderr and 'component-driver.mjs:56:10' in stderr
assert 'null !== 0' in stderr
assert (TMP / 'classic-corrected-workload-guest-v1.stdout.log').stat().st_size == 0

# Decode only the public component container, types, and exports as data.
binary = (OUTPUT / 'classic-correctness.component.wasm').read_bytes()
assert binary[:8] == b'\x00asm\x0d\x00\x01\x00'
position = 8
imports, exports, types = [], [], []
while position < len(binary):
    section_id = binary[position]
    position += 1
    length, position = uleb(binary, position)
    payload = binary[position:position + length]
    assert len(payload) == length
    position += length
    if section_id == 10:
        count, end = uleb(payload, 0)
        assert count == 0 and end == len(payload)
    elif section_id == 11:
        count, at = uleb(payload, 0)
        for _ in range(count):
            assert payload[at] == 0
            export_name, at = name(payload, at + 1)
            kind = payload[at]
            at += 1
            target_index, at = uleb(payload, at)
            assert payload[at] == 0
            at += 1
            exports.append({'name': export_name, 'sort': kind, 'index': target_index})
        assert at == len(payload)
    elif section_id == 7:
        types.append(payload.hex())
assert position == len(binary)
assert exports == [{'name': 'run', 'sort': 1, 'index': 0}, {'name': 'boundaries', 'sort': 1, 'index': 2}]
assert types == ['0140010a636173652d696e646578790073', '0140000073']
wit = (OUTPUT / 'emitted.wit').read_text()
assert 'export run: func(case-index: u32) -> string;' in wit
assert 'export boundaries: func() -> string;' in wit and 'import' not in wit
assert (OUTPUT / 'classic_correctness.core.wasm').read_bytes()[:8] == b'\x00asm\x01\x00\x00\x00'

oracle = load(SOURCE / 'node-workload-oracle.json')
assert oracle['node'] == 'v22.14.0' and len(oracle['expected']) == 20
row = oracle['expected'][0]
expected = {'schemaVersion': 1, 'calls': 1, 'caseIndex': 0, 'setup': row['setup'], 'result': row['oracle']}
jco = json.loads((TMP / 'classic-correctness-public-controls-v1/jco-case0.stdout.log').read_text())
wt_cli = json.loads((TMP / 'classic-correctness-public-case0-v1/stdout.log').read_text())
assert isinstance(wt_cli, str)
wt = json.loads(wt_cli)
assert jco == expected and wt == expected and jco == wt
jco_control = load(TMP / 'classic-correctness-public-controls-v1/jco-case0-result.json')
wt_control = load(TMP / 'classic-correctness-public-case0-v1/results.json')
case5 = load(TMP / 'classic-correctness-public-controls-v1/wasmtime-case5-result.json')
assert jco_control['rawChildExitCode'] == 0 and jco_control['timedOut'] is False
assert wt_control['rawChildExitCode'] == 0 and wt_control['timedOut'] is False
assert case5['rawChildExitCode'] is None and case5['timedOut'] is True and case5['timeoutSeconds'] == 55
assert case5['command'][-2:] == ['run(5)', str(OUTPUT / 'classic-correctness.component.wasm')]
assert (TMP / 'classic-correctness-public-controls-v1/wasmtime-case5.stdout.log').stat().st_size == 0
assert (TMP / 'classic-correctness-public-controls-v1/wasmtime-case5.stderr.log').stat().st_size == 0
long_root_path = FAMILY / 'production-adoption-v1/workload-public-case5-root-results.json'
checked(long_root_path, '793a2f0de42b931fac12c55c570a888add9ced3c2e9b25b09e8bef70363ce45e')
long_root = load(long_root_path)
for item in long_root['files']:
    checked(item['path'], item['sha256'], item['bytes'])
long_control = load(TMP / 'classic-correctness-public-case5-long-v1/results.json')
assert long_root['rawTerminalExitCode'] == 0 and long_control['rawChildExitCode'] == 0
assert long_control['timeoutSeconds'] == 600 and long_control['timedOut'] is False
long_cli = json.loads((TMP / 'classic-correctness-public-case5-long-v1/stdout.log').read_text())
assert isinstance(long_cli, str)
long_value = json.loads(long_cli)
long_row = oracle['expected'][5]
assert long_row['id'] == 'pipeline-view-524288' and long_row['iterations'] == 16
assert long_value == {'schemaVersion': 1, 'calls': 1, 'caseIndex': 5, 'setup': long_row['setup'], 'result': long_row['oracle']}
checked(Path(jco_control['command'][0]), seal['invocation'].get('nodeExecutableSha256', 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'))
checked(Path(wt_control['command'][0]), 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c')

# Final recheck of the evidence and immutable source inventories, with no calls.
for record in list(seen.values()):
    checked(record['path'], record['sha256'], record['bytes'])
report = {
    'schemaVersion': 1,
    'state': 'INDEPENDENT_WORKLOAD_HOST_TIMEOUT_FAILURE_EVIDENCE_VERIFIED_NO_RUNTIME_RERUN',
    'rootReceiptSha256': checked(ROOT),
    'sourceIndexSha256': checked(SOURCE / 'index.json'),
    'componentSha256': checked(OUTPUT / 'classic-correctness.component.wasm'),
    'originalFullGate': {'rawTerminalExitCode': 1, 'timeoutMilliseconds': 55000, 'timedOutCase': None, 'caseUnknown': True, 'resultsPublished': False, 'completionPublished': False, 'semanticCounterexamplePublished': False, 'correctnessPassed': False},
    'sourceControlFlowOnly': {'threeRetainedRotationsThenFreshJcoPrecedeWasmtime': True, 'theirObservationsWereNotDurablyPersisted': True, 'statusAssertionPrecedesWasmtimeResultRetention': True, 'unretainedObservationsNotPromotedToPass': True},
    'separatePublicControls': {'freshJcoCase0FullNodeRecordExact': True, 'freshWasmtimeCase0FullNodeRecordExact': True, 'case0Calls': 1, 'case0Id': row['id'], 'freshWasmtimeCase5TimedOutAt55Seconds': True, 'freshWasmtimeCase5ReturnedAt600SecondBoundFullNodeRecordExact': True, 'case5ObservedWallSecondsOperationalOnly': long_control['wallSecondsOperationalOnly'], 'case5Calls': 1, 'case5Id': long_row['id'], 'case5Iterations': 16, 'case5DoesNotIdentifyOriginalTimedOutCase': True, 'fiftyFiveSecondDeadlineInsufficientForSeparateCase5AtObservedLoad': True, 'allCaseDeadlineAdequacyClaim': False},
    'publicBinary': {'imports': imports, 'exports': exports, 'componentFunctionTypePayloadsHex': types, 'run': 'func(case-index: u32) -> string', 'boundaries': 'func() -> string', 'coreMagicVersionVerified': True},
    'sourceAndNative': {'activatedIndexFilesVerified': 21, 'sealedInputManifestRows': 7489, 'fullInputTreeAdmissionRerun': False, 'nativeFrozenCopiesAndOriginalsRehashed': 525, 'nativeSources': 342, 'addonSources': 2, 'externalEmbeddingSources': 3, 'engineSha256': actual['engineSha256'], 'metadataSha256': actual['metadataSha256'], 'freezeReceiptSha256': actual['freezeReceiptSha256'], 'originalSourceOrNativeOrCorpusModified': False},
    'partialOutputRegularFiles': regular,
    'partialOutputSymlink': partial_link,
    'cause': 'Unknown; host timeout is not proof of a semantic or native failure.',
    'rawRuntimeRerun': False,
    'ownerImportsOrActionMains': False,
    'fullCorrectnessPassed': False,
    'nodeCompatibilityPassed': False,
    'timingPerformed': False,
    'performanceClaim': False,
    'files': sorted(seen.values(), key=lambda value: value['path'])
}
with (HERE / 'results.json').open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': report['state'], 'verifiedFiles': len(seen), 'originalTimedOutCaseUnknown': True, 'separateCase0Exact': True, 'fullCorrectnessPassed': False}))
