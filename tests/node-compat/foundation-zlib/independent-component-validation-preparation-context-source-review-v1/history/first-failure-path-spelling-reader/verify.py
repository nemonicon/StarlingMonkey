"""Independent file/hash/JSON/AST source reader. Imports no project module."""
from pathlib import Path
import ast,hashlib,json,os,stat
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent
OWNER=FAMILY/'component-validation-preparation-context-amendment-v1'
OWNER_SHA='f6f0e1916d02445a0c7e2fc60b0b31b26ef19aef210d59a9964ba77dfcefdee9'
BOOT=FAMILY/'native-integration-candidate-v4'
BOOT_SHA='d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
SOURCE=Path('/tmp/starling-node-compat/zlib-source-v4').resolve()
STAGED=SOURCE/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
OLD=FAMILY/'component-validation-v4-rebind-amendment-v1'
OLD_SHA='cd45865813e06085dcd86065bf816dd18b8203d127df879b1b1e2ca876662a45'
FAIL_SHA='3ff30ff1d5ba07fa714cdb9061461df9a0d60a7f8205550aa26e5cc9bdcb9a35'
seen={}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path,h=None,size=None,capture=True):
 path=Path(path).absolute();a=path.lstat();assert stat.S_ISREG(a.st_mode)and not path.is_symlink(),path
 digest=hashlib.sha256();chunks=[]if capture else None
 with path.open('rb')as source:
  for block in iter(lambda:source.read(1024*1024),b''):
   digest.update(block)
   if capture:chunks.append(block)
 b=path.lstat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns),path
 assert h is None or digest.hexdigest()==h,path;assert size is None or b.st_size==size,path
 row={'path':str(path),'sha256':digest.hexdigest(),'bytes':b.st_size};assert str(path)not in seen or seen[str(path)]==row,path;seen[str(path)]=row
 return b''.join(chunks)if capture else row
def doc(path,h=None):return json.loads(read(path,h))
def indexed(root,h,count=None):
 value=doc(root/'index.json',h);assert count is None or len(value['files'])==count
 names=set()
 for row in value['files']:
  name=row['path'];assert name not in names and not Path(name).is_absolute()and all(p not in('','.','..')for p in name.split('/'));names.add(name)
  read(root/name,row['sha256'],row['bytes'],False)
 return value
assert not(HERE/'results.json').exists()
own=indexed(OWNER,OWNER_SHA,9);old=indexed(OLD,OLD_SHA,8)
owner_report=doc(OWNER/'results.json');manifest=doc(OWNER/'input-freeze.json')
assert owner_report['sourceChecks']==len(owner_report['checks'])==14 and owner_report['syntaxChecks']==3
assert len(manifest['inputs'])==owner_report['preparationInputs']==8877
assert manifest['activationOrGuestExecuted']is False
for row in manifest['inputs']:
 path=Path(row['path']);path=path if path.is_absolute()else OWNER/path
 read(path,row['sha256'],row['bytes'],False)
