"""Create a NEW runtime family only from explicit Root-reviewed real authority.

No compiler, package loader, componentizer, guest or target host is invoked.
The default/missing/null/unreviewed cases stop before any output is created.
"""
import sys
sys.dont_write_bytecode = True
if not __debug__: raise RuntimeError('Activation requires assertions enabled')
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
from authority import RECIPE, LABELS, load_authority

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PARENT = HERE.parent / 'integration-candidate-v1'
AMENDMENT = HERE.parent / 'harness-completion-amendment-v1'
CJS_AMENDMENT = HERE.parent / 'harness-cjs-contract-amendment-v1'
ACTIVATION_PARENT = HERE.parent / 'runtime-activation-candidate-v2'
SHARED_AMENDMENT = HERE.parent / 'shared-transpile-interface-amendment-v1'
OUTPUT = HERE.parent / 'production-runtime-activated-v3'
PARENT_INDEX = '5826a3dfc8d79ebbbbd139665dd06f9f493af3aa6f48302f2865611591fcff6d'
AMENDMENT_INDEX = '76e735336884634ab4811963586738da6c70fdcda722a74706e917a07c615489'
TOOLCHAIN = Path('/tmp/starling-node-compat/native-toolchain-lock')
PACKAGE = Path('/tmp/starling-node-compat/import-abi-clock-v2-build/package')
NODE = Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
WASMTIME = Path('/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime')
NODE_SHA = 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
WASMTIME_SHA = 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c'

