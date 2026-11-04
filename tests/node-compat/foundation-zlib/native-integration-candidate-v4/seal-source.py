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
 assert HERE==Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-zlib/native-integration-candidate-v4')
 assert not(HERE/'index.json').exists()
 parents={'../integration-candidate-v1':'56a6ee5fecc921ce78e4c4402761c9fc790487eb6f2deeb6297c12cf3597fd2d',
  '../independent-integration-source-review-v1':'bfaf3aa2ef3b06d6b93e056dff7bd1dfd8e6de5048fe8712c64aa41dd373a112',
  '../sdk-syntax-v1':'e7579d660126ab6688519f883ea76a3ac123b3e1f10368c7f1dd2b409f3b5682',
  '../independent-sdk-syntax-review-v1':'4ef48706dad6c487ab8d85865cdc5b5477c55d0d3ea3e23d2ba1e41979607d0d',
  '../../foundation-classic-streams/trace-integration-candidate-v1':'224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b',
  '../native-integration-candidate-v1':'3ff3a59d4fc1fafa32b2ba1e6ec5a1b8d7787f4e7eca1ee6855d7b38cc7c45db',
  '../independent-native-integration-source-review-v1':'dafaff07578be6f62883ddf0815c023f4ba0e12b0c5b1e6ab5899d4f0edb474c',
  '../forced-include-amendment-v1':'1d0c8626665c06247f4240be359704a2c10851489cb77e203f14ae511343c58c',
  '../native-integration-candidate-v2':'c65ed2c400b49e63d716ba92b05d0b5f0f56680f6a89d94a9b2c813faec0aba1',
  '../descriptor-shadow-amendment-v1':'c92e09b73f863dc9075b8d465b1804b8d8fd670dbff125f3188747c044190d37',
  '../independent-native-integration-v2-source-review-v1':'89bc84d69c17b3959105ef1776c3275981b3bdace2aca7de64a355a1e6aabe1b',
  '../native-integration-candidate-v3':'3929e24d4fe423dc388d3706b975c4704739943b7fcf78c49feb8fda79e03710',
  '../independent-native-integration-v3-source-review-v1':'f471ec276ce05ef3d80c90af8a30da25933663452dec2b9728ebc111a3a0013e',
  '../compound-link-parser-amendment-v1':'18ee1ab685fbafd331ad10eabe5c16352532bac83cee56181c75356f7e46ebdb',
  '../independent-native-zlib-v3-build-failure-review-v1':'c319335168016fcc40ec2b04548e82a3fd171972dcc3a488f30bbb0ffcecb4ce'}
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
 for row in json.loads((HERE/'evidence/actual-command-python.json').read_bytes())['actualInputs']:add(row['path'],row['sha256'],row['bytes'])
 link_capture=json.loads((HERE/'evidence/link-chain-tests.json').read_bytes())['actualCapture'];add(link_capture['path'],link_capture['sha256'],link_capture['bytes'])
 for path in ['/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/normal-off.engine.wasm.build.json','/tmp/starling-node-compat/production-scheduler-artifacts-v1/native-freeze/normal-off.engine.wasm.build.json',
  str(REPO/'tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-trace-runtime-pins-v1.json'),'/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node']:add(path)
 for path in HERE.rglob('*'):
  if path.is_file()and '__pycache__'not in path.parts and path.name not in ['index.json','input-freeze.json','source-receipt.json']:add(path)
 tool_count=len(json.loads((HERE/'artifact-tools/tool-pins.json').read_bytes())['toolDependencies'])
 write('input-freeze.json',{'schemaVersion':1,'state':'ORIGINAL_CONTEXT_PREPARATION_INPUTS_ONLY','originalPreparationRoot':str(HERE),'relocatedActionsMustNotReinterpretThesePaths':True,'inputs':[inputs[key]for key in sorted(inputs)],'nativeInputCount':350,'toolDependencyCount':tool_count,'priorSyntaxDependencies':1048})
 policy=json.loads((HERE/'policy.json').read_bytes());contract=json.loads((HERE/'admission-pins.json').read_bytes())
 checks={name:json.loads((HERE/'evidence'/name).read_bytes())for name in ['policy-tests.json','node-tests.json','bootstrap-tests.json','bootstrap-node-tests.json','syntax-tests.json','generator-check.json','actual-command-python.json','actual-command-node.json','after-contract-tests.json','link-chain-tests.json']}
 receipt={'schemaVersion':1,'state':'SEALED_UNAPPLIED_ZLIB350_NATIVE_PRODUCER_SOURCE','sourceOnly':True,'nativeOrGuestOrActionExecuted':False,
  'nativeSourceFiles':350,'parentNativeSourceFiles':342,'nativeAdds':8,'nativeParentChanges':2,'unchangedParentPaths':340,
  'finiteActiveCPP':{'zlibON':62,'zlibOFF':61},'finitePrivateTargetCPP':{'zlibON':6,'zlibOFF':5},'externalEmbeddingSources':3,
  'parentIndices':parents,'recipeSha256':contract['productionRecipeSha256'],'policySha256':contract['policySha256'],'helperSha256':contract['helperSha256'],
  'toolDependencies':tool_count,'inputManifestSha256':sha(HERE/'input-freeze.json'),'preparationInputs':len(inputs),'derivationProofs':proofs,'patchSha256':sha(HERE/'native-integration.UNAPPLIED.patch'),
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
