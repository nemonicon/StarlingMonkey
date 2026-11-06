"""Seal complete independent export DATA publication; root index exclusion only."""
from pathlib import Path
import hashlib,json,stat
OWN=Path(__file__).resolve().parent
def desc(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
checks=read(OWN/'checks.json');refs=read(OWN/'references.json');assert checks['passed']is True and not(OWN/'reader.stderr.log').read_bytes()
for key in('rootResult','candidate','nativeFrame','verifierCapsule','controllerObservation','externalTerminal','outerTerminal'):assert desc(Path(refs[key]['path']))==refs[key]
for r in read(OWN/'raw-copy-map.json')['copies']:
 a,b=Path(r['original']['path']),Path(r['copy']['path']);assert desc(a)==r['original']and desc(b)==r['copy']and r['original']['sha256']==r['copy']['sha256']
 sa,sb=a.stat(),b.stat();assert(sa.st_dev,sa.st_ino)!=(sb.st_dev,sb.st_ino)and sb.st_nlink==1 and stat.S_IMODE(sb.st_mode)==0o600
frozen=Path(refs['freezeReceipt']['path']).parent
assert stat.S_IMODE(frozen.stat().st_mode)==0o700
for p in frozen.rglob('*'):
 assert not p.is_symlink()
 if p.is_dir():assert stat.S_IMODE(p.stat().st_mode)==0o700
 else:assert p.is_file()and p.stat().st_nlink==1 and stat.S_IMODE(p.stat().st_mode)==0o600
source=Path(refs['toolingIndex']['path']).parent;assert desc(source/'index.json')==refs['toolingIndex']
for r in read(source/'index.json')['files']:assert desc(source/r['path'])==dict(r,path=str(source/r['path']))
future=read(Path(refs['futureExportReviewContract']['path']))
result=dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_NORMAL_OFF_PIN_EXPORT_REVIEW_PASSED_V1',verifiedPassed=True,readOnlyDataReview=True,toolingSourceIndexSha256=refs['toolingIndex']['sha256'],toolingIndex=refs['toolingIndex'],sourcePeer=refs['sourcePeer'],candidate=refs['candidate'],nativeFrame=refs['nativeFrame'],verifierCapsule=refs['verifierCapsule'],rootAuthority=refs['rootAuthority'],config=refs['config'],controllerObservation=refs['controllerObservation'],externalTerminal=refs['externalTerminal'],outerTerminal=refs['outerTerminal'],rootResult=refs['rootResult'],invocation=refs['invocation'],actualFrozenReview=refs['actualFrozenReview'],actualFrozenContract=refs['actualFrozenContract'],freezeReceipt=refs['freezeReceipt'],engine=refs['engine'],engineSha256=refs['engine']['sha256'],metadata=refs['metadata'],metadataSha256=refs['metadata']['sha256'],nativeSourceIndex=refs['nativeSourceIndex'],retryBuildControllerIndex=refs['retryBuildControllerIndex'],freezerSourceIndex=refs['freezerSourceIndex'],activeVerifier=refs['activeVerifier'],rawCandidateStdout=refs['rawCandidateStdout'],parentStdout=refs['parentStdout'],parentStderr=refs['parentStderr'],
 rawExporterExitCode=0,rawParentExitCode=0,rootToolObservedExitCode=0,rootToolObservationIsNotSeparateProcessLog=True,allObservedOwnedGroupsGone=True,noTimeoutSignalsErrorsOrForcedCleanup=True,wholeCandidateAndRawJsonEqual=True,rawAndPrettyBytesClaimedIdentical=False,rawCandidateJsonBytes=1314735,prettyCandidateJsonBytes=1574865,wholeFrameReconstructedIndependently=True,verifierCapsuleKeepsNotAcceptedState=True,candidateAndPinRemainUnreviewed=True,otherVariantsNull=True,variantLabels=['normal-off','normal-runtime','gc-off','disabled-off'],nativeSourceFiles=355,externalEmbeddingSources=3,fullMetadataFields=80,selectedManifestCount=11,allWholeManifestsPreserved=True,rawMetadataDescriptorBytes=656598,originalMetadataWorkPathsPreserved=True,freezeCopies=2596,freezeMembershipFiles=2597,frozenFileRowsPreserved=2596,compileDatabaseRows=68,policyCppCommands=62,otherConfiguredCommands=5,generatedNullCommands=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=6,
 producerOutputFiles=5,producerIndexOrCompletionExists=False,sourceParentPid=46729,workerPid=47096,outerParentDeadlineSeconds=1200,innerWorkerDeadlineSeconds=600,outerObservedProcessRows=59,outerOwnedGroups=2,innerOwnedGroups=1,sampledExtraProcessesAreMonitorPsHelpers=True,actualRawTextCopies=79,currentUniqueReferences=checks['currentUniqueReferences'],currentLogicalReadHashBytes=checks['currentLogicalBytes'],fixedCompactRows=2618,fixedBuildOriginalRows=20816,inheritedFamilies=15,frozenOriginalInodeAndModeProtectionVerified=True,stagedOriginalPairs=1613,originalReferenceAliases=31,originalArchiveHardlinks=1,allCurrentReferencesStable=True,actualTimeProtectionEvidence=checks['actualTimeProtectionEvidence'],singleVerifierInvocationEvidence=checks['verifierCallsEvidence'],historical57ByteSettingsNotRehashed=True,inheritedTreesRecopied=False,checks=desc(OWN/'checks.json'),rawCopyMap=desc(OWN/'raw-copy-map.json'),sourceDataChecks=checks['checks'],materialFindings=[],reviewerFailures=[],
 ownerActionsInvoked=False,hostActionsInvoked=False,reviewerVerifierHelperModelApiPhaseOrEngineInvoked=False,observedReadOnlyVerifierInvokedByOwner=True,expectedSourceCoupledVerifierCalls=1,engineExecuted=False,guestExecuted=False,bootstrapExecuted=False,reviewedPins=None,actualBootstrap=None,reviewedPinTransitionPerformedByReader=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsBootstrapOrPinAdoption=False,
 limits=['Candidate and pin remain unreviewed; this result grants no pin adoption/bootstrap/engine action.','One verifier call and actual-time protection are Source-coupled control-flow/whole-return/raw0 evidence, not independently retained function-call or per-read historical traces.','Both complete JSON values are equal; pretty candidate bytes and compact stdout bytes differ and are separately retained.','Declared originals must remain available; no disconnected/archive-aware boundary is introduced.','Only fixed declared provenance was rehashed; referenced originals/SDKs are not all physically copied.','Historical superseded57-byte preinstall settings were not retained/read as a current origin.','No new per-compiler exits, runtime backend version, all-invalid/resource/clock/GC/erasure/reset/reuse or remaining15 deviations approval.','No security completeness, benchmark, runtime or production adoption.'])
