"""Derive publisher context-only afterimage; no bootstrap/action imports."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'component-validation-v4-rebind-amendment-v1'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
 with(HERE/name).open('xb')as stream:stream.write(raw)
def main():
 before=(PARENT/'activate.py').read_text();current=before;edits=[]
 for old,new in[
  ("OUTPUT=HERE.parent/'component-validation-activated-v4'", "ORIGINAL_BOOTSTRAP=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-zlib/native-integration-candidate-v4')\nOUTPUT=HERE.parent/'component-validation-activated-v5'"),
  (" boot_rows=indexed(bootstrap,bootstrap_sha)", " boot_rows=indexed(bootstrap,bootstrap_sha)\n original_boot_rows=indexed(ORIGINAL_BOOTSTRAP,bootstrap_sha);assert original_boot_rows==boot_rows,'Original and staged indexed bootstrap bytes must agree'"),
  ("  for row in json.loads(regular(root/'input-freeze.json'))['inputs']:add(root/row['path'],row['sha256'],row['bytes'])", "  preparation_root=ORIGINAL_BOOTSTRAP if root==bootstrap else root\n  if root==bootstrap:\n   add(ORIGINAL_BOOTSTRAP/'index.json',bootstrap_sha)\n   for row in original_boot_rows:add(ORIGINAL_BOOTSTRAP/row['path'],row['sha256'],row['bytes'])\n  for row in json.loads(regular(preparation_root/'input-freeze.json'))['inputs']:add(preparation_root/row['path'],row['sha256'],row['bytes'])"),
  ("'mandatoryV4BootstrapRebindIndexSha256':own_sha,", "'mandatoryV4BootstrapRebindIndexSha256':'cd45865813e06085dcd86065bf816dd18b8203d127df879b1b1e2ca876662a45','mandatoryPreparationContextAmendmentIndexSha256':own_sha,'bootstrapPreparationRoot':str(ORIGINAL_BOOTSTRAP),"),
 ]:
  assert current.count(old)==1,old;current=current.replace(old,new);edits.append({'old':old,'new':new,'count':1})
 reverse=current
 for row in reversed(edits):assert reverse.count(row['new'])==1;reverse=reverse.replace(row['new'],row['old'])
 assert reverse==before
 put('activate.py',current.encode());put('publisher-proof.json',{'schemaVersion':1,'beforePath':str(PARENT/'activate.py'),'beforeSha256':sha(before.encode()),'afterSha256':sha(current.encode()),'edits':edits,'reverseExact':True,'guestOrDriverOrCorpusOrNativeMetadataChanged':False})
 print(json.dumps({'publisherEdits':4,'sourceGenerationOnly':True,'actionsExecuted':False}))
if __name__=='__main__':main()
