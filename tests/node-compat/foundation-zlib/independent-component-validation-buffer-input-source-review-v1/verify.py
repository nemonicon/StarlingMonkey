"""Independent three-input correction source/failure reader. No owner imports/actions."""
from pathlib import Path
import ast,hashlib,json,os,re,stat
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent
OWNER=FAMILY/'component-validation-buffer-input-amendment-v1';OWNER_SHA='b0ced580d2e20a482680455f86eed9126c4120639d6100f28b03064bc1053d5f'
PARENT=FAMILY/'component-validation-tooling-closure-amendment-v1';PARENT_SHA='daa7d28a7105f878a9465c4eb0fea2edaa3ef6329a15baafcabd7ccc28a0fd0c'
V7=FAMILY/'component-validation-activated-v7';V7_SHA='d67971d0fbf2e116c646a0411bf3ffc4d3209475033c2d2209c443deb9802c9e'
FAILURE_SHA='7460b94d1a151b897bb4ecdd2689ddf6d61e9dee392724e413172e4cd2da980d'
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
indexed(OWNER,OWNER_SHA,16);source=doc(OWNER/'source-receipt.json');manifest=doc(OWNER/'input-freeze.json');assert len(manifest['inputs'])==source['preparationInputs']==11086 and manifest['nativeOrGuestExecuted']is False
for row in manifest['inputs']:read(OWNER/row['path'],row['sha256'],row['bytes'],False)
for name,digest in source['parentIndices'].items():indexed(FAMILY/name,digest)
assert source['parentIndices'][PARENT.name]==PARENT_SHA and source['parentIndices'][V7.name]==V7_SHA
assert source['guestInputEdits']==source['publisherEdits']==3 and source['allReverseExact']is True and source['hostChecks']==12 and source['syntaxChecks']==8
assert source['nativeBufferContractDriverCorpusNodeOraclesAndRootAuthorityUnchanged']is True and source['bootstrapOrVerifierOrActivationOrCompilerOrNativeOrComponentizerOrGuestOrHostTargetOrTimingExecuted']is False
before_after={}
for name in['component.mjs','activate.py']:
 proof=doc(OWNER/(name+'.proof.json'));before=read(proof['beforePath'],proof['beforeSha256']).decode();after=read(OWNER/name,proof['afterSha256']).decode();current=before
 assert len(proof['edits'])==3 and proof['reverseExact']is True
 for edit in proof['edits']:assert edit['count']==1 and current.count(edit['old'])==1;current=current.replace(edit['old'],edit['new'])
 assert current==after
 for edit in reversed(proof['edits']):assert current.count(edit['new'])==1;current=current.replace(edit['new'],edit['old'])
 assert current==before;before_after[name]=(before,after)
guest_old,guest_new=before_after['component.mjs'];publisher_old,publisher_new=before_after['activate.py']
guest_proof=doc(OWNER/'component.mjs.proof.json');assert guest_proof['beforePath']==str(V7/'component.mjs')
expected_changes=[('Buffer.from([1])','Buffer.from(new Uint8Array([1]))'),('Buffer.from([0,1,2,3,254,255])','Buffer.from(new Uint8Array([0,1,2,3,254,255]))'),('Buffer.from([i])','Buffer.from(new Uint8Array([i]))')]
assert [(row['old'],row['new'])for row in guest_proof['edits']]==expected_changes
assert len(re.findall(r'Buffer\.from\(\s*\[',guest_old))==3 and not re.search(r'Buffer\.from\(\s*\[',guest_new)
assert guest_new.count('export ')==guest_old.count('export ')==5
assert "OUTPUT=HERE.parent/'component-validation-activated-v8'"in publisher_new and "payload['component.mjs']=regular(HERE/'component.mjs')"in publisher_new
assert "'mandatoryComponentToolClosureAmendmentIndexSha256':'"+PARENT_SHA+"'"in publisher_new and "'mandatoryBufferFixtureInputAmendmentIndexSha256':own_sha"in publisher_new
for name in['inventory.py','runtime-preflight.template.mjs','component-tools.mjs','component-tool-closure.json']:assert read(OWNER/name)==read(PARENT/name)
def collection(code):return code[code.index(' actual={};headers={};inputs={}'):code.index(' names=[',code.index(' actual={};headers={};inputs={}'))]
assert collection(publisher_new)==collection(publisher_old)
syntax=doc(OWNER/'evidence/syntax-results.json');assert len(syntax['checks'])==8;ast_count=0
for row in syntax['checks']:
 if row['kind']=='Python AST':ast.parse(read(OWNER/row['path']).decode());ast_count+=1
 else:assert row['kind']=='Node --check'and row['status']==0 and row['stdout']==row['stderr']==''
