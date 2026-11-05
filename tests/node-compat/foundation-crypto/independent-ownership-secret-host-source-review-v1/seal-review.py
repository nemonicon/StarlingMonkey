"""Seal a bounded independent Source review, never issue host permission."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'ownership-secret-host-candidate-v1'
EXPECTED='851392e5cca472b6b6f51a92ebcee1dc27b65359b301093d3b04c742519c34c2'
def desc(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
ix=desc(SOURCE/'index.json');assert ix['sha256']==EXPECTED
members=read(SOURCE/'index.json')['files'];assert len(members)==44
for r in members:assert desc(SOURCE/r['path'])==dict(r,path=str(SOURCE/r['path']))
assert not any(p.is_symlink()for p in SOURCE.rglob('*'))and{p.relative_to(SOURCE).as_posix()for p in SOURCE.rglob('*')if p.is_file()}=={r['path']for r in members}|{'index.json'}
checks=read(OWN/'checks.json');refs=read(OWN/'references.json');pure=read(OWN/'pure.stdout.log')
assert checks['passed']is pure['passed']is True and checks['sourceIndex']==ix and pure['pureCases']==58
assert not(OWN/'reader.stderr.log').read_bytes()and not(OWN/'pure.stderr.log').read_bytes()
assert pure['runSecretHostInvoked']is pure['wasmtimeOrCollectorOrMonitorOrGuestOrOracleInvoked']is False
runtime=read(Path(refs['actualRuntimeContract']['path']));jco_root=runtime['requiredExactDescriptors']['rootAuthority'];assert desc(Path(jco_root['path']))==jco_root
assert read(Path(jco_root['path']))['wasmtimeAllowed']is False
save('reader-terminal.json',dict(schemaVersion=1,kind='tool-observed-independent-source-data-reader',toolSession=2983,rawExitCode=0,stdout=desc(OWN/'reader.stdout.log'),stderr=desc(OWN/'reader.stderr.log'),ownerActionsInvoked=False,processIdNotIndependentlyRecorded=True))
save('pure-terminal.json',dict(schemaVersion=1,kind='tool-observed-source-pure-node-tests',rawExitCode=0,argv=[refs['node']['path'],str(SOURCE/'test-pure.mjs')],executable=refs['node'],stdout=desc(OWN/'pure.stdout.log'),stderr=desc(OWN/'pure.stderr.log'),sourceOnly=True,ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False,processIdNotIndependentlyRecorded=True))
result=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_HOST_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=ix['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False,wasmtimeExecuted=False,engineExecuted=False,keyOrGuestActionsInvoked=False,helperApiCollectorMonitorInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourceIndex=ix,
 actualRuntimeReview=refs['actualRuntimeReview'],actualRuntimeContract=refs['actualRuntimeContract'],actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],component=refs['component'],engine=refs['engine'],metadata=refs['metadata'],nativeSourceFiles=355,externalEmbeddingSources=3,fullMetadataFields=75,selectedManifestCount=11,emittedImports=[],publicAbiFunctions=['inspect','run','clear','validate'],actualJcoIndexedFiles=54,actualJcoActualFiles=56,actualJcoWrapper=refs['runtimeExactDescriptors']['rawWrapper'],nodeOracle=refs['runtimeExactDescriptors']['nodeOracle'],currentJcoRootAuthority=jco_root,currentJcoWasmtimeAllowedRemainsFalse=True,
 declaredInputs=34403,declaredInputLogicalBytes=2691407402,inheritedFamilies=38,ownSourceMembers=44,uniqueReadHashInputs=checks['uniqueReadHashInputs'],uniqueReadHashLogicalBytes=checks['uniqueReadHashLogicalBytes'],allAuthenticatedFamilies=checks['allAuthenticatedFamilies'],packagingFiles=4934,packagingAliases=22,explicitHistoricalDonorTrees=2,modules=10,staticEdges=14,dynamicEdges=1,exactReversibleFiles=6,exactReversibleEdits=435,sourceDataChecks=checks['checks'],independentPythonPureCases=10,sourceCoupledNodePureCases=58,retainedGrammarChecksAuthenticatedNotRerun=6,
 actualOwnContextInertImported=True,namespaceOrFrameInjected=False,allDeclaredInputsAndModesReadHashVerified=True,sourceFamiliesFullyRehashedAtReaderCompletion=True,allInputIdentitiesAndModesStableAtReaderCompletion=True,allLargeInputBytesIndependentlyRehashedTwice=False,rawMetadataProjected=False,
 proposedCoverage=dict(freshWasmtimeProcesses=3,outerPublicStrings=3,withinExportRunRecords=12,guestKeyImports=6,guestSignAttempts=33,guestVerifyAttempts=30,successfulFullTags=27,verificationBooleans=27,verifyTrue=15,verifyFalse=12,guardedCase3Records=3),
 actualHostResults=None,actualHostReview=None,rootHostAuthority=None,hostActionAuthorityGranted=False,materialFindings=[],independentChecks=desc(OWN/'checks.json'),
 limits=['Source-only verdict; no actual host execution or new authority.','No new Node oracle, original one-shot/helper/API/recheck, generated-JS or crypto operation was run.','Large protected originals were fully hashed once in the successful reader; completion rehashes complete Source families and checks all captured physical identities/modes.','Exact membership covers declared families/package/Jco/historical trees, not every arbitrary ancestor directory.','Failure evidence is limited to actual registered/persisted files; writer failures may leave partial evidence.','The2GiB disk check is a start boundary; pipe bounds and timeouts are operational limits.','Three future fresh validate wrappers do not prove separate host-call interleaving, process/request reuse, finalizer/free/wipe or native GC behavior.','No old75 secret-frame to80 combined-frame projection, other variants, adoption, security completeness or performance acceptance.'])
save('results.json',result)
save('result-contract.json',dict(schemaVersion=1,requiredState=result['state'],requiredFixedValues={k:result[k]for k in('schemaVersion','sourceIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','hostActionsInvoked','runtimeActionsInvoked')},requiredExactDescriptors=dict(sourceIndex=ix,actualRuntimeContract=refs['actualRuntimeContract'],actualArtifactContract=refs['actualArtifactContract']),hostActionAuthorityGranted=False))
save('source-receipt.json',dict(schemaVersion=1,sourceOnly=True,result=desc(OWN/'results.json'),contract=desc(OWN/'result-contract.json'),checks=desc(OWN/'checks.json'),reader=desc(OWN/'review.py'),readerTerminal=desc(OWN/'reader-terminal.json'),pureTerminal=desc(OWN/'pure-terminal.json'),sourceIndex=ix,noActionAuthority=True))
files=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file()and p.name!='index.json':files.append(dict(desc(p),path=p.relative_to(OWN).as_posix()))
save('index.json',dict(schemaVersion=1,files=files))
for r in files:assert desc(OWN/r['path'])==dict(r,path=str(OWN/r['path']))
for n in('index.json','results.json','result-contract.json','source-receipt.json'):print(n,json.dumps(desc(OWN/n)),flush=True)
