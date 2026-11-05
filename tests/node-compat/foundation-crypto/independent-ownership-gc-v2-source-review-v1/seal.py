"""Seal bounded v2 guest/proposal SOURCE review, never an action authority."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n')
d=json.loads((P/'data-results.json').read_bytes());s=P.parent/'ownership-gc-candidate-v2';a=json.loads((s/'inherited-source.json').read_bytes());protection=json.loads(Path(a['normalProtection']['path']).read_bytes());root=Path('/private/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')
assert {str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}==set(protection['requiredNormalFreezeMembership'])
assert d['sourceDataReviewPassed'] and d['findingM1Closed'] and d['perRunPressureDeltas']==[4,4,8,0]
fixed=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_GC_SOURCE_REVIEW_PASSED_V2',sourceIndexSha256=d['sourceIndex']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False)
result={**d,**fixed,'verifiedPassed':True,'normalFrozenMembers':1391,'normalOriginalReferenceEntries':1387,'normalDistinctOriginalPaths':1378,
 'currentNormalFreezeMembershipUnchanged':True,'oldSourceIndex':a['heldSourceIndex'],'oldHoldIndex':a['holdReviewIndex'],'requiredPriorCorrectionContract':a['requiredCorrectionContract'],
 'normalExpectedRecord':a['acceptedNormalExpectedRecord'],'newExpectedRecord':row(s/'expected-complete-gc-record.json'),'collector':row(s/'collector.py'),'guestSource':row(s/'guest.GC.UNEXECUTED.mjs'),
 'wholeRecordDataReview':row(P/'whole-record-data-review.json'),'inputClosure':row(P/'rehashed-inputs.json'),
 'newObservationVersion':'public-buffer-gc-pressure-v1','outerSchemaVersion':2,'outerKind':'crypto-owner-within-export-gc-validation-v2',
 'perRunPressureRequestFlags':[True,True,True,False],'outerPressureRecords':16,'outerPublicGcPressureRequested':True,
 'entropyRequested':False,'actualNativeGcCountObserved':False,'strongApplicationOwnersCombinedOnly':True,
 'isolatedTemporaryRootsProved':False,'finalizerFreeWipeObserved':False,'newGcPin':None,'rootActionAuthority':None,'gcResult':None,
 'buildAllowed':False,'freezeAllowed':False,'bootstrapAllowed':False,'componentAllowed':False,'guestAllowed':False,'keyOperationsAllowed':False,'gcAllowed':False,
 'operationalAdmission':False,'runtimeAcceptanceClaim':False,'timingAllowed':False,'sourcePromotionAllowed':False,
 'scope':'The six-edit guest/proposal correction closes GC-PROPOSAL-M1 as bounded source/data. It does not review or authorize the separate native source pipeline, adopt a new native pin/component or establish a GC runtime result.',
 'limitations':['The [4,4,8,0]/outer16 counts are source pressure requests and completed pressure records for the declared fresh one-validate schedule. They are not observed collections, compactions or WebCrypto-internal GC.',
 'Combined module, argument and local strong owners remain. Temporary-root isolation, private copies, finalizers, freeing, wiping, heap, memory capacity, reuse and performance are unproved.',
 'The complete expected record is a synthetic source model derived from the pinned independently reviewed normal record. It is not an actual GC pass or a projection of changed metadata.',
 'The reviewer read/hashed source and retained data, inspected Python AST and performed private pure DATA comparisons. No owner module or guest was imported; no parser/Node/key/crypto/GC/native/preflight/helper/action was invoked by the reviewer.',
 'Stored owner35 pure checks and one pinned Node --check raw-zero syntax capture were authenticated. The source peer, Root phase, actual native/freeze/bootstrap/component and raw collector/export action gates remain separate prerequisites.'],
}
save('results.json',result)
save('result-contract.json',dict(schemaVersion=1,state='BOUNDED_CRYPTO_OWNER355_GC_V2_GUEST_PROPOSAL_SOURCE_CONTRACT_V1',requiredReviewState=fixed['state'],requiredFixedValues=fixed,
 reviewResult=row(P/'results.json'),sourceIndex=d['sourceIndex'],requiredGuest=row(s/'guest.GC.UNEXECUTED.mjs'),requiredCollector=row(s/'collector.py'),requiredCompleteExpectedRecord=row(s/'expected-complete-gc-record.json'),
 requiredFollowOnContract=row(s/'follow-on-contract.json'),oldHoldMustRemainUnchanged=a['holdReviewIndex'],
 sourceFacts=dict(perRunRequests=[4,4,8,0],perRunCompletedRecords=[4,4,8,0],perRunRequestFlags=[True,True,True,False],outerRequests=16,outerCompletedRecords=16,outerRequestFlag=True,entropyRequested=False,actualNativeGcCountObserved=False),
 grantsNativeOrGuestActionAuthority=False,requiredNextActions='Separately reviewed actual native/freeze/bootstrap and GC-only pin, selected-Buffer component source/artifact, raw typed collector and explicit Root export phase; no old normal guard or metadata projection.'))
(P/'README.md').write_text('''GC guest/proposal v2 source review passed. The [result](results.json) supplies the exact prospective source-peer state; the [contract](result-contract.json) grants no action authority.

The old ambiguous `gcOrEntropyRequested` field is removed. Each run snapshots pressure request/completion counters; attempts increment before Buffer allocation and records append only after every encoded/decoded byte check. Successful deltas are 4, 4, 8 and 0 with request flags true, true, true and false. The fresh outer validate reports sixteen requests/records and true. A failed pressure attempt can truthfully retain a requested call with no completed record. Entropy remains unrequested and actual native collection counts remain unobserved.

All six edits reverse exactly to the held pressure guest and its eight edits reverse to the original HMAC source. Every underlying key/tag/boolean/refusal/window/sentinel/counter field in the complete expected record matches the pinned independently reviewed normal record. The actual collector AST performs complete type-aware JSON comparison; unknown fields, old flags, blanket run3 pressure, changed counters/tags, wrong types, missing records, clipped bytes and failed runs cannot match. Private DATA counterexamples did not invoke the owner collector or guest.

All eighteen members and 2,943 input descriptors were hashed. The old proposal and HOLD remain exact. Normal protection retains all 1,387 reference entries/1,378 distinct originals and the exact 1,391-member freeze. The separate native source is referenced as unadopted source only. All actual pins, components, export phases and results remain absent here.

The reviewer used read/hash/static source, four Python AST checks and private pure DATA reconstruction. The stored owner syntax-only raw-zero evidence was authenticated; no new Node/parser, owner import/helper, preflight, native, key, crypto, GC, component or guest action ran. Strong application owners remain combined. No collection/compaction count, isolated root, finalizer/free/wipe, private heap, capacity, reuse or performance proof is established.
''')
save('review-receipt.json',dict(schemaVersion=1,state=fixed['state'],sourceIndex=d['sourceIndex'],result=row(P/'results.json'),contract=row(P/'result-contract.json'),sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,grantsActionAuthority=False))
files=[]
for p in sorted(P.rglob('*')):
 if p.is_file()and p.name!='index.json':
  x=row(p);x['path']=str(p.relative_to(P));files.append(x)
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_GC_SOURCE_V2_REVIEW_V1',files=files))
print(json.dumps({n:row(P/n)for n in ['index.json','results.json','result-contract.json']}))
