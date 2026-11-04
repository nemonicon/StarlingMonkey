"""Finite read-only validation-publisher inventory. No action/codec imports."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
ORIGINAL=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-zlib/native-integration-candidate-v4')
STAGED=Path('/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/foundation-zlib/native-integration-candidate-v4')
BOOT_SHA='d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
BASES=(
 ('base','component-validation-candidate-v1','a7eca2349282a29649806c327c41ea19f01be9673c0bd7c72201f30672819816','PREPARATION'),
 ('control','component-validation-control-evidence-amendment-v1','fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353','PREPARATION'),
 ('coverage','component-validation-bootstrap-coverage-amendment-v1','a376c32b640df35ea563a722b9df480569bf08367ade8752876addc3d1423191','PREPARATION'),
 ('peer','independent-component-validation-coverage-source-review-v1','654f077fe86dbb2f615bc13d2133c9747a528e74018345ae47f9633f05e8a21e','INDEXED_ONLY'),
)
def regular(path,digest=None,size=None):
 path=Path(path);assert path.is_file()and not path.is_symlink(),str(path);raw=path.read_bytes();assert digest is None or hashlib.sha256(raw).hexdigest()==digest,str(path);assert size is None or len(raw)==size,str(path);return raw
def read_indexed(root,digest,read_file=regular):
 rows=json.loads(read_file(Path(root)/'index.json',digest))['files'];seen=set()
 for row in rows:
  name=row['path'];assert isinstance(name,str)and name not in seen and not Path(name).is_absolute()and all(p not in('','.','..')for p in name.split('/'));seen.add(name);read_file(Path(root)/name,row['sha256'],row['bytes'])
 return rows
def collect_validation_inventory(publisher_root,publisher_sha,bootstrap_root,bootstrap_sha,add,read_file=regular):
 publisher_root=Path(publisher_root).resolve(strict=True);bootstrap_root=Path(bootstrap_root).resolve(strict=True)
 assert publisher_root==HERE and re.fullmatch('[a-f0-9]{64}',publisher_sha)
 assert bootstrap_root==STAGED.resolve(strict=True)and bootstrap_sha==BOOT_SHA
 families=[('publisher',publisher_root,publisher_sha,'PREPARATION',publisher_root)]
 families.extend((role,HERE.parent/name,digest,kind,HERE.parent/name)for role,name,digest,kind in BASES)
 families.append(('bootstrap',bootstrap_root,bootstrap_sha,'PREPARATION',ORIGINAL))
 summaries=[]
 for role,root,digest,kind,preparation_root in families:
  rows=read_indexed(root,digest,read_file);add(root/'index.json',digest)
  for row in rows:add(root/row['path'],row['sha256'],row['bytes'])
  summary={'role':role,'root':str(root),'indexSha256':digest,'kind':kind,'indexedFiles':len(rows)}
  if kind=='INDEXED_ONLY':
   assert role=='peer';summary['preparationManifestRead']=False
  else:
   assert kind=='PREPARATION'and role in('publisher','base','control','coverage','bootstrap')
   if role=='bootstrap':
    original_rows=read_indexed(ORIGINAL,digest,read_file);assert original_rows==rows
    add(ORIGINAL/'index.json',digest)
    for row in original_rows:add(ORIGINAL/row['path'],row['sha256'],row['bytes'])
   # Known preparation families REQUIRE their actual manifest; no exists-skip.
   manifest=json.loads(read_file(preparation_root/'input-freeze.json'));assert manifest['schemaVersion']==1
   for row in manifest['inputs']:add(preparation_root/row['path'],row['sha256'],row['bytes'])
   summary.update({'preparationManifestRead':True,'preparationRoot':str(preparation_root),'preparationRows':len(manifest['inputs'])})
  summaries.append(summary)
 assert [row['role']for row in summaries]==['publisher','base','control','coverage','peer','bootstrap']
 return summaries
