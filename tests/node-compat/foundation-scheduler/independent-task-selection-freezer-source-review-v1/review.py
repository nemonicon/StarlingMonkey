"""Independent source/DATA/pure audit, with no operational module imports."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import os
import shlex
import stat
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
SOURCE = BASE / 'task-selection-freezer-candidate-v1'
SOURCE_SHA = '83c07efa19f56c0ad725212bf63dfac4b70ca1ed225b7737174e7357f15737e8'
TASK_SHA = '88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1'
SEED = BASE.parent / 'foundation-crypto/independent-ownership-secret-integration-source-review-v1'


def row(path):
    path = Path(path)
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(data)
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=path.stat().st_size)


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    seed_row = row(SEED / 'index.json')
    assert seed_row['sha256'] == '8665997e4edab561a0e0e63235104b8e358072995725002704f25e4499dfca45'
    seed = json.loads((SEED / 'index.json').read_bytes())
    names = {'index.json'}
    for item in seed['files']:
        assert row(SEED / item['path']) == dict(item, path=str(SEED / item['path']))
        names.add(item['path'])
    assert {str(p.relative_to(SEED)) for p in SEED.rglob('*') if p.is_file()} == names
    spec = importlib.util.spec_from_file_location('genuine_original_generic_source_reader', SEED / 'read-source.py')
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    need, regular, load, family = reader.need, reader.regular, reader.load, reader.family
    family(seed_row)
    own = row(SOURCE / 'index.json')
    need(own['sha256'] == SOURCE_SHA, 'exact freezer source seal')
    family(own)
    refs = load(row(SOURCE / 'references.json'))
    for item in refs['families']:
        family(item['index'])
    for item in refs['files']:
        regular(item)
    build = load(refs['actualBuildReview']['result'])
    contract = load(refs['actualBuildContract'])
    need(build['state'] == 'INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_NATIVE_BUILD_REVIEW_PASSED_V1' and build['verifiedPassed'] is True, 'actual BUILD6e8')
    for key, value in contract['requiredFixedValues'].items():
        need(build[key] == value, 'BUILD fixed '+key)
    for key, value in contract['requiredExactDescriptors'].items():
        need(build['artifacts'][key] == value, 'BUILD descriptor '+key)
    ledger = load(refs['buildInputLedger'])
    need(len(ledger['files']) == 20761, 'complete20761 BUILD ledger')
    for item in ledger['files']:
        regular({key: item[key] for key in ('path', 'sha256', 'bytes')})
    need(len(refs['sdkAliases']) == 31 and refs['sdkAliases'] == build['referenceAliases'], '31 declared aliases')
    for item in refs['sdkAliases']:
        path = Path(item['path'])
        need(path.is_symlink() and os.readlink(path) == item['linkText'] and str(path.resolve(strict=True)) == item['resolvedPath'], 'declared SDK alias')
    for key, count in [('actualStageResult', 566), ('oldResourceStage', 501)]:
        stage = load(refs[key])
        need(len(stage['copies']) == count, 'actual stage count')
        for item in stage['copies']:
            original = item['original']
            regular(original)
            current = regular(dict(original, path=item['path']))
            a, b = current.stat(), Path(original['path']).stat()
            need(stat.S_IMODE(a.st_mode) == stat.S_IMODE(b.st_mode) and (a.st_dev, a.st_ino) != (b.st_dev, b.st_ino), 'stage modes/inodes')
    old = load(refs['oldResourceFreeze'])
    need(len(old['copies']) == 666 and sum(item['original'] is not None for item in old['copies']) == 663, 'old666/663')
    for item in old['copies']:
        regular({key: item[key] for key in ('path', 'sha256', 'bytes')})
        need(stat.S_IMODE(Path(item['path']).stat().st_mode) == 0o600, 'old frozen mode')
        if item['original'] is not None:
            regular(item['original'])
    old_root = Path(refs['oldResourceFreeze']['path']).parent
    old_names = {str(Path(item['path']).relative_to(old_root)) for item in old['copies']} | {'normal-off-freeze-receipt.json'}
    need({str(p.relative_to(old_root)) for p in old_root.rglob('*') if p.is_file()} == old_names, 'old667 membership')
    for item in refs['preparationManifests']:
        for entry in load(item)['files']:
            regular({key: entry[key] for key in ('path', 'sha256', 'bytes')})
    plan = load(row(SOURCE / 'capture-plan.json'))
    need(len(plan['copies']) == plan['baseCopies'] == 712, 'complete base712 plan')
    need(sum(item['source']['bytes'] for item in plan['copies']) == 620065244, 'base bytes')
    targets = set()
    for item in plan['copies']:
        need(item['destination'] not in targets and '..' not in Path(item['destination']).parts and not Path(item['destination']).is_absolute(), 'safe distinct target')
        targets.add(item['destination'])
        regular(item['source'])
    texts = {name: (SOURCE / name).read_text() for name in ('entry.py', 'freeze.py', 'admission.py', 'verify.py', 'copy_io.py', 'monitor.py')}
    trees = {name: ast.parse(text) for name, text in texts.items()}
    functions = {name: {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)} for name, tree in trees.items()}
    entry = texts['entry.py']
    auth = ast.get_source_segment(entry, functions['entry.py']['authorize'])
    need('load_own(' not in auth and 'spec_from_file_location' not in auth, 'stdlib authorization before all custom imports')
    need(auth.index("len(ledger['files'])==20761") < auth.index("frame.update(metadata=metadata"), 'full BUILD intake before Frame return')
    need("for item in ledger['files']:add(frame" in auth and 'finally:' in auth and 'recheck(frame)' in auth, 'complete full and failure protection')
    need("finally:recheck(frame)" in entry, 'all phases finally protect')
    need('sys.modules[__name__]' in entry, 'genuine actual entry module passed')
    for name, tree in trees.items():
        need(not any(isinstance(node, ast.Assign) and any(isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id in {'g', 'model', 'layer', 'monitor', 'io'} for target in node.targets) for node in ast.walk(tree)), 'no imported globals rebound '+name)
    bindings = load(row(SOURCE / 'api-bindings.json'))
    for key in ('acceptedCopyPrimitives', 'monitor'):
        value = bindings[key]
        need(regular(value['donor']).read_bytes() == regular(value['ownCopy']).read_bytes(), 'byte exact donor '+key)
    monitor_fn = functions['monitor.py']['monitor']
    need([item.arg for item in monitor_fn.args.args] == ['argv', 'cwd', 'environment', 'output', 'timeout_seconds', 'authority'], 'genuine six positional monitor')
    parent_monitor = [node for node in ast.walk(functions['entry.py']['main']) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'monitor']
    need(len(parent_monitor) == 1 and len(parent_monitor[0].args) == 6 and not parent_monitor[0].keywords, 'actual parent monitor call')
    admission = texts['admission.py']
    for key, name, arity in [('configuredModel', 'validate_metadata', 7), ('configuredLayer', 'validate_sources', 2), ('configuredLayer', 'validate_classic_compilation', 4)]:
        source_tree = ast.parse(regular(refs[key]).read_text())
        definition = next(node for node in source_tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
        need(len(definition.args.args) == arity, 'genuine API '+name)
        calls = [node for node in ast.walk(trees['admission.py']) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == name]
        need(len(calls) == 1 and len(calls[0].args) == arity, 'caller API '+name)
    need("assert layer.HERE==g.SOURCE/" in admission, 'original configured layer context')
    freeze = texts['freeze.py']
    need(freeze.index("out=write('helper-calls/'") < freeze.index('assert status==0'), 'all available raw output precedes helper success')
    need('error.stdout or b' in freeze and 'capturedStreamsComplete=complete' in freeze, 'honest timeout prefix capture')
    need("'-t','commands','builtin_componentize_embedding'" in freeze and 'ninja_argv' in freeze, 'resolved post-build Ninja capture only')
    need(freeze.index('io.execute_plan(') < freeze.index("receipt_row=write('normal-off-freeze-receipt.json'"), 'receipt last')
    need('os.O_NOFOLLOW' in freeze and 'os.fsync(fd)' in freeze and 's.st_nlink==1' in freeze and 'finally:' in freeze, 'owned root/copy/durable/failure lifetimes')
    verify = texts['verify.py']
    need("self_path=Path(__file__).resolve()" in verify and "expected_source" in verify, 'executing verifier bound to saved exact source index')
    verify_imports = {node.module for node in trees['verify.py'].body if isinstance(node, ast.ImportFrom)}
    need(verify_imports <= {'pathlib'} and 'importlib' not in verify and 'subprocess' not in verify, 'no relocated helper execution')
    need('originalBuildReferencesNotReexecuted=True' in verify, 'frozen-only provenance scope honest')
    metadata = load(refs['metadata'])
    policy = load(refs['policy'])
    database = load(refs['compileCommands'])
    env = dict(Path=Path, shlex=shlex, OWN=SOURCE, SOURCE=Path(refs['configuredSourceRoot']),
               WORK=Path(refs['workRoot']), FREEZE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze'),
               EXTERNAL=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze-external-root'),
               SOURCE_SHA=TASK_SHA, ENGINE_SHA=refs['engine']['sha256'], META_SHA=refs['metadata']['sha256'])
    for name in ('root_model', 'peer_model', 'metadata_model', 'compilation_model'):
        exec(compile(ast.Module(body=[functions['entry.py'][name]], type_ignores=[]), '<independent isolated model>', 'exec'), env)
    cases = []

    def case(name, callback, reject=False):
        failed = False
        try:
            callback()
        except (AssertionError, KeyError, TypeError, ValueError, StopIteration):
            failed = True
        need(failed == reject, name)
        cases.append(dict(name=name, expectedReject=reject, passed=True))

    template = load(row(SOURCE / 'future-root-authority.template.json'))
    case('unissued Root refuses', lambda: env['root_model'](template, own), True)
    synthetic = copy.deepcopy(template)
    synthetic.update(state='ROOT_REVIEWED_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FREEZE_V1', phase='freeze', freezerIndex=own,
                     entry=row(SOURCE / 'entry.py'), freezeAllowed=True, readOnlySourceAdmissionAllowed=True,
                     postBuildNinjaCommandsAllowed=True)
    case('synthetic unissued exact phase shape', lambda: env['root_model'](synthetic, own))
    allowed = {'freezeAllowed', 'readOnlySourceAdmissionAllowed', 'postBuildNinjaCommandsAllowed'}
    for key in allowed:
        case('reject missing intended capability '+key, lambda name=key: env['root_model']({**synthetic, name: False}, own), True)
    for key, value in template.items():
        if value is False and key not in allowed:
            case('reject expanded '+key, lambda name=key: env['root_model']({**synthetic, name: True}, own), True)
    for key in ('actualFreezeResult', 'independentFreezeReview', 'reviewedEnginePins', 'runtimeAuthority'):
        case('reject future result '+key, lambda name=key: env['root_model']({**synthetic, name: {}}, own), True)
    peer = dict(schemaVersion=1, state='INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1', freezerSourceIndexSha256=SOURCE_SHA, taskSelectionSourceIndexSha256=TASK_SHA, sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False, hostActionsInvoked=False, nativeFreezeActionsInvoked=False)
    case('synthetic peer shape', lambda: env['peer_model'](peer, own))
    for key, value in [('sourceOnly', False), ('nativeFreezeActionsInvoked', True), ('freezerSourceIndexSha256', '0'*64), ('taskSelectionSourceIndexSha256', '0'*64)]:
        case('reject peer '+key, lambda name=key, bad=value: env['peer_model']({**peer, name: bad}, own), True)
    case('actual metadata pure model', lambda: env['metadata_model'](metadata, policy, refs))
    for key, value in [('engineSha256', '0'*64), ('gcStress', True), ('entropyPolicy', 'runtime-only'), ('sourceManifest', []), ('selectedModuleManifests', [])]:
        case('reject metadata '+key, lambda name=key, bad=value: env['metadata_model']({**metadata, name: bad}, policy, refs), True)
    case('actual compile DATA model', lambda: env['compilation_model'](database, metadata, policy, refs))
    case('reject missing DB row', lambda: env['compilation_model'](database[:-1], metadata, policy, refs), True)
    wrong = copy.deepcopy(database)
    wrong[0]['command'] = wrong[0]['command'].replace('-DNDEBUG', '-DDEBUG')
    case('reject debug compiler command', lambda: env['compilation_model'](wrong, metadata, policy, refs), True)
    need(not env['FREEZE'].exists() and not env['EXTERNAL'].exists(), 'no actual freeze action yet')
    ast_files = 0
    for path in SOURCE.rglob('*.py'):
        ast.parse(regular(row(path)).read_text())
        ast_files += 1
    snapshots = list(reader.checked.values())
    for item in snapshots:
        need(row(item['path']) == {key: item[key] for key in ('path', 'sha256', 'bytes')}, 'final full-byte rehash')
    family(own)
    save('input-hashes.json', dict(schemaVersion=1, files=[{key: item[key] for key in ('path', 'sha256', 'bytes')} for item in snapshots]))
    save('pure-results.json', dict(schemaVersion=1, cases=cases, scope='isolated new own Root/peer/metadata/compilation predicates; no complete freezer/helper imported'))
    result = dict(schemaVersion=1, state='INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1',
        freezerSourceIndexSha256=SOURCE_SHA, taskSelectionSourceIndexSha256=TASK_SHA, sourceOnly=True, sourceReviewPassed=True,
        ownerActionsInvoked=False, hostActionsInvoked=False, nativeFreezeActionsInvoked=False,
        checks=reader.checks, currentInputFiles=len(snapshots), fullBuildLedgerFiles=20761, basePlannedCopies=712,
        basePlannedBytes=620065244, isolatedPureCases=len(cases), pythonAstFiles=ast_files,
        completeOperationalModulesImported=False, sourceAndOriginalInputsRehashed=True, engineHashedAsData=True,
        engineExecuted=False, actualFreeze=None, operationalAdmission=False, runtimeAcceptanceClaim=False)
    save('results.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
