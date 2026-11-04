"""Finite read-only source seal; no toolchain/compiler/guest is loaded."""
from pathlib import Path
import hashlib
import json
import os
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
COMMON = HERE/'../production-regression-candidate-v4'
digest = lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
paths = set()
def add(path):
    path = Path(os.path.abspath(path))
    assert path.is_file() and not path.is_symlink(),path
    paths.add(path)

assert digest(COMMON/'index.json') == 'd0411aafee83a0ab238d456a722cf753ba850a4aaf9f55bc820827d0746491a9'
common_index = json.loads((COMMON/'index.json').read_text())
common_index_data = set()
add(COMMON/'index.json')
for row in common_index['files']:
    path = COMMON/row['path'];assert digest(path) == row['sha256']
    add(path)
    common_index_data.add(Path(os.path.abspath(path)))
common_freeze = json.loads((COMMON/'input-freeze.json').read_text())
common_runtime_paths = set()
for row in common_freeze['inputs']:
    path = COMMON/row['path'];assert digest(path) == row['sha256']
    add(path)
    common_runtime_paths.add(Path(os.path.abspath(path)))
for row in json.loads((HERE/'ancestry.json').read_text())['inputs']:
    assert digest(REPO/row['path']) == row['sha256']
    add(REPO/row['path'])
add(HERE/'preflight.mjs')
live_adapter = REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'
assert digest(live_adapter) == '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
add(live_adapter)
for name in ['sync','runtime','late','callbacks','stream-web']:
    add(HERE/('run-'+name+'.mjs'));add(HERE/'runners'/(name+'.mjs'))
web = REPO/'tests/node-compat/foundation-stream-web'
fixtures = ['native-component.mjs','native-checks.mjs','native-policies.mjs','native-require.cjs','native-aliases.mjs',
            'native-preflight.mjs','native-preflight-contract.json','native-harness.mjs','run-native-component-v11.mjs',
            'native-top-level-encoding.mjs','export-manifest.stream-web.node-v22.14.0.json']
fixtures += ['native-top-level-'+ctor+'-'+action+'.mjs' for ctor in ['compressionstream','decompressionstream'] for action in ['call','construct']]
fixtures += ['native-top-level-unknown-export-'+alias+'.mjs' for alias in ['canonical','bare']]
for name in fixtures:
    add(web/'production-candidate'/name)
for name in ['codec-cases.mjs','codec-node-results.json','guard-cases.mjs','byob-node-results.json',
             'typed-view-cases.mjs','typed-view-node-results.json','controller-cases.mjs','controller-node-results.json']:
    add(web/'candidate'/name)
for name in ['iteration/cases.mjs','iteration/node-results.json','iteration/intrinsics.mjs',
             'dataview/cases.mjs','dataview/node-results.json','dataview/policy.mjs','profile.wit']:
    add(web/name)
# Traverse only repository JS. The common external demand module is pinned
# data, whose four excerpts are validated by its preserved oracle/helper.
visited = set()
while True:
    pending = [path for path in paths-visited if path.is_relative_to(REPO) and path.suffix in ['.mjs','.js','.cjs']
               and (path not in common_index_data or path in common_runtime_paths)]
    if not pending:
        break
    for path in pending:
        visited.add(path)
        text = path.read_text()
        for spec in re.findall(r"(?:\bfrom\s*|\bimport\(\s*|\brequire\(\s*)['\"](\.[^'\"]+)['\"]",text):
            target = (path.parent/spec).resolve()
            assert target.is_relative_to(REPO) and target.is_file(),(path,spec)
            add(target)
        for spec in re.findall(r"new URL\(['\"](\.[^'\"]+)['\"],\s*import\.meta\.url\)",text):
            target = (path.parent/spec).resolve()
            if target.is_file():
                add(target)
rows = [{'path':os.path.relpath(path,HERE),'sha256':digest(path),'bytes':path.stat().st_size} for path in sorted(paths)]
document = {'schemaVersion':1,'state':'SEALED_NORMAL_OFF_FOLLOWON_LOCAL_INPUTS',
            'inputs':rows,'commonIndexSha256':digest(COMMON/'index.json'),'commonRuntimeInputs':len(common_freeze['inputs']),
            'productionNativeInputsSeparate':306,'productionExternalEmbeddingInputsSeparate':3,
            'packageProvenance':'Existing loadToolchain/loadComponentizer checks remain required; this does not snapshot all npm files.',
            'historicalGuardSources':'Included as data/source ancestry only; new bodies import the v3 fixed production preflight instead.',
            'noComponentizerCompilerOrGuestExecuted':True}
(HERE/'input-freeze.json').write_text(json.dumps(document,indent=2)+'\n')
print(json.dumps({'localInputs':len(rows),'commonRuntimeInputs':len(common_freeze['inputs']),'bytes':sum(row['bytes'] for row in rows)}))
