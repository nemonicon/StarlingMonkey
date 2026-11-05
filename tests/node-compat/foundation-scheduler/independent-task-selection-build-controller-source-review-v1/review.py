"""Independent finite source, actual staging DATA and isolated predicate audit."""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'task-selection-build-controller-candidate-v1'
EXPECTED = 'dd69c40580cfbb8671a4e3197e65a9e7f763c96f623ee95e6d3e14aa144c980f'
SEED = HERE.parents[1] / 'foundation-crypto/independent-ownership-secret-integration-source-review-v1'


def row(path):
    path = Path(path); data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def main():
    assert __debug__ and sys.dont_write_bytecode
    seed = row(SEED / 'index.json')
    assert seed['sha256'] == '8665997e4edab561a0e0e63235104b8e358072995725002704f25e4499dfca45'
    seed_index = json.loads((SEED / 'index.json').read_bytes())
    for value in seed_index['files']:
        assert value['path'] and not Path(value['path']).is_absolute() and '..' not in Path(value['path']).parts
        assert row(SEED / value['path']) == dict(value, path=str(SEED / value['path']))
    assert {p.relative_to(SEED).as_posix() for p in SEED.rglob('*') if p.is_file()} == {'index.json'} | {r['path'] for r in seed_index['files']}
    assert not any(p.is_symlink() for p in SEED.rglob('*'))
    spec = importlib.util.spec_from_file_location('authenticated_selector_build_generic_reader', SEED / 'read-source.py')
    reader = importlib.util.module_from_spec(spec); spec.loader.exec_module(reader)
    need, regular, load, family = reader.need, reader.regular, reader.load, reader.family
    family(seed)
    own = row(SOURCE / 'index.json')
    need(own['sha256'] == EXPECTED and own['bytes'] == 2739, 'exact dd69 source index')
    index = family(own)
    need(len(index['files']) == 17, 'complete17 source members')
    refs = json.loads((SOURCE / 'references.json').read_bytes())
    source_index = family(refs['sourceIndex'])
    for value in refs['families']:
        family(value['index'])
    inputs = json.loads((SOURCE / 'input-hashes.json').read_bytes())
    need(len(inputs['files']) == 2594, 'all2594 source inputs')
    for value in inputs['files']:
        regular(value)
    source_root = Path(refs['sourceIndex']['path']).parent
    baseline = json.loads((source_root / 'baseline-pins.json').read_bytes())
    for value in baseline['families'].values():
        family(value)
    policy = json.loads((source_root / 'policy.json').read_bytes())
    need(len(policy['expectedNativeSourceManifest']) == 342 and policy['taskSelectionSourcePolicy']['requiresFullNativeRebuild'] is True and policy['taskSelectionSourcePolicy']['compatibleWithParentEngineAbi'] is False, 'real342 ABI-changing source lineage')
    configured = Path(refs['configuredSourceRoot'])
    for value in policy['expectedNativeSourceManifest']:
        path = configured / value['path']
        regular(dict(path=str(path), sha256=value['sha256'], bytes=path.stat().st_size))
    journal = load(refs['actualJournal'])
    observation = load(refs['stageObservation'])
    need(len(journal['copies']) == len(observation['targetObservations']) == 566, 'all566 actual stage targets')
    observed = {r['path']: r for r in observation['targetObservations']}
    for value in journal['copies']:
        original = regular(value['original'])
        target = regular(dict(value['original'], path=value['path']))
        o = observed[value['path']]
        need(o['status'] == 'match' and o['expected'] == value['original'] and o['distinctInode'] is True, 'whole actual pair observation')
        need(stat.S_IMODE(original.stat().st_mode) == stat.S_IMODE(target.stat().st_mode) == o['mode'] == o['expectedMode'], 'fixed staged pair modes')
        need((original.stat().st_dev, original.stat().st_ino) != (target.stat().st_dev, target.stat().st_ino), 'actual independent staged copies')
    need((configured / '.git/HEAD').read_text() == '54b3329b3ce818fd1f244e871e9c259b63667cda\n' and not (configured / '.git/commondir').exists() and not (configured / '.git/objects/info/alternates').exists(), 'actual detached original source context')
    resource = load(refs['resourceFreezeReceipt'])
    need(len(resource['copies']) == 666 and sum(r['original'] is not None for r in resource['copies']) == 663, 'resource666/663 protection')
    for value in resource['copies']:
        path = regular({k: value[k] for k in ['path', 'sha256', 'bytes']})
        need(stat.S_IMODE(path.stat().st_mode) == 0o600, 'fixed resource frozen0600 mode')
        if value['original'] is not None:
            regular(value['original'])
    frozen = Path(refs['resourceFreezeReceipt']['path']).parent
    need({str(p) for p in frozen.rglob('*') if p.is_file()} == {r['path'] for r in resource['copies']} | {str(frozen / 'normal-off-freeze-receipt.json')}, 'complete old667 membership')
    old_stage = load(refs['resourceStage'])
    need(len(old_stage['copies']) == 501, 'old501 protection')
    for value in old_stage['copies']:
        regular(value['original']); regular(dict(value['original'], path=value['path']))
    text = (SOURCE / 'controller.py').read_text(); tree = ast.parse(text)
    functions = {v.name: v for v in tree.body if isinstance(v, ast.FunctionDef)}
    derivations = json.loads((SOURCE / 'derivations.json').read_bytes())
    for value in derivations['exactPrimitiveExtractions']:
        donor = regular(value['donor']).read_text(); donor_tree = ast.parse(donor)
        original = next(v for v in donor_tree.body if isinstance(v, ast.FunctionDef) and v.name == value['name'])
        need(ast.get_source_segment(text, functions[value['name']]) == ast.get_source_segment(donor, original) == value['source'], 'exact original streamed primitive')
    need(len(derivations['exactPrimitiveExtractions']) == 3 and derivations['donorGlobalsRebound'] is False, 'three primitives without donor rebinding')
    apis = json.loads((SOURCE / 'api-bindings.json').read_bytes())
    for key, actual_key in [('originalMonitor', 'monitorEntry'), ('originalLifecycle', 'lifecycleEntry')]:
        regular(apis[key]['entry']); family(apis[key]['index'])
        need(apis[key]['entry'] == refs[actual_key], 'exact original module API role')
    monitor_tree = ast.parse(Path(refs['monitorEntry']['path']).read_bytes())
    monitor = next(v for v in monitor_tree.body if isinstance(v, ast.FunctionDef) and v.name == 'monitor')
    need([v.arg for v in monitor.args.args] == ['argv', 'cwd', 'environment', 'output', 'timeout_seconds', 'authority'], 'actual six-positional monitor API')
    lifecycle_tree = ast.parse(Path(refs['lifecycleEntry']['path']).read_bytes())
    lifecycle = {v.name: v for v in lifecycle_tree.body if isinstance(v, ast.FunctionDef)}
    for name, args in [('prepare_output', ['output', 'free_bytes', 'required']), ('monitor_owned_command', ['command', 'cwd', 'environment', 'log', 'free_bytes', 'minimum_free', 'interval', 'term_seconds', 'kill_seconds']), ('finalize_status', ['result']), ('publish_result', ['output', 'result', 'stream', 'writer'])]:
        need([v.arg for v in lifecycle[name].args.args] == args, 'genuine lifecycle parameter shape ' + name)
    stage_proof = load(refs['actualStageReview']['result']); stage_contract = load(refs['actualStageContract'])
    for value in load(refs['actualStageInputLedger'])['files']:
        regular(value)
    environment = dict(Path=Path, REPO=Path('/Users/dan/dev/StarlingMonkey'), OWN=SOURCE, SOURCE=configured, WORK=Path(refs['workRoot']), FREEZE=Path(refs['freezeRoot']), OUTPUT=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-root'), EXTERNAL=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-external-root'), SOURCE_SHA=refs['sourceIndex']['sha256'])
    names = ['validate_root', 'validate_stage', 'validate_peer', 'validate_lifecycle_zero']
    isolated = ast.Module(body=[functions[n] for n in names], type_ignores=[])
    exec(compile(ast.fix_missing_locations(isolated), '<isolated source predicates>', 'exec'), environment)
    pure = 0
    root = json.loads((SOURCE / 'future-root-authority.template.json').read_bytes())
    root.update(state='ROOT_REVIEWED_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_BUILD_V1', buildAllowed=True, controllerIndex=own, controllerEntry=row(SOURCE / 'controller.py'))
    environment['validate_root'](root, own, refs); pure += 1
    environment['validate_stage'](stage_proof, stage_contract, refs); pure += 1
    def reject(fn, *args):
        nonlocal pure
        try:
            fn(*args)
        except (AssertionError, KeyError, TypeError):
            pure += 1
        else:
            raise AssertionError('invalid pure input accepted')
    for key, value in root.items():
        if value is False:
            bad = copy.deepcopy(root); bad[key] = True
            reject(environment['validate_root'], bad, own, refs)
    for key, value in [('sourceIndexSha256', '0' * 64), ('jobs', 2), ('configuredSourceRoot', '/old/source'), ('workRoot', '/old/work'), ('externalParentDeadlineSeconds', 7201), ('buildType', 'Debug')]:
        bad = copy.deepcopy(root); bad[key] = value
        reject(environment['validate_root'], bad, own, refs)
    peer = dict(schemaVersion=1, state='INDEPENDENT_SCHEDULER_TASK_SELECTION342_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1', controllerSourceIndexSha256=EXPECTED, taskSelectionSourceIndexSha256=refs['sourceIndex']['sha256'], sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False, hostActionsInvoked=False, nativeBuildActionsInvoked=False)
    environment['validate_peer'](peer, own); pure += 1
    for key, value in peer.items():
        if isinstance(value, bool):
            bad = dict(peer); bad[key] = not value
            reject(environment['validate_peer'], bad, own)
    success = dict(rawChildExitCode=0, status=0, lifecycleComplete=True, childStarted=True, stoppedForDiskSpace=False, stopReason=None, sigtermReceived=0, temporarySigtermHandlerRestored=True, launcherErrors=[], ownedGroupCleanup=dict(complete=True, rawChildExitCode=0, events=[], errors=[]))
    environment['validate_lifecycle_zero'](success); pure += 1
    for key, value in [('rawChildExitCode', 1), ('childStarted', False), ('stoppedForDiskSpace', True), ('temporarySigtermHandlerRestored', False), ('stopReason', 'disk-space-stop'), ('launcherErrors', ['error'])]:
        bad = copy.deepcopy(success); bad[key] = value
        reject(environment['validate_lifecycle_zero'], bad)
    for key, value in [('complete', False), ('rawChildExitCode', 1), ('events', ['sent']), ('errors', ['error'])]:
        bad = copy.deepcopy(success); bad['ownedGroupCleanup'][key] = value
        reject(environment['validate_lifecycle_zero'], bad)
    authorize_text = ast.get_source_segment(text, functions['authorize'])
    for token in ['family(index)', 'for r in ledger[', 'for r in preparation[', 'validate_stage(stage_peer', 'validate_peer(peer,index)', 'captured+=protect_resource(refs)', 'recheck(frame);return frame']:
        need(token in authorize_text, 'complete primitive authentication gate ' + token)
    need(text.index('def authorize(') < text.index('def load_actual(') and 'finally:recheck(frame)' in text, 'authorization and final/failure source checks')
    need('monitor.monitor(argv,str(REPO)' in text and 'EXTERNAL,7200' in text, 'real original monitor call and deadline')
    need("load_actual(frame['refs']['lifecycleEntry']" in text and 'lifecycle.monitor_owned_command(command,str(SOURCE),child_env,log,free)' in text, 'genuine original lifecycle invocation')
    need('lifecycle.finalize_status(result);lifecycle.publish_result(OUTPUT,result,writer=write)' in text, 'whole lifecycle result retained')
    need(text.index('validate_lifecycle_zero(result)') < text.index("result['actualMetadataObservation']=metadata_observation(frame)"), 'strict cleanup check before metadata observation')
    need('model.validate_metadata(metadata,read(policy_row)' in text and "shape==dict(state='FINITE_RESOURCE_TASK_SELECTION342_METADATA_SHAPE_ONLY'" in text, 'actual new shape model with unchanged metadata')
    need("inherited={k:v for k,v in os.environ.items()" in text and "'HOME'" not in text and 'module.HERE=' not in text and 'module.REPO=' not in text, 'no HOME or donor-global rebinding')
    parsed = []
    for path in SOURCE.glob('*.py'):
        ast.parse(path.read_bytes(), filename=str(path)); parsed.append(path.name)
    need(len(parsed) == 4, 'all four Python sources parse')
    for path in [refs['workRoot'], refs['freezeRoot'], str(environment['OUTPUT']), str(environment['EXTERNAL'])]:
        need(not Path(path).exists(), 'actual build/freeze output absent before authorization')
    for value in list(reader.checked.values()):
        regular(value)
    write('input-hashes.json', dict(schemaVersion=1, files=[{k: v for k, v in item.items() if k != 'identity'} for _, item in sorted(reader.checked.items())]))
    write('audit.json', dict(schemaVersion=1, state='INDEPENDENT_SELECTOR_BUILD_CONTROLLER_SOURCE_AUDIT_PASSED_V1', controllerIndex=own, taskSelectionSourceIndex=refs['sourceIndex'], checks=reader.checks, uniqueInputs=len(reader.checked), independentPureCases=pure, pythonAst=parsed, stagedPairs=566, actualStageReview=refs['actualStageReview'], originalApisPreserved=True, sourceOnly=True, ownerActionsInvoked=False, hostActionsInvoked=False, nativeBuildActionsInvoked=False))
    print(json.dumps(dict(checks=reader.checks, uniqueInputs=len(reader.checked), independentPureCases=pure, ownerActionsInvoked=False)))


if __name__ == '__main__':
    main()
