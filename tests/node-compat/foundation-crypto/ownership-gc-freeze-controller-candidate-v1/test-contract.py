"""Pure future-wire/source checks only; synthetic build fixtures are never proof."""
import ast
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = (HERE / 'controller.py').read_text()
tree = ast.parse(source)
pure_names = {'validate_stage', 'validate_freeze_root', 'validate_build_evidence', 'validate_peer'}
nodes = [n for n in tree.body if isinstance(n, ast.Assign)] + [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in pure_names]
env = {'Path': Path}
exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual-freeze-caller-pure-models>', 'exec'), env)
checks = 0


def check(value):
    global checks
    assert value
    checks += 1


def reject(call):
    global checks
    try:
        call()
    except (AssertionError, TypeError, KeyError):
        checks += 1
    else:
        raise AssertionError('unsafe synthetic pure wire accepted')


refs = json.loads((HERE / 'references.json').read_bytes())
staged = json.loads(Path(refs['actualStageResult']['path']).read_bytes())
stage_peer = json.loads(Path(refs['actualStageReview']['result']['path']).read_bytes())
stage_observation = json.loads(Path(refs['actualStageRootObservation']['path']).read_bytes())
stage_terminal = json.loads(Path(stage_observation['externalParentTerminal']['path']).read_bytes())
env['validate_stage'](dict(actualStageResult=refs['actualStageResult'], actualStageRootObservation=refs['actualStageRootObservation']), staged, stage_peer, stage_observation, stage_terminal)
checks += 1

own_index = dict(path=str(HERE / 'index.json'), sha256='0' * 64, bytes=1)
root = json.loads((HERE / 'future-root-authority.template.json').read_bytes())
reject(lambda: env['validate_freeze_root'](root, own_index))
def model_row(path):
    return dict(path=path, sha256='0' * 64, bytes=1)
# Pure synthetic wire shapes: no actual build/artifact/Root authority is issued.
root.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PHASE_V1', phase='freeze', sourceIndexSha256=env['NATIVE_SHA'], freezeAllowed=True, externalControllerEntry=dict(path=str(HERE / 'controller.py')), externalControllerIndex=own_index, actualBuildResult=model_row(env['BUILD_OUTPUT'] + '/result.json'), actualBuildExternalTerminal=model_row(env['BUILD_EXTERNAL'] + '/terminal.json'), actualBuildRootAuthority=model_row('/synthetic-only/build-root-authority.json'), actualBuildRootObservation=model_row('/synthetic-only/build-root-observation.json'), engine=model_row(env['WORK'] + '/artifacts/synthetic.engine.wasm'))
root['metadata'] = model_row(root['engine']['path'] + '.build.json')
env['validate_freeze_root'](root, own_index)
checks += 1
for key, value in [('phase', 'build'), ('freezeAllowed', False), ('variant', 'normal-off'), ('externalParentDeadlineSeconds', 7200), ('sourceIndexSha256', 'f' * 64), ('configuredSourceRoot', '/old-source'), ('workRoot', '/old-work'), ('freezeRoot', '/old-freeze'), ('nativeSourceFiles', 350), ('reviewedGcPins', {})]:
    changed = copy.deepcopy(root)
    changed[key] = value
    reject(lambda: env['validate_freeze_root'](changed, own_index))
for flag in ('stageAllowed', 'buildAllowed', 'exportAllowed', 'bootstrapAllowed', 'guestAllowed', 'keyOperationsAllowed', 'prototypeWorkloadsAllowed', 'componentAllowed', 'nativeSourceChangesAllowed', 'normalMutationAllowed', 'metadataProjectionAllowed', 'operationalAdmission', 'runtimeAcceptanceClaim', 'timingAllowed'):
    changed = copy.deepcopy(root)
    changed[flag] = True
    reject(lambda: env['validate_freeze_root'](changed, own_index))

built = dict(state='native-build-completed-runtime-pending', sourceIndexSha256=env['NATIVE_SHA'], rawChildExitCode=0, launcherExitCode=0, lifecycleComplete=True, ownedGroupCleanup=dict(complete=True), allOriginalNormalAndStageBytesPreserved=True, configuredSourceRoot=env['SOURCE'], workRoot=env['WORK'], externalParentDeadlineSeconds=7200, rootAuthority=root['actualBuildRootAuthority'], logSha256='0' * 64)
outer = dict(rawExitCode=0, parentOwnedGroupGone=True, allObservedOwnedGroupsGone=True, forcedCleanup=False, timeout=False, remainingObservedPids=[], errors=[], interruptedSignals=[], authority=root['actualBuildRootAuthority'])
proof = dict(schemaVersion=1, state='INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_BUILD_REVIEW_PASSED_V1', verifiedPassed=True, sourceIndexSha256=env['NATIVE_SHA'], variant='gc-off', nativeSourceFiles=355, externalEmbeddingSources=3, configuredSourceRoot=env['SOURCE'], workRoot=env['WORK'], actualBuildResult=root['actualBuildResult'], externalParentTerminal=root['actualBuildExternalTerminal'], rootBuildAuthority=root['actualBuildRootAuthority'], rootBuildObservation=root['actualBuildRootObservation'], engine=root['engine'], metadata=root['metadata'], buildLog=model_row(env['BUILD_OUTPUT'] + '/build.log'), externalParentExitCode=0, innerBuilderExitCode=0, allOwnedGroupsGone=True, noForcedCleanup=True, sourceAndNormalProtectionRechecked=True, actualFreezeVerified=False, engineExecuted=False, guestKeyCryptoGcActionsInvoked=False, operationalAdmission=False)
metadata = dict(engineSha256='0' * 64, engineBytes=1, gcStress=True, entropyPolicy='off', oomTesting=False, sourceManifest=[None] * 355, componentizeSourceManifest=[None] * 3, cryptoKeyOwnershipPolicy=dict(sourceFiles=355, runtimeValidation=None), cmakeCachePath=env['WORK'] + '/synthetic/CMakeCache.txt', compileCommandsPath=env['WORK'] + '/synthetic/compile_commands.json')
def invoke(b=built, o=outer, p=proof, m=metadata):
    env['validate_build_evidence'](root, b, o, p, m)
