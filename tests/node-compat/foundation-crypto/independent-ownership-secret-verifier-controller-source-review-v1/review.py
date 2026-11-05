"""Independent source/data/pure audit. Never import controller/helper/monitor."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import stat
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
SOURCE = BASE / 'ownership-secret-verifier-controller-candidate-v1'
SOURCE_SHA = '0fc0082da7d9842bf9bd9e46a28760e2cea5f698eec62880f0150c572d94a78f'
SEED = BASE / 'independent-ownership-secret-integration-source-review-v1'
SEED_SHA = '8665997e4edab561a0e0e63235104b8e358072995725002704f25e4499dfca45'


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    # Authenticate every byte of the existing generic reader before importing it
    # in its genuine original context. Its main and candidate-specific APIs stay unused.
    seed_index = row(SEED / 'index.json')
    assert seed_index['sha256'] == SEED_SHA
    index = json.loads((SEED / 'index.json').read_bytes())
    names = {'index.json'}
    for item in index['files']:
        assert not Path(item['path']).is_absolute() and '..' not in Path(item['path']).parts
        assert row(SEED / item['path']) == dict(item, path=str(SEED / item['path']))
        names.add(item['path'])
    assert {str(p.relative_to(SEED)) for p in SEED.rglob('*') if p.is_file()} == names
    spec = importlib.util.spec_from_file_location('original_generic_secret_source_reader', SEED / 'read-source.py')
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    need, load, regular, family = reader.need, reader.load, reader.regular, reader.family
    family(seed_index)
    source_index = row(SOURCE / 'index.json')
    need(source_index['sha256'] == SOURCE_SHA, 'exact new controller source')
    family(source_index)
    refs = load(row(SOURCE / 'references.json'))
    for item in refs['families']:
        family(item['index'])
    inputs = load(row(SOURCE / 'source-inputs.json'))
    for item in inputs['files']:
        regular(item)
    need(inputs['artifactInputLedger'] == refs['artifactInputLedger'], 'full artifact ledger identity')
    ledger = load(refs['artifactInputLedger'])
    for item in ledger['files']:
        regular(item)
    need(len(ledger['files']) == 26247, 'entire actual frozen-artifact input ledger')
    normal = load(refs['normalProtection'])
    need(normal['originalReferenceEntries'] == len(normal['originals']) == 1387, 'normal originals')
    regular(normal['freezeReceipt'])
    for item in normal['frozenCopyEntries']:
        regular({key: item[key] for key in ('path', 'sha256', 'bytes')})
    for item in normal['originals']:
        regular(item['original'])
        regular(item['frozen'])
    normal_root = Path(normal['freezeReceipt']['path']).parent
    normal_names = set(normal['requiredNormalFreezeMembership'])
    need(len(normal_names) == 1391, 'normal membership1391')
    need({str(p.relative_to(normal_root)) for p in normal_root.rglob('*') if p.is_file()} == normal_names, 'normal exact tree')
    receipt = load(refs['freezeReceipt'])
    need(len(receipt['copies']) == 1902 and sum(item['original'] is not None for item in receipt['copies']) == 1899, 'new frozen counts')
    frozen_root = Path(refs['frozenRoot'])
    frozen_names = {'normal-off-freeze-receipt.json'}
    for item in receipt['copies']:
        regular({key: item[key] for key in ('path', 'sha256', 'bytes')})
        need(stat.S_IMODE(Path(item['path']).stat().st_mode) == 0o600, 'private frozen copy')
        frozen_names.add(str(Path(item['path']).relative_to(frozen_root)))
        if item['original'] is not None:
            regular(dict(path=item['original'], sha256=item['sha256'], bytes=item['bytes']))
    need({str(p.relative_to(frozen_root)) for p in frozen_root.rglob('*') if p.is_file()} == frozen_names, 'new exact1903 tree')
    for path in frozen_root.rglob('*'):
        need(not path.is_symlink(), 'frozen no links')
        if path.is_dir():
            need(stat.S_IMODE(path.stat().st_mode) == 0o700, 'private frozen directory')
    text = regular(row(SOURCE / 'controller.py')).read_text()
    tree = ast.parse(text)
    definitions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    imported = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            imported.update(item.name for item in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module)
    need(imported <= {'pathlib', 'hashlib', 'importlib.util', 'json', 'os', 'stat', 'sys'}, 'stdlib bootstrap only')
    need(not any(isinstance(node, ast.Assign) and any(isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id in {'helper', 'monitor', 'module'} for target in node.targets) for node in ast.walk(tree)), 'no imported globals rebound')
    need("frame=authorize(json.loads(sys.argv[2]))" in ast.get_source_segment(text, definitions['main']), 'full authorization before role dispatch')
    need("finally:frame['capture'].recheck()" in text, 'both roles final protection')
    authorize = ast.get_source_segment(text, definitions['authorize'])
    need('load_actual(' not in authorize, 'no custom import before full source/proof/protection authentication')
    need("for r in ledger['files']:capture.file(r)" in authorize and 'capture.recheck()' in authorize, 'complete DATA ledger before custom import')
    worker = ast.get_source_segment(text, definitions['worker'])
    need(worker.index('frame[\'capture\'].recheck()') < worker.index('helper.verify_frozen(') < worker.index("write(OUT/'whole-frame.json',value)") < worker.index('print(json.dumps(value),flush=True)'), 'full frame retention ordering')
    need('assert helper.HERE==VERIFIER' in worker and "str(helper.FROZEN)==frame['contract']['frozenRoot']" in worker, 'actual original helper context')
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'helper' and node.func.attr == 'verify_frozen']
    need(len(calls) == 1, 'one complete verifier call, dormant')
    parent = ast.get_source_segment(text, definitions['parent'])
    monitor_calls = [node for node in ast.walk(definitions['parent']) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'monitor']
    need(len(monitor_calls) == 1 and len(monitor_calls[0].args) == 6 and not monitor_calls[0].keywords, 'real monitor six positional arguments')
    monitor_tree = ast.parse(regular(refs['monitorEntry']).read_text())
    monitor_function = next(node for node in monitor_tree.body if isinstance(node, ast.FunctionDef) and node.name == 'monitor')
    need([arg.arg for arg in monitor_function.args.args] == ['argv', 'cwd', 'environment', 'output', 'timeout_seconds', 'authority'], 'original monitor API')
    need("frame['capture'].read(terminal_row)==terminal" in parent, 'durable raw terminal equals returned object')
    need(parent.index("write(OUT/'raw-terminal-observed.json'") < parent.index('clean_terminal('), 'raw retention precedes interpretation')
    need('validate_retained_frame(value,retained,c,metadata,manifests)' in parent and 'finally:' in parent, 'whole-frame model and failure protection')
    need('stream.flush();os.fsync(stream.fileno())' in text, 'complete saved frame durable before stdout')
    c = load(refs['verifierContract'])
    metadata = load(c['metadata'])
    copies = {item['path']: item for item in receipt['copies']}
    manifests = []
    for item in metadata['selectedModuleManifests']:
        selected = copies[str(Path(c['frozenSourceRoot']) / item['path'])]
        manifests.append(load({key: selected[key] for key in ('path', 'sha256', 'bytes')}))
    need(len(manifests) == 11 and len(metadata['sourceManifest']) == 355, 'whole real11-manifest355 frame')
    env = dict(Path=Path, OWN=SOURCE, VERIFIER=Path(refs['verifierEntry']['path']).parent,
               OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-frozen-verifier-v1'),
               EXTERNAL=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-frozen-verifier-v1-external-root'),
               TIMEOUT=600, VERIFIER_SHA=refs['verifierSourceIndex']['sha256'])
    for name in ('validate_root', 'validate_peer', 'expected_frame', 'clean_terminal', 'validate_retained_frame'):
        exec(compile(ast.Module(body=[definitions[name]], type_ignores=[]), '<independent isolated predicate>', 'exec'), env)
    cases = []

    def case(name, callback, reject=False):
        failed = False
        try:
            callback()
        except (AssertionError, KeyError, TypeError, ValueError):
            failed = True
        need(failed == reject, name)
        cases.append(dict(name=name, passed=True, expectedReject=reject))

    root = load(row(SOURCE / 'future-root-authority.template.json'))
    case('unissued authority refuses', lambda: env['validate_root'](root, source_index, refs), True)
    synthetic = copy.deepcopy(root)
    synthetic.update(state='ROOT_REVIEWED_SECRET_OWNER355_FROZEN_VERIFIER_READ_ONLY_V1', verifierReadOnlyAllowed=True,
                     controllerIndex=source_index, controllerEntry=row(SOURCE / 'controller.py'))
    case('synthetic unissued shape', lambda: env['validate_root'](synthetic, source_index, refs))
    false_fields = [name for name, value in root.items() if value is False and name != 'verifierReadOnlyAllowed']
    case('reject missing verifier permission', lambda: env['validate_root']({**synthetic, 'verifierReadOnlyAllowed': False}, source_index, refs), True)
    null_fields = ['actualVerifierResult', 'independentActualVerifierReview', 'actualExport', 'reviewedPins', 'actualBootstrap', 'runtimeAuthority']
    for name in false_fields:
        case('reject expanded '+name, lambda key=name: env['validate_root']({**synthetic, key: True}, source_index, refs), True)
    for name in null_fields:
        case('reject future result '+name, lambda key=name: env['validate_root']({**synthetic, key: {}}, source_index, refs), True)
    for name, value in [('phase', 'export'), ('variant', 'gc-off'), ('expectedVerifierCalls', 2), ('externalParentDeadlineSeconds', 601), ('outputRoot', '/wrong')]:
        case('reject wrong '+name, lambda key=name, bad=value: env['validate_root']({**synthetic, key: bad}, source_index, refs), True)
    peer = dict(schemaVersion=1, state='INDEPENDENT_CRYPTO_OWNER355_SECRET_VERIFIER_CONTROLLER_SOURCE_REVIEW_PASSED_V1', controllerSourceIndexSha256=SOURCE_SHA, verifierSourceIndexSha256=refs['verifierSourceIndex']['sha256'], sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False, hostActionsInvoked=False, verifierActionsInvoked=False)
    case('synthetic independent peer', lambda: env['validate_peer'](peer, source_index))
    for name, value in [('sourceOnly', False), ('sourceReviewPassed', False), ('hostActionsInvoked', True), ('verifierActionsInvoked', True), ('controllerSourceIndexSha256', '0'*64)]:
        case('reject wrong peer '+name, lambda key=name, bad=value: env['validate_peer']({**peer, key: bad}, source_index), True)
    modeled = env['expected_frame'](c, metadata, manifests)
    helper_tree = ast.parse(regular(refs['verifierEntry']).read_text())
    helper_function = next(node for node in helper_tree.body if isinstance(node, ast.FunctionDef) and node.name == 'verify_frozen')
    return_expr = next(node.value for node in helper_function.body if isinstance(node, ast.Return))
    need(all(isinstance(node.func, ast.Name) and node.func.id in {'dict', 'str'} for node in ast.walk(return_expr) if isinstance(node, ast.Call)), 'isolated helper return contains no complete helper calls')
    helper_env = dict(c=c, metadata=metadata, values=manifests, selected=metadata['selectedModuleManifests'], CONFIGURED=c['configuredSourceRoot'], FROZEN=Path(c['frozenRoot']), WORK=c['workRoot'], HERE=env['VERIFIER'], data=modeled['commands'])
    helper_expression_value = eval(compile(ast.Expression(return_expr), '<isolated helper return expression only>', 'eval'), helper_env)
    need(helper_expression_value == modeled, 'whole real metadata/manifests/original-context helper return expression matches model')
    before = copy.deepcopy(metadata)
    case('whole frame and saved value', lambda: env['validate_retained_frame'](modeled, copy.deepcopy(modeled), c, metadata, manifests))
    for name in modeled:
        case('reject whole frame mutation '+name, lambda key=name: env['validate_retained_frame']({**modeled, key: 'changed'}, {**modeled, key: 'changed'}, c, metadata, manifests), True)
    case('reject saved/stdout mismatch', lambda: env['validate_retained_frame'](modeled, {}, c, metadata, manifests), True)
    need(metadata == before, 'metadata untouched')
    terminal = dict(rawExitCode=0, authority={'synthetic': True}, parentOwnedGroupGone=True, allObservedOwnedGroupsGone=True, timeout=False, forcedCleanup=False, errors=[], signals=[], interruptedSignals=[], remainingObservedPids=[], finalGroups=[dict(alive=False)], stderr=dict(bytes=0))
    case('synthetic clean terminal', lambda: env['clean_terminal'](terminal, terminal['authority']))
    for name, value in [('rawExitCode', 1), ('rawExitCode', False), ('timeout', True), ('forcedCleanup', True), ('signals', [9]), ('remainingObservedPids', [1]), ('finalGroups', []), ('stderr', {'bytes': 1})]:
        case('reject terminal '+name+repr(value), lambda key=name, bad=value: env['clean_terminal']({**terminal, key: bad}, terminal['authority']), True)
    need(not env['OUT'].exists() and not env['EXTERNAL'].exists(), 'no actual verifier phase output exists')
    need(not (BASE / 'ownership-secret-pin-tooling-candidate-v1/action.py').exists(), 'exporter still absent')
    for name in ('controller.py', 'prepare-data.py', 'check-source.py', 'seal-source.py'):
        ast.parse(regular(row(SOURCE / name)).read_text())
    # Final independent full-byte rehash; never clear/rebind the seed cache.
    rows = list(reader.checked.values())
    for item in rows:
        actual = row(item['path'])
        need(actual == {key: item[key] for key in ('path', 'sha256', 'bytes')}, 'final current bytes')
        state = Path(item['path']).stat()
        need((state.st_dev, state.st_ino, state.st_size, state.st_mtime_ns, state.st_ctime_ns) == item['identity'], 'final stable identity')
    family(source_index)
    need({str(p.relative_to(normal_root)) for p in normal_root.rglob('*') if p.is_file()} == normal_names, 'final normal membership')
    need({str(p.relative_to(frozen_root)) for p in frozen_root.rglob('*') if p.is_file()} == frozen_names, 'final new membership')
    save('input-hashes.json', dict(schemaVersion=1, files=[{key: item[key] for key in ('path', 'sha256', 'bytes')} for item in rows]))
    save('pure-results.json', dict(schemaVersion=1, cases=cases, sourceOnly=True, completeHelperOrControllerImported=False, originalHelperReturnExpressionOnly=True))
    result = dict(schemaVersion=1, state='INDEPENDENT_CRYPTO_OWNER355_SECRET_VERIFIER_CONTROLLER_SOURCE_REVIEW_PASSED_V1', controllerSourceIndexSha256=SOURCE_SHA, verifierSourceIndexSha256=refs['verifierSourceIndex']['sha256'], sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False, hostActionsInvoked=False, verifierActionsInvoked=False, completeControllerOrHelperOrMonitorImported=False, checks=reader.checks, inputFiles=len(rows), isolatedPureCases=len(cases), pythonAstFiles=4, wholeActualMetadataAndElevenManifestReturnExpressionMatches=True, actualControllerResult=None, actualVerifierResult=None, exportPinBootstrapImplemented=False, engineExecuted=False, runtimeAcceptanceClaim=False, grantsActionAuthority=False)
    save('results.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
