"""Independent disabled-runner source/data reader. No project imports/actions."""
from pathlib import Path
import ast,hashlib,json,os,re,stat
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;REPO=FAMILY.parents[2]
OWNER=FAMILY/'disabled-validation-candidate-v1';OWNER_SHA='89a38793670ce6066970a6cca288abf841ba194ddd4b6eb04a56edec363f4dd2'
V7=FAMILY/'component-validation-activated-v7';V7_SHA='d67971d0fbf2e116c646a0411bf3ffc4d3209475033c2d2209c443deb9802c9e'
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
def encoded(value):return(json.dumps(value,indent=2)+'\n').encode()
def indexed(root,digest,count=None):
 value=doc(root/'index.json',digest);assert count is None or len(value['files'])==count;names=set()
 for row in value['files']:
  name=row['path'];assert name not in names and not Path(name).is_absolute()and all(p not in('','.','..')for p in name.split('/'));names.add(name);read(root/name,row['sha256'],row['bytes'],False)
 return value
assert not(HERE/'results.json').exists()
indexed(OWNER,OWNER_SHA,10);report=doc(OWNER/'source-receipt.json');manifest=doc(OWNER/'input-freeze.json');assert len(manifest['inputs'])==report['preparationInputs']==11059
assert len(report['sourceChecks'])==8 and report['syntaxChecks']==5 and report['pureTestScriptExecuted']is False
assert report['bootstrapOrVerifierOrPreflightOrBundleOrComponentizerOrGuestOrHostOrNativeOrTimingExecuted']is False and report['operationalAdmission']is False
for row in manifest['inputs']:read(OWNER/row['path'],row['sha256'],row['bytes'],False)
for name,digest in report['parentIndices'].items():indexed(FAMILY/name,digest)
assert report['parentIndices'][V7.name]==V7_SHA
indexed(V7,V7_SHA,21);v7=doc(V7/'input-freeze.json');assert len(v7['inputs'])==11036 and len(v7['toolTrees'])==2 and len(v7['toolLinks'])==22
for row in v7['inputs']:read(V7/row['path'],row['sha256'],row['bytes'],False)
syntax=doc(OWNER/'syntax-results.json');assert len(syntax['checks'])==5
for row in syntax['checks']:
 if row['kind']=='Python AST':ast.parse(read(OWNER/row['path']).decode())
 else:assert row['kind']=='Node --check only; module not evaluated'and row['status']==0 and row['stdout']==row['stderr']==''
driver=read(OWNER/'run-disabled.mjs').decode();fixtures=read(OWNER/'fixtures.mjs').decode();checks=read(OWNER/'checks.mjs').decode();synthetic=read(OWNER/'test-source.mjs').decode()
assert "assert.equal(familySha,'"+V7_SHA+"'"in driver
assert driver.index('await indexed(here,ownSha);await indexed(family,familySha)')<driver.index('const{validationPreflight}')<driver.index("await import('./checks.mjs')")
assert "validationPreflight({variant:'disabled-off'})"in driver
for fragment in['admission.validationBootstrapOnly,true','admission.operationalAdmission,false','admission.metadata.zlibEnabled,false','admission.metadata.gcStress,false',"admission.metadata.entropyPolicy,'off'",'root,admission.componentToolRoot','root,admission.nativeConfiguredSourceRoot']:assert fragment in driver
assert 'async function recheck(){await indexed(here,ownSha);await indexed(family,familySha);await nativeRecheck();}'in driver
assert "const root=admission.toolSourceRoot"in driver and 'builtinManifests:admission.selectedManifests'in driver
assert 'selectedManifestsForEngine('not in driver and 'nativeHarness('not in driver and 'createZlibModule'not in driver
assert "['node:zlib','zlib'].flatMap(id=>["in fixtures
kinds=re.findall(r"kind:'([^']+)'",fixtures);assert kinds==['default-esm','named-esm','namespace-esm','literal-cjs']
assert "import z from ${JSON.stringify(id)}"in fixtures and "import {gzipSync} from ${JSON.stringify(id)}"in fixtures and "import * as z from ${JSON.stringify(id)}"in fixtures
assert "module.exports=require(${JSON.stringify(id)})"in fixtures and "'entry.mjs'"in fixtures and "'literal.cjs'"in fixtures
denial_matrix=[{'id':name,'kind':kind}for name in['node:zlib','zlib']for kind in kinds]
assert driver.index('assert.equal(denials.length,8)')<driver.index('componentizeCalls++;const{component')
denial_loop=driver[driver.index('for(let index=0;index<deniedSources.length;index++)'):driver.index('assert.equal(denials.length,8)')]
assert 'selected.componentize('not in denial_loop and 'assert.equal(componentizeCalls,0)'in denial_loop and 'preComponentizationOnly:true'in denial_loop
assert denial_loop.index("await save('denials/'+index+'/result.json',record)")<denial_loop.index('assert(failure)')
assert 'CommonJS require is not admitted:'in denial_loop and 'Node builtin is not admitted by this profile:'in denial_loop
for token in["assert.notEqual(canonical,'node:zlib')","assert.notEqual(canonical,'zlib')","!module.aliases.includes('zlib')","core.modules['node:buffer']"]:assert token in checks
assert 'core.profileVersion'in checks and "core.modules['node:child_process'].exports"in checks

