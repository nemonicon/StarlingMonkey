"""Independent finite source/hash/JSON/AST reader; no project imports/actions."""
from pathlib import Path
import ast,hashlib,json,os,re,stat
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;REPO=FAMILY.parents[2]
OWNER=FAMILY/'component-validation-tooling-closure-amendment-v1'
OWNER_SHA='daa7d28a7105f878a9465c4eb0fea2edaa3ef6329a15baafcabd7ccc28a0fd0c'
PARENT=FAMILY/'component-validation-indexed-peer-amendment-v1'
PARENT_SHA='bd66c16ce0525a23978e23e170a82cc755bdd313516e00d7e3246302f6730494'
BOOT=FAMILY/'native-integration-candidate-v4';BOOT_SHA='d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
NATIVE=Path('/tmp/starling-node-compat/zlib-source-v4').resolve();STAGED=NATIVE/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
PINS_SHA='b61e1f389b49d9e69c4bb1a3fd7b1314d16462a328627f94d141a39454b971cc';AUTH_SHA='7274a874ffd95d975fa84c7ad7213b52ff799c06de8a717f522aa07766b975a5'
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
def compact(value):return json.dumps(value,separators=(',',':'))
def indexed(root,digest,count=None):
 value=doc(root/'index.json',digest);assert count is None or len(value['files'])==count;names=set()
 for row in value['files']:
  name=row['path'];assert name not in names and not Path(name).is_absolute()and all(p not in('','.','..')for p in name.split('/'));names.add(name);read(root/name,row['sha256'],row['bytes'],False)
 return value
assert not(HERE/'results.json').exists()
owner=indexed(OWNER,OWNER_SHA,15);report=doc(OWNER/'source-receipt.json');manifest=doc(OWNER/'input-freeze.json')
assert len(manifest['inputs'])==report['preparationInputs']==11015 and report['sourceChecks']==22 and report['syntaxChecks']==7
for row in manifest['inputs']:read(OWNER/row['path'],row['sha256'],row['bytes'],False)
for name,digest in report['parentIndices'].items():indexed(FAMILY/name,digest)
assert report['parentIndices'][PARENT.name]==PARENT_SHA
assert report['parentIndices']['independent-component-validation-v6-family-review-v1']=='999df5f84956d185831488006271ba72abcb0a211484c1cb59567676d3255fd7'
assert report['guestDriverCorpusNativeAndRootAuthorityUnchanged']is True and report['nativeConfiguredSourceRootBoundToAuthenticatedBootstrapAncestor']is True
assert report['bootstrapOrVerifierOrPreflightOrActivationOrCompilerOrNativeOrBundleOrGuestOrHostOrTimingExecuted']is False
proof_counts={}
for name,expected in [('activate.py',7),('runtime-preflight.template.mjs',6)]:
 proof=doc(OWNER/(name+'.proof.json'));before=read(proof['beforePath'],proof['beforeSha256']).decode();after=read(OWNER/name,proof['afterSha256']).decode();value=before
 assert len(proof['edits'])==expected and proof['reverseExact']is True
 for edit in proof['edits']:assert edit['count']==1 and value.count(edit['old'])==1;value=value.replace(edit['old'],edit['new'])
 assert value==after
 for edit in reversed(proof['edits']):assert value.count(edit['new'])==1;value=value.replace(edit['new'],edit['old'])
 assert value==before;proof_counts[name]=expected
syntax=doc(OWNER/'evidence/syntax-results.json');assert len(syntax['checks'])==7
ast_count=0
for row in syntax['checks']:
 if row['kind']=='Python AST':ast.parse(read(OWNER/row['path']).decode());ast_count+=1
 else:assert row['kind']=='Node --check'and row['status']==0 and row['stdout']==row['stderr']==''
