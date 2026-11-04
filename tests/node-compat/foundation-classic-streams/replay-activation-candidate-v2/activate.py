"""Prepare one fresh replay sibling; main remains unexecuted before review.

Requires an existing independently reviewed activated runtime INDEX+SHA.
No runner, toolchain, native producer, componentizer, guest or host is invoked.
"""
import sys
sys.dont_write_bytecode = True
if not __debug__:
    raise RuntimeError('Activation requires assertions enabled')
from pathlib import Path
import argparse
import datetime
import json
import os
import re
from authority import (PINS_SHA, REVIEW_SHA, RECIPE, LABELS, regular, sha, indexed,
                       validate_authority, validate_runtime_receipt)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PARENT = HERE.parent / 'production-regression-candidate-v1'
PARENT_INDEX = '81c55887dc5e767db27477ba28f0e7a26a948435c7ddc61c70da329d4bd7f029'
PARENT_ROOT = '6eb9fac9dfccfd44b3195f1ef26e3beac471e219b3b37b576b93a4a2bd58f3fe'
PARENT_CAP = 'ebb6cfa82cf841f39b5b657556197ebdffef31d7c7582c06bf071b95a9e2dd1e'
REVIEW = HERE.parent / 'independent-production-regression-review-v1'
REVIEW_INDEX = '747ba2eff3945192f2ea0ebb9555ba70b86a776f40cea8e478d517cf63feb47a'
RUNTIME_NAMES = ('production-runtime-activated-v1', 'production-runtime-activated-v2', 'production-runtime-activated-v3')
AMENDMENT = HERE.parent / 'registrar-ancestry-oracle-amendment-v1'
AMENDMENT_INDEX = '7462f1255f4fd5048e345a96d58908c8e6251158bf36e5ab4450dab97be193b4'
OUTPUT = HERE.parent / 'production-regression-activated-v2'
EXCLUDE = {'README.md', 'index.json', 'source-receipt.json', 'input-freeze.json', 'capability/input-freeze.json',
    'native-preflight.mjs', 'runtime-pins.json', 'activation-reference.json', 'prepare.py', 'seal-inputs.py',
    'check-paths.py', 'test-source.mjs', 'host-test-results.json', 'path-check-results.json', 'syntax-results.json'}


def runtime_root(index_path):
    path = Path(index_path).absolute()
    assert path == Path(os.path.abspath(path)) and '..' not in path.parts
    assert path.name == 'index.json' and path.parent.parent == HERE.parent
    assert path.parent.name in RUNTIME_NAMES, 'Only explicit reviewed classic runtime siblings v1/v2/v3 are supported'
    return path.parent


def amendment_images():
    document=json.loads(regular(AMENDMENT/'transformation-proof.json'))
    assert document['oldBodiesByteIdentical']==62 and document['changedHostHarnessBodies']==2
    assert document['guestSemanticBytesChanged'] is False and document['oracleDocumentsChanged'] is False
    expected={'release/helpers/native-scalar-harness.mjs','release/runners/path.mjs'}
    assert {row['path']for row in document['records']}==expected and len(document['records'])==2
    images={}
    for row in document['records']:
        before=regular(PARENT/row['path'],row['beforeSha256'])
        after=regular(AMENDMENT/'proposed'/row['path'],row['afterSha256'])
        reverse=after.decode()
        for edit in reversed(row['edits']):
            assert reverse.count(edit['new'])==edit.get('occurrences',1)
            reverse=reverse.replace(edit['new'],edit['old'])
        assert reverse.encode()==before
        images[row['path']]=after
    return images


def expected_body_hash(row):
    image=amendment_images().get(row['destinationPath'])
    return sha(image) if image is not None else row['afterSha256']


