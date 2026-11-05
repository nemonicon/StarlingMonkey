"""Seal this source review; no original operational module is imported."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'ownership-secret-artifact-bootstrap-v3-root-controller-candidate-v1'
def load(p):return json.loads(Path(p).read_bytes())
def row(p):
    p=Path(p);assert p.is_file()and not p.is_symlink();b=p.read_bytes()
    return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,v):
    with(HERE/n).open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
audit=load(HERE/'audit-results.json');checks=load(HERE/'checks.json')
terminal=load(HERE/'evidence/reader-attempt2/terminal.json');failed=load(HERE/'evidence/reader-attempt1/terminal.json')
assert terminal['rawExitCode']==0 and terminal['stderr']['bytes']==0 and failed['rawExitCode']==1
assert audit['noConcreteSourceBlockerFound']is audit['fullSourceAndOriginalProtectionCurrent']is True
assert audit['sourceInputs']==27976 and audit['authenticatedPaths']==28017 and audit['checks']==checks['checks']==31947
for t in [terminal,failed]:
    for k in ['stdout','stderr']:assert row(t[k]['path'])==t[k]
for p in HERE.rglob('*.py'):ast.parse(p.read_bytes())
refs=load(SOURCE/'references.json')
result=load(SOURCE/'future-source-review-contract.json')
assert result['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_BOOTSTRAP_ROOT_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
result['controllerSourceIndexSha256']=audit['subjectIndex']['sha256']
result['actualProof']=row(HERE/'audit-results.json')
result.update(
    controllerSourceIndex=audit['subjectIndex'],toolingSourceIndex=refs['toolingIndex'],toolingSourceReview=refs['toolingSourceReview'],
    actualExportReview=refs['exportReview'],actualExportContract=refs['exportContract'],actualExportCandidate=refs['exportCandidate'],
    actualExportRootObservation=refs['exportRootObservation'],originalBootstrapEntry=refs['bootstrapEntry'],originalPinModelEntry=refs['pinModelEntry'],
    originalMonitorIndex=refs['monitorIndex'],originalMonitorEntry=refs['monitorEntry'],
    inputClosure=row(HERE/'input-hashes.json'),checks=row(HERE/'checks.json'),readerTerminal=row(HERE/'evidence/reader-attempt2/terminal.json'),
    ownSourceMembers=40,declaredPhysicalInputs=27976,completeFixedFamilies=14,authenticatedPaths=28017,
    logicalBytes=audit['logicalBytes'],independentChecks=31947,originalProtectedRows=27729,
    wholeFrozenEntries=1902,wholeFrozenTreeFiles=1903,nativeSourceFiles=355,externalEmbeddingSources=3,
    selectedManifestCount=11,metadataFields=75,originalNormalFrozenFiles=1391,originalNormalReferenceEntries=1387,
    exactPythonPrimitiveSegments=8,exactJavascriptPrimitiveBlocks=1,
    storedAuthorPythonPureChecks=52,storedAuthorJavascriptPureChecks=21,
    ownFamilyAndInputsAuthenticatedBeforeCustomImports=True,fullFinalAndFailureSourceChecksReviewed=True,
    sourcePhases=['derive-pins','bootstrap-js'],originalToolingContextsPreserved=True,
    proposedPinDelta='Only document state/reviewRequired and normal-off pin state/reviewRequired; other three variants remain null.',
    proposedOriginalApiCalls=1,proposedReturnedRecheckCalls=1,proposedCompleteVerifierCalls=1,
    plainNodeExecArgvRequired=True,outerNodeDeadlineSeconds=1800,originalApiExecFileTimeoutMs=1200000,innerPythonWorkerDeadlineSeconds=600,
    completePublicOwnDataAndCallableDescriptorCaptureReviewed=True,completePublicDataEqualsWholePythonFrameRequired=True,
    rawStreamsBeforeSuccessChecksReviewed=True,observedOwnedGroupCleanupRequired=True,
    actualPinDerivationExecuted=False,actualPinModelLoaded=False,actualBootstrapApiCalled=False,actualReturnedRecheckCalled=False,
    actualMonitorInvoked=False,originalPythonBootstrapRunSeparately=False,nodeInvokedByReviewer=False,
    engineExecuted=False,guestExecuted=False,keyOperationsInvoked=False,gcActionsInvoked=False,
    metadataOrSourceContextProjected=False,moduleAdmissionGranted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,
    rootAuthority=None,actualPinDerivation=None,actualBootstrap=None,grantsActionAuthority=False,
    limitations=[
        'Source review only; no effective Root phase, pin output, bootstrap config, original API call, returned recheck, monitor, Node, helper or engine action was performed.',
        'A separately issued derive-pins authority is required before the genuine pure pin model can transform the actual candidate. Actual derived DATA then needs Root review before a distinct one-shot bootstrap-js phase.',
        'The proposed observer uses the genuine original d62 API, which owns its Python parent invocation. It does not run an initial separate Python bootstrap.',
        'One complete verifier call is a source-supported future expectation, not a measured current invocation count. Actual processes, raw streams, output membership and cleanup require a later independent DATA review.',
        'The returned object contract is the original frozen own-DATA frame plus an enumerable immutable recheck function. Accessors, symbol/undefined DATA and unexpected callable fields refuse; no arbitrary opaque-object capture or proxy-safety claim is made.',
        'The 1800-second outer Node cap, 1200000ms API execFile timeout and 600-second owned Python worker cap have distinct scopes. Collection, source hashing and cleanup can add overhead; this review establishes no runtime feasibility or performance.',
        'Original raw metadata, all eleven complete manifests, false/null backend fields, configured/build/frozen paths and original helper globals remain intact. This is a harness bootstrap protocol, not runtime or module admission.',
        'Source-input preservation includes referenced originals and SDK/library/tool files beyond the frozen payload; it does not mean every referenced byte was copied into the frozen tree.',
        'The reviewer authenticated stored author grammar/JS synthetic evidence and did not rerun Node or operational entrypoints. Its only executed extracted guard used synthetic pin DATA.'
    ])
template=load(SOURCE/'future-source-review-contract.json')
for k,v in template.items():
    if v is not None:assert result[k]==v
    else:assert result[k]is not None
write('results.json',result)
fixed=['controllerSourceIndexSha256','toolingSourceIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','hostActionsInvoked','bootstrapActionsInvoked','actualPinDerivationExecuted','actualBootstrapApiCalled','actualReturnedRecheckCalled','actualMonitorInvoked','nodeInvokedByReviewer','engineExecuted','guestExecuted','keyOperationsInvoked','gcActionsInvoked','moduleAdmissionGranted','operationalAdmission','runtimeAcceptanceClaim','grantsActionAuthority']
descriptors=['controllerSourceIndex','toolingSourceIndex','actualProof','actualExportContract','actualExportCandidate','actualExportRootObservation','originalBootstrapEntry','originalPinModelEntry','originalMonitorIndex','originalMonitorEntry','inputClosure','checks','readerTerminal']
write('result-contract.json',dict(schemaVersion=1,requiredReviewState=result['state'],
    requiredFixedValues={k:result[k]for k in fixed},requiredExactDescriptors={k:result[k]for k in descriptors},
    requiredPairs={k:result[k]for k in ['toolingSourceReview','actualExportReview']},
    sourceFutureContract=row(SOURCE/'future-source-review-contract.json'),result=row(HERE/'results.json'),grantsActionAuthority=False))
write('preparation-history.json',dict(schemaVersion=1,
    readerAttempts=[row(HERE/'evidence/reader-attempt1/terminal.json'),row(HERE/'evidence/reader-attempt2/terminal.json')],
    preservedFailedReader=row(HERE/'history/reader-attempt1.py'),
    readerCorrection='First reader selected an extra separator newline after the identical JS donor primitive block. The corrected reader uses the pinned donor block length (3263 bytes). Exact block hash a4db3778 matches both sources; no owner Source change.',
    earlierReadOnlyInspection='A strip-based precheck removed both terminal newlines; corrected before the first reader run to preserve the exact declared block bytes.',
    operationalFailureOrOwnerSourceChange=False,failuresOmitted=False,
    authorPreparationHistory=row(SOURCE/'preparation-history.json'),ownerActionsInvoked=False))
with(HERE/'README.md').open('x')as f:
    f.write('''The dormant one-shot crypto bootstrap controller passes this bounded independent SOURCE review. Its 40 own members, 27,976 declared physical inputs and 14 fixed source/proof families are authenticated. The independent reader checked 28,017 lexical paths and 31,947 source/DATA conditions, with final file identities and family memberships stable. Eight copied Python primitives and the 3,263-byte JS donor primitive block match the original d62 files exactly; old operational authorization bodies are not relocated.

The actual a4c3 export review, f224 contract, unchanged 2bbb candidate and 2295 Root observation keep their original roles. All 75 raw metadata fields, 11 whole selected manifests, 355 native and three embedding sources, 1,902 frozen entries and 1,903-file tree are protected. The older normal tree remains separate. No shortened metadata or selected/core/module manifest substitute is admitted.

The new derive-pins phase is explicitly Root-gated and calls the real original pure pin model. Its producer makes only the four documented state/reviewRequired changes; the genuine schema-3 selector and strict JS pin guard retain the full frame, frozen rows and other three null variants. A separate bootstrap-js phase requires actual derived pin DATA, the exact Root pin-review object and an independently issued original d62 bootstrap authority/config.

The Python parent invokes the genuine original 0af monitor with six positional arguments and a 1,800-second cap, launching plain pinned Node without execArgv flags. The Node observer repeats complete authentication before its only operational import: original d62/bootstrap.mjs. That API owns the single Python parent/worker path; there is no separate preliminary Python bootstrap. The observer durably announces its one API call, preserves all own DATA fields and the callable property descriptor, compares the complete DATA with the actual full Python frame, and invokes the returned read-only recheck once with before/after records. Parent and Node final/failure paths preserve source checks and require raw-zero, clean observed-group cleanup. Error or capture failure remains unaccepted.

The author's 52 Python and 21 JS pure checks and syntax evidence were authenticated, without rerunning their entrypoints or Node. This reviewer used file hashes, JSON, Python AST and one extracted guard on synthetic DATA only. A first reviewer run failed on an extra separator newline in its donor-block extraction; the original reader and raw failure are preserved, and corrected exact-range verification passes. Owner files were never changed.

This proof grants no pin derivation, bootstrap, helper, Node, monitor, engine, key, GC, guest, module, runtime or adoption authority. Live API behavior, full output membership, actual call/process counts and cleanup still need a future independent result review. The distinct 1,800-second outer, 1,200,000ms API and 600-second worker deadlines are protocol caps, not measured completion or performance evidence. Opaque/proxy-object transport, all OS/SDK files, physical erasure and backend-runtime proofs are outside this review.
''')
write('review-receipt.json',dict(schemaVersion=1,state='INDEPENDENT_SECRET355_BOOTSTRAP_ROOT_CONTROLLER_SOURCE_REVIEW_SEALED',
    result=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),subjectIndex=audit['subjectIndex'],
    independentChecks=31947,authenticatedPaths=28017,declaredInputFiles=27976,completeFixedFamilies=14,
    readerRawExitCode=0,retainedFailedReaderAttempts=1,sourceOnly=True,ownerActionsInvoked=False,grantsActionAuthority=False))
members=[]
for p in sorted(HERE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():
        assert p.name!='index.json';d=row(p);d['path']=p.relative_to(HERE).as_posix();members.append(d)
write('index.json',dict(schemaVersion=1,files=members))
assert {p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}=={'index.json'}|{m['path']for m in members}
for d in members:assert row(HERE/d['path'])=={**d,'path':str(HERE/d['path'])}
for k in descriptors:assert row(result[k]['path'])==result[k]
print(json.dumps(dict(index=row(HERE/'index.json'),result=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),receipt=row(HERE/'review-receipt.json'),indexedMembers=len(members),ownerActionsInvoked=False)))