parents={'component-validation-candidate-v1':'a7eca2349282a29649806c327c41ea19f01be9673c0bd7c72201f30672819816','component-validation-control-evidence-amendment-v1':'fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353','component-validation-bootstrap-coverage-amendment-v1':'a376c32b640df35ea563a722b9df480569bf08367ade8752876addc3d1423191','independent-component-validation-coverage-source-review-v1':'654f077fe86dbb2f615bc13d2133c9747a528e74018345ae47f9633f05e8a21e','independent-component-validation-v4-rebind-source-review-v1':'74109e3fb4082c813592d0af340f21f4888c5d9e9b29e5d91cb77dd2e79d2f62','compound-link-parser-amendment-v1':'18ee1ab685fbafd331ad10eabe5c16352532bac83cee56181c75356f7e46ebdb'}
for name,h in parents.items():indexed(FAMILY/name,h)
original_index=indexed(BOOT,BOOT_SHA,85);staged_index=indexed(STAGED,BOOT_SHA,85);assert original_index==staged_index
for row in original_index['files']:assert read(BOOT/row['path'],row['sha256'])==read(STAGED/row['path'],row['sha256'])
prep=doc(BOOT/'input-freeze.json');assert prep['originalPreparationRoot']==str(BOOT)and prep['relocatedActionsMustNotReinterpretThesePaths']is True
assert len(prep['inputs'])==2261 and read(BOOT/'input-freeze.json')==read(STAGED/'input-freeze.json')
for row in prep['inputs']:read((BOOT/row['path']).resolve(),row['sha256'],row['bytes'],False)
row0=prep['inputs'][0];wrong=(STAGED/row0['path']).resolve();right=(BOOT/row0['path']).resolve()
assert row0['path']=='../../foundation-classic-streams/production-adoption-v1/reviewed-trace-runtime-pins-v1.json'
assert not wrong.exists()and not wrong.is_symlink();read(right,row0['sha256'],row0['bytes'],False)
regression=doc(OWNER/'context-regression.json');assert regression['bothIndexedViewsByteIdentical']is True and regression['preparationRowsVerifiedAtOriginalRoot']==2261
assert regression['row0']['incorrectStagedPath']==str(wrong)and regression['row0']['originalPath']==str(right)
failure=doc(FAMILY/'validation-source-activation-attempt2-context-failure-root-results.json',FAIL_SHA)
assert failure['rootToolSession']==49004 and failure['rawOuterExit']==1 and failure['incorrectResolution']==str(wrong)
assert failure['sourceOrNativeMetadataChanged']is failure['validationSourcePublished']is failure['guestExecuted']is failure['operationalAdmission']is False
assert len(failure['evidence'])==3
for row in failure['evidence']:read(row['path'],row['sha256'],row['bytes'],False)
terminal=doc(failure['evidence'][2]['path']);assert terminal['returncode']==1
stderr=read(failure['evidence'][1]['path']).decode();assert str(wrong)in stderr and'FileNotFoundError'in stderr
proof=doc(OWNER/'publisher-proof.json');assert proof['beforePath']==str(OLD/'activate.py')and len(proof['edits'])==4 and proof['reverseExact']is True
before=read(OLD/'activate.py',proof['beforeSha256']).decode();after=read(OWNER/'activate.py',proof['afterSha256']).decode();value=before
for edit in proof['edits']:assert edit['count']==1 and value.count(edit['old'])==1;value=value.replace(edit['old'],edit['new'])
assert value==after
for edit in reversed(proof['edits']):assert value.count(edit['new'])==1;value=value.replace(edit['new'],edit['old'])
assert value==before
asts={name:ast.parse(read(OWNER/name).decode())for name in['activate.py','prepare.py','seal-source.py']}
assert after.index('original_boot_rows=indexed(ORIGINAL_BOOTSTRAP,bootstrap_sha)')<after.index('spec_from_file_location')
assert after.index('boot_rows=indexed(bootstrap,bootstrap_sha)')<after.index('spec_from_file_location')
assert "ORIGINAL_BOOTSTRAP=Path('"+str(BOOT)+"')"in after
assert "OUTPUT=HERE.parent/'component-validation-activated-v5'"in after
assert "preparation_root=ORIGINAL_BOOTSTRAP if root==bootstrap else root"in after
assert "for row in json.loads(regular(preparation_root/'input-freeze.json'))['inputs']:add(preparation_root/row['path'],row['sha256'],row['bytes'])"in after
assert "for row in original_boot_rows:add(ORIGINAL_BOOTSTRAP/row['path'],row['sha256'],row['bytes'])"in after
assert "'mandatoryV4BootstrapRebindIndexSha256':'"+OLD_SHA+"'"in after
assert "'mandatoryPreparationContextAmendmentIndexSha256':own_sha"in after and"'bootstrapPreparationRoot':str(ORIGINAL_BOOTSTRAP)"in after
def collection(code):
 start=code.index(' actual={};headers={};inputs={}')
 return code[start:code.index(' names=[',start)]
