"""Seal finite independent actual DATA review, without owner imports/actions."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
d=json.loads((P/'data-results.json').read_bytes());t=json.loads((P/'tool-boundary-results.json').read_bytes())
assert d['dataReviewPassed'] and t['verifiedPassed'] and d['expectedRows']==90 and d['arms']==3
fixed={
 'schemaVersion':1,'state':'INDEPENDENT_ZLIB_COST_PREPARED_PLAN_V3_RESULTS_REVIEW_PASSED_V1','verifiedPassed':True,
 'sourceIndexSha256':d['sourceIndex']['sha256'],'expectedRows':90,'arms':3,'armNames':['native-on','fflate-on','fflate-off'],
 'actualIndexedFiles':1,'actualRegularFiles':3,'externalParentExitCode':0,'parentOwnedGroupGone':True,
 'allFiveRawFixturesWholeBytesRecomputed':True,'all60ActualEncodedStreamsWholeBytesRehashedAndFnvRecomputed':True,
 'all15NodeEncodedStreamsWholeBytesMatched':True,'all90ExpectedRowsExactlyReconstructed':True,
 'fullSourceFamiliesProofNativeToolClosuresRehashed':True,'toolTreeCount':2,'physicalToolLinkCount':22,
 'exactPrivatePlanPublicationMembershipVerified':True,'actionAuthority':False,'executionAuthority':False,
 'rootActualReadOnlyPrerequisiteGuardsCompleted':True,'rootGeneratedGuestCodecWorkerPilotOrTimingActionsInvoked':False,
 'reviewerReadHashDecodeDataOnly':True,'reviewerOwnerHelpersPreflightNodeGuestCodecNativePilotOrTimingActionsInvoked':False,
 'historicalCorrectnessControlOperations':0,'historicalCorrectnessPendingControl':True,'historicalTransportPendingControl':True,
 'separateActualControlOperations':540,'separateActualControlCodecCalls':0,'separateActualControlPilotPrerequisitesSatisfied':False,
 'pilotPrerequisitesSatisfied':False,'quietWindowAuthority':None,'phaseAuthority':None,'warmNPlan':None,'globalBudgetMs':None,
 'pilotAllowed':False,'timingAllowed':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False,
 'metadataProjection':False,'sourcePromotionAllowed':False,'performanceMemoryCapacityOrReuseClaim':False,
}
exact={k:d[k]for k in ['rootResult','sourceIndex','preparedPlan','actualIndex','actualCompletion','externalTerminal','rootAuthority','calibrationDecision']}
limits=[
 'This proof establishes exact prepared DATA against retained actual oracle/stream/artifact/proof inputs. It executes no worker, generated module, codec, pilot or timing sample.',
 'The Root action ran genuine unchanged read-only prerequisite guards with the old235d correctness authority. The reviewer did not run those guards or any owner helper.',
 'The original correctness controlOperations0 and actualBatchControlProofPendingtrue fields remain historical; the separate later540-control/codec0 proof remains pilotPrerequisitesSatisfiedfalse.',
 'timingNMax values are case caps from the selected source design. They are not chosen or empirically validated N values, budgets, feasible-runtime evidence or an action grant.',
 'The catalog contains actual Node/native/fflate streams; this review decoded base64 and recomputed whole-byte SHA/FNV as data. It did not compress, decompress, re-run Node or re-establish prior workload semantics.',
 'New explicit Root phase and quiet-window authorities plus actual independently reviewed paired calibration/matched-N data are required before any timing action. All old HOLD and failed attempts remain unchanged.',
]
result=dict(fixed,**exact,coverage=dict(expectedRows=90,arms=3,rawFixtures=5,actualEncoderStreams=60,nodeEncoderStreams=15),sourceReview=d['sourceReview'],fullCorrectness=d['fullCorrectness'],stockWasmtimeStrings=d['stockWasmtimeStrings'],
 actualControlsProof=d['actualControlsProof'],artifacts=d['artifacts'],
 expectedRowLedger=row(P/'per-row-ledger.json'),dataReview=row(P/'data-results.json'),toolBoundary=row(P/'tool-boundary-results.json'),
 inputClosure=row(P/'rehashed-inputs.json'),readerHistory=row(P/'reader-history.json'),
 uniqueDeclaredInputsVerified=d['uniqueDeclaredInputsVerified'],uniquePhysicalFilesHashed=d['uniquePhysicalFilesHashed'],dataChecks=d['checks'],
 rootReportedTerminalDirectlyObservedByThisReader=False,limitations=limits)
save('results.json',result)
save('result-contract.json',dict(schemaVersion=1,state='SEALED_PREPARED_CODEC_MEASUREMENT_PLAN_V3_DATA_CONTRACT_V1',
 requiredReviewState=fixed['state'],reviewResult=row(P/'results.json'),requiredFixedValues=fixed,
 requiredCoverage=dict(expectedRows=90,arms=3,rawFixtures=5,actualEncoderStreams=60,nodeEncoderStreams=15),
 requiredExactDescriptors=exact,requiredArtifacts=d['artifacts'],
 actualFullProofs={k:d[k]for k in ['fullCorrectness','stockWasmtimeStrings','actualControlsProof']},
 stableOriginalPlan=row(Path(d['preparedPlan']['path'])),grantsExecutionAuthority=False,
 consumerRules=['Authenticate every indexed peer member and the whole fixed values, exact descriptors and all three artifact tuples.',
 'Require the entire unchanged compact plan; do not select or silently alter expected rows, full-byte fingerprints, input origins, caps or calibration identity.',
 'Do not relabel historical correctness/transport pending-control fields. The separate540-control proof does not issue a pilot or timing grant.',
 'Supply separate new Root phase/window/budget authority; actual matched-N calibration and its independent proof are further prerequisites for timing.'],limitations=limits))
(P/'README.md').write_text('''Independent prepared codec measurement plan v3 DATA review passed. The [result](results.json) and [stable contract](result-contract.json) grant no execution authority.

The actual Root parent returned zero, retained complete raw stdout/stderr and reported its owned group gone. Its exact read-only authority, options, entry source, one indexed plan and three private physical output files were checked. No worker, generated module, codec, pilot or timing action was launched by this plan action or by the reviewer. Root ran the genuine existing read-only prerequisite guards; the reviewer inspected their authenticated source/control flow and retained proof data.

All 90 expected rows were independently reconstructed for three arms and 30 cases. Five raw fixtures were regenerated as ordinary Python byte data. All 60 retained Node/native/fflate encoded streams were base64-decoded and their whole lengths, SHA-256 and FNV values recomputed, including direct comparison of all fifteen Node encoder streams with the original full Node oracle. Each row's full input origin, digest, logical/output bytes, FNV, case identity and source cap matches without normalization. The [row ledger](per-row-ledger.json) retains exact source citations and whole-byte digests. No codec algorithm was invoked.

The three component/glue/core/WIT/metadata/package tuples match the actual artifact proofs. Full source families, 918 preparation rows and exact correctness/transport/control/native/tool proof closures were rehashed: 25,590 distinct physical files. The actual immutable packaging publication's complete membership, two tool trees and all 22 link texts/resolved targets were checked as typed data. No input was reinterpreted under a relocated context.

Historical correctness control count zero and both pending-control fields remain unchanged. The later independent 540-control, zero-codec proof is separate and still states that pilot prerequisites are unsatisfied. Case caps are source bounds, not empirical matched-N selections. Quiet window, phase, warm-N and global budget grants remain absent here. Prior HOLDs and failures remain literal history.

[Reader history](reader-history.json) records a private Python token typo and a corrected actual Node encoded-stream field assumption. Author/source/oracle/result bytes were not edited. No performance, capacity, private heap, reuse, operational admission or source-promotion result follows from this DATA publication.
''')
save('review-receipt.json',dict(schemaVersion=1,state=fixed['state'],verifiedPassed=True,result=row(P/'results.json'),contract=row(P/'result-contract.json'),rootResult=d['rootResult'],preparedPlan=d['preparedPlan'],sourceIndexSha256=d['sourceIndex']['sha256'],readHashDataOnly=True,ownerActionsInvoked=False,grantsExecutionAuthority=False))
files=[]
for q in sorted(P.rglob('*')):
 if q.is_file() and q.name!='index.json':
  r=row(q);r['path']=str(q.relative_to(P));files.append(r)
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_PREPARED_CODEC_PLAN_V3_DATA_REVIEW_V1',files=files))
print(json.dumps({n:row(P/n)for n in ['index.json','results.json','result-contract.json','review-receipt.json']}))