# Positive fixture stays within the bounded existing Buffer profile.
assert 'Buffer.from(backing,2,3)'in fixtures and 'Buffer.from(shared)'in fixtures and 'shared.subarray(1)'in fixtures and 'window.set([1,2,3])'in fixtures
assert not re.search(r'Buffer\.from\(\s*\[',fixtures)
assert "const snapshot={bytes:bytes(),call:refusal('call'),construction:refusal('new')}"in fixtures and 'let calls=0'in fixtures and 'run(){calls++'in fixtures
assert 'new child.exec('in fixtures and "refusal('call')"in fixtures and "refusal('new')"in fixtures
for token in['Object.keys(childNamespace).sort()','childNamespace[name]===child[name]',"typeof childNamespace.then","typeof child.then","globalThis.Buffer===Buffer"]:assert token in fixtures
for token in["code:'ERR_SM_NODE_UNSUPPORTED'","module:'node:child_process'","operation:'exec'",'profile:core.profileVersion',"{own:true,type:'string',value:wanted}",'value.snapshot.bytes','value.snapshot.call','value.snapshot.construction','value.namespace,core.exports']:assert token in checks
assert "sharedHex:'090203',copyHex:'010203',viewHex:'0203'"in checks and 'sharedOffset:2' in checks and 'viewOffset:3'in checks
assert "assert.deepEqual([...app.imports].sort(),['node:buffer','node:child_process'])"in driver
assert "world test { export run: func() -> string; }"in driver and 'selectedInterfaces:[]'in driver and "disableFeatures:['stdio','random','clocks','http','fetch-event']"in driver
assert "assert.deepEqual(interfaceAudit.emittedImports,[])"in driver and 'assert.doesNotMatch(emittedWit,/\\bimport\\b/)'in driver
assert "(emittedWit.match(/\\bexport\\b/g)??[]).length,1"in driver
assert "for(let call=1;call<=3;call++)"in driver and "'fresh-Jco',()=>fresh.run(),1"in driver and "'fresh-Wasmtime',()=>decodeCliString(result.stdout.trim()),1"in driver
observation=driver[driver.index('async function observed('):driver.index('for(let call=1;call<=3;call++)')]
assert observation.index("'.raw.txt',raw)")<observation.index('JSON.parse(raw)')<observation.index("'.observed.json',value)")<observation.index('assertSmoke(value,calls,core)')
assert "timeoutMs:600000,maxOutputBytes:16*1024*1024,graceMs:5000,heartbeatMs:30000"in driver
assert 'result.terminalExitZeroObserved&&result.ownedGroupGone'in driver and "await progress('wasmtime-terminal'"in driver
assert 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c'in driver
assert "directNativeSource=\"import * as z from 'node:zlib'"in fixtures
direct=driver[driver.index('// This explicit control'):driver.index('const report=')]
assert 'await selected.componentize(directNativeSource,options)'in direct and 'pairedValidSmoke:true' in direct and 'genericAbiErrorOnly:true'in direct and 'uniqueFailureCauseProven:false'in direct
assert direct.index("await save('direct-native-zlib-result.json'")<direct.index('assert(directFailure)')<direct.index('await recheck()')
assert driver.count('selected.componentize(')==2
assert 'disk.bavail*disk.bsize>=2*1024**3'in driver and 'current.bavail*current.bsize>=800*1024**2'in driver and driver.count('await headroom()')==3
assert "Fresh output required"in driver and "output.startsWith('/tmp/starling-node-compat/')"in driver
assert "await save('results.json',report)"in driver and "await save('completion.json'"in driver
assert 'reportSha256:hash(await readFile(join(output,\'results.json\')))'in driver and 'outputLinks:[link]'in driver
assert "await readlink(link.path),link.linkText"in driver and 'await realpath(link.path),link.resolvedTarget'in driver
assert "failure-source-recheck.json"in driver and 'completePass:false'in driver
assert 'test-source.mjs'not in driver and 'syntheticOnly:true'in synthetic
future=doc(OWNER/'future-validation-family.json');assert future['validationFamilyIndexSha256']==V7_SHA and future['actualRunOutput']is None and future['guestExecuted']is future['operationalAdmission']is False

# Actual v7 authority, source/tool contexts, output helper and closed native pins.
config=doc(V7/'activation.json');closure=doc(V7/'component-tool-closure.json',config['componentToolClosureSha256']);assert config['componentToolRoot']==str(REPO)
native=Path(config['nativeConfiguredSourceRoot']);assert native==Path('/tmp/starling-node-compat/zlib-source-v4').resolve()and native!=REPO
for group in['files','packages','endpoints','packageData']:
 for row in closure[group]:read(row['path'],row['sha256'],row['bytes'],False);assert str(Path(row['path']).resolve(strict=True))==row['realPath']
