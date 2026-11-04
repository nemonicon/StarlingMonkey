"""UNEXECUTED combined HTTP SOURCE activation, never a bundle/component/host.

Requires a later exact newly activated replay index; component pins stay null.
"""
import sys
sys.dont_write_bytecode = True
if not __debug__: raise RuntimeError('Assertions required')
from pathlib import Path
import argparse
import json
import os
from activate import (HERE, REPO, SOURCE_ROOT, CANONICAL_SOURCE_ROOT, FAMILY_RELATIVE,
    BASE, RUNTIME, RUNTIME_SHA, PINS_SHA, REVIEW_SHA, OUTPUT as REPLAY,
    regular, sha, indexed)
from authority import load_authority, POLICY

PARENT = HERE.parent / 'classic-http-candidate-v1'
PARENT_SHA = 'ced484750a07c7897b0e40f64da85416d32793bf083082072d304b094ceec982'
OUTPUT = CANONICAL_SOURCE_ROOT / FAMILY_RELATIVE / 'production-trace-http-activated-v1'


def source_payload():
    return {str(path.relative_to(HERE / 'http-payload')): regular(path)
            for path in sorted((HERE / 'http-payload').rglob('*')) if path.is_file()}


def inherited_http_inputs(payload):
    """Pure finite path/hash checks; does not require a future replay output."""
    policy = json.loads(regular(HERE.parent / 'trace-integration-candidate-v1/policy.json', POLICY))
    canonical = {row['path']: row['sha256'] for row in policy['expectedNativeSourceManifest']}
    tools = json.loads(regular(HERE.parent / 'trace-integration-candidate-v1/artifact-tools/tool-pins.json'))
    canonical.update({row['path']: row['sha256'] for row in tools['toolDependencies']})
    inputs = {}; mappings = []
    old = json.loads(regular(PARENT / 'input-freeze.json', '511723ec0ef2079d3fac2f6a6f78f2fa26c3be7d15cf55f7ec03a411e028193b'))
    old_freeze = Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze')
    old_freeze_real = old_freeze.resolve(strict=True)
    for row in old['inputs']:
        path = Path(os.path.abspath(PARENT / row['path']))
        if path.is_relative_to(PARENT):
            relative = str(path.relative_to(PARENT))
            if relative in payload or relative == 'capability/preflight.mjs': continue
        if path.is_relative_to(old_freeze) or path.is_relative_to(old_freeze_real): continue
        target = path; checksum = row['sha256']
        if path.is_relative_to(REPO):
            relative = str(path.relative_to(REPO)); target = CANONICAL_SOURCE_ROOT / relative
            checksum = canonical.get(relative, checksum)
            mappings.append({'original': str(path), 'actualNewSource': str(target), 'beforeSha256': row['sha256'], 'afterSha256': checksum})
        raw = regular(target, checksum)
        mapped = {'path': str(target), 'sha256': checksum, 'bytes': len(raw)}
        assert str(target) not in inputs or inputs[str(target)] == mapped
        inputs[str(target)] = mapped
    return old, inputs, mappings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--producer-index-sha256', required=True)
    parser.add_argument('--replay-index-sha256', required=True)
    parser.add_argument('--pins', type=Path, required=True); parser.add_argument('--root-review', type=Path, required=True)
    args = parser.parse_args()
    pins, pin_bytes, review, review_bytes = load_authority(args.pins, PINS_SHA, args.root_review, REVIEW_SHA)
    own_rows = indexed(HERE, args.producer_index_sha256)
    runtime_rows = indexed(RUNTIME, RUNTIME_SHA)
    replay_rows = indexed(REPLAY, args.replay_index_sha256)
    replay_receipt = json.loads(regular(REPLAY / 'source-receipt.json'))
    assert replay_receipt['state'] == 'ACTUAL_REVIEWED_CORRECTED_TRACE_REPLAY_SOURCE_CREATED_NOT_EXECUTED'
    assert replay_receipt['runtimeIndexSha256'] == RUNTIME_SHA and replay_receipt['reviewedPinsSha256'] == PINS_SHA
    assert regular(REPLAY / 'runtime-pins.json', PINS_SHA) == pin_bytes
    assert regular(REPLAY / 'root-review-receipt.json', REVIEW_SHA) == review_bytes
    indexed(PARENT, PARENT_SHA)
    assert not OUTPUT.exists() and not OUTPUT.is_symlink()
    staging = OUTPUT.with_name(OUTPUT.name + '.staging')
    assert not staging.exists() and not staging.is_symlink()
    payload = source_payload()
    assert json.loads(payload['capability/component-pins.json'])['component'] is None
    payload['runtime-pins.json'] = pin_bytes; payload['root-review-receipt.json'] = review_bytes
    binding = {'schemaVersion': 1, 'state': 'CORRECTED_TRACE_HTTP_SOURCE_AUTHORITY_BOUND_NOT_EXECUTED',
        'runtimeIndexSha256': RUNTIME_SHA, 'runtimeRoot': str(RUNTIME), 'replayIndexSha256': args.replay_index_sha256,
        'replayRoot': str(REPLAY), 'reviewedPinsSha256': PINS_SHA, 'rootReviewReceiptSha256': REVIEW_SHA,
        'nativeSourceMetadataRewritten': False, 'hostBundleStillRequired': True,
        'newComponentAndExternalPhaseStillRequired': True, 'runtimeAcceptanceClaim': False}
    payload['source-binding.json'] = (json.dumps(binding, indent=2) + '\n').encode()
    old, inputs, mappings = inherited_http_inputs(payload)
    def add(path, expected=None):
        path = Path(os.path.abspath(path)); raw = regular(path, expected)
        row = {'path': str(path), 'sha256': sha(raw), 'bytes': len(raw)}
        assert str(path) not in inputs or inputs[str(path)] == row
        inputs[str(path)] = row
    for root, rows in ((HERE, own_rows), (RUNTIME, runtime_rows), (REPLAY, replay_rows)):
        add(root / 'index.json')
        for row in rows: add(root / row['path'], row['sha256'])
    # Follow only the newly activated replay's actual source seal. Its native
    # backend remains delegated to the separately fixed e1f87 runtime family.
    replay_seal = json.loads(regular(REPLAY / 'input-freeze.json', replay_receipt['inputFreezeSha256']))
    for row in replay_seal['inputs']: add(Path(os.path.abspath(REPLAY / row['path'])), row['sha256'])
    add(args.pins, PINS_SHA); add(args.root_review, REVIEW_SHA)
    payload['source-mappings.json'] = (json.dumps({'schemaVersion': 1, 'mappings': mappings}, indent=2) + '\n').encode()
    for name, raw in payload.items():
        path = OUTPUT / name; inputs[str(path)] = {'path': str(path), 'sha256': sha(raw), 'bytes': len(raw)}
    listed = [{**row, 'path': os.path.relpath(row['path'], OUTPUT)} for row in inputs.values()]
    seal = {'schemaVersion': 1, 'state': 'CORRECTED_TRACE_COMBINED_HTTP_SOURCE_SEAL_NOT_BUNDLE_OR_RUNTIME_PROOF',
        'inputs': sorted(listed, key=lambda row: row['path']), 'runtimeIndexSha256': RUNTIME_SHA,
        'replayIndexSha256': args.replay_index_sha256, 'reviewedPinsSha256': PINS_SHA,
        'componentPinsRemainNull': True, 'hostBundleStillRequired': True, 'runtimeAcceptanceClaim': False}
    payload['input-freeze.json'] = (json.dumps(seal, indent=2) + '\n').encode()
    template = payload['capability/preflight.template.mjs'].decode()
    payload['capability/preflight.mjs'] = template.replace('@INPUTS_SHA@', sha(payload['input-freeze.json'])).encode()
    assert b'@INPUTS_SHA@' not in payload['capability/preflight.mjs']
    receipt = {'schemaVersion': 1, 'state': 'CORRECTED_TRACE_COMBINED_HTTP_SOURCE_FAMILY_CREATED_NOT_EXECUTED',
        'producerIndexSha256': args.producer_index_sha256, 'parentHTTPSourceIndexSha256': PARENT_SHA,
        'runtimeIndexSha256': RUNTIME_SHA, 'replayIndexSha256': args.replay_index_sha256,
        'reviewedPinsSha256': PINS_SHA, 'rootReviewReceiptSha256': REVIEW_SHA,
        'inputFreezeSha256': sha(payload['input-freeze.json']), 'consumedFiles': len(inputs),
        'baselineSchema5Protected29AndClassic19Unchanged': True, 'httpComponentPhaseNull': True,
        'hostBundleReviewRequired': True, 'componentizerGuestHostExecuted': False, 'runtimeAcceptanceClaim': False}
    payload['source-receipt.json'] = (json.dumps(receipt, indent=2) + '\n').encode()
    payload['README.md'] = b'New corrected combined HTTP SOURCE family. Run test-bundle before packaging. Fresh reviewed component and external trace phase required before either host.\n'
    index = {'schemaVersion': 1, 'state': 'CORRECTED_TRACE_COMBINED_HTTP_SOURCE_FAMILY_NOT_EXECUTED',
        'files': [{'path': name, 'sha256': sha(raw), 'bytes': len(raw)} for name, raw in sorted(payload.items())],
        'runtimeAcceptanceClaim': False}
    payload['index.json'] = (json.dumps(index, indent=2) + '\n').encode()
    def recheck():
        load_authority(args.pins, PINS_SHA, args.root_review, REVIEW_SHA)
        indexed(RUNTIME, RUNTIME_SHA); indexed(REPLAY, args.replay_index_sha256); indexed(HERE, args.producer_index_sha256)
        for row in inputs.values():
            if not Path(row['path']).is_relative_to(OUTPUT): regular(row['path'], row['sha256'])
    recheck(); staging.mkdir(exist_ok=False)
    for name, raw in payload.items():
        path = staging / name; path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as out: out.write(raw)
        regular(path, sha(raw))
    recheck(); assert not OUTPUT.exists() and not OUTPUT.is_symlink(); staging.rename(OUTPUT)
    print(json.dumps({'output': str(OUTPUT), 'indexSha256': sha(payload['index.json']), 'consumedFiles': len(inputs),
        'hostBundleStillRequired': True, 'runtimeAcceptanceClaim': False}))


if __name__ == '__main__': main()
