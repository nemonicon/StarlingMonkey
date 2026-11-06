"""Root-owned read-only artifact check. No engine, compiler or crypto execution."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
BASE = REPO / 'tests/node-compat/foundation-crypto'
SOURCE = BASE / 'node-crypto-hash-hmac-artifact-revalidation-candidate-v2'
PEER = BASE / 'independent-node-crypto-hash-hmac-artifact-revalidation-v2-source-review-v1'
PREFIX = BASE / 'node-crypto-hash-hmac-artifact-revalidation-v2-root'
PYTHON = Path('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9')


def row(path):
    path = Path(path)
    for parent in (path, *path.parents):
        assert not parent.is_symlink(), str(parent)
    before = path.stat()
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4194304), b''):
            h.update(block)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_mode, before.st_size,
            before.st_mtime_ns, before.st_ctime_ns) == (
                after.st_dev, after.st_ino, after.st_mode, after.st_size,
                after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=after.st_size)


def read(path):
    return json.loads(Path(path).read_bytes())


def family(path, expected):
    index = row(path / 'index.json')
    assert index['sha256'] == expected
    names = {'index.json'}
    for item in read(path / 'index.json')['files']:
        name = item['path']
        assert name not in names and not Path(name).is_absolute()
        assert all(part not in ('', '.', '..') for part in name.split('/'))
        names.add(name)
        assert row(path / name) == dict(item, path=str(path / name))
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


assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1
own = family(SOURCE, '559d600d9bedec4e319a415bcd30b984f445cfed7df2322dee25a86cba253172')
peer_index = family(PEER, '31d9b3f855be3dad706b1bcdde51cedf3f092e94b6c121a78657012375579775')
refs = read(SOURCE / 'references.json')
peer_result = read(PEER / 'results.json')
peer_contract = read(PEER / 'result-contract.json')
assert peer_result['state'] == peer_contract['requiredReviewState']
for key, value in peer_contract['requiredFixedValues'].items():
    assert peer_result[key] == value
for key, value in peer_contract['requiredExactDescriptors'].items():
    assert peer_result[key] == value
models = load(SOURCE / 'models.py', 'reviewed_artifact_read_only_pure_models')
models.peer(peer_result, own, refs)
python = row(PYTHON)
assert python['sha256'] == '4a81cbef89c3cded9c9435c2faf747823dfed9ca9a0da82df374834a18c70dc8'
monitor_index = family(Path(refs['monitorIndex']['path']).parent,
                       '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
assert monitor_index == refs['monitorIndex']
assert row(refs['monitorEntry']['path']) == refs['monitorEntry']
assert row(refs['entry']['path']) == refs['entry']
for key in ('outputRoot', 'externalOutputRoot', 'freezeRoot'):
    assert not Path(refs[key]).exists() and not Path(refs[key]).is_symlink()

authority = read(SOURCE / 'root-authority.template.json')
authority.update(state=models.STATE, adapterIndex=own,
                 sourceReview=dict(index=peer_index, result=row(PEER / 'results.json')),
                 readOnlySourceAdmissionAllowed=True, ownedEvidencePublicationAllowed=True)
models.root(authority, own, refs)
authority_path = Path(str(PREFIX) + '-authority.json')
config_path = Path(str(PREFIX) + '-config.json')
invocation_path = Path(str(PREFIX) + '-invocation.json')
observation_path = Path(str(PREFIX) + '-results.json')
assert all(not p.exists() for p in (authority_path, config_path, invocation_path, observation_path))
write(authority_path, authority)
config = read(SOURCE / 'config.template.json')
config.update(state='HASH_HMAC357_READ_ONLY_REVALIDATION_CONFIG_V2',
              adapterIndex=own, rootAuthority=row(authority_path))
write(config_path, config)
argv = [str(PYTHON), '-B', '-I', refs['entry']['path'],
        json.dumps(row(config_path), separators=(',', ':'))]
write(invocation_path, dict(schemaVersion=1, state='ROOT_ISSUED_READ_ONLY_REVALIDATION_V2',
      rootAuthority=row(authority_path), rootConfig=row(config_path), sourceIndex=own,
      sourceReviewIndex=peer_index, launcher=row(Path(__file__).resolve()), python=python,
      monitorEntry=refs['monitorEntry'], monitorIndex=monitor_index, actualArgv=argv,
      deadlineSeconds=600, outputRoot=refs['outputRoot'],
      externalOutputRoot=refs['externalOutputRoot'], engineExecutionAllowed=False,
      cryptoOperationsAllowed=False, compilerAllowed=False, freezeAllowed=False))
external = Path(refs['externalOutputRoot'])
external.mkdir(mode=0o700)
environment = {key: os.environ[key] for key in
               ('HOME', 'USER', 'LOGNAME', 'TMPDIR') if key in os.environ}
environment.update(PATH='/usr/bin:/bin:/usr/sbin:/sbin', PYTHONDONTWRITEBYTECODE='1')
monitor = load(refs['monitorEntry']['path'], 'genuine0af_read_only_revalidation_monitor')
print(json.dumps(dict(event='root-read-only-revalidation-start', invocation=row(invocation_path))), flush=True)
terminal = monitor.monitor(argv, str(REPO), environment, external, 600, row(authority_path))
clean = (terminal['rawExitCode'] == 0
         and terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
         and terminal['timeout'] is terminal['forcedCleanup'] is False
         and all(terminal[key] == [] for key in
                 ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
assert family(SOURCE, own['sha256']) == own
assert family(PEER, peer_index['sha256']) == peer_index
assert row(PYTHON) == python and row(refs['monitorEntry']['path']) == refs['monitorEntry']
result_path = Path(refs['outputRoot']) / 'result.json'
actual = read(result_path) if result_path.is_file() else None
if clean:
    models.result(actual, refs)
    assert actual['adapterSourceIndex'] == own and actual['rootAuthority'] == row(authority_path)
    assert read(Path(refs['outputRoot']) / 'producer-admission-return.json') == actual['producerAdmission']
    assert (Path(refs['outputRoot']) / 'raw-metadata.json').read_bytes() == Path(refs['metadata']['path']).read_bytes()
write(observation_path, dict(schemaVersion=1,
      state='ROOT_OBSERVED_READ_ONLY_ARTIFACT_REVALIDATION_COMPLETE_V2' if clean else
            'ROOT_OBSERVED_READ_ONLY_ARTIFACT_REVALIDATION_FAILED_UNACCEPTED_V2',
      invocation=row(invocation_path), rootAuthority=row(authority_path), rootConfig=row(config_path),
      adapterSourceIndex=own, sourceReviewIndex=peer_index,
      ownedTerminal=row(external / 'terminal.json'), rawParentExitCode=terminal['rawExitCode'],
      allOwnedGroupsGone=terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True,
      revalidationProcessSucceeded=clean, actualRevalidationResult=row(result_path) if actual is not None else None,
      originalFailureReview=refs['originalFailureReview'], engine=refs['engine'], metadata=refs['metadata'],
      originalRecipeExitCode=0, originalParentExitCodes=[1, 1], originalBuildPreservationPassed=False,
      originalBuildAccepted=False, engineExecuted=False, guestExecuted=False, cryptoOperationsInvoked=False,
      compilerInvoked=False, freezeInvoked=False, operationalAdmission=False, runtimeAcceptanceClaim=False))
print(json.dumps(dict(event='root-read-only-revalidation-terminal', rawExitCode=terminal['rawExitCode'],
      clean=clean, rootObservation=row(observation_path))), flush=True)
raise SystemExit(0 if clean else 1)
