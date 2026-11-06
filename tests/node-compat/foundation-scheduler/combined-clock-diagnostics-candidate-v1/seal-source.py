"""Publish this uncompiled Source template only. No native API/action."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent
assert not (OWN/'index.json').exists(),'sealed families remain immutable'
def j(n):return json.loads((OWN/n).read_text())
def d(p):
 b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
source=j('source-check-results.json');pure=j('evidence/pure.stdout.json')
assert source['passed'] and pure['passed'] and j('evidence/pure.terminal.json')['exitCode']==0
assert j('evidence/grammar.json')['passed']
put('future-gates.json',{'schemaVersion':1,'sourceReview':None,'cppSyntaxReview':None,'producerAndAdmissionModel':None,'new357Stage':None,'new357NativeArtifact':None,'privateSpecifierBundlePolicy':None,'actualFourExportComponent':None,'actualRuntimeProof':None,'rootPhase':None,'hostStoreDropObservability':None,'fatalPostTrapSnapshotProof':None,'fullTeardownOrReuseAuthority':None,'adoptionAuthority':None})
put('results.json',{'schemaVersion':1,'state':'UNCOMPILED_COMBINED_CLOCK_DIAGNOSTIC_VARIANT_SOURCE_PREPARED_V1','sourceOnly':True,'sourcePreparationPassed':True,'sourceCheck':source,'pureSnapshotCollectorChecks':pure['checks'],'nodeGrammarChecks':3,
 'parentNativeSourceFiles':355,'proposedNativeSourceFiles':357,'retainedParentNativeFiles':351,'nativeAfterimages':4,'newNativePaths':2,'externalEmbeddingSources':3,'externalEmbeddingAfterimages':1,'exactReversibleEdits':28,
 'parentFrozenArtifactsUnchanged':True,'existing355DiagnosticExports':False,'module':'starling:test-clock-lifecycle','privateMethods':['snapshot'],'bothFlagsDefaultOff':True,'maxTimerLeaseRows':512,'overflowOrIncompleteRejected':True,
 'newCrossTuSymbolsDefinedInSource':['runtime_counts','timer_registry_size','immediate_cache_owned'],'cppSyntaxChecked':False,'nativeSymbolsCompiledOrLinked':False,'inlinePodOdrIdentityProvedByLink':False,'witParsedByTool':False,
 'newProducerRecipeAdmissionImplemented':False,'privateSpecifierBundlePolicyImplemented':False,'allInvalidTaskFixtureImplemented':False,
 'hostResourceStoreObserved':False,'fatalPostTrapSnapshotReturned':False,'cachedImmediateExplicitDropAdded':False,'sameInstanceResetOrTeardownProved':False,
 'nativeHelperInvoked':False,'compilerInvoked':False,'engineInvoked':False,'guestOrClockOrHostWorkloadInvoked':False,'resetOrGcPressureOrCryptoKeyInvoked':False,'actualRootPhase':None,'runtimeOrAdoptionAcceptance':False})
put('source-receipt.json',{'schemaVersion':1,'result':d(OWN/'results.json'),'inputInventory':d(OWN/'proposed-source-inventory.json'),'policyTemplate':d(OWN/'proposed-policy.json'),'references':d(OWN/'references.json'),'derivations':d(OWN/'derivations.json'),'scope':'Finite source/API checks and pure synthetic snapshot models; no copied historical proof trees or operational wrapper.','sourceReview':None,'nativeCompilerOrWorkloadInvoked':False})
rows=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file() and p!=OWN/'index.json':
  row=d(p);row['path']=str(p.relative_to(OWN));rows.append(row)
put('index.json',{'schemaVersion':1,'state':'SEALED_UNCOMPILED_DIAGNOSTIC_SOURCE_TEMPLATE_NOT_NATIVE_OR_ACTION_AUTHORITY_V1','files':rows})
for name in ['index.json','results.json','source-receipt.json']:print(json.dumps(d(OWN/name)))