assert collection(before)==collection(after)and sha(collection(after).encode())==regression['actualSourceCollectionBlockSha256']
for fragment in["bootstrap==(DECLARED/PACKET).resolve(strict=True)","current==DECLARED.resolve(strict=True)","result=backend.bootstrap(pins_path,pins_sha,review_path,review_sha,variant)","result['metadata']['sourceManifest']","tool_pins['toolDependencies']","pin['frozenFiles']","'inferenceOnly':True,'privateBackendInfoObserved':False"]:assert fragment in after
assert after.index('review[\'proposalIndexSha256\']==bootstrap_sha')<after.index('spec_from_file_location')
assert 'recheck();stage.mkdir(exist_ok=False)'in after and"with(stage/name).open('xb')"in after and'stage.rename(OUTPUT)'in after
assert 'for row in inputs.values()'in after and"if Path(row['path']).is_absolute():regular(row['path'],row['sha256'],row['bytes'])"in after
assert after.count('recheck()')==3
base=FAMILY/'component-validation-candidate-v1';coverage=FAMILY/'component-validation-bootstrap-coverage-amendment-v1'
payloads=doc(OLD/'unchanged-payloads.json')
for row in payloads['payloads']:read(row['sourcePath'],row['sha256'],row['bytes'],False)
for fragment in["payload['run-validation.mjs']=regular(COVERAGE/'proposed/run-validation.mjs')","payload['component.mjs']=regular(COVERAGE/'proposed/component.mjs')","payload['coverage-checks.mjs']=regular(COVERAGE/'coverage-checks.mjs')"]:assert fragment in after
for name in['corpus.mjs','node-fixtures.mjs','node-results.json','profile-contract.mjs','profile-contract.json','canonical-require.cjs','durable-host.mjs','consumed.mjs','runtime-preflight.template.mjs']:read(base/name,capture=False)
tool_seal=doc(base/'tool-seal.json');assert len(tool_seal['toolTrees'])==2 and len(tool_seal['toolLinks'])==22
for tree in tool_seal['toolTrees']:
 root=Path(tree['path']);members=[]
 for directory,dirs,files in os.walk(root,followlinks=False):
  for name in sorted(dirs+files):
   path=Path(directory)/name;kind='symlink'if path.is_symlink()else'directory'if path.is_dir()else'file'if path.is_file()else None;assert kind
   members.append({'path':str(path.relative_to(root)),'kind':kind})
   if kind=='file':read(path,capture=False)
  dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
 assert sorted(members,key=lambda row:row['path'])==tree['entries']
