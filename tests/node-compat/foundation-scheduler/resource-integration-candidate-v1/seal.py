"""Seal only the inspected source/pure checker. No native, stage, Node or runtime action."""
from pathlib import Path
import hashlib,json,subprocess,sys,time

HERE=Path(__file__).resolve().parent
assert not(HERE/'index.json').exists()
EVIDENCE=HERE/'evidence'
EVIDENCE.mkdir(mode=0o700)
def descriptor(path,relative=False):
 raw=path.read_bytes();return dict(path=path.relative_to(HERE).as_posix()if relative else str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def write(name,value):
 with(HERE/name).open('x')as out:json.dump(value,out,indent=2);out.write('\n')
command=[sys.executable,str(HERE/'check-source.py'),str(EVIDENCE/'source-data-results.json')]
started=time.monotonic()
process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
for name in('stdout','stderr'):
 with(EVIDENCE/(name+'.log')).open('xb')as out:out.write(getattr(process,name))
terminal=dict(schemaVersion=1,command=command,rawExitCode=process.returncode,operationalSeconds=time.monotonic()-started,
             stdout=descriptor(EVIDENCE/'stdout.log'),stderr=descriptor(EVIDENCE/'stderr.log'),sourceCheckSubprocessOnly=True,
             nodeCompilerHelperStageOrRuntimeInvoked=False)
write('evidence/terminal.json',terminal)
assert process.returncode==0 and process.stderr==b''
data=json.loads((EVIDENCE/'source-data-results.json').read_bytes())
write('input-freeze.json',dict(schemaVersion=1,state='SOURCE_PREPARATION_REFERENCES_ONLY',files=data['inputs'],originalContextsRetained=True,
                             stageCopyRows=467,nativeRows=342,notACompletePackagingOrNativeArtifactClosure=True))
derivations=json.loads((HERE/'derivations.json').read_bytes())
policy=json.loads((HERE/'policy.json').read_bytes())
write('results.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_RESOURCE342_INTEGRATION_SOURCE_PREPARED_V1',
 sourceOnly=True,sourcePreparationPassed=True,sourceReviewPassed=False,sourceCheckpoint='6bc62c115d940568e8d21653127881f097db40ce',
 baseline='54b3329b3ce818fd1f244e871e9c259b63667cda',baselineKind='Accepted v13 corrected342 source and92-tool capture',
 nativeSourceFiles=342,unchangedNativeFiles=340,nativeAfterimageReplacements=2,externalEmbeddingSources=3,stageCopyRows=467,
 sourceDataAndPureChecks=data['checks'],inputDescriptors=len(data['inputs']),actualExpectedFunctionCases=342,oldReceiptNegativeCases=4,
 positiveNativeMetadataFabricated=False,pythonAstFiles=data['pythonAst'],recipePythonHeredocsParsed=data['recipePythonHeredocs'],
 helperReversibleEdits=len(derivations['helperEdits']),recipeReversibleReplacementGroups=len(derivations['recipeEdits']),
 newPolicy=descriptor(HERE/'policy.json'),newHelper=descriptor(HERE/'layer-policy.py'),newRecipe=descriptor(HERE/'proposed/tests/node-compat/build-engine.sh'),
 resourceOwnershipSourcePolicy=policy['resourceOwnershipSourcePolicy'],runtimeOrdinaryCases=7,runtimeTemplateHardNullActivation=True,
 timerSelectedInterfaces=['wasi:clocks/monotonic-clock@0.2.10','wasi:io/poll@0.2.10'],clockClosureAdmitted=False,unexpectedClockImportsMustFail=True,
 pureExpectedImports=[],argvAllocationFailureRuntimeProved=False,idExhaustionRuntimeProved=False,jsOrWitGrammarParserInvoked=False,
 cppFrontendForThisIntegrationInvoked=False,ownerHelperImported=False,nodeInvoked=False,gitStageOrBuildInvoked=False,componentOrGuestOrHostInvoked=False,
 productionSourceModified=False,native355ContextUsedAsBuildBaseline=False,oldReceiptsProjected=False,oldPassAdopted=False,
 actualSourceStage=None,actualNativePins={'normal-off':None,'gc-off':None},ownedBuildController=None,actualNativeOrFreezeReview=None,
 actualPackagingClosure=None,actualImportAdmission=None,actualComponentReview=None,actualGeneratedLoader=None,rootExportAuthority=None,
 sourceIndependentReview=None,rootStageAuthority=None,fullFallibleQueueImplemented=False,allInvalidSelectFixed=False,resetOrReuseImplemented=False,
 alsImplemented=False,publicNodeTimersEnabled=False,runtimeAcceptanceClaim=False,sourceCheckTerminal=descriptor(EVIDENCE/'terminal.json')))
for row in data['inputs']:
 assert descriptor(Path(row['path']))==row
write('source-receipt.json',dict(schemaVersion=1,state='RESOURCE342_SOURCE_PREPARATION_RECEIPT_NO_ACTIONS_V1',
 result=descriptor(HERE/'results.json'),inputFreeze=descriptor(HERE/'input-freeze.json'),derivations=descriptor(HERE/'derivations.json'),
 sourceOnly=True,rootStageAuthority=None,actualNativeReview=None,actualPackagingOrImportAdmission=None,runtimeAcceptanceClaim=False))
names=sorted(p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file())
assert not any(p.is_symlink()for p in HERE.rglob('*'))
write('index.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_SCHEDULER_RESOURCE342_INTEGRATION_SOURCE_V1',files=[descriptor(HERE/name,True)for name in names],
 sourceOnly=True,ownerActionsInvoked=False,sourceReviewRequired=True,actionAuthorityIssued=False))
index=json.loads((HERE/'index.json').read_bytes())
for row in index['files']:assert descriptor(HERE/row['path'],True)==row
assert sorted(p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file())==sorted(names+['index.json'])
for name in('index.json','results.json','source-receipt.json'):print(json.dumps(descriptor(HERE/name)))
print(json.dumps(dict(indexedFiles=len(names),sourceDataChecks=data['checks'],inputs=len(data['inputs']),ownerActionsInvoked=False)))