invoke()
checks += 1
for key, value in [('rawChildExitCode', 1), ('launcherExitCode', 1), ('lifecycleComplete', False), ('allOriginalNormalAndStageBytesPreserved', False), ('externalParentDeadlineSeconds', 2400), ('workRoot', '/old-work'), ('rootAuthority', None)]:
    changed = copy.deepcopy(built)
    changed[key] = value
    reject(lambda: invoke(b=changed))
for key, value in [('rawExitCode', 1), ('forcedCleanup', True), ('timeout', True), ('parentOwnedGroupGone', False), ('allObservedOwnedGroupsGone', False), ('remainingObservedPids', [101]), ('errors', ['x']), ('interruptedSignals', [15]), ('authority', None)]:
    changed = copy.deepcopy(outer)
    changed[key] = value
    reject(lambda: invoke(o=changed))
for key, value in [('state', 'later-frozen-artifact-state'), ('verifiedPassed', False), ('externalEmbeddingSources', 1), ('sourceIndexSha256', 'f' * 64), ('actualBuildResult', None), ('externalParentTerminal', None), ('rootBuildAuthority', None), ('rootBuildObservation', None), ('engine', None), ('metadata', None), ('innerBuilderExitCode', 1), ('allOwnedGroupsGone', False), ('noForcedCleanup', False), ('sourceAndNormalProtectionRechecked', False), ('actualFreezeVerified', True), ('engineExecuted', True), ('guestKeyCryptoGcActionsInvoked', True), ('operationalAdmission', True)]:
    changed = copy.deepcopy(proof)
    changed[key] = value
    reject(lambda: invoke(p=changed))
for key, value in [('engineSha256', 'f' * 64), ('engineBytes', 2), ('gcStress', False), ('entropyPolicy', 'runtime-only'), ('oomTesting', True), ('sourceManifest', [None] * 350), ('componentizeSourceManifest', [None]), ('cmakeCachePath', '/old-work/CMakeCache.txt')]:
    changed = copy.deepcopy(metadata)
    changed[key] = value
    reject(lambda: invoke(m=changed))

peer = json.loads((HERE / 'future-controller-review.template.json').read_bytes())
reject(lambda: env['validate_peer'](peer, own_index))
peer.update(state='INDEPENDENT_CRYPTO_OWNER355_GC_FREEZE_CONTROLLER_SOURCE_REVIEW_PASSED_V1', sourceReviewPassed=True, controllerSourceIndexSha256=own_index['sha256'])
env['validate_peer'](peer, own_index)
checks += 1
for key in ('ownerActionsInvoked', 'hostActionsInvoked', 'nativeFreezeActionsInvoked'):
    changed = copy.deepcopy(peer)
    changed[key] = True
    reject(lambda: env['validate_peer'](changed, own_index))
support = json.loads((HERE / 'support-derivations.json').read_bytes())
donor = Path(support['source']['path']).read_bytes()
check(hashlib.sha256(donor).hexdigest() == support['source']['sha256'] and len(donor) == support['source']['bytes'])
before_tree = ast.parse(donor.decode())
for row in support['exactUnchangedFunctions']:
    old = ast.get_source_segment(donor.decode(), next(n for n in before_tree.body if isinstance(n, ast.FunctionDef) and n.name == row['name']))
    new = ast.get_source_segment(source, next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == row['name']))
    check(old == new and hashlib.sha256(new.encode()).hexdigest() == row['sourceSha256'])
main = ast.get_source_segment(source, next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main'))
check(main.index('authorize(config_row)') < main.index('spec.loader.exec_module(module)') < main.index('module.monitor('))
check("str(NATIVE / 'freeze.py')" in main and 'OUT, 2400,' in main and 'finally:' in main)
check('sys.dont_write_bytecode' in main and 'environment = {**os.environ,' in main)
check("remainingObservedPids" in main and "not terminal['forcedCleanup']" in main)
print(json.dumps(dict(schemaVersion=1, state='FREEZE_CONTROLLER_PURE_CONTRACT_CHECKS_PASSED', checks=checks, buildFixturesSyntheticOnly=True, actualBuildEvidenceRead=False, controllerImported=False, monitorOrNativeFreezeInvoked=False, sourceAndPureOnly=True)))
