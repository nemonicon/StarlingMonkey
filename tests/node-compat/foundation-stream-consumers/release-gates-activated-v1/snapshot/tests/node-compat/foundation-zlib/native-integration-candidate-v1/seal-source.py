"""Seal this finite SOURCE proposal in its original preparation context only."""
import ast,difflib,hashlib,importlib.util,json,os,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb')as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def data_sha(data):return hashlib.sha256(data).hexdigest()
def write(name,value):
 path=HERE/name;assert not path.exists()and not path.is_symlink(),str(path)
 path.write_text(json.dumps(value,indent=2)+'\n')
def main():
 assert HERE==Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-zlib/native-integration-candidate-v1')
 assert not(HERE/'index.json').exists()
 parents={'../integration-candidate-v1':'56a6ee5fecc921ce78e4c4402761c9fc790487eb6f2deeb6297c12cf3597fd2d',
  '../independent-integration-source-review-v1':'bfaf3aa2ef3b06d6b93e056dff7bd1dfd8e6de5048fe8712c64aa41dd373a112',
  '../sdk-syntax-v1':'e7579d660126ab6688519f883ea76a3ac123b3e1f10368c7f1dd2b409f3b5682',
  '../independent-sdk-syntax-review-v1':'4ef48706dad6c487ab8d85865cdc5b5477c55d0d3ea3e23d2ba1e41979607d0d',
  '../../foundation-classic-streams/trace-integration-candidate-v1':'224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b'}
 for name,digest in parents.items():
  base=(HERE/name).resolve();assert sha(base/'index.json')==digest
  for row in json.loads((base/'index.json').read_bytes())['files']:assert sha(base/row['path'])==row['sha256']and(base/row['path']).stat().st_size==row['bytes']
 proofs=[]
 for name in ['source-transformations.json','tool-transformations.json','model-transformations.json']:
  document=json.loads((HERE/name).read_bytes())
  for record in document['records']:
   before=(REPO/record['origin']).read_text();assert data_sha(before.encode())==record['beforeSha256'];value=before
   for edit in record['edits']:
    for at in edit['afterOffsets']:
     assert value[at:at+len(edit['old'])]==edit['old'];value=value[:at]+edit['new']+value[at+len(edit['old']):]
   assert value==(HERE/record['path']).read_text()and data_sha(value.encode())==record['afterSha256']
   for edit in reversed(record['edits']):
    for at in reversed(edit['afterOffsets']):
     assert value[at:at+len(edit['new'])]==edit['new'];value=value[:at]+edit['old']+value[at+len(edit['new']):]
   assert value==before;proofs.append({'proof':name,'path':record['path'],'forwardAndReverseExact':True})
 # Build one complete patch against genuine corrected342 source/tool preimages.
 corrected=Path('/tmp/starling-node-compat/classic-trace-source-v1');patch=[];patch_rows=[]
 for after in sorted((HERE/'source').rglob('*')):
  if not after.is_file():continue
  relative=str(after.relative_to(HERE/'source'));old=corrected/relative
  before=old.read_text()if old.exists()else'';new=after.read_text()
  patch.extend(difflib.unified_diff(before.splitlines(True),new.splitlines(True),fromfile='a/'+relative if old.exists()else'/dev/null',tofile='b/'+relative))
  patch_rows.append({'path':relative,'beforeSha256':data_sha(before.encode())if old.exists()else None,'afterSha256':sha(after)})
 path=HERE/'native-integration.UNAPPLIED.patch';assert not path.exists();path.write_text(''.join(patch))
 write('patch-manifest.json',{'schemaVersion':1,'base':'actual corrected342 source/tool bytes','files':patch_rows,'nativeAdds':8,'nativeParentChanges':2,'sourceOnly':True})
 spec=importlib.util.spec_from_file_location('zlib_source_stage_plan',HERE/'stage-source.py');stage=importlib.util.module_from_spec(spec);spec.loader.exec_module(stage)
 plan=stage.source_plan();inputs={}
 def add(path,expected=None,size=None):
  path=Path(path);assert path.is_file()and not path.is_symlink(),str(path)
  digest=sha(path)
  if expected is not None:assert digest==expected,str(path)
  if size is not None:assert path.stat().st_size==size
  key=str(path.absolute());inputs[key]={'path':os.path.relpath(path,HERE),'sha256':digest,'bytes':path.stat().st_size}
 for row in plan:add(row['source'],row['sha256'],row['bytes'])
 for name in parents:
  base=(HERE/name).resolve();add(base/'index.json')
  for row in json.loads((base/'index.json').read_bytes())['files']:add(base/row['path'],row['sha256'],row['bytes'])
 # Independent proof already distinguishes2 CPP+1046 headers. These are original
 # context references, not new350 inputs or relocated build dependencies.
 dependencies=json.loads((HERE/'../sdk-syntax-v1/header-dependencies.json').read_bytes())['files'];assert len(dependencies)==1048
 for row in dependencies:add(Path(row['resolvedPath']),row['sha256'],row['bytes'])
 for path in HERE.rglob('*'):
  if path.is_file()and '__pycache__'not in path.parts and path.name not in ['index.json','input-freeze.json','source-receipt.json']:add(path)
 write('input-freeze.json',{'schemaVersion':1,'state':'ORIGINAL_CONTEXT_PREPARATION_INPUTS_ONLY','originalPreparationRoot':str(HERE),'relocatedActionsMustNotReinterpretThesePaths':True,'inputs':[inputs[key]for key in sorted(inputs)],'nativeInputCount':350,'toolDependencyCount':335,'priorSyntaxDependencies':1048})
 policy=json.loads((HERE/'policy.json').read_bytes());contract=json.loads((HERE/'admission-pins.json').read_bytes())
 checks={name:json.loads((HERE/'evidence'/name).read_bytes())for name in ['policy-tests.json','node-tests.json','bootstrap-tests.json','bootstrap-node-tests.json','syntax-tests.json','generator-check.json']}
 receipt={'schemaVersion':1,'state':'SEALED_UNAPPLIED_ZLIB350_NATIVE_PRODUCER_SOURCE','sourceOnly':True,'nativeOrGuestOrActionExecuted':False,
  'nativeSourceFiles':350,'parentNativeSourceFiles':342,'nativeAdds':8,'nativeParentChanges':2,'unchangedParentPaths':340,
  'finiteActiveCPP':{'zlibON':62,'zlibOFF':61},'finitePrivateTargetCPP':{'zlibON':6,'zlibOFF':5},'externalEmbeddingSources':3,
  'parentIndices':parents,'recipeSha256':contract['productionRecipeSha256'],'policySha256':contract['policySha256'],'helperSha256':contract['helperSha256'],
  'toolDependencies':335,'inputManifestSha256':sha(HERE/'input-freeze.json'),'preparationInputs':len(inputs),'derivationProofs':proofs,'patchSha256':sha(HERE/'native-integration.UNAPPLIED.patch'),
  'checks':{name:value.get('count',value.get('checks'))for name,value in checks.items()},'sdkSyntaxEvidence':'e757+4ef487 unchanged parent syntax0;2CPP+1046headers, not link/runtime',
  'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},'runtimeEnginePins':None,'validationBootstrapPins':None,'operationalAdmission':'CLOSED for every hinted350 receipt',
  'futureActualLinkShape':'Unobserved; fail closed','runtimeAcceptanceClaim':False,'performanceClaim':False}
 write('source-receipt.json',receipt)
 files=[]
 for path in sorted(HERE.rglob('*')):
  if path.is_file()and '__pycache__'not in path.parts and path.name!='index.json':files.append({'path':str(path.relative_to(HERE)),'sha256':sha(path),'bytes':path.stat().st_size})
 write('index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_ZLIB350_NATIVE_INTEGRATION_CANDIDATE','files':files})
 print(json.dumps({'indexSha256':sha(HERE/'index.json'),'files':len(files),'preparationInputs':len(inputs),'recipeSha256':contract['productionRecipeSha256']}))
if __name__=='__main__':main()
