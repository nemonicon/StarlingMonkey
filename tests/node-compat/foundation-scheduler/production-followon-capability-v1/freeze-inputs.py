"""Seal finite source/lineage inputs only; do not execute JS, a toolchain or host."""
from pathlib import Path
import hashlib
import json
import os
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE = HERE.parent / 'production-regression-candidate-v3'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(BASE / 'index.json') == '3064605fbf043c26e3d1bc85378b91d68c98be4034f4b6c5cf0f30f964ac61a2'
parent_index = json.loads((BASE / 'index.json').read_bytes())
parent_manifest_pin = next(row['sha256'] for row in parent_index['files'] if row['path'] == 'input-freeze.json')
assert sha(BASE / 'input-freeze.json') == parent_manifest_pin
parent = json.loads((BASE / 'input-freeze.json').read_bytes())
assert len(parent['inputs']) == 665
paths = set()
phase_pin = HERE / 'http-component-pins.json'

def add(path):
    path = Path(os.path.abspath(path))
    assert path != phase_pin, 'HTTP component pins are separately captured phase data'
    assert path.is_file() and not path.is_symlink(), path
    paths.add(path)

for row in parent['inputs']:
    path = (BASE / row['path']).resolve()
    assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes']
    add(path)
for path in sorted(HERE.rglob('*.mjs')):
    if 'history' not in path.parts and path.name != 'test-host.mjs':
        add(path)
for name in ['pins.json', 'README.md', 'focused/node-results.json', 'focused/profile.wit', 'focused/require.cjs']:
    add(HERE / name)
explicit = [
    'foundation-path/lexical-vectors.json', 'foundation-path/glob-vectors.json', 'foundation-path/glob-results.json',
    'foundation-events/native-node-results.json', 'foundation-string-decoder/component-corpus.json',
    'foundation-assert/native-node-results.json', 'foundation-querystring/native-node-results.json', 'foundation-util/native-node-results.json',
    'foundation-stream-web/production-candidate/native-preflight-contract.json',
    'foundation-stream-web/candidate/codec-node-results.json', 'foundation-stream-web/candidate/byob-node-results.json',
    'foundation-stream-web/candidate/typed-view-node-results.json', 'foundation-stream-web/candidate/controller-node-results.json',
    'foundation-stream-web/iteration/node-results.json', 'foundation-stream-web/dataview/node-results.json',
    'foundation-add-abort/production-native-m0.10/component.mjs', 'foundation-add-abort/production-native-m0.10/public-cases.mjs',
    'foundation-add-abort/production-native-m0.10/require.cjs', 'foundation-add-abort/production-native-m0.10/node-results.json',
    'wasmcloud/profile-runtime-entropy.wit', 'wasmcloud/http-stubbing.mjs', 'wasmcloud/type-audit.mjs',
    'wasmcloud/test-wasmtime-http.mjs', 'wasmcloud/run-host.mjs',
    'foundations/assert-http-report.mjs', 'foundations/assert-protected-abort-report.mjs', 'foundations/assert-stream-web-report.mjs',
]
for name in explicit:
    add(REPO / 'tests/node-compat' / name)
visited = set()
while True:
    pending = [path for path in paths - visited if path.is_relative_to(REPO) and path.suffix in ('.mjs', '.js', '.cjs')]
    if not pending:
        break
    for path in pending:
        visited.add(path)
        text = path.read_text()
        for spec in re.findall(r"(?:\bfrom\s*|\bimport\(\s*|\brequire\(\s*)['\"](\.[^'\"]+)['\"]", text):
            target = (path.parent / spec).resolve()
            assert target.is_relative_to(REPO), (path, spec)
            add(target)
        for spec in re.findall(r"new URL\(['\"](\.[^'\"]+)['\"],\s*import\.meta\.url\)", text):
            target = (path.parent / spec).resolve()
            if target.is_file():
                add(target)
rows = [{'path': os.path.relpath(path, HERE), 'sha256': sha(path), 'bytes': path.stat().st_size} for path in sorted(paths)]
document = {'schemaVersion': 1, 'state': 'SEALED_CAPABILITY_RUNTIME_SOURCES_AND_PARENT_LINEAGE',
            'inputs': rows, 'parentIndexSha256': sha(BASE / 'index.json'), 'parentInputManifestSha256': parent_manifest_pin,
            'parentLineageInputs': 665, 'historicalControls': parent['historicalControls'],
            'nativeProductionPartition': 306, 'externalEmbeddingPartition': 3,
            'phaseDataExcluded': [{'path': 'http-component-pins.json', 'reason': 'Unknown before packaging; separately reviewed and primitive-digest captured/rechecked before/after any host run'}],
            'packageProvenance': parent['packageProvenance'], 'noNativeBuildComponentGuestOrHostExecuted': True}
output = Path(os.environ.get('NODE_COMPAT_CAPABILITY_INPUT_FREEZE_OUTPUT', str(HERE / 'input-freeze.json')))
with output.open('x') as stream:
    json.dump(document, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': document['state'], 'inputs': len(rows), 'historicalLineageInputs': 665, 'binariesCopied': False}))
