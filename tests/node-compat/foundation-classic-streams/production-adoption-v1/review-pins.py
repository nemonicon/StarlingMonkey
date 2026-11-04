"""Root pin review; requires four completed independent actual-artifact proofs."""
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
EXPORT = Path('/tmp/starling-node-compat/classic-production-unreviewed-pins-v1.json')
LABELS = ['normal-off', 'normal-runtime', 'gc-off', 'disabled-off']
RECIPE = '71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
PROOFS = {'normal-off': ('independent-native-verification-v2', 'normal-off-v1'),
          'normal-runtime': ('independent-native-verification-v3', 'normal-runtime-v1'),
          'gc-off': ('independent-native-verification-v4', 'gc-off-v1'),
          'disabled-off': ('independent-native-verification-v5', 'disabled-off-v1')}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(row, root=None):
    path = (root/row['path']) if root else Path(row['path'])
    assert path.is_file() and not path.is_symlink(), path
    assert digest(path) == row['sha256'], path
    assert path.stat().st_size == row['bytes'], path

def main():
    exported = json.loads(EXPORT.read_bytes())
    assert exported['schemaVersion'] == 1 and exported['state'] == 'UNREVIEWED_CLASSIC_PRODUCTION_PIN_CANDIDATES_V1'
    assert list(exported['variants']) == LABELS
    anchors = json.loads((HERE/'native-input-anchors-v4.json').read_bytes())
    assert anchors['state'] == 'REVIEWED_ACTUAL_CLASSIC_FREEZE_INPUTS_V1'
    reviewed = copy.deepcopy(exported['variants'])
    proofs = {}
    for label in LABELS:
        pin = reviewed[label]
        assert pin['state'] == 'unreviewed-classic-production-freeze-pin-candidate'
        assert pin['variant'] == label and pin['sourceFiles'] == 342 and pin['recipeSha256'] == RECIPE
        proof_dir, result_dir = PROOFS[label]
        root = BASE/proof_dir
        index = json.loads((root/'index.json').read_bytes())
        for row in index['files']:
            check(row, root)
        result_path = root/result_dir/'results.json'
        result = json.loads(result_path.read_bytes())
        assert result['state'] == 'INDEPENDENT_CLASSIC_NATIVE_FREEZE_VERIFIED_NO_GUEST'
        assert result['label'] == label and result['anchors'] == anchors['variants'][label]
        for row in result['verifiedFiles']:
            check(row)
        assert result['frozenCopies'] == 405 and len(pin['frozenFiles']) == 405
        anchor = result['anchors']
        for key in ['engineSha256', 'engineBytes', 'freezeReceiptSha256']:
            assert pin[key] == anchor[key]
        assert pin['receiptSha256'] == anchor['metadataSha256']
        for row in pin['frozenFiles']:
            check(row)
        pin['state'] = 'reviewed-real-classic-production-freeze'
        pin['reviewRequired'] = False
        pin['runtimeAcceptanceClaim'] = False
        proofs[label] = {
            'engineSha256': pin['engineSha256'], 'engineBytes': pin['engineBytes'],
            'receiptSha256': pin['receiptSha256'], 'freezeReceiptSha256': pin['freezeReceiptSha256'],
            'independentProofIndexSha256': digest(root/'index.json'),
            'independentProofResultSha256': digest(result_path),
            'independentProofIndexPath': str(root/'index.json'),
            'independentProofResultPath': str(result_path),
            'consumedPathsRootRehashed': len(result['verifiedFiles']),
        }
    pins = {'schemaVersion': 1, 'state': 'REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1',
            'variants': reviewed, 'sourceUnreviewedExportSha256': digest(EXPORT),
            'sourceCandidateIndexSha256': digest(BASE/'integration-candidate-v1/index.json'),
            'runtimeAcceptanceClaim': False,
            'scope': 'Reviewed real native artifacts only; new source activation and actual component gates remain required.'}
    pins_path = HERE/'reviewed-runtime-pins-v1.json'
    assert not pins_path.exists() and not (HERE/'root-pin-review-receipt.json').exists()
    with pins_path.open('x') as stream:
        json.dump(pins, stream, indent=2)
        stream.write('\n')
    receipt = {'schemaVersion': 1, 'state': 'ROOT_REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1',
               'reviewedAtUtc': datetime.now(timezone.utc).isoformat(),
               'reviewedPinsSha256': digest(pins_path), 'sourceFiles': 342,
               'recipeSha256': RECIPE, 'labels': LABELS, 'variants': proofs,
               'immutablePredecessorPinsUnchanged': True,
               'runtimeAcceptanceClaim': False, 'guestPerformedByReview': False,
               'requiresSeparateSourceActivationAndComponentGates': True}
    receipt_path = HERE/'root-pin-review-receipt.json'
    with receipt_path.open('x') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'state': receipt['state'], 'reviewedPinsPath': str(pins_path),
                      'reviewedPinsSha256': digest(pins_path),
                      'rootReviewReceiptPath': str(receipt_path),
                      'rootReviewReceiptSha256': digest(receipt_path), 'guestPerformed': False}))

if __name__ == '__main__':
    main()
