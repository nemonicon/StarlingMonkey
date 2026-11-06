"""Own compact Source publication only. No phase/native/compiler API."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent

def data(n):return json.loads((OWN/n).read_bytes())
def desc(p):
 b=Path(p).read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
check=data('source-check-results.json');assert check['state']=='SOURCE_DATA_HOST_PURE_GRAMMAR_CHECKS_PASSED_V1'
for k in ['ownerApiInvoked','fixtureOrGuestImported','compilerInvoked','nativeClockOrTaskInvoked']:assert check[k]is False
for k,v in data('future-gates.json').items():
 if k not in ['schemaVersion','state']:assert v is None
save('results.json',dict(schemaVersion=1,state='COMBINED_CLOCK_DIAGNOSTIC_FIXTURE_SOURCE_SEALED_UNREVIEWED_V1',sourceOnly=True,sourceReviewPassed=None,diagnosticSourceIndex=data('references.json')['diagnosticSourceIndex'],lifecycleFixtureSourceIndex=data('references.json')['lifecycleFixtureSourceIndex'],fixtureCount=3,resourceCases=7,privateNativeApiUsed=['snapshot'],scalarWitOnly=True,sameInstanceRequired=True,selectedInterfaces=data('source-plan.json')['selectedInterfaces'],nativeExpectationsAreSourceCoupledNotObserved=True,sourceChecks=check['checks'],currentDirectInputs=check['currentDirectInputs'],fullSourceFamilies=check['fullSourceFamilies'],hostPureAndGrammarCommands=check['hostCommands'],syntheticModelChecks=check['syntheticResult']['checks'],allInvalidNativeSetupAvailable=False,nativeOffsetExportAvailable=False,hostStoreDeathObservable=False,fatalFinalNativeSnapshotAvailable=False,cachedImmediateExplicitDropImplemented=False,current355PrivateModuleAvailable=False,hashHmac357Interchangeable=False,fullLifecycleGateAccepted=False,originalSeventeenGatesPreserved=True,publicProfilePromotion=False,ownerActionsInvoked=False,hostActionsInvoked=False,compilerInvoked=False,fixtureOrGuestImported=False,nativeTaskOrClockInvoked=False,sourceReview=None,rootAuthority=None,actualNativeArtifact=None,actualComponent=None,actualRuntime=None,adoptionAuthority=None))
save('source-receipt.json',dict(schemaVersion=1,sourceOnly=True,result=desc(OWN/'results.json'),sourceChecks=desc(OWN/'source-check-results.json'),inputHashes=desc(OWN/'input-hashes.json'),catalogue=desc(OWN/'fixture-catalogue.json'),requirements=desc(OWN/'requirements.json'),noRuntimeOrLifecycleAcceptance=True))
index=dict(schemaVersion=1,files=[])
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file()and p!=OWN/'index.json':r=desc(p);index['files'].append(dict(path=p.relative_to(OWN).as_posix(),sha256=r['sha256'],bytes=r['bytes']))
save('index.json',index);print(json.dumps(dict(index=desc(OWN/'index.json'),result=desc(OWN/'results.json'),receipt=desc(OWN/'source-receipt.json'),members=len(index['files']),sourceOnly=True)))
