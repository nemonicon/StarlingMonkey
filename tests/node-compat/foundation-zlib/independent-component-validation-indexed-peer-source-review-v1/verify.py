"""Independent finite source/JSON/hash/AST reader. Imports no project module."""
from pathlib import Path
import ast,hashlib,json,os,stat
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent
OWNER=FAMILY/'component-validation-indexed-peer-amendment-v1'
OWNER_SHA='bd66c16ce0525a23978e23e170a82cc755bdd313516e00d7e3246302f6730494'
EVIDENCE=FAMILY/'component-validation-indexed-peer-regression-evidence-v1'
EVIDENCE_SHA='5aa0cd4ba9e9fef9b1273281fb9ad055831c39491cf6628bf5814950e7e10842'
PARENT=FAMILY/'component-validation-preparation-context-amendment-v1'
PARENT_SHA='f6f0e1916d02445a0c7e2fc60b0b31b26ef19aef210d59a9964ba77dfcefdee9'
HOLD=FAMILY/'independent-component-validation-preparation-context-source-review-v1'
HOLD_SHA='541b2779f049c2f25c81ff3aed2f77975da14ea9caa821a347181203ed9147ab'
BOOT=FAMILY/'native-integration-candidate-v4'
BOOT_SHA='d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
SOURCE=Path('/tmp/starling-node-compat/zlib-source-v4').resolve()
STAGED=SOURCE/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
PINS_SHA='b61e1f389b49d9e69c4bb1a3fd7b1314d16462a328627f94d141a39454b971cc'
REVIEW_SHA='7274a874ffd95d975fa84c7ad7213b52ff799c06de8a717f522aa07766b975a5'
seen={};identities={}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path,h=None,size=None,capture=True,force=False):
 path=Path(path);leaf=path.lstat();assert stat.S_ISREG(leaf.st_mode)and not path.is_symlink(),path
 path=path.resolve(strict=True);key=str(path);a=path.stat();identity=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)
 if not capture and not force and key in seen:
  assert identities[key]==identity,path;row=seen[key]
  assert h is None or row['sha256']==h,path;assert size is None or row['bytes']==size,path;return row
 digest=hashlib.sha256();chunks=[]if capture else None
 with path.open('rb')as source:
  for block in iter(lambda:source.read(1024*1024),b''):
   digest.update(block)
   if capture:chunks.append(block)
 b=path.stat();assert identity==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns),path
 assert h is None or digest.hexdigest()==h,path;assert size is None or b.st_size==size,path
 row={'path':key,'sha256':digest.hexdigest(),'bytes':b.st_size};assert key not in seen or seen[key]==row,path
 seen[key]=row;identities[key]=identity
 return b''.join(chunks)if capture else row
def doc(path,h=None):return json.loads(read(path,h))
def indexed(root,h,count=None):
 value=doc(root/'index.json',h);assert count is None or len(value['files'])==count
 names=set()
 for row in value['files']:
  name=row['path'];assert isinstance(name,str)and name not in names and not Path(name).is_absolute()and all(p not in('','.','..')for p in name.split('/'));names.add(name)
  read(root/name,row['sha256'],row['bytes'],False)
 return value
assert not(HERE/'results.json').exists()
own=indexed(OWNER,OWNER_SHA,9);parent=indexed(PARENT,PARENT_SHA,9);hold=indexed(HOLD,HOLD_SHA,12);evidence_index=indexed(EVIDENCE,EVIDENCE_SHA,3)
assert evidence_index['sourceIndexSha256']==OWNER_SHA
source_report=doc(OWNER/'source-receipt.json');source_manifest=doc(OWNER/'input-freeze.json')
assert source_report['sourceChecks']==len(source_report['checks'])==13 and len(source_report['syntaxChecks'])==5
assert source_report['preparationInputs']==len(source_manifest['inputs'])==8901
assert source_manifest['actionOrGuestExecuted']is False and source_report['postsealActualSelfInventoryRegressionRequired']is True
assert source_report['parentIndices']=={PARENT.name:PARENT_SHA,HOLD.name:HOLD_SHA}
assert source_report['guestOrDriverOrCorpusOrNativeOrAuthorityChanged']is False
for row in source_manifest['inputs']:read(OWNER/row['path'],row['sha256'],row['bytes'],False)
proof=doc(OWNER/'publisher-proof.json');assert proof['beforePath']==str(PARENT/'activate.py')and len(proof['edits'])==4 and proof['reverseExact']is True
before=read(PARENT/'activate.py',proof['beforeSha256']).decode();after=read(OWNER/'activate.py',proof['afterSha256']).decode();value=before
for edit in proof['edits']:assert edit['count']==1 and value.count(edit['old'])==1;value=value.replace(edit['old'],edit['new'])
assert value==after
for edit in reversed(proof['edits']):assert value.count(edit['new'])==1;value=value.replace(edit['new'],edit['old'])
assert value==before
def collection(code):
 start=code.index(' actual={};headers={};inputs={}')
 return code[start:code.index(' names=[',start)]
