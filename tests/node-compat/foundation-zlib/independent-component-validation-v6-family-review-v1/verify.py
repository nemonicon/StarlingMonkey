"""Independent generated-family source/data reader. No project imports/actions."""
from pathlib import Path
import hashlib,json,os,re,stat
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;REPOSITORY=FAMILY.parents[2]
GENERATED=FAMILY/'component-validation-activated-v6'
GENERATED_SHA='8868d212f4204f9319abecbe99bd40e75eb1de1c643fcac48f496c6a0fe88fe4'
PRODUCER=FAMILY/'component-validation-indexed-peer-amendment-v1'
PRODUCER_SHA='bd66c16ce0525a23978e23e170a82cc755bdd313516e00d7e3246302f6730494'
ROOT_SHA='6f90ae4b780ee3fbfbe31098a38bb05f58975a5d42bd61fc6a0099780c6d05d9'
BOOT_SHA='d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
PINS_SHA='b61e1f389b49d9e69c4bb1a3fd7b1314d16462a328627f94d141a39454b971cc'
AUTH_SHA='7274a874ffd95d975fa84c7ad7213b52ff799c06de8a717f522aa07766b975a5'
seen={};identities={}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path,h=None,size=None,capture=True,force=False):
 path=Path(path);a=path.lstat();assert stat.S_ISREG(a.st_mode)and not path.is_symlink(),path
 path=path.resolve(strict=True);key=str(path);identity=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)
 if not capture and not force and key in seen:
  assert identities[key]==identity,path;row=seen[key];assert h is None or row['sha256']==h,path;assert size is None or row['bytes']==size,path;return row
 digest=hashlib.sha256();blocks=[]if capture else None
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):
   digest.update(block)
   if capture:blocks.append(block)
 b=path.stat();assert identity==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns),path
 assert h is None or digest.hexdigest()==h,path;assert size is None or b.st_size==size,path
 row={'path':key,'sha256':digest.hexdigest(),'bytes':b.st_size};assert key not in seen or seen[key]==row,path;seen[key]=row;identities[key]=identity
 return b''.join(blocks)if capture else row
def doc(path,h=None):return json.loads(read(path,h))
def encoded(value):return(json.dumps(value,indent=2)+'\n').encode()
def indexed(root,digest,count=None):
 value=doc(root/'index.json',digest);assert count is None or len(value['files'])==count;names=set()
 for row in value['files']:
  name=row['path'];assert name not in names and not Path(name).is_absolute()and all(p not in('','.','..')for p in name.split('/'));names.add(name);read(root/name,row['sha256'],row['bytes'],False)
 return value
assert not(HERE/'results.json').exists()
index=indexed(GENERATED,GENERATED_SHA,19);indexed(PRODUCER,PRODUCER_SHA,9)
source_peer=FAMILY/'independent-component-validation-indexed-peer-source-review-v1'
indexed(source_peer,'6cbe5033d7bd10e627d3a2a1a7f9e7aa9f0849008b193b60ef3d517037e44727',9)
root=doc(FAMILY/'validation-source-activation-v3-root-results.json',ROOT_SHA)
assert root['rawExitCode']==0 and root['sourceIndexSha256']==GENERATED_SHA and root['indexedFiles']==19 and root['consumedInputs']==10964 and len(root['references'])==8
for row in root['references']:read(row['path'],row['sha256'],row['bytes'],False)
terminal=doc(root['references'][0]['path']);stdout=doc(root['references'][1]['path']);assert terminal['rawExitCode']==0
assert terminal['argv'][1]==str(PRODUCER/'activate.py')and terminal['argv'][2:4]==[PRODUCER_SHA,BOOT_SHA]
assert stdout=={'output':str(GENERATED),'indexSha256':GENERATED_SHA,'guestExecuted':False,'operationalAdmission':False}
assert read(root['references'][2]['path'])==b''
manifest=doc(GENERATED/'input-freeze.json');assert len(manifest['inputs'])==10964 and len(manifest['toolTrees'])==2 and len(manifest['toolLinks'])==22
assert encoded(manifest)==read(GENERATED/'input-freeze.json')
by_path={};relative=[]
for row in manifest['inputs']:
 name=row['path'];assert name not in by_path;by_path[name]=row
 if Path(name).is_absolute():assert 'boundary'not in row
 else:assert row['boundary']=='.'and name==Path(name).name;relative.append(name)
 read(GENERATED/name,row['sha256'],row['bytes'],False)
