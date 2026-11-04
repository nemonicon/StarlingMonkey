"""UNEXECUTED producer: new runtime source family, never an engine/guest action.

Requires all four future Root-reviewed trace artifacts. No default authority.
Preparation closure stays in its original context; this producer separately
checks actual corrected342 + tool92 + the byte-identical staged proposal.
"""
import sys
sys.dont_write_bytecode = True
if not __debug__:
    raise RuntimeError('Activation requires assertions enabled')
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
from authority import RECIPE, POLICY, HELPER, CONTRACT, SOURCE_ROOT, FREEZE_ROOT, LABELS, load_authority

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE = HERE.parent / 'production-runtime-activated-v3'
BASE_SHA = '7e9520e0859b939a8586e6d0cfa1fe376a3ace75a2624dd777d5825bbf91cf66'
INTEGRATION = HERE.parent / 'trace-integration-candidate-v1'
INTEGRATION_SHA = '224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b'
OUTPUT = HERE.parent / 'production-trace-runtime-activated-v1'
TOOLCHAIN = Path('/tmp/starling-node-compat/native-toolchain-lock')
PACKAGE = Path('/tmp/starling-node-compat/import-abi-clock-v2-build/package')
NODE = Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
WASMTIME = Path('/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime')
NODE_SHA = 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
WASMTIME_SHA = 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c'


def digest(data): return hashlib.sha256(data).hexdigest()


def regular(path, expected=None):
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), str(path)
    before = path.lstat()
    data = path.read_bytes()
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), str(path)
    if expected is not None: assert digest(data) == expected, str(path)
    return data


def verified_index(root, expected):
    rows = json.loads(regular(root / 'index.json', expected))['files']
    seen = set()
    for row in rows:
        assert not Path(row['path']).is_absolute() and row['path'] not in seen
        seen.add(row['path']); path = root
        for part in row['path'].split('/'):
            assert part not in ('', '.', '..'); path /= part
            assert not path.is_symlink(), str(path)
        assert len(regular(path, row['sha256'])) == row['bytes']
    return rows


def within(root, path): return path == root or root in path.parents


