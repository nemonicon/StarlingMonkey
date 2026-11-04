#!/usr/bin/env python3
"""Independent source/data review only; no owner imports or action execution."""
import ast
import hashlib
import json
from pathlib import Path
import re
import stat

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
OWNER=FAMILY/'component-validation-bootstrap-coverage-amendment-v1'
BASE=FAMILY/'component-validation-candidate-v1'
CONTROL=FAMILY/'component-validation-control-evidence-amendment-v1'
PRODUCER=FAMILY/'native-integration-candidate-v3'
seen={}
def checked(path,pin=None,size=None):
 path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
 digest=hashlib.sha256()
 with path.open('rb')as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
 after=path.lstat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
 value=digest.hexdigest()
 if pin is not None:assert value==pin,str(path)
 if size is not None:assert before.st_size==size,str(path)
 seen[str(path)]={'path':str(path),'sha256':value,'bytes':before.st_size};return value
def load(path):checked(path);return json.loads(Path(path).read_bytes())
def indexed(root,pin,count):
 checked(root/'index.json',pin);doc=load(root/'index.json');assert len(doc['files'])==count
 for row in doc['files']:checked(root/row['path'],row['sha256'],row['bytes'])
 return doc
indexed(OWNER,'a376c32b640df35ea563a722b9df480569bf08367ade8752876addc3d1423191',15)
indexed(BASE,'a7eca2349282a29649806c327c41ea19f01be9673c0bd7c72201f30672819816',25)
indexed(CONTROL,'fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353',8)
indexed(PRODUCER,'3929e24d4fe423dc388d3706b975c4704739943b7fcf78c49feb8fda79e03710',81)
manifest=load(OWNER/'input-freeze.json');assert len(manifest['inputs'])==8640
for row in manifest['inputs']:checked((OWNER/row['path']).resolve(),row['sha256'],row['bytes'])
def proof(name,parent_path,new_path,count):
 document=load(OWNER/name);before=Path(parent_path).read_text();after=Path(new_path).read_text()
 assert hashlib.sha256(before.encode()).hexdigest()==document['beforeSha256']and hashlib.sha256(after.encode()).hexdigest()==document['afterSha256']
 assert len(document['edits'])==count and document['reverseExact']is True
 value=before;positions=[]
 for edit in document['edits']:
  assert edit['count']==1 and value.count(edit['old'])==1;at=value.index(edit['old']);positions.append(at);value=value[:at]+edit['new']+value[at+len(edit['old']):]
 assert value==after
 for at,edit in reversed(list(zip(positions,document['edits']))):
  assert value[at:at+len(edit['new'])]==edit['new'];value=value[:at]+edit['old']+value[at+len(edit['new']):]
 assert value==before
 return after