assert len(relative)==16 and len(by_path)-len(relative)==10948
tools=doc(FAMILY/'component-validation-candidate-v1/tool-seal.json')
assert all(manifest[k]==tools[k]for k in['toolTrees','toolLinks','invocation'])
tool_regular=0
for tree in manifest['toolTrees']:
 tree_root=Path(tree['path']);assert str(tree_root.resolve(strict=True))==tree['realPath'];members=[]
 for directory,dirs,files in os.walk(tree_root,followlinks=False):
  for name in sorted(dirs+files):
   path=Path(directory)/name;kind='symlink'if path.is_symlink()else'directory'if path.is_dir()else'file'if path.is_file()else None;assert kind
   members.append({'path':str(path.relative_to(tree_root)),'kind':kind})
   if kind=='file':
    tool_regular+=1;canonical=str(path.resolve(strict=True));assert canonical in by_path;row=by_path[canonical];read(path,row['sha256'],row['bytes'],False)
  dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
 assert sorted(members,key=lambda row:row['path'])==tree['entries']
for row in manifest['toolLinks']:
 path=Path(row['path']);assert path.is_symlink()and os.readlink(path)==row['linkText']and str(path.resolve(strict=True))==row['resolvedTarget']
 target=Path(row['resolvedTarget']);assert('directory'if target.is_dir()else'file'if target.is_file()else None)==row['targetKind']
 if row['targetKind']=='file':read(target,row['targetSha256'],row['targetBytes'],False)
assert tool_regular==4890
config=doc(GENERATED/'activation.json');receipt=doc(GENERATED/'source-receipt.json');pins=doc(GENERATED/'reviewed-pins.json',PINS_SHA);authority=doc(GENERATED/'root-review.json',AUTH_SHA)
assert read(GENERATED/'reviewed-pins.json')==read(FAMILY/'reviewed-native-v4-validation-bootstrap-pins-v1.json',PINS_SHA)
assert read(GENERATED/'root-review.json')==read(FAMILY/'native-v4-validation-bootstrap-root-review-v1.json',AUTH_SHA)
assert config['operationalAdmission']is receipt['operationalAdmission']is receipt['guestExecuted']is False
assert config['actual']==receipt['actual']==root['actual']and config['headers']==root['headers']
assert config['pinsSha256']==PINS_SHA and config['rootReviewSha256']==AUTH_SHA and config['bootstrapIndexSha256']==BOOT_SHA
native_root=Path(config['toolSourceRoot']);bootstrap=Path(config['bootstrapRoot']);original=FAMILY/'native-integration-candidate-v4'
assert native_root==Path('/tmp/starling-node-compat/zlib-source-v4').resolve()and bootstrap==native_root/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
assert receipt['bootstrapPreparationRoot']==str(original)
assert indexed(bootstrap,BOOT_SHA,85)==indexed(original,BOOT_SHA,85)
prep=doc(original/'input-freeze.json');assert len(prep['inputs'])==2261 and prep['relocatedActionsMustNotReinterpretThesePaths']is True
for row in prep['inputs']:read(original/row['path'],row['sha256'],row['bytes'],False)
row0=prep['inputs'][0];assert not(bootstrap/row0['path']).resolve().exists();read(original/row0['path'],row0['sha256'],row0['bytes'],False)
previous_inventory=doc(FAMILY/'component-validation-indexed-peer-regression-evidence-v1/results.json','d29787dfb296744fcfc3ea6328d87a8788419324097a4d25d2e29f828986f73b')
assert receipt['inventoryFamilies']==previous_inventory['families']and len(previous_inventory['consumedFiles'])==8904
for row in previous_inventory['consumedFiles']:
 assert by_path[row['path']]==row;read(row['path'],row['sha256'],row['bytes'],False)
