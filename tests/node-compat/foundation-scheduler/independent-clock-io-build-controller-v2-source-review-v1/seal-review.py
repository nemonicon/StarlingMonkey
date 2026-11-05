"""Seal this independent source review only; no owner imports or actions."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
SUBJECT=HERE.parent/'clock-io-build-controller-candidate-v2'

def load(p):return json.loads(Path(p).read_bytes())
def row(p):
    p=Path(p);assert p.is_file()and not p.is_symlink();b=p.read_bytes()
    return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,v):
    with(HERE/n).open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')

audit=load(HERE/'audit-results.json');models=load(HERE/'model-results.json')
terminal=load(HERE/'evidence/reader-attempt1/terminal.json')
assert terminal['rawExitCode']==0 and terminal['stderr']['bytes']==0
assert audit['noConcreteSourceBlockerFound']is audit['fullPhysicalClosureCurrent']is True
assert audit['sourceInputs']==5667 and audit['authenticatedLexicalPaths']==5692
assert models['redirectCases']==35 and models['closeFailureCases']==5 and audit['checks']==models['checks']==10971
for k in ['stdout','stderr']:assert row(terminal[k]['path'])==terminal[k]
for n in ['review.py','seal-review.py']:ast.parse((HERE/n).read_bytes())
refs=load(SUBJECT/'references.json')
result=load(SUBJECT/'future-source-review-contract.json')
assert result['state']=='INDEPENDENT_CLOCK_IO_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V2'
result['controllerSourceIndexSha256']=audit['subjectIndex']['sha256']
result['actualProof']=row(HERE/'audit-results.json')
result.update(
    controllerSourceIndex=audit['subjectIndex'],proposalSourceIndex=refs['sourceIndex'],
    proposalSourceReview=refs['sourceReviewData'],predecessorSourceIndex=refs['predecessorIndex'],
    preservedRedirectHoldIndex=refs['redirectHoldIndex'],inputClosure=row(HERE/'input-hashes.json'),
    independentModelResults=row(HERE/'model-results.json'),readerTerminal=row(HERE/'evidence/reader-attempt1/terminal.json'),
    declaredPhysicalDependencies=5667,authenticatedLexicalPaths=5692,logicalBytes=audit['logicalBytes'],
    checkCount=audit['checks'],exactForwardInverseFiles=11,exactForwardInverseEdits=515,
    originalToolAliases=21,redirectStatusTargetCases=35,responseCloseFailureCases=5,
    localOpenerErrorDispatchCases=5,ownerStoredPureChecksAuthenticated=325,
    sourceCopiesPlanned=5138,sourceCopiesPerformed=0,sourceFiles=271,
    packageSourceFiles=5,jsDependencyFiles=4860,jsToolRootMetadataFiles=2,
    cachedLockedArchives=118,lockedFutureDownloads=models['missingDownloadEndpoints'],
    exactFutureCommandCount=8,perCommandCapsSeconds=[c['timeoutSeconds']for c in models['commandPlan']],
    workerDeadlineSeconds=7200,compilerJobs=1,
    minimumBoundaryFreeBytes=800*1024**2,startFreeBytes=2*1024**3,
    diskFloorMonitoredDuringCommand=False,fullFamilyAuthenticationBeforeCustomImport=True,
    fullFamilyAndInputRechecksOnFinalAndFailure=True,
    runtimeContextOrMetadataRebound=False,globalUrlOpenerInstalled=False,
    networkRequestsPerformed=False,vendorExtractionsPerformed=False,
    controllerOrMonitorExecuted=False,nodeOrCargoOrJcoInvoked=False,
    validAdapterPruningRun=False,adapterArtifactPublished=False,adapterCliPruneCommandInvoked=False,
    prunerFunctionInvokedByRefusalUnitTest=None,
    rootAuthority=None,actualStage=None,actualBuild=None,actualUnitResults=None,
    operationalAdmission=False,runtimeAcceptanceClaim=False,grantsActionAuthority=False,
    limitations=[
        'Source review only. A new exact Root authority/config and later independent build-result review are required; no download, stage, vendor, compiler, unit, Node or Jco action was run.',
        'Normal redirect responses are closed before refusal. If close raises, refusal still precedes a followup, but successful response closure is not established.',
        'The no-proxy local opener suppresses urllib environment/system proxy discovery and replaces the default redirect handler. It does not attest DNS, TLS/CA trust, intermediaries or all operating-system/SDK files.',
        'The 7200-second worker cap includes worker staging and hashing; command maxima do not add another allowance. Parent preflight, final hashing and cleanup may extend total operational elapsed time.',
        'Disk floors are observed at stage and before/after command boundaries, not continuously during commands.',
        'The four future Rust filters must each report exactly one passing test. The invalid-input refusal filter can call the pruner function; valid adapter pruning, CLI pruning and adapter publication remain disallowed.',
        'The 118 cached archives were authenticated and the author retained their parsed header DATA; the three missing locked archives were not downloaded by this reviewer.',
        'This review reran only extracted pure source/model functions and a request-free local stdlib opener/error dispatcher. It did not execute the controller module, operational main, monitor, network or build tools.'
    ])
template=load(SUBJECT/'future-source-review-contract.json')
for k,v in template.items():
    if v is not None:assert result[k]==v
    else:assert result[k]is not None
write('results.json',result)
fixed=['controllerSourceIndexSha256','sourceIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','hostActionsInvoked','buildActionsInvoked','networkRequestsPerformed','controllerOrMonitorExecuted','nodeOrCargoOrJcoInvoked','validAdapterPruningRun','adapterArtifactPublished','adapterCliPruneCommandInvoked','operationalAdmission','runtimeAcceptanceClaim','grantsActionAuthority']
descriptors=['controllerSourceIndex','proposalSourceIndex','predecessorSourceIndex','preservedRedirectHoldIndex','actualProof','inputClosure','independentModelResults','readerTerminal']
write('result-contract.json',dict(schemaVersion=1,requiredReviewState=result['state'],
    requiredFixedValues={k:result[k]for k in fixed},requiredExactDescriptors={k:result[k]for k in descriptors},
    sourceFutureContract=row(SUBJECT/'future-source-review-contract.json'),result=row(HERE/'results.json'),grantsActionAuthority=False))
write('preparation-history.json',dict(schemaVersion=1,readerAttempts=[row(HERE/'evidence/reader-attempt1/terminal.json')],
    failedReviewerAttempts=[],ownerPreparationHistory=row(SUBJECT/'preparation-history.json'),
    retainedOwnerFailedAttempt='evidence/pure-attempt1: HTTPError.url vs actual Python3.9 filename test assertion corrected; no operational action.',
    ownerEvidenceWasNotRerun=True,ownerActionsInvoked=False))
with(HERE/'README.md').open('x')as f:
    f.write('''The corrected clock controller passes this independent SOURCE review. The immutable 41b222 family, all 5,667 declared dependencies, five inherited families and 21 original tool aliases are authenticated. The 11-file derivation reverses exactly through 515 edits to 0640; the ef1f redirect HOLD and 55338/c9fa proposal remain unchanged.

The genuine stage uses a local opener with ProxyHandler({}) and the actual rejecting subclass. Thirty-five injected status/target cases cover 301/302/303/307/308, including same-URL, relative, cross-host, downgrade, malformed and missing Location. Each refuses before any fake parent.open and closes the normal response. Five additional close-failure cases refuse before followup without claiming closure succeeded; five local opener error-dispatch cases also pass. No request was opened and no global opener was installed.

Complete own-family and own-input authentication precedes operations and the sole custom monitor import. The loader rechecks before import; the real main, parent and worker retain full descriptor, identity and family checks through success and failure. Pre-WORK failure fallback and partial observations stay explicitly incomplete. No original module context, Root state, native metadata or imported monitor global is projected.

The pure plan preserves 5,138 copies: 271 source, five package-source and 4,862 tool files (4,860 dependencies plus two original tool-root metadata files under .toolchain-metadata), with 21 internal aliases. It retains 118 cached archives and exactly three literal locked future downloads, private regular-only bounded vendor extraction, independent roots and offline locked Rust commands. Eight actual command plans comprise two builds, four individually verified unit filters and two private Jco calls. Each Rust invocation uses jobs 1. The invalid-input pruner refusal unit may call the function; valid adapter transformation/CLI/publication remain closed.

The reader passed 10,971 checks over 5,692 lexical paths. These include initial streaming hashes, final identity/membership checks, mode checks, independent forward/reverse reconstruction, actual command-model evaluation, pinned Python 3.9 request-free opener tests and strict NULL/wrong-scope models. The author's 325 pure/injected/header checks and retained failed first reader attempt were authenticated without rerunning the author entrypoints.

This is no build or action authority. New Root/controller config and independent actual build acceptance remain necessary. Disk floors are boundary-only; the single 7,200-second worker cap includes worker staging/hashing, with parent/cleanup overhead explicitly separate. Host SDK selection is pinned partially, not all headers/OS files, DNS or TLS/CA policy. No controller, monitor, copy, vendor, download, Cargo, Node, Jco, valid pruner, native, component, engine or guest action ran in this review.
''')
write('review-receipt.json',dict(schemaVersion=1,state='INDEPENDENT_CLOCK_CONTROLLER_V2_SOURCE_REVIEW_SEALED',
    result=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),subjectIndex=audit['subjectIndex'],
    checks=10971,authenticatedLexicalPaths=5692,sourceInputs=5667,readerRawExitCode=0,
    fullSourceStabilityPassed=True,sourceOnly=True,ownerActionsInvoked=False,grantsActionAuthority=False))
members=[]
for p in sorted(HERE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():
        assert p.name!='index.json';r=row(p);r['path']=p.relative_to(HERE).as_posix();members.append(r)
write('index.json',dict(schemaVersion=1,files=members))
assert {p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}=={'index.json'}|{r['path']for r in members}
for r in members:assert row(HERE/r['path'])=={**r,'path':str(HERE/r['path'])}
for k in descriptors:assert row(result[k]['path'])==result[k]
print(json.dumps(dict(index=row(HERE/'index.json'),result=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),receipt=row(HERE/'review-receipt.json'),indexedMembers=len(members),ownerActionsInvoked=False)))