for name in closure['entries']:assert(REPO/name).is_file()
preflight=read(V7/'runtime-preflight.mjs').decode();assert 'toolSourceRoot:config.componentToolRoot'in preflight and 'freeze(structuredClone(native.selectedManifests))'in preflight
helper=read(V7/'durable-host.mjs').decode();assert 'flag:\'wx\''in helper and 'await handle.sync()'in helper and 'await persistFile({output,write,path:terminalPath' in helper
assert "timeoutMs<=600000"in helper and 'SIGTERM'in helper and 'SIGKILL'in helper and "register(stdoutPath)"in helper and "register(stderrPath)"in helper
pins=doc(V7/'reviewed-pins.json',PINS_SHA);authority=doc(V7/'root-review.json',AUTH_SHA);pin=pins['variants']['disabled-off']
assert pin is not None and pins['variants']['normal-runtime']is None and len(pin['frozenFiles'])==1024
for row in pin['frozenFiles']:read(row['path'],row['sha256'],row['bytes'],False)
meta=doc(str(pin['enginePath'])+'.build.json',pin['receiptSha256']);read(pin['enginePath'],pin['engineSha256'],pin['engineBytes'],False)
assert meta['zlibEnabled']is False and meta['gcStress']is False and meta['entropyPolicy']=='off'and len(meta['sourceManifest'])==350
assert meta['zlibPolicy']['runtimeBackendProof']==authority['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
assert authority['validationBootstrapOnly']is True and authority['operationalAdmission']is False
for row in meta['sourceManifest']:read(native/row['path'],row['sha256'],capture=False)
core_manifest=doc(native/'builtins/node-compat/export-manifest.node-v22.14.0.json');assert len(core_manifest['modules']['node:child_process']['exports'])==10
for tree in v7['toolTrees']:
 root=Path(tree['path']);members=[]
 for directory,dirs,files in os.walk(root,followlinks=False):
  for name in sorted(dirs+files):
   path=Path(directory)/name;kind='symlink'if path.is_symlink()else'directory'if path.is_dir()else'file'if path.is_file()else None;assert kind;members.append({'path':str(path.relative_to(root)),'kind':kind})
   if kind=='file':read(path,capture=False)
  dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
 assert sorted(members,key=lambda row:row['path'])==tree['entries']
for row in v7['toolLinks']:assert os.readlink(row['path'])==row['linkText']and str(Path(row['path']).resolve(strict=True))==row['resolvedTarget']
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'],False,True)
r={'schemaVersion':1,'state':'INDEPENDENT_DISABLED_ZLIB350_VALIDATION_SOURCE_REVIEW_PASSED','ownerIndexSha256':OWNER_SHA,'ownerFiles':10,'preparationInputsRehashed':11059,'actualV7FamilyIndexSha256':V7_SHA,'actualV7Files':21,'actualV7ConsumedRowsRehashed':11036,'plannedFiniteBundlerDenialMatrix':denial_matrix,'allEightDenialsPrecedeAnyComponentizerCall':True,'genuineDisabledBootstrapRequired':True,'noOldSelectorOrMetadataProjection':True,'plannedValidComponents':1,'plannedGenericDirectNativeImportRefusalControls':1,'genericControlHasNoUniqueAbiCauseClaim':True,'plannedRetainedJcoCalls':3,'plannedFreshJcoCalls':1,'plannedFreshWasmtimeCalls':1,'boundedBufferConstructors':['ArrayBuffer with explicit offset/length','Uint8Array copy','subarray shared view'],'plainArrayBufferFromAbsent':True,'snapshotAndDeployedBufferStubContractChecks':True,'stubExportCountFromActualCoreManifest':10,'rawAndParsedObservationsPersistBeforeAssertions':True,'wasmtimeRawStreamsAndTerminalPersistBeforeAssertion':True,'ownedWasmtimeDeadlineMs':600000,'initialDiskBytes':2147483648,'ongoingStageDiskBytes':838860800,'completionArtifactAndLinkSealsRequired':True,'failureSourceRecheckPreservesOriginalFailure':True,'ownerSealRecordsSyntheticTestUnrun':True,'syntheticSourceTestNotRunByReaderOrCountedAsGuestPass':True,'ownerStaticChecksAuthenticatedNotRerun':8,'ownerSyntaxChecksAuthenticatedNotRerun':5,'independentPythonASTParses':1,'nativeDisabledPin':{key:pin[key]for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']},'nativeRuntimeBackendProof':{'verified':False,'version':None,'vernum':None},'sourceToolTrees':2,'sourceToolLinks':22,'concreteSourceBlockers':[],'sourceReadyForRootDisabledGuestReview':True,'operationalAdmission':False,'ownerImportsSyntheticTestsHelpersPreflightsNodePackageGuestNativeHostActionsOrTimingExecuted':False,'guestOrRuntimeResultClaimed':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'scope':'Additional disabled source/selector/smoke control only; no normal codec, disabled runtime or unique ABI error result is claimed.','verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(r,stream,indent=2);stream.write('\n')
print(json.dumps({'state':r['state'],'files':10,'inputs':11059,'verifiedPaths':len(seen),'blockers':0}))