assert result['state']==future['requiredState']and future['requiredOwnIndexField']=='toolingSourceIndexSha256'
for k,v in future['requiredFixedValues'].items():assert result[k]==v,k
for k in future['requiredDirectRoles']:assert k in result,k
save('results.json',result)
save('result-contract.json',dict(schemaVersion=1,requiredReviewState=result['state'],requiredFixedValues={k:result[k]for k in('schemaVersion','verifiedPassed','toolingSourceIndexSha256','rawExporterExitCode','allObservedOwnedGroupsGone','wholeCandidateAndRawJsonEqual','otherVariantsNull','nativeSourceFiles','externalEmbeddingSources','fullMetadataFields','selectedManifestCount','engineExecuted','bootstrapExecuted','operationalAdmission','runtimeAcceptanceClaim')},requiredExactDescriptors={k:result[k]for k in('toolingIndex','candidate','nativeFrame','verifierCapsule','rootAuthority','config','controllerObservation','externalTerminal','outerTerminal','rootResult','invocation','actualFrozenReview','actualFrozenContract','freezeReceipt','engine','metadata')},grantsBootstrapOrPinAdoption=False))
save('reader-terminal.json',dict(schemaVersion=1,kind='tool-observed-independent-data-reader',toolSession=71714,rawExitCode=0,stdout=desc(OWN/'reader.stdout.log'),stderr=desc(OWN/'reader.stderr.log'),processIdNotIndependentlyRecorded=True,ownerActionsInvoked=False,hostActionsInvoked=False,verifierHelperOrEngineInvoked=False))
save('review-receipt.json',dict(schemaVersion=1,readOnlyDataReview=True,result=desc(OWN/'results.json'),contract=desc(OWN/'result-contract.json'),checks=desc(OWN/'checks.json'),reader=desc(OWN/'review.py'),readerTerminal=desc(OWN/'reader-terminal.json'),rawCopyMap=desc(OWN/'raw-copy-map.json'),rootResult=refs['rootResult'],grantsFurtherActions=False))
payload=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file()and p not in(OWN/'index.json',OWN/'member-ledger.json'):payload.append(dict(desc(p),path=p.relative_to(OWN).as_posix()))
save('member-ledger.json',dict(schemaVersion=1,scope='Every file except own root index and this ledger; own index binds ledger',files=payload))
files=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file()and p!=OWN/'index.json':files.append(dict(desc(p),path=p.relative_to(OWN).as_posix()))
save('index.json',dict(schemaVersion=1,files=files))
actual={p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()};names={r['path']for r in files}
assert len(names)==len(files)and actual==names|{'index.json'}
assert{r['path']for r in payload}==names-{'member-ledger.json'}
for r in files:assert desc(OWN/r['path'])==dict(r,path=str(OWN/r['path']))
assert [p for p in [OWN/'index.json',OWN/'evidence'/'index.json']if p!=OWN/'index.json']==[OWN/'evidence'/'index.json']
for n in('index.json','results.json','result-contract.json','review-receipt.json'):print(n,json.dumps(desc(OWN/n)),flush=True)
