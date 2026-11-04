"""Read-only real preparation-context regression and immutable source seal."""
from pathlib import Path
import ast,hashlib,json,sys
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'component-validation-v4-rebind-amendment-v1'
ORIGINAL=HERE.parent/'native-integration-candidate-v4'
STAGED=Path('/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/foundation-zlib/native-integration-candidate-v4')
BOOT_SHA='d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
PARENTS={
 'component-validation-v4-rebind-amendment-v1':'cd45865813e06085dcd86065bf816dd18b8203d127df879b1b1e2ca876662a45',
 'independent-component-validation-v4-rebind-source-review-v1':'74109e3fb4082c813592d0af340f21f4888c5d9e9b29e5d91cb77dd2e79d2f62',
 'native-integration-candidate-v4':BOOT_SHA,
}
FAILURE='validation-source-activation-attempt2-context-failure-root-results.json'
FAILURE_SHA='3ff30ff1d5ba07fa714cdb9061461df9a0d60a7f8205550aa26e5cc9bdcb9a35'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 with(HERE/name).open('xb')as stream:stream.write((json.dumps(value,indent=2)+'\n').encode())
def regular(path,digest=None,size=None):
 path=Path(path);assert path.is_file()and not path.is_symlink();raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path;return raw
def main():
 assert len(sys.argv)==1 and not(HERE/'index.json').exists();checks=[];proof=json.loads(regular(HERE/'publisher-proof.json'));before=regular(BASE/'activate.py').decode();after=regular(HERE/'activate.py').decode();assert sha(before.encode())==proof['beforeSha256']and sha(after.encode())==proof['afterSha256']and len(proof['edits'])==4;current=before
 for row in proof['edits']:assert current.count(row['old'])==1;current=current.replace(row['old'],row['new']);checks.append('exact forward publisher edit '+str(len(checks)+1))
 assert current==after
 for row in reversed(proof['edits']):assert current.count(row['new'])==1;current=current.replace(row['new'],row['old'])
 assert current==before;checks.append('all four reverse exactly')
 syntax=[]
 for path in sorted(HERE.glob('*.py')):ast.parse(path.read_text());syntax.append({'path':path.name,'kind':'Python AST','sha256':sha(path.read_bytes())})
 original_index=regular(ORIGINAL/'index.json',BOOT_SHA);staged_index=regular(STAGED/'index.json',BOOT_SHA);assert original_index==staged_index;original_rows=json.loads(original_index)['files'];assert len(original_rows)==85
 for row in original_rows:
  left=regular(ORIGINAL/row['path'],row['sha256'],row['bytes']);right=regular(STAGED/row['path'],row['sha256'],row['bytes']);assert left==right
 checks.append('original/staged d384 and all85 indexed files byte-identical')
 original_manifest=regular(ORIGINAL/'input-freeze.json');assert original_manifest==regular(STAGED/'input-freeze.json');manifest=json.loads(original_manifest);assert len(manifest['inputs'])==2261
 first=manifest['inputs'][0];assert first['path']=='../../foundation-classic-streams/production-adoption-v1/reviewed-trace-runtime-pins-v1.json';incorrect=(STAGED/first['path']).resolve();correct=(ORIGINAL/first['path']).resolve();assert not incorrect.exists()and not incorrect.is_symlink();regular(correct,first['sha256'],first['bytes']);checks.append('actual row0 missing at incorrect staged resolution and exact at original root')
 for row in manifest['inputs']:regular(ORIGINAL/row['path'],row['sha256'],row['bytes'])
 checks.append('all2261 original-context preparation rows rehash exactly')
 assert after.index('original_boot_rows=indexed(ORIGINAL_BOOTSTRAP,bootstrap_sha)')<after.index('spec_from_file_location');checks.append('both indexed views authenticated before staged genuine helper import')
 assert "preparation_root=ORIGINAL_BOOTSTRAP if root==bootstrap else root"in after and"regular(preparation_root/'input-freeze.json')"in after and"add(preparation_root/row['path']"in after;checks.append('only historical bootstrap preparation uses original context')
 def actual_block(text):return text[text.index(' actual={};headers={};inputs={}'):text.index(" names=['component.mjs'")]
 assert actual_block(before)==actual_block(after);checks.append('actual bootstrap/source350/tool632/frozen/header collection block unchanged')
 assert "spec_from_file_location('actual_zlib350_validation_bootstrap',bootstrap/"in after and 'current==DECLARED.resolve(strict=True)'in after;checks.append('actual staged bootstrap/configured source guard retained')
 for name in ['component-validation-activated-v5','component-validation-activated-v5.staging']:assert not(HERE.parent/name).exists()and not(HERE.parent/name).is_symlink()
 checks.append('new final and staging outputs absent')
 failure_raw=regular(HERE.parent/FAILURE,FAILURE_SHA);failure=json.loads(failure_raw);assert failure['rawOuterExit']==1 and failure['validationSourcePublished']is False and failure['guestExecuted']is False
 for row in failure['evidence']:regular(row['path'],row['sha256'],row['bytes'])
 checks.append('Root failed publication history and3 raw witnesses preserved')
 put('context-regression.json',{'schemaVersion':1,'state':'READ_ONLY_ACTUAL_PREPARATION_CONTEXT_REGRESSION_PASSED','bootstrapIndexSha256':BOOT_SHA,'originalBootstrapRoot':str(ORIGINAL.resolve()),'actualStagedBootstrapRoot':str(STAGED.resolve()),'indexedFilesPerView':85,'bothIndexedViewsByteIdentical':True,'preparationRowsVerifiedAtOriginalRoot':2261,'preparationManifestSha256':sha(original_manifest),'row0':{**first,'incorrectStagedPath':str(incorrect),'incorrectStagedPathAbsent':True,'originalPath':str(correct),'originalBytesVerified':True},'actualSourceCollectionBlockSha256':sha(actual_block(after).encode()),'originalGuestAndDriverPayloadsUnchanged':True,'bootstrapOrVerifierOrActivationOrBuildOrGuestExecuted':False})
 put('syntax-results.json',{'checks':syntax,'actionExecuted':False})
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);raw=regular(path,digest,size);path=path.resolve(strict=True);row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 for name,digest in PARENTS.items():
  parent=HERE.parent/name;add(parent/'index.json',digest)
  for row in json.loads(regular(parent/'index.json',digest))['files']:add(parent/row['path'],row['sha256'],row['bytes'])
  if(parent/'input-freeze.json').exists():
   for row in json.loads(regular(parent/'input-freeze.json'))['inputs']:add(parent/row['path'],row['sha256'],row['bytes'])
 add(STAGED/'index.json',BOOT_SHA)
 for row in original_rows:add(STAGED/row['path'],row['sha256'],row['bytes'])
 add(HERE.parent/FAILURE,FAILURE_SHA)
 for row in failure['evidence']:add(row['path'],row['sha256'],row['bytes'])
 for path in sorted(HERE.iterdir()):
  if path.is_file():add(path)
 put('input-freeze.json',{'schemaVersion':1,'state':'ZLIB_VALIDATION_ORIGINAL_PREPARATION_CONTEXT_SOURCE_ONLY','inputs':sorted(rows.values(),key=lambda row:row['path']),'activationOrGuestExecuted':False})
 put('results.json',{'schemaVersion':1,'state':'MANDATORY_ZLIB_VALIDATION_PREPARATION_CONTEXT_SOURCE_CORRECTION_PASSED','checks':checks,'sourceChecks':len(checks),'syntaxChecks':len(syntax),'publisherEdits':4,'allReverseExact':True,'parentIndices':PARENTS,'failureReceiptSha256':FAILURE_SHA,'originalBootstrapPreparationRowsVerified':2261,'stagedAndOriginalIndexedFilesPerView':85,'preparationInputs':len(rows),'guestOrDriverOrCorpusOrNativeOrRootAuthorityChanged':False,'activationOrBootstrapOrVerifierOrNativeOrBundleOrGuestOrHostOrTimingExecuted':False})
 files=[{'path':path.name,'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.iterdir())if path.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_ZLIB_VALIDATION_PREPARATION_CONTEXT_SOURCE_AMENDMENT','files':files,'operationalAdmission':False,'activationOrGuestExecuted':False})
 print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows),'sourceChecks':len(checks),'syntaxChecks':len(syntax),'actionsExecuted':False}))
if __name__=='__main__':main()