def digest(data): return hashlib.sha256(data).hexdigest()
def regular(path, expected=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    if expected is not None: assert digest(data) == expected, path
    return data
def verified_index(root, expected):
    raw = regular(root / 'index.json', expected)
    rows = json.loads(raw)['files']; seen = set()
    for row in rows:
        assert row['path'] not in seen; seen.add(row['path'])
        path = root
        for part in row['path'].split('/'):
            assert part not in ('', '.', '..'); path /= part; assert not path.is_symlink()
        assert len(regular(path, row['sha256'])) == row['bytes']
    return len(rows)
def within(root, path): return path == root or root in path.parents

def main():
    assert len(sys.argv) == 5, 'reviewedPinsPath expectedSHA RootReviewReceiptPath expectedSHA'
    pin_path, pin_sha, review_path, review_sha = sys.argv[1:]
    # No artifact module or output path is touched before this authority gate.
    pins, pin_bytes, review, review_bytes = load_authority(pin_path, pin_sha, review_path, review_sha)
    assert not OUTPUT.exists() and not OUTPUT.is_symlink(), 'Never overwrite an activated family'
    stage = OUTPUT.with_name(OUTPUT.name + '.staging')
    assert not stage.exists() and not stage.is_symlink(), 'Preserve any previous partial stage'
    own_index_sha = digest(regular(HERE / 'index.json'))
    verified_index(HERE, own_index_sha)  # Caller must independently approve this exact index before invocation.
    assert verified_index(PARENT, PARENT_INDEX) == 191
    assert verified_index(AMENDMENT, AMENDMENT_INDEX) == 12
    assert verified_index(CJS_AMENDMENT, '5a15ceca10c8037440eb08fc6d47b26e204a0d9b5be752f6866e8dd2ce0169f1') == 14
    assert verified_index(ACTIVATION_PARENT, '052a63818003cb4e4f80fbe5aeb0f449f7ab2711829d0a40ed9a05b1b1cd5341') == 17
    assert verified_index(SHARED_AMENDMENT, '40166f0eef5bb65a73c89c264933f18f7757f5eb205453d55ac7b8a4a920ed4c') == 19
    tools = PARENT / 'artifact-tools'
    assert verified_index(tools, 'b3404af2d65929903577b5d1bc989218ec30e2e8daa0c1e012a2b8bbb21f9731') == 23
    sys.path.insert(0, str(tools))
    spec = importlib.util.spec_from_file_location('reviewed_classic_pin_data_exporter', tools / 'export-pin-candidate.py')
    exporter = importlib.util.module_from_spec(spec); spec.loader.exec_module(exporter)
    # Reuse the genuine frozen-artifact verifier; never project306/diagnostic data.
    actual = {}
    for label in LABELS:
        row = exporter.candidate(label)
        pin = pins['variants'][label]
        for key, value in row.items():
            if key not in ('state', 'reviewRequired', 'runtimeAcceptanceClaim'):
                assert pin[key] == value, 'Reviewed pin differs from actual freeze: ' + label + '/' + key
        actual[label] = {key: row[key] for key in ('engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256')}
    payload = {}
    for name in ('checks.mjs', 'guest.mjs', 'deferred-snippets.mjs', 'deployed-fixtures.mjs', 'node-oracle.mjs', 'node-oracle-results.json', 'run.mjs'):
        payload['harness/' + name] = regular(PARENT / 'harness' / name)
    for name in ('component-driver.mjs', 'completion.mjs'):
        payload['harness/' + name] = regular(AMENDMENT / 'proposed/harness' / name)
    for name in ('component-driver.mjs', 'completion.mjs'):
        payload['harness/' + name] = regular(SHARED_AMENDMENT / 'proposed/harness' / name)
    payload['harness/guest.mjs'] = regular(CJS_AMENDMENT / 'proposed/harness/guest.mjs')
    payload['harness/cjs-bindings.cjs'] = regular(CJS_AMENDMENT / 'proposed/harness/cjs-bindings.cjs')
    payload.update({'runtime-contract.mjs': regular(PARENT / 'runtime-contract.mjs'),
        'runtime-preflight.template.mjs': regular(HERE / 'runtime-preflight.template.mjs'),
        'consumed.mjs': regular(HERE / 'consumed.mjs'), 'runtime-pins.json': pin_bytes,
        'root-review-receipt.json': review_bytes})
    payload['README.md'] = ('This family contains reviewed actual artifact pins and the mandatory completion amendment.\n'
        'It is not runtime acceptance: no component or host is run by activation.\n'
        'Run harness/run.mjs only after independent index/preflight review; collect completion.json AND raw exit0.\n'
        'Inherited checks/oracles and guest identity assertions are unchanged; reviewed completion, CJS placement and identical generated-interface reuse amendments apply.\n'
        'No Node API version promotion, public nextTick/process, ALS or reset guarantee.\n').encode()
    inputs = {}
    def add(path, expected=None):
        path = Path(os.path.abspath(path)); boundary_value = None
        boundaries = [REPO] + [Path(pins['variants'][label]['freezeRoot']) for label in LABELS]
        for boundary in boundaries:
            if within(boundary, path):
                cursor = path
                while cursor != boundary:
                    assert not cursor.is_symlink(), cursor
                    cursor = cursor.parent
                assert boundary.is_dir() and not boundary.is_symlink()
                boundary_value = str(boundary)
                break
        data = regular(path, expected)
        row = {'path': str(path), 'sha256': digest(data), 'bytes': len(data)}
        if boundary_value is not None: row['boundary'] = boundary_value
        if str(path) in inputs: assert inputs[str(path)] == row
        inputs[str(path)] = row
    old_inputs = json.loads(regular(PARENT / 'input-freeze.json', '472a6282e3d9f98bc115504c3ef1fa5e1629096f47a5fd105706d33cc90e667e'))['inputs']
    for row in old_inputs:
        path = Path(os.path.abspath(PARENT / row['path']))
        if within(PARENT / 'source', path): path = REPO / path.relative_to(PARENT / 'source')
        elif within(PARENT / 'harness', path) and 'harness/' + path.name in payload: continue
        elif path in [PARENT / name for name in ('runtime-pins.json', 'runtime-contract.mjs', 'runtime-preflight.template.mjs')]: continue
        add(path, row['sha256'])
    # Literal/computed native package guards and oracle reads beyond the old seal.
    for name in ('abi-fix/componentize-import-i32-v1.patch', 'abi-fix/splicer-Cargo.v1.lock', 'oom/componentize-clock-errno-v2.patch'):
        add(REPO / 'tests/node-compat' / name)
    for name in ('checks.mjs', 'source-receipt.json', 'export-manifest.classic-streams.node-v22.14.0.json', 'node-final-acceptance-results.json'):
        add(HERE.parent / 'implementation-candidate-v1' / name)
    for path, expected in ((NODE, NODE_SHA), (WASMTIME, WASMTIME_SHA), (Path(pin_path), pin_sha), (Path(review_path), review_sha)):
        add(path, expected)
    for label in LABELS:
        pin = pins['variants'][label]
        for row in pin['frozenFiles']: add(Path(row['path']), row['sha256'])
        add(Path(pin['freezeReceiptPath']), pin['freezeReceiptSha256'])
    for root in (HERE, ACTIVATION_PARENT, PARENT, AMENDMENT, CJS_AMENDMENT, SHARED_AMENDMENT):
        add(root / 'index.json')
        for row in json.loads(regular(root / 'index.json'))['files']: add(root / row['path'], row['sha256'])
    policy = json.loads(regular(PARENT / 'policy.json', '137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f'))
    for row in policy['expectedNativeSourceManifest']: add(REPO / row['path'], row['sha256'])
    tool_trees, tool_links = [], []
    canonical_roots = [root.resolve(strict=True) for root in (TOOLCHAIN, PACKAGE)]
    for name, version in {'@bytecodealliance/componentize-js': '0.23.0', '@bytecodealliance/jco': '1.40.0', 'rolldown': '1.2.16'}.items():
        assert json.loads(regular(TOOLCHAIN / 'node_modules' / name / 'package.json'))['version'] == version
    assert json.loads(regular(PACKAGE / 'package.json'))['version'] == '0.23.0'
    assert json.loads(regular(PACKAGE / 'splicer-build.json'))['packagingVersion'] == 'componentize-js-0.23.0+sm-import-i32.v1+sm-clock-errno.v1'
    for root in (TOOLCHAIN, PACKAGE):
        assert root.is_dir() and not root.is_symlink()
        entries = []
        for base, dirs, files in os.walk(root, followlinks=False):
            for name in sorted(dirs + files):
                path = Path(base) / name; mode = path.lstat().st_mode
                kind = 'symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file' if stat.S_ISREG(mode) else None
                assert kind, 'No special files in selected tool roots'
                entries.append({'path': str(path.relative_to(root)), 'kind': kind})
                if kind == 'file': add(path)
                elif kind == 'symlink':
                    target = path.resolve(strict=True); assert any(within(item, target) for item in canonical_roots), path
                    target_kind = 'directory' if target.is_dir() else 'file' if target.is_file() else None; assert target_kind
                    link = {'path': str(path), 'linkText': os.readlink(path), 'resolvedTarget': str(target), 'targetKind': target_kind}
                    if target_kind == 'file':
                        data = regular(target); link.update(targetSha256=digest(data), targetBytes=len(data))
                    tool_links.append(link)
            dirs[:] = [name for name in dirs if not (Path(base) / name).is_symlink()]
        tool_trees.append({'path': str(root), 'realPath': str(root.resolve()), 'entries': sorted(entries, key=lambda row: row['path'])})
    # Native file symlinks are never traversed; tool links are separately explicit.
    for name, data in payload.items(): inputs[name] = {'path': name, 'sha256': digest(data), 'bytes': len(data), 'boundary': '.'}
    document = {'schemaVersion': 1, 'state': 'REVIEWED_CLASSIC_WHOLE_CONSUMED_INPUT_SEAL',
        'inputs': sorted(inputs.values(), key=lambda row: row['path']), 'toolTrees': tool_trees, 'toolLinks': tool_links,
        'invocation': {'nodeRealPath': str(NODE.resolve()), 'wasmtimeRealPath': str(WASMTIME.resolve()),
            'toolchainRoot': str(TOOLCHAIN), 'componentizeModule': str(PACKAGE / 'src/componentize.js')},
        'scope': 'No cache exclusions; exact file/directory/link membership of both selected roots. Hashing occurs outside performance timing.'}
    input_bytes = (json.dumps(document, indent=2) + '\n').encode(); payload['input-freeze.json'] = input_bytes
    parent_contract = json.loads(regular(PARENT / 'source-receipt.json'))
    replacements = {'PINS_SHA': pin_sha, 'INPUTS_SHA': digest(input_bytes), 'RECIPE_SHA': RECIPE,
        'SELECTOR_SHA': parent_contract['selectorSha256'], 'ADMISSION_SHA': parent_contract['admissionSha256']}
    regular(REPO / 'tests/node-compat/module-selection.mjs', replacements['SELECTOR_SHA'])
    regular(REPO / 'tests/node-compat/classic-streams-admission.mjs', replacements['ADMISSION_SHA'])
    compiled = payload['runtime-preflight.template.mjs'].decode()
    for key, value in replacements.items(): compiled = compiled.replace('@' + key + '@', value)
    assert not re.search(r'@[A-Z_]+@', compiled), 'Unbound preflight source placeholder'
    payload['runtime-preflight.mjs'] = compiled.encode()
    receipt = {'schemaVersion': 1, 'state': 'ACTUAL_REVIEWED_CLASSIC_RUNTIME_FAMILY_CREATED_NOT_EXECUTED',
        'pinsSha256': pin_sha, 'rootReviewSha256': review_sha, 'recipeSha256': RECIPE, 'actualArtifacts': actual,
        'activationSourceIndexSha256': own_index_sha,
        'integrationIndexSha256': PARENT_INDEX, 'completionAmendmentIndexSha256': AMENDMENT_INDEX,
        'cjsContractAmendmentIndexSha256': '5a15ceca10c8037440eb08fc6d47b26e204a0d9b5be752f6866e8dd2ce0169f1',
        'activationParentIndexSha256': '052a63818003cb4e4f80fbe5aeb0f449f7ab2711829d0a40ed9a05b1b1cd5341',
        'sharedTranspileInterfaceAmendmentIndexSha256': '40166f0eef5bb65a73c89c264933f18f7757f5eb205453d55ac7b8a4a920ed4c',
        'inputFreezeSha256': digest(input_bytes), 'consumedFiles': len(inputs), 'toolLinks': len(tool_links),
        'engineMetadataRewritten': False, 'componentOrHostExecuted': False, 'runtimeAcceptanceClaim': False,
        'copiedPayloads': [{'path': name, 'sha256': digest(data), 'bytes': len(data)} for name, data in sorted(payload.items())]}
    payload['source-receipt.json'] = (json.dumps(receipt, indent=2) + '\n').encode()
    index = {'schemaVersion': 1, 'state': 'ACTUAL_REVIEWED_CLASSIC_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED',
        'files': [{'path': name, 'sha256': digest(data), 'bytes': len(data)} for name, data in sorted(payload.items())], 'runtimeAcceptanceClaim': False}
    payload['index.json'] = (json.dumps(index, indent=2) + '\n').encode()
    # Authority and all ordinary input bytes rechecked before the first output.
    load_authority(pin_path, pin_sha, review_path, review_sha)
    for row in inputs.values():
        if Path(row['path']).is_absolute(): assert len(regular(Path(row['path']), row['sha256'])) == row['bytes']
    stage.mkdir(exist_ok=False)
    for name, data in payload.items():
        path = stage / name; path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream: stream.write(data)
        assert regular(path, digest(data)) == data
    assert not OUTPUT.exists() and not OUTPUT.is_symlink()
    stage.rename(OUTPUT)
    print(json.dumps({'output': str(OUTPUT), 'indexSha256': digest(payload['index.json']), 'consumedFiles': len(inputs),
        'toolLinks': len(tool_links), 'runtimeAcceptanceClaim': False}))

if __name__ == '__main__': main()
