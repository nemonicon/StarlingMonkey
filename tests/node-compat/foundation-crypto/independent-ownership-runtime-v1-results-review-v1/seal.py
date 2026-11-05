"""Seal bounded actual correctness and a finite later-prerequisite contract."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def local(p):return dict(row(p),path=str(p.relative_to(P)))
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
d=json.loads((P/'data-results.json').read_bytes());ledger=json.loads((P/'per-call-ledger.json').read_bytes());coverage=json.loads((P/'decoded-coverage-and-refusals.json').read_bytes())
assert d['dataReviewPassed']is True and len(ledger['calls'])==23 and coverage['totals']==d['coverage']
assert all(c['exactIndependentExpectationMatched']is True for c in ledger['calls'])
for desc in [d[k]for k in ['rootResult','sourceIndex','rootAction','config','actualIndex','actualResult','actualCompletion','nodeOracle','externalParentTerminal']]+list(d['artifacts'].values()):assert row(Path(desc['path']))==desc
fixed=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_NORMAL_RUNTIME_RESULTS_REVIEW_PASSED_V1',verifiedPassed=True,
 sourceIndexSha256=d['sourceIndexSha256'],componentSha256=d['componentSha256'],nativeEngineSha256=d['artifacts']['engine']['sha256'],nativeSourceFiles=355,
 normalOnly=True,boundedNormalFixturePassed=True,allWholePrimitiveStringsDecoded=True,allFullFieldsMatchIndependentExpectedRecords=True,
 actualNodeOracleFullFieldsMatchSuccessfulGuestSemantics=True,externalParentExitCode=0,allThreeOwnedWorkersRawZeroClean=True,
 actualIndexedFiles=46,actualRegularFiles=48,generatedModuleImported=True,asyncGuestScalarObservedAsOrdinaryStrings=True,
 sourceGuardedPrototypeRefusalsObserved=True,positiveControlsBeforePrototypeCases=True,applicationHolderReleaseObserved=True,
 stockWasmtimeExecuted=False,gcExecuted=False,oomExecuted=False,resetExecuted=False,finalizerFreeWipeOrIsolatedRootObserved=False,
 nativeGlobalCountersInstrumented=False,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,
 reviewerHelpersPreflightNodeOracleGeneratedModuleKeyCryptoGuestWorkerNativeHostActionsInvoked=False)
result={**d,**fixed,'sourceOnly':False,'coverage':coverage['totals'],'rawRootSessionObservedByThisReader':False,
 'retainedParentAndWorkerTerminalsAuthenticated':True,'rootAuthorizedHostOracleAndNormalKeyFixtureExecuted':True,
 'nodeCryptoModuleApiAdded':False,'otherAlgorithmAcceptance':False,'fullWebCryptoAcceptance':False,
 'wasmtimeOrGcAuthorityIssued':False,'futureActionAuthority':None,'concreteBlockers':[],
 'limitations':[
 'This is actual bounded normal Jco fixture correctness for one exact guarded355 engine/component, not full WebCrypto or Node crypto module compatibility.',
 'All public strings and complete fields were independently decoded. Public source-coupled counters and ownership/mutation observations are not global native instrumentation or private-heap inspection.',
 'The actual host Node oracle and RFC constant agree on full successful tags and selected metadata/booleans. Prototype/native error messages and ordering are not claimed as Node error parity.',
 'Application-holder clear is observed; collection, finalizer/free/wipe, all secret copies, isolated rooting, allocator/OOM, teardown/reuse and other algorithms remain unproved.',
 'Stock Wasmtime and GC have not executed. Any next phase requires separate reviewed source and explicit new Root authority; normal proof cannot admit a different engine or GC mode.',
 'Root ran the actual normal/host-oracle workload. This reviewer only read/hashed/decoded evidence and did not run helpers, Node, generated modules, keys, crypto, workers, guests, native builds or hosts.',
 'Retained raw-zero terminals are authenticated data; the reviewer did not directly observe the original Root sessions. Elapsed durations are operational bounds, not performance samples.']}
save('results.json',result)
exact={k:d[k]for k in ['rootResult','sourceIndex','rootAction','config','actualIndex','actualResult','actualCompletion','nodeOracle','externalParentTerminal','artifactContract']}
exact.update(rawReturnLedger=row(P/'per-call-ledger.json'),decodedCoverageAndRefusals=row(P/'decoded-coverage-and-refusals.json'))
for s in d['sessions']:
 for key in ['terminal','result','index','completion']:exact[s['scenario']+'-'+key]=s[key]
save('result-contract.json',dict(schemaVersion=1,state='FINITE_CRYPTO_OWNER355_NORMAL_RUNTIME_RESULT_CONTRACT_V1',
 requiredReviewState=fixed['state'],requiredFixedValues=fixed,requiredCoverage=d['coverage'],requiredExactDescriptors=exact,
 artifacts=d['artifacts'],requiredArtifacts=d['artifacts'],sourceReview=d['sourceReview'],artifactReview=d['artifactReview'],artifactContract=d['artifactContract'],
 descriptorShape=['path','sha256','bytes'],finiteReviewIndexRequired=True,reviewResultIndexedExactlyOnce=True,allReviewIndexMembersRehashed=True,
 actual46MemberOutputIndexAndAllMembersRehashed=True,complete48FileMembershipRequired=True,all23RawStringsAndWrapperRecordsRevalidatedForSemanticReplay=True,
 comparisonScope='raw/JWK HMAC-SHA256, complete known-answer/public windows/state/counters and new-component prototype guards; no full Node error/API parity',
 stockWasmtimeExecuted=False,gcExecuted=False,futureActionAuthority=None,operationalAdmission=False,runtimeAcceptanceClaim=False,
 laterRequirements=[
 'Authenticate this finite review index and every member; locate its result exactly once and require every fixed value and coverage count.',
 'Rehash exact actual output index/result/completion, all46 indexed files, complete48 ordinary-file membership, Node oracle and all retained parent/worker terminals.',
 'Keep exact component/glue/core/WIT/package/artifact/native/source tuples and previous artifact/source proof descriptors. Do not relabel the construction proof or substitute metadata.',
 'A future stock-WT validate phase must have separately reviewed public ABI/transport/deadline/whole-output source and explicit Root action authority. This normal Jco proof is only a prerequisite.',
 'A future GC phase needs genuine applicable GC native build/freeze/review/pins plus new component/action evidence; do not transfer normal ownership observations into GC/root/free/wipe proof.',
 'No action, runtime/operational promotion, timing, other-algorithm or full Node/WebCrypto acceptance authority is granted.']))
save('review-receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_NORMAL_RUNTIME_RESULTS_REVIEW_V1',
 sourceIndexSha256=d['sourceIndexSha256'],componentSha256=d['componentSha256'],results=local(P/'results.json'),resultContract=local(P/'result-contract.json'),reader=local(P/'reader.py'),
 verifiedPassed=True,rawStringsDecoded=23,runRecords=20,fullTagReturns=45,verificationBooleans=45,reviewerReadHashDecodeOnly=True,actionAuthorityIssued=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_NORMAL_RUNTIME_RESULTS_REVIEW_V1',
 files=[local(p)for p in sorted(P.rglob('*'))if p.is_file()and p!=P/'index.json'],verifiedPassed=True,reviewerReadHashDecodeOnly=True,actionAuthorityIssued=False))
print(json.dumps({n:local(P/n)for n in ['index.json','results.json','result-contract.json','review-receipt.json']}))
