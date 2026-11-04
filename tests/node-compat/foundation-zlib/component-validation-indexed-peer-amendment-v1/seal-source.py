"""Seal code before the separately recorded actual-self inventory regression."""
from pathlib import Path
import ast,hashlib,json,sys
HERE=Path(__file__).resolve().parent
PARENTS={
 'component-validation-preparation-context-amendment-v1':'f6f0e1916d02445a0c7e2fc60b0b31b26ef19aef210d59a9964ba77dfcefdee9',
 'independent-component-validation-preparation-context-source-review-v1':'541b2779f049c2f25c81ff3aed2f77975da14ea9caa821a347181203ed9147ab',
}
CORRECTION='validation-source-activation-attempt2-root-origin-correction.json'
CORRECTION_SHA='19db5ef2caba575adb23b1126d4567bb7ce222fe75149a31c18bcf35f4311b06'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 with(HERE/name).open('xb')as stream:stream.write((json.dumps(value,indent=2)+'\n').encode())
def regular(path,digest=None,size=None):
 path=Path(path);assert path.is_file()and not path.is_symlink();raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path;return raw
def main():
 assert len(sys.argv)==1 and not(HERE/'index.json').exists();checks=[]
 proof=json.loads(regular(HERE/'publisher-proof.json'));before=regular(Path(proof['beforePath'])).decode();after=regular(HERE/'activate.py').decode();assert sha(before.encode())==proof['beforeSha256']and sha(after.encode())==proof['afterSha256']and len(proof['edits'])==4;current=before
 for row in proof['edits']:assert current.count(row['old'])==1;current=current.replace(row['old'],row['new']);checks.append('exact forward edit '+str(len(checks)+1))
 assert current==after
 for row in reversed(proof['edits']):assert current.count(row['new'])==1;current=current.replace(row['new'],row['old'])
 assert current==before;checks.append('four publisher edits reverse exactly')
 def actual_block(text):return text[text.index(' actual={};headers={};inputs={}'):text.index(" names=['component.mjs'")]
 assert actual_block(before)==actual_block(after);checks.append('actual source350/tool632/frozen/header collection block byte-identical')
 assert after.index('own=indexed(HERE,own_sha)')<after.index("HERE/'inventory.py'");assert after.index('original_boot_rows=indexed(ORIGINAL_BOOTSTRAP,bootstrap_sha)')<after.index("HERE/'inventory.py'");checks.append('new helper imported only after own/original/staged index authentication')
 inventory=regular(HERE/'inventory.py').decode();assert "'peer','independent-component-validation-coverage-source-review-v1'"in inventory and "'INDEXED_ONLY'"in inventory and "if kind=='INDEXED_ONLY':"in inventory and "assert role=='peer'"in inventory;checks.append('explicit peer-only indexed classification')
 assert "manifest=json.loads(read_file(preparation_root/'input-freeze.json'))"in inventory and '.exists('not in inventory;checks.append('known preparation manifests required without exists shortcut')
 assert "families.append(('bootstrap',bootstrap_root,bootstrap_sha,'PREPARATION',ORIGINAL))"in inventory and 'original_rows==rows'in inventory;checks.append('bootstrap indexed context staged, preparation context original')
 assert 'inventory.collect_validation_inventory(HERE,own_sha,bootstrap,bootstrap_sha,add)'in after;checks.append('publisher uses same finite collector as read-only regression')
 for name in ['component-validation-activated-v6','component-validation-activated-v6.staging']:assert not(HERE.parent/name).exists()and not(HERE.parent/name).is_symlink()
 checks.append('new output/staging absent')
 syntax=[]
 for path in sorted(HERE.glob('*.py')):ast.parse(path.read_text());syntax.append({'path':path.name,'kind':'Python AST','sha256':sha(path.read_bytes())})
 correction=json.loads(regular(HERE.parent/CORRECTION,CORRECTION_SHA));assert correction['laterIssueIsNotTheObservedSavedFailureOrigin']is True and correction['nativeArtifactsOrAuthorityOrGuestPayloadChanged']is False;checks.append('corrected Root first-failure origin pinned')
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);raw=regular(path,digest,size);path=path.resolve(strict=True);row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 for name,digest in PARENTS.items():
  root=HERE.parent/name;add(root/'index.json',digest)
  for row in json.loads(regular(root/'index.json',digest))['files']:add(root/row['path'],row['sha256'],row['bytes'])
  if name=='component-validation-preparation-context-amendment-v1':
   for row in json.loads(regular(root/'input-freeze.json'))['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
 add(HERE.parent/CORRECTION,CORRECTION_SHA)
 for path in sorted(HERE.iterdir()):
  if path.is_file():add(path)
 put('input-freeze.json',{'schemaVersion':1,'state':'EXPLICIT_VALIDATION_FAMILY_INVENTORY_SOURCE_PREPARATION','inputs':sorted(rows.values(),key=lambda row:row['path']),'actionOrGuestExecuted':False})
 put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_INDEXED_PEER_INVENTORY_SOURCE_REQUIRES_POSTSEAL_READONLY_REGRESSION','parentIndices':PARENTS,'rootOriginCorrectionSha256':CORRECTION_SHA,'sourceChecks':len(checks),'checks':checks,'syntaxChecks':syntax,'preparationInputs':len(rows),'publisherEdits':4,'allReverseExact':True,'actualNativeCollectionBlockUnchanged':True,'guestOrDriverOrCorpusOrNativeOrAuthorityChanged':False,'postsealActualSelfInventoryRegressionRequired':True,'bootstrapOrVerifierOrActivationOrNativeOrBundleOrGuestOrTimingExecuted':False})
 files=[{'path':path.name,'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.iterdir())if path.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_INDEXED_PEER_INVENTORY_SOURCE_PENDING_SEPARATE_READONLY_REGRESSION','files':files,'operationalAdmission':False,'actionOrGuestExecuted':False})
 print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows),'sourceChecks':len(checks),'syntaxChecks':len(syntax),'postsealReadOnlyRegressionRequired':True,'actionsExecuted':False}))
if __name__=='__main__':main()
