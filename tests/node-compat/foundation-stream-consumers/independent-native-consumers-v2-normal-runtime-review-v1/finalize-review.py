"""Read-only nested Root/stream crosscheck and seal of this owned text review."""
from pathlib import Path
import hashlib,json,shutil
HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
FROZEN=Path('/tmp/starling-node-compat/production-consumers-v1/native-freeze')
LOGS=Path('/tmp/starling-node-compat/consumers355-v2-normal-runtime-build-root')

def sha(path):
 h=hashlib.sha256()
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def load(path):return json.loads(path.read_text())
def row(path):return {'path':str(path.relative_to(HERE)),'sha256':sha(path),'bytes':path.stat().st_size}
def put(name,value):
 with(HERE/name).open('x')as stream:stream.write(json.dumps(value,indent=2)+'\n')
def check(item):
 p=Path(item['path']);assert sha(p)==item['sha256']and p.stat().st_size==item['bytes']

results=load(HERE/'results.json')
assert results['state']=='INDEPENDENT_CONSUMERS355_V2_NORMAL_RUNTIME_NATIVE_FREEZE_PASSED_NO_GUEST'
assert(HERE/'stderr.log').read_text()==''
root=load(FAMILY/'native-integration-v2-normal-runtime-root-results.json')
assert sha(FAMILY/'native-integration-v2-normal-runtime-root-results.json')=='0866e4b8d76a4c89225b07124874587c29b0ecce8de7c6992eaa5f164a8615b8'
authority=load(FAMILY/'native-integration-v2-normal-runtime-build-root-review.json')
build_record=load(FAMILY/'native-integration-v2-normal-runtime-build-terminal-root-results.json')
check(build_record['oldThreePostbuild'])
postbuild=load(Path(build_record['oldThreePostbuild']['path']))
postfreeze=load(Path(root['oldThreePostfreezeCheckpoint']['path']))
for data in [postbuild,postfreeze]:
 assert data['rowsRehashed']==3492 and data['allMatched']is True
 assert data['prebuildCheckpoint']==authority['oldThreeFrozenPrebuildCheckpoint']
build_terminal=load(LOGS/'terminal.json');freeze_terminal=load(LOGS/'freeze.terminal.json');verify_terminal=load(LOGS/'verify.terminal.json')
assert build_terminal['argv']==authority['argv']
expected_freeze=['python3',str(Path(authority['argv'][1]).with_name('freeze-engine.py')),authority['expectedEngine'],'normal-runtime',authority['configuredSourceRoot']]
assert freeze_terminal['argv']==expected_freeze
assert verify_terminal['argv'][:2]==['python3','-c']and "verify_frozen_variant('normal-runtime'"in verify_terminal['argv'][2]
assert verify_terminal['argv'][3]==str(Path(authority['argv'][1]).parent)
for terminal,pid in [(build_terminal,80946),(freeze_terminal,2217),(verify_terminal,2236)]:
 assert terminal['rawExitCode']==0 and terminal['pid']==pid and terminal['observedByRoot']is True
 for key in ['stdout','stderr']:check(terminal[key])
 assert Path(terminal['stderr']['path']).read_bytes()==b''
build_stdout=load(LOGS/'stdout.log')
assert build_stdout['output']=='/tmp/starling-node-compat/production-consumers-v1/builds/normal-runtime'
assert build_stdout['result']==load(Path(build_stdout['output'])/'result.json')
freeze_stdout=load(LOGS/'freeze.stdout.log')
assert freeze_stdout['receiptPath']==str(FROZEN/'normal-runtime-freeze-receipt.json')
assert freeze_stdout['receipt']==load(FROZEN/'normal-runtime-freeze-receipt.json')
verified=load(LOGS/'verify.stdout.log')
for key,value in {'state':'ACTUAL_CONSUMERS355_FROZEN_NORMAL_RUNTIME_READ_ONLY_VERIFIED',
 'freezeReceiptSha256':results['freezeReceiptSha256'],'engineSha256':results['engineSha256'],'engineBytes':10009523,
 'metadataSha256':results['metadataSha256'],'copies':1164,'toolRows':767,'nativeInputs':355,'externalEmbeddingInputs':3,
 'consumerEnabled':True,'zlibEnabled':True,'gcStress':False,'entropyPolicy':'runtime-only','guestExecuted':False}.items():assert verified[key]==value,key
