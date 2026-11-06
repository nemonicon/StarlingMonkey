# Genuine Root v2 successor to immutable v1 launcher b9936b431a1c71e926ea6b9a6dfb6bcf1fef0e8d3ea5d3dddb1ab3e52df310ea. Prior precompiler failure unchanged.
"""Root-issued two-CPP syntax check only. No object, link, engine or guest execution."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
BASE = REPO / 'tests/node-compat/foundation-crypto'
SOURCE = BASE / 'node-crypto-hash-hmac-init-barrier-sdk-syntax-v2'
PEER = BASE / 'independent-node-crypto-hash-hmac-init-barrier-source-review-v1'
PREFIX = BASE / 'node-crypto-hash-hmac-init-barrier-sdk-v2-root'


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


# Reader helpers copied from Root stage launcher SHA256 0d779ac0beded3d3ece94693f1933c3cca04ea4ed1fa5c504013e9cb0f32a581; original unchanged.
assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1
own = family(SOURCE, '9f0690d3ecd5c96256637718dfe3d1aec4650cab036036a71e680d5223762e9e')
peer = family(PEER, '7c8f9ab8cbf463a0e3a835caa25829d57d3e182d007df084369b0d9cfc00823f')
barrier = family(BASE / 'node-crypto-hash-hmac-init-barrier-candidate-v1',
                 'b8a4f219df0b5172361045632d1a1a96f068609496ac8ea128e38eb2aedd6b6c')
plan = read(SOURCE / 'plan.json')
refs = plan['references']
audit_path = BASE / 'independent-node-crypto-hash-hmac-init-barrier-sdk-v2-preflight-audit.json'
audit_row = descriptor(audit_path)
assert audit_row['sha256'] == '3aa36f2b4b2d30edc7e527afc4e7d0e18853b54f606c197cc02f45c54ddbba03'
audit = read(audit_path)
assert audit['state'] == 'BOUNDED_INIT_BARRIER_DORMANT_SDK_V2_PREFLIGHT_PASSED_V1'
assert audit['driverPreparationIndex'] == own and audit['sourceIndex'] == barrier
assert audit['reviewedSourcePair'] == dict(index=peer, results=descriptor(PEER / 'results.json'))
assert audit['driver'] == descriptor(SOURCE / 'run-sdk-syntax.py') and audit['plan'] == descriptor(SOURCE / 'plan.json')
assert audit['sourceActionsInvoked'] is audit['compilerMonitorHelperFixtureEngineCryptoInvoked'] is False
assert refs['sourceIndex'] == barrier and descriptor(sys.executable) == refs['python']
source_contract = read(BASE / 'node-crypto-hash-hmac-init-barrier-candidate-v1/future-source-review-contract.json')
peer_value = read(PEER / 'results.json')
assert peer_value['state'] == source_contract['requiredReviewState'] and peer_value['sourceIndexSha256'] == barrier['sha256']
for key, value in source_contract['requiredFixedValues'].items():
    assert peer_value[key] == value
output = Path(plan['outputRoot'])
assert not output.exists() and not output.is_symlink()
authority = read(SOURCE / 'root-authority-template.json')
authority.update(driverPreparationIndex=own,
                 sourceReview=dict(index=peer, results=descriptor(PEER / 'results.json')),
                 syntaxOnlyCompilerAllowed=True)
assert authority['sourceIndex'] == barrier and authority['units'] == ['entropy-policy', 'hash-hmac-kernel']
for key in ('objectOrLinkAllowed', 'nativeBuildAllowed', 'helperAllowed', 'engineAllowed',
            'cryptoAllowed', 'guestAllowed', 'snapshotAllowed', 'adoptionAllowed'):
    assert authority[key] is False
assert family(Path(refs['monitorIndex']['path']).parent,
              refs['monitorIndex']['sha256']) == refs['monitorIndex']
monitor_path = Path(refs['monitorIndex']['path']).parent / 'monitor.py'
assert descriptor(monitor_path)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
authority_path = Path(str(PREFIX) + '-authority.json')
invocation_path = Path(str(PREFIX) + '-invocation.json')
observation_path = Path(str(PREFIX) + '-results.json')
external = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-init-barrier-sdk-syntax-v2-root-monitor')
for path in (authority_path, invocation_path, observation_path, external):
    assert not path.exists() and not path.is_symlink()
write(authority_path, authority)
argv = [refs['python']['path'], '-B', '-I', str(SOURCE / 'run-sdk-syntax.py'),
        '--execute-root-authorized-two-frontends', json.dumps(descriptor(authority_path), separators=(',', ':'))]
write(invocation_path, dict(schemaVersion=1, state='ROOT_ISSUED_INIT_BARRIER_TWO_CPP_SYNTAX_V2',
      driverPreparationIndex=own, sourceIndex=barrier, sourceReviewIndex=peer,
      boundaryAudit=audit_row, rootAuthority=descriptor(authority_path),
      launcher=descriptor(Path(__file__).resolve()), actualArgv=argv,
      outerDeadlineSeconds=300, timeoutSecondsPerUnit=60, compilerCommands=2,
      objectOrLinkAllowed=False, engineAllowed=False, guestAllowed=False,
      cryptoAllowed=False, snapshotAllowed=False, adoptionAllowed=False))
external.mkdir(mode=0o700)
monitor = load(monitor_path, 'original0af_init_barrier_sdk_root_monitor')
print(json.dumps(dict(event='init-barrier-sdk-start', invocation=descriptor(invocation_path))), flush=True)
terminal = monitor.monitor(argv, str(REPO), dict(os.environ), external, 300, descriptor(authority_path))
clean = (terminal['rawExitCode'] == 0 and
         terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and
         terminal['timeout'] is terminal['forcedCleanup'] is False and
         all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
result_path = output / 'result.json'
actual = read(result_path) if result_path.is_file() else None
if clean:
    assert actual['state'] == 'INIT_BARRIER_TWO_CPP_FRONTEND_SYNTAX_PASSED_V2'
    assert actual['sourceIndex'] == barrier and actual['rootAuthority'] == descriptor(authority_path)
    assert actual['currentInputProtection']['unchanged'] is actual['allPlannedCompilerStartsProved'] is True
    assert len(actual['units']) == 2 and all(r['rawExitCode'] == 0 and r['ownedGroupsClean'] and r['actualStartedRecordPresent'] and not r['dependencyError'] and not r['commandError'] for r in actual['units'])
assert family(SOURCE, own['sha256']) == own and family(PEER, peer['sha256']) == peer
write(observation_path, dict(schemaVersion=1,
      state='ROOT_OBSERVED_INIT_BARRIER_TWO_CPP_SYNTAX_COMPLETE_UNREVIEWED_V2' if clean else
            'ROOT_OBSERVED_INIT_BARRIER_TWO_CPP_SYNTAX_FAILED_UNACCEPTED_V2',
      invocation=descriptor(invocation_path), driverPreparationIndex=own,
      sourceIndex=barrier, boundaryAudit=audit_row, rootAuthority=descriptor(authority_path),
      ownedTerminal=descriptor(external / 'terminal.json'), rawDriverExitCode=terminal['rawExitCode'],
      allOwnedGroupsGone=terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True,
      actualResult=descriptor(result_path) if actual is not None else None,
      actualOutputIndex=descriptor(output / 'index.json') if (output / 'index.json').is_file() else None,
      syntaxProcessSucceeded=clean, independentActualResultReviewRequired=True,
      objectOrLinkInvoked=False, nativeBuildInvoked=False, engineInvoked=False,
      guestInvoked=False, cryptoInvoked=False, snapshotInvoked=False,
      phaseBarrierRuntimeBehaviorProved=False, operationalAdmission=False))
print(json.dumps(dict(event='init-barrier-sdk-terminal', rawExitCode=terminal['rawExitCode'],
                      clean=clean, observation=descriptor(observation_path))), flush=True)
raise SystemExit(0 if clean else 1)
