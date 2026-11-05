"""Independent finite ACTUAL failure audit; stdlib read/hash/DATA/AST only.

No producer imports, subprocesses, process scans/signals, helpers or engine calls.
"""
from pathlib import Path
import ast,json,os,re
import review_io as I
HERE=Path(__file__).resolve().parent;K=HERE.parent
SOURCE=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source');FREEZE=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze')
NATIVE=K/'ownership-gc-native-candidate-v2';DRAFT=K/'independent-ownership-gc-native-artifact-review-v1'
def row(p):return I.descriptor(str(p))
def load(p):return I.read(row(p))
def eq(a,b,label):I.need(json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True),label)
def write(name,v):
    with(HERE/name).open('xb')as f:f.write((json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
root_row=dict(path=str(K/'ownership-gc-v2-freeze-failure-root-results-v1.json'),sha256='a396094463cc6f456b9678ebb2fb50d362188986ac4b2f7213ef393c77f148c8',bytes=10406)
root=I.read(root_row,'exact final Root failure record');I.need(root['rootObservedToolRawExitCode']==1 and root['rootToolSessionId']==34426 and root['pythonParentPid']==75163,'actual Root failure tuple, never artifact success')
I.need(root['state']=='ROOT_OBSERVED_CRYPTO_OWNER355_GC_FREEZE_FAILED_HELPER_SELECTION_M2_V1'and root['finding']=='GC-HELPER-SELECTION-M2','literal failed phase retained')
I.verify_descriptors(root,'whole original failure Root record')
terminal=I.read(root['externalParentTerminal']);started=I.read(root['externalParentStarted']);authority=I.read(root['rootAuthority']);config=I.read(root['config'])
I.need(root['externalParentTerminal']['sha256']=='7fc79a609852913a884edb8064aa3949700e6cb28416cd297f1fa01ed2b7fb7a'and root['stderr']['sha256']=='07c8b7105fd63aac2ddacf1e421b4c8725f5b33d441c21b05572135b9caa9ab8','exact independent raw tuple')
for k,v in dict(pid=75163,rawExitCode=1,timeout=False,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,forcedCleanup=False).items():eq(terminal[k],v,'raw failed terminal '+k)
for k in ['errors','signals','interruptedSignals','remainingObservedPids']:eq(terminal[k],[],'clean owned failure lifecycle '+k)
I.need(len(terminal['observedProcesses'])==len(terminal['finalGroups'])==1 and terminal['finalGroups'][0]==dict(pgid=75163,alive=False,signalAllowed=False),'one retained observed group gone')
eq(terminal['authority'],root['rootAuthority'],'raw terminal actual phase authority');eq(terminal['stdout'],root['stdout'],'whole raw stdout binding');eq(terminal['stderr'],root['stderr'],'whole raw stderr binding')
I.need(root['stdout']['bytes']==0 and root['stderr']['bytes']==898,'zero stdout and complete898-byte stack')
eq(config,dict(schemaVersion=1,sourceIndex=root['nativeSourceIndex'],rootAuthority=root['rootAuthority']),'authentic issued freeze config')
I.need(authority['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PHASE_V1'and authority['phase']=='freeze'and authority['freezeAllowed']is True and authority['variant']=='gc-off','authentic one-phase freeze authority, no projected action')
eq(authority['sourceIndexSha256'],root['nativeSourceIndex']['sha256'],'native source authority join');I.need(root['nativeSourceIndex']['sha256']=='ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05','old exact source seal preserved')
for k in ['stageAllowed','buildAllowed','exportAllowed','bootstrapAllowed','guestAllowed','keyOperationsAllowed','prototypeWorkloadsAllowed','componentAllowed','nativeSourceChangesAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:I.need(authority[k]is False,'original excluded phase scope '+k)
for k in ['reviewedGcPins','gcNativeRootReview','independentGcNativeReview','pinCandidateOutput']:I.need(authority[k]is None,'actual original unissued slot '+k)
I.need(authority['configuredSourceRoot']==str(SOURCE)and authority['freezeRoot']==str(FREEZE)and authority['externalParentDeadlineSeconds']==2400,'actual isolated source/freeze context')
eq(started['authority'],root['rootAuthority'],'started actual phase');I.need(started['pid']==75163 and started['timeoutSeconds']==2400 and started['argv'][1]==str(NATIVE/'freeze.py'),'actual owned wrapper argv')
eq(I.decode(started['argv'][2].encode()),root['config'],'actual exact config argument')
external=I.canonical(root['externalParentTerminal']['path']).parent;external_rows=[]
for p in external.iterdir():
    I.need(p.is_file()and not p.is_symlink()and p.stat().st_nlink==1,'ordinary independently retained failure evidence');d=row(p);I.verify(d,'whole failure external inventory');external_rows.append(d)
I.exact_tree(external,['started.json','terminal.json','stdout.log','stderr.log','owned-0000.json'])
owned=load(external/'owned-0000.json');I.need(owned['sequence']==0,'single ordered ownership observation');eq([owned['process']],terminal['observedProcesses'],'all retained process identity fields')
I.need(owned['process']['pid']==owned['process']['pgid']==75163,'fresh parent-owned session observed')
# Authenticate all issued source and controller families, proofs and predecessor holds.
families=[]
for d in [root['nativeSourceIndex'],root['controllerSourceIndex'],root['controllerSourceReviewIndex'],authority['independentSourceReview']['index'],authority['independentStageReview']['index'],authority['independentBuildReview']['index']]:
    index,members=I.indexed(d,'whole actual failed-phase prerequisite');families.append(dict(index=d,indexedMembers=len(members)))
I.verify_descriptors(authority,'all actual freeze authority prerequisite descriptors')
refs=load(NATIVE/'references.json');I.verify_descriptors(refs,'complete inherited native phase source references')
inputs=load(NATIVE/'stage-inputs.json');I.need(len(inputs['files'])==1311,'complete staged source context')
for d in inputs['files']:
    original=d['original'];I.verify(original,'unchanged normal staged original');I.verify(dict(path=str(SOURCE/d['path']),sha256=original['sha256'],bytes=original['bytes']),'unchanged isolated staged source')
stage_peer=I.read(authority['independentStageReview']['result']);I.need(stage_peer['declaredCopiedPaths']==1311 and stage_peer['actualDetachedGitHead']=='54b3329b3ce818fd1f244e871e9c259b63667cda','actual detached base plus finite1311 overlay, not an entire-tree1311 claim')
for p in [NATIVE/'input-freeze.json',NATIVE/'inherited-source.json']:
    value=load(p);I.verify_descriptors(value,'immutable own full native source closure')
# Eleven suffix candidates are actual immutable ordered DATA, not hypothetical rows.
matches=[d for d in inputs['files']if d['path'].endswith('/artifact-tools/artifact_common.py')]
I.need(len(matches)==11,'exact actual ambiguous suffix candidates');eq(matches,root['suffixMatches'],'whole eleven actual ordered suffix rows');eq(matches[0],root['wrongSelectedRow'],'actual first suffix selection')
exact='tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools/artifact_common.py';correct=[d for d in inputs['files']if d['path']==exact]
I.need(len(correct)==1 and matches[4]==correct[0],'exact crypto row uniquely present at suffix ordinal4');eq(correct[0],root['correctSelectedRow'],'whole actual correct row')
expected=matches[0]['original'];actual=I.descriptor(str(SOURCE/exact));eq(actual,root['actualCorrectHelper'],'actual helper bytes remain genuine')
I.need((expected['sha256'],expected['bytes'])==('8d3d872acf46a800332ba99cb3c1815ecb291a9e395dc9a80baf2b1d46b77ef8',15391),'wrong first helper exact bound tuple')
I.need((actual['sha256'],actual['bytes'])==('fff7bed72aec0c592e7a788060a5c1ecf6a0b0694ca519dbfa00e230584123ab',19299),'correct crypto helper exact tuple')
I.need(expected['sha256']!=actual['sha256']and expected['bytes']!=actual['bytes'],'genuine regular hash/size gate necessarily refuses, without invoking it')
# Verify full retained traceback against exact source line numbers, no owner evaluation.
stderr=I.verify(root['stderr']).read_text();I.need(stderr.startswith('Traceback (most recent call last):\n')and stderr.endswith('AssertionError\n'),'complete raw AssertionError stack')
frames=[]
for file,line,function,shown in re.findall(r'  File "([^"]+)", line (\d+), in ([^\n]+)\n    ([^\n]+)\n',stderr):
    source=I.verify(row(file),'actual traceback source');lines=source.read_text().splitlines();I.need(lines[int(line)-1].strip()==shown,'exact stack line matched held source');frames.append(dict(path=file,line=int(line),function=function,source=shown))
I.need([(Path(f['path']).name,f['line'],f['function'])for f in frames]==[('freeze.py',18,'<module>'),('freeze.py',12,'freeze'),('guard.py',57,'load_common'),('data_io.py',16,'regular')],'whole expected actual four-frame stack')
guard_text=(NATIVE/'guard.py').read_text();freeze_text=(NATIVE/'freeze.py').read_text();controller_text=I.verify(authority['externalControllerEntry']).read_text()
trees={str(p):ast.parse(p.read_text())for p in [NATIVE/'guard.py',NATIVE/'freeze.py',NATIVE/'freezer-body.py',NATIVE/'data_io.py',Path(authority['externalControllerEntry']['path'])]}
guard_tree=trees[str(NATIVE/'guard.py')];load_common=next(n for n in guard_tree.body if isinstance(n,ast.FunctionDef)and n.name=='load_common');snippet=ast.get_source_segment(guard_text,load_common)
for s in ["expected=next(r for r in frame['stageInputs']['files']if r['path'].endswith('/artifact-tools/artifact_common.py'))['original']","regular(dict(path=str(path),sha256=expected['sha256'],bytes=expected['bytes']))","common.HERE==Path(C.TOOLS)and common.REPO==Path(C.SOURCE)"]:
    I.need(s in snippet,'actual deterministic helper-source selection/gate '+s)
I.need(snippet.index('regular(dict(')<snippet.index('spec=importlib.util.spec_from_file_location')<snippet.index('spec.loader.exec_module(common)'),'hash rejection precedes common custom import')
I.need(freeze_text.index('common=guard.load_common(frame)')<freeze_text.index('spec=importlib.util.spec_from_file_location')<freeze_text.index('body.freeze(frame,common,guard)'),'rejected helper precedes body import and any body invocation')
I.need("checked(root['engine'])"in controller_text and controller_text.index("checked(root['engine'])")<controller_text.index("module.monitor(argv"),'outer controller hash-reads engine before launching wrapper; no engine invocation')
I.need(not FREEZE.exists()and not FREEZE.is_symlink(),'entire actual freeze root absent at independent review, no receipt/artifact')
# Same authenticated completed BUILD-only proof and full current input bytes persist.
build=I.read(authority['independentBuildReview']['result']);contract=load(K/'independent-ownership-gc-v2-native-build-review-v1/result-contract.json')
for k,v in contract['requiredFixedValues'].items():eq(build[k],v,'genuine unchanged BUILD-only proof '+k)
for k,d in contract['requiredExactDescriptors'].items():eq(build[k],d,'whole prior build tuple '+k);I.verify(d,'unchanged actual build input')
build_inputs=I.read(build['auditData']);I.need(len(build_inputs['inputs'])==10268,'finite build DATA input rows')
for d in build_inputs['inputs']:I.verify(d,'complete previously reviewed BUILD-only current input')
witness=I.read(build['witnessReview'])
for d in witness['externalEvidenceInventory']+witness['extraFileReads']:I.verify(d,'whole prior build raw ownership/tool witness DATA')
metadata=I.read(authority['metadata']);I.need(authority['engine']['sha256']=='289df4455b56b50a9598c42a7d924aaa2adca7f5461f96782f5758a979e966c8'and authority['metadata']['sha256']=='90c3f45e439c116aaa526167b6fc26122a38c7da702984d53dd3e35fde5304c8','same actual GC build retained')
I.need(metadata['engineSha256']==authority['engine']['sha256']and metadata['engineBytes']==authority['engine']['bytes']==10004458 and metadata['gcStress']is True and metadata['entropyPolicy']=='off','whole unchanged metadata binds actual GC engine')
I.need(len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3,'native355/external3 still retained')
I.need(I.verify(authority['engine']).read_bytes()[:8]==b'\x00asm\x01\x00\x00\x00','core Wasm magic only, no executable parse or engine invocation')
normal=load(NATIVE/'normal-protection.json');I.need(len(normal['originals'])==1387 and len(normal['requiredNormalFreezeMembership'])==1391,'normal full protected scope')
for d in normal['originals']:I.verify(d['original'],'protected original normal ref');I.verify(d['frozen'],'protected frozen normal ref')
for d in normal['frozenCopyEntries']:I.verify(d,'whole original normal frozen copy')
I.verify(normal['freezeReceipt'],'normal receipt preserved');I.exact_tree(I.canonical(normal['freezeReceipt']['path']).parent,normal['requiredNormalFreezeMembership'])
vulnerable=[]
for d in normal['frozenCopyEntries']:
    if d['path'].endswith(('/normal-off-CMakeCache.txt','/normal-off-compile_commands.json')):
        original={k:d[k]for k in ['sha256','bytes']};original['path']=d['original'];I.verify(original,'specifically vulnerable normal project original');vulnerable.append(dict(original=original,frozen={k:d[k]for k in ['path','sha256','bytes']}))
I.need(len(vulnerable)==2 and vulnerable[0]['original']['sha256'].startswith('a2c669')and vulnerable[1]['original']['sha256'].startswith('d88a5f'),'both actual original cache/DB stayed unchanged')
# Preserve all private pending artifact reader bytes/membership, never adopt it as proof.
draft_rows=[]
for p in sorted(DRAFT.rglob('*')):
    I.need(not p.is_symlink(),'private draft has no links')
    if p.is_file():d=row(p);I.verify(d,'unchanged pending artifact reader');draft_rows.append(d)
I.need(len(draft_rows)==8 and not(DRAFT/'index.json').exists()and not(DRAFT/'results.json').exists(),'pending artifact draft stays unsealed/no verdict')
for flag in ['frozenRootCreated','freezeReceiptPublished','commonHelperImported','freezerBodyImported','ninjaOrMetadataAdmissionInvoked','engineExecuted','guestOrKeyOrGcWorkloadInvoked','retryAllowedByThisRecord','operationalAdmission','runtimeAcceptanceClaim']:I.need(root[flag]is False,'bounded actual failure Root fact '+flag)
I.need(root['sourceReviewsMissedSelectionAmbiguity']is True and root['sourceReviewScopeCorrectionRequired']is True,'historical source-review miss retained honestly')
I.final_rehash();I.exact_tree(I.canonical(normal['freezeReceipt']['path']).parent,normal['requiredNormalFreezeMembership']);I.exact_tree(DRAFT,[Path(d['path']).relative_to(DRAFT).as_posix()for d in draft_rows]);I.need(not FREEZE.exists()and not FREEZE.is_symlink(),'freeze root still absent at final independent boundary')
write('failure-analysis.json',dict(schemaVersion=1,finding='GC-HELPER-SELECTION-M2',rootRecord=root_row,rawTraceback=stderr,exactStackFrames=frames,suffixMatches=matches,wrongFirstExpectedDescriptor=expected,correctUniqueCryptoRow=correct[0],actualCorrectHelper=actual,selectionUsesFirstBroadSuffix=True,bothShaAndSizeMismatch=True,commonImportUnreachedBySourceAndRawStack=True,bodyImportUnreachedBySourceAndRawStack=True,ninjaAndMetadataAdmissionUnreachedBySourceAndRawStack=True,fullFreezeRootAbsentAtInitialAndFinalReview=True,outerControllerAlreadyReadEngineBytesAsHashOnly=True,fullBuildProofRetained=True,normalProtection=dict(originalReferences=1387,distinctOriginalPaths=1378,exactFrozenMembers=1391,vulnerableOriginals=vulnerable),pendingArtifactDraft=draft_rows,historicalSourceReviewMissAcknowledged=True,noFrozenNativeArtifactProof=True,sourceCoupledEffectsNotSyscallTrace=True,reviewerActions='stdlib read/hash/JSON/AST and pure DATA comparison only'))
write('rehashed-inputs.json',dict(schemaVersion=1,files=list(I.ROWS.values()),families=families,allFinalHashesStable=True,normalExactMembershipInitialAndFinal=True,pendingArtifactDraftUnchanged=True,freezeRootAbsentInitialAndFinal=True,ownerActionsInvoked=False))
write('reader-results.json',dict(schemaVersion=1,state='FINITE_GC_FREEZE_FAILURE_DATA_AUDIT_PASSED_NOT_ARTIFACT',rootRecord=root_row,sourceIndex=root['nativeSourceIndex'],rawParentExitCode=1,pid=75163,totalObservedPids=1,ownedGroupsGone=True,noForcedCleanupTimeoutOrSignals=True,stdoutBytes=0,stderrBytes=898,finiteSuffixMatches=11,correctSuffixOrdinalZeroBased=4,sourceAndRawStackConfirmPreCommonPreBodyRejection=True,normalOriginalReferenceEntries=1387,normalFrozenMembers=1391,buildEngineSha256=authority['engine']['sha256'],buildMetadataSha256=authority['metadata']['sha256'],fullPriorBuildDataInputRows=10268,physicalInputs=len(I.ROWS),checks=I.CHECKS,reviewerOwnerHelpersNodeCliEngineGuestNativeGcActionsInvoked=False,artifactVerifiedPassed=False,actualFreezeSucceeded=False,retryAllowed=False,operationalAdmission=False,runtimeAcceptanceClaim=False,concreteCounterFindings=[]))
print(json.dumps(dict(state='FINITE_FAILURE_AUDIT_PASSED_NO_ARTIFACT',inputs=len(I.ROWS),checks=I.CHECKS,rootRaw=1,freezeRootAbsent=True,normalPreserved=True,ownerActionsInvoked=False)))
