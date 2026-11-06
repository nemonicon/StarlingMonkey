"""Own finite delta seal, no native/source generator rerun."""
from pathlib import Path
import ast,hashlib,json
OWN=Path(__file__).resolve().parent
def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists()
for p in OWN.glob('*.py'):ast.parse(p.read_bytes())
deriv=read(OWN/'derivations.json');refs=read(OWN/'references.json');checks=read(OWN/'checks.json')
for r in [deriv[k]for k in ['generatorBefore','generatorAfter','canonicalInventoryBefore','versionedInventory','headerBefore','headerAfter']]:assert d(r['path'])==r
before=Path(deriv['generatorBefore']['path']).read_text();after=before
for e in deriv['edits']:assert after.count(e['before'])==1;after=after.replace(e['before'],e['after'])
assert after==Path(deriv['generatorAfter']['path']).read_text()
for e in reversed(deriv['edits']):after=after.replace(e['after'],e['before'])
assert after==before
for row in checks['commands']:
 assert row['rawExitCode']==row['expectedRawExitCode']
 for k in ['stdout','stderr']:assert d(row[k]['path'])==row[k]
assert len(checks['commands'])==10 and checks['generatedFunctionBodyByteIdentical']and checks['unusedInventoryMutationOldPassNewFail']
parent=Path(refs['parentSourceIndex']['path']).parent;assert d(parent/'index.json')==refs['parentSourceIndex']
for r in read(parent/'index.json')['files']:assert d(parent/r['path'])==dict(r,path=str(parent/r['path']))
manifest=read(OWN/'prospective-source-manifest.json');mapping=read(OWN/'native-mappings.json');assert len(manifest['files'])==364
for row in mapping['overrides']:assert next(r['sha256']for r in manifest['files']if r['path']==row['path'])==row['origin']['sha256']and d(row['origin']['path'])==row['origin']
rows=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():rows.append(dict(d(p),path=p.relative_to(OWN).as_posix()))
save('index.json',dict(schemaVersion=1,state='SEALED_UNCOMPILED_INVENTORIED_NODE_MODULE_SOURCE_V2',files=rows))
for n in ['index.json','results.json','source-receipt.json','future-source-review-contract.json']:print(json.dumps(d(OWN/n)))
