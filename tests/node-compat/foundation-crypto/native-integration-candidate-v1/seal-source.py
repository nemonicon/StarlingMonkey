"""Seal source/data only; no action helper, stage, producer or SDK imports."""
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARENT = HERE.parents[1] / 'foundation-stream-consumers/native-integration-candidate-v2'
NODE = '/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
inputs = {}


def h(raw):
    return hashlib.sha256(raw).hexdigest()


def capture(path, expected=None, size=None):
    p = Path(path)
    st = p.lstat()
    assert stat.S_ISREG(st.st_mode) and not p.is_symlink(), str(p)
    raw = p.read_bytes()
    assert expected is None or h(raw) == expected, str(p)
    assert size is None or len(raw) == size, str(p)
    key = str(p.resolve())
    row = {'path': key, 'sha256': h(raw), 'bytes': len(raw)}
    assert key not in inputs or inputs[key] == row
    inputs[key] = row
    return raw


def write(name, value):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


assert not (HERE / 'index.json').exists()
families = []
for root, checksum in [
    (PARENT, '9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378'),
    (HERE.parent / 'key-owner-candidate-v1', '216d0272025145f70c3a1e1c5e4f27cc3cc47ef6f97ae8131467e803db3c47d0'),
    (HERE.parent / 'prototype-key-guard-candidate-v1', '73fbf4f24e013bfe6f7f87830c95b8690ef1700683d9b9620b09ce839d9da831')]:
    raw = capture(root / 'index.json', checksum)
    rows = json.loads(raw)['files']
    for row in rows:
        capture(root / row['path'], row['sha256'], row['bytes'])
    families.append({'path': str(root), 'indexSha256': checksum, 'indexedSourceFiles': len(rows),
                     'preparationManifestRowsFollowed': False})
for family in ['independent-key-owner-source-review-v1', 'independent-prototype-key-guard-source-review-v1']:
    root = HERE.parent / family
    raw = capture(root / 'index.json')
    for row in json.loads(raw)['files']:
        capture(root / row['path'], row['sha256'], row['bytes'])
policy = json.loads((HERE / 'policy.json').read_bytes())
pins = json.loads((HERE / 'admission-pins.json').read_bytes())
native = json.loads((HERE / 'native-origins.json').read_bytes())
for row in native['files']:
    capture(row['original'], row['sha256'])
tools = json.loads((HERE / 'tool-origins.json').read_bytes())
for row in tools['files']:
    capture(row['original'], row['sha256'], row['bytes'])
fixture = json.loads((HERE / 'validation-plan.json').read_bytes())['existingFixtureSource']
capture(fixture['path'], fixture['sha256'], fixture['bytes'])
# Generate reversible proof data from exact immutable parent source afterimages.
origins = {r['path']: r for r in json.loads((PARENT / 'tool-origins.json').read_bytes())['files']}
parents = {'policy.json': PARENT / 'policy.json', 'layer-policy.py': PARENT / 'layer-policy.py',
           'admission-pins.json': PARENT / 'admission-pins.json',
           'bootstrap-contract.json': PARENT / 'bootstrap-contract.json',
           'bootstrap-pins.json': PARENT / 'bootstrap-pins.json', 'runtime-pins.json': PARENT / 'runtime-pins.json',
           'proposed/tests/node-compat/build-engine.sh': Path(origins['tests/node-compat/build-engine.sh']['original']),
           'build-admission.mjs': Path(origins['tests/node-compat/stream-consumers-admission.mjs']['original'])}
for path in (HERE / 'artifact-tools').rglob('*'):
    if path.is_file():
        name = str(path.relative_to(HERE))
        if (PARENT / name).is_file():
            parents[name] = PARENT / name
proofs, same = [], []
for name, before_path in sorted(parents.items()):
    before = capture(before_path)
    after = (HERE / name).read_bytes()
    if before == after:
        same.append(name)
        continue
    delta = list(difflib.ndiff(before.decode().splitlines(keepends=True), after.decode().splitlines(keepends=True)))
    assert ''.join(difflib.restore(delta, 1)).encode() == before
    assert ''.join(difflib.restore(delta, 2)).encode() == after
    proofs.append({'path': name, 'parentPath': str(before_path), 'beforeSha256': h(before),
                   'afterSha256': h(after), 'exactForwardAndReverse': True, 'ndiff': delta})
write('derivations.json', {'schemaVersion': 1, 'files': proofs, 'parentByteIdenticalSourceFiles': same,
                         'nativeChanges': policy['cryptoKeyOwnershipSourcePolicy']['changes'],
                         'exactFivePayloadsPreserved': True, 'composedNativeEdits': 20})
