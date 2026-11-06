"""Root-issued stage only; no compiler, helper admission, engine or guest call."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
BASE = REPO / 'tests/node-compat/foundation-scheduler'
SOURCE = BASE / 'combined-clock-diagnostics-native-integration-candidate-v3'
PEER = BASE / 'independent-clock-diagnostic357-native-integration-v3-source-review-v1'
PREFIX = BASE / 'combined-clock-diagnostic357-stage-v3-root'


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


assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1
# Clean before the first controller import or Bash entry; preserve user homes.
removed = sorted(k for k in os.environ if k.startswith('BASH_FUNC_') or k in
                 ('BASH_ENV', 'ENV', 'SHELLOPTS', 'BASHOPTS', 'CDPATH', 'GLOBIGNORE'))
for key in removed:
    del os.environ[key]
own = family(SOURCE, '3beebcf7a52d0bcf92ce7da16846993c38fea14ce3a1827c27796777ecc2f1ac')
peer = family(PEER, 'a3c58ffdb922a4fed4ea39437ed3b358b428319d20d6ba5f1c809d6c6db9188d')
refs = read(SOURCE / 'references.json')
assert descriptor(refs['controller']['path']) == refs['controller']
controller = load(refs['controller']['path'], 'clock357_stage_only_reviewed_controller')
peer_value, _ = controller.proof(dict(index=peer, result=descriptor(PEER / 'results.json')),
                                 descriptor(PEER / 'result-contract.json'))
controller.peer_model(peer_value, own)
authority = read(SOURCE / 'root-authority.template.json')
authority.update(phase='stage', sourceIndex=own,
                 sourceReview=dict(index=peer, result=descriptor(PEER / 'results.json')),
                 sourceStageAllowed=True, nativeBuildAllowed=False, deadlineSeconds=600)
controller.root_model(authority, own, refs, 'stage')
for key in ('sourceRoot', 'workRoot', 'freezeRoot', 'stageOutputRoot', 'stageJournal'):
    controller.absent(Path(refs['contexts'][key]))
assert descriptor(sys.executable) == refs['pythonExecutable']
authority_path = Path(str(PREFIX) + '-authority.json')
config_path = Path(str(PREFIX) + '-config.json')
invocation_path = Path(str(PREFIX) + '-invocation.json')
observation_path = Path(str(PREFIX) + '-results.json')
external = Path('/private/tmp/starling-node-compat/combined-clock-diagnostic357-v3-stage-root-monitor')
for path in (authority_path, config_path, invocation_path, observation_path, external):
    controller.absent(path)
write(authority_path, authority)
config = read(SOURCE / 'config.template.json')
config.update(sourceIndex=own, phase='stage', rootAuthority=descriptor(authority_path))
write(config_path, config)
argv = [refs['pythonExecutable']['path'], '-B', '-I', refs['controller']['path'],
        'stage-parent', json.dumps(descriptor(config_path), separators=(',', ':'))]
assert family(Path(refs['monitorIndex']['path']).parent,
              refs['monitorIndex']['sha256']) == refs['monitorIndex']
assert descriptor(refs['monitorEntry']['path']) == refs['monitorEntry']
write(invocation_path, dict(schemaVersion=1, state='ROOT_ISSUED_CLOCK_DIAGNOSTIC357_STAGE_V3',
      sourceIndex=own, sourceReviewIndex=peer, rootAuthority=descriptor(authority_path),
      rootConfig=descriptor(config_path), launcher=descriptor(Path(__file__).resolve()),
      actualArgv=argv, outerDeadlineSeconds=720, innerDeadlineSeconds=600,
      removedEnvironmentNames=removed, environmentValuesRecorded=False,
      nativeBuildAllowed=False, engineExecutionAllowed=False, guestAllowed=False))
external.mkdir(mode=0o700)
monitor = load(refs['monitorEntry']['path'], 'original0af_clock357_stage_root_monitor')
print(json.dumps(dict(event='clock357-stage-start', invocation=descriptor(invocation_path))), flush=True)
terminal = monitor.monitor(argv, str(REPO), dict(os.environ), external, 720,
                           descriptor(authority_path))
clean = (terminal['rawExitCode'] == 0 and
         terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and
         terminal['timeout'] is terminal['forcedCleanup'] is False and
         all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
actual_path = Path(refs['contexts']['stageJournal'])
actual = read(actual_path) if actual_path.is_file() else None
if clean:
    assert actual['state'] == 'CLOCK_DIAGNOSTIC357_SOURCE_STAGED_NOT_BUILT_V3'
    assert actual['sourceIndex'] == own and len(actual['copiesCompleted']) == 1583
    assert actual['allSourceOriginalsPreserved'] is actual['finalInputProtectionPassed'] is True
    assert actual['originalGitUnchanged'] is actual['originalRepositoryIndexUnchanged'] is True
assert family(SOURCE, own['sha256']) == own
assert family(PEER, peer['sha256']) == peer
write(observation_path, dict(schemaVersion=1,
      state='ROOT_OBSERVED_CLOCK_DIAGNOSTIC357_STAGE_COMPLETE_UNREVIEWED_V3' if clean else
            'ROOT_OBSERVED_CLOCK_DIAGNOSTIC357_STAGE_FAILED_UNACCEPTED_V3',
      invocation=descriptor(invocation_path), sourceIndex=own, sourceReviewIndex=peer,
      rootAuthority=descriptor(authority_path), rootConfig=descriptor(config_path),
      ownedTerminal=descriptor(external / 'terminal.json'), rawParentExitCode=terminal['rawExitCode'],
      allOwnedGroupsGone=terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True,
      actualStageResult=descriptor(actual_path) if actual is not None else None,
      stageProcessSucceeded=clean, independentActualStageReviewRequired=True,
      nativeBuildExecuted=False, engineExecuted=False, guestExecuted=False,
      operationalAdmission=False))
print(json.dumps(dict(event='clock357-stage-terminal', rawExitCode=terminal['rawExitCode'],
                      clean=clean, observation=descriptor(observation_path))), flush=True)
raise SystemExit(0 if clean else 1)
