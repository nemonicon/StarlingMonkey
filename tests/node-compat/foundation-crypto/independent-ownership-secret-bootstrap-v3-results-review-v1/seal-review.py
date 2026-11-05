"""Seal only this independent actual DATA review; no operational imports."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_bytes())
def row(p):
    p=Path(p);assert p.is_file()and not p.is_symlink();b=p.read_bytes()
    return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,v):
    with(HERE/n).open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
audit=load(HERE/'audit-results.json');actual=load(HERE/'actual-descriptors.json');checks=load(HERE/'checks.json')
t=load(HERE/'evidence/reader-attempt1/terminal.json')
assert t['rawExitCode']==0 and t['stderr']['bytes']==0 and audit['noConcreteActualEvidenceBlockerFound']is True
assert audit['checks']==checks['checks']==32260 and audit['paths']==28193
for k in ['stdout','stderr']:assert row(t[k]['path'])==t[k]
for p in HERE.rglob('*.py'):ast.parse(p.read_bytes())
for k,d in actual.items():
    if type(d)is dict and set(d)=={'path','sha256','bytes'}:assert row(d['path'])==d
result=dict(schemaVersion=3,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_ARTIFACT_BOOTSTRAP_RESULTS_REVIEW_PASSED_V3',
    verifiedPassed=True,dataReviewOnly=True,controllerProtocolSchemaVersion=1,toolingProtocolSchemaVersion=3,
    controllerSourceIndexSha256=actual['controllerSourceIndex']['sha256'],toolingSourceIndexSha256=actual['toolingSourceIndex']['sha256'],
    nativeSourceIndexSha256=actual['nativeSourceIndex']['sha256'],**{k:v for k,v in actual.items()if k!='schemaVersion'},
    actualProof=row(HERE/'audit-results.json'),inputClosure=row(HERE/'input-hashes.json'),checks=row(HERE/'checks.json'),
    readerTerminal=row(HERE/'evidence/reader-attempt1/terminal.json'),coverage=audit['coverage'],
    authenticatedLexicalPaths=audit['paths'],logicalBytes=audit['logicalBytes'],
    nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,metadataFields=75,
    variant='normal-off',otherVariantsNull=True,completeTypedPinDeltaReviewed=True,pinStateChanges=4,
    completePublicDataEqualsPythonFrame=True,completeVerifierFrameUnchanged=True,
    wholePublicDataFields=41,publicOwnPropertyCount=42,wholePublicDataBytes=2030522,
    apiCallsObserved=1,returnedRecheckCallsObserved=1,sourceSupportedCompleteVerifierCalls=1,
    observedNodePid=13692,observedPythonParentPid=14109,observedOwnedWorkerPid=14294,
    observedOuterProcessIdentities=118,observedPythonOperationIdentities=2,
    rawNodeExitCode=0,rawApiPythonParentExitCode=0,rawOwnedPythonWorkerExitCode=0,
    allObservedOwnedGroupsGone=True,timeoutObserved=False,forcedCleanupObserved=False,signalsObserved=False,
    sourceAndOriginalProtectionRechecked=True,normalProtectionRechecked=True,
    currentFrozenEntries=1902,currentFrozenTreeFiles=1903,oldNormalFrozenFiles=1391,oldNormalOriginalEntries=1387,
    validationBootstrapOnly=True,bootstrapPreviouslyExecutedByRoot=True,
    reviewedPinDerivationPreviouslyExecutedByRoot=True,reviewerActionsInvoked=False,
    helperApiBootstrapReturnedRecheckMonitorNodeOrEngineRerun=False,
    engineExecuted=False,guestExecuted=False,keyOperationsInvoked=False,gcActionsInvoked=False,
    moduleAdmissionGranted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsRuntimeAuthority=False,
    serializedCallableIsExecutable=False,oneShotApiRerunIntoExistingRootsAllowed=False,
    activeRuntimeAuthority=None,actualComponent=None,actualKeyRuntime=None,
    limitations=[
        'This is an actual DATA review of a completed validation-only bootstrap, not runtime, component, key, GC, backend or source-promotion acceptance.',
        'The original API was one-shot into fresh fixed roots, which now exist. It must not be called again into those roots. The serialized callable descriptor is evidence, not a recovered callable or permission to invoke recheck.',
        'The complete live return object is represented by its retained own-property shape, full DATA bytes and callable descriptor under authenticated observer Source; this reviewer did not inspect a still-live JavaScript object.',
        'The API and returned read-only recheck each have one durable start/completion and Source-supported counter. One observed Python parent and owned verifier worker support the original launch; process sampling is not proof about unobserved processes.',
        'The derive-controller raw zero is reported by Root tool6189 and its repository review/actual observation. No additional raw derive-controller stdout/terminal is fabricated. The enclosing bootstrap-controller tool26525 zero is Root-reported; Node/Python levels have separately retained raw terminals.',
        'All 75 metadata fields, 11 complete manifests and original/configured/build/frozen paths remain unchanged. Historical runtimeBackendProof stays false/null/null; bootstrap success does not upgrade that proof.',
        'The original API execFile terminal keeps timeoutCauseEstablished:false. Its normal completed case has raw0/full streams; no ambiguous killed/error case or inferred timeout cause is accepted.',
        'Full referenced source/tool/library/SDK protections are verified independently from the frozen payload. This is not a claim that every referenced byte or all OS files was copied into the frozen tree.',
        'Any later retained-bootstrap preflight needs a new reviewed read-only harness contract. This receipt does not manufacture an old admission state or replace the genuine original metadata/manifests.'
    ])
write('results.json',result)
fixed=['verifiedPassed','dataReviewOnly','controllerProtocolSchemaVersion','toolingProtocolSchemaVersion','controllerSourceIndexSha256','toolingSourceIndexSha256','nativeSourceIndexSha256','nativeSourceFiles','externalEmbeddingSources','selectedManifestCount','metadataFields','variant','otherVariantsNull','completeTypedPinDeltaReviewed','pinStateChanges','completePublicDataEqualsPythonFrame','completeVerifierFrameUnchanged','wholePublicDataFields','publicOwnPropertyCount','wholePublicDataBytes','apiCallsObserved','returnedRecheckCallsObserved','sourceSupportedCompleteVerifierCalls','rawNodeExitCode','rawApiPythonParentExitCode','rawOwnedPythonWorkerExitCode','allObservedOwnedGroupsGone','sourceAndOriginalProtectionRechecked','normalProtectionRechecked','validationBootstrapOnly','reviewerActionsInvoked','helperApiBootstrapReturnedRecheckMonitorNodeOrEngineRerun','engineExecuted','guestExecuted','keyOperationsInvoked','gcActionsInvoked','moduleAdmissionGranted','operationalAdmission','runtimeAcceptanceClaim','grantsRuntimeAuthority','serializedCallableIsExecutable','oneShotApiRerunIntoExistingRootsAllowed']
descriptors={k:v for k,v in actual.items()if type(v)is dict and set(v)=={'path','sha256','bytes'}}
descriptors.update({k:result[k]for k in ['actualProof','inputClosure','checks','readerTerminal']})
pairs={k:v for k,v in actual.items()if type(v)is dict and set(v)=={'index','result'}}
write('result-contract.json',dict(schemaVersion=3,requiredReviewState=result['state'],requiredResultSchemaVersion=3,
    requiredFixedValues={k:result[k]for k in fixed},requiredExactDescriptors=descriptors,
    requiredPairs=pairs,requiredCoverage=result['coverage'],result=row(HERE/'results.json'),
    callerBoundary='Retained DATA/protection only; no second invocation of the original one-shot API and no reconstructed executable recheck.',
    grantsRuntimeAuthority=False))
write('preparation-history.json',dict(schemaVersion=1,readerAttempts=[row(HERE/'evidence/reader-attempt1/terminal.json')],
    failedReaderAttempts=[],actualOperationsRerun=False,ownerOutputsChanged=False,
    actualDeriveRawToolReport='Root6189 zero, retained Root review and actual observation; no separate raw Root-tool stream invented.',
    actualBootstrapRawToolReport='Root26525 zero, distinct from independently decoded Node and Python retained terminal records.'))
with(HERE/'README.md').open('x')as f:
    f.write('''The completed secret-owner V3 pin derivation and one-shot JS bootstrap pass this independent DATA review. The whole recursively typed pin comparison has exactly four documented state/reviewRequired changes; every other field remains unchanged and the other three variants stay null. The schema-3 Root pin review matches the genuine template and actual original roles. Root's copied DATA outputs match their original bytes.

The entire 41-field, 2,030,522-byte public DATA is byte-identical and strictly JSON-equal to the actual Python frame. All 42 live-return own-property records are retained: 41 immutable enumerable DATA fields plus the actual immutable enumerable recheck function. The callable descriptor records name recheck and length zero. One API-call announcement and one returned-recheck start/completion are present; the latter fulfilled with undefined. The callable descriptor cannot restore an executable function after the process exits.

The original d62 API owned the single Python launch; no separate preliminary Python bootstrap ran. Plain pinned Node PID 13692 had no execArgv flags. The observed original Python parent was 14109 and the owned verifier worker 14294. The Node monitor, API execFile parent record and owned Python monitor all report zero, with complete raw streams, no timeout/signals/forced cleanup and all observed groups gone. All 118 outer process identities and the owned worker event are reconciled. Full raw Node JSON, two-record Python parent JSONL and whole worker JSON agree with their retained observations and complete frame.

The reader passed 32,260 checks across 28,193 lexical paths. Own d99/34839 Source, original d62/522e, a4c3 export, 2bbb candidate, 2295 export observation, all 27,976 declared inputs and 14 fixed families remain authentic. Current protections include 1,902 frozen entries/exact 1,903-file tree and old normal 1,391/1,387. All 75 metadata fields and 11 whole manifests remain intact; original/configured/build/frozen roots and false/null backend proof are preserved. Final identities, membership, private output modes and independent frozen inodes pass.

Only file hashing, JSON and typed DATA comparisons were performed by this reviewer. No API, bootstrap, helper, returned recheck, monitor, Node, engine, key, GC, guest or compiler was rerun. The derive Root-tool zero is Root-reported via its review/observation; no absent raw derive-tool stdout or terminal is invented. Process observations are bounded by sampling. No runtime, backend, erasure, component or key acceptance follows.

The original bootstrap output roots now exist, so the one-shot API cannot be called into them again. A later reusable retained-bootstrap preflight must be a distinct reviewed read-only harness over these exact retained facts and current protections. This receipt supplies no synthetic admission frame, metadata projection, live callable, or automatic action authority.
''')
write('review-receipt.json',dict(schemaVersion=3,state='INDEPENDENT_SECRET355_ACTUAL_BOOTSTRAP_DATA_REVIEW_SEALED',
    result=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),rootObservation=actual['rootObservation'],
    wholePublicData=actual['wholePublicData'],retainedPythonFrame=actual['retainedPythonFrame'],
    checks=32260,authenticatedPaths=28193,readerRawExitCode=0,allObservedOwnedGroupsGone=True,
    reviewerActionsInvoked=False,oneShotApiRerunAllowed=False,grantsRuntimeAuthority=False))
members=[]
for p in sorted(HERE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():
        assert p.name!='index.json';d=row(p);d['path']=p.relative_to(HERE).as_posix();members.append(d)
write('index.json',dict(schemaVersion=1,files=members))
assert {p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}=={'index.json'}|{d['path']for d in members}
for d in members:assert row(HERE/d['path'])=={**d,'path':str(HERE/d['path'])}
for d in descriptors.values():assert row(d['path'])==d
print(json.dumps(dict(index=row(HERE/'index.json'),result=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),receipt=row(HERE/'review-receipt.json'),indexedMembers=len(members),reviewerActionsInvoked=False)))
