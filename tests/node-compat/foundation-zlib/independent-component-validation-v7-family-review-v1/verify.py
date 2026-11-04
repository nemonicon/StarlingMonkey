"""Independent deterministic source-family reader. No project imports/actions."""
from pathlib import Path
import hashlib,json,os,re,stat
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;REPO=FAMILY.parents[2]
GENERATED=FAMILY/'component-validation-activated-v7'
GENERATED_SHA='d67971d0fbf2e116c646a0411bf3ffc4d3209475033c2d2209c443deb9802c9e'
PRODUCER=FAMILY/'component-validation-tooling-closure-amendment-v1'
PRODUCER_SHA='daa7d28a7105f878a9465c4eb0fea2edaa3ef6329a15baafcabd7ccc28a0fd0c'
ROOT_SHA='80d3e8e373cad4a61240c27655ab91329e1ada85af168d14c517924cda3f121c'
BOOT=FAMILY/'native-integration-candidate-v4';BOOT_SHA='d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
PINS_SHA='b61e1f389b49d9e69c4bb1a3fd7b1314d16462a328627f94d141a39454b971cc';AUTH_SHA='7274a874ffd95d975fa84c7ad7213b52ff799c06de8a717f522aa07766b975a5'
NATIVE=Path('/tmp/starling-node-compat/zlib-source-v4').resolve();STAGED=NATIVE/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
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
generated_index=indexed(GENERATED,GENERATED_SHA,21);indexed(PRODUCER,PRODUCER_SHA,15)
source_peer=FAMILY/'independent-component-validation-tooling-closure-source-review-v1';indexed(source_peer,'567c3214f43e3794a1d6bb2ce9c8a13c72c927b7476f643e7913ca184fad765f',9)
root=doc(FAMILY/'validation-source-activation-v4-root-results.json',ROOT_SHA)
assert root['sourceIndexSha256']==GENERATED_SHA and root['rawExitCode']==0 and root['indexedFiles']==21 and root['consumedInputs']==11036 and len(root['references'])==10
for row in root['references']:read(row['path'],row['sha256'],row['bytes'],False)
terminal=doc(root['references'][0]['path']);stdout=doc(root['references'][1]['path']);assert terminal['rawExitCode']==0
assert terminal['argv'][1]==str(PRODUCER/'activate.py')and terminal['argv'][2:4]==[PRODUCER_SHA,BOOT_SHA]
assert stdout=={'output':str(GENERATED),'indexSha256':GENERATED_SHA,'guestExecuted':False,'operationalAdmission':False}and read(root['references'][2]['path'])==b''
actual_manifest=doc(GENERATED/'input-freeze.json');assert len(actual_manifest['inputs'])==11036 and len(actual_manifest['toolTrees'])==2 and len(actual_manifest['toolLinks'])==22
by_path={}
for row in actual_manifest['inputs']:
 assert row['path']not in by_path;by_path[row['path']]=row;read(GENERATED/row['path'],row['sha256'],row['bytes'],False)
