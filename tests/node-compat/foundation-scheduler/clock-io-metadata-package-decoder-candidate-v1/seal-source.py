"""Finalize this Source family only; never invoke its operational controller."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
assert not(HERE/'index.json').exists(),'Use a new successor after sealing'
def row(path):
    p=Path(path);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(path):return json.loads(Path(path).read_bytes())
def write(name,value):
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
refs=read(HERE/'references.json');closure=read(HERE/'closure-verification.json');pure=read(HERE/'pure-results.json')
assert closure['files']==24525 and closure['completeFamilies']==12 and closure['allInputsReadHashed']is closure['allFinalIdentitiesAndMembershipsPassed']is True
assert pure['checks']==69 and pure['actualControllerImported']is pure['actualToolExecuted']is pure['actualDecoderExecuted']is False
assert refs['failedPhaseReview']is not None and refs['failedPhaseContract']is not None
for p in HERE.rglob('*.py'):ast.parse(p.read_bytes())
write('api-and-phase-contract.json',dict(schemaVersion=1,state='SOURCE_ONLY_CLOCK_METADATA_PACKAGE_CONTINUATION_PROTOCOL_V1',
    actualSourcePeer=None,actualRootAuthority=None,actualInvocation=None,actualMetadataResult=None,
    originalController=str(HERE/'controller.py'),
    originalMonitor=refs['monitor'],python=refs['python'],
    futureRootState='ROOT_REVIEWED_CLOCK_IO_METADATA_PACKAGE_PHASE_V1',futureRootPhase='decode-retained-wit-package-once',
    futureEntryArgv=[refs['python']['path'],'-B','-I',str(HERE/'controller.py'),'CONFIG_DESCRIPTOR_JSON'],
    enclosingRootMonitorRequired=dict(api='monitor(argv,cwd,environment,output,timeout_seconds,authority)',originalContext=refs['monitor']['path'],timeoutSeconds=300,wholeRawTerminalAndStreamsRequired=True),
    soleOwnedNativeCommand=[refs['wasmTools']['path'],'component','wit',refs['metadataPayload']['path']],nativeDeadlineSeconds=60,
    exactRetainedMetadataPayload=refs['metadataPayload'],failedPhaseReview=refs['failedPhaseReview'],
    fullOutputPolicy='Default native1.235 WIT renderer prints the main and every nested package; retain complete original stdout and stderr, exact native/outer terminals and full inventory. No output/metadata rewrite or importization.',
    acceptance='Only clean raw0/empty stderr/no signals/no errors/no forced cleanup/all owned groups gone plus finite full-output observations and final protection can yield an UNREVIEWED metadata result. A result filename alone is insufficient.',
    observedPackages=6,observedDeclarations=28,observedAliasAndResourceClauses=10,
    oldPhaseRemainsFailed=True,oldActionsRepeated=False,
    defaultAdapterPromotionAllowed=False,applicationComponentOrEngineOrGuestAllowed=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
write('preparation-history.json',dict(schemaVersion=1,
    failedPureAttempt=dict(evidence='evidence/pure-attempt1',rawExitCode=1,source='history/test-source-attempt1.py',cause='Static test used the first function-name occurrence, matching its definition rather than actual call. No controller/tool ran.'),
    intermediatePureAttempt=dict(evidence='evidence/pure-attempt2',rawExitCode=0,checks=61,source='history/test-source-attempt2.py'),
    finalPureAttempt=dict(evidence='evidence/pure-attempt3',rawExitCode=0,checks=69),
    actualFailureContractSchemaBound='Actual968c contract uses requiredFixedValues.state, not a generic requiredReviewState field; extracted guard was checked against actual retained DATA before sealing.',
    actualControllerMonitorDecoderOrOldPhaseActionsInvoked=False))
write('results.json',dict(schemaVersion=1,state='CLOCK_IO_METADATA_PACKAGE_DECODER_SOURCE_SEALED_UNREVIEWED_V1',sourceOnly=True,
    sourceRoot=str(HERE),failedRootObservation=refs['failedRootObservation'],failedPhaseReview=refs['failedPhaseReview'],failedPhaseContract=refs['failedPhaseContract'],
    normalizedAdapter=refs['normalizedAdapter'],prunedAdapter=refs['prunedAdapter'],metadataPayload=refs['metadataPayload'],
    nativeTool=refs['wasmTools'],nativeToolVersionFromConfiguredAndArchiveData='1.235.0',nativeToolArchiveMemberByteExact=True,
    sourceInputs=24525,completeFamilies=12,oldProtectedInputs=24359,logicalProtectedBytes=closure['logicalBytes'],
    exactDonorPrimitiveBytes=4257,completeAssemblyAndReversePassed=True,pureChecks=69,
    closure=row(HERE/'closure-verification.json'),protocol=row(HERE/'api-and-phase-contract.json'),
    sourceIndependentReview=None,rootAuthority=None,actualInvocation=None,actualMetadataResult=None,actualMetadataReview=None,
    actualControllerImported=False,actualMonitorImported=False,nativeToolExecuted=False,metadataDecoded=False,
    normalizerOrPrunerRerun=False,nodeValidationRerun=False,previousPhasePassed=False,
    applicationEngineOrGuestExecuted=False,adapterPromoted=False,defaultPackagerReplaced=False,
    operationalAdmission=False,runtimeAcceptanceClaim=False,
    remainingGates=['Independent Source review and a new explicit metadata-only Root action','Actual package-aware native decode with complete raw output/clean owned terminals/final protection','Independent actual metadata/composition DATA review before any overall private artifact acceptance; no default adapter replacement or guest action granted']))
write('source-receipt.json',dict(schemaVersion=1,state='SOURCE_ONLY_METADATA_PACKAGE_CONTINUATION_RECEIPT_V1',sourceRoot=str(HERE),result=row(HERE/'results.json'),sourceInputs=row(HERE/'source-inputs.json'),closure=row(HERE/'closure-verification.json'),pureModels=row(HERE/'pure-results.json'),sourceOnly=True,sourceIndependentReview=None,rootAuthority=None,actualMetadataDecoded=False,operationalAdmission=False))
members=[]
for p in sorted(HERE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():members.append(dict(row(p),path=p.relative_to(HERE).as_posix()))
write('index.json',dict(schemaVersion=1,files=members))
assert {p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}=={'index.json'}|{m['path']for m in members}
for m in members:assert row(HERE/m['path'])==dict(m,path=str(HERE/m['path']))
print(json.dumps(dict(index=row(HERE/'index.json'),result=row(HERE/'results.json'),receipt=row(HERE/'source-receipt.json'),members=len(members),actualDecoderExecuted=False),indent=2))
