"""Seal bounded proposal HOLD; does not execute owner helpers or fixture."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
d=json.loads((P/'data-results.json').read_bytes());findings=json.loads((P/'findings.json').read_bytes());syntax=json.loads((P/'syntax-terminal.json').read_bytes())
assert d['sourceDataReviewComplete'] and d['concreteSourceBlockers']==1 and syntax['rawExitCode']==0 and syntax['parseOnly'] and not syntax['moduleEvaluated']
result={**d,'schemaVersion':1,'state':'INDEPENDENT_CRYPTO_OWNER355_GC_SOURCE_REVIEW_HELD_V1','verifiedPassed':False,
 'sourceIndexSha256':d['sourceIndex']['sha256'],'sourceOnly':True,'sourceReviewPassed':False,'ownerActionsInvoked':False,
 'newGuestSyntaxParsedByReviewer':True,'syntaxTerminal':row(P/'syntax-terminal.json'),
 'normalPreservationSourceDataVerified':True,'isolatedWorkRootMechanismVerified':True,'isolatedFreezeRootRequirementVerified':True,
 'supportedPublicBufferPressurePathsVerified':True,'sourceStaticHookSitesAreNotObservedCounts':True,
 'newRootOrNativePinsIssued':False,'nativePolicyOrRecipeChangedByProposal':False,
 'guestOrNativeExecutedByReviewer':False,'reviewerPinnedNodeCheckOnlyInvoked':True,
 'reviewerOwnerPreflightProducerBuildFreezeBootstrapCompilerKeyCryptoPrototypeGcOrGuestActionsInvoked':False,
 'separateNativeProducerDoesNotConsumeThisGuest':True,'gcGuestCollectorSuccessorRequiresCorrection':True,
 'findings':findings['findings'],'findingLedger':row(P/'findings.json'),'inputClosure':row(P/'rehashed-inputs.json'),
 'readerHistory':row(P/'reader-history.json'),'proposalFollowOnContract':row(P.parent/'ownership-gc-candidate-v1/follow-on-contract.json'),
 'futureSourceReview':None,'rootAuthority':None,'gcEngine':None,'gcNativeReview':None,'gcComponent':None,'gcResult':None,
 'buildAllowed':False,'freezeAllowed':False,'bootstrapAllowed':False,'componentAllowed':False,'guestAllowed':False,
 'keyOperationsAllowed':False,'gcAllowed':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False,
 'timingAllowed':False,'sourcePromotionAllowed':False,
 'scope':'The isolation, preservation, public-hook source mapping and exact fixture derivation checks pass as bounded DATA observations. The proposal as a whole remains HOLD for GC-PROPOSAL-M1; it is not a runnable native/component/GC pipeline or runtime proof.',
 'limitations':['Only a future actual GC-stress engine plus component and typed raw collector can establish the proposed observations. No such new artifact or action is supplied by this proposal.',
 'All six hook-site counts are static source facts. No actual collection count, moving/compacting event, isolated native root, private heap, finalizer, free or wipe was observed.',
 'Module holders, function arguments and other strong application owners remain combined. No GC inside a WebCrypto native call is claimed.',
 'The future owned native controller must retain full source/tool admission, single-job Release/no-OOM policy, owned cleanup and the existing2GiB-start/800MiB-stop safeguards; that controller and freezer/bootstrap successors remain unimplemented here.',
 'The normal1391 frozen-member inventory and1387 original-reference entries are strictly protected. Future native source work is separate; this HOLD does not approve a native build or mutate normal evidence.'],
}
save('results.json',result)
save('required-correction-contract.json',dict(schemaVersion=1,state='GC_PROPOSAL_M1_REQUIRED_TRUTHFUL_OBSERVATION_SOURCE_CORRECTION_V1',heldSourceIndex=d['sourceIndex'],findingId='GC-PROPOSAL-M1',
 oldSourceMustRemainUnchanged=True,newImmutableSuccessorRequired=True,
 requiredChanges=['Replace the inherited overbroad gcOrEntropyRequested:false observation in the GC guest with truthful explicit public GC pressure request and entropy request fields.',
 'State public GC pressure requested true, entropy requested false and actual native GC count unobserved. Preserve the strong-owner/no isolated-root/finalizer/wipe qualifications.',
 'Bind the changed typed-result schema in the new guest/proposal/collector contract. Keep the actual native/component/GC result and all new action authorities NULL until separately reviewed.',
 'Prove exact reversibility to the held fixture and keep all unrelated HMAC/key/refusal/window/sentinel bytes unchanged.'],
 sourceFactsAlreadyVerified={'supportedBuildRootOption':True,'distinctFreezeRequired':True,'normalFrozenMembers':1391,'normalOriginalReferenceEntries':1387,'normalDistinctOriginals':1378,'normalMutableProjectOriginals':2,'staticHookSitesPerPressure':6,'newGuestSyntaxParsed':True},
 noRetroactiveDirectOnlyInterpretation=True,sourceOnly=True,ownerActionsInvoked=False,grantsActionAuthority=False))
(P/'README.md').write_text('''GC proposal source review: **HOLD** for GC-PROPOSAL-M1. No build or GC action is authorized.

The proposed guest deliberately calls public Buffer hex encode/decode paths that reach full-GC hooks in a future stress build, but its run record still reports `gcOrEntropyRequested:false`. The inherited field cannot be reinterpreted as direct-only after this change. A fresh immutable successor must distinguish public GC pressure requested, entropy requested and the unobserved actual collection count. The [finding](findings.json) and [correction contract](required-correction-contract.json) give exact source citations and required semantics.

The other bounded source checks passed. The existing recipe supports `NODE_COMPAT_BUILD_ROOT`; its source/CMake suffix omits the GC selector, so a fresh work root is necessary. The old `build-one.py gc-off` would reuse the normal project. A distinct freeze root and reviewed freezer/bootstrap successors are also required; none is implemented or authorized by this proposal. All 1,390 frozen copies plus the receipt give the exact protected 1,391-member normal freeze. All 1,387 original-reference entries, including 1,378 distinct paths and both vulnerable CMakeCache/compile-command originals, still match their captured bytes.

The eight guest edits reverse exactly to the sealed normal guest and preserve the four public ABI functions. Buffer allocation/fill supplies allocation pressure. The two public hex operations reach three native source hook sites each under the private Node target GC macro. These are six static sites per pressure record, not observed collections. Four exercise calls schedule sixteen records per one fresh outer validate call. Module holders, arguments and other locals remain combined strong owners; this cannot isolate temporary roots or observe finalization, freeing or wiping.

The [result](results.json) binds 14 source members and all 2,845 input descriptors. The reviewer performed read/hash/source inspection, three Python AST checks and the explicitly allowed pinned Node `--check` syntax parse only. The new guest parsed successfully; it was neither imported nor evaluated. No owner preparation/helper, preflight, native build, freezer, bootstrap, key, prototype, crypto, GC, component or guest action ran. New native pins, component/GC results and phase authorities remain absent.

[Reader history](reader-history.json) preserves corrected private assumptions about a numeric new-source count and the exact Buffer allocation parameter name. No author or historical packet was edited. This HOLD concerns the fixture/proposal observation contract; the separate native producer does not consume this guest.
''')
save('review-receipt.json',dict(schemaVersion=1,state=result['state'],sourceIndex=d['sourceIndex'],result=row(P/'results.json'),correctionContract=row(P/'required-correction-contract.json'),sourceOnly=True,sourceReviewPassed=False,mandatoryFindings=1,ownerActionsInvoked=False,pinnedNodeSyntaxOnly=True,actionAuthorityIssued=False))
files=[]
for q in sorted(P.rglob('*')):
 if q.is_file()and q.name!='index.json':
  v=row(q);v['path']=str(q.relative_to(P));files.append(v)
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_GC_SOURCE_HOLD_V1',files=files))
print(json.dumps({n:row(P/n)for n in ['index.json','results.json','required-correction-contract.json']}))
