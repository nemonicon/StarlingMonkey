"""Source/pure contract checks; no controller, monitor, native helper or child action."""
import ast
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
source = (HERE / 'controller.py').read_text()
tree = ast.parse(source)
checks = 0


def check(value):
    global checks
    assert value
    checks += 1


def reject(call):
    global checks
    try:
        call()
    except (AssertionError, KeyError, TypeError):
        checks += 1
    else:
        raise AssertionError('unsafe pure model accepted')


# Only actual pure validators plus fixed path constants are compiled. No I/O/action function.
selected = [n for n in tree.body if isinstance(n, ast.Assign)]
selected += [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('validate_build_root', 'validate_stage', 'validate_peer')]
namespace = {'Path': Path}
exec(compile(ast.Module(body=selected, type_ignores=[]), '<actual-build-controller-pure-models>', 'exec'), namespace)
refs = json.loads((HERE / 'references.json').read_bytes())
stage = json.loads(Path(refs['actualStageResult']['path']).read_bytes())
stage_peer = json.loads(Path(refs['actualStageReview']['result']['path']).read_bytes())
root_observation = json.loads(Path(refs['actualStageRootObservation']['path']).read_bytes())
outer = json.loads(Path(root_observation['externalParentTerminal']['path']).read_bytes())
stage_root = dict(actualStageResult=refs['actualStageResult'], actualStageRootObservation=refs['actualStageRootObservation'])
namespace['validate_stage'](stage_root, stage, stage_peer, root_observation, outer)
checks += 1
for field, value in [('state', 'old-state'), ('verifiedPassed', False), ('sourceIndexSha256', '0' * 64), ('configuredSourceRoot', '/tmp/old-root'), ('actualStageResult', None), ('rootResult', None), ('externalParentTerminal', None)]:
    changed = copy.deepcopy(stage_peer)
    changed[field] = value
    reject(lambda: namespace['validate_stage'](stage_root, stage, changed, root_observation, outer))
for field, value in [('rawExitCode', 1), ('forcedCleanup', True), ('timeout', True), ('allObservedOwnedGroupsGone', False), ('remainingObservedPids', [101]), ('errors', ['error']), ('interruptedSignals', [15]), ('authority', None)]:
    changed = copy.deepcopy(outer)
    changed[field] = value
    reject(lambda: namespace['validate_stage'](stage_root, stage, stage_peer, root_observation, changed))
changed = copy.deepcopy(stage)
changed['destination'] = '/private/tmp/starling-node-compat/crypto-owner355-gc-v1-source'
reject(lambda: namespace['validate_stage'](stage_root, changed, stage_peer, root_observation, outer))

root = json.loads((HERE / 'future-root-authority.template.json').read_bytes())
own_index = dict(path=str(HERE / 'index.json'), sha256='0' * 64, bytes=1)
reject(lambda: namespace['validate_build_root'](root, own_index))
# A synthetic PURE shape exercises the exact future contract, not actual authority issuance.
root.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PHASE_V1', phase='build', sourceIndexSha256=namespace['NATIVE_SHA'], buildAllowed=True, externalControllerEntry=dict(path=str(HERE / 'controller.py')), externalControllerIndex=own_index)
namespace['validate_build_root'](root, own_index)
checks += 1
for field, value in [('state', 'old-state'), ('phase', 'stage'), ('variant', 'normal-off'), ('sourceIndexSha256', '0' * 64), ('buildAllowed', False), ('externalParentDeadlineSeconds', 2400), ('externalParentDeadlineSeconds', 7201), ('configuredSourceRoot', '/tmp/not-the-reviewed-source'), ('workRoot', '/tmp/reused-work'), ('freezeRoot', '/tmp/not-the-fresh-freeze'), ('nativeSourceFiles', 350), ('externalEmbeddingSources', 1), ('actualBuildResult', {}), ('engine', {}), ('reviewedGcPins', {})]:
    changed = copy.deepcopy(root)
    changed[field] = value
    reject(lambda: namespace['validate_build_root'](changed, own_index))
