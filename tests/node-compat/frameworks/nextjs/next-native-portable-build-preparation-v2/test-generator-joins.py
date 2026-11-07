"""Read completed real receipt and exercise DATA-only admission mutations."""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile

HERE = Path(__file__).absolute().parent
REPO = HERE.parents[4]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--result', required=True, type=Path)
args = parser.parse_args()
spec = importlib.util.spec_from_file_location('portable_v2_actual_receipt_test', HERE / 'portable.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def ref(path):
    b = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


result_ref = ref(args.result)
assert result_ref['sha256'] == 'f9e63c0455fb292e1c04ce2315f7680f58be3030c4df523c5b850eebee151b86'
assert result_ref['bytes'] == 970943
generated = m.document(result_ref)
root = m.document(generated['rootAuthority'])
selection_ref = root['portableSelection']
policy = json.loads((HERE / 'plan.json').read_text())['portableSourcePolicy']
selection = m.admit(selection_ref, policy, REPO)
# This is the unmodified completed receipt, including every ten-command and
# outer raw receipt. The new role gate and all previous deep gates must pass.
proof_refs = m.validate_generators(generated, selection, generated['node'], policy, selection_ref)
assert len(proof_refs) > 40
negative_labels = []
with tempfile.TemporaryDirectory(prefix='portable-v2-generator-join-data-', dir='/private/tmp') as temp:
    temp = Path(temp)

    def changed_root(label, update):
        document = copy.deepcopy(root)
        update(document)
        path = temp / (label + '.json')
        path.write_text(json.dumps(document, indent=2) + '\n')
        value = copy.deepcopy(generated)
        value['rootAuthority'] = ref(path)
        return value

    def reject(label, value, selected_ref=selection_ref):
        try:
            m.validate_generators(value, selection, generated['node'], policy, selected_ref)
        except (ValueError, KeyError, TypeError, OSError):
            negative_labels.append(label)
        else:
            raise AssertionError('Mutation admitted: ' + label)

    reject('unrelated-root-json', changed_root('unrelated-root', lambda d: d.clear()))
    reject('wrong-root-state', changed_root('wrong-state', lambda d: d.update(state='ROOT_NATIVE_BUILD_ALLOWED')))
    reject('wrong-root-source-index', changed_root('wrong-index', lambda d: d.update(sourceIndex=generated['plan'])))
    reject('wrong-root-plan', changed_root('wrong-plan', lambda d: d.update(plan=generated['sourceIndex'])))
    reject('wrong-root-selection', changed_root('wrong-selection', lambda d: d.update(portableSelection=generated['plan'])))
    for name in ['generatorChecksAllowed', 'nodeHostSourceOnly']:
        reject(name + '-false', changed_root(name, lambda d, n=name: d.update({n: False})))
    for name in ['nativeBuildAllowed', 'compilerAllowed', 'cmakeAllowed', 'cargoAllowed',
                 'engineAllowed', 'guestAllowed', 'networkAllowed', 'copySourceAllowed']:
        reject(name + '-true', changed_root(name, lambda d, n=name: d.update({n: True})))
    reject('unissued-root', changed_root('unissued', lambda d: d.update(unissued=True)))
    for name in ['argv', 'environment', 'outputRoot', 'monitorOutputRoot']:
        reject('root-override-' + name, changed_root('override-' + name, lambda d, n=name: d.update({n: None})))
    unrelated_plan = temp / 'unrelated-plan.json'
    unrelated_plan.write_text(json.dumps(m.document(generated['plan']), indent=2) + '\n')
    value = copy.deepcopy(generated)
    value['plan'] = ref(unrelated_plan)
    reject('same-plan-content-not-indexed-member', value)
    value = copy.deepcopy(generated)
    value['node']['sha256'] = '0' * 64
    reject('wrong-receipt-node', value)
    value = copy.deepcopy(generated)
    value['commands'][0]['argv'].append('--unapproved')
    reject('changed-generator-argv', value)
    value = copy.deepcopy(generated)
    value['composition'] = generated['plan']
    reject('changed-receipt-composition', value)
    # Equal bytes at a new path do not retarget the existing Root grant.
    selection_copy = temp / 'identical-selection.json'
    selection_copy.write_bytes(Path(selection_ref['path']).read_bytes())
    reject('equal-selection-bytes-different-path', generated, ref(selection_copy))
    # An explicit Source-only draft can select the exact existing descriptor,
    # rather than silently changing the proof's selected file path.
    output = temp / 'unissued-v2-preparation'
    prepared = subprocess.run([sys.executable, '-B', '-I', str(HERE / 'prepare.py'),
        '--selection', selection_ref['path'], '--output', str(output)], capture_output=True)
    assert prepared.returncode == 0, prepared.stderr.decode()
    draft = json.loads((output / 'root-authority.unissued.json').read_text())
    assert draft['portableSelection'] == selection_ref
    assert not (output / 'portable-selection.json').exists()
    assert draft['buildAllowed'] is draft['configureAllowed'] is draft['installedGeneratorResult'] is None

assert ref(args.result) == result_ref
assert m.document(generated['rootAuthority']) == root
print(json.dumps(dict(state='PORTABLE_V2_ACTUAL_GENERATOR_PROOF_DATA_TESTS_PASSED_V1',
    actualReceipt=result_ref, actualReceiptDeepGatePassed=True, proofReferencesChecked=len(proof_refs),
    dataMutationsRefused=len(negative_labels), mutationLabels=negative_labels,
    exactOriginalSelection=selection_ref, originalReceiptAndRootUnchanged=True,
    explicitUnissuedDraftRetainsOriginalSelection=True,
    generatorOrBuildOrRuntimeRerun=False, scratchContainsOnlySmallJson=True)))
