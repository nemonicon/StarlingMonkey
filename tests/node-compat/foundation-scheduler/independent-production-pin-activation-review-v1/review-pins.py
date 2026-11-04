"""Read-only comparison of reviewed pins with original export and real freezes."""
from pathlib import Path
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[3]
REVIEW = BASE/'production-pin-review-v1'
verified = {}


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def checked(path,digest=None,size=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(),path
    value = sha(path)
    assert digest is None or value == digest,path
    assert size is None or path.stat().st_size == size,path
    verified[str(path)] = dict(path=str(path),sha256=value,bytes=path.stat().st_size)
    return value


candidate_path = BASE/'production-execution-v1/all-unreviewed-pin-candidates.json'
checked(candidate_path,'56ae9a369443b63f5b95902171be56e78512c053a3d6e8ba922795fc107c2fe3')
candidate = read(candidate_path)
assert candidate['state'] == 'UNREVIEWED_PRODUCTION_PIN_CANDIDATES_V1'
assert candidate['requiresIndependentReviewAndNewAdmissionRevision'] is True
index_sha = checked(REVIEW/'index.json')
assert index_sha.startswith('656a88') and index_sha.endswith('3934')
for row in read(REVIEW/'index.json')['files']:
    checked(REVIEW/row['path'],row['sha256'],row['bytes'])
checked(REVIEW/'results.json','2388c49cefde6ae424712d2842423426220fb6cd03b147d0b46476cc43e6bb3e')
root_result = read(REVIEW/'results.json')
common_sha = checked(REVIEW/'common-pins.json','ed0d6f548ac354ce6ef0ab97c5162ece7091a4e22c81fdd3910665c0bbb21bea')
cap_sha = checked(REVIEW/'capability-pins.json','26b16ba1404c76d04a3ae1a137d37d88a08cc87de4907d14eb3bc028759104f1')
common,cap = read(REVIEW/'common-pins.json'),read(REVIEW/'capability-pins.json')
assert common['schemaVersion'] == cap['schemaVersion'] == 1
assert common['state'] == 'REVIEWED_REAL_PRODUCTION_FREEZES_V1'
assert cap['state'] == 'REVIEWED_REAL_PRODUCTION_CAPABILITY_FREEZES_V1'
assert set(common['variants']) == {'normal-off','gc-off'}
assert set(cap['variants']) == {'normal-off','normal-runtime','gc-off'}
proofs = {
    'normal-off':('production-normal-off-verification-v1','97a5b3683c74c3465666225fc5e440660e18e25b79bd786c5c9c05ecc324bbd0','6e5bc2ca3b3e3f7dccaa887003bc292e8a7abfbc5260691d1cda0114640dae84','86b5d78c81e97b33389302fe296e589863850bcc3aa60ce7f4ac5e52a2d33d7a'),
    'normal-runtime':('production-normal-runtime-verification-v1','9999f6ff4a9b2fcbf361b142ad28da4d53316336b9e20b150fe05ecb641ebe76','479821f8eefbc6aacbfe9df8538c5ee0a8745e530a474ecee8cb34251c0a1943','83be6fe14eaaceb96a446bb5423e9bfcaaa214dde0ac6b5bbe9e4a2d693625d8'),
    'gc-off':('production-gc-off-verification-v1','e47e5a7252835f9467dfa05248a83026b70c8aa255b1fa3eebef5a2b002c5814','502320aaed8c78ace92d8d8d782a355307868beee707b22e03c96f67cd42c833','8629f1cdd12178a12bfe5d07e49c3169c62f2b6f8693b1322f4e6a46bf63215f'),
}
variant_reports = []
for label,(proof_name,proof_sha,engine_sha,freeze_sha) in proofs.items():
    before = candidate['variants'][label]
    after = cap['variants'][label]
    assert before['state'] == 'unreviewed-production-freeze-pin-candidate' and before['reviewRequired'] is True
    expected = {key:value for key,value in before.items() if key not in ['state','reviewRequired']}
    expected.update(state='reviewed-real-production-freeze',artifactReviewCompleted=True,
                    independentReviewIndexPath='tests/node-compat/foundation-scheduler/'+proof_name+'/index.json',independentReviewIndexSha256=proof_sha)
    assert after == expected,label
    if label in common['variants']:
        assert common['variants'][label] == after
    assert after['engineSha256'] == engine_sha and after['freezeReceiptSha256'] == freeze_sha
    assert after['runtimeAcceptanceClaim'] is False
    checked(REPO/after['independentReviewIndexPath'],proof_sha)
    proof = BASE/proof_name
    for row in read(proof/'index.json')['files']:
        checked(proof/row['path'],row['sha256'],row['bytes'])
    assert read(proof/'results.json')['engineSha256'] == engine_sha
    checked(after['freezeReceiptPath'],freeze_sha)
    freeze = read(Path(after['freezeReceiptPath']))
    assert freeze['label'] == label and freeze['engineSha256'] == engine_sha
    assert freeze['schema'] == 1 and freeze['state'] == 'immutable-release-engine-frozen'
    expected_copies = [{key:row[key] for key in ['path','sha256','bytes']} for row in freeze['copies']]
    assert len(expected_copies) == 335 and after['frozenFiles'] == expected_copies
    for row in expected_copies:
        checked(row['path'],row['sha256'],row['bytes'])
    assert after['enginePath'] == freeze['engine']
    assert after['coreSources'] == freeze['coreSources']
    assert after['receiptSha256'] == freeze['receiptSha256']
    assert after['sourceRoot'] == freeze['sourceRoot'] and after['componentizeSourceRoot'] == freeze['componentizeSourceRoot']
    assert after['recipeSha256'] == freeze['recipeSha256']
    assert after['entropyPolicy'] == freeze['entropyPolicy'] and after['gcStress'] == freeze['gcStress']
    recorded = next(row for row in root_result['variants'] if row['label'] == label)
    assert recorded['independentReviewIndexSha256'] == proof_sha and recorded['frozenCopiesRehashed'] == 335
    assert recorded['engineSha256'] == engine_sha and recorded['freezeReceiptSha256'] == freeze_sha
    variant_reports.append(dict(label=label,engineSha256=engine_sha,freezeReceiptSha256=freeze_sha,independentProofIndexSha256=proof_sha,frozenFilesRehashed=335))
for row in list(verified.values()):
    checked(row['path'],row['sha256'],row['bytes'])
result = dict(schemaVersion=1,state='INDEPENDENT_REVIEWED_PIN_DATA_TRACE_TO_ACTUAL_FREEZES_PASSED',reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    rootReviewIndexSha256=index_sha,originalUnreviewedCandidateSha256=sha(candidate_path),commonPinSha256=common_sha,capabilityPinSha256=cap_sha,
    originalCandidatePreservedUnreviewed=True,onlyVariantChanges=['state to reviewed-real-production-freeze','reviewRequired removed','artifactReviewCompleted true','exact independent proof index path/hash added'],
    variants=variant_reports,commonSubsetExactlyOffAndGc=True,reviewedPinsDeclareNoRuntimeAcceptance=True,verifiedFiles=list(verified.values()),
    activationCodeReviewSeparate=True,guestNativeRepackOrNinjaExecuted=False,existingDataModified=False)
with (HERE/'pin-data-results.json').open('x') as stream:
    json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps(dict(state=result['state'],resultSha256=sha(HERE/'pin-data-results.json'),rootReviewIndexSha256=index_sha,readPaths=len(verified))))
