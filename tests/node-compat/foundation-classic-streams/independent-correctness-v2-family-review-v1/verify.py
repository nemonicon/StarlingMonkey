"""Independent generated-family reader; executes no owner/helper or JS code."""
from pathlib import Path
import hashlib
import json
import os
import stat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
ACTUAL = FAMILY / 'measurement-correctness-activated-v2'
ACTIVATOR = FAMILY / 'measurement-correctness-activation-candidate-v2'
PREVIOUS = FAMILY / 'measurement-correctness-activation-candidate-v1'
PERSIST = FAMILY / 'measurement-correctness-persistence-amendment-v1'
BASE = FAMILY / 'measurement-correctness-candidate-v1'
AMEND = FAMILY / 'measurement-correctness-reporting-amendment-v1'
DECLARED = Path('/tmp/starling-node-compat/classic-benchmark-trace-v2-source')
CANONICAL = Path('/private/tmp/starling-node-compat/classic-benchmark-trace-v2-source')
PRODUCER = CANONICAL / 'tests/node-compat/foundation-classic-streams/measurement-producer-candidate-v3'
FREEZE = Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze')
LABEL = 'benchmark-classic-on'
INDEX = '418ff8fe40fb26bd7eacc848129b0ca2354f93e9e2e9b9491ea75147a23119fa'
PIN_SHA = '2e9811a54b03733d7d4dde0b42f66831a9b97da2c2f26313f078443dc329165c'
REVIEW_SHA = '9681578ea64c826f72baa1e1bff1533af276ff27d6dda52c5bf1dbe064697001'
PRODUCER_SHA = '46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc'
RECIPE = 'd98d1129db0a55abe18c2b96e7fe314ab27d6bc9a2ef481abed3f07d996fbba6'
seen = {}
expected_inputs = {}
checks = []

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read(path, expected=None, size=None):
    path = Path(path)
    first = path.lstat()
    assert stat.S_ISREG(first.st_mode) and not path.is_symlink(), path
    raw = path.read_bytes()
    last = path.lstat()
    assert (first.st_dev, first.st_ino, first.st_size, first.st_mtime_ns) == (last.st_dev, last.st_ino, last.st_size, last.st_mtime_ns), path
    assert expected is None or sha(raw) == expected, path
    assert size is None or len(raw) == size, path
    key = str(path.resolve(strict=True))
    row = {'path': key, 'sha256': sha(raw), 'bytes': len(raw)}
    assert key not in seen or seen[key] == row, path
    seen[key] = row
    return raw

def doc(path, expected=None):
    return json.loads(read(path, expected))

def add(path, expected=None, size=None):
    raw = read(path, expected, size)
    key = str(Path(path).resolve(strict=True))
    row = {'sha256': sha(raw), 'bytes': len(raw)}
    assert key not in expected_inputs or expected_inputs[key] == row, key
    expected_inputs[key] = row

def indexed(root, digest, consumed=False):
    value = doc(root / 'index.json', digest)
    paths = set()
    if consumed:
        add(root / 'index.json', digest)
    for row in value['files']:
        name = row['path']
        assert name not in paths and not Path(name).is_absolute() and all(part not in ('', '.', '..') for part in name.split('/'))
        paths.add(name)
        cursor = root
        for part in name.split('/'):
            cursor /= part
            assert not cursor.is_symlink()
        (add if consumed else read)(cursor, row['sha256'], row['bytes'])
    return value

def check(name, condition=True):
    assert condition, name
    checks.append(name)