assert collection(before)==collection(after)and sha(collection(after).encode())=='0d2936e9828a1bd45e4cf8e40b6abe4690ee27ee29535b18508da95fd91aea95'
asts={row['path']:ast.parse(read(OWNER/row['path'],row['sha256']).decode())for row in source_report['syntaxChecks']}
assert set(asts)=={'activate.py','inventory.py','inventory-regression.py','prepare.py','seal-source.py'}
helper=read(OWNER/'inventory.py').decode();regression=read(OWNER/'inventory-regression.py').decode()
module=asts['inventory.py'];assigns={}
for node in module.body:
 if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
  try:assigns[node.targets[0].id]=ast.literal_eval(node.value)
  except(ValueError,TypeError):pass
BASES=(('base','component-validation-candidate-v1','a7eca2349282a29649806c327c41ea19f01be9673c0bd7c72201f30672819816','PREPARATION'),('control','component-validation-control-evidence-amendment-v1','fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353','PREPARATION'),('coverage','component-validation-bootstrap-coverage-amendment-v1','a376c32b640df35ea563a722b9df480569bf08367ade8752876addc3d1423191','PREPARATION'),('peer','independent-component-validation-coverage-source-review-v1','654f077fe86dbb2f615bc13d2133c9747a528e74018345ae47f9633f05e8a21e','INDEXED_ONLY'))
assert assigns['BASES']==BASES and assigns['BOOT_SHA']==BOOT_SHA
assert "ORIGINAL=Path('"+str(BOOT)+"')"in helper
assert "STAGED=Path('/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/foundation-zlib/native-integration-candidate-v4')"in helper
assert '.exists('not in helper and "if kind=='INDEXED_ONLY':"in helper and "assert role=='peer'"in helper
assert "kind=='PREPARATION'and role in('publisher','base','control','coverage','bootstrap')"in helper
assert "manifest=json.loads(read_file(preparation_root/'input-freeze.json'))"in helper
assert "for row in manifest['inputs']:add(preparation_root/row['path'],row['sha256'],row['bytes'])"in helper
assert "families.append(('bootstrap',bootstrap_root,bootstrap_sha,'PREPARATION',ORIGINAL))"in helper and 'original_rows==rows'in helper
assert "['publisher','base','control','coverage','peer','bootstrap']"in helper
for node in module.body:
 if isinstance(node,ast.Import):assert all(a.name.split('.')[0]in {'pathlib','hashlib','json','re'}for a in node.names)
 if isinstance(node,ast.ImportFrom):assert node.module in {'pathlib','hashlib','json','re'}
for fragment in["own=indexed(HERE,own_sha)",'boot_rows=indexed(bootstrap,bootstrap_sha)','original_boot_rows=indexed(ORIGINAL_BOOTSTRAP,bootstrap_sha)']:
 assert after.index(fragment)<after.index("HERE/'inventory.py'")
assert after.index("HERE/'inventory.py'")<after.index("bootstrap/'artifact-tools/bootstrap-classifier.py'")
assert 'sys.dont_write_bytecode=True'in after and "if not __debug__:raise RuntimeError('Assertions required')"in after
assert 'inventory.collect_validation_inventory(HERE,own_sha,bootstrap,bootstrap_sha,add)'in after
assert "'mandatoryPreparationContextAmendmentIndexSha256':'"+PARENT_SHA+"'"in after and "'mandatoryIndexedPeerInventoryAmendmentIndexSha256':own_sha"in after
assert "'inventoryFamilies':inventory_families"in after and "'bootstrapPreparationRoot':str(ORIGINAL_BOOTSTRAP)"in after
assert "OUTPUT=HERE.parent/'component-validation-activated-v6'"in after
for fragment in["bootstrap==(DECLARED/PACKET).resolve(strict=True)","current==DECLARED.resolve(strict=True)","result=backend.bootstrap(pins_path,pins_sha,review_path,review_sha,variant)","result['metadata']['sourceManifest']","tool_pins['toolDependencies']","pin['frozenFiles']","'inferenceOnly':True,'privateBackendInfoObserved':False"]:assert fragment in after
assert after.index("review['proposalIndexSha256']==bootstrap_sha")<after.index('spec_from_file_location')
assert 'recheck();stage.mkdir(exist_ok=False)'in after and "with(stage/name).open('xb')"in after and 'stage.rename(OUTPUT)'in after and after.count('recheck()')==3
assert "if Path(row['path']).is_absolute():regular(row['path'],row['sha256'],row['bytes'])"in after

