"""Seal completed independent source-stage result. No owner actions or imports."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n')
a=json.loads((P/'audit-data.json').read_bytes());c=json.loads((P/'final-closure-review.json').read_bytes());spec=json.loads((P/'actual-evidence-inputs.json').read_bytes())
assert a['copyRows']==1311 and a['nativeFiles']==355 and a['toolRows']==922 and c['verifiedPassed']and c['remainingObservedPids']==[]
fixed=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_GC_SOURCE_STAGE_REVIEW_PASSED_V1',verifiedPassed=True,
 actualStageResult=spec['journal'],sourceIndexSha256=spec['sourceIndex']['sha256'],configuredSourceRoot=a['configuredSourceRoot'],
 sourceOnly=True,externalParentExitCode=0,allObservedOwnedGroupsGone=True,remainingObservedPids=[],forcedCleanup=False,
 declaredCopiedPaths=1311,nativeSourceFiles=355,toolRows=922,allDeclaredCopyHashesModesAndIndependentInodesVerified=True,
 allCurrentOriginalNativeAndToolSourceInputsUnchanged=True,normalOriginalReferenceEntries=1387,normalDistinctOriginalPaths=1378,normalFrozenMembers=1391,
 normalCmakeCacheAndCompileCommandsUnchanged=True,actualDetachedGitHead=a['actualDetachedBase'],gitAlternatesAbsent=True,gitObjectHardlinksAbsent=True,
 historicalStageInputDestinationRetainedAsData=True,actualDestinationMatchesV2Context=True,
 nativeBuildFreezeBootstrapOrGuestInvokedByReader=False,ownerHelpersOrPhaseActionsInvokedByReader=False,
 grantsNativeBuildAuthority=False,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,sourcePromotionAllowed=False)
result=dict(fixed,sourceIndex=spec['sourceIndex'],sourceReview=spec['sourceReview'],controllerReview=spec['controllerReview'],
 stageCallerSourceIndex=spec['stageControllerSourceIndex'],genericMonitorSourceIndex=spec['genericMonitorSourceIndex'],
 rootResult=c['rootResult'],rootAuthority=spec['rootAuthority'],config=spec['config'],externalParentTerminal=spec['externalTerminal'],externalParentStarted=spec['started'],
 rootReportedToolRawExitCode=0,rootReportedToolSession=49205,rootToolStatusDirectlyObservedByThisReader=False,ownedStagePid=44203,
 completeStageStdoutEqualsJournal=True,actualCloneAndCheckoutCommandsRawZero=True,recordedObservedProcesses=4,
 auditData=row(P/'audit-data.json'),finalClosureReview=row(P/'final-closure-review.json'),
 readerWasPreparedBeforeOutcomeAndRunOnlyAfterRootReportedCompletion=True,
 independentReadHashChecks=a['checks'],sourcePreparationInputsFinallyRehashed=2852,runtimePinnedRowsFinallyRehashed=58,
 limitations=['This proof covers the completed source clone/checkout and declared1311 source/tool copy publication only. It establishes no native build, compilation, freeze, pin, bootstrap, component, guest, key or GC result.',
 'The declared1311 files are the copied overlay on a pinned Git baseline, not a claim that the entire checkout contains only1311 files. HEAD and recorded clone/checkout commands were checked without executing Git; no alternates or hardlinked Git files were found.',
 'The retained source peer remains source-only. This actual stage proof does not relabel it as a native artifact review or issue a build authority.',
 'The copied stage-inputs destinationv1 annotation is historical DATA. Root explicitly qualifies it; actual stage journal, configured paths and copied files are checked against contextv2. No old descriptor is rewritten or reinterpreted.',
 'Process cleanup findings refer to the authenticated monitor and its complete retained observed-process evidence: no remaining observed PIDs/groups, forced cleanup, signal, error or timeout. The reviewer did not run processes or a cleanup probe.',
 'Root directly reported the tool terminal raw zero; this reader independently checked retained terminal/journal/whole streams and current physical bytes. Operational duration is not a performance result.'])
save('results.json',result)
save('result-contract.json',dict(schemaVersion=1,state='CRYPTO_OWNER355_GC_SOURCE_STAGE_RESULT_CONTRACT_V1',requiredReviewState=fixed['state'],requiredFixedValues=fixed,
 reviewResult=row(P/'results.json'),requiredActualStageResult=spec['journal'],requiredSourceIndex=spec['sourceIndex'],requiredSourceReview=spec['sourceReview'],requiredControllerReview=spec['controllerReview'],
 requiredExactDescriptors={k:result[k]for k in ['rootResult','rootAuthority','config','externalParentTerminal','externalParentStarted','stageCallerSourceIndex','genericMonitorSourceIndex']},
 grantsNativeOrGuestAuthority=False,consumerRule='The native guard may use this exact actualStageResult/sourceIndex/configuredSourceRoot DATA only under a new separate Root build/freeze/export/bootstrap phase and all existing authentic source/normal-protection checks.'))
(P/'README.md').write_text('''Independent actual GC source-stage review passed. The [result](results.json) binds the direct stage journal and exact source identity expected by the native guard. The [contract](result-contract.json) grants no native build authority.

Root reported tool49205 raw zero. The retained600-second owned monitor observed stage child44203 return zero with complete stdout/stderr, all observed groups gone, no remaining observed PIDs, signals, forced cleanup, timeout or errors. All four retained process observations reconcile with the terminal. Full raw stage stdout equals the completed journal; its two clone/checkout commands returned zero.

The actual v2 checkout has detached HEAD54b3329b, no Git alternates and no hardlinked Git files. All 1,311 declared copied files match their original bytes and modes and have independent inodes. These include the complete native355 and tool922 sets. The declaration is an overlay on the baseline checkout, not its total physical file count. The reader did not execute Git or a source helper.

The exact reviewed sourceed066, corrected monitor71b7/caller29d592 and independent peer e3c/e00 identities were checked. All 2,852 inherited preparation inputs and 58 runtime pinned rows were rehashed. Every normal protected copy/original remains exact, including 1,387 reference entries, 1,378 distinct original paths, both normal CMakeCache/compile_commands inputs and the strict 1,391-member normal freeze.

The unchanged copied stage-inputs destinationv1 annotation remains historical DATA. The Root stage authority explicitly records this distinction. Actual journal, native configured context and files were checked against v2; no original descriptor or metadata was rewritten.

The reader was prepared privately before the stage and executed only after Root supplied terminal completion. This review used read/hash/JSON/physical metadata only. No helper, preflight, native build, freezer, bootstrap, process, guest, key, crypto, GC or host action ran. Native artifact/pin/component/GC results remain future independent gates; source-peer proof stays source-only.
''')
save('review-receipt.json',dict(schemaVersion=1,state=fixed['state'],verifiedPassed=True,result=row(P/'results.json'),contract=row(P/'result-contract.json'),actualStageResult=spec['journal'],sourceIndexSha256=fixed['sourceIndexSha256'],configuredSourceRoot=fixed['configuredSourceRoot'],sourceOnly=True,ownerActionsInvoked=False,grantsNativeBuildAuthority=False))
files=[]
for p in sorted(P.rglob('*')):
 if p.is_file()and p.name!='index.json':
  x=row(p);x['path']=str(p.relative_to(P));files.append(x)
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_GC_SOURCE_STAGE_REVIEW_V1',files=files))
print(json.dumps({n:row(P/n)for n in ['index.json','results.json','result-contract.json']}))
