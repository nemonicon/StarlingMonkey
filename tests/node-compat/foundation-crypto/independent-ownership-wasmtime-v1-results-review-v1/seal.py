"""Seal only this independent DATA packet; no producer code imports or actions."""
from pathlib import Path
import hashlib,json,os,stat

HERE=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_bytes())
def descriptor(p):
    p=Path(p);before=p.stat();assert p.is_file() and not p.is_symlink();h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=p.stat();assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=before.st_size)
def write(name,value):
    p=HERE/name
    with p.open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    return descriptor(p)

assert not (HERE/'index.json').exists()
data=load(HERE/'data-results.json');ledger=load(HERE/'rehashed-inputs.json')
assert data['verifiedPassed'] is True and data['concreteBlockers']==[]
total=0
for d in ledger['files']:
    actual=descriptor(d['path']);assert all(actual[k]==d[k] for k in ['path','sha256','bytes']);total+=d['bytes']
assert len(ledger['files'])==data['uniqueInputsRehashed']==13504
root=load(data['requiredExactDescriptors']['rootResult']['path'])
refs=load(Path(data['requiredExactDescriptors']['sourceIndex']['path']).parent/'references.json')
actual_index=load(root['index']['path'])
members=[dict(path=str(Path(root['index']['path']).parent/r['path']),sha256=r['sha256'],bytes=r['bytes']) for r in actual_index['files']]
fixed={k:v for k,v in data.items() if k not in ['coverage','sessions','requiredExactDescriptors','artifacts','sourceReview','normalReview','artifactReview','sourceMembers','sourceClosureRows','uniqueInputsRehashed','freshFinalInputRehash','checks','concreteBlockers']}
exact=dict(**data['requiredExactDescriptors'],rawReturnLedger=descriptor(HERE/'decoded-coverage.json'),completeExpectedRecord=descriptor(HERE/'expected-complete-record.json'),inputRehashLedger=descriptor(HERE/'rehashed-inputs.json'),familyMembership=descriptor(HERE/'family-membership.json'))
observations=dict(schemaVersion=1,readerScope='independent standard-library READ/HASH/strict WAVE+JSON decode and complete model comparison only',rawRootSessionObservedByReviewer=False,retainedRootAndOwnedTerminalsAuthenticated=True,rawRootSession=43833,rootPid=15457,wasmtimePids=[16735,17913,17995],rawParentExitCode=0,rootHelperAdmissionExecuted=True,rootStockWasmtimeKeyFixtureExecuted=True,reviewerOwnerActionsInvoked=False,rawBeforeDecodeEvidence='Authenticated unchanged collector persists/fsyncs complete pipes and terminal before returning; caller retains whole decoded string before JSON/semantic assertions. Ordering is source-coupled, not independently traced fsync syscalls.',completeNativeCopies=1390,completeNativeFamilyRegularFiles=1391,normalMetadataRuntimeValidation=None,priorNormalGeneratedModuleAndNodeOracleExecuted=True,thisPhaseGeneratedJsImported=False,thisPhaseNewNodeOracleExecuted=False,componentImportsFromExistingArtifactReview=[],freshBinaryWitDecoderInvoked=False,fullChildEnvironmentValuesRetained=False,selectedControllerEnvironment=dict(PYTHONDONTWRITEBYTECODE='1',BINARYEN_CORES='1',RAYON_NUM_THREADS='1',CARGO_BUILD_JOBS='1'),retainedArgumentAccounting=dict(completeArgv=True,argumentBytes=[78,4,9,11,98],environmentBytes=4228,pointerBytes=680,totalBytes=5108,argMax=1048576,perArgumentLimit=None,kernelPaddingAndPerArgumentSemanticsNotProved=True),operationalRootDurationSeconds=root['operationalElapsedSeconds'],durationIsPerformanceSample=False,sourcePolicyNotRewritten=True,readerPreparationHistory=[dict(attempt=1,outcome='Reader refused source membership until the genuine nonindexed source-receipt.json was explicitly identified; no product error and no result files emitted.'),dict(attempt=2,outcome='Reader refused source-peer membership until its genuine nonindexed review-receipt.json was explicitly identified; no product error and no result files emitted.'),dict(attempt=3,outcome='Complete independent reader passed all retained outputs, complete expected fields, source/native closure and final input rehash.')],sourceAndNativeSealsModified=False,ordinaryAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,futureActionAuthority=None)
write('review-observations.json',observations)
limitations=[
 'Three fresh literal zero-argument validate() invocations on this exact component and normal355 native engine only.',
 'Each inner string is compared byte for byte against the actual accepted normal wrapper and every parsed field against a new complete independent expected object; no crypto oracle was rerun.',
 'Counters are public/source-coupled attempts, not native global or pending-operation instrumentation. Opaque imported key internals are not fully inspected.',
 'Application holders and public output/input stability are observed; native frees, finalizers, wipes, every private copy and isolated GC roots are not observed.',
 'Within one outer export only; no separate host-call interleaving, process/request reuse, GC, OOM, reset, another algorithm or general WebCrypto acceptance.',
 'Retained terminal/controller evidence and inspected source bind cleanup/raw-before-decode ordering; reviewer did not observe the live Root session or trace fsync syscalls.',
 'Selected environment values and complete argv are retained; full environment values and portable kernel/per-argument limits are not.',
 'imports[] and ABI come from the existing exact component review; this reader ran no new binary-WIT or AST decoder.',
 'Root preflight and actual Wasmtime key operations did execute; independent reviewer actions were strictly new Python DATA reads/hashes/decode.',
 'All durations are operational, no performance or memory claim, admission or future action authority.'
]
result={**data,'sourceOnly':False,'boundedPublicSourceCoupledReview':True,'allInputDescriptorsFinallyRehashedAgainAtSeal':True,'finalSealInputBytes':total,'rawRootSessionObservedByThisReader':False,'retainedParentAndWorkerTerminalsAuthenticated':True,'rootGenuineHelperAndThreeFreshStockWasmtimeKeyFixturesExecuted':True,'newNodeOracleOrGeneratedJsOrGcOomResetExecutedInThisPhase':False,'freshBinaryWitDecodeInvoked':False,'metadataRuntimeValidationUnchanged':None,'reviewerActedOnlyOnRetainedData':True,'futureGcOrOtherPhaseAuthority':None,'requiredExactDescriptors':exact,'limitations':limitations}
observations['sealPreparationHistory']=[dict(outcome='An initial independent seal.py SyntaxError occurred before any I/O; corrected dict construction in unsealed reviewer script, no producer failure or action.')]
result_row=write('results.json',result)
contract=dict(schemaVersion=1,state='FINITE_CRYPTO_OWNER355_STOCK_WASMTIME_V1_RESULTS_CONTRACT_V1',requiredReviewState=data['state'],requiredFixedValues=fixed,requiredCoverage=data['coverage'],requiredExactDescriptors=exact,artifacts=data['artifacts'],requiredArtifacts=data['artifacts'],sourceReview=data['sourceReview'],normalReview=data['normalReview'],normalContract=refs['normalContract'],artifactReview=data['artifactReview'],artifactContract=refs['artifactContract'],requiredSessions=data['sessions'],requiredActualOutputMembers=members,requiredActualOutputIndexedFiles=23,requiredActualOutputRegularFiles=25,requiredSourceClosureRows=13425,requiredFullNativeFamilyRegularFiles=1391,descriptorShape=['path','sha256','bytes'],finiteReviewIndexRequired=True,reviewResultIndexedExactlyOnce=True,allReviewIndexMembersRehashed=True,all23ActualOutputMembersAndIndexCompletionRequired=True,allThreeRawWaveStringsMustBeStrictlyDecoded=True,wholeDecodedUtf8BytesMustEqualActualNormalWrapper=True,allCompleteExpectedRecordFieldsMustMatch=True,rootAndOwnedTerminalsMustBeRawZeroClean=True,completePriorNormalAndArtifactContractsRemainRequired=True,comparisonScope='Three fresh stock Wasmtime42 literal validate() calls, complete bounded within-export four-case normal355 public/source-coupled fixture.',rootHelperAndWasmtimeKeyFixtureExecuted=True,reviewerHelpersPreflightNodeCliGeneratedJsWasmtimeGuestCryptoNativeActionsInvoked=False,fullEnvironmentValuesRetained=False,importsAudit='Existing same-component artifact proof only; no fresh binary-WIT decoder in this result review.',finalizerFreeWipeOrIsolatedRootObserved=False,separateHostCallInterleavingProved=False,processOrRequestReuseProved=False,nativeGlobalCountersInstrumented=False,gcExecuted=False,oomExecuted=False,resetExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,actionAuthorityIssued=False,futureActionAuthority=None,futureRootAction=None,limitations=limitations)
contract_row=write('result-contract.json',contract)
write('seal-verification.json',dict(schemaVersion=1,actualReaderChecksAtDataResult=data['checks'],uniqueInputDescriptorsFreshlyRehashed=13504,finalInputBytes=total,fullRawStrings=3,decodedUtf8Bytes=47187,sourceInputRows=13425,sourceMembers=30,actualIndexedFiles=23,actualRegularFiles=25,completeNativeFrozenMembers=1391,allExpectedFieldsPassed=True,allSourceAndNativeFilesPreserved=True,reviewerOwnerActionsInvoked=False))
receipt=write('review-receipt.json',dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_WASMTIME_V1_RESULTS_REVIEW_SEALED_V1',result=result_row,resultContract=contract_row,dataResult=descriptor(HERE/'data-results.json'),verifiedPassed=True,actionAuthorityIssued=False,futureActionAuthority=None))
files=[]
for p in sorted(HERE.rglob('*')):
    if p.is_file():
        r=descriptor(p);r['path']=p.relative_to(HERE).as_posix();files.append(r)
    else:assert p.is_dir() and not p.is_symlink()
index=write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_WASMTIME_V1_RESULTS_REVIEW_V1',files=files,verifiedPassed=True,reviewerReadHashDecodeOnly=True,actionAuthorityIssued=False))
assert len(list(HERE.rglob('*')))>=len(files)+1
for r in files:
    actual=descriptor(HERE/r['path']);assert actual['sha256']==r['sha256'] and actual['bytes']==r['bytes']
print(json.dumps(dict(index=index,result=result_row,resultContract=contract_row,receipt=receipt,indexedFiles=len(files),actualFiles=len(files)+1,uniqueInputsRehashed=13504,inputBytes=total)))
