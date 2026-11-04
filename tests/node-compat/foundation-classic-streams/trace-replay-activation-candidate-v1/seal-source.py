"""Seal only this new source proposal; never call either activation main."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import os
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from activate import (BASE, BASE_SHA, RUNTIME, RUNTIME_SHA, SOURCE_ROOT, CANONICAL_SOURCE_ROOT,
    OUTPUT, regular, sha, indexed, source_payload, map_inputs)
spec = importlib.util.spec_from_file_location('trace_http_source_seal_data_only', HERE / 'activate-http-source.py')
http = importlib.util.module_from_spec(spec); spec.loader.exec_module(http)
rows = {}


def add(path, expected=None):
    path = Path(os.path.abspath(path)); raw = regular(path, expected)
    row = {'path': str(path), 'sha256': sha(raw), 'bytes': len(raw)}
    assert str(path) not in rows or rows[str(path)] == row
    rows[str(path)] = row


def put(name, value):
    with (HERE / name).open('x') as out: json.dump(value, out, indent=2); out.write('\n')


def main():
    assert not (HERE / 'index.json').exists() and not (HERE / 'input-freeze.json').exists()
    parent_index = indexed(BASE, BASE_SHA)
    runtime_index = indexed(RUNTIME, RUNTIME_SHA)
    http_parent = indexed(http.PARENT, http.PARENT_SHA)
    for root, files in ((BASE, parent_index), (RUNTIME, runtime_index), (http.PARENT, http_parent)):
        add(root / 'index.json')
        for row in files: add(root / row['path'], row['sha256'])
    # Original manifests remain preparation-context source/history references.
    # These rows are never used to manufacture positive corrected native pins.
    for root, name in ((BASE, 'input-freeze.json'), (BASE, 'capability/input-freeze.json'),
                       (RUNTIME, 'input-freeze.json'), (http.PARENT, 'input-freeze.json')):
        doc = json.loads(regular(root / name)); base = (root / name).parent
        for row in doc['inputs']: add(Path(os.path.abspath(base / row['path'])), row['sha256'])
    payload, _ = source_payload()
    payload.update({'runtime-pins.json': regular(RUNTIME / 'runtime-pins.json'), 'root-review-receipt.json': regular(RUNTIME / 'root-review-receipt.json')})
    for name, expected in [('input-freeze.json', 'a9c41e39e811620a27d71cce21f084a17c7c0f785ae69dd6b9d2c29085e23a97'),
                           ('capability/input-freeze.json', '24ade3ad845315b96190b3977c7f7e256faf1e16ba274f46b86445d1a944475a')]:
        _, mapped, _ = map_inputs(name, expected, payload)
        for row in mapped.values():
            if not Path(row['path']).is_relative_to(OUTPUT): add(row['path'], row['sha256'])
    _, mapped, _ = http.inherited_http_inputs(http.source_payload())
    for row in mapped.values(): add(row['path'], row['sha256'])
    assert not OUTPUT.exists() and not OUTPUT.with_name(OUTPUT.name + '.staging').exists()
    assert not http.OUTPUT.exists() and not http.OUTPUT.with_name(http.OUTPUT.name + '.staging').exists()
    for path in sorted(HERE.rglob('*')):
        if path.is_file(): add(path)
    parsed = []
    for path in sorted(HERE.rglob('*.py')):
        ast.parse(path.read_text(), filename=str(path)); parsed.append(str(path.relative_to(HERE)))
    seal = {'schemaVersion': 1, 'state': 'CORRECTED_TRACE_REPLAY_HTTP_SOURCE_PREPARATION_INPUTS_NOT_ACTIVATED',
        'inputs': sorted(rows.values(), key=lambda row: row['path']),
        'configuredNativeSourceRootUnchanged': str(SOURCE_ROOT), 'canonicalNewTestSourceRoot': str(CANONICAL_SOURCE_ROOT),
        'futureReplayRoot': str(OUTPUT), 'futureHTTPRoot': str(http.OUTPUT),
        'scope': 'Finite inherited source/history records, actual e1f87 backend and exact canonical staged mappings. No old runtime pass reuse or metadata projection.',
        'activationOutputsCreated': False}
    put('input-freeze.json', seal)
    receipt = {'schemaVersion': 1, 'state': 'CORRECTED_TRACE_REPLAY_AND_HTTP_SOURCE_ACTIVATION_PROPOSAL_READY_NOT_EXECUTED',
        'runtimeIndexSha256': RUNTIME_SHA, 'parentReplayIndexSha256': BASE_SHA,
        'parentHTTPSourceIndexSha256': http.PARENT_SHA,
        'reviewedPinsSha256': '182e8b724d94ebf73450c0ffcea81fb19b902028e2839bd2a9d1452ab7fab5eb',
        'rootReviewReceiptSha256': 'ce88ac3495afdf97718a34f7bf2c2360613f95a91f5c193e556c87269b4a8be0',
        'inputFreezeSha256': sha((HERE / 'input-freeze.json').read_bytes()), 'consumedPreparationFiles': len(rows),
        'inheritedBodies': 64, 'currentV3BodiesByteIdentical': 62, 'newChangedHostBodies': 2,
        'reversibleReplayBodyAndTemplateFiles': 3, 'reversibleHTTPSourceFiles': 21,
        'guestOrNodeOracleBodiesChanged': False, 'fullStrictOrProtectedPolicyTagsChanged': False,
        'sourceChecks': 49, 'pureMetadataOracleGuardChecks': 7, 'httpSourceChecks': 86,
        'jsSyntaxChecks': 88, 'pythonAstFiles': len(parsed),
        'httpComponentPinNullAndSealed': True, 'wholeEntryHostBundleUnexecutedRequiredBeforePackaging': True,
        'futureReplayIndexStillRequiredForHTTPSource': True,
        'noPromiseOrQueueMicrotaskSubstitutionFor20Plus14': True,
        'activationMainNativePreflightPackageLoaderBundleGuestHostNativeOrTimingExecuted': False,
        'oldPacketsOrReportsOrStagedNativeInputsModified': False, 'activationOutputsCreated': False,
        'runtimeAcceptanceClaim': False, 'performanceClaim': False}
    put('source-receipt.json', receipt)
    files = []
    for path in sorted(HERE.rglob('*')):
        if path.is_file():
            raw = path.read_bytes(); files.append({'path': str(path.relative_to(HERE)), 'sha256': sha(raw), 'bytes': len(raw)})
    put('index.json', {'schemaVersion': 1, 'state': 'SEALED_CORRECTED_TRACE_REPLAY_AND_HTTP_SOURCE_PRODUCERS_ACTIONS_HELD',
        'files': files, 'runtimeAcceptanceClaim': False})
    print(json.dumps({'indexSha256': sha((HERE / 'index.json').read_bytes()), 'files': len(files),
        'inputFreezeSha256': receipt['inputFreezeSha256'], 'inputs': len(rows), 'activationOutputsCreated': False}))


if __name__ == '__main__': main()
