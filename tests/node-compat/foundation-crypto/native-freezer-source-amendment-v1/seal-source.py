"""Own source/data sealer only; no producer, staging or artifact code is imported."""
from pathlib import Path
import hashlib
import json
import stat

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = HERE.parents[3]


def row(path):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink()
    data = path.read_bytes()
    after = path.lstat()
    assert (before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns)
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def put(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


inputs = {}
for family, expected in [
    ('native-integration-candidate-v2', '68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575'),
    ('independent-crypto-owner355-native-integration-v2-source-review-v1', 'ebbfda800fc288ea249b9c2e3af2f77a6a0ae1153bc9586b9aab91999a060dac'),
    ('independent-native-integration-v2-freeze-contract-review-v1', '62cf4f2c270668b26fa0e21612f2bb1fdc4bef3884c1ac538550c41a87cbc912')
]:
    index = row(BASE / family / 'index.json')
    assert index['sha256'] == expected
    inputs[index['path']] = index
    for member in json.loads(Path(index['path']).read_bytes())['files']:
        name = member['path']
        assert not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/'))
        actual = row(BASE / family / name)
        assert actual['sha256'] == member['sha256'] and actual['bytes'] == member['bytes']
        inputs[actual['path']] = actual
put('input-freeze.json', {'schemaVersion': 1, 'state': 'ORIGINAL_SOURCE_AND_DIAGNOSIS_DATA_ONLY_NOT_A_RELOCATED_EXECUTION_CONTEXT',
    'files': sorted(inputs.values(), key=lambda value: value['path']), 'oldPreparationManifestsFollowed': False})
checks = json.loads((HERE / 'source-results.json').read_bytes())
assert checks['passed'] and checks['checks'] == 53 and checks['genuineArtifactHelpersOrAuthorizeOrActionsInvoked'] is False
donor = BASE / 'native-integration-candidate-v2'
pins = json.loads((donor / 'artifact-tools/tool-pins.json').read_bytes())
put('source-receipt.json', {'schemaVersion': 1, 'state': 'UNEXECUTED_CRYPTO_OWNER355_FREEZER_SOURCE_CORRECTION_SEALED',
    'donorSourceIndexSha256': '68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575',
    'activeFreezer': row(HERE / 'freeze-engine.py'), 'guard': row(HERE / 'freezer-guard.py'),
    'recipeSha256': pins['recipeSha256'], 'policySha256': pins['sourcePolicySha256'],
    'sourceHelperSha256': pins['sourceHelperSha256'], 'toolPinsSha256': row(donor / 'artifact-tools/tool-pins.json')['sha256'],
    'unchangedToolRows': len(pins['toolDependencies']), 'unchangedNativeSources': 355,
    'exactDonorEdits': 7, 'sourceAndPureChecks': 53, 'syntax': 'Three AST-only checks included in the 53',
    'preparationScope': 'Own pure guard data functions, tiny owned files, hashes and AST only.',
    'actualAdmissionOrArtifactHelpersInvoked': False, 'freezeExecuted': False, 'engineReadOrExecuted': False,
    'stageBuildCryptoGcGuestHostActionsInvoked': False, 'positiveAuthority': None})
for original in inputs.values():
    assert row(original['path']) == original
files = [row(path) for path in sorted(HERE.rglob('*')) if path.is_file()]
assert all(not path.is_symlink() for path in HERE.rglob('*'))
put('index.json', {'schemaVersion': 1, 'state': 'IMMUTABLE_UNEXECUTED_CRYPTO_OWNER355_FREEZER_SOURCE_CORRECTION',
    'files': [dict(value, path=str(Path(value['path']).relative_to(HERE))) for value in files]})
print(json.dumps({'index': row(HERE / 'index.json'), 'files': len(files), 'inputs': len(inputs)}))