def base_payload(parent_index, pin_bytes, review_bytes, runtime_index_sha, pin_path, review_path, runtime):
    """Pure in-memory copies/render data; no future directory is created."""
    payload = {row['path']: regular(PARENT / row['path'], row['sha256']) for row in parent_index['files']
               if not row['path'].startswith('history/') and row['path'] not in EXCLUDE}
    records = json.loads(regular(PARENT / 'derivations.json'))['records']
    assert len(records) == 64
    for row in records:
        assert row['destinationPath'] in payload
        assert sha(payload[row['destinationPath']]) == row['afterSha256']
    payload.update(amendment_images())
    payload['registrar-ancestry-proof.json']=regular(AMENDMENT/'transformation-proof.json')
    assert json.loads(payload['capability/http-component-pins.json'])['component'] is None
    payload.update({'runtime-pins.json': pin_bytes, 'root-review-receipt.json': review_bytes,
        'native-preflight.template.mjs': regular(HERE / 'native-preflight.template.mjs')})
    binding = {'schemaVersion': 1, 'state': 'ROOT_REVIEWED_CLASSIC342_REPLAY_AUTHORITY_BOUND_NOT_EXECUTED',
        'reviewedPinsPath': str(pin_path), 'reviewedPinsSha256': PINS_SHA,
        'rootReviewReceiptPath': str(review_path), 'rootReviewReceiptSha256': REVIEW_SHA,
        'runtimeRoot': str(runtime), 'runtimeIndexPath': str(runtime / 'index.json'),
        'runtimeIndexSha256': runtime_index_sha, 'requiredEntry': str(runtime / 'runtime-preflight.mjs'),
        'requiredExport': 'classicPreflight({variant})', 'sameFourTuplesRequired': True,
        'sourcePreparationOnly': True, 'runtimeAcceptanceClaim': False,
        'httpComponentPinRemainsNullAndSealed': True,
        'laterHTTPHostActivation': 'New independently reviewed minimal host runner binds original actual build family, source/entry/audit paths and same bytes; no relabel/projection/repackage to move folders.'}
    payload['activation-reference.json'] = (json.dumps(binding, indent=2) + '\n').encode()
    return payload, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pins', type=Path, required=True)
    parser.add_argument('--pins-sha256', required=True)
    parser.add_argument('--root-review', type=Path, required=True)
    parser.add_argument('--root-review-sha256', required=True)
    parser.add_argument('--runtime-index', type=Path, required=True)
    parser.add_argument('--runtime-index-sha256', required=True)
    parser.add_argument('--producer-index-sha256', required=True)
    args = parser.parse_args()
    # These explicit actual authority bytes precede any output or artifact import.
    assert args.pins_sha256 == PINS_SHA and args.root_review_sha256 == REVIEW_SHA
    pin_path, review_path = args.pins.absolute(), args.root_review.absolute()
    pin_bytes, review_bytes = regular(pin_path, PINS_SHA), regular(review_path, REVIEW_SHA)
    pins, review = validate_authority(pin_bytes, review_bytes)
    runtime = runtime_root(args.runtime_index)
    runtime_index, runtime_raw = indexed(runtime, args.runtime_index_sha256)
    assert regular(runtime / 'runtime-pins.json', PINS_SHA) == pin_bytes
    assert regular(runtime / 'root-review-receipt.json', REVIEW_SHA) == review_bytes
    runtime_receipt_sha = next(row['sha256'] for row in runtime_index['files'] if row['path'] == 'source-receipt.json')
    runtime_receipt = json.loads(regular(runtime / 'source-receipt.json', runtime_receipt_sha))
    validate_runtime_receipt(runtime_index, runtime_receipt, pins, review)
    assert not OUTPUT.exists() and not OUTPUT.is_symlink(), 'Never overwrite an activated replay'
    stage = OUTPUT.with_name(OUTPUT.name + '.staging')
    assert not stage.exists() and not stage.is_symlink(), 'Preserve any prior partial stage'
    own_index, _ = indexed(HERE, args.producer_index_sha256)
    parent_index, _ = indexed(PARENT, PARENT_INDEX)
    indexed(REVIEW, REVIEW_INDEX)
    amendment_index,_=indexed(AMENDMENT,AMENDMENT_INDEX)
    assert len(parent_index['files']) == 174
    payload, records = base_payload(parent_index, pin_bytes, review_bytes, args.runtime_index_sha256, pin_path, review_path, runtime)
    external = {}
    def external_file(path, expected=None):
        path = Path(os.path.abspath(path))
        data = regular(path, expected)
        row = {'path': str(path), 'sha256': sha(data), 'bytes': len(data)}
        assert str(path) not in external or external[str(path)] == row
        external[str(path)] = row
        return row
    # Complete fixed runtime source index closure; its preflight/recheck owns the
    # larger artifact/tool-tree consumed seal. We do not implement that backend.
    for root, index in ((runtime, runtime_index), (HERE, own_index), (PARENT, parent_index), (AMENDMENT, amendment_index)):
        external_file(root / 'index.json')
        for row in index['files']:
            external_file(root / row['path'], row['sha256'])
    amendment_inputs=json.loads(regular(AMENDMENT/'input-freeze.json'))
    for row in amendment_inputs['inputs']:
        path=Path(row['path']);assert path.is_absolute()
        external_file(path,row['sha256'])
    external_file(REVIEW / 'index.json', REVIEW_INDEX)
    external_file(pin_path, PINS_SHA)
    external_file(review_path, REVIEW_SHA)

    def inherited_rows(name, expected):
        document = json.loads(regular(PARENT / name, expected))
        assert document['schemaVersion'] == 1 and document['nativeSources'] == 342
        rows = {}
        for row in document['inputs']:
            original = Path(os.path.abspath(PARENT / Path(name).parent / row['path']))
            if original.is_relative_to(PARENT):
                relative = str(original.relative_to(PARENT))
                if relative == 'capability/input-freeze.json':
                    continue  # Replaced by the derived capability manifest below.
                if relative in payload:
                    target = OUTPUT / relative
                    data = payload[relative]
                    rows[str(target)] = {'path': str(target), 'sha256': sha(data), 'bytes': len(data)}
                    continue
            external_file(original, row['sha256'])
            rows[str(original)] = external[str(original)]
        return document, rows

    cap_document, cap_rows = inherited_rows('capability/input-freeze.json', PARENT_CAP)
    root_document, root_rows = inherited_rows('input-freeze.json', PARENT_ROOT)
    assert len(cap_document['inputs']) == 1776 and len(root_document['inputs']) == 1777
    def manifest(rows, cap):
        rows = dict(rows)
        rows.update(external)
        for name, data in payload.items():
            if name in ('native-preflight.mjs', 'input-freeze.json', 'capability/input-freeze.json'):
                continue
            target = OUTPUT / name
            rows[str(target)] = {'path': str(target), 'sha256': sha(data), 'bytes': len(data)}
        base = OUTPUT / 'capability' if cap else OUTPUT
        listed = [{**row, 'path': os.path.relpath(row['path'], base)} for row in rows.values()]
        return {'schemaVersion': 1, 'state': 'REVIEWED_CLASSIC342_REPLAY_CONSUMED_SOURCE_SEAL',
            'nativeSources': 342, 'inheritedRootRows': 1777, 'inheritedCapabilityRows': 1776,
            'parentSourceIndexSha256': PARENT_INDEX, 'runtimeIndexSha256': args.runtime_index_sha256,
            'reviewedPinsSha256': PINS_SHA, 'rootReviewReceiptSha256': REVIEW_SHA,
            'liveComputedInputs': root_document['liveComputedInputs'],
            'httpComponentPin': 'Null and sealed. Host activation/reseal is separate and must preserve original build paths/bytes.',
            'runtimeAcceptanceClaim': False, 'inputs': sorted(listed, key=lambda row: row['path'])}
    cap = manifest(cap_rows, True)
    payload['capability/input-freeze.json'] = (json.dumps(cap, indent=2) + '\n').encode()
    root_rows[str(OUTPUT / 'capability/input-freeze.json')] = {'path': str(OUTPUT / 'capability/input-freeze.json'),
        'sha256': sha(payload['capability/input-freeze.json']), 'bytes': len(payload['capability/input-freeze.json'])}
    root = manifest(root_rows, False)
    payload['input-freeze.json'] = (json.dumps(root, indent=2) + '\n').encode()
    compiled = payload['native-preflight.template.mjs'].decode()
    for key, value in {'AUTHORITY_SHA': sha(payload['activation-reference.json']), 'INPUTS_SHA': sha(payload['input-freeze.json']), 'RUNTIME_INDEX_SHA': args.runtime_index_sha256, 'RUNTIME_FAMILY': runtime.name}.items():
        compiled = compiled.replace('@' + key + '@', value)
    assert not re.search(r'@[A-Z_]+@', compiled), 'Unbound delegation wrapper placeholder'
    payload['native-preflight.mjs'] = compiled.encode()
    payload['README.md'] = ('Actual reviewed native authority is bound through the separately indexed classicPreflight runtime family.\n'
        'No regression/component/host is run by activation. Require raw exit0 plus completion seals and independent result closure.\n'
        '62 of64 inherited bodies are byte-identical; only exact registrar ancestry admission and Path Node oracle host orchestration are amended. Guest/facade/oracle semantics unchanged. HTTP pins stay null and sealed.\n'
        'Later minimal reviewed host activation must bind original actual build family/source/entry/audit paths and same bytes, without metadata projection or repackaging to relocate.\n').encode()
    receipt = {'schemaVersion': 1, 'state': 'ACTUAL_REVIEWED_CLASSIC_REPLAY_FAMILY_CREATED_NOT_EXECUTED',
        'preparedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'parentIndexSha256': PARENT_INDEX, 'independentSourceReviewIndexSha256': REVIEW_INDEX,
        'producerIndexSha256': args.producer_index_sha256, 'runtimeIndexSha256': args.runtime_index_sha256, 'runtimeRoot': str(runtime),
        'reviewedPinsSha256': PINS_SHA, 'rootReviewReceiptSha256': REVIEW_SHA,
        'inheritedBodies':len(records),'oldBodiesByteIdentical':62,'changedHostHarnessBodies':2,
        'registrarOracleAmendmentIndexSha256':AMENDMENT_INDEX,'guestSemanticBodiesChanged':False,
        'inheritedBodyHashes':{row['destinationPath']:row['afterSha256']for row in records},
        'publishedBodyHashes':{row['destinationPath']:expected_body_hash(row)for row in records},
        'nativeAdmission': 'Delegated exact indexed classicPreflight({variant}); no duplicate/projected backend',
        'inputFreezeSha256': sha(payload['input-freeze.json']), 'capabilityFreezeSha256': sha(payload['capability/input-freeze.json']),
        'consumedRootRows': len(root['inputs']), 'consumedCapabilityRows': len(cap['inputs']),
        'httpPinsStillNullAndSealed': True, 'runtimeAcceptanceClaim': False, 'guestOrHostExecuted': False}
    payload['source-receipt.json'] = (json.dumps(receipt, indent=2) + '\n').encode()
    index = {'schemaVersion': 1, 'state': 'ACTUAL_REVIEWED_CLASSIC_REPLAY_SOURCE_FAMILY_NOT_EXECUTED',
        'files': [{'path': name, 'sha256': sha(data), 'bytes': len(data)} for name, data in sorted(payload.items())],
        'runtimeAcceptanceClaim': False}
    payload['index.json'] = (json.dumps(index, indent=2) + '\n').encode()
    # Validate all external ordinary bytes BEFORE first output, then again before
    # publication. No source, authority or historical report is ever overwritten.
    def final_inputs():
        regular(runtime / 'index.json', args.runtime_index_sha256)
        for row in external.values():
            assert len(regular(row['path'], row['sha256'])) == row['bytes']
        for row in records:
            assert sha(payload[row['destinationPath']]) == expected_body_hash(row)
    final_inputs()
    stage.mkdir(exist_ok=False)
    for name, data in payload.items():
        path = stage / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(data)
        assert regular(path, sha(data)) == data
    final_inputs()
    assert not OUTPUT.exists() and not OUTPUT.is_symlink()
    stage.rename(OUTPUT)
    print(json.dumps({'output': str(OUTPUT), 'indexSha256': sha(payload['index.json']), 'inheritedBodiesByteIdentical': 62, 'changedHostHarnessBodies': 2,
        'httpHostAdmission': False, 'runtimeAcceptanceClaim': False}))


if __name__ == '__main__':
    main()
