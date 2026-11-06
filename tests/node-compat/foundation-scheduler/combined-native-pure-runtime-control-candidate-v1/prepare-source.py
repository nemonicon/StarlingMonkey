"""Read/hash/text derivation only; no application/API/helper invocation."""
from pathlib import Path
import json,hashlib
OWN=Path(__file__).resolve().parent;S=OWN.parent;REPO=S.parents[2]
def row(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def dump(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
caller=S/'combined-native-component-caller-candidate-v1';old=json.loads((caller/'references.json').read_bytes());clock=json.loads((S/'clock-v13-runtime-candidate-v2/references.json').read_bytes())
pure=S/'independent-combined355-pure-component-artifact-review-v1';proof=json.loads((pure/'results.json').read_bytes())
assert row(pure/'index.json')['sha256']=='0dc8bf11f2cc5d153a7a062131784af84cb3e5f63eddfe26b97437461cd70c2c'
generated=proof['generatedFiles'];art=proof['artifacts']
refs={k:old[k]for k in ['node','nativeApi','nativeApiSourceIndex','nativeApiSourcePeer','nativeEngine','nativeMetadata','freezeReceipt','readOnlyConfig','actualReadOnlyData','actualReadOnlyReview','actualBootstrapReview','monitorIndex','monitorEntry','python','packageInventory','loaderPackageRoot']}
refs.update(schemaVersion=1,outputRoot='/private/tmp/starling-node-compat/combined355-pure-control-v1',
 callerSourceIndex=row(caller/'index.json'),callerSourceInputs=row(caller/'source-inputs.json'),callerEntry=row(caller/'entry.mjs'),
 actualPureReview={'index':row(pure/'index.json'),'result':row(pure/'results.json')},actualPureContract=row(pure/'result-contract.json'),
 component=art['component'],fixtureSource=art['fixtureSource'],fixtureWit=art['fixtureWit'],generated=generated,
 wasmtime=clock['wasmtime'],waveDonor=row(S/'clock-v13-runtime-candidate-v2/wave.mjs'))
dump('references.json',refs)
helpers=[REPO/'tests/node-compat/foundation-crypto/ownership-component-candidate-v1'/x for x in ['durable.mjs','authority.mjs','durable-host.mjs']]
child_files=[refs[k]for k in ['node','wasmtime','component','fixtureSource','fixtureWit','nativeEngine','nativeMetadata','actualReadOnlyData']]+list(generated.values())+[refs['actualPureContract']]+[row(p)for p in helpers]
dump('source-inputs.json',{'schemaVersion':1,'files':child_files,'families':[refs['actualPureReview']['index']],
 'parentOnlyBoundary':refs['callerSourceInputs'],'parentFullNativePackageProtection':True,
 'childScope':'own full Source/Root/peer/per-pure proof/helpers/native descriptor and exact component/glue/core/fixture loading tuple; parent owns full original native/package read-only API and bookends',
 'childNativeApiInvocations':0,'allActionAuthoritiesUnissued':True})
wave=Path(refs['waveDonor']['path']).read_bytes();(OWN/'wave.mjs').write_bytes(wave)
prefix=(caller/'entry.mjs').read_text().split('export function nativeRecordModel',1)[0]
prefix=prefix.replace("const ORIGINAL='"+str(caller)+"';", "const ORIGINAL='"+str(OWN)+"';")
tail=(OWN/'entry-body.txt').read_text();(OWN/'entry.mjs').write_text(prefix+tail)
dump('source-derivations.json',{'schemaVersion':1,'stdlibCapturePrefixDonor':row(caller/'entry.mjs'),'prefixEndsBefore':'export function nativeRecordModel',
 'ownOriginalPathSubstitution':{'from':str(caller),'to':str(OWN)},'captureBehaviorUnchanged':True,'parentOnlyActualNativeModel':refs['callerEntry'],
 'waveByteIdentical':row(OWN/'wave.mjs'),'waveDonor':refs['waveDonor'],'operationalCodeOrMetadataRebound':False})
dump('future-config.template.json',{'schemaVersion':1,'state':'COMBINED355_PURE_CONTROL_CONFIG_V1','sourceIndex':None,'rootAuthority':None})
dump('future-root-authority.template.json',{'schemaVersion':1,'state':'UNISSUED_COMBINED355_PURE_CONTROL_ROOT_TEMPLATE_V1','requiredIssuedState':'ROOT_REVIEWED_COMBINED355_PRELIMINARY_PURE_CONTROL_V1','sourceIndex':None,'sourceIndependentReview':None,'entry':None,'externalController':None,
 'actualPureReview':None,'actualPureContract':None,'component':None,'fixtureSource':None,'readOnlyConfig':None,'outputRoot':None,'externalRoot':None,
 'parentNativeReadOnlyApiAllowed':None,'nodeFixtureOracleAllowed':None,'pureGeneratedImportAllowed':None,'pureRunAllowed':None,'stockWasmtimeAllowed':None,
 'parentDeadlineSeconds':1200,'childDeadlineMs':60000,'parentNativeApiCalls':1,'childNativeApiCalls':0,
 'nativeSourceFiles':355,'externalEmbeddingSources':3,'fullMetadataFields':80,'selectedWholeManifests':11,
 'nodeOracleCalls':3,'retainedJcoCalls':3,'freshJcoCalls':1,'freshWasmtimeCalls':3,'componentValues':7,'totalValues':10,
 **{k:False for k in ['resourceRuntimeAllowed','otherGuestAllowed','componentConstructionAllowed','transpileOrMappingAllowed','nativeBuildAllowed','nativeFreezeAllowed','keyOrCryptoAllowed','gcOrOomOrFaultAllowed','unsafeResetOrReuseAllowed','allSixFixtureGateComplete','fullSeventeenGateComplete','fullNextCompatibility','deploymentAccepted','adoptionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']}})
dump('future-source-review-contract.json',{'schemaVersion':1,'requiredState':'INDEPENDENT_COMBINED355_PURE_RUNTIME_CONTROL_SOURCE_REVIEW_PASSED_V1','requiredOwnIndexField':'sourceIndexSha256','requiredFixedValues':{'schemaVersion':1,'sourceOnly':True,'sourceReviewPassed':True,'ownerActionsInvoked':False,'hostActionsInvoked':False,'runtimeActionsInvoked':False,'nativeSourceFiles':355,'externalEmbeddingSources':3,'fullMetadataFields':80,'selectedWholeManifests':11},'actualProof':None,'grantsRuntimeAuthority':False})
print(json.dumps({'sourceOnly':True,'targetActionsInvoked':False,'childDirectFiles':len(child_files),'parentBoundary':refs['callerSourceInputs'],'waveBytes':len(wave)}))
