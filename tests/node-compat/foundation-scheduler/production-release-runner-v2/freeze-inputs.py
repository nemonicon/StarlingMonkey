"""Seal finite local inputs and historical controls; never execute a guest."""
from pathlib import Path
import hashlib
import json
import os
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ROOT = REPO / 'tests/node-compat'
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
paths = set()


def add(path):
    path = Path(os.path.abspath(path))
    assert path.is_file() and not path.is_symlink(), path
    paths.add(path)


for sibling, expected in [('production-regression-candidate-v4','d0411aafee83a0ab238d456a722cf753ba850a4aaf9f55bc820827d0746491a9'),
                          ('production-followon-off-v2','48117ef405f4861ead8c8d6abfd3623efa67596d20f8db755a50082111794376')]:
    base=HERE.parent/sibling
    assert digest(base/'index.json')==expected
    add(base/'index.json');add(base/'input-freeze.json')
    for row in json.loads((base/'input-freeze.json').read_bytes())['inputs']:
        path=base/row['path'];assert digest(path)==row['sha256'];add(path)
    for row in json.loads((base/'index.json').read_bytes())['files']:
        path=base/row['path'];assert digest(path)==row['sha256'];add(path)

for path in HERE.rglob('*'):
    if path.is_file() and path.suffix in ['.mjs','.py'] and 'history' not in path.parts:
        add(path)
for name in ['historical-controls.json','runner-transformations.json']:
    add(HERE/name)
live_adapter=REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'
assert digest(live_adapter)=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
add(live_adapter)
names={
 'path':['component.mjs','static-require.cjs','raw-aliases.mjs','profile.wit','top-level-budget.mjs','top-level-invalid.mjs','semantic.mjs','glob.mjs'],
 'events':['native-component.mjs','native-checks.mjs','native-require.cjs','checks.mjs','prototype-checks.mjs','native-node-results.json'],
 'string-decoder':['native-component.mjs','native-require.cjs','native-aliases.mjs','top-level-unsupported.mjs','top-level-unknown.mjs','top-level-no-new.mjs','decoder-cases.mjs','profile.wit','component-corpus.json','production-candidate-pins.json'],
 'assert':['native-component.mjs','native-require.cjs','checks.mjs','native-node-results.json'],
 'querystring':['native-component.mjs','native-require.cjs','checks.mjs','native-node-results.json'],
 'util':['native-component.mjs','native-require.cjs','native-dynamic.mjs','component-cases.mjs','prototype-scope.mjs','native-node-results.json'],
}
old_outputs=[]
for name,files in names.items():
    base=ROOT/('foundation-'+name)
    for filename in files:add(base/filename)
    report=base/('results.json' if name=='path' else 'native-component-results.json')
    add(report);old_outputs.append(dict(path=str(report.relative_to(REPO)),sha256=digest(report)))
for row in json.loads((HERE/'runner-transformations.json').read_text())['files']:
    path=REPO/row['original'];assert digest(path)==row['originalSha256'];add(path)
upstream=ROOT/'foundation-path/upstream/sources.json';add(upstream)
for row in json.loads(upstream.read_text())['files']:
    add(upstream.parent/row['path'])
for filename in ['lexical-vectors.json','semantic-results.json','glob-vectors.json','glob-differences.json','glob-results.json']:
    path=ROOT/'foundation-path'/filename;add(path);old_outputs.append(dict(path=str(path.relative_to(REPO)),sha256=digest(path)))
controls=json.loads((HERE/'historical-controls.json').read_text())
for control in controls['modules'].values():
    engine=Path(control['engine']);assert digest(engine)==control['engineSha256'];add(engine)
    metadata=Path(str(engine)+'.build.json');assert digest(metadata)==control['receiptSha256'];add(metadata)
    for row in json.loads(metadata.read_text())['sourceManifest']:
        path=Path(control['sourceRoot'])/row['path'];assert digest(path)==row['sha256'];add(path)

# Follow real relative repository imports in selected source files. Generated
# negative-fixture strings are source data; unresolved references are listed.
visited=set();unresolved=[];nonRuntimeSourceWitnesses=[]
while True:
    pending=[p for p in paths-visited if p.is_relative_to(REPO) and p.suffix in ['.mjs','.cjs','.js']]
    if not pending:break
    for path in pending:
        visited.add(path)
        if 'history' in path.parts or (path.name=='test-host.mjs' and path.parent!=HERE):
            nonRuntimeSourceWitnesses.append(str(path.relative_to(REPO)))
            continue
        for spec in re.findall(r"(?:\bfrom\s*|\bimport\(\s*|\brequire\(\s*)['\"](\.[^'\"]+)['\"]",path.read_text()):
            target=(path.parent/spec).resolve()
            if target.is_file():add(target)
            else:
                assert path.is_relative_to(ROOT/'foundation-path/upstream') and spec in ['../common','../common/fixtures'],(path,spec)
                unresolved.append(dict(source=str(path.relative_to(REPO)),literal=spec,
                    role='Pinned Node upstream source data; selected VM execution uses the exact require shims in semantic.mjs'))
rows=[dict(path=os.path.relpath(path,HERE),sha256=digest(path),bytes=path.stat().st_size) for path in sorted(paths)]
report=dict(schemaVersion=1,state='SEALED_RELEASE_LOCAL_INPUTS_AND_HISTORICAL_CONTROLS',inputs=rows,
            preservedOldOutputs=old_outputs,unresolvedSourceLiterals=unresolved,
            archivedAndHostTestSourcesNotTraversedAsRuntimeImports=nonRuntimeSourceWitnesses,
            futureNativePartition=306,futureExternalEmbeddingPartition=3,
            packageProvenance='Existing checked loadToolchain/loadComponentizer contract remains; no whole npm-tree byte claim.',
            sourceOrGuestExecuted=False)
output=Path(os.environ.get('NODE_COMPAT_RELEASE_INPUT_FREEZE_OUTPUT',str(HERE/'input-freeze.json')))
with output.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps(dict(inputs=len(rows),oldOutputs=len(old_outputs),unresolvedLiterals=len(unresolved),guestExecuted=False)))