assert ast_count==4

# Authenticate actual failure streams, exact source frame and physical output.
failure=doc(FAMILY/'normal-codec-validation-attempt1-fixture-failure-root-results.json',FAILURE_SHA)
assert failure['rawExitCode']==1 and failure['sourceIndexSha256']==V7_SHA and len(failure['references'])==11
assert failure['componentPublished']is failure['deploymentExecuted']is False and failure['codecCaseResults']==0 and failure['sourceFailureRecheckPassed']is True
for row in failure['references']:read(row['path'],row['sha256'],row['bytes'],False)
for row in failure['outputLinks']:assert os.readlink(row['path'])==row['linkText']and str(Path(row['path']).resolve(strict=True))==row['resolvedTarget']
output=Path(failure['output']);stderr=read('/tmp/starling-node-compat/zlib-v4-normal-off-codec-validation-v1.stderr.log').decode();terminal=doc('/tmp/starling-node-compat/zlib-v4-normal-off-codec-validation-v1.terminal.json')
assert terminal['rawExitCode']==1 and terminal['argv'][1]==str(V7/'run-validation.mjs')and terminal['argv'][2:]==[V7_SHA,'normal-off']
assert failure['observedError']in stderr and 'from@<node-profile-factory>:191:11'in stderr and '@source.js:564:30'in stderr
bundle_raw=read(output/'guest.bundle.mjs');bundle=bundle_raw.decode();lines=bundle.splitlines();assert lines[563].strip()=='const snapshotInput = Buffer.from(['
assert re.search(r'const snapshotInput = Buffer\.from\(\[\s*0,\s*1,\s*2,\s*3,\s*254,\s*255\s*\]\)',bundle)
assert 'import __smBuiltin0' in bundle and 'from "node:zlib"'in bundle
assert bundle.index('const snapshotInput = Buffer.from([')<bundle.index('const snapshotCompressed = __smBuiltin0.gzipSync(snapshotInput)')
bundle_report=doc(output/'bundle.json');assert bundle_report['code'].encode()==bundle_raw and bundle_report['sha256']==sha(bundle_raw)
failure_recheck=doc(output/'failure-source-recheck.json');assert failure_recheck['passed']is True and failure_recheck['completePass']is False and failure['observedError']in failure_recheck['originalFailure']['message']
for name in['results.json','completion.json','zlib-validation.component.wasm']:assert not(output/name).exists()
ordinary=[];links=[]
for directory,dirs,files in os.walk(output,followlinks=False):
 for name in dirs+files:
  path=Path(directory)/name
  if path.is_symlink():links.append(str(path));continue
  if path.is_file():ordinary.append(str(path))
 dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
expected_output={row['path']for row in failure['references']if row['path'].startswith(str(output)+'/')}
assert set(ordinary)==expected_output and len(ordinary)==6 and links==[failure['outputLinks'][0]['path']]