# Independently reconstruct the six-family union without importing the shared helper.
inventory={};summaries=[]
def consume(path,h=None,size=None):
 row=read(path,h,size,False);key=row['path'];assert key not in inventory or inventory[key]==row;inventory[key]=row
families=[('publisher',OWNER,OWNER_SHA,'PREPARATION',OWNER)]
families.extend((role,FAMILY/name,digest,kind,FAMILY/name)for role,name,digest,kind in BASES)
families.append(('bootstrap',STAGED,BOOT_SHA,'PREPARATION',BOOT))
for role,root,digest,kind,preparation_root in families:
 index=indexed(root,digest);consume(root/'index.json',digest)
 for row in index['files']:consume(root/row['path'],row['sha256'],row['bytes'])
 summary={'role':role,'root':str(root),'indexSha256':digest,'kind':kind,'indexedFiles':len(index['files'])}
 if kind=='INDEXED_ONLY':
  assert role=='peer'and len(index['files'])==5 and not(root/'input-freeze.json').exists();summary['preparationManifestRead']=False
 else:
  if role=='bootstrap':
   original_index=indexed(BOOT,digest,85);assert original_index==index;consume(BOOT/'index.json',digest)
   for row in original_index['files']:
    consume(BOOT/row['path'],row['sha256'],row['bytes']);assert read(BOOT/row['path'])==read(STAGED/row['path'])
  prep=doc(preparation_root/'input-freeze.json');assert prep['schemaVersion']==1
  for row in prep['inputs']:consume(preparation_root/row['path'],row['sha256'],row['bytes'])
  summary.update({'preparationManifestRead':True,'preparationRoot':str(preparation_root),'preparationRows':len(prep['inputs'])})
 summaries.append(summary)
assert len(inventory)==8904
stored=doc(EVIDENCE/'results.json','d29787dfb296744fcfc3ea6328d87a8788419324097a4d25d2e29f828986f73b')
assert stored['sourceIndexSha256']==OWNER_SHA and stored['families']==summaries
assert stored['consumedFiles']==sorted(inventory.values(),key=lambda row:row['path'])and stored['consumedFileCount']==8904
for key in['completeInventoryVerifiedTwice','indexedPeerFileOmissionRefused','requiredPreparationManifestOmissionRefused','latentStagedRow0Absent','latentOriginalRow0Exact']:assert stored[key]is True
assert stored['peerManifestInventedOrRead']is False and stored['bootstrapOrVerifierOrActivationOrCompilerOrGuestOrHostExecuted']is False
execution=doc(EVIDENCE/'execution.json');assert execution['observedExitCode']==0 and execution['sourceIndexSha256']==OWNER_SHA
assert execution['command'][0]=='python3'and execution['command'][1].endswith('/inventory-regression.py')and execution['command'][2]==OWNER_SHA
external=execution['externalReport'];assert read(external['path'],external['sha256'],external['bytes'])==read(EVIDENCE/'results.json')
assert 'module.collect_validation_inventory(HERE,source_sha,BOOT,BOOT_SHA,add)'in regression
assert 'module.collect_validation_inventory(HERE,source_sha,BOOT,BOOT_SHA,final_add)==families'in regression
assert 'assert final==consumed'in regression and 'sys.dont_write_bytecode=True'in regression
assert regression.index("regular(HERE/'index.json',source_sha)")<regression.index("HERE/'inventory.py'")
assert "target=peer_root/'verify.py'"in regression and "module.read_indexed(peer_root,peer['indexSha256'],deny_indexed)"in regression
assert "manifest_target=HERE/'input-freeze.json'"in regression and 'lambda *args:None,deny_manifest'in regression
assert "if Path(path)==target:raise FileNotFoundError"in regression and "if Path(path)==manifest_target:raise FileNotFoundError"in regression
assert 'assert indexed_failed'in regression and 'assert prep_failed'in regression
assert 'bootstrap-classifier'not in regression and 'activate.py'not in regression
prep=doc(BOOT/'input-freeze.json');assert len(prep['inputs'])==2261 and prep['originalPreparationRoot']==str(BOOT)and prep['relocatedActionsMustNotReinterpretThesePaths']is True
row0=prep['inputs'][0];wrong=(STAGED/row0['path']).resolve();right=(BOOT/row0['path']).resolve();assert not wrong.exists();read(right,row0['sha256'],row0['bytes'],False)
correction=doc(FAMILY/'validation-source-activation-attempt2-root-origin-correction.json','19db5ef2caba575adb23b1126d4567bb7ce222fe75149a31c18bcf35f4311b06')
assert correction['originalRootFailureSha256']=='3ff30ff1d5ba07fa714cdb9061461df9a0d60a7f8205550aa26e5cc9bdcb9a35'and correction['laterIssueIsNotTheObservedSavedFailureOrigin']is True
assert correction['nativeArtifactsOrAuthorityOrGuestPayloadChanged']is False
failure=doc(FAMILY/'validation-source-activation-attempt2-context-failure-root-results.json',correction['originalRootFailureSha256'])
for row in failure['evidence']:read(row['path'],row['sha256'],row['bytes'],False)
assert failure['rawOuterExit']==1
assert doc(HOLD/'review-receipt.json')['activationApproved']is False

