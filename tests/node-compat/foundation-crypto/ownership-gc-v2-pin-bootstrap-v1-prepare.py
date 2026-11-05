"""Root checkpoint: derive new validation-only GC pins from reviewed actual DATA.

No engine, component, guest or key operation. Existing packets are never edited.
Run with python3 -B -I. Outputs are exclusive and cannot replace prior records.
"""
from pathlib import Path
import copy
import datetime
import hashlib
import importlib.util
import json
import sys

K = Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto')
TOOLING = K / 'ownership-gc-pin-tooling-candidate-v1'
NATIVE = K / 'ownership-gc-native-candidate-v2'


def descriptor(path):
    path = Path(path)
    assert path.is_absolute() and not path.is_symlink()
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def read(row):
    assert descriptor(row['path']) == row
    return json.loads(Path(row['path']).read_bytes())


def family(path, expected_sha):
    row = descriptor(path)
    assert row['sha256'] == expected_sha
    value = read(row)
    root = Path(path).parent
    names = set()
    for member in value['files']:
        name = member['path']
        assert name not in names and not name.startswith('/')
        assert all(part not in ('', '.', '..') for part in name.split('/'))
        names.add(name)
        assert descriptor(root / name) == dict(member, path=str(root / name))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'index.json'}
    assert not any(p.is_symlink() for p in root.rglob('*'))
    return row


def write(name, value):
    path = K / name
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')
    return descriptor(path)


def main():
    assert sys.dont_write_bytecode and __debug__
    native_ix = family(NATIVE / 'index.json', 'ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05')
    tooling_ix = family(TOOLING / 'index.json', '08ea93796d6e3402467b4296f5e4fd7173f5b649d14983d18038866ba19f9c56')
    export_ix = family(K / 'independent-ownership-gc-pin-export-results-review-v1/index.json', 'bda61549734352f06f7d90da3d2cc56d105ccb04c790d9b9d6c540beb6e73229')
    artifact_ix = family(K / 'independent-ownership-gc-native-artifact-results-review-v1/index.json', '64ec1c1e7629827f604c51b67f4024c8519a642e04512168b293c3c25f3b1737')
    exported_row = descriptor(Path(export_ix['path']).parent / 'results.json')
    exported = read(exported_row)
    assert exported['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_PIN_EXPORT_REVIEW_PASSED_V1'
    assert exported['verifiedPassed'] is True and exported['pinsAdopted'] is False
    assert exported['sourceIndexSha256'] == tooling_ix['sha256']
    assert exported['nativeSourceIndexSha256'] == native_ix['sha256']
    artifact = exported['independentNativeArtifactReview']
    assert artifact['index'] == artifact_ix
    artifact_result = read(artifact['result'])
    assert artifact_result['state'] == 'INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_ARTIFACT_REVIEW_PASSED_V1'
    assert artifact_result['verifiedPassed'] is True
    actual_export = dict(index=export_ix, result=exported_row)
    candidate = read(exported['candidate'])
    assert candidate['state'] == 'UNREVIEWED_CRYPTO_OWNER355_ISOLATED_GC_PIN_CANDIDATE_V1'
    assert all(candidate['variants'][n] is None for n in ('normal-off', 'normal-runtime', 'disabled-off'))
    before = candidate['variants']['gc-off']
    assert before['reviewRequired'] is True
    pin = copy.deepcopy(before)
    pin.update(state='reviewed-crypto-owner355-native-build-for-validation', reviewRequired=False,
               independentProofIndexPath=artifact['index']['path'], independentProofIndexSha256=artifact['index']['sha256'],
               independentProofResultPath=artifact['result']['path'], independentProofResultSha256=artifact['result']['sha256'])
    assert {k: v for k, v in pin.items() if k in before and k not in ('state', 'reviewRequired')} == {k: v for k, v in before.items() if k not in ('state', 'reviewRequired')}
    assert len(pin['frozenFiles']) == 1462
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    pins = dict(schemaVersion=1, state='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_BOOTSTRAP_V1',
                sourceIndexSha256=native_ix['sha256'], variants={n: pin if n == 'gc-off' else None for n in candidate['variants']},
                actualUnreviewedCandidate=exported['candidate'], independentExportReview=actual_export,
                independentNativeArtifactReview=artifact, issuedAtUtc=now,
                adoptionScope='GC-only validation and read-only bootstrap; no production adoption or runtime acceptance',
                operationalAdmission=False, runtimeAcceptanceClaim=False)
    pins_row = write('reviewed-ownership-gc-v2-native-pins-v1.json', pins)
    export_native = read(descriptor(K / 'ownership-gc-v2-pin-export-v1-native-root-authority.json'))
    review = dict(schemaVersion=1, state='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PINS_V1',
                  sourceIndexSha256=native_ix['sha256'], reviewedPinsSha256=pins_row['sha256'],
                  **{k: export_native[k] for k in ('configuredSourceRoot', 'artifactToolsRoot', 'workRoot', 'freezeRoot')},
                  sourceFiles=355, externalSources=3, operationalAdmission=False, runtimeAcceptanceClaim=False,
                  gcOff={k: pin[k] for k in ('engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256', 'independentProofIndexSha256', 'independentProofResultSha256')},
                  actualUnreviewedCandidate=exported['candidate'], independentExportReview=actual_export,
                  independentNativeArtifactReview=artifact, issuedAtUtc=now,
                  scope='New GC-only validation pins after independent actual export/artifact reviews; unchanged normal and consumer pins')
    review_row = write('reviewed-ownership-gc-v2-native-pin-root-review-v1.json', review)
    # Genuine existing pure selector after authenticating every native member.
    sys.path.insert(0, str(NATIVE))
    spec = importlib.util.spec_from_file_location('actual_gc_pin_model', NATIVE / 'pin_model.py')
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    assert model.select(pins, review, pins_row['sha256'], native_ix['sha256']) == pin
    native = copy.deepcopy(export_native)
    native.update(phase='bootstrap', exportAllowed=False, bootstrapAllowed=True,
                  reviewedGcPins=pins_row, gcNativeRootReview=review_row, pinCandidateOutput=None,
                  issuedAtUtc=now, scope='Read-only actual GC bootstrap using new validation-only pins and corrected tooling; no engine/component/guest/key/GC workload')
    native_row = write('ownership-gc-v2-bootstrap-v1-native-root-authority.json', native)
    tooling = read(descriptor(K / 'ownership-gc-v2-pin-export-v1-tooling-root-authority.json'))
    tooling.update(phase='bootstrap', nativeRootAuthority=native_row, reviewedGcPins=pins_row,
                   gcNativeRootReview=review_row, exportAllowed=False, bootstrapAllowed=True,
                   pinCandidateOutput=None, actualExportReview=actual_export, issuedAtUtc=now,
                   externalOutputRoot='/private/tmp/starling-node-compat/crypto-owner355-gc-pin-tooling-v1-bootstrap-external-root')
    tooling_row = write('ownership-gc-v2-bootstrap-v1-tooling-root-authority.json', tooling)
    config = dict(schemaVersion=1, sourceIndex=native_ix, rootAuthority=native_row,
                  toolingIndex=tooling_ix, toolingRootAuthority=tooling_row)
    config_row = write('ownership-gc-v2-bootstrap-v1-root-config.json', config)
    assert read(exported['candidate']) == candidate
    print(json.dumps(dict(reviewedGcPins=pins_row, gcNativeRootReview=review_row,
                          nativeRootAuthority=native_row, toolingRootAuthority=tooling_row,
                          config=config_row, genuinePureSelectorPassed=True, engineExecuted=False)))


if __name__ == '__main__':
    main()