env = dict(os.environ)
env['PYTHONDONTWRITEBYTECODE'] = '1'
env.pop('PYTHONOPTIMIZE', None)
run = subprocess.run([sys.executable, str(HERE / 'check-source.py')], capture_output=True, env=env)
for name, data in [('source.stdout.log', run.stdout), ('source.stderr.log', run.stderr)]:
    p = HERE / 'evidence' / name
    p.parent.mkdir(exist_ok=True)
    with p.open('xb') as f:
        f.write(data)
assert run.returncode == 0, run.stderr.decode()
report = json.loads(run.stdout)
write('evidence/source-results.json', report)
syntax = []
capture(NODE, 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
for p in sorted(HERE.rglob('*')):
    if p.suffix == '.py':
        ast.parse(p.read_text())
        syntax.append({'path': str(p.relative_to(HERE)), 'PythonASTParsed': True})
    elif p.suffix == '.mjs':
        result = subprocess.run([NODE, '--check', str(p)], capture_output=True, env=env)
        assert result.returncode == 0, result.stderr.decode()
        syntax.append({'path': str(p.relative_to(HERE)), 'NodeSyntaxExitCode': 0})
    elif p.suffix == '.sh':
        result = subprocess.run(['bash', '-n', str(p)], capture_output=True, env=env)
        assert result.returncode == 0, result.stderr.decode()
        syntax.append({'path': str(p.relative_to(HERE)), 'BashParseOnlyExitCode': 0})
write('evidence/syntax-results.json', {'schemaVersion': 1, 'checks': len(syntax), 'files': syntax,
                                     'scriptBodiesExecuted': False})
for row in list(inputs.values()):
    capture(row['path'], row['sha256'], row['bytes'])
write('input-freeze.json', {'schemaVersion': 1, 'state': 'SOURCE_PREPARATION_INPUTS_NOT_CONFIGURED_OR_FROZEN_ROOT',
                           'files': sorted(inputs.values(), key=lambda r: r['path']), 'families': families,
                           'parentPreparationManifestsFollowed': False, 'runtimeAuthority': None})
write('source-receipt.json', {
    'schemaVersion': 1, 'state': 'UNAPPLIED_CRYPTO_OWNER355_INTEGRATION_BUILD_MECHANISM_SOURCE_ONLY',
    'parent355IndexSha256': families[0]['indexSha256'], 'ownerIndexSha256': families[1]['indexSha256'],
    'prototypeGuardIndexSha256': families[2]['indexSha256'],
    'recipeSha256': pins['productionRecipeSha256'], 'policySha256': pins['policySha256'],
    'helperSha256': pins['helperSha256'], 'nativeSources': 355, 'unchangedParentSources': 350,
    'changedNativeSources': 5, 'exactComposedEdits': 20, 'nativeCpp': 62, 'strictCpp': 4,
    'privateNodeCpp': 6, 'embeddingCpp': 1, 'toolRows': len(tools['files']),
    'toolPinsSha256': h((HERE / 'artifact-tools/tool-pins.json').read_bytes()),
    'sourceDataChecks': report['checks'], 'negativeSourceModels': report['negativeSourceModelsRejected'],
    'syntaxChecks': len(syntax), 'sourcePreparationReferences': len(inputs),
    'ordinarySelectorOrNodeFacadeOrCMakeOrMacroSelectionChanged': False,
    'stageOrProducerOrArtifactHelperOrAdmissionOrBootstrapOrCompilerOrCryptoOrGuestExecuted': False,
    'oldUnsafePrototypePathExecuted': False, 'operationalAdmission': False,
    'futureEnginePins': None, 'futureRootStageAuthority': None, 'futureRuntimeAuthority': None,
    'allCopiesErasedClaim': False, 'runtimeAcceptanceClaim': False, 'performanceClaim': False,
    'independentSourceReviewContract': {'schemaVersion': 1,
        'state': 'INDEPENDENT_CRYPTO_OWNER355_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V1',
        'sourceIndexSha256': 'EXACT_THIS_INDEX_SHA256', 'sourceOnly': True,
        'sourceReviewPassed': True, 'ownerActionsInvoked': False}})
rows = []
for p in sorted(HERE.rglob('*')):
    if p.is_dir():
        continue
    assert p.is_file() and not p.is_symlink()
    raw = p.read_bytes()
    rows.append({'path': str(p.relative_to(HERE)), 'sha256': h(raw), 'bytes': len(raw)})
write('index.json', {'schemaVersion': 1, 'state': 'SOURCE_ONLY_CRYPTO_OWNER355_NATIVE_INTEGRATION_SEALED',
                     'files': rows, 'nativeSourceInputs': 355, 'futureEnginePins': None,
                     'operationalAdmission': False, 'runtimeAcceptanceClaim': False})
print(json.dumps({'indexSha256': h((HERE / 'index.json').read_bytes()), 'files': len(rows),
                  'inputRows': len(inputs), 'recipeSha256': pins['productionRecipeSha256'],
                  'sourceOnly': True, 'actionsExecuted': False}))