assert ast_count==4
publisher=read(OWNER/'activate.py').decode();template=read(OWNER/'runtime-preflight.template.mjs').decode();helper=read(OWNER/'component-tools.mjs').decode();test=read(OWNER/'test-resolution.mjs').decode()
assert read(OWNER/'inventory.py')==read(PARENT/'inventory.py')
def collection(code):return code[code.index(' actual={};headers={};inputs={}'):code.index(' names=[',code.index(' actual={};headers={};inputs={}'))]
assert collection(publisher)==collection(read(PARENT/'activate.py').decode())and sha(collection(publisher).encode())=='0d2936e9828a1bd45e4cf8e40b6abe4690ee27ee29535b18508da95fd91aea95'
for token in["'nativeConfiguredSourceRoot':str(tool_root)","'componentToolRoot':str(COMPONENT_TOOL_ROOT)","'componentToolClosureSha256':sha(component_closure_raw)","current==DECLARED.resolve(strict=True)","for group in ['files','packages','endpoints','packageData']",'inventory.collect_validation_inventory(HERE,own_sha,bootstrap,bootstrap_sha,add)']:assert token in publisher
assert publisher.index('own=indexed(HERE,own_sha)')<publisher.index('component_closure_raw=regular')<publisher.index('spec_from_file_location')
assert publisher.index('original_boot_rows=indexed(ORIGINAL_BOOTSTRAP,bootstrap_sha)')<publisher.index('component_closure_raw=regular')
assert 'recheck();stage.mkdir(exist_ok=False)'in publisher and "with(stage/name).open('xb')"in publisher and publisher.count('recheck()')==3
assert "if Path(row['path']).is_absolute():regular(row['path'],row['sha256'],row['bytes'])"in publisher
assert "assert.equal(config.nativeConfiguredSourceRoot,resolve(config.bootstrapRoot,'../../../..'))"in template
assert "assert.equal(config.nativeConfiguredSourceRoot,'/private/tmp/starling-node-compat/zlib-source-v4')"in template and 'assert.notEqual(config.componentToolRoot,config.nativeConfiguredSourceRoot)'in template
assert 'nativeConfiguredSourceRoot:config.nativeConfiguredSourceRoot,componentToolRoot:config.componentToolRoot,toolSourceRoot:config.componentToolRoot'in template
assert 'sourceRoot:config.'not in template
assert template.index('await verifyConsumedSeal')<template.index('await verifyComponentToolClosure(componentToolClosure)')<template.index('await import(pathToFileURL')
assert 'async function recheck(){await verifyComponentToolClosure(componentToolClosure);'in template and 'await nativeRecheck()'in template
assert template.index('await recheck();return Object.freeze')>template.index('async function recheck()')
assert 'freeze(structuredClone(native.selectedManifests))'in template and 'selectedManifestsForEngine('not in template

# Reconstruct the finite physical graph from exact repository source bytes.
closure=doc(OWNER/'component-tool-closure.json',report['componentToolClosureSha256']);assert closure['componentToolRoot']==str(REPO)
assert len(closure['files'])==17 and len(closure['packages'])==4 and len(closure['endpoints'])==5 and len(closure['packageData'])==27
entries=['tests/node-compat/toolchain.mjs','tests/node-compat/componentizer.mjs','tests/node-compat/profile-bundler.mjs','tests/node-compat/foundations/native-scalar-harness.mjs'];assert closure['entries']==entries
for group in['files','packages','endpoints','packageData']:
 for row in closure[group]:
  path=Path(row['path']);read(path,row['sha256'],row['bytes'],False);assert str(path.resolve(strict=True))==row['realPath']
texts={};edges=[];queue=entries[:]
while queue:
 name=queue.pop(0)
 if name in texts:continue
 path=REPO/name;texts[name]=read(path).decode()
 for match in re.finditer(r"^\s*import\b[^\n;]*?\bfrom\s*(['\"])([^'\"]+)\1\s*;?",texts[name],re.M):
  request=match[2]
  if request.startswith('node:'):continue
  assert request.startswith('.');target=str((path.parent/request).resolve().relative_to(REPO));edges.append({'importer':name,'request':request,'target':target});queue.append(target)
assert len(texts)==len(edges)==9
assert set(texts)=={row['relativePath']for row in closure['files']if row['kind']=='local-module'}
assert sorted(edges,key=compact)==closure['staticImportEdges']
active={row['relativePath']for row in closure['files']if row['kind']!='local-module'};inactive={row['path']for row in closure['inactiveLazyReads']};assert len(active)==8 and len(inactive)==6
urls=[]
for name,text in texts.items():
 for match in re.finditer(r"new URL\((['\"])([^'\"]+)\1,\s*import\.meta\.url\)",text):
  request=match[2];target=(REPO/name).parent/request;target=target.resolve()
  if request=='../../':assert target==REPO;continue
  local=str(target.relative_to(REPO));assert local in active or local in inactive
  urls.append({'importer':name,'request':request,'target':local,'usage':'selected-import-time'if local in active else'inactive-selector-only'})
