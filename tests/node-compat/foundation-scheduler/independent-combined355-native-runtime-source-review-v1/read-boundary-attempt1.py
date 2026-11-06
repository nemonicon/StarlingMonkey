"""Independent read/hash boundary. No owner operational module imports."""
import hashlib,json,os,stat
from pathlib import Path
OWN=Path(__file__).resolve().parent;SOURCE=OWN.parent/'combined-native-runtime-candidate-v1'
rows={};identities={};families={};aliases=[]
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
def row(d):
 assert set(d)=={'path','sha256','bytes'}and Path(d['path']).is_absolute()
 p=Path(d['path']);a=p.lstat();assert stat.S_ISREG(a.st_mode)and a.st_size==d['bytes']
 actual=dict(path=str(p),sha256=sha(p),bytes=a.st_size);z=p.lstat()
 identity=(z.st_dev,z.st_ino,z.st_mode,z.st_nlink,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 assert identity==(a.st_dev,a.st_ino,a.st_mode,a.st_nlink,a.st_size,a.st_mtime_ns,a.st_ctime_ns)and actual==d
 if d['path']in rows:assert rows[d['path']]==d and identities[d['path']]==identity
 rows[d['path']]=d;identities[d['path']]=identity
 return d
def desc(p):p=Path(p);return row(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
def read(d):row(d);return json.loads(Path(d['path']).read_bytes())
def family(d):
 if d['path']in families:row(d);return
 v=read(d);root=Path(d['path']).parent;names={'index.json'}
 for r in v['files']:
  n=r['path'];assert n not in names and n and not n.startswith('/')and '\\'not in n and all(x not in('.','..','')for x in n.split('/'));names.add(n);row(dict(r,path=str(root/n)))
 assert not any(p.is_symlink()for p in root.rglob('*'))
 assert {str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}==names
 families[d['path']]=d
own_index=desc(SOURCE/'index.json');assert own_index['sha256']=='859957d7dee30696f99591fef70a6d7efb769f1e2d58949cc31b12d4f53991de'
family(own_index);own_paths=set(rows)
inputs=json.loads((SOURCE/'source-inputs.json').read_bytes())
for d in inputs['files']:row(d)
for d in inputs['families']:family(d)
for b in inputs['boundaries']:
 value=read(b['manifest']);assert len(value[b['field']])==b['expectedRows']
 for d in value[b['field']]:row(d)
 for d in value.get(b['familyField'],[]):family(d)
refs=json.loads((SOURCE/'references.json').read_bytes());inventory=read(refs['packageInventory'])['package'];root=Path(inventory['root']);assert root.lstat().st_mode&0o777==0o700
assert len(inventory['files'])==4889 and len(inventory['links'])==21
names=set()
for d in inventory['files']:
 row({k:d[k]for k in ['path','sha256','bytes']});p=Path(d['path']);s=p.lstat();assert p==root/d['relativePath']and s.st_nlink==1 and s.st_mode&0o777==d['mode'];names.add(d['relativePath'])
for d in inventory['links']:
 p=root/d['path'];assert p.is_symlink()and os.readlink(p)==d['target']and str(p.resolve(strict=True))==d['resolvedPath']and p.resolve().is_relative_to(root)
 aliases.append(dict(path=str(p),linkText=os.readlink(p),resolved=str(p.resolve()),mode=p.lstat().st_mode));names.add(d['path'])
assert {str(p.relative_to(root))for p in root.rglob('*')if p.is_file()or p.is_symlink()}==names
child=json.loads((SOURCE/'child-inputs.json').read_bytes());assert len(child['files'])==89
for d in child['files']:assert rows[d['path']]==d
assert child['nativeApiInvocations']==0 and child['nativeFrameReturned']is False
metadata=read(refs['nativeMetadata']);assert len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==11
actual_record=read(refs['actualReadOnlyData']);assert actual_record['metadata']==metadata
catalogue=read(refs['fixtureCatalogue']);assert len(catalogue['fixtures'])==6
requirements=read(refs['fixtureRequirements']);assert len(requirements['gates'])==17
# Bookend independently; preserve hashes, current modes and identities.
for path,d in list(rows.items()):row(d)
for d in aliases:assert Path(d['path']).is_symlink()and os.readlink(d['path'])==d['linkText']and str(Path(d['path']).resolve())==d['resolved']
result=dict(schemaVersion=1,state='INDEPENDENT_SOURCE_DATA_BOUNDARY_AUTHENTICATED',sourceIndex=own_index,allUniqueFiles=len(rows),externalUniqueFiles=len(set(rows)-own_paths),ownIndexedPayloadFiles=len(own_paths)-1,families=len(families),packageFiles=4889,packageLinks=21,childFiles=89,metadataFields=80,nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifests=11,fullFixtureCount=6,requiredGates=17,nativeApiImported=False,operationalActionsInvoked=False,sourceInputs=desc(SOURCE/'source-inputs.json'),boundaryDescriptors=inputs['boundaries'],familyIndices=list(families.values()),node=refs['node'])
(OWN/'boundary-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['familyIndices','boundaryDescriptors']}))
