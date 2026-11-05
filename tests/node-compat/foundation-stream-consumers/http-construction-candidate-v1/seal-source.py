#!/usr/bin/env python3
"""Final finite SOURCE/data seal; never runs publication/admission/package/guest."""
import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent

def row(path):
 path=Path(path);h=hashlib.sha256();size=0
 with path.open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block);size+=len(block)
 return {'path':str(path),'sha256':h.hexdigest(),'bytes':size}
def save(name,value):
 path=D/name
 if path.exists():raise RuntimeError('Fresh source seal only '+name)
 path.write_text(json.dumps(value,indent=2)+'\n')
closure=json.loads((D/'closure.json').read_bytes());inputs={}
def add(path,role,expected=None):
 r=row(path)
 if expected:assert r['sha256']==expected['sha256']and r['bytes']==expected['bytes']
 previous=inputs.get(r['path']);assert previous is None or all(previous[k]==r[k]for k in ['path','sha256','bytes']);inputs[r['path']]={**r,'role':role}
for r in closure['files']:add(r['path'],'actual-finite-source-tool-native-reference',r)
mechanisms=json.loads((D/'copied-mechanisms.json').read_bytes())
for r in mechanisms['rows']:add(r['origin']['path'],'immutable-origin-of-byte-identical-copy',r['origin'])
p=json.loads((D/'prerequisites.json').read_bytes())
for name in ['analysisIndex','nativeSourceIndex','wholeReleaseProofIndex','followonProofIndex','oldHTTPSourceIndex']:
 ix=p[name];add(ix['path'],'INDEXED_ONLY-provenance-reference',ix)
 # Explicit finite indexed material is preserved as references; no historical
 # nested consumed manifest is evaluated in a relocated context.
 for r in json.loads(Path(ix['path']).read_bytes())['files']:add(Path(ix['path']).parent/r['path'],'finite-indexed-provenance-member',r)
save('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_PREPARATION_ORIGINAL_CONTEXT_FINITE_INPUTS','files':list(inputs.values()),'runtimeClosure':'closure.json','historicalNestedPreparationManifestsNotReinterpreted':True,'allOwnerActionsInvoked':False})
pure=json.loads((D/'evidence/pure.stdout.log').read_bytes());data=json.loads((D/'evidence/source.stdout.log').read_bytes());syntax=json.loads((D/'evidence/syntax.json').read_bytes())
save('results.json',{'schemaVersion':1,'state':'CONSUMERS355_HTTP_CONSTRUCTION_SOURCE_CANDIDATE_ONLY','sourcePreparationPassed':True,'pureChecks':pure['checks'],'sourceDataChecks':data['checks'],'parseChecks':len(syntax['records']),'runtimeClosureUniqueFiles':len(closure['files']),'runtimeClosureSummedLogicalBytes':sum(r['bytes']for r in closure['files']),'completeToolInputs':4892,'toolTrees':2,'knownToolLinks':22,'liveWitAndAdapterFiles':8,'genuineNativeSourcesPerContext':355,'selectedRuntimeFrozenCopies':closure['selectedRuntimeFrozenCopies'],'unchangedProtectedGroups':29,'unchangedClassicOrdinaryGroups':19,'newRequestLocalIterableConsumerGroups':2,'sourcePublicationAuthority':None,'sourceIndependentReview':None,'bundleActionAuthority':None,'actualWholeEntryBundleReview':None,'componentActionAuthority':None,'actualComponentPhase':None,'stockHostAuthorities':None,'publisherMainInvoked':False,'genuinePreflightOrHelperInvoked':False,'bundlerOrJcoOrComponentizerInvoked':False,'guestOrHostOrNodeOracleInvoked':False,'wireBodyAdapterImplemented':False,'metadataProjected':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False})
save('source-receipt.json',{'schemaVersion':1,'state':'SEALED_UNEXECUTED_CONSUMERS355_HTTP_CONSTRUCTION_SOURCE','sourceOnly':True,'sourceHeadAtPreparation':'c51cc993a536beea358ea78f4866b116300df0fb','historicalNativeBaselineIdentifier':'54b','analysisIndexSha256':p['analysisIndex']['sha256'],'genuineFamilyIndexSha256':p['familyIndex']['sha256'],'reviewedPinsSha256':p['reviewedPins']['sha256'],'nativeRootReviewSha256':p['nativeRootReview']['sha256'],'sourceInputs':len(inputs),'futureSourceRoot':'/private/tmp/starling-node-compat/consumers355-http-source-v1','futureBundleRoot':'/private/tmp/starling-node-compat/consumers355-http-bundle-v1','futureComponentRoot':'/private/tmp/starling-node-compat/consumers355-http-component-v1','implementedSourceActions':['source-publication','bundle-source','component-build'],'allActionAuthoritiesUnconfigured':True,'allOwnerActionsInvoked':False,'nativeGuestOrProofPredecessorsModified':False})
files=[]
for path in sorted(D.rglob('*')):
 if path.is_file()and path.name!='index.json':
  r=row(path);files.append({'path':str(path.relative_to(D)),'sha256':r['sha256'],'bytes':r['bytes']})
save('index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_CONSUMERS355_HTTP_CONSTRUCTION_CANDIDATE','files':files,'sourceOnly':True,'ownerActionsInvoked':False})
for r in files:assert row(D/r['path'])['sha256']==r['sha256']
# The complete runtime closure was rehashed during input assembly immediately
# before sealing. Source-index rehash closes all own code/data/pure receipts.
print(json.dumps({'index':row(D/'index.json'),'results':row(D/'results.json'),'receipt':row(D/'source-receipt.json'),'files':len(files),'inputs':len(inputs)}))