relative=[row for row in actual_manifest['inputs']if not Path(row['path']).is_absolute()];assert len(relative)==18 and all(row['boundary']=='.'and row['path']==Path(row['path']).name for row in relative)
config=doc(GENERATED/'activation.json');receipt=doc(GENERATED/'source-receipt.json')
assert config['nativeConfiguredSourceRoot']==receipt['nativeConfiguredSourceRoot']==root['nativeConfiguredSourceRoot']==str(NATIVE)
assert config['componentToolRoot']==receipt['componentToolRoot']==root['componentToolRoot']==str(REPO)and NATIVE!=REPO
assert Path(config['bootstrapRoot'])==STAGED and STAGED.parents[3]==NATIVE
assert config['bootstrapIndexSha256']==BOOT_SHA and config['pinsSha256']==PINS_SHA and config['rootReviewSha256']==AUTH_SHA
assert config['operationalAdmission']is receipt['operationalAdmission']is receipt['guestExecuted']is False
assert indexed(BOOT,BOOT_SHA,85)==indexed(STAGED,BOOT_SHA,85)
for row in doc(BOOT/'index.json')['files']:assert read(BOOT/row['path'],row['sha256'])==read(STAGED/row['path'],row['sha256'])
prep=doc(BOOT/'input-freeze.json');assert len(prep['inputs'])==2261 and prep['relocatedActionsMustNotReinterpretThesePaths']is True
for row in prep['inputs']:read(BOOT/row['path'],row['sha256'],row['bytes'],False)
assert not(STAGED/prep['inputs'][0]['path']).resolve().exists()
pins=doc(GENERATED/'reviewed-pins.json',PINS_SHA);authority=doc(GENERATED/'root-review.json',AUTH_SHA)
assert read(GENERATED/'reviewed-pins.json')==read(FAMILY/'reviewed-native-v4-validation-bootstrap-pins-v1.json',PINS_SHA)
assert read(GENERATED/'root-review.json')==read(FAMILY/'native-v4-validation-bootstrap-root-review-v1.json',AUTH_SHA)
assert pins['variants']['normal-runtime']is None and authority['validationBootstrapOnly']is True and authority['operationalAdmission']is False and authority['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}

# Reconstruct every producer-consumed row and generated byte without invoking it.
expected_inputs={}
def consume(path,digest=None,size=None):
 row=read(path,digest,size,False);assert row['path']not in expected_inputs or expected_inputs[row['path']]==row;expected_inputs[row['path']]=row
native_tuples={};headers={};tool_pins=doc(STAGED/'artifact-tools/tool-pins.json');assert len(tool_pins['toolDependencies'])==632
for variant in['normal-off','gc-off','disabled-off']:
 pin=pins['variants'][variant];assert len(pin['frozenFiles'])==1024
 for row in pin['frozenFiles']:consume(row['path'],row['sha256'],row['bytes'])
 consume(pin['freezeReceiptPath'],pin['freezeReceiptSha256']);freeze=doc(pin['freezeReceiptPath'],pin['freezeReceiptSha256']);meta=doc(str(pin['enginePath'])+'.build.json',pin['receiptSha256'])
 read(pin['enginePath'],pin['engineSha256'],pin['engineBytes'],False)
 assert freeze['runtimeBackendProof']==meta['zlibPolicy']['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}and len(meta['sourceManifest'])==350
 for row in meta['sourceManifest']:consume(NATIVE/row['path'],row['sha256'])
 for row in tool_pins['toolDependencies']:consume(NATIVE/row['path'],row['sha256'],row['bytes'])
 native_tuples[variant]={key:pin[key]for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']}
 for key,value in native_tuples[variant].items():assert authority['variants'][variant][key]==value
 if variant!='disabled-off':
  primary=[row for row in meta['zlibPolicy']['codecWitness']['headers']if Path(row['path']).name=='zlib.h'];assert len(primary)==1
  frozen=[row for row in freeze['copies']if row['original']==primary[0]['path']];assert len(frozen)==1
  text=read(frozen[0]['path'],primary[0]['sha256']).decode();version=re.search(r'^#define ZLIB_VERSION\s+"([^"]+)"',text,re.M);vernum=re.search(r'^#define ZLIB_VERNUM\s+(0x[0-9a-fA-F]+|[0-9]+)',text,re.M);assert version and vernum
  kernel=[row for row in meta['sourceManifest']if row['path']=='builtins/node-compat/zlib/kernel.cpp'];assert len(kernel)==1
  headers[variant]={'versionText':version.group(1),'vernum':int(vernum.group(1),0),'headerSha256':primary[0]['sha256'],'kernelSha256':kernel[0]['sha256'],'inferenceOnly':True,'privateBackendInfoObserved':False}
assert native_tuples==config['actual']==receipt['actual']==root['actual']and headers==config['headers']==root['headers']
families=[('publisher',PRODUCER,PRODUCER_SHA,'PREPARATION',PRODUCER),('base',FAMILY/'component-validation-candidate-v1','a7eca2349282a29649806c327c41ea19f01be9673c0bd7c72201f30672819816','PREPARATION',FAMILY/'component-validation-candidate-v1'),('control',FAMILY/'component-validation-control-evidence-amendment-v1','fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353','PREPARATION',FAMILY/'component-validation-control-evidence-amendment-v1'),('coverage',FAMILY/'component-validation-bootstrap-coverage-amendment-v1','a376c32b640df35ea563a722b9df480569bf08367ade8752876addc3d1423191','PREPARATION',FAMILY/'component-validation-bootstrap-coverage-amendment-v1'),('peer',FAMILY/'independent-component-validation-coverage-source-review-v1','654f077fe86dbb2f615bc13d2133c9747a528e74018345ae47f9633f05e8a21e','INDEXED_ONLY',None),('bootstrap',STAGED,BOOT_SHA,'PREPARATION',BOOT)]
summaries=[]
for role,family,digest,kind,preparation_root in families:
 index=indexed(family,digest);consume(family/'index.json',digest)
 for row in index['files']:consume(family/row['path'],row['sha256'],row['bytes'])
 summary={'role':role,'root':str(family),'indexSha256':digest,'kind':kind,'indexedFiles':len(index['files'])}
 if kind=='INDEXED_ONLY':assert role=='peer'and len(index['files'])==5 and not(family/'input-freeze.json').exists();summary['preparationManifestRead']=False
 else:
  if role=='bootstrap':
   consume(BOOT/'index.json',digest)
   for row in indexed(BOOT,digest)['files']:consume(BOOT/row['path'],row['sha256'],row['bytes'])
  manifest=doc(preparation_root/'input-freeze.json')
  for row in manifest['inputs']:consume(preparation_root/row['path'],row['sha256'],row['bytes'])
  summary.update({'preparationManifestRead':True,'preparationRoot':str(preparation_root),'preparationRows':len(manifest['inputs'])})
 summaries.append(summary)
assert summaries==receipt['inventoryFamilies']and summaries[0]['preparationRows']==11015
closure=doc(GENERATED/'component-tool-closure.json','340db04ebf86c0620f2c20fc0eb5368cc3942f62771ae52e0e0840557f490417')
assert read(GENERATED/'component-tool-closure.json')==read(PRODUCER/'component-tool-closure.json')and read(GENERATED/'component-tools.mjs')==read(PRODUCER/'component-tools.mjs')
assert config['componentToolClosureSha256']==receipt['componentToolClosureSha256']=='340db04ebf86c0620f2c20fc0eb5368cc3942f62771ae52e0e0840557f490417'
assert closure['componentToolRoot']==str(REPO)and len(closure['files'])==17 and len(closure['packages'])==4 and len(closure['endpoints'])==5 and len(closure['packageData'])==27
for group in['files','packages','endpoints','packageData']:
 for row in closure[group]:consume(row['path'],row['sha256'],row['bytes']);assert str(Path(row['path']).resolve(strict=True))==row['realPath']
texts={};edges=[];queue=closure['entries'][:]
while queue:
 name=queue.pop(0)
 if name in texts:continue
 path=REPO/name;texts[name]=read(path).decode()
 for match in re.finditer(r"^\s*import\b[^\n;]*?\bfrom\s*(['\"])([^'\"]+)\1\s*;?",texts[name],re.M):
  request=match[2]
  if request.startswith('node:'):continue
  assert request.startswith('.');target=str((path.parent/request).resolve().relative_to(REPO));edges.append({'importer':name,'request':request,'target':target});queue.append(target)
assert len(texts)==len(edges)==9 and sorted(edges,key=lambda row:json.dumps(row,separators=(',',':')))==closure['staticImportEdges']
for name in closure['entries']:assert(REPO/name).is_file()and not(NATIVE/name).exists()
assert len([row for row in closure['files']if row['kind']!='local-module'])==8 and len(closure['inactiveLazyReads'])==6
packages={row['name']:row for row in closure['packages']};package_docs={name:doc(row['path'])for name,row in packages.items()};endpoints={row['request']:row for row in closure['endpoints']}
for request,name,key in[('rolldown','rolldown','.'),('rolldown/parseAst','rolldown','./parseAst'),('@bytecodealliance/jco','@bytecodealliance/jco','.')]:
 export=package_docs[name]['exports'][key];export=export['default']if isinstance(export,dict)else export;assert str((Path(packages[name]['path']).parent/export).resolve())==endpoints[request]['realPath']
consume(FAMILY/'reviewed-native-v4-validation-bootstrap-pins-v1.json',PINS_SHA);consume(FAMILY/'native-v4-validation-bootstrap-root-review-v1.json',AUTH_SHA)
base=FAMILY/'component-validation-candidate-v1';coverage=FAMILY/'component-validation-bootstrap-coverage-amendment-v1';tools=doc(base/'tool-seal.json')
assert all(actual_manifest[key]==tools[key]for key in['toolTrees','toolLinks','invocation'])
tool_files=0
for tree in tools['toolTrees']:
 tree_root=Path(tree['path']);assert str(tree_root.resolve(strict=True))==tree['realPath'];members=[]
 for directory,dirs,files in os.walk(tree_root,followlinks=False):
  for name in sorted(dirs+files):
   path=Path(directory)/name;kind='symlink'if path.is_symlink()else'directory'if path.is_dir()else'file'if path.is_file()else None;assert kind;members.append({'path':str(path.relative_to(tree_root)),'kind':kind})
   if kind=='file':consume(path);tool_files+=1
  dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
 assert sorted(members,key=lambda row:row['path'])==tree['entries']
for row in tools['toolLinks']:
 path=Path(row['path']);assert path.is_symlink()and os.readlink(path)==row['linkText']and str(path.resolve(strict=True))==row['resolvedTarget'];target=Path(row['resolvedTarget'])
 assert('directory'if target.is_dir()else'file'if target.is_file()else None)==row['targetKind']
 if row['targetKind']=='file':read(target,row['targetSha256'],row['targetBytes'],False)
assert tool_files==4890
names=['component.mjs','canonical-require.cjs','corpus.mjs','node-fixtures.mjs','node-results.json','profile-contract.mjs','profile-contract.json','durable-host.mjs','consumed.mjs','runtime-preflight.template.mjs','run-validation.mjs','future-authority.json']
payload={name:read(base/name)for name in names}
for name,path in [('run-validation.mjs',coverage/'proposed/run-validation.mjs'),('component.mjs',coverage/'proposed/component.mjs'),('coverage-checks.mjs',coverage/'coverage-checks.mjs'),('runtime-preflight.template.mjs',PRODUCER/'runtime-preflight.template.mjs'),('component-tools.mjs',PRODUCER/'component-tools.mjs'),('component-tool-closure.json',PRODUCER/'component-tool-closure.json')]:payload[name]=read(path)
payload['reviewed-pins.json']=read(GENERATED/'reviewed-pins.json');payload['root-review.json']=read(GENERATED/'root-review.json')
expected_config={'schemaVersion':1,'state':'ROOT_REVIEWED_ZLIB350_COMPONENT_VALIDATION_SOURCE_V1','bootstrapRoot':str(STAGED),'bootstrapIndexSha256':BOOT_SHA,'nativeConfiguredSourceRoot':str(NATIVE),'componentToolRoot':str(REPO),'componentToolClosureSha256':sha(payload['component-tool-closure.json']),'pinsSha256':PINS_SHA,'rootReviewSha256':AUTH_SHA,'actual':native_tuples,'headers':headers,'operationalAdmission':False}
payload['activation.json']=encoded(expected_config);assert payload['activation.json']==read(GENERATED/'activation.json')
for name,raw in payload.items():expected_inputs[name]={'path':name,'sha256':sha(raw),'bytes':len(raw),'boundary':'.'}
expected_manifest={'schemaVersion':1,'inputs':sorted(expected_inputs.values(),key=lambda row:row['path']),'toolTrees':tools['toolTrees'],'toolLinks':tools['toolLinks'],'invocation':tools['invocation']}
assert len(expected_inputs)==11036 and expected_manifest==actual_manifest
payload['input-freeze.json']=encoded(expected_manifest);assert payload['input-freeze.json']==read(GENERATED/'input-freeze.json')
template=payload['runtime-preflight.template.mjs'].decode()
for key,value in{'CONFIG_SHA':sha(payload['activation.json']),'INPUTS_SHA':sha(payload['input-freeze.json'])}.items():assert template.count('@'+key+'@')==1;template=template.replace('@'+key+'@',value)
payload['runtime-preflight.mjs']=template.encode()
expected_receipt={'state':'ZLIB350_VALIDATION_SOURCE_CREATED_NOT_GUEST','producerIndexSha256':PRODUCER_SHA,'parentSourceIndexSha256':families[1][2],'mandatoryControlEvidenceAmendmentIndexSha256':families[2][2],'mandatoryBootstrapCoverageAmendmentIndexSha256':families[3][2],'coverageSourcePeerIndexSha256':families[4][2],'mandatoryV4BootstrapRebindIndexSha256':'cd45865813e06085dcd86065bf816dd18b8203d127df879b1b1e2ca876662a45','mandatoryPreparationContextAmendmentIndexSha256':'f6f0e1916d02445a0c7e2fc60b0b31b26ef19aef210d59a9964ba77dfcefdee9','mandatoryIndexedPeerInventoryAmendmentIndexSha256':'bd66c16ce0525a23978e23e170a82cc755bdd313516e00d7e3246302f6730494','mandatoryComponentToolClosureAmendmentIndexSha256':PRODUCER_SHA,'componentToolRoot':str(REPO),'nativeConfiguredSourceRoot':str(NATIVE),'componentToolClosureSha256':sha(payload['component-tool-closure.json']),'inventoryFamilies':summaries,'bootstrapPreparationRoot':str(BOOT),'bootstrapIndexSha256':BOOT_SHA,'actual':native_tuples,'operationalAdmission':False,'guestExecuted':False}
payload['source-receipt.json']=encoded(expected_receipt)
for name,raw in payload.items():assert read(GENERATED/name)==raw,name
expected_index={'schemaVersion':1,'state':'ZLIB350_COMPONENT_VALIDATION_SOURCE_CREATED_NOT_EXECUTED','files':[{'path':name,'sha256':sha(raw),'bytes':len(raw)}for name,raw in sorted(payload.items())],'operationalAdmission':False}
assert len(payload)==21 and encoded(expected_index)==read(GENERATED/'index.json')
assert {path.name for path in GENERATED.iterdir()}==set(payload)|{'index.json'}and not(GENERATED.with_name(GENERATED.name+'.staging')).exists()
driver=payload['run-validation.mjs'].decode();preflight=payload['runtime-preflight.mjs'].decode()
assert 'const root=admission.toolSourceRoot'in driver and 'builtinManifests:admission.selectedManifests'in driver and 'selectedManifestsForEngine('not in driver and 'nativeHarness('not in driver
assert 'toolSourceRoot:config.componentToolRoot'in preflight and 'nativeConfiguredSourceRoot:config.nativeConfiguredSourceRoot'in preflight
assert "config.nativeConfiguredSourceRoot,resolve(config.bootstrapRoot,'../../../..')"in preflight and "nativeConfiguredSourceRoot,'/private/tmp/starling-node-compat/zlib-source-v4'"in preflight
assert preflight.index('await verifyComponentToolClosure(componentToolClosure)')<preflight.index('await import(pathToFileURL')and 'async function recheck(){await verifyComponentToolClosure(componentToolClosure)'in preflight
assert 'freeze(structuredClone(native.selectedManifests))'in preflight and 'sourceRoot:config.'not in preflight
assert len(doc(GENERATED/'profile-contract.json')['exports'])==40 and len(doc(GENERATED/'node-results.json')['cases'])==61
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'],False,True)
r={'schemaVersion':1,'state':'INDEPENDENT_ZLIB350_GENERATED_V7_FAMILY_SOURCE_REVIEW_PASSED','generatedIndexSha256':GENERATED_SHA,'generatedIndexedFiles':21,'consumedRowsIndependentlyReconstructedAndRehashed':11036,'absoluteConsumedRows':11018,'relativeSealedPayloadRows':18,'entireGeneratedIndexConfigManifestReceiptAndPayloadBytesReconstructed':True,'producerIndexSha256':PRODUCER_SHA,'producerPreparationRows':11015,'inventoryFamilies':summaries,'componentClosureLocalModules':9,'componentClosureStaticEdges':9,'componentClosureSelectedDataAndAdapter':8,'componentClosurePackageVersions':4,'componentClosureEndpoints':5,'componentClosurePackageData':27,'componentClosureInactiveLazyReads':6,'allFourActualDriverLoadersExistAtComponentRootAndAreSealed':True,'nativeConfiguredRootAndFrozenSourceRootAndComponentToolContextDistinct':True,'physicalResolutionCheckedBeforeBootstrapReturnAndOnRecheck':True,'toolTrees':2,'toolRegularFilesCovered':tool_files,'toolLinks':22,'originalAndStagedBootstrapIndexedFiles':85,'originalPreparationRows':2261,'actualNative350AndTool632Checked':True,'nativeFrozenCopiesPerVariant':1024,'actualNativeTuples':native_tuples,'headerVersionInferenceOnly':headers,'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},'existingRootPinsSha256':PINS_SHA,'existingRootReviewSha256':AUTH_SHA,'rootActivationReceiptSha256':ROOT_SHA,'rootReportedActivationTerminal':0,'rootReferencesRehashed':10,'pastRootTerminalObservedByThisReader':False,'guestDriverCorpus61Fixtures28Exports40Constants107ByteUnchanged':True,'genuine350BootstrapSelectedManifestsPreserved':True,'priorV6HoldUnchanged':True,'concreteSourceBlockers':[],'sourceReadyForRootGuestReview':True,'operationalAdmission':False,'ownerImportsHelpersPreflightsNodePackageGuestNativeHostActionsOrTimingExecuted':False,'guestOrRuntimeResultClaimed':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'scope':'Generated source family and selected physical tool closure only. Exact bytes and resolution are not package evaluation, componentization or guest correctness.','verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(r,stream,indent=2);stream.write('\n')
print(json.dumps({'state':r['state'],'indexed':21,'consumed':11036,'verifiedPaths':len(seen),'blockers':0}))