def main():
    assert len(sys.argv) == 6, 'expectedOwnIndexSHA reviewedPinsPath expectedPinsSHA RootReviewReceiptPath expectedReviewSHA'
    own_sha, pin_path, pin_sha, review_path, review_sha = sys.argv[1:]
    # Null/unreviewed/old authority stops before artifact imports or any output.
    pins, pin_bytes, review, review_bytes = load_authority(pin_path, pin_sha, review_path, review_sha)
    own_rows = verified_index(HERE, own_sha)
    assert not OUTPUT.exists() and not OUTPUT.is_symlink()
    stage = OUTPUT.with_name(OUTPUT.name + '.staging')
    assert not stage.exists() and not stage.is_symlink(), 'Preserve prior partial activation'
    base_rows = verified_index(BASE, BASE_SHA)
    trace_parent = HERE.parent / 'stream-trace-regression-candidate-v2'
    trace_parent_sha = '5b40a987b3a2bba08b3192c8a3e3b80a16a32d8de2019c4ecdc9406d3733ef30'
    trace_rows = verified_index(trace_parent, trace_parent_sha)
    integration_rows = verified_index(INTEGRATION, INTEGRATION_SHA)
    assert len(integration_rows) == 159
    policy = json.loads(regular(INTEGRATION / 'policy.json', POLICY))
    regular(INTEGRATION / 'layer-policy.py', HELPER)
    assert SOURCE_ROOT.is_dir() and not SOURCE_ROOT.is_symlink()
    relative_integration = INTEGRATION.relative_to(REPO)
    verified_index(SOURCE_ROOT / relative_integration, INTEGRATION_SHA)
    source_expected = {row['path']: row['sha256'] for row in policy['expectedNativeSourceManifest']}
    assert len(source_expected) == 342
    for name, checksum in source_expected.items(): regular(SOURCE_ROOT / name, checksum)
    tool_document = json.loads(regular(INTEGRATION / 'artifact-tools/tool-pins.json',
        'd50e7d7ad946a80c7d7f58c23395ed1bb40ab437e53fc0f84c3a64a9c16e39f1'))
    assert len(tool_document['toolDependencies']) == 92
    source_expected.update({row['path']: row['sha256'] for row in tool_document['toolDependencies']})
    for row in tool_document['toolDependencies']:
        assert len(regular(SOURCE_ROOT / row['path'], row['sha256'])) == row['bytes']
    # The genuine successor verifier is imported from the corrected checkout.
    # Original preparation1175 is not followed from a relocated packet.
    tools = SOURCE_ROOT / relative_integration / 'artifact-tools'
    sys.path.insert(0, str(tools))
    assert 'artifact_common' not in sys.modules
    spec = importlib.util.spec_from_file_location('reviewed_trace_pin_data_exporter', tools / 'export-pin-candidate.py')
    exporter = importlib.util.module_from_spec(spec); spec.loader.exec_module(exporter)
    actual = {}
    for label in LABELS:
        row = exporter.candidate(label)
        pin = pins['variants'][label]
        for key, value in row.items():
            if key not in ('state', 'reviewRequired', 'runtimeAcceptanceClaim'):
                assert pin[key] == value, label + '/' + key
        assert pin['classicTraceSourcePolicy'] == policy['classicTraceSourcePolicy']
        actual[label] = {key: row[key] for key in ('engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256')}
    payload = {}
    for path in sorted((HERE / 'payload').rglob('*')):
        if path.is_file(): payload[str(path.relative_to(HERE / 'payload'))] = regular(path)
    for name in ('runtime-contract.mjs', 'runtime-preflight.template.mjs', 'consumed.mjs'):
        payload[name] = regular(HERE / name)
    payload['runtime-pins.json'] = pin_bytes
    payload['root-review-receipt.json'] = review_bytes
    payload['fresh-gates.json'] = regular(HERE / 'fresh-gates.json')
    payload['README.md'] = b'New trace source family only; runtime acceptance remains false. Fresh gates are mandatory.\n'
    inputs = {}

    def add(path, expected=None):
        path = Path(os.path.abspath(path)); boundary_value = None
        for boundary in (REPO, SOURCE_ROOT, FREEZE_ROOT):
            if within(boundary, path):
                cursor = path
                while cursor != boundary:
                    assert not cursor.is_symlink(), str(cursor); cursor = cursor.parent
                assert boundary.is_dir() and not boundary.is_symlink()
                boundary_value = str(boundary); break
        raw = regular(path, expected)
        row = {'path': str(path), 'sha256': digest(raw), 'bytes': len(raw)}
        if boundary_value is not None: row['boundary'] = boundary_value
        assert str(path) not in inputs or inputs[str(path)] == row
        inputs[str(path)] = row

    # Preserve the existing consumed graph, with explicit canonical-source
    # substitutions; discard old native freeze data, not source/body controls.
    old_seal = json.loads(regular(BASE / 'input-freeze.json',
        '085b85656558e28aa748bcbc3551a0bd9054f0fb8a43c59ee9814ce1e8d51d68'))
    old_freeze = Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze')
    mapped = []
    for row in old_seal['inputs']:
        path = Path(os.path.abspath(BASE / row['path']))
        if within(BASE, path) or within(old_freeze, path):
            continue
        if within(TOOLCHAIN, path) or within(PACKAGE, path):
            add(path, row['sha256'])
            continue
        if within(REPO, path):
            name = str(path.relative_to(REPO))
            if name in source_expected or name.startswith('tests/node-compat/') and 'foundation-classic-streams/' not in name:
                destination = SOURCE_ROOT / name
                checksum = source_expected.get(name, row['sha256'])
                add(destination, checksum)
                mapped.append({'beforePath': str(path), 'afterPath': str(destination), 'beforeSha256': row['sha256'],
                    'afterSha256': checksum, 'role': 'actual-corrected-source-or-unchanged-host-helper'})
                continue
        add(path, row['sha256'])
    for name, checksum in source_expected.items(): add(SOURCE_ROOT / name, checksum)
    for root, rows, expected in ((HERE, own_rows, own_sha), (BASE, base_rows, BASE_SHA),
                                 (INTEGRATION, integration_rows, INTEGRATION_SHA),
                                 (trace_parent, trace_rows, trace_parent_sha)):
        add(root / 'index.json', expected)
        for row in rows: add(root / row['path'], row['sha256'])
    for path, expected in ((Path(pin_path), pin_sha), (Path(review_path), review_sha), (NODE, NODE_SHA), (WASMTIME, WASMTIME_SHA)):
        add(path, expected)
    for pin in pins['variants'].values():
        for row in pin['frozenFiles']: add(Path(row['path']), row['sha256'])
        add(Path(pin['freezeReceiptPath']), pin['freezeReceiptSha256'])
    tool_trees, tool_links = [], []
    canonical_roots = [root.resolve(strict=True) for root in (TOOLCHAIN, PACKAGE)]
    for root in (TOOLCHAIN, PACKAGE):
        assert root.is_dir() and not root.is_symlink(); entries = []
        for base, dirs, files in os.walk(root, followlinks=False):
            for name in sorted(dirs + files):
                path = Path(base) / name; mode = path.lstat().st_mode
                kind = 'symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file' if stat.S_ISREG(mode) else None
                assert kind; entries.append({'path': str(path.relative_to(root)), 'kind': kind})
                if kind == 'file': add(path)
                elif kind == 'symlink':
                    target = path.resolve(strict=True); assert any(within(item, target) for item in canonical_roots)
                    target_kind = 'directory' if target.is_dir() else 'file' if target.is_file() else None
                    assert target_kind
                    link = {'path': str(path), 'linkText': os.readlink(path), 'resolvedTarget': str(target), 'targetKind': target_kind}
                    if target_kind == 'file':
                        raw = regular(target); link.update(targetSha256=digest(raw), targetBytes=len(raw))
                    tool_links.append(link)
            dirs[:] = [name for name in dirs if not (Path(base) / name).is_symlink()]
        tool_trees.append({'path': str(root), 'realPath': str(root.resolve()), 'entries': sorted(entries, key=lambda row: row['path'])})
    assert tool_trees == old_seal['toolTrees'], 'Selected tool-root membership changed'
    assert tool_links == old_seal['toolLinks'], 'Selected tool-link bindings changed'
    for name, data in payload.items(): inputs[name] = {'path': name, 'sha256': digest(data), 'bytes': len(data), 'boundary': '.'}
    seal = {'schemaVersion': 1, 'state': 'REVIEWED_CLASSIC_TRACE_WHOLE_CONSUMED_INPUT_SEAL',
        'inputs': sorted(inputs.values(), key=lambda row: row['path']), 'toolTrees': tool_trees, 'toolLinks': tool_links,
        'invocation': {'nodeRealPath': str(NODE.resolve()), 'wasmtimeRealPath': str(WASMTIME.resolve()),
            'toolchainRoot': str(TOOLCHAIN), 'componentizeModule': str(PACKAGE / 'src/componentize.js')},
        'sourceContext': {'actualConfiguredRoot': str(SOURCE_ROOT), 'originalPreparationRoot': str(INTEGRATION),
            'preparation1175RelocatedOrFollowed': False, 'canonicalSourceMappings': mapped}}
    seal_bytes = (json.dumps(seal, indent=2) + '\n').encode(); payload['input-freeze.json'] = seal_bytes
    replacements = {'PINS_SHA': pin_sha, 'INPUTS_SHA': digest(seal_bytes), 'RECIPE_SHA': RECIPE,
        'SELECTOR_SHA': digest(regular(SOURCE_ROOT / 'tests/node-compat/module-selection.mjs')),
        'ADMISSION_SHA': digest(regular(SOURCE_ROOT / 'tests/node-compat/classic-streams-admission.mjs')),
        'ROOT_REVIEW_SHA': review_sha}
    compiled = payload['runtime-preflight.template.mjs'].decode()
    for key, value in replacements.items(): compiled = compiled.replace('@' + key + '@', value)
    assert not re.search(r'@[A-Z_]+@', compiled); payload['runtime-preflight.mjs'] = compiled.encode()
    new_receipt = {'schemaVersion': 1, 'state': 'ACTUAL_REVIEWED_CLASSIC_TRACE_RUNTIME_FAMILY_CREATED_NOT_EXECUTED',
        'pinsSha256': pin_sha, 'rootReviewSha256': review_sha, 'recipeSha256': RECIPE, 'sourceContractVersion': CONTRACT,
        'sourcePolicySha256': POLICY, 'sourceHelperSha256': HELPER, 'configuredSourceRoot': str(SOURCE_ROOT),
        'actualArtifacts': actual, 'activationSourceIndexSha256': own_sha, 'integrationIndexSha256': INTEGRATION_SHA,
        'parentRuntimeSourceIndexSha256': BASE_SHA, 'inputFreezeSha256': digest(seal_bytes),
        'consumedFiles': len(inputs), 'toolLinks': len(tool_links), 'engineMetadataRewritten': False,
        'componentOrHostExecuted': False, 'runtimeAcceptanceClaim': False,
        'copiedPayloads': [{'path': name, 'sha256': digest(raw), 'bytes': len(raw)} for name, raw in sorted(payload.items())]}
    payload['source-receipt.json'] = (json.dumps(new_receipt, indent=2) + '\n').encode()
    index = {'schemaVersion': 1, 'state': 'ACTUAL_REVIEWED_CLASSIC_TRACE_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED',
        'files': [{'path': name, 'sha256': digest(raw), 'bytes': len(raw)} for name, raw in sorted(payload.items())],
        'runtimeAcceptanceClaim': False}
    payload['index.json'] = (json.dumps(index, indent=2) + '\n').encode()
    load_authority(pin_path, pin_sha, review_path, review_sha)
    verified_index(HERE, own_sha)
    for row in inputs.values():
        if Path(row['path']).is_absolute(): assert len(regular(row['path'], row['sha256'])) == row['bytes']
    stage.mkdir(exist_ok=False)
    for name, raw in payload.items():
        path = stage / name; path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream: stream.write(raw)
        assert regular(path, digest(raw)) == raw
    # Recheck authority plus all external bytes after staging, before publishing.
    load_authority(pin_path, pin_sha, review_path, review_sha)
    for row in inputs.values():
        if Path(row['path']).is_absolute(): regular(row['path'], row['sha256'])
    assert not OUTPUT.exists() and not OUTPUT.is_symlink(); stage.rename(OUTPUT)
    print(json.dumps({'output': str(OUTPUT), 'indexSha256': digest(payload['index.json']),
        'consumedFiles': len(inputs), 'toolLinks': len(tool_links), 'runtimeAcceptanceClaim': False}))


if __name__ == '__main__': main()
