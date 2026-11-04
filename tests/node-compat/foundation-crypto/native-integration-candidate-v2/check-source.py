"""Source/JSON checks only: no producer/guard/helper import or action calls."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PARENT = HERE.parents[1] / 'foundation-stream-consumers/native-integration-candidate-v2'
GUARD = HERE.parent / 'prototype-key-guard-candidate-v1'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(Path(path).read_bytes())


def exact_model(rows, expected):
    assert isinstance(rows, list) and len(rows) == 355
    assert all(set(r) == {'path', 'sha256'} for r in rows)
    assert len({r['path'] for r in rows}) == 355
    assert sorted(rows, key=lambda r: r['path']) == expected


def main():
    checks = 0

    def yes(value):
        nonlocal checks
        assert value
        checks += 1

    policy = load(HERE / 'policy.json')
    parent = load(PARENT / 'policy.json')
    pins = load(HERE / 'admission-pins.json')
    before = {r['path']: r['sha256'] for r in parent['expectedNativeSourceManifest']}
    after = {r['path']: r['sha256'] for r in policy['expectedNativeSourceManifest']}
    composed = load(GUARD / 'composition.json')
    changes = policy['cryptoKeyOwnershipSourcePolicy']['changes']
    yes(set(before) == set(after) and len(after) == 355)
    yes(sum(before[k] == after[k] for k in before) == 350)
    yes(len(changes) == composed['composedSourceFiles'] == 5 and composed['composedExactEdits'] == 20)
    yes({r['path']: r['afterSha256'] for r in changes} == {r['path']: r['sha256'] for r in composed['afterimages']})
    for row in changes:
        yes(before[row['path']] == row['beforeSha256'] and after[row['path']] == row['afterSha256'])
        data = Path(row['afterimage']).read_bytes()
        yes(sha(data) == row['afterSha256'] and len(data) == row['bytes'])
    for key in ['classicTraceSourcePolicy', 'zlibSourcePolicy', 'streamConsumersSourcePolicy',
                'strictPolicyVersion', 'protectedPolicyVersion', 'privateTargetCpp',
                'embedding', 'profileVersion', 'classicManifest', 'zlibManifest']:
        yes(policy[key] == parent[key])
    yes(len(policy['privateTargetCpp']) == 6)
    yes(sum(r['path'].endswith('.cpp') and r['path'].startswith(('builtins/', 'runtime/')) for r in policy['expectedNativeSourceManifest']) == 62)
    yes(pins['policySha256'] == sha((HERE / 'policy.json').read_bytes()))
    yes(pins['helperSha256'] == sha((HERE / 'layer-policy.py').read_bytes()))
    yes(pins['productionRecipeSha256'] == sha((HERE / 'proposed/tests/node-compat/build-engine.sh').read_bytes()))
    body = (HERE / 'build-admission.mjs').read_text()
    yes(sha((HERE / 'admission-pins.json').read_bytes()) in body)
    yes(pins['productionRecipeSha256'] in body)
    yes('validateCryptoOwnerBuildSourceAdmission' in body and 'CryptoOwner355 operational admission CLOSED' in body)
    yes('Object.keys(policy.sourceLayer).length,56' in body)
    yes('cryptoKeyOwnershipBuildEvidence' in body and 'cryptoKeyOwnershipSourcePolicy' in body)
    tree = ast.parse((HERE / 'layer-policy.py').read_text())
    oldtree = ast.parse((PARENT / 'layer-policy.py').read_text())
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    oldfunctions = {n.name: n for n in oldtree.body if isinstance(n, ast.FunctionDef)}
    for name in ['expected', 'resolved', 'source_manifest', 'validate_sources', '_macro', '_release', 'validate_classic_compilation']:
        yes(ast.dump(functions[name]) == ast.dump(oldfunctions[name]))
    # The six non-main launcher definitions remain exact, not reimplemented.
    old_launch = ast.parse((PARENT / 'artifact-tools/build-one.py').read_text())
    new_launch = ast.parse((HERE / 'artifact-tools/build-one.py').read_text())
    old_defs = {n.name: n for n in old_launch.body if isinstance(n, ast.FunctionDef) and n.name != 'main'}
    new_defs = {n.name: n for n in new_launch.body if isinstance(n, ast.FunctionDef) and n.name != 'main'}
    yes(set(old_defs) == set(new_defs))
    for name in old_defs:
        yes(ast.dump(old_defs[name]) == ast.dump(new_defs[name]))
    common = ast.parse((HERE / 'artifact-tools/artifact_common.py').read_text())
    reader = next(n for n in common.body if isinstance(n, ast.FunctionDef) and n.name == 'verify_frozen_variant')
    yes(isinstance(reader.body[1], ast.Expr) and isinstance(reader.body[1].value, ast.Call) and reader.body[1].value.func.id == 'tool_dependencies')
    for name in ['bootstrap-pins.json', 'runtime-pins.json']:
        j = load(HERE / name)
        yes(all(v is None for v in j['variants'].values()) and j['operationalAdmission'] is False)
    yes(load(HERE / 'future-authority.json')['rootStageAuthority'] is None)
    tools = load(HERE / 'artifact-tools/tool-pins.json')
    rows = load(HERE / 'tool-origins.json')['files']
    yes(len(rows) == len(tools['toolDependencies']) == 922)
    yes({r['path']: (r['sha256'], r['bytes']) for r in rows} == {r['path']: (r['sha256'], r['bytes']) for r in tools['toolDependencies']})
    yes(tools['nativeSources'] == 355 and tools['reviewedEnginePins'] is None)
    yes(tools['recipeSha256'] == pins['productionRecipeSha256'])
    toolsha = sha((HERE / 'artifact-tools/tool-pins.json').read_bytes())
    yes(toolsha in (HERE / 'artifact-tools/artifact_common.py').read_text() and toolsha in (HERE / 'artifact-tools/metadata-admission.mjs').read_text())
    # Real old355 rows cannot enter the new source identity merely by count.
    rejected = []
    bad = [parent['expectedNativeSourceManifest'], policy['expectedNativeSourceManifest'][:-1],
           policy['expectedNativeSourceManifest'] + [{'path': 'unexpected.cpp', 'sha256': 'a' * 64}]]
    mixed = copy.deepcopy(policy['expectedNativeSourceManifest'])
    next(r for r in mixed if r['path'] == changes[0]['path'])['sha256'] = changes[0]['beforeSha256']
    bad.append(mixed)
    duplicate = copy.deepcopy(policy['expectedNativeSourceManifest'])
    duplicate[-1] = copy.deepcopy(duplicate[0])
    bad.append(duplicate)
    for number, rows_bad in enumerate(bad):
        try:
            exact_model(rows_bad, policy['expectedNativeSourceManifest'])
        except AssertionError:
            rejected.append(number)
        else:
            raise AssertionError('bad model admitted')
    yes(len(rejected) == 5)
    exact_model(policy['expectedNativeSourceManifest'], policy['expectedNativeSourceManifest'])
    # Existing real metadata is DATA only; no classifier/admission is invoked.
    existing = []
    for label in ['normal-off', 'normal-runtime', 'gc-off', 'disabled-off']:
        path = Path('/tmp/starling-node-compat/production-consumers-v1/native-freeze') / (label + '.engine.wasm.build.json')
        metadata = load(path)
        yes(metadata['buildRecipeSha256'] != pins['productionRecipeSha256'])
        yes({r['path']: r['sha256'] for r in metadata['sourceManifest']} == before)
        yes('cryptoKeyOwnershipPolicy' not in metadata)
        existing.append({'label': label, 'path': str(path), 'sha256': sha(path.read_bytes()), 'oldRecipeAndFivePreimagesRemainDistinct': True})
    # Derive full filename lengths for all finite modes; never execute recipe.
    lengths = {}
    for label in ['normal-off', 'normal-runtime', 'gc-off', 'disabled-off']:
        artifact = 'starlingmonkey_embedding.abi-i32-i64-v1' + ('.gc-stress' if label == 'gc-off' else '')
        artifact += '.keyowner-v2.' + ('RUNTIME_ONLY' if label == 'normal-runtime' else 'OFF')
        artifact += '.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s' + ('0' if label == 'disabled-off' else '1') + '.ko355v2'
        names = [artifact + suffix for suffix in ['.wasm', '.wasm.build.json', '.raw.wasm', '.raw.wasm.build.json']]
        names += [prefix + artifact + suffix for prefix, suffix in [('componentize-native-inputs-', '.json'), ('source-inputs-', '.json'), ('openssl-source-', '.before.json'), ('configure-', '.log'), ('build-', '.log')]]
        yes(max(map(len, names)) <= 255)
        lengths[label] = {'longestGeneratedBasenameBytesASCII': max(map(len, names)), 'engine': len(artifact + '.wasm'), 'sidecar': len(artifact + '.wasm.build.json')}
    result = {'schemaVersion': 1, 'state': 'CRYPTO_OWNER355_SOURCE_DATA_CHECKS_PASSED',
              'checks': checks, 'negativeSourceModelsRejected': len(rejected),
              'nativeFiles': 355, 'unchangedParentFiles': 350, 'changedNativeFiles': 5,
              'launcherLifecycleDefinitionsByteEquivalent': len(old_defs),
              'existing355MetadataReadAsDataOnly': existing, 'filenameLengths': lengths,
              'producerHelperArtifactBootstrapStageCompilerCryptoGuestOrHostInvoked': False,
              'sourceOnly': True, 'operationalAdmission': False}
    print(json.dumps(result))


if __name__ == '__main__':
    main()
