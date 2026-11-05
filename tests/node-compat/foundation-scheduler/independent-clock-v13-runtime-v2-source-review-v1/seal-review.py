"""Independent Source review sealing only; no phase or runtime authority."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'clock-v13-runtime-candidate-v2'
EXPECTED='135d1e45ea4214a99e2a835cfab0b212c92519ea6600a7c802336e7a323be384'
def desc(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
ix=desc(SOURCE/'index.json');assert ix['sha256']==EXPECTED
members=read(SOURCE/'index.json')['files'];assert len(members)==40
for r in members:assert desc(SOURCE/r['path'])==dict(r,path=str(SOURCE/r['path']))
assert not any(p.is_symlink()for p in SOURCE.rglob('*'))and{p.relative_to(SOURCE).as_posix()for p in SOURCE.rglob('*')if p.is_file()}=={r['path']for r in members}|{'index.json'}
checks=read(OWN/'checks.json');refs=read(OWN/'references.json');assert checks['passed']is True and checks['sourceIndex']==ix
assert not(OWN/'reader.stderr.log').read_bytes()
pure=[]
for name,count,field in [('inherited-pure',81,'checks'),('presence-pure',52,'checks'),('exact-presence',80,'checks')]:
 result=read(OWN/(name+'.stdout.log'));assert result.get('passed',True)is True and result[field]==count and not(OWN/(name+'.stderr.log')).read_bytes();pure.append(dict(name=name,cases=count,result=result))
save('terminals.json',dict(schemaVersion=1,reader=dict(kind='tool-observed-source-data-reader',toolSession=38388,rawExitCode=0,stdout=desc(OWN/'reader.stdout.log'),stderr=desc(OWN/'reader.stderr.log')),pure=[dict(kind='tool-observed-source-pure-node',rawExitCode=0,executable=refs['node'],stdout=desc(OWN/(r['name']+'.stdout.log')),stderr=desc(OWN/(r['name']+'.stderr.log')),checks=r['cases'])for r in pure],ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False,processIdsNotIndependentlyRecorded=True))
result=dict(schemaVersion=1,state='INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_PASSED_V2',sourceIndexSha256=ix['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False,sourceIndex=ix,previousSourceIndex=refs['previousSourceIndex'],heldSourceReview=refs['previousSourceHold'],requiredCorrectionContract=refs['requiredCorrectionContract'],actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],component=refs['component'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],nativeSourceFiles=342,externalEmbeddingSources=3,fullMetadataFields=64,selectedWholeManifests=9,allFourActualCoreIdentitiesUnchanged=True,artifactRows=14,generatedRows=7,retainedOracle=refs['oracleEvidence'],retainedOracleValue=refs['oracleValue'],mappingOptions=refs['mappingOptions'],mappedOutputRoot=refs['mappedOutputRoot'],runtimeOutputRoot=refs['runtimeOutputRoot'],
 nullPrimaryFindingClosed=True,primaryPresenceBodySites=3,primaryPresenceEntrySites=2,truthfulFailurePresenceFields=3,literalNullAndFalseLikeThrowsRemainFailures=True,combinedOriginalCaptureErrorsPreserved=True,parentTypedThrowRefusalPreserved=True,exactFailureBlockTests=80,inheritedPureCases=81,focusedPresencePureCases=52,totalPureChecks=213,readHashSourceChecks=checks['checks'],declaredOriginalFiles=12079,declaredOriginalLogicalBytes=1374542216,inheritedOriginalRowsUnchanged=11995,inheritedFamilies=18,ownSourceMembers=40,uniqueReadHashInputs=checks['uniqueReadHashInputs'],uniqueReadHashLogicalBytes=checks['uniqueReadHashLogicalBytes'],physicalPackageFiles=4889,physicalPackageAliases=21,exactDerivedFiles=6,exactReversibleSubstitutions=27,actualExternalOwnInertImported=True,namespaceOrFrameInjected=False,completeFamilyBytesRehashedAtReaderCompletion=True,allCapturedPhysicalIdentitiesStableAtReaderCompletion=True,allLargeOriginalBytesIndependentlyRehashedTwice=False,retainedGrammarChecksAuthenticatedNotRerun=6,
 plannedJcoRetainedWholeStrings=3,plannedJcoFreshWholeStrings=1,plannedStockWasmtimeFreshWholeStrings=3,plannedFullHtmlUtf8Bytes=45,firstActualSingleWasmtimeProofNotTransferred=True,sourceChecks=desc(OWN/'checks.json'),materialFindings=[],reviewerFailures=[],rootPhaseAuthority=None,actualMappedOutputReview=None,actualRuntimeReview=None,phaseAuthorityGranted=False,jcoCompilerImported=False,standardShimImported=False,generatedApplicationImported=False,nativePreflightInvoked=False,monitorInvoked=False,wasmtimeExecuted=False,engineOrGuestExecuted=False,fullClockProfileAcceptance=False,resourceDateSnapshotTimerTeardownSevenCaseGateComplete=False,operationalAdmission=False,runtimeAcceptanceClaim=False,
 limits=['Source-only verdict; both mapping and runtime phases remain unissued.','Large original bytes hashed once in successful reader; all Source families rehashed at completion and all captured physical identities/modes checked.','Exact extracted branch tests use memory sinks and invoke no operational phase or admitted Frame.','Standard shim worker threads/Atomics waits require external process ownership; no resource/thread teardown completeness is proved.','Three future fresh stock-WT and retained3/fresh1 Jco calls remain planned, not observed in this review.','All seven full clock/resource/Date/snapshot/timer/teardown gates and reset/reuse/profile promotion remain separate.','No unique cause, wasmCloud/service, security completeness, adoption or performance claim.'])
save('results.json',result)
save('result-contract.json',dict(schemaVersion=1,requiredState=result['state'],requiredFixedValues={k:result[k]for k in('schemaVersion','sourceIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','hostActionsInvoked','runtimeActionsInvoked')},requiredExactDescriptors=dict(sourceIndex=ix,previousSourceIndex=refs['previousSourceIndex'],requiredCorrectionContract=refs['requiredCorrectionContract']),grantsAnyPhase=False))
save('source-receipt.json',dict(schemaVersion=1,sourceOnly=True,result=desc(OWN/'results.json'),contract=desc(OWN/'result-contract.json'),checks=desc(OWN/'checks.json'),reader=desc(OWN/'review.py'),exactBranchTest=desc(OWN/'test-exact-presence.mjs'),terminals=desc(OWN/'terminals.json'),sourceIndex=ix,noPhaseAuthority=True))
files=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file()and p.name!='index.json':files.append(dict(desc(p),path=p.relative_to(OWN).as_posix()))
save('index.json',dict(schemaVersion=1,files=files))
for r in files:assert desc(OWN/r['path'])==dict(r,path=str(OWN/r['path']))
for n in('index.json','results.json','result-contract.json','source-receipt.json'):print(n,json.dumps(desc(OWN/n)),flush=True)
