"""Pure data and owned tiny-text fixtures; no artifact-tool main/native/guest run."""
import sys
sys.dont_write_bytecode = True
import ast
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from artifact_common import (HERE, REPO, RECIPE, classify, compile_command, manifest,
                             embedding_command, destination, validate_plan, execute_plan, sha, digest, capture_regular)

results = []
def check(name, operation):
    operation()
    results.append({'name': name, 'passed': True})
def rejects(operation):
    try:
        operation()
    except (AssertionError, FileExistsError, FileNotFoundError, ValueError):
        return
    raise AssertionError('Malformed input accepted')
def equal(left, right):
    assert left == right

def main():
    output = Path(os.environ.get('NODE_COMPAT_ARTIFACT_TEST_OUTPUT', str(HERE / 'python-test-results.json')))
    assert not output.exists()
    for label, gc, entropy in [('normal-off', False, 'off'), ('normal-runtime', False, 'runtime-only'), ('gc-off', True, 'off')]:
        metadata = {'buildRecipeSha256': RECIPE, 'gcStress': gc, 'entropyPolicy': entropy}
        check('pure-label-coherence-' + label, lambda m=metadata, l=label: equal(classify(m, l), (m['gcStress'], m['entropyPolicy'])))
    baseline = {'buildRecipeSha256': RECIPE, 'gcStress': False, 'entropyPolicy': 'off'}
    for name, change in [('old-recipe', {'buildRecipeSha256': '0'*64}), ('diagnostic', {'diagnosticOnly': True}),
                         ('null-diagnostic', {'diagnosticOnly': None}), ('diagnostic-policy', {'internalTickDiagnosticPolicy': {}}),
                         ('synthetic', {'syntheticMetadataOnly': True}), ('wrong-gc', {'gcStress': True}),
                         ('runtime-in-off-label', {'entropyPolicy': 'runtime-only'})]:
        check(name + '-rejected', lambda c=change: rejects(lambda: classify({**baseline, **c}, 'normal-off')))
    check('runtime-gc-label-rejected', lambda: rejects(lambda: classify(baseline, 'gc-runtime')))
    actual_old = [Path('/tmp/starling-node-compat/foundations-v11/native-freeze/off-foundations.engine.wasm.build.json'),
                  Path('/tmp/starling-node-compat/foundation-scheduler-link1-v1/native-freeze/diagnostic-release.engine.wasm.build.json')]
    old_rows = []
    for path in actual_old:
        data = json.loads(path.read_bytes())
        check('actual-old-receipt-before-engine-' + path.parent.parent.name, lambda m=data: rejects(lambda: classify(m, 'normal-off')))
        old_rows.append({'path': str(path), 'sha256': sha(path), 'engineBytesRead': False})

    command = 'clang++ -O3 -DNDEBUG -DNODE_COMPAT_INTERNAL_TICKS=1 -DNODE_COMPAT_STRICT_INITIALIZATION=1 -DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1 -DNODE_COMPAT_ENTROPY_POLICY=1 -c /fixture/engine.cpp -o out.o'
    check('pure-compile-off', lambda: compile_command(command, False))
    check('pure-compile-runtime', lambda: compile_command(command + ' -DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1', True))
    for name, value, runtime in [('missing-ticks', command.replace(' -DNODE_COMPAT_INTERNAL_TICKS=1', ''), False),
                                 ('conflicting-ticks', command + ' -DNODE_COMPAT_INTERNAL_TICKS=0', False),
                                 ('duplicate-strict', command + ' -DNODE_COMPAT_STRICT_INITIALIZATION=1', False),
                                 ('runtime-on-off', command + ' -DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1', False),
                                 ('runtime-zero', command + ' -DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=0', True),
                                 ('syntax-only', command + ' -fsyntax-only', False),
                                 ('debug', command + ' -DDEBUG=1', False),
                                 ('missing-o3', command.replace(' -O3', ''), False)]:
        check('compile-' + name + '-rejected', lambda v=value, r=runtime: rejects(lambda: compile_command(v, r)))
    raw = b'ninja: Entering directory /fixture\nclang++ -O3 -c /fixture/embedding.cpp -o x.o\n'
    check('separate-parent-compile-selection', lambda: equal(embedding_command(raw, '/fixture/embedding.cpp'), ['clang++ -O3 -c /fixture/embedding.cpp -o x.o']))
    check('duplicate-parent-rejected', lambda: rejects(lambda: embedding_command(raw+raw, '/fixture/embedding.cpp')))
    check('missing-parent-rejected', lambda: rejects(lambda: embedding_command(raw, '/fixture/other.cpp')))
    check('canonical-manifest', lambda: manifest([{'path': 'runtime/test.cpp', 'sha256': '1'*64}], 1))
    for name in ('../escape.cpp', '/absolute.cpp', 'runtime/./test.cpp', 'runtime//test.cpp', 'runtime/../test.cpp', 'runtime\\test.cpp', 'runtime/\0test.cpp'):
        check('manifest-path-' + repr(name), lambda n=name: rejects(lambda: manifest([{'path': n, 'sha256': '1'*64}], 1)))
    check('duplicate-manifest-rejected', lambda: rejects(lambda: manifest([{'path':'x', 'sha256':'1'*64}]*2, 2)))

    with tempfile.TemporaryDirectory(prefix='production-artifacts-host-text-') as temporary:
        root = Path(temporary)
        source = root / 'owned-input.txt'
        source.write_text('owned plain text fixture\n')
        check('regular-capture-digest-bound-to-bytes', lambda: equal(capture_regular(source), (source.read_bytes(), sha(source))))
        alias = root / 'source-alias.txt'
        alias.symlink_to(source)
        check('receipt-symlink-capture-rejected', lambda: rejects(lambda: capture_regular(alias)))
        base = root / 'native-freeze'
        target = base / 'label.txt'
        receipt = base / 'receipt.json'
        row = {'original': source, 'target': target, 'sha256': sha(source), 'shared': False}
        check('invalid-second-target-before-first-copy', lambda: rejects(lambda: validate_plan([row, {**row, 'target': root/'escape.txt'}], receipt, base)))
        check('invalid-plan-created-no-output', lambda: equal(base.exists(), False))
        check('receipt-target-collision-rejected', lambda: rejects(lambda: validate_plan([row], target, base)))
        check('canonical-destination-rejected', lambda: rejects(lambda: destination(base/'sub/../label.txt', base)))
        check('complete-plan-validation', lambda: validate_plan([row], receipt, base))
        check('exclusive-copy-owned-text-only', lambda: execute_plan([row], base))
        check('copied-text-equal', lambda: equal(target.read_bytes(), source.read_bytes()))
        check('variant-overwrite-rejected', lambda: rejects(lambda: validate_plan([row], receipt, base)))
        shared = {**row, 'shared': True}
        check('shared-identical-only', lambda: validate_plan([shared], receipt, base))
        check('shared-wrong-hash-rejected', lambda: rejects(lambda: validate_plan([{**shared, 'sha256': '2'*64}], receipt, base)))
        link = base / 'link'
        link.symlink_to(root, target_is_directory=True)
        check('symlink-ancestor-rejected', lambda: rejects(lambda: destination(link/'output.txt', base)))
        check('duplicate-target-rejected', lambda: rejects(lambda: validate_plan([shared, shared], receipt, base)))
        generated = {'original': None, 'data': b'captured text only\n', 'target': base/'after.txt', 'sha256': digest(b'captured text only\n'), 'shared': False}
        check('generated-capture-plan', lambda: validate_plan([generated], receipt, base))
        check('generated-capture-exclusive-copy', lambda: execute_plan([generated], base))
        check('generated-capture-digest', lambda: equal(sha(base/'after.txt'), generated['sha256']))
        source.write_text('changed owned text\n')
        check('source-mutation-rejected', lambda: rejects(lambda: validate_plan([shared], receipt, base)))
        check('existing-copied-text-preserved', lambda: equal(target.read_text(), 'owned plain text fixture\n'))

    original_path = HERE.parent/'production-adoption-v1/build-one-diagnostic-v4.py'
    original = original_path.read_text()
    launcher = (HERE/'build-one.py').read_text()
    old_tree, new_tree = ast.parse(original), ast.parse(launcher)
    helpers = [row for row in old_tree.body if isinstance(row, (ast.FunctionDef, ast.ClassDef)) and row.name != 'main']
    equal(len(helpers), 8)
    for row in helpers:
        replacement = next(item for item in new_tree.body if isinstance(item, type(row)) and item.name == row.name)
        check('lifecycle-byte-identity-' + row.name, lambda a=row, b=replacement: equal(ast.get_source_segment(original, a), ast.get_source_segment(launcher, b)))
    for path in HERE.glob('*.py'):
        check('python-ast-' + path.name, lambda p=path: ast.parse(p.read_text()))
    report = {'state': 'PURE_DATA_AND_OWNED_TEXT_HOST_TESTS_PASSED', 'tests': len(results), 'passed': len(results), 'failures': 0,
              'results': results, 'oldReceiptControls': old_rows, 'launcherHelpersByteIdentical': 8,
              'launcherMainExecuted': False, 'freezerMainExecuted': False, 'exporterMainExecuted': False,
              'actualProductionFreezeValidated': False, 'nativeOrGuestExecuted': False,
              'syntheticClassificationIsNotArtifactProof': True}
    with output.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'tests': len(results), 'passed': len(results), 'output': str(output), 'nativeOrGuestExecuted': False}))

if __name__ == '__main__':
    main()
