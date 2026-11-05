"""Seal this independent Source/DATA review only; no owner API invocation."""
from pathlib import Path
import hashlib,json

OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'combined-native-freezer-candidate-v1'
EXPECTED='5230be984948519000c818450ada155917097ca26f259ee37dbcc3bb36728a4b'

def desc(path):
    raw=path.read_bytes()
    return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def data(path):return json.loads(path.read_bytes())
def save(name,value):(OWN/name).write_text(json.dumps(value,indent=2)+'\n')

index=desc(SOURCE/'index.json');assert index['sha256']==EXPECTED
source=data(SOURCE/'index.json');assert len(source['files'])==26
for row in source['files']:
    assert desc(SOURCE/row['path'])==dict(row,path=str(SOURCE/row['path']))
assert {p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob('*') if p.is_file()}=={r['path']for r in source['files']}|{'index.json'}
checks=data(OWN/'checks.json');refs=data(OWN/'references.json');assert checks['passed'] is True and checks['sourceIndex']==index
assert not (OWN/'reader.stderr.log').read_bytes()
native=data(SOURCE/'references.json')['nativeSourceIndex']
raw=dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1',freezerSourceIndexSha256=index['sha256'],nativeSourceIndexSha256=native['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeFreezeActionsInvoked=False,engineExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,
    freezerSourceIndex=index,nativeSourceIndex=native,actualBuildReview=refs['actualBuildReview'],actualBuildContract=refs['actualBuildContract'],actualBuildInputLedger=refs['actualBuildInputLedger'],engine=refs['engine'],metadata=refs['metadata'],rawMetadataFields=80,nativeSourceFiles=355,unchangedSecretParentFiles=348,nativeReplacements=7,externalEmbeddingSources=3,selectedManifestCount=11,compileDatabaseRows=68,policyCppCommands=62,otherConfiguredCommands=5,generatedNullCommands=1,separateEmbeddingCommands=1,strictCommands=4,privateCommands=6,
    independentChecks=desc(OWN/'checks.json'),independentSourceReadHashChecks=checks['checks'],independentPureChecks=checks['pureChecks'],ownSourceMembers=26,inheritedSourceFamilies=15,allAuthenticatedFamilies=checks['allAuthenticatedFamilies'],originalBuildInputsVerified=20816,originalBuildInputLogicalBytes=3869017050,uniqueReadHashInputs=checks['uniqueReadHashInputs'],uniqueReadHashLogicalBytes=checks['uniqueReadHashLogicalBytes'],originalModesAndLinkCountsVerified=20816,stagedOriginalPairs=1613,referenceAliases=31,archiveHardlinkReferences=1,failedV1WorkFiles=755,baseCopies=2544,baseCopyBytes=653814002,staticLibraries=29,objectFiles=69,exactReversibleFiles=5,exactReversibleEdits=990,
    actualOwnContextInertImported=True,globalsOrFrameRebound=False,genuineConfiguredProducerModelOrLayerInvoked=False,ownPureModelsOnly=True,authorChecksAuthenticatedNotRerun=True,rawMetadataChanged=False,allSourceFamiliesFullyRehashedAtCompletion=True,allInputIdentitiesAndModesStableAtCompletion=True,allOriginalBytesRehashedTwice=False,
    monitor=dict(actualSha256='7f557af375cd683810a11dbfcd1bd290712cc99d50b2664886d90cb888adace4',bytes=15094,exactTaskSelectionFreezerDonor=True,original0afSha256='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe',byteIdenticalOriginal0af=False,soleOriginal0afDelta='timeout_seconds <= 7200 becomes timeout_seconds <= 2400',actualCallPositionalArguments=6,actualDeadlineSeconds=2400,apiMismatch=False),
    materialFindings=[],qualifiedDocumentationFinding='README/API byte-identical0af wording means exact task-selection donor; original0af differs only deadline ceiling. See monitor tuple.',frozenOnlyVerifierSourceReviewed=True,frozenVerifierInvoked=False,actualFreezeResult=None,independentFrozenArtifactReview=None,rootFreezeAuthority=None,actionAuthorityGranted=False,
    limits=['Source review only; no actual frozen-artifact or external-parent acceptance.','Full originals hashed once in successful reader; completion checks all physical identities/modes and rehashes complete Source families.','All 20,816 references are not claimed physically copied; entire SDK/OpenSSL trees remain referenced inputs.','Superseded 57-byte preinstall settings were not separately retained or opened as a current file.','Raw post-build admission/Ninja capture is future work, not per-compiler raw terminals.','Bookend/root/inode checks do not establish adversarial concurrent-write isolation or a security sandbox.','No GC/runtime/all-invalid/resource lifecycle, reset/reuse, backend-version, zlib-deviation, adoption or performance acceptance.'],
    history=dict(reviewerReaderFirstAttemptRawExitCode=1,cause='reviewer-local missing global declaration at final AST loop',failedReader=desc(OWN/'reader-first-failed.py.txt'),failedStderr=desc(OWN/'reader-first-failed.stderr.log'),correctedReaderRawExitCode=0,ownerSourceUnchanged=True))
contract=dict(schemaVersion=1,state='FINITE_COMBINED355_FREEZER_SOURCE_REVIEW_CONTRACT_V1',requiredState=raw['state'],requiredFixedValues={k:raw[k] for k in ('schemaVersion','freezerSourceIndexSha256','nativeSourceIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','hostActionsInvoked','nativeFreezeActionsInvoked')},requiredExactDescriptors=dict(freezerSourceIndex=index,nativeSourceIndex=native,actualBuildContract=refs['actualBuildContract'],actualBuildInputLedger=refs['actualBuildInputLedger']),grantsFreezeOrRuntimeAuthority=False)
save('results.json',raw);save('result-contract.json',contract)
save('reader-terminal.json',dict(schemaVersion=1,kind='tool-observed-independent-data-reader',toolSession=19406,rawExitCode=0,stdout=desc(OWN/'reader.stdout.log'),stderr=desc(OWN/'reader.stderr.log'),ownerActionsInvoked=False,processIdNotIndependentlyRecorded=True,firstFailedToolSession=2837,firstFailedRawExitCode=1))
save('source-receipt.json',dict(schemaVersion=1,sourceOnly=True,result=desc(OWN/'results.json'),contract=desc(OWN/'result-contract.json'),checks=desc(OWN/'checks.json'),reader=desc(OWN/'review.py'),readerTerminal=desc(OWN/'reader-terminal.json'),sourceIndex=index,noActionAuthorityGranted=True))
files=[]
for path in sorted(OWN.rglob('*')):
    assert not path.is_symlink()
    if path.is_file()and path.name!='index.json':
        row=desc(path);row['path']=path.relative_to(OWN).as_posix();files.append(row)
save('index.json',dict(schemaVersion=1,files=files))
for row in files:assert desc(OWN/row['path'])==dict(row,path=str(OWN/row['path']))
for name in ('index.json','results.json','result-contract.json','source-receipt.json'):
    print(name,json.dumps(desc(OWN/name)),flush=True)
