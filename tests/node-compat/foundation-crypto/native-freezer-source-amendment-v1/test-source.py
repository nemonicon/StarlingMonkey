"""Pure source/data fixtures only. Does not import an artifact helper/action."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import os
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pure_freezer_guard', HERE / 'freezer-guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)  # Own stdlib-only data functions; no authorize call.
checks = []


def check(name, fn):
    fn()
    checks.append({'name': name, 'passed': True})


def equal(a, b):
    assert a == b


def refuses(fn):
    try:
        fn()
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError('Expected refusal')


donor = Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/native-integration-candidate-v2')
actual_state = re.findall(r"return\{state:'([^']+)'", (donor / 'artifact-tools/metadata-admission.mjs').read_text())
check('Actual saved selector source has one finite result state', lambda: equal(actual_state, [guard.ADMISSION_STATE]))
admission = {'state': actual_state[0], 'sourceFiles': 355, 'engineBytesRead': False}
check('Exact actual source result state accepted as DATA', lambda: guard.validate_admission(admission))
for name, key, value in [('old consumers state', 'state', 'ACTUAL_FINITE_CONSUMERS_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'), ('unknown state', 'state', 'UNKNOWN'), ('old source count', 'sourceFiles', 350), ('engine-read claim', 'engineBytesRead', True)]:
    value_data = dict(admission, **{key: value})
    check('Refuse ' + name, lambda v=value_data: refuses(lambda: guard.validate_admission(v)))

own_sha = 'a' * 64
peer = {'schemaVersion': 1, 'state': guard.PEER_STATE, 'sourceIndexSha256': own_sha, 'sourceOnly': True, 'sourceReviewPassed': True, 'ownerActionsInvoked': False}
authority = {'schemaVersion': 1, 'state': 'ROOT_REVIEWED_CRYPTO_OWNER355_FREEZER_CORRECTION_V1', 'amendmentSourceIndexSha256': own_sha, 'donorSourceIndexSha256': guard.DONOR_SHA, 'configuredSourceRoot': str(guard.CONFIGURED), 'stagedArtifactToolsRoot': str(guard.STAGED / 'artifact-tools'), 'freezeRoot': str(guard.FROZEN), 'freezeAllowed': True, 'engineExecutionAllowed': False, 'operationalAdmission': False, 'runtimeAcceptanceClaim': False, 'label': 'normal-off'}
for label in ('normal-off', 'normal-runtime', 'gc-off', 'disabled-off'):
    check('Finite authority data label ' + label, lambda label=label: equal(guard.validate_authority_data(dict(authority, label=label), own_sha, peer), label))
for key, value in [('state', 'UNISSUED'), ('amendmentSourceIndexSha256', 'b' * 64), ('donorSourceIndexSha256', 'b' * 64), ('configuredSourceRoot', str(guard.FROZEN / 'source')), ('stagedArtifactToolsRoot', '/unrecognized/tools'), ('freezeRoot', '/unrecognized/freeze'), ('freezeAllowed', False), ('engineExecutionAllowed', True), ('operationalAdmission', True), ('runtimeAcceptanceClaim', True), ('label', 'runtime-gc')]:
    altered = dict(authority, **{key: value})
    check('Refuse wrong authority ' + key, lambda altered=altered: refuses(lambda: guard.validate_authority_data(altered, own_sha, peer)))
for key, value in [('state', 'HOLD'), ('sourceIndexSha256', 'b' * 64), ('sourceOnly', False), ('sourceReviewPassed', False), ('ownerActionsInvoked', True)]:
    altered = dict(peer, **{key: value})
    check('Refuse wrong peer ' + key, lambda altered=altered: refuses(lambda: guard.validate_authority_data(authority, own_sha, altered)))

active_sha = hashlib.sha256((HERE / 'freeze-engine.py').read_bytes()).hexdigest()
donor_sha = hashlib.sha256((donor / 'artifact-tools/freeze-engine.py').read_bytes()).hexdigest()
active_path = str(guard.FROZEN / 'artifact-tools/freeze-engine.py')
donor_path = str(guard.FROZEN / 'artifact-tools/donor-data/freeze-engine.py')
receipt = {'helperSha256': active_sha, 'activeFreezerTooling': {'role': 'ACTUAL_ACTIVE_CORRECTED_FREEZER', 'path': active_path, 'sha256': active_sha}, 'donorFreezerTooling': {'role': 'IMMUTABLE_STAGED_DONOR_DATA_NOT_ACTIVE', 'path': donor_path, 'sha256': donor_sha}, 'copies': [{'path': active_path, 'sha256': active_sha}, {'path': donor_path, 'sha256': donor_sha}]}
check('Saved correction role proof distinguishes actual active and staged DATA bytes', lambda: guard.validate_receipt_roles(receipt, active_sha, donor_sha))
for label, change in [('helper self hash', lambda r: r.update(helperSha256=donor_sha)), ('old bytes as active', lambda r: r['copies'][0].update(sha256=donor_sha)), ('missing donor', lambda r: r['copies'].pop()), ('untyped donor', lambda r: r['donorFreezerTooling'].update(role='ACTIVE')), ('same active and donor path', lambda r: r['donorFreezerTooling'].update(path=active_path))]:
    altered = copy.deepcopy(receipt)
    change(altered)
    check('Refuse incorrect correction proof ' + label, lambda altered=altered: refuses(lambda: guard.validate_receipt_roles(altered, active_sha, donor_sha)))

derivation = json.loads((HERE / 'derivations.json').read_text())
before = Path(derivation['donorPath']).read_text()
after = before
for edit in derivation['edits']:
    assert after.count(edit['before']) == 1
    after = after.replace(edit['before'], edit['after'])
check('Exact seven-edit afterimage reconstruction', lambda: equal(after, (HERE / 'freeze-engine.py').read_text()))
for edit in reversed(derivation['edits']):
    assert after.count(edit['after']) == 1
    after = after.replace(edit['after'], edit['before'])
check('Exact reverse to immutable donor', lambda: equal(after, before))
source = (HERE / 'freeze-engine.py').read_text()
check('Root/source guard precedes genuine staged helper import', lambda: equal(source.index('guard.authorize(') < source.index('_common_spec.loader.exec_module(common)'), True))
check('Genuine staged context assertions precede main', lambda: equal(source.index('assert common.HERE') < source.index('def main():'), True))
check('Explicit donor DATA target and active actual file are both captured', lambda: equal("add(ENTRY, 'artifact-tools/freeze-engine.py'" in source and "artifact-tools/donor-data/freeze-engine.py" in source, True))
check('No staged helper or native file write/patch action', lambda: equal('write_text(' not in source and 'write_bytes(' not in source and 'subprocess.run' in source, True))
for name in ('../escape', '/absolute', 'a//b', 'a/./b', 'a\\b', 'nul\0name', ''):
    check('Refuse non-finite source path ' + repr(name), lambda name=name: refuses(lambda: guard.safe(name)))
with tempfile.TemporaryDirectory(prefix='crypto-freezer-source-only-') as temporary:
    tiny = Path(temporary).resolve() / 'tiny.txt'
    tiny.write_bytes(b'bounded source fixture\n')
    row = guard.regular(tiny)
    check('Own tiny source descriptor exact hash/size', lambda: equal(guard.descriptor(row), row))
    check('Wrong own tiny source digest rejected', lambda: refuses(lambda: guard.regular(tiny, '0' * 64)))
    check('Wrong own tiny source size rejected', lambda: refuses(lambda: guard.regular(tiny, row['sha256'], row['bytes'] + 1)))
    link = tiny.parent / 'symlink.txt'
    link.symlink_to(tiny)
    check('Symlink source rejected before helper import', lambda: refuses(lambda: guard.regular(link)))
    link.unlink()
    hard = tiny.parent / 'hardlink.txt'
    os.link(tiny, hard)
    check('Hard-linked source rejected before helper import', lambda: refuses(lambda: guard.regular(tiny)))
    hard.unlink()
for name in ('freezer-guard.py', 'freeze-engine.py', 'test-source.py'):
    check('AST parse only ' + name, lambda name=name: ast.parse((HERE / name).read_text()))
result = {'schemaVersion': 1, 'passed': True, 'checks': len(checks), 'details': checks, 'scope': 'Own stdlib-only data functions and AST/text only; actual admission result name read as source DATA.', 'genuineArtifactHelpersOrAuthorizeOrActionsInvoked': False}
with (HERE / 'source-results.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
with (HERE / 'saved-correction-proof.DATA-ONLY.json').open('x') as stream:
    json.dump({'schemaVersion': 1, 'state': 'SYNTHETIC_RECEIPT_ROLE_PROOF_NOT_AN_ACTUAL_FREEZE', 'receipt': receipt, 'actualSelectorSourceState': actual_state[0], 'actualNativeArtifact': None, 'freezeExecuted': False}, stream, indent=2)
    stream.write('\n')
print(json.dumps({'passed': True, 'checks': len(checks), 'artifactActions': 0}))