# Stored host evidence is explicitly scoped to facade/reference/Node doubles.
host=doc(OWNER/'evidence/host-results.json');test=read(OWNER/'host-regression.mjs').decode();assert host['passed']==len(host['checks'])==12 and len(host['inputs'])==5
assert host['noNativeBackendOrComponentProof']is True and host['nativeOrGuestOrBootstrapOrComponentizerExecuted']is False
assert host['originalWrongConstructorModuleCount']==6 and host['correctedRefusalRecords']==68
assert host['codecKernel']=='PINNED HOST NODE CODEC TEST DOUBLE'and host['hexKernel']=='JS REFERENCE TEST DOUBLE'
assert len(host['codecCalls'])==3 and [(row['format'],row['encode'],row['inputBytes'],row['limit'],row['testDouble'])for row in host['codecCalls']]==[(1,True,6,16777216,True),(1,False,26,16777216,True),(1,False,40,16777216,True)]
assert host['snapshot']['inputHex']==host['snapshot']['plainHex']=='00010203feff'and len(bytes.fromhex(host['snapshot']['compressedHex']))==26
assert host['ordinaryGcOperations']==[format(i,'02x')for i in range(8)]
meta=doc('/tmp/starling-node-compat/production-zlib-v4/native-freeze/normal-off.engine.wasm.build.json','59942584d9aed799776913f158904abf6b4beb8feac04b56f28a813dfdced46e')
frozen=Path('/tmp/starling-node-compat/production-zlib-v4/native-freeze/source');native_sources={row['path']:row['sha256']for row in meta['sourceManifest']}
for row in host['inputs']:
 read(row['path'],row['sha256'],row['bytes'],False)
 if Path(row['path']).is_relative_to(frozen):assert native_sources[str(Path(row['path']).relative_to(frozen))]==row['sha256']
 else:assert row['sha256']=='ed04116feed90ae3827cbee6c45022a7c12ec5acdabb7cc5f850bfd04e8dd627'
buffer=read(frozen/'builtins/node-compat/buffer-facade.mjs').decode();start=buffer.index('Buffer.from = function from(');end=buffer.index('Buffer.isBuffer',start);from_body=buffer[start:end]
assert 'if (value instanceof AB)'in from_body and 'if (value instanceof U8)'in from_body and "reject('from input kind')"in from_body and 'Array.isArray'not in from_body
assert "nodeZlib[names[format]](input,{maxOutputLength:limit})"in test and "kernel={backendInfo()"in test and 'process.versions.zlib'in test
assert "'JS REFERENCE TEST DOUBLE'"in test and "'PINNED HOST NODE CODEC TEST DOUBLE'"in test
assert "assert.equal(codecCalls.length,before)"in test and "assert.equal(codecCalls.length-beforeKernel,2)"in test
assert "assert.equal(values.filter(row=>row.error.fields.module.value==='node:buffer').length,6)"in test
assert 'for(const row of guest.initializationRefusals)'in test and "module:'node:zlib'"in test and 'row.error.fields[key].own,true'in test
assert "old.replace(/^import[^\\n]*\\n/gm,'').replace(/^export /gm,'')"in test
assert 'refusalRecords'not in host and 'initializationRefusals'not in host
disabled=FAMILY/'disabled-validation-candidate-v1';indexed(disabled,'89a38793670ce6066970a6cca288abf841ba194ddd4b6eb04a56edec363f4dd2',10)
assert not re.search(r'Buffer\.from\(\s*\[',read(disabled/'fixtures.mjs').decode())

# Preserve genuine native/tool/payload authority; no old result is transferred.
v7=doc(V7/'input-freeze.json');assert len(v7['inputs'])==11036 and len(v7['toolTrees'])==2 and len(v7['toolLinks'])==22
for row in v7['inputs']:read(V7/row['path'],row['sha256'],row['bytes'],False)
config=doc(V7/'activation.json');closure=doc(OWNER/'component-tool-closure.json',config['componentToolClosureSha256'])
for group in['files','packages','endpoints','packageData']:
 for row in closure[group]:read(row['path'],row['sha256'],row['bytes'],False);assert str(Path(row['path']).resolve(strict=True))==row['realPath']