component=proof('component-proof.json',BASE/'component.mjs',OWNER/'proposed/component.mjs',2)
driver=proof('driver-proof.json',CONTROL/'proposed/run-validation.mjs',OWNER/'proposed/run-validation.mjs',14)
publisher=proof('activation-proof.json',CONTROL/'activate.py',OWNER/'activate.py',9)
checker=(OWNER/'coverage-checks.mjs').read_text()
assert component.count('await import(aliasId)')==2 and component.count('await import(canonicalId)')==2
for text in['aliasNamespaceCached:alias===aliasAgain','canonicalNamespaceCached:canonical===canonicalAgain','canonicalStaticNamespace:canonical===namespace','sameAliases:names.every(name=>alias[name]===namespace[name])']:assert text in component
assert 'alias===namespace'not in component and 'alias===canonical'not in component
assert "function namespace(value,expectedCalls){assertRunCounter(value,expectedCalls);"in driver
assert "function checkCase(index,value,expectedCalls){assertRunCounter(value,expectedCalls);"in driver
assert 'Number.isSafeInteger(value.calls)'in checker and 'assert.equal(value.calls, expected' in checker
for text in["namespace(moduleObservation.value,0)",'let retainedCalls=0',"'retained-'+round,++retainedCalls",'namespace(checkpoint.value,retainedCalls)','assert.equal(retainedCalls,161)',".value,0);let freshCalls=0","'fresh-Jco',++freshCalls",'assert.equal(freshCalls,61)','namespace(freshCheckpoint.value,freshCalls)',"'fresh-Wasmtime',1",'let gcCalls=0',"'ordinary-GC',++gcCalls",'assert.equal(gcCalls,3)','namespace(gcCheckpoint.value,gcCalls)',"records.length,variant==='normal-off'?283:3"]:assert text in driver,text
assert "for(const key of['aliasNamespaceCached','canonicalNamespaceCached','canonicalStaticNamespace'"in driver
for text in['fields.errno.own, true','fields.errno.type, \'number\'','Number.isSafeInteger(fields.errno.value)','assert.deepEqual(fields.operation, absent','assert.deepEqual(fields.errno, absent',"{own:true, type:'string', value:operation}"]:assert text in checker,text
assert "new Set(['ERR_OUT_OF_RANGE', 'ERR_INVALID_ARG_TYPE', 'ERR_SM_NODE_UNSUPPORTED'])"in checker
assert "row.id === 'unknown-option-level'"in checker and "row.id === 'ordinary-string-input-refusal'"in checker
assert 'assertErrorContract(value.error,row,contract.profileVersion)'in driver
assert "assertErrorContract(value.roundtrip.error,{operation:decoder,profileCode:'ERR_OUT_OF_RANGE'}"in driver
assert "paths.add(join(output,'package.json'))"in driver and 'outputLinks:[moduleLink]'in driver
assert 'readlink(moduleLink.path),moduleLink.linkText'in driver and 'realpath(moduleLink.path),moduleLink.resolvedTarget'in driver
assert 'decoded.equals(expected)'in driver and 'compressedByteIdentityRequired:false'in driver
assert 'directPrivateBackendObserved:false'in driver and 'runtimeBackendMetadataRemainsUnverified:true'in driver
assert "key==='ZLIB_VERNUM'?{type:'number',value:admission.expectedHeader.vernum}:expected"in driver
assert "nodeZlib[decoder](bytes"in driver and "maxOutputBytes:64*1024*1024"in driver
assert "BOOTSTRAP_INDEX='3929e24d4fe423dc388d3706b975c4704739943b7fcf78c49feb8fda79e03710'"in publisher
assert "DECLARED=Path('/tmp/starling-node-compat/zlib-source-v3')"in publisher
assert "PACKET='tests/node-compat/foundation-zlib/native-integration-candidate-v3'"in publisher
assert "OUTPUT=HERE.parent/'component-validation-activated-v3'"in publisher
assert "assert bootstrap_sha==BOOTSTRAP_INDEX"in publisher
assert publisher.index('boot_rows=indexed(bootstrap,bootstrap_sha)')<publisher.index("spec_from_file_location('actual_zlib350_validation_bootstrap'")
assert "payload['component.mjs']=regular(HERE/'proposed/component.mjs')"in publisher and "payload['coverage-checks.mjs']=regular(HERE/'coverage-checks.mjs')"in publisher
assert "(CONTROL,control_rows,CONTROL_INDEX)"in publisher
assert "'mandatoryControlEvidenceAmendmentIndexSha256':CONTROL_INDEX"in publisher and "'mandatoryBootstrapCoverageAmendmentIndexSha256':own_sha"in publisher
assert "stage.mkdir(exist_ok=False)"in publisher and "open('xb')"in publisher and 'recheck()'in publisher
receipt=load(PRODUCER/'source-receipt.json')
assert receipt['recipeSha256']=='b8b26474682c4236a6f1b02337f7b100a3a79adab5c95c2c7a96a0d0176b546e'
checked(PRODUCER/'source/tests/node-compat/build-engine.sh',receipt['recipeSha256'])
node=load(BASE/'node-results.json');assert len(node['cases'])==61 and len(node['dataFiles'])==28 and len(node['inventory']['exports'])==40 and len(node['inventory']['constants'])==107
for row in node['dataFiles']:checked(row['path'],row['sha256'],row['bytes'])
assert node['inventory']['zMaxChunk']=={'type':'number','valueEncoding':'positive-infinity'}
assert node['inventory']['vernum']=={'type':'number','value':4865}
future=load(BASE/'future-authority.json');assert future['reviewedPins']is None and future['rootReview']is None and all(v is None for v in future['variants'].values())
for family in['component-validation-activated-v1','component-validation-activated-v2','component-validation-activated-v3']:
 assert not(FAMILY/family).exists()and not(FAMILY/(family+'.staging')).exists()