assert receipt['producerIndexSha256']==receipt['mandatoryIndexedPeerInventoryAmendmentIndexSha256']==PRODUCER_SHA
assert receipt['mandatoryPreparationContextAmendmentIndexSha256']=='f6f0e1916d02445a0c7e2fc60b0b31b26ef19aef210d59a9964ba77dfcefdee9'
assert pins['variants']['normal-runtime']is None and authority['operationalAdmission']is False and authority['validationBootstrapOnly']is True
assert authority['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
tool_pins=doc(bootstrap/'artifact-tools/tool-pins.json');assert len(tool_pins['toolDependencies'])==632
for row in tool_pins['toolDependencies']:read(native_root/row['path'],row['sha256'],row['bytes'],False)
native_tuples={};inferred_headers={}
for variant in['normal-off','gc-off','disabled-off']:
 pin=pins['variants'][variant];assert len(pin['frozenFiles'])==1024
 read(pin['enginePath'],pin['engineSha256'],pin['engineBytes'],False)
 for row in pin['frozenFiles']:read(row['path'],row['sha256'],row['bytes'],False)
 freeze=doc(Path(pin['freezeReceiptPath']),pin['freezeReceiptSha256']);meta=doc(Path(str(pin['enginePath'])+'.build.json'),pin['receiptSha256'])
 assert freeze['runtimeBackendProof']==meta['zlibPolicy']['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
 assert len(meta['sourceManifest'])==350
 for row in meta['sourceManifest']:read(native_root/row['path'],row['sha256'],capture=False)
 actual={key:pin[key]for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']}
 for key,value in actual.items():assert config['actual'][variant][key]==authority['variants'][variant][key]==value
 native_tuples[variant]=actual
 if variant!='disabled-off':
  primary=[row for row in meta['zlibPolicy']['codecWitness']['headers']if Path(row['path']).name=='zlib.h'];assert len(primary)==1
  frozen=[row for row in freeze['copies']if row['original']==primary[0]['path']];assert len(frozen)==1
  text=read(frozen[0]['path'],primary[0]['sha256']).decode();version=re.search(r'^#define ZLIB_VERSION\s+"([^"]+)"',text,re.M);vernum=re.search(r'^#define ZLIB_VERNUM\s+(0x[0-9a-fA-F]+|[0-9]+)',text,re.M);assert version and vernum
  kernel=[row for row in meta['sourceManifest']if row['path']=='builtins/node-compat/zlib/kernel.cpp'];assert len(kernel)==1
  expected={'versionText':version.group(1),'vernum':int(vernum.group(1),0),'headerSha256':primary[0]['sha256'],'kernelSha256':kernel[0]['sha256'],'inferenceOnly':True,'privateBackendInfoObserved':False};assert config['headers'][variant]==expected;inferred_headers[variant]=expected
base=FAMILY/'component-validation-candidate-v1';coverage=FAMILY/'component-validation-bootstrap-coverage-amendment-v1'
payload_names=['canonical-require.cjs','consumed.mjs','corpus.mjs','node-fixtures.mjs','node-results.json','profile-contract.mjs','profile-contract.json','durable-host.mjs','runtime-preflight.template.mjs','future-authority.json']
for name in payload_names:assert read(GENERATED/name)==read(base/name)
for name,source in [('component.mjs',coverage/'proposed/component.mjs'),('run-validation.mjs',coverage/'proposed/run-validation.mjs'),('coverage-checks.mjs',coverage/'coverage-checks.mjs')]:assert read(GENERATED/name)==read(source)
template=read(GENERATED/'runtime-preflight.template.mjs').decode()
for key,value in{'CONFIG_SHA':sha(read(GENERATED/'activation.json')),'INPUTS_SHA':sha(read(GENERATED/'input-freeze.json'))}.items():assert template.count('@'+key+'@')==1;template=template.replace('@'+key+'@',value)
assert template.encode()==read(GENERATED/'runtime-preflight.mjs')
assert doc(GENERATED/'future-authority.json')['operationalAdmission']is False
contract=doc(GENERATED/'profile-contract.json');assert len(contract['exports'])==40 and len(contract['sync'])==6
assert len(doc(GENERATED/'node-results.json')['cases'])==61

# Executability is a distinct gate from exact indexed/consumed bytes.
driver=read(GENERATED/'run-validation.mjs').decode();assert 'const root=admission.toolSourceRoot'in driver
primary_loaders=re.findall(r"await import\(pathToFileURL\(join\(root,'([^']+)'\)\)\)",driver)
assert primary_loaders==['tests/node-compat/toolchain.mjs','tests/node-compat/componentizer.mjs','tests/node-compat/profile-bundler.mjs','tests/node-compat/foundations/native-scalar-harness.mjs']
missing=[]
for name in primary_loaders:
 path=native_root/name;original_path=REPOSITORY/name;assert not path.exists()and not path.is_symlink()
 assert str(path)not in by_path and str(original_path)not in by_path
 read(original_path,capture=False)
 missing.append({'relativePath':name,'resolvedGeneratedPath':str(path),'exists':False,'manifestContainsGeneratedPath':False,'manifestContainsOriginalPath':False,'originalPath':str(original_path),'originalSha256':seen[str(original_path)]['sha256'],'originalBytes':seen[str(original_path)]['bytes']})
assert driver.index("join(root,'tests/node-compat/toolchain.mjs')")<driver.index('await mkdir(output)')
static_graph={};queue=[REPOSITORY/name for name in primary_loaders]
while queue:
 path=queue.pop(0).resolve();name=str(path.relative_to(REPOSITORY))
 if name in static_graph:continue
 code=read(path).decode();dependencies=[]
 for match in re.finditer(r"^import\s+[^;]*?\s+from\s+['\"]([^'\"]+)['\"]",code,re.M):
  spec=match.group(1)
  if spec.startswith('.'):
   target=(path.parent/spec).resolve();dependencies.append(str(target.relative_to(REPOSITORY)));queue.append(target)
 static_graph[name]=dependencies
assert len(static_graph)==9
data_names=['tests/node-compat/wasi-0.2.10-interfaces.json','builtins/node-compat/manifest.schema.json','builtins/node-compat/export-manifest.node-v22.14.0.json','tests/node-compat/legacy-stream-web-receipts.json','tests/node-compat/oom/componentize-clock-errno-v2.patch','tests/node-compat/abi-fix/componentize-import-i32-v1.patch','tests/node-compat/abi-fix/splicer-Cargo.v1.lock']
data_boundary=[]
for name in data_names:
 row=read(REPOSITORY/name,capture=False);data_boundary.append({'relativePath':name,'originalSha256':row['sha256'],'originalBytes':row['bytes'],'generatedNativeStageExists':(native_root/name).is_file(),'originalPathManifested':str(REPOSITORY/name)in by_path})
assert 'builtinManifests:admission.selectedManifests'in driver
assert 'selectedInterfaces:[]'in driver and "preview2Adapter:adapter"in driver
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'],False,True)
result={'schemaVersion':1,'state':'INDEPENDENT_ZLIB350_GENERATED_V6_FAMILY_HOLD_MISSING_COMPONENT_TOOL_CLOSURE','generatedIndexSha256':GENERATED_SHA,'generatedIndexedFiles':19,'consumedRowsRehashed':10964,'absoluteConsumedRows':10948,'relativeSealedPayloadRows':16,'toolTrees':2,'toolLinks':22,'toolRegularFilesCovered':4890,'sourcePayloadCopiesByteExact':13,'runtimePreflightTemplateReconstructed':True,'producerIndexSha256':PRODUCER_SHA,'producerSixFamilyInventoryRowsPreserved':8904,'originalAndStagedBootstrapIndexedFiles':85,'originalPreparationRowsRehashed':2261,'actualSourceNative350AndTool632Rehashed':True,'nativeFrozenCopiesPerVariant':1024,'actualNativeTuples':native_tuples,'headerVersionInferenceOnly':inferred_headers,'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},'existingRootPinsSha256':PINS_SHA,'existingRootReviewSha256':AUTH_SHA,'rootActivationReceiptSha256':ROOT_SHA,'rootReportedActivationTerminal':0,'observedPastRootTerminalByThisReader':False,'rootReceiptReferencesRehashed':8,'guestAttemptOrResultClaimed':False,'concreteSourceBlockers':[{'id':'ZV6-M1','scope':'Generated component tool root has no required harness loaders or sealed harness closure','declaredToolSourceRoot':str(native_root),'missingPrimaryLoaders':missing,'effect':'Even if validation preflight completes, the first dynamic toolchain import cannot resolve; the driver has not reached output creation, bundling or guest execution.','requiredCorrection':'Use an explicit separately authenticated component harness root/closure or a reviewed additional stage. Retain actual configured native source root and genuine bootstrap-selected350 manifests; do not project changed source under old native authority.'}],'staticLocalHarnessGraphAtOriginalRoot':static_graph,'knownImportTimeAndSelectedPackagingDataBoundary':data_boundary,'lazyAdmissionDataMustBeAssessedBySuccessor':True,'operationalAdmission':False,'generatedFamilyReadyForGuest':False,'ownerImportsHelpersPreflightsActionsNativeCompilerNodeGuestHostOrTimingExecuted':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({'state':result['state'],'indexed':19,'consumed':10964,'verifiedPaths':len(seen),'blockers':1,'missingPrimaryLoaders':4}))