def main():
    assert not (HERE / 'results.json').exists()
    actual = indexed(ACTUAL, INDEX)
    assert len(actual['files']) == 22
    check('actual twenty two indexed generated files authenticated before their data is followed')
    source_parents = [
        (ACTIVATOR, '4ef958e973bddea315c383e22e58e3f2908da874a0796fe738ad69ab3eed79bd', 15),
        (PREVIOUS, 'ce2f254f2cf27d44df5f0d23915ca4e09c98ac15b2f88f762d41f57fb8e6048e', 19),
        (PERSIST, '60a8687e9b6bfff4c68df2a36e9dd47ad0f5cd327441f8cf32d63caa67518ba8', 35),
        (BASE, '138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da', 36),
        (AMEND, '0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350', 14),
        (PRODUCER, PRODUCER_SHA, 40),
    ]
    for root, digest, count in source_parents:
        assert len(indexed(root, digest, consumed=True)['files']) == count
    prior_root = FAMILY / 'independent-measurement-correctness-activation-source-review-v1'
    indexed(prior_root, 'ee4d5de5d3bd977abd0f22653de13dd54a6867f3cc8cf13a6ffaed86f596347a')
    check('exact activator correctness mandatory reporting genuine producer and prior independent review preserved')
    indexed(FAMILY / 'independent-correctness-activation-v2-source-review-v1', 'c9dba776f3a4bc951da11644cc67c768c75efa80be6e13fe2075bee16b3dd359')
    indexed(FAMILY / 'independent-correctness-persistence-source-review-v1', '6fb6bfebdd3f1b0240553b342be5159a2240459d274938aca26af13d3f28872d')
    check('both mandatory v2 source peers authenticated without executing their helpers')
    pins_original = FAMILY / 'production-adoption-v1/reviewed-diagnostic-v3-on-pins.json'
    review_original = FAMILY / 'production-adoption-v1/diagnostic-v3-on-root-review-receipt.json'
    add(pins_original, PIN_SHA)
    add(review_original, REVIEW_SHA)
    pins_raw = read(ACTUAL / 'reviewed-pins.json', PIN_SHA)
    review_raw = read(ACTUAL / 'root-review-receipt.json', REVIEW_SHA)
    assert pins_raw == read(pins_original, PIN_SHA) and review_raw == read(review_original, REVIEW_SHA)
    pins, review = json.loads(pins_raw), json.loads(review_raw)
    assert pins['state'] == 'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V3'
    assert pins['variants']['benchmark-classic-off'] is None
    pin = pins['variants'][LABEL]
    assert pin['state'] == 'reviewed-classic-trace-benchmark-diagnostic-freeze' and pin['reviewRequired'] is False
    for key in ('engineSha256', 'engineBytes', 'metadataSha256', 'freezeReceiptSha256', 'sourceIndexSha256', 'recipeSha256', 'sourceFiles', 'addonFiles', 'sourceContractVersion'):
        assert pin[key] == review[key]
    assert review['reviewedPinsSha256'] == PIN_SHA and review['runtimeAcceptanceClaim'] is False and review['performanceClaim'] is False
    assert DECLARED.resolve(strict=True) == CANONICAL and not DECLARED.is_symlink() and not CANONICAL.is_symlink()
    check('generated authority byte exact ON only actual tuple and declared canonical source relationship')
    receipt_path = FREEZE / (LABEL + '-freeze-receipt.json')
    add(receipt_path, pin['freezeReceiptSha256'])
    receipt = doc(receipt_path, pin['freezeReceiptSha256'])
    assert len(receipt['copies']) == 525 and len({row['path'] for row in receipt['copies']}) == 525
    for row in receipt['copies']:
        assert Path(row['path']).is_relative_to(FREEZE)
        add(row['path'], row['sha256'], row['bytes'])
    metadata = doc(FREEZE / (LABEL + '.engine.wasm.build.json'), pin['metadataSha256'])
    assert receipt['engineSha256'] == metadata['engineSha256'] == pin['engineSha256']
    assert receipt['engineBytes'] == metadata['engineBytes'] == pin['engineBytes']
    assert receipt['sourceIndexSha256'] == PRODUCER_SHA and receipt['recipeSha256'] == RECIPE
    assert metadata['diagnosticOnly'] is True and metadata['classicStreamsEnabled'] is True and metadata['gcStress'] is False
    assert receipt['nativeInputsVerified'] == 342 and receipt['addonInputsVerified'] == 2 and receipt['externalEmbeddingInputsVerified'] == 3
    assert {key: receipt[key] for key in ('actualNativeCommands', 'actualStrictCommands', 'actualPrivateCommands', 'actualEmbeddingCommands', 'actualDiagnosticCommands')} == {
        'actualNativeCommands': 61, 'actualStrictCommands': 4, 'actualPrivateCommands': 5, 'actualEmbeddingCommands': 1, 'actualDiagnosticCommands': 1}
    assert len(metadata['sourceManifest']) == 342
    for row in metadata['sourceManifest']:
        add(CANONICAL / row['path'], row['sha256'])
    contract = doc(PRODUCER / 'contract.json')
    assert len(contract['addonSources']) == 2
    for row in contract['addonSources']:
        add(CANONICAL / row['path'], row['sha256'])
    assert len(metadata['componentizeSourceManifest']) == 3 and len(receipt['toolDependencyClosure']) == 92
    for row in receipt['toolDependencyClosure']:
        add(CANONICAL / row['sourcePath'], row['sha256'], row['bytes'])
    check('all actual ON frozen525 source344 external3 and corrected tooling92 bind without metadata rewrite')
    for root in (BASE, PRODUCER):
        preparation = doc(root / 'input-freeze.json')
        for row in preparation['inputs']:
            add(root / row['path'], row['sha256'], row['bytes'])
    original = doc(BASE / 'input-freeze.json')
    original_root_paths = [Path(row['path']) for row in original['toolTrees']]
    assert len(original_root_paths) == 2 and len(original['toolLinks']) == 22
    for root_row in original['toolTrees']:
        root = Path(root_row['path'])
        assert root.is_dir() and not root.is_symlink() and str(root.resolve(strict=True)) == root_row['realPath']
        members = []
        for directory, dirs, files in os.walk(root, followlinks=False):
            for name in sorted(dirs + files):
                path = Path(directory) / name
                mode = path.lstat().st_mode
                kind = 'symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file' if stat.S_ISREG(mode) else None
                assert kind
                members.append({'path': str(path.relative_to(root)), 'kind': kind})
                if kind == 'file':
                    add(path)
            dirs[:] = [name for name in dirs if not (Path(directory) / name).is_symlink()]
        assert sorted(members, key=lambda row: row['path']) == root_row['entries']
    canonical_roots = [Path(row['realPath']) for row in original['toolTrees']]
    for row in original['toolLinks']:
        path = Path(row['path'])
        assert path.is_symlink() and os.readlink(path) == row['linkText']
        target = path.resolve(strict=True)
        assert str(target) == row['resolvedTarget'] and any(target.is_relative_to(root) for root in canonical_roots)
        assert ('directory' if target.is_dir() else 'file' if target.is_file() else None) == row['targetKind']
        if row['targetKind'] == 'file':
            read(target, row['targetSha256'], row['targetBytes'])
    check('original context preparation stays original and exact two tool trees twenty two links')
    names = ['native-provider.mjs', 'guest.mjs', 'workload.mjs', 'encoding-cases.mjs', 'activation-contract.mjs', 'runtime-preflight.template.mjs', 'consumed.mjs', 'bundle-diagnostic.mjs', 'completion.mjs', 'run.UNEXECUTED.mjs', 'node-workload-oracle.json', 'node-encoding-oracle.json']
    expected_payloads = {name: read(BASE / name) for name in names}
    expected_payloads['component-driver.mjs'] = read(PERSIST / 'proposed/component-driver.mjs')
    expected_payloads['durable-host.mjs'] = read(PERSIST / 'durable-host.mjs')
    expected_payloads['bounded-comparison.mjs'] = read(AMEND / 'bounded-comparison.mjs')
    expected_payloads['reviewed-pins.json'] = pins_raw
    expected_payloads['root-review-receipt.json'] = review_raw
    config = doc(ACTUAL / 'activation-template.json')
    assert config == {'schemaVersion': 1, 'state': 'ROOT_REVIEWED_CLASSIC_DIAGNOSTIC_CORRECTNESS_ACTIVATION_V1', 'variant': LABEL,
        'producerIndexSha256': PRODUCER_SHA, 'recipeSha256': RECIPE, 'producerRoot': str(PRODUCER), 'sourceRoot': str(CANONICAL),
        'declaredConfiguredSourceRoot': str(DECLARED), 'canonicalDiagnosticSourceRoot': str(CANONICAL),
        'reviewedPinsPath': str(ACTUAL / 'reviewed-pins.json'), 'reviewedPinsSha256': PIN_SHA,
        'rootReviewReceiptPath': str(ACTUAL / 'root-review-receipt.json'), 'rootReviewReceiptSha256': REVIEW_SHA,
        'reviewedActualEngine': {**{key: pin[key] for key in ('engineSha256', 'engineBytes', 'metadataSha256', 'freezeReceiptSha256', 'sourceFiles', 'addonFiles')}, 'diagnosticOnly': True},
        'runtimeAcceptanceClaim': False, 'timingAllowed': False}
    expected_payloads['activation-template.json'] = read(ACTUAL / 'activation-template.json')
    expected_payloads['README.md'] = b'Fresh correctness-v2 source family with mandatory per-case persistence and finite600s Wasmtime cap; full20/14 guest gates unexecuted. No resume or timing authority.\n'
    for name, raw in expected_payloads.items():
        assert read(ACTUAL / name) == raw, name
        expected_inputs[name] = {'sha256': sha(raw), 'bytes': len(raw)}
    workload = json.loads(expected_payloads['node-workload-oracle.json'])
    encoding = json.loads(expected_payloads['node-encoding-oracle.json'])
    assert workload['node'] == 'v22.14.0' and len(workload['expected']) == 20 and len(encoding['expected']) == 14
    proof = doc(AMEND / 'transformation-proof.json')
    current = read(BASE / 'component-driver.mjs', proof['beforeSha256']).decode()
    before = current
    for row in proof['edits']:
        assert current.count(row['old']) == row['count']
        current = current.replace(row['old'], row['new'])
    assert len(proof['edits']) == 9 and current.encode() == read(AMEND / 'proposed/component-driver.mjs')
    for row in reversed(proof['edits']):
        assert current.count(row['new']) == row['count']
        current = current.replace(row['new'], row['old'])
    assert current == before
    check('all nineteen local payloads full20 workload and14 boundary bytes exact with mandatory reporting and persistence')
    persistence = doc(PERSIST / 'transformation-proof.json')
    current = read(AMEND / 'proposed/component-driver.mjs', persistence['beforeSha256']).decode()
    persistence_before = current
    for row in persistence['edits']:
        assert current.count(row['old']) == row['count']
        current = current.replace(row['old'], row['new'])
    assert len(persistence['edits']) == 8 and current.encode() == expected_payloads['component-driver.mjs']
    for row in reversed(persistence['edits']):
        for offset in reversed(row['afterOffsets']):
            assert current[offset:offset + len(row['new'])] == row['new']
            current = current[:offset] + row['old'] + current[offset + len(row['new']):]
    assert current == persistence_before
    activation = doc(ACTIVATOR / 'transformation-proof.json')
    current = read(PREVIOUS / 'activate.py', activation['beforeSha256']).decode()
    activation_before = current
    for row in activation['edits']:
        assert current.count(row['old']) == row['count']
        current = current.replace(row['old'], row['new'])
    assert len(activation['edits']) == 6 and current.encode() == read(ACTIVATOR / 'activate.py', activation['afterSha256'])
    for row in reversed(activation['edits']):
        for offset in reversed(row['afterOffsets']):
            assert current[offset:offset + len(row['new'])] == row['new']
            current = current[:offset] + row['old'] + current[offset + len(row['new']):]
    assert current == activation_before
    check('eight persistence edits and six activator edits reproduce and reverse exactly')
    helper = expected_payloads['durable-host.mjs'].decode()
    driver = expected_payloads['component-driver.mjs'].decode()
    assert helper.index('await persistFile({output,write,path:terminalPath') < helper.index('return{...outcome,terminalPath')
    assert 'timeoutMs=600000' in helper and 'timeoutMs<=600000' in helper
    assert all(value in helper for value in ('detached:true', 'process.kill(-pid', "error.code==='ESRCH'", "signal('SIGTERM')", "signal('SIGKILL')", 'const ceiling=timeoutMs+2*graceMs+1000'))
    assert "persist('case-results/'+name+'.raw.txt',raw)" in driver and "persist('case-results/'+name+'.observed.json'" in driver
    wt = driver[driver.index('const wasmtime=[];'):]
    assert wt.index('const actual=await invoke(') < wt.index('if(!actual.terminalExitZeroObserved)') < wt.index('value=JSON.parse(')
    assert wt.index("persist('case-results/'+name+'.observed.json'") < wt.index('await validateCase(')
    assert 'round<3' in driver and 'index<20' in driver and 'index<=20' in driver
    check('actual approved durable per-case host observations and finite owned600s collection exact')
    witness = doc(FAMILY / 'production-adoption-v1/workload-public-case5-root-results.json', '793a2f0de42b931fac12c55c570a888add9ced3c2e9b25b09e8bef70363ce45e')
    assert witness['caseIndex'] == 5 and witness['timeoutSeconds'] == 600 and witness['originalFailedRunCaseStillUnknown'] is True
    assert witness['fullTwentyPlusFourteenPassed'] is False and witness['deadlineAdequateForAllCasesClaim'] is False and witness['performanceClaim'] is False
    for row in witness['files']:
        read(row['path'], row['sha256'], row['bytes'])
    check('case5 operational witness remains separate unknown original failure no fullpass or performance claim')
    manifest_raw = read(ACTUAL / 'input-freeze.json', '406946e8b609c7ff91c05fc80e499a4e48e936a0cb10f506944d21d221309639')
    manifest = json.loads(manifest_raw)
    assert manifest['state'] == 'ROOT_REVIEWED_DIAGNOSTIC_CORRECTNESS_FULL_ACTUAL_CONSUMED_SEAL'
    assert manifest['toolTrees'] == original['toolTrees'] and manifest['toolLinks'] == original['toolLinks'] and manifest['invocation'] == original['invocation']
    assert manifest['sourceContext'] == {'declaredConfiguredSourceRoot': str(DECLARED), 'canonicalDiagnosticSourceRoot': str(CANONICAL), 'metadataRewritten': False, 'preparationRowsRelocated': False}
    actual_inputs = {}
    for row in manifest['inputs']:
        name = row['path']
        assert name not in actual_inputs
        actual_inputs[name] = {'sha256': row['sha256'], 'bytes': row['bytes']}
        path = ACTUAL / name
        if not Path(name).is_absolute():
            assert row['boundary'] == '.' and len(Path(name).parts) == 1
        read(path, row['sha256'], row['bytes'])
    assert len(actual_inputs) == len(expected_inputs) == 7542
    assert actual_inputs == expected_inputs
    check('complete current consumed inventory independently reconstructed exactly7542 no omitted or extra dependency')
    live_adapter = str((CANONICAL / 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm').resolve(strict=True))
    assert actual_inputs[live_adapter] == {'sha256': '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0', 'bytes': 53512}
    check('exact LIVE adapter988 and frozen adapter both within actual consumed closure')
    template = expected_payloads['runtime-preflight.template.mjs'].decode()
    assert template.count('@CONFIG_SHA@') == template.count('@INPUTS_SHA@') == 1
    compiled = template.replace('@CONFIG_SHA@', sha(expected_payloads['activation-template.json'])).replace('@INPUTS_SHA@', sha(manifest_raw)).encode()
    assert read(ACTUAL / 'runtime-preflight.mjs') == compiled
    assert 'const nativeRecheck=native.recheck' in template and 'await nativeRecheck()' in template
    assert 'const frozenRows=index.files.map(row=>({...row}))' in template
    assert template.index('await seal()') < template.index('await import(pathToFileURL(join(producer,\'runtime-preflight.mjs\')))')
    check('compiled preflight exact two token rendering with private captured native recheck and producer rows')
    source_receipt = doc(ACTUAL / 'source-receipt.json')
    assert source_receipt['state'] == 'ROOT_REVIEWED_CORRECTNESS_ACTIVATION_CREATED_GUEST_UNEXECUTED'
    expected_observed = {key: pin[key] for key in ('engineSha256', 'engineBytes', 'metadataSha256', 'freezeReceiptSha256', 'freezeRoot', 'recipeSha256', 'sourceIndexSha256', 'sourceFiles', 'addonFiles', 'sourceContractVersion', 'classicStreamsEnabled')}
    assert source_receipt['actualON'] == expected_observed and source_receipt['consumedInputs'] == 7542 and source_receipt['frozenRowsConsumed'] == 525 and source_receipt['toolLinks'] == 22
    assert source_receipt['activationProducerIndexSha256'] == '4ef958e973bddea315c383e22e58e3f2908da874a0796fe738ad69ab3eed79bd'
    assert source_receipt['pinsSha256'] == PIN_SHA and source_receipt['rootReviewSha256'] == REVIEW_SHA
    assert source_receipt['mandatoryReportingIndexSha256'] == '0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350'
    assert source_receipt['mandatoryPersistenceIndexSha256'] == '60a8687e9b6bfff4c68df2a36e9dd47ad0f5cd327441f8cf32d63caa67518ba8'
    assert source_receipt['perCaseWasmtimeDeadlineMs'] == 600000 and source_receipt['resumeSupported'] is False and source_receipt['reusedResults'] == 0
    assert source_receipt['fullCorpusGuestProviderOracleBundleInputsChanged'] is False
    assert source_receipt['metadataRewritten'] is False and source_receipt['guestOrPackagerOrTargetHostExecuted'] is False and source_receipt['runtimeAcceptanceClaim'] is False and source_receipt['timingAllowed'] is False
    assert not ACTUAL.with_name(ACTUAL.name + '.staging').exists() and not ACTUAL.with_name(ACTUAL.name + '.staging').is_symlink()
    check('generated source receipt truthfully binds actual tuple source creator no guest timing and no residual staging')
    for row in list(seen.values()):
        read(row['path'], row['sha256'], row['bytes'])
    evidence_raw = (json.dumps({'schemaVersion': 1, 'files': sorted(seen.values(), key=lambda row: row['path'])}, indent=2) + '\n').encode()
    result = {'schemaVersion': 1, 'state': 'INDEPENDENT_ACTUAL_CORRECTNESS_V2_SOURCE_FAMILY_REVIEW_PASSED',
        'actualIndexSha256': INDEX, 'generatedFiles': 22, 'consumedInputs': 7542, 'passed': len(checks), 'checks': checks,
        'uniquePathsRehashed': len(seen), 'evidenceSha256': sha(evidence_raw), 'genuineProducerFiles': 40, 'frozenCopies': 525,
        'nativeSources': 342, 'addonSources': 2, 'externalEmbeddingSources': 3, 'correctedToolDependencies': 92, 'toolTrees': 2, 'toolLinks': 22,
        'allPayloadsAndFull20And14OraclesExact': True, 'unamendedDriverAdmitted': False, 'metadataRewritten': False,
        'ownerOrActionOrPreflightOrVerifierOrNodeOrGuestOrNativeOrBundleOrTargetHostExecutedByReviewer': False,
        'runtimeAcceptanceClaim': False, 'timingAllowed': False,
        'limitations': ['This independently authenticates generated source/data and frozen bytes; no positive preflight or action helper was called.', 'Root separately observed source activation exit0. Actual20/14 component outcomes remain a future gate.', 'Native queue-counter visibility, reset/ALS, VM root isolation, broad Streams parity and performance are not claimed.']}
    for name, raw in [('evidence.json', evidence_raw), ('results.json', (json.dumps(result, indent=2) + '\n').encode())]:
        with (HERE / name).open('xb') as stream:
            stream.write(raw)
    print(json.dumps({'passed': len(checks), 'paths': len(seen), 'resultsSha256': sha((HERE / 'results.json').read_bytes())}))

if __name__ == '__main__':
    main()