tests=load(OWNER/'evidence/source-tests.json');assert tests['passed']==81 and len(tests['checks'])==81
syntax=load(OWNER/'evidence/syntax-results.json');assert len(syntax['checks'])==7
for row in syntax['checks']:
 checked(OWNER/row['path'],row['sha256'])
 if row['kind']=='Node --check':assert row['status']==0 and row['stdout']==row['stderr']==''
python=[]
for path in OWNER.glob('*.py'):ast.parse(path.read_text());python.append(path.name)
for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])
report={'schemaVersion':1,'state':'INDEPENDENT_ZLIB_COMPONENT_COVERAGE_REBIND_SOURCE_REVIEW_PASSED_NO_ACTIONS','ownerIndexSha256':checked(OWNER/'index.json'),'ownerFiles':15,'preparationInputs':8640,'guestForwardReverseEdits':2,'driverForwardReverseEdits':14,'publisherForwardReverseEdits':9,'findingsResolved':['ZVAL-M1-call-counters','ZVAL-M2-native-errno-facade-operation','ZVAL-M3-same-ID-namespace-cache'],'callLifecycle':{'initialModule':0,'retainedCodecRange':[1,161],'retainedCheckpoints':[61,111,161],'freshJcoInitial':0,'freshJcoRange':[1,61],'eachFreshWasmtime':1,'gcRetainedRange':[1,3],'finalNormalCodecRecords':283,'finalGcCodecRecords':3},'nativeErrorContract':'Own string code/module/profile + own safe-integer numeric errno + absent/undefined operation','facadeErrorContract':'Own string code/module/profile + exact finite operation + absent/undefined errno','namespaceContract':'Repeat each canonical/bare ID; require per-ID cache and canonical dynamic/static identity; cross-ID bindings equal, cross-ID namespace identity not assumed.','producerIndexSha256':checked(PRODUCER/'index.json'),'recipeSha256':receipt['recipeSha256'],'declaredStage':'/tmp/starling-node-compat/zlib-source-v3','futureOutput':'component-validation-activated-v3','genuineBootstrapAPIPreserved':True,'old3ffNotAdmittedByPublisher':True,'fd3PackageAndOutputLinkControlsPreserved':True,'all61NodeOracles28ByteFiles40Exports107ConstantsUnchanged':True,'publicVernumRemainsSourceCoupledInference':True,'metadataBackendProofNotPromoted':True,'futureActualPinsNullAndOutputAbsent':True,'ownerStoredChecksAuthenticatedNotRerun':{'source':81,'syntax':7},'pythonASTParsed':sorted(python),'concreteSourceBlockers':[],'ownerHelpersOrTestsOrBootstrapOrNativeVerifierOrBundleOrCompilerOrGuestOrHostOrCodecExecuted':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'limitations':['Source mechanism review only; actual native freezes/independent review/Root bootstrap authority/source activation and codec outcomes remain separate.','No direct private backend observation, complete Node/zlib, temporary-root isolation, GC-in-codec, reset/ALS or cost claim.','Existing finite deadline, large payload and whole-byte comparison resource adequacy remain empirical future gates.'],'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps({'state':report['state'],'verifiedPaths':len(seen),'ownerFiles':15,'preparationInputs':8640,'proofEdits':[2,14,9],'concreteSourceBlockers':0}))
