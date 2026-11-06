"""Read/hash-only installed-generator consistency check; no generator/native call."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
refs=json.loads((HERE/'references.json').read_text())
checks=0
def checked(row):
    global checks
    b=Path(row['path']).read_bytes()
    assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'];checks+=1
    return b
for key in ('parentV2Index','correctedNativeV3Index','pinnedNode','unchangedInventory','unchangedManifest','unchangedCore','unchangedHeader'):checked(refs[key])
a=HERE/'after/builtins/node-compat'
for row in refs['installedInputs']:checked(row)
old=checked(refs['oldGenerator']).decode();new=(a/'generate-async-hooks-factory.mjs').read_text();e=refs['edit']
assert old.count(e['before'])==1 and new==old.replace(e['before'],e['after']);checks+=1
for name,key in (('async-hooks-node22-surface.json','unchangedInventory'),('export-manifest.async-hooks.node-v22.14.0.json','unchangedManifest'),('async-local-storage-factory.mjs','unchangedCore'),('async-hooks-factory.generated.h','unchangedHeader')):
    assert (a/name).read_bytes()==checked(refs[key]);checks+=1
surface=json.loads((a/'async-hooks-node22-surface.json').read_text());manifest=json.loads((a/'export-manifest.async-hooks.node-v22.14.0.json').read_text())
assert surface['node']=='v22.14.0' and len(surface['providers'])==63
assert manifest['modules']['node:async_hooks']['exports']==surface['exports'];checks+=2
source=(a/'async-local-storage-factory.mjs').read_text();surface_text=(a/'async-hooks-node22-surface.json').read_text();manifest_text=(a/'export-manifest.async-hooks.node-v22.14.0.json').read_text()
digest=hashlib.sha256((source+'\0'+surface_text+'\0'+manifest_text).encode()).hexdigest()
assert '// Canonical source SHA-256: '+digest+'\n' in (a/'async-hooks-factory.generated.h').read_text();checks+=1
result=json.loads((HERE/'installed-generator-test-results.json').read_text());assert result['checks']==21
assert [x['rawExitCode'] for x in result['outcomes']]==[1,0,1,1,0];checks+=2
assert refs['nativeCppChanges']==0 and refs['inventoryPathDelta']==1;checks+=1
print(json.dumps({'checks':checks,'canonicalSourceSha256':digest,'nativeActions':False}))
