"""Seal exact native/tool-root separation and read-only physical regression."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PARENTS=(
 ('component-validation-indexed-peer-amendment-v1','bd66c16ce0525a23978e23e170a82cc755bdd313516e00d7e3246302f6730494',True),
 ('component-validation-indexed-peer-regression-evidence-v1','5aa0cd4ba9e9fef9b1273281fb9ad055831c39491cf6628bf5814950e7e10842',False),
 ('independent-component-validation-indexed-peer-source-review-v1','6cbe5033d7bd10e627d3a2a1a7f9e7aa9f0849008b193b60ef3d517037e44727',False),
 ('component-validation-activated-v6','8868d212f4204f9319abecbe99bd40e75eb1de1c643fcac48f496c6a0fe88fe4',True),
 ('independent-component-validation-v6-family-review-v1','999df5f84956d185831488006271ba72abcb0a211484c1cb59567676d3255fd7',False),
)
ROOT_RECEIPT='validation-source-activation-v3-root-results.json'
ROOT_SHA='6f90ae4b780ee3fbfbe31098a38bb05f58975a5d42bd61fc6a0099780c6d05d9'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode();path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb')as stream:stream.write(raw)
def regular(path,digest=None,size=None):
 path=Path(path);assert path.is_file()and not path.is_symlink();raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path;return raw
def main():
 assert len(sys.argv)==2 and not(HERE/'index.json').exists();report=json.loads(regular(sys.argv[1]));assert report['passed']==22 and report['bootstrapOrPreflightOrOwnerModuleOrToolModuleOrCompilerOrBundleOrGuestOrHostExecuted']is False;put('evidence/resolution-results.json',regular(sys.argv[1]))
 for name,count in [('activate.py',7),('runtime-preflight.template.mjs',6)]:
  proof=json.loads(regular(HERE/(name+'.proof.json')));before=regular(proof['beforePath']).decode();after=regular(HERE/name).decode();assert len(proof['edits'])==count and sha(before.encode())==proof['beforeSha256']and sha(after.encode())==proof['afterSha256'];current=before
  for row in proof['edits']:assert current.count(row['old'])==1;current=current.replace(row['old'],row['new'])
  assert current==after
  for row in reversed(proof['edits']):assert current.count(row['new'])==1;current=current.replace(row['new'],row['old'])
  assert current==before
 assert regular(HERE/'inventory.py')==regular(HERE.parent/'component-validation-indexed-peer-amendment-v1/inventory.py')
 syntax=[]
 for path in sorted(HERE.rglob('*')):
  if path.suffix=='.mjs'and path.name!='runtime-preflight.template.mjs':
   process=subprocess.run([str(NODE),'--check',str(path)],capture_output=True);assert process.returncode==0,(path,process.stderr);syntax.append({'path':str(path.relative_to(HERE)),'kind':'Node --check','status':process.returncode,'stdout':process.stdout.decode(),'stderr':process.stderr.decode()})
  elif path.suffix=='.py':ast.parse(path.read_text());syntax.append({'path':str(path.relative_to(HERE)),'kind':'Python AST'})
 # Placeholders are string contents, so the uncompiled template is syntax-checkable.
 process=subprocess.run([str(NODE),'--check',str(HERE/'runtime-preflight.template.mjs')],capture_output=True);assert process.returncode==0;syntax.append({'path':'runtime-preflight.template.mjs','kind':'Node --check','status':process.returncode,'stdout':process.stdout.decode(),'stderr':process.stderr.decode()});put('evidence/syntax-results.json',{'checks':syntax,'actionsExecuted':False})
 closure=json.loads(regular(HERE/'component-tool-closure.json'));assert closure['scope']['localModules']==9 and len(closure['files'])==17 and len(closure['packages'])==4 and len(closure['endpoints'])==5 and len(closure['packageData'])==27
 rows={}
 def add(path,digest=None,size=None):
  path=Path(path);raw=regular(path,digest,size);path=path.resolve(strict=True);row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
 for name,digest,preparation in PARENTS:
  root=HERE.parent/name;add(root/'index.json',digest)
  for row in json.loads(regular(root/'index.json',digest))['files']:add(root/row['path'],row['sha256'],row['bytes'])
  if preparation:
   for row in json.loads(regular(root/'input-freeze.json'))['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
 for group in ['files','packages','endpoints','packageData']:
  for row in closure[group]:add(row['path'],row['sha256'],row['bytes'])
 add(HERE.parent/ROOT_RECEIPT,ROOT_SHA)
 old=json.loads(regular(HERE.parent/'component-validation-activated-v6/input-freeze.json'));assert len(old['toolTrees'])==2 and len(old['toolLinks'])==22
 for name in ['component-validation-activated-v7','component-validation-activated-v7.staging']:assert not(HERE.parent/name).exists()and not(HERE.parent/name).is_symlink()
 for path in sorted(HERE.rglob('*')):
  if path.is_file():add(path)
 put('input-freeze.json',{'schemaVersion':1,'state':'FINITE_COMPONENT_TOOL_RESOLUTION_SOURCE_PREPARATION','inputs':sorted(rows.values(),key=lambda row:row['path']),'operationalAdmission':False})
 put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_NATIVE_AND_COMPONENT_TOOL_ROOT_SEPARATION_SOURCE_ONLY','parentIndices':{name:digest for name,digest,_ in PARENTS},'rootV6ActivationReceiptSha256':ROOT_SHA,'sourceChecks':report['passed'],'syntaxChecks':len(syntax),'preparationInputs':len(rows),'publisherEdits':7,'preflightEdits':6,'allReverseExact':True,'componentToolClosureSha256':sha(regular(HERE/'component-tool-closure.json')),'actualPhysicalLocalModules':9,'selectedLocalDataIncludingAdapter':8,'packageVersions':4,'packageEndpoints':5,'selectedPackageData':27,'inactiveLazyReadsExcluded':6,'originalToolTrees':2,'originalToolLinks':22,'inventoryHelperByteIdentical':True,'guestDriverCorpusNativeAndRootAuthorityUnchanged':True,'nativeConfiguredSourceRootBoundToAuthenticatedBootstrapAncestor':True,'ownerOrPackageModuleImported':False,'bootstrapOrVerifierOrPreflightOrActivationOrCompilerOrNativeOrBundleOrGuestOrHostOrTimingExecuted':False})
 files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
 put('index.json',{'schemaVersion':1,'state':'SEALED_COMPONENT_TOOL_CLOSURE_SOURCE_SUCCESSOR_NO_ACTIVATION','files':files,'operationalAdmission':False,'guestExecuted':False})
 print(json.dumps({'indexSha256':sha(regular(HERE/'index.json')),'files':len(files),'inputs':len(rows),'sourceChecks':report['passed'],'syntaxChecks':len(syntax),'actionsExecuted':False}))
if __name__=='__main__':main()