# Existing actual native authority/source/frozen bytes and unchanged payload/tool closure.
pins=doc(FAMILY/'reviewed-native-v4-validation-bootstrap-pins-v1.json',PINS_SHA)
authority=doc(FAMILY/'native-v4-validation-bootstrap-root-review-v1.json',REVIEW_SHA)
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
 frozen=doc(Path(pin['freezeReceiptPath']),pin['freezeReceiptSha256']);metadata=doc(Path(str(pin['enginePath'])+'.build.json'),pin['receiptSha256'])
 assert frozen['runtimeBackendProof']==metadata['zlibPolicy']['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
 for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']:assert pin[key]==authority['variants'][variant][key]
 assert pin['independentProofIndexSha256']==authority['variants'][variant]['independentProofIndexSha256']
 indexed(Path(pin['independentProofIndexPath']).parent,pin['independentProofIndexSha256'],8)
 read(pin['independentProofResultPath'],pin['independentProofResultSha256'],capture=False)
 native_tuples[variant]={key:pin[key]for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']}
old=FAMILY/'component-validation-v4-rebind-amendment-v1';indexed(old,'cd45865813e06085dcd86065bf816dd18b8203d127df879b1b1e2ca876662a45',8)
for row in doc(old/'unchanged-payloads.json')['payloads']:read(row['sourcePath'],row['sha256'],row['bytes'],False)
base=FAMILY/'component-validation-candidate-v1';tool_seal=doc(base/'tool-seal.json');assert len(tool_seal['toolTrees'])==2 and len(tool_seal['toolLinks'])==22
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
for name in['component-validation-activated-v6','component-validation-activated-v6.staging']:assert not(FAMILY/name).exists()and not(FAMILY/name).is_symlink()
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'],False,True)
result={'schemaVersion':1,'state':'INDEPENDENT_ZLIB350_INDEXED_PEER_SOURCE_REVIEW_PASSED','ownerIndexSha256':OWNER_SHA,'ownerFiles':9,'preparationInputsRehashed':8901,'publisherExactReversibleEdits':4,'parentPreparationContextIndexSha256':PARENT_SHA,'priorIndependentHoldIndexSha256':HOLD_SHA,'resolvedBlocker':'ZVCTX-M2','concreteSourceBlockers':[],'inventoryRoles':summaries,'independentlyReconstructedInventoryFiles':len(inventory),'exactStoredInventoryRowsMatch':True,'storedEvidenceIndexSha256':EVIDENCE_SHA,'storedEvidenceFiles':3,'storedCollectorReportedTerminal':0,'pastRootOrOwnerTerminalObservedByThisReader':False,'storedPositiveFullInventoryTwiceAndTwoNegativeCasesAuthenticatedNotRerun':True,'ownerSourceChecksAuthenticatedNotRerun':13,'independentASTParses':5,'bootstrapIndexSha256':BOOT_SHA,'originalAndStagedIndexedFilesPerView':85,'originalPreparationRowsRehashed':2261,'wrongStagedRow0StillAbsent':True,'correctOriginalRow0Exact':True,'indexedOnlyPeerAllFiveFilesRequired':True,'knownPreparationManifestsRequiredWithoutOptionalFallback':True,'actualNativeCollectionBlockByteUnchanged':True,'actualSourceNative350AndTool632Checked':True,'nativeFrozenCopiesPerVariant':1024,'nativeTuples':native_tuples,'existingRootValidationPinsSha256':PINS_SHA,'existingRootReviewSha256':REVIEW_SHA,'nativeRuntimeBackendProof':{'verified':False,'version':None,'vernum':None},'guestDriverCorpus61Fixtures28Exports40Constants107ByteUnchanged':True,'toolTrees':2,'toolLinks':22,'futureOutputFamily':'component-validation-activated-v6','futureOutputAbsentAtReview':True,'operationalAdmission':False,'activationExecutedOrApprovedByReader':False,'newAuthorityOrNativeOrRuntimeOrGuestProofClaim':False,'ownerImportsFunctionsHelpersTestsPublishersBootstrapNativeVerifiersNodeCompilerGuestHostOrTimingExecuted':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'scope':'Finite source inventory correction only; historical failure/HOLD and all three reviewed native snapshots remain unchanged.','verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({'state':result['state'],'sourceFiles':9,'preparationInputs':8901,'inventoryFiles':8904,'verifiedPaths':len(seen),'blockers':0}))
