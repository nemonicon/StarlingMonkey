"""Derive only the explicit peer-inventory publisher correction."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'component-validation-preparation-context-amendment-v1'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
 with(HERE/name).open('xb')as stream:stream.write(raw)
def main():
 before=(PARENT/'activate.py').read_text();current=before;edits=[]
 old_loop=before[before.index(' for root,rows,digest in['):before.index(' add(pins_path,pins_sha)')]
 for old,new in[
  ('component-validation-activated-v5','component-validation-activated-v6'),
  (" spec=importlib.util.spec_from_file_location('actual_zlib350_validation_bootstrap'", " inventory_spec=importlib.util.spec_from_file_location('explicit_validation_inventory',HERE/'inventory.py');inventory=importlib.util.module_from_spec(inventory_spec);inventory_spec.loader.exec_module(inventory)\n spec=importlib.util.spec_from_file_location('actual_zlib350_validation_bootstrap'"),
  (old_loop," inventory_families=inventory.collect_validation_inventory(HERE,own_sha,bootstrap,bootstrap_sha,add)\n"),
  ("'mandatoryPreparationContextAmendmentIndexSha256':own_sha,", "'mandatoryPreparationContextAmendmentIndexSha256':'f6f0e1916d02445a0c7e2fc60b0b31b26ef19aef210d59a9964ba77dfcefdee9','mandatoryIndexedPeerInventoryAmendmentIndexSha256':own_sha,'inventoryFamilies':inventory_families,"),
 ]:
  assert current.count(old)==1,old;current=current.replace(old,new);edits.append({'old':old,'new':new,'count':1})
 reverse=current
 for row in reversed(edits):assert reverse.count(row['new'])==1;reverse=reverse.replace(row['new'],row['old'])
 assert reverse==before
 put('activate.py',current.encode());put('publisher-proof.json',{'schemaVersion':1,'beforePath':str(PARENT/'activate.py'),'beforeSha256':sha(before.encode()),'afterSha256':sha(current.encode()),'edits':edits,'reverseExact':True,'guestOrDriverOrNativeChanged':False})
 print(json.dumps({'publisherEdits':4,'sourceOnly':True,'actionsExecuted':False}))
if __name__=='__main__':main()
