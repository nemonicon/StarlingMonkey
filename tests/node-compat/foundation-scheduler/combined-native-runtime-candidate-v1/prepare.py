"""Own Source preparation only. Never imports/executes providers or fixtures."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
assert not (P/'index.json').exists()
r=json.loads((P/'references.json').read_text())
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def row(x):
 b=x.read_bytes();return dict(path=str(x.resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
child={r[k]['path']:r[k]for k in ['collectors','fixtureCatalogue','wave','parser','durable','durableHost','node']}
# Whole small runtime-shim subtree includes exact worker bundle and synckit.
shim=Path(r['shimClocks']['path']).parents[1]
for f in shim.rglob('*'):
 if f.is_file()and not f.is_symlink():child[str(f)]=row(f)
for f in [shim.parent/'package.json',Path(r['parser']['path']).parent.parent/'package.json',P.parent.parent/'foundation-crypto/ownership-component-candidate-v1/authority.mjs']:
 child[str(f.resolve())]=row(f)
write('child-inputs.json',dict(schemaVersion=1,scope='runtime Source/artifact/shim support only; zero child retained API invocation or native admission claim',files=sorted(child.values(),key=lambda d:d['path']),shimSubtree=str(shim),completeShimSubtreeFiles=sum(x['path'].startswith(str(shim)+'/')for x in child.values()),nativeApiInvocations=0,nativeFrameReturned=False))
a=json.loads(Path(r['callerSourceInputs']['path']).read_text());files={d['path']:d for d in a['files']};families={d['path']:d for d in a['families']}
def walk(v):
 if isinstance(v,dict):
  if set(v)=={'path','sha256','bytes'}:
   files[v['path']]=v
   if v['path'].endswith('/index.json'):families[v['path']]=v
  else:
   for w in v.values():walk(w)
 elif isinstance(v,list):
  for w in v:walk(w)
walk(r)
for d in child.values():files[d['path']]=d
write('source-inputs.json',dict(schemaVersion=1,scope='Compact source/actual proof/whole native and package boundaries expanded before first parent custom import; no historical tree recopy',files=sorted(files.values(),key=lambda d:d['path']),families=sorted(families.values(),key=lambda d:d['path']),boundaries=a['boundaries'],nativeSourceFiles=355,externalEmbeddingSources=3,fullMetadataFields=80,selectedWholeManifests=11,packageRegularFiles=4889,packageLinks=21,allOperationalAuthoritiesUnissued=True))
s=Path(r['fixtureCatalogue']['path']).parent.joinpath('test-models.mjs').read_text();start=s.index('function emptyState()');end=s.index('const sequence =',start);x=s.index('function clock(');y=s.index('const firstClock',x);z=s.index('const survivor =');last=s.index("test('observable",z)
(P/'synthetic-data.mjs').write_text("// Extracted synthetic DATA only, never guest source.\nimport {CASE_IDS,CASE_CALLBACKS} from '../combined-clock-lifecycle-candidate-v2/collectors.mjs';\nconst copy=structuredClone;\n"+s[start:end].replace('function ','export function ')+s[x:y].replace('function clock','export function clock')+s[z:last].replace('const survivor =','export const survivor ='))
root=dict(schemaVersion=1,state='UNISSUED_ROOT_TEMPLATE_NO_AUTHORITY_V1',requiredIssuedState='ROOT_REVIEWED_COMBINED355_NATIVE_RUNTIME_PHASE_V1',sourceIndex=None,entry=None,externalController=None,sourceIndependentReview=None,phase=None,fixtureId=None,fixtureSource=None,fixtureWit=None,worldName=None,outputRoot=None,externalOutputRoot=None,nativeSourceFiles=355,externalEmbeddingSources=3,fullMetadataFields=80,selectedWholeManifests=11,nativeEngine=r['nativeEngine'],nativeMetadata=r['nativeMetadata'],nativeReadOnlyConfig=r['readOnlyConfig'],actualBootstrapReview=r['actualBootstrapReview'],actualReadOnlyReview=r['actualReadOnlyReview'],nativeReadOnlyApiAllowed=False,mappingOnlyAllowed=False,jcoCompilerHelpersAllowed=False,generatedApplicationImportAllowed=False,ordinaryGuestExportsAllowed=False,stockWasmtimeAllowed=False,nodePureOracleAllowed=False,standardShimWorkerThreadsAllowed=False,requiredExternalParentDeadlineSeconds=1200,childDeadlineMs=180000,maxOutputBytes=16777216,wallClockCoarseAllowanceMs=1,clockAdjustmentPolicy='inconclusive-if-host-wall-clock-decreases',performanceTimeOriginEpochAssumed=False,selectedInterfaces=None,expectedEmittedImports=None,actualArtifactReview=None,actualArtifactContract=None,actualMappedReview=None,actualMappedContract=None,actualResourceRuntimeReview=None,actualResourceRuntimeContract=None)
for k in ['componentConstructionAllowed','nativeBuildAllowed','nativeFreezeAllowed','keyOrCryptoAllowed','gcOrFaultActionsAllowed','debugOrUnsafeResetAllowed','customHostServicesAllowed','adapterPromotionAllowed','metadataProjectionAllowed','nativeDiagnosticVariantAllowed','fullClockProfileAcceptance','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']:root[k]=False
write('future-root-authority.template.json',root)
write('future-config.template.json',dict(schemaVersion=1,state='COMBINED355_RUNTIME_CONFIG_V1',sourceIndex=None,rootAuthority=None,phase=None,fixtureId=None))
write('future-source-review-contract.json',dict(schemaVersion=1,requiredState='INDEPENDENT_COMBINED355_NATIVE_RUNTIME_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=None,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False,rootAuthorityIssued=False,actualRuntimeProof=None))
write('remaining-gates.json',dict(schemaVersion=1,fixtureSource=r['fixtureSourceIndex'],requirements=r['fixtureRequirements'],requiredGateCount=17,requiredFixtureIds=list(r['artifactSlots']),currentNativeSourceFiles=355,fullMetadataFields=80,diagnostic357Adopted=False,initFatalConstructionFailureReview=None,initFatalNoAcceptedComponent=True,initFatalRuntimeBranchImplemented=False,actualMappedOutputReviews=None,actualOrdinaryRuntimeReviews=None,actualFatalRuntimeReview=None,actualNativeOffsetInterestDropAndTeardownProof=None,all17GatesSatisfied=False,fullSixFixturesAccepted=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
print(json.dumps(dict(schemaVersion=1,sourcePreparationOnly=True,sourceInputs=len(files),families=len(families),childInputs=len(child),operationalCalls=0)))