assert sorted(urls,key=compact)==closure['relativeDataReads']and {row['target']for row in urls if row['usage']=='inactive-selector-only'}==inactive
assert all(row['usage']=='EXCLUDED_NOT_CALLED'for row in closure['inactiveLazyReads'])
patches=['tests/node-compat/'+match[2]for match in re.finditer(r"readFile\(join\(here,\s*(['\"])([^'\"]+)\1\)\)",texts['tests/node-compat/componentizer.mjs'])]
assert sorted(patches)==sorted(name for name in active if name.endswith(('.patch','.lock')))
assert 'readFileSync(resolve(repository, CORE_MANIFEST))'in texts['tests/node-compat/module-selection.mjs']
adapter=[row for row in closure['files']if row['kind']=='selected-adapter'];assert len(adapter)==1 and adapter[0]['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'and adapter[0]['bytes']==53512
packages={row['name']:row for row in closure['packages']};assert {name:row['version']for name,row in packages.items()}=={'@bytecodealliance/componentize-js':'0.23.0','@bytecodealliance/jco':'1.40.0','rolldown':'1.2.16','selected-componentizer':'0.23.0'}
package_docs={name:doc(row['path'])for name,row in packages.items()}
for name,value in package_docs.items():assert value['version']==packages[name]['version']
endpoints={row['request']:row for row in closure['endpoints']}
for request,name,key in[('rolldown','rolldown','.'),('rolldown/parseAst','rolldown','./parseAst'),('@bytecodealliance/jco','@bytecodealliance/jco','.')]:
 value=package_docs[name]['exports'][key];value=value['default']if isinstance(value,dict)else value
 expected=(Path(packages[name]['path']).parent/value).resolve();assert str(expected)==endpoints[request]['realPath']
packager=Path(packages['selected-componentizer']['path']).parent
for name in['src/componentize.js','lib/spidermonkey-embedding-splicer.js']:assert str((packager/name).resolve())==endpoints['selected-packager:'+name]['realPath']
provenance=doc(packager/'splicer-build.json');assert provenance['packagingVersion']=='componentize-js-0.23.0+sm-import-i32.v1+sm-clock-errno.v1'
assert len(provenance['checkedFiles'])+1==len(closure['packageData'])==27
package_data={row['path']:row for row in closure['packageData']};assert str(packager/'splicer-build.json')in package_data
for row in provenance['checkedFiles']:assert package_data[str(packager/row['path'])]['sha256']==row['sha256']
assert 'exact(await captureComponentToolClosure(),expected' in helper
assert all(match[2].startswith('node:')for match in re.finditer(r"^\s*import\b[^\n;]*?\bfrom\s*(['\"])([^'\"]+)\1",helper,re.M))
assert 'require.resolve(request)'in helper and 'await import('not in helper and 'import('not in helper
assert 'FINITE checks for these exact pinned source'in read(OWNER/'README.md').decode()
physical=doc(OWNER/'evidence/resolution-results.json');assert physical['passed']==len(physical['checks'])==22 and physical['packageEndpoints']==closure['endpoints']
assert physical['oldV6ExecutionAttempted']is False and physical['bootstrapOrPreflightOrOwnerModuleOrToolModuleOrCompilerOrBundleOrGuestOrHostExecuted']is False
for name in['missing loader','missing catalogue','missing ABI patch','missing LIVE adapter','changed package endpoint','changed graph edge']:assert 'reject '+name in physical['checks']
assert 'await assert.rejects(()=>verifyComponentToolClosure(broken))'in test

# Authenticate native/source views and unchanged driver/payload/tool trees.
assert indexed(BOOT,BOOT_SHA,85)==indexed(STAGED,BOOT_SHA,85)
prep=doc(BOOT/'input-freeze.json');assert len(prep['inputs'])==2261 and prep['relocatedActionsMustNotReinterpretThesePaths']is True
for row in prep['inputs']:read(BOOT/row['path'],row['sha256'],row['bytes'],False)
assert not(STAGED/prep['inputs'][0]['path']).resolve().exists()
pins=doc(FAMILY/'reviewed-native-v4-validation-bootstrap-pins-v1.json',PINS_SHA);authority=doc(FAMILY/'native-v4-validation-bootstrap-root-review-v1.json',AUTH_SHA)
assert pins['variants']['normal-runtime']is None and authority['validationBootstrapOnly']is True and authority['operationalAdmission']is False
assert authority['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
native_tuples={}
for variant in['normal-off','gc-off','disabled-off']:
 pin=pins['variants'][variant];assert len(pin['frozenFiles'])==1024
 for row in pin['frozenFiles']:read(row['path'],row['sha256'],row['bytes'],False)
 read(pin['enginePath'],pin['engineSha256'],pin['engineBytes'],False)
 freeze=doc(pin['freezeReceiptPath'],pin['freezeReceiptSha256']);meta=doc(str(pin['enginePath'])+'.build.json',pin['receiptSha256'])
 assert freeze['runtimeBackendProof']==meta['zlibPolicy']['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
 assert len(meta['sourceManifest'])==350
 for row in meta['sourceManifest']:read(NATIVE/row['path'],row['sha256'],capture=False)
 native_tuples[variant]={key:pin[key]for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']}
 for key,value in native_tuples[variant].items():assert authority['variants'][variant][key]==value
toolpins=doc(STAGED/'artifact-tools/tool-pins.json');assert len(toolpins['toolDependencies'])==632
for row in toolpins['toolDependencies']:read(NATIVE/row['path'],row['sha256'],row['bytes'],False)
bootstrap_js=read(STAGED/'artifact-tools/bootstrap-preflight.mjs').decode();classifier=read(STAGED/'artifact-tools/bootstrap-classifier.py').decode()
assert 'sourceRoot:actual.sourceRoot'in bootstrap_js and "'sourceRoot':pin['sourceRoot'],'configuredSourceRoot':str(common.REPO)"in classifier
coverage=FAMILY/'component-validation-bootstrap-coverage-amendment-v1';driver=read(coverage/'proposed/run-validation.mjs').decode()
assert "payload['run-validation.mjs']=regular(COVERAGE/'proposed/run-validation.mjs')"in publisher and "payload['component.mjs']=regular(COVERAGE/'proposed/component.mjs')"in publisher
assert 'builtinManifests:admission.selectedManifests'in driver and 'const root=admission.toolSourceRoot'in driver and 'selectedManifestsForEngine('not in driver and 'nativeHarness('not in driver
old=FAMILY/'component-validation-v4-rebind-amendment-v1'
for row in doc(old/'unchanged-payloads.json')['payloads']:read(row['sourcePath'],row['sha256'],row['bytes'],False)
seal=doc(FAMILY/'component-validation-candidate-v1/tool-seal.json');assert len(seal['toolTrees'])==2 and len(seal['toolLinks'])==22
for tree in seal['toolTrees']:
 root=Path(tree['path']);members=[]
 for directory,dirs,files in os.walk(root,followlinks=False):
  for name in sorted(dirs+files):
   path=Path(directory)/name;kind='symlink'if path.is_symlink()else'directory'if path.is_dir()else'file'if path.is_file()else None;assert kind;members.append({'path':str(path.relative_to(root)),'kind':kind})
   if kind=='file':read(path,capture=False)
  dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
 assert sorted(members,key=lambda row:row['path'])==tree['entries']
for row in seal['toolLinks']:assert os.readlink(row['path'])==row['linkText']and str(Path(row['path']).resolve(strict=True))==row['resolvedTarget']
for name in['component-validation-activated-v7','component-validation-activated-v7.staging']:assert not(FAMILY/name).exists()and not(FAMILY/name).is_symlink()
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'],False,True)
r={'schemaVersion':1,'state':'INDEPENDENT_ZLIB350_TOOLING_CLOSURE_SOURCE_REVIEW_PASSED','ownerIndexSha256':OWNER_SHA,'ownerFiles':15,'preparationInputsRehashed':11015,'publisherReversibleEdits':7,'preflightReversibleEdits':6,'resolvedBlocker':'ZV6-M1','concreteSourceBlockers':[],'physicalLocalModules':9,'staticImportEdges':9,'selectedLocalDataAndAdapter':8,'physicalClosureFiles':17,'packageVersions':4,'packageEndpoints':5,'selectedPackageData':27,'inactiveLazyAdmissionReadsClassifiedExcluded':6,'finitePinnedSourceRegexScopeOnly':True,'packageResolverEndpointsIndependentlyDerivedFromPinnedJSON':True,'physicalClosureCheckedBeforeBootstrapBeforeReturnAndDuringRecheck':True,'nativeConfiguredRootBoundToAuthenticatedBootstrapAncestor':True,'nativeFrozenSourceRootPreserved':True,'driverToolSourceRootAliasNamesComponentRootOnly':True,'genuine350BootstrapSelectedManifestsPreserved':True,'inventoryHelperByteExact':True,'actualNativeCollectionBlockByteExact':True,'guestDriverCorpus61Fixtures28Exports40Constants107ByteUnchanged':True,'sourceToolTrees':2,'sourceToolLinks':22,'originalAndStagedBootstrapIndexedFiles':85,'bootstrapPreparationRowsAtOriginalRoot':2261,'actualNative350AndTool632Checked':True,'nativeFrozenCopiesPerVariant':1024,'actualNativeTuples':native_tuples,'nativeRuntimeBackendProof':{'verified':False,'version':None,'vernum':None},'existingRootValidationPinsSha256':PINS_SHA,'existingRootReviewSha256':AUTH_SHA,'ownerPhysicalSourceChecksAuthenticatedNotRerun':22,'ownerSyntaxChecksAuthenticatedNotRerun':7,'independentPythonASTParses':4,'futureOutputFamily':'component-validation-activated-v7','futureOutputAbsentAtFinalReview':True,'rootOrOwnerPastTerminalsObservedByThisReader':False,'operationalAdmission':False,'ownerImportsFunctionsHelpersTestsPreflightsBootstrapNativeVerifierCompilerNodeGuestHostOrTimingExecuted':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'scope':'Source correction of component harness tool closure; physical resolution is not package evaluation or component/guest success.','verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(r,stream,indent=2);stream.write('\n')
print(json.dumps({'state':r['state'],'files':15,'inputs':11015,'verifiedPaths':len(seen),'blockers':0}))