pins=doc(V7/'reviewed-pins.json','b61e1f389b49d9e69c4bb1a3fd7b1314d16462a328627f94d141a39454b971cc');authority=doc(V7/'root-review.json','7274a874ffd95d975fa84c7ad7213b52ff799c06de8a717f522aa07766b975a5')
assert authority['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}and authority['operationalAdmission']is False
native_tuples={}
for variant in['normal-off','gc-off','disabled-off']:
 pin=pins['variants'][variant];assert len(pin['frozenFiles'])==1024
 for row in pin['frozenFiles']:read(row['path'],row['sha256'],row['bytes'],False)
 read(pin['enginePath'],pin['engineSha256'],pin['engineBytes'],False);native_tuples[variant]={key:pin[key]for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']}
 assert native_tuples[variant]==config['actual'][variant]
coverage=FAMILY/'component-validation-bootstrap-coverage-amendment-v1';assert "payload['run-validation.mjs']=regular(COVERAGE/'proposed/run-validation.mjs')"in publisher_new
assert read(V7/'run-validation.mjs')==read(coverage/'proposed/run-validation.mjs')
for tree in v7['toolTrees']:
 root=Path(tree['path']);members=[]
 for directory,dirs,files in os.walk(root,followlinks=False):
  for name in sorted(dirs+files):
   path=Path(directory)/name;kind='symlink'if path.is_symlink()else'directory'if path.is_dir()else'file'if path.is_file()else None;assert kind;members.append({'path':str(path.relative_to(root)),'kind':kind})
   if kind=='file':read(path,capture=False)
  dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
 assert sorted(members,key=lambda row:row['path'])==tree['entries']
for row in v7['toolLinks']:assert os.readlink(row['path'])==row['linkText']and str(Path(row['path']).resolve(strict=True))==row['resolvedTarget']
for name in['component-validation-activated-v8','component-validation-activated-v8.staging']:assert not(FAMILY/name).exists()and not(FAMILY/name).is_symlink()
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'],False,True)
r={'schemaVersion':1,'state':'INDEPENDENT_ZLIB350_BUFFER_INPUT_SOURCE_REVIEW_PASSED','ownerIndexSha256':OWNER_SHA,'ownerFiles':16,'preparationInputsRehashed':11086,'exactGuestReversibleInputEdits':3,'guestInputEdits':expected_changes,'exactPublisherReversibleEdits':3,'supportFilesByteExactToDaa7':4,'guestExportsUnchanged':5,'driverCorpus61Fixtures28Exports40Constants107Unchanged':True,'actualNativeCollectionBlockByteUnchanged':True,'failedAttemptRootReceiptSha256':FAILURE_SHA,'failedAttemptReportedTerminal':1,'pastRootTerminalObservedByThisReader':False,'failureReferencesRehashed':11,'failureOutputLinkChecked':1,'failureOutputRegularFilesObserved':6,'failureAttributedSourceFrame':564,'failureObservedOrdinaryBufferUnsupportedInput':True,'failedAttemptComponentOrDeploymentOrCodecCaseResultObserved':False,'failureSourceRecheckStoredPassed':True,'nativeCodecFailureClaim':False,'hostChecksAuthenticatedNotRerun':12,'hostNodeCodecTestDoubleCallsReported':3,'hostOldWrongBufferModuleCountReported':6,'hostCorrectedRefusalCountReported':68,'hostStoredSnapshotRoundtripHex':'00010203feff','hostStoredOrdinaryOperations':[format(i,'02x')for i in range(8)],'hostReferenceAndFrozenFacadeInputsRehashed':5,'hostRefusalFull68RawRecordsRetained':False,'hostPerRecordAssertionsInspectedNotIndependentlyDecoded':True,'hostBackendVersionObservationNeverTreatedAsGuest':True,'hostOrNativeOrGuestProofTransferred':False,'ownerSyntaxChecksAuthenticatedNotRerun':8,'independentPythonASTParses':4,'actualV7IndexSha256':V7_SHA,'actualV7ConsumedRowsRehashed':11036,'sourceToolTrees':2,'sourceToolLinks':22,'nativeFrozenCopiesPerVariant':1024,'actualNativeTuples':native_tuples,'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},'futureOutputFamily':'component-validation-activated-v8','futureOutputAbsentAtReview':True,'concreteSourceBlockers':[],'sourceReadyForRootActivationReview':True,'operationalAdmission':False,'ownerImportsHostTestsHelpersPreflightsBootstrapNodeCodecGuestNativeHostTargetActionsOrTimingExecuted':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'scope':'Three public fixture argument corrections and coherent source publisher only; stored host data uses explicit reference/Node test doubles, and the preserved original attempt is a fixture-input failure.','verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(r,stream,indent=2);stream.write('\n')
print(json.dumps({'state':r['state'],'files':16,'inputs':11086,'verifiedPaths':len(seen),'blockers':0}))