put('root-checkpoint-and-stream-crosscheck.json',{'schemaVersion':1,'state':'NESTED_ROOT_CHECKPOINT_AND_RAW_STREAM_VALUES_VERIFIED',
 'oldThreeRows':3492,'prebuildCheckpoint':authority['oldThreeFrozenPrebuildCheckpoint'],
 'postbuildCheckpoint':build_record['oldThreePostbuild'],'postfreezeCheckpoint':root['oldThreePostfreezeCheckpoint'],
 'postbuildAndPostfreezeMatchedPrebuildRecord':True,'RootHistoricalCheckpointEventsObservedByThisReader':False,
 'buildStdoutEqualsOwnedLauncherResult':True,'freezeStdoutEqualsActualReceipt':True,'verifyStdoutMatchesActualTupleAndCounts':True,
 'allThreeArgvPidsStatusesAndStreamsAuthenticated':True,'ownerActionsInvoked':False})

# Preserve the initial derivation record and record the corrected reader scope.
history=HERE/'history/consumer-define-scope'
shutil.copyfile(HERE/'reader-derivation.json',history/'initial-reader-derivation.json')
put('reader-corrections.json',{'schemaVersion':1,'history':'history/consumer-define-scope',
 'failedReaderExitCode':1,'artifactFailure':False,
 'reason':'The first derived reader expected NODE_COMPAT_STREAM_CONSUMERS on all native/embedding compiles; actual and prior normalOFF source contract selects exactly six private node CPP files, absent from embedding.',
 'correction':'Use the same private-target predicate as prior normalOFF, preserving actual exact six and entropyRuntimeOnly on all62 native+embedding.',
 'actualCorrectedReaderSha256':sha(HERE/'verify.py'),
 'orchestrationNote':'A preliminary JS tool orchestration printed rs rather than rr and raised ReferenceError after read-only source calls. The bounded reads were repeated; no owner/native action executed.'})

# Fresh final rehash of every finite reference collected by the independent reader.
for item in results['verifiedFiles']:check(item)
receipt={'schemaVersion':1,'state':'SEALED_INDEPENDENT_CONSUMERS355_V2_NORMAL_RUNTIME_NATIVE_FREEZE_PASS_NO_GUEST',
 'results':row(HERE/'results.json'),'reader':row(HERE/'verify.py'),
 'readerExit':{'exitCode':0,'observedByThisReader':True,'stdout':row(HERE/'stdout.log'),'stderr':row(HERE/'stderr.log')},
 'nativeProducerIndexSha256':results['sourceIndexSha256'],'engineSha256':results['engineSha256'],'engineBytes':10009523,
 'metadataSha256':results['metadataSha256'],'freezeReceiptSha256':results['freezeReceiptSha256'],
 'frozenCopies':1164,'originalReferences':1162,'oldThreeFrozenReferencesPreserved':3492,
 'completeRuntimeOpenSslSourcesIndependentlyRehashed':4650,'finiteFinalReferenceRehash':len(results['verifiedFiles']),
 'rootRawOuterStatuses':{'buildSession':7122,'freezeVerifySession':80421,'build':0,'freeze':0,'verify':0,'observedByThisReader':False},
 'nestedRootCheckpointsAndStdoutCrosscheck':row(HERE/'root-checkpoint-and-stream-crosscheck.json'),
 'allCheckedInRuntimePinsStillNull':True,'newReviewedPinAuthorityIssuedByThisReader':False,
 'ownerHelperNativeVerifierNinjaNmCompilerGuestHostOrTimingExecuted':False,
 'operationalAdmission':False,'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},
 'runtimeAcceptanceClaim':False,'performanceClaim':False}
put('review-receipt.json',receipt)
files=[]
for path in sorted(HERE.rglob('*')):
 if path.is_file()and path.name!='index.json':path.read_text();files.append(row(path))
put('index.json',{'schemaVersion':1,'state':receipt['state'],'files':files,'operationalAdmission':False,'runtimeAcceptanceClaim':False,'performanceClaim':False})
for item in files:assert sha(HERE/item['path'])==item['sha256']
print(json.dumps({'state':receipt['state'],'indexSha256':sha(HERE/'index.json'),'receiptSha256':sha(HERE/'review-receipt.json'),
 'resultsSha256':sha(HERE/'results.json'),'files':len(files),'finiteReferencesRehashed':len(results['verifiedFiles'])}))