for flag in ('stageAllowed', 'freezeAllowed', 'exportAllowed', 'bootstrapAllowed', 'guestAllowed', 'keyOperationsAllowed', 'prototypeWorkloadsAllowed', 'componentAllowed', 'nativeSourceChangesAllowed', 'normalMutationAllowed', 'metadataProjectionAllowed', 'operationalAdmission', 'runtimeAcceptanceClaim', 'timingAllowed'):
    changed = copy.deepcopy(root)
    changed[flag] = True
    reject(lambda: namespace['validate_build_root'](changed, own_index))

peer = json.loads((HERE / 'future-controller-review.template.json').read_bytes())
reject(lambda: namespace['validate_peer'](peer, own_index))
peer.update(state='INDEPENDENT_CRYPTO_OWNER355_GC_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1', controllerSourceIndexSha256=own_index['sha256'], sourceReviewPassed=True)
namespace['validate_peer'](peer, own_index)
checks += 1
for field, value in [('controllerSourceIndexSha256', 'f' * 64), ('nativeSourceIndexSha256', '0' * 64), ('sourceOnly', False), ('sourceReviewPassed', False), ('ownerActionsInvoked', True), ('hostActionsInvoked', True), ('nativeBuildActionsInvoked', True)]:
    changed = copy.deepcopy(peer)
    changed[field] = value
    reject(lambda: namespace['validate_peer'](changed, own_index))

derivation = json.loads((HERE / 'monitor-derivation.json').read_bytes())
old = Path(derivation['source']['path']).read_bytes()
check(len(old) == derivation['source']['bytes'] and hashlib.sha256(old).hexdigest() == derivation['source']['sha256'])
edit, = derivation['edits']
check(old.count(edit['before'].encode()) == 1)
new = (HERE / 'monitor.py').read_bytes()
check(old.replace(edit['before'].encode(), edit['after'].encode()) == new)
check(new.replace(edit['after'].encode(), edit['before'].encode()) == old)
# Exercise the actual first API assert in both definitions; no monitor body executes.
for text, maximum in [(old.decode(), 2400), (new.decode(), 7200)]:
    module = ast.parse(text)
    monitor = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'monitor')
    assertion = next(n for n in monitor.body if isinstance(n, ast.Assert))
    code = compile(ast.Module(body=[assertion], type_ignores=[]), '<actual-monitor-first-assert-only>', 'exec')
    for deadline in (1, maximum):
        exec(code, dict(timeout_seconds=deadline, parent_grace_seconds=45))
        checks += 1
    for deadline in (0, maximum + 1):
        reject(lambda: exec(code, dict(timeout_seconds=deadline, parent_grace_seconds=45)))
    reject(lambda: exec(code, dict(timeout_seconds=1, parent_grace_seconds=46)))
check('terminal = monitor(argv, str(REPO), environment, output, 2400,' in new.decode())
main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
main_text = ast.get_source_segment(source, main)
check(main_text.index('authorize(config_row)') < main_text.index('spec.loader.exec_module(module)') < main_text.index('module.monitor('))
check("str(NATIVE / 'build.py')" in main_text and 'OUT, 7200,' in main_text)
check('finally:' in main_text and main_text.index('finally:') < main_text.index("assert terminal['rawExitCode']"))
check('environment = {**os.environ,' in main_text and not any(word in source for word in ('HOME=', "['HOME'] =", "['CODEX_HOME'] =")))
check("remainingObservedPids" in main_text and "not terminal['forcedCleanup']" in main_text)
print(json.dumps(dict(schemaVersion=1, checks=checks, state='PURE_BUILD_CONTROLLER_CONTRACT_CHECKS_PASSED', actualStageDataRead=True, sourceAndPureOnly=True, controllerImported=False, monitorInvoked=False, childOrNativeBuildInvoked=False)))
