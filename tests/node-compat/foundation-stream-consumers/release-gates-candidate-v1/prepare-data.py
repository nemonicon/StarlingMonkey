"""Finite pure-file provenance/lineage preparation, never owner/action imports."""
from pathlib import Path
import hashlib,json,os,re
H=Path(__file__).resolve().parent;S=H/'snapshot';R=H.parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def data(name):return json.loads((S/name).read_bytes())
def put(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n')
base='tests/node-compat/'
tick=data(base+'foundation-scheduler/integration-candidate-v1/policy.json')
classic=data(base+'foundation-classic-streams/trace-integration-candidate-v1/policy.json')
zlib=data(base+'foundation-zlib/native-integration-candidate-v4/policy.json')
consumers=data(base+'foundation-stream-consumers/native-integration-candidate-v2/policy.json')
def transition(before,after):
 b={r['path']:r['sha256']for r in before};a={r['path']:r['sha256']for r in after}
 assert len(a)==len(after)and len(b)==len(before)and set(b)<=set(a)
 return([{'path':p,'beforeSha256':b[p],'afterSha256':a[p]}for p in sorted(b)if b[p]!=a[p]],sorted(set(a)-set(b)))
layers=[d['expectedNativeSourceManifest']for d in [tick,classic,zlib,consumers]]
registrars=[next(row['sha256']for row in layer if row['path']=='builtins/node-compat/register.cpp')for layer in layers]
assert registrars==['19eef9879c94e5232238f6df738d57057d384fa025849ee319fcf51eb06eda2b','2848f059fb5693aa37c54945bff685444c8431007ceaec59d3335d01f7aced4a','ace206308be53e2709a629e1e530ccd1cc0d6d7f86ec6035e0ffc5f4c676c796','879b74c797eac19f07e86fa4e93bfa29578e11d0250fc3fb00439167580af9f6']
lineage={'schemaVersion':1,'state':'FULL_ACTUAL_SOURCE_POLICY_LINEAGE_NOT_METADATA_PROJECTION','registrars':registrars}
for count,rows in zip([306,342,350,355],layers):assert len(rows)==count;lineage['native'+str(count)]=rows
for count,b,a in zip([342,350,355],layers,layers[1:]):lineage['delta'+str(count)],lineage['added'+str(count)]=transition(b,a)
proof_files={
 'tickPolicyBytes':base+'foundation-scheduler/integration-candidate-v1/policy.json',
 'tickPatchBytes':base+'foundation-scheduler/taskqueue-owner-v2/starling-taskqueue-ticks.UNAPPLIED.patch',
 'classicPolicyBytes':base+'foundation-classic-streams/trace-integration-candidate-v1/policy.json',
 'classicPatchBytes':base+'foundation-classic-streams/implementation-candidate-v1-allocation-order-amendment/native-integration.corrected.UNAPPLIED.patch'}
lineage['originalProofHashes']={k:sha((S/v).read_bytes())for k,v in proof_files.items()}
lineage['policies']=[{'path':p,'sha256':sha((S/p).read_bytes())}for p in [*proof_files.values(),base+'foundation-zlib/native-integration-candidate-v4/policy.json',base+'foundation-stream-consumers/native-integration-candidate-v2/policy.json']]
lineage['oracles']={
 'assert':{'sha256':'cbb3bcb3f6bc9e97b12b1a61167483ac0f949de199ae6bd0172926419f4c01a3','required':['assert.mjs','assert-strict.mjs','assert-factories.generated.h','export-manifest.assert.node-v22.14.0.json']},
 'querystring':{'sha256':'e59e05a7cb470970d9bcce230f359cf74bf62a00b094510a2df16d4ab3f901a4','required':['querystring.mjs','querystring-factories.generated.h','export-manifest.querystring.node-v22.14.0.json']},
 'util':{'sha256':'489cb9cf4fbe256201f70e385d4326ea32552d2f2a1f187211d9409e73838816','required':['util.mjs','util-types.mjs','util-core.mjs','util-metadata.mjs','util-unsupported.mjs','export-manifest.util.node-v22.14.0.json','generate-util-factories.mjs','util-factories.generated.h']}}
assert classic['parentExpectedNativeSourceManifest']==tick['expectedNativeSourceManifest']
assert zlib['zlibSourcePolicy']['parentTracePolicySha256']==sha((S/proof_files['classicPolicyBytes']).read_bytes())
assert consumers['streamConsumersSourcePolicy']['parentPolicySha256']==sha((S/(base+'foundation-zlib/native-integration-candidate-v4/policy.json')).read_bytes())
assert consumers['streamConsumersSourcePolicy']['changes']==lineage['delta355']or sorted(consumers['streamConsumersSourcePolicy']['changes'],key=lambda r:r['path'])==lineage['delta355']
put('lineage.json',lineage)

refs={r['path']:r for r in json.loads((H/'source-inputs.preparation.json').read_bytes())['files']}
def reference(path,expected=None,size=None,role='SUPPLEMENTAL_SOURCE_DATA'):
 p=Path(path);assert p.is_file()and not p.is_symlink();raw=p.read_bytes();digest=sha(raw);assert expected is None or expected==digest,(p,expected,digest);assert size is None or len(raw)==size
 row={'path':str(p),'canonicalPath':str(p.resolve()),'sha256':digest,'bytes':len(raw),'roles':[role]}
 if str(p)in refs:assert refs[str(p)]['sha256']==digest
 else:refs[str(p)]=row
 return raw
def archive_reference(row):
 p=Path(row['path']);assert p.is_file()and not p.is_symlink();digest=hashlib.sha256();size=0
 with p.open('rb')as stream:
  for chunk in iter(lambda:stream.read(1048576),b''):digest.update(chunk);size+=len(chunk)
 assert digest.hexdigest()==row['sha256']and size==row['bytes']
 refs[str(p)]={'path':str(p),'canonicalPath':str(p.resolve()),'sha256':digest.hexdigest(),'bytes':size,'roles':['GENUINE_FROZEN_VERIFIER_EXTERNAL_SELECTED_SM_ARCHIVE_HASH_REFERENCE_NO_COPY']}
# A second literal allocator control is a distinct historical m0.8 tuple.
controls=json.loads((H/'historical-controls.sealed.json').read_bytes())
p=Path('/tmp/starling-node-compat/foundations-v10/native-freeze/off-foundations.engine.wasm')
reference(p,'1098e7531004a4ca1b47f2ca80527a01e64cd3392d28d760da37326c08a85154',role='EXACT_DELEGATED_M08_HISTORICAL_CONTROL_ENGINE')
raw=reference(str(p)+'.build.json',role='EXACT_DELEGATED_M08_HISTORICAL_CONTROL_METADATA');m=json.loads(raw);root='/tmp/starling-node-compat/foundations-v10/native-freeze/source'
for row in m['sourceManifest']:reference(Path(root)/row['path'],row['sha256'],role='EXACT_DELEGATED_M08_HISTORICAL_CONTROL_SOURCE')
if not any(row['engineSha256']==m['engineSha256']for row in controls['controls']):controls['controls'].append({'engine':str(p),'sourceRoot':root,'engineSha256':m['engineSha256'],'receiptSha256':sha(raw),'sourceFiles':len(m['sourceManifest']),'enabledField':'allocator-delegated-m08','optional':False,'metadata':m})
put('historical-controls.sealed.json',controls)

pinpath=R/'reviewed-native-v2-validation-bootstrap-pins-v2.json';reviewpath=R/'native-v2-validation-bootstrap-root-review-v2.json'
pins=json.loads(reference(pinpath,'93512520ba6f9ddaba096c09936f16f33462b371b5a9df4cf3315e9a43a5d67b',role='EXTERNAL_FOUR_NATIVE_PINS_DATA_NOT_GUEST_AUTHORITY'))
review=json.loads(reference(reviewpath,'6359ca0b635bb252643f7082cc0df02d6c7fc83cdec5b4fc94e470c231470ce4',role='EXTERNAL_FOUR_NATIVE_REVIEW_DATA_NOT_GUEST_AUTHORITY'))
native_refs=[]
for label,pin in pins['variants'].items():
 assert pin is not None and label==pin['variant']and pin['reviewRequired']is False
 receipt=json.loads(reference(pin['freezeReceiptPath'],pin['freezeReceiptSha256'],role='NATIVE_FROZEN_RECEIPT_'+label))
 archive_reference(receipt['codecArchiveReference'])
 for row in receipt['copies']:
  reference(row['path'],row['sha256'],row['bytes'],'NATIVE_FROZEN_COPY_'+label)
  native_refs.append({'variant':label,'path':row['path'],'sha256':row['sha256'],'bytes':row['bytes']})
 # Original mutable CMakeCache/compileDB entries in prior normal freezes are
 # intentionally NOT followed; the actual immutable frozen copies are authority.
 for key,digest in [('independentProofIndexPath','independentProofIndexSha256'),('independentProofResultPath','independentProofResultSha256')]:reference(pin[key],pin[digest],role='INDEPENDENT_NATIVE_PROOF_'+label)
 assert len(receipt['copies'])==1164
put('native-frozen-inputs.json',{'schemaVersion':1,'state':'FOUR_ACTUAL_FROZEN_NATIVE_INPUT_TUPLES_NO_GUEST_PASS_TRANSFER','rows':native_refs,'mutableOriginalDescriptorsFollowed':False})

old_context=json.loads((R/'component-validation-activated-v2/activation.json').read_bytes())
live=[old_context['liveAdapter'],*old_context['liveWit']]
for row in live:reference(row['path'],row['sha256'],row['bytes'],'LIVE_ADAPTER_OR_STANDARD_WASI_0_2_10_DECLARATION')
package=json.loads((R/'component-validation-activated-v2/component-tool-closure.json').read_bytes())
put('package-endpoints.json',{k:package[k]for k in ['packages','endpoints','packageData']})
for key in ['packages','endpoints','packageData']:
 for row in package[key]:reference(row['path'],row['sha256'],row['bytes'],'PINNED_PACKAGE_VERSION_RESOLUTION_PROVENANCE')
put('external-authority-requirements.json',{'schemaVersion':1,'reviewedPinsPathArgument':None,'reviewedPinsSha256Argument':None,'rootNativeReviewPathArgument':None,'rootNativeReviewSha256Argument':None,'reviewedCurrentNativeFact':{'pinsSha256':sha(pinpath.read_bytes()),'reviewSha256':sha(reviewpath.read_bytes())},'sourceReviewPathArgument':None,'sourceReviewSha256Argument':None,'runtimeActionAuthorityPathArgument':None,'runtimeActionAuthoritySha256Argument':None,'operationalAdmission':False,'actionsApprovedByCandidate':False,'runtimeBackendProof':{'verified':False,'zlibVersion':None,'ZLIB_VERNUM':None}})
put('runtime-authority.template.json',{'schemaVersion':1,'state':'ROOT_AUTHORIZED_FRESH_CONSUMERS355_RELEASE_GATES_V1','familyIndexSha256':None,'consumerValidationSha256':None,'operationalAdmission':False,'allowTiming':False,'allowNativeBuild':False,'noResume':True,'noPriorPassReuse':True,'scopes':{name:{'approved':None,'variant':variant,'output':None,'deadlineMs':None}for name,variant in [('release-off','normal-off'),('allocator-gc','gc-off'),('focused-off','normal-off'),('focused-runtime','normal-runtime'),('focused-gc','gc-off'),('getter','normal-off')]}})
put('source-review.template.json',{'state':'ROOT_REVIEWED_CONSUMERS355_RELEASE_SOURCE_PROPOSAL_V1','proposalIndexSha256':None,'sourceActivationApproved':None,'runtimeActionsApproved':False,'operationalAdmission':False})
put('context.json',{'schemaVersion':1,'nativeConfiguredSourceRoot':'/private/tmp/starling-node-compat/consumers-source-v2','bootstrapRoot':'/private/tmp/starling-node-compat/consumers-source-v2/tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2','bootstrapIndexSha256':'9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378','nativeFrozenSourceRoot':'/tmp/starling-node-compat/production-consumers-v1/native-freeze/source','componentToolRoot':'GENERATED_FAMILY/snapshot','sourcePublicationRoot':None,'originalPreparationRoot':str(H),'liveInputs':live,'httpImplemented':False,'ordinary355OperationalSelectorClosed':True})
put('source-inputs.preparation.json',{'schemaVersion':1,'state':'ORIGINAL_PREPARATION_CONTEXT_ONLY','originalPreparationRoot':str(H),'files':[refs[k]for k in sorted(refs)],'nativeConfiguredSourceRoot':'/private/tmp/starling-node-compat/consumers-source-v2','oldNestedPreparationRowsFollowed':False,'oldMutableNormalCacheOriginalsFollowed':False,'actionsExecuted':False})
print(json.dumps({'lineageCounts':[len(row)for row in layers],'historicalControls':len(controls['controls']),'fourNativeFrozenRows':len(native_refs),'externalUniqueInputs':len(refs),'actionsExecuted':False}))
