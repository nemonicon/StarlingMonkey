"""Root-issued Release native build only; no engine or guest execution."""
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
PREFIX = BASE / 'combined-clock-diagnostic357-build-v3-root'


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


# Common reader functions copied from Root stage launcher SHA256 0d779ac0beded3d3ece94693f1933c3cca04ea4ed1fa5c504013e9cb0f32a581; original unchanged.
assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1
assert len(sys.argv) == 2 and len(sys.argv[1]) == 64
removed = sorted(k for k in os.environ if k.startswith('BASH_FUNC_') or k in
                 ('BASH_ENV', 'ENV', 'SHELLOPTS', 'BASHOPTS', 'CDPATH', 'GLOBIGNORE'))
for key in removed:
    del os.environ[key]
own = family(SOURCE, '3beebcf7a52d0bcf92ce7da16846993c38fea14ce3a1827c27796777ecc2f1ac')
peer = family(PEER, 'a3c58ffdb922a4fed4ea39437ed3b358b428319d20d6ba5f1c809d6c6db9188d')
refs = read(SOURCE / 'references.json')
assert descriptor(refs['controller']['path']) == refs['controller']
controller = load(refs['controller']['path'], 'clock357_build_only_reviewed_controller')
peer_value, _ = controller.proof(dict(index=peer, result=descriptor(PEER / 'results.json')),
                                 descriptor(PEER / 'result-contract.json'))
controller.peer_model(peer_value, own)
stage_peer_path = BASE / 'independent-clock-diagnostic357-stage-v3-results-review-v1'
stage_peer = family(stage_peer_path, sys.argv[1])
stage_result = descriptor(Path(refs['contexts']['stageJournal']))
stage_proof = dict(index=stage_peer, result=descriptor(stage_peer_path / 'results.json'))
stage_value, _ = controller.proof(stage_proof, descriptor(stage_peer_path / 'result-contract.json'))
controller.stage_review_model(stage_value, own, stage_result)
stage_root_path = BASE / 'combined-clock-diagnostic357-stage-v3-root-results.json'
assert descriptor(stage_root_path)['sha256'] == '89ba64054cf68d60e4abb68f83f1abdcc3fb4c2df71c4bfa9323ba65ee5c41da'
stage_root = read(stage_root_path)
assert stage_root['actualStageResult'] == stage_result and stage_root['stageProcessSucceeded'] is True
authority = read(SOURCE / 'root-authority.template.json')
authority.update(phase='build', sourceIndex=own,
                 sourceReview=dict(index=peer, result=descriptor(PEER / 'results.json')),
                 actualStageReview=stage_proof, actualStageResult=stage_result,
                 sourceStageAllowed=False, nativeBuildAllowed=True, deadlineSeconds=7200)
controller.root_model(authority, own, refs, 'build')
for key in ('workRoot', 'freezeRoot', 'buildOutputRoot', 'buildResultRoot'):
    controller.absent(Path(refs['contexts'][key]))
assert descriptor(sys.executable) == refs['pythonExecutable']
authority_path = Path(str(PREFIX) + '-authority.json')
config_path = Path(str(PREFIX) + '-config.json')
invocation_path = Path(str(PREFIX) + '-invocation.json')
observation_path = Path(str(PREFIX) + '-results.json')
external = Path('/private/tmp/starling-node-compat/combined-clock-diagnostic357-v3-build-root-monitor')
for path in (authority_path, config_path, invocation_path, observation_path, external):
    controller.absent(path)
write(authority_path, authority)
config = read(SOURCE / 'config.template.json')
config.update(sourceIndex=own, phase='build', rootAuthority=descriptor(authority_path))
write(config_path, config)
argv = [refs['pythonExecutable']['path'], '-B', '-I', refs['controller']['path'],
        'build-parent', json.dumps(descriptor(config_path), separators=(',', ':'))]
assert family(Path(refs['monitorIndex']['path']).parent,
              refs['monitorIndex']['sha256']) == refs['monitorIndex']
assert descriptor(refs['monitorEntry']['path']) == refs['monitorEntry']
write(invocation_path, dict(schemaVersion=1, state='ROOT_ISSUED_CLOCK_DIAGNOSTIC357_BUILD_V3',
      sourceIndex=own, sourceReviewIndex=peer, actualStageReview=stage_proof,
      actualStageResult=stage_result, rootAuthority=descriptor(authority_path),
      rootConfig=descriptor(config_path), launcher=descriptor(Path(__file__).resolve()),
      actualArgv=argv, outerDeadlineSeconds=7200, innerDeadlineSeconds=7200,
      removedEnvironmentNames=removed, environmentValuesRecorded=False,
      buildType='Release', jobs=1, entropy='OFF', gcAllowed=False, oomAllowed=False,
      debugAllowed=False, resetAllowed=False, engineExecutionAllowed=False, guestAllowed=False))
external.mkdir(mode=0o700)
monitor = load(refs['monitorEntry']['path'], 'original0af_clock357_build_root_monitor')
print(json.dumps(dict(event='clock357-build-start', invocation=descriptor(invocation_path))), flush=True)
terminal = monitor.monitor(argv, str(REPO), dict(os.environ), external, 7200,
                           descriptor(authority_path))
clean = (terminal['rawExitCode'] == 0 and
         terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and
         terminal['timeout'] is terminal['forcedCleanup'] is False and
         all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')))
actual_path = Path(refs['contexts']['buildResultRoot']) / 'result.json'
actual = read(actual_path) if actual_path.is_file() else None
if clean:
    assert actual['launcherExitCode'] == actual['rawChildExitCode'] == 0
    assert actual['allSourceStageOriginalAndCacheInputsPreserved'] is True
    engine = actual['engine']
    metadata = actual['metadata']
    assert descriptor(engine['path']) == engine and descriptor(metadata['path']) == metadata
    raw = read(metadata['path'])
    assert len(raw) == 82 and len(raw['sourceManifest']) == 357
    assert len(raw['componentizeSourceManifest']) == 3 and len(raw['selectedModuleManifests']) == 11
assert family(SOURCE, own['sha256']) == own
assert family(PEER, peer['sha256']) == peer
assert family(stage_peer_path, stage_peer['sha256']) == stage_peer
write(observation_path, dict(schemaVersion=1,
      state='ROOT_OBSERVED_CLOCK_DIAGNOSTIC357_BUILD_COMPLETE_UNREVIEWED_V3' if clean else
            'ROOT_OBSERVED_CLOCK_DIAGNOSTIC357_BUILD_FAILED_UNACCEPTED_V3',
      invocation=descriptor(invocation_path), sourceIndex=own, sourceReviewIndex=peer,
      actualStageReview=stage_proof, actualStageResult=stage_result,
      rootAuthority=descriptor(authority_path), rootConfig=descriptor(config_path),
      ownedTerminal=descriptor(external / 'terminal.json'), rawParentExitCode=terminal['rawExitCode'],
      allOwnedGroupsGone=terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True,
      actualBuildResult=descriptor(actual_path) if actual is not None else None,
      buildProcessSucceeded=clean, rawRecipeExitCode=actual.get('rawChildExitCode') if actual else None,
      engine=actual.get('engine') if actual else None, metadata=actual.get('metadata') if actual else None,
      independentActualBuildReviewRequired=True, freezeExecuted=False,
      engineExecuted=False, guestExecuted=False, clockRuntimeInvoked=False,
      operationalAdmission=False))
print(json.dumps(dict(event='clock357-build-terminal', rawExitCode=terminal['rawExitCode'],
                      clean=clean, observation=descriptor(observation_path))), flush=True)
raise SystemExit(0 if clean else 1)
