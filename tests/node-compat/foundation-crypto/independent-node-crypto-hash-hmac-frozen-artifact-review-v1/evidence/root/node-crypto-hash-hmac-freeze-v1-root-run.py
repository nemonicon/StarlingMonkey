"""Root-issued revalidated artifact freeze; no engine, guest or crypto execution."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
BASE = REPO / 'tests/node-compat/foundation-crypto'
SOURCE = BASE / 'node-crypto-hash-hmac-freezer-candidate-v1'
PEER = BASE / 'independent-node-crypto-hash-hmac-freezer-source-review-v1'
PREFIX = BASE / 'node-crypto-hash-hmac-freeze-v1-root'


def descriptor(path):
    path = Path(path)
    assert path.is_absolute()
    for part in (path, *path.parents):
        assert not part.is_symlink(), str(part)
    before = path.stat()
    assert path.is_file()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    after = path.stat()
    assert before == after
    return dict(path=str(path), sha256=digest, bytes=after.st_size)


def read(path):
    return json.loads(Path(path).read_bytes())


def family(path, expected):
    index = descriptor(path / 'index.json')
    assert index['sha256'] == expected
    names = {'index.json'}
    for item in read(path / 'index.json')['files']:
        name = item['path']
        assert name and not Path(name).is_absolute()
        assert all(p not in ('', '.', '..') for p in name.split('/'))
        assert name not in names
        names.add(name)
        assert descriptor(path / name) == dict(item, path=str(path / name))
    assert not any(p.is_symlink() for p in path.rglob('*'))
    assert names == {p.relative_to(path).as_posix() for p in path.rglob('*') if p.is_file()}
    return index


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


# Reader functions copied from Root stage launcher SHA256 0d779ac0beded3d3ece94693f1933c3cca04ea4ed1fa5c504013e9cb0f32a581; original unchanged.
assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1
assert len(sys.argv) == 2 and len(sys.argv[1]) == 64
own = family(SOURCE, '45eef4b6de1e24e450737b66cfc7216e81e39192f8be11be7e80f4312f7c9355')
peer = family(PEER, sys.argv[1])
refs = read(SOURCE / 'references.json')
assert descriptor(refs['entry']['path']) == refs['entry']
entry = load(refs['entry']['path'], 'reviewed_hash357_freeze_entry_no_bootstrap_call')
peer_proof = dict(index=peer, result=descriptor(PEER / 'results.json'))
peer_contract = descriptor(PEER / 'result-contract.json')
peer_value, _, _ = entry.whole_proof(peer_proof, peer_contract)
assert peer_value['state'] == 'INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_FREEZER_SOURCE_REVIEW_PASSED_V1'
assert peer_value['freezerSourceIndexSha256'] == own['sha256']
assert peer_value['artifactReviewIndexSha256'] == refs['artifactReview']['index']['sha256']
assert peer_value['producerSourceIndexSha256'] == refs['producerIndex']['sha256']
assert peer_value['sourceOnly'] is peer_value['sourceReviewPassed'] is True
for key in ('ownerActionsInvoked', 'hostActionsInvoked', 'nativeFreezeOrAdmissionActionsInvoked', 'engineOrGuestOrCryptoActionsInvoked'):
    assert peer_value[key] is False
artifact, _, _ = entry.whole_proof(refs['artifactReview'], refs['artifactContract'])
entry.artifact_model(artifact, refs)
authority = read(SOURCE / 'root-authority.template.json')
authority.update(freezerIndex=own, sourceReview=peer_proof, sourceReviewContract=peer_contract,
                 freezeAllowed=True, readOnlyProducerAdmissionAllowed=True,
                 frozenOnlyVerificationAllowed=True, ownedCopiesAllowed=True)
entry.root_model(authority, own, refs)
for key in ('freezeRoot', 'externalRoot'):
    path = Path(refs[key])
    assert not path.exists() and not path.is_symlink()
assert descriptor(sys.executable) == refs['python']
authority_path = Path(str(PREFIX) + '-authority.json')
config_path = Path(str(PREFIX) + '-config.json')
invocation_path = Path(str(PREFIX) + '-invocation.json')
observation_path = Path(str(PREFIX) + '-results.json')
external = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-freeze-v1-root-monitor')
for path in (authority_path, config_path, invocation_path, observation_path, external):
    assert not path.exists() and not path.is_symlink()
write(authority_path, authority)
config = read(SOURCE / 'config.template.json')
config.update(freezerIndex=own, rootAuthority=descriptor(authority_path))
write(config_path, config)
argv = [refs['python']['path'], '-B', '-I', refs['entry']['path'],
        'parent', json.dumps(descriptor(config_path), separators=(',', ':'))]
assert family(Path(refs['monitorIndex']['path']).parent,
              refs['monitorIndex']['sha256']) == refs['monitorIndex']
assert descriptor(refs['monitorEntry']['path']) == refs['monitorEntry']
write(invocation_path, dict(schemaVersion=1, state='ROOT_ISSUED_HASH_HMAC357_REVALIDATED_FREEZE_V1',
      sourceIndex=own, sourceReview=peer_proof, sourceReviewContract=peer_contract,
      artifactReview=refs['artifactReview'], artifactContract=refs['artifactContract'],
      rootAuthority=descriptor(authority_path), rootConfig=descriptor(config_path),
      launcher=descriptor(Path(__file__).resolve()), actualArgv=argv,
      outerDeadlineSeconds=1800, innerDeadlineSeconds=1800,
      originalRecipeExitCode=0, originalParentExitCodes=[1,1],
      originalBuildPreservationPassed=False, originalBuildAccepted=False,
      nativeBuildAllowed=False, engineExecutionAllowed=False, guestAllowed=False,
      cryptoOperationsAllowed=False, liveEvpSnapshotAdmission=False,
      operationalAdmission=False))
external.mkdir(mode=0o700)
monitor = load(refs['monitorEntry']['path'], 'original0af_hash357_freeze_root_monitor')
print(json.dumps(dict(event='hash357-freeze-start', invocation=descriptor(invocation_path))), flush=True)
terminal = monitor.monitor(argv, str(REPO), dict(os.environ), external, 1800,
                           descriptor(authority_path))
clean = (terminal['rawExitCode'] == 0 and
         terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and
         terminal['timeout'] is terminal['forcedCleanup'] is False and
         all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
receipt_path = Path(refs['freezeRoot']) / 'normal-off-freeze-receipt.json'
receipt = read(receipt_path) if receipt_path.is_file() else None
if clean:
    assert receipt['state'] == 'HASH_HMAC357_NORMAL_OFF_REVALIDATED_FREEZE_COMPLETE_UNREVIEWED_V1'
    assert receipt['freezerSourceIndex'] == own and receipt['rootAuthority'] == descriptor(authority_path)
    assert receipt['freshProducerAdmissionCalls'] == 1 and receipt['originalNinjaCommandReexecuted'] is False
    assert receipt['rawMetadataFields'] == 83 and receipt['nativeSourceFiles'] == 357
    assert receipt['originalParentExitCodes'] == [1,1] and receipt['originalBuildAccepted'] is False
    assert descriptor(receipt['engine']['path']) == receipt['engine']
    assert descriptor(receipt['metadata']['path']) == receipt['metadata']
assert family(SOURCE, own['sha256']) == own
assert family(PEER, peer['sha256']) == peer
write(observation_path, dict(schemaVersion=1,
      state='ROOT_OBSERVED_HASH_HMAC357_FREEZE_COMPLETE_UNREVIEWED_V1' if clean else
            'ROOT_OBSERVED_HASH_HMAC357_FREEZE_FAILED_UNACCEPTED_V1',
      invocation=descriptor(invocation_path), sourceIndex=own, sourceReview=peer_proof,
      artifactReview=refs['artifactReview'], rootAuthority=descriptor(authority_path),
      rootConfig=descriptor(config_path), ownedTerminal=descriptor(external / 'terminal.json'),
      rawParentExitCode=terminal['rawExitCode'],
      allOwnedGroupsGone=terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True,
      freezeProcessSucceeded=clean,
      actualFreezeReceipt=descriptor(receipt_path) if receipt is not None else None,
      engine=receipt.get('engine') if receipt else None,
      metadata=receipt.get('metadata') if receipt else None,
      originalRecipeExitCode=0, originalParentExitCodes=[1,1],
      originalBuildPreservationPassed=False, originalBuildAccepted=False,
      independentActualFreezeReviewRequired=True, engineExecuted=False, guestExecuted=False,
      cryptoOperationsInvoked=False, liveEvpSnapshotAdmission=False,
      operationalAdmission=False, runtimeAcceptanceClaim=False))
print(json.dumps(dict(event='hash357-freeze-terminal', rawExitCode=terminal['rawExitCode'],
                      clean=clean, observation=descriptor(observation_path))), flush=True)
raise SystemExit(0 if clean else 1)