for row in tool_seal['toolLinks']:assert os.readlink(row['path'])==row['linkText']and str(Path(row['path']).resolve(strict=True))==row['resolvedTarget']
pins=doc(FAMILY/'reviewed-native-v4-validation-bootstrap-pins-v1.json','b61e1f389b49d9e69c4bb1a3fd7b1314d16462a328627f94d141a39454b971cc')
authority=doc(FAMILY/'native-v4-validation-bootstrap-root-review-v1.json','7274a874ffd95d975fa84c7ad7213b52ff799c06de8a717f522aa07766b975a5')
assert pins['state']=='ROOT_REVIEWED_ZLIB350_VALIDATION_BOOTSTRAP_V1'and authority['state']=='ROOT_REVIEWED_ZLIB350_BUILD_INPUTS_FOR_CODEC_VALIDATION_V1'
assert authority['proposalIndexSha256']==BOOT_SHA and authority['validationBootstrapOnly']is True and authority['operationalAdmission']is False
assert authority['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}and pins['variants']['normal-runtime']is None
policy=doc(BOOT/'policy.json');tool_pins=doc(BOOT/'artifact-tools/tool-pins.json');assert len(policy['expectedNativeSourceManifest'])==350 and len(tool_pins['toolDependencies'])==632
for row in policy['expectedNativeSourceManifest']:read(SOURCE/row['path'],row['sha256'],capture=False)
for row in tool_pins['toolDependencies']:read(SOURCE/row['path'],row['sha256'],row['bytes'],False)
native_tuples={}
for variant in['normal-off','gc-off','disabled-off']:
 pin=pins['variants'][variant];assert pin is not None and len(pin['frozenFiles'])==1024
 for row in pin['frozenFiles']:read(row['path'],row['sha256'],row['bytes'],False)
 frozen=doc(Path(pin['freezeReceiptPath']),pin['freezeReceiptSha256'])
 metadata=doc(Path(str(pin['enginePath'])+'.build.json'),pin['receiptSha256'])
 assert frozen['runtimeBackendProof']==metadata['zlibPolicy']['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
 for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']:assert pin[key]==authority['variants'][variant][key]
 assert pin['independentProofIndexSha256']==authority['variants'][variant]['independentProofIndexSha256']
 indexed(Path(pin['independentProofIndexPath']).parent,pin['independentProofIndexSha256'],8)
 read(pin['independentProofResultPath'],pin['independentProofResultSha256'],capture=False)
 native_tuples[variant]={key:pin[key]for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']}
for name in['component-validation-activated-v5','component-validation-activated-v5.staging']:assert not(FAMILY/name).exists()and not(FAMILY/name).is_symlink()
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'],False)
result={'schemaVersion':1,'state':'INDEPENDENT_ZLIB_VALIDATION_PREPARATION_CONTEXT_SOURCE_REVIEW_PASSED_NO_ACTIONS','ownerIndexSha256':OWNER_SHA,'ownerFiles':9,'preparationInputs':8877,'publisherExactReversibleEdits':4,'parentPublisherIndexSha256':OLD_SHA,'bootstrapIndexSha256':BOOT_SHA,'originalAndStagedIndexedFilesPerView':85,'bothIndexedViewsByteExact':True,'bootstrapOriginalPreparationRowsRehashed':2261,'actualWrongStagedRow0Absent':True,'row0':{'relativePath':row0['path'],'incorrectStagedPath':str(wrong),'originalPath':str(right),'sha256':row0['sha256'],'bytes':row0['bytes']},'actualCollectionBlockByteUnchanged':True,'actualSourceNative350AndTool632Checked':True,'sourceAndHeaderAndFrozenCollectionStillUsesActualStagedBootstrap':True,'bothOriginalAndStagedSealsEnterPrivateFinalRechecks':True,'guestDriverCorpus61Fixtures28Exports40Constants107ByteUnchanged':True,'toolTrees':2,'toolLinks':22,'existingRootValidationPinsSha256':'b61e1f389b49d9e69c4bb1a3fd7b1314d16462a328627f94d141a39454b971cc','existingRootReviewSha256':'7274a874ffd95d975fa84c7ad7213b52ff799c06de8a717f522aa07766b975a5','nativeTuples':native_tuples,'futureOutputFamily':'component-validation-activated-v5','futureOutputAbsentAtReview':True,'failedAttemptReceiptSha256':FAIL_SHA,'failedAttemptRawOuterExit':1,'pastRootTerminalObservedByThisReader':False,'ownerSourceChecksAuthenticatedNotRerun':14,'independentASTParses':3,'concreteSourceBlockers':[],'operationalAdmission':False,'newAuthorityOrNativeOrRuntimeOrGuestProofClaim':False,'ownerImportsHelpersTestsPublishersBootstrapNativeVerifiersNodeCompilerGuestHostOrTimingExecuted':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'scope':'Four-edit source correction only. Original preparation context is authenticated separately; actual staged source/frozen/native authority and immutable payloads are unchanged.','verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({'state':result['state'],'files':9,'preparationInputs':8877,'paths':len(seen),'blockers':0}))
