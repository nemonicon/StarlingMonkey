"""Seal completed BUILD-only independent data review. No helper/tool actions."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
def row(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def save(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n')
a=json.loads((P/'audit-data.json').read_bytes());w=json.loads((P/'witness-review.json').read_bytes());spec=json.loads((P/'actual-evidence-inputs.json').read_bytes())
assert a['nativeCompileCommands']==62 and a['strictCompileCommands']==4 and a['privateCompileCommands']==6 and a['embeddingCompileCommands']==1 and w['verifiedPassed']and w['actualFinalNinjaStep']==[108,108]
unique={}
for r in a['inputs']+w['extraFileReads']:
 if r['path']in unique:assert unique[r['path']]==r
 unique[r['path']]=r
for r in unique.values():assert row(r['path'])==r
save('final-input-rehash.json',dict(schemaVersion=1,allInputsFinallyRehashed=True,uniqueInputPaths=len(unique),auditData=row(P/'audit-data.json'),witnessReview=row(P/'witness-review.json'),ownerActionsInvoked=False))
fixed=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_BUILD_REVIEW_PASSED_V1',verifiedPassed=True,
 sourceIndexSha256=a['sourceIndexSha256'],nativeSourceFiles=355,externalEmbeddingSources=3,variant='gc-off',configuredSourceRoot=a['configuredSourceRoot'],workRoot=a['workRoot'],
 externalParentExitCode=0,innerBuilderExitCode=0,allOwnedGroupsGone=True,allObservedOwnedGroupsGone=True,noForcedCleanup=True,
 sourceAndNormalProtectionRechecked=True,actualFreezeVerified=False,engineExecuted=False,guestKeyCryptoGcActionsInvoked=False,
 nativeCompileCommands=62,strictCompileCommands=4,privateCompileCommands=6,embeddingCompileCommands=1,
 gcStress=True,gcMacroPrivateTargetOnly=True,entropyPolicy='off',oomTesting=False,webCryptoEnabled=True,
 normalOriginalReferenceEntries=1387,normalDistinctOriginalPaths=1378,normalFrozenMembers=1391,normalCmakeCacheAndCompileCommandsUnchanged=True,
 operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,sourcePromotionAllowed=False)
exact={k:spec[k]for k in ['actualBuildResult','externalParentTerminal','rootBuildAuthority','rootBuildConfig','rootBuildObservation','engine','metadata','buildLog']}
result=dict(fixed,**exact,engineSha256=spec['engine']['sha256'],engineBytes=spec['engine']['bytes'],engineMetadataSha256=spec['metadata']['sha256'],
 sourceIndex=spec['sourceIndex'],sourceReview=spec['sourceReview'],controllerSourceIndex=spec['controllerSourceIndex'],controllerReview=spec['controllerReview'],actualSourceStageReview=spec['stageReview'],
 externalParentStarted=spec['externalParentStarted'],rootReportedToolRawExitCode=0,rootReportedToolSession=58915,rootRawToolTerminalDirectlyObservedByThisReader=False,
 ownedOuterPythonPid=49070,ownedInnerBashPgid=49081,observedProcesses=w['observedProcesses'],actualObservedFinalGroups=w['actualFinalGroups'],remainingObservedPids=[],
 fullRawBuilderStdoutEqualsActualResult=True,completeBuildLogRetained=True,actualFinalNinjaStep=[108,108],standaloneCMakeRawTerminalIndependentlyObserved=False,
 sourcePolicySha256='5a3bd48ebac975f7a3fd72691432b34c0e4afb9eec33bd2ad6273d78225193f9',sourceHelperSha256='4e5a1019ceffea629f2ec0b42322e17444cb877519596cb273ea34464d15bd78',recipeSha256='eec3245841fff07e5bf9c3ff7b488106c94b71705262b22272d60a8ea4d7bfb3',
 toolDependencyRows=922,changedNativePayloads=5,unchangedParentNativePaths=350,composedNativeEdits=20,actualChangedCryptoCppCommands=3,actualCryptoInstallNamespaceCount=1,
 actualCompiler='WASI SDK30 / LLVM21.1.4',sourceBeforeAfterManifestsAndRecipeSealsVerified=True,
 selectedCodecArchiveSha256='298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc',selectedCodecHeaders=4,selectedMozZDefinitions=7,
 actualCompilerCdOptimizerChainReconstructed=True,selectedHeaderSearchAndForcedIncludeVerified=True,noSecondCodecLink=True,
 opensslCompleteSourcesIndependentlyRehashed=4650,opensslVersion='3.0.17',cargoLocked=True,staticLibcryptoCleanupSymbolIndexVerified=True,
 runtimeBackendProof=dict(verified=False,version=None,vernum=None),
 auditData=row(P/'audit-data.json'),witnessReview=row(P/'witness-review.json'),finalInputRehash=row(P/'final-input-rehash.json'),readerHistory=row(P/'reader-history.json'),uniqueInputPathsFinallyRehashed=len(unique),
 reviewerReadHashJsonCompilerTextTarAndArchiveDataOnly=True,reviewerHelpersPreflightNodeGitCompilerNinjaNmEngineGuestKeysCryptoGcHostsOrTimingInvoked=False,
 actualGcFreezeReceipt=None,actualFrozenNativeArtifactReview=None,newReviewedGcPin=None,grantsFreezeOrOtherActionAuthority=False,
 limitations=['Completed BUILD-only provenance. No actual GC freeze, frozen inventory, reviewed GC pin, bootstrap, component, guest, key/crypto or GC workload result is established.',
 'Raw outer Python and inner Bash zero/cleanup records plus full logs and authenticated producer control flow support completion. No standalone CMake raw terminal is invented;108/108 is retained log evidence.',
 'Observed715 processes/final groups are the retained sampled monitor evidence. This does not prove that a descendant created and orphaned wholly between samples was observed.',
 'Selected headers/archive, raw compiler/link records, SDK tar/tool bytes and GNU cleanup symbol indices establish static build provenance. They do not execute zlib/OpenSSL or prove runtime freeing/zeroization/GC behavior.',
 'Root directly reported tool58915 raw zero. The reader independently authenticated its retained terminal, full streams, actual result and current input/artifact bytes; it did not observe the original tool event.',
 'Six private Node target commands carry GC stress; WebCrypto commands do not acquire that private macro. No collection count or GC inside a crypto call is inferred.',
 'BIGNUM/private-copy/allocation-bound, isolated-root, complete wipe, memory, reuse, full Node and performance follow-ons remain outside this build result.'])
save('results.json',result)
save('result-contract.json',dict(schemaVersion=1,state='SEALED_CRYPTO_OWNER355_GC_NATIVE_BUILD_ONLY_RESULT_CONTRACT_V1',requiredReviewState=fixed['state'],requiredFixedValues=fixed,requiredExactDescriptors=exact,reviewResult=row(P/'results.json'),
 requiredRootBindings=['Root.actualBuildRootAuthority == proof.rootBuildAuthority','Root.actualBuildExternalTerminal == proof.externalParentTerminal'],
 laterFrozenNativeArtifactState='INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_ARTIFACT_REVIEW_PASSED_V1',actualFreezeVerified=False,grantsActionAuthority=False,
 consumerRule='Authenticate this whole indexed proof and exact source/context/artifact/build/Root descriptors. A new separately reviewed source/controller and explicit Root freeze phase are still required before calling the genuine freeze wrapper. This build-only state cannot substitute for the later frozen native artifact proof.'))
(P/'README.md').write_text('''Independent actual GC native BUILD-only provenance review passed. The [result](results.json) and [contract](result-contract.json) expose the agreed eight exact build/Root/engine/metadata/log descriptors. This proof grants no freeze or runtime action.

Root reported tool58915 raw zero. Retained outer Python49070 and inner owned Bash49081 returned zero with no timeout, forced signal, error or remaining observed PID/group. All715 retained process observations reconcile with the terminal. Full raw builder stdout equals the actual result; the full2,064,357-byte build log contains the completed108/108 sequence. No standalone CMake raw terminal is claimed.

All355 actual native sources,922 tool inputs, three external embedding inputs and prebuild source/recipe seals match. All62 native commands, four strict commands, six private commands and the separate no-LTO embedding command were checked against raw compiler evidence. Only the six private Node commands carry GC stress. Release, entropyOFF, noOOM, WebCryptoON, the actual crypto install namespace and all three changed crypto CPP commands match the genuine source policy. The five native replacements/350 unchanged paths retain the exact reviewed owner355 identity.

The actual SDK30/LLVM21.1.4 archives, declared compiler aliases/tools, raw compiler/cd/optimizer chain, selected SM archive/four headers/forced include/header order, seven MOZ_Z definitions and lack of a second zlib library were checked without invoking tools. All4,650 patched OpenSSL3.0.17 source files match the authenticated archive; before/after audit, locked Rust inputs, actual libcrypto link and static cleanup-symbol archive entries agree. Backend proof remains false/null/null; no engine or crypto algorithm ran in this review.

The normal strict1,391-member freeze,1,387 original references/1,378 distinct originals, both normal CMake cache/compile-command inputs and the declared1,311 source-stage copies remain exact. Every recorded independent input was streamed again at sealing. [Reader history](reader-history.json) preserves two corrected private metadata/sort assumptions; no producer/source/evidence was changed.

No owner helper, preflight, Node, Git, compiler, Ninja, nm, engine, component, key, guest, GC, host or timing action was invoked. This is not the later frozen GC native artifact proof and does not issue a pin. Isolated GC roots, collection counts, freeing/wiping/private copies, BIGNUM/bounds, memory, reuse, runtime acceptance and performance remain unproved.
''')
save('review-receipt.json',dict(schemaVersion=1,state=fixed['state'],verifiedPassed=True,result=row(P/'results.json'),contract=row(P/'result-contract.json'),rootBuildObservation=spec['rootBuildObservation'],actualBuildResult=spec['actualBuildResult'],engine=spec['engine'],metadata=spec['metadata'],actualFreezeVerified=False,ownerActionsInvoked=False,grantsActionAuthority=False))
files=[]
for p in sorted(P.rglob('*')):
 if p.is_file()and p.name!='index.json':
  r=row(p);r['path']=str(p.relative_to(P));files.append(r)
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_BUILD_ONLY_REVIEW_V1',files=files))
print(json.dumps({n:row(P/n)for n in ['index.json','results.json','result-contract.json']}))
