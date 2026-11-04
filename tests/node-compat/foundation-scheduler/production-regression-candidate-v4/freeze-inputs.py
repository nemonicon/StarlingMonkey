"""Seal finite local runtime inputs and the two fixed historical controls as data.

Does not import/execute JS, compile, package, build or modify an engine/old source.
Native306 and external embedding3 are separate fixed-artifact preflight partitions.
"""
from pathlib import Path
import hashlib
import json
import os
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
digest = lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
paths = set()
def add(path):
    path = Path(os.path.abspath(path))
    assert path.is_file() and not path.is_symlink(),path
    paths.add(path)

for name in ['admission.mjs','preflight.mjs','pins.json','run-core.mjs','run-allocator.mjs','run-allocator-gc.mjs','runners/allocator.mjs','runners/allocator-gc.mjs']:
    add(HERE/name)
explicit = [
    'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm',
    'tests/node-compat/profile.wit','tests/node-compat/legacy-stream-web-receipts.json',
    'tests/node-compat/foundation-alloc-unsafe/node-results.json',
    'tests/node-compat/foundation-alloc-unsafe/installed/checks.mjs',
    'tests/node-compat/foundation-alloc-unsafe/installed/component-v11.mjs',
    'tests/node-compat/foundation-alloc-unsafe/installed/numeric-hooks-v11.mjs',
    'tests/node-compat/foundation-alloc-unsafe/installed/static-require.cjs',
    'tests/node-compat/foundation-alloc-unsafe/installed/run-component-v11.mjs',
    'tests/node-compat/foundation-alloc-unsafe/installed/run-gc-v11.mjs',
    'tests/node-compat/foundation-stream-web/production-candidate/native-preflight-contract.json',
    'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json',
    'tests/node-compat/foundation-scheduler/integration-candidate-v1/layer-policy.py',
    'tests/node-compat/foundation-scheduler/admission-candidate-v1/pins.json',
    'tests/node-compat/wasi-0.2.10-interfaces.json',
    'tests/node-compat/oom/componentize-clock-errno-v2.patch',
    'tests/node-compat/abi-fix/componentize-import-i32-v1.patch',
    'tests/node-compat/abi-fix/splicer-Cargo.v1.lock',
]
for name in explicit:
    add(REPO/name)
assert digest(REPO/explicit[0]) == '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
# module-selection reads these via computed repository paths, not JS imports.
# Seal every finite selected manifest as host-consumed data as well as its
# separate copy in the future native production partition.
for path in sorted((REPO/'builtins/node-compat').glob('export-manifest*.json')):
    add(path)
# The complete finite core fixture directory includes dynamic negative fixtures.
for path in (REPO/'tests/node-compat/fixtures').iterdir():
    if path.suffix in ['.mjs','.cjs']:
        add(path)
oracle = json.loads((REPO/'tests/node-compat/foundation-alloc-unsafe/node-results.json').read_text())
demand = Path(oracle['demandSource']['path'])
assert digest(demand) == oracle['demandSource']['sha256']
add(demand)
# Import graph over repository files only. Package loader proofs stay explicit
# in the existing toolchain/componentizer provenance, not silently approximated.
visited = set()
while True:
    pending = [path for path in paths-visited if path.is_relative_to(REPO) and path.suffix in ['.mjs','.cjs','.js']]
    if not pending:
        break
    for path in pending:
        visited.add(path)
        text = path.read_text()
        specs = re.findall(r"(?:\bfrom\s*|\bimport\(\s*|\brequire\(\s*)['\"](\.[^'\"]+)['\"]",text)
        for spec in specs:
            target = (path.parent/spec).resolve()
            assert target.is_file(),(path,spec)
            assert target.is_relative_to(REPO),'Unexpected outside-repository relative JS import'
            add(target)
        for spec in re.findall(r"new URL\(['\"](\.[^'\"]+)['\"],\s*import\.meta\.url\)",text):
            target = (path.parent/spec).resolve()
            if target.is_file():
                add(target)
historical = []
for version,count,expected in [(7,293,'ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09'),
                               (10,304,'1098e7531004a4ca1b47f2ca80527a01e64cd3392d28d760da37326c08a85154')]:
    root = Path('/tmp/starling-node-compat/foundations-v'+str(version)+'/native-freeze')
    engine = root/'off-foundations.engine.wasm'
    assert digest(engine) == expected
    metadata = Path(str(engine)+'.build.json')
    receipt = json.loads(metadata.read_text())
    assert receipt['engineSha256'] == expected and len(receipt['sourceManifest']) == count
    add(engine);add(metadata)
    for row in receipt['sourceManifest']:
        path = root/'source'/row['path']
        assert digest(path) == row['sha256']
        add(path)
    historical.append({'version':version,'engineSha256':expected,'sourceInputs':count,'purpose':'Preserved old-core/delegated controls only; not new-source evidence'})
rows = [{'path':os.path.relpath(path,HERE),'sha256':digest(path),'bytes':path.stat().st_size} for path in sorted(paths)]
document = {'schemaVersion':1,'state':'SEALED_RUNTIME_LOCAL_INPUTS_AND_HISTORICAL_CONTROLS',
            'inputs':rows,'historicalControls':historical,
            'nativeProductionPartition':306,'externalEmbeddingPartition':3,
            'packageProvenance':'Existing loadToolchain/loadComponentizer version/artifact checks remain mandatory and are reported by actual future runs.',
            'noNativeBuildComponentOrGuestExecuted':True}
(HERE/'input-freeze.json').write_text(json.dumps(document,indent=2)+'\n')
print(json.dumps({'inputs':len(rows),'historicalSources':597,'bytes':sum(row['bytes'] for row in rows)}))
