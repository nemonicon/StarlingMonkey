"""Seal finite independent SOURCE HOLD. No owner code is imported."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
d=json.loads((P/'data-results.json').read_bytes());f=json.loads((P/'findings.json').read_bytes())
assert d['sourceDataReviewComplete'] and d['mandatorySourceFindings']==1 and d['finiteLiteralEdgesIndependentlyReconstructed']==104
result={**d,'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_HTTP_HOST_SOURCE_REVIEW_HELD_V1','sourceIndexSha256':d['sourceIndex']['sha256'],
 'verifiedPassed':False,'sourceOnly':True,'sourceReviewPassed':False,'ownerActionsInvoked':False,
 'findings':f['findings'],'findingLedger':row(P/'findings.json'),'inputClosure':row(P/'rehashed-inputs.json'),'readerHistory':row(P/'reader-history.json'),
 'actualServerPortCurlRequestPreflightHelperComponentGuestNativeOrHostActionsInvoked':False,
 'sourceIndependentReview':None,'rootAuthority':None,'componentPhase':None,'hostController':None,
 'hostExecutionAllowed':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False,'sourcePromotionAllowed':False,
 'scope':'One source failure-evidence defect blocks host action. No actual host failure or response was observed. Other bounded admission/context/lifecycle/source observations were checked as source and retained DATA only.',
 'limitations':['The proposed servers, requests, returned355 response values and stopped-listener outcomes remain unexecuted. Source paths and stored pure fixtures establish no host behavior.',
 'The available actual component proof establishes construction/initialization and its binary/native provenance. It supplies no host authority or request-reuse, isolation, GC, backend, wire-body or performance result.',
 'Source preparation stored38812data/86pure/13grammar/2PythonAST checks were authenticated as owner evidence; the reviewer did not rerun owner tests or import owner code.',
 'The reviewer inspected and rehashed original immutable contexts. The old pure validator modules are not engine admission; their declared ephemeral response/audit views preserve full new raw audit/body objects.'],
}
save('results.json',result)
save('required-correction-contract.json',dict(schemaVersion=1,state='HTTP_HOST_M1_REQUIRED_RAW_RESPONSE_CAPTURE_SOURCE_CORRECTION_V1',heldSourceIndex=d['sourceIndex'],findingId='HTTP-HOST-M1',newImmutableSuccessorRequired=True,oldSourceAndAllEvidenceMustRemainUnchanged=True,
 requiredChanges=['Persist actual response status and public header values durably as soon as fetch returns, before attempting reader acquisition or body reads.',
 'On reader acquisition/read/abort/network failure, retain every available received body chunk before failure assertions/throw, including an empty partial body when appropriate.',
 'Distinguish complete body, partial body and capture/write failure truthfully. Never report full available raw evidence retained unless that capture succeeded; keep partial/failure responses unaccepted.',
 'Exercise injected headers-only, mid-body read rejection, abort/network failure and capture-write-failure cases using pure/synthetic seams without network/servers. Verify source-order and complete inherited helper/import/final-failure audit coverage.',
 'Bind the thin afterimages/new source index/output namespace and keep all future host/component/controller authorities NULL until source review and a separate Root action.'],
 preservedRequirements=['Genuine unchanged constructionConfig/httpPreflight and full355 metadata/manifests/contexts',
 'Exact same reviewed component/core and six standard WASI interfaces/type-only clock',
 'Original baseline/protected29/classic19/consumer fixtures and pure validators; raw full new audit/body data untouched',
 'Three requests per host, owned clean graceful shutdown, stopped curl7/no HTTP bytes and no later request to that stopped listener',
 'HOME/home/CODEX_HOME preserved; only intended XDG/TMP/user-config/project isolation',
 'Own/runtime dependency authentication before imports and final/failure full source/native/artifact rechecks'],
 sourceOnly=True,ownerActionsInvoked=False,grantsActionAuthority=False))
(P/'README.md').write_text('''HTTP host source review: **HOLD** for HTTP-HOST-M1. No host action is authorized.

The request function persists status/header metadata and ordinary body bytes only after the body stream completes. If reader acquisition, reading, abort or networking fails after headers or chunks arrive, its catch records only received-header and byte-count summaries. Available header values and body chunks are lost while the error claims all available raw evidence was retained. This is a source failure-evidence gap, not an observed server or guest failure. The [finding ledger](findings.json) gives source citations and static counterexamples; the [correction contract](required-correction-contract.json) requires a fresh immutable successor and honest complete/partial/capture-failure evidence.

Other bounded source checks passed. All 42 indexed members and 12,781 input descriptors were rehashed, resolving to 12,846 physical files including the actual component proof and prerequisite data. The finite module graph has 103 static edges and one literal dynamic edge. Four standard helper copies and all three command-lifecycle edits/reversals match exactly. Stored author test/syntax evidence was authenticated; no owner test was rerun.

The guard binds the actual da7a/368c/f371 component proof and unchanged construction config before calling the genuine published355 preflight. Full actual native metadata, all eleven selected manifests, configured/frozen/packaging contexts, the 12,667-file closure, two tool trees, 22 links and eight live WIT/adapter inputs remain declared and hashed. Six standard WASI imports, sole incoming handler and the type-only clock remain actual component facts. No old342 engine selector or metadata projection is substituted.

The accepted stock Wasmtime42 and wash2.11 command mechanisms, three-request schedule, private output/configuration, source rechecks, processes-directory setup, raw command/server terminals, owned groups, graceful-only acceptance and stopped curl7 checks are present. HOME, home and CODEX_HOME are carried unchanged; intended XDG/TMP and explicit wash user/project configuration supply isolation. Old combined/both-host validators receive explicit ephemeral DATA views; original new audit and response objects remain separate.

No preflight/helper, server, port, curl, request, componentizer, generated module, guest, native build or host action was invoked by this review. Root/source-peer/component-phase/controller authority slots stay absent. Actual HTTP behavior, request reuse/isolation, wire-body handling, GC, backend and performance are unproved. [Reader history](reader-history.json) retains a corrected private edge-category assumption; no author packet was edited.
''')
save('review-receipt.json',dict(schemaVersion=1,state=result['state'],sourceIndex=d['sourceIndex'],result=row(P/'results.json'),correctionContract=row(P/'required-correction-contract.json'),sourceOnly=True,sourceReviewPassed=False,mandatoryFindings=1,ownerActionsInvoked=False,hostExecutionAllowed=False))
files=[]
for q in sorted(P.rglob('*')):
 if q.is_file()and q.name!='index.json':
  v=row(q);v['path']=str(q.relative_to(P));files.append(v)
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CONSUMERS355_HTTP_HOST_SOURCE_HOLD_V1',files=files))
print(json.dumps({n:row(P/n)for n in ['index.json','results.json','required-correction-contract.json']}))
